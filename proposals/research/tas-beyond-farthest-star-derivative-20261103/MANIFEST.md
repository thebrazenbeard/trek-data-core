# TAS: *Beyond the Farthest Star* — complete available derivative-script reading

**Role:** TAS research worker. **State:** `PROPOSAL_ONLY / DERIVATIVE_TEXT_PROCESSED / NOT_ADMITTED`.
This is a source-relative close reading of one public third-party transcription, not an authenticated audiovisual or studio-script reading. The 22 publisher-listed TAS episode slots already indexed on accepted `main` are discovery observations, not accepted coverage.

## Sources and actual processing

- Candidate Work: *Star Trek: The Animated Series*, Season 1 Episode 1, *Beyond the Farthest Star*, as [Paramount+ labels it](https://www.paramountplus.com/shows/video/1792898835/). The official episode page is **metadata only** for this batch; no video was streamed or viewed.
- Text source actually retrieved: [Springfield! Springfield! third-party episode script](https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s01e01&tv-show=star-trek-the-animated-series-1973), HTTP 200, retrieved 2026-11-03 UTC. Exact raw response **43,366 bytes**, SHA-256 `07bdbddad2000679c6c97b86b0fb7aa7316c2891c248e42e711cbdabac8ee198`.
- The sole `scrolling-script-container` on that response was extracted, each HTML `<br>` separated, remaining tags removed, HTML entities decoded, surrounding whitespace stripped, and empty fragments discarded. Joining the resulting **263 ordered nonempty fragments** with single LF separators gives SHA-256 `9b5bba7a654c66b8d294c5b08bdc299ea1bbbf09245ac3c5c4fe8024cc1652a3`. Fragment numbers 1–263 are **source-relative to this exact captured HTML**, not canon script line numbers or audiovisual timecodes.
- I read all 263 ordered fragments, covering the opening log, anomalous star encounter, alien vessel exploration, translated warning, shipboard control conflict, crew response and final log. This is the complete **available page transcript body** in this capture, not proof of accuracy, completeness, speaker identity, direction or performance against the aired cut.
- A direct request for the separately indexed [Chakoteya version](https://www.chakoteya.net/StarTrek/TAS004.htm) returned HTTP 503 (and subsequent web open returned 502). It was **not read**. No independence between these two derivative transcription websites is claimed. The Springfield page's upstream transcription and editorial chain are `UNKNOWN`.
- The raw HTML and any complete transcript rendition stay in private transient scratch custody; they are **not committed**. This proposal contains only cryptographic fingerprints, fragment locators, paraphrased evidence, local referents and original assertions. Public reproduction rights to transcript text are unresolved.

## Source-relative reasoning boundaries

1. The unusual star properties, ship age, and magnetic readings are *instrument or character reports*. They do not become independently authenticated physics or chronology.
2. The translated alien-vessel warning reports a crew decision to destroy its own ship. The episode's translated-message representation is evidence of that reported history, not an independently inspected event 300 million years ago.
3. Spock's later classification of an incorporeal magnetic organism is a character hypothesis, whereas earlier sensors report no life/energy. Preserve both epistemic frames rather than forcing a definitive ontology.
4. The intruder's commands and later plea support a conflict between self-preservation, coercion, protection of crew, and isolation; they do not establish a verified mental state or official moral judgment.
5. Transcript speaker turns are poorly separated by the page's `<br>` segmentation; I therefore avoid pretending every unlabeled statement has a uniquely verified speaker.

The records cover **12 local entity referents, 15 source-bounded evidence notes, and 7 typed proposed assertions**. They create **zero** accepted Source–Work bindings, global identities, Briefings, coverage events, copyrighted source passages, public artwork or publication effects.

## Validation and hostile challenge

```bash
python3 proposals/research/tas-beyond-farthest-star-derivative-20261103/validate.py
python3 -m unittest proposals/research/tas-beyond-farthest-star-derivative-20261103/test_validate.py -v
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_explorer.mjs
```

> **Falsifier — derivative mismatch:** An authorized film/video comparison may find missing, misordered, mislabeled or invented transcript content. Nothing here qualifies audiovisual `CLOSE_READ` or `SEMANTICALLY_ANALYZED` coverage.

> **Falsifier — source lineage:** The Springfield transcript may copy another public transcription or subtitles. The availability of two URLs does not create two independent evidence families.

> **Falsifier — translated message:** A character's translation, even when presented as dramatic dialogue, may be partial or unreliable. The ancient crew's alleged self-destruction is not independent historical fact.

> **Falsifier — lifeform and motives:** Sensor readings, Spock's speculation, spoken commands and a plea for company have different evidentiary statuses. They cannot alone resolve biology, consciousness or moral standing.

**Next frontier:** Librarian source/edition custody and independent transcript comparison, primary audiovisual or authorized script validation, adversarial semantic audit, and explicit acceptance before any governed research or coverage promotion.
