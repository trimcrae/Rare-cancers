# C04 — paralogue-matched cryptic-pocket druggability

> **$0 CPU/CI. No GPU, no rental.** Nothing here is a claim about binding, reactivity, degradation,
> selectivity in vivo, efficacy or safety.
>
> **★ ONE FACT, ONE PLACE.** Every number lives in
> [`paralogue-pocket-contrast.json`](./paralogue-pocket-contrast.json), produced by
> [`paralogue_pocket_contrast.py`](./paralogue_pocket_contrast.py). This file carries the reasoning and
> points at the JSON; it is not a second home for any figure. The committed NR4A3-only table keeps its own
> home at [`nr4a3-pocket-reharmonize-summary.json`](./nr4a3-pocket-reharmonize-summary.json).

---

## 1 · Why this existed to be run at all

The premise of the whole **non-covalent route** (`R1` → `R7`, Route A) is that the cryptic orthosteric pocket
is itself a paralogue discriminator — that NR4A3 opens a druggable cavity the paralogues do not. That premise
had **never been measured against a paralogue.**

Two committed facts made the gap visible and the fix free:

1. [`nr4a-paralogue-dynamics.json`](./nr4a-paralogue-dynamics.json) → `ensemble_census` records
   `results/nr4a1-pocket-ensemble` and `results/nr4a2-pocket-ensemble` with **100 frames each, in exactly
   NR4A3's subset structure** (`metad` 25 + `release_rep0/1/2` 25 each; 75 unbiased). Those frames are
   committed to this repo.
2. [`nr4a3-pocket-reharmonize-summary.json`](./nr4a3-pocket-reharmonize-summary.json) has **eight rows and
   every one of them is NR4A3.**

So the detector existed, the frames existed, the frames were frame-matched — and the two had never been put
together. That is candidate **C04** in [`instrument-options.md`](./instrument-options.md), and it needed one
external binary (fpocket) and no money.

## 2 · What is matched, and the one thing that is not

**Matched:** the frames (one lane, identical subset structure), the site definition, the acceptance
thresholds ([`pocket_tracking.match_params()`](./pocket_tracking.py)), `D*`
([`pocket_tracking.D_STAR`](./pocket_tracking.py)), and — because all three species are scored in **one
process** — the fpocket binary itself.

**Not matched to the committed table.** `nr4a3-pocket-reharmonize-summary.json` records
`fpocket_version: "4.0"`; this run pins whatever CI resolves, and records it. ⚠ **That is exactly why NR4A3's
own 100 frames are RE-SCORED here** rather than quoting the committed rows: the contrast that carries the
conclusion is computed inside this run under one build, and the committed table is demoted to a
**reproduction check** (`committed_nr4a3_reproduction_check` in the JSON).

**The site is NR4A3's site.** The prespecified Pocket-5 lining set is mapped onto each paralogue by the same
BLOSUM62 Needleman-Wunsch construction `nr4a3_metad._resolve_target` uses to put the metadynamics CV on the
homologous paralogue pocket (`nr4a_paralogue_dynamics.homologous_pocket`). All three species map **10 of 10**
lining residues. So the question asked is *"is NR4A3's site open here?"* — **not** *"does this protein have
any druggable cavity?"* Those are different questions and only the first is Route A's premise.

## 3 · What a result licenses

**Licenses.** A paralogue-matched **conformational-selection** statement with no free energy in it: *the site
that must open to bind is detected at rate X and reaches `D*` at rate Y, on matched ensembles and one
detector.* That is a selectivity argument that is immune to the regime gap
([`instrument-options.md` §0](./instrument-options.md)) — it needs no ~1 kcal/mol resolution because it is not
a free-energy quantity at all.

**Does not license.**

- **`ΔG_open`.** A detection fraction is **not** an opening penalty and must never be reported as one.
  `R6` stays open.
