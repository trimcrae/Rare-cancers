# Supplementary Information: In-silico ligand design for a cryptic, paralogue-selective NR4A3 pocket

**Tristan D. McRae** — *Independent researcher. Correspondence: trimcrae@gmail.com*

*This Supplementary Information collects the pre-registered falsification scheme and its
deviation log (SI §1), the outcomes of the pre-registered gates (SI §2), the full
selectivity-architecture analysis (SI §3), and a distilled account of the adversarial
self-review (SI §4). All results are in-silico predictions; no molecule was synthesized and
there is no wet-lab validation. Every number below is reported at the evidentiary weight
justified by the analysis that produced it.*

---

## SI §1 — Pre-registration and deviation log

### §1.1 Purpose and integrity model

The decision thresholds below were fixed **before** the production metadynamics, the calibration
panel, and the downstream design results were in hand, so that the conclusion could not be
reverse-justified from whatever numbers happened to appear. The guard is against a specific
failure mode: *would any fpocket number end up supporting druggability?* The answer must be no —
each gate has a pre-set way to fail, and a negative result is reported as a negative, with the
route's weight shifting to the backup modalities (a designed protein binder, an AlphaFold-surface
approach, or the fusion-junction antisense route).

At the time the scheme was written, the only production input available was the static AlphaFold2
orthosteric score, **0.495** (Pocket 5, residues 406–534), and a short preliminary simulation
showing the collective variable (radius of gyration, Rg) opens from ~0.5 to ~1.05 nm. No updated
druggability number and no calibration-panel results existed yet.

### §1.2 The claim under test

*A transient, energetically accessible cryptic opening of the NR4A3 orthosteric pocket (Pocket 5)
reaches a druggable state, into which a drug-like, NR4A1/NR4A2-selective warhead can bind.*

This is a **chain of independent gates**. The claim is supported only if the gates pass; failing
gates are reported, not discarded.

### §1.3 The pre-registered gates (thresholds fixed before results)

**Gate 0 — Pipeline calibration** (must pass, else fpocket evidence is down-weighted).
Run the fpocket pipeline on a known nuclear-receptor panel.
- **PASS if** the known-druggable controls (PPARγ + rosiglitazone; ERα + 17β-estradiol) score
  their experimentally bound orthosteric ligand site clearly **≥ 0.5** (expected ~0.7–1.0),
  **and** the occluded Nurr1 apo crystal scores its maximum **< 0.5** — demonstrating the pipeline
  separates true-druggable from occluded NR pockets.
- **Defines** the working druggable threshold **D\*** = max(0.5, midpoint between the lowest
  druggable-control ligand-site score and the occluded-crystal score). All downstream
  "crosses druggable" tests use **D\***, not a naive 0.5.
