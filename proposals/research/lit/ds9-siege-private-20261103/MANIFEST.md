# LIT — private *The Siege* TXT deep read (proposed, not admitted)

**Lane:** literary source-relative research only. **Batch:** `LIT-DS9-SIEGE-TXT-20261103`. **Base accepted main:** `885df8dc60122e55d9f37195eabd0b1a7c67b3c6` (2026-11-03, GitHub-confirmed PR #478 base at creation). No global Work/character reconciliation, deployment, public source-text redistribution, artwork, or accepted coverage effects.

## Source and independently checked provenance

- Input is the user's private in-memory TXT ZIP member already catalogued by the accepted Librarian under `proposals/librarian/private-ds9-txt50-20261103/observations.json`, `txt-local:0002`.
- The *uncompressed bytes*, accessed read-only on the authorized owner host, exactly rehash to SHA-256 `72c60433e98c6d8cc0ad0e2de7edc2713c2db8efaae55a27def51da6aaae5d5f` (423,375 bytes), agreeing with the accepted receipt. ZIP SHA-256 is `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`.
- Sequential private reading was actually performed for the complete observed artifact: preface and prologue followed by **22 consecutively numbered chapters**. The in-memory text contains **2,989 nonempty conversion-local lines** and approx. 72,873 regex word matches. All 23 sections have contiguous character and nonempty-line ranges plus SHA-256 receipts, without retaining or publishing their contents.
- The opening prose preface identifies an **original DS9 novel** (rather than an episode screenplay or episode novelization), and the remaining text is multi-focal third-person narrative, not a transcript. Its title/author/content fit [the official Simon & Schuster catalogue record for *The Siege* by Peter David, DS9 book #2, eBook ISBN 9780743412216](https://www.simonandschuster.com/books/The-Star-Trek-Deep-Space-Nine-The-Siege/Peter-David/Star-Trek-Deep-Space-Nine/9780743412216). **Candidate only:** no authenticated publisher title/copyright pages, publisher-format collation, or conversion history prove this exact TXT is the cited edition or complete as issued.
- This partition includes only hashes, locators, local occurrences, original short descriptions and interpretations, and audit/validator code. No private file path, transcript, source paragraphs, cover image, or text payload is distributed.

## Original source-local chapter structure

| Segment | First-hand neutral summary |
|---|---|
| Preface / prologue (0) | The preface situates the prose commission and its permitted transformations; the prologue conceals a murderer within the shape of luggage. |
| 1 | Domestic frustration over Molly's birthday and O'Brien's failed magic intersects with Dax's discovery of anomalous wormhole measurements. |
| 2 | A vessel emerges damaged from the compressed wormhole; recovered wreckage is interpreted as Borg, producing Sisko's safety dilemma. |
| 3 | Jake questions promised security and Odo privately treats wormhole visitors as possible clues to his lost origins. |
| 4 | A missionary family is diverted to safety; Glav narrates a seeming reversal of his earlier financial grievance with Quark, while another traveler conceals an alien form. |
| 5 | Bashir examines the sick child Rasa in informal conversation; Glav proposes purchasing the station; Lobb is killed after attempting conversion. |
| 6 | The first crime scene is marked with a numeral; Bashir names Rasa's illness and a possible treatment, initiating a care/refusal conflict. |
| 7 | Marko and Azira reject intervention on religious grounds while officials disagree about medical obligation and the Prime Directive. |
| 8 | The proposed station sale fails; Odo argues against mass lockdown and briefly suspects an apparently ordinary stranger. |
| 9 | The disguised killer gains the confidence of a Bajoran child; a Cardassian envoy threatens her mother and is murdered, challenging security's model of the suspect. |
| 10 | Dukat demands jurisdiction over the Cardassian death; the third numbered victim is found in the cargo area, destabilizing station confidence. |
| 11 | Civilians demand escape; Sisko worries evacuation will distribute an unidentifiable murderer; medical staff devise identity checks. |
| 12 | False alarms and invasive private-likeness holosuites distract station personnel as the killer's disguises change. |
| 13 | The killer attacks Quark's bar, uses Jake as a hostage, and escapes despite an ingenious mirrored rescue. |
| 14 | Bashir compels Quark to erase misappropriated images and to build another holosuite program; security engineers duct traps. |
| 15 | Bashir subjects Azira to a simulated future loss of Rasa; a fourth crime scene and stolen challenge phrase further expose institutional vulnerability. |
| 16 | Odo clarifies his literal reply in the opening card trick; the Edemian and Cardassian warships threaten the station. |
| 17 | Azira voluntarily brings Rasa for treatment while condemning Bashir's conduct; Odo struggles with the possibility of a kindred killer. |
| 18 | A seeming Quark confronts Glav about using serial killings to mask a personal assassination; Meta attacks the apparent Quark, setting up a false death. |
| 19 | The victim is revealed as Odo in disguise; Meta kills Glav and fights Odo through station corridors to a stolen runabout. |
| 20 | The opposed warships endanger DS9; Meta is dispersed in the unstable wormhole yet narratively remains conscious; Odo is recovered exhausted. |
| 21 | Rasa survives, but Marko publicly repudiates Azira and the family; she questions both the cost of rescue and Bashir's means. |
| 22 | Jake and Sisko renegotiate security and trust; the O'Brien family receives a pony that is Odo in disguise, paying off the opening device. |

## Semantic and evidence framing

`records.json` contains **25 local occurrences, 30 conversion-local source observations, seven interpretations and seven unresolved categories**. Each observation names its source narrative frame; no local entity is a global identity resolution. Locators are `chapter` including prefatory segment 0, plus zero-based **nonempty line within that segment**; headings count as line 0 for numbered chapters. They are not publisher page references.

The key corrective pair is `ev-20` and `ev-21`: the source initially renders Quark as killed but then reveals Odo's masquerade. Any representation that admitted the former as confirmed death would be falsified by the latter. The distinction is not a generic counterweight: it is an explicit source chronology correction of an **apparent event**, modeled as such.

**Local-occurrence correction:** In `ev-19` and `ev-20`, the `participants` list now names Odo rather than Quark because the indexed next-chapter reveal explicitly identifies who was actually present in the disguise. The observations retain the *apparent* Quark identity as narrative focalization, and the record does not claim a global identity merge. Validator regression tests reject reintroducing Quark as an actual participant in those two decoy events. This repairs a source-local graph traversal hazard without changing the observed text, locator, evidence kind or coverage.

Likewise, Meta's purported common origin with Odo is an adversarial offer, not objective proof; the scene of Meta's dispersed yet continuing consciousness is this novel's imaginative narration, **not** a cross-work biological or metaphysical finding. A holographic forecast of Rasa's death is neither his actual death nor independent evidence that this future would occur. Azira's request for treatment is distinct from endorsing the means used to influence her and from declaring her choice free of regret.

All seven source-local interpretations therefore leave `counterweight: []` and `counterevidence_status: UNKNOWN`. This expresses lack of indexed, logically pertinent disconfirmers, **not** a claim that a complete cross-work hostile search found none. Arbitrary links to unrelated evidence were expressly forbidden after the predecessor's hostile audit.

> **Hostile challenge — identity:** The shapechanging killer makes contested claims about origins and uses disguises successfully against onlookers. Do not infer species equivalence, global entity identity, or a reliable victim ID from one uncorrected visual description.

> **Hostile challenge — agency and coercion:** Azira's later informed request does not retroactively validate the pressure exerted by Bashir's fearful simulation. Religious penalties and the Prime Directive rationale are positions represented by characters and require separate institutional corroboration.

> **Hostile challenge — text and edition:** An apparently complete converted novel can still omit, modify, or conflate pages. The official catalogue establishes a matching **Work candidate**, not authenticated source/edition custody.

> **Hostile challenge — distributed awareness:** Meta's first-person-like experience after bodily rupture is narrated within a licensed-fiction candidate; it neither proves persistence of awareness across sources nor licenses confident extrapolation to nonbiological consciousness.

## Validation and precise limits

Run `python proposals/research/lit/ds9-siege-private-20261103/validate.py` and `python -m unittest discover -s proposals/research/lit/ds9-siege-private-20261103 -p 'test_*.py'`. The immutable chapter-index SHA recorded in the validator was computed after private segment verification; all 23 segment digests and 30 locator bounds can be checked in public CI **without** the private source.

**Research artifact scope:** Complete, SHA-matched private TXT **reading**, structural partition and locally grounded analysis for one candidate. **Accepted Work scope:** no `SOURCE_BOUND`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, identity admission or production projection yet. Separate Librarian edition audit, independent hostile content/semantics review and authorized integration are still needed.
