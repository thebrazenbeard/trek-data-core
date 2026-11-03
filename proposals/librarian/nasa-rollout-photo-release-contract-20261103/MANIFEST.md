# NASA Space Shuttle Enterprise real-world photograph — release criteria (HELD)

**Purpose:** A bounded, machine-checked future release contract for one actual NASA Star Trek cultural-history photograph. This is not another source photograph packet (#418/#428) or a UI implementation (#426); it defines what an image-specific reviewer would need to approve before any publication.

Photo is [NASA's 1976 *Enterprise* rollout image](https://www.nasa.gov/image-article/star-trek-nasa-54-years-counting/), original exact source [JPEG](https://www.nasa.gov/wp-content/uploads/2023/03/ec76-5806-1.jpg): **165,312 bytes**, **1041 × 833**, SHA-256 **`e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8`** (independently retrieved and visually checked by Librarian and Lou-Pole Auditor in earlier wave). It is a documentary photo of the real NASA shuttle at a public 1976 event, not a narrative media frame. Official NASA [2015 article](https://www.nasa.gov/image-article/shuttle-enterprise/) and [NASA Commons photo catalog](https://www.flickr.com/photos/nasacommons/9467279838/) document cast/NASA group and image number `S91-27436`.

## Legal/source interpretation and falsifier

NASA's current [media usage policy](https://www.nasa.gov/nasa-brand-center/images-and-media/) broadly allows credited factual informational website use of NASA-created media without implying NASA endorsement, but warns about third-party copyright and identifiable-person commercial/promotional rights. NASA Commons displays **“No known copyright restrictions”** for this photo. That is a catalog-level status, **not** a separate affirmative copyright license, a proven chain of title from the individual photographer, or a personality-rights release. NASA and its Flickr Commons collection are the same institution; these are corroborating primary descriptions but not independent rights-holders.

The same NASA policy now contains specific **super-intelligence/AI-use guidance** about attribution and NASA insignia in SI-generated works or training. A factual reproduction of this original photograph must remain clearly distinguished from any AI-generated illustration or model-training use; this contract authorizes neither NASA logo training nor claims that NASA verified or endorsed generated output.

> **Material remaining challenge:** A source photo and useful NASA media-policy exception do not, alone, prove that this *specific image* was NASA-authored without third-party rights, nor that a proposed Explorer presentation would remain nonpromotional and clearly unrelated to fictional Work artwork. A reviewer must examine the image-specific credit and context, not infer permission from `S91-27436` or the filename alone.

The exact source photo appears **potentially usable** for a narrowly factual nonprofit research panel, but this packet cannot certify it publicly display-eligible. `release_state=HOLD_NO_MEDIA_PUBLICATION`; no image, gallery row, thumbnail, prefetch/hotlink or site file is included or enabled.

## Required acceptance chain

1. Source crosswalk from [draft PR #428](https://github.com/thebrazenbeard/trek-data-core/pull/428) accepted on `main`, without laundering its source-only GO into a rights release.
2. Independent image-specific rights/attribution decision with an exact photograph and contemporaneous NASA policy basis, considering photographer, people and marks.
3. Independently reviewed nonpromotional, nonendorsing real-world history-panel design; [draft #426](https://github.com/thebrazenbeard/trek-data-core/pull/426) is not an accepted release.
4. Exact-byte/derivative hash-pinned **new image release manifest**, with approved, isolated asset storage and no remote hotlink assumption.
5. Browser/privacy/accessibility QA for 320/375/600/760/1440 widths, keyboard/focus, alt/caption, session-local opt-in and zero image network before opt-in.
6. Separate authorized publication/deployment decision. No model-written status value or reviewer opinion alone substitutes for accepted source evidence and owner authority.

The contract remains a source-only proposal regardless of CI outcome. Do not count this historical image as fiction work/episode/film artwork or source close reading. Other held candidates (#414, #424, #429) remain independent.

Validate: `python3 validate.py` and `python3 -m unittest -v test_validate.py` (both default and `-O`).
