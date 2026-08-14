# Short Treks staging research: SHORT-S01-B001

Status: PROPOSAL / STAGING ONLY  
Lane: SHORT  
Accepted base examined: `main` @ `d58359a207da89e812d0a0330558c66774ed1241`  
Governed coverage advanced: **no**

## Why this is staging

Accepted `main` contains no accepted Source/Work registry, Short Treks Work IDs, research schema, predicate registry, or Short Treks coverage ledger. The SHORT worker therefore does not invent canonical Source IDs, Work IDs, source hashes, or global identity mappings.

This staging packet preserves a completed close read of one full transcript representation while source binding remains a Librarian-owned blocker. It is intentionally not a completed governed batch manifest.

## Work-local scope

Provisional title label only: **Runaway**  
Series/lane: Star Trek: Short Treks / SHORT  
Release metadata crosscheck: Paramount+ identifies `Runaway` as a Short Treks installment dated 2018-10-04 and approximately 15 minutes.  
No canonical `work_id` is asserted here.

## Sources actually used

### S1 — full transcript representation used for close read

- Provider/site: Springfield! Springfield!
- Page title: `Star Trek: Short Treks (2018) s01e01 Episode Script — Runaway`
- URL: `https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s01e01&tv-show=star-trek-short-treks-2018`
- Retrieval/read date: 2026-08-14
- Extent actually processed: complete transcript body from opening computer announcement through Po's departure and Tilly's closing reaction.
- Source type: third-party transcript representation; not verified primary audiovisual media.
- Upstream transcript lineage: UNKNOWN.
- Reproducible byte hash: unavailable in this pass; do not promote to SOURCE_BOUND until Librarian binds and hashes an approved source instance.

### S2 — official metadata crosscheck only

- Provider: Paramount+
- Page: `Runaway`
- URL: `https://www.paramountplus.com/shows/video/J5m6KbSMyQY1ze592dA0NVXkcrbK0OOt/`
- Use: title/date/runtime/premise crosscheck only.
- Not used as a substitute for the full transcript.

### S3 — official franchise announcement crosscheck only

- Provider: StarTrek.com
- Page: `Tilly Helps an Unexpected Visitor`
- URL: `https://www.startrek.com/news/tilly-helps-an-unexpected-visitor`
- Use: confirms the installment's announced premise, Tilly/Mary Wiseman focus, writer/director metadata, and placement as the first Short Treks rollout installment.

## Local entity candidates

These labels are local to this staged work and make no global sameness claims.

| local label | type | source-relative role |
|---|---|---|
| `runaway:tilly` | person occurrence | Starfleet ensign; Command Training Program participant; encounters Po |
| `runaway:po` | person occurrence | Xahean visitor; engineer/inventor; later discloses royal succession |
| `runaway:siobhan` | person occurrence | Tilly's mother in remote conversation |
| `runaway:discovery` | vessel occurrence | Federation starship setting |
| `runaway:xahea` | place/world occurrence | Po's homeworld as described/reported in-source |
| `runaway:computer` | system occurrence | ship computer producing search/report output |
| `runaway:tricorder` | device occurrence | scanner producing biological classification/report output |
| `runaway:dilithium-incubator` | technology occurrence | device Po says she built to recrystallize dilithium |
| `runaway:po-brother` | person occurrence | deceased brother described by Po as king |

## Source-relative evidence notes

Evidence IDs below are staging-local labels, not canonical repository IDs.

### E01 — Tilly's command-program anxiety is introduced through family dialogue
- Kind: dialogue/testimony
- Scene anchor: opening remote conversation before the mess-hall encounter
- Participants: `runaway:tilly`, `runaway:siobhan`
- Evidence: Tilly says she is in the Command Training Program. Siobhan compares it to a childhood failure and expresses doubt framed as concern. Tilly resists the comparison.
- Epistemic limit: establishes the conversation and Tilly's participation in the program; Siobhan's characterization of Tilly is testimony, not objective diagnosis.

### E02 — ship systems warn about Tilly's caffeine request
- Kind: computer/system output + depiction
- Scene anchor: replicator interaction immediately before first contact
- Participants: `runaway:tilly`, `runaway:computer`
- Evidence: the replicator warns that the requested caffeine quantity is ill-advised; Tilly dismisses the warning.
- Epistemic limit: supports the system warning and Tilly's response, not a medical conclusion.

### E03 — biological identification comes from scanner/system reports
- Kind: sensor/computer report
- Scene anchor: first close encounter with the stowaway
- Participants: `runaway:po`, `runaway:tricorder`
- Evidence: the tricorder reports Xahean blood-based circulatory fluid and later a female developmental classification of approximately seventeen years. Tilly also states that ship sensors would have initiated quarantine for contagion.
- Epistemic limit: these are in-universe instrument/report outputs. They are not silently promoted here to omniscient world-state facts.

