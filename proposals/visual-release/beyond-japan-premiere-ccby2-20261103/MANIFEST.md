# One-source CC BY 2.0 documentary photo release — affirmative proposal

This is a **text-only, proposed affirmative** editorial release decision for a single Dick Thomas Johnson photograph of the October 19, 2016 *Star Trek Beyond* Japan premiere. It is **not a film frame**, a fictional source, a publisher endorsement, or a grant of general publicity/trademark rights.

No image bytes, site effects, Work admissions, or coverage advances are included here. Accepted held records remain byte-identical and authoritative until a separately reviewed, owner-accepted successor changes the release status:

- `proposals/librarian/beyond-japan-premiere-ccby-display-criteria-20261103/contract.json` (SHA256 `9ed8d519d8bba7ef7e605ad0d09bdcf74dd7f48c9f9c1ef829dc28772ab8e4a5`)
- `explorer/beyond-premiere-release-decision.json` (SHA256 `b3041c0fe9ed739c1187b5d9da97e9817dfca753683ca100bd8c93263b68cd89`)

`decision.json` proposes only the **one** original source-linked, same-origin 960×640 JPEG (116,536 bytes; SHA256 `e8c2933469a00fb2c8b142f41472153ed7982c05f98f9c7c154b6bea689cc06f`) after independently reviewed license, visible attribution, modification and no-endorsement notices, browser consent/accessibility evidence, and Patrick's release acceptance. The photographer's CC BY 2.0 license applies to photographer copyright; other rights require contextual assessment. Existing review IDs establish prior scrutiny of *held* source and UI, **not** affirmative publication approval. Full reviewer and source/evidence distinctions are in the decision record.

## Validation / next gate

`python3 proposals/visual-release/beyond-japan-premiere-ccby2-20261103/validate.py` and its `test_validate.py` intentionally fail if accepted held contracts change, a JPEG appears in the proposed public location, any positive disposition is prematurely asserted, or the source/rights/bytes/consent receipts drift. This proposal is not itself read by the Explorer at runtime.

After two independent affirmative exact-head reviews and Patrick's accepted release disposition, prepare a **separate** binary + UI branch and test the exact 116,536-byte file, JPEG dimensions/SHA, no external fetch, keyboard/viewport behavior and actual permitted-browser screenshot before merge/deployment. Do not flip the old false records in place.
