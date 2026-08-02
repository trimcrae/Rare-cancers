# NR4A3-unique cysteines: accessibility across the experimental ensemble, with NR4A1 Cys551 (the NR-V04 site) as the positive control

NR-V04's NR4A1 selectivity is ATTRIBUTED — proposed by Zhang et al. 2018, never structurally confirmed — to covalent engagement at NR4A1 Cys551, a position NR4A3 lacks. Does NR4A3 carry a cysteine of its own that BOTH paralogues lack, and how accessible is it across the experimental ensemble?

*Method:* Uniqueness: imported from nr4a_paralogue_unique_residues.classify_positions (two independent aligners). Geometry: Shrake-Rupley SASA (atlas implementation, 96 sphere points for residue SASA, 960 for the single-atom SG measures) on the atoms of interest with all atoms as occluders; SG distance to the mapped cryptic pocket. Numbering by global BLOSUM62 alignment of each model's ATOM-record sequence to its own UniProt sequence, identity asserted >= 0.9. Pure stdlib, $0 CPU.

## Pre-specified criteria

PRE-SPECIFIED BY IMPORT. Both thresholds already existed in the repo before this question was asked and are imported, not re-typed here. They were NOT tuned.

- **accessible** — residue RSA >= EXPOSED_RSA (0.25) — nr4a_differential_atlas
- **reachable** — SG within a tethered reach band (in_pocket/exit_vector/linker_borne) — nr4a_paralogue_unique_residues.REACH_BANDS
- **flagged** — accessible AND reachable

## Positive control — does the test recover the known case?

**NR4A1 C551** — celastrol warhead of NR-V04; PROPOSED by Zhang et al. 2018 from mutagenesis and MS, NOT structurally confirmed.

| paralogue | aligned residue | cysteine? |
|---|---|---|
| NR4A2 | Y551 | no |
| NR4A3 | T579 | no |

**Result: NOT_RECOVERED**

The pre-specified criteria DO NOT flag the known covalent site. Per the design of this analysis that is the finding: the criteria are wrong, or too coarse, and any NR4A3 cysteine they flag inherits that unreliability. The thresholds are NOT adjusted to fix this — see `criteria_diagnosis` for the threshold-free reading that replaces them.

- state-matched opened model: RSA **0.165** (exposed >= 0.25: False), SG-to-pocket **10.67 A** (`exit_vector`), SG SASA 6.17 A^2 all-atom / 20.51 A^2 heavy-atom-only

- across the 25-frame NR4A1 metadynamics ensemble: RSA 0.026-0.223 (median 0.064), SG-to-pocket 10.06-14.63 A (median 10.84); flagged in 0/25 frames

- failed on: **accessible (RSA 0.165 < 0.25)**; passed: reachable

### Threshold-free reading — where the known site RANKS

A cutoff that misses the known site is ambiguous between *the observable is uninformative* and *the observable is fine, the line is misplaced*. Rank separates them, and unlike a re-tuned cutoff it cannot be steered toward a preferred answer.

Pool: 18 cysteines — all cysteines of NR4A1, NR4A2, NR4A3 state-matched opened models. Rank 1 = most exposed.

| observable | control value | rank | top 3 |
|---|---|---|---|
| `rsa` | 0.165 | **3/18** | NR4A3 C397 = 0.395; NR4A3 C420 = 0.311; NR4A1 C551 = 0.165 |
| `rsa_heavy` | 0.24 | **3/18** | NR4A3 C397 = 0.416; NR4A3 C420 = 0.301; NR4A1 C551 = 0.24 |
| `sg_sasa_A2` | 6.17 | **3/18** | NR4A3 C420 = 30.29; NR4A3 C397 = 16.62; NR4A1 C551 = 6.17 |
| `sg_sasa_heavy_A2` | 20.51 | **3/18** | NR4A3 C420 = 38.34; NR4A3 C397 = 24.53; NR4A1 C551 = 20.51 |
| `sg_rel` | 0.293 | **3/18** | NR4A3 C420 = 0.514; NR4A3 C397 = 0.364; NR4A1 C551 = 0.293 |

**Diagnosis: OBSERVABLE INFORMATIVE, CUTOFF MISPLACED. The known covalent site is not mid-pack — it ranks in the top fifth of all pooled NR4A-family LBD cysteines on 5/5 accessibility observables (rsa, rsa_heavy, sg_rel, sg_sasa_A2, sg_sasa_heavy_A2). So accessibility does order these cysteines usefully; what fails is the location of the 0.25 RSA line, which sits ABOVE the known site. The line is NOT moved here — a cutoff re-fitted to make the control pass would make every downstream NR4A3 call circular. Rank is reported instead, and rank is what any NR4A3 statement must be read against.**

*Thresholds are imported from pre-existing repo constants and are NOT re-fitted in this module. See `_criteria` for their homes.*

### Which SASA convention is being quoted

SG SASA with hydrogens present vs deleted, per cysteine, on the state-matched opened models. The occluding atom is the residue's own HG thiol proton — the atom a covalent warhead replaces.

Across the pooled cysteines the residue's own thiol proton occludes **0.21–1.0** of the SG surface (median **0.918**).

A large occluded fraction means the ALL-ATOM convention answers 'how exposed is the protonated thiol', not 'how exposed is the sulfur a warhead must reach'. Both are reported here so neither can be quoted as the other; the pre-specified criterion uses the all-atom convention because that is what the committed artifact used.

## NR4A3 LBD cysteines and their aligned paralogue residues

