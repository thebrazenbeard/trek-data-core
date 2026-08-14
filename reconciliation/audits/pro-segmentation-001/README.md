# Prodigy premiere segmentation audit 001

Role: AUDITOR  
Proposal audited: PR #11 `research/pro/pro-s01-opening-five-staging` @ `04c39135a1db7506277a8516bbb0beaf32d40c8d`  
Disposition: **CONFIRMED SEGMENTATION AMBIGUITY / STAGING HANDLING SUPPORTED**

This audit targets the Work/Source cardinality problem around `Lost & Found` Parts 1 and 2. It does not resolve canonical Prodigy Work identities.

## Independent source comparison

The staging packet reports three incompatible-but-useful source shapes:

1. Springfield! Springfield exposes one `s01e01` page titled `Lost & Found (Part 1, Part 2)` with a combined transcript body.
2. Forever Dreaming exposes one transcript topic labeled `01x01 & 01x02- Lost & Found (part 1, part 2)`.
3. TVsubtitles exposes separate subtitle files for `1x01 - Lost and Found Part 1` and `1x02 - Lost and Found Part 2`.

Independent reopening confirmed all three shapes.

The combined Springfield transcript includes opening Tars Lamora material and continues through the Protostar escape to activation of Hologram Janeway, demonstrating that the page is not merely a mislabeled Part 1 snippet.

## Findings

### AUD-PRO-SEG-001 — one evidence-bearing source artifact may span multiple Work identities

**Verdict:** CONFIRMED  
**Severity:** CRITICAL for Librarian Work/Source binding

The premiere proves that source cardinality and Work cardinality are independent.

A model that assumes `one physical/source artifact == one Work` would likely collapse Parts 1 and 2 into one canonical Work merely because Springfield and Forever Dreaming package them together.

A model that assumes `one Work == one physical source` would instead invent two physical Source identities from one combined transcript artifact.

Both shortcuts are wrong.

**Required invariant:** Source records must be able to represent an artifact/container covering one or more Work identities, with Work-specific spans/locators or contained-source segmentation when evidence supports it.

---

### AUD-PRO-SEG-002 — source packaging agreement is not independent evidence of Work ontology

**Verdict:** CONFIRMED  
**Severity:** HIGH

Springfield and Forever Dreaming both package Parts 1 and 2 together. That agreement does not prove the franchise's canonical Work registry should collapse them. The separate subtitle inventory supplies direct counterevidence that the same audiovisual material can circulate as two installment-level representations.

Provider packaging is evidence about source representation, not automatic canonical Work identity.

---

### AUD-PRO-SEG-003 — the staging worker preserves the ambiguity correctly

**Verdict:** CONFIRMED  
**Severity:** POSITIVE CONTROL

PR #11 explicitly:
- calls its five units `titled transcript works/pages`, not canonical Works;
- refuses canonical `source_id` / `work_id` issuance;
- records the combined-versus-split premiere disagreement;
- routes final Work/Source identity to the Librarian;
- advances no accepted coverage.

That is correct staging behavior.

---

### AUD-PRO-SEG-004 — sampled representation/identity discipline is materially supported

**Verdict:** CONFIRMED  
**Severity:** POSITIVE CONTROL

The combined transcript independently supports two high-risk staging distinctions:

- Zero explicitly distinguishes the Medusan non-corporeal life-form from the constructed containment suit.
- the Janeway-form entity explicitly identifies herself as `Hologram Janeway` and a training advisor.

The staging packet therefore acts correctly by keeping Zero/person-versus-suit embodiment and Hologram Janeway/antecedent-Janeway identity unresolved rather than merging by appearance/name.

This is a bounded semantic sample, not full re-audit of all 46 evidence notes.

## Recommended Librarian representation

At minimum preserve separately:

- source artifact/container identity;
- provider packaging/title/index metadata;
- canonical Work identity or identities;
- source-to-work coverage relation;
- Work-specific source spans/locators when one artifact spans multiple Works;
- derived/member source relationships when split files are downstream representations of combined or original material;
- edition/release segmentation status and unresolved alternatives.

Do not choose a canonical Work count from filenames alone.

## Admission disposition

Preserve PR #11 as staging. No re-reading is required merely because its source is combined. Promotion remains blocked on Librarian Work/Source binding and accepted architecture/schema.

## Exact next frontier

Re-audit this case only when a Librarian Prodigy inventory/source-binding proposal chooses a canonical representation. Verify that the chosen model can preserve both combined and split source variants without duplicate Work inflation or source splitting.
