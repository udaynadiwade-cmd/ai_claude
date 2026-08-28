# The smallest piece of importing we can do

**Date:** August 2026 · **Status:** recommendation
**Question:** what is the smallest, cleanest part of the import process to start with?

---

## Every step, checked

| Step | Our money at risk? | Licence needed? | Can we do it from a desk in Hyderabad? | Verdict |
|---|---|---|---|---|
| **Sourcing** — find supplier, check them, get price | **No** | **No** | **Yes** | **Start here** |
| **Quality check** — inspect goods before shipping | No | No | **No — needs people in China** | Later |
| **Freight** — book the shipping | No, if we only resell | No | Yes | Thin margin, crowded |
| **Customs clearance** | No | **Yes — CHA licence** | Yes | Blocked |
| **Delivery** in India | No | No | Yes | Commodity, no margin |
| **Payment / foreign exchange** | Yes | **Yes — RBI regulated** | Yes | Blocked |

**Two steps are legally closed to us today:** customs clearance needs a Customs House
Agent licence, and cross-border payment is RBI-regulated.

**One step needs staff in China:** quality inspection. Third-party inspectors charge
**$149–$320 per man-day** (QIMA charges $290–$700). `FACT` That is a real business,
but not one we can run from Hyderabad on day one.

**That leaves sourcing.**

---

## The recommendation — sourcing only, goods never touched

**What we sell:** send us a product. We come back with verified suppliers and the full
landed price in rupees.

**What we do NOT do:** buy the goods, ship them, clear them, or handle the money.

### Why this is the smallest clean thing

- **No money locked up.** We never own stock. Nothing sits on water for 6 weeks.
- **No licence needed.**
- **No customs risk.** We are not the importer of record.
- **No delivery risk.** No damaged goods, no returns.
- **Done from a desk.** No China office, no warehouse.
- **Uses what we already have** — the 1688 and Alibaba API, plus two years of knowing
  what a real supplier looks like.
- **Can start this week.** Nothing to build.

### What the market pays

- Sourcing agents charge **3% to 10% of order value** `FACT`
- Inspection alone runs **0.6–1.2% of order value** `FACT`

**Better for us: charge a flat fee per request, not a percentage.** A flat fee gets
paid whether or not the customer places the order. A percentage only pays if the deal
closes, which puts our income in the customer's hands.

---

## The one real weakness, stated plainly

**If we give the supplier's name, the customer can go direct next time.**

Three ways to handle it, in order of honesty:

1. **Charge upfront, accept defection.** We are paid for the work regardless. Some
   customers will come back for the harder jobs. This is clean and simple.
2. **Give the quote and the supplier's capability, but hold the name until they
   commit.** Protects us, but feels like a hostage negotiation and customers dislike it.
3. **Pretend defection will not happen.** It will. Do not plan on this.

**Recommended: option one.** Take the money upfront, do good work, let the relationship
earn the repeat business. Trying to trap customers in a service business rarely holds.

---

## The hidden benefit — this is a data machine

Every request tells us:
- What Indian businesses actually want to import
- Which products get asked about again and again
- Who asks repeatedly

**That is exactly the data the bigger model needed and did not have.** The earlier
catalog plan had one fatal gap: to launch our own brand we need many customers buying
the same product, and we had no way to find out what that product was.

This small service answers that question for us, and **customers pay us while we learn
it.** That is a better position than building a large free catalog and hoping the data
shows up.

---

## Honest limits

- **It will not make much money.** At a few thousand rupees per job, a hundred jobs is
  a few lakh. This is a starting point, not the business.
- **It does not use our logistics or customs experience** — the most expensively-earned
  skill we have sits idle in this version.
- **It is easy to copy.** Any sourcing agent does this. Our edge is speed from the API
  and honesty about landed cost, not something structural.

**So treat it as step zero, not the plan.** Its job is to earn a little, risk nothing,
and produce the demand data that decides the real category.

---

## First 30 days

1. **Pick a price.** One flat fee per sourcing request. Simple, published, no
   negotiation.
2. **Go to the existing ~100 clients first.** They already trust us. Offer it to them
   before anyone else.
3. **Do 20 requests properly.** Every one done well, on time, with a real landed price.
4. **Record every request in one sheet:** who asked, what product, did they order, did
   they come back.
5. **After 20, read the sheet.** If the same product appears more than twice, that is
   the first real signal about what to build next.

---

## Sources

- [China inspection pricing 2026 — $149–320 per man-day](https://mindensourcing.com/china-quality-inspection-service-cost)
- [QIMA pricing $290–700 per man-day](https://xilinkglobaltrade.com/qima-inspection-pricing-2026/)
- [China sourcing agent commission 3–10% of order value](https://goodcantrading.com/china-buying-agent-guide-2026/)
