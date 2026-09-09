---
id: DOC-OPUS-CAMPAIGN-VIEWS-REGEN-1
title: "VIEWS-REGEN-1 — what regeneration of systems/views/ actually produces, and the two stale sites it does not fix"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# VIEWS-REGEN-1 — regeneration of `systems/views/`, measured

## Question

Commit `6466168d7` (TD1 R1–R4) changed `systems/graph/publications.json` and the RT-chaperone
route fields; the generated views were last written at `a6a21fc59`. **Exactly what does
regeneration produce, and does regeneration alone remove both the TD1-driven staleness and the
pre-withdrawal fusion-partner text that FUSION-PARTNER-2 found?**

## Merit

`systems/views/L3-publications.md` currently prints a withdrawn pooled prognostic magnitude
("7/15 = 46.7% … a magnitude this contrast has never had") as a live claim, contradicting the
corrected `publications.json` in the same repository. A reader navigating the model surface is
handed a withdrawn number. The generated-view contract (`systems_check.py` module docstring)
promises exactly that this cannot happen without failing the build; establishing whether the
promised mechanism fully repairs it, and where it does not, is what tells the coordinator whether
regeneration is sufficient or whether a graph edit is also required.

## Evidence gap this closes

Two lanes named the regeneration need, and FUSION-PARTNER-2 named three stale line numbers, but
nobody had run the generator and diffed the result. The unknown was whether the stale prose is
*derived* (fixed by regeneration) or *stored elsewhere in the graph* (survives regeneration).
It is both, and the split is the finding.

## Step taken

Ran the repository's own generator against the committed graph, rendering into this lane only.

### The generator — read, not guessed

`systems/systems_check.py` ("The EMC systems model — invariant checker and view generator").

* Regenerate: `python3 systems/systems_check.py --write-views`
* Check mode: `python3 systems/systems_check.py --check` — `check_views()` re-renders every view
  **in memory** and compares it to the committed file; a mismatch is `ERROR [G2]`, exit 1.
  `--no-view-check` skips that comparison; `--json` gives machine-readable findings.
* Renderer entry point: `all_views(g)` over `derive(load_graph())`; `write_views(g)` writes each
  key of that dict under the module-level constant `VIEWS = systems/views`.
* Dependencies: `jsonschema` + `pyyaml`, both present. **No network. It runs fully offline.**

`write_views()` has no output-directory argument, so calling it would have written over the tracked
tree. This lane therefore imports the module and calls `all_views()` directly, writing the returned
bodies into `regenerated/` — the generator's own rendering functions, unmodified, with no guard
touched. Driver: `regen_to_lane.py`.

## Artifact

* `regenerated/` — all **111** views as the committed graph renders them (2026-09-09T01:33Z).
* `views-regen.patch` — **UNAPPLIED** unified diff, committed views → regenerated, 11 files.
* `views-regen.diff.raw` — same content with absolute paths, for reading.
* `hash-table.md`, `regen_to_lane.py`, `checks/01..05`.

## Validation

| execution | exit code |
|---|---|
| `checks/01-regen-into-lane` — render 111 views into lane | **0** |
| `checks/02-diff-all` — `diff -rq systems/views <lane>/regenerated` | **1** (11 files differ) |
| `checks/04-git-apply-check` — `git apply --check --verbose views-regen.patch` | **0** |
| `checks/05-systems-check` — `python3 systems/systems_check.py --check` | **1** |

`--check` reports **exactly 11 `ERROR [G2]`** view-drift errors, naming the same 11 files the diff
finds — independent corroboration of the diff. (That run also reports 5788 ERROR and 271 WARN in
total; the other 5777 are pre-existing findings in unrelated invariants, outside this lane's scope
and untouched.) The tracked tree was verified clean for `systems/` before and after every step
(`git status --porcelain systems/` empty). **No file under `systems/` was written.**

## What regeneration produces — per file

