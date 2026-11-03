# Explorer original abstract artwork

The five small category backgrounds in `explorer/art-original-*.svg` are **original, procedural, non-narrative placeholders** for episode, film, literary, short-form, and audio discovery cards. They are not Star Trek stills, licensed covers, depictions of a specific story, or evidence that any source was read.

They are generated without external inputs from the already accepted safe renderer at `proposals/librarian/original-nasa-fallback-20261103/tools/render_original_abstract_art.py`. The entry seeds, titles, and medium palette are fixed constants in `tools/build_explorer_abstract_art.py`.

Rebuild with `python3 tools/build_explorer_abstract_art.py`; validate committed bytes with `python3 tools/build_explorer_abstract_art.py --check`. Automated tests enforce deterministic output, safe SVG vocabulary, and exact same-origin CSS references. The GitHub Pages allowlist and committed-byte integrity barrier include precisely these five files.

Independent, source-attributed publisher images and Open Library covers remain behind the existing separate artwork-catalog rights/crosswalk gate and opt-in switch. Display of an abstract background is automatic; display of any claimed external art is **not** automatically authorized, fetched, mirrored, or released by this change.

Research status, callable search index, author/title/source identity and synopsis review receipts are unaffected.
