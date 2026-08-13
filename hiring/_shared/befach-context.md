# Befach — shared hiring context

**This file is the missing dependency.** All six `hiring-*` skills open by
reading `../_shared/befach-context.md`, and it was never packaged with them.
Until this exists at a path they can resolve, every one of them either stalls or
silently invents company facts.

**Canonical copy: this file, in this repo.** A mirror is written to
`~/.claude/skills/synced/_shared/befach-context.md` so the skills resolve today,
but that directory is synced from claude.ai and lives in an ephemeral container
— treat the mirror as disposable and this file as the source of truth. To make
it permanent, add it to the skill bundle on claude.ai.

## Status legend

- `CONFIRMED` — told to me directly by you.
- `RESEARCHED` — from public sources, cited. Accurate as far as I can verify,
  but you should correct it.
- `INFERRED` — read out of the hiring skills' own text. Plausible, unverified.
- `NEEDED` — I cannot let a skill run properly without this.

---

## Company

| Field | Value | Status |
|---|---|---|
| Legal entity | **Befach 4x Pvt Ltd** | RESEARCHED |
| Founded | 2018 | RESEARCHED |
| Base | Hyderabad, Telangana | RESEARCHED |
| Founders | Two co-founders | RESEARCHED |
| Team size | `[NEEDED]` | NEEDED |
| Hiring approver | `[NEEDED — named person; hiring-decision and hiring-candidate-comms both refer to "the approver named in the context file"]` | NEEDED |
| Careers inbox / apply route | `[NEEDED]` | NEEDED |
| Default work mode | Hyderabad on-site | INFERRED |

## Verticals

The hiring skills assume a multi-vertical group and name work samples per
vertical. This is what each one actually is:

| Vertical | What it is | Customer | Status |
|---|---|---|---|
| **befach.com** | End-to-end India import platform — factory-direct sourcing, QC inspection, customs, landed-cost transparency, last-mile. Verified suppliers across China, Vietnam, Thailand, Indonesia, Turkey. ~2,400 import-ready SKUs, 10,000+ suppliers, 50+ Indian cities. | B2B only — distributors, retailers, builders, hospitality chains. No consumer retail. | RESEARCHED |
| **befach.in** | Sourcing-agent services entity, Hyderabad. China sourcing, import-to-India. | B2B | RESEARCHED |
| **befachbrands.com** | Own-brand storefront. Carries D'Cal. | Mixed | RESEARCHED |
| **D'Cal** (dcal.co.in) | Zero-electricity, zero-maintenance hard water softener. ~₹3,600, ~1 year life, treats ~3 lakh litres, drops into a borewell — no pipes, plumber or electricity. Sold via own site, Flipkart, Amazon India. Live in Telangana, MP, UP, Gujarat, Rajasthan, Tamil Nadu. | **D2C — homeowners.** | RESEARCHED |
| **91gi** | Referenced in `hiring-interview-kit` as an ops/catalogue vertical with "GI product listings". | `[NEEDED]` | INFERRED |

> **This matters for every JD and work sample.** befach.com is B2B trade;
> D'Cal is D2C e-commerce at a ₹3,600 price point. They need different hires,
> different channels and different work samples. A skill that does not know
> which vertical a role sits in will produce a JD that fits neither — which is
> why `hiring-role-intake` asks for the vertical first and should keep doing so.

## What the work is actually like

- Small company, wide surface area, no large team behind any one person.
  Candidates who want scope read that as the pitch; candidates who want a
  defined lane should self-select out. Say it plainly in JDs. `INFERRED`
- Hyderabad talent pool, well connected — reputational damage from a retracted
  offer or a ghosted candidate travels. `INFERRED`
- Useful hires have come from outside the tier-1 college set. College tier is
  explicitly not a screening criterion. `INFERRED`

## Scarce and valuable, for befach.com roles

Trade literacy is genuinely rare in the Hyderabad pool and should be surfaced
loudly wherever it appears in a resume: HS codes, Incoterms, customs clearance,
freight forwarding, supplier negotiation, LC/TT payment terms, landed-cost
build-up (FOB → freight → insurance → BCD → IGST → AIDC → surcharge → CHA →
port → last-mile).

## Compensation bands

| Vertical / level | Band | Status |
|---|---|---|
| All roles | `[NEEDED]` | NEEDED |

> `hiring-job-description` instructs you to **state the band in the post**, and
> `hiring-decision` instructs you to **anchor the offer on the band, not on the
> candidate's current CTC**. Neither works without real numbers here. This is
> the single highest-value gap in this file.

## Standing rules these skills already enforce

Carried here so they survive even if a skill is edited:

- Never screen or ask on caste, surname, religion, native place, mother tongue,
  gender, marital or pregnancy status, age, photo, disability, or college tier.
- No coded language in JDs — "young and energetic", "bachelor boy", "male
  candidates" and equivalents are off the table. Replace with the real
  requirement.
- Work samples are timeboxed and stated; anything over two hours is paid; a
  candidate's assignment is never shipped as production work.
- Scorecards are filled in before the debrief, and the hire/no-hire call is
  binary — no "maybe".
- Rejections go out fast, with one specific honest reason.

## Open questions blocking full use

1. Comp bands per vertical and level.
2. Named hiring approver.
3. What 91gi is, and whether it is active.
4. Team size and current org shape.
5. Apply mechanism — inbox, form, or ATS.
6. **Which verticals are actually hiring right now.**
