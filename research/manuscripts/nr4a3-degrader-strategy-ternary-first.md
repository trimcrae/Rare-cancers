# NR4A3 degrader — strategy redirection: ternary-selectivity-first, chemotype-anchored

> **⚠️ EXECUTION-PLAN SUPERSEDED 2026-07-15 (external reviewer-AI verdict — conditional approval + 5 mandatory
> changes).** The *thesis* below stands unchanged (selectivity from binary × ternary × ubiquitination geometry),
> but the naive **three-step spine** (RBFE → NR-V04 → prospective) is replaced by a **3-kinds-of-validation
> architecture** with a fixed ordered plan. **For WHAT WE RUN AND IN WHAT ORDER, read
> [STRATEGY.md](./STRATEGY.md)** (the master ordered plan) and
> [nr4a3-degrader-reviewer-revisions-2026-07-15.md](./nr4a3-degrader-reviewer-revisions-2026-07-15.md) (the
> verbatim verdict). Key deltas: add a **public measured-ΔΔG accuracy benchmark** + a **known-answer ternary
> benchmark (VHL–BRD4/SMARCA2)**; treat cmpd19 RBFE as **conditional hypotheses** (no pose); affinities are
> **conditional on the open state** (ΔG_open enters selectivity); **ABFE is HELD/reframed** (no transferable
> T4L offset; does not prove "binds at all"); **NR-V04 celastrol is covalent (C551)** → covalent controls;
> prospective matrix = **staged gates + Pareto**, modeling **EWSR1::NR4A3 in fusion context**. §§ below are
> retained for their (still-valid) biological + chemotype rationale.

**Status: ADOPTED 2026-07-11 (external reviewer-AI recommendation, relayed by trimcrae; reconciled with the
existing Track B primacy in CLAUDE.md).** This note is the authoritative capture of the redirection so it is
not re-litigated. It **supersedes the binary-warhead-first de novo funnel** as the program's flagship. It does
**not** change the modality (still degradation) or the biological rationale (NR4A3-fusion EMC).

## The one-sentence change

Old flagship: *"a computationally selective NR4A3 warhead (denovo_401)."*
New flagship: **"a synthesis-ready, experimentally-anchored degrader MATRIX (~6–12 sharply differentiated
compounds) that obtains selectivity JOINTLY from a modest binary NR4A3 preference, paralogue-specific ternary
cooperativity, and ubiquitination-compatible geometry."**

This is the Track B hypothesis (selectivity from warhead × linker × E3 × ternary-interface geometry even when
binary selectivity is incomplete) made concrete, with the discovery funnel inverted away from de novo.

## Why (grounded in the repo's OWN negative findings — this uses them, it doesn't repair the same funnel)

- The useful orthosteric state is a **low-population, conformationally-variable cryptic pocket** (score-independent
  audit finds the site in 95–100% of frames, but only **3/20 experimental 8XTT NMR conformers are druggably
  open** — and 8XTT is a deposited low-energy ensemble, **NOT** an equilibrium population, so 3/20 is *not* a
  15% solution-state occupancy).
- The **conserved pocket core rewards larger/tighter compounds**, and the repo's larger-molecule de novo
  campaigns drifted toward **pan-NR4A**, not NR4A3-selective.
- NR4A2 offers **only ~4 engageable divergent residues** — thin ground for binary selectivity.
- **Cheap methods cannot rank NR4A paralogue chemistry** (Gate-2: docking + multi-snapshot MM-GBSA do not
  reproduce known preferences; single-snapshot MM-GBSA called 39% of unrelated marketed drugs "NR4A3-selective";
  generated compounds were not enriched over that null).
- **denovo_401 is a benchmark + chemical hypothesis, not a lead**: clears its design-frame decoy null but not a
  different opened NR4A3 frame; receptor-provenance moved ABFE by ~4.7 kcal/mol, **larger than the claimed
  selectivity margin**.
- **Co-fold cannot rank affinity/cooperativity**: the VHL-inactive hydroxyproline **epimer** bridged in
  essentially the same geometry as the active NR-V04 construct. A co-fold predicts *structure*, not
  thermodynamic competence.

Conclusion: **do not require the binary pocket to solve the whole selectivity problem.** Demand only a modest,
robust binary preference and let the ternary + geometry supply the rest.

## The revised program

