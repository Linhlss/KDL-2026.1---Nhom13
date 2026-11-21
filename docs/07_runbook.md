# Chạy pipeline G2 tháng 04 năm 2025

Pipeline dùng PostgreSQL 18, Python 3.12 và ba file Parquet baseline của TV2. Chạy các lệnh dưới từ thư mục gốc repo trên nhánh `tv3/g2-pipeline`. [Thiết kế G2](TV3_g2_model_decisions.md) ghi grain, khóa, kỳ thời gian và phần đang chờ TV4. [Báo cáo tuần 2](../reports/TV3_week2_summary.md) liên kết kết quả thực chạy và các mục review.

## Môi trường và nguồn

Mở Postgres.app, kiểm server đang chạy, rồi dùng môi trường Python đã chuẩn bị ở tuần 1. Điền `configs/.env` theo `configs/.env.example`, gồm host, port, database và user của máy chạy. Mật khẩu được lưu cục bộ khi server yêu cầu. [Hướng dẫn môi trường](06_environment_setup.md) có lệnh tạo venv và kiểm kết nối.

Các script Python đọc `configs/.env`. Công cụ `psql`, `createdb`, `pg_dump` và `pg_restore` dùng cấu hình libpq của Terminal; điều chỉnh host/port và thêm `-U <user>` theo máy thực tế. Mật khẩu được hỏi qua Terminal khi server yêu cầu.

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

## Tạo bảng và chạy

Database `workforce_dw` đã được dùng cho tuần 1. Nếu replay trên máy mới, kiểm tên database trước rồi chỉ tạo khi chưa tồn tại. Dùng database riêng `workforce_dw_g2_check` cho kiểm DDL sạch. CLI đọc cấu hình cục bộ và nhận `--database` để chọn đích.

```sh
.venv/bin/python etl/g2_pipeline.py \
  --config configs/.env --database workforce_dw \
  --month 202504 --raw-dir data/raw --job all
```

Luồng thực thi gồm J00 kiểm manifest/file/schema, J01 COPY theo batch vào Staging, J02 chuẩn hóa vào ODS, J03–J05 build Dimension/Fact/Mart và J06 đối soát. Mỗi dòng nguồn giữ cặp `file_id`–ordinal. Log ghi run_id, phiên bản mã, checksum, expected/actual, thời gian và lỗi.

Để kiểm riêng từng nhóm, dùng các job sau.

```sh
.venv/bin/python etl/g2_pipeline.py --database workforce_dw --job init
.venv/bin/python etl/g2_pipeline.py --database workforce_dw --month 202504 --raw-dir data/raw --job source
.venv/bin/python etl/g2_pipeline.py --database workforce_dw --month 202504 --job model
.venv/bin/python etl/g2_pipeline.py --database workforce_dw --month 202504 --job check
```

Lượt chạy cùng baseline đã nạp được kiểm rồi SKIPPED. Nếu checksum, bytes, schema hoặc row count lệch inventory, CLI ghi FAIL và kết thúc thất bại. Nếu file đổi version/hash so với metadata đã đăng ký, TV2/TV3 phải xác minh phiên bản dùng tính KPI. Khi xử lý lỗi, kiểm `audit.load_run`, CSV log và dữ liệu theo file_id trước khi chạy lại. Thay đổi nguồn hoặc rule chuẩn hóa cần cập nhật bằng chứng và chạy lại các phép đối soát liên quan.

## Kiểm SQL và dữ liệu bàn giao

```sh
psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -d workforce_dw \
  -v month=202504 -f sql/05_g2_kpi.sql
```

K01 toàn tháng 04 kỳ vọng 2.271.969. K06 theo report month kỳ vọng 7.153 và K07 kỳ vọng 24.088. Khi lọc agency trên Power BI, SQL tham chiếu dùng cùng `month_key` và `agency_key` hoặc `agency_code` của Mart. Key 0 là nhóm Unknown, tập hợp các mã chưa có một nhãn READY trong lookup theo kỳ. Mã gốc vẫn nằm trong ODS/Fact để TV2/TV5 kiểm lại.

Lượt chạy tháng 04 có 206.687 dòng Employment, 1.591 dòng Accessions và 1.936 dòng Separations trong agency Unknown. TV4 cần trình bày rõ nhóm này khi thử slicer; TV2/TV5 dùng mã gốc và trạng thái lookup để xác minh nhãn. [Báo cáo tuần 2](../reports/TV3_week2_summary.md) ghi phạm vi kết quả SQL và phần còn chờ xác nhận.

