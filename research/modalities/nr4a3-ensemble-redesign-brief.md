# Agent brief: ensemble-robust NR4A3 ligand redesign

*Canonical true-north spec (trimcrae, 2026-07-11). This brief is authoritative; the live implementation
status/ledger is [`nr4a3-ensemble-redesign-plan.md`](./nr4a3-ensemble-redesign-plan.md), and the pure scoring
layer is [`ensemble_robust_score.py`](./ensemble_robust_score.py). Follow this brief as work proceeds.*

## Mission

Design and evaluate a **new computational NR4A3-favoured ligand candidate whose predicted preference is robust
to receptor conformer choice.**

Do not optimize merely for a high score in the existing AF2-derived release frame. The current candidate,
`denovo_401`, showed that changing the NR4A3 opened conformer can move the ABFE result by approximately the
size of the original paralogue-selectivity margin. The redesign must therefore treat receptor conformational
provenance as part of the design problem.

The desired outcome is not "another high-scoring molecule." It is a candidate for which:

1. the same mapped orthosteric pocket is present under a corrected, score-independent tracking method;
2. NR4A3 preference survives multiple prespecified NR4A3 conformers;
3. the preference survives held-out experimental conformers;
4. matched NR4A1 and NR4A2 conformers do not provide strong counterexamples;
5. receptor preference is larger and more reproducible than conformer sensitivity;
6. the result survives repaired alchemical calculations.

`denovo_401` remains the benchmark and control. **Do not delete or replace its existing results.**

## Scientific principle

Optimize for: **receptor preference − conformer sensitivity − paralogue counterexamples − chemical liabilities.**

The primary objective is **worst-case robustness, not best-frame score.** A smaller reproducible preference
across conformers is more valuable than a large margin in one selected structure.

## Phase 0 — protect provenance and freeze the current record

Before changing any existing workflow:

1. Freeze the current manuscript-result snapshot.
2. Record the commit hash, environment, package versions and input hashes.
3. Preserve all existing `denovo_401` structures, poses, receptor frames and ABFE inputs.
4. Do not overwrite legacy results when introducing the corrected pocket tracker, dense-λ schedule or new
   receptor panels.
5. Give every new result an explicit **generation**: `legacy`, `harmonized_tracking`, `dense_lambda`,
   `ensemble_redesign`.
6. Maintain a machine-readable provenance table linking every reported result to: receptor structure; source
   PDB/model; trajectory and frame; pocket-tracking implementation; ligand microstate; stereoisomer; software
   version; random seed; simulation protocol; output location.

**Do not silently mix legacy and repaired results in one comparison.**

## Phase 1 — finish the methodological submission gates

Do not begin expensive free-energy evaluation of new molecules until these gates are resolved.

### 1. Harmonized pocket definition and tracking
Replace the current outcome-selected reference-pocket definition.
- **Site definition:** define the orthosteric region *independently of fpocket druggability* using a fixed set
  of canonical nuclear-receptor ligand-pocket residues mapped by structural alignment. Fixed before reading
  pocket scores; identical in intent across NR4A1/2/3; stored as residue mappings with alignment provenance.
- **Matching rule (per structure/frame):** detect all fpocket cavities → match to the predefined orthosteric
  region using a composite rule → read the matched cavity's score *only after* matching. Composite matcher:
  residue-set Jaccard; fraction of canonical site residues recovered; centroid distance from mapped reference;
  explicit split/merge policy; explicit no-match outcome. **Do not accept a match on one shared residue.**
- **Outputs (per dataset):** total frames; matched count; unmatched count; fraction above D\* among matched;
  fraction above D\* among all frames (unmatched counted as non-druggable); sensitivity to matching thresholds.
- **Pin one fpocket build and rerun:** calibration panel; static AF2; all 20 8XTT conformers; three
  metadynamics replicas; three release replicas; exact generation receptor frame.