### 1. Warhead source: congeneric campaign, NOT de novo
Anchor on the **Zaienne 2022 NOR-1/NR4A3 series — principally compound 19, methyl 5-bromoindole-3-carboxylate**
(`zaienne_cmpd19`; SMRT IC50 9±2 µM, NCoR1 12±3 µM; PMID 35704774; evidence class *functional_target_
engagement*, i.e. **experimentally anchored but NOT a structurally proven binder** — the exit-vector hypothesis
must not be over-claimed as a known pose). Enumerate a focused set:
- 5-position substitutions giving chemically distinct **linker attachment vectors**;
- indole-carboxylate replacements that **preserve the measured SAR**;
- **neutral / weakly-ionizable** analogues with unambiguous microstates;
- a few **denovo_401 analogues retained only as a comparator series**.
Goal is not a nM NR4A3-only binder — a **reproducible 1–3 kcal/mol ensemble preference** suffices if the ternary
supplies the rest.

### 2. Primary quantitative tool: RBFE within the congeneric series (ABFE demoted to secondary calibration)
Congeneric **relative** binding free energies are a far more tractable question than absolute binding of
unrelated generated scaffolds. Run each perturbation across: the prespecified druggable 8XTT validation
conformers; independent release-derived NR4A3 conformers; **structurally matched NR4A1 + NR4A2 open conformers**;
and resolved **stereoisomers / tautomers / protonation states**. Rank by the **worst conformer** and by whether
the **receptor effect exceeds the conformer effect** (the ensemble-robust redesign's existing standards —
`ensemble_robust_score.py`, the conformer panels — are endorsed and reused).

### 3. Ternary is the CENTRAL selectivity variable (not just triage)
Once 2–3 modestly NR4A3-favoured warheads survive, build an explicit **matrix**: {2–3 warheads} × {2 exit
vectors} × {VHL, CRBN} × {short/medium/constrained linkers}. **VHL is prioritized** because **NR-V04** proves
family-selective NR4A degradation is achievable (celastrol-warhead × VHL degrades NR4A1, spares NR4A2/NR4A3) —
an *anchored* starting geometry, though it does **not** show the same geometry works in reverse for NR4A3.
Per construct, compute SEPARATE quantities: binary warhead affinity (×3 receptors); binary recruiter affinity;
**physics-based ternary cooperativity / relative ternary stability**; ternary conformational heterogeneity;
target–E3 interface contacts; linker strain / effective concentration; target-Lys accessibility; and
compatibility with the larger Cullin–RING/E2~Ub assembly. **The co-fold stays an early ARCHITECTURE filter with
no authority to rank affinity, cooperativity, or degradation selectivity** (the epimer control forbids it).

### 4. Paralogue-specific ternary objective
**[SUPERSEDED as the selection method 2026-07-15 — see the top banner + [`/STRATEGY.md`](../../STRATEGY.md)
mandate 5: use staged gates → Pareto front, NOT this scalar. The `S_d` below is retained only to show the axes,
which become the Pareto dimensions.]**
Rank degraders on a ternary-selectivity-centered score (conceptually):
`S_d = min_c ΔG_ternary-selectivity,c − λ·SD_c − γ·max(NR4A1/2 counterexample) − η·linker_strain −
ρ·ubiquitination_incompatibility`. The central variable is **ternary** selectivity, not binary-warhead
selectivity. A moderately-selective warhead forming a cooperative, ubiquitination-compatible NR4A3 ternary can
beat a nominally-selective warhead whose ternary geometry is pan-NR4A — the underused advantage of
induced-proximity pharmacology.

### 5. Deliverable: a synthesis-ready matrix, not another in-silico "lead"
~6–12 sharply differentiated compounds with built-in controls: active + inactive recruiter stereoisomers;
linker-length-matched pairs; ≥2 exit vectors; VHL + CRBN representatives; one **pan-NR4A predicted control**;
one **binary-favoured-but-ternary-unfavoured control**. Far more collaborator-actionable than a single generated
ligand with an uncertain pose and a large conditional ABFE margin.

