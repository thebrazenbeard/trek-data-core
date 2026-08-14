# DS9 season 1 staging batch 003

## Authority status

This is proposal-only DS9 research staging. It is not accepted coverage.

At the start of this tranche, accepted `main` still contained no accepted DS9 research records, no accepted architecture/schema/predicate registry, and no Librarian-owned DS9 Source/Work bindings. This packet therefore does not invent canonical `source_id`, `work_id`, source hashes, or coverage transitions.

The packet is intentionally stored only under the DS9 research partition.

## Works actually processed

Five complete transcript-body close reads were performed in season-one broadcast sequence:

1. Vortex
2. Battle Lines
3. The Storyteller
4. Progress
5. If Wishes Were Horses

This advances only the proposal research frontier. It does not advance accepted DS9 coverage.

## Source and retrieval notes

### Episode identity/order

The season-one episode order was crosschecked against complete-series transcript indexes before selection. The intended sequence for this tranche is Vortex through If Wishes Were Horses.

### Transcript representations

Complete third-party transcript representations were used for close reading. Primary audiovisual masters were not directly verified in this tranche.

Retrieval used multiple transcript hosts because individual providers intermittently returned 403/502 or anti-bot responses. Provider availability therefore must not be mistaken for provenance independence.

Observed source-family / locator notes:

- Forever Dreaming topic IDs in this range resolve as `95430` Vortex, `95431` Battle Lines, `95432` The Storyteller, `95433` Progress, `95434` If Wishes Were Horses.
- Springfield Springfield's DS9 season-one index presents the correct broadcast ordering, but individual transcript-page headings in this range are shifted relative to their transcript bodies. For example, its `s01e16` page is headed `The Forsaken` while the body is the complete `If Wishes Were Horses` transcript.
- Earlier DS9 staging tranches observed the same systematic heading/body displacement. It is preserved here as a source-binding anomaly rather than silently normalized.
- TVWriting exposes production-numbered script locators for this range, but direct text retrieval returned HTTP 403 during this pass.
- Chakoteya was usable for episode-order/production-number discovery but direct transcript retrieval was intermittently unavailable.

These providers may share upstream transcript lineage. Independence is UNKNOWN pending Librarian analysis.

No reproducible canonical source hash is claimed here. Therefore `SOURCE_BOUND` is not claimed.

## Local entity candidates

These labels are work-local staging handles only. They are not global identity mappings.

### Vortex

- `vortex:odo` — station security officer/changeling occurrence
- `vortex:croden` — Rakhari fugitive/prisoner occurrence
- `vortex:yareth` — Croden's daughter, encountered in stasis
- `vortex:ah_kel` — surviving Miradorn twin occurrence
- `vortex:ro_kel` — killed Miradorn twin occurrence
- `vortex:miradorn_twinned_self_claim` — claimed single-self/two-halves identity framing
- `vortex:rakhari_authority` — offscreen governing/legal authority as represented through communication/testimony
- `vortex:crystal_key` — object Croden associates with changeling mythology and later uses to access stasis
- `vortex:chamra_vortex` — spatial hazard/location

### Battle Lines

- `battle_lines:sisko`
- `battle_lines:kira`
- `battle_lines:bashir`
- `battle_lines:opaka`
- `battle_lines:shel_la`
- `battle_lines:zlangco`
- `battle_lines:ennis_group`
- `battle_lines:nol_ennis_group`
- `battle_lines:resurrection_microbes` — artificial/biomechanical organisms reported to restore damaged bodies
- `battle_lines:satellite_defense_net`
- `battle_lines:prison_planetoid`

### The Storyteller

- `storyteller:obrien`
- `storyteller:bashir`
- `storyteller:dying_sirah`
- `storyteller:apprentice`
- `storyteller:dalrok` — destructive manifested phenomenon as locally depicted/reported
- `storyteller:orb_fragment` — object identified by the apprentice as catalyst
- `storyteller:village_collective`
- `storyteller:varis_sul`
- `storyteller:paqu`
- `storyteller:navot`
- `storyteller:jake`
- `storyteller:nog`

