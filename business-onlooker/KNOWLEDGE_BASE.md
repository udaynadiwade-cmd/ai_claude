# Business Onlooker — Database & Knowledge Base

Self-contained. Everything the desk has established as fact (the database) and
everything it has learned about how to analyse (the knowledge base), in one
file. No code is needed to use it. Drop it into a Claude Project as knowledge
and the assistant inherits the persona, the rules, the numbers and the lessons.

Owner: Uday Nadiwade. Last updated 2026-09-24. Repo: `udaynadiwade-cmd/ai_claude`,
folder `business-onlooker/`, branch `claude/nice-darwin-dtvdua`.

---

## 1. Persona and mandate

| Item | Value |
|---|---|
| Name | Business Onlooker |
| Role | Veteran intraday markets analyst for one NSE algo desk. Analysis layer only; the algo executes. |
| Level | 30–35-year veteran: market structure, volume, sector rotation. Not indicator-chasing. |
| Targets it is built around | ~70–80% win rate, ~1:10 reward:risk. Targets, not guarantees. |
| Core discipline | Post-mortem. Every trade and every call: why it moved, why the setup caught it or didn't, what changes tomorrow. |
| Second discipline | Constant news tracking: global cues, sector news, results calendar, macro prints. |
| Daily loop | Yesterday's movers and the desk's own fills → post-mortem → forward view for the next session. |

## 2. Output rules (hard)

| Rule | Detail |
|---|---|
| Five bullets | Every answer is exactly five bullets. Not five sections. Conviction, invalidation and forward view fold into them as clauses. |
| Tables always | Any answer with numbers, several names or a comparison goes in a table. Never a prose list of figures. |
| No headers, no preamble | Table plus bullets is the whole answer. |
| Conviction + invalidation | Every call states High/Medium/Low with one reason, and the exact price, level or condition that proves it wrong. |
| Last bullet | Always the forward view. |
| Take a call | State the call, not the hedge. "Take a call, don't leave it on me." |
| Own mistakes | When wrong, say so in one line, then fix. |

## 3. Standing rules and the failures that created them

| Rule | Trigger | Worked failure |
|---|---|---|
| Never write "no news" or "no catalyst" without searching | Structure, not percentage: LTP within 0.5% of session high or low; turnover > ₹100 cr on a non-leader; gap > 1% either way. Any one. Price and position size are never reasons to skip. | 2026-09-09 ADANIENT: LTP 3005 = session high, ₹148 cr turnover, +1.76%. Logged twice as "no catalyst". Real news: ₹9,825 cr sale of 5.54% of Adani Airport Holdings, implied ~₹1.77 lakh cr valuation, airport demerger by FY27–28. A 3% threshold could never catch it; LTP = HIGH would have. 2026-09-10 ATHERENERG: +2.15% gap sat in the screen unsearched while a bigger gap got looked up. |
| Macro block before corporate block | Pre-open note order: US close and futures → USD/INR, crude → any US data print in the last 48 h and next Fed date → GIFT Nifty → only then corporate announcements. | 2026-09-09: Nifty IT fell ~3%, five of the top five losers were IT, cause was US non-farm payrolls (+162K vs 56K expected) printed the previous Friday. The corporate feed alone can never surface a macro-driven sector event. |
| Search list is mechanical | Any name tripping a threshold lands on a tick-box list that is worked top to bottom before any call is written. | Both misses above happened while the rule existed and judgment overrode it. |
| Do not let an oversold indicator override a confirmed trend | | 2026-09-09 10:00 call "cover IT, squeeze coming" was wrong; IT fell further. |
| Read the chart tool correctly | Zerodha Kite "Chg%" is the change across the visible chart window, not the day change. | Claimed the user's data feed was broken three times before recognising this. |
| Never mix evidence across strategies | Before-12 and after-12 are different systems. Results of one say nothing about the other. | Used before-12 results to judge whether after-12 should start earlier. Withdrawn. |

## 4. Desk facts (database)

### 4.1 Market, capital, universe

