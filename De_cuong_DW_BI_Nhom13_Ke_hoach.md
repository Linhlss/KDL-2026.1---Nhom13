# ĐỀ CƯƠNG CHI TIẾT & TIÊU CHUẨN NGHIỆM THU ĐỀ TÀI DW & BI — NHÓM 13

**Môn học:** Kho dữ liệu và Kinh doanh thông minh (MI4214)  
**Nhóm:** 13 — 5 thành viên  
**Tên đề tài:** **Xây dựng kho dữ liệu và hệ thống Business Intelligence hỗ trợ phân tích quy mô, cơ cấu và biến động nhân sự tại các cơ quan liên bang Hoa Kỳ**  
**Domain:** Human Resources Management (HR Management)  
**Tuần trình bày dự kiến:** Tuần 16  
**Mục tiêu nội bộ:** phấn đấu **4,5–5/5 ở từng tiêu chí** của bảng chấm thầy sử dụng; đây là chuẩn tự nghiệm thu, **không phải cam kết/tiêu chí chính thức quy đổi điểm**.

> **Cách đọc tài liệu:** **[GV]** = yêu cầu/đề nghị ghi trực tiếp trong file hướng dẫn môn học; **[BÀI 6]** = cách nhóm 6 đã triển khai trong tài liệu mẫu, chỉ dùng tham khảo; **[NHÓM 13]** = thiết kế/chuẩn nghiệm thu do nhóm tự đề xuất. Tất cả số liệu kết quả chạy pipeline/dashboard phải được tạo từ dataset gốc, không điền trước theo suy đoán.

## 0. Căn cứ và nguyên tắc

**Căn cứ:** (1) `Hướng dẫn môn học - DW & BI 20252.xlsx`, các sheet `MI4214-Nội dung`, `Đánh giá-MI4214`, `Hướng dẫn bài tập nhóm`, `Nội dung báo cáo`, `Đánh giá thành viên nhóm`; (2) hình bảng chấm nhóm 6; (3) `DWH-Nhom6.pdf` và `DWH-Nhom6.pptx`; (4) `Group13_HR_Management_Dataset.zip`; (5) `Bao_cao_tom_tat_de_tai_DW_BI_Nhom13.md`.

**Phân biệt yêu cầu và gợi ý của thầy:** [GV] Có hệ thống DW/BI, làm việc với dữ liệu lớn và performance, trình bày quy trình nghiệp vụ → yêu cầu → dữ liệu nguồn → ERD/OLTP → EDA → kiến trúc → ETL → Dimension → mô hình OLAP → KPI → Dashboard → bài học; dùng Power BI, sử dụng được hệ quản trị CSDL, có dashboard public trên website; làm slide/báo cáo 30–45 phút và báo cáo cuối kỳ đúng biểu mẫu. [GV] Hướng dẫn có đề nghị đa dạng công cụ như R, Excel Data Analysis, Python, SQL và Power Query; **không quy định phải sử dụng đồng thời tất cả**, không ấn định số Fact/Dimension/dashboard. SQL Server/Oracle là ví dụ công nghệ. Chuyên đề Lakehouse/AI là mở rộng, không được đồng nhất với điều kiện bắt buộc.

**Dữ liệu hiện có:** 12 file Parquet của OPM/EHRI, 03–06/2025, khoảng 301,5 MB (dữ liệu không nén lại trong ZIP), 9.181.290 bản ghi qua bốn kỳ: Employment 9.057.997; Accessions 30.782; Separations 92.511. Đây là **bản ghi qua các kỳ**, không phải 9,18 triệu người riêng biệt. Số liệu sơ bộ về `REDACTED` và lệch tháng phải được tái kiểm chứng bằng code trong EDA.

**Ba điểm phải làm rõ từ đầu (không được che đi):**
1. [GV] “Kích thước lớn hơn 100M”: tài liệu không giải thích rõ **MB hay số bản ghi**; nhóm phải xin thầy xác nhận. Bộ dữ liệu đạt trên 100 MB, **không** đạt 100 triệu bản ghi.
2. Dữ liệu OPM/EHRI công bố là nguồn phân tích dạng file, **không phải bản sao một hệ thống OLTP giao dịch nguyên bản**. Cần xin thầy chấp thuận cách trình bày **ERD lớp nguồn/ODS quan hệ được thiết kế minh họa trên trường dữ liệu thật**, đồng thời ghi chú đúng bản chất.
3. [GV] Phải public dashboard lên website; kiểm tra khả năng cấp quyền Power BI/Publish-to-web sớm và chỉ công bố dữ liệu tổng hợp phù hợp công khai. Nếu không thực hiện được, ghi rõ trở ngại và xin phương án được thầy chấp thuận; không coi ảnh chụp là tương đương yêu cầu public.

**Giới hạn dữ liệu không được vi phạm:** Không tạo employee_id giả; không nối Employment, Accessions, Separations thành lịch sử nhân viên; không cộng số dòng Employment bốn tháng thành “số nhân viên”; không gọi `REDACTED` là lương 0; không khẳng định Headcount delta = Accessions − Separations; không khẳng định mùa vụ/nhiều năm dựa trên bốn tháng; không dựng hệ thống nguồn thực tế của OPM rồi mô tả như thông tin đã được xác minh.

---

## I. Bảng chuẩn tự nghiệm thu 11 tiêu chí theo bảng thầy chấm

| ID | Tiêu chí bảng chấm | Nhóm 6 | Mục tiêu nhóm 13 | Minh chứng quan trọng nhất |
|---|---|---:|---:|---|
| C01 | Quy trình nghiệp vụ | 5/5 | 4,5–5 | Sơ đồ quy trình, cây nghiệp vụ, mô hình quản trị, điểm phân tích gắn KPI và nguồn |
| C02 | Requirement | 4,5/5 | 4,5–5 | Đối tượng sử dụng, bài toán, chủ điểm, cây yêu cầu, cây dashboard, KPI có định nghĩa |
| C03 | Hệ thống / quy mô dữ liệu | 4,5/5 | 4,5–5 | Chứng cứ nguồn, kiểm kê file/row/field/size, taxonomy, data flow hiện trạng và đề xuất |
| C04 | ERD OLTP | 5/5 | 4,5–5 có điều kiện | ERD nguồn đúng bản chất, ma trận quan hệ được kiểm chứng, mapping OLTP/ODS → OLAP |
| C05 | Data Exploration | 4/5 | 4,5–5 | EDA tái lập được, null/outlier/redacted, phân bố/Pareto, thống kê, phân tích liên hệ |
| C06 | Kiến trúc DW | 4/5 | 4,5–5 | Kiến trúc rõ luồng, công nghệ thực dùng, schema/tầng vật lý và data mart tách biệt |
| C07 | ETL | 5/5 | 4,5–5 | ETL jobs chạy được, before–after, số dòng đối soát, log, nạp nhiều kỳ/idempotent |
| C08 | Data Dimension | 4/5 | 4,5–5 | Grain & conformed dimensions, thuộc tính/phân cấp, dữ liệu ví dụ và số hàng từng Dim |
| C09 | Data Model OLAP | 5/5 | 4,5–5 | 3 Fact/Dimensions có grain, logic/vật lý staging/DW/DM, phép OLAP và KPI đúng ngữ nghĩa |
| C10 | Dashboard / BI | 3,5/5 | 4,5–5 | BI tương tác + DAX + cảnh báo + public + tình huống thật + SQL/DAX reconciliation |
| C11 | Bài học tổng kết | 4/5 | 4,5–5 | Những vấn đề đã gặp, thử nghiệm, hiệu năng đo thật, hạn chế, bài học và cải tiến |

**Không có rubric chi tiết quy đổi 4,5 hay 5/5** trong file Excel; bảng trên là mục tiêu quản trị chất lượng nội bộ suy ra từ yêu cầu của thầy và bài đã chấm, không thay cho quyết định của giảng viên.

---

## II. Đề cương công việc chi tiết theo từng tiêu chí

