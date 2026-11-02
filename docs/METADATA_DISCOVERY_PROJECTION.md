# Proposed metadata-only discovery projection (not an admission path)

**Mission** means a series. **Mission Briefing** means an episode accepted
through the canonical, content-evidenced projection gate. A publisher episode
heading or slot is neither an admitted Briefing nor a complete episode read.

`tools/build_metadata_discovery_index.py` offers an offline **read-only
proposal** compiling validated publisher roster candidates and optional
review-receipt declarations into deterministically ordered JSON on stdout.
It never reads or writes `explorer/index.json`, accepted Works, Source↔Work
bindings, coverage events, or projection approval receipts. It creates no
new admission mechanism and must not be added to the public Pages artifact
without separate governance and validation.

## Local, bounded use

From the repository root:

```sh
python3 tools/build_metadata_discovery_index.py \
  --candidate proposals/discovery/tos-publisher-s01-b001-20261102/paramountplus.json \
  --candidate proposals/discovery/tos-publisher-s01-b001-20261102/plutotv.json
```

The compiler reads bounded, regular JSON files with duplicate JSON-key
rejection. Its JSON output is deterministic across candidate argument order,
and includes the exact SHA-256 of each **candidate file's original bytes**,
not a normalized replacement. The output also carries a canonical JSON
SHA-256 for reproducibility; that is an integrity receipt, **not project
acceptance**. All output fields are metadata-only and bounded by the
existing validator. Input roster completeness remains `UNRESOLVED`.

An optional review receipt is joined only by its exact candidate byte hash:

```sh
python3 tools/build_metadata_discovery_index.py \
  --candidate /path/to/candidate.json \
  --review /path/to/private/review.json \
  --snapshot-for-review /path/to/private/review.json /path/to/private/publisher-page.html
```

`--snapshot-for-review` is optional; the private publisher bytes are hashed
locally, not copied to stdout. If the receipt is structurally valid but no
snapshot bytes are supplied, only *the declaration* is represented. If bytes
match the receipt's hash, only *the byte-hash match* is represented. Neither
proves that the publisher content supports the receipt's checked slots, that
the declared reviewer is independent, or that a human review occurred.
`receipt_sha256` binds output to exact receipt file bytes. Unchecked
slots of the same candidate retain `NO_REVIEW_RECEIPT`.

## Source-local disagreement is an output, not a defect to be hidden

Every record retains its Mission, publisher, publisher independence group,
original page locator, observed date, exact candidate byte hash and its
publisher's **source-local** season/episode number and title. Identical
source-local slots across input proposals are rejected, whether their
titles agree or conflict. Different source pages can disagree; both records
remain, with two explicit unresolved lists:

- `source_local_slot_disagreements`: same Mission/season/ordinal, different
  titles across distinct page locators.
- `title_position_disagreements`: same casefolded Mission/title, different
  season/ordinals across page locators.

For example, the current candidate Paramount+ TOS roster lists *The Cage*
at Season 1 Episode 1, while Pluto TV lists *The Man Trap* there. The output
retains both positions. Both candidates use `publisher:paramount`, and this
does **not** count as independent source corroboration. No publication,
production, original-pilot, or air-order interpretation can be selected by
this projection alone.

## Strict governance boundary

There are no canonical Work IDs, source binding IDs, assertion verdicts,
episode completeness claims or coverage milestones in the output.
`canonical_work`, `source_binding`, `continuity`, `coverage`, `denominator`
and `publication` effects are all fixed to `NONE`. A `review` input is a
**proposal-only human attestation claim**, not a verified human action.
Reviewed identity metadata (if ever independently authenticated and admitted)
must eventually receive its own separately approved public projection.
Admitted episode identity would still **not** imply watched, close-read,
semantic analysis, or audited continuity.

**Release gate:** Syntactically valid Source/Work/binding JSON, a matching
`sha256:` string, a deterministic projection hash, or a declared reviewer
identity is **not evidence of actual source-byte custody or external human
approval**. Before any public metadata release, authority must verify the
underlying lawful publisher snapshot, human review and explicit acceptance,
then authorize a separate release contract. The existing canonical Explorer
may only expose episodes from its own admitted content-evidence path; this
script must never be used as a shortcut around it.

## Verification

```sh
python3 -m unittest discover -s tests -p 'test_metadata_discovery_index.py' -v
```

Regression cases include the cross-publisher TOS numbering disagreement,
input-order reproducibility, duplicate or contradictory source-local slots,
synthetic review-receipt scope, verified private snapshot byte mismatch,
exact candidate hash mismatch and ensuring `explorer/index.json` remains
unchanged. Synthetic receipts are test fixtures and do not represent actual
independent reviewer custody or publisher page inspection.