- **FAIL** (controls don't separate): fpocket is uninformative on these models; no druggability
  claim rests on fpocket scores and the route relies on orthogonal evidence (pocket volume/SASA,
  docking, experimental NR4A ligand-site precedent).

**Gate 0b — Model-vs-crystal over-call check** (interpretation, not pass/fail). Compare the NR4A2
AF2-model maximum druggability to the occluded-crystal maximum. A large positive delta would
quantify AF2 over-call and would mean the NR4A3 static 0.495 should be read as an **upper bound** on
static druggability.

**Gate 1 — Cryptic opening occurs (metadynamics).**
- **PASS if** the converged free-energy profile F(Rg) shows an accessible **minimum or shoulder** at
  an opened Rg **distinct from the closed basin** (not just biased excursions). Convergence assessed
  by hill-deposition rate and profile stability.

**Gate 2 — The opened state is actually druggable.** Per-frame fpocket on the opened conformations.
- **PASS if** a non-negligible fraction of opened frames (pre-set: **≥ 5 % of frames**, and at least
  one well-formed cluster) reach druggability **≥ D\***, with the pocket still lining residues
  406–534 (not a splayed/unfolded artifact — checked via lining-residue identity and that the
  selectivity handles remain pocket-facing).
- **FAIL** if opening does not produce a druggable cavity → the small-molecule orthosteric route is
  not supported.

**Gate 3 — Opening is energetically accessible.** From the converged F(Rg).
- **PASS if** the free-energy cost from the closed basin to the druggable-open state is **≤ ~5
  kcal/mol** (transiently populated at physiological temperature).
- **FAIL** (cost ≫ 5 kcal/mol) → the druggable state exists but is not realistically populated;
  report as "cryptic but energetically costly."

**Gate 4 — A selective, drug-like ligand can engage it (downstream).** Dock/generate into the best
opened conformer.
- **PASS if** drug-like matter docks with a reasonable score **and** contacts a meaningful subset of
  the seven selectivity handles (L406, T407, T410, R412, I484, I531, L534) with predicted
  selectivity margin versus NR4A1/NR4A2.
- **FAIL** if no drug-like/selective binder → the small-molecule warhead route is not supported.

**Decision rule.** Route supported only if Gate 0 passes and Gates 1–3 pass; Gate 4 strengthens it
and is required before claiming a candidate. Any of Gates 1–3 failing → report the negative and shift
weight to the backup modalities; thresholds are **not** re-tuned post hoc to rescue the result.

### §1.4 Anti-confirmation safeguards

1. The thresholds (D\*, the 5 %-of-frames bar, the ~5 kcal/mol cost) were fixed before the
   production and calibration numbers were known.
2. D\* is set by an **external yardstick** — known-druggable NR controls — not by NR4A3's own number.
3. All gates are reported including negatives; the static 0.495 is treated as an upper bound, never
   as standalone evidence of druggability.
4. A change of collective variable or metadynamics parameters invalidates prior sampling (enforced by
   a manifest guard), so the coordinate cannot be silently swapped to manufacture an opening.

### §1.5 Deviation log (disclosed; preserves pre-registration integrity)

**Deviation 1 — Gate 0 metric corrected (disclosed).** As written, Gate 0 used the *maximum*
pocket druggability and required the occluded Nurr1 crystal's maximum to be < 0.5. The calibration
run showed that maximum is **0.864** — because *max-anywhere* is non-discriminating: every NR LBD,
the occluded crystal included, has a high-scoring **non-orthosteric** cavity. The test therefore
**fails as literally specified**. The discriminator was corrected to the **ligand-site /
orthosteric-specific** druggability (computed in the same run), and **D\* = 0.53** was set from the
validated drug-bound NR controls (PPARγ 0.599, ERα 0.586, Nurr1-holo 0.677, Nur77-holo 0.529). This
is disclosed rather than silently swapped; the corrected bar (0.53) is a *real* drug-bound score, not
a laxer one, and the downstream qualitative conclusion (static pocket sub-D\*, breathing-open pocket
above D\*) holds under both a naive 0.50 cutoff and the calibrated 0.53.

**Deviation 2 — Gate 1 outcome qualified (disclosed; met only in the weaker basin-breathing sense).**
Gate 1 required the converged F(Rg) to show an accessible minimum or shoulder at an opened Rg
distinct from the closed basin (not just biased excursions). The production F(Rg) is instead
**monotonic — a single closed basin with a rising wall and no opened minimum or shoulder** (and the
opening frontier is under-converged). The literal condition is therefore **not met**: the druggable
conformations arise by **basin-internal breathing** under the bias, not via a distinct opened
metastable state. This is reported as a **weaker, basin-breathing pass**, still consistent with the
experimentally demonstrated *breathing* Nurr1 pocket (de Vera 2019 — a dynamic pocket that breathes,
not a two-state switch). Per the decision rule this **weakens** the route's energetic-accessibility
leg until an unbiased simulation confirms a populated sub-state; it does not on its own abandon the
route (Gate 2 druggability and the low basin-breathing cost still stand at feasibility weight). This
correction also retired an earlier overstatement ("Gates 0–3 pass") that had never actually scored
Gate 1.

**Deviation 3 — Gate 4 scored explicitly, then disciplined by a decoy control, then narrowed to one
frame-dependent lead (disclosed).** Gate 4 (a selective, drug-like ligand can engage the opened
pocket) is its own downstream test and was scored only after the de-novo campaign. Its evolution is
recorded honestly:
- An initial single-snapshot "lead" was **retracted**: a decoy specificity control (38 non-NR4A
  marketed drugs through the identical dock → single-snapshot MM-GBSA funnel) showed the
  "NR4A3-selective" verdict is **non-specific** — 39 % of decoys scored "confirmed_selective" and the
  developability-gated de-novo set was **not enriched** over that null. The single-snapshot verdict
  cannot, on its own, support a selectivity claim; the decoy run was thereafter treated as a
  **calibrated null** that candidates must beat.
- A **multi-snapshot** endpoint-MM-GBSA tier (short GB Langevin MD; ΔG averaged over frames with
  error bars) then isolated **denovo_401** as the one candidate whose selectivity survives ensemble
  de-noising, and it exceeds a **like-for-like multi-snapshot decoy null** in its **unbiased release
  (design) frame** — but **not** in the biased metad-opened frame, where the null balloons and the
  candidate does not stand out.
- Gate 4 is therefore scored **met in silico by a single lead (denovo_401) whose specificity control
  passes in its design frame but is receptor-frame-dependent** — a real but qualified pass, consistent
  with the "fragile margin in a cryptic pocket" thesis. Honest bounds: single-trajectory GB-implicit
  MD (not affinity-grade FEP), unsynthesized, no wet lab; and the decoy null controls the **scoring**
  step but not the **generative** step or the best-of-N selection (see SI §4, F16). The affinity-grade
  selectivity tier (three-replicate ABFE) has since been **run** and is NR4A3-selective in direction
  across all three replicates (offset-invariant ΔΔG only; NR4A2 λ-overlap repair pending).

---

## SI §2 — Pre-registered gates: outcomes

*Calibration panel (fpocket, same pipeline throughout).* Experimentally drug-bound NR ligand sites
score **0.53–0.68** (PPARγ 0.599, ERα 0.586, Nurr1-holo 0.677, Nur77-holo 0.529), defining
**D\* = 0.53**. The static NR4A3 orthosteric pocket scores **0.495** (< D\*). The occluded Nurr1
crystal scores 0.864 at a *non-orthosteric* cavity (the reason the max-anywhere metric was
discarded). The NR4A2 AF2 model's max (0.801) ≈ the occluded crystal's max (0.864), i.e. **no
model over-call**.

| Gate | Tests | Pre-fixed threshold | Outcome | Basis |
|---|---|---|---|---|
| **0** | Pipeline separates druggable from occluded NR pockets; sets D\* | Controls ≥ 0.5; occluded crystal max < 0.5 | **Deviation → pass on corrected metric** | Max-anywhere non-discriminating (occluded crystal 0.864); corrected to ligand-site metric, D\* = 0.53 from drug-bound controls (disclosed; SI §1.5) |
| **0b** | AF2-model over-call of the cavity | Interpretation (not pass/fail) | **No over-call** | NR4A2 model max 0.801 ≈ occluded crystal 0.864 → static NR4A3 0.495 is trustworthy and conservative |
| **1** | A genuine cryptic *opening* occurs | Converged F(Rg) shows an opened minimum/shoulder distinct from the closed basin | **Qualified — met only in the weaker basin-breathing sense** | F(Rg) monotonic (single closed basin, rising wall, no opened minimum); druggable frames reached by basin-internal breathing, not a two-state switch; consistent with de Vera 2019 |
| **2** | The opened state is druggable | ≥ 5 % of opened frames ≥ D\*; pocket still lines 406–534; handles pocket-facing | **Pass (both clauses)** | Peak orthosteric Pocket-5 druggability 0.931 (max over frames; report as fraction ≥ D\*, met); mean 5.0/7 selectivity handles pocket-facing in druggable frames (L406, T410, I484, I531, L534 reliably inward; T407/R412 splay outward) |
| **3A** | Opened geometry **persists** after bias removal | Seeded druggable frame does not promptly collapse in unbiased MD | **Supported** | Unbiased release MD seeded at the low-energy druggable frame: geometry **persists — 3/3 replicas held 5 ns, mean drift 0.025 nm, no collapse**, and is **druggable in ~24 % of unbiased frames** (max 0.842, mean 0.262) at Rg ≈ 0.737 — a spontaneously sampled cavity, not a static always-open pocket |
| **3B** | Opening is **equilibrium-accessible** from the closed ensemble | Converged closed → druggable-open cost ≤ ~5 kcal/mol | **Unresolved** | F(Rg) is monotonic/under-converged and the release replicas do not agree on a converged opening free energy, so the equilibrium population is not established; the ~0.76 kcal/mol reading of the biased profile is a feasibility number, not a converged cost. 5 ns rules out prompt collapse, not tens-to-hundreds-of-ns relaxation |
| **4** | A selective, drug-like ligand engages the pocket | Docks well, contacts handles, predicted selectivity margin vs NR4A1/2 | **Qualified pass in silico (one lead)** | denovo_401: multi-snapshot margin +12.83 ± 2.98 (margin − SD +9.85); exceeds a like-for-like multi-snapshot decoy null in its **release/design frame**, but **not** in the biased metad-opened frame (receptor-frame-dependent). Endpoint MM-GBSA + three-replicate ABFE (below); unsynthesized; decoy null controls scoring but not generation (SI §4, F16) |

**Decision-rule reading.** Gate 0 passes (on the corrected, disclosed metric) and Gate 0b is
reassuring. Gate 2 passes cleanly. Gate 1 is met only in the weaker basin-breathing sense. Gate 3 is
split: **3A (persistence after bias removal) is supported** by the unbiased release run (the seeded
druggable geometry holds 5 ns in 3/3 replicas and is druggable in ~24 % of frames), while **3B
(equilibrium accessibility) is unresolved** — the biased F(Rg) is monotonic/under-converged and the
replicas do not agree on a converged opening free energy, so we do not claim the opened state's
equilibrium population. Gate 4 is a qualified, in-silico, frame-dependent pass carried by a single
lead. Net: the orthosteric pocket is **computationally tractable as a dynamic, basin-breathing site
whose opened geometry persists once bias is removed** at feasibility weight; the affinity-grade
selectivity tier (three-replicate ABFE) has since been **run** — NR4A3-selective in direction across
all three replicates (offset-invariant ΔΔG −4.76/−4.98 kcal/mol vs NR4A1/NR4A2; NR4A2 λ-overlap repair
pending; absolute scale not validated).

---

## SI §3 — Selectivity architecture: a binder × ternary budget

### §3.1 Two axes, three stages, one multiplicative budget

"Selectivity" for this degrader is not one thing. There are two independent axes, each of which can
in principle be encoded at any of three pharmacological stages.

**Axes (what to discriminate).**
- **Axis A — paralogue:** NR4A3 vs NR4A1 and NR4A2. A tox-mitigation requirement — combined loss of
  NR4A1 and NR4A3 is leukaemogenic in mice; loss of NR4A2 risks dopaminergic/Parkinsonian effects.
  Sparing the paralogues is about therapeutic index, not anti-tumour efficacy.
- **Axis B — fusion vs wild-type:** the oncogenic driver is the EWSR1/TAF15::NR4A3 chimera;
  wild-type NR4A3 also exists in normal tissue. Discriminating the two is an efficacy /
  on-target-safety axis — it is what would make the therapy tumour-exclusive.

**Stages (where selectivity can be encoded).** (1) **Binding** — warhead affinity for the NR4A3 LBD
pocket versus the paralogue/wild-type pockets. (2) **Ternary** — formation of a *productive*
E3–PROTAC–target complex: PPI-surface complementarity, cooperativity (α), and degradable-lysine
geometry. (3) **Kinetics** — ubiquitination rate, complex residence time, target resynthesis rate.

**The governing model.** Degradation selectivity is **multiplicative** across stages:

```
S_degradation(target_i vs target_j)  ≈  S_binding × S_ternary × S_kinetic
```

The factors **compound**: the selectivity burden can be placed on whichever stage is cheapest and
most reliable to engineer, and a non-selective binder can in principle degrade selectively if only
one paralogue forms a productive ternary geometry (the established cooperativity precedent — e.g.
MZ1–BRD4 positive cooperativity driving BRD4 selectivity from a pan-BET binder). The important
consequence is that the binder does **not** have to carry selectivity alone.

### §3.2 The warhead pocket is a selectivity hotspot, not a conserved liability

The intuition that paralogue selectivity must come from the ternary because the conserved LBD pocket
cannot deliver it is **wrong for NR4A3**. Comparing divergence in the orthosteric cryptic pocket (the
warhead's contact residues) against the LBD-wide pocket-residue census, using the family alignment
(AFDB models + BLOSUM62):

| residue set | n | divergent vs ≥ 1 paralogue | divergent vs **both** paralogues |
|---|---|---|---|
| **Orthosteric cryptic pocket (warhead contacts)** | 10 | **70 %** | **60 %** |
| LBD-wide pocket census | 148 | 45 % | 28 % |
| Non-orthosteric remainder (surface/PPI proxy) | 138 | 43 % | — |

The warhead pocket is **~1.6× more divergent than the rest of the LBD** (70 % vs 43 %), and on the
stricter "differs from *both* paralogues at once" criterion the gap is wider (60 % vs 28 %). Far from
a conserved wall, the NR4A3 orthosteric pocket is the **most paralogue-divergent zone of the LBD** —
a selectivity hotspot.

**Reading.** The binder's selectivity problem was never handle scarcity (seven of ten pocket-contact
residues diverge; five stay pocket-facing and are engageable). The binder's *actual* problem is
**druggability + affinity-margin robustness**: NR4A3's pocket is the least druggable of the three
paralogues, it is **cryptic** (druggable in only ~a quarter of unbiased frames), and a selectivity
margin large enough to survive scoring noise is hard to reach — but *achievable* with effort
(denovo_401 holds at +12.83 ± 2.98, margin − SD +9.85, under multi-snapshot MM-GBSA). The decoy-control
non-specificity and the multi-snapshot collapse of an earlier single-snapshot "best" are symptoms of
**noise in a poorly druggable pocket**, not of absent divergent contacts.

### §3.3 The asymmetric paralogue window

The engageable window is **asymmetric across paralogues**. Of the seven divergent handles, five stay
pocket-facing in the druggable ensemble (L406, T410, I484, I531, L534). All five distinguish NR4A3
from NR4A1, but only four distinguish it from NR4A2, because **I531 is identical (Ile) in NR4A3 and
NR4A2**. NR4A2 is therefore the molecularly *harder* paralogue to spare — relevant because NR4A2/Nurr1
carries the dopaminergic-loss liability one most wants to avoid. Because that NR4A2 toxicity is
anatomically **CNS-localized** and EMC is a peripheral soft-tissue sarcoma, the cheapest reliable
NR4A2-sparing lever is **pharmacokinetic** (a peripherally restricted, non-CNS-penetrant degrader),
not molecular; molecular NR4A2 selectivity is a secondary top-up. NR4A1 selectivity, by contrast, is
sourced from the binder's NR4A1-discriminating contacts compounded with the ternary.

### §3.4 The ternary is productive but not paralogue-selective for this linker — and where selectivity remains structurally available

The predicted **NR4A3/NR4A1/NR4A2-LBD + CRBN + denovo_401-PROTAC** ternaries (pipeline validated on the
CRBN + lenalidomide control, which seats the glutarimide in the tri-tryptophan pocket, 2.85 Å to W380,
ligand-iPTM 0.99 — an in-distribution sanity check, not a generalization proof) show **all three
paralogues form an equally productive-geometry complex**: the PROTAC bridges LBD and CRBN, and each
LBD presents an exposed lysine within ubiquitin reach of CRBN (NR4A3 K195 3.1 Å, NR4A1 K53 2.3 Å,
NR4A2 K175 4.0 Å), with comparable within-noise confidence (iptm 0.72/0.83/0.82). So the ternary is
**productive (the degrader mechanism is geometrically viable) but not a paralogue-selectivity lever
for this linker** — it does not add NR4A3 selectivity on top of the binder. This is mechanistically
unsurprising (the PROTAC engages the conserved LBD fold) and **narrows the selectivity budget onto the
binder** (+ pharmacokinetics/CNS-exclusion for NR4A2).

**But the ternary is not a spent lever.** Mapping paralogue divergence at the predicted NR4A3–CRBN
interface (33 residues) shows **8 of 33 interface residues differ from each paralogue (24 %), 6 from
both (18 %: E545, T563, Q570, S571, L576, E580, V588 …)**, on a surface **distinct from the pocket
handles** (0 of the 7 handles lie at the interface). Ternary selectivity is therefore **structurally
available** — a divergent patch a linker could be designed toward — just **not realized** by this
representative linker. Because that patch and the pocket handles are **independent residue sets**, a
binder and a ternary that each drew on its own set would deliver a genuine *multiplicative* gain.

**Caveats.** One representative linker/exit vector was tested (the interface — and its divergent-patch
set — will shift with the linker). Boltz returns a single ternary pose, not the cooperativity (α) or
the productive ensemble that sets real degradation selectivity, so single-pose docking can **flag
availability** but cannot **optimize or validate** ternary selectivity (a ternary-ensemble method is
the appropriate tool). The lysine-proximity is a CRBN-only proxy (no full CRL4^CRBN + E2~Ub).

### §3.5 Fusion vs wild-type is unobtainable from the degrader

A LBD-binding degrader **cannot** distinguish the fusion from wild-type NR4A3 at any stage. The fusion
retains the identical NR4A3 LBD; the only tumour-unique feature is the EWSR1/TAF15::NR4A3 junction,
which lies in a disordered N-terminal region with no structured pocket, tens of nanometres of
disordered chain from where the ternary forms at the LBD. No kinetic handle distinguishes two proteins
identical in the degraded domain. Fusion-versus-wild-type exclusivity is therefore the **complementary
antisense (ASO) route's** job (RNA-level base-pairing to the chimeric junction spares wild-type NR4A3);
the degrader's honest scope is **paralogue selectivity plus accepted wild-type-NR4A3 loss** (a
tolerability argument — viable single-knockout animals, paralogue redundancy, catalytic dose-titratable
pharmacology — not a selectivity one).

