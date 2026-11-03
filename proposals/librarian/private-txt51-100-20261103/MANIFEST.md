# Private literary TXT source member fingerprints: ordinals 51–100

**LIBRARIAN proposal only.** Baseline accepted `main@69f0a5c46e78b9d034ff168d969374892fc997e0` (which incorporates the independently reviewed first-50 packet). Observation date 2026-11-03.

The owner's original ebook ZIP was opened read-only on Lappy. The ZIP member directory was sorted lexically, all `.txt` member candidates numbered in that order, and exact uncompressed member bytes of positions **51–100** streamed through SHA-256. The stream was not saved, displayed, semantically read, or published. This proposal adds source-file receipt metadata only, without a canonical Source→Work binding.

| Filename-derived family hint | ZIP TXT ordinal range | Member count |
| --- | --- | ---: |
| Deep Space Nine (`DS9`) | 51–52 | 2 |
| New Frontier | 53–69 | 17 |
| Slings and Arrows | 70–75 | 6 |
| Stargazer | 76–81 | 6 |
| Titan | 82–87 | 6 |
| The Next Generation (`TNG`) | 88–100 | 13 |
| **Total** | **51–100** | **50** |

- These 50 member payloads total **20,085,802 uncompressed bytes**.
- There are **50 distinct exact-byte SHA-256 fingerprints** within this tranche, and **zero identical fingerprints or source-local IDs** across the earlier accepted 1–50 packet. Combined, 100 file members have 100 distinct exact byte fingerprints; that is **not** a proof of 100 distinct stories, books, Works, or licensed editions.
- Source container `OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B` is pinned to the previously independently verified SHA-256 `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`, 126,481,241 bytes and 573 ZIP entries (347 LIT, 220 TXT, six directory members). This tranche **did not rehash the outer ZIP**, relying on accepted prior host-only receipt; re-running against that private ZIP can independently validate the 50 hashes.
- Opaque `txt-local:0051` through `txt-local:0100` are private source-member **observations**, not global Work IDs. Public `observations.json` includes only a series/title *filename-derived hint*, original uncompressed byte length and member SHA-256; no private ZIP member path, user identity or account locator.
- `data_rights=UNKNOWN`, `member_byte_access=HASHED_WITHOUT_SEMANTIC_READ`, `work_coverage_stage=DISCOVERED`, `source_work_binding=UNRESOLVED`, `edition_binding=UNRESOLVED`. Neither the 50 file receipts nor the full 100-file cross-packet inventory advances literary CLOSE_READ, FULL_TEXT_AVAILABLE, reconciliation or public edition validation.

> **Hostile challenge:** Filename hints can encode incorrect titles or series numbering, and byte-unique TXT copies can reproduce one Work in multiple encodings, versions or parts. *Excalibur* numbered parts, *Destiny* book numbers, and numbered *Slings and Arrows* entries particularly require a later literature worker's independent work/collection assessment. OPF-derived conversion metadata is not an independent narrative witness. No book, chapter, synopsis, dialogue, ebook cover, screenshot, full text, or extracted copyrighted image is in this PR.

## Validation

`observations.json` locks a deterministic SHA-256 over 50 canonical JSON rows and pins the prior accepted first-50 packet digest `56017619758a9e0294384187ec1c18569b1966729bfaf47fbdc85a8d68438553`. The validator checks source receipt, 51–100 ordinals, expected series and file sequence hints, byte sizes, 50 unique SHA-256 values, no overlap with first 50, title-path exclusions, no false coverage/rights/binding claims and fail-closed behavior even under Python `-O`.

```sh
python3 proposals/librarian/private-txt51-100-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_private_txt_51_100.py' -v
```

These tests validate the Git derivative, not the unavailable-for-public-repo private source bytes. They do not grant publication rights or admit literary analysis. Next frontier: read-only member fingerprint tranche **101–150**, plus independent bibliographic edition and series-container reconciliation under separate authority. No merge/deploy or deletion in this proposal.
