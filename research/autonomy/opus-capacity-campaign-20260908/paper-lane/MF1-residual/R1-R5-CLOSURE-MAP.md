---
id: DOC-MF1-RESIDUAL-R1-R5-CLOSURE-MAP
title: "MF1 residual — R1–R5 closure map"
level: L4
kind: memo
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# R1–R5 closure map — MF1 finite residual batch, 2026-09-08

One row per residual: what it was, the exact edit, the file and anchor, what was **removed** versus
**attributed** versus **scoped**, and what remains open. ⛔ **F08–F11 were not redone. P1–P6 were not
reapplied.** ⛔ **No new measurement, source acquisition, simulation, chronology audit, review or
biological producer.**

---

## R1 — the supplement's current claim scope, and the source-to-display propagation

| | |
|---|---|
| **The residual** | The generated supplement republished three claims the main text withdraws, as its **final reader-facing claim-scope column**: `SI:61` (V5) *closure localises the miss to endpoint-state error and more sampling will not fix it*; `SI:72` (V16) *S may be read as a bound; S ≈ 0 means the marginal wedge is absent*; `SI:77` (V20) *no downstream method can recover a signal below its noise*. The cause was structural: the extraction copies `instrument-census.json.scope_limit` verbatim into that column, and the census is generated from the roadmap. The filed patch instruction claimed the extraction needed no regeneration "because it does not read the roadmap". |
| **The exact edit** | (1) A new **author-current claim-scope axis** (`CURRENT_SCOPE`) for `V5`, `V11`, `V16`, `V20` in `extract_mf1_inventory.py`, rendered as the operative column; the census string is retained verbatim in a new, explicitly labelled **superseded historical annotation** column. (2) Two new columns exposing the census `known_answer_test` and `result` per row. (3) A **source / governing correction** column naming `instruments[id=…]` and the dated corrective interpretation. (4) The manuscript states the chain **roadmap → census → extraction → inventory/SI** and withdraws the false no-regeneration instruction. (5) The §2 divergence note is updated: P1/P2 **are applied** at `a6a21fc5…`; four cells remain and are named. (6) An exact **unapplied** patch for the four shared cells. |
| **File and anchor** | `MF1-repair/extract_mf1_inventory.py` §2b `CURRENT_SCOPE`, `GOVERNING_NOTE`, `inventory_rows`, `write_inventory`, `SI_HEADER`, `SI_FOOTER` items 5–7 · regenerated `degrader-methods-failure-record-SI.md` S2 · main §2 *The disclosed divergence*, §3 *The display chain* and *Supersession is dated*, §11 registers bullet · `patches/0001-roadmap-four-live-residues.patch` (Q1, Q3, Q4, Q5, Q6) · `DATED-SUPERSESSIONS-…md` S1 |
| **REMOVED** | The three withdrawn claims as the SI's operative claim limits. The false "MF1 extraction needs no regeneration" instruction (superseded beside the original, whose bytes are unchanged). The stale §2 statement that `PUB-METHODS` still carries the superseded formulation. |
| **ATTRIBUTED** | The retained census wording is kept **verbatim**, relabelled as a superseded historical annotation with the date of supersession and the governing corrective interpretation. |
| **SCOPED** | Supersession is dated **at the current rows a reader actually reaches**. ⛔ No wholesale rewrite of the historical roadmap was performed or proposed. |
| **OPEN** | The four shared cells — census `V16.scope_limit`, census `V20.scope_limit`, census `V11.result`, roadmap `:3246` — are **still wrong in the shared tree**; the patch is prepared, verified with `git apply --check` (exit 0) and **not applied**, because those files are parent-owned. The **one admitted instrument-census update was not spent**: `instrument_census.py --check` returned exit 0, so the census is in sync with the *unpatched* roadmap and a regeneration now would change nothing. Sequencing is in `patches/README.md`. |

---

## R2 — unproved pre-outcome chronology, and literal shared structural inputs

