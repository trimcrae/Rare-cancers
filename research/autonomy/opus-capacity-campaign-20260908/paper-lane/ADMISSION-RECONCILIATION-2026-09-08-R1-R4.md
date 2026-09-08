---
id: DOC-OPUS-CAMPAIGN-ADMISSION-RECONCILIATION-R1-R4
title: "Refill admission reconciliation — R1, R2, R3, R4, 2026-09-08"
level: L4
kind: selection-record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Refill admission reconciliation — R1–R4

**My selection error, named plainly.** I refilled four owners from
`PROPOSAL-next-work-backlog.md`. That file is a **proposal for root admission and is not itself
authorization** — its own last line says *"Nothing above is admitted. Root adjudicates."* I treated
it as a live queue. It is not one, and an entry in it is neither proof that work is outstanding nor
proof that its design was ever admitted. **Names alone are not proof of identity.** All four are
reconciled below against the actual existing records; nothing is reworded to survive.

## R1 · risk-table density — STOPPED, duplicate of CLOSED work

Completed at `78f268caf` as `R1-risk-table-sensitivity/` (`RESULT.md` 12,536 B; `RUN-01.stdout.json`
72,838 B; empty stderr), and **closed** by root's dated interpretation correction at `1dd53f562`.
Its **52-cell** diagnostic grid — the full 10 × 5 crossing plus sentinel and rounding probes —
strictly contains the 30-cell grid I dispatched. **There is no pending second density/sensitivity
sweep, no 16-render arm and no paper in that admission.**

Preserved in `R1-risk-table-density/`: the contract, `BEFORE/` byte copies, and **four real runs with
measured exits, all 0** — baseline check, baseline tests, reproduction-gate prototype, grid
prototype. The reproduction gate **passed exactly** (events Δ 0, censored Δ −7, deviation 0.0009,
matching the committed baseline). Recorded as an independent corroboration of an existing artifact
and **nothing more** — not promoted, no requirement stated. **No tracked file was modified.** Detail:
`R1-risk-table-density/STOPPED-DUPLICATE-2026-09-08.md`.

## R4 · zero-handling — STOPPED, duplicate of CLOSED work

Completed at `78f268caf` as `R4-zero-handling-sensitivity/` — per-gene convention table (2,587 lines),
sign-rank sensitivity (863 lines = 862 genes + header), summary, 304-line write-up, 381-line
producer — and closed by `1dd53f562` ("R4 bracketing"). Its recorded conclusion is **stronger and
less flattering** than the one my contract went looking for: *the zero-handling invariance is a
tautology of the panel's construction, not robustness.*

The agent was stopped **while reading its specification**. **No command ran, no file was written, no
tracked file changed.** There is no execution stream, and none is invented. Detail:
`R4-zero-handling-robustness/STOPPED-DUPLICATE-2026-09-08.md`.

## R2 · condensate convergence — RAN; NO simulation; result held NOT ADMITTED

The owner had already returned when the reconciliation arrived. **It executed no scientific
simulation and acquired nothing.**

**Precondition NOT MET**, established by real commands with measured exits (`checks/01`–`09`):
`import calvados` **exit 1** (required 0.8.1 @ `c16f59a6`, a git pin), `import openmm` **exit 1**
(8.4.0.post2), `import MDAnalysis` **exit 1**, `import mdtraj` **exit 1**, `pandas` absent; no
install anywhere on disk; no conda (**exit 2**); `nvidia-smi` absent; PyPI hosts sit in `no_proxy`.
Acquisition was fenced, so it stopped compute — correctly.

**Second independent stop, the clock:** at the retained 3,392 s/run on 4 threads, a whole-panel
doubling is **103.6 h** and even a targeted 14-run extension is **13.2 h**, against **3.75 h**
remaining at check time — short by 3.5×–28×.

It then re-scored the **retained 55 runs** through the **unaltered frozen `score()`** using
`nu_second_half`, the later-time estimator the prereg §2 already registers. No new sampling, no
protocol deviation, no threshold touched; `emc-condensate-calvados.json`, `emc_condensate_calvados.py`
and the prereg are **byte-identical** and no run was appended.

⛔ **That re-scoring is HELD, NOT ADMITTED, and is not promoted anywhere.** Root's dispositions did
not admit R2's scientific execution without a fixed design / restart / runtime / resource contract,
and I did not have one when I dispatched. The output stays in `R2-condensate-convergence/` as a
preserved artifact of an unadmitted contract. It changes nothing: `converged = false` and 0.2545 >
0.20 stand, `PROVISIONAL` was not lifted, and the four registered negatives stand exactly as
committed.

**Concrete missing contract:** a root-fixed design, restart policy, runtime bound and resource
allocation for the CALVADOS arm — plus, separately, the absent CALVADOS 2 / OpenMM environment,
which no fence here permits acquiring.

## R3 · fourth-cohort EWSR1-negative — STOPPED mid-run, result NOT ADMITTED

Stopped while writing its artifacts. Root's dispositions did not admit this cohort scope — a
**mismatched native-versus-fusion-junction cohort without the required data identities**.

Preserved exactly as found: `r3_place_probes.py`, `r3_informative_window.py`,
`PROBE-PLACEMENT.tsv`, and **four real runs, all measured exit 0** — probe placement, a v2 placement
with a chimeric-seam scan, an informative-window computation, and a write-isolation check. That last
run confirms **no tracked file under `research/modalities`, `research/manuscripts` or `systems` was
modified by this owner.** No exit is invented, and no partial output is discarded or completed.

⛔ **Its partial findings are not quoted, promoted or carried into any manuscript.**

**Concrete missing identities:** the native-versus-fusion-junction cohort correspondence this
question needs, and the Ensembl cDNA + ncRNA FASTA that `map_probes_to_genes` fetches over the
network — backlog **B1**, present in neither the checkout nor the frozen corpus, and **not
authorised**.

## What I am changing about selection

Refill selection now checks, before dispatch: (1) the lane directory for a completed sibling, (2)
the commit history for a dated closure, and (3) that an actual **root disposition** covers the
design — not merely that a proposal describes it. Standing refill authority covers **ready work in
already-admitted streams**; it does not convert a proposal into an admission, and root's authority
over new scientific designs is untouched.
