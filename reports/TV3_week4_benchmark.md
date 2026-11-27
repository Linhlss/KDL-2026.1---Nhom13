# Benchmark L3-15 — Fact vs Mart và trước/sau index

**Issue:** #55. **Người chạy:** TV1 (Linh), thay TV3 theo phân công lại ngày 27/11/2026. **TV5 cần chạy lại độc lập** để nghiệm thu.

- **Máy:** Apple M1 (8 nhân, 16 GB RAM), macOS.
- **PostgreSQL:** 17.12, `shared_buffers = 128MB`, `work_mem = 4MB`, `max_parallel_workers_per_gather = 2`.
- **DB benchmark:** `workforce_dw_g3_bench`, chứa đủ 12 file G3. Đây là DB riêng, không phải DB bàn giao.
- **Mã:** [`sql/tests/09_benchmark.sql`](../sql/tests/09_benchmark.sql) và [`evidence/TV3_week4/run_benchmark.py`](../evidence/TV3_week4/run_benchmark.py).
- **Cách đo:** mỗi biến thể chạy 1 lần làm nóng (không tính), rồi **3 lần đo** bằng `EXPLAIN (ANALYZE, BUFFERS)`. Bảng dưới dùng **trung vị**; cache đã nóng.
- **Dữ liệu thô:** [`reports/week4/benchmark_results.csv`](week4/benchmark_results.csv). **Plan đầy đủ:** `evidence/TV3_week4/benchmark_explain_*.txt`.

## Kết quả

| Test | Câu hỏi | Biến thể | Trung vị (ms) | 3 lần đo (ms) | Plan chính |
|---|---|---|---:|---|---|
| B1 | K01 theo cơ quan, tháng 04/2025 | FACT (9.057.997 dòng) | **320,4** | 320,4 · 324,3 · 318,3 | Parallel Seq Scan trên `fact_employment_snapshot` |
| B1 | | MART (510 dòng) | **0,05** | 0,052 · 0,050 · 0,049 | Seq Scan trên `workforce_monthly` |
| B2-SEP | Sự kiện nghỉ việc theo tháng hiệu lực của TR | BEFORE (không index) | **5,6** | 5,76 · 5,62 · 5,49 | Seq Scan trên `fact_separations` |
| B2-SEP | | AFTER: index `(agency_code, effective_month_key)` | **1,2** | 1,27 · 1,24 · 1,18 | Bitmap Index Scan → Bitmap Heap Scan |
| B2-EMP | Headcount theo tháng của TR | BEFORE (không index) | **216,0** | 215,7 · 216,7 · 216,0 | Parallel Seq Scan |
| B2-EMP | | AFTER: index `(agency_code, snapshot_month_key)` | **274,8** | 279,6 · 271,7 · 274,8 | Parallel Bitmap Heap Scan, bị lossy |

**Kiểm tính đúng trước khi so thời gian:**
- B1: kết quả Fact và Mart trùng nhau hoàn toàn (`EXCEPT` hai chiều = 0 dòng).
- B2: kết quả trước và sau index giống nhau.

## Nhận xét

1. **Mart là lựa chọn đúng cho dashboard.** Cùng câu hỏi K01 theo cơ quan, Mart trả lời trong khoảng 0,05 ms so với khoảng 320 ms trên Fact, tức **nhanh hơn khoảng 6.400 lần**, với kết quả giống hệt. Power BI chỉ đọc Mart (510 dòng thay vì 9,06 triệu dòng), nên refresh và tương tác không phụ thuộc kích thước Fact.
2. **Index có lợi khi bộ lọc chọn lọc trên bảng nhỏ.** Ở B2-SEP, mã TR chiếm khoảng 6.200 trên 92.511 dòng. Index giảm thời gian **khoảng 4,5 lần**.
3. **Index không có lợi khi bộ lọc ít chọn lọc trên Fact lớn.** Ở B2-EMP, mã TR chiếm khoảng 456 nghìn dòng (≈5%) và rải trên nhiều trang dữ liệu.
   - Với `work_mem = 4MB`, bitmap bị chuyển sang dạng *lossy* (14.430 trang exact, 22.428 trang lossy). PostgreSQL phải kiểm lại khoảng **1,4 triệu dòng**, nên chậm hơn quét tuần tự song song (**+27%**).
   - **Kết luận thiết kế:** với truy vấn phân tích theo cơ quan, dùng Mart tổng hợp. Không thêm index `agency_code` vào Fact Employment. Ở điều kiện này, planner chọn bitmap vì ước lượng chi phí, nhưng trên thực tế lại chậm hơn.
4. **Giới hạn của phép đo:**
   - Chỉ đo trên một máy, với dữ liệu 4 tháng và cache đã nóng.
   - Chưa thử tăng `work_mem`; khả năng cao bitmap sẽ hết lossy khi tăng.
   - Chưa đo thời gian refresh Power BI; TV4/TV5 bổ sung.

## Việc còn lại

- [ ] TV5 chạy lại `evidence/TV3_week4/run_benchmark.py --operator TV5` trên máy của TV5 (DB benchmark riêng), ghi vào cùng file CSV, rồi so xu hướng.
- [ ] TV4 đo thời gian refresh PBIX khi đọc Mart, để bổ sung vào phần nghiệm thu hiệu năng (L3-17).
