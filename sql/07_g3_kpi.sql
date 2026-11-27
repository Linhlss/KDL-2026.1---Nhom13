\set ON_ERROR_STOP on
-- Snapshot totals are separate observations, never unique people across months.
WITH workforce AS (
  SELECT month_key, sum(headcount) AS k01
  FROM mart.workforce_monthly GROUP BY month_key
), previous AS (
  SELECT w.*, p.k01 AS previous_headcount
  FROM workforce w LEFT JOIN workforce p ON p.month_key =
    to_char(to_date(w.month_key::text,'YYYYMM') - interval '1 month','YYYYMM')::integer
), flows AS (
  SELECT month_key,sum(accessions) AS k06,sum(separations) AS k07
  FROM mart.personnel_flows_monthly GROUP BY month_key
)
SELECT w.month_key,k01,k01-previous_headcount AS k02,
       (k01-previous_headcount)/nullif(previous_headcount,0) AS k03,
       k06,k07,k06-k07 AS k08
FROM previous w LEFT JOIN flows USING(month_key) ORDER BY month_key;

-- Match a Power BI Dimension filter to SQL using agency_code across scoped keys.
-- FULL JOIN keeps agencies that have flows but no headcount row in that month.
SELECT month_key,agency_key,
       coalesce(w.agency_code,f.agency_code) AS agency_code,
       coalesce(w.agency_label,f.agency_label) AS agency_label,
       coalesce(w.headcount,0) AS headcount,
       coalesce(f.accessions,0) AS accessions,coalesce(f.separations,0) AS separations
FROM mart.workforce_monthly w
FULL JOIN mart.personnel_flows_monthly f USING(month_key,agency_key)
ORDER BY month_key,agency_code;

-- D2 reference (issue #51): events by report month, family and action category; key 0 kept.
SELECT month_key,family,category_key,category_code,category_label,
       sum(events) AS events,sum(source_rows) AS source_rows
FROM mart.personnel_flows_category_monthly
GROUP BY month_key,family,category_key,category_code,category_label
ORDER BY month_key,family,events DESC;

-- K10 reference (issue #52): official % only where TV2 marked VERIFIED/COMPLETE; otherwise BLANK.
-- dw_* columns show how the DW lookup actually resolved the field (not an official coverage claim).
SELECT month_key,family,lookup_field,lookup_status,reference_coverage,eligible_rows,
       official_matched_rows,official_coverage_pct,
       dw_total_rows,dw_matched_rows,dw_unknown_rows,dw_null_rows,dw_empty_rows,dw_redacted_rows
FROM mart.dq_coverage_monthly
ORDER BY month_key,family,lookup_field;
