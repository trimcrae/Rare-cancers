---
id: DOC-MF1-RESIDUAL-PATCHES
title: "MF1 residual — exact unapplied patches for the parent-owned shared files"
level: L4
kind: memo
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# MF1 residual R1 — the four live shared cells, as an exact unapplied patch

⛔ **NOTHING HERE HAS BEEN APPLIED.** These are parent-owned shared files. The MF1 residual author
prepared, verified and filed this patch and did not touch the shared tree.

## What this narrows

The 13 P1–P6 edits are **already applied** at `a6a21fc591d2451038cdf53449b91e3990d59cfb`; ⛔ **do not
reapply them.** That commit changed only three census rows — `V5.scope_limit`, `V16.result` and coverage
`R5.hole_verbatim` — and left four current cells still carrying readings the manuscript withdraws. This
patch is exactly those four, plus the two chronology/absent-wedge phrasings they sit inside. It performs
**no wholesale rewrite of the historical roadmap**: only the current statements a reader actually arrives
at are corrected, and each correction is dated in place beside the wording it supersedes.

## The file

`0001-roadmap-four-live-residues.patch` — a unified diff against
`research/manuscripts/nr4a3-program-map.md` at the current branch state.

| # | roadmap target | what changes | residual |
|---|---|---|---|
| Q1 | §3.1 `V11` **result** cell | `NULL, adequately powered` → `NULL` plus a dated withdrawal: the 1/462 floor is discreteness, not power; no effect size is established | R1 |
| Q2 | §3.1 `V16` **result** cell | `registered in advance as the LIKELY outcome` → *the retained protocol **describes** it as registered in advance; the chronology is unestablished* | R2 |
| Q3 | §3.1 `V16` **scope** cell | `S may be read as a bound` → `may NOT be read as a bound`; `S ≈ 0 means the marginal wedge is absent` → explicitly withdrawn | R1 |
| Q4 | §3.1 `V20` **scope** cell | the universal *"not recoverable by any downstream method"* claim withdrawn; replaced by the positive-call-rate scope | R1 |
| Q5 | the dependency row at `:3246` | the surviving *"with a quantified bound"* clause that still preceded the a6 withdrawal is removed and dated | R1 |
| Q6 | the reading row at `:986` | `S ≈ 0 → the marginal wedge is absent` withdrawn; `reading (fixed in advance)` re-attributed to the retained protocol | R1 / R2 |

Every OLD string was verified to occur **exactly once** in the roadmap before the diff was generated;
the generating script is `mkpatch-roadmap.py` beside this file and refuses to emit a patch otherwise.

## Verification actually performed

| check | command | measured exit |
|---|---|---|
| uniqueness + diff generation | `python3 mkpatch-roadmap.py …` | **0** — 6/6 targets unique, 5 changed lines |
| applicability, **without applying** | `git apply --check -p1 0001-roadmap-four-live-residues.patch` | **0** |

Both are preserved in full under `../checks/03-…` and `../checks/04-…`.

## ⭐ The sequencing the integrator needs, and why it matters

The dependency is **roadmap → `research/modalities/instrument-census.json` → the MF1 extraction → the
inventory and the manuscript supplement.** The census is **generated, never hand-edited**
(`research/modalities/instrument_census.py`), so the three census cells named above cannot be patched
directly — they change only when the roadmap changes and the census is regenerated.

1. Apply `0001-roadmap-four-live-residues.patch`.
2. Run the **one admitted instrument-census metadata update**: `python3 research/modalities/instrument_census.py`.
   ⛔ **This author did not spend it.** Running it before the roadmap patch lands would produce no change:
   `instrument_census.py --check` returned **exit 0, "OK (22 instruments, 16 requirements)"** against the
   current roadmap on 2026-09-08, so the committed census is already in sync with the unpatched source.
   Capture the real command, complete stdout, complete stderr and measured exit.
3. Regenerate the views the graph/roadmap edit staled, as the a6 record did.
4. ⚠ The MF1 supplement does **not** need a further extraction to stop republishing the withdrawn claims:
   the extraction now carries an explicit **author-current claim-scope** column and demotes the census
   string to a labelled *superseded historical annotation*, so the supplement is correct whether or not
   this patch lands. A re-extraction after step 2 would only refresh the historical column and the input
   manifest, and is the integrator's call, not a correction this batch owes.

⛔ **No wet-lab, efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim is created
or implied by any of these edits, and none of them is a new measurement.**
