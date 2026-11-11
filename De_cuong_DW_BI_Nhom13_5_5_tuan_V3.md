# ĐỀ CƯƠNG TRIỂN KHAI KHO DỮ LIỆU VÀ BUSINESS INTELLIGENCE — NHÓM 13

**Môn học:** Kho dữ liệu và Kinh doanh thông minh (MI4214)  
**Đề tài:** Xây dựng kho dữ liệu và hệ thống Business Intelligence hỗ trợ phân tích quy mô, cơ cấu và biến động nhân sự tại các cơ quan liên bang Hoa Kỳ  
**Lĩnh vực:** HR Management / Federal Workforce Analytics  
**Quy mô nhóm:** 5 thành viên  
**Thời gian:** 5,5 tuần (~39 ngày kể từ khi khởi động)  
**Mục tiêu:** Hoàn chỉnh nguồn dữ liệu → mô hình nguồn quan hệ → Staging/ODS → Data Warehouse → Data Mart → Power BI; chuẩn bị đầy đủ minh chứng cho 11 tiêu chí đánh giá, phấn đấu 4,5–5/5 ở từng mục.

> **Nguyên tắc:** Kết quả thực nghiệm phải xuất phát từ dữ liệu thật, có lệnh và bằng chứng tái lập. Mô hình do nhóm tái cấu trúc từ OPM/EHRI không được trình bày là hệ thống OLTP sản xuất của OPM. Các PK/FK nghiệp vụ chỉ được tuyên bố sau khi kiểm định. Không tạo nhân viên, hồ sơ, giao dịch hay lịch sử cá nhân giả.

## 1. Phạm vi, dữ liệu và mục tiêu phân tích

### 1.1. Dữ liệu đầu vào

Bộ dữ liệu sử dụng gồm 12 file Parquet OPM/EHRI về nhân sự liên bang Hoa Kỳ, giai đoạn tháng 03–06/2025, dung lượng khoảng **301,5 MB**. Theo kiểm kê ban đầu:

| Nhóm dữ liệu | Số file | Tổng số dòng | Vai trò |
|---|---:|---:|---|
| Employment | 4 | 9.057.997 | Snapshot nhân sự theo từng tháng |
| Accessions | 4 | 30.782 | Bản ghi tiếp nhận nhân sự |
| Separations | 4 | 92.511 | Bản ghi rời cơ quan |
| **Tổng** | **12** | **9.181.290** | Không phải 9,18 triệu nhân viên khác nhau |

Tài liệu giảng viên ghi “Lớn hơn 100M”. Nhóm đang dự trù theo **100 MB** và dataset vượt ngưỡng MB này; chưa có bằng chứng xác nhận riêng cách hiểu “100M”. Không suy rộng sự đồng ý về ERD thành xác nhận ngưỡng dữ liệu. Các trường mã và tên xuất hiện trong dữ liệu bao gồm những nhóm như `agency_code`, `department_code`, `agency_subelement_code`, `occupational_series_code`, `occupational_group_code`, `duty_station_code`, `pay_plan_code`, `grade`. Employment có kỳ snapshot; các file sự kiện có kỳ báo cáo và kỳ hiệu lực hành động. Không có khóa `employee_id` công khai để liên kết một người qua ba họ dữ liệu.

**Chốt baseline:** 12 file trong ZIP, ghi đầy đủ tên file, tháng, source version, số byte, số dòng, schema, SHA-256 vào `docs/03_source_inventory.csv`. Giữ nguyên raw files; không pha trộn bản phát hành khác nhau trong cùng một kết quả mà không có quy tắc version. Những số đếm `REDACTED` và lệch kỳ chỉ được nêu ở báo cáo sau khi chạy script kiểm chứng.

### 1.2. Phạm vi bài toán và câu hỏi quản trị

- **D1 — Workforce Overview:** quy mô nhân lực cuối tháng; cơ cấu theo cơ quan, nghề nghiệp, địa lý, cấp bậc và nhóm phân loại thực sự tồn tại.
- **D2 — Personnel Flows:** số lượt Accessions/Separations theo kỳ báo cáo, cơ quan, nhóm nghề nghiệp và loại hành động nhân sự.
- **D3 — Workforce Changes & OLAP:** mức thay đổi headcount giữa hai kỳ, nhóm tăng/giảm mạnh, phân tích drill-down trên các phân cấp đã xác minh.

Kết quả phục vụ công tác phân tích và lập báo cáo nhân lực, **không** phải hệ thống HRMS quản lý từng nhân viên. Người dùng dự kiến là chuyên viên phân tích nhân sự và người hoạch định nhân lực liên bang; đây là persona thiết kế, không phải khách hàng thực tế đã tham gia đề tài.

### 1.3. Những điều không được suy diễn

