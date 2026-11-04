# Isolated HELD publisher-literature LCARS preview

**Proposal only. Not an accepted Explorer route, index, deployment or Work projection.**

This directory contains an opt-in static HTML preview, script and compiled
metadata sidecar for ten source-local publisher edition observations:

- Five eBook product metadata rows from draft [PR #494](https://github.com/thebrazenbeard/trek-data-core/pull/494), Simon & Schuster source family.
- Five nonfiction hardback artbook product metadata rows from draft [PR #497](https://github.com/thebrazenbeard/trek-data-core/pull/497), Titan Books source family.

Each upstream publisher counts as one source family. The publisher source
reads are reported in the draft PR records, not newly independently repeated
here. The `Unification` attribution anomaly remains visibly HELD. The page
does not render publisher descriptions, covers, external images, book contents,
private owner files or speculative canon claims.

## Run a voluntary local preview

From the repository root:

```bash
python3 tools/build_held_publisher_draft_preview.py --check-preview
python3 -m http.server 8000 --bind 127.0.0.1
```

Open locally:

`http://127.0.0.1:8000/proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.html`

No draft JSON is fetched until **Show 10 HELD metadata leads** is selected.
Click **Clear preview** to remove rendered cards. The page references the
version-pinned accepted Explorer CSS for LCARS appearance; the script and
JSON have separate immutable SHA-256 cache/digest pins verified by tests.

Rebuild (requires both exact pinned draft Git commits available locally):

```bash
python3 tools/build_held_publisher_draft_preview.py --write-preview
python3 -m unittest tests/test_held_publisher_draft_preview.py
node --test tests/test_held_publisher_preview_ui.mjs
```

If either draft source changes, the build fails until the source receipt and
semantics are re-reviewed. The browser fails closed if the preview JSON differs
from its script-embedded digest. Do not repin solely to silence validation.

Nothing in this proposal changes `explorer/index.html`, `explorer/app.js`,
the accepted `explorer/index.json`, or the Pages publishing allowlist. A future
public integration would require explicit research acceptance, separate
source/rights review, integration tests and deployment authorization.
