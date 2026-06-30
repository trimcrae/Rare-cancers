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

## Third pass (2026-06-30) — the decoy control invalidates the MM-GBSA selectivity tier (DECISIVE)

### F15 (severity: HIGH) — Single-snapshot MM-GBSA "NR4A3-selective" verdict is NON-SPECIFIC (no enrichment over a non-NR4A decoy null)
**Test.** Built a decoy/specificity control (red-team Tier-1 #2): 38 diverse **non-NR4A marketed drugs**
(`decoy_library.py`) pushed through the *identical* dock→single-snapshot-MM-GBSA funnel as the de-novo
candidates (same NR4A3 release receptor + NR4A1/NR4A2 metad frames), then compared the rate of
"NR4A3-selective" calls.
**Result (run 28414348202 / report 28416243043).** The decoy null is **`confirmed_selective` 15/38 = 39 %**
(census: confirmed_selective 15 · rescued 3 · weakened 2 · reversed 2 · confirmed_nonselective 16), and
**~58 %** of decoys have a *positive* NR4A3 MM-GBSA margin. The "selective" decoys include **caffeine,
ibuprofen, lidocaine, phenytoin, diazepam, atenolol** — molecules with no plausible NR4A3 selectivity. The
developability-gated **de-novo set is `confirmed_selective` 2/11 = 18 %** — i.e. **below** the decoy baseline,
**not enriched**.
**Why it matters (load-bearing).** The paper's de-novo headline ("**MM-GBSA-confirmed NR4A3-selective**
candidates", §2.5/abstract) rests on this verdict. The control shows the verdict has **no specificity** — the
single-snapshot, single-pose MM-GBSA + the asymmetric receptor (NR4A3 scored in its druggable release frame
vs paralogues) systematically favours NR4A3, so ~40–58 % of *any* drug-like matter scores "NR4A3-selective."
This **retro-explains** why the original artifact `denovo_15` came back "confirmed_selective" (the metric
calls everything selective) and means **the MM-GBSA tier cannot support a selectivity claim as run.**
**Fix applied.** (a) §2.5 + abstract + §5: retract/​downgrade "MM-GBSA-confirmed NR4A3-selective" to "the
single-snapshot MM-GBSA selectivity verdict **fails a decoy control** (39 % of non-NR4A drugs score
selective; de-novo not enriched), so selectivity is **not established** by this tier — a properly-controlled
**multi-snapshot/ensemble MM-GBSA or selectivity FEP** is required." (b) Recorded the decoy control as a
**standing gate**: any future selectivity tier must beat the decoy null. (c) next-steps updated: Tier 3 #6
(multi-snapshot MM-GBSA with the decoy control re-run) is now the *necessary* fix, not optional polish.
**Decision for trimcrae (surfaced):** this guts the de-novo section's selectivity claim. Options: re-frame
§2.5 as "funnel + honest negative control (endpoint metric non-specific; FEP needed)", or hold the de-novo
arc out of the paper until a controlled energy method shows real enrichment. Awaiting steer; the honest
write-up is in place either way.

## Second pass (2026-06-29) — fresh adversarial review after the de-novo result landed

> The F1–F8 pass predates the matrix / MM-GBSA / de-novo results being folded into the paper. This second
> pass re-reviews the *current* draft (incl. §2.5 de-novo) and verifies claims against the committed data.
> Findings F9–F14; fixes applied in the same change. F9 also carries a decision escalated to trimcrae.

### F9 (severity: high) — The headline de-novo lead `denovo_15` is a generative-model artifact, presented as a "warhead candidate"
**Deficiency.** RDKit on the committed SMILES (`C=C(CC1=CC=C(NC(=O)O)C1)[C@H]1C=C2C(=NC1)OC[C@H](C)[C@@H]2C`,
C19H24N2O3, MW 328) shows `denovo_15` carries multiple **instability/reactivity liabilities**: a **carbamic
acid** (`NC(=O)O` — its polar "handle", which is hydrolytically unstable and decomposes to the amine + CO₂),
a **1,3-cyclopentadiene** (a reactive diene), an **imine**, an **exocyclic alkene**, and **no aromatic ring
at all**. Its **SAscore 5.08 is above the campaign's own ≤4.5 synthesizability cut**. The paper called it
"the first *designed* NR4A3-selective warhead candidate" with QED 0.774 cited as drug-likeness — but QED does
not screen stability/reactivity, and a med-chem reviewer flags these groups immediately. This is the textbook
DiffSBDD failure mode (optimise to *fit and score* a pocket, not to be stable or makeable).

**Why it matters.** "Warhead candidate" overstates what `denovo_15` is. The defensible, durable result is the
**funnel and the selectivity *direction* it produces** (de-novo matter survives MM-GBSA without reversing,
where repurposed matter reversed) — not this specific molecule.

**Fix applied.** Recast `denovo_15` throughout (abstract, §2.5, §5 caveat 6, §6 Gate 4, figures Fig 5d,
next-steps) as a **selective chemotype/pose hypothesis to be re-designed into a stable, synthesizable
analogue**, with the specific liabilities + the SA-vs-cut tension named.

**Triage of the other two `confirmed_selective` hits (report-denovo run 28405141248 + RDKit, 2026-06-29) —
neither rescues the headline.** `denovo_94` (mm +5.02, 4 handles) carries a **peroxide (1,2-dioxane)** + N,S-/
O,S-acetals — equally non-viable. `denovo_57` (`NC[C@@H]1CCN(Cc2ccccc2)C1`) is the **only chemically clean,
synthesizable** hit (SA 2.09, aromatic, basic amine) but is the **weakest** selectivity (mm +1.07), engages
only **2** handles, and is in the docking "none" cell. So the three confirmed-selective hits are
*strong-but-artifactual* (15/94) or *clean-but-weak* (57); **none is both viable and strongly selective.** The
defensible claim collapses to the **method** (the funnel produces de-novo matter whose selectivity survives an
endpoint energy model, unlike the repurposed library), not a developable molecule. Recorded in §2.5 + next-steps.
**Escalated to trimcrae** (decision below): re-frame §2.5 around the method (recommended), and whether to add a
stability/reactivity filter + re-generate before publishing the de-novo arc.

### F10 (medium-high) — The de-novo selectivity tier is NOT state-matched, but was labelled "state-matched"
**Deficiency.** §2.4's whole rigor claim is state-matching (all three paralogues docked in their *metad-opened*
frames, killing the opened-vs-static confound). §2.5 reused the phrase "state-matched NR4A3-release / NR4A1 /
NR4A2 pockets" — but per the data the de-novo funnel docks NR4A3 in its **unbiased-release** frame (fpocket
0.667) against **biased-metad** NR4A1 frame 524 (0.981) / NR4A2 frame 125 (0.938). Those states are *not*
matched; the label was inaccurate.

