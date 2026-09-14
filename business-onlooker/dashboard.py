#!/usr/bin/env python3
"""
Render every day's tradebook under reports/ into one dashboard.

    python3 dashboard.py                   # reads reports/*/tradebook.json
    python3 dashboard.py --reports DIR     # another folder (tests)

Writes two files, both self-contained - no libraries, no network:

  reports/dashboard.html   charts + tables; open in any browser
  reports/README.md        the same numbers as Markdown, so GitHub renders
                           it at the reports/ folder URL on any device

daily_report.py runs this after each day's fetch, so the dashboard is always
current to the last close and never hand-fed. Every number comes from the
functions in analyze_trades.py - same pairing, same Shoonya charges - so the
dashboard and the text report cannot disagree.

What it answers, per day and across days:
  - net, win rate, profit factor, expectancy, realised R:R
  - BEFORE-12 vs AFTER-12 by ENTRY time (the desk runs two strategies)
  - LONG vs SHORT
  - exits that fired on SIGNAL vs the timer SQUARE-OFF (an exit after the
    cutoff, or one sharing a second with 2+ other exits, is the timer)
  - concentration: how much of the day's profit one trade carried
  - every rule breach from CONTEXT.md
"""

import argparse
import html
import sys
from collections import Counter
from datetime import datetime, time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import analyze_trades as at  # noqa: E402

NOON = time(12, 0)
SESSIONS = ("BEFORE 12", "AFTER 12")
DIRS = ("LONG", "SHORT")
EXITS = ("SIGNAL", "SQUARE-OFF")


# ----------------------------------------------------------------- numbers

def load_day(folder, args, universe):
    fills = at.load(folder / "tradebook.json")
    trades, open_legs = at.pair_trades(fills)
    trades = at.merge_partials(trades)
    if not trades:
        return None
    at.price_trades(trades, args.brokerage)
    cutoff = datetime.strptime(args.squareoff_after, "%H:%M").time()

    # Exits from 3+ symbols in the same second are the timer, not the logic.
    batch = Counter(et for _, et in {(t["symbol"], t["exit_time"])
                                     for t in trades if t["exit_time"]})
    for t in trades:
        et = t["exit_time"]
        t["exit_mode"] = ("SQUARE-OFF" if et and (et.time() >= cutoff or batch[et] >= 3)
                          else "SIGNAL")
        t["session"] = ("BEFORE 12" if t["entry_time"] and t["entry_time"].time() < NOON
                        else "AFTER 12")

    s = at.summarise(trades)
    best = max(trades, key=lambda t: t["net"])
    share = (best["net"] / s["gross_profit"] * 100
             if best["net"] > 0 and s["gross_profit"] else 0.0)
    return {
        "date": folder.name, "fills": len(fills), "trades": trades, "stats": s,
        "breaches": at.rule_check(trades, open_legs, s, args.capital, universe, args.flat_by),
        "by_session": {k: at.summarise([t for t in trades if t["session"] == k]) for k in SESSIONS},
        "by_dir": {k: at.summarise([t for t in trades if t["direction"] == k]) for k in DIRS},
        "by_exit": {k: at.summarise([t for t in trades if t["exit_mode"] == k]) for k in EXITS},
        "best": best, "best_share": share, "net_ex_best": s["net"] - max(best["net"], 0),
    }


def rs(x, sign=True):
    if x is None:
        return "—"
    if abs(x) < 0.5:                      # never print "-₹0"
        return "₹0"
    return ("-" if x < 0 else "+" if sign and x > 0 else "") + f"₹{abs(x):,.0f}"


def pct(x):
    return "—" if x is None else f"{x:.0f}%"


def ratio(x):
    return "—" if x is None else f"{x:.2f}"


def hhmm(dt):
    return dt.strftime("%H:%M") if dt else "—"


def split_rows(groups):
    """Rows for any of the BEFORE/AFTER, LONG/SHORT, SIGNAL/SQUARE-OFF tables."""
    return [[k, g["n"], pct(g["win_rate"]) if g["n"] else "—", rs(g["net"]),
             rs(g["avg_win"], False), rs(-g["avg_loss"]) if g["avg_loss"] else "—",
             ratio(g["pf"])] for k, g in groups.items()]


