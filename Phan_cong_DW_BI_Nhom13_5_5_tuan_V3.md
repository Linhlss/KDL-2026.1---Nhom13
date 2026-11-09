# PHÂN CÔNG CÔNG VIỆC DW & BI — NHÓM 13, 5 THÀNH VIÊN, 5,5 TUẦN

**Đề tài:** Xây dựng kho dữ liệu và hệ thống Business Intelligence hỗ trợ phân tích quy mô, cơ cấu và biến động nhân sự tại các cơ quan liên bang Hoa Kỳ.  
**Tài liệu chuẩn:** `De_cuong_DW_BI_Nhom13_5_5_tuan_V2_phan_hoi_thay.md`  
**Nguồn:** 12 Parquet OPM/EHRI, 03–06/2025, ~301,5 MB.  
**Thời gian:** Ngày 1–39 kể từ ngày khởi động.  
**Phạm vi:** OPM/EHRI → Relational Source Model → Staging/ODS → DW (3 Fact + Dimensions) → ≥2 Data Mart → 3 Power BI dashboards.

> **Quy định:** Không sử dụng dữ liệu HR giả, không dựng employee_id, không liên kết các bản ghi Employment/Accessions/Separations ở cấp nhân viên. Phân biệt rõ khóa nghiệp vụ OPM, khóa kỹ thuật trong pipeline và quan hệ phân tích. Mọi kết quả phải có mã nguồn, đầu ra và người review. Không ghi nhận ERD tái cấu trúc là OLTP của OPM.

## 1. Vai trò và trách nhiệm

| TV | Vai trò | Máy | Phạm vi sở hữu | Reviewer |
|---|---|---|---|---|
| **TV1** | Trưởng nhóm / Project Lead & Business Analyst | **MacBook Pro M1** | C01–C02, quản lý tiến độ, KPI, liên hệ thầy, báo cáo và slide | TV2, TV4, TV5 |
| **TV2** | Data Analyst / Source & EDA | Windows | C03–C05; inventory, codebook, taxonomy, kiểm mã, ERD nguồn, EDA | TV3, TV5 |
| **TV3** | Data Engineer / DW & ETL | Windows | C06–C07; PostgreSQL, ODS, ETL, 3 Fact, Data Mart, kiến trúc vật lý | TV2, TV5 |
| **TV4** | BI & OLAP Developer | Windows | C08–C10; Dimension logic, bus matrix, DAX, dashboard, Power BI public | TV1, TV3, TV5 |
| **TV5** | QA / Performance / Integration | Windows | C11 và kiểm thử C01–C10; đối soát, hiệu năng, gói nộp | TV1, TV3 |

**Nguyên tắc:** TV1 không phải tự viết báo cáo thay cả nhóm; mỗi thành viên viết đúng phần mình phụ trách và hiểu toàn bộ pipeline. TV3/TV4 có khối lượng kỹ thuật lớn nên TV2 hỗ trợ ref/DQ, TV5 hỗ trợ SQL tests và dashboard QA. TV4 phải làm Power BI Desktop trên Windows; TV1 dùng Mac để review nghiệp vụ, SQL, diagram và tài liệu.

**Dự trù công sức:** TV1 khoảng 10–12h/tuần, TV2 13–16h, TV3 15–20h, TV4 15–18h, TV5 12–15h. Thực tế phải được 5 người thống nhất, không dồn hết việc vào một người.

## 2. Cổng quyết định tuần 1 — không được bỏ qua

| ID | Điều chưa được giải quyết | Hành động | Owner | Hạn | Minh chứng |
|---|---|---|---|---|---|
| **R01** | Thầy có chấp nhận ERD nguồn quan hệ tái cấu trúc đáp ứng mục “ERD OLTP” không? | TV2 đưa ERD phác thảo, TV1 gửi giảng viên hỏi trực tiếp, TV3 phản biện | TV1 | Ngày 2–5 | Ảnh/tin nhắn trả lời hoặc trạng thái chưa phản hồi trong `docs/00_scope_decisions.md` |
| **R02** | Publish to web có khả thi không? | TV4 thử một báo cáo tổng hợp từ dữ liệu thật, TV5 mở ẩn danh | TV4/TV5 | Ngày 4 | URL hoạt động hoặc ảnh lỗi và kế hoạch xin duyệt phương án thay thế |
| **R03** | Có quan hệ PK/FK nào được xác minh qua codebook không? | TV2 kiểm code→label, uniqueness, key scope, orphan, lịch sử mã; TV3 xác nhận DDL | TV2/TV3 | Ngày 7 bản đầu; ngày 12 chốt | `docs/04_relationship_audit.csv` + SQL |
| **R04** | Baseline và version | 12 file, tháng/version/schema/sha256, khóa baseline | TV2 | Ngày 3 | `docs/03_source_inventory.csv` |

