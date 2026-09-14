# Getting the writer read access to befach.com

## What blocks it

Every product URL on befach.com returns the same 99,741-byte page to a script:
a "Quick check" shell that renders nothing server-side. The gate is
Cloudflare Turnstile:

    GET https://befach.com/api/human/challenge
    {"mode":"turnstile","siteKey":"0x4AAAAAAEr8anU8T-yg37Ip"}

Turnstile is a real CAPTCHA. There is no header or cookie a script can send to
satisfy it, by design. Verified closed, on 2026-09-14:

| Route | Result |
|---|---|
| `GET /product/<id>?w=china&q=...` | gate |
| `GET /product/<id>` (canonical, in sitemap) | gate |
| RSC fetch (`RSC: 1`) | gate |
| `/api/product/<id>`, `/api/products`, `/api/catalog` | 404 |
| `/products.json`, `/feed.xml`, `/sitemap-products.xml` | 404 |
| `/sitemap.xml` | 200 — 5,060 URLs, **no prices** |
| Headless Chromium | no network path from this environment |

Note `robots.txt` already disallows `/*?*q=`, the URL shape used when sharing a
product from search. The canonical `/product/<id>` is the one in the sitemap.

**Not an option:** routing requests through a CAPTCHA-solving service. Those are
third-party farms; it would put the catalog through someone else's hands and
would be defeating your own control rather than opening it.

## Three doors, any one of which works

`catalog.py` already speaks all three. Set one in `linkedin/.env`.

### 1. Catalog export — simplest, no network, no gate
Dump the catalog (or just the SKUs worth posting about) to JSON on a schedule
and drop it somewhere this repo can read, including a synced Drive folder.

    CATALOG_EXPORT=/path/to/catalog.json

Shape — a list, or `{"products": [...]}`:

```json
[{"id":"1601814328302","title":"AI smart glasses","currency":"INR",
  "exw":4200,"duty":840,"freight":610,"landed":5650,"moq":50}]
```

### 2. Read-only product API — best long-term
Add an endpoint on befach.com that returns the landed-cost breakup for one SKU,
authenticated by a bearer key, and exempt its path from the challenge.

    CATALOG_API=https://befach.com/api/internal/products
    CATALOG_API_KEY=<key>

### 3. Cloudflare WAF skip rule — fastest if you want it today
In the Cloudflare dashboard for befach.com, add a WAF custom rule:

    If  http.request.headers["x-befach-automation"][0] eq "<long random token>"
    Then  Skip → All remaining custom rules, and skip Turnstile

Then:

    CATALOG_URL=https://befach.com
    CATALOG_BYPASS_TOKEN=<the same long random token>

Treat the token like a password: it is a standing bypass of your own bot
protection. Rotate it if it leaks, and keep it out of git — `.env` is ignored.

## Check it works

    python3 linkedin/catalog.py 1601814328302
    python3 linkedin/catalog.py 1601814328302 --field landed

If the channel is still challenged, `catalog.py` says so rather than returning
a page of HTML.
