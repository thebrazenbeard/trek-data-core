# *Star Trek Beyond* film-premiere documentary image: photographer-licensed source

**LIBRARIAN source-local proposal; public image display HELD pending independent review.**
Retrieved against accepted `main` `2b1b76850abfe23bab42977e60213c06e70165ee`
on 2026-11-03. This does not create a Work, assert a film scene or change
research coverage.

## Source-relative identity

- Existing `explorer/film-catalog.json` source-local ID `film-beyond`;
  prospective artwork row `film:film-beyond`.
- First-party film locator: [StarTrek.com — Star Trek Beyond](https://www.startrek.com/movies/star-trek-beyond).
- Accepted film-catalog SHA-256:
  `6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de`.
- The proposed photo depicts **J. J. Abrams and Simon Pegg at the October 2016
  Japanese premiere of the film**, according to its source caption. It is an
  **editorial event photograph**, not a *Star Trek Beyond* frame, poster,
  publicity still, or fictional event. Pixel review independently found two
  people matching the named subjects, with Pegg holding a microphone;
  pixels alone do not establish who, where or when.

## Direct photographer and rights trail

- [Original Flickr post 31784488840](https://www.flickr.com/photos/31029865@N06/31784488840/):
  author Dick Thomas Johnson; photo title names the *Star Trek Beyond*
  Japanese red carpet, captured 2016-10-19, uploaded 2017-01-07. Its
  `Some rights reserved` link points to the photographer's
  [CC BY 2.0 deed](https://creativecommons.org/licenses/by/2.0/).
- [Wikimedia Commons file page](https://commons.wikimedia.org/wiki/File:Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg),
  [pinned revision 1217252320](https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_(31784488840).jpg&oldid=1217252320):
  photographer Dick Thomas Johnson, 2016-10-19 premiere; reports a
  FlickreviewR CC BY 2.0 confirmation on 2017-01-08 and links the same Flickr
  photo. This is an attribution-conditioned license for the **photographer's
  image**, not blanket permission to imply endorsement by the subjects,
  Paramount, Trek trademark owners, or Flickr.

## Real byte and pixel verification

On 2026-11-03, authorized owner-host Lappy HTTPS retrieves with a task-scoped
User-Agent and independently downloaded temporary scratch copy yielded:

| Exact artifact | HTTP | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Commons pinned HTML rights page, oldid `1217252320` | 200 | 131,423 | `120ef8dab3534b75d8c0cbf56f0dede4ea3a232a4e31e31d081488a3579bc1c1` |
| Original Commons photograph (JPEG, 4,552 × 3,035) | 200 | 4,134,183 | `7fd481633086f97e7b05e0eccbd3515a90d44f4fa7ce1255180007d9d13b4250` |

The original photograph was **viewed visually** in scratch to verify that
J. J. Abrams and Simon Pegg appear together in a real event setting. It was
not committed. The Commons page's media SHA-1 metadata is not a substitute
for our original-byte SHA-256 receipt. The direct Flickr page was read via
public retrieval; the actual Flickr *image bytes* were not independently
compared with Commons original bytes.

## Exact future display and independent gate

If independently approved, the only accurate Explorer use is a visibly
captioned **2016 Japan premiere documentary photograph**, with photo credit,
Commons file/source and CC BY 2.0 license links, indication of any crop,
and no apparent studio or cast endorsement. No thumbnail should be labeled
film still, scene or poster. An unmodified thumbnail can be linked to the
same page; a crop/resize must state modification under the license.

> **Hostile challenge:** A photograph accurately associated with the film's
> premiere still does not depict an event in the film. A film card showing
> only a photograph without an event-kind caption would materially mislead
> the reader, even where the photographer provided a valid CC license.

This batch **does not** modify the Explorer, release image bytes, hotlink the
image, change canonical Work/Source binding, or claim coverage. Display
eligibility remains `HELD_UNTIL_INDEPENDENT_REVIEW` pending context,
personality/privacy, exact media and nonendorsement review. See
`records.json` for machine-readable evidence and `validate.py` for the
tamper/contract gate.

Validation:

```sh
python3 proposals/librarian/beyond-commons-premiere-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/beyond-commons-premiere-20261103 -p 'test_validate.py' -v
python3 tools/validate.py
```
