# Bank Credit Risk Forecasting and Model Validation

A retrospective study of whether an interpretable statistical model improves forecasts of U.S. bank loan losses relative to a simple persistence benchmark. The analysis uses public FDIC financial reports only. It is an independent educational project, not a Wells Fargo model or a regulatory assessment.

## Abstract

The source snapshot contains 231,664 institution-quarter records from 6,586 entities over 2015–2025. On 53,590 held-out forecasts targeting 2023–2025, Ridge regression had a mean absolute error (MAE) of **0.058789 percentage points**, compared with **0.054440** for persistence. Ridge's MAE was about 8% higher. The evidence supports retaining persistence for this study rather than promoting the more complex model. See the [saved metrics](outputs/metrics.json) and [validation report](docs/validation.md) for the evaluation and its limitations.

## Estimand and forecast design

The outcome is the quarterly net charge-off rate: net charge-offs for the quarter divided by the average of beginning- and end-of-quarter gross loans, expressed as a nonannualized percentage. This project-defined measure captures institution-level accounting losses. It is neither an individual borrower's probability of default nor a reproduction of the FDIC's annualized rate.

At the assumed forecast origin, the end of quarter `q+1`, the model uses financials from report quarter `q` to forecast the rate for quarter `q+2`. For example, it uses a 2022Q3 report to forecast 2023Q1 at the end of 2022Q4. The one-quarter reporting buffer avoids assuming immediate publication; it does not establish what was originally observable, because historical filings may have been restated.

## Model selection and evaluation

- **Benchmarks:** Carry forward the latest reported rate (persistence). Compare with a seasonal baseline on the subset with a prior-year observation.
- **Challenger:** Fit Ridge regression. Imputation, clipping and scaling are learned only from the fitting sample. Clipping applies to predictors, not outcomes. Select the penalty on validation MAE, fix it, and refit on the training and validation periods before evaluating the final test.
- **Chronological split by target quarter:** Train through 2020Q3; validate on 2021Q1–2022Q3; test on 2023Q1–2025Q4. Exclude 2020Q4 and 2022Q4 to allow an additional reporting quarter for fitting labels before the next evaluation origin.

The held-out results are retrospective, not a live or point-in-time backtest. The same institutions can appear across periods, so the evaluation does not establish performance on previously unseen banks. No production deployment or independent regulatory validation is claimed.

## Reproduce the analysis

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.download
python -m src.model
python -m unittest discover -s tests -v
```

The downloader retrieves public data from the [FDIC financial API](https://api.fdic.gov/banks/docs) and may take several minutes. There is no synthetic fallback. Download or validation failures stop the run. Retain the generated source manifest and checksum: a fresh pull may differ from the [November 11 source snapshot](docs/source_manifest.json).

Raw records, the local SQLite database, and institution-level predictions are not committed. The pipeline regenerates them, along with the aggregate diagnostics in [`outputs/`](outputs/).

## Repository guide

| Resource | Contents |
|---|---|
| [Python pipeline](src/) | Data acquisition, accounting reconciliation, target alignment, model fitting and evaluation |
| [SQL quality checks](sql/quality_checks.sql) and [tests](tests/) | Panel integrity and reproducibility checks |
| [Data dictionary](docs/data_dictionary.md) and [source manifest](docs/source_manifest.json) | Field definitions, units and provenance |
| [Development record](docs/development.md) and [validation report](docs/validation.md) | Modeling choices, diagnostics and limitations |
| [Learning guide](docs/learning_path.md) | Exercises for interpreting and challenging the analysis |

**Data scope and attribution.** The observations are individual FDIC-reporting institutions, not consolidated bank holding companies. The study does not use licensed WRDS exports. In the [official FDIC field metadata](https://api.fdic.gov/banks/docs/risview_properties.yaml), `NTLNLS` is net charge-offs and `NCLNLS` is noncurrent loans; the two are not interchangeable. Developed with AI assistance.
