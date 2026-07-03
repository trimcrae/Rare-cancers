# In-silico completeness ledger — NR4A3-selective degrader

> **Why this doc exists.** The North Star is *the state of the art of what in-silico testing can do for an
> NR4A3-selective degrader* (CLAUDE.md, 2026-07-01). We were finding gaps **reactively** — the red-team
> surfaced F1–F20; the user caught that the safety argument rested on DepMap alone (2026-07-02). A
> SOTA claim needs a **proactive completeness map**: every stage a leading degrader-discovery group
> would compute with no wet lab, graded honestly against what we actually have. This is that map. It is a
> **living checklist** — update the Status column as gaps close; never silently drop a row.
>
> **Grading key.** ✅ done (at stated rigor) · 🟡 partial / provisional · 🟠 built-but-idle / queued ·
> ❌ missing · N/A not applicable in-silico. "Cost" is GPU/compute order-of-magnitude
> (¢ = free CI/CPU-seconds; $ = a single <$10 GPU run; $$ = a multi-run GPU campaign).

## A. Target structure & binding pocket
| # | Stage | Status | What's there / what's missing | Cost |
|---|-------|--------|-------------------------------|------|
| A1 | AF2/homology model of NR4A3 LBD + **model-confidence at the pocket** (pLDDT, PAE) | 🟡 | Model exists and is used throughout; the pocket-region confidence is **not stated as an explicit honesty item** in the paper. Reviewers will ask "is the cryptic pocket in a well-modeled region?" | ¢ |
| A2 | Cryptic/induced-fit pocket ID + druggability (fpocket + MD) | 🟡 | Done and **honestly graded** (red-team 2026-06-26): Gate 0/0b/2 pass, Gate 1 basin-breathing only, Gate 3 provisional, druggability reported as fraction-of-frames. **UPDATE 2026-07-03: metad extended to 60 ns cumulative** (`report_metad.py`, `metad-fes-60ns.dat`, 4-test core) — F(Rg) **robust to 2× sampling**: single basin (min Rg 0.755 nm), no separate opened minimum (Gate 1 weak-form holds), druggable-frame region ~0.6 kcal/mol above basin (was ~0.76), frontier ~35 kcal/mol (was ~38) → provisional Gate-3 energetics **confirmed, not revised**. Release run POSITIVE (§2.2). Remaining cheap follow-up: extend per-frame fpocket to the 60 ns frames. | done (60 ns) |
| A3 | **Warhead-pocket** residue divergence NR4A3 vs NR4A1/2 (selectivity determinants) | 🟡 | Interface divergence computed at the **NR4A–CRBN** ternary interface (F18). The **warhead-site** pocket-lining residue comparison — the structural basis for *binder* selectivity — is not separately reported. | ¢ |
| A4 | **Broader NR-superfamily** LBD-pocket cross-reactivity (48 NRs share the LBD fold) | ✅ (honest) | **DONE + FOLDED (§2.7), 2026-07-03** (run 28641411743, `nr4a-superfamily-selectivity.json`). Screened all 47 reviewed human NRs (`nr4a_superfamily_selectivity.py`, 5-test core). Positive controls validate: NR4A1/2 are the ONLY NRs combining pocket coincidence with high-confidence alignment (NR4A2 4/10 @ overall 0.58; NR4A1 3/10 @ 0.51). Honest, non-clean result folded at true weight: two oxosteroid receptors **MR (NR3C2) and AR** coincide at 3/10 and each overlap **2 selectivity handles** (necessary-not-sufficient demonstrated) — bounded (miss the conserved core, ~0.32 marginal confidence, cryptic-pocket unlikely to transfer) and named as the sole non-paralogue energetic-cross-check follow-up. **Residual:** AR/MR docking/FEP (GPU, when unblocked); proteome-wide off-target still open (D4). | ¢–$ |

## B. Ligand generation & pose
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| B1 | De-novo generation (DiffSBDD) | ✅ | denovo_401 sole robust lead. | done |
| B2 | Docking (smina) | ✅ | | done |
| B3 | Pose stability / ensemble | ✅ | Folded into FEP complex-leg equilibration + early-stop (standalone pose-MD judged redundant). | queued w/ FEP |
| B4 | Stereo/protonation robustness | ✅ | Species resolution: denovo_401 stereo-robust; denovo_111 withdrawn (cation reverses). | done |

## C. Affinity (potency)
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| C1 | MM-GBSA single-snapshot | ✅ | | done |
| C2 | Multi-snapshot MM-GBSA + winner's-curse de-bias | ✅ | F16/F17 independent-replicate. | done |
| C3 | Generation-matched decoy null | 🟡 | **Deliberately deferred** (non-enrichment bounds confound; FEP dominates) — decision logged, not an oversight. | (deferred) |
| C4 | FEP absolute binding ΔG | 🟠 | Full spot/parallel/early-stop/diagnostic-gated harness **built**; gated on spot-quota + user go-ahead. | $$ |

