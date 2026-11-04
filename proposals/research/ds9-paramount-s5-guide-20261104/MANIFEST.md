# DS9 Season 5: held Paramount+ episode-guide research cards

**Partition:** DS9. **Batch ID:** `ds9-paramount-s5-guide-20261104`. **Effect:** proposal-only, with no admitted Work, accepted source binding, episode semantic/audiovisual coverage, published Explorer briefing, or global identity resolution.

## Official source actually processed

- [Paramount+ DS9 Season 5 Episode Guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/5/).
- Fetched on 2026-11-04 with `TinyFish fetch_content`; read the rendered Markdown `Season 5 > Episode Guide` page's visible title/episode ordinal/short description for every extracted episode card.
- **24 visible publisher cards:** S5 E1–E11 and S5 E13–E25. The rendering omitted **E12 and E26**, so neither is assigned a title, synopsis, source digest, or completed-coverage claim.
- For each visible card, records hold its publisher-literal title and ordinal, exact source heading path, a SHA-256 of the **single rendered description line as UTF-8 without a trailing newline**, and an original concise publisher-attributed synopsis. Source description text itself is not reproduced verbatim.
- Corporate lineage: `publisher:paramount`. Twenty-four cards from one guide are **not** twenty-four independent primary sources. Source page-body SHA, raw HTML byte count, HTTP status, complete script/video reading and episode air dates are not established.

## Source-relative treatment

The S5 E1 guide suggests a suspected Changeling identity; that is a **mission premise**, not proof that the Klingon leader is a Changeling. E5 contains an entity-hostage description, E8 assigns the crew mysterious historical roles, E10 concerns visions, E19 involves an affective paternal label, and E22 concerns possible descendants. All are preserved as `PUBLISHER_GUIDE_DESCRIBES` assertions tied to source-local cards, without cross-work identity reconciliation or elevating subjective experiences into established fictional truth.

## Structure and validation

`SOURCE → [WORK unbound] → LOCAL ENTITY → EVIDENCE → ASSERTION`

The proposal contains 24 source slots, 24 local entities, 24 evidence records, and 24 attributed assertions. Every evidence record includes exact card locator and a fingerprint of the underlying publisher's description. All `work_ref` fields are null; source binding and research coverage remain unchanged.

```bash
python proposals/research/ds9-paramount-s5-guide-20261104/validate.py
python -m unittest discover -s proposals/research/ds9-paramount-s5-guide-20261104 -p 'test_*.py' -v
```

The validator pins each observed ordinal/title/fingerprint triple and the entire evidence linkage. Eight test groups challenge inaccurate Work admission, missing/duplicated ordinals, title/hash tampering, invented source-body/media reading, broken subject/evidence links, unsupported identity resolution, and distorted attribution.

**Next frontier:** Retrieve and verify the absent S5 E12/E26 guide cards through legitimate accessible primary publisher views (or hold `UNKNOWN`). Any full audiovisual/script close read, accepted Work reconciliation, or published Explorer synopsis needs its own evidentiary and authorization step.
