-- TV2 exact code/label observations. The runner supplies identifier-quoted fields.
-- Grouping the raw observations preserves all rows and raw missing-value states.
SELECT {{keys}}, {{label}} AS observed_label, count(*) AS records
FROM read_parquet(?)
GROUP BY ALL
ORDER BY ALL;