**Nếu R01 không được thầy chấp nhận:** nhóm phải tìm cấu trúc nguồn giao dịch HR có khóa thật hoặc điều chỉnh đề tài trước khi xây full DW; không tự tạo quan hệ nhân viên cho đủ ERD. Nếu R01 chưa có phản hồi, chỉ làm các phần không phụ thuộc và ghi trạng thái chưa đóng.

## 3. Quản lý tiến độ và bàn giao

**Trạng thái:** `TODO → DOING → REVIEW → DONE`, hoặc `BLOCKED` khi thiếu đầu vào. Mỗi task ghi `ID, Owner, Reviewer, Deadline, Dependency, Output Path, Evidence Path, Pass Criteria`. Người review phản hồi trong 24 giờ. Khi KPI/Fact grain/ref key thay đổi sau ngày 14, phải cập nhật change log và báo cả TV1–TV5.

**Các cổng chất lượng:**

| Gate | Ngày | Điều kiện đạt |
|---|---|---|
| G0 | 1–5 | R01/R02 có tình trạng và bằng chứng; inventory/version và môi trường cơ bản |
| G1 | 6–7 | Business scope, KPI v0, source taxonomy/dictionary v0, ownership rõ |
| G2 | 8–14 | Verified ERD source + mapping, EDA, DW grain/bus matrix/DDL, MVP 3 nguồn → 1 KPI Power BI |
| G3 | 15–21 | ETL 12 file, 3 Fact, ≥2 Data Mart, Dim audit, SQL reconciliation, rerun pass |
| G4 | 22–28 | Ba dashboard v1, slicer/drill/tooltip/DAX, 10 SQL–DAX cases, benchmark baseline |
| G5 | 29–35 | Bug fix, benchmark, publication, full report/slide, evidence C01–C11 |
| G6 | 36–39 | Hai buổi tổng duyệt 30–45 phút và đóng gói nộp chính thức |

**Hệ thống không được coi DONE nếu** chỉ có ảnh mà không chạy được, hoặc mô hình có bảng mã do nhóm đoán mà không ghi nguồn.

## 4. TV1 — Trưởng nhóm / Business Analyst (MacBook Pro M1)

### Tuần 1 — Ngày 1–7

- [ ] **L1-01 | Ngày 1:** Tạo repo issue board, `docs/00_scope_decisions.md` (domain, dataset, ba dashboard, deadline, các quyết định chưa đóng). **Output:** quyết định phạm vi nhóm và lịch họp, người review.
- [ ] **L1-02 | Ngày 2–3:** Nhận bản ERD phác từ TV2, hỏi thầy có chấp nhận mô hình nguồn quan hệ EHRI thay ERD OLTP giao dịch không. **Output:** ảnh/phản hồi thầy; ghi rõ đồng ý/không đồng ý/chưa trả lời; không tự kết luận.
- [ ] **L1-03 | Ngày 3:** Đối chiếu sheet yêu cầu và thông báo kỳ này: báo cáo, slides, phiếu đánh giá, thời lượng 30–45 phút, public. **Output:** `docs/00_course_requirements.md`.
- [ ] **L1-04 | Ngày 4–6:** Viết bối cảnh: HR data cấp cơ quan, OPM EHRI và Federal Workforce Data; phân biệt nguồn được OPM công bố với hệ thống phân tích nhóm đề xuất. **Output:** `docs/01_business_scope.md`.
- [ ] **L1-05 | Ngày 6–7:** Sơ đồ quy trình quản trị nhân lực và phân tích dữ liệu, cây nghiệp vụ, điểm phân tích A01–A10 và mapping KPI. **Output:** `diagrams/01_business_process.drawio`, `diagrams/01_business_tree.drawio`, `docs/01_touchpoint_mapping.csv`.

**Nghiệm thu:** Không có quy trình nội bộ OPM bịa đặt; mỗi bước có input/output, chỉ số và nguồn, R01 minh bạch.

