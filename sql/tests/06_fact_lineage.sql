WITH lineage AS (
    SELECT file_id, source_row_ordinal, 'ODS' AS side FROM {{ods_table}}
    UNION ALL
    SELECT file_id, source_row_ordinal, 'FACT' AS side FROM {{fact_table}}
), key_counts AS (
    SELECT file_id, source_row_ordinal,
           count(*) FILTER (WHERE side = 'ODS') AS ods_rows,
           count(*) FILTER (WHERE side = 'FACT') AS fact_rows
    FROM lineage
    GROUP BY file_id, source_row_ordinal
)
SELECT k.file_id, k.source_row_ordinal, v.finding, k.ods_rows, k.fact_rows
FROM key_counts k
CROSS JOIN LATERAL (VALUES
    ('NULL_ODS_KEY', (k.file_id IS NULL OR k.source_row_ordinal IS NULL) AND k.ods_rows > 0),
    ('NULL_FACT_KEY', (k.file_id IS NULL OR k.source_row_ordinal IS NULL) AND k.fact_rows > 0),
    ('MISSING_FACT_KEY', k.file_id IS NOT NULL AND k.source_row_ordinal IS NOT NULL
                        AND k.ods_rows > 0 AND k.fact_rows = 0),
    ('EXTRA_FACT_KEY', k.file_id IS NOT NULL AND k.source_row_ordinal IS NOT NULL
                      AND k.ods_rows = 0 AND k.fact_rows > 0),
    ('DUPLICATE_ODS_KEY', k.ods_rows > 1),
    ('DUPLICATE_FACT_KEY', k.fact_rows > 1)
) AS v(finding, applies)
WHERE v.applies
