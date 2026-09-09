---
id: DOC-NEOANTIGEN-6-FINDING
title: "NEOANTIGEN-6 — the junction-neoantigen panel re-emitted under an explicit zero-partner filter: 174 → 146 peptides, 11 → 9 ranked binders, rank 1 and rank 3 removed, and a second removal class NEOANTIGEN-4 did not report"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# NEOANTIGEN-6 — 28 of 174 peptides and 2 of 11 ranked binders removed; the pre- and post-filter panels stand side by side

Lane `NEOANTIGEN-6` (the discovery proposal names this work `NEOANTIGEN-5`; that directory was
already taken by a completed task, so the lane is **6**). Executes **P5 / rank 5** of
`../FOLLOWTHROUGH-DISCOVERY/PROPOSALS.md`. Follows **NEOANTIGEN-3** (per-partner residue split for
the 11 ranked binders), **NEOANTIGEN-4** (8/174 and 2/11 zero-EWSR1; the `PARENTS` accession repair)
and **NEOANTIGEN-5** (the regression test for that repair).

Writes confined to this directory. Nothing added, committed or pushed; no preflight; no manuscript,
graph or shared script edited; no subagents; **no network** — routes B1/B2/B4/B8/B9 stay closed and
were not retried or proxied around; no GPU, no paid API, $0.

⛔ **A filtered prediction is still a prediction.** Nothing here is an immunogenicity, presentation,
tolerance, TCR-cross-reactivity, efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim, in either direction. This is a **screen-configuration** result.

## 1 · The question

> What does the ranked EWSR1::NR4A3 junction-neoantigen panel look like once peptides carrying zero
> residues from one parent are removed by an **explicit, reported** filter — with pre- and
> post-filter ranks retained side by side?

## 2 · Merit

Every claim that a ranked peptide is a *fusion* neoantigen rests on the peptide actually spanning the
fusion. A peptide that draws no residue from one parent is that parent's wild-type sequence plus the
one hybrid seam residue: it is not junction-specific, it cannot support an EMC-specific (public,
off-the-shelf) argument, and any future measurement on it could not be attributed to the fusion. The
screen's own top-ranked binder is in that class. Producing the re-filtered panel is what turns a
measured proportion into something a paper owner can act on, and doing it as a **separately reported**
filter — never a silent one — is what keeps the change auditable.

## 3 · The exact evidence gap this closes

NEOANTIGEN-4 §5.3 and §8.1 **measured** the proportion (8/174 peptides, 2/11 binders, including rank
1) and repaired the novelty guard's parent accession. It **never produced the re-emitted panel**, and
its zero-partner reading covered **one direction only** (zero-EWSR1). Both are closed here.

## 4 · The step taken

1. **Baseline, unmodified.** The existing repository tests for the audited script
   (`fusion_breakpoints.py`) run untouched: `test_fusion_breakpoint_panel_seam.py`,
   `test_junction_aso_seam.py`, `test_scope_rungs_free.py`, `test_junction_frameshift_peptides.py`
   → **79 passed, 0 skipped, 0 deselected** (`checks/01`, exit 0). NEOANTIGEN-4's 9 novelty tests
   were re-run green as well (`checks/02`, exit 0).
2. **`neoantigen6_zero_partner_refilter.py`** — recomputes the per-peptide parent split **from the
   committed panel itself** (each junction row's 21-residue `junction_context`, seam at window index
   10, peptide placement recovered by search and asserted unique), applies the discriminator, and
   re-emits the ranked panel with both ranks side by side (`refiltered-panel.json`).
3. **`UNAPPLIED-zero-partner-filter.diff`** — the same filter inside `fusion_breakpoints.py`, as an
   **unapplied** diff (the file is shared).
4. **`verify_patched_emit.py`** — drives the **patched** `emit_junction` over the real transcript
   model (`TRANSCRIPT_SOURCE=cache`, no network) on a symlink mirror, and requires the code path to
   reproduce the artifact's numbers exactly (`checks/10`, exit 0).