### Progress

- `progress:kira`
- `progress:mullibok`
- `progress:baltrim`
- `progress:keena`
- `progress:sisko`
- `progress:minister_toran`
- `progress:jeraddo`
- `progress:jake`
- `progress:nog`
- `progress:quark`
- `progress:noh_jay_consortium` — improvised trading identity used by Jake and Nog
- `progress:stem_bolts` — traded cargo
- `progress:land_parcel` — seven-tessipate property acquired through barter

### If Wishes Were Horses

- `wishes:sisko`
- `wishes:jake`
- `wishes:obrien`
- `wishes:keiko`
- `wishes:molly`
- `wishes:bashir`
- `wishes:dax`
- `wishes:odo`
- `wishes:quark`
- `wishes:buck_bokai_manifestation`
- `wishes:rumpelstiltskin_manifestation`
- `wishes:idealized_dax_manifestation`
- `wishes:subspace_rupture_manifestation`
- `wishes:observer_manifestation_group` — entities later identifying themselves as explorers/observers

## Source-relative evidence notes

Evidence keys below are staging handles only. Each records what the transcript representation supports, not an omniscient fictional world-state.

### Vortex

- `DS9-B003-E001` — depiction/action: a Miradorn is killed during the failed criminal exchange involving Quark, Croden, and the Miradorn pair.
- `DS9-B003-E002` — testimony: Ah-Kel describes Miradorn twins as one self divided into two halves and frames Ro-Kel's death as damage to himself.
- `DS9-B003-E003` — testimony: Croden offers Odo information about a supposed changeling colony and uses that prospect while seeking escape/leniency.
- `DS9-B003-E004` — testimony/counterevidence: Croden later admits the changeling stories he told were myths and that he does not actually know the stone's origin.
- `DS9-B003-E005` — depiction/action: Croden uses the crystal object to access a hidden stasis chamber containing Yareth rather than a changeling colony.
- `DS9-B003-E006` — testimony: the Rakhari authority represents Croden as an enemy/criminal and demands his return.
- `DS9-B003-E007` — testimony: Croden says his family was killed because of his status as an enemy of the people and admits killing security officers.
- `DS9-B003-E008` — depiction/action: Odo ultimately transfers Croden and Yareth to a Vulcan vessel rather than completing Croden's return to Rakhar.
- `DS9-B003-E009` — testimony/action: Odo reports Croden dead and explicitly adopts Croden's language of dissembling.

### Battle Lines

- `DS9-B003-E010` — testimony: Opaka interprets her visit and possible non-return through prophecy/religious meaning.
- `DS9-B003-E011` — depiction/action: the runabout is attacked by an automated satellite system and crashes on the prison world.
- `DS9-B003-E012` — depiction/medical report: Opaka is found dead after the crash and later returns to life.
- `DS9-B003-E013` — medical report: Bashir identifies artificial/biomechanical microbes as repairing/restoring damaged bodies.
- `DS9-B003-E014` — medical report: Bashir concludes restored inhabitants become dependent on the local microbes and cannot safely leave their environment.
- `DS9-B003-E015` — testimony: members of the Ennis/Nol-Ennis groups give uncertain and differing accounts of what originally caused their conflict.
- `DS9-B003-E016` — depiction/action: Sisko proposes extraction/ceasefire; the groups remain mutually distrustful and resume conflict.
- `DS9-B003-E017` — testimony: Kira distinguishes the Bajoran resistance struggle she experienced from the purposeless recurring violence she sees on the prison world.
- `DS9-B003-E018` — testimony: Opaka directly challenges Kira's relationship to violence and self-concept.
- `DS9-B003-E019` — testimony/counterevidence: when Bashir raises the possibility of reprogramming the microbes so inhabitants can die permanently, Shel-la immediately frames that possibility as a means to destroy the opposing group.
- `DS9-B003-E020` — depiction/testimony: Opaka remains behind and interprets that outcome through the Prophets/prophecy.

