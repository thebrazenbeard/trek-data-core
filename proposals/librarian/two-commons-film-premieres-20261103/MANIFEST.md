# Two actual film-premiere photographs with photographer CC BY 2.0 evidence

**LIBRARIAN proposal only — independent rights and presentation review pending.**
Against accepted `main` at `26d87065072fef8f6944a63b3a8a46f165f020d9`
on 2026-11-03. Existing film-catalog source bytes: SHA-256
`6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de`.
Both source-local film rows remain `UNVERIFIED_METADATA` and this is **not** a
full-source read or a coverage claim.

| Film row | What the separate source actually depicts | Photographer | File / source / license |
| --- | --- | --- | --- |
| `film:film-2009` | Sydney Opera House film premiere on 7 Apr 2009; group with performers and production team. **Not a film still or poster.** | Penny B. Dreadful | [Commons photo](https://commons.wikimedia.org/wiki/File:StarTrekSydneyOperaHousePremiereApr09.jpg) · [original Flickr post](https://www.flickr.com/photos/visible-woman/3420160659) · [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) |
| `film:film-beyond` | *Star Trek Beyond* Japan red-carpet premiere on 19 Oct 2016; J. J. Abrams, Atsuko Maeda, Simon Pegg, Justin Lin. **Not a film still or poster.** | Dick Thomas Johnson | [Commons photo](https://commons.wikimedia.org/wiki/File:Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams,_Simon_Pegg,_Justin_Lin_%26_Maeda_Atsuko_(32041428851).jpg) · [original Flickr post](https://flickr.com/photos/31029865@N06/32041428851) · [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) |

These are **two independent photographs, not two independent confirmations of
fictional facts**. Commons reports that the first file's Flickr license was
checked by reviewer High Contrast on 2 May 2009 and the second by FlickreviewR
on 8 Jan 2017. The original Flickr pages were not independently read in this
tranche. The reported CC grants apply to each *photographer's photograph*;
they neither authorize Paramount posters/stills nor extinguish personality,
privacy, trademark, moral-rights or implied-endorsement concerns. The
[CC BY 2.0 deed](https://creativecommons.org/licenses/by/2.0/) explains that
other rights may remain. Both sources require creator/source/license credit,
notice of modification, and no suggestion the photographer endorses the archive.
CC BY 2.0 **does not impose ShareAlike**; do not mistakenly label these BY-SA.

## Measured source-byte observations

| Artifact | HTTP | Actual bytes | SHA-256 |
| --- | --- | ---: | --- |
| [Sydney pinned Commons rights page, oldid=1254161622](https://commons.wikimedia.org/w/index.php?title=File:StarTrekSydneyOperaHousePremiereApr09.jpg&oldid=1254161622) | 200 | 139,338 | `4b7bce02a22b7af112e7759fa664efcdf9a29cc708c9d2450a1de72a14de803f` |
| [Sydney original 1886 × 934 JPEG](https://upload.wikimedia.org/wikipedia/commons/9/9c/StarTrekSydneyOperaHousePremiereApr09.jpg) | 200 | 1,133,462 | `50c48ae7ce2fbbf30fa2010708eda4bf30503311bb71d0b4ceb5ca2d65837c04` |
| [Japan pinned Commons rights page, oldid=1173717753](https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams,_Simon_Pegg,_Justin_Lin_%26_Maeda_Atsuko_(32041428851).jpg&oldid=1173717753) | 200 | 136,365 | `f89befc960e1155e0e21407e3c84b4607441bb13ef8a7df513748b0e5fdb44a5` |
| [Japan original 5184 × 3456 JPEG](https://upload.wikimedia.org/wikipedia/commons/3/35/Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams%2C_Simon_Pegg%2C_Justin_Lin_%26_Maeda_Atsuko_%2832041428851%29.jpg) | 200 | 4,275,247 | `0e2be16a586aa3b3d29b77215986a85580c45b32d334376ecff60daf5f423fd1` |

Original image bytes were downloaded to **temporary untracked research
scratch**, decoded and visually inspected to test whether the subjects/context
match Commons descriptions. The image SHA-1 digests independently measured
match Commons' separately published file checksums (`57f391...` and
`7e30e6...`). The higher-resolution Japan photo contains a **studio film
advertising backdrop**; rights and incidental copyrighted background content
need an independent decision even though the documentary photograph itself is
CC BY. Do not misdescribe the Commons image as a poster cleared for reuse.
Page HTML SHA-256 receipts represent one retrieval of the selected revisions,
not a legal guarantee or an independently archived permanent snapshot.

No image binary is in this proposal or the public repo. No Explorer asset
or hotlink is changed; no public `rights_status` is upgraded. A *future*
release decision would have to independently review photographer license,
context, subjects, backdrop and attribution, then separately pin an exact
image SHA and rights receipt in the existing code-owned Explorer release gate.
An information panel should label photos as their **premiere events**.

> **Hostile countercase:** Film title and names in a Commons caption establish
> source attribution and a proposed film-event crosswalk, not primary
> verification of the entire feature film, any plot event, or blanket public
> display permission. A film listing with a photograph can mislead users into
> assuming it is an official screen capture. Keep the event label visible.

Validation (also run with `python3 -O` to ensure no assert bypass):

```bash
python3 proposals/librarian/two-commons-film-premieres-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/two-commons-film-premieres-20261103 -p 'test_validate.py' -v
python3 -O -m unittest discover -s proposals/librarian/two-commons-film-premieres-20261103 -p 'test_validate.py' -v
```

**Effects:** 2 photo metadata candidates, 0 public images, 0 coverage,
0 source/edition identity admission, 0 Explorer changes, 0 deployment.