## 5 · Result — `refiltered-panel.json`

**The filter rule, stated once:** a candidate is retained only if it draws **≥ 1 residue from EWSR1
and ≥ 1 residue from NR4A3** at some junction that emits it. The hybrid seam residue counts for
neither parent. Retention is the permissive direction — a peptide is removed only when it is
zero-partner at **every** junction that emits it.

### 5.1 Peptide arm — 174 → 146

| class | n | share |
|---|---|---|
| retained (junction-specific) | **146** | 83.9 % |
| removed, **zero from EWSR1** | **8** | 4.6 % |
| removed, **zero from NR4A3** | **20** | 11.5 % |
| removed, zero from both | 0 | — |

The 8 are `{D,N}MPCVQAQ`, `{D,N}MPCVQAQY`, `{D,N}MPCVQAQYS`, `{D,N}MPCVQAQYSP` — exactly
NEOANTIGEN-4's set, reproduced independently here (`cross_check_against_NEOANTIGEN_4`: 174 rows
compared, **0 disagreements**).

**The 20 zero-NR4A3 peptides are new in this lane.** They are the symmetric class — a peptide
*ending* at the seam, every other residue EWSR1's — e.g. `AAVEWFDD`, `TAKAAVEWFDD`, `MPPPLRGD`,
`SQQSSSYGQQN`. NEOANTIGEN-4's own per-peptide table contains the evidence (`AAVEWFDD`:
`n_from_NR4A3 = 0`) but its zero-partner reading only ever inspected the EWSR1 side, so the class was
not counted. Applied symmetrically the discriminator removes **28 of 174 (16.1 %)**, not 8.

### 5.2 Ranked-binder arm — 11 → 9, with both ranks side by side

| pre-rank | peptide | allele | percentile | class | EWSR1 · seam · NR4A3 | verdict | post-rank |
|---|---|---|---|---|---|---|---|
| 1 | `DMPCVQAQY` | B\*35:01 | 1.2493 | weak | 0 · 1 · 8 | **REMOVED** (zero EWSR1) | — |
| 2 | `GDMPCVQAQY` | B\*44:02 | 0.9687 | weak | 1 · 1 · 8 | retained | **1** |
| 3 | `NMPCVQAQY` | B\*15:01 | 0.3736 | strong | 0 · 1 · 8 | **REMOVED** (zero EWSR1) | — |
| 4 | `RGDMPCVQAQY` | A\*01:01 | 0.4061 | strong | 2 · 1 · 8 | retained | 2 |
| 5 | `MPPPLRGDM` | B\*07:02 | 0.4580 | strong | 7 · 1 · 1 | retained | 3 |
| 6 | `QQNMPCVQAQY` | B\*15:01 | 0.4986 | strong | 2 · 1 · 8 | retained | 4 |
| 7 | `DLDMPCVQAQY` | A\*01:01 | 0.5601 | weak | 2 · 1 · 8 | retained | 5 |
| 8 | `FDDMPCVQAQY` | A\*01:01 | 0.6837 | weak | 2 · 1 · 8 | retained | 6 |
| 9 | `KPGDMPCVQA` | B\*07:02 | 0.9381 | weak | 1 · 1 · 8 | retained | 7 |
| 10 | `MPPPLRGDMPC` | B\*07:02 | 1.2367 | weak | 7 · 1 · 3 | retained | 8 |
| 11 | `LDMPCVQAQY` | A\*01:01 | 1.8202 | weak | 1 · 1 · 8 | retained | 9 |

The panel's ranking key is `(-in_n_junctions, presentation_percentile)`; it is **read verbatim** from
the committed artifact and is never recomputed or touched.

**Two things worth saying plainly, neither of them comfortable.**

* The filter removes the **rank-1** candidate and the candidate with the **lowest (best)
  presentation percentile in the entire panel** (`NMPCVQAQY`, 0.3736, the only `strong` call among
  the removed). A screen-configuration filter that only ever removed weak tail candidates would not
  have changed anything; this one takes the head off the list. The new top of the panel,
  `GDMPCVQAQY`, is a **weak** call at 0.9687 that differs from the removed rank-1 by exactly one
  EWSR1 residue.
