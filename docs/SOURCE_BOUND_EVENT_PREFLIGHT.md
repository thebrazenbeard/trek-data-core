# First nonfixture `SOURCE_BOUND` event: read-only preflight

`tools/check_source_bound_readiness.py` checks whether **one exact** episode Work,
Source and Librarian Source↔Work binding have the minimum mechanical context
for a **proposed** `SOURCE_BOUND` coverage event. It creates no registry,
coverage, projection or Explorer records.

The existing [first-episode pilot](FIRST_NONFIXTURE_EPISODE_PILOT.md) checks
the longer Evidence→Assertion→coverage→projection chain. This tool isolates
the earliest binding/event boundary and adds an exact local-byte replay gate.

## Invocation

```sh
python3 tools/check_source_bound_readiness.py \
  --work-id <accepted-episode-id> \
  --source-id <accepted-source-id> \
  --binding-id <accepted-binding-id> \
  --request /private/authorized-request.json \
  --receipt /private/receipt.json \
  --source-file /private/authorized-source-copy.bin \
  --require-ready
```

Before this call, use `tools/source_custody_receipt.py capture` and `verify`
as described in [Source custody receipts](SOURCE_CUSTODY_RECEIPTS.md).
Keep the full source outside the public repository. The command rehashes
the supplied regular file and checks that the receipt exactly replays from
the declared request and actual bytes. The private file paths and its contents
are **never printed or copied** into the report.

The tool checks accepted, nonfixture authoritative Work, Source and binding
records; an eligible `EVIDENCE_BEARING` binding with exact `BYTE_HASH` basis,
matching IDs and source provenance labels; an active accepted `DISCOVERED`
predecessor for the Work; no existing accepted `SOURCE_BOUND` event for the
same Work/Source/binding; plus both global admission and coverage validators.
The accepted `DISCOVERED` event IDs are reported for review, not automatically
chosen as a new event's prerequisites.

The output is `BLOCKED` with specific blocker codes or
`READY_FOR_EVENT_PROPOSAL_REVIEW_REQUIRED`. The latter establishes *only*
mechanical consistency with the supplied private byte copy and accepted
metadata. It does not establish independent source authenticity, rights,
actual episode identity, independent human observation, or acceptance of an
event. A second qualified reviewer must check those separately. A matching
declared checksum alone is insufficient.

Default invocation exits `0` for a valid diagnostic even when `BLOCKED`.
`--require-ready` exits `2` for blocked input; invalid governed corpus input
exits `3`. Only a properly reviewed, explicitly accepted event physically
recorded under `coverage/` can change the coverage ledger. This preflight
cannot advance the denominator, close-read status or any mission briefing.

On accepted `main` as of 2026-11-03, the nonfixture Work/Source/binding
rosters and coverage event ledger are empty; there is no ready instance.

Synthetic tests only:

```sh
python3 -m unittest discover -s tests -p 'test_source_bound_readiness.py' -v
```
