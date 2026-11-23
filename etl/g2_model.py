"""Build the runnable G2 model proposal. Grain approval remains with TV4."""

import re
from pathlib import Path

from psycopg import sql


ROOT = Path(__file__).resolve().parents[1]
FACTS = {
    "employment": "fact_employment_snapshot",
    "accessions": "fact_accessions",
    "separations": "fact_separations",
}
# TV2 review results (ehri_label_review_131.csv) meaning "same organisation, different
# wording". HOLD_ORG_SCOPE and anything unreviewed stay out of the dimensions.
BENIGN_REVIEW = ("ABBREVIATION", "FORMATTING", "TEXT_VARIANT", "DOCUMENTED_RENAME",
                 "APOSTROPHE_REPAIR")


def build_model(conn, month):
    """Build one report month; caller owns the surrounding transaction and audit."""
    month = str(month)
    if not re.fullmatch(r"[0-9]{4}(0[1-9]|1[0-2])", month):
        raise ValueError("Model month must be YYYYMM")
    month_key = int(month)
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", ("tv3/g2-model",))
        cur.execute(
            "SELECT family, count(*) FROM raw_meta.source_file "
            "WHERE report_month = %s AND is_active AND status = 'LOADED' GROUP BY family",
            (month,),
        )
        if dict(cur.fetchall()) != {family: 1 for family in FACTS}:
            raise ValueError("Model needs exactly one active LOADED file in each family")

        for family in FACTS:
            cur.execute(sql.SQL(
                "SELECT count(*) FILTER (WHERE o.count_value IS DISTINCT FROM 1), "
                "count(*) FROM {} o JOIN raw_meta.source_file f USING(file_id) "
                "WHERE f.report_month = %s AND f.is_active AND f.status = 'LOADED'"
            ).format(sql.Identifier("ods", f"ods_{family}_record")), (month,))
            invalid_counts, records = cur.fetchone()
            if invalid_counts or not records:
                raise ValueError(f"{family} has invalid count values or empty ODS; KPI build blocked")

        for path in ("sql/03_dw_ddl.sql", "sql/04_create_marts.sql"):
            cur.execute((ROOT / path).read_text(encoding="utf-8"))

        # A source lookup row is usable only if the complete observed key is unique.
        # Invalid/unreviewed rows cannot become eligible by filtering before grouping.
        # REVIEW rows become usable only when TV2's EHRI label review classifies the
        # difference as wording only (BENIGN_REVIEW); the reviewed display label is used.
        cur.execute("DROP TABLE IF EXISTS pg_temp.g2_ready_lookup")
        cur.execute(
            "CREATE TEMP TABLE g2_ready_lookup ON COMMIT DROP AS "
            "SELECT d.relation, d.report_month, d.code, "
            "min(CASE WHEN d.load_status = 'READY' THEN d.label "
            "ELSE r.proposed_display_label END) AS label, "
            "min(d.provenance) AS provenance, "
            "CASE WHEN bool_and(d.load_status = 'READY') THEN 'PARTIAL' "
            "ELSE 'REVIEWED_TV2' END AS verification_status "
            "FROM ref.derived_lookup d LEFT JOIN ref.label_review r "
            "ON r.relation = d.relation AND r.report_month = d.report_month AND r.code = d.code "
            "WHERE d.report_month = %s "
            "AND d.relation IN ('agency', 'accession_category', 'separation_category') "
            "AND btrim(d.code) <> '' AND upper(btrim(d.code)) <> 'REDACTED' "
            "GROUP BY d.relation, d.report_month, d.code HAVING count(*) = 1 "
            "AND bool_and(CASE WHEN d.load_status = 'READY' THEN d.label "
            "WHEN d.load_status = 'REVIEW' AND r.review_result = ANY(%s) "
            "THEN r.proposed_display_label END IS NOT NULL) "
            "AND bool_and(btrim(CASE WHEN d.load_status = 'READY' THEN d.label "
            "ELSE r.proposed_display_label END) <> '')",
            (month, list(BENIGN_REVIEW)),
        )
        cur.execute(
            "CREATE UNIQUE INDEX ON g2_ready_lookup(relation, report_month, code)"
        )
        cur.execute(
            "INSERT INTO dw.dim_month(month_key, yyyymm, calendar_year, calendar_month) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (month_key, month, month_key // 100, month_key % 100),
        )
        for family in FACTS:
            business_month = "snapshot_yyyymm" if family == "employment" else "effective_month"
            cur.execute(sql.SQL(
                "INSERT INTO dw.dim_month(month_key, yyyymm, calendar_year, calendar_month) "
                "SELECT DISTINCT o.{business}::integer, o.{business}, "
                "o.{business}::integer / 100, o.{business}::integer %% 100 "
                "FROM {ods} o JOIN raw_meta.source_file f USING(file_id) "
                "WHERE f.report_month = %s AND f.is_active AND f.status = 'LOADED' "
                "AND o.{business} ~ '^[0-9]{{4}}(0[1-9]|1[0-2])$' "
                "ON CONFLICT DO NOTHING"
            ).format(
                business=sql.Identifier(business_month),
                ods=sql.Identifier("ods", f"ods_{family}_record"),
            ), (month,))

        cur.execute(
            "INSERT INTO dw.dim_agency "
            "(month_key, agency_code, agency_label, provenance, verification_status) "
            "SELECT %s, code, label, provenance, verification_status FROM g2_ready_lookup "
            "WHERE relation = 'agency' "
            "ON CONFLICT(month_key, agency_code) DO UPDATE SET "
            "agency_label=excluded.agency_label, provenance=excluded.provenance, "
            "verification_status=excluded.verification_status", (month_key,),
        )
        cur.execute(
            "INSERT INTO dw.dim_action_category "
            "(month_key, family, category_code, category_label, provenance, verification_status) "
            "SELECT %s, CASE relation WHEN 'accession_category' THEN 'accessions' "
            "ELSE 'separations' END, code, label, provenance, verification_status "
            "FROM g2_ready_lookup WHERE relation IN ('accession_category', 'separation_category') "
            "ON CONFLICT(month_key, family, category_code) DO UPDATE SET "
            "category_label=excluded.category_label, provenance=excluded.provenance, "
            "verification_status=excluded.verification_status", (month_key,),
        )

        metrics = {"model_status": "PROPOSED_PENDING_TV4", "month": month, "facts": {}}
        for family, fact_name in FACTS.items():
            fact = sql.Identifier("dw", fact_name)
            cur.execute(sql.SQL("DELETE FROM {} WHERE report_month_key = %s").format(fact),
                        (month_key,))
            insert_fact(cur, family, fact, month_key)
            cur.execute(sql.SQL(
                "SELECT count(*), coalesce(sum(count_value),0), "
                "count(*) FILTER(WHERE agency_key=0) FROM {} WHERE report_month_key=%s"
            ).format(fact), (month_key,))
            records, total, unknown_agency = cur.fetchone()
            cur.execute(sql.SQL(
                "SELECT coalesce(sum(row_count),0) FROM raw_meta.source_file "
                "WHERE family=%s AND report_month=%s AND is_active AND status='LOADED'"
            ), (family, month))
            expected = cur.fetchone()[0]
            if records != expected:
                raise ValueError(f"{family} Fact row count does not match active source metadata")
            metrics["facts"][family] = {
                "rows": records, "measure_sum": int(total), "unknown_agency_rows": unknown_agency,
            }

        # These aggregate tables are small. Recompute from every persisted Fact so
        # all source report months, including effective/snapshot exceptions, remain represented.
        cur.execute("DELETE FROM mart.workforce_monthly")
        cur.execute(
            "INSERT INTO mart.workforce_monthly "
            "SELECT f.snapshot_month_key, f.agency_key, d.agency_code, d.agency_label, "
            "sum(f.count_value), count(*) "
            "FROM dw.fact_employment_snapshot f JOIN dw.dim_agency d USING(agency_key) "
            "GROUP BY f.snapshot_month_key, f.agency_key, d.agency_code, d.agency_label"
        )
        cur.execute("DELETE FROM mart.personnel_flows_monthly")
        cur.execute(
            "INSERT INTO mart.personnel_flows_monthly "
            "WITH flows AS ("
            "SELECT report_month_key, agency_key, sum(count_value) AS accessions, "
            "0::numeric AS separations, count(*) AS source_rows "
            "FROM dw.fact_accessions GROUP BY report_month_key, agency_key "
            "UNION ALL "
            "SELECT report_month_key, agency_key, 0::numeric, sum(count_value), count(*) "
            "FROM dw.fact_separations GROUP BY report_month_key, agency_key) "
            "SELECT f.report_month_key, f.agency_key, d.agency_code, d.agency_label, "
            "sum(f.accessions), sum(f.separations), sum(f.accessions)-sum(f.separations), "
            "sum(f.source_rows) FROM flows f JOIN dw.dim_agency d USING(agency_key) "
            "GROUP BY f.report_month_key, f.agency_key, d.agency_code, d.agency_label"
        )
        cur.execute(
            "SELECT coalesce(sum(headcount),0), count(*) FROM mart.workforce_monthly "
            "WHERE month_key=%s", (month_key,),
        )
        headcount, workforce_groups = cur.fetchone()
        cur.execute(
            "SELECT coalesce(sum(accessions),0), coalesce(sum(separations),0), count(*) "
            "FROM mart.personnel_flows_monthly WHERE month_key=%s", (month_key,),
        )
        accessions, separations, flow_groups = cur.fetchone()
        metrics["marts"] = {
            "headcount": int(headcount), "accessions": int(accessions),
            "separations": int(separations), "workforce_groups": workforce_groups,
            "flow_groups": flow_groups,
        }
        if (accessions != metrics["facts"]["accessions"]["measure_sum"]
                or separations != metrics["facts"]["separations"]["measure_sum"]):
            raise ValueError("Event Mart sums do not reconcile to report-month Facts")
        return metrics


