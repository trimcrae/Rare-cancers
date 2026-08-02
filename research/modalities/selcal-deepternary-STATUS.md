# DeepTernary head-to-head — status and the one open defect (2026-08-02)

**Goal it serves:** a **positive ternary control** for the paper. The program has none in any form. This
run would supply one *at the generation stage*: a known-answer ternary test, run blind, that the workflow
passes. It would **not** supply a positive control for paralogue-selectivity *detection* — different stage,
harder claim, and the panel our co-folds fed returned a NULL whose bound is unchanged by any of this.

## Established and committed

| step | state |
|---|---|
| Blindness of the test cases | **verified** — 9DTY/9DTX absent from DeepTernary's disclosed exclusion set (`deepternary-leakage-check.json`) |
| Input sourcing from RCSB | **done** — 12 target-side + 12 E3-side candidates per arm |
| Input curation | **done** — SMARCA2: 9DU0 + 5NVX; SMARCA4: 5DKD + 5NVX |
| Fragment verification | **done** — SMARCA2 warhead overlap **1.000**, anchor 0.778 → READY; SMARCA4 warhead **0.417** → **REFUSED** below the 0.55 bar |
| Chain resolution | **done** — one copy of the E3, seeded from a single ligand instance |
| Blind input prep (6 files) | **done** |
| Prediction | ⛔ **BLOCKED — see below** |
| Scoring | not reached |

The incumbent to beat, read from `selcal-cofold-dockq.json`: our Boltz co-folds score DockQ **0.023–0.038**
on this arm's target↔VHL interface, fnat 0.000.

## The open defect — CONECT records

`predict_cpu.get_lig_coords` calls `Chem.MolFromPDBFile('unbound_lig1.pdb')` and gets `None`
(run 30752326235, `AttributeError: 'NoneType' object has no attribute 'GetConformer'`).

**Cause:** 9DU0 and 9DTY are **mmCIF-only** entries, so this lane converts them to PDB
(`selcal_deepternary_run.write_pdb`) for `deepternary_blind_prep`, which is PDB-only. mmCIF stores bonds in
`chem_comp_bond`, not as CONECT records, so the converter emits **coordinates without connectivity**.
RDKit's PDB reader infers protein bonds from residue templates but has no template for a novel HETATM like
`A1BB5`, so with no CONECT it produces an unsanitizable molecule and returns `None`.

⚠ This is a **format-plumbing defect, not a scientific one**, and it must not be read as "DeepTernary failed"
or as "the inputs were bad". The inputs passed verification: the warhead is a perfect substructure of the
degrader (21/21 heavy atoms).

### Plumbing chain: fully resolved, five CI runs (30752190988 → 30753431082)

Every layer below is now **fixed and passing**. Each was found only by the run after the previous fix,
and each returned a plausible-looking success rather than an error — the pattern this whole session has
been about.

| layer | defect | state |
|---|---|---|
| structure fetch | 9DU0/9DTY are mmCIF-only; `.pdb` 404s | fixed — fetch falls back to CIF |
| CIF→PDB conversion | mmCIF has no CONECT; RDKit can't bond a novel HETATM | fixed — CONECT sourced from the CCD `_chem_comp_bond` table, never distance-guessed |
| `extract_ligand` | copies HETATM lines only, stripping the CONECT just added | fixed — re-appended post-prep, serials renumbered to the extracted file |
| **residue-name width** | **legacy PDB gives 3 columns; `A1BB5` truncated to `A1B`, so extraction found ZERO atoms — and `prep_control` still reported `ok: true`, because its contract tests file existence, not content** | **fixed — long CCD ids aliased to a short placeholder; extraction uses the alias, bond lookup keeps the real id; workflow now asserts every `unbound_*` atom count is non-zero** |
| return-tuple edit | landed on `fix_ligand_conect` instead of `emit_raw` | fixed — both verified by AST walk rather than another CI round |

**Now passing:** blindness verified → inputs sourced and curated → fragments verified (SMARCA2 warhead
overlap **1.000**; SMARCA4 refused at 0.417) → chains resolved to one E3 copy → six blind input files built
→ ligand files readable by RDKit → non-zero atom counts asserted.

## The open failure — inside the model, not the plumbing

Run 30753431082, step 9:

```
RuntimeError: max(): Expected reduction dim to be specified for input.numel() == 0
```

An **empty tensor inside DeepTernary's own forward path**. The inputs are now well-formed by every check
this lane applies, so this is the first failure that is not file plumbing. Most likely candidate: no atom
correspondence is being found between the extracted warhead fragment and the full degrader, leaving a
zero-length index tensor — but that is a **hypothesis, not a diagnosis**, and it must be instrumented
before it is acted on.

**Next step:** run `predict_one_unbound` for the single ready arm directly, with the tensor shapes printed
at each stage, and find which one is empty. Do **not** patch around it — a reduction over an empty tensor
means something upstream selected nothing, and silencing it would produce a pose built from no
correspondence at all.

## Still binding

- **Do not lower the 0.55 fragment bar** to admit the SMARCA4 arm.
- **Do not quote DeepTernary's 0.62–0.83** as an expectation — those are on structures inside its exclusion set.
- **Do not report an unrun arm as a zero.** The scorer already refuses this and says so:
  *"No arm produced a scored prediction. Unrun is not a failed run."*
