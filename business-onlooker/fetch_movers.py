#!/usr/bin/env python3
"""
Pull NSE top gainers/losers and dump them where Business Onlooker can read them.

Run this on YOUR machine (the one with NSE access), not in a Claude session —
Claude Code's sandbox blocks nseindia.com at the network-policy level.

    python3 fetch_movers.py            # today, F&O + all securities
    python3 fetch_movers.py --commit   # also git-commit the output

Then push. Claude reads the committed CSV/JSON straight from the repo.

Why this exists: NSE fronts its API with Cloudflare and refuses any request
that has not first picked up cookies from the homepage. A bare requests.get()
on the API endpoint returns 401. The handshake below is the whole trick.
"""

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import gzip
import http.cookiejar
import urllib.error
import urllib.request

DATA_DIR = Path(__file__).parent / "data"

# NSE spells it "loosers". Not a typo on our side.
ENDPOINT = "https://www.nseindia.com/api/live-analysis-variations?index={}"

# Sections NSE returns inside each response. FOSec = F&O securities (what the
# manual CSV download gives you); allSec = full cash market, where the real
# 10-20% movers live.
SECTIONS = ["FOSec", "allSec", "NIFTY"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.nseindia.com/market-data/top-gainers-losers",
}

COLUMNS = ["symbol", "open_price", "high_price", "low_price",
           "prev_price", "ltp", "perChange", "trade_quantity", "turnover"]


def nse_session():
    """Cookie handshake. Homepage first, then the market-data page, then API.

    NSE answers the first hit with 403 but still sets the cookies the API
    needs, so the HTTPError body is read and discarded rather than raised.
    HTTP/2 gets reset by Cloudflare; urllib speaks HTTP/1.1, which passes.
    """
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    for url in ("https://www.nseindia.com/",
                "https://www.nseindia.com/market-data/top-gainers-losers"):
        _read(opener, url, "text/html,application/xhtml+xml,*/*;q=0.8")
    return opener


def _read(opener, url, accept):
    req = urllib.request.Request(url, headers={**HEADERS, "Accept": accept})
    try:
        body = opener.open(req, timeout=30).read()
    except urllib.error.HTTPError as e:
        body = e.read()
    return gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body


def fetch(session, index):
    return json.loads(_read(session, ENDPOINT.format(index), "*/*"))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="git add + commit the output")
    args = ap.parse_args()

    stamp = datetime.now().strftime("%Y-%m-%d")
    out = DATA_DIR / stamp
    session = nse_session()

    written = []
    for direction in ("gainers", "loosers"):
        payload = fetch(session, direction)
        label = "losers" if direction == "loosers" else "gainers"

        # Keep the raw JSON — every section, so nothing is lost to our parsing.
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{label}_raw.json").write_text(json.dumps(payload, indent=2))

        for section in SECTIONS:
            rows = payload.get(section, {}).get("data", [])
            if not rows:
                continue
            n = write_csv(out / f"{label}_{section}.csv", rows)
            written.append(f"{label}/{section}: {n}")

    print(f"Wrote {out}")
    for line in written:
        print(f"  {line}")

    if args.commit:
        subprocess.run(["git", "add", str(out)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Market movers {stamp}"], check=True
        )
        print("Committed. Push, then tell Claude the date.")


if __name__ == "__main__":
    main()