- **Critical dependency audit (Gate A):** confirm whether the *exact* release-derived frame used to generate
  `denovo_401` still (a) matches the predefined orthosteric site, (b) exceeds D\*, (c) contains the claimed
  candidate pocket-facing handles. **If it fails, stop the current ligand-lead interpretation** — the existing
  generative campaign becomes an exploratory result produced from a misclassified receptor frame.

### 2. Dense-λ ABFE validation
Complete the NR4A2 repair pilot; determine whether the dense schedule restores connected overlap. Assess:
adjacent-window overlap; effective sample size; forward/reverse stability; time convergence; replicate
consistency; sensitivity to adding further intermediate windows. Apply the validated final schedule to **both**
NR4A3 variants (AF2-opened; 8XTT-seeded). Do not compare repaired 8XTT with legacy AF2 as if the difference
isolated receptor conformation. The conformer comparison must use the same λ schedule, sampling duration,
solvent leg, ligand stereoisomer/parameters, analysis/deduplication, restraint-selection principles, and
independent repeats. The conformer shift is supported only if pathological overlap is removed, the shift keeps
its sign across repeats, its magnitude exceeds combined uncertainty, and estimates stabilize with sampling.
Until then, describe the 8XTT result as a **preliminary indication of conformer sensitivity.**

### 3. T4L protocol-matched benchmark
Run T4 lysozyme L99A–benzene using the **final production protocol** (dense λ; per-window duration;
equilibration; reduction; restraint treatment; replicate strategy), not the shorter legacy setup. Classify the
ABFE implementation: validated enough for exploratory receptor contrasts / still strongly biased / needs
further debugging. Do not infer that good overlap alone guarantees accuracy.

### 4. Validate the TICA-derived coordinate
The current TICA was derived from metadynamics-biased trajectories. Do not treat its apparent 17 ns timescale
as a physical unbiased timescale without bias handling. Audit whether the implementation includes: metadynamics
reweighting or time rescaling; per-replica preprocessing; feature normalization; lag-time sensitivity;
held-out-replica validation; bootstrap stability of the eigenvector; comparison with bias-free release
trajectories. Until validated, describe it as an exploratory component derived from biased data. Do not launch
the full phase-2 fleet solely because the coordinate produces repeated threshold crossings.

## Phase 2 — construct the receptor ensemble

Start only after the harmonized pocket classifier is operational.

**NR4A3 panel:** the original AF2-derived release frame; the AF2 metadynamics-opened frame; multiple
cavity-bearing 8XTT-derived structures or bias-free continuations; at least one minimally qualifying open-like
conformer; at least one more expanded conformer; held-out 8XTT conformers not used for generation. **Do not
select conformers using `denovo_401` scores or any new candidate's scores.**

**NR4A1 and NR4A2 panels:** matched using the same site and geometry definitions. Experimental anchoring alone
is insufficient — NR4A1/2 crystals are collapsed; any opened paralogue structures from MD must be labeled
**experiment-seeded computational conformers.** Match states by structural criteria (pocket-residue recovery;
centroid; volume/enclosure; gate geometry; relevant side-chain states). Do not assume equal fpocket scores
imply equivalent physical states.

**Design / validation / stress split — separate the panel before molecule generation:**
- **Design:** a small number of NR4A3 conformers spanning defensible open-like geometries.
- **Validation:** held-out NR4A3 conformers, especially 8XTT-derived structures not shown to the generator.
- **Stress:** more-occluded NR4A3 conformer; highly expanded NR4A3 conformer; matched NR4A1/2 conformers; any
  known promiscuous open-pocket state.

**Never tune the generator directly against the held-out validation set.**

## Phase 3 — diagnose `denovo_401`

Before generating broadly, identify *why* `denovo_401` is conformer-sensitive. For each receptor conformer,
compute and compare: docking pose; ligand heavy-atom RMSD; key residue contacts; hydrogen bonds; hydrophobic
contacts; buried surface area; cavity hydration; ligand strain; restraint anchors; short explicit-solvent pose
persistence; per-residue endpoint decomposition (qualitative); ABFE complex-leg components after repair.
Determine whether the AF2-vs-8XTT difference is associated with: loss of a specific contact; altered rotamer;
changed hydration; ligand reorientation; increased strain; changed restraint geometry; different cavity shape;
or global receptor placement rather than local pocket shape. **Produce a concise mechanistic report before
selecting redesign substitutions.**

