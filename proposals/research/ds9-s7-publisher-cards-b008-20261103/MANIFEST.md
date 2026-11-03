# DS9 B008 — Paramount+ Season 7 source-card recheck, E7–E16

**Role:** DS9 source-only metadata worker. **Accepted selection base:** `main@1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b` (2026-11-03 UTC). **Disposition:** ten source-local publisher-guide title/slot observations. No Source↔Work admission, episode-body read, approved synopsis, global identity, coverage event, or Pages effect.

## Source retrieval and actual processing

I opened the public, currently rendered [Paramount+ *Deep Space Nine* Season 7 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/), read and checked its contiguous cards **S7E7–S7E16** by their rendered heading and displayed season/episode slot, and compared them with the already accepted source-local publisher Season 7 CSV and the deterministic discovery directory. This is a **same-publisher-family recheck**, not independent corroboration and not ten new Works. The rendered descriptions were visible but **no description text or paraphrase is stored**; synopsis release is `HELD`.

The current response's raw HTML was not obtained or archived. `fresh_raw_html_sha256=null` and `fresh_raw_html_captured=false` are intentional. The prior publisher CSV SHA-256 is `1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea`; the exact accepted discovery directory SHA-256 is `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`. These hashes verify **existing local inputs**, not a fresh raw publisher webpage, its underlying content-management data, or any episode cut.

| Source-local row | Rendered Paramount+ card (season slot) | Disposition |
| --- | --- | --- |
| `publisher:s7:ds9:006` | *Once More Unto the Breach* — S7E7 | Publisher title/slot agrees with previous publisher directory |
| `publisher:s7:ds9:007` | *The Siege of AR-555* — S7E8 | **Held same-family title conflict**, see below |
| `publisher:s7:ds9:008` | *Covenant* — S7E9 | Same-family agreement |
| `publisher:s7:ds9:009` | *It's Only A Paper Moon* — S7E10 | Same-family agreement |
| `publisher:s7:ds9:010` | *Prodigal Daughter* — S7E11 | Same-family agreement |
| `publisher:s7:ds9:011` | *The Emperor's New Cloak* — S7E12 | Same-family agreement |
| `publisher:s7:ds9:012` | *Field of Fire* — S7E13 | Same-family agreement |
| `publisher:s7:ds9:013` | *Chimera* — S7E14 | Same-family agreement |
| `publisher:s7:ds9:014` | *Badda-Bing, Badda-Bang* — S7E15 | Same-family agreement |
| `publisher:s7:ds9:015` | *Inter Arma Enim Silent Leges* — S7E16 | Same-family agreement |

## Material discrepancy, deliberately unresolved

Paramount+ currently prints **“The Siege of AR-555”** for S7E8, including on its [episode page](https://www.paramountplus.com/shows/video/mIdm1LceoK_eeqSuaO8_jl7G_QNJuhi6/). The franchise's official [StarTrek.com preview](https://www.startrek.com/videos/episode-preview-the-siege-of-ar-558) instead titles the episode **“The Siege of AR-558”**. Those are different source-relative title strings within the broader Paramount franchise/distribution family; they are **not** two independent witnesses and this worker has not resolved the governed Work title. The previous CSV and current Paramount+ guide use the same `AR-555` spelling. The separate StarTrek.com title is stored as a contested source-relative locator, never silently substituted into the publisher row.

> **Hostile challenge:** Corporate product pages can carry stale or erroneous titles. A visible guide title does not independently authenticate the episode's on-screen title, broadcast identity, script, or edit. Resolving `AR-555` versus `AR-558` requires source-edition/reconciliation review, not a generator's string correction.

> **Coverage challenge:** This B008 tranche extends the earlier S7E2–E6 publisher-card recheck to E7–E16. It does **not** increase the already-accepted 1,214-row directory count, admit ten Briefings, prove ten distinct Works, or advance episode close-read coverage. The Director's primary-source hold remains in force.

## Batch verification and next frontier

The `observations.json` has exactly ten contiguous, source-local card records with synopsis and coverage effects closed. `validate.py` pins both repository input checksums, the literal titles/slots, exact source URLs, unresolved title disagreement, and fail-closed schema/effect fields. `tests/test_ds9_s7_b008.py` challenges fabricated capture hashes, Work IDs, title correction, synopsis approval, extra keys, and coverage promotion in ordinary and optimized Python. No copyrighted synopsis, transcript, still, or video was copied.

```bash
python3 proposals/research/ds9-s7-publisher-cards-b008-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_ds9_s7_b008.py'
python3 tools/validate.py
```

**Next source-only DS9 frontier:** S7E17–S7E25, after checking whether another accepted worker has already processed those exact source cards. Separate publisher metadata can be indexed; further synopsis or canonical Work promotion needs editorial, Librarian, and governed Source↔Work review. Full audiovisual research requires an authorized primary source.
