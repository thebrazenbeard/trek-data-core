# Literary publisher/distributor verification — Ring of Fire and five memoirs

**Role:** LIT. **State:** PROPOSAL_ONLY. **Observed:** 2026-11-03 UTC. **Previous independent tranche:** Draft PR #261, non-overlapping.

I directly opened the **four official Simon & Schuster product pages** for *Star Trek: Strange New Worlds: Ring of Fire* and the **five specific Penguin Random House/Titan Books paperback pages** for the fictional autobiographies of Kirk, Picard, Janeway, Spock, and Sisko. On each edition page I checked title, author, format, ISBN, imprint, on-page publication date, and page count or runtime. The nine checks match the respective existing Librarian candidate bundles:

- `proposals/librarian/ring-of-fire-editions-20261102/records.json` (four ISBN-specific sources);
- `proposals/librarian/prh-star-trek-autobiographies-20261103/records.json` (five ISBN-specific sources).

The distributor's own descriptions and the publisher's *Ring of Fire* description were read, then **six concise original synopsis paraphrases** were written, each specifically labeled `PUBLISHER_DESCRIPTION_PARAPHRASE` and tied to that candidate Work's page. These are **not** novel/memoir text close reads or claims that events objectively occurred in the fiction. One page describing a fictional autobiography is evidence of the distributor's description, not eyewitness evidence for the book or story-world truth.

Primary locators are in `observations.json`. All nine pages are official publisher/distributor inventory observations, but share only **two upstream source lineages**. The PRH selected paperback page may visibly advertise hardcovers/eBooks with **different publication dates and page extents**; those other formats have **not been verified by ISBN in this tranche**. The proposed Kirk/Picard/Janeway boxed set remains a container, **not** an additional independent literary Work.

The pages were read using a rendered web reader, **without authenticated raw HTML byte custody**. No page content hash is invented; the source bundle's older HTML hashes were not revalidated in this reading. Any site changes require a new observation date/sidecar. No source work bytes, scanned art, cover image, or long promotional passage are committed.

## Explicit limits

- `SOURCE_BOUND=false`, `FULL_TEXT_AVAILABLE=false`, `CLOSE_READ=false`; no literary scene evidence or accepted coverage.
- No source-bound source Work identities, accepted global identities, or candidate-to-canonical reconciliation.
- No ISBN edition-family completeness, no artwork display permission, no private book-artifact equivalence.
- No automatic acceptance even though the nine **edition-page metadata fields** were directly verified.

## Verification

`validate.py` pins and checks `observations.json` against a reviewed raw SHA-256, the two accepted Librarian discovery proposals, per-ISBN locators, allowed statuses, six work-level synopsis labels, and all negative coverage gates. Tests live in `tests/test_lit_ring_memoir_publisher_verification.py` and exercise identity, ISBN, URL, synopsis, and acceptance mutation rejection. Approval, merge, and publication are separate human decisions.
