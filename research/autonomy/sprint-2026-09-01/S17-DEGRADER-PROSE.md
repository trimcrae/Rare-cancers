---
id: DOC-SPRINT-S17-DEGRADER-PROSE
title: "S17-DEGRADER-PROSE — splitting PUB-DEGRADER's 145 over-length sentences without moving a claim"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S17-DEGRADER-PROSE — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S17-DEGRADER-PROSE — 145 → 0 over-ceiling sentences in the degrader paper

**Item(s):** readability of `PUB-DEGRADER` (`publish_bar` clause 7, `readable_enough_to_review`); the
worklist is S5-READABILITY's measurement, taken after that seat repaired `lint_readability.sentences()`
**Owned paths:** `research/manuscripts/degrader/nr4a3-degrader-paper.md`, this file
**Started/Finished (UTC):** 2026-09-01

## Verdict

**FIXED.** `research/manuscripts/degrader/nr4a3-degrader-paper.md` now measures **0 sentences over the
60-word ceiling** (was 145, longest 175 w), with **no caution marker lost** — the caution count *rose*
521 → 523 and no individual marker class fell. `lint_readability --check` on the file is **green**.

⛔ **The paper grew, and by how much is stated rather than glossed: +168 raw words (45,364 → 45,532,
+0.37 %) and +81 extracted-prose words (41,450 → 41,531, +0.20 %).** Splitting a semicolon-joined clause
into a sentence needs a subject and a finite verb that the clause borrowed from its neighbour — "…, so the
fractions are not denominator-inflated; the harmonized re-analysis is done" becomes "… not
denominator-inflated. **The** harmonized re-analysis is done". 214 tokens were added and 48 removed, and
essentially all of both are function words (`the`, `is`, `it`, `we`, `that`) and participles turned into
finite verbs (*Superposing* → *We superposed*; *Repeating it* → *We repeated it*). **No content word,
number, identifier or citation was removed anywhere** — see "What I measured" below for the census that
establishes it.

## What I measured

### 1 · Refute-by-default: the defect is real, and it is real prose

S5-READABILITY's row said PUB-DEGRADER carried **145** genuine over-ceiling sentences, longest 175 w. It
reproduced exactly on the working tree with the corrected splitter:

```
$ python3 research/manuscripts/lint_readability.py --report research/manuscripts/degrader/nr4a3-degrader-paper.md
nr4a3-degrader-paper.md    1314  31.5  62  175   145  17.2   12.6
```

⭐ **But not all 145 were prose defects, and the split matters for what the next seat should expect.**
Working through them found **three measurement artefacts** that the corrected splitter still produces,
each of which I fixed **in the prose** rather than by touching the instrument (not an owned path, and
`lint_readability.py` is S5's file):

| artefact | why the splitter joins the pair | how many | prose fix used |
|---|---|---:|---|
| a sentence opening with a **lowercase word** (`fpocket analysis of …`, `denovo_401 is a …` where the inline-code name is stripped to nothing) | `_CALLOUT_OPENERS` deliberately excludes a lowercase opener — a false split understates a length, so the exclusion is the safe direction | 3 | reworded the opener (`An fpocket analysis …`, `The candidate \`denovo_401\` is …`) |
| a sentence opening with a **digit** (`8/10 Pocket-5 residues …`, `5 ns cannot establish …`, `3A — persistence …`) | same exclusion | 4 | `In that scoring, **8/10** …`; `A 5 ns window cannot …`; `Subclaim **3A** …` |
| a **stop inside two closers** (`… sub-state.")*`) | the closer-aware lookbehind is fixed-width and handles one closer, not `."` + `)` | 1 | dropped the inner quotation so the sentence ends `… sub-state.)` |
| a **bulleted list** whose items end in `;` and start lowercase, measured as one sentence (the §2.2 calibration panel at 150 w; the §2.8 ΔΔG bullets at 96 w) | `paragraphs()` does not break at a list item — **this is exactly ledger row 1 of S5-READABILITY**, still open | 2 | ended each bullet with `.` and gave it a capital opener |

⛔ **None of these is a licence to loosen the splitter**, and I did not touch it: every one of them
overstates a length, which is the safe direction, and the prose reads better after the rewording anyway.
⭐ The list-item case is the one worth the driver's attention, because S5's proposed ledger row 1 measures
5 such flags corpus-wide and two of them were in this paper.

### 2 · The result

| measure | before | after |
|---|---:|---:|
| sentences over the 60-word ceiling | **145** | **0** |
| longest sentence | **175 w** | **60 w** |
| mean sentence length | 31.5 w | **26.5 w** |
| p90 sentence length | 62 w | **48 w** |
| % over 40 words | 29.9 % | **20.8 %** |
| Flesch–Kincaid grade | 17.2 | **15.3** |
| sentences counted | 1,314 | 1,569 |
| **caution markers** | **521** | **523** |
| caution per 1000 w | 12.6 | 12.6 |
| extracted prose words | 41,450 | 41,531 (+81) |
| raw file words | 45,364 | 45,532 (+168) |

```
$ python3 research/manuscripts/lint_readability.py --check research/manuscripts/degrader/nr4a3-degrader-paper.md
✅ readability check OK (1 document(s)): no sentence over 60 words, no caution lost.
```

### 3 · ⛔ The check that readability did not cost honesty (`scientific-writing` §4)

This is the failure the seat exists to prevent, so it is measured three ways rather than asserted.

**(a) Caution markers rose and none fell.** Itemised over the raw file with `lint_readability._CAUTION`
and `_INTERVAL`, before vs after — only two classes moved, both **up**:

```
total markers 440 -> 442
  is not:      81 -> 82
  limitation:   9 -> 10
```

**(b) A hedge census over the whole file, before vs after** — every class held or rose except one token:

```
'never' 34->34   'cannot' 43->43   'does not' 72->72   'do not' 25->25   'is not' 81->82
'are not' 17->17 'was not' 13->13  'were not' 5->5     'unresolved' 18->18 'provisional' 13->13
'unvalidated' 4->4  'limitation' 15->16  'caveat' 16->16  'only' 135->135  'may' 23->23
'might' 2->2  'could' 27->27  'withdrawn' 20->20  'retracted' 9->9  'null' 109->109
'not' 807 -> 806   <-- the one fall
```

⭐ **The single lost `not` is located and it is a synonym swap, not a dropped qualification.** It is in
the §3 pocket-tracking limits: *"recorded as missing (`None`) and **excluded** — not scored zero — so
every reported fraction …"* became *"… and **excluded** rather than scored zero, so every reported
fraction …"*. The excluded-vs-scored-zero distinction — which is the whole point of that limitation,
because it is what can inflate a frame fraction — is intact.

**(c) A punctuation-insensitive token diff over the entire file.** 214 tokens added, 48 removed. The
complete removed list is function words and participles: `which`(5) `while`(3) `and`(2) `by`(2) `but`(2)
`addressed`(2) `not`(1, above) `under` `exceeding` `whose` `probed` `favouring` `so` `chemistry`
`displacing` `does` `sampling` `making` `asking` `detect` `though` `strength` `precisely` `mapping`
`running` `match` `requiring` `then` `collapse` `aligning` `drops` `re-scored` `repeating` `evaluating`
`superposing` `enumerating` `measuring` `holding`. **No number, unit, gene symbol, PDB ID, PMID, p-value,
kcal/mol figure or citation appears in that list**, and every participle has a finite-verb counterpart in
the added list.

**(d) I re-read every rewritten sentence against its original.** The full before/after table is the
appendix of this file — 114 edit sites, each rendered as the removed text and the text that replaced it,
so the driver can audit meaning rather than trust it.

### 4 · Gates run (scoped to my change, per charter §6)

| gate | result |
|---|---|
| `lint_readability.py --check` on the paper | ✅ green (this seat's target) |
| `lint_readability` splitter suite (53 tests) | ✅ 53 passed |
| `lint_claims.py` | ✅ **0 ERROR** (170 WARN corpus-wide, 24 of them on this paper, all pre-existing R1–R5 advisories) |
| `lint_consistency.py` | ✅ 0 ERROR across 26 target files |
| `lint_citations.py` | ⚠ 1 ERROR — `program/emc-treatment-roadmap.md:497`, a missing cached PubMed record. **Not mine, not my file, pre-existing.** |
| `lint_style.py` (default targets) | ⚠ 1 ERROR — `neoantigen/emc-vaccine-development-path.md:653`. **Not mine.** ⭐ The degrader paper **is not in `lint_style.TARGETS`** (12 targets, this is not one), so the prose-style gate does not run on it; forced onto the file by hand it reports 1170 → 1176 bold-midsentence hits, i.e. the change is neutral on a gate that does not apply. |
| `pytest test_verify_map_edit_anchors.py test_line_citations.py` | ⚠ **1 failed** — `test_no_resolvable_line_citation_points_at_the_wrong_line`. See below: **already red at HEAD**, and my edit adds to it. |

## What I could not do, and what it is actually waiting on

⛔ **One real follow-up, and it needs a path I do not own.** Splitting sentences added ~100 lines to the
paper, so the roadmap's `:NNNN` line citations into it have drifted and `test_line_citations.py` fails.

⭐ **That test was already failing before I touched anything**, proved rather than assumed — running the
resolver's own quote-search against `git show HEAD:…nr4a3-degrader-paper.md`:

| citation | true line at HEAD | true line now | verdict |
|---|---:|---:|---|
| `:2508` "This paper's claimed contribution…" | 2576 | 2611 | **stale at HEAD** |
| `:2200` "validates **one contact in one pair**" | 2272 | 2298 | **stale at HEAD** |
| `:552` "the **pre-harmonized** tracker" | 567 | 575 | **stale at HEAD** |
| `:1310` "under-binding by ≈ +7.1 kcal/mol" | 1310 | 1325 | drift is mine |
| `:2363` "approximately reproduced" | 2363 | 2391 | drift is mine |
| `:1596` "**four** NR4A3-unique cysteines" | 1596 | 1614 | drift is mine |
| `:2851` "priced, **not run**" | 2851 | 2892 | drift is mine |

**The fix is one command and it belongs to the driver**, because `line_citations.py --fix` writes into
`research/manuscripts/nr4a3-program-map.md` and the downstream copies it names — none of them mine, and
running it from a seat while eleven others mutate the tree is precisely what charter §2 forbids:

```
python3 research/manuscripts/line_citations.py --fix        # then regenerate the copies it names
```

⚠ **And it must run AFTER my edit lands**, not before — the derived line numbers are only correct against
the committed paper.

⭐ **The 12 `NOT FOUND` citations the resolver also reports are NOT mine and must not be swept in.** Each
quote is absent from `git show HEAD` of the paper as well — checked string by string — so they are
pre-existing paraphrase rot, and `line_citations.py` deliberately leaves them alone rather than
repointing them.

**Nothing else is blocked.** No other file was touched. `readability-baseline.json` needs no change: this
paper is not one of its 11 pinned documents, and the caution ratio is unmoved at 12.6 either way.

## Ledger rows the driver should write

1. **`what`:** ⭐ PUB-DEGRADER's readability clause is CLEARED — `nr4a3-degrader-paper.md` measures 0
   sentences over the 60-word ceiling (was 145, longest 175 w), caution 521 → 523, no marker class
   fell, paper +0.37 % raw words. `publish_bar` clause 7 (`readable_enough_to_review`) computes from a
   committed sha, so it flips on the commit that lands this edit, not before.
   **`kind`:** `manuscript` · **`state`:** `done` · `cost_class`: free.

2. **`what`:** ⛔ `line_citations.py --fix` MUST RUN AFTER THE S17 PROSE EDIT LANDS, AND THE TEST WAS
   ALREADY RED BEFORE IT. Three roadmap citations into the degrader paper (`:2508`, `:2200`, `:552`)
   were measurably stale at HEAD; the prose split adds ~17 more. One `--fix` run clears both classes;
   the 12 `NOT FOUND` entries are pre-existing paraphrase rot and are deliberately left alone.
   **`kind`:** `process_defect` · **`state`:** `queued` · `cost_class`: free.

3. **`what`:** ⚠ `lint_readability.paragraphs()` LIST-ITEM DEFECT COST TWO REAL FLAGS IN PUB-DEGRADER —
   a 150-word "sentence" (§2.2 nuclear-receptor calibration panel) and a 96-word one (§2.8 ΔΔG
   contrasts) were each a bulleted list joined into one paragraph. Both were fixed in the prose here
   (bullets now end in `.` and open with a capital), so the paper no longer depends on the repair —
   but this is the SAME defect as S5-READABILITY's proposed ledger row 1, now with two more instances
   measured, and the corpus-wide 5 remain.
   **`kind`:** `process_defect` · **`state`:** `queued` · `cost_class`: free.

4. **`what`:** ⚠ THE SPLITTER STILL JOINS A SENTENCE THAT OPENS WITH A LOWERCASE WORD, A DIGIT, OR AFTER
   A STOP INSIDE TWO CLOSERS (`."` + `)`) — 8 of PUB-DEGRADER's 145 flags were one of these, not
   over-length prose. ⛔ **This is the SAFE direction and the exclusions are deliberate** (a false
   split understates a length and walks a long sentence past the gate), so the row is a note for the
   next writer, **not** a request to widen `_CALLOUT_OPENERS`: the cheap fix is to reword the opener,
   which is what was done here. The one arguably-mechanical case is the double closer, where the
   fixed-width lookbehind handles `.)` but not `.")`.
   **`kind`:** `note` · **`state`:** `queued` · `cost_class`: free.

## Amendment record

**None required.** `amendment_guard.is_governed()` covers `**/tests/**` and the governed constants; this
seat edited one manuscript and one findings file, changed no threshold, no bar, no baseline and no
instrument. `SENTENCE_CEILING` is untouched at 60 and `publish_bar.py` was not opened for writing.
⭐ **The self-serving edit available here was to widen the splitter so the paper measured better, and it
was not taken:** the eight artefact flags were fixed in the prose instead, leaving the instrument stricter
than the paper.

---

## Appendix — the full before/after audit, 114 edit sites

⛔ **This is the deliverable.** Each site is the text removed and the text that replaced it, rendered from
`git diff` so it cannot drift from what is on disk. Read it as the meaning check: every number,
identifier, hedge, null and limitation should appear on both sides.

<!-- 114 edit sites -->

#### 1 · original line 45

**Before —** solution-NMR ensemble (PDB 8XTT, 2025). fpocket analysis of the 20 deposited low-energy conformers shows **substantial geometric heterogeneity at the mapped orthosteric site** — most strongly occluded, a few exceeding an empirical drug-bound reference boundary (these are low-energy structural models, **not** equilibrium-population samples) — and a three-independent-seed metadynamics workflow on an AlphaFold2 working model explores cavity-bearing "open-like" geometries; short bias-free continuations from a selected geometry show **geometric persistence in 3/3 replicas** (harmonized pocket-tracking: the orthosteric pocket is detected in every propagated frame of all three replicas and is druggable at ≥ D\*=0.53 in **56 %/40 %/80 %** of frames per replica — **44/75 = 59 % pooled**), while the replicas do **not** yet agree on a **common quantitative free-energy profile**. A falsification-heavy, pocket-conditioned generative campaign (chemical triage, an empirical decoy null, multi-snapshot rescoring, independent-seed replication, and molecular-species resolution) leaves a single candidate, **denovo_401**, whose NR4A3-favoured preference is probed by **initial three-replicate absolute-binding free-energy calculations conditional on selected opened conformers** (favouring NR4A3 over both paralogues in the AF2-opened states; a receptor-specific λ-overlap defect leaves the whole block provisional, its repair is scoped but held, and the engine's *absolute* scale is not validated). A completed

**After —** solution-NMR ensemble (PDB 8XTT, 2025). An fpocket analysis of the 20 deposited low-energy conformers shows **substantial geometric heterogeneity at the mapped orthosteric site**: most are strongly occluded, and a few exceed an empirical drug-bound reference boundary. These are low-energy structural models, **not** equilibrium-population samples. A three-independent-seed metadynamics workflow on an AlphaFold2 working model explores cavity-bearing "open-like" geometries, and short bias-free continuations from a selected geometry show **geometric persistence in 3/3 replicas**. Harmonized pocket-tracking detects the orthosteric pocket in every propagated frame of all three replicas, druggable at ≥ D\*=0.53 in **56 %/40 %/80 %** of frames per replica (**44/75 = 59 % pooled**). The replicas do **not** yet agree on a **common quantitative free-energy profile**. A falsification-heavy, pocket-conditioned generative campaign — chemical triage, an empirical decoy null, multi-snapshot rescoring, independent-seed replication, and molecular-species resolution — leaves a single candidate, **denovo_401**. **Initial three-replicate absolute-binding free-energy calculations conditional on selected opened conformers** probe its NR4A3-favoured preference, and favour NR4A3 over both paralogues in the AF2-opened states. A receptor-specific λ-overlap defect leaves the whole block provisional, its repair is scoped but held, and the engine's *absolute* scale is not validated. A completed

#### 2 · original line 66

**Before —** which NR4A1/NR4A2 are structurally incapable rather than merely disfavoured. It identifies an exposed any receptor model; finds that the chemistry axis is **one residue deep, with no geometric fallback**; returns a **negative on E3-recruiter breadth** (structural stageability, not target availability, is the binding constraint, and widening the panel confirmed the incumbent recruiters rather than displacing them); nominates orientation basins that exploit the categorical terms in only a **small minority** of placements; and enumerates a **reversible-covalent-preferring virtual linker library** whose covalent handle is reported as an unresolved liability alongside the parent warhead's own pharmacology. Two ubiquitination-geometry parameters are corrected against solved intact assemblies rather than assumed. **A preregistered known-answer test of the ternary machinery itself — measured SPR cooperativity for a linker pyridine→benzene edge on SMARCA2/VHL — returns the wrong sign in all three preregistered replicates (ΔΔG_coop = −0.599 kcal/mol at n = 3 vs a target of +0.944), and does so with converged, structurally stable, forward/reverse-antisymmetric sampling and a closed cycle, making the miss ~34× the statistical uncertainty and therefore systematic rather than a sampling deficit that replicates could remove.** No cooperativity or — a sensitivity control asking whether the endpoint readout can detect paralogue selectivity that a primary source reports, run on SMARCA2 vs SMARCA4 with the PRT3789 chemotype, a pair with solved structures on both arms — returns a NULL on an adequately-powered design** (exact one-sided *p* = 0.7468; reference set of 462 arrangements with a floor of 0.00216 against α = 0.05; no technical failures; the observed separation runs opposite to the predicted direction but is not significant in either, mirrored *p* = 0.2554). **Every

**After —** which NR4A1/NR4A2 are structurally incapable rather than merely disfavoured. That stage identifies an exposed any receptor model. It finds that the chemistry axis is **one residue deep, with no geometric fallback**. It returns a **negative on E3-recruiter breadth**: structural stageability, not target availability, is the binding constraint, and widening the panel confirmed the incumbent recruiters rather than displacing them. It nominates orientation basins that exploit the categorical terms in only a **small minority** of placements. And it enumerates a **reversible-covalent-preferring virtual linker library** whose covalent handle is reported as an unresolved liability alongside the parent warhead's own pharmacology. Two ubiquitination-geometry parameters are corrected against solved intact assemblies rather than assumed. **A preregistered known-answer test of the ternary machinery itself — measured SPR cooperativity for a linker pyridine→benzene edge on SMARCA2/VHL — returns the wrong sign in all three preregistered replicates** (ΔΔG_coop = −0.599 kcal/mol at n = 3 vs a target of +0.944). **It does so with converged, structurally stable, forward/reverse-antisymmetric sampling and a closed cycle, which makes the miss ~34× the statistical uncertainty and therefore systematic rather than a sampling deficit that replicates could remove.** No cooperativity or asks whether the endpoint readout can detect paralogue selectivity that a primary source reports**: a sensitivity control run on SMARCA2 vs SMARCA4 with the PRT3789 chemotype, a pair with solved structures on both arms. **It returns a NULL on an adequately-powered design** (exact one-sided *p* = 0.7468; reference set of 462 arrangements with a floor of 0.00216 against α = 0.05; no technical failures). The observed separation runs opposite to the predicted direction but is not significant in either direction (mirrored *p* = 0.2554). **Every

#### 3 · original line 94

**Before —** study — **no molecule was synthesized and no wet-lab validation was performed** — whose principal unresolved dependence of the free-energy selectivity**, cross-replica convergence, the atomic binding pose and ensemble-weighted selectivity, and — for the prospective stage — a double conditionality on a hypothesized warhead pose and a chosen receptor frame.

**After —** study: **no molecule was synthesized and no wet-lab validation was performed**. Its principal unresolved dependence of the free-energy selectivity**, cross-replica convergence, and the atomic binding pose and ensemble-weighted selectivity. For the prospective stage, a further limitation is the double conditionality on a hypothesized warhead pose and a chosen receptor frame.

#### 4 · original line 107

**Before —** structurally.** A fragment screen against NOR-1/NR4A3 (hit rate <1 %) returned three ligand chemotypes, one *"Druggability Evaluation of NOR-1"*; the same compounds are recapitulated in the Safe 2025 review, which PubMed types as a **Retracted Publication** — the primary result here is Zaienne 2022 and does not rest on it). We note leave the binding site structurally undefined: NR4A3's LBD has an experimental structure only as a recently released **apo solution-NMR ensemble (PDB 8XTT, 2025)** — **no ligand-bound structure and no published pocket-dynamics analysis** exist — the structural gap this paper addresses (our in-silico druggable pocket supplies a candidate *mechanism* for the ligandability their pharmacology already demonstrates). Crucially, 8XTT also **corroborates** that premise rather than pre-empting our work: an

**After —** structurally.** A fragment screen against NOR-1/NR4A3 (hit rate <1 %) returned three ligand chemotypes. One was *"Druggability Evaluation of NOR-1"*). The same compounds are recapitulated in the Safe 2025 review, which PubMed types as a **Retracted Publication**; the primary result here is Zaienne 2022 and does not rest on it. We note leave the binding site structurally undefined. NR4A3's LBD has an experimental structure only as a recently released **apo solution-NMR ensemble (PDB 8XTT, 2025)**: **no ligand-bound structure and no published pocket-dynamics analysis** exist. That is the structural gap this paper addresses, and our in-silico druggable pocket supplies a candidate *mechanism* for the ligandability their pharmacology already demonstrates. Crucially, 8XTT also **corroborates** that premise rather than pre-empting our work: an

#### 5 · original line 132

**Before —** Targeted **degradation** is one attractive downstream application: productive target *engagement* need not itself encode the sustained occupancy pharmacology that a classical agonist/antagonist requires (the demonstrated NR4A ligandability above is real but chemotype-specific and mostly low-affinity), so a degrader that transiently engages the LBD to recruit an E3 and remove the protein is a rational route —

**After —** Targeted **degradation** is one attractive downstream application. Productive target *engagement* need not itself encode the sustained occupancy pharmacology that a classical agonist/antagonist requires, and the demonstrated NR4A ligandability above is real but chemotype-specific and mostly low-affinity. A degrader that transiently engages the LBD to recruit an E3 and remove the protein is therefore a rational route —

#### 6 · original line 150

**Before —** more directly, the heterobifunctional PROTAC class reached its first regulatory approval in May 2026: vepdegestrant (ARV-471), an oral cereblon-recruiting **estrogen-receptor** degrader, was approved by the FDA for ESR1-mutated ER+/HER2− advanced breast cancer (FDA 2026), on the strength of the phase-3 VERITAC-2 trial in which — in the ESR1-mutant population — median progression-free survival was 5.0 vs 2.1 months versus fulvestrant

**After —** more directly, the heterobifunctional PROTAC class reached its first regulatory approval in May 2026. Vepdegestrant (ARV-471), an oral cereblon-recruiting **estrogen-receptor** degrader, was approved by the FDA for ESR1-mutated ER+/HER2− advanced breast cancer (FDA 2026). The approval rests on the phase-3 VERITAC-2 trial, in which the ESR1-mutant population had median progression-free survival of 5.0 vs 2.1 months versus fulvestrant

#### 7 · original line 163

**Before —** **nuclear receptors** — the estrogen and androgen receptors, the same superfamily as NR4A3 — and nuclear receptors have proven a favourable degrader class precisely because their ligand-binding domain offers a defined pocket with decades of prior medicinal chemistry, and because removing the receptor circumvents resistance that

**After —** **nuclear receptors** — the estrogen and androgen receptors, the same superfamily as NR4A3. Nuclear receptors have proven a favourable degrader class for two reasons: their ligand-binding domain offers a defined pocket with decades of prior medicinal chemistry, and removing the receptor circumvents resistance that

#### 8 · original line 188

**Before —** not an AF2-independent site *discovery*). Mapping our pocket-5 residues onto 8XTT (sequence identity 1.000, 248 residues mapped) and running the **corresponding fpocket analysis workflow** per conformer (build pinning `nr4a3_8xtt_benchmark.py`) shows **substantial conformational heterogeneity at the same mapped site**: most

