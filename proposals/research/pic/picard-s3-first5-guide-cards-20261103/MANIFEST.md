# PIC.PPLUS.S3.FIRST5.CARDS.20261103 — held publisher guide observations

**Role:** PIC research worker. **Status:** proposal-only, not accepted evidence until independently reviewed/merged. **Scope:** five first-party *Star Trek: Picard* season 3 Paramount+ guide cards (episodes 1–5), not the underlying complete audiovisual episodes.

## Actual source observations

- First-party season guide: https://www.paramountplus.com/shows/star-trek-picard/episodes/3/
- Retrieved 2026-11-03: direct publisher HTTP 200 via Lappy WSL and separate web-rendered view. Two raw responses were **271,825 bytes** with differing full-page SHA256s `02dbab5ad9518af0589ff5be618fee1a13e983270cdf948807dd32b4667c683f` and `9911e2cfb52ba80ee75e0e63063b4c04c7797b4df3f82b399446a164398539a4`. Raw HTML is dynamic and deliberately not retained/published. These are observations, not a claim of immutable publisher source bytes.
- First five exact title/slot entries on publisher guide text lines 104–128, and own-card `/shows/video/{id}/` links plus adjacent `thumbnails.cbsig.net` still-image locator for each. The card contains a publisher synopsis paragraph; only its SHA256 fingerprint and character count are retained. Fingerprint rule: HTML-unescape and strip surrounding whitespace of `div.ep__copy` text, hash UTF-8 bytes; **no verbatim publisher paragraph** published.
- Independent same-provider inventory crosscheck: `proposals/discovery/modern-paramount-season3-20261102/pic-observed-slots.csv`, exact SHA256 `033f18a51a5ea16c452aab27bbcdd3373ed321f97bf38bd994d813b5edbb6fe0`. The ten-row inventory is a separate *source-local slot observation*, **not independent corroboration** or coverage.

## Source-relative conclusions and limits

| Card | Episode title | Allowed observation | Held from promotion |
|---|---|---|---|
| S3 E1 | The Next Generation | Publisher title/slot, own-card asset locators, literal description mentions and description fingerprint | Publisher's plot claims are not on-screen fact |
| S3 E2 | Disengage | Same | No Work/episode content admission |
| S3 E3 | Seventeen Seconds | Same | No image hotlink/public rights release |
| S3 E4 | No Win Scenario | Same | Paraphrased guide descriptions are not a completed semantic read |
| S3 E5 | Imposters | Same | No accepted source binding, coverage, denominator, or Explorer release |

Original short synopsis **candidates** are marked `HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE`. The publisher's character/ship-name appearances support only *publisher utterance*, never cross-work identity or canonical screen truth. The thumbnail URL is an observation of an HTML pointer; neither the existence of a link nor noncommercial intent establishes reuse rights. No thumbnails, episodes, transcripts, text extracts, or cover bytes are committed.

## Reproduction and adversarial checks

```sh
python proposals/research/pic/picard-s3-first5-guide-cards-20261103/validate.py
python -m unittest discover -s proposals/research/pic/picard-s3-first5-guide-cards-20261103 -p 'test_*.py' -q
python -O proposals/research/pic/picard-s3-first5-guide-cards-20261103/validate.py
```

The validator requires exact five code-owned full-row digest pins (including mentions, synopsis, rights/status and URLs), independently fixed source/card identity, description fingerprints, approved mutable HTTP receipts, original discovery SHA, source-local rows and date. Hostile tests challenge same-host link swaps, paired link swaps, forged descriptions/mentions, promoted rights/Work/coverage/Explorer effects, extra/duplicate keys, wrong counts, wrong source, and optimized-Python fail-open.