### C01. KHẢO SÁT QUY TRÌNH NGHIỆP VỤ — mục tiêu 4,5–5/5

**[GV] Phải trình bày:** Hình quy trình nghiệp vụ; đánh dấu hệ thống phân tích tại các giai đoạn thích hợp; cây nghiệp vụ; mô hình kinh doanh/ví dụ Canvas.

**[NHÓM 13] Phạm vi đúng:** Không dựng quy trình tuyển dụng end-to-end từ các file vốn không mô tả quy trình đó. Mô tả **quy trình lập báo cáo, giám sát và hỗ trợ hoạch định lực lượng lao động** ở mức minh họa, nêu các bước OPM/cơ quan cung cấp và phân tích chỉ khi có cơ sở nguồn. Nếu biểu diễn bước giả định về vận hành thì ghi “quy trình quản trị đề xuất”, không gán đó là quy trình OPM đã xác minh.

**Cần làm:**
- Xác định đối tượng dữ liệu: cơ quan, vị trí/nghề nghiệp, cấp bậc, địa điểm, thời gian báo cáo, tiếp nhận, rời cơ quan.
- Lập sơ đồ quy trình phân tích: dữ liệu công bố → tiếp nhận/tập hợp → kiểm soát chất lượng → chuẩn hóa → DW → phân tích quy mô/cơ cấu/biến động → hỗ trợ quyết định.
- Lập ít nhất 2 luồng tác nghiệp quản trị ở cấp phân tích: (a) giám sát cơ cấu nhân lực định kỳ; (b) theo dõi tiếp nhận và nhân sự rời cơ quan. Nếu đưa BPMN, xác định actor, đầu vào, đầu ra và điểm phân tích.
- Vẽ cây nghiệp vụ: quản trị quy mô → cơ cấu → dòng nhân sự → so sánh giữa cơ quan/khu vực; chỉ gắn nhánh có dữ liệu thật.
- Thay Business Model Canvas thương mại thuần túy bằng **mô hình tạo giá trị quản trị công** (Stakeholders, Activities, Data Resources, Decision Outputs, Measures). Có thể trình bày trên khung Canvas và giải thích không có Revenue Streams phù hợp; không tự dựng lợi nhuận/khách hàng.
- Lập bảng `Điểm phân tích → quy trình → trường dữ liệu/bảng Fact → KPI → dashboard`, tương tự A1–A11 của nhóm 6, nhưng dựa trên nghiệp vụ HR thực có.

**Tài liệu & ảnh minh chứng:** `docs/01_business_scope.md`, `diagrams/business_process.drawio`, `diagrams/business_tree.drawio`, `docs/01_analysis_touchpoints.csv`, tối thiểu 1 sơ đồ và 1 bảng mapping trong slide.

**Điều kiện tự nghiệm thu:** Mọi bước vẽ có nhãn “thực chứng” hay “mô hình đề xuất”; từng KPI truy vết tới trường dữ liệu; sơ đồ không mâu thuẫn với cấu trúc OPM; một người khác có thể giải thích vì sao hệ thống BI xuất hiện ở mỗi bước.

### C02. REQUIREMENT / YÊU CẦU PHÂN TÍCH — mục tiêu 4,5–5/5

**[GV] Phải trình bày:** các chủ điểm cần phân tích, các khía cạnh của từng chủ điểm, cây yêu cầu, cây phân tích dữ liệu chi tiết cho **từng dashboard**.

**Cần làm:**
- Liệt kê 3 nhóm người dùng giả định hợp lý: lãnh đạo hoạch định nhân lực cấp cơ quan, chuyên viên HR analytics, cán bộ theo dõi biến động. Ghi đây là **personas mục tiêu của sản phẩm**, không phải đơn vị đã đặt hàng.
- Nêu vấn đề hiện tại **của quá trình khai thác tập dữ liệu công bố**, ví dụ: nhiều file theo kỳ, khó so sánh và tái sử dụng; không được khẳng định OPM đang sử dụng Excel thủ công hay hệ thống cũ bị lỗi nếu không có nguồn.
- Chốt 3 chủ điểm: D1 Quy mô–cơ cấu; D2 Tiếp nhận–rời cơ quan; D3 Biến động–so sánh đa chiều.
- Với mỗi chủ điểm, ghi `Câu hỏi quản trị → KPI → grain → Dimension phân tích → nguồn → công thức/định nghĩa → giới hạn → đồ thị`.
- Vẽ **1 cây yêu cầu chung và 3 cây phân tích cho D1, D2, D3**; phân biệt chỉ số (measure) và khía cạnh (dimension).
- Tách FR (lọc theo kỳ/cơ quan/ngành nghề, drill-down, báo cáo), NFR (nạp 12 file, tái lập, integrity, độ trễ/thời gian đáp ứng được đo, khả năng public).

**KPI lõi đề xuất (chỉ đưa vào chính thức sau khi kiểm tra grain/source):**

| Mã | Chỉ số | Định nghĩa chặt chẽ | Điều kiện/cảnh báo |
|---|---|---|---|
| K01 | Monthly headcount | Đếm bản ghi Employment của **một kỳ snapshot** theo grain xác nhận | Không cộng các tháng |
| K02 | Headcount change | HC(t) − HC(t−1) | So sánh tổng thể hoặc cùng nhóm/định nghĩa |
| K03 | Headcount change % | [HC(t)−HC(t−1)] / HC(t−1) | BLANK nếu kỳ trước thiếu/0 |
| K04 | Share by agency | HC(agency,t) / HC(all,t) trong cùng filter | Kiểm tra mẫu số khi slicer |
| K05 | Share by occupation/grade/location | HC(segment,t) / HC(all,t) | Chỉ dùng chiều hiện có và mapping hợp lệ |
| K06 | Accessions count | Số bản ghi tiếp nhận theo tháng **đã chọn rõ** (file/effective) | Không suy ra tuyển mới nếu không lọc loại |
| K07 | Separations count | Số bản ghi rời cơ quan theo tháng đã chọn rõ | Không suy ra nghỉ việc tự nguyện nếu thiếu nhãn |
| K08 | Event mix | Số lượt từng loại sự kiện / tổng lượt cùng kỳ | Loại mã phải giải thích theo codebook |
| K09 | Net event difference | Accessions − Separations theo cùng định nghĩa thời gian | **Không gọi bằng thay đổi headcount** |
| K10 | Top changes | Xếp hạng tăng/giảm headcount theo agency/occupation | Có xử lý zero và thiếu kỳ |
| K11 | Data quality coverage | Tỷ lệ được gắn mã chiều hợp lệ; số dòng REDACTED | KPI kỹ thuật, không suy diễn nghiệp vụ |
| K12 | ETL/Query performance | Thời gian nạp và truy vấn trên dữ liệu thật | Đo, không điền số giả |

**Đầu ra:** `docs/02_requirements.md`, `docs/kpi_dictionary.csv`, `diagrams/requirements_tree.drawio`, `diagrams/dashboard_tree_D1-D3.drawio`.

**Nghiệm thu:** Mỗi KPI có định nghĩa duy nhất và ví dụ SQL test; mỗi dashboard trả lời tối thiểu 2 câu hỏi quản trị có dữ liệu thật; không thiết kế chỉ số bị dataset ngăn cản (turnover/retention thật, salary mean toàn hệ thống, tuyển dụng end-to-end, dự báo dài hạn).

### C03. HỆ THỐNG / QUY MÔ DỮ LIỆU NGUỒN — mục tiêu 4,5–5/5

**[GV] Phải có:** kích cỡ file, số bảng/bản ghi/thuộc tính; tần suất và khối lượng cập nhật (nếu có); Data Taxonomy; luồng dữ liệu giữa hệ thống CNTT.

