# Validation report — real-data first version

## Executive finding
**Do not promote the Ridge challenger.** On the held-out 2023–2025 target period it performs worse than the simple latest-rate benchmark. A more complicated model is not automatically more useful. The observed failure is retained, not hidden by selecting a different test period or clipping difficult outcomes.

## Data and quality
- 231,664 actual FDIC institution-quarter records, 6,586 entities, 44 quarters, 2015Q1–2025Q4.
- 207,112 eligible forecast pairs across 6,209 entities after exact-horizon joins and accounting/denominator requirements.
- 110,399 training rows; 33,561 validation; 53,590 test. A further 9,562 eligible rows fall in the two label-availability embargo quarters and are intentionally unused.
- No duplicated entity-quarter keys. All 44 requested quarter endpoints returned.
- 230,847 comparable YTD/quarterly records: 400 differ by more than one source monetary unit. These affected quarterly rate observations are excluded. This is a reconciliation issue for review, not proof that the source is wrong.
- Zero gross-chargeoffs minus recoveries versus net-chargeoffs differences greater than one unit among nonmissing comparisons.
- Several financial columns have 748 missing entries; targets are never imputed. Detailed counts are in `outputs/quality.json`.

## Held-out performance
All errors below are percentage points of the nonannualized project-defined quarterly rate.

| Model | MAE | RMSE | Bias | Median absolute error |
|---|---:|---:|---:|---:|
| Latest-rate persistence | 0.054440 | 0.373692 | -0.004103 | 0.007019 |
| Ridge (alpha 1000) | 0.058789 | 0.410240 | -0.012845 | 0.018817 |

Ridge's MAE is about 7.99% higher (worse). Its RMSE is also worse. The seasonal baseline has MAE 0.054417 on 53,472 available rows, compared with Ridge MAE 0.058778 on those same rows. This is not a confidence interval or significance test.

## Completed verification
Nine automated tests passed using the actual downloaded records: unique keys; quarter coverage; exact forecast horizon; temporal split/label embargo; Q1 cumulative reset; nonmissing targets/baseline; duplicate rejection; train-only preprocessing; missing target quarters not filled with zero. Python compilation and complete pipeline execution passed. Source retrieval manifest and raw-file SHA256 are included.

## Model-risk limitations
1. Retrospective revised snapshot, not original vintages. A full-quarter reporting buffer does not erase restatement leakage.
2. Merger accounting, changing institution composition and absent future outcomes remain; non-survival should not be interpreted as zero loss.
3. Quarterly flows may be adjusted around mergers. Excluding mismatches changes the sample.
4. Two-point average gross loans is not necessarily the regulator's official average denominator. No annualization is applied.
5. Errors are correlated across banks and quarters. Row-level confidence intervals would be misleading; none are claimed.
6. Unweighted bank-quarter metrics do not quantify dollar exposure or business impact.
7. A few large errors drive RMSE. Investigate them rather than blindly removing them.
8. Current review is developer self-validation, not independent validation.

## Next step, without contaminating the test
Review data issues and model failures using training/validation data, add diagnostics, and predefine changes. Treat 2023–2025 as already inspected, not an untouched future holdout for later versions. Obtain new or separately held-out evidence for new model claims. The immediate project deliverable is rigorous validation and communication, not a production-ready forecast.
