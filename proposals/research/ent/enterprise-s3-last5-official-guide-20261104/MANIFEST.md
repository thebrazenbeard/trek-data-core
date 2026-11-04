# Enterprise Season 3, official publisher-guide E06–E10 — HELD

**Batch:** `ENT.PPLUS.S3.LAST5.GUIDE.20261104`

**Role:** ENT series research worker, source-relative guide descriptions only. This is a **separate successor** to E01–E05, not a modification of that packet.

## Exact source retrieval and comparison

Fresh full official HTML GET: [Paramount+ *Enterprise* Season 3 episode guide](https://www.paramountplus.com/shows/enterprise/episodes/3/), **HTTP 200**, Date `Wed, 04 Nov 2026 21:27:07 GMT`, observed at `2026-11-04T21:27:07.719354+00:00`.

- Complete HTML response: **308,190 bytes**, raw SHA-256 `0cf747270fe37f0027b4a4c90937e2bd2b2ca91442768e6f7fafcc22adee1253`.
- All **24** publisher cards and descriptions were traversed in memory using the same structural parser as the first-five packet; their 24 normalized metadata and description fingerprints matched those from the first retrieval **exactly**.
- The **whole HTML** SHA differed from E01–E05 (`227c1cbcbafd29cabb62ff83e73cccd2466604ab0e3c4462920badf774453391`). These are two mutable page observations, **not two independent source witnesses**.
- The E06–E10 descriptions were actually read and processed: **five descriptions totaling 836 source-text characters**, yielding five original short paraphrases, source-local entities, description-evidence rows and typed `PUBLISHER_DESCRIBES` assertions. No original publisher paragraphs or raw HTML were committed.
- `source_probe.py` reuses the original structural parser and emits hashes and card locators. Its optional internal-prose mode is for private source reading only; output must never be committed.

| Publisher card | Official title | HTML description line | Description SHA-256 |
|---|---|---:|---|
| S3E06 | Exile | 1640 | `9fbfe25466b7f8d670d35c66d480f498884f0ece7b9cbc4050cc8c3fc1c98c53` |
| S3E07 | The Shipment | 1668 | `e797d41bea3abc7f33f89dbfe4702f91168ff002a7c6fd048fa06444e2c1c590` |
| S3E08 | Twilight | 1696 | `25046c252c40e19250ca307777cee39edffffbb1f8b18f5a9092c4b2ce021915` |
| S3E09 | North Star | 1724 | `5065c3891b188cce824b3ba881f682a341d87cb9f973f6bccee5782623f36743` |
| S3E10 | Similitude | 1752 | `037c1fad4eed589d8633110f841d48adc862349a93ff81a2facf085b264267e3` |

Description line references are relative to the *exact retrieved HTML*. The 24-card traversal does **not** mean 24 analyses or 24 accepted episodes.

## Distinct predecessor and evidence holds

The first-five packet is `proposals/research/ent/enterprise-s3-first5-official-guide-20261104/records.json`, exact SHA-256 `05e7375949b0facdbda22bc2e0a3ff8ec6a46c9cdb901a34ac5fd4e98d837f27`, local commit `67e997fe4db0eaa20a96b311c91006520c767848`. It contains five E01–E05 publisher-description analyses and all 24 guide-card hashes for context; this separate E06–E10 packet has distinct IDs and a separate manifest and pinned full HTML receipt.

> **Hostile challenge:** Paramount+ descriptions establish only what its editorial cards say. They cannot establish actual audiovisual depictions, plot truth, exact character identity, global Work boundaries, or source independence. The repeated publisher read strengthens metadata stability but does not grant CLOSE_READ or license rights.

No episode video/audio, transcript, script, image bytes or artwork were accessed. No canonical Work or Source binding, global reconciliation, accepted coverage/denominator, or public Explorer effect. This is a local held proposal, not accepted `main`.

## Verification

```bash
python3 proposals/research/ent/enterprise-s3-last5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s3-last5-official-guide-20261104 -p test_validate.py
python3 proposals/research/ent/enterprise-s3-first5-official-guide-20261104/validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests
git diff --check
```

The validator pins the preceding file-byte SHA, source hashes, exact five card fingerprints and locators, non-overlapping E01–E10 local IDs, no false independent lineage and all protected no-effect flags. Targeted adversarial tests challenge duplicate IDs, digest tampering, title/ordinal errors, and fabricated episode viewing/coverage.

**Next frontier:** A new held ENT Season 3 E11–E15 description tranche with its own source receipt, or rights-compatible, genuinely authenticated episode/transcript close-reading authority. The latter has not yet occurred.
