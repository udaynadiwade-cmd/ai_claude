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

- **NSE access WORKS as of 2026-09-10.** The environment network policy was widened; `nseindia.com` no longer 403s at the proxy. NSE itself still fronts Cloudflare — it resets HTTP/2 and answers the first request with 403 while setting cookies, so `fetch_movers.py` uses HTTP/1.1 + browser headers and reads the 403 body to complete the handshake. Run it directly in-session.
  is a strict allowlist (GitHub + package registries only). NSE, BSE, Yahoo
  Finance, Moneycontrol, Trendlyne, Groww, Upstox and Kite all return
  `403` on CONNECT. This is set at environment level and cannot be fixed
  from inside a session — don't waste a turn retrying it.
- **`WebSearch` still works** (it runs server-side, not through the sandbox
  proxy). `WebFetch` does not, for any blocked host. So news lookups are
  possible; live price fetches are not.
- **The working data path** is `fetch_movers.py` in this folder: run it on a
  machine that has NSE access, commit the output to `business-onlooker/data/`,
  push. Claude reads it from the repo, which *is* reachable.
- Manual fallback that also works: download the CSV from the NSE page in a
  browser and upload it into the chat directly.
- Longer term the right source is the desk's own **OpenAlgo instance**, not
  NSE's website — it's authenticated, doesn't fight Cloudflare, and serves
  intraday OHLCV the public page never exposes.

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
