# NR4A3 paper — Round-5 review response ledger (2026-07-10)

Single manuscript now (`nr4a3-degrader-paper.md` + `-paper-SI.md`); the preprint was retired/consolidated,
so every fix below lands in ONE place. Reviewer recommendation: **major revision**, risk "sharply
concentrated." Status keys: **DONE** (this session) · **EDIT** (text change, no compute) · **GATED**
(waiting on an in-flight/queued run) · **OPEN**.

Reviewer's own top framing: the strongest advance is the metad falsification (independent replicas *invalidate*
the old ~0.6 kcal/mol accessibility story). Central remaining risk = "is the same physical pocket identified
consistently, is 'druggable state' defined equivalently across replicas, and does the receptor preference
survive the NR4A2 λ-repair + NR4A3 structural-model sensitivity."

## ✅ DONE in first round-5 pass (2026-07-10, non-gated integrity/contradiction fixes)
P0.1/2/3/4 metad data-to-text + like-for-like reframe · **c17** NR4A2 overlap propagates directly into
ΔΔG(3−2) (was backwards) · **c18** NR4A2 −4.98±0.68 labelled *initial estimate/provisional* · **c33** "sole
robust lead" → "sole candidate advanced through the computational funnel/to ABFE" (all 5 sites) · **c35**
"Two"→"Three" gate deviations · **c38** Limitations caveat 1 release-run "settles population" → "tests only
short-timescale persistence (3A), not equilibrium accessibility (3B)" · **c39** "equally productive ternaries"
→ "comparable predicted geometry, no evidence for NR4A3-selective ternary" · **c40** "asymmetry conservative"
→ "direction uncertain" · **c41/42** "corroborated/predicted by FEP" → "supported by initial conditional ABFE
receptor contrasts (λ-repair + 8XTT sensitivity pending)".

## ✅ DONE in second round-5 pass (2026-07-10 PM)
**c14** title → reviewer's exact "In silico design of a paralogue-favoured ligand for a cryptic NR4A3 pocket"
(paper+SI) · **c24/c25** denovo_15/94/57/189/111 archaeology CUT to new **SI §S8** (falsification record);
main text condensed + "first designed warhead" claim dropped; Limitations self-contradiction now resolved ·
**SI S7** carried the same c17 error → fixed · **c20/21** methane benchmark reworded, unsourced "GAFF/TIP3P
norms" deleted · **c22** ABFE precedent softened · **c23** winner's-curse "FEP removes selection bias" fixed ·
**c26** §2.4 opener "validated as druggable/accessible" → "cavity-bearing + short-timescale persistence" ·
**c27** repurposing "method-validation" → "did not advance under specificity controls" · **c29** frame-robust →
"same sign in two selected frames" · **c30** Fig S1 "single-snapshot/no-entropy" → multi-frame wording ·
**c31** "single-snapshot margins carry SD" → "multi-frame SDs" · **c32 (partial)** trimmed trustworthy×2 /
crucially×2 / rewrote the refutation sentence (rest of self-cert language = remaining) · **c36** Gate 2 pass →
provisional · **c45/46** PocketMiner terminus/propensity · **c47** fpocket proxy · **c48** enclosure inference
softened · **c49** priority claim removed.

## ✅ DONE in third round-5 pass (2026-07-10 PM) — ALL remaining non-gated EDITs cleared
**c19** ABFE → new Results **§2.7** (§4 de-duplicated to protocol + pointer) · **c34** denovo_111 pKa method
documented honestly (rule-based RDKit SMARTS, NOT a pKa predictor — no tool fabricated) · **c28** 6k screen
condensed to 1 sentence + SI pointer · **c50** references block completed (titles verified for NR4A2-DBD +
ETV6/EWS-FLI1; 2 unverifiable marked "title TBD at submission") · **c52** AI disclosure model family + access
period surfaced, **Figures** statement (programmatic, no gen-AI images), actual **Acknowledgments** section
added · **c37** Gate-4 prose halved · **c5** per-replica COLVAR provenance table + r2 reclassified as
pipeline-repair · **c6** drift-comparison protocol specified (verified vs code) · **c3** "closed basin" →
"single F(Rg) minimum".

**⚠ CORRECTNESS FIX (commit d402fb5):** the metad cross-replica values were listed **sorted**, not in r1/r2/r3
order; the round-5 reviewer misread the sorted list and P0.1's "fix" trusted the misreading. Data file is
unambiguous: **r1** = basin 0.87 / ΔF 16.03 (expanded/uphill), r2 = 0.73/0.06, r3 = 0.74/0.83. Now stated in
explicit r1/r2/r3 order everywhere.

