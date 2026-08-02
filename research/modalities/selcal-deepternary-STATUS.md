# DeepTernary lane — status (2026-08-02)

**Goal it serves:** a **positive ternary control** for the paper. The program had none in any form.

⚠ **THE SHAPE OF THAT CONTROL CHANGED TODAY, AND THE OLD SHAPE WAS NOT ACHIEVABLE.** This lane was built to
supply a *blind* known-answer ternary test on 9DTY/9DTX. Reading DeepTernary's own released data showed the
protocol it would have to use is not blind — see "The protocol, measured" below. So the control now has two
parts, and only the first is a control:

| | what it is | what it licenses |
|---|---|---|
| **1. Positive control on the harness** | the generator on `6HAX_B_A_FWZ` — a VHL/SMARCA2 PROTAC ternary from its **own shipped benchmark inputs** — re-scored by **our** two instruments | that this build, this checkpoint, this seed budget and these scorers can produce **and recognise** a correct ternary. A near-zero reading elsewhere is then about that input, not the plumbing. **Nothing about generalisation:** 6HAX is a 2018 deposit, inside the model's 2023-10-14 horizon, so it is memorisation-permitting by construction. |
| **2. The selcal arms** | the same generator on 9DTY/9DTX with inputs built the way the published protocol builds them | a comparison between two generators on the same two systems. **Not blind**, and not a positive control. |

Neither part is a positive control for paralogue-selectivity **detection** — different stage, harder claim,
and the panel our co-folds fed returned a NULL whose bound is unchanged by any of this.

## The protocol, measured — and why the earlier reading was wrong

Two runs (30753431082, 30754028742) died inside the forward pass at

```
predict_cpu.replace_to_unbound_coords ->  assert cdist.min(dim=1)[0][update_mask].max() < 1
RuntimeError: max(): Expected reduction dim to be specified for input.numel() == 0
```

`update_mask = cdist.min(dim=1)[0] < 1` selects the degrader atoms lying within 1 Å of a supplied fragment
atom. Our `ligand.pdb` was the **CCD ideal conformer** in an arbitrary frame, so nothing was near anything,
the mask was empty, and the reduction died. **The empty tensor was never a model bug** — it was the model
correctly reporting that nothing had been positioned.

The next guess was a **constrained embed** (pin the warhead onto `unbound_lig1`, the anchor onto
`unbound_lig2`). **DeepTernary's own `output.zip` refutes that guess**, which is why it was measured before
it was built. In the shipped `6HAX_B_A_FWZ`:

| observation | value |
|---|---|
| `ligand.pdb` vs the FWZ ligand of `gt_complex.pdb` | **max deviation 0.000 Å over all 66 heavy atoms** — it is the NATIVE pose |
| `unbound_protein1.pdb` (a different entry: chain I, 1150 atoms) centroid | (−21.6, 17.3, −20.3) vs the native POI's (−21.3, 17.6, −20.7) |
| `unbound_protein2.pdb` centroid | matches the native E3 the same way |
| degrader atoms within 1 Å of `unbound_lig1` / `unbound_lig2` | **33 / 18** |

So the published UNBOUND protocol **superposes each unbound binary into the native ternary frame and supplies
the native degrader pose**. `selcal_deepternary_frame.py` does that, and `--reproduce-reference` proves it is
the same construction: displace each shipped unbound structure by 63° / ~40 Å, re-derive the frame from
sequence-matched Cα Kabsch, and the snap masks come back **33 → 33 and 18 → 18**. No pinned number is
compared against, so that check cannot pass by having been tuned to a remembered figure.

### ⛔ What this costs, stated plainly

**The word "blind" is not available for the selcal arms**, and it was used across this lane until the shipped
data was read. `tests/test_selcal_deepternary_frame.py` fails on an unretired claim.

- The leakage check (`deepternary-leakage-check.json`: 9DTY/9DTX absent from the disclosed exclusion set)
  **still holds and still matters** — it is *necessary* for a blind claim. It is no longer *sufficient*.
