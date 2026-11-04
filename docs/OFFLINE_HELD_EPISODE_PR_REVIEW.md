# Offline held-episode PR review — no admission or publication

This is a **Consolidator review tool**, not a research batch, canonical
projection, public synopsis release, source binding or coverage event. It
reads exact Git object bytes from eight *unmerged* publisher-guide PR heads
using `git show <full-commit-sha>:<path>` and checks SHA-256 pins. It does
not assume that any branch, PR, source observation or existing HELD synopsis
has been accepted into `main`.

## Snapshot frontier at accepted main `3028765359001b90bc3e6b5c1835ee283b326e91`

| Proposal | Publisher-guide lane | Source-local observations |
|---|---|---:|
| #538 | TNG S2 first five | 5 |
| #551 | TNG S2 next seventeen | 17 |
| #559 | TNG S3 twenty-six cards | 26 |
| #554 | DS9 S2 twenty-five cards | 25 |
| #557 | DS9 S3 observed slots | 24 |
| #560 | DS9 S4 observed slots | 24 |
| #544 | VOY S4 E15–E19 | 5 |
| #558 | Held source-local publisher-note sidecar | 58 |
| **Total candidate observations** | | **184** |

There are **183 pre-existing held promotional-description paraphrases** and
**one withheld combined/multipart identity**. This is not an episode count:
repeated source families, varying card scopes, unresolved identity, omitted
publisher ordinals, and unverified full sources make that denominator invalid.
No observed card is treated as a read episode or an accepted Work.

Two DS9 extraction tranches explicitly preserve missing publisher ordinal
slots: S3 **4 and 26** (#557), S4 **2 and 26** (#560). #560 also records a
**possible source-title/description cross-assignment for ordinals 3 and 4**,
still unresolved. The compiler does not fill gaps, swap descriptions or
declare publisher card titles canonically reconciled.

## Reproduce offline

Use an isolated clone of accepted `main` plus this review branch. Fetch the
draft Git objects into local read-only refs first (no merge required):

```sh
git fetch origin \
  pull/538/head:refs/remotes/origin/review-pr-538 \
  pull/551/head:refs/remotes/origin/review-pr-551 \
  pull/559/head:refs/remotes/origin/review-pr-559 \
  pull/554/head:refs/remotes/origin/review-pr-554 \
  pull/557/head:refs/remotes/origin/review-pr-557 \
  pull/560/head:refs/remotes/origin/review-pr-560 \
  pull/544/head:refs/remotes/origin/review-pr-544 \
  pull/558/head:refs/remotes/origin/review-pr-558

python3 -B tools/review_held_episode_prs.py --check-summary
python3 -B -m unittest tools.test_review_held_episode_prs -v
```

The input manifest `tools/held_episode_pr_sources.json` names **full commit
SHAs and exact packet-byte SHA-256**, not mutable branch labels. A changed
PR head does not silently change the snapshot. If the exact old commit is not
locally available, the command fails closed and tells the operator to fetch
the relevant object; do not substitute a new head without reviewing the diff.

`docs/HELD_EPISODE_PR_REVIEW_SNAPSHOT.json` contains **counts and provenance
only**. It excludes every unpublished paraphrase string. To produce the full
text-bearing reviewer bundle, explicitly choose a new path **outside** the
repository and outside any directory reachable as a repo ancestor:

```sh
python3 -B tools/review_held_episode_prs.py \
  --private-output /private/review-only-held-episode-notes.json
```

The `--private-output` target must have a trusted existing parent and must
not already exist. On POSIX platforms with directory-relative `O_NOFOLLOW`
opens, the tool pins the parent directory by descriptor, rechecks its inode
identity before and after writing, and creates the new file with `O_EXCL`
and owner-only `0600` permissions. A swapped parent symlink cannot redirect
the write into the repository; a detected swap fails closed and cleans up
the new file through the pinned descriptor. This does not defend against
privileged mount replacement or malicious modification of the pinned
directory inode itself.

On Windows or platforms missing these no-follow directory-descriptor
primitives, private output **fails closed by default**. An explicit weaker
compatibility option exists only for a trusted local directory tree without
concurrent mutation:

```sh
python3 -B tools/review_held_episode_prs.py \
  --private-output 'D:\\trusted-review\\held-notes.json' \
  --trusted-output-path
```

That mode rejects observed symlink/junction parents and resolves its target,
but **cannot guarantee** safety against adversarial concurrent directory or
mount replacement. Never use it for untrusted/shared mutable paths.

Do **not** commit that output or expose it via GitHub Pages: it contains
unapproved held synopsis drafts. The repository checks in no such source
text, imported image, episode clip, script, HTML body or transcript.

Counts-only summaries accept only governed typed series/anomaly codes. The
DS9 S4 hypothesis remains `POSSIBLE_TITLE_DESCRIPTION_CROSS_ASSIGNMENT`;
arbitrary draft prose is rejected rather than copied into public metadata.

## Mechanical governance barrier: `SOURCE_BOUND`

The compiler invokes the repository's existing **read-only**
`check_episode_pilot_readiness.py` and records its current result separately
from draft observations. At the pinned accepted main, the diagnostic reports
**zero accepted nonfixture episode Works, zero fully qualified pilot Works,
zero approved projection hashes, and technical prerequisites blocked**.
This does not imply a complete absence of useful discovery leads. It says
those leads have not crossed governed admission gates.

To propose one real nonfixture `SOURCE_BOUND` event, the separate existing
`check_source_bound_readiness.py` requires an independently accepted episode
Work, Source, evidence-bearing Librarian binding with an exact `BYTE_HASH`
basis, rights-valid private source bytes, replayed custody receipt and an
accepted `DISCOVERED` predecessor. Human review and acceptance remain
separate. Source-local promotional guide snippets, even 184 of them, **cannot
provide these prerequisites** or bypass the accepted source-binding/coverage
hold. See `docs/SOURCE_BOUND_EVENT_PREFLIGHT.md` and
`docs/FIRST_NONFIXTURE_EPISODE_PILOT.md`.

## Explicit non-effects

This proposed tool does not touch `registry/authoritative/`, `coverage/`,
`explorer/index.json`, `explorer/search-catalog.json`, `explorer/app.js`,
`explorer/index.html`, public Mission Briefings, credentials, pages deployments
or any PR merge state. It is safe to review the eight unmerged drafts in
parallel with later source-custody work because it never promotes them.