1. Employment là snapshot: headcount tính cho **một kỳ**, không cộng bốn tháng để suy ra số người khác nhau.
2. Accessions và Separations là các bản ghi sự kiện công khai; không tự nối từng dòng để xác định cùng một nhân viên.
3. Chênh lệch headcount giữa hai tháng **không mặc nhiên bằng** Accessions trừ Separations do khác thời điểm và phạm vi.
4. Cần lưu **report month** và **effective month** riêng biệt cho sự kiện.
5. `REDACTED` là dữ liệu bị che; không được chuyển thành 0 hay tự điền giá trị suy đoán.
6. Bốn tháng chỉ phù hợp so sánh MoM, không đủ kết luận mùa vụ năm hoặc dự báo dài hạn đáng tin cậy.
7. Sự tương quan giữa hai biến phân loại không chứng minh có khóa ngoại giữa hai bảng dữ liệu.
8. `source_record_key` kỹ thuật, nếu tạo, chỉ dùng truy vết dòng tệp; **không phải employee_id**.

## 2. Những rủi ro cần xử lý dứt điểm

| ID | Tình trạng | Vấn đề | Hành động cụ thể | Người/hạn | Nếu không đạt |
|---|---|---|---|---|---|
| **R01** | Đã chấp thuận theo xác nhận TV1 ghi nhận 11/11/2026; chưa có ảnh gốc | Giữ ERD mô hình nguồn quan hệ tái cấu trúc cho mục ERD OLTP; không gọi là OLTP gốc OPM | Lưu nguồn xác nhận; TV2/TV3 tiếp tục kiểm khóa, quan hệ và mapping | TV1 ghi nhận; TV2/TV3 xây và kiểm theo lịch | Chỉ trao đổi lại với thầy nếu đổi phương án hoặc nội dung chấp thuận khác; không dựng quan hệ giả |
| **R02** | Cần thử | Quyền Power BI Publish to web | TV4 thử dashboard chỉ chứa dữ liệu tổng hợp, TV5 truy cập ẩn danh | Ngày 1–4 | Xin quyền admin hoặc phương án thay thế được thầy chấp thuận |
| **R03** | Cần kiểm chứng | Mã Agency, Occupation, Duty Station, Pay Plan có đủ điều kiện làm PK/FK không | Dùng codebook OPM, kiểm uniqueness, key scope, orphan và mã quá khứ | TV2–TV3, ngày 8–12 | Không ép relationship sai; đưa ngoại lệ vào bảng QA |
| **R04** | Cần kiểm chứng | Version/file/schema drift | Lưu checksum và metadata; chỉ dùng 12 file baseline | TV2, ngày 3 | Cách ly file/version khác khỏi baseline |
| **R05** | Cần đo | Hơn 9 triệu dòng có thể nặng khi nạp và làm dashboard | Pilot ingest, đo, dùng chunking/mart aggregate | TV3–TV5, ngày 12–17 | Tối ưu indexing/aggregation; không cắt bản ghi để đẹp kết quả |
| **R06** | Hạn chế dữ liệu | 4 tháng, REDACTED, kỳ file khác kỳ hiệu lực | KPI Dictionary, EDA và chú giải công khai | TV1–TV2, ngày 10 | Không làm KPI/nhận định ngoài khả năng dữ liệu |
| **R07** | Cần rà soát hành chính | Mã học kỳ và lịch báo cáo trong nguồn hướng dẫn khác lịch nhóm hiện tại | Kiểm thông báo thầy và cách nộp hiện hành | TV1, ngày 3 | Lấy yêu cầu hiện hành làm chuẩn |
| **R08** | Cần kiểm thử | Public Power BI model có thể lộ dữ liệu bản ghi | Tạo semantic model công khai riêng từ mart tổng hợp, thử export và quyền xem | TV4–TV5, ngày 25 | Không công bố raw/ODS, xin duyệt phương án khác |

**Cập nhật R01:** thầy đã đồng ý phương án ERD nguồn quan hệ tái cấu trúc, theo xác nhận trưởng nhóm được ghi nhận ngày 11/11/2026. [Nguồn ghi nhận](evidence/TV1_week1/R01_confirmation.md) chưa có ảnh/tin nhắn gốc và không ghi ngày thầy trả lời. Không cần hỏi lại nếu phương án giữ nguyên; TV2/TV3 vẫn phải kiểm chứng khóa, ERD và mapping. C04 chưa được nghiệm thu.

## 3. Đối chiếu 11 tiêu chí giảng viên chấm

