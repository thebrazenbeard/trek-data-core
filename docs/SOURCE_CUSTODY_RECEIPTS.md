# Offline, independently reproducible Source byte custody receipts

`tools/source_custody_receipt.py` hashes an **actually readable local file** and emits a proposal-only manifest containing its exact SHA-256, byte length, declared source identity, edition/version, locator, and provenance family. It provides a byte-level input to the Librarian review process; it does **not** certify that a title matches the bytes, grant rights, create a canonical Source/Work/binding, read a narrative for research, or advance coverage.

The CLI does not contact external services, upload/copy file contents, or print local paths. Run it only on source copies you may lawfully inspect and keep the input source file outside public Git. The resulting receipt has no source bytes, subscriber credentials or local paths, but a digest can still identify a known work; review any receipt before publication.

## Private request and capture

In a private directory, create a bounded `request.json` with source-relative metadata. This is a **synthetic example**, not a Star Trek observation:

```json
{
  "record_type": "source_custody_request",
  "schema_version": "1.0.0",
  "receipt_id": "synthetic-source-receipt-001",
  "source_candidate_id": "synthetic-source-001",
  "source_kind": "AUDIOVISUAL_EPISODE",
  "locator_kind": "PRIVATE_OPAQUE",
  "source_locator": "private:synthetic-source-001",
  "source_version": "synthetic-master-v1",
  "edition_identity": "synthetic fixture, not an actual Trek episode",
  "provenance_family": "SYNTHETIC_FIXTURE",
  "independence_group": "SYNTHETIC_FIXTURE",
  "rights_basis_reported": "OWNED_COPY",
  "observed_on": "2026-11-03",
  "declared_sha256": null
}
```

For a public page or official source locator, use `locator_kind=PUBLIC_HTTPS` with a **clean public HTTPS URL** without credentials, query parameters, fragments or ports. For a file with no shareable public locator, use `locator_kind=PRIVATE_OPAQUE` and a stable `private:<opaque-id>` rather than exposing a local filename, signed URL, account path, or subscriber token. The private locator is an inventory key, *not* proof of identity.

All free-text edition/version/provenance labels forbid `/` and `\` path separators to prevent private absolute file paths from being copied into a supposedly path-free public receipt. Describe versions using stable names or ISO dates with hyphens; retain original private file paths only in private custody records outside this tool's output. Request and receipt JSON paths also reject symlinked ancestors.

The version/edition/rights/access fields are operator declarations and need later independent review. A null `declared_sha256` permits first capture; if an independent digest is already recorded, supply its lowercase 64-hex value to catch mismatched source files.

```sh
python3 tools/source_custody_receipt.py capture \
  --request /private/request.json \
  --source-file /private/synthetic-source.bin > /private/receipt.json

python3 tools/source_custody_receipt.py verify \
  --request /private/request.json \
  --source-file /private/synthetic-source.bin \
  --receipt /private/receipt.json
```

The second command independently recalculates all fields and the receipt checksum from the supplied metadata and **current exact file bytes**; any byte/edition/locator/metadata change rejects the receipt. Retain source bytes under authorized private custody. A distinct reviewer should independently obtain the same source representation and compare its SHA and variant/edition identity; two passes over the same file are not independent Source witnesses.

## Receipt interpretation and limits

| Receipt field | Meaning | Does not establish |
| --- | --- | --- |
| `content_sha256`, `size_bytes` | Exact bytes streamed from one local regular file and observed byte length | Rights, provenance, or publisher authenticity |
| `source_locator`, `source_version`, `edition_identity` | Declared address and representation/version for later audit | Correct Work identity without actual source inspection |
| `provenance_family`, `independence_group` | Custodian-supplied lineage labels | Independent corroboration; derived copies cannot manufacture new witnesses |
| `rights_basis_reported` | Operator's access explanation | A license grant or legal opinion |
| `receipt_sha256` | Deterministic checksum of canonical receipt JSON without that field | Signature, timestamp attestation, or third-party approval |
| `acceptance_effect`, `coverage_effect`, `source_work_binding_effect` | Always `NONE` | `SOURCE_BOUND` or content close-read |

The CLI requires regular, non-symlink files, refuses devices/pipes and symlinked source paths, checks metadata shape and JSON duplicate keys, hashes in bounded chunks, and rejects source changes detectable across the read. It currently requires host support for `O_NOFOLLOW` and `O_NONBLOCK` and fails closed otherwise. It is not a cryptographic snapshot of a simultaneously writable file: freeze or copy a stable authorized edition under private custody before hashing. File cap: 128 GiB; private request/receipt cap: 64 KiB each.

A **hardlink alias is permitted**: it is another filename for the same file bytes/inode and produces the same deterministic receipt given the same declared source metadata. The tool does not expose or authenticate the local inode in its public receipt, and a hardlink never constitutes an independent second Source or independent corroboration. Distinguishing an original artifact from its hardlinks/copies remains a Librarian provenance review obligation.

Do **not** commit media, ebook contents, full transcripts, subtitles, covers, signed streaming URLs or subscription identifiers alongside a receipt. This tool deliberately neither creates an `EVIDENCE_BEARING` binding nor constructs the accepted evidence ledger. After independent byte identity and rights review, use existing Librarian governance, research-lane source reads, and Auditor/reconciliation gates. The existing `prepare_episode_review_packet.py` still accepts researcher-reported digests; a matching custody receipt strengthens its provenance handoff but does not promote the packet.

## Synthetic checks

```sh
python3 -m unittest discover -s tests -p 'test_source_custody_receipt.py' -v
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/validate.py
```
