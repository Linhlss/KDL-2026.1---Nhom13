"""Run the inventoried full baseline and verify May rerun without changing G2 reports."""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from psycopg import sql

from g2_model import FACTS, build_model
from g2_pipeline import (ROOT, FAMILIES, before_after, connect, export_logs, finish_run,
                         initialize, reconciliation, resolve_config, rows, safe_error,
                         selected_sources, source_load, start_run, validate_month, write_csv)

MONTHS = ('202503', '202504', '202505', '202506')


def audited(conn, job, month, version, operation):
    meta = dict(family='employment', report_month=month, version='model' if job=='J03-J05' else 'check',
                filename='G3_'+job, sha256='', row_count='0')
    run_id = start_run(conn, job, meta, version)
    start = perf_counter()
    try:
        result = operation()
        finish_run(conn, run_id, 'SUCCESS', start)
        return result
    except Exception as error:
        finish_run(conn, run_id, 'FAIL', start, error=safe_error(error))
        raise


def model(conn, month):
    with conn.transaction():
        result = build_model(conn, month)
    print(json.dumps(result), flush=True)
    return result


def snapshot(conn):
    """Stable binary COPY digests: same typed columns and primary-key order per table.

    Source identities cover every ordinal (PK enforced); Facts/Dimensions/Marts
    cover every business column. Operational audit/timestamps are excluded.
    """
    tables = [('raw_meta.source_file', 'file_id,family,report_month,version,filename,sha256,'
               'schema_hash,size_bytes,row_count,column_count,is_active,status', 'file_id')]
    for family in FAMILIES:
        tables.extend([(f'staging.{family}_record', 'file_id,source_row_ordinal', 'file_id,source_row_ordinal'),
                       (f'ods.ods_{family}_record', 'file_id,source_row_ordinal', 'file_id,source_row_ordinal'),
                       (f'dw.{FACTS[family]}', '*', 'file_id,source_row_ordinal')])
    tables.extend([('dw.dim_month','*','month_key'), ('dw.dim_agency','*','agency_key'),
                   ('dw.dim_action_category','*','category_key'),
                   ('mart.workforce_monthly','*','month_key,agency_key'),
                   ('mart.personnel_flows_monthly','*','month_key,agency_key'),
                   ('mart.personnel_flows_category_monthly','*','month_key,agency_key,family,category_key'),
                   ('mart.dq_coverage_monthly','*','month_key,family,lookup_field')])
    result = {}
    with conn.transaction():
        conn.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
        for table, columns, order in tables:
            digest = hashlib.sha256()
            with conn.cursor().copy(f'COPY (SELECT {columns} FROM {table} ORDER BY {order}) TO STDOUT (FORMAT BINARY)') as reader:
                for block in reader:
                    digest.update(block)
            count = conn.execute('SELECT count(*) FROM '+table).fetchone()[0]
            result[table] = dict(rows=count, sha256=digest.hexdigest())
            print('SNAPSHOT', table, count, digest.hexdigest(), flush=True)
    return result


def compare_snapshots(before, after, path):
    result = [dict(test_id='T06', table=table, expected_rows=left['rows'], actual_rows=after[table]['rows'],
                   expected=left['sha256'], actual=after[table]['sha256'],
                   delta=after[table]['rows']-left['rows'],
                   status='PASS' if left==after[table] else 'FAIL',
                   scope='all persisted months; source identities and all model business columns',
                   reviewer='TV3; PENDING independent TV5', tested_at=datetime.now(UTC).isoformat())
              for table,left in before.items()]
    write_csv(path, result)
    if any(row['status']=='FAIL' for row in result):
        raise ValueError('Rerun changed business data; inspect before/after snapshots')
    return result


def export_g3_logs(conn, directory):
    export_logs(conn, directory)
    logs = rows(directory/'07_load_log.csv')
    for record in logs:
        success = record['status']=='SUCCESS'
        record['rows_read'] = record['actual_rows'] if record['status'] in ('SUCCESS','SKIPPED') and record['job'] in ('J00','J01','J02') else ''
        record['rows_written'] = record['actual_rows'] if success and record['job'] in ('J01','J02') else 0
        record['rows_rejected'] = 0 if record['status'] in ('SUCCESS','SKIPPED') else ''
    write_csv(directory/'07_load_log.csv', logs)


