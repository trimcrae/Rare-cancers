# Revision of the ternary-selectivity strategy — 2026-07-24

> **Scope.** A review of how [nr4a3-program-map.md](nr4a3-program-map.md)'s prospective stage goes about *finding a
> paralogue-selective ternary*, with changes aimed at two things only: **making a good selective candidate more
> likely to be found**, and **making the search cheaper**. Nothing here loosens the reviewer's five validation
> requirements or the language discipline — two of the changes tighten them.
>
> **Status:** proposal + the free evidence that motivates it. Everything cited below is computed and committed;
> the GPU consequences are presented at their gates and wait for an explicit go, per the spending rules.

---

## The one-paragraph verdict

The plan's prospective stage is well-engineered but it is betting the headline result on the **single hardest
axis**: it tries to create paralogue selectivity out of a favourable-vs-frustrated induced target–E3 interface,
i.e. out of a free-energy margin. Two numbers, both computed below, say that bet is worse than it looks —
a useful degradation window needs **~2.0 kcal/mol** of *true* interface margin, while the best-case *resolvable*
difference at the prereg's own error model is **1.12 kcal/mol** and the method's accuracy is **~1.7 kcal/mol
RMSE**. Meanwhile two **categorical** selectivity axes — where NR4A1/NR4A2 are structurally *incapable*, not
merely disfavoured — sit unexploited in data the repo already owned: NR4A3 carries **cysteines and lysines that
both paralogues lack**, now verified from full-length UniProt sequences with two independent aligners. At *zero*
thermodynamic margin those axes deliver 0.82–0.92 on the same window metric where the interface-only null gives
0.185. The revision is therefore: **search the categorical axes first, use the ternary machinery to do what it
is actually good at (confirming geometry and ubiquitination competence), and stop asking it to win a contest at
the edge of its own resolution.** Six cost levers, each evidence-backed, cut the priceable ladder substantially and make the leading gates free.
**⚠ The headline total this review originally carried is WITHDRAWN** — a same-afternoon measurement on the
real system showed the per-edge bases under it were ~3× low; see the boxed correction in §5. The levers are ratios and survive; the
absolute number does not.

---

## 1. Diagnosis — the plan asks for an effect smaller than the tool's resolution

### 1.1 What the plan currently does

nr4a3-program-map.md's orientation-first ladder is:

```
paralogue surface differences → selective interface BASINS → productive CRL geometry
    → linker requirements → candidate molecules
```

Every selectivity claim in that chain is a **difference of free energies between paralogues**. The kill-switch
(5a-KS) is a mutation cycle producing a ΔΔG. The prospective ranking (5c/5d) is a ΔΔG_coop comparison. The
thesis paragraph even concedes the problem: *"There is no validated prospective selectivity predictor in the
field"*, and *"in every landmark case it was discovered then rationalized by a solved ternary structure — never
predicted blind."*

### 1.2 How big does the margin have to be?

[`selectivity_margin_model.py`](../modalities/selectivity_margin_model.py) (+ 19 unit tests) answers this with a
cooperative 1:1:1 ternary equilibrium feeding a steady-state degradation balance. Two design choices stop the
answer being tunable:

- **The ubiquitination drive is re-calibrated per scenario** so the NR4A3 arm is always a *working* degrader.
  Without that the model conflates "the paralogue is spared" with "nothing was degraded at all."
- **The metric is continuous, not a threshold** — the best NR4A3 degradation reachable at any dose where the
  paralogue stays ≤20%, both arms at the same dose. With zero selectivity the two arms are identical at every
  dose, so the metric is *pinned to the ceiling by construction*. An earlier threshold version flipped its
  conclusion when the threshold moved, which meant the threshold was driving the answer.

Swept over 27 potency scenarios (warhead K_d 10 nM–1 µM × α 1–10 × on-target D_max 90–99 %):

| NR4A3 target | scenarios reachable | required margin (min / **median** / max), kcal/mol |
|---|---|---|
| 70 % | 21/27 | 1.5 / **1.5** / 1.75 |
| 80 % | 21/27 | 1.75 / **2.00** / 2.25 |
| 90 % | 12/27 | 2.5 / **2.75** / 2.75 |

