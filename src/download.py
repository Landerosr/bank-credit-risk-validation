"""Download public FDIC bank-level records, never holding companies."""
import json, time, hashlib, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
URL='https://banks.data.fdic.gov/api/financials'
FIELDS=['CERT','REPDTE','NAME','ASSET','EQ','LNLSGR','NCLNLS','NTLNLS','NTLNLSQ','DRLNLS','CRLNLS','DEP','ROA']
FILTER='REPDTE:[20150331 TO 20251231]'

def fetch(report_date):
    params={'filters':'REPDTE:'+report_date,'fields':','.join(FIELDS),'limit':10000,'offset':0,'sort_by':'CERT','sort_order':'ASC','format':'json'}
    url=URL+'?'+urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url,timeout=90) as r: return json.load(r),url
        except Exception:
            if attempt==3: raise
            time.sleep(2**attempt)

def main():
    target=ROOT/'data/raw';target.mkdir(parents=True,exist_ok=True)
    metaurl='https://api.fdic.gov/banks/docs/risview_properties.yaml'
    with urllib.request.urlopen(metaurl,timeout=60) as r: metadata=r.read()
    (target/'fdic_field_metadata.yaml').write_bytes(metadata)
    report_dates=[p.end_time.strftime('%Y%m%d') for p in pd.period_range('2015Q1','2025Q4',freq='Q')]
    pages=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for page,url in pool.map(fetch,report_dates):
            if len(page['data'])!=page['meta']['total']:raise RuntimeError('Quarter exceeded page size or missing records')
            pages.append(page);print('Loaded',sum(len(p['data']) for p in pages),flush=True)
    first=pages[0];total=sum(p['meta']['total'] for p in pages)
    indexes={json.dumps(p['meta']['index'],sort_keys=True) for p in pages}
    if len(indexes)!=1: raise RuntimeError('FDIC source index changed during pagination; rerun')
    df=pd.DataFrame([r['data'] for p in pages for r in p['data']])
    if len(df)!=total or df.duplicated(['CERT','REPDTE']).any(): raise RuntimeError('Pagination count or key validation failed')
    missing=set(FIELDS)-set(df)
    if missing: raise ValueError(f'Missing fields: {missing}')
    path=target/'fdic_bank_quarters_2015_2025.csv';df.to_csv(path,index=False)
    manifest={'source':URL,'filter':FILTER,'fields':FIELDS,'retrieved_utc':datetime.now(timezone.utc).isoformat(),
      'index':first['meta']['index'],'rows':len(df),'entities':int(df.CERT.nunique()),
      'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'metadata_url':metaurl,
      'scope':'Individual institution financial reports returned by FDIC API; not holding companies','status':'real public FDIC data; current restated snapshot, not historical vintages'}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
