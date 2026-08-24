# 15-Day Curriculum — Outskill Mentor

Built 24 Aug 2026 from three documents shared in Uday's Drive (folder:
[🛠️ Hands-On Workbooks](https://drive.google.com/drive/folders/18KUAdu1otGg7PekyvnUJ8Gq3tGtjzlja)):

- **[Pre-Read]** *Fundamentals of Gen AI & Prompt Engineering*
- **[Workbook 1]** *Building Claude Artifacts*
- **[Workbook 5]** *Building your own AI Employee*

15 minutes/day. Days 5, 8, and 14 are lighter — apply-what-you-learned days,
not new content, so the pace stays realistic. If a new workbook lands in the
Drive folder before Day 15, read it and propose where it slots in (a new
day, or folded into a review day) — see `CHARTER.md` step 5.

| Day | Source | Focus | Nugget (send this) | Question / 15-min action |
|---|---|---|---|---|
| 1 | Pre-Read, "AI Is Not Google" | Mindset shift: AI is a context engine, not a search engine — it doesn't find answers, it generates them from what you give it | The output is only as good as the situation you describe. Vague prompt → generic guess. Specific context → targeted answer. This is the single lever that matters most. | Think of one AI prompt you wrote this week that got a mediocre answer. What context did you *not* give it that you now realize mattered? |
| 2 | Pre-Read, "5-Step Pipeline" + hallucinations | AI predicts the most likely next word from your context — it doesn't "know" or verify facts, so it can sound confident and still be wrong | Never treat an AI answer as fact-checked. Treat it as a fast, well-read first draft that you verify before it touches a candidate, a client, or a number. | Name one thing you'd never paste into a free AI tool because it's sensitive — candidate data, salary bands, anything from `config/hiring-brief.md`. |
| 3 | AI Employee Workbook, Level 1 — the 5-part prompt structure | Every strong prompt has up to five parts: **Role** (who it should act as), **Objective** (the task, one line), **Context** (everything it needs to know about you and the situation), **Instructions** (rules for the output), **Notes** (anything else) | This structure is the difference between "screen this resume" and getting a rubric-driven evaluation you can actually trust. | Pick one real task you'll do today. Write it as Role / Objective / Context / Instructions / Notes and run it. What changed versus how you'd normally ask? |
| 4 | AI Employee Workbook, Level 1 — Markdown prompting | `#` marks a heading (bigger `#` = more important), `**bold**` marks something the AI should pay special attention to. AI can't see font size, so you signal importance with these two symbols instead | Structuring a prompt with headings and bold is a five-second habit that measurably changes output quality — use it in *every* prompt you plan to reuse. | Take yesterday's Role/Objective/Context prompt and add `#` headings and one `**bolded**` instruction. Did the output get sharper? |
| 5 | Review — no new material | Apply Days 1–4 | — | 15-minute action: rewrite one prompt you use regularly at Befach (a resume-screening prompt, a JD prompt, a candidate email prompt) using the full 5-part + Markdown structure. Save it somewhere you'll reuse it. |
| 6 | Artifacts Workbook, §1–2 — what an Artifact is | An Artifact isn't a description of the thing you asked for — it's the thing itself, running: an app, dashboard, or tool built from one prompt, no code, no install | Anything you'd normally build as a spreadsheet or ask someone to code — a calculator, a tracker, a checklist app — you can build free in about 15 minutes and share as a link. | Name one clunky spreadsheet or manual process at Befach that could become a 15-minute Artifact this week. |
| 7 | Artifacts Workbook, §4 — AI-powered artifacts | A normal Artifact stores and displays data. An AI-powered one can also *reason* — it calls Claude from inside itself while it runs, so the app can summarise, suggest, or judge, not just record | This is the real unlock: a tool that doesn't just hold your data but thinks about it — e.g. a screening tool that reads a CV and drafts a first-pass score, not just logs it. | If your Day 6 idea could also *think* — summarise, suggest, or score something — what would you ask it to reason about? |
| 8 | Review — no new material | Apply Days 6–7 | — | 15-minute action: open Claude, turn on the three Visuals toggles (Artifacts, AI-powered artifacts, Inline visualizations — Artifacts Workbook §3), and build the Day 6/7 idea as a real, working Artifact. |
| 9 | AI Employee Workbook, "Start Here" | An AI employee is an assistant you set up once that then does a repeatable job on its own — the same way you'd onboard a new hire: give it a workspace, show it the files, explain the job once, then set it a routine | This is exactly the model already running the Befach hiring pipeline (see root `AGENT.md`) — a standing charter plus a schedule. You already know this pattern works; now you're learning to build it yourself. | What's one task you still do by hand every week at Befach that's genuinely repeatable — a report, a summary, a first-pass draft? |
| 10 | AI Employee Workbook, Level 2 — the reusable project + the two-step move | Instead of writing a long instruction prompt yourself: (1) ask the AI to draft it as an expert prompt engineer, (2) hand it your Markdown cheat sheet and say "rewrite using this structure." Then save the result as a reusable Project (Claude) or Custom GPT (ChatGPT) | Stop re-explaining the same task every time. A five-minute one-time setup turns "write me a prompt" into "just give it the topic." | Pick your Day 9 repeatable task. Use the two-step move to draft its instructions, then create a Project/Custom GPT with them saved in. |
| 11 | AI Employee Workbook, Level 2 — the Style Playbook | Don't try to *describe* your own writing style — that's hard. Instead, feed AI a sample of your real past writing and have it produce a "Style Playbook" of how you actually write: hooks, structure, phrases, what performed well | This applies directly to candidate emails, JD posts, and LinkedIn copy — the templates in `templates/emails/candidate-emails.md` and `jd/platform-posts/` could sound like you instead of like a template. | Export or gather a handful of your own past emails or posts. Ask AI to build a Style Playbook from them — what does it notice about how you write that you hadn't named yourself? |
| 12 | AI Employee Workbook, Level 3 — workspace, sub-agents, SOP | A real employee doesn't wait for every task spelled out — it needs a workspace (a folder with its files), can run a team of sub-agents in parallel (one per topic), and can document its own process as an SOP once you're happy with it | This is the exact shape of the recruiting agent already running in this repo: a folder, a charter, and a documented procedure. You're looking at the finished version of what this lesson teaches. | Of your Day 9 task, which part would benefit from *parallel* sub-agents — several angles worked at once — versus one agent doing it step by step? |
| 13 | AI Employee Workbook, Level 3 — scheduling + "Practicalities" (free vs paid, privacy) | You can learn every level free; running it for real (folder access, multiple sub-agents, daily scheduling) needs a paid plan because autonomous runs consume much more usage. On free tiers, don't paste anything genuinely sensitive — it may be used to improve the model | Prove the idea free first — one manual run, by hand, exactly as the SOP describes — before you pay for the automation. Never pilot with real candidate or salary data on a free tier. | For your Day 9 task, would a free trial or one manual walkthrough prove the idea before you'd commit to a paid, scheduled version? |
| 14 | Review — no new material | Apply Days 9–13, "Plan your own AI employee" worksheet | — | 15-minute action: fill in, for your real task — What job should it do? What files does it need? What should it produce? How would you judge a good result? When should it run? |
| 15 | Capstone | Everything | You didn't just learn prompting — you learned how to hand a whole job to AI: set the workspace, supply the files, teach it once, let it use a team, schedule it. That pattern extends to almost any recurring job at Befach. | State the one AI employee you're actually going to build and ship in the next two weeks — in one sentence: job, inputs, output, cadence. |

## Pending material (not yet in the curriculum)

The bootcamp schedule (Drive: "GEN AI BOOTCAMP SCHEDULE") lists sessions
with no matching workbook in the folder yet, as of 24 Aug 2026:

- Vibe Coding (Lovable / Bolt / Replit) — Day 1
- AI Workflows & Connectors — Day 1
- Building AI Agents on N8N — Day 2
- Visual Storytelling & Content Creation using AI (images/videos) — Day 3
  (tonight's bonus session, 7–10 PM IST)

If workbooks for these appear in the Drive folder, read them and propose
where they fit — as extra days, or swapped in for a review day — rather
than silently lengthening the 15-day promise.
