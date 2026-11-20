# Data dictionary and provenance

Primary source: [FDIC financial API](https://api.fdic.gov/banks/docs/).
Official field metadata: https://api.fdic.gov/banks/docs/risview_properties.yaml
A copy of the verified run’s source manifest is committed at `docs/source_manifest.json`. A new download saves raw records, official metadata and a fresh manifest under the ignored local `data/raw/` directory.

| Raw field | Role |
|---|---|
| CERT | Institution certificate identifier |
| REPDTE | Quarter-end financial report date |
| NAME | Institution name for reporting, not model input |
| ASSET | Total assets |
| EQ | Equity capital |
| LNLSGR | Total gross loans and leases |
| NCLNLS | Noncurrent loans and leases, NOT net charge-offs |
| NTLNLS | Total net loan/lease charge-offs, cumulative within year |
| NTLNLSQ | Quarterly net loan/lease charge-offs |
| DRLNLS | Gross loan/lease charge-offs, cumulative within year |
| CRLNLS | Loan/lease recoveries, cumulative within year |
| DEP | Total deposits |
| ROA | Annualized return on average assets, percent |

Financial amounts are in the source's monetary units (FDIC reporting convention: thousands of dollars). Dimensionless ratios cancel common units. The model does not convert accounting losses to dollar forecasts.

Quarterly NTLNLSQ is checked against NTLNLS differences across adjacent same-year quarters; Q1 uses NTLNLS itself. DRLNLS minus CRLNLS is checked against NTLNLS. Rows with a difference above one raw unit are excluded when forming loss-rate targets. Merger/restatement adjustments may explain some discrepancies; exclusion is not proof of source error. Negative net charge-offs (net recoveries) remain permitted.

Project target: 100 × NTLNLSQ / ((current LNLSGR + immediately preceding LNLSGR)/2). Requires positive loan balances and an adjacent predecessor. It is **not annualized**, and the denominator is a two-point average rather than an official daily average.

To avoid confusing similarly named fields, this model uses reconciled raw components and official definitions rather than treating NTLNLSR and NCLNLSR as interchangeable. Neither ratio is used as a target or predictor here.

Panel includes every returned report in 2015Q1–2025Q4; it does not select only currently active institutions. Some banks exit or merge, causing unavailable future outcomes. This missing-outcome attrition is a limitation, not permission to fill targets with zeros. CERT continuity does not eliminate merger accounting changes.

The download includes reports returned by the FDIC financial API without a current-active filter or a separately verified historical bank-class universe. Observations missing required charge-off fields or with invalid loan denominators are excluded. Do not call this a fully audited census of all insured U.S. banks.