### §3.6 Allocation of the selectivity budget for EMC

- **Binder:** keep it selective *and* optimize for affinity + a productive, solvent-exposed exit
  vector. A selective binder is the primary goal and strictly valuable; denovo_401 delivers a
  decoy-null-screened paralogue margin (a foothold, not a fully control-validated specificity result).
  The margin is **fragile** in a poorly druggable cryptic pocket, which argues for *compounding* it with
  the ternary — not for abandoning binder selectivity.
- **NR4A1 selectivity:** source primarily from the binder's NR4A1-discriminating contacts compounded
  with the ternary (a divergent interface patch, §3.4).
- **NR4A2 safety:** source primarily from PK / CNS-exclusion (peripheral restriction), because the
  molecular handle is the weakest (I531 shared) and the toxicity is CNS-localized.
- **Fusion vs wild-type:** do not attempt with the degrader; route to the ASO. Accept wild-type NR4A3
  loss as a labelled on-target cost.
- **Pan-NR4A:** off the table for systemic EMC (combined NR4A1+NR4A3 loss is leukaemogenic); retained
  only as a deliberate ex-vivo immuno-oncology design mode (reversing CD8⁺ T-cell exhaustion requires
  degrading all three NR4As).

---

## SI §4 — Adversarial self-review (distilled)

