# Enterprise S2 E06–E10 — complete publisher-guide description pass (HELD)

**Evidence class:** Paramount+ first-party episode-guide HTML description, not watched audiovisual, script CLOSE_READ, canonical Work, or accepted Explorer Briefing.

## Source custody and actual reading

- Full first-party source: https://www.paramountplus.com/shows/enterprise/episodes/2/
- HTTP 200; date header `Wed, 04 Nov 2026 22:56:26 GMT`; observation `2026-11-04T22:56:26.093633+00:00`.
- Entire response **312,754 bytes**, raw SHA-256 `321513d93517b9ea1e50b9ad339352da7dbc38a7564ec1806b4fc4cdc0badc26`.
- All **26** publisher cards traversed again; every normalized title, ordinal, route, date, line, description length and description SHA-256 exactly matched the predecessor E01–E05 receipt, whose original full raw response SHA-256 was `860df3bd8d3c3e91727ab71c712cd60718da0bddf63fcd5bd5914b83358d9cdd`. Dynamic outer HTML bytes differed. This is **one publisher provenance family observed twice**, not two independent witnesses.
- This tranche actually read **five** full publisher description paragraphs, E06–E10, **842 source characters** total, and produced five original short paraphrases. The other 21 cards' descriptions are structurally fingerprinted; not newly read for synopsis.
- Description source text and raw HTML remain transient and uncommitted. `source_probe.py` imports the first-five exact S2 parser rather than manufacturing an alternate card model.

| Source-local episode | Official guide title | HTML anchor / description line | Description SHA-256 |
| --- | --- | ---: | --- |
| E06 | Marauders | 1622 / 1640 | `68b4109b374fde6c194d56b5f735113eb262d13e24ead999cfe1e30132aec648` |
| E07 | The Seventh | 1650 / 1668 | `82b7e0de2e74e260739a0f7be35756c015c0d415938557a2b6af2d03c461422e` |
| E08 | The Communicator | 1678 / 1696 | `3ee8adb601775a30ee8992264c247ec06e2c17133c4fbc3017d7aa05076f122c` |
| E09 | Singularity | 1706 / 1724 | `2e7ffc2fcfa631897fadd944ba1e6c90ed54370606f512d3fd8b1cccef3cf378` |
| E10 | Vanishing Point | 1734 / 1752 | `c96a2ede0435119fc325677be0299ccfab345c9cdfc8f0825055f1c924fca703` |

## Source-relative claims, not objective episode truth

- E07: T'Pol encounters difficult memories. The official guide describes her experience; this does **not** establish her recollection's content as independently true.
- E08: Reed and Archer are suspected of espionage by local inhabitants. The accusation is evidence of suspicion, **not proof that they actually spied**.
- E10: Hoshi begins questioning her own identity following transporter use. Her question is **not proof of replacement, death, continuity failure, or any global metaphysical identity claim**.
- E01–E05 source-local **publisher datetime inversions** E01/E02 and E04/E05 remain reproduced from the predecessor, unresolved. Guide ordinal and publisher timestamp must not be silently conflated with an accepted broadcast chronology.

All five new records use `SOURCE → local publisher card → evidence → PUBLISHER_DESCRIBES assertion`; canonical Work IDs remain null. Their brief original paraphrases are in `records.json`. Companion `validate.py` reruns the exact predecessor validator and checks both source receipts, source-relative IDs, narrative attribution and protected-effect boundaries. `test_validate.py` attacks these assumptions.

## Honest batch boundary

**10 of 26** first-party publisher-guide description proposals now HELD across two nonoverlapping local batches. The **remaining 16** publisher descriptions have not yet received a source-relative synopsis pass. Neither ten nor twenty-six represents admitted Works, episodes watched, transcript close reads, or a public database coverage increment.

No full copyrighted publisher description or HTML, video, audio, script, captions, art, or streaming material committed. No Source/Work binding, global reconciliation, public Explorer effect, push, merge, or deployment.

**Next exact frontier:** S2 E11–E15 complete first-party publisher-description pass with a fresh full source receipt and nonoverlap tests. The larger audiovisual CLOSE_READ frontier remains separate and requires actual primary episode access.