### 1.3 How big a margin can we actually resolve?

MDD = z · replicate-SD · √(2/n) for the difference of two independently-estimated ΔΔG values (replicate SD per
the prereg, **not** MBAR SE):

| replicate SD | n = 2 | n = 3 | n = 5 | n = 8 |
|---|---|---|---|---|
| 0.4 | 0.78 | 0.64 | 0.50 | 0.39 |
| **0.7** | 1.37 | **1.12** | 0.87 | 0.69 |
| 1.0 | 1.96 | 1.60 | 1.24 | 0.98 |

So the required effect is **~1.8× the best-case noise floor** and of the *same order as the method's accuracy*
(OpenFE's public RBFE benchmark is ~1.7 kcal/mol RMSE — and, as nr4a3-program-map.md itself now records, that citation
**does not even cover the ternary lane**, which runs NAGL charges and has no accuracy number of its own until
Val B). A precision floor near the effect size is survivable with enough replicates; an *accuracy* floor near
the effect size is not, because replicates do not shrink systematic error.

**This does not say the interface axis is worthless.** It says it is a *confirmation* tool operating near its
limit, not a *discovery* tool — and the plan is currently using it as the latter.

---

## 2. Two categorical axes exist, and they were already in the repo's data

A **categorical** mechanism is one where the paralogue cannot do the thing at all — no free-energy contest to
win. [`nr4a_paralogue_unique_residues.py`](../modalities/nr4a_paralogue_unique_residues.py) maps them from
full-length UniProt sequences (P22736 / P43354 / Q92570 / Q01844), run on CI because the sandbox's egress proxy
blocks UniProt. Uniqueness is computed **twice**, with the linear-gap NW aligner already used for the NR-V04
Leg-0 and with the atlas's affine-gap BLOSUM62 aligner, and only alignment-robust calls are allowed to be a
design premise (two lysines, K85 and K194, were excluded on disagreement).

### 2.1 Axis 1 — a paralogue-unique nucleophile (covalent capture)

| NR4A3 | NR4A1 | NR4A2 | RSA | d(cryptic pocket) | d(nearest docked pose) | reach |
|---|---|---|---|---|---|---|
| **C397** | N363 | S363 | 0.395 | **10.9 Å** | 12.3 Å | exit-vector arm |
| **C420** | Q388 | A389 | 0.311 | 18.3 Å | 16.0 Å | linker-borne |
| C559 | Q528 | Q528 | 0.095 | 12.8 Å | 13.5 Å | linker-borne (buried in this conformer) |
| C166 | H160 | N151 | — | — | — | outside the modelled LBD (hinge/DBD) |

