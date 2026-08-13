# Hiring — how the two systems fit together

There are two hiring systems in play and they were built independently. This
file is the ruling on which governs what, so you never have to wonder which one
to follow.

**The short version:** the six `hiring-*` skills are the **method**. The older
repo folders are **content and channel knowledge**. They are not competitors —
one is process, one is material — but three things genuinely conflicted and are
resolved below.

---

## System A — the six `hiring-*` skills

Synced from claude.ai; source at `~/.claude/skills/synced/hiring-*/`.

`hiring-role-intake` → `hiring-job-description` → `hiring-resume-screen` →
`hiring-interview-kit` → `hiring-decision` → `hiring-candidate-comms`

Role-agnostic, Befach-specific, and methodologically stronger than what the repo
had. They generate per-role artifacts into `hiring/roles/<role-slug>/`.

**They were broken until now.** All six open with *"Read
`../_shared/befach-context.md`"*, and the manifest shows six standalone bundles
with no `_shared` entry — that file was never packaged. Every skill was either
stalling on a missing file or quietly inventing Befach facts.
**Fixed:** [`_shared/befach-context.md`](_shared/befach-context.md), researched
and marked CONFIRMED / RESEARCHED / INFERRED / NEEDED.

## System B — the repo folders

`jd/` · `screening/` · `pipeline/` · `candidates/` · `templates/` · `config/`

Built earlier in this workspace for three named roles. Two parts of it are
genuinely valuable and have no equivalent in the skills; one part is now
superseded; and the role content itself has a problem — see the flag below.

---

## Precedence — read this if the two disagree

| Concern | Governed by | Why |
|---|---|---|
| Whether to open a role at all | **Skills** (`hiring-role-intake`) | The repo has no equivalent, and its "is this even a hire?" challenge is the most valuable step in the stack |
| Role definition, must-haves | **Skills** — max 5 ranked, each with a stated verification method | Forces a discipline the repo's open-ended rubrics did not |
| Where artifacts are written | **Skills** — `hiring/roles/<role-slug>/` | One convention. The repo's split across `jd/`, `screening/`, `candidates/` scattered one role across four folders |
| Resume scoring | **Skills** — 0–3 per must-have, weighted by rank; buckets Advance / Maybe / Hold / Pass | See conflict 1 |
| Interview structure | **Skills** — 4 rounds max, competency owned by exactly one round, 1–4 scorecards filled in *before* debrief, binary hire/no-hire | Materially better method than the repo's 3-stage kits |
| Offer and debrief | **Skills** (`hiring-decision`) | The repo had nothing here at all |
| Candidate messaging | **Skills** (`hiring-candidate-comms`) | But keep the repo's templates as raw material — see conflict 3 |
| **Which job boards, what they cost, what to title the post** | **Repo** — [`../pipeline/POSTING-PLAYBOOK.md`](../pipeline/POSTING-PLAYBOOK.md) | The skills name channels but carry no channel strategy. The repo's platform matrix, title/keyword guidance and the direct-outreach target list are real knowledge the skills lack |
| **Structured application intake** | **Repo** — [`../pipeline/intake-setup.md`](../pipeline/intake-setup.md) | The skills assume resumes arrive as a pile. A Google Form gives every applicant an identical comparable record, which is what makes 0–3 scoring defensible |

---

## The three real conflicts, resolved

**1 — Two incompatible scoring scales.** The repo scores 100 points across 6–7
weighted criteria with bands (Interview / Strong maybe / Maybe / Reject). The
skills score 0–3 against a maximum of five ranked must-haves, into buckets
(Advance / Maybe / Hold / Pass). Running both produces two non-comparable numbers
for the same candidate and an argument about which is right.
**Resolution: the skills' scale wins.** It is simpler, it caps must-have
inflation at five, and — the deciding factor — it requires a stated verification
method per criterion, which is what stops a criterion becoming a vibe. The
repo's rubric weights are not wasted: they are the correct *ranking input* when
`hiring-role-intake` asks you to rank the five must-haves.

**2 — Two intake mechanisms.** The repo routes everything through a Google Form
into a Sheet and Drive; the skills assume Naukri/LinkedIn/Internshala applications
arriving as resumes.
**Resolution: keep the form, feed the skills.** The form is upstream of
`hiring-resume-screen`, not a rival to it. One change: the form's screening
question should follow the skills' rule — one question a generic applicant
cannot answer (`hiring-job-description`, "Application-quality note"). The repo's
Sales Executive Q8 already does exactly this; the other roles' should be
tightened to match.

**3 — Two sets of candidate email templates.** The repo has eight finished
templates; `hiring-candidate-comms` has principles and a two-option draft format
but no library.
**Resolution: repo templates become raw material, skill governs the send.** The
skills add three things the repo templates lack and that should be applied on
every send: give concrete slots rather than asking candidates to propose, state
the band in the first outreach message, and put a real deadline on offers.

---

## ⚠️ Unresolved — and it needs your answer

The repo's three roles were written against a company profile that **does not
match Befach**:

| | Repo assumed | Befach actually is |
|---|---|---|
| Sales Executive | B2C, **high-ticket** considered purchase, wants loans / plots / property / insurance closers, site visits, uncapped incentive | befach.com is **B2B** import; D'Cal is D2C at **₹3,600** — not high-ticket, and not a loans/property sales motion |
| Digital Marketing Executive | High-ticket lead-gen where **a salesperson closes the lead** | D'Cal is marketplace + own-site e-commerce; befach.com is B2B trade |
| Research Manager | Market research for a high-ticket D2C business | Conceptually a good fit for import category, competitor and pricing intelligence — but the JD text assumes the wrong business |

I wrote those roles from a brief where company, industry and city were all
`NEEDED`, and I marked the industry `ASSUMED`. That assumption now looks wrong.

**So: are those three roles Befach roles, or a different venture?**

- **If Befach** — they need re-briefing through `hiring-role-intake` against a
  real vertical, not merging as-is. The rubric criteria carry over as ranking
  input; the JD prose does not.
- **If a different venture** — say so and I will keep the two systems separate,
  because a Befach-scoped skill stack should not be generating JDs for it.

Until that is answered the repo role content stays where it is, untouched and
unused by the skills. Nothing has been deleted.

---

## Using the stack today

1. `hiring-role-intake` — it will now find the context file. It will still ask
   for **vertical**, **comp band** and **approver**; the first is per-role, the
   other two are the top NEEDED items in
   [`_shared/befach-context.md`](_shared/befach-context.md). Fill those two once
   and every later run gets faster.
2. Everything downstream reads the brief it writes.
3. Artifacts land in `hiring/roles/<role-slug>/`.

Fill the comp bands and name the approver and this stack is fully operational.