### Tuần 2 — Ngày 8–14

- [ ] **L1-06 | Ngày 8–10:** Soạn persona, FR/NFR, cây yêu cầu tổng và ba cây D1–D3. **Output:** `docs/02_requirements.md`, `diagrams/02_requirements_tree.drawio`, ba dashboard trees.
- [ ] **L1-07 | Ngày 9–11:** Chốt `docs/02_kpi_dictionary.csv`: K01–K10, công thức, nguồn, grain, tháng report/effective, filter, NULL, ngưỡng; duyệt cùng TV4. **Pass:** không có KPI không có nguồn.
- [ ] **L1-08 | Ngày 11–12:** Review Data Dictionary và ERD; hỏi TV2 bảng mã nào được verified và không cho phép vẽ FK giả. **Output:** comment review `docs/04_relationship_audit.csv`.
- [ ] **L1-09 | Ngày 13–14:** Họp khóa model: grain, Dim, DAX, phiên bản file, schema; ghi `docs/00_model_decisions.md`, viết phần nghiệp vụ/nguồn của báo cáo.

**Nghiệm thu:** Bằng chứng một đường `bài toán → KPI → trường nguồn → Fact/Dim → Mart → DAX` và KPI không mâu thuẫn giữa các thành viên.

### Tuần 3 — Ngày 15–21

- [ ] **L1-10:** Review row reconciliation cùng TV5 và ý nghĩa KPI; nếu biến động headcount không khớp events, phải ghi giới hạn, không sửa công thức để ép khớp.
- [ ] **L1-11:** Viết Phần I (DW) và II (BI) đúng format giảng viên; liên hệ với stack thực dùng, không dùng thông tin công nghệ không triển khai.
- [ ] **L1-12:** Chuẩn bị slide nghiệp vụ, phạm vi nguồn, ERD nguồn và disclaimer để bảo vệ.

### Tuần 4 — Ngày 22–28

- [ ] **L1-13:** Review mỗi dashboard theo chuỗi bối cảnh → câu hỏi → thao tác → bằng chứng → insight → khuyến nghị.
- [ ] **L1-14:** Kiểm định nghĩa headcount, action count, event difference, tháng, đơn vị, giới hạn 4 kỳ; từ chối các kết luận suy ra nguyên nhân không có bằng chứng.
- [ ] **L1-15:** Ghép chương nghiệp vụ và EDA có kết quả thật vào báo cáo; lưu nguồn trích dẫn và ảnh.

### Tuần 5 — Ngày 29–35

- [ ] **L1-16:** Tổng hợp báo cáo từ 4 người, theo ba phần chính thầy yêu cầu, Times New Roman 12, căn đều, số trang, tài liệu tham khảo và phụ lục.
- [ ] **L1-17:** Thiết kế slide 30–45 phút, thời lượng 5 thành viên, runbook demo trên Windows và backup.
- [ ] **L1-18:** Thu phiếu đánh giá 5 thành viên đúng mẫu thầy, đầy đủ chữ ký; kiểm tra 11 folder evidence.
- [ ] **L1-19:** Chốt những lỗi P0 cần sửa trước ngày 35, không thêm tính năng mới.

### 0,5 tuần — Ngày 36–39

- [ ] **L1-20:** Tổ chức hai buổi tổng duyệt và hỏi chéo về Fact grain, ERD, report/effective time, DAX và benchmark.
- [ ] **L1-21:** Kiểm gói nộp: report, slide, SQL, ETL, PBIX, DB dump, model, ảnh, phiếu ký; bảo đảm đúng phiên bản demo.

## 5. TV2 — Data Analyst / Source, ERD, EDA (Windows)

### Tuần 1 — Ngày 1–7

- [ ] **L2-01 | Ngày 1–3:** Inventory 12 Parquet: family, month, version, bytes, row count, columns, SHA-256, schema. **Output:** `docs/03_source_inventory.csv`, `data/manifest/sha256.txt`.
- [ ] **L2-02 | Ngày 2–5:** Tìm FWD Dictionary, EHRI current/past standards, Duty Stations, lưu URL, ngày truy xuất, file chứng cứ. **Output:** `data/reference/README.md` và reference manifest.
- [ ] **L2-03 | Ngày 3–6:** Data Dictionary nhóm mã quan trọng, percent Null/REDACTED và ý nghĩa theo OPM. **Output:** `docs/03_data_dictionary.csv`, TV5 review.
- [ ] **L2-04 | Ngày 4:** Phác ERD record-source_file-ref tables có chú giải verified/unverified, gửi TV1 hỏi thầy. **Output:** `diagrams/04_relational_source_erd.drawio` v0.
- [ ] **L2-05 | Ngày 6–7:** Data Taxonomy có ví dụ dữ liệu thật, sơ đồ data flow OPM, mũi tên ghi dữ liệu trao đổi. **Output:** `docs/03_taxonomy.md`, `diagrams/03_opm_source_flow.drawio`.

