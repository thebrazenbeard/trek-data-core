# FILMS — *Star Trek Beyond*: Paramount's film-page metadata

**FILMS source-local research proposal, 2026-11-03 UTC, based on accepted `main@3c0b37564123166bf38bcfa66f018abc4d5c9996`.** One previously registered film candidate (`film-beyond`), one additional first-party film-page locator. This is **not** a new film discovery, film viewing, Work admission, or replacement for the accepted StarTrek.com publisher-description proposal.

## Observed source and claims

Read the distributor/studio's [*Star Trek Beyond* film page](https://www.paramount.com/movies/star-trek-beyond) through a rendered reader. Its **About the Film** area lists year **2016**, rating **PG-13**, genre **Action / Adventure / Science Fiction**, and running time **122 MIN**. Its **Synopsis** describes a rescue mission, Krall's ambush, the crew scattered on an alien world, and Jaylah's help. Its **About the Cast** lists eight performer/role pairs (John Cho/Sulu, Simon Pegg/Scotty, Chris Pine/Kirk, Zachary Quinto/Spock, Zoe Saldana/Uhura, Karl Urban/Bones, Anton Yelchin/Chekov, Idris Elba/Krall), while **About the Crew** names director Justin Lin and writers Simon Pegg and Doug Jung.

`records.json` preserves those **publisher-reported fields**, source-section labels, and a freshly authored, brief synopsis *candidate*. Its source is a separate Paramount page from the accepted StarTrek.com observations, but Paramount and StarTrek.com belong to a related corporate publishing family; they are **not independent witnesses**. The existing accepted film summary already covers *Beyond*; the new value is source-specific runtime, rating, cast-role and creative-credit metadata, plus a competing publisher-description candidate for **future** editorial comparison. No automatic replacement or public release is proposed.

The source page includes a poster image label. It conveys **no** independently verified repository display license; no image URL or pixels are stored here. No raw HTML bytes or authenticated source snapshot were retained; `source_page_sha256=null`. The 122-minute figure is **what the page lists**, not a proven runtime for every theatrical, home-video, streaming, international, or alternate version. The `2016` label is a page year, **not independently verified exact theatrical release date**.

## Hostile checks

> **Duplicate synopsis risk:** `film-beyond` already has a StarTrek.com publisher-derived paraphrase. A second paraphrase from a related Paramount source is a candidate for comparison, not independent confirmation or an automatic Explorer replacement.

> **Runtime ambiguity:** The listing says 122 minutes without a cut/medium identifier. Assigning it to every edition, or treating streaming schedules and cut lengths as identical, is unjustified.

> **Credit ambiguity:** The eight featured cast pairs are only the eight *displayed on that page*, not exhaustive film credits or identities reconciled across continuities. Role strings such as “Bones” and “Chekov” must remain literal source fields.

> **Release and copyright:** A page's poster, synopsis and marketing rights do not grant independent display rights. A future display synopsis still needs exact-text editorial receipt and the existing release compiler's protections.

> **Snapshot and drift:** The current rendered page was inspected but not captured as immutable raw bytes. A later page edit must require a fresh, separately reviewed proposal rather than silently changing this evidence.

## Effects and validation

All accepted Source/Work, coverage, public synopsis and artwork effects are `NONE`. No film frames, video, audio, screenplay, full copyrighted synopsis, or licensed images are committed. The source-local candidate does not affect the Explorer or any published catalog.

```bash
python3 proposals/films/beyond-paramount-metadata-20261103/validate.py
python3 -O -m unittest discover -s proposals/films/beyond-paramount-metadata-20261103 -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
```

**Next:** independent audit of the exact fields and wording, immutable first-party page custody if permitted, editorial review of any future synopsis release, and edition-specific runtime corroboration before a version-dependent statement.
