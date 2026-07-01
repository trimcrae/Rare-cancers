# Selectivity architecture of an NR4A3 degrader: binder vs ternary, and whether to select at all

**Status:** design analysis (in-silico + literature reasoning; no wet lab). Scoped to the EMC
(EWSR1/TAF15::NR4A3) degrader program. Written 2026-06-30.
**One-line thesis:** *Selectivity is a **multiplicative** budget whose factors **compound** across three
pharmacological stages and two independent axes — so the levers **add to** each other, none replaces another.
A selective **binder is the primary goal and strictly valuable** (`denovo_401` is a decoy-null-screened foothold — not fully control-validated, since the null does not control the generative step, F16); the
architecture's point is that because binder selectivity is **fragile** in this cryptic pocket, a robust
degrader should **also** draw paralogue selectivity from the ternary complex (compounding the binder's margin;
plus pharmacokinetics for NR4A2), and route fusion-vs-wild-type — unobtainable from the degrader — to the ASO.
The binder should be optimized for **affinity + a productive exit vector + the paralogue selectivity it already
shows**, with the ternary an **additional** robustness lever, not a substitute for the binder campaign.*

This document treats "where does selectivity come from" as its own optimization problem, deliberately
independent of the binder-hunting campaign's momentum. It is **evidence-led**: the central claim is a
computed result (below), and it overturns the intuition the campaign was implicitly operating on.

---

## 1. The question, stated precisely

"Selectivity" for this degrader is not one thing. There are **two independent axes**, and each can in
principle be encoded at any of **three pharmacological stages**. Conflating them is the main source of
muddled reasoning.

**Two axes (what we want to discriminate):**

- **Axis A — paralogue:** NR4A3 vs NR4A1 (NUR77) and NR4A2 (NURR1). A *tox-mitigation* requirement.
  Losing NR4A1 together with NR4A3 is leukaemogenic in mice (Mullican et al., *Nat Med* 2007); losing
  NR4A2 risks dopaminergic/Parkinsonian effects (NR4A2/Nurr1 is a midbrain-DA-neuron gene). So sparing
  the paralogues is about therapeutic index, not anti-tumour efficacy.
- **Axis B — fusion vs wild-type:** the oncogenic driver is the EWSR1/TAF15::NR4A3 chimera; wild-type
  NR4A3 also exists in normal tissue (vascular, metabolic, vestibular, bone roles; tumour-suppressive in
  several contexts — Safe & Karki 2021). Discriminating the fusion from wild-type NR4A3 is an *efficacy/
  on-target-safety* axis — it is what would make the therapy tumour-exclusive.

**Three stages (where selectivity can be encoded):**

1. **Binding** — warhead affinity for the NR4A3 LBD pocket vs the paralogue/wild-type pockets.
2. **Ternary** — formation of a *productive* E3–PROTAC–target complex: PPI surface complementarity,
   cooperativity (α), and degradable-lysine geometry.
3. **Kinetics / processivity** — ubiquitination rate, complex residence time, target resynthesis rate —
   the determinants of catalytic, sub-stoichiometric degradation.

**The selectivity budget (the governing model).** Degradation selectivity is *multiplicative* across
stages:

```
S_degradation(target_i vs target_j)  ≈  S_binding × S_ternary × S_kinetic
```

This is the single most important framing in the whole problem. It means the selectivity burden can be
placed on **whichever stage is cheapest and most reliable to engineer** — the binder does **not** have to
carry it alone. This is precisely the principle behind "binding selectivity ≠ degradation selectivity":
a *non-selective binder can degrade selectively* if only one paralogue forms a productive ternary
geometry (the textbook case: Bondeson et al., *Cell Chem Biol* 2018, selective degradation from a
promiscuous warhead; Gadd et al., *Nat Chem Biol* 2017, MZ1–BRD4 positive cooperativity α≈17.6 driving
BRD4 selectivity from a pan-BET binder).¹ The campaign so far has implicitly assumed the binder must be
selective on its own — that assumption is what this analysis corrects.

¹ *PROTAC cooperativity references (Gadd 2017; Bondeson 2018) are well-established literature; cited from
memory and should be page-checked before they enter the formal manuscript. They are used here only to
support a mechanistic principle, not a quantitative claim.*

---

## 2. Computed result: the warhead pocket is a selectivity *hotspot*, not a conserved liability

