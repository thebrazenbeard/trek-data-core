# HELD — film-specific Creative Commons premiere photography for Explorer

Date: 2026-11-04 · Librarian independent artwork lane · local proposal only.
Accepted GitHub `main` `3028765359001b90bc3e6b5c1835ee283b326e91` was reverified
with a literal remote query. [Draft PR #513](https://github.com/thebrazenbeard/trek-data-core/pull/513)
is **open, not accepted**; it contains other held photo and image URL leads,
but confers no art release authority. The existing accepted
`explorer/beyond-premiere-photo.json` already records a distinct *Star Trek
Beyond* Japan-premiere photograph; it is not duplicated here.

## Directly observed file-level evidence

These are **real-world documentary event photographs associated with a specific film**,
not publicity stills, theatrical posters, screenshots, or screenshots of an
episode. The accepted source-local film record is
`film:film-into-darkness`, with first-party source locator
`https://www.startrek.com/movies/star-trek-into-darkness`.
`explorer/search-catalog.json` is pinned at SHA-256
`a197138a9069fb67ac5307055588659dd74a9fb4e1caa9d5295d24bc0687d4e5`.

| Candidate | Observed source | File author, license, original | Primary license review | Distinct display context |
|---|---|---|---|---|
| Ensemble photograph | [Commons original file record](https://commons.wikimedia.org/wiki/File:Star_Trek_Into_Darkness_Cast_2013.jpg) and [immutable revision](https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Into_Darkness_Cast_2013.jpg&oldid=1158784125) | Eva Rinaldi; **CC BY-SA 2.0**; [Flickr original 8674151469](https://www.flickr.com/photos/58820009@N05/8674151469); file 1000×612 | Commons reports FlickreviewR confirmed original Flickr license on 2013-04-23 | Karl Urban, Zachary Quinto, J. J. Abrams, Chris Pine at Sydney premiere |
| Two-cast photograph | [Commons original file record](https://commons.wikimedia.org/wiki/File:Chris_Pine,_Karl_Urban_(8674159443).jpg) and [immutable revision](https://commons.wikimedia.org/w/index.php?title=File:Chris_Pine,_Karl_Urban_(8674159443).jpg&oldid=1165852288) | Eva Rinaldi; **CC BY-SA 2.0**; [Flickr original 8674159443](https://www.flickr.com/photos/58820009@N05/8674159443); file 1000×1821 | Commons reports imported-file review confirmed original Flickr license on 2013-08-08 | Chris Pine and Karl Urban at Sydney premiere |

The Commons descriptions identify the Sydney event as 2013-04-23. Both photos
share one author and Flickr upstream lineage. Two files are **not two
independent source authorities** for the film's plot or production.

The actual [Creative Commons Attribution–ShareAlike 2.0 license](https://creativecommons.org/licenses/by-sa/2.0/)
permits photography reuse when its terms are met. Obligations include supplied
file title, author credit, source link, precise license link, a change
indication when applicable, no suggestion of endorsement, and ShareAlike terms
for adaptations. The [Commons external-reuse guidance](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia)
expressly requires file-specific review; a CC license on the photograph does
not by itself cover publicity/privacy rights, proprietary backdrops or logos.

## Honest rights/semantics split

| Evidence | Established | Not established |
|---|---|---|
| Photographer's source | Commons per-file credited Eva Rinaldi and linked reviewed Flickr license | Independent direct communication with photographer |
| Photo copyright | File page explicitly asserts CC BY-SA 2.0 with Flickr review | Authorized Explorer's exact resized image bytes, attribution placement, or adaptation compliance |
| Film relevance | Event is expressly described as the *Into Darkness* premiere | Photograph is from the film, a studio-approved official still, or a theatrical poster |
| User/rights | Film row ID and first-party film source locator match accepted search catalog | Depicted-person, third-party logo/backdrop, event/venue or other rights clearance |
| Explorer release | A possible **`OTHER` documentary photo** after human/independent rights and exact-byte review | Current display permission, accepted art-sidecar mapping or release-ready asset |

> **HOSTILE FALSIFIER:** A source-specific photograph should not be mislabeled
> as an episode still or film poster just because it makes a more exciting card.
> CC BY-SA's permissions cover the photographer's image copyright and impose
> obligations; they do not turn the studio's branded backdrop into CC art or
> make an actor's likeness an endorsement. A Commons preview and its metadata
> are not an accepted local media binary receipt.

No pixels, image blobs or private source files were downloaded, included,
modified or published. The two records have `public_release_eligible=false`,
null image/thumbnail SHA-256, null exact release binding, null independent
reviewers, and `public_explorer_effect=NONE`. This is a source-led **legal
route to potential film-specific photography**, not the film's cover image.

## Exact next admission frontier

1. A human/independent rights and visual reviewer checks the *actual pixels*
   of a chosen original or size derivative, its Commons fixed revision,
   attribution requirements and depicted people/marks/venue. Reject or revise
   if a third-party rights question cannot be cleared.
2. If permitted, produce exact image SHA-256, chosen derivative dimensions,
   immutable source/revision receipt, visible attribution with license and
   change notice, and non-endorsement notice. For a modified thumbnail,
   ensure ShareAlike obligations and rights to crop/alter are documented.
3. Submit a separately reviewed exact film-row and rights-tuple release receipt
   to `registry/artwork-rights-receipts/`, then qualify under the code-owned
   `tools/validate_artwork_release.py` and an opt-in tested Explorer UI.
   The source-local film metadata remains `UNVERIFIED_METADATA`; artwork
   does not advance `SOURCE_BOUND`, `CLOSE_READ` or semantic coverage.

Code: `tools/validate_into_darkness_commons_leads.py --check` and
`tests/test_into_darkness_commons_leads.py`. These perform deterministic
local-only validation; they do not themselves grant legal clearance.
