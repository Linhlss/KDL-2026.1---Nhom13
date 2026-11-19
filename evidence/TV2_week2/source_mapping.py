"""Build the TV2 source-to-target design from the dictionary and inventory."""
from source_baseline import ROOT, TIME, read_csv, write_csv

TABLES = {
    "employment": ("ods_employment_record", "fact_employment_snapshot"),
    "accessions": ("ods_accession_record", "fact_accessions"),
    "separations": ("ods_separation_record", "fact_separations"),
}
DIM_KEYS = {
    "agency_code": ("dim_agency", "agency_key"),
    "occupational_series_code": ("dim_occupation", "occupation_key"),
    "duty_station_code": ("dim_location", "location_key"),
    "grade": ("dim_grade", "grade_key"),
    "age_bracket": ("dim_age_bracket", "age_bracket_key"),
    "accession_category_code": ("dim_accession_category", "accession_category_key"),
    "separation_category_code": ("dim_separation_category", "separation_category_key"),
}
MVP_LABELS = {
    "agency": "dim_agency",
    "accession_category": "dim_accession_category",
    "separation_category": "dim_separation_category",
}


def fact_lineage_sql(ods, fact):
    template = (ROOT / "sql/tests/06_fact_lineage.sql").read_text(encoding="utf-8")
    return " ".join(template.split()).replace("{{ods_table}}", f"ods.{ods}").replace(
        "{{fact_table}}", f"dw.{fact}")


def row(family, source, dtype, schema, table, col, rule, test, *, time_role="",
        lookup="None", nullable="Preserve NULL/empty", redacted="Preserve marker", status="PROPOSED"):
    return dict(source_family=family, source_field=source, source_dtype=dtype,
                target_schema=schema, target_table=table, target_column=col,
                transform_rule=rule, nullable_rule=nullable, redacted_rule=redacted,
                source_time_role=time_role, lookup_rule=lookup, validation_sql=test,
                owner="TV2 + TV3", status=status)


