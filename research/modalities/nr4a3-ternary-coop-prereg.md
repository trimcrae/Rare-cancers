# NR4A3 ternary-cooperativity method — PREREGISTRATION (physics method + calibration + accept/abort)

**Committed BEFORE any ternary GPU spend, per the external reviewer (2026-07-11, "APPROVED WITH SCOPE
CHANGES").** This fixes — a priori, before any favorable number is visible — the physics method, the
thermodynamic definitions, the calibration structures, the retrospective bar, the sequencing, the budget
caps, and the promotion/claim terminology for the **ternary (induced-proximity / degrader-selectivity)**
path of the NR4A3-selective degrader program (EMC / EWSR1::NR4A3). It mirrors the pattern of
[`nr4a3-abfe-repair-prereg.md`](./nr4a3-abfe-repair-prereg.md) (the Track A / ABFE prereg) and is the
ternary analogue of the co-fold's frozen criteria in
[`nrv04-ternary-benchmark.json`](./nrv04-ternary-benchmark.json).

**Scope boundary.** This governs Track B (ternary). It does **not** touch Track A / ABFE / the denovo_401
λ-repair (a separate session owns that). The machine-readable frozen copy of §2–§6 lives in
[`nr4a3-ternary-coop-prereg.json`](./nr4a3-ternary-coop-prereg.json); the gate is enforced by
[`ternary_coop_gate.py`](./ternary_coop_gate.py) so no criterion can be re-decided post-hoc on a favorable
result.

---

## 0. Why a separate physics method (context — what the co-fold cannot do)

The co-fold ternary workflow ([`nrv04_ternary.py`](./nrv04_ternary.py)) **passed its retrospective control
as an ARCHITECTURE-TRIAGE filter only**: it recovers the NR-V04 phenotype at the architecture level (NR4A1
seed-bridged 0.67 vs NR4A2 0.00 / NR4A3 0.00 at 4.5 Å; robust across 4.0/4.5/5.0 Å; survives
leave-one-seed-out), **but the VHL-inactive hydroxyproline epimer PROTAC bridged at 1.00 ≥ active 0.67**
(`descriptive_v3_result`). A geometry classifier that cannot detect a stereochemical affinity knockout has
**zero authority over affinity, cooperativity, or degradation-selectivity ranking.** The two things the
co-fold could not do — (a) recover a *cooperativity ordering* and (b) *reject the inactive epimer* — are
exactly what this physics method must earn the right to do before any prospective NR4A3 ternary ranking is
trusted.

**One scope change the reviewer imposed up front:** an NR-V04-only retrospective is **not** quantitative
validation of a cooperativity method. NR-V04's published evidence establishes VHL-dependent ternary
formation and selective NR4A1 degradation sparing NR4A2/3; it does **not** provide paralogue-resolved
K_d, α, or ΔG_coop. So calibration is **two-layered**: a *quantitative* VHL panel with measured
cooperativity (Layer 1), then NR-V04 as a *family transfer* test (Layer 2, functional-order concordance,
not recovery of measured NR-V04 cooperativity).

---

## 1. The physics method (Q1) — thermodynamic-cycle cooperativity, method (ii) implementing (iii)

**Committed definition.** Cooperativity is a *thermodynamic-cycle* quantity, never a docking/geometry score:

```
ΔG_coop = −RT ln α                    (α = cooperativity factor)
```

estimated through **matched relative alchemical calculations run in both the binary and ternary
environments**, so that shared-scaffold and common-mode terms cancel by construction:

```
ΔΔG_coop  =  ΔΔG_alch,ternary  −  ΔΔG_alch,binary
```

Perturbations are **ligand** (degrader-analogue) morphs, and — *where technically tractable* — staged
protein/interface perturbations to estimate cross-paralogue coupling differences. This is options (ii)
[relative ternary free energy] **implementing** (iii) [cooperativity via a binary-vs-ternary cycle], with
(i) [ternary MD + interface MM-GBSA] **subordinate** (ensemble/diagnostic role only, below). Combined
ligand+protein FEP precedent exists for molecular glues; **its transfer from glues to bifunctional PROTACs
is itself unvalidated here** and is exactly what Layer 1 tests.

### 1a. TWO distinct reported quantities — never collapsed into one score
The final ranking must track, separately (Q4 point 1):
1. **Binary warhead preference** — per receptor (NR4A3 vs NR4A1 vs NR4A2); the RBFE map's job.
2. **E3-ligand affinity integrity** — the recruiter (VH032/VHL) binds as intended; controls, below.
3. **Effective ternary recruitment** — relative ternary affinity / effective recruitment free energy.
4. **Cooperative coupling** — ΔG_coop / relative ΔΔG_coop.

A compound may have favorable cooperativity but inadequate binary affinity (or vice-versa); experimental
PROTAC series show both matter and **no single ternary parameter universally explains degradation**. The
epimer result is the standing proof that #3/#4 must be separated from geometry.

### 1b. Role of all-atom MD — APPROVED, but as ensemble/diagnostic ONLY
MD is approved for: ensemble generation and pose survival; identifying metastable ternary arrangements;
persistent contacts / buried surface / hydration / interface frustration / linker preorganization;
detecting pose- or paralogue-dependent failure modes.

### 1c. Interface MM-GBSA — NOT a ranking endpoint or gate
Trajectory-based interface MM-GBSA is **not authorized** as a ranking endpoint or a gate. A 2025 VHL–SMARCA2
PROTAC study found **no correlation** between trajectory MM-GBSA cooperativity estimates and measured
cooperativity (though ensemble descriptors still carried qualitative information), and showed a single
ternary structure is only part of a broad ensemble. MM-GBSA may appear in the manuscript **only** as a
qualitative descriptor, explicitly labeled non-predictive, never as a number a ranking depends on.

---

## 2. Calibration structure (Q1) — two retrospective layers

### Layer 1 — QUANTITATIVE VHL thermodynamic calibration (required before relying on NR-V04)
A literature VHL panel with *measured* cooperativity. The Ciulli-lab **SMARCA2–VHL** series is the primary
candidate (structurally characterized ternary complexes spanning ~α = 0.2 … 93; multiple linker/exit-vector
arrangements; inactive *cis*-hydroxyproline stereoisomer controls; long MD showing ensemble diversity).

**Minimum panel = six systems**, containing at least:
- **≥2 negatively/weakly cooperative** systems,
- **≥2 strongly cooperative** systems,
- **1 inactive VHL stereochemical control**,
- **preferably MZ1 (or another independent VHL system) as a transfer control** — MZ1 has a solved
  cooperative VHL–BRD4 ternary complex.

> **HONESTY / PROVENANCE FREEZE (Stage-0 blocker).** The exact compound identities, PDB IDs, and *measured*
> α / ΔG_coop values are **NOT asserted in this document** and must **NOT** be fabricated. They are to be
> extracted from primary sources and frozen into `nr4a3-ternary-coop-prereg.json →
> calibration.layer1_vhl_panel.systems` **before the pilot's calibration leg is trusted**, via a CI-runner
> full-text fetch (egress-proxy rule: NCBI/PMC/Springer are blocked in-sandbox → route through a GitHub
> Actions runner). Until each system carries a verified primary reference + a verified measured α, it is a
> `provenance: unverified` placeholder and cannot enter the scored panel. This mirrors the NR-V04
> `chemical_identity` blocker already recorded in the benchmark JSON.

### Layer 2 — NR-V04 family transfer test (functional-order concordance, NOT measured-α recovery)
Then test the four VHL systems:
- NR-V04 – NR4A1, NR-V04 – NR4A2, NR-V04 – NR4A3, and the **inactive hydroxyproline epimer** in each.

Described in the manuscript as **functional-order concordance** — whether the Layer-1-validated physics
*transfers* to the NR4A family — **never** as "recovery of measured NR-V04 cooperativity" (no
paralogue-resolved NR-V04 α exists). Carry forward the standing caveat that the NR-V04 chemistry in-repo is
an **"NR-V04-inspired representative reconstruction"** until primary-source structure verification lands
(`chemical_identity.blocker`).

---

## 3. Minimum retrospective bar — ALL must pass before ANY prospective NR4A3 ternary ranking (Q1)

### 3a. Technical convergence (every free-energy leg)
- **≥3 independent replicas** per free-energy leg.
- **Cycle closure OR forward/reverse hysteresis ≤ 1.0 kcal/mol.**
- **95% CI half-width ≤ 1.5 kcal/mol** for any decision-bearing quantity.
- **≥2 independently generated starting ternary poses** per retained architecture.
- **No rank reversal under leave-one-pose-out.**
- No restraint-coordinate, ligand-mapping, or microstate pathology (semantic checks, per the ABFE prereg §2
  discipline: λ identity/order, endpoint definitions, sample-dedup, target identity).

### 3b. Quantitative VHL panel (Layer 1)
- **Correct favorable/unfavorable cooperativity class for ≥ 5 of 6** systems.
- **Kendall τ ≥ 0.5** for the ordinal ranking vs measured cooperativity.
- **No inactive stereochemical control classified as ternary-competent.**
- Result **survives exclusion of any one calibration compound** (leave-one-compound-out).

### 3c. NR-V04 affinity control (Layer 2, the two things the co-fold failed)
- Active NR-V04 favored over its VHL-inactive epimer by **≥ 3.0 kcal/mol in the binary VHL** calculation,
  uncertainty interval **excluding zero**.
- Active favored by **≥ 2.0 kcal/mol in effective ternary recruitment**.
- **No retained pose reverses** the active/epimer ordering.

### 3d. NR4A family transfer (Layer 2)
- **NR4A1 outranks both NR4A2 and NR4A3** in effective ternary recruitment.
- Each difference **≥ 1.0 kcal/mol**, with a **90% interval excluding zero**.
- **Joint P(NR4A1 is best) > 0.90.**
- Ordering **survives starting-pose and conformer-panel sensitivity** analyses.

### 3e. Honest failure semantics (pre-committed)
Failure of §3d does **not** prove the ternary-first biological thesis false — NR-V04's degradation
selectivity could arise partly *downstream* at ubiquitination. It **does** mean the computational
cooperativity method is **not validated for prospective NR4A paralogue ranking** and must not be used as
manuscript authority for a selectivity claim. (Symmetric to the ABFE prereg's "one replicate cannot
establish an artifact" discipline: the bar is falsifiable and pre-set, not tuned to the outcome.)

---

## 4. Sequencing (Q2) — parallel pilots, staged fleet release

**Stage 0 — now, free (this document + its JSON + construct freeze).** Freeze: the §1 thermodynamic
definitions; the §2 calibration compounds/structures/microstates; force fields; restraints; the uncertainty
estimator; the §3 failure criteria; the **construct definitions** (§4a below); and **how binary and ternary
terms combine** (§4b — no weights invented after results are visible).

**Stage 1 — run BOTH pilots in parallel (authorized, §5).**
- **Binary pilot:** the existing `5-Br → 5-NH₂` RBFE edge (`e_zaienne_cmpd19__cw_ev_5nh2`) on one
  `nr4a3_design` frame — the most well-behaved perturbation, isolating "can a congeneric RBFE converge on
  this dynamic cryptic pocket" (per the RBFE-map plan §"pilot edge").
- **Ternary feasibility pilot:** the fixed bundle in §5b.

**Stage 2 — SECOND authorization (not automatic).** If the binary pilot passes its pre-registered abort
criteria, authorize a **selection-oriented RBFE tranche** — *not* the full 19-compound combinatorial fleet:
anchor-rooted exit-vector series; the most defensible SAR-preserving analogues; required microstate legs;
NR4A1/2/3; only conformers that survive the pre-registered pocket/pose gates. **Capped** at what is needed
to identify ~2–3 warhead/exit-vector hypotheses. The carboxylate bioisosteres that can change pose stay a
**separate pose-revalidation tranche** (not wired into the common-mode network just to inflate compound
count).

**Stage 3 — ternary prospective release.** Prospective NR4A3 ternary calculations begin **only after** the
quantitative VHL panel (§3b), the epimer control (§3c), and the NR-V04 family-transfer gates (§3d) pass.

**Stage 4 — the matrix.** Build the degrader matrix only when: 2–3 warheads survive binary RBFE; their
attachment poses remain credible; the ternary method is validated; and ≥2 exit-vector architectures survive
co-fold + ensemble checks.

### 4a. Construct definitions (frozen at Stage 0)
- **NR4A ligand-binding domains:** each paralogue's LBD = its **C-terminal 254 residues** (NR4A3 kept
  explicit at **373–626** for exact reproducibility; NR4A1/NR4A2 defined identically), matching
  `nr4a3_ternary.py` / `nrv04_ternary.py`. Binary RBFE uses the frozen `nr4a3-conformer-panel.json`
  receptor-state axis (druggable 8XTT validation conformers + release held-out ranks 4–6 + matched
  NR4A1/NR4A2 open frames).
- **E3 (Layer 2 / flagship):** **VHL + Elongin B/C**, recruiter **VH032** (structure-verified,
  `control_ligand` in the benchmark JSON).
- **Fusion context (ubiquitination stage only, §6 point 4):** the **EWSR1::NR4A3** breakpoint + domain
  context is defined and modeled **separately** from the isolated LBD (declared disordered-domain
  uncertainty); the LBD-local ternary energetics and the fusion-context ubiquitination geometry are
  **reported as separate quantities**, never silently merged.

### 4b. Binary↔ternary combination rule (frozen at Stage 0 — no post-hoc weights)
The ranking objective is the strategy doc's `S_d` skeleton with **weights and the exact functional form
frozen HERE, before results**:
```
S_d = min_c [ w_t·(effective ternary recruitment, NR4A3 − worst paralogue)_c
              + w_c·(ΔG_coop, NR4A3 − worst paralogue)_c ]
      − λ·SD_c
      − γ·max(NR4A1/NR4A2 counterexample)
      − η·linker_strain
      − ρ·ubiquitination_incompatibility
```
Effective ternary recruitment (#3) and cooperative coupling (#4) enter as **separate terms** (never summed
into one pre-collapsed score); binary preference (#1) and E3-ligand integrity (#2) are **eligibility gates**
upstream of `S_d`, not addends. Numerical weights (`w_t, w_c, λ, γ, η, ρ`) are registered in the JSON as
frozen constants; any change is a dated amendment to this prereg, not a silent retune.

---

## 5. Budget (Q3) — both pilots authorized; NO full fleet

### 5a. Binary RBFE pilot — AUTHORIZED (~$5–15)
The `5-Br → 5-NH₂` edge on one design frame. **Passing it authorizes only the *preparation* of a
right-sized Stage-2 proposal — it does NOT release the full fleet.** Abort criteria are the RBFE-map plan's
pre-registered set (hysteresis ≤ 0.5 kcal/mol/leg; min adjacent-λ MBAR overlap ≥ 0.03; cycle closure
≤ 1.0 kcal/mol; Pocket-5 survival ≥ 50% of windows).

### 5b. Ternary-control feasibility pilot — AUTHORIZED WITH A HARD $200 CAP
Fixed scope, **exactly**:
1. **One high-vs-low cooperativity VHL calibration comparison** (preferably a structurally characterized
   pair from the SMARCA2 series).
2. **Active NR-V04 vs inactive epimer in binary VHL.**
3. **Active NR-V04 vs inactive epimer in the NR4A1 ternary architecture.**
4. **≥3 independent replicas and a minimally adequate λ schedule** — *not* single-trajectory endpoint
   scoring.

**Not-to-exceed AWS spot spend: $200.** **Before production, generate a dry-run GPU-hour forecast**
(`MODE=plan`, one-leg-first). **If the defined pilot cannot fit under $200 without compromising replica
count or convergence diagnostics → STOP before production and return a revised costed scope** (do not
silently drop replicas to fit the cap). Spot-only; pilot-one-leg-first; wait out spot capacity; checkpoint
continuously (standing rules).

### 5c. Full fleets — NOT AUTHORIZED (held for the second decision)
Held: the exhaustive binary congeneric fleet; the complete NR-V04 retrospective fleet; all prospective
ternary matrix calculations; **all CRBN calculations**. The second decision compares **observed cost per
converged leg, failure rate, CI width, checkpoint recovery, and actual conformer survival** — not nominal
trajectory count.

### 5d. Separate CRBN gate
NR-V04 validates **VHL recruitment only** — it cannot validate CRBN architecture, thermodynamics,
glutarimide chemistry, or CRL4 geometry. Therefore: the flagship matrix is **VHL-first**; CRBN constructs
may be **chemically enumerated** but must **not** enter the flagship ranked set until a **CRBN-specific
positive/negative calibration + affinity control** is run and passes. A VHL-only 6–12-compound package is
more defensible than doubling E3 breadth.

---

## 6. Architecture sufficiency (Q4) — the core is right but four layers are added

"Co-fold architecture triage + a separate physics cooperativity method" is **necessary but not sufficient.**
Four additional layers are **required**:

**1. Separate ternary affinity from cooperativity** — the four tracked quantities of §1a; ranking is never
on α alone. (The epimer result is why.)

**2. Explicit ensemble + linker-strain treatment** — for every serious construct: multiple co-fold
architectures; multiple binary receptor conformers; independent ternary MD replicas; cluster populations +
pose exchange; **linker strain relative to its unbound conformational ensemble** (reported as a **separate
penalty/diagnostic**, *not* assumed captured by an endpoint interface energy); PROTAC intramolecular
contacts / folded-state populations; sensitivity to protonation, tautomer, and charge assignment. Single-
pose analysis is not an adequate ranking basis.

**3. Explicit Cullin–RING + ubiquitination-compatibility stage (on finalists)** — model an ensemble of
VHL–EloBC + **neddylated CUL2–RBX1** + a relevant **E2~Ub** catalytic complex + the ternary target
orientation. Score: solvent-exposed target lysines; Lys→E2~Ub transfer geometry; **fraction of frames with
≥1 transfer-competent lysine**; persistence across CRL conformations; **differences among NR4A1/2/3**;
whether a candidate presents **multiple** lysines vs one fragile solution. **Cheap geometric screening on
all survivors; full CRL MD only for the top ~3–5.** No claim that any distance cutoff quantitatively
predicts degradation. (Ternary formation is necessary, not sufficient, for degradation.)

**4. Fusion-relevant target context** — the ubiquitination stage must not rely solely on the isolated NR4A3
LBD. Define + model the EWSR1::NR4A3 breakpoint/domain context (fusion may alter domain orientation /
accessible lysines / presented surface; EWSR1 disordered regions may supply lysines). Where a full fusion
ensemble is too uncertain, report **separately**: LBD-local ternary energetics; fusion-context
ubiquitination geometry; and a **declared uncertainty** from disordered-domain modeling.

### 6a. Additional required controls (all pre-committed)
- Warhead-only binary complexes.
- E3-ligand-only controls.
- Inactive E3 epimer (the affinity-knockout control).
- **≥1 linker-matched non-productive architecture** (a designed negative).
- Force-field / charge-model sensitivity on finalists.
- **Blinded control labels through completion of the retrospective scoring** (analyst does not know
  active/epimer/paralogue identity until scoring is locked).
- **Identical analysis + stopping rules for NR4A1/2/3** (no paralogue gets bespoke treatment).
- Ternary residence-time calculations are **optional secondary** evidence, **never a primary gate**
  (half-life↔degradation-rate relationships differ across experimental PROTAC series).

---

## 7. Promotion + manuscript-claim terminology (what this evidence can and cannot buy)

**Permitted ceiling (only when §3 fully passes AND the prospective matrix is built):**
> *"NR4A3-selective degrader designs computationally **prioritized** by calibrated binary, ternary, and
> ubiquitination-geometry analyses."*

**NOT permitted from any amount of this evidence:**
- "validated NR4A3-selective degraders";
- any **quantitative degradation prediction**;
- promoting denovo_401 (or any warhead) to "lead" — the ABFE prereg ceiling ("computational warhead
  candidate / priority synthesis candidate") stands; ternary competence does not upgrade it to "lead"
  without experimental engagement.

**Standing honesty carry-overs:** co-fold stays architecture-triage-only; NR4A2 is the primary anti-target
gate, NR4A1 provisional/unresolved; the NR-V04 chemistry is a "representative reconstruction" until
primary-source verified; interface MM-GBSA is descriptive-only.

---

## 8. Final approved dependency chain (reviewer, 2026-07-11)

1. Co-fold architecture: **passed; remains triage-only.**
2. Binary RBFE pilot: **authorized** (§5a).
3. Ternary alchemical feasibility pilot: **authorized under the $200 cap** (§5b).
4. Quantitative VHL calibration panel: **required before prospective use** (§2 L1, §3b).
5. NR-V04 epimer + paralogue transfer: **required before prospective NR4A ranking** (§2 L2, §3c/§3d).
6. Selection-oriented binary RBFE tranche: **conditionally releasable after the binary pilot** (§4 Stage 2).
7. VHL-only prospective degrader matrix: **after both binary and ternary gates** (§4 Stage 4).
8. Full CRL2–E2~Ub lysine-presentation analysis: **required on finalists** (§6 point 3).
9. CRBN branch: **held pending independent CRBN validation** (§5d).
10. Manuscript claim: **"prioritized by calibrated … analyses," never "validated … degraders"** (§7).

---
**Decision (reviewer, 2026-07-11):** APPROVED WITH SCOPE CHANGES. Both pilots authorized now; neither full
fleet authorized. Freeze §1–§6 before spending; NR-V04 is a family transfer test, not the sole thermodynamic
calibration; separate ternary affinity from cooperativity; add ensemble/linker-strain, Cullin–RING/E2~Ub
lysine-presentation, and fusion-context layers; VHL-first, CRBN held.
