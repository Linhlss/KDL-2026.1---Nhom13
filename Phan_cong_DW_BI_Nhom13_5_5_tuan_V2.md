# PHÂN CÔNG CÔNG VIỆC CHI TIẾT — NHÓM 13 (5 NGƯỜI / 5,5 TUẦN)

**Môn:** Kho dữ liệu và Kinh doanh thông minh (MI4214)  
**Đề tài:** Xây dựng kho dữ liệu và hệ thống Business Intelligence hỗ trợ phân tích quy mô, cơ cấu và biến động nhân sự tại các cơ quan liên bang Hoa Kỳ  
**Dữ liệu:** 12 Parquet OPM/EHRI (Employment, Accessions, Separations), 03–06/2025, ~301,5 MB, 9.181.290 bản ghi qua nhiều kỳ  
**Thời gian:** 5 tuần + khoảng 3–4 ngày (tổng ~38–39 ngày), **T1** là tuần đầu tiên nhóm bắt đầu thực hiện  
**Mục tiêu nội bộ:** Chuẩn bị minh chứng đủ mạnh để phấn đấu **4,5–5/5** ở **mỗi** tiêu chí C01–C11. Đây **không phải** mức điểm được giảng viên bảo đảm.  
**Sườn nội dung chính:** `De_cuong_DW_BI_Nhom13_Ke_hoach_5_5_tuan.md` (giữ nguyên làm nguồn yêu cầu; tài liệu này là bảng điều hành & phân việc).  
**Tình trạng:** Bản phân công v1 — thay `TV1` … `TV5` bằng tên, xác nhận thời gian rảnh và chốt trong buổi họp đầu tiên.

> **Phân biệt nguồn gốc yêu cầu:** **[GV]** là nội dung có trong workbook hướng dẫn môn học; **[NB]** là chuẩn bổ sung do nhóm tự đặt để hướng đến điểm cao. Tên file, số testcase, hạn chót nội bộ, số giờ và lựa chọn công cụ là **[NB]**, không phải định mức giáo viên bắt buộc.

---

## A. HƯỚNG DẪN SỬ DỤNG TÀI LIỆU

1. **Chốt sườn:** Không thay đổi mục tiêu/11 tiêu chí trong đề cương chính chỉ bằng lời nói. Mọi thay đổi thiết kế phải cập nhật `docs/change_log.md` và thông báo cho người phụ thuộc.
2. **Thay tên:** Điền tên và phương tiện liên lạc của 5 người ở bảng B. Một người chỉ có **một vai trò chính**, nhưng ai cũng phải hiểu toàn bộ luồng `Parquet → Staging → DW → Data Mart → Power BI`.
3. **Mỗi tác vụ có trạng thái:** `TODO / DOING / REVIEW / DONE / BLOCKED`; chỉ chuyển `DONE` khi đạt đủ định nghĩa hoàn thành ở mục G.
4. **Đo bằng sản phẩm:** Commit code/diagram/ảnh/bảng đối soát và ghi đường dẫn vào issue; không báo “xong” vì đã đọc tài liệu hoặc viết xong lý thuyết.
5. **Lịch họp:** 2 lần/tuần, mỗi lần 20–30 phút, và một phiên kiểm thử chéo cuối mỗi tuần; không cần họp cả nhóm liên tục để làm các việc độc lập.
6. **Quy tắc thời gian:** Mọi mục **P0** cần có trước cuối T4; **T5 là hoàn thiện, kiểm thử, công bố và báo cáo**, không dành để bắt đầu lại kiến trúc.

**Dự trù [NB]:** Mỗi người khoảng **10–15 giờ/tuần**, riêng người phụ trách ETL/BI có thể cần hơn trong T3/T4. Tổng sức nhóm tham khảo ~275–410 giờ trong 5,5 tuần; chỉ là dự toán lập kế hoạch, cần điều chỉnh sau buổi họp đầu. Nếu nhóm không đáp ứng được quỹ thời gian, cắt P2 trước rồi P1 ít giá trị, không tự cắt yêu cầu [GV].

---

## B. DANH SÁCH VAI TRÒ, TRÁCH NHIỆM VÀ NGƯỜI THAY THẾ

| Mã | Thành viên (điền tên) | Vai trò chính | Phạm vi chịu trách nhiệm cuối cùng | Backup/kiểm tra độc lập |
|---|---|---|---|---|
| **TV1** | **[Họ tên 1]** | **Trưởng nhóm / Business Analyst / Biên tập báo cáo** | C01–C02, KPI dictionary ở cấp nghiệp vụ, đồng bộ yêu cầu, bố cục báo cáo/slide, liên hệ giảng viên | **TV4** phản biện KPI; **TV5** kiểm form báo cáo |
| **TV2** | **[Họ tên 2]** | **Data Analyst / Source & EDA Engineer** | C03–C05: inventory, data profiling, ERD nguồn, mapping nguồn, EDA, chuẩn hóa dữ liệu đầu vào phối hợp ETL | **TV3** kiểm ERD/ingestion; **TV5** đối soát số liệu |
| **TV3** | **[Họ tên 3]** | **Data Warehouse / ETL Engineer** | C06–C07, triển khai DB Staging/DW/DM, nạp 12 file, Fact/Dimension vật lý, pipeline và logging | **TV2** hỗ trợ staging; **TV5** kiểm ETL, có bản hướng dẫn khôi phục |
| **TV4** | **[Họ tên 4]** | **BI / OLAP Developer** | C08–C10 (đồng chủ trì C08–C09 với TV3): bus matrix, KPI SQL/DAX, semantic model, ba dashboard, Publish to web | **TV1** nghiệm thu nghiệp vụ; **TV5** kiểm KPI, TV3 hỗ trợ mô hình |
| **TV5** | **[Họ tên 5]** | **QA / Performance / Release & Demo** | C11, bộ kiểm thử C01–C11, benchmark, đối soát SQL–DAX, issue board, tích hợp và gói bàn giao | **TV3** hỗ trợ performance; **TV1** kiểm biên tập & trình bày |

**Nguyên tắc cân bằng:** TV3 và TV4 có đường găng kỹ thuật; TV2 **phải** nhận phần staging/profiling đưa vào ETL, TV5 **phải** viết và chạy test cùng TV3/TV4 từ T2, không đẩy tất cả sang T5. TV1 chịu trách nhiệm biên tập, **không** phải một mình viết mọi chương; từng người bàn giao phần thuyết minh và hình minh chứng của chính mình.

### B1. Phân công theo đúng 11 ô chấm thầy dùng

| ID | Tiêu chí | Người chịu trách nhiệm (Owner) | Người review | Bằng chứng bắt buộc đưa vào hồ sơ |
|---|---|---|---|---|
| **C01** | Quy trình nghiệp vụ | TV1 | TV2 | Quy trình có điểm phân tích, cây nghiệp vụ, mô hình quản trị |
| **C02** | Requirement | TV1 | TV4 | Personas, FR/NFR, cây yêu cầu, 3 cây dashboard, KPI dictionary |
| **C03** | Hệ thống/quy mô dữ liệu | TV2 | TV5 | Inventory, nguồn/phiên bản, taxonomy, tần suất/cỡ kỳ dữ liệu |
| **C04** | ERD OLTP & Data flow | TV2 | TV3 | ERD nguồn/ODS minh họa có ghi chú, bảng kiểm chứng liên kết, mapping OLAP |
| **C05** | Data Exploration | TV2 | TV1 | Notebook chạy lại, missing/REDACTED, Pareto, phân bố và liên hệ |
| **C06** | Kiến trúc DW | TV3 | TV5 | Logical/physical architecture, luồng và công nghệ đúng với hệ thống chạy |
| **C07** | ETL | TV3 | TV2, TV5 | Pipeline, before–after, log, nạp lại không trùng, row reconciliation |
| **C08** | Data Dimension | **TV4 (thiết kế)** + **TV3 (DDL/nạp)** | TV2 | Catalog/grain/hierarchy, dữ liệu và row count mỗi Dimension |
| **C09** | Data Model OLAP | **TV4 (logic/semantic)** + **TV3 (vật lý)** | TV5 | 3 star schema/bus matrix, Staging/DW/DM logic + vật lý, KPI SQL |
| **C10** | Dashboard / BI | TV4 | TV1, TV5 | `.pbix`, 3 tình huống, slicer/drill/DAX, công bố, đối soát KPI |
| **C11** | Bài học + performance | TV5 | TV3, TV1 | Benchmark trước/sau, test results, hạn chế, lessons learned |

**Quyền quyết định kỹ thuật:** TV3 đề xuất schema, TV4 đề xuất tính KPI và BI; **TV1 + TV2 + TV3 + TV4** cùng duyệt *grain, ý nghĩa tháng, KPI dictionary* ở cuối T2; TV5 ký duyệt khi test nguồn và KPI không có lỗi nghiêm trọng. Không một người tự thay đổi mô hình đã khóa mà không thông báo.

