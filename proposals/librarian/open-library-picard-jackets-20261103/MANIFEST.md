# Picard two-jacket source observation — release held

This is a **source-local image candidate** packet, not a public artwork
sidecar, a canonical Work admission, a book close-read or permission to copy
these covers. The accepted Explorer already displays the two publisher
metadata-only leads from `picard-literature-overlay.json`. The public artwork
catalog still displays **four** independently reviewed autobiography jackets.

## Actual source reads, 2026-11-03

- Authoritative publisher metadata: [The Dark Veil](https://www.simonandschuster.com/books/Star-Trek-Picard-The-Dark-Veil/James-Swallow/Star-Trek-Picard/9781982154073), trade paperback ISBN **9781982154073**, James Swallow; [Rogue Elements](https://www.simonandschuster.com/books/Star-Trek-Picard-Rogue-Elements/John-Jackson-Miller/Star-Trek-Picard/9781982175207), trade paperback ISBN **9781982175207**, John Jackson Miller.
- Accepted publisher source record SHA-256: `cdbda4dfa33c795bd51a1ebbfb09e41c7d838b73ce17aa6756428bd6ed8d8da4`.
- Accepted two-row Picard overlay SHA-256: `ab8e5d15f7b33bf1311aec0afb2755322b41bca73978d3c7889f1272dbfe21c8`.
- Canonical Open Library edition JSON responses were independently retrieved by ISBN. Their exact raw SHA-256 digests, cover IDs and observed edition titles appear in [`records.json`](records.json). An Open Library edition title is not a second independent publishing-source corroboration: for **Rogue Elements**, the metadata title is only *Star Trek : Picard*. The exact ISBN and visual front-jacket text disambiguate the candidate.
- Exact Open Library API M and L JPEG bytes were fetched for both candidates, hashed and decoded for dimensions. Both M images were actually visually inspected as **front jackets**, with correct titles/author credits—not generic photos or interior title pages. The binary images were **not** copied into Git.
- Official [Open Library Covers API](https://openlibrary.org/dev/docs/api/covers) documents remote HTML cover display and courtesy attribution links. Its [licensing notice](https://openlibrary.org/developers/licensing) does **not** determine underlying book-jacket copyright. These are opt-in API-preview candidates only.

| Title | ISBN-13 | Open Library ID | Cover ID | Medium JPEG bytes / dimensions |
| --- | --- | --- | --- | --- |
| *The Dark Veil* | 9781982154073 | OL32025277M | 10691195 | 19,466 / 180×271 |
| *Rogue Elements* | 9781982175207 | OL36102337M | 13231543 | 25,665 / 180×280 |

`python3 tools/validate_picard_cover_candidates.py --check` deterministically
rejects substitutions of source-local title/ISBN, publisher or overlay bytes,
artwork ID, preview digest/size/dimensions, provenance URL, coverage status or
release state. The validation uses source snapshots already accepted in Git,
and **does not** independently fetch live Open Library bytes when run in CI.
The reviewer re-fetch recorded above is a separate human-visible source check.

## Release gate

**HELD:** no change to the public Explorer artwork manifest/JS, no new remote
request, no image binaries, no rights promotion and no semantic coverage.
Separate edition/source/large-image/medium-image reviewer receipts and a
backward-compatible dual-catalog UI/validator migration are required before
these two can join the four accepted opt-in previews. The existing v1.2
four-cover fallback is immutable. The live 1,214-row discovery catalog must
remain byte-identical; these two targets are in the separately pinned overlay.

Hostile path to guard against: adding two plausible JPEG IDs to an unreviewed
sidecar must **not** cause the browser to fetch them; a candidate packet or
public JSON cannot be its own permission grant. A provider HTTP 200 is not a
visual check, and the cover copyright remains unresolved even with documented
API display support.
