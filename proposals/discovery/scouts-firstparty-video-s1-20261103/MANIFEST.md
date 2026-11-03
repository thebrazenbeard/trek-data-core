# *Star Trek: Scouts* — first publisher-video metadata tranche

Status: **DISCOVERY_ONLY / SOURCE_LOCAL / PROPOSAL**. No accepted Work, Source
binding, audiovisual close read, Briefing, continuity assertion, coverage,
denominator, or global identity decision was created.

## What was read and what was not

- Retrieved the complete first-party [StarTrek.com / CBS Studios Scouts
  announcement](https://www.startrek.com/news/star-trek-60th-2026-fan-centric-celebrations)
  as private HTML. Its canonical publisher URL and wording establish an
  announced **20-installment, 3–4 minute original animated short-form order**;
  this does *not* establish that every announced installment was distributed.
- Retrieved **20 individual YouTube public oEmbed JSON responses** for videos
  currently credited to *Blaze and the Monster Machines*, the Nickelodeon
  channel identified in StarTrek.com's announcement. Each video title includes the *Star Trek: Scouts*
  series tag and either *Asteroid Blasters #1–#10* or *Holodeck Rescues Episode
  #1–#10*. Each exact first-party response has a private byte-body SHA-256
  and length receipt in `source.json`.
- Retrieved six complete TrekCore pages whose YouTube embeds supplied a
  **discovery crosswalk** for nineteen of those video IDs. The twentieth
  (*Asteroid Blasters #10*) was located and verified directly against its
  first-party YouTube video metadata. TrekCore is **not independent supporting
  evidence** for the publisher's content and the six pages are not transcript
  sources. Their source-body consistency receipts are in `source.json`.
- Did **not** download or watch video/audio, read scripts, scrape private
  metadata, establish air order, or verify global franchise canon. Source
  metadata is not audiovisual evidence. No raw publisher article, video,
  iframe content or third-party article text is republished here.

## Identity and numbering boundaries

Two numbered YouTube mini-series strands are visible; both restart at `#1`.
The 20 direct publisher video IDs are distinct link identifiers in this
snapshot, not versioned global Work IDs or verified season ordinals. The
source-local index therefore labels them as *Scouts* **short-form** releases,
not television-episode Work records or a 13th top-level TV Mission.

The YouTube oEmbed titles are the publisher metadata **as retrieved on this
date**, which can differ from the original labels printed in earlier embedded
TrekCore articles. Those title variants have not been silently reconciled.
All first-party properties are one broader Paramount corporate provenance
family, not 20 independent corroborators.

## Files and reproducibility

- `source.json` — 20 first-party title/ID/URL observations, private-response
  hashes and lengths; six discovery crosswalk receipts; full publisher
  announcement receipt; explicit lack of accepted effects.
- `records.json` — deterministic, vetted 20-row public candidate projection.
- `tools/build_scouts_publisher_discovery.py` — strict parser, publisher-account
  check, canonical announcement check, bounded file reads, no-follow output
  directories, deterministic offline recheck.
- `tests/test_scouts_publisher_discovery.py` — source tamper, forged canonical,
  publisher spoof, symlink input/output regressions and source-only status.

The temporary source bodies are deliberately kept outside public Git; they
can be recaptured from publisher and discovery locators, but a new publisher
response may differ from these exact historical SHA-256 receipts. This is a
byte-consistency record, **not cryptographic authentication by the publisher**.

To check the committed outputs without network:

```bash
python3 -m tools.build_scouts_publisher_discovery --check
python3 -m tools.build_unified_discovery --check
python3 -m unittest tests.test_scouts_publisher_discovery tests.test_unified_discovery -v
```

Next frontier: publisher-first, source-hashed *Scouts* Season 2 metadata, and
independent franchise-scope review of the short-form container. Do not fill
unobserved slots from the announcement alone.
