import csv, json, math, collections, zipfile
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path('/mnt/data/TV2_Phan_tich_Profiling')
OUT=BASE

def read(name):
    with (BASE/name).open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,fields,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def i(x): return int(float(x or 0))
def fmt(n):return f'{n:,}'.replace(',','.')
def percent(n,d):return round(100*n/d,4) if d else None

def fpercent(n,d):return f'{percent(n,d):,.2f}%'.replace(',','.')
cols=read('column_profile.csv');counts=read('count_quality.csv');months=read('month_consistency.csv');files=read('file_summary.csv');cats=read('category_top10.csv')

total=sum(i(r['rows']) for r in files)
datasets=['employment','accessions','separations']
periods=['202503','202504','202505','202506']
counts_by={(r['dataset'],r['period']):i(r['rows']) for r in files}
num_by_dataset={x:sum(i(r['rows']) for r in files if r['dataset']==x) for x in datasets}
col_agg=collections.defaultdict(lambda:dict(rows=0,null=0,empty=0,redacted=0,files=0))
for r in cols:
    st=col_agg[(r['dataset'],r['column'])]
    st['rows']+=i(r['total_rows']);st['null']+=i(r['null_count']);st['empty']+=i(r['empty_string_count']);st['redacted']+=i(r['redacted_count']);st['files']+=1
col_agg_list=[]
for (ds,cn),a in sorted(col_agg.items()):
    col_agg_list.append({'dataset':ds,'column':cn,'rows':a['rows'],'null_count':a['null'],'null_pct':percent(a['null'],a['rows']),'empty_count':a['empty'],'empty_pct':percent(a['empty'],a['rows']),'redacted_count':a['redacted'],'redacted_pct':percent(a['redacted'],a['rows']),'unavailable_union_count':a['null']+a['empty']+a['redacted'],'unavailable_union_pct':percent(a['null']+a['empty']+a['redacted'],a['rows'])})
write('column_quality_aggregated.csv',list(col_agg_list[0]),col_agg_list)
# record count evolution
trend=[]
for ds in datasets:
    prev=None
    for period in periods:
        n=counts_by[(ds,period)]
        trend.append({'dataset':ds,'period':period,'record_count':n,'delta_from_previous':n-prev if prev else '', 'change_pct':percent(n-prev,prev) if prev else ''})
        prev=n
write('monthly_trends.csv',list(trend[0]),trend)
# monthly mismatch details
month_summary=[]
for r in months:
    n=i(r['total_rows']);bad=i(r['mismatch_month']);
    month_summary.append({**r,'mismatch_pct':percent(bad,n)})
write('month_check_extended.csv',list(month_summary[0]),month_summary)
# count check
count_agg=[]
for ds in datasets:
 rs=[r for r in counts if r['dataset']==ds]
 metrics=['total_rows','null_count','empty_count','redacted_count','numeric_count','other_invalid_count','negative_numeric_count','zero_numeric_count']
 agg={k:sum(i(r[k]) for r in rs) for k in metrics}
 agg.update({'dataset':ds,'min_numeric':min(float(r['min_numeric']) for r in rs),'max_numeric':max(float(r['max_numeric']) for r in rs),'sum_numeric_nonredacted':sum(float(r['sum_numeric_nonredacted']) for r in rs)})
 count_agg.append(agg)
write('count_check_by_dataset.csv',list(count_agg[0]),count_agg)
# top agency shares on four periods
agency=[]
for ds in datasets:
 for period in periods:
  l=[r for r in cats if r['dataset']==ds and r['period']==period and r['column']=='agency_code']
  l.sort(key=lambda r:i(r['rank']))
  if l:
    n=counts_by[(ds,period)]
    agency.append({'dataset':ds,'period':period,'top1_agency_code':l[0]['value'],'top1_record_count':i(l[0]['record_count']),'top1_pct':percent(i(l[0]['record_count']),n),'top10_record_count':sum(i(a['record_count']) for a in l),'top10_pct':percent(sum(i(a['record_count']) for a in l),n),'denominator_records':n})
write('agency_top10_share.csv',list(agency[0]),agency)

def c(ds,cn):
 q=next(x for x in col_agg_list if x['dataset']==ds and x['column']==cn)
 return q

