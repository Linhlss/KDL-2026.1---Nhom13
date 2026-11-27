# GIẢI TRÌNH TÍCH HỢP PIPELINE G3 CỦA TV3 VÀ SỬA LỖI TRƯỚC KHI BÀN GIAO TV4

**Người thực hiện:** TV1 (trưởng nhóm), với agent Claude Code hỗ trợ. **Ngày:** 27/11/2026.
**Nhánh:** `tv1/g3-integration` → `main`. Nhánh này thay thế PR #43 và giữ nguyên toàn bộ commit của TV3 trong lịch sử.
**Phạm vi:** sửa các lỗi còn tồn đọng trong pipeline G2/G3 của TV3 (PR #43, #44, #47), chạy lại đủ 12 file, tạo lại dump và bằng chứng, rồi đưa lên `main` để TV4 bắt đầu dashboard.

> **Cập nhật đợt 2 (27/11/2026, mục 11):** TV1 làm thêm các việc mở đang chặn TV4.
> - Gộp nhánh `codex/g2-alignment` của TV2 (#53).
> - Thêm Mart category cho D2 (#51) và Mart K10 (#52).
> - Chạy benchmark L3-15 (#55).
>
> Dump bàn giao hiện tại là **`3b467c00…`**, thay cả `ec3ddf32…`. Các số liệu "sau" ở mục 4 vẫn đúng. Mục 11 ghi phần bổ sung.

## 1. Kết luận nhanh

| Câu hỏi | Trả lời |
|---|---|
| Lỗi của TV3 đã sửa hết chưa? | **Đã sửa 6/6 phát hiện của lần review PR #43**: 2 lỗi chặn merge và 4 lỗi nhỏ. Không còn lỗi kỹ thuật nào đang mở trong phần pipeline. |
| Dữ liệu đã lên repo chưa? | **Đã có trên `main`**: mã ETL/SQL/test, kết quả G3 trong `reports/week3/`, bằng chứng và **dump G3 mới** tại `handoff/TV3_G3/workforce_g3.dump` (SHA-256 `3b467c00…` sau đợt 2; bản đợt 1 là `ec3ddf32…`). |
| TV4 bắt đầu được chưa? | **Được.** `git pull` `main`, restore dump mới theo `handoff/TV3_G3/README.md`, làm mới PBIX. Không dùng các dump cũ `6d85ea29…` và `ec3ddf32…`. |
| Bỏ phần nào của TV3? | **Không bỏ gì.** Toàn bộ mã, test, tài liệu, sơ đồ và dump G2 được giữ. Chỉ các kết quả chạy cũ (CSV G3, log, dump G3) được thay bằng lượt chạy mới; bản cũ vẫn còn trong lịch sử Git. |

## 2. Bối cảnh

- PR #43 của TV3 (pipeline G2, kéo theo G3 của PR #44/#47) **không merge được** vì bị xung đột, nên `main` chưa có pipeline hay dump nào.
- GitHub hiển thị 148 file vì PR được tạo từ một base cũ. So với `main` hiện tại, PR thực chất chỉ có **102 file**: 93 file mới và 9 file sửa. **Không file nào của TV2 bị ghi đè.**
- Lần review của TV1 tìm ra 6 lỗi (mục 3). Lỗi nghiêm trọng nhất làm sai dashboard theo cơ quan.

## 3. Các lỗi đã sửa

| # | Mức | Lỗi | Nguyên nhân | Cách sửa | File |
|---|---|---|---|---|---|
| 1 | **Chặn merge** | **846.942 dòng (≈9,17% headcount) rơi vào Agency Unknown.** Bộ Tài chính, Bộ Nội vụ, NASA, HUD, FQ, AH, HB hiển thị 0 khi lọc theo cơ quan. | Bảng tra cứu chỉ nhận mã `READY`. 7 mã này ở trạng thái `REVIEW` chỉ vì nhãn Parquet khác EHRI. TV2 đã duyệt cả 28 khóa–tháng là `ABBREVIATION` (`ehri_label_review_131.csv`, 23/11) nhưng pipeline chưa dùng kết quả này. | Nạp kết quả duyệt vào bảng mới `ref.label_review`. Mã `REVIEW` được dùng khi TV2 kết luận chỉ khác cách viết (`ABBREVIATION`, `FORMATTING`, `TEXT_VARIANT`, `DOCUMENTED_RENAME`, `APOSTROPHE_REPAIR`). Nhãn hiển thị là `proposed_display_label`, `verification_status = 'REVIEWED_TV2'`. `HOLD_ORG_SCOPE` và mã chưa duyệt vẫn ở Unknown. | `etl/g2_model.py`, `etl/g2_pipeline.py`, `sql/00_raw_ref_ods_ddl.sql`, `tests/g2_model_checks.py` |
| 2 | **Chặn merge** | PR #43 xung đột với `main`. | Tracker `.xlsx` (file nhị phân) bị cả TV3 lẫn `main` sửa. | Lấy bản của `main`, chép 26 ô TV3 đã sửa (L3-10…L3-13, H07) ở mức XML, dùng style sẵn có. Đối chiếu 2.335 ô: không lệch, giữ định dạng có điều kiện. | `Progress_Tracker_DW_BI_Nhom13_5_5_tuan.xlsx` |
| 3 | Nhỏ | J06 so headcount của Mart theo tháng snapshot với số dòng của file, nên sẽ báo FAIL sai khi có dòng lệch tháng. | Mart Employment nhóm theo `snapshot_month_key`. | So Mart với Fact theo đúng vai trò thời gian của Mart. | `etl/g2_pipeline.py` |
| 4 | Nhỏ | Truy vấn KPI theo cơ quan bỏ sót cơ quan chỉ có tuyển dụng/nghỉ việc. | `LEFT JOIN` bắt đầu từ Mart headcount. | Đổi sang `FULL JOIN`. Tên cột giữ nguyên, nên script đọc kết quả không phải sửa. | `sql/07_g3_kpi.sql` |
| 5 | Nhỏ | DDL của DB chuyển giao chép lại bằng tay, dễ lệch bản gốc. | `06_g2_transfer.sql` là bản chép của 03/04. | `g2_transfer.py` so từng `CREATE TABLE` với 03/04 và từ chối chạy nếu lệch. | `etl/g2_transfer.py` |
| 6 | Nhỏ | Có thể lỗi đọc file trên Windows (TV3/TV4/TV5). | `read_text()` không chỉ định encoding. | Đọc SQL/manifest/JSON bằng UTF-8 ở mọi chỗ. | `etl/*.py`, `tests/g3_full_checks.py`, `evidence/TV3_week3/prepare_review.py` |

**Sửa thêm trong công cụ tạo bằng chứng:** `prepare_review.py` ghi cứng tên DB, máy và số nhóm Mart của lượt chạy ngày 23/11. Nay script lấy các giá trị này từ `run_manifest.json`, từ git và từ DB, và có thêm tham số `--operator`.

## 4. Kết quả trước và sau

| Chỉ số | Trước (dump `6d85ea29…`, 25/11) | Sau (dump `ec3ddf32…`, 27/11) |
|---|---:|---:|
| Agency Unknown — Employment (4 kỳ) | 830.229 dòng | **0** |
| Agency Unknown — Accessions / Separations | 6.185 / 10.528 | **0 / 0** |
| `dw.dim_agency` | 493 | **521** (+28 khóa cơ quan–tháng đã duyệt) |
| `mart.workforce_monthly` / `personnel_flows_monthly` | 486 / 340 nhóm | **510 / 361** nhóm |
| K01 / K06 / K07 tháng 03…06 | 2.289.192 · 2.271.969 · 2.255.056 · 2.241.780 / 4.862 · 7.153 · 8.813 · 9.954 / 22.061 · 24.088 · 26.415 · 19.947 | **Không đổi** |
| K02 / K08 tháng 04 | −17.223 / −16.935 | **Không đổi** |
| Ví dụ tháng 04: Bộ Tài chính (TR) | thuộc Unknown | **114.791 người**, nhãn "DEPARTMENT OF THE TREASURY" [REVIEWED_TV2] |
| Ví dụ tháng 04: Bộ Nội vụ / NASA / HUD | thuộc Unknown | 63.962 / 17.868 / 8.581 |

## 5. Kiểm thử đã chạy (máy TV1, macOS, PostgreSQL 17.12, Python 3.13)

| Bước | Kết quả | Bằng chứng |
|---|---|---|
| Nhận nguồn: 12 Parquet khớp SHA-256, bytes, số dòng, schema | 12/12 VERIFIED | `evidence/TV3_week3/00_receive_sources.txt` |
| 4 bộ hồi quy của TV3 (G3 synthetic, source, model, replay) | Đều PASS, gồm ca mới "REVIEW đã duyệt được nạp, HOLD vẫn Unknown" | `01`–`04_*.txt` |
| Chạy đầy đủ G3 trên DB mới `workforce_dw_g3_tv1` (khoảng 23 phút) | 12 file Source = Staging = ODS = Fact; tổng 9.181.290 dòng | `05_full_pipeline.txt`, `reports/week3/07_file_counts.csv` |
| J06 bốn kỳ | 84 PASS + 12 PENDING (phần DAX chờ TV4) | `reports/week3/07_reconciliation.csv` |
| Kiểm trực tiếp Parquet ↔ ODS, ordinal, vai trò thời gian, FK | 152/152 PASS | `reports/week3/09_quality_checks.csv` |
| Chạy lại tháng May, so snapshot 15 bảng | 15/15 PASS, khóa Dimension ổn định | `reports/week3/TV3_week3_rerun_results.csv` |
| Assertion SQL 12 file và bốn tháng | PASS | `07_sql_assertions.txt` |
| Tạo DB chuyển giao, dump, restore và so từng dòng | PASS 5 bảng, KPI bốn kỳ | `06_transfer_restore.txt` |
| Restore đúng file bàn giao: checksum, số dòng, KPI, Unknown = 0, nhãn TR/IN/NN/HU | PASS | `12_dump_handoff_check.txt` |
| `prepare_review.py`: hash code khớp lượt chạy, 20 báo cáo G2 giữ nguyên byte, giữ 593 event lệch kỳ | PASS | `00_environment_and_commands.txt` |

## 6. Giữ lại và thay thế

- **Giữ nguyên từ TV3:**
  - `etl/` (6 file), `sql/` (7 file và `sql/tests/`), `tests/` (5 file), runbook G2/G3, sơ đồ kiến trúc/ETL/DW.
  - Dump G2 (bằng chứng cho MVP K01 của TV4, PR #46) và hướng dẫn replay cho TV5.
- **Được tạo lại** (bản cũ vẫn trong lịch sử Git):
  - Kết quả và log: `reports/week3/*`, `reports/TV3_week3_summary.md`, `reports/TV3_week3_open_items.csv`.
  - Bằng chứng: `evidence/TV3_week3/00`–`08`, `12`.
  - Dump bàn giao: `handoff/TV3_G3/workforce_g3.dump` và `.sha256`.
- **Giữ làm lịch sử, có thêm ghi chú:** `evidence/TV3_week3/10_final_review.md`, `11_clean_checkout_review.txt` (biên bản ngày 23/11 của TV3), `docs/07_runbook.md` (số Unknown của G2).
- **Không bị ảnh hưởng:** mọi file của TV2 và các file `docs/`/`evidence/` của TV4 trên `main`.

## 7. Ảnh hưởng và việc cần làm tiếp

| Ai | Việc | Hạn đề xuất |
|---|---|---|
| **TV4** | 1. `git pull` `main`; restore **dump mới** vào database mới; làm mới PBIX. 2. Chụp lại các ảnh có nhóm Unknown trong PR #48 (`07_g3_dax_unknown`, `11/12_g3_report_unknown_*`, `14_g3_sql_unknown`), vì Unknown nay bằng 0. Ảnh tổng K01/K06/K07 và ảnh cơ quan AF giữ nguyên số, nhưng nên chụp lại từ database mới để cùng một nguồn. 3. Cập nhật số Unknown cũ (206.687 / 1.591 / 1.936) trong `docs/09_bus_matrix.md` và `docs/10_dashboard_specs.md`. 4. Dựng D1–D3. Hiện có đủ dữ liệu cho K01–K04 và K06–K08. | Ngay |
| **TV3** | 1. Review commit `51ab0d9` (sửa Unknown và 4 lỗi nhỏ). 2. Từ nay làm tiếp trên `main`, không dùng nhánh `tv3/g2-pipeline` cũ. 3. Phối hợp TV4 chốt Mart mở rộng (nghề, ngạch/bậc, địa điểm) nếu dashboard cần K05/K09. | 28/11 |
| **TV2** | Xác nhận cách dùng kết quả duyệt nhãn (mục 3, lỗi 1); quyết định số phận các mã `HOLD_ORG_SCOPE` (AF4F, ARE1, chỉ ở cấp đơn vị con). | 28/11 |
| **TV5** | Chạy lại độc lập trên database riêng theo runbook G3 với commit trên `main`; ký kết quả QA. | Trước nghiệm thu G3 |
| **TV1** | Theo dõi TV4 làm mới PBIX; điều phối nghiệm thu G3; cập nhật tracker khi có kết quả review. | — |

## 8. Giới hạn còn mở (không phải lỗi pipeline)

1. **K05 và K09** cần chiều nghề, ngạch/bậc hoặc địa điểm. Hai Mart hiện chỉ có tháng × cơ quan; đây là quyết định thiết kế còn chờ TV4/TV3 (`G3-D03`).
2. Mô hình vẫn **PROPOSED, chờ TV4 duyệt**. SQL–DAX và QA độc lập của TV5 vẫn **PENDING**.
3. **Môi trường:** TV1 chạy trên PostgreSQL 17.12 macOS; runbook ghi PostgreSQL 18. Mã chỉ dùng tính năng từ bản 16 trở lên, và dump 17 restore được trên 18. Lượt chạy trên Windows/PostgreSQL 18 vẫn cần TV4/TV5 xác nhận.
4. Nhãn cơ quan vẫn là **PARTIAL / REVIEWED_TV2**, chưa phải danh mục chính thức đã xác minh đầy đủ. Hai mã đơn vị con `HOLD_ORG_SCOPE` không được dùng.
5. Thay thế bằng bản republish thật của nguồn vẫn **NOT_TESTED** (`G3-D06`).

## 9. Cách kiểm lại

```sh
git switch main && git pull
python etl/fetch_baseline.py --raw-dir <thư mục 12 Parquet>
python tests/g2_model_checks.py --config configs/.env.g3.local
createdb workforce_dw_g3_check
python -u etl/g3_pipeline.py --config configs/.env.g3.local --database workforce_dw_g3_check \
  --raw-dir <thư mục 12 Parquet> --report-dir .qa/TV5_G3/run01 --verify-rerun --quality-check
psql -d workforce_dw_g3_check -f sql/tests/08_g3_full_baseline.sql
psql -d workforce_dw_g3_check -c "SELECT count(*) FROM dw.fact_employment_snapshot WHERE agency_key = 0"   -- kỳ vọng 0
```

## 10. Commit và PR

| Commit | Nội dung |
|---|---|
| `9b639cb` | Merge nhánh `tv3/g2-pipeline` (G2 + G3 của TV3) vào bản sao `main`; gộp tracker theo từng ô |
| `51ab0d9` | Dùng kết quả duyệt nhãn EHRI của TV2; sửa J06, KPI `FULL JOIN`, kiểm DDL chuyển giao, UTF-8; thêm regression |
| (commit cuối) | Chạy lại G3, dump mới, bằng chứng, tài liệu và file giải trình này |

PR tích hợp và trạng thái merge được ghi trong bình luận trên PR #43 và PR #48.

## 11. Đợt 2 — xử lý nốt các việc mở đang chặn TV4 (27/11/2026)

Sau khi PR #49 merge, còn bốn việc mở. Trong đó ba việc chặn trực tiếp TV4: D2 theo category, K10, và nhánh TV2 đụng vào pipeline. TV1 xử lý ngay thay vì chờ TV3, vì TV4 đang ở giai đoạn dashboard. Các issue tương ứng được chuyển sang `status: REVIEW` để TV3/TV2/TV5 kiểm.

| Issue | Việc đã làm | File |
|---|---|---|
| #53 | **Gộp nhánh `codex/g2-alignment` của TV2.** Cherry-pick `aaee4ce`, `dfc3cc5` (giữ tác giả, có `-x`). Xung đột ở `g2_model.py` và `g2_pipeline.py` được gộp bằng cách **giữ cả hai bên**: logic `ref.label_review` của TV1, cộng với `lookup_state_sql()` của TV2 (REDACTED không phân biệt hoa/thường, bỏ khoảng trắng), điều kiện lọc mã chặt hơn, và bảng/VIEW audit K10 (`audit.lookup_coverage_snapshot`, `audit.fk_lookup_coverage`). | `etl/g2_model.py`, `etl/g2_pipeline.py`, `sql/00_raw_ref_ods_ddl.sql`, `tests/g2_coverage_checks.py`, `tests/g2_model_checks.py` |
| #51 | **Mart D2 `mart.personnel_flows_category_monthly`**, theo đề nghị của TV4 ở #32. Grain: tháng báo cáo × cơ quan × family × category. Tổng hợp riêng từng event Fact rồi `UNION ALL`; key 0 giữ trong tổng. `build_model` kiểm hai chiều với `personnel_flows_monthly`. | `sql/04_create_marts.sql`, `sql/06_g2_transfer.sql`, `etl/g2_model.py`, `etl/g2_transfer.py`, `etl/g3_pipeline.py`, `sql/tests/08_g3_full_baseline.sql`, `sql/07_g3_kpi.sql` |
| #52 | **Mart K10 `mart.dq_coverage_monthly`**, dựa trên audit độ phủ chính thức của TV2. Tỷ lệ chính thức chỉ có khi TV2 ghi `VERIFIED`/`COMPLETE`, đúng định nghĩa trong `02_kpi_dictionary.csv`. Có thêm số liệu thực tế về việc DW tra mã (khớp/Unknown/NULL/rỗng/REDACTED). | như trên |
| #55 | **Benchmark L3-15.** Mart trả lời K01 theo cơ quan trong 0,05 ms, so với 320 ms trên Fact (kết quả trùng khớp). Index giúp khoảng 4,5 lần trên Fact Separations, nhưng làm chậm 27% trên Fact Employment (bitmap lossy) ⇒ dùng Mart. | `sql/tests/09_benchmark.sql`, `evidence/TV3_week4/run_benchmark.py`, `reports/TV3_week4_benchmark.md`, `reports/week4/*` |

**Kiểm thử đợt 2** (PostgreSQL 17.12, code `0d36e10`, DB mới `workforce_dw_g3_tv1`):
- **Regression:** 5 bộ đều PASS, gồm `g2_coverage_checks` của TV2 và ca mới `check_new_marts`.
- **G3 đầy đủ:** J06 84 PASS + 12 PENDING; 152/152 kiểm chất lượng; **rerun May 17/17 bảng** không đổi (gồm 2 Mart mới); assertion 08 PASS, gồm category = K06/K07 và K10 104 dòng.
- **Dump `3b467c00…` (53.139 byte):** restore khớp từng dòng 7 bảng. Mart category tách đúng K06/K07 từng tháng; Mart K10 có 104 dòng (2 dòng có % chính thức, 20 dòng có số liệu tra mã của DW). Agency Unknown vẫn = 0.

**Trạng thái mới so với mục 7–8:**
- **TV4:** dùng dump `3b467c00…`. Đã đủ dữ liệu cho K01–K04, K06–K08, **D2 theo category** và **K10**.
  - K10: chỉ `agency_subelement_code` ở 2 file có tỷ lệ chính thức; các trường khác hiển thị BLANK kèm trạng thái, theo đúng từ điển KPI.
  - **K05/K09 vẫn chờ** chiều nghề/địa điểm/cấp bậc, cần TV2 audit.
- **TV3:** review các commit của đợt 1 và 2 (#50, #51, #52); làm tiếp #54, #56–#58.
- **TV2:** xác nhận cách gộp nhánh của mình (#53); mở PR cho nhánh L2-14 (`codex/l2-14-source-mart`).
- **TV5:** chạy lại G3 và benchmark độc lập. Đây vẫn là điều kiện để nghiệm thu G2/G3.