## D. Selectivity — the entire thesis
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| D1 | Warhead selectivity screen (NR4A3 vs NR4A1/2) | 🟠 | Built, idle. | $ |
| D2 | **Selectivity FEP (ΔΔG_bind, NR4A3 − NR4A1/2)** | 🟠 | The definitive selectivity number; queued with C4. Early-stop fires on a confidently non-selective ΔΔG **with a per-residue WHY-map**. | $$ |
| D3 | Ternary-level paralogue selectivity | ✅ | F18 across NR4A1/2/3. | done |
| D4 | Off-target beyond paralogues (NR-family / proteome) | 🟡 | NR-family side **DONE + folded** — see A4 (§2.7; MR/AR the only non-paralogue sequence-level flags, energetic cross-check named). Proteome-wide off-target still open. | ¢–$ |

## E. Degradation-specific (it is a degrader, not just a binder)
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| E1 | Ternary complex prediction (Boltz-2) | ✅ | | done |
| E2 | Ternary selectivity across paralogues | ✅ | F18. | done |
| E3 | Degradation geometry / surface-lysine accessibility / ubiquitination zone | 🟡 | `degradation_geometry` in report_ternary computes it; not yet written up as a first-class result with a lysine-accessibility readout. | ¢ |
| E4 | Linker **exit-vector** feasibility (does the warhead's solvent-exposed vector admit a CRBN linker?) | ❌ | Required to claim a *buildable* degrader vs an abstract binder. | ¢ |
| E5 | Ternary **cooperativity (α)** estimate | ❌ | | $ |
| E6 | E3-ligase (CRBN) availability | ✅ | **DONE 2026-07-02** (`nr4a3_e3_expression.py`, HPA): the full CRL4^CRBN machinery — **CRBN, DDB1, CUL4A, CUL4B, RBX1 — is "Detected in all" tissues**, so the degrader's ligase is available in soft-tissue/mesenchymal contexts (premise grounded, not a tissue-restriction risk). | ¢ |
| E7 | Molecular-glue **neo-substrate off-target** risk (thalidomide/IMiD lesson) | ✅ (flag) | **DONE 2026-07-03 (documented risk).** The design recruits CRBN via a **pomalidomide-class** ligand, whose glue face degrades a known set of **C2H2 zinc-finger / IMiD neo-substrates** — IKZF1/IKZF3, ZFP91, SALL4 (the teratogenicity substrate), plus CK1α / GSPT1 for related IMiDs (**well-established degrader literature — add verified primary refs before preprint; do NOT cite from memory**). **Mitigating for a PROTAC vs a glue:** the linker is attached to the CRBN ligand's solvent-exposed rim, which typically **occludes the glue interface and suppresses neo-substrate ternary formation** — but this is not guaranteed, so the assembled degrader must be **counter-screened** (global proteomics / a zinc-finger-degron panel) at the wet-lab handoff. This is a design-risk flag, correctly in-silico's scope only to *name* the liability; quantifying it needs the assembled PROTAC + wet lab. | ¢ |

## F. Developability / ADMET  →  DONE 2026-07-02 (`nr4a3_developability.py`)
Lead **binder** denovo_401: MW 304.5, cLogP **4.63** (lipophilic-leaning — the one watch-item), TPSA 29.5,
HBD 1 / HBA 2, rot-bonds 7, Fsp3 0.70, **QED 0.796**, **0 Lipinski violations**, **Veber pass**, SA **3.87**
(readily synthesizable), **PAINS + BRENK clean**. Projected full-PROTAC envelope (binder + pomalidomide +
short linker): MW ~657, cLogP ~4.2, rot-bonds ~14 → normal **beyond-Ro5** degrader space.
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| F1 | Physchem / beyond-Ro5 profile | ✅ | Computed (above). Binder is Ro5/Veber compliant; PROTAC projection lands in expected bRo5. | done |
| F2 | Structural alerts / PAINS | ✅ | **Clean** on both PAINS and BRENK catalogs. | done |
| F3 | Synthetic accessibility (SA score) | ✅ | SA 3.87 (1=easy..10=hard) — synthesizable. | done |
| F4 | Permeability / chameleonicity / efflux | ✅ | **DONE 2026-07-02** (`nr4a3_admet_ext.py`): conformer-ensemble IMHB **0** (no PSA-masking needed — TPSA already low), Rg range 0.87 Å (modest flexibility), **P-gp efflux risk low** (0 flags). Full-PROTAC chameleonicity awaits the linker build (E4). | ¢ |
| F5 | Aggregation + hERG/reactive-group liability (audit Tier-B #6) | ✅ | **DONE** — colloidal-aggregation **low** (1 flag = cLogP 4.63; high Fsp3 0.70 + one aromatic ring offset it). **hERG: low** — denovo_401 has **no nitrogen at all**, so it lacks the classic basic-amine hERG pharmacophore. **Reactive toxicophores: none** (no Michael acceptor / epoxide / aldehyde / nitro / acyl-halide / anhydride). | ¢ |

## G. Biological rationale
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| G1 | **H2 efficacy** — EMC fusion-dependency prior | ✅ | 4-pillar prior; honest floor = no direct LoF in an EMC line (dTAG is the wet-lab make-or-break). `nr4a3-emc-biology-evidence.md`. | done |
| G2 | **H1 safety** — paralogue redundancy / tolerability | ✅ (honest) | **DONE 2026-07-02.** DepMap NR4A1/2/3 (NR4A3 0/1178 dependent) + gnomAD (NR4A3 **LoF-constrained** pLI 0.9999 — the honest brake; "dispensable⇒safe" invalidated) + HPA (NR4A1/3 broadly co-expressed; NR4A2 CNS-enhanced). Residual risk now *located* (developmental/CNS, NR4A2-sparing-dependent). IMPC empty → MGI is the one open follow-up. | ¢ |

## H. Honesty / statistical controls
| # | Stage | Status | Notes |
|---|-------|--------|-------|
| H1 | Winner's-curse de-bias | ✅ | F16/F17. |
| H2 | Iterated adversarial red-team | ✅ | F1–F20; findings folded. |
| H3 | **This completeness ledger** | ✅ (new) | Proactive gap map; keep it live. |

---

## The honest bottom line — where "state of the art" currently has holes
Ranked by (impact on the *selective-degrader* claim) × (how cheap to close):

1. **Developability/ADMET (F1–F5)** — *free, absent, reviewers always ask.* One RDKit script gives physchem/bRo5, PAINS/structural alerts, SA score for the lead. Highest value-per-cost.
2. **Broader selectivity beyond the two paralogues (A4 / D4)** — was the single most exposed part of the thesis. **DONE + folded into §2.7 (2026-07-03):** all 47 human NRs screened; controls validate; only MR/AR flag at the sequence level (each overlapping 2 handles, but bounded + named for an energetic cross-check). Proteome-wide off-target still open.
3. **Degrader-completeness (E3/E4/E6/E7)** — linker exit-vector, lysine-accessibility write-up, E3/tissue rationale, neo-substrate risk. These are what make it a *degrader* result, not a *binder* result. Mostly free.
4. **Model-confidence honesty (A1)** — state pLDDT/PAE at the pocket explicitly. Free.
5. **The two queued GPU campaigns (C4/D2, A2 release run)** — already scoped; the expensive, decisive ones.

**Everything in tiers 1–4 is free or a single <$10 run and is currently missing or unwritten.** Closing them is what moves the paper from "a good binder story with a big FEP pending" to "a genuinely complete in-silico characterization."

---

## Audit-expanded gaps — adversarial multi-lens sweep (2026-07-02, `insilico-completeness-audit` workflow)
8 expert lenses proposed ~36 candidate omissions; **each was handed to an independent skeptic agent that tried
to refute it** (real? no-wet-lab-feasible? material? already-covered?). Result: **35 KEEP / 9 DROP**. The DROP
layer is as valuable as the KEEP layer — it caught false positives (including one *I* had ranked "critical").

### ✂️ DROPPED as already-covered (do NOT spend on these — verified redundant)
- **Cross-validate the AF2 cryptic pocket against experimental NR4A (Nurr1/Nur77) LBD crystals** — DROP ×3
  (already covered: §2.1 anchors druggability on an NR panel *including the occluded 1OVL Nurr1 LBD as the
  negative control*). *This corrects my earlier "critical gap" call — the adversarial verify refuted it.*
- **Full stereoisomer enumeration / eutomer ID** — covered by the pre-FEP species resolution (16 diastereomers).
- **Paralogue cryptic-pocket formability rerun** — covered by the state-matched NR4A1/NR4A2 metadynamics (§2.4).
- Fraction-unbound/PPB, CYP soft-spot mapping, allosteric H12/AF-2 effect, a duplicate QSP model — low materiality.

### ✅ KEEP — adversarially-verified real gaps, clustered + ranked (materiality × cheapness)
**Tier A — do first (critical/high, cheap):**
1. 🟡→ **Bound-pose validity + strain of denovo_401** (`nr4a3_pose_validity.py`, 2 tests). The audit's #1
   finding, confirmed: MM-GBSA (`mmgbsa_energy.py`) **cancels intramolecular strain by construction**, so the
   scoring stack is provably strain-blind. **Mode A (done now):** receptor-free conformational accessibility —
   denovo_401 is **well-behaved** (7 rot-bonds; 5 conformers within 3 kcal/mol; no rigidity flag), so the
   scaffold is not intrinsically strain-prone. **Mode B (wired):** exact bound-pose strain (bound vs global-min
   + PoseBusters-lite validity) is now computed on the *identical* NR4A3 pose inside the MM-GBSA loop and
   emitted per candidate — so the real strain-corrected ΔG **lands automatically on the next MM-GBSA run**
   (piggybacks, no extra GPU). [¢]
2. ✅ **DONE 2026-07-02 — Quantitative degradation model** (`nr4a3_degradation_model.py`, 4 unit tests).
   Three-body cooperative equilibrium (Douglass 2013) + steady-state synthesis/degradation → DC50, Dmax,
   hook. Delivered as a mechanistic harness + **sensitivity maps over α and binary Kd_target** (the two
   quantities the queued FEP sets), so it *becomes* the analysis layer the selectivity FEP feeds — the
   NR4A3-vs-NR4A1/2 spread in the Kd_target map IS the predicted degradation selectivity. Illustrative regime:
   DC50 425 nM → 16 nM as α 1 → 10; hook present throughout. Not a calibrated point prediction until FEP (so
   labelled). [¢]
3. **Cryptic-pocket OPENING free energy / apo open-state population** — KEEP, **critical**. *Rigorously quantify
   ΔG(apo→open) + equilibrium open population; partly addressed by the release run (24 % druggable frames) but
   the opening free energy is still read off an unconverged biased F(Rg) — this is the honest gate.* [single-GPU/$]

**Tier B — high value, cheap-to-moderate:**
4. **AF2 conformational ensemble (MSA-subsampling / AF-Cluster / AlphaFlow)** as MD-orthogonal evidence the
   pocket opens — KEEP ×4, high. *Independent of the biased MD our claim currently rests on.* [single-GPU/$]
5. **Proteome-wide off-target** — structure-based reverse-docking/pocket-similarity **and** ligand-based
   polypharmacology (with OOD applicability flag), beyond the NR fold — KEEP ×4, high. *This is Tier 2 (D4),
   now sharpened: go proteome-wide, not just NR-family.* [¢–$]
6. **bRo5 permeability & chameleonicity** — 3D-PSA / intramolecular-H-bond / Rg ensemble + efflux (P-gp/BCRP)
   substrate-liability — KEEP ×2, high/med. *Extends F4/F5; the real ADMET question for a degrader.* [¢]
7. **Pocket hydration thermodynamics** (GIST / inhomogeneous solvation) — KEEP ×3, high. *Are there displaceable
   high-energy waters driving the affinity? energetic druggability beyond fpocket geometry.* [$–campaign]
8. 🟡→ **Resistance / escape-mutation forecast** of the warhead pocket — KEEP ×2, med. **Conservation half
   DONE 2026-07-02** (`nr4a3_resistance_map.py`): all 10 pocket residues are **invariant across 5 NR4A3
   orthologs spanning ~300 My (human→chicken; xenopus/zebrafish auto-dropped by the alignment-identity
   guard)**, so escape via pocket mutation is evolutionarily disfavoured — and the selectivity handles are
   **paralogue-divergent yet ortholog-invariant** (selective *and* durable). *(A first run with hardcoded
   accessions gave a spurious "no anchors"; caught by the identity guard, refetched by organism query.)*
   **Energetic half BUILT + GPU-queued** (`nr4a3_resistance_ddg.py` + `gpu-resistance-aws.yml`): computational
   Ala scan (mutate each pocket residue → Ala, re-score denovo_401 by MM-GBSA → ΔΔG), dispatches when the g5
   frees from metad. [¢ done / $ queued]

**Tier C — high value, GPU-campaign (sequence after the cheap wins):**
9. **Ternary-complex MD stability / kinetic persistence** (not just static Boltz-2) + **binary & ternary
   residence-time / koff** (τ-RAMD / infrequent metadynamics) — KEEP ×3, high. *Degrader efficacy is
   koff/residence-driven; static ternary confidence isn't enough.* [campaign]
10. **CRBN / ubiquitin-machinery co-partitioning into the EWSR1::NR4A3 condensate** — KEEP, med. *Does the E3
    even reach the fusion's phase-separated compartment? a degrader-in-context question.* [¢–$]

**Sequencing note.** Tier A #1 and #2 are free and I start them immediately. The GPU items serialize behind the
one-concurrent-g5 rule and the queued FEP/release runs — none is a wet-lab ask; all fit the no-lab mandate.
