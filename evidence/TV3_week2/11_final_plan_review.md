# Nhận xét cuối gói bàn giao TV3 G2

Ngày 23/11/2026, rà soát commit `9d60e1c3c5800cd84289c77e325a98d75e54043c` theo kế hoạch “Hoàn thiện gói bàn giao tuần 2 cho TV4 và TV5”. Đây là tự rà soát của TV3 trước khi đẩy bổ sung; kết luận QA độc lập vẫn thuộc TV5.

**Kết luận:** đã đáp ứng phạm vi triển khai của kế hoạch; lượt rà soát lại không phát hiện lỗi chặn bàn giao cho TV4/TV5. Không cần sửa thêm mã trong lượt này. Gói tiếp tục ở trạng thái REVIEW, mô hình PROPOSED chờ TV4 và tích hợp chờ TV4/TV5. Kết luận này chưa phải nghiệm thu G2.

| Yêu cầu trong kế hoạch | Kết quả và bằng chứng |
| --- | --- |
| TV4 nhận dump/checksum/restore/SQL/DAX | Đủ trong [README bàn giao](../../handoff/TV3_G2/README.md), liên kết tới dump, checksum, SQL và runbook tồn tại trong checkout sạch. Restore mới kiểm đúng năm bảng và ba KPI; xem [log kiểm lại](10_final_review_checks.txt). |
| Quan hệ Power BI đề xuất | README có sơ đồ bốn quan hệ Single từ `dim_month`/`dim_agency` tới cả hai Mart, hướng dẫn tắt đường lọc Month → Agency và Mart → Mart. Đã đối chiếu khóa với DDL; thực chạy Power BI chờ TV4. |
| Dimension slicer, tên query/DAX và Unknown | README ghi tên query tương ứng, slicer Dimension và tránh lọc tháng trực tiếp trên agency Dimension. SQL sau restore kiểm Unknown tháng 202504 = 206.687 / 1.591 / 1.936. |
| Giới hạn category/grain | README và [quyết định mô hình](../../docs/TV3_g2_model_decisions.md) ghi hai Mart hỗ trợ tháng/cơ quan; category cần grain bổ sung do TV4 thống nhất. |
| TV5 có hướng dẫn Windows/Python/venv/requirements/PostgreSQL/QA | [TV5_REPLAY.md](../../handoff/TV3_G2/TV5_REPLAY.md) có lệnh PowerShell, cấu hình riêng và database QA mới; ghi rõ quyền CREATEDB, kết nối postgres và xóa database tạm. Đã đọc lại lệnh; chưa thực thi trên Windows. |
| Nhận đúng ba Parquet tháng 04 và kiểm hash | TV5_REPLAY có bảng filename/version/bytes/SHA-256 theo inventory, lệnh đối chiếu manifest trước khi nạp và hai layout phẳng/theo family. Trình kiểm trực tiếp hiện tại xác minh cả ba file thật thành công. |
| Lệnh regression, Parquet–ODS và end-to-end | TV5_REPLAY có hai bộ source/model, bộ replay bổ sung, pipeline all, direct checker, SQL KPI và rerun. Ba regression được chạy lại trên checkout sạch và database tạm, đều đạt. |
| Checklist expected/actual và nơi lưu reviewer | TV5_REPLAY tạo expected-actual.csv trong `.qa/TV5_G2/<run>/`; giữ phần actual/status PENDING cho reviewer tự điền. `.qa/` được Git bỏ qua. |
| `--report-dir` tương thích mặc định | [Pipeline](../../etl/g2_pipeline.py) giữ mặc định reports; cả ba CSV có mặt trong thư mục QA riêng sau kiểm lại, checksum của 20 báo cáo bàn giao giữ nguyên. |
| Ưu tiên CLI → dotenv → mặc định | Pipeline và direct checker dùng cùng resolve_config; bộ replay kiểm cấu hình và thực chạy các CLI trên database/nguồn fixture riêng, đều đạt. |
| J06 yêu cầu đúng một active/LOADED mỗi family | Regression kiểm 0/1/2 family FAIL, đủ 3 nhưng thiếu Fact/Mart hoặc sai KPI vẫn FAIL, đủ nguồn/lớp/đúng số mới SUCCESS. Audit FAIL và CSV coverage được kiểm trong test; nguồn inactive/REGISTERED không được tính. |
| Direct checker từ chối tháng/nguồn thiếu | Regression kiểm tháng sai, tháng không có inventory, thiếu/trùng family, thiếu file/hash sai; không có thông báo thành công. Mismatch vẫn bị chặn với Python -O. |
| Cập nhật trạng thái tài liệu | [README](../../README.md), [task board](../../docs/00_task_board.md) và [báo cáo tuần 2](../../reports/TV3_week2_summary.md) ghi REVIEW, PROPOSED chờ TV4 và tích hợp chờ TV4/TV5. |
| Kiểm checkout sạch và bằng chứng bản sửa | Checkout sạch của commit rà soát kiểm 239 đích liên kết Markdown nội bộ, chạy cả ba regression rồi vẫn sạch. [Bằng chứng triển khai](09_replay_hardening.txt) ghi lượt all mới/rerun với dữ liệu thật; SHA-256 ba file mã được đối chiếu lại và không đổi. [Log lượt nhận xét](10_final_review_checks.txt) lưu các kiểm mới riêng. |

Các lệnh regression có thể tái chạy từ gốc repo với Python trong venv và cấu hình PostgreSQL cục bộ:

```sh
.venv/bin/python tests/g2_source_checks.py --config configs/.env
.venv/bin/python tests/g2_model_checks.py --config configs/.env
.venv/bin/python tests/g2_replay_checks.py --config configs/.env
```

Lượt đọc dữ liệu thật hiện tại cho J06 **21 PASS + 3 PENDING DAX**, K01/K06/K07 = **2.271.969 / 7.153 / 24.088**. Source-direct giữ 43 Accessions và 61 Separations khác kỳ; các chỉ tiêu chất lượng so với ODS đều khớp. Bằng chứng end-to-end trước đó dùng đúng mã hiện tại; lượt rà soát này không chạy lại toàn bộ COPY/build khi mã không đổi.

Nhận xét về khả năng bàn giao: TV4 có thể bắt đầu restore và xây model theo đề xuất; TV5 có đủ hướng dẫn để replay vào môi trường riêng và ghi actual. Rủi ro còn lại nằm ở nhãn agency/category PARTIAL, nhóm Unknown cần review và các bước tích hợp chưa có xác nhận thực tế.

| Phần tiếp theo theo kế hoạch | Người phụ trách | Trạng thái |
| --- | --- | --- |
| PBIX, bus matrix, Dimension catalog, duyệt grain/relationship | TV4 | Chờ xác nhận |
| Bằng chứng restore/kết nối Power BI trên Windows | TV4 | Chờ thực chạy |
| Replay độc lập, SQL–DAX cùng bộ lọc và kết luận QA | TV5 phối hợp TV4 | Chờ xác nhận |
| Chốt nghiệm thu G2 | TV1 theo bằng chứng TV4/TV5 | Chờ tích hợp |

Sau lượt nhận xét đạt, commit phần nhận xét và log mới, đẩy đúng nhánh `tv3/g2-pipeline`, cập nhật PR nháp #43 và đối chiếu SHA từ xa. Không đánh dấu DONE/PASS thay TV4/TV5.
