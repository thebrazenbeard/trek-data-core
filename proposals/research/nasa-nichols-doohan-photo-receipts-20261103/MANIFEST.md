# NASA–Star Trek real-world history photos: Nichols and Doohan

**PROPOSAL ONLY — three NASA-hosted archival photo candidates, none released.**
This research packet is a separate successor to [NASA's 1976 Space Shuttle
*Enterprise* rollout proposal](https://github.com/thebrazenbeard/trek-data-core/pull/411).
It documents three different real-world scenes and explicitly declines to
associate any photo with a fictional Trek episode, film, or Work identity.

## First-party source and measured image receipts

The main [NASA historical article](https://www.nasa.gov/history/55-years-ago-star-trek-debuts-begins-an-enduring-relationship-with-nasa/)
(John Uri, Johnson Space Center, September 8, 2021) captions the three scenes.
A [second NASA article](https://www.nasa.gov/history/55-years-ago-star-trek-final-episode-airs-relationship-with-nasa-endures/)
provides another institutional description of Nichols's shuttle recruitment
visit. Both pages belong to the **same NASA provenance family**—not separate
independent corroborating institutions.

The following original NASA-hosted JPEGs were read **in memory only** on
2026-11-03, each returning HTTP 200; no file was stored, altered, or copied into
the public repository. The first-party article captions provide **month/year**
support, not independent confirmation of the exact day encoded in some image
filenames. Preserve date precision accordingly.

| Historical subject | Exact original NASA JPEG | Dimensions and bytes | Measured SHA-256 |
| --- | --- | --- | --- |
| Nichelle Nichols with astronaut Alan L. Bean in JSC's shuttle simulator, **March 1977** | [S77-22306 source photo](https://www.nasa.gov/wp-content/uploads/2021/09/star_trek_first_episode_5_nichols_and_bean_nin_shuttle_simulator_mar_4_1977_s77-22306.jpg) | 985×730; 110,305 bytes | `921f03fb404949c77642f0dd3ce0b194abf59b17c5da0316eb29c055098e021b` |
| Nichols filming a recruiting video at JSC Mission Control, **March 1977** | [S77-22305 source photo](https://www.nasa.gov/wp-content/uploads/2021/09/star_trek_first_episode_6_nichols_in_mcc_filming_promotional_video_s77-22305.jpg) | 985×659; 92,904 bytes | `dfd5d4c861867477f666c96103d41f8bf472e7fdb29b977b337eb35ad1cd8dd1` |
| James Doohan visiting pilot Bruce A. Peterson at NASA Dryden beside the M2-F2, **April 1967** | [Dryden photo](https://www.nasa.gov/wp-content/uploads/2021/09/star_trek_first_episode_9_doohan_and_bruce_peterson_at_dryden_apr_13_1967.jpg) | 512×640; 55,896 bytes | `edca35e4ab946bbb202334ac14cb7aa1a8973487095ffe82f1fc6b1489b5fd20` |

The NASA page's image filenames contain day-of-month text and, for the two
Nichols photos, `S77-22306` / `S77-22305` archival-looking identifiers.
Because a separate NASA image catalog entry was **not** retrieved for those
identifiers, neither the precise day nor the formal archival catalog identity
is considered independently verified in this packet. The original image-page,
second image-history page, and NASA media-rights page live HTML byte counts and
SHA-256 retrieval receipts are in `records.json`. Page bytes can change without
the historical evidence or rights policy itself changing.

For repeatability the packet records its Python `requests` 2.34.2 client and
`Accept-Encoding: gzip, deflate, zstd`: the article and supplementary HTML
were fetched with the default `python-requests/2.34.2` User-Agent, while the
rights-page snapshot used `TrekDataCoreResearch/1.0`; all hashes are over
`response.content` **after HTTP transfer decoding**, without HTML normalization.
An independent comparison of NASA page GETs using a different Python HTTP
client returned equal byte *counts* but different SHA-256 values. Therefore
these hashes identify **one observed HTTP representation**, not a permanent
source version; a future different-byte response must be reviewed, not
automatically declared source tampering or a new grant.

## Rights and subject controls

The [NASA Image and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)
generally permit factual educational/informational reuse of NASA-owned imagery
with NASA credited and no implied agency endorsement. They explicitly exclude
third-party copyrighted material and note that identifiable-person images,
especially in promotional contexts, require additional care. These articles
host the three JPEGs and caption their subjects, but **none of these individual
photos carries an unambiguous separate photographer/license statement in the
article text**. They therefore remain held until an independent image-specific
rights reviewer confirms authorship and the actual editorial use.

> **Rights falsifier:** NASA hosting is not automatically NASA ownership. The
> 2021 page groups the 1967 Doohan picture with a 1991 NASA simulator image
> and a 2004 picture credited to Anne Cusack/Los Angeles Times. That explicit
> third-party credit appears under the grouped caption and most likely applies
> to the rightmost 2004 image; it does **not** prove either the leftmost photo's
> individual authorship or any broader free-use grant.

> **Identity falsifier:** Nichols visiting NASA or Doohan speaking with an
> actual flight-test pilot is a **real-world event**. These photographs are not
> fictional character appearances, source-relative assertions about Star Trek
> canon, episode stills, or proof that a Trek Work was close-read. One NASA
> article's mention of a fictional role does not convert the real person in a
> real historical photo into the character.

Potential credit text, **not cleared for publication**:

- `NASA-hosted historical photograph: Nichelle Nichols with Alan L. Bean in a
  shuttle simulator at Johnson Space Center, March 1977. Individual photograph
  credit pending verification. NASA does not endorse this independent archive.`
- `NASA-hosted historical photograph: Nichelle Nichols filming a NASA astronaut
  recruitment video at Johnson Space Center, March 1977. Individual photograph
  credit pending verification. NASA does not endorse this independent archive.`
- `NASA-hosted historical photograph: James Doohan with test pilot Bruce A.
  Peterson and NASA's M2-F2 at Dryden, April 1967. Individual photograph credit
  pending verification. NASA does not endorse this independent archive.`

## Validation and next gate

This packet contains **3** NASA-hosted JPEG source locators, **3** independently
measured image SHA-256 receipts, **3** explicitly source-limited historical
subjects, and **3** rights HOLDs. It includes **0** binaries, **0** public image
links in the rendered Explorer, **0** fictional Work/episode bindings, **0**
canonical records, **0** close reads, and **0** coverage/admission effects.

```bash
python proposals/research/nasa-nichols-doohan-photo-receipts-20261103/validate.py
python -m unittest discover -s proposals/research/nasa-nichols-doohan-photo-receipts-20261103 -p 'test_validate.py' -v
python -O -m unittest discover -s proposals/research/nasa-nichols-doohan-photo-receipts-20261103 -p 'test_validate.py' -v
```

**Next:** verify individual photographer/credit or NASA asset-catalog IDs,
confirm permissible factual nonpromotional use for actual Explorer placement,
then seek separate independent approval for a real-world historical-panel
media sidecar. These photo receipts cannot fill the episode/film thumbnail gap.
