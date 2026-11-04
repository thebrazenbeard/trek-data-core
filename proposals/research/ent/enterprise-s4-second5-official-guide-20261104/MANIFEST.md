# Enterprise Season 4 E06–E10 — second held publisher-guide description batch

**Batch:** `ENT.PPLUS.S4.SECOND5.GUIDE.20261104`

**Role:** ENT series publisher-guide source-relative research, not audiovisual episode close reading.

**Dependency:** isolated branch `research/ent-s4-e06-e10-20261104` from the local first-five commit `9da214b3231870c3879f9f645e9bf9e9ab6f7c53` and records SHA-256 `f8e65b062b7b53929341d6dbca31dd20f29bf09f995b9a5daf628dc12b6e4f10`. Accepted GitHub `main` ancestor remains `3028765359001b90bc3e6b5c1835ee283b326e91` with no accepted research Work/coverage changes from these local batches.

## Fresh complete official page receipt

At `2026-11-04T22:14:11.211831+00:00`, retrieved the **complete** [Paramount+ *Enterprise* Season 4 guide](https://www.paramountplus.com/shows/enterprise/episodes/4/) in a read-only operation: HTTP 200, Date `Wed, 04 Nov 2026 22:14:11 GMT`, **301,606 bytes**, raw SHA-256 `45b350714aa0d57596d38977018664e116e790f9186671999988c638e08d55e8`.

Its 22 publisher cards and associated normalized descriptions were parsed in memory using the exact first-five source parser; every title, ordinal, video-route metadata locator, datetime string and description fingerprint matched the first local snapshot. The raw HTML SHA differs from the first snapshot (`e0a5c2910e2f9cd43a3316d1bbbc06774c9d76eec422829f0f60fd9630eb6392`), as expected for a mutable publisher page. **This is one Paramount+ publisher lineage, not independent corroboration.**

The five actual E06–E10 descriptions (**723 publisher-text characters**) were read and condensed into five independently worded short paraphrases in `records.json`, each linked to a local source entity, source-relative description evidence, and a `PUBLISHER_DESCRIBES` assertion.

| Source-local card | Publisher display title | HTML anchor / description line | Exact publisher-description SHA-256 |
|---|---|---|---|
| E06 | The Augments | 1622 / 1640 | `739295c7b2a8253ff2571357b5cd9631583671c0fbfebc6928a641cd2f156c12` |
| E07 | The Forge | 1650 / 1668 | `47ae93ad886d52f46f1ab82dd517ec73665b99c86eaba6cffadd8a43eb7d5e29` |
| E08 | Awakening | 1678 / 1696 | `352fe70f2709ef74f953c4fe5781ff3c34a359ec14afa96738b81ec64d6ca1cd` |
| E09 | Kir'Shara | 1706 / 1724 | `bded78321051f42921244c738e156cbd6e8b2dd80165e74ce3fea067a55e32de` |
| E10 | Daedalus | 1734 / 1752 | `9c1e2540da710e80246cf015b1d27ed88c776fc573bfe2b3ae276282c33a0456` |

Locators refer to the exact response identified by hash; future dynamically generated page bytes may differ. Source video-route paths are metadata **only**. No linked video, caption, script, audiobook, images, source raw HTML, or full copyrighted source paragraphs were committed.

## Preserved anomaly and effect boundary

The current entire page independently re-exhibited the **same source-internal E22 capitalization disagreement** seen in the first read: displayed and leaf-analytics title `These Are the Voyages`; analytics series-title `These Are The Voyages`. The record preserves both and the `CAPITALIZATION_VARIANT_UNRESOLVED` status. It is not silently normalized into a canonical Work title or used to inflate E22 research coverage.

Across two disjoint held batches the source-relative publisher-description synopsis proposal count is **10 of the 22 official guide cards**. Twelve publisher descriptions remain unprocessed. No accepted Work/Source bindings, governed coverage, episode audiovisual `CLOSE_READ`, reconciliation, public Explorer synopsis publication, media rights decision, merge, deployment, or remote changes occurred.

> **Hostile review:** Repeated reads of one publisher's editorial blurbs may confirm stable metadata but cannot verify narrated events in audiovisual content. Even source-derived episode ordinals are local hints until separate Work reconciliation. The held E22 capitalization discrepancy is a provenance flag, not a repaired name.

## Validation

```bash
python3 proposals/research/ent/enterprise-s4-second5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s4-second5-official-guide-20261104 -p test_validate.py -q
python3 proposals/research/ent/enterprise-s4-first5-official-guide-20261104/validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests -q
git diff --check
```

The validator pins exact predecessor record-file/commit/source receipts, re-runs its accepted discovery lineage validator, confirms all 22 normalized source cards unchanged, enforces the unique five new local entity/evidence/assertion IDs and exact metadata fingerprints, and rejects protected-effect or count promotion. Hostile tests tamper with cross-batch IDs, receipt ancestry, source type, card order, E22 conflict, claim scope and unsupported coverage.

**Next frontier:** a fresh, separate publisher-guide E11–E15 held tranche from this exact predecessor, or independent authorized episode source access for genuine audiovisual analysis. Do not treat a 22-card guide as 22 reviewed episodes.
