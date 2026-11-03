# DS9 custody/authenticity addendum (candidate-only)

Source-identity gate checked against [accepted main](https://github.com/thebrazenbeard/trek-data-core) and [Director hold #23](https://github.com/thebrazenbeard/trek-data-core/issues/23) on 2026-11-03 UTC. No new episode/script close read, Source↔Work acceptance, or coverage event was authorized or performed.

## Newly verified archival item locator

The [Online Archive of California UC Riverside MS 379 item page](https://oac.cdlib.org/findaid/ark:/13030/c84t6grz_aspace_ref54_5ke) names **“Call sheets and other material for the Star Trek Deep Space Nine episode titled ‘For the Uniform’”**, cataloged **1996**, **Box 3, Folder 15**. Its item page identifies UC Riverside Special Collections and Archives, says the collection is open for research, and warns that copyright, reproduction, licensing, and other restrictions may apply. The displayed item page contains **catalog metadata only**. The actual folder, item contents, script text, permissions and source bytes were not retrieved or inspected.

`archive_item_leads.json` records this one source-local candidate with `accepted_work_id: null`. It is outside the five existing Season 1 publisher-guide cards. Its 1996 date is **the cataloged material date**, not an independently verified broadcast date. Its title is a possible Work discovery key, **not** an accepted global identity match or evidence of a draft script. No attempt was made to convert call sheets into script coverage.

## Exact allowed Source → Work frontier

1. **Source custody:** Obtain a permitted item-consultation receipt from UCR, or authenticated and rights-authorized bytes from a publisher CD-ROM/studio source, recording custodian, collection/box/folder or disc edition, source media hash if actually available, and permitted use.
2. **Fidelity:** Identify the *specific material* actually inspected: call sheet, draft script, shooting script, or audiovisual cut. If script or audiovisual, record title, draft/revision/date or release cut, edition, and byte-addressable private locator. A call sheet alone cannot support dialogue/scene research.
3. **Work binding:** Librarian/Director route the exact source item to a governed Source↔Work proposal; reconcile uncertain title/edition matches without treating S1 candidate cards or the archive item as accepted Works.
4. **Research admission:** Only after issue #23 hold release, approved bindings, permitted full primary material access and batch admission may a DS9 worker close-read and generate source-relative entity/evidence/assertion records.
5. **Public projection:** Keep protected source bytes private. Version only lawful factual locators, hashes, compact source-relative evidence, and explicit reconciliation decisions; compute coverage from accepted events, never a marketing count.

## Hostile checks

> **Item-level is not byte-level.** Box/folder metadata proves an archive describes materials, not that any specific script draft or performance has been authenticated or read.

> **An archive title does not create a Work.** A page saying “For the Uniform” does not settle edition, release cut, or archival material identity. The current five Season 1 slots do not contain this title.

> **A boolean is not custody.** The five older route observations are historical gap receipts. If later access is obtained, publish a new independently verified source receipt; never silently flip their unread or rights fields to imply an earlier script read.

The associated source-route validator now checks exact closed record keys, `1.0.0` schema versions, route identity, exact observed URLs and source-evidence locators, lineage, claim/evidence classification, remote access state, rights, and mandatory route-specific unread flags. Canonical JSON SHA-256 fingerprints freeze the accepted candidate receipts to prevent silent rewrites; **these fingerprints attest only to the recorded proposal bytes/semantics, not authenticity of any underlying studio source**. Negative tests execute both normally and with Python `-O`, rejecting injected admission fields, local paths, copyrighted-text fields and fabricated source access. None of these tests certifies future access to a source.