**After —** not an AF2-independent site *discovery*). We mapped our pocket-5 residues onto 8XTT (sequence identity 1.000, 248 residues mapped) and ran the **corresponding fpocket analysis workflow** per conformer (build pinning `nr4a3_8xtt_benchmark.py`). It shows **substantial conformational heterogeneity at the same mapped site**: most

#### 9 · original line 200

**Before —** conformers** (one fewer than the original 4/20, as expected from the pinned build and the stricter score-independent matcher). Because these are observation, not an estimate of a 15 % open-state population** (and both the experimental median and the static the AF2 model — AF2 may over-open the site relative to the typical 8XTT conformer). The point is qualitative

**After —** conformers**. That is one fewer than the original 4/20, as expected from the pinned build and the stricter score-independent matcher. Because these are observation, not an estimate of a 15 % open-state population**. Both the experimental median and the static the AF2 model — AF2 may over-open the site relative to the typical 8XTT conformer. The point is qualitative

#### 10 · original line 211

**Before —** this global divergence to genuine apo flexibility rather than model error: over all shared Cα, the AF2 model's

**After —** this global divergence to genuine apo flexibility rather than model error. Over all shared Cα, the AF2 model's

#### 11 · original line 219

**Before —** Cα-RMSD (`nr4a_af_crystal_rmsd.py`; BLOSUM62 residue maps): the AlphaFold models reproduce the experimental folds tightly — **NR4A1 AF vs Nur77 crystal 3V3E global 1.20 Å / Pocket-5-local 0.44 Å; NR4A2 AF vs Nurr1

**After —** Cα-RMSD (`nr4a_af_crystal_rmsd.py`; BLOSUM62 residue maps). The AlphaFold models reproduce the experimental folds tightly: **NR4A1 AF vs Nur77 crystal 3V3E global 1.20 Å / Pocket-5-local 0.44 Å; NR4A2 AF vs Nurr1

#### 12 · original line 229

**Before —** 8XTT-derived conformers (not a full workflow rebase — the metadynamics, generation, and ABFE still run on AF2-derived structures) hold:** (i) **PocketMiner scored on the 8XTT conformers still enriches** the Pocket-5 residues (median 1.40× vs 1.36× on AF2 — the propensity call **transfers to the experimental conformers**, though, evaluated at the preselected AF2-defined region, it does not by itself establish an AF2-independent site *discovery*); and (ii) a **multi-snapshot MM-GBSA re-dock of `denovo_401` into the four cavity-bearing 8XTT conformers keeps its NR4A3 preference in all four** (min-margin median 9.4 kcal/mol; NR4A3 favoured over both paralogue reference states in every conformer). These are **binding-competent-state robustness tests, not an unbiased ensemble

