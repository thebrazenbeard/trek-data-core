# Source-local publisher synopsis corrections — append-only v2

The two corrections are anchored to the *accepted* six-title source packet
`lit-six-next-publisher-works-20261103`, its immutable SHA-256, and the
already-accepted v1 editorial request SHA-256. The historical source packet
and request are preserved, not rewritten. This v2 proposal supersedes only the
**display paraphrase texts** for *Somewhere to Belong* and *Firewall*.

Two independently initiated reviews identified an overstated outcome/modal
claim and an understated confirmed premise. The official Simon & Schuster
About the Book pages are the source-relative basis, not readings of the novels.
Both replacements are original, short paraphrases with review status pending.

No new Source/Work/Evidence admission, literature close-read, public synopsis,
cover art or coverage follows from this correction. The v2 editorial request
must be rebuilt, independently checked against **all 18** exact publisher
description pages, and separately signed before a public candidate sidecar can
be generated. The old request v1 remains an audit artifact.

The v2 compiler is isolated in `tools/build_lit_modal_corrected_request.py`:
it first invokes the original strict v1 source/edition validator and then
applies only the two hash-bound corrections. The original compiler is **not
weakened or replaced**. The candidate release scaffold reads the v2 request
and fails closed without a new independent exact-text editorial receipt.