## Phase 4 — two redesign branches

**Branch A — `denovo_401` analogues (matched molecular pairs):** reduce dependence on exact hydrophobic shape
complementarity; lower cLogP where possible; reduce unnecessary flexibility; add 1–2 directional contacts to
NR4A3-divergent residues; preserve stable interactions with conserved anchors; test substitutions near L406,
T410, I484, L534; treat I531 only as an NR4A1-discrimination handle; avoid ambiguous basic centres unless pKa/
microstates are explicitly handled; include the promising alternative stereoisomer as a separate candidate. Do
not optimize solely against the AF2 frame.

**Branch B — unrelated chemotypes:** new pocket-conditioned generation against *multiple* NR4A3 design
conformers. A candidate should preferably contact ≥2 stable conserved anchors and ≥2 NR4A3-divergent handles;
retain a similar interaction pattern across design conformers; avoid dependence on one mobile side chain; have a
defined stereochemical/protonation state; pass structural-alert + developability filters; not acquire strongly
favourable poses in expanded NR4A1/2 pockets. Generate enough to permit strict filtering, but do not advance
candidates merely because they top a weak batch.

## Phase 5 — ensemble-aware scoring

Score all design conformers and all matched paralogue conformers for every candidate. **Store the full
receptor-by-conformer matrix; do not reduce to one mean.** Compute: median NR4A3 score; worst NR4A3 score; best
paralogue score; minimum NR4A3-vs-paralogue margin; between-conformer variance; number of sign reversals;
number of receptor/conformer counterexamples.

Robust objective:  **S = min_c M_c − λ·σ_c − γ·C − η·L**, where M_c is the candidate's paralogue margin in
conformer c, σ_c is conformer sensitivity, C penalizes counterexample conformers, L penalizes chemical
liabilities. **Do not rank by the maximum margin.**

**Advancement standard:** positive minimum margin across the design set; no strong NR4A1/NR4A2 counterexample;
same qualitative contact architecture retained; no reliance on one receptor frame; passes chemical/microstate
checks.

## Phase 6 — matched controls

**Generation-matched null:** the marketed-drug decoy null tests the scoring pipeline but not pocket-conditioned
generation. Apply equivalent generation + filtering to an NR4A1 pocket, an NR4A2 pocket, an unrelated
nuclear-receptor pocket, or perturbed/mismatched NR4A3 pockets. Answer: *how often does pocket-conditioned
generation + this scoring pipeline produce an apparent NR4A3-favoured molecule by chance or design-match
overfitting?* Do not claim specificity from marketed-drug comparison alone.

**Known controls:** `denovo_401`; `denovo_924`; relevant repurposed candidates known to fail; neutral/cationic
`denovo_111` as a microstate-sensitivity control. Use internal labels such as `pipeline_positive`, not
`confirmed_selective`.

## Phase 7 — explicit-solvent triage

For top candidates: resolve exact stereoisomer/tautomer/protonation; estimate pKa where ionizable; run multiple
independent explicit-solvent pose simulations in multiple NR4A3 conformers + matched NR4A1/2 conformers; test
whether the modeled interaction pattern persists. Reject candidates with frequent pose loss, strong paralogue
poses, microstate-dependent reversal, severe conformer dependence, or large ligand strain. **Do not call short
trajectory persistence proof of binding.**

## Phase 8 — repaired ABFE

Use the repaired, benchmarked ABFE protocol only on a small final set: ≥2 NR4A3 conformers; ≥2 matched NR4A1
conformers; ≥2 matched NR4A2 conformers; independent repeats. Do not report one selected conformer per receptor
as the final selectivity result. Separate replicate variance, conformer variance, and receptor effect.

