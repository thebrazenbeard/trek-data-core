# Publisher roster comparison: keep source-local order visible

Publisher episode guides can disagree without either being an admissible
canonical episode sequence. This comparison is deliberately a **read-only
research aid**, not a reconciliation decision or Work-identity authority.

## Run on the bounded TOS Season 1 sample

```bash
python3 tools/compare_episode_rosters.py \
  --left proposals/discovery/tos-publisher-s01-b001-20261102/paramountplus.json \
  --right proposals/discovery/tos-publisher-s01-b001-20261102/plutotv.json
python3 -m unittest discover -s tests -p 'test_compare_episode_rosters.py' -v
```

Both input proposals must pass the existing strict publisher-roster validator.
It accepts *source-local* titles and positions, not episode content evidence.
The comparator never fetches network data or changes any accepted registry,
coverage ledger, denominator, or projection. The JSON report is emitted to
stdout; `comparison_sha256` is a reproducibility checksum over the report,
**not** a source-body receipt, signature or independent review.

For the five-slot sample observed on 2026-11-02:

| Title | Paramount+ source-local slot | Pluto TV source-local slot |
| --- | --- | --- |
| The Cage | S1E1 | Not in sampled five |
| The Man Trap | S1E2 | S1E1 |
| Charlie “X” | S1E3 | S1E2 |
| Where No Man Has Gone Before | S1E4 | S1E3 |
| The Naked Time | S1E5 | S1E4 |
| The Enemy Within | Not in sampled five | S1E5 |

The four shared title candidates have conflicting source-local slots. An
omission from either *sample* does not prove absence from a complete roster.
Paramount+ and Pluto TV have the same declared `publisher:paramount`
independence group; their two listings do not amount to two independent
source families. The comparator does not assert that title equality resolves
the underlying audiovisual Work identity.

**Do not conflate three orderings:** original pilot/production chronology,
original broadcast order, and a streaming distributor's current season/episode
slots. For example, *The Cage* is the original Pike-led pilot, while *The Man
Trap* was the first originally broadcast episode; this bounded comparison
does not compute either ordering from the providers' numbered slots. Any
canonical ordering decision needs its own cited authority, order-type label,
and review. Even the two providers' disagreement is not proof that one is
wrong: they may be displaying different scope conventions.

Primary publisher context for those distinctions: [StarTrek.com on the
original Pike pilot](https://www.startrek.com/news/the-cage-rolled-camera-53-years-ago),
[StarTrek.com on the second Kirk pilot](https://www.startrek.com/news/a-look-back-at-treks-second-pilot),
and [StarTrek.com on the first broadcast, *The Man Trap*](https://www.startrek.com/news/catching-up-with-the-salt-vampire-sandra-gimpel).
These retrospective articles are *ordering evidence leads*; they are not
episode-content inspection or independent source hashes.

## Review before any admission

1. Establish each publisher page's actual dated retrieval and revision
   independently. The current metadata-only proposals contain no response
   checksum and no audiovisual-source witness.
2. Determine whether differences reflect pilot-inclusion policy, production
   order, broadcast order, distributor order or page presentation; record
   source-local conventions without overwriting either list.
3. Explicitly resolve Work identities, adaptations, multipart installments
   and alternate cuts with separate Librarian review.
4. Admit evidence only under the registry's distinct Source/Work, provenance,
   assertion and coverage gates. Matching text or slots cannot supply them.

All comparison outputs retain `NONE` for accepted Work, Source binding,
coverage, denominators and independent corroboration effects. Both samples
retain `UNRESOLVED` completeness. Never copy an output into the canonical
episode catalog without the independent decisions above.
