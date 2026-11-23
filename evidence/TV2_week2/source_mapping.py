"""Build the TV2 source-to-target design from the dictionary and inventory."""
from source_baseline import ROOT, TIME, read_csv, write_csv

TABLES = {
    "employment": ("ods_employment_record", "fact_employment_snapshot"),
    "accessions": ("ods_accessions_record", "fact_accessions"),
    "separations": ("ods_separations_record", "fact_separations"),
}
ACTION_RELATIONS = {"accessions": "accession_category", "separations": "separation_category"}
MONTH_PATTERN = "^[0-9]{4}(0[1-9]|1[0-2])$"


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
                      "Read from locked manifest", check, nullable="Required")
        for field in fields:
            if field["dataset"] != family:
                continue
            name, dtype = field["raw_field"], field["raw_type"]
            if dtype != "derived":
                yield row(family, name, dtype, "ods", ods, name, "Keep source value and type",
                          f"SELECT COUNT(*) FROM ods.{ods} WHERE {name} IS NULL")
        yield from typed_rows(family, ods, fact)
        yield from month_rows(family, ods, fact)
        yield from lookup_rows(family, ods, fact, "agency", "agency", "dim_agency")
        if family in ACTION_RELATIONS:
            yield from lookup_rows(family, ods, fact, ACTION_RELATIONS[family], "category", "dim_action_category")
        yield from k10_rows(family)


def typed_rows(family, ods, fact):
    time_source = "snapshot_yyyymm" if family == "employment" else TIME
    effective_source = "NULL::text" if family == "employment" else TIME
    pay = "annualized_adjusted_basic_pay"
    checks = (
        ("manifest.report_month", "report_month", "Use the registered source file report month",
         f"SELECT o.file_id FROM ods.{ods} o JOIN raw_meta.source_file f USING (file_id) "
         "WHERE o.report_month IS DISTINCT FROM f.report_month", "Required", "report_month"),
        ("count", "count_value", "Cast valid text to bigint and keep the source count",
         f"SELECT file_id, source_row_ordinal FROM ods.{ods} WHERE count_value IS NULL",
         "NULL for invalid bigint", ""),
        (effective_source, "effective_month", "Carry source action month for event families",
         f"SELECT file_id, source_row_ordinal FROM ods.{ods} WHERE effective_month IS DISTINCT FROM {effective_source}",
         "Preserve raw NULL", "effective_month" if family != "employment" else ""),
        (pay, "pay_value", "Parse numeric pay in ODS and retain the raw value and state",
         f"SELECT file_id, source_row_ordinal FROM ods.{ods} WHERE pay_state = 'VALUE' AND pay_value IS NULL",
         "NULL for unavailable pay", ""),
        (pay, "pay_state", "Classify NULL, EMPTY, REDACTED, VALUE and INVALID in J02",
         f"SELECT file_id, source_row_ordinal FROM ods.{ods} WHERE pay_state NOT IN "
         "('NULL', 'EMPTY', 'REDACTED', 'VALUE', 'INVALID')", "Required", ""),
        (f"count | {time_source} | {pay}", "dq_flags", "Record count, month and pay quality flags in ODS",
         f"SELECT file_id, source_row_ordinal FROM ods.{ods} WHERE dq_flags IS NULL", "Required", ""),
    )
    for source, target, rule, check, nullable, role in checks:
        yield row(family, source, "derived", "ods", ods, target, rule, check,
                  nullable=nullable, time_role=role)
    for field in ("count_value", "dq_flags"):
        yield row(family, f"ods.{field}", "derived", "dw", fact, field, "Carry typed value from ODS",
                  f"SELECT f.file_id, f.source_row_ordinal FROM dw.{fact} f "
                  f"JOIN ods.{ods} o USING (file_id, source_row_ordinal) "
                  f"WHERE f.{field} IS DISTINCT FROM o.{field}", nullable="Required")


