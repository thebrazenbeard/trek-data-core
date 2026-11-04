# Commons file-level licensed photo leads — no automatic Explorer artwork

**LIBRARIAN / PROPOSED / HELD** · 2026-11-04 · authoritative GitHub `main@3028765359001b90bc3e6b5c1835ee283b326e91`. This tranche adds *three independently located, file-page license-explicit metadata leads*, not any copyright-cleared Star Trek episode still, film poster, cover, asset download, release or research admission.

## Exact source and asserted photograph licensing

| Candidate and truthful proposed use | First-party-by-photographer source / Commons file page | Commons file-page copyright assertion | Held issue |
| --- | --- | --- | --- |
| **Leonard Nimoy at 2011 Star Trek convention** — real-world actor portrait, **not** an image of Spock as a canonical character | [Commons file](https://commons.wikimedia.org/wiki/File:Leonard_Nimoy,_2011,_ST_Con-2.jpg), [original photographer Flickr](https://www.flickr.com/photos/29456903@N04/6060504064) | Photo by **Beth Madison**, CC BY 2.0. Commons' Flickr license reviewer confirmed original CC BY status 2011-10-30. | Identifiable person's publicity/privacy rights and no implied endorsement. |
| **2013 Star Trek fan convention** — fandom/convention context, **not** a television production still | [Commons file](https://commons.wikimedia.org/wiki/File:Star_Trek_Convention_(9501108956).jpg), [original photographer Flickr](https://www.flickr.com/photos/tomasdelcoro/9501108956/) | Photo by **Tomás Del Coro**, CC BY-SA 2.0. Commons FlickreviewR confirmed Flickr licensing 2017-04-24. | Identifiable people and any visible copyrighted cosplay/branding must be assessed independently. |
| **TOS Set Tour building exterior, Ticonderoga, 2022** — real-world location, **not** a still from *The Original Series* | [Commons file](https://commons.wikimedia.org/wiki/File:Star_Trek_Original_Series_Set_Tour_Ticonderoga_NY.jpg) | Photo by **Kenneth C. Zirkel**, uploader-declared own work under CC BY-SA 4.0. | Exterior signage/trademarks and any visible sculpture/props may implicate underlying third-party rights. |

The `records.json` packet also stores exact Commons `oldid` permalinks and license URLs, origin links and creator names, dated observations, distinct media-context labels, attribution duties, and the third-party-rights questions. These facts were read from the **individual Commons file description pages** on 2026-11-04, not inferred from search snippets, file names, a general Commons policy, or the *Star Trek* label. A Commons metadata permalink is a **DOC observation**, not a byte-level file fingerprint, rights chain-of-title review or independent Explorer release verification. No image pixels were retrieved or visually audited in this tranche.

The two Flickr imports have Commons' historical platform license-review evidence. That is useful additional metadata corroboration, but it does **not** constitute an independent legal review of the image's complete rights chain or depicted people's consent. The Ticonderoga photo has the uploader's own-work assertion, not an external ownership certification. If those Commons pages change, the exact page revision records remain an audit trail; a future user-facing release must re-check current file identity and licensing.

## Why these are held despite explicit Creative Commons photo licenses

Creative Commons licenses can authorize reuse of the photographer's **licensed photograph** with conditions. They do not necessarily cover every depicted IP, trademark, sculpture, copyrighted prop, identifiable person's publicity/privacy rights, or implied affiliation. Sources: [Wikimedia Commons' external reuse guide](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia), [Creative Commons FAQ](https://creativecommons.org/faq/), and individual [BY 2.0](https://creativecommons.org/licenses/by/2.0/), [BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/), [BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) texts.

Attribution plan for each potential **later** use: credit original creator; link original Commons page and relevant CC license; say whether cropped/modified; avoid suggesting the author or Star Trek rightsholders endorse Explorer. For BY-SA photographs, any published adapted copy must respect the same/compatible ShareAlike obligation. Image captions must accurately say **actor portrait**, **fan convention**, or **exterior of a set-tour venue**, not canonical episode stills, film publicity posters, or Starfleet-issued insignia.

> **Hostile review:** The uploaded photo's CC tag is not a release from Paramount, CBS or another owner of distinct artwork seen in the photograph. Treat an image-specific rights issue as **UNRESOLVED**, not automatically solved by the photographer's own-work declaration.

> **Hostile review:** A photographed actor is not the fictional character; a fan convention is not canon footage; a set-tour exterior is not the TOS Enterprise set itself. These may only serve truthful real-world/category illustrations, with no source coverage numerator or exact canonical Work binding.

> **Hostile review:** CC BY-SA licensing affects downstream *modified photograph* distribution, not necessarily the entire Explorer codebase; any actual image derivative and attribution UI need a separate licensing review. License name, linked source and two reviewing models do not equate to independent permission verification.

## Release frontier

No candidate becomes a public image merely by adding this packet. All three are `HELD_FILE_PAGE_LICENSE_VISIBLE_RELEASE_NOT_REVIEWED`, and they have **zero** independent rights/visual reviewers, zero image byte hashes, zero accepted exact Explorer binding, and `public_display_eligible=false` / `public_rehost_eligible=false`.

For a future use, independently inspect the actual image for embedded IP and real-person rights, re-verify photographer attribution and source file metadata, select a truthful noncanonical UI category, document complete CC attribution and any adaptation's license, establish image bytes digest, and obtain separate human/independent rights review. Then submit to the existing `tools/validate_artwork_release.py` exact code-owned pin/receipt gate in a separately authorized PR. This packet cannot trigger Pages or download any image.

## Deterministic validation

```bash
python3 tools/validate_commons_visual_leads.py --check
python3 -m unittest tests.test_commons_visual_leads -v
python3 tools/validate_artwork_release.py --check --verify-git
```

The 21 hostile tests reject swapped photographer/source/license/Commons revision, attribution or ShareAlike omissions, fabricated reviewers, false actor-to-character or fan-to-episode bindings, binary/inline payload insertion, and rights/publication self-promotion. All results remain local-only, `PROPOSED`, with research/Source/Work/UI effects `NONE`.
