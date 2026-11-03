# Holodeck Rescues #6–#10 — direct first-party video-page description follow-up

- Batch: `trek-scouts-holodeck-direct-video-followup-v1`, read 2026-11-03 UTC.
- Partition: `SHORT_FORM` source-local candidate research; **proposal only**.
- Primary source: first-party public YouTube `ytInitialPlayerResponse.videoDetails` and `microformat.playerMicroformatRenderer`, read from the five individual video-page HTML responses. The publisher channel is *Blaze and the Monster Machines*; all five items share one Paramount/Nickelodeon publisher lineage.
- Source read **is metadata/description reading, not video playback**. The five HTML documents were downloaded in memory only, not committed; their individual response-byte hashes, byte sizes, title hashes, and first-description-paragraph hashes are recorded in [`observations.json`](observations.json).
- Immutable observed metadata packet SHA-256: `bc40f22a7da0e8423e9c7bf0b1afc1b046637dbd174afa1aa1f1395587bfea04`. The raw HTML bytes may vary across fetches; these are retrieval receipts, not immutable publisher-version identities.
- Original source-relative synopsis proposals: the prior four are retained untouched in [`../scouts-holodeck-06to09-descriptions-20261103/observations.json`](../scouts-holodeck-06to09-descriptions-20261103/observations.json); one **new** original synopsis paraphrase is proposed for episode #10 now that its direct first-party description was actually retrieved.
- Effects: **NONE** on accepted Work identity, audiovisual close reads, semantic coverage, public Explorer synopsis publication, artwork publication, or reconciliation.

| Source-local entry | Video ID and direct first-party page | Publisher page title state on 2026-11-03 | Reading result |
| --- | --- | --- | --- |
| #6 | [-m7ISEuAhac](https://www.youtube.com/watch?v=-m7ISEuAhac) | Differs from previously recorded search-result display title | Existing search-result synopsis remains source-relative; direct description corroborates subject matter within one upstream publisher family |
| #7 | [cYRzkzu_zhg](https://www.youtube.com/watch?v=cYRzkzu_zhg) | Differs from previously recorded search-result display title | Existing source-relative synopsis retained; no new plot/viewing claim |
| #8 | [O5wUrGB_6qw](https://www.youtube.com/watch?v=O5wUrGB_6qw) | Differs from previously recorded search-result display title | Existing source-relative synopsis retained; no new plot/viewing claim |
| #9 | [TbZFOtuHpxk](https://www.youtube.com/watch?v=TbZFOtuHpxk) | Matches previously recorded search-result display title | Description mentions a giant crab; the title's whirlpool language is not treated as an observed animated outcome |
| #10 | [vlez2Dtu95E](https://www.youtube.com/watch?v=vlez2Dtu95E) | Newly obtained first-party video title and description | Publisher says a Klingon farmer's corn is invaded by small pink aliens, whom the Scouts try to catch; one new synopsis candidate, without retroactively editing the earlier hold |

The earlier #10 `HOLD_FIRST_PARTY_DESCRIPTION_NOT_RETRIEVED` remains accurate **for that older search-result research wave**. This later direct-page retrieval supersedes its source-availability limitation prospectively without falsifying prior provenance. The three different older/newer title observations are preserved, not silently normalized into one "official" title.

## Validation

```bash
python3 proposals/research/short/scouts-holodeck-06to09-descriptions-20261103/validate.py
python3 proposals/research/short/scouts-holodeck-direct-video-followup-20261103/validate.py
python3 -O proposals/research/short/scouts-holodeck-direct-video-followup-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_scouts_holodeck*' -v
python3 tools/validate.py
```

Required next gate: independent exact-head source/editorial audit and accepted-main reconciliation. These records are not yet public Explorer synopses or completed source research.
