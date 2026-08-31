# CJdropshipping — is it real, and does it cover India duty and GST?

**Date:** August 2026 · **Status:** verification
**Question:** is CJdropshipping a genuine China-to-India dropshipping route, and do
they include customs duty and GST?

> **Note on method:** `cjdropshipping.com` is blocked by this environment's network
> egress policy, so I could not open the site directly. Everything below comes from
> indexed copies of CJ's own pages (user agreement, warehouse list, shipping-method
> articles), plus Indian customs sources. Confirm the CJ policy lines on their live
> site before acting.

---

## Short answer

**Yes, it is a real dropshipping company. No, it does not include duty or GST.**

Their user agreement is explicit: **the user pays all tariffs and taxes.** If customs
holds a parcel because import duty or VAT was not paid, **the user bears it alone.**
`FACT`

That is a **DDU** arrangement — Delivered Duty Unpaid. The tax bill lands on whoever
receives the parcel in India.

---

## What CJdropshipping actually is

| | |
|---|---|
| Model | Dropshipping supplier + fulfilment agent. Sourcing, warehousing, print-on-demand, and shipping under your brand |
| Warehouses | **50+ worldwide** `CLAIM`. Named: China, USA, Germany, Thailand, Indonesia, plus partner warehouses in UK, Australia, France `FACT` |
| **India warehouse** | **None found.** Every India order ships from China. |
| Countries served | 60+ `CLAIM` |
| India route | **CJPacket** line, then **India Post or a private courier** does last-mile `FACT` |
| Delivery time to India | **7–40 days** depending on service. Registered around 15 days `CLAIM` |

---

## The duty and GST position, stated plainly

### 1. India has no duty-free threshold

**India's de minimis is ₹0.** `FACT` Every single imported item is liable for basic
customs duty and import tax. There is no small-parcel free pass the way some countries
have.

### 2. What a parcel actually costs on arrival

| Charge | Rate |
|---|---|
| Basic Customs Duty | **20%, cut to 10% for personal courier imports from April 2026** `FACT` |
| Social Welfare Surcharge | 10% of the duty `FACT` |
| **IGST** | Usually **18%** `FACT` |
| Courier handling fee | **₹500–₹1,500** `FACT` |

**Old total: roughly 40–50% of value.** `FACT`
**After the April 2026 BCD cut: roughly 30–35%.** `ESTIMATE` — my arithmetic on the
new 10% rate, not a published figure.

### 3. Who pays it

**The receiver.** `FACT` In a CJ dropship order, the receiver is **your Indian
customer, at their door.**

---

## The three things that break this model in India

### 1. Cash on delivery dies

Most Indian online buyers want COD. A CJ parcel arrives with a **separate customs
demand the customer never agreed to.** They refuse it. You have paid for the goods and
the freight and got nothing back.

### 2. Your customer becomes the importer

The parcel is addressed to them, so **they are the importer of record**, not you.
That has a tax consequence most people miss:

**You cannot claim input tax credit on the IGST paid at import**, because the import
document is not in your name. `ESTIMATE` — this follows directly from how GST input
credit works, but confirm with a CA before building on it. Meanwhile **you still owe
GST on your sale to the customer.** You are taxed on the way in and again on the way
out, with no credit joining them.

### 3. Speed

**7–40 days** against Amazon's two. `FACT` For any product an Indian buyer can get
locally, that is not a competitive offer.

---

## Reported problems worth knowing

- Parcels **stuck in transit for over a month** with tracking frozen at the arrival
  airport `CLAIM` — customer reviews
- **Prices changed after the order was placed**, with extra charges notified more than
  7 days later `CLAIM` — customer reviews
- Generic support responses with no ownership of the problem `CLAIM`
- Reviews are mixed, not uniformly bad. Some India-based users report good support.
  `CLAIM`

`CLAIM` throughout because these are user reviews, not verified incidents. Treat as
signal about the failure modes, not as proof of frequency.

---

## What this means for Befach

**CJ's model is the exact opposite of the one we have been designing.**

| | CJdropshipping | What we are building |
|---|---|---|
| Who handles customs | **The customer, alone** | **Us** |
| Landed price | **Unknown until the parcel arrives** | **Fixed and quoted upfront** |
| Who is importer of record | The end customer | Us |
| What happens if duty is higher than expected | Customer pays, or refuses the parcel | **We absorb it** |

Our whole promise is *"it will clear customs, it will meet Indian rules, and the landed
price will be what we quoted."* **CJ's terms say customs is your problem.** That is not
a competitor to worry about. It is confirmation that the gap we identified is real, and
that even a large, well-funded China-side operator has not closed it.

### Is CJ useful to us at all?

**As a per-parcel dropship route into India: no.** It fails on duty transparency, COD,
speed and input tax credit.

**As a sourcing and fulfilment supplier: possibly yes.** If **Befach is the importer of
record** and brings goods in as one consolidated commercial import under our own IEC —
duty paid by us, IGST creditable to us, landed cost known before we quote — then CJ is
just another China-side sourcing and packing partner to price against 1688 and direct
factories. **The problem is the parcel-by-parcel dropship structure, not the company.**

---

## What to verify before using them

1. Open the live site and read the current user agreement clause on tariffs — mine is
   from an indexed copy
2. Ask CJ directly whether they offer a **DDP** (duty-paid) line to India. If they do,
   the whole picture changes and this note needs rewriting
3. Confirm the input-tax-credit point with a CA before treating it as settled
4. Price a consolidated commercial import through them against 1688 and direct factory
   quotes for the same SKU

---

## Sources

- [CJdropshipping user agreement — tariffs and taxes borne by the user](https://cjdropshipping.com/user-agreement)
- [CJ Dropshipping policy — customs detention responsibility](https://blog.cjdropshipping.com/detail/cj-drop-shipping-policy/)
- [CJ warehouses home and abroad](https://cjdropshipping.com/article-details/146)
- [CJ Packet tracking to India — India Post and private courier last mile](https://couriertrackingz.com/cj-packet-tracking/)
- [CJ Packet carrier profile](https://carriers.aftership.com/cjpacket)
- [CJdropshipping shipping times and costs](https://www.dropshippinghustle.com/cj-dropshipping-shipping-times/)
- [CJdropshipping Trustpilot reviews](https://www.trustpilot.com/review/cjdropshipping.com)
- [CJdropshipping Shopify app reviews](https://apps.shopify.com/cucheng/reviews)
- [India de minimis is ₹0 — all imports dutiable](https://www.stackry.com/duties-and-taxes/india)
- [India import duty and taxes guide — DHL](https://www.dhl.com/discover/en-my/logistics-advice/import-export-advice/guide-to-import-duty-and-taxes-in-india)
- [Customs duty and import-export taxes in India — India Briefing](https://www.india-briefing.com/doing-business-guide/india/taxation-and-accounting/customs-duty-and-import-export-taxes-in-india)
- [Courier Imports and Exports Amendment Regulations 2026 — BCD on personal courier imports cut 20% to 10%](https://courierstoindia.com/india-international-courier-rules-2026/)
- [CBIC removes ₹10 lakh courier consignment cap](https://mundhraconsulting.com/current-updates/courier-imports-exports-amendment-regulations-2026/)
- [Dropshipping legal requirements in India — IEC, GST, IGST](https://www.shiprocket.in/blog/dropshipping-legal-requirements/)
- [Is dropshipping legal in India — GST and tax guide](https://qikink.com/blog/what-are-dropshipping-legal-requirements-in-india/)
