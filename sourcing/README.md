# Sourcing Manager

Operating kit for an AI **Senior International Sourcing & Import Director (India)** — the system
prompt plus the reference material, checklists and arithmetic the persona is expected to apply.

Scope: China/Asia sourcing, Indian customs clearance, landed-cost computation, FTA and CAROTAR 2020
compliance, freight and container-cost control, QC sampling, and FEMA/IDPMS closure.

## Layout

```
SYSTEM_PROMPT.md              The agent's system prompt — load this as-is
data/
  hs/                         WCO HS 2022 nomenclature — 6,939 real codes (fetched)
  rates/                      Duty, FX and freight data (fetched on demand)
  STATUS.md                   What is populated, what is not, and why
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
  sources.json                Registry of primary sources + staleness budgets
  net.py                      HTTP/browser layer with typed failure classification
  provenance.py               Manifests: source, timestamp, sha256, staleness
  fetch_hs.py                 Pulls the WCO HS nomenclature
  fetch_rates.py              status | fx | tariff | freight
  hs_lookup.py                Classify, validate and search HS/ITC(HS) codes
  landed_cost.py              Landed-cost calculator
  test_landed_cost.py         8 tests — the duty cascade
  test_data_layer.py          22 tests — fetch, provenance, lookup, wiring
  shipment.example.json       Worked input
```

## Live data

```bash
pip install -r requirements.txt

cd tools
python3 fetch_hs.py                          # WCO HS nomenclature -> data/hs/
python3 fetch_rates.py status                # probe every source, report local state
python3 fetch_rates.py tariff --hsn 85444999 # ICEGATE duty heads -> data/rates/tariff/
python3 fetch_rates.py fx                    # CBIC notified exchange rates
python3 fetch_rates.py freight               # Drewry WCI composite
```

`data/hs/` ships populated with real data: 6,939 HS 2022 codes across 97 chapters and
21 sections. Duty, FX and freight data are **not** bundled — see `data/STATUS.md` for
what each fetcher needs and why shipping a rate snapshot would be a liability.

Classification, on real data, right now:

```bash
python3 hs_lookup.py 8544.49.99        # full section/chapter/heading chain
python3 hs_lookup.py --search "cable"  # candidate headings by description
python3 hs_lookup.py --chapter 85      # headings in a chapter
```

`hs_lookup.py` rejects odd-length codes, codes absent from the nomenclature, and the
UN Comtrade "not specified" chapter-99 bucket, and flags a 6-digit code as unfileable
because Indian duty differs between national extensions of the same HS-6.

## Design rule: the tooling holds no tariff data

`tools/landed_cost.py` will not tell you a BCD rate, an IGST rate, or whether an ADD notification
applies. Those are inputs. The point of the tool is that the **cascade** — what stacks into the IGST
base, what SWS is levied on, what is creditable and what is absorbed — is computed the same way
every time, from rates you looked up and can cite.

```bash
python3 tools/landed_cost.py --config tools/shipment.example.json
python3 tools/landed_cost.py --fob 25000 --rate 84.50 --freight 1800 \
    --bcd 10 --igst 18 --hsn 85444999 --origin China --quantity 5000
python3 tools/landed_cost.py --hsn 85444999 --fob 25000 --rate 84.50 --auto --strict
python3 tools/landed_cost.py --config tools/shipment.example.json --json   # machine-readable
```

`--auto` fills any rate you did not supply from `data/rates/tariff/<hsn>.json`, and
only from there. `--strict` exits non-zero unless BCD and IGST both came from a
fetched source — use it in any pipeline that quotes a price to a customer.

Every run prints a `RATE PROVENANCE` block naming the origin of each rate
(`command line`, `config file`, `ICEGATE, fetched <date>`, or `unset`), the
classification the HSN resolved to, and a warning if BCD or IGST silently defaulted
to zero.

Tests (30 in total; no network, standard library only):

```bash
cd tools && python3 test_landed_cost.py && python3 test_data_layer.py
```

## Failure is never silent

`net.py` classifies every failure. A request that never reached the origin — proxy
refusal, DNS failure, browser tunnel rejection, untrusted TLS interception — raises
`EgressBlocked`, which is a different type from an HTTP error precisely so that
"I could not reach ICEGATE" can never be recorded as "ICEGATE reports no duty". On
any such failure the fetcher writes nothing and exits non-zero, leaving the previous
data and its timestamp intact.

`provenance.py` gives every dataset a `MANIFEST.json` with source, URL, licence,
fetch timestamp, per-file sha256 and a staleness budget (14 days for CBIC exchange
rates, 30 for tariff lookups, 5 for FBX, 365 for the HS nomenclature). Stale or
tampered data is reported as such by `fetch_rates.py status` and stamped `[STALE]`
wherever a rate derived from it is quoted.

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
