# Taxonomy nguồn dữ liệu Nhóm 13

| Nhánh | Grain và nhóm thuộc tính | Ví dụ từ baseline |
|---|---|---|
| Employment | Một bản ghi trạng thái trong snapshot. Có tổ chức, nghề, địa lý, pay plan và khoảng tuổi. | `employment_202504_v4.parquet`, 202504. `snapshot_yyyymm=202504`, `occupational_series_code=0301`. |
| Accessions | Một bản ghi hành động tiếp nhận. Có category, cơ quan và tháng hiệu lực. | `accessions_202504_v5.parquet`, kỳ file 202504. `accession_category_code=AC`; 43 bản ghi khác tháng hiệu lực. |
| Separations | Một bản ghi hành động rời cơ quan. Có category, tháng hiệu lực, và chỉ báo DRP khi có. | `separations_202504_v5.parquet`, kỳ file 202504. `separation_category_code=SC`; toàn file có 24.088 bản ghi. |
| Reference | Mã/nhãn quan sát và định nghĩa OPM. Phạm vi mã theo kỳ cần review. | `employment_202504_v4.parquet`, 202504. `pay_plan_code=GS`, `pay_plan=GENERAL SCHEDULE`. |
| Metadata kỹ thuật | Họ, kỳ, version, checksum, schema, số dòng/cột và ordinal. | `employment_202504_v4.parquet` có kỳ 202504, version v4 và 64 cột. |

`report_month` sinh từ tên file. NULL, rỗng và REDACTED có quy tắc riêng. Event đếm theo kỳ file mặc định và có vai trò thời gian hiệu lực riêng.

[Sơ đồ nguồn](../diagrams/03_opm_source_flow.drawio) · [Nguồn OPM](https://data.opm.gov/resources/data-sources) · [Dictionary](03_data_dictionary.csv) · [Nguồn tham chiếu](../data/reference/README.md)