**Cần làm:**
- Tạo **data inventory cho cả 12 file**, gồm đường dẫn, file size MB/MiB, tháng file, version v4/v5, row count, column count, schema, hash SHA-256 (khuyến nghị), provenance URL và ngày tải nếu xác định được.
- Bảng thống kê theo tháng/nguồn, tỷ lệ bản ghi của mỗi nhóm; ghi rõ 12 file không tương ứng 12 loại bảng OLTP khác nhau mà là **3 họ dữ liệu × 4 kỳ**.
- Có `source_data_dictionary.md/csv`: field, kiểu, giá trị miền, ý nghĩa từ tài liệu nguồn nếu xác minh, nullable, phân loại, có sử dụng trong mô hình không.
- Taxonomy: snapshot personnel, personnel events, reference/dimensional attributes, metadata/technical columns, redacted/limited; phân biệt nguồn thông tin thật và metadata nhóm tự bổ sung (file_name, ingest_at).
- Hai sơ đồ: **luồng được biết của nguồn công bố** (không tự gán các hệ thống nghiệp vụ giả thành thực tế OPM) và **luồng kiến trúc nhóm đề xuất**.
- Tần suất thực tế: dataset mẫu có các kỳ tháng 03–06/2025; đề xuất lịch ETL theo kỳ, không tuyên bố dữ liệu cập nhật realtime nếu không có nguồn.

**Đầu ra:** `docs/03_source_inventory.csv`, `docs/source_data_dictionary.csv`, `docs/source_provenance.md`, `diagrams/source_data_flow.drawio`, chương giới thiệu dataset.

**Nghiệm thu:** Lấy được toàn bộ con số từ lệnh/metadata tái lập; tổng 12 files = tổng 3 nhóm = tổng qua 4 tháng; hoàn toàn phân biệt file size (301,5 MB) với số dòng.

### C04. ERD NGUỒN / OLTP & MAPPING OLTP → OLAP — mục tiêu 4,5–5/5 có điều kiện

**[GV] Phải có:** ERD OLTP, data flow, gạch chân/highlight các trường nguồn và ghi chú mapping tương ứng khi chuyển sang OLAP.

**Rủi ro:** Dataset không chứa một ERD OLTP giao dịch đã xác minh. Không thể đạt chất lượng chuyên môn bằng cách vẽ quan hệ nhân viên giả.

**Cần làm:**
- Kiểm tra bản chất từng cột: business key/code, dữ liệu phân loại, tháng file, tháng hiệu lực, các mã shared giữa họ dữ liệu.
- Vẽ **ERD logic của lớp nguồn/ODS mô phỏng quan hệ** có 3 staging tables (hoặc tables theo family/tháng) + metadata về file/batch và các bảng mã tham chiếu nếu codebook nguồn có; các bảng Dim được xây từ distinct code có kiểm chứng.
- Phân biệt rõ 3 loại đường nối trên sơ đồ: `(i) FK verified`, `(ii) common attribute/code for conformed dimension`, `(iii) mapping ETL only`; không vẽ `(ii)` thành một FK employee-to-employee.
- Lập `source_to_target_mapping.csv`: source_file_type, source_column, transform, target_table, target_column, type, PK/FK, handling_null, handling_redacted, validation_sql.
- Highlight màu các cột tạo Fact, cột tạo Dim, cột thời gian, cột không dùng; bảng giải thích nguyên nhân loại cột.
- Nếu có thể, tạo **các bảng quan hệ trong PostgreSQL** cho ODS và chạy kiểm tra uniqueness/validity trên business code; giải thích đó là **OLTP-like/ODS model** phục vụ minh họa, không phải production OLTP của OPM.

**Đầu ra:** `diagrams/source_ods_erd.drawio`, `docs/04_relationship_audit.md`, `docs/source_to_target_mapping.csv`, `sql/00_ods_schema.sql`, ảnh hiện trường DB và câu truy vấn chứng minh liên kết.

**Nghiệm thu:** Không có khóa tự tạo nhằm chứng minh nhân viên đi từ Employment sang Accessions/Separations; từng quan hệ nêu cách và tỷ lệ kiểm chứng; thầy được hỏi xác nhận loại mô hình chấp nhận trước khi nhóm khẳng định đạt tiêu chí ERD.

### C05. DATA EXPLORATION / EDA — mục tiêu 4,5–5/5

**[GV] Phải có:** dữ liệu lỗi và tiền xử lý; Pareto/distribution; thống kê các trường; phân tích tương quan giữa Dimension–Dimension và Dimension–Fact (ví dụ scatter hoặc bảng phân tích); dùng đa dạng công cụ, gợi ý R/Excel Data Analysis.

**Cần làm 6 mô-đun có kết quả tái lập:**
1. **Dữ liệu cơ bản:** null count, distinct, min/max, frequency, số hàng, số cột, mã thiếu trong từng nhóm.
2. **Chất lượng:** missing, REDACTED, giá trị ngoài codebook, sai dạng thời gian, cột bất thường, quan hệ tháng file–tháng hiệu lực (sơ bộ 593 dòng), phân biệt giá trị có nghĩa với lỗi.
3. **Phân bố:** headcount theo cơ quan/nghề nghiệp/cấp bậc/địa điểm/nhóm tuổi; Accessions/Separations theo loại và tháng; chọn top-k hợp lý tránh chart không đọc được.
4. **Pareto:** ví dụ phần trăm headcount hoặc separations theo top 20% cơ quan; không giả định luôn đúng quy luật 80/20.
5. **Thống kê & liên hệ:** các bảng chéo agency×occupation, agency×grade, month×agency; kiểm định độ tập trung; dùng chi-square/Cramér’s V cho hai biến phân loại nếu phù hợp, hoặc biểu đồ stacked heatmap. Với Fact measure dạng count, dùng association effect size dựa trên bảng tổng hợp; **không dùng Pearson vô nghĩa trực tiếp cho mã categorical**.
6. **Xu hướng theo kỳ:** 4 tháng quan sát, so sánh MoM, không suy ra mùa vụ hay YoY; ghi sample bias/vấn đề kỳ thời gian.

**Công cụ:** Python + SQL là tối thiểu do nhóm tự lựa chọn; thêm minh chứng một phép phân tích bằng Excel Data Analysis/Power Query hoặc R để đáp ứng tinh thần “đa dạng công cụ” của thầy, có cùng số liệu đối chiếu.

**Đầu ra:** `notebooks/01_eda.ipynb`, `reports/data_quality.md`, `reports/eda_charts/`, `tests/source_data_checks.sql`, `docs/05_eda_summary.md`.

**Nghiệm thu:** Mỗi phát hiện có (vấn đề → số lượng/tỷ lệ → bằng chứng truy vấn → cách xử lý → ảnh hưởng KPI); tối thiểu một phân tích Pareto, hai bảng/biểu đồ liên hệ Dimension–Fact/Dimension–Dimension có diễn giải và giới hạn; thống kê không cộng sai snapshot.

### C06. KIẾN TRÚC DATA WAREHOUSE — mục tiêu 4,5–5/5

**[GV] Phải có:** kiến trúc riêng của bài toán chỉ rõ ETL, Dimension, Fact, tên dashboard và logo công nghệ ở từng phần; mục tiêu cấu trúc Data Sources → DW → Data Mart → BI, xử lý performance.

**Kiến trúc đề xuất có thể triển khai thực:**

`12 Parquet OPM/EHRI` → `Raw immutable + metadata` → `Staging/ODS trên PostgreSQL hoặc tạm trong DuckDB` → `ETL Python/SQL` → `PostgreSQL DW (3 Fact + Dim)` → `2 Data Mart (views/materialized tables)` → `Power BI (Import, DAX, OLAP)`.

**Cần làm:**
- Vẽ logical architecture và physical deployment architecture tách biệt; mọi công nghệ ghi trong sơ đồ phải thực sự có code/bảng chạy.
- Tổ chức schema vật lý gợi ý: `raw_meta`, `staging`, `dw`, `mart`, `audit` trong PostgreSQL; các file Parquet lưu immutable ngoài DB. **Không bắt buộc phải dùng DuckDB**, chỉ nếu hữu ích để đọc/đối soát parquet.
- Ghi rõ dữ liệu đi qua mỗi tầng, khóa/ID, hình thức batch, load run ID, nơi ghi log, data tests, điểm người dùng truy cập.
- Thiết kế tối thiểu hai **Data Mart là cấu trúc dữ liệu thực**, không phải tên hai trang Power BI: `mart.workforce_monthly` và `mart.personnel_flows_monthly`; tạo bằng SQL view/table cụ thể.
- Đề xuất tối ưu theo kết quả benchmark thực nghiệm (index trên date/agency nếu phù hợp, preaggregation, predicate pushdown, partition chỉ nếu có lợi).