J06 kiểm source → Staging → ODS → Fact theo từng file và tổng measure Mart cùng kỳ. Truy vấn [lineage TV2](../sql/tests/06_fact_lineage.sql) là mẫu SQL cần bind cặp bảng cụ thể; CLI thực hiện các phép kiểm đã gắn tên bảng. Các trường hợp tháng hiệu lực khác tháng báo cáo được giữ. Baseline 202504 có 43 Accessions và 61 Separations lệch kỳ theo đối chiếu TV2.

Để đọc trực tiếp Parquet và đối chiếu chất lượng với ODS, chạy script sau. [Kết quả đã lưu](../evidence/TV3_week2/07_source_direct_crosscheck.txt) kiểm count, NULL/rỗng/REDACTED của pay, mã nghề có số 0 đầu và khác kỳ trên toàn ba file tháng 04.

```sh
.venv/bin/python evidence/TV3_week2/reconcile_sources.py \
  --config configs/.env --database workforce_dw --month 202504 --raw-dir data/raw
```

## TV4 nhận DB và thử Power BI

TV3 chuẩn bị database chuyển riêng chứa Mart và các Dimension phụ thuộc, tạo dump định dạng custom rồi kiểm restore trên máy Mac. TV4 nhận dump qua kênh riêng, dùng PostgreSQL 18 trên Windows và restore vào database mới/rỗng. `localhost` trong kết nối Power BI chỉ đến PostgreSQL trên máy Windows của TV4.

```sh
# Máy Mac TV3, dùng target mới hoặc rỗng.
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

Script chuyển dữ liệu chỉ nhận target rỗng, tự tạo database target nếu chưa có và đọc source trong một snapshot nhất quán. Nó chép ba Dimension và hai Mart rồi đối chiếu số dòng từng bảng. File dump nằm trong `db_dumps/` được Git bỏ qua. Lần kiểm lại dùng tên database đích mới để giữ các bản đã kiểm.

Lượt bàn giao hiện tại đã copy và restore thử trên Mac vào `workforce_g2_restore_check`, với ba KPI sau restore khớp 2.271.969, 7.153 và 24.088. [Bằng chứng restore](../evidence/TV3_week2/06_transfer_restore.txt) ghi số dòng và SHA-256 dump để TV4 đối chiếu bản nhận.

```sh
# Máy TV4, thay TV4_ROLE và đường dẫn bằng giá trị thực tế.
createdb -h 127.0.0.1 -U TV4_ROLE workforce_g2
pg_restore -h 127.0.0.1 -U TV4_ROLE -d workforce_g2 \
  --no-owner --no-acl --exit-on-error work/workforce_g2.dump
psql -X -h 127.0.0.1 -U TV4_ROLE -d workforce_g2 \
  -c "SELECT month_key, SUM(headcount) FROM mart.workforce_monthly GROUP BY month_key;"
```

Trong Power BI Desktop, chọn PostgreSQL database, điền host `localhost:5432` và database `workforce_g2` cùng thông tin xác thực của TV4. Nạp `mart.workforce_monthly` và `mart.personnel_flows_monthly`. TV4 duyệt model/filter theo bus matrix, tạo measure thử và chụp model cùng filter đang dùng.

```dax
K01 Headcount = SUM(workforce_monthly[headcount])
K06 Accessions = SUM(personnel_flows_monthly[accessions])
K07 Separations = SUM(personnel_flows_monthly[separations])
```

Lọc `month_key = 202504` khi đối soát. TV5 so SQL–DAX với cùng agency, kỳ và source version, ghi actual/PASS/FAIL vào báo cáo reconciliation và gắn ảnh bằng chứng. TV4 cần phản hồi cả kết quả restore, SELECT và kết nối PBIX. Phần kiểm Power BI trên Windows và ký xác nhận độc lập đang chờ TV4/TV5.

## Gói reviewer cần nhận

- Mã SQL/ETL, requirements, cấu hình mẫu và commit dùng chạy.
- Inventory/manifest cùng commit đầu vào TV2 và ba file raw qua kênh riêng.
- Log nạp, before–after, reconciliation và bằng chứng SQL trong `evidence/TV3_week2/`.
- Ba sơ đồ draw.io và PNG, bản thiết kế cần TV4 duyệt.
- Dump chuyển riêng và kết quả kiểm restore, khi reviewer cần tái hiện tích hợp.

TV5 replay dữ liệu nguồn và kiểm độc lập trên database riêng. Chỉ chốt G2 sau khi nhóm ghi nhận kết quả Power BI và QA thực tế trong [báo cáo bàn giao](../reports/TV3_week2_summary.md).
