# Into Darkness Sydney premiere — release-readiness decision, not an image release

**LOCAL DRAFT ONLY. No remote push, image publication, Explorer mutation or
new admission.** Evaluated from accepted `main`
`3e1a49e6d06af28fd8cab89fa02dae14d63ca5f8`, 2026-11-03.

## Source and Work boundaries

The accepted librarian [#416 source packet](../into-darkness-commons-premiere-20261103/records.json)
is an observation about a separately created documentary photograph.
It is not an episode frame, a film poster, a fictional scene, or a primary
source for Star Trek continuity. The relevant existing film catalog entry is
`film:film-into-darkness`, source-local `UNVERIFIED_METADATA`, official film
page `https://www.startrek.com/movies/star-trek-into-darkness`. A proposed
real-world local event, `commons:Star_Trek_Into_Darkness_Cast_2013.jpg#sydney-premiere`,
is linked *about* this film; it must not be resolved to a fictional Work event.

The source shows four people on a premiere wall and is described by Commons
as Karl Urban, Zachary Quinto, J. J. Abrams and Chris Pine at Sydney's
23 April 2013 premiere. On local visual inspection the exact original
1000×612 pixels match a documentary group photograph, including a substantial
partial promotional cast portrait and logos in the studio backdrop. Human
identity names come from Commons' caption, not independent biometric proof.

## License and source receipts

| Source artifact | Pinned evidence |
| --- | --- |
| Original Commons JPEG, 438,150 bytes | SHA-256 `fadaaaedf16cc0b5c5924251f2ae1ddb3545a04796ec85fab951c160f9c3a9a6` |
| [Commons file description oldid 1158784125](https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Into_Darkness_Cast_2013.jpg&oldid=1158784125) | Retrieved HTML SHA-256 `6c715ffff293381a1cd2764a838e0463cb1119c6e208a7149944457a70e800f7` |
| [Original Flickr photo](https://www.flickr.com/photos/evarinaldiphotography/8674151469/) | Source attribution; original page **not** directly authenticated from earlier retrieval |
| [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) | Commons FlickreviewR checked the listed photographer license on 23 April 2013; grant applies to Eva Rinaldi's *photographic work* |
| Accepted librarian source packet | `proposals/librarian/into-darkness-commons-premiere-20261103/records.json`, raw SHA-256 `b7a25bd69d641e183d1a19a38a970795ed9ea4fdbfc8e37c608dbe313267ded9` |

The photograph is *not* declared public domain. The CC license requires
credit to **Eva Rinaldi**, work title **Star Trek Into Darkness Cast 2013**,
source and license links, a change notice and ShareAlike where adaptation
requirements attach. A viewer-controlled opt-in does not impose DRM or
restrict legally permitted downstream copying; it only avoids unwanted
network requests. Neither a photo license nor a benign presentation can
grant Paramount's depicted key-art rights or waive publicity/privacy/moral
rights. Treat any fair-use or incidental-use theory as an unadjudicated legal
question, not a license. No model reviewer is legal counsel.

## Proposed exact visible UI copy

**Heading:** Behind the premiere: Star Trek Into Darkness (Sydney, 2013)

**Caption:** Documentary photo from the Sydney premiere on 23 April 2013.
This is a real-world event, not a frame or poster from the film.

**Alt text:** Karl Urban, Zachary Quinto, J. J. Abrams and Chris Pine
photographed together at the 2013 Sydney premiere.

**Attribution:** Star Trek Into Darkness Cast 2013 — photo by Eva Rinaldi /
Wikimedia Commons · [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/)
· Unmodified by this archive.

Two visible links belong alongside the credit: [Commons source with full
attribution](https://commons.wikimedia.org/wiki/File:Star_Trek_Into_Darkness_Cast_2013.jpg)
and [license terms](https://creativecommons.org/licenses/by-sa/2.0/).
Do not imply the performer, studio, or photographer endorses this archive.
Include: “Independent fan research; not affiliated with or endorsed by the
photographer, performers, Paramount or Star Trek rights holders.”

## Image optimization and privacy without additional licensed bytes

The exact original source JPEG is only **438,150 bytes (about 428 KiB)** at
1000×612, sufficiently bounded to make **unaltered** reuse a defensible
first release candidate. No resized, cropped, re-encoded or WebP derivative
was produced or distributed in this review. This avoids triggering extra
adaptation-analysis and accidental art/credit stripping; an optimized
derivative can be evaluated later, but would require its **own** hash,
visible modification notice and BY-SA treatment. Serving the original on
free static GitHub Pages avoids a paid image CDN; its availability/quotas
remain a hosting constraint, not a promised perpetual service level.

If independently cleared and explicitly authorized in a separate release:

1. Place the **identical** hashed JPEG under `licensed-artwork/` as a
   same-origin static asset, within the existing code-owned artwork gate.
2. Have the panel render **no `<img>` or CSS background image until deliberate
   opt-in**. After opt-in, use `loading=lazy`, `decoding=async`, exact
   `width=1000` and `height=612` to avoid layout shift. No CSS URL, prefetch,
   preload or service worker may request it before consent.
3. Set `referrerPolicy=no-referrer` on image and separate source links.
   The JPEG request itself goes only to the same GitHub Pages origin, not
   Wikimedia, Flickr or Paramount. Following attribution links is a distinct
   visitor action. **GitHub Pages still receives ordinary visitor network
   metadata**; this is a narrowly scoped third-party-image-request privacy
   design, not a claim of zero IP exposure to the host.
4. Never label the panel `PUBLICITY_STILL`, `FILM_POSTER`, or cinematic
   footage. The thumbnail policy currently permits `artwork_kind=OTHER`
   for a separately reviewed licensed local file, but a *distinct real-world
   event panel* is preferable to an ordinary fictional-film card.
5. Add an independent rights receipt containing the **image SHA**, separately
   captured **rights-page SHA**, license/source and exact local file path,
   reviewed title/caption/attribution, source-local film relation and two
   review identities. Require exact fixed code-owned release tuple and
   authenticated Pages package validation.

This packet itself does not write that receipt, change a release validator,
deploy any image, or reserve a future automatic permission flag.

## Independent hostile review and release disposition

Separate internal Auditor (a different model worker; provider/runtime not
established in this record) independently viewed the same image bytes and
returned **CONDITIONAL GO to build** the separate opt-in real-world event
panel, **HOLD actual public display**. Specific concerns:

> **Underlying rights:** Paramount photographic key art and logos are
> substantially visible on the wall. CC BY-SA 2.0 for Eva Rinaldi's camera
> photo does not necessarily cover embedded studio imagery. The image may
> be a derivative of non-licensed visual art; independent rights counsel or
> a defensible editorial-use adjudication is needed before public release.

> **People and association:** Four identifiable real persons are represented;
> event photography often serves editorial identification, but publicity,
> privacy, moral-rights and implicit studio endorsement cannot be assumed
> waived. Promotional presentation could shift the use from documentary to
> endorsement.

> **License details:** Version 2.0 BY-SA needs the supplied work title,
> creator/source/license links and change notice, and potential ShareAlike
> obligations for derivative treatment. A CSS `object-fit:cover` crop might
> visually alter the work and remove critical contextual backdrop. Better
> use the unchanged full image and `contain` semantics.

> **Misclassification:** A photograph alongside a film result is easily
> mistaken for an official movie still. Explicit event heading and source
> qualifier must persist through search, cards and accessibility output.

> **Privacy falsifier:** A `src`, preconnect, CSS background, thumbnail URL
> or eager preview pointing to Wikimedia before opt-in leaks a browser
> request despite a disabled-looking toggle. Only a browser/network
> inspection can verify absence of those requests in the released build.

The human legal/release decision is **not yet present**. Current status:
`CONDITIONAL_GO_TO_BUILD_ONLY_PUBLIC_RELEASE_HELD`.

Tests:

```bash
python3 proposals/librarian/into-darkness-release-readiness-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/into-darkness-release-readiness-20261103 -p 'test_validate.py' -v
python3 -O -m unittest discover -s proposals/librarian/into-darkness-release-readiness-20261103 -p 'test_validate.py' -v
```
