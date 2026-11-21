\set ON_ERROR_STOP on
-- Run psql -v month=202504 -f sql/05_g2_kpi.sql.
-- K01 is one snapshot; K06/K07 use report month.
SELECT 'K01' AS kpi, month_key, sum(headcount) AS value
FROM mart.workforce_monthly WHERE month_key = :month
GROUP BY month_key;

SELECT 'K06' AS kpi, month_key, sum(accessions) AS value
FROM mart.personnel_flows_monthly WHERE month_key = :month
GROUP BY month_key
UNION ALL
SELECT 'K07', month_key, sum(separations)
FROM mart.personnel_flows_monthly WHERE month_key = :month
GROUP BY month_key;

-- Agency filter reference for the Power BI slicer.
SELECT month_key, agency_code, agency_label, headcount
FROM mart.workforce_monthly WHERE month_key = :month
ORDER BY agency_code;
