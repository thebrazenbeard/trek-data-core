# Prodigy opening-five close-read staging packet

Status: **PROPOSAL / STAGING ONLY**  
Lane: **PRO (Star Trek: Prodigy)**  
Base accepted state inspected: `main` at `d58359a207da89e812d0a0330558c66774ed1241`  
Research date: 2026-08-14

## Why this is staging rather than a governed batch

Accepted `main` contained only `README.md` when this pass began. It had no accepted Librarian-owned Source/Work registry, Prodigy inventory, research schema, predicate registry, coverage ledger, or prior PRO batch.

This packet therefore does **not**:

- create canonical `source_id` or `work_id` values;
- claim SOURCE_BOUND or any later accepted coverage state;
- resolve the premiere's work/episode segmentation;
- merge Prodigy occurrences with global legacy-character identities;
- treat holograms, simulations, recordings, memories, generated lures, or represented persons as physically present antecedents;
- commit complete copyrighted transcript text.

It preserves a completed full-transcript close-read so that it can later be converted into governed records after accepted source binding and schema/predicate validation exist.

## Bounded research unit actually processed

Five contiguous **titled transcript works/pages** were read in full:

1. `Lost & Found (Part 1, Part 2)` — transcript source presents the two-part premiere as one combined page.
2. `Starstruck`.
3. `Dreamcatcher`.
4. `Terror Firma`.
5. `Kobayashi`.

This title-level grouping is deliberately not asserted as the canonical Work registry. Source indexes disagree on segmentation: Springfield Springfield exposes the premiere as one combined `s01e01` page, Forever Dreaming labels it `01x01 & 01x02`, while subtitle inventories expose separate `1x01` and `1x02` files. Librarian/source-binding work must resolve the registry representation without losing those source variants.

## Full-source retrieval notes

The close read used complete third-party transcript bodies, not recaps or snippets.

- Springfield Springfield — `Lost & Found (Part 1, Part 2)`: https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s01e01&tv-show=star-trek-prodigy-2021
- Forever Dreaming — `Starstruck`: https://transcripts.foreverdreaming.org/viewtopic.php?t=55261
- Forever Dreaming — `Dreamcatcher`: https://www.transcripts.foreverdreaming.org/viewtopic.php?t=55262
- Springfield Springfield — `Terror Firma`: https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s01e05&tv-show=star-trek-prodigy-2021
- Springfield Springfield — `Kobayashi`: https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s01e06&tv-show=star-trek-prodigy-2021

Crosscheck/index sources consulted for segmentation/discovery only:

- Forever Dreaming Prodigy transcript index: https://www.transcripts.foreverdreaming.org/viewforum.php?f=1133
- Springfield Springfield Prodigy episode-script index: https://www.springfieldspringfield.co.uk/episode_scripts.php?tv-show=star-trek-prodigy-2021
- TVsubtitles season-one inventory exposing separate `1x01` / `1x02` subtitle files: https://www.tvsubtitles.net/subtitle-3134-1-en.html

No transcript-source byte hash is asserted here because source identity, variant lineage, hashes, and preferred-source decisions belong to the Librarian. Primary audiovisual media was not directly verified in this pass. Transcript lineage independence is unresolved.

## Staging-label convention

Labels such as `PRO-STG-EV-001` below are packet-local navigation labels only. They are **not canonical IDs** and must not survive migration merely because they look official.

---

# 1. Lost & Found (Part 1, Part 2)

## Local entity candidates

- Dal R'El occurrence.
- Rok-Tahk occurrence.
- Zero occurrence, with explicit distinction between the Medusan non-corporeal life-form and the containment suit Zero built and inhabits/uses.
- Jankom Pog occurrence.
- Murf occurrence.
- Gwyndala/Gwyn occurrence.
- The Diviner occurrence.
- Drednok occurrence.
- USS Protostar occurrence.
- Tars Lamora mining/prison complex occurrence.
- Hologram Janeway occurrence activated at the end of the combined transcript.

No global SAME_AS relations are proposed.

## Source-relative evidence notes

