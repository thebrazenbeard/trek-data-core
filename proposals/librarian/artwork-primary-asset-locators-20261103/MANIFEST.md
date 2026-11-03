# Primary-publisher artwork locator recheck — Librarian batch

**Batch:** `ARTWORK.PRIMARY.LOCATORS.20261103`  
**State:** ten **source-relative image URL observations**, proposal only.  
**Accepted baseline inspected:** `main@ab268db0a822508565c264ab7c7537b1cdda1dfc` (2026-11-03).  
**Effects:** no accepted Work/identity/reconciliation, Explorer, coverage, download, public artwork release, or deployment effect.

## Actual observations and attribution

| Source-local Work or edition | Medium | First-party provenance read | Image locator type | Release |
|---|---|---|---|---|
| `film-wrath-of-khan` | Film | StarTrek.com *Wrath of Khan* film page, HTTP 200; `og:image` | Publisher site-wide/header artwork, **not** verified theatrical poster | HELD |
| `film-nemesis` | Film | StarTrek.com *Nemesis* film page, HTTP 200; `og:image` | Publisher header, not verified poster | HELD |
| `film-2009` | Film | StarTrek.com *Star Trek* (2009) film page, HTTP 200; `og:image` | Publisher header, not verified poster; file is oddly named `STARTREK_IX_HEADER` | HELD |
| `lit-sns-kobayashi-maru-ebook-9780743419987-20261103` | Literature | Simon & Schuster rendered publisher edition page; ISBN `9780743419987` | Linked high-res cover for **eBook** edition | HELD |
| `lit-sns-shadows-of-the-sun-abridged-audio-9780743546744-20261103` | Literature | Simon & Schuster rendered publisher edition page; ISBN `9780743546744` | Linked high-res cover for **abridged audiobook** | HELD |
| `lit-sns-genesis-wave-three-adapted-audio-9780743546591-20261103` | Literature | Simon & Schuster rendered publisher edition page; ISBN `9780743546591` | Linked high-res cover for **adapted audiobook** | HELD |
| `snw-s3-e01-pplus` | Episode | Paramount+ *Strange New Worlds* S3 guide, episode 1 card | Official 400px episode-card thumbnail | HELD |
| `snw-s3-e05-pplus` | Episode | Same Paramount+ guide, episode 5 card | Official 400px episode-card thumbnail | HELD |
| `snw-s3-e06-pplus` | Episode | Same Paramount+ guide, episode 6 card | Official 400px episode-card thumbnail | HELD |
| `snw-s3-e10-pplus` | Episode | Same Paramount+ guide, episode 10 card | Official 400px episode-card thumbnail | HELD |

The exact ten source URLs, CDN locators, source-local IDs, image kinds, source attribution groups, reading receipts, and digests appear in [`records.json`](records.json). The four SNW artwork locators are **already present** in previously accepted SNW *source-local research proposals*: this packet adds no episodes, and the repeated presence is **not independent corroboration**. It explicitly checks each against its existing source-bound Work and source candidate.

## Retrieval and evidence limits

- Three StarTrek.com film pages were read as publisher HTML; `og:image` metadata was observed. The HTML response digests and sizes are in the records. Publisher page metadata proves **what image the publisher page points at**, not the owner of the asset, poster identity, or licensing terms.
- Three Simon & Schuster rendered publisher edition pages provided product ISBN and linked `Resources and Downloads > High Resolution Images > Book Cover Image` URLs. Direct raw-page requests returned HTTP 403; image-link navigation returned a binary-decode failure while revealing the exact link target. **No image contents were read.** ISBN applies to *publisher edition*, not an unverified privately owned ebook file. Audio-cover-to-print-edition substitution is prohibited.
- The Paramount+ season-three page was read directly as HTML (HTTP 200; 271,774 bytes; recorded response SHA-256) with episode-card `img` URL anchors. HTML is volatile; line anchors and digest describe a specific reading, not a durable publisher revision.
- Memory Alpha is secondary **discovery/crosswalk only**. The previously accepted `memory-alpha-artwork-discovery` packet records search-indexed file-title leads; robots-blocked file-description routes were not retried here. Its file-name leads cannot serve as first-party attribution, independent publisher corroboration, or copyright license.
- All ten image URLs are metadata **locators**. No third-party binary image files were downloaded or committed, no asset dimensions/pixels were checked, and no public hotlinks were inserted. The source page link is not itself an image redistribution license; no explicit rehosting/display authorization has been established.

## Deterministic checks and known falsifiers

Run from repository root:

```bash
python3 proposals/librarian/artwork-primary-asset-locators-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/artwork-primary-asset-locators-20261103 -p 'test_*.py' -v
```

The validator pins four accepted-source input hashes **and separately pins each of the ten exact first-party-page-observed asset URLs to its immutable batch-local observation ID**. It checks expected media and source-local bindings, source URL host/lineage, exact publisher ISBN/format or episode card Work, and forbids accidental display release/coverage claims. Mutation tests cover license escalation, public Explorer effect, asset fetching, input digest drift, episode image swapping, print/audio edition confusion, forged film binding, duplicate IDs, and URL userinfo/control characters. **Adversarial same-host film substitution, publisher film-image swap, and fake same-ISBN high-resolution book-cover URLs all fail.** It does not independently authenticate remote publisher content; that evidence is captured as source-specific reading receipts. The expected URL pins are code-reviewed observations, not image-byte digests or an external signature.

### Post-admission corrective validation (append-only, 2026-11-03)

The initially merged validator left a provenance identity crossing undetected: exchanging *both* the source-local film ID and publisher page URL between the Wrath of Khan and Nemesis observations yielded no errors while their local IDs retained their original, correct CDN locators. The film catalogue checks still passed because the swapped page and film ID agreed with each other; an unordered film-ID census did not bind those pairs to the unchanged artwork observation. That pre-correction counterexample was reproduced against accepted main.

The corrective validator pins the **entire ten-row local ID → medium → source-local work/edition ID → exact publisher page URL → source input path tuple**, alongside the existing exact image URL map. It also pins all four source-input **paths as well as their SHA-256 digests**, preventing an arbitrary in-repository JSON source with a newly computed correct hash from masquerading as a reviewed input. New hostile mutations explicitly exchange both film identifiers and their page URLs without touching image URLs, substitute a page from the same publisher family, alter a season source input, and replace a source file with its true matching SHA. These fail under ordinary and `python -O` execution. No records, artwork URL, rights status, source-reading claim, or previous accepted history were changed.

> **Hostile review:** A source-controlled CDN URL is not an express license to display, republish, or embed the graphic. A “High Resolution Images” marketing download link is insufficient to assume a standing general-use license. A header filename containing `IX` on the 2009 film page is not proof of the image's content. Image-location correctness and public image rights remain separate unresolved questions.

## Next frontier

Use this source-only packet for a future attribution/review ledger. Preserve `HELD_NO_PUBLIC_DISPLAY_LICENSE` until image-specific permission or defensible license terms are documented and reviewed. Obtain independently reviewed source/edition identity and licensing before proposing any Explorer thumbnail release. No reconciliation or Explorer mutation is authorized by this packet.