---

## C. LỊCH CHUNG 5,5 TUẦN — CỔNG NGHIỆM THU

| Mốc | Hạn nội bộ | Kết quả bắt buộc | Người điều phối | Điều kiện qua cổng |
|---|---|---|---|---|
| **G0** | **Cuối T1 / ngày 7** | Xác minh 100M, khả năng dùng ERD/OLTP minh họa, Publish-to-web; kiểm kê nguồn, KPI v0, môi trường chạy | TV1 | Có câu trả lời của giảng viên **hoặc** blocker và phương án xử lý được ghi, không giả vờ đã được duyệt |
| **G1–G2** | **Cuối T2 / ngày 14** | C01–C05 v1; grain + KPI dictionary v1; ERD nguồn; **MVP 3 loại nguồn → Mart → 1 KPI Power BI** | TV1 + TV3 | Một KPI SQL và DAX khớp cho một tháng; source → DW truy vết được; thiết kế được khóa |
| **G3–G4** | **Cuối T3 / ngày 21** | Nạp đủ 12 Parquet; 3 Fact, Dimension, 2 Mart, job log; dữ liệu tháng 03–06 đối soát | TV3 + TV5 | Full load hoạt động, rerun 1 file/tháng không nhân đôi, số liệu nguồn–Fact–Mart đúng |
| **G5** | **Cuối T4 / ngày 28** | 3 dashboard v1, DAX + slicer/drill, 3 demo case, benchmark baseline, test SQL–DAX | TV4 + TV5 | D1–D3 dùng được và không có KPI sai khi lọc; không còn blocker DW/ETL |
| **G6** | **Cuối T5 / ngày 35** | Release candidate, benchmark tối ưu, public dashboard hoặc phương án được thầy duyệt, báo cáo/slide v1 cuối | TV5 + TV1 | Toàn bộ C01–C11 đủ evidence, lỗi nghiêm trọng đóng, freeze tính năng |
| **G7** | **0,5 tuần cuối / ngày 36–39** | Tổng duyệt 2 lần, đối soát bản nộp, phiếu đánh giá ký đủ và gói dự phòng | TV1 + TV5 | Demo 30–45 phút ổn định, cả 5 thành viên trả lời được phần việc và luồng tổng thể |

**Quy tắc chặn:** Nếu tới cuối T2 mà **MVP chưa chạy xuyên**, 1–2 ngày đầu T3 phải ưu tiên sửa MVP, **chưa** làm dashboard trang trí. Nếu T4 chưa có cả 3 dashboard v1 thì bỏ toàn bộ P2, giảm phần làm đẹp, chuyển người hỗ trợ TV4. Nếu T5 chưa public được vì quyền, chỉ dùng phương án thay thế **sau khi giảng viên đồng ý**.

---

## D. VIỆC CỤ THỂ CỦA TỪNG NGƯỜI THEO TUẦN

> Một **mã `TVx-Ty`** là một gói công việc của một người tại một tuần. Mỗi gói có checklist thực thi, đầu ra và tiêu chí nghiệm thu. Người review ở bảng B1 phải kiểm tra và để lại nhận xét trước khi đổi trạng thái `DONE`. Đường dẫn file là **đề xuất giao diện bàn giao**, có thể đổi nhất quán trước khi bắt đầu.

### D1. TV1 — Trưởng nhóm / Business Analyst / Biên tập

#### T1 — Khóa mục tiêu, bài toán và yêu cầu giảng viên (`TV1-T1`)
> **Nhận xét thầy bổ sung:** chuẩn bị bảng **điểm phân tích A# ↔ từng bước nghiệp vụ ↔ KPI ↔ chiều phân tích ↔ Fact/Dim ↔ dashboard**, thống nhất với TV2; mỗi touchpoint phải có nguồn thực.

- [ ] Gửi thầy 3 câu hỏi: **“100M” là MB hay số bản ghi?**, chấp nhận **ERD nguồn/ODS minh họa** hay yêu cầu OLTP gốc?, cách **public Power BI** hợp lệ; xin xác nhận bản hướng dẫn hiện áp dụng.
- [ ] Viết phạm vi dự án: 4 tháng, 3 nhóm dữ liệu, 3 chủ điểm (D1 quy mô/cơ cấu; D2 accessions/separations; D3 biến động/OLAP); rõ **không nghiên cứu HR cá nhân, không dự báo dài hạn**.
- [ ] Xác định 2–3 nhóm người sử dụng BI **giả định của sản phẩm**, câu hỏi quản trị, dữ liệu nào trả lời được và chưa được.
- [ ] Tạo KPI dictionary v0 với TV2/TV4: công thức, grain, thời gian tính, nguồn, tính cộng dồn được hay không, cảnh báo.
- [ ] Mở `issue_board`, thống nhất quy tắc đặt tên, họp và chuẩn chụp minh chứng cùng TV5.

**Bàn giao:** `docs/scope_decisions.md`, `docs/01_business_scope.md` v0, `docs/02_requirements.md` v0, `docs/kpi_dictionary.csv` v0, biên bản hỏi thầy.  
**Đạt khi:** Từng KPI truy được tới trường dữ liệu nguồn theo TV2; các vấn đề chưa được thầy xác nhận phải ghi là **BLOCKED**, không ghi “đã duyệt”.  
**Phụ thuộc:** TV2 gửi danh sách trường / thời gian có thực; TV4 phản biện tính khả thi KPI.

#### T2 — Hoàn chỉnh C01–C02 và khóa Data Contract (`TV1-T2`)
- [ ] Vẽ sơ đồ luồng giám sát và báo cáo workforce (phân biệt quy trình đề xuất và những gì nguồn OPM chứng minh); đánh dấu điểm phân tích gắn Fact/KPI.
- [ ] Hoàn thiện cây nghiệp vụ, khung mô hình tạo giá trị khu vực công (không gán doanh thu giả), bảng touchpoint → KPI → dashboard.
- [ ] Hoàn thiện FR/NFR, cây yêu cầu chung và **ba cây dashboard D1–D3**.
- [ ] Họp chốt `grain`, `report_month vs effective_month`, conformed dims và dictionary cuối T2; ký duyệt nội bộ cùng TV2–TV5.
- [ ] Viết phần Requirement và khảo sát nghiệp vụ vào bản báo cáo từ T2, kèm hình và tài liệu tham khảo.

**Bàn giao:** `docs/01_business_scope.md`, `docs/02_requirements.md`, `docs/01_analysis_touchpoints.csv`, `diagrams/business_process.drawio`, `diagrams/business_tree.drawio`, `diagrams/requirement_tree.drawio`, `diagrams/dashboard_tree_D1_D2_D3.drawio`; `docs/kpi_dictionary.csv` v1.  
**Đạt khi:** C01–C02 có đủ hình/cây, bản định nghĩa KPI thống nhất với TV3/TV4; không có KPI ngoài phạm vi dữ liệu.

#### T3 — Xây nội dung báo cáo song song với triển khai (`TV1-T3`)
- [ ] Viết **Phần I — Tổng quan DW** và **Phần II — Tổng quan BI** ngắn gọn, có nguồn; liên hệ trực tiếp tới hệ thống nhóm 13.
- [ ] Biên tập các phần C01–C05 do TV1/TV2 bàn giao vào **Phần III — Ứng dụng HR**; thống nhất thuật ngữ, màu/label hình và đánh số.
- [ ] Viết khung **3 tình huống BI thực tế**; chưa điền kết luận số liệu khi chưa có kết quả SQL/DAX kiểm chứng.
- [ ] Thử trình bày 5–7 phút phần nghiệp vụ + requirement cho TV2/TV5 chất vấn.

**Bàn giao:** `deliverables/report_draft` (phần I, II, III.1–III.4), `docs/bi_use_cases.md` v0, danh mục tài liệu tham khảo.  
**Đạt khi:** Có bản thảo hữu hình, không để đến T5 mới viết; tất cả hình/số liệu có đường dẫn nguồn.

#### T4 — Nghiệm thu ý nghĩa dashboard (`TV1-T4`)
> **Nhận xét thầy bổ sung:** review **3 câu chuyện phân tích** của D1–D3 (bối cảnh → bằng chứng trên chart → insight → đề xuất); không duyệt dashboard chỉ vì đã có hình và slicer.

- [ ] Cùng TV4 soát dashboard D1–D3: mỗi trang có **câu hỏi quản trị → KPI → thao tác lọc → kết luận thận trọng**.
- [ ] Cùng TV5 kiểm tra **không** cộng bốn tháng Employment thành headcount duy nhất, không gọi chênh lệch headcount là `accessions − separations`, không khẳng định nguyên nhân/vì sao khi nguồn không hỗ trợ.
- [ ] Soạn slide v0 theo đúng 11 tiêu chí, ưu tiên ảnh ETL/ERD/DW/BI thực; phân bổ thời gian 30–45 phút.
- [ ] Ghép phần III.5–III.9 từ TV3/TV4 thành báo cáo v1; lập danh mục mục thiếu minh chứng.

