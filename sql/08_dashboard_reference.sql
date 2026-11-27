-- L3-14 (issue #54): SQL reference for every KPI shown on D1–D3, read only from the handoff
-- database (Dimensions + Marts). Each block is named; evidence/TV3_week4/build_sql_dax_reference.py
-- runs them and writes reports/week4/sql_dax_reference.csv for TV4 to fill the DAX column.
-- Rules (docs/02_kpi_dictionary.csv):
--   * K01 is one snapshot; never add months together into "unique people".
--   * K02/K03 compare with the previous calendar month for the SAME agency_code
--     (agency_key is scoped by report month); missing previous month -> NULL (DAX BLANK).
--   * K04 denominator removes the agency filter but keeps the month filter.
--   * K06/K07 use the report month; K08 = K06 - K07 is not a net headcount change.
--   * K10 percentage exists only where TV2 marked the field VERIFIED/COMPLETE; else NULL (BLANK).
--   * Agency/category key 0 (Unknown) stays inside every total.

-- name: K01_K02_K03_TOTAL
WITH m AS (SELECT month_key, sum(headcount) AS k01 FROM mart.workforce_monthly GROUP BY month_key)
SELECT c.month_key, c.k01,
       c.k01 - p.k01 AS k02,
       round((c.k01 - p.k01)::numeric / nullif(p.k01, 0), 6) AS k03
FROM m c LEFT JOIN m p
  ON p.month_key = to_char(to_date(c.month_key::text, 'YYYYMM') - interval '1 month', 'YYYYMM')::integer
ORDER BY c.month_key;

-- name: K01_K02_K03_AGENCY
WITH a AS (SELECT month_key, agency_code, max(agency_label) AS agency_label, sum(headcount) AS k01
           FROM mart.workforce_monthly GROUP BY month_key, agency_code)
SELECT c.month_key, c.agency_code, c.agency_label, c.k01,
       c.k01 - p.k01 AS k02,
       round((c.k01 - p.k01)::numeric / nullif(p.k01, 0), 6) AS k03
FROM a c LEFT JOIN a p
  ON p.agency_code = c.agency_code
 AND p.month_key = to_char(to_date(c.month_key::text, 'YYYYMM') - interval '1 month', 'YYYYMM')::integer
ORDER BY c.month_key, c.agency_code;

-- name: K04_AGENCY_SHARE
SELECT month_key, agency_code, max(agency_label) AS agency_label, sum(headcount) AS agency_headcount,
       sum(sum(headcount)) OVER (PARTITION BY month_key) AS all_agencies_headcount,
       round(sum(headcount)::numeric / nullif(sum(sum(headcount)) OVER (PARTITION BY month_key), 0), 6) AS k04
FROM mart.workforce_monthly
GROUP BY month_key, agency_code
ORDER BY month_key, k04 DESC;

-- name: K06_K07_K08_TOTAL
SELECT month_key, sum(accessions) AS k06, sum(separations) AS k07,
       sum(accessions) - sum(separations) AS k08
FROM mart.personnel_flows_monthly GROUP BY month_key ORDER BY month_key;

-- name: K06_K07_K08_AGENCY
SELECT month_key, agency_code, max(agency_label) AS agency_label,
       sum(accessions) AS k06, sum(separations) AS k07, sum(accessions) - sum(separations) AS k08
FROM mart.personnel_flows_monthly GROUP BY month_key, agency_code ORDER BY month_key, agency_code;

-- name: K06_K07_CATEGORY
SELECT month_key, family, category_code, max(category_label) AS category_label,
       sum(events) AS events, sum(source_rows) AS source_rows
FROM mart.personnel_flows_category_monthly
GROUP BY month_key, family, category_code ORDER BY month_key, family, events DESC;

-- name: K10_COVERAGE
SELECT month_key, family, lookup_field, lookup_status, reference_coverage, eligible_rows,
       official_matched_rows,
       CASE WHEN lookup_status = 'VERIFIED' AND reference_coverage = 'COMPLETE'
            THEN round(official_matched_rows::numeric / nullif(eligible_rows, 0), 6) END AS k10,
       dw_total_rows, dw_matched_rows, dw_unknown_rows, dw_null_rows, dw_empty_rows, dw_redacted_rows
FROM mart.dq_coverage_monthly ORDER BY month_key, family, lookup_field;

-- name: UNKNOWN_CHECK
SELECT 'agency key 0 headcount' AS item, coalesce(sum(headcount), 0) AS value
FROM mart.workforce_monthly WHERE agency_key = 0
UNION ALL SELECT 'agency key 0 events', coalesce(sum(accessions + separations), 0)
FROM mart.personnel_flows_monthly WHERE agency_key = 0
UNION ALL SELECT 'category key 0 events', coalesce(sum(events), 0)
FROM mart.personnel_flows_category_monthly WHERE category_key = 0;