| Mã | Tiêu chí | Minh chứng hướng tới mức 4,5–5/5 | Chủ trì |
|---|---|---|---|
| C01 | Quy trình nghiệp vụ | Quy trình HR phù hợp bối cảnh OPM, vai trò, cây nghiệp vụ, điểm phân tích A#, KPI/nguồn ở từng bước | TV1 |
| C02 | Requirement | Persona, FR/NFR, mô hình quản trị, cây yêu cầu và ba cây dashboard, KPI Dictionary | TV1 |
| C03 | Hệ thống/quy mô dữ liệu | Inventory >100 MB, taxonomy với dữ liệu thật, Data Dictionary, nguồn và data flow OPM | TV2 |
| C04 | ERD OLTP | ERD mô hình nguồn quan hệ có PK/FK kiểm chứng, audit, mapping sang OLAP, giải thích phạm vi, phản hồi thầy | TV2 + TV3 |
| C05 | Data Exploration | DQ, Pareto, đặc trưng, Chi-square/Cramér’s V, trend ngắn hạn, phép đo có giải thích | TV2 |
| C06 | Kiến trúc DW | Architecture thành phần và deployment riêng biệt với luồng ETL, công nghệ đúng thực tế | TV3 |
| C07 | ETL | Job list, pipeline, before–after, đối soát, idempotence, log/errors, chạy full 12 file | TV3 |
| C08 | Dimension | Dimension catalog, số dòng, khóa, grouping, hierarchy có căn cứ, mẫu thật | TV4 + TV3 |
| C09 | Data Model OLAP | Fact grain, bus matrix, logic model và **physical overall ERD**, Data Mart DDL, OLAP demo | TV4 + TV3 |
| C10 | Dashboard | 3 dashboard kể câu chuyện phân tích, DAX, cảnh báo, slicer/drill/tooltip, public, đối soát SQL | TV4 |
| C11 | Tổng kết | Benchmark có số đo và điều kiện đo, bài học, limitations, báo cáo/demo | TV5 |

Các mức điểm 4,5–5 là mục tiêu nhóm tự đặt, không phải kết quả chấm được bảo đảm. Nền tảng học tập từ bài nhóm 6 và 10 là **giữ mô hình Dimension/OLAP đúng về ngữ nghĩa và có bằng chứng**, không chỉ thêm công nghệ hoặc slide.

## 4. C01 — Bài toán nghiệp vụ

**Hai quy trình cần mô tả:** (i) đo quy mô/cơ cấu nhân lực theo snapshot; (ii) phân tích tiếp nhận và rời cơ quan. Mô tả có sự phân biệt giữa quy trình các cơ quan nộp dữ liệu lên OPM được tài liệu hóa và quy trình phân tích do nhóm thiết kế. Không đưa tác vụ nội bộ OPM chưa có nguồn xác minh như thể đã khảo sát trực tiếp.

**Điểm phân tích phải map sang dữ liệu:**

| Điểm | Bước | Kết quả cần đo | Nguồn | Dashboard |
|---|---|---|---|---|
| A01 | Nhận file theo kỳ | Số file, version, dung lượng | Manifest | DQ |
| A02 | Kiểm tra chất lượng | Missing/REDACTED/schema drift | 3 họ file | DQ |
| A03 | Xác thực mã | Code coverage, orphan | Các `_code`, OPM dictionary | DQ |
| A04 | Nạp snapshot | Monthly headcount | Employment | D1 |
| A05 | Phân tích cơ cấu | Tỷ trọng theo nhóm | Employment | D1 |
| A06 | Tiếp nhận | Accessions count | Accessions | D2 |
| A07 | Rời cơ quan | Separations count | Separations | D2 |
| A08 | So sánh kỳ | Headcount MoM, event difference | Các Fact tương ứng | D3 |
| A09 | Đối soát | KPI SQL–DAX | Data Mart + Power BI | QA |
| A10 | Tổng hợp insight | Insight và giới hạn | D1–D3 | Báo cáo |

**Bàn giao:** `docs/01_business_scope.md`, `diagrams/01_business_process.drawio`, `diagrams/01_business_tree.drawio`, `docs/01_touchpoint_mapping.csv`; mỗi điểm A# có nguồn, trường, KPI, Dimensions và cách kiểm chứng. Có một ví dụ trình bày xuyên suốt bước nghiệp vụ → dữ liệu → Fact/Dim → Mart → dashboard.

## 5. C02 — Yêu cầu phân tích và KPI

**FR:** nhập dữ liệu theo kỳ; phân tích quy mô, cơ cấu và hành động nhân sự; lọc theo cơ quan/nghề nghiệp/kỳ; drill-down ở phân cấp có cơ sở; đối soát và xuất kết quả. **NFR:** có khả năng chạy lại, log, xử lý >100 MB Parquet, không mất dòng khi lookup, trả số liệu nhất quán, hạn chế public model và đo hiệu năng.

**Tài liệu:** `docs/02_requirements.md`, `docs/02_kpi_dictionary.csv`, cây tổng quan yêu cầu, ba cây D1–D3.

