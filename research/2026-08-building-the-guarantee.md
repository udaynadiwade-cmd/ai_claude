# Building an import guarantee for Indian buyers

**Date:** August 2026 · **Status:** roadmap
**Question:** can we copy Alibaba's Trade Assurance? Can we do it back-to-back with them?

---

## The finding that changes the whole plan

**Alibaba's Trade Assurance does NOT cover the risks Indian buyers actually fear.**

### What it covers `FACT`
- Supplier did not ship
- Product does not match the specification written in the purchase order

### What it does NOT cover `FACT`
- **Customs holds and customs seizure**
- **Regulatory failure** — if goods fail BIS, CE, FCC and customs detains them, **no
  dispute process covers it**
- Shipping delays in transit
- Subjective quality — colour shade, feel
- Payments made off the platform
- Buyer's remorse
- Indirect damages

### How a claim works `FACT`
- File within **30 days of delivery** — after that, coverage is gone
- Supplier gets **3 days** to settle directly
- Auto-escalates to Alibaba mediation after **7 days**
- **Quality claims require a third-party inspection report**

### The most important line
**Trade Assurance is not insurance. It is a dispute resolution process.** It sets no
quality standard of its own — it only enforces what the buyer wrote into the contract.
Vague specification, weak claim.

---

## Why back-to-back with Alibaba only half works

**The idea:** Befach buys on Alibaba using Trade Assurance, then resells to the Indian
buyer with our own guarantee. Alibaba covers us upstream.

**Where it works:** it genuinely protects us against a Chinese supplier who does not
ship, or ships the wrong goods. That is real and worth using on every order.

**Where it fails — and this is the whole problem:**

| Risk | Who fears it | Covered by Trade Assurance? |
|---|---|---|
| Supplier does not ship | Us | **Yes** |
| Wrong product sent | Us | **Yes** |
| **Stuck at Indian customs** | **The Indian buyer** | **No** |
| **Fails BIS / QCO, gets detained** | **The Indian buyer** | **No** |
| **Wrong HS code, duty higher than quoted** | **The Indian buyer** | **No** |
| **Landed cost higher than promised** | **The Indian buyer** | **No** |

**Everything the Indian buyer is actually afraid of happens after the goods reach
India — and Alibaba covers none of it.**

So back-to-back is a **useful input, not the product.** Use it to protect ourselves.
It does not create the guarantee our customer wants.

---

## The real opportunity, stated plainly

**Guarantee exactly what Alibaba refuses to guarantee.**

That is: **it will clear customs, it will meet Indian regulations, and the landed price
will be what we quoted.**

Nobody offers this. Alibaba explicitly excludes it. IndiaMART does not touch
transactions at all. And it is precisely what our two years and 100–150 shipments
taught us how to control.

**This is a much better USP than copying Trade Assurance**, because it is built on
knowledge we already have rather than on a mechanism we would have to license.

---

## The escrow route is closed — do not plan around it

To hold a customer's money in escrow in India, we would need an **RBI payment
aggregator licence.** `FACT`

| Requirement | Figure |
|---|---|
| Net worth at application | **₹15 crore** |
| Net worth within 3 years | **₹25 crore** |
| Escrow must sit with | A Scheduled Commercial Bank |
| Structure | Company incorporated in India |

**₹15 crore of net worth rules this out for now.** Stop considering escrow as a
starting move.

---

## The roadmap that actually works

### Phase 1 — Become the seller, not the middleman `no licence needed`

**We buy from the Chinese supplier. We sell to the Indian buyer. Two separate
transactions.**

This one structural choice solves the regulatory problem completely:
- We never hold anyone else's money, so **no payment aggregator licence is needed**
- Our "guarantee" is simply our own sale terms — the same as any seller's warranty
- The customer's counterparty is us, an Indian company they can reach and sue

**What we promise in writing:**
1. **Landed price is fixed.** If duty or freight comes in higher than quoted, we absorb
   it. This is the headline promise and the one nobody else makes.
2. **Customs clearance is our job.** If it is held for our paperwork error, we fix it at
   our cost.
3. **Compliance checked before order.** We confirm the product is not under a QCO and
   has valid BIS status before a rupee is spent.
4. **Replacement or refund** if goods do not match the agreed specification.

**What we must NOT promise:**
- Delivery date to the day — port congestion is outside anyone's control
- Anything about subjective quality unless it is written into a specification sheet
- Cover for the customer changing their mind

### Phase 2 — Cap our own risk `months 3–9`

- **Use Alibaba Trade Assurance on every purchase** we make, so China-side risk sits
  upstream with them
- **Write tight specification sheets** on every order — Trade Assurance enforces the
  contract, so a weak spec means no claim
- **Buy third-party inspection** where order value justifies it. Inspection costs
  0.6–1.2% of order value, and a quality claim is not even accepted without an
  inspection report
- **Price the guarantee in.** If we absorb duty variance, add a few percent to cover it.
  A guarantee is an insurance product and must be priced like one.

### Phase 3 — Only after real volume `year 2+`

- **Trade credit insurance** to cover larger orders, once volumes justify the premium
- **A licensed payment aggregator partner** if we want genuine escrow without holding
  the licence ourselves
- Consider the RBI licence only if net worth genuinely reaches ₹15 crore

---

## How to prove it works before betting on it

Do not build a platform. Run this on the next **20 orders** manually.

1. Offer the fixed-landed-price guarantee to the existing ~100 clients
2. **Record every order: quoted landed cost vs actual landed cost**
3. After 20 orders, look at the gap
   - If our quotes are accurate within 2–3%, the guarantee is cheap and we should
     advertise it loudly
   - If the gap is 10%+, the guarantee would bankrupt us and our pricing needs work
     before we promise anything

**That number — quoted versus actual — is the whole business case.** It costs nothing
to collect and it decides everything.

---

## Sources

- [Trade Assurance — what it covers and does not, customs and regulatory exclusions](https://www.aqualora.us/blog/alibaba-trade-assurance-explained)
- [Trade Assurance gaps for importers](https://milasourcing.com/news/alibaba-trade-assurance-what-it-covers/)
- [Claim process — 30 day window, 3 and 7 day escalation, inspection requirement](https://guidedimports.com/blog/alibaba-trade-assurance-overview/)
- [RBI Regulation of Payment Aggregators Directions, 2025 — net worth requirements](https://sarafpartners.com/rbi-issues-the-reserve-bank-of-india-regulation-of-payment-aggregators-directions-2025/)
- [Payment aggregator escrow rules — AZB Partners](https://www.azbpartners.com/bank/payment-aggregators-and-gateways-indias-regulatory-framework/)
- [China inspection cost as % of order value](https://mindensourcing.com/china-quality-inspection-service-cost)
