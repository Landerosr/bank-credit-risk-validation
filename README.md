# Bank Credit Risk Lab — Real FDIC Data

**This project uses actual publicly reported FDIC financial records only.** Independent educational research inspired by model-development and validation roles. Not affiliated with Wells Fargo; not an internal bank model or regulatory assessment.

## Main finding
On 53,590 held-out forecasts targeting 2023–2025, **Ridge did not outperform persistence** (carrying forward the last reported rate). Ridge MAE was 0.058789 percentage points versus 0.054440 for persistence, about 8% higher. The result supports keeping the simple benchmark for this study. See the [saved metrics](outputs/metrics.json) and [validation report](docs/validation.md).

The verified source snapshot contains 231,664 institution-quarter records from 6,586 entities over 2015–2025. Raw records and row-level predictions are intentionally omitted from GitHub; the pipeline can regenerate them using the [public FDIC API](https://api.fdic.gov/banks/docs). Small saved aggregate diagnostics and the [November 11 source manifest](docs/source_manifest.json) are included. Fresh downloads may differ because reports can be revised.

## Question
Can a small, interpretable statistical model improve forecasts of future quarterly loan charge-offs relative to repeating the latest reported rate?

## What we predict
Nonannualized quarterly net charge-offs as a percentage of average beginning/end gross loans. This is a project-defined ratio, not a claim to reproduce FDIC's official annualized rate. It is bank-level accounting loss, not borrower default probability.

## Get started
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.download     # actual FDIC data, may take several minutes
python -m src.model
python -m unittest discover -s tests -v
```
No synthetic fallback exists. Download or validation failures stop the run. Public data can be revised, so record the generated source manifest and checksum.

## Forecast timing
Use financial report quarter q, allow one full quarter as a reporting buffer, and forecast q+2. Example: report 2022Q3, assumed forecast origin end 2022Q4, target 2023Q1. This avoids pretending quarter-end figures were instantly known. It does **not** establish original availability because the downloaded snapshot may be restated.

## Model and validation
Persistence benchmark; seasonal comparison on available rows; Ridge regression with training-only imputation, feature clipping and scaling. Alpha is selected on validation MAE, then fixed for the final test. Targets are NOT clipped to make scores look better.

Target-period splits: training through 2020Q3; validation 2021Q1–2022Q3; test 2023Q1–2025Q4. Targets 2020Q4 and 2022Q4 are embargoed so labels used for fitting have a full reporting quarter before the next evaluation origin. Published metrics describe a retrospective dataset study, not live or point-in-time forecasting. 

## Deliverables
Python model/data pipeline, SQL quality queries, source manifest, data dictionary, development/validation reports, aggregate quarterly diagnostics and learning guide. Running the pipeline generates the local SQLite database and row-level test predictions; neither is committed.

## Data rights and identity
This version uses public FDIC data, not licensed WRDS exports. It contains individual FDIC-reporting institutions, not consolidated bank holding companies. Do not mix the two entity types. Do not reuse labels from older drafts: official FDIC metadata identifies **NTLNLS as net charge-offs** and **NCLNLS as noncurrent loans**.

Developed with AI assistance. The learner should understand and challenge the analysis before presenting it as their work. No production deployment, live forecast performance, or independent regulatory validation is claimed.

## Label-availability embargo
Training labels end 2020Q3, with 2020Q4 embargoed before validation starts 2021Q1. Validation labels end 2022Q3, with 2022Q4 embargoed before test starts 2023Q1. This allows a full quarter for training outcomes to become available before the first next-period forecast. It still does not remove restatement risk.