## Gate that still governs everything (unchanged; NR-V04 REFRAMED per reviewer 2026-07-13)
Before ANY prospective ternary ranking is trusted, the ternary workflow must pass the **retrospective, blinded
NR-V04 control**. **CRITICAL CORRECTION (reviewer-AI, 2026-07-13):** NR-V04 has **NO experimentally-determined
NR4A1–NR-V04–VHL ternary structure** — the Wang 2024 paper establishes selective NR4A1 degradation
(sparing NR4A2/3), VHL/proteasome dependence, and ternary formation **functionally / by proximity (PLA + co-IP)**,
with the NR4A1 ligand designed by docking. So NR-V04 is **NOT** a "reproduce the known ternary architecture"
structural test, and it must **NOT** be described as *architecture concordance*. It is an **END-TO-END FUNCTIONAL
retrospective gate**: whether the generated NR4A1/NR4A2/NR4A3 ensembles, passed **unchanged** through the physics +
ubiquitination pipeline, recover the known **NR4A1-degraded / NR4A2·NR4A3-spared** outcome (with the VHL-inactive
hydroxyproline epimer as a negative *functional* control — generators are explicitly **allowed** to give the epimer
a similar geometry; demanding geometric discrimination would repeat the original co-fold category error).
Boltz↔DeepTernary agreement on NR-V04 would be **inter-model agreement, not structural validation**. Prospective
affinity/selectivity inference stays prohibited until the RBFE + physics-based ternary tools — not any
generator — support it. Full qualification protocol:
[research/modalities/deepternary-qualification-protocol.md](../modalities/deepternary-qualification-protocol.md).

## ⏸ DEFERRED DECISION — selectivity TARGET: NR4A3-selective (Level 1, current) vs EWSR1::NR4A3-FUSION-exclusive (Level 2) [trimcrae, 2026-07-13]
**Do NOT decide now; decide at the post-NR-V04-validation / pre-prospective-design gate. This section exists so
we have every input ready when it becomes relevant. Do not let it block the current validation work.**

**The question.** This program is currently framed **Level 1 = NR4A3-selective** (degrade NR4A3, spare NR4A1/2).
But the NR4A3 **LBD is IDENTICAL in the fusion and in wild-type NR4A3**, so an LBD-recruiting degrader also
removes **wild-type NR4A3**. Before committing prospective design, revisit whether to aim instead for
**Level 2 = fusion-exclusive** (spare wild-type NR4A3 too, and ideally NR4A1/2). **Tightening levels**
(corrected 2026-07-13 per reviewer — note the tractable INTERMEDIATE):
tumour-vs-normal (weak) → **NR4A3-selective (Level 1, current — co-degrades WT NR4A3)** →
**fusion-PREFERENTIAL (Level 1.5 — a *single-arm* LBD–E3 degrader that removes the fusion MORE than WT NR4A3
because the EWSR1 appendage changes the ternary interface, lysine presentation, localization + ubiquitination
geometry; NOT a guaranteed molecular gate, but reachable WITHIN the current ternary program with no new ligand)**
→ **fusion-EXCLUSIVE (Level 2, the prize — a hard molecular AND-gate; blocked at second-arm ligand validation)**
(cf. [`fusion-selective-approaches-overview.md`](./fusion-selective-approaches-overview.md)).

**Why Level 2 could matter.** Wild-type NR4A3 is **tumour-suppressive** (combined NR4A1/NR4A3 loss is
leukaemogenic — Mullican 2007; tumour-suppressor roles in HCC/breast/lymphoma — Safe & Karki 2021), so
systemic co-degradation of WT NR4A3 is an **on-target liability**. Level 2 removes it → lowest-toxicity,
truly tumour-specific.

**Why Level 2 is harder (the crux) — CORRECTED 2026-07-13 (reviewer).** Binary LBD binding **cannot** distinguish
fusion from WT (identical LBD) — the *same wall* as paralogue selectivity. **KEY CORRECTION: the EWSR1
low-complexity (LC/IDR) domain is NOT itself fusion-restricted — wild-type EWSR1 also carries it.** What is
fusion-specific is the **covalent adjacency *in cis*** of EWSR1-LC to the NR4A3-LBD on one polypeptide
(`EWSR1-LC :: NR4A3-LBD`). So an EWSR1-LC binder *alone* would also grab normal EWSR1; fusion specificity can
only come from **requiring both features in cis**. Hard fusion-exclusivity therefore needs a **trivalent
degrader — NR4A3-LBD arm + EWSR1/junction arm + E3 recruiter** — each target-arm deliberately too weak alone, so
avidity engages only the chain presenting both (precedent for two-sites-on-one-protein selectivity exists, but
with *structured tandem domains*, not an IDR).
- **The gate, stated narrowly:** **no validated, selective, cell-active, chemically-tractable ligand is currently
  established for the retained EWSR1-LC segment (or the junction) suitable as a second degrader arm.** (YK-4-279 /
  TK216 bind *recombinant* EWS::FLI1 and perturb its RNA-helicase-A interaction, but that does **not** establish a
  transferable EWSR1-LC ligand, an LC epitope, or a qualified arm for EWSR1::NR4A3.) A cleaner-uniqueness second
  arm could instead target the **exact fusion junction**, a **fusion-created neo-interface**, an **EWSR1-LC
  conformation/condensate state**, or a **fusion-specific partner complex** — the junction gives the cleanest
  molecular uniqueness, though breakpoint variation + disorder make it hard.
