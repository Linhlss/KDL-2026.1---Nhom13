# Đặc tả ba dashboard D1 / D2 / D3 (L4-02)

**Task:** L4-02 (issue #31) — Owner: TV4 — Reviewer: TV1 — Người nhận tiếp: TV1, TV3
**Phiên bản:** v0.1, ngày 19/11/2026 (cập nhật theo bàn giao G2 của TV2, PR #42)
**Trạng thái:** REVIEW (chờ TV1 xác nhận; chưa PASS)
**Đầu vào đã dùng:** `docs/02_kpi_dictionary.csv` (K01–K10), `docs/01_business_scope.md`, số tổng hợp từ `evidence/TV2_week1/TV2_Data_Quality_Phan_Tich_V1/` (profiling v1 của TV2), và bàn giao G2 của TV2 trên nhánh `tv2/g2-source-model` (PR #42, chưa merge): `docs/04_relationship_audit.csv`, `docs/04_source_model_handoff.md`, `reports/05_eda_findings.md`. Các đầu vào của TV2 đang ở trạng thái REVIEW, chưa PASS.

> **Cách đọc tài liệu này.** Tên bảng, tên cột trong mô hình, DAX và SQL là **thiết kế dự kiến**. Chúng được chốt ở L4-03/L4-04 (bus matrix, Dimension catalog) và L4-05/L4-06 (kết nối Mart MVP). Mọi con số dùng làm ví dụ là **tổng kiểm từ profiling TV2 trên file Parquet**, chưa phải kết quả database, ETL hay Power BI. Chỗ nào chưa có số thật thì để `[điền sau khi chạy]`, không viết trước kết luận.

---

## 1. Mục tiêu và phạm vi

Ba dashboard trả lời ba câu hỏi chính của đề tài:

| Dashboard | Câu hỏi | Nguồn | Kỳ thời gian |
|---|---|---|---|
| **D1 — Workforce Overview** | Kỳ đang chọn có bao nhiêu bản ghi nhân sự, cơ cấu thế nào? | Employment snapshot | `snapshot_yyyymm` |
| **D2 — Personnel Flows** | Có bao nhiêu lượt tiếp nhận/rời cơ quan theo kỳ báo cáo và loại hành động? | Accessions, Separations | `report_month` (từ tên file) |
| **D3 — Workforce Changes (OLAP)** | Nhóm nào đóng góp vào mức tăng/giảm giữa hai kỳ? | So sánh hai snapshot Employment | `snapshot_yyyymm`, hai kỳ liền nhau |

Phạm vi dữ liệu: 12 file Parquet OPM/EHRI, 4 kỳ 03–06/2025 (Employment v4, Accessions và Separations v5).

## 2. Nguyên tắc bắt buộc (áp dụng cho cả ba trang)

1. **Headcount là snapshot.** Không cộng Employment của nhiều tháng thành "số nhân viên". Mỗi phép đo headcount luôn gắn với đúng một tháng (semi-additive theo thời gian).
2. **Không nối Fact với Fact.** Không có mã nhân viên. Ba Fact chỉ gặp nhau qua các Dimension dùng chung (tháng, cơ quan, ...). Mỗi measure tính trên đúng một Fact rồi đặt cạnh nhau.
3. **Event Difference không phải thay đổi headcount.** K08 = Accessions − Separations tính theo lượt; thay đổi headcount K02 là hiệu hai snapshot. Hai số này khác nhau và không cần bằng nhau (tháng 04/2025: −16.935 lượt so với −17.223 người).
4. **Hai trục thời gian của event tách riêng.** D2 mặc định lọc theo `report_month` (do nhóm tạo từ tên file, không phải cột raw). Tháng hiệu lực `personnel_action_effective_date_yyyymm` là vai trò thời gian thứ hai, chỉ dùng khi ghi rõ nhãn.
5. **`REDACTED` không bằng 0.** Giữ nhóm `REDACTED`/`Unknown` hiển thị riêng; không loại ngầm khỏi mẫu số.
6. **Thiếu kỳ trước thì BLANK, không phải 0.** Mẫu số bằng 0 cũng trả BLANK.
7. **Không suy diễn nguyên nhân.** Không viết "tuyển mới", "sa thải", "nghỉ việc tự nguyện" khi dữ liệu không có nhãn tương ứng.
8. **Không tuyên bố mùa vụ, YoY hay dự báo** từ 4 kỳ.

### 2.1. Giới hạn dữ liệu từ audit của TV2 (ảnh hưởng thiết kế)

| Phát hiện | Số liệu (audit TV2, Employment) | Hệ quả cho dashboard |
|---|---|---|
| Quan hệ danh mục (agency, nghề nghiệp, địa điểm, pay plan, category) mới ở trạng thái **PARTIAL** | Danh mục lịch sử chưa đối chiếu hết | Chưa vẽ hierarchy hay khẳng định FK; ghi `uncertain` trong bus matrix |
| **Grade không có FK riêng (UNSUPPORTED)** | Grade phụ thuộc pay plan | `dim_grade` dùng cặp **pay_plan + grade**, không dùng grade đơn lẻ |
| `duty_station` bị `REDACTED` nhiều | 1.050.981 / 2.289.192 bản ghi tháng 03 (≈ 45,9%); 1.046.119 tháng 04; 1.036.800 tháng 05; 1.032.821 tháng 06 (≈ 46%/tháng); khoảng 17.000 mã khác nhau | Chiều địa điểm không đủ tin cậy: **bản đồ D1 chưa khả thi**; nếu dùng chiều này phải hiển thị nhóm `REDACTED` riêng |
| `pay_plan` có giá trị NULL | 366 bản ghi tháng 03, 2.488 tháng 04, 2.444 tháng 05, 2.430 tháng 06 | Giữ nhóm `Unknown` trong cơ cấu K05, không loại ngầm |
| Event có tháng hiệu lực khác tháng file | 593 bản ghi (269 Accessions, 324 Separations) trong 4 kỳ | Giữ hai trục thời gian tách riêng; ghi vào tooltip D2 |
| Phân bố cơ quan rất lệch | Khoảng 120–130 mã cơ quan mỗi kỳ; nhóm top 20% cơ quan chiếm khoảng 98% snapshot | Top 10 cơ quan là hợp lý; thêm nhóm "Khác" để mẫu số đầy đủ |

## 3. Danh mục KPI dùng trong ba trang

Lấy từ `docs/02_kpi_dictionary.csv` (v0). Số ví dụ là tổng kiểm từ profiling TV2.

| KPI | Tên hiển thị | Đơn vị | Dùng ở | Công thức (ý nghĩa) | Ví dụ 04/2025 | Giới hạn |
|---|---|---|---|---|---:|---|
| K01 | Monthly Headcount | người | D1, D3 | Số bản ghi Employment trong **một** snapshot | 2.271.969 | Không cộng nhiều tháng |
| K02 | Headcount Change | người | D1, D3 | K01(t) − K01(t−1), cùng phạm vi lọc | −17.223 | Thiếu kỳ trước: BLANK |
| K03 | Headcount MoM | % | D1, D3 | K02 / K01(t−1) | −0,75% | Mẫu số 0 hoặc thiếu: BLANK |
| K04 | Agency Share | % | D1 | HC cơ quan / HC mọi cơ quan, cùng kỳ | VA ≈ 20,76% | Mẫu số bỏ lọc cơ quan, giữ các lọc khác |
| K05 | Group Share | % | D1 | HC nhóm / HC mọi nhóm cùng chiều và kỳ | [điền sau khi chạy] | Chỉ dùng chiều đã được TV2 xác minh |
| K06 | Accessions Count | lượt | D2 | Số bản ghi Accessions của kỳ báo cáo đã chọn | 7.153 | Không suy ra "tuyển mới" |
| K07 | Separations Count | lượt | D2 | Số bản ghi Separations của kỳ báo cáo đã chọn | 24.088 | Không suy ra "tự nguyện" |
| K08 | Event Difference | lượt | D2 | K06 − K07, cùng kỳ báo cáo | −16.935 | Không gọi là net headcount |
| K09 | Growth/Decline Contribution | người | D3 | Xếp hạng HC nhóm(t) − HC nhóm(t−1) | [điền sau khi chạy] | Nhóm vắng một kỳ phải phân biệt với nhóm bằng 0 |
| K10 | DQ Coverage | % | D1–D3 (chú thích) | Bản ghi tra mã thành công / bản ghi đủ điều kiện | chưa tính | Chờ audit khóa (L2-06) |

Số tổng kiểm dùng cho đối soát (đối chiếu `monthly_trends.csv`, TV2):

| Kỳ | Employment (K01) | Δ so tháng trước (K02) | MoM % (K03) | Accessions (K06) | Separations (K07) | K08 |
|---|---:|---:|---:|---:|---:|---:|
| 202503 | 2.289.192 | BLANK | BLANK | 4.862 | 22.061 | −17.199 |
| 202504 | 2.271.969 | −17.223 | −0,7524% | 7.153 | 24.088 | −16.935 |
| 202505 | 2.255.056 | −16.913 | −0,7444% | 8.813 | 26.415 | −17.602 |
| 202506 | 2.241.780 | −13.276 | −0,5887% | 9.954 | 19.947 | −9.993 |

## 4. Quy ước chung cho mô hình, định dạng và trình bày

### 4.1. Mô hình dự kiến (chốt ở L4-03/L4-04)

| Thành phần | Tên dự kiến | Ghi chú |
|---|---|---|
| Fact | `fact_employment_snapshot` | Một dòng = một bản ghi Employment trong một snapshot |
| Fact | `fact_accessions` | Một dòng = một bản ghi hành động tiếp nhận được công bố |
| Fact | `fact_separations` | Một dòng = một bản ghi hành động rời cơ quan được công bố |
| Dimension | `dim_month` | Vai trò chính: tháng snapshot (Employment) và tháng báo cáo (event) |
| Dimension (vai trò phụ) | `dim_effective_month` | Bản role-playing của tháng, quan hệ không active, dùng bằng `USERELATIONSHIP` |
| Dimension | `dim_agency` | Mã và tên cơ quan; chỉ dựng hierarchy khi TV2 xác minh |
| Dimension | `dim_accession_category`, `dim_separation_category` | Theo codebook thật |
| Dimension (nếu có căn cứ) | `dim_occupation` | Chỉ thêm vào slicer khi TV2 đánh dấu `verified` |
| Dimension | `dim_grade` | Khóa là cặp `pay_plan_code + grade` (grade không có FK riêng, UNSUPPORTED) |
| Dimension (hạn chế) | `dim_location` | `duty_station` bị `REDACTED` khoảng 46%; chỉ dùng như thuộc tính phụ, nhóm `REDACTED` hiển thị riêng, không dùng cho bản đồ |

Quan hệ trong Power BI: một chiều (Dim → Fact), không dùng many-to-many hay bi-directional nếu gây đếm đôi.

### 4.1.1. Tên schema và bảng đã có trong repo

Schema do TV3 tạo (`sql/01_create_schemas.sql`): `raw_meta`, `staging`, `ref`, `ods`, `dw`, `mart`, `audit`. Mapping TV2 dùng `ods.ods_employment_record`, `dw.fact_employment_snapshot`, `raw_meta.source_file`; mỗi dòng Fact mang `file_id` và `source_row_ordinal` để truy vết. Báo cáo Power BI chỉ nối vào schema `mart` hoặc các view tổng hợp, **không** nối trực tiếp vào `ods` hay `raw_meta`. Tên cột Dimension và Fact vẫn là dự kiến cho đến khi chốt bus matrix (L4-03/04) và DDL (L3-07).

### 4.2. Định dạng hiển thị

| Mục | Quy ước |
|---|---|
| Đơn vị | Hiển thị rõ `người`, `lượt` hoặc `%` ở tiêu đề card/trục |
| Số nguyên | Có dấu phân cách hàng nghìn, ví dụ `2,271,969` hoặc `2.271.969` theo locale của báo cáo (chọn một kiểu và dùng nhất quán) |
| Phần trăm | 2 chữ số thập phân cho MoM (ví dụ `−0,75%`) |
| Nhãn kỳ | Luôn ghi kỳ đang chọn trong tiêu đề, ví dụ "Headcount tháng 04/2025" |
| BLANK | Hiển thị `—` kèm tooltip "Chưa có kỳ trước để so sánh" |
| Last refresh | Ghi ngày làm mới dữ liệu ở chân trang |
| Chú giải | Mỗi trang có hộp "Cách đọc" giải thích snapshot, lượt và giới hạn 4 kỳ |
| Màu | Một bảng màu chung cho ba trang; màu xanh cho chỉ số tăng/tốt, đỏ cho giảm/cảnh báo, xám cho Unknown/REDACTED |

### 4.3. Điều hướng chung

- Thanh điều hướng giữa D1, D2, D3 ở đầu trang.
- Slicer **Tháng** đồng bộ giữa D1 và D3 (snapshot). D2 có slicer **Tháng báo cáo** riêng, dùng cùng `dim_month` nhưng gắn nhãn rõ.
- Mỗi trang có nút "Xóa bộ lọc".

---

## 5. D1 — Workforce Overview

### 5.1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Persona | Lãnh đạo hoạch định nhân lực cấp cơ quan, cần nhìn quy mô và cơ cấu trong một màn hình |
| Câu hỏi quản trị | (1) Tháng đang chọn có bao nhiêu bản ghi nhân sự và thay đổi bao nhiêu so với tháng trước? (2) Cơ quan nào chiếm tỷ trọng lớn? (3) Cơ cấu theo nghề nghiệp/cấp bậc ra sao (nếu mã được xác minh)? Địa lý chưa đưa vào vì dữ liệu địa điểm bị `REDACTED` nhiều. |
| KPI | K01, K02, K03, K04, K05 |
| Kỳ thời gian | `snapshot_yyyymm` (một tháng được chọn; đường xu hướng hiển thị từng tháng riêng) |
| Slicer | Tháng; Cơ quan; Nghề nghiệp (chỉ khi `verified`); Cấp bậc (theo pay plan + grade). Địa điểm **không** đưa vào slicer chính vì `REDACTED` khoảng 46% |
| Nguồn | `fact_employment_snapshot` |

### 5.2. Bố cục (wireframe)

```
+------------------------------------------------------------------------------+
| [D1 Workforce Overview]  [D2]  [D3]                                          |
+--------------+---------------------------------------------------------------+
| Bộ lọc       |  [K01 Headcount tháng 04/2025]  [K02 Thay đổi]  [K03 MoM %]  |
| - Tháng      |       2.271.969 người           −17.223 người      −0,75%     |
| - Cơ quan    +---------------------------------------------------------------+
| - Nghề nghiệp|  Đường: headcount theo từng tháng (03→06)   | Cột: Top 10     |
| - Cấp bậc    |  (mỗi điểm là một snapshot, không cộng)      | cơ quan theo HC |
|  [Xóa lọc]   |                                              | + K04 tỷ trọng  |
|              +---------------------------------------------+-----------------+
|              |  Cột xếp chồng 100%: cơ cấu theo nghề nghiệp / cấp bậc (K05),  |
|              |  có nhóm Unknown/REDACTED riêng                                 |
+--------------+---------------------------------------------------------------+
| Cách đọc: mỗi cột/điểm là một snapshot; không cộng các tháng.  Last refresh  |
+------------------------------------------------------------------------------+
```

Ghi chú: bản đồ địa lý đã **bỏ khỏi bố cục** (mục 2.1). Nếu TV2 sau này xác minh được ánh xạ địa điểm đủ tin cậy thì mới thêm lại.

### 5.3. Biểu đồ và tương tác

| Thành phần | Loại biểu đồ | Đo | Ghi chú |
|---|---|---|---|
| Card KPI | Card | K01, K02, K03 | K03 có định dạng điều kiện (mục 8) |
| Xu hướng 4 kỳ | Đường (line) | K01 theo `dim_month` | Chỉ nhận xét ngắn hạn; không dự báo |
| Top cơ quan | Cột ngang (bar), top 10 | K01 theo `dim_agency`; nhãn K04 | Có nhóm "Khác" nếu cần mẫu số đủ |
| Cơ cấu | Cột xếp chồng 100% | K05 theo nghề nghiệp hoặc cấp bậc (pay plan + grade) | Giữ nhóm Unknown/REDACTED, ví dụ `pay_plan` NULL (366 bản ghi tháng 03) |
| Bản đồ | (bỏ) | | **Chưa khả thi:** `duty_station` bị `REDACTED` khoảng 46% mỗi kỳ và có khoảng 17.000 mã; chỉ làm lại khi có ánh xạ địa điểm được TV2 xác minh |
| Drill-down | Hierarchy cơ quan → ... | | **Chỉ khi** có quan hệ cha–con chính thức |

**Tooltip:** "Headcount = số bản ghi Employment của một snapshot (cuối tháng). Không cộng các tháng. Một bản ghi không đồng nghĩa một người duy nhất qua các tháng."

### 5.4. DAX dự kiến

```dax
-- K01: headcount của tháng đang chọn (semi-additive: luôn lấy một tháng)
Headcount =
VAR m = MAX ( dim_month[month_key] )
RETURN
    CALCULATE ( COUNTROWS ( fact_employment_snapshot ), dim_month[month_key] = m )

-- Tháng liền trước có trong dữ liệu (bỏ lọc tháng để tìm)
Prev Month Key =
VAR m = MAX ( dim_month[month_key] )
RETURN
    CALCULATE ( MAX ( dim_month[month_key] ), ALL ( dim_month ), dim_month[month_key] < m )

Headcount Prev =
VAR pm = [Prev Month Key]
RETURN
    IF ( ISBLANK ( pm ), BLANK (),
         CALCULATE ( COUNTROWS ( fact_employment_snapshot ), dim_month[month_key] = pm ) )

-- K02
Headcount Change =
IF ( ISBLANK ( [Headcount Prev] ), BLANK (), [Headcount] - [Headcount Prev] )

-- K03 (DIVIDE trả BLANK khi mẫu số 0 hoặc BLANK)
Headcount MoM % = DIVIDE ( [Headcount Change], [Headcount Prev] )

-- K04: tỷ trọng cơ quan, mẫu số bỏ lọc cơ quan, giữ các lọc còn lại
Agency Share % =
DIVIDE ( [Headcount], CALCULATE ( [Headcount], REMOVEFILTERS ( dim_agency ) ) )
```

K05 dùng cùng mẫu với K04, thay `dim_agency` bằng chiều đang hiển thị (nghề nghiệp hoặc cấp bậc theo pay plan + grade) và chỉ dùng khi chiều đó `verified`. Chiều địa điểm không dùng cho K05 vì `REDACTED` khoảng 46%.

**Lưu ý:** ẩn dòng Total của bảng theo tháng, vì `Headcount` ở dòng Total trả về kỳ cuối chứ không phải tổng các tháng.

### 5.5. SQL đối chiếu (PostgreSQL, dự kiến)

```sql
-- K01: headcount theo tháng
SELECT m.month_key, COUNT(*) AS headcount
FROM dw.fact_employment_snapshot f
JOIN dw.dim_month m ON m.month_key = f.snapshot_month_key
WHERE m.month_key = 202504
GROUP BY m.month_key;

-- K02/K03: so với tháng liền trước (không lọc thêm nên cùng phạm vi)
WITH hc AS (
  SELECT snapshot_month_key AS month_key, COUNT(*) AS headcount
  FROM dw.fact_employment_snapshot
  GROUP BY snapshot_month_key
)
SELECT cur.month_key,
       cur.headcount,
       cur.headcount - prev.headcount AS change,
       ROUND(100.0 * (cur.headcount - prev.headcount) / NULLIF(prev.headcount, 0), 4) AS mom_pct
FROM hc cur
LEFT JOIN hc prev ON prev.month_key = (SELECT MAX(month_key) FROM hc WHERE month_key < cur.month_key)
ORDER BY cur.month_key;

-- K04: tỷ trọng cơ quan trong tháng 04
SELECT a.agency_code,
       COUNT(*) AS headcount,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4) AS share_pct
FROM dw.fact_employment_snapshot f
JOIN dw.dim_agency a ON a.agency_key = f.agency_key
WHERE f.snapshot_month_key = 202504
GROUP BY a.agency_code
ORDER BY headcount DESC;
```

Đối chiếu thêm với TV2: tổng `COUNT(*)` phải khớp tổng `SUM(count)` sau cast (trường `count` đều bằng 1 trong 12 file).

### 5.6. Câu chuyện dự kiến (storytelling)

| Bước | Nội dung |
|---|---|
| Bối cảnh/quyết định | Người hoạch định nhân lực cần biết quy mô hiện tại và mức thay đổi ngắn hạn trước khi xem xét nơi cần chú ý |
| Câu hỏi | Quy mô tháng 04/2025 là bao nhiêu và thay đổi thế nào so với tháng 03? |
| Bộ lọc | Tháng = 202504; không lọc cơ quan (toàn bộ) |
| Chỉ số/biểu đồ | K01, K02, K03; đường 4 kỳ; top cơ quan |
| So sánh | Tháng 04 so tháng 03; sau đó lọc một cơ quan lớn so với toàn bộ |
| Insight (dự kiến, chờ pipeline) | Headcount giảm ở cả ba kỳ liên tiếp theo số tổng kiểm (−0,75%, −0,74%, −0,59%); cơ quan lớn nhất (`VA`) chiếm khoảng 20,8% mỗi kỳ |
| Đề xuất / câu hỏi tiếp | Chuyển sang D3 để xem nhóm nào đóng góp vào mức giảm; chưa kết luận nguyên nhân |
| Giới hạn | Chỉ 4 kỳ, không đủ để nói xu hướng dài hạn hay mùa vụ |

---

## 6. D2 — Personnel Flows

### 6.1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Persona | Cán bộ theo dõi biến động nhân sự, cần biết lượt tiếp nhận/rời cơ quan theo kỳ và theo loại |
| Câu hỏi quản trị | (1) Mỗi kỳ có bao nhiêu lượt Accessions và Separations? (2) Loại hành động nào chiếm nhiều nhất? (3) Cơ quan nào phát sinh nhiều lượt nhất? |
| KPI | K06, K07, K08 (và chú thích K10 nếu có) |
| Kỳ thời gian | `report_month` mặc định. Tháng hiệu lực là góc nhìn phụ, phải ghi nhãn |
| Slicer | Tháng báo cáo; Cơ quan; Loại Accessions; Loại Separations |
| Nguồn | `fact_accessions`, `fact_separations` (hai Fact riêng, không nối với nhau) |

### 6.2. Bố cục (wireframe)

```
+------------------------------------------------------------------------------+
| [D1]  [D2 Personnel Flows]  [D3]                                             |
+--------------+---------------------------------------------------------------+
| SLICER       |  [K06 Accessions]   [K07 Separations]   [K08 Chênh lệch lượt] |
| - Tháng BC   |      7.153 lượt        24.088 lượt          −16.935 lượt      |
| - Cơ quan    +---------------------------------------------------------------+
| - Loại Acc.  |  Cột ghép theo tháng báo cáo:      | Cột ngang: Top category   |
| - Loại Sep.  |  Accessions vs Separations         | theo loại hành động       |
|  [Xóa lọc]   +------------------------------------+---------------------------+
|              |  Bảng/Cột: Top cơ quan theo lượt Accessions và Separations     |
+--------------+---------------------------------------------------------------+
| Cách đọc: đây là LƯỢT hành động, không phải thay đổi headcount. Last refresh |
+------------------------------------------------------------------------------+
```

### 6.3. Biểu đồ và tương tác

| Thành phần | Loại biểu đồ | Đo | Ghi chú |
|---|---|---|---|
| Card KPI | Card | K06, K07, K08 | K08 hiển thị kèm nhãn "lượt" |
| So sánh theo tháng | Cột ghép (clustered column) | K06 và K07 theo `report_month` | Ghi rõ kỳ báo cáo |
| Theo loại hành động | Cột ngang | K06 hoặc K07 theo category | Diễn giải theo codebook; không gán nghĩa ngoài codebook |
| Theo cơ quan | Bảng hoặc cột | K06, K07 theo `dim_agency` | Mỗi measure tính trên Fact của nó |
| Tháng hiệu lực | Trang tooltip hoặc trang phụ | K06/K07 theo `dim_effective_month` | Nhãn bắt buộc "theo tháng hiệu lực" |

**Tooltip:** "Số liệu theo **tháng báo cáo** (tháng của file). Tháng hiệu lực của hành động có thể khác. Theo profiling của TV2, trong file 202504 có 7.110 trong 7.153 bản ghi Accessions (99,4%) và 24.027 trong 24.088 bản ghi Separations (99,75%) có tháng hiệu lực trùng tháng file. Trong cả 4 kỳ có 593 bản ghi (269 Accessions, 324 Separations) có tháng hiệu lực khác tháng file; chưa có dấu thời gian gửi nên không kết luận là nộp chậm."

### 6.4. DAX dự kiến

```dax
-- K06: quan hệ active là fact_accessions[report_month_key] -> dim_month
Accessions = COUNTROWS ( fact_accessions )

-- K07
Separations = COUNTROWS ( fact_separations )

-- K08: tính từng Fact rồi trừ, không nối Fact với Fact.
-- Cả hai measure cùng bị lọc bởi dim_month và dim_agency dùng chung.
Event Difference =
IF ( ISBLANK ( [Accessions] ) && ISBLANK ( [Separations] ),
     BLANK (),
     [Accessions] - [Separations] )

-- Góc nhìn phụ theo tháng hiệu lực
Accessions by Effective Month =
CALCULATE ( [Accessions], USERELATIONSHIP ( fact_accessions[effective_month_key], dim_effective_month[month_key] ) )
```

`Accessions` và `Separations` phải dùng các Dimension dùng chung. Loại hành động của Accessions (`dim_accession_category`) không dùng được để lọc Separations và ngược lại; khi lọc category ở D2 cần ghi rõ slicer nào ảnh hưởng measure nào.

### 6.5. SQL đối chiếu (PostgreSQL, dự kiến)

```sql
-- K06, K07 theo tháng báo cáo, tính riêng từng nguồn rồi đặt cạnh nhau
SELECT m.month_key,
       COALESCE(a.cnt, 0) AS accessions,
       COALESCE(s.cnt, 0) AS separations,
       COALESCE(a.cnt, 0) - COALESCE(s.cnt, 0) AS event_difference
FROM dw.dim_month m
LEFT JOIN (SELECT report_month_key, COUNT(*) AS cnt FROM dw.fact_accessions  GROUP BY 1) a
       ON a.report_month_key = m.month_key
LEFT JOIN (SELECT report_month_key, COUNT(*) AS cnt FROM dw.fact_separations GROUP BY 1) s
       ON s.report_month_key = m.month_key
ORDER BY m.month_key;
```

Hai truy vấn con gộp riêng rồi nối theo **tháng** (Dimension), không nối từng dòng hai Fact với nhau. Với báo cáo hiển thị 0 hay BLANK cho kỳ không có dữ liệu, thống nhất với TV5: trong DAX là BLANK, trong SQL đối chiếu dùng `COALESCE` chỉ để so sánh, ghi chú rõ.

### 6.6. Câu chuyện dự kiến

| Bước | Nội dung |
|---|---|
| Bối cảnh/quyết định | Cán bộ theo dõi biến động muốn biết nơi phát sinh nhiều lượt hành động để chọn điểm cần kiểm tra thêm |
| Câu hỏi | Tháng báo cáo 04/2025 có bao nhiêu lượt tiếp nhận và rời cơ quan, chủ yếu thuộc loại nào? |
| Bộ lọc | Tháng báo cáo = 202504 |
| Chỉ số/biểu đồ | K06, K07, K08; cột theo loại hành động; top cơ quan |
| So sánh | Chuyển qua các tháng 03–06 |
| Insight (dự kiến, chờ pipeline) | Số lượt Separations lớn hơn Accessions ở cả bốn kỳ theo số tổng kiểm (04/2025: 24.088 so với 7.153); loại hành động chiếm nhiều nhất: `[điền sau khi chạy]` |
| Đề xuất / câu hỏi tiếp | Xem loại hành động nào chiếm nhiều theo codebook; không kết luận "nghỉ việc" hay "tuyển mới" nếu codebook chưa nói |
| Giới hạn | K08 không bằng thay đổi headcount; mỗi lượt là một bản ghi hành động, không phải một người duy nhất |

---

## 7. D3 — Workforce Changes (OLAP)

### 7.1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Persona | Chuyên viên HR analytics, cần so sánh hai snapshot và đi sâu vào nhóm đóng góp nhiều nhất |
| Câu hỏi quản trị | (1) Nhóm (cơ quan, nghề nghiệp, cấp bậc) nào đóng góp nhiều nhất vào mức tăng/giảm giữa hai kỳ? (2) Cấu trúc nhóm thay đổi thế nào? (3) Nơi nào cần điều tra thêm? |
| KPI | K02, K03, K09 (kèm K01 làm nền) |
| Kỳ thời gian | `snapshot_yyyymm`, kỳ hiện tại và kỳ liền trước (cùng định nghĩa) |
| Slicer | Tháng hiện tại; Cơ quan; Nghề nghiệp (chỉ khi `verified`); Cấp bậc (theo pay plan + grade) |
| Nguồn | `fact_employment_snapshot` |

### 7.2. Bố cục (wireframe)

```
+------------------------------------------------------------------------------+
| [D1]  [D2]  [D3 Workforce Changes]                                           |
+--------------+---------------------------------------------------------------+
| SLICER       |  [K02 Thay đổi tổng]   [K03 MoM %]   [Số nhóm tăng | giảm]     |
| - Tháng      +---------------------------------------------------------------+
| - Cơ quan    |  Thanh: Top 10 nhóm TĂNG   | Thanh: Top 10 nhóm GIẢM          |
| - Nghề nghiệp|  (K09, người)              | (K09, người)                     |
| - Cấp bậc    +----------------------------+----------------------------------+
|  [Xóa lọc]   |  Heatmap: cơ quan x nghề nghiệp/cấp bậc, giá trị = K02         |
|              |  Bảng xếp hạng thay đổi (màu/biểu tượng theo ngưỡng, mục 8)    |
|              |  Drill-through: chuột phải một cơ quan -> trang chi tiết nhóm  |
+--------------+---------------------------------------------------------------+
| Cách đọc: so hai snapshot, không giải thích nguyên nhân.  Last refresh       |
+------------------------------------------------------------------------------+
```

### 7.3. Biểu đồ và tương tác

| Thành phần | Loại biểu đồ | Đo | Ghi chú |
|---|---|---|---|
| Card KPI | Card | K02, K03 | |
| Top tăng/giảm | Hai cột ngang | K09 | Phải xử lý nhóm chỉ có ở một kỳ (không coi là 0 một cách ngầm) |
| Heatmap | Matrix với định dạng điều kiện | K02 theo cơ quan x nghề nghiệp/cấp bậc | Chỉ dùng chiều `verified` |
| Bảng xếp hạng | Bảng | K09, K03 theo nhóm | Có biểu tượng/màu theo ngưỡng minh họa |
| Drill-through | Trang chi tiết | Một cơ quan -> nghề nghiệp -> cấp bậc | **Ít nhất một** drill-through |
| Roll-up/Drill-down | Hierarchy | | Chỉ khi hierarchy có thật |

**Tooltip:** "Thay đổi là hiệu hai snapshot cùng phạm vi lọc. Không cho biết nguyên nhân (không có lịch sử từng nhân viên)."

### 7.4. DAX dự kiến

```dax
-- K09: đóng góp của từng nhóm (tái dùng Headcount Change của D1 trong ngữ cảnh nhóm)
Contribution = [Headcount Change]

-- Xếp hạng nhóm tăng nhiều nhất = 1 (ALLSELECTED giữ lọc người dùng)
Rank Increase =
RANKX ( ALLSELECTED ( dim_agency[agency_code] ), [Contribution], , DESC, DENSE )

Rank Decrease =
RANKX ( ALLSELECTED ( dim_agency[agency_code] ), [Contribution], , ASC, DENSE )

-- Nhóm có mặt ở một kỳ nhưng vắng ở kỳ kia: kiểm riêng, không đổi ngầm thành 0
Group Present Both Months =
VAR cur = [Headcount]
VAR prv = [Headcount Prev]
RETURN IF ( NOT ISBLANK ( cur ) && NOT ISBLANK ( prv ), 1, 0 )
```

### 7.5. SQL đối chiếu (PostgreSQL, dự kiến)

```sql
-- K09: thay đổi theo cơ quan giữa 202503 và 202504
WITH c AS (
  SELECT a.agency_code, COUNT(*) AS hc
  FROM dw.fact_employment_snapshot f
  JOIN dw.dim_agency a ON a.agency_key = f.agency_key
  WHERE f.snapshot_month_key = 202504
  GROUP BY a.agency_code
), p AS (
  SELECT a.agency_code, COUNT(*) AS hc
  FROM dw.fact_employment_snapshot f
  JOIN dw.dim_agency a ON a.agency_key = f.agency_key
  WHERE f.snapshot_month_key = 202503
  GROUP BY a.agency_code
)
SELECT COALESCE(c.agency_code, p.agency_code) AS agency_code,
       c.hc AS hc_cur, p.hc AS hc_prev,
       COALESCE(c.hc,0) - COALESCE(p.hc,0) AS change
FROM c FULL OUTER JOIN p ON c.agency_code = p.agency_code
ORDER BY change;
```

Kiểm điều kiện: nếu các nhóm rời nhau và bao phủ toàn bộ, tổng cột `change` phải bằng K02 của toàn hệ thống (−17.223 cho 04/2025).

### 7.6. Câu chuyện dự kiến

| Bước | Nội dung |
|---|---|
| Bối cảnh/quyết định | Chuyên viên HR analytics cần xác định nơi tập trung mức giảm để quyết định phân tích tiếp |
| Câu hỏi | Nhóm nào đóng góp nhiều nhất vào mức giảm headcount từ 03 sang 04/2025? |
| Bộ lọc | Tháng = 202504; lần lượt lọc theo cơ quan lớn nhất, rồi nghề nghiệp và cấp bậc nếu `verified` |
| Chỉ số/biểu đồ | K02, K09; hai biểu đồ top tăng/giảm; heatmap; drill-through |
| So sánh | Snapshot hiện tại và kỳ trước |
| Insight | `[điền sau khi chạy: nhóm đóng góp nhiều nhất, số người, tỷ lệ so với tổng thay đổi]` |
| Đề xuất / câu hỏi tiếp | Nhóm nào cần xem thêm ở kỳ sau; không khẳng định nguyên nhân từ dữ liệu chưa đo |
| Giới hạn | Không có lịch sử từng nhân viên; không suy diễn chuyển cơ quan hay thôi việc |

---

## 8. Cảnh báo bằng DAX và định dạng có điều kiện

Hai ví dụ tối thiểu (ngưỡng do nhóm đặt, **chỉ để minh họa**, không phải quy chuẩn của OPM). Ngưỡng nên đặt trong tham số để dễ chỉnh khi demo.

**Ví dụ 1 — Trạng thái MoM của card K03 (D1, D3):**

```dax
MoM Status =
VAR x = [Headcount MoM %]
RETURN
    SWITCH ( TRUE (),
        ISBLANK ( x ), "Chưa có kỳ trước",
        x <= -0.01,    "Giảm mạnh (ngưỡng minh họa: ≤ −1%)",
        x < 0,         "Giảm nhẹ",
        "Không giảm" )
```

Màu card: đỏ khi "Giảm mạnh", vàng khi "Giảm nhẹ", xanh khi "Không giảm", xám khi BLANK. Với số tổng kiểm hiện có (−0,75% ở 04/2025) card sẽ ở mức "Giảm nhẹ".

**Ví dụ 2 — Biểu tượng cho bảng xếp hạng thay đổi theo nhóm (D3):**

```dax
Group Trend Icon =
VAR g = [Headcount MoM %]
VAR overall = CALCULATE ( [Headcount MoM %], REMOVEFILTERS ( dim_agency ) )
RETURN
    SWITCH ( TRUE (),
        ISBLANK ( g ), "—",
        g < overall - 0.005, "▼ giảm nhanh hơn mức chung (ngưỡng minh họa: 0,5 điểm %)",
        g > overall + 0.005, "▲ tốt hơn mức chung",
        "● gần mức chung" )
```

Báo cáo trong tài liệu thuyết minh: các trường hợp BLANK, mẫu số 0 và thiếu kỳ trước.

## 9. Bộ test đối soát SQL–DAX (đề xuất, ít nhất 10)

Chuẩn "ít nhất 10 test" là chuẩn nhóm tự đặt. Giá trị kỳ vọng lấy từ profiling TV2 (REVIEW), TV5 sẽ kiểm độc lập trước khi PASS. Nguồn đối soát ghi trong `reports/dashboard_kpi_reconciliation.csv` sau khi có pipeline.

| Mã | KPI | Bộ lọc | Kỳ vọng (từ profiling TV2) | Ghi chú |
|---|---|---|---:|---|
| T01 | K01 | Tháng 202503 | 2.289.192 | |
| T02 | K01 | Tháng 202504 | 2.271.969 | |
| T03 | K01 | Tháng 202506 | 2.241.780 | |
| T04 | K02 | 202504 | −17.223 | |
| T05 | K03 | 202504 | −0,7524% | |
| T06 | K02 | 202503 | BLANK | Kỳ đầu, không có kỳ trước |
| T07 | K04 | Cơ quan `VA`, 202504 | ≈ 20,7582% | Mẫu số bỏ lọc cơ quan |
| T08 | K06 | Tháng báo cáo 202504 | 7.153 | |
| T09 | K07 | Tháng báo cáo 202504 | 24.088 | |
| T10 | K08 | 202504 | −16.935 | Không bằng K02 |
| T11 | K08 | 202506 | −9.993 | 9.954 − 19.947 |
| T12 | K06 | Cơ quan `IN`, 202504 | 1.553 | Top cơ quan Accessions tháng 04 theo profiling |
| T13 | Tổng nhóm | Tổng thay đổi theo cơ quan 03→04 | −17.223 | Các nhóm rời nhau, cộng về K02 |
| T14 | K01 | Không chọn tháng (không lọc) | Không phải 9.057.997 | Phải trả đúng một kỳ hoặc BLANK, không cộng bốn tháng |

## 10. Phụ thuộc và câu hỏi còn mở

| Chủ đề | Cần từ ai | Ảnh hưởng | Hạn dự kiến |
|---|---|---|---|
| Danh sách trường/mã `verified` (cơ quan, nghề nghiệp, cấp bậc, category) | TV2 | Audit G2 đã bàn giao (PR #42, REVIEW): các quan hệ đang **PARTIAL**, Grade **UNSUPPORTED**; cần TV3/TV5 review và đối chiếu danh mục lịch sử | Theo PR #42 |
| Ánh xạ địa điểm đủ tin cậy (để làm lại bản đồ D1, chiều địa điểm) | TV2 | `duty_station` bị `REDACTED` khoảng 46%; chưa có ánh xạ | Chưa có hạn |
| Tên bảng/cột thật trong DW | TV3 (và bus matrix của TV4) | Schema đã có (`dw`, `mart`...); tên cột Fact/Dim đổi trong DAX/SQL khi có DDL | 23/11 (L3-07) |
| Phương án TV4 kết nối PostgreSQL | TV3 (L3-03) | Làm `.pbix` MVP | 19–20/11 |
| Ngưỡng cảnh báo | TV1 xác nhận | Mục 8 | Khi review |
| Chọn locale hiển thị số (dấu chấm hay phẩy) | Cả nhóm | Mục 4.2 | Khi dựng D1 |
| Phương án công bố | TV1 hỏi thầy | Trang public (R02 bị chặn Publish to web) | Theo `docs/10_publish_feasibility.md` |

## 11. Điều kiện PASS cho L4-02 (để TV1 review)

- [ ] Mỗi trang D1/D2/D3 có persona, câu hỏi, KPI, kỳ thời gian, slicer, chart, drill, tooltip, DAX dự kiến, SQL đối chiếu, câu chuyện
- [ ] Không có chỗ nào cộng nhiều snapshot thành headcount
- [ ] Không có chỗ nào nối Fact với Fact; K08 tính từng Fact rồi so sánh
- [ ] K08 không bị gọi là thay đổi headcount
- [ ] Ba wireframe đã vẽ và xuất ảnh (xem mục 12)
- [ ] TV1 xác nhận cả ba trang trả lời được câu hỏi nghiệp vụ (ghi tên, nhận xét, PASS/FAIL trong issue #31)

## 12. Wireframe dạng ảnh 

Các sơ đồ ASCII ở mục 5.2, 6.2, 7.2 là bản phác. TV4 vẽ lại ba trang trang trống trong Power BI Desktop, xuất PNG và đặt vào `docs/diagrams/`:

- `docs/diagrams/10_wireframe_D1.png`
- `docs/diagrams/10_wireframe_D2.png`
- `docs/diagrams/10_wireframe_D3.png`

Sau đó chèn vào tài liệu bằng `![D1](img/10_wireframe_D1.png)` ở đầu mục 5, 6, 7.