| KPI | Công thức/ý nghĩa | Điều kiện |
|---|---|---|
| K01 Monthly Headcount | COUNT bản ghi Employment trong **một** snapshot kỳ được chọn | Không `DISTINCT employee_id` |
| K02 Headcount Change | HC(t) − HC(t−1) | Thiếu tháng trước → BLANK |
| K03 Headcount MoM | [HC(t) − HC(t−1)] / HC(t−1) | Mẫu số bằng 0/thiếu → BLANK |
| K04 Agency Share | HC(agency,t) / HC(all agencies,t) | Cùng kỳ và nhất quán với slicer |
| K05 Group Share | HC(group,t) / HC(all groups,t) | Theo một kỳ, không cộng bốn kỳ |
| K06 Accessions Count | COUNT dòng Accessions theo một vai trò tháng | Ghi rõ report/effective month |
| K07 Separations Count | COUNT dòng Separations theo một vai trò tháng | Như K06 |
| K08 Event Difference | Accessions Count − Separations Count | **Không** gọi net headcount |
| K09 Growth/Decline | Xếp hạng HC(t) − HC(t−1) theo nhóm | Kiểm điều kiện nhóm thiếu ở một kỳ |
| K10 DQ Coverage | matched / eligible | Tách Unknown và REDACTED |

KPI turnover rate chỉ thêm nếu giải thích được mẫu số headcount, kỳ đo và tính tương thích của phạm vi. Không mặc định Accession/Separation là lịch sử một người.

## 6. C03 — Nguồn dữ liệu, taxonomy, Data Dictionary

Tạo inventory 12 file với `family, month, version, filename, size_bytes, row_count, schema_hash, sha256, downloaded_at, source_url`. Tạo cây Data Taxonomy: (A) Employment snapshots; (B) Accessions events; (C) Separations events; (D) reference/codebook; (E) technical metadata. Mỗi nhánh phải có vài dòng dữ liệu **thật** trích từ file.

Data Dictionary từng trường dùng trong mô hình phải có `field_name, data_type, business_definition, code_domain, example_real_value, missing_pct, redacted_pct, source_reference, target_table, reviewer, verification_status`. Nếu nghĩa trường chưa chắc chắn, ghi `uncertain` chứ không suy luận.

**Nguồn chính thức để tra cứu:**
- OPM FWD downloads: https://data.opm.gov/get-data/data-downloads
- EHRI standards: https://data.opm.gov/data-standards/ehri-data-standards
- EHRI validation checks: https://data.opm.gov/data-standards/ehri-data-validation-checks
- Data sources và nguồn công bố: https://data.opm.gov/resources/data-sources
- OPM API / metadata: https://data.opm.gov/get-data/api-access

Sơ đồ data flow hệ thống nguồn nêu những thành phần có bằng chứng: cơ quan liên bang → EHRI submission/processing → OPM Federal Workforce Data → Parquet của nhóm. Mỗi mũi tên ghi **dữ liệu được truyền**, không đặt tên động tác chung chung. Phân biệt luồng thật theo OPM với pipeline do nhóm tự triển khai.

## 7. C04 — ERD nguồn quan hệ, Staging và ODS

### 7.1. Mục tiêu và giới hạn

Thiết kế **ERD mô hình nguồn quan hệ được tái cấu trúc từ dữ liệu OPM/EHRI công khai**, không gọi là bản sao OLTP giao dịch gốc. Đặc biệt, không phát minh bảng Employee/employee_id rồi nối ba nguồn để tạo lịch sử cá nhân.

### 7.2. Mô hình quan hệ dự kiến

| Bảng | Vai trò | PK/FK dự kiến |
|---|---|---|
| `source_file` | Manifest bản file | `file_id` kỹ thuật, khóa định danh theo file/version/checksum |
| `ods_employment_record` | Mỗi dòng snapshot Employment | `source_record_key` kỹ thuật; FK `file_id`; mã nghiệp vụ đã kiểm |
| `ods_accession_record` | Mỗi dòng Accessions | `source_record_key`; FK `file_id`; các mã hành động |
| `ods_separation_record` | Mỗi dòng Separations | `source_record_key`; FK `file_id`; các mã hành động |
| `ref_agency` | Mã cơ quan | PK theo mã hoặc mã ghép đúng phạm vi |
| `ref_agency_subelement` | Mã đơn vị thành phần | Key và parent relation nếu standard xác nhận |
| `ref_occupation_series` | Mã nghề nghiệp | Key/hierarchy nếu mapping chính thức hợp lệ |
| `ref_duty_station` | Mã nơi làm việc | Key và địa lý nếu chuẩn mã xác minh |
| `ref_pay_plan` | Mã kế hoạch lương/bậc | Chỉ gắn Grade khi có đủ ngữ cảnh |
| `audit.load_run`, `audit.dq_issue` | Log pipeline | ID kỹ thuật, file/run refs |

