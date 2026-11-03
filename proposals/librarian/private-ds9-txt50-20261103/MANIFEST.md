# Private Star Trek TXT member fingerprints: DS9 001–050

**LIBRARIAN proposal only.** Baseline accepted `main@b75328ef7a75d0dc272323cd7a8478f269027644`; observed 2026-11-03 on the owner's Lappy. This is a source-local **file inventory** and not a 50-Work literary corpus admission.

## Source and scope

- Source container: `OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B`, prior independent accepted container receipt SHA-256 `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`, 126,481,241 bytes. This run confirmed the private local ZIP byte length matched its separate SharePoint listing; it **did not rehash the whole container**.
- Central directory: **573 members = 347 LIT + 220 TXT files + 6 directories**. It recorded no case-insensitive exact-name collisions. The separate converted archive contains 347 OPF XML packages along with images and HTML; it is potentially derivative of the LIT source family and does not count as independent corroboration.
- Bounded sample: first **50 lexically sorted TXT entries**, with original filename sequence hints **DS9 001–050**. Each member was opened directly from the ZIP in streaming read-only mode solely to compute an exact-member SHA-256, not to read chapters or interpret prose.
- The 50 members contain **25,579,763 uncompressed bytes**, with **50 distinct SHA-256 values** and **zero exact-byte duplicates inside this sample**. Nothing about the other 170 TXT members, the 347 LIT files or possible cross-format semantic duplicates is established by that zero.
- Public `observations.json` contains only an opaque source-local ID, ordinal, filename-derived display-title hint, byte length, and member fingerprint. No original member path, owner account/SharePoint identifier, text, cover image, screenshot, description or extracted quotation is published.

## Identity, editions, and coverage

| Question | Actual finding |
| --- | --- |
| Were 50 source-member bytes opened for hashing? | **Yes.** Streaming hashing was the only content-byte operation. |
| Were 50 full books read or structurally indexed? | **No.** No prose, chapters, paragraphs, or narrative assertions were processed. |
| Are these 50 unique literary Works? | **Unresolved.** Names and different hashes alone cannot settle Work, volume, story, or edition identity. |
| Are the private TXT entries authenticated editions? | **Unresolved.** No independent publisher comparison or rights-holder validation in this batch. |
| Is any Source→Work binding admitted? | **No.** `source_work_binding=UNRESOLVED`; `work_coverage_stage=DISCOVERED`. |
| Has any release, citation, or public full-text use been authorized? | **No.** `data_rights=UNKNOWN`, no full text, images, or coverage effects. |

Note particularly the filename-derived *Avatar (Book 1)*/*Avatar (Book 2)* and *Worlds of Deep Space Nine* volumes: multiple files might relate to different literary works, parts, collections, editions, or copied formats. No automatic grouping/merging was performed.

> **Hostile challenge:** A byte hash identifies one ZIP member's current bytes, not a licensed edition, authoritative transcription, canonical Work or legitimate downstream publication. A public filename-derived title is a lead, not proof of original title or authorship. The owner ZIP is required to independently reproduce member fingerprints, and the member locator map is intentionally withheld. All Work and edition claims remain pending independent bibliographic source checks.

## Deterministic public validation

`observations.json` pins a SHA-256 over a canonical JSON serialization of its exact 50 records (sorted object keys, compact separators, UTF-8). Its locked format asserts no rights, Work admission or source binding, and tests reject changes to source container receipt, record hashes, private-path injection and duplicate member fingerprints:

```sh
python3 proposals/librarian/private-ds9-txt50-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_private_txt_fingerprints.py' -v
```

These tests validate the **public derivative**; they do not substitute for rehashing the owner's ZIP, accessing a publisher's edition record, or reading the books.

**Next LIBRARIAN frontier:** privately fingerprint the remaining 170 TXT members; compute file-hash and stem-pairing duplicate candidates across original LIT and OPF lineage; resolve the known replacement-character TOS filename anomaly without silently rewriting history; review omnibus/member containment and externally verify edition claims. No global reconciliation or publication effects in this tranche.
