# PR82 Windows case-collision preservation crosswalk (PROPOSED / HELD)

Source: accepted GitHub `main@3028765359001b90bc3e6b5c1835ee283b326e91`, tree `3028765359001b90bc3e6b5c1835ee283b326e91`, complete recursive Git-tree response (`truncated=false`). This is an **inventory and proposed reversible path mapping**, not a performed migration, source-read custody, or permission to merge/deploy. No original blob is deleted or rewritten. All destination names are distinct under NFKC/casefold. Git blob SHA-1 identifies repository objects, **not** an independently retained source-byte SHA-256.

Collision groups: **8**; distinct original blobs: **16**. All modes are preserved in this proposed mapping. To execute later, copy/move each exact blob to the proposed destination in a separately reviewed migration, validate byte/object identities, preserve historical Git lineage, then prove native Windows checkout on the exact candidate. Retain this crosswalk as a provenance artifact. The old names remain in accepted main until separately authorized.

| Original path | Proposed unique destination | Git blob SHA-1 | Mode | Size (bytes) |
| --- | --- | --- | --- | ---: |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1507db0.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1507db0--gitblob-34a5ba81dec1.md` | `34a5ba81dec1532bf9078dcd7df31543e88fd6d2` | 100644 | 5959 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1507DB0.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1507DB0--gitblob-f437a64bfe00.md` | `f437a64bfe0007f1cace062f16da7d17ca74b5ff` | 100644 | 1467 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1a9ade2.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1a9ade2--gitblob-10c03ec02c6c.md` | `10c03ec02c6cd8943b5ab79432f690d61bb9a494` | 100644 | 5474 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1A9ADE2.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1A9ADE2--gitblob-d495a7ec17e5.md` | `d495a7ec17e50c243fdb1a20c536b3cb74cf0c6c` | 100644 | 1077 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1c209a4.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1c209a4--gitblob-436ef93980fa.md` | `436ef93980fa2c08b8c908bdab381a2834158cd7` | 100644 | 1366 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1C209A4.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-1C209A4--gitblob-9842be5854d1.md` | `9842be5854d13a24393a4d140f0600bc056a883a` | 100644 | 1448 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-20ea175.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-20ea175--gitblob-04548c621428.md` | `04548c62142847085597e2b9e564d98022e52aee` | 100644 | 6569 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-20EA175.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-20EA175--gitblob-47b016698de6.md` | `47b016698de6cf10000037812c2d5d72486b98c6` | 100644 | 2438 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-a21c997.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-a21c997--gitblob-75ac1432ea32.md` | `75ac1432ea32a91e3803860230caa6c4a8417f7a` | 100644 | 7327 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-A21C997.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-A21C997--gitblob-25fb80e501d9.md` | `25fb80e501d90719fc452771a4d6e21718a9e163` | 100644 | 3424 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-d822243.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-d822243--gitblob-9690076fa9b1.md` | `9690076fa9b1f7be38f97101efac997185019396` | 100644 | 9212 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-D822243.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-D822243--gitblob-e0828b55c49f.md` | `e0828b55c49f54611e9f500cd6c0c9356c72ea61` | 100644 | 2146 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-dca65c1.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-dca65c1--gitblob-0eefac861f53.md` | `0eefac861f53c9ee04f980801af29f9bcafad97c` | 100644 | 5856 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-DCA65C1.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-DCA65C1--gitblob-69fe79c43451.md` | `69fe79c4345119fe5a7d1808efe2917e6368ef35` | 100644 | 1474 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-e61dc46.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-e61dc46--gitblob-c3a02bd6daad.md` | `c3a02bd6daadf05c67ff1a216a918dfc19a1f4b2` | 100644 | 5067 |
| `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-E61DC46.md` | `reconciliation/audits/architecture-bootstrap-001/DELTA-PR82-E61DC46--gitblob-309ef677d10c.md` | `309ef677d10c36b9c2ed4932aa54519e9e171fdb` | 100644 | 1364 |

## Hold and verification

- **HELD** under Director issue #23 and portability PR #603; this document is not accepted research coverage.
- Independently verify all 16 source blob objects, the eight collision groups, proposed destination uniqueness, and a lossless 16-to-16 bijection against the exact Git tree.
- Validate the resulting Git tree using the checker at the candidate's exact head, then perform real native Windows checkout tests (including path length, symlink behavior, Git config, and long-path policy). WSL-only tests are insufficient.
- Obtain independent hostile review and explicit per-effect authorization before any migration merge or Pages action.
