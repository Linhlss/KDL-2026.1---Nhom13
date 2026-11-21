"""Prepare the scoped OPM reference CSV from public FedScope and EHRI files."""
import argparse
import csv
import hashlib
from datetime import date, datetime
from io import TextIOWrapper
from pathlib import Path
from zipfile import ZipFile

from source_baseline import ROOT, read_csv, write_csv

AGENCY_URL = "https://data.opm.gov/data-standards/agency-subelement"
BASELINE_START = date(2025, 3, 1)
BASELINE_END = date(2025, 6, 30)
EHRI_TAB_ROWS = {"Current values": 802, "Past values": 2931}
FED_SCOPE = {
    "accession_category": (
        "https://www.opm.gov/data/datasets/Files/761/6124a377-5e92-43e7-ade2-3be674580bc7.zip",
        "44d9284bf5310d8a676f6181fff24d71a8cf67d5ff81eb1e94628497569046ef",
        "March_2025_Accessions.txt", "ACC", "ACCT",
    ),
    "separation_category": (
        "https://www.opm.gov/data/datasets/Files/763/1e0ad2cd-40ee-4646-9daa-58b762bcddfb.zip",
        "8714663f56364894ad49c91831af707b897b49add9130a485c34593573f983d0",
        "March_2025_Separations.txt", "SEP", "SEPT",
    ),
}


def reference_row(relation, code, label, valid_from, valid_through, source_url, coverage, source_scope):
    return dict(relation=relation, code=code, label=label, valid_from=valid_from,
                valid_through=valid_through, source_url=source_url, coverage=coverage,
                source_scope=source_scope)


def fedscope_categories(path, relation):
    url, sha256, member, code_field, label_field = FED_SCOPE[relation]
    with path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != sha256:
            raise ValueError(f"Unexpected FedScope archive hash for {path}")
    with ZipFile(path) as archive, TextIOWrapper(
        archive.open(member), encoding="utf-8-sig", newline=""
    ) as stream:
        rows = csv.DictReader(stream, delimiter="|")
        pairs = {(row[code_field], row[label_field]) for row in rows}
    return [reference_row(relation, code, label, "", "", url, "SAMPLE", "FedScope 202404–202503")
            for code, label in sorted(pairs)]


def agency_categories(paths):
    result = []
    for path, tab in zip(paths, ("Current values", "Past values"), strict=True):
        rows = read_csv(path)
        if len(rows) != EHRI_TAB_ROWS[tab]:
            raise ValueError(f"{tab}: expected {EHRI_TAB_ROWS[tab]} rows, found {len(rows)}")
        for row in rows:
            code = row["code"]
            start = datetime.strptime(row["valid_from"], "%m/%d/%Y").date()
            end_text = row["valid_through"]
            end = None if end_text == "Present" else datetime.strptime(end_text, "%m/%d/%Y").date()
            if end is not None and end < start:
                raise ValueError(f"Invalid dates for {code}: {start} to {end}")
            if start > BASELINE_END or (end is not None and end < BASELINE_START):
                continue
            if len(code) not in (2, 4):
                raise ValueError(f"Unexpected EHRI Agency/Subelement key {code!r}")
            relation = "agency" if len(code) == 2 else "agency_subelement"
            # The high-level FWD Agency domain is not the same as EHRI's two-character subset.
            coverage = "SAMPLE" if relation == "agency" else "COMPLETE"
            result.append(reference_row(relation, code, row["label"], start.isoformat(),
                                        end.isoformat() if end else "", AGENCY_URL, coverage, tab))
        print(f"{tab}: {len(rows)} source rows")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accessions_zip", type=Path)
    parser.add_argument("separations_zip", type=Path)
    parser.add_argument("--agency-tables", type=Path, nargs=2, required=True, metavar=("CURRENT", "PAST"),
                        help="Full EHRI tables with code, label, valid_from and valid_through")
    args = parser.parse_args()
    agency = agency_categories(args.agency_tables)
    rows = agency + fedscope_categories(args.accessions_zip, "accession_category") + fedscope_categories(
        args.separations_zip, "separation_category")
    rows.sort(key=lambda row: (row["relation"], row["code"], row["valid_from"], row["label"]))
    write_csv(ROOT / "data/reference/opm_lookup_g2.csv", rows)
    print(f"{len(rows)} scoped OPM reference rows")


if __name__ == "__main__":
    main()