The intuitive case for "get paralogue selectivity from the ternary, because the conserved LBD pocket
can't deliver it" turns out to be **wrong for NR4A3**. Using the repo's own NR4A1/2/3 LBD alignment
(`research/modalities/nr4a-selectivity.json`; AFDB models + BLOSUM62), comparing divergence in the
orthosteric cryptic pocket (the warhead's contact residues, NR4A3 Pocket-5 lining:
406/407/410/411/412/481/484/485/531/534) against the LBD-wide pocket-residue census:

| residue set | n | divergent vs ≥1 paralogue | divergent vs **both** at once |
|---|---|---|---|
| **Orthosteric cryptic pocket (warhead contacts)** | 10 | **70%** | **60%** |
| LBD-wide pocket census | 148 | 45% | 28% |
| Non-orthosteric remainder (surface/PPI proxy) | 138 | 43% | — |

**The warhead pocket is ~1.6× more divergent than the rest of the LBD** (70% vs 43%), and on the
demanding "differs from *both* paralogues simultaneously" criterion the gap is wider still (60% vs 28%).
Far from being a conserved wall, the NR4A3 orthosteric pocket is the **most paralogue-divergent zone of
the LBD** — it is a selectivity hotspot.

**What this means, un-spun:**

- The binder's selectivity problem was **never handle scarcity.** Seven of ten pocket-contact residues
  diverge; the design-spec's engageable handles (L406, T410, I484, I531, L534, plus T407/R412) are real.
- The binder's *actual* problem is **druggability + affinity-robustness**: NR4A3's pocket is the least
  druggable of the three (fpocket 0.495 vs NR4A1 0.657, NR4A2 0.801), it is **cryptic** (druggable in
  only ~a quarter of frames), and a selectivity *margin* large enough to survive scoring noise is hard to
  reach. The red-team decoy control (F15) and the multi-snapshot collapse of denovo_393 (+18.34 →
  −2.95 ± 3.65) are symptoms of *this* — noise, not absence of divergent contacts. And it is *achievable*
  with effort: denovo_401 holds at +12.83 ± 2.98 (margin − SD = +9.85) under multi-snapshot.
- **The asymmetric window is confirmed at the residue level.** I531 is *identical* in NR4A3 and NR4A2
  (Ile↔Ile), so the pocket offers one fewer NR4A2-discriminating contact than NR4A1-discriminating
  contact. NR4A2 is the harder paralogue to spare **molecularly** — which matters for §6.

**Caveat on the proxy.** "Non-orthosteric remainder" is pocket-lining residues across all 33 fpocket
cavities, used as a stand-in for the true E3-facing PPI surface (**now directly mapped on the F18 ternary —
§8.3 step 3: 24 % divergent vs each paralogue, distinct from the pocket** — so the proxy below is superseded).
It is a reasonable but imperfect proxy; the ternary-surface conservation should be computed directly on
the actual predicted E3 interface before this comparison is load-bearing in a manuscript.

---

## 3. Stage-by-stage tractability (paralogue axis)

| stage | handles available? | tractability here | what it buys | what it costs |
|---|---|---|---|---|
| **Binding** | **Yes — abundant** (pocket is a divergence hotspot, §2) | **Hard but proven** — poorly druggable cryptic pocket → fragile, noise-limited margin; 1 lead (denovo_401) survived a large campaign | a head-start margin that *relaxes* the ternary requirement | the costliest stage to push; low yield per candidate |
| **Ternary** | Fewer divergent residues on the surface on average (§2 proxy), but **mechanism amplifies** small differences | **The documented degrader strength** — cooperativity is multiplicative and can be large (α≈17.6 precedent); degradable-lysine *positions* can differ between paralogues regardless of sequence conservation | selectivity orthogonal to the fragile pocket-affinity problem; rescues a non-selective binder | requires the ternary model to be *run* (primed, not yet executed); E3 choice (CRBN/VHL) is a design variable |
| **Kinetics** | implicit (target resynthesis + complex lifetime differ by paralogue) | least controllable in silico; emerges from the above | catalytic amplification of any upstream margin | hardest to predict without wet-lab degradation kinetics |

**Reading:** the binder *can* contribute selectivity (real handles) but it is the **expensive, fragile**
place to source it. The ternary is the **cheap, robust, mechanism-amplified** place — and it is exactly
where degraders are known to get their selectivity in practice. The rational budget allocation therefore
puts the **primary** paralogue-selectivity burden on the **ternary**, and treats whatever the divergent
pocket yields (denovo_401) as a bonus that lowers the bar the ternary must clear — not as the gate.