def model(fields):
    for family, (ods, fact) in TABLES.items():
        lineage = f"SELECT file_id, source_row_ordinal FROM ods.{ods} GROUP BY 1,2 HAVING COUNT(*) > 1"
        orphan = (f"SELECT o.file_id FROM ods.{ods} o LEFT JOIN raw_meta.source_file f "
                  "ON o.file_id = f.file_id WHERE f.file_id IS NULL")
        fact_lineage = fact_lineage_sql(ods, fact)
        for key, rule, test in (
            ("file_id", "Use registered source_file ID resolved by SHA-256", orphan),
            ("source_row_ordinal", "Persist original row ordinal as one-based, consistent with TV3 prototype", lineage),
        ):
            yield row(family, key, "derived", "ods", ods, key, rule, test, nullable="Required")
            yield row(family, key, "derived", "dw", fact, key, "Carry ODS lineage", fact_lineage,
                      nullable="Required")
        for field, check in (
            ("sha256", "SELECT sha256 FROM raw_meta.source_file GROUP BY 1 HAVING COUNT(*) > 1"),
            ("report_month", "SELECT file_id FROM raw_meta.source_file WHERE report_month IS NULL"),
            ("family", "SELECT file_id FROM raw_meta.source_file WHERE family IS NULL"),
            ("filename", "SELECT file_id FROM raw_meta.source_file WHERE filename IS NULL"),
            ("version", "SELECT file_id FROM raw_meta.source_file WHERE version IS NULL"),
            ("row_count", "SELECT file_id FROM raw_meta.source_file WHERE row_count <= 0"),
            ("schema_hash", "SELECT file_id FROM raw_meta.source_file WHERE schema_hash IS NULL"),
        ):
            yield row(family, f"manifest.{field}", "derived", "raw_meta", "source_file", field,
                      "Read from locked manifest", check, nullable="Required", time_role="report_month")
        for field in fields:
            if field["dataset"] != family:
                continue
            name, dtype = field["raw_field"], field["raw_type"]
            if dtype != "derived":
                yield row(family, name, dtype, "ods", ods, name, "Keep source value and type",
                          f"SELECT COUNT(*) FROM ods.{ods} WHERE {name} IS NULL")
            if name == "count":
                measure = "record_count" if family == "employment" else "event_count"
                yield row(family, name, dtype, "dw", fact, measure, "Validate then cast to BIGINT",
                          f"SELECT COUNT(*), SUM({measure}) FROM dw.{fact}",
                          nullable="Required", redacted="DQ error")
            if name in ("report_month", "snapshot_yyyymm", TIME):
                role = {TIME: "effective_month", "snapshot_yyyymm": "snapshot_month"}.get(name, name)
                rule = ("Carry manifest value through source_file" if name == "report_month"
                        else "Validate and preserve the source YYYYMM")
                yield row(family, name, dtype, "dw", fact, role, rule,
                          f"SELECT COUNT(*) FROM dw.{fact} WHERE {role} IS NULL", time_role=role,
                          nullable="Required", redacted="DQ error")
                yield row(family, name, dtype, "dw", "dim_month", "month_yyyymm",
                          f"Use independent {role} role", "SELECT month_yyyymm FROM dw.dim_month "
                          "GROUP BY 1 HAVING COUNT(*) > 1", time_role=role, nullable="Required")
            if name in DIM_KEYS:
                dim, key = DIM_KEYS[name]
                natural = "pay_plan_code, grade" if name == "grade" else name
                columns = natural.split(", ")
                for column in columns:
                    yield row(family, column, dtype, "dw", dim, column, "Keep natural key in agreed scope",
                              f"SELECT {natural} FROM dw.{dim} GROUP BY {natural} HAVING COUNT(*) > 1",
                              nullable="Unknown only after review", status="PARTIAL")
                yield row(family, natural, dtype, "dw", fact, key, "Resolve surrogate from agreed reference",
                          f"SELECT COUNT(*) FROM dw.{fact} f LEFT JOIN dw.{dim} d "
                          f"ON f.{key} = d.{key} WHERE d.{key} IS NULL",
                          lookup="Cardinality-preserving LEFT JOIN after scope and key review",
                          nullable="Unknown only after review", redacted="Retain REDACTED state",
                          status="PARTIAL")
            if name in MVP_LABELS:
                dim = MVP_LABELS[name]
                yield row(family, name, dtype, "dw", dim, name, "Confirm source label against scoped OPM reference",
                          f"SELECT {name}_code FROM ods.{ods} GROUP BY {name}_code "
                          f"HAVING COUNT(DISTINCT {name}) > 1",
                          lookup="Use the reference label only after code and scope review", status="PARTIAL")
            if name == "annualized_adjusted_basic_pay":
                yield row(family, name, dtype, "dw", fact, name, "Parse observed amount to DECIMAL(18,2)",
                          f"SELECT COUNT(*) FROM dw.{fact} WHERE {name} < 0",
                          nullable="NULL for unavailable", redacted="Set numeric NULL; carry state separately")
        yield from k10_rows(family)


def k10_rows(family):
    checks = {
        "source_file": ("manifest.filename", "Keep the filename from the checked manifest"),
        "report_month": ("manifest.report_month", "Keep the file's report month"),
        "lookup_field": ("relationship_audit.key_columns", "Keep the exact key columns used by the check"),
        "lookup_status": ("relationship_audit.status", "Keep the audit status for this scope"),
        "eligible_rows": ("relationship_audit.eligible_rows", "Count rows whose keys are present"),
        "matched_rows": ("relationship_audit.reference_unique_matches",
                         "Count eligible rows with exactly one official match. Use NULL if the reference is incomplete"),
        "coverage_pct": ("relationship_audit.k10_coverage_pct",
                         "Divide 100 * matched_rows by eligible_rows. Use NULL if unverified or the denominator is zero"),
    }
    validation = (
        "SELECT * FROM audit.fk_lookup_coverage WHERE matched_rows > eligible_rows "
        "OR (lookup_status = 'VERIFIED' AND eligible_rows > 0 AND coverage_pct IS NULL) "
        "OR (coverage_pct IS NOT NULL AND (lookup_status IS DISTINCT FROM 'VERIFIED' "
        "OR eligible_rows IS NULL OR eligible_rows <= 0 OR matched_rows IS NULL "
        "OR ABS(coverage_pct - 100.0 * matched_rows / NULLIF(eligible_rows, 0)) > 0.000001))"
    )
    for target, (source, rule) in checks.items():
        yield row(family, source, "derived", "audit",
                  "fk_lookup_coverage", target, rule,
                  validation,
                  time_role="report_month", lookup="One official reference check per source file and key",
                  nullable="See coverage rule", redacted="Count separately from eligible", status="PARTIAL")


if __name__ == "__main__":
    source = read_csv(ROOT / "docs/03_data_dictionary.csv")
    write_csv(ROOT / "docs/04_source_to_target_mapping.csv", list(model(source)))
