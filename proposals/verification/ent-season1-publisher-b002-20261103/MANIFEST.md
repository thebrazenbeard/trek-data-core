# Enterprise Season 1 B002 — S1E12–E21 official publisher cards (held)

**Role:** Enterprise source-local research. **Accepted `main` baseline:** `7e0c56e5bbef70296de034e5283ed6217e6e7f91` on 2026-11-03 UTC. This is a **draft proposal**, not accepted source/work research or a public Explorer deployment.

## What was read

I actually reread the complete [first-party Paramount+ *Enterprise* Season 1 guide](https://www.paramountplus.com/shows/enterprise/episodes/1/) on 2026-11-03, including a 311,043-character UTF-8 raw HTML response received HTTP 200 with 25 displayed cards. I inspected the ten S1E12–E21 cards in their separate `<div class="episode">` blocks: exact title, displayed `Episode #`, decoded short description, and each card's `<img src>`. The raw response is ephemeral, **not archived**, and its length is not a stable source version. Each extracted short publisher description was SHA-256 fingerprinted but its original copyrighted text is **not committed**. I drafted ten newly worded, **held** one-sentence synopses and recorded ten exact first-party CBS thumbnail URL *leads only* (no images fetched or copied).

| Source-local discovery ID | Publisher S1 card | Source-bound note |
| --- | --- | --- |
| `legacy:s1:ent:010` | E12 *Silent Enemy* | Trip and Reed are literal publisher mentions |
| `legacy:s1:ent:011` | E13 *Dear Doctor* | Source says `Dr. Phlox`; not automatically global identity |
| `legacy:s1:ent:012` | E14 *Sleeping Dogs* | Klingon vessel and named landing party from publisher description |
| `legacy:s1:ent:013` | E15 *Shadows of P'Jem* | A publisher-reported blame/removal claim, not audiovisual finding |
| `legacy:s1:ent:014` | E16 *Shuttlepod One* | Scattered ship remains are a publisher description, not certified destruction |
| `legacy:s1:ent:015` | E17 *Fusion* | Publisher's capitalized `Mind meld` phrase retained literally |
| `legacy:s1:ent:016` | E18 *Rogue Planet* | No unsupported hunted target identity assigned |
| `legacy:s1:ent:017` | E19 *Acquisition* | The publisher calls the raiders `Ferengi` |
| `legacy:s1:ent:018` | E20 *Oasis* | No survivor identities inferred |
| `legacy:s1:ent:019` | E21 *Detained* | `Tandarans` and `Suliban` are publisher words only |

No new independent corporate family was accessed. Open [B001 Draft PR #360](https://github.com/thebrazenbeard/trek-data-core/pull/360) covers different source-local IDs `legacy:s1:ent:000–009` and guide card S1E1+E3–E11. This B002 branch starts at fresh accepted `main`, does **not** include or assume acceptance of B001, and never repeats its source-local IDs. All ten new cards use S1E12–E21, so no multipart gap/Work split is inferred in this tranche. The accepted 1,214-row discovery catalog byte SHA-256 is `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`; accepted Enterprise S1 discovery bundle SHA-256 is `79a1347c46e73fc74120353c43a819d891b1406e4ea91fa5d20793ba7040c486` (25 source-local slots). The compiler pins these prior source snapshots, the current ten exact publisher fingerprints, exact original-summary hashes, literal mention arrays, and full correct-card artwork URLs.

## Strict boundaries

- `entity_mentions_source_relative` records **literal publisher-description text strings**, not an episode utterance, depiction, global entity or fictional truth claim.
- Original synopsis drafts are **held, unpublished summaries of publisher descriptions**, not authenticated full-text or audiovisual close reads.
- Artwork URLs are **unfetched candidate locators only**: neither a copyright license nor hotlink/publication approval nor verified image content.
- **Zero** governed Source/Work admissions, independent corroborations, videos watched, scripts read, episode close reads, entity reconciliations, public summaries/image assets, Explorer updates, or coverage increases.

> **Hostile challenge:** A current streaming listing proves the publisher currently presents a title and description, not that the represented episode has been watched, that any fictional event occurred, or that a synopsis/image is publishable. A plausible-looking card URL from the same host can point to another episode; every row uses immutable exact art-locator pins.

## Reproduce

```bash
python3 tools/build_ent_publisher_cards_b002.py --check
python3 -m unittest tests.test_ent_publisher_cards_b002
python3 tools/validate.py
```

Adversarial tests reject wrong card slots/titles/IDs, duplicate records and raw duplicate JSON keys (normal and `python -O`), same-host swapped images, unreviewed synopsis/mentions, forged rights/private AV custody/identity/coverage status, and altered prior seed hashes.

**Next unclaimed local source frontier:** Enterprise S1E22 *Vox Sola*, ID `legacy:s1:ent:020` — recheck live accepted `main` and open PRs first.
