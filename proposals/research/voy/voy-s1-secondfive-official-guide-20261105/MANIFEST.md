# Voyager Season One — US publisher-guide cards 6–10 (HELD)

Role: **VOY**. Accepted `main` baseline: `3028765359001b90bc3e6b5c1835ee283b326e91`. This is a second, non-overlapping source-relative synopsis batch, not an admission of episode Work identity or close-reading.

## Retrieval and bounded content actually processed

- Complete first-party English-US [Paramount+ Season One episode guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/) retrieved via HTTP200 and parsed in memory. One observed raw HTML response: `292,338` bytes, SHA-256 `1c079a6bfd707c9252a576d71884344ce6fab0ef8cb963c90a8ffc6df47bbdbf`. Exact retrieval timestamp was not captured; date recorded as 2026-11-05 UTC. The HTML remains mutable and was not committed.
- Fifteen US **publisher cards** identified, not a canonical episode count. Stable normalized card/description-metadata fingerprint: `7bef657a899ca288a86e7f5dc6e310784b33ffbc46e04b78d2fa412a7f0e2f80`, across repeated live retrievals.
- Selected and fully read cards: guide ordinals `6,7,8,9,10`, official episode badges `7,8,9,10,11` — *Eye Of The Needle*, *Ex Post Facto*, *Emanations*, *Prime Factors*, and *State Of Flux*. Total original publisher description text inspected: **1,314 characters**. Source titles, publisher datetimes, opaque video route identifiers, original HTML line locators and per-paragraph hashes are in `records.json`; source paragraphs themselves are not.
- The prior first-five batch `research/voy-s1-firstfive-source-20261105` covers different guide ordinals `1..5` as another **HELD proposal**. Neither batch adds accepted coverage or silently combines global episodes.

## Epistemic and identity boundaries

The US guide's *Caretaker* pilot is one combined publisher card, with first badge 1 and next badge 3. The separate German-language Paramount+ listing displayed two pilot cards; this is a different locale/source-page observation, **not** automatic identity reconciliation. Card ordinal, badge, premiere datetime and canonical episode/Work identity remain different concepts.

The five original paraphrases are all **publisher-attributed**. Specifically, *Eye Of The Needle* describes a Romulan contact who *appears* willing to assist rather than proving a completed rescue; *Emanations* ends with an explicit question about the asserted afterlife explanation; *Prime Factors* describes a rule conflict and possible unauthorized plan, not confirmed outcome. None of these are audiovisual episode-close-read evidence.

One SOURCE→LOCAL_ENTITY→EVIDENCE→ASSERTION chain per publisher card (five chains). No third-party pixels, scripts, transcripts, publisher copy, video, audio or ebook bytes are committed. All identity, reconciliation, coverage, public Explorer and rights effects remain **NONE**.

## Reproduction and tests

`source_probe.py` parses the full US guide and fails closed on card-count/badge/route/title changes. Because direct Python requests can intermittently return 503 while the same page is accessible to curl, the following in-memory alternative was verified:

```bash
curl -sS -L --retry 2 --max-time 25 https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/ | python proposals/research/voy/voy-s1-secondfive-official-guide-20261105/source_probe.py --stdin
```

`--internal-prose` is intentionally nonpersistent and must never be redirected into the public repository.

The `validate.py` source/analysis gate pins the exact reviewed research JSON byte digest and all five independently paraphrased claim fingerprints, in addition to strict provenance, publisher dates, locale and route bindings. Changing an analysis demands a new reviewed research revision, not a recomputed self-attested manifest SHA. Run:

```bash
python proposals/research/voy/voy-s1-secondfive-official-guide-20261105/validate.py
python proposals/research/voy/voy-s1-secondfive-official-guide-20261105/test_validate.py -q
python -m unittest discover -s tests -q
python tools/validate.py
```

Twenty-six focused negative/regression tests cover source forgeries, rights/admission claims, global work identities, title/card/route swaps, invented plot outcomes, disputed afterlife, and exact reviewed text. All remain HELD until an independent **AUDITOR** examines the exact frozen commit and source.

No remote mutation, merge, deletion, force-push, deployment or coverage promotion authorized.
