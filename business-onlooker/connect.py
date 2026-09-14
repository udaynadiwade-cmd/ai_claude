#!/usr/bin/env python3
"""
Connect Business Onlooker to Shoonya. One command, once, on any machine in
India that stays on at 15:35 — the OpenAlgo box is the obvious one:

    python3 business-onlooker/connect.py

It asks for the five Shoonya API values (secrets typed hidden, saved only to
the gitignored .env beside this file, owner-only permissions), proves the
connection by logging in and pulling today's books, runs and pushes the
first report if there are fills, and schedules daily_report.py for 15:35
IST on weekdays. After that nothing is manual: fills flow
trade.shoonya.com -> this repo -> the dashboard, every close.

Where the values come from (all on Shoonya's side, nothing from OpenAlgo):
    client id, password   your trade.shoonya.com login
    vendor code, API key  Shoonya API page — enable API access (free)
    TOTP secret           the base32 text shown under the QR when you set
                          up TOTP for API login (Shoonya's TOTP setup guide)

Why here and not in the cloud: Shoonya's API answers non-India addresses
with 502 (verified from a US egress, 2026-09-14).

    --openalgo       use OpenAlgo's REST instead (tradebook only)
    --no-schedule    set up and test, but leave cron / Task Scheduler alone
    --no-push        run the first report without committing (testing)
"""

import argparse
import getpass
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
ENV = HERE / ".env"
LOG = HERE / "daily_report.log"
TASK = "BusinessOnlookerDailyReport"
RUN_AT_IST = (15, 35)

sys.path.insert(0, str(HERE))
import daily_report as dr  # noqa: E402


def ask(label, default="", secret=False):
    prompt = f"{label}{f' [{default}]' if default else ''}: "
    val = (getpass.getpass(prompt) if secret else input(prompt)).strip()
    return val or default


def write_env(values):
    """Merge into .env, keeping anything already there. Owner-only perms."""
    lines = ENV.read_text().splitlines() if ENV.exists() else []
    seen, out = set(), []
    for line in lines:
        k = line.split("=", 1)[0].strip() if "=" in line and not line.startswith("#") else None
        if k in values:
            out.append(f"{k}={values[k]}")
            seen.add(k)
        else:
            out.append(line)
    out += [f"{k}={v}" for k, v in values.items() if k not in seen]
    ENV.write_text("\n".join(out) + "\n")
    try:
        os.chmod(ENV, 0o600)
    except OSError:
        pass


def local_run_time():
    """15:35 IST expressed in this machine's clock, for the scheduler."""
    ist = datetime.now(ZoneInfo("Asia/Kolkata")).replace(
        hour=RUN_AT_IST[0], minute=RUN_AT_IST[1], second=0, microsecond=0)
    local = ist.astimezone()
    return local.hour, local.minute, local.tzname()


def schedule():
    h, m, tz = local_run_time()
    py, script = sys.executable, HERE / "daily_report.py"
    if platform.system() == "Windows":
        cmd = ["schtasks", "/Create", "/F", "/TN", TASK, "/SC", "WEEKLY",
               "/D", "MON,TUE,WED,THU,FRI", "/ST", f"{h:02d}:{m:02d}",
               "/TR", f'"{py}" "{script}"']
        r = subprocess.run(cmd, capture_output=True, text=True)
        return (r.returncode == 0,
                f"Task Scheduler '{TASK}' at {h:02d}:{m:02d} {tz}, weekdays"
                if r.returncode == 0 else r.stderr.strip() or r.stdout.strip())
    tag = "# Business Onlooker daily report, 15:35 IST"
    line = f"{m} {h} * * 1-5 cd {REPO} && {py} {script} >> {LOG} 2>&1  {tag}"
    cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = "\n".join(l for l in (cur.stdout if cur.returncode == 0 else "").splitlines()
                         if tag not in l)
    new = existing.rstrip("\n") + ("\n" if existing.strip() else "") + line + "\n"
    r = subprocess.run(["crontab", "-"], input=new, capture_output=True, text=True)
    return (r.returncode == 0,
            f"cron at {h:02d}:{m:02d} {tz} weekdays, log -> {LOG}"
            if r.returncode == 0 else r.stderr.strip())


def dashboard_url():
    url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=REPO,
                         capture_output=True, text=True).stdout.strip()
    br = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO,
                        capture_output=True, text=True).stdout.strip()
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url[len("git@github.com:"):]
    url = url.removesuffix(".git")
    return f"{url}/tree/{br}/business-onlooker/reports" if "github.com" in url else str(HERE / "reports")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--openalgo", action="store_true", help="OpenAlgo REST instead of Shoonya direct")
    ap.add_argument("--no-schedule", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    print("Business Onlooker — connect to Shoonya\n"
          "Values are saved to business-onlooker/.env (gitignored) and nowhere else.\n")
    if args.openalgo:
        values = {
            "OPENALGO_URL": ask("OpenAlgo URL", default="http://127.0.0.1:5000"),
            "OPENALGO_APIKEY": ask("OpenAlgo API key", secret=True),
        }
    else:
        uid = ask("Shoonya client id")
        values = {
            "SHOONYA_USER": uid,
            "SHOONYA_PWD": ask("Shoonya password", secret=True),
            "SHOONYA_TOTP_SECRET": ask("TOTP secret (base32 text under the API 2FA QR)", secret=True),
            "SHOONYA_VENDOR": ask("Vendor code", default=f"{uid}_U"),
            "SHOONYA_APIKEY": ask("API key", secret=True),
        }
    values.setdefault("CAPITAL_PER_STOCK", "10000")
    values.setdefault("FLAT_BY", "15:00")

    print("\nTesting the connection...")
    env = {**dict(os.environ), **values}
    try:
        books = dr.from_openalgo(env) if args.openalgo else dr.from_shoonya(env)
    except SystemExit as e:
        books = None
        print(f"  {e}")
    if books is None:
        sys.exit("\nConnection failed. Nothing saved. Check the values and run again.")
    fills = books.get("tradebook") or []
    orders = books.get("orderbook") or []
    print(f"  Connected. Today: {len(fills)} fill(s)"
          + (f", {len(orders)} order(s)" if not args.openalgo else "") + ".")

    write_env(values)
    print(f"  Saved -> {ENV}")

    if fills:
        print("\nRunning the first report...")
        cmd = [sys.executable, str(HERE / "daily_report.py")] + (["--no-push"] if args.no_push else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-4:])
        print("  " + tail.replace("\n", "\n  "))
        if "Push failed" in r.stdout:
            print("  This machine can't push to GitHub yet — set up git credentials, "
                  "then the 15:35 run will push on its own.")
    else:
        print("\nNo fills yet today; the scheduled run will produce the first report.")

    if args.no_schedule:
        print("\n--no-schedule: not touching the scheduler.")
    else:
        ok, msg = schedule()
        print(f"\n{'Scheduled' if ok else 'Scheduling FAILED'}: {msg}")

    print(f"\nDashboard: {dashboard_url()}\n"
          f"Charts:    {HERE / 'reports' / 'dashboard.html'}\n"
          "Done. Nothing else is manual from here.")


if __name__ == "__main__":
    main()
