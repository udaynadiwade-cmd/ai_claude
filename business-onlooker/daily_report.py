#!/usr/bin/env python3
"""
Pull today's books from Shoonya, analyse them, rebuild the dashboard, commit.
Runs unattended on a machine in India — Shoonya's API answers foreign
addresses with 502, so this cannot run from a cloud session abroad.

    python3 daily_report.py            # today
    python3 daily_report.py --no-push  # dry run, leaves files uncommitted

Backfill a past day (the API only serves today; use the web export from
trade.shoonya.com -> Reports -> Trade Book -> pick the date -> CSV):

    python3 daily_report.py --file ~/Downloads/TradeBook.csv --date 2026-09-11

Source of truth is Shoonya's own API at api.shoonya.com — the same backend
trade.shoonya.com talks to, same login, same data. Three books are pulled
and saved raw under reports/<date>/:

    tradebook.json   every fill                       -> the analysis
    orderbook.json   every order, incl. REJECTED + rejreason
    positions.json   net positions with realised / MTM

Credentials: environment variables first, then a .env beside this file.
connect.py writes that file. Never commit it.

    SHOONYA_USER          client id
    SHOONYA_PWD           plain password, SHA-256'd here before sending
    SHOONYA_TOTP_SECRET   base32 secret from the API TOTP setup QR
    SHOONYA_VENDOR        vendor code, usually <client id>_U
    SHOONYA_APIKEY        API key from the Shoonya API page

Optional:
    CAPITAL_PER_STOCK=10000          SIZE rule
    FLAT_BY=15:00                    WINDOW rule + square-off cutoff
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import shutil
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
SHOONYA_KEYS = ["SHOONYA_USER", "SHOONYA_PWD", "SHOONYA_TOTP_SECRET",
                "SHOONYA_VENDOR", "SHOONYA_APIKEY"]
FORM = {"Content-Type": "application/x-www-form-urlencoded"}


def load_env():
    env = dict(os.environ)
    dotenv = HERE / ".env"
    if dotenv.exists():
        for line in dotenv.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def post(url, data, headers=None):
    body = data.encode() if isinstance(data, str) else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers=headers or {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def totp(secret, digits=6, period=30):
    """RFC 6238 time-based OTP, SHA-1, from a base32 secret. No dependency."""
    key = base64.b32decode(secret.replace(" ", "").upper() + "=" * (-len(secret.strip()) % 8))
    counter = struct.pack(">Q", int(time.time()) // period)
    mac = hmac.new(key, counter, hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    code = (struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF) % 10 ** digits
    return f"{code:0{digits}d}"


# ------------------------------------------------------------------ Shoonya

def shoonya_base(env):
    return env.get("SHOONYA_URL", "https://api.shoonya.com/NorenWClientTP").rstrip("/")


def shoonya_login(env):
    """QuickAuth. Returns (uid, session token). Exits with a plain reason."""
    missing = [k for k in SHOONYA_KEYS if not env.get(k)]
    if missing:
        sys.exit(f"Missing {', '.join(missing)}. Run: python3 connect.py")
    uid = env["SHOONYA_USER"]
    sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
    payload = {
        "apkversion": "1.0.0", "uid": uid,
        "pwd": sha(env["SHOONYA_PWD"]),
        "factor2": totp(env["SHOONYA_TOTP_SECRET"]),
        "vc": env["SHOONYA_VENDOR"],
        "appkey": sha(f"{uid}|{env['SHOONYA_APIKEY']}"),
        "imei": env.get("SHOONYA_IMEI", "abc1234"), "source": "API",
    }
    try:
        res = post(f"{shoonya_base(env)}/QuickAuth", "jData=" + json.dumps(payload), FORM)
    except urllib.error.HTTPError as e:
        sys.exit(f"Shoonya API returned HTTP {e.code} on login. Shoonya refuses "
                 f"non-India addresses — this must run from India.")
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"Shoonya API unreachable: {e}")
    if res.get("stat") != "Ok":
        sys.exit(f"Shoonya login failed: {res.get('emsg')}")
    return uid, res["susertoken"]


def noren(env, path, uid, token, **extra):
    """One authenticated Noren call. Empty books come back as Not_Ok -> []."""
    body = f"jData={json.dumps({'uid': uid, **extra})}&jKey={token}"
    res = post(f"{shoonya_base(env)}/{path}", body, FORM)
    return res if isinstance(res, list) else []


def from_shoonya(env):
    """All three books. Fill rows carry flqty/flprc/fltm for THIS fill."""
    uid, token = shoonya_login(env)
    return {
        "tradebook": noren(env, "TradeBook", uid, token, actid=uid),
        "orderbook": noren(env, "OrderBook", uid, token),
        "positions": noren(env, "PositionBook", uid, token, actid=uid),
    }


# --------------------------------------------------------------------- main

def git(*args):
    return subprocess.run(["git", *args], cwd=HERE.parent, capture_output=True, text=True)


def run_py(script, *args):
    r = subprocess.run([sys.executable, str(HERE / script), *args],
                       capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-push", action="store_true", help="write files, skip git")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                    help="folder name; the API only serves today's books")
    ap.add_argument("--file", help="ingest an exported Trade Book (CSV/JSON) "
                    "instead of fetching — backfill, pair with --date")
    args = ap.parse_args()

    env = load_env()
    out = REPORTS / args.date
    out.mkdir(parents=True, exist_ok=True)

    if args.file:
        src = Path(args.file).expanduser()
        ext = src.suffix.lower() if src.suffix.lower() in (".csv", ".json") else ".csv"
        raw = out / f"tradebook{ext}"
        shutil.copy(src, raw)
        print(f"Backfilling {args.date} from {src} -> {raw}")
        have_fills = True
    else:
        print(f"Fetching Shoonya books for {args.date}...")
        books = from_shoonya(env)
        for name, rows in books.items():
            if rows:
                (out / f"{name}.json").write_text(json.dumps(rows, indent=1))
                print(f"  {name:<10} {len(rows):>4} rows")
        raw = out / "tradebook.json"
        have_fills = bool(books.get("tradebook"))
        rejected = [o for o in books.get("orderbook", []) if o.get("status") == "REJECTED"]
        if not have_fills:
            print("No fills today." + (f" {len(rejected)} rejected order(s) saved." if rejected else ""))
            if not rejected:
                return

    common = []
    n500 = HERE / "data" / "nifty500.txt"
    if n500.exists():
        common += ["--n500", str(n500)]
    if env.get("CAPITAL_PER_STOCK"):
        common += ["--capital", env["CAPITAL_PER_STOCK"]]
    if env.get("FLAT_BY"):
        common += ["--flat-by", env["FLAT_BY"]]

    if have_fills:
        report = run_py("analyze_trades.py", str(raw), *common)
        (out / "report.txt").write_text(report + "\n")
        print(report)
        dash = common + (["--squareoff-after", env["FLAT_BY"]] if env.get("FLAT_BY") else [])
        print(run_py("dashboard.py", "--reports", str(REPORTS), *dash))

    if args.no_push:
        print("--no-push: files written, nothing committed.")
        return

    rel = "business-onlooker/reports"
    git("add", f"{rel}/{args.date}", f"{rel}/dashboard.html", f"{rel}/README.md")
    if not git("diff", "--cached", "--quiet").returncode:
        print("No change to commit.")
        return
    git("commit", "-m", f"Trade report {args.date}")
    push = git("push")
    if push.returncode and "rejected" in push.stderr:      # someone else pushed
        git("pull", "--rebase")
        push = git("push")
    print("Pushed." if push.returncode == 0 else f"Push failed:\n{push.stderr}")


if __name__ == "__main__":
    main()
