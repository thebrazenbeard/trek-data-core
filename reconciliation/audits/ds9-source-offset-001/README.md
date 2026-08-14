# DS9 transcript source-offset audit 001

Role: AUDITOR  
Proposal audited: PR #2 `research/ds9/s1-opening-five-staging` @ `114d96b41865eff37a309fea747e8a6404c3a512`  
Disposition: **CONFIRMED SOURCE-BINDING ANOMALY / STAGING HANDLING SUPPORTED**

This audit targets the proposal's reported Springfield! Springfield season-one metadata/body mismatch. It does not convert the staging packet into accepted coverage or invent canonical Source/Work IDs.

## Deterministic / independent source readback

The worker reported that beginning with the feature-length premiere, the Springfield script-page metadata is shifted relative to the actual transcript body.

Independent page reopening confirmed the claimed mapping across the five-work staging range:

| Springfield page parameter | Page heading | Transcript-body identity |
| --- | --- | --- |
| `s01e02` | `Past Prologue` | `Emissary` |
| `s01e03` | `A Man Alone` | `Past Prologue` |
| `s01e04` | `Babel` | `A Man Alone` |
| `s01e05` | `Captive Pursuit` | `Babel` |
| `s01e06` | `Q-Less` | `Captive Pursuit` |

Body identity was established from episode-specific characters/events and opening content, not from page heading or URL parameter.

## Findings

### AUD-DS9-SRC-001 — provider locator metadata and content identity diverge systematically

**Verdict:** CONFIRMED  
**Severity:** CRITICAL for initial Source↔Work binding

In this range, three fields that a naïve importer might collapse are distinct:

1. URL/index parameter (`s01e0N`);
2. provider page title/heading;
3. actual transcript-body Work identity.

The first two agree with each other and disagree with the body. Therefore agreement between URL metadata and page heading is not independent corroboration of Work identity.

A Librarian binding process that maps Source→Work from URL/heading alone would mis-bind all five sampled pages.

**Required correction/invariant:** Source records must preserve provider locator metadata separately from audited content-identity binding. Work binding must be supported by content-specific evidence/fingerprint or an independently verified provider crosswalk, not by title/episode-number fields alone.

---

### AUD-DS9-SRC-002 — staging worker correctly preserved the anomaly instead of silently normalizing it

**Verdict:** CONFIRMED  
**Severity:** POSITIVE CONTROL

PR #2 explicitly:
- leaves canonical Source/Work IDs unminted;
- says the metadata/body mismatch requires Librarian resolution;
- identifies each body by content while retaining the original provider URL;
- marks the suspected feature-length-premiere numbering cause as an inference rather than fact;
- advances no accepted coverage ledger.

That is appropriate staging behavior under the current blocker.

---

### AUD-DS9-SRC-003 — source lineage and locator identity require two-level representation

**Verdict:** CONFIRMED  
**Severity:** HIGH

A useful future Source representation needs both:

- **provider locator identity:** provider, URL/index key, retrieved version/date, displayed heading;
- **bound content identity:** Work ID, content fingerprint/hash/locators, binding method, binding evidence, and anomaly status.

If provider metadata is overwritten with the corrected Work title, the historical source anomaly disappears. If the wrong provider metadata is promoted as Work identity, the corpus becomes mis-bound. Both must survive.

---

### AUD-DS9-SRC-004 — five pages do not prove the causal explanation for the offset

**Verdict:** CONFIRMED  
**Severity:** MEDIUM

The observed five-page shift is consistent with a numbering offset associated with treatment of the feature-length premiere. That mechanism remains a hypothesis unless provider/index lineage or a broader systematic test proves it.

The staging packet correctly keeps this causal explanation inferential.

## Blind-spot consequence

This defect is dangerous precisely because two metadata fields agree. A generic duplicate/crosswalk routine could treat URL parameter + page heading as two confirming signals when they are one provider-controlled metadata family. The transcript body is the disconfirming channel.

The same audit pattern should be applied anywhere a provider exposes:
- episode number + title + body;
- chapter filename + OPF title + text body;
- archive member name + embedded metadata + actual work content.

Correlated metadata is not independent evidence.

## Admission disposition

Preserve PR #2 as staging. No re-reading of these five transcripts is required merely because the provider metadata is defective; the worker's body-identity routing survived independent audit.

Promotion remains blocked on:
1. accepted architecture/schema;
2. Librarian Work identities;
3. canonical Source records that preserve the erroneous provider metadata and separately record the audited body binding;
4. reproducible source hashes/fingerprints;
5. governed validation.

## Exact next frontier

For this DS9 anomaly, no additional Auditor pass is needed until the Librarian proposes actual Source↔Work bindings or a provider crosswalk. At that point, verify that the five pages bind to body identity rather than provider heading/episode parameter and that the anomaly remains queryable rather than silently rewritten.