# audit 5 CSV consistency
checks=[]
checks.append({'test':'Kiểm kê đúng 12 file, 4 tháng/3 nhóm','expected':'12 files (3 x 4)','observed':f'{len(files)} files','status':'PASS' if len(files)==12 and len({(r["dataset"],r["period"]) for r in files})==12 else 'REVIEW'})
checks.append({'test':'Tổng số bản ghi','expected':'9,181,290 (V2)','observed':str(total),'status':'PASS' if total==9181290 else 'REVIEW'})
checks.append({'test':'804 bản ghi metadata cột','expected':'(64 + 68 + 69) x 4','observed':str(len(cols)),'status':'PASS' if len(cols)==804 else 'REVIEW'})
checks.append({'test':'Mỗi cột có total_rows khớp file','expected':'804/804 phù hợp','observed':str(sum(i(r['total_rows'])==counts_by[(r['dataset'],r['period'])] for r in cols))+'/804','status':'PASS' if all(i(r['total_rows'])==counts_by[(r['dataset'],r['period'])] for r in cols) else 'REVIEW'})
checks.append({'test':'Kiểm tra phân loại count bao phủ toàn bộ dòng','expected':'12/12 phù hợp','observed':str(sum(sum(i(r[k]) for k in ['null_count','empty_count','redacted_count','numeric_count','other_invalid_count'])==i(r['total_rows']) for r in counts))+'/12','status':'PASS' if all(sum(i(r[k]) for k in ['null_count','empty_count','redacted_count','numeric_count','other_invalid_count'])==i(r['total_rows']) for r in counts) else 'REVIEW'})
checks.append({'test':'Kiểm tra tháng bao phủ toàn bộ dòng','expected':'12/12 phù hợp','observed':str(sum(sum(i(r[k]) for k in ['null_month','malformed_month','mismatch_month','matching_month'])==i(r['total_rows']) for r in months))+'/12','status':'PASS' if all(sum(i(r[k]) for k in ['null_month','malformed_month','mismatch_month','matching_month'])==i(r['total_rows']) for r in months) else 'REVIEW'})
checks.append({'test':'count_numeric_sum của top10 bằng record_count','expected':'652/652 phù hợp','observed':str(sum(float(r['record_count'])==float(r['count_numeric_sum']) for r in cats))+'/652','status':'PASS' if all(float(r['record_count'])==float(r['count_numeric_sum']) for r in cats) else 'REVIEW'})
write('validation_checks.csv',list(checks[0]),checks)