| | |
|---|---|
| **The residual** | The paper asserted as **fact** that gates were frozen before their own runs (`M:146–152`), that `S`'s outcome and expected magnitude were registered **in advance** (`M:374`, `M:385–386`), and that the consequence sentence was written **before the deciding run** (`M:402–403`, `M:757–766`) — while conceding it cannot present the records needed to check it. Separately it claimed the alchemical lane *"shares this program's structural inputs, co-folding route"*. |
| **The exact edit** | Every affirmative chronology claim replaced with *the retained protocol **describes** this rule / outcome / consequence as prespecified*, and *the actual chronology is **unestablished***. The shared-dependency sentence narrowed to *shared programme assumptions, selection decisions and code base*, with the actual input difference named: **valB resolves its chains from RCSB `8G1Q`; the NR-V04 assemblies come from a different co-fold source** whose Elongin B sequence was fetched from a module constant. New dated corrective interpretation **C13**. Shared roadmap V16 `result` cell handled by patch **Q2** and the `:986` reading row by **Q6**. |
| **File and anchor** | main §3 *Retrospective, not prospective* · §6 spine table row 4 · §6.1 · §6.2 · §6.2's consequence sentence · §9.6 both paragraphs · §10.5 item 6 · `corrective-interpretations-2026-09-08.md` **C13** · patch Q2, Q6 |
| **REMOVED** | *"were frozen before their own runs"*, *"registered **in advance**"* (as fact), *"**before** the deciding run"* (as fact), *"shares this program's structural inputs, co-folding route"*. |
| **ATTRIBUTED** | All four to the retained protocol's own description. The dated historical protocol text is unchanged. |
| **SCOPED** | The reading of `S` and the program's stop decision are stated as **not depending** on the chronology. Reopening is limited to **already retained** pre-outcome rule versions, amendments and outcome-access bindings. |
| **OPEN** | ⛔ **No chronology investigation was run and none is proposed.** The census `V16.result` field still contains *"registered in advance"* — it is a **shared** cell, quoted in the SI under a column explicitly headed *result as recorded (census)*, and patch Q2 corrects it at source. |

---

## R3 — the retained grading facts, the exclusion stages, and the generation/provenance overstatement

| | |
|---|---|
| **The residual** | The displays reported benchmark **grades** without the identities, references, results or criteria the frozen census already held; the E1 denominator omitted its excluded model; the main was described as generated and drift-proof; the manifest recorded working-tree bytes beside a `HEAD` blob id **without comparing them**; scope cells carried bare `:NNNN` locators from another document. |
| **The exact edit** | New **§4.2** in the main with the five benchmark rows, provenance to field and line, and uncertainty kinds marked **unknown** where unestablished. New **§4.1(a)** paragraph reporting the **24 → 2 → 22** stages and separating them from collector `rejected_records` and technical failures; the same split is now generated into the SI E1 row from `selectivity-sensitivity-control-prereg.md`, which was **added to the extraction's input registry** and is hashed into the manifest. The "cannot drift" claims replaced by a stated **generated-vs-authored boundary** and a **verifiable binding**: the manifest now records `head_blob_sha256` and `bytes_match_head_blob` per input. The inventory gained `known answer`, `result` and `source / governing correction` columns, plus a note that a bare `:NNNN` is a roadmap line range. `M:734`'s repository-wide absence rephrased. New corrective interpretation **C14**. |
| **File and anchor** | main §3 *Deterministic extraction, and its boundary*, §4 lead, §4.1(a), **§4.2**, §9.5, §10.5 items 7 and 10, §11 manifest paragraph · `extract_mf1_inventory.py` `head_blob_sha256()`, `INPUTS`, E1 `counts`, covalent `counts`, `inventory_rows`, `write_inventory`, `SI_HEADER`, `SI_FOOTER` 5–7, `main()` · `corrective-interpretations-…md` **C14** · `BENCHMARK-FACTS.md` |
| **REMOVED** | *"so it cannot drift"* / *"neither can drift"* (both the main's and the SI's). The main's description of its own §4 paragraphs as generated output. The `V5` register phrase *"~34× the statistical uncertainty"*. The repository-wide absence assertion at `M:734`. |
| **ATTRIBUTED** | The five benchmark rows to `instrument-census.json` by field and line, and through it to roadmap §3.1 — explicitly as **retained register values, not new verification**. The exclusion stages to the prereg's AMENDMENT 1. |
| **SCOPED** | Uncertainty kinds marked **UNKNOWN** where not established. The external-source absence scoped to *"not identified in the retained evidence used here"*. The `bytes_match_head_blob` field makes the binding checkable instead of assumed — measured **18 of 18 matching, 0 unbound**. |
| **OPEN** | The primary literature identifiers for the `V6`/`V7`/`V8`/`V10` benchmarks are still **not retrieved** and are not asserted (§11). ⚠ A transposition of reference and result in the commissioning memo and contract is recorded in `BENCHMARK-FACTS.md`; the manuscript follows the retained source. |

