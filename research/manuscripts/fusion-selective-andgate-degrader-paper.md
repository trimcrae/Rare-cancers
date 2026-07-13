# A coincidence-detection ("AND-gate") bivalent degrader for protein-level fusion-exclusivity in EWSR1::NR4A3 extraskeletal myxoid chondrosarcoma

> **In-silico design / feasibility draft (2026-06).** No wet lab; **no molecule synthesized; NO new
> GPU/AWS run was performed for this draft.** The *only* new computation cited here is a CPU/stdlib
> avidity model — [`../modalities/fusion-andgate-selectivity-model.json`](../modalities/fusion-andgate-selectivity-model.json)
> (produced by [`../modalities/andgate_selectivity_model.py`](../modalities/andgate_selectivity_model.py)).
> **The fusion-exclusivity rationale in one line:** an LBD-binding degrader cannot tell the fusion from
> wild-type NR4A3 (the LBD is the *same* sequence in both); a bivalent ligand whose two arms are each
> individually too weak — arm 1 on the shared NR4A3 LBD, arm 2 on the *fusion-restricted* EWSR1
> low-complexity domain / its condensate — engages, by **avidity, only the chain that presents both
> features at once**, i.e. only the fusion, sparing wild-type NR4A3 and its tumour-suppressor role.
> Every Kd/EM input to the model is an **illustrative assumption**, not a measured affinity, and is
> flagged as such throughout. Every clinical claim is cited or flagged. Nothing here is a validated drug
> or clinical evidence.

---

> **⚠ CORRECTION / ERRATUM (2026-07-13, reviewer-AI) — read before the draft.** This draft repeatedly calls the
> EWSR1 low-complexity (LC/IDR) domain a "**fusion-restricted** feature … present only in the chimera." **That is
> imprecise and is corrected here:** wild-type EWSR1 also carries the N-terminal LC/transactivation domain. What is
> genuinely fusion-specific is the **covalent adjacency *in cis*** of EWSR1-LC to the NR4A3-LBD on one polypeptide
> (`EWSR1-LC :: NR4A3-LBD`), **not** the LC domain itself. The avidity/AND-gate logic below is unchanged and still
> valid (it relies on each arm being individually weak), but two consequences must be read into it: (1) an EWSR1-LC
> arm *alone* would also bind normal EWSR1 — specificity comes ONLY from requiring **both** sites in cis; (2) a new
> dominant failure mode — the bivalent molecule binding **WT NR4A3 + WT EWSR1 as two separate proteins *in trans***
> (especially in transcriptional condensates) — must be excluded by demonstrating **K_eff(cis fusion) ≫
> K_eff(trans)** (linker reach / effective molarity / geometry). The blocking gate, stated narrowly: **no validated,
> selective, cell-active, chemically-tractable EWSR1-LC (or junction) second-arm ligand currently exists** —
> YK-4-279 / TK216 bind *recombinant* EWS::FLI1 but do **not** qualify as a transferable EWSR1-LC arm. Because of
> this gate, the fusion-EXCLUSIVE degrader is a **research hypothesis, NOT a synthesis-ready claim.** Full corrected
> treatment: [`nr4a3-degrader-strategy-ternary-first.md` → "DEFERRED DECISION — selectivity TARGET"](./nr4a3-degrader-strategy-ternary-first.md).

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is defined in the large majority of cases by an in-frame fusion
of *EWSR1* (less often *TAF15*) to the orphan nuclear receptor *NR4A3*, on an otherwise "quiet" genome
[Sjögren; Panagopoulos]. The companion NR4A3-degrader program in this repo recruits the **NR4A3
ligand-binding domain (LBD)** to an E3 ligase ([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)).
That LBD sequence is **identical in the fusion and in wild-type NR4A3** — the fusion retains a near-intact
LBD — so the agent is NR4A3-selective (it can be tuned to spare the NR4A1/NR4A2 paralogues) but **not
fusion-selective**: it also removes tumour-suppressive wild-type NR4A3, whose loss is implicated in AML and
in HCC/breast/lymphoma [Mullican 2007; Safe & Karki 2021]. This manuscript designs the protein-level route
to the feature the LBD degrader structurally cannot reach: **true fusion-exclusivity.** We exploit
**coincidence detection (an "AND-gate")**. Arm 1 binds the shared NR4A3 LBD (the opened cryptic pocket of
the companion paper); arm 2 binds the EWSR1 low-complexity/transactivation
domain (LC/IDR) or its phase-separated micro-environment — a feature whose *fusion-specificity comes from its
cis-adjacency to the NR4A3-LBD*, NOT from the LC domain being unique to the chimera (WT EWSR1 has it too; see
Erratum). Each arm is chosen
**deliberately too weak** to occupy its target alone. Only the fusion presents *both* features on one
polypeptide, so once one arm engages, the second arm's high effective concentration (effective molarity,
EM) drives bivalent, avidity-enhanced binding; wild-type NR4A3, seen by arm 1 only, stays largely unbound.
We quantify this with a CPU effective-molarity model (the only new computation here). In a base case with
illustrative arm affinities Kd1 = 10 µM (LBD), Kd2 = 100 µM (EWS-LC) and EM = 1 mM, the fusion is engaged
at an avidity Kd ≈ 1 µM and is bound 5.5× more than wild-type NR4A3 — a **binding** window tunable to
~11× by raising EM (shorter/optimised linker) or weakening the single arms. We are explicit that (i) the
inputs are assumptions, not affinities; (ii) this is a *binding* window, not a *degradation* window
(degradation selectivity is additionally set by the ternary complex); and (iii) the hard, unproven part is
arm 2 — the EWS-LC domain is intrinsically disordered (mean pLDDT 38.8, 98.1% of residues < 50;
[`novel-modalities.md`](./novel-modalities.md) §2) with no pocket, so arm 2 cannot be a classical pocket
ligand and must be an emerging condensate-partitioning / IDR-contacting moiety. We lay out the deferred
(GPU-requiring) in-silico program and the decisive experiment for others. The AND-gate logic generalises
to any fusion that joins a ligandable domain to an IDR — the FET-fusion sarcomas broadly.