### Tuần 2 — Ngày 8–14

- [ ] **L2-06 | Ngày 8–10:** Audit `agency_code`, `department_code`, `agency_subelement_code`, `occupational_series_code`, `occupational_group_code`, `duty_station_code`, `pay_plan_code`, `grade`: distinct, code→label, key scope, orphan, lịch sử mã. **Output:** `docs/04_relationship_audit.csv`, `sql/tests/04_fk_audit.sql`.
- [ ] **L2-07 | Ngày 9–11:** Chỉ tạo các bảng ref có định nghĩa chính thức/đã kiểm chứng; xác minh mã và nhãn, provenance, exceptions. **Output:** `data/reference/verified_codebook_manifest.csv`.
- [ ] **L2-08 | Ngày 11–12:** Hoàn chỉnh ERD và source→target mapping tới ODS/Dim/Fact, từng trường ghi rule và validation. **Output:** `docs/04_source_to_target_mapping.csv`, ERD v1.
- [ ] **L2-09 | Ngày 8–13:** EDA 7 chiều chất lượng, Pareto, histogram phù hợp, hai bảng chéo categorical, Chi-square + Cramér’s V trên một snapshot, biểu đồ MoM. **Output:** `notebooks/01_eda.ipynb`, `reports/05_eda_findings.md`.
- [ ] **L2-10 | Ngày 13–14:** Slide tính tay Eij/Chi-square/Cramér’s V bằng bảng chéo nguồn thật, ý nghĩa thống kê, giới hạn mẫu và không dùng Pearson trên mã. Không sử dụng dữ liệu giả lập 300 người làm minh chứng.

**Nghiệm thu:** ERD có ranh giới nguồn thật vs key pipeline; code→label có reference và kết quả SQL; không tuyên bố association là FK.

### Tuần 3 — Ngày 15–21

- [ ] **L2-11:** Hỗ trợ TV3 job J02 kiểm `REDACTED`, NULL/Unknown, report/effective month và missing codes.
- [ ] **L2-12:** Tạo bảng `before/rule/after/affected_rows/impact`, ghi SQL và ảnh trên dữ liệu thật, không xóa dòng chỉ vì giống nhau.
- [ ] **L2-13:** Báo cáo orphan FK/exception, quality statistics từng họ và tham vấn xử lý với TV3; kiểm không làm mất Fact khi lookup.

### Tuần 4 — Ngày 22–28

- [ ] **L2-14:** Đối chiếu EDA source với Mart, xác định nguyên nhân mọi chênh lệch do filter/kỳ/Unknown.
- [ ] **L2-15:** Viết chương nguồn dữ liệu/ERD/EDA với các công thức, biểu đồ và hạn chế, đưa ảnh/tham chiếu cụ thể cho báo cáo.

### Tuần 5 và 0,5 tuần — Ngày 29–39

- [ ] **L2-16:** Hoàn thành Data Dictionary, taxonomy, ERD, codebook audit, data flow và appendix nguồn; xuất slide giải trình C03–C05.
- [ ] **L2-17:** Tổng duyệt bảo vệ: trả lời vì sao thiếu employee ID, FK nào có thật, Cramér’s V tính thế nào, tại sao bốn tháng chưa đủ cho seasonality.

## 6. TV3 — Data Engineer / DW & ETL (Windows)

### Tuần 1 — Ngày 1–7

- [ ] **L3-01 | Ngày 1–3:** Chọn DB chính (mặc định PostgreSQL), cấu hình schema và cách kết nối TV4; không commit password. **Output:** `configs/.env.example`, `docs/06_environment_setup.md`.
- [ ] **L3-02 | Ngày 3–5:** Thử nạp một file Accessions/Separations và phần Employment thật để kiểm kiểu, tốc độ, ordinal, checksum; có SQL row-count. **Output:** `etl/prototype_ingest.py`, log.
- [ ] **L3-03 | Ngày 5–7:** Kiến trúc thành phần v0 gồm storage, Python ETL, PostgreSQL, Power BI; ghi đúng máy chạy và kết nối. **Output:** `diagrams/06_architecture_components.drawio`.
- [ ] **L3-04 | Ngày 7:** Phản biện PK/FK và source ERD của TV2; chỉ chấp nhận các ref được xác minh.

