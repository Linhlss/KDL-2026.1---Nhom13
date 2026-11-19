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
python -B evidence/TV2_week2/review_checks.py
```

Bộ chạy kiểm đủ 12 file và so độc lập số byte, dòng, cột, schema hash 16 ký tự và SHA-256 với crosscheck của TV1. Đối chiếu thêm workbook TV2 và pointer Git LFS của cả 12 URL mirror cho kết quả khớp SHA-256 và số byte. Nguồn raw lấy từ bộ TV2, có thể lưu ngoài repo. Trong notebook, đặt `TV2_RAW` để chọn cùng bộ.

## Kết quả xử lý review PR #42

- Audit tháng 03/2025 phân loại đúng 423 mã `agency_subelement_code` chỉ chứa dấu cách. Số bản ghi đủ điều kiện là 2.288.769 trên 2.289.192 dòng.
- Audit có số đo theo phạm vi mẫu OPM. Tháng 04, mã `AC` khớp 3.899 dòng Accessions và mã `SC` khớp 8.806 dòng Separations. K10 và orphan toàn file cần bộ mã đúng kỳ đầy đủ.
- DuckDB chạy 24 ca lineage trên ba cặp ODS/Fact, gồm ca hợp lệ và ca thiếu, thừa, trùng, NULL hoặc cùng tổng nhưng khác khóa. Ca J02 giữ đủ 8 dòng kiểm tra với các trạng thái khớp, Unknown, nhiều bản tham chiếu, NULL, rỗng và REDACTED.
- Đối soát trước/sau trên 12 file giữ nguyên 9.181.290 bản ghi, 269 Accessions và 324 Separations có tháng hiệu lực khác tháng file.

TV3 có thể chạy bộ kiểm lookup trên PostgreSQL bằng lệnh dưới đây. Kết quả mong đợi là 0 dòng lỗi. Khi J02 sẵn sàng, dùng cùng đầu vào và kết quả mong đợi để kiểm triển khai thực tế.

```powershell
python -B evidence/TV2_week2/review_checks.py --postgres-j02 | psql -X -v ON_ERROR_STOP=1
```

**Trạng thái REVIEW.** TV3 và TV4 xác nhận tên bảng, trường và vai trò kỳ theo DDL và bus matrix G2. TV5 kiểm độc lập theo #35/#38.
