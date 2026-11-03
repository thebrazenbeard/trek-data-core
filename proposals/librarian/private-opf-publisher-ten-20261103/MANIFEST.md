# Librarian — owner OPF ↔ publisher bibliographic candidate crosswalk (10)

Status: **PROPOSED / SOURCE-LOCAL / NO WORK OR EDITION ADMISSION**. 2026-11-03, based on accepted `main` `885df8dc60122e55d9f37195eabd0b1a7c67b3c6`.

This intentionally small, non-exhaustive tranche connects ten already indexed OPF XML metadata observations to separate official Simon & Schuster eBook product pages. A product page independently identifies a bibliographic product; an ISBN conversion and matching title do **not** demonstrate that a privately converted LIT/OPF file is that exact edition or that rights to its contents/artwork exist.

## Actual evidence processed

- The original owner-controlled converted OPF ZIP has 347 OPF XML members among 3,846 ZIP entries. Its whole-file SHA-256 and opaque container receipt are in `observations.json`. All ten selected original OPF XML member streams were reopened **read-only**, each rehashed byte-for-byte, and compared with the accepted 347-source OPF observation ledger. Ten of ten hashes matched. No book chapter prose or jackets were read from the archive.
- Ten official [Simon & Schuster](https://www.simonandschuster.com/) publisher eBook product pages were inspected on 2026-11-03 for displayed title, contributor byline, ISBN-13, series position where present, and presence of a linked high-resolution JPG jacket reference. The exact official page URLs are recorded per row in `observations.json`. The public publisher pages are sources for publisher claims, not for authenticity of the owner's private conversion.
- Nine early *The Next Generation* single-title candidate records (`opf-local:0050`–`0058`) have source-claimed ISBN-10s which correctly convert to the publisher page's eBook ISBN-13. Their source text candidate references (`txt-local:0088`–`0094`, `0096`–`0097`) are **filename/title hints only**: they do not assert identical text, shared edition, or canonical Work resolution. This ten-row sample intentionally skips the number-eight TNG title and is not a completeness claim.
- One *Starfleet Corps of Engineers* **omnibus** (`opf-local:0009`, *Have Tech, Will Travel*) has a source-claimed ISBN-10 converting to ISBN-13 `9780743439961`, whereas the displayed official eBook product is ISBN-13 `9780743439978`. The OPF creator set has four names and the displayed product byline three. **Both conflicts remain HOLD; do not bind them as one exact edition or count the omnibus as one independently confirmed Work.** Other SCE omnibus members coexist with constituents in the archive, so duplicate/containment must be resolved separately.

## Explicit holds

| Hold | Source-local records | Reason |
| --- | --- | --- |
| OPF XML repaired namespace | `0050`–`0054` | Five legacy OPF XML documents require namespace recovery. Metadata title/ISBN are claims, not a clean XML parse. |
| Publisher name-order discrepancy | `0052` | Owner metadata says Carmen Carter; official publisher byline displays Carter Carmen. Preserve both readings. |
| Omnibus edition / contributor mismatch | `0009` | Source ISBN-10 and official eBook ISBN-13 differ; OPF/publisher contributor sets differ. |
| Jacket availability vs release authority | all ten | Publisher pages link JPG jackets. No image was downloaded, committed, or authorized for republication by this tranche. |
| Edition and Work identity | all ten | Source-local candidates only. Zero accepted edition bindings, Work admissions, or semantic coverage change. |

The publisher's linked jacket images can be individually reviewed by the artwork custodian, who must separately check source/edition linkage, permitted distribution mechanism, and rights before any in-app visual. **No jacket URL in this packet is itself a license or automatic Explorer projection instruction.**

## Determinism and scope

- `observations.json`: only opaque owner source-local IDs, original OPF XML SHA-256/byte length and bibliographic claims, exact official publisher page locators, explicit conflict states, and a deterministic sorted-key rowset digest. No private owner path, OPF text, chapter prose, images, or GUIDs.
- `validate.py`: checks every selected source hash, source OPF title/ISBN/creator, XML parse hold, accepted prior TXT filename-only hint, ISBN10→13 mathematics, official publisher product ISBN/page shape, omnibus and byline conflict preservation, and zero-Work/zero-artwork release invariants. It does **not** re-crawl publisher pages or re-open the private ZIP in CI.
- `tests/test_private_opf_publisher_ten.py`: eleven focused tests, including adversarial mutation of source hash, ISBN conflict, cover release flag, private-path leakage, repaired-XML classification, publisher byline hold, and false Work admission.

```bash
python3 proposals/librarian/private-opf-publisher-ten-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_private_opf_publisher_ten.py' -v
```

No deletions, merged decisions, protected deployments, or coverage advances are requested. Next owner-source tranche should investigate publisher edition ambiguity/omnibus constituent relationship before expanding crosswalks indiscriminately.
