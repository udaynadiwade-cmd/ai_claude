# LinkedIn post writer

One post a day, written in Uday's voice, with a card, sent through the webhook.

## Setup (two minutes)
1. `cp linkedin/.env.example linkedin/.env` and paste the **webhook URL** from
   the old `30-config.md`.
2. Overwrite `linkedin/cardgen.py` with the Python block from the old
   `10-cardgen.md`. Keep its CLI as `--title --body --out` (or adjust the one
   line that calls it in `.claude/skills/daily-post/SKILL.md`).
3. Optional: `pip install pillow` so the placeholder card renders PNG instead of SVG.

## Each morning
```
/daily-post
```
Claude asks you three to six numbered questions first (always — see
`INTERVIEW.md`), then drafts, you pick and edit by number, it renders the
card, shows the payload, and sends only on your **Y**.

## Files
| | |
|---|---|
| `voice.md` | who is writing and how — edit this when a post sounds off |
| `topics.md` | pillars + topic bank; move used topics to *Used* |
| `posts/YYYY-MM-DD.md` | one file per post, `_template.md` shows the shape |
| `posts/log.md` | what went out when |
| `cardgen.py` | card renderer (yours, from 10-cardgen.md) |
| `post.py` | sends `{title, text, image_base64, ...}` to `WEBHOOK_URL` |
| `out/` | rendered cards, git-ignored |

## By hand, without the skill
```
python3 linkedin/cardgen.py --title "Hook" --body "line" --out linkedin/out/2026-09-14.png
python3 linkedin/post.py linkedin/posts/2026-09-14.md --dry-run
python3 linkedin/post.py linkedin/posts/2026-09-14.md
```

## Getting it onto the feed

`post.py` sends to `WEBHOOK_URL`. It does not talk to LinkedIn. LinkedIn's API
only grants direct posting to approved partner apps, so the webhook is the
practical route: point it at a Zapier / Make / n8n scenario whose action is
"LinkedIn → Create post", and that scenario holds the LinkedIn auth, not this
repo. That is almost certainly what the old `30-config.md` URL already was.

The payload it posts is `{title, text, image_name, image_base64, date, author}`.
Map `text` to the post body and `image_base64` to the image in that scenario.

## Safety rails in post.py
- Refuses to send if the draft still contains `[[PLACEHOLDER]]` markers, so a
  post with unverified numbers cannot go out. `--dry-run` still previews it.
- Unwraps editor line breaks; LinkedIn renders every newline literally.

## Later
Cron/routine is deliberately off. Get a week of good posts out by hand, then
automate the trigger (a Routine that fires `/daily-post` at 8:00 IST).