### The Storyteller

- `DS9-B003-E021` — depiction/sensor report: O'Brien and Bashir encounter a destructive recurring phenomenon the villagers call the Dal'Rok; ordinary initial readings do not establish a conventional atmospheric source.
- `DS9-B003-E022` — testimony: villagers and the Sirah frame the Dal'Rok struggle through communal story, leadership, and religious language.
- `DS9-B003-E023` — depiction/action: the dying Sirah designates O'Brien as successor, but O'Brien's initial attempt to reproduce the ritual/story is only partly effective.
- `DS9-B003-E024` — testimony: the apprentice later explains that an Orb fragment serves as a catalyst through which the villagers' collective fears take physical form.
- `DS9-B003-E025` — depiction/action: when the apprentice assumes the storytelling role and regains the villagers' focus/confidence, the destructive phenomenon retreats.
- `DS9-B003-E026` — testimony: the apprentice says the prior Sirah intentionally chose O'Brien in order to force the apprentice to intervene and prove himself.
- `DS9-B003-E027` — testimony: Varis Sul describes the Paqu/Navot land dispute in the context of a river altered during the Cardassian occupation.
- `DS9-B003-E028` — depiction/action: Jake and Nog help Varis reframe the land conflict toward negotiated mutual benefit rather than simple winner/loser logic.
- `DS9-B003-E029` — testimony: Varis says her parents were killed by Cardassians; Jake separately says his mother was killed in the Borg attack he experienced.

### Progress

- `DS9-B003-E030` — institutional/documentary context: Kira is assigned to remove the final inhabitants of Jeraddo so Bajor can begin an energy-extraction project expected to benefit hundreds of thousands.
- `DS9-B003-E031` — testimony: Mullibok says he escaped a Cardassian labor camp and built his life on Jeraddo over approximately four decades.
- `DS9-B003-E032` — testimony: Mullibok refuses relocation despite being told the atmosphere will become unbreathable and says he would rather die there than leave.
- `DS9-B003-E033` — dialogue/interpretation: Kira compares forced removal with Cardassian behavior; Toran rejects the comparison and insists the broader project cannot be delayed for three holdouts.
- `DS9-B003-E034` — depiction/action: a confrontation wounds Mullibok; Baltrim and Keena are evacuated.
- `DS9-B003-E035` — depiction/action: Bashir proposes taking the wounded Mullibok for medical care; Kira refuses to authorize removal without his consent and temporarily remains to care for him.
- `DS9-B003-E036` — dialogue: Sisko tells Kira that her long identification with resistance/underdogs conflicts with her new institutional position and responsibilities.
- `DS9-B003-E037` — depiction/action: after Mullibok recovers enough to continue refusing evacuation, Kira destroys the cottage he has made the condition of his staying.
- `DS9-B003-E038` — testimony/action: Mullibok demands that Kira kill him rather than remove him; Kira refuses and orders transport for both of them.
- `DS9-B003-E039` — depiction/action: Jake and Nog barter unwanted yamok sauce into self-sealing stem bolts and then into a parcel of land.
- `DS9-B003-E040` — depiction/action: when Bajoran authorities need the acquired parcel for another project, Quark recognizes its leverage/value and moves to insert himself into negotiations.

### If Wishes Were Horses