def lookup_state_sql(raw_code, dimension_key):
    return (
        f"CASE WHEN {raw_code} IS NULL THEN 'NULL' "
        f"WHEN btrim({raw_code}) = '' THEN 'EMPTY' "
        f"WHEN upper(btrim({raw_code})) = 'REDACTED' THEN 'REDACTED' "
        f"WHEN {dimension_key} IS NULL THEN 'UNKNOWN' ELSE 'MATCHED_DERIVED' END"
    )


def insert_fact(cur, family, fact, month_key):
    employment = family == "employment"
    business_column = "snapshot_yyyymm" if employment else "effective_month"
    business_key = "snapshot_month_key" if employment else "effective_month_key"
    base_columns = [
        "file_id", "source_row_ordinal", "report_month_key", business_key,
        "agency_key", "agency_code", "agency_lookup_state", "count_value", "dq_flags",
    ]
    selects = [
        "o.file_id", "o.source_row_ordinal", "%(month_key)s",
        "coalesce(t.month_key,0)", "coalesce(a.agency_key,0)", "o.agency_code",
        lookup_state_sql("o.agency_code", "a.agency_key"),
        "o.count_value", "coalesce(o.dq_flags,ARRAY[]::text[])",
    ]
    extra_join = sql.SQL("")
    if not employment:
        category = "accession_category" if family == "accessions" else "separation_category"
        base_columns.extend(["category_key", "category_code", "category_lookup_state"])
        selects.extend([
            "coalesce(c.category_key,0)", f"o.{category}_code",
            lookup_state_sql(f"o.{category}_code", "c.category_key"),
        ])
        extra_join = sql.SQL(
            "LEFT JOIN g2_ready_lookup lc ON lc.relation={relation} "
            "AND lc.report_month=o.report_month AND lc.code=o.{category} "
            "LEFT JOIN dw.dim_action_category c ON c.month_key=%(month_key)s "
            "AND c.family={family} AND c.category_code=lc.code "
        ).format(relation=sql.Literal(category), category=sql.Identifier(category + "_code"),
                 family=sql.Literal(family))
    cur.execute(sql.SQL(
        "INSERT INTO {fact} ({columns}) SELECT {selects} FROM {ods} o "
        "JOIN raw_meta.source_file f USING(file_id) "
        "LEFT JOIN dw.dim_month t ON t.yyyymm=o.{business} "
        "LEFT JOIN g2_ready_lookup la ON la.relation='agency' "
        "AND la.report_month=o.report_month AND la.code=o.agency_code "
        "LEFT JOIN dw.dim_agency a ON a.month_key=%(month_key)s AND a.agency_code=la.code "
        "{extra} WHERE f.report_month=%(month)s AND f.is_active AND f.status='LOADED'"
    ).format(
        fact=fact, columns=sql.SQL(", ").join(map(sql.Identifier, base_columns)),
        selects=sql.SQL(", ").join(map(sql.SQL, selects)),
        ods=sql.Identifier("ods", f"ods_{family}_record"),
        business=sql.Identifier(business_column), extra=extra_join,
    ), {"month_key": month_key, "month": str(month_key)})