**Why it matters / direction.** The mismatch biases **against** NR4A3-selectivity (paralogue pockets scored
in their more-druggable opened state dock ligands more favourably), so a positive NR4A3 call is *conservative*
rather than flattered — but the paper must not claim the §2.4 state-matching rigor for the §2.5 tier.

**Fix applied.** Dropped "state-matched" from §2.5's funnel sentence; added an explicit receptor-state caveat
(the asymmetry + its conservative direction + the cheap fully-state-matched re-dock follow-up) to §2.5 and §5
(caveat 7) and the next-steps dock-tier entry.

### F11 (medium) — Gate 4 was never scored, though the de-novo campaign is its test (the F1 failure mode, repeated)
**Deficiency.** Exactly parallel to F1 (Gate 1 unscored): the prereg defines Gate 4 ("a selective, drug-like
ligand can engage the opened pocket"); §6 gestured at it ("the first to clear this last condition") but never
*scored* it, and the deviation log had no Gate 4 entry.

**Fix applied.** Added an explicit Gate 4 scoring paragraph to §6 and a deviation-log entry: **cautiously met
in silico**, with the two honest qualifications (energy tiers are screening-grade, FEP unrun; "drug-like" holds
on QED but not on stability — F9), i.e. cleared by a chemotype/pose hypothesis pending a stable analogue + FEP.

### F12 (medium) — "metastable (3/3) AND druggable ~24 %" conflates a triplicate Rg result with a single-replica druggability result
**Deficiency.** The abstract/§2.2 present "metastable (3/3 replicas) and druggable in ~24 % of frames" as one
joint finding. The **3/3** is an Rg-persistence result across the triplicate; the **~24 %** druggability
fraction is measured on the **single** `release_rep0` trajectory only. Also "metastable" rests on a **5 ns**
window, which excludes fast collapse but not tens–hundreds-of-ns relaxation.

**Fix applied.** Added a scope note to §2.2: the 24 % is rep0 (the other two confirm Rg persistence, not
druggability independently), and 5 ns "metastable" = "does not promptly collapse", not a verified long-lived
sub-state.

### F13 (medium) — MM-GBSA "direction is robust" is asserted without any replicate/error estimate
**Deficiency.** The paper leans on "trust the verdict/direction, not the magnitude" for both the §2.4 and §2.5
MM-GBSA censuses (incl. the de-novo "reversed 0"). But single-snapshot, single-pose MM-GBSA has **no replicate
or ensemble average**, so the *direction* of each verdict is itself an unreplicated point estimate whose sign
can move with pose/snapshot — "direction is the robust part" is asserted, not shown.

**Fix applied.** §5 caveat 7 now states the verdicts (incl. "reversed 0") are single-snapshot unreplicated
point estimates, not confidence-bounded; multi-snapshot averaging is the documented follow-up (already in
next-steps).

### F14 (low) — Internal inconsistency: `denovo_15`'s matrix cell (paper "NR4A2+NR4A3" vs next-steps "the only NR4A3-only cell")
**Deficiency.** The paper §2.5 says `denovo_15`'s strict cell is NR4A2+NR4A3 (NR4A3 favoured, NR4A2 weakly
co-engaged at the −7 cutoff); the next-steps handoff said "the only NR4A3-only cell." The next-steps census in
the *same* entry lists **no NR4A3-only cell** at all (20 = NR4A2+NR4A3 4 · pan 4 · none 5 · NR4A2-only 3 ·
NR4A1+NR4A2 2 · NR4A1+NR4A3 1 · NR4A1-only 1), so the paper is right and the handoff line was stale/wrong.