| file | bytes before → after | sha256 before | sha256 after | changed lines |
|---|---|---|---|---|
| `L2-rt-b7h3.md` | 9376 → 9403 | `0a35fdf44caa1aa72fe516a4d6418b34c60494ed2c156e3ff68385f9260c8eb6` | `deac2ef9119d18b2e47fd0aae5c3237193e390002ef3cd685b6f8e503dd36d64` | 1 |
| `L2-rt-cart-surface.md` | 10164 → 10191 | `ae26ed02af6c8848a1ba70c198e12b2dd6367e3ca8056f2179d24bc5cb331de9` | `1e2adec34cb62514919aa33da649bd03bc907c0fed457cdef9dae0b0f233291b` | 1 |
| `L2-rt-chaperone.md` | 9830 → 9973 | `115ab8f2422e57c9c0c7eab13e479542737d3aad981c41a4cd7a6c00438b35fb` | `d09af9e2098333b767a319c8b7660eb55564c81d3ecca65fcc7dbe5927af0423` | 2 |
| `L2-rt-fap-rlt.md` | 10136 → 10163 | `504ad4ef864df2ed8f6dbc739c5afc01e01b5a005d32afe9e357d339f58dc03a` | `345943c0742546e32fce5ae304dec174b1010a98b3d22a028fe4a9147ff6e40c` | 1 |
| `L2-rt-partner-strat.md` | 20690 → 23160 | `3b2d2883985f50f88a35242f789bbcc6f33877503f83081a7d304906cc35abc5` | `20b77962162d00636ce595c79181a114d72ea6607b512a01a87f44ef2fbc511c` | 1 |
| `L2-rt-prame-immtac.md` | 10395 → 10422 | `58aece07657486bd487cb43c490a2bc2ec13e2516a69cde3af44a55487afa9fd` | `fd5da74638d469d5e068749266439c80a117d6afabb34a384fccea49059b2c4c` | 1 |
| `L2-rt-sstr2.md` | 9946 → 9973 | `3979674f5f93e7cf43c93612b7c32abec8d8a9b66f6fb4302d15251344124b11` | `50ad19228364809647b6ea12eb2f27bc53ebe35b269372d166e73eb515e1c758` | 1 |
| `L2-rt-tcip.md` | 15003 → 18545 | `9995a6b12d540cc979499c32cb61df3bf475d6f9b34e95cacf6bccf9fbd4a3aa` | `027d0717a71f25105bb167943be690d2719c5887ffa2511b57f6848387a4a9d3` | 2 |
| `L2-rt-tcrt-cta.md` | 9501 → 9528 | `5b3b8b274d34b3cb2188208fc233f8e4d9fda9c7f3fe00e83e07184ef7e0b4ba` | `aad15f2e9c627cd3cae1ef51070d34fbf156ca20b93e680c06ba70045e64ca28` | 1 |
| `L2-rt-txn-cdk.md` | 8671 → 8814 | `16ebc2fe88be9e40c7f09c79f465404ed850b6276912dc3c2e6632b07f7737ee` | `adb663c016e7a29e8bc2cf8b538a7429e1a1abab24165e44014b8c31094c1d80` | 2 |
| `L3-publications.md` | 97109 → 103293 | `aede90aaafcb77ed872f068fecb7c3afee28a56cd8adf39edd2396b9e30978a5` | `100bbefee20ecaeaa6a79440d5258b9c939fd975ff9008370aab3ee2bd057cad` | 8 |

**42 changed lines in total.** They are of three kinds:

1. **PUB-SURFACE-TARGETS title change** (7 files: `L2-rt-b7h3`, `L2-rt-cart-surface`,
   `L2-rt-fap-rlt`, `L2-rt-prame-immtac`, `L2-rt-sstr2`, `L2-rt-tcrt-cta`, plus the
   `L3-publications` index row): "…a lineage-surrogate ranking **tested against** three
   tumour-tissue cohorts" → "…**an archival comparison of** a lineage-surrogate ranking **with**
   three tumour-tissue **transcript** cohorts". A retired efficacy-flavoured verb.
2. **TD1-driven** (`L2-rt-chaperone`, `L2-rt-txn-cdk`, `L3-publications`): PUB-TXN-DEPENDENCY's
   title and claim are replaced by the corrected two-unpaired-streams text carrying the
   2026-09-08 F1 correction. Also PUB-TCIP's title and claim (`L2-rt-tcip`, `L3-publications`),
   the 2026-09-08 narrowing to a toolchain audit.
3. **Fusion-partner withdrawal** (`L2-rt-partner-strat` line 113, `L3-publications` line 236):
   the pre-withdrawal paragraph — including "a magnitude this contrast has never had" — is
   replaced by the corrected descriptive claim with its WITHDRAWN 2026-09-08 list.

## The answer — regeneration fixes most of it, and two sites survive