**The precedent is the repo's own result, read the other way round.** `nrv04_cys_conservation.py` established
that celastrol's reactive **NR4A1 Cys551 is unique to NR4A1** — NR4A3 has Thr579, NR4A2 has Tyr. This revision's
run reproduces that exactly (C551 → NR4A3 T579) and completes the picture: NR4A1 has **5** cysteines NR4A3
lacks, NR4A3 has **4** that both paralogues lack. nr4a3-program-map.md currently files celastrol's covalency purely as a
*confound* ("NR-V04 does not validate the noncovalent machinery… its selectivity may be largely
target-engagement"). That is true and must stay. But it is also the field's **only demonstrated case of
NR4A-family-selective degradation**, and the most parsimonious explanation of it is a paralogue-unique cysteine.
A programme trying to achieve the reciprocal outcome should take the reciprocal handle seriously rather than
treating the mechanism only as noise in someone else's control experiment.

None of the three LBD cysteines sits *inside* the pocket, so this is not a covalent-warhead design — it is an
**electrophile on the exit vector or the linker**, which in a degrader is architecturally free: the linker
already leaves the pocket and travels 10–20 Å. C397 at 10.9 Å is the lead handle.

### 2.2 Axis 2 — a paralogue-unique ubiquitination site

| NR4A3 | NR4A1 | NR4A2 | RSA | d(cryptic pocket) |
|---|---|---|---|---|
| **K572** | A | N | **0.879** | 11.5 Å |
| **K518** | L | V | 0.413 | 13.4 Å |
| **K592** | T | T | 0.506 | 16.2 Å |
| K178 | R | I | — | outside the modelled LBD |

All three exposed unique lysines lie in the **same 11–16 Å band from the pocket as the conserved ones**, so an
E3 orientation *can* be steered to cover a unique lysine rather than a shared one. Ternary formation is
necessary but not sufficient — that is already reviewer requirement 5. The revision promotes it from a *late
filter* to a **primary design objective**: pick the orientation basin by which lysine its transfer zone covers.

### 2.3 What the model says these axes are worth

Same window metric, **zero** thermodynamic margin (identical ternary energetics on both paralogues), median over
the 27-scenario grid:

| mechanism | median best NR4A3 degradation at the 20 % paralogue ceiling |
|---|---|
| interface thermodynamics only (**the null**) | 0.185 |
| covalent capture — equilibrium proxy (**lower bound**) | 0.245 |
| unique lysine | **0.824** |
| covalent (proxy) + unique lysine | **0.885** |
| covalent capture — **kinetic**, time-integrating form | **0.915** |

Covalency is modelled twice on purpose. An irreversible adduct is not an affinity — it is a time-integrating
capture, `L(t) = 1 − exp(−k_inact·θ·t)`, with the paralogue's L identically **zero** because there is no
nucleophile. The equilibrium proxy therefore *understates* it, and the code asserts (unit-tested) that the proxy
is a lower bound on the kinetic form.

### 2.4 An axis that was checked and came back weak — report it, don't quietly drop it

The fusion's own N-terminus looked like the strongest possible handle: lysines on EWSR1 are absent from NR4A1/2
*and* from wild-type NR4A3. **The sequence says no.** EWSR1 residues 1–264 (the exon-7-like junction the repo's
neoantigen work already uses) contribute **1 lysine**; 1–349 contribute 2. The EWSR1 low-complexity region is
Gln/Gly/Tyr-rich and Lys-poor. So fusion-lysine-directed ubiquitination is a **thin** handle, and the
fusion-vs-wild-type-NR4A3 discrimination it would have bought is not available this way. It stays in the plan
only as a modelling scenario, not as a design axis.

---

## 3. The revised search — mechanism-first, not orientation-first

The change is one level up from the current ladder. Orientation-first was already an improvement on
molecule-first; the same logic applied once more says **choose the selectivity mechanism before searching
orientation space**, because the mechanism determines what the orientation search is even optimising.

```
       paralogue-unique CHEMISTRY (nucleophile) + paralogue-unique GEOMETRY (lysine)
                                    │
                 ┌──────────────────┴──────────────────┐
      basins that place              basins that cover a UNIQUE lysine
      an electrophile at             in the E2~Ub transfer zone and
      an NR4A3-unique Cys            NOT the conserved ones
                 └──────────────────┬──────────────────┘
                    interface thermodynamics used to RANK
                    within the surviving set — never to create
                    selectivity on its own
                                    │
                      linker requirements → candidates
```

Concretely, the 5a orientation-basin search (still **$0 CPU**) gains two scoring terms and one breadth change:

1. **Electrophile-reach term** — does the basin's linker path pass within tethering distance of C397 / C420 /
   C559, at a geometry a mild electrophile could adopt?
2. **Transfer-zone lysine identity term** — which lysine does the modelled E2~Ub transfer zone cover? Score
   *unique-only* highest, *unique + conserved* next, *conserved-only* lowest. This is a set-membership question,
   not an energy.
3. **E3 breadth** — the plan considers exactly two recruiters (VHL, CRBN). Since basin search is CPU, widening
   to the ligandable set with public ligand-bound structures (VHL, CRBN, cIAP1/BIRC2, DCAF1, DCAF15, DCAF16,
   KEAP1, FEM1B, RNF114) costs ~nothing and multiplies the chance that *some* E3 surface is complementary to
   NR4A3's differential surface. **Downselect to ≤2 before any GPU spend**; the free E3-expression analysis
   (`nr4a3_e3_expression.py`, already run for both CRL arms) extends to the new candidates for the same $0.

**Pose-robustness, also free.** Everything is conditional on the hypothesised cmpd19 pose. Since the basin
search is CPU, run it over the *pose ensemble* and carry only basins that persist across poses, reporting the
surviving fraction. The sequence-level uniqueness of C397/K572 is pose-independent; only the *reach* estimate is
conditional, which is a much smaller conditional surface than the current plan carries.

---

## 4. Replace the primary causal test with one the ligand-alchemy lane can actually run

nr4a3-program-map.md's designated primary causal result is the reciprocal protein-mutation cycle
`ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary`. As of today that rung is **UNPRICED**, it has produced no leg,
and it is the repo's only **cross-lane** subtraction (NAGL ternary against am1bcc binary) — a charge-model difference that does not cancel
and would be indistinguishable from the very effect it is built to detect. The paper's headline causal claim
should not be hostage to that.

> **Cross-session update, 2026-07-24 PM (added after this document was first written).** A parallel session was
> mid-build on this exact lane while the review was being written, and it has since established two things that
> sharpen §4 rather than change it: **perses' protein-mutation path is OpenEye-gated** (established by running
> it — a commercial licence, not available here), so the engine was retired and **rebuilt on pmx + GROMACS**
> (trimcrae decision, same day). The benchmark legs are staged from RCSB with mutation-site verification and
> reference ΔΔG checked against **SKEMPI 2.0**; no GPU leg has run yet. Two consequences, stated plainly:
> (a) the demotion proposed here **does not cancel that work** — the known-answer benchmark is required under
> either framing, and the confirmatory line is gated on exactly it; (b) the fact that the lane needed two engine
> rebuilds in one day, and is still unpriced, is *additional* evidence for not making the paper's headline causal
> claim depend on it. It is not evidence that the lane is a bad investment — a second, independent causal line is
> worth having, which is why it is kept.

