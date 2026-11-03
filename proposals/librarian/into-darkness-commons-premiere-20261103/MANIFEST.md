# Film-specific documentary photo with an explicit photographer license

**Librarian proposal, independent display review pending.** This is an actual
candidate to replace unavailable proprietary poster hotlinks, not a claim of
public image release. Acquired against accepted main
`a0494934782963b9a7f344cf50ed83191e08bf95` (2026-11-03).

## Exact source-relative identity

The existing 14-film `explorer/film-catalog.json` has an
`UNVERIFIED_METADATA` first-party row:

- Source-local film ID: `film-into-darkness`; prospective artwork sidecar
  row ID: `film:film-into-darkness`.
- Title: *Star Trek Into Darkness*.
- First-party film locator: [StarTrek.com movie page](https://www.startrek.com/movies/star-trek-into-darkness).
- Source catalog raw SHA-256:
  `6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de`.

The proposed image is **not a film frame, studio poster or fictional scene**.
It is a separate **editorial/documentary photograph** of performers and
director at the film's Sydney premiere on 23 April 2013, according to
the Commons file description: Karl Urban, Zachary Quinto, J. J. Abrams,
Chris Pine. Its film-specific event caption supports a narrow relation to
this particular accepted film row, without merging other film identities
or claiming a source text was read.

## Permission evidence — a real photographer grant

The exact [Wikimedia Commons file page](https://commons.wikimedia.org/wiki/File:Star_Trek_Into_Darkness_Cast_2013.jpg)
at [pinned oldid 1158784125](https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Into_Darkness_Cast_2013.jpg&oldid=1158784125)
attributes the photo to **Eva Rinaldi**, original
[Flickr photo 8674151469](https://www.flickr.com/photos/evarinaldiphotography/8674151469/).
Commons records a **FlickreviewR license check dated 23 April 2013** and
labels the *photographer's work* [CC BY-SA 2.0 Generic](https://creativecommons.org/licenses/by-sa/2.0/).
That license provides a conditional copying/display/adaptation route: name
the photographer, link the source and license, identify modifications,
avoid implying endorsement, and license adaptations as required by ShareAlike.

The [Creative Commons 2.0 deed](https://creativecommons.org/licenses/by-sa/2.0/)
explicitly warns that other privacy, publicity and moral rights can remain.
Those and contextual/nonendorsement presentation remain an independent
review step. This grant applies to **the original premiere photograph**,
not Paramount's theatrical key art or embedded film properties; no
Paramount CDN image is proposed for redistribution.

## Actual retrieval and byte receipts

On 2026-11-03, an authorized Lappy Python HTTPS read returned:

| Artifact | Status | Raw bytes | SHA-256 |
| --- | --- | ---: | --- |
| Commons file-description page pinned `oldid=1158784125` | 200 | 145,529 | `6c715ffff293381a1cd2764a838e0463cb1119c6e208a7149944457a70e800f7` |
| Commons original `Star_Trek_Into_Darkness_Cast_2013.jpg` (1,000 × 612 JPEG) | 200 | 438,150 | `fadaaaedf16cc0b5c5924251f2ae1ddb3545a04796ec85fab951c160f9c3a9a6` |

Image bytes were read transiently in memory for hashing but **not saved,
uploaded, committed or served**. These measured SHA-256 values are distinct
from Commons metadata checksums. The Commons page's original Flickr link
was not directly accessible to this public retrieval tool; the FlickreviewR
confirmation is an observed Commons claim, not a newly authenticated direct
Flickr response. An independent reviewer has not yet confirmed the image
pixels visually in this tranche, so release is **HELD** even though the
photographer's CC license is materially stronger than a studio image URL.
The raw Commons response digest is an observation, not an immutable legal
archive or blanket rights attestation.

## Proposed future use, contingent on review

- Label visibly as **film-premiere event photograph**, *never* a film poster
  or still. Exact alt text and creator/source/license links are pinned in
  `records.json`.
- An approved public image could use the original unmodified JPEG plus
  attribution, avoiding unnecessary cropping/transformation; a thumbnail
  crop requires additional ShareAlike/modification handling.
- Check publicity/privacy/personality context and nonendorsement, verify
  pixels, exact file SHA and rights receipt under independent review.
  Only then may a separately reviewed release PR add the asset and
  exact code-owned pin to `explorer/artwork-catalog.json` under the existing
  licensed-artwork gate. This packet itself cannot authorize display.

> **Hostile countercase:** Commons' CC grant verifies the photographer's
> own licensed contribution, not every conceivable right of film subjects
> or the Trek brand. A premiere photo as a film-identification thumbnail
> can be misleading if shown without the *premiere/event* caption.

Validation:

```sh
python3 proposals/librarian/into-darkness-commons-premiere-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/into-darkness-commons-premiere-20261103 -p 'test_validate.py' -v
python3 -O -m unittest discover -s proposals/librarian/into-darkness-commons-premiere-20261103 -p 'test_validate.py' -v
```

**Effects:** no image publish, hotlink, Explorer asset manifest, public
domain claim, Source/Work admission, identity reconciliation or coverage.
