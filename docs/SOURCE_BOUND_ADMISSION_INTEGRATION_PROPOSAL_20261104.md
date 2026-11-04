# SOURCE_BOUND admission controls: integration candidate (HELD)

This is an **unmerged engineering proposal**, not a Source/Work admission, an
accepted reconciliation, an episode close read, a publication license, or a
coverage event. The accepted baseline inspected for this candidate is
`main@3028765359001b90bc3e6b5c1835ee283b326e91`.

## Exact predecessor proposals

| Input | Tested draft head | Independent review | Scope |
| --- | --- | --- | --- |
| [#574](https://github.com/thebrazenbeard/trek-data-core/pull/574) | `58929211178abeb0cbc76c71685a79a5374cab53` | [#5777242362](https://github.com/thebrazenbeard/trek-data-core/pull/574) | Read-only preflight pins exact authoritative registry and coverage file bytes and rejects input drift. |
| [#577](https://github.com/thebrazenbeard/trek-data-core/pull/577) | `c189261e6f8cdc06f96691e622e917a12f23b01c` | [#5777297050](https://github.com/thebrazenbeard/trek-data-core/pull/577) | Canonical `enforce_origins=True` SOURCE_BOUND needs content-addressed Librarian custody claim and separately recorded Auditor review. |

The code files from these proposals do not overlap. This branch layers their
verified changes together and tests the new shared boundary: the preflight
governed-input byte fingerprint includes the canonical gate's
`coverage/bound-claims/*.json` **and** `coverage/bound-reviews/*.json` files,
including raw LF/CRLF differences. A claim or review created or changed during
preflight cannot remain invisible to the before/after state comparison.

## Intended sequence, not automatic acceptance

1. A Librarian separately establishes defensible source/edition identity,
   rights for private research, complete authorized bytes and their replayable
   private custody receipt. This step is **not** fulfilled by an archive
   filename, public synopsis, declared SHA, or converter crosswalk alone.
2. Accepted governed nonfixture Work, Source, `EVIDENCE_BEARING` BYTE_HASH
   binding, and a separate accepted DISCOVERED predecessor must exist.
3. The preflight verifies the exact local source bytes against its custody
   request and receipt and pins the governed context. `READY_FOR_EVENT_PROPOSAL_REVIEW_REQUIRED`
   means **review the event proposal**; it never grants admission.
4. The proposed SOURCE_BOUND event references a content-addressed custody
   *claim* plus separate recorded Auditor *review* bound to the Work, Source,
   binding, byte digest, event scope and a private custody-receipt digest.
   The canonical validator checks record shape, context and byte-addressing.
5. A genuinely independent reviewer must still authenticate the private
   source/receipt, reviewer authority, edition/work interpretation and rights.
   Neither a role string nor a self-re-signed in-repo review proves those facts.
   Only an explicitly accepted and validated event can advance coverage.

> **Hostile boundary:** A malicious actor able to rewrite and re-sign all
> in-repository Source/Work/binding records and claim/review hashes can make a
> synthetically consistent ledger. Issue [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23)
> requires evidence and independent review external to that self-consistency.
> This integration cannot turn `UNKNOWN` rights or identity into fact.

## Verification

Run from the integration branch:

```sh
python -B -m unittest discover -s tests -p 'test_source_bound_readiness.py' -q
python -B -m unittest discover -s tools -p 'test_coverage_ledger.py' -q
python -B -m unittest discover -s tools -p 'test_*.py' -q
python -B -m unittest discover -s tests -p 'test_*.py' -q
python -B tools/validate.py
python -B tools/coverage_ledger.py validate
python -B tools/check_source_bound_readiness.py --work-id missing --source-id missing --binding-id missing
```

Expected on currently accepted `main`: the preflight remains `BLOCKED`,
governed admission remains empty and the denominator remains unresolved.
All accepted corpus effects, public Explorer and release effects are **NONE**.

This candidate does not supersede either predecessor's independent review.
It needs its own integrated-tree review before an authorized acceptance or
release decision.
