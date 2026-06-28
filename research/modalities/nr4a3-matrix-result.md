# NR4A selectivity matrix — result, robustness, and the FEP go/no-go

**Status: matrix COMPLETE (2026-06-28, `gpu-matrix-aws.yml` run 28319737517).** This is the Fig 4
deliverable of the NR4A3-degrader paper: a per-candidate selectivity fingerprint built by docking one
deduped library into the **state-matched metad-OPENED conformer of each paralogue** (NR4A3 frame 300
druggability 0.931 · NR4A1 frame 524 0.981 · NR4A2 frame 125 0.938), which removes the opened-vs-static
confound that voided the first warhead screen. Outputs in `s3://<bucket>/nr4a3-matrix/`:
`nr4a3-matrix.json`, the three opened-conformer PDBs, docked SDFs, and `nr4a3-matrix.png` (Fig 4b heatmap).
Re-read any time (read-only) via `report-matrix-aws.yml`.

## The result (13 deduped candidates; all contact 4/5 engageable handles)
Engagement cutoff dG < −7.0 kcal/mol; selectivity margin bar 1.0 kcal/mol (`selectivity_fingerprint.py`).
Docking dG is a **screening prior, not an affinity** — cells are triage hypotheses.

| candidate | cell | dG_NR4A3 | dG_NR4A1 | dG_NR4A2 | Δ vs NR4A1 | Δ vs NR4A2 |
|---|---|---|---|---|---|---|
| **cytosporone B** (=CHEMBL1221517) | NR4A3-only | −7.08 | −5.66 | −5.91 | +1.42 | +1.16 |
| amodiaquine (=CHEMBL682) | NR4A3-only | −7.82 | −6.51 | −6.94 | +1.31 | +0.89 |
| celastrol | pan-NR4A | −8.58 | −8.14 | −7.62 | +0.44 | +0.96 |
| CHEMBL475 | pan-NR4A | −8.61 | −7.01 | −9.07 | +1.59 | −0.46 |
| CHEMBL1873475 | pan-NR4A | −8.40 | −8.41 | −8.80 | −0.01 | −0.40 |
| CHEMBL196 | NR4A2+NR4A3 | −7.35 | −6.33 | −7.77 | +1.02 | −0.42 |
| resveratrol | NR4A1+NR4A2 | −6.95 | −7.54 | −7.01 | −0.60 | −0.07 |
| chloroquine / CHEMBL76 | none | −6.39 | −5.11 | −6.30 | +1.27 | +0.09 |
| piperlongumine | none | −6.90 | −6.00 | −6.75 | +0.90 | +0.15 |

**Cell census:** NR4A3-only 4 · pan-NR4A 3 · none 3 · NR4A2+NR4A3 1 · NR4A2-only 1 · NR4A1+NR4A2 1 ·
**NR4A1+NR4A3 (AML-risk anti-target) = 0.**

**Framework-level conclusions (these are robust and are what the paper should claim):**
1. **Programmable selectivity is real in-silico** — the library partitions across distinct NR4A3-only /
   pan-NR4A / paralogue-leaning cells; the pipeline produces a usable selectivity fingerprint.
2. **The AML-risk NR4A1+NR4A3 anti-target cell is empty** — nothing in the library to engineer away from;
   off-target leakage instead leans NR4A2.
3. A NR4A3-leaning sub-pocket and a conserved pan-pocket both exist and are dockable (the two design modes).

## Why the *specific* leads are NOT yet a result (the honest caveats)
**(a) Every quantitative call is within docking noise.** 6/9 candidates sit on a classification boundary
(a dG within ~0.5 kcal/mol of the −7.0 engage cutoff, or a margin within ~0.5 of the 1.0 bar). Five have a
dG within **0.10 kcal/mol** of the engage cutoff (cytosporone B −7.08, amodiaquine NR4A2 −6.94, CHEMBL475
NR4A1 −7.01, piperlongumine −6.90, resveratrol −6.95/−7.01) — i.e. the cell assignment is a coin-flip under
smina's ~1–2 kcal/mol error. The lead's own selectivity margins (+1.42/+1.16) clear the 1.0 bar by only
0.42/0.16, **inside docking noise**.

**(b) The top NR4A3-selective hit contradicts known pharmacology.** **cytosporone B (Csn-B) is the
canonical Nur77/NR4A1 agonist** (Zhan et al., *Nat Chem Biol* 2008; EC50 0.278 nM, binds the NR4A1 LBD).
The matrix calling it NR4A3-selective (+1.42 vs NR4A1) is therefore almost certainly a docking artefact —
it inverts the established NR4A1 preference. FEP on this molecule would most likely **refute** the docking
call, not validate a lead.

