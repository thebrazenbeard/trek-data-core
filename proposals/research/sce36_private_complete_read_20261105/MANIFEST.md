# S.C.E. #36 — *The Demon Book 2* (HELD owner-private complete-source read)

**Effect state:** `HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED`. One literature worker's bounded **source-local research proposal**, not acceptance onto `main`. No novel prose, audio, video, cover, publisher image, or converted ebook was copied into Git.

## Exact source and reproducible reading extent

- Accepted baseline: `3028765359001b90bc3e6b5c1835ee283b326e91`.
- User-private original: `ST ebooks.zip` member `ST ebooks/STAR TREK - SCE - 36 - Demon Bk 2.lit`, 259,797 bytes, SHA-256 `759f8692b8b20fbe5492d85015e4e176b2541e815ea920ff30d77c173aadc8ec`.
- User-private conversion: `Star_Trek_OPF_Converted.zip` (95,673,655 bytes, SHA-256 `0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f`). Its specific OPF (`7d0bbdd715aefcb480a76b0c075e5b6903a318ae40f654e4bf6cc3f21b53ffe9`), HTML (`a3b815931fafe9464bd4b74f7eff47b4218136011896f17f1aca227c4265a08d`) and TOC (`8dc0bd26adf7574247c7c5510a7bce713b59b17fceb7ae7005ece9eb6e9bd214`) were separately inspected and byte-hashed.
- Converter manifest reports one successful source with DRM label 1, exit code 0, 13 output files. That report does **not** prove a reproducible conversion from original LIT or authenticate a purchased edition.
- This worker actually read the converted narrative in memory, covering **14 ordered chapters**. `records.json` holds each source-relative chapter locator, raw-byte range, SHA-256 and original short summary. **Corrected structural boundaries:** chapter starts are the first byte of the full `<div class="chapter" id="ch_N">` tag, not the embedded `ch_N` token 21 bytes later. Chapter 1 starts at byte **7,427** and chapter 14 ends at raw HTML byte **166,413**, exactly where `backMatterPage` begins. The author biography and next-book advertisement are excluded from this novel's evidence. This succeeds an earlier packet whose chapter ranges overlapped into the next header; an independent audit caught that regression, and the prior held commit remains in history.
- The original `.lit` member and converted members were located within Patrick's OneDrive `Documents/Books`; no private source file was extracted into the repository.

## Publisher and edition boundaries

[Simon & Schuster's official publisher page](https://www.simonandschuster.biz/books/Star-Trek-The-Demon-Book-2/Loren-Coleman/Star-Trek-Starfleet-Corps-of-Engineers/9780743476102) identifies *Star Trek: The Demon Book 2*, *Starfleet Corps of Engineers* #36, Loren Coleman and Randall N. Bills, publisher Pocket Books/Star Trek, January 1, 2004, ISBN-13 `9780743476102`, ebook, 124 pages. That is a metadata crosscheck, not evidence of the private copy's licensed derivation.

The raw OPF has two different identifiers: work ISBN-10 `0-7434-7610-7` (whose checksum conversion equals the publisher ISBN-13), and generic converter-header ISBN-10 `0-9673008-1-9`. Creator rendering in the owner OPF is `Loren L. Coleman & Randall N. Bills`; the publisher renders primary author `Loren Coleman`. These differences stay source-local/unresolved. No global work/creator identity is created by the literature worker.

## Original source-relative outputs

- One private source manifestation and one local work candidate, **15 source-local entity occurrences**, **14 chapter-relative evidence observations**, **7 guarded typed assertions**, **14 chapter summaries**, one original complete-work synopsis.
- A ship seen twice around the black hole is a light-path effect, **not** proof of duplicate vessels or alternate-reality identity.
- Gold's nightmare and fears are character experiences, **not** established precognition or injury to his granddaughter.
- Tev's revised suspicion about the first anchor failure and Sha'a's separately depicted later tractor interference must **not** be flattened into a single proven act.
- The successful station and multi-ship extraction is **depicted in Book Two**. This source does not retroactively change the Book One source packet's own ending or silently reconcile cross-work identities.
- The presence of children is directly depicted; statements about earlier captives and Resaurian historical policy retain their testified/incomplete status. Eventual political treatment of the descendants remains **UNRESOLVED**.

## Validation and protected boundary

```sh
python3 -m unittest tests.test_sce36_private_source_read_held -v
python3 -m proposals.research.sce36_private_complete_read_20261105.validate
python3 -m unittest discover -s tests -q
python3 tools/validate.py
# Owner device only, optional read-only fingerprints and chapter-end recheck:
python3 -m proposals.research.sce36_private_complete_read_20261105.verify_owner_archive \
  --archive /path/to/Star_Trek_OPF_Converted.zip \
  --original-lit-archive /path/to/ST\ ebooks.zip
```

No source/work admission, canonical ledger or coverage promotion, global reconciliation, public Explorer publication, remote push, merge, deployment, copyrighted prose export, or rights assertion was performed. The packet is ready for an independent reviewer to challenge and for the Consolidator to consider only by an **explicit accepted reconciliation/admission path**.
