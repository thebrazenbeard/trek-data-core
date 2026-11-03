# TOS Season 2: first five first-party publisher-guide cards

**Lane:** TOS · **Batch:** `TOS.PPLUS.S2.FIRST5.20261103` · **Status:** `PROPOSAL_ONLY`

**Accepted baseline:** `f4ea65391cf1543a55bf19dfcf3ed776dd80ab04` (2026-11-03)
**Effects:** `NONE` on accepted Source/Work binding, coverage, denominator, reconciliation, Explorer release, or artwork publication.

**Director queue hold:** [Issue #23](https://github.com/thebrazenbeard/trek-data-core/issues/23) is OPEN. This already-started publisher-guide extraction is preserved under its bounded in-progress checkpoint allowance, not an authorization for a successor tranche. The five records remain HELD, and the TOS lane stops after this preservation proposal until the issue's accepted admission prerequisites are met.

## Retrieved and actually processed

On 2026-11-03, I retrieved the [Paramount+ *Star Trek* Season 2 episode guide](https://www.paramountplus.com/shows/star_trek/episodes/2/) as an HTTP 200 HTML response and read the first five episode cards. The private raw response was 308,788 bytes (SHA-256 `617ea64c3408fc228151ef839c71ce5b9043614dc5e97b64b83fb8e0adffe1a6`), with 26 episode cards in that site rendering. Its full source bytes are **not** committed; the SHA is a reference to this specific retrieved response, not a promise that a future dynamic page will have identical bytes.

The source is a **publisher listing**, not the episode video, a transcript, a shooting script or a copy of any complete fictional work. I read five complete *listing cards*, not five complete episodes. No audiovisual viewing, transcript reading or accepted close-read coverage occurred.

| Publisher Season 2 slot | Title | Primary page card / private HTML title line | Publisher video locator |
| --- | --- | ---: | --- |
| 1 | Amok Time | 1 / 1467 | `/shows/video/1226104276/` |
| 2 | Who Mourns for Adonais? | 2 / 1495 | `/shows/video/1226100875/` |
| 3 | The Changeling | 3 / 1523 | `/shows/video/1226123965/` |
| 4 | Mirror, Mirror | 4 / 1551 | `/shows/video/1226170276/` |
| 5 | The Apple | 5 / 1579 | `/shows/video/1226152002/` |

Five original, source-relative paraphrases and five local mentions are in `records.json`. Publisher descriptions are preserved as length + SHA-256 fingerprints, not copied into the public data. Five source-relative evidence records support five `PUBLISHER_DESCRIBES / UNVERIFIED_FICTIONAL_CONTENT` assertions; none is projected as objective fictional-world truth.

The five title/slot pairs also match the accepted [legacy S2 Paramount candidate bundle](../../../discovery/legacy-paramount-season2-20261102/tos/bundle.json) (SHA-256 `b5cfe891190b5054b748c520d7640d520717b414a410e8d5cc923488ea61f466`). That legacy bundle derives from the publisher ecosystem and is **not** independent corroboration. Source-local Work IDs remain unmerged.

**Known cross-proposal overlap (HELD):** The Librarian's open [PR #380](https://github.com/thebrazenbeard/trek-data-core/pull/380) is *not* limited to Season 1; its exact head `ecf6cbd8230ea30da0050292679c1aa3bef5dd29` includes `lead:0012`, TOS S2E4 *Mirror, Mirror*. It records the same Paramount+ Season 2 guide URL and publisher-card description SHA-256 (`765ab4c99e2c07e908c30f2bb40b3c584f816db8cabefeaf73f33a2f41be858c`) as this batch's fourth card. The two packets have different transient complete-HTML hashes, but those receipts do **not** constitute independent corroboration. They are overlapping descriptions within one corporate publisher family. Count neither as an extra episode, Source↔Work admission, or independent witness; preserve the overlap for later Librarian/Consolidator reconciliation. The *Cage/Menagerie* derivative [PR #335](https://github.com/thebrazenbeard/trek-data-core/pull/335) remains outside this five-slot selection.

Five thumbnail URLs appeared in the publisher HTML. Their URLs are **HELD metadata only**, without downloads, copying, or publication-rights claims. The displayed local timestamp fields are faithfully recorded, but interpretation as historical broadcast dates remains unverified.

## Validation and replay

```bash
python3 proposals/research/tos/s2-publisher-first5-20261103/validate.py
python3 proposals/research/tos/s2-publisher-first5-20261103/validate.py --source-html /path/to/private/pinned-publisher-response.html
python3 -m unittest discover -s tests -p 'test_tos_s2_publisher_first5.py' -v
python3 -m unittest discover -s tests -q
```

The validator pins the full reviewed JSON packet's canonical SHA-256, all five Work/local-entity/evidence/assertion relations, the accepted discovery crosswalk, and the non-promotion fields. With the private raw HTML it additionally verifies exact source hash, card order, titles, season/episode, time, video, description fingerprints and thumbnail locators. A hash-only public record cannot independently reproduce source extraction after ephemeral private bytes expire; that custody limitation is explicit.

## Exact next frontier — blocked by #23 until its resume conditions are met

1. Obtain authorized complete episode media, script or full transcript for a named TOS variant, retain a separate source/edition receipt, and actually read it before asserting `CLOSE_READ`.
2. Distinguish Remastered streaming guide versions, original broadcast cuts, draft scripts and their work/edition relationships under explicit later reconciliation.
3. Have an independent auditor review this proposal's five card extractions and retained custody limitations before any acceptance or Explorer publication.

None of these steps is authorized merely by filing this preservation packet. The next TOS worker must recheck accepted `main`, [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23), Source/Work custody, governed coverage, and pending overlapping proposals before starting new research.

This batch does **not** assert five more episodes researched to semantic depth, no new canon, and no increase to accepted episode coverage.
