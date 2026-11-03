# Discovery S1 first-five publisher metadata and synopsis research

**Proposal only.** Worker lane `DISCOVERY`; source is the official
[Paramount+ Discovery Season 1 guide](https://www.paramountplus.com/shows/star-trek-discovery/episodes/1/),
one direct HTTP 200 body retrieved and read 2026-11-03. Accepted starting
`main` SHA: `6271a861f6dbf5337a6a6792bb4b5ee355311157`.

## Actual result

- Five **first-party publisher** card descriptions structurally inspected
  (S1E1–E5), with original short, source-labeled synopsis paraphrases and
  first-party title, slot, raw zone timestamp, video locator and held image
  URL per card.
- One **289,705-byte** publisher HTML response digest and five normalized
  *publisher-description* digests. Raw publisher descriptions and HTML
  source snapshot stay out of Git. The source digest is an observation of
  bytes retrieved, not an authenticated publisher signature or guarantee
  they won't change.
- Five local Work candidates, five source-local entity mentions, five
  evidence records, five `PUBLISHER_DESCRIBES` assertions. Distinct global
  Work/Entity identities **unresolved**. The existing 15-row S1 publisher
  roster remains a separate candidate inventory, not independent content
  evidence.
- Five image CDN locators marked `HELD_NO_PUBLIC_DISPLAY_LICENSE`.
  **No image copied, displayed, hotlinked, or released.**
- Zero accepted Source/Work identity, reconciliation, coverage, denominator,
  published synopsis, or Explorer/artwork effects.

The five Publisher statements are **not** five independently witnessed
episodes. This batch did not view/close-read complete audiovisual works,
subtitles, scripts or transcripts. It does not claim to resolve emotional,
causal, moral, or identity facts beyond the publisher's own promotional
premises.

## Reproducibility and review

`records.json` is semantically pinned with a **code-owned canonical JSON
SHA-256** covering every claim, art URL and original synopsis. The validator
also checks accepted candidate-directory bytes, Work/evidence/entity scope,
held rights and no-publication invariants. When given an authenticated local
copy of the separately retrieved **exact** original HTML, it replays title,
slot, timestamp, video, art and description digest associations from the
same five source card blocks.

```sh
python3 proposals/research/discovery/s1-publisher-first5-20261103/validate.py
python3 -m unittest discover -s proposals/research/discovery/s1-publisher-first5-20261103 -p 'test_*.py'
python3 -O proposals/research/discovery/s1-publisher-first5-20261103/validate.py
python3 proposals/research/discovery/s1-publisher-first5-20261103/validate.py --source-html /path/to/private/exact_guide.html
```

**Review frontier:** Independent source re-read, own-card cross-bind and
rights/identity hostile audit of exact head; afterward only a separate
Librarian/Consolidator acceptance decision can change public projections.
The full-work research boundary remains open.
