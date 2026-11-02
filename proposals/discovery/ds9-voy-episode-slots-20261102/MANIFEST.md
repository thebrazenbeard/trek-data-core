# First-party episode-slot discovery: DS9, Voyager, The Animated Series

- Batch: `ds9-voy-episode-slots-20261102`
- Research status: **PROPOSED — publisher metadata only**
- Observed: 2026-11-02 UTC
- Family: Paramount+ U.S. streaming episode guides; a single publisher independence group.
- Scope: five first-displayed season-one slots per series (DS9, Voyager, TAS): 15 publisher-listed slots. This is intentionally **not** a full inventory or a denominator.
- Source-bound provenance: `*-observed-slots.csv` are human-curated short title+slot transcriptions from the first-party URLs in `*-observation.json`. Each receipt has a matching SHA-256 over the exact local CSV bytes. The source web pages themselves have no authenticated raw response-byte receipt here.
- Generated proposals: `ds9/bundle.json`, `voy/bundle.json`, `tas/bundle.json` are deterministic outputs of the existing `tools/normalize_episode_roster.py`; governed Work IDs, Source↔Work bindings and accepted facts are all deliberately null.
- Canonical effect: **NONE** on registries, accepted Work IDs, coverage, denominator, source bindings, or public Explorer counts.

## Critical numbering pitfall

The U.S. Paramount+ lists *Deep Space Nine*'s combined *The Emissary* premiere and *Voyager*'s combined *Caretaker* premiere as a single displayed S1E1 item, then jumps to S1E3. The omitted S1E2 is not silently invented, and the two-part narrative must not be merged/partitioned across platforms without explicit identity reconciliation.

## Additional discovery work

- TOS already has an explicit conflicting-source ordinal comparison in `proposals/discovery/official-tos-roster-scope-20261102/`; retain it independently.
- `Star Trek: Short Treks` and `Star Trek: very Short Treks` are separate short-form productions absent from the 12-series directory. A Librarian must first propose Work/container treatment before the series-only public counts can encompass them.
- For complete franchise coverage, source-version custody, independently reconciled season rosters, lawful access to primary media/text, close reading, semantic indexing and audit are still required.

See `RESEARCH_LOG.md` for direct official locators, confirmatory versus exploratory work, and unresolved verification limits.
