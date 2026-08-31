#!/usr/bin/env python3
"""Fetch the WCO Harmonized System nomenclature into data/hs/.

This is the spine every other lookup hangs off: an India ITC(HS) 8-digit line is
an HS 6-digit subheading plus a two-digit national extension, so a code whose
first six digits are not in the HS nomenclature is malformed and no rate lookup
against it can be trusted.

The dataset is a public-domain extraction of the WCO HS 2022 nomenclature. It
carries codes and descriptions only -- deliberately no duty rates, because a
rate must come from ICEGATE/CBIC on the day you file.

    python3 fetch_hs.py            # fetch into ../data/hs
    python3 fetch_hs.py --check    # verify checksums and staleness, no network
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import provenance  # noqa: E402
from net import EgressBlocked, Fetcher, FetchError  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data", "hs"))
SOURCES = os.path.join(HERE, "sources.json")


def load_source() -> dict:
    with open(SOURCES, encoding="utf-8") as fh:
        return json.load(fh)["sources"]["hs_nomenclature"]


def normalise(nomenclature_csv: str, sections_csv: str) -> tuple[list, dict]:
    """Flatten the source CSVs into one row per code with its chapter/section."""
    sections = {}
    for row in csv.DictReader(io.StringIO(sections_csv.lstrip("﻿"))):
        sections[row["section"]] = row["name"].strip()

    rows = []
    for row in csv.DictReader(io.StringIO(nomenclature_csv.lstrip("﻿"))):
        code = (row.get("hscode") or "").strip()
        if not code or code.upper() == "TOTAL":
            continue
        level = int(row["level"])
        rows.append(
            {
                "hs_code": code,
                "level": level,
                "description": (row.get("description") or "").strip(),
                "parent": (row.get("parent") or "").strip(),
                "chapter": code[:2],
                "section": (row.get("section") or "").strip(),
                "section_name": sections.get((row.get("section") or "").strip(), ""),
            }
        )
    rows.sort(key=lambda r: (len(r["hs_code"]), r["hs_code"]))
    return rows, sections


def write(rows: list, sections: dict, source: dict) -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    csv_path = os.path.join(DATA_DIR, "hs_nomenclature.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "hs_code",
                "level",
                "description",
                "parent",
                "chapter",
                "section",
                "section_name",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    sections_path = os.path.join(DATA_DIR, "hs_sections.json")
    with open(sections_path, "w", encoding="utf-8") as fh:
        json.dump(sections, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    by_level = {}
    for row in rows:
        by_level[row["level"]] = by_level.get(row["level"], 0) + 1

    return provenance.write_manifest(
        directory=DATA_DIR,
        dataset="hs_nomenclature",
        source_name=source["publisher"],
        source_url=source["url"],
        files=["hs_nomenclature.csv", "hs_sections.json"],
        max_age_days=source["max_age_days"],
        licence=source["licence"],
        notes=(
            "Codes and descriptions only. Contains NO duty rates: BCD/IGST/SWS/AIDC/cess "
            "must be read from ICEGATE or the CBIC tariff for the Bill of Entry date."
        ),
        extra={
            "hs_version": "HS 2022",
            "rows": len(rows),
            "rows_by_level": {str(k): v for k, v in sorted(by_level.items())},
            "sections": len(sections),
        },
    )


def cmd_check() -> int:
    ok, problems = provenance.verify(DATA_DIR)
    manifest = provenance.read_manifest(DATA_DIR)
    if manifest is None:
        print(f"NOT FETCHED  {DATA_DIR}\n  run: python3 fetch_hs.py")
        return 1
    print(provenance.describe(manifest))
    print(f"  rows: {manifest.get('rows')}  expires: {provenance.expiry(manifest)}")
    for problem in problems:
        print(f"  ! {problem}")
    return 0 if ok else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify local data, no network")
    args = parser.parse_args(argv)

    if args.check:
        return cmd_check()

    source = load_source()
    fetcher = Fetcher()
    try:
        print(f"GET {source['url']}")
        nomenclature = fetcher.get(source["url"]).text
        print(f"GET {source['sections_url']}")
        sections_csv = fetcher.get(source["sections_url"]).text
    except EgressBlocked as exc:
        print(f"EGRESS BLOCKED: {exc.detail}\n  host unreachable from this network: {exc.url}")
        print("  Nothing was written. Run this from a network that permits the host.")
        return 2
    except FetchError as exc:
        print(f"FETCH FAILED: {exc}")
        return 2

    rows, sections = normalise(nomenclature, sections_csv)
    if len(rows) < 5000:
        print(f"REFUSED: source returned only {len(rows)} rows, expected >5000. Not overwriting.")
        return 3

    manifest = write(rows, sections, source)
    print(
        f"\nwrote {manifest['rows']} codes to {DATA_DIR}\n"
        f"  by level: {manifest['rows_by_level']}\n"
        f"  sections: {manifest['sections']}\n"
        f"  expires:  {provenance.expiry(manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