Các bảng `ref_*` là **dự kiến**, chỉ được tạo quan hệ FK sau kiểm tra. Không cần tạo bảng tham chiếu cho mọi trường có hậu tố `_code`.

### 7.3. Phép kiểm chứng khóa

Cho mỗi quan hệ dự kiến phải có: nguồn định nghĩa; phạm vi mã (global hay trong một department); số mã khác nhau; số label cho mỗi code và kỳ; kiểm Null/REDACTED; orphan code và orphan rows; kiểm lịch sử/phiên bản chuẩn; quy tắc Unknown. Trạng thái relationship gồm `VERIFIED / PARTIAL / UNSUPPORTED`.

Không JOIN trực tiếp Employment với Accessions hoặc Separations theo `agency_code` để tạo quan hệ từng nhân viên. Các bảng có thể dùng chung Dimension trong DW và được so sánh ở mức tổng hợp có grain phù hợp.

### 7.4. Phân lớp và mapping

`Raw Parquet + metadata → Staging (giữ trường gốc) → verified reference & ODS (3 dòng nguồn + lineage + DQ flag) → DW Fact/Dim → Data Mart → Power BI`.

| Source | Target | Quy tắc |
|---|---|---|
| Tên file và SHA-256 | `source_file`, `report_month` | Một source file theo family/tháng/version, tránh nhân bản |
| Employment `snapshot_yyyymm` | `dim_month`, Fact snapshot month | Một kỳ snapshot, đúng `YYYYMM` |
| Event `personnel_action_effective_date_yyyymm` | Fact effective month | Không ghi đè kỳ file |
| `agency_code`, `agency` | `ref_agency` → `dim_agency` | Code→label đã kiểm, join không nhân dòng |
| `occupational_series_code` | `dim_occupation` | Mã nhóm/series theo chuẩn có thời kỳ phù hợp |
| `duty_station_code` | `dim_location` | Unknown nếu unmapped, có DQ log |
| `pay_plan_code` + `grade` | `dim_grade` | Có thể cần khóa ghép; không giả định một thang Grade chung |
| Action category codes | `dim_accession_category`/`dim_separation_category` | Mapping đúng định nghĩa từng họ sự kiện |

**Bàn giao:** `diagrams/04_relational_source_erd.drawio`, `diagrams/03_opm_source_flow.drawio`, `docs/04_relationship_audit.csv`, `docs/04_source_to_target_mapping.csv`, `sql/00_raw_ref_ods_ddl.sql`, `sql/tests/04_fk_audit.sql`. Trình bày ngay trong phần khảo sát/thiết kế nguồn của báo cáo.

**Điều kiện C04:** ERD có khóa/quan hệ được kiểm chứng, rõ khác biệt OLTP gốc/ODS; có phản hồi thầy đồng ý hoặc trạng thái R01 chưa đóng.

## 8. C05 — Khám phá dữ liệu và phương pháp thống kê

1. Thống kê quy mô, cột, type, số mức danh mục, tỷ lệ missing/REDACTED theo file/kỳ.
2. Data Quality theo các chiều đầy đủ, hợp lệ, nhất quán, duy nhất theo đúng grain, toàn vẹn tham chiếu, bất thường, kịp thời; không gán `employee_id`.
3. Phân bố, histogram (với biến số có nghĩa), Pareto của headcount/agency và các action categories.
4. Quan hệ biến phân loại: bảng chéo Agency × Occupation, Occupation × Grade, Agency × Location trên **một snapshot** trước khi mở rộng. Dùng Chi-square và Cramér’s V; không dùng Pearson trực tiếp với mã danh mục.
5. Trình bày công thức `Eij = row_total_i × col_total_j / N`; `χ² = Σ (Oij−Eij)^2/Eij`; `V = sqrt(χ²/[N×min(r−1,c−1)])`. Kèm một ví dụ ô tính từ dữ liệu thật, kiểm expected counts và giải thích ý nghĩa effect size.
6. Thời gian: biểu đồ tháng 03–06/2025, MoM, nhóm biến động; không kết luận mùa vụ năm, nhân quả hay forecast đáng tin từ 4 kỳ.
7. Trước/sau xử lý: `REDACTED`, mã orphan, kỳ report/effective khác nhau, không xóa các dòng giống nhau chỉ vì nội dung trùng khi không có business key.

**Bàn giao:** `notebooks/01_eda.ipynb`, `reports/05_data_quality.csv`, `reports/05_eda_findings.md`, `reports/05_charts/`, `sql/tests/05_dq_checks.sql`.

## 9. C06 — Kiến trúc Data Warehouse

