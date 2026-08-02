# Does the CATEGORICAL case survive paralogue dynamics? — matched NR4A1 / NR4A2 / NR4A3 ensembles

> **Lane doc (LANE 13).** Tier 2's GO was won on the **CATEGORICAL** basis: NR4A3 carries reactive residues
> both paralogues lack, so the paralogues are structurally *incapable* rather than merely disfavoured. That
> basis matters because the **marginal** axis needs ~2.0 kcal/mol against a resolvable difference this lane doc
> **originally** put at ~1.12, calling it *"a confirmation tool operating near its limit, not a discovery tool."*
> ⚠ **Both quotations are SUPERSEDED and retained only as the framing this lane ran under** — the replicate SD
> was measured on 2026-07-30 and the current pair lives once, in nr4a3-program-map.md §MECHANISM-FIRST (STRATEGY.md Appendix A row
> 53). **Nothing in this lane's result depends on either**: it is a categorical, geometric measurement, and the
> quotation appears here only to say why the categorical basis was worth testing.
>
> The NR4A3 side of the categorical case is now well characterised over 100 conformers. **The paralogue side
> had only ever been tested on ONE static opened conformer each**, and nr4a3-program-map.md names the matched paralogue
> ensembles as the open cheap add-on in two places. This lane runs them and asks the question they were for:
> **do paralogue DYNAMICS open a compensating site?**
>
> Subordinate to [nr4a3-program-map.md](nr4a3-program-map.md); this lane does not edit it. Exact deltas are in §6.
> Language discipline applies throughout: nothing here implies efficacy, safety, a therapeutic window or
> clinical readiness, and every result is design prioritisation, not validation.

---

## 1. The question, sharpened — and why the committed analysis could not answer it

A degrader **does not care which cysteine it labels.** The categorical claim is not "NR4A1 lacks a cysteine at
the position aligned to NR4A3 C397" — that is a sequence fact and it is not in dispute. The claim that carries
weight is the stronger one: *at the geometry where this construct's electrophile reaches NR4A3, no paralogue
nucleophile is in range.* Two things in the committed pipeline mean that stronger claim had never been tested.

**(i) Term (a) was only ever scored on the three NR4A3-UNIQUE cysteines.**
`nr4a3_basin_search.run_arm_pose` builds its term-(a) block from `ctx["reactive"]["unique_cysteines"]`; the
conserved set is summarised as a single count at the **20-atom sampling ceiling** (`cons_reachable/cons_total`)
and never evaluated at the 12-atom gate. So the headline *"all 7 term-(a) meta-basins reach C397 and only
C397"* is a statement about **{C397, C420, C559}**. NR4A3's four conserved cysteines — C496, C506, C536, C594 —
have exact paralogue homologues (NR4A1 C465/C475/C505/C566; NR4A2 C465/C475/C505/C566), so a conserved NR4A3
cysteine inside the gate would be a **non-discriminating** electrophile target, and no statistic in the
committed run would show it.

**(ii) The paralogue side was one static conformer.** `nr4a1-opened.pdb` / `nr4a2-opened.pdb` are single
opened models. Exposure and reach both fluctuate substantially over MD — the committed NR4A3 numbers show
C397's RSA ranging 0.108–0.673 and C420's median 0.186 with a maximum of 0.451 — so a paralogue cysteine that
looks marginal in one frame can be well inside the criterion in a populated conformer.

## 2. What was built