**c43 8XTT-first reorder — DONE** (trimcrae: "churn costs nothing"). Results now open 8XTT-first: NEW §2.1
(experimental 8XTT ensemble) + §2.2 (AF2 working model); metad→§2.3, handles→§2.4, matrix→§2.5, de-novo→§2.6,
multi-snapshot→§2.7, ABFE→§2.8. ~63 paper + ~23 SI cross-refs remapped and verified (headings 2.1–2.8
sequential, no dangling refs). **c32 self-cert sweep — DONE** (remaining "honest read"/"true weight"/etc.
trimmed).

**✅ ALL NON-GATED ROUND-5 EDITS ARE NOW COMPLETE.**

**Still gated on tonight's fleet (nothing else to do until results land):** c5(pocket)/8/9/10/11/13/14
harmonized pocket rerun + pinned fpocket · c15 NR4A2 λ-repair · c16 8XTT ABFE sensitivity · c7/c44 Fig 1
(8XTT-centered) & Fig 2 (3-replica) redesign. When they land: fold numbers into §2.1/§2.3/§2.8, regenerate
Figs 1–2, done.

## P0 — submission blockers
| # | Item | Status |
|---|------|--------|
| 1 | r1/r2/r3 metad data-to-text contradiction (prose mislabelled which replica is uphill) | **DONE** (commit be1d57e) — r1/r2 near-basin, r3 (0.87 nm) expanded/uphill |
| 2 | Cross-replica ΔF at fixed Rg is not like-for-like (same Rg ≠ same pocket/druggability) | **DONE (text)** — reframed to "free energy assigned to the reference Rg region"; per-replica pocket scoring flagged pending. Full fix **GATED** on harmonized rerun (P1.13) |
| 3 | "one closed basin" not structurally justified from a 1-D minimum | **DONE (text)** — now "single F(Rg) minimum", not "closed"; classification pending |
| 4 | State strongest honest metad conclusion as the narrower one (profiles differ) | **DONE (text)** |
| 5 | r2 COLVAR/event-analysis provenance (corr=0.96 but "single usable sample") | **OPEN — EDIT** (add a per-replica provenance table: HILLS/raw-COLVAR/reduced-COLVAR/FES/event/2D validity); if reduction kept 1 sample, repair not caveat |
| 6 | Within-run drift metric needs a specified comparison protocol (zeroing, common support, masking, 2nd less edge-sensitive metric e.g. RMSE) | **OPEN — EDIT** (+ small analysis) |
| 7 | Promote the 3-replica disagreement to a central figure (new Fig 2); demote the 60 ns single-traj profile | **GATED** (figure regen; pairs with harmonized rerun panel D) |
| 8 | Independent orthosteric-site definition (current "highest-druggability pocket w/ ≥1 residue in 373–626" = score-selection at the foundation) | **GATED** — harmonized `pocket_tracking` uses fixed lining-residue set + composite gate; **rerun in flight** |
| 9 | Replace ≥1-residue matching rule (Jaccard≥0.25, ≥40% recovered, centroid≤5 Å) | **GATED** — implemented (JACCARD_MIN 0.25 / FRAC_RECOVERED 0.30 / CENTROID 8 Å); **rerun in flight** (revisit thresholds vs reviewer's 40%/5 Å) |
| 10 | Report BOTH detected-pocket and all-frame denominators as a main result | **GATED** — both computed by reharmonize; fold table into Results after rerun |
| 11 | Pin fpocket (4.2.3) + rerun ALL load-bearing analyses (panel/AF2/20×8XTT/metad replicas/3 release) | **GATED** — pinned; reharmonize rerun in flight |
| 12 | Remove denovo_15/94/57/189/111 archaeology from main text → SI (reviewer: "largest editorial problem"; self-contradiction vs Limitations) | **OPEN — EDIT** (big) |
| 13 | Per-replica harmonized pocket scoring on the 3 metad replicas (define druggable region per replica) | **GATED** — add metad-replica ensembles to reharmonize |
| 14 | Structural classification of each FES minimum (closed vs open) | **GATED** |
| 15 | Finish NR4A2 λ-repair | **GATED** — running (nr4a2rep r1/r2/r3) |
| 16 | Finish 8XTT-anchored NR4A3 ABFE **sensitivity** (frame as receptor-model sensitivity, NOT experimental-anchored selectivity; predefine conformer/pose/charge/λ; selection must not use denovo_401 score) | **GATED** — running (abfe-8xtt r1/r2/r3); predefinition = EDIT now |
| 17 | NR4A2 overlap error propagates DIRECTLY into ΔΔG(3−2) — current "reinforces resting on ΔΔG" is WRONG | **OPEN — EDIT** (Methods/Results/Falsification/Abstract) |
| 18 | Treat −4.98 ± 0.68 NR4A2 as **provisional/initial estimate** everywhere; no precise/tight/strongest/stable | **OPEN — EDIT** |
| 19 | ABFE results → new Results **§2.7** (not Methods); §2.6→§4 jump | **GATED-ish** (structure now; final numbers tonight) |

## P1 — strengthening (mostly GATED on the reharmonize/ABFE fleet)
13 per-replica pocket scoring · 14 FES-minimum classification · 15 non-redundant 2nd CV (pocket volume / χ-states) · 16 event-based recrossing w/ hysteresis · 17 cross-replica FES on common support · 18 8XTT matched decoy null (ran) · 19 harmonized all-20 8XTT (in rerun) · 20 AF2↔NMR vs NMR↔NMR RMSD decomposition (cheap) · 21 contact-graph PocketMiner null (cheap) · 22 selection-aware divergence permutation (cheap) · 23 generation-matched decoy null (ran; fold) · 24 production-matched T4L (running, #3).

## P2 / wording — EDIT (non-gated)
- **20** methane "machinery is sound" → "supports basic solvent-decoupling on a simple neutral system".
- **21** "well within GAFF/TIP3P norms" → cite or delete.
- **22** ABFE precedent → "provides precedent for receptor-to-receptor selectivity estimates using ABFE across related proteins".
- **23** winner's-curse: "FEP removes selection bias" is wrong → "higher-tier calcs test the selected molecule but don't erase the selection".
- **24/25** cut denovo archaeology + its stale claims ("first designed NR4A3-selective warhead", "survives an endpoint energy model", "selectivity FEP remain the gates ahead", "next de-novo steps re-generate").
- **26** §2.4 opener "pocket validated as druggable and accessible" → "cavity-bearing model geometries + short-timescale persistence"; "screen a selective warhead" → "screen for an NR4A3-favoured profile".
- **27** "repurposed matter is method-validation" → "did not yield a candidate that advanced under later specificity controls".
- **28** move 6k screen to SI.
- **29** "+7.44 stays NR4A3-selective" → "retains a positive NR4A3-favoured endpoint margin"; "selectivity direction frame-robust" → "same sign in the two selected frames".
- **30** SI Fig S1 "single-snapshot/no-entropy" → "short-trajectory multi-frame endpoint MM-GBSA without entropy or equilibrated receptor ensemble".
- **31** "single-snapshot margins carry SD 4–6" is wrong → "multi-frame analysis revealed frame-to-frame SDs ~4–6, comparable to/larger than several single-snapshot margins".
- **32** strip self-certifying language (honest read / true weight / trustworthy / real / confirmed / crucially / decisively).
- **33** "sole robust lead" → "sole candidate advanced through the current computational funnel".
- **34** denovo_111 pKa method (software/version/predicted pKa/protomer pops/tautomer policy) — load-bearing rejection, document it.
- **35** Falsification intro "Two gate outcomes deviate" → **"Three"**.
- **36** Gate 2 "pass" + "pending" → "provisional / initial pass under original implementation, final pending harmonized reanalysis".
- **37** shorten Gate-4 prose under the table.
- **38** Limitations caveat 1 kinetic/thermo error ("settled by the release run") contradicts Abstract/§2.2/3A-3B → delete/replace.
- **39** Limitations caveat 5 "equally productive ternaries" → use earlier "no evidence for selective ternary geometry" wording consistently.
- **40** Limitations caveat 7 "asymmetry conservative" contradicts §2.5 "direction uncertain" → delete.
- **41** "corroborated by FEP" → "supported by initial conditional ABFE receptor contrasts" (while λ-repair + 8XTT sensitivity pending).
- **42** strongest-claim sentence "predicted by absolute-binding FEP to retain selectivity" → "designed for an NR4A3-favoured profile and supported by initial ABFE receptor contrasts conditional on selected opened conformers".
- **43** Results 8XTT-first reorder (2.1 8XTT → 2.2 AF2 working model → 2.3 metad replicas → 2.4 persistence → 2.5 handles → 2.6 generation → 2.7 ABFE).
- **44** Fig 1 → 8XTT-centered (conformers/distribution/AF2-vs-distribution/reference sites/AF2↔8XTT RMSD).
- **45** PocketMiner terminus: drop "decisively"/"proves"; "enrichment persists under a null excluding the truncation-edge region".
- **46** PocketMiner "corroborates site existence" → "supports elevated cryptic-pocket-forming propensity".
- **47** "fpocket standard, validated metric" → "established computational pocket-druggability proxy".
- **48** fpocket "splayed-open would score lower ∴ enclosure" mechanistic inference → report component features or delete.
- **49** remove "to our knowledge, the first pocket-dynamics analysis of NR4A3" priority claim.
- **50** references "identifiers only" block → complete titles or move claims to SI.
- **51** mint archive DOI before submission (custom pocket-tracking/ABFE/generated mols).
- **52** AI disclosure: model versions into Methods/SI (not just archive); add actual Acknowledgments; state whether figures used generative AI.

## Title (c14) — reviewer prefers "In silico design of a paralogue-favoured ligand for a cryptic NR4A3 pocket"
"paralogue-selective pocket" reads as the *pocket* being selective; "In-silico" → "In silico" (unhyphenated
adjectival). **OPEN — EDIT** (consider adopting reviewer's exact title).