---

## 4. Axis B (fusion vs wild-type): unobtainable from the degrader — and why that is the key strategic fact

A LBD-binding degrader **cannot** distinguish the fusion from wild-type NR4A3, at **any** of the three
stages:

- **Binding:** the fusion retains the *identical* NR4A3 LBD; the only tumour-unique feature is the
  EWSR1/TAF15::NR4A3 junction, which lies in a **disordered** N-terminal region with no structured
  pocket. The warhead binds a domain common to fusion and wild-type. Impossible by construction.
- **Ternary:** the ternary complex forms *at the LBD* — tens of nanometres of disordered chain away from
  the N-terminal fusion partner. A standard CRBN/VHL ternary has no line of sight to the FET partner, so
  it cannot be steered toward the fusion. The *only* way the ternary touches axis B is an **avidity /
  AND-gate** design (arm 1 on the shared LBD, arm 2 on the fusion-restricted EWSR1 low-complexity domain
  / condensate) — and the repo's own modelling shows that route's **degradation** window is narrow and
  dose-fragile (≈6.8× at sub-saturating dose, eroding toward ≈1× at saturation), on top of unsolved
  arm-2 chemistry. It is a separate, speculative program, not a property of the lead degrader.
- **Kinetics:** no kinetic handle distinguishes two proteins identical in the degraded domain.

**Strategic consequence (the load-bearing conclusion of this whole analysis):** **do not spend any of the
degrader's selectivity budget trying to be fusion-selective.** It is the single least tractable thing the
molecule could attempt, and effort there is effort not spent on the achievable axes. Fusion-vs-wild-type
exclusivity is the **ASO's** job (RNA-level base-pairing to the chimeric junction spares wild-type
NR4A3 — the documented #1 fusion-exclusive route). The degrader and the ASO are **complementary, not
competing**: degrader = potent/druggable but fusion-*blind*; ASO = fusion-*exclusive* but delivery-limited.

The degrader's honest selectivity scope is therefore **axis A only** (paralogue), and its relationship to
wild-type NR4A3 is "**accepted on-target cost**," not "designed-around." Wild-type NR4A3 single loss is
plausibly tolerable (viable single-knockout animals; paralogue redundancy; catalytic, dose-titratable
PROTAC) — but that is a *tolerability* argument, not a *selectivity* one, and it must be labelled as such.

---

## 5. Where to actually spend the paralogue (axis A) budget — per paralogue, not in aggregate

Treating "spare NR4A1 and NR4A2" as one requirement hides that the two have **different optimal levers**:

**NR4A1 (the strongest requirement; AML safety net, Mullican 2007):**
- Most divergent from NR4A3 at the pocket *and* most likely to differ on the ternary surface and in
  lysine layout. → Source NR4A1 selectivity from the **ternary** primarily (robust, mechanism-amplified),
  with the binder's NR4A1-discriminating contacts (which include I531, *not* shared with NR4A1) as a bonus.

**NR4A2 (dopaminergic/CNS risk; the molecularly *hardest* paralogue — I531 identical):**
- The pocket offers one fewer NR4A2 handle (§2), so molecular NR4A2 discrimination is intrinsically
  harder at *both* binder and (likely) ternary stages.
- **But the NR4A2 tox is anatomically localized to the CNS.** The cheapest, most reliable lever is
  therefore **pharmacokinetic, not molecular**: a **peripherally-restricted, non-CNS-penetrant** degrader
  spares midbrain NR4A2 by *exposure*, sidestepping the hardest molecular-selectivity problem entirely.
  EMC is a peripheral soft-tissue sarcoma, so CNS exclusion costs little efficacy. → Source NR4A2 safety
  from **PK/CNS-exclusion** as the primary lever; molecular NR4A2 selectivity is a secondary, optional top-up.

This is the un-obvious payoff of decomposing the axis: **the two paralogues should be spared by different
mechanisms** (NR4A1 by ternary selectivity, NR4A2 by pharmacokinetics), and recognizing that removes the
need to solve the hardest molecular case (NR4A2 discrimination in a poorly druggable pocket).

---

## 6. Designing *against* selectivity: the pan-NR4A option, taken seriously

Selectivity is a design variable that can be optimized **toward zero** — a deliberately *pan*-NR4A
degrader (built from the *conserved* pocket residues, the opposite profile from denovo_401). When is that
the better molecule?