**Essential success criterion:  |receptor effect| > |between-conformer effect|.** A credible result does not
require a 5–10 kcal/mol margin; a consistent ~1.5–3 kcal/mol preference across prespecified conformers is more
persuasive than a large single-frame difference.

## Phase 9 — opening-state weighting

Only start the full opening-free-energy fleet after the pocket-state classifier is valid, the reaction
coordinate is validated, and the conditional ABFE result is reasonably stable across conformers. The final
thermodynamic question requires receptor-state weighting: **ΔG_effective,r ≈ ΔG_open,r + ΔG_bind|open,r** (or a
multi-state weighted equivalent). Do not combine a precise opening penalty with unstable conditional binding.

## Decision gates

- **Gate A — pocket dependency.** Pass: the exact design frame survives the harmonized site definition and
  remains druggable. Fail: stop treating the existing ligand campaign as a validated design result; rebuild the
  receptor panel before further generation.
- **Gate B — ABFE repair.** Pass: dense schedule removes the overlap bottleneck and gives stable repeated
  estimates. Fail: do not use the custom ABFE engine as the principal selectivity tier.
- **Gate C — conformer robustness.** Pass: candidate preference survives held-out NR4A3 conformers and matched
  paralogue panels. Fail: reject or redesign, regardless of best-frame score.
- **Gate D — receptor effect vs conformer effect.** Pass: receptor preference exceeds between-conformer
  variability. Fail: the candidate is structure-sensitive, not computationally selective.
- **Gate E — matched null.** Pass: candidate exceeds a generation-matched null and does not merely exploit its
  design frame. Fail: treat the result as generator–receptor overfitting.

## Stopping rules

Stop advancing a candidate when any occurs: preference reverses in a prespecified NR4A3 conformer; a matched
NR4A1/2 conformer becomes clearly favoured; the result depends on an unestablished protonation state; the
result depends on one arbitrary stereoisomer; conformer variance exceeds receptor preference; the candidate
clears only the receptor frame used for generation; repaired ABFE does not reproduce the scoring direction;
overlap/convergence remains pathological; the exact generation receptor fails the harmonized pocket audit.
**Do not rescue failed candidates through post hoc conformer selection.**

## Required deliverables

1. Harmonized pocket-tracking specification and tests. 2. Pinned fpocket rerun across all required structures.
3. Exact design-frame dependency-audit report. 4. Dense-λ validation report. 5. Protocol-matched T4L benchmark.
6. TICA/reaction-coordinate validation report. 7. Prespecified receptor-conformer panel with design/validation/
stress split. 8. `denovo_401` conformer-sensitivity mechanism report. 9. Focused analogue library. 10. Unrelated
multi-conformer generation library. 11. Full receptor-by-conformer scoring matrices. 12. Generation-matched
null. 13. Exact species and stereochemistry records. 14. Explicit-solvent multi-seed triage. 15. Repaired
multi-conformer ABFE results. 16. Machine-readable decision ledger showing every rejection and advancement.

## Reporting language

**Use:** computational candidate; NR4A3-favoured profile; conditional receptor contrast; release-derived
bias-free-continuation frame; experiment-seeded computational conformer; same sign across selected conformers;
provisional pending repaired protocol.

**Avoid:** drug; confirmed selective; validated binder; structure-independent selectivity; unbiased receptor
frame; equilibrium population from NMR model counts; robust conformer effect before λ repair; physiological
microstate without pKa/population analysis.

## Final objective

Ideal result: *the first-generation candidate exposed receptor-conformer dependence; ensemble-aware redesign
then produced a second-generation candidate whose NR4A3 preference survived held-out experimental conformers,
matched paralogue conformers, generation-matched controls and repaired multi-conformer ABFE, with the receptor
effect exceeding conformer variability.*

Fallback (also publishable): *no candidate achieved receptor preference exceeding conformer uncertainty,
demonstrating that structural provenance is a dominant limitation for computational selectivity design in this
cryptic pocket.*

**Both outcomes are scientifically useful. Do not weaken the controls to force the first outcome.**
