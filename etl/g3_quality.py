"""Direct raw/ODS quality, source identity, time-role and physical FK evidence."""
import json
import sys
from datetime import UTC, datetime

from psycopg import sql
from g2_pipeline import ROOT, FAMILIES, rows, verify_file, write_csv
from g2_model import FACTS

sys.path.insert(0,str(ROOT/'evidence/TV3_week2'))
from reconcile_sources import source_metrics


def export_quality(conn, args, selected):
    checks, quality = [], []
    now=datetime.now(UTC).isoformat()

    def add(item, name, expected, actual):
        checks.append(dict(test_id=name,task_id='L3-11/L3-13',family=item['family'],
                           report_month=item['report_month'],input_version=item['version']+':'+item['sha256'],
                           layer_table='ODS/Fact/Dimension',grain_filter=item['filename'],
                           expected=expected,actual=actual,delta=actual-expected,
                           status='PASS' if actual==expected else 'FAIL',
                           evidence='09_quality_checks.csv',reviewer='TV3; PENDING independent TV5',tested_at=now))
    for item in selected:
        family, month=item['family'],item['report_month']
        path=args.raw_dir/item['filename']
        if not path.is_file(): path=args.raw_dir/family/item['filename']
        verify_file(path,item)
        registered=conn.execute('SELECT file_id,filename,sha256,row_count FROM raw_meta.source_file WHERE family=%s AND report_month=%s AND is_active AND status=\'LOADED\'',(family,month)).fetchall()
        if len(registered)!=1 or registered[0][1:]!=(item['filename'],item['sha256'],int(item['row_count'])):
            raise ValueError('Active source identity differs from verified inventory')
        file_id=registered[0][0]
        expected=source_metrics(path,family,month)
        time='snapshot_yyyymm' if family=='employment' else 'effective_month'
        table=sql.Identifier('ods',f'ods_{family}_record')
        actual=dict(zip(expected,conn.execute(sql.SQL('''
          SELECT count(*),count(*) FILTER(WHERE "count" IS DISTINCT FROM '1'),
          count(*) FILTER(WHERE pay_state='NULL'),count(*) FILTER(WHERE pay_state='EMPTY'),
          count(*) FILTER(WHERE pay_state='REDACTED'),count(*) FILTER(WHERE {time}<>%s),
          count(*) FILTER(WHERE occupational_series_code ~ '^0[0-9]')
          FROM {table} WHERE file_id=%s
        ''').format(time=sql.Identifier(time),table=table),(month,file_id)).fetchone(),strict=True))
        for key,value in expected.items(): add(item,'T04_'+key,value,actual[key])
        ordinal=conn.execute(sql.SQL('SELECT count(DISTINCT source_row_ordinal),min(source_row_ordinal),max(source_row_ordinal) FROM {} WHERE file_id=%s').format(table),(file_id,)).fetchone()
        for key,value,got in zip(('distinct_ordinals','min_ordinal','max_ordinal'),(int(item['row_count']),1,int(item['row_count'])),ordinal,strict=True):
            add(item,'T02_'+key,value,got)
        fact=sql.Identifier('dw',FACTS[family])
        business='snapshot_month_key' if family=='employment' else 'effective_month_key'
        orphan=conn.execute(sql.SQL('''SELECT count(*) FROM {fact} f
          LEFT JOIN dw.dim_month r ON r.month_key=f.report_month_key
          LEFT JOIN dw.dim_month b ON b.month_key=f.{business}
          LEFT JOIN dw.dim_agency a ON a.agency_key=f.agency_key
          WHERE file_id=%s AND (r.month_key IS NULL OR b.month_key IS NULL OR a.agency_key IS NULL)
        ''').format(fact=fact,business=sql.Identifier(business)),(file_id,)).fetchone()[0]
        add(item,'T03_month_agency_orphans',0,orphan)
        time_differences=conn.execute(sql.SQL('''SELECT count(*) FROM {fact} f JOIN {ods} o USING(file_id,source_row_ordinal)
          WHERE file_id=%s AND (f.report_month_key<>%s OR f.{business} IS DISTINCT FROM
          CASE WHEN o.{time} ~ '^[0-9]{{4}}(0[1-9]|1[0-2])$' THEN o.{time}::integer ELSE 0 END)
        ''').format(fact=fact,ods=table,business=sql.Identifier(business),time=sql.Identifier(time)),(file_id,int(month))).fetchone()[0]
        add(item,'T04_fact_time_roles',0,time_differences)
        if family!='employment':
            orphan=conn.execute(sql.SQL('SELECT count(*) FROM {} f LEFT JOIN dw.dim_action_category c USING(category_key) WHERE file_id=%s AND c.category_key IS NULL').format(fact),(file_id,)).fetchone()[0]
            add(item,'T03_category_orphans',0,orphan)
        unknown=conn.execute(sql.SQL('SELECT count(*) FROM {} WHERE file_id=%s AND agency_key=0').format(fact),(file_id,)).fetchone()[0]
        quality.append(dict(family=family,report_month=month,file_id=file_id,**actual,unknown_agency_rows=unknown,
                            provenance='DERIVED_LOOKUP; PARTIAL',reviewer='PENDING TV2/TV4/TV5'))
    write_csv(args.report_dir/'09_quality_checks.csv',checks)
    write_csv(args.report_dir/'09_source_quality.csv',quality)
    catalog=[]
    dimensions=[('dim_month','month_key','yyyymm','one valid YYYYMM; snapshot/report/effective roles'),
                ('dim_agency','agency_key','month_key,agency_code','one agency code in one report month'),
                ('dim_action_category','category_key','month_key,family,category_code','one family-specific category code in one report month')]
    for name,key,natural,grain in dimensions:
        table=sql.Identifier('dw',name)
        count=conn.execute(sql.SQL('SELECT count(*) FROM {}').format(table)).fetchone()[0]
        samples=conn.execute(sql.SQL('SELECT row_to_json(d) FROM {} d WHERE {}<>0 ORDER BY {} LIMIT 3').format(table,sql.Identifier(key),sql.Identifier(key))).fetchall()
        duplicates=conn.execute(sql.SQL('SELECT count(*) FROM (SELECT '+natural+' FROM {} GROUP BY '+natural+' HAVING count(*)>1) d').format(table)).fetchone()[0]
        if duplicates: raise ValueError('Duplicate Dimension natural key')
        catalog.append(dict(table='dw.'+name,grain=grain,natural_key=natural,surrogate_key=key,actual_rows=count,
                            unknown_key=0,version_policy='calendar' if name=='dim_month' else 'key scoped by report month; stable upsert',
                            provenance='source months' if name=='dim_month' else 'data/reference/derived_lookup_g2.csv; DERIVED_LOOKUP; PARTIAL',
                            hierarchy='not asserted; pending TV4',fact_usage='all three Facts',
                            examples=json.dumps([s[0] for s in samples],ensure_ascii=False),approval='PROPOSED_PENDING_TV4'))
    write_csv(args.report_dir/'08_dimension_observed.csv',catalog)
    constraints=[dict(zip(('table','constraint','kind','validated'),row,strict=True)) for row in conn.execute('''
      SELECT conrelid::regclass::text,conname,contype,convalidated FROM pg_constraint
      WHERE connamespace IN ('dw'::regnamespace,'ods'::regnamespace,'staging'::regnamespace,'mart'::regnamespace)
      ORDER BY 1,2
    ''')]
    write_csv(args.report_dir/'09_constraints.csv',constraints)
    if any(not c['validated'] for c in constraints) or any(r['status']=='FAIL' for r in checks):
        raise ValueError('G3 quality/identity/FK/time reconciliation failed')
    print(f'PASS {len(checks)} direct raw/ODS, ordinal, time-role and FK checks; Dimension uniqueness and constraints validated',flush=True)