- **Extra AND-gate failure mode (must be qualified):** even with two arms, the molecule could bind **WT NR4A3 and
  WT EWSR1 as two separate proteins *in trans*** (especially inside transcriptional condensates), faking fusion
  specificity. Qualification must demonstrate **K_eff(cis fusion) ≫ K_eff(WT NR4A3 + WT EWSR1 in trans)** via
  linker reach, effective molarity, and geometric constraints.
- Feasibility analysis (avidity model, ~5–11× *binding* window, binding≠degradation):
  [`fusion-selective-andgate-degrader-paper.md`](./fusion-selective-andgate-degrader-paper.md) (note: that paper's
  "arm-2 target = fusion-restricted" wording is corrected by the *cis-adjacency* point above).

**Key reassurance — Level 1 now does NOT foreclose Level 2.** The current warhead + ternary work **IS the
foundation of the AND-gate's arm 1** (an NR4A3-LBD ternary binder + the validated ternary method transfer
directly). So this is a decision about whether to **add a fusion-restricted second layer later**, not a fork
that wastes current effort. Proceeding Level 1 is the shared prerequisite for either endpoint.

**Information ALREADY IN HAND (cross-refs — read these at the gate):**
- Three-level framework + 5-route fusion-exclusive comparison (ranked by likelihood-of-working; leads with the
  ASO) → [`fusion-selective-approaches-overview.md`](./fusion-selective-approaches-overview.md).
- AND-gate degrader feasibility + its blocking gate (arm-2 IDR ligand) →
  [`fusion-selective-andgate-degrader-paper.md`](./fusion-selective-andgate-degrader-paper.md).