| file | what it is |
|---|---|
| [`nr4a_paralogue_dynamics.py`](../modalities/nr4a_paralogue_dynamics.py) | the analysis: every cysteine of every species, per conformer, on two independent tests + the matched E2~Ub transfer-zone lysine comparison + the categorical verdict |
| [`nr4a-paralogue-dynamics.json`](../modalities/nr4a-paralogue-dynamics.json) | its output |
| [`Dockerfile.nr4ametad`](../compute/Dockerfile.nr4ametad) | the baked metad/release stack (openmm + openmm-plumed + pdbfixer + mdtraj + biopython) — the exact package set `sagemaker_src/entry_metad.py` created on the fly for the NR4A3 run |
| [`nr4a_paralogue_release.py`](../modalities/nr4a_paralogue_release.py) | `nr4a3_md_release` made TARGET-aware, plus frame export and a strided heavy-atom trajectory |
| [`nr4a_paralogue_md_job.py`](../modalities/nr4a_paralogue_md_job.py) | resume-safe host driver (metad `NS` is a SEGMENT length, so remaining work is read from the manifest **and** the trajectory's own frame count) |
| [`nr4a_paralogue_md_vast_launch.py`](../modalities/nr4a_paralogue_md_vast_launch.py), [`nr4a_paralogue_md_ops.py`](../modalities/nr4a_paralogue_md_ops.py) | Vast launcher (offers ranked by all-in $/ns) and the CI-side status/watch/reap/collect |
| [`gpu-nr4a-paralogue-md-vast.yml`](../../.github/workflows/gpu-nr4a-paralogue-md-vast.yml) | the ladder: selftest → bake → smoke → launch → watch → collect → analyse |
| [`tests/test_paralogue_dynamics.py`](../modalities/tests/test_paralogue_dynamics.py) | unit tests for every pure helper a wrong answer would be invisible in |

### 2.1 Two independent tests, deliberately

| | what it asks | why both |
|---|---|---|
| **A1 — E3-independent reach envelope**, per species in its OWN frame, on its OWN homologous cryptic pocket, with its OWN exit-vector pose ensemble | *could SOME construct put an electrophile on this cysteine?* | an **upper bound**: a cysteine closed here is closed for every recruiter, which is the right way to rule a site OUT |
| **A2 — matched-construct reach**, ONE placement set sampled on the NR4A3 reference frame, every conformer superposed into it | *at a placement where the construct reaches an NR4A3-unique cysteine, is a paralogue cysteine ALSO in budget?* | the **design question**. A1 over-counts when ruling a site IN; A2 holds the warhead anchor, the E3 anchor and the length budget fixed and asks about the same molecule |

A2's premise — that the paralogue's homologous pocket lands where NR4A3's is after superposition — is
**measured per frame** (`homologous_pocket_centroid_offset_A`) rather than asserted, because if that offset
were large the test would be measuring the superposition instead of the chemistry.

### 2.2 Term (b) is computed exactly, not sampled

The committed `transfer_zone` draws `n_e2_samples` E2 positions uniformly in a ball of radius
`observed_anchor_mobility_A` about the **observed** catalytic cysteine and asks which lysines fall within the
**measured 17.09 Å** transfer distance. For a lysine at distance *r* that per-sample probability is the
sphere–sphere lens volume over the ball volume — a closed form — so the per-conformer comparison is not swamped
by Monte-Carlo noise. Validated against the committed sampler across the whole distance range: **max
|MC − analytic| = 0.0015–0.0089** over 11 distances (`--validate-coverage`, and a unit test).

---

## 3. RESULTS

*(§3.1–§3.4 are complete and needed no GPU. §3.5 lands when the matched paralogue ensembles finish.)*

### 3.0 The pipeline reproduces the committed NR4A3 numbers before it is asked anything new

Over the same **75 unbiased** NR4A3 conformers, this module's independent implementation returns
**C397 reachable at the ≤12-atom gate in 0.960** of frames (Wilson 95 % **0.889–0.986**) and **C420 and C559
in 0.000** — the committed `nr4a3-handle-ensemble.json` values (72/75 = 96 %, 0/75, 0/75) to three decimals.
C397's RSA median is **0.416**, again the committed value. So the differences reported below are the
deliberate ones in §2.1, not an incidental reimplementation drift.

### 3.1 The cysteine inventory — the reciprocal handles were never enumerated

Read off the two models with the same BLOSUM62 Needleman–Wunsch aligner the metad CV mapping uses, and
cross-checked against full-length UniProt (offsets **derived** from each construct's own sequence, not
hardcoded: NR4A3 +372, NR4A1 +347, NR4A2 +343):

| paralogue cysteine | aligns to NR4A3 | NR4A3 has a Cys there? |
|---|---|---|
| NR4A1 **C465** / NR4A2 **C465** | C496 | yes (conserved) |
| NR4A1 **C475** / NR4A2 **C475** | C506 | yes (conserved) |
| NR4A1 **C505** / NR4A2 **C505** | C536 | yes (conserved) |
| NR4A1 **C534** / NR4A2 **C534** | **S565** | **NO** |
| NR4A1 **C551** | *(no aligned NR4A3 residue)* | **NO** — the celastrol/NR-V04 covalent site |
| NR4A1 **C566** / NR4A2 **C566** | C594 | yes (conserved) |

So the family carries **reciprocal** categorical handles as well as NR4A3's: **both** paralogues have a
cysteine (C534) where NR4A3 has serine, and NR4A1 additionally has C551. Three of NR4A3's seven cysteines are
unique to it; **four are shared with both paralogues.**

### 3.2 ★ The reach envelope at the design gate is NOT specific to the unique cysteines — on either side

**A1, NR4A3 over 75 unbiased conformers.** Every cysteine, not the three the committed run scores:

| NR4A3 Cys | unique? | RSA median | fraction of frames at the ≤12-atom gate | Wilson 95 % | median shortest linker |
|---|---|---|---|---|---|
| **C397** | unique | **0.416** | **0.960** | 0.889–0.986 | 10 |
| C420 | unique | 0.186 | 0.000 | 0.000–0.049 | 16 |
| C559 | unique | 0.132 | 0.000 | 0.000–0.049 | 20 |
| **C496** | **shared with BOTH paralogues** | **0.023** | **0.387** | **0.285–0.500** | 14 |
| C506 | shared | 0.021 | 0.000 | 0.000–0.049 | 20 |
| C536 | shared | 0.000 | 0.000 | 0.000–0.049 | 20 |
| C594 | shared | 0.032 | 0.000 | 0.000–0.049 | 20 |

**In 39 % of unbiased NR4A3 conformers a CONSERVED cysteine — C496, whose homologue is NR4A1 C465 and NR4A2
C465 — is inside the 12-atom gate** (68 % in the biased metadynamics set). The committed pipeline could not
see this: it scores term (a) on the unique set and summarises the conserved set only at the 20-atom sampling
ceiling. **What closes C496 is not geometry, it is burial** — RSA median 0.023 against C397's 0.416.

**A1, the static paralogue models.** On the same criterion, at the same gate:

| | Cys | aligns to | RSA | at ≤12-atom gate | shortest linker |
|---|---|---|---|---|---|
| NR4A1 | **C465** | C496 (**shared**) | 0.138 | **yes** | **6** |
| NR4A1 | **C551** | *(none — the celastrol/NR-V04 site)* | 0.165 | **yes** | 10 |
| NR4A2 | **C465** | C496 (**shared**) | 0.011 | **yes** | 10 |
| NR4A2 | **C534** | S565 (**NR4A3 lacks**) | 0.120 | **yes** | 12 |

**Each paralogue presents TWO cysteines inside the design gate, and NR4A1's C465 opens at a SHORTER linker
(6 atoms) than NR4A3's own C397 (10).** So the geometric half of "structurally incapable" is false as stated:
on the reach criterion the program uses, the paralogues are not out of range.

**What still separates them is EXPOSURE, and only that.** Every paralogue cysteine inside the gate sits below
the 0.25 relative-SASA cutoff (0.011–0.165) while NR4A3's C397 sits at 0.395. **That is a single-frame number
on the paralogue side, and RSA is exactly the quantity that fluctuates most over MD** — C397's own range over
75 frames is 0.108–0.673, and C420's median 0.186 reaches 0.451. A residue at median 0.14 crossing 0.25 in a
material fraction of frames is not a remote possibility; it is the expected behaviour of a partially buried
side chain. **This is precisely the question the matched paralogue ensembles were run to answer.**

### 3.3 A2 — matched-construct collision, static models, 5 657 placements

Same placement, same warhead exit anchor, same E3 anchor, same length budget:

| linker atoms | P(NR4A3-unique reached) | **P(a paralogue Cys also reached \| NR4A3 reached)** | same, requiring RSA ≥ 0.25 | P(any Cys) NR4A3 / NR4A1 / NR4A2 |
|---|---|---|---|---|
| **12 (gate)** | 0.00106 | **0.000** | 0.000 | 0.0011 / 0.0002 / 0.0000 |
| 14 | 0.00619 | 0.000 | 0.000 | 0.0062 / 0.0030 / 0.0000 |
| 16 | 0.01962 | **0.081** | 0.000 | 0.0198 / 0.0101 / 0.0042 |
| 20 | 0.08361 | **0.258** | 0.000 | 0.0886 / 0.0624 / 0.0544 |

Two readings, and they must be kept apart:

- **On REACH alone the collision probability climbs steeply with linker length** — 0 at the 12-atom gate,
  8 % at 16, **26 % at 20**. A degrader with a 16–20-atom linker (which is what C420 and C559 would cost, and
  what `best_linker_atoms = 19` sits at) is materially likely to put its electrophile within reach of a
  paralogue cysteine at the same placements where it reaches NR4A3.
- **On REACH AND EXPOSURE it is 0.000 everywhere** — entirely because no paralogue cysteine clears RSA 0.25
  in these single frames.

So the whole categorical chemistry claim currently rests on **one number per paralogue cysteine, taken from
one conformer**: its solvent exposure. That is a thinner foundation than the axis has been credited with, and
it is measured, not argued.

### 3.4 Term (b) — the transfer-zone lysine comparison is already non-discriminating on the any-lysine measure

Over the same matched placement set, expected coverage of the observed E2~Ub transfer zone (17.09 Å measured,
8 Å isotropic anchor mobility, exact lens formula):

| species | ensemble | P(zone covers any lysine) | P(covers an EXPOSED lysine) | superposition core RMSD |
|---|---|---|---|---|
| NR4A3 | pooled unbiased (75) | **0.438** | 0.419 | 0.96 Å |
| NR4A3 | static opened model | 0.401 | 0.401 | 0.00 Å |
| NR4A1 | static opened model | **0.387** | 0.380 | 1.73 Å |
| NR4A2 | static opened model | **0.363** | 0.292 | 1.60 Å |

The paralogues' lysine sets are covered about as often as NR4A3's. This does **not** contradict Tier 2 — the
gate's discriminating statistic is the *joint* event (an NR4A3-**unique** lysine covered **and** both
paralogue zones bare), which the committed run reports at 0.0–0.032 and which these marginals are consistent
with. What it does show is that term (b) buys its discrimination from a **rare joint coincidence**, not from
the paralogues being short of lysines near the transfer zone.

