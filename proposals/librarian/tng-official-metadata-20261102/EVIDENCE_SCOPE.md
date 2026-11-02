# Official-page metadata observations and limits

All URLs below are controlled by StarTrek.com. The research pass viewed public
page metadata on 2026-11-02; no original article body, scripts, imagery or
video bytes are included in this repository. These locators are not
independently signed remote-source snapshots.

| Proposed Mission Briefing | External candidate QID | Official locator | Narrow page observation |
| --- | --- | --- | --- |
| The Neutral Zone | `Q1058477` | [Official video page](https://www.startrek.com/videos/star-trek-the-next-generation-the-neutral-zone) | TNG title and S1E26 label |
| New Ground | `Q16744120` | [Official video page](https://www.startrek.com/videos/watch-star-trek-the-next-generation-new-ground) | TNG title and S5E10 label |
| Hide and Q | `Q1102231` | [Official preview](https://www.startrek.com/videos/episode-preview-hide-and-q) | Preview title only; **no verified series or episode ordinal on that page** |
| Skin of Evil | `Q1392472` | [Editorial retrospective](https://www.startrek.com/news/a-look-back-at-skin-of-evil) | TNG episode name; no verified ordinal for this pilot |
| Brothers | `Q14045941` | [Official watch guide](https://www.startrek.com/news/your-ultimate-star-trek-picard-watch-guide) | TNG episode reference in larger guide; no dedicated episode page or ordinal |

No publisher page provides a Wikidata QID. The external candidate association
therefore combines two data families: a Wikidata result and a separate
publisher page title/reference. This is useful for a **proposed** identity
crosswalk, but it is not a verified equivalence. In particular, preview and
editorial page references are not witnesses to the underlying episode body.

Source properties in `bundle.json` preserve only the labels actually supported
by the specific page. Episode season/ordinal values appear for *The Neutral
Zone* and *New Ground* only; no ordinal has been inferred from Wikidata for the
other three. All five sources share a single publisher independence group.

This bundle must **not** be used to infer narrative facts, historical episode
counts, coverage denominators, or an accepted `SOURCE_BOUND` state. The current
Librarian policy permits proposed metadata-only mappings but rejects an
accepted metadata-only binding. Rights, source fidelity, and identity require
additional human review.