**There is a causal test that runs on the same ligand-alchemy lane Val B is already calibrating.** For a candidate *d* and a
matched control *d₀* differing only in the element that engages the wedge:

```
S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)
```

Each term is an ordinary relative alchemical quantity inside one protein. The difference asks the *design*
question — **does this structural element create paralogue discrimination?** — rather than the *residue*
question. It needs no protein-mutation engine, no cross-lane subtraction, and (see §5, lever 2) **only ternary
legs**, because the binary and solvent legs cancel identically.

Recommendation: **the ligand-side double difference becomes the primary causal result; the protein-mutation
cycle stays as an optional confirmatory experiment**, gated on its own known-answer benchmark
(barnase–barstar Y29A/Y29F, hGH–hGHR W104A) exactly as nr4a3-program-map.md already specifies. If the benchmark passes,
the paper gets *two* independent causal lines. If it never runs, the paper still has one — on a lane whose
accuracy is being established by Val B anyway.

**A second substitution, for the same reason.** The NR-V04 retrospective currently gates the whole prospective
ladder at $45–115. By the repo's own UniProt result its selectivity is most plausibly **covalent
target-engagement**, so it is a weak calibrator for a noncovalent ternary pipeline — the reviewer said as much
when demoting it to a biological holdout, but the dependency graph still has it gating 5a-KS. The natural
method calibrator is **SMARCA2 vs SMARCA4**: a close paralogue pair with degrader-level selectivity, solved
structures, a non-covalent mechanism, and — decisively — **already staged in this repo** (8G1Q, the
SMARCA4→SMARCA2 substitution, `smarca2_model.py`, the frozen Wurz calibration). It is the same system valB_mini
is running on, so the paralogue-discrimination module becomes a marginal add-on rather than a new campaign.

---

## 5. Six cost levers, each with its evidence

**Lever 1 — run ternary production at 4 fs (≈2× on every ternary leg).**
`ternary-rbfe-runbook.md` §1c records the decisive experiment: after plain-MD pre-equilibration the calib
ternary leg ran **warmup 48/48 at 1 fs → production 40/40 at 4 fs, zero NaN, ΔG_morph = 47.28 ± 0.53**, where
every prior attempt died at warmup iteration 1.

