# TV5 replay G2 trên Windows · chờ QA độc lập

Chạy từ thư mục gốc repo trên nhánh `tv3/g2-pipeline`. TV5 dùng PostgreSQL 18, Python 3.12 và **database QA mới riêng**, không dùng database bàn giao tổng hợp của TV4 hoặc database làm việc của TV3. [Gói TV4](README.md) dùng dump gồm năm bảng; replay dưới đây cần ba Parquet thật để tạo toàn bộ Staging/ODS/DW/Mart/audit.

Các kết quả TV3 đã lưu là đầu vào review. TV5 ghi môi trường, actual và kết luận riêng; bằng chứng Windows, SQL–DAX và kết luận QA vẫn chờ TV4/TV5 thực hiện.

## 1. Chuẩn bị Python, PostgreSQL và thư mục QA

Cài Python 3.12 có Python Launcher (`py`) và PostgreSQL 18. Thêm thư mục `bin` PostgreSQL vào PATH PowerShell, rồi kiểm:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
py -3.12 --version
if ($LASTEXITCODE -ne 0) { throw 'Cần Python 3.12.' }
psql --version
if ($LASTEXITCODE -ne 0) { throw 'Cần PostgreSQL CLI trong PATH.' }
py -3.12 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Tạo venv thất bại.' }
$Python = (Resolve-Path '.\.venv\Scripts\python.exe').Path
& $Python -m pip install -r .\requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Cài requirements thất bại.' }
& $Python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency check thất bại.' }

