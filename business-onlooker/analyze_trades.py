#!/usr/bin/env python3
"""
Post-mortem a day's Shoonya trading against the desk's own rules.

    python3 analyze_trades.py tradebook.csv
    python3 analyze_trades.py tradebook.csv --capital 10000 --brokerage 20

Export from Shoonya: Reports -> Trade Book -> download CSV. Or dump
OpenAlgo's /tradebook response to JSON and pass that instead.

This is not a P&L report - the broker already gives you one. It pairs fills
into round trips and then checks them against the rules in CONTEXT.md:
Rs 10,000 a stock, Nifty 500 only, 2% risk, flat by 11:15. The point is to
show which rule you broke and what it cost, because that is the number that
changes behaviour.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

# Shoonya intraday equity, as fractions of turnover unless stated.
BROKERAGE_PER_ORDER = 20.0      # Rs 20 or 0.03%, whichever is lower
BROKERAGE_PCT = 0.0003
STT_SELL = 0.00025              # sell side only, intraday equity
EXCHANGE_TXN = 0.0000297        # NSE
SEBI_FEES = 0.000001
STAMP_DUTY_BUY = 0.00003        # buy side only
GST = 0.18                      # on brokerage + exchange + SEBI

# Column aliases. Shoonya's web export and OpenAlgo disagree on names.
ALIASES = {
    "symbol": ["tsym", "tradingsymbol", "symbol", "scrip", "instrument"],
    "side": ["trantype", "buy/sell", "side", "action", "type"],
    "qty": ["fillshares", "qty", "quantity", "filled qty", "tradeqty"],
    "price": ["flprc", "price", "avg price", "average_price", "fillprice"],
    "time": ["fltm", "time", "norentm", "timestamp", "order time", "exch_tm"],
    "product": ["prd", "product", "producttype"],
}


def pick(row, key):
    """Find a column by any of its known aliases, case-insensitively."""
    lowered = {k.strip().lower(): v for k, v in row.items() if k}
    for alias in ALIASES[key]:
        if alias in lowered and str(lowered[alias]).strip():
            return str(lowered[alias]).strip()
    return ""


def parse_time(raw):
    for fmt in ("%H:%M:%S %d-%m-%Y", "%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%d-%b-%Y %H:%M:%S", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(raw.strip(), fmt)
        except ValueError:
            continue
    return None


def load(path):
    """Read Shoonya CSV or OpenAlgo JSON into a flat list of fills."""
    text = Path(path).read_text()
    if text.lstrip().startswith(("[", "{")):
        blob = json.loads(text)
        rows = blob if isinstance(blob, list) else blob.get("data", [])
    else:
        rows = list(csv.DictReader(text.splitlines()))

    fills = []
    for row in rows:
        sym, side = pick(row, "symbol"), pick(row, "side").upper()
        qty, price = pick(row, "qty"), pick(row, "price")
        if not (sym and side and qty and price):
            continue
        fills.append({
            "symbol": sym.replace("-EQ", "").upper(),
            "buy": side.startswith("B"),
            "qty": int(float(qty)),
            "price": float(price),
            "time": parse_time(pick(row, "time")),
            "product": pick(row, "product").upper(),
        })
    return fills


def pair_trades(fills):
    """FIFO-match opposing fills per symbol into round trips."""
    books = defaultdict(lambda: {"long": deque(), "short": deque()})
    trades = []

    for f in sorted(fills, key=lambda x: (x["time"] or datetime.min)):
        book = books[f["symbol"]]
        # A buy first closes open shorts, then opens a long. And vice versa.
        opposite = book["short"] if f["buy"] else book["long"]
        qty = f["qty"]

        while qty and opposite:
            entry = opposite[0]
            matched = min(qty, entry["qty"])
            gross = ((f["price"] - entry["price"]) * matched if f["buy"] is False
                     else (entry["price"] - f["price"]) * matched)
            trades.append({
                "symbol": f["symbol"],
                "direction": "SHORT" if f["buy"] else "LONG",
                "qty": matched,
                "entry": entry["price"],
                "exit": f["price"],
                "entry_time": entry["time"],
                "exit_time": f["time"],
                "gross": gross,
                "turnover": (entry["price"] + f["price"]) * matched,
                "exposure": entry["price"] * matched,
            })
            entry["qty"] -= matched
            qty -= matched
            if not entry["qty"]:
                opposite.popleft()

        if qty:
            book["long" if f["buy"] else "short"].append({**f, "qty": qty})

    open_legs = [(s, side, leg) for s, b in books.items()
                 for side in ("long", "short") for leg in b[side]]
    return trades, open_legs


def costs(trade, brokerage_per_order):
    """Round-trip charges. Two orders, STT on the sell, stamp on the buy."""
    half = trade["turnover"] / 2
    brok = 2 * min(brokerage_per_order, half * BROKERAGE_PCT)
    txn = trade["turnover"] * EXCHANGE_TXN
    sebi = trade["turnover"] * SEBI_FEES
    return (brok + txn + sebi + GST * (brok + txn + sebi)
            + half * STT_SELL + half * STAMP_DUTY_BUY)


def rupees(x):
    return f"{'-' if x < 0 else ''}Rs {abs(x):,.0f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tradebook")
    ap.add_argument("--capital", type=float, default=10000.0)
    ap.add_argument("--brokerage", type=float, default=BROKERAGE_PER_ORDER)
    ap.add_argument("--n500", default="", help="Nifty 500 symbol list, one per line")
    ap.add_argument("--flat-by", default="11:15")
    args = ap.parse_args()

    fills = load(args.tradebook)
    if not fills:
        sys.exit("No fills parsed. Check the export has symbol/side/qty/price columns.")
    trades, open_legs = pair_trades(fills)
    if not trades:
        sys.exit(f"{len(fills)} fills, no round trips. Positions still open?")

    for t in trades:
        t["cost"] = costs(t, args.brokerage)
        t["net"] = t["gross"] - t["cost"]

    wins = [t for t in trades if t["net"] > 0]
    losses = [t for t in trades if t["net"] <= 0]
    gross = sum(t["gross"] for t in trades)
    cost = sum(t["cost"] for t in trades)
    net = gross - cost
    avg_win = sum(t["net"] for t in wins) / len(wins) if wins else 0
    avg_loss = abs(sum(t["net"] for t in losses) / len(losses)) if losses else 0

    print(f"\n{'='*62}\n  {len(trades)} round trips | {len(fills)} fills\n{'='*62}")
    print(f"  Gross P&L        {rupees(gross):>16}")
    print(f"  Costs            {rupees(-cost):>16}   "
          f"({cost / abs(gross) * 100:.0f}% of gross)" if gross else "")
    print(f"  NET P&L          {rupees(net):>16}   "
          f"({net / args.capital * 100:+.2f}% on capital)")
    print(f"\n  Win rate         {len(wins)}/{len(trades)} = "
          f"{len(wins) / len(trades) * 100:.0f}%")
    print(f"  Avg win          {rupees(avg_win):>16}")
    print(f"  Avg loss         {rupees(-avg_loss):>16}")
    if avg_loss:
        print(f"  Realised R:R     {avg_win / avg_loss:>13.2f}:1"
              f"   (target 1:10 — see CONTEXT.md)")
    gp = sum(t["net"] for t in wins)
    gl = abs(sum(t["net"] for t in losses))
    if gl:
        print(f"  Profit factor    {gp / gl:>16.2f}")
    print(f"  Expectancy/trade {rupees(net / len(trades)):>16}")

    print(f"\n{'-'*62}\n  RULE CHECK — against CONTEXT.md\n{'-'*62}")
    breaches = []

    over = [t for t in trades if t["exposure"] > args.capital * 1.02]
    if over:
        worst = max(over, key=lambda t: t["exposure"])
        breaches.append(
            f"SIZE: {len(over)} trade(s) above Rs {args.capital:,.0f}/stock. "
            f"Worst {worst['symbol']} at {rupees(worst['exposure'])} "
            f"({worst['exposure'] / args.capital:.1f}x).")

    if args.n500 and Path(args.n500).exists():
        universe = {s.strip().upper() for s in Path(args.n500).read_text().split()}
        outside = sorted({t["symbol"] for t in trades if t["symbol"] not in universe})
        if outside:
            breaches.append(f"UNIVERSE: outside Nifty 500 — {', '.join(outside)}.")

    cutoff = datetime.strptime(args.flat_by, "%H:%M").time()
    late = [t for t in trades if t["exit_time"] and t["exit_time"].time() > cutoff]
    if late:
        cost_of_late = sum(t["net"] for t in late)
        breaches.append(
            f"WINDOW: {len(late)} exit(s) after {args.flat_by}, "
            f"worth {rupees(cost_of_late)} — kept or lost by holding on.")

    if len(wins) and len(losses) and avg_loss > avg_win:
        breaches.append(
            f"ASYMMETRY: avg loss {rupees(avg_loss)} exceeds avg win "
            f"{rupees(avg_win)}. Losers are running further than winners — "
            f"this is the one that compounds against you.")

    held = [t for t in trades if t["entry_time"] and t["exit_time"]]
    if held:
        def mins(t):
            return (t["exit_time"] - t["entry_time"]).total_seconds() / 60
        win_hold = [mins(t) for t in held if t["net"] > 0]
        loss_hold = [mins(t) for t in held if t["net"] <= 0]
        if win_hold and loss_hold:
            w, l = sum(win_hold) / len(win_hold), sum(loss_hold) / len(loss_hold)
            print(f"  Avg hold — winners {w:.0f} min, losers {l:.0f} min")
            if l > w * 1.3:
                breaches.append(
                    f"DISCIPLINE: losers held {l:.0f} min vs winners {w:.0f} min. "
                    f"You are cutting winners early and hoping on losers.")

    if net > 0 and cost > abs(gross) * 0.25:
        breaches.append(
            f"COSTS: charges ate {cost / abs(gross) * 100:.0f}% of gross. "
            f"Position sizes are too small for the trade frequency.")

    if open_legs:
        breaches.append(
            f"OPEN: {len(open_legs)} unmatched leg(s) — "
            f"{', '.join(sorted({s for s, _, _ in open_legs}))}. "
            f"Carried overnight, or the export is partial.")

    for b in breaches:
        print(f"  [!] {b}")
    if not breaches:
        print("  Clean. Every rule held.")

    print(f"\n{'-'*62}\n  TRADES\n{'-'*62}")
    print(f"  {'SYMBOL':<12}{'DIR':<7}{'QTY':>5}{'ENTRY':>10}{'EXIT':>10}{'NET':>11}")
    for t in sorted(trades, key=lambda t: t["net"]):
        print(f"  {t['symbol']:<12}{t['direction']:<7}{t['qty']:>5}"
              f"{t['entry']:>10.2f}{t['exit']:>10.2f}{rupees(t['net']):>11}")
    print()


if __name__ == "__main__":
    main()
