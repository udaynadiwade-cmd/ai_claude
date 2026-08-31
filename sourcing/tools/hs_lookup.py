#!/usr/bin/env python3
"""Look up and validate HS / ITC(HS) codes against the fetched WCO nomenclature.

India's ITC(HS) is the 6-digit HS subheading plus a 2-digit national extension.
So an 8-digit code whose first six digits are absent from the HS nomenclature is
malformed, and any duty quoted against it is quoting a code that does not exist.
This tool catches that before a PO is raised.

    python3 hs_lookup.py 85444999          # explain a code, with its full tree
    python3 hs_lookup.py --search "cable"  # find candidate headings by keyword
    python3 hs_lookup.py --chapter 85      # list the headings in a chapter
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import provenance  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data", "hs"))
CSV_PATH = os.path.join(DATA_DIR, "hs_nomenclature.csv")


class NomenclatureMissing(RuntimeError):
    pass


def load() -> dict:
    if not os.path.exists(CSV_PATH):
        raise NomenclatureMissing(
            f"HS nomenclature not present at {CSV_PATH}\n"
            "  run: python3 fetch_hs.py"
        )
    with open(CSV_PATH, encoding="utf-8") as fh:
        return {row["hs_code"]: row for row in csv.DictReader(fh)}


def clean(code: str) -> str:
    """Strip the dots and spaces people type: '8544.49.99' -> '85444999'."""
    return re.sub(r"[^0-9]", "", code or "")


def validate(code: str, table: dict) -> dict:
    """Classify a code and return a structured verdict."""
    digits = clean(code)
    result = {
        "input": code,
        "digits": digits,
        "length": len(digits),
        "valid": False,
        "kind": "",
        "problems": [],
        "chain": [],
        "national_extension": "",
    }

    if not digits:
        result["problems"].append("no digits supplied")
        return result
    if len(digits) % 2:
        result["problems"].append(
            f"{len(digits)} digits: HS codes are even-length (2, 4, 6 or 8)"
        )
        return result
    if len(digits) > 8:
        result["problems"].append(f"{len(digits)} digits: longer than an 8-digit ITC(HS) line")
        return result

    if digits[:2] == "99":
        result["problems"].append(
            "Chapter 99 in this dataset is UN Comtrade's 'commodities not specified' bucket, "
            "not a WCO trade chapter. It is not a classification -- reclassify the goods."
        )
        return result

    for cut in (2, 4, 6):
        if len(digits) >= cut:
            node = table.get(digits[:cut])
            if node is None:
                result["problems"].append(
                    f"HS-{cut} '{digits[:cut]}' is not in the WCO nomenclature"
                )
                return result
            result["chain"].append(node)

    if len(digits) == 8:
        result["kind"] = "ITC(HS) 8-digit national line"
        result["national_extension"] = digits[6:]
        result["valid"] = True
        result["problems"].append(
            "The last 2 digits are India's national extension and are NOT covered by the "
            "WCO nomenclature -- confirm the 8-digit line exists on ICEGATE/DGFT before filing."
        )
    else:
        result["kind"] = {2: "chapter", 4: "heading", 6: "subheading"}[len(digits)]
        result["valid"] = True
        if len(digits) < 8:
            result["problems"].append(
                f"Only {len(digits)} digits. An Indian Bill of Entry needs the full "
                "8-digit ITC(HS) line -- duty can differ between extensions of the same HS-6."
            )
    return result


def render(result: dict, table: dict) -> str:
    out = []
    status = "OK" if result["valid"] else "INVALID"
    out.append(f"{status}  {result['input']} -> {result['digits']} ({result['kind'] or 'unknown'})")
    if result["chain"]:
        section = result["chain"][0]
        if section["section_name"]:
            out.append(f"Section {section['section']} — {section['section_name']}")
        for node in result["chain"]:
            indent = "  " * (int(node["level"]) // 2 - 1)
            out.append(f"  {indent}{node['hs_code']:<8} {node['description']}")
    if result["national_extension"]:
        out.append(f"  National extension: --{result['national_extension']} (India-specific)")
    for problem in result["problems"]:
        out.append(f"  ! {problem}")
    return "\n".join(out)


def search(term: str, table: dict, limit: int = 25) -> list:
    needle = term.lower()
    hits = [
        row
        for row in table.values()
        if needle in row["description"].lower()
    ]
    hits.sort(key=lambda r: (int(r["level"]), r["hs_code"]))
    return hits[:limit]


def chapter(code: str, table: dict) -> list:
    ch = clean(code)[:2]
    rows = [r for r in table.values() if r["chapter"] == ch and int(r["level"]) <= 4]
    rows.sort(key=lambda r: (len(r["hs_code"]), r["hs_code"]))
    return rows


def source_line() -> str:
    manifest = provenance.read_manifest(DATA_DIR)
    if not manifest:
        return ""
    stale = "  [STALE — re-run fetch_hs.py]" if provenance.is_stale(manifest) else ""
    return (
        f"source: {manifest['source_name']} | {manifest.get('hs_version','')} | "
        f"fetched {manifest['fetched_at']}{stale}"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("code", nargs="?", help="HS or ITC(HS) code, dots optional")
    parser.add_argument("--search", help="find codes whose description contains this text")
    parser.add_argument("--chapter", help="list the headings in a chapter")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args(argv)

    try:
        table = load()
    except NomenclatureMissing as exc:
        print(exc)
        return 2

    if args.search:
        hits = search(args.search, table, args.limit)
        if not hits:
            print(f"no HS description contains {args.search!r}")
            return 1
        print(f"{len(hits)} match(es) for {args.search!r}:")
        for row in hits:
            print(f"  {row['hs_code']:<8} (HS-{row['level']})  {row['description']}")
        print(f"\nNarrow to the 6-digit subheading, then get the Indian 8-digit line "
              f"from ICEGATE.\n{source_line()}")
        return 0

    if args.chapter:
        rows = chapter(args.chapter, table)
        if not rows:
            print(f"chapter {args.chapter} not found")
            return 1
        for row in rows:
            indent = "" if int(row["level"]) == 2 else "  "
            print(f"  {indent}{row['hs_code']:<6} {row['description']}")
        print(f"\n{source_line()}")
        return 0

    if not args.code:
        parser.error("supply a code, --search or --chapter")

    result = validate(args.code, table)
    print(render(result, table))
    print(f"\n{source_line()}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