def month_rows(family, ods, fact):
    business_role = "snapshot_month" if family == "employment" else "effective_month"
    business_column = "snapshot_yyyymm" if family == "employment" else "effective_month"
    business_source = "snapshot_yyyymm" if family == "employment" else TIME
    for role, source, expected in (
        ("report_month", "manifest.report_month", "o.report_month"),
        (business_role, business_source, f"CASE WHEN o.{business_column} ~ '{MONTH_PATTERN}' THEN o.{business_column} END"),
    ):
        key = f"{role}_key"
        yield row(family, source, "derived", "dw", fact, key,
                  "Resolve the independent month role against dim_month; key 0 for unknown business month",
                  f"SELECT f.file_id, f.source_row_ordinal FROM dw.{fact} f "
                  f"JOIN ods.{ods} o USING (file_id, source_row_ordinal) "
                  f"JOIN dw.dim_month d ON d.month_key=f.{key} WHERE d.yyyymm IS DISTINCT FROM {expected}",
                  time_role=role, nullable="Required")
        for column in ("month_key", "yyyymm", "calendar_year", "calendar_month"):
            yield row(family, source, "derived", "dw", "dim_month", column,
                      "Derive key, year and month from valid YYYYMM; key 0 reserves Unknown",
                      "SELECT yyyymm FROM dw.dim_month WHERE month_key <> 0 GROUP BY 1 HAVING COUNT(*) > 1",
                      time_role=role, nullable="Nullable attributes for Unknown")


def lookup_rows(family, ods, fact, relation, prefix, dimension):
    key, code, state = (f"{prefix}_{suffix}" for suffix in ("key", "code", "lookup_state"))
    raw = f"{relation}_code"
    is_category = prefix == "category"
    scope = f" WHERE family = '{family}'" if is_category else ""
    natural = f"month_key, {'family, ' if is_category else ''}{code}"
    unique = f"SELECT {natural} FROM dw.{dimension}{scope} GROUP BY {natural} HAVING COUNT(*) > 1"
    columns = {
        key: "generated identity",
        "month_key": "manifest.report_month",
        code: f"ref.derived_lookup.code ({raw})",
        f"{prefix}_label": "ref.derived_lookup.label",
        "provenance": "ref.derived_lookup.provenance",
        "verification_status": "PARTIAL",
    }
    if is_category:
        columns["family"] = f"ref.derived_lookup.relation ({relation})"
    for target, source in columns.items():
        yield row(family, source, "derived", "dw", dimension, target,
                  "Load only a unique READY lookup by report month and code; reserve key 0",
                  unique, lookup="DERIVED_LOOKUP; official coverage PARTIAL", nullable="Required", status="PARTIAL")
    source_table = f"FROM dw.{fact} f JOIN ods.{ods} o USING (file_id, source_row_ordinal)"
    family_mismatch = f" OR d.family IS DISTINCT FROM '{family}'" if is_category else ""
    for target, rule, check, nullable in (
        (key, "LEFT JOIN month-scoped derived lookup; send unresolved rows to key 0",
         f"SELECT f.file_id, f.source_row_ordinal FROM dw.{fact} f LEFT JOIN dw.{dimension} d "
         f"ON f.{key}=d.{key} WHERE d.{key} IS NULL OR (f.{key} <> 0 AND "
         f"(d.month_key IS DISTINCT FROM f.report_month_key OR d.{code} IS DISTINCT FROM f.{code}{family_mismatch}))", "Required"),
        (code, "Keep raw code including leading zeros and whitespace",
         f"SELECT f.file_id, f.source_row_ordinal {source_table} WHERE f.{code} IS DISTINCT FROM o.{raw}",
         "Preserve raw NULL"),
        (state, "Classify after btrim and uppercase REDACTED; join on the exact raw code",
         f"SELECT f.file_id, f.source_row_ordinal {source_table} WHERE f.{state} IS DISTINCT FROM "
         f"CASE WHEN o.{raw} IS NULL THEN 'NULL' WHEN btrim(o.{raw}) = '' THEN 'EMPTY' "
         f"WHEN upper(btrim(o.{raw})) = 'REDACTED' THEN 'REDACTED' "
         f"WHEN f.{key} = 0 THEN 'UNKNOWN' ELSE 'MATCHED_DERIVED' END", "Required"),
    ):
        yield row(family, raw, "string", "dw", fact, target, rule, check,
                  nullable=nullable, lookup="Exact key; retain raw code and DQ state", status="PARTIAL")


def k10_rows(family):
    checks = {
        "file_id": ("raw_meta.source_file.file_id", "Expose coverage for the matching active LOADED file"),
        "family": ("manifest.family", "Use the family of the registered source file"),
        "source_file": ("manifest.filename", "Keep the filename from the checked manifest"),
        "source_sha256": ("manifest.sha256", "Match the audited source file by SHA-256"),
        "report_month": ("manifest.report_month", "Keep the file's report month"),
        "lookup_field": ("relationship_audit.key_columns", "Keep the exact key columns used by the check"),
        "lookup_status": ("relationship_audit.status", "Keep the audit status for this scope"),
        "reference_coverage": ("relationship_audit.reference_coverage", "Distinguish complete, sampled and unchecked reference scope"),
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
