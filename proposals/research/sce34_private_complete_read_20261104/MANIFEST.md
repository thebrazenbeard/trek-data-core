# HELD private source reading — *Collective Hindsight Book 2*, S.C.E. #34

2026-11-04 | **HELD proposal, not accepted corpus ingestion.** No ebook text, cover pixels, extraction folders or absolute owner paths committed.

## Primary source actually read

- I opened the existing user-controlled `Star_Trek_OPF_Converted.zip` on the authorized Lappy using read-only Python `zipfile`, without extracting it to disk. The ZIP is 95,673,655 bytes, SHA-256 `0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f`.
- I read the **complete narrative of all seven chapters**, from `CollectiveHindsightBook2.html#ch_1` through the end of `#ch_7`, stopping at the narrative `END` marker. Following author biography and advertisement for S.C.E. #35 *The Demon Book 1* were recognized as backmatter, not included in the Work. Raw converted HTML is 115,388 bytes, SHA-256 `fcc08e791e209bd2c90d36fea30f1820137ca753b1f3a1ff9eb0ea82683ed3bd`.
- The separate owner OPF is 4,222 bytes, SHA-256 `ca025b2d11a8982524e89a97e1e454340ae639c1b6a38f4f1eebbb09b07e2706`; table of contents member 1,401 bytes, SHA-256 `63739a129851c7d736d4c09c2f1d1efca917b517fe9bf8bc8c11fd8f537d21fa`. The OPF spine cites one narrative HTML item and its chapter tour correctly lists seven anchors.
- The owner conversion manifest (115,409 bytes, SHA-256 `7b83b960729b3a51f2d2e026a543860f30dbd4183e7958c52a068935a9a65782`) reports source `.lit`, success, DRM label 1, exit 0 and twelve output files. The original `ST ebooks.zip` archive (SHA-256 `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`) independently contains the exact matching-name `.lit` member, 236,948 bytes, SHA-256 `d86f0743b2582b5ba4227c349504b0843b0b3a1af70835c335e2ea3fc174c956`. The conversion process was **not independently reproduced**, and conversion metadata is not purchase/licensing proof.
- The user-controlled converted ebook includes a proprietary work; original lawful acquisition, licensed public ingestion, edition-authenticity and redistribution authority are **not independently authenticated**. No copyrighted narrative text is exported.

## Publisher metadata and edition falsifiers

- The [official Simon & Schuster listing](https://www.simonandschuster.com/books/Star-Trek-Collective-Hindsight-Book-2/Aaron-Rosenberg/Star-Trek-Starfleet-Corps-of-Engineers/9780743480840) identifies Aaron Rosenberg, S.C.E. #34, Pocket Books/Star Trek, 17 November 2003, 79 ebook-listed pages and ISBN13 `9780743480840`.
- Historical owner OPF inventory record `opf-local:0045` (`observations.json` SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`) says `isbn_checksum_valid=[]`. Direct source OPF read found the decorated literal `ISBN 0-7434-8084-8`, which converts by checksum to publisher ISBN13 `9780743480840`. The inventory parser omission remains an unresolved metadata discrepancy; it does **not** prove exact publisher-edition manifestation or licensing.
- Book One S.C.E. #33 and Book Two S.C.E. #34 remain **separate owner source-local Work candidates and separately scoped local entities**. Same titles/characters, two publisher listings and sequential numbering motivate a candidate relation, not an accepted global `SAME_AS`, shared Source, or cross-Work reconciliation.

## Source-relative chapter fingerprints

All offsets are zero-based raw HTML member bytes, end exclusive. They are not printed page/line numbers. The seventh ends *before* the separate `END` marker at byte `113016` and backmatter.

| Chapter | Relative byte span | Raw slice SHA-256 | Original source-grounded summary |
| --- | --- | --- | --- |
| `#ch_1` | `[6413,17685)` | `c000e263fa41bea8a439d69794e81960787de2a1932f8165e697334e958f5df4` | Gomez and Tev separately reexamine the previously encountered vessel and challenge each other's observational assumptions. |
| `#ch_2` | `[17685,36826)` | `3855bbaf7c9fd0b9cf1cf429e16fa5061cc33d471b5d483a10a8dd1e9c18a63c` | Androssi retrieval mission begins; Soloman reconsiders his lost pair while the team models an earlier supernova speed boost. |
| `#ch_3` | `[36826,57912)` | `6af0b83d7b316e9115e8bc194860459092b58c675e91846982477b0be26031db` | Hull absorption and a hidden automatic return program emerge from engineering analysis, with past deactivated safeguards explaining renewed danger. |
| `#ch_4` | `[57912,69108)` | `1098e026c07bbdc05ba20d330842935c2c5b2cf7330571247ef438d6886f3452` | The Androssi vessel separates into three modules; the crew proposes entering a sun inside the larger alien craft. |
| `#ch_5` | `[69108,80802)` | `4a2a6136168fc95f8492e53ce0e621b25c2c1831d4d7c11bc86a0e7f52e75fb6` | An improvised tractor-assisted asteroid pivot changes course before the da Vinci shelters inside the cargo hold. |
| `#ch_6` | `[80802,103622)` | `61ee3a3663e501bbd5a4ac1a0d385f6dde273b4fdb3845dedf5f494eca129b74` | The team survives a solar dive and uses the alien engine to destroy the remaining Androssi guard before leaving the star. |
| `#ch_7` | `[103622,113016)` | `c5eac07db5931ac85b4715dfff831cbc43664d20a89d580c2ef05959bcbf6014` | The ship's drive/computer pathways are disabled; its **hull survival remains unknown**, and the surviving crew reassesses past grief and shared competence. |

## Evidence discipline and protected effects

- `records.json` contains one held local Source, one local Work candidate, eight local-only entity occurrences, ten source-relative observations and five proposed assertions. The first officer's opening report is an **in-story reconstruction**, not externally corroborated history. Supernova path is a **crew model**; automatic-return instructions are **Soloman's report of code**; the Androssi sensor's failure to detect the hidden ship is a **sensor limit**, not proof it was destroyed.
- The closing scene expressly says it is unknown whether the hull remains intact inside Cardienne's star. Disabling the ship and judging it no longer threatening does **not** establish hull destruction. Do not write `DESTROYED`, `SAME_AS` or `CLOSE_READ` to accepted ledgers.
- `validate.py` freezes source/provenance/publisher identity and all analyzed record semantics with a canonical digest; tests attack altered bytes, chapter count/end boundary, mistaken ISBN promotion, private rights, inference class, bogus destruction and cross-Work promotion.
- `verify_owner_archive.py` can **optionally** rehash private ZIP plus OPF/TOC/HTML and seven slices on an authorized host without emitting novel prose or writing extracted files:

  `python -m proposals.research.sce34_private_complete_read_20261104.verify_owner_archive --archive <owner-local-zip>`

  The factual source fingerprint probes in this manifest were performed through direct in-memory Lappy commands; this packaged CLI was tested locally with synthetic invalid files, **not claimed as run verbatim on Lappy**.
- **Effects: zero** accepted Source/Work/Evidence/Close Read/coverage/cross-Work identity, zero public Explorer/projected Work changes, zero remote push/merge/deploy, zero copyrighted book/cover text or pixels. This is a HELD proposal for independent audit and rights review.

Next: independent hostile semantic review of this packet, rights/edition-custody gate, and any authorized source-relative ledger admission; otherwise continue a separate 1–3-work bounded privately accessible literary batch. No silent conversion from HELD to accepted coverage.