$QaRoot = Join-Path (Get-Location) ('.qa\TV5_G2\' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$Reports = Join-Path $QaRoot 'reports'
New-Item -ItemType Directory -Force -Path $Reports | Out-Null
git rev-parse HEAD | Set-Content -Encoding UTF8 (Join-Path $QaRoot 'commit.txt')
& $Python --version 2>&1 | Set-Content -Encoding UTF8 (Join-Path $QaRoot 'python-version.txt')
psql --version | Set-Content -Encoding UTF8 (Join-Path $QaRoot 'postgres-version.txt')
```

Gọi trực tiếp Python trong venv nên không cần đổi execution policy để activate. `.qa/`, venv, cấu hình và raw được Git bỏ qua. Giữ kết quả riêng trong `$QaRoot`; không ghi đè `reports/07_*.csv` hoặc bằng chứng TV3 đã bàn giao.

```powershell
$Config = '.\configs\.env.qa.local'
if (-not (Test-Path $Config)) { Copy-Item '.\configs\.env.example' $Config }
Start-Process notepad.exe -ArgumentList $Config -Wait
```

Điền cấu hình cục bộ, thay `TV5_ROLE` và mật khẩu theo server của TV5:

```dotenv
PGHOST=127.0.0.1
PGPORT=5432
PGDATABASE=workforce_dw_tv5_qa
PGUSER=TV5_ROLE
PGPASSWORD=
RAW_DATA_DIR=./data/raw
```

`PGPASSWORD` để trống chỉ khi server cho phép kết nối không cần mật khẩu; nếu cần, điền mật khẩu trong file cục bộ này. Không chép cấu hình/mật khẩu vào evidence. `psql`/`createdb` không tự đọc file dotenv; dùng host/port/user giống cấu hình và nhập mật khẩu khi được hỏi (hoặc dùng pgpass cục bộ).

```powershell
$PgRole = 'TV5_ROLE'
$Database = 'workforce_dw_tv5_qa'
createdb -h 127.0.0.1 -p 5432 -U $PgRole $Database
if ($LASTEXITCODE -ne 0) { throw 'Chọn database QA mới hoặc kiểm quyền; không chạy tiếp trên DB chưa xác minh.' }
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U $PgRole -d $Database -c 'SELECT current_database(), current_user, version();'
if ($LASTEXITCODE -ne 0) { throw 'Kiểm kết nối QA thất bại.' }
```

Các regression bên dưới kết nối database bảo trì `postgres`, tự `CREATE DATABASE tv3_g2_check_<id>` rồi `DROP DATABASE ... WITH (FORCE)` khi kết thúc. Role trong `$Config` cần quyền `CREATEDB`, quyền kết nối `postgres` và quyền xóa database do mình tạo. Nhờ quản trị viên cấp quyền hoặc dùng role QA phù hợp trước khi chạy; chỉ tạo sẵn database `$Database` chưa đủ cho các regression này.

Pipeline và trình đối soát trực tiếp chọn `--database`/`--raw-dir` theo thứ tự **tham số CLI → `PGDATABASE`/`RAW_DATA_DIR` trong file `--config` → mặc định `workforce_dw`/`data/raw`**. Ví dụ dưới truyền rõ database/raw để reviewer nhìn thấy đích chạy. Pipeline `--report-dir` mặc định vẫn là `reports/` trong repo; vì vậy luôn truyền `$Reports` khi replay.

## 2. Nhận đúng ba Parquet tháng 04 từ TV2

Nhận file qua kênh chia sẻ nguồn của TV2, đối chiếu [inventory](../../docs/03_source_inventory.csv) và [SHA manifest](../../data/manifest/sha256.txt) cùng commit đang review. Inventory có 12 file nhưng lượt MVP chỉ cần đúng ba file dưới. Nếu dùng mirror, URL cụ thể nằm ở cột `source_url` của inventory; chỉ dùng sau khi checksum khớp baseline TV2.

| Family | Filename | Số dòng | Byte | SHA-256 |
| --- | --- | ---: | ---: | --- |
| employment | `employment_202504_v4.parquet` | 2.271.969 | 74.442.213 | `d0bfcf7158fbd552469ec2f8df84cb0ec12c51578e6c571aa21d7c32fe203e72` |
| accessions | `accessions_202504_v5.parquet` | 7.153 | 283.855 | `933b33c65b2553867efce924cfe87696ba5152c25d0861b5f1cb085481da72fa` |
| separations | `separations_202504_v5.parquet` | 24.088 | 1.007.803 | `b34e3a68ddd28c912f8bcbd961b3da914d6ca7e94ed20523b364f929bf9c0c5c` |

Đặt `$Raw` là thư mục cha chứa file; thay bằng đường dẫn nguồn riêng nếu không dùng `data/raw`. Loader/checker nhận cả hai cấu trúc:

```text
data/raw/employment_202504_v4.parquet
data/raw/accessions_202504_v5.parquet
data/raw/separations_202504_v5.parquet
```

hoặc:

```text
data/raw/employment/employment_202504_v4.parquet
data/raw/accessions/accessions_202504_v5.parquet
data/raw/separations/separations_202504_v5.parquet
```

Tránh giữ hai bản khác nhau cùng filename ở cả hai vị trí: công cụ ưu tiên file phẳng. Kiểm đủ family, manifest, kích thước và SHA-256 **trước khi nạp**:

```powershell
$Raw = (Resolve-Path '.\data\raw').Path
$Sources = @(Import-Csv '.\docs\03_source_inventory.csv' | Where-Object { $_.report_month -eq '202504' })
if ($Sources.Count -ne 3 -or (($Sources.family | Sort-Object) -join ',') -ne 'accessions,employment,separations') {
    throw 'Inventory phải có đúng một file của mỗi family tháng 202504.'
}
$Manifest = @{}
Get-Content '.\data\manifest\sha256.txt' | Where-Object { $_.Trim() } | ForEach-Object {
    $Parts = $_.Trim() -split '\s+', 2
    $Manifest[$Parts[1]] = $Parts[0]
}
$HashResults = foreach ($Item in $Sources) {
    if ($Manifest[$Item.filename] -ne $Item.sha256) { throw "Inventory/manifest khác nhau: $($Item.filename)" }
    $Path = Join-Path $Raw $Item.filename
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $Path = Join-Path (Join-Path $Raw $Item.family) $Item.filename
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Thiếu nguồn: $($Item.filename)" }
    $Hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    $Bytes = (Get-Item -LiteralPath $Path).Length
    if ($Hash -ne $Item.sha256 -or $Bytes -ne [long]$Item.size_bytes) { throw "Nguồn không khớp: $($Item.filename)" }
    [pscustomobject]@{ family=$Item.family; filename=$Item.filename; expected_sha256=$Item.sha256; actual_sha256=$Hash; expected_bytes=$Item.size_bytes; actual_bytes=$Bytes; status='PASS' }
}
$HashResults | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $QaRoot 'source-sha256.csv')
$HashResults | Format-Table family,filename,status
```

Pipeline J00 tiếp tục kiểm số dòng, số cột, schema hash và kiểu text. Sai metadata/hash phải dừng; không sửa inventory để cho file sai vượt qua.

## 3. Chạy hai bộ regression và kiểm replay bổ sung

Các test này dùng fixture tổng hợp, không thay thế lượt chạy Parquet thật.

```powershell
& $Python .\tests\g2_source_checks.py --config $Config 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'source-regression.txt')
if ($LASTEXITCODE -ne 0) { throw 'Source regression FAIL; xem log QA.' }
& $Python .\tests\g2_model_checks.py --config $Config 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'model-regression.txt')
if ($LASTEXITCODE -ne 0) { throw 'Model regression FAIL; xem log QA.' }
& $Python .\tests\g2_replay_checks.py --config $Config 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'replay-regression.txt')
if ($LASTEXITCODE -ne 0) { throw 'Replay regression FAIL; xem log QA.' }
```

Expected: source rerun SKIPPED không nhân dòng; file thiếu/hash sai/version sai/COPY lỗi tạo audit FAIL và rollback dữ liệu nguồn lỗi. Model giữ Unknown khi lookup mơ hồ, giữ kỳ đã có, rerun không nhân Fact, count lỗi không publish và giữ Mart trước đó. Bộ replay bổ sung kiểm J06 với không/một/hai/đủ ba family, nguồn inactive/chưa LOADED, sai số dòng, audit FAIL, ưu tiên cấu hình/CLI, thư mục báo cáo riêng và preflight của trình đối soát. Các test xóa database tạm sau khi chạy.

## 4. Pipeline end-to-end và kiểm trực tiếp Parquet–ODS

```powershell
& $Python .\etl\g2_pipeline.py --config $Config --database $Database --month 202504 --raw-dir $Raw --report-dir $Reports --job all 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'pipeline-all.txt')
if ($LASTEXITCODE -ne 0) { throw 'Pipeline FAIL; xem audit và CSV QA.' }
& $Python .\evidence\TV3_week2\reconcile_sources.py --config $Config --database $Database --month 202504 --raw-dir $Raw 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'source-direct.txt')
if ($LASTEXITCODE -ne 0) { throw 'Parquet–ODS FAIL.' }
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U $PgRole -d $Database -v month=202504 -f .\sql\05_g2_kpi.sql 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'sql-kpi.txt')
if ($LASTEXITCODE -ne 0) { throw 'SQL KPI FAIL.' }
```

Expected: J00–J06 thành công, đủ ba family active/LOADED; nguồn = Staging = ODS = Fact theo từng family; 0 khác biệt lineage. J06 xuất **21 PASS** (3 kiểm coverage + 18 kiểm SQL) và **3 PENDING** dành DAX. K01/K06/K07 = **2.271.969 / 7.153 / 24.088**. Trình đối soát trực tiếp phải in PASS riêng cho employment/accessions/separations và đối chiếu count, pay NULL/rỗng/REDACTED, mã nghề có 0 đầu, khác kỳ; 43 Accessions và 61 Separations khác kỳ vẫn được giữ. Tháng sai định dạng hoặc tháng thiếu đủ ba family phải kết thúc lỗi, không báo kiểm thành công.

Kiểm hai tháng không hợp lệ/không có nguồn; ở đây mã thoát khác 0 mới là kết quả kỳ vọng:

```powershell
& $Python .\evidence\TV3_week2\reconcile_sources.py --config $Config --database $Database --month 202513 --raw-dir $Raw 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'invalid-month.txt')
if ($LASTEXITCODE -eq 0) { throw 'Tháng 202513 đã vượt kiểm sai.' }
& $Python .\evidence\TV3_week2\reconcile_sources.py --config $Config --database $Database --month 209901 --raw-dir $Raw 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'absent-month.txt')
if ($LASTEXITCODE -eq 0) { throw 'Tháng không có nguồn đã vượt kiểm sai.' }
```

Chạy lại cùng baseline để kiểm tính lặp lại:

```powershell
& $Python .\etl\g2_pipeline.py --config $Config --database $Database --month 202504 --raw-dir $Raw --report-dir $Reports --job all 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'pipeline-rerun.txt')
if ($LASTEXITCODE -ne 0) { throw 'Pipeline rerun FAIL.' }
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 5432 -U $PgRole -d $Database -c "SELECT job,family,status,count(*) FROM audit.load_run GROUP BY job,family,status ORDER BY job,family,status;" 2>&1 | Tee-Object -FilePath (Join-Path $QaRoot 'audit-summary.txt')
if ($LASTEXITCODE -ne 0) { throw 'Đọc audit thất bại.' }
```

Expected: J01/J02 của ba file SKIPPED ở lượt sau, tổng Mart không đổi. J06 chỉ PASS khi **đúng một** file active/LOADED mỗi family và các số đối soát đúng; thiếu một/hai family hoặc không có dữ liệu phải FAIL và lưu audit J06 FAIL. Ba CSV mới ở `$Reports`: `07_load_log.csv`, `07_before_after.csv`, `07_reconciliation.csv`. `powerbi_dax` vẫn PENDING cho đến khi TV4/TV5 kiểm thật.

## 5. Checklist expected/actual và phản hồi

Tạo bảng riêng để TV5 điền actual, status và đường dẫn evidence. Không đánh PASS từ expected hoặc chép kết luận TV3 thành kết luận QA.

```powershell
@'
check,expected,actual,status,evidence
commit_received,commit.txt recorded,,PENDING,
source_sha256,3 families SHA256/bytes match,,PENDING,source-sha256.csv
source_regression,all checks PASS and temporary DB removed,,PENDING,source-regression.txt
model_regression,all checks PASS and temporary DB removed,,PENDING,model-regression.txt
replay_regression,all checks PASS and temporary DB removed,,PENDING,replay-regression.txt
pipeline_all,J00-J06 success on QA database,,PENDING,pipeline-all.txt
source_direct,3 family PASS lines,,PENDING,source-direct.txt
K01_202504,2271969,,PENDING,sql-kpi.txt
K06_202504,7153,,PENDING,sql-kpi.txt
K07_202504,24088,,PENDING,sql-kpi.txt
lineage_differences,0 each family,,PENDING,reports/07_reconciliation.csv
pipeline_rerun,J01/J02 SKIPPED and unchanged totals,,PENDING,pipeline-rerun.txt
J06_missing_family,FAIL with audit FAIL,,PENDING,replay-regression.txt
invalid_or_absent_month,nonzero exit and no success message,,PENDING,invalid-month.txt + absent-month.txt
report_isolation,outputs only in QA report-dir; tracked reports unchanged,,PENDING,
windows_restore,5 tables and 3 KPI match TV4 handoff,,PENDING,
powerbi_relationships,4 Single dimension-to-Mart relationships,,PENDING,
unknown_202504,206687 employment / 1591 accessions / 1936 separations,,PENDING,
sql_dax_same_filters,SQL equals DAX at month/agency filters,,PENDING,
PBIX_bus_matrix_dimension_catalog,TV4 supplies and approves,,PENDING,
independent_QA_conclusion,TV5 signs with reviewer/date/commit,,PENDING,
'@ | Set-Content -Encoding UTF8 (Join-Path $QaRoot 'expected-actual.csv')
git diff --exit-code -- reports
if ($LASTEXITCODE -ne 0) { throw 'Báo cáo bàn giao bị thay đổi; kiểm đường dẫn output.' }
git status --short
```

Lưu ảnh/model/PBIX reference, ghi tên reviewer, ngày, commit, Windows/PostgreSQL/Python/Power BI version và bộ lọc trong `$QaRoot`. Báo cáo nội bộ của reviewer gửi theo kênh nhóm; chỉ đưa evidence đã review vào repo khi nhóm thống nhất. TV4 chịu trách nhiệm PBIX, bus matrix, Dimension catalog và bằng chứng Windows; TV5 chịu trách nhiệm replay, SQL–DAX và kết luận QA độc lập. Tình trạng G2 tiếp tục **REVIEW**, mô hình **PROPOSED chờ TV4**, tích hợp **chờ TV4/TV5** theo [báo cáo tuần 2](../../reports/TV3_week2_summary.md).
