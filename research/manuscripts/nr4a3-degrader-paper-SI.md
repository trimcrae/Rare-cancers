# Supporting Information — In silico design of a paralogue-favoured ligand for a cryptic NR4A3 pocket

**Tristan D. McRae**

*Independent researcher.* Correspondence: trimcrae@gmail.com

<!-- EDITORIAL, NOT FOR SUBMISSION: this Supporting Information was split out of nr4a3-degrader-paper.md
in the 2026-07-10 "cut hard to the spine" restructure (see nr4a3-degrader-paper-review-response.md). It
holds the material demoted from the main-text spine: the 6,000-drug repurposing screen (was §2.5b), the
CRBN ternary + degradation-window detail (was §2.5 tail), the full selectivity-architecture + superfamily
liability screen (was §2.8 back half), the indication landscape / pan-NR4A CAR-T pole (was §3), the
lo_m0_NCCO lead-optimization FEP (was §3), and the deep safety-genetics essay (was §4). No scientific
claim, number, or caveat was altered in the move. Section/figure numbers are prefixed "S". All references
are in the main-text References section of nr4a3-degrader-paper.md unless noted here. -->

Section and figure numbers here are prefixed **S**. Cross-references of the form "§2.x/§3/§4/§5" point to
the **main text** (`nr4a3-degrader-paper.md`); "SI §Sx" points within this document. Figure/data paths
(`../modalities/...`) are unchanged from the main text.

## S1. At scale: a 6,000-drug marketed-library screen with an anti-target panel finds no repurposed selective binder
The §2.5 disqualification rests on a small set of known NR4A ChEMBL actives, inviting the objection that a
broader search would find an existing selective drug. We therefore ran the **entire Broad Drug Repurposing
Hub (~6,000 marketed/clinical compounds)** through the *same* funnel and receptors, and added an adversarial
**anti-target panel** as a new selectivity axis. Full provenance + tables:
[`../modalities/nr4a3-repurpose-decoy-blend.md`](../modalities/nr4a3-repurpose-decoy-blend.md).

*(1) The raw margin is non-specific at scale.* Docking-triaged to the strong tail (top-250, dG ≲ −8.4),
3-receptor-docked on the canonical frames, and single-snapshot-MM-GBSA'd, **97/250 (39 %)** score raw
`confirmed_selective` — matching the 38-drug decoy false-positive rate almost exactly, so the raw verdict is
noise at 250-drug scale, and only ~5.6 % clear the +13.12 decoy-null bar (not enriched over decoys).

*(2) Replicated de-noising leaves two paralogue-margin survivors.* Single 10-frame de-noising is **not
reproducible run-to-run** (AGI-5198 swung +16.4 vs +6.4 across passes; the within-run SD of one autocorrelated
trajectory understates the true uncertainty), so — as for `denovo_401`, which we held to the same bar
(+12.83 / +14.75 across independent passes) — we ran **three independent replicates** and took the between-run
mean − SD. Of the shortlist, only **SNX-5422** (HSP90 inhibitor; +17.56) and **AGI-5198** (IDH1 inhibitor; +9.41, n=4) survive the NR4A3-vs-paralogue margin (a striking demonstration of the need for replication: SNX-5422
had *collapsed* in the single pass). The pan-NR4A cell (balanced tri-engagement, for the SI §S4 ex-vivo CAR-T mode)
is populated by KB-SRC-4, flupentixol, AT-1015, CP-640186 — but see below.

*(3) The anti-target panel disqualifies all of them.* We docked the survivors into a 9-target panel — six
unrelated nuclear receptors (RXRα, PPARγ, ERα, AR, GR, VDR) plus the promiscuity sensors **PXR** (xenobiotic
receptor), CYP3A4, and serum albumin — with the identical smina protocol, and compared each drug's best
off-target ΔG to its NR4A3 ΔG (`antitarget_{panel,prep,dock,report}.py`). **Every survivor is promiscuous**:
each binds ≥1 off-target *more tightly* than NR4A3 (gap −0.3 to −5.7 kcal/mol) with 5–8 panel targets within
2 kcal and **PXR + HSA engaged within 2 kcal in every case** (AGI-5198 best-off −10.8 at PXR vs NR4A3 −8.4;
SNX-5422 −10.9 at PXR vs −8.5). As a positive control that the panel *discriminates* rather than merely
saturates, `denovo_401` through the same panel tops out at **−9.1 (VDR)** — 1.7–5 kcal weaker than any
repurposed survivor and not a PXR/HSA hit. **Conclusion:** the marketed-drug library contains no compound that
is both NR4A3-selective *and* clean against this 9-target counter-screen panel; its paralogue-margin
survivors each receive a more favourable docking score at ≥1 counter-screen target than at NR4A3 (a screen-level
observation from a 9-target panel, not a proteome-wide selectivity measurement). This
extends §2.5 from a small-set claim to a 6k-scale, promiscuity-controlled negative result — and is precisely
why a *de-novo* design (§2.6) is required. (The much-noted AGI-5198↔chondrosarcoma link is coincidental: it
engages the NR4A3 pocket but no better than half a dozen unrelated targets. Screening-grade throughout —
smina + endpoint MM-GBSA, no FEP.)

## S2. The CRBN ternary-complex model and the degradation window

*(Moved verbatim from the tail of main-text §2.5; the 2-sentence summary that replaces it in main points here.)*

Once a warhead SMILES exists, the NR4A3–PROTAC–E3 ternary-complex model (`nr4a3_ternary.py`,
Boltz-2) scores degradable-lysine geometry per paralogue. **This pipeline is validated on a positive
control:** predicting the CRBN + lenalidomide complex, Boltz-2 **seats the glutarimide in CRBN's
tri-tryptophan pocket** — closest heavy-atom approach 2.85 Å to W380 (3.4 Å to W386/W400), with high
confidence (ligand-iPTM 0.99) — recovering the experimentally known IMiD binding mode. This is a **necessary
sanity check, not a demonstration of generalization**: CRBN/IMiD is one of the most-deposited ligase
complexes in the PDB and is almost certainly in Boltz-2's training data, so recovering it is
memorization-consistent and says little about performance on an **AF2-modeled cryptic NR4A3 LBD** with a
**de-novo** warhead and a possibly different E3. **We nonetheless ran that step:**
we built a **representative `denovo_401`-PROTAC** (warhead–PEG2–succinyl–lenalidomide, RDKit-validated
C41H56N4O8, glutarimide intact) and predicted the **NR4A3/NR4A1/NR4A2-LBD + CRBN + PROTAC** ternaries. The
result is honest and instructive: **all three paralogues form a productive-geometry-proxy ternary** — the
PROTAC bridges the LBD and CRBN (2.5–3.1 Å each side) and each LBD presents an exposed lysine near the modeled
CRBN-facing interface (closest Lys-Nζ to the nearest CRBN heavy atom NR4A3 K195 3.12 Å, NR4A1 K53 2.34 Å,
NR4A2 K175 3.96 Å — a **CRBN-proximity proxy, not modeled ubiquitin-transfer geometry**) — with **comparable,
within-Boltz-noise confidence** (iptm 0.72/0.83/0.82). So for this representative linker the **ternary adds no
NR4A3 degradation-selectivity**: it does *not* "multiply" the binder's paralogue margin the way SI §S3 hoped;
degradation selectivity, if any, rests on the **binder** margin (denovo_401/111), with **linker/exit-vector
design** the (untested) lever that might introduce ternary selectivity. Caveats: one arbitrary linker; Boltz
gives a single ternary pose (not the productive-ensemble/cooperativity α that sets real degradation
selectivity); Lys-proximity is a CRBN-only proxy (no full CRL4^CRBN + E2~Ub). This is not a formality: the
binding-selectivity matrix is a **necessary but not sufficient** filter, because a degrader's actual
selectivity is set by the *ternary complex* — a non-selective binder can degrade selectively and a selective
binder can fail to degrade; the ternary result above shows the *converse risk* here (a selective binder whose
ternary is non-selective). **No molecule is synthesized; this is design prep.** Run instructions + program state:
[`../modalities/nr4a3-degrader-next-steps.md`](../modalities/nr4a3-degrader-next-steps.md).


