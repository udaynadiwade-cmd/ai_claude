#!/usr/bin/env python3
"""Pull live rate data from the primary sources into data/rates/.

Subcommands:
    status              probe every registered source and report reachability
    fx                  CBIC notified customs exchange rates (ERAM)
    tariff --hsn CODE   duty heads for one 8-digit ITC(HS) line, from ICEGATE
    freight             Drewry World Container Index composite

Design rule: **a value that could not be fetched is never written.** If a source
is unreachable the command exits non-zero, says which host failed and why, and
leaves the previous data (and its manifest date) untouched. Downstream, an
absent rate makes landed_cost.py demand the number explicitly rather than
substitute a guess.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import provenance  # noqa: E402
from net import EgressBlocked, Fetcher, FetchError, browser_get  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RATES_DIR = os.path.normpath(os.path.join(HERE, "..", "data", "rates"))
SOURCES_PATH = os.path.join(HERE, "sources.json")

DUTY_HEAD_PATTERNS = [
    ("bcd", r"basic\s*(customs)?\s*duty|^bcd\b"),
    ("sws", r"social\s*welfare|^sws\b"),
    ("aidc", r"agriculture\s*infrastructure|^aidc\b"),
    ("igst", r"^igst\b|integrated\s*gst|integrated\s*goods"),
    ("comp_cess", r"compensation\s*cess"),
    ("add", r"anti[-\s]?dumping"),
    ("safeguard", r"safeguard"),
    ("health_cess", r"health\s*cess"),
]


def sources() -> dict:
    with open(SOURCES_PATH, encoding="utf-8") as fh:
        return json.load(fh)["sources"]


def soup(html: str):
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("beautifulsoup4 not installed: pip install -r requirements.txt") from exc
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:  # lxml absent
        return BeautifulSoup(html, "html.parser")


def to_number(text: str):
    """Pull a numeric value out of '10%', 'Rs. 84.50', '18.00 %'. None if absent."""
    if text is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(text).replace(",", ""))
    return float(m.group()) if m else None


def label_value_pairs(html: str) -> dict:
    """Collect every two-column (label, value) pair in every table on the page.

    Government portals reshuffle their markup often, so this keys on the visible
    label text rather than on a brittle CSS path.
    """
    pairs = {}
    for table in soup(html).find_all("table"):
        for row in table.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
            if len(cells) >= 2 and cells[0]:
                pairs.setdefault(cells[0], cells[1])
    return pairs


def map_duty_heads(pairs: dict) -> tuple[dict, list]:
    """Map scraped labels onto our duty-head keys. Unmatched labels are returned."""
    found, unmatched = {}, []
    for label, value in pairs.items():
        key = next(
            (k for k, pat in DUTY_HEAD_PATTERNS if re.search(pat, label, re.I)), None
        )
        if key is None:
            unmatched.append(label)
        elif key not in found:
            found[key] = {"rate": to_number(value), "label": label, "raw": value}
    return found, unmatched


# ---------------------------------------------------------------- status ----

def probe(fetcher: Fetcher, url: str) -> tuple[str, str]:
    try:
        r = fetcher.get(url, allow_redirects=True)
        return "REACHABLE", f"HTTP {r.status} in {r.elapsed_s}s, {len(r.content)} bytes"
    except EgressBlocked as exc:
        return "BLOCKED", exc.detail
    except FetchError as exc:
        return "ERROR", exc.detail


def cmd_status(args) -> int:
    fetcher = Fetcher(retries=1, timeout=20, min_interval_s=0.2)
    reg = sources()
    print("SOURCE REACHABILITY")
    print("=" * 78)
    blocked = 0
    for key, src in reg.items():
        state, detail = probe(fetcher, src["url"])
        if state != "REACHABLE":
            blocked += 1
        print(f"{state:<10} {key:<26} {src['url']}")
        print(f"{'':<10} {detail}")
    print()

    print("LOCAL DATASETS")
    print("=" * 78)
    for directory in sorted(
        d for d in (
            os.path.normpath(os.path.join(HERE, "..", "data", x))
            for x in os.listdir(os.path.normpath(os.path.join(HERE, "..", "data")))
        )
        if os.path.isdir(d)
    ):
        manifest = provenance.read_manifest(directory)
        name = os.path.basename(directory)
        if manifest is None:
            print(f"EMPTY      {name}: not fetched")
            continue
        ok, problems = provenance.verify(directory)
        print(f"{'OK' if ok else 'PROBLEM':<10} {provenance.describe(manifest)}")
        for problem in problems:
            print(f"{'':<10} ! {problem}")
    if blocked:
        print(
            f"\n{blocked} source(s) unreachable from this network. Rates from those sources "
            "are NOT available and must not be assumed."
        )
    return 1 if blocked else 0


# -------------------------------------------------------------------- fx ----

def cmd_fx(args) -> int:
    src = sources()["cbic_exchange_rate"]
    fetcher = Fetcher()
    print(f"GET {src['url']}")
    try:
        page = fetcher.get(src["url"])
    except EgressBlocked as exc:
        print(f"EGRESS BLOCKED: {exc.detail}\n  {exc.url}\n  Nothing written.")
        return 2
    except FetchError as exc:
        print(f"FETCH FAILED: {exc}\n  Nothing written.")
        return 2

    doc = soup(page.text)
    links = []
    for a in doc.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        if re.search(r"exchange\s*rate|notification", text, re.I):
            href = a["href"]
            if href.startswith("/"):
                href = "https://www.cbic.gov.in" + href
            links.append({"text": text, "url": href})

    rates = {}
    for label, value in label_value_pairs(page.text).items():
        if re.fullmatch(r"[A-Za-z .()]+", label) and to_number(value) is not None:
            rates[label.strip()] = to_number(value)

    if not links and not rates:
        print(
            "REFUSED: the page returned no notification links and no rate table.\n"
            "  The page layout has changed, or the response was a login/JS shell.\n"
            f"  Re-run with --dump to inspect: nothing written."
        )
        if args.dump:
            path = os.path.join(RATES_DIR, "cbic_fx_raw.html")
            os.makedirs(RATES_DIR, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(page.text)
            print(f"  raw HTML saved to {path}")
        return 3

    out_dir = os.path.join(RATES_DIR, "fx")
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        "retrieved_from": src["url"],
        "notification_links": links[:20],
        "rates_seen_on_page": rates,
        "caveat": (
            "Use the rate in force on the Bill of Entry date. Under ERAM, rates are revised "
            "on the 1st and/or 3rd Thursday and take effect the following Friday. Confirm the "
            "notification number and effective date before using any figure here."
        ),
    }
    with open(os.path.join(out_dir, "cbic_fx.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    provenance.write_manifest(
        out_dir, "cbic_exchange_rate", src["publisher"], src["url"],
        ["cbic_fx.json"], src["max_age_days"], notes=src.get("notes", ""),
    )
    print(f"wrote {len(rates)} rate rows and {len(links)} notification links to {out_dir}")
    return 0


# ---------------------------------------------------------------- tariff ----

def cmd_tariff(args) -> int:
    reg = sources()
    src = reg["icegate_duty_calculator"]
    hsn = re.sub(r"[^0-9]", "", args.hsn)
    if len(hsn) != 8:
        print(f"REFUSED: '{args.hsn}' is not an 8-digit ITC(HS) line. Duty differs between "
              "extensions of the same HS-6, so a 6-digit lookup is not a rate.")
        return 4

    legacy = f"{src['legacy_url']}?CCode={hsn}"
    html = None
    errors = []
    for label, getter in (
        ("legacy trade guide", lambda: Fetcher().get(legacy).text),
        ("icegate CDC (browser)", lambda: browser_get(
            src["url"], wait_selector="table", timeout_ms=args.timeout * 1000)),
    ):
        print(f"try: {label}")
        try:
            html = getter()
            break
        except (EgressBlocked, FetchError) as exc:
            errors.append(f"{label}: {exc.detail}")
            print(f"  failed: {exc.detail}")
        except RuntimeError as exc:
            errors.append(f"{label}: {exc}")
            print(f"  failed: {exc}")

    if html is None:
        print("\nNo route to ICEGATE. Duty rates NOT retrieved; nothing written.")
        for err in errors:
            print(f"  - {err}")
        print("\n  Get the rates manually from https://www.icegate.gov.in/cdc and pass them to "
              "landed_cost.py explicitly, recording the notification number.")
        return 2

    if args.dump:
        os.makedirs(RATES_DIR, exist_ok=True)
        path = os.path.join(RATES_DIR, f"icegate_{hsn}_raw.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"raw HTML saved to {path}")

    pairs = label_value_pairs(html)
    heads, unmatched = map_duty_heads(pairs)
    if not heads:
        print(
            "REFUSED: reached the page but found no recognisable duty heads.\n"
            "  The layout changed, or the code returned no result. Nothing written.\n"
            f"  Labels seen: {unmatched[:15]}"
        )
        return 3

    out_dir = os.path.join(RATES_DIR, "tariff")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{hsn}.json")
    payload = {
        "hsn": hsn,
        "retrieved_from": src["url"],
        "retrieved_at": provenance.now_iso(),
        "duty_heads": heads,
        "unmatched_labels": unmatched[:40],
        "caveat": (
            "Effective rates depend on exemption notifications, end-use conditions and origin. "
            "Confirm against the operative notification before filing."
        ),
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    provenance.write_manifest(
        out_dir, "icegate_tariff", src["publisher"], src["url"],
        [os.path.basename(path)], src["max_age_days"], notes=src.get("notes", ""),
    )
    print(f"\nwrote {path}")
    for key, head in sorted(heads.items()):
        print(f"  {key:<12} {head['rate']}  ({head['label']})")
    return 0


# --------------------------------------------------------------- freight ----

def cmd_freight(args) -> int:
    src = sources()["drewry_wci"]
    print(f"GET {src['url']}")
    try:
        html = Fetcher().get(src["url"]).text
    except EgressBlocked as exc:
        print(f"EGRESS BLOCKED: {exc.detail}\n  {exc.url}\n  Nothing written.")
        return 2
    except FetchError as exc:
        print(f"FETCH FAILED: {exc}\n  Nothing written.")
        return 2

    text = soup(html).get_text(" ", strip=True)
    composite = None
    m = re.search(r"composite index[^$]{0,80}\$\s?([\d,]+)", text, re.I)
    if m:
        composite = to_number(m.group(1))
    week = None
    m = re.search(r"(\d{1,2}\s+[A-Z][a-z]{2,8}\s+20\d\d)", text)
    if m:
        week = m.group(1)

    if composite is None:
        print("REFUSED: could not locate the composite index value on the page. Nothing written.")
        return 3

    out_dir = os.path.join(RATES_DIR, "freight")
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        "index": "Drewry World Container Index composite",
        "unit": "USD per 40ft container",
        "value": composite,
        "as_of_text": week,
        "retrieved_at": provenance.now_iso(),
        "caveat": src.get("notes", ""),
    }
    with open(os.path.join(out_dir, "wci.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    provenance.write_manifest(
        out_dir, "drewry_wci", src["publisher"], src["url"],
        ["wci.json"], src["max_age_days"], notes=src.get("notes", ""),
    )
    print(f"WCI composite: USD {composite:,.0f} per 40ft ({week or 'date not parsed'})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dump", action="store_true", help="save raw HTML for inspection")
    parser.add_argument("--timeout", type=int, default=45)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="probe sources and report local dataset state")
    sub.add_parser("fx", help="CBIC notified exchange rates")
    t = sub.add_parser("tariff", help="duty heads for one ITC(HS) line")
    t.add_argument("--hsn", required=True)
    sub.add_parser("freight", help="Drewry WCI composite")

    args = parser.parse_args(argv)
    return {
        "status": cmd_status,
        "fx": cmd_fx,
        "tariff": cmd_tariff,
        "freight": cmd_freight,
    }[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
