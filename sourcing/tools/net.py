"""HTTP layer for the data fetchers.

Two things matter here beyond "get the bytes":

1. **Honest failure classification.** A sourcing agent that cannot tell
   "the portal says this HS line has no ADD" from "I never reached the portal"
   will eventually file a Bill of Entry on a number it invented. Every failure
   is therefore classified, and `EgressBlocked` is raised as its own type.
2. **Corporate-proxy tolerance.** These fetchers are expected to run behind a
   MITM proxy with a private CA (very common on a company laptop and on CI).
   Set REQUESTS_CA_BUNDLE or pass ca_bundle -- never disable verification.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

try:
    import requests
except ImportError:  # pragma: no cover - dependency is declared in requirements
    requests = None

DEFAULT_UA = (
    "sourcing-manager/1.0 (+import compliance tooling; contact: set SOURCING_UA_CONTACT)"
)
RETRYABLE_STATUS = (429, 500, 502, 503, 504)


class FetchError(RuntimeError):
    """Base class for every fetch failure."""

    def __init__(self, url: str, detail: str):
        self.url = url
        self.detail = detail
        super().__init__(f"{detail} [{url}]")


class EgressBlocked(FetchError):
    """The request never reached the origin: proxy/policy/DNS refusal.

    Distinct from an HTTP error so callers never treat "unreachable" as
    "absent". A rate that could not be fetched must stay unset.
    """


class UpstreamError(FetchError):
    """The origin answered, but not usefully (4xx/5xx after retries)."""


@dataclass
class Response:
    url: str
    status: int
    text: str
    content: bytes
    elapsed_s: float
    final_url: str = ""
    headers: dict = field(default_factory=dict)


# Signatures of a request that died before the origin saw it.
_BLOCK_MARKERS = (
    "tunnel connection failed",
    "err_tunnel_connection_failed",
    "proxyerror",
    "cannot connect to proxy",
    "connection refused",
    "name or service not known",
    "temporary failure in name resolution",
    "nodename nor servname",
    "max retries exceeded",
)


def classify(exc: Exception, url: str) -> FetchError:
    msg = str(exc).lower()
    if any(m in msg for m in _BLOCK_MARKERS):
        return EgressBlocked(url, f"blocked before reaching origin: {type(exc).__name__}")
    if "certificate" in msg or "sslerror" in msg or "pkix" in msg:
        return EgressBlocked(
            url,
            "TLS interception not trusted: point REQUESTS_CA_BUNDLE at your proxy CA "
            "(never disable verification)",
        )
    return UpstreamError(url, f"{type(exc).__name__}: {exc}")


class Fetcher:
    """Thin, polite HTTP client with retry and backoff."""

    def __init__(
        self,
        timeout: int = 45,
        retries: int = 3,
        backoff: float = 2.0,
        user_agent: str = "",
        ca_bundle: str = "",
        min_interval_s: float = 1.0,
    ):
        if requests is None:
            raise RuntimeError("requests is not installed: pip install -r requirements.txt")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.min_interval_s = min_interval_s
        self._last_call = 0.0
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent or os.environ.get(
            "SOURCING_UA", DEFAULT_UA
        )
        bundle = ca_bundle or os.environ.get("REQUESTS_CA_BUNDLE", "")
        if bundle:
            self.session.verify = bundle

    def _throttle(self) -> None:
        """Never hammer a government portal; they rate-limit and then ban."""
        gap = time.monotonic() - self._last_call
        if gap < self.min_interval_s:
            time.sleep(self.min_interval_s - gap)
        self._last_call = time.monotonic()

    def get(self, url: str, **kwargs) -> Response:
        last: Exception | None = None
        for attempt in range(1, self.retries + 1):
            self._throttle()
            started = time.monotonic()
            try:
                r = self.session.get(url, timeout=self.timeout, **kwargs)
            except Exception as exc:  # noqa: BLE001 - re-raised as a typed FetchError
                err = classify(exc, url)
                if isinstance(err, EgressBlocked):
                    raise err from exc
                last = exc
            else:
                if r.status_code in RETRYABLE_STATUS and attempt < self.retries:
                    last = UpstreamError(url, f"HTTP {r.status_code}")
                elif r.status_code >= 400:
                    if r.status_code in (403, 407) and "proxy" in r.text.lower()[:400]:
                        raise EgressBlocked(url, f"proxy refused with HTTP {r.status_code}")
                    raise UpstreamError(url, f"HTTP {r.status_code}")
                else:
                    return Response(
                        url=url,
                        status=r.status_code,
                        text=r.text,
                        content=r.content,
                        elapsed_s=round(time.monotonic() - started, 3),
                        final_url=r.url,
                        headers=dict(r.headers),
                    )
            if attempt < self.retries:
                time.sleep(self.backoff ** attempt)
        raise UpstreamError(url, f"exhausted {self.retries} attempts: {last}")


def browser_get(url: str, wait_selector: str = "", timeout_ms: int = 45000) -> str:
    """Render a JS-heavy portal page and return its HTML.

    ICEGATE, BIS Manakonline and the DGFT portals build their tables client-side,
    so a plain GET returns an empty shell. Requires: pip install playwright &&
    playwright install chromium.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "playwright is not installed: pip install playwright && playwright install chromium"
        ) from exc

    exe = os.environ.get("PLAYWRIGHT_CHROMIUM_PATH", "")
    launch = {"args": ["--no-sandbox"]}
    if exe:
        launch["executable_path"] = exe

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch)
        try:
            page = browser.new_page(user_agent=os.environ.get("SOURCING_UA", DEFAULT_UA))
            try:
                page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            except Exception as exc:  # noqa: BLE001
                raise classify(exc, url) from exc
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=timeout_ms)
            return page.content()
        finally:
            browser.close()
