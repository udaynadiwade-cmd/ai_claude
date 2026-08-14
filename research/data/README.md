# UNSPSC data — standing reference for category discovery

## What this is

`unspsc-segments-10-26.csv` is the founder-uploaded UNSPSC (United Nations Standard
Products and Services Code) extract, parsed once from the original `.xlsx` and saved
here so it survives past the ephemeral upload directory it arrived in. 13,605 rows,
four-level hierarchy: Segment → Family → Class → Commodity.

**Read the limitation before using this for anything:** the file covers **only
segments 10 through 26 of the roughly 55 in the full UNSPSC standard** — raw
materials, chemicals, and heavy industrial/vehicle machinery. It is missing segment 31
(Manufacturing Components — where bearings, fasteners, gaskets and seals actually
live) and everything from segment 27 onward: electronics, medical/lab, IT, food,
apparel, furniture, and all services categories. Do not treat an absence from this
file as evidence a category doesn't exist — check whether the relevant segment is
even present before concluding anything.

The 13 segments present, most codes first: Live Plant/Animal (8,266 — almost entirely
flower/plant species variants, not a business signal), Vehicles & Components (1,098),
Industrial Manufacturing Machinery (908), Mining/Well Drilling (834), Chemicals (561),
Mineral/Textile (465), Material Handling (451), Power Generation (266),
Resin/Rubber/Foam (197), Paper (159), Farming/Fishing/Forestry Machinery (141),
Building/Construction Machinery (131), Fuels/Lubricants (128).

To extend this properly: the complete UNSPSC (all ~55 segments) is a free public
download from UNDP (unspsc.org / undp.org/unspsc). Getting it would let this same
method reach segment 31 directly, plus electronics, medical and food — all currently
invisible to this analysis.

## How to use it for category discovery — the method that worked

This was applied once, in full, in `../2026-08-unspsc-screen.html`. The method:

1. **Segment and family-level scan first.** Group by segment, then family, sorted by
   commodity-code count. This finds where the taxonomy is deep — but code count is a
   measure of *how granular the standard gets there*, not of market size or
   opportunity. Flowers have 8,266 codes because UNSPSC gives every species its own
   code, not because flowers are a bigger business than vehicles.

2. **Class-level breakdown inside promising families.** This is where the real signal
   is — it shows the actual sub-structure (e.g. "Welding and soldering and brazing"
   splits cleanly into machinery / accessories / supplies, which is exactly the shape
   of a real distribution category).

3. **Apply the capital-equipment filter before scoring anything.** Tested against five
   separate families in this pass (material handling, industrial process machinery,
   power sources, farming machinery, construction machinery) and it held every time:
   **is this bought once and used for years, or consumed and reordered?** Deep,
   detailed taxonomy entries for forklifts, excavators, tractors and packaging lines
   all fail the pooling/distribution model for the same reason — they are financed or
   project-purchased, not restocked. Apply this filter first; it eliminates most of
   what looks promising on code-count alone.

4. **Then apply the standing framework** from the rest of this research series:
   fungibility (does one SKU serve many buyers unmodified — the reason bearings beat
   lubricants), demand lumpiness, stockout severity, deliverability, and whether the
   category is already served by a funded incumbent. None of this is in the CSV; it
   has to be researched per category once the CSV has narrowed the list.

5. **Cross-check market size externally.** The CSV has no revenue or market-size data
   — it is a pure classification taxonomy. Every number in the write-ups (bearings at
   $5.2–12.0 Bn, welding at $1.8–3.72 Bn) came from separate web research, not from
   this file. Use the CSV to find candidates; use search to size them.

## Quick reference — how to query it

```bash
# Search commodity/class/family titles for a keyword
grep -i "bearing" research/data/unspsc-segments-10-26.csv

# Count codes per segment
cut -d, -f1,2 research/data/unspsc-segments-10-26.csv | sort | uniq -c | sort -rn

# Count codes per family within a segment
awk -F, '$1==23000000' research/data/unspsc-segments-10-26.csv | cut -d, -f3,4 | sort | uniq -c | sort -rn
```

(Note: several titles contain commas inside quoted fields — for serious analysis,
reload with `csv.reader` / pandas rather than raw `awk`/`cut` field-splitting.)

## Findings on record from the one pass done so far

- **Welding consumables** — confirmed at class level, clean machine/accessory/supply
  split. Best new candidate found in this file.
- **Auto components** — confirmed combinatorially deep (389 codes in one family alone),
  validating why fitment complexity was scored as a real execution risk, not an
  overstated one.
- **Industrial lubricants** — surfaced as a candidate but downgraded: brand pull
  (Indian Oil, Castrol, Gulf already own retail distribution) likely defeats the
  fungibility the pooling model needs. Untested in the field.
- **Material handling, industrial process machinery, farming machinery, construction
  machinery** — all deep in the taxonomy, all ruled out on the capital-equipment
  filter.
- **Mining/well-drilling** — the single deepest segment in the file (834 codes),
  irrelevant regardless of depth — upstream oil & gas, no Hyderabad relevance.
- **Bearings and fasteners** — cannot be checked against this file. Segment 31 is
  missing. The existing #1 ranking stands on research from other sources, not on this
  taxonomy.

This file has now been examined at the segment and family level across all 13 present
segments. Further mileage from *this specific extract* is limited — the next real gain
requires either the complete UNSPSC file, or moving from desk research to the field
test already recommended (ten factory visits, bearings and welding together).
