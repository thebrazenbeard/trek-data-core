# SFA S01 B001 Staging — Kids These Days

Status: `STAGING_CLOSE_READ_COMPLETE`
Role: `SFA` — Star Trek: Starfleet Academy Research & Index
Authority: proposal-only; not accepted coverage; not SOURCE_BOUND

This packet preserves one completed full-transcript close read while accepted `main` still lacks a Librarian-owned Work/Source registry. It does not create canonical Work IDs or Source IDs, does not advance accepted coverage, and does not globally reconcile any legacy character, institution, technology, or historical reference.

## Accepted-state pin

- repository: `thebrazenbeard/trek-data-core`
- accepted branch at start: `main`
- accepted head observed: `d58359a207da89e812d0a0330558c66774ed1241`
- accepted SFA Work registry observed: absent
- accepted SFA Source registry observed: absent
- accepted SFA coverage ledger observed: absent

## Current external inventory observation — discovery only

Observed 2026-08-14 from the official Paramount+ Starfleet Academy page. This is a current external discovery snapshot, **not** an accepted project denominator and not a replacement for the Librarian-owned Work registry.

Paramount+ currently exposes one season with ten episode entries:

1. Kids These Days — 2026-01-15
2. Beta Test — 2026-01-15
3. Vitus Reflux — 2026-01-22
4. Vox in Excelso — 2026-01-29
5. Series Acclimation Mil — 2026-02-05
6. Come, Let's Away — 2026-02-12
7. Ko'Zeine — 2026-02-19
8. The Life of the Stars — 2026-02-26
9. 300th Night — 2026-03-05
10. Rubincon — 2026-03-12

Discovery source:
`https://www.paramountplus.com/shows/star-trek-starfleet-academy/`

Source-binding anomaly for Librarian review: Springfield's season index renders episode 10 as `Rubicon`, while the current official Paramount+ listing renders `Rubincon`. No correction is made here.

## Staged work

Provisional work label: `SFA-S01E01-KIDS-THESE-DAYS`
Title: `Kids These Days`
Official release observation: 2026-01-15
Official runtime observation: approximately 1h15m on Paramount+

No canonical `work_id` is minted in this worker packet.

## Full-source retrieval and read

Full-text representation used for close read:
`https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s01e01&tv-show=star-trek-starfleet-academy-2026`

Observed page identity: `Star Trek: Starfleet Academy (2026) s01e01 Episode Script — Kids These Days`.

Read status:
- transcript body read end-to-end from opening through final scene;
- page exposes approximately 2,079 indexed lines, with episode body occupying roughly lines 13–2073;
- line windows were revisited around the attack transition to ensure no skipped content;
- primary audiovisual media was not directly inspected in this unit;
- transcript-provider lineage and independence are unresolved;
- no reproducible source-byte hash is claimed because the worker did not obtain a stable source artifact byte stream.

Therefore this packet is `CLOSE_READ` staging only. It does not claim `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE` in accepted registry state, or accepted semantic coverage.

## Local entity candidates

All identities below are work-local only.

- `SFA01-LE-001` — Caleb Mir, adult cadet/prisoner occurrence
- `SFA01-LE-002` — young Caleb Mir occurrence
- `SFA01-LE-003` — Nahla Ake occurrence
- `SFA01-LE-004` — Anisha Mir occurrence
- `SFA01-LE-005` — Nus Braka occurrence
- `SFA01-LE-006` — Charles Vance occurrence
- `SFA01-LE-007` — Lura Thok occurrence
- `SFA01-LE-008` — Jay-Den Kraag occurrence
- `SFA01-LE-009` — Darem Reymi occurrence
- `SFA01-LE-010` — Genesis occurrence
- `SFA01-LE-011` — Series Acclimation Mil / Sam occurrence
- `SFA01-LE-012` — the Doctor occurrence
- `SFA01-LE-013` — USS Athena occurrence
- `SFA01-LE-014` — Starfleet Academy occurrence
- `SFA01-LE-015` — Venari Ral occurrence/group
- `SFA01-LE-016` — Federation occurrence/institution
- `SFA01-LE-017` — Starfleet occurrence/institution
- `SFA01-LE-018` — Little Blooms school occurrence
- `SFA01-LE-019` — Scrap occurrence
- `SFA01-LE-020` — Digital Dean of Students occurrence

No claim is made that any local entity above is globally identical to same-named entities in Discovery, Voyager, Prodigy, or any other work.

## Source-relative evidence notes

`SFA01-E001` — Frame: narration/dialogue. Nahla describes Starfleet Academy as having ceased after the Burn and presents its return as institutional rebuilding. Locator: transcript lines ~19–31.

