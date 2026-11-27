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
