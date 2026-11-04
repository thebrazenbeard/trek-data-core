# S.C.E. #35 — *The Demon Book 1* (HELD complete owner-private source read)

**Status:** `HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED`. This is a literature worker's bounded proposal based on a complete read of fifteen narrative chapters in the owner's locally converted ebook. Neither the source, the work, nor its research is admitted into accepted `main`. No copyrighted novel prose, cover, or ebook bytes are committed.

## Provenance and read boundary

- Accepted baseline: `3028765359001b90bc3e6b5c1835ee283b326e91`.
- Owner's original `ST ebooks.zip` contains `.lit` member `ST ebooks/STAR TREK - SCE - 35 - Demon Bk 1.lit` (262,020 bytes; SHA-256 `31c5149fa7bc5f9b99270c71df5accf72f2e7d5d89c73106f86b5a3b5f0275e6`).
- Owner's `Star_Trek_OPF_Converted.zip` contains one OPF (4,581 bytes; SHA-256 `d263edc0cc885417a73b27ebcd8057ebb26a956cb095d887f85d4ad5292f8eed`), source HTML (170,638 bytes; SHA-256 `66d6fb884b0374cfb98cd96d8d2b0eb9b375aeab82a8e7cc9341991d82abc0eb`), and TOC (1,893 bytes; SHA-256 `5b094a495890fa011697259fcc6ec8a3f803bfab6b27f502b0cf33a8f4eac6bc`). The full ZIP, conversion manifest, and source-local OPF inventory fingerprints are frozen in `records.json`.
- In-memory close reading covered all **15 OPF-indexed narrative chapters**. Each ordered raw HTML byte span and SHA-256 is recorded. The *Book One* read stops at the `TO BE CONTINUED` marker at raw HTML byte 166,726; following *Book Two* material is **not** included as this source's evidence.
- Independent read-only Lappy recheck matched the original `.lit` member and the OPF/HTML/TOC SHA-256, all chapter anchors, and the exact continuation boundary. The original `.lit`→converted HTML transformation has **not** been independently reproduced or authenticated as a licensed edition.

## Source and identity uncertainty

Official [Simon & Schuster publisher listing](https://www.simonandschuster.com/books/Star-Trek-The-Demon-Book-1/Loren-Coleman/Star-Trek-Starfleet-Corps-of-Engineers/9780743476096) confirms *Star Trek: The Demon Book 1*, S.C.E. #35, by Loren Coleman and Randall N. Bills, publication December 15, 2003, ISBN-13 `9780743476096`, 125 pages. It does not by itself authenticate Patrick's private manifestation or transfer distribution rights.

The owner OPF inventory `opf-local:0046` failed to capture a decorated work ISBN-10 `0-7434-7609-3`, which converts checksum-validly to the publisher's ISBN-13. A second converter-header ISBN-10 `0-9673008-1-9` is distinct. The converted OPF creator display `Loren L. Coleman & Randall N. Bills` differs from the official `Loren Coleman` variant. Both are retained as **source-local unresolved edition/creator discrepancies**, not automatic global identity reconciliation.

## Content processed; epistemic controls

- 15 original bounded chapter summaries, 12 **source-local** entity occurrences, 13 original evidence observations, six evidence-linked guarded assertions, and one original novel synopsis.
- Gold's nightmare does **not** establish harm to his granddaughter.
- Sha'a's claim that a research station was abandoned after an insanity plague is uncorroborated; testimony about political imprisonment is not an omniscient historical record.
- S'eth's reported eightfold time dilation is contradicted by a later crew measurement nearer twofold; neither is a timeless canonical physical constant.
- Tev **suspects** intentional Resaurian tractor interference; responsibility/sabotage is not independently established.
- A rescue is **ordered**, not shown completed, before the novel's continuation marker.

## Validation and effect boundary

- `python3 -m unittest tests.test_sce35_private_source_read_held -v`
- `python3 -m proposals.research.sce35_private_complete_read_20261104.validate`
- `python3 -m unittest discover -s tests -q`
- `python3 tools/validate.py`
- Optional, on a machine already holding the owner's ZIP: `python3 -m proposals.research.sce35_private_complete_read_20261104.verify_owner_archive --archive /path/to/Star_Trek_OPF_Converted.zip`; this hashes in memory without emitting source text.

Protected effect fields in `records.json` remain `NONE`/`false`: no accepted Source/Work binding, CLOSE_READ coverage promotion, global entity identity merge, public Explorer change, copyrighted source export, merge or deployment. The packet is ready for independent source, semantic and rights review, **not** for automatic admission.