---

## 1. Background and the fusion-selectivity gap

EMC's defining lesion fuses the N-terminal low-complexity/transactivation domain of EWSR1 (a FET-family
prion-like IDR) to most of NR4A3, including a near-intact ligand-binding domain [Sjögren; Panagopoulos;
Boulay 2017 for the EWS prion-like domain's condensate/BAF-retargeting behaviour]. On a quiet genome the
chimera is, to a first approximation, the disease — an attractive single target.

The repo's lead protein-level agent is a **degrader of the NR4A3 LBD**
([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)): because the collapsed orphan-receptor pocket
precludes occupancy pharmacology, the apt modality is to recruit the ordered LBD to an E3 ligase and remove
the protein. That program shows the LBD's borderline static pocket (fpocket druggability 0.495, below the
calibrated drug-bound band 0.53–0.68) **breathes** under metadynamics into transiently druggable
conformations, and it maps NR4A3-vs-NR4A1/NR4A2 divergent residues as handles for **paralogue**
selectivity.

**But paralogue selectivity is not fusion selectivity.** The LBD that the degrader's warhead engages is
the *same* domain — the same sequence, ~100% identity over the LBD — in the EMC fusion and in wild-type
NR4A3. A warhead that binds the fusion's LBD will, by construction, bind wild-type NR4A3's LBD equally
well. So the LBD degrader degrades *all* NR4A3 (and is rightly framed target-centrically, covering both
EMC and NR4A3-over-expression diseases such as acinic cell carcinoma). The residual liability is real:
wild-type NR4A3 is **tumour-suppressive** outside EMC — combined Nr4a1/Nr4a3 loss causes AML in mice
[Mullican 2007], and NR4A3 is tumour-suppressive in HCC/breast/lymphoma [Safe & Karki 2021]. An ideal EMC
agent would remove the fusion while leaving wild-type NR4A3 intact.

No single shared epitope can deliver that, because the only fusion-unique *protein* feature is the
**juxtaposition** of the EWSR1 LC domain and the NR4A3 LBD on one chain — neither half is itself unique to
the fusion (wild-type EWSR1 has the LC domain; wild-type NR4A3 has the LBD). The design problem is
therefore not "find a fusion-only pocket" but "**detect the co-occurrence** of two non-unique features on
one molecule." That is exactly what a coincidence-detecting bivalent ligand does.

---

## 2. The AND-gate design

The molecule is a single bivalent ligand with two binding arms joined by a linker, plus (in the degrader
version) an E3-recruiting element. Coincidence is enforced by avidity.

