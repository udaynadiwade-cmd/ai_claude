# tools/

## wa-link.py — send WhatsApp from Uday's own number

Candidates for these roles largely do not read email. WhatsApp is the channel
that actually reaches them. This turns a drafted message into a link that opens
WhatsApp with the message already typed, addressed to that candidate.

```
python3 tools/wa-link.py 9640769453 "Hi Pavan, ..."
python3 tools/wa-link.py 9640769453 --file message.txt   # multi-line
```

Output is a `https://wa.me/...` link. Open it on the phone (or in WhatsApp Web),
the chat opens with the text filled in, press send. The message goes from Uday's
own number and lands in his normal WhatsApp.

Indian 10-digit numbers get `91` prefixed automatically.

### Why this rather than an API

| | wa.me link | WhatsApp Business API |
|---|---|---|
| Setup | none | Meta business verification, days |
| Cost | free | free tier then per-conversation |
| Sends from Uday's existing number | yes | no — needs a dedicated number |
| Message wording | anything | pre-approved templates only |
| Terms-of-service risk | none | none |
| Effort per candidate | one tap | fully automatic |

At current volume — a handful of candidates a day — one tap is cheaper than the
setup and the template-approval friction. The API becomes worth it past roughly
50 messages a day, or if messages need to go out unattended.

### What NOT to do

Driving WhatsApp Web with Playwright or Selenium to send automatically from a
personal number breaches WhatsApp's terms and risks the number being banned.
9885179008 is the number candidates are told to send videos to; losing it would
cost more than the automation saves.