- `PRO-STG-EV-001` — Dal is held as a prisoner/laborer on Tars Lamora and repeatedly attempts escape; the facility suppresses translation among prisoners. **Kind:** depiction/action + dialogue.
- `PRO-STG-EV-002` — Gwyn acts as translator/intermediary for the Diviner and expresses incomplete knowledge of his plan. **Kind:** dialogue/testimony.
- `PRO-STG-EV-003` — The Diviner tells Drednok that Gwyn must not learn the true purpose of the search and specifically fears Federation influence. This supports the utterance and secrecy policy, not yet the ultimate truth of his mission. **Kind:** dialogue/testimony.
- `PRO-STG-EV-004` — Zero describes themself as a Medusan energy-based/non-corporeal life-form and separately describes building the containment suit. **Kind:** dialogue/testimony corroborated by ongoing depiction of suit-mediated embodiment.
- `PRO-STG-EV-005` — Zero reports having been captured, used as a weapon, and later escaping. This is Zero's testimony; the historical events are not independently depicted in this work. **Kind:** recollection/testimony.
- `PRO-STG-EV-006` — Dal and Rok activate a translator aboard the buried Protostar and can then communicate; the translation event changes their practical social coordination. **Kind:** depiction/action.
- `PRO-STG-EV-007` — Dal, Rok, Zero, Jankom, and Murf cooperate to launch and escape aboard the Protostar despite limited competence and conflicting motives. **Kind:** depiction/action.
- `PRO-STG-EV-008` — Gwyn initially helps the Diviner locate the Protostar, then is taken aboard during the escape. **Kind:** depiction/action.
- `PRO-STG-EV-009` — At the end of the transcript a Janeway-form entity identifies herself as Hologram Janeway and a Starfleet training advisor. **Kind:** depiction + self-identification.

## Candidate assertions

- `PRO-STG-AS-001` — The opening work frames communication infrastructure as a material condition of collective agency: the prison suppresses translators, while the Protostar's translator enables a multi-species escape coalition. **Interpretive; links EV-001, EV-006, EV-007.**
- `PRO-STG-AS-002` — Zero's person/body relation should not be modeled as ordinary biological embodiment; source evidence explicitly distinguishes the Medusan life-form from the constructed containment suit. **Interpretive/identity-structure; links EV-004.**
- `PRO-STG-AS-003` — Gwyn's allegiance is already non-binary: she participates in the Diviner's control system but also negotiates, hesitates, and becomes entangled with the escapees. **Interpretive; links EV-002, EV-008.**
- `PRO-STG-AS-004` — Hologram Janeway enters as a new local entity occurrence whose relation to any antecedent Kathryn Janeway is not resolved by appearance/name alone. **Identity-preservation assertion; links EV-009.**

## Counterevidence / uncertainty

- Zero's account of prior weaponization is first-person testimony, not direct depiction in this work.
- The Diviner's statements about being among the last Vau N'Akat and Gwyn's future are assertions by an interested actor; they are not yet promoted to objective fictional truth here.
- The combined transcript page prevents this worker from deciding whether the premiere is one Work, two Works, or one multipart Work with two contained installments.

---

# 2. Starstruck

## Local entity candidates

- Dal, Rok-Tahk, Zero, Jankom Pog, Murf, Gwyn, Diviner, Drednok.
- USS Protostar.
- **Hologram Janeway**, explicitly a holographic training advisor based on a decorated Starfleet captain.
- Binary star system / gravity-well hazard.

## Source-relative evidence notes

- `PRO-STG-EV-010` — Janeway explicitly identifies herself as a hologram based on a decorated Starfleet captain and says she is programmed to assist the Protostar crew's journey toward Federation space. **Kind:** self-identification/dialogue.
- `PRO-STG-EV-011` — Janeway describes her authority as advisory plus maintenance of lower-level ship functions; she leaves broader choices to the crew. **Kind:** dialogue/testimony.
- `PRO-STG-EV-012` — The crew falsely presents themselves as Starfleet cadets; Janeway accepts that frame. **Kind:** depiction/dialogue.
- `PRO-STG-EV-013` — Janeway provides a Federation/Starfleet institutional description. This establishes what this holographic advisor communicates, not automatically a complete constitutional truth about the Federation. **Kind:** institutional testimony.
- `PRO-STG-EV-014` — Dal distrusts authority from prior experience and resists seeking Federation assistance. **Kind:** dialogue/self-report.
- `PRO-STG-EV-015` — Zero attempts telepathic reading of Gwyn and reports unusual resistance that Zero infers may be inherited. The inheritance claim remains Zero's inference. **Kind:** sensor-like mental perception/testimony.
- `PRO-STG-EV-016` — The crew's chosen course puts the Protostar into a severe stellar hazard after Dal rejects Janeway's offered navigation help. **Kind:** depiction/action.
- `PRO-STG-EV-017` — Dal eventually asks Janeway for help; she guides the crew through ship-control recovery while the crew performs the actions. **Kind:** depiction/action.
- `PRO-STG-EV-018` — The successful escape also depends on Zero's idea to exploit the stellar shock wave; Janeway explicitly credits the crew rather than herself alone. **Kind:** depiction/dialogue.

