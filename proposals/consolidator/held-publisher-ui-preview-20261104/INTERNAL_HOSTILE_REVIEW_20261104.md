# Internal hostile review — local HELD publisher edition preview

**Review class:** INTERNAL_REVIEW by the implementer, not independent audit,
source reading or formal verification. **Base local commit:** `847bc4b`.
**Accepted main examined:** `3028765359001b90bc3e6b5c1835ee283b326e91`.

> Could a reviewer re-pin JSON with the title of one book and the first-party
> URL of another, while retaining `HELD` badges and passing envelope checks?

**Falsified initial implementation.** A same-Simon-and-Schuster-family URL
swap was accepted even when JSON was rehashed to simulate a carelessly
repinned artifact. Original browser JSON SHA-256 pin prevented this without
code changes, but semantic defense-in-depth failed. Added exact per-edition
source-local ISBN/title/creator/URL pins in the preview consumer. These pins
do not merge candidate identities globally or assert fictional truth.

> Could a rehashed preview include a nonsense publication date, a negative
> page extent, or attach the `Unification` author anomaly to the wrong edition?

**Confirmed weakness in local commit `8ddfdac` after a separate immutable
re-review.** The external report was relayed by the Director; reviewer
provider/runtime are not captured here, so the report itself remains a
secondary REVIEW lead. I independently reproduced its failing behavior in
the local Node DOM harness: a rehashed `2099-99-99` publisher date rendered all
ten cards (expected zero). Added exact typed per-ISBN publisher date, extent,
and anomaly-state pins, plus four red/green mutation cases (invalid date,
HTML-looking date, negative extent, misplaced anomaly). All now fail closed.

> Does `0 admitted Works` on a draft card read like a claim about the current
> entire corpus even after accepted main advances?

**Ambiguous wording corrected.** The card now says **No Work admission from
this edition**, the tally says **0 Work admissions from this preview**, and
historical main-branch counts are labeled with their exact snapshot commit.

> Can five products from one publisher be counted as five independent source
> witnesses or used to inflate accepted coverage?

**Rejected by review scope and tests.** Five ISBN rows belong to one
Simon & Schuster family, five to one Titan Books family; the two publisher
families are separate, but individual products are not independent
corroboration. Browser payload requires exact two source families, five rows
each, no `accepted_*` or coverage effects. No compilers or denominators change.

> Can payloads inject HTML, external images, credentials, unapproved downloads,
> or arbitrary off-site requests?

The dynamic renderer uses `textContent` and locally created text/link nodes,
not `innerHTML`; external source URLs are individually pinned to reviewed
publisher product locators. Page CSP sets `img-src 'none'` and `connect-src
'self'`; the only automated data fetch is the same-origin JSON following a
manual click, with `credentials: 'omit'`. There are no image elements, model
requests or third-party scripts. Publisher links navigate only on a user's
direct selection. **No real browser network trace was obtained:** the
available Playwright package lacks its Chromium executable; tests exercise
the actual module with a controlled DOM/network seam and static source audit.

> Can a draft-only HTML and JSON be swept into GitHub Pages accidentally,
> or will a new unexpected `explorer/*` asset break unrelated releases?

No: all preview files live under `proposals/consolidator/`.
`.github/workflows/static.yml` uploads only `path: explorer` and has a strict
`find explorer -mindepth 1` allowlist; no production `app.js`, `index.html`
or Pages workflow edits were made. Regression tests check these facts.

> Would a changed draft source silently update a visually plausible preview?

No: source Git commit SHA and raw `records.json` SHA-256 are pinned in the
Python builder. The generated JSON has a separate browser SHA-256 pin; the
script and accepted Explorer CSS have versioned URL digests tested against
their actual bytes. Changed inputs or assets require explicit re-review and
repinning; tests reject rehashed semantic spoofing in important identity and
admission dimensions.

**Residual limits:** This is a source-relative metadata-only review preview.
The compiler did not independently re-fetch publisher pages, authenticate
private books, inspect full book text, clear artwork rights, or reconcile
global Work identity. Any future publication needs independent research
acceptance and release authorization.
