# Explorer original abstract artwork

The five small category backgrounds in `explorer/art-original-*.svg` are **original, procedural, non-narrative placeholders** for episode, film, literary, short-form, and audio discovery cards. They are not Star Trek stills, licensed covers, depictions of a specific story, or evidence that any source was read.

The public category backgrounds retain the renderer's original shapes and colors but omit its three fixed textual labels. The Explorer already renders medium, series, record initials, title, and the non-official-art disclaimer as HTML over the background. Keeping the SVG decorative prevents those two text layers from colliding, especially at 82×118px mobile card sizes. The generator verifies the expected three-label renderer contract before stripping it.

They are generated without external inputs from the already accepted safe renderer at `proposals/librarian/original-nasa-fallback-20261103/tools/render_original_abstract_art.py`. The entry seeds, titles, and medium palette are fixed constants in `tools/build_explorer_abstract_art.py`.

Rebuild with `python3 tools/build_explorer_abstract_art.py`; validate committed bytes with `python3 tools/build_explorer_abstract_art.py --check`. Automated tests enforce deterministic output, safe SVG vocabulary, and exact same-origin CSS references. The GitHub Pages allowlist and committed-byte integrity barrier include precisely these five files.

Independent, source-attributed publisher images and Open Library covers remain behind the existing separate artwork-catalog rights/crosswalk gate and opt-in switch. Display of an abstract background is automatic; display of any claimed external art is **not** automatically authorized, fetched, mirrored, or released by this change.

Research status, callable search index, author/title/source identity and synopsis review receipts are unaffected.

Each visible record placeholder additionally carries an **original, source-local
signal**: eight small CSS bars and a bounded geometric rotation drawn solely
from the displayed record's `directory:<row_id>` or first-party film key.
Edition-only publisher candidates, which intentionally have no artwork lookup
key, use their own source-local `row_id`. The `data-source-local-key` attribute
keeps that mapping inspectable; `data-record-phase` controls only CSS geometry.
The displayed eight-digit value is a reproducible, non-cryptographic **visual
seed**, not a provenance hash, source authentication, cross-work identity, or
thumbnail-coverage result. Hash collisions are possible; the underlying row
identifier remains the authority. If no key exists, the caption says so.

These signals render without network requests or local binary images beyond
the five already released category backgrounds. Visitors may still separately
opt in to the exact-edition jacket preview route under its existing rights
and source receipts; none of the signal marks changes that approval boundary.
