# LD L002 — official Season 2 episode-guide cards, source-only

**Batch:** `ld-s2-guide-l002-20261103`
**Role:** LD series worker
**Selection base:** accepted `main` `7e0c56e5bbef70296de034e5283ed6217e6e7f91`
**Observations SHA-256:** `98ef31e0e885df527b2684fb94d0d6513bf2b69813f8011370b950f7658e5881`
**Status:** unaccepted research proposal; **not** a Work, episode-reading, or coverage admission.

## Primary source actually read

- Paramount+ U.S. public **Season 2 episode guide**: <https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/2/>.
- Rendered primary guide was read on 2026-11-03, with ten cards and complete displayed descriptions, lines 107–160 of that retrieval's web-readable form. The five initial cards also have a previously accepted first-five *title/slot discovery* receipt (`proposals/discovery/modern-paramount-season2-first5-20261102/ld/`), which is the **same publisher lineage**, not independent confirmation.
- Fresh direct HTTP GET returned status 200, 273,095 bytes, SHA-256 `168764bebbde440545fb6471be24b3162d9b5718802eb6cdf0594f459419ed8c`. The raw page was inspected transiently and **was not committed or archived**. The reported digest is a historical retrieval receipt, **not independently replayable or a frozen source snapshot**. The page may change on future requests.
- Verified all ten card titles, `S2 E1` through `S2 E10` slots, and every listed literal mention within its **own** guide card's displayed description, using this HTTP HTML. Literal mentions reflect Paramount's published description, **not** that a person or object actually appears on screen.
- Existing same-family historical first-five discovery: `ld-observed-slots.csv` SHA-256 `603c969c7a2d82cd99d63610ca04371db0dbdeeb9dbef1aed21176178f2b4115`; `ld/bundle.json` SHA-256 `f7514d54a138df96c33264cc21510fabc74a1f954cf16bbf09bc432b77330c66`. Validator verifies both exact accepted files.

## Observed primary publisher-card titles

| Guide slot | Card title | Rendered text window |
| --- | --- | --- |
| S2 E1 | Strange Energies | 107–111 |
| S2 E2 | Kayshon, His Eyes Open | 112–116 |
| S2 E3 | We'll Always Have Tom Paris | 118–122 |
| S2 E4 | Mugato, Gumato | 123–127 |
| S2 E5 | An Embarrassment of Dooplers | 129–133 |
| S2 E6 | The Spy Humongous | 134–138 |
| S2 E7 | Where Pleasant Fountains Lie | 140–144 |
| S2 E8 | I, Excretus | 145–149 |
| S2 E9 | wej Duj | 151–155 |
| S2 E10 | First First Contact | 156–160 |

The authoritative locators for these observations are individual title/season/episode/description card groupings on the guide. Line windows are transient web-reader display positions and must not be mistaken for a stable edition's line numbers. The publisher spells a name **`Dr. T Ana`** in E3; that observed token is preserved literally rather than silently normalized. Every card has only a page-level artwork discovery lead; **no image URL, image bytes, licensing grant or display effect** is claimed.

## Explicit evidence and rights holds

- **Source → local card entity → source-relative observed mention**, not an accepted global Work or identity decision. No scenes, dialogue, streaming playback, scripts, full text, or semantic cross-work analysis were examined.
- The ten `literal_mentions` are tokens actually present in the **publisher's descriptions**, not confirmation of events or people in the episodes. There are no copied descriptions, recaps, synopses, or paraphrase candidates in the public batch.
- `synopsis_status = HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE`; `artwork_rights_status = UNKNOWN_HELD`; no asset URLs to display or hotlink. The guide page is a **discovery lead only**.
- `accepted_source_work_effect`, `accepted_work_effect`, `coverage_effect`, `public_synopsis_effect`, and `public_artwork_effect` all remain `NONE`. The ten observations **do not advance** `SOURCE_BOUND`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, or any episode denominator.

## Reproduction and falsifiers

```bash
python3 proposals/research/ld-s2-guide-l002-20261103/validate.py
python3 -m unittest discover -s proposals/research/ld-s2-guide-l002-20261103 -p 'test_*.py' -q
python3 -O -m unittest discover -s proposals/research/ld-s2-guide-l002-20261103 -p 'test_*.py' -q
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

The closed schema and pinned source/local IDs reject duplicate raw JSON keys; unsupported provenance, rights, or coverage claims; fabricated identity; wrong/missing/reordered cards; incorrect titles/slots or publisher mentions; and substituted artwork sources. Code-embedded pins protect the proposal's declared contents, **not external publisher truth**; an independent reviewer should re-open the original guide and challenge the pins themselves.

**Next frontier:** Lower Decks S3 E1–10 official guide, if still unclaimed at freshly accepted `main` plus open PR check. No merge authorization is inferred from this source read.
