# NR4A3 selective degrader — ensemble-robust redesign plan

*Branch `claude/nr4a3-ensemble-redesign` · single source of truth for the redesign · created 2026-07-11
(trimcrae directive: "design a new candidate against an ensemble-defined target, not another molecule
against one selected frame").*

Read alongside: the program state ([`nr4a3-degrader-next-steps.md`](./nr4a3-degrader-next-steps.md)), the
manuscript §2.1/§2.8 ([`../manuscripts/nr4a3-degrader-paper.md`](../manuscripts/nr4a3-degrader-paper.md)), the
pre-registration ([`nr4a3-druggability-prereg.md`](./nr4a3-druggability-prereg.md)), and the harmonized
pocket tracker ([`pocket_tracking.py`](./pocket_tracking.py) + [`nr4a3_pocket_reharmonize.py`](./nr4a3_pocket_reharmonize.py)).
**This plan is the source of truth for the redesign's next steps** (per trimcrae's 2026-07-11 directive).

## 1. Why redesign (the single-frame failure modes we already hit)

Every NR4A3-selective candidate so far — `denovo_401` and the `lo_m0_*` lead-opt series — was nominated by a
score in **one** receptor frame. Two of our own results say that is not enough:

- **Metad-frame decoy null (2026-07-01).** `denovo_401` clears the *release-frame* multi-snapshot decoy null
  (+12.83 vs 95th +6.69) but **fails the metad-opened-frame null** (+7.44 at ~84th pct; 6/38 decoys higher).
  Its specificity is **receptor-frame-dependent**.
- **8XTT provenance recalc (2026-07-10).** Anchoring the NR4A3 ABFE leg on an 8XTT-derived druggable NMR
  conformer instead of the AF2-opened frame moves ΔG_bind by **~4.7 kcal/mol** (+8.17 vs +3.5) — **larger than
  the entire selectivity margin.** The **conformer effect can exceed the receptor (paralogue) effect.**

A new *molecule* can fix ligand fragility; it cannot fix an ill-defined pocket or mismatched receptor states.
The redesign therefore reframes the target as an **ensemble**, and reranks candidates on **worst-case
robustness across a prespecified conformer panel**, not best score in one frame.

## 2. Two campaigns in parallel

### Keep `denovo_401` as the benchmark (do NOT discard it)
It is the current best AF2-frame candidate, the positive control for the existing funnel, the reference for
measuring conformer robustness, and the probe of which chemical features drive the AF2-vs-8XTT sensitivity.
**Rule: a new compound must BEAT `denovo_401` on a matched multi-conformer test** (worst-case S *and*
worst-case selectivity margin — see `ensemble_robust_score.beats_benchmark`), not merely score better in one
frame. The `lo_m0_NCCO/CC/SNOO` ortho-decorated series is the existing **Branch A** output; under FEP it came
out **affinity/selectivity-EQUAL to 401, not tighter** — so Branch A has not yet produced a robust *beat*, and
its members must be re-tested on the same conformer panel as everyone else.

### Start the ensemble-robust redesign
Build the design objective around **several** receptor structures.

## 3. The conformer panel (design / validation / stress)

The panel is split so generalisation is **tested, not assumed**. The generator and early scoring see ONLY the
design conformers; the validation conformers are held out.

**✅ GATE-1 audit landed (2026-07-11 — [`nr4a3-pocket-reharmonize-summary.json`](./nr4a3-pocket-reharmonize-summary.json)).**
The harmonized, **score-independent** pocket tracker (fixed Pocket-5 lining set; composite Jaccard/recovery +
centroid gate; pinned fpocket 4.0; D\*=0.53) gives two facts that fix the panel:
1. **The canonical site is real and well-defined** — detected in **95–100 %** of frames in *every* ensemble
   (8XTT 19/20; metad 25/25; all 75 unbiased release frames; AF2-static). Site identity is decoupled from the
   fpocket score, so the earlier circularity concern is closed.
2. **Druggability is a low-population property of the experimental ensemble** — only **3/20 (15 %)** 8XTT NMR
   models clear D\*, vs metad 68 %, unbiased-release-pooled **59 %** (44/75), AF2-static 0/1. The honest
   cryptic-pocket picture: the site is nearly always geometrically present but druggably *open* ~15 % of the
   time experimentally.

Panel membership, grounded in the audit:

- **NR4A3 design set (2–3, moderately open):** moderately-open **druggable frames from the unbiased release
  sub-ensemble** (44/75 clear D\*; `nr4a3-release-druggable` primary/alt1/alt3). **Not** the AF2-opened frame
  (that is `denovo_401`'s design frame → circular).
- **NR4A3 validation set (held-out, never seen by the generator/early scoring):** the **3 druggable 8XTT NMR
  models** (the audit's experimental druggable minority — the highest-value held-out *experimental* test) +
  release-druggable frames not used in design.
- **NR4A3 stress set:** the **occluded 8XTT models** (the ~16 detected-but-below-D\* + the 1 non-detected) +
  the **original AF2-opened release frame** (scoring a 401-derived scaffold there is a circularity probe, not
  pass/fail) + a **metad-opened frame** (68 % druggable but a known promiscuous discriminator → hardest
  specificity stress).
- **NR4A1 / NR4A2 panels:** matched — the **same** harmonized pocket definition (the fixed Pocket-5 lining set
  mapped by BLOSUM62 / `residue_map`) and the **same** geometric selection rules, over AF, crystal-seeded-opened
  (3V3E / 1OVL are collapsed → require the symmetric opening-MD step), and the metad-opened paralogue frames
  (NR4A1 frame 524 druggability 0.981, NR4A2 frame 125 0.938).

## 4. The scoring objective (implemented, unit-tested)

For a candidate scored across the panel (favourability units, higher = tighter; = −ΔG):

```
S  =  min_c M_{3,c}   −   λ·SD_c(M_{3,c})   −   γ·max_{p∈{1,2},c} B_{p,c}
```

- `M_{3,c}` = NR4A3 favourability in conformer *c*; `min_c` = **worst-case** (not best/mean).
- `SD_c(M_{3,c})` = conformer-sensitivity penalty (λ, default 1.0).
- `max_{p,c} B_{p,c}` = worst paralogue leakage over **every** tested paralogue conformer (γ, default 1.0) —
  so a candidate cannot hide a paralogue counterexample in an untested pocket state.
- Chemical liabilities stay a **hard upstream developability gate** (`structural_alerts.py`), not folded into S.

**The central criterion:** `|receptor effect| > |conformer effect|` — the NR4A3-vs-paralogue preference must
exceed the frame-to-frame wobble; if the conformer effect dominates, the "selectivity" is a geometry artefact
(exactly the 401 provenance situation). This and the whole objective are in
**[`ensemble_robust_score.py`](./ensemble_robust_score.py)** (pure, dependency-free, 24 unit tests in
`tests/test_ensemble_robust_score.py`): `robust_score`, `receptor_vs_conformer`, `panel_split_report`,
`beats_benchmark`, `advancement_verdict`, `rank_candidates`. Running it needs the panel + docking/MM-GBSA
tiers; the decision logic itself is done and gated on nothing.

## 5. Two chemical branches

- **Branch A — optimize `denovo_401` (matched molecular pairs).** Determine what causes the structural
  sensitivity: reduce hydrophobic dependence on one precise pocket shape; add 1–2 directional interactions to
  stable NR4A3-specific residues; reduce cLogP; test smaller/less flexible analogues; vary substituents near
  the four NR4A3-vs-NR4A2 handles (L406/T410/I484/L534); evaluate the co-best stereoisomer rather than assuming
  the generated isomer. `nr4a3_leadopt.py` already enumerates 401 decorations — extend it to score on the
  panel, not one frame.
- **Branch B — generate new chemotypes jointly against multiple NR4A3 conformers** (not conditioned on one
  release frame). Prioritise candidates that contact ≥2 conserved structural anchors AND ≥2 NR4A3-divergent
  handles, don't rely on a single mobile side chain, preserve their interaction pattern across conformers,
  don't acquire favourable paralogue poses when those pockets expand, and have unambiguous protonation/tautomer
  states. A new scaffold may be necessary if 401's hydrophobic shape-complementarity is inherently tied to the
  AF2 pocket.

## 6. Revised funnel

1. **Harmonized pocket qualification** — only conformers passing the fixed site definition
   (`pocket_tracking`) enter the panel.
2. **Multi-conformer generation / docking** — no single-frame nomination.
3. **Matched paralogue counter-screen** — same state-selection rules for all three receptors.
4. **Generation-matched null** — controls generated against paralogue/irrelevant pockets
   (`nr4a3_generation_matched_null.py`), not only a comparison to marketed drugs.
5. **Microstate & stereochemistry resolution** — before expensive simulation (`fep_species.py` pattern).
6. **Independent short explicit-solvent pose tests** — multiple seeds and conformers.
7. **Endpoint scoring across the whole panel** — rank by worst-case margin and conformer variance
   (`ensemble_robust_score`).
8. **Repaired ABFE on ≥2 conformers per receptor** — never advance on one structure per protein.
9. **Opening-state weighting** — only for the final one or two candidates.

## 7. Sequencing & gates (what unblocks what)

**Cheap redesign work is gated on the audit; expensive ABFE on new compounds is gated on the λ / T4L work.**

- **✅ GATE-1 (cheap work) — CLEARED 2026-07-11.** The harmonized pocket-tracking audit landed
  ([`nr4a3-pocket-reharmonize-summary.json`](./nr4a3-pocket-reharmonize-summary.json), §3): the canonical site
  is confirmed (95–100 % detection across all ensembles by a score-independent definition) and the conformer
  panel is defensibly fixed (3 druggable 8XTT NMR models = held-out experimental; release-druggable frames =
  design; occluded/AF2/metad = stress). Ensemble construction, scaffold enumeration, multi-conformer docking,
  generation-matched controls, and chemical triage are now **unblocked** (CPU/spot, non-FEP).
- **GATE-2 (expensive ABFE on NEW compounds):** per trimcrae's directive, do not commit substantial ABFE to
  new compounds until (a) the dense-λ schedule is validated, (b) T4L benchmark v2 is understood (engine
  absolute-accuracy anchor), and (c) the same repaired protocol is applied to **both** the AF2- and
  8XTT-derived NR4A3 states.

Per the standing autonomy rules: build/enumerate/triage (engineering + CPU docks) proceed once GATE-1 clears;
each expensive GPU leg (selectivity FEP on a new candidate) still needs the explicit FEP go-ahead (§ FEP
carve-out) and waits behind GATE-2.

## 8. Advancement criteria (a credible NEW candidate must satisfy ALL)

Encoded in `ensemble_robust_score.advancement_verdict` (tri-state: pass / fail / not-yet-assessed):

- NR4A3-favoured in **every** prespecified design conformer;
- retains preference in **held-out** 8XTT-derived validation conformers;
- **worst-case** selectivity margin > 0 (favoured in the worst panel conformer);
- `|receptor effect| > |conformer effect|` — **the central criterion**;
- clears the generation-matched decoy null;
- no dependence on one protonation state or arbitrary stereoisomer;
- repaired ABFE gives the **same preference direction** on ≥2 NR4A3 conformers;
- no single paralogue conformer produces a strong counterexample;
- **beats `denovo_401`** on the matched panel (worst-case S and worst-case margin).

Until such a candidate exists, call the output a **new computational candidate / chemotype**, not a new drug.

## 9. Paper implication

A candidate designed **in response to** the falsification result — whose NR4A3 preference generalises across
held-out experimental conformers and exceeds between-conformer uncertainty — is a strictly stronger story than
the current single-frame narrative: *"the first candidate exposed receptor-conformer dependence; an
ensemble-robust redesign then produced a second-generation candidate whose preference generalised and exceeded
the conformer effect."* That is the deliverable this branch is for.

## 10. Status (2026-07-11)

- ✅ **Scoring layer built:** `ensemble_robust_score.py` + 24 unit tests.
- ✅ **Plan codified:** this document.
- ✅ **GATE-1 cleared:** harmonized pocket-tracking audit landed + committed; conformer panel fixed (§3).
- ⏳ **GATE-2:** λ-repair validation + T4L v2 + repaired both-provenance NR4A3 ABFE (prereq for new-compound ABFE; FEP-class, held per trimcrae's "short of a new FEP run").
- ▶ **Next (non-FEP, unblocked):** wire `ensemble_robust_score` into `nr4a3_matrix` / `nr4a3_leadopt` /
  `nr4a3_8xtt_conformer_scoring` to rank Branch-A (`lo_m0_*`) and Branch-B candidates on the panel; build the
  panel receptor set from the audit-selected conformers; run the generation-matched null on the redesign.
  These are CPU/spot dock + MM-GBSA tiers (no new FEP).