| NR4A3 | context | NR4A1 | NR4A2 | unique vs both | aligners agree |
|---|---|---|---|---|---|
| C397 | `PSPPI[C]MMNAL` | N363 | S363 | **yes** | yes |
| C420 | `DYSRY[C]PTDQA` | Q388 | A389 | **yes** | yes |
| C496 | `DKFVF[C]NGLVL` | C465 | C465 | no | yes |
| C506 | `LHRLQ[C]LRGFG` | C475 | C475 | no | yes |
| C536 | `IQALA[C]LSALS` | C505 | C505 | no | yes |
| C559 | `RVEEL[C]NKITS` | Q528 | Q528 | **yes** | yes |
| C594 | `ELRKI[C]TLGLQ` | C566 | C566 | no | yes |

## Spread across the experimental ensemble — experimental solution-NMR ensemble (PDB 8XTT, 20 conformers)

20 of 20 models analysed.

| NR4A3 Cys | unique | RSA min–med–max | SG SASA heavy min–med–max (Å²) | SG→pocket min–med–max (Å) | reach classes seen | flagged in |
|---|---|---|---|---|---|---|
| C397 | **yes** | 0.327 – **0.464** – 0.629 | 32.57 – **51.61** – 73.59 | 10.93 – **12.92** – 14.06 | exit_vector, linker_borne | 20/20 |
| C420 | **yes** | 0.195 – **0.266** – 0.314 | 30.96 – **43.765** – 47.45 | 16.85 – **17.07** – 18.93 | linker_borne | 16/20 |
| C496 | no | 0.074 – **0.099** – 0.146 | 2.55 – **5.9** – 11.26 | 2.66 – **4.975** – 5.59 | in_pocket | 0/20 |
| C506 | no | 0.0 – **0.0** – 0.029 | 0.0 – **1.47** – 6.3 | 10.87 – **11.715** – 12.36 | exit_vector, linker_borne | 0/20 |
| C536 | no | 0.0 – **0.0** – 0.0 | 0.0 – **0.0** – 1.07 | 5.89 – **6.27** – 6.42 | in_pocket | 0/20 |
| C559 | **yes** | 0.155 – **0.205** – 0.24 | 31.9 – **36.055** – 40.48 | 12.22 – **12.76** – 13.23 | linker_borne | 0/20 |
| C594 | no | 0.021 – **0.107** – 0.16 | 2.01 – **4.155** – 26.81 | 8.47 – **8.85** – 11.18 | exit_vector | 0/20 |

Spread across the ensemble is itself the result: a single conformer's number is not the answer for any of these cysteines.

## Cross-checks (rule 1 — this module must not mint a second value for an existing number)

- `committed_unique_residue_map`: **AGREES** (max |ΔRSA| 0.0, max |Δd| 0.0 A)
- `8xtt_numbering_vs_benchmark`: **AGREES**

## Which comparisons these numbers license

**Licensed:**

- NR4A3 cysteines against each other, within the 8XTT ensemble — *same protein, same 20 experimental conformers, same measurement*
- NR4A1 Cys551 against every NR4A3/NR4A2 cysteine, on the state-matched opened models (this is what `control_rank` does) — *all three models come from one modelling pipeline in one state, so a rank across them compares proteins rather than methods — which is why rank, not the ensemble spread, is the load-bearing cross-paralogue statement here*
- the spread of one cysteine across conformers, read as structural heterogeneity — *within a single ensemble, spread is a property of that ensemble and is reported as such*

**NOT licensed:**

- NR4A3 8XTT ensemble spread against the NR4A1/NR4A2 metadynamics ensemble spread — *experimental restraint-satisfying NMR conformers vs conformers driven along a pocket-opening bias potential. Neither is Boltzmann-weighted and they are not weighted the same way, so a difference in spread is not evidence about the proteins.*
- any ensemble spread read as a population or an occupancy — *neither ensemble is Boltzmann-weighted; frequency across conformers is not probability*
- a flagged/not-flagged count read as evidence of ligandability — *the pre-specified criteria do not recover the known covalent site, so passing them is not evidence — see criteria_diagnosis*

**Missing input:** There is no experimental NR4A1 or NR4A2 LBD ensemble in this repo, so the like-for-like ensemble comparison the question really wants CANNOT be made from what is here. That is a missing input, not a negative result.

## Honest limits

- Sequence uniqueness is exact. Accessibility, tether reach, adduct formation and degradation are HYPOTHESES generated for testing, not results.
- Intrinsic thiol reactivity (pKa, local electrostatics, hard/soft electrophile preference) is NOT computed. An exposed cysteine is not necessarily a reactive one.
- The 8XTT ensemble is 20 solution-NMR conformers of the APO LBD: a restraint-satisfying ensemble, not a Boltzmann-weighted one. Spread across it is a measure of experimental structural heterogeneity, not of populated-state probability.
- The NR4A1/NR4A2 metadynamics ensembles are BIASED along a pocket-opening collective variable and are not Boltzmann-weighted either; they are a heterogeneity comparator only.
- NR4A1 Cys551's status as the NR-V04 covalent site is PROPOSED (Zhang et al. 2018), not structurally confirmed. The positive control therefore tests the criteria against a literature attribution, not against a solved covalent complex.
- No claim is made — and none follows from these measurements — that a covalent NR4A3 degrader is feasible. This reports accessibility, its spread, and control recovery only.
- No efficacy, safety, therapeutic-window or clinical claim is made or implied.