**After —** 8XTT-derived conformers hold** — this is not a full workflow rebase, and the metadynamics, generation, and ABFE still run on AF2-derived structures. (i) **PocketMiner scored on the 8XTT conformers still enriches** the Pocket-5 residues (median 1.40× vs 1.36× on AF2), so the propensity call **transfers to the experimental conformers**; evaluated at the preselected AF2-defined region, it does not by itself establish an AF2-independent site *discovery*. (ii) A **multi-snapshot MM-GBSA re-dock of `denovo_401` into the four cavity-bearing 8XTT conformers keeps its NR4A3 preference in all four** (min-margin median 9.4 kcal/mol; NR4A3 favoured over both paralogue reference states in every conformer). These are **binding-competent-state robustness tests, not an unbiased ensemble

#### 13 · original line 251

**Before —** experimental 8XTT NMR ensemble (0.15)**. Two readings follow, both stated straight: (i) an independent, and openability on a *new* evidence axis; and (ii) the concordance of **two unbiased sources (BioEmu 0.125, NMR enhanced-sampling fractions likely **over-represent** the open state — the honest open-state population is more

**After —** experimental 8XTT NMR ensemble (0.15)**. Two readings follow, both stated straight. (i) An independent, and openability on a *new* evidence axis. (ii) The concordance of **two unbiased sources (BioEmu 0.125, NMR enhanced-sampling fractions likely **over-represent** the open state; the honest open-state population is more

#### 14 · original line 265

**Before —** nuclear-receptor calibration panel ([`../modalities/nr4a3_calibration.py`](../../modalities/nr4a3_calibration.py)): - experimentally **drug-bound** NR pockets score **0.53–0.68** (PPARγ/rosiglitazone 0.599, ERα/estradiol 0.586, Nurr1-holo 0.677, Nur77-holo 0.529) → **empirical reference boundary D\* = 0.53** (the lower edge of this small, selected drug-bound panel — a descriptive reference, not a statistically calibrated threshold with a negative distribution); - fpocket **`max` is non-discriminating** (even the occluded 1OVL crystal scores 0.864 at a *non-orthosteric* cavity) — so the widely-quoted "Nurr1 ~0.8" is **not** the orthosteric pocket, and is present in both model (0.801) and crystal (0.864), i.e. **not an AlphaFold artifact**; - the AF2 static orthosteric score (0.495) lies **below the empirical drug-bound reference boundary (D\* = 0.53)** but **above the median score across the deposited 8XTT conformers** (0.012; §2.1 above); the AF2 model may therefore already represent a **relatively open member of the experimentally

**After —** nuclear-receptor calibration panel ([`../modalities/nr4a3_calibration.py`](../../modalities/nr4a3_calibration.py)). - Experimentally **drug-bound** NR pockets score **0.53–0.68** (PPARγ/rosiglitazone 0.599, ERα/estradiol 0.586, Nurr1-holo 0.677, Nur77-holo 0.529) → **empirical reference boundary D\* = 0.53**. That boundary is the lower edge of this small, selected drug-bound panel — a descriptive reference, not a statistically calibrated threshold with a negative distribution. - The fpocket **`max` score is non-discriminating**: even the occluded 1OVL crystal scores 0.864 at a *non-orthosteric* cavity. So the widely-quoted "Nurr1 ~0.8" is **not** the orthosteric pocket, and it is present in both model (0.801) and crystal (0.864), i.e. **not an AlphaFold artifact**. - The AF2 static orthosteric score (0.495) lies **below the empirical drug-bound reference boundary (D\* = 0.53)** but **above the median score across the deposited 8XTT conformers** (0.012; §2.1 above). The AF2 model may therefore already represent a **relatively open member of the experimentally

#### 15 · original line 291

**Before —** 0.47 whole-LBD background (1.36× enrichment)**, with **8/10 Pocket-5 residues ≥ 0.5** and **4/10 ≥ 0.7** (residues 406, 481, 484, 531 — three of which, 406/484/531, are among our seven selectivity handles); eight true weight, with two honest caveats: (i) PocketMiner is a *propensity predictor* — it supports **elevated opened geometry nor a druggability value, which remain the job of the metadynamics + fpocket analysis below; and (ii) the

**After —** 0.47 whole-LBD background (1.36× enrichment)**. In that scoring, **8/10 Pocket-5 residues** are ≥ 0.5 and **4/10 ≥ 0.7** (residues 406, 481, 484, 531 — three of which, 406/484/531, are among our seven selectivity handles), and eight true weight, with two honest caveats. (i) PocketMiner is a *propensity predictor*: it supports **elevated opened geometry nor a druggability value, which remain the job of the metadynamics + fpocket analysis below. (ii) The

#### 16 · original line 307

**Before —** permutation** — which corrects for having *selected* the Pocket-5 patch by requiring it to beat the *best* same-size contiguous window under each permutation, not merely a random one — is decisive about the terminus: with the truncation edge included the enrichment does **not** survive the familywise correction (p = 0.74, because that edge itself supplies the winning patches), but with the flagged region masked it **does**

**After —** permutation** corrects for having *selected* the Pocket-5 patch: it requires that patch to beat the *best* same-size contiguous window under each permutation, not merely a random one. That test is decisive about the terminus. With the truncation edge included the enrichment does **not** survive the familywise correction (p = 0.74, because that edge itself supplies the winning patches); with the flagged region masked it **does**

#### 17 · original line 362

**Before —** per-frame fpocket on the **orthosteric Pocket-5 cavity** (the *same* metric as the static 0.495 and D\*, not the non-discriminating "max-anywhere" cavity of §2.2) reaches druggability **0.931** (max over the 25 fpocket-sampled frames; mean 0.582; `crosses_0.5 = True`; ≥ D\*=0.53 in 0.68 of sampled frames); SASA of the lining residues rises by up to **+6.1 nm²**, with **70.8 % of the 1200 frames more open than the equilibrated production-frame-0 baseline**. (A 5 ns validation gave a consistent 0.751.)

**After —** per-frame fpocket on the **orthosteric Pocket-5 cavity** reaches druggability **0.931** (max over the 25 fpocket-sampled frames; mean 0.582; `crosses_0.5 = True`; ≥ D\*=0.53 in 0.68 of sampled frames). That is the *same* metric as the static 0.495 and D\*, not the non-discriminating "max-anywhere" cavity of §2.2. SASA of the lining residues rises by up to **+6.1 nm²**, with **70.8 % of the 1200 frames more open than the equilibrated production-frame-0 baseline**. (A 5 ns validation gave a consistent 0.751.)

#### 18 · original line 391

**Before —** hydrophobic breathing cavity. fpocket cannot establish whether such geometries occur with appreciable **equilibrium probability**; the open-seeded **release** simulations (below) address only the narrower

**After —** hydrophobic breathing cavity. Whether such geometries occur with appreciable **equilibrium probability** is something fpocket cannot establish. The open-seeded **release** simulations (below) address only the narrower

#### 19 · original line 399

**Before —** (druggable frames + handles pocket-facing, below); **the harmonized pocket-tracking re-analysis has since been run and committed** and the frame-fraction clause passes more strongly under it (0.56/0.40/0.80 vs the earlier 0.20/0.16/0.28), while the **handles-pocket-facing clause was not re-run under the harmonized tracker** and is

**After —** (druggable frames + handles pocket-facing, below). **The harmonized pocket-tracking re-analysis has since been run and committed**, and the frame-fraction clause passes more strongly under it (0.56/0.40/0.80 vs the earlier 0.20/0.16/0.28). The **handles-pocket-facing clause was not re-run under the harmonized tracker** and is

#### 20 · original line 411

**Before —** jointly settle** (a kinetic/thermodynamic distinction): **3A — persistence after bias removal** (does a seeded open-like geometry promptly collapse?) and **3B — equilibrium energetic accessibility from the closed ensemble** (is that geometry reachable with appreciable probability at equilibrium?). **3B is addressed only provisionally, by the biased F(Rg)** (this paragraph); **3A is addressed by the release run** (next paragraph). Neither establishes the other: a conformation can be equilibrium-rare yet persist for a few ns superseded single-profile reasoning, for completeness: the naive closed→fully-open cost is ~38 kcal/mol, but that is the cost to the *most-open* edge (Rg 1.06) at the **under-converged sampling frontier**, not a *druggable* state: correlating per-frame druggability with F(Rg) shows the pocket is already druggable (fpocket 0.80) at Rg ≈ 0.72 — in the well-sampled basin region — at only ~0.76 kcal/mol. The caveat:

**After —** jointly settle**, a kinetic/thermodynamic distinction. Subclaim **3A — persistence after bias removal** asks whether a seeded open-like geometry promptly collapses. Subclaim **3B — equilibrium energetic accessibility from the closed ensemble** asks whether that geometry is reachable with appreciable probability at equilibrium. We address **3B only provisionally, by the biased F(Rg)** (this paragraph), and **3A by the release run** (next paragraph). Neither establishes the other: a conformation can be equilibrium-rare yet persist for a few ns superseded single-profile reasoning, for completeness. The naive closed→fully-open cost is ~38 kcal/mol, but that is the cost to the *most-open* edge (Rg 1.06) at the **under-converged sampling frontier**, not a *druggable* state. Correlating per-frame druggability with F(Rg) shows the pocket is already druggable (fpocket 0.80) at Rg ≈ 0.72 — in the well-sampled basin region — at only ~0.76 kcal/mol. The caveat:

#### 21 · original line 439

**Before —** only over the **interpretable region** with sparsely-sampled edge bins excluded; we quote the pointwise **max**|ΔF|, and the **mean and RMSD** of |ΔF| over the same region — also computed by

**After —** only over the **interpretable region** with sparsely-sampled edge bins excluded. We quote the pointwise **max**|ΔF|. The **mean and RMSD** of |ΔF| over the same region — also computed by

#### 22 · original line 455

**Before —** (0.87 nm)**, putting the same reference geometry ≈ 16 kcal/mol uphill. Two cautions bound this comparison, both flagged for the harmonized rerun: a fixed Rg independent replica (the per-replica harmonized pocket scoring that would define an equivalent druggable region is pending, §3), and a single F(Rg) minimum is not, on its own, a structural classification of a "closed"

**After —** (0.87 nm)**, putting the same reference geometry ≈ 16 kcal/mol uphill. Two cautions bound this comparison, both flagged for the harmonized rerun. First, a fixed Rg independent replica; the per-replica harmonized pocket scoring that would define an equivalent druggable region is pending (§3). Second, a single F(Rg) minimum is not, on its own, a structural classification of a "closed"

#### 23 · original line 466

**Before —** whether Rg captures all slow degrees of freedom**. A data-driven test now shows it does **not**: **TICA

**After —** whether Rg captures all slow degrees of freedom**. A data-driven test now shows it does **not**. **TICA

#### 24 · original line 472

**Before —** **data-derived coordinate directly** rather than adding sampling to the 1-D Rg profile (in progress; §4). **(iv) Recrossing is heterogeneous** (a "crossing" is a **low-Rg↔high-Rg reference/"druggable" window **Rg ∈ [0.7, 1.1] nm** — *not* a structurally classified closed↔open transition; a distinct entry into the window counts as one "visit" (so a long residence is one visit, not many, but no minimum-dwell filter is applied and no structural state is defined — refinements flagged for the harmonized re-analysis): r1 shows **3 low-Rg↔high-Rg crossings** with 41 window-visits (partial recrossing); r3 makes **360 window-visits** but does not fully recross within 30 ns; **r2's crossing count is not reported** (its

**After —** **data-derived coordinate directly** rather than adding sampling to the 1-D Rg profile (in progress; §4). **(iv) Recrossing is heterogeneous.** Here a "crossing" is a **low-Rg↔high-Rg reference/"druggable" window **Rg ∈ [0.7, 1.1] nm** — and *not* a structurally classified closed↔open transition. A distinct entry into the window counts as one "visit", so a long residence is one visit, not many; no minimum-dwell filter is applied and no structural state is defined, and both refinements are flagged for the harmonized re-analysis. On that definition, r1 shows **3 low-Rg↔high-Rg crossings** with 41 window-visits (partial recrossing), r3 makes **360 window-visits** but does not fully recross within 30 ns, and **r2's crossing count is not reported** (its

#### 25 · original line 485

**Before —** correlation above use the full **HILLS / raw COLVAR** and are valid for all three replicas; the

**After —** correlation above use the full **HILLS / raw COLVAR** and are valid for all three replicas. The

#### 26 · original line 506

**Before —** Net: enhanced sampling generated cavity-bearing geometries not represented by the static AF2 snapshot (0.495); the biased metadynamics profile breathes to a geometrically druggable cavity at low apparent cost on that shows that cavity **persists over the 5 ns propagated** (not that it is a thermally-populated equilibrium state) — a feasibility result, stated at that weight.

**After —** Net: enhanced sampling generated cavity-bearing geometries not represented by the static AF2 snapshot (0.495). The biased metadynamics profile breathes to a geometrically druggable cavity at low apparent cost on that shows that cavity **persists over the 5 ns propagated** — not that it is a thermally-populated equilibrium state. That is a feasibility result, stated at that weight.

#### 27 · original line 520

**Before —** replica; *provenance note:* these two persistence numbers are recorded in the committed run ledger repository** — they are reproducible from the deposited trajectories, not checkable against a repo artifact). the orthosteric Pocket-5 is **detected in 75/75 propagated frames (detection fraction 1.00 in every replica)** and is druggable at ≥ D\*=0.53 in **56 % / 40 % / 80 %** of frames (rep0/rep1/rep2) — **44/75 = 59 % pooled** **Rg-persistence** result across the triplicate; the druggability frame-fraction was originally quoted on the 20/25), pooled **44/75 = 0.59**, so **all three independent bias-free trajectories cross into the druggable

**After —** replica). *Provenance note:* these two persistence numbers are recorded in the committed run ledger repository** — they are reproducible from the deposited trajectories, not checkable against a repo artifact. the orthosteric Pocket-5 is **detected in 75/75 propagated frames (detection fraction 1.00 in every replica)**. It is druggable at ≥ D\*=0.53 in **56 % / 40 % / 80 %** of frames (rep0/rep1/rep2) — **44/75 = 59 % pooled** **Rg-persistence** result across the triplicate. The druggability frame-fraction was originally quoted on the 20/25), pooled **44/75 = 0.59**. So **all three independent bias-free trajectories cross into the druggable

