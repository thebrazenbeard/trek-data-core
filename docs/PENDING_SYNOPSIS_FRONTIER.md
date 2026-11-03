# Pending publisher-description release frontier

`tools/audit_pending_synopsis_release.py` is a **read-only, nonpublication**
gate for two accepted *proposals*: 18 Simon & Schuster literary description
paraphrases and 10 *Scouts: Asteroid Blasters* YouTube-search-description
paraphrases. It does not create an Explorer data file, modify a Publisher
Synopsis release, grant art rights, bind global Works, or advance coverage.

Run:

```bash
python3 -B tools/audit_pending_synopsis_release.py
python3 -B tools/audit_pending_synopsis_release.py --require-ready
```

The first prints a deterministic status report without copyrighted source
passages, cover URLs, or the proposed paraphrase text. The second exits **2**
while documentary prerequisites are missing, deliberately allowing downstream
automation to refuse an accidental release. Structural/input drift fails with
an error rather than being relabeled as approved research.

At accepted `main` `35eb90b`:

| Lane | Source-only proposals | Current public directory matches | Missing gates |
| --- | ---: | ---: | --- |
| Literary expansion | 18 | 0 | Separate exact-text editorial review receipt; accepted source-local directory rows |
| Scouts Asteroid Blasters #1–10 | 10 | 10 | Source page observation (search snippets alone are insufficient); separate exact-text editorial review receipt |

The existing 23 reviewed publisher-description overviews (9 literary, 14
film) and separately published 14 reviewed **Short Treks / Very Short Treks**
descriptions are independently rebuild-checked by this adapter and left
unchanged. Those 14 are **not** the proposed *Scouts: Asteroid Blasters*
descriptions. Total approved display overviews on this accepted main: **37**.

## Future review and release boundary

New reviewer receipts must be separately authored, source-relative, and
explicitly code-pinned by SHA-256 after review. The adapter requires exact
review-request, source-observation, source-locator, and paraphrase digests,
reviewer/provider/runtime descriptions, and effects all set to `NONE`.
Simply adding a receipt JSON cannot release anything. Even a code-pinned
receipt is **not cryptographic proof of reviewer identity, human review,
rights clearance, primary-work reading, or authorization to deploy**.
The Scouts page-observation hold is **intentional and unconditional** on this
historical search-result-only packet: future rendered first-party source-page
observations must supersede it, and a separately reviewed adapter change must
lift that gate. A pinned editorial receipt by itself never lifts that hold.

An independent auditor must challenge the exact future submission; the
Librarian must accept source-local directory metadata without silently
resolving Work identity; a separate versioned display compiler, explicit
release decision, and the manual Pages workflow remain distinct downstream
gates. The Shorts source pages must actually be inspected before any
description is labeled source-verified. Images and complete copyrighted
works stay outside this release contract.
