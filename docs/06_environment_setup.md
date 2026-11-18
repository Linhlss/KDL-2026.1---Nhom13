# Môi trường và cách chạy prototype TV3 tuần 1

Đã chạy trên MacBook M3 Pro (Apple Silicon, macOS 27.0) với Postgres.app 18.7, cổng 5432, và Python 3.12.14. PostgreSQL lưu trong database cục bộ `workforce_dw`. Power BI Desktop sẽ chạy trên Windows của TV4. Xem [kết quả kiểm tra PostgreSQL](../evidence/TV3_week1/01_postgres_environment.txt).

## L3-01 · Chuẩn bị môi trường

Chạy từ thư mục gốc repo. Mở Postgres.app và xác nhận server đang chạy. Terminal trên máy TV3 đã nhận `psql`; nếu máy khác chưa nhận, chỉ cần thêm đường dẫn cho phiên Terminal hiện tại.

```sh
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
psql --version
psql -X -w -h 127.0.0.1 -d postgres -c "SELECT current_user, current_setting('server_version'), inet_server_port();"
psql -X -w -h 127.0.0.1 -d postgres -Atc "SELECT datname FROM pg_database WHERE datname = 'workforce_dw';"
```

Nếu lệnh cuối trả về rỗng, chạy `createdb -h 127.0.0.1 workforce_dw` bằng role có quyền tạo database. Nếu server yêu cầu mật khẩu, dùng cấu hình xác thực của máy và bỏ `-w` để `psql` hỏi mật khẩu. Lệnh sau có thể chạy lại trên database đã có.

```sh
psql -X -h 127.0.0.1 -d workforce_dw -f sql/01_create_schemas.sql
psql -X -h 127.0.0.1 -d workforce_dw -c '\dn'
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
cp -n configs/.env.example configs/.env
chmod 600 configs/.env
```

Điền `PGUSER` bằng kết quả `current_user` và điều chỉnh `RAW_DATA_DIR` theo nơi lưu Parquet. Chỉ điền `PGPASSWORD` cục bộ nếu server yêu cầu. Git đã bỏ qua `configs/.env`, `.venv`, `data/raw`, Parquet và DB dump.

| Schema | Vai trò |
| --- | --- |
| `raw_meta`, `audit` | Metadata nguồn và log ETL khi nhóm triển khai pipeline |
| `staging` | Hai bảng nạp thử tuần 1 |
| `ref`, `ods` | Bộ mã tham chiếu và bản ghi nguồn đã chuẩn hóa |
| `dw`, `mart` | Mô hình phân tích và bảng tổng hợp |

## L3-02 · Nạp lại dữ liệu thử

Lấy đúng file cùng kỳ và version từ TV2. Lượt chạy hiện tại dùng bản OPM Parquet công khai đã ghim revision và kiểm SHA-256 ở [hồ sơ nguồn](../evidence/TV3_week1/04_source_metadata.txt). Hai file khớp metadata TV1 về tên, kích thước, số dòng và số cột. Cần TV2 xác nhận checksum của bộ baseline nhóm.

```sh
ACCESSIONS_SHA=933b33c65b2553867efce924cfe87696ba5152c25d0861b5f1cb085481da72fa
EMPLOYMENT_SHA=d0bfcf7158fbd552469ec2f8df84cb0ec12c51578e6c571aa21d7c32fe203e72

.venv/bin/python etl/prototype_ingest.py \
  --file accessions_202504_v5.parquet --family accessions --month 202504 \
  --version 5 --expected-sha256 "$ACCESSIONS_SHA" \
  --log reports/TV3_week1_load_log.local.csv

.venv/bin/python etl/prototype_ingest.py \
  --file employment_202504_v4.parquet --family employment --month 202504 \
  --version 4 --limit 50000 --expected-sha256 "$EMPLOYMENT_SHA" \
  --log reports/TV3_week1_load_log.local.csv
```

`--file` nhận đường dẫn đầy đủ hoặc tên trong `RAW_DATA_DIR`. Nếu dùng Separations, thay file, family và checksum tương ứng, rồi bỏ giới hạn số dòng. Có thể chỉ định file cấu hình với `--config`. Khi verifier chạy lại, dùng log cục bộ khác để giữ [log đã bàn giao](../reports/TV3_week1_load_log.csv).

Loader đọc bằng PyArrow theo batch 10.000 dòng, thêm checksum và ordinal rồi dùng PostgreSQL COPY. Hai file thực tế có toàn bộ cột nguồn dạng chuỗi nên được lưu dạng `text`. Checksum là của toàn file kể cả khi chỉ nạp mẫu. Mỗi lượt chạy dùng một transaction. Nếu thành công, bảng prototype của đúng family được cập nhật theo lần nạp mới. Nếu lỗi, transaction được rollback và lượt chạy được ghi `FAIL`. Loader chỉ thay bảng đã có dấu nhận diện do chính prototype tạo.

Từ cùng Terminal, đối soát bằng các lệnh sau.

```sh
psql -X -h 127.0.0.1 -d workforce_dw \
  -v target=prototype_accessions -v expected_rows=7153 \
  -v expected_source_columns=68 -v expected_sha256="$ACCESSIONS_SHA" \
  -f sql/tests/TV3_week1_prototype_checks.sql

psql -X -h 127.0.0.1 -d workforce_dw \
  -v target=prototype_employment -v expected_rows=50000 \
  -v expected_source_columns=64 -v expected_sha256="$EMPLOYMENT_SHA" \
  -f sql/tests/TV3_week1_prototype_checks.sql
```

Hai lệnh kiểm số dòng, ordinal, checksum và kiểu cột của đúng cặp file trên. Nếu dùng một file khác, cập nhật các tham số theo footer Parquet và checksum đã đối chiếu. Xem [kết quả nạp thử](../reports/TV3_week1_prototype_results.md).

## L3-03 · Phương án bàn giao TV4

Power BI Desktop dự kiến đọc Mart qua PostgreSQL trên máy Windows của TV4. Khi có Mart mẫu, TV3 tạo bản sao PostgreSQL theo phạm vi được nhóm chọn, chuyển riêng cho TV4 và ghi phiên bản nguồn/đích. TV4 dùng PostgreSQL 18 để restore và thử kết nối Power BI với DB Windows. Hai máy giữ kết nối cục bộ trong phương án này. TV4 cần phản hồi về khả năng restore và môi trường Power BI. Trạng thái hiện tại là dự kiến. Xem [sơ đồ triển khai v0](../diagrams/06_architecture_components.png).