issues=[
('DQ01','High','Employment','annualized_adjusted_basic_pay','REDACTED',c('employment','annualized_adjusted_basic_pay')['redacted_count'],c('employment','annualized_adjusted_basic_pay')['redacted_pct'],'Không thể coi giá trị lương bị che là 0; mọi thống kê lương chỉ phản ánh phần có thể quan sát.','Giữ cờ is_redacted, lưu giá trị số NULL khi REDACTED; chỉ tính trên giá trị hợp lệ, công bố coverage.','TV2 + TV3','Chờ xác minh codebook/ETL'),
('DQ02','High','Employment','duty_station_state','REDACTED',c('employment','duty_station_state')['redacted_count'],c('employment','duty_station_state')['redacted_pct'],'Khoảng 46% số bản ghi trong trường địa lý không có state quan sát được; cơ cấu địa lý có nguy cơ thiếu đại diện.','Giữ REDACTED/Unknown rõ trong Dimension và dashboard; không phân bổ lại vào state thật.','TV2 + TV3 + TV4','Chờ thiết kế'),
('DQ03','High','Separations','occupational_category_code','EMPTY+NULL',c('separations','occupational_category_code')['empty_count']+c('separations','occupational_category_code')['null_count'],round(c('separations','occupational_category_code')['empty_pct']+c('separations','occupational_category_code')['null_pct'],4),'Mã occupational category thiếu ở nhiều bản ghi; nguy cơ mất sự kiện khi join Dimension bằng INNER JOIN.','Phân biệt NULL và chuỗi rỗng; mapping Unknown, không làm mất dòng; đối chiếu column nhãn và codebook.','TV2 + TV3','Chờ kiểm codebook'),
('DQ04','High','Separations','occupational_category','NULL 03/2025',10914,round(100*10914/22061,4),'Tỷ lệ NULL rất cao ở kỳ 03, giảm mạnh ở kỳ sau; xu hướng theo occupation category có thể méo.','Kiểm schema/codebook theo kỳ, báo coverage từng tháng, giữ Unknown.','TV2 + TV4','Chờ xác minh nguyên nhân'),
('DQ05','Medium','Separations','pathways_group','NULL',c('separations','pathways_group')['null_count'],100.0,'Cột trống hoàn toàn trong 4 file Separations; không thể dùng làm Dimension từ nguồn này.','Không sử dụng trong Separations Mart cho tới khi có định nghĩa/nguồn thay thế; không tự gán giá trị.','TV2 + TV4','Theo dõi'),
('DQ06','Medium','Accessions','pathways_group','NULL',c('accessions','pathways_group')['null_count'],c('accessions','pathways_group')['null_pct'],'Chỉ số bản ghi có giá trị rất ít; phân tích phân bố pathways thiếu đại diện.','Gắn cờ missing và không triển khai KPI coverage toàn tập nếu chưa rõ phạm vi áp dụng.','TV2 + TV4','Chờ kiểm codebook'),
('DQ07','Medium','Separations','appointment_not_to_exceed_date','NULL',c('separations','appointment_not_to_exceed_date')['null_count'],c('separations','appointment_not_to_exceed_date')['null_pct'],'Trường ngày hạn bổ nhiệm NULL nhiều, có thể do không áp dụng; không thể tự kết luận lỗi.','Giữ NULL; kiểm điều kiện nghiệp vụ khi thuộc nhóm appointment tương ứng.','TV2 + TV3','Chờ xác minh'),
('DQ08','High','Accessions+Separations','personnel_action_effective_date_yyyymm','MISMATCH file month',sum(i(r['mismatch_month']) for r in months if r['dataset']!='employment'),round(100*sum(i(r['mismatch_month']) for r in months if r['dataset']!='employment')/sum(i(r['total_rows']) for r in months if r['dataset']!='employment'),4),'Khác biệt kỳ file và kỳ hiệu lực; KPI event theo kỳ có thể đổi nếu chọn thời gian khác.','Giữ cả kỳ file và effective; ghi lựa chọn rõ trong KPI và kiểm SQL/DAX. Không xóa tự động.','TV2 + TV3 + TV4','Chờ thống nhất date semantics'),
('DQ09','Low','Cả 3 nhóm','count','NUMERIC string',total,100.0,'count là chuỗi nguồn, nhưng toàn bộ giá trị quét được đều =1; không có lỗi parse.','TRY_CAST(count AS BIGINT) và kiểm 1; không dùng count tổng bốn kỳ làm số nhân viên duy nhất.','TV2 + TV3','Đã kiểm đầu vào; chờ ETL'),
('DQ10','Medium','Separations','grade','EMPTY + NULL',c('separations','grade')['empty_count']+c('separations','grade')['null_count'],round(c('separations','grade')['empty_pct']+c('separations','grade')['null_pct'],4),'Grade thiếu ở một phần event; nếu join thẳng có thể mất sự kiện.','Chuẩn hóa chuỗi rỗng thành missing có lý do, gắn Unknown trong DIM.','TV2 + TV3','Chờ codebook'),
]
issues_rows=[dict(zip(['issue_id','priority','dataset','column','issue_type','affected_occurrences','affected_pct','risk','proposed_handling','owner','verification_status'],x)) for x in issues]
write('data_quality_findings.csv',list(issues_rows[0]),issues_rows)

# charts using only source data with original fields
plt.rcParams['font.family']='DejaVu Sans'
plt.figure(figsize=(9.2,4.6))
for ds in datasets:
    y=[counts_by[(ds,t)] for t in periods]
    if ds=='employment':plt.plot(['Mar','Apr','May','Jun'],[v/1e6 for v in y],marker='o',label='Employment (million)',linewidth=2)
plt.title('Employment record volume by snapshot month (2025)')
plt.xlabel('Month');plt.ylabel('Million records');plt.grid(alpha=.25);plt.tight_layout();plt.savefig(OUT/'chart_employment_monthly.png',dpi=160);plt.close()

plt.figure(figsize=(9.2,4.6))
for ds in ['accessions','separations']:
    plt.plot(['Mar','Apr','May','Jun'],[counts_by[(ds,t)] for t in periods],marker='o',label=ds.title(),linewidth=2)
