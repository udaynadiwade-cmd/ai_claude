#!/usr/bin/env python3
"""
Screen today's Nifty 500 movers and print a MANDATORY search list.

    python3 screen.py            # live
    python3 screen.py --top 15

Exists because the standing rule in AGENT.md ("never assert no-news without
searching") kept being applied selectively. On 2026-09-09 ADANIENT was logged
twice as "no catalyst" without a search; the cause was a Rs 9,825 cr airport
stake sale. On 2026-09-10 the same thing happened to ATHERENERG - a +2.15%
gap sat in the screen output and went unsearched while IRB, with a bigger
gap, got looked up. Both times the rule existed and judgment overrode it.

So the trigger is no longer a judgment call. Any name tripping a threshold
lands in SEARCH LIST, and that list is worked top to bottom before any call
is written. No exceptions for price, for size, or for "it doesn't fit the
theme" - those are exactly the reasons the last two were missed.
"""

import argparse
import gzip
import http.cookiejar
import json
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
N500 = HERE / "data" / "nifty500.txt"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# Thresholds. Any ONE of these makes a search mandatory.
GAP_PCT = 1.0            # overnight information shows up in the gap
AT_EXTREME_PCT = 0.5     # LTP within this of the session high/low
TURNOVER_CR = 100.0      # real money, whatever the percentage


def session():
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    for url in ("https://www.nseindia.com/",
                "https://www.nseindia.com/market-data/top-gainers-losers"):
        read(op, url, "text/html,*/*;q=0.8")
    return op


def read(op, url, accept="*/*"):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": accept, "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.nseindia.com/market-data/top-gainers-losers"})
    try:
        body = op.open(req, timeout=30).read()
    except urllib.error.HTTPError as e:
        body = e.read()
    return gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body


def why_flagged(r):
    """Return the reasons this name must be searched. Empty means skip."""
    reasons = []
    gap = (r["open_price"] - r["prev_price"]) / r["prev_price"] * 100 if r["prev_price"] else 0
    if abs(gap) > GAP_PCT:
        reasons.append(f"gap {gap:+.2f}%")
    hi, lo, ltp = r["high_price"], r["low_price"], r["ltp"]
    if hi and (hi - ltp) / hi * 100 <= AT_EXTREME_PCT:
        reasons.append("at HIGH")
    if lo and (ltp - lo) / lo * 100 <= AT_EXTREME_PCT:
        reasons.append("at LOW")
    if r.get("turnover", 0) / 100 > TURNOVER_CR:   # NSE reports in lakhs
        reasons.append(f"Rs {r['turnover'] / 100:,.0f} cr")
    return reasons, gap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    universe = {s.strip().upper() for s in N500.read_text().split()} if N500.exists() else set()
    op = session()
    flagged = []

    for side, key in (("GAINERS", "gainers"), ("LOSERS", "loosers")):
        blob = json.loads(read(op, f"https://www.nseindia.com/api/live-analysis-variations?index={key}"))
        seen = {}
        for sec in ("allSec", "FOSec", "NIFTY"):
            for r in blob.get(sec, {}).get("data", []):
                if not universe or r["symbol"] in universe:
                    seen.setdefault(r["symbol"], r)
        rows = sorted(seen.values(), key=lambda r: -abs(r["perChange"]))[:args.top]

        print(f"\n=== {side} — Nifty 500 | {blob.get('allSec', {}).get('timestamp', '?')} ===")
        print(f"{'SYMBOL':<13}{'%CHG':>7}{'GAP%':>7}{'LTP':>10}{'HIGH':>10}{'LOW':>10}")
        for r in rows:
            reasons, gap = why_flagged(r)
            print(f"{r['symbol']:<13}{r['perChange']:>7.2f}{gap:>7.2f}"
                  f"{r['ltp']:>10.1f}{r['high_price']:>10.1f}{r['low_price']:>10.1f}"
                  f"{'   <<<' if reasons else ''}")
            if reasons:
                flagged.append((r["symbol"], r["perChange"], reasons))

    print(f"\n{'=' * 60}\n  SEARCH LIST — {len(flagged)} names. Work every one.\n{'=' * 60}")
    for sym, chg, reasons in sorted(flagged, key=lambda x: -abs(x[1])):
        print(f"  [ ] {sym:<13}{chg:>7.2f}%   {', '.join(reasons)}")
    print("\n  No call gets written until each box above is ticked.")
    print("  Price and position size are NOT reasons to skip one.\n")


if __name__ == "__main__":
    main()
