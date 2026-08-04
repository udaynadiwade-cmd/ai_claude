# Posting Playbook

## Read this first — what I can and cannot do

I **cannot** log into Naukri, LinkedIn, Indeed or Apna and click "Post". Those
platforms require an authenticated employer account, and I have no credentials
for them and no authorised browser session. Nobody should hand an agent those
credentials either.

So the division of labour is:

- **I do:** the JD, the platform-specific rewrites sized to each portal's format
  and character limits, the titles and keywords that decide whether your post
  gets seen, the sequencing, the budget guidance, and every screening and
  candidate-communication step after the post goes live.
- **You do:** the ten minutes of copy-paste-and-publish, once per platform.

Everything below is written so that step is mechanical. Ready-to-paste text is
in `jd/platform-posts/`.

**If you want the posting itself automated**, there are two real paths — tell me
if either interests you and I will set it up:
1. An ATS with an API and multi-posting built in (Zoho Recruit, Keka, Freshteam).
   I can drive those programmatically and push to all boards from one place.
2. Naukri and LinkedIn both offer employer APIs on paid plans.

---

## Platform matrix — where these two roles actually get filled

Ranked for **B2C sales, 1–3 years, India, on-site** and **digital marketing
executive, 1–3 years**.

| # | Platform | Best for | Cost | Priority |
|---|---|---|---|---|
| 1 | **Naukri.com** | Both roles. Largest resume database in India (~7.8 crore) and fills the large majority of Indian postings. Where loan/property sales candidates actually are. | Paid. Single job posting plans start modest; resume database access ("Resdex") costs more and is the part that actually matters | **Do first** |
| 2 | **LinkedIn** | DME especially; sales secondarily. Best for candidates who can demonstrate work publicly. | Free post gets limited reach; promoted is pay-per-day | **Do first** |
| 3 | **Apna.co** | Sales Executive. Built for high-volume frontline and field sales in India. Fast, large applicant flow. | Free tier available, paid for volume | **Do first (sales)** |
| 4 | **Indeed India** | Both. Free to post, pay only for sponsored reach. No reason not to. | Free base | **Do first** |
| 5 | **WorkIndia** | Sales Executive. Strong for field/frontline sales, phone-verified candidates. | Free tier | Do second |
| 6 | **Foundit** (ex-Monster India) | Both, mid-level reach | Free posting tier | Do second |
| 7 | **Shine.com** | Both, supplementary volume | Free tier | Do second |
| 8 | **Your own network** | Both — highest quality per applicant, zero cost | Free | **Do first** |
| 9 | **Instagram / Facebook** (your own handles) | Both. Your DME candidate pool literally lives here | Free | Do first |
| 10 | **Internshala / Freshersworld** | Only if you widen the sales role to freshers | Free/low | Skip for now |

**Deliberately skipped:** iimjobs and Hirist are for senior management and tech
respectively — wrong pool for executive-level roles. Instahyre is tech-heavy.

### My recommended first wave

Post to **Naukri + Apna + Indeed + LinkedIn + your own social and WhatsApp
network** on day one. That combination covers volume, frontline sales
specifically, free reach, and quality referrals. Add Foundit, Shine and
WorkIndia in week two only if the funnel is thin — more boards mainly means more
duplicate applications to screen.

---

## Titles — this matters more than the JD body

Portal search is keyword matching. The title decides whether your post is ever
seen. Use these exact strings:

**Sales Executive**
- Naukri / Apna / WorkIndia: `Sales Executive - Loans / Real Estate / Field Sales (1-3 Yrs) | [CITY]`
- LinkedIn: `Sales Executive`, and separately set the "job function" to Sales
- Indeed: `Sales Executive (B2C) - [CITY] - Fixed + Uncapped Incentive`

Put **"uncapped incentive"** in the title wherever the platform allows it. For
this candidate pool it is the strongest single click driver.

**Digital Marketing Executive**
- Naukri: `Digital Marketing Executive - Google Ads, Meta Ads, SEO, GA4 (1-3 Yrs) | [CITY]`
- LinkedIn: `Digital Marketing Executive (Performance Marketing)`
- Indeed: `Digital Marketing Executive - Paid Ads + SEO - [CITY]`

## Keywords to enter in the portal's skills/tags field

**Sales Executive:** Sales, Field Sales, Direct Sales, B2C Sales, Inside Sales,
Home Loans, Personal Loan, Loan Against Property, Real Estate Sales, Plot Sales,
Property Sales, Insurance Sales, Lead Generation, Cold Calling, Target
Achievement, Negotiation, CRM, Business Development

**Digital Marketing Executive:** Digital Marketing, Performance Marketing,
Google Ads, PPC, Meta Ads, Facebook Ads, Instagram Marketing, SEO, On-Page SEO,
Off-Page SEO, SEM, GA4, Google Analytics, Google Tag Manager, Search Console,
Semrush, Ahrefs, Email Marketing, Mailchimp, HubSpot, Social Media Marketing,
Content Marketing, Canva, Lead Generation

---

## Posting checklist

Work down this list once per platform. Tick as you go.

- [ ] **Prerequisite:** both Google Forms built (`pipeline/intake-setup.md`)
- [ ] **Prerequisite:** form links pasted into `config/hiring-brief.md`
- [ ] **Prerequisite:** all `[BRACKETED]` placeholders filled — say the word and
      I will do this in one pass once you give me the values
- [ ] Naukri — Sales Executive
- [ ] Naukri — Digital Marketing Executive
- [ ] Apna — Sales Executive
- [ ] Indeed — both
- [ ] LinkedIn — both
- [ ] Your LinkedIn personal post (highest engagement of all of these)
- [ ] Company Instagram / Facebook story + post
- [ ] WhatsApp to your network (text in `jd/platform-posts/whatsapp-referral.md`)
- [ ] Log the date and cost of each post in `candidates/tracker.csv`

## Important: keep the form as the only front door

Several portals default to "collect applications in our inbox". Where the
platform allows an external application URL, **use the Google Form link**. Where
it does not (Naukri and Apna push applicants into their own dashboard), put the
form link as the first line of the JD body and write: *"To be considered, please
also complete this 4-minute form."*

This is what keeps every candidate in one comparable format so I can screen them
consistently. Where a portal traps applicants in its dashboard, bulk-export the
resumes weekly and drop them in the Drive folder — I will screen those too, just
with less structured data to work from.

## After posting

Tell me it is live. I will then:
- track which source each applicant came from (form Q18/Q17),
- report cost per qualified applicant per platform after week one, and
- tell you which boards to renew and which to drop.
