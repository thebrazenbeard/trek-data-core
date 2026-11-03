# Next gate — separate literary candidate synopsis display

`tools/build_lit_overview_candidate_release.py` is an intentionally
non-publishing compiler scaffold. It reads the **v2-corrected** exact
18-candidate request built by `tools/build_lit_modal_corrected_request.py` and
will reject any attempt to generate `explorer/literary-candidate-overviews.json`
until a **separately authored model-editorial review receipt** exists at
`proposals/reviews/model-editorial-lit-overviews-18-20261103/receipt.json`.

The receipt must pin the corrected v2 request SHA-256 and the exact 18
`(candidate_work_id, publisher_edition_url, original_paraphrase_sha256)` tuples;
every text must have independent source-page editorial review. There is no
release receipt at this checkpoint, so a deliberate `--check` failure is the
correct result.

The future sidecar would be **additional publisher candidate cards**, not new
rows in the immutable 1,214-row discovery ledger and not a promotion of an
unadmitted Work. No publisher cover images are included. The Explorer has not
been taught to consume this sidecar yet. A separate vetted UI change, pinned
asset hashes, CI, and explicit Pages deployment are required for visible change.

Prototype tests exercise a simulated receipt in memory only. Such a fixture
is **not** real editorial approval or permission to display publisher text.

The v1 editorial request remains solely for historical audit. Its two
identified modal inaccuracies are superseded and must never be displayed.
The v2 builder delegates to the unchanged strict v1 source validator,
retaining closed-field, ISBN, private-path and cover-locator checks.
