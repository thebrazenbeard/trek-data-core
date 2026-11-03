# Librarian Source↔Work preflight: exact private bytes to proposed records

The accepted registry currently lacks a reviewed nonfixture Source, Work and Source↔Work binding for the next held research lane. Issue #23 correctly keeps new content research paused. `tools/propose_librarian_source_work.py` closes **one mechanical handoff**, not the admission decision: it deterministically replays an existing `source_custody_receipt` against the exact private file and emits a triad of schema-valid **PROPOSED** records. It does not modify any files, accept records, emit coverage, or read source content semantically.

## Actual workflow

1. Capture a request/receipt pair from an authorized private source copy using `tools/source_custody_receipt.py` as described in [Source custody receipts](SOURCE_CUSTODY_RECEIPTS.md). Retain the bytes, request, and receipt privately; do not put full scripts, episodes, novels, captions, or ebook files in Git.
2. Record an explicit, unverified human Work identity declaration in another private JSON file, e.g.:

```json
{
  "record_type": "work_identity_declaration",
  "schema_version": "1.0.0",
  "proposal_id": "proposal-replace-with-real-001",
  "work_candidate_id": "work-replace-with-real-001",
  "work_title": "Replace with edition-verified title",
  "work_type": "EPISODE",
  "work_identity_note": "State the specific independent source and reason this local representation maps to this Work.",
  "work_identity_reference": "https://www.startrek.com/",
  "fixture_only": false
}
```

This is an **input template**, not a new Trek observation or an accepted identity. The reference is a declared clean public metadata URL, not an authenticated byte identity or independent review. No automatic media downloads are performed.

3. Re-verify exact current bytes **and** the receipt before constructing proposed candidate records:

```sh
python3 tools/propose_librarian_source_work.py \
  --request /private/request.json \
  --receipt /private/receipt.json \
  --source-file /private/exact-source-file \
  --work-declaration /private/work-identity.json \
  > /private/librarian-proposal.json
```

The JSON contains `source`, `work`, and `source_work_binding` that pass the Librarian contract but retain `status/lifecycle=PROPOSED`, `mapping_role=METADATA_ONLY`, explicit input `fixture_only`, and `accepted_registry_effect=NONE`. Synthetic inputs **must** set `fixture_only=true`; real-source operators may declare false, but that declaration itself is not authenticity proof. `BYTE_HASH` proves only which private bytes were read at this invocation, *not* the declared title, publisher, narrative authenticity, lineage independence, copyright clearance, or Source↔Work identity. That is why the binding remains metadata-only. The machine-readable `admission_blockers` are not review approvals.

The generator refuses `fixture_only=false` when explicit synthetic/fixture/test-only markers survive anywhere in Source custody identifiers, locator, version, edition, provenance/independence labels, Work identifiers/type, or clear fixture descriptions. This includes the adversarial case where someone relabels `SYNTHETIC_ONLY` provenance while leaving `source_version=fixture-v1` or an `edition_identity` saying `synthetic fixture`. Ordinary story titles about synthetic beings are not automatically test fixtures. These consistency checks cannot authenticate arbitrary declarations or detect a synthetic input deliberately disguised as a real edition. Nonfixture output is still only an operator-labeled **PROPOSED** record.

Work-title fields also reject embedded absolute POSIX paths after punctuation delimiters (for example `Episode|/private/secret-path`), as well as after whitespace. Ordinary title separators such as `A/B` remain valid. This reduces accidental private path echo in proposal JSON; source filenames are never placed in proposal output.

4. A Librarian can then investigate source edition, upstream lineage, public/private identity and lawful access; an independent Auditor must challenge any proposed promotion. Separate versioned review/reconciliation, accepted authoritative file-backed records, and governed coverage are still needed before `SOURCE_BOUND` or `CLOSE_READ`. Never copy generated candidates into `registry/authoritative` and silently flip flags. This CLI deliberately contains no promotion option.

## Bounded next acquisition: TOS “Charlie X”

The held [TOS derivative research proposal](../proposals/research/tos-charlie-x-derivative-close-read-20261103/MANIFEST.json) records a previously read public derivative HTML transcript, reportedly fetched from `https://tvmeg.com/index.php/2023/08/07/charliextrans/`, at 144,687 raw bytes and SHA-256 `4498f2ac33c4e1aa4c48123aab84254b890fb9dd8603f0540189d7abdcd3c616`. It self-reports an upstream transcript source and disagrees with a first-party episode-number convention. Its raw bytes were **not** durably preserved as an independently replayable custody file, and no official full episode, script, or edition has been authenticated. These values are **proposal-reported**, not reverified here.

The narrow re-entry gate is to obtain an authorized stable source representation of the actual Work (preferably primary licensed episode audiovisual or publisher script) under private custody, capture and independently replay its exact hash, document its edition and provenance, compare publisher identity metadata, then create a proposed Source/Work triad for independent review. A fresh derivative transcript may be separately captured and labeled `TRANSCRIPT_REPRESENTATION`, but it must never be relabeled as the primary audiovisual episode or treated as independent of the source from which it derives. A changed HTML capture digest is a new representation, not proof the original claim was false.

Until that happens, the genuine accepted nonfixture Source/Work/binding count remains **zero** and Issue #23's research hold remains in force. The synthetic unit tests validate machinery only, not copyrighted work custody or content.

## Validation

```sh
python3 -m unittest discover -s tests -p 'test_propose_librarian_source_work.py' -v
python3 -m unittest discover -s tests -p 'test_source_custody_receipt.py' -v
python3 tools/validate.py
```