def report(conn, args, selected, version):
    checks, changes, counts = [], [], []
    now = datetime.now(UTC).isoformat()
    for month in args.months:
        directory = args.report_dir/'monthly'/month
        records = audited(conn, 'J06', month, version, lambda: reconciliation(conn, month, directory))
        before_after(conn, month, directory)
        changes.extend(rows(directory/'07_before_after.csv'))
        for item in records:
            source = next(s for s in selected if s['report_month']==month and s['family']==item['family'])
            item.update(test_id='T01/T02/T05' if item['check']!='powerbi_dax' else 'T09',
                        input_version=source['version']+':'+source['sha256'],
                        layer_table=item['check'], grain_filter=f"{item['family']}/report_month={month}/active LOADED",
                        delta=int(item['actual'])-int(item['expected']) if item['actual']!='' else '',
                        evidence=f'monthly/{month}/07_reconciliation.csv', tested_at=now)
            checks.append(item)
    for source in selected:
        family, month = source['family'], source['report_month']
        file_id = conn.execute('SELECT file_id FROM raw_meta.source_file WHERE family=%s AND report_month=%s AND is_active AND status=\'LOADED\'', (family,month)).fetchone()[0]
        record = dict(family=family, report_month=month, filename=source['filename'], file_id=file_id,
                      input_version=source['version'], sha256=source['sha256'], expected=int(source['row_count']))
        for layer, table in [('staging',f'{family}_record'),('ods',f'ods_{family}_record'),('dw',FACTS[family])]:
            record[layer] = conn.execute(sql.SQL('SELECT count(*) FROM {}.{} WHERE file_id=%s').format(sql.Identifier(layer),sql.Identifier(table)), (file_id,)).fetchone()[0]
        record.update(status='PASS' if all(record[k]==record['expected'] for k in ('staging','ods','dw')) else 'FAIL')
        counts.append(record)
    write_csv(args.report_dir/'07_reconciliation.csv', checks)
    write_csv(args.report_dir/'07_before_after.csv', changes)
    write_csv(args.report_dir/'07_file_counts.csv', counts)
    export_g3_logs(conn,args.report_dir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'configs/.env')
    parser.add_argument('--database')
    parser.add_argument('--raw-dir', type=Path)
    parser.add_argument('--inventory', type=Path, default=ROOT/'docs/03_source_inventory.csv')
    parser.add_argument('--months', nargs='+', default=list(MONTHS))
    parser.add_argument('--report-dir', type=Path, default=ROOT/'reports/week3')
    parser.add_argument('--batch-size', type=int, default=10000)
    parser.add_argument('--job', choices=('all','check'), default='all')
    parser.add_argument('--verify-rerun', action='store_true', help='rerun full J00-J06 chain for May and compare all persisted business data')
    parser.add_argument('--quality-check', action='store_true', help='verify every raw file against ODS, time roles, keys and FKs')
    args=parser.parse_args()
    if not args.config.is_file() or args.batch_size<1: parser.error('config and positive batch size required')
    try:
        if len(set(args.months))!=len(args.months): raise ValueError('duplicate requested month')
        args.months=sorted(validate_month(month) for month in args.months)
        inventory=rows(args.inventory)
        selected=[item for month in args.months for item in selected_sources(inventory,month)]
        manifest=dict(line.strip().split(None,1)[::-1] for line in (ROOT/'data/manifest/sha256.txt').read_text(encoding='utf-8').splitlines() if line.strip())
        if len({item['filename'] for item in inventory})!=len(inventory) or any(manifest.get(item['filename'])!=item['sha256'] for item in inventory):
            raise ValueError('inventory filenames/TV2 SHA manifest disagree')
        if args.verify_rerun and '202505' not in args.months: raise ValueError('May must be included for rerun verification')
    except ValueError as error:
        parser.error(str(error))
    resolve_config(args)
    version=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain','--','etl','sql','tests'],cwd=ROOT,text=True): version+='+working-tree'
    args.report_dir.mkdir(parents=True,exist_ok=True)
    run_manifest=dict(code_version=version, inventory_sha256=hashlib.sha256(args.inventory.read_bytes()).hexdigest(),
                      code_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in (ROOT/'etl').glob('*.py')},
                      months=args.months, database=args.database, batch_size=args.batch_size,
                      started_at=datetime.now(UTC).isoformat(), model_status='PROPOSED_PENDING_TV4', status='RUNNING')
    manifest_path=args.report_dir/'run_manifest.json'
    manifest_path.write_text(json.dumps(run_manifest,indent=2),encoding='utf-8')
    try:
        with connect(args) as conn:
            # Prevent concurrent G3 orchestration/rerun from changing snapshot scope.
            conn.execute("SELECT pg_advisory_lock(hashtext('tv3/g3-pipeline'))")
            try:
                if args.job=='all':
                    initialize(conn)
                    for month in args.months:
                        for item in selected_sources(inventory,month): source_load(conn,args,item,version)
                        audited(conn,'J03-J05',month,version,lambda: model(conn,month))
                report(conn,args,selected,version)
                if args.verify_rerun:
                    before=snapshot(conn)
                    (args.report_dir/'rerun_before.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
                    for item in selected_sources(inventory,'202505'): source_load(conn,args,item,version)
                    audited(conn,'J03-J05','202505',version,lambda: model(conn,'202505'))
                    report(conn,args,selected,version)
                    after=snapshot(conn)
                    (args.report_dir/'rerun_after.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
                    compare_snapshots(before,after,args.report_dir/'TV3_week3_rerun_results.csv')
                    print('PASS May rerun: full baseline identities, stable Dimension keys, all Facts and Marts unchanged',flush=True)
                if args.quality_check:
                    from g3_quality import export_quality
                    export_quality(conn,args,selected)
            finally:
                export_g3_logs(conn,args.report_dir)
                conn.execute("SELECT pg_advisory_unlock(hashtext('tv3/g3-pipeline'))")
        run_manifest['status']='SUCCESS'
    except Exception as error:
        run_manifest.update(status='FAIL', error=safe_error(error))
        print('FAIL '+safe_error(error),file=sys.stderr)
        return 1
    finally:
        run_manifest['finished_at']=datetime.now(UTC).isoformat()
        manifest_path.write_text(json.dumps(run_manifest,indent=2),encoding='utf-8')
    print('Completed G3 technical run; TV4 model approval / TV5 independent QA pending',flush=True)
    return 0


if __name__=='__main__':
    sys.exit(main())
