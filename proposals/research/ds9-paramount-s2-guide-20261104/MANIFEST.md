# DS9 Season 2 Paramount+ guide cards — held proposal

**Partition:** DS9 source-local research. **Status:** proposal-only, no accepted source/work binding, no published briefing, and no episode CLOSE_READ or other research-coverage advancement.

## Provenance receipt

- Publisher: Paramount+; source family `publisher:paramount` (one corporate publisher, **not** independent corroboration).
- Exact source: <https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/2/>.
- Retrieval: 2026-11-04, TinyFish `fetch_content`, rendered Markdown, with page heading `Season 2 > Episode Guide`. The extraction yielded **25 visible numbered cards (S2 E1–E25)**, each read for title, ordinal, and short description. Original, nonverbatim paraphrases are in `observations.json` with exact visible heading locators.
- The publisher's page metadata reported the canonical URL above. **No direct HTTP status verification, raw HTML byte count, raw source hash, audiovisual viewing, or complete screenplay reading.** The `source_body_sha256` field remains `null`. The validator's locator-inventory digest is a fingerprint of *our card locators*, not the publisher text.
- **Unresolved:** S2 E26 was not visible in the returned guide extraction. The 25 rows are *observed publisher cards*, not a claim of full Season 2 coverage or a verified episode census. This batch must not infer episode E26's title or contents.

## Claim policy

`original_held_paraphrase` means an original summary of what the **publisher guide describes**; it is not an episode fact proven by direct audiovisual/source inspection. In particular, apparent hostility in `Whispers`, the allegation in `The Collaborator`, and the charge denied in `Tribunal` retain their narrative/attributed status. No entity identity reconciliation is attempted.

## Reproduce

```bash
python proposals/research/ds9-paramount-s2-guide-20261104/validate.py
python -m unittest discover -s proposals/research/ds9-paramount-s2-guide-20261104 -p 'test_*.py' -v
```

**Next frontier:** locate and source-bind the separately absent S2 E26 publisher guide card, inspect full source only where rights/access permit, then editorial review and comparison with independent primary evidence. Do not graduate these held proposals into accepted Works without a separate reconciliation/acceptance decision.
