"""Audit candidate source keys over all twelve baseline files without inventing reference FKs."""
import argparse
from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import duckdb

from source_baseline import DUTY, EHRI, FWD, ROOT, identifier, make_inventory, paths, read_csv, write_csv

OPM_AGENCY = "https://data.opm.gov/data-standards/agency-subelement"
OPM_SAMPLE = ROOT / "data/reference/opm_lookup_samples.csv"

RELATIONS = {
    "department": (("department_code",), "department", FWD),
    "agency": (("agency_code",), "agency", OPM_AGENCY),
    "agency_subelement": (("agency_subelement_code",), "agency_subelement", OPM_AGENCY),
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
    trimmed = [value.strip(" ") for value in values]
    if "" in trimmed:
        return "empty"
    if any(value.upper() == "REDACTED" for value in trimmed):
        return "redacted"
    return "present"


def load_reference(path):
    references = defaultdict(list)
    for row in read_csv(path):
        relation = row["relation"]
        if relation not in RELATIONS or len(RELATIONS[relation][0]) != 1:
            raise ValueError(f"No single-column reference key for {relation}")
        mode = row["coverage"]
        start = date.fromisoformat(row["valid_from"]) if row["valid_from"] else None
        end = date.fromisoformat(row["valid_through"]) if row["valid_through"] else None
        if (mode not in {"SAMPLE", "COMPLETE"} or state((row["code"],)) != "present"
                or not row["source_url"].startswith("https://") or (mode == "COMPLETE" and start is None)
                or (end is not None and (start is None or end < start))):
            raise ValueError(f"Invalid reference record for {relation}: {row}")
        references[relation].append((row["code"], start, end, row["source_url"], mode))
    if any(len({r[4] for r in rows}) != 1 for rows in references.values()):
        raise ValueError("Use one reference coverage mode per relation")
    return references


def reference_metrics(by_key, month, references, source_rows=None):
    result = dict(reference_coverage="NOT_CHECKED", reference_eligible_rows="",
                  reference_unique_matches="", reference_checked_duplicate_keys="",
                  reference_left_join_rows="", orphan_rows="", duplicate_ref_keys="",
                  k10_coverage_pct="")
    if not month or not references:
        return result
    year, month_number = int(month[:4]), int(month[4:])
    as_of = date(year, month_number, monthrange(year, month_number)[1])
    active = Counter((code,) for code, start, end, _, _ in references
                     if (start is None or start <= as_of) and (end is None or as_of <= end))
    if not active:
        return result
    complete = references[0][4] == "COMPLETE"
    observed = by_key if complete else {key: by_key[key] for key in active if key in by_key}
    eligible = sum(observed.values())
    matched = sum(n for key, n in observed.items() if active[key] == 1)
    duplicate = sum(n > 1 for n in active.values())
    join_rows = sum(n * max(active[key], 1) for key, n in observed.items())
    if complete and source_rows is not None:
        join_rows += source_rows - eligible
    result.update(reference_coverage="COMPLETE" if complete else "SAMPLE",
                  reference_eligible_rows=eligible, reference_unique_matches=matched,
                  reference_checked_duplicate_keys=duplicate,
                  reference_left_join_rows=join_rows)
    if complete:
        orphans = sum(n for key, n in observed.items() if not active[key])
        result.update(orphan_rows=orphans, duplicate_ref_keys=duplicate)
        if eligible and not (orphans or duplicate):
            result["k10_coverage_pct"] = f"{100 * matched / eligible:.6f}"
    return result


def audit_scope(grouped, relation, scope, month=None, references=()):
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
    tested_rows = sum(counts.values())
    metrics = reference_metrics(by_key, month, references, tested_rows)
    verified = metrics["reference_coverage"] == "COMPLETE" and not (
        metrics["orphan_rows"] or metrics["duplicate_ref_keys"])
    reference_scope = "See dated reference checks by file; complete catalog required"
    if month and references:
        reference = " | ".join(sorted({row[3] for row in references}))
        reference_scope = f"{month} month-end; {metrics['reference_coverage']}"
    result = dict(relation=relation, scope=scope, key_columns=" + ".join(keys),
                  label_column=label or "", source_reference=reference,
                  reference_scope=reference_scope,
                  tested_rows=tested_rows, eligible_rows=counts["present"],
                  null_rows=counts["null"], empty_rows=counts["empty"],
                  redacted_rows=counts["redacted"], distinct_keys_exact=len(by_key),
                  keys_with_multiple_labels=len(ambiguous) if label else "",
                  keys_without_observed_label=len(unlabelled) if label else "",
                  derived_lookup_keys=len(derived_keys) if label else "",
                  derived_lookup_unmatched_rows=(sum(by_key[key] for key in by_key.keys() - derived_keys) if label else ""),
                  **metrics, status="VERIFIED" if verified else "PARTIAL" if label else "UNSUPPORTED",
                  reviewer="PENDING TV3/TV5")
    exceptions = [
        dict(relation=relation, scope=scope, key=" | ".join(key), exception=reason,
             observed_labels=" | ".join(sorted(labels[key])), eligible_rows=by_key[key])
        for reason, matches in (("MULTIPLE_LABELS", ambiguous), ("NO_LABEL", unlabelled))
        for key in sorted(matches)
    ]
    return result, exceptions


def scan(con, files, schemas, inventory, references):
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
            item, issues = audit_scope(counts, relation, scope, month, references.get(relation, ()))
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
    parser.add_argument("--references", type=Path, default=OPM_SAMPLE,
                        help="Scoped official keys and validity dates; defaults to OPM samples")
    args = parser.parse_args()
    files = paths(args.raw.resolve())
    inventory, schemas = make_inventory(files)
    with duckdb.connect() as con:
        summaries, exceptions = scan(con, files, schemas, inventory, load_reference(args.references))
    write_csv(ROOT / "docs/04_relationship_audit.csv", summaries)
    write_csv(ROOT / "evidence/TV2_week2/relationship_exceptions.csv", exceptions)
    print(f"{len(summaries)} relationship scopes; {len(exceptions)} exception groups")


if __name__ == "__main__":
    main()
