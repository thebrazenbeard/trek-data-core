# Prior-chat migration triage, not recovered research

This source-neutral queue was derived from Patrick's saved ChatGPT page,
`Deploy subagents build repo.zip`. It captures **reported previous-work leads**
at the accepted `main` head pinned in `MANIFEST.json`. No claims in this file
are adopted as evidence that Trek audiovisual or literary sources were read.

## Reproduce the chat-page locator convention

Keep the private archive outside the public checkout. Verify its SHA-256, then
render its single HTML conversation member with Pandoc **3.1.3**:

```bash
sha256sum '/private/path/Deploy subagents build repo.zip'
unzip -p '/private/path/Deploy subagents build repo.zip' \
  'Deploy subagents build repo.htm' |
  pandoc -f html -t plain --wrap=none 2>/dev/null |
  nl -ba
```

The manifest gives both SHA-256 digests and inclusive rendered-text line
locators for each lead. These locators are a replay aid, not a cryptographic
signature or durable source identifier. The archive's HTML also contains
navigation/sidebar snippets that repeat earlier messages and cannot be counted
as corroboration. No raw HTML, embedded scripts, transcript passage, or ebook
content was transferred to this directory.

## Scope and handoff

- `EXPORT-TNG-B001` and the historical research inventory already have partial
  candidate counterparts on `main`. The open historical migration Draft PR
  #193 is a separate proposal: compare exact Git objects before duplicating its
  work or declaring acceptance.
- The DS9 title/body mismatch, TNG lineation failures and TAS archive/reference
  defects are **falsifiers to investigate**, not evidence to silently correct
  titles, source bindings or local identity.
- The derivative transcript pilots in the chat reportedly read complete
  *third-party textual representations*. Even if their private receipts can be
  replayed, that would not authenticate full audiovisual viewing.
- `LIT` lacks a recovered ebook source representation in this archive. A
  publisher listing or historical conversation claim cannot supply that text.

Each queue entry states the unresolved verification gate. It is not a Work,
Source, evidence, assertion, accepted reconciliation, or coverage ledger
record. **All admitted-research, Source↔Work, coverage, denominator and
reconciliation effects are `NONE`.**

Validation of this proposed queue alone:

```bash
python3 proposals/migration/chat-export-triage-20261103/verify_manifest.py
```
