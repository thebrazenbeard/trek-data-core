# Mission Briefing evidence review packets

This is a **human handoff** for researching one real episode (a **Mission Briefing**)
within a series (a **Mission**). It is a small, offline step toward the first
nonfixture episode admission described in
[`FIRST_NONFIXTURE_EPISODE_PILOT.md`](FIRST_NONFIXTURE_EPISODE_PILOT.md).
It is **not** an episode ingester, an audiovisual viewer, a rights assessor,
or an accepted record generator. The current public corpus does **not** gain
episode facts merely because this tool produces valid JSON.

## Researcher workflow

1. Pick a Mission ID from `registry/mission_catalog.json`. Establish the
   Mission Briefing's season, episode slot, title and publisher roster URL.
   Treat the roster as an **identity lead only**, not as audiovisual evidence.
2. Create a JSON input template somewhere **outside the public checkout**:

   ```sh
   python3 tools/prepare_episode_review_packet.py --template tng
   ```

   Save and edit the printed JSON in a private working directory. The initial
   template is intentionally `PUBLISHER_METADATA` / `NOT_INSPECTED` and has
   no observations or assertions; that is the only honest starting state.
3. If and only if you actually inspect a lawfully accessed episode
   representation, change `source.kind` to `EPISODE_CONTENT`,
   `source.inspection` to `RESEARCHER_REPORTED`, identify a specific stable
   version and public *locator*, record your access basis and contextual
   rights note, inspection date, and the actual SHA-256 of the exact inspected
   representation. An unrelated web-page hash, guessed hash, or checksum of
   an episode title **must not** substitute for the representation digest.
   If you cannot obtain a real byte digest, remain in metadata-only status;
   this pilot's accepted `SOURCE_BOUND` gate requires a genuine exact hash.
4. Write only short **original research notes**, one bounded episode time
   span per observation (`cue_start_seconds`, `cue_end_seconds`), and a small
   set of proposed factual assertions referring to `evidence_id` values in
   that same packet. Keep dialogue, scene descriptions, plot transcription,
   scripts, subtitles, encoded media, page scans, access keys, license IDs,
   and full prose **out of the input and out of Git**. A claim such as
   “a fictional instrument was calibrated” is synthetic testing language,
   not evidence that a real Mission Briefing was observed.
5. Run the offline packet check and hand the emitted packet to the
   appropriate independent reviewers **outside the accepted registry**:

   ```sh
   python3 tools/prepare_episode_review_packet.py --input /path/to/private/review-input.json
   ```

   Output is deterministic JSON on stdout. The CLI creates no files,
   fetches no web pages, reads no episode media and changes no canonical
   record. Save its output privately if the rights/access notes may identify
   a subscriber or restricted representation. Inputs are bounded to 64 KiB,
   must be regular non-symlink JSON files and cannot contain duplicate keys.
   Platforms without the required non-symlink/nonblocking open flags fail
   closed; overly nested JSON is also rejected. Invalid inputs exit `1`
   with a `REVIEW_PACKET_REJECTED` message.

The schema is [`schema/episode-review-input.schema.json`](../schema/episode-review-input.schema.json).
The CLI additionally checks known Missions, HTTPS locator hygiene, valid
dates, unique proposal IDs, 10-minute maximum citation spans, local evidence
references and the content-source prerequisites. The packet's `packet_sha256`
is a **reproducibility checksum of the packet JSON** (excluding that field),
not a signature or proof that someone watched the episode.

## Distinct review decisions

| Handoff stage | What this packet can present | What must happen separately |
| --- | --- | --- |
| Mission → episode Work | Dated publisher identity and episode slot | **Librarian** resolves authoritative Work identity and series parent, then admits the independent Work records. |
| Episode Source ↔ Work | Public locator, version, stated rights basis, reported digest; `PROPOSED` binding | **Rights/source reviewer + Librarian** lawfully and independently inspect the exact bytes, validate digest/scope and Source identity, then decide if `EVIDENCE_BEARING` is admissible. Metadata-only links never count as viewing. |
| Evidence | Original notes pinned to a source-specific, bounded timecode | **Researcher/reviewer** confirms every cited moment against the admitted source and exact Work; no transcript or episode body is imported. |
| Assertion | Local assertion-to-evidence citations | **Reconciler/Auditor** checks predicate eligibility, epistemic interpretation, conflicts and independent verification before any accepted Assertion. |
| Coverage | A suggested `SOURCE_BOUND` state for independent consideration only if an inspection was reported | **Coverage authority** separately constructs and accepts an exact Source/Work/binding coverage event. This tool emits no ledger event and changes no denominator. |
| Projection | A review checklist, with no computed projection hash | **Projection maintainer/project authority** regenerates canonical output, reviews and approves its exact hash, then rebuilds the Explorer. Pages release remains a separate protected manual action. |

Everything in the generated packet has `admission: NONE`,
`accepted_source_work_binding_effect: NONE`, `coverage_effect: NONE`,
`denominator_effect: NONE`, or `projection_effect: NONE` where applicable.
The `PENDING_INDEPENDENT_REVIEW` gate statuses are tasks, **not approvals**.
`fixture_only: true` instead blocks the review gates and cannot be promoted.

For authoritative record contracts and approval gates see
[`registry/README.md`](../registry/README.md),
[`COVERAGE_DENOMINATOR_GATE.md`](COVERAGE_DENOMINATOR_GATE.md) and
[`CANONICAL_PROJECTION_INTEGRATION.md`](CANONICAL_PROJECTION_INTEGRATION.md).

## Synthetic reproducibility exercise

```sh
python3 tools/prepare_episode_review_packet.py --input tests/fixtures/episode_review_synthetic.json
python3 -m unittest discover -s tests -p 'test_episode_review_packet.py' -v
python3 tools/check_episode_pilot_readiness.py
```

The synthetic fixture describes a **nonexistent training exercise**, uses
`example.org` and a dummy digest, and was not obtained from any Star Trek
episode. It demonstrates citation linking and no-op semantics without
contributing any real episode evidence. The last command checks the accepted
corpus independently; processing a packet does not alter its result.
