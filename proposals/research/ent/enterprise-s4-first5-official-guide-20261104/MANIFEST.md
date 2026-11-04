# Enterprise Season 4 E01–E05 — first-party publisher-guide descriptions, HELD

**Batch:** `ENT.PPLUS.S4.FIRST5.GUIDE.20261104`

**Role:** ENT series research worker. Five original source-relative publisher-guide synopsis proposals; no audiovisual episode close reads.

**Authority check:** GitHub accepted `main` was `3028765359001b90bc3e6b5c1835ee283b326e91` on 2026-11-04. Existing accepted Season 4 [Paramount discovery](../../../discovery/publisher-season4-20261102/ent/bundle.json) had 22 `CANDIDATE` slots but zero Work binding or coverage; its exact file SHA-256 is `15dcc53ab83df5cf0dcf602a6938588b290c16217c0e36fb0375489b077c0e17`. Open relevant ENT PR titles #516, #520, #528 concern held S3 E01–E20, not Season 4. A separate S3 E21–E24 local packet is also held. This S4 research branch comes directly from accepted `main`, not any proposed S3 stack.

## Fresh full publisher-guide source

At `2026-11-04T22:06:53.474398+00:00`, fetched the complete [Paramount+ *Enterprise* Season 4 guide](https://www.paramountplus.com/shows/enterprise/episodes/4/) read-only: HTTP 200, response Date `Wed, 04 Nov 2026 22:06:53 GMT`, **301,606 bytes**, raw SHA-256 `e0a5c2910e2f9cd43a3316d1bbbc06774c9d76eec422829f0f60fd9630eb6392`.

The parser traversed all 22 cards and full in-page description strings. This does **not** mean 22 episode analyses were completed. The five E01–E05 description strings, **712 source-text characters total**, were read and rendered as five original concise paraphrases linked to local entities, source-relative evidence and `PUBLISHER_DESCRIBES` assertions. No raw page, full publisher description paragraphs, images, scripts, captions, or episode videos were committed.

| Source-local card | Display title | HTML anchor / description lines | Exact description SHA-256 |
|---|---|---|---|
| S4E01 | Storm Front, Pt. 1 | 1482 / 1500 | `59aa440296569e80ad659b6fa4bcfef1d5d53e9ac94cc39e520859daf374d9e1` |
| S4E02 | Storm Front, Pt. 2 | 1510 / 1528 | `877563d86183bc5e724c543b35a2b297acfbf4cb347999d4dd95cf8f5fe783ac` |
| S4E03 | Home | 1538 / 1556 | `2df3fc33e639774b86deef2623e5d4b19e12dd38e9427d41ba05f70ac7535ff5` |
| S4E04 | Borderland | 1566 / 1584 | `42275b6146ea5b96a24a2c08dd6d4cba58184522a68277c63d9405026f4c7cd7` |
| S4E05 | Cold Station 12 | 1594 / 1612 | `bc568c551852e4b2cdfae7af0c8e8aba7bf9a7eba8c7ba98d82f824205ce534f` |

Line numbers are source-relative to this exact mutable HTTP response; future dynamic HTML may shift them. Publisher `datetime` strings are retained literally without assuming their broadcast or distribution semantics. Linked `/shows/video/.../` URLs are unrequested metadata locators, not watched content.

## Falsifier found on the same official page

The final E22 source card contains an internal capitalization variant: display/analytics leaf title **“These Are the Voyages”**, but analytics series title **“These Are The Voyages”**. This was observed in the complete official page while processing the first five. It is explicitly preserved in `source_internal_title_variants`, its raw field values in `all_22_guide_cards`, and a hostile regression. The parser tolerates only capitalization-equivalent variants and rejects genuinely divergent titles.

> **Hostile review:** A source-internal capitalization mismatch must not be silently normalized into canonical identity. A publisher description is proof of what a publisher says, not independent episode-content verification. The accepted Season 4 discovery bundle itself comes from the same Paramount publisher lineage, so it is not another witness.

No Source/Work admission, canonical reconciliation, episode `CLOSE_READ`, governed coverage/denominator, public Explorer synopsis effect, media/cover art rights claim, merge or deployment occurred.

## Deterministic verification

```bash
python3 proposals/research/ent/enterprise-s4-first5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s4-first5-official-guide-20261104 -p test_validate.py -q
python3 tools/validate.py
python3 -m unittest discover -s tests -q
git diff --check
```

The validator pins accepted discovery's file digest and 22 candidate titles, every source-card description fingerprint and video metadata route, source byte/time hash, exact E22 variant, five evidence triples and protected `NONE` effects. Synthetic parser tests reject incomplete 21-card sources and substantive title mismatches; accepted case-only source conflict stays unresolved.

**Exact next frontier:** S4 E06–E10 full official publisher descriptions into a *separate* five-card HELD tranche from this pinned packet; independent source identity review and actual complete audiovisual source custody are still needed before any Work/coverage admission.