**Stack mục tiêu:** Python + PostgreSQL + SQL + Power BI Desktop (Windows). DuckDB hỗ trợ đọc/khảo sát Parquet nếu thực sự cần; không đưa thêm Kafka, Spark, Airflow, Lakehouse hoặc LLM vào sơ đồ khi chưa triển khai.

Tách riêng **hai sơ đồ**:
- `diagrams/06_architecture_components.drawio`: thành phần ứng dụng, máy triển khai, file storage, DB, Python ETL, Power BI, kết nối, công nghệ/logo thực dùng.
- `diagrams/06_etl_data_flow.drawio`: J00–J06 theo đúng thứ tự, từ file tới bảng nguồn/đích, lỗi DQ, batch/run_id, dữ liệu đi trên mũi tên.

Tầng PostgreSQL có thể gồm `raw_meta`, `staging`, `ref`, `ods`, `dw`, `mart`, `audit`. Mỗi thành phần phải chỉ ra một bảng, tệp, script hoặc ảnh chụp kết quả thực thi để kiểm chứng.

## 10. C08–C09 — Dimension, Fact và OLAP

### 10.1. Dimension catalog

| Nhóm | Dim mục tiêu | Quy tắc |
|---|---|---|
| Thời gian | `dim_month` | `YYYYMM`, report/effective là hai vai trò riêng |
| Tổ chức | `dim_agency` | Agency/department/subelement chỉ phân cấp nếu audit hợp lệ |
| Nghề nghiệp | `dim_occupation` | Group → series theo chuẩn mã |
| Địa lý | `dim_location` | Duty station và phân cấp geographic được xác minh |
| Cấp bậc | `dim_grade` | Pay plan + grade khi có ngữ cảnh |
| Nhân khẩu học | `dim_age_bracket` | Dải tuổi hiện có, không tạo DOB/tuổi cụ thể |
| Hành động | `dim_accession_category`, `dim_separation_category` | Mã loại hành động thuộc từng dataset |

Mỗi Dimension có tên, grain, natural key, surrogate key, số dòng, 2–3 ví dụ dữ liệu thật, Unknown rule, nguồn codebook, hierarchy đã kiểm và Fact dùng. Đừng ép tất cả Dimension vào mọi Fact. Nếu mapping tên mã đổi giữa các kỳ, ghi rõ phương án xử lý version.

### 10.2. Grain của ba Fact

| Fact | Grain | Lưu ý |
|---|---|---|
| `fact_employment_snapshot` | Một dòng công khai Employment trong một snapshot | Measure `record_count=1`; semi-additive theo tháng |
| `fact_accessions` | Một dòng Accessions | `event_count=1`; report/effective month riêng |
| `fact_separations` | Một dòng Separations | `event_count=1`; không nối sự kiện với nhân viên |

**Bus matrix**: bảng hàng gồm 3 Fact, cột gồm Dim; chú thích Shared/Only-this-fact/Unavailable. Mỗi Fact phải có PK/truy vết nguồn và các FK Dimension hợp lệ. Không có FK nối ba Fact trực tiếp.

**Các mô hình phải có:** (i) ERD nguồn/ODS, (ii) DW logical schema, (iii) DW **physical overall** với đầy đủ bảng/PK/FK/index, (iv) Data Mart physical và SQL tạo bảng/view, (v) Power BI semantic model có quan hệ và hướng filter. Đối chiếu mọi hình với DDL đang chạy.

### 10.3. Data Mart tối thiểu

| Mart | Grain | KPI chính |
|---|---|---|
| `mart.workforce_monthly` | Tháng snapshot × cơ quan × nhóm nghề/địa lý/cấp bậc đã chốt | Headcount, tỷ trọng, MoM |
| `mart.personnel_flows_monthly` | Tháng báo cáo × cơ quan × họ hành động × category | Accessions, Separations, event difference |

Không JOIN thẳng hai Fact sự kiện trên month + agency vì nhân số dòng. Tổng hợp từng Fact tới cùng grain rồi UNION ALL hoặc join các bảng **đã tổng hợp**. Không gọi Data Mart là bản sao nguyên xi của Fact.

## 11. C07 — ETL và đối soát

| Job | Đầu vào | Đầu ra | Điều kiện pass |
|---|---|---|---|
| J00 — Inventory | 12 Parquet | File manifest/checksum/log | Đủ 12 file, đúng version |
| J01 — Stage | Raw Parquet | 3 bảng Staging | Row count theo file khớp nguồn |
| J02 — Validate & Normalize | Staging + official reference | 3 ODS + DQ issues | Bảo toàn raw, không mất dòng ngoài quy tắc |
| J03 — Build Dimensions | ODS + ref đã kiểm | `dw.dim_*` | Natural key unique theo scope, Unknown hợp lệ |
| J04 — Load Facts | ODS + Dim | 3 Fact | Không nhân dòng khi JOIN |
| J05 — Build Marts | Facts | 2 Data Mart | Tổng hợp theo đúng grain |
| J06 — Reconcile | Tất cả tầng | Audit/CSV | Source → ODS → Fact → Mart → KPI khớp |

