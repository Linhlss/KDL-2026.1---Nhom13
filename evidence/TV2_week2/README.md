# Gói TV2 · dùng cho review G2

- **L2-01/02/03** · [Inventory](../../docs/03_source_inventory.csv), [SHA-256](../../data/manifest/sha256.txt), [nguồn OPM](../../data/reference/README.md), [Dictionary](../../docs/03_data_dictionary.csv).
- **L2-04/06/07/08** · [ERD, audit và mapping](../../docs/04_source_model_handoff.md), [ngoại lệ theo mã](relationship_exceptions.csv).
- **L2-05** · [Taxonomy và data flow](../../docs/03_taxonomy.md).
- **L2-09/10** · [Notebook](../../notebooks/01_eda.ipynb), [kết quả EDA](../../reports/05_eda_findings.md), [ví dụ tính tay](../../reports/05_categorical_method_example.md).
- **L2-11–13** · [Đối soát quy tắc J02](../../reports/07_source_quality_to_etl_rules.csv). Đây là diễn tập nguồn bằng DuckDB. TV3 cần tái chạy trên PostgreSQL sau khi J02 có sẵn.

## Chạy lại trên Windows

Cho `$tv2Raw` trỏ tới thư mục có ba thư mục con `employment/`, `accessions/` và `separations/`. Trên máy TV2 đã dùng bộ `E:/TV2_Data_Profiling/data/raw`. Chạy ở gốc repo.

```powershell
python -m pip install duckdb pyarrow scipy matplotlib
$tv2Raw = 'E:\TV2_Data_Profiling\data\raw'
python -B evidence/TV2_week2/source_baseline.py $tv2Raw
python -B evidence/TV2_week2/audit_relationships.py $tv2Raw
python -B evidence/TV2_week2/source_mapping.py
python -B evidence/TV2_week2/eda.py $tv2Raw
python -B evidence/TV2_week2/quality_handoff.py $tv2Raw
```

Bộ chạy kiểm đủ 12 file và so độc lập số byte, dòng, cột, schema hash 16 ký tự và SHA-256 với crosscheck của TV1. Đối chiếu thêm workbook TV2 và pointer Git LFS của cả 12 URL mirror cho kết quả khớp SHA-256 và số byte. Nguồn raw lấy từ bộ TV2, có thể lưu ngoài repo. Trong notebook, đặt `TV2_RAW` để chọn cùng bộ.

**Cần reviewer điền kết quả.** TV5 kiểm độc lập theo #35/#38. TV3/TV4 vẫn cần xác nhận tên bảng, trường, quan hệ và kỳ theo DDL/bus matrix G2. Tỷ lệ orphan và uniqueness theo catalog OPM cần thêm export hợp lệ cho 03–06/2025; audit hiện có dùng mã và nhãn quan sát được. DuckDB kiểm diễn tập J02 giữ nguyên 9.181.290 bản ghi, trong đó 593 action có tháng hiệu lực khác tháng file.
