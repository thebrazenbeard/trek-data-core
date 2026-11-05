# Enterprise Season 1 E01–E06 — first five Paramount+ publisher cards (HELD)

**Research lane:** ENT. **Evidence class:** a full first-party publisher HTML *guide* was structurally processed; only five card descriptions were actually close-read and paraphrased. **Not:** viewing episodes, admitting Source/Work identities, audiovisual CLOSE_READ, canonical synopses, global reconciliation, or changing public Explorer.

## Exact source receipt

- https://www.paramountplus.com/shows/enterprise/episodes/1/ returned HTTP **200**.
- Response Date `Wed, 04 Nov 2026 23:58:50 GMT`; observed `2026-11-04T23:58:50.902109+00:00`.
- Entire response **311,889 bytes**, SHA-256 `e4c46b3b56ecaf2bc20ac562b69e94be7fbc9321ade1939e080ccaefc0d543f4`.
- All **25** structured guide cards parsed and fingerprinted; normalized 25-card SHA-256 `a6ca94bbdfbe7a32e304e3bc9c0f4ce516e639f9d8f505af97fb82b92df8a9c4`.
- Only the **first five** complete publisher paragraphs (1,012 characters total) were read for new, short source-relative paraphrases. No original paragraphs or raw HTML were committed.
- Exact complete proposed `records.json` SHA-256 `e6b1b49ad21151dc25c1307b305ca28dd8a2bac015d26d794731b02298c98439` is pinned by the validator, in addition to all five independently pinned original-paraphrase SHA-256 values; any text edit requires a fresh audit.

| Guide card | Source episode badge | Official title | Description line | Source paragraph SHA-256 |
|---:|---:|---|---:|---|
| 1 | 1 | Broken Bow - Part 1 and 2 | 1500 | `f9cdbebc04c72787fb2d4fbd27a18b7328f560a67e48f95360c0842a439bcd04` |
| 2 | 3 | Fight or Flight | 1528 | `13e04b4fee6e130a6e24d101a6f6867ea7f718bbdf1d971db04f66ee3e7ef113` |
| 3 | 4 | Strange New World | 1556 | `cacf492e4be677014615a61dbbd655e64112ba3b2372a20129ab04587f2ff101` |
| 4 | 5 | Unexpected | 1584 | `21e7fe97c79abfb50c4e6f7d08214ab1b480d559f2c7b0280eab38ca88c5f8ea` |
| 5 | 6 | Terra Nova | 1612 | `2ee93b94196b39c376dc5d6259bbb34dd76cf2947833837b5205af30c8448832` |

## Crucial structural falsifier: guide cards ≠ canonical episodes

The publisher labels its first *single guide card* **“Broken Bow - Part 1 and 2”** with episode badge 1. The second card has badge **3** while its analytics/display ordinal is **2**. All subsequent badge labels run 3–26, while analytics/display ordinals run 2–25. It would be an error to silently relabel the second guide card episode 2 or claim this 25-card page contains only 25 episodes. Whether the two-part pilot is one Work, two Works, or an edition-specific container is **not resolved by this packet**.

## Source-relative semantic holds

- Card 1 mission to deliver a Klingon messenger and seek human autonomy does not independently prove arrival or the state of Vulcan–human relations.
- Card 2 publisher dilemma between crew safety and intervention is not evidence that either choice or outcome occurred.
- Card 3 publisher attributes distrust and distorted perceptions to pollen exposure. Perceived events are not objective facts without independent supporting depiction.
- Card 4 the publisher describes Trip's unusual pregnancy during aid to another ship. This description is not an independent biological or mechanism study.
- Card 5 publisher's “evolved” characterization of Terra Nova descendants is not a scientifically verified evolutionary mechanism.

All five retained as `PUBLISHER_DESCRIBES` assertions attached to local publisher-card entities. The previous accepted Season 1 `proposals/discovery/legacy-paramount-season1-20261102/ent/bundle.json` is CANDIDATE metadata, not a separate complete primary reading or independent corroboration. Both derive from the Paramount+ family.

## Validation and exact next frontier

- `python3 proposals/research/ent/enterprise-s1-first5-official-guide-20261104/validate.py` validates the exact source receipt, pilot card/badge distinction, five fingerprinted descriptions, 5 local entity/evidence/assertion chains and protected-effect holds.
- `python3 -m unittest discover -s proposals/research/ent/enterprise-s1-first5-official-guide-20261104 -q` runs hostile claim/identity/date/coverage tests.
- Full repository Python suite and `python3 tools/validate.py` are required before clean commit.

**Coverage:** 5/25 publisher card **description proposals HELD**, not 5 episodes watched and not 5 accepted CLOSE_READ events. **Next:** cards 6–10 (publisher badges 7–11), first-party source read and provenance checks. No merge, push, deployment or copyrighted-media publication in this packet.
