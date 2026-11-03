# Enterprise Season 1 B003 — five final Paramount publisher-guide cards (held)

**Role:** Enterprise source-local worker. **Authoritative accepted `main` at this branch creation:** `90aee8750c87afb8f64fa5d687e76db6e3f1c7aa` (2026-11-03 UTC), now including the independently reviewed and **merged** B001 [PR #360](https://github.com/thebrazenbeard/trek-data-core/pull/360). B002 [PR #365](https://github.com/thebrazenbeard/trek-data-core/pull/365), S1E12–E21, remains a separate open proposal at this checkpoint. This B003 branch is unaccepted, changes **no** Work identity, accepted ledger, Explorer publication, or governed coverage.

## Direct first-party research

I reread the [official Paramount+ *Enterprise* Season 1 episode guide](https://www.paramountplus.com/shows/enterprise/episodes/1/) on 2026-11-03 and separately fetched the raw first-party HTML over HTTP 200 (approximately 311 KB, 25 episode cards). For all five final cards I actually inspected their exact displayed S1E# and `<h2>` title, decoded *publisher short description*, and exact same-card CBS `<img src>` URL. The raw page bytes are **not archived**, and the response length is not a reproducible source edition hash. The five descriptions are stored only as UTF-8 SHA-256 fingerprints; original copyrighted wording is **not** copied into this public repo. Five freshly worded one-sentence summaries and five thumbnail locator URLs are explicitly **held**, not published assets.

| Accepted discovery ID | Paramount display card | Epistemic/identity hold |
| --- | --- | --- |
| `legacy:s1:ent:020` | S1E22 **Vox Solis** | The live official guide and accepted source-local discovery both say **Vox Solis**. A competing *Vox Sola* spelling is **not adjudicated** as the same Work or canonically corrected here. |
| `legacy:s1:ent:021` | S1E23 *Fallen Hero* | Publisher mentions `Archer`, `Vulcan Ambassador`, and `Mazar`; no global identity links. |
| `legacy:s1:ent:022` | S1E24 *Desert Crossing* | Publisher mentions `Archer` and `Trip`; no episode scene is authenticated. |
| `legacy:s1:ent:023` | S1E25 *Two Days and Two Nights* | Publisher mentions `Risa` and `Enterprise`; no full-source close read. |
| `legacy:s1:ent:024` | S1E26 *Shockwave Part I* | **Part I** label is source-as-stated; any cross-season continuation relation remains unresolved, not automatically a merged Work. |

Accepted 1,214-row discovery catalog SHA-256: `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`; accepted Enterprise S1 25-row discovery bundle SHA-256: `79a1347c46e73fc74120353c43a819d891b1406e4ea91fa5d20793ba7040c486`. Accepted Enterprise B001 observations SHA-256: `761f45a956f8fc409f2c3a80273c9e0d6ba479310ac536729760cef10716de4b`; B001 records SHA-256: `4a48f7136eebff4693fb516bdc3af9bd320af3f2670abfbd492e48816b4e9fc0`. The compiler rejects any deviation from those accepted snapshots; its five source-local IDs `020–024` cannot collide with merged B001 `000–009` or open B002 `010–019`.

## No silent promotions

`entity_mentions_source_relative` lists are exactly literal words in **Paramount publisher descriptions**. They do not establish episode dialogue, actions depicted on video, statements by fictional persons, global character identity, or fictional truth. Held original synopsis drafts are *editorial reinterpretations of short publisher descriptions only*. Held `thumbnails.cbsig.net` URLs are **artwork discovery leads**, not downloaded images, copyright permissions, image authenticity or publication. The validator pins each complete URL to its one exact card so a different image on the same host cannot be substituted.

**Counters:** five source-local publisher title/slot/description rechecks, five held original synopsis drafts, five held image locator leads, one unresolved title variant, one unresolved multipart continuation link; zero independent corroborations; zero audiovisual episodes watched; zero governed Source/Work admissions; zero accepted close reads; zero global identity reconciliations; zero public images/synopses, zero Explorer or coverage mutation.

> **Hostile challenge:** The currently displayed streaming guide is not an audiovisual copy, verified script, broadcast chronology, or a license to republish CBS imagery. A *Part I* label and an alternate spelling are not grounds for silent cross-work identity fusion. Publisher claims remain publisher-relative until different admissible source evidence actually supports them.

## Deterministic reproduction

```bash
python3 tools/build_ent_publisher_cards_b003.py --check
python3 -m unittest tests.test_ent_publisher_cards_b003
python3 tools/validate.py
```

Adversarial regressions reject raw duplicate keys in normal/optimized Python, same-host swapped images, unreviewed summary changes, forged titles/ordinals/mentions, accepted B001 source drift, duplicate IDs, and fictitious rights/private source custody/Work/coverage claims.

**Next frontier:** Enterprise Season 2 first-party guide, **after** fresh accepted `main`/open proposal collision checks. A separate full audiovisual/text source qualification and independent semantic audit remain required for deeper episode-level evidence.
