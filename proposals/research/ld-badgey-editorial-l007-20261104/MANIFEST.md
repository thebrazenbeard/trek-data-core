# Lower Decks L007 — Badgey first-party editorial source boundary

**Role:** LD audiovisual research worker. **Accepted baseline at selection:** `3028765359001b90bc3e6b5c1835ee283b326e91`. **Date:** 2026-11-04 UTC. **Status:** HELD_EDITORIAL_BOUNDARY_FIXTURE; unaccepted, source-local research only. The articles are first-party franchise **publisher editorials**, not the episode audiovisual primary source. No episode video, transcript, or complete production script was read.

## Publisher sections directly inspected

- Christine Dinh, [*A Who's Who Guide to Star Trek's Megalomaniacal AI*](https://www.startrek.com/news/star-trek-megalomaniacal-ai-guide), StarTrek.com, displayed October 23, 2023. Read the Badgey, AGIMUS and Peanut Hamper sections. The publisher describes Badgey as a Rutherford-created holodeck tutor; a later separation into Badgey, Goodgey and Logic-y; and a transformation/departure in *A Few Badgeys More*. Its separate AGIMUS and Peanut Hamper entries describe the Daystrom confinement.
- Dayton Ward, [*Below Deck with Lower Decks: The Good, the Badge, and the Ugly*](https://www.startrek.com/news/below-deck-lower-decks-407-good-badge-and-ugly), StarTrek.com, displayed October 13, 2023. Read the S4E7 Daystrom and Badgey passages, which present separate subplots; the Badgey account includes an implant recovery, network expansion and dimensional departure.

`observations.json` records seven short original source-relative paraphrases with article heading/paragraph locators, six **local** entity labels, and four held typed assertions about **what the publisher editorial describes**. The two articles have a shared StarTrek.com publisher lineage. Neither supplies an independent full episode witness. Source/Work admission, episode audiovisual close-reading and canon reconciliation all remain absent.

## Hostile test against the Explorer premise

The [draft Badgey Explorer PR #486](https://github.com/thebrazenbeard/trek-data-core/pull/486), inspected at head `dd858712a31319aecc3bde67e0f7dcaf1900f776`, portrays a Starfleet digital prison as a **deliberately invented, alternate-fiction scenario**, prominently disclosed in `explorer/index.html` and the local character reply for confinement questions. That fictional interface premise **must not become a source-backed claim that Badgey is one of the Daystrom detainees**. The publisher editorials identify AGIMUS and Peanut Hamper in Daystrom material while telling a different Badgey story.

> **Hostile identity challenge:** Shared descriptions such as “dangerous AI” or “imprisoned computer” do not make AGIMUS, Peanut Hamper and Badgey interchangeable. Do not transfer a source-relative containment predicate to a different local entity merely because the interface borrows the *idea* of a fictional prison.

> **Hostile negative-evidence challenge:** An editorial's omission of a Badgey arrest is not universal proof that such an event never occurs in any Star Trek source. The conservative result is **not established by the inspected source and explicitly alternate for this interface**.

> **Hostile provenance challenge:** A first-party official *retrospective* has meaningful publisher authority, but it is still interpretive/editorial compression. No publisher summary can be promoted to direct scene evidence without reading the episode or an authorized full script. The two corporate editorials are not independent primary sources.

## Regression expectation and effects

The closest behavior safeguard in PR #486 tests only a broad `Where are you?` conversation. A bounded follow-up regression should probe `Is Badgey imprisoned at Daystrom?` and `Did Starfleet imprison Badgey?`, requiring explicit alternate-fiction/non-canon disclosure and **zero** off-page requests. A separate fixture check should reject any mapping of the editorial Daystrom evidence IDs onto `l007-badgey`, and any attempt to mark publisher editorials `FULL_EPISODE_READ` or emit an episode coverage event.

No copyrighted article text, transcripts, screenshots or source imagery are reproduced here; source body digests and redistribution rights are not established. This packet does not edit the canonical evidence ledger, Work identities, Librarian register, reconciliation decisions, Explorer, or public deployment.

Validation:

```bash
python3 proposals/research/ld-badgey-editorial-l007-20261104/validate.py
python3 -O proposals/research/ld-badgey-editorial-l007-20261104/validate.py
python3 tools/validate.py
```

The L007 validator enforces an exact source-title/URL/byline/date binding, frozen source-relative observations, entity and supporting-evidence mappings, schema key allowlists, a canonical JSON fixture digest, held-status fields, and a pinned PR head/disclosure locator. It exercises ten hostile data mutations (including the four independent review attacks: forged Daystrom incarceration text, arbitrary source URL, injected transcript field, and swapped assertion support) plus a duplicate-key parse test. Explicit exceptions remain active under optimized Python. The digest pins **our local observation fixture**, not the full editorial HTML or the primary episode. This proves only consistency/fail-closed scope of the **local receipt**, not the source article's truth, continued availability or accepted coverage.
