# Prodigy publisher episode metadata: conservative source-local observations

- Batch: `prodigy-startrek-publisher-20261102`.
- Status: **DISCOVERY / CANDIDATE_METADATA_ONLY**, never accepted Work/Source binding or research coverage.
- Observed **2026-11-02** from downloaded first-party StarTrek.com article HTML, HTTP 200. Full raw source HTML is deliberately **not** in this public Git repository.
- Publisher source A: [Season 1 episodes 11–20 physical-media release](https://www.startrek.com/news/star-trek-prodigy-season-1-episodes-11-20-release). Its labeled episode list yields **10** titles with relative ordinal 11–20. **It is not a full Season 1 roster.**
- Publisher source B: [Season 2 now available](https://www.startrek.com/news/star-trek-prodigy-season-2-now-available). Its numbered entries 201–220 yield **20** titles with source-local season 2 ordinal 1–20.
- Total: **30 publisher-listed episode-slot observations**, not an independently deduplicated increase in canonical episode count. Other candidate sources (including Wikidata) may describe the same works.
- Official [Season 1 volume 1 release](https://www.startrek.com/news/star-trek-prodigy-season-1-volume-1-release) corroborates that its physical-media volume has ten episodes, **but does not provide a numbered title roster**. Season 1 episodes 1–10 are an explicit sourcing gap here. Distributor storefront title listings can be proposed in a separate tranche after source-independent ordinal/edition reconciliation.
- `s1b.csv` and `s2.csv` preserve only source-licensed *short titles* and season-relative ordinals; generated `*/bundle.json` uses the strict `publisher_episode_roster_proposal` schema. Null canonical Work and Source binding IDs are intentional.
- `index.json` preserves page URL, HTML byte count and SHA-256 and exact emitted CSV SHA-256 per source. Body hashes establish the captured local bytes' identity; they are **not publisher signatures, independent content authentication, full text availability, or episode evidence**.
- No transcript, dialogue, synopsis, media, protected image, user-preference weighting, or fictional continuity proposition is imported. Source independence is `publisher:paramount` for both articles.
- Deterministic offline recheck: `python tools/build_prodigy_publisher_discovery.py --check`. To reproduce from separately retrieved original pages, put the HTML in a temporary directory as `s1b.html` and `s2.html`, then use `python tools/build_prodigy_publisher_discovery.py --ingest-dir TEMP_DIRECTORY`; this rebuild is strict about source canonical URL, exact ordinal sequence and normalized short titles. Retrieved page changes legitimately alter body hashes and may alter observations; review such differences before acceptance.

## Unresolved before possible admission

1. Cross-reference each source-local slot against accepted canonical Works, other publisher/distributor rosters and Wikidata candidates; do not count them additively by default.
2. Bind exact accessible audiovisual sources for any later close reading; none were watched or structurally indexed in this batch.
3. Cover Season 1's first ten title slots from an appropriate primary, fully numbered publisher listing. Do not infer them from this sparse sample, summaries or title mentions.
4. Reviewer must inspect the source documents and confirm title/ordinal extraction before the Consolidator proposes accepted state changes. No user merge/deploy authorization is presumed here.
