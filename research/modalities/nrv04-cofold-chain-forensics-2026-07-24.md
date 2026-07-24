# NR-V04 co-fold + chain-split forensics (2026-07-24)

**Two independent defects, found while de-risking the NR-V04 retrospective before spending anything.** Both
were found by *measuring* the assemblies rather than trusting the conventions the code assumed. Both are
recorded here with the observation that proves them, per the standing root-cause rule.

Neither was caught by any existing test, because both produce **numbers, not errors**.

---

## Defect 1 — the descriptive-v3 co-folds contain 14-3-3 epsilon in place of Elongin B

### Evidence
CI run **30122648680** (`nrv04_cofold_audit.py`, free runner, open internet). UniProt lengths fetched live;
chain census taken from the real CIFs with gemmi.

| co-fold prefix | built (S3 LastModified) | chain F | verdict |
|---|---|---|---|
| `nrv04-descriptive-v3` — **the retrospective's intended inputs** | 2026-07-11 | **255 res → `sp\|P62258\|1433E_HUMAN` 14-3-3 protein epsilon** | **AFFECTED** |
| `nrv04-shakeout` | 2026-07-11 | **255 res → P62258 14-3-3 epsilon** | **AFFECTED** |
| `nrv04-covalent-cofold` — the completed feasibility panel's inputs | 2026-07-22 | 118 res → `sp\|Q15370\|ELOB_HUMAN` Elongin-B | **clean** |

Every affected assembly is: A = 254 (NR4A LBD), E = 213 (VHL), **F = 255 (14-3-3ε)**, G = 112 (Elongin C).

### Mechanism
`nrv04_ternary.py` builds its co-fold YAML by fetching `ELONGIN_B`'s sequence directly from the module
constant. That constant was **P62258 — 14-3-3 protein epsilon (YWHAE)** until it was corrected to **Q15370**
on 2026-07-17. The timeline matches exactly: co-folds built 2026-07-11 carry 14-3-3ε; the 2026-07-22
regeneration carries real Elongin B.

This was **already half-known**. [`e3-provenance-correction.json`](./e3-provenance-correction.json) records the
accession error and correctly establishes that **valB was physically unaffected** (valB resolves its chains from
RCSB 8G1Q, which always mapped Elongin B correctly). But that record scoped the remaining exposure to *"the
NR-V04 co-fold sequence-fetch constant (a separate, **parked** workstream)"* — and the follow-up never ran. The
physical consequence measured here is what that parked item actually amounted to.

### Consequences
- The **retrospective cannot use `nrv04-descriptive-v3`.** Those co-folds must be regenerated with the
  corrected accession. (Cheap: Boltz co-folds, ~$1–2 for the 9 R1 models.)
- The earlier **co-fold ternary benchmark** result — the exploratory "NR4A1 moiety-bridges 2/3, NR4A2/NR4A3
  0/3" concordance, plus the epimer-blindness finding, both recorded from the `descriptive_v3` run — rests on
  assemblies in which one E3 subunit is the wrong protein. That result is **not** invalidated in its *negative*
  conclusion (the epimer-blindness limitation was a statement about what the readout cannot see), but its
  *positive* paralogue separation is no longer supportable as stated and must be re-derived or withdrawn.
- The completed **covalent feasibility panel is clean on this defect** — its inputs were regenerated after the
  correction.

---

## Defect 2 — the E3/target chain split was positional, and pointed at Elongin C

### Evidence
Two independent measurements agree.

**(a) The chain census.** In every co-fold, the NR4A LBD is chain **A** (254 residues, matching the frozen
construct) and the chains sort **A, E, F, G**. `nrv04_covalent_md._topology_indices` took *the last protein
chain in sorted order* as the degradation target → it selected **G = Elongin C, 112 residues**.

**(b) The completed panel's own committed artifacts** (CI run **30122828434**). The same driver resolves the
reactive cysteine independently, **by geometry**, and records its chain in each leg's `meta.reactive_cys`. That
cysteine sits on the NR4A1 LBD. Across the 14 landed legs:

