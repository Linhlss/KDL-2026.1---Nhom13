# KẾ HOẠCH THỰC THI VÀ NGHIỆM THU — NHÓM 13

**Dự án:** Federal Workforce Intelligence — Kho dữ liệu và Business Intelligence phân tích nhân lực liên bang Hoa Kỳ  
**Phạm vi giao việc:** TV2 (Data Analyst/ERD/EDA), TV3 (Data Engineer/ETL/DW); phối hợp bắt buộc với TV4 (OLAP/Power BI) và TV5 (QA).  
**Tài liệu quản lý gốc:** `De_cuong_DW_BI_Nhom13_5_5_tuan_V3.md`, `Phan_cong_DW_BI_Nhom13_5_5_tuan_V3.md`, `Progress_Tracker_DW_BI_Nhom13_5_5_tuan.xlsx`.  
**Repository:** https://github.com/Linhlss/KDL-2026.1---Nhom13  
**Ngày đối chiếu repository:** 18/11/2026. **Cập nhật sau merge:** 18/11/2026 — PR #13 (TV2) và #14 (TV3) đã vào `main` ở trạng thái REVIEW; xem mục 0.  
**Mục tiêu trước mắt:** hoàn thành cổng **G2 — ngày 8–14 trong kế hoạch 39 ngày**, với ERD nguồn được kiểm chứng và pipeline thực sự chạy từ ba họ dữ liệu tới ít nhất một KPI Power BI.

> **Cách đọc hạn:** `Ngày 1–39` là ngày tương đối tính từ ngày khởi động chính thức của dự án trong bản V3. Do ngày khởi động chưa được ghi trên repository, tài liệu này **không tự gán ngày lịch hoặc tuyên bố công việc quá hạn**. Các mốc `T+24h`, `T+48h`, ... dưới đây là **hạn phối hợp nội bộ đề xuất tính từ khi TV1 giao tài liệu này**, không thay hạn trong V3. TV1 điền ngày bắt đầu/hạn thực tế trong Progress Tracker ngay khi giao.

---

## 0. Cập nhật 18/11/2026 — đã merge gì, đã kiểm gì, mốc T0

