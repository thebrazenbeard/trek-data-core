# SFA publisher artwork locator candidates — proposal only

Batch: `SFA-ARTWORK-METADATA-20261103-001`

Partition: `research/sfa`

Parent source-relative proposal: [`../sfa-publisher-refresh-20261103/records.json`](../sfa-publisher-refresh-20261103/records.json)
Parent JSON SHA-256: `e6965602a534a5976a371501b457eb91aa5e9375302fdc62c99a42fd9a4136d3`

## What was processed

This bounded derivative batch **read the accepted-main copy of a prior SFA
publisher-page proposal**, not any photo pixels, transcript, episode video, or
fresh private Press Express HTML snapshot. Its upstream publisher source is
`https://www.paramountpressexpress.com/cbs-studios/shows/star-trek-starfleet-academy/`,
represented by the earlier retrieval receipt at `2026-11-03T01:23:34Z`,
raw-response SHA-256
`c5753b461be1739321643286a5d9c69666d2b67b94e0fa8ab549bed2db67f332`.
The source HTML bytes are **not** included here. The upstream record is itself
`PROPOSAL_ONLY_PUBLISHER_METADATA`, not an admitted source binding. Its
publisher lineage is `publisher:paramount`, not independent corroboration.

Three previously observed filename/caption references at the upstream
`sfa-cbs-photo-filename-evidence` locator (HTML lines 1056–1150) are copied
without promotion:

| Candidate | Source-relative HTML line | Publisher filename | Caption names as metadata |
| --- | ---: | --- | --- |
| `sfa-artwork-20261103-photo-200-01` | 1079 | `SFA_200_BZ_1021_0295_RT.jpg` | Sandro Rosta; Kerrice Brooks; Karim Diané |
| `sfa-artwork-20261103-photo-200-02` | 1112 | `SFA_200_MG_1201_0147_RT.JPG` | Robert Picardo; Bill Nighy |
| `sfa-artwork-20261103-photo-200-03` | 1145 | `SFA_200_BZ_1021_0416_RT.JPG` | Bella Shepard; Zoë Steiner |

The upstream page groups these in a Season 2 early-release **media bucket**.
This is not an assertion of a Season 2 episode, still's visible content,
fictional characters, plot, or image copyright permission.

## Rights reconciliation — not a license

- [Paramount Press Express Terms of Use](https://www.paramount.com/paramount-press-express-terms-of-use): a limited, revocable authorized-user editorial/promotional permission is not an unrestricted grant for a public Star Trek directory. Mirroring or archival reuse cannot be presumed from an accessible image URL.
- [CBS Footage Licensing FAQ](https://www.cbsfootagelicensing.com/faq): public uses of CBS-owned stills are subject to reviewed, media/term/territory-specific licenses, ordinarily with fees. [Request route](https://www.cbsfootagelicensing.com/request). No request was submitted or fee incurred.
- [Existing Explorer artwork policy](../../../docs/ARTWORK_THUMBNAIL_POLICY.md): `PUBLIC_DISPLAY_PERMISSION_VERIFIED` requires independent license receipt and file hashes; publisher URLs are not proof of a right to reproduce/hotlink. No `artwork-catalog.json` or image binary should be emitted from this proposal.

Thus all three remain `NOT_ESTABLISHED` for rights. No image URL,
signed CDN URL, image byte, alleged zero-fee permission, contact attempt,
licensed asset, or deployment was added. **Committed cost: $0.**

## Validation and boundaries

`records.json` is a derivative candidate ledger in the SFA research partition,
not the Librarian's artwork inventory and not the Consolidator's projection.
`validate.py` pins the exact upstream JSON SHA-256 and verifies source identity,
independence group, retrieval receipt, evidence locator, filename, source-local
line, caption names, and all public-display/rights holds. It rejects novel image
paths/URLs, global Work IDs, altered lineage, unexpected fields, invented
permissions, and nonzero spend. `test_validate.py` exercises adversarial edits.

Run from the repository root:

```bash
python3 proposals/research/sfa-artwork-candidates-20261103/validate.py
python3 -m unittest discover -s proposals/research/sfa-artwork-candidates-20261103 -p 'test_validate.py' -v
```

Passing these tests proves only deterministic **structural consistency with the
accepted-main proposal**. It does not prove the original publisher HTML hash,
the image contents, episode identity, or legal permission.

## Exact next frontier

The Librarian may cross-index these three source-relative SFA references as
rights-**unverified** candidates only after independent review. Any true public
artwork release needs a source-specific rights decision/receipt, and must pass
the Explorer's separate `ARTWORK_THUMBNAIL_POLICY.md` gate. At the user’s $0
budget, a paid CBS licensing route is on hold unless a verified fee waiver is
offered. No rights contact or public image release is authorized by this batch.

> Hostile challenge: a Press Express file label and apparent editorial access
> do not prove that the exact public GitHub Pages use is authorized. A model
> can validate the filename lineage but cannot turn a marketing image into a
> licensed asset by categorizing it.
