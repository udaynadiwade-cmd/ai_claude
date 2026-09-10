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