- What the model **is still genuinely asked for** is the **relative placement of the two proteins**:
  `predict_one_unbound` applies an independent random rotation+translation to protein 2 and to the ligand
  before the forward pass, so the native arrangement is destroyed in the input and the architecture is an
  output. `gt_complex.pdb` is read at exactly one place in that file — `cal_dockq(...)` — and never reaches
  the model.
- What the model **is given** is which pocket on each protein the ligand occupies. Our Boltz co-folds were
  given sequence and ligand and nothing else. **The two numbers must never be set side by side as though
  they were the same test.**

## Established and committed

| step | state |
|---|---|
| Exclusion-set check on the test cases | **verified** — 9DTY/9DTX absent (`deepternary-leakage-check.json`) |
| Input sourcing from RCSB | **done** — 12 target-side + 12 E3-side candidates per arm |
| Input curation | **done** — SMARCA2: 9DU0 + 5NVX; SMARCA4: 5DKD + 5NVX |
| Fragment verification | **done** — SMARCA2 warhead overlap **1.000**, anchor 0.778 → READY; SMARCA4 warhead **0.417** → **REFUSED** below the 0.55 bar |
| Chain resolution | **done** — one copy of the E3, seeded from a single ligand instance |
| Input prep (six files) | **done** |
| Builder reproduces the published construction | **verified offline** — p1 33→33, p2 18→18 on `6HAX_B_A_FWZ`; re-checked in CI every run |
| Positive control on the harness | **running** |
| Selcal arms: prediction + scoring | **running** |

The incumbent, read from `selcal-cofold-dockq.json`: our Boltz co-folds score DockQ **0.023–0.038** on this
arm's target↔VHL interface, fnat 0.000.

## Plumbing chain: fully resolved, seven CI runs (30752190988 → 30754028742)

Each layer was found only by the run after the previous fix, and **each returned a plausible-looking success
rather than an error** — the pattern this whole session has been about.

| layer | defect | state |
|---|---|---|
| structure fetch | 9DU0/9DTY are mmCIF-only; `.pdb` 404s | fixed — fetch falls back to CIF |
| CIF→PDB conversion | mmCIF has no CONECT; RDKit can't bond a novel HETATM | fixed — CONECT sourced from the CCD `_chem_comp_bond` table, never distance-guessed |
| `extract_ligand` | copies HETATM lines only, stripping the CONECT just added | fixed — re-appended post-prep, serials renumbered to the extracted file |
| **residue-name width** | **legacy PDB gives 3 columns; `A1BB5` truncated to `A1B`, so extraction found ZERO atoms — and `prep_control` still reported `ok: true`, because its contract tests file existence, not content** | **fixed — long CCD ids aliased to a short placeholder; extraction uses the alias, bond lookup keeps the real id; workflow asserts every `unbound_*` atom count is non-zero** |
| return-tuple edit | landed on `fix_ligand_conect` instead of `emit_raw` | fixed — both verified by AST walk rather than another CI round |
| **degrader frame** | **the ideal conformer is in an arbitrary frame, so the model's 1 Å proximity mask was empty** | **fixed — `selcal_deepternary_frame.py` builds the native-frame inputs the protocol requires** |
| **predictions deleted** | **`cfg.tmp_dir` is a `TemporaryDirectory` and the script's last line is `cleanup()`, so every predicted complex was erased before our scorers ran — they would have recorded "no predictions" for a run that predicted fine** | **fixed — the directory is redirected to `dt/predictions/` and both scorers follow it** |

## Still binding

- **Do not lower the 0.55 fragment bar** to admit the SMARCA4 arm.
- **Do not quote DeepTernary's 0.62–0.83** as an expectation — those are on structures inside its exclusion set.
- **Do not report an unrun arm as a zero.** Both scorers refuse this and say so.
- **Do not call the selcal arms blind.** A test enforces it.
- **Do not quote the 6HAX positive control as evidence of generalisation.** It is inside the data horizon;
  that is the point of it, and also its limit.