### Tuần 2 — Ngày 8–14

- [ ] **L3-05 | Ngày 8–9:** Tạo `raw_meta`, `staging`, `ref`, `ods`, `dw`, `mart`, `audit`, DDL `source_file`, `ods_*_record`, run logs. **Output:** `sql/00_raw_ref_ods_ddl.sql`, `sql/01_create_schemas.sql`.
- [ ] **L3-06 | Ngày 10:** Viết J00/J01 scan/checksum/parquet ingest; source row identity theo `(file_id, source_row_ordinal)` đã chốt. **Output:** ETL code + `reports/07_load_log.csv`.
- [ ] **L3-07 | Ngày 11–12:** DW DDL ba Fact, Dim và 2 Mart từ bus matrix TV4; giữ report/effective month riêng. **Output:** `sql/03_dw_ddl.sql`, `sql/04_create_marts.sql`.
- [ ] **L3-08 | Ngày 12–13:** MVP 1 file mỗi family → ODS → 3 Fact → 1 Mart → TV4 xem KPI bằng Power BI. **Output:** DB + SQL KPI và log.
- [ ] **L3-09 | Ngày 14:** Sơ đồ architecture, ETL pipeline và DW **physical overall** khớp DDL; không dùng sơ đồ flow thay architecture. **Output:** 3 tệp draw.io.

**Nghiệm thu:** End-to-end chạy được, source→Fact→Mart không nhân dòng, PK/FK hợp lệ và KPI MVP soát được.

### Tuần 3 — Ngày 15–21

- [ ] **L3-10 | Ngày 15–17:** Chạy full J01/J02 nạp 12 file; log theo tháng/family/version/rows/duration; không mất raw record.
- [ ] **L3-11 | Ngày 16–19:** J03 build Dim/ref, Unknown và surrogate keys; J04 build 3 Fact đúng grain; lưu số dòng từng bảng, orphan/exception.
- [ ] **L3-12 | Ngày 18–20:** J05 build 2 Mart thật. Với các event Fact, **aggregate trước hoặc UNION ALL**, không JOIN raw Fact theo agency/month.
- [ ] **L3-13 | Ngày 20–21:** J06 reconciliation, thử chạy lại tháng 05 và xử lý version; DB/Fact/Mart không tăng dòng bất thường; xuất log và ảnh before–after.

**Nghiệm thu:** 12 file, 3 Fact, 2 Mart và full test pass; exceptions có bằng chứng; người khác có thể rerun theo runbook.

### Tuần 4 — Ngày 22–28

- [ ] **L3-14:** Hỗ trợ TV4 model/DAX/SQL, giữ ổn định schema; mọi sửa key/grain phải được TV1–TV5 duyệt.
- [ ] **L3-15:** Benchmark một truy vấn Fact vs Mart hoặc trước/sau index, cùng điều kiện ba lần đo, SQL/EXPLAIN ANALYZE cùng TV5.
- [ ] **L3-16:** Chuẩn hóa ảnh architecture components và data flow, tạo `docs/07_runbook.md`, DB dump/schema backup.

### Tuần 5 và 0,5 tuần — Ngày 29–39

- [ ] **L3-17:** Freeze schema, chỉ sửa lỗi có ảnh hưởng KPI, nghiệm thu performance, query và pipeline rerun trên máy demo.
- [ ] **L3-18:** Bàn giao SQL/ETL/DDL/DB dump và slide giải trình ETL, grain, idempotence, mô hình vật lý và log.

## 7. TV4 — BI/OLAP Developer (Windows)

### Tuần 1 — Ngày 1–7

- [ ] **L4-01 | Ngày 1–4:** Cài Power BI Desktop, kiểm quyền Service/Publish to web bằng report tổng hợp an toàn, TV5 mở ẩn danh. **Output:** `docs/10_publish_feasibility.md`, URL hoặc ảnh lỗi.
- [ ] **L4-02 | Ngày 3–7:** Thiết kế ba wireframe D1–D3, mỗi trang có persona, câu hỏi, measure, filter, chart, story. **Output:** `docs/10_dashboard_specs.md`.
- [ ] **L4-03 | Ngày 6–7:** Bus matrix và nhóm Dimension dự thảo, nhận danh sách mã từ TV2; ghi `verified/uncertain`.

