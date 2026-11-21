"""Audit candidate source keys over all twelve baseline files without inventing reference FKs."""
import argparse
from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import duckdb

from source_baseline import DUTY, EHRI, FWD, ROOT, identifier, make_inventory, paths, read_csv, write_csv

OPM_AGENCY = "https://data.opm.gov/data-standards/agency-subelement"
OPM_REFERENCE = ROOT / "data/reference/opm_lookup_g2.csv"

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
MVP_LOOKUPS = ("agency", "agency_subelement", "accession_category", "separation_category")


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
    fedscope_labels = defaultdict(set)
    dated_labels = defaultdict(list)
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
        if row.get("source_scope") == "FedScope 202404–202503" and row.get("label"):
            fedscope_labels[relation, row["code"]].add(row["label"])
        elif start is not None and row.get("label"):
            dated_labels[relation, row["code"]].append((start, end, row["label"]))
    if any(len({r[4] for r in rows}) != 1 for rows in references.values()):
        raise ValueError("Use one reference coverage mode per relation")
    return references, fedscope_labels, dated_labels


def month_end(month):
    year, month_number = int(month[:4]), int(month[4:])
    return date(year, month_number, monthrange(year, month_number)[1])


def active_reference_keys(month, references):
    as_of = month_end(month)
    return Counter((code,) for code, start, end, _, _ in references
                   if (start is None or start <= as_of) and (end is None or as_of <= end))


def reference_metrics(by_key, month, references, source_rows=None):
    result = dict(reference_coverage="NOT_CHECKED", reference_eligible_rows="",
                  reference_unique_matches="", reference_checked_duplicate_keys="",
                  reference_left_join_rows="", orphan_rows="", duplicate_ref_keys="",
                  k10_coverage_pct="")
    if not month or not references:
        return result
    active = active_reference_keys(month, references)
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


def profile_keys(grouped, label):
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
    return counts, by_key, labels


def audit_scope(grouped, relation, scope, month=None, references=()):
    keys, label, reference = RELATIONS[relation]
    counts, by_key, labels = profile_keys(grouped, label)
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
    reasons = [("MULTIPLE_LABELS", ambiguous), ("NO_LABEL", unlabelled)]
    if metrics["reference_coverage"] == "COMPLETE":
        active = active_reference_keys(month, references)
        reasons.extend([
            ("OPM_KEY_NOT_ACTIVE", [key for key in by_key if active[key] == 0]),
            ("OPM_DUPLICATE_ACTIVE_KEY", [key for key in active if active[key] > 1]),
        ])
    exceptions = [
        dict(relation=relation, scope=scope, key=" | ".join(key), exception=reason,
             observed_labels=" | ".join(sorted(labels[key])), eligible_rows=by_key[key])
        for reason, matches in reasons
        for key in sorted(matches)
    ]
    return result, exceptions


def derived_lookup(by_month, references, fedscope_labels, dated_labels):
    rows = []
    archived_relations = {relation for relation, _ in fedscope_labels}
    for (relation, month), grouped in sorted(by_month.items()):
        _, by_key, labels = profile_keys(grouped, RELATIONS[relation][1])
        catalog = references.get(relation, ())
        active = active_reference_keys(month, catalog) if catalog and catalog[0][4] == "COMPLETE" else None
        as_of = month_end(month)
        for key, count in sorted(by_key.items()):
            names = sorted(labels[key])
            observed = {name.strip().casefold() for name in names}
            reason = "NO_LABEL" if not names else "MULTIPLE_LABELS" if len(names) > 1 else ""
            if active is not None and active[key] != 1:
                reason = "OPM_DUPLICATE_ACTIVE_KEY" if active[key] > 1 else "OPM_KEY_NOT_ACTIVE"
            published = fedscope_labels.get((relation, key[0]), set())
            label_check = ""
            if published:
                normalized = {name.strip().casefold() for name in published}
                label_check = "MATCH" if observed == normalized and len(normalized) == 1 else "REVIEW"
                if label_check == "REVIEW" and not reason:
                    reason = "FEDSCOPE_LABEL_REVIEW"
            elif relation in archived_relations:
                label_check = "NOT_IN_ARCHIVE"
                reason = reason or "FEDSCOPE_CODE_NOT_OBSERVED"
            active_labels = [label for start, end, label in dated_labels.get((relation, key[0]), ())
                             if start <= as_of and (end is None or as_of <= end)]
            ehri_label = active_labels[0] if len(active_labels) == 1 else ""
            ehri_check = ""
            if ehri_label:
                ehri_check = "MATCH" if observed == {ehri_label.strip().casefold()} else "DIFFERENT"
            status = "UNKNOWN" if reason else "READY"
            rows.append(dict(relation=relation, report_month=month, code=key[0],
                             label=names[0] if status == "READY" else "", observed_rows=count,
                             provenance="DERIVED_LOOKUP", load_status=status, exception=reason,
                             observed_labels=" | ".join(names), fedscope_label_check=label_check,
                             ehri_label=ehri_label, ehri_label_check=ehri_check))
    return rows


def scan(con, files, schemas, inventory, references, fedscope_labels, dated_labels):
    query = (ROOT / "sql/tests/04_fk_audit.sql").read_text(encoding="utf-8")
    summaries = []
    exceptions = []
    all_scopes = defaultdict(Counter)
    by_month = defaultdict(Counter)
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
            if relation in MVP_LOOKUPS:
                by_month[relation, month].update(counts)
    for (relation, scope), grouped in all_scopes.items():
        item, issues = audit_scope(grouped, relation, f"{scope}/all_months")
        summaries.append(item)
        if scope == "all_families":
            exceptions.extend(issues)
    return summaries, exceptions, derived_lookup(by_month, references, fedscope_labels, dated_labels)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    parser.add_argument("--references", type=Path, default=OPM_REFERENCE,
                        help="Scoped official keys and validity dates")
    args = parser.parse_args()
    files = paths(args.raw.resolve())
    inventory, schemas = make_inventory(files)
    references, fedscope_labels, dated_labels = load_reference(args.references)
    with duckdb.connect() as con:
        summaries, exceptions, lookup = scan(con, files, schemas, inventory, references,
                                             fedscope_labels, dated_labels)
    write_csv(ROOT / "docs/04_relationship_audit.csv", summaries)
    write_csv(ROOT / "evidence/TV2_week2/relationship_exceptions.csv", exceptions)
    write_csv(ROOT / "data/reference/derived_lookup_g2.csv", lookup)
    print(f"{len(summaries)} relationship scopes, {len(exceptions)} exception groups, "
          f"{len(lookup)} derived code-month keys")


if __name__ == "__main__":
    main()
