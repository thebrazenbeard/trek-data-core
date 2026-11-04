# Starfleet Academy publisher–Wikidata difference audit (held)

**Packet:** `SFA-PUBLISHER-WDQS-DIFF-20261104-001` · **role:** SFA audiovisual worker · **status:** `HELD_COMPARISON_PROPOSAL` · **date:** 2026-11-04 UTC.

Accepted baseline: `thebrazenbeard/trek-data-core main@3028765359001b90bc3e6b5c1835ee283b326e91`. This audit is stacked **locally** on unaccepted SFA route-proposal commit `bef9925`; that dependency is not accepted `main`. It is a deterministic comparison of already-observed metadata, **not** a new content extraction, a canonical episode list, an audiovisual close-read, or Source↔Work admission.

## Question and method

Can the ten [Paramount+ publisher episode-guide routes](../sfa-publisher-video-routes-20261104/records.json) be paired with rows from the accepted repository's [SFA Wikidata sample](../../discovery/wikidata-mission-samples-20261102/nextgen/RESEARCH_RECORD.md) or [subsequent simple membership query](../../discovery/wikidata-ent-sfa-second-pass-20261102/RESEARCH_RECORD.md) by exact displayed title, season and episode ordinal?

I read the four official-project method files, accepted publisher roster, SFA press refresh, two WDQS query receipts, the explicit [Wikidata QID review hold](../../discovery/wikidata-ent-sfa-second-pass-20261102/REVIEW_HOLDS.json) and research-result records. Then I compared immutable candidate-route data with the accepted publisher roster field-by-field and evaluated the actual **historical query inputs**. The inputs have pinned SHA-256 digests checked by `validate.py`. No new WDQS request was made; the raw WDQS result bytes are not in this public repository, so this audit can validate accepted **reported** zero-result status and query identity, not reproduce the original network response from first principles.

## Result, without false denominator arithmetic

| Comparison | Exact result | Evidence class | Interpretation |
| --- | --- | --- | --- |
| Paramount+ routes ↔ Paramount+ accepted roster proposal | **10/10 exact title, Season 1, ordinal alignments** | Publisher HTML route metadata vs same publisher's prior metadata | Confirmed data consistency, **not** independent media corroboration or ten admitted Works |
| Historical Wikidata typed query | **0 reported candidate rows**, `Q134592591` | Secondary WDQS report / query receipt | No rows eligible for a title comparison; not evidence of no episodes |
| Historical Wikidata simple `P179` query | **0 reported candidate rows**, `Q134592591` | Secondary WDQS report / query receipt | Same wrong/redirected series key; not independent falsification of publisher roster |
| Current Wikidata series identity | Redirect **`Q134592591` → `Q117350388`** previously observed | Accepted review hold, not a fresh query | Corrected-ID query absent; **cross-system title alignment is untestable** |

The ten comparison records each keep `wikidata_episode_qid=null`, `wikidata_title=null`, `wikidata_alignment=UNTESTABLE_NO_COMPARABLE_ROWS`. They must **not** be reported as ten missing Wikidata episodes, a database completeness score, or a ten-to-zero fictional disagreement. Two historical query outputs against one redirected key are correlated limitations, not independent corroborating negative witnesses.

## Disconfirming/ambiguous observations retained

1. Press Express includes a `Season 2 - Early Release` **photo/media bucket** with code `200`. A naive episode card crawler would generate a fictitious S2 episode 200.
2. Its `Early Release Images` **media bucket** carries Season 1 code `Multiple`; the same crawler would fabricate an episode number from non-episode promotional content.
3. The S1E5 publisher label is `Series Acclimation Mil`; no longer title is inferred from expected wording.
4. The S1E10 official displayed publisher label is `Rubincon`; it is not silently changed to an alternate `Rubicon` spelling.
5. The Wikidata redirect means both reported zero-result queries are inconclusive for the current target entity. A corrected-entity lookup would be **new evidence**, not a reinterpretation of their unchanged historical receipts.

> **Hostile challenge:** Labeling these sources "independent" would launder source lineage: the two Paramount pages are publisher-dependent; the third-party Wikidata snapshots offer **no episode records to compare**. Agreement on ten publisher cards does not establish canonical Work identities, complete coverage, or audiovisual media provenance.

> **Reproduction challenge:** Current public Git evidence contains WDQS query text, receipt metadata and accepted research assertions but not their original raw zero-row response bytes; the historical absence of bindings is therefore **documentary evidence**, not a freshly reproducible system probe in this packet.

## Zero effect and checks

- No canonical Work, source binding, coverage, denominator, reconciliation, projection, or public media rights change.
- No episode source was read. Issue #23 remains the Source↔Work governance/admission blocker.
- `crosswalk.json` is an *SFA research proposal* pinned to accepted source-proposal inputs, not an accepted reconciled Work table.

From repository root:

```sh
python3 proposals/research/sfa-wikidata-crosswalk-audit-20261104/validate.py
python3 -m unittest discover -s proposals/research/sfa-wikidata-crosswalk-audit-20261104 -p test_validate.py -v
python3 tools/validate.py
```

The explicit regression tests reject invented Wikidata episode QIDs, false exact cross-system alignment, code-200 episode promotion, title correction, wrong ordinals, independent-source laundering and all governance bypasses.

**Next frontier:** A distinct, preregistered, bounded WDQS query against verified current series `Q117350388` could test whether candidate rows now exist, but any result would remain third-party discovery metadata pending review. True audiovisual CLOSE_READ still requires governed accepted Source↔Work admission and lawful primary media access.