The manuscript was subjected to four passes of adversarial self-review. The scope of each pass was the
*manuscript's claims, framing, and internal consistency* — "an experiment is not finished" was never a
finding; "the writeup claims more than the finished analyses establish" was. Twenty findings (F1–F20)
are summarized below with their severity and the mitigation applied. All mitigations were folded into
the manuscript and its supporting analyses.

| # | Severity | Finding | Mitigation / status |
|---|---|---|---|
| **F1** | High | Gate 1 was never scored, and as written it is **not** met (F(Rg) monotonic → druggable frames are basin-internal breathing, not a distinct opened basin) | Added an explicit, honest Gate 1 entry (met only in the weaker basin-breathing sense); reframed abstract/§2.2 to "breathes to transiently druggable conformations"; retired the "Gates 0–3 pass" overstatement. **Resolved** |
| **F2** | Medium | The 0.931 opened-frame druggability is an extreme-value statistic compared to the static holo panel as if on one scale | Report as the **fraction** of frames ≥ D\* (pre-registered ≥ 5 % bar, met) with 0.931 as a biased-MD **peak**; added the biased-vs-static caveat; noted enclosure-rewarding metric means a merely splayed pocket would score lower. A bespoke fpocket negative control was considered and **retracted as redundant** (fpocket is a standard, panel-anchored metric incl. the occluded-crystal negative; the physical-population question is the release run's, not fpocket's). **Resolved** |
| **F3** | High | Metric conflation: 0.931 sat under a "max druggability" column shared with max-anywhere crystal scores — the very apples-to-oranges error the paper accuses others of | Relabelled the metad-opened row as the **orthosteric Pocket-5 score, max over frames** (commensurate with the static 0.495 and D\*), distinct from the max-anywhere crystal column. **Resolved** |
| **F4** | Medium-high | Gate 3's ~38 → ~0.76 kcal/mol rescue reads a second point off the *same* under-converged biased profile, yet the paper called Gate 3 "resolved" | Reworded to **provisionally met** by the basin-breathing reading of an incompletely converged F(Rg); the independent metastability confirmation is the unbiased release run. **Resolved** |
| **F5** | Medium | "Converged" was overstated | Replaced with "production-length (30 ns); the closed basin is well-sampled, the opening frontier is not fully converged." **Resolved** |
| **F6** | Medium | NR4A1-vs-NR4A2 selectivity asymmetry was hidden by a single "divergent" flag | Added the per-paralogue breakdown: engageable divergent handles are **5 vs NR4A1 but 4 vs NR4A2** (I531 conserved with NR4A2); flagged NR4A2 as the harder, narrower case. **Resolved** |
| **F7** | Medium | "AciCC substantially more common than EMC" was unsourced (medical-integrity rule) | Softened to "a more common salivary-gland carcinoma than EMC (incidence locator to attach before submission)"; flagged the missing citation. **Resolved (citation pending)** |
| **F8** | Low | The binding-selectivity matrix is necessary-but-not-sufficient for *degradation* selectivity | Sharpened §2.4/§5 to frame the matrix as a necessary-not-sufficient filter, with degradation-direction selectivity set downstream by the ternary. **Resolved** |
| **F9** | High | The first de-novo "warhead" (denovo_15) is a generative-model artifact (carbamic acid, 1,3-cyclopentadiene, imine, no aromatic ring; SAscore above the campaign cut) presented as a candidate | Recast throughout as a **selective chemotype/pose hypothesis** to be re-designed into a stable, synthesizable analogue; named the specific liabilities. Triage of the other confirmed-selective hits (peroxide/acetals, or clean-but-weak) rescued none. **Resolved** |
| **F10** | Medium-high | The de-novo tier was labelled "criterion-matched" but docks NR4A3 in its unbiased-release frame against biased-metad paralogue frames | Dropped "criterion-matched" from §2.5; added the receptor-state caveat and noted the mismatch biases **against** NR4A3-selectivity (so a positive call is conservative). **Resolved** |
| **F11** | Medium | Gate 4 was never scored though the de-novo campaign is its test (the F1 failure mode, repeated) | Added an explicit Gate 4 scoring paragraph and deviation-log entry. **Resolved** |
| **F12** | Medium | "Metastable (3/3) AND druggable ~24 %" conflates a triplicate Rg-persistence result with a single-replica druggability result; 5 ns excludes only prompt collapse | Added a scope note: 3/3 is Rg-persistence across the triplicate; ~24 % is measured on one release replica; 5 ns rules out prompt, not tens-to-hundreds-of-ns, collapse. **Resolved** |
| **F13** | Medium | "MM-GBSA direction is robust" was asserted without any replicate/error estimate | Stated the single-snapshot verdicts (incl. "reversed 0") are unreplicated point estimates whose sign can move with pose/snapshot; multi-snapshot averaging is the follow-up. **Resolved** |
| **F14** | Low | Internal inconsistency in denovo_15's matrix cell (paper vs handoff memo) | Reconciled the handoff line to the paper (cell = NR4A2+NR4A3; no NR4A3-only cell exists). **Resolved** |
| **F15** | High (decisive) | Single-snapshot MM-GBSA "NR4A3-selective" verdict is **non-specific**: 38 non-NR4A marketed drugs through the identical funnel score 39 % (15/38) "confirmed_selective" (caffeine, ibuprofen, lidocaine, phenytoin …); the de-novo set is **not enriched** | Retracted "MM-GBSA-confirmed NR4A3-selective"; established the decoy null as a **standing gate**; made a properly controlled multi-snapshot/ensemble or FEP tier the *necessary* fix. **Resolved (decisive)** |
| **F16** | High | The decoy null controls the **scoring** step but not the **generation** step (denovo_401 was pocket-conditioned on the release frame; the decoys were fit to no pocket) or the best-of-N selection; the release frame it passes is the one it was designed for, and the level-playing-field metad frame it **fails** | Narrowed the claim to a **"de-noised foothold, not a demonstrated specificity result."** The confound is **empirically bounded small** (all ~191 developable generations shared the release frame, yet the set is not enriched over decoys and only ~2/11 survive de-noising — uniform inflation would clear the whole set). The decisive resolution is **FEP** (machinery-independent); a generation-matched decoy null is a lower-value follow-up. **Narrowed; FEP is the gate** |
| **F17** | Medium-high | Winner's-curse: denovo_401 is the max of ~10 noisy estimates, so its point estimate is upward-biased beyond the reported within-candidate SD | Added the best-of-~10 selection-bias note; an independent-seed multi-snapshot replicate (+14.75 ± 4.82) reproduces the margin, bounding the bias. **Mitigated** |
| **F18** | Medium | The Boltz-2 ternary "positive control" (CRBN + lenalidomide) is a canonical, in-training-data complex, so "the model can be trusted for the NR4A3 prediction" overclaims generalization | Softened to "reproduces a *known* IMiD mode — a necessary sanity check, not a generalization proof." Then **resolved by running the actual prediction**: the NR4A3/NR4A1/NR4A2 ternaries all form equally productive complexes → no ternary selectivity for this linker (which also *corrected* the earlier hope that the ternary "multiplies" the binder margin). **Resolved** |
| **F19** | Medium | Stale absolute claim ("denovo_111 the one candidate to clear the null; every other de-novo falls in it") is contradicted by denovo_401's own single-snapshot margin | Qualified to "the one candidate **in that harvest**"; noted denovo_401 (a later batch) also clears the single-snapshot bar and dominates on de-noising. Subsequently **denovo_111 was withdrawn** by a pre-FEP species sweep (its physiological cation reverses selectivity, multi-snapshot −15.01 ± 5.14), leaving denovo_401 as the sole robust lead. **Resolved/superseded** |
| **F20** | Low | The working-doc abstract carried an editing artifact (doubled "still") and buried the honest bottom line across three successive retracted leads | Removed the artifact; the deliverable preprint abstract is the tighter, factually current version (feasibility druggability result + one de-noised foothold, no FEP, no wet lab). **Resolved** |

**Net effect of the review.** The self-review repeatedly **narrowed** claims to what the finished
analyses support: the druggability case is a **feasibility** result (a basin-breathing cavity druggable
~a quarter of the time — persistence supported, equilibrium accessibility unresolved — not an always-open
pocket); the lead is a **receptor-frame-dependent de-noised foothold**, not a demonstrated-specificity
hit; the ternary is **productive but not paralogue-selective** for the representative linker; and the
affinity-grade **selectivity ABFE** has since been **run** (three-replicate, NR4A3-selective in direction;
offset-invariant ΔΔG only, NR4A2 λ-overlap repair pending). No finding was left un-mitigated, and every
mitigation moved the manuscript toward a more conservative reading.
