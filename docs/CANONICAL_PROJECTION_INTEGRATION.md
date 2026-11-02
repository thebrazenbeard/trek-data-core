# Canonical projection integration — source-only review

This is a **clean mainline integration proposal** for the canonical data
compiler, validation and derived query consumers. It intentionally carries
neither a historical `.vscode` task nor the earlier development branch's
unreviewed research corpus. It is stacked on the safer coverage-ledger draft.

## Authority boundaries

- The Librarian Source/Work/binding contract on main determines authoritative
  identities. Accepted non-fixture Source and Work objects belong under
  `registry/authoritative/`; proposal records remain proposals.
- An Evidence record requires a corresponding accepted **evidence-bearing**
  Source↔Work binding. A metadata-only or crosswalk mapping cannot establish
  Evidence. The proposal compiler embeds the eligible binding in its
  provenance output and hashes it into the logical input identity.
- Proposed or rejected superseding assertions never silently deactivate an
  accepted predecessor. Reconciliation and active accepted status must be
  explicit, traceable and regression-tested.
- TNG historical research and Wikidata episode metadata remain discovery
  candidates, not accepted Works or projected claims.

## Verification on the integration tree

Run from the repository root with Python 3.12:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py' -q
python3 -B -m unittest discover -s tests -p 'test_*.py' -q
python3 -B tools/validate.py
python3 -B tools/coverage_ledger.py validate
python3 -B tools/coverage_ledger.py report
```

The local integration snapshot passed **150 tool tests and 3 current source
startup-safety tests**. Repository validation found **zero governed records**;
coverage correctly reported `DENOMINATOR_UNRESOLVED`. Two canonical empty
projections built with identical arguments were byte-identical with projection
hash `sha256:a3214eb7a9f67c79f46548d0ef19371134ce5fb6b0dfdecb27e34b0726212f4b`.
The semantic diff returned `changes=0`, and SQLite, PostgreSQL and
graph/search projection builders completed successfully.

These checks verify contract mechanics on synthetic fixtures and the empty
repository only. They do **not** establish an admitted Star Trek corpus,
source licensing, independent research signoff, or live service performance.

## Remaining acceptance tasks

1. Independently review exact Git tree hashes and the combined Librarian
   contract versus the proposal Source/Work schemas. The mainline schema is
   authoritative for registry entries.
2. Complete the coverage contract: derived discovery/source-binding states,
   owner event attestation, full denominator/native-unit rules and accepted
   head verification.
3. Admit a small, rights-valid Source/Work/Evidence pilot with an accepted
   binding, then verify the full projection and query build against **nonempty**
   output, including contested and unresolved assertions.
4. Approve the projection hash independently before enabling nonempty facts
   in the public Explorer. No hash has yet been added to the Explorer's
   reviewed-hash allowlist.

Keep this pull request in draft until its coverage dependency and these
acceptance checks are resolved. Do not bulk-merge historical branch heads.