**Bàn giao:** `deliverables/report_v1`, `deliverables/slides_v0`, `docs/bi_use_cases.md` v1, `docs/missing_evidence.md`.  
**Đạt khi:** Ba tình huống có đường dẫn KPI test; không còn mục báo cáo chỉ có hình minh họa mà không có bằng chứng.

#### T5 — Biên tập kết quả cuối và bảo vệ (`TV1-T5`)
- [ ] Chuẩn hóa **báo cáo nhóm** theo [GV]: **Phần I DW / Phần II BI / Phần III ứng dụng**, có mục lục, kết luận, nguồn, số trang, **Times New Roman 12, căn đều hai bên**, chính tả.
- [ ] Đảm bảo các hình cần thiết: quy trình, Canvas/quản trị, taxonomy, ERD/mapping, EDA, kiến trúc có công nghệ, ETL before–after, Dimension, OLAP, dashboard.
- [ ] Viết kết luận, hạn chế, bài học (TV5 cung cấp benchmark và bài học kỹ thuật), biên soạn slide phiên bản nộp.
- [ ] Lập danh sách câu hỏi thầy có thể hỏi cho 11 tiêu chí; mỗi thành viên có câu trả lời cho phần của mình và 3 câu hỏi liên nhóm.

**Bàn giao:** `deliverables/Group13_Final_Report.*`, `deliverables/Group13_Presentation.*`, `docs/defense_QA.md` v1.  
**Đạt khi:** Báo cáo và slide khớp hệ thống đang chạy, không khẳng định công nghệ/công bố chưa thực hiện.

#### 0,5 tuần cuối — Tổng duyệt, bàn giao (`TV1-T5H`)
- [ ] Điều phối **2 lần thuyết trình thử 30–45 phút**, điều chỉnh tốc độ và chuyển lượt 5 người.
- [ ] Kiểm tra danh sách thành viên, **bảng đánh giá đóng góp 1–5 có tối thiểu 4 mức điểm phân biệt và đủ 5 chữ ký** theo mẫu [GV].
- [ ] Chốt mọi file nộp, rà số liệu cuối cùng với TV5 và đường dẫn công bố/ảnh dự phòng.

**Bàn giao:** biên bản tổng duyệt, báo cáo/slide cuối, bảng đánh giá thành viên có chữ ký.  
**Đạt khi:** Không vượt thời gian, không có mâu thuẫn giữa slide–báo cáo–dashboard.

---

### D2. TV2 — Data Analyst / Source & EDA Engineer

#### T1 — Inventory, profiling ban đầu (`TV2-T1`)
> **Nhận xét thầy bổ sung:** taxonomy phải có **ví dụ hàng dữ liệu nguồn**; từ điển có `meaning/source/verified_by`, TV1/TV5 duyệt độ chính xác.

- [ ] Giải nén/đọc metadata của **đúng 12 Parquet**, kiểm file, tháng, schema, size, số dòng; kiểm chứng tổng bằng code từ nguồn.
- [ ] Tra codebook/nguồn của OPM/EHRI; phân biệt field code với nhãn, `REDACTED` với NULL; lưu provenance/version và checksum nếu có thể.
- [ ] Lập Data Dictionary/Taxonomy v0, nhóm các chiều khả thi theo Agency, Occupation, Grade, Location, Time.
- [ ] Kiểm tra sample schema và `grain` bằng dữ liệu thật; trả TV1 các KPI có thể tính **và những KPI không thể tính**.
- [ ] Hỗ trợ TV3 thử đọc 1 Employment + 1 Accessions + 1 Separations Parquet vào staging.

**Bàn giao:** `reports/source_inventory.csv`, `docs/03_source_system.md` v0, `docs/source_data_dictionary.csv` v0, `data/README_sources.md`, notebook hoặc script thống kê nguồn.  
**Đạt khi:** Mỗi số bản ghi/dung lượng có kết quả đọc thực; không dùng “9,18 triệu nhân viên” thay “9,18 triệu bản ghi qua kỳ”.

#### T2 — EDA, ERD nguồn và mapping (`TV2-T2`)
> **Nhận xét thầy bổ sung:** chuẩn bị **bảng chéo 2 biến phân loại + Cramér’s V hoặc chỉ số hiệu ứng phù hợp**, giải thích vì sao không Pearson trên mã. Phân tích MoM 4 tháng và nêu lý do **không đủ dữ liệu kết luận mùa vụ**; đặt Flow nguồn→OLAP cạnh ERD trong phần phân tích.

- [ ] Hoàn chỉnh EDA **null, REDACTED, giá trị lạ, distribution, Pareto, thống kê, bảng liên hệ Dimension–Dimension / Dimension–Fact**, so sánh 4 kỳ; có kết luận và giới hạn.
- [ ] Xác minh lại từ dữ liệu gốc số trường hợp `report_month` khác `effective_month` (con số 593 trong tóm tắt là **sơ bộ**).
- [ ] Vẽ **ERD lớp nguồn/ODS** và ma trận quan hệ: khóa nào được chứng minh, quan hệ nào chỉ là **thiết kế phục vụ phân tích**, không có `employee_id` xuyên Fact.
- [ ] Tạo **source-to-target mapping** cho từng field cần vào Dimension/Fact; đưa ra quy tắc chuẩn hóa, giá trị Unknown và dữ liệu che.
- [ ] Chốt với TV1/TV3/TV4: khóa tự nhiên, tháng nguồn/tháng hiệu lực, địa lý/cấp bậc có hierarchy thật đến đâu.

**Bàn giao:** `notebooks/01_eda.ipynb`, `reports/data_quality.md`, `reports/eda_charts/`, `docs/04_source_erd.md`, `diagrams/source_ods_erd.drawio`, `docs/source_to_target_mapping.csv`, `docs/05_eda_summary.md`.  
**Đạt khi:** Có thống kê/biểu đồ tính trực tiếp từ file, ít nhất một Pareto và hai phân tích liên hệ có ý nghĩa; ERD không bịa quan hệ cá nhân.

#### T3 — Staging & Data Quality vào ETL (`TV2-T3`)
- [ ] Cùng TV3 hiện thực `job_01_stage` và/hoặc `job_02_validate_clean` theo mapping, không tự ý xóa bản ghi sự kiện giống thuộc tính.
- [ ] Thực hiện 4 **before–after** từ bản ghi gốc có thật: ví dụ giá trị mã, parse tháng, `REDACTED`, category; ghi dữ liệu nguồn và đầu ra sau staging.
- [ ] Đối chiếu số bản ghi theo 12 file và tháng trước/sau staging; liệt kê unmatched codes và giá trị Unknown vào Dims.
- [ ] Gửi catalogue chiều chuẩn hóa cho TV3/TV4: attribute, natural key, hierarchy, mô tả codebook và row count kỳ vọng.

**Bàn giao:** `etl/job_01_stage.py`/`etl/job_02_validate_clean.py` (phần do TV2 sở hữu), `docs/07_etl_before_after.md`, `reports/data_quality_v2.md`, `docs/dimension_catalog.csv` v0.  
**Đạt khi:** TV3 chạy được job chỉ dựa vào README; các quy tắc làm sạch có test hoặc query chứng minh không làm mất/nhân bản dòng.

#### T4 — Kiểm tra insight và sửa EDA theo DW thực (`TV2-T4`)
- [ ] Đối soát lại EDA so với DW/Fact cho 3–5 KPI đã khóa, bao gồm theo tháng/cơ quan/nghề nghiệp.
- [ ] Xem xét sự thay đổi phân bố khi đổi kỳ báo cáo ↔ kỳ hiệu lực trong D2; ghi hướng xử lý và phần nào không so sánh được.
- [ ] Viết lời thuyết minh C03–C05 ngắn, 3–5 hình chính dễ đọc để đưa slide; tập trung **bài học dữ liệu → tác động thiết kế**.
- [ ] Review các hàng tương ứng trong Power BI với TV4, không chấp nhận visual dùng category/label chưa được kiểm chứng.

**Bàn giao:** `docs/03_source_system.md`, `docs/05_eda_summary.md`, hình EDA đã kiểm tra, `reports/eda_to_dw_validation.csv`.  
**Đạt khi:** Bảng/phân bố trên slide khớp số liệu nguồn; không nhầm biến mã phân loại thành số đo tương quan Pearson.

