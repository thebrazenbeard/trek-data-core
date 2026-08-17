# Librarian legacy intake / external crosswalk proposal

Status: **PROPOSAL ONLY**. This branch does not modify accepted `main` registry state.

Accepted base when this tranche began: `main@d58359a207da89e812d0a0330558c66774ed1241`.

## Included artifacts

- `ST_LIBRARIAN_CUSTODY_INTAKE_V1.json` — records the two reported ebook ZIP containers as not byte-exposed; creates no Source or Work IDs.
- `ST_LIBRARIAN_COLLISION_RECOVERY_QUEUE_V1.json` — preserves legacy collision counts (84 high-confidence LIT↔TXT candidates, 121 title-overlap groups, 41 suspicious short conversions) without inventing unrecovered memberships.
- `ST_LIBRARIAN_EXTERNAL_CROSSWALK_TRANCHE_001.json` — candidate external metadata for six legacy abstract works.
- `ST_LIBRARIAN_EXTERNAL_CROSSWALK_TRANCHE_002.json` — candidate external metadata for the remaining eight legacy abstract works, including container/contained-work and edition distinctions.
- `ST_LIBRARIAN_EXTERNAL_ADAPTER_ASSESSMENT_V1.json` — STAPI/rtrek/Memory Alpha/Memory Beta lineage and independence rules.

## Non-promotion guarantees

- Legacy `STW-*` identifiers are migration evidence, not accepted `trek-data-core` Work IDs.
- No `STS-*` or other canonical Source IDs are assigned without readable source bytes and hashes.
- External IDs/URLs are crosswalk candidates only.
- Derivative LIT→TXT/OPF/HTML representations have zero independent corroboration weight.
- Container identity, contained-work identity, edition identity, and physical source identity remain separate.
- No copyrighted ebook text or large passages are committed.

## Current blocker

Neither `Star_Trek_OPF_Converted(1).zip` nor `ST ebooks(1).zip` is byte-addressable through the current Librarian surfaces. File Library refresh on 2026-08-17 returned only prior Librarian artifacts, not the ZIP objects themselves.

## Exact continuation frontier

`FIRST_BYTE_ADDRESSABLE_EBOOK_CONTAINER`

When triggered: hash container → enumerate/hash members → classify primary/derivative/container/sidecar → build provenance families → detect exact/normalized duplicates → run integrity checks → only then propose Source↔Work bindings.
