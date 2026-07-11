# NR4A3 degrader — strategy redirection: ternary-selectivity-first, chemotype-anchored

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

## Gate that still governs everything (unchanged, and the reviewer agrees)
Before ANY prospective ternary ranking is trusted, the ternary workflow must pass the **retrospective, blinded
NR-V04 control** (recover the known NR4A1-selective / NR4A2·NR4A3-spared outcome as *architecture concordance*,
honestly caveated as descriptive-only). That validation is what the in-flight `nrv04-smoke-restart` work
finishes. Prospective affinity/selectivity inference stays prohibited until the RBFE + physics-based ternary
tools — not the co-fold — support it.

## Explicitly de-prioritized (reviewer + repo agree)
- Broad additional **de novo pocket generation** (demonstrated failure modes: unstable chemistry, winner's-curse
  selection, frame conditioning, pan-NR4A drift).
- **Generic ML degrader-activity prediction** (target-unseen AUROC ~0.60–0.65 with high seed variance; Dmax far
  less predictable than potency) — may triage E3 choice, not decide the campaign.
- **AF-2/H12 molecular-glue** discovery (cavity transient + more conserved across paralogues → poorer NR4A3
  selectivity handle).
- **Fusion-junction small-molecule degrader** design (no experimentally-anchored pocket; adds structural
  uncertainty).

## What carries over unchanged
Ensemble-robust redesign machinery (worst-conformer objective, conformer panels, receptor>conformer criterion);
the published-warhead registry (the anchored chemistry + honest evidence classes); the retrospective NR-V04
ternary workflow + its honest limitations; the running denovo_401 ABFE (finishes as a **benchmark/methodology**
data point, not a lead); the atlas as support infrastructure.