**⚠ Checked against the live lane rather than the doc** (2026-07-24 4:12 PM ET, GH run 30123894814 `mode=tail`
reading the running VM `gcp-ternary-30112102294`), because "aren't we already at 4 fs?" is exactly the kind of
question a stale doc answers wrongly:

```
[tfep] timestep=2.0 fs, minimization_steps=5000 (NaN-robust start)
[PROGRESS-SUMMARY] leg=calib_hi_to_lo__binary_vhl seed=0 src=live live_vms=1
  warmup_committed_iter=00000800 production_committed_iter=00001680 NaN_seen=no charge=nagl
  warmup_dt_override="WARMUP timestep overridden to 1.0 fs" reduced_dt_warn="none" nan_at=""
```

The as-run shape is **1 fs warmup → 2 fs production**. The remembered "4 fs with a 1 fs warmup" is the §1c
*pre-equilibration demonstration*, not the production lane: `gpu-ternary-fep-gcp.yml` defaults `timestep_fs: 2.0`
and `use_preequil: 0`, and the 4 fs demonstration held only *because* pre-equilibration was on. So the lever is
live, not already banked — and the adoption run must set `use_preequil=1` and `reset_commits=1` (OpenFE refuses
to resume a checkpoint whose protocol timestep differs, so a dt change is a fresh edge, not a continuation).
Iterations are **timestep-independent** (2.5 ps/iteration, `rbfe_spot_driver._iters_from_time`), so 4 fs is
exactly half the force evaluations: **~$10–16/edge → ~$5–8/edge**.
*Caveat that must be honoured:* the runbook requires validation and production to run at the **same** timestep,
and the 4 fs evidence is 40 production iterations, not 2000. So this is not "switch and hope" — see §7 for the
one paid step that settles it, which doubles as the matched-timestep calibration.

**Lever 2 — the binary and solvent legs cancel in every paralogue comparison (up to 2×).**
`nr4a3_ternary_fep.py` defines the three environments as `solvent`, `binary_<e3>` (E3 machinery + PROTAC, **no
target**) and `ternary_<target>`, with `ΔΔG_coop = ΔG_ternary,morph − ΔG_binary,morph`. The binary and solvent
legs are therefore **paralogue-independent**, so for any morph:

```
ΔΔG_coop(P) − ΔΔG_coop(P′)  =  ΔG_ternary,P − ΔG_ternary,P′        (exactly)
```

A three-paralogue comparison needs **three ternary legs plus one shared binary and one shared solvent leg — not
three edges.** `nrv04_retrospective` and valB_full module 3 are both currently priced as "3–6 ternary *edges*",
i.e. paying for the shared legs three to six times over. Naive 3 edges = 18 legs; shared = 12 legs (−33 %); and
if only the selectivity *contrast* is needed, 9 legs (−50 %).

**And the saving is larger than the leg count suggests, because a binary leg is not cheap.** pricing.md carried
"conservative: the binary leg is a smaller box and should run faster"; the live log above refutes it — the
`binary_vhl` leg ran at **~28.6–38.2 s/iter (median ≈33)** on L4, the same rate as the ternary leg's ~33 s/iter.
A shared binary leg is a *full-price* leg paid once instead of N times.

**Lever 3 — sequential stopping instead of a fixed 3 replicas (~20–25 %).**
The repo already contains `adaptive_certify.py` (anytime-valid bounds, honest under repeated looks and
data-dependent stopping) and `adaptive_allocator.py`, both built and unit-tested, and **neither is wired into
the ternary ladder**. Run 2 replicas; add the third only where the decision is not yet determined at the
preregistered margin. Anytime-valid bounds are what make this legitimate rather than p-hacking.

**Lever 4 — reorder so the free gates lead.**
`selectivity_wedge_confirm` currently `depends_on: [orientation_basin_search, valB_full, nrv04_retrospective]` —
i.e. ~$80–215 of ternary work must be bought before the causal kill-switch can fire. Its validation needs are
*protein-mutation* (or, per §4, ligand-morph) benchmarks, not a PROTAC-cooperativity cube. Decoupling lets the
kill-switch fire early, and puts the two free categorical screens (§2) ahead of everything priced.