**(c) The library is repurposing/tool compounds, not designed warheads.** cytosporone B, amodiaquine
(antimalarial), celastrol (promiscuous natural product), chloroquine, resveratrol, piperlongumine — these
are NR4A tool/repurposing actives, not selective degrader chemotypes. They populate the matrix to validate
the *method*; they are not the molecules the program would carry forward.

## FEP go/no-go — recommendation: **DEFER**
Selectivity FEP (ABFE of a lead in each of the 3 opened pockets, or a paralogue thermodynamic cycle) is the
**dominant GPU cost of the whole program**: ~hundreds of ns–~1 µs of sampling per protein per ligand →
roughly **1–3 days of g5.xlarge per protein**, ×3 proteins ×(1–3 leads) = **~1–3 weeks serial** on the
1-instance quota. Three converging reasons not to spend it now:

1. **Prematurity (pocket).** FEP precision is wasted on biased-MD opened pockets whose physical metastability
   is unconfirmed — Gate 1 holds only in the weaker basin-breathing sense and Gate 3 is provisional. The
   **unbiased release run** (`gpu-release-aws.yml`, already queued) is the cheaper prerequisite that decides
   whether the opened state is metastable or bias-induced strain. FEP before it risks precisely quantifying
   binding to an artefact.
2. **Wrong molecule.** The top selective hit is a known NR4A1 agonist (caveat b); FEP would likely disprove,
   not confirm, its NR4A3-selectivity. FEP belongs on *bona fide* selective candidates from the de-novo
   campaign (matrix step 3: divergent-handle-conditioned generation), not on repurposing tool compounds.
3. **Cost/benefit.** Weeks of the program's scarcest resource to put an error bar on a chemotype that won't
   be carried forward is a poor trade.

**Cheaper, better-sequenced alternatives (in order):**
- **MM-GBSA endpoint rescoring first** (single-snapshot / short-ensemble implicit solvent on the docked
  poses + opened PDBs already in S3). Far cheaper than FEP; tells us whether the docking selectivity even
  survives a better energy model before any alchemical spend. Can be built CPU-side (GitHub-Actions CPU or a
  short SageMaker job), no multi-day GPU. **This is the natural next quantitative step.**
  **Status (2026-06-28): DONE — run 11 (`mmgbsa-aws.yml`, g5/OpenCL, `_status: ok`, all 13 candidates).**
  Census: rescued 3 · confirmed_selective 3 · reversed 3 · weakened 2 · confirmed_nonselective 2. **Result
  validates the matrix's central caveat: the docking-level NR4A3-selectivity does NOT robustly survive a
  physics-based energy model.** The headline docking hit **cytosporone B reverses** (NR4A3 margin +1.16 ->
  **−5.83**; its duplicate library entry CHEMBL1221517 also reverses, −7.02) — the known Nur77/NR4A1 agonist
  is correctly demoted, confirming the docking call was an artefact. **amodiaquine (CHEMBL682) and celastrol
  hold up as `confirmed_selective`** (mm margins +2.2 / +2.6); both of amodiaquine's library entries agree
  (internal consistency check passes). **Honest caveat:** single-snapshot MM-GBSA (no entropy, no ensemble)
  inflates magnitudes (margins of ±3–7 kcal/mol are not affinities) — trust the *direction/verdict*, not the
  numbers; still triage, FEP remains the affinity tier. Output `s3://<bucket>/nr4a3-mmgbsa/nr4a3-mmgbsa.json`;
  re-read any time via `report-mmgbsa-aws.yml`. Infra post-mortem (runs 7–11) in
  `nr4a3-degrader-next-steps.md` → MM-GBSA.
- **Unbiased release run** — the actual gate on whether the opened pocket is real (already launch-ready).
- **De-novo design (matrix step 3)** to fill the cells with real selective candidates before FEP.

**Bottom line:** the matrix succeeds as the *framework* result (Fig 4: programmable selectivity, empty
anti-target cell, working state-matched pipeline). The specific lead chemotypes are method-validation
compounds, within docking noise, and the headline hit contradicts known pharmacology — so **FEP is not worth
launching yet.** Gate it behind (i) the release run confirming the pocket and (ii) MM-GBSA + de-novo
candidates that are actually worth a multi-day alchemical run.
