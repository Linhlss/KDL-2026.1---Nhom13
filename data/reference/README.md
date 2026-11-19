# Nguồn định nghĩa và bảng mã TV2

[Reference manifest](reference_manifest.csv) ghi URL, ngày truy cập, phạm vi và vị trí tra cứu. [FWD Data Dictionary](https://data.opm.gov/FWD%20Data%20Dictionary.xlsx) là workbook công khai của OPM. Sheet1 cung cấp định nghĩa, ví dụ và họ áp dụng. Dùng EHRI Current/Past Values để kiểm danh mục cùng khoảng hiệu lực. Duty Stations là danh sách đang công bố.

[Manifest kiểm chứng](verified_codebook_manifest.csv) ghi trạng thái theo quan hệ. Lookup dẫn xuất từ Parquet dùng để khảo sát code–label với TV3 và TV5. Chỉ đặt FK sau khi kiểm đủ bảng mã đúng kỳ, khóa trùng, orphan và số dòng sau lookup.

[Mẫu đối chiếu OPM](opm_lookup_samples.csv) lấy mã Agency/Subelement và khoảng hiệu lực từ các tab [Current/Past Values](https://data.opm.gov/data-standards/agency-subelement). Mã `IN`, `AC` và `SC` lấy từ cột Sample Value của FWD Dictionary và có phạm vi minh họa. Bản xuất đầy đủ chưa lấy được, nên các phép đo này dùng phạm vi `SAMPLE`.

Audit tách NULL, chuỗi rỗng sau TRIM và REDACTED sau TRIM và so không phân biệt hoa thường. Với khóa ghép, thứ tự phân loại là NULL → rỗng → REDACTED. Giá trị gốc, gồm số 0 đầu mã, được giữ để so khớp chính xác.

Các phép đối chiếu chính thức chạy theo từng file, dùng ngày cuối tháng báo cáo để lọc khoảng hiệu lực theo cả hai đầu. Với `SAMPLE`, các trường `reference_*` chỉ đo tập mã mẫu. `reference_left_join_rows` tính số dòng LEFT JOIN trước khi lọc trùng, dùng số bản ghi theo mã nhân số dòng tham chiếu khớp, hoặc nhân 1 nếu không khớp. `orphan_rows`, `duplicate_ref_keys` và tỷ lệ K10 của toàn file để trống khi thiếu bộ mã đầy đủ. Event vẫn giữ tháng hiệu lực riêng.

Khi có export đầy đủ, chạy `audit_relationships.py <raw> --references <csv>` với cùng cột như file mẫu. Mỗi quan hệ dùng một phạm vi, `SAMPLE` hoặc `COMPLETE`. Chỉ dùng `COMPLETE` cho bộ mã bao phủ toàn miền khóa và các kỳ cần kiểm, ghi rõ nguồn và ngày bắt đầu hiệu lực. Ngày kết thúc trống biểu thị còn hiệu lực. Giữ các dòng tham chiếu vốn trùng để audit phát hiện được chúng.