- **Easier:** any decent NR4A binder works; the fragile pocket-affinity-margin problem disappears.
- **Possibly more efficacious** where the paralogues are redundant: full T-cell-exhaustion reversal needs
  NR4A *triple* loss (Chen et al., *Nature* 2019), so a pan-NR4A degrader is the *right* tool for ex-vivo
  CAR-T manufacturing.

**But for systemic EMC therapy, pan-NR4A is off the table on tox grounds**, and the genetics are decisive,
not hand-wavy: NR4A1+NR4A3 co-loss is leukaemogenic (Mullican 2007), and all three NR4As contribute to
myeloid tumour suppression — so *systemic, sustained* pan-NR4A degradation removes a tumour-suppressor
safety net. The repo's position (pan-NR4A = **ex-vivo CAR-T only**, systemic = contraindicated) is correct
and this analysis does not overturn it.

**The honest uncertainty:** the contraindication rests on *genetic-knockout* phenotypes, whereas a
degrader delivers *transient, dose-titratable, possibly tissue-restricted* pharmacology — which is not the
same as constitutive biallelic loss. We cannot resolve where that window sits without tox data we cannot
generate (no wet lab). So the defensible statement is: **for systemic EMC, design *for* paralogue
selectivity (at minimum vs NR4A1); reserve pan-NR4A for ex-vivo indications** — and flag the
genetics-vs-pharmacology gap rather than pretending it is closed.

---

## 7. Recommendation for EMC (the allocation)

Evidence-led, EMC as the fixed goal:

1. **Binder:** keep it **selective *and*** optimize for **affinity + a productive, solvent-exposed exit
   vector** (for the linker) — a selective binder is the primary goal and strictly valuable, and `denovo_401`
   already delivers a **decoy-null-screened** paralogue margin (exceeds a same-tier multi-snapshot decoy null in
   its design frame — a foothold, not fully control-validated, since that null does not control the generative
   step or the best-of-N selection, F16).
   The realistic caveat is only that this margin is **fragile** in a poorly druggable cryptic pocket (one
   survivor out of ~10 multi-snapshot-tested), so **don't rely on the binder *alone*** and don't expect blind
   generation to keep yielding survivors — but that argues for *compounding* the binder margin with the ternary,
   **not** for abandoning binder selectivity. (Prior wording here said "optimize for affinity, *not* selectivity"
   / "don't burn campaigns on binder selectivity"; that overstated the case and contradicted the campaign — corrected.)
2. **Paralogue selectivity (NR4A1):** the binder already discriminates NR4A1 (ΔG NR4A3 −38.18 vs NR4A1 −22.98);
   **compound** that with the **ternary complex** — run the already-built ternary model across NR4A1/2/3 to find
   an E3 + linker geometry that is productive on NR4A3 and *un*productive on NR4A1. This is the highest-value
   un-run experiment in the program — an *additional* lever on top of the binder's margin, not a replacement.
3. **Paralogue safety (NR4A2):** source primarily from **PK / CNS-exclusion** (peripheral restriction),
   because the molecular handle is the weakest (I531 shared) and the tox is CNS-localized.
4. **Fusion vs wild-type:** **do not attempt with the degrader.** Accept wild-type NR4A3 loss as a
   labelled on-target cost; route fusion-exclusivity to the **ASO**. The degrader's deliverable is potency
   + paralogue safety, not tumour-exclusivity.
5. **Pan-NR4A:** keep only as the **ex-vivo CAR-T** design mode; off-table for systemic EMC.

**So: does it matter whether selectivity comes from the binder or the ternary? Yes — decisively.** The
optimal source is *mechanism-matched to the axis*: paralogue → ternary (+PK), fusion → a different
modality entirely. The binder is an affinity/vector module whose selectivity is welcome but not relied on.

---

## 8. What is computable next (no wet lab) — the ternary-selectivity work-package

The binder campaign has a mature in-silico funnel; the **ternary** axis — now the higher-value one — does
not yet have its evidence. Concrete, runnable steps (all in-silico):

1. **Run the primed ternary model** (`nr4a3_ternary.py` / Boltz-2 / AF3 swap-in; `gpu-ternary-aws.yml`)
   for NR4A3 **and** NR4A1/NR4A2, with denovo_401 as the warhead and CRBN + VHL as alternative E3s.
   Output: predicted cooperativity and a *productive-geometry* verdict per paralogue. Positive control:
   CRBN + lenalidomide seating in the tri-Trp pocket. **This is the gating experiment for any degradation-
   selectivity claim and should be the next GPU job after the binder screen closes.**