`SFA01-E002` — Frame: depicted childhood interaction. Anisha teaches young Caleb a private mnemonic/code associated with moons and a promised future journey to Earth. Locator: ~33–84.

`SFA01-E003` — Frame: hearing/dialogue. Nahla attributes a Federation supply-vessel death to the theft operation involving Braka and Anisha; Braka frames his conduct as providing food during scarcity. These are conflicting character accounts within the same proceeding. Locator: ~97–150.

`SFA01-E004` — Frame: institutional action/dialogue. Nahla tells Anisha that Caleb will become a Federation ward and tells Caleb she will try to keep him safe and reunite him with his mother. Locator: ~145–228.

`SFA01-E005` — Frame: computer/drone report. Fifteen years later, a system identifies Caleb as 21 and lists a sequence of juvenile and adult offenses. Locator: ~250–275.

`SFA01-E006` — Frame: computer report. Caleb searches for Anisha and receives a result that she is absent from known databases. This establishes the report, not her objective status. Locator: ~295–321.

`SFA01-E007` — Frame: dialogue/recollection. Vance recruits Nahla as chancellor; Nahla says she resigned because of the mother-child separation and rejects Vance's claim that she had no choice. Locator: ~365–456.

`SFA01-E008` — Frame: dialogue. Vance reports Caleb has been found alive; Nahla later offers Caleb Academy service as an alternative available under a Federation/Toroth arrangement and says Anisha escaped custody a year earlier. Locator: ~457–545.

`SFA01-E009` — Frame: depiction/institutional announcement. The USS Athena is presented as both a ship and a major Academy learning environment paired with the San Francisco campus. Locator: ~554–605 and ~773–831.

`SFA01-E010` — Frame: self-identification/dialogue. Lura Thok introduces herself through Klingon and Jem'Hadar lineage language. This establishes her stated lineage framing, not a global genealogy resolution. Locator: ~592–630.

`SFA01-E011` — Frame: dialogue. Jay-Den identifies a medical/scientific specialization and says he seeks a valiant life rather than a valiant death. Locator: ~642–661.

`SFA01-E012` — Frame: dialogue. The Doctor serves as chief medical officer and later says he added an aging program to his matrix roughly five centuries earlier to put organics at ease. Locator: ~727–839 and ~1011–1060.

`SFA01-E013` — Frame: self-report/dialogue. Sam identifies as Series Acclimation Mil, prefers the term photonic, says she was programmed to feel 17, has existed a little over four months, and comes from a photonic colony on Kasq. Locator: ~1020–1074.

`SFA01-E014` — Frame: dialogue/testimony. Sam references the Doctor's prior mentorship of Voyager crew and the Protostar children; the Doctor does not elaborate and redirects. This is retained as dialogue evidence only. Locator: ~1080–1099.

`SFA01-E015` — Frame: depiction/computer report. Caleb overrides an Academy communication subsystem and sends a private message to his mother using the childhood code. Locator: ~1104–1134.

`SFA01-E016` — Frame: sensor reports and depiction. Athena detects anomalous readings that are revealed as sensor deception preceding a multi-contact attack. Locator: ~1181–1244.

`SFA01-E017` — Frame: sensor/crew reports and depiction. A programmable-matter variant engulfs the Athena and disrupts helm, weapons, transporters, power, and other systems. Locator: ~1247–1368.

`SFA01-E018` — Frame: depiction/dialogue. Lura is seriously injured; cadets move her to a training medical space and perform emergency stabilization under her direction. Locator: ~1308–1390 and ~1585–1620.

`SFA01-E019` — Frame: antagonist dialogue. Braka says an intercepted message exposed Athena's location and demands access to the warp drive for resale. Nahla characterizes the attack as an act of war. Locator: ~1397–1512.

`SFA01-E020` — Frame: operational reports. Bridge officers report that weapons and propulsion options are effectively unavailable and outside help will not arrive in time. A report says Discovery is undergoing retrofit; this is not globally reconciled here. Locator: ~1513–1534.

`SFA01-E021` — Frame: dialogue/depiction. Caleb proposes exploiting the attacking programmable matter's identifying coefficient and integration behavior; Nahla authorizes him to continue. Locator: ~1535–1577.

`SFA01-E022` — Frame: self-report plus depiction. Darem claims Khionian physiology allows brief survival in extreme pressure/temperature conditions, exits the ship without an EV suit, and subsequently experiences a dangerous body-temperature decline. Locator: ~1643–1660 and ~1695–1807.

`SFA01-E023` — Frame: dialogue/testimony. Genesis says her father is a Starfleet admiral and that she has received training since early childhood. Locator: ~1697–1710.