**Đầu ra:** `diagrams/warehouse_architecture.drawio`, `diagrams/physical_deployment.drawio`, `sql/01_create_schemas.sql`, `docs/06_architecture_decisions.md`.

**Nghiệm thu:** Có thể kiểm tra từng mũi tên bằng bảng SQL hoặc file thực; có bảng trong Staging, DW và Mart; biểu đồ không tuyên bố Kafka/streaming/real-time nếu không triển khai.

### C07. ETL / ELT PIPELINE — mục tiêu 4,5–5/5

**[GV] Phải có:** tổng hợp các bước ETL/công cụ; mô hình pipeline/ETL jobs; bảng dữ liệu cụ thể; ví dụ before–after có đánh dấu shape các chỗ tiền xử lý; minh chứng OLTP/ODS → OLAP; dùng đa dạng công cụ khi có thể.

**Các job đề xuất:**
- `job_00_inventory`: đọc file, version, hash, schema, row count; phát hiện file đã xử lý.
- `job_01_stage`: nạp 12 Parquet vào staging (bổ sung `source_file`, `report_month`, `load_run_id`, `source_row_position` hoặc định danh dòng có chứng cứ); bảo toàn raw.
- `job_02_validate_clean`: kiểm tra kiểu, codebook, missing, REDACTED, tháng file/tháng hiệu lực; lưu cờ chất lượng (không xóa dòng âm thầm).
- `job_03_build_dimensions`: unique business code + surrogate keys, Unknown row đúng semantics, conformed dimension chỉ nếu xác minh shared meaning; log unmatched values.
- `job_04_build_facts`: xây Fact Employment Snapshot, Accessions và Separations; mỗi fact có lineage về file/row; đảm bảo không nhân bản.
- `job_05_build_marts`: tạo/refresh hai mart và bảng tổng hợp theo kỳ, cơ quan.
- `job_06_audit_reconcile`: kiểm row count, month totals, KPI, FK, duplicate load, lưu nhật ký batch/ảnh chạy.

**Thiết kế nạp nhiều kỳ:** demo nạp 03 → 04 → 05 → 06/2025 (theo report_month), sau đó chạy lại 05 để chứng minh không trùng (idempotence). Nếu cần load lại bản sửa có cùng tháng nhưng version khác, ghi logic replace-by-batch và dữ liệu thay thế không bị cộng dồn.

**Chú ý sự kiện:** Accessions/Separations lưu rõ `source_report_month` và `effective_month`/ngày hiệu lực nếu trường thực tồn tại; 593 trường hợp lệch cần đối soát lại từ file. Khi aggregate D2, có lựa chọn ngày mặc định và hiển thị rõ trên dashboard, không tự trộn các thước đo.

**Before–After bắt buộc trình bày:** ít nhất 4 ví dụ dữ liệu gốc → sau staging → sau DW (ví dụ month parsing, event category, REDACTED → NULL + status flag, conforming agency code). Chỉ dùng ví dụ thực sự có trong file. Có ảnh chạy và kết quả SQL.

**Đầu ra:** `etl/*.py`, `sql/02_etl_*.sql`, `logs/etl_run_summary.csv`, `reports/etl_reconciliation.csv`, `docs/07_etl_before_after.md`, screenshot 2 lần nạp.

**Nghiệm thu:** `SUM(rows in Fact by month)` đối soát với nguồn sau khi xác nhận grain; không có row duplicates do load lại; fail-fast khi schema đổi; quy tắc được mã hóa thành test; có log thời gian và trạng thái thành công/thất bại.

### C08. HỆ THỐNG DIMENSION — mục tiêu 4,5–5/5

**[GV] Phải có:** chi tiết dữ liệu ở từng chiều, hệ thống chiều khái niệm, số bản ghi từng chiều, nhóm các chiều có liên quan (địa lý, tổ chức, ...).

**Dimension sơ bộ (chỉ xác nhận sau data profiling):**
- `Dim_Month`/`Dim_Date` — grain theo kỳ tháng và, nếu cần, vai trò của report/effective date.
- `Dim_Agency` — mã cơ quan, tên cơ quan/cấp tổ chức nếu codebook cung cấp, không dựng hệ thống cấp bậc nếu thiếu.
- `Dim_Occupation` — mã nghề/nhóm nghề nếu có dữ liệu đối chiếu đáng tin cậy.
- `Dim_Location` — mã địa lý, phân cấp quốc gia/vùng/bang chỉ nếu nguồn cung cấp mapping đáng tin cậy.
- `Dim_Grade` — cấp bậc/thang ngạch phù hợp với dữ liệu; tránh gộp mã khác hệ thống lương tùy tiện.
- `Dim_Age_Bracket` — nếu field nguồn có; không suy ra ngày sinh cụ thể.
- `Dim_Accession_Category`, `Dim_Separation_Category` — loại sự kiện theo codebook thực.

**Cần làm:** bảng thiết kế từng dimension: `grain`, surrogate_key, natural_key, source_fields, thuộc tính, hierarchy, null/Unknown handling, update strategy SCD Type 1/2 phù hợp; bảng row count, sample data sau ETL; sơ đồ nhóm phân cấp `agency hierarchy`, `occupation hierarchy`, `location hierarchy`, `time hierarchy` nếu có thật.

**SCD:** Không dựng SCD Type 2 về lịch sử chuyển cơ quan hoặc nhân viên thiếu employee ID. Nếu dùng SCD Type 2 cho mô tả **mã cơ quan** giữa các kỳ thì phải có bằng chứng giá trị thay đổi thực sự; bằng không chọn Type 1/immutable-code dimension cho phạm vi 4 tháng.

**Đầu ra:** `docs/08_dimensions.md`, `docs/dimension_catalog.csv`, `diagrams/dimension_hierarchies.drawio`, `reports/dim_row_counts.csv`.

**Nghiệm thu:** mỗi Dim có dữ liệu thật, row count, quy tắc khóa và phân cấp; 100% conformed keys mà nhóm dùng trong Fact tìm được dimension hoặc Unknown được ghi nhận minh bạch; phân cấp không trùng/mâu thuẫn.

### C09. DATA MODEL OLAP — mục tiêu 4,5–5/5

**[GV] Phải có:** data model logic **và vật lý** của staging, data marts, data warehouse; màu phân biệt Fact/Dimension, nhóm vùng bằng Shape; trình bày KPI, cây dashboard và OLAP.

**Fact sơ bộ:**
- `Fact_Employment_Snapshot`: grain dựa trên **một dòng snapshot Employment thực tế trong một kỳ**, gắn `snapshot_month_key`, agency, occupation, location, grade...; count ở mức một kỳ, không cộng chéo kỳ.
- `Fact_Accessions`: grain một dòng sự kiện tiếp nhận trong nguồn (xác nhận sau EDA), gắn report/effective period và shared dimensions hợp lệ.
- `Fact_Separations`: grain một dòng sự kiện rời cơ quan, tương tự.

**Cần làm:**
- Viết `grain statement` (một bản ghi biểu diễn gì) và `aggregation rule` cho từng Fact trước khi viết DDL.
- Chốt conformed dimensions, xử lý các dimension chỉ áp dụng một Fact; xây **3 star schema** có chiều dùng chung — có thể gọi bus matrix/galaxy tùy thực tế.
- Sơ đồ (a) staging/ODS vật lý, (b) DW logic, (c) DW vật lý có PK/FK/index, (d) hai Data Mart logic/vật lý, (e) Power BI semantic model.
- Bảng bus matrix: row = fact/process, column = dimensions, đánh dấu hỗ trợ/chưa hỗ trợ và grain của thời gian.
- Mỗi KPI chỉ rõ SQL và DAX tính tương ứng, xử lý ngữ nghĩa snapshot **semi-additive**; người dùng drill-down agency/location/occupation và filter theo thời gian đúng.
- Trình bày OLAP: roll-up, drill-down, slice, dice; minh chứng truy vấn SQL và thao tác ở Power BI trên data mart.

