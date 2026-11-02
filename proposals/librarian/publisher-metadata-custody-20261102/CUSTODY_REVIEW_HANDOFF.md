# Librarian handoff: Paramount+ public-roster response custody (proposal only)

**As-of:** 2026-11-02 UTC. **Accepted baseline:** `main`
`c7a14ddb62dfa45d5d01855952d9e562c1af21de`.
**Scope:** source/Work **identity metadata** and publisher provenance, not
episode-content inspection, semantic evidence, or global reconciliation.

## Actual collection and checks

An LLM operator collected four anonymous, public Paramount+ season-guide
responses over HTTPS, without signing in. All four final requests returned
HTTP 200, `text/html; charset=utf-8`, no redirects. The server Date header
for the final responses was `2026-11-02T18:28:40Z`; the local check finished
by `2026-11-02T18:28:46Z` UTC. `curl --compressed` saved **decompressed**
response-body bytes to private transient scratch, not the repository. This
distinction matters: SHA-256 values below do not digest the gzip wire stream,
any response headers, JavaScript-loaded follow-up requests, or audiovisual
content. Exact URL, candidate JSON digest, body digest and byte counts appear
in [`receipts.json`](receipts.json).

| Official publisher guide | Candidate subset checked | Decoded HTML bytes | SHA-256 prefix |
| --- | ---: | ---: | --- |
| [TOS Season 1](https://www.paramountplus.com/shows/star_trek/episodes/1/) | 5 | 318,777 | `9fa560890bbd` |
| [TNG Season 1](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/) | 3 | 315,030 | `5b9132f196b9` |
| [TNG Season 4](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/4/) | 1 | 315,431 | `d9c10b219ae7` |
| [TNG Season 5](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/5/) | 1 | 315,886 | `9ae0eb5b7319` |

The private HTML includes JSON-LD `TVSeries` → `containsSeason` →
`TVSeason` → `episode`/`TVEpisode`. A local deterministic comparator parsed the
JSON-LD and checked **exact season-page episode-number/title pairs** for all
ten candidate slots already declared in the existing TOS/TNG proposal JSON.
The four JSON-LD `TVSeason.name` fields explicitly stated `Season 1`,
`Season 1`, `Season 4`, and `Season 5` respectively; none of the four
snapshots exposed a `seasonNumber` in that object. The comparator requires a
matching parseable season name or season number and rejects any **conflicting**
declared season number, even when every title/episode number matches. No
discrepancy was observed among those ten *publisher-local* title/slot pairs.
The comparator also checked exact candidate JSON bytes and source body
digests and requires no additional Python dependencies. The comparison is
replayable only while the exact private snapshots remain available:

```sh
python3 proposals/librarian/publisher-metadata-custody-20261102/check_local_custody.py \
  --snapshot-dir /path/to/private/captured-html
```

Expected output includes `checked_total: 10`, `human_review:
NOT_PERFORMED`, and `accepted_effect: NONE`. A fresh HTTP fetch **cannot**
be presumed byte-for-byte identical to this response; pages, personalization
and server-rendering can change, and captured bytes were **not durably
escrowed**. The page included normal anonymous-session `Set-Cookie` headers;
these headers were neither published nor authenticated as a protected
reviewer's evidence.

**Executed checks on 2026-11-02:** The four real private captures returned
`checked_total: 10` with four `LOCAL_BYTE_AND_JSONLD_SLOT_MATCH_NOT_ADMITTED`
results and `accepted_effect: NONE`. A separate copy with its TOS HTML
truncated to one byte was **rejected** with `snapshot digest mismatch for
tos-s1.html` (exit 1). The existing publisher candidate validator retained
`PUBLISHER_ROSTER_CANDIDATE`, and all 15
`tests/test_verified_episode_roster.py` unit tests passed. These are **local
program checks**, not independent human or media review.

Auditor hardening subsequently added fd-based `O_NOFOLLOW`/`O_NONBLOCK`
snapshot opening, a pre/post-open inode/device/type check, and a bounded
`MAX_SNAPSHOT_BYTES + 1` read instead of the earlier potentially racing
`lstat`/`read_bytes` pair. A later pass also anchored candidate JSON reads
to the repository directory using no-follow directory/file descriptors,
with a separate 1 MiB candidate limit; this rejects symlinked parent
directories as well as final-file symlinks before comparing digests.
Eleven synthetic regressions passed, including
`TVSeason.seasonNumber=99` despite matching episode data, conflicting season
name, missing season identity, symlinked/oversized snapshot and candidate
inputs, and an end-to-end synthetic matching receipt. The original four
private captures were replayed successfully against the final hardened checker
on 2026-11-02: `checked_total: 10`, all four responses
`LOCAL_BYTE_AND_JSONLD_SLOT_MATCH_NOT_ADMITTED`, `human_review:
NOT_PERFORMED`. The corrupted capture failed on the earlier run; it was not
replayed again after this last candidate-reader change.

## Limits: this is a collector receipt, not independent review

- **Operator receipt only:** this agent collected the response bytes and ran
  the local comparator. No separately accountable human collector/reviewer
  identities or signed review exist; do **not** manufacture a
  `publisher_episode_metadata_review` document to satisfy the validator.
- **Publisher metadata only:** exact HTML bytes and matching JSON-LD establish
  what the publisher **listed** at that retrieval. They do not establish a
  complete production/broadcast/streaming roster or that anyone watched an
  episode. No Source-to-Work **content** binding, `FULL_TEXT_AVAILABLE`,
  `CLOSE_READ`, `AUDITED`, accepted Work, continuity assertion or denominator
  follows.
- **No persistent byte custody:** the public repository contains digests and
  locators, not the copyrighted publisher page. The temporary snapshots may
  disappear; durable, rights-compliant private escrow would be a separate
  operational step. A digest without a retrievable exact byte snapshot is a
  historical collector claim, not independent proof.
- **Pilot and multipart ambiguity:** publisher Season 1 puts *The Cage* at
  TOS S1E1, whereas other order conventions place *The Man Trap* first;
  this is compatible with *The Cage* being the original unaired Pike pilot,
  not proof of a canonical episode ordinal. TNG *Encounter at Farpoint*
  has multipart presentation/counting implications. These need explicit
  reconciliation and source-attributed ordering conventions.

> **Hostile challenge:** A matching SHA-256 only binds these bytes to the
> operator's receipt. It cannot establish independent human attestation or
> that publisher JSON-LD is accurate about original broadcast dates or
> identity. The site may serve a different response by region, session,
> edition, or later revision. An internal comparator is not an independent
> content witness.

## Source-family normalization recommendation — not accepted

Current proposals contain at least three **literal** independence-group
names that could be mistaken for independent publisher families:

| Observed proposal family | Example proposal | Cautious interpretation |
| --- | --- | --- |
| `publisher:paramount` | TOS/TNG Paramount+ and TOS Pluto TV | Common corporate publishing-family label; not multiple independent confirmations |
| `paramount-franchise-publishing` | SNW/VOY Paramount+ batches | Likely a naming alias at corporate-lineage level; resolve via reviewed alias record |
| `publisher:startrek.com` | TNG StarTrek.com official metadata bundle | Different editorial domain, apparently shared franchise-publishing lineage; editorial/data derivation unresolved |

Do **not** count one Paramount+ listing, one Pluto TV listing and one
StarTrek.com summary as three independent observations merely because their
hostnames or proposal strings differ. Equally, do not assert that the three
pages necessarily copied the exact same upstream data unless actual source
lineage is shown. Recommend a future **reviewed corporate-family alias map**
with distinct fields for `(raw_independence_group, corporate_lineage,
editorial_source, upstream_feed, independence_assessment)` and an explicit
`UNRESOLVED` value when feeds are unknown. Treat these as potentially
dependent during cross-source hypothesis tests until an accountable reviewer
documents independent production of the facts. Preserve all original raw
group strings; do not silently rewrite historical proposal evidence.

This proposal **does not** change registries, publisher groups, schema,
accepted `main`, coverage, Work identifiers, external crosswalks or public
Explorer behavior.

## Required next gates

1. An accountable independent reviewer receives the exact private HTML
   captures under appropriate rights and validates the ten page-local pairs,
   their scope, ordering conventions and presentation variants. A new HTTP
   retrieval alone is not the same exact snapshot.
2. Record a real, distinct collector/reviewer attestation using
   `schema/verified-episode-roster.schema.json` and
   `tools/validate_verified_episode_roster.py` with `--snapshot`. That tool
   still returns **not admitted** for a valid receipt.
3. Project authority separately decides if a metadata-only identity roster
   should be admitted. Episode-content access, evidence-ledger records and
   source bindings remain different subsequent gates.
4. The Librarian and Auditor review source-family aliasing and challenge
   false cross-domain independence before any accepted normalization.
