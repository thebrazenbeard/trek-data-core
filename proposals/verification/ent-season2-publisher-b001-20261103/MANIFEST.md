# Enterprise Season 2 B001 — ten official Paramount publisher cards (held)

**Role:** Enterprise source-local worker. **Exact accepted `main` baseline:** `e5bfab953a9da961fd9d7ebc5d94b432ebca8fbc` on 2026-11-03 UTC, with independently reviewed Enterprise S1 B001 PR #360 and S1 B002 PR #365 both **merged**. Enterprise S1 E22–26 B003 [draft PR #367](https://github.com/thebrazenbeard/trek-data-core/pull/367) was open at branch creation. This proposal neither assumes acceptance of that branch nor introduces an implicit S1–S2 Work identity.

## Primary publisher surface directly read

I directly retrieved and read the [official Paramount+ *Enterprise* Season 2 guide](https://www.paramountplus.com/shows/enterprise/episodes/2/) on 2026-11-03, including HTTP 200 first-party HTML response of about 312 KB, containing 26 episode cards. I inspected the first ten card blocks (`<h2>` title, displayed episode number, decoded short description, and same-card `<img src>`). These publisher-description texts were fingerprinted SHA-256 but **not copied** into GitHub; original raw page bytes and image bytes were **not archived**. Ten newly worded short synopsis candidates and exact CBS thumbnail URL leads are **held**, not publicly released assets.

| Source-local ID | Paramount card | Critical source-relative frame |
| --- | --- | --- |
| `legacy:s2:ent:000` | S2E1 *Shockwave Part II* | Publisher says `Part II`; proposed continuation of S1E26 *Part I* remains **unresolved**; no cross-season global Work link. |
| `legacy:s2:ent:001` | S2E2 *Carbon Creek* | Publisher says **TPol relates a tale** and frames historic contact as her **claim**, not verified fictional history. The exact publisher token `TPol` is retained, not silently rewritten as `T'Pol`. |
| `legacy:s2:ent:002` | S2E3 *Minefield* | Publisher plot claim only, no authenticated audiovisual depiction or actual source video custody. |
| `legacy:s2:ent:003` | S2E4 *Dead Stop* | Publisher says Mayweather is found dead; source-relative metadata does **not** establish actual death or later continuity. |
| `legacy:s2:ent:004` | S2E5 *A Night in Sickbay* | Publisher source-relative short description only. |
| `legacy:s2:ent:005` | S2E6 *Marauders* | Publisher source-relative short description only. |
| `legacy:s2:ent:006` | S2E7 *The Seventh* | Description's troubled memories are **not** independently verified past events; publisher renders `TPol`, `Archers`, and `Mayweathers` without identity normalization. |
| `legacy:s2:ent:007` | S2E8 *The Communicator* | Mistaken-for-spies is a **suspicion**, not evidence that Archer/Reed are spies. |
| `legacy:s2:ent:008` | S2E9 *Singularity* | Behavior is a publisher claim, not a clinical or semantic diagnosis. |
| `legacy:s2:ent:009` | S2E10 *Vanishing Point* | Hoshi **questions her identity**; no actual split, deletion, or replacement is inferred. |

The accepted source-local discovery catalog SHA is `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc` (1,214 candidates); ENT S2 discovery bundle SHA is `b3ba6c175202d0bd55b711a850a939af6aee2786d0900bc1365cbd109086ef84` (26 publisher-listed cards). Accepted S1 B001 observations/records byte SHAs: `761f45a956f8fc409f2c3a80273c9e0d6ba479310ac536729760cef10716de4b` / `4a48f7136eebff4693fb516bdc3af9bd320af3f2670abfbd492e48816b4e9fc0`. Accepted S1 B002 observations/records: `ce21bf57f9863915e612f46d9e81cc15139433b909a48b6e659c03add5a324b4` / `88996d6a16d52d6ea82faeccbc01cf97b924b8657d2f78139f2ec131d2e01ae0`. The compiler enforces all prior byte/source-only states, immutable card-specific publisher descriptions, original synopsis hashes, exact literal mention arrays, claim frames, exact CBS image links, and new S2 local ID/slot bindings.

## Evidence and effects

Ten `entity_mentions_source_relative` arrays are literal **publisher-description strings** only, with no transcript, on-screen depicted action, objective fictional truth, or global character identity inferred. Ten `source_claim_frame` values explicitly hold descriptions as narration, memory, death report, suspicion, or identity-question contexts when the publisher text demands distinction. Ten original synopsis drafts are not public publisher copy and must receive human/editorial approval before any display. Held `thumbnails.cbsig.net` URLs are artwork **discovery locators** only, without image download, verified content, hotlink permissions, or public redistribution.

**Quantities:** ten first-party source-local title/slot/description observations; ten held synopsis drafts; ten held artwork URL leads; zero independent family corroborations; zero full episode video or transcript reads; zero governed Source/Work admission; zero cross-season Work links; zero accepted coverage, entity identity promotion, public synopsis/artwork, or Explorer change.

> **Hostile challenge:** Reusing Paramount for both seasons is not an independent witness. The publisher’s part labels, character storytelling, reported memory, apparent death and identity doubt are not proof of global continuity, settled diegetic events, or actual episode footage. A valid-looking CBS URL can be a different episode’s image; every card URL is pinned exactly by source-local row.

## Deterministic recheck

```bash
python3 tools/build_ent_publisher_cards_s2_b001.py --check
python3 -m unittest tests.test_ent_publisher_cards_s2_b001
python3 tools/validate.py
```

The independent reviewer should mutate raw duplicate JSON keys under normal and optimized Python, same-host image swaps, narrative frames, false Work/source/privacy rights/coverage claims, source-local IDs and publisher slots, and accepted S1 snapshot lineage.

**Next source-only frontier:** `legacy:s2:ent:010`, S2E11 *Precious Cargo*, after refreshing accepted main and open proposals. Deeper research requires authenticated full episode/script access and governed independent review; this batch does not claim it.
