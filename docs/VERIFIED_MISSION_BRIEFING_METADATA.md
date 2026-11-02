# Independent episode-identity metadata review (proposal-only)

**Mission** means a television series; **Mission Briefing** means an episode.
The repository previously had two public categories: unverified research leads
and source-bound, assertion-evidenced Briefings. These must remain separate.
An accurate publisher episode roster can be reviewed as **metadata** without
implying that an episode has been watched or continuity researched.

The new publisher_episode_metadata_review contract is an offline intermediate
handoff for that independent metadata review. The word *review* describes
what a human attests, not what a validator establishes on its own.
**It is not a new acceptance route yet.** No review changes the authoritative
registry, public Explorer, canonical projection or coverage ledger.

## Strict tier separation

| Tier | Evidence required | Safe claim |
| --- | --- | --- |
| Research lead | Candidate title, ID or publisher heading | Discovery only, no accepted identity |
| Proposed publisher metadata review | Original candidate bytes, publisher snapshot hash, checked slots, distinct collector/reviewer declarations | Human comparison reported, still **not admitted** |
| Authority-admitted episode identity (future) | Authenticated independent review and metadata acceptance receipt | Episode identity indexed, **not watched** |
| Source-bound continuity research | Exact inspected Source bytes, Source-to-Work binding, scoped Evidence, accepted assertions and reviewed projection | Only the continuity and coverage states supported by evidence |

Metadata identity must never imply SOURCE_BOUND, CLOSE_READ, AUDITED, a
complete season denominator or resolved continuity. Different publication,
production and air orders need explicit reconciliation rather than an
assumed global episode ordinal.

## Offline two-step handoff

1. Prepare an unadmitted publisher candidate proposal using
   tools/normalize_episode_roster.py or the existing proposal format. Keep
   the original CSV, source observation and publisher snapshot in private
   rights-authorized custody.
2. A separately identified reviewer compares the proposed season, episode
   number and title to the exact publisher snapshot. The reviewer produces
   JSON conforming to schema/verified-episode-roster.schema.json.
   The reviewer ID must differ from the collector ID. Disputed slots stay
   out of the reviewed subset and need separate reconciliation.

Example shape (the episode is fictional; hash placeholders intentionally
cannot pass the validator until replaced by genuine byte digests):

    {
      "record_type": "publisher_episode_metadata_review",
      "schema_version": "1.0.0",
      "candidate_batch_id": "example-batch-s01",
      "candidate_sha256": "sha256:REPLACE_WITH_EXACT_PROPOSAL_BYTES_HASH",
      "mission_id": "tos",
      "publisher_snapshot": {
        "locator": "https://example.org/episodes",
        "independence_group": "publisher:example",
        "retrieved_on": "2026-11-02",
        "content_sha256": "sha256:REPLACE_WITH_PRIVATE_PAGE_BYTES_HASH",
        "representation": "PUBLISHER_PAGE_BYTES",
        "publication": "BYTES_EXCLUDED"
      },
      "review": {
        "collector_id": "collector-example",
        "reviewer_id": "reviewer-example",
        "reviewed_on": "2026-11-02",
        "attestation": "IDENTITY_FIELDS_MATCH_SNAPSHOT",
        "scope": "PUBLISHER_TITLE_SEASON_EPISODE_ONLY",
        "checked_episode_slots": [
          {"season": 1, "episode_number": 1, "title": "Example Episode"}
        ]
      },
      "metadata_status": "REVIEW_PROPOSAL_ONLY",
      "canonical_work_effect": "NONE",
      "source_binding_effect": "NONE",
      "continuity_effect": "NONE",
      "coverage_effect": "NONE",
      "denominator_effect": "NONE",
      "publication_effect": "NONE"
    }

Run from the repository root with actual private file paths:

    python3 tools/validate_verified_episode_roster.py \
      --candidate proposals/librarian/example/bundle.json \
      --review /path/to/private/metadata-review.json \
      --snapshot /path/to/private/publisher-page.html

The optional --snapshot checks a SHA-256 digest of exact page bytes in a
bounded regular local file, without uploading, executing or copying those
bytes. Without it the command prints DECLARED_REVIEW_RECEIPT_ONLY_NOT_ADMITTED;
with matching bytes it prints SNAPSHOT_BYTES_MATCH_RECEIPT_NOT_ADMITTED.
Both have accepted_effect: NONE. A digest match does **not** prove that the
page supports the episode titles, the reviewer exists, or the publisher is
authoritative. These need a genuine external review.

The validator checks a known Mission, exact candidate bundle hash, publisher
locator and independence group, distinct collector/reviewer declarations,
date ordering, sorted and exact candidate slot matches, safe input files,
and fixed no-effect fields. Duplicate JSON keys are rejected. No scripts,
subtitles, book text, scene transcriptions or restricted source bytes should
be committed.

## Required future integration gates

1. An accountable Librarian checks publisher identity, lawful snapshot
   provenance, source content versus proposed slots, ordering conventions,
   multipart identities and conflicting references.
2. Project authority separately approves a versioned episode-metadata
   roster/receipt. A JSON reviewer string or green test cannot approve it.
3. A distinct, deterministic public metadata index is built from the
   approved receipt. The UI labels such identities **metadata-verified,
   not content-reviewed**, distinct from unverified leads and continuity
   projections.
4. Negative tests prove a metadata record cannot generate canonical
   assertions, Source-to-Work bindings, coverage milestones or admitted
   continuity. The guarded Pages artifact scope must be updated and reviewed
   before any public release.

No actual verified episode, accepted Work or public index change is produced
by this patch.

    python3 -m unittest discover -s tests -p 'test_verified_episode_roster.py' -v