`SFA01-E024` — Frame: depiction/dialogue. The Doctor provides a command override after Genesis explains that access is needed to save Darem's life. Locator: ~1756–1789.

`SFA01-E025` — Frame: simulation explicitly identified by computer. Academy Mode / Ramcon Six creates a false warp-core emergency that causes the boarding party to react; the computer then identifies the event as a simulation when it ends. Locator: ~1903–1933.

`SFA01-E026` — Frame: antagonist testimony. Braka implies that something happened to Anisha on Goja V after a prison escape but does not establish the event before the confrontation resumes. Her status remains unresolved. Locator: ~1937–1969.

`SFA01-E027` — Frame: depiction/computer report. Caleb's protocol succeeds, followed by reports that shields and weapons are restored. Locator: ~1957–1976.

`SFA01-E028` — Frame: institutional dialogue. Nahla says the hearing committee found Caleb's unauthorized communications endangered the ship and were expulsion grounds, while also crediting his crisis initiative and command potential. Locator: ~2019–2044.

`SFA01-E029` — Frame: personal testimony/recollection. Nahla says she had a son who was an Academy cadet and whose class was aboard a ship when the Burn occurred. This establishes her account and its role in her decision-making. Locator: ~2045–2064.

`SFA01-E030` — Frame: dialogue/decision. Caleb accepts a conditional Academy stay involving campus restriction and menial-labor obligations, while explicitly limiting the commitment to the present. Locator: ~2065–2072.

## Candidate assertions

All assertions are `PROPOSED_STAGING` and must be rebound to accepted evidence records before promotion.

`SFA01-A001` — The episode frames the Academy's reopening as part of a broader institutional reconstruction project after the Burn. Evidence: E001, E007, E009.

`SFA01-A002` — Caleb's entry into Starfleet Academy is not depicted as purely voluntary aspiration; it begins as a negotiated alternative to punitive custody and remains conditional. Evidence: E008, E028, E030.

`SFA01-A003` — Nahla's leadership arc in this work is materially shaped by her judgment that prior institutional compliance caused preventable harm. Evidence: E004, E007, E029.

`SFA01-A004` — The work explicitly contrasts rule/institutional procedure with discretionary ethical responsibility rather than treating procedure as self-justifying. Evidence: E003, E007, E028.

`SFA01-A005` — The Academy's local educational model combines terrestrial campus instruction with starship-based experiential training. Evidence: E009.

`SFA01-A006` — During the attack, cadet competence emerges through improvised cooperation across technical, medical, and command problems rather than through one designated hero alone. Evidence: E018, E021–E025, E027.

`SFA01-A007` — Sam's local identity presentation distinguishes programmed subjective age from elapsed existence and explicitly uses photonic rather than hologram as preferred self-description. Evidence: E013.

`SFA01-A008` — The Doctor's local presentation distinguishes matrix chronology from chosen apparent aging, making age/embodiment dimensions potentially relevant without resolving his global continuity. Evidence: E012.

`SFA01-A009` — Jay-Den's self-concept resists a warrior-death expectation by orienting Klingon identity toward medicine and preservation of life. Evidence: E011, E018.

`SFA01-A010` — Darem's extraordinary environmental tolerance is supported by both his claim and risky behavior but the exact physiological limits remain unverified within this source. Evidence: E022.

`SFA01-A011` — Anisha's present status is unresolved in this work: database absence, Nahla's escape report, and Braka's later insinuation do not converge on a verified outcome. Evidence: E006, E008, E026.

`SFA01-A012` — Caleb's trust in Nahla and Starfleet remains conditional at episode end rather than becoming complete institutional identification. Evidence: E007, E008, E028, E030.

`SFA01-A013` — The disciplinary resolution holds two propositions simultaneously: Caleb caused serious institutional risk and also demonstrated valued crisis capability. Evidence: E028.

`SFA01-A014` — The Ramcon Six sequence must remain coded as a simulation used tactically inside baseline diegesis, not as an objective warp-core failure. Evidence: E025.

`SFA01-A015` — Cross-series references to Discovery, Voyager, Prodigy-era persons, and historical Starfleet are evidence of statements/appearances in this work only; global continuity links remain reconciliation work. Evidence: E012, E014, E020.

## Explicit counterevidence and unresolved points

