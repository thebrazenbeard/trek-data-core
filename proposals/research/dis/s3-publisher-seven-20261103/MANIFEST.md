# DIS S3 · Seven publisher-guide source observations (B009)

Status: **research proposal only**. No accepted Source→Work binding, globally reconciled identity, close-read coverage, user-facing synopsis, Explorer admission, or artwork publication.

Source: Paramount+ primary Season 3 episode guide, `https://www.paramountplus.com/shows/star-trek-discovery/episodes/3/`.
Read 2026-11-03; HTTP 200; 2,775 HTML lines; 282,393 bytes on two reads.
The two whole-response SHA-256 receipts differed:

- `e57dd125d6952b28534d7c2e4f9a3d80bb8a982783c1724f420bef604abde2fe`
- `0dee11548fbd9a3703c30d57f52b4c5beccdc1f2e221823d353795b0e05c97a6`

The HTML is dynamic. These hashes prove two observed responses, **not** a stable immutable Paramount edition. The first-party card title, E-number, `time datetime`, video ID, summary, and thumbnail URL were inspected in full for seven cards (HTML lines 1612–1803). No video playback, captions, screenplay, or transcript was accessed.

| Source-local lead | Publisher slot | Exact publisher title | Local scope |
| --- | --- | --- | --- |
| `lead:0108` | DIS S3E04 | Forget Me Not | Trill/Adira; publisher description |
| `lead:0109` | DIS S3E05 | Die Trying | Federation/Starfleet; publisher description |
| `lead:0110` | DIS S3E06 | Scavengers | Book rescue; publisher description |
| `lead:0111` | DIS S3E07 | Unification III | Burn data debate; publisher description |
| `lead:0112` | DIS S3E08 | The Sanctuary | Osyraa and Book's planet; publisher description |
| `lead:0113` | DIS S3E09 | Terra Firma, Part 1 | Georgiou's condition; publisher description |
| `lead:0114` | DIS S3E10 | Terra Firma, Part 2 | Georgiou's changed outlook; publisher description |

These leads were already discovered from Wikidata and Paramount guide proposals. This batch adds **first-party source-relative fields**, not seven novel canonical Works. The existing Wikidata display uses Roman `Part I/II`; Paramount uses numeric `Part 1/2`. A separate Wikidata `Terra Firma` unsplit item also exists. They are not silently merged or assumed equivalent.

All seven paraphrases are newly authored descriptions of what Paramount says. Thirteen mentions are **local** only; their labels do not cause global identity joins. All seven image URLs are held official-card locators without image bytes, hotlinks, rights clearance, or Explorer effect. One publisher guide constitutes one source lineage, not seven independent corroborations.

Deterministic validation: `python3 proposals/research/dis/s3-publisher-seven-20261103/validate.py`; 16 adversarial tests in `tests/test_dis_s3_publisher_seven.py`, including a regression that forbids rewriting Paramount's rescue description as an unsupported defensive action. The raw `records.json` SHA-256 is pinned in the validator; changes require explicit new review. No source copy or copyrighted promotional prose is committed.

Next frontier: independent source/semantic audit, exact GitHub CI, then parent-coordinated conditional integration; separately obtain complete primary AV/caption sources before any close-read or continuity assertions.
