# Target-route options — questioning the target, not the method

> **Role:** decision memo. It asks the question the program has never asked: **must the molecule be
> NR4A-paralogue-selective at all, and if so, against what?** The whole degrader programme assumes a
> hard discrimination against NR4A1 and NR4A2. Some of the best options may sidestep that requirement
> rather than solve it. This file ranks every route by **its effect on the selectivity requirement**
> and grades each against the roadmap's failure record — not against novelty.
>
> **Subordinate to [`nr4a3-program-map.md`](./nr4a3-program-map.md)** (the roadmap owns the plan, the
> gates and the prices; nothing here restates one) and to
> [`emc-treatment-strategy.md`](./emc-treatment-strategy.md) + [`../IDEAS.md`](../IDEAS.md) (the route
> portfolio). Where any of them conflicts with this memo on a plan or an ordering, **they win.**
> This memo's contribution is the *target* axis, which none of them carries.
>
> **$0.** No GPU, no rental, no wet lab. Every number below is either read from a committed artifact or
> computed on CPU by [`../modalities/target_route_census.py`](../modalities/target_route_census.py) →
> [`target-route-census.json`](../modalities/target-route-census.json) (pure stdlib, reproduces under
> `--check`). Nothing here is a molecule, a structure, a binding claim, or a clinical statement, and no
> statement about activity or tolerability in a patient is made or implied.

---

## 0 · The evidence taken this session, before any argument

Per CLAUDE.md §4 — a $0 observation is never "watching". Four checks were run first; three changed the
question, one closed a route.

