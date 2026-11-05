# Four source-local thematic visual proposals — HELD

This is a **source-evidence-bound original art proposal**, separate from the
accepted Explorer, third-party jacket rights crosswalk, and owner-private OPF
books. It is not publication authority. The accepted-main anchor was
`3028765359001b90bc3e6b5c1835ee283b326e91`; the immediate base is held
thematic-episode proposal `8d86f578a5c7b92e5158805b385beddb35a315c0`.

## Source → original motif mapping

| Source-local row | First-party source/section | Original interpretation | Limits |
| --- | --- | --- | --- |
| `film:film-2009` | [StarTrek.com / Star Trek (2009) / Synopsis](https://www.startrek.com/movies/star-trek-2009): father's legacy; adversary arriving from the future | Two intersecting blue/orange trajectories over an abstract star chart. No actors, vessels, uniforms, logos, or stills. | Synopsis-only; no film viewing. |
| `film:film-nemesis` | [StarTrek.com / Star Trek Nemesis / Synopsis](https://www.startrek.com/movies/star-trek-nemesis): Picard clone; powerful destructive weapon | Mirrored blue/pink polygons with a central destructive bar. Not a depiction of a scene, person, or canon weapon. | Synopsis-only; no film viewing. |
| `literature:prh-autobiography-janeway` | [Penguin Random House / *The Autobiography of Kathryn Janeway* / Book Description](https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/): first-person life story; Delta Quadrant journey | Open generic memoir pages overlaid by a meandering dotted journey. Not a reproduction of the jacket or page text. | Distributor description only; no book text read. |
| `literature:proposed-lit-snw-ring-of-fire` | [Simon & Schuster / *Star Trek: Strange New Worlds: Ring of Fire* / About the Book](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898): black-hole accretion disk; elevated classified research facility | Abstract accretion torus and tiny generic geometric station. No commissioned cover, official station design, spacecraft likeness, or copyrighted pixels. | Publisher description only; no novel text read. |

The exact, short source cues, their independently pinned UTF-8 SHA-256
digests, source-local IDs, motif-element mappings, source pages, accepted
metadata status, and generated SVG hashes are in [`manifest.json`](manifest.json).
The `source_cue_sha256` digests attest the recorded strings, **not** the
complete live publisher pages. No HTML/body hash or original media custody
is claimed. The generator verifies all four source rows against the immutable
six-row source-local input contract and independent first-party title/URL pins.
Reviewer-approved digests also pin every complete source-kind/section/cue/
motif tuple, the selected publisher format/ISBN listings, and each motif's
deterministic drawing body. A change to evidence wording, a valid-but-wrong
source-to-scene mapping, extra rights fields, or an unnoticed art replacement
fails closed. These code-local pins are integrity tripwires, **not independent
source custody or proof of review by themselves**.

## Literary edition *page listing* pins, not edition reconciliation

The PRH page currently selects paperback ISBN **9781789095333** (Titan Books,
2021-11-16, 224 pages). The Simon & Schuster page selects hardcover ISBN
**9781668095898** (Pocket Books/Star Trek, 2025-10-07, 336 pages). These are
first-party **page listing locators**, not identity or textual-equivalence
proof for a privately held ebook, a different ISBN, another format, or an
accepted Work. The accepted source-local rows still say
`edition_identifier=null`, `identity_scope=SOURCE_LOCAL`, and
`verification_status=UNVERIFIED_METADATA`.

## Material exclusions and verification

- **0** copyrighted film frames, promotional stills, jackets, portraits,
  logos, ship designs, book passages, audio, or video reused.
- **0** accepted Work admissions, coverage advances, source images, edition
  equivalence claims, or public release effects.
- **0** full films viewed, books read, or archived raw publisher HTML files.
- Each SVG is original deterministic geometry and visibly marked as
  `NOT OFFICIAL ART · NO FILM/BOOK CLOSE READ · SOURCE-LOCAL`.
- The source snippets justify broad thematic metaphors, **not** a claim that
  the drawn composition occurs on screen or on a page.
- Tests mutate source URLs, titles, cue text, edition/rights/coverage claims,
  and renderer inputs; changes fail closed. Generation is byte deterministic.

Regenerate with `python3 tools/build_thematic_film_literature_art.py` and
validate with `python3 tools/build_thematic_film_literature_art.py --check` and
`python3 -m unittest discover -s tests -p test_thematic_film_literature_art.py -v`.

**Status:** HELD. Requires separate Librarian provenance/rights review,
Explorer accessibility/design review, and authorized release process before
any integration. Does not change the accepted Explorer or Supabase.