#### 28 · original line 548

**Before —** (ii) **5 ns is a short persistence window**: no prompt sub-nanosecond collapse of the seeded conformation was observed in these three trajectories, but a geometry can hold on 5 ns and still relax on tens–hundreds of ns, so "persists" here means "does not promptly collapse," not "a verified long-lived sub-state.")* This is **not** a

**After —** (ii) **5 ns is a short persistence window.** No prompt sub-nanosecond collapse of the seeded conformation was observed in these three trajectories, but a geometry can hold on 5 ns and still relax on tens–hundreds of ns, so "persists" here means that it does not promptly collapse, not that it is a verified long-lived sub-state.)* This is **not** a

#### 29 · original line 556

**Before —** not denominator-inflated; the **harmonized re-analysis is done and is what is quoted here** the frames, not the pocket-matching rule. 5 ns cannot establish the equilibrium probability of

**After —** not denominator-inflated. The **harmonized re-analysis is done and is what is quoted here** the frames, not the pocket-matching rule. A 5 ns window cannot establish the equilibrium probability of

#### 30 · original line 581

**Before —** screen's handle-contact scoring (§2.5). The open-seeded "release" run is the orthogonal Gate-3A test (does the seeded open-like geometry persist, or promptly collapse once the bias is removed?); the seeded geometry release replicas** (≥ D\* in 0.56/0.40/0.80, harmonized tracker), so the **short-timescale

**After —** screen's handle-contact scoring (§2.5). The open-seeded "release" run is the orthogonal Gate-3A test: does the seeded open-like geometry persist, or promptly collapse once the bias is removed? The seeded geometry release replicas** (≥ D\* in 0.56/0.40/0.80, harmonized tracker). So the **short-timescale

#### 31 · original line 593

**Before —** ~45 Å for a compact LBD), which a reviewer could read as an over-driven metadynamics artifact — so we measured it directly (`nr4a3_frame_sanity.py`): against the pre-metad AF2 LBD, the opened frame **retains 100 % of the

**After —** ~45 Å for a compact LBD), which a reviewer could read as an over-driven metadynamics artifact, so we measured it directly (`nr4a3_frame_sanity.py`). Against the pre-metad AF2 LBD, the opened frame **retains 100 % of the

#### 32 · original line 637

**Before —** that sentence and are not softenable: a **germline knockout bounds developmental, complete, lifelong loss**, whereas a degrader is adult, transient and incomplete, and **no source cited here measures that regime**; and this work reports **no measured or predicted CNS-exposure datum for any candidate**, so the exposure lever that would otherwise narrow the NR4A2 question is a property of a molecule that does not exist.

**After —** that sentence and are not softenable. First, a **germline knockout bounds developmental, complete, lifelong loss**, whereas a degrader is adult, transient and incomplete, and **no source cited here measures that regime**. Second, this work reports **no measured or predicted CNS-exposure datum for any candidate**, so the exposure lever that would otherwise narrow the NR4A2 question is a property of a molecule that does not exist.

#### 33 · original line 717

**Before —** *opened* conformer (`nr4a3_warhead.py` + `gpu-warhead-aws.yml`): it extracts the most-druggable opened

**After —** *opened* conformer (`nr4a3_warhead.py` + `gpu-warhead-aws.yml`). The screen extracts the most-druggable opened

#### 34 · original line 727

**Before —** to obtain **criterion-matched opened-pocket ensembles** for all three (here and throughout, "criterion-matched" means *analogously selected* high-druggability metadynamics-opened conformers — matched on the selection criterion, **not** on state definition or equilibrium population), and docked one library into each (0.981) / NR4A2 frame 125 (0.938)). Each candidate carries a **selectivity fingerprint** across the family, partitioning

**After —** to obtain **criterion-matched opened-pocket ensembles** for all three, and docked one library into each (0.981) / NR4A2 frame 125 (0.938)). Here and throughout, "criterion-matched" means *analogously selected* high-druggability metadynamics-opened conformers — matched on the selection criterion, **not** on state definition or equilibrium population. Each candidate carries a **selectivity fingerprint** across the family, partitioning

#### 35 · original line 748

**Before —** (amodiaquine, celastrol, + a duplicate), *reversed* 3, *weakened* 2, *rescued* 3, *confirmed_nonselective* 2. MM-GBSA magnitudes here are inflated by the single-snapshot/no-entropy approximation, so we read the **verdict/direction, not the kcal/mol** — but the direction is clear: **the exploratory repurposing screen

**After —** (amodiaquine, celastrol, + a duplicate), *reversed* 3, *weakened* 2, *rescued* 3, *confirmed_nonselective* 2. MM-GBSA magnitudes here are inflated by the single-snapshot/no-entropy approximation, so we read the **verdict/direction, not the kcal/mol**. The direction is clear: **the exploratory repurposing screen

#### 36 · original line 757

**Before —** CRBN heavy atom — NR4A3 K195 3.1 Å, NR4A1 K53 2.3 Å, NR4A2 K175 4.0 Å — a **CRBN-proximity proxy, not modeled ubiquitin-transfer geometry**, since no CRL4^CRBN assembly or E2~Ub is included). We read this only as *geometric feasibility*, not as NR4A3-selective ternary geometry** (comparable confidence for all three paralogues from one linker is not proof of nonselectivity), so **this representative modeled linker did not provide evidence that ternary geometry adds NR4A3 selectivity** — degradation selectivity, if any, rests on the **binder** margin, with

**After —** CRBN heavy atom — NR4A3 K195 3.1 Å, NR4A1 K53 2.3 Å, NR4A2 K175 4.0 Å). That distance is a **CRBN-proximity proxy, not modeled ubiquitin-transfer geometry**, since no CRL4^CRBN assembly or E2~Ub is included. We read this only as *geometric feasibility*, not as NR4A3-selective ternary geometry**; comparable confidence for all three paralogues from one linker is not proof of nonselectivity. So **this representative modeled linker did not provide evidence that ternary geometry adds NR4A3 selectivity**. Degradation selectivity, if any, rests on the **binder** margin, with

#### 37 · original line 807

**Before —** affinity or linker ranking. Further limitations: only three seeds × one top model were analyzed here (thin; poses within a seed are nested, so pooled counts overstate independence); the free-celastrol control detects one gross architectural failure (no recruiter) but one control does not establish specificity; celastrol's covalent engagement of NR4A1 Cys551 was **not evaluated here** — the residue-offset lookup has since been rather than merely unmeasured; the Cullin–RING/E2~Ub machinery was absent; and the phenotype does not establish that selectivity is *caused* by ternary geometry. Under the same gross classifier the representative

**After —** affinity or linker ranking. Four further limitations apply. Only three seeds × one top model were analyzed here (thin; poses within a seed are nested, so pooled counts overstate independence). The free-celastrol control detects one gross architectural failure (no recruiter), but one control does not establish specificity. Celastrol's covalent engagement of NR4A1 Cys551 was **not evaluated here**: the residue-offset lookup has since been rather than merely unmeasured. And the Cullin–RING/E2~Ub machinery was absent, so the phenotype does not establish that selectivity is *caused* by ternary geometry. Under the same gross classifier the representative

#### 38 · original line 820

**Before —** 2026-07-11: the metric is "correct-half dual-surface proximity" (not "productive geometry"); the analyzer fixes paired active-vs-epimer comparison — are **committed**; the corrected descriptive rerun is authorized as a

**After —** 2026-07-11. The metric is "correct-half dual-surface proximity", not "productive geometry". The analyzer fixes paired active-vs-epimer comparison — are **committed**. The corrected descriptive rerun is authorized as a

#### 39 · original line 945

**Before —** (amber14 / GAFF-2.11 / TIP3P, OpenMM 4 fs hydrogen-mass-repartitioned LangevinMiddle), scored by an

**After —** (amber14 / GAFF-2.11 / TIP3P, OpenMM 4 fs hydrogen-mass-repartitioned LangevinMiddle). Each is scored by an

#### 40 · original line 1003

**Before —** plausibly runs *against* NR4A3-selectivity (the paralogue pockets are scored in their more-druggable opened state), but a higher fpocket score does not guarantee a more favourable docking score for *every* chemotype, so we treat the direction of this asymmetry as **a limitation of uncertain direction across the library**, demonstrated only for the candidate: a fully criterion-matched re-dock (NR4A3 metad-opened) **has since been run for `denovo_401`** (§2.7) and it **retains a positive NR4A3-favoured endpoint margin** there too (+7.44 ± 4.18), so the positive *sign* is not unique to the design frame — though, as §2.7 shows, the candidate does **not** clear the frame-matched decoy null in that metad frame, i.e. specificity-control success is itself frame-dependent.)* The result is qualitatively different (`denovo_15/94/57`) shows **none is simultaneously chemically viable and a strong selective binder**: the two strong-margin hits carry generative-model liabilities (a carbamic acid / reactive diene; a peroxide / acetals)

**After —** plausibly runs *against* NR4A3-selectivity, because the paralogue pockets are scored in their more-druggable opened state. But a higher fpocket score does not guarantee a more favourable docking score for *every* chemotype, so we treat the direction of this asymmetry as **a limitation of uncertain direction across the library**, demonstrated only for the candidate. A fully criterion-matched re-dock (NR4A3 metad-opened) **has since been run for `denovo_401`** (§2.7) and it **retains a positive NR4A3-favoured endpoint margin** there too (+7.44 ± 4.18), so the positive *sign* is not unique to the design frame. As §2.7 shows, though, the candidate does **not** clear the frame-matched decoy null in that metad frame, i.e. specificity-control success is itself frame-dependent.)* The result is qualitatively different (`denovo_15/94/57`) shows **none is simultaneously chemically viable and a strong selective binder**. The two strong-margin hits carry generative-model liabilities (a carbamic acid / reactive diene; a peroxide / acetals),

#### 41 · original line 1037

**Before —** `selectivity_calibration.py`)** — an empirical rank, not a precisely calibrated universal cutoff (with n = 38 the upper tail is estimated from one or two order statistics, so we also report the raw rank and, in SI, the full ECDF and a bootstrap interval on the percentile). Against that bar, **`denovo_111`** (a clean

**After —** `selectivity_calibration.py`)**. That is an empirical rank, not a precisely calibrated universal cutoff: with n = 38 the upper tail is estimated from one or two order statistics, so we also report the raw rank and, in SI, the full ECDF and a bootstrap interval on the percentile. Against that bar, **`denovo_111`** (a clean

#### 42 · original line 1046

**Before —** reverses selectivity — §2.7; so `denovo_401` is the sole candidate advanced through the computational funnel.))* So the read is therefore **not** "no selectivity"; it is "**raw single-snapshot MM-GBSA is

**After —** reverses selectivity — §2.7. So `denovo_401` is the sole candidate advanced through the computational funnel.))* The read is therefore **not** "no selectivity". It is "**raw single-snapshot MM-GBSA is

#### 43 · original line 1065

**Before —** every published active (docking ΔG −5 to −9 kcal/mol) but does not *discriminate* paralogues:** only THPN's known NR4A1 preference is cleanly recovered, the rest fall within docking noise, and multi-snapshot MM-GBSA does not rescue it — it labels *both* neutral NR4A1 ligands (THPN, TMPA) as **false NR4A3-selective** (the opened NR4A3 frame is intrinsically more accommodating) and the charged 4-aminoquinolines show

**After —** every published active (docking ΔG −5 to −9 kcal/mol) but does not *discriminate* paralogues.** Only THPN's known NR4A1 preference is cleanly recovered, and the rest fall within docking noise. Multi-snapshot MM-GBSA does not rescue it: it labels *both* neutral NR4A1 ligands (THPN, TMPA) as **false NR4A3-selective** (the opened NR4A3 frame is intrinsically more accommodating), and the charged 4-aminoquinolines show

#### 44 · original line 1100

**Before —** pocket-lining side chains grey) — a screening-grade *docked* pose in an AF2-derived LBD *model*, an pose, and **not "the" predicted pose**: the poses this program holds of this molecule in this receptor do

**After —** pocket-lining side chains grey). It is a screening-grade *docked* pose in an AF2-derived LBD *model*, an pose, and **not "the" predicted pose**. The poses this program holds of this molecule in this receptor do

#### 45 · original line 1118

**Before —** comparable to or larger than several single-snapshot margins** — so the single-snapshot "above-null" harvest is noise-dominated; `denovo_393`'s +18.34 was an extreme-value artifact (de-noised, it is ~0/slightly paralogue-favouring): the apparent lead lost its

**After —** comparable to or larger than several single-snapshot margins** — so the single-snapshot "above-null" harvest is noise-dominated. `denovo_393`'s +18.34 was an extreme-value artifact (de-noised, it is ~0/slightly paralogue-favouring). The apparent lead lost its

#### 46 · original line 1173

**Before —** of them — so **every endpoint quantity in this section, the multi-snapshot margins, their decoy-null

**After —** of them. So **every endpoint quantity in this section, the multi-snapshot margins, their decoy-null

#### 47 · original line 1192

**Before —** (marketed drugs pushed through the identical dock→multi-snapshot funnel), but it does **not** control the **generative** step: `denovo_401` is a DiffSBDD molecule pocket-conditioned on the NR4A3 **release** frame, whereas the decoys were fit to no pocket — so in the release frame `denovo_401` carries a design-match

**After —** — marketed drugs pushed through the identical dock→multi-snapshot funnel — but it does **not** control the **generative** step. The candidate `denovo_401` is a DiffSBDD molecule pocket-conditioned on the NR4A3 **release** frame, whereas the decoys were fit to no pocket, so in the release frame `denovo_401` carries a design-match

