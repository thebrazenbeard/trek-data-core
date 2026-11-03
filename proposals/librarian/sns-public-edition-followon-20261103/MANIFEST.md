# Seven public publisher ISBN manifestations — source-local extension

**Role:** LIBRARIAN. **Base:** accepted `main@2070b0153228272b5dd667b0a23465ff49a95a5f` (observed 2026-11-03 UTC). **Admission and coverage:** `NONE`.

This bounded extension lists **seven new, separately ISBN-identified public publisher product-page observations** across previously discovered Trek literary titles. It adds **zero new accepted Works**, zero Source↔Work bindings, zero literary readings and no corpus denominator changes. Format relation to an earlier paperback candidate is a **publisher-supported proposed edition association**, not proof of identical book text, a canonical Work ID, or independent narrative corroboration.

| Publisher product display title | Format | Public ISBN13 / source |
| --- | --- | --- |
| *Star Trek: Strange New Worlds: Asylum* | Hardcover | [9781668051368](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Asylum/Una-McCormack/Star-Trek-Strange-New-Worlds/9781668051368) |
| *Star Trek: Strange New Worlds: Toward the Night* | eBook | [9781668074589](https://parents.simonandschuster.com/9781668074589) |
| *Star Trek: Picard: Firewall* | eBook | [9781668046371](https://www.simonandschuster.com/books/Star-Trek-Picard-Firewall/David-Mack/Star-Trek-Picard/9781668046371) |
| *Pliable Truths* | Unabridged audio | [9781797172699](https://www.simonandschuster.com/books/Pliable-Truths/Dayton-Ward/Star-Trek-The-Next-Generation/9781797172699) |
| *Shadows Have Offended* | eBook | [9781982154189](https://www.simonandschuster.com/books/Shadows-Have-Offended/Cassandra-Rose-Clarke/Star-Trek-The-Next-Generation/9781982154189) |
| *The Higher Frontier* | eBook | [9781982133672](https://www.simonandschuster.com/books/The-Higher-Frontier/Christopher-L-Bennett/Star-Trek-The-Original-Series/9781982133672) |
| *Available Light* | eBook | [9781982113285](https://www.simonandschuster.com/books/Available-Light/Dayton-Ward/Star-Trek-The-Next-Generation/9781982113285) |

## Source access, lineage, and collision checks

1. On 2026-11-03, the seven **publisher product detail pages** above were opened and their complete rendered page text inspected through a public web reader. Each showed matching publisher title/creator, edition format, product ISBN13, imprint, publication date, and page count or runtime. These are publisher metadata pages, **not full books or audiobook contents**. The main S&S route for the *Toward the Night* eBook timed out during a direct recheck; its first-party `parents.simonandschuster.com` product page rendered the same ISBN/format/detail fields. No claim is made about an independently captured main-site response for that ISBN.
2. Exact seven candidate ISBN strings were checked against the accepted repository proposals at the pinned base with `rg`; none were already present. This is **a bounded duplicate check**, not a proof of global franchise-edition uniqueness. Source-local references to the same novel via other formats remain separate.
3. All seven source pages belong to **one Simon & Schuster corporate independence group**. The `parents.` subdomain is not an independent bibliographic corroborator. Simon & Schuster Audio is also same-lineage despite its distinct imprint.
4. The publisher page supplies *Asylum* hardcover ISBN `9781668051368` dated November 5, 2024, while an existing source-local trade paperback has a later date. This is **edition-specific**, not a new story Work or an editorial correction to the earlier paperback.
5. No raw HTTP source-page bytes were captured; exact response digests/versions are unknown. Each `source_raw_sha256` remains `null`; publisher URLs and `Product Details / ISBN13` are retrievable locators but **not immutable page receipts**.

## Privacy, rights, and acceptance gate

This batch is derived exclusively from independently accessed **public publisher pages**. It contains **no owner-private OPF fields, ISBN derivations, archive names, paths, filenames, ZIP contents, book bytes or private reading claims**. Previous private bibliographic intake remains outside the publication lineage of these records. No full copyrighted text, publisher promotional passage, cover art, audio, image URL or raw HTML is copied. The fact that a product page displays a cover is not display permission.

The metadata must remain `PROPOSED_METADATA_ONLY`. Independent source-custody review, permitted content access, edition comparison and explicit governed reconciliation are needed before any Work identity, `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, source admission, public verified Briefing, or literary coverage event can be asserted.

## Validation and next frontier

```bash
python3 -O -B proposals/librarian/sns-public-edition-followon-20261103/validate.py
python3 -B -m unittest discover -s proposals/librarian/sns-public-edition-followon-20261103 -p 'test_validate.py' -v
python3 tools/validate.py
```

The deterministic local validator pins public publisher fields, ISBN-13 checksums, no-admission invariants, source origins/locators, strict schemas and duplicate IDs. Optimized-mode adversarial cases reject swapped ISBNs, URLs, formats, forged byte hashes, private-field injection and unauthorized coverage promotion. They cannot independently attest that a publisher website remains unchanged or establish source copyright permissions. Next: another nonoverlapping **public-only** edition batch after current-main and draft collision checks, plus lawful private content custody handled separately.
