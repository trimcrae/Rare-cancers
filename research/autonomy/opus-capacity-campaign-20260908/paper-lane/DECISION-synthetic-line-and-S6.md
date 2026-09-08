# Paper-level decision on the synthetic instrument line, and the next step — recorded 2026-09-08 06:29:42 UTC (`date -u`)

## What the synthetic line actually contributes, and what it cannot

**The durable methods contribution is a negative about a quality metric, and S5 hardened it.** Across
**four structurally distinct censoring shapes**, `assess_quality`'s admissibility check passed **189 of 200**
reconstructions under the unchanged 0.05 floor while individual cells lost up to **51 of 53** censorings
(maxdev 0.0225) and **41 of 41** (maxdev 0.0142). The metric compares the reconstruction against the
*digitized* curve, so an error that moves the input moves both sides together. That is reusable, it is
measured on 200 reconstructions with raw bytes retained, and it does not depend on which of S4's two effects
generalises.

**S5 resolved the merit question that was open after S4, and the answer reduces the line's value.** S4's
density finding is **not** a property of the instrument: its exact-arm form fails in 3 of 4 shapes, its
read-arm form in 1 of 4, and `line_width_4` — a *degraded* render — largely abolished it. S4's extent finding
persists in direction 4 of 4 but its endpoint and magnitude are cohort properties. So the headline that looked
paper-shaped after S4 is, after S5, **a cohort-and-render artifact**, and the surviving contribution is the
metric-blindness result above.

## ⛔ DECISION: **NO-GO on further synthetic sweeps.** The child's named successor is NOT executed.

S5 proposed varying `render_km`'s figure `width` to separate digitized-point count from row count. It is
runnable, cheap and deterministic — **and runnability is not a reason to run it.** The decision against it:

1. It refines the **mechanism of an effect S5 has already shown does not generalise**. Explaining a
   cohort-and-render artifact more precisely does not make it a finding.
2. It cannot touch the **material merit limit**, which is transfer. Every result in this line is synthetic, and
   as the appended disposition on S5's report now records, **synthetic ease establishes no bound on real-figure
   error in either direction.** A methods paper about reconstructing *published* figures cannot rest on an
   instrument validated only against inputs it generated itself.
3. Continuing would be the "endless sequence of synthetic sweeps" the standing instruction forbids, and each
   further sweep would inherit the same transfer gap.

**Exact reopening input, so this is a blocker with a condition rather than an abandonment:** a **real published
survival figure whose patient-level ground truth is also published** — a paper printing both a Kaplan-Meier
curve and the per-patient data behind it (a per-subject table, a swimmer plot, or supplementary IPD). One such
pair converts every synthetic result above into a validated or refuted claim about real figures. Absent that,
the synthetic line stays a description of its own instrument, and **no reporting requirement, no journal
recommendation and no clinical claim follows from any of it.** Nothing here is a manuscript admission.

## Next step, selected and executed in the same cycle: **S6 — assemble the validation set**

The reopening input is itself a bounded, independently useful public-source question, so the next step is to
**go get it** rather than to park the line.

**Question.** Which published series — in extraskeletal myxoid chondrosarcoma first, then rare sarcoma more
broadly — print **both** a survival figure **and** the patient-level data behind it, such that a digitization
method can be validated against real ground truth rather than against synthetic inputs?

**Why it is distinct, and not a closed route.** This is **not** the closed IPD paper, **not** an
inverse-baseline application, **not** the long-term-recurrence gate, **not** an RT/IPD synthesis, and **not**
a pooled dataset — no reconstruction is performed and no patient-level data is pooled or produced. It is the
assembly of a **method-validation corpus**: figure–truth pairs. The campaign has already stumbled on two
fragments of exactly this shape (a per-subject table in one trial report; a swimmer plot in another), which is
evidence the class exists and has never been enumerated.

**Scientific purpose.** It is the one input that could make the whole digitization line say something about
real figures — and if the class turns out to be empty or unreachable at $0, that is itself the decisive,
publishable-grade negative about what this literature permits, and it closes the line honestly.

