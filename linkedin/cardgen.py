#!/usr/bin/env python3
"""cardgen.py — renders the image card that goes with a post.

>>> REPLACE THIS FILE with the Python block from the old 10-cardgen.md. <<<
The design lives there; this is only a placeholder so /daily-post runs
end-to-end on day one. Keep the same command-line contract so post.py and
the skill keep working:

    python3 cardgen.py --title "Hook line" --body "one or two lines" --out out/2026-09-14.png

Prints the output path. Exit non-zero on failure.

Placeholder behaviour: writes a PNG via Pillow if installed, otherwise an
SVG next to the requested path (post.py accepts either).
"""
import argparse
import sys
import textwrap
from pathlib import Path

W, H = 1200, 1200
BG, FG, ACCENT = "#0B1F3A", "#FFFFFF", "#F5A623"
BRAND = "Befach  ·  Better. Faster. Cheaper."


def render_svg(title, body, out):
    tl = textwrap.wrap(title, 26)[:4]
    bl = textwrap.wrap(body, 44)[:5]
    y = 320
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
             f'<rect width="{W}" height="{H}" fill="{BG}"/>',
             f'<rect x="80" y="200" width="120" height="12" fill="{ACCENT}"/>']
    for line in tl:
        parts.append(f'<text x="80" y="{y}" font-family="Helvetica,Arial" font-size="72" '
                     f'font-weight="700" fill="{FG}">{_esc(line)}</text>')
        y += 86
    y += 40
    for line in bl:
        parts.append(f'<text x="80" y="{y}" font-family="Helvetica,Arial" font-size="38" '
                     f'fill="{FG}" opacity="0.85">{_esc(line)}</text>')
        y += 52
    parts.append(f'<text x="80" y="{H-90}" font-family="Helvetica,Arial" font-size="30" '
                 f'fill="{ACCENT}">{_esc(BRAND)}</text></svg>')
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def render_png(title, body, out):
    from PIL import Image, ImageDraw, ImageFont  # noqa
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    try:
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 72)
        small = ImageFont.truetype("DejaVuSans.ttf", 38)
        foot = ImageFont.truetype("DejaVuSans.ttf", 30)
    except OSError:
        big = small = foot = ImageFont.load_default()
    d.rectangle([80, 200, 200, 212], fill=ACCENT)
    y = 250
    for line in textwrap.wrap(title, 26)[:4]:
        d.text((80, y), line, font=big, fill=FG)
        y += 86
    y += 40
    for line in textwrap.wrap(body, 44)[:5]:
        d.text((80, y), line, font=small, fill=FG)
        y += 52
    d.text((80, H - 120), BRAND, font=foot, fill=ACCENT)
    img.save(out)
    return out


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--body", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        path = render_png(a.title, a.body, out.with_suffix(".png"))
    except ImportError:
        path = render_svg(a.title, a.body, out.with_suffix(".svg"))
    print(path)


if __name__ == "__main__":
    sys.exit(main())