### Tuần 2 — Ngày 8–14

- [ ] **L4-04 | Ngày 8–11:** Khóa Fact grain, Dim month/agency/occupation/location/grade/category, hierarchy hợp lệ, Unknown rule và việc sử dụng mỗi Dim. **Output:** `docs/08_dimension_catalog.csv`, `diagrams/08_dimension_groups.drawio`.
- [ ] **L4-05 | Ngày 11–12:** Mô hình logic DW, bus matrix, ghi rõ role-playing date report/effective, không nối Fact-Fact trực tiếp. **Output:** `docs/09_bus_matrix.md`, `diagrams/09_dw_logical.drawio`.
- [ ] **L4-06 | Ngày 13–14:** Kết nối Mart mẫu từ TV3 vào Power BI, tạo slicer Month/Agency và ít nhất một KPI DAX đối soát SQL. **Output:** `.pbix` MVP, screenshot/model test.

### Tuần 3 — Ngày 15–21

- [ ] **L4-07:** Kết nối Mart thật, kiểm relationship, ambiguity và hướng lọc; ghi tên cột, bảng đích, role dates.
- [ ] **L4-08:** Viết DAX K01–K10, điều kiện missing/zero prior month, báo cáo KPI totals theo cùng filter; format người/lượt/%.
- [ ] **L4-09:** Dimension catalog chính thức: số dòng, 2–3 dòng dữ liệu thật, grouping/hierarchy, natural key và Fact sử dụng; phối hợp TV3 kiểm physical overall.

### Tuần 4 — Ngày 22–28

- [ ] **L4-10 | Ngày 22–24:** D1 Workforce Overview: snapshot headcount, cơ cấu, MoM, slicer/drill. Không cộng snapshot giữa tháng.
- [ ] **L4-11 | Ngày 23–25:** D2 Personnel Flows: Accessions, Separations theo report month, agency, category; tooltip về effective month; không gán event difference là net headcount.
- [ ] **L4-12 | Ngày 24–27:** D3 Workforce Changes/OLAP: top tăng/giảm, heatmap, drill-through, conditional formatting, hai threshold DAX có lời giải thích.
- [ ] **L4-13 | Ngày 26–28:** Tạo **public-only semantic model** từ mart aggregate; không công bố bản ghi raw/ODS, REDACTED; test URL ẩn danh và quyền export.

**Nghiệm thu:** 3 trang chạy trực tiếp, 3 stories có SQL làm chứng, 10 test DAX/SQL pass và xử lý các hạn chế public.

### Tuần 5 và 0,5 tuần — Ngày 29–39

- [ ] **L4-14:** Điều chỉnh storytelling, nhãn thời gian/đơn vị/dấu nghìn, tooltip, số 0 và BLANK, ngưỡng minh họa; không vẽ forecast/năm từ 4 kỳ.
- [ ] **L4-15:** Freeze `.pbix`, public link, export screenshot và video demo backup; bảo đảm file trên repo là bản bảo vệ.
- [ ] **L4-16:** Tổng duyệt live D1→D2→D3, trả lời câu hỏi measure, slice/dice/drill/roll-up, semi-additive snapshot.

## 8. TV5 — QA/Performance/Integration (Windows)

### Tuần 1 — Ngày 1–7

- [ ] **L5-01 | Ngày 1–3:** Tạo `tests/test_plan.md`, acceptance matrix C01–C11 và board bug; mỗi test có SQL/expected/actual/evidence.
- [ ] **L5-02 | Ngày 4–6:** Audit độc lập inventory và field meanings quan trọng, checksum/version 12 file; không copy số liệu sơ bộ khi chưa chạy.
- [ ] **L5-03 | Ngày 4–7:** Hỗ trợ TV4 thử URL ẩn danh, kiểm model nào công bố và rủi ro export.

### Tuần 2 — Ngày 8–14

