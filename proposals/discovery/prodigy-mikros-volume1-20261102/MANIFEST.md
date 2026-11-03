# *Star Trek: Prodigy* Volume 1 — Mikros Animation source-local observations

- **Batch:** `prodigy-mikros-volume1-20261102` (Librarian source discovery)
- **Status:** `CANDIDATE_METADATA_ONLY`; **no** accepted Work, audiovisual source binding, Briefing, coverage or franchise denominator change.
- **Retrieved 2026-11-02:** [Mikros Animation production-studio article](https://www.mikrosanimation.com/en/news/star-trek-prodigy-begins-its-blu-ray-journey/) (HTTP 200). The exact response is 39,863 bytes, SHA-256 `eb60ef3f60e5a466bda79b2c58ac97d3cd63c0c9fd730a82ab6e467169079716`. The raw article remains private in temporary custody; it is **not** committed.
- The article explicitly identifies *Star Trek: Prodigy* Season 1 Volume 1 as the **first ten episodes** and lists ten short title fragments **without per-title ordinal labels in that list**. However, a **separate image caption in the same article** identifies **“Starstruck” `Ep#103`**. That isolated production-style caption label is recorded in `index.json` as same-source metadata: it is **not** a studio-published numbered title roster, official season ordinal for the complete sequence, or independent corroboration. The batch's **source-local positions 1–10 remain inferred from listed order**; no ten distinct audiovisual Works are admitted.
- The article abbreviates the second half of two multipart titles as only “Part II” and “Part 2.” The generated CSV expands these contextually to `Lost and Found, Part II` and `A Moral Star, Part 2`. Both editorial expansions are explicitly recorded in `index.json`; neither is represented as a direct quotation or independently authenticated title.
- Crosscheck: [official StarTrek.com first-volume release](https://www.startrek.com/news/star-trek-prodigy-season-1-volume-1-release) confirms the first-ten-volume identity but **does not independently provide a numbered title roster**. Avoid counting a publicity/producer distribution chain as independent corroboration. The batch uses conservative `publisher:paramount` lineage grouping.
- `mikros-s1a.csv` preserves only short metadata titles and inferred sequence positions; `mikros-s1a/bundle.json` conforms to candidate-only roster schema with null global Work/Source IDs and `UNRESOLVED` completeness. `index.json` stores the captured response SHA/size and CSV hash.
- No copyrighted transcript, episode synopsis, audio/video, long article text, or graphic is included. This is a source-inventory step, **not full-text or close-read research**.

Reproduce offline from the previously retrieved original raw HTML:

```sh
python tools/build_prodigy_mikros_s1a_discovery.py --ingest /path/to/mikros.html
python tools/build_prodigy_mikros_s1a_discovery.py --check
```

The parser fails closed for incorrect/missing/duplicate canonical URLs, changed volume identity, malformed title-list structure, and unsupported data. New site responses legitimately produce new SHA receipts; differences require review.

## Admission blockers

1. Independently verify the **numbered** episode slots and multipart treatment against an authorized primary/distributor episode guide or audiovisual edition. Sequence position in studio promotional prose alone is not official ordinal custody.
2. Reconcile these title observations against already indexed Prodigy S1 E11–20/S2 E1–20 and other source-local candidates **without adding counts or global identity automatically**.
3. Bind an authenticated source edition and perform appropriate content reading before claiming a researched Briefing or audiovisual coverage.
