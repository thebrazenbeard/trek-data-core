# Enterprise S1 B001 — ten Paramount+ publisher-guide cards (held proposal)

**Research lane:** Enterprise series source-local worker. **Accepted `main` at branch creation:** `91d1af747d728345fa86fdfbb5ab7228327516af` (2026-11-03 UTC). None of these records changes the accepted source/work ledger, actual audiovisual episode coverage, governed reconciliation, or public Explorer.

## Direct source retrieval and actual read

On 2026-11-03 I read the [official Paramount+ *Enterprise* Season 1 episode guide](https://www.paramountplus.com/shows/enterprise/episodes/1/) and separately retrieved the first-party HTML response (HTTP 200; approximately 311 KB; 25 visible episode cards). For the first ten display cards I parsed and inspected each `<h2>` title, displayed `Episode #` ordinal, HTML-decoded short publisher description, and the card's own `<img src>` from `thumbnails.cbsig.net`. I retained only SHA-256 digests of publisher description strings, exact source-relative literal mentions, original synopsis paraphrases, and ten *unfetched* artwork URL locators. Neither raw HTML nor publisher descriptions nor image bytes were archived in the repository; the response byte count is **not** a stable source digest or full episode read.

| Accepted discovery source-local ID | Direct first-party card | Source-specific issue |
| --- | --- | --- |
| `legacy:s1:ent:000` | S1E1 *Broken Bow - Part 1 and 2* | **One combined publisher card**, no separate E2 displayed; multipart/work identity unresolved |
| `legacy:s1:ent:001` | S1E3 *Fight or Flight* | Publisher title/slot source recheck only |
| `legacy:s1:ent:002` | S1E4 *Strange New World* | Publisher title/slot source recheck only |
| `legacy:s1:ent:003` | S1E5 *Unexpected* | Publisher title/slot source recheck only |
| `legacy:s1:ent:004` | S1E6 *Terra Nova* | Publisher title/slot source recheck only |
| `legacy:s1:ent:005` | S1E7 *The Andorian Incident* | Publisher title/slot source recheck only |
| `legacy:s1:ent:006` | S1E8 *Breaking The Ice* | Publisher title/slot source recheck only |
| `legacy:s1:ent:007` | S1E9 *Civilization* | Publisher title/slot source recheck only |
| `legacy:s1:ent:008` | S1E10 *Fortunate Son* | Publisher title/slot source recheck only |
| `legacy:s1:ent:009` | S1E11 *Cold Front* | Publisher title/slot source recheck only |

The accepted `explorer/discovery-catalog.json` SHA-256 is `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc` (1,214 unadmitted candidates), and the accepted Enterprise S1 discovery bundle SHA-256 is `79a1347c46e73fc74120353c43a819d891b1406e4ea91fa5d20793ba7040c486` (25 source-local episode slots). The compiler pins those exact accepted snapshots, the ten expected row IDs, displayed slots, publisher-description hashes, literal mention arrays, per-card artwork URLs, synopsis paraphrase hashes, and the E1 multipart hold. Existing older open PRs are proposals, not accepted evidence. No independent source-family corroboration is claimed.

## Field-specific evidence boundaries

Each `entity_mentions_source_relative` list consists solely of names literally present in the *publisher's short description*. It is **not** a verified utterance, filmed depiction, transcript, identity crosswalk, in-fiction truth, or complete episode read. A string such as `Trip` is preserved as written, not automatically resolved globally to another name. Each of the ten `original_synopsis_draft` fields is newly worded and **held** for human/editorial review; no publisher prose is copied. Artwork URLs are **held discovery leads only**, not evidence of copying, license, hotlink permission, or public image publication. URL-to-card binding uses a full exact image locator pin, not merely a trusted hostname.

**Quantities remain separate:** 10 publisher-card metadata rechecks; 10 editorial synopsis *drafts*; 10 held artwork URL leads; 1 unresolved combined multipart card; 0 invented E2 cards; 0 audited audiovisual episodes; 0 admitted governed Works; 0 cross-work entity reconciliations; 0 independent corroborations; 0 publicly published synopses or image assets; 0 Explorer updates.

> **Hostile challenge:** A corporate streaming guide title/slot does not independently prove episode cut, broadcast chronology, fictional events, dialogue, or part-specific identity. A current publisher short description can also differ from actual source footage. Treat every summary and art locator as a held proposal until independently audited; do not turn a second reference to the same Paramount lineage into corroboration.

## Deterministic validation

```bash
python3 tools/build_ent_publisher_cards_b001.py --check
python3 -m unittest tests.test_ent_publisher_cards_b001
python3 tools/validate.py
```

Tests reject changed publisher titles, ordinals, metadata fingerprints, literal mention identities, original synopsis drafts, same-host swapped artwork, false Work/AV/coverage/publication claims, changed accepted source snapshots, duplicate rows and raw duplicate JSON keys both normally and with `python -O`.

**Next unclaimed source-local frontier:** `legacy:s1:ent:010` — *Silent Enemy*, Paramount guide S1E12, then S1E13 onward. Recheck accepted `main` and open proposals again before taking that tranche.
