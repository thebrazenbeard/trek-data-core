# S.C.E. #37 — *Ring Around the Sky* (HELD complete owner-private source read)

**Status:** `HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED`. One source-relative literary research proposal from a full in-memory read of **ten narrative chapters** in Patrick's owner-private converted ebook. The author's biography and later promotional material are excluded. Source bytes, copyright prose, cover art and graphics are **not** committed or exported.

## Source ownership and manifestation verification

- Live accepted `main` baseline on this worktree: `3028765359001b90bc3e6b5c1835ee283b326e91`.
- Private original ZIP: `ST ebooks.zip`; member `ST ebooks/STAR TREK - SCE - 37 - Ring Around The Sky.lit`, **240,233 bytes**, SHA-256 `a414415911f6c6502e1f8234c6ba9f297229fee438340843a695cc8cb4215282`.
- Private conversion ZIP: `Star_Trek_OPF_Converted.zip`, **95,673,655 bytes**, SHA-256 `0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f`. SCE37's OPF: 4,242 bytes / `392224d17900b9dd6293d1a83936a56b1fa4642c86d59168a913b83fc29d76f8`; HTML: 199,115 bytes / `467832c627a4240d422a398cbdb09a325a129f7c153e553f181910186b734f46`; TOC: 1,456 bytes / `a2c80ff26db346a9587ef5004c48401b9f920dde3d4c86400ee10b53e72cc088`.
- The conversion manifest reports `success` for exactly `STAR TREK - SCE - 37 - Ring Around The Sky.lit` (DRM label 1, exit code 0, thirteen output files). The original LIT-to-HTML conversion has **not** been independently reproduced or publisher-authenticated.
- The accepted OPF discovery inventory is `opf-local:0048`; it supplies the source-local work title `Ring Around the Sky` and creator `Allyn Gibson`.
- True tag-anchored chapter spans begin at the first byte of the complete `<div class="chapter" id="ch_N">` HTML tag. **Chapter 1 begins at byte 7,250; the author biography begins at byte 197,110.** The ten spans in `records.json` include exact byte starts/ends and SHA-256 fingerprints. This explicit rule prevents the earlier SCE36 +21-byte embedded-ID offset error.

## Official publisher crosscheck — not an edition authentication

[Simon & Schuster's publisher page](https://www.simonandschuster.com/books/Star-Trek-Ring-Around-the-Sky/Allyn-Gibson/Star-Trek-Starfleet-Corps-of-Engineers/9780743476119) identifies *Star Trek: Ring Around the Sky*, S.C.E. **#37**, by Allyn Gibson, *Pocket Books/Star Trek*, published March 29, 2004, ebook ISBN-13 `9780743476119`, 136 pages. The OPF embedded work ISBN-10 `0-7434-7611-5` checksum-converts to this publisher ISBN-13; the distinct converter-header ISBN-10 `0-9673008-1-9` does not designate this work. A matching title/creator/ISBN is metadata alignment **only**, not proof that the privately converted bytes derive from the identified licensed edition or may be republished.

## What was actually coded

- One source-local candidate and one work-local candidate, **15 source-local entities**, **10 source-relative evidence observations**, **7 guarded typed assertions**, **10 original chapter summaries**, and a new whole-book synopsis.
- The opening elevator catastrophe is **Tev's recurrent dream**, not a presently unfolding crash. The death of his mother is disclosed in memories and at a memorial; Tev's described Fury fear-weapon experience stays separately attributed testimony.
- The hypothesis that the Ring was made by the Furies comes from an in-story archaeological interpretation. The briefing also entertains competing reasons for construction; no definitive evolutionary origin or purpose is established.
- The government's temporary structural fields worsen the shaft according to crew assessment. Local minister Eevraith initially proposes an inadequate replacement. That diagnosis is source-reported technical reasoning.
- Tev originates the controlled-collapse solution but deliberately allows Eevraith to promote it as his own for political acceptance. The story does not establish how public historical credit will later be assigned.
- The maneuver begins to fail due to an **inferred mechanical recoil and premature charge detonation**. Rescue operators deflect the larger piece and crew report the Ring stable; this is **a bounded preservation outcome**, not reconstruction of the destroyed segment or a complete repair.
- Faulwell presents stylometric/linguistic clues and Tev confirms he wrote the dissertation claimed by Eevraith. This supports local authorship; it is not an independent legal ruling of plagiarism or a full account of all academic records.
- Tev's explanation of unequal treatment of Tellar-born outsiders remains a source-local account, not an unrestricted sociological assertion about every Kharzh'ullan.

## Tests and effects

```sh
python3 -m unittest tests.test_sce37_private_source_read_held -v
python3 -m proposals.research.sce37_private_complete_read_20261105.validate
python3 -m unittest discover -s tests -q
python3 tools/validate.py
# On Lappy with the owner-private archive, optional rehash (emits no source content):
python3 -m proposals.research.sce37_private_complete_read_20261105.verify_owner_archive \
  --archive /path/to/Star_Trek_OPF_Converted.zip \
  --original-lit-archive '/path/to/ST ebooks.zip'
```

**All accepted effects remain `NONE`:** no canonical Source/Work admission, canonical evidence or coverage change, cross-work or global identity reconciliation, public Explorer update, copyright prose export, distribution-rights claim, push, merge, deployment, credential change, or paid service. Independent source and semantic audit is required before any incorporation.
