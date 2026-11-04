# Starfleet Academy — corrected Wikidata series-QID discovery (held)

**Packet:** `SFA-WDQS-CORRECTED-QID-20261104-001` · **role:** SFA audiovisual worker · **disposition:** `HELD_WDQS_SOURCE_RELATIVE_CANDIDATES` · **date:** 2026-11-04 UTC.

Accepted `main` baseline: `3028765359001b90bc3e6b5c1835ee283b326e91`. This is a **new** Wikidata query against the previously identified redirect target `Q117350388`. It does not alter the original two accepted zero-result receipts against `Q134592591` or retroactively reinterpret them. The SFA publisher video-route proposal and [prior held crosswalk](../sfa-wikidata-crosswalk-audit-20261104/MANIFEST.md) remain unaccepted branch input; this packet is stacked locally for continuity.

## Preregistered read-only request and exact receipt

I issued **one** GET using the exact [`queries/sfa-current-qid.rq`](queries/sfa-current-qid.rq) text against `https://query.wikidata.org/sparql`, requesting English labels of direct `P179` series members, with OPTIONAL `P1545` series ordinal and OPTIONAL `P4908` season-item/season ordinal bindings. `ORDER BY ?episode LIMIT 40`; 30-second timeout, a 1,000,000-byte read cap, JSON Accept header and named user agent. No retry, mirror endpoint, rate-limit bypass, credential or paid action.

| Receipt | Actual observed value |
| --- | --- |
| HTTP | `200`; `application/sparql-results+json;charset=utf-8` |
| Server Date header | `Wed, 04 Nov 2026 11:40:54 GMT` |
| Observation clock | `2026-11-04T11:40:54.777494+00:00` |
| Exact UTF-8 query SHA-256 | `6611641ce34596d7f6f90b7050d5da4f4c9ea30cb7257d393899b5074034cce2` |
| Raw JSON response bytes | `4,069` |
| Raw response SHA-256 | `3cd6579c8073e9e5f1547542b59a28384879917149615e5c36b00df11eb4d161` |
| JSON result bindings | `11` |
| Returned ordinal bindings | `0` |

The response was decoded in the read-only tool process, and all eleven returned item URI/English-label/season-item values were normalized into `candidates.json`. **The exact 4,069 response bytes were not retained in the public tree.** Thus this is an operator-observed primary WDQS response receipt, not a durable raw-response rehash or independent authenticity attestation. Any future independent replay must use the saved query and compare a fresh (possibly changed) response; the original raw digest alone cannot prove long-term source immutability.

## Source-relative findings

| Observed category | Number | Interpretation |
| --- | ---: | --- |
| Direct `P179` series-member rows | 11 | The query is **not typed** as episodes; `P179` alone does not establish installment identity |
| Rows with titles matching Paramount+ labels exactly | 9 | Metadata crosswalk leads, not admitted Work identities |
| Case-only title variant | 1 | WDQS `Vox In Excelso` vs official publisher `Vox in Excelso`; preserve both spellings |
| Season-labeled series member | 1 | `Q137786752`: `Star Trek: Starfleet Academy, season 1`; held as potential non-episode member |
| Wikidata episode/season ordinals returned | 0 | Do not borrow publisher episode numbers as if Wikidata supplied them |

The ten plausible installment-title leads have IDs `Q137793912` through `Q137793918` and `Q137793920` through `Q137793922`. Their `P4908` season item is `Q137786752`, but no `P1545` ordinal was returned for that item. `Q137793919` was not among bindings; a QID numeric gap is **not** evidence of a missing installment or lost source. Every `publisher_episode_hint` in `candidates.json` was **derived by title matching to the publisher roster**, never claimed as a Wikidata episode ordinal. Case-folding was used only for identifying the one case variant; original labels remain exact.

## Source, Work, evidence, and identity boundaries

- Wikidata is a third-party structured discovery registry with a distinct provider from Paramount, **not** independent audiovisual evidence for plot, dialogue, fictional continuity or canonical Work identity.
- `Q137786752` may be a season item, but we examined no `P31` statement here. The label alone does not formally certify ontology. It is explicitly excluded from publisher episode-title pairing while retained as a source-local row.
- `P179` results can include non-episode members; the prior Enterprise audit's story-arc false-positive is an independent methodological warning, not a fact about these SFA candidates.
- No FULL_TEXT_AVAILABLE, CLOSE_READ, SEMANTICALLY_ANALYZED, canonical Source↔Work binding, denominator or coverage effect. Admission issue #23 remains open.
- No primary audiovisual source, script, caption track, still image, or copyrighted transcript was fetched or processed.

> **Hostile challenge:** An automated importer could declare eleven episodes simply because eleven `P179` rows returned. This query itself supplies a counterexample: one row bears a season title, not a normal installment title. The remaining ten are candidates whose type, exact ordinal, completeness and source binding have **not** been independently authenticated.

> **Lineage challenge:** Ten labels correspond closely to the Paramount roster, but Wikidata may be downstream of publisher or community cataloguing sources. Different domains do not establish independent sourcing. A source editor's copy of a publisher label is not independent corroboration of a fictional-world event.

## Validation and exact next frontier

Run from repository root:

```bash
python3 proposals/research/sfa-wdqs-corrected-qid-20261104/validate.py
python3 -m unittest discover -s proposals/research/sfa-wdqs-corrected-qid-20261104 -p test_validate.py -v
python3 tools/validate.py
```

The deterministic validator checks query SHA and corrected QID, fixed 11 source-relative labels/QIDs, ten title-only joins, absent ordinals, five falsifier holds and all zero-effect constraints; adversarial tests reject admission, count and type inflation. No script claims to authenticate the unretained raw response bytes.

**Next valid frontier:** After separate preregistration, a Librarian can review item-by-item Wikidata type/ordinal/source claims for `Q137786752` and ten title leads, and decide whether any have independent, rights-valid provenance suitable for the governed Source↔Work process. This is still discovery. Do not run CLOSE_READ until issue #23 admits primary episode sources.
