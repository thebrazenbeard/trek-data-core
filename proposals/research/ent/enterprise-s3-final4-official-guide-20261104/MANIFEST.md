# Enterprise S3 E21–E24 — final four official publisher-guide descriptions, HELD

**Batch:** `ENT.PPLUS.S3.FINAL4.GUIDE.20261104`
**Role:** ENT series worker, publisher-guide source-relative research only.
**Dependency:** isolated branch `research/ent-s3-e21-e24-20261104` based on local predecessor commit `e4fac2d43c0e24f7259a9eb22200d4dbcda1ee3f`; prior four separate held packets included. Accepted-main ancestor `3028765359001b90bc3e6b5c1835ee283b326e91` remains unchanged.

## Complete first-party source receipt

A fresh read-only GET fetched the **entire** [Paramount+ *Enterprise* Season 3 episode guide](https://www.paramountplus.com/shows/enterprise/episodes/3/) at `2026-11-04T21:56:03.917959+00:00`: HTTP **200**, Date `Wed, 04 Nov 2026 21:56:03 GMT`, **308,190** response bytes, raw SHA-256 `6c27e3a8ab1e8a5b7842f66bc51ecc142abe401aaefa08be201acd6a36aac7be`.

The same parser traversed **all 24** publisher cards and description strings. Normalized title/ordinal/video-route/date/description fingerprints of **all 24** agreed with the four preceding complete publisher-guide reads, though each full raw HTML SHA differs (dynamic HTML). The four final descriptions—**699 publisher-text characters total**—were actually inspected; each has one original brief paraphrase in `records.json`. The actual publisher paragraphs and raw HTML are not stored in this public Git packet.

| Source-local episode | Publisher title | HTML anchor / description line | Description SHA-256 |
|---|---|---|---|
| E21 | E (squared) | 2042 / 2060 | `5570b50cb63f0043941cbf9a2469b9414152432f4628384deeb99989055b483a` |
| E22 | The Council | 2070 / 2088 | `51e321ada9f03d4b72e64fa5f98e63b4d99b8d8092765c5eef3d4354fbb30956` |
| E23 | Countdown | 2098 / 2116 | `ab20b5e99082d383d162e6fc721d9d945f0e7f871d89fd5f2b02d45b4485812d` |
| E24 | Zero Hour | 2126 / 2144 | `f29bf2d5a9eec9512619456ed68a93dcc0df61527ad11f5eba76bee9025c4343` |

Line locators refer to this exact mutable HTTP response; without preserving a copyrighted raw snapshot, future page retrieval may shift them. `source_probe.py` can recover contemporary cards/hashes, not guarantee byte identity with this response. Linked `/shows/video/.../` paths are **metadata locators only**; no video, audio, transcript, caption, image, or book content was requested or close-read.

## Five disjoint held description packets

| HELD packet | Source-relative description analyses | Local commit | Records SHA-256 |
|---|---:|---|---|
| first5 | E01–E05 | `67e997fe4db0eaa20a96b311c91006520c767848` | `05e7375949b0facdbda22bc2e0a3ff8ec6a46c9cdb901a34ac5fd4e98d837f27` |
| last5 | E06–E10 | `865291996cf0c16286f1aea05fe562c354a83408` | `54e50b5e169a961912f2cde1d1a19bdf8eabfc704bd5b216b40902df9ff302d7` |
| third5 | E11–E15 | `5719fcab4cac59c868d80456cb10a3110e728600` | `f8dd841d56f6551824dbac89739893fb0b924c46743cb96ff6226d6d8fe9572c` |
| fourth5 | E16–E20 | `e4fac2d43c0e24f7259a9eb22200d4dbcda1ee3f` | `5783a77f9910588ac4647e9c3ca384faae38912fa893749be5e04d9b032046ca` |
| final4 | E21–E24 | current proposal | see SHA-256 of `records.json` at commit handoff |

**This closes the *24/24 publisher-guide description-proposal lane only*.** All 24 source-local cards have individually source-bound synopsis paraphrase proposals across five disjoint packets. Neither an E25 nor a 25th synopsis is invented. This is **not** 24 accepted canonical Works, transcripts, audiovisual CLOSE_READ episodes, or a completed season in any accepted semantic-coverage denominator. All five first-party reads are one source lineage `publisher:paramountplus.com`, not five independent corroborations.

> **Hostile finding:** A publisher synopsis is evidence that the publisher describes an episode that way. Neither repeated retrieval nor deterministic agreement validates the described fictional events, independent identity, original broadcast semantics, or audiovisual episode content. True episode CLOSE_READ still requires direct eligible complete source access and separate evidence custody.

All four `PUBLISHER_DESCRIBES` assertions explicitly remain `SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED`; each has a local entity/evidence/claim with exact content fingerprint. Six protected effects—including Source/Work admission, reconciliation, coverage denominator and public Explorer release—are `NONE`. No raw publisher text, copyrighted media, artwork, source video, or credentials were committed or deployed.

## Reproducibility and next frontier

```bash
python3 proposals/research/ent/enterprise-s3-final4-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s3-final4-official-guide-20261104 -p test_validate.py -q
python3 tools/validate.py
python3 -m unittest discover -s tests -q
git diff --check
```

Validator pins the four previous record-file digests, commits, independent raw receipt SHA values, publisher lineage, disjoint E01–E24 local IDs/order, four final exact description fingerprints and source lines, and zero protected effects. Hostile tests deliberately mutate source custody, copied-source independence, order, E25, unsupported Work/coverage/CLOSE_READ and false claim status. No evidence is upgraded because tests passed.

**Next frontier:** independent work/source identity review and eventual qualified complete episode audiovisual/transcript source inspection under the project's rightful custody controls—only then could any actual CLOSE_READ or governed coverage be proposed. This is a local proposal branch only, not merged/pushed/deployed.
