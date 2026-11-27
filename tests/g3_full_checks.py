"""Synthetic four-month orchestration, exact rerun and failure gates; no HR baseline substituted."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'etl'))
import g3_pipeline as g3
from g2_pipeline import rows, write_csv
from g2_model import build_model
from g2_test_support import temporary_database


def require(value,message):
    if not value: raise AssertionError(message)


def fixture(directory, family, month):
    time='snapshot_yyyymm' if family=='employment' else 'personnel_action_effective_date_yyyymm'
    table=pa.table({name:pa.array(values,type=pa.string()) for name,values in {
        'count':['1','1'], 'agency_code':['AA',family+'_FIXTURE'],
        'annualized_adjusted_basic_pay':[None,'REDACTED'],
        time:[month,month], 'occupational_series_code':['0018','0343']}.items()})
    path=directory/f'{family}_{month}_v5.parquet'
    pq.write_table(table,path)
    schema='|'.join(f'{field.name}:{field.type}' for field in table.schema)
    return dict(family=family,report_month=month,version='v5',filename=path.name,
                size_bytes=str(path.stat().st_size),row_count='2',column_count=str(len(table.schema)),
                schema_hash=hashlib.sha256(schema.encode()).hexdigest()[:16],
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_url='synthetic-g3-regression')


def check(config):
    with TemporaryDirectory(prefix='g3-fixtures-') as name, temporary_database(config) as conn:
        directory=Path(name)
        records=[fixture(directory,family,month) for month in g3.MONTHS for family in g3.FAMILIES]
        inventory=directory/'inventory.csv'
        write_csv(inventory,records)
        (directory/'data/manifest').mkdir(parents=True)
        manifest=directory/'data/manifest/sha256.txt'
        manifest.write_text(''.join(f"{r['sha256']}  {r['filename']}\n" for r in records),encoding='utf-8')
        output=directory/'reports'
        command=['g3_pipeline.py','--config',str(config),'--database',conn.info.dbname,
                 '--raw-dir',str(directory),'--inventory',str(inventory),'--report-dir',str(output),'--verify-rerun','--quality-check']
        # Only provenance Git queries and manifest location are isolated; every SQL/COPY/model/CLI parser is real.
        with patch.object(g3,'ROOT',directory), patch.object(sys,'argv',command), patch.object(g3.subprocess,'check_output',side_effect=['synthetic-test-commit\n','']):
            require(g3.main()==0,'Full four-month orchestration failed')
        require(len(rows(output/'07_file_counts.csv'))==12,'Full file coverage lost')
        results=rows(output/'07_reconciliation.csv')
        require(sum(r['status']=='PASS' for r in results)==84,'Expected 84 technical PASS')
        require(sum(r['status']=='PENDING' for r in results)==12,'DAX must stay PENDING')
        require(len(rows(output/'07_before_after.csv'))==48,'Before-after must include all 12 files and four rules')
        require(all(r['status']=='PASS' for r in rows(output/'09_quality_checks.csv')),'Direct quality/FK/time checks failed')
        require(all(r['status']=='PASS' for r in rows(output/'TV3_week3_rerun_results.csv')),'Rerun changed business data')
        require(conn.execute("SELECT count(*) FROM audit.load_run WHERE status='SKIPPED'").fetchone()[0]==6,'May source rerun not skipped')
        print('PASS four months / 12 files, report coverage, 84 technical PASS + 12 pending DAX, May skip and all-table business digests')
        before=g3.snapshot(conn)
        conn.execute("UPDATE dw.fact_accessions SET agency_code='CHANGED' WHERE file_id=2 AND source_row_ordinal=1")
        after=g3.snapshot(conn)
        try: g3.compare_snapshots(before,after,directory/'expected-failure.csv')
        except ValueError: pass
        else: raise AssertionError('Same totals but changed business field passed')
        print('PASS same-count business mutation is detected by stable ordered typed digests')
        try:
            with conn.transaction():
                conn.execute("UPDATE ods.ods_employment_record SET count_value=2 WHERE source_row_ordinal=1")
                build_model(conn,'202505')
        except ValueError: pass
        else: raise AssertionError('Count 2 violated one-source-row grain without blocking')
        require(conn.execute('SELECT sum(headcount) FROM mart.workforce_monthly').fetchone()[0]==8,'Invalid count damaged Mart')
        print('PASS count != 1 blocks model publication and preserves existing Mart')
        # Re-enter with a missing source: J00 FAIL and current FAIL export must survive.
        (directory/records[0]['filename']).unlink()
        with patch.object(g3,'ROOT',directory), patch.object(sys,'argv',command), patch.object(g3.subprocess,'check_output',side_effect=['synthetic-test-commit\n','']):
            require(g3.main()==1,'Missing file falsely completed')
        require(json.loads((output/'run_manifest.json').read_text(encoding='utf-8'))['status']=='FAIL','Run manifest falsely SUCCESS')
        require(any(r['status']=='FAIL' and r['job']=='J00' for r in rows(output/'07_load_log.csv')),'Failure missing from exported load log')
        require(conn.execute('SELECT sum(headcount) FROM mart.workforce_monthly').fetchone()[0]==8,'Source failure damaged valid Mart')
        print('PASS failed run exports J00 FAIL, records FAIL manifest and preserves previously valid data')
    print('PASS disposable four-month fixtures and database removed')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/.env')
    check(parser.parse_args().config.resolve())
