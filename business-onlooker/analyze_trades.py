#!/usr/bin/env python3
"""
Post-mortem a day's Shoonya trading against the desk's own rules.

    python3 analyze_trades.py tradebook.csv
    python3 analyze_trades.py tradebook.json --n500 data/nifty500.txt

Input is Shoonya's own data: the /TradeBook JSON that daily_report.py pulls
every close, or the Trade Book CSV exported from trade.shoonya.com for a
past day.

This is not a P&L report - the broker already gives you one. It pairs fills
into round trips and then checks them against the rules in CONTEXT.md:
Rs 10,000 a stock, Nifty 500 only, flat by the session cutoff. The point is
to show which rule you broke and what it cost, because that is the number
that changes behaviour.

dashboard.py imports the functions below, so the numbers on the dashboard
and in this report can never disagree.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

# Shoonya NSE equity intraday rate card, shoonya.com/pricing as of
# 2026-09-14. Fractions of turnover unless stated. Until 2026-09-14 this
# file modelled brokerage at Rs 20/order - four times the real cap - so
# every cost figure before that date was overstated. The contract note is
# the final word; this is the rate card applied to the fills.
BROKERAGE_PER_ORDER = 5.0       # Rs 5 or 0.03% per executed order, whichever is lower
BROKERAGE_PCT = 0.0003
STT_SELL = 0.00025              # sell side only, intraday equity
EXCHANGE_TXN = 0.0000297        # NSE
SEBI_FEES = 0.000001
STAMP_DUTY_BUY = 0.00003        # buy side only
GST = 0.18                      # on brokerage + exchange + SEBI

FLAT_BY = "15:00"               # CONTEXT.md session window ends here

# Column aliases. Shoonya's TradeBook API and its web CSV export disagree
# on names; the generic ones cover any hand-made file. First match wins.
#
# Shoonya API: flqty/flprc/fltm are THIS fill. fillshares/avgprc are the
# parent order's running totals, so a partially filled order shows them
# repeated on every row - summing fillshares would count shares twice.
ALIASES = {
    "symbol": ["tsym", "tradingsymbol", "symbol", "scrip", "instrument"],
    "side": ["trantype", "buy/sell", "side", "action", "type"],
    "qty": ["flqty", "fillshares", "qty", "quantity", "filled qty", "tradeqty"],
    "price": ["flprc", "price", "average_price", "avg price", "fillprice"],
    "time": ["fltm", "exch_tm", "time", "norentm", "timestamp", "order time"],
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
    text = Path(path).read_text()
    if text.lstrip().startswith(("[", "{")):
        blob = json.loads(text)
        rows = blob if isinstance(blob, list) else blob.get("data", [])
    else:
        rows = list(csv.DictReader(text.splitlines()))

    fills = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        sym, side = pick(row, "symbol"), pick(row, "side").upper()
        qty, price = pick(row, "qty"), pick(row, "price")
        if not (sym and side and qty and price):
            continue
        qty, price = int(float(qty)), float(price)
        if qty <= 0 or price <= 0:          # rejected / unfilled rows
            continue
        fills.append({
            "symbol": sym.replace("-EQ", "").upper(),
            "buy": side.startswith("B"),
            "qty": qty,
            "price": price,
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


def merge_partials(trades):
    """Collapse partial fills of one position back into one round trip.

    A 6-share exit filled as 4 + 2 pairs into two rows above. For win rate
    and expectancy that is one trade, not two, so rows sharing symbol,
    direction and entry time are combined at volume-weighted prices. It also
    gets brokerage right: a partial fill is still one order.
    """
    merged = {}
    for t in trades:
        key = ((t["symbol"], t["direction"], t["entry_time"])
               if t["entry_time"] else (t["symbol"], t["direction"], id(t)))
        m = merged.get(key)
        if m is None:
            merged[key] = dict(t)
            continue
        q = m["qty"] + t["qty"]
        m["entry"] = (m["entry"] * m["qty"] + t["entry"] * t["qty"]) / q
        m["exit"] = (m["exit"] * m["qty"] + t["exit"] * t["qty"]) / q
        m["qty"] = q
        for k in ("gross", "turnover", "exposure"):
            m[k] += t[k]
        if t["exit_time"] and (not m["exit_time"] or t["exit_time"] > m["exit_time"]):
            m["exit_time"] = t["exit_time"]
    return list(merged.values())


CHARGE_KEYS = ["brokerage", "stt", "exchange", "sebi", "stamp", "gst"]
CHARGE_LABELS = {
    "brokerage": "Brokerage (Rs 5 or 0.03% per order)",
    "stt": "STT (0.025% on sell)",
    "exchange": "Exchange txn (0.00297%)",
    "sebi": "SEBI (Rs 10/crore)",
    "stamp": "Stamp duty (0.003% on buy)",
    "gst": "GST (18% on brokerage + exchange + SEBI)",
}


def charge_parts(trade, brokerage_per_order=BROKERAGE_PER_ORDER):
    """Round-trip charges by component. Two orders, STT on the sell leg's
    value, stamp on the buy leg's value, GST on the broker/exchange items."""
    buy_val = (trade["entry"] if trade["direction"] == "LONG" else trade["exit"]) * trade["qty"]
    sell_val = trade["turnover"] - buy_val
    brok = (min(brokerage_per_order, buy_val * BROKERAGE_PCT)
            + min(brokerage_per_order, sell_val * BROKERAGE_PCT))
    txn = trade["turnover"] * EXCHANGE_TXN
    sebi = trade["turnover"] * SEBI_FEES
    return {"brokerage": brok, "stt": sell_val * STT_SELL, "exchange": txn,
            "sebi": sebi, "stamp": buy_val * STAMP_DUTY_BUY, "gst": GST * (brok + txn + sebi)}


