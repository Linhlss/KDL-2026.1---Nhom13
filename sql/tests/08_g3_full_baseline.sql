\set ON_ERROR_STOP on
-- Explicit acceptance assertions for the TV2 12-file baseline, not just SELECT success.
DO $$
DECLARE item record; layer text; target text; actual bigint; measure numeric;
BEGIN
  IF (SELECT count(*) FROM raw_meta.source_file WHERE is_active AND status='LOADED'
      AND report_month BETWEEN '202503' AND '202506') <> 12 THEN
    RAISE EXCEPTION 'Expected 12 active LOADED baseline files';
  END IF;
  FOR item IN
    SELECT f.*, CASE family WHEN 'employment' THEN 'fact_employment_snapshot'
      ELSE 'fact_'||family END AS fact_name FROM raw_meta.source_file f
    WHERE is_active AND status='LOADED' AND report_month BETWEEN '202503' AND '202506'
  LOOP
    FOREACH layer IN ARRAY ARRAY['staging','ods','dw'] LOOP
      target := CASE layer WHEN 'staging' THEN item.family||'_record'
        WHEN 'ods' THEN 'ods_'||item.family||'_record' ELSE item.fact_name END;
      EXECUTE format('SELECT count(*) FROM %I.%I WHERE file_id=$1',layer,target)
        INTO actual USING item.file_id;
      IF actual <> item.row_count THEN
        RAISE EXCEPTION 'Row difference file % layer %: % <> %',item.filename,layer,actual,item.row_count;
      END IF;
    END LOOP;
    EXECUTE format('SELECT sum(count_value) FROM dw.%I WHERE file_id=$1',item.fact_name)
      INTO measure USING item.file_id;
    IF measure IS DISTINCT FROM item.row_count::numeric THEN
      RAISE EXCEPTION 'Fact measure difference for %',item.filename;
    END IF;
  END LOOP;
  FOR item IN SELECT * FROM (VALUES
    (202503,2289192,4862,22061), (202504,2271969,7153,24088),
    (202505,2255056,8813,26415), (202506,2241780,9954,19947)
  ) b(month_key,employment,accessions,separations)
  LOOP
    SELECT sum(headcount) INTO measure FROM mart.workforce_monthly WHERE month_key=item.month_key;
    IF measure IS DISTINCT FROM item.employment::numeric THEN RAISE EXCEPTION 'K01 mismatch %',item.month_key; END IF;
    SELECT sum(accessions) INTO measure FROM mart.personnel_flows_monthly WHERE month_key=item.month_key;
    IF measure IS DISTINCT FROM item.accessions::numeric THEN RAISE EXCEPTION 'K06 mismatch %',item.month_key; END IF;
    SELECT sum(separations) INTO measure FROM mart.personnel_flows_monthly WHERE month_key=item.month_key;
    IF measure IS DISTINCT FROM item.separations::numeric THEN RAISE EXCEPTION 'K07 mismatch %',item.month_key; END IF;
  END LOOP;
  RAISE NOTICE 'PASS 12-file Source/Staging/ODS/Fact and four-month Mart baseline';
END $$;