- [ ] **L5-04 | Ngày 8–10:** Viết SQL tests file count, raw/ODS row counts, unique PK, orphan FK, null/REDACTED, Date role.
- [ ] **L5-05 | Ngày 11–12:** Kiểm ERD ref audit của TV2, đánh dấu verified/partial/unsupported và người review; không duyệt FK sai.
- [ ] **L5-06 | Ngày 13–14:** Kiểm MVP source → ODS → Fact → Mart → Power BI, soát ít nhất một KPI cùng kỳ/nhóm; báo lỗi chặn G2.

### Tuần 3 — Ngày 15–21

- [ ] **L5-07 | Ngày 15–18:** Kiểm full row count từng family và file: Employment 9.057.997, Accessions 30.782, Separations 92.511, tổng 9.181.290; exceptions phải có lý do.
- [ ] **L5-08 | Ngày 18–20:** Test rerun tháng 05, idempotence và version; bảo đảm không nhân bản kết quả.
- [ ] **L5-09 | Ngày 20–21:** SQL kiểm 3 Fact, 2 Mart, Dimension keys, Unknown và 10 KPI; xuất `reports/07_reconciliation.csv`.

### Tuần 4 — Ngày 22–28

- [ ] **L5-10 | Ngày 22–25:** Benchmark truy vấn cùng dữ liệu/điều kiện, ít nhất 3 lần, median, query plan, ghi máy và cấu hình.
- [ ] **L5-11 | Ngày 24–28:** Test ≥10 trường hợp slicer/SQL–DAX với month, agency, occupation; drill/tooltip/đơn vị, threshold và BLANK/0.
- [ ] **L5-12 | Ngày 27–28:** Public model audit: không có raw record, salary redacted, chi tiết không nên xuất; mở ẩn danh, kiểm export và log.

### Tuần 5 và 0,5 tuần — Ngày 29–39

- [ ] **L5-13 | Ngày 29–32:** Regression test sau tối ưu, đảm bảo kết quả KPI không đổi, xử lý blockers.
- [ ] **L5-14 | Ngày 31–34:** Viết `docs/11_lessons_learned.md`: vấn đề → chứng cứ → quyết định → đo đạc → kết quả → hạn chế.
- [ ] **L5-15 | Ngày 34–35:** Chốt checklist C01–C11, kiểm release manifest, hashes, `.pbix`, DB dump, source and scripts; gửi TV1.
- [ ] **L5-16 | Ngày 36–39:** Tổng duyệt, test lỗi mạng/DB/Power BI và phương án backup; không che lỗi chưa khắc phục.

## 9. Bảng bàn giao giữa các thành viên

| Mốc | Người giao → nhận | Hạn | Sản phẩm | Điều kiện nhận |
|---|---|---|---|---|
| H01 | TV2 → TV1 | 4 | Inventory và source ERD phác | Có nội dung đủ để hỏi thầy, không có nhân viên giả |
| H02 | TV1 → toàn nhóm | 5 | Quyết định R01 và thông báo thầy | Ghi rõ đồng ý / không đồng ý / chưa trả lời |
| H03 | TV2 → TV3 | 10 | Verified codebook, FK audit | Mã, phạm vi, exceptions và source đầy đủ |
| H04 | TV1/TV2 → TV4 | 11 | KPI Dictionary + field mapping | Mọi KPI có trường dữ liệu, kỳ và grain |
| H05 | TV4 → TV3 | 12 | Bus matrix, Fact grain, Dimension catalog | Đủ để dựng DDL mà không tự suy diễn |
| H06 | TV3 → TV4/TV5 | 14 | MVP DB + Mart + SQL KPI | Power BI kết nối và SQL đối soát được |
| H07 | TV3 → TV4/TV5 | 21 | Full DW + 2 Mart + pipeline logs | Row counts, tests, rerun đạt |
| H08 | TV4 → TV1/TV5 | 28 | 3 dashboard v1, stories, publish test | SQL/DAX khớp, nội dung giải thích đúng |
| H09 | TV5 → TV3/TV4 | 30 | Bug list + benchmark | Có độ nghiêm trọng, owner, deadline |
| H10 | TV2/3/4/5 → TV1 | 33 | Chương báo cáo + evidence | Không dùng số liệu chưa chạy |
| H11 | TV1 → cả nhóm | 35 | Slide/report/demo runbook | Freeze tính năng và sẵn sàng tập trình bày |

## 10. Bộ kiểm thử tổng thể