## Candidate assertions

- `PRO-STG-AS-005` — Hologram Janeway functions as inherited institutional knowledge without being treated as physically present antecedent-Janeway. **Interpretive; links EV-010, EV-011, EV-013.**
- `PRO-STG-AS-006` — The work contrasts Dal's experience-grounded distrust of authority with the crew's attraction to Federation ideals; neither position is coded as a corpus-level truth claim here. **Interpretive; links EV-013, EV-014.**
- `PRO-STG-AS-007` — Leadership development is depicted as moving from unilateral self-assertion toward asking for and integrating help. **Interpretive; links EV-016, EV-017, EV-018.**

## Counterevidence / uncertainty

- Janeway's Federation description is institutionally framed speech from a programmed advisor, not an omniscient narration.
- Dal's claim that authorities lie is autobiographical generalization, not evidence that the Federation specifically deceives the crew.
- Zero's claim that Gwyn's telepathic resistance is inherited remains an inference in-source.

---

# 3. Dreamcatcher

## Local entity candidates

- Dal, Rok-Tahk, Zero, Jankom Pog, Murf, Gwyn.
- Hologram Janeway.
- USS Protostar and Runaway vehicle.
- Uncharted M-class planetary superorganism.
- Planet-generated desire/lure representations, including apparent parent figures/voices, appealing creatures/food, an apparent engine-object, and an apparent Diviner. These are local representational phenomena, **not** merged with the persons/objects they imitate.

## Source-relative evidence notes

- `PRO-STG-EV-019` — Janeway proposes a Federation-style survey of an M-class planet after sensors report no sentient life-forms. **Kind:** computer/sensor report relayed by holographic advisor.
- `PRO-STG-EV-020` — Janeway states that holograms cannot leave the ship, constraining her participation in the away mission. **Kind:** dialogue/self-report, consistent with depiction in this work.
- `PRO-STG-EV-021` — Gwyn escapes confinement, accesses ship controls using training her father provided, and contacts the Diviner. **Kind:** depiction/action + recollection of training.
- `PRO-STG-EV-022` — Multiple crew members encounter highly personalized desirable phenomena that appear real to their senses. **Kind:** altered perception/depiction.
- `PRO-STG-EV-023` — A representative/lure encountered by Dal states that the planetary life can perceive desires and fabricate them. **Kind:** testimony from an uncertain/generated frame.
- `PRO-STG-EV-024` — Zero later characterizes the planet as a superorganism that fabricates desires onto cilia to lure and consume prey; spores are said to cloud minds and senses. **Kind:** analysis/testimony within the episode.
- `PRO-STG-EV-025` — Rok's appealing creatures and Jankom's food are explicitly rejected by the crew as unreal despite sensory vividness. **Kind:** depiction + dialogue.
- `PRO-STG-EV-026` — Gwyn recognizes an apparent Diviner as not her father, rejecting the lure representation. **Kind:** depiction/dialogue.
- `PRO-STG-EV-027` — The planet entangles the Protostar; Gwyn's attempt to use the ship leaves the crew stranded at the episode end. **Kind:** depiction/action.

## Candidate assertions

- `PRO-STG-AS-008` — Desire-lure figures must be represented as generated/altered-perception phenomena rather than ordinary physical occurrences of the depicted persons or objects. **Identity/frame assertion; links EV-022 through EV-026.**
- `PRO-STG-AS-009` — Sensor output initially reports no sentient life while later crew analysis treats the planet as a sentient/superorganism-like agent; this is an epistemic update, not evidence that the earlier sensor report never occurred. **Interpretive; links EV-019, EV-024.**
- `PRO-STG-AS-010` — Hologram Janeway's inability to leave the ship is a material boundary on her agency in this work. **Interpretive; links EV-020.**