**Lever 5 — the ligand-side double difference (§4) instead of an unpriced protein-mutation campaign.**
Cost known and small (2 ternary legs × replicas, and lever 2 applies); cost of the alternative: unpriced.

**Lever 6 — E3 breadth is free at the search stage and must stay free.**
Widen at 5a (CPU), downselect to ≤2 recruiters before any GPU leg. Explicitly log what was dropped — a silent
top-N is exactly the "no silent caps" failure mode.

### ⚠⚠ The revised total is WITHDRAWN (2026-07-24 ~5:15 PM ET)

A parallel session measured the real system while this was being written and **halted `step1_fanout` on the
result** (branch `claude/step1-fanout-cmpd19-congeneric-jfwg0j`). Two errors compounded, and they hit every GPU
line here, not only theirs:

1. **System transferability** — the RBFE edge was priced on a **TYK2** rate (~5.2 s/iter); the real
   cmpd19/NR4A3 cryptic-pocket complex samples at **~13.6 s/iter** (three independent hosts, 16 samples each) —
   a **~2.6× heavier system**.
2. **Bid basis** — $0.122/hr assumed vs **$0.35–0.39/hr** realized on the current 4090 market.

`step1_fanout` is therefore **~$91–101, not ~$12–26**; ~$2 was realized before the halt and **0/19 units produced
a ΔΔG**. The bid error applies to my ternary lines too (**~$20–28/edge, not ~$10–16**), and the transferability
error is **live and unmeasured** there — the ~16 s/iter ternary rate came from **SMARCA2/VHL 8G1Q** and is being
used to price **NR4A** ternaries, which is exactly the move that just cost 2.6×.

**The six levers survive; the total does not.** Every lever is a *ratio* (halved force evaluations, an exact
cancellation, sequential stopping), so none depends on $/hr or system size. The absolute figure was built on
bases now measured low, so the honest first-order re-derivation at 2 fs is **~$400–450 mid**, not ~$240 —
higher than the ~$390 this review started from. **That strengthens the argument rather than weakening it:** if
GPU work costs ~3× the assumption, buying an axis that needs ~2.0 kcal/mol when the method resolves 1.12 is a
worse trade than ever, and the $0 categorical screens are worth correspondingly more.

*(The table below is pre-correction and is retained to show what each lever contributes, not as a total.)*

### Revised ladder cost

| Rung | current | revised | why |
|---|---|---|---|
| 0–1 (done) | ~$2 | ~$2 | — |
| 2 · step1_pilot (done) + valB_mini (in flight, 2 fs) | ~$13 | ~$13 | sunk; running on GCP trial credit |
| **2b · NEW: 4 fs adoption + matched re-calibration** | — | **~$5–8** | lever 1; pays for itself if ≥1 further ternary edge runs |
| 3 · valB_full cube | $35–100 | **$20–65** | levers 1+2; SMARCA2/4 module reuses the staged system |
| 3 · NR-V04 covalent feasibility (done) | $8 | $8 | — |
| 4 · step1_fanout | $12–26 | $12–26 | unchanged |
| 4 · NR-V04 retrospective | $45–115 | **$15–40** | levers 1+2; and moved *behind* the free gates |
| 5a · basin search (now multi-E3, + 2 categorical terms) | $0–50 | $0–50 | still CPU |
| 5a-KS · causal wedge | UNPRICED | **$5–25** | lever 5 (ligand-side); protein-FEP kept optional |
| 5b · inverse linker | $0–20 | $0–20 | unchanged |
| 5c · ensemble refinement | $20–150 | **$15–100** | fewer survivors to refine |
| 5d · local ternary FEP | $21–90 | **$10–45** | levers 1+2 |
| **total (GO at every gate)** | **~$390 mid (~$170–610)** | **~$240 mid (~$90–390)** | |

The *expected* cost falls further than the totals suggest, because the two new leading gates are **$0** and can
return a NO-GO before any of it is spent.

---

## 6. What this does NOT change

- The five reviewer validation requirements, verbatim. Val B is still load-bearing; the accuracy/precision/
  ternary-control separation is untouched; cryptic-pocket results stay conditional; ABFE stays HELD.