**Đầu ra:** `diagrams/staging_physical.drawio`, `diagrams/dw_logical.drawio`, `diagrams/dw_physical.drawio`, `diagrams/marts_logical_physical.drawio`, `diagrams/powerbi_model.png`, `docs/09_bus_matrix.md`, `sql/03_dw_ddl.sql`, `sql/04_marts.sql`.

**Nghiệm thu:** không có many-to-many/ambiguous filter làm double count, không JOIN giữa Fact qua thiếu employee ID, không lấy `SUM(headcount)` bốn tháng như tổng nhân viên; có ví dụ KPI tính ở SQL khớp Power BI với cùng bộ lọc.

### C10. DASHBOARD / BI — mục tiêu 4,5–5/5

**[GV] Phải có:** thống kê loại/số dashboard; đa dạng biểu đồ phù hợp; slicer để đi sâu; conditional formatting, DAX (cảnh báo, tăng trưởng...); public dashboard lên website.

**D1: Workforce Overview (Executive/Operational snapshot)**
- KPI: headcount tháng đang chọn, chênh lệch tháng trước, tỷ lệ thay đổi, số cơ quan trong phạm vi lọc (nếu xác định).
- Charts: đường headcount bốn tháng, bar top agency, stacked cơ cấu occupation/grade, địa lý có thể dùng map nếu mã vị trí đáng tin cậy.
- Slicers: report month, agency, occupation, location, grade phù hợp.
- Tình huống: xác định nhóm cơ quan có quy mô lớn và sự dịch chuyển ngắn hạn.

**D2: Accessions & Separations (Event flow)**
- KPI: accessions, separations, difference of events, top event categories.
- Charts: clustered columns theo tháng, bar theo category, agency ranking; ghi rõ report month/effective month và trường hợp lệch.
- Tình huống: cơ quan nào phát sinh nhiều lượt tiếp nhận/rời cơ quan; không tự kết luận tuyển mới hay thôi việc tự nguyện nếu dữ liệu không hỗ trợ.

**D3: Workforce Changes & OLAP (Management comparison)**
- KPI: MoM headcount change, top tăng/giảm theo nhóm, thay đổi cơ cấu theo cơ quan.
- Charts: waterfall chênh lệch cùng kỳ (nếu đủ nhóm), heatmap agency×occupation/grade, small multiples hoặc bảng matrix drill-through.
- Tình huống: lọc một agency → xem occupation → grade → so sánh snapshot hiện tại và kỳ trước để phát hiện nơi cần điều tra thêm, không khẳng định nguyên nhân từ data chưa đo.

**Tính năng chung:** uniform design; tooltip, legend, last refresh, chú giải thước đo; DAX measures có folder, không tạo hàng chục measure thừa; conditional formatting có ngưỡng rõ (do nhóm định nghĩa, ghi “ngưỡng minh họa”), ít nhất một drill-through; test cross-filter; kiểm tra số liệu bằng SQL trong bảng đối soát.

**Công bố:** có URL Power BI public hoạt động và ảnh minh chứng trên trình duyệt khác/tài khoản không đăng nhập (nếu quyền cho phép); chỉ xuất bản các tổng hợp phù hợp. Nếu không có quyền, phải xin thầy phương án thay thế được chấp thuận, tránh tự khẳng định đã đáp ứng yêu cầu.

**Đầu ra:** `powerbi/Group13_Workforce_BI.pbix`, `docs/10_dashboard_specs.md`, `docs/dashboard_test_cases.md`, `reports/dashboard_kpi_reconciliation.csv`, `evidence/dashboard/`, link publish nếu được.

**Nghiệm thu:** 3 dashboard có câu hỏi–insight–khuyến nghị dựa vào dữ liệu thật; drill/slicer không sai; ít nhất 10 test KPI lọc theo month/agency/segment khớp SQL (số 10 là chuẩn nhóm đề xuất); public link kiểm tra được; không dồn quá nhiều chart khó đọc như rủi ro ở bài tham khảo.

### C11. BÀI HỌC TỔNG KẾT + PERFORMANCE — mục tiêu 4,5–5/5

**[GV] Phải trình bày:** bài học nhóm thu được; làm việc với dữ liệu lớn, giải quyết performance là mục tiêu bài tập nhóm.

**Cần làm:**
- Bảng “Problem → Evidence → Decision → Test → Result”: ví dụ thiếu employee_id chung, REDACTED, mismatch month, snapshot semi-additivity, nạp trùng file và truy vấn chậm.
- Benchmark công bằng: cùng dữ liệu, cùng máy, cùng filter, tối thiểu 3 lần lặp mỗi phương án (chuẩn nhóm); ghi median, số dòng đọc, query plan, kích thước bảng; so sánh truy vấn raw Fact với Mart aggregation/index chỉ nếu thực sự đo được.
- Đo ETL: lần nạp full 12 files, từng lần incremental month, rerun cùng file, tốc độ rows/s; nêu phần cứng cấu hình.
- Nêu hạn chế và kế hoạch mở rộng thực tế: 4 tháng không chứng minh mùa vụ dài hạn; thiếu danh tính nhân viên; lương bị redacted; chưa có OLTP; public Power BI phụ thuộc license/quyền.
- Kết luận một insight có dẫn chứng từ truy vấn và dashboard **sau khi hệ thống chạy**, không viết sẵn số liệu minh họa vào báo cáo như là kết quả.

**Đầu ra:** `reports/11_benchmarks.csv`, `reports/11_benchmark_notes.md`, `docs/11_lessons_learned.md`, `evidence/performance/`.

**Nghiệm thu:** ít nhất 1 trường hợp tối ưu có số đo before–after thật; phân biệt thời gian đo và cảm nhận chủ quan; có bài học thuộc 3 nhóm: nghiệp vụ, kỹ thuật DW/ETL, phân tích BI.

---

## III. Những hợp đồng kỹ thuật cần khóa trước khi code (Data Contracts)

| Hợp đồng | Quy tắc nhóm 13 |
|---|---|
| Scope | 03–06/2025 là phạm vi bắt buộc; thêm tháng ngoài phạm vi chỉ sau khi hoàn thiện pipeline |
| Grain | Mỗi Fact ghi rõ một dòng là gì và có thể cộng theo chiều nào |
| Employment | Là monthly snapshot; headcount không cộng qua tháng; `COUNT(*)` chỉ là headcount khi xác minh mỗi dòng đại diện một nhân viên ở kỳ đó |
| Event time | Có `report_month` và `effective_month` nếu nguồn chứa cả hai; không gộp ngầm |
| Fact linkage | Không có link từng nhân viên giữa 3 Fact; dùng conformed Dim trên mã thực được kiểm chứng |
| REDACTED | Dữ liệu bị che giữ trạng thái `REDACTED`, không chuyển thành 0, không suy diễn lương |
| Source preservation | Giữ file gốc immutable; có provenance và batch ID để truy ngược |
| Duplicate handling | Không dùng `DISTINCT` vô điều kiện trên bản ghi sự kiện — hai bản ghi giống thuộc tính vẫn có thể là hai sự kiện hợp lệ; idempotence xử lý theo source file/version/row position |
| Tests | Row reconciliation, uniqueness theo grain hợp lệ, null/unknown FK, KPIs SQL ↔ DAX, rerun integrity, schema drift |
| Names | Một data dictionary và KPI dictionary là nguồn sự thật duy nhất; tên bảng/measure thống nhất từ code đến slide |

### Bộ test tối thiểu đề xuất (không phải định mức do thầy quy định)

