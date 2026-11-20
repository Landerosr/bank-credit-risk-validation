# Development record

## Intended use
An interpretable retrospective study of bank loan-loss forecasting, demonstrating development, data quality, SQL, Python and model validation. Not a lending, capital, bank-failure or investment model.

## Features
Current project-defined charge-off rate; noncurrent loans/gross loans; equity/assets; loans/deposits; log assets; reported ROA; calendar-quarter sine/cosine. No bank names or future values enter the feature matrix. No macroeconomic feature is added until its historical availability is addressed.

## Methods
Persistence: latest observed rate. Seasonal: the target quarter's rate one year earlier (when available). Ridge: linear regression with penalty alpha selected from [.1,1,10,100,1000] on validation MAE. Pipeline uses median imputation, 1st/99th percentile predictor clipping, then standardization, all fitted on the development sample only. Imputation never fills targets. Ridge coefficients are associations, not causal effects.

The final model refits on train+validation once and evaluates the held-out target period. The same institutions can appear across periods. This assesses future outcomes for a recurring panel, not generalization to unseen banks.

## Timing and source limitation
A report q produces an assumed forecast at end q+1 of outcome q+2. The full-quarter buffer is a conservative operational assumption, not a verified original-publication schedule. Current FDIC reports can contain revisions. Consequently results must be labeled retrospective; no claim of a point-in-time backtest is justified.

## Evaluation
MAE and RMSE in percentage points, mean signed error, median absolute error, quarterly breakdown and baseline comparison. Report unweighted bank-quarter metrics; results are not weighted by dollars of exposure. Missing/invalid target exclusions and source accounting differences are disclosed. Repeated tuning using these test results would turn the test into development data and require a new holdout.

## Future work
Review a sample against original filings; analyze mergers/outliers and attrition; peer-group errors; rolling-origin validation; bank/time-clustered uncertainty; stability and drift monitoring; independent human review. Stress scenarios, if added, measure model sensitivity rather than causal predictions.

## Label-availability embargo
Training labels end 2020Q3, with 2020Q4 embargoed before validation starts 2021Q1. Validation labels end 2022Q3, with 2022Q4 embargoed before test starts 2023Q1. This allows a full quarter for training outcomes to become available before the first next-period forecast. It still does not remove restatement risk.