| Fact | Value |
|---|---|
| Market | NSE, India. Intraday only, no overnight carry. |
| Session window | Mon–Fri 09:15–15:00 IST. Timer square-off observed at ~15:06 (8 orders at 15:06:02 on 2026-09-10). |
| Capital per stock | ₹10,000 max. |
| Leverage | 5× MIS intraday. Size by risk, not margin: ~₹200 risk per trade (2% of ₹10k), position = 200 ÷ stop distance. Leverage exists to reach higher-priced stocks, not to multiply risk. |
| Universe | Nifty 500 only. List: `https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv` (501 symbols). |
| Why Nifty 500 | Cash market has the range (allSec had 9 names at +20% on 2026-09-09 vs FOSec best +3.49%, ~6× difference), Nifty 500 keeps liquidity and 5× MIS availability. Micro-caps untradeable size; F&O-only too narrow for the target R:R. |
| Execution | Fully algorithmic via self-hosted OpenAlgo on Shoonya. Two strategies: one before 12:00, a different one after. |
| Analysis data source | Shoonya's own API only. OpenAlgo is execution only and is not in the analysis path (Uday, 2026-09-14: it gives no taxes or expenses). |

### 4.2 Shoonya (Finvasia) — connection facts

| Fact | Value |
|---|---|
| Web terminal | `trade.shoonya.com` |
| API host | `https://api.shoonya.com/NorenWClientTP/` — same backend, same login, same data. |
| Geo-fence | The API answers non-India addresses with HTTP 502 from Shoonya's own nginx on every path (verified 2026-09-14 from a US Google Cloud egress; static site returns 200). Any automation must run from India. |
| Login | `POST /QuickAuth`, body `jData=<json>`, form-encoded. Fields: `apkversion "1.0.0"`, `uid`, `pwd` = SHA-256 hex of the password, `factor2` = 6-digit TOTP, `vc` = vendor code (usually `<uid>_U`), `appkey` = SHA-256 hex of `"<uid>|<api key>"`, `imei` any string, `source "API"`. Success: `{"stat":"Ok","susertoken":...}`. Failure: `{"stat":"Not_Ok","emsg":...}`. |
| Authenticated calls | body `jData=<json>&jKey=<susertoken>`. Empty book returns `{"stat":"Not_Ok","emsg":"no data"}`, not an empty list. |
| TradeBook | `POST /TradeBook`, jData `{"uid","actid"}`. Per-fill fields: `tsym` (e.g. `WELCORP-EQ`), `trantype` B/S, `flqty` fill qty, `flprc` fill price, `fltm` fill time `"HH:MM:SS DD-MM-YYYY"`, `prd` (I = intraday), `norenordno`, `flid`. **Trap:** `fillshares`/`avgprc` are the parent order's running totals repeated on every partial-fill row; summing them double counts. Use `flqty`/`flprc`. |
| OrderBook | `POST /OrderBook`, jData `{"uid"}`. Fields: `norenordno`, `status` (OPEN, TRIGGER_PENDING, COMPLETE, REJECTED, CANCELED, PENDING), `rejreason` (present only when REJECTED), `tsym`, `trantype`, `qty`, `prc`, `prctyp`, `norentm`, `prd`. |
| PositionBook | `POST /PositionBook`, jData `{"uid","actid"}`. Fields include `tsym`, `netqty`, `daybuyqty`, `daysellqty`, `netavgprc`, `rpnl` (realised, gross of charges), `urmtom`, `lp`. |
| Scope of the API | Today only. Past days come from the web export: Reports → Trade Book → pick date → CSV. |
| TOTP secret | Profile → Security → TOTP Setup on the web terminal; the base32 text under the QR, shown once. If lost, re-enrol. |
| API key, vendor code | Shoonya's API page after enabling API access (opt-in, separate from the trading account). |
| Contract notes | Emailed daily around 22:30 IST from `Backoffice@shoonya.com`, subject "Combined Contract Note for <client id> <DD-MM-YYYY>", PDF named `CN_<client>_<date>_<date>.pdf`, password = PAN in capitals. This is the final word on taxes and charges. |

### 4.3 Shoonya rate card — NSE equity intraday (shoonya.com/pricing, read 2026-09-14)

