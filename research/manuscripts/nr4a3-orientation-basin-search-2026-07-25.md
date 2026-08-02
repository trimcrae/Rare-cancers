# RUNG 5a — the mechanism-first orientation-basin search

> **Lane doc.** This is the record for nr4a3-program-map.md's RUNG 5a, the **$0 CPU** basin search that decision #4
> puts first ("run 5a's $0 basin search first — it tells us which exit vectors matter"). It is subordinate to
> [nr4a3-program-map.md](nr4a3-program-map.md); where they differ, nr4a3-program-map.md wins and this file is reconciled to it.
> Proposed nr4a3-program-map.md deltas are collected at the end rather than applied here.
>
> **Status:** engine built, unit-tested (42 tests), E3 arms staged from RCSB on CI, search executed. No GPU
> was used and none is requested by this rung. The optional MM-GBSA rescore in the 5a envelope was **not**
> run and is not recommended (see §7).
>
> **Language discipline applies throughout.** A surviving basin is a **nomination** — an input to a
> *predicted selective candidate* series — never a "selective hit". Nothing here implies efficacy, safety,
> a therapeutic window, or clinical readiness.

---

## 0. What this rung was asked to answer

nr4a3-program-map.md's prospective stage is **mechanism-first**:

```
paralogue-unique CHEMISTRY (nucleophile) + paralogue-unique GEOMETRY (lysine)
    → basins that exploit ONE of them → productive CRL geometry
    → interface thermodynamics used to RANK within the survivors
    → linker requirements → candidate molecules
```

and the Tier-2 kill-switch reads: *"No basin exploits a categorical handle **and** none even nominally
discriminates NR4A3 ⇒ STOP cheaply."*

The reason the search is mechanism-first, not orientation-first, is a number: a useful degradation window
needs **~2.0 kcal/mol** of true induced-interface margin against a best-case **resolvable** difference of
**1.12 kcal/mol**, so the marginal axis is *a confirmation tool operating near its limit, not a discovery
tool*. What this rung searches on instead is the two **categorical** axes, where NR4A1/NR4A2 are structurally
*incapable* rather than merely disfavoured.

---

## 1. What was built

| file | what it is |
|---|---|
| [`basin_geom.py`](../modalities/basin_geom.py) | pure-stdlib geometry + polymer-statistics kernels (18 tests) |
| [`nr4a3_e3_stage.py`](../modalities/nr4a3_e3_stage.py) | E3 arm staging from RCSB by **UniProt-accession set**, never by a remembered PDB ID |
| [`nr4a3_basin_search.py`](../modalities/nr4a3_basin_search.py) | the search itself (17 tests, shared file) |
| [`tests/test_basin_geom.py`](../modalities/tests/test_basin_geom.py) · [`tests/test_basin_search.py`](../modalities/tests/test_basin_search.py) | 35 unit tests, each against a closed-form or hand-constructed answer |
| `nr4a3-e3-arm-registry.json` | the staged arms (CI output) |
| `nr4a3-orientation-basins.json` | the search result (CI output) |

Everything is **pure stdlib** — the dev sandbox has no numpy/scipy/rdkit and this rung is $0 by design. The
network-touching parts run on a free GitHub Actions runner because the sandbox's egress proxy 403s RCSB at
CONNECT.

### The four kernels that carry weight

1. **Linker reach — the prolate-spheroid criterion.** A linker of contour length *L* tethered at the warhead
   exit vector **a** and the E3 ligand exit vector **b** can route its backbone through a point **p** only if
   `|p−a| + |p−b| ≤ L`. That is exact, and it is what makes term (a) a real constraint rather than a wish:
   reaching a cysteine and spanning to the E3 are paid for out of the **same** contour length. A pendant
   electrophile of reach *e* relaxes it by exactly `2e`. The reported **detour** — the excess focal sum over
   the straight anchor-to-anchor span — is the extra linker a chemist actually has to buy.
2. **A clamped nearest-atom distance field** with a *conservative* clash convention: the returned value is
   exact from the cell centre, so a query point sits up to half a cell diagonal away, and the clash test
   subtracts that slack before passing. Unit-tested to never miss a real overlap in 2 000 random probes.
3. **Worm-like-chain end-to-end density** (Thirumalai–Ha), which is the **accessibility** half of
   nr4a3-program-map.md's load-bearing piece 4. A Gaussian chain is wrong here — real degrader linkers are 3–16
   backbone atoms, far from the Gaussian limit, and a Gaussian assigns non-zero probability *beyond the
   contour length*, i.e. exactly where the answer matters.
4. **Horn quaternion superposition** (no SVD, so it is stdlib and exactly testable), used to put NR4A1/NR4A2
   into the NR4A3 frame so that **one** sampled set of E3 placements is evaluated against all three
   paralogues. That is what makes the comparison *matched*: a difference between paralogues cannot be an
   artefact of three independent searches finding different corners of orientation space.

