# Landed Cost — Assessment Order & Known Pitfalls

## The sequence

Customs assesses in a fixed order. Getting the order wrong changes the IGST base and therefore
the total outflow.

| # | Head | Base | Notes |
|---|------|------|-------|
| 1 | FOB | Commercial invoice | Converted at the **CBIC notified exchange rate** on the Bill of Entry date, not the bank card rate |
| 2 | Freight | Actual, per BL/AWB | Notional loading only where the actual is not ascertainable |
| 3 | Insurance | Actual policy premium | Notional loading only where the actual is not ascertainable |
| 4 | **Assessable Value (CIF)** | 1 + 2 + 3 | This is the value on which every ad-valorem duty is charged |
| 5 | BCD | AV | Rate from the CBIC tariff for the 8-digit ITC(HS), net of any effective-rate notification |
| 6 | AIDC | AV | Applies only to goods listed in the operative Finance Act schedule |
| 7 | SWS | BCD (see below) | 10% unless a notification exempts the item |
| 8 | ADD / CVD / Safeguard | AV or per-unit | Often **specific** (USD/MT), not ad valorem — read the notification |
| 9 | **IGST base** | 4+5+6+7+8 | Every customs duty stacks into the GST base |
| 10 | IGST | IGST base | Rate per the IGST rate schedule for the HSN |
| 11 | Compensation cess | IGST base | Only for cess-notified goods |

## Pitfalls that cost real money

- **Exchange rate.** Use the CBIC notified rate in force on the date of Bill of Entry presentation.
  Budgeting at the spot rate under-states landed cost.
- **SWS base.** SWS is levied on the aggregate of customs duties, not on IGST. Whether a particular
  cess (e.g. AIDC) sits inside the SWS base depends on the exempting notification — check it per
  item. The calculator exposes `sws_base` for exactly this reason; do not leave it on the default
  without checking.
- **Specific-rate anti-dumping duty.** ADD is frequently levied per metric tonne or per unit in USD.
  A percentage assumption here can be off by an order of magnitude.
- **Notional insurance/freight loadings.** Rule 10(2) of the Customs Valuation (Determination of
  Value of Imported Goods) Rules, 2007 prescribes loadings where the actual cost is not
  ascertainable. **Verify the current percentages against the Rules before relying on any default —
  including the ones hard-coded in `tools/landed_cost.py`.** Percentages circulating in trade
  practice do not all trace back to the Rules, and the wrong loading understates AV, which
  understates every downstream duty.
- **IGST is creditable, BCD is not.** For a registered importer, IGST flows back as input tax
  credit; BCD/SWS/AIDC/ADD are absorbed into cost. Quote the *effective* landed cost when comparing
  suppliers, and the *cash outflow* when planning working capital.
- **Second-hand and related-party imports.** Transaction value can be rejected under the Valuation
  Rules. Related-party imports go to the Special Valuation Branch (SVB) — budget for provisional
  assessment and an EDD deposit.

## Duty-saving routes worth evaluating before you buy

| Route | Fits when | Watch out for |
|-------|-----------|---------------|
| FTA preferential rate | Origin qualifies under the agreement's rules of origin | CAROTAR 2020 — see `fta-carotar.md` |
| Advance Authorization | Inputs are physically incorporated into an export product | Export obligation period, input-output norms |
| EPCG | Importing capital goods against a future export obligation | Export obligation quantum, block-wise fulfilment |
| MOOWR | Manufacturing in a bonded warehouse; duty deferred | Bonding, record-keeping, warehouse licence |
| IGCR Rules | Concessional rate for a specified end-use | Continuity bond, end-use evidence, periodic returns |

## Using the calculator

```bash
python3 tools/landed_cost.py --config tools/shipment.example.json
python3 tools/landed_cost.py --fob 25000 --rate 84.50 --freight 1800 --bcd 10 --igst 18 --json
```

Every rate is an input. The tool holds no tariff data and will never invent one — look the rate up
on ICEGATE or the CBIC tariff, record the notification number in your file, then feed it in.
