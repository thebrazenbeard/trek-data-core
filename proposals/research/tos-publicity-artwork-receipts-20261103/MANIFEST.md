# TOS publicity artwork — six source-local image candidates

**State: PROPOSAL / RIGHTS HOLD, no image release.** Research snapshot on
2026-11-03 UTC against accepted `main@da44aecc4a44829c2cd8c969e80ade7d311c355d`.
The exact accepted Explorer directory input
`explorer/discovery-catalog.json` had SHA-256
`2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`.
The directory's `legacy:s*:tos:*` rows remain **source-local discovery slots**,
not governed Work identities or accepted evidence.

## Source-method and results

The Commons [TOS publicity photograph category](https://commons.wikimedia.org/wiki/Category:Publicity_photographs_of_Star_Trek:_The_Original_Series)
was a discovery aid. We then read six **individual file description and
copyright-template pages**, pinned each page's Commons oldid, and compared the
claimed episode/scene against exact accepted Paramount publisher discovery
`row_id`, `title`, and `source_locator` pairs. The JSON records include raw HTML
fetch byte counts and SHA-256 receipts from one 2026-11-03 GET of each pinned
rights page. The bytes are a **fetch receipt, not immutable hosted legal proof**;
the page may render differently on later fetches. The one original Commons
JPEG fetched for research was streamed to memory and SHA-256 checked, not saved
or republished. Two Commons metadata SHA-1 values were recorded separately;
they are **not** independently measured SHA-256 digests.

| Episode (accepted directory row) | Commons publicity source | Rights-page SHA-256 prefix | Exact work link | Proof issue |
| --- | --- | --- | --- | --- |
| [The Paradise Syndrome](https://commons.wikimedia.org/wiki/File:The_Paradise_Syndrome.jpg) (`legacy:s3:tos:002`) | NBC Television, Commons `PD-US-no-notice` claim | `8f220ce861c8` | File explicitly names episode | Front/back links opened, original notice not independently adjudicated; original JPEG SHA-256 `65b0fc186de9…` |
| [Spock's Brain](https://commons.wikimedia.org/wiki/File:Leonard_Nimoy_William_Shatner_Spock%27s_Brain_Star_Trek_1968.JPG) (`legacy:s3:tos:000`) | Paramount Television, Commons `PD-US-no-notice` claim | `d552ec0cd455` | File explicitly names episode | Back link opened, front failed; current file modified |
| [Where No Man Has Gone Before](https://commons.wikimedia.org/wiki/File:William_Shatner_Sally_Kellerman_Star_Trek_1966.JPG) (`legacy:s1:tos:003`) | McFadden, Strauss Eddy & Irwin / Desilu, Commons `PD-US-no-notice` claim | `1e50702a706f` | File explicitly names episode | Historical front/back image links 403; no notice check |
| [The Naked Time](https://commons.wikimedia.org/wiki/File:Star_Trek_The_Naked_Time.jpg) (`legacy:s1:tos:004`) | Paramount Television, Commons `PD-US-no-notice` claim | `2c9887e1f383` | File explicitly names episode | No back-of-photo notice evidence located |
| [Patterns of Force](https://commons.wikimedia.org/wiki/File:Star_Trek_Patterns_of_Force.JPG) (`legacy:s2:tos:020`) | NBC Television, Commons `PD-US-no-notice` claim | `a29b166883cc` | File explicitly names episode | Uploader says they never viewed back; checked registrations instead; contextual Nazi imagery |
| [This Side of Paradise](https://commons.wikimedia.org/wiki/File:Smiling_Spock_and_Leila_Kalomi.png) (`legacy:s1:tos:024`) | NBC Television, Commons `PD-US-no-notice` claim | `c2d7030dcce1` | **Tentative:** characters + Commons file usage, not explicit episode wording | Historical front/back linked but untested; current file cropped |

## Rights/semantic hostile review (Lou-Pole model-mode)

> **Primary falsifier:** A file's Commons `PD-US-no-notice` tag, a historical
> eBay front/back link, or an uploader's copyright-registration search is not
> independently sufficient to prove U.S. original publication before 1978
> without a legally required notice on the precise distributed photograph.
> Current Commons derivatives may differ from the historical photo; other
> jurisdictions and potential trademark/personality constraints are separate.

> **Identity falsifier:** A wiki file-page usage list linking Spock and Leila
> to *This Side of Paradise* is only a proposed episode identification. The
> work association is not established by the image description itself. None
> of these directory slots imply canon reconciliation or admitted Work ID.

An **independent follow-up agent report to the Director** (reviewer model and
provider/runtime identity not supplied to this worker) of three linked file descriptions
reported that the *Paradise Syndrome* historical photo links yielded tiny
placeholder images on its retrieval (despite our browser navigation reporting
success), *Spock's Brain* had a visually legible undated front/back pair with
no apparent notice, and *Where No Man Has Gone Before* had a visually legible
dated front/back pair without apparent notice. Those observations conflict
with our own failed original-link retrieval for *Where No Man*; they remain
**separate retrieval observations**, not a reconciled rights verdict. The
reviewer could not fetch the *Where No Man* current image bytes because of
HTTP 429. U.S. Copyright Office Circular 22 notes that historical publication
facts are material; none of these visual inspections independently proves
original distribution/publication or complete rights clearance. The candidate
record scan-state fields reflect this packet author's initial fetches.

The `rights_status` of all six is **`HOLD_INDEPENDENT_REVIEW`**, not `PD` or
`LICENSED`. No file binaries, site images, displays, remote hotlinks, CSP
changes, rights grants, canonical records, semantic assertions, or coverage
effects are included. No image can be promoted by editing a flag in this packet:
separate independent rights findings and an approved release sidecar are
required. A conservative next reviewer should inspect original front/back
scans, first-publication provenance/notice, transformed-file lineage, U.S.
versus non-U.S. reuse, and attribution/nonendorsement requirements. Explicitly
reject candidates where those checks cannot be substantiated.

## Bounded deliverable and reproducibility

- **6** exact accepted Explorer episode-row crosswalks, **6** Commons file-page
  oldid references, **6** raw page-byte SHA-256 receipts.
- **1** fetched image-byte SHA-256 receipt (*Paradise Syndrome*), plus **2**
  additional Commons metadata SHA-1 values and one matching SHA-1 for the
  fetched image. All other image-byte SHA-256 fields are `null` (additional
  download attempts were throttled HTTP 429; not retried).
- **4** candidates whose Commons descriptions link a historical front and back
  scan (*Paradise Syndrome*, *Spock's Brain*, *Where No Man*, Smiling Spock),
  one with neither usable back receipt (*Naked Time*), one with uploader's
  explicit no-back admission (*Patterns of Force*).
- **0** rights approvals, **0** public-display releases, **0** images copied to
  repo, **0** governed Source/Work/Evidence/Assertion records, **0** close reads,
  **0** accepted coverage promotions.

Re-run with:

```bash
python proposals/research/tos-publicity-artwork-receipts-20261103/validate.py
python -m unittest discover -s proposals/research/tos-publicity-artwork-receipts-20261103 -p 'test_validate.py' -v
python -O -m unittest discover -s proposals/research/tos-publicity-artwork-receipts-20261103 -p 'test_validate.py' -v
```

These checks enforce exact schema and accepted directory-byte binding while
failing on invented rights grants, hotlinks, coverage effects, and silently
changed candidate bindings. They cannot verify a copyright license or prove
the historical photographic back was truly free of notice.

**Next frontier:** independent image-rights decision for the strongest
*Paradise Syndrome* original, followed by *Spock's Brain* if front/back can be
authenticated; only then optionally prepare image release sidecar pinned to
approved raw bytes and proper attribution. Preserve static licensed-artwork
fallback until an independent rights reviewer actually clears individual files.
