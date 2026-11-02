# Paramount+ legacy Season 1 publisher observations — proposal only

Observed 2026-11-02 against five official HTTPS Paramount+ episode guides. **114
source-local listing rows**, not 114 unique or fully researched episodes. No
copyrighted webpage HTML, scripts, video, or transcript is committed.

| Series | Official Season 1 guide | Publisher-listed slots |
| --- | --- | ---: |
| TOS | https://www.paramountplus.com/shows/star_trek/episodes/1/ | 30 |
| TNG | https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/ | 25 |
| DS9 | https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/1/ | 19 |
| Voyager | https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/ | 15 |
| Enterprise | https://www.paramountplus.com/shows/enterprise/episodes/1/ | 25 |

The exact HTML response bodies were processed locally and left in a temporary
directory outside Git. `index.json` holds each local body SHA-256 and byte count
along with the exact committed observation CSV digest. Generated bundles retain
publisher page URL, `publisher:paramount` lineage, season and episode ordinal,
and title only; `canonical_work_id` and `source_binding_id` remain null.

The premiere titles/part numbering demonstrate **edition-specific gaps**:
TNG lists *Encounter At Farpoint Part 1 and 2* as S1E1 followed by S1E3;
DS9 *The Emissary, Parts I and II*, Voyager *Caretaker, Part 1 & 2*, and
Enterprise *Broken Bow - Part 1 and 2* follow the same combined-premiere
pattern. These are not gaps to fill with invented Works. TOS includes *The
Cage* as publisher S1E1; the original broadcast and release interpretation
requires later source/edition reconciliation.

The five guide pages share one publisher family and are **not independent
corroborating sources**. A local response digest is not a publisher signature,
and an observed listing does not establish a full-season denominator or that
the audiovisual work has been viewed. The batch has
`DISCOVERY_ONLY`/`CANDIDATE_METADATA_ONLY` status, with admission, accepted
Source↔Work binding, coverage, and episode-denominator effects all `NONE`.

Offline reproduction of the committed derivative:

```bash
python tools/build_legacy_s1_discovery.py --check
python -m unittest tests.test_legacy_paramount_s1 -v
python tools/validate.py
```

To obtain a fresh source observation, independently retrieve the official
pages again and provide their raw HTML (outside Git) as `<mission>-s1.html`
to `--ingest-dir`. Compare the new source-body hashes and published ordinals
instead of treating old captures as unchanged source truth.

**Next:** independent hostile source/sample review, then Consolidator-only
integration into the separate public candidate directory. Do not silently
upgrade any record to a Briefing or canonical Work.
