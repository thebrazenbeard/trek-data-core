# Held publisher-guide notes sidecar (proposal; not a Briefings release)

`tools/build_publisher_guide_notes.py` compiles **existing, held source-local
research from accepted `main`** into `explorer/publisher-guide-notes.json`.
The standalone `explorer/publisher-guide-notes.html` is a separate, searchable
LCARS-style *review surface*, deliberately absent from the canonical search,
episode roster, synopsis catalog and Mission Briefings index.

## Exact source-local contents

| Lane | Observation cards | Existing held paraphrases | Withheld |
|---|---:|---:|---:|
| ENT S1 guide (b001–b003) | 25 | 25 | 0 |
| VOY S4 publisher guide (E10–E14) | 5 | 5 | 0 |
| VOY b006 first-party guide rechecks | 13 | 12 | 1 multipart scope hold |
| PIC S1 publisher guide (first/last five) | 10 | 10 | 0 |
| DIS S1 publisher guide (first five) | 5 | 5 | 0 |
| **Source-local observations** | **58** | **57** | **1** |

These are **observations, not 58 independently accepted episode Works**. The
source family is Paramount/CBS, so repeated publisher-guide references are
not independent corroboration. The VOY `Caretaker` card remains explicitly
`WITHHELD_MULTIPART_IDENTITY`, with **no invented synopsis** or binary Work
identity. The ENT `Vox Solis` publisher variant and VOY apostrophe variants
retain their original identity holds.

The short paraphrases were authored in previously held packets. This compiler
does not read complete episodes/transcripts, rephrase copyrighted page bodies,
derive new story claims, or use a language model. No artwork, clip, thumbnail,
publisher passage or copyrighted transcript is copied. The sidecar's
`MARKETING_DESCRIPTION_PARAPHRASE` designation means only that an earlier
worker summarized publisher *promotion text*, **not** that the fictional event
occurred or the episode was watched.

## Custody and rebuild

Each note identifies its exact accepted proposal `source_packet_path`,
SHA-256 of the packet bytes, local row ID, canonicalized row SHA-256, published
guide URL, source-card locator, and any actually recorded publisher-description
digest or source response receipts. Separate upstream discovery pointers and
digests preserve the original lineage path; for VOY b006 that includes a
Wikidata-derived discovery lead and a distinct official publisher-card check,
**not** independent episode-content corroboration. These provenance classes
are separate:

- `source_packet_sha256` proves the input Git JSON bytes match the compiler's
  reviewed pins, not that the live publisher page is unchanged.
- `publisher_description_sha256` is a previously recorded digest of a
  promotional card blurb where available, not an archived raw page.
- `reported_source_receipts` preserve historical reported HTML response
  checksums; the original HTML is not stored in this repository, and dynamic
  publisher pages may yield differing response digests.

Rebuild and compare deterministically from repository root:

```sh
python3 -B tools/build_publisher_guide_notes.py
python3 -B tools/build_publisher_guide_notes.py --check
python3 -B -m unittest tools.test_publisher_guide_notes -v
node --check explorer/publisher-guide-notes.js
```

On missing or changed input packets, duplicated JSON keys, source-local slot
collisions, absent paraphrases, or admission/status promotions, the compiler
fails closed. The existing original packet validators remain independent
checks on the underlying evidence and publisher-source crosswalks.

## Review and release gate

This PR adds a **proposal branch sidecar and standalone reviewer page**, not
public release approval. `synopsis_publication_approval=NONE`, zero canonical
Work/Briefing additions, and unchanged coverage remain explicit in JSON. No
automatic changes to `explorer/index.html`, `explorer/app.js`,
`explorer/search-catalog.json`, `explorer/synopsis-catalog.json`, or projection
compilers are proposed. That avoids conflict with concurrent LCARS Explorer
work and prevents accidental canonical Briefings inflation.

Before linking the standalone review page from the live Explorer or treating
the paraphrases as approved public synopses, obtain explicit editorial and
publication approval. Until then the current sidecar is an inspectable
candidate artifact only. Future real episode ingestion must use independently
source-bound full primary content and its own accepted evidence/coverage gates.
