"""Create and restore-check a private full-period aggregate handoff; never commit its dump."""
import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from dotenv import dotenv_values
from psycopg import sql

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'etl'))
sys.path.insert(0,str(ROOT/'tests'))
from g2_pipeline import connect
from g2_transfer import TABLES
from g2_test_support import temporary_database


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/.env.g3.local')
    parser.add_argument('--database',required=True)
    parser.add_argument('--target',default='workforce_g3_transfer')
    parser.add_argument('--dump',type=Path,default=ROOT/'db_dumps/workforce_g3.dump')
    args=parser.parse_args()
    if args.dump.exists():parser.error('Dump already exists; select a new path to preserve the prior handoff')
    if args.target==args.database:parser.error('Target must be separate from source')
    config=dotenv_values(args.config,interpolate=False)
    env=dict(os.environ)
    env.update({k:str(config[k]) for k in ('PGHOST','PGPORT','PGUSER','PGPASSWORD') if config.get(k)})
    subprocess.run([sys.executable,str(ROOT/'etl/g2_transfer.py'),'--config',str(args.config),
                    '--source',args.database,'--target',args.target],check=True,cwd=ROOT)
    args.dump.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['pg_dump','-d',args.target,'-Fc','--no-owner','--no-acl','-f',str(args.dump)],env=env,check=True)
    digest=hashlib.sha256(args.dump.read_bytes()).hexdigest()
    args.dump.with_suffix('.dump.sha256').write_text(digest+'  '+args.dump.name+'\n',encoding='utf-8')
    print('PostgreSQL:',subprocess.check_output(['pg_dump','--version'],text=True).strip(),flush=True)
    print('Private dump:',args.dump.name,'bytes=',args.dump.stat().st_size,'SHA256=',digest,flush=True)
    with connect(args) as source, temporary_database(args.config) as restored:
        subprocess.run(['pg_restore','-d',restored.info.dbname,'--no-owner','--no-acl','--exit-on-error',str(args.dump)],env=env,check=True)
        actual={schema+'.'+table for schema,table in restored.execute("SELECT schemaname,tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema')")}
        if actual!=set(TABLES):raise ValueError('Unexpected restored tables')
        for name in TABLES:
            key={'dw.dim_month':'month_key','dw.dim_agency':'agency_key','dw.dim_action_category':'category_key',
                 'mart.personnel_flows_category_monthly':'month_key,agency_key,family,category_key',
                 'mart.dq_coverage_monthly':'month_key,family,lookup_field'}.get(name,'month_key,agency_key')
            query='SELECT * FROM '+name+' ORDER BY '+key
            expected=source.execute(query).fetchall()
            got=restored.execute(query).fetchall()
            if got!=expected:raise ValueError('Restored rows differ: '+name)
            print('PASS restored exact rows',name,len(got),flush=True)
        query='''SELECT w.month_key,sum(w.headcount),
          (SELECT sum(accessions) FROM mart.personnel_flows_monthly f WHERE f.month_key=w.month_key),
          (SELECT sum(separations) FROM mart.personnel_flows_monthly f WHERE f.month_key=w.month_key)
          FROM mart.workforce_monthly w GROUP BY w.month_key ORDER BY w.month_key'''
        kpis=restored.execute(query).fetchall()
        expected=[(202503,2289192,4862,22061),(202504,2271969,7153,24088),
                  (202505,2255056,8813,26415),(202506,2241780,9954,19947)]
        if kpis!=expected:raise ValueError('Restored KPI baseline differs')
        for row in kpis:print('PASS restored month / K01 / K06 / K07:',*row,flush=True)
        category=restored.execute('''SELECT month_key,
          sum(events) FILTER (WHERE family='accessions'),sum(events) FILTER (WHERE family='separations'),
          sum(events) FILTER (WHERE category_key=0)
          FROM mart.personnel_flows_category_monthly GROUP BY month_key ORDER BY month_key''').fetchall()
        if [(m,a,s) for m,a,s,_ in category]!=[(m,a,s) for m,_,a,s in expected]:
            raise ValueError('Restored category Mart does not split K06/K07 exactly')
        for m,a,s,unknown in category:print('PASS restored category Mart month / K06 / K07 / key0 events:',m,a,s,unknown,flush=True)
        dq=restored.execute('SELECT count(*),count(official_coverage_pct),count(dw_total_rows) FROM mart.dq_coverage_monthly').fetchone()
        print('PASS restored K10 Mart rows / with official % / with DW lookup states:',*dq,flush=True)
    print('PASS temporary restore DB removed; transfer DB and dump retained locally for private handoff',flush=True)
    print('Windows and Power BI execution remain PENDING TV4',flush=True)


if __name__=='__main__':main()