SPLIT_HEAD = ["", "Trades", "Win %", "Net", "Avg win", "Avg loss", "PF"]
TRADE_HEAD = ["Symbol", "Dir", "Session", "Qty", "Entry", "Exit", "In", "Out",
              "Hold", "Exit mode", "Net"]


def trade_rows(trades):
    return [[t["symbol"], t["direction"], t["session"], t["qty"],
             f"{t['entry']:.2f}", f"{t['exit']:.2f}", hhmm(t["entry_time"]),
             hhmm(t["exit_time"]),
             f"{t['hold_min']:.0f}m" if t["hold_min"] is not None else "—",
             t["exit_mode"], rs(t["net"])]
            for t in sorted(trades, key=lambda t: t["net"])]


def headline_rows(d):
    s = d["stats"]
    return [["Trades", f"{s['n']} ({d['fills']} fills)"],
            ["Win rate", f"{s['wins']}/{s['n']} = {pct(s['win_rate'])}"],
            ["Gross", rs(s["gross"])], ["Costs", rs(-s["cost"])],
            ["NET", rs(s["net"])],
            ["Avg win / avg loss", f"{rs(s['avg_win'], False)} / {rs(-s['avg_loss'])}"],
            ["Realised R:R", f"{ratio(s['rr'])}:1" if s["rr"] is not None else "—"],
            ["Profit factor", ratio(s["pf"])],
            ["Expectancy / trade", rs(s["expectancy"])],
            ["Hold — winners / losers",
             f"{s['win_hold']:.0f}m / {s['loss_hold']:.0f}m"
             if s["win_hold"] is not None and s["loss_hold"] is not None else "—"]]


HIST_HEAD = ["Date", "Trades", "Win %", "Net", "PF", "Before 12", "After 12",
             "Square-offs", "Breaches"]


def history_rows(days):
    return [[d["date"], d["stats"]["n"], pct(d["stats"]["win_rate"]),
             rs(d["stats"]["net"]), ratio(d["stats"]["pf"]),
             rs(d["by_session"]["BEFORE 12"]["net"]),
             rs(d["by_session"]["AFTER 12"]["net"]),
             f"{d['by_exit']['SQUARE-OFF']['n']}/{d['stats']['n']}",
             len(d["breaches"])] for d in days]


def concentration_line(d):
    b = d["best"]
    if b["net"] <= 0:
        return "No winning trade to concentrate in."
    return (f"{b['symbol']} carried {d['best_share']:.0f}% of gross profit "
            f"({rs(b['net'])}). Net without it: {rs(d['net_ex_best'])}.")


# --------------------------------------------------------------------- svg

def svg_equity(trades, w=720, h=230):
    """Cumulative net through the day, by exit time."""
    pts = sorted((t for t in trades if t["exit_time"]), key=lambda t: t["exit_time"])
    if not pts:
        return ""
    xs = [t["exit_time"].hour * 60 + t["exit_time"].minute + t["exit_time"].second / 60
          for t in pts]
    ys, cum = [], 0.0
    for t in pts:
        cum += t["net"]
        ys.append(cum)
    x0, x1 = 9 * 60 + 15, 15 * 60 + 30
    lo, hi = min(0.0, min(ys)), max(0.0, max(ys))
    if hi == lo:
        hi = lo + 1
    pl, pr, pt, pb = 60, 14, 14, 28

    def X(m):
        return pl + (min(max(m, x0), x1) - x0) / (x1 - x0) * (w - pl - pr)

    def Y(v):
        return pt + (hi - v) / (hi - lo) * (h - pt - pb)

    line = f"M{X(x0):.1f},{Y(0):.1f} " + " ".join(
        f"L{X(x):.1f},{Y(y):.1f}" for x, y in zip(xs, ys))
    dots = "".join(
        f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.5" class="{"up" if t["net"] > 0 else "dn"}">'
        f'<title>{html.escape(t["symbol"])} {rs(t["net"])} @ {hhmm(t["exit_time"])}</title></circle>'
        for x, y, t in zip(xs, ys, pts))
    ticks = "".join(f'<text x="{X(hm * 60):.0f}" y="{h - 8}" class="tk" text-anchor="middle">{hm:02d}:00</text>'
                    for hm in range(10, 16))
    return f"""<svg viewBox="0 0 {w} {h}" class="chart" role="img" aria-label="Intraday equity curve">
<line x1="{pl}" y1="{Y(0):.1f}" x2="{w - pr}" y2="{Y(0):.1f}" class="zero"/>
<line x1="{X(720):.1f}" y1="{pt}" x2="{X(720):.1f}" y2="{h - pb}" class="noon"/>
<text x="{X(720) + 4:.0f}" y="{pt + 10}" class="tk">12:00</text>
<text x="{pl - 6}" y="{Y(hi) + 4:.0f}" class="tk" text-anchor="end">{rs(hi)}</text>
<text x="{pl - 6}" y="{Y(0) + 4:.0f}" class="tk" text-anchor="end">0</text>
<text x="{pl - 6}" y="{Y(lo) + 4:.0f}" class="tk" text-anchor="end">{rs(lo)}</text>
<path d="{line}" class="eq"/>{dots}{ticks}</svg>"""


