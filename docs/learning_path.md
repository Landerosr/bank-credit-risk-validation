# Learn the project one step at a time

1. **Business question:** Why would a bank risk team forecast loan losses? What decision could the forecast inform, and what should it never decide alone?
2. **Data unit:** One row is an institution-quarter, not a borrower. Find rows for a bank in the real CSV. Explain why a holding company is not the same entity as a bank subsidiary.
3. **Target:** Net charge-offs are gross write-offs minus recoveries. Read NTLNLSQ and the beginning/end LNLSGR balances. Calculate the percentage manually for one actual row and compare with the cleaned dataset.
4. **Timing:** Using a 2022Q3 report, assume we wait until end 2022Q4, then forecast 2023Q1. Explain why historical revisions still prevent calling this a true point-in-time backtest.
5. **SQL:** Run the quality queries and count banks by reporting date. Why does that number change?
6. **Baseline:** Predict the future rate with the latest available rate. Why might this be hard for regression to beat?
7. **Ridge:** Learn linear regression first, then the penalty and feature scaling. Explain why preprocessing must be fitted on development data only.
8. **Validation:** Training develops the model, validation selects its settings, and test evaluates the fixed choice. Explain the embargo periods and why we cannot repeatedly tune on the same test.
9. **Actual finding:** The first Ridge model loses to the baseline. Explain that honestly, then inspect development-period errors before changing anything.
10. **Communication:** Write three sentences: what we tested, what the evidence says, and the biggest limitation. Negative findings can show sound model-risk judgment.

Potential additions: bank peer-group error views, accounting reconciliation drill-down, reporting-lag sensitivity, rolling validation, uncertainty estimates, or a clear dashboard. Add them to answer a business question, not just decorate the repository.