Lưu `run_id`, filename, checksum/version, rows_read/written/rejected, duration, status, errors và DQ flags. Thử nạp tháng 03→06 và chạy lại tháng 05: kết quả cuối không nhân bản. Khi tệp được republish, quản lý phiên bản tại cấp file; không cộng chồng hai version cùng kỳ.

**Before–after tối thiểu:** (1) `REDACTED` giữ cờ/Unknown; (2) tháng file khác tháng hiệu lực được bảo tồn; (3) code nguồn → verified ref → surrogate key; có ảnh/chạy SQL trước sau.

**Test tối thiểu:** 12 file/checksum; row counts theo family; 3 Fact; 2 Mart; PK/FK; no-orphan hoặc exception; rerun/idempotence; report/effective; 10 trường hợp SQL–DAX; zero/blank denominator; benchmark ba lần/biến thể; public model không lộ record-level.

## 12. C10 — Dashboard & OLAP

| Dashboard | Mục tiêu | Tương tác/bài demo |
|---|---|---|
| D1 Workforce Overview | Headcount, tỷ trọng, MoM, cơ cấu | Slicer kỳ/cơ quan, drill theo hierarchy đã xác minh |
| D2 Personnel Flows | Accessions/Separations theo tháng/category/agency | Slicer kỳ report, tooltip effective month, KPI rõ đơn vị |
| D3 Workforce Changes & OLAP | Top tăng/giảm headcount, heatmap theo nhóm | Drill-through agency → occupation/grade; cảnh báo DAX |

Mỗi trang có **storytelling**: bối cảnh → câu hỏi → thao tác lọc → biểu đồ bằng chứng → insight → hành động kiểm chứng tiếp. Đưa đơn vị người/lượt/%, dấu ngăn nghìn, tháng snapshot/report/effective và chú giải BLANK/0. Có ít nhất hai ví dụ conditional formatting/threshold đặt bởi nhóm và nêu rõ đó không phải chuẩn OPM.

**Công bố:** thử Publish to web trong tuần 1; khi public thật, sử dụng semantic model riêng chỉ có mart tổng hợp phù hợp, không đưa raw/ODS hoặc bảng mức bản ghi công khai. TV5 xác minh mở bằng trình duyệt ẩn danh và kiểm giới hạn export. Nếu không được cấp quyền, xin thầy phương án thay thế **trước** kỳ bảo vệ.

## 13. C11 — Hiệu năng, bài học và báo cáo

Benchmark một cặp truy vấn tương đương (từ Fact vs từ Mart tổng hợp, hoặc trước/sau index) tối thiểu **3 lần mỗi phương án**, ghi DB, CPU/RAM, số dòng, SQL, `EXPLAIN ANALYZE`, median, warm/cold cache nếu kiểm soát được. Đo thêm thời gian ETL full 12 file và rerun; không tuyên bố cải thiện khi chưa có bằng chứng số.

**Cấu trúc báo cáo:**
1. Bìa, danh sách 5 người, phiếu đánh giá có chữ ký, mục lục.
2. **Phần I — Tổng quan về Data Warehouse:** khái niệm, OLTP/OLAP, ODS, ETL, architecture, Data Mart.
3. **Phần II — Tổng quan về Business Intelligence:** KPI, OLAP, DAX, Power BI, dashboard phục vụ ra quyết định.
4. **Phần III — Ứng dụng vào bài toán HR:** nghiệp vụ/requirement; nguồn OPM và Data Dictionary; ERD nguồn; EDA; kiến trúc; ODS/DW/Mart logic và vật lý; ETL/tests; Dimensions/OLAP; D1–D3; benchmark; bài học và giới hạn.
5. Kết luận, tài liệu tham khảo, phụ lục SQL/ảnh; trình bày Times New Roman 12, căn đều, số trang và hình/bảng có tiêu đề.

**Bảo vệ:** 30–45 phút, lựa chọn lịch 40 phút: TV1 5'; TV2 11' (nguồn/ERD/EDA); TV3 9' (architecture/ETL); TV4 11' (OLAP/BI); TV5 4' (benchmark/QA). Mọi thành viên phải trả lời được câu hỏi về grain, khóa, giới hạn nguồn và KPI.

**Hướng mở rộng:** chỉ khi P0/P1 hoàn thành. Ưu tiên một automation nhỏ (kiểm metadata và xuất Data Quality report theo tháng); không ôm Kafka, Lakehouse, ML, AI Copilot hoặc seasonal forecast từ 4 tháng.

