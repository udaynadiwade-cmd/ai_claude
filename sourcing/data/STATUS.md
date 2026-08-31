# Data status

What is actually in `data/`, where it came from, and what is still missing.
Regenerate this picture at any time with:

```bash
cd tools && python3 fetch_rates.py status
```

## Populated

| Dataset | Source | Contents | Refresh |
|---------|--------|----------|---------|
| `data/hs/` | WCO Harmonized System 2022, via the public-domain `datasets/harmonized-system` package (UN Comtrade extraction) | 6,939 codes — 97 chapters, 1,229 headings, 5,613 subheadings, across 21 sections | `python3 tools/fetch_hs.py` (annual) |

This gives real classification: `hs_lookup.py` resolves any code to its heading and
section, rejects malformed and non-existent codes, and searches descriptions. It is
also what `landed_cost.py` validates `--hsn` against.

It contains **no duty rates**, by design — see below.

## Not populated

Duty rates, exchange rates, import policy and freight indices are **not** in this
repository and are not bundled with it. Each has a working fetcher; none can run
from a network that cannot reach the source.

| Dataset | Fetcher | Source |
|---------|---------|--------|
| `data/rates/tariff/` | `fetch_rates.py tariff --hsn CODE` | ICEGATE Custom Duty Calculator |
| `data/rates/fx/` | `fetch_rates.py fx` | CBIC notified exchange rates (ERAM) |
| `data/rates/freight/` | `fetch_rates.py freight` | Drewry World Container Index |

### Why they are empty here

The environment this was built in refuses outbound connections to every
government and trade host at the network egress proxy. Verified three ways:

```
curl      https://www.icegate.gov.in/   -> 403 to CONNECT (policy denial)
WebFetch  https://www.cbic.gov.in/      -> EGRESS_BLOCKED
Chromium  https://www.icegate.gov.in/   -> net::ERR_TUNNEL_CONNECTION_FAILED
```

`raw.githubusercontent.com` and `pypi.org` are the only reachable hosts, which is
why the HS nomenclature could be fetched and nothing else could.

Run the fetchers from a network with normal outbound access and they will populate
`data/rates/`. Nothing else needs to change.

### What the code does about it

No fetcher writes a value it did not receive. An unreachable source raises
`EgressBlocked`, the command exits non-zero, and any previously fetched data keeps
its original timestamp. Downstream, `landed_cost.py` prints a `RATE PROVENANCE`
block showing where every rate came from — `command line`, `config file`,
`ICEGATE, fetched <date>`, or `unset` — warns when BCD or IGST defaulted to zero,
and `--strict` exits non-zero unless both came from a fetched source.

The alternative — shipping a snapshot of duty rates — would be worse. Rates change
with every effective-rate notification, and a stale bundled figure that looks
authoritative is exactly how a Bill of Entry gets filed on a wrong number.
