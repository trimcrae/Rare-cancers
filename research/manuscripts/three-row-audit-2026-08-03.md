# Three-row audit — §10 rows 3, 6 and 7 (2026-08-03)

**$0 throughout.** Free CI + committed artifacts + read-only S3. No GPU, no rental, nothing to tear down.

**Machine-readable map edits:** [`three-row-audit-map-edits.json`](three-row-audit-map-edits.json) →
`map_edits_required`. Every `current_text` there was `grep -F`-verified against `origin/main` at the end of
this session. **Do not re-type any number from this page into the map** — each edit's `artifact` field names
the file that owns it (invariant 6 / CLAUDE.md rule 1).

| row | serves | outcome |
|---|---|---|
| **3** | `R3` | ✅ **RESOLVED — and the submission gate FAILS.** The generation frame is named and scored; it does **not** clear D\* under the harmonized criteria |
| **6** | `V5` | ✅ **RESOLVED.** The $0 pose diagnostic ran for the first time; the pre-registered prediction is upheld and LANE 20's hold is discharged |
| **7** | `R11` | ⚠ **PARTIAL — and the brief's premise is superseded.** Arm F **is** already classified (⏸ parked, map §6b). What is outstanding is a *decision*, which is trimcrae's. **New finding:** the reopening trigger has no rung, no gate and no price anywhere in the program, and the board item that resembles it calibrates a **different quantity** |

---

## ROW 3 — `R3`, the frame-level generation-receptor dependency audit

**Verdict: `GATE_A_FAIL_BELOW_DSTAR`.** One home for every number:
[`r3-generation-frame-harmonized.json`](../modalities/r3-generation-frame-harmonized.json) (the score) and
[`r3-generation-frame-audit.json`](../modalities/r3-generation-frame-audit.json) (the identity + the
coverage proof). Code: [`r3_generation_frame_audit.py`](../modalities/r3_generation_frame_audit.py),
[`r3_score_generation_frame.py`](../modalities/r3_score_generation_frame.py), 15 tests in
[`tests/test_r3_generation_frame.py`](../modalities/tests/test_r3_generation_frame.py). Job:
[`r3-generation-frame-audit.yml`](../../.github/workflows/r3-generation-frame-audit.yml).

### F3.1 · The generation frame is NAMED

`nr4a3-release-druggable.pdb` = the **unbiased release replica 0, frame 95**, CV Rg **0.7367 nm**.

