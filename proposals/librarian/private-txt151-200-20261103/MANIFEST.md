# Private ebook TXT source-member SHA receipts: ordinals 151–200

**LIBRARIAN proposal only**, observed 2026-11-03 from accepted `main@4a6ebb1c1ae22f7e4b1221f20c32aa93b322d01c`. The previously accepted original TXT source-file fingerprint packets 1–50, 51–100 and 101–150 are treated as immutable, separately SHA-pinned predecessors.

On the owner's Lappy, the private original Star Trek ebook ZIP was opened read-only, sorted by ZIP TXT member name, and uncompressed byte streams of exact TXT positions **151–200** were each passed through SHA-256. All 50 were thus **actually accessed as bytes for hashing**, but no narrative prose was interpreted, quoted, copied, exported or semantically analyzed. No full text or cover artwork appears in the public Git proposal.

| Filename-derived source family | Original ZIP TXT position | Filenames' series sequence hint | File observations |
| --- | --- | --- | ---: |
| TNG | 151–190 | 064–103 | 40 |
| VOY | 191–200 | 001–010 | 10 |
| **Combined** | **151–200** | — | **50** |

## Measured result

- Current 50 exact-member SHA256 values are all distinct from one another and have **zero exact-byte fingerprint overlap** with the prior accepted 150. The 50 members contain **22,859,698 uncompressed bytes**.
- Combined first four packets therefore bind hashes to **200 byte-distinct TXT *files*** totaling **88,366,598 uncompressed bytes**; **20 of the 220 original TXT entries remain** for this file-level inventory. This is expressly **not** a claim of 200 unique novels, complete literary Works, source-accepted editions or completed close-reads.
- The whole original ZIP's already independently verified SHA256 is `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`, 126,481,241 bytes, with 573 members (347 LIT, 220 TXT, six directory members). This bounded run did not rescan/re-hash the outer container; its exact private source-member receipts can be reproduced by the owner or independent host auditor against that container.
- Source-local `txt-local:0151`–`txt-local:0200` records expose only ordinals, filename-derived series/title hints, byte lengths and SHA256s, with **no private ZIP member paths**, owner IDs, prose, quotations, cover images or screenshots.
- Grouped filename hints include *Genesis Wave*, *A Time to...*, *Invasion*, and Voyager's introductory novelizations. These names are not independent bibliographic verification; continuations, variant editions, transcriptions and collections remain for later reconciliation.

All rows inherit `data_rights=UNKNOWN`, `member_byte_access=HASHED_WITHOUT_SEMANTIC_READ`, `work_coverage_stage=DISCOVERED`, `source_work_binding=UNRESOLVED`, and `edition_binding=UNRESOLVED`. No accepted Work, edition or narrative evidence arises from this source-file inventory.

> **Hostile challenge:** A valid SHA256 proves only that the archived byte sequence has been specifically fingerprinted. It does not authenticate its publisher edition or resolve copyright. File-based, title-based, or sequence-based counts may merge, split or double-count literature and derivative formats. The remaining LIT/OPF representations share potential conversion lineage and must not be treated as independent full-text witnesses.

## Deterministic derivative validation

The exact previous three accepted packets' canonical row hashes are pinned and rechecked. The current 50-record row hash and sequential source-local IDs are verified, including uniqueness across all four source packets and privacy/rights fail-closed controls. Tests include hostile tampering, duplicated prior hashes, extra private path fields, wrong series-boundary claims and false semantic/rights assertions.

```sh
python3 proposals/librarian/private-txt151-200-20261103/validate.py
python3 -O proposals/librarian/private-txt151-200-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_private_txt_151_200.py' -v
```

These tests validate the public-safe metadata derivative, not the withheld source text or owner authorization. **Next frontier:** read-only metadata-only fingerprinting of the final **TXT ordinals 201–220**, followed by source/work/edition external verification and omnibus/collection accounting. No merge, deployment, deletion or public copyrighted asset release authorized by this packet.
