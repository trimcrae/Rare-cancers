# Red-team of the NR4A3-degrader paper — deficiencies + fixes applied

> **Role:** adversarial self-review of [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md) (2026-06-26).
> Scope per the directive: critique the *manuscript's claims, framing and internal consistency* — **not**
> the experiments still in flight. "Experiment not finished" is never a finding here; "the writeup claims
> more than the finished analyses establish" is. Each finding below has a fix that was applied to the
> paper and/or its supporting memos in the same change. Findings are ordered by severity.

## F1 (severity: high) — Pre-registration integrity: Gate 1 was never scored, and as written it is *not* met
**Deficiency.** The pre-registration ([`../modalities/nr4a3-druggability-prereg.md`](../modalities/nr4a3-druggability-prereg.md))
defines five gates. The reconciliation memo scores Gates 0, 0b, 2, 3; the paper says "Gate 2 PASSES and
Gate 3 PASSES"; the next-steps TL;DR says "Gates 0–3 pass." **Gate 1 is scored nowhere.** And Gate 1's
literal pass condition is: *"the converged F(Rg) shows an accessible minimum or shoulder at an opened Rg
distinct from the closed basin (**not just biased excursions**)."* The actual F(Rg) is **monotonic — a
single closed basin with a rising wall and no opened minimum/shoulder** (stated in `nr4a3_md_release.py`
docstring and the reconciliation's "monotonic wall, no open basin"). So the opened conformations are
reached *only under the metadynamics bias*, which is precisely the "just biased excursions" case Gate 1
was written to exclude. This is the exact failure mode the pre-registration exists to catch ("would *any*
fpocket number end up supporting druggability?").

**Why it matters.** "Cryptic pocket **opens** to a druggable **state**" implies a distinct, populated
opened conformation. The energetics do not (yet) show one. The defensible reading is *basin-internal
breathing* to transiently druggable sub-states (which is what de Vera 2019 actually report for Nurr1 — a
dynamic pocket that breathes, not a two-state cryptic switch). Whether those sub-states are a genuinely
populated minimum vs. bias-induced strain is the open question the (in-progress) unbiased release run is
designed to answer — so it must not be pre-judged as "passed."

**Fix applied.** (a) Added an explicit, honest **Gate 1** entry to the reconciliation's gate scoring —
"met only in the weaker basin-breathing sense; no opened free-energy minimum/shoulder resolved;
metastability pending the unbiased release run." (b) Reframed the paper's abstract/§2.2 from "opens a
cryptic druggable pocket / the opened state" to "the orthosteric pocket **breathes** to transiently
druggable conformations," with the no-separate-basin caveat stated. (c) Corrected the next-steps TL;DR and
the prereg deviation log to stop claiming an unqualified "Gates 0–3 pass."

## F2 (medium) — The headline 0.931 is an extreme-value statistic and is compared to the static holo panel as if on one scale
**Deficiency.** The abstract and §2.2 said the opened-frame druggability **0.931** is "above every
experimentally drug-bound NR pocket in our panel (0.53–0.68)." Two real problems: (a) 0.931 is the
**maximum over 600 frames** — an extreme-value statistic that overstates the typical opened conformation;
the faithful summary is the *fraction* of opened frames clearing D\*=0.53 (the pre-registered ≥5 % bar,
met) with 0.931 as the peak. (b) It is computed on **biased-MD** conformations while the panel numbers are
**static crystal ligand sites**, so the magnitudes are not on the same footing and "beats the drug-bound
band" is not like-for-like.

**Correction to an earlier over-statement of this finding.** An earlier version of this memo also called
the opened-frame score "uncalibrated" and recommended a bespoke fpocket **negative control** (run the same
Rg-metadynamics on a genuinely undruggable pocket). On reflection that was overstated and is **retracted**:
fpocket's druggability score is a *standard, validated* metric (a logistic model of hydrophobic enclosure
and polarity — not raw cavity volume), and §2.1 already anchors it on an NR panel that includes the
occluded 1OVL crystal as a de-facto negative. So the metric itself is not in question, and — because
druggability rewards hydrophobic *enclosure* — a pocket that merely splayed open / became solvent-exposed
would score *lower*, not higher, which means the rise is informative, not an artifact of "opening." The one
thing fpocket cannot settle (is the breathing-open geometry physically populated, or bias-induced strain?)
is answered by the **unbiased release run**, which dominates any fpocket control for that purpose. Net: the
negative control is redundant; the surviving, legitimate fixes are the max-vs-distribution reporting and
the biased-vs-static comparison caveat.

**Fix applied.** (a) Dropped the "above every drug-bound pocket" claim; relabelled 0.931 a biased-MD
**peak** and lead instead with the fraction-of-frames-≥-D\* distribution. (b) Stated the rise reflects a
hydrophobic, *enclosed* cavity (a splayed pocket would score lower). (c) Replaced the next-steps
"negative-control calibration" item with a "report-as-distribution" item and an explicit note that no
bespoke fpocket negative control is needed. Paper §2.2/§5, abstract, and the reconciliation †-note updated
to match.

## F3 (high) — Metric conflation in the calibration table (the very error the paper accuses others of)
**Deficiency.** The reconciliation's calibration table reports 0.931 under a column headed "max
druggability," the same column where the crystals are scored as **max-anywhere-on-LBD** (1OVL 0.864,
4JGV 0.960). The paper's whole §2.1 argument is that "max-anywhere" is non-discriminating and one must use
the **orthosteric/Pocket-5-specific** score. The metad-opened 0.931 *is* in fact the orthosteric Pocket-5
score (per `nr4a3_mdpocket.py`: per-frame fpocket is computed on the Pocket-5 lining residues, the same
metric as the static 0.495 and D\*) — but the table's label invites a reader to compare it to the
crystals' non-orthosteric max, the apples-to-oranges error §1/§2.1 exists to prevent.