#### T5 — Phụ lục nguồn, hỗ trợ khôi phục & vấn đáp (`TV2-T5`)
- [ ] Chốt từ điển nguồn, mã hóa giá trị, Data Taxonomy, ERD, mapping và phụ lục kết quả EDA.
- [ ] Kiểm tra tất cả ví dụ before–after thực sự tồn tại trong file gốc; ghi file, tháng và cách truy vết nhưng không lộ thông tin không nên công khai.
- [ ] Tập trả lời câu hỏi C03–C05, hỗ trợ TV3 nếu cần chạy lại staging từ nguồn mới/thiếu file.

**Bàn giao:** phần III.2–III.4 và phụ lục có thể copy vào báo cáo; `evidence/source/`, `evidence/eda/`.  
**Đạt khi:** Người khác chạy notebook tái lập được bảng số liệu then chốt.

#### 0,5 tuần cuối — Phản biện số liệu (`TV2-T5H`)
- [ ] Review ngẫu nhiên 5 số liệu xuất hiện trong slide và truy ngược về query/notebook nguồn.
- [ ] Tham gia hai buổi tổng duyệt; chuẩn bị mở nhanh ERD/source mapping khi thầy hỏi.

---

### D3. TV3 — Data Warehouse / ETL Engineer

#### T1 — Môi trường DB & smoke test (`TV3-T1`)
- [ ] Khởi tạo repo, thư mục ETL/SQL, thiết lập PostgreSQL (local/container) và quyền DB; lưu cấu hình mẫu **không chứa mật khẩu thật**.
- [ ] Tạo script tạo schema `staging`, `dw`, `mart`, `audit`; bảng metadata `source_file`/`load_run`.
- [ ] Thử đọc 3 file đại diện bằng Python/DuckDB tùy công cụ, tạo bảng nhỏ và kiểm query SQL mẫu.
- [ ] Đo thử chi phí đọc Parquet → DB để chọn batch/chunk hợp lý; không tối ưu quá sớm.

**Bàn giao:** `README.md` phần setup, `configs/example.env`, `sql/01_create_schemas.sql`, `etl/job_00_inventory.py` bản đầu, ảnh DB smoke-test.  
**Đạt khi:** TV2/TV5 làm theo README dựng được DB và đọc dữ liệu có thực.

#### T2 — Khóa kiến trúc/DDL, dựng MVP xuyên hệ thống (`TV3-T2`)
> **Nhận xét thầy bổ sung:** logo công nghệ đặt vào **đúng tầng chạy thực tế**, có bảng mapping tool→job→file/schema; không đưa logo Spark/Kafka/AI nếu nhóm không triển khai.

- [ ] Vẽ logical và physical architecture thể hiện **Source → Staging/ODS → DW → Data Mart → Power BI**, công nghệ đúng với code sử dụng; có metadata/audit.
- [ ] Chốt grain từng Fact với TV2/TV4; thiết kế Dimension keys, conformed dimensions; DDL `dw` và `mart` phiên bản đầu.
- [ ] Cùng TV2 tạo **MVP**: từ 3 file đại diện → Staging → mỗi Fact mẫu → Dimension cần thiết → một Mart/SQL KPI → Power BI.
- [ ] So sánh số liệu source/staging/DW/Mart cho một tháng; ghi execution logs và kế hoạch nạp đủ 12 file.
- [ ] Xác nhận vật lý rõ ràng: `raw_meta`/`staging`/`dw`/`mart` có bảng/view/truy vấn thực; không chỉ nạp CSV trực tiếp Power BI rồi gọi là DW.

**Bàn giao:** `diagrams/warehouse_architecture.drawio`, `diagrams/physical_deployment.drawio`, `diagrams/dw_logical.drawio`, `sql/03_dw_ddl.sql` v1, `sql/04_marts.sql` v1, `docs/06_architecture_decisions.md`, log chạy MVP.  
**Đạt khi:** TV4 xác nhận Power BI đọc được ít nhất 1 KPI từ Mart và TV5 xác nhận source = SQL.

#### T3 — Full ETL 12 file + DW & Data Mart (`TV3-T3`)
- [ ] Hoàn thiện `job_03_build_dimensions`, `job_04_build_facts`, `job_05_build_marts`, `job_06_audit_reconcile`, ghép job_01/02 từ TV2.
- [ ] Nạp 03 → 04 → 05 → 06/2025; tạo **3 Fact**, Dimension đã chốt và **ít nhất 2 Mart SQL thực**.
- [ ] Giữ đủ `report_month` và `effective_month` cho dòng sự kiện khi nguồn có; `REDACTED` thành trạng thái che/NULL hợp lệ, không 0.
- [ ] Chạy lại tháng 05 và kiểm không bị tăng bản ghi/KPI; không `DISTINCT` vô điều kiện trên sự kiện.
- [ ] Sinh log batch, mapping các khóa Dimension, bảng đối soát theo loại/tháng; kiểm tra query Fact và Mart trên toàn bộ data.

**Bàn giao:** `etl/`, `sql/`, `logs/etl_run_summary.csv`, `reports/etl_reconciliation.csv`, SQL DDL cuối, `evidence/etl/`.  
**Đạt khi:** Có bằng chứng `full load 12/12`, log 4 kỳ, 3 Fact + 2 Mart chạy được, rerun idempotent, thống kê tháng không mất dòng ngoài quy tắc có giải thích.

#### T4 — Hỗ trợ BI, benchmark và đóng băng mô hình (`TV3-T4`)
- [ ] Đảm bảo view/tables Mart cung cấp đủ field cho D1–D3, tối ưu truy vấn khi benchmark cho thấy cần thiết.
- [ ] Cùng TV5 chạy benchmark có cùng điều kiện trước/sau (index hoặc pre-aggregation), lưu `EXPLAIN` và thời gian.
- [ ] Tạo **logical + physical** model Staging, DW và Mart, màu Fact/Dimension và grouping rõ như hướng dẫn [GV].
- [ ] Hoàn chỉnh DBA/ETL docs: chỉ dẫn full rebuild, incremental rerun, logs, backup/restore; khóa schema cuối T4 nếu test pass.

**Bàn giao:** `diagrams/staging_physical.drawio`, `diagrams/dw_physical.drawio`, `diagrams/marts_logical_physical.drawio`, `docs/07_etl_runbook.md`, `reports/etl_performance.csv`.  
**Đạt khi:** Một thành viên khác chạy lại thành công; không có KPI bị thay đổi vô cớ sau tối ưu.

#### T5 — Release & vận hành ổn định (`TV3-T5`)
- [ ] Sửa lỗi blocking P0/P1, đảm bảo SQL/migrations có thể tạo lại kho từ dữ liệu gốc.
- [ ] Cung cấp số bảng và số dòng từng Fact/Dim/Mart, dung lượng lưu trữ, thời gian ETL đo thực để đưa báo cáo.
- [ ] Chụp minh chứng DB thật, query, log và output; hỗ trợ chuyển môi trường demo (không để demo phụ thuộc một máy cá nhân).
- [ ] Review phần C06/C07/C08/C09 trong báo cáo, đối chiếu sơ đồ với DDL chạy thật.

**Bàn giao:** `docs/runbook.md`, `reports/table_row_counts.csv`, schema export/backup script, `evidence/architecture/`, `evidence/etl/`.  
**Đạt khi:** Code checkout + cấu hình + nguồn → chạy lại pipeline theo hướng dẫn; không còn nguồn dữ liệu giả.

#### 0,5 tuần cuối — Phụ trách demo pipeline/SQL (`TV3-T5H`)
- [ ] Demo live một bước ETL hoặc dùng log đã được xác minh, query Fact/Dim/Mart và giải thích mapping.
- [ ] Giữ bản backup schema/data và phương án phục hồi nếu DB/máy phát sinh lỗi khi trình bày.

---

### D4. TV4 — BI / OLAP Developer

#### T1 — Rà khả năng Power BI, thiết kế dashboard từ câu hỏi (`TV4-T1`)
- [ ] Xác nhận ai có Windows + **Power BI Desktop**; kiểm tra quyền dịch vụ, Publish to web hoặc ghi blocker; thực hiện công bố thử chỉ với dữ liệu **không nhạy cảm được phép** nếu cần.
- [ ] Cùng TV1 đề xuất layout ba dashboard, danh sách KPI và thao tác người dùng; không tạo DAX dựa vào headcount cộng chéo tháng.
- [ ] Lập `docs/10_dashboard_specs.md` v0: D1/D2/D3, KPIs, slicers, visuals, drill, câu hỏi, lưu ý month.
- [ ] Phản biện KPI v0/field availability với TV2: phân biệt snapshot headcount với event counts.

**Bàn giao:** `docs/10_dashboard_specs.md` v0, 3 wireframes, biên bản kiểm thử PBI/Publish-to-web.  
**Đạt khi:** Không có rủi ro kỹ thuật PBI bị bỏ quên đến T4.

