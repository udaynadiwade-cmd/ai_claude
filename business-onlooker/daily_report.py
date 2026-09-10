#!/usr/bin/env python3
"""
Pull today's fills, analyse them, commit the report. Runs unattended.

Put this on a scheduler at 15:35 IST on weekdays. It fetches the day's
tradebook, runs analyze_trades.py over it, writes both under
business-onlooker/reports/<date>/ and pushes. Nothing to upload by hand.

Credentials come from a .env beside this file and never leave your machine.
Two sources, tried in order:

  OpenAlgo (preferred — it already holds your Shoonya login):
      OPENALGO_URL=http://127.0.0.1:5000
      OPENALGO_APIKEY=...

  Shoonya direct (fallback):
      SHOONYA_USER=...          # client id
      SHOONYA_PWD=...           # plain password, hashed here
      SHOONYA_TOTP_SECRET=...   # base32 secret from the TOTP setup QR
      SHOONYA_VENDOR=...        # vendor code, usually <userid>_U
      SHOONYA_APIKEY=...        # API secret from Shoonya
"""

import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
SHOONYA = "https://api.shoonya.com/NorenWClientTP"


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


def from_openalgo(env):
    """OpenAlgo already authenticates to Shoonya, so this needs one key."""
    url, key = env.get("OPENALGO_URL"), env.get("OPENALGO_APIKEY")
    if not (url and key):
        return None
    try:
        res = post(f"{url.rstrip('/')}/api/v1/tradebook", {"apikey": key})
    except (urllib.error.URLError, OSError) as e:
        print(f"  OpenAlgo unreachable ({e}) — falling back to Shoonya", file=sys.stderr)
        return None
    if res.get("status") == "error":
        print(f"  OpenAlgo error: {res.get('message')}", file=sys.stderr)
        return None
    return res.get("data", res)


def from_shoonya(env):
    """Direct Noren API. Needs TOTP, so pyotp is required for this path."""
    need = ["SHOONYA_USER", "SHOONYA_PWD", "SHOONYA_TOTP_SECRET",
            "SHOONYA_VENDOR", "SHOONYA_APIKEY"]
    if any(not env.get(k) for k in need):
        sys.exit("No usable credentials. Set OPENALGO_* or all SHOONYA_* in .env")
    try:
        import pyotp
    except ImportError:
        sys.exit("pip install pyotp  (needed for the Shoonya direct path)")

    uid = env["SHOONYA_USER"]
    sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
    payload = {
        "apkversion": "1.0.0", "uid": uid,
        "pwd": sha(env["SHOONYA_PWD"]),
        "factor2": pyotp.TOTP(env["SHOONYA_TOTP_SECRET"]).now(),
        "vc": env["SHOONYA_VENDOR"],
        "appkey": sha(f"{uid}|{env['SHOONYA_APIKEY']}"),
        "imei": env.get("SHOONYA_IMEI", "abc1234"), "source": "API",
    }
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}
    res = post(f"{SHOONYA}/QuickAuth", "jData=" + json.dumps(payload), hdr)
    if res.get("stat") != "Ok":
        sys.exit(f"Shoonya login failed: {res.get('emsg')}")

    token = res["susertoken"]
    tb = post(f"{SHOONYA}/TradeBook",
              f"jData={json.dumps({'uid': uid, 'actid': uid})}&jKey={token}", hdr)
    return tb if isinstance(tb, list) else []


def git(*args):
    return subprocess.run(["git", *args], cwd=HERE.parent,
                          capture_output=True, text=True)


def main():
    env = load_env()
    stamp = datetime.now().strftime("%Y-%m-%d")
    out = REPORTS / stamp
    out.mkdir(parents=True, exist_ok=True)

    print(f"Fetching tradebook for {stamp}...")
    fills = from_openalgo(env)
    if fills is None:
        fills = from_shoonya(env)

    if not fills:
        print("No trades today. Nothing to report.")
        return

    raw = out / "tradebook.json"
    raw.write_text(json.dumps(fills, indent=1))
    print(f"  {len(fills)} fills -> {raw}")

    cmd = [sys.executable, str(HERE / "analyze_trades.py"), str(raw)]
    n500 = HERE / "data" / "nifty500.txt"
    if n500.exists():
        cmd += ["--n500", str(n500)]
    if env.get("CAPITAL_PER_STOCK"):
        cmd += ["--capital", env["CAPITAL_PER_STOCK"]]

    run = subprocess.run(cmd, capture_output=True, text=True)
    report = run.stdout or run.stderr
    (out / "report.txt").write_text(report)
    print(report)

    rel = f"business-onlooker/reports/{stamp}"
    git("add", rel)
    if git("diff", "--cached", "--quiet").returncode:
        git("commit", "-m", f"Trade report {stamp}")
        push = git("push")
        print("Pushed." if push.returncode == 0 else f"Push failed:\n{push.stderr}")
    else:
        print("No change to commit.")


if __name__ == "__main__":
    main()