* All **4** peptides that NEOANTIGEN-4 recorded as occurring verbatim in the reviewed human proteome
  (`DMPCVQAQ`, `DMPCVQAQY`, `DMPCVQAQYS`, `DMPCVQAQYSP`, all NR4A3 isoform Q92570-3) fall inside the
  8 removed here. The filter **never consults the proteome** — that the two agree is a fact about
  this seam (NEOANTIGEN-4 §5.3's mechanism), **not** evidence that a composition filter substitutes
  for a novelty search. It does not, and the 20 zero-NR4A3 peptides were never tested against any
  isoform: no isoform sequence is present in this checkout and their status there is **UNKNOWN**.

### 5.3 Positive control — passed

`DMPCVQAQY`: zero EWSR1 residues (NEOANTIGEN-3), recorded verbatim in NR4A3 isoform **Q92570-3**
(`junction-proteome-novelty.json`, quoted into the artifact), pre-filter **rank 1**.
**Required to be removed → it was removed**, reason `zero_from_EWSR1`. Had it survived, the filter
would have been wrong and that would have been the result.

### 5.4 Remove-only, asserted rather than asserted-about

All eight assertions in `monotonicity_assertions` are `true`, and they fail the run rather than warn:
no candidate added; the post-filter panel is a **subsequence** of the pre-filter panel in pre-filter
order; it is a subset of it; pre-filter ranks strictly increase along the post-filter panel; no
retained candidate's `post_filter_rank` exceeds its `pre_filter_rank`; every retained candidate's
ranking key (`in_n_junctions`, `presentation_percentile`) is byte-identical to the committed one;
removed + retained = 11; and the positive control was removed. The same three assertions are carried
**inside** the diff so the property is enforced in the script, not only in this lane.

## 6 · The diff — UNAPPLIED, and how it interacts with NEOANTIGEN-4 / -5

`UNAPPLIED-zero-partner-filter.diff` (against `research/modalities/fusion_breakpoints.py`, sha256
`e9a2f4fcc10f626c0faa038555f444d5a9f3ebabab62305ab699b7e6f45ca626`) adds a module-level
`partner_residue_split()` reusing `junction_peptides`' own enumeration (one definition of the peptide
set, two readings of it), adds four reported fields per junction row, and adds
`panel_zero_partner_filter` to the result with both ranks side by side.

**`novel_peptides` is deliberately left exactly as it was.** The filter is reported *beside* the
unfiltered set, never applied to it in place — so every downstream reader and every committed
comparison keeps its meaning, and `test_fusion_breakpoint_panel_seam.py:172`
(`len(row["novel_peptides"]) == single["n_spanning_peptides"]`) is untouched rather than worked
around. **No guard, floor, gate, matcher, pin or test is weakened anywhere in this lane.**

* `git apply --check` on the diff alone: **exit 0** (`checks/05`).
* With NEOANTIGEN-4's `PARENTS` diff: **exit 0** (`checks/06`). With NEOANTIGEN-5's two diffs:
  **exit 0** (`checks/07`). With all four: **exit 0** (`checks/08`).
* Cumulative application (`patch -p1`, real applies on scratch copies), because `git apply --check`
  tests each patch against the tree rather than against the accumulated state:
  * `checks/12` — NEOANTIGEN-5 `-01`, then `-02`, then **mine**: **exit 0**, and the resulting
    `fusion_breakpoints.py` is byte-identical to the copy validated in `checks/09`/`checks/10`.
  * `checks/11` — NEOANTIGEN-4, then **mine**, then NEOANTIGEN-5 `-01`: **exit 1**, and the failure
    is *not* mine. NEOANTIGEN-4's diff and NEOANTIGEN-5's `-01` are **byte-identical files**: the
    third apply is the same patch a second time ("Reversed (or previously applied) patch detected").