- `DS9-B003-E041` — depiction: apparent physical manifestations corresponding to private stories, desires, memories, and fears appear aboard the station.
- `DS9-B003-E042` — depiction/testimony: a Buck Bokai manifestation has memories matching information Jake placed in a holosuite program, while O'Brien's Rumpelstiltskin manifestation is not sourced from a holosuite instance.
- `DS9-B003-E043` — depiction/testimony: an idealized Dax manifestation reflects Bashir's private romantic/sexual fantasy while the actual Dax rejects identification with it.
- `DS9-B003-E044` — sensor report/inference: station personnel detect what they interpret as a subspace rupture and compare its apparent readings with the historical Hanoli disaster.
- `DS9-B003-E045` — counterevidence/inference: Sisko notices that the threatening rupture matches what the crew collectively imagined after discussing the anomaly and concludes that the rupture itself is part of the manifestation process.
- `DS9-B003-E046` — depiction/action: after Sisko orders the crew to stop treating the rupture as real, the apparent threat disappears from the readings.
- `DS9-B003-E047` — testimony: the manifestations later identify themselves as explorers/observers who followed a ship through the wormhole and were studying humanoid imagination.
- `DS9-B003-E048` — testimony: the observers say the station's imagined phenomena, including the apparent danger, were created through the crew's imagination while the observers watched the results.
- `DS9-B003-E049` — testimony/epistemic limit: the observers decline to give a substantive account of their species before departing.
- `DS9-B003-E050` — consequence: the episode ends with an explanatory account of the immediate manifestations but does not provide a fully specified mechanism for how imagination acquired physical/sensor-real effects.

## Candidate assertions

All assertions remain PROVISIONAL staging interpretations and must be converted to governed predicates only after accepted schema/predicate and Source/Work binding exist.

### Vortex

- `DS9-B003-A001` — linked to E002: Miradorn twin identity is presented as an internally significant self-concept in which two biological individuals are described as one self; the transcript does not independently establish the claim as metaphysical fact.
- `DS9-B003-A002` — linked to E003-E005: Croden's early changeling-origin claims are contradicted by his later admission and by the actual discovery in the hidden chamber.
- `DS9-B003-A003` — linked to E006-E009: Odo resolves the prisoner-transfer problem by privileging Croden/Yareth's protection over literal compliance with the requested return, then conceals that choice through a false/deceptive report.
- `DS9-B003-A004` — linked to E003-E005: Odo's uncertainty about his origins is an exploitable epistemic vulnerability in this work, but the attempted exploitation does not resolve his origin.

### Battle Lines

- `DS9-B003-A005` — linked to E010,E020: Opaka consistently interprets events through prophecy/Prophets, but those utterances establish her religious interpretation rather than independently proving supernatural causation.
- `DS9-B003-A006` — linked to E012-E014: the episode supplies medical/sensor-style support for bodily restoration by artificial microbes while simultaneously imposing an environmental dependency that prevents simple rescue.
- `DS9-B003-A007` — linked to E015-E019: indefinite resurrection does not end the conflict; the groups preserve adversarial identity and readily incorporate proposed technological change into continued warfare.
- `DS9-B003-A008` — linked to E017-E018: Kira is forced to distinguish her own history of resistance violence from violence that has become self-perpetuating, producing an explicit challenge to her self-concept.

### The Storyteller

- `DS9-B003-A009` — linked to E021-E025: the Dal'Rok is depicted as responsive to communal cognition/storytelling mediated by an Orb fragment, but the apprentice's explanatory model should remain an attributed mechanism rather than omniscient ontology.
- `DS9-B003-A010` — linked to E023-E026: successful Sirah authority depends not simply on possession of a ritual object but on social confidence, narrative performance, and collective participation.
- `DS9-B003-A011` — linked to E027-E029: the Paqu/Navot dispute is reframed from inherited grievance toward negotiated interdependence, while occupation-era harms remain testimonial context rather than being erased by the settlement.

### Progress

- `DS9-B003-A012` — linked to E030-E038: Kira's assignment creates a conflict between individual attachment/autonomy and institutional policy aimed at aggregate public benefit; the episode does not make either value disappear merely because evacuation ultimately occurs.
- `DS9-B003-A013` — linked to E031-E038: Mullibok treats home, continued residence, and continued life as inseparable; Kira eventually rejects his stated preference for death by removing the material basis of his refusal and ordering evacuation.
- `DS9-B003-A014` — linked to E036-E038: Kira's resistance-era identity is explicitly challenged by her new exercise of state/institutional power.
- `DS9-B003-A015` — linked to E039-E040: the Jake/Nog trading chain depicts value as relational and context-dependent rather than intrinsic to the exchanged goods.

