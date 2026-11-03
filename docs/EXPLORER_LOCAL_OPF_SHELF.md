# Explorer: opt-in, browser-local OPF shelf (draft only)

This is an **isolated personal metadata shelf**. It does not enlarge the
public literature directory, create canonical Work identities, admit research,
alter Lore's publicly sourced search, store data in browser storage, or
publish private ebook content. The feature is only a draft proposal until
reviewed and explicitly deployed by project authority.

## Why this shelf is separate

The public discovery directory currently has **nine** publisher/distributor
literary metadata leads: four novel candidates and five in-universe memoirs.
It does not import the owner's separate Star Trek ZIP inventory. The owner
inventory has **347 OPF title-metadata observations**, from an archive whose
paired ebook ZIP contains **347 LIT and 220 TXT members**. These member counts
are *not* a census of distinct literary Works, licensed editions or book reads.
The private-derived index has **0 verified edition bindings, 0 full-text reads,
0 accepted Works and 0 coverage effect**.

## Manual use

1. Obtain the exact reviewed `search-index.json` from the local checkout at
   `proposals/librarian/private-opf-metadata-20261103/search-index.json`.
2. In the Explorer, navigate to **My OPF metadata shelf**, select that JSON
   with the file chooser, then search title, creator or checksum-valid ISBN
   candidates. By default 40 observations render; **Show more** extends the
   list without changing public catalog counts.
3. Select **Clear local shelf** to remove the current list and search terms
   from the page. Reloading the page also starts empty.

No file picker opens automatically. The feature never requests the JSON by
`fetch`, never uploads it, creates no URLs from private metadata, and uses
`textContent` for every supplied string. It has no telemetry, cookies,
`localStorage`, `sessionStorage`, IndexedDB or download/export operation.
The browser reads and hashes at most 512 KiB in memory and accepts only the
**exact reviewed** 347-record derivative SHA-256
`ef3c6de334a00a55588ebd1fe839d1f5229033b1f60f78be09c8ec19d8ef8c72`;
other files fail closed without retaining a prior displayed inventory.
This hash validates against the committed derivative, **not** the underlying
private ZIP's authenticity, source authority, work identities or review.

The **normalized title/creator search-index metadata is already publicly
committed** in accepted GitHub `main`; `owner-private` denotes the source ZIP
containers, original paths and unpublished book content, **not** secrecy of all
bibliographic metadata. The existing repository proposal derivative excludes
archive paths, private GUIDs, full text and images. This shelf's file-selection
and rendering are local; it does not newly transmit its selected bytes. Do not
repurpose the shelf as a public auto-loaded JSON endpoint or merge its 347
entries into the nine separately publisher-reviewed public leads.

## Verification

`node --test tests/test_explorer*.mjs` checks opt-in loading, exact-byte pin,
size/rejection cases, safe text-only rendering, local filtering, Clear, and
isolation from public directory/admission counts. The broader Python and
Pages artifact suites must also pass before any proposal is reviewed.