### E04 — Po demonstrates language/technical competence during first communication
- Kind: dialogue + action/depiction
- Scene anchor: universal-translator exchange
- Participants: `runaway:tilly`, `runaway:po`
- Evidence: after translator activation, Po gives her name and claims she could build a translator of that kind, saying she did so at nine. She also correctly challenges Tilly's boast about an Earth food she had only just encountered.
- Epistemic limit: the childhood engineering claim remains Po's testimony; the immediate conversational competence is depicted.

### E05 — reporting duty conflicts with Po's request to remain hidden
- Kind: dialogue + institutional-rule reference
- Scene anchor: Tilly tells Po she boarded a Federation starship without authorization
- Participants: `runaway:tilly`, `runaway:po`
- Evidence: Tilly says the unauthorized boarding is serious, that she is supposed to report Po, and that both could end up in the brig. Po says she had to run and reports that her parents and brother are dead.
- Epistemic limit: Tilly's statements establish her understanding of duty/consequences; no independent Starfleet regulation text is supplied in this work.

### E06 — Po describes Xahea through a twin-world model and dilithium mining
- Kind: dialogue/testimony
- Scene anchor: cargo-bay conversation after Tilly checks the Starfleet database
- Participants: `runaway:po`, `runaway:xahea`
- Evidence: Po says Xaheans were born with their planet and describes a natural balance between people and world; she says she mined dilithium caves from childhood.
- Epistemic limit: the biological/cosmological 'born with our planet' model is Po's account. It is not promoted to objective cosmology here.

### E07 — Discovery's computer reports Po as strategically critical
- Kind: computer/database report
- Scene anchor: Starfleet database search result
- Participants: `runaway:computer`, `runaway:po`
- Evidence: the computer/search output produces an active alert and language classifying Po as strategically critical and to be kept alive and secure.
- Epistemic limit: establishes the database/report state visible to Tilly, not the correctness or provenance of the underlying classification.

### E08 — Po says she invented a dilithium recrystallization device
- Kind: dialogue/testimony
- Scene anchor: Po explains why events on Xahea changed after her invention
- Participants: `runaway:po`, `runaway:dilithium-incubator`, `runaway:xahea`
- Evidence: Po says she built an incubator to recrystallize dilithium and intended it as something for her planet; she describes political/economic upheaval after the invention became known.
- Epistemic limit: the invention and its effects are primarily established by Po's testimony in this source; Tilly's reaction supplies corroborating recognition inside the conversation but not independent provenance.

### E09 — Tilly and Po explicitly connect through experiences of not being heard
- Kind: dialogue/interpersonal action
- Scene anchor: response to Po's account of the invention
- Participants: `runaway:tilly`, `runaway:po`
- Evidence: Po says no one listened to her. Tilly responds that being ignored by people who should care can be frightening and isolating and says she understands that experience.
- Epistemic limit: supports the expressed affinity and Tilly's self-report, not a broader psychological diagnosis.

### E10 — protection of Xahea becomes a decision problem
- Kind: dialogue/value conflict
- Scene anchor: debate over whether Po can continue hiding
- Participants: `runaway:tilly`, `runaway:po`, `runaway:xahea`
- Evidence: Po says she alone controls the knowledge and wants the door kept closed. Tilly argues that Po cannot hide and frames Xahea as entering a new phase. Po says others became greedy, fears harm to the planet, and says no one loves/protects it as she does. Tilly concludes that Po therefore has her answer and should go home.
- Epistemic limit: Tilly's evolutionary framing and Po's claims about others' motives are character positions, not narrator-certified truths.

### E11 — Po discloses succession status only late in the encounter
- Kind: dialogue/testimony
- Scene anchor: transporter preparation
- Participants: `runaway:po`, `runaway:po-brother`, `runaway:tilly`
- Evidence: Po says her brother was the king, that her coronation is the next day, and that she ran away because she was not ready to become queen. She explains that she withheld the title because people change how they listen after hearing it.
- Epistemic limit: establishes Po's disclosure and rationale within the conversation. Formal Xahean succession records are not present in this source.

### E12 — departure resolves the immediate concealment choice and reframes Tilly's self-concept
- Kind: dialogue + action/depiction
- Scene anchor: final transporter sequence
- Participants: `runaway:tilly`, `runaway:po`
- Evidence: Tilly prepares transport home. Po gives Tilly a dilithium crystal, Tilly predicts Po will be a good queen, and Po returns the affirmation by telling Tilly she will be a good commander after Tilly dismisses her earlier self-doubt.
- Epistemic limit: supports a local change in expressed attitude. It does not establish Tilly's later career outcome or a durable psychological transformation beyond this work.

## Interpretive assertions linked to evidence

### A01 — Present command identity is under negotiation, not settled
- Type: identity/self-concept
- Supports: E01, E12
- Assertion: the episode frames Tilly's command aspiration as contested by inherited/familial doubt and then locally reaffirmed through her interaction with Po.
- Counterevidence/limit: the closing affirmation is brief and does not prove a lasting change outside this installment.

