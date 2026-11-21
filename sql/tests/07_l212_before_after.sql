-- TV2 binds report_month and the Parquet path. The runner supplies the
-- normalized projection with one row per original file ordinal.
SELECT count(*) AS after_rows, count(DISTINCT ordinal) AS unique_ordinals,
       count(*) FILTER (WHERE try_cast(raw_count AS BIGINT) = 1) AS parse_count,
       count(*) FILTER (WHERE business_month <> ?) AS different_month,
       count(*) FILTER (WHERE pay_state = 'NULL') AS pay_null,
       count(*) FILTER (WHERE pay_state = 'EMPTY') AS pay_empty,
       count(*) FILTER (WHERE pay_state = 'REDACTED') AS pay_redacted,
       count(*) FILTER (WHERE pay_state = 'PRESENT'
                        AND try_cast(raw_pay AS DECIMAL(18,2)) IS NULL) AS pay_invalid,
       count(*) FILTER (WHERE lookup_state = 'NULL') AS lookup_null,
       count(*) FILTER (WHERE lookup_state = 'EMPTY') AS lookup_empty,
       count(*) FILTER (WHERE lookup_state = 'REDACTED') AS lookup_redacted,
       count(*) FILTER (WHERE lookup_state = 'MATCHED') AS lookup_matched,
       count(*) FILTER (WHERE lookup_state = 'UNKNOWN') AS lookup_unknown,
       count(*) FILTER (WHERE lookup_state = 'AMBIGUOUS') AS lookup_ambiguous
FROM ({{normalized}}) measured;
