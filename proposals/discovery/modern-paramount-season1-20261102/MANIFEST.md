# Modern Paramount+ episode discovery — first season

- Batch: `modern-paramount-season1-20261102`
- State: **PROPOSED, UNVERIFIED_METADATA**; proposal-only publisher title and source-local episode-slot observations.
- Observation date: 2026-11-02 (web-retrieved first-party Paramount+ U.S. episode guides).
- Scope: **45 publisher-listed season-one slots** across Discovery (15), Picard (10), Lower Decks (10), and Strange New Worlds (10). These are four separate publisher guide views, **not an exhaustive franchise or series denominator**.
- Independence group: `publisher:paramountplus.com` for all four; four pages from one publisher are **not four independent confirming sources**.
- Receipt: exactly hashed locally transcribed CSV rows and `*-observation.json` metadata, with deterministic `tools/normalize_episode_roster.py` output in each `<series>/bundle.json`.
- Not included: Prodigy (publisher guide unavailable here) and Starfleet Academy (an overlapping S1 publisher candidate batch already exists at `proposals/librarian/sfa-paramount-roster-20261102/`); absence from this tranche does not imply exclusion from the universe.
- Effects on governed records, admitted Briefings, source bindings, canonical Works, coverage and denominator: **NONE**.

## Publisher locator ledger

| Local mission | Source locator | Source-local display slots |
|---|---|---:|
| `dis` | https://www.paramountplus.com/shows/star-trek-discovery/episodes/1/ | 15 |
| `pic` | https://www.paramountplus.com/shows/star-trek-picard/episodes/1/ | 10 |
| `ld` | https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/1/ | 10 |
| `snw` | https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/1/ | 10 |

The four URLs were opened during the 2026-11-02 observation. Title and displayed source-local season/episode numbers were manually transcribed; episode prose, transcripts and source media were not copied. The original HTML response bytes are **not archived or authenticated** by these local SHA receipts. A checksum of our CSV certifies only the CSV's local bytes, not the publisher's changing page. First-party publisher metadata may be mistaken or subsequently edited, and is not independently reviewed audiovisual research.

## Admission and identity boundaries

1. Maintain Work/episode identity independently from publisher-local slots; do not infer global identifiers from exact titles, sequence positions or season numbers.
2. Do not treat observed S1 entries as proof that every real episode of each series was captured. Further season research remains outstanding.
3. Do not fold the 45 rows into the 218 external episode leads and advertise a 263-episode universe total: those are separate source-local reference populations that may overlap.
4. Before semantic research, obtain lawful primary-source access and create separate authenticated Source, Evidence and Assertion records with independently governed admission and coverage review.