#### T2 — OLAP logic & Power BI MVP (`TV4-T2`)
- [ ] Soạn **grain statement**, **bus matrix**, **logic star schema** 3 Fact, danh mục Dimension; xác nhận với TV2/TV3.
- [ ] Định nghĩa conformed dims, hierarchy theo Agency/Occupation/Location/Grade/Month **chỉ khi mapping có thực**.
- [ ] Kết nối Power BI đến Mart MVP từ TV3, dựng một visual + một KPI, có measure DAX đối chiếu SQL.
- [ ] Chốt tên KPI, date semantics, bảng/measure trong semantic model; lưu ảnh bản MVP trước cuối T2.

**Bàn giao:** `docs/09_bus_matrix.md`, `docs/08_dimensions.md` v0, `diagrams/dw_logical.drawio` (phối hợp TV3), `powerbi/Group13_Workforce_BI.pbix` MVP, `reports/kpi_mvp_reconciliation.csv`.  
**Đạt khi:** Một KPI lọc theo 1 tháng khớp SQL/Power BI; không join Fact-to-Fact qua dữ liệu không có ID.

#### T3 — Semantic Model, Dimension và DAX bản đầu (`TV4-T3`)
> **Nhận xét thầy bổ sung:** sơ đồ **nhóm Dimension theo lĩnh vực khái niệm**, kèm row count và 2–3 dòng dữ liệu thật mỗi bảng; chưa có hierarchy chính thức thì không nối mã bằng suy đoán.

- [ ] Dựng relationship trong Power BI từ các Dimension và Fact đã nạp đủ; không dùng relationship many-to-many/bi-directional nếu gây double count.
- [ ] Hoàn thiện Dimension Catalog cùng TV3: natural/surrogate key, count, mô tả, hierarchy, xử lý Unknown và Type 1 phù hợp.
- [ ] Viết DAX cho KPI lõi: headcount (kỳ được chọn), MoM difference/%, accessions, separations, số lượt chênh lệch (đặt tên tránh hiểu là thay đổi headcount), ranking agency.
- [ ] Tạo bản đầu D1/D2 trên full data, kiểm thử ít nhất vài bộ lọc với SQL, ghi thiếu field cho TV3 khắc phục.

**Bàn giao:** `.pbix` v0.5, `docs/08_dimensions.md` và `docs/dimension_catalog.csv`, `docs/dax_measure_catalog.md`, `reports/kpi_sql_dax_draft.csv`.  
**Đạt khi:** D1/D2 có KPI và một số visual làm việc trên DW/Mart thực; tất cả relationship được kiểm tra.

#### T4 — Hoàn thiện D1–D3 và công bố (`TV4-T4`)
> **Nhận xét thầy bổ sung:** định dạng dấu phân cách nghìn, đơn vị, số %, tooltip KPI; có ít nhất **2 trường hợp conditional formatting/alert DAX** và **3 story** diễn giải được số liệu thực. Không tự làm YoY/mùa vụ/forecast từ 4 tháng.

- [ ] D1: Workforce Overview; D2: Accessions & Separations; D3: Workforce Changes & OLAP — mỗi trang có KPI quan trọng, đủ visual phù hợp và slicer.
- [ ] Thêm thao tác **drill-down, roll-up, slice/dice, ít nhất một drill-through**, tooltip/last refresh/metric definition; conditional formatting có ngưỡng **minh họa được ghi rõ**.
- [ ] Kiểm SQL–DAX theo tháng và agency/occupation/grade với TV5; không đưa insight chưa kiểm chứng vào thuyết minh.
- [ ] Thử public bằng phương pháp hợp lệ, chỉ dùng aggregate phù hợp công khai. Lưu URL/ảnh thử trên trình duyệt không đăng nhập nếu được; nếu bị tenant chặn thì xin phép giảng viên cách xử lý, không tự coi ảnh là thay thế.
- [ ] Chốt ba kịch bản demo: filter → drill → đối chiếu → insight/giới hạn.

**Bàn giao:** `powerbi/Group13_Workforce_BI.pbix` v1, `docs/dashboard_test_cases.md`, `reports/dashboard_kpi_reconciliation.csv`, `evidence/dashboard/`, `docs/publication_status.md`.  
**Đạt khi:** Cả 3 dashboard chạy được trên máy demo, KPI không sai khi lọc, tính năng OLAP tương tác và tình trạng public rõ ràng.

#### T5 — Hoàn thiện hiệu năng/UX và tài liệu Power BI (`TV4-T5`)
- [ ] Sửa lỗi/kết quả sai trước khi làm đẹp; kiểm tra top-k, color/legend, layout ít rối, chú giải snapshot/event.
- [ ] Chốt tất cả KPI/công thức và kết luận sau khi TV5 ký xác nhận số liệu.
- [ ] Chụp ảnh D1–D3 có trường hợp lọc cụ thể, screenshot semantic model, ảnh công bố (nếu có), làm slide minh chứng BI.
- [ ] Đóng gói `.pbix`, dashboard guide và link public; tạo video demo dự phòng **không coi là public**.

**Bàn giao:** `.pbix` final, `docs/10_dashboard_specs.md`, `docs/bi_user_guide.md`, `evidence/dashboard/`, link công bố nếu được.  
**Đạt khi:** 3 tình huống có câu hỏi–insight–giới hạn rõ, người khác mở `.pbix` và refresh được.

#### 0,5 tuần cuối — Demo BI (`TV4-T5H`)
- [ ] Trình diễn D1–D3 theo script định giờ; có sẵn saved views/filters.
- [ ] Chuẩn bị 2 phương án: Power BI Desktop offline và link web nếu publish thành công.

---

### D5. TV5 — QA / Performance / Release & Demo

#### T1 — Test plan, quản lý issue và khung evidence (`TV5-T1`)
- [ ] Tạo repo/project board, quy tắc branch/PR và issue template; thêm checklist DoD và người review.
- [ ] Lập **test matrix C01–C11** và các test nguồn/ETL/KPI/dash/Publish; chuẩn bị log template và folder `evidence/C01`…`C11`.
- [ ] Ghi phần cứng/môi trường dự kiến benchmark, cách đo thời gian và dữ liệu test **thật**.
- [ ] Thử tái lập setup DB/Python từ README của TV3, báo blocker sớm.

**Bàn giao:** `docs/project_board.md`, `tests/test_plan.md`, `docs/evidence_index.md`, `reports/environment_baseline.md`, issue list.  
**Đạt khi:** Test case nào cũng có expected result/rule và vị trí lưu evidence; không dùng test data synthetic.

#### T2 — Kiểm MVP, khóa acceptance rules (`TV5-T2`)
> **Nhận xét thầy bổ sung:** thêm kiểm chứng **data dictionary & taxonomy**: ví dụ dữ liệu nguồn có tồn tại, ý nghĩa trường có dẫn nguồn, có reviewer và trạng thái `verified/uncertain`.

- [ ] Kiểm tra độc lập đúng 12 nguồn và tháng; so sánh schema/row counts từ notebook TV2 với SQL TV3.
- [ ] Viết/check test: source count, month snapshot, event month mismatch, unknown mapping, malformed source, `REDACTED`.
- [ ] Chạy end-to-end MVP cùng TV3/TV4: source → Staging → Fact/Dim → Mart → KPI SQL ↔ DAX cho 1 kỳ.
- [ ] Chuẩn hóa checklist nghiệm thu 11 tiêu chí theo điểm nhóm 6 và hướng dẫn thầy; yêu cầu đường dẫn ảnh/câu trả lời vấn đáp.

**Bàn giao:** `tests/source_data_checks.sql`, `tests/test_cases.md`, `reports/mvp_test_result.csv`, `docs/evidence_index.md` cập nhật.  
**Đạt khi:** Lỗi blocker của MVP có owner và deadline; không chốt grain khi KPI nguồn/SQL không khớp.

#### T3 — Đối soát full-load, test chạy lại (`TV5-T3`)
- [ ] Đối chiếu 12 Parquet và 3 nhóm nguồn ở từng tháng với Staging/Fact/Mart; phân biệt số dòng và headcount.
- [ ] Kiểm **idempotence** rerun kỳ 05; kiểm dữ liệu duplicate hợp lệ, null/Unknown dimension, `REDACTED`, report/effective month mismatch.
- [ ] Test fault handling: file bị thiếu hoặc schema lệch phải báo rõ, không âm thầm thành công; dùng file đầu vào gốc và kiểm tra điều kiện thiếu file, không cần dựng dữ liệu giả.
- [ ] Ghi bug list phân loại P0/P1/P2; chụp minh chứng kết quả chạy và số dòng DB.

