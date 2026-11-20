"""Retrospective real-data bank loss forecasting. No generated financial data."""
import json,sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error,mean_squared_error
ROOT=Path(__file__).resolve().parents[1]
FEATURES=['nco_pct','noncurrent_pct','equity_pct','loans_deposits_pct','log_assets','roa_pct','quarter_sin','quarter_cos']

class TrainQuantileClipper(BaseEstimator,TransformerMixin):
    """Prevent extreme predictor influence; bounds learned only from fit sample."""
    def __init__(self,lower=.01,upper=.99): self.lower=lower;self.upper=upper
    def fit(self,X,y=None):
        self.low_=np.quantile(X,self.lower,axis=0);self.high_=np.quantile(X,self.upper,axis=0);return self
    def transform(self,X): return np.clip(X,self.low_,self.high_)

def convert_ytd(d):
    d=d.sort_values(['CERT','period']).copy();g=d.groupby('CERT')
    adjacent=d.period-g.period.shift()==1
    same_year=d.year==g.year.shift()
    val=(d.NTLNLS-g.NTLNLS.shift()).where(adjacent & same_year)
    return val.where(d.qnum!=1,d.NTLNLS)

def prepare(raw):
    d=raw.copy()
    if d.duplicated(['CERT','REPDTE']).any(): raise ValueError('Duplicate entity/report keys')
    date=pd.to_datetime(d.REPDTE.astype(str),format='%Y%m%d',errors='raise')
    if not date.dt.is_quarter_end.all():raise ValueError('Non-quarter-end report')
    d['quarter']=date.dt.to_period('Q').astype(str)
    d['period']=date.dt.to_period('Q').astype('int64');d['qnum']=date.dt.quarter;d['year']=date.dt.year
    for col in ['ASSET','EQ','LNLSGR','NCLNLS','NTLNLS','NTLNLSQ','DRLNLS','CRLNLS','DEP','ROA']:
        d[col]=pd.to_numeric(d[col],errors='coerce')
    d=d.sort_values(['CERT','period']).reset_index(drop=True)
    d['ytd_derived_q']=convert_ytd(d)
    reconciled=d[['ytd_derived_q','NTLNLSQ']].dropna()
    delta=(reconciled.ytd_derived_q-reconciled.NTLNLSQ).abs()
    balance=(d.DRLNLS-d.CRLNLS-d.NTLNLS).abs()
    quality={'raw_rows':len(d),'banks':int(d.CERT.nunique()),'quarter_count':int(d.quarter.nunique()),
             'ytd_reconciliation_rows':len(delta),'ytd_vs_quarterly_mismatches_gt_1_thousand':int((delta>1).sum()),
             'chargeoffs_less_recoveries_mismatches_gt_1_thousand':int((balance>1).sum()),
             'missing_by_field':{c:int(d[c].isna().sum()) for c in raw.columns},
             'note':'1 means one raw financial unit (thousand dollars). Mismatches can reflect merger/restatement adjustments; exclude mismatches from target construction.'}
    g=d.groupby('CERT');adjacent=(d.period-g.period.shift()==1)
    d['avg_gross_loans']=(d.LNLSGR+g.LNLSGR.shift())/2
    valid=adjacent & (d.avg_gross_loans>0) & (d.LNLSGR>0) & (d.ASSET>0)
    # Exclude observed disagreements in either reconciliation, without filling missing target.
    q_ok=(d.ytd_derived_q-d.NTLNLSQ).abs().le(1)
    total_ok=balance.le(1)
    d['nco_pct']=(100*d.NTLNLSQ/d.avg_gross_loans).where(valid & q_ok & total_ok)
    d['noncurrent_pct']=(100*d.NCLNLS/d.LNLSGR).where(d.LNLSGR>0)
    d['equity_pct']=(100*d.EQ/d.ASSET).where(d.ASSET>0)
    d['loans_deposits_pct']=(100*d.LNLSGR/d.DEP).where(d.DEP>0)
    d['log_assets']=np.log(d.ASSET.where(d.ASSET>0))
    d['roa_pct']=d.ROA
    d['quarter_sin']=np.sin(2*np.pi*d.qnum/4);d['quarter_cos']=np.cos(2*np.pi*d.qnum/4)
    # q data -> forecast origin end of q+1 -> predict q+2. Publication buffer is not proof of original availability.
    future=d[['CERT','period','quarter','nco_pct']].rename(columns={'quarter':'target_quarter','nco_pct':'target'})
    future['period']=future.period-2
    out=d.merge(future,on=['CERT','period'],how='inner',validate='one_to_one')
    season=d[['CERT','period','nco_pct']].rename(columns={'nco_pct':'seasonal_prediction'})
    season['period']=season.period+2 # target q+2, same quarter last year = q-2
    out=out.merge(season,on=['CERT','period'],how='left',validate='one_to_one')
    out=out.replace([np.inf,-np.inf],np.nan)
    out=out.loc[out.target.notna() & out.nco_pct.notna() & out.log_assets.notna()].copy()
    out['forecast_origin']=(pd.PeriodIndex(out.quarter,freq='Q')+1).astype(str)
    quality['model_rows']=len(out);quality['model_banks']=int(out.CERT.nunique())
    quality['unmatched_or_excluded_rows']=len(d)-len(out)
    return d,out,quality

