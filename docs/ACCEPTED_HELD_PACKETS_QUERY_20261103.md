# Callable accepted-file HELD research query (source-local only)

`tools/query_accepted_held_packets.py` is a **read-only local query**, not an
Explorer data file, reconciliation decision, accepted Work registry, full-source
coverage report, or model training corpus. It does not require network access,
an API key, a model, or any hosted service.

## Exact first inventory

| Reviewed accepted-main packet | Indexed source-local observations | Source file SHA-256 |
| --- | ---: | --- |
| Voyager S4 E1–E5 publisher guide (`proposals/research/voy-s4-e01-e05-guide-recheck-20261103/records.json`) | 5 guide-card headings/slots | `5653fc0baa4bb816ce741b2a1817425b2978d5baea9c41a288f3eff578901163` |
| Lore publisher editorials (`proposals/research/tng-lore-official-character-surface-20261103/records.json`) | 6 source-relative editorial observations | `b639c2b5af578c804c86b610f9315670e089d9c3d14cdfee1b078f16f929a04c` |
| TNG OPF 0090–0092 publisher crosschecks (`proposals/librarian/tng-opf-0090-0092-publisher-editions-20261103/records.json`) | 3 edition-specific metadata observations | `ac67d958c0c75aee0fe3979bba8cd145972cfaca40aca920748ceec55b892964` |

These are *14 observations in three disjoint evidence lanes*, **not 14 newly
admitted fictional Works**. Source file and original validator bytes are pinned
in the code. Each query rereads all three packets, checks exact file digests,
and executes their original research validators (including their upstream
crosswalk custody checks). A new source packet requires an explicit reviewed
code change, not a recursive directory scan.

The Voyager guide observation is not an episode viewing or an additional
discovered episode. Its original five synopsis candidates remain HELD and are
not included in query responses. Lore publisher retrospectives are editorial
observations, not authenticated episode evidence or proof about a living AI.
The literary `opf-local:0091` ISBN mismatch stays `UNRESOLVED`; a title/creator
match does not establish private eBook identity. No synopsis candidate prose,
cover URLs, image bytes, private file paths, or proprietary source bodies are
emitted. The original source-relative editorial observations and explicit
uncertainty statements are searchable, always labeled as such.

## Usage

From the checkout root:

```sh
python tools/query_accepted_held_packets.py --q Lore --limit 3
python tools/query_accepted_held_packets.py --kind VOY_GUIDE_CARD --limit 2 --offset 2
python tools/query_accepted_held_packets.py --id opf-crosscheck:opf-local:0091
python tools/query_accepted_held_packets.py --tag source-kind:publisher-guide
```

Results are deterministic in namespaced source-local `row_id` order. Filters
`--id`, `--kind`, `--status`, `--source-family`, and `--tag` are exact; `--q`
AND-matches source-relative text case-insensitively. Facet counts cover matches
before pagination. Each row includes source URL, source-record path and SHA,
source-relative locator, raw lineage label, HELD status, and zero-effect flags.
The source family's label does **not** establish an independent witness:
StarTrek.com and Paramount+ observations here share a corporate lineage.

## Admission and extension boundary

This CLI reads accepted *files that contain unadmitted proposals*. It does
not mutate them, append to the 1,214-row discovery search directory, alter the
20-card HELD Explorer shelf, resolve global entity identity, publish artwork or
synopsis, or update the close-read/semantic coverage ledger.

Before indexing another lane, independently review its source packet and
validator, pin both exact byte digests, define a source-relative mapping,
exercise negative tests (poisoned packet, validator failure, identity/coverage
promotion, duplicate IDs), and preserve query semantics. Do not simply add
new rows to a broad aggregate denominator.

Checks:

```sh
python -m unittest tests.test_accepted_held_packets_query -q
python -O -m unittest tests.test_accepted_held_packets_query -q
python tools/query_accepted_held_packets.py --id opf-crosscheck:opf-local:0091
```
