-- L3-15 benchmark queries (issue #55). Run on a SEPARATE benchmark database, never on the
-- handoff database: B2 creates and drops indexes. Driver: evidence/TV3_week4/run_benchmark.py
-- (EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON), 1 warm-up + 3 measured runs per variant).

-- name: B1-FACT  | K01 by agency, April 2025, from the 9,057,997-row Employment Fact
SELECT a.agency_code, sum(f.count_value) AS headcount
FROM dw.fact_employment_snapshot f JOIN dw.dim_agency a USING (agency_key)
WHERE f.snapshot_month_key = 202504
GROUP BY a.agency_code;

-- name: B1-MART  | same question from the aggregate Mart
SELECT agency_code, sum(headcount) AS headcount
FROM mart.workforce_monthly
WHERE month_key = 202504
GROUP BY agency_code;

-- name: B1-CHECK | must return 0: both directions of EXCEPT between B1-FACT and B1-MART
SELECT count(*) FROM (
  (SELECT a.agency_code, sum(f.count_value) FROM dw.fact_employment_snapshot f
   JOIN dw.dim_agency a USING (agency_key) WHERE f.snapshot_month_key = 202504 GROUP BY 1
   EXCEPT SELECT agency_code, sum(headcount) FROM mart.workforce_monthly WHERE month_key = 202504 GROUP BY 1)
  UNION ALL
  (SELECT agency_code, sum(headcount) FROM mart.workforce_monthly WHERE month_key = 202504 GROUP BY 1
   EXCEPT SELECT a.agency_code, sum(f.count_value) FROM dw.fact_employment_snapshot f
   JOIN dw.dim_agency a USING (agency_key) WHERE f.snapshot_month_key = 202504 GROUP BY 1)
) d;

-- name: B2-SEP   | events by effective month for one agency (Treasury) — run BEFORE/AFTER
--                  CREATE INDEX bench_sep_agency ON dw.fact_separations (agency_code, effective_month_key)
SELECT effective_month_key, sum(count_value) AS events
FROM dw.fact_separations WHERE agency_code = 'TR'
GROUP BY effective_month_key;

-- name: B2-EMP   | headcount by snapshot month for one agency (Treasury) — run BEFORE/AFTER
--                  CREATE INDEX bench_emp_agency ON dw.fact_employment_snapshot (agency_code, snapshot_month_key)
SELECT snapshot_month_key, sum(count_value) AS headcount
FROM dw.fact_employment_snapshot WHERE agency_code = 'TR'
GROUP BY snapshot_month_key;
