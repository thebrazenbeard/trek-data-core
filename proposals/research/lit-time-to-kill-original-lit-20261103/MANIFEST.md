# Original LIT blob custody candidate — *A Time to Kill*

**Role:** LIT. **Status:** DRAFT source-relative observation only. **Accepted research effects:** NONE.

This narrowly extends [the private converted-OPF structural proposal](https://github.com/thebrazenbeard/trek-data-core/pull/240) without treating that proposal as accepted. The original owner-held `ST ebooks.zip` archive was opened on Lappy through its authorized WorkBridge Commander WSL route; the source ZIP and one candidate member were hashed in place without extracting or publishing copyrighted bytes. The original ZIP archive SHA-256 agrees with the prior private corpus custody receipt.

The exact converted OPF archive-member basename (minus `.opf`, Unicode casefolded) matched **one** `.lit` archive-member basename (minus `.lit`, same normalization). The shared normalized-stem fingerprint is `79e039dde7b3da841760b53fded27ae0d35149bca4eb04b95aed2a72da01ddc6`. That `.lit` member is **330,907 bytes**, SHA-256 `3c1057258180b14175160e9af5b564c4ec2c7cb7e0fbfb0c6aea97d4afb0c276`, and begins with the eight-byte Microsoft Reader LIT magic `ITOLITLS`. The linked converted OPF member and HTML spine SHA-256 values match the private structural receipt in #240.

**Critical boundary:** This is only a *filename-correlated binary custody candidate*. A valid LIT magic and matching filename neither authenticate that the two files hold the same book text nor prove that the conversion preserved any chapter. The `.lit` content was **not decoded or read**. Publisher-edition completeness, textual equivalence, semantic close reading, rights, and accepted Source↔Work identity remain **UNVERIFIED**. No research coverage advances.

The public `RECEIPT.json` contains only hashes, byte counts, LIT magic, a ZIP CRC32 observation, and explicit non-admission fields. It contains no archive member paths, book prose, binary assets, images, or user filesystem paths. Hashes are custody fingerprints, not independent authenticity or rights certification. A public validator can detect changes to this recorded observation; it cannot recreate the private archive or prove the uninspected `.lit` payload.

## Required next gate

Under Patrick's authorized private host custody, qualify a lawful reader for this original Microsoft Reader LIT representation; verify decrypted/decoded source identity and full textual boundaries against the converted OPF/HTML and publisher edition, record exact private hashes/locators, then conduct an actual neutral close read. Until then, this is **DISCOVERED + candidate source custody**, not `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, or `CLOSE_READ`.