### A02 — Mutual recognition, rather than rank, is the central interpersonal bridge
- Type: interpersonal dynamics
- Supports: E09, E11, E12
- Assertion: Tilly and Po become useful to one another after each discusses being reduced or misheard by others; Po explicitly values Tilly's unaltered response before revealing royal status.
- Counterevidence/limit: the relationship begins with fear, concealment, threats of reporting, and asymmetric institutional power; it is not frictionless solidarity.

### A03 — The invention creates an agency-versus-institution problem
- Type: agency / technology / politics
- Supports: E07, E08, E10
- Assertion: Po's technical innovation turns private ingenuity into a political resource problem, forcing a decision between concealment and assuming responsibility for how the technology affects Xahea.
- Counterevidence/limit: the transcript does not independently establish the full political system, motives of all Xaheans, or actual downstream effects of the device.

### A04 — Institutional information is explicitly source-relative
- Type: epistemic/evidence pattern
- Supports: E03, E07
- Assertion: important claims about Po are mediated through tricorder and database outputs. Under the common method, the work supports that those systems reported those claims; it does not justify treating every report as omniscient truth without further evidence.

### A05 — Tilly exercises discretion rather than mechanically applying stated duty
- Type: agency / institution / ethics
- Supports: E05, E10, E12
- Assertion: Tilly begins from an expressed obligation to report the unauthorized visitor but ultimately assists Po's return without the transcript depicting a formal reporting process.
- Counterevidence/limit: absence of a depicted report does not establish that no later report occurred or that Tilly violated a specific written regulation.

### A06 — Royal status alters the social meaning of listening
- Type: identity / social role
- Supports: E11
- Assertion: Po distinguishes between being heard as herself and being heard after others know she is a queen, suggesting that title/status can distort interpersonal recognition.
- Counterevidence/limit: this is Po's interpretation of others' behavior, not a quantified social rule.

## Neutral coding summary

- Plot/problem structure: unauthorized visitor hiding aboard Discovery; immediate concealment problem expands into a return/responsibility decision.
- Agency/decision points: Tilly decides whether to report/help; Po decides whether to remain hidden or return for coronation.
- Institutions/rules: Starfleet/Federation unauthorized-boarding expectations are referenced by Tilly; database classification of Po is visible.
- Interpersonal dynamics: initial fear/defensiveness changes through food, conversation, technical respect, and mutual disclosure.
- Identity/self-concept: Tilly's command aspiration; Po's engineer-versus-queen tension; status changing how others respond.
- Epistemic patterns: tricorder output, computer/database alert, testimony, self-report, and inference are distinguishable.
- Ethics/value conflict: protection of Xahea, political exploitation risk, duty to report, autonomy, responsibility accompanying technical power.
- Technology/material constraints: universal translator, replicator, transporter, dilithium mining, claimed dilithium recrystallization incubator.
- Culture/politics: Po describes Xahea's relationship with its planet and emerging strategic significance; details remain partly testimony-mediated.
- Humor/form: food/replicator exchanges and Tilly's verbal reactions repeatedly soften otherwise high-stakes disclosure.
- Continuity/worldbuilding: source mentions Federation, Starfleet, Discovery, Xahea, warp capacity, dilithium, and royal succession; no cross-series/global identity merges are made.
- Character-state changes: Po moves from concealment toward return; Tilly moves from voiced command doubt toward local reaffirmation.
- Consequences/unresolved: actual political handling of Po's invention, formal Starfleet reporting, and long-term outcomes are outside this work.
- Counterevidence: testimony and system reports are kept distinct from objective world-state; closing affirmations are not treated as permanent psychological/career facts.

## Coverage state for this staging packet

- `Runaway`: full transcript representation actually read and neutrally coded in this staging packet.
- `SOURCE_BOUND`: **not claimed**.
- `FULL_TEXT_AVAILABLE`: source representation was available during this pass, but no accepted Source record exists.
- `CLOSE_READ`: completed as proposal/staging work only.
- `SEMANTICALLY_ANALYZED`: staging-level neutral analysis completed; not accepted coverage.
- `ENTITY_LINKED`, `CROSS_REFERENCED`, `AUDITED`: not claimed.

No numeric Short Treks denominator or accepted percentage is advanced.

## Blockers to governed promotion

1. Librarian-owned accepted Short Treks Work inventory / canonical Work identity.
2. Approved Source binding for the transcript or another complete source representation.
3. Reproducible source bytes/hash or other approved fingerprint/locator scheme.
4. Accepted schema/predicate registry on `main`.
5. Conversion of these staging-local labels into governed records without silently adding claims.
6. Validation under accepted batch tooling.

## Exact next SHORT frontier

Continue the same bounded first-run tranche with **Calypso**, but only after obtaining a complete source representation that can actually be read end-to-end in the current pass. Do not infer completion from snippets or episode summaries. When source binding becomes accepted, promote this staging work by mapping rather than rewriting its evidence semantics.
