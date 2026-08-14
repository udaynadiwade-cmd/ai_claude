# Inventory pooling — your idea, screened

**Date:** August 2026 · **Status:** model evaluation and category screen
**The idea:** take over clients' inventory of standardised, high-value stock and hold it
centrally; because one pool serves many businesses, turns rise and their capital is
freed.

---

## First — you are right, and you are right about why my model was weak

Pooling gain is not uniform across categories. It scales roughly with:

> **(item value × demand uncertainty) ÷ cost of holding**

Cheap items with predictable consumption produce almost no pooling gain, because
over-holding them is already cheap. **Expensive items with lumpy, unpredictable demand
produce enormous pooling gain**, because that is exactly where a business is forced to
hold insurance stock it will not use for months.

Electrical fittings are the first kind. **The category I recommended is precisely the
one where your mechanism does least work.** That criticism lands.

---

## Your idea has a name and a proven industry

**The principle is risk pooling.** Under independent demand, the safety stock needed to
hit a given service level scales with the *square root* of the number of demand streams
pooled. Serving 25 customers from one pool needs roughly **one-fifth** the safety stock
of 25 separate pools at the same service level. `STATISTICAL PRINCIPLE — the square-root
law; the practical gain is smaller because cycle stock does not pool as cleanly.`

**The industry is metals service centres**, and the trade literature describes them in
almost exactly your words: they exist *"because of the focus on just-in-time inventory
management and materials management outsourcing in the capital goods and related
industries."* `FACT`

Scale and margins:

| | Revenue | Gross margin |
|---|---|---|
| **Reliance Steel** | ~$14 Bn | **29.7%** (Q1 2025, non-GAAP) `FACT` |
| **Ryerson** | $5.1 Bn (2023) | 17.1% (FY2025) `FACT` |
| **Kloeckner Metals** | $4.1 Bn (2023) | — |

**Reliance Steel earns 29.7% gross margin distributing a commodity.** Compare with
OfBusiness at 2.7% net and Infra.Market at 1.2%. The difference is not the product. It
is that a service centre sells *availability and processing*, not steel.

### And it answers the objection I would otherwise raise

I would have said: holding steel makes you long steel. The research answers it directly
— service centres *"that emphasize rapid inventory turnover and minimal contract sales
are generally less vulnerable to changing metals prices than metals producers."* `FACT`

**Turn ratio is the hedge.** At 4 turns your average holding is 90 days of price
exposure; at 12 turns it is 30. The same mechanism that creates your margin advantage
also shrinks your commodity risk. That is an unusually clean piece of business design
and it is the strongest argument for the whole idea.

---

## The arithmetic, made concrete

Twenty-five fabricators, each holding ₹40 lakh of steel against ₹1.6 Cr of annual
consumption:

```
INDIVIDUALLY
  Inventory held         25 × ₹40 L   =  ₹10.0 Cr
  Annual consumption     25 × ₹1.6 Cr =  ₹40.0 Cr
  Turns                                     4.0×

POOLED
  Inventory required     ~35–45% of sum =  ₹3.5–4.5 Cr   [ESTIMATE]
  Same consumption                      =  ₹40.0 Cr
  Turns                                     ~10×

  Capital released to customers         =  ₹5.5–6.5 Cr
  Gross profit @15% on ₹40 Cr           =  ₹6.0 Cr
  Gross return on ₹4 Cr of inventory    =  150%
```

**You free ₹6 Cr of their working capital and your own capital works two and a half
times harder than theirs did.** Both sides win, which is why this is a proposition
rather than a negotiation.

---

## The opening move that makes it capital-light

Do not buy new stock. **Buy theirs.**

> *"You have ₹18 lakh of bearings on your shelves. Most has not moved in two years. We
> will buy it at book value today, and guarantee any of it back to you within four
> hours, forever."*

For the plant: cash today, shelf space back, no stockout risk.
For you: **inventory at cost with zero procurement lead time, a customer, and their
consumption history — all in one transaction.**

Your first ₹2 Cr of stock can come from a dozen factories' dead inventory rather than
from a supplier. It is the most capital-efficient start available to this model, and it
is also the single most persuasive sales pitch in it.

**Caveat:** you are buying stock that may be obsolete, damaged or slow for a reason.
Inspect, apply a haircut, and refuse the genuinely dead lines.

---

## What makes a category good for pooling

1. **High inventory value per customer** — the capital release must be worth a meeting
2. **Fungible specification** — the same item serves many buyers, unmodified
3. **Lumpy, unpredictable individual demand** — this is what forces them to over-hold
4. **Slow individual turns** — the arbitrage exists only if they are slow and you are fast
5. **No obsolescence** — you inherit the risk they are shedding
6. **Severe stockout cost** — proves they are over-holding today, and prices your service
7. **Fast to deliver** — you must be able to replace their shelf within hours
8. **Not already consolidated** — no incumbent running this model at scale

---

## The screen

Scored 1–5, higher is better.

| Category | Value | Fungible | Lumpy | Slow turns | No obsol. | Stockout cost | Deliverable | Open | **Total** |
|---|---|---|---|---|---|---|---|---|---|
| **Bearings, seals, power transmission** | 4 | **5** | **5** | **5** | 5 | **5** | **5** | 4 | **38** |
| **Industrial valves, pipes, fittings** | 5 | 4 | 4 | 5 | 5 | 5 | 3 | 4 | **35** |
| Machinery critical spares | 5 | 2 | 5 | 5 | 4 | 5 | 4 | 4 | 34 |
| Aluminium, copper, brass sections | 4 | 5 | 4 | 4 | 5 | 4 | 3 | 4 | 33 |
| **Steel — sheet, plate, structurals** | **5** | **5** | 4 | 4 | 5 | 4 | 3 | 2 | **32** |
| Electronic components | 4 | 4 | 4 | 4 | **1** | 4 | 5 | 3 | 29 |
| Industrial fasteners | 2 | 5 | 3 | 3 | 5 | 3 | 5 | 2 | 28 |
| Textiles — yarn, grey fabric | 5 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 27 |
| Plywood, laminates, boards | 4 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 26 |