* **Order to apply.** My diff touches a **different file** and is independent of both; it may be
  applied before or after either. The only ordering constraint in the family is between NEOANTIGEN-4
  and NEOANTIGEN-5: apply the `PARENTS` change **once** (either copy — they are the same patch),
  then NEOANTIGEN-5's `-02` test file, in that order. No rebase of my diff was needed.

## 7 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `refiltered-panel.json`; generators `neoantigen6_zero_partner_refilter.py` and
  `verify_patched_emit.py`; `UNAPPLIED-zero-partner-filter.diff`; `checks/` — **12 attempts, real
  exit codes, every failure preserved** (`checks/03` is a genuine failed run, exit 1: the
  cross-check assumed NEOANTIGEN-4 emitted one row per (peptide, junction) when it emits one row per
  distinct peptide; `checks/11` is exit 1 for the reason in §6).
* **Validation / baseline.** 79 existing tests for the audited script, run **unmodified**, green
  before any change (`checks/01`); the same 79 green against the **patched** copy (`checks/09`), so
  the diff breaks nothing; 9 novelty tests green (`checks/02`); the patched `emit_junction` driven
  over the real transcript model reproduces 5 junctions, 174 distinct peptides, the same 8 and the
  same 20, with `novel_peptides` byte-identical to the committed artifact (`checks/10`); an
  independent recomputation of the split agreeing with NEOANTIGEN-4 on all 174 of its rows with 0
  disagreements; eight remove-only assertions; and the required positive control.
* **Provenance.** Inputs read in place from the existing checkout — `fusion-breakpoint-neoantigens.json`
  (`_utc` 2026-08-19T16:26:49Z), `junction-proteome-novelty.json` (sha256 `ff1ccc2c…`),
  `../NEOANTIGEN-4/neoantigen4-novelty-audit.json`. No repo copy and no worktree: the patched-code
  run used a **symlink mirror** of `research/modalities` and `research/manuscripts` in the scratchpad
  (15 MB of directory entries, no data copied), with the shared tracked file left untouched.
  **$0** — no network, no GPU, no paid API.
* **Limitations.**
  1. ⛔ No immunogenicity, presentation, tolerance, safety, selectivity, therapeutic-window or
     clinical claim. The panel is still MHCflurry screen output; filtering it changes which
     predictions are listed, not what a prediction is worth.
  2. **The binding predictions were not recomputed.** MHCflurry is not importable here, so the
     ranking keys are read verbatim from the committed artifact. Re-running the screen end to end
     with the diff applied is a runner job, not done here.
  3. The filter is a **composition** rule; it does not test wild-type occurrence. §5.2's 4-of-4
     agreement with the proteome hits is a property of this seam, not a general substitution.
  4. Whether the 20 zero-NR4A3 peptides occur in any recorded isoform is **UNKNOWN here** — no
     isoform sequence is in this checkout and none was fetched.
  5. The discriminator is retention-permissive (zero-partner at *every* emitting junction). On this
     panel the choice is inert — no peptide is zero-partner at one junction and specific at another —
     but the rule is stated because a future junction set could make it bite.
  6. The panel's own five junctions and their transcript model are this repository's.
* **Stop condition.** Reached, exactly as the proposal set it: the re-emitted panel plus the diff.
  Nothing further was started.

## 8 · What the paper owner may do with this (not done, not authorised here)

1. Decide whether to apply the diff. It is additive and remove-only; the re-emitted panel is in
   `refiltered-panel.json` either way.
2. If the screen's headline is ever quoted as "11 ranked binders, top `DMPCVQAQY`", it should become
   **"9 junction-specific ranked binders of 11 screened; the pre-filter rank-1 and rank-3 candidates
   carry no EWSR1 residue and were removed"** — with the pre-filter panel kept beside it, as here.
3. Re-run the screen with the diff applied on a runner that has MHCflurry, to confirm the panel end
   to end rather than by recomputation from the committed artifact.