def costs(trade, brokerage_per_order=BROKERAGE_PER_ORDER):
    return sum(charge_parts(trade, brokerage_per_order).values())


def price_trades(trades, brokerage_per_order=BROKERAGE_PER_ORDER):
    """Attach cost, net and hold time to every round trip. In place."""
    for t in trades:
        t["charges"] = charge_parts(t, brokerage_per_order)
        t["cost"] = sum(t["charges"].values())
        t["net"] = t["gross"] - t["cost"]
        t["hold_min"] = ((t["exit_time"] - t["entry_time"]).total_seconds() / 60
                         if t["entry_time"] and t["exit_time"] else None)
    return trades


def summarise(trades):
    """Aggregate priced trades. Works on any subset, so it drives every split."""
    wins = [t for t in trades if t["net"] > 0]
    losses = [t for t in trades if t["net"] <= 0]
    gross = sum(t["gross"] for t in trades)
    cost = sum(t["cost"] for t in trades)
    gp = sum(t["net"] for t in wins)
    gl = abs(sum(t["net"] for t in losses))
    avg_win = gp / len(wins) if wins else 0.0
    avg_loss = gl / len(losses) if losses else 0.0
    win_hold = [t["hold_min"] for t in wins if t["hold_min"] is not None]
    loss_hold = [t["hold_min"] for t in losses if t["hold_min"] is not None]
    charges = {k: sum(t["charges"][k] for t in trades) for k in CHARGE_KEYS}
    return {
        "charges": charges, "orders": 2 * len(trades),
        "n": len(trades), "wins": len(wins), "losses": len(losses),
        "win_rate": len(wins) / len(trades) * 100 if trades else 0.0,
        "gross": gross, "cost": cost, "net": gross - cost,
        "gross_profit": gp, "gross_loss": gl,
        "avg_win": avg_win, "avg_loss": avg_loss,
        "rr": avg_win / avg_loss if avg_loss else None,
        "pf": gp / gl if gl else None,
        "expectancy": (gross - cost) / len(trades) if trades else 0.0,
        "win_hold": sum(win_hold) / len(win_hold) if win_hold else None,
        "loss_hold": sum(loss_hold) / len(loss_hold) if loss_hold else None,
    }


