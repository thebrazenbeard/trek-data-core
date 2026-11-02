# Private literary Work / edition reconciliation proposals

Status: **offline private proposal only**. This lane follows the OPF metadata
intake in [LITERARY_OPF_PRIVATE_INTAKE.md](LITERARY_OPF_PRIVATE_INTAKE.md),
but it does not change the intake, authoritative registry, Work table, Source
bindings, statements, coverage, or explorer. Nothing produced by this lane is
safe to commit to a public repository merely because it is bibliographic.

`tools/reconcile_literary_metadata.py` accepts an existing **private JSON
inventory** from `inventory_opf_metadata.py`, and optionally a separate
human-authored private bibliographic review JSON. It neither opens ebook ZIPs
nor reads EPUB/LIT/TXT/HTML/chapter/cover bytes. It neither calls external
catalogs nor searches the public project inventory. Input records are
validated against the intake's proposal-only invariants, capped in size,
whitelisted to descriptive title/creator/identifier/publisher/date/language
fields, and emitted to a new owner-only private JSON file outside this repo.

## Model and non-effects

| Distinct concept | This pipeline represents | It cannot claim |
| --- | --- | --- |
| File manifestation | One converted OPF description with its OPF digest and optional LIT filename *hint* | Original prose, source identity, or another independent witness |
| Edition | OPF publisher/date/identifier/language/title *descriptors*, unverified | A uniquely identified edition or manifestation of the right Work |
| Work | No Work candidate by default; explicitly reviewed component Work hypotheses only | Canonical Work ID or validated title/creator equivalence |
| Omnibus/anthology | One edition hypothesis containing **at least two distinct proposed Works** | A collection title alone proves those contents |
| Multipart single Work | One proposed Work with at least two ordered part labels | That parts are distinct Works |

Default `publication_form=UNRESOLVED`, `work_candidates=[]`. Exact normalized
title and creator matches form a `possible_related_group` **review hint only**;
the items are not merged and are not assumed to be the same edition or Work.
No title keyword, ISBN-looking identifier, LIT basename, catalog URL, or OPF
conversion can automatically promote a hypothesis. A prior OPF XML repair
remains an input review hold even if a structural review is supplied.

Every item has `status=CANDIDATE`; canonical Source, Work and edition IDs stay
`null`. Every output sets `accepted_work_effect`,
`accepted_source_binding_effect`, and `coverage_effect` to `NONE`. Its
`independent_witness_count=0` refers to independently verified source witnesses:
the converted OPF and the presumed original file are **one lineage**, not two
corroborating works. A reviewer-provided external URL is **not fetched or
verified by the script**, and does not become an accepted Source or witness.

## Private use

Requires Python 3.10+ and files located outside this public checkout.

```bash
python3 tools/reconcile_literary_metadata.py \
  --inventory /private/path/to/literary-inventory.json \
  --out /private/path/to/literary-proposals-unreviewed.json
```

The output supplies opaque local `candidate_id` values. A catalog reviewer can
then prepare a **separate private** JSON file using those IDs. This wholly
fictional example illustrates the contract, not a Star Trek assertion:

```json
{
  "schema_version": "0.1.0",
  "reviews": [
    {
      "candidate_id": "PRIVATE-LIT-<id-from-private-output>",
      "publication_form": "OMNIBUS_EDITION",
      "works": [
        {"title": "Fictional Work One", "creators": ["A. Example"], "work_type": "NOVEL"},
        {"title": "Fictional Work Two", "creators": ["A. Example"], "work_type": "NOVEL"}
      ],
      "parts": [],
      "bibliographic_references": [
        {
          "provider": "Example Independent Catalog",
          "url": "https://catalog.example.test/fictional-record",
          "retrieved_on": "2026-11-02",
          "supports": ["PUBLICATION_FORM", "WORK_STRUCTURE"]
        }
      ]
    }
  ]
}
```

```bash
python3 tools/reconcile_literary_metadata.py \
  --inventory /private/path/to/literary-inventory.json \
  --reviews /private/path/to/catalog-reviews.json \
  --out /private/path/to/literary-proposals-reviewed.json
```

For `SINGLE_WORK`, supply exactly one `works` object and no parts. For
`ANTHOLOGY_EDITION` or `OMNIBUS_EDITION`, supply at least two distinct Works.
For `MULTIPART_SINGLE_WORK`, supply **one** Work and two or more ordered string
labels in `parts`; citation `supports` must also include `PART_STRUCTURE`.
All structures require bibliographic references supporting both
`PUBLICATION_FORM` and `WORK_STRUCTURE`. The supported Work types are
`NOVEL`, `NOVELLA`, `SHORT_STORY`, `COLLECTION`, `OTHER`, and `UNKNOWN`.
`EDITION_METADATA` is an optional support kind. References must use HTTPS
URLs without embedded credentials or fragments; do not insert signed URLs,
private catalog tokens, extracted text, passages, or scans.
The program validates only the URL's syntax: it does not fetch a citation,
verify that a host is publicly reachable or safe, or establish that the
referenced catalog supports the reviewer's claim. A localhost or internal
HTTPS URL is not independent public bibliographic evidence merely because
it passes syntax validation.

All structured reviews are `REVIEWER_PROPOSED_UNVERIFIED`, **not catalog
verification by software**. Reviewers must independently inspect external
bibliographic records, title/author variants, edition identifiers, split
volumes, short-story/anthology tables of contents, component identities, and
the trustworthiness and independence of each source. An external link may be
inaccurate, stale, derivative, or simply fail to prove the cited claim.

No automatic crosswalk or source binding is emitted. A Librarian may later
draft separate Source↔Work and external crosswalk proposals against the
project's registry contract; the Consolidator and Auditor must review their
evidence, lineage, scope, editions, and reconciliation decisions before any
accepted state. `METADATA_ONLY` must never be upgraded to `EVIDENCE_BEARING`
without content/manifest/hash-grounded evidence and the normal gates. Private
file possession or format conversion does not establish copyrights or license
to redistribute text or covers.

The output refuses overwrite, creates mode `0600`, pins no-follow directory
file descriptors, and checks for parent replacement before exclusive creation.
Private JSON inputs must be regular non-symlink files: the reader opens them
with no-follow/nonblocking flags and confirms that the opened inode still
matches the pre-open regular-file check. This also fails closed when a local
filesystem race tries to substitute a FIFO or another input file.
Malformed/inconsistent inventory, unsafe paths, unparsed review targets,
ambiguous/duplicate Work components, unsupported publication forms and absent
citation support fail closed. Tool output is only aggregate counts, not titles
or filenames. JSON and any human decision metadata may still reveal private
reading holdings; **never commit the inputs, review file, or generated output**.

## Synthetic verification

```bash
python3 -m unittest discover -s tests -p 'test_literary_reconciliation_proposals.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/test_librarian_registry.py
```

All examples are fabricated. These tests verify validation, invariants, and
private-file behavior—not bibliographic correctness of any real book.