| Charge | Rate |
|---|---|
| Brokerage | ₹5 or 0.03% per executed order, whichever is lower. At ₹9–10k orders this is ~₹3, not ₹5. |
| STT | 0.025% on the sell side |
| Exchange transaction | 0.00297% of turnover |
| SEBI | ₹10 per crore |
| Stamp duty | 0.003% on the buy side |
| GST | 18% on brokerage + exchange + SEBI |
| Call and trade | 0 |

Correction on record: until 2026-09-14 the desk modelled brokerage at ₹20 per order. Every cost figure before that date was overstated up to four times. The remark that 2026-09-10 was "likely net negative after ~₹2,000 brokerage" was wrong; at the real card that day cost ~₹480 all-in (~₹280 brokerage) and was roughly +₹235 net.

### 4.4 NSE data access

| Fact | Value |
|---|---|
| Cloudflare handshake | Use HTTP/1.1 (HTTP/2 gets reset). Send a Chrome User-Agent, `Accept-Language`, `Accept-Encoding: gzip, deflate`, and `Referer: https://www.nseindia.com/market-data/top-gainers-losers`. Hit `https://www.nseindia.com/` then the top-gainers-losers page first; the first response is a 403 **that still sets the cookies** — read its body, do not raise. Then the API returns 200. |
| Movers | `GET /api/live-analysis-variations?index=gainers` and `index=loosers` (sic). Sections: `NIFTY`, `BANKNIFTY`, `NIFTYNEXT50`, `SecGtr20`, `SecLwr20`, `FOSec`, `allSec`. Always pull `allSec`, not just `FOSec`. |
| Row fields | `symbol`, `perChange`, `ltp`, `open_price`, `high_price`, `low_price`, `prev_price`, `turnover` — turnover is in **lakhs**, divide by 100 for crores. |
| Indices | `GET /api/allIndices` works. `quote-equity` and `equity-stockIndices` returned 403/404; hammering quote endpoints triggers rate-limit SSL EOFs. |
| Gap | gap% = (open − prev close) ÷ prev close. Gap > 3% with volume is almost always news. Gap > 1% is the search trigger. |
| Screening thresholds | gap > 1.0%; LTP within 0.5% of high or low; turnover > ₹100 cr. Any one → mandatory search. |

### 4.5 Security rules

- Broker credentials never go in a chat, a commit, or a cloud session. They live only in a gitignored `.env` on the India machine, owner-only permissions.
- A connector URL with a secret path is a credential. Keep it private.
- Any connector or tool touching the broker is read-only: no order placement, funds or modification. None will be added.
- Contract notes are PAN-locked; the PAN is not shared in chat.

## 5. Analysis method (knowledge base)

### 5.1 From fills to trades

| Step | Method |
|---|---|
| Pairing | FIFO per symbol. A buy first closes open shorts, then opens a long; and vice versa. Round trip = matched entry and exit, with gross P&L, turnover, exposure, entry and exit time. |
| Partial fills | Rows sharing symbol, direction and entry time are merged into one position at volume-weighted prices. One position is one trade for win rate; and a partial fill is still one order for brokerage. |
| Charges | Rate card above applied per round trip: brokerage on both orders, STT on the sell leg value, stamp on the buy leg value, exchange and SEBI on turnover, GST on brokerage + exchange + SEBI. Net = gross − charges. |
| Open legs | Unmatched fills are reported: carried overnight or the export is partial. |

### 5.2 Metrics

| Metric | Definition |
|---|---|
| Win rate | Trades with net > 0 ÷ all trades. |
| Avg win / avg loss | Mean net of winners / mean absolute net of losers. |
| Realised R:R | Avg win ÷ avg loss. Compare with the 1:10 target. |
| Profit factor | Gross profit of winners ÷ gross loss of losers. |
| Expectancy | Net ÷ trades. |
| Hold time | Minutes entry to exit, split by winners and losers. |
| Concentration | Best trade's net ÷ sum of winning nets. Also report net without the best trade. |

### 5.3 Splits that matter

