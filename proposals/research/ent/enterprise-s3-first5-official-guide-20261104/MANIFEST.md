# Enterprise Season 3, official publisher-guide E01–E05 — HELD

**Batch:** `ENT.PPLUS.S3.FIRST5.GUIDE.20261104`

**Role:** ENT series research partition, source-relative metadata and original publisher-synopsis paraphrases only.

**Accepted-main baseline:** `3028765359001b90bc3e6b5c1835ee283b326e91` (2026-11-04 read-only `git ls-remote`). No accepted Source, Work, reconciliation, coverage, denominator or public Explorer effect.

## Collision and source selection

Accepted main already contains the candidate metadata roster `proposals/discovery/legacy-paramount-season3-20261102/ent/bundle.json` (SHA-256 `ae106b332e3e2c4d966b544ad6c31d9deb04c7f6843533519d79f93c2ebc9358`) with 24 Season 3 episode slots. I found **no held ENT S3 description-level research tranche** in the local accepted-main research tree or current open PR title list; ENT S2 has an open separate proposal, and Lower Decks S4/S5 already have ten-card analyses. Thus this packet adds *description-level detail to existing candidate slots*, not 24 newly discovered episodes.

## Exact complete first-party source read

- [Paramount+ official *Enterprise* Season 3 guide](https://www.paramountplus.com/shows/enterprise/episodes/3/).
- Fresh **HTTP 200**, Date `Wed, 04 Nov 2026 21:17:58 GMT`; observed `2026-11-04T21:17:58.093971+00:00`.
- Complete accessible HTML response: **308,190 bytes**, SHA-256 `227c1cbcbafd29cabb62ff83e73cccd2466604ab0e3c4462920badf774453391`.
- `source_probe.py` traversed and fingerprinted all **24** publisher cards and their description text in memory. It verifies title, season and episode badges, `aa-link` analytics ordinal, video route, publisher datetime and description source line. The first five descriptions were actually read for **five** original brief paraphrases, totaling **951** publisher-description characters inspected.
- Raw HTML and exact publisher paragraphs were not committed. No video, audio, captions, scripts, or image bytes were retrieved or inspected.

| Source-local S3 card | Official guide title | HTML description line | Exact publisher-description SHA-256 |
|---|---|---:|---|
| E01 | The Xindi | 1500 | `09f7401e2e1b1c9c9ea481974abdeed46792c04451d52a430f08d28e8663bf32` |
| E02 | Anomaly | 1528 | `cfe67589d19c28dd42e2eaf988ca7427e970d8d6331350b1be8261bcbacc3faa` |
| E03 | Extinction | 1556 | `95c0b5b6c23ac338f52cef3c8f6006b3cacbf554683d2dbe0a1f161435b9fedd` |
| E04 | Rajiin | 1584 | `fe5c2f6e438c215a0934a1141450089cac2238f33e3081ad7ce3514118362f3f` |
| E05 | Impulse | 1612 | `0b0fd0666adfbe98c16657fb2a94f55f2c7ceec15e255917d0baabf55a4d3c10` |

The source line numbers apply **only to this exact retrieved HTML response**. Dynamic publisher markup may change. The remaining 19 cards are context metadata/fingerprints, not 19 synopsis analyses. The 24 source-relative cards have zero canonical Work identities.

## Provenance boundary and falsifiers

Each local claim follows `publisher guide → source-local episode card → precise description fingerprint and line → original synopsis paraphrase → PUBLISHER_DESCRIBES` assertion. The candidate title roster and this guide belong to **the same publisher family**; their agreement is not independent corroboration.

> **Hostile challenge:** An official description can be editorially incomplete, misleading, or stale. It establishes what Paramount+ stated, not what necessarily happened in the moving-image work. Reading the complete episode-guide webpage does not constitute an audiovisual episode CLOSE_READ or a verified plot transcription.

No complete copyrighted source prose, clips, subtitle files, e-books, or original image bytes were redistributed. No artwork license or public display permission is asserted. `records.json` has explicit `NONE` effects for accepted Source/Work, coverage, denominator, global reconciliation and Explorer synopsis release.

## Deterministic validation

```bash
python3 proposals/research/ent/enterprise-s3-first5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s3-first5-official-guide-20261104 -p test_validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests
git diff --check
```

The validator pins the exact observed HTML receipt; separate upstream title roster digest; all 24 source-route and description fingerprints, ordinal and date shapes; the five source-relative entity/evidence/assertion joins; and the protected hold boundaries. Its hostile tests challenge double counts, title/ordinal drift, digest tampering, false Work binding, false close-read/coverage, and misleading independent witnesses. Reproducing against the live publisher page should compare normalized cards, not demand immutable raw-HTML bytes.

**Exact next frontier:** ENT S3 publisher descriptions E06–E10, with a new complete-page receipt and five original paraphrases in a **separate** held batch, or an authenticated, rights-compatible access route for true audiovisual content analysis. No accepted integration has been performed.
