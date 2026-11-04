# Enterprise Season 4 E16–E20 — fourth HELD publisher-description batch

**Batch:** `ENT.PPLUS.S4.FOURTH5.GUIDE.20261104`

**Role:** ENT worker, source-relative first-party publisher guide descriptions only.

**Dependency:** a separate isolated worktree/branch `research/ent-s4-e16-e20-20261104` from exact local previous commit `1dcd8662c2e7f0fdd7c9fd60fce789a28f2e841c`. This stacked local research proposal includes held first-five commit `9da214b3231870c3879f9f645e9bf9e9ab6f7c53` and second-five `1bd2d94506815a2039d95a5dbabc932ef6a35cfd`; accepted GitHub `main` ancestor `3028765359001b90bc3e6b5c1835ee283b326e91` remains unchanged. Prior exact record SHA-256 and raw source response digests are pinned in `records.json`.

## Full official source read

At `2026-11-04T22:29:51.676867+00:00`, read the **entire** [Paramount+ *Enterprise* Season 4 episode guide](https://www.paramountplus.com/shows/enterprise/episodes/4/) read-only: HTTP 200, response Date `Wed, 04 Nov 2026 22:29:51 GMT`, **301,606** HTML bytes, raw SHA-256 `aa3731ca64e8022d2090cc833f420fb6ab367575d870ea102d9146c60461b04e`.

The complete page's **22** publisher cards and description fingerprints matched all three previous normalized source snapshots, even though all four raw HTML digests differ. These repeated reads are one `publisher:paramountplus.com` source lineage, **not four independent corroborations**. The five actual E16–E20 publisher blurbs (**681 source-text characters**) were inspected and rewritten as five original concise paraphrases, each associated with a source-local entity, evidence locator and typed `PUBLISHER_DESCRIBES` assertion. Neither full copyrighted publisher paragraphs nor raw HTML or any linked media was committed.

| Guide-local card | Display title | HTML anchor / description line | Exact description SHA-256 |
|---|---|---|---|
| E16 | Divergence | 1902 / 1920 | `f167b224da7cbd93f181dac161fc8886d69ba0decd3cc45a8ec606972824bfcf` |
| E17 | Bound | 1930 / 1948 | `1690a6918b7a68894bae542dad95b8ec2e5ae2b31ddd7775e8a17c9f58fcdb92` |
| E18 | In a Mirror, Darkly, Pt. 1 | 1958 / 1976 | `56afde4fd595b85776d0527011bf3c9adbf33db03bd56ee3ab612baaeba6cd31` |
| E19 | In A Mirror, Darkly, Pt 2 | 1986 / 2004 | `701428343bc7690929b7bcf2ac5f53e82579d5bed64aa7a99e52b56abbfd840c` |
| E20 | Demons | 2014 / 2032 | `0c0195adbe71a85a6228aee12aae873031cfdbe33d6168dfd49abaffb0211cd4` |

The HTML line numbers refer only to the precise mutable publisher response identified by hash. Source-local `/shows/video/.../` URLs were recorded as metadata routes only; no video/audio/caption, scripts, transcripts, stills, or cover art were retrieved. Publisher date strings remain literal display metadata and do not automatically establish original-airdate facts.

## Source-relative alternate-frame and identity holds

The official descriptions of E18 and E19 explicitly use the **mirror universe** frame. The two typed assertions preserve `claimed_narrative_frame=MIRROR_UNIVERSE`, `frame_claim_status=PUBLISHER_DESCRIPTION_ONLY`; no prime-universe identity, timeline or event assertions are inferred. E17's publisher description uses an exploitative historical/fictional framing of enslaved Orion women; the new concise paraphrase preserves the source-stated status without repeating the publisher's full passage.

The complete guide still shows the same E22 source-internal capitalization mismatch: display/leaf analytics `These Are the Voyages` versus analytics series title `These Are The Voyages`. The conflicting strings and `CAPITALIZATION_VARIANT_UNRESOLVED` status persist; no canonical Work reconciliation occurred.

> **Hostile review:** A publisher blurb is evidence of publisher wording, not a witnessed audiovisual event. A mirror-universe plot description cannot simply be flattened into prime continuity. Four retrievals of the same source do not provide four independent validations. Source metadata, exact title strings, and local episode ordinals are not sufficient to admit canonical Works.

**Current HELD source-relative description proposal count: 20/22** across four separate batches. The final two publisher descriptions (E21–E22) are **not yet processed**; there is no E23 source card and no right to invent one. No accepted Source or Work, governed coverage/denominator, audiovisual `CLOSE_READ`, reconciliation, Explorer/public publication, merge, deployment, or credential/permission change occurred.

## Deterministic validation

```bash
python3 proposals/research/ent/enterprise-s4-fourth5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s4-fourth5-official-guide-20261104 -p test_validate.py -q
python3 proposals/research/ent/enterprise-s4-third5-official-guide-20261104/validate.py
python3 proposals/research/ent/enterprise-s4-second5-official-guide-20261104/validate.py
python3 proposals/research/ent/enterprise-s4-first5-official-guide-20261104/validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests -q
git diff --check
```

The validator pins three predecessor file and original full-source hashes/commits, reruns all three predecessor and upstream source-candidate checks, matches all 22 normalized publisher cards, and checks five independent new local ID/evidence/assertion chains with exact source-description hashes and lines, narrative-frame attribution, non-overlap, and zero protected effects. Hostile tests falsify title/lineage/source changes, duplicate identities, fake episode count/coverage, and any prime-universe assertion promotion.

**Exact next frontier:** S4 E21–E22 final two *publisher-description* paraphrases in a new held packet from this exact branch, not an episode video close read. Any actual audiovisual source inspection/Work binding/coverage is a separately governed step.
