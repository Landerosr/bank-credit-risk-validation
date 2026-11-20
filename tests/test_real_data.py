"""Integration tests run only against the downloaded real FDIC panel."""
import unittest
import numpy as np
import pandas as pd
from src.model import ROOT,prepare,split,make_model,FEATURES

class RealDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/'data/raw/fdic_bank_quarters_2015_2025.csv'
        if not path.exists():raise unittest.SkipTest('Download real FDIC data first; no synthetic substitution')
        cls.raw=pd.read_csv(path);cls.clean,cls.panel,cls.quality=prepare(cls.raw)
    def test_unique_keys(self):self.assertFalse(self.raw.duplicated(['CERT','REPDTE']).any())
    def test_source_all_requested_quarters(self):self.assertEqual(self.raw.REPDTE.nunique(),44)
    def test_exact_forecast_horizon(self):
        p=self.panel
        self.assertTrue(((pd.PeriodIndex(p.target_quarter,freq='Q').asi8-pd.PeriodIndex(p.quarter,freq='Q').asi8)==2).all())
        self.assertTrue(((pd.PeriodIndex(p.target_quarter,freq='Q').asi8-pd.PeriodIndex(p.forecast_origin,freq='Q').asi8)==1).all())
    def test_temporal_split(self):
        a,b,c=split(self.panel)
        self.assertLess(a.target_quarter.max(),b.target_quarter.min());self.assertLess(b.target_quarter.max(),c.target_quarter.min())
        self.assertLessEqual(pd.Period(a.target_quarter.max(),freq='Q')+1,pd.Period(b.forecast_origin.min(),freq='Q'))
        self.assertLessEqual(pd.Period(b.target_quarter.max(),freq='Q')+1,pd.Period(c.forecast_origin.min(),freq='Q'))
    def test_ytd_q1_reset(self):
        q=self.clean[self.clean.qnum==1]
        np.testing.assert_allclose(q.ytd_derived_q,q.NTLNLS,equal_nan=True)
    def test_target_and_baseline_not_missing(self):self.assertFalse(self.panel[['target','nco_pct']].isna().any().any())
    def test_raw_duplicate_rejected(self):
        with self.assertRaises(ValueError):prepare(pd.concat([self.raw.iloc[:5],self.raw.iloc[:1]]))
    def test_clipping_fit_only_training(self):
        a,b,c=split(self.panel);m=make_model(1).fit(a[FEATURES],a.target)
        imputed=m.named_steps['simpleimputer'].transform(a[FEATURES])
        np.testing.assert_allclose(m.named_steps['trainquantileclipper'].low_,np.quantile(imputed,.01,axis=0))
        self.assertTrue(np.isfinite(m.predict(c[FEATURES])).all())
    def test_missing_target_does_not_become_zero(self):
        # Remove actual target observations; supervised pair count must not grow.
        cut=self.raw[self.raw.REPDTE!=20241231]
        _,reduced,_=prepare(cut)
        self.assertLess(len(reduced),len(self.panel))
        self.assertNotIn('2024Q4',set(reduced.target_quarter))
if __name__=='__main__':unittest.main()