**From ternary geometry to a degradation *window* (`nr4a3_degradation_model.py`).** A ternary pose is not yet a
degradation prediction. We therefore add the standard **three-body cooperative-equilibrium** layer (Douglass
2013; Gadd 2017) coupled to a steady-state synthesis/degradation balance, which converts binary affinities +
cooperativity α into the numbers that actually decide a degrader: **DC50, Dmax, and the hook effect**. Because
absolute affinities and α are exactly the quantities the current ABFE does **not** validate (the absolute
scale fails the T4L benchmark, §3; the initial three-replicate ABFE gives a *conditional receptor contrast*
only, and the NR4A2 λ-overlap repair pilot was run and classified a technical failure on the pre-registered
temporal-stability criterion (S7), leaving no gated NR4A2 ΔΔG — and MM-GBSA ΔG is likewise not a calibrated Kd), the
model is delivered honestly as a **mechanistic harness + sensitivity maps over α and binary Kd** that would
accept experimentally measured or validated ensemble-weighted affinities in future work, **not** a
point DC50 derived from the current raw ABFE absolutes — in an illustrative potent regime it reproduces the expected behaviour (DC50 425 → 16 nM as α 1 →
10, with a hook at high occupancy). Its purpose is twofold: (i) it makes the degrader's efficacy claim
*quantitative and falsifiable* rather than "a ternary forms," and (ii) it **is the analysis layer the FEP feeds** —
per-paralogue FEP Kd's drop straight in, and the NR4A3-vs-NR4A1/NR4A2 spread in the Kd-sensitivity map becomes
the predicted *degradation* selectivity, closing the binder→degradation-selectivity gap flagged above.

## S3. Selectivity architecture: the pocket is a selectivity hotspot, and a superfamily-wide pocket-liability screen

Treating "where should selectivity come from" as its own optimization (full analysis:
[`nr4a3-degrader-selectivity-architecture.md`](./nr4a3-degrader-selectivity-architecture.md)) yields a
computed result (not asserted) that **contextualizes — not contradicts — the binder campaign.** The
divergence table folded into main-text §2.4 establishes that the orthosteric cryptic pocket (the warhead
contacts) is the *most* paralogue-divergent zone of the LBD (70 % vs the ~43 % LBD-wide average); here we
develop what that implies for the selectivity architecture, and screen the liability across the whole NR
superfamily.

**The predicted ternary interface — now computed
on the real ternary complex rather than the earlier surface/PPI *proxy* (caveat closed) — is *also* paralogue-
divergent** (8/33 interface residues differ vs each paralogue, 6 vs both: E545, T563, Q570, S571, L576, E580,
V588…), and critically it is a **different surface from the pocket handles** (zero of the seven pocket handles
sit at the ternary interface). So the binder and the ternary would draw selectivity from **independent**
residue sets — the multiplicative budget is real, not double-counting one patch. This carries three design conclusions:

1. **Selectivity is a *multiplicative* budget** across binding × ternary × kinetics — the factors
   **compound** (binder *and* ternary *and* kinetics); none *replaces* another. A selective binder is
   therefore strictly valuable and **remains the program's primary goal** — `denovo_401`'s pocket
   selectivity is a **decoy-null-screened first factor** (it exceeds a same-tier multi-snapshot decoy null in
   its design frame, §2.7 — a foothold, not fully control-validated, since that null does not control the
   generative step), not a discardable bonus. The architecture's contribution is the *complementary* point:
   because that binder selectivity is **fragile** in this cryptic, least-druggable-of-three pocket (two
   survivors out of ~11 multi-snapshot-tested; §2.7), a *robust* degrader would ideally **add** ternary
   selectivity *on top of* the binder's — **but the ternary experiment has now been run (§2.5) and, for a
   representative `denovo_401`-PROTAC, does *not* add it** (all three paralogues form an equally productive
   ternary). So on current evidence the full budget rests **more heavily on the binder** than this architecture
   originally hoped: binder optimization must pursue **affinity, a productive linker exit vector, *and* the
   paralogue selectivity `denovo_401` already shows** (denovo_111 withdrawn as protonation-fragile, §2.7). **The ternary is not a *spent* lever, though —
   the interface-divergence analysis (the §2.4 divergence table) shows the induced NR4A3–CRBN interface carries a
   paralogue-divergent patch (6 residues divergent vs both, E545/T563/Q570/S571/L576/E580/V588…) on a surface
   distinct from the pocket handles.** So ternary selectivity is **structurally available but not yet realized**:
   the *representative* linker did not exploit it, but a linker **designed to place the induced interface against
   that divergent patch** could, in principle, add a *second, independent* selectivity factor — the doubly-
   selective degrader is a rational goal, not a dead end. The honest limit is tooling: single-pose Boltz can
   flag that the divergent patch *exists at the interface*, but it cannot **optimize or validate** ternary
   selectivity (that needs ternary-ensemble/cooperativity scoring — a method-watch item), so this is an
   engineerable-but-unvalidated lever. The "binding selectivity ≠ degradation selectivity" point (caveat 5)
   still holds: here a selective binder gave a non-selective ternary *for this linker*, with a divergent
   interface patch as the route to fix that.
2. **Paralogue selectivity then compounds per-paralogue via matched levers — but the ternary is now a *tested,
   negative* lever, not a hoped-for one:** NR4A1 (the AML-safety-net, mandatory) — `denovo_401` discriminates it
   at the binder level (ΔG NR4A3 −38.18 vs NR4A1 −22.98, §2.7), but the **ternary does *not* multiply that
   margin** for the representative PROTAC (§2.5: NR4A1 forms an equally productive ternary), so NR4A1
   selectivity currently rests on the **binder** — plus linker engineering toward the divergent interface patch
   the analysis above identifies (E545/T563/G573/L576/E580/V588 all differ NR4A3→NR4A1), an available-but-
   untested route; NR4A2 (the
   molecularly hardest case — I531 is NR4A3=NR4A2-identical, §2.4) is topped up from **pharmacokinetics /
   CNS-exclusion**, on the *assumption* that NR4A2/Nurr1 toxicity is CNS-localized (Nurr1's canonical role is
   dopaminergic) and EMC is a peripheral sarcoma — **an assumption not yet verified**: a systematic check of
   NR4A2 single-loss tolerability (MGI/IMPC single-KO phenotypes) did not confirm it (SI §S6 safety note).
3. **Fusion-vs-wild-type selectivity is unobtainable from the degrader at any stage** (the warhead binds a
   LBD identical in fusion and wild-type, and the ternary forms at that LBD, nowhere near the N-terminal
   fusion partner). It is the **ASO's** job (RNA-level junction targeting); the degrader's honest scope is
   paralogue selectivity + accepted wild-type-NR4A3 loss, **not** tumour-exclusivity. Effort spent making
   the degrader fusion-selective is effort misallocated.

