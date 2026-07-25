# Does the CATEGORICAL case survive paralogue dynamics? — matched NR4A1 / NR4A2 / NR4A3 ensembles

> **Lane doc (LANE 13).** Tier 2's GO was won on the **CATEGORICAL** basis: NR4A3 carries reactive residues
> both paralogues lack, so the paralogues are structurally *incapable* rather than merely disfavoured. That
> basis matters because the **marginal** axis needs ~2.0 kcal/mol against ~1.12 resolvable and is explicitly
> *"a confirmation tool operating near its limit, not a discovery tool."*
>
> The NR4A3 side of the categorical case is now well characterised over 100 conformers. **The paralogue side
> had only ever been tested on ONE static opened conformer each**, and STRATEGY.md names the matched paralogue
> ensembles as the open cheap add-on in two places. This lane runs them and asks the question they were for:
> **do paralogue DYNAMICS open a compensating site?**
>
> Subordinate to [STRATEGY.md](../../STRATEGY.md); this lane does not edit it. Exact deltas are in §6.
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

*(filled in below as each stage lands; §3.1 is complete and needed no GPU)*

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

---

## 4. Honest scope

- Reach and exposure are **necessary, not sufficient**. Nothing here tests thiol pKa, intrinsic
  nucleophilicity, local electrostatics, adduct stability or electrophile promiscuity; the last needs
  chemoproteomics.
- The A1 envelope is an **E3-independent upper bound**. For this lane's question that is the conservative
  direction when ruling a site out, and A2 exists precisely because it is *not* conservative when ruling one in.
- Metadynamics frames are **biased** along the pocket-opening CV; they are reported separately and never pooled
  with the unbiased release frames, and are read only as an adversarial upper bound on how far each pocket opens.
- Every model is **LBD-only**, as everywhere in this program.
- No efficacy, safety, therapeutic-window or clinical claim is made or implied.
