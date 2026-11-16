\set ON_ERROR_STOP on
-- Pass target, expected_rows, expected_sha256 and expected_source_columns with psql -v.
-- target is the unqualified name of one prototype table in staging.
\pset null 'NULL'

SELECT count(*) AS sql_count,
       count(DISTINCT source_row_ordinal) AS distinct_ordinals,
       min(source_row_ordinal) AS first_ordinal,
       max(source_row_ordinal) AS last_ordinal,
       count(*) - count(DISTINCT (source_file_sha256, source_row_ordinal)) AS duplicate_source_keys,
       count(*) FILTER (WHERE source_file_sha256 <> :'expected_sha256') AS wrong_source_hashes
FROM staging.:"target";

SELECT data_type, count(*) AS columns
FROM information_schema.columns
WHERE table_schema = 'staging' AND table_name = :'target'
GROUP BY data_type
ORDER BY data_type;

SELECT field,
       count(*) FILTER (WHERE val IS NULL) AS nulls,
       count(*) FILTER (WHERE val = '') AS empty,
       count(*) FILTER (WHERE val = 'REDACTED') AS redacted,
       count(*) FILTER (WHERE val = '0') AS zero,
       count(*) FILTER (WHERE val ~ '^0[0-9]') AS leading_zero
FROM staging.:"target"
CROSS JOIN LATERAL (VALUES
    ('agency_code', agency_code),
    ('agency_subelement_code', agency_subelement_code),
    ('occupational_series_code', occupational_series_code),
    ('duty_station_code', duty_station_code),
    ('pay_plan_code', pay_plan_code),
    ('grade', grade),
    ('annualized_adjusted_basic_pay', annualized_adjusted_basic_pay),
    ('count', "count")
) AS raw(field, val)
GROUP BY field
ORDER BY field;

SELECT count(*) = :expected_rows
   AND count(DISTINCT source_row_ordinal) = :expected_rows
   AND min(source_row_ordinal) = 1
   AND max(source_row_ordinal) = :expected_rows
   AND count(*) FILTER (WHERE source_file_sha256 <> :'expected_sha256') = 0
   AND (
       SELECT count(*) = :expected_source_columns
          AND bool_and(data_type = 'text')
       FROM information_schema.columns
       WHERE table_schema = 'staging' AND table_name = :'target'
         AND column_name NOT IN ('source_file_sha256', 'source_row_ordinal')
   ) AS checks_passed
FROM staging.:"target"
\gset
\if :checks_passed
    \echo PASS count, ordinal, checksum and source column types
\else
    DO $$ BEGIN RAISE EXCEPTION 'Prototype acceptance check failed'; END $$;
\endif
