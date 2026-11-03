# Private TXT ↔ converted OPF bibliographic candidates

Librarian proposal under issue #404. This report is not a distinct-Work count,
edition identity, close read, or coverage admission. Hold #23 remains in force.

## Why a separate title crosswalk

The prior private custody pilot byte-hashed 567 original file observations
(347 LIT and 220 TXT). Filename-stem equality gave 345 LIT→OPF hints and
zero TXT→OPF hints. This new utility compares original TXT basenames with
converted OPF Dublin Core title metadata, without reading or extracting book
prose. All source labels stay transient in memory.

## Owner-controlled Linux/WSL invocation

Run Python inside WSL or Linux, never native Windows Python. Supply previously
verified exact SHA-256 values from the accepted manifest and your private
member receipt. Use output storage on an ext4 private directory.

    python tools/reconcile_private_txt_opf_titles.py \
      --original-zip /private/original.zip \
      --opf-zip /private/converted-opf.zip \
      --member-ledger /private/member-ledger.json \
      --expected-original-sha256 ORIGINAL_SHA256 \
      --expected-opf-sha256 CONVERTED_SHA256 \
      --expected-ledger-sha256 LEDGER_SHA256 \
      --out /private/new-txt-candidates.json

The tool checks both container SHA-256s against the accepted manifest,
requires the exact prior private ledger digest, and binds every original ZIP
name transiently to its ordinal/private SHA-256/size/CRC receipt. Both original
and converted ZIPs are accessed through pinned non-symlink directory
descriptors. The older OPF parser is given only an already-open
procfs descriptor path, so pathname swaps cannot make parsed metadata come
from one ZIP while its reported digest comes from another. The descriptors
are re-hashed/re-statted after processing. A changed input is refused.

Unicode NFKC + casefold + punctuation/space normalization is used for exact
title-string hypotheses. Prefixes, articles, subtitle tokens, authors and
volume identifiers are not guessed away. One TXT to many OPFs, or many TXTs
to the same OPF title, is **AMBIGUOUS**. One-to-one title equality is merely
an **UNVERIFIED CANDIDATE**, never SAME_WORK or same edition. A nonmatch means
NO_EXACT_TITLE_CANDIDATE, not that a Work is absent. The OPF metadata repair
holds remain counted; no conversion partial-completeness claim is made.
The earlier private LIT↔OPF stem candidate ledger remains separate; this
tranche deliberately does not construct transitive TXT→OPF→LIT links.

Output contains only opaque member IDs, OPF ordinals, normalized-title hashes
and statuses. Hashes of guessed labels are not anonymous: private JSON must
never be placed in GitHub, CI logs, Pages, or the Explorer. Output uses POSIX
0600 mode with exclusive creation outside the repo. Windows DrvFS ACL privacy
requires separate verification; use WSL ext4 instead.

## Validation

    python -m unittest discover -s tests -p 'test_private_txt_opf_crosswalk.py' -v

All tests use disposable synthetic ZIPs and include an OPF pathname-swap
regression. Neither archived book texts nor private paths are test fixtures.