| Gói | PR | Trạng thái trên `main` | TV1 đã đối chiếu | Còn thiếu để PASS |
|---|---|---|---|---|
| TV2 profiling v1 (`evidence/TV2_week1/`) | [#13](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/13) | **REVIEW** | 12 file, 9.181.290 dòng, `count` chỉ bằng `1`, 593 event lệch tháng (269 Accessions + 324 Separations) — **khớp từng file** khi đo lại trực tiếp Parquet | TV5 review độc lập (L5-02); các file đầu ra L2-01…L2-08 theo mục 3 |
| TV3 PostgreSQL + ingest prototype | [#14](https://github.com/Linhlss/KDL-2026.1---Nhom13/pull/14) | **L3-01/02/03 REVIEW, L3-04 BLOCKED** | SHA-256 của `accessions_202504_v5` và `employment_202504_v4` trong log TV3 **thuộc baseline nhóm** | Separations 202504, ODS/`source_file`, J00/J01 ba họ; TV5 replay (L5-04); TV4 xác nhận kết nối |
| TV4 | — | Nhánh `tv4/week1` rỗng, issue #12 mở | — | Toàn bộ mục 5 |
| TV5 | — | Chưa có sản phẩm | — | Toàn bộ mục 6 |

Bằng chứng đối chiếu của TV1: [`evidence/TV1_week2/`](evidence/TV1_week2/README.md). **Đây là kiểm tra điều phối của TV1, không thay review độc lập của TV5** và không chuyển task nào sang DONE.

**Mốc T0 = 18/11/2026** (ngày kế hoạch được đưa lên `main`). Do đó T+24h = 19/11, T+48h = 20/11, T+72h = 21/11, T+5 ngày = 23/11, T+7 ngày = 25/11. Thứ tự việc của từng người: [`docs/00_next_steps_by_member.md`](docs/00_next_steps_by_member.md).

---

## 1. Trạng thái đầu vào — không làm lại sản phẩm đã có

| Thành viên | Sản phẩm đã hiện diện trên GitHub | Trạng thái chính xác | Việc chưa được tính hoàn thành |
|---|---|---|---|
| **TV2** | `main` (từ nhánh `tv2-data-profiling-v1`): script profiling 12 Parquet; 5 CSV thô; báo cáo Data Quality; workbook phân tích; biểu đồ; 7 phép kiểm nhất quán nội bộ | **Có kết quả profiling v1; đã merge `main` qua PR #13 ở trạng thái REVIEW; TV1 đo lại khớp; chưa có reviewer TV5 PASS** | Manifest SHA-256 của baseline nhóm; codebook có provenance; Data Dictionary hoàn chỉnh; ERD nguồn; relationship audit; taxonomy với dòng nguồn; EDA đa biến |
| **TV3** | `main` (từ nhánh `tv3/week1-setup`): 7 schema PostgreSQL; loader prototype; 7.153 dòng Accessions 202504 và mẫu 50.000 dòng Employment 202504; SQL checks, log, architecture v0 | **Đã merge `main` qua PR #14; L3-01/02/03 REVIEW, L3-04 BLOCKED; checksum 2 file prototype thuộc baseline (TV1 kiểm); chưa nghiệm thu** | Nạp Separations; DDL source_file/ODS; pipeline cho 3 họ; bản full 12 file; DW Fact/Dim/Mart; integration test |
| **TV4** | Issue `#12` / `L4-01` thử Publish to web | **Issue mở; chưa thấy file kết quả hoặc link thử** | Quyền public; dashboard specs; bus matrix; Dimension catalog; MVP `.pbix` |
| **TV5** | Chưa tìm thấy gói kiểm thử độc lập trên `main` hoặc nhánh TV2/TV3 đã kiểm | **Chưa có bằng chứng review/PASS** | Test plan; chạy lại profiling/ETL độc lập; kiểm khóa; kiểm Power BI; ghi kết quả PASS/FAIL |

**Giữ làm baseline:** 12 Parquet OPM/EHRI tháng 03–06/2025, khoảng 301,5 MB, tổng **9.181.290 bản ghi qua các kỳ** (Employment **9.057.997**, Accessions **30.782**, Separations **92.511**). Đây không phải số nhân viên khác nhau. Báo cáo TV2 chỉ ra `count` ở các file hiện tại parse được thành `1`, **593** event có tháng hiệu lực khác tháng file, nhiều trường `REDACTED` và missing; các số này phải được TV5 xác nhận độc lập trước khi ký nghiệm thu.

**R01:** phương án ERD nguồn quan hệ tái cấu trúc đã được thầy đồng ý **theo xác nhận TV1 ghi trong repo**; chưa có ảnh/tin nhắn gốc. Không hỏi lại nếu không đổi phương án. Thầy đồng ý cách tiếp cận **không đồng nghĩa** ERD hay PK/FK đã đạt yêu cầu. Không gọi đây là hệ thống OLTP sản xuất của OPM.

---

## 2. Thứ tự ưu tiên và quy tắc phối hợp

1. **P0 — Không được trượt G2:** bản kiểm kê/checksum đúng; codebook và audit quan hệ; ERD + source-to-target mapping; Staging/ODS; ETL ba họ; bus matrix và DDL tối thiểu; Mart mẫu + một KPI Power BI; QA độc lập.
2. **P1 — Hoàn thiện C03/C05/C08/C09:** Data Dictionary đầy đủ, taxonomy và source flow có chứng cứ; EDA categorical và Pareto; các Dim/hierarchy; sơ đồ physical overall; dashboard specs.
3. **P2 — Sau MVP:** tự phát hiện/nạp kỳ mới, hiệu năng nâng cao, phân tích lệch kỳ, mở rộng dữ liệu, hoặc các công nghệ không nằm trong phạm vi chính. P2 không được chặn P0.

**Quy ước trạng thái:** `TODO` → `DOING` → `REVIEW` → `DONE` hoặc `BLOCKED`. `REVIEW` nghĩa là đã gửi sản phẩm, **không có nghĩa PASS**. Chỉ chuyển `DONE` khi có đường dẫn sản phẩm, lệnh tái lập/bằng chứng, reviewer có tên và kết quả `PASS` trong tracker/issue. Khi bị chặn, phải gửi task ID + thiếu đầu vào nào + người cung cấp + thời hạn cần nhận.

**Tổ chức Git:** sản phẩm tuần 1 của TV2/TV3 đã vào `main`. Từ nay **mỗi người tạo nhánh mới từ `main` mới nhất** (`tv2/g2-source-model`, `tv3/g2-pipeline`, `tv4/week1`, `tv5/qa`), không tiếp tục commit lên hai nhánh cũ; tạo PR khi sản phẩm đạt tiêu chuẩn đầu ra của đợt, TV5 review dữ liệu/test, TV1 review phạm vi và ghép vào `main`. Không gộp bằng cách chép các file Excel/tài liệu mà bỏ script, provenance và log. Không đưa Parquet raw, passwords, dump nhạy cảm hoặc `.env` thật lên GitHub.

---

## 3. TV2 — Data Analyst / Source / ERD / EDA

**Đầu vào:** `evidence/TV2_week1/` trên `main` (PR #13); `evidence/TV1_week2/baseline_crosscheck.csv` (SHA-256/row count 12 file do TV1 đo lại); hồ sơ metadata TV1; 12 Parquet baseline; nguồn định nghĩa OPM/EHRI; yêu cầu ở V3.  
**Đầu ra quan trọng nhất:** một **bộ mô hình nguồn có căn cứ** để TV3 xây ODS và TV4 thiết kế Dimension. Không được đợi làm xong toàn bộ EDA rồi mới giao khóa/mapping.

### Đợt A — Khóa baseline và nghĩa trường (ưu tiên giao TV3 trong T+48h)

- [ ] **L2-01 / T+24h — Inventory 12 file.** Dùng chính 12 Parquet baseline; với **mỗi file** ghi `family`, `report_month`, `version`, `filename`, `size_bytes`, `row_count`, `column_count`, `schema_hash`, `sha256`, `source_url`, cách lấy dữ liệu. Ghi 12 dòng, không chỉ tổng cộng. **File:** `docs/03_source_inventory.csv` và `data/manifest/sha256.txt`. **PASS:** TV5 lấy một mẫu kiểm theo cả ba họ và xác minh checksum; tổng số dòng/tổng số file khớp; TV3 xác nhận checksum hai file prototype có thuộc baseline hay không. Nếu khác, ghi version và quyết định giữ/cách ly, không âm thầm trộn.
- [ ] **L2-02 / T+24–48h — Danh mục tài liệu chuẩn OPM.** Thu thập **đúng những** trang/bảng mã phục vụ KPI và ERD: Agency, Agency Subelement, Occupational Group/Series, Duty Station, Pay Plan và loại hành động Accessions/Separations. Mỗi mục có link chính thức, tên tài liệu, thời điểm truy cập, thời kỳ áp dụng, file lưu và trạng thái `FOUND / NEED_VERIFY / NOT_FOUND`. **File:** `data/reference/README.md`, `data/reference/reference_manifest.csv`. **PASS:** reviewer truy lại được nguồn/định nghĩa; thiếu chuẩn nào ghi thiếu, không suy nhãn từ trực giác.
- [ ] **L2-03 / T+48h — Data Dictionary ưu tiên trường dùng trong KPI/FK.** Tạo **một dòng mỗi cặp dataset–field** cho các trường quan trọng: `count`, `snapshot_yyyymm`, `personnel_action_effective_date_yyyymm`, `agency_code`, `agency`, `department_code`, `agency_subelement_code`, `occupational_group_code`, `occupational_series_code`, `duty_station_code`, `pay_plan_code`, `grade`, hai nhóm category; tách biệt trường không xuất hiện ở một họ. Cột tối thiểu: `dataset, raw_field, raw_type, meaning_vi, real_example, source_reference, missing_pct, redacted_pct, target_candidate, verified_status, reviewer`. **File:** `docs/03_data_dictionary.csv`. **PASS:** ví dụ thật có nguồn/file, tỷ lệ lấy đúng mẫu số, `REDACTED` không đồng nhất NULL/empty.
- [ ] **Phần việc tức thời chuyển TV3:** gửi bản Inventory, Dictionary cốt lõi và danh sách codebook cho TV3 **ngay khi có**, không chờ bảng EDA hoàn thành. Bàn giao bằng PR/issue có commit SHA và ghi các phần chưa kiểm.

### Đợt B — ERD nguồn, kiểm khóa và mapping (T+48h đến T+5 ngày; chặn L3-04/L3-07)

- [ ] **L2-04 — ERD nguồn v0.** Vẽ bảng metadata `source_file`, ba bảng bản ghi `ods_employment_record`, `ods_accession_record`, `ods_separation_record` và **chỉ các** bảng `ref_*` có căn cứ dữ liệu. Thể hiện PK kỹ thuật `file_id` và `(file_id, source_row_ordinal)` hoặc khóa kỹ thuật tương đương có định nghĩa nhất quán; biểu diễn các FK **dự kiến bằng nét đứt hoặc nhãn `PARTIAL`**. Ghi grain của từng bảng và nguồn codebook cạnh từng quan hệ. **File:** `diagrams/04_relational_source_erd.drawio` (+ bản PNG/SVG). **PASS:** TV3/TV5 đọc được cardinality, ranh giới nguồn–ODS; không có employee_id tự tạo để nối ba họ.
- [ ] **L2-06 — Audit quan hệ trên **toàn bộ các kỳ thích hợp**, không chỉ top 10.** Đối với `agency_code`, `agency_subelement_code`, `occupational_series_code`, `occupational_group_code`, `duty_station_code`, `pay_plan_code` và cặp `pay_plan_code + grade` khi có cơ sở, kiểm: distinct exact, uniqueness của khóa tham chiếu, code→label (theo tháng/phạm vi), NULL/empty/REDACTED, orphan, lịch sử hiệu lực, số dòng khớp sau lookup. **File:** `docs/04_relationship_audit.csv`, `sql/tests/04_fk_audit.sql` hoặc truy vấn DuckDB có thể tái chạy. **PASS:** **mỗi quan hệ** có `source_reference, key_columns, scope, tested_rows, orphan_rows, duplicate_ref_keys, status=VERIFIED/PARTIAL/UNSUPPORTED, reviewer`; không coi tương quan hai biến là FK.
- [ ] **L2-07 — Tạo bảng mã có provenance.** Chỉ ghi `VERIFIED` khi có codebook phù hợp kỳ và kiểm trên dữ liệu; mã không map được giữ riêng (Unknown/DQ) thay vì gán nhãn đoán. Nếu dùng mã phát hiện trực tiếp trong Parquet làm bảng tra mô tả, phải ghi rõ đây là **derived lookup**, không giả làm danh mục chuẩn của OPM. **File:** `data/reference/verified_codebook_manifest.csv` (+ dữ liệu ref được phép phân phối). **PASS:** TV3 có thể tạo bảng `ref` không có duplicate key trong phạm vi định nghĩa; danh sách ngoại lệ minh bạch.
- [ ] **L2-08 — Source-to-target mapping từng trường dùng trong Fact/Dim.** Có các cột `source_family, source_field, source_dtype, target_schema, target_table, target_column, transform_rule, nullable_rule, redacted_rule, source_time_role, lookup_rule, validation_sql, owner`. Đặc biệt ghi `report_month` suy từ manifest/tên file là metadata do nhóm tạo, không phải cột raw; `effective_month` không ghi đè `report_month`. **File:** `docs/04_source_to_target_mapping.csv`, ERD v1. **PASS:** TV3 đối chiếu được bảng/cột với DDL, TV4 đối chiếu được các KPI K01–K10, TV5 có test cho biến đổi quan trọng.
- [ ] **Handoff chính thức cho TV3/TV4.** Ghi rõ `VERIFIED`, `PARTIAL`, `UNSUPPORTED` cho từng quan hệ/Dimension; gửi mapping và danh sách ngoại lệ. **PASS:** TV3 xác nhận đã nhận phiên bản ERD/mapping; TV4 xác nhận những Dim có thể dùng trong bus matrix. Nếu codebook thiếu, tiếp tục làm ETL thô/ODS nhưng không chốt FK giả.

### Đợt C — C03/C05 hoàn thiện, chạy song song sau khi giao ERD v0

- [ ] **L2-05 — Taxonomy + OPM source flow.** Có 5 nhánh Employment, Accessions, Separations, Reference, Technical Metadata. Mỗi nhánh có một số ví dụ **dòng/cột thật** có tên file và tháng; tách quy trình công bố OPM có nguồn với pipeline do nhóm tạo. **Files:** `docs/03_taxonomy.md`, `diagrams/03_opm_source_flow.drawio`. **PASS:** TV1/TV5 truy được ví dụ đến Parquet; mũi tên ghi rõ dữ liệu.
- [ ] **L2-09 — EDA đủ nội dung thầy đánh giá.** Tái dùng profiling v1; thực hiện full-scan bổ sung: phân bố và Pareto **toàn bộ** agency (không dùng chỉ top 10 làm top 20%), ít nhất **hai bảng chéo** từ cùng snapshot ví dụ Agency × Occupation, Occupation × Grade; Chi-square/Cramér's V với công thức, kiểm expected cell và effect size; MoM 03–06/2025; missing/REDACTED theo tháng và hạn chế diễn giải. **Files:** `notebooks/01_eda.ipynb`, `reports/05_eda_findings.md`, `reports/05_charts/`. **PASS:** notebook chạy lại được trên dữ liệu thật; con số/tổng từng biểu đồ có lệnh kiểm; không Pearson trên code và không suy nhân quả/mùa vụ từ 4 tháng.
- [ ] **L2-10 — Một ví dụ thống kê có thể bảo vệ trên lớp.** Chọn bảng chéo đủ điều kiện, xuất `Oij`, `Eij`, thành phần Chi-square và Cramér's V có cách tính; nêu giới hạn do cỡ mẫu rất lớn, phân loại hiếm và các ô có expected thấp. **File:** `reports/05_categorical_method_example.md` và ảnh minh chứng. **PASS:** TV5 tính lại được ít nhất một ô và công thức tổng.
- [ ] **L2-11/L2-12/L2-13 (chuẩn bị từ tuần 2).** Với TV3, viết quy tắc chuẩn hóa `count`, missing/REDACTED, Unknown, mismatched months và bảng trước–sau có `affected_rows`; đối soát không làm mất event. **Output:** `reports/07_source_quality_to_etl_rules.csv` và input cho test của TV5. **PASS:** mỗi quy tắc có test, không tự xóa 593 record khác kỳ.

**Ghi chú riêng cho TV2:** báo cáo profiling v1 đã chứa 10 phát hiện và các phép kiểm nội bộ; **không cần viết lại báo cáo cũ**. Chỉ làm các phần chưa có/thiếu độ tin cậy. Đầu ra nhóm cần nhất lúc này là ERD, codebook và mapping — EDA chuyên sâu có thể tiếp tục sau khi đã bàn giao bản đầu.

---

## 4. TV3 — Data Engineer / PostgreSQL / ETL / DW

**Đầu vào:** `main` (PR #14): log và loader prototype; 12 file OPM; inventory/codebook/ERD TV2; bus matrix TV4; reviewer TV5.  
**Đích kỹ thuật:** từ **prototype hai file** sang **MVP ba họ → ODS → Fact/Dim → Mart → một KPI Power BI**. Không gọi việc đã nạp mẫu 50.000 Employment là đã nạp toàn bộ dữ liệu.

### Đợt A — Hoàn tất hạ tầng có thể làm độc lập (T+24–48h)

- [ ] **L3-01 — Chuyển sản phẩm môi trường sang review.** Hoàn thiện `docs/06_environment_setup.md`, `configs/.env.example`, `requirements.txt`, `sql/01_create_schemas.sql`. TV3 đã chạy trên MacBook M3 Pro + PostgreSQL 18.7; tài liệu cần mô tả **môi trường đã dùng**, không bắt buộc chuyển máy vì bản phân công viết Windows. **PASS:** TV5 chạy lại `CREATE SCHEMA`, cài dependencies và kết nối trên môi trường kiểm chứng; không lộ secrets.
- [ ] **L3-02 — Nạp thử Separations 202504 v5.** Dùng loader hiện có, nạp **đủ 24.088 dòng** từ một file Separations tháng 04/2025; kiểm checksum theo manifest TV2, row ordinal duy nhất, bảo toàn kiểu text/mã có số 0 ở đầu/NULL/REDACTED; ghi log. **Files:** cập nhật `reports/TV3_week1_prototype_results.md`, `reports/TV3_week1_load_log.csv`, SQL/evidence tương ứng. **PASS:** raw count = staging count = 24.088; chạy lại không tăng dòng; lỗi checksum rollback an toàn. Không dùng báo cáo tồn tại sẵn để khẳng định bước này đã chạy.
- [ ] **L3-03 — Chốt phương án TV4 kết nối database.** Nêu 1 đường vận hành khả thi: bản sao PostgreSQL trên Windows TV4 hoặc DB host được phép truy cập; ghi `host/port/db/schema`, cách dump/restore, dữ liệu chỉ gồm mẫu/Mart thử, không commit mật khẩu. **File:** `docs/06_environment_setup.md` và bản kiến trúc `diagrams/06_architecture_components.drawio`. **PASS:** TV4 tự xác nhận kết nối và chạy được một `SELECT` vào bảng thử (hoặc ghi lỗi có ảnh).
- [ ] **L3-04 — Chờ đầu vào ERD nhưng không dừng các bước trên.** Profile khóa ứng viên từ mẫu đã có; ghi những gì là sơ bộ, không đặt FK ref nếu thiếu uniqueness/codebook. Khi nhận ERD v0 của TV2, lập biên bản phản biện từng quan hệ. **File:** `docs/TV3_week1_erd_review.md`. **PASS:** có trạng thái/giới hạn rõ cho từng FK dự kiến và reviewer TV5.

### Đợt B — Nguồn quan hệ và pipeline ba họ (T+2 đến T+5 ngày)

- [ ] **L3-05 — DDL Staging/ODS và metadata thật.** Tạo `raw_meta.source_file`, ba bảng record ODS và `audit.load_run`/`audit.dq_issue`, khóa kỹ thuật định danh **file + vị trí dòng**; giữ tên file, version, hash, `report_month`, các trường raw, trạng thái DQ. Phân biệt Staging (giữ gần nguồn) với ODS (chuẩn hóa); ghi rationale khi dùng một DB nhiều schema. **File:** `sql/00_raw_ref_ods_ddl.sql`; cập nhật runbook. **PASS:** SQL chạy được từ DB sạch; 3 family có grain và lineage; cùng file/version chạy lại không nhân dòng; không có employee_id giả.
- [ ] **L3-06 — J00/J01 cho cả ba family.** Scan manifest, xác nhận SHA-256 trước khi nạp, kiểm schema, chuyển batch, `COPY`, log run_id, rows, status, duration và lý do lỗi; không ghi đè baseline khác version không kiểm soát. **File:** thư mục `etl/` với entrypoint và `reports/07_load_log.csv`. **PASS:** nạp thử 202504 của ba family, tách đúng month/file lineage; test sai checksum và source file thiếu cho kết quả FAIL có log, không hỏng dữ liệu đã hợp lệ.
- [ ] **J02 — Xử lý giá trị với TV2.** Cast `count` có kiểm (`1` đối với 12 file hiện tại), giữ null/empty/REDACTED phân biệt; thêm `Unknown` chỉ ở lớp lookup/Dim khi có quy tắc; giữ `snapshot_yyyymm`, `report_month`, `effective_month` theo đúng family. **File:** ETL transform SQL/Python + `reports/07_before_after.csv` + test. **PASS:** sau xử lý không mất bản ghi; không bỏ 593 events chỉ vì khác kỳ; không INNER JOIN ref làm giảm row count.
- [ ] **L3-09 — Hoàn thiện hai sơ đồ riêng.** `diagrams/06_architecture_components.drawio` mô tả thành phần/máy/công nghệ đang chạy; `diagrams/06_etl_data_flow.drawio` mô tả J00–J06, trường dữ liệu, đường exception, checkpoint. **PASS:** hai sơ đồ không bị dùng thay nhau; tên bảng/trường khớp DDL thực tế.

### Đợt C — Thiết kế và chạy MVP DW/BI (T+4 đến T+7 ngày, cổng G2)

- [ ] **L3-07 — Nhận bus matrix từ TV4 trước khi khóa DW DDL.** Tối thiểu có `dim_month`, `dim_agency` ở phạm vi audit cho phép, `dim_accession_category`, `dim_separation_category` khi nghĩa mã có căn cứ; các chiều khác thêm có kiểm. Dùng 3 Fact theo 3 grain khác nhau, role-playing time cho report/effective. **File:** `sql/03_dw_ddl.sql`, `sql/04_create_marts.sql`, sơ đồ `diagrams/09_dw_physical_overall.drawio`. **PASS:** TV4 duyệt grain/hierarchy; TV5 kiểm PK/FK và physical overall khớp DDL.
- [ ] **L3-08 — MVP end-to-end từ nguồn thật.** Chạy ít nhất một file mỗi family trong **cùng kỳ 202504** → Staging/ODS → 3 Fact → ít nhất 1 Mart → Power BI của TV4. Dùng KPI đơn giản K01 (Monthly Headcount) hoặc K06/K07; nếu muốn K02 MoM cần thêm Employment 202503. **PASS định lượng:** Employment 202504 = **2.271.969** chỉ khi nạp **toàn bộ file**; Accessions 202504 = **7.153**; Separations 202504 = **24.088**; SQL-Mart-DAX khớp filter cùng kỳ. Nếu chỉ nạp mẫu Employment, **không được** báo K01 toàn kỳ bằng 50.000 như headcount thực.
- [ ] **L3-09 — Sơ đồ vật lý overall có đủ bảng.** Ngoài sơ đồ architecture/ETL, có sơ đồ DW logic (TV4) và DW vật lý (TV3) gồm toàn bộ Fact, Dim, PK/FK và Mart hiện thực; export PNG để thuyết trình. **PASS:** thầy đọc một hình để thấy được các quan hệ, reviewer lần ngược sang SQL DDL.
- [ ] **Bàn giao TV4 + TV5:** database phiên bản MVP, scripts, tên bảng/column, row counts, SQL tham chiếu K01/K06/K07, log, ảnh/record demo, cách restore và version dữ liệu. **PASS:** TV4 kết nối được không cần TV3 điều khiển máy; TV5 chạy lại số ít nhất một KPI.

### Đợt D — Công việc sau G2, giữ theo tuần 3 của V3

- [ ] **L3-10:** mở rộng J01/J02 sang **12/12 file**, log riêng từng file, version, rows và duration; kỳ nào FAIL phải làm rõ.
- [ ] **L3-11:** J03 build Dimension với Unknown/version; J04 build **3 Fact**; kiểm số dòng/PK/lineage và mối quan hệ đúng grain.
- [ ] **L3-12:** J05 build ít nhất **2 Mart**; với luồng Accessions/Separations phải aggregate trước hoặc `UNION ALL` phù hợp, không JOIN bản ghi các Fact theo agency/month làm nhân dòng.
- [ ] **L3-13:** J06 reconciliation source → staging → ODS → Fact → Mart; rerun kỳ 202505 và kiểm idempotence/version; TV5 review logs. **PASS G3:** full 12 file, 3 Fact, >=2 Mart, test rerun không nhân bản, số liệu theo kỳ đúng, ngoại lệ có báo cáo.

**Ghi chú riêng cho TV3:** prototype đang dùng `staging.prototype_accessions`/`prototype_employment` và **thay toàn bảng prototype khi chạy lại**. Đây là hành vi hợp lệ để thử ingest nhưng **không phải thiết kế incremental/idempotence đã hoàn chỉnh**. Khi chuyển sang J00–J06, phải có policy file/version, transaction, unique key hoặc load replacement có kiểm soát, QA rerun và audit. Đừng gọi prototype là full ETL.

---

## 5. TV4 — Phải bắt đầu ngay, không chờ toàn bộ DW

**Owner:** TV4. **Reviewer:** TV1/TV5 (ngữ nghĩa và công bố), TV3 (mô hình/kết nối).

- [ ] **L4-01 / T+24h — Test Power BI Desktop/Service/Publish to web.** Tạo report thử chỉ dùng **số tổng hợp thật đã ghi nguồn** (không dùng dữ liệu HR giả); thử Publish to web. Ghi account type, workspace, URL công bố hoặc thông báo chặn; TV5 truy cập cửa sổ ẩn danh và kiểm export. **File:** `docs/10_publish_feasibility.md`, `evidence/TV4_week1/` (ảnh và URL). **PASS:** có URL công khai hoạt động được với người không đăng nhập **hoặc** ảnh lỗi + đề xuất phương án xin thầy chấp thuận; không được tuyên bố công bố thành công nếu chỉ publish lên workspace cá nhân.
- [ ] **L4-02 / T+48h — Wireframe 3 dashboard D1/D2/D3.** Với từng trang ghi persona, câu hỏi, KPI, thời gian dùng, filter, chart, drill, tooltip, DAX dự kiến, nguồn SQL đối chiếu, câu chuyện cần kể. **File:** `docs/10_dashboard_specs.md`. **PASS:** TV1 xác nhận cả ba trang trả lời câu hỏi nghiệp vụ; không cộng nhiều snapshot làm headcount.
- [ ] **L4-03/L4-04 / T+48–72h — Bus matrix + Dimension catalog v0.** Ghi cột `Fact`, `grain`, `Dim`, `natural_key`, `hierarchy`, `role_month`, `verified_status`, `unknown_rule`, `source_field`. Không tự vẽ hierarchy Agency/Location/Grade trước khi TV2 xác minh. **Files:** `docs/09_bus_matrix.md`, `docs/08_dimension_catalog.csv`, `diagrams/08_dimension_groups.drawio`. **PASS:** TV3 nhận đủ để viết DW DDL MVP, TV2 ký các chiều có kiểm chứng.
- [ ] **L4-05/L4-06 / G2 — Kết nối Mart MVP và tạo một KPI Power BI.** Làm `.pbix` chạy trên Windows, cấu hình PostgreSQL, measure K01 hoặc K06/K07, một slicer tháng/cơ quan nếu Mart hỗ trợ. Chụp SQL vs DAX theo cùng filter. **Files:** `powerbi/MVP_G2.pbix` và `evidence/TV4_G2/`. **PASS:** TV5 xác nhận số liệu DAX khớp SQL, có ảnh model/relationship.

**Không làm lúc này:** chờ có full 12 file mới bắt đầu Power BI; triển khai cả 3 dashboard trước khi chốt grain; đẩy raw/ODS hoặc các trường chi tiết/REDACTED lên semantic model public.

---

## 6. TV5 — Phải kiểm độc lập từ bây giờ, không chờ cuối kỳ

**Owner:** TV5. **Reviewer:** TV1; TV2/TV3/TV4 nhận lỗi theo đúng sở hữu.

- [ ] **L5-01 / T+24h — Test plan + acceptance matrix.** Tạo `tests/test_plan.md` và `reports/qa_issue_log.csv`. Mỗi test có `test_id, task_id, criterion_Cxx, input_version, script_or_steps, expected, actual, status, evidence_link, reviewer, tested_at`. **PASS:** các test Q01–Q15 trong V3 đều được gắn owner và có test thao tác cụ thể; không đánh dấu PASS khi chưa chạy.
- [ ] **L5-02 / T+48h — Kiểm độc lập profiling TV2.** Kiểm 12 file, checksum mẫu và tổng nguồn, `count` parse, 593 mismatch, trường `REDACTED`, tính đúng mẫu số các tỷ lệ; tối thiểu tái chạy trực tiếp Parquet ở đủ ba family/ít nhất một file mỗi family và đối chiếu báo cáo. **File:** `reports/qa_tv2_profiling_review.md` + command/output. **PASS:** ghi chính xác phạm vi test và chênh lệch nếu có; các test nội bộ TV2 không tự thay cho reviewer.
- [ ] **L5-03 / T+48h — Public review TV4.** Mở link ở trình duyệt ẩn danh/thiết bị không đăng nhập, ghi màn hình và kiểm không lộ dữ liệu cấp bản ghi; nếu bị chặn ghi FAIL và đề xuất phương án giải quyết. **File:** `reports/qa_powerbi_publish.md`. **PASS:** kết quả có bằng chứng, không mặc định account trường được quyền public.
- [ ] **L5-04 / T+72h — Replay ETL prototype TV3.** Dựng schema từ SQL, thử nạp lại Accessions 202504 và mẫu Employment 202504, kiểm checksum/row count/ordinal, mã có số 0 đầu, NULL/REDACTED, chạy lại không nhân dòng, lỗi checksum rollback. Test thêm Separations khi TV3 bàn giao. **File:** `reports/qa_tv3_prototype_review.md`, SQL/log. **PASS:** ghi version file, số thực đo, PASS/FAIL từng phép; không lấy mỗi báo cáo TV3 làm kiểm thử độc lập.
- [ ] **L5-05 / Khi nhận ERD — Review PK/FK.** Với mỗi quan hệ TV2 đề xuất, TV5 kiểm statement nguồn, uniqueness, null, orphan, phạm vi mã và số dòng trước/sau JOIN; gắn `VERIFIED / PARTIAL / UNSUPPORTED`. **File:** `reports/qa_erd_fk_review.csv`. **PASS:** không có quan hệ nghiệp vụ `VERIFIED` nếu thiếu bằng chứng, không có relationship nhân viên giữa ba Fact.
- [ ] **L5-06 / G2 — Test KPI end-to-end.** Đối chiếu 202504 từ Parquet → ODS → Fact → Mart → SQL → Power BI trong cùng filter và version. **File:** `reports/07_reconciliation.csv`, ảnh/log. **PASS:** K01/K06/K07 không sai số; exception được phân loại; reviewer ký kết quả.

**Quy định QA:** TV5 không tự sửa kết quả của TV2/TV3 để khớp. Nếu FAIL, ghi bug có `owner, severity, expected/actual, step to reproduce, deadline`, giao lại đúng người; đóng sau khi chạy regression.

---

## 7. Kế hoạch phối hợp 7 ngày tiếp theo (từ lúc giao kế hoạch)

| Mốc phối hợp | TV2 phải gửi | TV3 phải gửi | TV4 phải gửi | TV5 phải gửi | TV1 kiểm |
|---|---|---|---|---|---|
| **T+24h** | Inventory bản đầu + danh mục codebook có nguồn | Môi trường và runbook review; kế hoạch nạp Separations | Kết quả thử Publish to web hoặc ảnh lỗi | Test plan, phân công test | Người nhận, phiên bản commit, blocker |
| **T+48h** | Manifest SHA-256; Dictionary trường cốt lõi; ERD phác | Separations prototype + log; DDL `source_file`/ODS bản đầu | Specs D1–D3; bus matrix phác | Review profiling và pilot TV3 | Hai nhánh có PR, phân loại review/blocked |
| **T+72h** | Audit khóa nhóm Agency/Occupation/Duty Station/Pay Plan có trạng thái, bản ref đầu | Ba họ qua Staging, bộ test checksum/rerun | Catalog Dim + logic model v0 | Review sơ bộ PK/FK; thử anonymous Power BI | Chốt FK nào verified, chỗ nào chưa được đặt FK |
| **T+5 ngày** | ERD v1, source→target mapping; taxonomy/source flow | ODS ba họ và DDL Fact/Dim/Mart bản đầu | Bus matrix/Dim được TV2/TV3 đồng ý | SQL tests ODS/lookup | Ghi quyết định grain/kỳ và cập nhật tracker |
| **T+7 ngày** | EDA bổ sung và handoff C03–C05 | **MVP ba họ → ODS → Fact → Mart** | **Một KPI chạy trên Power BI** | **KPI reconciliation PASS/FAIL có bằng chứng** | Quyết định đạt/chưa đạt G2; task còn chặn G3 |

Các mốc này là **mục tiêu điều phối nội bộ đề xuất**, không phải xác nhận rằng nhóm đang ở Ngày 8–14 của lịch học. Nếu G2 chính thức đến sớm hơn, TV1 ưu tiên **ERD + MVP + QA** và lùi phần EDA bổ sung, không lùi pipeline.

---

## 8. Tiêu chí nghiệm thu G2: chỉ tuyên bố đạt khi đủ bằng chứng

- [ ] Có inventory/checksum cho đúng **12 Parquet**, có người kiểm độc lập.
- [ ] Có **ERD nguồn** với PK kỹ thuật đúng, bảng ref và mối quan hệ phân loại được kiểm; không có employee_id giả.
- [ ] Có `docs/04_relationship_audit.csv` và mapping từ source fields tới ODS/Dim/Fact; mọi quan hệ chưa đủ chứng cứ ghi PARTIAL hoặc UNSUPPORTED.
- [ ] PostgreSQL có DDL Staging/ODS và script nạp được **cả ba họ dữ liệu** có log.
- [ ] Có 3 Fact theo 3 grain riêng; tối thiểu **một Mart mẫu** phục vụ KPI G2, có bus matrix/Dimension cần thiết; không JOIN raw Fact–Fact làm nhân số.
- [ ] Một KPI thật được TV4 tính trên Power BI và đối soát với SQL/nguồn cùng kỳ.
- [ ] TV5 có report độc lập và kết quả PASS/FAIL. Không đánh dấu DONE chỉ vì thành viên đặt `100%` trong tracker.
- [ ] Có PR từ TV2/TV3 (và TV4/TV5 khi có đầu ra), reviewer được gán; các phần merge vào `main` là bản đã review.

**Ví dụ kiểm số kỳ 202504** khi nạp **toàn file tương ứng**: Employment **2.271.969**; Accessions **7.153**; Separations **24.088**. Nếu hiển thị Headcount Change 202504 so 202503 thì phải nạp thêm Employment 202503 = **2.289.192**, hiệu **−17.223**. Event Difference 202504 là **−16.935 lượt**, **không** có nghĩa Headcount Change và không bắt buộc bằng −17.223.

---

## 9. Ma trận bàn giao và người chịu trách nhiệm

| Gói | Người tạo | Người kiểm | Người dùng tiếp | Không được bàn giao khi |
|---|---|---|---|---|
| Inventory + checksum | TV2 | TV5 + TV3 kiểm prototype | TV3 | Thiếu 12 dòng/version/hash hoặc lệch baseline không giải thích |
| Dictionary + codebook | TV2 | TV5 + TV1 kiểm nghĩa | TV3/TV4 | Mã/nhãn tự suy ra, không có nguồn hoặc không có trạng thái xác minh |
| ERD + FK audit + mapping | TV2 | TV3/TV5 | TV3 tạo ODS/Dim | Quan hệ giả, thiếu grain, không biết orphan/duplicate |
| ODS + loader + logs | TV3 | TV5 + TV2 kiểm nguồn | TV4/TV5 | Chạy lại nhân dòng, mất REDACTED, mất tháng hiệu lực |
| Bus matrix + Dimension catalog | TV4 | TV2/TV3/TV5 | TV3 tạo Fact/Mart | Dimension chung không xác minh, thiếu time role |
| Fact + Mart + KPI SQL | TV3 | TV5 + TV4 | TV4 | Nguồn–SQL lệch số hoặc không tái lập được |
| Power BI MVP | TV4 | TV5 + TV1 | TV1 demo | DAX khác SQL hoặc chỉ dùng dữ liệu giả |
| QA/reconciliation report | TV5 | TV1 | TV2/TV3/TV4 xử lý lỗi | Không có câu lệnh, expected/actual và chứng cứ chạy |

**Báo cáo tiến độ:** mỗi người cập nhật vào `Progress_Tracker_DW_BI_Nhom13_5_5_tuan.xlsx`/bản Google Sheets đang dùng và GitHub Issue tương ứng **ít nhất 2 lần/tuần**; với việc P0 bị chặn, cập nhật ngay trong ngày. Viết ngắn: `task_id`, việc hoàn thành, link commit/file, test đã chạy, kết quả, blocker, đầu vào cần người khác gửi. TV1 chịu trách nhiệm chốt `DONE/PASS` sau review, không dựa trên tự báo.

---

## 10. Nguồn và ranh giới chứng cứ

- **Đề cương/Phân công V3:** nằm ở thư mục gốc repository; bản này giữ nguyên task IDs `L2-*`, `L3-*`, `L4-*`, `L5-*` và điều kiện G2/G3 của V3.
- **TV2:** `evidence/TV2_week1/` trên `main` (merge từ nhánh `tv2-data-profiling-v1`, PR #13); `data_quality.md` và `README_Ban_Giao.md` xác nhận profiling v1, đồng thời liệt kê rõ các phần chưa có.
- **TV3:** `reports/TV3_week1_summary.md`, `reports/TV3_week1_prototype_results.md`, `etl/prototype_ingest.py` trên `main` (merge từ nhánh `tv3/week1-setup`, PR #14); kết quả là prototype có bằng chứng do TV3 tạo, chưa phải kiểm thử độc lập.
- **TV4:** GitHub Issue `#12` cho L4-01 đang mở tại thời điểm đối chiếu; chưa có file công bố xác minh.
- **TV5:** chưa có bằng chứng nghiệm thu độc lập trên các nhánh đã kiểm.
- **TV1 (18/11/2026):** `evidence/TV1_week2/` — đo lại SHA-256, số dòng, số cột, giá trị `count` và số event lệch tháng trên 12 Parquet baseline.
- **OPM/EHRI:** dùng dữ liệu thật, giữ version và provenance; không tạo bản ghi nhân viên, giao dịch hoặc quan hệ không có trong nguồn. `REDACTED` không phải 0; `report_month` khác `effective_month`; Employment snapshot không cộng qua kỳ để suy người duy nhất.

Tài liệu này là **kế hoạch hành động và tiêu chuẩn bàn giao**, không phải báo cáo kết quả đã nghiệm thu. Khi TV2/TV3/TV4/TV5 hoàn thành, trạng thái và số liệu thực tế phải được cập nhật qua tracker, log, GitHub PR và hồ sơ review.
