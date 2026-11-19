# Nguồn định nghĩa và bảng mã TV2

[Reference manifest](reference_manifest.csv) ghi URL, ngày truy cập, phạm vi và vị trí tra cứu. [FWD Data Dictionary](https://data.opm.gov/FWD%20Data%20Dictionary.xlsx) là workbook công khai của OPM. Sheet1 cung cấp định nghĩa, ví dụ và họ áp dụng. Dùng EHRI Current/Past Values để kiểm danh mục cùng khoảng hiệu lực. Duty Stations là danh sách đang công bố.

[Manifest kiểm chứng](verified_codebook_manifest.csv) ghi trạng thái theo quan hệ. Lookup dẫn xuất từ Parquet chỉ dùng khảo sát code–label và phản biện với TV3, TV5. Để chuyển sang `VERIFIED`, đối chiếu bảng mã chính thức đúng kỳ, đo trùng khóa và orphan trên giá trị đủ điều kiện, ghi ngoại lệ và xác nhận với reviewer.

Audit tách NULL, chuỗi rỗng và REDACTED. Với khóa ghép, nếu thành phần có nhiều trạng thái thì phân loại theo thứ tự NULL → rỗng → REDACTED để mỗi bản ghi chỉ thuộc một nhóm. Các ô `orphan_rows` và `duplicate_ref_keys` để trống khi thiếu tập mã chính thức đúng kỳ. Chỉ số `derived_lookup_unmatched_rows` đo khả năng tra lookup dẫn xuất trong phạm vi ghi ở audit.
