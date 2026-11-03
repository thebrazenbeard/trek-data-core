# DS9 B009 — Season 7 publisher-guide tail, E17–E25

**Role:** DS9 source-relative metadata worker. **Accepted base:** `main@5b59deec9cf832ed030f25bd09c6fd7c318efb90` (2026-11-03 UTC). **Status:** source-only candidate records; no accepted Source↔Work binding, Work admission, episode audiovisual/script reading, approved synopsis, global reconciliation, coverage event, or Pages effect.

## Actual source processing and lineage

I freshly opened and read the visible title and season/episode slot of nine contiguous cards on the [Paramount+ *Deep Space Nine* Season 7 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/): **S7E17–S7E25**. Each card was compared with the existing publisher Season 7 CSV and deterministic 1,214-row discovery directory. These are **same-corporate-publisher rechecks**, not nine new distinct Works or independent witnesses. The page's description blocks were visible, but no publisher description text, original synopsis paraphrase, transcript, still, or media was copied into these records. Synopsis state remains **HELD**.

The current guide's raw HTML was **not** captured, so `current_raw_html_sha256=null` is deliberate. The repository pins the accepted directory SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc` and historical Paramount CSV SHA-256 `1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea`. Those are existing artifact receipts, **not the new webpage body hash or an authenticated broadcast cut**.

The previously accepted source-only Season 7 tranches remain separate and are checked byte-for-byte: S7E7–E11 from former PR #326 and S7E12–E16 from former PR #334. This B009 batch starts at source-local row `publisher:s7:ds9:016`, so none of the 9 observations overlap those earlier spans. The concurrently open Draft PR #340 addresses **S7E12–E16** date-source variants and does not authorize treating those dates as accepted evidence here.

| Source-local row | Current Paramount guide card |
| --- | --- |
| `publisher:s7:ds9:016` | *Penumbra* — S7E17 |
| `publisher:s7:ds9:017` | *'Til Death Do Us Part* — S7E18 |
| `publisher:s7:ds9:018` | *Strange Bedfellows* — S7E19 |
| `publisher:s7:ds9:019` | *The Changing Face of Evil* — S7E20 |
| `publisher:s7:ds9:020` | *When It Rains...* — S7E21 |
| `publisher:s7:ds9:021` | *Tacking Into The Wind* — S7E22 |
| `publisher:s7:ds9:022` | *Extreme Measures* — S7E23 |
| `publisher:s7:ds9:023` | *The Dogs of War* — S7E24 |
| `publisher:s7:ds9:024` | *What You Leave Behind* — S7E25 |

## Finale presentation hold

Paramount+'s current guide has **one S7E25 card** for *What You Leave Behind*. The corporate franchise's [StarTrek.com anniversary article](https://www.startrek.com/news/what-you-leave-behind-aired-18-years-ago-today) describes the historical broadcast as a **two-hour series finale**. These statements can describe different presentation contexts rather than incompatible episodes. Neither licenses this worker to invent an additional S7E26, split one globally reconciled Work into two, assert the streaming cut's exact duration, or infer a franchise-wide denominator. The records explicitly retain `UNRESOLVED` split/edition identity.

> **Hostile challenge:** Guide order and card count do not establish a unique physical broadcast episode, a universal season ordinal, or exact source equivalence between a scheduled two-hour event and a current streaming presentation. Historical official anniversary commentary and the streaming guide share a corporate lineage; they are not independent corroboration of media content.

> **Coverage challenge:** Completing the visible Season 7 **metadata-card recheck** is not completion of DS9 Season 7 primary-source research. The nine titles already appear in the candidate directory. No governed Source↔Work, close-read, semantic evidence, continuity reconciliation, artwork license, or accepted coverage is generated.

## Validation and exact next frontier

`observations.json` contains precisely nine source-relative title/slot records plus a separate, held finale-presentation context. `validate.py` checks exact source URLs, accepted input hashes, prior S7E7–E16 non-overlap, literal titles/slots, close-schema admission gates and no fictitious S7E26. The adversarial test suite rejects forged source captures, Work IDs, descriptions, second-finale claims, extra fields, and coverage promotion, including optimized Python mode.

Raw JSON duplicate-key custody is explicitly enforced by `read_json(..., object_pairs_hook=unique_pairs)`. The regression harness now uses the same strict parser when feeding raw attacker-controlled JSON into `validate(data)`. Both the actual file-bound parser and normal/optimized process probes reject a forged `CLOSE_READ` followed by `NONE`, an asserted raw HTML capture followed by `false`, or a forged nested Work ID followed by `null`. A Python `dict` alone cannot prove the originating raw JSON was duplicate-free; source admission must use the strict file-bound parser.

```bash
python3 proposals/research/ds9-s7-tail-b009-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_ds9_s7_b009.py'
python3 tools/validate.py
```

**Next DS9 frontier:** The currently exposed Paramount+ Season 7 title/slot guide is exhausted through displayed E25. Further useful work requires an independently qualified source representation, production-script/episode custody, edition/part identity review, or documented editorial synopsis qualification—not another duplicate scrape. New primary audiovisual close-reading remains subject to the Director's source-admission hold.