plt.title('Personnel event records by file month (2025)')
plt.xlabel('File month');plt.ylabel('Records');plt.legend();plt.grid(alpha=.25);plt.tight_layout();plt.savefig(OUT/'chart_event_monthly.png',dpi=160);plt.close()

# top 8 null and redacted grouped explicitly
for kind,field,label,fn in [
 ('null','null_pct','NULL percent','chart_top_missing.png'),
 ('redacted','redacted_pct','REDACTED percent','chart_top_redacted.png')]:
    a=sorted(col_agg_list,key=lambda r:r[field],reverse=True)[:10]
    plt.figure(figsize=(10,5.6)); labs=[r['dataset'][:3]+'/'+r['column'] for r in a]
    plt.barh(labs[::-1],[r[field] for r in a][::-1]);plt.xlim(0,105);plt.xlabel(label)
    plt.title(('Most missing' if kind=='null' else 'Most redacted')+' column by dataset (2025-03 to 06)')
    plt.tight_layout();plt.savefig(OUT/fn,dpi=150);plt.close()

# markdown report
X=lambda ds,cn:c(ds,cn)
sep_missing=X('separations','occupational_category_code')
sep_label=X('separations','occupational_category')
lines=[
'# Báo cáo Data Quality / Data Profiling — TV2, Nhóm 13',
'',
'> **Trạng thái:** Bản phân tích kết quả profiling v1 — 16/11/2026.  Nguồn số liệu: 5 CSV trong `csv.zip` do script `profile_12_parquet.py` của TV2 xuất từ 12 file Parquet (03–06/2025). Đối chiếu yêu cầu theo `De_cuong_DW_BI_Nhom13_5_5_tuan_V2.md` và `Phan_cong_DW_BI_Nhom13_5_5_tuan_V2.md`.',
'',
'## 1. Phạm vi và phương pháp',
'',
'- 3 họ dữ liệu × 4 tháng = **12 file Parquet**. Có 5 bảng CSV: `file_summary` (12 dòng), `column_profile` (804), `count_quality` (12), `month_consistency` (12), `category_top10` (652).',
'- **Đơn vị quan sát** ở báo cáo này là bản ghi trong file, không suy diễn thành cá nhân duy nhất. Tất cả tỷ lệ chất lượng được tính trên **số bản ghi của cùng dataset/field**, không lấy mẫu số 9,18 triệu cho từng trường.',
'- `NULL`, chuỗi rỗng (`empty_string`) và chuỗi `REDACTED` là **ba trạng thái riêng**. Các tổng `redacted_count` trên nhiều field không phải số người bị che và không cộng dồn để suy ra số bản ghi bị che ít nhất một field.',
'- `distinct_approx` trong CSV là **ước lượng**, không dùng để khẳng định số mã chính xác. Báo cáo không có kết quả kiểm tra giá trị ngoài codebook, hash trùng, ngoại lai lương hay phân tích bảng chéo; các phần đó chưa hoàn thành.',
'',
'## 2. Đối soát khối lượng dữ liệu',
'',
'| Tháng file | Employment | Accessions | Separations | Tổng file |',
'|---|---:|---:|---:|---:|',
]
for period in periods:
    vv=[counts_by[(ds,period)] for ds in datasets]
    lines.append(f'| {period} | {fmt(vv[0])} | {fmt(vv[1])} | {fmt(vv[2])} | {fmt(sum(vv))} |')
