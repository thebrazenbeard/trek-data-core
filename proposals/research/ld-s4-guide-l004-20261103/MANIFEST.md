# LD L004 — Lower Decks Season 4 Paramount+ guide cards

**Role:** Lower Decks series source-local researcher

**Batch:** `ld-s4-guide-l004-20261103`

**Accepted `main` at selection:** `c1668772cab7004da1bfe0759f521d22c3679280`
**State:** unaccepted proposal; no governed Work, Source–Work, coverage or publication effects.

## Primary material actually read

- [Paramount+ U.S. Lower Decks Season 4 episode guide](https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/4/), all ten displayed **S4 E1–E10** guide cards, rendered text lines 108–163 on 2026-11-03.
- One additional direct first-party HTTPS retrieval returned HTTP 200, **271,583 bytes**, SHA-256 `e78ce95aca066d8bc126fc203bf1c28b1bf16a8675847e28d3821f566d73dc32`. The publisher's page may change dynamically; this is a receipt for the transient response, **not** an immutable source edition or an archived HTML capture. Raw HTML is not committed.
- Each card's own `<h2>` title, publisher Season 4 episode ordinal, and decoded, whitespace-trimmed short description were inspected. SHA-256 of each exact UTF-8 description is recorded; no promotional description is reproduced in `observations.json`.
- Each record contains source-relative **literal terms** from that card's publisher description, plus an exact *same-card* `thumbnails.cbsig.net` URL discovered in its HTML. These are information locators, **not image copies or public-display permission**. No image bytes were downloaded.

| Publisher position | Source-local title | Source-relative evidence |
| --- | --- | --- |
| S4 E1 | Twovix | Card, SHA-256 description fingerprint, Cerritos mention, HELD CDN image URL |
| S4 E2 | I Have No Bones Yet I Must Flee | Card, description fingerprint, three publisher mention strings, HELD image URL |
| S4 E3 | In the Cradle of Vexilon | Card, description fingerprint, Boimler mention, HELD image URL |
| S4 E4 | Something Borrowed, Something Green | Card, description fingerprint, Tendi/Orion mentions, HELD image URL |
| S4 E5 | Empathalogical Fallacies | Card, description fingerprint, Betazoids/Cerritos mentions, HELD image URL |
| S4 E6 | Parth Ferengi's Heart Place | Card, description fingerprint, Cerritos/Ferengi mentions, HELD image URL |
| S4 E7 | A Few Badgeys More | Card, description fingerprint, Cerritos mention, HELD image URL |
| S4 E8 | Caves | Card, description fingerprint, Lower Deckers mention, HELD image URL |
| S4 E9 | The Inner Fight | Card, description fingerprint, three publisher mention strings, HELD image URL |
| S4 E10 | Old Friends, New Planets | Card, description fingerprint, Mariner mention, HELD image URL |

## Source, evidence and identity boundaries

`SOURCE → LOCAL CARD ENTITY → DESCRIPTION FINGERPRINT/LITERAL MENTION → ATTRIBUTED PUBLISHER ASSERTION`.

- This is a guide read, **not** a read/viewing of ten actual episodes, scripts, dialogue, events or on-screen appearances. Mention strings establish only that the publisher wrote them. Identity reconciliation, fictional truth and cross-work connections are out of scope.
- Earlier accepted Lower Decks Season 3 guide packet `proposals/research/ld-s3-guide-l003-20261103/observations.json` is byte-pinned at `e8153b87644354a60ff900f0cc612b4efe37aae9dccbd13fc95960879f575e65`. It is a separate season and the same corporate publisher family, **not independent corroboration**. Accepted S1/S2/S3 research partitions do not occupy these new L004 local IDs.
- There is no accepted Season 4 discovery CSV/bundle at this checkpoint. This batch does not manufacture one or promote ten source-local cards into the 1,214-row discovery denominator.
- `accepted_source_work_effect`, `accepted_work_effect`, `coverage_effect`, `denominator_effect`, `public_synopsis_effect`, `public_artwork_effect`: **NONE**.
- Ten **synopses are withheld**: neither copied publisher prose nor author-written paraphrases are published. Ten image URLs are `HELD` by field name, with no image rights assertion, artwork bytes or Explorer display.

## Deterministic checks and falsifiers

```bash
python3 proposals/research/ld-s4-guide-l004-20261103/validate.py
python3 -O proposals/research/ld-s4-guide-l004-20261103/validate.py
python3 -m unittest discover -s proposals/research/ld-s4-guide-l004-20261103 -p 'test_*.py' -q
python3 -O -m unittest discover -s proposals/research/ld-s4-guide-l004-20261103 -p 'test_*.py' -q
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

The validator enforces exact field schemas, all ten publisher title/slot/description hashes, literal mention lists, own-card image URL pairs, HTTPS source host, predecessor packet SHA, no Work/coverage/publication effects, and duplicate-key rejection. Adversarial tests include more than 40 targeted alterations, including same-host artwork swaps, false licenses and global identity claims. These model-written checks do **not** independently verify an immutable publisher edition.

**Next frontier:** Independent reviewer source reread, exact-HEAD tests/CI, then accepted merge only under Patrick's delegated authorization. Future S5 remains a separate research lane after fresh collision checks.
