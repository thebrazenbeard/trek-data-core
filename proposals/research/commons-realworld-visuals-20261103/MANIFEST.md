# Commons real-world performer/object photographs — research proposal only

Observation: 2026-11-03. Exact accepted-main baseline:
`a0494934782963b9a7f344cf50ed83191e08bf95`.

This source-first tranche records three **photographs** that could eventually
support real-world actor and production-object discovery. They are not episode
stills, film posters, canonical depictions, complete production provenance, or
evidence that an episode/book was read. No global entity ID, Work, episode, or
character identity was assigned. The **separate rights in depicted subjects**
remain unresolved; all three records are held from public display.

| Photo subject (source-described) | Photographer and original source | Commons photo license | Original bytes / SHA-256 |
|---|---|---|---|
| [William Shatner at SDCC 2016](https://commons.wikimedia.org/wiki/File:William_Shatner_(27997025984).jpg) | [Gage Skidmore, Flickr 27997025984](https://www.flickr.com/photos/gageskidmore/27997025984/) | CC BY-SA 2.0; FlickreviewR confirmed 2017-02-13 | 8,733,749; `9785b90c298c029e6db85338cb0c304f88e52f4bb2e6ef9d92f55dba7ab1da5b` |
| [Enterprise-D exhibit miniature at Henry Ford Museum](https://commons.wikimedia.org/wiki/File:USS_Enterprise_star_ship_filming_model_-Star_Trek_-_The_Next_Generation_-_Star_Trek-_Exploring_New_Worlds_Exhibit_at_the_Henry_Ford_Museum,_Dearborn,_Michigan_-_49785050153.jpg) | [Joe Ross, Flickr 49785050153](https://www.flickr.com/photos/joeross/49785050153/) | CC BY-SA 2.0; FlickreviewR 2 confirmed 2023-06-15 | 6,760,907; `e7394586a9c2c4c7aa10e65a42b0dec45daf5b08293726a3b3538db369c0171a` |
| [Original Series tricorder exhibit at Henry Ford Museum](https://commons.wikimedia.org/wiki/File:Original_Series_Tricorder_-_Star_Trek_-_Exploring_New_Worlds_Exhibit_at_the_Henry_Ford_Museum.jpg) | [Joe Ross, Flickr 49785328466](https://www.flickr.com/photos/joeross/49785328466/) | CC BY-SA 2.0; FlickreviewR 2 confirmed 2023-06-15 | 6,379,752; `799a1fe8ad64bd6d5a9a640a8d4241f7a1f2096aff5b4e7937b8578611cab8ae` |

## Evidence classes, not collapsed

- **SOURCE / RETRIEVED:** Wikimedia Commons file pages explicitly state the
  photographer, source Flickr photo, description, license and Flickr license
  review. Wikimedia API `imageinfo` returned JPEG size, dimensions, MIME and
  SHA-1. Exact Commons `oldid` links and GET-response SHA-256 values are in
  `records.json` for source snapshots; transient API responses are hashed too.
- **REAL SYSTEM PROBE:** Lappy directly downloaded each unmodified original
  JPEG **in memory only**, computed SHA-256 and SHA-1, and checked the first
  three JPEG magic bytes. Each independently computed SHA-1 exactly matched
  Commons `imageinfo`. No original images were saved or committed. The
  response SHA-256 is a byte observation, not a copyright grant.
- **SOURCE CLAIM, NOT ADMITTED FACT:** Commons captions identify the attendee,
  displayed miniature and tricorder. Claims that the miniature/tricorder were
  used for screen filming remain uncorroborated source statements; the photos
  are not tied to episodes or accepted identity records.
- **REVIEW:** The **photographs** are listed by Commons under
  [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0). This license
  requires credit, a license link, identification of changes, and share-alike
  on qualifying adaptations. Commons/Flickr metadata share an upstream
  lineage and are **not** two independent production-object confirmations.
- **UNKNOWN / RIGHTS HOLD:** A photographer's CC license does not, on its
  own, clear publicity/personality issues, Star Trek designs/trademarks,
  exhibit terms, or other separately held rights. Independent source-specific
  rights and visual/subject audit is needed before any display approval.

The proposal validator additionally owns immutable SHA-256 pins for the
**complete canonical JSON tuple** of each of these three records. This prevents
a coordinated substitution of plausible-looking subject labels, historical
context, Commons oldid, author/Flickr link and hash-looking strings from
passing merely because their field types still look valid. Those code pins
certify internal immutability of this review packet, **not** independent
photographic authenticity, publicity rights, or a license to underlying IP.

The first candidate's publisher/actor connection must never imply Shatner is
appearing as Captain Kirk in this real-world convention photograph. Similarly,
the two museum images must not be silently used as visual covers for a TNG/TOS
episode or treated as proof of canonical appearance.

## Reproduction and future review gate

1. Re-open exact file-page `oldid` revisions from `records.json`; re-check
   author, Flickr source, declared CC BY-SA 2.0, and license-review history.
2. Query Commons `action=query&prop=imageinfo&iiprop=size|sha1|mime|extmetadata|url`.
   Compare the reported image SHA-1/size and inspected original JPEG SHA-256
   with immutable proposal receipts; flag changed bytes or license claims.
3. Independently inspect each image and verify the **real-world subject**
   description and any museum-object provenance before creating a usable
   source-local subject binding. A factual subject claim is not canon.
4. Obtain separate rights review for intended public context, attribution,
   and possible adaptation. A reviewed release requires a new code-owned
   rights/asset receipt; these proposal hashes cannot authorize themselves.

Run offline structural tests:

```sh
python3 validate.py
python3 -m unittest -q test_validate.py
python3 -O -m unittest -q test_validate.py
```

**Effects:** source/Work/entity admission NONE; coverage NONE; live Explorer
artwork release NONE; public URLs and local binary paths null; no upstream
StarTrek.com image URLs or official-site hotlinks.