lines.extend([
    f'| **Tổng** | **{fmt(num_by_dataset["employment"])}** | **{fmt(num_by_dataset["accessions"])}** | **{fmt(num_by_dataset["separations"])}** | **{fmt(total)}** |',
'',
'**Kiểm tra nội bộ:** 12/12 tệp, 804/804 profile field, 12/12 phân loại `count`, 12/12 thống kê tháng và 652/652 bản ghi `category_top10` đều vượt qua các phép đối soát có thể thực hiện bằng 5 CSV. Chi tiết trong `validation_checks.csv`. Điều này **không thay thế kiểm tra độc lập trực tiếp Parquet**.',
'',
'## 3. Trường `count`: không thấy vấn đề parse trong phạm vi kiểm tra',
'',
f'- Cả **{fmt(total)}** giá trị `count` ở 12 file đều parse được sang số, min = max = **1**, không NULL, rỗng, REDACTED, âm, 0 hoặc giá trị không hợp lệ trong báo cáo `count_quality.csv`.',
'- Do `count` là chuỗi ở nguồn, ETL nên cast có kiểm tra (`TRY_CAST` và assert), không bỏ qua nguy cơ schema tương lai thay đổi.',
'- Ở dữ liệu này `sum_numeric_nonredacted = record_count` theo từng file và mọi dòng top 10. **Không vì vậy mà xác nhận 9,18 triệu nhân viên khác nhau**; Employment là snapshot nhiều kỳ.',
'',
'## 4. Phân tích missing: NULL và empty phải tách',
'',
'| Dataset / Cột | NULL | Empty | Thiếu (NULL+empty) | Tỷ lệ thiếu |',
'|---|---:|---:|---:|---:|',
])
for ds,cl in [('separations','pathways_group'),('accessions','pathways_group'),('separations','appointment_not_to_exceed_date'),('accessions','appointment_not_to_exceed_date'),('separations','occupational_category'),('separations','occupational_category_code'),('separations','grade'),('employment','core_based_statistical_area')]:
    z=X(ds,cl);n=z['null_count']+z['empty_count']
    lines.append(f'| `{ds}.{cl}` | {fmt(z["null_count"])} | {fmt(z["empty_count"])} | {fmt(n)} | {fpercent(n,z["rows"])} |')
lines.extend([
'',
f'- **`separations.occupational_category_code`** có {fmt(sep_missing["empty_count"])} chuỗi rỗng và {fmt(sep_missing["null_count"])} NULL, cộng **{fmt(sep_missing["empty_count"]+sep_missing["null_count"])} / {fmt(sep_missing["rows"])} = {fpercent(sep_missing["empty_count"]+sep_missing["null_count"],sep_missing["rows"])}** lượt không có mã. Trong khi cột nhãn `occupational_category` có {fpercent(sep_label["null_count"],sep_label["rows"])} NULL, tức mức độ thiếu khác nhau; cần kiểm codebook và quy tắc mã/nhãn, không tự lấp bằng dự đoán.',
'- Riêng `separations.occupational_category` ở **tháng 03** thiếu **10.914/22.061 = 49,47%**; tháng 04 còn **393/24.088 = 1,63%**; tháng 05 và 06 báo 0 NULL. Đây là điểm khác biệt giữa kỳ cần được kiểm tra trước khi phân tích nghề nghiệp.',
'- `pathways_group` trong Separations trống 100%; chưa có căn cứ gọi đây là dữ liệu lỗi vì có thể không áp dụng. Không đưa vào KPI/Dimension Separations cho tới khi đối chiếu định nghĩa.',
'',
'## 5. REDACTED: không được đổi thành 0',
'',
'| Dataset / Cột | REDACTED | Tỷ lệ | Ý nghĩa đối với BI |',
'|---|---:|---:|---|',
])
for ds,cl,des in [('employment','bargaining_unit','Nhóm lao động bị che nhiều; báo coverage'),('employment','annualized_adjusted_basic_pay','Không tính lương che thành 0'),('employment','duty_station_state','Không suy rộng cơ cấu theo state ra toàn bộ nhân sự'),('accessions','annualized_adjusted_basic_pay','KPI lương tiếp nhận chỉ trên phần quan sát'),('separations','annualized_adjusted_basic_pay','KPI lương nhân sự rời chỉ trên phần quan sát')]:
 z=X(ds,cl)
 lines.append(f'| `{ds}.{cl}` | {fmt(z["redacted_count"])} | {fpercent(z["redacted_count"],z["rows"])} | {des} |')
lines.extend([
'',
'- Nhiều trường địa lý có số REDACTED trùng nhau theo từng dataset; đó là **số lần bị che theo cột**, không khẳng định có cùng tập bản ghi hay cùng nguyên nhân. Khi cần phân tích mức độ bị che theo bản ghi, phải quét Parquet với phép `OR` trên các cột.',
'- Nên lưu đồng thời `*_is_redacted` hoặc trạng thái quan sát được; số liệu bị che không được tự nội suy, điền 0 hoặc chuyển thành mã địa lý thật.',
'',
'## 6. Thời gian: kết quả xác nhận 593 lượt khác kỳ',
'',
'| Nhóm | Kỳ file vs tháng hiệu lực | Tổng bản ghi | Tỷ lệ |',
'|---|---:|---:|---:|',
])
for ds in datasets:
 a=sum(i(r['mismatch_month']) for r in months if r['dataset']==ds); n=num_by_dataset[ds]
 lines.append(f'| {ds.title()} | {fmt(a)} | {fmt(n)} | {fpercent(a,n)} |')
