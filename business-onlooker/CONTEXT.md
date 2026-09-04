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
