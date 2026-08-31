# Daily Water Scout — standing 9am email

**Set up:** 31 August 2026 · **Status:** live
**Routine ID:** `trig_011vQhAiS9FnULhiKmKcBRzV`
**Fires:** `27 3 * * *` UTC = **08:57 IST, every day**
**Delivers to:** uday.nadiwade@gmail.com

---

## What it does

Every morning a fresh session searches the web for **water-category products Befach
could import and sell in India**, alongside the D'Cal softener line, and emails a short
brief.

## The four filters — a product only makes the email if it passes all of them

1. **Innovative** — not a commodity every Indian trader already stocks
2. **High India demand** — real evidence (Indian retail listings, Indian prices, Indian
   market data), never a guess
3. **Importable** — asset-light, low MOQ, no heavy inventory commitment
4. **Compliance-clean** — anything needing BIS or QCO gets flagged, not buried

## Scope

Softeners, descalers, salt-free conditioners, resin, salt · shower/tap/whole-house
filters and cartridges · water tank IoT (level controllers, overflow cut-off, leak
detectors, auto shut-off valves, smart meters) · pumps, boosters, valves, fittings, RO
spares · testing kits, TDS and hardness meters · anything genuinely new in water tech.

## Standing compliance rules baked into the prompt

| Product | Rule |
|---|---|
| **RO point-of-use purifiers** | **DO NOT TOUCH.** BIS under **IS 16240:2015** is mandatory before import. Scheme-I takes **4–6 months** with factory inspection. `FACT` |
| **Mains-powered water appliances** | **Always flag.** May fall under the **90+ electrical appliance QCO enforced from 1 October 2026**. `FACT` |
| Non-electrical filters, magnetic descalers | Clean to import — no QCO |

---

## Two known limits

### 1. Alibaba and Amazon are blocked

`alibaba.com`, `amazon.in`, `amazon.com` and `dcal.co.in` are all blocked by this
environment's network egress policy. **The scout cannot browse listings directly.**

It uses web search instead, which does surface Alibaba showroom and supplier pages
along with prices and MOQs. That is enough to shortlist — but **every price in the
email is indicative and must be confirmed on the supplier page before acting.**

### 2. The email path depends on the connector

The routine could not be given the Gmail connector — this environment does not allow
connectors to be attached to a trigger from inside a session. So the routine has two
delivery paths:

- **If Gmail is available** in the fired session, it sends a formatted HTML email
- **If not**, it writes the full brief as its final message, and the routine's own
  **completion email** (push + email notifications are both ON) delivers that text to
  the inbox

**To get the properly formatted Gmail version every day**, recreate the routine from the
claude.ai Routines UI with the Gmail connector attached. The fallback still lands in the
inbox either way.

---

## Changing it

- **Different time:** the cron is in UTC. 9am IST = `30 3 * * *`. Currently set 3 minutes
  early to avoid the top-of-hour scheduling crowd.
- **Different scope, filters or format:** update the routine prompt, do not delete and
  recreate — that keeps the run history.
- **Stop it:** delete `trig_011vQhAiS9FnULhiKmKcBRzV`.

---

## First run — 31 August 2026

Sent manually to prove the pipeline. Findings:

| Product | Verdict |
|---|---|
| **Hard water shower filter** | **TOP PICK.** Compliance-clean, proven India demand at ₹1,499–1,899, sells on hair-fall not plumbing. The entry-level product our softener line lacks. |
| Water tank IoT level controller | $4–75, MOQ 1. Obvious pain. **Check the QCO list first** if mains-powered. |
| Salt-free magnetic descaler | ~$28–70. Answers the "cannot install a softener" objection. Never sell it as a softener replacement. |
| Smart leak detector + shut-off valve | WATCH. Good margin, thin volume. |
| Smart WiFi water meter | WATCH. Sold to a committee, long cycle. |
| RO purifiers | **DO NOT TOUCH** — BIS IS 16240:2015 |
