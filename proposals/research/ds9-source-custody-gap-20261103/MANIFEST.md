# DS9 primary-source custody and fidelity route gate

**Role:** DS9 research worker. **Disposition:** `SOURCE_CUSTODY_GAP_AUDIT_ONLY / NO_NEW_CLOSE_READ / NO_ACCEPTANCE`.

**Accepted base:** `main@afe25c07400ff14534e79b635c7551c5bed18c57`, checked 2026-11-03 UTC. The live [Director hold #23](https://github.com/thebrazenbeard/trek-data-core/issues/23) still bars new episode close-reading without accepted Source↔Work bindings and research-admission infrastructure. Accepted DS9 research has candidate metadata but zero governed Work/coverage events. This tranche does not assert that any episode or original studio script was read.

## What was actually inspected

Five bounded public source/policy pages were read for provenance and access descriptions, not for narrative content:

1. [Writers Guild Foundation Star Trek holdings article](https://www.wgfoundation.org/blog/2026/9/1/read-it-in-the-wgf-library-60-years-of-star-trek): institutional statement that its library holds a few DS9 scripts; exact title/edition membership was not established.
2. [WGF FAQ](https://www.wgfoundation.org/frequently-asked-questions): script reading is onsite only; no remote copies or loans. Institution-owned holdings notice and policy are one independence family.
3. [UC Riverside MS 379 finding aid](https://oac.cdlib.org/findaid/ark:/13030/c84t6grz): collection description identifies preliminary, first and final DS9/Voyager script drafts and production materials; access is for research, while copyright, reproduction, donor and trademark restrictions remain. The collection-level finding aid is not an item-level DS9 script custody receipt.
4. [TrekCore transcription of the DS9 Companion CD-ROM box](https://gaming.trekcore.com/ds9companion/description.html): its description claims a searchable collection of the shooting scripts and trailers. The original packaging/disc was **not** directly inspected, and a marketing count is not an accepted Work denominator.
5. [Noble Knight reseller listing](https://www.nobleknight.com/P/2148381541/Star-Trek---Deep-Space-Nine-Companion): identifies a 1999 Simon & Schuster PC CD-ROM release; it does not attest to the actual script bytes or revision labels. Its repeated product-copy claims are not independent corroboration of the box claim.

The public [Star Trek Minutiae script index](https://www.memoryalpha.st-minutiae.com/resources/scripts/index.html) and [Paramount+ DS9 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/1/) were separately identified as lower-fidelity discovery and licensed-video routes. Their episode/script bodies were **not** read in this tranche. Public scripts on a third-party mirror remain a candidate derivative until original-source chain and edition are established.

## Source route classification

| Route | Potential fidelity | Verified access limit |
| --- | --- | --- |
| Simon & Schuster *DS9 Companion* PC CD-ROM | Publisher-released searchable shooting-script text may enable exact draft inventory | No authenticated media copy, hashes, extraction or per-episode revision verified |
| WGF Library/Archive | Studio/script copies in institutional custody | Only a few DS9 holdings described; onsite only and no remote copies |
| UC Riverside MS 379 | Mixed original production draft types, possible revision evidence | Collection-level finding aid only; item identity and source bytes unknown |
| Third-party script index | Discovery and possible derivative comparison text | No authenticated studio chain, content reading or independent witness status |
| Paramount+ audiovisual | Potential aired-cut performance evidence | Metadata guide only; no actual authorized episode viewing or cut/timecode receipt |

**Edition collision warning:** A literary book titled *Star Trek: Deep Space Nine Companion* and the 1999 PC CD-ROM script library have very similar names. A filename or bibliographic title match does not prove possession of the disc or its scripts. No private archive path, private source bytes or identifying personal metadata is committed here.

## Hostile challenges

> **Packaging is not the source text.** A description of scripts on a CD-ROM cannot establish that our corpus has retrieved, read or authenticated one script; product-copy text repeated by a retailer is not independent corroboration.

> **A shooting script is not the aired episode.** Even an authentic final draft may differ from a particular cut's performance, edits, staging and dialogue. Draft date, revision pages, edition/region and comparison witness must remain explicit.

> **Archive collection is not episode-level custody.** WGF's unspecified few DS9 scripts and UCR's mixed DS9/Voyager collection do not prove one of the five target cards has an accessible verified item.

> **Mirror text is not an authenticated primary master.** A third-party index may point to substantial text, but no chain to the licensed CD or studio draft is presently verified. Do not treat mirrored copies as independent witnesses.

> **Queue hold still applies.** This source-route audit cannot be used to justify fresh narrative close-reading, accepted Source/Work bindings, continuity assertions or an inflated episode denominator.

## Output and exact next frontier

`source_routes.json` records five role-scoped route candidates for the five existing DS9 Season 1 source-local cards. `evidence.json` contains five catalog/policy observations only. `assertions.json` records three unresolved custody/fidelity claims. Their deterministic validator enforces no accepted records, no new primary read, no public script bytes or global identity links.

Checks:

```bash
python3 proposals/research/ds9-source-custody-gap-20261103/validate.py
python3 -m unittest discover -s proposals/research/ds9-source-custody-gap-20261103 -p 'test_*.py'
python3 tools/validate.py
```

**Next permitted action:** Librarian or Auditor checks exact public item-level metadata for the WGF/UCR script holdings or verified private custody of an authorized Simon & Schuster CD-ROM (disc/edition hash, rights status, per-episode draft identity). The DS9 worker must then wait for issue #23's resume gates, accepted Source↔Work bindings and authorized full primary-source access before new close-read research.

No copyrighted script text, images, audio, video, or source binaries are part of this proposal. No merge, Pages publication or episode research admission is implied.
