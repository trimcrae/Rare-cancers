# RUNG 5a — the mechanism-first orientation-basin search

> **Lane doc.** This is the record for STRATEGY.md's RUNG 5a, the **$0 CPU** basin search that decision #4
> puts first ("run 5a's $0 basin search first — it tells us which exit vectors matter"). It is subordinate to
> [STRATEGY.md](../../STRATEGY.md); where they differ, STRATEGY.md wins and this file is reconciled to it.
> Proposed STRATEGY.md deltas are collected at the end rather than applied here.
>
> **Status:** engine built, unit-tested (35 tests), E3 arms staged from RCSB on CI, search executed. No GPU
> was used and none is requested by this rung. The optional MM-GBSA rescore in the 5a envelope was **not**
> run and is not recommended (see §7).

---

## 0. What this rung was asked to answer

STRATEGY.md's prospective stage is **mechanism-first**:

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
   STRATEGY.md's load-bearing piece 4. A Gaussian chain is wrong here — real degrader linkers are 3–16
   backbone atoms, far from the Gaussian limit, and a Gaussian assigns non-zero probability *beyond the
   contour length*, i.e. exactly where the answer matters.
4. **Horn quaternion superposition** (no SVD, so it is stdlib and exactly testable), used to put NR4A1/NR4A2
   into the NR4A3 frame so that **one** sampled set of E3 placements is evaluated against all three
   paralogues. That is what makes the comparison *matched*: a difference between paralogues cannot be an
   artefact of three independent searches finding different corners of orientation space.

---

## 2. Five things the run itself corrected — each with the observation that forced it

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
  paralogues** with the same placement. The ordering is STRATEGY.md's, with a paralogue-bare refinement on
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

### The gate is not read at the sampling ceiling

At the permissive 20-atom sampling ceiling the focal-sum criterion admits almost any cysteine near the anchor
midpoint, so "reachable" would be nearly free and **term (a) could not fail**. A gate that cannot fail is not
a gate. The categorical limb is therefore read at a **practical 12-atom linker**, with the full length profile
reported so a reader can move it.

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

The parallel recruiter lane stages the widened ligandable panel and downselects it; its output is consumed by
`arms_from_lane1()` rather than duplicated. One structural distinction is added here because a flat recruiter
list hides it, and it changes how much modelling term (b) requires:

- a **cullin–RING recruiter** (VHL, CRBN, the DCAFs, KEAP1, FEM1B) is a substrate receptor bolted onto a
  cullin, so its RING is 40–70 Å away on a separate polypeptide and must be composed in — inheriting §3's
  48.6 Å uncertainty;
- a **monomeric RING E3** (BIRC2, MDM2, RNF114) carries its own RING in the **same chain**, so the RING needs
  no composition at all and its position is fixed relative to the ligand by covalent geometry.

That makes the monomeric arms structurally *cheaper to be confident about* on term (b), independent of any
ligandability ranking.

---

## 7. On the optional MM-GBSA rescore in the 5a envelope

**Not run, and not recommended.** It is a GPU step, and it would refine the one axis this rung is explicitly
*not* deciding on. STRATEGY.md's Tier-2 asymmetry is the argument: cheap scoring nominates on **geometric set
membership**, which it answers reliably, and is not trusted to adjudicate a ~1 kcal/mol energy difference — an
MM-GBSA rescore buys a better number on the axis that needs ~2.0 kcal/mol of true margin against a resolvable
1.12, which is the axis the whole mechanism-first reframe demoted. The next spend on the ladder should be
**5a-KS**, the ligand-side double difference, not a better interface score.