lines.extend([
'',
f'**Tổng:** {fmt(sum(i(r["mismatch_month"]) for r in months))} lượt; cả 12 file đều có `null_month = 0` và `malformed_month = 0` theo báo cáo. Employment so sánh với `snapshot_yyyymm`, events so sánh với `personnel_action_effective_date_yyyymm`.',
'',
'**Ý nghĩa:** kỳ trong tên file và kỳ hiệu lực có thể khác nhau một cách hợp lệ. TV3 cần giữ cả `source_file_period` và `effective_month`, TV4 cần xác định rõ mỗi KPI đang dùng thời gian nào. **Không xóa 593 dòng này**, không kết luận sai dữ liệu nếu chưa xem quy tắc công bố OPM/EHRI.',
'',
'## 7. Phân bố và MoM từ số dòng (EDA sơ bộ)',
'',
'| Nhóm | 03/2025 | 04/2025 | 05/2025 | 06/2025 | So sánh 06 với 03 |',
'|---|---:|---:|---:|---:|---:|',
])
for ds in datasets:
 v=[counts_by[(ds,t)] for t in periods];change=v[-1]-v[0]
 lines.append(f'| {ds.title()} | {fmt(v[0])} | {fmt(v[1])} | {fmt(v[2])} | {fmt(v[3])} | {fmt(change)} ({fpercent(change,v[0])}) |')