2. **Degradable-lysine map per paralogue:** SASA + geometric reachability of lysines within the
   ubiquitin-transfer zone of each ternary, for NR4A3 vs NR4A1/2. Lysine *positions* can differ even
   where sequence is conserved — an orthogonal, possibly larger, selectivity source than pocket contacts.
3. **True PPI-surface conservation map — ✅ DONE (2026-07-01, F18 ternary + `report_ternary.py` interface
   mode).** The predicted NR4A3–CRBN interface (33 residues) is **24 % divergent vs each paralogue (8/33), 18 %
   vs both (6/33: E545/T563/Q570/S571/L576/E580/V588…)** — *less* selectivity-rich than the orthosteric pocket
   (70 %/60 %) but **not conserved**, and it is a surface **distinct from the pocket handles** (0 of 7 handles
   at the interface). So ternary selectivity is **structurally available on an independent surface** (real
   multiplicative gain), though single-pose Boltz can flag availability, not optimize/validate it.
4. **E3 / linker-exit-vector scan:** since the binder is being optimized for a productive exit vector
   (§7), enumerate linker attachment points on denovo_401 and score ternary productivity vs each paralogue
   — making the binder and ternary optimizations explicitly *joint*, not sequential.

---

## 9. Falsification — what would change these conclusions

- The true E3-interface conservation map (step 3) has now been computed (F18): the interface is **24 %
  divergent vs each paralogue — less than the pocket (70 %) but not conserved.** Per this test that lands
  *between* the two extremes: ternary selectivity is **available but the interface is less selectivity-rich
  than the pocket**, so the **binder stays the primary lever** (§7.1) and the ternary is a *real secondary*
  one (a divergent patch to design a linker toward), not the dominant source once hoped.
- If the ternary model (step 1) finds **no** E3/linker geometry that discriminates NR4A3 from NR4A1 →
  paralogue selectivity may be unobtainable from *either* stage, forcing either (a) reliance on PK/tissue
  restriction for *all* paralogues, or (b) a re-examination of whether NR4A1 co-degradation is actually
  tolerable at therapeutic exposure (a tolerability, not selectivity, question).
- If credible evidence emerges that **transient** pan-NR4A degradation is tolerable systemically (vs the
  knockout genetics) → the pan-NR4A option re-opens for EMC and the whole selectivity budget can be
  redirected to potency. This is the single assumption most worth pressure-testing, because if it holds it
  collapses the hardest part of the problem.

---

## 10. Honest limits

- **No wet lab.** Every tox/tolerability statement is reasoning from published genetics + tissue
  distribution, not measured therapeutic index. The genetics-vs-pharmacology gap (§6, §9) is real and open.
- **§2 used a pocket-residue proxy** for the PPI surface; the real interface has since been mapped on the F18
  ternary (§8.3, step 3) — 24 % divergent vs each paralogue, distinct from the pocket — so the proxy is no
  longer load-bearing.
- **The ternary axis has now been RUN (F18, 2026-07-01), not just argued:** the NR4A3/1/2–CRBN–denovo_401-PROTAC
  ternaries all form productively (mechanism viable) and are **not paralogue-selective for the representative
  linker**, while the interface itself is divergent (ternary selectivity *available* but unrealized). So the
  ternary is a **real secondary** selectivity lever, **not the primary source** this document once leaned
  toward — the binder (§7.1) stays primary. Single-pose Boltz cannot optimize/validate ternary selectivity
  (a ternary-ensemble/cooperativity method is the right tool — method-watch).
- **PROTAC cooperativity citations** (Gadd 2017; Bondeson 2018) are used for a mechanistic principle and
  should be verified before formal use.

---

## Relationship to existing repo documents

- Sharpens, and is consistent with, `nr4a3-degrader-paper.md` (§2.4/§5 binding≠degradation),
  `nr4a3-degrader-design-spec.md` (fusion-vs-WT not solvable; ternary primed), and
  `nr4a3-degrader-paper-redteam.md` (F8, F15). **New here:** the computed pocket-is-a-hotspot result (§2),
  the multiplicative-budget framing (§1), the per-paralogue lever split (NR4A1→ternary, NR4A2→PK; §5), and
  the explicit recommendation to *not* source selectivity from the binder as a gate (§7).
- The pan-NR4A and fusion-exclusivity positions align with `nr4a3-degrader-broader-indications.md` and
  `fusion-selective-approaches-overview.md`; nothing here overturns them.
