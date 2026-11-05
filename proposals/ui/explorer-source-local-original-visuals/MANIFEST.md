# Explorer original source-local imagery — HELD review proposal

**Role:** CONSOLIDATOR/Explorer presentation. This work is a proposed user-interface projection, not a reconciliation of fictional identities or an admitted source-read. The source baseline is accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`; this UI proposal is stacked on the HELD first-screen LCARS work in DRAFT PR #587. Source-art origins are the separately held art-only DRAFT PR #586 and thematic DRAFT PR #589. No release is claimed by inclusion in this branch.

## What actually changes

Seven **original local SVG graphics** are now wired into the real `explorer/app.js` browse/card renderer and physically included inside the static Pages artifact allowlist. The source-local row identity, medium, exact title and exact source locator must **all** match a code-owned pin. No title-string lookup can hand another row an image. The accepted directory still contains 1,214 historical rows, plus a separately gated 2-row Picard supplement; these images do not increase that denominator.

**HELD successor:** four originally generic metadata/title-card graphics below have been replaced byte-for-byte, at their existing allowlisted Explorer filenames, by independently audited source-description motifs from HELD DRAFT #593, source commit `0a14381a01b77966f6c2d1be9b805aaf025d58b4`. The manifest and generator in that source proposal pin original geometry, literal short evidence cues and their first-party sections, not any complete film, book, publisher HTML, or publisher image. The Explorer release validator separately pins their exact SVG SHA-256. All four source-local row IDs, titles, media, source locator URLs and `UNVERIFIED_METADATA` status stay unchanged.

| Source-local record | Presentation | Source lineage |
| --- | --- | --- |
| `lead:0000` *The Doomsday Machine* | Original illustrated mechanical threat / fragmented planet | Wikidata discovery ID, plus separate Paramount+ publisher description motif |
| `lead:0001` *The Trouble with Tribbles* | Original illustrated furry-circle overflow | Wikidata discovery ID, plus separate Paramount+ publisher description motif |
| `lead:0050` *Crossfire* | Original metadata index illustration | Wikidata discovery only |
| `film:film-2009` *Star Trek (2009)* | Original intersecting legacy/future paths, abstract star chart | StarTrek.com film *Synopsis*; HELD #593 `legacy-future.svg` |
| `film:film-nemesis` *Star Trek Nemesis* | Original mirrored forms and destructive center bar | StarTrek.com film *Synopsis*; HELD #593 `mirror-weapon.svg` |
| `literature:prh-autobiography-janeway` | Original memoir pages and dotted travel path | Penguin Random House distributor *Book Description*; HELD #593 `delta-journal.svg` |
| `literature:proposed-lit-snw-ring-of-fire` | Original abstract accretion torus and generic research station | Simon & Schuster publisher *About the Book*; HELD #593 `accretion-station.svg` |

The two original TOS thematic SVGs come from full *publisher descriptions*, **not** watched episode video. The *Crossfire* graphic is a metadata-only index card. The four newly upgraded film/book graphics are broad abstract interpretations of **short first-party publisher/distributor descriptions**; none is based on watching/reading the actual work. They are not depicted scenes, poster art, jacket art, official Starfleet trademarks, or real people. The browser labels and caption distinguish each kind. Copyrighted film frames, jacket pixels and publicity stills are **not** imported. No third-party request is initiated to show these same-origin CSS backgrounds. Source credit links remain explicit and separate. The publisher-listed ISBN for either literary page **does not reconcile any private ebook edition** or upgrade the accepted `edition_identifier=null`.

## Regression and publication barriers

- 81+ Explorer JavaScript behavior tests, including a real duplicate-title collision case: two *Doomsday Machine* and two *Tribbles* observations display separately; only the exact Wikidata source-local ID receives the thematic illustration.
- `tools/validate_original_source_art.py` SHA-256-pins exact seven files, checks SVG-only safe grammar, checks directory/film row metadata, rejects symlinks and unexpected files. It now additionally pins the **entire effective** `explorer/app.js` and `explorer/app.css` plus matching HTML cache hashes; editing either UI file requires explicit checksum review. Checking only the first Map and first CSS selector proved insufficient under independent hostile review.
- Ten original-art boundary unit tests include source misbinding, SVG-byte mutation, extra files, offsite CSS substitution, and three independently supplied P1 crosswires: late same-origin CSS override, post-Map JavaScript mutation, and early resolver return assigning one illustration to every record. These three initially **passed** the old gate (red tests) and now **fail closed** (green tests).
- `.github/workflows/static.yml` refuses uncommitted or modified source-art bytes. There is **no** broad `explorer/*` asset glob or extension-wide allowance. The existing `licensed-artwork/` physical release prohibition remains intact.
- On 320px screens, illustrated cards become single-column to avoid unreadable copy. This is a CSS/DOM regression claim only; no actual mobile browser screenshot has been obtained.
- The original SVGs contain tiny internal source-status text when scaled down to thumbnail size; those bytes are **not** used as the accessible label. Large external card titles, explicit original-art captions and meaningful `aria-label` text remain. A larger independent visual inspection/preview is still required before release.
- External jacket images continue to require their separate explicit visitor opt-in. Original art never toggles or bypasses external image permission.

> **Hostile challenge:** an attractive scene illustration may be mistaken for an official still or verified episode plot. This proposal marks source-description interpretation and source-local metadata plainly; neither the graphics nor their juxtaposition with publisher data establishes close-reading, authoritative global Work identity, or canonical continuity facts. A separate independent visual and semantic review is still required before any protected Pages publication.

**State:** HELD DRAFT-proposal code only. No merge, release, deployment, rights grant, or accepted research coverage effect.