- T01–T03: 12 file và tổng bản ghi theo 3 loại nguồn khớp inventory.
- T04: snapshot/headcount ở kỳ 03/2025 khớp giữa source, Fact và Power BI khi không filter.
- T05: tương tự cho 06/2025.
- T06: accessions từng tháng khớp sau ETL; nếu dùng effective_month ghi phạm vi chính xác.
- T07: separations từng tháng khớp.
- T08: code Dimension có mapping hoặc Unknown có log, không mất dòng.
- T09: chạy lại cùng file không tăng bản ghi hay KPI.
- T10: chọn tháng trong Power BI không làm cộng cả 4 snapshots.
- T11: thay đổi slicer agency/occupation mà SQL và DAX vẫn bằng nhau.
- T12: tình huống effective_month ≠ report_month được giữ và hiển thị đúng.
- T13: `REDACTED` không thành 0 và không bị đưa lên public dashboard như mức lương thật.
- T14: public dashboard chỉ có bảng tổng hợp và không vô tình phơi bày dữ liệu cần loại.
- T15: thử schema drift/file thiếu nêu rõ thông báo lỗi và fail/recover được.

---

## IV. Cấu trúc báo cáo, slide và hồ sơ bàn giao

### 4.1. Báo cáo cuối kỳ nhóm — theo đúng sheet `Nội dung báo cáo` [GV]

**Đầu tài liệu:** trang bìa, danh sách 5 thành viên; bảng đánh giá thành viên; phần tự đánh giá báo cáo; mục lục; danh mục hình/bảng (nên có); danh mục viết tắt (nên có).

**PHẦN I. TỔNG QUAN VỀ DATA WAREHOUSE:** khái niệm, đặc tính, quy trình ETL, ODS/Data Mart, kiến trúc sử dụng trong dự án và phân biệt OLTP/OLAP. Viết ngắn gọn, có dẫn nguồn, liên hệ ứng dụng.

**PHẦN II. TỔNG QUAN VỀ BUSINESS INTELLIGENCE:** mục tiêu BI, KPI, OLAP, dashboard, ứng dụng Power BI/DAX và vai trò hỗ trợ ra quyết định.

**PHẦN III. ỨNG DỤNG DATA WAREHOUSE & BI VÀO BÀI TOÁN HR:**
- 3.1. Bối cảnh, phạm vi, Requirement và giá trị quản trị.
- 3.2. Dữ liệu nguồn, metadata, provenance, taxonomy và ODS.
- 3.3. Khảo sát nghiệp vụ, luồng dữ liệu và ERD nguồn/OLTP minh họa.
- 3.4. EDA và tiền xử lý: vấn đề, phân bố, Pareto, mối liên hệ, trước–sau.
- 3.5. Kiến trúc Data Warehouse và quyết định công nghệ.
- 3.6. Triển khai ETL/ELT, pipeline, code, kiểm tra và đối soát.
- 3.7. Data Dimension, grain, mô hình OLAP logic/vật lý, Fact–Dimension, Data Mart.
- 3.8. Định nghĩa KPI, cây dashboard, mô hình Power BI, DAX và OLAP.
- 3.9. Ba dashboard, tình huống sử dụng và insight, link công bố nếu có.
- 3.10. Kiểm thử, benchmark, hạn chế, phương án nâng cấp.

**Cuối tài liệu:** kết luận, bài học thu được, tài liệu tham khảo, phụ lục ảnh minh chứng/SQL/data dictionary.

**[GV] Hình thức:** có mục lục, kết luận, tài liệu tham khảo, số trang; **Times New Roman 12**, căn đều hai bên, không sai chính tả. Cần thỏa đúng yêu cầu này ở bản báo cáo nhóm cuối kỳ; dùng Word/PDF tùy hướng dẫn nộp cập nhật.

### 4.2. Slide trình bày [GV: 30–45 phút]

**Đề xuất nhịp 40 phút (không phải yêu cầu phân chia chính thức):** 5 phút nghiệp vụ & requirement; 5 phút nguồn & ERD; 6 phút EDA; 5 phút kiến trúc/Dimension/OLAP; 6 phút ETL/demo log; 9 phút Power BI/demo 3 tình huống; 4 phút benchmark/bài học. Chuẩn bị phương án trình bày ngắn nếu thầy yêu cầu, và để thời gian trao đổi theo thực tế lớp.

**Slide bắt buộc phải đọc được:** kiến trúc có logo/nhãn công nghệ; mô hình Fact/Dim tô màu; ảnh before–after; bảng reconciliation; dashboard tình huống thực; kết luận không phóng đại dữ liệu. Không cần sao chép 238 slide nhóm 6; slide trình bày chọn lọc, báo cáo chi tiết để ở bản nộp.

### 4.3. Bảng tự đánh giá thành viên [GV]

- Sử dụng mẫu sheet `Đánh giá thành viên nhóm` với 5 thành viên.
- Các mục: hoàn thành công việc, liên hệ khi cần, sáng kiến, giúp đỡ, đóng góp chung.
- Chấm mỗi mục từ 1–5 theo hướng dẫn; file ghi điểm đánh giá **mỗi thành viên có tối thiểu 4 bậc điểm** — trưởng nhóm cần đối chiếu cách hiểu và thực hiện đúng mẫu.
- **Tất cả thành viên ký**, trưởng nhóm tổng hợp.
- Hướng dẫn ghi điểm báo cáo cuối kỳ có bổ sung trọng số đóng góp và tối đa bằng điểm trình bày nhóm. Các thành viên cần giải thích được phần mình làm khi vấn đáp.

### 4.4. Cấu trúc dự án để chia việc sau khi chốt (đề xuất)

```text
DW_BI_Group13/
├── README.md
├── configs/
├── data/                       # Không commit bản ghi gốc vào Git nếu không cần
│   ├── README_sources.md       # Link + checksum + nguồn + version
│   └── sample_schema/          # Chỉ metadata/schema, không tạo bản ghi giả
├── docs/                       # 01_business... đến 11_lessons...
├── diagrams/                   # source/ODS/DW/DM/pipeline/dashboard trees
├── notebooks/                  # EDA và kiểm chứng
├── etl/                        # job_00...job_06
├── sql/                        # DDL, ETL, mart, KPI, tests
├── tests/                      # Automated + manual reconciliation
├── reports/                    # Inventory, quality, KPI, benchmark
├── powerbi/                    # .pbix và dashboard specifications
├── evidence/                   # Ảnh SQL/ETL/dashboard/benchmark theo rubric
└── deliverables/               # Báo cáo nhóm, slide, phụ lục, đánh giá thành viên
```

**Definition of Done cho mọi phần:** có **(1) file nguồn có thể sửa/chạy, (2) kết quả tái lập, (3) ảnh minh chứng gắn nhãn, (4) vài dòng giải thích ý nghĩa, (5) ít nhất một kiểm tra độc lập**. Không đánh dấu hoàn thành chỉ vì đã viết slide.

---

## V. Thứ tự triển khai và các mốc khóa thiết kế

> Các chặng dưới đây theo **quan hệ phụ thuộc**, không tự suy ra lịch ngày cụ thể trước tuần 16.

