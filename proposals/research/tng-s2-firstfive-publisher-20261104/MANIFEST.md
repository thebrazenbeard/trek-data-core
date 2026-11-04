# TNG Season 2 B013 — first five publisher episode-card observations (HELD)

**Role:** TNG. **Accepted baseline:** `main@3028765359001b90bc3e6b5c1835ee283b326e91`.
**Observation date:** 2026-11-04 UTC. **Batch state:** `HELD_SOURCE_LOCAL_PUBLISHER_METADATA`.
**Source:** [Paramount+ TNG Season 2 complete guide](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/2/).

## Actual read and scope

The full accessible publisher guide was retrieved in the web reader, and its **22** Season 2 headings, displayed episode ordinals and short descriptions were read as a complete season-guide surface. This bounded batch records original paraphrases and source-relative mentions for the first five visible cards, **S2E1–E5**. It rechecks five already-existing publisher source-local discovery IDs; it does not discover five new global Works. The accepted CSV, bundle and 1,214-row directory are byte-pinned by the validator.

| Source-local ID | Displayed publisher card | Original analysis scope |
| --- | --- | --- |
| `legacy:s2:tng:000` | *The Child*, S2E1 | Publisher's transport/pregnancy premise only |
| `legacy:s2:tng:001` | *Where Silence Has Lease*, S2E2 | Publisher's unknown-void/captivity premise only |
| `legacy:s2:tng:002` | *Elementary, Dear Data*, S2E3 | Publisher's Holmes/Pulaski danger premise only |
| `legacy:s2:tng:003` | *The Outrageous Okona*, S2E4 | Publisher's visitor/Data-humor premise only |
| `legacy:s2:tng:004` | *Loud as a Whisper*, S2E5 | Publisher's mediator/communication premise only |

The five publisher-description fingerprints are SHA-256 of the **web-reader-rendered, trimmed UTF-8/NFC descriptive strings**, not the publisher's raw HTML bytes or a source-edition hash. On Lappy, a separate unauthenticated `HttpClient` attempt returned HTTP 406; therefore the raw response was **not** archived, and no raw HTTP content digest is claimed. The browser-accessible rendered guide was read, but this is not a replayable primary-byte custody receipt. Individual card location is the guide URL plus exact heading and displayed S2E ordinal. No verbatim source descriptions, images or transcript passages are committed.

## Boundaries and counterclaims

- All five records remain source-relative observations of **Paramount's description**. They do not establish depicted episode events, actual dialogue, characterization, a specific broadcast edit, or full video/script access.
- This batch and the older legacy S2 directory derive from the same Paramount corporate source family. Agreement is not independent corroboration and does not increase the universe denominator.
- A named person or institution is recorded only when the guide text itself names it. For example, the unnamed visitor in E4 and the unnamed mediator in E5 are not silently identified from episode-title lore.
- No new canonical Source↔Work binding, Work identity, public synopsis/image permission, or coverage event is proposed. Issue #23's close-reading and admission hold remains in force.
- Patrick's personal preferences did not influence the first-five contiguous selection, source choice, or evidence weighting.

> **Hostile limitation:** A complete *episode-guide webpage* is still only promotional metadata. A current streaming-page ordinal may differ from production, syndication, or cut order, and the fingerprints do not reproduce the underlying response bytes. An approved audiovisual close read requires a different source custody and review path.

## Deterministic replay and next frontier

```bash
python3 proposals/research/tng-s2-firstfive-publisher-20261104/validate.py --check
python3 -m unittest discover -s proposals/research/tng-s2-firstfive-publisher-20261104 -p 'test_*.py'
python3 tools/validate.py
```

The validator pins the baseline discovery catalog, S2 CSV and S2 publisher bundle by SHA-256, rejects title/ordinal/description/mention drift, promotion claims, ambiguous local IDs and altered held paraphrases, and emits `records.json` deterministically. The next TNG source-local tranche is S2E6–E10 after reviewing overlap and edition status. The next **governed** stage remains blocked pending independent source custody, accepted Work/Source bindings and approved primary content access.