#### 48 · original line 1223

**Before —** receptor** — a real but **receptor-frame-dependent** signal (it fails the null in the biased metad-opened frame, which is itself non-discriminating), consistent with the selectivity-architecture analysis (SI §S3), that this cryptic pocket is a fragile place

**After —** receptor**. That is a real but **receptor-frame-dependent** signal — it fails the null in the biased metad-opened frame, which is itself non-discriminating — and it is consistent with the selectivity-architecture analysis (SI §S3), which holds that this cryptic pocket is a fragile place

#### 49 · original line 1247

**Before —** that it does not establish anything:** a control campaign that manufactures zero survivors in 191 generations real campaign's own **0.0052** — so a funnel quietly manufacturing at up to that rate is not excluded, and the

**After —** that it does not establish anything.** A control campaign that manufactures zero survivors in 191 generations real campaign's own **0.0052** — so a funnel quietly manufacturing at up to that rate is not excluded. The

#### 50 · original line 1262

**Before —** Two results. (i) **the selected isomer was not uniquely favoured in the endpoint analysis; several diastereomers retained positive margins:** nearly all 16 diastereomers were pipeline-classified within SD), with iso00/iso14 behind — so the as-generated isomer was **among the subset advanced for multi-frame evaluation**, not established as uniquely optimal (isomer selection is itself another winner-selection step). **The completed

**After —** Two results. (i) **The selected isomer was not uniquely favoured in the endpoint analysis, and several diastereomers retained positive margins.** Nearly all 16 diastereomers were pipeline-classified within SD), with iso00/iso14 behind. So the as-generated isomer was **among the subset advanced for multi-frame evaluation**, not established as uniquely optimal — isomer selection is itself another winner-selection step. **The completed

#### 51 · original line 1281

**Before —** (ABFE)** — explicit-solvent (`nr4a3_abfe.py`; protocol and benchmarks in §3) — for `denovo_401` (the resolved DiffSBDD-generated diastereomer, SMILES `COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`) against each of NR4A3, NR4A1 and NR4A2 in its selected opened conformer. SD). We report each selectivity contrast as its raw replicates, mean, SD, and the small-sample 95% *t*-interval (not a Gaussian σ, which n = 3 does not support): - **ΔΔG(NR4A3 − NR4A1):** replicates **−6.90, −2.85, −4.53**; mean **−4.76 ± 2.03** (SD); 95% *t*-interval **[−9.80, +0.28]** kcal/mol — the direction is **unanimous across all three replicates but the contrast is - **ΔΔG(NR4A3 − NR4A2):** replicates **−5.48, −4.20, −5.26**; mean **−4.98 ± 0.68** (SD); 95% *t*-interval **[−6.67, −3.29]** kcal/mol — **resolved below zero** (statistically; still held provisional for the separate λ-overlap reason in (ii) below).

**After —** (ABFE)** for `denovo_401` against each of NR4A3, NR4A1 and NR4A2 in its selected opened conformer. The protocol is explicit-solvent (`nr4a3_abfe.py`; protocol and benchmarks in §3), and `denovo_401` is the resolved DiffSBDD-generated diastereomer, SMILES `COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1`. SD). We report each selectivity contrast as its raw replicates, mean, SD, and the small-sample 95% *t*-interval, not a Gaussian σ, which n = 3 does not support. - For **ΔΔG(NR4A3 − NR4A1)**: replicates **−6.90, −2.85, −4.53**; mean **−4.76 ± 2.03** (SD); 95% *t*-interval **[−9.80, +0.28]** kcal/mol. The direction is **unanimous across all three replicates but the contrast is - For **ΔΔG(NR4A3 − NR4A2)**: replicates **−5.48, −4.20, −5.26**; mean **−4.98 ± 0.68** (SD); 95% *t*-interval **[−6.67, −3.29]** kcal/mol. That contrast is **resolved below zero** statistically, but is still held provisional for the separate λ-overlap reason in (ii) below.

#### 52 · original line 1310

**Before —** returns **+1.90 ± 0.09**, under-binding by **≈ +7.1 kcal/mol** — a failed/strongly-biased absolute benchmark — so we interpret **the receptor contrasts rather than the raw absolute values**, never calibrated absolute affinities, and do not treat +7.1 as a subtractable constant (a single system cannot establish a target-independent offset). The contrast eliminates the literally shared solvent leg and is a **protocol-matched relative comparison expected to reduce some common-mode errors**, but the engine's absolute offset is **not guaranteed to cancel across paralogues** — target-specific restraint terms, receptor-/bound-state definitions, protonation, and treatment; it **remains vulnerable to receptor-specific complex-leg errors** (e.g. the NR4A2 overlap median adjacent overlap per leg is a healthy ≈0.13–0.22, but **every leg — the shared solvent leg and all three

**After —** returns **+1.90 ± 0.09**, under-binding by **≈ +7.1 kcal/mol** — a failed/strongly-biased absolute benchmark. So we interpret **the receptor contrasts rather than the raw absolute values**, never calibrated absolute affinities, and we do not treat +7.1 as a subtractable constant (a single system cannot establish a target-independent offset). The contrast eliminates the literally shared solvent leg and is a **protocol-matched relative comparison expected to reduce some common-mode errors**. But the engine's absolute offset is **not guaranteed to cancel across paralogues**: target-specific restraint terms, receptor-/bound-state definitions, protonation, and treatment. It **remains vulnerable to receptor-specific complex-leg errors** (e.g. the NR4A2 overlap median adjacent overlap per leg is a healthy ≈0.13–0.22. But **every leg — the shared solvent leg and all three

#### 53 · original line 1350

**Before —** conformer (+3.5). Two readings, both stated at their true weight: **(a)** the choice of opened conformer moves structure-independent selectivity; **(b)** this remains a **receptor-model sensitivity test, not a selectivity calculation** — it pairs an experiment-anchored NR4A3 leg against *AF2-opened* paralogue references, a

**After —** conformer (+3.5). Two readings follow, both stated at their true weight. **(a)** The choice of opened conformer moves structure-independent selectivity. **(b)** This remains a **receptor-model sensitivity test, not a selectivity calculation**: it pairs an experiment-anchored NR4A3 leg against *AF2-opened* paralogue references, a

#### 54 · original line 1386

**Before —** carboxylate, a *functional* NR4A3 ligand; IC₅₀ ≈ 8–47 µM, no solved co-crystal pose) → its **5-NH₂** analogue, docked into the same metadynamics-derived **opened** NR4A3 conformer used throughout §2, with OpenFE's

**After —** carboxylate, a *functional* NR4A3 ligand; IC₅₀ ≈ 8–47 µM, no solved co-crystal pose) → its **5-NH₂** analogue. The edge was docked into the same metadynamics-derived **opened** NR4A3 conformer used throughout §2, with OpenFE's

#### 55 · original line 1483

**Before —** `cycle_3carbonyl` — cmpd19 → free acid → primary amide → cmpd19, i.e. `+0.136` and `+2.106` against the direct

**After —** The third, `cycle_3carbonyl` — cmpd19 → free acid → primary amide → cmpd19, i.e. `+0.136` and `+2.106` against the direct

#### 56 · original line 1502

**Before —** does not license a reproducibility statistic in either direction — but it is a direct, concrete illustration of

**After —** does not license a reproducibility statistic in either direction. But it is a direct, concrete illustration of

#### 57 · original line 1529

**Before —** not chemistry, not the atom map (17 mapped against a provable floor of 12) and not the rented hardware: the

**After —** not chemistry, not the atom map (17 mapped against a provable floor of 12) and not the rented hardware. The

#### 58 · original line 1538

**Before —** as a before/after on the same build rather than argued: the system's largest gradient falls from 4.996 × 10¹⁷ to displacement — the singular force is removed and every other force in the box is unchanged to six significant

**After —** as a before/after on the same build rather than argued. The system's largest gradient falls from 4.996 × 10¹⁷ to displacement. The singular force is removed and every other force in the box is unchanged to six significant

#### 59 · original line 1596

**Before —** requiring agreement (`nr4a_paralogue_unique_residues.py`) identifies **four NR4A3-unique cysteines**, of which **Cys397** — NR4A1 Asn363, NR4A2 Ser363 — is exposed and sits **10.9 Å** from the cryptic pocket along the exit vector, and **four NR4A3-unique lysines**, of which **K572, K518 and K592** are exposed in the LBD in the

**After —** requiring agreement (`nr4a_paralogue_unique_residues.py`) identifies **four NR4A3-unique cysteines** and **four NR4A3-unique lysines**. Of the cysteines, **Cys397** — NR4A1 Asn363, NR4A2 Ser363 — is exposed and sits **10.9 Å** from the cryptic pocket along the exit vector. Of the lysines, **K572, K518 and K592** are exposed in the LBD in the

#### 60 · original line 1604

**Before —** **The categorical claim's one untested assumption has now been tested against paralogue dynamics, and it holds.** Uniqueness at the *aligned* position is a sequence fact, but a degrader does not care which cysteine it labels: the assumption that actually carries the claim is that no paralogue presents some **other** nucleophile that the same linker path reaches. That had been checked only on one static conformer per paralogue. Repeating it over **300 matched conformers** — NR4A3/NR4A1/NR4A2, 100 each (25 well-tempered metadynamics on the homologous cryptic-pocket CV + 3 × 25 ns unbiased release, identical protocol per species) — against **73,867 matched E3 placements** at the 12-atom gate gives **P(no paralogue cysteine reachable | the construct reaches an NR4A3-unique cysteine) = 1.000 for solvent-exposed cysteines in every scope** (static, unbiased-release and biased), with the mean per-placement probability of reaching *any* exposed NR4A1 or NR4A2 cysteine identically **0.0**. On the all-cysteine measure a small residue appears (0.12 % unbiased, 0.29 % biased) and it is entirely on **buried** paralogue cysteines — reachability without labelability. *Reported as the rare-event statistic it is:* the conditioning event fires in ~0.04 % of placements (**122 hits in 73,867**), so the defensible statement is the exposed column — **zero co-labelling events observed** — not a probability quoted to five figures. This removes a specific structural failure mode; it says nothing about thiol pKa, nucleophilicity, adduct stability or promiscuity, which remain the untested and chemical limits on this axis. The same analysis reproduces, from the

**After —** **The categorical claim's one untested assumption has now been tested against paralogue dynamics, and it holds.** Uniqueness at the *aligned* position is a sequence fact, but a degrader does not care which cysteine it labels: the assumption that actually carries the claim is that no paralogue presents some **other** nucleophile that the same linker path reaches. That had been checked only on one static conformer per paralogue. We repeated it over **300 matched conformers** — NR4A3/NR4A1/NR4A2, 100 each (25 well-tempered metadynamics on the homologous cryptic-pocket CV + 3 × 25 ns unbiased release, identical protocol per species) — against **73,867 matched E3 placements** at the 12-atom gate. That gives **P(no paralogue cysteine reachable | the construct reaches an NR4A3-unique cysteine) = 1.000 for solvent-exposed cysteines in every scope** (static, unbiased-release and biased), with the mean per-placement probability of reaching *any* exposed NR4A1 or NR4A2 cysteine identically **0.0**. On the all-cysteine measure a small residue appears (0.12 % unbiased, 0.29 % biased) and it is entirely on **buried** paralogue cysteines — reachability without labelability. *Reported as the rare-event statistic it is:* the conditioning event fires in ~0.04 % of placements (**122 hits in 73,867**), so the defensible statement is the exposed column — **zero co-labelling events observed** — not a probability quoted to five figures. This removes a specific structural failure mode; it says nothing about thiol pKa, nucleophilicity, adduct stability or promiscuity, which remain the untested and chemical limits on this axis. The same analysis reproduces, from the

#### 61 · original line 1631

**Before —** fractions say nothing about whether those are the same frames; had they been anti-correlated the axis would

**After —** fractions say nothing about whether those are the same frames. Had they been anti-correlated, the axis would

#### 62 · original line 1647

