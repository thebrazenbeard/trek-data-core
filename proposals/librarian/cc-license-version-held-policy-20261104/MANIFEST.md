# HELD — version-exact Creative Commons artwork policy triage

Date: 2026-11-04. Librarian source/artwork lane. **Advisory and test-only, no public release gate changes.** Literal live GitHub `main` check: `3028765359001b90bc3e6b5c1835ee283b326e91`.

## Accepted policy versus actual source claims

Accepted `tools/validate_artwork_release.py` (SHA-256 `402cb3d0620906d8f700bb4335c2e56dea4f7dcb9b396fafc56bef8112d0d35e`) has **zero** `REVIEWED_LOCAL_ARTWORK_PINS`, and its exact `LICENSE_BASES` includes `CC-BY-4.0` and `CC-BY-SA-4.0`, **not** CC BY 2.0 or CC BY-SA 2.0. That is an **application gate limitation**, not proof that the legacy CC 2.0 grants are invalid.

| Accepted held source-only candidate | Source file class | Reported license | Allowlisted by accepted release code? | Deterministic result |
|---|---|---|---|---|
| *Star Trek Beyond* Japan premiere, Dick Thomas Johnson photo | Accepted `explorer/beyond-premiere-photo.json` | CC BY **2.0** | No | `HELD_VERSION_CLASS_NOT_ACCEPTED` |
| *Lower Decks* 2019 SDCC panel, Gage Skidmore photo | Accepted Librarian source-only record | CC BY-SA **2.0** | No | `HELD_VERSION_CLASS_NOT_ACCEPTED` |
| Starfleet OF1 rank insignia attributed to Sano | Accepted Librarian Commons discovery lead | CC BY-SA **4.0** | Yes | `HELD_FILE_LEVEL_RIGHTS_UNVERIFIED` (derivative design/mark risk) |

The 4.0 case is important: passing a version allowlist does **not** clear the exact work, image bytes, underlying trademark/prop design, personal likeness, attribution placement, or reviewer custody. Every row above remains HELD, and the status is not `SOURCE_BOUND`, `WORK`, or semantic coverage advancement.

## Independent legal-code basis (primary sources, read this wave)

- Creative Commons [Attribution 2.0 Generic legal code](https://creativecommons.org/licenses/by/2.0/legalcode) calls itself version 2.0 and specifies original author/title/source/license credit and derivative credit requirements.
- Creative Commons [Attribution-ShareAlike 2.0 Generic legal code](https://creativecommons.org/licenses/by-sa/2.0/legalcode) is a **distinct** versioned instrument with ShareAlike conditions for derivatives; it must not be simplified to ordinary CC BY.
- The [BY 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode) and [BY-SA 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/legalcode) legal codes explicitly identify version 4.0. The 2.0 legal-code pages themselves explain that 4.0 is a newer license option for works authors choose to license; that explanation does **not** retroactively relicense a specific older photo.

> **HOSTILE CHALLENGE:** Renaming `CC-BY-SA-2.0` as `CC-BY-SA-4.0` to satisfy `LICENSE_BASES` would fabricate a rights grant and conceal which obligations govern the original photograph. Conversely, changing `LICENSE_BASES` to allow 2.0 without version-exact attribution, source/photo identity, independent rights review, code-owned pin, and tested release receipts would weaken the actual guardrail. The independent review of publicity, privacy, trademark, and endorsement risks remains necessary under either license version.

## Distinct, no-effect future options

1. **Preserve HELD.** Default with no code or image effects.
2. **Obtain explicit, exact-file written permission.** A rights-holder's independently verified grant, with separate licensing terms, could be evaluated on the accepted `EXPLICIT_WRITTEN_PERMISSION` path. Preserve the **observed** original CC 2.0 metadata; do not relabel it 4.0 or assume a permission document already exists. Reviewed exact image bytes and owner release authority remain prerequisites.
3. **Propose audited CC 2.0 policy support.** Future separately authorized work would need a version-specific legal-code/rights assessment, exact release-receipt schema and code-owned allowlist change, license-specific tests (including adaptations and attribution), source+rights reviewer custody, image digest and UI QA. None of this was done in this packet.

The new metadata-only `tools/check_cc_license_version_held.py` is **not** installed into production release logic and never returns a public `ALLOW` result. It pins accepted input SHA-256s and current gate semantics, tests the exact license string/version and does not allow promotion through an `EXPLICIT_WRITTEN_PERMISSION` label alone. This is materially different from the prior separate CC attribution-text receipt template: it tests which versioned policy route is open or blocked before anyone prepares a release receipt.

## Checkpoint

```bash
python3 tools/check_cc_license_version_held.py
python3 -m unittest tests.test_cc_license_version_held -q
```

No downloaded pixels, rehosting, hotlinks, repo Explorer/Page changes, Work admission, coverage promotion, merge, or deployment. Tests verify the accepted gate has not changed, and the source-file author/license claims remain separate from independent legal/right-to-display conclusions.
