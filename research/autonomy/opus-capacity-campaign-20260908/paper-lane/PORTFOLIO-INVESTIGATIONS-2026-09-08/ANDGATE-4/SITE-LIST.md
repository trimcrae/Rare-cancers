---
id: DOC-PORTFOLIO-INVESTIGATION-ANDGATE-4-SITE-LIST-2026-09-09
title: "ANDGATE-4 — exhaustive site list for the AND-gate in-trans selectivity-inversion claim"
level: L4
kind: investigation-evidence
status: live
date: 2026-09-09
lane: ANDGATE-4
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# Site list — every occurrence of the inversion claim and its numbers

**Search terms.** `invert` / `inversion` / `inverted`; `prefers wild-type` (single-line **and**
across a line break, via `perl -0777` — the single-line form MISSES the PUB-ANDGATE site, which
wraps mid-phrase); `0.70×` / `0.58×` / `0.70x` / `0.58x`; `0.696` / `0.578`; window-below-unity
paraphrases (`below 1`, `below unity`, `less than one`, `under 1`, `sub-unity`, `<1x`); `C_E`;
`in-trans` / `in trans` / `trans-competition`.

**Surfaces searched.** Whole repository excluding `.git` (checks/02), then each named target
individually (checks/03): the AND-gate manuscript, `systems/graph/*.json`, `systems/views/`,
`research/manuscripts/pinned-figures.json`, `research/manuscripts/program/emc-unexplored-treatment-lanes.md`,
`research/manuscripts/nr4a3-program-map.md`, and every lane directory under
`PORTFOLIO-INVESTIGATIONS-2026-09-08/`.

## (b) PRESENT AS A LIVE CLAIM — 2 sites, both inside this campaign's own lane artifacts

| # | File | Line(s) | Text | Note |
|---|------|---------|------|------|
| b1 | `…/PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-ANDGATE/FINDING.md` | **87–88** | "**1.00× (selectivity entirely gone) at C_E = 1 mM = EM**, and **inverted (0.70×, 0.58×) above EM** — where the molecule prefers / wild-type NR4A3 to the fusion." | §4 "The bounded step taken", item 3. The origin of the claim. **No superseded marker.** Corrected by the unapplied diff in this directory. |
| b2 | `…/PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-ANDGATE/fusion-andgate-trans-competition.json` | `trans_competition_sweep[11]`, `[12]` | `"C_E_uM": 3000.0, "window": 0.7` and `"C_E_uM": 10000.0, "window": 0.58` | The **data** the prose is read off. Correct output of the asymmetric model as written; wrong as a description of the design. Not silently rewritten — the diff at b1 annotates these rows as superseded-but-retained. Rewriting them requires re-running the parent lane's script, which is that lane's to do. |

## (c) PRESENT INSIDE AN EXPLICIT SUPERSEDED MARKER — 4 sites, all correct as they stand

| # | File | Line(s) | Context |
|---|------|---------|---------|
| c1 | `…/ANDGATE-3/FINDING.md` | 86 | Quoted verbatim inside §5 Result A, immediately followed by "become **1.064 and 1.008**" and "the inversion was the omitted term". Correctly marked. |
| c2 | `…/ANDGATE-3/FINDING.md` | 146 | §6: "PUB-ANDGATE's 'inverted / prefers wild-type' statement should not be carried forward by any later lane." A prohibition, not a claim. Correct. |
| c3 | `…/ANDGATE-3/andgate3_symmetric_trans_model.py` | 224–225 | String literal inside the `consequence` field: "…0.70x/0.58x) is an artifact of the omission." Correct. |
| c4 | `…/ANDGATE-3/andgate3-symmetric-trans-competition.json` | 133 | Same string, emitted. Correct. |

## (a) CORRECTLY ABSENT — every shared surface

| Surface | Evidence | Result |
|---|---|---|
| `research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md` | checks/03 T5 (exit 0) | **No inversion claim and no number below 1.** Its window values are 5.5× (base), ~11× (ceiling), 1.8× (strong-arm-1 collapse), 9.9–11.0× (linker-length sweep) — all > 1. §8.7 says only that the in-trans mode "is not modelled" and that the windows are "upper bounds with respect to it". The Erratum (l. 59–60) names the failure mode and sets `K_eff(cis) ≫ K_eff(trans)` without evaluating it. **The manuscript never made the claim; ANDGATE-3's §6 statement is confirmed.** |
| `systems/graph/*.json` | checks/03 T6 (exit 0) | No `C_E`, no trans-competition, no AND-gate window number. `MOD-ANDGATE` (`modalities.json:1687`) and `RT-ANDGATE` carry no selectivity figure. The `0.58` hits are an unrelated hyperthermia RH and a sequence-identity fraction. |
| `systems/views/` | checks/03 T6 (exit 0) | Generated views carry no AND-gate window number. `views/readiness.md:49` lists RT-ANDGATE's blocker as "arm-2 chemistry" only. |
| `research/manuscripts/pinned-figures.json` | checks/03 T7 (**exit 1**, no match) | **No AND-gate pin exists at all** — no `andgate`, `and-gate`, `avidity`, `coincidence` or `EWSR1-LC` key. Nothing to correct, and nothing pinned that the correction would move. |
| `research/manuscripts/nr4a3-program-map.md` | checks/03 T8 (exit 0) | Its `invert` occurrences are the covalent-mechanism, GPU-card-probe, Route-B and pmx items. None is the AND-gate window. |
| `research/manuscripts/program/emc-unexplored-treatment-lanes.md` | checks/03 T8 | One `Inverted` at l. 614, about PARP-1 repressing wild-type NOR1. Unrelated. |
| Every other lane directory (89 of them) | checks/03 T9 | No occurrence. ANDGATE-2 inherits the defective `f_fusion` **structurally** (its `place_literature_bound_on_cost_curve.py` imports the same asymmetry) but its committed numbers sit at `C_E` ≤ 5 µM, far below `EM`, where the asymmetric and symmetric curves differ by < 1% — so **ANDGATE-2 states no inversion and no value below 1**, and needs no correction. |

## Verdict

**The error did not propagate.** It is confined to the two PUB-ANDGATE artifacts that produced it,
plus four correctly-marked quotations of it inside ANDGATE-3's own refutation. No shared file — no
manuscript, no canonical graph object, no generated view, no pinned figure, no roadmap or program-map
row — carries the claim or a number derived from it. **No diff against a shared file is offered,
because none is warranted.**