### If Wishes Were Horses

- `DS9-B003-A016` — linked to E041-E043: the manifestations initially look like autonomous embodiments of private mental content, but resemblance/content origin does not imply identity with the remembered, fictional, holographic, or desired persons they resemble.
- `DS9-B003-A017` — linked to E044-E048: the apparent subspace catastrophe is not securely established as an independent external event; the final observer testimony and Sisko's successful test support treating it as part of the imagination-mediated phenomenon.
- `DS9-B003-A018` — linked to E047-E050: the observers provide a motive and causal attribution for the manifestations but leave the physical mechanism substantially unresolved.
- `DS9-B003-A019` — linked to E042-E043: manifested memory/personality content can be derivative of stored program data or private imagination without establishing persistence of the represented historical/fictional person.

## Counterevidence / ambiguity register

- `Vortex`: Croden supplies both claims and later retractions; no changeling colony is found. Do not promote his earlier origin story because Odo wanted it to be true.
- `Vortex`: Ah-Kel's single-self/two-halves language is meaningful identity testimony but is not sufficient to collapse the twins into one global entity.
- `Battle Lines`: Opaka's prophetic framing coincides with events but remains religious interpretation unless separately corroborated by evidence of causal agency.
- `Battle Lines`: medical resurrection is strongly depicted, but the exact limits and complete engineering of the microbes are not established in this work.
- `Battle Lines`: the possibility of restored mortality does not itself support a peace hypothesis; Shel-la immediately treats it as a new way to win the war.
- `The Storyteller`: the apprentice's Orb-fragment explanation fits observed events but is still a character explanation of an extraordinary mechanism.
- `The Storyteller`: communal belief/confidence affects the outcome, so a purely object-centric explanation is incomplete.
- `Progress`: Mullibok's consent is explicit and persistent; eventual evacuation should not be rewritten as voluntary merely because Kira believes she is saving him.
- `Progress`: Kira's coercive resolution does not erase her prior sympathy or the project's public-benefit rationale; both remain relevant evidence.
- `If Wishes Were Horses`: the crew initially interprets sensor evidence as an external subspace rupture; later events undercut that interpretation. Preserve both the initial report and later reassessment.
- `If Wishes Were Horses`: the observers' final account is testimony by involved agents, not omniscient narration. It has strong corroborating behavioral context but does not exhaustively specify mechanism.

## Provisional cross-work hypothesis tests

### H1 — Formal duty versus relational/ethical commitment

**Hypothesis:** Early DS9 repeatedly places institutional agents in situations where literal formal duty conflicts with a relationship-based or individualized ethical judgment.

Supporting evidence in this tranche:
- Odo declines literal prisoner return in `Vortex` after protecting Croden and Yareth.
- Kira resists and delays Jeraddo evacuation in `Progress`, then ultimately enforces institutional removal herself.

Neutral/less-supportive evidence:
- The Paqu/Navot negotiation in `The Storyteller` is largely a mediation problem rather than a direct duty-versus-relationship conflict.
- `If Wishes Were Horses` is primarily epistemic/anomalous rather than institutional.

Disconfirming search target:
- Later DS9 works in which an officer's formal duty and individualized ethical judgment align cleanly, especially where the narrative gives no meaningful conflict between them.

### H2 — Extraordinary causation is layered through competing evidence frames

**Hypothesis:** Extraordinary events in DS9 are frequently presented through multiple epistemic layers rather than a single immediate omniscient explanation.

Supporting evidence in this tranche:
- `Battle Lines`: death/return is first observed, then medically attributed to artificial microbes; Opaka separately supplies prophetic meaning.
- `The Storyteller`: villagers use religious/story language while the apprentice gives an Orb-fragment/collective-cognition explanation.
- `If Wishes Were Horses`: sensor readings suggest a catastrophic subspace rupture before later evidence and observer testimony recast it as imagination-mediated.