---

### 3.5 ★ THE MATCHED PARALOGUE ENSEMBLES — LANDED, AND THE ANSWER IS YES (2026-07-26 2:49 PM ET)

Both legs reached their deliverables and the analysis ran over the committed ensembles. **300 matched
conformers** — NR4A3 / NR4A1 / NR4A2, **100 each** (25 well-tempered metadynamics + 3 × 25 unbiased release) —
against **73 867 matched E3 placements**, at the preregistered **12-atom** gate and an exposure cutoff of
RSA > 0.25.

**P(no paralogue cysteine is reachable | the same construct reaches an NR4A3-unique cysteine):**

| scope | frames / species | all cysteines | **solvent-exposed only** |
|---|---|---|---|
| static opened model | 1 | 1.000 | **1.000** |
| **unbiased release ensemble** | 75 | 0.99876 | **1.000** |
| metadynamics (biased) | 25 | 0.9971 | **1.000** |

**On exposed cysteines the answer is exactly 1.000 in every scope.** `mean_P_any_EXPOSED_cysteine` is **0.0**
for NR4A1 and **0.0** for NR4A2 throughout — not small, zero. The non-zero co-labelling on the all-cysteine
measure (0.12 % unbiased, 0.29 % biased) is entirely on **buried** paralogue cysteines: reachability without
labelability. NR4A2 is essentially absent on every measure (1 × 10⁻⁶ – 7 × 10⁻⁶); NR4A1 carries what little
signal there is, and none of it is exposed.

