# Voyager S1 — first five English-US Paramount+ publisher-guide cards (HELD)

Role: **VOY series worker**. Baseline accepted `main`: `3028765359001b90bc3e6b5c1835ee283b326e91`. This is one bounded source-relative analysis proposal, **not** five completed episode close-reads or five accepted Work identities.

## Primary-source retrieval

- Publisher: Paramount+, one `publisher:paramountplus.com` lineage.
- Exact source: `https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/`, observed English-US HTTP 200 on 2026-11-05 UTC.
- Full HTML retrieved and parsed in memory by `source_probe.py`; `292,338` bytes, retrieval SHA-256 `d13c1985dc71d8ea560378bac946d4fa07cce2c2929556a4ddf8a0dbbc37be69` (mutable response, not archived source custody).
- Normalized 15-card source fingerprint SHA-256 `7bef657a899ca288a86e7f5dc6e310784b33ffbc46e04b78d2fa412a7f0e2f80`.
- Exactly **15 displayed US publisher-guide cards**, numbered by analytics order `1..15` and episode badges `1,3..16`. The first *Caretaker* guide card combines two named pilot parts; it is **one card, not one resolved canonical episode Work**. Another first-party German-locale guide displays two separate pilot cards; that distinct locale observation was inspected but has **not** been reconciled or independently source-hashed into this packet.
- First five US publisher descriptions (guide ordinals `1..5`, badges `1,3,4,5,6`, total `926` publisher text characters) read in full. First card's publisher synopsis ends abruptly after “newly launched U.S.S.”; nothing beyond that fragment was inferred.
- Full publisher text, HTML, screenshots, audio and video are **not** committed. Exact source-relative routes, HTML line locators, title/date/paragraph length/digests, original paraphrases and guarded assertions are in `records.json`.

## Output and evidence discipline

Exactly five local card entities, five source-relative publisher-description evidence records, and five typed assertions. Each description was paraphrased in original language; events and character choices are attributed to publisher synopsis, not independently verified fictional world-state or actual audiovisual viewing. The Time And Again synopsis explicitly leaves competing causal explanations unresolved.

Coverage ladder remains separate: observed 15 publisher cards; first five descriptions analyzed; remaining ten not yet coded; **zero** audiovisual CLOSE_READ and **zero** accepted coverage/admissions. No global card/work reconciliation, no third-party image rights, no public Explorer publication effect.

## Reproduction and validation

1. `python proposals/research/voy/voy-s1-firstfive-official-guide-20261105/source_probe.py` retrieves a current US publisher snapshot and fails closed if the 15-card / composite-pilot structure changes. The live site intermittently returns HTTP 503 to Python's direct request; a verified alternative is `curl -sS -L --retry 2 --max-time 25 https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/ | python proposals/research/voy/voy-s1-firstfive-official-guide-20261105/source_probe.py --stdin`. Compare normalized card fingerprint and first-five description hashes to the frozen packet. `--internal-prose` temporarily prints private source text for a human researcher; never commit that output.
2. `python proposals/research/voy/voy-s1-firstfive-official-guide-20261105/validate.py` checks exact reviewed packet bytes, schema, publisher lineage, source identifiers, evidence, source-description hashes, neutral paraphrases and no protected effects.
3. `python proposals/research/voy/voy-s1-firstfive-official-guide-20261105/test_validate.py` executes negative mutation tests for source/episode identity, truncated plot, canonical causal overclaim, copyright/license spoof and release effects.
4. `python -m unittest discover -s tests -q` and `python tools/validate.py` must pass before independent AUDITOR review.

Status: **HELD LOCAL PROPOSAL**. No merge, force-push, deployment, credential change, global Work mapping, media release or coverage promotion authorized.
