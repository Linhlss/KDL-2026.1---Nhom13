\set ON_ERROR_STOP on
-- Supply an unqualified staging prototype table name with psql -v target=....
-- Profiles the loaded file/sample only. Multiple labels per code require review.
WITH code_cells AS (
    SELECT field, code, label
    FROM staging.:"target"
    CROSS JOIN LATERAL (VALUES
        ('agency_code', agency_code, agency),
        ('occupational_series_code', occupational_series_code, occupational_series),
        ('duty_station_code', duty_station_code, duty_station_city),
        ('pay_plan_code', pay_plan_code, pay_plan)
    ) AS raw(field, code, label)
), quality AS (
    SELECT field, count(*) AS rows_profiled,
           count(*) FILTER (WHERE code IS NULL OR btrim(code) = '') AS null_or_blank,
           count(*) FILTER (WHERE code = 'REDACTED') AS redacted
    FROM code_cells
    GROUP BY field
), labels_per_code AS (
    SELECT field, code, count(DISTINCT label) FILTER (
        WHERE nullif(btrim(label), '') IS NOT NULL AND label <> 'REDACTED'
    ) AS label_count
    FROM code_cells
    WHERE nullif(btrim(code), '') IS NOT NULL AND code <> 'REDACTED'
    GROUP BY field, code
)
SELECT q.field, q.rows_profiled, q.null_or_blank, q.redacted,
       count(l.code) AS distinct_codes,
       count(l.code) FILTER (WHERE l.label_count = 0) AS codes_without_label,
       count(l.code) FILTER (WHERE l.label_count > 1) AS codes_with_multiple_labels
FROM quality q
LEFT JOIN labels_per_code l USING (field)
GROUP BY q.field, q.rows_profiled, q.null_or_blank, q.redacted
ORDER BY q.field;
