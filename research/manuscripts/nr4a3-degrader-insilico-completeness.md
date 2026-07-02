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
| A2 | Cryptic/induced-fit pocket ID + druggability (fpocket + MD) | 🟡 | Done and **honestly graded** (red-team 2026-06-26): Gate 0/0b/2 pass, Gate 1 basin-breathing only, Gate 3 provisional pending release run, druggability reported as fraction-of-frames. | $ (release run queued) |
| A3 | **Warhead-pocket** residue divergence NR4A3 vs NR4A1/2 (selectivity determinants) | 🟡 | Interface divergence computed at the **NR4A–CRBN** ternary interface (F18). The **warhead-site** pocket-lining residue comparison — the structural basis for *binder* selectivity — is not separately reported. | ¢ |
| A4 | **Broader NR-superfamily** LBD-pocket cross-reactivity (48 NRs share the LBD fold) | ❌ | A "selective" degrader checked against **only 2 paralogues** is under-powered on selectivity. The warhead binds an LBD; nearest-neighbour NRs (esp. other orphan NRs) should be screened for pocket similarity / cross-binding. | ¢–$ |

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
| D4 | Off-target beyond paralogues (NR-family / proteome) | ❌ | See A4 — same gap from the ligand side. | ¢–$ |

## E. Degradation-specific (it is a degrader, not just a binder)
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| E1 | Ternary complex prediction (Boltz-2) | ✅ | | done |
| E2 | Ternary selectivity across paralogues | ✅ | F18. | done |
| E3 | Degradation geometry / surface-lysine accessibility / ubiquitination zone | 🟡 | `degradation_geometry` in report_ternary computes it; not yet written up as a first-class result with a lysine-accessibility readout. | ¢ |
| E4 | Linker **exit-vector** feasibility (does the warhead's solvent-exposed vector admit a CRBN linker?) | ❌ | Required to claim a *buildable* degrader vs an abstract binder. | ¢ |
| E5 | Ternary **cooperativity (α)** estimate | ❌ | | $ |
| E6 | E3-ligase choice (CRBN) rationale + **CRBN/E3 expression in EMC-relevant tissue** | ❌ | A degrader is only as good as ligase availability where the tumour is. | ¢ |
| E7 | Molecular-glue **neo-substrate off-target** risk (the thalidomide/IMiD lesson) | ❌ | CRBN-recruiting warheads risk degrading unintended neo-substrates (e.g. zinc-finger degrons). Worth an in-silico flag. | ¢–$ |

## F. Developability / ADMET (all cheap, all currently absent)
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| F1 | Physchem / **beyond-Rule-of-5** profile (MW, cLogP, TPSA, HBD/HBA, rot-bonds) | ❌ | Seconds of RDKit. PROTACs live in bRo5 space — quantify where the lead sits. | ¢ |
| F2 | Structural alerts / **PAINS** | ❌ | RDKit/`FilterCatalog`. Cheap credibility check. | ¢ |
| F3 | Synthetic accessibility (SA score) | 🟡 | May be partially captured in de-novo generation; **verify + report explicitly**. | ¢ |
| F4 | Permeability / solubility predictors | ❌ | | ¢ |
| F5 | hERG / CYP / reactive-metabolite liability flags | ❌ | Structure-based alerts (in-silico only). | ¢ |

## G. Biological rationale
| # | Stage | Status | Notes | Cost |
|---|-------|--------|-------|------|
| G1 | **H2 efficacy** — EMC fusion-dependency prior | ✅ | 4-pillar prior; honest floor = no direct LoF in an EMC line (dTAG is the wet-lab make-or-break). `nr4a3-emc-biology-evidence.md`. | done |
| G2 | **H1 safety** — paralogue redundancy / tolerability | 🟡→ | DepMap NR4A1/2/3 essentiality **(running)**; gnomAD LoF constraint + IMPC single-KO + HPA co-expression **(running)**. Closes the post-mitotic/tissue-tolerability hole DepMap can't. | ¢ |

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
2. **Broader selectivity beyond the two paralogues (A4 / D4)** — a "selective" claim tested against only NR4A1/2 is the single most exposed part of the thesis. Screen the nearest NR-superfamily LBD pockets.
3. **Degrader-completeness (E3/E4/E6/E7)** — linker exit-vector, lysine-accessibility write-up, E3/tissue rationale, neo-substrate risk. These are what make it a *degrader* result, not a *binder* result. Mostly free.
4. **Model-confidence honesty (A1)** — state pLDDT/PAE at the pocket explicitly. Free.
5. **The two queued GPU campaigns (C4/D2, A2 release run)** — already scoped; the expensive, decisive ones.

**Everything in tiers 1–4 is free or a single <$10 run and is currently missing or unwritten.** Closing them is what moves the paper from "a good binder story with a big FEP pending" to "a genuinely complete in-silico characterization."