---

## 2. Seven things the run itself corrected — each with the observation that forced it

Every item here was found by reading a real run's output or a real measurement, not by reasoning about the
code. They are recorded because several change what the result means, not just how it was computed.

### 2.1 The paralogue superposition is a **core** fit, and the discarded fraction is not negligible

A single global least-squares fit of all aligned Cα pairs gives **6.38 Å** for NR4A1 and **4.93 Å** for
NR4A2 — values that would make any paralogue comparison meaningless. Iterating with outlier rejection
converges to a structured core of **203/244 at 1.73 Å** (NR4A1) and **206/249 at 1.60 Å** (NR4A2), normal for
62 %/68 % sequence identity, while the discarded minority deviates by up to **32–37 Å**.

*Consequence that is now carried into the output:* a paralogue lysine sitting in one of those discarded
segments has an unreliable position in this frame, so a term-(b) claim about it is unreliable too. Every
paralogue lysine now carries its own post-fit deviation and a `position_reliable` flag, and a covered-but-
unreliably-placed lysine is reported separately rather than silently counted.

### 2.2 Basins are **target-surface patches**, not SE(3) micro-clusters — and the first clustering produced none

Clustering placements on landmark RMSD returned **zero** basins. That was not a bug: with an E3 of ~18 Å
radius, an 8 Å landmark RMSD corresponds to a ~25° rotation, and the measured fraction of accepted placement
**pairs** falling inside that is **0.09 %**. Closing the gap by sampling would need ~10⁷–10⁸ placements per
arm.