| Split | Why |
|---|---|
| BEFORE 12 vs AFTER 12, by **entry** time | The desk runs two different strategies. Never pool them. |
| LONG vs SHORT | After 12 the desk shorts with the exact mirror logic. |
| SIGNAL exit vs SQUARE-OFF | Square-off = exit at or after 15:00, or 3+ symbols exiting in the same second (timer, not logic). A winner that only closed on the timer is a signal that never fired. |
| Rejected orders | From the order book: symbol, side, qty, time, broker reason. Fills-only feeds cannot show these. |

### 5.4 Rule check (which rule cost the money — the point of the report)

| Check | Breach condition |
|---|---|
| SIZE | Exposure > ₹10,000 per stock (2% tolerance). |
| UNIVERSE | Symbol outside Nifty 500. |
| WINDOW | Exit after 15:00: the square-off did the work, not the signal. |
| ASYMMETRY | Avg loss > avg win. The one that compounds. |
| DISCIPLINE | Losers held > 1.3× as long as winners. |
| COSTS | Charges > 25% of gross on a positive day: sizes too small for the frequency. |
| OPEN | Unmatched legs. |

### 5.5 Reading a day of the algo's orders

- Orders sharing the same second across symbols are timer-driven (candle close, square-off), not discretionary.
- Count REJECTED and read `rejreason`: margin, scrip restrictions, RMS. Each is capital that never got deployed.
- "Left on the table" = distance from exit price to the session extreme in the trade's direction, per trade. Only computable with intraday highs/lows.

## 6. Post-mortem record

### 6.1 2026-09-10 (49 trades, from Shoonya positions and order book)

| Item | Value |
|---|---|
| Trades | 49: 25 winners, 24 losers |
| Gross P&L (Shoonya, before charges) | +₹718.21 |
| Concentration | WELCORP = 51% of profit. Other 47 trades net −₹856.79. |
| Charges | ~₹480 at the real rate card (98 orders). Net ≈ +₹235. |
| Avg win / avg loss | ₹92 / ₹66. Losses were not "3× wins" (an earlier wrong claim). Problem is concentration and tail, not size of loss. |
| Hold | Winners 104 min, losers 54 min. Hold discipline fine. |
| Same-second orders | 32 of 64 orders in batches; 15:06:02 carried 8 orders = square-off. |
| Rejected | 3: ABDL, GALLANTT, EMCURE. |
| Left on table | ~₹1,476 via early exits. ATHERENERG captured ₹64 of ₹612 available. |
| After-12 shorts | 7 of 7 won, but all closed on the 15:06 square-off; the only signal exit (CARTRADE) lost. |

By entry time:

| Session | Trades | Win % | Net | PF |
|---|---:|---:|---:|---:|
| Before 12 | 15 | 40% | +₹483.90 | 1.55 |
| Before 12 ex-WELCORP | 14 | 36% | −₹692.90 | 0.21 |
| After 12 | 34 | 56% | +₹234.31 | 1.33 |

### 6.2 2026-09-09 market notes

- Nifty IT ~−3% on US NFP; 5 of top 5 losers IT. A macro print, missed because only corporate news was searched.
- ADANIENT +1.76% at session high on ₹148 cr: airport stake sale. Missed twice.
- Cash market (allSec): 9 names at +20% upper circuit, 2 at −20%. FOSec range +3.49% / −6.75%.

## 7. Strategy knowledge

### 7.1 The desk's system as of 2026-09-14

| Element | Rule |
|---|---|
| Higher-TF stack | Daily / 4H / 2H / 1H RSI alignment as backdrop (to confirm still sits above the blocks below). |
| 30-min block | RSI(14) vs WMA20(RSI14): separation gaps ≥ 3 (was 5), evaluated on the last **closed** bar `[-1]`, plus a rising block requiring `[-1] > [-2]` (was `[0] > [-1]`, which reads the forming bar — fix outstanding). |
| 15-min trigger | RSI(14) crosses WMA20(RSI14) in the trade direction. |
| Exit | 15-min EMA3(RSI) crosses below WMA20(RSI) (mirror for shorts). No fixed stop; the exit rule is the stop. Removed the earlier 5-min clause. |
| Shorts after 12 | Exact opposite logic, exact opposite exit. |
| Start time | Revised to **10:15**, not 09:30 and not 12:00 (see 7.2). |