- The language discipline. A covalent handle does not upgrade anything to "selective degrader" — the deliverable
  is still a **computationally prioritized, structure-defined, retrosynthetically annotated candidate set**, and
  no efficacy, safety, window or clinical claim is licensed by anything here.
- The honest-negative exit. If no basin places an electrophile at a unique cysteine *and* no basin covers a
  unique lysine *and* no wedge survives, the paper is the negative result — and now it is a **stronger**
  negative, because it will have ruled out three mechanisms instead of one.
- The spending rules. Nothing here is pre-authorised.

---

## 7. Risks and honest limits of this revision

1. **A covalent PROTAC sacrifices catalytic turnover.** Irreversible target capture makes the degrader
   stoichiometric — the very property that makes PROTACs attractive. Mitigation: prefer a **reversible-covalent**
   handle (cyanoacrylamide-type), which keeps turnover while retaining the categorical dependence on a
   nucleophile. The margin model does **not** represent this cost.
2. **Electrophile promiscuity is a real liability.** A reactive handle that labels the proteome is worse than no
   selectivity, and with no wet lab there is no chemoproteomics to check it. This must be stated as an
   unresolved liability, ranked alongside the parent warhead's reported MYC induction — not buried.
3. **C397's exposure is from one static opened conformer** (RSA 0.395). Cysteine accessibility in a
   cryptic-pocket protein is conformer-dependent. The already-costed matched NR4A1/2 MD ensemble add-on
   (~$10–40) should report the *distribution* of C397 exposure, not a single frame's value.
4. **The unique-lysine axis is probabilistic, not absolute.** Real degraders often ubiquitinate several lysines,
   and lysine-less substrates can still be degraded via N-terminal/Ser/Thr/Cys ubiquitination. Removing the
   unique lysine raises the odds; it does not guarantee the paralogue is spared. The model's
   `eps_paralogue_frac = 0.05` is an assumption, and the write-up must say so.
5. **Reach is conditional on the cmpd19 pose.** The *uniqueness* is not, but the 10.9 Å is. Pose-marginalised
   basin search (§3) is the mitigation, and the residual conditionality must be reported.
6. **Widening the E3 set adds combinatorics.** Only legitimate because the widening happens where compute is
   free; the downselect before GPU is mandatory, with the dropped set logged.
7. **The margin model is a sensitivity analysis, not a prediction.** Every K_d, α, rate and efficiency in it is
   an illustrative assumption. Its role is to compare *mechanisms* under matched assumptions — which is
   assumption-robust in a way that any single number from it is not.

---

## 8. Decisions this puts in front of trimcrae

Everything free in this document is already built, run and committed. Three items cross a gate:

*(Status 2026-07-24: items 2 and 3 are **ADOPTED**; item 1 remains open and was sharpened by the live-lane check
in §5 — production really is at 2 fs, so the ~2× lever is live rather than already banked.)*

1. **Adopt 4 fs for the ternary lane (lever 1)?** The cheapest honest way to settle it is to **re-run the
   valB_mini calibration edge at 4 fs** (~$5–8). That single edge does three jobs at once: it validates the
   timestep over a full production leg, it supplies the **matched-timestep calibration** the runbook requires,
   and it is an independent reproducibility replicate of the 2 fs result. If it converges, every downstream
   ternary leg is ~2× cheaper — the ladder has ≥6 of them, so it pays back several times over.
2. **Swap the method calibrator from NR-V04 to SMARCA2-vs-SMARCA4 (§4)?** Free to decide, changes what
   valB_full module 3 runs on. NR-V04 remains the biological holdout either way.
3. **Demote the protein-mutation wedge from primary to confirmatory (§4)?** This is the one genuinely
   *program-shaping* call: it changes what the paper's headline causal evidence is. Recommended, because the
   ligand-side double difference runs on the lane Val B already has an accuracy control for, while the
   protein-FEP lane has an engine that was rebuilt twice in one day (perses retired as OpenEye-gated → pmx +
   GROMACS), has produced no leg, is unpriced, and carries a cross-lane charge mismatch to resolve first.
