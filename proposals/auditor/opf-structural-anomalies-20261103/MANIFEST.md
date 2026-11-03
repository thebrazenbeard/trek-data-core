# Private converted OPF archive — structural anomaly audit

**AUDITOR proposal only**, based on accepted `main@69f0a5c46e78b9d034ff168d969374892fc997e0` and the accepted, pinned 347-row private-derived OPF metadata observation. This audit was performed read-only against the owner's actual ZIP on Lappy. The public record contains only source-local OPF IDs, anomaly classes and counts: no private member paths, book text, image bytes, covers, screenshots, quotations, local account identifiers or rights claims.

| Finding | Observed result |
| --- | ---: |
| Converted OPF XML packages matched by exact XML-byte SHA-256 to accepted source-local IDs | 347/347 |
| Strict XML parses with external entity resolution disabled | 332 |
| Strict XML namespace failures (`dc:` used without an available declaration) | 15 |
| Manifest item hrefs examined in the 332 parseable OPFs | 2,626 |
| Literal archive-member target misses | 3, in one source-local OPF |
| URI-semantic misses including fragment splitting and percent-decoding | 8, in six source-local OPFs |
| Unresolved UTF-8 LIT filename middle-dot (`U+00B7`) → OPF stem pairing candidate | 1 |

The three literal misses occur in an OPF whose manifest points to a multi-part compilation using raw `#` characters in filenames/hrefs; three separate XHTML/HTML targets exist in the private archive, but the literal manifest attributes point incorrectly and URL parsing treats the first `#` as a fragment delimiter. Five additional hrefs have matching **raw** ZIP filenames containing literal `%26`, but URL percent-decoding changes that sequence to `&`, so the decoded paths no longer match. Their encoding should be reviewed in a private correction workflow rather than silently rewritten in public metadata. The other 15 OPFs require in-memory legacy Dublin Core namespace recovery for metadata extraction; raw OPF bytes remain unchanged.

An original LIT filename associated provisionally with converted OPF candidate `opf-local:0156` contains the actual Unicode **middle dot** (`U+00B7`). The ZIP entry's flag bits are `0x0808`, which explicitly include the UTF-8 filename flag (`0x0800`). Independent Python ZIP inspection found **zero** replacement characters (`U+FFFD`) among the 347 original LIT filenames. An earlier terminal display rendered the middle dot as `�`; that was a console representation artifact, **not** an observed replacement character in the source name. The U+00B7 punctuation creates a *filename-stem pairing question*, not proof of text corruption, a distinct Work or edition. Keep the potential LIT→OPF association unresolved; do not silently strip punctuation or count both archives as independent sources.

> **Hostile challenge:** Strict isolated XML parsing can fail on undeclared namespace prefixes, but recovery is a parser accommodation, not an authoritative correction to the source or an endorsement of a particular edition. Manifest integrity does not by itself establish complete text, and a source member need not equal one Work: the archive contains omnibus/constituent relationships. The 347 OPFs are conversions in a possibly shared lineage with the original 347 LIT members; file counts are not distinct-Work counts.

The accompanying `validate.py` pins the accepted OPF derivative bytes and its source-local parse statuses. The synthetic tests separately demonstrate fail-closed XML namespace, unescaped-fragment, percent-decoding, actual UTF-8 middle-dot pairing and a rejected spurious replacement-character claim. They cannot reproduce the private ZIP from public Git; independent re-audits require the owner's original ZIP and per-entry SHA-256 matching.

There are **zero** Source→Work admissions, verified edition bindings, literary full-text reads, source-grounded narrative assertions, coverage effects, licensed book-text publication or artwork approvals in this proposal. `data_rights=UNKNOWN` remains unchanged. No Explorer auto-ingestion, publication, merge or deployment is requested.

Verification:

```sh
python3 proposals/auditor/opf-structural-anomalies-20261103/validate.py
python3 -m unittest tests.test_private_opf_structural_anomalies -v
```

**Next frontier:** The Librarian can review affected raw OPF namespace and href records on the owner host, classify malformed conversion-vs-source differences, and submit explicit versioned correction proposals. The Consolidator must preserve unresolved edition, Work and omnibus containment identity until corroborated.
