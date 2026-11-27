# Bàn giao tuần 3 của TV3

**REVIEW phần kỹ thuật TV3; G3 chưa được nghiệm thu.** Đã nạp thật đủ 12 Parquet tháng 03–06/2025, build ba Fact và hai Mart theo grain tháng/cơ quan. Mô hình vẫn PROPOSED chờ TV4; Windows/PBIX/SQL–DAX và QA độc lập chờ TV4/TV5.

Nhánh `tv3/g3-full-pipeline` kế thừa G2 commit `3b30235`, PR G2 #43 chưa merge tại lúc tạo nhánh. [Runbook G3](../docs/TV3_week3_runbook.md), [quyết định mô hình](../docs/TV3_g3_model_review.md) và [sơ đồ](../diagrams/10_g3_full_pipeline.svg) ghi scope/dependency. Kế hoạch nguồn: Ke_hoach_Tuan_3_TV3_Nhom13.docx, phiên bản 1.0 ngày 23/11/2026.

| Task | Trạng thái | Sản phẩm thực chạy |
| --- | --- | --- |
| L3-10 | REVIEW | 12 file Source=Staging=ODS; [counts](week3/07_file_counts.csv), [audit](week3/07_load_log.csv), [before–after](week3/07_before_after.csv) |
| L3-11 | REVIEW thực thi; model PROPOSED | 3 Fact, khóa/FK/time roles, [catalog quan sát](week3/08_dimension_observed.csv), [quality checks](week3/09_quality_checks.csv) |
| L3-12 | REVIEW tháng/cơ quan | Workforce Mart 486 nhóm và flows Mart 340 nhóm đủ bốn kỳ; [KPI SQL](week3/05_kpi_monthly.csv); category/các chiều bổ sung chờ TV4 |
| L3-13 | REVIEW tự kiểm | [J06](week3/07_reconciliation.csv), [rerun May](week3/TV3_week3_rerun_results.csv), [failure tests](../evidence/TV3_week3/02_source_regression.txt); TV5 độc lập chờ xác nhận |

| Tháng | Employment | Accessions | Separations | K02 | K08 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 202503 | 2289192 | 4862 | 22061 | NULL | -17199 |
| 202504 | 2271969 | 7153 | 24088 | -17223 | -16935 |
| 202505 | 2255056 | 8813 | 26415 | -16913 | -17602 |
| 202506 | 2241780 | 9954 | 19947 | -13276 | -9993 |

Tổng dòng Fact: Employment 9,057,997; Accessions 30,782; Separations 92,511. Tổng 9,181,290 bản ghi qua các kỳ, không phải số người duy nhất.

**Kiểm chứng:** 84 J06 PASS + 12 DAX PENDING; 152 kiểm raw/ODS, ordinal, time role và FK PASS. Giữ 593 event khác kỳ (269 Accessions, 324 Separations), riêng May 107. PK/UNIQUE/FK đều validated; lookup không nhân/mất dòng. [Chất lượng theo file và Unknown](week3/09_source_quality.csv) ghi số thực đo.

**Rerun May thật:** ba file được J00 kiểm lại, sáu J01/J02 SKIPPED, J03–J05 rebuild May rồi J06 đủ bốn kỳ. Cả 15 bảng có cùng count/digest trước–sau, gồm stable Dim keys và Fact/Mart mọi tháng; source identity toàn baseline giữ nguyên. Audit được thêm run mới. Mã/cột/thứ tự digest ghi trong runbook. Không gọi nhánh skip là đã thử replacement.

Dimension thực đo: dw.dim_month = 9 dòng, dw.dim_agency = 493 dòng, dw.dim_action_category = 53 dòng. Unknown key=0; nhãn dẫn xuất PARTIAL. Các tháng hiệu lực ngoài bốn kỳ vẫn có Dimension; không cắt event.

**Bàn giao TV4:** [workforce_g3.dump](../handoff/TV3_G3/workforce_g3.dump), [SHA-256](../handoff/TV3_G3/workforce_g3.dump.sha256) và [lệnh restore](../handoff/TV3_G3/README.md) đã có trong repo; ba Dimension và hai Mart; [bằng chứng chuyển/restore](../evidence/TV3_week3/06_transfer_restore.txt) ghi SHA-256, 9/493/53/486/340 dòng và KPI cả bốn kỳ. Đã so toàn bộ nội dung bảng sau restore trên PostgreSQL 18 cùng máy; Windows và Power BI chưa chạy. Raw/config và dump cục bộ không commit; ngoại lệ đúng bản aggregate G3 đã kiểm trong handoff/TV3_G3/.

**Kiểm thử lỗi:** fixture QA kiểm file thiếu, checksum/version/hash thay dưới cùng tên, schema không hỗ trợ, lỗi COPY giữa transaction, rollback và audit FAIL; model chặn count != 1 và giữ Mart cũ. Test mới phát hiện thay đổi trường nghiệp vụ dù tổng không đổi. Không sửa raw thật; replacement thành công với file republish thật NOT_TESTED.

Giữ nguyên byte của 20 báo cáo G2. CSV G3 ở reports/week3; QA riêng dùng --report-dir .qa/TV5_G3/<run>. [Run manifest](week3/run_manifest.json) ghi code/inventory SHA-256 và thời gian; lượt full chạy trên working tree có hash mã chính xác để đối chiếu commit sau.

**Nhận xét:** phần TV3 có đủ dữ liệu, code, log, SQL và lệnh replay để gửi review. Chưa có căn cứ ghi G3 DONE/PASS: TV4 còn duyệt catalog/grain/nhận Mart và TV5 còn kết luận độc lập. Chi tiết và owner trong [danh sách còn mở](TV3_week3_open_items.csv). Các ID G3-Dxx là mục theo dõi nội bộ, không phải số issue GitHub.

[Nhận xét lại theo từng mục kế hoạch](../evidence/TV3_week3/10_final_review.md) đối chiếu T01–T09, L3-10…13, H07 và các giới hạn còn mở trước khi đẩy repo.

Tracker L3-10…13 và H07 chỉ chuyển REVIEW; 100% là tự báo phần kỹ thuật đã nộp, kết quả review vẫn CHUA_REVIEW và nghiệm thu vẫn 0. TV1 điền lịch/chốt G3. [Hồ sơ bằng chứng](../evidence/TV3_week3/) có regression, full run, SQL và restore; người nhận tự ghi actual và phạm vi đã chạy, không chép kết luận TV3 thành QA độc lập.