def rule_check(trades, open_legs, s, capital=10000.0, universe=None, flat_by=FLAT_BY):
    """Audit priced trades against CONTEXT.md. Returns breach strings."""
    breaches = []

    over = [t for t in trades if t["exposure"] > capital * 1.02]
    if over:
        worst = max(over, key=lambda t: t["exposure"])
        breaches.append(
            f"SIZE: {len(over)} trade(s) above Rs {capital:,.0f}/stock. "
            f"Worst {worst['symbol']} at {rupees(worst['exposure'])} "
            f"({worst['exposure'] / capital:.1f}x).")

    if universe:
        outside = sorted({t["symbol"] for t in trades if t["symbol"] not in universe})
        if outside:
            breaches.append(f"UNIVERSE: outside Nifty 500 — {', '.join(outside)}.")

    cutoff = datetime.strptime(flat_by, "%H:%M").time()
    late = [t for t in trades if t["exit_time"] and t["exit_time"].time() > cutoff]
    if late:
        breaches.append(
            f"WINDOW: {len(late)} exit(s) after {flat_by}, worth "
            f"{rupees(sum(t['net'] for t in late))} — the signal never fired, "
            f"the square-off did.")

    if s["wins"] and s["losses"] and s["avg_loss"] > s["avg_win"]:
        breaches.append(
            f"ASYMMETRY: avg loss {rupees(s['avg_loss'])} exceeds avg win "
            f"{rupees(s['avg_win'])}. Losers are running further than winners — "
            f"this is the one that compounds against you.")

    if s["win_hold"] is not None and s["loss_hold"] is not None \
            and s["loss_hold"] > s["win_hold"] * 1.3:
        breaches.append(
            f"DISCIPLINE: losers held {s['loss_hold']:.0f} min vs winners "
            f"{s['win_hold']:.0f} min. You are cutting winners early and "
            f"hoping on losers.")

    if s["net"] > 0 and s["gross"] and s["cost"] > abs(s["gross"]) * 0.25:
        breaches.append(
            f"COSTS: charges ate {s['cost'] / abs(s['gross']) * 100:.0f}% of gross. "
            f"Position sizes are too small for the trade frequency.")

    if open_legs:
        breaches.append(
            f"OPEN: {len(open_legs)} unmatched leg(s) — "
            f"{', '.join(sorted({sym for sym, _, _ in open_legs}))}. "
            f"Carried overnight, or the export is partial.")
    return breaches


def read_universe(path):
    p = Path(path) if path else None
    if p and p.exists():
        return {x.strip().upper() for x in p.read_text().split() if x.strip()}
    return None


def rupees(x):
    return f"{'-' if x < 0 else ''}Rs {abs(x):,.2f}" if abs(x) < 10 else f"{'-' if x < 0 else ''}Rs {abs(x):,.0f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tradebook")
    ap.add_argument("--capital", type=float, default=10000.0)
    ap.add_argument("--brokerage", type=float, default=BROKERAGE_PER_ORDER)
    ap.add_argument("--n500", default="", help="Nifty 500 symbol list, one per line")
    ap.add_argument("--flat-by", default=FLAT_BY)
    args = ap.parse_args()

    fills = load(args.tradebook)
    if not fills:
        sys.exit("No fills parsed. Check the export has symbol/side/qty/price columns.")
    trades, open_legs = pair_trades(fills)
    trades = merge_partials(trades)
    if not trades:
        sys.exit(f"{len(fills)} fills, no round trips. Positions still open?")

    price_trades(trades, args.brokerage)
    s = summarise(trades)

    print(f"\n{'='*62}\n  {s['n']} round trips | {len(fills)} fills\n{'='*62}")
    print(f"  Gross P&L        {rupees(s['gross']):>16}")
    if s["gross"]:
        print(f"  Costs            {rupees(-s['cost']):>16}   "
              f"({s['cost'] / abs(s['gross']) * 100:.0f}% of gross)")
    print(f"  NET P&L          {rupees(s['net']):>16}   "
          f"({s['net'] / args.capital * 100:+.2f}% on capital)")
    print(f"\n  Win rate         {s['wins']}/{s['n']} = {s['win_rate']:.0f}%")
    print(f"  Avg win          {rupees(s['avg_win']):>16}")
    print(f"  Avg loss         {rupees(-s['avg_loss']):>16}")
    if s["rr"] is not None:
        print(f"  Realised R:R     {s['rr']:>13.2f}:1   (target 1:10 — see CONTEXT.md)")
    if s["pf"] is not None:
        print(f"  Profit factor    {s['pf']:>16.2f}")
    print(f"  Expectancy/trade {rupees(s['expectancy']):>16}")
    if s["win_hold"] is not None and s["loss_hold"] is not None:
        print(f"  Avg hold — winners {s['win_hold']:.0f} min, losers {s['loss_hold']:.0f} min")

    print(f"\n{'-'*62}\n  TAXES & CHARGES — Shoonya rate card, {s['orders']} orders\n{'-'*62}")
    for k in CHARGE_KEYS:
        print(f"  {CHARGE_LABELS[k]:<44}{rupees(s['charges'][k]):>14}")
    print(f"  {'Total':<44}{rupees(s['cost']):>14}")

    print(f"\n{'-'*62}\n  RULE CHECK — against CONTEXT.md\n{'-'*62}")
    breaches = rule_check(trades, open_legs, s, args.capital,
                          read_universe(args.n500), args.flat_by)
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
