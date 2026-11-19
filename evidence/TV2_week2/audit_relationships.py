"""Audit candidate source keys over all twelve baseline files without inventing reference FKs."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

import duckdb

from source_baseline import DUTY, EHRI, FWD, ROOT, identifier, make_inventory, paths, write_csv

RELATIONS = {
    "department": (("department_code",), "department", FWD),
    "agency": (("agency_code",), "agency", EHRI),
    "agency_subelement": (("agency_subelement_code",), "agency_subelement", EHRI),
    "occupational_group": (("occupational_group_code",), "occupational_group", FWD),
    "occupational_series": (("occupational_series_code",), "occupational_series", EHRI),
    "duty_station": (("duty_station_code",), "duty_station_city", DUTY),
    "pay_plan": (("pay_plan_code",), "pay_plan", EHRI),
    "pay_plan_grade": (("pay_plan_code", "grade"), None, EHRI),
    "accession_category": (("accession_category_code",), "accession_category", FWD),
    "separation_category": (("separation_category_code",), "separation_category", FWD),
}


def state(values):
    if None in values:
        return "null"
    if "" in values:
        return "empty"
    if "REDACTED" in values:
        return "redacted"
    return "present"


def audit_scope(grouped, relation, scope):
    keys, label, reference = RELATIONS[relation]
    counts = Counter()
    by_key = Counter()
    labels = defaultdict(set)
    for (key, name), count in grouped.items():
        category = state(key)
        counts[category] += count
        if category == "present":
            by_key[key] += count
            if label and state((name,)) == "present":
                labels[key].add(name)
    ambiguous = [key for key in by_key if len(labels[key]) > 1]
    unlabelled = [key for key in by_key if not labels[key]] if label else []
    derived_keys = {key for key in by_key if len(labels[key]) == 1} if label else set(by_key)
    result = dict(relation=relation, scope=scope, key_columns=" + ".join(keys),
                  label_column=label or "", source_reference=reference,
                  reference_scope="OPM definitions available; baseline-valid external key list pending",
                  tested_rows=sum(counts.values()), eligible_rows=counts["present"],
                  null_rows=counts["null"], empty_rows=counts["empty"],
                  redacted_rows=counts["redacted"], distinct_keys_exact=len(by_key),
                  keys_with_multiple_labels=len(ambiguous) if label else "",
                  keys_without_observed_label=len(unlabelled) if label else "",
                  derived_lookup_keys=len(derived_keys) if label else "",
                  derived_lookup_unmatched_rows=(sum(by_key[key] for key in by_key.keys() - derived_keys) if label else ""),
                  orphan_rows="", duplicate_ref_keys="",
                  status="UNSUPPORTED" if not label else "PARTIAL", reviewer="PENDING TV3/TV5")
    exceptions = [
        dict(relation=relation, scope=scope, key=" | ".join(key), exception=reason,
             observed_labels=" | ".join(sorted(labels[key])), eligible_rows=by_key[key])
        for reason, matches in (("MULTIPLE_LABELS", ambiguous), ("NO_LABEL", unlabelled))
        for key in sorted(matches)
    ]
    return result, exceptions


def scan(con, files, schemas, inventory):
    query = (ROOT / "sql/tests/04_fk_audit.sql").read_text(encoding="utf-8")
    summaries = []
    exceptions = []
    all_scopes = defaultdict(Counter)
    per_file = {row["filename"]: row["row_count"] for row in inventory}
    for (family, month), path in files.items():
        scope = f"{family}/{month}"
        # DuckDB exposes zero-based positions; ODS uses the one-based prototype convention.
        n, unique_n, first, last = con.execute("""
            SELECT count(*), count(DISTINCT file_row_number), min(file_row_number + 1), max(file_row_number + 1)
            FROM read_parquet(?, file_row_number=true)
        """, [str(path)]).fetchone()
        if n != per_file[path.name] or (n, first, last) != (unique_n, 1, n):
            raise ValueError(f"File-row grain failed for {path.name}")
        for relation, (keys, label, _) in RELATIONS.items():
            if not set(keys).issubset(schemas[family, month]):
                continue
            items = ", ".join(identifier(key) for key in keys)
            groups = con.execute(query.replace("{{keys}}", items).replace(
                "{{label}}", identifier(label) if label else "NULL"), [str(path)]).fetchall()
            counts = Counter({(tuple(row[:-2]), row[-2]): row[-1] for row in groups})
            item, issues = audit_scope(counts, relation, scope)
            if item["tested_rows"] != n:
                raise ValueError(f"Lost rows in audit of {relation}, {scope}")
            summaries.append(item)
            exceptions.extend(issues)
            all_scopes[relation, family].update(counts)
            all_scopes[relation, "all_families"].update(counts)
    for (relation, scope), grouped in all_scopes.items():
        item, issues = audit_scope(grouped, relation, f"{scope}/all_months")
        summaries.append(item)
        if scope == "all_families":
            exceptions.extend(issues)
    return summaries, exceptions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    args = parser.parse_args()
    files = paths(args.raw.resolve())
    inventory, schemas = make_inventory(files)
    with duckdb.connect() as con:
        summaries, exceptions = scan(con, files, schemas, inventory)
    write_csv(ROOT / "docs/04_relationship_audit.csv", summaries)
    write_csv(ROOT / "evidence/TV2_week2/relationship_exceptions.csv", exceptions)
    print(f"{len(summaries)} relationship scopes; {len(exceptions)} exception groups")


if __name__ == "__main__":
    main()