| legs | recorded reactive-Cys chain | what the positional rule called "target" |
|---|---|---|
| `cov_nr4a1` ×3, `noncov_nr4a1` ×3, `recruiter_active` ×3, `recruiter_epimer` ×3 | **A** (resid 222, Sγ 7.4 Å) | **G** (Elongin C) |
| `warhead_only` ×2 | G (resid 74, Sγ **12.44 Å** — the driver's own >8 Å warning fired) | G |

The driver was pointing at chain A and chain G **at the same time, in the same run**, for the same complex.

### Mechanism
`nrv04_ternary.py` composes the ternary YAML as `proteins = [("A", target_lbd)] + e3` — **target first**. The
driver's comment asserted the opposite convention (*"E3 are the first assembled chains, target LBD is the last
protein chain"*). The two were never reconciled, and because a wrong chain split yields perfectly well-formed
numbers, nothing failed.

### Consequences
- The covalent feasibility panel's **R1 (interface RMSD), R2 (recruitment) and R3 (Lys presentation) describe
  the Elongin C↔rest interface**, not the VHL↔NR4A1 interface they were reported as. R3 in particular counted
  **Elongin C's lysines** as the ubiquitination-competent target lysines.
- That panel's recorded result — *"recruiter_active 3/3 stable vs epimer 1/3"* — is reproduced exactly by the
  landed plateaus (active 3.07 / 2.418 / 3.367 all < 4.0 Å; epimer 4.175 / 4.492 / 2.844) so the **arithmetic is
  right**; it is the **interface being measured** that is wrong. The panel's **GO verdict for RUNG 4 does not
  survive as stated.**
- The `warhead_only` legs additionally tethered celastrol to an **Elongin C cysteine 12.4 Å away**, because no
  nearer Sγ existed — the co-fold had not posed free celastrol in the NR4A1 pocket at all.

---

## Fixes applied (2026-07-24)

1. **The split is identified, not guessed.** `nrv04_covalent_assemble.identify_chains` matches every chain to a
   known E3 component by residue count (VHL 213 / EloB 118 / EloC 112, all verified against UniProt in the audit
   run) and takes the single leftover as the degradation target, requiring it to be the frozen 254-residue LBD.
   It **fails closed** on anything ambiguous.
2. **A contaminated co-fold is rejected at staging.** 255 residues (14-3-3ε) is an explicit contaminant signature
   — it is within one residue of the NR4A LBD, so a naive largest-chain rule would have swapped them.
3. **The split is written to `chains.json`** beside the inputs, and `nrv04_covalent_md._topology_indices` consumes
   it. The positional fallback survives only for pre-existing inputs and prints a loud warning naming this
   incident.
4. **Every leg now records the chain split it used** (`result.chain_split`). The completed panel could not be
   audited from its own output — the split had to be reconstructed from the source CIFs — which is precisely why.
5. **Regression tests** (`tests/test_nrv04_chain_split.py`) pin that the identifier selects the LBD, that the old
   positional rule would have picked Elongin C, that composition (not chain order) decides, and that a
   contaminated or wrong-sized assembly raises.
6. **The retrospective's stage test refuses to launch** on a chain-split mismatch, which is how Defect 2 surfaced.

## What is NOT yet done — and is a decision, not an oversight

- **The descriptive-v3 co-folds have not been regenerated.** The retrospective's R1/R2 legs are blocked on that.
- **The feasibility panel has not been re-run.** Its trajectories were not retained (only the readouts), so
  correcting its result requires re-running the 14 legs (~$6 at the measured per-leg cost) with the fixed split.
- **The manuscript and STRATEGY.md still carry both affected results** — the covalent panel's GO and the co-fold
  benchmark's paralogue separation. Until the re-runs land, they should be marked as under correction rather
  than cited.