- The **sequence-clean** fusion-exclusive alternative *modality* (junction ASO/siRNA — fusion-exclusive by
  base-pairing, spares WT NR4A3; gated on tumour **delivery**, not biology) →
  [`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md).
- WT-NR4A3 tumour-suppressor liability citations: Mullican 2007; Safe & Karki 2021.

**Information STILL NEEDED before deciding (assemble at the gate):**
1. **QUANTIFY the WT-co-degradation liability (the pivotal input).** Normal-tissue NR4A3 expression +
   therapeutic-window estimate; tolerability of **single-gene** NR4A3 loss (single-KO phenotype vs the
   *combined*-loss leukaemogenesis, which may not apply to NR4A3-only depletion); whether tumour-localized /
   transient / incomplete degradation mitigates it. **If WT co-degradation is tolerable → Level 1 suffices and
   Level 2's extra difficulty isn't worth it. If it is toxic → Level 2 is justified.** This input decides it.
2. **Does the fusion retain a near-intact LBD across the relevant breakpoint variants?** (Common type: yes.
   Confirm variant coverage — a variant that truncates the LBD would make an LBD-degrader miss the fusion
   entirely, independently arguing against the LBD-degrader for those patients.)
3. **Arm-2 handle status (method-watch trigger).** Has any EWS-LC / condensate-partitioning / IDR-contacting
   ligand emerged? Currently none → a Level-2 *degrader* is **not yet buildable**; this gates feasibility.
4. **Modality comparison for the fusion-exclusive goal.** If WT-sparing turns out essential, weigh the AND-gate
   degrader vs the **junction ASO** (fusion-exclusive by sequence, delivery-gated) vs neoantigen — do NOT assume
   the degrader is the vehicle for Level 2. The ASO may be the better fusion-exclusive route.
5. **Transfer check.** Quantify how much of the validated ternary workflow + warhead carries into the AND-gate's
   arm 1 (expected: most) — this sets the true marginal cost of Level 2.

**Default if unresolved at the gate:** proceed with the Level-1 warhead/ternary work (shared foundation), keep
Level 2 open, and let inputs #1 (WT-loss tolerability) and #3 (arm-2 handle existence) drive the call.

**Recommended framing (reviewer 2026-07-13) — keep TWO separate programs, don't conflate:**
- **Current, tractable:** LBD–E3 degraders seeking **EWSR1::NR4A3-PREFERENTIAL** (Level 1.5), *not* fusion-exclusive,
  degradation via ternary + ubiquitination geometry — reachable now, and a natural extension of the current ternary
  workflow (model the fusion `EWSR1-LC::NR4A3-LBD` vs WT-NR4A3 ternary; no new ligand required). This upgrades the
  honest ceiling of the current program from "NR4A3-selective (co-degrades WT)" toward "fusion-preferential" — to be
  *tested*, not assumed.
- **Future, fusion-exclusive:** discover + validate an **EWSR1/junction second-arm ligand**, then build a
  coincidence-gated **trivalent** degrader. For a computational-only program this is **presently BLOCKED at ligand
  validation** → present it as a **research hypothesis, NOT among synthesis-ready degrader claims.**

**Canonical statement to reuse (do not drift from this):** *Binary NR4A3-LBD binding cannot distinguish
EWSR1::NR4A3 from wild-type NR4A3. Ternary geometry might still produce fusion-PREFERENTIAL degradation, but hard
fusion-EXCLUSIVE recognition would require a second cis-recognition event directed at the EWSR1 segment, the fusion
junction, or another fusion-specific feature. No suitably validated second-arm ligand is currently available.*

## Explicitly de-prioritized (reviewer + repo agree)
- Broad additional **de novo pocket generation** (demonstrated failure modes: unstable chemistry, winner's-curse
  selection, frame conditioning, pan-NR4A drift).
- **Generic ML degrader-activity prediction** (target-unseen AUROC ~0.60–0.65 with high seed variance; Dmax far
  less predictable than potency) — may triage E3 choice, not decide the campaign.
- **AF-2/H12 molecular-glue** discovery (cavity transient + more conserved across paralogues → poorer NR4A3
  selectivity handle).
- **Fusion-junction small-molecule degrader** design (no experimentally-anchored pocket; adds structural
  uncertainty).

## ★★ TRACK A SHELVED — GO TRACK B (trimcrae, 2026-07-15)
The de novo warhead / **ABFE-validation track is SHELVED** (parked, revisit-when-warranted — not deleted). The
program is now this ternary workflow, expressed as trimcrae's **three-step spine**:
1. **FEP converges on the known literature NR4A3 molecule** — congeneric **RBFE** on Zaienne cmpd19 (§2 above;
   RBFE not ABFE; "converges" = reproducible *relative* ΔG on modeled druggable conformers — cmpd19 has no
   solved pose, so this is NOT matching a crystal structure). *(RBFE KEPT as the warhead input, trimcrae
   2026-07-15.)*
2. **Replicate the patented NR4A1 degrader's selectivity in-silico** — the retrospective **NR-V04** functional
   control (the gate; §"Gate that still governs everything"). NOT a known-architecture match (Wang 2024 has no
   solved ternary).
3. **Design + ternary-test degraders on the cmpd19 anchor — a selective hit is the win** (§§3–5; only after the
   NR-V04 gate passes).
Steps 1 and 2 run in parallel; step 3 gates on both. Canonical calendar:
[degrader-paper-schedule.json](./degrader-paper-schedule.json). **denovo_401 → side comparator only.** The
shelved ABFE (λ-repair, replicates, T4L benchmark) is retained in that file's `shelved` block.

## What carries over unchanged
Ensemble-robust redesign machinery (worst-conformer objective, conformer panels, receptor>conformer criterion);
the published-warhead registry (the anchored chemistry + honest evidence classes); the retrospective NR-V04
ternary workflow + its honest limitations; the atlas as support infrastructure. **(Updated 2026-07-15: the
denovo_401 ABFE is no longer "running as a benchmark" — Track A is shelved; denovo_401 is at most a side
comparator series within the congeneric RBFE.)**