The identity chain is the generator's own receptor loader, not a prose summary: `nr4a3_denovo.py` loads that
PDB from the Step-0 receptor directory (*"the thermally-real, breathing, induced-fit pocket — NOT the
biased-metad frame"*), the red-team's F16.1 quotes the same lines, and the paper anchors *"all downstream
design"* to it. The `(rep, frame)` pair lives in the S3 manifest
`s3://sagemaker-us-east-2-646605541856/nr4a3-release-druggable/nr4a3-release-druggable.json` (3,862 B,
2026-06-29) — **not committed to this repo**, which is why this was an S3 read. The receptor PDB itself
(327,474 B) is still present, which is what made the score possible at all.

⚠ **The audit follows `selection_primary_receptor`, never `docking_primary_receptor`.** The manifest promotes
an alternate when the selection primary fails confirmation, and an alternate is a structure `denovo_401` was
never conditioned on. Here they agree; the guard is pinned by a test regardless.

### F3.2 · The harmonized rerun never scored it — a stronger statement than the paper's

The paper says the committed artifact *"reports **ensemble-level** fractions only and does not identify which
individual frames cleared D\*"*. True, and it understates the gap. `sagemaker_src/entry_pocket_reharmonize.py`
builds entries for exactly `af2_static`, `calibration_nr4a3`, `8xtt_20conformers`, `metad_frames` and
`release_rep0..2` (plus the pooled row). **There is no `release_druggable` entry** — although
`nr4a3_pocket_reharmonize.detection_from_result` implements that kind, and the redesign brief's own rerun list
ends with *"exact generation receptor frame"*. The generation receptor was **never an input to the rerun.**

⚠ **And a per-frame dump of `release_rep*` would still not be the missing measurement.** The generation
receptor is re-extracted and re-boxed into its own PDB and scored by its own fpocket call;
`nr4a3_release_druggable.py`'s `confirm_filter` states that the reused per-frame summary and the fresh
confirmation *"can disagree"* and that *"the **confirmed** score … governs"*. A trajectory-frame row is a
different measurement of a different object.

### F3.3 · Scored under the harmonized criteria — it FAILS

Same code path `nr4a3_mdpocket.druggability_timeseries` uses for every release frame, `POCKET_MATCH=harmonized`,
fpocket pinned to **4.2.3** (banner `4.0`, byte-identical to the string in the committed table, so this is
protocol parity and not merely a similar run), gate `jaccard ≥ 0.25 / frac_recovered ≥ 0.3 / centroid ≤ 8.0 Å`.

The mapped orthosteric site **is detected** — this is not a detection failure — and it is **not druggable**:

| | pocket | overlap | Jaccard | frac_recovered | centroid | druggability | gate |
|---|---|---|---|---|---|---|---|
| **the harmonized site** | **1** | **8/10** | **0.615** | **0.80** | **3.478 Å** | **0.259** | ✅ accepted |
| the legacy pick | 2 | 6/10 | 0.375 | 0.60 | 7.562 Å | 0.667 | ✅ accepted |

**0.259 against D\* = 0.53.** The frame does not qualify — and per the paper's own sentence, *"if the
generation frame does not qualify, the **generation receptor** — not merely a reported frame-fraction — is
affected."* `R3` is therefore answered, and answered against the program.

### F3.4 · The mechanism is the outcome-selection defect itself — stated at its honest strength

The pre-harmonized manifest recorded **0.667**, which is **exactly pocket 2's** score in this run. That is the
defect the harmonized rerun exists to remove, in the paper's words: *"the reference site was chosen as the
highest-**druggability** pocket in a residue window that is essentially the whole LBD, [so] the foundational
site identity is **partly outcome-selected**."* Caught on the single most load-bearing structure in the
program.

⚠ **But the weaker reading is the true one, and it must not be upgraded.** Pocket 2 **also clears** the
composite gate (2 of 15 cavities do). So this is **not** "the legacy classifier picked a cavity that is not
the site". It is: **two cavities both qualify as the site, and the score-independent rule prefers the
better-matching one — which is the less druggable one.** Pocket 1 wins on all three acceptance criteria
(more overlap, higher Jaccard, nearer centroid); druggability enters `pocket_tracking.match_pocket`'s
ordering only as a final deterministic tiebreak and never as an acceptance criterion.

⚠ **Consequence, stated rather than buried: this verdict is sensitive to the matching rule, and the redesign
brief asks for exactly that sensitivity** (*"sensitivity to matching thresholds"*). The defence against
"you chose the rule that fails it" is checkable and it holds: the rule and its three thresholds were **frozen
before this datum existed** — `nr4a3-conformer-panel.json` is stamped *"FROZEN 2026-07-11"* with these
thresholds, and the committed 8-ensemble table was produced under them. This measurement is 2026-08-03.
⚠ *Limitation: repo git history is shallow (one commit touches `pocket_tracking.py`), so precedence rests on
the artifact stamps above rather than on `git log`.*

### F3.5 · Two errata found on the way, neither of them mine to fix

1. **`nr4a3-redesign-provenance.json` transposes the two numbers.** Its `results[0].frame` reads
   *"release-derived design frame (**Rg~0.667** primary; 0.74 seed)"*. Measured: Rg is **0.7367 nm** and
   **0.667** is the pre-harmonized **druggability**. The field labels the druggability as the Rg.
2. **`nr4a3-conformer-panel.json` and `panel_select.py` misattribute `af2_static`'s row.** The panel's
   `sources_s3.af2` reads *"AF-Q92570 AF2-opened release frame (denovo_401 design frame; **0/1 ≥ D\***)"*,
   and `panel_select.AF2_ENSEMBLES` is commented *"the circular denovo_401 design frame(s)"*. But
   `af2_static` in the harmonized table is the **raw AFDB model**, fetched at runtime by
   `entry_pocket_reharmonize.py` via `nr4a3_structure.fetch_pdb('Q92570')` and scored by
   `nr4a3_fpocket_enumerate.py`, whose docstring says *"The AF2 model uses UniProt numbering"*. It is not an
   MD frame and it is **not the generation receptor** — which is release rep 0 frame 95, renumbered 1–254.
   Any reading of that `0/1` as *"the design frame fails D\*"* scores a different structure. **The design
   frame's real failure is F3.3, and it needed this measurement.**

---

## ROW 6 — `V5`'s pose diagnostic, `task=triangle-converge`

**RESOLVED. It ran for the first time, it is genuinely $0, and it took 5 min 45 s** (GH run `30775278345`,
00:47:03 → 00:52:48 AM ET, `ubuntu-latest`). Confirmed $0 by construction, not by assumption: the `launch`
job — the only one on this workflow that rents a GPU — excludes `triangle-converge` from its `if:`, so no
placement call is reachable. The lane's own map `ternary_vast_launch.CONVERGE_TASK_MODES` sends it to mode
`triangle` (2 fs, seed 0), leaving `task=converge` pinned to RUNG 2b's `edge` legs byte-for-byte.

**The pre-registered prediction is UPHELD.** The workflow's own frozen reading is *"Departure PRESENT → the
non-zero `R_binary` is attributable to it. Departure ABSENT → `R_binary` is ordinary path error and the
restrained re-run's rationale weakens."* Measured on the triangle's four legs:

| leg | replicas ending beyond 4.0 Å | contact_pose max / median (Å) | dominant class |
|---|---|---|---|
| `calib_hi_to_lo2__binary_vhl` | **10 of 12** | 12.103 / 5.389 | DISPLACED_AND_STAYED 7 |
| `calib_lo_to_lo2__binary_vhl` | **8 of 12** | 15.695 / 9.105 | DISPLACED_AND_STAYED 7 |
| `calib_hi_to_lo2__ternary_vhl` | 1 of 12 | 4.192 / 2.027 | STABLE 11 |
| `calib_lo_to_lo2__ternary_vhl` | **0 of 12** | 3.152 / 1.767 | STABLE 12 |

Against the two cycles on record (audit §L.3d, its one home): binary **8/12** at 2 fs and **7/12** at 4 fs,
both ternary arms **0/12**. The triangle's binaries depart at the same rate or higher; its ternary arms are
clean. **Departure PRESENT.**

Run mechanically rather than paraphrased, `valb_triangle_closure.binary_departure_prereg` on the landed
[`valb-triangle-reduction.json`](../modalities/valb-triangle-reduction.json) returns
**`BINARY_PATH_DEPENDENT`, `prediction_upheld: true`**, at `power_to_detect_r0_sized_effect: 1.0`.

**What this discharges.** LANE 20 — the restrained binary re-run — was *"HELD ON PURPOSE"* behind this
diagnostic, and the prereg forbade interpreting `R_binary` without it. Both holds are now released, and the
departure is attributable rather than assumed. The map's *"has still never run"* is superseded.

⚠ **Two things the run showed that nobody predicted, recorded so they are not lost.** (a) Three of the four
legs carry `tech_fail=True` while still returning complete pose series. (b) The `hi_to_lo2` **ternary** leg
shows **1 of 12** DISPLACED_AND_STAYED where both prior cycles' ternary arms were 0/12 — small, but the
ternary arm's cleanliness is load-bearing for the reading above, so it is stated rather than rounded away.
Neither is a blocker; both belong in the record.

---

## ROW 7 — Arm F of the NR-V04 retrospective

### F7.1 · Arm F is NOT unclassified — the brief's premise is stale

The live map **already classifies it**, in two places added 2026-08-03: §6b (⏸ parked, with the reopening
trigger named — *"a ternary alchemical free-energy method that **passes** the valB known-answer control"*)
and §6c (*"⏸ parked · ⛔ undecided"*). The *"UNCLASSIFIED, AND THAT IS THE FINDING"* wording traces to
[`map-merge-inventory.md`](map-merge-inventory.md) row 4, which predates that sweep. **That inventory row is
now stale and is a map edit below.**

### F7.2 · The ⏸ is correct under §0.2's strict bar, and ✕ is refused with evidence

The test is *"is there any future development that would make us retry this?"* — and the answer is yes, with
a concrete, already-measured route (F7.4). Nothing shows ΔΔG_coop **cannot** be computed. What failed is a
particular calibrator on a particular system: `V5` returned **−0.599** against a target of **+0.944**, wrong
sign in all three replicates. **A gate that cannot fire is a fact about the gate**; §6a already files the
*edge* rescope and the *P-series* rescope as ✕ on arithmetic, and neither reaches the arm.

⚠ **And it is not 🔒 held either**, on §6c's own test (*"could it run tomorrow if trimcrae said yes?"*).
It could not: `selectivity_resolution_options.py` records the blocker as *"valB calibration condition 7 —
**not a spend decision, a preregistration one**"*. A budget nod would not release it.

### F7.3 · What IS outstanding is a decision, and it is trimcrae's alone

Arm E got an explicit ruling ([Open decision 12](nr4a3-program-map.md#open-decisions)); Arm F never did. Per
§0.3's three axes, that is the **authorization/decision** axis, not the work state — and conflating the two is
why §10 row 7 reads as *"unclassified"* when §6b has classified it. The choice is: record it as **held with
its trigger** (the status quo, made explicit), or **retire it explicitly** with the reason on the record.
⚠ Both are legitimate; neither is mine to take. §10 row 7 stays open until it is taken.

### F7.4 · NEW — the reopening trigger has no rung, no gate and no price

This is the finding that makes the row more than bookkeeping, and it is the *"caveat with nowhere to go"*
pattern §10.3 exists to catch.

Arm F needs a **ΔΔG_coop** calibrator that passes. The board's nearest-looking item, §10 row 11 — *"a
known-answer calibrator for the `S`-shaped quantity"* — is **a different quantity**, in the program's own
words: [Open decision 9](nr4a3-program-map.md#open-decisions) states that *"valB_mini calibrated `ΔΔG_coop`,
a quantity `S` does not contain (its binary leg cancels algebraically)"*. Nothing else on §10 serves it —
row 19 (`valB_full`) is the object behind the same failed gate, row 12 closed on evidence, row 27 is the
ΔΔΔG searches. **So the named unblocker is unscheduled: it can be neither refused, nor costed, nor sequenced.**

**And its feasibility is already measured, at $0, and it is favourable.** [Open decision
6](nr4a3-program-map.md#open-decisions) closed the *edge* rescope and framed the successor as a **system**
question; [`s-calibrator-survey.json`](../modalities/s-calibrator-survey.json) then answered the structural
half. The valB calibrator's frozen template **8G1Q** is on the **SMARCA4** arm, and **8G1P** — same
deposition series, **2.7 Å** against 8G1Q's **3.73 Å** — is on the **SMARCA2** arm, with 6HAX / 6HAY / 9HYB
as three further SMARCA2 ternaries. The repo currently carries a **SMARCA4→SMARCA2 homology substitution**,
`R` localised the valB miss to *"the MODEL or REFERENCE DATA"*, and that substitution is exactly that class.
So a **structure-symmetric** re-run is buildable from deposits that exist today.

⚠ **Scoped honestly, three ways, because this is the kind of claim that gets over-read.** (a) The survey's
own words: these rows *"do NOT assert the entries are interchangeable"*, and `_does_not_supply_selectivity:
true`. (b) It is a **structural** screen — it says a real structure exists on both arms; it does **not** say a
suitable known-answer **cooperativity** exists for that pair, which is a separate, unrun search. (c) It does
**not** amend decision 9 and must not be read as doing so: decision 9 declined to amend the gate or decouple
module 3, and this is a route to *satisfying* the gate, not to loosening it. Decision 9's own warning — that a
calibrator on the same family carrying the suspected error is ambiguous — was about the **homology-substituted
arm**, which is precisely what 8G1P would remove.

---

## Verification

| check | result |
|---|---|
| `lint_consistency.py` | **0 ERROR** across 12 target files |
| `lint_claims.py` | **0 ERROR**, 50 WARN across 3 files (all pre-existing) |
| the fast six | **6/6 PASS** |
| `tests/test_r3_generation_frame.py` | **15/15 PASS** (new) |

## Refusals and limitations, collected

- **Row 7 is not fully resolved and cannot be by me** — it needs a decision only trimcrae can take (F7.3).
- **Row 3's verdict is rule-sensitive** and says so (F3.4); the precedence defence rests on artifact stamps,
  not on `git log`, because repo history is shallow.
- **Two errata (F3.5) are reported, not fixed** — `nr4a3-redesign-provenance.json`, `nr4a3-conformer-panel.json`
  and `panel_select.py` are outside this task's scope and may be held by other lanes.
- **The map itself was not edited.** Every proposed change is in
  [`three-row-audit-map-edits.json`](three-row-audit-map-edits.json), anchor-verified against `origin/main`.