| ID | Nội dung | Tiêu chuẩn PASS |
|---|---|---|
| Q01 | 12 tệp Parquet baseline | Đủ tháng/family/version, không lẫn file `__MACOSX` |
| Q02 | Row count | 9.057.997 + 30.782 + 92.511, đối soát từ file nguồn |
| Q03 | Data Dictionary | Có định nghĩa, codebook và reviewer cho trường dùng trong KPI |
| Q04 | Source PK/FK | `file_id` hợp lệ, code FK có audit; exception có log |
| Q05 | Không tạo quan hệ giả | Không gán employee_id hoặc kết nối 3 family bằng agency để suy người |
| Q06 | Monthly Headcount | Source/Fact/Mart/DAX khớp theo cùng một kỳ |
| Q07 | Events | Counts theo report month, effective month giữ nguyên tách biệt |
| Q08 | ETL rerun | Nạp lại không tăng row counts/KPI, version có rule |
| Q09 | REDACTED | Không thành 0 hay giá trị tự tạo; Unknown được theo dõi |
| Q10 | Data Mart | Tối thiểu 2 bảng/view tổng hợp chạy SQL trong database |
| Q11 | Mô hình vật lý | DW physical overall khớp DDL, grain, PK/FK và marts |
| Q12 | OLAP/BI | 3 dashboard, 3 story, slice/drill/tooltip, 10 SQL–DAX cases PASS |
| Q13 | Công bố | URL anonymous hợp lệ hoặc phương án khác thầy chấp thuận; public model an toàn |
| Q14 | Benchmark | ≥3 lần đo/biến thể, cùng môi trường, median và query plan |
| Q15 | Hồ sơ | Báo cáo 3 phần, Time New Roman 12, phiếu 5 người ký, backup |

**Đặc biệt:** Khi chưa có phản hồi thầy về ERD, Q04 chỉ là đánh giá **đúng kỹ thuật**; không được tự tuyên bố C04 đạt yêu cầu giảng viên. Khi Power BI bị chặn Publish to web, ảnh screenshot không tự động thay cho yêu cầu công bố.

## 11. Trình bày trên lớp và trách nhiệm vấn đáp

| Người | Nội dung | Thời lượng |
|---|---|---:|
| TV1 | Bài toán HR, quy trình, requirement, KPI | 5 phút |
| TV2 | Source, Data Dictionary, ERD nguồn, EDA | 11 phút |
| TV3 | Architecture, ODS/ETL, DW/Data Mart | 9 phút |
| TV4 | Dimension, OLAP và 3 Power BI dashboards demo | 11 phút |
| TV5 | Đối soát, hiệu năng, kiểm thử, bài học | 4 phút |
| **Tổng** | **5 người** | **40 phút** |

TV3 thao tác DB/ETL và TV4 thao tác Power BI trên Windows; TV5 chuẩn bị runbook và backup. TV1 kiểm lời nói thống nhất giữa các phần, không dùng tên OLTP gốc của OPM cho mô hình nhóm tái cấu trúc.

## 12. Danh sách nộp cuối

- [ ] R01 có phản hồi hoặc trạng thái chưa chốt được báo trung thực.
- [ ] R02 có link công khai mở ẩn danh hoặc phương án thay thế thầy chấp thuận.
- [ ] 12 file có manifest SHA-256/version và nguồn chính thức.
- [ ] C01–C11 đủ sơ đồ/bảng/query/evidence tương ứng.
- [ ] Source ERD (verified PK/FK) khác DW logical/physical và ETL flow.
- [ ] Full pipeline 12 file chạy lại, 3 Fact/2 Mart, row reconciliation và SQL–DAX tests.
- [ ] Ba dashboard có story, slicer, drill, tooltip, ngưỡng cảnh báo và đơn vị đúng.
- [ ] Benchmark đo được, ghi môi trường và thời gian trước/sau.
- [ ] Báo cáo đúng cấu trúc, slide/demo 30–45 phút, tài liệu tham khảo và phiếu đánh giá đủ chữ ký.
- [ ] Đã tập hai lần, tất cả người có thể trả lời về giới hạn OPM, grain, ERD, KPI và pipeline.

**Quy tắc ưu tiên khi trễ:** P0 gồm ERD/ETL/DW/Dim/OLAP/3 dashboard/SQL–DAX/báo cáo; P1 là quality và performance; P2 là API scheduler, thêm kỳ, AI, Lakehouse, ML hoặc dashboard thứ tư. Cắt P2 trước, không thay thế lỗi kiến trúc bằng mở rộng công nghệ.
