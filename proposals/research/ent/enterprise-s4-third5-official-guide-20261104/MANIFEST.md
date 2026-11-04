# Enterprise Season 4 E11–E15 — third HELD Paramount+ guide-description batch

**Batch:** `ENT.PPLUS.S4.THIRD5.GUIDE.20261104`

**Role:** ENT research, strictly source-relative first-party episode-guide descriptions. No video/audio/transcript CLOSE_READ.

**Dependency:** isolated branch `research/ent-s4-e11-e15-20261104` based on exact local S4 second-five commit `1bd2d94506815a2039d95a5dbabc932ef6a35cfd` and first-five ancestor `9da214b3231870c3879f9f645e9bf9e9ab6f7c53`. Accepted GitHub `main` ancestor `3028765359001b90bc3e6b5c1835ee283b326e91` is not changed. The two predecessor record file SHA-256 digests, source response hashes, and local commits are pinned in `records.json`, not treated as accepted state.

## Fresh full publisher-guide source receipt

At `2026-11-04T22:21:44.382069+00:00`, read the entire first-party [Paramount+ *Enterprise* Season 4 guide](https://www.paramountplus.com/shows/enterprise/episodes/4/) in memory, HTTP 200, response Date `Wed, 04 Nov 2026 22:21:44 GMT`, **301,606** response bytes, raw SHA-256 `07d67fdee1a556a92367d9e22913d8bc8bf26806c5d753a1113b189e4f85fde3`.

All **22** publisher guide cards and descriptions were structurally parsed. Their normalized title, episode label, analytics ordinal, video-route metadata, publisher date string and description hashes matched both previously held complete-page observations. Their raw HTML SHA-256 values differ across the three snapshots because the delivered publisher HTML is dynamic; these are **not three independent source witnesses**.

Only the five E11–E15 original publisher description strings (**721 publisher-text characters**) were read to create new concise original paraphrases. These source-attributed paraphrases are in `records.json` beside source-local entity, evidence and `PUBLISHER_DESCRIBES` assertion records. No raw HTML, complete copyrighted publisher blurb, linked media, image, caption, audio, script or transcript content was committed.

| Guide-local card | Display title | HTML anchor / description line | Exact description SHA-256 |
|---|---|---|---|
| E11 | Observer Effect | 1762 / 1780 | `ff0443f6a0295ec0c093fbeddf7f1168e7a58fec70c2dc736a21c7a484875e9f` |
| E12 | Babel One | 1790 / 1808 | `8a915effba1911f81f3ee231295a2be84f73923bfbd67ef9c8476ea4a607d969` |
| E13 | United | 1818 / 1836 | `fea2b749aad42b88e778b6296567984d42ccea27d1f82cd3747f860084fc3af2` |
| E14 | The Aenar | 1846 / 1864 | `74e5a90e9973c1fa055397fb9cfdd686223564ba3bb725e368cfe92261fe869e` |
| E15 | Affliction | 1874 / 1892 | `2dc78705299e93d73b33c25a4bb2a0f5b0be243876babd1602e18d45194ac7df` |

Line numbers are locators for the exact dynamic HTML response identified by this digest; a fresh page may rearrange lines. The publisher date strings are preserved literally and are not automatically original broadcast dates. Linked video URL paths are metadata locators only, never watched episodes.

## Lineage and explicit holds

| Separate held batch | Guide-description analyses | Local commit | Records SHA-256 |
|---|---|---|---|
| first5 | E01–E05 | `9da214b3231870c3879f9f645e9bf9e9ab6f7c53` | `f8e65b062b7b53929341d6dbca31dd20f29bf09f995b9a5daf628dc12b6e4f10` |
| second5 | E06–E10 | `1bd2d94506815a2039d95a5dbabc932ef6a35cfd` | `a21928c263501e34be287ffd2c8524267ab30fa50e19dca1262ae8c0b9e49b05` |
| third5 | E11–E15 | this local proposal | see `records.json` SHA-256 at handoff |

The current full guide still carries a real **E22 capitalization variant**: display/analytics leaf title `These Are the Voyages`, analytics series-title `These Are The Voyages`. This packet preserves both strings with `CAPITALIZATION_VARIANT_UNRESOLVED` and no global identity join.

**Result: 15/22 source-local publisher-guide description analyses held across three disjoint batches, seven not yet analyzed.** These counts are not accepted canonical Works, audiovisual close reads, governed coverage, or independently corroborated source claims. No Source/Work admission, reconciliation, public Explorer publication, permission changes, merge, deployment, or external effects occurred.

> **Hostile finding:** Publisher editorial descriptions are evidence of publisher wording; they do not independently establish what actually occurs in the show. Complete metadata-page parsing is neither audiovisual CLOSE_READ nor a basis for coverage inflation. E22's source-internal capitalization difference is not resolved by repeated appearances on the same publisher page.

## Validation and frontier

```bash
python3 proposals/research/ent/enterprise-s4-third5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s4-third5-official-guide-20261104 -p test_validate.py -q
python3 proposals/research/ent/enterprise-s4-second5-official-guide-20261104/validate.py
python3 proposals/research/ent/enterprise-s4-first5-official-guide-20261104/validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests -q
git diff --check
```

Validator re-runs first and second predecessor deterministic checks against exact file and discovery digests; enforces two prior metadata snapshots, current full-guide snapshot, 15 nonoverlapping local IDs, exact five new evidence hashes/locators, E22 title conflict, and zero protected effects. Hostile tests attack count inflation, false independent corroboration, made-up source lines, shifted ordinals, bad local joins, forged precursor commits, and unearned Work/coverage/CLOSE_READ promotions.

**Next frontier:** E16–E20 in a new held packet based on this exact local branch, then the real final two E21–E22 (do not invent E23), all strictly publisher-guide source-relative. Complete actual-episode analysis remains a separate source-access and custody task.