⚠ **REPORT IT AS THE RARE-EVENT STATISTIC IT IS.** The conditioning event is thin *by construction* — a matched
placement reaches an NR4A3-unique cysteine in only **~0.04 %** of placements, i.e. **122 hit placements out of
73 867** in the unbiased ensemble. Raising the sampler to 2 000 000 samples per (arm × pose) is what made that
denominator two orders of magnitude better than the 500 k setting, which returned single-digit events. But 122
is still a small denominator, and **0.99876 must not be quoted to five figures as though it were tight. The
defensible statement is the exposed column: zero paralogue co-labelling events observed, not a probability
estimated near one.**

**What this does and does not settle.** It removes the specific failure mode this lane was built to find: a
paralogue is not merely missing a cysteine at the aligned position while carrying a reachable one elsewhere.
Across every populated conformer sampled, where the construct can label NR4A3 it cannot label an exposed
cysteine on either paralogue. It does **not** establish that a bond forms, that it forms selectively in a cell,
or anything about efficacy — see §5.

*Artifact:* [`nr4a-paralogue-dynamics.json`](../modalities/nr4a-paralogue-dynamics.json) (`categorical_verdict`).
*Cost:* the two legs ran ~12.5 h each on rented 4090s/4080Ss at $0.13–0.21/hr, against a $2.5 point estimate,
a $1.5–6 band and a $40 ceiling. One capacity-refused 3090 rental cost under $0.02 before it was destroyed and
its machine excluded.

