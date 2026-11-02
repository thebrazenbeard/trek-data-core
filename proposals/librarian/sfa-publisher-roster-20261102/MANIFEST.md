# Starfleet Academy — publisher episode-slot metadata proposal

Batch `SFA-PUBLISHER-ROSTER-20261102-001` · Observed **2026-11-02 UTC**.

This is a bounded, manually checked observation of the official
[Paramount+ season-one episode guide](https://www.paramountplus.com/shows/star-trek-starfleet-academy/episodes/1/),
cross-checked against [Paramount Press Express episode listings](https://www.paramountpressexpress.com/paramount-plus/shows/star-trek-starfleet-academy/episodes/).
The two pages are **one publisher independence group**, not independent
audiovisual witnesses. They display ten season-one title/ordinal pairs,
represented as metadata-only **candidates** in [`bundle.json`](bundle.json).
No episode synopsis, scripted dialogue, image, video, caption, or body response
is copied here. No streaming playback or episode-content inspection occurred.

The Press Express page additionally labels an entry `Season 2 - Early Release`
with `S2 Ep200` and `Early Release Images` with episode `Multiple`. These
are **excluded** from the ten observed season-one episode slots. The page
also uses a release-code numbering convention (`101`–`110`), whereas the
Paramount+ season guide explicitly displays `S1 E1`–`S1 E10`. The bundle
records the latter *displayed* slots, not a guessed universe-wide denominator.

The historical discovery request used Wikidata `Q134592591` and returned zero
rows. The [item page at that URL](https://www.wikidata.org/wiki/Q134592591)
now explicitly displays `Q117350388` and states it was redirected from the
former ID. That redirection is an **observed crosswalk hint**, not a proof that
a future SPARQL query must return ten rows, nor an independent episode-source
attestation. It does not modify the older immutable response receipt.

## Admission ceiling and unresolved work

- `listed_slot_count=10` means **ten observed web-page slots**, not a verified
  complete season, complete series, or all-episodes denominator. The pages
  may change, and future seasons or releases need separate observations.
- Every entry remains `CANDIDATE` with null canonical Work and binding IDs.
  `accepted_work_effect`, `accepted_source_binding_effect`, `coverage_effect`
  and `denominator_effect` all equal `NONE`.
- The observation date has day precision only. No preserved publisher response
  bytes, content hash, page revision, authenticated publisher signature or
  independent playback evidence exists. The URLs are locators, not receipts
  for video content or proof of redistribution rights.
- A Librarian must reconcile Work identity, season/release variants and an
  accepted, rights-valid Source representation before promoting anything.
  Coverage remains `DENOMINATOR_UNRESOLVED` until separately reviewed.

Offline structural verification, without network or writes:

```sh
python3 tools/validate_publisher_episode_roster.py \
  --input proposals/librarian/sfa-publisher-roster-20261102/bundle.json
python3 -m unittest discover -s tests -p 'test_publisher_episode_roster.py' -v
```

The validator checks candidate status, exact fields, Mission membership,
positive unique episode slots, a bounded observation and the explicit
no-admission/unknown-completeness contract. It **does not authenticate** a
remote publisher site. The observation should be repeated independently
before any identity decision.