**Before —** was committed before the fetch** — three eligibility gates (a public ligand-bound structure at ≤3.0 Å or by to a hard cap of two, with **no tunable scalar** (`e3_recruiter_staging.py`; the gates, axes, tiebreak and cap are byte-identical between the preregistering commit and the final artifact). *Stated precisely because the

**After —** was committed before the fetch**. The rule applies three eligibility gates (a public ligand-bound structure at ≤3.0 Å or by to a hard cap of two, with **no tunable scalar**. Its gates, axes, tiebreak and cap are byte-identical between the preregistering commit and the final artifact (`e3_recruiter_staging.py`). *Stated precisely because the

#### 63 · original line 1665

**Before —** to the partner than to DCAF16 itself: that is what a **molecular-glue interface looks like when the partner is taken away — not a handle pocket to hang a linker on** — and it holds despite DCAF16 carrying the panel's negative for the E3-breadth argument rather than a null to absorb quietly. Three honest riders travel with it: the confirmation holds only *after* the biological-assembly frame fix (before it, the advanced pair was the very orientation space being scored — those numbers are retracted, not merely superseded); **BIRC2 lost by bring back at $0; and **the rule is blind to recruiter-intrinsic pharmacology** — MDM2 and KEAP1 rank well on "weakly" is part of the verdict.** Sampling 10⁶ rigid-body placements of each recruiter arm around the warhead-bound target, over an ensemble of **12** warhead exit-vector poses, and evaluating every placement against NR4A3 and both paralogues superposed into **one** frame (so a paralogue difference cannot be an artifact of three independent searches; `nr4a3_basin_search.py`), then clustering on the interface fingerprint the scored terms actually depend on, gives **58 pose-marginalised meta-basins over 192 basins**. Of these,

**After —** to the partner than to DCAF16 itself. That is what a **molecular-glue interface looks like when the partner is taken away — not a handle pocket to hang a linker on**, and it holds despite DCAF16 carrying the panel's negative for the E3-breadth argument rather than a null to absorb quietly. Three honest riders travel with it. First, the confirmation holds only *after* the biological-assembly frame fix: before it, the advanced pair was the very orientation space being scored, and those numbers are retracted, not merely superseded. Second, **BIRC2 lost by bring back at $0. Third, **the rule is blind to recruiter-intrinsic pharmacology**: MDM2 and KEAP1 rank well on "weakly" is part of the verdict.** We sampled 10⁶ rigid-body placements of each recruiter arm around the warhead-bound target, over an ensemble of **12** warhead exit-vector poses, and evaluated every placement against NR4A3 and both paralogues superposed into **one** frame, so a paralogue difference cannot be an artifact of three independent searches (`nr4a3_basin_search.py`). Clustering on the interface fingerprint the scored terms actually depend on gives **58 pose-marginalised meta-basins over 192 basins**. Of these,

#### 64 · original line 1691

**Before —** terms.** **`crbn|M0`** survives **11 of 12** poses and clears the *lysine* term's background by **7.5×** — the best nomination in the run on both counts — but under the exact reach kernel its shortest C397 requirement is

**After —** terms.** **`crbn|M0`** survives **11 of 12** poses and clears the *lysine* term's background by **7.5×**, the best nomination in the run on both counts. But under the exact reach kernel its shortest C397 requirement is

#### 65 · original line 1731

**Before —** placement concluded that linker tractability *inverts* the basin ranking, `crbn|M0` looking the least buildable of the set; emitting the achieving placement explicitly removed that apparent inversion, leaving

**After —** placement concluded that linker tractability *inverts* the basin ranking, with `crbn|M0` looking the least buildable of the set. Emitting the achieving placement explicitly removed that apparent inversion, leaving

#### 66 · original line 1745

**Before —** abolished at 10 Å — 84 of 192 basins still reach rank ≥ 3 somewhere in the sweep at 10 Å against 75 at 17 Å, because a wider zone also picks up **paralogue** lysines and demotes the rank — so the correct statement is

**After —** abolished at 10 Å. 84 of 192 basins still reach rank ≥ 3 somewhere in the sweep at 10 Å against 75 at 17 Å, because a wider zone also picks up **paralogue** lysines and demotes the rank. So the correct statement is

#### 67 · original line 1757

**Before —** generalises past this section — **no degradation-geometry claim in this program may rest on a RING or an E2 that was composed rather than observed** — and it is **not in force in the run reported here**, which anchors

**After —** generalises past this section: **no degradation-geometry claim in this program may rest on a RING or an E2 that was composed rather than observed.** It is **not in force in the run reported here**, which anchors

#### 68 · original line 1768

**Before —** would have weakened the lysine term across the board. **8R5H [69] settles it with no model at all**: it holds reproduces it to **0.09 Å** (like-for-like, because that staging's source entry carries the *same* ligand and the rule selects a neighbouring atom of it — which is also the resolution this convention can be expected to convention's own resolution, not as a precision claim); the alternative misses by **39.15 Å**. Decomposing

**After —** would have weakened the lysine term across the board. **8R5H [69] settles it with no model at all.** It holds reproduces it to **0.09 Å**, and the alternative misses by **39.15 Å**. That comparison is like-for-like, because that staging's source entry carries the *same* ligand and the rule selects a neighbouring atom of it. That is also the resolution this convention can be expected to convention's own resolution, not as a precision claim. Decomposing

#### 69 · original line 1784

**Before —** covalency for a reason that is argued, not measured.** Enumerating linker architectures against each confirmed Cys397's Sγ — gives **36 retained constructs from 3,544 enumerated** at the achieving (exemplar) placement and a further **18 from 1,791** at the representative placement, **54 in total**, under a filter **fixed before enumeration** (span the anchor-to-anchor floor; comfortably hold ≥25 % of the basin's members; ≤3 kT of chain strain at the designed placement; ≤24 backbone atoms; a per-basin cap; one construct retained per confirmed dropping the best basin). *Both placements are enumerated for the reason given in rule 4 above — a construct emitted as an explicit SMILES from staged warhead chemistry (the cmpd19 methyl 5-X-indole-3-carboxylate anchor with exit vectors already in the congeneric series), a published E3 handle (VH032 on the *tert*-leucine nitrogen, or pomalidomide on the 4-amino nitrogen), and an L-amino-acid branch residue that makes the pendant's stereocentre a defined **(S)** centre inherited from a catalogue building block rather than an unspecified one. **All 54 were verified with RDKit against the parsed molecule

**After —** covalency for a reason that is argued, not measured.** We enumerated linker architectures against each confirmed Cys397's Sγ. That gives **36 retained constructs from 3,544 enumerated** at the achieving (exemplar) placement and a further **18 from 1,791** at the representative placement, **54 in total**. The filter was **fixed before enumeration**: span the anchor-to-anchor floor; comfortably hold ≥25 % of the basin's members; ≤3 kT of chain strain at the designed placement; ≤24 backbone atoms; a per-basin cap; and one construct retained per confirmed dropping the best basin. *Both placements are enumerated for the reason given in rule 4 above — a construct emitted as an explicit SMILES from three staged parts: the cmpd19 methyl 5-X-indole-3-carboxylate warhead anchor, whose exit vectors are already in the congeneric series; a published E3 handle (VH032 on the *tert*-leucine nitrogen, or pomalidomide on the 4-amino nitrogen); and an L-amino-acid branch residue. That branch residue makes the pendant's stereocentre a defined **(S)** centre inherited from a catalogue building block rather than an unspecified one. **All 54 were verified with RDKit against the parsed molecule

#### 70 · original line 1969

**Before —** because a small residual can be two large closures cancelling: **R_ternary = −0.0312** essentially closes, the path dependence. Three limits travel with this number and none is incidental: it is **n = 1 by design**, **no error bar is quoted and none is constructed** from the per-leg MBAR SEs; at the σ_leg upper bound measured `UNDERPOWERED`, and that divergence is recorded rather than resolved; and closure bounds **internal

**After —** because a small residual can be two large closures cancelling. **R_ternary = −0.0312** essentially closes, the path dependence. Three limits travel with this number and none is incidental. First, it is **n = 1 by design**, **no error bar is quoted and none is constructed** from the per-leg MBAR SEs. Second, at the σ_leg upper bound measured `UNDERPOWERED`, and that divergence is recorded rather than resolved. Third, closure bounds **internal

#### 71 · original line 1999

**Before —** is built on. The substitution was nonetheless **not avoidable for this edge**: 8G1Q's deposition is SMARCA4, while each deposited SMARCA2 ternary carries a **different** ligand (Compound 11, PROTAC 1, PROTAC 2,

**After —** is built on. The substitution was nonetheless **not avoidable for this edge**. 8G1Q's deposition is SMARCA4. Each deposited SMARCA2 ternary carries a **different** ligand (Compound 11, PROTAC 1, PROTAC 2,

#### 72 · original line 2062

**Before —** campaign would actually depend on. The covalent arm was retired on measured evidence (the C6→Cys551 adduct admissibility limit — 0 of 3 pass, so it is unbuildable on every available input), and no covalent

**After —** campaign would actually depend on. The covalent arm was retired on measured evidence: the C6→Cys551 adduct admissibility limit, so 0 of 3 pass and it is unbuildable on every available input. No covalent

#### 73 · original line 2107

**Before —** the artifact or here; and the emitted tier is unchanged. E2 in particular is **not** leaned on: its motivating panel behind it had scored the Elongin C interface rather than VHL↔NR4A1 — the endpoint and its 4.0 Å

**After —** the artifact or here; and the emitted tier is unchanged. E2 in particular is **not** leaned on. Its motivating panel behind it had scored the Elongin C interface rather than VHL↔NR4A1. The endpoint and its 4.0 Å

#### 74 · original line 2123

**Before —** p-value at every count, because the scorer collapses a model's legs to their mean *before* the enumeration: the unit of independence is the co-fold model, so the reference set is sized by models and replicates cannot

**After —** p-value at every count, because the scorer collapses a model's legs to their mean *before* the enumeration. The unit of independence is the co-fold model, so the reference set is sized by models and replicates cannot

#### 75 · original line 2180

**Before —** readout is blunt" from "this pair is hard"**, and must not be reported as though it did — SMARCA2/SMARCA4

**After —** readout is blunt" from "this pair is hard"**, and must not be reported as though it did. SMARCA2/SMARCA4

#### 76 · original line 2187

**Before —** simulated complexes were the complexes whose selectivity was measured. They were not. Scored against the deposited ternaries the panel was designed around — 9DTY and 9DTX, chosen precisely so that *"each arm's co-fold can be validated against a real structure of the very complex it models"*, a comparison that was **never** run at the time — all twelve starting

**After —** simulated complexes were the complexes whose selectivity was measured. They were not. The panel was designed around the deposited ternaries 9DTY and 9DTX, chosen precisely so that *"each arm's co-fold can be validated against a real structure of the very complex it models"* — a comparison that was **never** run at the time. Scored against them, all twelve starting

#### 77 · original line 2215

**Before —** *And how wrong is 0.03?* Holding VHL fixed and displacing the **true** target chain of 9DTY by a rigid motion variable — gives DockQ **1.000 → 0.948 (0.5 Å) → 0.845 (1 Å) → 0.717 (2 Å) → 0.401 (4 Å) → 0.240 (8 Å) →

**After —** *And how wrong is 0.03?* We held VHL fixed and displaced the **true** target chain of 9DTY by a rigid motion variable. That gives DockQ **1.000 → 0.948 (0.5 Å) → 0.845 (1 Å) → 0.717 (2 Å) → 0.401 (4 Å) → 0.240 (8 Å) →

#### 78 · original line 2224

**Before —** ★ **AND THE COMPLEX ITSELF IS RECOVERABLE IN SILICO, WHICH LOCATES THE FAILURE PRECISELY.** Run on **9DTY** — deposited well after its 2023-10-14 data horizon — the same generator reaches **DockQ 0.839 (CAPRI "High"),

**After —** ★ **AND THE COMPLEX ITSELF IS RECOVERABLE IN SILICO, WHICH LOCATES THE FAILURE PRECISELY.** Consider **9DTY**, deposited well after its 2023-10-14 data horizon. Run on it, the same generator reaches **DockQ 0.839 (CAPRI "High"),

#### 79 · original line 2233

**Before —** each end of the degrader occupies**; what it predicts is the two proteins' **relative placement**, which is

**After —** each end of the degrader occupies**. What it predicts is the two proteins' **relative placement**, which is

#### 80 · original line 2243

**Before —** ★ **AND THE FAILURE IS LOCALISED: THE TWO HALVES ARE APPROXIMATELY RIGHT, THE ASSEMBLY IS NOT.** Superposing each co-fold on one protein at a time and measuring the degrader's deviation over the native atoms contacting *that* protein — correspondence through the reference molecule's own atom graph, never by proximity — all

**After —** ★ **AND THE FAILURE IS LOCALISED: THE TWO HALVES ARE APPROXIMATELY RIGHT, THE ASSEMBLY IS NOT.** We superposed each co-fold on one protein at a time and measured the degrader's deviation over the native atoms contacting *that* protein, with correspondence through the reference molecule's own atom graph, never by proximity. All

#### 81 · original line 2260

**Before —** the two crystals, at no cost, against an answer published before this program existed. Scoring the target↔VCB contact map of 9DTY and 9DTX and aligning the two bromodomains **by sequence** (they are numbered in their own full-length proteins, so equal numbers are different residues; interface-alignment identity 0.890), the descriptor finds exactly one position where a glutamine on the SMARCA2 arm makes a **side-chain**

**After —** the two crystals, at no cost, against an answer published before this program existed. We scored the target↔VCB contact map of 9DTY and 9DTX and aligned the two bromodomains **by sequence** — they are numbered in their own full-length proteins, so equal numbers are different residues (interface-alignment identity 0.890). The descriptor finds exactly one position where a glutamine on the SMARCA2 arm makes a **side-chain**

#### 82 · original line 2279

**Before —** positive control **for this program's selectivity claims** have now been run and none succeeded — a

**After —** positive control **for this program's selectivity claims** have now been run and none succeeded. That is a

#### 83 · original line 2308

**Before —** the static model. **Three honest limits of this scheme, which the manuscript does not overstate:** (i) the volume-overlap gate, so in a poorly-formed frame a spurious low-overlap cavity could be selected; (ii) the approximately uniform across sections; and (iii) **split/merge is not explicitly handled** and frames with **no** overlapping pocket are recorded as missing (`None`) and **excluded** — not scored zero — so every

**After —** the static model. **Three honest limits of this scheme, which the manuscript does not overstate.** (i) The volume-overlap gate, so in a poorly-formed frame a spurious low-overlap cavity could be selected. (ii) The approximately uniform across sections. (iii) **Split/merge is not explicitly handled**, and frames with **no** overlapping pocket are recorded as missing (`None`) and **excluded** rather than scored zero, so every

#### 84 · original line 2322

**Before —** using the fpocket score** — from a fixed, prespecified set of canonical NR ligand-pocket residues (mapped by structural alignment to homologous NR orthosteric sites) — then detect cavities, match to that region under a composite Jaccard + fraction-recovered + centroid gate (replacing the ≥1-residue rule), and read druggability only afterward, under one pinned fpocket build across the reference panel, AF2, all 20 8XTT conformers, the three metad replicas, and the three release replicas. **That rerun has been executed and is committed**

**After —** using the fpocket score**, from a fixed, prespecified set of canonical NR ligand-pocket residues mapped by structural alignment to homologous NR orthosteric sites. Cavities are then detected and matched to that region under a composite Jaccard + fraction-recovered + centroid gate (replacing the ≥1-residue rule), and druggability is read only afterward, under one pinned fpocket build across the reference panel, AF2, all 20 8XTT conformers, the three metad replicas, and the three release replicas. **That rerun has been executed and is committed**

#### 85 · original line 2348

**Before —** (confirmed_selective / reversed / weakened / rescued) vs the docking margins; magnitudes are inflated (no entropy/ensemble average) and read as direction, not affinity; selectivity FEP on the lead is the next

**After —** (confirmed_selective / reversed / weakened / rescued) vs the docking margins. Magnitudes are inflated (no entropy/ensemble average) and read as direction, not affinity. Selectivity FEP on the lead is the next

#### 86 · original line 2358

**Before —** convergence trace. We adopted this specifically for **spot-interruption robustness** — small per-window long spot runs to all-or-nothing checkpointing — and the engine was **evaluated on two benchmark systems**, with **opposite outcomes** ([`../modalities/nr4a3-abfe-calibration.json`](../../modalities/nr4a3-abfe-calibration.json)): a **hydration-free-energy** benchmark (methane ΔG_hyd = **+1.60 ± 0.04** kcal/mol vs experimental +2.0, FreeSolv — a **−0.40** kcal/mol offset; **approximately reproduced**, which supports the basic solvent-decoupling implementation on a simple neutral test system — it does *not* validate charge assignment, conformational sampling, or drug-like solvation for `denovo_401`) and a **protein–ligand binding** benchmark (T4-lysozyme L99A + benzene; below) that **fails by ≈ +7.1

**After —** convergence trace. We adopted this specifically for **spot-interruption robustness**: small per-window long spot runs to all-or-nothing checkpointing. The engine was **evaluated on two benchmark systems**, with **opposite outcomes** ([`../modalities/nr4a3-abfe-calibration.json`](../../modalities/nr4a3-abfe-calibration.json)). A **hydration-free-energy** benchmark (methane ΔG_hyd = **+1.60 ± 0.04** kcal/mol vs experimental +2.0, FreeSolv — a **−0.40** kcal/mol offset) is **approximately reproduced**, which supports the basic solvent-decoupling implementation on a simple neutral test system; it does *not* validate charge assignment, conformational sampling, or drug-like solvation for `denovo_401`. A **protein–ligand binding** benchmark (T4-lysozyme L99A + benzene; below) **fails by ≈ +7.1

#### 87 · original line 2373

**Before —** per-receptor ΔG_bind, the two ΔΔG contrasts, the unanimous direction, and the provisional-NR4A2 caveat). **Full FEP diagnostics are in SI §S7** (per-replicate paired ΔΔG table, λ-overlap matrices, effective sample sizes, forward/reverse convergence traces). **Artifact pointer (read this carefully — the path is version-pinned).** The diagnostics JSON for the three-replicate AF2-conditioned run is `results/nr4a3-abfe/diagnostics/nr4a3-abfe-diagnostics.json` **as committed at git `b4b8e217`** (tags `nr4a3-abfe`, `-r2`, `-r3`; 12 λ-windows × 2000 samples per leg); the file **at that same path in the current working tree has since been overwritten** by a later, unrelated λ-repair pilot scoped to the `nr4a3-abfe-nr4a2rep-*` tags, which contains only partial complex legs, no solvent legs and no ΔG_bind, and therefore does **not** support any number in this paper. The overlap/ESS/convergence PNGs for the three original replicates (`*_nr4a3-abfe.png`, `*-r2.png`, `*-r3.png`) were not overwritten and remain in the tree. Against the `b4b8e217` JSON the reduction is reproducible: it recomputes these ΔG_bind from the raw reduced potentials with a maximum absolute deviation of **0.022 kcal/mol** across all ten checked means and SDs (its own `manuscript_consistency` block records `consistent: true`), which is the basis for the ≤0.03 kcal/mol statement. On overlap, the honest picture is **not** a single localized exception: median adjacent overlap per leg is ≈0.13–0.22, but **every leg — including the shared solvent leg and all three NR4A3 complex legs — has at least one soft-core-tail window pair below 0.03**, with per-leg minima spanning **0.003–0.027** (worst: complex-NR4A2 in r3, 0.0034). The defect is therefore **systematic across the λ-schedule's decoupling tail, not NR4A2-specific**, so the same λ-repair caveat applies to *all* absolutes and to *both* ΔΔG contrasts; NR4A2 is singled out in §2.8 only because it is the worst case and because a receptor-specific complex-leg error does not cancel in ΔΔG(3−2). We do not report calibrated absolute ΔG_bind. The engine mis-predicts a rigid textbook benchmark

