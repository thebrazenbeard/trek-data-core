# DS9 B010 — Season 6 publisher guide, episodes 6–15

**Role:** DS9 source-relative title/slot worker. **Accepted base at selection:** `main@07d0ab4294ede4ff202eb80f4055bc5c676413b2` (2026-11-03 UTC). **Status:** unaccepted proposal; no Source↔Work identity decision, episode viewing, script read, approved synopsis, global reconciliation, artwork/media custody, or research coverage event.

## Direct public publisher-guide read

On 2026-11-03 UTC I freshly read the visible title and `S6 E#` position of ten contiguous cards on Paramount+'s [*Star Trek: Deep Space Nine* Season 6 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/6/). The source's short descriptions were displayed, but this batch stores **neither their text nor paraphrases**. It records only the exact title, streaming-guide slot and page/card locator, compared against already accepted but **unadmitted discovery metadata**. No episode audiovisual source, production script, publisher HTML byte snapshot, release/region variation, or page DOM capture was obtained.

The same corporate publisher family supplied both the earlier discovery CSV and this recheck. Agreement therefore **does not count as independent corroboration**, a newly authenticated Work, or multiple independent source witnesses. The source-directory SHA `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`, publisher Season 6 CSV SHA `328e2df32a5492249a756a23a22eb641d135877cfca930ffc444b005c04b9ef8`, and earlier accepted B006 observations SHA `12bacfb550e3b52ce8e14c591bcc7e258f59e1544bf28fa010ce249f60c96a08` pin **repository inputs only**, not the current Paramount+ HTML or a broadcast cut.

| Source-local directory row | Rendered publisher card |
| --- | --- |
| `publisher:s6:ds9:005` | S6E6 — *Sacrifice Of Angels* |
| `publisher:s6:ds9:006` | S6E7 — *You Are Cordially Invited* |
| `publisher:s6:ds9:007` | S6E8 — *Resurrection* |
| `publisher:s6:ds9:008` | S6E9 — *Statistical Probabilities* |
| `publisher:s6:ds9:009` | S6E10 — *The Magnificent Ferengi* |
| `publisher:s6:ds9:010` | S6E11 — *Waltz* |
| `publisher:s6:ds9:011` | S6E12 — *Who Mourns For Morn?* |
| `publisher:s6:ds9:012` | S6E13 — *Far Beyond The Stars* |
| `publisher:s6:ds9:013` | S6E14 — *One Little Ship* |
| `publisher:s6:ds9:014` | S6E15 — *Honor Among Thieves* |

## Nonduplication and source custody

The accepted B005–B006 Wikidata-lead research partition covered different local seed IDs. Its two Season 6 public publisher-card rechecks are *Favor The Bold* **S6E5** and *His Way* **S6E20**, neither in this tranche. Open Draft PR #290 similarly rechecks the latter two DS9 seed titles; it is a **proposal, not accepted evidence**, and has no S6E6–E15 records. Accepted S7 publisher-card batches (B008 and previous B009) and open Draft PRs #340/#344 concern **Season 7**, not these Season 6 IDs. Do not merge the Wikidata `lead:*` namespace with publisher `publisher:s6:ds9:*` identity merely because a display title matches.

`observations.json` keeps ten separate source-local observations, each `SAME_PUBLISHER_RECHECK_MATCH` with `HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE` and `accepted_work_id:null`. Raw HTML is explicitly `current_raw_html_captured:false`, hash `null`; the branch does not update a canonical Source ledger, Work registry, public synopsis, database, Pages deployment, or coverage ledger.

> **Hostile challenge:** Publisher card positioning is a website presentation, not proof of broadcast ordinal, an exact episode cut, edit identity, script authenticity, plot-event truth, or global Work equivalence. A guide listing and the prior CSV share lineage and cannot independently corroborate one another.

> **Hostile challenge:** These ten card titles were already discovered in a 1,214-row directory. The new batch provides a current publisher-page **source-relative recheck**, not ten new Works or ten completed source reads. Close-read and semantic completion counters must remain unchanged.

## Reproducibility and next gate

`validate.py` compares exact accepted input SHA-256 fingerprints, literal title/slot/locator pairs, the prior B006 source-card subset for non-overlap, and closed schemas that forbid any source-rights, Work, synopsis or coverage promotion. The raw JSON reader rejects duplicate keys before parsing a dict; the test harness exercises raw duplicate-key attacks in both standard and `-O` Python modes, alongside forged source-family, artifact, page-capture, Work and coverage fields.

```bash
python3 proposals/research/ds9-s6-middle-b010-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_ds9_s6_b010.py'
python3 tools/validate.py
```

**Next DS9 source-card frontier:** Other Season 6 publisher guide spans remain candidate-only, but advancement beyond card metadata requires independently qualified audiovisual/script source custody, Source↔Work admission and neutral close-reading under the Director's hold. No Season 6 title/slot card alone satisfies those gates.
