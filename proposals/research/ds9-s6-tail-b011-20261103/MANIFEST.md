# DS9 B011 — held Season 6 publisher cards, E16–E25 except E20

**Role:** DS9 source-relative title/slot worker. **Accepted base at final selection:** `main@96fbfe270d249e6c3ba04e3aa49b40ed7b508caf`, freshly rechecked and rebased after accepted B010/#348 integration on 2026-11-03 UTC. **Status:** unaccepted research proposal; no Source↔Work binding, primary audiovisual or script reading, synopsis approval, global reconciliation, edition determination, media custody, or coverage admission.

## Actual source observation

The visible [Paramount+ *Star Trek: Deep Space Nine* Season 6 guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/6/) was opened and its current titles, displayed `S6 E#` slots and adjacent description-block presence read for the 2026-11-03 UTC recheck. The records preserve **nine** distinct current guide cards in the E16–E25 range, **deliberately omitting E20** because the accepted B006 publisher-card recheck already recorded *His Way* at S6E20 against the separate Wikidata seed row `lead:0068`. We do **not** infer an accepted global identity between the seed and publisher directory IDs.

| Unadmitted publisher directory row | Visible Paramount+ guide card |
| --- | --- |
| `publisher:s6:ds9:015` | S6E16 — *Change Of Heart* |
| `publisher:s6:ds9:016` | S6E17 — *Wrongs Darker Than Death Or Night* |
| `publisher:s6:ds9:017` | S6E18 — *Inquisition* |
| `publisher:s6:ds9:018` | S6E19 — *In The Pale Moonlight* |
| `publisher:s6:ds9:019` | **S6E20 — *His Way*: OMITTED, previously source-rechecked in accepted B006** |
| `publisher:s6:ds9:020` | S6E21 — *The Reckoning* |
| `publisher:s6:ds9:021` | S6E22 — *Valiant* |
| `publisher:s6:ds9:022` | S6E23 — *Profit And Lace* |
| `publisher:s6:ds9:023` | S6E24 — *Time's Orphan* |
| `publisher:s6:ds9:024` | S6E25 — *The Sound of Her Voice* |

The prior B006 observation source `proposals/research/ds9-publisher-guide-tail-b006-20261103/observations.json` has SHA-256 `12bacfb550e3b52ce8e14c591bcc7e258f59e1544bf28fa010ce249f60c96a08`; its accepted Season 6 source-card slots are S6E5 and S6E20. The accepted B010/#348 observations `proposals/research/ds9-s6-middle-b010-20261103/observations.json` have SHA-256 `98701739ef225d6b36d2c17ecc057dd1a94b8987e1c58f277bde5851a543d1d5`, containing source-local E6–E15 IDs `publisher:s6:ds9:005`–`014`; the B011 validator rejects any reused IDs. The historical publisher S6 discovery CSV SHA-256 is `328e2df32a5492249a756a23a22eb641d135877cfca930ffc444b005c04b9ef8` and accepted `DISCOVERY_ONLY` directory SHA-256 is `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`. These hashes pin **already accepted repository inputs only**, not the freshly rendered publisher HTML, which was **not captured or hashed** (`current_raw_html_sha256:null`).

During initial selection, prior Season 6 E6–E15 publisher recheck **Draft PR #348** was still open. Before publication it was merged into accepted `main@96fbfe2` and this B011 was rebased, retested, and pinned to its accepted source-only record. Earlier Season 7 B008 and B009/#344 rechecks are also separate; the corrected #344 is **accepted main**, not a pending draft. Open #290 covers E5/E20 discovery seeds, which remain outside B011. The guide and historical discovery CSV are from the **same Paramount corporate source family**, never two independent corroborating witnesses.

Each source row has exactly one visible guide card/slot, but this is **not proof** that a universal physical episode, alternate cut, historical broadcast or streaming runtime has a unique match. This tranche does not infer additional multipart installments or collapse presentations into a global Work registry. Although short publisher descriptions were visible, the batch stores **no description text, original synopsis paraphrase, transcript passage, artwork, audio or video**. All synopsis flags are `HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE`.

> **Hostile challenge:** The current streaming guide's display ordinal and a historical publisher CSV agree because they share a publisher lineage. The recheck improves the source-relative record, but cannot alone authenticate an actual episode cut, govern a Source↔Work match, or establish independent corroboration.

> **Hostile challenge:** E20 must not re-enter the candidate batch through an unqualified title match or re-numbering of list indexes. Nine observations across a ten-slot interval are the correct intended count. Treating ten guide slots as ten new verified Works would inflate research completion.

## Validation and next source frontier

`validate.py` pins accepted input hashes including merged B010 and exact direct-source title/slot/locator pairs; enforces nine disjoint records, explicit prior E20 exclusion, closed schemas, same-family provenance, no raw body capture, no source/Work/coverage promotion, and a strict duplicate-key JSON parser. Regression tests challenge forgery of accepted SHA, source independent-family claims, metadata, Work IDs, E20 inclusion, episode viewing and coverage, and four duplicate-key attacks in both standard and optimized Python.

```bash
python3 proposals/research/ds9-s6-tail-b011-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_ds9_s6_b011.py'
python3 tools/validate.py
```

**Next DS9 source-local card:** S6E26 *Tears Of The Prophets* remains outside this bounded tranche. More importantly, full-source/episode scene research remains blocked until authenticated rights-authorized AV/script source custody and a governed Source↔Work mapping satisfy the Director's research gate. No coverage ledger was changed here.
