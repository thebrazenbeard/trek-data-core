# Owner-held Star Trek TXT source-member receipt: positions 101–150

**LIBRARIAN proposal only**, observed 2026-11-03, branch baseline accepted `main@05d05de1c0238ed7ff39bd04427795e351f9b68b`. Previous source-local 1–50 and 51–100 packets are already accepted on that main; their bytes and record IDs remain unchanged.

## Source observation

The private original ebook container `OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B` is identified by the already independently verified whole-container SHA-256 `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`, 126,481,241 bytes, 573 ZIP entries (347 LIT, 220 TXT and six directories). This tranche read that owner's ZIP via Lappy's read-only ZIP API. The ZIP member directory was sorted lexically and all TXT entries given source-local positions.

Exactly **50** TXT member byte streams at sorted positions **101–150** were opened solely to compute their original, uncompressed SHA-256. Their filename-derived family prefix is TNG; filename-derived sequence numbers are **014–063**. Member uncompressed lengths total **19,841,335 bytes**. None of the prose was interpreted as narrative evidence, structurally indexed, quoted, exported or publicly published; no archive member was extracted onto disk.

| Check | Observation |
| --- | ---: |
| Current bounded sample | 50 TXT source-member receipts |
| Exact-byte fingerprints unique within current sample | 50 |
| Duplicate member hashes across accepted previous 100 | 0 |
| Total first-three-packet source members now fingerprinted | 150 |
| Distinct exact-byte fingerprints across all three packets | 150 |
| Total first-150 uncompressed TXT member bytes SHA-hashed | 65,506,900 |
| Original TXT file members remaining for source-level hashing | 70 |
| Verified separate literary Works, editions or publisher authorizations | 0 |

The filename sequence includes *Invasion*, *Q Continuum*, *Double Helix*, *Gemworld*, and *Maximum Warp* labels. These are **unreviewed filename hints**, not independent authoritative edition, chronology, omnibus, or Work/part classifications. Distinct TXT byte hashes do not imply distinct literary Works; identical/near-identical stories can appear in multiple formats or editions, and collections may enclose multiple Works.

## Privacy and evidence boundaries

- `observations.json` contains only opaque `txt-local:0101`–`txt-local:0150` source-member IDs, ordinal, filename-derived series/title hints, uncompressed byte lengths and per-member SHA-256. Original ZIP member paths, owner host/account identifiers, prose, excerpts and images are excluded.
- `data_rights=UNKNOWN`; `member_byte_access=HASHED_WITHOUT_SEMANTIC_READ`; `work_coverage_stage=DISCOVERED`; `source_work_binding=UNRESOLVED`; `edition_binding=UNRESOLVED`. No public Work count, accepted literary Source→Work binding, full-text reading, edition assertion or right-to-republish inference is justified.
- The prior two accepted packets' exact deterministic SHA-pinned row receipts are referenced and cross-checked, including a fail-closed guard on duplicate IDs and exact-byte fingerprints across **all 150**.

> **Hostile challenge:** Filename normalization cannot rescue a mislabeled or incomplete private transcription. The container receipt and 50 member digests make this source-file observation reproducible with the private ZIP, but do not authenticate a publisher edition, verify human transcription quality, or authorize public copyright use. No automated projection may promote these file observations to canonical Works or source-bound narrative claims.

## Deterministic validation

```sh
python3 proposals/librarian/private-txt101-150-20261103/validate.py
python3 -O proposals/librarian/private-txt101-150-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_private_txt_101_150.py' -v
```

The validator checks exact source metadata, record SHA-256, ordinal/series consistency, sequential nonoverlap with both accepted packet digests, privacy constraints and absence of false rights/coverage/edition claims. Nine adversarial Python tests exercise these invariants. These Git checks validate the derivative and do **not** themselves rehash the owner-held ZIP or read literature.

**Next Librarian frontier:** original TXT ordinals **151–200**, then **201–220**; later evaluate cross-format LIT/OPF file lineage and book/collection/omnibus/edition relationships with independent bibliographic evidence. No merge, deployment, deletion, copyrighted-image release or global reconciliation in this proposal.
