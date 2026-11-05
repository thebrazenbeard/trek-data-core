# Source-linked original reference-card gallery (HELD)

**Role:** Explorer/website designer. **Dependency:** local cherry-pick `02b3c92` of Librarian source-local rights/field contract `d43c2f10a11758b2ec300c4c783a8f5f239c3944`. Accepted metadata baseline remains `main@3028765359001b90bc3e6b5c1835ee283b326e91`. Neither the contract nor this gallery is merged or deployed.

Six **original procedural SVGs** are deterministically keyed to six accepted source-local record IDs: **2 EPISODE**, **2 FILM**, **2 LITERATURE**. The accepted safe renderer (`render_original_abstract_art.py`) creates only SVG rect/circle/path/text shapes with a medium-specific palette, metadata title, and visible `ABSTRACT PLACEHOLDER · NOT OFFICIAL ART` notice. Repeated display titles with different source-local IDs produce different graphics because the seed is `SHA256(medium + NUL + row_id)`.

The HTML preview provides exact citation links and hides no rights boundary: every record remains `UNVERIFIED_METADATA`, potentially narrower `rechecked_exact` metadata never becomes accepted canonical identity, no ISBN inferred from publisher URLs, zero Work/coverage effects. Original graphics are not screenshots, official film posters, book jackets, franchise insignia, copied character/actor likenesses, or licensed studio images. No remote image fetch, browser storage, user-private upload or full source read occurs. The gallery is **not** under the `explorer/` public Pages root.

The six generated SVG files and their exact SHA-256 digests appear in `manifest.json`. The page's CSP permits only same-origin SVG files, inline local styles, and no scripts or network connections. All artwork fallback descriptions are readable without images, and publisher links are opt-in clicks. **This art-only proposal is based directly on accepted `main`, excluding the 347-entry owner-private-derived OPF preview entirely.**

Reproduction:

```sh
python3 tools/build_reference_card_inputs.py
python3 tools/build_source_local_art_preview.py --check
python3 -m unittest tests.test_source_local_art_preview tests.test_reference_card_provenance_contract tests.test_explorer_abstract_art -q
python3 tools/validate.py
```

> **Hostile challenge:** attractive per-record original graphics might look like official episode stills or book covers. The gallery therefore labels them *original metadata references*, uses explicit no-still/no-poster/no-jacket wording, preserves source-local IDs and provenance hashes, and does not silently upgrade their `UNVERIFIED_METADATA` status.

**Release gate:** an independent visual/accessibility reviewer and user authorization are still required. No actual 320/390 screenshot is claimed: browser executables remain unavailable in this environment. Original SVG/graphics rendering determinism is a source/test result, not a real-browser proof.