| # | check | cost | result |
|---|---|---|---|
| **A** | Domain-resolved NR4A paralogue identity, computed from the cached UniProt sequences | $0 CPU | The premise "two ~80 %-identical paralogues" does not hold anywhere. **LBD 59.4 % (NR4A1) / 67.3 % (NR4A2)**; **zinc-finger DBD 92.8 % / 98.6 %**; AF1 26.9 % / 36.9 % ([census](../modalities/target-route-census.json) `paralogue_identity_by_domain`, `zinc_finger_window`) |
| **B** | The junction residue swap — what the chimera trades when EWSR1-LC replaces NR4A3's own AF1 | $0 CPU | **NR4A3 AF1 (1–260): 7 lysines, 3 cysteines (C3, C75, C166). EWSR1-LC (1–264): 1 lysine (K144), 0 cysteines.** The LBD is byte-identical in both proteins ([census](../modalities/target-route-census.json) `af1_to_lc_swap`) |
| **C** | Which fusion protein the repo actually models | $0, read | ⛔ **Two committed objects disagree, and nobody has reconciled them** — see [§1.3](#13--finding-3--the-repo-holds-two-incompatible-models-of-the-fusion-protein) |
| **D** | Is the paralogue-cross-reactivity liability uniform across NR4A1 and NR4A2? | $0, read | **No — it is asymmetric, and the two halves have different evidence and different remedies.** See [route 1](#route-1--asymmetric-selectivity-nr4a1-sparing-mandatory-nr4a2-sparing-best-effort--pk) |

---

## 1 · Three findings that reframe the question

### 1.1 · Finding 1 — the paralogue problem is not a sequence problem, and the "~80 %" framing is a retracted number

The roadmap already retracted the bare *"~80 %-identical pocket"* figure: it is **SMARCA2/SMARCA4**,
transplanted onto NR4A ([§8 Route B](./nr4a3-program-map.md#route-b--a-linker-borne-covalent-handle-at-an-nr4a3-unique-cysteine---blocked-on-r5-nothing-running--serves-r8-r15) — *"Nothing in this repo puts the NR4A paralogue pocket at ~80 % identity"*).
Its own numbers are Pocket-5 lining **30 % identical** (7 of 10 lining residues divergent) and the LBD
**≈57 %** pooled. Check A adds the per-paralogue, per-domain version, and it sharpens the point:

| object | NR4A3 vs NR4A1 | NR4A3 vs NR4A2 |
|---|---|---|
| zinc-finger DBD (69 aa, motif-anchored) | **92.8 %** | **98.6 %** |
| hinge (338–372) | 94.3 % | 97.1 % |
| **ligand-binding domain (373–626)** | **59.4 %** | **67.3 %** |
| AF1 (1–260) | 26.9 % | 36.9 % |
| Pocket-5 lining (10 residues) — *pooled across both paralogues, from [`nr4a-selectivity.json`](../modalities/nr4a-selectivity.json), not recomputed here* | **30 % identical** | **30 % identical** |

**Two consequences, and both are load-bearing for this memo.**

1. **The programme is already working in the most divergent part of the protein.** The LBD is the least
   conserved *ordered* domain and the pocket lining is more divergent still. There is no better place to
   stand. So a route that promises "an easier selectivity problem" has to say *where* — and the answer
   is nowhere on this protein.
2. ⛔ **Any route that relocates the target to the DBD or to DNA binding makes the requirement strictly
   worse** — 93–99 % identity against 59–67 %. That kills, on arithmetic and for $0, the whole family of
   "block the fusion's DNA binding instead" ideas before anyone builds one.

### 1.2 · Finding 2 — the requirement is a MEASUREMENT problem, so a route "sidesteps" it only by leaving the free-energy axis

The roadmap's margin arithmetic has one home
([MECHANISM-FIRST](./nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged)):
a useful degradation window needs **~2.0 kcal/mol** of true margin, against a best-case **resolvable**
difference of **0.60** and an engine accuracy of **1.543 kcal/mol, wrong sign**. The roadmap is explicit
that *"a passing selectivity benchmark would not close that gap"* and that `R7` is blocked by three
things, only one of which is the instrument.

**So the grading axis for this memo writes itself.** A route reduces the paralogue requirement only if it
moves the claim off "a free-energy difference between two similar pockets" and onto one of:

- **a categorical axis** — a residue one protein has and the other does not, which is set membership and
  needs no instrument that resolves 1 kcal/mol (the roadmap's own framing of Route B: *"a **categorical**
  discriminator … a set-membership fact rather than an energy difference the method cannot resolve. That
  is the honest case, and it is a stronger one."*);
- **a different molecule entirely** (RNA, peptide-HLA — base-pairing and peptide identity are also
  categorical);
- **a different target** (downstream node, dependency partner);
- **a different exposure regime** (ex vivo, or restricted biodistribution), where the liability the
  selectivity exists to avoid does not arise.

Everything else *relocates* the problem. That distinction is the deliverable in
[§3](#3--what-genuinely-sidesteps-the-paralogue-problem-and-what-merely-relocates-it).

### 1.3 · Finding 3 — the repo holds two incompatible models of the fusion protein

⛔ **This is the finding with the widest blast radius, it was free, and it has been sitting in two
committed files.**

| model | where | NR4A3 resumes at | AF1 present? | DBD present? | is C166 in the fusion? |
|---|---|---|---|---|---|
| **A** | [`fusion_cofold.py`](../modalities/fusion_cofold.py) (`EWS_CUT = 264`, *"NR4A3 resumed at res 2"*) | **residue 2** | yes | yes | **yes** |
| **B** | [`fusion-breakpoint-neoantigens.json`](../modalities/fusion-breakpoint-neoantigens.json) — 7 in-frame junctions derived from Ensembl exon structure | **318 / 361 / 419** | no | partial or none (the C4 zinc finger begins at NR4A3 **C292**) | **no** |

Model A is *self-declared* an assumption — `fusion_breakpoints.py`'s own docstring calls it *"an
assumption, not a sourced breakpoint"*, and building the exon-derived alternative was that module's whole
purpose. **But the two were never reconciled**, and the repo's downstream work uses both: the co-fold
constructs use A, the junction neoepitope predictions use B.

**Evidence already in the repo bears against B as written.** The fusion binds a response element in the
*PPARG* promoter and transactivates it (Filion et al., *J Pathol* 2009, **PMC4429309**; band-shift +
transfection — cited as pillar 2 of the gain-of-function case in
[`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md)). That is a DNA-binding-domain-dependent
function, and every model-B resume point (≥318) truncates or deletes the zinc-finger DBD. So they cannot
both be right, and the one with independent functional support is A.

**Why it matters here, in four places:**

1. **`R13` is worse than "unpriced".** The roadmap says every structure in the programme is an isolated
   LBD construct (373–626) and that requirement 13 has *"no lane, no rung, no row anywhere"*
   ([§2.2](./nr4a3-program-map.md#22--requirements-with-no-instrument--the-holes)). It is not only
   unscheduled — **the object it would model is not defined.** A rung cannot be written for a target
   whose sequence is ambiguous by ~360 residues.
2. **The C166 argument depends on it.** [§7 branch 1](./nr4a3-program-map.md#branch-1--answered-2026-08-02--serves-r8)
   records C166 as a fourth NR4A3-unique cysteine that the LBD construct boundary removes from the design
   space — *"it removes a real residue … and nothing on the plan asks what else it removes."* Under model
   B, C166 is **not in the disease protein at all**, so the construct boundary costs nothing there and the
   isolated LBD is a *better* model of the fusion than of wild-type NR4A3. Under model A the roadmap's
   reading stands. One free check decides which sentence is true.
3. **Every junction neoepitope is conditional on it.** The 26 predicted binders in
   `fusion-breakpoint-neoantigens.json` are peptides *spanning the seam*. If the seam moves, the peptide
   set moves. That is a caveat the neoantigen manuscript does not carry.
4. **It is the one place where "model the real biological object" is cheap.** Validation requirement 5
   asks for the fusion-context ensemble; the blocker everyone assumed was GPU cost. It is not — it is a
   sequence definition, and that is free.

⭑ **Named $0 test:** re-derive NR4A3's coding-exon offsets from the MANE transcript **in CI** (networked,
so GitHub Actions, not the sandbox) and audit `fusion_breakpoints.py`'s resume index — `offsets[n-2]`
assumes exon 2 is the first coding exon, which shifts the resume point by one exon if it is not. Then pin
the EMC junction against a primary breakpoint report rather than either model, and record it once.
Owner: [`target-route-census.json`](../modalities/target-route-census.json) `fusion_model_disagreement`.

---

## 2 · The route register

Ordered by **decision value per $0**, which is not the same as ceiling. The last two columns are the ones
this memo exists to fill.

| # | route | effect on the paralogue requirement | grade | cheapest decisive $0 test |
|---|---|---|---|---|
| **1** | **Asymmetric selectivity** — NR4A1-sparing mandatory, NR4A2-sparing best-effort + biodistribution | **RESHAPES.** One hard target instead of two symmetric ones | **★★ adopt now — free, and it changes the design brief** | MGI single-KO phenotypes for *Nr4a1/2/3* (IMPC returned nothing); HPA per-tissue nTPM for NR4A2 |
| **2** | **Covalent inhibitor / covalent probe at C397**, not a degrader | **RESHAPES.** Thermodynamic → categorical (a residue the paralogues lack) | **★★ promote** | re-run the linker-reach enumeration **without the E3 arm** — the constraint that produced branch 1b's counter-result does not apply to an inhibitor |
| **3** | **Fusion-junction ASO / siRNA** (already priority paper 2) | ⛔ **REMOVES it entirely** — base-pairing at a sequence neither paralogue has | ★★ already the plan; nothing here changes it | — (its gate is delivery, not selectivity) |
| **4** | **Ex-vivo pan-NR4A pole** (CAR-T manufacturing additive) | ⛔ **REMOVES it** — the systemic liability that motivates selectivity does not arise | ★ already in the paper as pole 2; under-used as an *argument* | — (readout already committed, `nr4a3-pan-readout.json`) |
| **5** | **Downstream nodes the fusion transactivates** (PPARG / TZDs) | ⛔ **REMOVES it** — different target | ★ keep; direction unresolved | resolve agonism-vs-antagonism from published EMC + TZD-in-sarcoma data |
| **6** | **TCIP / transcriptional chemical-induced proximity** (co-opt the fusion, don't degrade it) | **RESHAPES.** Keeps `R4` `R5` `R7`; **retires `R9` `R10` `R12`** | ★ new row — belongs on the board | grade the mechanism against the failure record; verify the auto-captured citation through `verify-refs` |
| **7** | **Junction neoantigen** (vaccine / TCR-T / soluble TCR) | ⛔ **REMOVES it** — peptide identity is categorical | ○ drafted; tolerance + cold tumour + partial HLA coverage | attach finding 3 as a caveat: the epitope set is conditional on an unreconciled junction |
| **8** | **AND-gate bivalent degrader** (avidity coincidence detection) | **NEUTRAL** — a second, independent axis; arm 1 still carries the paralogue handles | ⏸ hold — arm-2 chemistry does not exist | — (already computed; nothing free left) |
| **9** | **Synthetic-lethal / dependency partner** | ⛔ **REMOVES it** — different target | ⏸ parked on data, not on ideas | check whether the one EMC line in DepMap (**ACH-001519 / H-EMC-SS**) has gained CRISPR data since 24Q4 |
| **10** | **Molecular glue instead of a PROTAC** | **RELOCATES and WORSENS** — same discrimination, fewer independent axes | ⏸ watch, do not build | — (add a method-watch trigger) |
| **11** | **Target the EWSR1 half at the protein level** | ⛔ **RELOCATES onto an essential gene** — WT EWSR1 gene effect ≈ **−1.2** | ✕ down | — (already answerable from committed data) |
| **12** | **Target the DBD / DNA binding** | ⛔ **WORSENS** — 92.8 % / 98.6 % identity | ✕ down, on arithmetic | — (finding 1 closes it) |
| **13** | **Fusion-selective *ubiquitination*** — discriminate at the transfer step, not the binding step | **NEUTRAL on paralogues; would have been a fusion-vs-WT axis** | ✕ **closed by a measurement already committed** | — (done; see [route 13](#route-13--fusion-selective-ubiquitination-closed-by-a-number-the-repo-already-owns)) |

---

## 3 · What genuinely sidesteps the paralogue problem, and what merely relocates it

**Genuinely removes it (4 routes, and they share one property).** The junction ASO, the junction
neoantigen, the ex-vivo pan-NR4A pole, and the downstream/dependency routes all remove the requirement —
and every one of them does so by **leaving the free-energy axis entirely**: base pairing, peptide
identity, exposure regime, or a different protein. None of them removes it by being cleverer about the
pocket. That is finding 2 restated as a result: *on this target, selectivity cannot be won by better
chemistry against the paralogues; it can only be won by not needing it.*

**Reshapes it into something smaller (3 routes).** Asymmetric selectivity, the covalent/categorical axis,
and TCIP each keep an NR4A3 binder but shrink what it must achieve — one paralogue instead of two, a
residue instead of a ΔΔG, or a binder without a degradation geometry.

**Merely relocates it (3 routes), and two of the three land somewhere worse.** A molecular glue faces the
same discrimination with fewer handles; targeting EWSR1 at the protein level moves the selectivity burden
onto an essential housekeeping protein; targeting the DBD moves it onto a 93–99 %-identical domain.
⚠ **"Fusion-selective" is not automatically "paralogue-free".** The AND-gate is the clean example: it adds
a fusion-vs-wild-type layer and leaves the paralogue layer exactly where it was — its own §7 says arm 1
*"can additionally carry the … selectivity handles"*, i.e. two orthogonal requirements, not one replaced.

---

## 4 · The routes in detail

Each carries: the biological rationale (cited), what would have to be true, what in this repo already
bears on it, the cheapest decisive $0 test, its effect on the selectivity requirement, and a grade
**against the failure record** ([§6 of the roadmap](./nr4a3-program-map.md#6--the-closed-route-register)).

---

### Route 1 — asymmetric selectivity: NR4A1-sparing mandatory, NR4A2-sparing best-effort + PK

*The task asked whether degrading NR4A1/NR4A2 alongside NR4A3 is actually disqualifying — i.e. whether the
entire selectivity requirement dissolves. It does not, but the honest answer is more useful than "no":
**the two halves of the requirement are not the same requirement**, and the programme has been treating
them as one.*

**Rationale, cited.** The evidence base is already assembled and quantified in
[`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md) (hypothesis 1) with its numbers
committed in [`nr4a-safety-genetics.json`](../modalities/nr4a-safety-genetics.json). Read across the three
paralogues it is strikingly asymmetric:

| | NR4A1 | NR4A2 | NR4A3 |
|---|---|---|---|
| DepMap 24Q4 gene effect (n = 1178 CRISPR lines) | −0.115, 0.5 % dependent | −0.05, 0.3 % | **+0.023, 0 of 1178** |
| gnomAD pLI · LOEUF | 0.0017 · 0.71 — **LoF-tolerant** | **1.0 · 0.094** (1 observed LoF vs 50.5 expected) | 0.9999 · 0.37 |
| HPA tissue call | low specificity, *detected in all* | **tissue enhanced**, detected in all | low specificity, detected in many |
| named anti-target | ⛔ **combined *Nr4a1*⁻/⁻;*Nr4a3*⁻/⁻ mice die of AML in 3–4 weeks; single nulls do not** (Mullican et al., *Nat Med* 2007, PMID **17515897**; NR4A1/NR4A3 as *"functionally redundant suppressors of AML"*, *Blood* 2018, PMID **29343483**) | CNS/dopaminergic bias — the paralogue whose loss the roadmap calls *"the dopaminergic-loss liability one most wants to spare"* | the target |

**So the two halves answer differently.**

- ⛔ **NR4A1 co-degradation is the one thing that cannot be argued away.** The drug's *purpose* is to
  remove NR4A3. Adding NR4A1 removes both — which is precisely the genotype with the named lethal
  phenotype. This is not a generic "hitting a paralogue is untidy" worry; it is the specific pair.
  Worse, the repo's own adversarial verification pass **refuted (0-3)** the softening claim that dual
  NR4A1/3 loss is not catastrophic to HSCs (the double KO damages them: loss of quiescence, oxidative
  stress, DNA damage). **NR4A1-sparing is a hard requirement.**
  ⚠ Stated at its true weight in both directions: the mouse result is **germline homozygous loss from
  conception**, and a partial, reversible, adult pharmacological knockdown is a different exposure. That
  cuts against reading it as a prediction — but it is the correct anti-target to design away from, and
  nothing in silico can settle it.
- **NR4A2 co-degradation is the half nobody has bounded.** It is the *most* constrained paralogue in human
  population genetics (pLI 1.0, LOEUF 0.094) and the most tissue-enhanced. But the repo's IMPC query
  returned **no phenotyped KO for any of the three**, and the widely-repeated "Nurr1 single-KO is
  neonatal-lethal" is explicitly flagged **UNCONFIRMED** in
  [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md). So the state is: strongly selected
  against in humans, unbounded for adult transient loss, and **not verified by a standardized source**.

**What would have to be true** for this to change the design brief: that NR4A1 and NR4A2 sparing carry
different weights, and that the harder of the two is not the one with the larger liability. Both hold —
and the roadmap already records the mismatch without drawing the conclusion:
[§8 Route A](./nr4a3-program-map.md#route-a--a-warhead-engaging-paralogue-divergent-pocket-handles---blocked-nothing-running--serves-r7)
says **all 7** handles differ against NR4A1 but only **6 of 7** against NR4A2 (I531 is Ile in both), so of
the 5 engageable handles only **4** distinguish NR4A3 from NR4A2. **The programme has more discriminating
power against the paralogue whose sparing is mandatory, and less against the one it has no bound on.**

⭑ **The consequence nobody has written down.** A symmetric brief — "be selective over both" — is a harder
design target than the biology asks for and is 20 % thinner exactly where it is weakest. An **asymmetric**
brief is cheaper and more honest:

> **Hard constraint:** spare NR4A1 (the AML anti-target pair). **Soft constraint:** spare NR4A2 as far as
> the four handles allow, and treat the residual as an exposure question rather than a chemistry question.

**The exposure half — a lever, stated as a hypothesis and graded downward.** The HPA call that makes
NR4A2 the watch-zone is a *tissue* statement ("tissue enhanced", CNS/dopaminergic bias), not a potency
statement. So one way to reduce that half of the requirement is to restrict where the molecule goes rather
than what it binds — i.e. treat it as a biodistribution parameter instead of a ΔΔG. ⚠ **Three reasons this
is not a solution and must not be written as one.** (i) HPA also calls NR4A2 **"detected in all"** tissues,
so peripheral NR4A2 exists and a distribution restriction reduces rather than removes the liability.
(ii) The per-tissue nTPM field in [`nr4a-safety-genetics.json`](../modalities/nr4a-safety-genetics.json) is
`null`, so **the size of the reduction is unquantified** — $0 test 3 below fills it. (iii) Whether a
degrader of this class would in fact be CNS-restricted is a **property of a molecule that does not exist**,
and this repo holds no measured or predicted CNS-penetration datum for any NR4A candidate; nothing here
should be read as a claim about one. What is defensible today is only the shape of the argument: the NR4A2
half of the requirement has a non-chemical lever available to it and the NR4A1 half does not.

**Cheapest decisive $0 tests** (both networked → CI, both on the repo's own open-follow-up list):
1. **MGI single-KO phenotypes for *Nr4a1* / *Nr4a2* / *Nr4a3*** — the named remaining source after IMPC
   returned nothing. It is the only thing that would bound the NR4A2 question without a lab.
2. **HPA consensus nTPM per tissue for NR4A1/2/3** — fills the `null` field and sizes the CNS-vs-periphery
   split. `nr4a_safety_genetics.py` already talks to HPA; this is one more query.

**Effect on the requirement: RESHAPES.** Two symmetric hard targets → one hard target, one soft target
with a PK lever. It does **not** dissolve the requirement, and the route-3 hypothesis in the brief ("this
could dissolve the entire selectivity requirement") is **answered NO for any systemic molecule** — on the
strength of one specific, cited, mouse-genetic anti-target that happens to be exactly this drug's pair.

**Grade against the failure record: ★★ adopt now.** It costs nothing, it is a *narrowing* of a claim
rather than a new claim, and it inherits no instrument. It is the cheapest change to the programme's
hardest requirement available today.

---

### Route 2 — a covalent inhibitor (or covalent probe) at C397, instead of a degrader

**Rationale.** [Finding 2](#12--finding-2--the-requirement-is-a-measurement-problem-so-a-route-sidesteps-it-only-by-leaving-the-free-energy-axis):
the only selectivity axis this programme can state without an instrument that resolves ~1 kcal/mol is a
categorical one. NR4A3 has **three LBD cysteines the paralogues lack** — C397, C420, C559 — across all 20
conformers of the experimental 8XTT ensemble
([`nr4a3-covalent-handle-ensemble.json`](../modalities/nr4a3-covalent-handle-ensemble.json)). A residue the
paralogues do not have cannot be hit in them, at any affinity.

**What would have to be true.**

1. The electrophile must reach a unique cysteine from a pocket-bound anchor. It cannot reach from the
   warhead: the two cysteines *inside* the pocket band (C496, C536) are **conserved in all three
   paralogues and fully buried** — [§6a](./nr4a3-program-map.md#6a--dead--conclusively-unworkable-never-retry)
   files "covalent warhead at an NR4A3 pocket cysteine" as ✕ **dead**, *definitional*: a residue the
   paralogues share cannot discriminate between them. The unique cysteines sit **10.9–18.9 Å** out —
   tether range.
2. The thiol must be reactive, not merely present. ⛔ **No thiol pKa, intrinsic reactivity or adduct is
   computed anywhere in this repo** — the covalent artifact says so in its own `_limits`.
3. Occupancy must do something. This is where an inhibitor is *weaker* than a degrader here, and it must
   be said plainly: NOR-1 is constitutively active and its transcriptional output scales with **expression
   level** (Munck 2022, as cited in [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md)
   §1), which is exactly why degradation was chosen — *"an inhibitor would have to block a function NOR-1
   may not even gate on a pocket."* **A covalent inhibitor buys selectivity and gives up the mechanism
   argument.**

**What in this repo already bears on it.** Route B has already computed the geometry — for the *degrader*
case. [`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json) finds only
**C397** survives cleanly (C420 refuted in 0 of 60 cells; C559 at one cell), and branch 1b's counter-test
returns a result that looks bad for the route: **in 30 of 30 graded cells the first cysteine to come into
reach is a *paralogue* one**. ⚠ Read that with two caveats the roadmap attaches: the branch-1b prose is
**not yet reconciled to its landed artifact** (*"do not quote branch 1b's numbers yet"*), and *which*
paralogue cysteine closes the window differs by convention — under through-space it is NR4A1 C505, which
**aligns to NR4A3 C536**, so NR4A3 carries a cysteine there too and the reciprocal-uniqueness reading does
not apply; under corridor it is NR4A2 C534, aligning to NR4A3 **S565**, which NR4A3 genuinely lacks.

⭑ **The observation that makes this a distinct route rather than a re-label of Route B.** Every one of
those reach cells was enumerated for a molecule that must **also** present an E3 arm to solvent —
`build_smiles` places the E3 at a chain terminus, and the pendant slot carries the electrophile. **An
inhibitor has no E3 arm.** The geometric constraint that generated the 30-of-30 counter-result is
therefore *not the constraint an inhibitor faces*, and the enumeration has never been run in that
configuration. That is a strictly smaller search problem with one fewer terminus to satisfy, and it is
**free CPU**.

**Cheapest decisive $0 test:** re-run the reach enumeration with the E3 arm removed — anchor, pendant,
electrophile only — and ask whether C397's window still closes on a paralogue cysteine first. A negative
kills the covalent axis for inhibitors as well as degraders and is worth as much as a positive. (Do this
*after* the branch-1b reconciliation, which is already roadmap row 5 and also $0 — otherwise the
comparison has no baseline.)

**Effect on the requirement: RESHAPES.** It moves the paralogue claim from a thermodynamic ΔΔG the
instruments cannot resolve to a kinetic/categorical one at a residue the paralogues do not have. It does
**not** remove it — a paralogue cysteine can still be hit, which is exactly what branch 1b found.

**Grade against the failure record: ★★ promote.** It needs no de-novo-generated structure (the 8XTT
ensemble is experimental), no ternary, no E3, no ubiquitin geometry, and its claim does not reduce to a
~1 kcal/mol ΔΔG — so it clears both of the brief's grading-down criteria. Its real risks are named and
unglamorous: reach is necessary and never sufficient; the exposure criterion `V17` **fails its own
positive control** (NR4A1 Cys551, 0 of 25 frames), so "exposed" survives only as a threshold-free rank;
and every anchor inherits `V3`'s **INCONCLUSIVE** pose verdict.

⭑ **And a second use that is worth more than the drug.** The programme's single un-buyable requirement is
`R4` — *does anything bind the opened cryptic pocket* — which the roadmap calls the cheapest decisive
experiment in the programme and which *"needs a bench"*. A **covalent probe** is the cheapest form of that
experiment for a collaborator: an irreversible adduct gives an intact-mass or peptide-level readout
without SPR, ITC or a thermal-shift assay. Proposing the probe rather than the drug is a materially
easier ask of a wet-lab group, and it is the same molecule class.

---

### Route 3 — fusion-junction ASO / siRNA (already priority paper 2)

**Effect on the requirement: ⛔ REMOVES it entirely.** Base pairing discriminates on sequence, and neither
paralogue carries the junction. Nothing in this memo changes the existing plan; it is recorded here only
so the register is complete and so the comparison is explicit: **this is the only route in the programme
that removes the paralogue requirement *and* the wild-type-NR4A3 liability at once.** Its gate is
delivery — an engineering problem with active solutions, not a question about whether the biology works
([`fusion-selective-approaches-overview.md`](./fusion-selective-approaches-overview.md)).

⚠ **One new caveat from [finding 3](#13--finding-3--the-repo-holds-two-incompatible-models-of-the-fusion-protein).**
The ASO work is breakpoint-resolved and already models the junction as variable (390 modelled breakpoints,
243 favourable), so it is *less* exposed than the neoantigen route. But the exon-derived junction set it
scans comes from the same module whose resume index finding 3 flags. The $0 exon audit protects both.

---

### Route 4 — the ex-vivo pan-NR4A pole (CAR-T manufacturing additive)

**Rationale, cited.** CAR-T cells with all three NR4A genes knocked out show restored effector function
and tumour regression where wild-type CAR-T fails (Chen J, López-Moyado IF, … Rao A, *Nature* 2019;
**567:530–534**, *"NR4A transcription factors limit CAR T cell function in solid tumours"*), and the
effect is a **redundant-family** effect — so a *pan*-NR4A agent is what that application needs.

**Effect on the requirement: ⛔ REMOVES it, and it is the only place in the programme where the
cross-reactivity the whole selectivity effort exists to avoid is the *design goal*.** The reasons
selectivity is mandatory in vivo — the AML pair and the NR4A2 constraint above — are **chronic systemic
exposure** arguments. A transient, washed-out exposure in a culture dish does not create them.

**What is already banked.** [`nr4a3-pan-readout.json`](../modalities/nr4a3-pan-readout.json) carries the
pan pole as a *designed* result, not only by-catch: a conserved-core-ranked campaign makes pan the
dominant docking outcome (4 of 7, 0 paralogue-selective) with lead `denovo_9`, and endpoint multi-snapshot
MM-GBSA is favourable on all three (−28.3 / −23.9 / −20.7 kcal/mol). ⚠ Read at its true weight: this is
docking-and-endpoint tier, no molecule was synthesized, the functional endpoint is a wet-lab claim the
programme does not make, and the +4.44 NR4A3 lean sits inside noise (SD 5.47).

**What this memo adds.** The pan pole is currently used as a *reach-extending second application*. It is
also **the strongest available answer to "why is this target worth anything if paralogue selectivity is
unresolvable?"** — because one of the two poles does not need it. That argument is free and is not being
made.

**$0 test:** none needed; the readout exists. The work is a framing change in the paper.

**Grade: ★ under-used argument, already-banked evidence.**

---

### Route 5 — downstream of the fusion: PPARG and the transactivated nodes

**Rationale, cited.** The fusion binds a response element in the *PPARG* promoter and transactivates it
(Filion et al., *J Pathol* 2009, **PMC4429309**), and EMC tumours over-express PPARG and NDRG2 relative to
other sarcomas. PPARG is a nuclear receptor with **approved agonists** — attack the pathway where it is
tractable rather than the driver where it is not.

**Effect on the requirement: ⛔ REMOVES it.** Different target, different family, no NR4A discrimination
anywhere.

**What would have to be true:** that the fusion's PPARG transactivation is load-bearing for the tumour
rather than a marker, and that the useful direction is known. **The direction is the blocker** — the route
board has carried "agonism-vs-antagonism unresolved" since 2026-06 and it is a literature question, not a
compute question.

**$0 test:** resolve the direction from published EMC PPARG-axis data and TZD-in-sarcoma reports, in CI
(Europe PMC is reachable from a runner; the sandbox proxy blocks it).

**Grade: ★ keep, unblock cheaply.** It is the highest-readiness route on this list that removes the
selectivity requirement — approved drugs, no new chemistry — and it is stalled on one unanswered
literature question that nobody has spent an hour on.

---

### Route 6 — TCIP: co-opt the fusion instead of degrading it

**Rationale.** Bivalent "transcriptional chemical-induced proximity" molecules recruit a transcriptional
effector to a tumour-specific fusion TF rather than removing it, demonstrated on **EWSR1::FLI1** in Ewing
sarcoma. ⚠ **Citation status: auto-captured by the weekly field scan (2026-07-13), URL recorded in
[`../IDEAS.md`](../IDEAS.md), and it has *not* been through the repo's `verify-refs` check** — so it is a
lead, and it must be verified before it is quoted in any manuscript.

**Why it belongs on the board.** EWSR1::NR4A3 is the same object class as EWSR1::FLI1 — a FET
low-complexity domain fused to a DNA-binding effector — and the repo already carries the shared-mechanism
argument (Boulay et al., *Cell* 2017, doi:10.1016/j.cell.2017.07.036: the EWS prion-like domain retargets
BAF complexes). IDEAS.md flags it as *"may warrant a new row on the route board — for human review"* and it
has been sitting there since 2026-07-13 without one.

**What it changes about the requirement set, which is the interesting part.** A TCIP still needs an
NR4A3-LBD binder, so `R4` (something binds), `R5` (the pose) and `R7` (paralogue selectivity of the
binder) all survive unchanged. But it needs **no E3, no ternary with a ubiquitin ligase, no productive
lysine and no transfer geometry** — so it retires `R9` (our ternary correctly assembled — the roadmap's
*"whole remaining gap"*), `R10` and `R12` outright. Those three are, between them, the block behind rows
1, 18, 21 and 22 of the roadmap's ordered list.

**Effect on the requirement: RESHAPES** — same paralogue discrimination on the binder, far fewer
downstream requirements riding on it. And there is a genuine *effective* fusion-selectivity argument:
recruiting a repressive effector only matters where the fusion is bound on chromatin, so wild-type NR4A3
engagement is less consequential than it is for a degrader. ⚠ That is a mechanism argument, not a measured
one, and it must be labelled as such.

**Grade against the failure record: ★ new row — grade it, don't build it yet.** It inherits the same
induced-complex modelling problem as `R9` (an assembled ternary-like complex nobody has built), which is
the roadmap's largest gap — so it is not free of the failure record. What it *does* avoid is the
ubiquitination-geometry layer, where the programme has no known-answer test at all (`V18`).

**$0 test:** verify the citation through `verify-refs`; then a one-page grading against the register in
[§2](#2--the-route-register), and a row on `IDEAS.md`'s board.

---

### Route 7 — junction neoantigen (vaccine / TCR-T / soluble TCR)

**Effect on the requirement: ⛔ REMOVES it** — a peptide either is or is not presented; no paralogue
discrimination is involved. Already drafted
([`fusion-junction-neoantigen-paper.md`](./fusion-junction-neoantigen-paper.md)), and the class has real
external support in fusion-driven sarcoma (the overview memo records afami-cel's full approval in synovial
sarcoma and public-neoantigen TCRs for SYT-SSX and EWSR1-WT1, captured in `IDEAS.md` 2026-07-13).

**What this memo adds — and it is a caveat, not a promotion.** Per
[finding 3](#13--finding-3--the-repo-holds-two-incompatible-models-of-the-fusion-protein), every predicted
epitope is a peptide **spanning the seam**, and the seam's position is exactly what the two committed
fusion models disagree about. The epitope set is therefore conditional on an unreconciled model, and the
manuscript does not say so. **That caveat is free to add and it belongs there.**

**Grade: ○ unchanged** (tolerance to a mostly-self junction, a cold tumour, and partial HLA coverage were
already the stated doubts), **with one free correction owed.**

---

### Route 8 — the AND-gate bivalent degrader

**Effect on the requirement: NEUTRAL — and this is the memo's clearest example of a "fusion-selective"
route that does not touch the paralogue problem.** Its own §7 is explicit that arm 1 *"can additionally
carry"* the paralogue handles: the AND-gate adds a fusion-vs-wild-type layer **on top of** the paralogue
layer. Two requirements, not one replaced.

**Already computed, nothing free left.** Binding window 5.5× base case, ~11× ceiling, robust across the
synthesizable linker range; the **degradation** window is narrower and dose-fragile (~6.8× at
sub-saturating dose, eroding toward ~1× at saturation, and shrinking with positive cooperativity). Inputs
are illustrative assumptions, so flagged in the model and the manuscript.

**Grade against the failure record: ⏸ hold, and now for two reasons rather than one.** The stated blocker
is chemistry — *"no validated, selective, cell-active, chemically-tractable EWSR1-LC (or junction)
second-arm ligand currently exists"* (the 2026-07-13 erratum), and YK-4-279 / TK216 do not transfer. The
failure record adds a second: the design needs a modelled **folded-plus-disordered chimera**, i.e. a
structure generated de novo — the class that put two halves **32 Å** apart (`V12`, ⏸ parked). The brief
grades that down, and it should.

---

### Route 9 — synthetic-lethal / dependency partner

**Effect on the requirement: ⛔ REMOVES it** — different target entirely.

**Already run, and negative.** [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) §2b:
BRD9 mean gene effect **+0.11** in sarcoma and **+0.13, 0 % dependent** in Ewing — the one lineage where
the EWSR1-prion→BAF mechanism is established (Boulay 2017) — while BRD4 (−0.95), CDK7 (−1.85) and CDK9
(−1.46) are pan-essential with no window. The cheap transfer prior is spent, and the repo's standing
decision is **do not spend a scarce wet-lab slot on a transfer-justified BRD9 test.**

**$0 test that has not been run:** the repo found **one EMC line in DepMap** — ACH-001519 / H-EMC-SS,
expression only, CRISPR-dependency "[to verify]" as of 2026-07-03. Whether a later release has added
dependency data for it is a free query through the existing `depmap-dependency.yml` lane. It would not
make n = 1 decisive, but it is the only EMC-specific dependency datum that could exist without a lab.

**Grade: ⏸ parked on data, not on ideas.** The trigger is already on
[`../method-watch.md`](../method-watch.md): a new patient-derived EMC / FET-fusion model, or an improved
perturbation/DepMap-transfer model.

---

### Route 10 — a molecular glue instead of a PROTAC

**Rationale, and why it is more tempting than it should be.** A glue is smaller, has better physicochemical
properties, and — crucially — its selectivity is created **at the induced interface**, which is precisely
the programme's own thesis: close-paralogue degrader selectivity *"is created at the induced target–E3
interface … not at the conserved warhead pocket."* On the thesis alone, a glue is the modality that best
matches the mechanism.

**Why it grades down anyway, on the failure record.**

1. **The thesis's own second clause is the problem.** It continues: *"in every landmark case it was
   **discovered then rationalized** by a solved ternary structure, never predicted blind,"* and *"there is
   no validated prospective selectivity predictor in the field."* A glue is the modality most dependent on
   exactly that missing capability.
2. **It removes handles rather than adding them.** A PROTAC gives three independent selectivity mechanisms
   the roadmap names — divergent pocket handles, a linker-borne covalent handle at a unique cysteine, and
   the categorical unique-lysine term. A glue has no linker, so it has **no covalent axis and no designed
   exit vector**; the claim collapses back onto a single interface ΔΔG of the same ~1 kcal/mol size that
   no instrument here resolves.
3. **The repo has already met a glue interface and classified it as unstageable.** The E3-recruiter
   downselect found DCAF16's ligand **34 % buried with its partner removed** — *"a glue interface, not a
   handle pocket"* — which is the structural signature, recorded as a reason the recruiter could not be
   staged.

**Effect on the requirement: RELOCATES and WORSENS.**

**Grade: ⏸ watch, do not build.** The right action is a
[`method-watch.md`](../method-watch.md) row — *"a validated prospective molecular-glue design or
glue-interface selectivity predictor"* → re-grade this route — because a glue is the modality most likely
to arrive from someone else's screen rather than from this programme's design.

---

### Route 11 — target the EWSR1 half at the protein level

**Effect on the requirement: ⛔ RELOCATES it onto an essential gene, which is worse than where it started.**

**Two independent reasons, both already in the repo.**

1. **The EWSR1-LC is not fusion-specific.** The 2026-07-13 erratum on the AND-gate paper is explicit:
   wild-type EWSR1 carries the same N-terminal LC/transactivation domain. What is fusion-specific is the
   **covalent adjacency in cis** of EWSR1-LC to the NR4A3-LBD. An EWSR1-LC-directed agent therefore hits
   wild-type EWSR1.
2. **Wild-type EWSR1 is essential.** [`depmap-insilico-findings.md`](../modalities/depmap-insilico-findings.md)
   records EWSR1 gene effect **≈ −1.2**, attributed to its housekeeping RNA-binding role. So the trade is:
   stop discriminating against two dispensable paralogues (DepMap: NR4A1 0.5 % dependent, NR4A2 0.3 %) and
   start discriminating against a pan-essential one.

**Grade: ✕ down** as a protein-level target. ⚠ Scoped precisely: this closes *targeting the EWSR1 half on
its own*. It does **not** close the AND-gate (route 8), whose whole logic is that neither arm works alone,
nor the RNA-level junction routes (routes 3 and 7), which act on a sequence wild-type EWSR1 does not have.

---

### Route 12 — target the DBD / DNA binding

**Effect on the requirement: ⛔ WORSENS it, on arithmetic, for $0.**
[Finding 1](#11--finding-1--the-paralogue-problem-is-not-a-sequence-problem-and-the-80--framing-is-a-retracted-number):
the zinc-finger DBD is **92.8 %** identical to NR4A1 and **98.6 %** to NR4A2, against **59.4 % / 67.3 %**
for the LBD the programme already targets. The whole family also binds the same NBRE/NurRE elements
(the shared DNA-binding grammar recorded in
[`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md)), so the *functional* site is shared as
well as the sequence.

**Grade: ✕ down.** Recorded so it is not re-proposed. It is the intuitive move — "the fusion works through
DNA binding, so block that" — and it is the worst available place to stand on this target.

---

### Route 13 — fusion-selective *ubiquitination*: closed by a number the repo already owns

*This is the route the memo went looking for and did not find: a way for a shared-LBD binder to still be
fusion-selective. It is worth recording as a clean negative so it is not re-derived.*

**The idea.** Binding cannot discriminate the fusion from wild-type NR4A3 — the LBD is identical. But
**degradation is not binding**: it additionally requires a lysine in the E2~Ub transfer zone. Check B shows
the two proteins present *different* N-terminal acceptor sets — NR4A3's own AF1 carries **7 lysines**, the
EWSR1-LC that replaces it carries **1** (K144). If the productive ubiquitination site lay outside the
shared LBD, a single binder could degrade one and spare the other with no binding difference at all. That
would be a **categorical** fusion-vs-wild-type axis, immune to the resolution problem.

**Why it is closed.** The transfer zone is LBD-local, and the repo measured it:

- the ubiquitin-transfer distance is **17.1 Å**, measured as the nearest of 11 substrate lysines in a
  *solved* CRL4–CRBN assembly (validation requirement 5's 2026-07-25 measurement — and the repo's
  previously assumed 10 Å was ~7 Å too strict);
- the exposed NR4A3-unique lysines sit at **13.4 / 11.5 / 16.2 Å** from the cryptic pocket (K518, K572,
  K592 — [`nr4a-paralogue-unique-residues.json`](../modalities/nr4a-paralogue-unique-residues.json)).

Both numbers are **inside the shared LBD**. The differential lysines are ≥100 residues away on the far
side of the DBD and hinge, and no transfer zone anchored at the cryptic pocket reaches them. ⚠ Under
fusion model B ([finding 3](#13--finding-3--the-repo-holds-two-incompatible-models-of-the-fusion-protein))
the differential does not exist at all, because the AF1 is absent from the fusion — so the route fails
under one model and is unreachable under the other.

**Grade: ✕ closed, and cheap to have closed.** ⚠ Filed at the roadmap's strict bar this is a *route* closed
by measurements that already exist, not a proof of impossibility — a construct that anchored the E3 far
from the cryptic pocket would re-open the geometry question. It is recorded here rather than in the
roadmap's [§6](./nr4a3-program-map.md#6--the-closed-route-register) because it was never an open route
there; it is a hypothesis this memo generated and closed in the same pass.

---

## 5 · The $0 backlog this produces

Every item is free, none needs an authorization, and each is stated as an action rather than a topic.

| # | action | serves | why it is worth doing |
|---|---|---|---|
| **1** | **Audit the NR4A3 coding-exon offsets in CI and pin the EMC junction** | `R13`, routes 3 / 7 | ⛔ two committed models of the fusion disagree by ~360 residues; `R13` cannot be given a rung until the object is defined |
| **2** | **MGI single-KO phenotypes for *Nr4a1/2/3*** | route 1 | the only thing that would bound the NR4A2 half of the requirement without a lab; IMPC returned nothing and MGI is the repo's own named next source |
| **3** | **HPA per-tissue nTPM for NR4A1/2/3** | route 1 | sizes the CNS-vs-periphery split, i.e. how much of the NR4A2 liability a biodistribution lever could remove. The field is `null` today |
| **4** | **Re-run the linker-reach enumeration with the E3 arm removed** | route 2 | the 30-of-30 counter-result was computed under a constraint an inhibitor does not face. Run *after* roadmap row 5 (branch-1b reconciliation), or there is no baseline |
| **5** | **Resolve the PPARG agonist-vs-antagonist direction from the literature, in CI** | route 5 | unblocks the highest-readiness route that removes the selectivity requirement; approved drugs, no new chemistry |
| **6** | **Verify the TCIP citation through `verify-refs`, then give it a row on `IDEAS.md`** | route 6 | it has sat as an auto-captured lead since 2026-07-13 with an explicit *"may warrant a new row — for human review"* |
| **7** | **Re-query DepMap for CRISPR data on ACH-001519 / H-EMC-SS** | route 9 | the only EMC-specific dependency datum that could exist without a lab |
| **8** | **Add a `method-watch.md` row for prospective molecular-glue design** | route 10 | the modality most likely to arrive from outside; a trigger costs nothing and stops it being re-litigated |
| **9** | **Add finding 3 as a caveat to the neoantigen manuscript** | route 7 | its epitope set is conditional on an unreconciled model and does not say so |

⚠ **Items 1–3, 5 and 7 are networked and must run on a GitHub Actions runner**, not in the dev sandbox
(CLAUDE.md §6: the egress proxy blocks NCBI/GEO, PMC, Europe PMC, UniProt).

---

## 6 · The honest summary

**The selectivity requirement does not dissolve, and the specific reason is worth carrying.** The route
the brief hoped might dissolve it — accept paralogue cross-reactivity and argue tolerability — fails on
one cited, specific anti-target: combined *Nr4a1*/*Nr4a3* loss is the pair that gives mice AML, and that is
exactly the pair a non-selective NR4A3 degrader would remove (Mullican 2007, PMID 17515897; *Blood* 2018,
PMID 29343483). A route cannot argue its way past the one genotype it reconstitutes.

**But it is not one requirement, and treating it as one has cost the programme.** It is a hard NR4A1
constraint and a soft, unbounded NR4A2 constraint — and the programme currently has *more* discriminating
power against the hard one (5 engageable handles) than against the soft one (4). Writing the brief
asymmetrically is free and is the largest available reduction of the hardest requirement.

**Four routes remove the requirement outright, and every one of them does so by leaving the free-energy
axis** — RNA base-pairing, peptide identity, exposure regime, or a different target. That is the real
finding: on this target, selectivity is not won by better chemistry against the paralogues. Two more
routes reshape it into something categorical, which is the only axis this programme's instruments can
support. Three relocate it, and two of those land somewhere strictly worse.

**And the widest-blast-radius item was free and had been sitting in two committed files:** the repo does
not have one definition of the protein it is trying to drug. `R13` is not merely unpriced — its object is
undefined, and that is a sequence question, not a GPU question.

---

## References

*Every entry below is relayed from a repo document that already carries it; the "as cited in" column is
the repo's own provenance, per the fact-check discipline in `AGENTS.md`. Items not yet through
`verify-refs` are flagged. No citation here was generated for this memo.*

| citation | used for | as cited in |
|---|---|---|
| Mullican SE, et al. *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute myeloid leukemia.* **Nat Med** 2007. PMID **17515897**, doi:10.1038/nm1579 | the NR4A1+NR4A3 anti-target pair (route 1) | [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md); [`fusion-selective-andgate-degrader-paper.md`](./fusion-selective-andgate-degrader-paper.md) |
| *NR4A1/NR4A3 as functionally redundant suppressors of AML.* **Blood** 2018. PMID **29343483** | conditional double-KO unmasks HSC-homeostasis defects (route 1) | [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md) |
| Safe S, Karki K. *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* **Mol Cancer Res** 2021. doi:10.1158/1541-7786.mcr-20-0707 | wild-type NR4A3 tumour-suppressor roles (context for routes 1, 3, 8) | [`fusion-selective-andgate-degrader-paper.md`](./fusion-selective-andgate-degrader-paper.md) |
| Chen J, López-Moyado IF, … Rao A. *NR4A transcription factors limit CAR T cell function in solid tumours.* **Nature** 2019;**567**:530–534 | the pan-NR4A / exhaustion result behind route 4 | [`nr4a3-degrader-carT-and-family-druggability-framing.md`](./nr4a3-degrader-carT-and-family-druggability-framing.md) |
| Filion C, et al. **J Pathol** 2009. **PMC4429309** | the fusion transactivates a PPARG response element — routes 5 and 12, and the discriminating evidence in finding 3 | [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md) |
| Boulay G, et al. *Cancer-specific retargeting of BAF complexes by a prion-like domain.* **Cell** 2017. doi:10.1016/j.cell.2017.07.036 | FET prion-like-domain biology — routes 6, 9, 11 | [`fusion-selective-andgate-degrader-paper.md`](./fusion-selective-andgate-degrader-paper.md); [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) |
| Brien GL, et al. *Targeted degradation of BRD9 reverses oncogenic gene expression in synovial sarcoma.* **eLife** 2018 | the ncBAF/BRD9 comparator behind route 9 | [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) |
| **Zaienne 2022** — NOR-1/NR4A3 druggability evaluation, low-µM inverse agonist cmpd 19, **PMC9542104**; ⚠ **no NR4A1/2 counter-screen** (and *"Safe 2025 selective analogues"* is a review's loose paraphrase of the same compounds, **not** a distinct selective series — corrected in the repo 2026-07-12) | NR4A3 is experimentally ligandable | [`nr4a3-degrader-carT-and-family-druggability-framing.md`](./nr4a3-degrader-carT-and-family-druggability-framing.md) |
| **Munck 2022** — NOR-1 druggability; NOR-1 transcriptional output scales with expression level | route 2's occupancy caveat (why degradation was chosen over inhibition) | [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) §1. ⚠ cited there without a PMID — **resolve through `verify-refs` before quoting in a manuscript** |
| Nabet B, et al. *The dTAG system for immediate and target-specific protein degradation.* **Nat Chem Biol** 2018. doi:10.1038/s41589-018-0021-8 | the delegated fusion-dependence test that gates every driver-directed route | [`fusion-selective-andgate-degrader-paper.md`](./fusion-selective-andgate-degrader-paper.md) |
| Modern Pathology 2023, PMID **36948401** (58 EMC, 58/58 NR4A3-rearranged); Agaram et al., **Hum Pathol** 2014, **PMC4015728** | the fusion is near-invariant and clonal — the premise of the whole memo | [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md) |
| TCIP on EWSR1::FLI1 — https://pmc.ncbi.nlm.nih.gov/articles/PMC12851799/ | route 6 | ⚠ **auto-captured field scan, 2026-07-13, [`../IDEAS.md`](../IDEAS.md) — NOT yet through `verify-refs`** |
| DepMap 24Q4 · gnomAD · Human Protein Atlas · Ensembl · UniProt | routes 1, 9, 11, 12; findings 1 and 3 | committed queries: [`nr4a-safety-genetics.json`](../modalities/nr4a-safety-genetics.json), [`depmap-sarcoma-dependency.json`](../modalities/depmap-sarcoma-dependency.json), [`nr4a-sequences-cache.json`](../modalities/nr4a-sequences-cache.json), [`fusion-breakpoint-neoantigens.json`](../modalities/fusion-breakpoint-neoantigens.json) |

---

*Medical-integrity note: no clinical fact, statistic, citation or patient datum in this memo is fabricated.
Every quantitative statement is either read from a named committed artifact or produced by
[`target_route_census.py`](../modalities/target_route_census.py), whose output reproduces under `--check`.
No molecule was synthesized, no GPU or rented host was used, and no wet-lab work was performed or proposed
as a next step for this programme. Mouse-genetic and population-genetic results are reported as what they
are — germline loss in a model organism, and reproductive-fitness constraint in humans — neither of which
bounds adult transient pharmacological knockdown. Nothing here asserts activity in EMC, tolerability in a
patient, or clinical applicability.*
