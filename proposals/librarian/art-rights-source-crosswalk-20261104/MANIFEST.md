# Artwork provenance × reference identity × rights state (HELD crosswalk)

Authoritative `main` verified as `3028765359001b90bc3e6b5c1835ee283b326e91`. This is a **12-row bounded crosswalk sample**, not a new global artwork census, Source→Work admission, book-title resolution or release decision. Exact SHA-256 input pins are in `records.json`; all accepted source records are read at those bytes by the validator.

| Class | Sample count | Correct meaning | False promotion prohibited |
|---|---:|---|---|
| Accepted repo-original category SVG | 3 | Original category backgrounds (episode, film, literature), already in accepted Explorer | Not an episode frame, movie poster, jacket, or source-bound canonical Work |
| Accepted documentary photo, release HELD | 1 | *Beyond* premiere event photo, licensed CC BY 2.0, original/rendition hash receipts | Not cleared to publish or treat as still; accepted decision says `public_image_display_authorized:false` |
| Accepted Open Library jacket API preview | 2 | Existing visitor-opt-in external cover previews with linked ISBN/edition metadata | Underlying jacket copyright unresolved; API display ≠ rehost license or exact OPF binding |
| Accepted OPF→publisher metadata, NO image | 3 | Publisher ISBN metadata: one agreement, one format discrepancy, one title discrepancy | `work_identity:NOT_RECONCILED`, `private_edition_equivalence:UNVERIFIED`; not cover custody or literary close-read admission |
| Local unaccepted documentary photo proposals | 3 | Discovery and Nemesis original-byte SHA-256 privately observed, Picard TIFF HEAD/API metadata only | Local commits are unmerged; license grants photographer rights only, third-party/personality/design/trademark gates held |

The complete accepted `explorer/search-catalog.json` has 1,214 **source-local, non-admitted, `UNVERIFIED_METADATA`** candidates. Per-record graphic labels must follow their exact row identity, not assume canonical Work identity. `tools/build_explorer_abstract_art.py` and `explorer/app.js` already provide safe original category artwork and source-relative title/context labels. A richer reference-specific generator is a separate Consolidator/Designer implementation; this Librarian crosswalk exposes why a generic art availability boolean would be dishonest.

## File-level source reality

1. **Original repo SVG:** exact bytes can be deterministically rebuilt from accepted renderer. The repository's source-available license covers original repo-owned material, not external franchise designs or any film/episode footage.
2. **Licensed third-party photo:** a Commons/photographer CC statement is distinct from original image-byte identity, which in turn is distinct from a public-rights decision. *Beyond* has accepted SHA receipts but a held review; *Discovery*/*Nemesis* have independent private SHA-256 observations only in **unaccepted local commits** `36b8661`/`736024a`, while *Picard* local `f5541e5` has only API + HTTP HEAD size/MIME and an uncomputed original SHA-256.
3. **Jacket preview:** accepted Open Library opt-in catalog source/cover IDs are edition-level discovery and preview links with unresolved underlying copyright. They must not be joined to OPF private-book edition IDs by similar title or URL suffix.
4. **OPF publisher crosscheck:** 39 accepted public-source crosscheck rows include 30 ISBN agreements and 9 held discrepancies; no accepted global Work or private edition equivalence. The three exemplar rows here include both success and falsifiers, not a collapsed pass count.

> Hostile falsifier: artwork `PROVENANCE_REVIEWED_ARTWORK` is a catalog metadata label, not a court-cleared license for a copyrighted book jacket. A release implementation that treats this as `APPROVED_REHOST` would be unsound.

> Hostile falsifier: a locally calculated photo SHA-256 proves byte identity, not the actor's consent, a studio costume-design license, a mark grant, or official franchise endorsement.

> Hostile falsifier: an OPF ISBN matching a publisher ISBN may be a source-local identifier agreement but still have edition/format variants and no corresponding cover. Never silently map `opf-local:*` to `directory:literature:*` or global Work IDs.

## Next review boundaries

- **Librarian:** maintain source/edition/artwork rights classes, exact file receipts and held discrepancies; no canvas/editor UI edits.
- **Consolidator:** only after accepted reconciliation and deterministic row identity, bind provenance to renderable artwork records without hiding uncertainty. Maintain separate accepted/proposed and visual/semantic denominators.
- **Explorer Designer/Auditor:** ensure the UI displays source-local tags and relevant copyright/attribution warnings, with no implicit image loads or mistaken official-art labeling. Test generated motifs visually and accessibly before release.
- **Owner/reviewer:** exact public image decision for each third-party asset, including derivative/change notices, personality rights, studio marks/costumes, credit and no endorsement.

Tests: `python3 -m unittest tests.test_art_rights_source_crosswalk tests.test_explorer_abstract_art tests.test_artwork_release_contract -q`. No external image bytes are added, and none of the 12 rows becomes newly publishable by this report.