1. **Institutional necessity vs individual agency:** Vance initially frames the historic separation as something Nahla could not avoid; Nahla explicitly rejects that framing and says she had alternatives. Both statements are preserved.
2. **Braka's famine justification vs criminal harm:** Braka frames himself as providing a practical food solution; Nahla attributes a dead shuttle pilot and exploitation of Anisha to his operation. The worker does not convert either speaker's rhetoric into omniscient motive truth.
3. **Anisha status:** absent from databases, reportedly escaped, later referenced by Braka in connection with Goja V. Outcome remains `UNRESOLVED`.
4. **Darem physiology:** his self-report is partly behavior-supported, but his rapid temperature decline during EVA limits any simplistic claim of invulnerability.
5. **Sam/Doctor photonic identity:** Sam is described as the first holographic/photonic student while the Doctor clearly predates her as a photonic person. These propositions are not contradictory because the relevant class is student status, not existence.
6. **Doctor history:** prior Voyager/Protostar mentorship is raised in dialogue, but this worker does not globally merge the local Doctor occurrence with prior-series entities.
7. **Discovery status:** the retrofit reference is an in-work operational report and is not used here to mutate Discovery coverage or timeline state.
8. **Simulation frame:** the apparent warp-core emergency is explicitly terminated as Ramcon Six simulation content; treating it as a real core breach would violate source-relative coding.
9. **Caleb's institutional commitment:** accepting the conditional stay does not erase his repeated distrust or establish permanent allegiance.

## Neutral coding summary

- plot/problem structure: coerced/conditional recruitment develops into a first-day ship crisis and disciplinary choice;
- agency/decision points: Nahla's recruitment choice, Caleb's decision to use unauthorized communication, cadet improvisation during attack, final decision to remain;
- institutions/rules: Federation penal/rehabilitation systems, Academy admission/service arrangement, command authorization, cadet discipline, hearing committee;
- interpersonal dynamics: Caleb–Nahla distrust/repair, Caleb–Jay-Den emergent friendship, Genesis–Darem rivalry/attraction, Sam–Doctor awkward mentorship attempt;
- identity/self-concept: Sam's photonic age/existence distinction, Doctor's self-modified aging, Jay-Den's medical orientation, Darem's Khionian self-conception;
- epistemic patterns: conflicting testimony around past culpability, database absence, antagonist insinuation, sensor deception, simulation masking;
- ethics/value conflict: institutional accountability, family separation, punitive rehabilitation, trust, rule-breaking during crisis;
- technology/material constraints: programmable matter, system integration, transporter loss, environmental exposure, deflector-mediated hack, simulation mode;
- culture/politics: post-Burn rebuilding, Federation legitimacy, first-of-species Academy participation claims;
- continuity/worldbuilding: Academy reopening after >120 years, Earth/San Francisco return, legacy Doctor references, Discovery retrofit report;
- character-state changes: Caleb moves from intending to leave toward conditional participation; Nahla resumes Starfleet command/chancellorship; cadets form initial working relationships;
- consequences/unresolved threads: Anisha's status, Braka's continuing threat, Caleb's 90-day restriction, unresolved global identity/continuity links.

## Provisional cross-work hypotheses for later testing

`SFA-H001` — The series may repeatedly test Starfleet's legitimacy through cadets whose biographies give them reasons to distrust institutions.
- current support: E007, E008, E028, E030.
- disconfirming target: later works where institutional legitimacy is simply assumed and distrust is neither revisited nor consequential.

`SFA-H002` — Photonic personhood and identity may become a sustained topic rather than incidental characterization.
- current support: E012–E014.
- disconfirming target: later works treating Sam/Doctor photonic distinctions only as exposition or comedy without agency/personhood consequences.

`SFA-H003` — Academy pedagogy may repeatedly rely on real operational crises and experiential decision-making rather than classroom instruction alone.
- current support: E009, E016–E027.
- disconfirming target: evidence that the premiere is exceptional and later pedagogy is primarily conventional/non-operational.

No corpus-level hypothesis is promoted from one work.

## Promotion blockers

Before any of this staging material can become a governed accepted batch:

1. accepted `main` must expose the governing architecture/schema/predicate state;
2. Librarian must assign an accepted Work identity for this episode;
3. Librarian must bind an accepted Source identity/variant and provenance family;
4. source hashing or another reproducible source-identity mechanism must be available;
5. staging evidence/assertions must be converted into governed record shapes against those accepted IDs;
6. deterministic validation must pass;
7. coverage may advance only after the governed batch manifest is generated.

## Exact next SFA frontier

If accepted infrastructure remains blocked, the next proposal-only staging candidate is the currently official-listed season-one episode 2, `Beta Test`, **only if** a complete full-text representation can be retrieved and read end-to-end.

If accepted Work/Source registry state lands first, stop relying on this external sequence, refresh the accepted SFA inventory from `main`, and select the frontier from that registry instead.

No merge, coverage promotion, global reconciliation, credential/permission change, or other protected effect was performed by this packet.