**Bàn giao:** `reports/full_load_reconciliation.csv`, `reports/rerun_test.md`, `reports/defects.csv`, `evidence/etl/`, `tests/etl_*.sql`.  
**Đạt khi:** Không có lỗi P0 làm sai KPI và duplicate load; không mất dòng vô giải thích.

#### T4 — Benchmark và kiểm dashboard (`TV5-T4`)
> **Nhận xét thầy bổ sung:** checklist BI phải có **display units, thousand separator, alert DAX, story có SQL đối soát, giới hạn 4 tháng**. Lập 3 câu hỏi giả định thầy hỏi để TV1/TV2/TV4 cùng tập trả lời.

- [ ] Chọn ít nhất 1 truy vấn truy cập Fact lớn (theo tháng/cơ quan), so sánh với Mart/index phù hợp; đo **ít nhất 3 lần mỗi phương án**, cùng DB/máy/điều kiện.
- [ ] Lưu `EXPLAIN`, thời gian các lần, median và phần cứng; nếu tối ưu không hiệu quả, báo trung thực và thử một phương án hợp lý khác trong thời gian cho phép.
- [ ] Kiểm tra KPI/DAX theo 2 kỳ, agency và một chiều phân tích khác; thực hiện **tối thiểu 10 ca kiểm SQL ↔ DAX** theo đề cương chính.
- [ ] Kiểm các thao tác dashboard: slicer, drill, conditional format, tương tác, date semantics và quyền/trạng thái public.
- [ ] Đưa report QA cho TV3/TV4 sửa trong T4, không giữ bug đến T5.

**Bàn giao:** `reports/11_benchmarks.csv`, `reports/11_benchmark_notes.md`, `reports/dashboard_kpi_reconciliation.csv`, `tests/dashboard_checklist.md`, `evidence/performance/`.  
**Đạt khi:** Có một bảng kết quả benchmark thật, dashboard test pass, truy vấn không bị so sánh lệch phạm vi dữ liệu.

#### T5 — Chốt chất lượng, release, minh chứng và bài học (`TV5-T5`)
- [ ] Chạy **regression tests** sau các thay đổi ETL/DAX; đối soát lại C01–C11 với từng owner và reviewer.
- [ ] Tổng hợp **Problem → Evidence → Decision → Test → Result**: grain/employee_id, kỳ thời gian, REDACTED, query performance và xuất bản.
- [ ] Đóng gói repo/data provenance, runbook, schema/DB backup, `.pbix`, báo cáo, slide, dữ liệu đối soát và evidence index.
- [ ] Rà tất cả URL/ảnh đã chứng minh từng tính năng, tạo `README` chạy lại và thứ tự demo; phối hợp TV1 lập checklist mẫu đánh giá 5 người.
- [ ] Chạy thử với môi trường dự phòng, rà dữ liệu không cần công khai trong Power BI Publish to web.

**Bàn giao:** `docs/11_lessons_learned.md`, `docs/release_checklist.md`, `docs/evidence_index.md` cuối, `deliverables/Group13_Submission/` theo yêu cầu nộp.  
**Đạt khi:** Mỗi C01–C11 có file thực + evidence + người trả lời; không còn lỗi P0, bản nộp mở được.

#### 0,5 tuần cuối — Tổng kiểm tra trước khi nộp (`TV5-T5H`)
- [ ] Chạy quick smoke test ETL/DB/PBI, kiểm link public và copy dự phòng.
- [ ] Bấm giờ hai lượt trình bày, ghi lỗi và giao người sửa ngay; không thay thiết kế mới.
- [ ] Đối chiếu từng file giữa bản nộp và bản slide cuối, lưu hash/list file nếu cần.

---

## E. BẢNG GIAO NHẬN GIỮA CÁC THÀNH VIÊN (DEPENDENCIES)

| Ngày cần giao muộn nhất | Người giao → người nhận | Đầu ra để người nhận làm tiếp | Tiêu chuẩn tiếp nhận |
|---|---|---|---|
| **T1-N4** | TV2 → TV1, TV4 | Trường dữ liệu thật, tháng, các chiều có thể dùng | KPI và slicer không dựa trên trường không tồn tại |
| **T1-N5** | TV3 → TV2, TV5 | DB setup, schema, script đọc Parquet | Máy khác chạy được 1 file và SQL mẫu |
| **T1-N6** | TV4 → TV1, TV5 | Kết quả thử PBI Publish-to-web | Có bằng chứng hoặc blocker + phương án hỏi thầy |
| **T2-N10** | TV2 → TV3, TV4 | EDA sơ bộ, ERD, source-to-target mapping, codebook | Có natural keys, month semantics, quy tắc `REDACTED` |
| **T2-N11** | TV1 → TV3, TV4 | KPI dictionary v1 + 3 dashboard requirement | Công thức không mâu thuẫn grain, có source field |
| **T2-N13** | TV3 → TV4, TV5 | MVP DB/Mart + query KPI | Power BI kết nối được, SQL có expected count |
| **T2-N14** | TV4 + TV3 → cả nhóm | Bus matrix, grain/DDL, model v1 đã khóa | Cả nhóm ký duyệt, lưu `change_log.md` |
| **T3-N18** | TV2 → TV3 | Staging clean + quality checks + catalogue mã | Không mất dòng và có báo cáo phát hiện lỗi |
| **T3-N20** | TV3 → TV4, TV5 | Full DW 3 Fact + Dim + 2 Mart | Các bảng query được và đối soát theo tháng |
| **T4-N24** | TV4 → TV5, TV1 | D1/D2 full data, D3 v0, DAX catalog | SQL–DAX tính được cùng phạm vi chọn |
| **T4-N27** | TV5 → TV3, TV4 | Bug list + benchmark baseline + dashboard checks | Lỗi P0/P1 có deadline và owner sửa |
| **T5-N32** | TV2/TV3/TV4/TV5 → TV1 | Hình, bảng thật, phần thuyết minh, tài liệu nguồn | Nội dung copy vào báo cáo không phải viết lại |
| **T5-N34** | TV1 → cả nhóm | Report + slide release candidate | Mọi người đọc, ký duyệt phần kỹ thuật của mình |
| **T5-N35** | TV5 → cả nhóm | Gói release + evidence index + smoke tests | Feature freeze, sẵn sàng tổng duyệt |

**Ý nghĩa các mốc:** `T3-N18` = **ngày 18 tính từ lúc bắt đầu dự án**, thuộc tuần 3. Đây là deadline **nội bộ đề xuất**, không phải thời gian chính thức của thầy.

---

## F. ĐIỂM ƯU TIÊN VÀ PHƯƠNG ÁN CỨU TIẾN ĐỘ

| Mức | Công việc | Quy tắc |
|---|---|---|
| **P0 — Bắt buộc để hoàn thành bài** | C01–C11 đúng phạm vi; OLTP/ODS minh bạch; DB + ETL + 3 Fact + Dimension + ≥2 Mart; 3 BI dashboard; tài liệu + slide + bảng đánh giá thành viên | Không được bỏ. Có thể tinh giản số biểu đồ/ảnh thừa, **không** bỏ lớp kiến trúc/bằng chứng |
| **P1 — Ưu tiên cao để nhắm 4,5–5** | Idempotence, EDA liên hệ/Pareto, mapping chứng cứ, SQL–DAX tests, before–after, benchmark, 3 business scenarios, drill, Publish to web theo quy định | Có kế hoạch từ T1, làm sâu sau MVP. Một số nội dung như Pareto, public, performance vốn đã thuộc tinh thần/yêu cầu [GV], **không được loại tùy tiện** |
| **P2 — Chỉ khi dư thời gian** | Nạp thêm tháng, thêm dashboard thứ 4, automation scheduler, thêm advanced model | Cắt ngay khi trễ MVP hoặc full load |
| **Không làm** | AI/Text-to-SQL, Lakehouse, Kafka, Spark, ML dự báo, tạo HRMS/employee_id giả | Không cần cho bài 5,5 tuần, tăng mạnh rủi ro |

**Nếu quá tải:** Giữ đủ ba dashboard nhưng giảm visual cho từng trang; dùng SQL view thay materialized workflow phức tạp nếu hiệu năng hợp lý; đo benchmark trên một truy vấn đại diện; viết một script CLI orchestration thay hệ thống Airflow. Tuyệt đối không tô đẹp slide để che việc ETL/DW/DM chưa chạy.

**Ba rủi ro phải xử lý sớm [GV + đặc thù dữ liệu]:** (1) “100M” chưa rõ đơn vị; (2) thầy có chấp nhận ERD nguồn/ODS minh họa thay OLTP thực?; (3) Power BI Publish to web có được phép không? TV1 **hỏi thầy ở T1**, TV2/TV3/TV4 đồng thời chuẩn bị phương án kỹ thuật; không đợi thầy mới bắt đầu các việc không phụ thuộc. Nếu một rủi ro khiến đề tài **không đáp ứng điều kiện bắt buộc**, phải quyết định đổi cách thực hiện/dataset/phạm vi ngay T1, không che đến ngày bảo vệ.

