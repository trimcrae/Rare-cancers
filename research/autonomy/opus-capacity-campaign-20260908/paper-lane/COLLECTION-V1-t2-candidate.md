# V1 — collection: the T2 candidate, built and verified, NOT applied

⛔ **Nothing applied.** The candidate lives in its lane. **Shared integration remains the scientific
coordinator's final decision**, and the committed manuscript, tier, registry, figure and reference list
are unchanged.

| item | measured |
|---|---|
| child | `a36744029567f093b` |
| model strings | **`claude-opus-5` only** |
| tool pairs | **22** (self-reported 15) |
| shared writes | **none** — `git status` clean at start and end |

## Parent verification — I re-derived each central claim

| claim | check |
|---|---|
| baseline == the committed manuscript | sha256 `1933916c…` on **both** |
| **reference section byte-identical** | `6d5f11139792bca06a4905e4a87dd66c` on **both** — matches V1's own figure |
| citation-token counts unchanged | identical across all 20 references, **49 tokens -> 49** |
| **the §5 rule clause preserved verbatim** | present **once in baseline, once in candidate** |
| the §2.6 rule clause preserved verbatim | present **once in each** |
| R2's overgeneralised rationale removed | `"neither prospective nor substantial"` -> **0 occurrences** |
| mismatch disclosed **in the body** | all six disclosure phrases present; **not inside an HTML comment** |
| figure untouched | PNG still `f711ea7f…`; **0** modified figure or registry paths |

⚠ **A caution about my own first check:** two greps initially returned 0 and 1. That was **line
wrapping in my search, not absence** — re-running on whitespace-normalised text confirmed every
clause. I record the false alarm rather than only the corrected result.

## What the candidate does — the rule is untouched; only its description changed

The firewall's admission criterion is **byte-for-byte the committed text**: *"only a candidate reaching
direct EMC clinical evidence at T3 may migrate into the project's cited clinical registry, and then
only after clinician review."* What is new is framing plus disclosure, in **running prose across §2.6,
§4 and §5**, and in the **figure alt text and caption**:

- it is stated as the **intended criterion**, with *"we do not claim that it is currently enforced in
  full"*;
- the **imatinib registry entry is disclosed as falling below that criterion** under the T2 grade; and
- **registry conformance is marked unresolved**, with *"no clinician review, authorised exception or
  prospective-only scope is asserted for that entry, the registry is not altered by this paper."*

⭐ **Nothing was invented to make the mismatch go away** — no approval, no exception, no policy, no
governance resolution. The mismatch is disclosed, not resolved.

**The rationale is correctly narrowed:** *"The assembled record supplies a case-level signal and does
not establish the prospective or substantial EMC clinical evidence that this paper's definitions
require for T3."* Nothing implies [7] was newly read.

**§2.2** keeps the four-tier scale and adds occupancy: *"no candidate reaches T3 … T3 is therefore
defined but unoccupied, and is retained to mark what a prospective or substantial EMC clinical result
would look like."*

## ⭐ The figure: no change needed, and none made — the better outcome

`14 existing drugs, tiers T0–T3` states the **scale range**, and four tiers are retained, so it stays
true. `T3 plus clinician review only` states the **admission rule**, which is deliberately unchanged —
the corrected claim is about **enforcement**, a property of the registry, not of the diagram. **The
generator was not copied, not modified and not run; no figure was regenerated; the committed PNG was
not even re-inspected**, U2's terminal result being reused as instructed.

## Validation scope, stated by the child and accepted

**Verified by execution:** baseline byte-identity, all 8 edit anchors matching exactly once,
reference-section hash identity, citation counts, a sentence-set diff showing **7 sentences removed —
all seven the intended targets — and 19 added**, with every §5/§6 limitation and hedge surviving.
**Asserted, not verified:** editorial adequacy, the T2 premise itself, anything about [7] beyond the
manuscript's characterisation, anything about the figure beyond U2. **Not run:** preflight, any gate,
any citation checker, any figure generator.

## Remaining dependencies

1. **Registry conformance unresolved** — a clinical-governance decision for the responsible clinician
   or owner. 2. `emc-clinical-registry.json` still lists imatinib; unchanged here. 3. Scale arity
settled at four; R2's Option B fragments unused. 4. Integration and any gate run are the
coordinator's. 5. A revision-label discrepancy is recorded, not resolved — the file-content baseline is
unambiguous. 6. The 25-vs-22 reference-count question is untouched and out of scope. 7. **No figure
dependency remains** under four tiers; only a reopened three-tier decision would require both labels
and the alt text to change together.

**R2's original proposal is retained separately** from V1's candidate, as two distinct artifacts.
