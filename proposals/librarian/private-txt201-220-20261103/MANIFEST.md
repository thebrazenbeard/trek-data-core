# Private original Trek TXT source-member fingerprint inventory: FINAL 201–220

**LIBRARIAN metadata-only proposal**, observed 2026-11-03. The exact accepted baseline for this final packet is `main@e4348bdf4287d82c2bb6e88db39209f1db5688af`, containing the four separately accepted first-200 original-TXT source-member packets. This is **completion of the 220-file byte-fingerprint census only**; it does **not** mean the library's unique literary Works, editions or content have been researched, read or fully ingested.

## Actual source-byte observation

- Used Lappy's read-only ZIP API against the owner-held original ebook container, opaque `OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B`. Previously independently verified whole-ZIP SHA-256 `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`, 126,481,241 bytes, 573 members: 347 LIT, 220 TXT, six directories.
- Sorted all 220 `.txt` members lexically by ZIP member name. Exact **last 20** TXT member payloads in sorted positions **201–220**, filename-derived Voyager (VOY) sequences **011–030**, were opened as streams solely to compute their individual SHA256 fingerprints. Total 20 member uncompressed bytes: **8,602,096**.
- All 20 final hashes are distinct within the batch, and none duplicate a fingerprint in the four earlier **accepted** 50-record packets. The entire original 220-member TXT file set has **220 distinct exact-byte hashes**, covering **96,968,694 uncompressed member bytes**. This is not a literary Work count, duplicate-content/text-similarity audit, licensed edition validation or canonical Source→Work admission.
- Titles such as *Dark Matter* multi-part, *Spirit Walk* and *String Theory* appear as **filename-derived hints**, not identity, chronology, collection or edition conclusions. Multiple byte-distinct files can be different transcriptions or parts of one Work; a collection may encompass multiple Works.

## Boundaries deliberately retained

Public `observations.json` includes only opaque source-local IDs `txt-local:0201`–`txt-local:0220`, TXT ordinal, filename-derived series/title hints, member size and original member SHA256. It exposes **no private raw ZIP member path, owner account, actual book prose, images, screenshots, dialogue, passage or excerpt**.

Its explicit statuses remain:

| Dimension | State |
| --- | --- |
| Private member bytes | `HASHED_WITHOUT_SEMANTIC_READ` |
| Literary work coverage | `DISCOVERED` (filename/member discovery only) |
| Source→Work binding | `UNRESOLVED` |
| Edition binding | `UNRESOLVED` |
| Publication/reuse rights | `UNKNOWN` |
| Full-text/chapter semantic reads admitted | **0** |
| Copyrighted prose/cover images published | **0** |

> **Hostile challenge:** Each byte digest authenticates a **file byte observation only**, not an officially published licensed text, a complete story or copyright permissions. The separate 347 LIT files and 347 converted OPF package metadata observations belong to potentially overlapping lineages. Summing 220 + 347 + 347 and calling that number of books would be unjustified. No global Work, edition, character or narrative assertion can be compiled from these filename-derived file receipts.

## Validation and provenance

The current 20-record canonical JSON SHA-256 and all four accepted 50-record rowset digests are pinned. The fail-closed validator cross-checks **all 220** opaque IDs, ordinals and individual member fingerprints for uniqueness, ordered series hints, intact predecessor packets, no exposed private paths and no inflated rights/coverage/edition claims:

```sh
python3 proposals/librarian/private-txt201-220-20261103/validate.py
python3 -O proposals/librarian/private-txt201-220-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_private_txt_201_220.py' -v
```

These checks validate only the committed metadata derivative; independent auditor reproduction against the private original source ZIP is a separate host-only evidentiary check.

**Next actual literature frontier** is not more file-name enumeration: establish source-rights custody and external publisher edition matches, handle collections versus constituent Works, inspect 347 LIT↔347 OPF conversion lineage and its known XML/URI anomalies, then perform bounded source-grounded literary close-reads under LIT worker authority. No deletion, merge, deployment or public copyrighted publication by this proposal.