## Counterevidence / uncertainty

- The planet/lure's own explanation of its abilities comes from within the manipulated frame and should not stand alone as objective truth.
- Zero's later superorganism explanation is stronger in context but still a character analysis, not omniscient narration.
- Individual desire-scenes cannot be mined as straightforward biography without preserving that they were induced/fabricated experiences.

---

# 4. Terror Firma

## Local entity candidates

- Dal, Rok-Tahk, Zero, Jankom Pog, Murf, Gwyn, Diviner, Drednok.
- Hologram Janeway.
- USS Protostar.
- Planetary superorganism / mobile terrain and generated threat phenomena.
- Protostar's gravimetric containment/protostar-drive system.

## Source-relative evidence notes

- `PRO-STG-EV-028` — Hologram Janeway remains aboard the ship and independently attempts to protect it from the invasive planetary organism using systems available to her. **Kind:** depiction/action.
- `PRO-STG-EV-029` — Janeway asks herself what the “real Janeway” would do, explicitly distinguishing the holographic advisor from the antecedent/person-model she references. **Kind:** self-directed dialogue with identity relevance.
- `PRO-STG-EV-030` — The crew observes terrain changes and concludes the planet is reshaping routes to keep them from the ship. **Kind:** depiction + interpretation.
- `PRO-STG-EV-031` — Characters discuss earlier personalized desire experiences and recognize them as not real despite emotional impact. **Kind:** recollection/dialogue.
- `PRO-STG-EV-032` — Dal describes wanting someone to tell him what species/family origin he has, while rejecting the claim that this means he straightforwardly wants his parents. **Kind:** self-report with internal nuance.
- `PRO-STG-EV-033` — Gwyn's heirloom and knowledge help the group navigate and survive; the others' attitude toward her begins to change. **Kind:** depiction/action + interpersonal response.
- `PRO-STG-EV-034` — The Diviner chooses pursuit of the Protostar over immediately rescuing Gwyn when she is endangered; Gwyn later frames this as his choice. **Kind:** depiction/action + subsequent interpretation.
- `PRO-STG-EV-035` — Janeway/ship systems reveal a command-restricted gravimetric containment system; the crew realizes the ship's propulsion system contains/uses a protostar. **Kind:** computer report + inference/dialogue.
- `PRO-STG-EV-036` — Gwyn chooses the crew over the Diviner's demand and activates the proto-drive, escaping beyond the pursuer's maps. **Kind:** depiction/action.

## Candidate assertions

- `PRO-STG-AS-011` — The hologram's own reference to “real Janeway” is direct evidence against silently treating Hologram Janeway as an ordinary physical occurrence of antecedent Janeway. **Identity-preservation assertion; links EV-029.**
- `PRO-STG-AS-012` — Emotional content learned from generated lures may still be character evidence about desires/fears, but the represented events/persons remain frame-qualified. **Interpretive; links EV-031, EV-032.**
- `PRO-STG-AS-013` — Gwyn's affiliation materially changes through observed choices, but no permanent/global identity or loyalty state is inferred beyond this local work sequence. **Interpretive; links EV-033, EV-034, EV-036.**

## Counterevidence / uncertainty

- Dal explicitly qualifies the simple reading that he “wanted to see his parents”; the packet therefore preserves his more specific desire for origin/species knowledge.
- The protostar-drive explanation is assembled by characters from ship-system evidence and should remain linked to those reports until accepted source reconciliation.

---

# 5. Kobayashi

## Local entity candidates

- Dal, Rok-Tahk, Zero, Jankom Pog, Murf, Gwyn.
- Hologram Janeway.
- USS Protostar.
- **Holodeck simulation environment**.
- Simulated crew representations selected by the holodeck/computer: Uhura, Beverly Crusher, Odo, Spock, and later Scotty. These are simulation-local representations and are not globally merged with legacy persons.
- Simulated Kobayashi Maru, Klingon ships/forces, Enterprise/bridge environment and related no-win scenario elements.
- Recovered/corrupted Protostar data fragments.
- **Recorded Captain Chakotay representation/message** in recovered data; no physical Chakotay presence is established by this scene.

