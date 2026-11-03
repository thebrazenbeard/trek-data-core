# Seven additional private OPF → official publisher edition candidates (HELD)

**Status:** Proposal only. The exact accepted `main` at research start was `969626a`. This is a separate deterministic overlay, not part of the public Explorer, a Work inventory, or edition admission.

I selected seven *different source-local* rows in the already accepted 347-OPF-derived source packet and 39-card held illustrative sample. Each retains its original OPF XML member SHA-256 as previously recorded in accepted metadata, but **the seven original XML bytes were not independently re-hashed in this wave**. The whole owner-held OPF ZIP SHA is a prior independent librarian custody observation, not new verification by this worker. No ebook text was retrieved, copied, embedded, or published.

| OPF source row | Exact official publisher edition candidate | Publisher format / ISBN13 | Important hold |
|---|---|---|---|
| `0110` | [A Time for War, A Time for Peace](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-9-A-Time-for-War-A-Time-for-Peace/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9781982134907) | Gallery Books trade paperback, 9781982134907 | 2019 format is not evidence of private OPF edition identity |
| `0150` | [Yesterday's Son](https://www.simonandschuster.com/books/Yesterdays-Son/A-C-Crispin/Star-Trek-The-Original-Series/9780743419628) | Pocket Books/Star Trek ebook, 9780743419628 | OPF adds “The Yesterday Saga I”; containment/edition unknown |
| `0181` | [Doctor's Orders](https://www.simonandschuster.com/books/Doctors-Orders/Diane-Duane/Star-Trek-The-Original-Series/9780743420013) | Pocket Books/Star Trek ebook, 9780743420013 | OPF sequence hint not an ISBN match |
| `0275` | [Homecoming](https://www.simonandschuster.com/books/Homecoming/Christie-Golden/Star-Trek-Voyager/9780743475631) | Pocket Books/Star Trek ebook, 9780743475631 | **Already recorded in accepted** `ss-three-series-ebooks` as `SSEBOOK-VOY-HOMECOMING-9780743475631`: same publisher family, no second independent witness |
| `0296` | [The Heart of the Warrior](https://www.simonandschuster.com/books/The-Heart-of-the-Warrior/John-Gregory-Betancourt/Star-Trek-Deep-Space-Nine/9780743420488) | Pocket Books/Star Trek ebook, 9780743420488 | OPF #17 local sequence hint, not proven source edition |
| `0326` | [Star Trek: Enterprise: Shockwave](https://www.simonandschuster.com/books/Star-Trek-Enterprise-Shockwave/Paul-Ruditis/Star-Trek-Enterprise/9780743464574) | Pocket Books/Star Trek ebook, 9780743464574 | OPF labels “Novelization”; not evidence of screen transcript or text identity |
| `0335` | [Fire On High](https://www.simonandschuster.com/books/Fire-On-High/Peter-David/Star-Trek-The-Next-Generation/9780743455725) | Pocket Books/Star Trek ebook, 9780743455725 | OPF says “New Frontiers #6”; publisher classifies as TNG #6; preserve disagreement |

Dates and page extents live in the exact pinned source observations. All seven publisher pages are first-party **one Simon & Schuster corporate source family**, not seven independent corroborating data families. The pages were inspected on 2026-11-03; no page HTML snapshots are retained, so product claims must be rechecked if stale. ISBNs are valid publisher *product* edition identifiers, not ISBNs extracted from owner OPF (all seven selected OPF rows have no checksum-valid ISBN candidate). The local OPF XML title/creator labels are retained literally, including historical typos/series ambiguity. A source file may contain multiple Works or share a Work with a different source; **347 OPFs ≠ 347 distinct Works**.

`tools/build_opf_seven_publisher_crosschecks.py` hashes the exact accepted 347-OPF observations, 39-card sample, 1,214-row discovery baseline, and the prior accepted same-family publisher packet before projecting seven HELD metadata cards. There is no global Work ID resolution, complete source text read, artwork release, public import, coverage increase, or source-to-Work admission.

Validation:

```sh
python3 tools/build_opf_seven_publisher_crosschecks.py --check
python3 -m unittest tests.test_opf_seven_publisher_crosschecks -v
```

**Next frontier:** Librarian independently re-hashes these seven exact owner OPF XML members read-only; then separate source/edition reconciliation, semantic containment review and independent publisher-page recheck before any public Work/edition proposal. No public admission is authorized by this packet.