- **Arm 1 — the shared LBD warhead.** This is the **opened-LBD cryptic-pocket warhead** of the companion
  degrader paper ([`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md) §2.2–2.4). Cited at honest weight:
  that pocket's druggability rises under bias to a **biased-MD peak of 0.931** (maximum over 600 opened
  frames — an extreme-value statistic best read as a *fraction-of-frames-druggable distribution*, not a
  single number), via **basin-internal breathing** rather than a separate opened free-energy basin (F(Rg)
  is monotonic), at a low apparent cost (~0.76 kcal/mol to a druggable conformation, read off an
  incompletely-converged biased profile and therefore **provisional** pending the unbiased release run)
  [see [`nr4a3-degrader-paper-redteam.md`](./nr4a3-degrader-paper-redteam.md) F1–F5]. Arm 1 binds the LBD
  that the fusion and wild-type NR4A3 share. **Crucially, here we want this arm *weak*** — strong enough to
  contribute to avidity on the fusion, too weak to occupy wild-type NR4A3 on its own.

- **Arm 2 — the fusion-restricted anchor.** Arm 2 binds the **EWSR1 low-complexity / transactivation
  domain** (residues 1–264 of the fusion's EWS portion) or, more realistically, the **condensate
  micro-environment** that this prion-like IDR nucleates [Boulay 2017]. This feature is present only in the
  fusion: wild-type NR4A3 has no EWS LC domain. Arm 2 is the harder arm (§4) precisely because the LC
  domain is disordered and pocket-less.

- **The coincidence logic.** On the **fusion**, both features sit on one chain. Once either arm binds, the
  partner arm is held at a high local concentration — the **effective molarity (EM)** — so the second
  engagement is intramolecular and avidity-enhanced; the apparent bivalent dissociation constant follows
  the standard tethered-ligand relation **Kd_avidity ≈ Kd1·Kd2 / EM** (valid when EM ≫ Kd2). On
  **wild-type NR4A3**, there is no arm-2 partner, so only arm 1 can engage — **monovalently, at the weak
  Kd1**. Choosing both arms weak enough that neither meaningfully occupies its target alone means wild-type
  NR4A3 (arm 1 only) stays largely unbound, while the fusion (both arms, avidity) is engaged. The molecule
  thus computes a logical AND over "LBD present" and "EWS-LC present" — true only for the fusion.

This is the only one of the three protein-level fusion-unique routes (the other two being a juxtaposition-
created composite surface, and a condensate-conditional degrader) that converts two *individually
non-selective* contacts into a *selective* one purely through geometry/avidity, without requiring a
genuinely fusion-unique pocket to exist.

---

## 3. Quantitative selectivity model (the new CPU result)

The one new computation here is a pure-stdlib, CPU-only equilibrium avidity model
([`andgate_selectivity_model.py`](../modalities/andgate_selectivity_model.py) →
[`fusion-andgate-selectivity-model.json`](../modalities/fusion-andgate-selectivity-model.json)). It asks a
single quantitative question: *can two arms that are each individually too weak to matter become
fusion-selective by avidity?* The selectivity window is defined as (fraction of fusion bound) / (fraction
of wild-type NR4A3 bound) at a given free-ligand concentration; the fusion is modelled by Kd_avidity =
Kd1·Kd2/EM, wild-type by Kd1 alone.

**The inputs are illustrative assumptions, not measured affinities** (the JSON carries
`_inputs_are_illustrative: true`). They are parameterised to plausible ranges from the bivalent/PROTAC/
avidity literature [Békés/Langley/Crews 2022] to test the *design principle*, and assert nothing about any
real compound.

**Base case** (Kd1 = 10 µM on the LBD, Kd2 = 100 µM on EWS-LC, EM = 1 mM, free ligand 1 µM):

| quantity | value |
|---|---|
| Kd_avidity (fusion) | ≈ 1 µM (= Kd1·Kd2/EM) |
| fusion fraction bound | 0.50 |
| wild-type NR4A3 fraction bound | 0.091 |
| **fusion-vs-wild-type window** | **5.5×** |

So with each arm individually weak, wild-type NR4A3 — engaged only monovalently by arm 1 — stays ~9%
bound, while avidity pulls the fusion to ~50% bound: a **5.5× binding window** from arms that, alone, would
be dismissed as too weak to develop.

**The window is tunable.** Sweeping the effective molarity (the key linker-geometry knob) at fixed arms:

| EM (M) | Kd_avidity | fusion bound | WT bound | window |
|---|---|---|---|---|
| 1e-4 | 10 µM | 0.091 | 0.091 | 1.0× (no avidity — arms equal, no selectivity) |
| 3e-4 | 3.3 µM | 0.231 | 0.091 | 2.5× |
| **1e-3** | **1.0 µM** | **0.500** | **0.091** | **5.5× (base case)** |
| 3e-3 | 0.33 µM | 0.750 | 0.091 | 8.2× |
| 1e-2 | 0.10 µM | 0.909 | 0.091 | 10.0× |
| 3e-2 | 33 nM | 0.968 | 0.091 | 10.6× |
| 1e-1 | 10 nM | 0.990 | 0.091 | **10.9× (ceiling)** |

The window rises from 1× (no avidity) to a ceiling of **~11×** as EM increases — i.e. a shorter, better
pre-organised linker that raises the second arm's local concentration widens fusion-selectivity, because
the wild-type baseline (arm-1-only, fixed at 0.091) does not move. Sweeping arm-1 strength tells the same
story from the other side: making arm 1 *weaker* (Kd1 100 µM) drops wild-type occupancy to ~1% and widens
the window to ~9×, while making arm 1 *strong* (Kd1 1 µM) lifts wild-type to 50% bound and collapses the
window to 1.8× — confirming the design rule.

**EM is not a free parameter — it is set by the linker, and the physics is encouraging.** A second
CPU/stdlib model ([`andgate_linker_em.py`](../modalities/andgate_linker_em.py) →
[`fusion-andgate-linker-em.json`](../modalities/fusion-andgate-linker-em.json)) grounds EM in ideal-chain
polymer physics: for a flexible linker of contour length L\_c and Kuhn length ~0.5 nm, the coincident-site
effective molarity EM = (3/(2π·L\_c·b))^{3/2}·(1e24/N\_A). Over the synthesizable range this gives EM from
~1.5 M (1 nm, ~3 PEG units) down to ~9×10⁻³ M (30 nm, ~86 units) — and, fed back into the avidity model,
the fusion-vs-WT window stays **~10–11× across the entire range** (10.8× at 10 nm, 9.9× even at 30 nm).
The design reading: because even a long tether keeps EM well above the weak arm-2 Kd (100 µM), the window
is **robust to linker length** rather than fragile — the ceiling (~11×) is set by arm-1 strength, not the
linker, so widening it means *weakening arm 1*, not shortening the tether. Honest caveat: this EM is the
*coincident-site upper bound*; a mobile, disordered EWS-LC anchor will realise a lower EM, so these are
optimistic ceilings (the §4 mobility point).

**Design rule (from the model):** *pick **both** arms individually too weak to occupy wild-type NR4A3 at
the dosed concentration, and rely on avidity (EM) to engage only the fusion, which uniquely presents both
features on one chain.* Larger EM (shorter/optimised linker) and weaker single arms widen the
fusion-vs-WT window — at the cost of needing a higher total dose to reach the avidity-bound fusion.

**From a binding window to a degradation window (a third CPU model).** Because a degrader acts through a
ternary complex, we modelled whether the binding window survives into *degradation*
([`andgate_degradation_model.py`](../modalities/andgate_degradation_model.py) →
[`fusion-andgate-degradation-model.json`](../modalities/fusion-andgate-degradation-model.json)): a
cooperative 1:1:1 target–degrader–E3 equilibrium where the fusion is engaged at the avidity Kd and
wild-type NR4A3 at the weak monovalent Kd1, with the **E3 arm and cooperativity shared** (both present the
same LBD/E3 handle). The result is sobering and honest: the degradation window **does not inherit the full
binding window** — it peaks near it (~6.8×) only at **low, sub-saturating** degrader and **erodes toward
~1× at saturating dose** (the hook effect — ternary falling as the degrader separately saturates target and
E3 — hits *both* species), and it **shrinks with stronger positive cooperativity** (5.4× at α=1 → 1.7× at
α=30, because cooperativity proportionally rescues the weaker-binding wild-type). Design implications: run
the AND-gate at **sub-saturating dose** and avoid strong cooperativity; and since the shared E3 side cannot
add selectivity, **all** of it must come from the avidity arm. So degradation selectivity is *narrower and
more dose-fragile* than the binding window — a genuine caveat, not a footnote.

**Two honest caveats, stated up front, not buried:**
1. **This is a binding window, not a degradation window.** Occupancy selectivity is necessary but not
   sufficient for *degradation* selectivity, which is additionally set by whether each species forms a
   productive ternary complex with the E3 ligase (a non-selective binder can degrade selectively, and vice
   versa). The 5.5–11× is fusion-vs-WT *occupancy*, the upstream filter — not a degradation margin.
2. **The numbers ride on assumed inputs.** They demonstrate the *principle scales as claimed*; they are not
   a prediction for any specific molecule. A modest window (single digits, low double digits) is the
   honest expectation for a real, manufacturable AND-gate — and is presented as such, not inflated.

---

## 4. The hard part (honest)

The AND-gate's selectivity is only as good as its weakest assumption, which is **arm 2**.

- **Arm 2 has no pocket to bind.** The EWSR1 LC/transactivation domain is intrinsically disordered:
  mean pLDDT **38.8**, with **98.1%** of residues below 50 ([`novel-modalities.md`](./novel-modalities.md)
  §2.1; [`nr4a3-structure-assessment.json`](../modalities/nr4a3-structure-assessment.json), EWSR1 region
  1–264). There is no folded cavity and no fpocket-druggable site on it — by contrast the NR4A3 LBD is
  confidently folded (mean pLDDT 85.0) yet still only borderline-druggable (best fpocket 0.495). So arm 2
  **cannot be a classical pocket ligand.** It must instead be a **condensate-partitioning / IDR-contacting
  moiety** — a chemotype that preferentially enriches in, or transiently contacts, the EWS-LC's
  phase-separated micro-environment [the prion-like-domain condensate behaviour of Boulay 2017]. This is an
  **emerging and genuinely hard** area: IDR/condensate-targeting medicinal chemistry is early-stage, the
  "site" is a dynamic ensemble rather than a structure, and predicting partitioning is not a solved
  problem. Arm 2 is the make-or-break unknown of this design, and we do not assert it is in hand.

- **The bivalent geometry must actually be reachable.** Even granting both arms, the molecule must span
  from the LBD pocket to the EWS-LC region in the folded-plus-disordered fusion with a linker that achieves
  the EM the §3 window assumes. The LBD is ordered; the EWS-LC is a flexible IDR whose spatial relationship
  to the LBD is not fixed — which both *helps* (the IDR can reach the linker) and *hurts* (the EM is an
  effective average over a fluctuating geometry, not a rigid tether). Linker length/rigidity, attachment
  vectors, and the E3-handle placement are all unsolved ternary-complex design problems.

- **EM is an assumption, and a fluctuating-geometry one.** The 1 mM–0.1 M EM range driving the §3 window
  is typical of *well-tethered* bivalent ligands; an arm anchored to a disordered, mobile IDR may realise a
  *lower* effective EM, shrinking the window toward the low end. The model's ceiling (~11×) should be read
  as optimistic.

---

## 5. In-silico program (clearly deferred — needs GPU later)

No GPU/AWS work was done for this draft. The computational program that *would* de-risk arms 2 and the
geometry is specified here but **deferred**:

1. **Ternary-complex / bivalent-pose modelling.** Build the fusion (opened-LBD ensemble from the companion
   metadynamics, reused directly) + EWS-LC ensemble, and sample arm-1/arm-2/linker poses to estimate the
   realisable effective molarity and whether a productive E3 ternary geometry is compatible with bivalent
   engagement. Reuses the existing opened pocket — no new pocket discovery needed for arm 1.
2. **Linker sampling.** Scan linker length/rigidity/attachment vectors against the EM the §3 model needs,
   to find the geometry that maximises the fusion-vs-WT window subject to synthesizability.
3. **Condensate-partitioning prediction for arm 2.** Apply emerging IDR/condensate-partitioning predictors
   to candidate arm-2 chemotypes — the highest-risk, least-mature step; success here is the precondition
   for the whole design.

These are GPU-class jobs (MD on the folded+disordered fusion, ternary docking) and are explicitly *not*
run here; the single new computation in this paper is the CPU avidity model of §3.

---

## 6. The decisive experiment others run

Computation cannot validate this; a wet-lab group would:

0. **First, the fusion-addiction precondition (no new chemistry).** Run the **dTAG** fusion-addiction test
   [Nabet 2018] — a FKBP12^F36V degron knock-in at the fusion locus in patient-derived EMC lines (USZ-EMC;
   NCC-EMC1/2 [Bangerter 2023; Iwata]) + acute dTAG-13/V-1 degradation viability — to confirm that *acute*
   removal of the fusion kills EMC cells. If acute fusion loss is not lethal, the entire degrader premise
   (AND-gate included) is moot, so this gates everything downstream.
1. **Then, synthesise a candidate** AND-gate bivalent degrader (arm 1 = opened-LBD warhead, arm 2 =
   condensate/IDR anchor, linker + E3 handle).
2. **Test fusion-vs-wild-type degradation selectivity** in EMC cells (fusion+) versus control cells
   expressing wild-type NR4A3 only: measure loss of fusion protein vs loss of wild-type NR4A3, confirming
   the AND-gate spares the latter. This converts the §3 *binding* window into the *degradation* window the
   design actually needs.

---

## 7. Selectivity & safety

The design's whole point is a safety improvement the LBD degrader cannot offer:

- **Fusion-exclusive — spares wild-type NR4A3.** Because wild-type NR4A3 is engaged only monovalently by a
  deliberately weak arm 1, it is largely untouched; this avoids depleting NR4A3's **tumour-suppressor**
  function elsewhere (the AML liability of combined Nr4a1/Nr4a3 loss [Mullican 2007]; NR4A3's
  tumour-suppressive roles in HCC/breast/lymphoma [Safe & Karki 2021]). This is the central advantage over
  the shared-LBD degrader.
- **Spares paralogues too.** Arm 1 can additionally carry the companion paper's NR4A3-vs-NR4A1/NR4A2
  selectivity handles ([`nr4a-selectivity.json`](../modalities/nr4a-selectivity.json): 7 divergent Pocket-5
  residues, 5 pocket-facing in the opened ensemble), so the agent can be both **fusion-selective** (via the
  AND-gate) and **paralogue-selective** (via the handles) — two orthogonal selectivity layers.
- **Net:** the AND-gate adds fusion-vs-wild-type-NR4A3 discrimination on top of the existing
  NR4A3-vs-paralogue discrimination, narrowing the on-target liability surface from "all NR4A3" to "fusion
  NR4A3 only."

---

## 8. Limitations

1. **Binding ≠ degradation selectivity.** The §3 window is fusion-vs-WT *occupancy*; degradation
   selectivity additionally requires a productive, species-specific ternary complex. The honest claim is a
   binding window, not a degradation margin.
2. **Arm 2 is unproven and hard.** Targeting the EWS-LC IDR / its condensate (pLDDT 38.8, no pocket) with a
   small-molecule arm is an emerging, unsolved problem; there is no validated arm-2 chemotype. If arm 2
   fails, the AND-gate fails.
3. **The window is modest.** ~5.5× base case, ceiling ~11×. This is a feature of honest modelling, not a
   shortfall to be inflated — and the realised window on a mobile-IDR anchor may sit at the low end.
4. **The model inputs are illustrative.** Kd1, Kd2 and EM are assumptions chosen from literature ranges to
   probe the design principle; they are not measured affinities and predict no specific molecule.
5. **No molecule, no GPU run.** Nothing was synthesized; the ternary/linker/condensate computations (§5)
   are deferred GPU work; the only new result here is the CPU avidity model.

---

## 9. Broader indications

The AND-gate logic is **target-general**: it works for *any* fusion that joins a **ligandable domain** (for
arm 1) to an **IDR / condensate-forming partner** (for arm 2) on one chain, where neither half is itself
fusion-unique but their *co-occurrence* is. The FET-fusion sarcomas are the natural set — Ewing sarcoma
(EWSR1::FLI1), desmoplastic small round cell tumour (EWSR1::WT1), clear-cell sarcoma (EWSR1::ATF1), myxoid
liposarcoma (FUS::DDIT3), and others — all fuse a FET prion-like IDR (the same class as the EWS-LC arm-2
target here) to a DNA-binding/effector partner that may furnish arm 1 [Boulay 2017 for the shared
prion-like-domain biology]. In each case the same coincidence-detection principle could, in principle, spare
the wild-type partners while removing the chimera — making EMC the worked example for a class-wide protein-
level fusion-exclusivity strategy. (These remain motivation, not demonstrated efficacy.)

---

## References

*Cited from the repo's verified pool; entries not in that pool are flagged "[citation to verify]". DOIs/
journals to collate to final format before submission.*

- Békés M, Langley DR, Crews CM. *PROTAC targeted protein degraders: the past is prologue.* **Nat Rev Drug
  Discov** 2022. doi:10.1038/s41573-021-00371-6. (Bivalent-degrader / avidity context for §3.)
- Nabet B, et al. *The dTAG system for immediate and target-specific protein degradation.* **Nat Chem
  Biol** 2018. doi:10.1038/s41589-018-0021-8. (Fusion-addiction precondition, §6.)
- Boulay G, et al. *Cancer-specific retargeting of BAF complexes by a prion-like domain.* **Cell** 2017.
  doi:10.1016/j.cell.2017.07.036. (EWS prion-like LC domain → condensate/BAF retargeting; the arm-2 target
  biology and the FET-fusion generalisation, §4, §9.)
- Wang Z, et al. *Structure and function of Nurr1 identifies a class of ligand-independent nuclear
  receptors.* **Nature** 2003. (NR4A orphan-receptor collapsed pocket; PDB 1OVL. doi:10.1038/nature01645.)
- de Vera IMS, et al. *Defining a Canonical Ligand-Binding Pocket in the Orphan Nuclear Receptor Nurr1.*
  **Structure** 2019. doi:10.1016/j.str.2018.10.002. (Breathing NR4A pocket — arm-1 precedent.)
- Varadi M, et al. *AlphaFold Protein Structure Database.* **Nucleic Acids Res** 2022.
  doi:10.1093/nar/gkab1061. (pLDDT order/disorder for the EWS-LC and NR4A3 LBD.)
- Le Guilloux V, Schmidtke P, Tufféry P. *Fpocket: an open source platform for ligand pocket detection.*
  **BMC Bioinformatics** 2009. doi:10.1186/1471-2105-10-168. (Druggability scoring.)
- Mullican SE, et al. *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute
  myeloid leukemia.* **Nat Med** 2007. doi:10.1038/nm1579. (Wild-type NR4A3 tumour-suppressor liability,
  §1, §7.)
- Safe S, Karki K. *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* **Mol Cancer
  Res** 2021. doi:10.1158/1541-7786.mcr-20-0707. (NR4A3 tumour-suppressor roles, §1, §7.)
- Sjögren H, et al. *EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma.* (EMC biology — shared with
  companion papers; finalise in fact-check log.)
- Panagopoulos I, et al. *Fusion variants/partners in EMC* (incl. TAF15, TCF12, TFG, FUS). (EMC biology —
  shared with companion papers.)
- Bangerter, et al. 2023. *USZ-EMC patient-derived EMC model.* (EMC cell line for §6.)
- Iwata S, et al. *NCC-EMC patient-derived EMC cell lines.* (EMC cell lines for §6.)

**Companion repo documents (not external citations):**
[`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md) (arm-1 LBD warhead / opened pocket),
[`nr4a3-degrader-paper-redteam.md`](./nr4a3-degrader-paper-redteam.md) (honest weight of the 0.931 / Gate
results), [`novel-modalities.md`](./novel-modalities.md) §2 (EWS-LC disorder + LBD druggability),
[`../modalities/andgate_selectivity_model.py`](../modalities/andgate_selectivity_model.py) +
[`../modalities/fusion-andgate-selectivity-model.json`](../modalities/fusion-andgate-selectivity-model.json)
(the §3 CPU avidity model).

*Medical-integrity note: no clinical fact, statistic, citation, or affinity in this draft is fabricated.
The §3 numbers are the real committed output of the CPU avidity model, whose Kd/EM **inputs are illustrative
assumptions** (so flagged in the model, the abstract, §3, §8) — they demonstrate the design principle and
predict no real compound. The opened-pocket arm-1 result is cited at the honest, red-teamed weight (biased-MD
peak, basin-breathing, provisional). No molecule was synthesized and no GPU/AWS run was performed for this
draft. Any reference not in the repo's verified pool is flagged for verification before submission.*