`ASSUMPTION` — the framework is defensible; the individual scores are debatable and
worth arguing with.

---

## The top three

### 1 — Bearings, seals and power transmission · the best pooling mechanics available

**India market: $5.2 Bn (2025) → $12.0 Bn (2034), 9.69% CAGR.** `FACT`

Why it scores highest on the mechanism itself:

- **Perfectly fungible.** Bearing numbering (6205, 22210, 32011) is a global standard.
  The same part serves any customer with that shaft size — no modification, no spec
  negotiation. **Nothing else on this list is this fungible.**
- **Demand is maximally lumpy.** Nobody knows when a bearing will fail. That is the
  textbook condition for pooling gain.
- **Individually glacial, collectively fast.** A plant may hold 200 SKUs and consume 20
  a year. Pooled across 30 plants, most of those SKUs move monthly.
- **Stockout is catastrophic and quantified.** A failed bearing stops a line. The plant
  manager can tell you the cost per hour, which means he can price your service himself.
- **Small, light, van-deliverable.** Four-hour replacement is genuinely achievable.
- **No obsolescence, stable pricing.** You inherit almost no risk from holding it.

**The counterfeit angle doubles the proposition.** Fake SKF and FAG bearings are endemic
in India. A pooled inventory with verified provenance sells authenticity and availability
in the same conversation — the two things B2B buyers actually pay for.

*Caveats:* brands control authorised channels; Moglix and others sell bearings
transactionally. **Nobody appears to run the buy-their-stock consignment pooling model.**
`ASSUMPTION — verify before committing.`

### 2 — Industrial valves, pipes and fittings

High value, spec-standardised, held as project and maintenance insurance, no
obsolescence, severe stockout cost. Loses to bearings only on deliverability — bulkier,
so the four-hour promise is harder. Genuinely open.

### 3 — Steel service centre · your own example

**The biggest market and the strongest global proof** — 125 Mt of Indian consumption a
year, about a third going into fabricated products `FACT`, and a $14 Bn US comparable
earning 29.7%.

It ranks fifth on the screen for two reasons, both real: **OfBusiness and Zetwerk are
already in steel**, and physical handling — cranes, cutting, slitting, flatbed transport
— makes it a capital-heavy, slow-to-start business rather than a van-and-a-warehouse
one. Indian service centres are also regionally concentrated, notably around Ludhiana.
`FACT`

**Steel is the better business at ₹1,000 Cr. Bearings is the better business to start.**

---

## What kills it

1. **Fungibility failing in practice.** If customers demand *their* brand, their batch,
   their certificate, the pool fragments into 30 private stockpiles and the whole gain
   disappears. **This is the assumption to test first and hardest.**
2. **Buying dead stock.** Their unused inventory may be unused because it is unusable.
   Inspect ruthlessly; take a haircut; walk away from lines that have not moved anywhere.
3. **Adverse selection.** The customers keenest to hand you inventory may be the ones
   with the worst inventory. Price accordingly.
4. **Service-level failure.** The moment you miss a four-hour promise on a stopped line,
   that customer rebuilds his own shelf and never trusts you again. **Your fill rate is
   the entire product** — which is, again, the part your Six Sigma training actually wins.
5. **Working capital.** You are literally taking other people's inventory onto your
   balance sheet. The model releases *their* capital by consuming *yours*. Buying dead
   stock cheaply mitigates the start; it does not solve scale.
6. **Brand channel conflict.** SKF and Schaeffler may not welcome a pooled distributor
   who reduces total channel inventory. Expect friction.

---

## What to test, and it is cheap

Ten factory visits in Hyderabad's industrial belts — Balanagar, Jeedimetla, Patancheru,
Cherlapally. Five questions:

1. **"What is the rupee value of spares sitting on your shelves right now?"**
2. **"How much of it hasn't moved in a year?"** — this is the pooling opportunity, measured
3. **"What does an hour of downtime cost you?"** — this prices your service
4. **"If I bought that stock today at book value and guaranteed four-hour replacement
   forever, would you sell it to me?"** — the whole business in one question
5. **"Would you accept an equivalent part from a different approved brand?"** — the
   fungibility test, and the one that decides whether this works at all

If question 4 gets a yes and question 5 gets a yes, you have a business — and unlike
everything else in this series, **you would be starting with revenue from day one,
because the first transaction is you buying, not selling.**

---

## Sources

- [Metals service centre model, industry structure, and price-exposure characteristics](https://matrixbcg.com/blogs/competitors/rsac) · [Reliance Steel 10-K filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000861884) · [Ryerson FY2025 results](https://www.prnewswire.com/news-releases/ryerson-reports-fourth-quarter-and-full-year-2025-results-302693098.html) · [Ryerson strategy and business model](https://umbrex.com/resources/company-profiles/ryerson-holding-corporation/)
- [India bearings market — $5.2 Bn 2025 to $12.0 Bn 2034, 9.69% CAGR](https://www.imarcgroup.com/india-bearings-market) · [Ken Research on India bearings](https://www.kenresearch.com/industry-reports/india-bearings-market)
- [India steel consumption and service centre development](https://www.niir.org/blog/steel-business-india-2026/) · [India metal fabrication market structure](https://www.mordorintelligence.com/industry-reports/india-metal-fabrication-market)
