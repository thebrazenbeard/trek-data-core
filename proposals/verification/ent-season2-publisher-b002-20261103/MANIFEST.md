# Enterprise Season 2 B002 — Paramount+ episode cards E11–E20 (held)

**Role:** Enterprise series source-local researcher.

**Selected accepted main:** `8744c1dd234fa1e3ad3eb34951399b34f5fe9c6f` (2026-11-03).
**Scope:** ten original publisher cards, no admitted Work, public synopsis, image or coverage effect.

## Primary source actually inspected

[Official Paramount+ *Enterprise* Season 2 episode guide](https://www.paramountplus.com/shows/enterprise/episodes/2/) was directly read for displayed S2E11–S2E20 cards. An HTTP 200 first-party retrieval returned **311,909 HTML bytes**, SHA-256 `ad950d0c81e82a6ffc5cb94aca6fbb69ab231d865d957d78cb334ae317245532`. This is a dated transient response receipt, not an immutable archived publisher document; raw HTML is **not committed**. Exact per-card <h2> titles, episode ordinals, short description UTF-8 SHA-256, literal publisher mentions, source-local Paramount video links and same-card `thumbnails.cbsig.net` image URL leads were inspected. Publisher prose, image bytes and audiovisual episodes were not copied/read.

| Publisher card | Source-relative context hold |
| --- | --- |
| S2E11 *Precious Cargo* | Rescue and romance are attributed to publisher description, not a viewed episode |
| S2E12 *The Catwalk* | Eight-day refuge remains a publisher narrative claim |
| S2E13 *Dawn* | Encounter/landing not corroborated from footage |
| S2E14 *Stigma* | T'Pol's reported illness is not a separately verified medical/AV fact |
| S2E15 *Cease Fire* | Archer's negotiating role is a publisher description |
| S2E16 *Future Tense* | **Appears** to be a corpse: not a confirmed death or human identity |
| S2E17 *Canamar* | Publisher calls the arrest **mistaken**; no guilty/criminal identity |
| S2E18 *The Crossing* | Proposed consciousness exchange is not evidence of actual identity transfer |
| S2E19 *Judgement* | Tribunal **accusation** is not established conspiracy or guilt |
| S2E20 *Horizon* | Mayweather's childhood freighter is source-relative biographical narration |

The ten original, independently worded synopsis drafts, ten source-local video URLs and ten exact source-local thumbnail URLs are HELD for later review. Video URLs are discovery locators, not watched footage. No public media license or hotlink permission is inferred. The publisher family is a single source lineage, not ten independent corroborators. The fact that records mention people or species does not resolve global entity identity or on-screen truth.

## Source and reconciliation boundary

The accepted B001 predecessor covers S2E1–E10 (`legacy:s2:ent:000`–`009`), and is SHA-pinned by both accepted observation and compiled-record bytes: `547eae257037f2888ccd9eaee50795eed494d9ef02cfcda5ca0d0645a79458af` / `d71c0e01c6e60c60222b3fd39dd9c21943f581d9816b4063d96b1b26ae897a9d`. This batch owns exactly `legacy:s2:ent:010`–`019`; cross-row swaps and predecessor overlap fail. Both batches remain source-local; neither resolves global Work, image rights, or accepted coverage. Discovery source catalog and Enterprise S2 26-card seed remain independently pinned.

```bash
python3 tools/build_ent_publisher_cards_s2_b002.py --check
python3 -m unittest tests.test_ent_publisher_cards_s2_b002
python3 -O -m unittest tests.test_ent_publisher_cards_s2_b002
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

> **Hostile challenge:** Exact CBS thumbnail URLs are only publisher card image pointers. An image may be incorrect, rights-unreleased or later changed. Same-host image swaps and claim-frame/slot mutations are rejected, but the archive lacks authenticated full audiovisual evidence and no semantic continuity conclusions follow.

**Next source-only frontier:** S2E21 `The Breach` through S2E26 `The Expanse` after a fresh accepted-main and duplicate check.
