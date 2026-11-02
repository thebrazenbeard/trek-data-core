# Short-form and scripted-audio source discovery — 2026-11-02

Status: **PROPOSED / DISCOVERY_ONLY**. No source-body reading, accepted Work IDs, Source↔Work bindings, governed Briefings, continuity facts, coverage denominators or universe completeness claim.

## Publisher metadata observed

| Candidate container | Source and observation | Typed classification |
|---|---|---|
| *Star Trek: Short Treks* | [Paramount+ episode guide](https://www.paramountplus.com/shows/star-trek-short-treks/episodes/): ten publisher-listed `S1E1`–`S1E10` title+slot pairs | Scripted audiovisual short anthology; ten source-local installment metadata leads |
| *Star Trek: very Short Treks* | [StarTrek.com announcement](https://www.startrek.com/en-un/news/star-trek-very-short-treks-announce) identifies five promotional spots and an announced release schedule | Promotional animation series; five **announced release-order** leads, **not** a canonical episode-number sequence |
| *Star Trek: Khan* | [Official StarTrek.com podcast page](https://www.startrek.com/en-un/podcasts/star-trek-khan) identifies a scripted audio series; [Paramount Press Express](https://www.paramountpressexpress.com/paramount-plus/releases/?view=111635-khaaaaaan-star-trek-khan-audio-series-releases-official-key-art-trailer-premiere-date-and-additional-voice-casting-at-san-diego-comic-con-panel) confirms its announced 2025 premiere | Scripted audio-series container; **zero episode candidates in this tranche** because no complete first-party audio episode guide was admitted |

Observed through source lookup on 2026-11-02. These are manually transcribed short titles and metadata locators. **The upstream website response bytes are not present here.** `bundle.json` is a research proposal, not an independently authenticated web snapshot. All three sources belong to the broader Paramount/CBS rights-holder family; they are **not three independent witnesses**.

The public `main` TV Mission registry currently contains 12 television series. These additional short-form/audio containers are **not merged** into that Mission count. The source schema intentionally gives them separate medium and Work types. No implied claims about canon status or continuity scope have been made.

## Deterministic projection and validation

Run `python3 tools/build_shorts_audio_candidates.py` to regenerate `records.json` or `--check` to fail if committed candidate bytes drift. The tool rejects duplicate IDs, publisher slots and titles within a container, forged URLs, unexpected fields, made-up audio episodes, symlinks on known source/output paths, and any proposal attempting to set admission or coverage effects.

An accepted record remains future work: individually resolve a Source and Work identity, obtain authorized audiovisual/audio access, review complete primary media, record evidence and counterevidence, then perform independent audit. The five *very Short Treks* are marketing shorts; their announced rollout does not establish canon status.
