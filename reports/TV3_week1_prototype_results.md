# Kết quả nạp thử TV3 tuần 1

Chạy ngày 16/11/2026 trên MacBook M3 Pro, PostgreSQL 18.7 qua Postgres.app và Python 3.12.14. Batch tối đa 10.000 dòng. Hai file OPM thật thuộc kỳ 202504 và có tên, kích thước, số dòng cùng danh sách cột khớp hồ sơ TV1. SHA-256 toàn file khớp bản công khai tại revision đã ghi. TV2 cần cung cấp manifest để đối chiếu checksum baseline nhóm.

| Nguồn và phạm vi | Dòng trong footer | Kỳ vọng | SQL count | Ordinal | Khóa nguồn trùng | Kết quả |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| Accessions v5, toàn file | 7.153 | 7.153 | 7.153 | 1–7.153 | 0 | PASS |
| Employment v4, 50.000 dòng đầu | 2.271.969 | 50.000 | 50.000 | 1–50.000 | 0 | PASS |

Đối soát độc lập từng ô theo ordinal khớp **486.404 ô** ở Accessions và **3.200.000 ô** ở mẫu Employment. Có 68 và 64 cột nguồn tương ứng, đều lưu kiểu `text`. Ví dụ số đếm độc lập trong PostgreSQL tìm thấy 4.477 mã nghề bắt đầu bằng 0, 2.593 giá trị `REDACTED` ở mã địa điểm và 97 giá trị `NULL` ở cột lương của Accessions. Cả ba trường hợp được giữ trong dữ liệu nạp. Mẫu Employment dùng để kiểm đường nạp, không đại diện cho KPI toàn kỳ.

| Nguồn | SHA-256 | Đọc/chuyển batch | COPY | SQL check | Tổng | Dòng/giây COPY |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Accessions | 0,001 s | 0,026 s | 0,083 s | 0,003 s | 0,162 s | ~86.687 |
| Employment | 0,033 s | 0,127 s | 0,374 s | 0,021 s | 0,599 s | ~133.678 |

Tốc độ = số dòng / thời gian COPY chưa làm tròn trong CSV. Tổng bao gồm thiết lập kết nối, DDL, đọc nguồn, COPY, đối soát và commit. Đây là số đo một lượt nạp trên máy TV3.

Chạy lại Accessions giữ nguyên 7.153 dòng. Hai lượt thử sai checksum và lỗi dữ liệu khi COPY đều kết thúc với `FAIL` và giữ nguyên bảng đã nạp.

- [Metadata và SHA-256 nguồn](../evidence/TV3_week1/04_source_metadata.txt)
- [CSV log hai lượt chạy](TV3_week1_load_log.csv)
- [SQL kiểm tra](../sql/tests/TV3_week1_prototype_checks.sql) và [đầu ra SQL](../evidence/TV3_week1/05_prototype_counts.txt)
- [Đối soát từng ô Parquet và PostgreSQL](../evidence/TV3_week1/06_value_reconciliation.txt)
- [Kiểm tra chạy lại và lỗi](../evidence/TV3_week1/08_prototype_failure_checks.txt)
- [Hướng dẫn chạy lại](../docs/06_environment_setup.md#l3-02--nạp-lại-dữ-liệu-thử)