---

## R4 — the per-prefix result-object count

| | |
|---|---|
| **The residual** | `M:702` and `C:150–152` reported **17** final per-leg records for the **combined** two-prefix census. 17 is the first-prefix count. |
| **The exact edit** | *"17 under the original prefix and 1 under the chainfix prefix — 18 stored result objects across both — and zero multi-frame coordinate objects in either survey"*, with the source fields named, in the main and in **C7**; the SI row now generates the split rather than only the sum. Full erratum in `DENOMINATOR-ERRATUM.md`. |
| **File and anchor** | main §9.4 · `corrective-interpretations-…md` **C7** (dated erratum block, original wording quoted inside it) · SI S1 covalent row · `extract_mf1_inventory.py` covalent `counts` · `DENOMINATOR-ERRATUM.md` |
| **REMOVED** | The combined figure **17**. |
| **ATTRIBUTED** | ⛔ Named as **a reviewer erratum and a root erratum**, originating in the independent final review and carried into the adjudication before the author adopted it. The original mistaken baseline, the focused report and the root memo are left **immutable**. |
| **SCOPED** | **18 stored result objects, not 18 independent experiments** and not 18 intended panel legs; the conclusion stays scoped to the two surveyed prefixes. |
| **OPEN** | Nothing. ⛔ The absent-coordinate conclusion is unchanged and no trajectory was discovered. |

---

## R5 — the mechanism transfer across the ligand boundary

| | |
|---|---|
| **The residual** | `M:431–433` said *"the published selectivity turns on a single hydrogen bond"* about a panel whose reference is **PRT3789**, while `selcal_panel.py` identifies that statement as a mechanism citation about the **SMARCA2/SMARCA4 pair against VCB** and records that it is *"NOT a claim about the reference ligand."* |
| **The exact edit** | The sentence is withdrawn at the point of use and replaced by what the record supports: the result does not separate an insensitive E1 readout from an unsuitable or structurally narrow test, with input validity unresolved. The hydrogen-bond observation is attributed to its cited system and ligand context (Kofink *et al.* 2022, `doi:10.1038/s41467-022-33430-6`, PMC9551036) and its transfer to PRT3789 labelled an **unestablished mechanistic rationale**. New corrective interpretation **C15**, completing **C2** at the point of use. |
| **File and anchor** | main §6.3 binding 1 · `corrective-interpretations-…md` **C15** |
| **REMOVED** | The transferred mechanism claim. |
| **ATTRIBUTED** | To Kofink *et al.* 2022 and the SMARCA2BD/SMARCA4BD–VCB pair, quoting `selcal_panel.py`'s own `pair_mechanism_source.note`. |
| **SCOPED** | ⛔ No expected Ångström or structural magnitude inferred. ⛔ No source acquisition: the PRT3789 primary body is not open access and was not retrieved. |
| **OPEN** | Nothing within this batch's scope. |

---

## The four live residue rows, restated

| row | before | after |
|---|---|---|
| census **`V16.scope_limit`** (`:228`) / roadmap `:1778` | *"`S` may be read as a bound … `S ≈ 0` means the marginal wedge is absent"* | **shared file unchanged by this author.** ⭐ The SI now shows the **author-current** scope (`S` may NOT be read as a bound; `S ≈ 0` does NOT mean the wedge is absent) and demotes this string to a labelled superseded historical annotation. Patch **Q3** corrects the source. |
| census **`V20.scope_limit`** (`:301`) / roadmap `:1783` | *"A signal smaller than its own noise is not recoverable by any downstream method"* | same treatment; SI shows the positive-call-rate scope with the universal claim marked **withdrawn**. Patch **Q4** corrects the source. |
| census **`V11.result`** (`:156`) / roadmap `:1773` | *"p = 0.747 (NULL, adequately powered)"* | same treatment; SI's author-current scope states it is **NOT an adequately-powered null** and that the 1/462 floor is discreteness, not power. Patch **Q1** corrects the source. |
| roadmap **`:3246`** dependency row | *"returned a preregistered null **with a quantified bound**"* before its own withdrawal | **shared file unchanged.** Patch **Q5** removes the surviving clause and dates the withdrawal. The manuscript already carries the corrected reading (§4.1b) and names this cell as a known live divergence (§2). |