## Source-relative evidence notes

- `PRO-STG-EV-037` — The crew votes to seek the Federation while Dal resists; the group challenges his self-appointed captaincy. **Kind:** dialogue/decision.
- `PRO-STG-EV-038` — Janeway identifies the holodeck as a holographic simulation room containing many programs. **Kind:** holographic advisor testimony + depicted program changes.
- `PRO-STG-EV-039` — Dal selects the Kobayashi Maru training module; the computer populates a simulated crew using named legacy-character representations. **Kind:** simulation/holodeck.
- `PRO-STG-EV-040` — Repeated Kobayashi attempts generate explicit simulation-complete states and performance scores; Dal initially treats success/failure as evidence about his fitness to command. **Kind:** simulation output + character interpretation.
- `PRO-STG-EV-041` — Dal repeatedly restarts the simulation, changes simulated crewmates/tactics, and eventually recognizes the exercise as a no-win scenario about reaction rather than literal victory. **Kind:** simulation + learning/decision.
- `PRO-STG-EV-042` — A simulated Spock representation provides leadership-oriented dialogue; the evidentiary frame is the holodeck simulation, not a physically present Spock occurrence. **Kind:** simulation dialogue.
- `PRO-STG-EV-043` — Zero and Gwyn probe Janeway/ship information about the Protostar. Janeway first appears to have no record, then clarifies that her memory is intact but classified. **Kind:** dialogue about memory/access state.
- `PRO-STG-EV-044` — Gwyn uses Solum/Vau N'Akat language to access encrypted/classified data, reinforcing the distinction between literal translation and interpretation discussed with Zero. **Kind:** depiction/action + dialogue.
- `PRO-STG-EV-045` — Recovered data fragments describe the Protostar as a prototype and expose a corrupted but readable distress recording identifying Captain Chakotay aboard the USS Protostar. **Kind:** log/recording/data fragment.
- `PRO-STG-EV-046` — On seeing the recovered recording, Hologram Janeway recognizes that the present crew was not her first crew. **Kind:** holographic advisor reaction to recorded evidence.

## Candidate assertions

- `PRO-STG-AS-014` — Every named legacy officer inside the Kobayashi program must remain simulation-local unless later reconciliation explicitly relates that representation to an antecedent source/person. **Identity/frame assertion; links EV-038 through EV-042.**
- `PRO-STG-AS-015` — Hologram Janeway's knowledge state is not a simple faithful copy of an antecedent person's accessible memory: this work distinguishes intact memory, classification/access restrictions, and later recovered external data. **Interpretive; links EV-043, EV-045, EV-046.**
- `PRO-STG-AS-016` — Captain Chakotay's appearance in the recovered material is a recorded/data representation. The scene supports that a recording identifies him as Protostar captain; it does not depict him physically present with the current crew. **Frame assertion; links EV-045.**
- `PRO-STG-AS-017` — The episode explicitly treats language competence as interpretation rather than mere token substitution, with practical consequences for access to inherited/encoded information. **Interpretive; links EV-044.**
- `PRO-STG-AS-018` — Dal's leadership development continues through simulation-mediated failure and self-reassessment, but the simulation's assessments remain training outputs rather than objective numeric measures of personhood or worth. **Interpretive; links EV-040, EV-041.**

## Counterevidence / uncertainty

- The holodeck's legacy-character dialogue should not be harvested as direct testimony by the antecedent persons without a separate provenance model for how the program was authored/generated.
- The Chakotay material is corrupted data; the packet records what the readable fragment depicts/reports and leaves broader historical reconstruction unresolved.
- Janeway's statement that her memory is “fine” but classified does not establish the completeness, fidelity, or ontological identity of the hologram's memory relative to any antecedent person.

---

# Cross-work neutral coding

## Plot/problem structure

The sequence moves from prison escape and acquisition of an unfamiliar ship, through basic navigation/crew learning, an apparently hospitable but predatory planetary encounter, escape from the pursuing Diviner, and then deliberate training/investigation aboard the ship.

## Agency and decision points

