# DS9 B008 — Paramount+ Season 7 nonduplicate source-card recheck, E12–E16

**Role:** DS9 source-only metadata worker. **Accepted selection base:** `main@1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b` (2026-11-03 UTC). **Disposition:** five nonduplicate source-local publisher-guide title/slot observations. No Source↔Work admission, episode-body read, approved synopsis, global identity, coverage event, or Pages effect.

## Source retrieval and actual processing

I opened the public, currently rendered [Paramount+ *Deep Space Nine* Season 7 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/), read and checked the contiguous cards **S7E12–S7E16** by their rendered heading and displayed season/episode slot, and compared them with the already accepted source-local publisher Season 7 CSV and deterministic discovery directory. This is a **same-publisher-family recheck**, not independent corroboration and not five new Works. The rendered descriptions were visible but **no description text or paraphrase is stored**; synopsis release is `HELD`.

The simultaneously open, **unaccepted** [Draft PR #326](https://github.com/thebrazenbeard/trek-data-core/pull/326) already proposes S7E7–S7E11 title/slot cards. An initial version of this B008 draft also repeated those five cards. The current exact proposal **excludes** rows `publisher:s7:ds9:006`–`010` and carries only rows `011`–`015`; #326 is a proposal, **not accepted evidence**. Its records, synopsis drafts and audit outcome must not be silently treated as accepted progress or a second independent source.

The current response's raw HTML was not obtained or archived. `fresh_raw_html_sha256=null` and `fresh_raw_html_captured=false` are intentional. The prior publisher CSV SHA-256 is `1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea`; the exact accepted discovery directory SHA-256 is `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`. These hashes verify **existing local inputs**, not a fresh raw publisher webpage, its underlying content-management data, or any episode cut.

| Source-local row | Rendered Paramount+ card (season slot) | Disposition |
| --- | --- | --- |
| `publisher:s7:ds9:011` | *The Emperor's New Cloak* — S7E12 | Same-family agreement |
| `publisher:s7:ds9:012` | *Field of Fire* — S7E13 | Same-family agreement |
| `publisher:s7:ds9:013` | *Chimera* — S7E14 | Same-family agreement |
| `publisher:s7:ds9:014` | *Badda-Bing, Badda-Bang* — S7E15 | Same-family agreement |
| `publisher:s7:ds9:015` | *Inter Arma Enim Silent Leges* — S7E16 | Same-family agreement |

## Overlap and material source discrepancy, deliberately excluded from this count

The excluded S7E8 card exposes a still-unresolved same-family discrepancy: Paramount+ prints **“The Siege of AR-555”** on its [episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/), while the franchise's [StarTrek.com preview](https://www.startrek.com/videos/episode-preview-the-siege-of-ar-558) says **“The Siege of AR-558.”** That issue belongs to Draft PR #326's source-card batch; here it is contextual **only** and is **not counted as a sixth B008 observation** or independently reconciled.

> **Hostile challenge:** Corporate product pages can carry stale or erroneous titles. A visible guide title does not independently authenticate the episode's on-screen title, broadcast identity, script, or edit. Resolving `AR-555` versus `AR-558` in the separate overlapping draft requires source-edition/reconciliation review, not a generator's string correction.

> **Coverage challenge:** This B008 tranche extends the earlier S7E2–E6 publisher-card recheck only to the nonduplicated E12–E16 portion; E7–E11 are held by the other unaccepted draft. It does **not** increase the already-accepted 1,214-row directory count, admit five Briefings, prove five distinct Works, or advance episode close-read coverage. The Director's primary-source hold remains in force.

## Batch verification and next frontier

The `observations.json` has exactly five contiguous, source-local card records with synopsis and coverage effects closed. `validate.py` pins both repository input checksums, the literal titles/slots, exact source URLs, excluded prior draft rows, and fail-closed schema/effect fields. `tests/test_ds9_s7_b008.py` challenges fabricated capture hashes, Work IDs, title substitutions, overlapping rows, synopsis approval, extra keys, and coverage promotion in ordinary and optimized Python. No copyrighted synopsis, transcript, still, or video was copied.

```bash
python3 proposals/research/ds9-s7-publisher-cards-b008-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_ds9_s7_b008.py'
python3 tools/validate.py
```

**Next source-only DS9 frontier:** S7E17–S7E25, after checking whether another accepted worker has already processed those exact source cards. Separate publisher metadata can be indexed; further synopsis or canonical Work promotion needs editorial, Librarian, and governed Source↔Work review. Full audiovisual research requires an authorized primary source.