Counterexample / caution:
- `Vortex` includes extraordinary-origin claims that turn out to be deliberate or strategic misinformation, showing that layered evidence does not imply all layers are partially true.

Disconfirming search target:
- Cases where extraordinary causation is directly and independently established early, remains stable, and is not materially complicated by testimony, altered frame, sensor ambiguity, or later reinterpretation.

### H3 — Self-concept is socially and institutionally pressured rather than merely stated

**Hypothesis:** Character self-concepts are repeatedly tested by changed roles, external expectations, or social narratives.

Supporting evidence:
- Kira contrasts resistance identity with both the prison war in `Battle Lines` and her new institutional authority in `Progress`.
- Miradorn twin identity in `Vortex` is expressed through a culturally meaningful self-description under bereavement.
- O'Brien's unwanted Sirah role in `The Storyteller` demonstrates social assignment of identity/authority that does not automatically match personal acceptance or competence.

Disconfirming search target:
- Repeated cases where asserted identity remains untouched by role, social recognition, institutional position, embodiment, or narrative pressure.

## Neutral coding summary

Across the five works, salient source-supported dimensions include:

- plot/problem structure: criminal custody and deception; perpetual warfare; ritual/community crisis; forced relocation; imagination-mediated anomaly
- agency/decision: Odo's prisoner disposition; Opaka's choice to remain; apprentice assuming Sirah role; Kira's evacuation decision; Sisko's decision to reject the apparent rupture
- institutions/rules: extradition/custody; penal exile; Bajoran village leadership; public infrastructure/relocation; station emergency command
- interpersonal dynamics: Odo/Croden; Kira/Opaka; O'Brien/apprentice; Kira/Mullibok; Bashir/actual Dax/manifested Dax
- identity/self-concept: Miradorn twin testimony; Kira's relationship to violence and authority; assigned Sirah status; manifested-person representation
- epistemic patterns: deceptive testimony; medical explanation versus prophecy; attributed Orb mechanism; competing public/private claims; sensor interpretation revised by later evidence
- ethics/value conflict: prisoner protection versus custody; endless punishment/war; inherited grievance; public benefit versus individual autonomy; privacy and embodied fantasy
- technology/material constraints: stasis/key object; resurrection microbes; Orb fragment; lunar energy project; subspace/sensor phenomena
- culture/politics: Rakhari legal authority; Bajoran faith; village/land politics; post-occupation development; interspecies observation
- consequences/unresolved: Odo's origin remains unresolved; prison war continues; Dal'Rok mechanism not exhaustively established; Mullibok is coerced off Jeraddo; imagination mechanism remains only partly explained

## Promotion blockers

This staging packet cannot honestly become a governed completed batch yet because accepted state lacks:

1. accepted research architecture/schema and predicate registry;
2. Librarian-owned canonical Work records for these five episodes;
3. Librarian-owned Source records/variants and lineage analysis;
4. reproducible content hashes for the source representations actually used;
5. accepted Source→Work bindings;
6. a governed manifest/coverage transition built against those accepted inputs.

Until those exist:

- canonical IDs are not invented;
- `SOURCE_BOUND` is not claimed;
- accepted coverage remains unchanged;
- no global identity reconciliation is attempted;
- the five complete close reads are preserved only as proposal research staging.

## Proposal frontier after this tranche

Proposal research has now processed the first fifteen season-one broadcast works through `If Wishes Were Horses`.

If infrastructure remains blocked after the next accepted-state refresh, the next bounded five-work provisional research tranche is:

1. The Forsaken
2. Dramatis Personae
3. Duet
4. In the Hands of the Prophets
5. The Homecoming

This crosses the season boundary after completing season one; exact Work identity/order must still be refreshed from accepted registry state before any governed batch claim.