def svg_history(days, w=720, h=230):
    """One bar per day (net), line = running total."""
    if not days:
        return ""
    nets = [d["stats"]["net"] for d in days]
    cum, run = 0.0, []
    for n in nets:
        cum += n
        run.append(cum)
    lo, hi = min(0.0, min(nets + run)), max(0.0, max(nets + run))
    if hi == lo:
        hi = lo + 1
    pl, pr, pt, pb = 60, 14, 14, 28
    n = len(days)
    slot = (w - pl - pr) / n
    bw = max(4.0, min(36.0, slot * 0.55))

    def X(i):
        return pl + slot * (i + 0.5)

    def Y(v):
        return pt + (hi - v) / (hi - lo) * (h - pt - pb)

    bars = "".join(
        f'<rect x="{X(i) - bw / 2:.1f}" y="{min(Y(v), Y(0)):.1f}" width="{bw:.1f}" '
        f'height="{abs(Y(v) - Y(0)):.1f}" class="{"up" if v > 0 else "dn"}">'
        f'<title>{d["date"]} {rs(v)}</title></rect>'
        for i, (d, v) in enumerate(zip(days, nets)))
    line = "M" + " L".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(run))
    step = max(1, n // 8)
    ticks = "".join(
        f'<text x="{X(i):.0f}" y="{h - 8}" class="tk" text-anchor="middle">{d["date"][5:]}</text>'
        for i, d in enumerate(days) if i % step == 0 or i == n - 1)
    return f"""<svg viewBox="0 0 {w} {h}" class="chart" role="img" aria-label="Daily net and running total">
<line x1="{pl}" y1="{Y(0):.1f}" x2="{w - pr}" y2="{Y(0):.1f}" class="zero"/>
<text x="{pl - 6}" y="{Y(hi) + 4:.0f}" class="tk" text-anchor="end">{rs(hi)}</text>
<text x="{pl - 6}" y="{Y(0) + 4:.0f}" class="tk" text-anchor="end">0</text>
<text x="{pl - 6}" y="{Y(lo) + 4:.0f}" class="tk" text-anchor="end">{rs(lo)}</text>
{bars}<path d="{line}" class="run"/>{ticks}</svg>"""


# -------------------------------------------------------------------- html

CSS = """
:root{--bg:#f4f5f7;--card:#fff;--ink:#181b21;--mute:#6b7280;--line:#e3e6eb;
      --up:#0f8a4b;--dn:#c8322b;--acc:#2456d6;--soft:#eef1f6}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--card:#171a21;--ink:#e7e9ee;
      --mute:#98a1b1;--line:#2a2f3a;--up:#3ec27a;--dn:#ff6b61;--acc:#7aa2ff;--soft:#1f2430}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:14px/1.45 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
     padding:20px 16px 48px}
main{max-width:1100px;margin:0 auto}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:15px;margin:0 0 10px;color:var(--mute);font-weight:600;
   text-transform:uppercase;letter-spacing:.04em}
.sub{color:var(--mute);margin:0 0 18px}
.hero{display:flex;flex-wrap:wrap;gap:12px;align-items:baseline;margin-bottom:18px}
.hero .net{font-size:40px;font-weight:700;line-height:1}
.up{color:var(--up)} .dn{color:var(--dn)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi .l{color:var(--mute);font-size:12px} .kpi .v{font-size:20px;font-weight:600;margin-top:2px}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin-bottom:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.chart{width:100%;height:auto;display:block}
.chart .zero{stroke:var(--mute);stroke-width:1;stroke-dasharray:3 3}
.chart .noon{stroke:var(--acc);stroke-width:1;stroke-dasharray:2 4}
.chart .eq{fill:none;stroke:var(--acc);stroke-width:2}
.chart .run{fill:none;stroke:var(--ink);stroke-width:1.5}
.chart .tk{fill:var(--mute);font-size:13px}
.chart circle.up,.chart rect.up{fill:var(--up)} .chart circle.dn,.chart rect.dn{fill:var(--dn)}
.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);white-space:nowrap}
th{text-align:left;color:var(--mute);font-weight:600;font-size:12px}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
tr:last-child td{border-bottom:0}
.breach{background:var(--soft);border-left:3px solid var(--dn);padding:8px 12px;border-radius:6px;margin:6px 0}
.clean{color:var(--up)}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 16px;margin-bottom:10px}
summary{cursor:pointer;font-weight:600;display:flex;gap:14px;flex-wrap:wrap}
summary .m{color:var(--mute);font-weight:400}
.foot{color:var(--mute);font-size:12px;margin-top:24px}
"""

NUMERIC = {"Trades", "Win %", "Net", "Avg win", "Avg loss", "PF", "Qty", "Entry",
           "Exit", "Hold", "Breaches", "Square-offs"}


def h_table(head, rows):
    def cell(tag, v, col):
        cls = ' class="n"' if col in NUMERIC else ""
        txt = html.escape(str(v))
        if tag == "td" and isinstance(v, str) and v.startswith(("+₹", "-₹")):
            cls = f' class="n {"up" if v[0] == "+" else "dn"}"'
        return f"<{tag}{cls}>{txt}</{tag}>"
    thead = "".join(cell("th", c, c) for c in head)
    body = "".join("<tr>" + "".join(cell("td", v, c) for v, c in zip(r, head)) + "</tr>"
                   for r in rows)
    return f'<div class="tw"><table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table></div>'


def h_day(d, is_latest):
    s = d["stats"]
    kpis = [("Net", rs(s["net"])), ("Win rate", f"{s['wins']}/{s['n']} · {pct(s['win_rate'])}"),
            ("Profit factor", ratio(s["pf"])), ("Expectancy", rs(s["expectancy"])),
            ("Avg win / loss", f"{rs(s['avg_win'], False)} / {rs(-s['avg_loss'])}"),
            ("Costs", f"{rs(-s['cost'])} · {s['cost'] / abs(s['gross']) * 100:.0f}% of gross"
             if s["gross"] else rs(-s["cost"]))]
    kpi_html = "".join(
        f'<div class="kpi"><div class="l">{l}</div>'
        f'<div class="v{" up" if v.startswith("+") else " dn" if v.startswith("-") else ""}">{html.escape(v)}</div></div>'
        for l, v in kpis)
    breaches = ("".join(f'<div class="breach">{html.escape(b)}</div>' for b in d["breaches"])
                or '<p class="clean">Clean. Every rule held.</p>')
    body = f"""
<div class="grid">{kpi_html}</div>
<div class="row">
 <div class="card"><h2>Equity through the day</h2>{svg_equity(d["trades"])}</div>
 <div class="card"><h2>Two strategies, by entry time</h2>{h_table(SPLIT_HEAD, split_rows(d["by_session"]))}
  <h2 style="margin-top:14px">Direction</h2>{h_table(SPLIT_HEAD, split_rows(d["by_dir"]))}</div>
</div>
<div class="row">
 <div class="card"><h2>Signal exit vs timer square-off</h2>{h_table(SPLIT_HEAD, split_rows(d["by_exit"]))}
  <p class="sub" style="margin:10px 0 0">{html.escape(concentration_line(d))}</p></div>
 <div class="card"><h2>Rule check — CONTEXT.md</h2>{breaches}</div>
</div>
<div class="card"><h2>Trades</h2>{h_table(TRADE_HEAD, trade_rows(d["trades"]))}</div>"""
    if is_latest:
        return body
    return (f'<details><summary>{d["date"]}<span class="m">{s["n"]} trades · '
            f'{pct(s["win_rate"])} · PF {ratio(s["pf"])}</span>'
            f'<span class="{"up" if s["net"] > 0 else "dn"}">{rs(s["net"])}</span></summary>{body}</details>')


def render_html(days, stamp):
    latest = days[-1]
    s = latest["stats"]
    total = sum(d["stats"]["net"] for d in days)
    older = "".join(h_day(d, False) for d in reversed(days[:-1]))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Business Onlooker — Trading Dashboard</title><style>{CSS}</style></head><body><main>
<h1>Business Onlooker — Trading Dashboard</h1>
<p class="sub">Shoonya fills via daily_report.py · updated {stamp} · costs are real Shoonya intraday charges</p>
<div class="hero"><div class="net {"up" if s["net"] > 0 else "dn"}">{rs(s["net"])}</div>
<div>{latest["date"]} · {s["n"]} trades · {pct(s["win_rate"])} win rate</div>
<div class="sub" style="margin:0">Running total over {len(days)} day{"s" if len(days) != 1 else ""}:
<b class="{"up" if total > 0 else "dn"}">{rs(total)}</b></div></div>
{h_day(latest, True)}
<div class="row" style="margin-top:18px">
 <div class="card"><h2>Daily net and running total</h2>{svg_history(days)}</div>
 <div class="card"><h2>History</h2>{h_table(HIST_HEAD, history_rows(list(reversed(days))))}</div>
</div>
<h2 style="margin-top:8px">Earlier days</h2>{older or '<p class="sub">None yet.</p>'}
<p class="foot">Generated by business-onlooker/dashboard.py. Numbers come from analyze_trades.py —
same FIFO pairing and Shoonya charge model as the text report. SQUARE-OFF = exit at/after the cutoff
or in the same second as 2+ other exits.</p>
</main></body></html>"""


# ---------------------------------------------------------------- markdown

def md_table(head, rows):
    align = "|".join("---:" if c in NUMERIC else "---" for c in head)
    out = ["| " + " | ".join(head) + " |", f"|{align}|"]
    out += ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
    return "\n".join(out)


def render_md(days, stamp):
    d = days[-1]
    total = sum(x["stats"]["net"] for x in days)
    breaches = "\n".join(f"- [!] {b}" for b in d["breaches"]) or "- Clean. Every rule held."
    return f"""# Trading dashboard

Updated {stamp} by `daily_report.py`. Open `dashboard.html` from this folder for charts.
Running total over {len(days)} day(s): **{rs(total)}**.

## History

{md_table(HIST_HEAD, history_rows(list(reversed(days))))}

## {d['date']} — {rs(d['stats']['net'])}

{md_table(["Metric", "Value"], headline_rows(d))}

### Two strategies, by entry time

{md_table(SPLIT_HEAD, split_rows(d['by_session']))}

### Direction

{md_table(SPLIT_HEAD, split_rows(d['by_dir']))}

### Signal exit vs timer square-off

{md_table(SPLIT_HEAD, split_rows(d['by_exit']))}

{concentration_line(d)}

### Rule check — CONTEXT.md

{breaches}

### Trades

{md_table(TRADE_HEAD, trade_rows(d['trades']))}
"""


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", default=str(HERE / "reports"))
    ap.add_argument("--capital", type=float, default=10000.0)
    ap.add_argument("--brokerage", type=float, default=at.BROKERAGE_PER_ORDER)
    ap.add_argument("--n500", default=str(HERE / "data" / "nifty500.txt"))
    ap.add_argument("--flat-by", default=at.FLAT_BY)
    ap.add_argument("--squareoff-after", default="15:00",
                    help="exits at/after this are the timer, not the signal")
    args = ap.parse_args()

    root = Path(args.reports)
    universe = at.read_universe(args.n500)
    days = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir() and (p / "tradebook.json").exists()):
        try:
            day = load_day(folder, args, universe)
        except Exception as e:  # one bad day must not kill the dashboard
            print(f"  skip {folder.name}: {e}", file=sys.stderr)
            continue
        if day:
            days.append(day)
    if not days:
        sys.exit(f"No tradebooks with round trips under {root}")

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    (root / "dashboard.html").write_text(render_html(days, stamp))
    (root / "README.md").write_text(render_md(days, stamp))
    latest = days[-1]
    print(f"Dashboard: {len(days)} day(s), latest {latest['date']} "
          f"{rs(latest['stats']['net'])} on {latest['stats']['n']} trades")
    print(f"  {root / 'dashboard.html'}\n  {root / 'README.md'}")


if __name__ == "__main__":
    main()