| Chặng | Công việc và quyết định khóa | Điều kiện qua chặng |
|---|---|---|
| G0. Thống nhất phạm vi | Xác nhận `100M`, OLTP minh họa, Power BI public; rà lại phiên bản hướng dẫn lớp đang áp dụng | Ba blocker có ghi nhận phản hồi/đề xuất xử lý và người chịu trách nhiệm |
| G1. Business + Data Inventory | Hoàn thành C01–C03, danh sách KPI, inventory 12 file, codebook kiểm tra | KPI truy được về source field; không còn thông tin nguồn chưa rõ được dùng làm fact |
| G2. Data Contract + ERD | Hoàn thành ERD C04, EDA C05, chốt grain, dimensions, date semantics | Có source-to-target mapping và test source quality; thống nhất ontology mã |
| G3. Warehouse Foundation | C06, C08, C09: staging, DW/DM DDL và sơ đồ logic/vật lý | Tạo được DB, bảng Dim/Fact/mart và kiểm chứng khóa/quan hệ |
| G4. ETL + Tests | C07: nạp 4 kỳ, idempotence, xử lý date/redacted, reconciliation | Pipeline lặp lại được; KPI SQL đúng, log đủ |
| G5. BI + Performance | C10, C11: DAX, 3 dashboard, public, benchmark, bài học | 3 demo case, KPI khớp SQL, benchmark thật, public hoặc phương án được thầy đồng ý |
| G6. Reporting/Defense | Báo cáo đúng form, slide 30–45 phút, danh sách bằng chứng và đánh giá thành viên | Mỗi tiêu chí có ít nhất 1 slide + 1 evidence; mock Q&A và demo chạy thành công |

**Có thể làm song song:** G1 nghiệp vụ ↔ inventory và EDA sơ bộ; cuối G2 thiết kế Dimension ↔ dựng môi trường; G4 test ↔ triển khai ETL; G5 dashboard ↔ tích hợp tài liệu. **Không nên làm trước khi khóa:** DAX/KPI trước grain, ERD trước khảo sát key, benchmark trước có bản chạy nền, kết luận insight trước SQL đối soát.

---

## VI. Ma trận minh chứng — một bước nữa trước khi phân công 5 người

| C | Tệp/bằng chứng buộc có để nhóm tự xét “đã xong” | Câu hỏi vấn đáp cần trả lời |
|---|---|---|
| C01 | BPMN/quy trình, cây nghiệp vụ, Canvas quản trị, bảng điểm phân tích | Nghiệp vụ nào sinh dữ liệu nào? Đây là quy trình thật hay mô phỏng? |
| C02 | Cây yêu cầu, 3 cây dashboard, KPI dictionary, FR/NFR | Vì sao tính KPI đó? Dữ liệu có hỗ trợ không? |
| C03 | Inventory + taxonomy + provenance + source data flow | 9,18 triệu dòng nghĩa là gì? 100M là đơn vị gì? |
| C04 | ERD nguồn, verified-link matrix, source-to-target mapping | Không có employee_id thì nối 3 loại dữ liệu thế nào? |
| C05 | Notebook EDA, Pareto, heatmaps, data quality log | `REDACTED` và 593 dòng lệch kỳ được xử lý thế nào? |
| C06 | Logical+physical architecture, evidence SQL tầng staging/dw/mart | Mỗi tầng làm nhiệm vụ gì và khác nhau ra sao? |
| C07 | ETL jobs, log 4 lần nạp, before/after, idempotence | Chạy lại tháng 05 có bị tăng đúp không? |
| C08 | Catalog + row count + hierarchy + Unknown/Type 1 rules | Dimension nào được dùng chung và vì sao? |
| C09 | Grain, bus matrix, 3 star, staging/DW/DM models, KPI SQL | Vì sao headcount không được SUM qua nhiều tháng? |
| C10 | `.pbix`, 3 demo cases, DAX/SQL reconciliation, public link | Khi slicer thay đổi, kết luận có còn đúng không? |
| C11 | Benchmark CSV, SQL plans, lessons, limitation | Nhóm đã tối ưu điều gì, nhanh hơn bao nhiêu, đo bằng cách nào? |

**Quy tắc chấm thử nội bộ:** Mỗi mục chỉ được đánh dấu **sẵn sàng phấn đấu ≥4,5/5** nếu đầy đủ: (A) nội dung đúng yêu cầu file hướng dẫn; (B) sản phẩm/code/DB thật; (C) minh chứng; (D) giải thích được khi hỏi; (E) không vượt khả năng dữ liệu. Nếu thiếu A hoặc B, mục đó chưa hoàn tất, dù slide đẹp.

**Kết luận quyết định:** Nhóm 13 có quy mô dữ liệu và độ sâu kỹ thuật đủ để phấn đấu điểm cao trên từng mục. Thành công phụ thuộc nhiều nhất vào **sự trung thực trong mô tả OLTP/ERD**, **định nghĩa grain và KPI đúng**, **ETL + Data Mart thực sự vận hành**, **dashboard được kiểm thử và public**, và **chứng cứ đo hiệu năng**. Phân công 5 người nên thực hiện *sau khi chốt G0–G2*, ưu tiên chia theo các gói bàn giao phụ thuộc nhau thay vì chia theo số trang báo cáo.

---

## VII. KẾ HOẠCH TRIỂN KHAI THỰC TẾ TRONG 5,5 TUẦN (BỔ SUNG)

> Phần này chuyển **đề cương nội dung (C01–C11)** thành **kế hoạch thực thi có cổng nghiệm thu**. Đây là lịch nội bộ nhóm 13, không phải thời hạn do giảng viên quy định. Năm thành viên cần làm song song theo các luồng nghiệp vụ/tài liệu, dữ liệu/ETL, kho/OLAP, Power BI, kiểm thử/tích hợp; phân công chính thức theo tên thực hiện sau khi chốt phạm vi.

### 7.1. Nguyên tắc cắt phạm vi và thứ tự ưu tiên

| Ưu tiên | Hạng mục | Nguyên tắc |
|---|---|---|
| **P0 — Không được thiếu** | Yêu cầu + nghiệp vụ; inventory/EDA cơ bản; ERD nguồn được ghi rõ tính chất; Data Contract/grain; Staging, DW, Data Mart; ETL chạy được; 3 Fact/conformed Dim; KPI SQL + Power BI; ba dashboard; báo cáo và trình bày đúng mẫu | Mọi mục có minh chứng chạy thật và người khác có thể giải thích |
| **P1 — Để cạnh tranh 4,5–5** | Idempotent/incremental ETL; data-quality audit; before–after; DAX/SQL reconciliation; OLAP drill; benchmark; Power BI public; 3 tình huống phân tích có insight thật; checklist vấn đáp | Làm sau khi P0 đã chạy end-to-end, nhưng chuẩn bị thiết kế từ đầu |
| **P2 — Chỉ khi còn dư thời gian** | Thêm tháng/năm dữ liệu; thêm dashboard thứ tư; tự động hóa lịch chạy; tối ưu nâng cao ngoài case benchmark chính | Không được đẩy lùi P0/P1 |
| **Không đưa vào 5,5 tuần** | Lakehouse, Kafka/Spark Streaming, AI/Text-to-SQL, ML dự báo, dựng HRMS giao dịch giả | Ngoài mục tiêu môn và làm tăng rủi ro giao bài không hoàn chỉnh |

**Định nghĩa MVP kỹ thuật:** từ ít nhất 1 file Employment, 1 file Accessions và 1 file Separations, dữ liệu đi qua Staging → DW (Fact/Dim) → Data Mart → Power BI, kèm ít nhất 1 KPI đối soát đúng. Hoàn thành MVP nhỏ *trước* khi nạp toàn bộ 9,18 triệu bản ghi; sau đó mở rộng đến đủ 12 file.

### 7.2. Tiến độ tuần theo cổng nghiệm thu

