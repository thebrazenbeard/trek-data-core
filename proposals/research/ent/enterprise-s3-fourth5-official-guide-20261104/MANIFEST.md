# Enterprise Season 3 E16–E20 — first-party publisher guide, HELD

**Batch:** `ENT.PPLUS.S3.FOURTH5.GUIDE.20261104`

**Role:** ENT series worker; source-relative publisher-guide metadata and original synopsis paraphrases only.

**Dependency:** New isolated worktree/branch `research/ent-s3-e16-e20-20261104` based on predecessor `5719fcab4cac59c868d80456cb10a3110e728600`, with three previous, separate held ENT S3 tranches. The common accepted-main ancestor remains `3028765359001b90bc3e6b5c1835ee283b326e91`; no accepted-main changes.

## Fresh complete first-party guide reading

At `2026-11-04T21:45:29.161021+00:00`, the complete [Paramount+ *Enterprise* Season 3 episode-guide](https://www.paramountplus.com/shows/enterprise/episodes/3/) HTML was retrieved read-only: **HTTP 200**, response Date `Wed, 04 Nov 2026 21:45:29 GMT`, **308,190 bytes**, raw SHA-256 `b939d2a77786228811338f2c3b3b4d7c2bf0babc289f47768339945e017283bb`.

The same structural parser traversed all **24** guide cards and their source-description strings in memory. Their exact normalized title/ordinal/video-locator/datetime/description hashes matched all prior observations, even though the raw page HTML SHA changed. For E16–E20, **five source descriptions totaling 819 source-text characters were actually read** and rewritten into five original brief paraphrases. Complete publisher paragraphs and raw HTML were not committed. No video, audio, script, caption, or image bytes were fetched.

| Source-local card | Publisher title | HTML description line | Description SHA-256 |
|---|---|---:|---|
| S3E16 | Doctor's Orders | 1920 | `2b060a05e7e317e320e793f83696a8d529f8f4742dfe93572057369fd6537c7d` |
| S3E17 | Hatchery | 1948 | `9f307bd33144f6f21dc221607b3a5993de5dec3dd3cec9da2a249cf2e5f98125` |
| S3E18 | Azati Prime | 1976 | `465eb244c950bcb79cd685ee3f25449ab5d692fc79c3a119c851fff1528fded5` |
| S3E19 | Damage | 2004 | `0647b740b5dff34294f1cc59508f06966b2c4d5e2b450a62f93c6a137709385b` |
| S3E20 | The Forgotten | 2032 | `78d4de662bfffd6c2f070c3b3c8eb5771f8b52e8dc3051b84d30cd13d05a08c2` |

Line numbers apply to this **exact** dynamic HTML retrieval, not a permanently archived edition. Source-relative video paths were recorded solely as metadata; no video route was requested. Publisher date strings were preserved without assuming original broadcast or streaming availability semantics.

## Disjoint predecessor lineage

| Held batch | Episode-analysis scope | Local commit | Records SHA-256 |
|---|---|---|---|
| `first5` | E01–E05 | `67e997fe4db0eaa20a96b311c91006520c767848` | `05e7375949b0facdbda22bc2e0a3ff8ec6a46c9cdb901a34ac5fd4e98d837f27` |
| `last5` | E06–E10 | `865291996cf0c16286f1aea05fe562c354a83408` | `54e50b5e169a961912f2cde1d1a19bdf8eabfc704bd5b216b40902df9ff302d7` |
| `third5` | E11–E15 | `5719fcab4cac59c868d80456cb10a3110e728600` | `f8dd841d56f6551824dbac89739893fb0b924c46743cb96ff6226d6d8fe9572c` |
| `fourth5` | E16–E20 | this proposal | see `records.json` |

The previous three record files and response digests are pinned in `records.json`. This packet's five local entity/evidence/assertion IDs cannot overlap the prior fifteen. The 24-card guide context is not 24 source-close-reads, and repeated retrievals from `publisher:paramountplus.com` are **not independent source witnesses**.

> **Hostile challenge:** The editorial episode synopses may simplify, omit, or misstate fictional events. Their hashes and consistent publisher card ordering are genuine source-relative evidence, but neither objective audiovisual plot verification nor canonical Work identity admission.

Every typed assertion is `PUBLISHER_DESCRIBES`, status `SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED`. The packet claims **zero** accepted Source/Work binding, reconciliation, coverage, denominator or public Explorer synopsis effects. Artwork rights are unresolved; no original copyrighted paragraphs or media assets were redistributed.

## Validation and exact next frontier

```bash
python3 proposals/research/ent/enterprise-s3-fourth5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s3-fourth5-official-guide-20261104 -p test_validate.py
python3 proposals/research/ent/enterprise-s3-third5-official-guide-20261104/validate.py
python3 proposals/research/ent/enterprise-s3-last5-official-guide-20261104/validate.py
python3 proposals/research/ent/enterprise-s3-first5-official-guide-20261104/validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests
git diff --check
```

The validator enforces the exact three predecessor file SHA/commit receipts, all four disjoint source-local episode intervals, current five publisher card fingerprints and HTML lines, original paraphrase bounds, and protected no-effect flags. Synthetic hostile tests challenge double count, source/lineage tamper, false Work/CLOSE_READ/coverage promotion and strict ordinal typing.

**Next frontier:** ENT Season 3 E21–E24, a final **four-episode** publisher-description tranche (do not invent E25); or genuine authorized audiovisual/transcript source custody before any actual episode CLOSE_READ. This batch remains local-only.
