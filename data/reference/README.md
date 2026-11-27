# Nguồn định nghĩa và bảng mã TV2

[Reference manifest](reference_manifest.csv) ghi URL, ngày truy cập, phạm vi và vị trí tra cứu. [FWD Data Dictionary](https://data.opm.gov/FWD%20Data%20Dictionary.xlsx) là workbook công khai của OPM. Sheet1 cung cấp định nghĩa, ví dụ và họ áp dụng. Dùng EHRI Current/Past Values để kiểm danh mục cùng khoảng hiệu lực. Duty Stations là danh sách đang công bố.

[Manifest kiểm chứng](verified_codebook_manifest.csv) ghi trạng thái theo quan hệ. Lookup dẫn xuất từ Parquet dùng để khảo sát code–label với TV3 và TV5. Chỉ đặt FK sau khi kiểm đủ bảng mã đúng kỳ, khóa trùng, orphan và số dòng sau lookup.

## Bảng mã OPM dùng cho G2

[Bảng mã theo kỳ](opm_lookup_g2.csv) lưu mã, nhãn, ngày hiệu lực và nguồn. Hai tab [Agency/Subelement Current/Past Values](https://data.opm.gov/data-standards/agency-subelement) được đọc ngày 21/11/2026. Số dòng thu được khớp bộ đếm của OPM, gồm 802 Current Values và 2.931 Past Values. Sau khi lọc khoảng hiệu lực giao với 03–06/2025, còn 751 dòng Subelement bốn ký tự và 31 dòng mã hai ký tự. `COMPLETE` áp dụng cho miền mã Subelement bốn ký tự theo EHRI. Tập mã hai ký tự vẫn ở `SAMPLE` vì phạm vi Agency cấp cao của FWD rộng hơn.

Bản công bố FedScope 04/2024–03/2025 có 5 cặp mã–nhãn Accessions và 9 cặp Separations. Các nhãn này khớp mọi giá trị quan sát được trong 30.782 Accessions và 92.511 Separations của baseline khi bỏ khoảng trắng đầu/cuối và so không phân biệt hoa thường. Bản công bố này ghi nhận mã đã xuất hiện đến 03/2025, nên kết quả dùng phạm vi `SAMPLE`. [Accessions](https://www.opm.gov/data/datasets/Files/761/6124a377-5e92-43e7-ade2-3be674580bc7.zip) · [Separations](https://www.opm.gov/data/datasets/Files/763/1e0ad2cd-40ee-4646-9daa-58b762bcddfb.zip)

Audit tách NULL, chuỗi rỗng sau TRIM và REDACTED sau TRIM và so không phân biệt hoa thường. Với khóa ghép, thứ tự phân loại là NULL → rỗng → REDACTED. Giá trị gốc, gồm số 0 đầu mã, được giữ để so khớp chính xác.

Các phép đối chiếu chạy theo từng file. Audit dùng cuối tháng báo cáo để xét ngày hiệu lực theo cả hai đầu. Event vẫn giữ tháng hiệu lực riêng. Với `SAMPLE`, các trường `reference_*` chỉ đo phạm vi mã đã xác định. `reference_left_join_rows` cho biết số dòng LEFT JOIN trước khi lọc khóa trùng. `orphan_rows` và `duplicate_ref_keys` để trống khi thiếu bộ mã đầy đủ. K10 để trống với phạm vi chưa xác minh hoặc mẫu số bằng 0.

## Bàn giao TV3 và kiểm lại

[Lookup theo kỳ](derived_lookup_g2.csv) là bảng `DERIVED_LOOKUP` từ nhãn quan sát trong Parquet. Khi nạp, lọc `load_status = 'READY'` và đặt khóa chính `(relation, report_month, code)`. LEFT JOIN theo cả ba thành phần. Dòng tra không khớp giữ nguyên mã gốc và được ghi vào Unknown/DQ. Khóa có một nhãn Parquet khác EHRI được giữ riêng ở `REVIEW` với lý do `EHRI_LABEL_DIFFERENCE`. Khóa lỗi hoặc có nhiều nhãn giữ trạng thái `UNKNOWN`. TV3 và TV5 đối chiếu `observed_labels` với `ehri_label` trước khi chốt nhãn Dimension. Cột `label` để trống cho cả hai nhóm này.

**Cập nhật 27/11/2026 (TV1, tích hợp G3):** pipeline nạp thêm kết quả duyệt nhãn của TV2 ([`ehri_label_review_131.csv`](../../evidence/TV2_week2/ehri_label_review_131.csv)) vào `ref.label_review`.
- **Được dùng:** khóa `REVIEW` mà TV2 kết luận chỉ khác cách viết (`ABBREVIATION`, `FORMATTING`, `TEXT_VARIANT`, `DOCUMENTED_RENAME`, `APOSTROPHE_REPAIR`). Nhãn hiển thị lấy từ `proposed_display_label`, `verification_status = 'REVIEWED_TV2'`.
- **Vẫn ở Unknown:** khóa `HOLD_ORG_SCOPE`, khóa `UNKNOWN` và khóa chưa được duyệt.
- **Lý do:** trước đây 28 khóa–tháng Agency ở trạng thái `REVIEW` (TR, IN, NN, HU, FQ, AH, HB) bị đưa toàn bộ vào Unknown. Các mã này chiếm toàn bộ dòng Agency Unknown của bốn kỳ.

Trong 2.657 khóa–tháng, DuckDB nạp thử được 2.521 khóa `READY`. Có 131 khóa–tháng `REVIEW`, gồm 103 Subelement và 28 Agency. Có 5 khóa–tháng `UNKNOWN`, gồm mã `HU**` qua bốn tháng và một khóa–tháng có nhiều nhãn. LEFT JOIN Agency và Subelement giữ đủ 9.181.290 dòng trên 12 file. Audit theo danh mục EHRI xác định 1.339 bản ghi `HU**` thiếu khóa hoạt động và 0 khóa tham chiếu trùng tại cuối mỗi tháng. [Audit khóa](../../docs/04_relationship_audit.csv) · [Ngoại lệ khóa](../../evidence/TV2_week2/relationship_exceptions.csv)

Chạy `python -B evidence/TV2_week2/audit_relationships.py <raw>` để tái tạo audit và lookup. Để tái tạo danh mục OPM theo kỳ, tải hai ZIP FedScope ở trên và chạy `python -B evidence/TV2_week2/prepare_opm_lookup.py accessions.zip separations.zip` từ thư mục gốc. Script lấy hai CSV gốc từ [bản chụp EHRI ngày 21/11/2026](source/ehri_agency_subelement_20261121.zip), kiểm SHA-256 của từng CSV trước khi ghi phạm vi `COMPLETE` và kiểm SHA-256 của hai ZIP FedScope. Có thể dùng `--agency-tables current.csv past.csv` với hai CSV có cùng SHA-256.