**Fixed by regeneration alone:** `L3-publications.md` line 236 and `L2-rt-partner-strat.md`
line 113, both of the sites FUSION-PARTNER-2 flagged as carrying the withdrawn endpoint paragraph,
plus every TD1-driven staleness.

**NOT fixed — and this is the finding.** `L2-rt-partner-strat.md` line 62, the third site
FUSION-PARTNER-2 named, **regenerates byte-identical and is still wrong**, and a second site beside
it does the same:

| surviving site | graph field it is rendered from | withdrawn content it still prints |
|---|---|---|
| `systems/views/L2-rt-partner-strat.md` **line 62** (and identically at `regenerated/L2-rt-partner-strat.md:62`) | `systems/graph/routes.json` → `RT-PARTNER-STRAT.remaining_unknowns[3]` | "the crude two-cohort magnitude that landed 2026-08-08 (disease-specific death 46.7% TAF15 vs 10.3% EWSR1)" — the pooled magnitude WITHDRAWN 2026-09-08 as unverified Huang 2023 Table 1 input |
| `systems/views/L2-rt-partner-strat.md` **lines 94 and 97** | `RT-PARTNER-STRAT.readiness.why_not_higher` and `readiness.missing[0]` | line 94 still rests the readiness argument on the pooled two-cohort base; line 97 states "a zero-event arm yields no magnitude at any denominator", which the same withdrawal records as **mathematically false** |

**Cause — not a hard-coded template.** `render_l2()` derives every one of these strings from the
route object: `remaining_unknowns` at `systems_check.py` render_l2 body (`"## Remaining unknowns"`),
`readiness` at (`"## Readiness — what this could become today"`). No prose is hard-coded in the
renderer. The withdrawal was applied to `publications.json` (title, claim) and propagated correctly;
it was **never applied to `RT-PARTNER-STRAT`'s own `remaining_unknowns` and `readiness` fields in
`routes.json`**. Regeneration is therefore faithful and still wrong: **the view is not stale, the
graph is.** `RT-PARTNER-STRAT.closure_note` carries the same withdrawn "73 patients … 6/58" text
but is not rendered into any view (the route has no `closure_kind`), so it is a latent, not a
printed, defect.

**Consequence for the coordinator:** applying `views-regen.patch` is necessary and clears the 11
`[G2]` errors, but it is **not sufficient**. A separate graph edit to
`systems/graph/routes.json → RT-PARTNER-STRAT` (`remaining_unknowns`, `readiness`, and
`closure_note` for consistency) is required, after which the views must be regenerated **again**.
Applying the patch first and editing the graph later would leave the tree green at neither point;
the graph edit and a fresh `--write-views` are one unit of work. This lane may not make that edit
(the graph is out of lane) and does not propose its wording.

## Provenance

Inputs re-hashed at time of use, 2026-09-09T01:33Z, tracked tree clean for `systems/`:

* `systems/graph/publications.json` sha256 `fc55087c5de17c4fd5044dc7b87b9718e33d2b1c99d72c21c55d95dc0855d526`
* `systems/graph/routes.json` sha256 `17d208e48c7901eeb01c64a16a415bb1f56a6ce729dfd05846c3b5e0e25f3d3b`
* `systems/graph/*.json` last changed at `6466168d7`; `systems/views/*` last changed at `a6a21fc59` — the staleness window.
* Generator: `systems/systems_check.py`, unmodified.

## Limitations

* The diff is of **generated output against committed output**. It is not a scientific review of
  the corrected claims, and this lane did not check the corrected `publications.json` text against
  its sources.
* The other 5777 `--check` errors are pre-existing, unexamined here, and may include further
  graph-level defects of the same shape as the one found.
* Only `RT-PARTNER-STRAT` was audited field-by-field for surviving withdrawn text. Other routes may
  carry stale free-text fields that regeneration equally cannot fix; the search here was scoped to
  the fusion-partner withdrawal strings.
* The patch is **unapplied by design**. It is validated by `git apply --check` (exit 0) against the
  tree as of the hashes above; concurrent lane writes to `systems/views/` would invalidate it.

## Stop condition

Reached. The question is answered with a measured diff, the surviving sites are named with file and
line and with the exact graph fields that feed them, and the patch is delivered unapplied with a
real `git apply --check` exit code. Nothing further in this lane without a coordinator decision on
the `routes.json` edit.