## 14. Lộ trình 5,5 tuần

| Mốc | Ngày | Công việc và tiêu chuẩn qua cổng |
|---|---|---|
| G0 | 1–5 | Thầy xác nhận hoặc ghi rõ R01 chưa phản hồi; test Publish to web; kiểm mã nguồn và version |
| G1 | 6–7 | Business scope/KPI v0, inventory, Data Dictionary, môi trường DB |
| G2 | 8–14 | Verified ERD + mapping; EDA, bus matrix, DDL; **MVP ba họ nguồn → Mart → một KPI Power BI** |
| G3 | 15–21 | Nạp đủ 12 file, 3 Fact, 2 Mart, Dim audit và rerun pass |
| G4 | 22–28 | 3 dashboard v1, SQL–DAX test, OLAP interaction và benchmark baseline |
| G5 | 29–35 | Fix, benchmark after, public/approved alternative, báo cáo/slide, đủ evidence C01–C11 |
| G6 | 36–39 | Hai lần tổng duyệt, bàn giao DB dump/scripts, `.pbix`, báo cáo, slide, phiếu ký |

**Ưu tiên P0:** nguồn/ERD đúng; DW/ETL hoạt động; 3 Fact; 2 Mart; 3 dashboard; đối soát và báo cáo theo hướng dẫn.  
**P1:** official codebook, categorical statistics, idempotence, storytelling, benchmark, public-safe BI.  
**P2:** mở rộng nguồn/kỳ/automation, nếu còn thời gian và không làm trễ P0/P1.

## 15. File bàn giao và ma trận tự nghiệm thu

```text
DW_BI_Group13/
├── README.md
├── docs/              # business scope, requirements, KPI, dictionary, inventory, mappings
├── diagrams/          # BPMN, source ERD, architecture, DW/DM physical models
├── data/manifest/     # file list, checksum, versions
├── data/reference/    # OPM standards/codebook with provenance
├── configs/           # config templates, no secrets
├── notebooks/         # EDA
├── etl/               # J00–J06 + runbook
├── sql/               # schema, Fact/Dim/Mart DDL, checks
├── tests/             # data, integration and KPI tests
├── reports/           # DQ, reconciliation, benchmark
├── powerbi/           # .pbix and public model instructions
├── evidence/C01..C11/ # images, query outputs, logs
└── deliverables/      # report, slides, member evaluation
```

| Tiêu chí | Điều kiện tự nghiệm thu |
|---|---|
| C01 | Điểm A# gắn KPI và bảng nguồn, có sơ đồ nghiệp vụ có cơ sở |
| C02 | Có KPI Dictionary, cây requirement và D1–D3, câu hỏi thực tế |
| C03 | 12 file >100 MB, metadata và taxonomy có ví dụ thật, dictionary có reviewer |
| C04 | Source relational ERD, audit PK/FK, mapping, khác biệt với OLTP gốc và trạng thái phản hồi thầy rõ |
| C05 | DQ, Pareto, categorical association có công thức, MoM có giới hạn |
| C06 | Architecture, deployment, ETL dataflow là các sơ đồ phân biệt |
| C07 | Full pipeline, before/after, tests, logs, idempotence |
| C08 | Dimension catalog, row counts, hierarchy đã kiểm chứng |
| C09 | Bus matrix, DW logical + physical **overall**, Mart DDL, Fact grain |
| C10 | 3 dashboard, DAX/OLAP/story, SQL reconciliation, publication thực tế |
| C11 | Benchmark công bằng, hạn chế, tổng kết và hồ sơ bảo vệ |

**Lưu ý hiện trạng:** R01 đã được chấp thuận theo xác nhận TV1; không còn coi là chưa hỏi thầy. Sự chấp thuận không thay kết quả kiểm khóa và nghiệm thu C04.

**Định nghĩa DONE:** Có file thành phẩm, hướng dẫn chạy, bằng chứng từ dữ liệu thật, người review và kết quả kiểm thử. **R01 chưa được thầy chấp thuận thì không được khẳng định C04 đã chính thức đạt.**

## Cập nhật gói bàn giao TV1

Ngày 11/11/2026: giữ 12 file OPM; chốt mở rộng tự phát hiện/nạp kỳ mới và kiểm chất lượng sau MVP. Phân tích lệch tháng báo cáo–hiệu lực chỉ dự kiến. Chưa triển khai ETL/DB/BI. Xem [phạm vi hiện hành](docs/00_scope_decisions.md), [bảng việc](docs/00_task_board.md) và [TV2 bắt đầu từ đây](docs/00_handoff_tv1_tv2.md). Các đầu việc TV1 có sản phẩm ở trạng thái REVIEW, không tự ghi DONE/PASS.
