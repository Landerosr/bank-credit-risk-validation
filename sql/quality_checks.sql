-- Read-only queries for data/research.sqlite after python -m src.model
SELECT CERT, REPDTE, COUNT(*) n FROM fdic_raw GROUP BY CERT, REPDTE HAVING COUNT(*) > 1;
SELECT REPDTE, COUNT(*) bank_count, SUM(ASSET) reported_assets FROM fdic_raw GROUP BY REPDTE ORDER BY REPDTE;
SELECT CERT, NAME, REPDTE, DRLNLS, CRLNLS, NTLNLS
FROM fdic_raw WHERE ABS(DRLNLS-CRLNLS-NTLNLS)>1;
