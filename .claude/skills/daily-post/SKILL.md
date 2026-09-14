---
name: daily-post
description: Draft, card, and send today's LinkedIn post for Uday. Run once each morning.
---

# /daily-post

Everything lives in `linkedin/`. Work in this order and do not skip the gate.

0. **Ask first — always.** Standing instruction from Uday (2026-09-14).
   Before drafting anything, read `linkedin/INTERVIEW.md`, then put three to
   six numbered questions to him about the topic: his own angle, the one fact
   only he knows, who it should reach and who to tag, the ask, sell or no
   sell, anything off limits. Wait for the answers. Do not draft until he has
   replied. If he says "just write it", draft with placeholders for what you
   would have asked and let `post.py` hold the send.
1. **Read context**: `linkedin/voice.md`, `linkedin/topics.md`, the last five
   rows of `linkedin/posts/log.md`, and yesterday's `linkedin/posts/*.md`.
   Pick the next pillar in rotation and a topic not yet used. If Uday gave a
   topic in chat, use that instead.
1b. **If the post cites a product**, get its real figures with
   `python3 linkedin/catalog.py <sku>`. Never read them off a web page and
   never estimate them. If no channel is configured the script says so —
   then either ask Uday for the numbers or write a post that needs none.
   `linkedin/ACCESS.md` explains how to open a channel.
2. **Draft three options** in voice.md's shape. Label them 1, 2, 3. Each under
   200 words. Different hooks, same topic. Show them in full.
3. **Ask by number**: "Which one? (1/2/3, or edits)". Wait. Apply edits until
   Uday says it is final.
4. **Save** the final as `linkedin/posts/YYYY-MM-DD.md` using
   `posts/_template.md` (title = hook line, `card:` = `out/YYYY-MM-DD.png`).
   Move the topic to *Used* in `topics.md`.
5. **Render the card**:
   `python3 linkedin/cardgen.py --title "<hook>" --body "<one supporting line>" --out linkedin/out/YYYY-MM-DD.png`
   If it produced `.svg` instead, set `card:` to the `.svg` path. Show the file
   to Uday.
6. **Dry run**: `python3 linkedin/post.py linkedin/posts/YYYY-MM-DD.md --dry-run`.
   Then put exactly one decision at the end of the message:

   ```
   1. Send today's post to the webhook?  Y/N
      Goes out now via post.py; logged in posts/log.md.
   ```
7. On **Y**: run `python3 linkedin/post.py linkedin/posts/YYYY-MM-DD.md`, paste
   the response status, confirm the log row. On **N**: leave the file as draft,
   set `status: held`, stop.

Rules: never draft without asking first. Never send without the Y. Never invent numbers (voice.md). If
`WEBHOOK_URL` is missing, say so and stop at step 6. If `cardgen.py` is still
the placeholder, say so once in the message and carry on.
