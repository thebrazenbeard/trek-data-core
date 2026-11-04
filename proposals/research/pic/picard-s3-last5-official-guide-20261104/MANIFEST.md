# Picard Season 3 — official publisher-guide E06–E10, held

**Batch:** `PIC.PPLUS.S3.LAST5.GUIDE.20261104`

**Role:** PIC episode metadata/source-relative synopsis worker
**Disposition:** `HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE` — **zero accepted Source/Work, CLOSE_READ, coverage, denominator, reconciliation, or Explorer release effects**.

## Source retrieval and actual processing

On 2026-11-04 at `21:06:01.532629+00:00`, a fresh read-only HTTPS GET retrieved the **complete 272,699-byte** HTML response for Paramount+'s first-party [Star Trek: Picard, Season 3 episode guide](https://www.paramountplus.com/shows/star-trek-picard/episodes/3/) (HTTP 200; response Date `Wed, 04 Nov 2026 21:06:01 GMT`). The raw response SHA-256 was:

`c938f6fe567d1782f7c2130acf051ee09867adcf8abf3bc6cae8ef305c8035d4`

The in-memory extractor from the predecessor batch traversed all **10** cards and publisher descriptions, then the E06–E10 description texts were actually read to write **five original, brief paraphrases** in `records.json`. The five publisher source descriptions totaled **1,174 characters**. No raw page text, full episode, transcript, video, audio, or image was downloaded into or committed with this packet. Video routes are card metadata only; not content-read evidence.

The HTML response digest differs from the E01–E05 receipt's raw digest (`54f51850043a1073f8ac4f4e68a22b6acf2bd5b70ad416adce695c36d9e659b3`), but the **ten normalized publisher-card metadata and description fingerprints match exactly**. Both observations share `publisher:paramountplus.com` lineage; **two retrievals are not independent corroboration**.

## Scope, locators, and distinction from E01–E05

The predecessor is the separate `picard-s3-first5-official-guide-20261104/records.json` packet, exact file SHA-256 `fdbb21d3b168b6375ef304fd70a4a55dc964213ac8102cf5929d4d689df5a948`, local commit `da3b01eeca623bde26642d9177dbf7aad4b24b25`. It contains E01–E05 source-relative description analyses **plus ten-card inventory**. This batch contributes only E06–E10 analyses; ten-card inventory is not ten new analyses or ten verified Works.

| Episode card ordinal | Guide title | HTML description line | Publisher-description SHA-256 |
|---|---|---:|---|
| 6 | The Bounty | 1628 | `947a9d13f43590ed96eeda4079f82642db2c9fd61e036a737673ff2488e54a1d` |
| 7 | Dominion | 1656 | `fee4ac7d2bd80d0a056254310226ac9b78a3b00a92f5b598dc7f1248da3c6f1c` |
| 8 | Surrender | 1684 | `7b302beb35512f2e53b81b1cd54a49f0bbece229ef0bc1c4fbd91cd29b0c9801` |
| 9 | Võx | 1712 | `42511bacc17ff8c051d2a0d81b2f9ba5a3f24b26332e10095c07928ae1449a80` |
| 10 | The Last Generation | 1740 | `a2c429168eb01b95e1999e2b8aea942e6f3126bc3825e3672e67dc37c0ff332f` |

Line numbers are locators **relative to the exact retrieved HTML**; a live webpage may shift. The per-card dates, source routes, ordinals, description lengths, entity/evidence IDs, and synopsis paraphrases reside in `records.json`. Typed assertions say only `PUBLISHER_DESCRIBES`: publisher-guide descriptions are **not independently validated episode-event truth**. Every entity remains source-local, with `canonical_work_id: null`.

## Deterministic validation and hostile checks

```bash
python3 proposals/research/pic/picard-s3-last5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/pic/picard-s3-last5-official-guide-20261104 -p 'test_validate.py'
python3 proposals/research/pic/picard-s3-first5-official-guide-20261104/validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests
```

Validator pins the exact earlier file bytes and predecessor commit, source receipt, official-card metadata and description fingerprints, source lineage, non-overlap across local evidence IDs, E06–E10 order, original paraphrase bounds and all protected hold effects. Negative tests deliberately attempt card drift, copied-ID reuse, double count, Work/coverage claims, and false independent witness promotion.

## Unresolved, and next research frontier

No episode audiovisual content or authenticated full transcript was read: **no CLOSE_READ, entity-linking conclusion, global Work identity resolution or coverage increment is warranted.** This local proposal is not accepted `main`. For PIC Season 3, a separate authenticated, rights-compatible full-episode/transcript access path would be needed before audiovisual CLOSE_READ. Alternatively proceed with another underrepresented first-party publisher-guide tranche as **discovery/source-relative metadata only**, preserving independent source lineages and distinct denominators.