lines.extend([
'',
'- Employment giảm liên tục qua các kỳ snapshot được cung cấp, nhưng các bản ghi này **chưa chứng minh biến động nhân sự gốc hay quan hệ kế toán với Accessions/Separations**.',
'- Accessions tăng về **số lượt ghi nhận theo tháng file**, Separations cao nhất vào tháng 05 rồi giảm vào tháng 06; 4 tháng **không đủ kết luận mùa vụ**, không phải cơ sở để dự báo dài hạn.',
'- Top 10 mã cơ quan theo số bản ghi Employment chiếm khoảng **82,68%–82,84%** từng tháng trong bảng `category_top10.csv`. Đây là tỷ trọng **top 10**, **chưa phải kiểm định Pareto top 20% toàn bộ cơ quan** vì bảng chỉ chứa 10 mã nổi bật mỗi tháng.',
'',
'![Số dòng Employment theo tháng](chart_employment_monthly.png)',
'',
'![Số lượt sự kiện theo tháng file](chart_event_monthly.png)',
'',
'## 8. Quy tắc đề xuất để TV3 xây dựng Staging/ETL (cần chốt với nhóm)',
'',
'| Mã | Quy tắc kỹ thuật | Test bàn giao |',
'|---|---|---|',
'| ETL-01 | Lưu `source_file`, `source_period`, `dataset`, `load_run_id`; kiểm tra 4 kỳ x 3 nhóm | row count mỗi kỳ source = staging, ghi log |',
'| ETL-02 | Với `count`, `TRY_CAST` sang INTEGER/BIGINT và phát cảnh báo khi NULL/khác 1 ở nguồn mới | 12 file hiện tại parse 100%, sum = rows |',
'| ETL-03 | Phân biệt NULL, empty, REDACTED; không đặt `REDACTED=0` | đối soát từng loại theo cột |',
'| ETL-04 | NULL/empty ở category key map sang Unknown khi cần dùng DIM; **không INNER JOIN làm mất sự kiện** | tổng Fact không giảm vì missing code |',
'| ETL-05 | Lưu `snapshot_month` cho Employment và đồng thời `source_file_period`, `effective_month` cho events | 593 event mismatch được giữ lại, không loại bỏ |',
'| ETL-06 | Không deduplicate sự kiện chỉ vì cùng thuộc tính nếu chưa xác nhận grain/khóa gốc | ghi lại quy tắc grain và đối soát số dòng |',
'| ETL-07 | Mọi nhãn mã Agency/Occupation/Grade/Separation phải tra codebook, có cờ `verified` | audit độc lập TV1/TV5 theo V2 |',
'',
'**File phân công:** `data_quality_findings.csv` chứa 10 phát hiện, ưu tiên, người phối hợp và trạng thái xác minh. Các quy tắc trên là **đề xuất từ profiling**, chưa phải quy tắc đã áp dụng vào hệ thống DW.',
'',
'## 9. Những việc chưa thể kết luận từ 5 CSV',
'',
'- **Không có kết quả kiểm tra trùng lặp toàn dòng:** script chỉ sinh `potential_duplicates_hash.csv` khi chạy thêm `--check-duplicates`; kể cả thấy hash trùng vẫn phải phân biệt sự kiện hợp lệ.',
'- **Không có bảng tra codebook/meaning đã được kiểm chứng**; chưa thể khẳng định mã có hợp lệ hoặc mô tả đầy đủ ý nghĩa của các giá trị như `AD`, `SC`, `0301`.',
'- **Không có dữ liệu mẫu hàng gốc** để gắn vào các nhánh Taxonomy theo yêu cầu bổ sung của thầy ở V2. `category_top10.csv` chỉ là thống kê nhóm, **không được gọi là dòng dữ liệu nguồn**.',
'- **Không có tất cả danh mục Agency** và toàn bộ bảng chéo Agency × Occupation/Grade, vì `category_top10.csv` chỉ chứa 10 giá trị nổi bật theo cột. Chưa đủ tính Cramér’s V, Pareto top 20% chính xác hoặc 2 phân tích liên hệ theo C05.',
'- **Không có min/max/percentile của trường lương/tuổi** ngoài `count`; chưa thể kết luận outlier, phân bố lương hoặc bias đại diện ở trường bị che.',
'- **Chưa đối soát SQL/ETL thực tế và chưa có Before–After bản ghi thật.**',
'',
'## 10. Việc tiếp theo theo V2',
'',
'1. **TV2 + TV1/TV5:** kiểm codebook, lập Dictionary `field/raw_type/semantic meaning/example/valid values/source/ETL target/verified_by` và Taxonomy có ví dụ **hàng gốc**.',
'2. **TV2 + TV3:** chốt ý nghĩa `count`, grain, cách phân biệt `file_period`/`effective_month`, nhóm dữ liệu che; cung cấp mapping và test.',
'3. **TV2:** dùng Parquet trực tiếp để tạo EDA đầy đủ (phân bố, Pareto tất cả cơ quan, bảng chéo hai biến phân loại với Cramér’s V hoặc effect size phù hợp, MoM kèm giới hạn), ERD lớp nguồn/ODS và source-to-target mapping.',
'4. **TV2 + TV3/TV5:** chạy kiểm thử Staging và đối soát không mất hoặc nhân dòng.',
'',
'## 11. Danh mục bằng chứng và trạng thái',
'',
'- **Đã làm:** Chạy 12/12 Parquet → 5 CSV profiling; đối soát tổng và phân loại `count`, thời gian; 10 vấn đề dữ liệu có đề xuất xử lý trong `data_quality_findings.csv`.',
'- **Đang thiếu trước khi tuyên bố hoàn thành C03/C05:** provenance/codebook được xác minh, Data Dictionary audit hai người, Taxonomy có raw row mẫu, các thành phần EDA chuyên sâu, notebook/SQL kiểm chứng và sơ đồ.',
'',
'**Lưu ý phương pháp:** Đây là báo cáo phân tích **đúng năm kết quả CSV đã nhận**, không tự coi là EDA toàn phần hay minh chứng tất cả yêu cầu V2. Người review cần kiểm tra lại kết quả trên máy TV2/Parquet gốc và ký nhận.'
])
(OUT/'data_quality.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
summary={'total_records':total,'by_dataset':num_by_dataset,'mismatch_total':sum(i(r['mismatch_month']) for r in months),'mismatch_by_dataset':{ds:sum(i(r['mismatch_month']) for r in months if r['dataset']==ds) for ds in datasets},'column_groups':len(col_agg_list),'source_files':len(files),'profile_columns':len(cols),'issues':len(issues),'files_csv':[p.name for p in OUT.glob('*.csv')],'checks':checks}
(OUT/'metrics_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2)[:3500])