**After —** per-receptor ΔG_bind, the two ΔΔG contrasts, the unanimous direction, and the provisional-NR4A2 caveat). **Full FEP diagnostics are in SI §S7** (per-replicate paired ΔΔG table, λ-overlap matrices, effective sample sizes, forward/reverse convergence traces). **Artifact pointer (read this carefully — the path is version-pinned).** The diagnostics JSON for the three-replicate AF2-conditioned run is `results/nr4a3-abfe/diagnostics/nr4a3-abfe-diagnostics.json` **as committed at git `b4b8e217`** (tags `nr4a3-abfe`, `-r2`, `-r3`; 12 λ-windows × 2000 samples per leg). The file **at that same path in the current working tree has since been overwritten** by a later, unrelated λ-repair pilot scoped to the `nr4a3-abfe-nr4a2rep-*` tags. That file contains only partial complex legs, no solvent legs and no ΔG_bind, and therefore does **not** support any number in this paper. The overlap/ESS/convergence PNGs for the three original replicates (`*_nr4a3-abfe.png`, `*-r2.png`, `*-r3.png`) were not overwritten and remain in the tree. Against the `b4b8e217` JSON the reduction is reproducible: it recomputes these ΔG_bind from the raw reduced potentials with a maximum absolute deviation of **0.022 kcal/mol** across all ten checked means and SDs (its own `manuscript_consistency` block records `consistent: true`), which is the basis for the ≤0.03 kcal/mol statement. On overlap, the honest picture is **not** a single localized exception: median adjacent overlap per leg is ≈0.13–0.22, but **every leg — including the shared solvent leg and all three NR4A3 complex legs — has at least one soft-core-tail window pair below 0.03**, with per-leg minima spanning **0.003–0.027** (worst: complex-NR4A2 in r3, 0.0034). The defect is therefore **systematic across the λ-schedule's decoupling tail, not NR4A2-specific**, so the same λ-repair caveat applies to *all* absolutes and to *both* ΔΔG contrasts; NR4A2 is singled out in §2.8 only because it is the worst case and because a receptor-specific complex-leg error does not cancel in ΔΔG(3−2). We do not report calibrated absolute ΔG_bind. The engine mis-predicts a rigid textbook benchmark

#### 88 · original line 2394

**Before —** identical, the contrast is, algebraically, ΔΔG(3−1) = −ΔG_cplx,3 + ΔG_cplx,1 − SSC₃ + SSC₁ (the shared ΔG_solv drops out), so a per-engine bias cancels **only to the extent it is common across the receptors' complex legs and standard-state corrections** — which system-dependent complex-leg error is not guaranteed to

**After —** identical, the contrast is, algebraically, ΔΔG(3−1) = −ΔG_cplx,3 + ΔG_cplx,1 − SSC₃ + SSC₁, with the shared ΔG_solv dropping out. A per-engine bias therefore cancels **only to the extent it is common across the receptors' complex legs and standard-state corrections**, which system-dependent complex-leg error is not guaranteed to

#### 89 · original line 2417

**Before —** (ABFE) scale above, the same OpenMM/OpenFE infrastructure's **relative binding FEP** path — tool any relative warhead campaign would rely on — was validated end-to-end against a **public known-answer edge**: the TYK2 congeneric pair `ejm_31→ejm_42` from the OpenFE protein–ligand benchmark, at full sampling published accuracy for this protocol. This is a **build-consistency check on the relative-FEP path** (it does not touch NR4A and makes no NR4A3 claim), but it establishes two operationally relied-upon facts: our container *absolute* scale above — and the **spot-safe GCS checkpoint/resume infrastructure** carries a multi-hour FEP check, and its timings do not transfer: on the real cmpd19/NR4A3 congeneric complex, three independent RTX-4090 same card class** — the NR4A3 hybrid is ~2.6× more expensive per unit of sampling. Effective protocol settings,

**After —** (ABFE) scale above, the same OpenMM/OpenFE infrastructure's **relative binding FEP** path was validated end-to-end against a **public known-answer edge**. That path is tool any relative warhead campaign would rely on. The edge is the TYK2 congeneric pair `ejm_31→ejm_42` from the OpenFE protein–ligand benchmark, at full sampling published accuracy for this protocol. This is a **build-consistency check on the relative-FEP path**: it does not touch NR4A and makes no NR4A3 claim. But it establishes two operationally relied-upon facts. Our container *absolute* scale above. And the **spot-safe GCS checkpoint/resume infrastructure** carries a multi-hour FEP check, and its timings do not transfer. On the real cmpd19/NR4A3 congeneric complex, three independent RTX-4090 same card class**. The NR4A3 hybrid is ~2.6× more expensive per unit of sampling. Effective protocol settings,

#### 90 · original line 2463

**Before —** partly recovered here: because the ligand is identical across all three experiments, the solvent-decoupling ligand-charge/protonation error, so the *selectivity* ΔΔG **eliminates the shared solvent leg and may reduce truly common errors** (a general numerical claim of "better-behaved" would need a relevant selectivity benchmark). A confirmatory alchemical-mutation cross-check is **no longer blocked on tooling**: an alchemical 2026-07-25, **passed a known-answer benchmark** on the barnase–barstar interface at 3 × 3 replication — **Y29A +4.42 ± 1.08** against a SKEMPI-verified +3.40 (abs err 1.02) and the near-null control **Y29F −0.37 ± 0.18** against −0.13 (abs err 0.24), both inside a ±1.5 kcal/mol tolerance and correctly ordered.

**After —** partly recovered here. Because the ligand is identical across all three experiments, the solvent-decoupling ligand-charge/protonation error. So the *selectivity* ΔΔG **eliminates the shared solvent leg and may reduce truly common errors**; a general numerical claim of "better-behaved" would need a relevant selectivity benchmark. A confirmatory alchemical-mutation cross-check is **no longer blocked on tooling**. An alchemical 2026-07-25, **passed a known-answer benchmark** on the barnase–barstar interface at 3 × 3 replication. **Y29A** gave **+4.42 ± 1.08** against a SKEMPI-verified +3.40 (abs err 1.02), and the near-null control **Y29F** gave **−0.37 ± 0.18** against −0.13 (abs err 0.24) — both inside a ±1.5 kcal/mol tolerance and correctly ordered.

#### 91 · original line 2485

**Before —** never trimmed) — motivated by the structural-sanity control (§2.3: fold intact, core RMSD 1.76 Å) and standard separately evaluated**; this also keeps the explicit-solvent box within a (P411/R481/R485), weighting the both-paralogue handles in the selective campaign; DiffSBDD pocket-conditioned diffusion (pretrained CrossDocked weights; `nr4a3_denovo.py` + `entry_denovo.py`) conditioned on the + pose-handle-contact triage (`denovo_funnel.py`); generated candidates are funneled through the same matrix dock + MM-GBSA pipeline

**After —** never trimmed). The trim is motivated by the structural-sanity control (§2.3: fold intact, core RMSD 1.76 Å) and is standard separately evaluated**. It also keeps the explicit-solvent box within a (P411/R481/R485), weighting the both-paralogue handles in the selective campaign. DiffSBDD pocket-conditioned diffusion (pretrained CrossDocked weights; `nr4a3_denovo.py` + `entry_denovo.py`) is conditioned on the + pose-handle-contact triage (`denovo_funnel.py`). Generated candidates are funneled through the same matrix dock + MM-GBSA pipeline

#### 92 · original line 2509

**Before —** CRL arm with every removed chain recorded; burial by [71], cavity volume by a LIGSITE protein–solvent–protein scan [72], and an exit vector taken as the **solid-angle centroid of the near-maximal rays** from the

**After —** CRL arm with every removed chain recorded; burial by [71]; and cavity volume by a LIGSITE protein–solvent–protein scan [72]. The exit vector is taken as the **solid-angle centroid of the near-maximal rays** from the

#### 93 · original line 2516

**Before —** artifact of three separate searches; every paralogue lysine carries its own post-fit deviation and a cysteine and spanning to the E3 compete for the *same* budget; accessibility uses a worm-like-chain fingerprint** the scored terms depend on, rather than on the RMSD between placements' reference points: at an

**After —** artifact of three separate searches. Every paralogue lysine carries its own post-fit deviation and a cysteine and spanning to the E3 compete for the *same* budget. Accessibility uses a worm-like-chain fingerprint** the scored terms depend on, rather than on the RMSD between placements' reference points. At an

#### 94 · original line 2541

**Before —** assumption.** Three attempts have been run and none succeeded — the ternary cooperativity calibrator returned the **wrong sign** systematically (§2.11), the preregistered NR-V04 retrospective returned a **non-resolution** and is covalency-confounded so it could never have served at any *n* (§2.12), and the sensitivity control reading is the tempting one: it does **not** distinguish an insensitive readout from a genuinely narrow structural signal, and it does **not** retroactively invalidate any individual ΔΔG — it removes the evidence

**After —** assumption.** Three attempts have been run and none succeeded. The ternary cooperativity calibrator returned the **wrong sign** systematically (§2.11). The preregistered NR-V04 retrospective returned a **non-resolution** and is covalency-confounded, so it could never have served at any *n* (§2.12). And the sensitivity control reading is the tempting one. It does **not** distinguish an insensitive readout from a genuinely narrow structural signal. And it does **not** retroactively invalidate any individual ΔΔG: it removes the evidence

#### 95 · original line 2558

**Before —** since been run (§2.12a): the same DockQ build returns **0.618, CAPRI "Medium"** for a dedicated ternary generator on a known complex, so the near-zero score is not an artefact of the scorer; and displacing the

**After —** since been run (§2.12a). The same DockQ build returns **0.618, CAPRI "Medium"** for a dedicated ternary generator on a known complex, so the near-zero score is not an artefact of the scorer. And displacing the

#### 96 · original line 2568

