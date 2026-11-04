# Canonical projection integration — implemented scaffold

The canonical data compiler, bundle verifier and derived query consumers are
implemented on `main`, independently from the historical development branches.
The implementation carries neither the historical executable `.vscode` task
nor the research branches' unreviewed corpus. **Merged code is not accepted
Star Trek evidence**: the current nonfixture corpus and projection-hash
allowlist are both empty.

## Authority boundaries

- The Librarian Source/Work/binding contract on `main` determines authoritative
  identities. Accepted non-fixture Source and Work objects belong under
  `registry/authoritative/`; proposal records remain proposals.
- An Evidence record requires a corresponding accepted **evidence-bearing**
  Source↔Work binding. A metadata-only or crosswalk mapping cannot establish
  Evidence. The canonical compiler embeds the eligible binding in its
  provenance output and hashes it into the logical input identity.
- Proposed or rejected superseding assertions never silently deactivate an
  accepted predecessor. Reconciliation and active accepted status must be
  explicit, traceable and regression-tested.
- TNG historical research and Wikidata episode metadata remain discovery
  candidates, not accepted Works or projected claims.

## Verification of the implementation

Run from the repository root with Python 3.12:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py' -q
python3 -B -m unittest discover -s tests -p 'test_*.py' -q
python3 -B tools/validate.py
python3 -B tools/coverage_ledger.py validate
python3 -B tools/coverage_ledger.py report
```

The original 2026-11-02 integration snapshot passed **156 tool tests**, including six
adversarial regressions independently demonstrated to fail against the prior
implementation, and source startup-safety checks. The admission
path now rejects forged SHA-256 byte evidence, Source/Work ancestry cycles,
invented derivative independence groups, symlinked governed inputs, and
duplicate JSON object keys. Repository validation found **zero governed records**;
coverage correctly reported `DENOMINATOR_UNRESOLVED`. Two canonical empty
projections built with identical arguments were byte-identical with projection
hash `sha256:a3214eb7a9f67c79f46548d0ef19371134ce5fb6b0dfdecb27e34b0726212f4b`.
The semantic diff returned `changes=0`, and SQLite, PostgreSQL and
graph/search projection builders completed successfully.

Projection bundle verification also rejects symlinked and hardlinked manifest
or JSONL artifacts, even if their current bytes match the declared hashes. The
compiler preflights its output directory, every lexical ancestor (including
components before `..`), and named files before writing, preventing ordinary
builds from silently replacing an aliased file outside the bundle.
This is an output-path consistency safeguard, not a claim of protection against
concurrent hostile filesystem mutation or proof of source authenticity.

The command-line semantic diff (`python3 -B tools/diff_projection.py OLD NEW`)
verifies **both complete canonical bundles before comparing records**. A
missing partition, altered JSONL, or absent manifest now fails before the CLI
can misreport missing data as a `REMOVED_FACT` or missing provenance as a
research change. The lower-level `semantic_diff()` helper intentionally accepts
partial, manifest-free synthetic fixtures for isolated taxonomy tests; it is
**not** the verified entry point for auditable comparisons. This input-integrity
check does not promote the manifest's upstream declarations into attested
research provenance; the receipt limitations below still apply.

## Verification receipts are not upstream provenance certificates

`projection_bundle.verify_projection()` establishes canonical JSONL byte
serialization, declared output hashes/counts, required partitions, and the
aggregate projection hash. It **cannot** independently authenticate the
manifest's `research_head`, `reconciliation_head`, `compiler_commit`,
`schema_version`, `methodology_version`, registry hashes, or `input_hash` from
the bundle alone. For those fields, the returned receipt explicitly says
`UNVERIFIED_DECLARATION` by default. A changed `research_head` can accompany
the old `input_hash` and still pass intrinsic bundle checks; this must never be
interpreted as accepted Git state or source custody.

JSON decoding rejects duplicate keys, nonstandard `NaN`/`Infinity` constants,
and numeric exponents that overflow to non-finite Python floats, even when
declared output hashes are internally consistent. The canonical encoder also
refuses non-finite floats. These are bundle-integrity checks, not evidence of
the authenticity of asserted upstream research or reconciliation heads.

A caller with **independently obtained accepted values** may pass a bounded
`expected_identity` map to `verify_projection(root, expected_identity={...})`.
Only exact-matching supplied fields change to `EXTERNAL_EXPECTATION_MATCHED`;
the rest remain `UNVERIFIED_DECLARATION`. A mismatch fails closed. This is a
comparison to caller-supplied expectations—not an independent source lookup,
review approval, admission event, or verification that the expectations
themselves are authoritative. Derived SQLite, PostgreSQL, and graph/search
receipts inherit these explicit statuses when no expectations are provided.

These checks verify contract mechanics on synthetic fixtures and the empty
repository only. They do **not** establish an admitted Star Trek corpus,
source licensing, independent research signoff, or live service performance.

## Remaining data-admission tasks

1. For each proposed nonfixture batch, independently review exact Git tree
   hashes, Source/Work/binding origins and the authoritative Librarian schema.
2. Apply the existing coverage gates to accepted Work/Source/binding events.
   The resolved accepted-registry roster check does **not** certify a complete
   Mission episode denominator; an independently reviewed complete roster
   mechanism remains necessary.
3. Admit a small, rights-valid Source/Work/Evidence pilot with an accepted
   binding, then verify the full projection and query build against **nonempty**
   output, including contested and unresolved assertions.
4. Approve the projection hash independently before enabling nonempty facts
   in the public Explorer. No hash has yet been added to the Explorer's
   reviewed-hash allowlist.

Review future data admissions and public projections in separate, bounded PRs.
Do not bulk-merge historical branch heads or promote candidate metadata by
reclassifying this implemented infrastructure as an admitted corpus.
