# Chạy và bàn giao pipeline G3 tuần 3

Chạy ở gốc repo, nhánh `tv3/g3-full-pipeline`. Nhánh này kế thừa G2 commit `3b30235`; [PR G2 #43](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/43) chưa merge tại lúc bắt đầu. Không checkout main cũ rồi bỏ mất phần G2. Mô hình tháng/cơ quan hiện tại vẫn PROPOSED, chờ TV4 duyệt; xem [quyết định và dependency](TV3_g3_model_review.md). Không coi G2/G3 đã nghiệm thu.

## Môi trường và nhận nguồn

Python 3.12, PostgreSQL 18 và [requirements](../requirements.txt). Mac dùng `.venv/bin/python`; Windows dùng `.\.venv\Scripts\python.exe`. [Hướng dẫn Windows G2](../handoff/TV3_G2/TV5_REPLAY.md) có cách tạo venv và cấu hình PostgreSQL; lệnh G3 dưới đây thay entrypoint và phạm vi nguồn. Cấu hình cục bộ theo [mẫu](../configs/.env.example). Không commit mật khẩu/raw hoặc dump tùy ý; bản bàn giao G3 đã kiểm được theo dõi riêng tại [handoff/TV3_G3](../handoff/TV3_G3/README.md).

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
cp -n configs/.env.example configs/.env.g3.local
```

Điền host/port/user/password đúng máy, đặt `PGDATABASE=workforce_dw_g3_qa` và `RAW_DATA_DIR=./data/raw`. CLI database/raw ưu tiên tham số, rồi cấu hình, cuối cùng mặc định G2. Đường dẫn tương đối tính từ thư mục chạy. `psql`/`createdb`/`pg_dump` không đọc dotenv: truyền cùng host/port/user hoặc dùng pgpass cục bộ.

Nhận đủ 12 file từ TV2 theo [inventory](03_source_inventory.csv) và [manifest](../data/manifest/sha256.txt), hoặc dùng công cụ nhận từ đúng URL mirror đã ghi trong inventory:

```sh
.venv/bin/python etl/fetch_baseline.py --raw-dir data/raw
```

Script kiểm cả file đã có, nhận file thiếu vào tệp tạm và chỉ đổi tên sau khi SHA-256, bytes, row count, column count, schema hash và kiểu text khớp. Mismatch dừng xử lý, không thay expected/hash và không ghi đè bản lỗi đã có. Hỗ trợ raw phẳng hoặc `<raw-dir>/<family>/<filename>`. File rác không có trong inventory không được chọn. Employment v4; Accessions/Separations v5; tháng 202503–202506.

## Kiểm thử trước lượt nạp đầy đủ

Role QA cần kết nối database bảo trì `postgres`, CREATEDB và quyền xóa các database do mình tạo. Bốn regression dùng fixture tổng hợp trong database riêng; các fixture không thay cho dữ liệu HR thật.

```sh
.venv/bin/python tests/g2_source_checks.py --config configs/.env.g3.local
.venv/bin/python tests/g2_model_checks.py --config configs/.env.g3.local
.venv/bin/python tests/g2_replay_checks.py --config configs/.env.g3.local
.venv/bin/python tests/g3_full_checks.py --config configs/.env.g3.local
```

G3 regression kiểm đủ bốn tháng, ghép báo cáo 12 file, rerun May, dữ liệu có cùng tổng nhưng đổi trường nghiệp vụ, gate `count_value=1` và xuất audit FAIL khi thiếu file. Các test nguồn cũ kiểm checksum/version/COPY rollback. Thành công mỗi lệnh phải có exit code 0; PowerShell kiểm `$LASTEXITCODE` như runbook G2.

## Nạp đủ 12 file và kiểm chạy lại May

Tạo database mới, không xóa DB G2 hoặc DB có dữ liệu hợp lệ. Dùng tên mới nếu đích đã tồn tại và chưa xác minh. Ngừng các writer khác trong database QA khi đo trước/sau.

```sh
createdb -h 127.0.0.1 -U YOUR_ROLE workforce_dw_g3_qa
.venv/bin/python -u etl/g3_pipeline.py \
  --config configs/.env.g3.local --database workforce_dw_g3_qa \
  --raw-dir data/raw --report-dir .qa/TV5_G3/run01 \
  --verify-rerun --quality-check
```

Lệnh PowerShell tương đương (venv đã tạo bằng `py -3.12 -m venv .venv`):

```powershell
$Python = '.\.venv\Scripts\python.exe'
$Database = 'workforce_dw_g3_qa'
$Reports = '.qa\TV5_G3\run01'
createdb -h 127.0.0.1 -U YOUR_ROLE $Database
if ($LASTEXITCODE -ne 0) { throw 'Cần database QA mới và quyền hợp lệ.' }
& $Python .\etl\fetch_baseline.py --raw-dir .\data\raw
if ($LASTEXITCODE -ne 0) { throw 'Nguồn chưa khớp baseline.' }
& $Python -u .\etl\g3_pipeline.py --config .\configs\.env.g3.local --database $Database --raw-dir .\data\raw --report-dir $Reports --verify-rerun --quality-check
if ($LASTEXITCODE -ne 0) { throw 'G3 FAIL; xem audit và run_manifest.json.' }
```

Mặc định `--months 202503 202504 202505 202506`; có thể truyền một/nhiều tháng khác có trong inventory. `--verify-rerun` yêu cầu phạm vi gồm 202505. Bỏ cờ này khi chỉ nạp/kiểm. `--job check --quality-check` chỉ đối soát dữ liệu đã nạp, không build; kết hợp `--verify-rerun` sẽ thực sự chạy lại chuỗi May nên không còn là read-only.

J00 kiểm file; J01/J02 dùng transaction theo file và ordinal xuyên batch. J03–J05 transaction theo tháng, giữ tháng khác, tạo khóa Dim bằng upsert theo natural key đã xác định. Mart được refresh từ tất cả Fact đã lưu trong cùng transaction build. Event aggregate từng Fact rồi UNION ALL về tháng/cơ quan. Chỉ một nguồn/version cho mỗi family/tháng; nguồn đã LOADED cùng identity/hash được SKIPPED. `count_value` bắt buộc 1 trước build để bảo vệ grain một dòng nguồn. Cột này là measure record_count/event_count trong thiết kế, không phải employee_id.

J06 chạy cho từng tháng. Cờ quality-check tính lại checksum/metadata và các metric trực tiếp từ toàn bộ Parquet, so ODS, ordinal, khóa thời gian Fact, orphan Dimension/FK và uniqueness natural key. Các kiểm SQL này do TV3 chạy; DAX giữ PENDING.

## Kết quả và cách đọc

Mặc định G3 ghi vào `reports/week3/`, giữ CSV G2 ở `reports/` nguyên vẹn. Reviewer luôn dùng `--report-dir .qa/TV5_G3/<run>` để giữ kết quả riêng. Thư mục cùng tên bị ghi lại khi rerun; chọn thư mục mới để giữ nhiều lượt.

| File trong report-dir | Nội dung |
| --- | --- |
| `run_manifest.json` | Commit, SHA-256 mã ETL/inventory, database, tháng, batch size, thời gian và RUNNING/SUCCESS/FAIL |
| `07_load_log.csv` | Audit mọi lượt trong DB: family/month/version/hash, expected/actual, read/written/rejected, duration, status/error |
| `07_file_counts.csv` | 12 dòng theo file, Source/Staging/ODS/Fact |
| `07_before_after.csv` | Rule và affected_rows cho đủ file/tháng |
| `07_reconciliation.csv` | test_id, input_version, layer/table, filter, expected/actual/delta, status/evidence/reviewer/tested_at |
| `monthly/<month>/` | CSV G2 tương thích theo từng tháng |
| `08_dimension_observed.csv` | Catalog thực đo: grain, natural/surrogate key, số dòng, ví dụ, Unknown, provenance; chờ TV4 duyệt |
| `09_quality_checks.csv`, `09_source_quality.csv`, `09_constraints.csv` | Raw–ODS, ordinal/time-role/FK, Unknown và trạng thái constraint |
| `rerun_before.json`, `rerun_after.json` | Snapshot count/digest của registry, source identities, Dim/Fact/Mart |
| `TV3_week3_rerun_results.csv` | Trước/sau từng bảng, expected/actual/delta và kết luận May |

`rows_read` là actual của J00/J01/J02 đã thành công/skip; J00 đọc metadata+hash toàn file. `rows_written` là số dòng commit ở J01/J02 SUCCESS, bằng 0 khi skip hoặc rollback. `rows_rejected=0` khi thành công; khi lỗi thì để trống vì reader có thể dừng giữa chừng. Các dòng source bị lỗi không được âm thầm bỏ qua. Không dùng số lượt audit để đếm file active.

Digest sử dụng PostgreSQL binary COPY, cùng kiểu/cột và thứ tự PK. Staging/ODS so cặp file_id/ordinal; Fact/Dim/Mart so mọi cột nghiệp vụ; registry bỏ timestamp vận hành. Không so run_id hoặc thời gian audit. Phạm vi gồm toàn bộ tháng đã lưu, do đó 03/04/06 và MoM June cũng được bảo vệ khi rerun May. Snapshot này so trên cùng database/server; không dùng digest binary để so hai phiên bản PostgreSQL khác nhau.

Expected theo nguồn: Employment 9.057.997, Accessions 30.782, Separations 92.511; tổng 9.181.290 bản ghi qua các kỳ. J06 cho bốn tháng có 84 PASS kỹ thuật + 12 PENDING DAX. Event khác kỳ phải giữ đủ 269 Accessions + 324 Separations = 593; riêng May = 107. K01 tháng 04 = 2.271.969, K02 = −17.223, K03 dùng mẫu số 2.289.192; K06/K07 = 7.153/24.088, K08 = −16.935 lượt, khác phép đo headcount change.

```sh
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -U YOUR_ROLE -d workforce_dw_g3_qa -f sql/tests/08_g3_full_baseline.sql
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -U YOUR_ROLE -d workforce_dw_g3_qa -f sql/07_g3_kpi.sql
```

SQL thứ nhất có assertion trả lỗi khi số không khớp. SQL KPI xuất từng tháng và từng cơ quan để TV4/TV5 so cùng filter với DAX. K02/K03 thiếu tháng trước hoặc mẫu số 0 giữ NULL/BLANK. Không cộng bốn snapshot thành số người duy nhất. Hai Mart hiện không có category key hoặc các chiều nghề/địa lý/grade; mở rộng cần TV4 thống nhất grain, không dùng slicer category giả.

## Lỗi, phục hồi và version

Giữ database lỗi để đọc audit. Sau lỗi file, các file đã commit vẫn còn, file lỗi rollback; source loader không checkpoint nửa file. Kiểm run_manifest FAIL, audit FAIL và CSV trước khi sửa. Chạy lại cùng lệnh sau khi trả đúng file baseline sẽ skip nguồn hợp lệ và tiếp tục tháng cần build. Lỗi model rollback cả rebuild Fact/Mart tháng đó; kết quả Mart hợp lệ trước đó giữ nguyên.

Hash/version/tên file đổi phải dừng để TV2/TV3 xác minh. Registry hiện cố ý chỉ cho một version mỗi family/tháng; chưa có luồng replacement thành công. Không sửa raw thật để mô phỏng HR. Regression dùng fixture tách biệt để kiểm lỗi COPY/schema và gate version; metadata mismatch đã thử. Replacement thật ghi **NOT_TESTED**, cần bản republish thật đã xác minh và quyết định active/recovery của nhóm trước khi triển khai. Đó là giới hạn đã ghi của hệ thống, không đánh PASS bằng nhánh skip.

## Bàn giao TV4 và TV5

TV4 tải ngay [workforce_g3.dump và SHA-256 trong repo](../handoff/TV3_G3/README.md). Bản này được bổ sung theo yêu cầu bàn giao, khớp dump đã kiểm. Khi cần tạo lại bản aggregate-only để review, dùng script đã có và xuất cục bộ:

```sh
mkdir -p db_dumps
.venv/bin/python etl/g2_transfer.py --config configs/.env.g3.local --source workforce_dw_g3_qa --target workforce_g3_transfer
pg_dump -h 127.0.0.1 -U YOUR_ROLE -d workforce_g3_transfer -Fc --no-owner --no-acl -f db_dumps/workforce_g3.dump
shasum -a 256 db_dumps/workforce_g3.dump
```

Tạo `db_dumps/` trước khi xuất, chọn target mới/rỗng. Ghi checksum/PG version và count. Bản đã kiểm cho TV4 được commit duy nhất tại handoff/TV3_G3/workforce_g3.dump cùng checksum; db_dumps/ vẫn là thư mục cục bộ. Windows dùng PostgreSQL 18, createdb mới và pg_restore --no-owner --no-acl --exit-on-error. Lệnh chi tiết và bốn relationship Single giống [gói TV4](../handoff/TV3_G2/README.md), nhưng thay dump/database/tổng count bằng bằng chứng G3. Không dùng dump MVP tháng 04 để đại diện G3 đủ bốn kỳ.

TV4 nhận ba Dimension/hai Mart đủ kỳ, catalog quan sát và SQL; phản hồi một tổng/một cơ quan thật cùng bộ lọc, PBIX/model và duyệt thiết kế. TV5 nhận cả 12 Parquet qua kênh nguồn, tự chạy full/rerun trên DB riêng, ghi rõ phạm vi chạy, actual/PASS/FAIL, tên reviewer/ngày/commit. TV1 chốt lịch và G3; không tự tạo số issue tuần 3 khi chưa có.
