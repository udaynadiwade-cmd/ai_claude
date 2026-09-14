#!/usr/bin/env python3
"""catalog.py — fetch one product's landed-cost breakup from Befach.

befach.com puts a Cloudflare Turnstile challenge in front of every page for
non-browser clients, so there is no way to read a product by URL from a script.
This module reads it through whichever authorised channel is configured, in
this order. Configure exactly one.

  1. CATALOG_EXPORT  — path to a JSON export of the catalog (local file, or a
     file synced from Drive). No network, no gate. Simplest to run daily.
  2. CATALOG_API     — base URL of a read-only product endpoint, plus
     CATALOG_API_KEY sent as Authorization: Bearer.
  3. CATALOG_URL + CATALOG_BYPASS_TOKEN — befach.com itself, with a token that
     a Cloudflare WAF skip rule accepts so the request is not challenged.

Usage:
    python3 catalog.py 1601814328302
    python3 catalog.py 1601814328302 --field landed

Exits non-zero with a readable reason if nothing is configured. It never
invents a figure and never tries to defeat the challenge.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ("exw", "duty", "freight", "landed", "currency", "title", "moq")


def load_env():
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _get_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
    except urllib.error.HTTPError as e:
        sys.exit(f"{url} returned {e.code} {e.reason}")
    if "Quick check" in body or "turnstile" in body.lower():
        sys.exit("Blocked by the Turnstile challenge. This channel is not "
                 "exempt yet — add the WAF skip rule for your token, or use "
                 "CATALOG_EXPORT / CATALOG_API instead.")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        sys.exit(f"{url} did not return JSON. First 200 chars:\n{body[:200]}")


def from_export(sku, path):
    data = json.loads(Path(path).read_text())
    items = data if isinstance(data, list) else data.get("products", [])
    for it in items:
        if str(it.get("id") or it.get("sku") or "") == str(sku):
            return it
    sys.exit(f"SKU {sku} not found in {path} ({len(items)} products).")


def from_api(sku, base, key):
    h = {"Accept": "application/json"}
    if key:
        h["Authorization"] = f"Bearer {key}"
    return _get_json(f"{base.rstrip('/')}/{sku}", h)


def from_site(sku, base, token):
    return _get_json(f"{base.rstrip('/')}/api/product/{sku}",
                     {"Accept": "application/json", "X-Befach-Automation": token})


def fetch(sku):
    load_env()
    e = os.environ
    if e.get("CATALOG_EXPORT"):
        return from_export(sku, e["CATALOG_EXPORT"])
    if e.get("CATALOG_API"):
        return from_api(sku, e["CATALOG_API"], e.get("CATALOG_API_KEY"))
    if e.get("CATALOG_URL") and e.get("CATALOG_BYPASS_TOKEN"):
        return from_site(sku, e["CATALOG_URL"], e["CATALOG_BYPASS_TOKEN"])
    sys.exit(
        "No catalog channel configured. befach.com challenges every scripted\n"
        "request with Cloudflare Turnstile, so one of these must be set in\n"
        "linkedin/.env:\n"
        "  CATALOG_EXPORT=/path/to/catalog.json          (simplest)\n"
        "  CATALOG_API=https://.../api/products + CATALOG_API_KEY=...\n"
        "  CATALOG_URL=https://befach.com + CATALOG_BYPASS_TOKEN=...\n"
        "See linkedin/ACCESS.md for how to open each one.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sku")
    ap.add_argument("--field", choices=FIELDS)
    a = ap.parse_args()
    item = fetch(a.sku)
    if a.field:
        v = item.get(a.field)
        if v is None:
            sys.exit(f"Field '{a.field}' missing. Present: {', '.join(sorted(item))}")
        print(v)
    else:
        print(json.dumps(item, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
