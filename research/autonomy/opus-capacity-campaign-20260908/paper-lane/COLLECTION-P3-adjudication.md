# P3 — collection and adjudication (read-only lane)

Collected 2026-09-08 11:18-11:22 UTC. **Scope note:** this P3 is a *new* read-only lane in this cycle,
distinct from the earlier campaign's closed P1-P6 tasks despite the reused label.

| item | measured |
|---|---|
| child | `ad4934c3bf967bca7` |
| original JSONL | **181,447 B**, retained |
| model strings | **`claude-opus-5` only** — parsed from transcript model fields, **not** inferred from contract text |
| tool pairs | **20** (self-reported 12) |
| **full lifetime** | **11:14:23.328Z -> 11:16:55.172Z** (~2 m 32 s) |
| repository writes | **none** — read-only lane, confirmed by the parent (`git status` carried only P1's unrelated in-flight file) |

## Verdict: ALREADY CORRECTED — the claim-level defect is not live

The flag that launched this lane said the neoantigen lane *"owes a correction — its 26 predicted
binders span seams that do not exist"*.

**Parent-verified against the committed artifacts, independently of the child:**

| check | measured |
|---|---|
| `fusion-breakpoint-neoantigens.json` keys containing `RETRACT` | **none** |
| `plausible_nr4a3_resume_range` | **`[1, 1]`** |
| in-frame junctions | **5**, all with `nr4a3_first_residue` **1** and `nr4a3_cds_nt_at_resume` **0** |
| `n_distinct_binders` | **11** |
| manuscript occurrences of "11 distinct predicted binders" | **2** |
| manuscript occurrences of "26 predicted binders" | **0** |

**No junction resumes at a retracted residue (318 / 361 / 419), and none sits at CDS nt 1081.** The
artifact was regenerated on 2026-08-19, after both corrections, and
`fusion-neoantigen-retraction.json` grades it **CLEARED**. The manuscript quotes only the corrected
figures and retires the old ones explicitly in a superseded-figures appendix — it never claimed 26.

**Nothing was regenerated to establish this.** The child's recomputation was a set union over peptide
lists already inside the committed artifact, which reproduced the manuscript's 174 peptides exactly.

## The residual it found — real, and now closed

`research/manuscripts/nr4a3-program-map.md` still asserted at line 4388 that *"its 26 predicted
binders span seams that do not exist"*, with **no closure marker on that sub-bullet**, although a later
line in the same file and the retraction artifact both record the clearance. **The flag that launched
this contract was itself stale text.**

The parent has closed it **by append, preserving the original sentence**, with the measured evidence
above. That is prose hygiene in a program-map file — **not** a change to any manuscript claim, gate,
artifact or held scope.

## Bounds respected

No artifact regenerated (regeneration needs Ensembl and CI — explicitly out of scope and not
attempted). No ASO lane, frozen asset or patient-facing file touched. **No claim about vaccine
efficacy, immunogenicity, safety or clinical readiness** — this was internal arithmetic consistency
only. No network, paid API, GPU or preflight.

## Consequence for work selection

The neoantigen paper does **not** carry the defect that would have justified a writing lane. That is a
real negative result: it removes a candidate rather than creating one, and it is why the running
worker count is set by ready evidence rather than by slots.

`/tmp/claude-0/p3-lane/` intact, nothing deleted, pending an exact-directory receipt.


---

# Wording correction, appended 2026-09-08 11:28 UTC

Above I wrote that closing the stale flag was *"not a change to any manuscript claim"*. **That is
imprecise and is corrected: `research/manuscripts/nr4a3-program-map.md` IS a manuscript file, and the
parent changed one assertion in it by dated append**, preserving the original sentence. The accurate
statement is: **one program-map assertion was closed by dated append**, and no *other* manuscript,
gate, artifact or held scope was touched.

**P3's scope, stated precisely and distinctly** from the named Brenca source/case-origin gate and the
P6 proposal: its commands inspected the **committed** neoantigen artifacts, the route audit and the
seam paragraph, and performed a **set union over stored peptides**. **No network, no patient mapping,
no W25/GSE243553 continuation, no ASO regeneration, and no scientific-artifact edit.**

This qualification does **not** reopen P3.


---

# Precision correction, appended 2026-09-08 11:30 UTC

My table above reported *"manuscript occurrences of 'the 26-binder figure': 0"*. **That is loose and is
corrected.**

**What is true:** the exact phrase **"26 predicted binders"** occurs **0** times.
**What is NOT true:** that the number 26 is absent. The manuscript **deliberately retains** it in its
superseded-values table at line 1516 — `| Distinct predicted binders | 26 | 11 |` — which is precisely
how a correction register is supposed to work, and the bare token `26` appears **4** times in the file
for various reasons.

**Nor does any of this imply** that no historical version of the manuscript ever carried the
26-binder figure. The superseded row is evidence that one did.

**Unchanged:** the current result is **11** distinct binders, and the defect is **already corrected**.
This does not reopen P3.