## 4. What is already established, and what it does to the categorical claim

**The claim as nr4a3-program-map.md states it is: the paralogues "have no nucleophile at the aligned position, so a
covalent bond *cannot form* on them at all."** The first clause is true and is not in dispute. **The second
does not follow, and three measurements now say so:**

1. **NR4A3's categorical cysteines are 3 of 7; the other 4 are shared with both paralogues** — and one of the
   shared ones, **C496, is inside the 12-atom gate in 38.7 % of unbiased NR4A3 conformers**. The committed
   pipeline scores term (a) on the unique set only and summarises the conserved set at the 20-atom sampling
   ceiling, so this was invisible, not absent.
2. **Each paralogue presents two cysteines inside the same gate**, and NR4A1's C465 opens at a **6-atom**
   linker against C397's 10. On the reach criterion the program itself uses, the paralogues are in range.
3. **On the matched-construct test the collision probability is length-dependent and large**: 0 at 12 atoms,
   **0.081 at 16**, **0.258 at 20** — and 16–20 atoms is exactly the range the program already contemplates
   (C420 needs 16, C559 needs 20, `best_linker_atoms` reads 19).

**What still holds the axis up is a single quantity: solvent exposure.** Every paralogue cysteine inside the
gate sits at RSA 0.011–0.165 against C397's 0.395, so on a reach-**and**-exposure criterion the collision
probability is 0.000 at every length. But that is **one number per residue from one conformer**, and RSA is
the most conformationally variable quantity in this whole analysis (C397's own range is 0.108–0.673). The
matched ensembles exist to turn those four single-frame numbers into distributions.

> **Verdict as of the $0 stage: the categorical chemistry axis is NARROWER than the record states — it is not
> "a covalent bond cannot form on the paralogues", it is "at a 12-atom linker, and only because the paralogue
> cysteines that ARE in range are partially buried in the one conformer we looked at." Whether that survives
> paralogue dynamics is measured, not assumed, by the run now in flight.**

## 5. Honest scope

- Reach and exposure are **necessary, not sufficient**. Nothing here tests thiol pKa, intrinsic
  nucleophilicity, local electrostatics, adduct stability or electrophile promiscuity; the last needs
  chemoproteomics.
- The A1 envelope is an **E3-independent upper bound**. For this lane's question that is the conservative
  direction when ruling a site out, and A2 exists precisely because it is *not* conservative when ruling one in.
- Metadynamics frames are **biased** along the pocket-opening CV; they are reported separately and never pooled
  with the unbiased release frames, and are read only as an adversarial upper bound on how far each pocket opens.
- Every model is **LBD-only**, as everywhere in this program.
- No efficacy, safety, therapeutic-window or clinical claim is made or implied.

---

## 6. Exact nr4a3-program-map.md deltas proposed by this lane

*This lane does not edit nr4a3-program-map.md.* All four deltas below are supported by the $0 stage alone; §3.5's
result will either sharpen D1 or add a fifth.

**D1 — §MECHANISM-FIRST: the CATEGORICAL bullet's second clause is not established, and must be narrowed.**
Current text: *"**CATEGORICAL** — the paralogue is structurally *incapable*. NR4A3 carries reactive residues
that BOTH paralogues lack …"*, and the Tier-0 row: *"No paralogue-unique nucleophile within tether range …
⇒ PASSED — GO on both axes (C397 at 10.9 Å exit-vector reach …)"*. Both read as claims about the MOLECULE.
Add, immediately after the C397 sentence:

> **⚠ NARROWED 2026-07-25 (LANE 13, $0). "Structurally incapable" is established for the ALIGNED POSITION,
> not for the molecule.** Scored over EVERY cysteine rather than the three NR4A3-unique ones — which the
> committed search never does, because `run_arm_pose` builds term (a) from `unique_cysteines` and summarises
> the conserved set only at the 20-atom SAMPLING CEILING — the same E3-independent envelope that puts C397
> inside the 12-atom gate also puts **NR4A1 C465 there at a 6-atom linker** (shorter than C397's 10),
> **NR4A1 C551** (the celastrol/NR-V04 site, no aligned NR4A3 residue) at 10, **NR4A2 C465** at 10 and
> **NR4A2 C534** (NR4A3 has S565) at 12. On the matched-construct test — same placement, same warhead exit
> anchor, same E3 anchor, same budget — P(a paralogue cysteine is also reached | an NR4A3-unique one is) is
> 0 at 12 atoms but **0.081 at 16 and 0.258 at 20**, and 16–20 atoms is the range the program already
> contemplates (C420 needs 16, C559 needs 20, `best_linker_atoms` reads 19). **The axis therefore survives on
> EXPOSURE, not on the absence of a nucleophile:** every paralogue cysteine inside the gate sits at RSA
> 0.011–0.165 against C397's 0.395, so requiring RSA ≥ 0.25 as well as reach returns 0 collisions at every
> length. That exposure margin is currently **one number per residue from one conformer**, and RSA is the most
> conformationally variable quantity in the analysis (C397's own range over 75 frames is 0.108–0.673). Matched
> NR4A1/NR4A2 ensembles are what turn it into a distribution.

**D2 — NR4A3's own CONSERVED C496 is inside the gate in 38.7 % of unbiased conformers, and the record does not
say so.** STRATEGY currently carries *"★ But the chemistry axis is ONE RESIDUE DEEP: C420 and C559 reach the
gate in 0/75 unbiased frames."* That is correct and should stay, but it is a statement about the three
**unique** cysteines. Add:

> **C496 — CONSERVED, and present in both paralogues as C465 — reaches the ≤12-atom gate in 29/75 = 0.387 of
> unbiased frames (Wilson 0.285–0.500), and 0.68 of the biased metadynamics frames.** Median shortest linker
> 14 atoms. What closes it is **burial, not geometry**: RSA median 0.023 against C397's 0.416. So "one residue
> deep" understates the risk in one direction (there is a second NR4A3 cysteine the linker can reach) and
> overstates the selectivity in another (that second one is shared with both paralogues, so an electrophile
> that finds it is non-discriminating). Report both.

**D3 — the E2~Ub transfer term's discrimination comes from a rare JOINT event, not from paralogue lysine
scarcity.** Over one matched placement set at the measured 17.09 Å transfer distance, the probability that the
zone covers *any* lysine of the species is **NR4A3 0.438 (pooled over 75 unbiased conformers), NR4A1 0.387,
NR4A2 0.363** — statistically indistinguishable. This is consistent with, and does not contradict, the
committed `fraction_members_unique_and_paralogues_bare` of 0.0–0.032; it simply names where the
discrimination comes from. Add one line to the Tier-2 block so the term is not read as "the paralogues have
no lysines there."

**D4 — record the reciprocal handles, which the Tier-0 artifact enumerates in only one direction.**
`nr4a-paralogue-unique-residues.json` lists NR4A3-unique residues and mentions NR4A1 Cys551 in prose. The
symmetric fact is: **both paralogues carry C534 at a position where NR4A3 has Ser565**, and NR4A1 carries
C551 with no aligned NR4A3 residue at all. That matters twice over — it is the reciprocal of the program's
own mechanism (and the most parsimonious explanation of NR-V04's selectivity, which STRATEGY already leans
on), and it is a candidate compensating site for exactly the failure mode this lane tests.

---

## 7. Reproducing this

```bash
# $0, ~25 min on one core — the static models plus whatever ensembles are present
python research/modalities/nr4a_paralogue_dynamics.py --mode all --validate-coverage --samples 500000
python research/modalities/nr4a_paralogue_report.py
python research/modalities/tests/test_paralogue_dynamics.py
```

The GPU half is fired by committing a task to
[`nr4a-paralogue-md-task.json`](../modalities/nr4a-paralogue-md-task.json); the ladder is
`selftest → bake → smoke → launch → watch → collect → analyse`, and after `launch` the lane chains itself to
completion.