(Caveat — now largely resolved: the "surface/PPI proxy" row used pocket-lining residues across all cavities as
a stand-in for the true E3-facing interface. The real NR4A3–CRBN interface has since been computed on the
ternary (the ternary-interface row of the §2.4 divergence table; §2.5) and is paralogue-divergent (8/33 vs each, 6 vs both), confirming the
binder-vs-ternary comparison is not double-counting one patch. Remaining limits: it is a single-pose,
single-linker interface — the divergent-patch set is expected to shift with linker/exit-vector choice — so the
*specific* residues are indicative, not fixed.)

**Beyond the two paralogues — a superfamily-wide pocket-liability screen (A4/D4).** A selectivity claim tested
only against NR4A1/2 is under-powered: the human nuclear-receptor (NR) superfamily is ~48 proteins that share
the LBD fold, so a *non-paralogue* NR could in principle present a pocket resembling NR4A3's. We therefore
mapped the ten warhead-pocket residues (Q92570 numbering) onto **every reviewed human NR** (n = 47; UniProt
family query, no hardcoded accessions; BLOSUM62 global alignment — the same core as the resistance map, §3) and
scored pocket-residue identity, gating on overall LBD-alignment identity as a **mapping-confidence** axis
(`nr4a_superfamily_selectivity.py` → `nr4a-superfamily-selectivity.json`). The two paralogues behave as
positive controls must — they are the **only** NRs combining pocket coincidence with high-confidence alignment
(NR4A2 4/10 pocket residues at overall identity 0.58; NR4A1 3/10 at 0.51), and NR4A2's one shared *handle* is
I531, the NR4A3=NR4A2-identical position already flagged as the hardest case (§2.4). The result is reported at
its true, unflattering weight:

| NR (confidence-gated, overall id ≥ 0.30) | pocket id | shared residues (Q92570 #) | on selectivity handles |
|---|---|---|---|
| NR4A2 (control) | 4/10 | 411, 481, 485, 531 | 531 (I531) |
| NR4A1 (control) | 3/10 | 411, 481, 485 | none (conserved core only) |
| **NR3C2 / MR** | 3/10 | 406, 407, 485 | **406, 407** |
| **AR** | 3/10 | 407, 410, 485 | **407, 410** |
| PGR | 1/10 | 485 | none |

**Supplementary Figure S3** ([`../modalities/nr4a3-figS3.png`](../modalities/nr4a3-figS3.png); generated by
`nr4a3_journal_figures.py`, read live from `nr4a-superfamily-selectivity.json`). Warhead-pocket residue
identity (y) vs overall NR4A3-LBD alignment identity (x, the mapping-confidence axis) across all 47 reviewed
human NRs. Only five receptors clear the confidence gate (overall identity ≥ 0.30): the paralogue positive
controls NR4A2/NR4A1, the two flagged oxosteroid near-neighbours MR (NR3C2) and AR — each overlapping two
selectivity handles — and PGR. Receptors at high apparent pocket identity but low overall identity (THRB,
THRA, RORA…) are correctly down-weighted as distant-homology mis-registration. The output is a prioritised
shortlist (AR/MR need an energetic cross-binding check), not a selectivity clearance.

Two oxosteroid receptors — the **mineralocorticoid receptor (NR3C2)** and the **androgen receptor (AR)** —
coincide with the NR4A3 pocket at the same 3/10 level as NR4A1 and, unlike NR4A1 (which matches only the
conserved structural core 411/481/485), each overlaps **two selectivity handles** (MR 406/407; AR 407/410).
They **cannot be dismissed on sequence alone.** Three facts bound the concern without waving it away: they miss
most of the pocket, including the core residues 411/481 that even the paralogues retain; their overall LBD
identity (~0.32) sits only marginally above the confidence floor, so the handle "matches" carry genuine
alignment uncertainty (a distant global alignment can mis-register a two-residue run); and — decisively — the
warhead binds a **cryptic** pocket, an *induced* NR4A3 conformation that AR/MR (each with its own well-formed
orthosteric pocket) are not shown to reproduce. This is precisely the **necessary-not-sufficient** logic the
screen was built to expose: pocket-residue sequence resemblance **prioritises**, it does not **certify**. The
honest output is a *shortlist, not a clearance* — **AR and MR are the NRs an energetic cross-binding check
(docking/FEP into their LBDs plus a cryptic-pocket-formation test) must clear** before the selectivity claim
extends past the paralogues; off-target AR activity is in any case a routine developability counter-screen. The
other 43 NRs either fall well below the paralogues on pocket identity or coincide only at low homology where the
mapping is unreliable. **Net:** at superfamily scale the primary selectivity liability remains the two
paralogues we already address, with MR/AR named as the sole sequence-level non-paralogue follow-ups — a
breadth statement the two-paralogue comparison could not make.

## S4. Indication landscape — a programmable selectivity matrix (EMC is the entry point, not the endpoint)
Detail + references: [`nr4a3-degrader-broader-indications.md`](./nr4a3-degrader-broader-indications.md).
The family-wide ensembles (§2.5) let a degrader be designed for a chosen NR4A *combination*. A cell of
that matrix is a real application only where the disease wants those paralogue(s) **degraded** (direction
matters: degrading neuroprotective Nurr1/NR4A2 in Parkinson's would be the *wrong* direction, so most
single-paralogue cells are not degrader indications) — and some combinations are actively harmful. So the
matrix has three kinds of cell:

**Lead — NR4A3-selective (the validated path):**
1. **EMC** — EWSR1/TAF15::NR4A3 fusion; clean single-driver proof-of-concept.
2. **Acinic cell carcinoma (AciCC) of the salivary glands** — driven by **NR4A3 over-expression via
   enhancer hijacking** (Haller, *Nat Commun* 2019; cooperates with MYB, Lee 2020). NR4A3 is the diagnostic driver;
   a selective degrader removes it directly. AciCC is the **third most common malignant salivary-gland
   tumour** (after mucoepidermoid and adenoid cystic carcinoma; ≈6–7 % of salivary neoplasms [Khan 2023]),
   giving an annual incidence on the order of ~0.1 per 100,000 (derived from the ≈1.1 per 100,000
   salivary-gland-malignancy incidence Khan 2023 reports), whereas EMC is **ultra-rare** (<1 per 1,000,000
   per year [Stacchiotti 2020]) — so the
   same selective agent addresses a materially larger population through AciCC. (Both are rare; the
   comparison is order-of-magnitude, not a precise ratio.)
3. **Other NR4A3-rearranged sarcomas** — the EMC fusion-variant spectrum.

**Second design mode — pan-NR4A (a distinct molecule, not a contingency):** reversing CD8⁺ T-cell
exhaustion (NR4A-deficient CAR-T cells control solid tumours better; Chen, *Nature* 2019) **requires
degrading all three NR4As**. This is the *opposite* selectivity profile, deliberately designed for from
the conserved pocket residues, and scoped to **ex-vivo / transient** use (CAR-T manufacturing) so the
systemic-toxicity bound below does not apply — indeed ex-vivo use *removes* the AML/CNS toxicity argument
that mandates selectivity for the systemic lead, so the pan agent is the strictly *easier* design (no
selectivity budget to satisfy). **This mode is demonstrated, not asserted, by reading out the *pan-NR4A
cell* of the same criterion-matched family matrix** ([`../modalities/nr4a3-pan-readout.json`](../modalities/nr4a3-pan-readout.json)):
(i) the repurposed library populates the pan-NR4A cell (3 members), including a ChEMBL NR4A active that is
**essentially equipotent across all three opened pockets** (dG NR4A3/NR4A1/NR4A2 = −8.40/−8.41/−8.80,
|margin| ≤ 0.4 kcal/mol) — the balanced tri-paralogue engagement this mode wants; and (ii), more tellingly,
the de-novo funnel's own **`confirmed_nonselective`** rejects — the pile discarded *for* the selective
programme — include **two gate-developable de-novo molecules in the pan-NR4A cell** (`denovo_106`, QED 0.78 /
SA 3.8 / 5 handle contacts, the lead; and `denovo_86`, QED 0.68 / SA 3.9), each engaging all three
criterion-matched opened pockets. So **one cryptic-pocket generative campaign yields both poles of the NR4A
selectivity axis at once** — NR4A3-selective warheads for the systemic cancer lead, and, in its non-selective
by-catch, pan-NR4A binders for the ex-vivo CAR-T mode. We hold both poles to the *same honest weight*: these
are docking-tier screening priors (not affinities, no molecule synthesized), and a manual RDKit triage
(beyond the automated gate, which none of them trips for PAINS/BRENK) flags the same class of generative-model
liabilities the selective pole's `denovo_15` carries — a reactive diene/alkylidene in `denovo_106`, an
N,O-acetal plus high logP in `denovo_86` — so each is a pan **chemotype/pose hypothesis to redesign**, not a
developable molecule ([`../modalities/nr4a3-pan-readout.json`](../modalities/nr4a3-pan-readout.json)). The
durable, load-bearing claim is therefore the *framework*: one funnel produces matter that engages the
conserved pocket across all three paralogues.

**We then made pan-NR4A the explicit design *objective* (not a reject-pile readout), and it is the stronger
result.** A second generative campaign ranked candidates by **conserved-core contact** (residues 411/481/485,
the paralogue-invariant pocket residues) instead of the divergent handles, then docked the top developable
generations into the three opened pockets. Designing *for* the conserved core **flips the census**: the
pan-NR4A cell becomes the **dominant** outcome (**4 of 7 docked candidates pan-NR4A, and *zero*
NR4A3-selective** — the mirror image of the selective campaign, where pan was the by-catch;
[`../modalities/nr4a3-pan-readout.json`](../modalities/nr4a3-pan-readout.json)). And it yields a **clean**
lead where the by-catch had none: **`denovo_9`** (a fluoro-anilide / salicylate-ether; docking dG
NR4A3/NR4A1/NR4A2 = −7.69/−7.31/−7.40) engages **all three conserved-core residues (3/3)** and is
**PAINS/BRENK/NIH-clean with no reactive/unstable liability on manual RDKit triage** (MW 335, logP 1.74,
QED 0.64). So the same cryptic-pocket framework, retargeted from the divergent handles to the conserved core,
**designs a pan-NR4A binder on demand** — the CAR-T pole is now a *designed* result, not by-catch.

**Endpoint-energy re-scoring confirms tri-paralogue engagement (one tier above docking).** We ran the same
endpoint tier used for the selective lead on `denovo_9` — **short-trajectory multi-frame endpoint MM-GBSA**
(10 frames from one short GB-implicit trajectory, no entropy, no fully-equilibrated receptor ensemble):
**all three paralogue ΔG are strongly
favorable — NR4A3/NR4A1/NR4A2 = −28.3 / −23.9 / −20.7 kcal/mol** (amber14/GBn2, 10-frame average), so the
endpoint tier **confirms `denovo_9` binds all three** — the core pan requirement, now shown above docking.
We report the selectivity read honestly: the point estimate leans NR4A3 (margin +4.44 kcal/mol, raw verdict
"confirmed_selective"), **but this lean is *not* robust** — the margin is smaller than its own SD (5.47;
margin − SD = −1.03 < 0), failing the same margin − SD > 0 bar that qualifies the selective lead `denovo_401`
(+12.83 ± 2.98), and sitting far below the single-snapshot decoy null (+13.1, §2.6). So there is **no
statistically supported paralogue preference** — consistent with balanced pan engagement, not selectivity.
Net: `denovo_9` is a **confirmed tri-paralogue (pan) binder** at the endpoint-energy tier with no
de-noising-robust selectivity — the pan profile, honestly bounded (short-trajectory multi-frame endpoint
MM-GBSA — one short GB-implicit trajectory, no entropy, no equilibrated ensemble; magnitudes read for
engagement/direction, not absolute Kd; no molecule synthesized). A pan-pole
selectivity FEP was not warranted (the pan objective is engages-all-three, which this already supports, not a
robust margin).

**The whole docking-tier pan census survives endpoint re-scoring in the pan-relevant sense.** Rather than
endpoint-confirm only the lead, we ran the same multi-snapshot MM-GBSA on **all four** pan-cell candidates
(`denovo_9/79/61/125`). Two results, both pan-favourable. *(i) "Engages all three" holds 4/4:* every candidate
binds all three paralogues favourably at the endpoint tier (ΔG spans −18 to −32 kcal/mol; weakest paralogue
leg ≥ −18), and **none re-scores as NR4A3-selective** (census: 3 `confirmed_nonselective`, 1 `reversed`, 0
`confirmed_selective`) — "nonselective"/"reversed" are the *wanted* labels here, meaning no NR4A3 preference.
*(ii) The margins are demonstrably noise:* `denovo_9`'s NR4A3 margin **flips sign between the two independent
runs** (+4.44 above → **−4.28** in the census run, each with SD ~4–5 spanning zero), the cleanest possible
confirmation that its apparent lean is not a real preference. So the docking-tier "pan cell" calls survive
endpoint scoring where it counts (tri-paralogue engagement), while the docking "balanced-margin" character
loosens honestly to "non-selective within noise." This is a specificity-style check on the pan pole,
symmetric with the decoy/de-noising controls the selective pole receives.

**A pan *binder* implies a pan *degrader* — the same ternary result carries the opposite sign here.** The
CRBN–PROTAC ternary analysis (§2.5) found that a representative degrader forms **productive-geometry
ternaries with all three paralogues at comparable confidence** — i.e. the ternary step adds *no* paralogue
selectivity. For the systemic selective lead that is a *liability* (degradation selectivity has to come from
the binder, not the ternary). For the pan pole it is exactly the **wanted** property: a non-selective ternary
means the geometry to degrade *all three* NR4As is feasible, so a pan binder (`denovo_9`) is expected to yield
a pan **degrader**, not merely a pan binder. This is a re-reading of work already done (a single-pose CRBN
proxy on a `denovo_401`-linker, not a `denovo_9`-specific ternary or a full degradation simulation), so it is
an inference at that weight — but it needs no new computation, and it makes the CAR-T pole a *degradation*
story rather than only a binding one.

**Figure S4.** The programmable NR4A selectivity axis: one cryptic-pocket framework tuned from
NR4A3-selective (engaging the divergent handles; lead `denovo_401`) to pan-NR4A (engaging the conserved core
411/481/485; lead `denovo_9`, docking dG −7.69/−7.31/−7.40), with the AML NR4A1+NR4A3 anti-target as the
forbidden cell the matrix designs away from. Both poles are docking-tier priors; no molecule synthesized.
Full figure: [`../modalities/nr4a3-fig6.png`](../modalities/nr4a3-fig6.png) (rendered by `nr4a3_journal_figures.py`).

**Anti-target — NR4A1+NR4A3 (design *away* from):** NR4A1/NR4A3 are myeloid **tumour suppressors** —
combined loss causes AML (Mullican, *Nat Med* 2007); NR4A3 is also tumour-suppressive in HCC/breast/
lymphoma (Safe & Karki 2021). This cell is a liability, not an indication; the matrix is explicitly used
to *avoid* it (and is *why* NR4A1-sparing selectivity (§2.4) is mandatory for the systemic lead). Showing
the method can design **into** NR4A3-only and **away from** NR4A1+NR4A3 is itself a safety-design result.

**The pan-NR4A / CAR-T pole is bounded separately, and more tightly.** The second design pole (SI §S4, above) makes two
claims that must not be over-read. (i) **Chemical-feasibility only, not function.** We show the framework can
*design a pan-NR4A binder* (the conserved-core-designed campaign is pan-dominant with a clean lead, `denovo_9`,
whose tri-paralogue engagement is confirmed one tier above docking by endpoint MM-GBSA — all three ΔG
favorable — though these remain screening priors, not affinities, and no molecule is synthesized); we do
**not** show it reverses T-cell exhaustion — that endpoint (restored effector function,
persistence, tumour control) is the wet-lab claim owned by the genetic triple-KO literature (Chen 2019) and
is future work, not a result here. The pan pole rides on the same druggable-pocket evidence as the selective
pole, but its *application* is a hypothesis. (ii) **Ex-vivo removes the systemic-toxicity bound, but adds its
own parameter.** Transient ex-vivo dosing during manufacturing sidesteps the in-vivo AML/CNS argument that
mandates selectivity — but degradation *persists after washout* (its virtue as a reprogramming pulse), so
residual pan-NR4A suppression in the infused product is a real dose/exposure/washout variable to characterise,
not a solved point. Neither is a claim the in-silico work settles; both are flagged so the CAR-T framing is a
*reach-extending, honestly-bounded* second mode, not an overclaim.

## S5. Lead-optimization cross-check (`lo_m0_NCCO`) — an FEP tie, not an improvement

**Lead-optimization cross-check (`lo_m0_NCCO` = `denovo_401` + ortho-acetamido) — an FEP tie, not an improvement.** The single
scaffold-decorated variant that multi-snapshot MM-GBSA had nominated as a tighter, still-selective lead (`lo_m0_NCCO`, projected
~+5.5 kcal/mol *tighter* than `denovo_401` by MM-GBSA) was put through the **identical** engine, opened-NR4A3 frame, and
Boresch/double-decoupling scheme, as an affinity-grade check on that MM-GBSA ranking. One converged replicate returns
per-receptor raw-engine ΔG_bind = **+2.85 ± 0.28** (NR4A3), **+9.57 ± 0.32** (NR4A1), **+8.27 ± 0.50** (NR4A2) →
ΔΔG(NR4A3 − NR4A1) = **−6.7** and ΔΔG(NR4A3 − NR4A2) = **−5.4** kcal/mol (both favour NR4A3; the NR4A2 leg's reduction
required the robust MBAR solver on marginal window overlap). Every one of these lands **within statistical noise of
`denovo_401`** (raw-engine NR4A3 +2.6; NR4A1 +9.5; NR4A2 +8.1; ΔΔG −6.9 / −5.5): the ortho-acetamido decoration is
**affinity- and selectivity-neutral at ABFE grade** — free
energy does **not** reproduce the MM-GBSA-predicted tightening, a concrete instance of the MM-GBSA absolute scale over-ranking a
sub-kcal difference that ABFE declines to confirm. `denovo_401` therefore **remains the program's strongest candidate**;
`lo_m0_NCCO` is a validated *equal*, not an advance. (Caveats favour reading this as a tie rather than a regression: the
`lo_m0_NCCO` leg ran at the workflow-default **1 ns/window, n_iter = 1000** — half `denovo_401`'s 2 ns/window sampling — is a
single replicate, and required the robust MBAR solver on marginal window overlap; sampling-matched, its absolute would be expected
only to *fall toward or below* `denovo_401`'s, not rise above it, so the "no improvement over 401" reading is the conservative one.)

## S6. Safety and tolerability rationale — stated at its true (limited) weight

**Safety/tolerability rationale — stated at its true (limited) weight (verified 2026-07-02,
[`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md)).** The premise that NR4A3-selective
degradation is tolerable "because NR4A1/2 do the same jobs" is **only partially evidenced and must not be
overstated**. What is verified (now *quantified*, 2026-07-02 direct database queries): (i) the **whole NR4A
family is non-essential in dividing cells** — DepMap CRISPR across n=1178 lines gives NR4A3 gene effect
**+0.023 with 0/1178 lines dependent**, NR4A1 −0.115 (0.5 %), NR4A2 −0.05 (0.3 %) — so proliferating cells,
tumour included, tolerate single-NR4A loss (caveat — no DepMap line is EMC); (ii) NR4A1↔NR4A3 are **functionally
redundant tumour suppressors *in the myeloid compartment*** (combined *Nr4a1;Nr4a3* loss causes AML while single
nulls do not — Mullican 2007 [PMID 17515897]; Blood 2018 [PMID 29343483]) — but that specific redundancy **is**
the AML anti-target, i.e. it is *why* NR4A1-sparing is mandatory, **not** a general safety guarantee; (iii)
NR4A1 and NR4A3 are **broadly co-expressed** (Human Protein Atlas: both "low tissue specificity," detected across
most tissues), making paralogue buffering plausible outside the CNS, whereas NR4A2 is CNS/"tissue-enhanced."
**★ An honest brake the data now force us to state:** human germline genetics says NR4A3 loss is **constrained,
not free** — gnomAD scores NR4A3 LoF-constrained by pLI (**0.9999**), though its **LOEUF (0.37) sits just
*above* the conventional LoF-intolerant threshold of 0.35**, i.e. borderline (13 observed vs 55.6 expected
LoF variants); NR4A2 is intolerant on both metrics (pLI 1.0, LOEUF **0.094**), and only NR4A1 is clearly
LoF-tolerant (pLI 0.002, LOEUF 0.71). This does **not** contradict the DepMap
dispensability — it localizes NR4A3's essentiality to a **developmental / tissue-specific** context rather than
proliferation — but it **invalidates the glib "dispensable ⇒ safe" inference** and makes **NR4A2-sparing a
safety requirement** (most-constrained *and* CNS-enriched paralogue), not merely an efficacy nicety.

**Supplementary Figure S5** ([`../modalities/nr4a3-figS4.png`](../modalities/nr4a3-figS4.png); generated
by `nr4a3_journal_figures.py` from `nr4a-safety-genetics.json` (gnomAD) + the SI §S6 DepMap values). The
NR4A paralogues plotted on two orthogonal safety axes: DepMap CRISPR gene effect (proliferative essentiality;
all three are non-essential, NR4A3 0/1178 lines dependent) vs gnomAD LOEUF (germline LoF constraint). NR4A2
sits well *below* the LoF-intolerant line (LOEUF 0.094) and NR4A3 sits just *above* it (LOEUF 0.37,
borderline; pLI-intolerant but LOEUF-tolerant) despite both being dispensable for proliferation —
the honest point that "dispensable ⇒ safe" is invalid, and that NR4A2 (most constrained + CNS-enriched) is a
sparing requirement. Constraint reflects reproductive fitness, not adult drug-tolerability — a supporting
datum, not proof.

What
remains **not** established (assumption, not fact): adult pan-tissue *transient-knockdown* tolerability, and
individual **mouse single-KO phenotypes** — an IMPC query returned **no phenotyped KO** for any of the three, so
the Nurr1-single-loss-is-CNS-confined assumption is **still unconfirmed** (MGI is the remaining follow-up).
Net: the safety case rests on quantified proliferative-compartment dispensability + demonstrated *myeloid*
redundancy + broad NR4A1/NR4A3 co-expression + mechanistic plausibility + PK restriction — a **materially
stronger and more honest** basis than before, with its residual risk now **specifically located**
(developmental / CNS, and NR4A2-sparing-dependent) rather than vaguely gestured at.

## S7. ABFE diagnostics — per-replicate ΔG, λ-overlap, ESS, convergence (review comment 17/18)
Full free-energy diagnostics for the three-replicate selectivity ABFE (§3), computed directly from the
per-window reduced potentials (the engine's `window_XX.jsonl` output; ~13k files in the run bucket, deposited
to the Zenodo archive; the derived diagnostics figures + JSON are committed in `results/nr4a3-abfe/diagnostics/`
via `nr4a3_abfe_diagnostics.py`). Each leg is 12 λ-windows × 2000 iterations.

**Per-replicate paired result (the review's "show every replicate").** Raw-engine ΔG_bind (kcal/mol) and the
NR4A3-vs-paralogue ΔΔG per replicate:

| replicate | NR4A3 | NR4A1 | NR4A2 | ΔΔG(3−1) | ΔΔG(3−2) |
|---|---|---|---|---|---|
| r1 | +2.61 | +9.51 | +8.08 | **−6.90** | **−5.48** |
| r2 | +5.12 | +7.98 | +9.33 | **−2.85** | **−4.20** |
| r3 | +2.83 | +7.36 | +8.10 | **−4.53** | **−5.26** |
| **mean ± SD** | +3.52 ± 1.39 | +8.28 ± 1.11 | +8.50 ± 0.71 | **−4.76 ± 2.03** | **−4.98 ± 0.68** |

The selectivity **direction is unanimous** across all three replicates for both contrasts. **Small-n
statistics (n = 3, 2 dof) — reported as *t*-intervals, not a Gaussian σ, which n = 3 does not support:** the
95% *t*-interval is **[−9.80, +0.28] kcal/mol for ΔΔG(3−1)** — unanimous in direction but **not resolved from
zero** — and **[−6.67, −3.29] kcal/mol for ΔΔG(3−2)** — **resolved below zero**. The wider NR4A1
SD is driven entirely by r2, whose NR4A3 leg sampled ~2.5 kcal/mol weaker (+5.12 vs +2.6/+2.8) — visible in
the per-replicate values, and the reason the NR4A2 contrast (SD 0.68) is tighter than NR4A1 (SD 2.03).

**Component decomposition (review comment 7 — where the ΔΔG comes from).** Each ΔG_bind is
ΔG_bind,X = ΔG_solv − ΔG_cplx,X − SSC_X, where the ligand-in-water **solvent (decoupling) leg is literally
shared** across the three receptors within a replicate (same ligand, no receptor), and SSC_X is the analytic
Boresch standard-state correction. The per-leg finished ΔG values (kcal/mol; MBAR at full sampling) are:

| replicate | ΔG_solv (shared) | ΔG_cplx,NR4A3 | ΔG_cplx,NR4A1 | ΔG_cplx,NR4A2 |
|---|---|---|---|---|
| r1 | 23.13 | 29.31 | 22.19 | 23.61 |
| r2 | 23.30 | 26.97 | 23.89 | 22.53 |
| r3 | 22.91 | 28.86 | 24.12 | 23.37 |

The **SSC is per-receptor and deterministic** (it depends only on the restraint geometry/force constants, not
sampling): SSC_NR4A3 = **−8.79**, SSC_NR4A1 = **−8.57**, SSC_NR4A2 = **−8.56** kcal/mol — **identical to two
decimals across all three replicates**, as an analytic correction should be (Boresch anchor atoms are defined
per receptor in `nr4a3_abfe.py`; the small SSC differences reflect the slightly different anchor geometries
across receptors). Two consequences are now explicit rather than asserted. **(i) The shared solvent leg
cancels exactly:** ΔΔG(3−X) = −ΔG_cplx,3 + ΔG_cplx,X − SSC_3 + SSC_X, i.e. the ΔΔG is the **complex-leg
difference plus a small constant SSC offset** (SSC_1−SSC_3 = +0.22; SSC_2−SSC_3 = +0.23) — ΔG_solv drops out
identically, so it contributes **zero** to the contrast or its variance. **(ii) All run-to-run ΔΔG scatter
lives in the complex legs:** ΔG_cplx,NR4A3 varies 29.31/26.97/28.86 across r1/r2/r3 (r2 the weak outlier),
while SSC and ΔG_solv are effectively fixed — so the between-replicate SD is a genuine complex-leg sampling
variance, and the smaller NR4A2-contrast SD reflects lower observed complex-leg scatter for that pair, **not**
demonstrated cancellation of systematic complex-leg error.

**Consistency with §3 (reproducibility check).** The diagnostics recompute ΔG_bind from the raw reduced
potentials and reproduce the §3 values to within ≤0.03 kcal/mol on every mean and SD (e.g. NR4A3 3.52 vs 3.5;
NR4A1 8.28 vs 8.3) — i.e. the §3 reduction is faithfully reproducible from the archived data.

**λ-overlap.** MBAR nearest-neighbour overlap is healthy across most windows (adjacent overlaps ≈0.20–0.26,
a well-behaved near-tridiagonal overlap matrix), **but drops to a minimum adjacent overlap of 0.003** at one
window pair in the complex-NR4A2 leg (and ≈0.01 in a few other complex legs) — a **locally under-overlapped
region** where MBAR interpolates across a gap in the **complex-NR4A2** leg specifically. Because
**ΔΔG(NR4A3 − NR4A2) = −ΔG_cplx,3 + ΔG_cplx,2 − SSC_3 + SSC_2**, an error in the NR4A2 complex leg propagates
**directly into the NR4A3–NR4A2 contrast** — it is receptor-specific and does **not** cancel via the shared
solvent leg. This window pair therefore **directly limits confidence in the NR4A3–NR4A2 ΔΔG (not only the
absolute legs)**; the −4.98 ± 0.68 NR4A2 contrast is an **initial estimate held provisional** until the
λ-repair (add windows at that decoupling endpoint and re-reduce) lands. (What *does* cancel in the ΔΔG is the
shared solvent leg and any common charge/protonation error — not system-dependent complex-leg pathologies like
this one.) Per-leg overlap matrices, effective
sample sizes, and forward/reverse convergence traces are in `results/nr4a3-abfe/diagnostics/`
(`overlap_*.png`, `ess_*.png`, `convergence_*.png`).

**λ-overlap repair pilot — outcome (pre-registered; technical failure).** The repair was pre-registered before
the dense runs completed (`research/modalities/nr4a3-abfe-repair-prereg.md`) to fix the stopping rule,
acceptance criteria, statistics and promotion terminology in advance. A dense **16-window** schedule (four
added windows in the soft-core endpoint region) was run for the complex-NR4A2 leg as a single technical pilot,
replicate **r1** (S3 tag `nr4a3-abfe-nr4a2rep-r1`). *Provenance/completeness correction:* the pilot's endpoint
window 15 was initially incomplete (1000 of the target 2000 iterations) while a job had reported `Completed`;
this was detected by re-gating against the actual per-window S3 counts (a SageMaker `Completed` status means
only that the container exited 0, not that every window reached its target `n_iter`), the leg was carried to
completion (**all 16 windows at 2000 iterations**), and the target `n_iter` is now recorded in each leg's
`meta.json` so the completeness check has an explicit reference. On the completed leg the pre-registered
technical-validity gate (`abfe_repair_gate.py`, prereg §2) returned: **sampling-completeness, schedule
identity, data integrity, connected MBAR overlap (min adjacent 0.085, up from 0.003), ESS (≥ 50 independent
samples/state; observed autocorrelation-ESS ≈ 570–620) and the plateau sub-check all PASS**, but the
**temporal-stability criterion FAILED** — the full-versus-second-half ΔG difference was **1.147 kcal/mol
against the pre-registered 1.0 kcal/mol limit** (ΔG_full 21.85, ΔG_second-half 20.71). Completing window 15
improved this from 1.36 to 1.147 (more sampling moved it the right way, but not below the limit). The pilot is
therefore **classified as a technical failure**, and **no gated NR4A2 selectivity ΔΔG is reported** from the
repaired leg; the ΔG_full/ΔG_second-half values are retained only as quality-control diagnostics, not as a
validated binding or selectivity result. Per the pre-registration the sole sanctioned extra sampling is
ESS-triggered (ESS passed), so a convergence-triggered extension would be outcome-contingent optional sampling
and is **not** a continuation under this gate; the error-bar replicates r2/r3 are **not** unlocked, and the
standard-schedule −4.98 ± 0.68 contrast is **not** upgraded. Any later 4000-iteration run may be conducted
**only as a separately declared exploratory method diagnostic** (fixed total iterations, no intermediate
looks, identical estimator/equilibration/overlap/convergence/plateau definitions and software version) that
**cannot** change r1 from FAIL to PASS, unlock r2/r3, be described as the pre-registered pilot, or support a
confirmatory selectivity claim — a favourable exploratory result could only motivate a newly pre-registered
protocol or fresh pilot. **This outcome concerns the reliability of this ABFE protocol for the NR4A2 leg under
the pre-registered sampling; it does not establish that `denovo_401` is nonselective.** *Reproducibility
handles:* gate re-run GitHub Actions `run_id` 29190987163; the completeness guard + `meta.json` `n_iter`
recording were added in commit `3f6e3c9`, a procedural-integrity improvement that **did not alter the
convergence threshold** (the 1.0 kcal/mol limit is unchanged from the pre-registration).

## S8. Single-snapshot de-novo archaeology — the falsification record (not carried in the main text)

The main text collapses the early single-snapshot de-novo screening to one sentence (it was non-specific and
no nomination was accepted); the per-molecule forensic detail is preserved here as the falsification record.

**The three single-snapshot `confirmed_selective` hits, and why none was accepted.** The first pass docked the
top-20 generations into the NR4A3-release / NR4A1 / NR4A2 pockets and MM-GBSA-rescored all 20; three came back
`confirmed_selective` with none reversing (census: confirmed_selective 3 · rescued 7 · weakened 1 ·
confirmed_nonselective 9 · reversed 0). Medicinal-chemistry triage (RDKit, 2026-06-29) then split them into
*strong-but-artifactual* and *clean-but-weak*, with **none simultaneously chemically viable and a strong
selective binder** — the characteristic behaviour of a pretrained pocket-conditioned diffusion model
(DiffSBDD) with no stability/synthesizability term in its objective:

- **`denovo_15`** — SMILES `C=C(CC1=CC=C(NC(=O)O)C1)[C@H]1C=C2C(=NC1)OC[C@H](C)[C@@H]2C`; QED 0.774, SAscore
  **5.08 (above the campaign's ≤4.5 cut)**, contacts 4/5 handles; docking margin +1.0, single-snapshot MM-GBSA
  margin +10.7 kcal/mol (magnitude inflated by the single-snapshot approximation). **Liabilities:** a carbamic
  acid (`NC(=O)O`, hydrolytically unstable), a 1,3-cyclopentadiene (reactive diene), an imine, an exocyclic
  alkene, and no aromatic ring — optimised to fit/score, not to be stable or makeable. Read as a chemotype/pose
  hypothesis to be re-designed, not a developable molecule.
- **`denovo_94`** — MM-GBSA margin +5.02, 4 handles; carries a **peroxide (1,2-dioxane)** plus N,S- and
  O,S-acetals — non-viable.
- **`denovo_57`** — SMILES `NC[C@@H]1CCN(Cc2ccccc2)C1` (3-(aminomethyl)-1-benzylpyrrolidine); SAscore **2.09**,
  aromatic, basic amine, no flagged liabilities — the **one chemically clean, readily synthesizable** hit, but
  the **weakest** signal (margin +1.07), engaging only 2/5 handles and in the docking "none" cell.
- **`denovo_189`** — the drug-likeness top hit — instead landed in the docking anti-target cell and did not come
  back selective (a reminder that drug-likeness ≠ selectivity).

**The decoy control that retracted the "MM-GBSA-confirmed selective" headline.** 38 non-NR4A marketed drugs
pushed through the identical dock → single-snapshot MM-GBSA funnel scored `confirmed_selective` in **39 %
(15/38)** of cases (caffeine, ibuprofen, lidocaine, phenytoin among them), while the developability-gated
de-novo set scored `confirmed_selective` in only **2/11 (18 %)** — i.e. **below the decoy baseline and not
enriched**. The single-snapshot, single-pose MM-GBSA plus the asymmetric receptor (NR4A3 in its druggable
release frame vs the paralogue metad frames) systematically favours NR4A3, so the verdict has **no
demonstrated specificity** — which is why the artifact `denovo_15` had scored selective. Against an empirical
decoy 95th-percentile bar (+13.1 kcal/mol; raw rank + ECDF + bootstrap also reported), the clean
fluoro-phenyl-pyrrolidine **`denovo_111`** (QED 0.87 / SA 2.9; margin +15.7; ranked above 37/38 decoys) was the
one candidate above the null in that harvest — but it was **subsequently withdrawn** when the pre-FEP
species-resolution sweep showed its **cation reverses** selectivity (multi-snapshot −15.01 ±
5.14; binds NR4A1 more tightly than NR4A3) — a protonation-state *sensitivity*, since the rule-based assignment
does not establish which microstate dominates at pH 7.4. A later generation produced **`denovo_401`**, which additionally
survives multi-snapshot de-noising and independent-seed replication, leaving it the sole candidate advanced to
ABFE. **No single-snapshot nomination was accepted**; the load-bearing claim is the funnel + the falsification
controls, not any of these molecules.

## S9. EMC dependence (the therapeutic prior and its one decisive gap), safety, and the pan-NR4A pole

*(Moved from the main-text Limitations in the 2026-07-10 round-6 restructure so the main Limitations stay focused on the computational method; no claim, number, or caveat was altered in the move.)*

**In particular, the therapeutic rationale for degrading NR4A3 in EMC (and
AciCC) assumes the tumour remains *dependent on NR4A3 for survival*, which is not yet demonstrated in
EMC.** Two kinds of support raise this prior, each stated with its boundary so neither is mistaken for
proof:
- **A transfer prior — used to justify *testing* the target, not as EMC evidence.** Related EWSR1/FET-fusion
  sarcomas are reliably *fusion-addicted* (Ewing/EWS-FLI1: −0.93 DepMap gene effect, 74 % of lines
  dependent), and EMC shares the profile that makes addiction the class norm — a quiet genome with a single
  near-clonal fusion driver. Reasoning from a represented lineage to an un-profiled one this way is standard
  practice for prioritising a target; it raises the prior and warrants the experiment, but it **cannot
  establish EMC dependence**. Its transferable content is also bounded: what these fusions share is the
  **EWS low-complexity transactivation domain**, so the analogy supports "EMC is probably addicted to its
  fusion," **not** "the NR4A3 effector specifically is the essential part" (EWS-FLI1's ETS-domain mechanism
  at GGAA microsatellites differs from a nuclear receptor) — a caveat that matters because the degrader
  engages the NR4A3 end.
- **EMC-specific molecular evidence (non-transfer) that the fusion is a functional transcriptional driver.**
  The chimera directly transactivates real targets — most concretely **PPARG**, via a bioinformatically
  identified EWSR1/NR4A3 response element in the PPARG promoter confirmed by band-shift and transactivation
  assays [Filion 2009], with further EMC-over-expressed targets reported (e.g. NDRG2). This is EMC-native
  support that the fusion *does something* transcriptionally — but it shows the fusion is a functional
  driver, **not** that the cell cannot survive its loss; *functional driver ≠ addiction*.
- **The fusion is a near-invariant, clonal driver in a quiet genome (quantified; verified evidence base:
  [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md)).** An **NR4A3 rearrangement is
  near-pathognomonic for EMC (~90–98 % of cases)** — EWSR1::NR4A3 in ~62–79 % (58/58 NR4A3-rearranged in a
  58-case cohort, Modern Pathology 2023 [PMID 36948401]; 24/26 in Agaram *Hum Pathol* 2014 [PMC4015728]) —
  with NR4A3 the **invariant 3′ partner** regardless of the 5′ gene. It is the **shared founding/clonal lesion**
  across matched primary + metastases in a **genomically quiet** tumour (matched-trio WGS, [PMC11285543]; EMC is
  <3 % of soft-tissue sarcomas). A single invariant clonal driver in a quiet genome is the textbook
  oncogene-addiction *profile* — a materially stronger prior than a lone analogy, though still a prior.

**The one decisive gap, stated plainly: there is NO direct loss-of-function experiment in any EMC cell line —
every published EMC functional result is *gain-of-function* (transactivation, transformation of non-EMC cells);
no RNAi/CRISPR/ASO knockdown of NR4A3 or the fusion in a human EMC model (e.g. H-EMC-SS) with a survival readout
exists** (verified 2026-07-02, [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md)). So the
multi-pillar case above is a strong *prior*, not demonstrated dependence. The acute, specific degradation (dTAG)
test that would convert this prior into a demonstration is the make-or-break experiment, delegated to the
EMC-program paper ([`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)); **this paper's claimed contribution
is the target's druggability/selectivity, not EMC efficacy.**

**Safety/tolerability, and the pan-NR4A/CAR-T pole — bounded in SI §S6 and §S4.** The systemic lead's tolerability case (the NR4A family's proliferative dispensability by DepMap; the *myeloid* NR4A1↔NR4A3 redundancy that makes NR4A1-sparing mandatory; broad NR4A1/NR4A3 co-expression; PK/CNS restriction) is quantified in **SI §S6**. Two load-bearing caveats carry back into main text: human germline genetics (gnomAD) **invalidates the glib "dispensable ⇒ safe" inference** and makes **NR4A2-sparing a safety requirement** — NR4A2 is the most LoF-constrained *and* CNS-enriched paralogue (LOEUF 0.094), NR4A3 borderline (LOEUF 0.37, pLI-intolerant) — and single-KO tolerability remains an *assumption* (no phenotyped IMPC KO for any of the three). The pan-NR4A / CAR-T pole is bounded separately and more tightly in **SI §S4** (chemical-feasibility only — the framework can *design* a pan-NR4A binder, not that it reverses T-cell exhaustion — plus an ex-vivo washout/exposure parameter).

## S10. The published-warhead registry — the experimentally anchored NR4A chemistry (Workstream B)

The brief gives *published* NR4A chemistry the same or greater priority as internally generated molecules:
denovo_401 must compete against real chemotypes, not be favoured for being ours. **SI data + provenance:**
[`../modalities/published-warhead-registry.md`](../modalities/published-warhead-registry.md) (narrative +
evidence) and the versioned machine-readable
[`published-warhead-registry.json`](../modalities/published-warhead-registry.json) (v1.0.0), built by
[`published_warhead_registry.py`](../modalities/published_warhead_registry.py) on a CPU runner.

**What it assembles, with evidence class + source per compound:** the **Zaienne 2022** NOR-1
fragment→low-µM-inverse-agonist series [ref 5] (the primary published NR4A3 warhead source; its elaborated
lead — **compound 19, methyl 5-bromoindole-3-carboxylate**, blocking NOR-1↔SMRT/NCoR1 and derepressing MYC —
was transcribed from the OA full text and is a **resolved** entry, alongside PGA2 and 6-mercaptopurine as
further NR4A3 ligands); the **NR4A1/Nur77** panel
(cytosporone B — a *pan*-NR4A direct binder [Zhan 2008; Munoz-Tello 2021]; THPN — Nur77 LBD cocrystal PDB 4JGV;
TMPA and C-DIM8 — functional); the **NR4A2/Nurr1** panel (amodiaquine, chloroquine — direct Nurr1 LBD binders
by NMR [Munoz-Tello 2021]; DHI and PGA1 — the only NR4A2 cocrystal ligands, both **covalent** to Cys566;
C-DIM12 — a functional **non-binder** control); and **NR-V04** [ref 12] as a verified composite
(celastrol warhead + VH032 VHL ligand) alongside the CRBN handle lenalidomide.

**Structure integrity.** Every named compound's isomeric SMILES/InChIKey is resolved and **cross-checked
across three independent resolvers (ChEMBL, PubChem, NCI CACTUS)** by InChIKey skeleton; confidence is high
(≥2 agree) / medium (1, or a flagged disagreement) / unresolved (none — kept null, never fabricated). The
cross-check caught two mis-resolutions and handled both honestly: (i) name-resolving "NR-V04" returns a
**CRBN/glutarimide PROTAC** (CHEMBL4779766) that contradicts the published **VHL/celastrol** composition — the
collided record is **rejected**, not asserted; (ii) "5,6-dihydroxyindole" resolved to a carboxylic-acid
derivative of the wrong mass in one source, corrected by an `expected_mw` disambiguator to the correct parent.

**Use.** These panels are the ligand set for the Gate-2 published-chemistry docking benchmark and the standing
anti-target-discrimination set (a candidate resembling amodiaquine/cytosporone B is a promiscuity flag, not a
lead). Covalent/reactive warheads (celastrol, DHI, PGA1) are flagged for special handling (brief 21.1).
**Gate-2 result (2026-07-11) — a negative control on the in-silico selectivity stack.** Docking the panel
into the state-matched opened NR4A3/NR4A1/NR4A2 pockets shows the pocket model **accommodates** every
published NR4A active (dG −5 to −9 kcal/mol) but **does not discriminate paralogues** (only THPN's NR4A1
preference is cleanly reproduced; the rest fall within docking noise; the one strong "NR4A3-selective" signal,
celastrol, is a reactive-triterpenoid artifact). **Multi-snapshot MM-GBSA does not rescue it** — worse, it
labels *both* neutral NR4A1 ligands (THPN, TMPA) as **false NR4A3-selective** (the opened-NR4A3-frame is more
accommodating), and the charged 4-aminoquinolines show protonation-fragile ~10–20 kcal electrostatic
artifacts. **Combined: neither cheap tier reproduces known NR4A paralogue preferences on experimentally
anchored chemistry** — an external corroboration (independent of the de-novo set) that a paralogue-selectivity
claim cannot rest on docking or single-frame MM-GBSA; it must come from FEP with resolved microstates and
ensemble/opened-state controls, or be hedged. Full tables:
[`../modalities/published-warhead-registry.md`](../modalities/published-warhead-registry.md) (Gate-2 sections).
