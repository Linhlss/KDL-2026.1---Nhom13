-- TV2 source-only quality checks. The runner binds the file and report month.
WITH raw AS (
    SELECT "count", {{time_field}} AS business_month, annualized_adjusted_basic_pay
    FROM read_parquet(?)
), period AS (SELECT ? AS report_month)
SELECT count(*) AS records,
       sum(try_cast("count" AS BIGINT)) AS numeric_count_sum,
       count(*) FILTER (WHERE "count" IS DISTINCT FROM '1') AS invalid_count,
       count(*) FILTER (WHERE business_month IS NULL OR
           NOT regexp_full_match(business_month, '[0-9]{4}(0[1-9]|1[0-2])')) AS invalid_month,
       count(*) FILTER (WHERE business_month <> report_month) AS different_month,
       count(*) FILTER (WHERE annualized_adjusted_basic_pay IS NULL) AS pay_null,
       count(*) FILTER (WHERE TRIM(annualized_adjusted_basic_pay) = '') AS pay_empty,
       count(*) FILTER (WHERE UPPER(TRIM(annualized_adjusted_basic_pay)) = 'REDACTED') AS pay_redacted,
       count(*) FILTER (WHERE UPPER(TRIM(annualized_adjusted_basic_pay)) NOT IN ('', 'REDACTED')
           AND try_cast(annualized_adjusted_basic_pay AS DECIMAL(18,2)) IS NULL) AS pay_invalid,
       count(*) FILTER (WHERE try_cast(annualized_adjusted_basic_pay AS DECIMAL(18,2)) < 0)
           AS pay_negative
FROM raw CROSS JOIN period;
