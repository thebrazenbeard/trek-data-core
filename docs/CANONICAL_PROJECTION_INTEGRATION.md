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
