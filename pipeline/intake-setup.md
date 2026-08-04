# Application Intake — Setup

You chose **Google Form → Sheet + Drive upload**. This is the right call: it
gives every applicant an identical, comparable record, which is what lets me
score them consistently instead of guessing from free-form emails.

**What I have already done for you:** the Drive folder structure and the tracker
sheet exist (links in `README.md`).

**What you need to do:** build the Form. Ten minutes, one time, per role. Google
does not expose a Forms API to me, so this is the one step I cannot do for you.

---

## Step 1 — Create the form

1. Go to **forms.google.com** → Blank form.
2. Title it `Sales Executive — Application` (repeat separately for the DME role;
   two forms are cleaner than one branching form).
3. Settings (gear icon):
   - **Responses → Collect email addresses:** ON (Verified).
   - **Responses → Send responders a copy:** ON. This is your auto-acknowledgement.
   - **Presentation → Confirmation message:** paste the text from
     `templates/emails/01-acknowledgement.md`.
   - File uploads require the responder to sign in to Google. This is fine and
     it filters out junk.

## Step 2 — Questions, Sales Executive

Mark ✱ questions Required.

| # | Question | Type | Notes |
|---|---|---|---|
| 1 | Full name ✱ | Short answer | |
| 2 | Mobile number ✱ | Short answer | Response validation → regex `^[6-9]\d{9}$` |
| 3 | Current city ✱ | Short answer | |
| 4 | Are you able to work on-site in `[CITY]`? ✱ | Multiple choice | Yes / No / Willing to relocate |
| 5 | Total years in a target-carrying sales role ✱ | Multiple choice | 0–1 / 1–2 / 2–3 / 3–5 / 5+ |
| 6 | What have you sold? ✱ | Checkboxes | Home loans / Personal loans / LAP / Real estate plots / Residential property / Commercial property / Insurance / Other consumer product / Other |
| 7 | Current or most recent employer ✱ | Short answer | |
| 8 | Your monthly sales target, and what you actually achieved against it ✱ | Paragraph | **The single most important question. See scoring note below.** |
| 9 | Largest single deal you have closed (₹) ✱ | Short answer | |
| 10 | Roughly how many calls did you make on a typical day? ✱ | Short answer | |
| 11 | Which CRM have you used? ✱ | Short answer | "None" is an acceptable answer |
| 12 | Languages you are fluent in ✱ | Checkboxes | English / Hindi / `[REGIONAL]` / Other |
| 13 | Current fixed CTC ✱ | Short answer | |
| 14 | Expected fixed CTC ✱ | Short answer | |
| 15 | Notice period ✱ | Multiple choice | Immediate / 15 days / 30 days / 60 days / 90 days |
| 16 | Upload your CV ✱ | File upload | PDF/DOC, max 1 file, 10 MB |
| 17 | Optional: 60-second voice note or video introducing yourself | File upload | Not required — but see note |
| 18 | Where did you see this job? | Multiple choice | Naukri / LinkedIn / Indeed / Apna / Referral / Other — **tells us which channel works** |

> **On Q8:** this question does the heavy lifting. Candidates who give a real
> number ("target 12 lakh disbursement, did 9–14 depending on the month") are a
> different population from candidates who write "always exceeded expectations".
> My rubric scores this at the highest weight.

> **On Q17:** for a role where spoken communication *is* the product, thirty
> seconds of audio tells you more than the whole CV. Keep it optional so you do
> not lose applicants, but candidates who submit one should jump the queue.

## Step 3 — Questions, Digital Marketing Executive

| # | Question | Type | Notes |
|---|---|---|---|
| 1 | Full name ✱ | Short answer | |
| 2 | Mobile number ✱ | Short answer | Same regex validation |
| 3 | Current city ✱ | Short answer | |
| 4 | Able to work on-site in `[CITY]`? ✱ | Multiple choice | Yes / No / Willing to relocate |
| 5 | Years of hands-on digital marketing experience ✱ | Multiple choice | 0–1 / 1–2 / 2–3 / 3–5 / 5+ |
| 6 | Which of these have you personally run? ✱ | Checkboxes | Google Ads Search / Performance Max / Meta Ads / GA4 / Google Tag Manager / Search Console / Semrush or Ahrefs / Mailchimp/HubSpot/Zoho / Canva or Figma / Video editing / None of these |
| 7 | Largest monthly ad budget you personally managed ✱ | Multiple choice | Never managed a budget / Under ₹50k / ₹50k–2L / ₹2L–5L / ₹5L–10L / ₹10L+ |
| 8 | Describe one campaign: channel, monthly budget, starting CPL, ending CPL ✱ | Paragraph | **Highest-weighted question.** |
| 9 | Have you set up conversion tracking yourself (GTM, pixel, CAPI)? ✱ | Multiple choice | Yes end-to-end / Partly, with help / No |
| 10 | Have you marketed a high-ticket product where a salesperson closed the lead? ✱ | Multiple choice | Yes / No |
| 11 | Link to portfolio, website you ran, or social handle you managed | Short answer | |
| 12 | Certifications | Checkboxes | Google Ads / Meta Blueprint / GA4 / HubSpot / None |
| 13 | Current fixed CTC ✱ | Short answer | |
| 14 | Expected fixed CTC ✱ | Short answer | |
| 15 | Notice period ✱ | Multiple choice | Immediate / 15 / 30 / 60 / 90 days |
| 16 | Upload your CV ✱ | File upload | |
| 17 | Where did you see this job? | Multiple choice | Same options |

## Step 4 — Wire it to Drive and the tracker

1. In the form, **Responses → Link to Sheets**. Google creates a response sheet.
2. Google automatically creates a Drive folder named
   `Sales Executive — Application (File responses)` holding every uploaded CV.
3. **Move both** the response sheet and the file-responses folder into the
   `Hiring 2026` Drive folder I created, under the matching role subfolder.
4. **Share both with me** — or simply tell me the role name, and I will find them
   via Drive search. I already have access to your Drive.

## Step 5 — Hand me the links

Paste the two form links into this repo (`config/hiring-brief.md`) or just drop
them in chat. I will:

- substitute them into both JDs and every platform post, and
- start screening as soon as responses arrive.

---

## What happens after that

Say **"screen the new applications"** — at whatever cadence you like, or I can
run it on a schedule — and I will:

1. Read every new row in the response sheet.
2. Download and read each CV from Drive.
3. Score each candidate against the rubric in `screening/`.
4. Update `candidates/tracker.csv` and the Drive tracker sheet.
5. Give you a ranked shortlist: **Interview / Maybe / Reject**, with a one-line
   reason each and the specific evidence behind the score.
6. Draft the outreach emails for everyone you approve.

I never auto-reject and never email a candidate without you seeing it first.