---

## G. ĐỊNH NGHĨA HOÀN THÀNH, KIỂM THỬ VÀ MINH CHỨNG

### G1. Definition of Done (DoD) áp dụng cho **mọi** task

- [ ] **Đầu ra có thật:** file code/notebook/DDL/draw.io/PBIX hoặc báo cáo, đặt đúng thư mục.
- [ ] **Chạy hoặc mở được:** người review khác chạy lại trên máy/môi trường được mô tả (hoặc có video/log khi yêu cầu quyền hạn).
- [ ] **Có minh chứng:** ảnh thật/CSV query result có ngày, phạm vi filter, file nguồn/SQL, nhãn `Cxx`.
- [ ] **Có giải thích:** nghiệp vụ, quy tắc xử lý, giả định và hạn chế được ghi trong docs.
- [ ] **Có kiểm tra độc lập:** người review ở B1 đã ký duyệt hoặc ghi issue cần sửa.
- [ ] **Không bịa dữ liệu:** không làm sai mối liên hệ nhân viên, giả KPI, tự viết số liệu benchmark/insight không có nguồn.

### G2. Bộ kiểm thử tối thiểu để bàn giao

| Test ID | Kết quả mong đợi | Owner | Reviewer |
|---|---|---|---|
| T01–T03 | Kiểm kê 12 Parquet/tổng dòng theo nguồn đúng | TV2 | TV5 |
| T04–T05 | Headcount 03 và 06/2025 source = Fact = PBI (khi đúng grain, không filter khác) | TV4 | TV5 |
| T06–T07 | Accessions và Separations theo từng tháng khớp SQL–nguồn | TV3 | TV5 |
| T08 | Dimension code mapping hoặc Unknown được log, không mất hàng | TV3 | TV2 |
| T09 | Rerun 05/2025 không tăng bản ghi/KPI | TV3 | TV5 |
| T10 | Filter một tháng không cộng lẫn 4 Employment snapshots | TV4 | TV1 |
| T11 | Slicer agency/occupation (nếu trường có thật) vẫn khớp SQL–DAX | TV4 | TV5 |
| T12 | Event report/effective month lệch được phân biệt | TV2 + TV3 | TV5 |
| T13 | `REDACTED` không được biến thành 0/giá trị lương đoán | TV2 | TV5 |
| T14 | Public dashboard không phơi bày dữ liệu bản ghi không nên public | TV4 | TV5 |
| T15 | Thiếu file/source schema mismatch báo fail/alert, không âm thầm thành công | TV3 | TV5 |
| T16 | Benchmark có log/cùng query, cùng phạm vi, nhiều lần đo | TV5 | TV3 |
| T17 | Có full load 12/12, snapshot/events đúng theo 4 kỳ, báo cáo row count | TV3 | TV2, TV5 |
| T18 | Report 3 phần đúng mẫu, bảng đánh giá thành viên, slide 30–45 phút | TV1 | TV5 |

**[NB]** Số lượng/mã kiểm thử là tiêu chuẩn nội bộ; workbook [GV] không quy định phải đủ 18 ca. Điểm chính là kiểm chứng dữ liệu và hệ thống.

### G3. Danh sách minh chứng bắt buộc trong `evidence/`

| Thư mục | Minh chứng | Owner |
|---|---|---|
| `C01/` | Quy trình, cây nghiệp vụ, điểm phân tích và mô hình quản trị | TV1 |
| `C02/` | KPI dictionary, requirement tree, ba dashboard trees | TV1 |
| `C03/` | Metadata 12 files, taxonomy, provenance | TV2 |
| `C04/` | ERD nguồn, mapping color, bảng mối liên hệ & giới hạn | TV2 |
| `C05/` | EDA plots, data quality, Pareto, liên hệ chiều/Fact | TV2 |
| `C06/` | Arch logical/physical có logo công nghệ, các schema DB | TV3 |
| `C07/` | ETL jobs, before–after, logs, reconciliation | TV3 + TV2 |
| `C08/` | Dimension catalogue, row counts, hierarchy và sample data | TV4 + TV3 |
| `C09/` | Bus matrix, three stars, staging/DW/DM diagrams & KPI SQL | TV4 + TV3 |
| `C10/` | D1–D3, DAX, slicer/drill-through, publish, test KPI | TV4 |
| `C11/` | Benchmark, tests, lessons, limitations | TV5 |

---

## H. BÁO CÁO, SLIDE VÀ ĐÁNH GIÁ THÀNH VIÊN

**[GV] Báo cáo nhóm bắt buộc theo sheet `Nội dung báo cáo`:** đánh giá thành viên, tự đánh giá báo cáo, **Phần I: Tổng quan DW; Phần II: Tổng quan BI; Phần III: Ứng dụng DW & BI vào HR**, gồm Requirement, ODS, kiến trúc, tiền xử lý, mô hình OLTP và OLAP, các mẫu dashboard; có mục lục, kết luận, tài liệu tham khảo, số trang; **Times New Roman 12**, căn đều hai bên, không sai chính tả.

**Phân công người viết nội dung để TV1 biên tập:**

| Chương/nhóm trang | Người soạn nháp và hình | Người kiểm chuyên môn | Người biên tập vào bản cuối |
|---|---|---|---|
| Phần I + II (kiến thức nền áp dụng) | TV1 | TV3, TV4 | TV1 |
| III.1 Business & Requirement | TV1 | TV2, TV4 | TV1 |
| III.2 Nguồn + ODS/OLTP + ERD + EDA | TV2 | TV3, TV5 | TV1 |
| III.3 Kiến trúc + ETL + DW vật lý | TV3 | TV2, TV5 | TV1 |
| III.4 Dimension + OLAP + DAX + BI | TV4 | TV3, TV5 | TV1 |
| III.5 Test + Performance + Bài học | TV5 | TV3, TV1 | TV1 |
| Phụ lục SQL, notebook, KPI dictionary, log, ảnh | Mỗi người nộp phần mình | TV5 kiểm index | TV1 chèn/chú thích |

**Phân thời gian demo đề xuất [NB]: 40 phút** (nằm trong 30–45 phút [GV]): TV1 **6 phút** (bài toán, yêu cầu, KPI), TV2 **7 phút** (dữ liệu, ERD, EDA), TV3 **9 phút** (kiến trúc, ETL, Fact/DM), TV4 **12 phút** (Dimension/OLAP, 3 dashboard và tình huống), TV5 **6 phút** (test, performance, tổng kết). Nếu giảng viên dành thời gian hỏi đáp trong 30–45 phút, cắt 3–5 phút từ demo và phần trình bày để có chỗ trả lời.

**[GV] Bảng đánh giá 5 thành viên:** điểm đóng góp 1–5, có **ít nhất 4 mức điểm phân biệt**, tất cả thành viên ký tên. Mẫu đánh giá phải theo workbook, không tự cho cả 5 người điểm bằng nhau nếu mẫu hướng dẫn yêu cầu phân biệt. TV1 điều phối, TV5 kiểm đủ chữ ký và định dạng; đánh giá dựa trên issue/commit/evidence và mức hỗ trợ thực tế.

**Mỗi người phải chuẩn bị:** 2–3 câu hỏi khó của phần mình và ít nhất 1 câu hỏi liên ngành (ví dụ `grain`/`headcount`, không có `employee_id`, sự khác biệt `report_month/effective_month`, công bố Power BI).

---

## I. CÁCH THEO DÕI HÀNG TUẦN — DÙNG NGAY TỪ BUỔI HỌP ĐẦU

### I1. Checklist của trưởng nhóm (tick vào cuối mỗi tuần)

| Cuối mốc | Đã chốt / đã nghiệm thu? | Ai xác nhận? |
|---|---|---|
| T1: nguồn, yêu cầu, blockers, PBI, DB | [ ] | TV1 + TV2 + TV3 + TV4 + TV5 |
| T2: ERD/EDA/KPI/grain, MVP nguồn→BI | [ ] | TV1 + TV3 + TV4 + TV5 |
| T3: Full 12 file, DW/DM, rerun test | [ ] | TV2 + TV3 + TV5 |
| T4: D1–D3, SQL/DAX, baseline benchmark | [ ] | TV1 + TV4 + TV5 |
| T5: RC báo cáo/demo, full evidence, public | [ ] | Cả nhóm |
| T5,5: Hai lượt tổng duyệt, ký tên, nộp | [ ] | Cả nhóm |

### I2. Mẫu báo cáo tiến độ của một thành viên (copy vào issue/nhắn nhóm)