def split(d):
    return (d[d.target_quarter<='2020Q3'].copy(),d[(d.target_quarter>='2021Q1')&(d.target_quarter<='2022Q3')].copy(),d[d.target_quarter>='2023Q1'].copy())

def metrics(y,p):
    y=np.asarray(y);p=np.asarray(p)
    return {'n':len(y),'MAE_pp':float(mean_absolute_error(y,p)),'RMSE_pp':float(np.sqrt(mean_squared_error(y,p))),
            'bias_pp':float(np.mean(p-y)),'median_absolute_error_pp':float(np.median(np.abs(p-y)))}

def make_model(alpha):return make_pipeline(SimpleImputer(strategy='median'),TrainQuantileClipper(),StandardScaler(),Ridge(alpha=alpha))

def main():
    outdir=ROOT/'outputs';outdir.mkdir(exist_ok=True)
    raw=pd.read_csv(ROOT/'data/raw/fdic_bank_quarters_2015_2025.csv')
    with sqlite3.connect(ROOT/'data/research.sqlite') as con:
        raw.to_sql('fdic_raw',con,if_exists='replace',index=False)
        con.execute('CREATE UNIQUE INDEX IF NOT EXISTS entity_quarter ON fdic_raw(CERT,REPDTE)')
        pd.read_sql_query('SELECT REPDTE,COUNT(*) AS bank_count FROM fdic_raw GROUP BY REPDTE ORDER BY REPDTE',con).to_csv(outdir/'sql_coverage.csv',index=False)
        raw=pd.read_sql_query('SELECT * FROM fdic_raw ORDER BY CERT,REPDTE',con)
    d,panel,quality=prepare(raw)
    train,validation,test=split(panel)
    grid=[]
    for a in [.1,1,10,100,1000]:
        m=make_model(a).fit(train[FEATURES],train.target)
        grid.append({'alpha':a,**metrics(validation.target,m.predict(validation[FEATURES]))})
    best=min(grid,key=lambda x:x['MAE_pp'])['alpha']
    fit=pd.concat([train,validation]);model=make_model(best).fit(fit[FEATURES],fit.target)
    pred=model.predict(test[FEATURES]);test=test.copy();test['ridge_prediction']=pred;test['persistence_prediction']=test.nco_pct
    seasonal=test.dropna(subset=['seasonal_prediction'])
    results={'data_status':'REAL PUBLIC FDIC DATA, RESTATED SNAPSHOT','target':'Nonannualized quarterly net chargeoffs / average beginning-end gross loans, percent',
      'horizon':'Report q -> forecast origin end q+1 -> target q+2; original release vintages unavailable',
      'selected_alpha':best,'validation_grid':grid,
      'split_rows':{k:len(v) for k,v in [('train',train),('validation',validation),('test',test)]},
      'split_target_ranges':{k:[v.target_quarter.min(),v.target_quarter.max()] for k,v in [('train',train),('validation',validation),('test',test)]},
      'test_persistence':metrics(test.target,test.persistence_prediction),'test_ridge':metrics(test.target,pred),
      'seasonal_subset':{'seasonal':metrics(seasonal.target,seasonal.seasonal_prediction),'ridge_same_rows':metrics(seasonal.target,seasonal.ridge_prediction)},
      'claim_limit':'Retrospective research only, not point-in-time or production performance. One bank-weighted observation per quarter; errors correlated across time/banks.'}
    (outdir/'metrics.json').write_text(json.dumps(results,indent=2));(outdir/'quality.json').write_text(json.dumps(quality,indent=2))
    cols=['CERT','NAME','quarter','forecast_origin','target_quarter','target','ridge_prediction','persistence_prediction','seasonal_prediction']
    test[cols].to_csv(outdir/'test_predictions.csv',index=False)
    per=[]
    for q,g in test.groupby('target_quarter'):
        for name in ['ridge','persistence']:per.append({'quarter':q,'model':name,**metrics(g.target,g[name+'_prediction'])})
    pd.DataFrame(per).to_csv(outdir/'quarterly_errors.csv',index=False)
    pd.DataFrame({'feature':FEATURES,'standardized_coefficient':model.named_steps['ridge'].coef_}).to_csv(outdir/'coefficients.csv',index=False)
    d.to_csv(ROOT/'data/cleaned_bank_quarters.csv',index=False)
    print(json.dumps({'quality':quality,'results':results},indent=2))
if __name__=='__main__':main()
