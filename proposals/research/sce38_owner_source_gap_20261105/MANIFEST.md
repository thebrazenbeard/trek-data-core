# S.C.E. #38 — *Orphans* (HELD source gap; no close read)

**Status:** `HELD_SOURCE_ABSENT_NOT_CLOSE_READ`. This is a bounded LITERATURE **owner-archive discovery** result, **not** a full-source literary research batch. It does not advance accepted coverage or canonical source/work identity.

## Evidence actually checked

- Live accepted `main` baseline at worktree creation: `3028765359001b90bc3e6b5c1835ee283b326e91`.
- On Lappy, the owner-private `OneDrive/Documents/Books/ST ebooks.zip` (SHA-256 `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`) contains **573 ZIP members**, including **347 `.lit` files** and **40 S.C.E.-labeled `.lit` files**. Those 40 files represent **36 distinct numbered entries**, numbered **1–37 except #10**, with duplicates under numbers 1, 5, 9 and 13. **No member name matched SCE #38 or *Orphans*.**
- The owner-private `Star_Trek_OPF_Converted.zip` (SHA-256 `0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f`) contains **3,846 ZIP members** and **40 S.C.E.-labeled OPF members**, also 36 distinct numbered labels, maximum #37. **No member name matched SCE #38 or *Orphans*.**
- A case-insensitive filename scan of the **locally synced** `OneDrive/Documents/Books` tree through depth five found no `*orphans*` filename. This is deliberately **not** a claim about every possible cloud, removable or external source.
- The [official Simon & Schuster publisher listing](https://www.simonandschuster.com/books/Star-Trek-Orphans/Kevin-Killiany/Star-Trek-Starfleet-Corps-of-Engineers/9780743480857) identifies *Star Trek: Orphans*, S.C.E. **#38**, Kevin Killiany, ebook ISBN-13 `9780743480857`. **Publisher bibliographic metadata is not owner-held primary source text or proof of the private manifestation's edition/rights.**

## Research interpretation

The evidence establishes a **specific gap in the searched owner-local archive manifestations**, not an absence from all libraries or editions. No novel chapters were processed; no chapter count, span SHA, original narrative synopsis, source-relative evidence, or local entity/assertion is fabricated. No text, ebook bytes, graphics or cover art are exported.

Next literary frontier: acquire or locate an owner-authorized complete S.C.E. #38 full primary source, verify title/creator/edition and content structure, read all actual narrative chapters privately, and generate held, source-relative evidence with a private byte verifier. An alternate complete work in the archive may be assigned separately, but cannot silently erase the #38 gap.

## Validation and effects

```sh
python3 -m unittest tests.test_sce38_owner_source_gap_held -v
python3 -m proposals.research.sce38_owner_source_gap_20261105.validate
python3 -m unittest discover -s tests -q
python3 tools/validate.py
```

**Accepted effects:** `NONE` — no source/work binding, close-read admission, canonical evidence, coverage promotion, identity reconciliation, public Explorer update, remote push, merge, or deployment. This local proposal is audit-ready but not an accepted research result.
