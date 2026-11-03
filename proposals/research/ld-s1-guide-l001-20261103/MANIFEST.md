# Lower Decks L001 — Season 1 full publisher-guide card recheck

**Role:** LD series worker performing **source-local publisher metadata research**, not episode audiovisual close-reading. **Accepted main at selection:** `d07eced8571275fe7f1bb6387935db98f95e0bca` (2026-11-03 UTC). **Status:** unaccepted research proposal. No admitted Source↔Work identity, global character identities, close-read, synopsis approval, artwork license, or coverage event.

## Directly read first-party guide

I opened and read the full ten-card Season 1 listing on Paramount+'s official [*Star Trek: Lower Decks* Season 1 episode guide](https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/1/) during the 2026-11-03 UTC recheck. I read its visible episode titles, `S1 E#` display positions and description blocks, but **did not view any episode video, consult scripts, or retrieve raw HTML bytes or actual poster/thumbnail binaries**. The source body presented title/slot and short editorial descriptions; no complete episode has been accessed or inferred.

| Unadmitted source directory ID | Current Paramount+ guide card | Selected literal description mentions only |
| --- | --- | --- |
| `roster:modern-s1:ld:000` | S1E1 — *Second Contact* | Ensign Tendi; U.S.S. Cerritos; Mariner; Boimler; Rutherford |
| `roster:modern-s1:ld:001` | S1E2 — *Envoys* | Boimler; Mariner |
| `roster:modern-s1:ld:002` | S1E3 — *Temporal Edict* | buffer time; Lower Decks |
| `roster:modern-s1:ld:003` | S1E4 — *Moist Vessel* | Captain Freeman; Mariner |
| `roster:modern-s1:ld:004` | S1E5 — *Cupid's Errant Arrow* | Mariner; Boimler; Tendi; Rutherford |
| `roster:modern-s1:ld:005` | S1E6 — *Terminal Provocations* | Ensign Fletcher; Mariner; Boimler; Rutherford; Tendi |
| `roster:modern-s1:ld:006` | S1E7 — *Much Ado About Boimler* | Mariner; Starfleet Academy |
| `roster:modern-s1:ld:007` | S1E8 — *Veritas* | Mariner; Boimler; Tendi; Rutherford |
| `roster:modern-s1:ld:008` | S1E9 — *Crisis Point* | Mariner; Boimler; holodeck |
| `roster:modern-s1:ld:009` | S1E10 — *No Small Parts* | U.S.S. Cerritos; Tendi |

These are literal **tokens in a distributor's description text**, not verified appearances, dialogue, actions, episode events, in-universe objective facts, global person identity or independent confirmation. Each observation records its own local publisher card entity and evidence ID, type `PUBLISHER_CARD_DISPLAY_AND_LITERAL_DESCRIPTION_MENTION`, with scope `TITLE_SLOT_AND_MENTION_TOKENS_NOT_PLOT_FACTS`. I store **no full publisher description, source quote passage or synopsis paraphrase**. Every synopsis is `HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE`.

## Provenance and artwork hold

The accepted `DISCOVERY_ONLY` directory SHA-256 is `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`, containing these ten rows as `UNVERIFIED_METADATA`; the historical publisher Season 1 CSV SHA-256 is `435dde1dc5e62b8298e1f38bca1e57413f25e9dc1e9acc323603b185220a6132`; and the original discovery observation receipt SHA-256 is `9ea6d99bc63104bfcce9cfa145cc5c8a0e340b9e1b5a8d06639e135ef48a54a4`. Those hashes pin **repository inputs**, not the current publisher HTML or an authorized full episode. The old CSV and current guide share **one Paramount corporate publisher lineage**, so agreement is a same-family recheck, not an independent corroborating source.

No accepted LD Season 1 source-local research recheck or open LD Season 1 draft overlapped these row IDs at selection; the accepted old modern Paramount Season 1 file was discovery, not a governed Source↔Work/close-read batch. Existing Season 2/3 metadata discovery files and other series drafts are separate partitions. No new Work count or research coverage is advanced.

The official guide URL is an **artwork investigation starting point only**. The text source did not authenticate any per-episode image asset URL, bytes, content digest, attribution, redistribution permission or artwork license. Each record therefore holds the page lead, leaves `artwork_asset_url:null`, marks `artwork_rights_status:UNKNOWN_HELD`, and has `public_artwork_effect:NONE`. No images were hotlinked, downloaded or reproduced.

> **Hostile challenge:** A distributor synopsis can misassociate blurb details with a neighboring episode and is not the episode itself. The literal token “Mariner” appearing below a guide card proves a **publisher text mention**, not that a particular globally reconciled person acted in that episode or that the assertion is fictional-world truth.

> **Artwork challenge:** A first-party URL or poster description is not a reusable image license. No asset may be added to Explorer until content provenance, rights and publication authority are independently established.

## Deterministic validation and next frontier

The closed-schema validator checks exact publisher titles, slots, card locators and mention-token lists, the three accepted discovery-artifact SHA-256 receipts, ten distinct local IDs, strict duplicate-key JSON parsing, and explicit synopsis/art/Work/coverage holds. The regression tests reject forged source access, new authenticity keys, narrative-event elevation, unlicensed artwork, metadata rewriting, and raw duplicate keys, including Python optimized mode. No deterministic projection output or global registry was changed.

```bash
python3 proposals/research/ld-s1-guide-l001-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_ld_s1_l001.py'
python3 tools/validate.py
```

**Next LD frontier:** The accepted directory still has discoverable later-season publisher rows. Bounded future guide work must freshly check main/open proposals and keep full audiovisual, semantic, entity reconciliation, synopsis release and licensed artwork separate from this metadata evidence.
