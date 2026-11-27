# Runbook cuối — Kho dữ liệu nhân sự liên bang (G3, 12 Parquet 03–06/2025)

**Bản gộp ngày 27/11/2026 (TV1, issue #56).** Đây là **một runbook duy nhất** cho bản trên `main`, đi từ nhận nguồn tới dump bàn giao, benchmark và đối chiếu SQL–DAX.
- **Chi tiết G3 (cách đọc từng file kết quả, phục hồi lỗi):** [`TV3_week3_runbook.md`](TV3_week3_runbook.md), phụ lục B.
- **Lệnh G2 tháng 04 cũ:** phụ lục A ở cuối file này.
- **Bối cảnh các sửa đổi:** [giải trình TV1](TV1_giai_trinh_tich_hop_G3.md).

## 1. Môi trường

| Thành phần | Yêu cầu | Ghi chú |
|---|---|---|
| PostgreSQL | ≥ 16; nhóm dùng 18 (Windows/Postgres.app) | Lượt chạy kiểm chứng 27/11 dùng 17.12. Mã dùng `pg_input_is_valid` (có từ 16) |
| Python | ≥ 3.11; nhóm dùng 3.12 | `pip install -r requirements.txt` |
| Nguồn | 12 Parquet theo [`docs/03_source_inventory.csv`](03_source_inventory.csv) | Thư mục phẳng hoặc `<raw-dir>/<family>/<file>` |
| Quyền DB | Role có `CREATEDB`, kết nối được DB `postgres` | Các bộ regression tạo rồi tự xóa DB tạm |

Cấu hình cục bộ: chép `configs/.env.example` thành `configs/.env.g3.local` (bị Git bỏ qua, **không commit**). Điền `PGHOST/PGPORT/PGUSER/PGPASSWORD`, `PGDATABASE` (tên DB mới) và `RAW_DATA_DIR`. Các lệnh `psql`/`createdb`/`pg_dump` không đọc file này, nên phải truyền `-h -p -U` hoặc dùng pgpass.

```sh
# macOS
python3.12 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt && .venv/bin/python -m pip check
```

```powershell
# Windows
py -3.12 -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt; .\.venv\Scripts\python.exe -m pip check
```

Các lệnh bên dưới viết cho macOS (`.venv/bin/python`). Trên Windows, thay bằng `.\.venv\Scripts\python.exe`, thêm `if ($LASTEXITCODE -ne 0) { throw }` sau mỗi lệnh, và đặt `git config core.autocrlf false` trước khi checkout.

## 2. Nhận và kiểm nguồn

```sh
.venv/bin/python etl/fetch_baseline.py --raw-dir <thư mục 12 Parquet>
```

Script kiểm SHA-256, bytes, số dòng, số cột, schema hash và kiểu text của cả 12 file. Lệch bất kỳ điểm nào là dừng, không ghi đè. Kỳ vọng: 12 dòng `VERIFIED`.

## 3. Regression trên dữ liệu giả (5 bộ, phải exit 0)

```sh
for t in g3_full_checks g2_source_checks g2_model_checks g2_replay_checks g2_coverage_checks; do
  .venv/bin/python -u tests/$t.py --config configs/.env.g3.local || break
done
```

`g2_model_checks` phải có các dòng: `PASS TV2-reviewed REVIEW agency loads…`, `PASS Fact lookup states…` và `PASS category Mart keeps key 0…`.

## 4. Nạp đủ 12 file, chạy lại May, kiểm chất lượng (khoảng 25 phút trên Apple M1)

```sh
createdb -h 127.0.0.1 -U <role> workforce_dw_g3_<tên>          # luôn dùng DB MỚI
.venv/bin/python -u etl/g3_pipeline.py --config configs/.env.g3.local \
  --database workforce_dw_g3_<tên> --raw-dir <thư mục 12 Parquet> \
  --report-dir .qa/<người chạy>/run01 --verify-rerun --quality-check
```

Bản chính thức trên repo dùng `--report-dir reports/week3`. Reviewer dùng `.qa/…` (Git bỏ qua). **Kỳ vọng:**

| Kiểm tra | Giá trị |
|---|---|
| Số dòng Source = Staging = ODS = Fact | 9.181.290 (Employment 9.057.997; Accessions 30.782; Separations 92.511) |
| J06 (`07_reconciliation.csv`) | 84 PASS + 12 PENDING (DAX) |
| `09_quality_checks.csv` | 152/152 PASS |
| Rerun May (`TV3_week3_rerun_results.csv`) | 17/17 bảng PASS |
| Agency Unknown (`09_source_quality.csv`) | 0 trên cả 12 file |
| Dimension / Mart | `dim_agency` 521; `workforce_monthly` 510; `personnel_flows_monthly` 361; `personnel_flows_category_monthly` 1.697; `dq_coverage_monthly` 104 |

## 5. Kiểm SQL

```sh
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -U <role> -d workforce_dw_g3_<tên> -f sql/tests/08_g3_full_baseline.sql
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -U <role> -d workforce_dw_g3_<tên> -f sql/07_g3_kpi.sql
```

Assertion phải in `PASS 12-file …, category Mart and K10 Mart baseline`. KPI tháng 04: K01 2.271.969; K02 −17.223; K06 7.153; K07 24.088; K08 −16.935.

## 6. Tạo dump bàn giao cho TV4 và kiểm restore

```sh
.venv/bin/python -u evidence/TV3_week3/verify_handoff.py --config configs/.env.g3.local \
  --database workforce_dw_g3_<tên> --target workforce_g3_transfer_<tên> --dump db_dumps/workforce_g3.dump
```

Script làm các bước sau:
1. Kiểm DDL chuyển giao khớp `03/04` (`g2_transfer.check_transfer_ddl`).
2. Chép 3 Dimension và 4 Mart sang DB chuyển giao.
3. `pg_dump -Fc`, rồi restore vào DB tạm.
4. So **từng dòng** 7 bảng; kiểm KPI 4 tháng và kiểm Mart category = K06/K07.

Khi bàn giao, chép `db_dumps/workforce_g3.dump` và `.sha256` vào `handoff/TV3_G3/`, rồi cập nhật [README bàn giao](../handoff/TV3_G3/README.md): checksum, số byte, số dòng. TV4 restore theo đúng README đó.

## 7. Bằng chứng, benchmark và đối chiếu SQL–DAX

```sh
.venv/bin/python -u evidence/TV3_week3/prepare_review.py --database workforce_dw_g3_<tên> --operator "<người chạy>"
.venv/bin/python -u evidence/TV3_week4/run_benchmark.py --database <DB benchmark RIÊNG> --operator "<người chạy>"
.venv/bin/python -u evidence/TV3_week4/build_sql_dax_reference.py --database <DB đã restore dump>
```

- **`prepare_review.py`:**
  - Kiểm hash code khớp lượt chạy; 20 báo cáo G2 giữ nguyên byte; 593 dòng event lệch kỳ được giữ.
  - Ghi `evidence/TV3_week3/00`–`08` và `reports/TV3_week3_summary.md`. Cần các log `.qa/TV3_G3/00`–`08_*.txt` từ các bước 2–5.
- **`run_benchmark.py`:** tạo rồi xóa index, nên **không** chạy trên DB bàn giao. Kết quả: `reports/week4/benchmark_results.csv` và [báo cáo](../reports/TV3_week4_benchmark.md).
- **`build_sql_dax_reference.py`:** đọc `sql/08_dashboard_reference.sql` (read-only), xuất `reports/week4/sql_dax_reference.csv` để TV4 điền cột `dax_value`.

## 8. Backup

- **Chỉ schema** (đã có trong repo): [`handoff/TV3_schema/workforce_schema.sql`](../handoff/TV3_schema/README.md).
- **DB đầy đủ** (vài GB, **không commit**):
  - Tạo: `pg_dump -Fc -d workforce_dw_g3_<tên> -f <ổ cá nhân>/workforce_full.dump`, rồi `shasum -a 256`.
  - Restore: `pg_restore --no-owner --no-acl --exit-on-error`.

## 9. Lỗi thường gặp

| Hiện tượng | Nguyên nhân / cách xử lý |
|---|---|
| `fetch_baseline` báo mismatch | File khác bản TV2. Không sửa hash; lấy lại đúng file từ mirror trong inventory |
| `Source identity/version conflict` | DB đã có file khác cùng family/tháng. Dùng DB mới; chỉ đổi version khi nhóm đã quyết định |
| `verify_week1`/LF lỗi trên Windows | `git config core.autocrlf false` rồi checkout lại |
| `06_g2_transfer.sql differs from 03/04` | Sửa DDL Mart ở `04_create_marts.sql` thì phải chép y hệt sang `06_g2_transfer.sql` |
| `Category Mart does not reconcile` | Lỗi dựng Mart; dừng lại, giữ DB để đọc `audit.load_run`, báo TV3 |
| Pipeline FAIL giữa chừng | File đã commit vẫn giữ; file lỗi được rollback. Đọc `run_manifest.json` và `audit.load_run`; sửa nguyên nhân rồi chạy lại cùng lệnh (file đúng sẽ được bỏ qua) |


## Phụ lục B — Runbook G3 chi tiết

Xem [`TV3_week3_runbook.md`](TV3_week3_runbook.md): cách đọc từng file kết quả, phục hồi lỗi, version và lệnh PowerShell đầy đủ. Phần TV4/TV5 trong đó nay dùng dump và bảng của mục 6 ở trên.

## Phụ lục A — Runbook G2 tháng 04/2025 (lịch sử, giữ để replay bằng chứng G2)

Tuần 3 có [runbook G3 riêng](TV3_week3_runbook.md) để nạp đủ 12 file, đối soát bốn kỳ và kiểm May rerun. Các lệnh/trạng thái MVP tháng 04 dưới đây được giữ để replay bằng chứng G2.

Pipeline dùng PostgreSQL 18, Python 3.12 và ba file Parquet baseline của TV2. Chạy các lệnh dưới từ thư mục gốc repo trên nhánh `tv3/g2-pipeline`. [Thiết kế G2](TV3_g2_model_decisions.md) ghi grain, khóa, kỳ thời gian và phần đang chờ TV4. [Báo cáo tuần 2](../reports/TV3_week2_summary.md) liên kết kết quả thực chạy và các mục review.

**TV5 trên Windows:** dùng [hướng dẫn PowerShell đầy đủ](../handoff/TV3_G2/TV5_REPLAY.md) để tạo Python 3.12/venv, nhận và kiểm hash ba Parquet, tạo database QA riêng, chạy regression và lưu expected/actual độc lập.

### Môi trường và nguồn

Mở Postgres.app, kiểm server đang chạy, rồi dùng môi trường Python đã chuẩn bị ở tuần 1. Điền `configs/.env` theo `configs/.env.example`, gồm host, port, database và user của máy chạy. Mật khẩu được lưu cục bộ khi server yêu cầu. [Hướng dẫn môi trường](06_environment_setup.md) có lệnh tạo venv và kiểm kết nối.

Các script Python đọc `configs/.env`. Công cụ `psql`, `createdb`, `pg_dump` và `pg_restore` dùng cấu hình libpq của Terminal; điều chỉnh host/port và thêm `-U <user>` theo máy thực tế. Mật khẩu được hỏi qua Terminal khi server yêu cầu.

Pipeline và trình đối soát trực tiếp chọn database theo `--database` → `PGDATABASE` trong file `--config` → `workforce_dw`; raw directory theo `--raw-dir` → `RAW_DATA_DIR` trong cấu hình → `data/raw` của repo. Đường dẫn tương đối trong CLI hoặc `RAW_DATA_DIR` tính từ thư mục đang chạy, vì vậy mở Terminal tại gốc repo. Có thể dùng đường dẫn tuyệt đối để tránh nhầm.

`--report-dir` của pipeline chọn nơi ghi cả ba CSV `07_load_log.csv`, `07_before_after.csv`, `07_reconciliation.csv`. Mặc định vẫn là `reports/` để tương thích. Reviewer luôn truyền thư mục QA riêng, ví dụ `.qa/TV5_G2/run01/reports` (được Git bỏ qua), để giữ báo cáo bàn giao. Các lượt chạy trong cùng thư mục ghi lại CSV, nên dùng thư mục mới khi cần giữ bằng chứng từng lượt.

```sh
psql --version
.venv/bin/python --version
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python etl/g2_pipeline.py --help
```

Đặt ba file sau trong `data/raw/`, hoặc truyền đường dẫn bằng `--raw-dir`. Loader cũng nhận cấu trúc `<raw-dir>/<family>/<filename>` của bộ dữ liệu TV2. So đúng filename và SHA-256 từ inventory trước khi chạy.

| File | Số dòng | Số cột |
| --- | ---: | ---: |
| `employment_202504_v4.parquet` | 2.271.969 | 64 |
| `accessions_202504_v5.parquet` | 7.153 | 68 |
| `separations_202504_v5.parquet` | 24.088 | 69 |

Ba checksum đầy đủ nằm trong [manifest](../data/manifest/sha256.txt) và [inventory TV2](03_source_inventory.csv). Schema hash được tính theo thứ tự các cặp `field_name:Arrow_type`, nối bằng `|`, SHA-256 lấy 16 ký tự đầu, khớp phương pháp TV2. Giữ các file raw ngoài Git.

Inventory/manifest tiếp nhận có 12 file. Lượt MVP TV3 chỉ tính lại hash, kiểm metadata và nạp ba file 202504 trên máy cục bộ. Kết quả kiểm 9 file các kỳ khác vẫn dựa trên đầu vào TV2 cho đến khi TV3 mở rộng pipeline và đo lại.

### Tạo bảng và chạy

Database `workforce_dw` đã được dùng cho tuần 1. Nếu replay trên máy mới, kiểm tên database trước rồi chỉ tạo khi chưa tồn tại. Dùng database riêng `workforce_dw_g2_check` cho kiểm DDL sạch. CLI đọc cấu hình cục bộ và nhận `--database` để chọn đích.

```sh
createdb -h 127.0.0.1 workforce_dw_g2_check
.venv/bin/python etl/g2_pipeline.py \
  --config configs/.env --database workforce_dw_g2_check \
  --month 202504 --raw-dir data/raw --job all \
  --report-dir .qa/TV5_G2/run01/reports
```

Luồng thực thi gồm J00 kiểm manifest/file/schema, J01 COPY theo batch vào Staging, J02 chuẩn hóa vào ODS, J03–J05 build Dimension/Fact/Mart và J06 đối soát. Mỗi dòng nguồn giữ cặp `file_id`–ordinal. Log ghi run_id, phiên bản mã, checksum, expected/actual, thời gian và lỗi.

Để kiểm riêng từng nhóm, dùng các job sau.

```sh
.venv/bin/python etl/g2_pipeline.py --database workforce_dw_g2_check --job init --report-dir .qa/TV5_G2/run01/reports
.venv/bin/python etl/g2_pipeline.py --database workforce_dw_g2_check --month 202504 --raw-dir data/raw --job source --report-dir .qa/TV5_G2/run01/reports
.venv/bin/python etl/g2_pipeline.py --database workforce_dw_g2_check --month 202504 --job model --report-dir .qa/TV5_G2/run01/reports
.venv/bin/python etl/g2_pipeline.py --database workforce_dw_g2_check --month 202504 --job check --report-dir .qa/TV5_G2/run01/reports
```

Lượt chạy cùng baseline đã nạp được kiểm rồi SKIPPED. Nếu checksum, bytes, schema hoặc row count lệch inventory, CLI ghi FAIL và kết thúc thất bại. Nếu file đổi version/hash so với metadata đã đăng ký, TV2/TV3 phải xác minh phiên bản dùng tính KPI. Khi xử lý lỗi, kiểm `audit.load_run`, CSV log và dữ liệu theo file_id trước khi chạy lại. Thay đổi nguồn hoặc rule chuẩn hóa cần cập nhật bằng chứng và chạy lại các phép đối soát liên quan.

### Kiểm SQL và dữ liệu bàn giao

```sh
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -d workforce_dw_g2_check \
  -v month=202504 -f sql/05_g2_kpi.sql
```

K01 toàn tháng 04 kỳ vọng 2.271.969. K06 theo report month kỳ vọng 7.153 và K07 kỳ vọng 24.088. Khi lọc agency trên Power BI, SQL tham chiếu dùng cùng `month_key` và `agency_key` hoặc `agency_code` của Mart. Key 0 là nhóm Unknown, tập hợp các mã chưa có một nhãn READY trong lookup theo kỳ. Mã gốc vẫn nằm trong ODS/Fact để TV2/TV5 kiểm lại.

Lượt chạy G2 tháng 04 (bản cũ) có 206.687 dòng Employment, 1.591 dòng Accessions và 1.936 dòng Separations trong agency Unknown.

> **Đã sửa ngày 27/11/2026.** Các dòng Unknown này đều thuộc 7 mã cơ quan ở trạng thái `REVIEW` vì nhãn khác EHRI. TV2 đã duyệt các mã đó là chỉ khác cách viết. Từ bản tích hợp G3, pipeline dùng kết quả duyệt này ([data/reference/README.md](../data/reference/README.md)), nên Agency Unknown của bốn kỳ bằng 0. Hãy dùng số của [báo cáo tuần 3](../reports/TV3_week3_summary.md); các con số ở trên chỉ còn giá trị lịch sử của G2.

TV4 cần trình bày rõ nhóm Unknown, nếu có, khi thử slicer; TV2/TV5 dùng mã gốc và trạng thái lookup để xác minh nhãn. [Báo cáo tuần 2](../reports/TV3_week2_summary.md) ghi phạm vi kết quả SQL và phần còn chờ xác nhận.

J06 yêu cầu đúng một file active/LOADED cho mỗi family trong tháng rồi kiểm source → Staging → ODS → Fact theo từng file và tổng measure Mart cùng kỳ. Thiếu hoặc trùng nguồn trả mã lỗi, CSV ghi FAIL tại `active_loaded_sources` và `audit.load_run` giữ J06 FAIL. Khi đủ nguồn và đúng số có 21 dòng PASS (3 coverage + 18 SQL), 3 dòng DAX PENDING chờ TV4/TV5. Truy vấn [lineage TV2](../sql/tests/06_fact_lineage.sql) là mẫu SQL cần bind cặp bảng cụ thể; CLI thực hiện các phép kiểm đã gắn tên bảng. Các trường hợp tháng hiệu lực khác tháng báo cáo được giữ. Baseline 202504 có 43 Accessions và 61 Separations lệch kỳ theo đối chiếu TV2.

Để đọc trực tiếp Parquet và đối chiếu chất lượng với ODS, chạy script sau. [Kết quả đã lưu](../evidence/TV3_week2/07_source_direct_crosscheck.txt) kiểm count, NULL/rỗng/REDACTED của pay, mã nghề có số 0 đầu và khác kỳ trên toàn ba file tháng 04.

```sh
.venv/bin/python evidence/TV3_week2/reconcile_sources.py \
  --config configs/.env --database workforce_dw_g2_check --month 202504 --raw-dir data/raw
```

### TV4 nhận DB và thử Power BI

TV4 nhận bản dump đã bổ sung trong nhánh tại [handoff/TV3_G2/workforce_g2.dump](../handoff/TV3_G2/workforce_g2.dump), dùng PostgreSQL 18 trên Windows và restore vào database mới/rỗng. [Hướng dẫn PowerShell và checksum](../handoff/TV3_G2/README.md) có lệnh kiểm file, restore và SELECT KPI. `localhost` trong kết nối Power BI chỉ đến PostgreSQL trên máy Windows của TV4.

```sh
# Máy Mac TV3: ví dụ xuất bản bàn giao từ database TV3 đã kiểm.
.venv/bin/python etl/g2_transfer.py --config configs/.env \
  --source workforce_dw --target workforce_g2_transfer
mkdir -p db_dumps
pg_dump -h 127.0.0.1 -d workforce_g2_transfer \
  -Fc --no-owner --no-acl -f db_dumps/workforce_g2.dump

# Kiểm restore trên Mac với database kiểm thử mới.
createdb -h 127.0.0.1 workforce_g2_restore_check
pg_restore -h 127.0.0.1 -d workforce_g2_restore_check \
  --no-owner --no-acl --exit-on-error db_dumps/workforce_g2.dump
```

Script chuyển dữ liệu chỉ nhận target rỗng, tự tạo database target nếu chưa có và đọc source trong một snapshot nhất quán. Nó chép ba Dimension và hai Mart rồi đối chiếu số dòng từng bảng. Bản xuất cục bộ trong `db_dumps/` được Git bỏ qua. Bản bàn giao đã kiểm được theo dõi riêng tại `handoff/TV3_G2/workforce_g2.dump`, với ngoại lệ Git áp dụng đúng đường dẫn này. Lần kiểm lại dùng tên database đích mới để giữ các bản đã kiểm.

Lượt bàn giao hiện tại đã copy và restore thử trên Mac vào `workforce_g2_restore_check`, với ba KPI sau restore khớp 2.271.969, 7.153 và 24.088. [Bằng chứng restore](../evidence/TV3_week2/06_transfer_restore.txt) ghi số dòng và SHA-256 dump để TV4 đối chiếu bản nhận.

```powershell
# Chạy từ thư mục gốc repo trên máy TV4, thay TV4_ROLE bằng user thực tế.
createdb -h 127.0.0.1 -U TV4_ROLE workforce_g2
pg_restore -h 127.0.0.1 -U TV4_ROLE -d workforce_g2 --no-owner --no-acl --exit-on-error .\handoff\TV3_G2\workforce_g2.dump
psql -X -h 127.0.0.1 -U TV4_ROLE -d workforce_g2 -c "SELECT month_key, SUM(headcount) FROM mart.workforce_monthly GROUP BY month_key;"
```

Trong Power BI Desktop, chọn PostgreSQL database, điền host `localhost:5432` và database `workforce_g2` cùng thông tin xác thực của TV4. Nạp `mart.workforce_monthly` và `mart.personnel_flows_monthly`. TV4 duyệt model/filter theo bus matrix, tạo measure thử và chụp model cùng filter đang dùng.

Nạp thêm `dw.dim_month` và `dw.dim_agency`, đổi tên bảng Power Query tương ứng thành `dim_month`, `dim_agency`, `workforce_monthly`, `personnel_flows_monthly`. Xem [sơ đồ quan hệ đề xuất và cách giữ Unknown](../handoff/TV3_G2/README.md): hai Dimension lọc một chiều tới cả hai Mart, slicer lấy từ Dimension. Tắt tự tạo quan hệ qua Month → Agency hoặc giữa hai Mart. Mart hiện hỗ trợ tháng/cơ quan; phân tích category cần TV4 thống nhất grain bổ sung.

```dax
K01 Headcount = SUM(workforce_monthly[headcount])
K06 Accessions = SUM(personnel_flows_monthly[accessions])
K07 Separations = SUM(personnel_flows_monthly[separations])
```

Lọc `month_key = 202504` khi đối soát. TV5 so SQL–DAX với cùng agency, kỳ và source version, ghi actual/PASS/FAIL vào báo cáo reconciliation và gắn ảnh bằng chứng. TV4 cần phản hồi cả kết quả restore, SELECT và kết nối PBIX. Phần kiểm Power BI trên Windows và ký xác nhận độc lập đang chờ TV4/TV5.

### Gói reviewer cần nhận

- Mã SQL/ETL, requirements, cấu hình mẫu và commit dùng chạy.
- Inventory/manifest cùng commit đầu vào TV2 và ba file raw qua kênh riêng.
- Log nạp, before–after, reconciliation và bằng chứng SQL trong `evidence/TV3_week2/`.
- Ba sơ đồ draw.io và PNG, bản thiết kế cần TV4 duyệt.
- [Dump tổng hợp cho TV4](../handoff/TV3_G2/workforce_g2.dump), checksum và kết quả kiểm restore.

TV5 replay dữ liệu nguồn và kiểm độc lập trên database riêng. Chỉ chốt G2 sau khi nhóm ghi nhận kết quả Power BI và QA thực tế trong [báo cáo bàn giao](../reports/TV3_week2_summary.md).