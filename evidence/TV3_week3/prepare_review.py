"""Verify completed G3 outputs and prepare the TV3 review package from actual results."""
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'etl'))
from psycopg import sql
from g2_pipeline import connect,rows,write_csv


def require(value,message):
    if not value:raise ValueError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/.env.g3.local')
    parser.add_argument('--database',required=True)
    parser.add_argument('--report-dir',type=Path,default=ROOT/'reports/week3')
    parser.add_argument('--log-dir',type=Path,default=ROOT/'.qa/TV3_G3')
    parser.add_argument('--operator',default='TV3',help='who ran the full pipeline (written to evidence)')
    args=parser.parse_args()
    p=args.report_dir
    manifest=json.loads((p/'run_manifest.json').read_text(encoding='utf-8'))
    require(manifest['status']=='SUCCESS','Wait for the specific running pipeline process to complete successfully')
    for name,digest in manifest['code_sha256'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'ETL changed since full run: '+name)
    files=rows(p/'07_file_counts.csv');checks=rows(p/'07_reconciliation.csv')
    require(len(files)==12 and all(r['status']=='PASS' for r in files),'Full file coverage/counts missing')
    require(Counter(r['status'] for r in checks)=={'PASS':84,'PENDING':12},'Unexpected J06 results')
    quality=rows(p/'09_source_quality.csv');detail=rows(p/'09_quality_checks.csv')
    require(len(detail)==152 and all(r['status']=='PASS' for r in detail),'Quality/time/FK check failed')
    mismatch={('accessions','202503'):53,('accessions','202504'):43,('accessions','202505'):53,('accessions','202506'):120,
              ('separations','202503'):63,('separations','202504'):61,('separations','202505'):54,('separations','202506'):146}
    for r in quality:require(int(r['other_month'])==mismatch.get((r['family'],r['report_month']),0),'Mismatch baseline differs')
    require(sum(int(r['other_month']) for r in quality)==593,'593 cross-month events not retained')
    rerun=rows(p/'TV3_week3_rerun_results.csv')
    require(len(rerun)==15 and all(r['status']=='PASS' for r in rerun),'Rerun changed business data')
    require(json.loads((p/'rerun_before.json').read_text(encoding='utf-8'))==json.loads((p/'rerun_after.json').read_text(encoding='utf-8')),'Snapshot digests differ')
    totals={f:sum(int(r['dw']) for r in files if r['family']==f) for f in ('employment','accessions','separations')}
    require(totals=={'employment':9057997,'accessions':30782,'separations':92511},'Fact baseline differs')
    audit=rows(p/'07_load_log.csv')
    require(sum(r['status']=='SKIPPED' and r['report_month']=='202505' and r['job'] in ('J01','J02') for r in audit)==6,'May rerun audit missing')
    require(not any(r['status'] in ('RUNNING','FAIL') for r in audit),'Full run has unresolved failures')
    original=subprocess.check_output(['git','ls-tree','-r','--name-only','3b30235','reports'],cwd=ROOT,text=True).splitlines()
    for name in original:
        require(subprocess.check_output(['git','show','3b30235:'+name],cwd=ROOT)==(ROOT/name).read_bytes(),'G2 report modified: '+name)
    with connect(args) as conn:
        script='\n'.join(line for line in (ROOT/'sql/07_g3_kpi.sql').read_text(encoding='utf-8').splitlines() if not line.startswith('\\'))
        with conn.cursor() as cur:
            cur.execute(script)
            columns=[c.name for c in cur.description]
            monthly=[dict(zip(columns,r,strict=True)) for r in cur.fetchall()]
            write_csv(p/'05_kpi_monthly.csv',monthly)
            require(cur.nextset(),'Agency query missing')
            columns=[c.name for c in cur.description]
            agencies=[dict(zip(columns,r,strict=True)) for r in cur.fetchall()]
            write_csv(p/'05_kpi_agency.csv',agencies)
        april=next(r for r in monthly if r['month_key']==202504)
        require(april['k02']==-17223 and april['k08']==-16935,'April KPI semantics incorrect')
        require(monthly[0]['k02'] is None and monthly[0]['k03'] is None,'Missing prior month must stay NULL')
        sample=next(r for r in agencies if r['month_key']==202504 and r['agency_key']!=0)
        meta=conn.execute("SELECT current_user,current_setting('server_version')").fetchone()
        mart_groups=dict(workforce=conn.execute('SELECT count(*) FROM mart.workforce_monthly').fetchone()[0],
                         flows=conn.execute('SELECT count(*) FROM mart.personnel_flows_monthly').fetchone()[0])
        unknown_agency=sum(conn.execute(sql.SQL('SELECT count(*) FROM dw.{} WHERE agency_key=0').format(sql.Identifier(f))).fetchone()[0]
                           for f in ('fact_employment_snapshot','fact_accessions','fact_separations'))
    observed=rows(p/'08_dimension_observed.csv')
    evidence=ROOT/'evidence/TV3_week3'
    for name in ['00_receive_sources.txt','01_synthetic_g3.txt','02_source_regression.txt','03_model_regression.txt',
                 '04_replay_regression.txt','05_full_pipeline.txt','06_transfer_restore.txt','07_sql_assertions.txt','08_sql_kpi.txt']:
        text=(args.log_dir/name).read_text(encoding='utf-8')
        (evidence/name).write_text('\n'.join(line.rstrip() for line in text.rstrip().splitlines())+'\n',encoding='utf-8')
    branch=subprocess.check_output(['git','rev-parse','--abbrev-ref','HEAD'],cwd=ROOT,text=True).strip()
    environment='Python '+sys.version.split()[0]+'; PostgreSQL '+meta[1]+'; '+platform.system()+' '+platform.machine()+'; operator '+args.operator+'\n'
    environment+='Base G2 commit: 3b30235; branch '+branch+'; full-run code '+manifest['code_version']+'\n'
    environment+='COMMAND: python -u etl/g3_pipeline.py --config configs/.env.g3.local --database '+str(manifest['database'])+' --raw-dir <12 Parquet TV2> --report-dir reports/week3 --verify-rerun --quality-check\n'
    environment+='Run window (UTC): '+manifest['started_at']+' -> '+manifest['finished_at']+'\n'
    environment+=f'PASS code hashes match completed full run; {len(original)} G2 reports byte-identical; 593 mismatches preserved\n'
    environment+='PASS April K02=-17223, K08=-16935; missing March prior-month K02/K03 remain NULL\n'
    environment+='Actual agency example (same SQL filters for TV4): '+json.dumps(sample,default=str,ensure_ascii=False)+'\n'
    environment+='NOT_TESTED real republish replacement; PENDING Windows/SQL-DAX and independent TV5 QA\n'
    (evidence/'00_environment_and_commands.txt').write_text(environment,encoding='utf-8')
    open_items=[
      dict(id='G3-D01',owner='TV1',status='OPEN',item='G2 #43 superseded by TV1 integration branch tv1/g3-integration (TV3 commits kept); close #43 after merge'),
      dict(id='G3-D02',owner='TV4',status='PENDING',item='Approve bus matrix, Dimension catalog, grain and Unknown/time roles'),
      dict(id='G3-D03',owner='TV4/TV3',status='PENDING_DESIGN',item='Occupation/location/grade/category Mart extensions require agreed grain; current Marts month/agency'),
      dict(id='G3-D04',owner='TV4',status='NOT_RUN_WINDOWS',item='Receive private full-period dump, refresh PBIX, compare total and actual agency filter with SQL'),
      dict(id='G3-D05',owner='TV5',status='PENDING_INDEPENDENT_QA',item='Replay full 12 files and May rerun; sign actual SQL-DAX/QA results'),
      dict(id='G3-D06',owner='TV2/TV3',status='NOT_TESTED',item='Successful replacement with real republish source unavailable; mismatch rejection and skip tested'),
      dict(id='G3-D07',owner='TV2/TV4',status='PARTIAL_REFERENCE',item='Agency labels PARTIAL or REVIEWED_TV2 (TV2 EHRI label review applied, agency Unknown = 0); HOLD_ORG_SCOPE subelements stay out; official verification pending')]
    dependencies=[('G2/G3','Trước merge/nghiệm thu G3','OPEN_DEPENDENCY'),
                  ('L3-11 / L4-07..09','Trước duyệt Dimension/grain và nghiệm thu G3','BLOCKED'),
                  ('L3-12 / L4-07..09','Trước mở rộng Mart ngoài tháng/cơ quan','BLOCKED'),
                  ('H07 / T09','Trước xác nhận TV4 nhận Mart và nghiệm thu G3','NOT_RUN_WINDOWS'),
                  ('L3-13 / L5-07..09','Trước nghiệm thu G3','BLOCKED_ACCEPTANCE'),
                  ('T08','Trước bật replacement; cần republish thật','NOT_TESTED'),
                  ('L3-11 / T03','Trước kết luận theo agency/category','PARTIAL_REFERENCE')]
    for item,(task,needed_by,status) in zip(open_items,dependencies,strict=True):
        item.update(task_id=task,needed_by=needed_by,status=status)
    write_csv(ROOT/'reports/TV3_week3_open_items.csv',open_items)
    lines=['# Bàn giao tuần 3 của TV3','',
           '**REVIEW phần kỹ thuật TV3; G3 chưa được nghiệm thu.** Đã nạp thật đủ 12 Parquet tháng 03–06/2025, build ba Fact và hai Mart theo grain tháng/cơ quan. Mô hình vẫn PROPOSED chờ TV4; Windows/PBIX/SQL–DAX và QA độc lập chờ TV4/TV5.',
           '', 'Nhánh `tv3/g3-full-pipeline` kế thừa G2 commit `3b30235`, PR G2 #43 chưa merge tại lúc tạo nhánh. [Runbook G3](../docs/TV3_week3_runbook.md), [quyết định mô hình](../docs/TV3_g3_model_review.md) và [sơ đồ](../diagrams/10_g3_full_pipeline.svg) ghi scope/dependency. Kế hoạch nguồn: Ke_hoach_Tuan_3_TV3_Nhom13.docx, phiên bản 1.0 ngày 23/11/2026.',
           '', '| Task | Trạng thái | Sản phẩm thực chạy |', '| --- | --- | --- |',
           '| L3-10 | REVIEW | 12 file Source=Staging=ODS; [counts](week3/07_file_counts.csv), [audit](week3/07_load_log.csv), [before–after](week3/07_before_after.csv) |',
           '| L3-11 | REVIEW thực thi; model PROPOSED | 3 Fact, khóa/FK/time roles, [catalog quan sát](week3/08_dimension_observed.csv), [quality checks](week3/09_quality_checks.csv) |',
           '| L3-12 | REVIEW tháng/cơ quan | Workforce Mart '+str(mart_groups['workforce'])+' nhóm và flows Mart '+str(mart_groups['flows'])+' nhóm đủ bốn kỳ; [KPI SQL](week3/05_kpi_monthly.csv); category/các chiều bổ sung chờ TV4 |',
           '| L3-13 | REVIEW tự kiểm | [J06](week3/07_reconciliation.csv), [rerun May](week3/TV3_week3_rerun_results.csv), [failure tests](../evidence/TV3_week3/02_source_regression.txt); TV5 độc lập chờ xác nhận |',
           '', '| Tháng | Employment | Accessions | Separations | K02 | K08 |', '| --- | ---: | ---: | ---: | ---: | ---: |']
    for r in monthly:
        lines.append('| '+' | '.join(str(r[k]) if r[k] is not None else 'NULL' for k in ('month_key','k01','k06','k07','k02','k08'))+' |')
    lines.extend(['',f'Tổng dòng Fact: Employment {totals["employment"]:,}; Accessions {totals["accessions"]:,}; Separations {totals["separations"]:,}. Tổng {sum(totals.values()):,} bản ghi qua các kỳ, không phải số người duy nhất.',
       '', '**Kiểm chứng:** 84 J06 PASS + 12 DAX PENDING; 152 kiểm raw/ODS, ordinal, time role và FK PASS. Giữ 593 event khác kỳ (269 Accessions, 324 Separations), riêng May 107. PK/UNIQUE/FK đều validated; lookup không nhân/mất dòng. [Chất lượng theo file và Unknown](week3/09_source_quality.csv) ghi số thực đo.',
       '', '**Rerun May thật:** ba file được J00 kiểm lại, sáu J01/J02 SKIPPED, J03–J05 rebuild May rồi J06 đủ bốn kỳ. Cả 15 bảng có cùng count/digest trước–sau, gồm stable Dim keys và Fact/Mart mọi tháng; source identity toàn baseline giữ nguyên. Audit được thêm run mới. Mã/cột/thứ tự digest ghi trong runbook. Không gọi nhánh skip là đã thử replacement.',
       '', 'Dimension thực đo: '+', '.join(r['table']+' = '+r['actual_rows']+' dòng' for r in observed)+'. Unknown key=0; nhãn dẫn xuất PARTIAL, riêng 28 khóa Agency–tháng TV2 đã duyệt nhãn EHRI là REVIEWED_TV2; Agency Unknown = '+str(unknown_agency)+' dòng trên 12 file. Các tháng hiệu lực ngoài bốn kỳ vẫn có Dimension; không cắt event.',
       '', '**Bàn giao TV4:** [workforce_g3.dump](../handoff/TV3_G3/workforce_g3.dump), [SHA-256](../handoff/TV3_G3/workforce_g3.dump.sha256) và [lệnh restore](../handoff/TV3_G3/README.md) đã có trong repo; ba Dimension và hai Mart; [bằng chứng chuyển/restore](../evidence/TV3_week3/06_transfer_restore.txt) ghi SHA-256, 9/493/53/486/340 dòng và KPI cả bốn kỳ. Đã so toàn bộ nội dung bảng sau restore trên PostgreSQL 18 cùng máy; Windows và Power BI chưa chạy. Raw/config và dump cục bộ không commit; ngoại lệ đúng bản aggregate G3 đã kiểm trong handoff/TV3_G3/.',
       '', '**Kiểm thử lỗi:** fixture QA kiểm file thiếu, checksum/version/hash thay dưới cùng tên, schema không hỗ trợ, lỗi COPY giữa transaction, rollback và audit FAIL; model chặn count != 1 và giữ Mart cũ. Test mới phát hiện thay đổi trường nghiệp vụ dù tổng không đổi. Không sửa raw thật; replacement thành công với file republish thật NOT_TESTED.',
       '', f'Giữ nguyên byte của {len(original)} báo cáo G2. CSV G3 ở reports/week3; QA riêng dùng --report-dir .qa/TV5_G3/<run>. [Run manifest](week3/run_manifest.json) ghi code/inventory SHA-256 và thời gian; lượt full chạy trên working tree có hash mã chính xác để đối chiếu commit sau.',
       '', '**Nhận xét:** phần TV3 có đủ dữ liệu, code, log, SQL và lệnh replay để gửi review. Chưa có căn cứ ghi G3 DONE/PASS: TV4 còn duyệt catalog/grain/nhận Mart và TV5 còn kết luận độc lập. Chi tiết và owner trong [danh sách còn mở](TV3_week3_open_items.csv). Các ID G3-Dxx là mục theo dõi nội bộ, không phải số issue GitHub.',
       '', 'Tracker L3-10…13 và H07 chỉ chuyển REVIEW; 100% là tự báo phần kỹ thuật đã nộp, kết quả review vẫn CHUA_REVIEW và nghiệm thu vẫn 0. TV1 điền lịch/chốt G3. [Hồ sơ bằng chứng](../evidence/TV3_week3/) có regression, full run, SQL và restore; người nhận tự ghi actual và phạm vi đã chạy, không chép kết luận TV3 thành QA độc lập.'])
    lines.extend(['', '[Nhận xét lại theo từng mục kế hoạch](../evidence/TV3_week3/10_final_review.md) đối chiếu T01–T09, L3-10…13, H07 và các giới hạn còn mở trước khi đẩy repo.'])
    (ROOT/'reports/TV3_week3_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(environment,flush=True)


if __name__=='__main__':main()