**Fix applied.** Relabelled the table so the metad-opened row is explicitly the **orthosteric Pocket-5
score, max over frames** (commensurate with the static 0.495 and D\*), distinct from the "max-anywhere"
column used for the crystal rows; added a one-line metric note. Stated the same explicitly in §2.2.

## F4 (medium-high) — Gate 3's 38→0.76 kcal/mol rescue reads a second point off the *same* under-converged biased profile
**Deficiency.** Gate 3 (pre-registered ≤5 kcal/mol) naively reads ~38 kcal/mol (fail). The rescue: a
druggable frame (fpocket 0.80) sits at Rg≈0.717 nm costing only ~0.76 kcal/mol on F(Rg). Both numbers come
from the *same* biased sum_hills F(Rg). The team correctly calls the 38 unreliable because the profile is
monotonic and read at the under-converged frontier — but then treats a different point on that same curve
as reliable. The asserted "0.717 is in the well-sampled region" is plausible (more sampling near the
start) but is an assertion, and the paper currently states Gate 3 is "resolved... [the release run] not
required," which over-claims relative to the team's own logic (the release run is the *independent*
metastability test).

**Fix applied.** Reworded Gate 3 in the paper and reconciliation from "resolved / not required" to
"**provisionally** met by the basin-breathing reading of an as-yet-incompletely-converged F(Rg); the
independent metastability confirmation (unbiased release run) is in progress." Kept the substantive point
(the 38 was a frontier artifact, a druggable conformation is cheap) but stopped asserting finality.

## F5 (medium) — "converged" is overstated
**Deficiency.** The paper header/abstract call the 30 ns run "complete (converged)" / "converged," while
the energetics frontier is "under-converged," F(Rg) has no opened basin, and "a converged longer metad to
put a precise number on the full free-energy profile" is an open to-do. "Production-length and basin
well-sampled" is true; "converged" (unqualified) is not.

**Fix applied.** Replaced unqualified "converged" with "**production-length (30 ns); the closed basin is
well-sampled, the opening frontier is not fully converged**" in the header, abstract and §2.2.

## F6 (medium) — Selectivity asymmetry NR4A1 vs NR4A2 is hidden by the "divergent" flag
**Deficiency.** The 7 handles are flagged "divergent" = differs from NR4A1 **or** NR4A2. But selectivity
must hold against **each** paralogue separately, and the subsets differ (from `nr4a-selectivity.json`,
Pocket 5):
- vs **NR4A1**: all 7 handles differ (L406→H, T407→L, T410→G, R412→A, I484→Y, I531→V, L534→F).
- vs **NR4A2**: only **6** differ — **I531 is identical (Ile in both)**; (L406→H, T407→V, T410→N, R412→T,
  I484→Y, L534→F).
Intersecting with the 5 *engageable* (pocket-facing) handles (L406, T410, I484, I531, L534): the engageable
**divergent** set is **5 vs NR4A1 but only 4 vs NR4A2** (I531 drops, being conserved with NR4A2). So
NR4A3-vs-NR4A2 selectivity rests on a *narrower* handle set than NR4A3-vs-NR4A1 — and NR4A2/Nurr1 is the
paralogue whose loss carries the neuro (dopaminergic) liability one most wants to avoid. The paper presents
"5 engageable handles" without this per-paralogue breakdown.

**Fix applied.** Added the per-paralogue handle breakdown to §2.3 and flagged in §5 that selectivity vs
NR4A2 is intrinsically the harder, narrower case (4 engageable divergent handles, I531 conserved).

## F7 (medium) — AciCC "substantially more common than EMC / enlarges the market" is unsourced
**Deficiency.** The market/motivation argument leans repeatedly on AciCC being "substantially more common
than EMC, materially enlarging the addressable population," with no incidence citation. Both are rare;
under the repo's medical-integrity rule every clinical/epidemiological claim must be cited. The relative-
incidence claim is probably true but is currently asserted.

**Fix applied.** Softened to "AciCC is a more common salivary-gland carcinoma than EMC (incidence locator
to attach before submission)" and flagged the missing citation in the medical-integrity note / §5, rather
than stating a quantitative-sounding market claim unsourced.

## F8 (low, already partly disclosed) — Binding-selectivity matrix is necessary-not-sufficient for degradation selectivity
**Deficiency.** The §2.4 selectivity matrix scores **warhead-binding** selectivity, but a degrader's
selectivity is set by the *ternary complex* and ubiquitinatable-lysine geometry; a non-selective binder can
degrade selectively and vice versa. The paper notes "degradation selectivity ≠ warhead-binding
selectivity," but the matrix is still framed as the selectivity deliverable.

**Fix applied.** Sharpened §2.4/§5 to state the binding matrix is a *necessary, not sufficient* filter and
that degradation-direction selectivity is set downstream by the per-paralogue ternary model — already the
planned tier, now explicitly labelled as the gating step for any selectivity claim.

## Not changed (judged acceptable as written)
- The **Gate 0 metric swap** (max → orthosteric/ligand-site, D\*=0.53) is post-hoc but openly disclosed,
  the new bar is a *real* drug-bound score (not laxer), and the conclusion holds under 0.50 or 0.53.
  Honest as written.
- The **AF2-not-AF3** justification is sound and well-argued.
- The **de Vera 2019 / Nur77-MD precedent** framing is appropriate (and, post-F1, now *more* accurate —
  de Vera's "breathing" pocket is the right analogy for basin-internal dynamics, not a two-state switch).
</content>
</invoke>
