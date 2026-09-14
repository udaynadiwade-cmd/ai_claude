#!/usr/bin/env python3
"""post.py — send a finished post (text + optional card) to WEBHOOK_URL.

    python3 post.py posts/2026-09-14.md                 # send
    python3 post.py posts/2026-09-14.md --dry-run       # show payload, send nothing
    python3 post.py posts/2026-09-14.md --card out/2026-09-14.png

The post file: first line is `# <title>`, an optional `card:` line, then the
post body after the first blank line. See posts/_template.md.

Payload is JSON: {title, text, image_name, image_base64, date, author}.
If the old webhook expected different field names, change payload() only.
No third-party dependencies.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_env():
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def parse_post(path: Path):
    raw = path.read_text(encoding="utf-8")
    head, _, body = raw.partition("\n\n")
    title = re.sub(r"^#\s*", "", head.splitlines()[0]).strip()
    card = None
    for line in head.splitlines()[1:]:
        if line.lower().startswith("card:"):
            card = line.split(":", 1)[1].strip() or None
    return title, card, body.strip()


def payload(title, text, card_path, author):
    p = {"title": title, "text": text, "date": date.today().isoformat(), "author": author}
    if card_path:
        cp = Path(card_path)
        if not cp.is_absolute():
            cp = HERE / cp
        p["image_name"] = cp.name
        p["image_base64"] = base64.b64encode(cp.read_bytes()).decode()
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("post")
    ap.add_argument("--card", help="override the card: line in the post file")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    load_env()

    title, card, text = parse_post(Path(a.post))
    card = a.card or card
    body = payload(title, text, card, os.environ.get("AUTHOR", ""))

    if a.dry_run:
        shown = {**body, "image_base64": f"<{len(body.get('image_base64', ''))} chars>"} \
            if "image_base64" in body else body
        print(json.dumps(shown, indent=2, ensure_ascii=False))
        return 0

    url = os.environ.get("WEBHOOK_URL")
    if not url:
        sys.exit("WEBHOOK_URL is not set. Copy .env.example to .env and paste the URL from 30-config.md.")

    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"{r.status} {r.reason}")
        print(r.read().decode(errors="replace")[:500])
    log = HERE / "posts" / "log.md"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"| {date.today().isoformat()} | {title} | sent |\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
