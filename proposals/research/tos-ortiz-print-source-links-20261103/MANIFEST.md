# TOS Juan Ortiz art-print source leads — repaired draft custody

**Batch:** `tos-ortiz-print-source-links-20261103`
**Role:** TOS artwork-source research, **not** episode or image-rights qualification
**Original accepted selection base:** `2070b0153228272b5dd667b0a23465ff49a95a5f`
**State:** source-local proposal only; no Source–Work/coverage/public-art effect.

## Publisher sources actually read

1. StarTrek.com staff, [*Four New Star Trek Art Prints Now Available*](https://www.startrek.com/news/four-new-star-trek-art-prints-now-available), displayed publication date **February 3, 2014**. Publisher lists Juan Ortiz's **The Cage** among four print products and records Ortiz's first-person comments about designing the piece differently from a possible Menagerie composition. The author's interview statements establish what he **said about his design**; they do not establish events depicted in the episode or grant public image-display rights.
2. StarTrek.com staff, [*Juan Ortiz Unveils May 2013 TOS Art Prints*](https://www.startrek.com/news/juan-ortiz-unveils-may-2013-tos-art-prints), displayed publication date **May 1, 2013**. Publisher lists **The Menagerie: Part 1** in the May art-print set, while Ortiz discusses his Pike-chair concept and why he credited Jeffrey Hunter for integrated *The Cage* footage. These are **publisher listing and attributed artist statements**, not independently viewed episode frames, an authenticated audiovisual derivative analysis, or a licensed thumbnail.

Both public article **rendered text views** were read on **2026-11-03**. No authenticated raw HTML, immutable source snapshot, full article transcript, linked image bytes, media playback, or license grant was obtained. Source access is exactly `PUBLIC_WEB_TEXT_READ_2026-11-03_NOT_AUTHENTICATED_RAW_HTML`; `raw_source_sha256` is `null`. This packet therefore qualifies as **source-local art-product discovery**, not verified primary artwork custody. The two articles share the same `startrek_com_editorial` publication family: they are not independent licensors.

## Exact proposal and source-row pins

The strict validator's SHA-256 pins use canonical UTF-8 JSON serialization with **sorted keys**, compact separators and `ensure_ascii=False`. They are **integrity checks on the reviewed proposal text**, not source-authentication digests or permission receipts. The original `observations.json` is unchanged by this repair.

| Scope | SHA-256 |
| --- | --- |
| Full `observations.json` file bytes | `b151c7736b409bc90d97802e5ac7ca4e961d3ef197c123d7b49131fe10e7b115` |
| Canonical envelope excluding `records` | `553c5a04729de33a01e5984e4b0f14c15bdd35017de47c43c58cdbdfd98e7cfb` |
| `startrek:ortiz:2014-02-03:cage` full canonical row | `7dfdea24070ebe136a2df6515b3f8933c873b9abb7ba972ae252a0bb65ee6198` |
| `startrek:ortiz:2013-05-01:menagerie1` full canonical row | `7fb1adff8f2bcbe396d571d452370815c0ac56cff839b29c4bfe9aafc7275c89` |

Each row's full digest pins **source date, article URL, publisher-observed art-product title, creator, medium, evidence text, source-relative assertion, original held short description, editorial status, artwork-rights hold, binary status and unresolved Work identity**. Exact envelope/source-class and limitations are pinned separately, with explicit rights/status allowlists. Additional fields, changed order/IDs, duplicate raw JSON keys and assertions claiming broad licenses fail validation.

## Rights, interpretation, and next gate

- `artwork_rights = HELD_NO_PUBLIC_DISPLAY_LICENSE` for each candidate. The articles advertise commercial print products; availability for purchase is **not** a license to mirror, embed, hotlink, transform or publicly display their images.
- `image_binary_included = false`, `work_identity = UNRESOLVED`; there is no stored poster or inferred canonical artwork/episode Work match.
- `accepted_source_work_effect`, `coverage_effect`, `public_artwork_effect` all **NONE**. Original short descriptions are held research prose and do not become public Explorer art/synopsis.
- The May artist's remark about integrated footage is evidence **of his attributed statement**, not independent proof of specific frames or shot equivalence. The Cage and Menagerie print leads remain distinct source-local product candidates.

## Reproduction and hostile repair history

```bash
python3 proposals/research/tos-ortiz-print-source-links-20261103/validate.py
python3 -m unittest discover -s proposals/research/tos-ortiz-print-source-links-20261103 -p 'test_*.py' -q
python3 -O -m unittest discover -s proposals/research/tos-ortiz-print-source-links-20261103 -p 'test_*.py' -q
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

Independent [original HOLD review](https://github.com/thebrazenbeard/trek-data-core/pull/357) ID `5753354069` demonstrated that replacing source class with `LICENSED_PUBLIC_IMAGE_SET`, deleting limitations, forging 2099 publication date and adding false reuse-license evidence **all previously passed**. New tests were executed **before** repair and reproduced failure, then the fixed validator rejected the combined and individual forgeries in both normal Python and optimized `python -O`. The repair does **not** upgrade source authentication or rights status; independent new-head review is still required before any protected merge.