| Thời gian | Trọng tâm và công việc song song | Đầu ra buộc có cuối mốc | Cổng nghiệm thu (đủ mới chuyển mốc) |
|---|---|---|---|
| **Tuần 1 (ngày 1–7)** | Xác minh yêu cầu với thầy; kiểm tra Publish to web; kiểm kê 12 Parquet và codebook; EDA sơ bộ; chốt 3 chủ điểm và người dùng; khởi tạo Git/DB; thử đọc/đổ một tập dữ liệu nhỏ | `scope_decisions.md`, inventory, source schema, KPI v0, kiến trúc v0, môi trường chạy, issue list | Không nhầm 100M; ghi rõ rủi ro OLTP; đọc được Parquet; mọi KPI có nguồn; phân công được người chịu trách nhiệm từng đầu ra |
| **Tuần 2 (ngày 8–14)** | Hoàn tất Business/Requirement/EDA chính; ERD nguồn có quan hệ được kiểm chứng; source-to-target mapping; grain và bus matrix; DDL staging/dw/mart; dựng MVP 3 loại Fact → 1 Mart → 1 KPI trên Power BI | BPMN/cây yêu cầu/KPI dictionary, EDA, ERD, DW logic/vật lý v1, **MVP chạy xuyên hệ thống** | Các bước ETL nhỏ chạy lại được; KPI nguồn = SQL = Power BI cho 1 tháng và 1 bộ lọc; không tự nối employee_id |
| **Tuần 3 (ngày 15–21)** | Hoàn thiện ingestion 12 file; chuẩn hóa conformed Dim; nạp 4 tháng; tạo 3 Fact và 2 Mart; kiểm thử null/REDACTED/kỳ hiệu lực; log run và idempotence | Database DW + marts đầy đủ, pipeline version 1, data quality report, bảng đối soát theo tháng/nguồn | Đối soát tổng dòng và các KPI cơ bản; chạy lại 1 tháng không nhân đôi; các bảng mart truy vấn được; lưu log lỗi/runs |
| **Tuần 4 (ngày 22–28)** | Power BI 3 dashboard hoàn chỉnh v1; DAX/OLAP; drill/slicer; công bố thử; testing và benchmark nền; bắt đầu ghép báo cáo | `.pbix` v1, 3 dashboard, 3 kịch bản demo, SQL/DAX reconciliation, benchmark baseline, draft báo cáo | Không có KPI sai khi lọc; mỗi dashboard trả lời được một câu hỏi; có kết quả benchmark lần đầu; không còn lỗi blocking của pipeline |
| **Tuần 5 (ngày 29–35)** | Chỉ sửa lỗi, tối ưu có đo; chốt dashboard/Publish to web; hoàn thiện báo cáo/slide, bảng đánh giá thành viên; test end-to-end và chuyển máy | **Release candidate:** pipeline, marts, dashboard, kết quả kiểm thử, link công bố (hoặc phương án được thầy duyệt), báo cáo và slide gần cuối | Mỗi C01–C11 có ít nhất một bằng chứng; toàn bộ demo chạy từ máy dự kiến trình bày; đối soát SQL/DAX pass; freeze tính năng trước cuối tuần |
| **0,5 tuần cuối (khoảng 3–4 ngày)** | Chạy tổng duyệt 30–45 phút, dự phòng lỗi cài đặt/Power BI, sửa lỗi báo cáo, ký đánh giá thành viên và đóng gói | Gói nộp cuối, slide, demo video/offline backup, README cách chạy, phiếu điểm nội bộ 11 tiêu chí | Hai lần tổng duyệt liên tiếp không lỗi; 5 người đều trả lời được phần của mình và kiến trúc tổng thể |

**Không chờ phản hồi giảng viên mới bắt đầu việc khác:** gửi ngay ba câu hỏi về 100M, OLTP minh họa, quyền public dashboard; đồng thời làm các phần không phụ thuộc như source inventory, data profiling và thiết lập môi trường. Nếu điều kiện OLTP không được chấp nhận, cần quyết định điều chỉnh dataset/phạm vi ngay trong **tuần 1**, không để đến giữa dự án.

### 7.3. Nhóm việc bắt buộc chạy song song (chưa gán tên)

1. **Nghiệp vụ & hồ sơ:** scope, Requirement, KPI dictionary, sơ đồ nghiệp vụ, viết báo cáo liên tục từ tuần 1.
2. **Khảo sát nguồn:** inventory, data profiling, codebook, mapping, kiểm tra quan hệ mã và độ lệch kỳ; bàn giao data contract cho đội ETL.
3. **DW/ETL:** schema, Fact/Dimension, nạp Parquet, mart, log; phải chạy phiên bản MVP trước khi hoàn thiện tài liệu kiến trúc.
4. **Power BI/OLAP:** dựng semantic model, KPI/DAX và layout mẫu từ sớm; phát triển chính trên các bảng mart đã được khóa cấu trúc.
5. **Kiểm thử/tích hợp:** viết test SQL ngay từ tuần 2, theo dõi vấn đề Git, benchmark và tổng duyệt; không chỉ xuất hiện cuối dự án.

**Phụ thuộc cần khóa:** KPI/grain → Fact/Dim → Mart → DAX/dashboard. Nhóm có thể chuẩn bị song song layout Power BI, nhưng không chốt measure trước khi grain được phê duyệt nội bộ.

### 7.4. Cơ chế kiểm soát tiến độ và thay đổi

- **Họp 20–30 phút hai lần/tuần**: mỗi người báo đầu ra đã commit, kết quả kiểm thử, blocker, việc tiếp theo; không tính "đã đọc tài liệu" là hoàn thành.
- **Một Git repo + một issue board**: mỗi task có `owner`, `deadline`, `depends_on`, `DoD`, đường dẫn file/evidence. PR/review ít nhất bởi một người khác cho thay đổi grain/KPI/SQL.
- **Cuối tuần 2 khóa grain, KPI dictionary và tên bảng**; chỉ đổi qua `change_log.md` vì mọi thay đổi sau mốc này có thể làm vỡ ETL và DAX.
- **Cuối tuần 4 đóng băng mô hình dữ liệu nếu đã pass kiểm thử**, chỉ nhận sửa lỗi làm sai kết quả; **cuối tuần 5 freeze tính năng**.
- **Sao lưu/demo**: có dump/schema SQL, `.pbix`, ảnh dashboard và kịch bản demo; chuẩn bị video demo nếu mạng/PBI web lỗi nhưng không coi video thay thế cho yêu cầu public của thầy.

### 7.5. Rủi ro phải có kế hoạch dự phòng

| Rủi ro | Mốc phát hiện muộn nhất | Phương án xử lý |
|---|---|---|
| Thầy không chấp nhận OLTP minh họa hoặc "100M" = 100 triệu dòng | **Tuần 1** | Hỏi xác nhận trực tiếp; điều chỉnh phạm vi/dataset, không làm sai bản chất nguồn |
| Không Publish to web được do tenant/quyền | **Tuần 1 kiểm tra; tuần 4 xác nhận lại** | Sớm tìm tài khoản/môi trường hợp lệ; hỏi thầy phương án công bố được chấp thuận, không đưa dữ liệu nhạy cảm |
| Laptop/DB chậm khi nạp 9,18 triệu bản ghi | **Tuần 2 MVP, tuần 3 full load** | Nạp theo file/tháng, batch/chunks, dùng Parquet + SQL, đo trước khi tối ưu; không chờ đủ full load mới thử dashboard |
| SQL/DAX lệch do headcount và event time | **Tuần 2–4** | Chốt grain/date semantics; đối soát theo tháng và agency; test lại sau mỗi sửa dữ liệu |
| Báo cáo và slide bị dồn vào cuối | **Mọi tuần** | Viết ngay khi mỗi phần chạy xong; evidence đặt đúng C01–C11; tuần 5 chỉ còn biên tập |
| Bị thiếu người/gián đoạn lịch | **Mọi tuần** | Mỗi gói kỹ thuật có 1 người chính + 1 người backup; README chạy lại trong repo; tối thiểu 2 người biết demo |

### 7.6. Điều kiện xác nhận "đủ sức nhắm 4,5–5/5"

Đến hết **tuần 4**, nếu chưa có **full pipeline 12 file + ba Fact + Data Mart + ít nhất ba dashboard v1**, nhóm phải cắt ngay mọi P2 và tập trung cứu P0. Đến hết **tuần 5**, mỗi C01–C11 phải có file kết quả, ảnh/evidence, người trình bày và câu trả lời vấn đáp. Trong 0,5 tuần cuối không thêm chủ đề, bảng dữ liệu hay dashboard mới.

**Lưu ý:** điểm 4,5–5/5 không thể suy ra chắc chắn từ checklist. Đây là mức độ chuẩn bị nội bộ để giảm rủi ro bị trừ điểm vì thiếu, sai hoặc không chứng minh được nội dung.
