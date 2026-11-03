# Discovery S1 episode 6–10: five first-party publisher cards

**Research proposal only — not accepted Source/Work admission or close-read coverage.**

Lane: `DISCOVERY`; bounded batch `DIS.PPLUS.S1.SECOND5.20261103`.
Accepted baseline: `f4ea65391cf1543a55bf19dfcf3ed776dd80ab04`.
Publisher: [Paramount+ Season 1 Episode Guide](https://www.paramountplus.com/shows/star-trek-discovery/episodes/1/), retrieved 2026-11-03 (HTTP 200).

## Actual extraction

One direct `curl -L --fail` retrieved a **289,669-byte** HTML response, SHA-256
`1c428f8c7e85197d50dcfe5c8b2c7546933dc2293874eabb321b1ab03343c77e`.
That full response is kept outside the public repository. The exact five
source-card blocks were separately read and source-pinned:

| Publisher episode slot | Publisher title | Raw HTML lines |
|---|---|---|
| S1E6 | Lethe | 1667–1694 |
| S1E7 | Magic to Make the Sanest Man Go Mad | 1695–1722 |
| S1E8 | Si Vis Pacem, Para Bellum | 1723–1750 |
| S1E9 | Into the Forest I Go | 1751–1778 |
| S1E10 | Despite Yourself | 1779–1806 |

The records preserve the publisher's own time string, source-local video path,
description SHA-256 and character count, short **new original paraphrase**,
one local Work candidate, one local Entity mention, one source-bound Evidence
observation and one `PUBLISHER_DESCRIBES` assertion per episode. Five first-party
image URLs are preserved only as `HELD_NO_PUBLIC_DISPLAY_LICENSE` locators;
no image/video bytes were downloaded or displayed.

The 2026-11-02 Discovery Season 1 candidate roster was re-hashed at
`0d3db808c7319e32168be00e8756cf31e9686fe363419c6e671e1a7c0bc27418`.
All five title/number pairs matched the same publisher lineage. This is
**not** independent corroboration.

## Strict evidence boundary

- Only **publisher descriptions** were read. The actual episodes, authenticated
  scripts, full subtitles, and complete audiovisual works were **not** read.
- The source establishes that Paramount+ published these claims, not that
  the described fictional events objectively occur in all continuities.
- Local entities remain unresolved; no cross-work or global identity decisions.
- Raw timestamps do not settle local release/broadcast semantics.
- No accepted coverage, denominator, reconciliation, Explorer synopsis, source
  registry, or artwork publication effects.

## Validation and handoff

```sh
python3 proposals/research/discovery/s1-publisher-second5-20261103/validate.py
python3 -m unittest discover -s proposals/research/discovery/s1-publisher-second5-20261103 -p 'test_*.py'
python3 -O proposals/research/discovery/s1-publisher-second5-20261103/validate.py
python3 proposals/research/discovery/s1-publisher-second5-20261103/validate.py --source-html /path/to/private/exact_guide.html
```

The validator checks a code-owned semantic packet digest and the accepted
candidate-roster hash; optional exact private source replay checks card-local
association for title, number, timestamp, video, artwork and description bytes.
An **independent reviewer** must re-retrieve and rehash source cards from the
exact proposal head before any acceptance claim. Author validation is not
independent review.

**Next frontier:** S1E11–E15 publisher-card extraction, then source-authenticated
full-work reading and separately authorized Source/Work admission. Do not
confuse five new metadata research records with five close-read episodes.
