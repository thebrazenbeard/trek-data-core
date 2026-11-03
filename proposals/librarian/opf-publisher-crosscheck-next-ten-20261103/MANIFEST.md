# Librarian proposal: ten additional private OPF ISBN ↔ publisher eBook crosschecks

**Observed:** 2026-11-03 · **Base accepted `main`:** `1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b`
**Status:** source-only proposal, not accepted Work/Edition identity, ebook close reading, or coverage.

## Source and bounded work completed

1. Read the accepted sanitized `private-opf-metadata-20261103/observations.json` (SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`) and accepted prior `opf-publisher-crosscheck-20261103/records.json`.
2. Selected **ten distinct, previously unreviewed** source-local OPF entries `opf-local:0052` through `opf-local:0061`, from the larger inventory of 347 OPFs and 75 entries with checksum-valid ISBN candidates. The original owner-private ZIPs and ebook bodies were **not** opened for this batch.
3. For each selected entry, converted the OPF-declared valid ISBN-10 to ISBN-13; independently located and read a **first-party Simon & Schuster public eBook product listing**, including product ISBN13, product-specific title and author byline, publication date, format, and About the Book text. All ten publisher ISBN13 values agree with the numerical ISBN conversions. Each listing has an exact HTTPS product URL in `records.json`.
4. Wrote **ten short original paraphrases** of the official publisher descriptions with uncertainty statements. These are *descriptions of publisher-listed products*, not verified synopses of the owner-private ebooks or observations extracted from full works. The exact source-local OPF fingerprint and original publisher creator strings remain distinguishable.
5. Validated the source-observation digest, ISBN checksums/conversions, source-local fingerprints, exact publisher locators, bounded schema, nonoverlap with the first nine, row review fingerprints, strict non-admission flags and adversarial mutation cases. The source evidence is one publisher family, not ten independent corroborating sources.

## Ten source-local results

| OPF local | Official eBook listing | eBook ISBN13 | Result |
| --- | --- | --- | --- |
| `0052` | [The Children of Hamlin](https://www.simonandschuster.com/books/The-Children-of-Hamlin/Carter-Carmen/Star-Trek-The-Next-Generation/9780743412155) | `9780743412155` | ISBN match; **creator rendering unresolved** |
| `0053` | [Survivors](https://www.simonandschuster.com/books/Survivors/Jean-Lorrah/Star-Trek-The-Next-Generation/9780743412162) | `9780743412162` | ISBN/catalog metadata match |
| `0054` | [Strike Zone](https://www.simonandschuster.com/books/Strike-Zone/Peter-David/Star-Trek-The-Next-Generation/9780743412179) | `9780743412179` | ISBN/catalog metadata match |
| `0055` | [Power Hungry](https://www.simonandschuster.com/books/Power-Hungry/Howard-Weinstein/Star-Trek-The-Next-Generation/9780743420860) | `9780743420860` | ISBN/catalog metadata match |
| `0056` | [Masks](https://www.simonandschuster.com/books/Masks/John-Vornholt/Star-Trek-The-Next-Generation/9780743420877) | `9780743420877` | ISBN/catalog metadata match |
| `0057` | [A Call to Darkness](https://www.simonandschuster.com/books/A-Call-to-Darkness/Michael-Jan-Friedman/Star-Trek-The-Next-Generation/9780743420891) | `9780743420891` | ISBN/catalog metadata match |
| `0058` | [A Rock and a Hard Place](https://www.simonandschuster.com/books/A-Rock-and-a-Hard-Place/Peter-David/Star-Trek-The-Next-Generation/9780743420907) | `9780743420907` | ISBN/catalog metadata match |
| `0059` | [Gulliver's Fugitives](https://www.simonandschuster.com/books/Gullivers-Fugitives/Keith-Sharee/Star-Trek-The-Next-Generation/9780743420914) | `9780743420914` | ISBN/catalog metadata match |
| `0060` | [Doomsday World](https://www.simonandschuster.com/books/Doomsday-World/Peter-David/Star-Trek-The-Next-Generation/9780743420921) | `9780743420921` | ISBN match; **creator rendering unresolved** |
| `0061` | [The Eyes of the Beholders](https://www.simonandschuster.com/books/The-Eyes-of-the-Beholders/A-C-Crispin/Star-Trek-The-Next-Generation/9780743420938) | `9780743420938` | ISBN/catalog metadata match |

### Honest creator mismatch

The private OPF observation for `0052` says `Carmen Carter`; the public publisher product byline displays `Carter Carmen`. The OPF `0060` contains `CARMEN CARTER` within a combined creator string, while the public publisher byline lists `Carter Carmen` among four contributors. The public publisher biographical copy mentions Carmen Carter, but this tranche does **not** silently rewrite a source-specific byline, normalize cross-source personal identity, or claim editorial resolution. Both records explicitly carry `PUBLISHER_ISBN_MATCH_CREATOR_RENDERING_CONFLICT_UNRESOLVED`. The remaining eight are publisher ISBN/metadata matches only; even those are **not** private edition equivalence.

## Provenance and publication limits

- External lineage: the first-party `www.simonandschuster.com` / Pocket Books Star Trek catalog only. All ten separate pages share **one upstream publisher family**. Citation URLs identify rendered products, **not captured raw HTML content**. The pages were read through publicly rendered search/page extraction; no exact raw webpage bytes or `publisher_raw_html_sha256` are available to this batch. Pages can change.
- Private original container identity and OPF-entry SHA-256 values are inherited from the separately audited, accepted **sanitized OPF observation snapshot**. This tranche has not re-opened owner files or independently rehashed the owner's archive bytes; do not infer an OPF-to-private-ebook content or edition binding.
- Neither original ebook text nor private member names/paths, cover images, image bytes, full publisher descriptions, or extensive copyrighted excerpts are committed. No changes to global identity, accepted reconciliation, projections, Explorer, Work membership or coverage ledgers are requested.
- Each row is fixed to its accepted source-local OPF evidence, publisher product locator, exact reviewed metadata, publisher description paraphrase, and code-owned SHA-256 of the entire deterministic row serialization. These pins guard mutation of the proposed record; they **do not** independently prove the publisher's underlying live raw bytes or the truth of its story description.

> **Hostile challenge:** A valid ISBN10 and a matching publisher eBook ISBN13 do not demonstrate that a privately converted book contains the advertised text. The publisher's inverted `Carter Carmen` byline could be a metadata error, source variant, or identity-order convention. Leave both creators as separate source strings and defer all semantic reconciliation.

## Reproduction and frontier

From the proposal directory:

```sh
python3 validate.py
python3 -O validate.py
python3 -m unittest -v test_validate.py
python3 -O -m unittest -v test_validate.py
```

The validator checks deterministic consistency against accepted metadata observations, the prior nine-record batch and code-owned reviewed snapshot. Tests include forged synopsis, extra author, private path, duplicate identifier, wrong ISBN, false Work/coverage, and unexpected-field mutations. Passing tests are not a source-content audit; reviewers must inspect first-party links and paraphrases independently before merge.

**Next source frontier:** continue beyond `opf-local:0061` with nonduplicate checksum-valid ISBN leads; hold absent or edition-mismatched publisher listings explicitly. Do not promote private ebook equivalence until a separately permitted content-specific source inspection and accepted reconciliation. The Consolidator, not this librarian batch, owns any future deterministic Explorer projection.