```text
[TVx] – [Tuần] – [Ngày]
TASK: TVx-Ty / Cxx
TRẠNG THÁI: TODO | DOING | REVIEW | DONE | BLOCKED
ĐÃ XONG (link commit/file/evidence): ...
CHƯA XONG + LÝ DO: ...
CẦN NGƯỜI NÀO BÀN GIAO: ...
VIỆC LÀM TIẾP TRƯỚC KỲ HỌP SAU: ...
TEST/REVIEWER: ...
```

### I3. Quy ước Git và thư mục nộp

```text
DW_BI_Group13/
├── README.md                         # TV3: setup; TV5: chạy lại + release
├── configs/                          # TV3: .env.example, không commit secret
├── data/README_sources.md            # TV2: URL, license/provenance, hash
├── docs/                             # TV1: scope/KPI; TV2: source/EDA; TV3: DW/ETL; TV4: Dim/BI; TV5: testing
├── diagrams/                         # TV1/TV2/TV3/TV4 theo hạng mục
├── notebooks/                        # TV2: EDA; TV5: validate nếu cần
├── etl/                              # TV3 chủ trì, TV2 phụ trách staging/quality
├── sql/                              # TV3: schema/ETL/marts; TV4: KPI SQL; TV5: test queries
├── tests/                            # TV5 + owners kỹ thuật
├── reports/                          # Kết quả CSV/MD từ code, không điền bừa
├── powerbi/                          # TV4: .pbix và ảnh model
├── evidence/                          # C01..C11, TV5 giữ index
└── deliverables/                     # TV1 report/slide; TV5 đóng gói bản bàn giao
```

**Hợp đồng kỹ thuật không được phá vỡ:** 12 Parquet có 4 kỳ snapshot/event; **headcount không cộng ngang tháng**; nếu chưa chứng minh mỗi dòng Employment là 1 người thì không gọi `COUNT(*)` là số người; **không tự nối nhân viên qua các Fact**; không tạo lịch sử bằng `employee_id` giả; không coi `REDACTED` là 0; không tự đặt KPI/insight; không tuyên bố dữ liệu nguồn công bố là hệ thống OLTP gốc.

---

## J. CÁC QUYẾT ĐỊNH NHÓM CẦN XÁC NHẬN TRONG BUỔI HỌP ĐẦU TIÊN

- [ ] Điền **họ tên TV1–TV5**; người có Windows/Power BI; ai quản lý DB chạy demo; thời gian rảnh thực tế.
- [ ] Chọn ngày bắt đầu T1 và nhập deadline thật vào issue board (các mốc T1-Nx ở trên là lịch tương đối).
- [ ] Phân phối link dataset chính thức và thống nhất **không commit 301,5 MB/zip** vào repo thông thường; sử dụng `data/README_sources.md` và script nạp.
- [ ] Chọn stack triển khai **một lần**: Python + PostgreSQL + Power BI (DuckDB chỉ hỗ trợ khi có nhu cầu). Không thay công cụ liên tục giữa dự án.
- [ ] TV1 gửi câu hỏi giảng viên về 100M/OLTP/Power BI; ghi phản hồi/không phản hồi và mốc xử lý.
- [ ] Thống nhất các tên bảng/KPI, quy tắc PR/review và thư mục evidence.
- [ ] Xác nhận **giới hạn phạm vi:** hoàn thiện 3 Fact + 2 Mart + 3 Dashboard trước, không làm AI/Lakehouse/dự báo nếu chưa hoàn tất.

**Chốt:** Đây là **file phân việc và kế hoạch thực thi**, dùng song song với **file đề cương chính**. Trong 5,5 tuần, không cố làm nhiều hơn nhóm 6 về số slide hoặc công nghệ; ưu tiên đủ 11 mục [GV] với code chạy thật, số liệu có thể đối soát, dashboard được dùng để trả lời câu hỏi, và chứng cứ hiện rõ trên slide.


---

## K. PHẢN HỒI CỦA THẦY VỀ BÀI NHÓM 6 — DANH MỤC CÔNG VIỆC BỔ SUNG V2

> Đây là **các nhiệm vụ bổ sung hoặc làm sâu phần đã phân công**, không thêm người, không gia tăng số dashboard/Fact. P0 = cần hoàn thành cho 11 mục chấm; P1 = tăng chất lượng trình bày; P2 = chỉ làm khi còn thời gian.

| Task ID | Việc cần làm | Chủ trì | Reviewer | Deadline | File/ảnh nghiệm thu | P |
|---|---|---|---|---|---|---|
| FB01 | Touchpoints trong quy trình: bước→KPI→Dimension/Fact→dashboard→source | TV1 | TV2 | Hết T1, chốt T2 | `docs/01_analysis_touchpoints.csv`, 1 slide A# hoàn chỉnh | P0 |
| FB02 | Data Taxonomy có ví dụ thật cho 3 họ file và metadata | TV2 | TV1 | Hết T1 | `diagrams/data_taxonomy.drawio`, ảnh sample raw | P0 |
| FB03 | Audit từ điển: nghĩa trường, kiểu, miền giá trị, nguồn, reviewer; ghi `uncertain` khi chưa chắc | TV2 | TV5 | Hết T2 | `docs/source_data_dictionary.csv`, `reports/dictionary_review.csv` | P0 |
| FB04 | Slide giải thích tương quan **categorical** (bảng chéo, Cramér’s V/Chi-square và giới hạn) | TV2 | TV1 | Hết T2 | `notebooks/01_eda.ipynb`, biểu đồ, trang method | P0 |
| FB05 | Phân tích thời gian 4 kỳ MoM; ghi rõ không thể chứng minh mùa vụ/forecast dài hạn | TV2 | TV4 | Hết T2 | `reports/short_time_series.md` + chart + caveat | P0 |
| FB06 | Sơ đồ nguồn/ODS→OLAP đặt sát ERD/mapping trong chương phân tích | TV2 | TV3 | Hết T2 | `diagrams/source_to_olap_flow.drawio`, slide mapping | P1 |
| FB07 | Kiến trúc có logo công nghệ thực dùng + sơ đồ deployment | TV3 | TV5 | Hết T2 | `diagrams/warehouse_architecture.drawio`, ảnh tools | P1 |
| FB08 | Dimension concept map thành nhóm; row counts + sample dòng của mỗi Dim | TV4 | TV3 | Hết T3 | `diagrams/dimension_groups.drawio`, `reports/dim_row_counts.csv` | P0 |
| FB09 | Dashboard D1–D3: đơn vị, dấu hàng nghìn, DAX cảnh báo + định dạng có điều kiện | TV4 | TV5 | Hết T4 | `.pbix`, ảnh DAX, dashboard QA checklist | P0 |
| FB10 | Ba câu chuyện BI: tình huống→slicer→chart→insight→quyết định/giới hạn, có SQL đối soát | TV4 | TV1 + TV5 | Hết T4 | `docs/10_storytelling_cases.md`, evidence 3 case | P0 |
| FB11 | Dàn câu hỏi vấn đáp: categorical correlation, grain/snapshot, kỳ hiệu lực, OLTP minh họa, seasonality, alert threshold | TV5 | TV1 | Hết T5 | `docs/oral_defense_questions.md`, 2 lần tổng duyệt | P0 |
| FB12 | Một tính năng bổ sung nhỏ (ưu tiên scheduling/log ETL) | TV3 | TV5 | Chỉ nếu T5 còn thời gian | log chạy lịch, ảnh kiểm thử hoặc nêu không triển khai | P2 |

### Giao kèo để không quá tải trong 5,5 tuần

- **TV1 (MacBook Pro M1):** làm KPI, story, báo cáo, quản lý; review bằng SQL/markdown trên Mac, **không chịu trách nhiệm tạo Power BI Desktop**.
- **TV2 (Windows):** chịu trách nhiệm thực nghiệm quan hệ phân loại (FB04) và dictionary; không làm thêm nghiên cứu seasonality nhiều năm trong 5,5 tuần trừ khi nâng cấp nguồn được duyệt.
- **TV3 (Windows):** ưu tiên kho dữ liệu chạy được, logo sơ đồ chỉ là tài liệu; không ưu tiên hướng mở rộng hơn lỗi ETL.
- **TV4 (Windows + Power BI Desktop):** chuẩn hóa trình bày dashboard và OLAP; không thêm chart/measure chỉ để tăng số lượng.
- **TV5 (Windows):** kiểm soát evidence và phản biện số liệu; nếu thiếu thời gian, cắt FB12 trước và dành buffer để bảo vệ demo.
- Mọi task P0 **phải có bằng chứng** (file, query/test, hình hoặc demo) và được reviewer khác người chủ trì xác nhận; từ điển/insight không được chép lại mà không kiểm chứng.

### Mẫu status cho từng FB task

`ID | Owner | Reviewer | Hạn | NOT_STARTED / DOING / REVIEW / DONE / BLOCKED | Link sản phẩm | Link evidence | Đã đối soát?`
