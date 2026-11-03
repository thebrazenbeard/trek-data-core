# Private Star Trek book archives: aggregate intake receipt

**LIBRARIAN proposal only** · accepted starting point `main@d4ecd970bf28019696abd692011007d7d47f9ff8` · observed 2026-11-03 UTC.

Two user-held ZIP containers were read privately on Lappy. An independent, bounded verification rehashed the entire original containers and checked the private inventory's receipt fields, summary and owner-only mode. The existing repository intake script scanned ZIP directories and OPF package metadata; it did **not** decompress or read chapter prose, images or covers. The private inventory remains outside Git and is referenced here only by hash and byte count.

| Observation | Count |
| --- | ---: |
| Converted OPF packages | 347 |
| Parsed OPF metadata packages | 347 |
| Unique original `.lit` filename-stem matches | 345 |
| Metadata review holds | 15 |
| Original `.lit` file entries | 347 |
| Original `.txt` file entries | 220 |

The 15 holds are legacy Dublin Core namespace repair candidates, **not** verified corrections. Even a unique filename-stem match is not a Source↔Work identity, edition correspondence, proof of a full-text read, or permission to republish. The two archives are one potentially derivative source family, not independent corroboration of narrative content. The 347 OPF packages are **not 347 accepted Works**; collections, parts, conversions and duplicates may be present.

## Reproducibility and privacy

- `receipt.json` pins both container byte lengths and whole-file SHA-256 digests, the exact accepted-main intake script SHA-256, the aggregate summary and a SHA-256 of the **withheld** private JSON inventory.
- Private ownership and format were checked on Lappy WSL2 Ubuntu using owner-only mode `0600`. Neither the private output path nor its internal file/member names, book titles, identifiers, local possession metadata, cover bytes or prose are included here.
- The run used `tools/inventory_opf_metadata.py` as committed on accepted main at the recorded SHA. Re-running against the same user-held ZIP bytes is the way to independently reproduce aggregate values; this repository validator cannot inspect private containers and does not claim to do so.
- The output file was not copied to GitHub or to this proposal. Its checksum is a receipt, not a permission grant or admission decision.

## Next gates

1. Privately review the 15 metadata namespace-repair holds and the unmatched/ambiguous file-stem candidates.
2. Compare editions against independent bibliographic authorities and preserve omnibus/container versus contained-Work distinctions.
3. Establish per-edition rights and access authority separately from possession or conversion.
4. Propose Source/Work bindings with private source-byte and edition receipts; only then can a literary worker perform source-grounded reading.

**Admission effects:** zero accepted Sources, Works, bindings, coverage events, global identities, projections or independent literary readings. No public artwork release is authorized by this receipt.

Run `python3 proposals/librarian/private-opf-custody-receipt-20261103/validate.py` for deterministic no-leak and invariant checks. These validate the **public aggregate record**, not unobserved rights, completeness or authenticity of the literature.