- **Evidence of ABSENCE.** At these ensemble sizes a paralogue that never opens is weak evidence. This
  supports a **ranking**, never a categorical exclusion. That is why C04 is graded `A−` and not `A`.
- **Anything about a cavity the paralogue may have elsewhere.** A paralogue row of 0 means *NR4A3's site did
  not open here*, not *this protein is undruggable*.
- Any statement about binding, reactivity, degradation, efficacy or safety.

**Decision-relevant either way, which is why it was worth running:** if the paralogues open an equally
druggable cavity, Route A's shape-based selectivity premise is in serious trouble and the covalent axis
becomes the whole argument. If they do not, Route A gains its **first paralogue-matched evidence**.

## 4 · Refusals are recorded, not scored

CLAUDE.md §4: *an absent reading is not a reading of absence.* A frame whose PDB cannot be read, whose
numbering cannot be mapped, or on which fpocket fails is counted in the JSON's `refusals` with its reason and
is **excluded from `n_propagated`** — it is never folded into a detection fraction as though the detector had
looked and found nothing. Both denominators are reported per row (`detection_fraction`,
`frac_ge_among_detected`, `frac_ge_among_propagated`), and `n_frames_found` / `n_refused` sit beside them, so
a row where the collector could not read the data is visibly different from a row where the pocket did not
open.

The **metadynamics** subsets are biased along the opening CV. They are reported separately, flagged
`biased: true`, and **never pooled** with the unbiased release frames — they are an adversarial upper bound
on how far each species' pocket can open, exactly as `nr4a-paralogue-dynamics.json` already treats them.

## 5 · The reference point the contrast is read against

NR4A3's committed harmonized table — `af2_static`, `calibration_nr4a3`, `8xtt_20conformers`, `metad_frames`,
`release_rep0/1/2`, `release_unbiased_pooled` — has its **one home** in
[`nr4a3-pocket-reharmonize-summary.json`](./nr4a3-pocket-reharmonize-summary.json). The row that anchors the
detector to something experimental is `8xtt_20conformers`: the **8XTT NMR ensemble**, scored with no
simulation bias applied. That is the in-repo known-answer anchor for "does this detector find a real cryptic
site without inventing one", and the paralogue arms go through the identical pinned build and `match_params`.

## 6 · What it returned

Numbers live in [`paralogue-pocket-contrast.json`](./paralogue-pocket-contrast.json) and are not restated
here (rule 1):

| read this | where |
|---|---|
| the per-species, per-subset table, both denominators | `rows` |
| the readout with **both** error bars, and which is honest | `contrast` |
| the verdict and the roadmap edits it requires | `map_edits_required` |
| did this run reproduce the committed NR4A3 table, cell by cell | `committed_nr4a3_reproduction_check.verdict` |
| frames the detector could not read | `refusals` (and `n_refused` per row) |

★ **The reproduction check is what licenses the contrast.** The NR4A3 arm re-scored here reproduces the
committed table **cell for cell** across every ensemble. That, not a matching `fpocket_version` string, is
the evidence the detector behaved identically — `fpocket -h` prints the banner `fpocket 4.0` whatever
conda-forge build is installed.

⚠ **Detection and druggability are different answers and must not be collapsed.** A high detection fraction
in a paralogue says the homologous site *exists and is findable*; the `≥ D*` fraction is the one that speaks
to druggability. And where the pooled Wilson interval and the per-replicate range disagree, **quote the
replicate range** — the 75 pooled frames are three correlated replicas, so the Wilson interval is
anti-conservative. `contrast.*.verdict_basis` states which bar the verdict used.

---

*Produced by [`paralogue_pocket_contrast.py`](./paralogue_pocket_contrast.py) via
[`.github/workflows/categorical-decoy-null.yml`](../../.github/workflows/categorical-decoy-null.yml).
Driver logic is unit-tested in [`tests/test_categorical_decoy_null.py`](./tests/test_categorical_decoy_null.py).*