**Acceptance.** A list of candidate figure–truth pairs with identifier, access state, what the figure shows,
what form the ground truth takes, and whether both are reachable at $0 — or a documented finding that the
class is empty/unreachable within the searched scope, with the scope stated.

**Stop.** When the search scope is exhausted or ~40 tool calls / ~40 minutes, whichever first.

**Bounds and prohibitions.** Retrieval only through the already-admitted PubMed MCP route. **No reconstruction,
no digitization, no pooling, no patient-level dataset.** The `CLOSED-WORK.md` denied list (Pazopanib,
Sunitinib 2014, Wagner, CTARC, Trabectedin/RT), GSE4303/GSE28866, PMID 22592656 and any held continuation are
excluded; a non-open-access source is **UNKNOWN**, not absent. No clinical claim, no manuscript, no
publication. W25 / primary-article / Results / novelty, the NR4A/P6 successor exclusion, the S1/S3 stops, the
P1–P3 closures and the P4–P6 intake limits all stay exact.

**Ownership.** Campaign record owned by the one parent collector; no manuscript or shared-graph write. Durable
artifacts to `/tmp/claude-0/s6-retained/`, verified before any cleanup, parent copies and commits.

---

# ⛔ NARROWING APPENDED 2026-09-08 06:34 UTC — two claims above were too strong

**The decision text above is preserved unchanged.** The NO-GO on further synthetic sweeps and the correction
that synthetic ease establishes no real-figure error bound both stand. Two claims in the S6 section are
narrowed here.

## 1. A matched pair tests the method on THAT pair — it does not validate the line

The text above says one figure–truth pair *"converts every synthetic result above into a validated or refuted
claim about real figures."* ⛔ **That is too strong and is withdrawn.** A single matched pair supports a test of
the method **on that pair only** — one figure, one cohort, one endpoint, one journal's rendering. It cannot
validate or refute *every* synthetic finding, and it establishes no general claim about real figures. Whether
any result transfers beyond the pairs actually tested remains **UNKNOWN**, and the number of pairs needed for
any broader statement is itself unestablished.

## 2. A null result is a bounded source/reachability finding — not automatic paper merit

The text above calls an empty class *"the decisive, publishable-grade negative that closes the line honestly."*
⛔ **Also withdrawn.** Failing to find or reach such a pair is a **bounded statement about what was searched and
what was reachable**, nothing more. It is **not** automatically publishable-grade, **not** paper merit, and
**not** a manuscript admission. Symmetrically: **source availability is not paper admission either** — finding
pairs admits no paper. Any paper-level consequence would need its own separate decision on its own evidence.

## 3. Matched cohort/endpoint versus merely adjacent — the distinction is load-bearing

A **matched** pair means the per-patient data covers **the same cohort and the same endpoint** as the survival
figure, so it can serve as ground truth for that figure. An **adjacent** fragment — a per-subject table for a
different subset, a swimmer plot of a different endpoint or a differently-defined population, patient-level
data for some arms of a mixed cohort — **does not supply ground truth for that figure** and must not be graded
as though it did. The two fragments this campaign already stumbled on are **candidates to be tested against this
definition, not established pairs**, and either may fail it. Verdicts must state matched-versus-adjacent
explicitly and default to the weaker reading when the source does not settle it.

## 4. Closures are unaffected by any of this

Every named closed and held source stays excluded — **including if it turns out to be one of the fragments that
motivated this candidate**. These narrowings must not be used to broaden scope, revisit a closed route, or
justify a retry. The `CLOSED-WORK.md` denied list, GSE4303/GSE28866, PMID 22592656, W25 / GSE243553 /
primary-article / Results / novelty, the NR4A Perspective, the S1/S3 stops, the P1–P3 closures and the P4–P6
limits all stand exactly as recorded.

The running S6 contract otherwise continues unchanged: source identification only, no digitization,
reconstruction, pooling or clinical dataset; retention and access-state recording as already permitted; no new
manuscript or publication action; no controller, session, deadline or billing change.
