# L2-14 · Đối chiếu nguồn Parquet với Mart

**25/11/2026 · TV2 REVIEW.** Phạm vi là bốn kỳ 03–06/2025 và ba KPI K01, K06, K07. Nguồn là 12 Parquet đã khóa SHA-256. Phía Mart dùng bản xuất SQL thực chạy trên PostgreSQL của TV3 tại commit `3a1a619`, với kiểm tra chéo từ manifest và J06 cùng lần chạy. Phạm vi này là số liệu SQL của G3. [Kế hoạch L2-14](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/main/Phan_cong_DW_BI_Nhom13_5_5_tuan_V3.md#L129) · [Bằng chứng TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/tree/3a1a6199df53cfa9ef5dbc556a146c844c378f87/reports/week3)

## Kết quả đối chiếu

Cả **36 phép đối chiếu** khớp khi dùng cùng kỳ và cùng bộ lọc. K01 theo tháng snapshot. K06 và K07 theo tháng báo cáo của file. Mỗi kỳ có ba phạm vi Agency gồm toàn hệ thống, mã `AF` và nhóm `UNKNOWN`. Toàn hệ thống bao gồm nhóm `UNKNOWN`. Bảng CSV ghi số từ từng bên, hiệu `Mart − nguồn` và nguyên nhân cho từng phép kiểm. [Bảng 36 phép đối chiếu](TV2_l2_14_source_mart.csv)

| Kỳ | K01 nguồn = Mart | K06 nguồn = Mart | K07 nguồn = Mart |
| --- | ---: | ---: | ---: |
| 03/2025 | 2.289.192 | 4.862 | 22.061 |
| 04/2025 | 2.271.969 | 7.153 | 24.088 |
| 05/2025 | 2.255.056 | 8.813 | 26.415 |
| 06/2025 | 2.241.780 | 9.954 | 19.947 |

Tổng cộng có **9.181.290 bản ghi nguồn qua bốn kỳ**, với `count = 1` ở mọi dòng. K01 mô tả số bản ghi trong từng snapshot. [KPI theo tháng của TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/3a1a6199df53cfa9ef5dbc556a146c844c378f87/reports/week3/05_kpi_monthly.csv)

## Vì sao hai cách tính có thể khác

- **Kỳ thời gian.** Có 269 Accessions và 324 Separations có tháng hiệu lực khác tháng báo cáo. Cả 593 dòng có tháng hiệu lực trong 03–06/2023 theo giá trị nguồn. Nếu đổi tháng 04/2025 sang lọc theo hiệu lực, K06 thành **7.110** và K07 thành **24.027**. Mart luồng hiện tổng hợp theo tháng báo cáo. [KPI Dictionary](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/main/docs/02_kpi_dictionary.csv#L7)
- **Bộ lọc Agency.** Mã `AF` có K01 **171.750** ở tháng 03 và **170.447** ở tháng 04, nên K02 của mã này là **−1.303**. `agency_key` của `AF` lần lượt là 15 và 139. So sánh qua tháng cần giữ cùng `agency_code`. [Bản xuất theo Agency](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/3a1a6199df53cfa9ef5dbc556a146c844c378f87/reports/week3/05_kpi_agency.csv)
- **Nhóm Unknown.** Để khớp cách tra mã của TV3, TV2 dùng đúng lookup cùng commit. Mã được so nguyên văn theo tháng báo cáo và cần đúng một nhãn `READY`. Ví dụ, bỏ Agency Unknown tháng 04 làm tổng giảm **206.687 Employment**, **1.591 Accessions** và **1.936 Separations**. [Số dòng Unknown theo file](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/3a1a6199df53cfa9ef5dbc556a146c844c378f87/reports/week3/09_source_quality.csv#L5)

## Chênh lệch trong bản xuất chi tiết Agency

Bản xuất theo Agency dùng Workforce Mart làm bảng bên trái. Các nhóm chỉ có trong Mart sự kiện bị bỏ khỏi file chi tiết. Kết quả gồm **42 lượt ở 14 tổ hợp kỳ/KPI/Agency**. Tổng Mart theo tháng vẫn khớp Parquet và số đo `mart_measure` của J06. [Danh sách mã và số lượt bị thiếu ở bản xuất](TV2_l2_14_mart_export_gaps.csv) · [SQL đang xuất](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/3a1a6199df53cfa9ef5dbc556a146c844c378f87/sql/07_g3_kpi.sql#L19)

| Kỳ | KPI | Tổng Mart | Cộng từ bản xuất Agency | Bản xuất thiếu |
| --- | --- | ---: | ---: | ---: |
| 03/2025 | K07 | 22.061 | 22.060 | 1 |
| 04/2025 | K06 | 7.153 | 7.130 | 23 |
| 04/2025 | K07 | 24.088 | 24.070 | 18 |

TV3 có thể xuất từ tập khóa hợp lại của hai Mart để giữ các cơ quan chỉ có sự kiện. Cột headcount của nhóm chỉ có sự kiện giữ giá trị NULL.

```sql
WITH agency_month AS (
    SELECT month_key, agency_key FROM mart.workforce_monthly
    UNION
    SELECT month_key, agency_key FROM mart.personnel_flows_monthly
)
SELECT g.month_key, g.agency_key, d.agency_code, d.agency_label,
       w.headcount, COALESCE(f.accessions, 0) AS accessions,
       COALESCE(f.separations, 0) AS separations
FROM agency_month g
JOIN dw.dim_agency d USING (agency_key)
LEFT JOIN mart.workforce_monthly w USING (month_key, agency_key)
LEFT JOIN mart.personnel_flows_monthly f USING (month_key, agency_key)
WHERE g.month_key BETWEEN 202503 AND 202506
ORDER BY g.month_key, d.agency_code;
```

## Rà soát lần hai và cách chạy lại

1. Đối chiếu định danh file, số dòng và SHA-256 của cả 12 file với TV1 và bảng số dòng G3. Xác minh byte của inventory và bảy file mã trong run manifest của TV3.
2. Tính lại từ Parquet bằng PyArrow theo batch, độc lập với truy vấn nhóm của DuckDB. Hai cách khớp cả số theo Agency và phân bố tháng nghiệp vụ từng file.
3. Kiểm lại **486 dòng xuất chi tiết** với nhóm nguồn tương ứng. Bốn kỳ có tổng Mart khớp J06, khóa ODS → Fact đều có 0 sai biệt. Tất cả 42 lượt chênh trong bản xuất chi tiết được giải thích bằng nhóm sự kiện vắng ở phía Workforce. [J06 của TV3](https://github.com/Linhlss/KDL-2026.1---Nhom13/blob/3a1a6199df53cfa9ef5dbc556a146c844c378f87/reports/week3/07_reconciliation.csv)
4. Thử SQL đề xuất trên mô hình kiểm tra tái dựng từ bản xuất và các nhóm sự kiện bị thiếu. Kết quả có **496 nhóm tháng/Agency**, giữ headcount NULL cho 10 nhóm chỉ có sự kiện và khớp tổng K01, K06, K07 ở cả bốn kỳ.

Chạy tại gốc repo sau khi có Python, DuckDB và PyArrow. Git fetch giúp lấy đúng commit chứa bản xuất Mart đã kiểm.

```powershell
git fetch origin tv3/g2-pipeline
$tv2Raw = 'E:\TV2_Data_Profiling\data\raw'
python -X utf8 -B evidence/TV2_week4/reconcile_source_mart.py $tv2Raw
```

**Kết luận TV2:** 36/36 phép đối chiếu đúng kỳ và bộ lọc đạt. TV3 xem lại phạm vi nhóm trong truy vấn xuất Agency trước khi dùng file chi tiết để phân tích. Phạm vi Power BI/DAX nhiều tháng tiếp tục do TV4 và TV5 kiểm độc lập.