- Dal repeatedly claims captaincy but the crew increasingly contests unilateral command.
- Gwyn moves from agent/daughter of the Diviner toward collaboration with the escapees through a series of local choices.
- Hologram Janeway advises and operates within system limits but generally does not replace crew decision-making.
- Zero's analysis/telepathy, Jankom's engineering, Rok's physical/social actions, and Gwyn's language/technical knowledge repeatedly supply capabilities Dal lacks.

## Institutions/rules

- Federation/Starfleet principles enter initially through Hologram Janeway's programmed institutional explanation.
- Starfleet protocol is presented by the holographic advisor and by training systems, not omniscient narration.
- The Kobayashi Maru module supplies a deliberately artificial institutional training frame.

## Identity/self-concept

- Dal lacks species/family-origin knowledge and resists simple readings of what he wants.
- Zero explicitly distinguishes non-corporeal self from containment apparatus.
- Hologram Janeway is repeatedly source-distinguished from an antecedent/“real” Janeway and from later recovered crew records.
- Simulation-local legacy figures and recorded Chakotay require frame-specific representation.

## Epistemic/evidence patterns

- Sensor reports can be incomplete or overtaken by later analysis (`Dreamcatcher`).
- Personalized perception can be fabricated by an environmental organism.
- Testimony from interested actors (Diviner, Gwyn, Dal, Zero) is informative without automatic world-state promotion.
- Classified memory/access restrictions differ from memory loss.
- Corrupted recordings can still provide partial evidence while preserving uncertainty.

## Ethics/value conflict

- Escape/liberty versus imposed order.
- Individual command authority versus crew consent.
- Rescue obligations versus self-preservation.
- Loyalty to parent/creator authority versus observed treatment of others.
- Training-system judgment versus learning through failure.

## Technology/material constraints

- Translation and universal-translation access materially shape who can coordinate.
- Holographic embodiment limits Janeway's location/action.
- Replicators, ship power allocation, containment fields, holodeck simulation, encrypted data, and proto-drive systems create concrete constraints rather than decorative lore.

## Consequences/unresolved threads

- The Diviner's actual mission and history remain unresolved in this packet.
- Protostar provenance and prior-crew history remain only partially exposed.
- Dal's origin remains unresolved.
- The exact technical and ontological relation between Hologram Janeway, her model/antecedent, her classified memory, and ship records remains intentionally unresolved pending further evidence and global reconciliation.

# Cross-work hypothesis tests (provisional)

These are not corpus conclusions.

### H1: Prodigy initially treats institutional knowledge as mediated rather than automatically authoritative.

**Support:** Hologram Janeway is a programmed training advisor; she supplies Federation/Starfleet knowledge while also having role limits and classified information. The crew sometimes benefits from her expertise and sometimes resists it.  
**Neutral:** Ship systems and training modules also provide technical/institutional information without requiring a person-level authority claim.  
**Disconfirming search target:** later works in which institutional claims are independently verified, contradicted, overridden, or exposed as program-specific.

### H2: Early crew formation is driven by complementary capability more than preexisting identity or loyalty.

**Support:** translation, telepathy, engineering, strength, language expertise, piloting, and advisory knowledge repeatedly become mutually necessary.  
**Neutral:** several alliances remain opportunistic or contested.  
**Disconfirming search target:** evidence that stable loyalty precedes or overrides practical interdependence.

### H3: Prodigy uses represented persons in multiple non-equivalent frames.

**Support:** Hologram Janeway, desire-lure figures, holodeck legacy officers, and recorded Chakotay are explicitly presented through different mechanisms.  
**Neutral:** ordinary physically present characters coexist with these frames.  
**Disconfirming search target:** later evidence collapsing or transforming one of these mechanisms in a way that changes the relevant identity relation.

# Promotion blockers

This staging packet cannot become an accepted governed research batch until at least:

1. Librarian/source-binding work supplies accepted Prodigy Work identities, including a decision/representation for the `Lost & Found` two-part segmentation.
2. Accepted Source records/variants establish reproducible source identity, lineage, and hashes for the transcript or preferred full source used.
3. The accepted research schema and predicate registry exist on `main`.
4. Staging notes are converted into structured Local Entity, Evidence, Assertion, manifest, and coverage records under those accepted contracts.
5. Deterministic validation passes on that governed batch.

Until then, accepted Prodigy coverage remains unchanged.