**Fix applied.** Corrected the next-steps dock-tier line to "NR4A3-favoured-by-margin (cell NR4A2+NR4A3)" with
a note that there is no NR4A3-only cell, reconciling to the paper.

## Not changed (judged acceptable as written)
- The **Gate 0 metric swap** (max → orthosteric/ligand-site, D\*=0.53) is post-hoc but openly disclosed,
  the new bar is a *real* drug-bound score (not laxer), and the conclusion holds under 0.50 or 0.53.
  Honest as written.
- The **AF2-not-AF3** justification is sound and well-argued.
- The **de Vera 2019 / Nur77-MD precedent** framing is appropriate (and, post-F1, now *more* accurate —
  de Vera's "breathing" pocket is the right analogy for basin-internal dynamics, not a two-state switch).

## Update for the next red-team (2026-06-30) — state at this checkpoint
Two things changed since the F15 decoy finding; a fresh adversarial pass should hold the paper to the
weaker reading on each.
- **Multi-snapshot de-noising tier is now run (§2.6).** It resolves the F15/caveat-7 follow-up the paper had
  listed as pending. It is *discriminating* (negative control `denovo_924` stays non-selective; the
  single-snapshot best `denovo_393` collapses +18.34 → −2.95 ± 3.65) and isolates **`denovo_401`
  (+12.83 ± 2.98, margin − SD = +9.85)** as the one survivor → the single FEP-justified lead. **Open angles
  to press:** (a) the **decoy null was not recomputed at multi-snapshot**, so "survives de-noising" ≠ "above
  a multi-snapshot null" — the paper now says this (§2.6, caveat 7); check it is never quietly upgraded;
  (b) it is **single-trajectory GB-implicit MD, not FEP**; (c) n=1 survivor out of a handful tested — the
  funnel is not shown to *reliably* produce de-noising survivors, only that one exists; (d) `denovo_111`
  (the single-snapshot decoy-null foothold) has **not** been multi-snapshot-tested, so the paper carries two
  differently-derived "leads" — watch for conflation.
- **Selectivity-architecture analysis added (§2.7 + `nr4a3-degrader-selectivity-architecture.md`).** New
  computed claim: the orthosteric pocket is the *most* paralogue-divergent LBD zone (70 % vs 43 %). **Press
  points:** (a) the "surface/PPI-proxy" row uses pocket-lining residues across all cavities, **not** the true
  E3 interface — flagged in the doc, but the binder-vs-ternary conclusion partly rests on it, so not settled
  until the real interface conservation is computed; (b) "source paralogue selectivity from the ternary"
  rests on the **un-run** ternary model — an argued strategy, not a demonstrated result; (c) the
  "fusion-vs-WT is unobtainable from the degrader" claim is load-bearing — verify it reads as a structural
  impossibility (shared LBD + LBD-distal fusion partner), not an empirical not-yet.
