# Independent documentary media candidates — HELD (2026-11-04)

Baseline accepted `main`: `3028765359001b90bc3e6b5c1835ee283b326e91`. Three distinct first-party photographer/uploaders; read-only Wikimedia Commons **fixed file-page revisions** were inspected. The page revision is not a binary hash. All checksums, where present, are **Commons-reported SHA-1**, not separately recomputed. No image pixels or hosted URLs were added to an Explorer artwork registry; no coverage or Source→Work admission.

| ID | Work scope | Creator and source | Rights class | Release state |
|---|---|---|---|---|
| `media-nemesis-2001-grcote-set-photo-held` | *Nemesis* film set, documentary | Grcote, [Commons oldid 931234115](https://commons.wikimedia.org/w/index.php?title=File:Glenn_Cote_Brent_Spiner.jpg&oldid=931234115) | GFDL 1.2-or-later, no invariant/cover text; VRT notice ticket 2010061710008511 (private ticket not read) | HELD — license not in public allowlist; third-party/personality rights unresolved |
| `media-discovery-2017-lucca-caranti-panel-held` | *Discovery* 2017 real-world panel, documentary | Niccolò Caranti, [Commons oldid 1155058425](https://commons.wikimedia.org/w/index.php?title=File:Teatro_del_Giglio_-_Lucca_2017.jpg&oldid=1155058425) | CC BY-SA 4.0 International | HELD — uploader rights claim, personality warning, adaptation/attribution and contextual review unresolved |
| `media-picard-2023-fourthords-costume-held` | *Picard* S3 costume on public display, documentary | Fourthords, [Commons oldid 1145272591](https://commons.wikimedia.org/w/index.php?title=File:Star_Trek-_Picard_season-three_Starfleet_flag_officer's_casual_uniform_(1_March_2023,_aboard_Star_Trek-_The_Cruise_VI,_1_of_3).tif&oldid=1145272591) | CC BY-SA 4.0 International (photo only) | HELD — separately protected costume/insignia design, large original TIFF, no derivative rights QA |

## Falsifiers and open gates

1. Commons metadata and its own SDC claims are **one evidence family**, not two independent witnesses. A VRT ticket notice says a copyright email exists; the actual ticket has not been read. The film-set photo is **not** treated as CC or unrestricted explicit permission.
2. These are useful **work-context images**, not authentic film frames, episode stills, or film posters. The *Discovery* source has no episode assignment; *Picard* has season-3 context only. No `episode_id`, cast-scene assertion or episode-level coverage is inferred.
3. Source photographer copyright licensing does not itself extinguish personality, trademark, underlying costume/art, or false-endorsement considerations. Public release requires an independent file-by-file rights/context determination, exact rendition bytes/hash and caption/attribution QA.
4. Proposed license and license-version fields must remain literal. No GFDL→CC substitution, and Commons's legal notice must not be silently equated to publication authorization for the LCARS website.
5. Existing `LICENSE_BASES` has no GFDL class. The 116.36 MB TIFF was not fetched or transformed; no standalone SHA-256 claim is made.

Validation: `python3 -m unittest tests.test_three_media_sources_held -v`; tests intentionally mutate each rule to ensure the packet fails closed. Results are recorded in the accompanying commit, not a published Explorer projection.