**Before —** validated against a published known answer (§2.12a) and applied to this work's own NR4A1/2/3 ternaries; it yields **no justified selectivity claim** — the single sequence-encoded candidate rests on one model per

**After —** validated against a published known answer (§2.12a) and applied to this work's own NR4A1/2/3 ternaries. It yields **no justified selectivity claim**: the single sequence-encoded candidate rests on one model per

#### 97 · original line 2576

**Before —** demonstrated efficacy**. Therapeutic application to EMC (and AciCC) additionally **assumes NR4A3 dependence, which is not tested here**: the supporting prior (a transfer prior from fusion-addicted EWSR1/FET sarcomas; EMC-native evidence the fusion is a functional driver; a near-invariant clonal fusion in a quiet genome) and the **one decisive gap** (no loss-of-function experiment in any EMC model — the make-or-break dTAG test is delegated to the EMC-program paper), together with the systemic-lead safety/tolerability rationale and the pan-NR4A/CAR-T pole, are in **SI §S9** (safety in **SI §S6**, indications in **SI §S4**). This paper's claimed contribution is the target's **computational druggability/selectivity, not EMC efficacy**. is done (§2.1) and is two-sided:** the experimental apo ensemble is structurally *heterogeneous* at the mapped site (most conformers occluded; under the harmonized tracker the site is matched in 19/20 conformers, of which **3 exceed D\*** — 3/19 among detected, 3/20 across all deposited; structural corroboration, not a population estimate), **but** the AF2 atomic pocket geometry *diverges* from it (pocket-local Cα-RMSD 3.56 Å, handle 3.44 Å). Two **A full workflow rebase and the review-warranted controls remain to do**: (i) an 8XTT-*started* metadynamics/MD and generation (not yet done here), and an **8XTT-anchored ABFE** — of which the **NR4A3 leg AF2/opened-conformer-conditional; (ii) a **matched 8XTT-frame decoy null** (denovo_401 + the 38 decoys through the same 4 conformers, since we have shown MM-GBSA margins are frame-dependent); (iii) vs NMR↔NMR RMSD decomposition and a true residue-contact-graph spatial-patch null; (iv) **repair of the under-overlapped ABFE windows** — note this is *not* a single window: every leg (solvent and all three

**After —** demonstrated efficacy**. Therapeutic application to EMC (and AciCC) additionally **assumes NR4A3 dependence, which is not tested here**. Two things bear on that assumption: the supporting prior (a transfer prior from fusion-addicted EWSR1/FET sarcomas; EMC-native evidence the fusion is a functional driver; a near-invariant clonal fusion in a quiet genome) and the **one decisive gap** (no loss-of-function experiment in any EMC model — the make-or-break dTAG test is delegated to the EMC-program paper). Both, together with the systemic-lead safety/tolerability rationale and the pan-NR4A/CAR-T pole, are in **SI §S9** (safety in **SI §S6**, indications in **SI §S4**). This paper's claimed contribution is the target's **computational druggability/selectivity, not EMC efficacy**. is done (§2.1) and is two-sided.** The experimental apo ensemble is structurally *heterogeneous* at the mapped site: most conformers are occluded, and under the harmonized tracker the site is matched in 19/20 conformers, of which **3 exceed D\*** — 3/19 among detected, 3/20 across all deposited. That is structural corroboration, not a population estimate. **But** the AF2 atomic pocket geometry *diverges* from it (pocket-local Cα-RMSD 3.56 Å, handle 3.44 Å). Two **A full workflow rebase and the review-warranted controls remain to do.** (i) An 8XTT-*started* metadynamics/MD and generation (not yet done here), and an **8XTT-anchored ABFE**. Of the latter the **NR4A3 leg AF2/opened-conformer-conditional. (ii) A **matched 8XTT-frame decoy null** (denovo_401 + the 38 decoys through the same 4 conformers, since we have shown MM-GBSA margins are frame-dependent). (iii) vs NMR↔NMR RMSD decomposition and a true residue-contact-graph spatial-patch null. (iv) **Repair of the under-overlapped ABFE windows** — and note this is *not* a single window. Every leg (solvent and all three

#### 98 · original line 2608

**Before —** But (a) 0.931 is the **maximum over 600 frames** — report it as a distribution (fraction of frames ≥ D\*=0.53, met) with 0.931 as the peak; and (b) it is computed on **biased-MD** conformations, so its

**After —** But (a) 0.931 is the **maximum over 600 frames**, so we report it as a distribution (fraction of frames ≥ D\*=0.53, met) with 0.931 as the peak. And (b) it is computed on **biased-MD** conformations, so its

#### 99 · original line 2615

**Before —** 2. **No separate opened free-energy basin.** The original production profile is monotonic (a single resolved minimum, rising wall) and independent replicas likewise **do not resolve a reproducible second minimum**, but their 1-D profiles and minimum locations **differ substantially** (the minimum is not structurally classified as "closed"); the

**After —** 2. **No separate opened free-energy basin.** The original production profile is monotonic (a single resolved minimum, rising wall), and independent replicas likewise **do not resolve a reproducible second minimum**. But their 1-D profiles and minimum locations **differ substantially**, and the minimum is not structurally classified as "closed". The

#### 100 · original line 2622

**Before —** ~0.6–0.76 kcal/mol interpretation is **not supported by the independent profiles**: at the fixed reference

**After —** ~0.6–0.76 kcal/mol interpretation is **not supported by the independent profiles**. At the fixed reference

#### 101 · original line 2628

**Before —** 75/75 frames, so detected-frame and all-frame denominators coincide) — correlated,

**After —** 75/75 frames, so detected-frame and all-frame denominators coincide). Those are correlated,

#### 102 · original line 2644

**Before —** kinetics) whose factors **compound**, so the binder need not carry it *alone* — but a selective binder is still strictly valuable and is the primary goal (`denovo_401` is a decoy-null-screened foothold, not fully control-validated (the decoy null does not control the generative step); the second candidate denovo_111 was withdrawn as protonation-fragile — §2.7). The

**After —** kinetics) whose factors **compound**, so the binder need not carry it *alone*. But a selective binder is still strictly valuable and is the primary goal. (`denovo_401` is a decoy-null-screened foothold, not fully control-validated, because the decoy null does not control the generative step; the second candidate denovo_111 was withdrawn as protonation-fragile — §2.7.) The

#### 103 · original line 2661

**Before —** stage that actually interrogates it: paralogue discrimination is searched first on **categorical** handles (a nucleophile and lysines the paralogues do not possess), because the induced-interface margin the co-fold

**After —** stage that actually interrogates it. Paralogue discrimination is searched first on **categorical** handles — a nucleophile and lysines the paralogues do not possess — because the induced-interface margin the co-fold

#### 104 · original line 2681

**Before —** atom typing reproduces none of them — so no singular "predicted pose" is claimed anywhere in this paper.

**After —** atom typing reproduces none of them. So no singular "predicted pose" is claimed anywhere in this paper.

#### 105 · original line 2698

**Before —** resolve this (§2.7): (a) the **multi-snapshot decoy null** (all 38 decoys re-scored multi-snapshot: 95th pct +6.69, max +7.10) — `denovo_401` (+12.83 ± 2.98, margin − SD +9.85) **clears it**, so the margin is above a decoy null recomputed at the same tier, not merely de-noised — **but that null

**After —** resolve this (§2.7). (a) The **multi-snapshot decoy null** re-scores all 38 decoys multi-snapshot (95th pct +6.69, max +7.10), and `denovo_401` (+12.83 ± 2.98, margin − SD +9.85) **clears it**, so the margin is above a decoy null recomputed at the same tier, not merely de-noised. **But that null

#### 106 · original line 2706

**Before —** — has run one of its three arms (scrambled objective, isolating the best-of-N selection step): it against the real campaign's own 0.0052, so it **narrows the confound without excluding it**, and the paralogue-pocket generation arm that would speak to the generative step directly is **not run** (§2.7); and (b) a **fully metad-frame decoy null was then run (§2.7) and, honestly, `denovo_401` does *not* clear it**: in the biased +24.74) and +7.44 sits at only ~the 84th percentile — so the metad-opened frame is a poor discriminator, but it is also the frame `denovo_401` was *not* generatively fit to, so the above-null result is **single-trajectory GB-implicit MD, not ABFE**, so **selectivity ABFE is the quantitative gate — initial three-replicate ABFE complete (three-replicate ΔΔG NR4A3-favoured; NR4A2-sparing resolved below zero, **deliberately held rather than queued** — it is parked, not in flight, and repairing error bars would not

**After —** — has run one of its three arms, the scrambled objective, isolating the best-of-N selection step. It against the real campaign's own 0.0052, so it **narrows the confound without excluding it**. The paralogue-pocket generation arm that would speak to the generative step directly is **not run** (§2.7). And (b) a **fully metad-frame decoy null was then run (§2.7) and, honestly, `denovo_401` does *not* clear it.** In the biased +24.74) and +7.44 sits at only ~the 84th percentile. So the metad-opened frame is a poor discriminator, but it is also the frame `denovo_401` was *not* generatively fit to, and the above-null result is therefore **single-trajectory GB-implicit MD, not ABFE**, so **selectivity ABFE is the quantitative gate.** The **initial three-replicate ABFE is complete** (three-replicate ΔΔG NR4A3-favoured; NR4A2-sparing resolved below zero, **deliberately held rather than queued**. **It is parked, not in flight, and repairing error bars would not

#### 107 · original line 2729

**Before —** conformer, so there is **no geometric fallback** — and the untested failure modes for C397 are **chemical,

**After —** conformer, so there is **no geometric fallback**. The untested failure modes for C397 are **chemical,

#### 108 · original line 2758

**Before —** are never accuracy evidence** — not as a matter of degree but by an identity: a closed cycle is

**After —** are never accuracy evidence** — not as a matter of degree but by an identity. A closed cycle is

#### 109 · original line 2767

**Before —** the quantitative tier is now **MM-GBSA-run** rather than planned — but single-snapshot MM-GBSA has **no trusted; **selectivity FEP** (the defensible affinity tier) is **now run** (independent-window ABFE;

**After —** the quantitative tier is now **MM-GBSA-run** rather than planned. But single-snapshot MM-GBSA has **no trusted. **Selectivity FEP** (the defensible affinity tier) is **now run** (independent-window ABFE;

#### 110 · original line 2798

**Before —** supported by **initial conditional ABFE receptor contrasts** but not experimentally validated. Two riders on those contrasts, at their current status: the NR4A3 structural-model sensitivity test **has been run** (the follow-up; and the dense-schedule λ-repair that would firm up the error bars is **held**, so every ABFE number

**After —** supported by **initial conditional ABFE receptor contrasts** but not experimentally validated. Two riders travel with those contrasts, at their current status. The NR4A3 structural-model sensitivity test **has been run** (the follow-up. And the dense-schedule λ-repair that would firm up the error bars is **held**, so every ABFE number

#### 111 · original line 2813

**Before —** that file's deviation log: (i) the **Gate 0** metric (max → orthosteric/ligand-site, D\*=0.53 — a *real* drug-bound bar, not a laxer one); and (ii) **Gate 1**, which asked for a free-energy *minimum or shoulder* at an opened Rg "not just biased excursions" — F(Rg) is instead monotonic, so Gate 1 is reported as hypothesis the release run then tested; and (iii) **Gate 3 is split** into two subclaims that no single run

**After —** that file's deviation log. (i) The **Gate 0** metric changed (max → orthosteric/ligand-site, D\*=0.53 — a *real* drug-bound bar, not a laxer one). (ii) **Gate 1** asked for a free-energy *minimum or shoulder* at an opened Rg "not just biased excursions", and F(Rg) is instead monotonic, so Gate 1 is reported as hypothesis the release run then tested. (iii) **Gate 3 is split** into two subclaims that no single run

#### 112 · original line 2830

**Before —** We explicitly do **not** claim "Gates pass" as unqualified: Gate 1 **failed** as pre-registered, Gate 2's only at pre-harmonized weight, and the frame-level generation-receptor dependency audit has now **CLOSED and FAILED** — the exact frame `denovo_401` was generated into does **not** clear D\* under the harmonized definition (§3),

**After —** We explicitly do **not** claim "Gates pass" as unqualified. Gate 1 **failed** as pre-registered. Gate 2's only at pre-harmonized weight. The frame-level generation-receptor dependency audit has now **CLOSED and FAILED** — the exact frame `denovo_401` was generated into does **not** clear D\* under the harmonized definition (§3).

#### 113 · original line 2909

**Before —** NR4A3 a *gain* rather than imposing a paralogue *penalty* (the aligned paralogue residues are hydrocarbon and simply cannot donate), and that a NO-GO may be acted on at this evidence grade because stopping is the

**After —** NR4A3 a *gain* rather than imposing a paralogue *penalty*, because the aligned paralogue residues are hydrocarbon and simply cannot donate. A NO-GO may be acted on at this evidence grade because stopping is the

#### 114 · original line 2934

**Before —** pocket (4/5 handles), stays NR4A3-favoured through multi-snapshot MM-GBSA where the single-snapshot harvest collapses, clears a same-tier decoy null in its design frame, is **supported by initial conditional it short of an unqualified pass: the decoy null controls the *scoring* step only, and the generation-matched confound, and missing the paralogue-pocket arm entirely (§2.7); the **positive margin persists in the metad-opened frame but the candidate does not clear the corresponding metad-frame decoy null** (itself a poor discriminator); and the ABFE is a

**After —** pocket (4/5 handles) and stays NR4A3-favoured through multi-snapshot MM-GBSA where the single-snapshot harvest collapses. It clears a same-tier decoy null in its design frame, is **supported by initial conditional it short of an unqualified pass. First, the decoy null controls the *scoring* step only, and the generation-matched confound, and missing the paralogue-pocket arm entirely (§2.7). Second, the **positive margin persists in the metad-opened frame but the candidate does not clear the corresponding metad-frame decoy null** (itself a poor discriminator). Third, the ABFE is a