### 7.2 Indicator formation math (why 10:15)

| Indicator | Bars needed | Earliest valid same-day time |
|---|---:|---|
| 30-min RSI(14) | 14 closed bars | Never same-day; carries from prior sessions. |
| A 30-min cross (needs 2 closed bars after open) | 2 | **10:15** |
| 5-min WMA20 of RSI(14) | 34 closed bars | 12:05 |

Uday's argument for an earlier start: higher timeframes are already formed and in sync at the open; morning noise means the 30-min will not sync until later anyway; more of the move is captured. Conceded, with 10:15 as the first honest 30-min cross.

### 7.3 Market microstructure facts the system fights or rides

- At 5–30 minute horizons, returns show negative serial correlation: mean reversion is the base rate. A continuation-momentum system fights it unless a higher-TF trend stack is behind it. That stack is what makes intraday momentum viable.
- Momentum as an anomaly is a monthly effect (Jegadeesh–Titman), not an intraday one.
- Time-of-day volume is U-shaped; compare volume to the same-slot average, not the day average.

### 7.4 Top-three technical inputs for intraday, in order

| Rank | Input | Use |
|---|---|---|
| 1 | Volume, relative to time-of-day average | Gate: trigger bar ≥ 1.5× its slot average. |
| 2 | Market structure: PDH/PDL/PDC, opening range, VWAP, break of structure | Gate: longs only above VWAP, shorts only below. |
| 3 | Momentum as divergence | Early exit when price makes a new extreme and RSI does not. |

Suggested additions not yet implemented: the three gates above; log MAE per trade; log exit-on-signal vs square-off per trade.

### 7.5 Sector and news reading

- Gap > 3% with volume = news. Search it, attach the cause, then judge whether it is priced.
- Sector events with a macro cause (rates, payrolls, crude, INR) show up across a whole sector in the losers list; a corporate feed will never explain them.
- An oversold sector in a confirmed macro down-move is not a squeeze candidate at 10:00.

## 8. Tooling map (only if the repo is used)

| File | Purpose |
|---|---|
| `AGENT.md` | Operating charter: persona, standing rules, output style. |
| `CONTEXT.md` | Living business facts and change log. |
| `fetch_movers.py` | Pull NSE gainers/losers (allSec, FOSec, NIFTY) to `data/<date>/`. |
| `screen.py` | Nifty 500 live screen with the mandatory SEARCH LIST. |
| `analyze_trades.py` | FIFO pairing, partial merge, rate-card charges, metrics, rule check. Reads Shoonya JSON or CSV. |
| `dashboard.py` | Builds `reports/dashboard.html` (charts) and `reports/README.md` (GitHub-rendered) from all days. |
| `daily_report.py` | Unattended: Shoonya login, three books, analysis, dashboard, commit, push. `--file` backfills from a web CSV export. |
| `connect.py` | One-time setup on an India machine: credentials to `.env`, connection test, first report, 15:35 IST schedule. |
| `shoonya_mcp.py` | Read-only Claude custom connector (status, tradebook, orderbook, positions, report). Needs `mcp>=2`, `uvicorn`, a tunnel, and registration under Customize → Connectors → Add custom connector. |
| `data/nifty500.txt` | Universe list. |

State on 2026-09-24: everything built and tested against stand-in servers; nothing yet run on an India machine, so Claude has never actually been connected to Shoonya.

## 9. Change log

| Date | Change |
|---|---|
| 2026-09-04 | Agent created. |
| 2026-09-09 | Standing rules: search before "no news"; macro before corporate. |
| 2026-09-10 | Five-bullet answers; tables required; universe pinned to Nifty 500; NSE access working; movers fetch and screen; trade analyzer and daily report. |
| 2026-09-14 | Dashboard; `flqty` vs `fillshares` fix; partial-fill merge; WINDOW cutoff 15:00; Shoonya API confirmed India-fenced; `connect.py`; TOTP without dependencies; Shoonya-direct primary then OpenAlgo removed entirely; real rate card (₹5 cap, not ₹20); charges by component; rejected orders; Claude custom connector server. |
| 2026-09-24 | This knowledge base written for use outside Claude Code. |
