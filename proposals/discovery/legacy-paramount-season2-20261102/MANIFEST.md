# Paramount+ legacy Season 2 episode-slot discovery — unadmitted

**Proposal status:** `DISCOVERY_ONLY` · **Observed:** 2026-11-02 · **Lineage:**
`publisher:paramount` · **Accepted research effect:** `NONE`

This is an official publisher *listing snapshot*, not an inventory of verified
canonical episodes. An anonymous public HTML response was retrieved for each
Season 2 listing, parsed for visible episode-card **titles and source-local
season/episode ordinals**, and reduced to five normalized CSV observation files.
The matching `index.json` preserves the SHA-256 and byte size of each retrieved
HTML body, plus the SHA-256 of the derived CSV. The raw HTML, images, summaries,
scripts, dialogue, transcripts and audiovisual media **are not committed**.
The body hash is an observation fingerprint, **not** a publisher signature,
immutable page revision or independent source authentication.

| Listing | Publisher-listed rows | Official observed source |
| --- | ---: | --- |
| *The Original Series* S2 | 26 | [Paramount+](https://www.paramountplus.com/shows/star_trek/episodes/2/) |
| *The Next Generation* S2 | 22 | [Paramount+](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/2/) |
| *Deep Space Nine* S2 | 26 | [Paramount+](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/2/) |
| *Voyager* S2 | 26 | [Paramount+](https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/) |
| *Enterprise* S2 | 26 | [Paramount+](https://www.paramountplus.com/shows/enterprise/episodes/2/) |
| **Total publisher listing rows** | **126** | **Five pages, one publisher family** |

Every batch is `CANDIDATE_METADATA_ONLY`, `roster_completeness: UNRESOLVED`,
with `accepted_work_effect`, `accepted_source_binding_effect`, `coverage_effect`
and `denominator_effect` all `NONE`. Every row has null canonical Work and
source-binding identifiers. These 126 source-local listing rows are **not 126
admitted Briefings, distinct global Works, narrative analyses or measured
franchise coverage**. They might overlap previously observed Wikidata or
Paramount metadata leads.

## Reproducibility and safety

- `python3 tools/build_legacy_s2_discovery.py --check` deterministically
  revalidates all five CSV observation hashes, source URL identities, canonical
  candidate-only bundle bytes, and the repository's existing publisher-roster
  schema. It performs no network access.
- `python3 -m unittest discover -s tests -p 'test_legacy_paramount_s2.py'`
  covers exact counts, non-admission, forged metadata, stale output, symlinks,
  duplicate ordinals, and malformed titles.
- To repeat an observation, obtain current **public** official HTML into a
  temporary directory, with exactly `tos-s2.html`, `tng-s2.html`,
  `ds9-s2.html`, `voy-s2.html`, and `ent-s2.html`, then run the builder's
  `--ingest-dir` mode. **Do not commit or redistribute the HTML bodies**.
- The generator reads only bounded input files and constructs deterministic
  discovery proposals. A new observation may legitimately change counts or
  hashes; each such difference requires independent comparison rather than
  silent replacement of the accepted proposal batch.

## Deliberate unresolved questions

1. The official streaming guide's episode ordinals are *platform slots*, not
   an automatically reconciled release order or unique canonical story unit.
   Earlier TNG/DS9/Voyager combined premieres demonstrate the hazard. This
   tranche is limited to Season 2; it does not fill missing earlier slots.
2. Five platform listing pages are **one publisher family**, not five
   independent witnesses. Their displayed card count is not a full-series or
   full-franchise denominator.
3. Episode-level source access, rights to retain copyrighted content, close
   reading, entity claims and continuity assertions remain unverified.
4. Existing discovery proposals must be reconciled by explicit identities;
   matching title strings are insufficient to merge records automatically.

Next step: independent audit of the raw-page observation method and selected
source-local slots before any medium-wide discovery projection incorporates
these candidates. No accepted main records, Briefings or continuity facts are
modified here.