The fix is to cluster on the descriptor the scored terms actually depend on — the **interface fingerprint**,
the set of target residues the E3 contacts (5.5 % of pairs at Jaccard ≥ 0.5). Rotation of the E3 about the
tether that leaves the interface unchanged is a **real degree of freedom the complex explores**, so the right
way to report it is as a *frequency within the basin* ("in what fraction of this basin's placements does the
transfer zone cover a unique lysine?"), not as a forest of singletons.

### 2.3 The best ligand-bound recruiter structures are **PROTAC ternaries**, and a naive exit vector lands on the wrong warhead

The verified VHL entry is **5T35** (VHL–EloB–EloC + BRD4-BD2 + a 69-heavy-atom ligand) and the verified CRBN
entry is **6BOY** (CRBN–DDB1 + BRD4-BD1 + a 59-heavy-atom ligand). In both, the bound "ligand" is a whole
degrader — E3 binder + linker + a second warhead. Taking its most solvent-exposed atom as the E3 exit vector
returns a point on the **other** warhead, which would have anchored the entire linker-reach restraint tens of
angstroms away.

The fix uses information the structures genuinely contain: split the ligand by **which protein each atom is
closer to**, and take the exit vector as the E3-side atom furthest from the recruiter — the last atom before
the linker departs. (Related: the first run reported both arms' exit exposure as exactly **8.00 Å**, which is
the distance field's *clamp*, not a distance; ligand distances are now exact.)

### 2.4 The E2 catalytic cysteine was being **guessed**, and the guess was wrong

Version 1 identified it as "the SG furthest from the RING centroid" — a heuristic dressed as a measurement,
which returned **Cys111** of UBE2D1 out of four candidates spanning 27.7–35.4 Å.

The discriminating observation is in the structure. A CRL ubiquitylation assembly carries **ubiquitin**, and
the catalytic cysteine is by definition the one bearing ubiquitin's C-terminal glycine as a thioester. Scored
that way the answer is unambiguous: **Cys85 at 3.4 Å from ubiquitin's C-terminus, against 16.4 / 17.3 /
20.0 Å for the other three.** The function now refuses rather than guessing if no ubiquitin chain is present.

### 2.5 ★ The transfer distance was assumed at 10 Å; the solved assembly says **17.1 Å**

The same structure — a cryo-EM **CRL4–DDB1–CRBN–IKZF3–UbcH5a–Ub** ubiquitylation assembly — yields the
quantity term (b) would otherwise have to assume: the distance from the E2 catalytic cysteine to the
substrate lysine about to be modified. Measured, the **nearest substrate lysine sits 17.1 Å** from the
catalytic cysteine (n = 11 substrate lysines; 17.1, 17.3, 28.2, 31.1, 37.0, …).

The search's default was **10 Å**. It was therefore **~7 Å too strict** and would have suppressed term (b)
across the board — a parameter choice quietly deciding a gate. It is now calibrated from the assembly, with
the sweep spanning 10–21 Å so the category's dependence on the choice stays visible.

*Honest limit:* a deposited assembly is a snapshot poised for transfer, not the transition state, so the
measured distance is an empirically anchored **permissive** radius, not a proof of the productive one.

### 2.6 The VHL "receptor body" was **two copies of the complex**

5T35 deposits **two** copies of VHL–EloB–EloC (chains B, C, D and F, G, H). Taking "every chain annotated as
one of those three proteins" as the rigid body gives an object that is literally two complexes with a void
between them, roughly twice the real size — on which every clash test, contact count and interface score would
have been meaningless.

The same defect corrupted the bridge, and *that* is how it surfaced: pairing VHL from one copy with Elongin C
from the other drove the joint superposition to **5.2–7.3 Å over 124–237 Cα** and caused **every** VHL
cullin-scaffold candidate to be rejected, where the earlier single-protein bridge had succeeded at 1.38 Å.
Neither symptom announces itself as a chain-selection problem. Copy selection now enumerates one chain per
protein, keeps combinations whose chains **mutually contact**, and ranks by contact — refusing when there is a
real choice and nothing is coherent, and *flagging rather than refusing* when only one combination exists.

### 2.7 A zero-hit search was being read as a network failure

RCSB answers an empty search with **204 No Content and an empty body**, which urllib treats as *success* — so
it never reached the HTTPError branch and `json.loads('')` raised, four times. Five legitimately-empty "is
there a VHL + E2 + ubiquitin structure?" probes each reported *"POST failed after 4 tries"*, turning a real
negative answer into a fake infrastructure problem. An empty body **is** the answer.

---

## 3. ★ The result that matters most: a composed CRL RING is not a placement

This one was produced by a known-answer check built specifically to test the staging against itself, and it
**falsified the construction it was testing**.

Every arm's RING is *composed*: a ligand-bound receptor entry plus a separate cullin-scaffold entry, bridged
by superposition. Nothing in that pipeline says the composition lands the RING where an intact assembly puts
it — and the RING is what the entire term-(b) transfer zone hangs off.

| quantity | value |
|---|---|
| composed RING (CRBN–DDB1 entry + DDB1–CUL4A–RBX1 crystal), bridge quality | 808 DDB1 Cα @ **1.17 Å** |
| observed RING (intact CRL4–CRBN ubiquitylation assembly), bridge quality | 789 DDB1 Cα @ **1.41 Å** |
| **displacement between them** | **48.6 Å** |
| ligand exit vector → composed RING | 44.5 Å |
| ligand exit vector → **observed** RING | 32.3 Å |
| ligand exit vector → **observed E2 catalytic cysteine** | **12.0 Å** |

Both superpositions are excellent, so the 48.6 Å is **not error — it is conformation.** CRL4 is a rotational
scaffold whose DDB1 propeller pivots on the cullin, and an unengaged crystal scaffold and a substrate-engaged
assembly genuinely place the RING differently. **A composed RING is one arbitrary point on a very large arc,
not a placement.**

**What was changed as a result.** Where a solved intact assembly exists for a recruiter, the transfer zone is
now anchored on the **E2 catalytic cysteine observed in it**, bridged into the receptor's frame — one step
closer to the observable than a RING, and needing *no swing model at all*. Where no such assembly exists the
composed RING is still used, but it is labelled `composed_ring_MODEL` and carries the 48.6 Å figure as the
honest scale of its uncertainty.

**Why this is worth surfacing beyond this lane.** Any ternary/degradation-geometry modelling in this program
that places a RING or an E2 by composing two structures inherits this. It is a *quantified* reason to prefer
intact-assembly evidence, and a *quantified* caveat wherever composition is unavoidable.

---

## 4. What the search computes, per basin

- **Term (a) — electrophile reach.** Focal sum and detour to each NR4A3-unique cysteine (C397, C420, C559),
  the **minimum linker length** needed to place a pendant reversible-covalent electrophile on it, and the
  reachable fraction across a linker-length profile. A **conserved-cysteine control set** is scored the same
  way, so "reachability" can be seen to be selective for the unique ones or generic.
  *The paralogue side is categorical by sequence and needs no geometry: NR4A1/NR4A2 carry **no nucleophile**
  at the aligned positions (C397 → N363/S363, C420 → Q388/A389, C559 → Q528/Q528).*
- **Term (b) — transfer-zone lysine identity**, as set membership, evaluated on NR4A3 **and both superposed
  paralogues** with the same placement. The ordering is nr4a3-program-map.md's, with a paralogue-bare refinement on
  top, and the paralogue evaluation is the part that decides whether a basin is genuinely categorical:

  | rank | category |
  |---|---|
  | 5 | unique lysine only, **and both paralogue zones bare** |
  | 4 | unique + conserved, **paralogue zones bare** |
  | 3 | unique only |
  | 2 | unique + conserved |
  | 1 | conserved only |
  | 0 | none |

- **Term (d) — pose marginalisation.** The whole search runs over an ensemble of warhead exit-vector anchors
  and basins are matched across it; the **pose-surviving fraction** is reported per meta-basin.
- **Accessibility `P(B_k | d, s)`, kept separate from stability** (piece 4): the mean WLC end-to-end density
  over the basin's anchor–anchor spans, per candidate linker length. A basin beyond a linker's contour length
  scores exactly zero, however good its interface looks.
- **A unitless contact score** with preregistered, never-fitted weights, used **only to rank within** the
  categorically selected set.

### ★ Term (a) also has an E3-**independent** upper bound, and it changes what a negative means

If term (a) comes back empty there are two completely different reasons, and the basin search alone cannot
tell them apart:

- **(i)** the geometry is fine but no E3 body happens to dock in the region from which the linker could reach
  the cysteine — a fact about the **recruiter**, fixable by trying another one; or
- **(ii)** no credible linker can reach that cysteine from the pocket exit vector *while also spanning to an
  E3* — a fact about the **target**, which no recruiter choice can fix.

That is the difference between "widen the E3 panel" and "this mechanism is closed", and a negative result has
to say which it is to be worth publishing. The bound needs no E3 and is exact: fixing the warhead exit anchor
**a**, a linker of contour length *L* with a pendant arm *e* can put an electrophile on **SG** for an E3
anchor at **b** iff `|SG−a| + |SG−b| ≤ L + 2e`. The fraction of the reach shell satisfying it — rejecting
anchor positions inside the protein exactly as the search does — is an upper bound **no basin can exceed**.

**First read, over the real pose ensemble: C397 is not geometrically closed.** It opens at a **10-atom**
linker — inside the 12-atom practical gate — with C420 opening at 14 and C559 at 20. So any term-(a)
shortfall in this rung is about *where an E3 can dock*, not about the target's geometry.

⚠ **The envelope is POSE-ENSEMBLE dependent, and a small ensemble reports a pessimistic bound.** The same
E3-independent calculation returned **10 atoms** for C397 on a 6-pose ensemble and **14 atoms** on a 4-pose
one, because the smaller ensemble simply did not sample an anchor as close to C397 (exit-anchor→SG spanned
9.75–25.91 Å versus 16.07–25.91 Å). The bound is a **minimum over poses**, so more poses can only lower it:
every quoted figure is an **upper bound on the true minimum**, and the 12-pose production run is the
authoritative one. This is a sampling property of the ensemble, not a difference between recruiters — the
envelope never sees the E3 at all.

### Term (b) is scored against a null, and the gate requires beating it

Without a null, *"this basin's transfer zone covers K572"* is uninterpretable: if **any** linker-feasible,
clash-free placement covers a unique lysine at the same rate, the term carries no information and a
good-scoring basin is just a placement that exists. The background is computed over the **unclustered**
accepted set — the same population the basins were drawn from, with the one step that could enrich it
(clustering) removed — and the Tier-2 term-(b) limb requires a basin to **exceed** it, not merely to reach
rank 3. Term (a) has its own control in the same spirit: the **conserved** cysteines are scored identically,
so reachability can be seen to be selective for the unique ones rather than generic.

### The gate is not read at the sampling ceiling

At the permissive 20-atom sampling ceiling the focal-sum criterion admits almost any cysteine near the anchor
midpoint, so "reachable" would be nearly free and **term (a) could not fail**. A gate that cannot fail is not
a gate. The categorical limb is therefore read at a **practical 12-atom linker**, with the full length profile
reported so a reader can move it.

---

## 4b. Result (VHL preview, 600 k placements × 6 poses) — **Tier-2 GO, on the CATEGORICAL limb, but weakly**

The authoritative run is the 12-pose, 10⁶-placement, two-arm CI job; this is the VHL preview, and its shape is
what matters more than its exact numbers.

**The gate reads GO on the categorical basis** — 19 pose-marginalised meta-basins, 2 exploiting term (a) at
the practical linker gate, 12 exploiting term (b) above the null, 8 nominally discriminating. But the honest
reading is *weak*, and the machinery built to make it honest is what says so:

| meta-basin | poses | members | term (a): C397 min linker | term (b) rank | mean frac. covering a unique lysine | enrichment vs null | nominal Δ (unitless) |
|---|---|---|---|---|---|---|---|
| **M2** | 5/6 | 139 | **10 atoms** | **5** (unique-only, paralogues bare) | 0.010 | 3.2× | **+0.15 … +5.39** |
| M0 | 6/6 | 183 | **9 atoms** | 3 | 0.005 | 3.2× | −14.4 … −4.61 |
| M4 | 4/6 | 127 | 13 atoms | 5 | 0.034 | 2.9× | +0.85 … +3.92 |
| M6 | 4/6 | 104 | 23 atoms | 3 | 0.053 | 11.8× | −18.4 … −3.4 |
| M5 | 3/6 | 100 | 21 atoms | 5 | 0.080 | 6.5× | −24.5 … −15.6 |

**M2 is the strongest nomination**: it survives 5 of 6 warhead exit-vector poses, reaches C397 with a
**10-atom** linker (inside the 12-atom gate), reaches term-(b) rank 5, and is the only top basin whose cheap
contact score also points the right way. Its interface patch (UniProt 390–412 plus **572**) sits on the
NR4A3 surface *around K572 itself*.

**What must be said alongside it.**

- **The categorical terms fire in a small MINORITY of each basin's placements** — 0.5–8 % cover a unique
  lysine, and term (a)'s gate-level reach fraction is 2–5 %. These are enrichments over a background of
  1–3.5 %, not saturation. A basin is a region that *admits* the mechanism, not one that enforces it.
- **The null is what makes those numbers readable at all.** Background coverage of a unique lysine by any
  linker-feasible, clash-free placement is only 0.010–0.035, so the enrichments (2.9–11.8×) are real signal
  rather than a zone so large it covers everything. Had the null come back near 1.0, every basin's term (b)
  would have been meaningless — and with the *uncalibrated* 10 Å transfer distance it would instead have come
  back near 0 and suppressed the term entirely.
- **The term-(b) category is NOT robust to the transfer-zone sweep** in the basin examined in detail: it holds
  at the calibrated 17.1 Å but drops to rank 1 at the old assumed 10 Å with a tight RING radius. This is
  reported per basin (`sensitivity_robust`) and it is the single biggest soft spot in the term.
- **The best-populated basin (M0) has a NEGATIVE nominal Δ** — the cheap contact score favours the
  paralogues there. Under mechanism-first that does not disqualify it (the categorical terms are what
  nominate), but it is exactly the sort of thing that a scalar score would have hidden by averaging.
- Two NR4A1 lysines covered in the detailed basin sit in **badly-superposed loops** and are flagged
  `covered_but_unreliably_placed` rather than counted silently.
- **★ `term_b_best_rank` is a BEST-OF-N statistic and is inflated by construction.** It is the maximum over a
  basin's sampled placements, each of which is itself a maximum over the sampled E2 arc — precisely the
  winner's-curse artifact nr4a3-program-map.md's load-bearing piece 5 says a raw Pareto set still admits. The
  unbiased quantities are the **mean fractions** (0.005–0.08 covering a unique lysine, 0.0–0.061 with the
  paralogue zones bare), and they are the numbers the table above leads with. **The gate's term-(b) count is
  therefore an upper bound on how many basins genuinely carry the mechanism, and should be read as one.**
  A basin selected on `best_rank` alone would be a selection artifact; requiring it to beat the null is what
  keeps the count meaningful, and even then the count is optimistic.

## 4c. Result (CRBN preview, 500 k placements × 4 poses) — GO on term (b) only, and more weakly

| | VHL (backfill / **E3-choice sensitivity control**) | CRBN (Pareto front) |
|---|---|---|
| meta-basins | 19 | 21 |
| exploiting **term (a)** at the 12-atom gate | **2** | **0** |
| shortest C397 linker over basins | **9 atoms** | 15 atoms |
| exploiting **term (b)** above the null | 12 | 12 |
| enrichment over null (top basins) | 2.9–11.8× | **1.06–5.6×** |
| background: any NR4A3 lysine covered | 0.35–0.49 | **0.81–0.96** |
| top pose-surviving fraction | **6/6 = 1.00** | 3/4 = 0.75 |

**Two things worth stating carefully.**

1. **The E3-choice sensitivity control earned its place.** Term (a) is reachable at a 9–10-atom linker in the
   VHL arm and **not at all** at the gate in the CRBN arm. On CRBN alone this rung would have concluded that
   term (a) fails; the control shows it is **E3-dependent, not closed**. That is precisely what a controlled
   variable is for. **It is not a CRBN-vs-VHL preference and must not be read as one** — the E3 lane reports
   the two as tied on its own axes (margin 0.033 in open solid angle, one conformer each), VHL is a labelled
   backfill, and the axis here is a different one entirely.
2. **CRBN's null is much higher** (0.81–0.96 of placements cover *some* NR4A3 lysine, versus 0.35–0.49 for
   VHL), because its observed transfer anchor sits only 12.9 Å from the ligand exit vector while VHL's sits
   30.9 Å away. A high background is exactly the regime where term (b) discriminates least, and it shows: one
   CRBN basin reaches rank 4 while scoring **below** background (0.82×) and is correctly **excluded** by the
   gate. Without the null it would have been counted.

---

## 5. Honest scope

Everything is conditional on the hypothesised **cmpd19 binary pose × the chosen receptor frame** — a *double*
conditionality. This repo holds **no cmpd19 pose in the matched-model frame** (cmpd19 has no solved NR4A3
co-crystal at all, only functional target engagement), so the warhead exit vector is **marginalised over an
ensemble** of pocket-mouth anchors rather than asserted, and the surviving-fraction column is the honest
measure of how pose-dependent each basin is. Sequence-level uniqueness of C397/K572 is pose-independent; only
the reach estimate is conditional.

Other limits, all written into the output JSON:

- One static opened conformer per paralogue. C397's exposure (RSA 0.395) is conformer-dependent; the matched
  NR4A1/2 MD-ensemble add-on that would give its *distribution* has **not** been run.
- Rigid-body, side-chain-rigid, no solvation, no induced fit. **A basin is a nomination of a region of
  orientation space, not a modelled complex.**
- **Term (b) raises the odds; it does not guarantee the paralogue is spared.** Real degraders often
  ubiquitinate several lysines, and lysine-less substrates can still be degraded via N-terminal/Ser/Thr/Cys
  ubiquitination.
- LBD-only: hinge/DBD/EWSR1 lysines are absent from these models. The EWSR1 moiety was checked and contributes
  only 1–2 lysines, so it is not a design axis, but the LBD lysine set is not the complete site set.
- **A covalent handle is an unresolved liability, not an upgrade.** Electrophile promiscuity cannot be checked
  without chemoproteomics, and it must be reported alongside the parent warhead's published MYC induction.
  Prefer **reversible-covalent** (cyanoacrylamide-type) chemistry so catalytic turnover survives — an
  irreversible adduct makes the degrader stoichiometric.
- Language: **"predicted selective candidate"**, never "selective hit". No efficacy, safety,
  therapeutic-window or clinical claim is made or implied.

---

## 6. Coordination with the E3 lane

**The E3 lane's FINAL downselect is `advanced = [CRBN, VHL]`, with CRBN the sole Pareto-front member and VHL
a labelled backfill.** Its contract is consumed through its own `load_advanced()` API — never by reading its
raw JSON shape, which it declares unstable — and three parts of that contract are honoured here:

1. **`anchor_xyz` + `exit_direction`** are adopted as the recruiter-side attachment point where they verify.
   They are *verified, not trusted*: the lane computes them on **biological assembly 1 (mmCIF)** while this
   script downloads the **asymmetric unit**, and those are not always the same frame — a coordinate handed
   across a frame boundary lands silently in the wrong place while every downstream distance still looks
   reasonable. `adopt_lane1_anchor` accepts the anchor only if it lands within 0.5 Å of a ligand heavy atom
   in the frame actually loaded, tries the biological assembly first, and **refuses** otherwise. Either way
   the distance between the lane's anchor and this lane's independently derived exit atom is reported — two
   independent derivations of the same quantity is a free consistency check, and neither agreement nor
   disagreement is allowed to pass unmeasured.
2. **`caveats` is carried into the output**, per the lane's requirement, on every arm and every report.
3. **VHL is a BACKFILL, not a co-winner.** The CRBN−VHL margin is 0.033 in open solid angle on one conformer
   each, which that lane reports as a tie. VHL is therefore the **E3-choice sensitivity control** — it is
   present so the E3 is a *controlled variable* — and this rung **does not report any CRBN-over-VHL
   preference**. The output stamps `_role` on a backfilled arm saying exactly that.

### Why the anchor could not be adopted yet — two concrete, diagnosed reasons

Staging was re-run against the lane's own chosen entries, and the anchor adoption **refused** in both cases.
The reasons are specific and were read out of the run, not inferred:

- **VHL / 9GIO — 404: the entry has no legacy PDB-format file.** This staging downloads `.pdb`; the lane
  works in **mmCIF biological assemblies**. Large and recent entries are frequently mmCIF-only, so this is a
  standing gap, not a one-off.
- **CRBN / 9CUO — the entry does not contain DDB1.** It is a CRBN-only structure. That is not an error on
  either side: the lane measures the **recruiter's** exit vector, for which a recruiter-only frame is
  appropriate, while this rung needs the whole **CRL arm** as a rigid docking body, because the omitted
  partner (DDB1 here, Elongin B/C for VHL) is a real steric occluder against the target.

**So the contract bridge is a superposition, not an entry match.** The right integration is to superpose the
lane's recruiter frame onto this rung's arm frame and map `anchor_xyz` across, rather than requiring both to
use the same deposited entry — plus mmCIF support so the lane's frames are loadable at all. Until that lands,
the authoritative result uses this rung's independently derived exit vector, and every arm record carries the
refusal with its reason rather than silently falling back.

> **★ RESOLVED 2026-07-25 by LANE 7 — read
> [nr4a3-transfer-anchor-and-handle-risk-2026-07-25.md](./nr4a3-transfer-anchor-and-handle-risk-2026-07-25.md).**
> The observation was run. Measured with **no composition** inside 8R5H, the exit vector sits **30.76 Å** from
> the E2 catalytic Cys93; **this rung's staging (5T35) reproduces it to 0.09 Å**. In a common frame the two
> mapped E2 cysteines agree to **0.02 Å** while the exit vectors differ by **50.67 Å**, so **neither** listed
> hypothesis is right: it is an **exit-vector defect** in the other registry, whose "recruiter ligand" is a
> fragment bound to **Elongin C** (6.87 Å from the nearest VHL atom). `pick_ligand` tested contact against the
> receptor *body* rather than the *recruiter*; fixed, with a unit test, and verified to leave this rung's arms
> bit-identical. **The transfer zone does NOT carry ~40 Å of frame-to-frame variation from this source, and
> the VHL basin ranking below stands.** The paragraph that follows is retained as the record of what was open.

**A second, unresolved observation, recorded because it is decision-relevant.** Staging VHL from two
different (both legitimate, both verified) receptor entries put the *observed* transfer anchor **30.9 Å** and
**69.9 Å** from the ligand exit vector respectively. Both were bridged from the same intact assembly at good
RMSD. Two hypotheses — a different copy selected within the source assembly, or genuinely different CRL arm
conformers — and **this lane has not run the observation that discriminates them.** It is not diagnosed, and
it is the top follow-up: it says the transfer-zone placement carries frame-to-frame variation of the same
order as the 48.6 Å composed-RING uncertainty in §3, which would weaken term (b) further if it is real.

### ★ A finding that argues for a THIRD downselect axis

An interim state of that lane's Pareto (before its final result) advanced **BIRC2 and MDM2** instead. Staging
them is worth recording, because it produces an axis neither ranking contains — and because it *agrees* with
where the lane's final answer landed.

I first argued that BIRC2/MDM2 were structurally fortunate: they are **monomeric RING** E3s, carrying their
own RING in the *same chain*, so — unlike a cullin–RING recruiter whose RING sits 40–70 Å away on a separate
polypeptide — they would need no composition and would inherit none of §3's 48.6 Å uncertainty.

**Staging them refuted that, and the evidence is unambiguous.** Both staged cleanly, at superb resolution,
and then returned `PARTIAL_no_transfer_geometry`. The reason is not a gap in ubiquitylation structures; it is
which *fragment* the ligandable structures actually are:

| arm | staged entry | residues present | fraction of full length | what that domain is |
|---|---|---|---|---|
| **BIRC2** | 4HY4, **1.25 Å** | **255–346** | **15 %** of 618 | the BIR3 domain — the SMAC-mimetic site |
| **MDM2** | 6Q9L, **1.13 Å** | **18–111** | **19 %** of 491 | the p53-binding domain — the nutlin site |
| VHL | 5T35, 2.7 Å | 61–209 (+EloB/EloC) | 70 % | the intact VHL–EloB–EloC module |
| CRBN | 6BOY, 3.33 Å | 44–427 (+DDB1) | 85 % | the intact CRBN–DDB1 module |

**The catalytic RING of BIRC2 and MDM2 is not in these structures at all.** It lies hundreds of residues away
at the C-terminus, and the ligandable domain and the RING are *separately crystallised fragments joined by a
long unstructured region that no deposited structure spans*. So "the RING is in the same polypeptide" does
**not** mean its position is known — it means it is attached by a several-hundred-residue flexible tether,
which leaves the transfer zone **less** determined than a composed CRL RING, not more. My earlier claim was
backwards and is retracted here rather than quietly dropped.

**The decision-relevant consequence, and it is constructive rather than a conflict.** Term (b) — one of the
two categorical axes the entire mechanism-first reframe rests on — **cannot be evaluated at all** for BIRC2
or MDM2, while it *can* be evaluated from **directly observed** geometry for **CRBN (9UUM) and VHL (8R5H)**
— which are precisely the two the E3 lane's final downselect advanced. So the two analyses **agree**, by
different routes: ligandability + exit geometry and ubiquitination-geometry evaluability both land on
CRBN + VHL.

That agreement is the reason to add the axis rather than to argue about a ranking. A downselect run on
ligandability and exit-vector geometry **cannot see** whether the transfer zone is placeable, because it
never asks where the RING is; here it happened to coincide, and on a differently-composed panel it would not
have. **Ubiquitination-geometry evaluability belongs in the Pareto set as its own axis**, with a concrete
test: *does a solved assembly place this recruiter's RING (or its E2) relative to its ligand-binding site?*
For BIRC2 and MDM2 the answer is no, and no amount of ligand quality changes it.

---

## 6b. Exact nr4a3-program-map.md deltas proposed by this lane

*This lane does not edit nr4a3-program-map.md (four lanes run concurrently and the orchestrator owns it). These are the
precise changes to apply, each with its evidence.*

**D1 — RUNG 5a status.** `[ ] 5a · Orientation-basin search, mechanism-first — ~$0–50 (CPU $0 + optional
MM-GBSA rescore) · Cum. ~$129` → **`[x]` … DONE 2026-07-25 · $0 REALIZED**, with the gate verdict. The
optional MM-GBSA rescore was **not** run and is recommended against (§7).

**D2 — the Tier-2 kill-switch row.** In §"The hard kill-switch", tier 2's status `pending (RUNG 5a)` → the
verdict, and it should record *both* limbs and the null, because "GO" alone overstates it: the categorical
terms fire in a minority of each basin's placements (0.5–8 % for term (b), 2–5 % for term (a) at the gate)
against a background of 1–3.5 %, i.e. **2.9–11.8× enrichment, not saturation.**

**D3 — the ladder total (DERIVED, must be regenerated, never typed).** In
[`pinned-figures.json`](pinned-figures.json) → `derivations.ladder_total.non_tool_stages`, the entry
`"5a_basin_search": [0.0, 25.0, 50.0]` should become `[0.0, 0.0, 50.0]` — the **mid becomes the realized $0**,
exactly the convention the same block already applies to `valA_mini` ("valA_mini's mid is its REALIZED ~$0 on
GCP credit, not the midpoint of its 0–15 band"). That moves `expect_mid` from 194 to **169**; regenerate with
`vast_cost_model.py` rather than editing the total, and register the superseded value in the same commit per
CLAUDE.md rule 1.3.

**D4 — two new measured figures, both from solved structures, both currently absent from the plan.**
Add under reviewer requirement 5 ("full CRL/E2~Ub geometry ensembles"):
- the substrate-lysine → E2-catalytic-cysteine distance is **17.1 Å**, measured in a solved CRL4–CRBN
  ubiquitylation assembly (nearest of 11 substrate lysines). Any ubiquitination-geometry model that assumes a
  tighter zone — this repo's own default was 10 Å — is too strict by ~7 Å;
- **a composed CRL RING carries ~48.6 Å of positional uncertainty.** Composing a RING from a receptor entry
  plus a separate cullin-scaffold entry, with both bridges better than 1.5 Å, put it 48.6 Å from the RING of
  an intact assembly. **This applies to any ternary or degradation-geometry modelling in the program that
  composes a RING or an E2 position**, not just to this rung. Prefer intact-assembly evidence; where
  composition is unavoidable, carry this as the caveat.

**D5 — §MECHANISM-FIRST gains a sharpening.** Term (a) is **not geometrically closed**: C397 opens at a
**10-atom** linker on an E3-independent bound (C420 at 14, C559 at 20). So a term-(a) shortfall is a fact
about *which recruiters dock where*, not about the target — which is an argument for widening the recruiter
panel rather than abandoning the axis.

**D6 — the E3 downselect gains a THIRD axis: is the transfer geometry evaluable at all?** The E3 lane's final
downselect (`advanced = [CRBN, VHL]`, CRBN on the front, VHL a labelled backfill) and this rung's
ubiquitination-geometry evaluability **agree**, by different routes. But that agreement was not guaranteed:
staging the two recruiters an interim Pareto had advanced (**BIRC2**, **MDM2**) shows term (b) **cannot be
evaluated** for either — their ligandable structures are the **BIR3 domain (255–346, 15 % of BIRC2)** and the
**p53-binding domain (18–111, 19 % of MDM2)**, and the catalytic RING, hundreds of residues away across a
region no structure spans, is absent. A ligandability-and-exit-vector Pareto cannot see that, because it
never asks where the RING is. RUNG 5a's downselect rationale should carry the axis explicitly, with the test
stated: *does a solved assembly place this recruiter's RING or E2 relative to its ligand-binding site?*
**And VHL must be recorded as the E3-choice sensitivity control, not a co-winner** — the CRBN−VHL margin is
0.033 in open solid angle on one conformer each, which is a tie; no CRBN-over-VHL preference is reportable
from this rung.

---

## 7. On the optional MM-GBSA rescore in the 5a envelope

**Not run, and not recommended.** It is a GPU step, and it would refine the one axis this rung is explicitly
*not* deciding on. nr4a3-program-map.md's Tier-2 asymmetry is the argument: cheap scoring nominates on **geometric set
membership**, which it answers reliably, and is not trusted to adjudicate a ~1 kcal/mol energy difference — an
MM-GBSA rescore buys a better number on the axis that needs ~2.0 kcal/mol of true margin against a resolvable
1.12, which is the axis the whole mechanism-first reframe demoted. The next spend on the ladder should be
**5a-KS**, the ligand-side double difference, not a better interface score.
