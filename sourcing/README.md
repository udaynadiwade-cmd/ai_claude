# Sourcing Manager

Operating kit for an AI **Senior International Sourcing & Import Director (India)** — the system
prompt plus the reference material, checklists and arithmetic the persona is expected to apply.

Scope: China/Asia sourcing, Indian customs clearance, landed-cost computation, FTA and CAROTAR 2020
compliance, freight and container-cost control, QC sampling, and FEMA/IDPMS closure.

## Layout

```
SYSTEM_PROMPT.md              The agent's system prompt — load this as-is
reference/
  landed-cost.md              Assessment order, pitfalls, duty-saving schemes
  fta-carotar.md              Preferential claims and CAROTAR 2020 defence
  compliance-gates.md         BIS / WPC / LMPC / EPR / FSSAI / CDSCO pre-order gates
  incoterms-logistics.md      Incoterms 2020, ports/ICDs, free time, documents
  china-sourcing.md           Factory vetting, cluster map, CNY calendar
  quality-aql.md              ISO 2859-1 sampling, FAI/DUPRO/PSI/CLC
  banking-fema.md             Payment structure, AD bank, IDPMS knock-off
templates/
  rfq.md                      Supplier enquiry template
  pre-shipment-checklist.md   PO → clearance → IDPMS closure checklist
  contract-clauses.md         Quality, origin, tooling, NNN, delay clauses
tools/
  landed_cost.py              Landed-cost calculator (arithmetic only)
  test_landed_cost.py         Tests for the duty cascade
  shipment.example.json       Worked input
```

## Design rule: the tooling holds no tariff data

`tools/landed_cost.py` will not tell you a BCD rate, an IGST rate, or whether an ADD notification
applies. Those are inputs. The point of the tool is that the **cascade** — what stacks into the IGST
base, what SWS is levied on, what is creditable and what is absorbed — is computed the same way
every time, from rates you looked up and can cite.

```bash
python3 tools/landed_cost.py --config tools/shipment.example.json
python3 tools/landed_cost.py --fob 25000 --rate 84.50 --freight 1800 \
    --bcd 10 --igst 18 --hsn 85444999 --origin China --quantity 5000
python3 tools/landed_cost.py --config tools/shipment.example.json --json   # machine-readable
```

Tests (no dependencies, Python 3.8+):

```bash
cd tools && python3 test_landed_cost.py
```

## Verify before you rely on it

Every rate, QCO, notification and statutory timeline in this repository must be confirmed against the
primary source at the time of use — ICEGATE, the CBIC tariff and notifications, the DGFT ITC(HS)
schedule and FTP, BIS Manakonline, the CPCB EPR portals, and the RBI Master Directions. This kit
encodes **method and sequence**, not current rates.

One known item to confirm before first use: the notional insurance and freight loadings in
`tools/landed_cost.py` are defaults under Rule 10(2) of the Customs Valuation Rules and should be
checked against the current Rules — see the note in `reference/landed-cost.md`. Supplying the actual
freight and insurance from the invoice and policy avoids the question entirely, and the tool warns
whenever it falls back to a notional loading.
