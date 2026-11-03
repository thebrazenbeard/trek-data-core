# TNG B012 — Season 1 final four Paramount publisher cards (held proposal)

**Role:** TNG source-local research worker. **Exact accepted `main` at branch creation:** `2070b0153228272b5dd667b0a23465ff49a95a5f` (2026-11-03 UTC). This is a proposal and does not change accepted research, governed Source↔Work identity, coverage, the Explorer, or public artwork/synopses.

## Actual primary source reread

I reread the entire rendered [Paramount+ *Star Trek: The Next Generation* Season 1 episode guide](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/) and directly accessed the first-party 316,180-byte HTML response on 2026-11-03. For each of its last four cards I inspected the literal title, visible `S1 E#`, publisher's short description, and that card's own HTML `<img src>` thumbnail URL. I fingerprinted the HTML-decoded, trimmed publisher description (SHA-256) and retained no copyrighted description copy or raw webpage bytes. The byte length is **not** a repository-custodied response hash or a stable source edition.

| Previously unadmitted discovery row | Current publisher card | Accepted B004 same-family title/slot overlap |
| --- | --- | --- |
| `legacy:s1:tng:021` | *Skin of Evil* — S1E23 | `lead:0043`; enriched card metadata, **not** new title/slot verification |
| `legacy:s1:tng:022` | *We'll Always Have Paris* — S1E24 | None; new source-local title/slot recheck |
| `legacy:s1:tng:023` | *Conspiracy* — S1E25 | None; new source-local title/slot recheck |
| `legacy:s1:tng:024` | *The Neutral Zone* — S1E26 | `lead:0040`; enriched card metadata, **not** new title/slot verification |

The accepted B011 author reviewed S1E13–E22 and ended at `legacy:s1:tng:020`. Accepted B004 had separately rechecked E23 and E26 from the *same Paramount corporate publisher family*, under **different local seed IDs**. Those older records are not independent corroboration, and the current four card-rich observations neither silently merge those IDs nor count them as four new title/slot verifications. The B012 compiler byte-pins accepted B004 observations, B011 observations, B011 compiled records, and the 1,214-row discovery catalog. It rejects any duplicate source-local ID, unacknowledged E23/E26 overlap, changed earlier state, wrong ordinal, or title.

## Source versus interpretation

Four description fingerprints and four independently worded one-sentence **held editorial synopsis drafts** are stored separately. They are *claims about short publisher descriptions*, not authenticated audiovisual close reads or assertions that a fictional event objectively occurred. Literal source-relative mentions deliberately retain the exact published naming boundary:

- S1E23 mentions **Enterprise** but does not identify the officer killed; no invented name.
- S1E24 explicitly says **Captain Picard**.
- S1E25 explicitly says **Captain Picard**, **Commander Riker**, **Earth**, and **Starfleet**.
- S1E26 explicitly mentions **Romulans** and **Americans**; no identities for the frozen people are inferred.

Four **exact card-bound `thumbnails.cbsig.net` URLs** are held as asset locators. No image bytes were copied, and URL discovery is not license/admission/hotlink permission or publication. The compiler pins the full URL to its specific source card and rejects same-host image swaps, plausible new synopsis prose, source-unsupported mention aliases, false HTML/video custody, and all Work/coverage/publication promotions.

**Ledger semantics:** four richer publisher-card observations; **two** genuinely new source-local title/slot rechecks, **two** enrichment-only overlaps with B004, **zero** independent corroborations, **zero** admitted Works/full episodes, **zero** accepted close reads, **zero** public synopses/artwork, **zero** Explorer changes. Legacy `UNVERIFIED_METADATA` labels in the discovery catalog remain untouched until separately governed integration.

> **Hostile challenge:** A current streaming guide slot does not establish broadcast/cut identity; the official short description and the older discovery bundle share upstream publisher lineage. Exact hashes pin metadata observations, not audiovisual works, and machine validation cannot itself vouch for original paraphrase fidelity.

## Deterministic reproduction

```bash
python3 tools/build_tng_publisher_cards_b012.py --check
python3 -m unittest tests.test_tng_publisher_cards_b012
python3 tools/validate.py
```

**Next frontier:** TNG Season 2 official guide card inventory after checking accepted source-local lanes for duplicates. For true scene semantics and accepted coverage, authenticate and fully read the actual episode or script in a source-governed workflow, with reviewer admission. Do not automatically publish held summaries or image leads.
