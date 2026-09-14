# Business Onlooker — Business Context

Living document. Append or edit as the desk's setup changes — don't delete
history; if a fact changes, keep the old value with a date next to the new
one so a post-mortem can tell what was true on the day a trade happened.

---

## Market & mandate

- Market: **NSE** (National Stock Exchange), India.
- Style: **Intraday only** — no overnight carry.
- Session window: **Monday–Friday, 09:15–15:00 IST**.
- Execution: **Fully algorithmic.** No discretionary manual trades.

## Capital & risk

- Max capital per stock: **₹10,000**.
- **Intraday leverage: 5x (MIS).** But size by RISK, not by margin — risk 2%
  of capital (~Rs 200) per trade, so position = 200 / stop-distance. The
  leverage exists to reach higher-priced stocks, not to multiply risk on
  ones already affordable.

## Universe — screen this and nothing else

- **NIFTY 500 only.** Wide enough for real range (allSec had 9 names at +20%
  on 2026-09-09 vs FOSec's best of +3.49%), liquid enough to exit, and 5x
  MIS leverage is available on it.
- Constituent list: `https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv`
  (501 symbols). Filter every mover screen against it.
- Skip anything outside it — the +20% micro-caps are untradeable size and
  the F&O-only list is too narrow to hit the target R:R.
- *(Add when set: total capital deployed, max concurrent positions, daily
  loss limit, per-trade stop-loss convention.)*

## Infrastructure

- Platform: **OpenAlgo**, self-hosted.
- Broker: **Shoonya** (Finvasia).
- *(Add when set: server/hosting details, strategy repo location,
  monitoring/alerting setup.)*

## Data access — read this before trying to fetch anything

- **NSE access WORKS as of 2026-09-10.** The environment's network policy was
  widened, so `nseindia.com` no longer 403s at the egress proxy.
- **NSE's own Cloudflare is the remaining hurdle**, and `fetch_movers.py`
  handles it: it resets HTTP/2 (so use HTTP/1.1 — urllib does, `requests`
  with HTTP/2 does not) and answers the first request with **403 while still
  setting the cookies the API needs**, so the 403 body is read, not raised.
  Browser User-Agent and a Referer are required.
- **Run `fetch_movers.py` directly in-session** — it writes CSV + raw JSON to
  `business-onlooker/data/<date>/`. No more screenshot reading.
- **Always pull `allSec`, not just `FOSec`.** Proven on 2026-09-09: allSec had
  nine names at +20% upper circuit and two at -20%, while FOSec's best was
  +3.49% and worst -6.75%. A ~6x difference in available range. The desk's
  target R:R only exists in the cash market.
- `WebSearch` works for news and runs server-side. Use it to attach a cause to
  every mover the filter flags.

## Daily loop — trade post-mortem (automated 2026-09-14)

- **Nothing is uploaded by hand.** `daily_report.py` runs on the machine that
  hosts OpenAlgo — a scheduler fires it at 15:35 IST on weekdays. It pulls the
  day's fills from OpenAlgo's `/api/v1/tradebook` (falls back to Shoonya's own
  `/TradeBook`), writes `reports/<date>/tradebook.json` + `report.txt`, then
  runs `dashboard.py` and pushes.
- **The dashboard is two files, rebuilt every run:** `reports/dashboard.html`
  (charts — open it locally) and `reports/README.md` (GitHub renders it at the
  `reports/` folder URL, so that is the daily dashboard on a phone).
- **Credentials live only in `business-onlooker/.env` on that machine**
  (gitignored). The OpenAlgo key alone is enough; Shoonya password/TOTP are
  only for the fallback path. Never paste any of them into a chat session —
  the remote Claude container cannot reach OpenAlgo (`127.0.0.1:5000` is
  local) and must never hold broker credentials. The connection runs there;
  the analysis reads the pushed files here.
- Manual fallback still works: export the Shoonya Trade Book CSV and run
  `python3 analyze_trades.py <file> --n500 data/nifty500.txt`.
- **The rule-breach block is the point, not the P&L.** The broker already
  shows P&L. What it can't show is which rule cost the money. The two that
  compound: ASYMMETRY (avg loss > avg win) and DISCIPLINE (losers held longer
  than winners).
- Dashboard splits, because the desk runs two strategies: **BEFORE 12 vs
  AFTER 12 by ENTRY time**, LONG vs SHORT, **SIGNAL exit vs timer SQUARE-OFF**
  (exit at/after 15:00, or 3+ symbols exiting in the same second — 2026-09-10
  had 8 orders at 15:06:02), and **concentration** (share of gross profit in
  the best trade — 2026-09-10 had 51% in WELCORP).
- Shoonya field trap, fixed 2026-09-14: `flqty`/`flprc`/`fltm` describe the
  fill; `fillshares`/`avgprc` are the parent order's running totals and
  repeat on every partial-fill row. The analyzer reads the former and merges
  partial fills back into one position before computing anything.
- WINDOW rule cutoff is **15:00** (was 11:15 in the first analyzer draft; the
  after-12 strategy runs to the close, so 11:15 flagged every legitimate
  afternoon exit).

## Daily loop

- Every trading day, the previous session's top movers (gainers/losers) are
  fed in for analysis.
- Business Onlooker's job on that input: post-mortem each mover (why it
  moved, whether the algo's setup caught it and why/why not), then a
  forward view for the next session — per the standing rule in
  [`AGENT.md`](AGENT.md), every verdict carries a conviction level and an
  invalidation level.

---

## Change log

- **2026-09-04** — Agent created. Context above is the starting set given by
  Uday; nothing has changed yet.
- **2026-09-09** — Standing rules added in `AGENT.md`: search before saying
  "no news" (ADANIENT miss), macro block before corporate (Nifty IT miss).
- **2026-09-10** — Five-bullet answers, tables required. Universe pinned to
  Nifty 500. NSE access works; `fetch_movers.py` and `screen.py` added.
  `analyze_trades.py` + `daily_report.py` added for the Shoonya post-mortem.
- **2026-09-14** — Dashboard added (`dashboard.py` → `reports/dashboard.html`
  + `reports/README.md`), wired into `daily_report.py`. Shoonya `flqty` vs
  `fillshares` fix; partial fills merged; WINDOW cutoff moved to 15:00.
