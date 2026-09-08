# TCIP — settlement of the parameter-analysis preprint

**Task:** TCIP, sole exclusive owner, admitted by root as execution. Disjoint from P-ST, P-CI, P-AB,
TD1 and both frozen reviews. Settled 2026-09-08.

**Disposition: FROZEN FOR ONE FINAL SCIENTIFIC REVIEW.** Not parked. No essential unsupported result
blocks the paper: every load-bearing quantity in the main text and SI was re-derived from the retained
enumeration, the retained structural census and the sampler source, and all of them hold. The scope
defects found were real but reparable in prose, and they are repaired. Two residuals are recorded below
for the final reviewer and for the artifact's owner; neither is a missing measurement.

---

## 1 · Intake

Confirmed as ordinary intake, no separate audit:

| file | bytes | sha256 |
|---|---|---|
| `research/manuscripts/tcip/tcip-induced-interface-preprint.md` (as received) | 26,984 | `3dbac6e82df765fe9bda6d17080d1d1764d4abfca5f52b4c9e189854b25d233e` |
| `research/manuscripts/tcip/tcip-induced-interface-preprint-si.md` (as received) | 14,116 | `ac387cbf8af6451771a382b8ff6ba7798c6f230fff44c92fe9ba689949a41814` |

Both match the stated identity for the main; the SI is the existing companion at the same path.
Post-settlement hashes and the full dependency set are in [`HASHES.txt`](./HASHES.txt) and
[`MANIFEST.md`](./MANIFEST.md).

## 2 · What was re-derived, and against what

No new computation, no coordinates fetch, no producer run, no figure producer, no threshold. Every
check reads a committed artifact or the sampler source. Each attempt is retained in its own file under
[`checks/`](./checks/), failures included (`CHECK-04` is a failed schema assumption, superseded by
`CHECK-05`; it is kept, not overwritten).

| quantity as printed | source | check | result |
|---|---|---|---|
| 0.896 / 1.121 / 1.254 and the three pooled pairs | `nr4a3-tcip-reach.json → ★_interface_floor_ablation` | `CHECK-01` | exact |
| per-arm ablation table (SI §S5) | same block, `per_arm` | `CHECK-01` | exact, all six arms |
| 8-rung ratios 0.928…0.972, contrasts, CI overlap at 2 rungs | `★_paired_body_size_comparison` | `CHECK-02` | exact |
| 0.858–0.972 span, 0.877 at the gate, within>between 8 of 8, 1.421× vs 1.165× | same + `verdict.★_the_size_axis` | `CHECK-02` | exact |
| `birc2` outperforms `crbn` at every rung; 13× smaller | `per_arm_acceptance_rate`, `body_geometry` | `CHECK-02`, `CHECK-10` | holds at 8/8; 1183/92 = 12.9 |
| 22 entries, class table S1 | `nr4a3-induced-interface-census.json → summary_over_induced_pairs` | `CHECK-03`, `CHECK-19` | exact; 22/22 status OK |
| 9MZA 6/7 and 7/6, 4 residues per side, both copies | census `entries[9MZA].chain_pairs` | `CHECK-05` | exact |
| BCL6 BTB 66/71 in 9MZA, 64/67 in 7LWG | same, and `entries[7LWG]` | `CHECK-05`, `CHECK-06` | exact |
| truncation control: 122–123 / 112–113 residues, 244–246 / 224–226 points | same | `CHECK-05` | exact |
| ligand 81 heavy atoms, contacts 33–42 atoms per partner | `entries[9MZA].ligands` | `CHECK-05` | exact (33, 42, 33, 40) |
| the 15 degrader pairs, in order; 6 of 15 in ≥1 direction, 1 in both | census, recomputed from the pairs | `CHECK-06` | exact, row for row |
| 6SIS split (10/11 fails, 13/16 clears), 6HAX 11 both copies, 5T35 10–11 | same | `CHECK-06` | exact |
| exit exposures 5.44 / 5.04 / 13.65 / 5.11 / 5.79 / 5.00, range 5.00–5.79 | `cross_checks.exit_vector_comparability` | `CHECK-15` | exact |
| `min_contact_residues = 12` and its comment; no derivation recorded | `nr4a3_basin_search.py:119` | `CHECK-07` | exact, verbatim |
| §6: counts points not residues; two points per residue; three-band `if/elif` | `nr4a3_basin_search.py:460–473, 590–607` | `CHECK-08`, `CHECK-09` | exact |
| Appendix A: `G.centroid(side)`, CA fallback for glycine, despite the name `cb` | `nr4a3_basin_search.py:473` | `CHECK-08` | exact |
| S7 sweeps: 100/20, 300/51, 31, 6, zero counts, `cooperativit*` once twice | `tcip-interface-floor-sizing.md` §3(a), §3(a′) | `CHECK-18` | exact |
| Appendix B: `_exptl.method` is `_details ?` for 9MZA only; 2.1 Å parsed | census entry, all 22 methods | `CHECK-05`, `CHECK-19` | exact; every other entry reads X-RAY DIFFRACTION |
| Appendix B: RCSB term searches returned zero; the X-ray quote | `tcip-interface-floor-sizing.md` §3(b)–(c) | `CHECK-18` | exact, quoted verbatim there |
| Appendix A(1): not registered in `pinned-figures.json` | `pinned-figures.json` | `CHECK-19` | confirmed — zero TCIP entries |
| 576 cells; 0.894 at 40 000 vs 0.896 at 30 000 | `paired_placement_envelope.cells`; route memo §4 line 216 | `CHECK-19` | exact |
| §8: no figure rendered | filesystem search for TCIP figures and producers | `CHECK-39` | confirmed — none exists |

**Nothing was found wrong with a number.** The paper's arithmetic and its attributions are sound.

## 3 · What was repaired, and why

Four scope repairs. All are prose; no quantity moved.

**(a) The abstract asserted as fact the justification §1 calls a reconstruction.** The abstract read
"The parameter **is** a degrader's requirement — a PROTAC must build a cooperative target·E3 interface
across which ubiquitin is transferred", while §1 already said that reading "is our reconstruction of the
intent, not a justification the source states". The source records a comment and no derivation
(`CHECK-07`). The abstract now states the checkable fact — the parameter's only committed provenance is
a degrader-recruitment sampler — and marks the mechanistic reading as reconstruction. This is the
⛔ undocumented-provenance trap, and it was live in the abstract only.

**(b) §1 generalised from one sampler to a class of samplers.** It read "Rigid-body proximity samplers
score a candidate placement on excluded volume plus a minimum induced interface." No survey of other
samplers exists in this package. §1 now scopes the sentence to the sampler examined and adds the
boundary explicitly: the inheritance documented is a property of one toolchain — `nr4a3_tcip_reach.py`
taking its scoring unchanged from `nr4a3_basin_search.py`, which is itself checkable — and not a
measured feature of the field.

**(c) The operational-filter/biological-requirement distinction was implicit, not stated.** §5 now opens
by stating it: the floor of 12 is the criterion by which one sampler admits or rejects a candidate
placement, every "fails the floor" means *would be rejected by this predicate* and never *is too small
to work*, and the threshold selected the cases rather than testing them. §1 carries the same statement
where the parameter is introduced.

**(d) Two pieces of existing artifact content were brought into the SI as warranted.** Table S1 now
carries the ligand-bridged / `allosteric_curated` split the artifact holds and that §S2 promises a
reader can act on — material for `induced_transcriptional`, where 10 of 12 pairs are curated by name;
the two rows the manuscript's claims rest on carry none. And §S1 now discloses the artifact's
`cross_checks.replicates_the_committed_E3_acceptance`, whose `status` reads **DISAGREES** (19 of 24
committed rates inside the recomputed 95 % interval, 5 outside against 1.20 expected), reported at its
own status rather than at the artifact's softer gloss, with the reason it does not touch any number
here: every contrast the paper reports is computed within a single pass, so a level offset between runs
cancels; the paper reports no absolute acceptance rate across the two runs.

Metadata: `last_verified` moved 2026-08-07 → 2026-09-08 in both files, which is what that field means —
someone read the document and checked it is still true. `date` is unchanged.

## 4 · Distinctions preserved, checked one by one

- **0.896 / 1.254** — present, at their own sample budget, with the 0.877/0.896 estimand-versus-budget
  note left intact (§2a).
- **6–7 contacts, n = 1 system, one crystal form** — present in the abstract, §3, §5.1 and SI §S9; the
  "two crystallographically independent copies are not two systems" clause is intact.
- **Contact-point versus residue units** — never silently converted. §6 reports both readings and
  declines to resolve them; §3's headline is "6–7 contact points across 4 residues per side"; Table S1's
  column is labelled in points; the SI's ⚠ block states 12 points is as few as 6 residues.
- **The within-class caveat** — intact in the abstract, §2a and SI §S5, with the "may not be reported as
  a size law" conclusion and the excluded arms named.
- **The search-limited census** — every absence claim is scoped to the search that produced it (§3, §5a,
  Appendix B), and none is stated as global. Verified sentence by sentence in `CHECK-39`'s diff context.

No new interface, construct or geometry computation; no coordinates fetch; no prediction; no new
threshold; no biological claim; no figure producer; no efficacy, safety, selectivity, therapeutic-window
or clinical-readiness claim; no `systems/graph/` edit; the FP paper and the MF1 methods record untouched;
no commit and no push.

## 5 · Checks — real exit codes, every attempt retained

| check | file | exit |
|---|---|---|
| repo-mode `lint_consistency` (before) | `checks/CHECK-21-BEFORE-lint_consistency-repo.txt` | 0 — 0 ERROR / 29 files |
| repo-mode `lint_asymmetry --report` (before) | `checks/CHECK-22-BEFORE-lint_asymmetry.txt` | 0 |
| repo-mode `lint_citations --report` (before) | `checks/CHECK-23-BEFORE-lint_citations.txt` | 0 |
| `lint_submission_residue --report` (before) | `checks/CHECK-24-BEFORE-lint_submission_residue.txt` | 0 — 0 NEW |
| gate-mode `lint_style` (before) | `checks/CHECK-25-BEFORE-lint_style-gatemode.txt` | 1 — 15 ERROR, all on `surface-targets/*` (P-ST lane); TCIP is not a target |
| gate-mode `lint_claims` (before) | `checks/CHECK-26-BEFORE-lint_claims-gatemode.txt` | 0 — 0 ERROR, 179 WARN |
| explicit-path `lint_style` on the two files (before) | `checks/CHECK-20-BEFORE-lint_style.txt` | 1 — 42 bold-midsentence + density, see residual R3 |
| explicit-path `lint_claims` on the two files (before) | `checks/CHECK-20-BEFORE-lint_claims.txt` | 0 |
| four lints invoked with the wrong interface (before) | `checks/CHECK-20-BEFORE-lint_{consistency,asymmetry,citations,submission_residue}.txt` | 2 — usage error, retained as the failed attempt it was; re-run correctly as CHECK-21…24 |
| `lint_consistency` (after) | `checks/CHECK-30-AFTER-lint_consistency.txt` | 0 — 0 ERROR / 29 files |
| `lint_claims` (after) | `checks/CHECK-31-AFTER-lint_claims.txt` | 0 — 0 ERROR, 179 WARN, unchanged |
| `lint_style` gate mode (after) | `checks/CHECK-32-AFTER-lint_style.txt` | 1 — same 15, still zero on TCIP |
| `lint_asymmetry` (after) | `checks/CHECK-33-AFTER-lint_asymmetry.txt` | 0 |
| `lint_citations` (after) | `checks/CHECK-34-AFTER-lint_citations.txt` | 0 |
| `lint_submission_residue` (after) | `checks/CHECK-35-AFTER-lint_submission_residue.txt` | 0 — 0 NEW |
| `pytest test_induced_interface_census.py test_nr4a3_tcip_reach.py` | `checks/CHECK-36-AFTER-pytest-tcip-modules.txt` | 0 — **28 passed**, none skipped, none deselected |
| `systems_check` (after edits, before the frozen-copy rename) | `checks/CHECK-37-AFTER-systems_check.txt` | 1 — 2621 + 25 duplicate-id/link errors my own `.md` evidence copies created |
| `systems_check` (after the rename) | `checks/CHECK-38-AFTER-systems_check-rerun.txt` | 1 — **2621 ERROR, zero of them naming this package**; the live TCIP files produce no error of their own |

⚠ `systems_check` exits 1 on a repo-wide pre-existing 2621-error state driven by other lanes' evidence
copies; that is not a TCIP result and this task did not touch it. What is a TCIP result: after the
rename, no error line names `TCIP-settlement/`, and the only error naming the live manuscript is a
duplicate-`id` [D6] caused by TC1's two retained evidence copies, which predates this task.

The frozen copies are stored as `.md.txt` for exactly that reason — byte-identical to the `.md` they
copy (the hashes in `HASHES.txt` prove it), but skipped by the frontmatter scanner, so retaining this
package costs the shared gate nothing. Bytes and hashes are the retention obligation; the extension is
not.

`PREFLIGHT_FULL` was not run: this is a preprint draft that is not submitted and not posted, no commit
is being made from this lane, and the parent integrates.

## 6 · Residuals — routed, not repaired here

**R1 — the title generalises where the body now does not. For the final reviewer to rule on.**
The title reads *"The induced-interface floor that **proximity design** inherits from degraders…"*. The
evidence is one sampler and one toolchain. The abstract's opening and §1 now both scope the inheritance
explicitly, so the body is correct and the title is a framing that runs ahead of it. I did not retitle:
the framing has survived three prior hardening rounds, a title change propagates to the SI title, the
frontmatter of both files and PUB-TCIP's entry in the publications view, and this is a judgement a
reviewer should make once rather than a fourth prose rewrite. **If the reviewer wants it scoped, the
minimal change is "that a proximity sampler inherits from degraders".**

**R2 — `nr4a3-tcip-reach.json` contradicts itself about named effectors. Routed to the artifact owner.**
`verdict.★_the_named_effector` reads `status: NO_NAMED_EFFECTOR_STAGED`,
`n_named_effectors_enumerated: 0`, `answer: "NOT ASKED — none staged"`, while the top-level
`★_named_effector` block holds both staged arms with full per-rung data. The manuscript's §5.5 reads the
populated block, and that block is corroborated independently by `body_geometry` and by
`per_arm_acceptance_rate` (`CHECK-10`, `CHECK-02`), so **the manuscript is right and the verdict field is
stale.** Repairing it means editing or re-running a producer, which is outside this task's fences. SI §S1
now discloses the contradiction and names the block actually used. **Reopening condition:** the artifact's
owner re-runs `nr4a3_tcip_reach.py` or corrects the verdict block, after which the SI note can be reduced
to a sentence.

**R3 — TCIP is not covered by `lint_style`'s gate-mode target list.** Run explicitly, the main text is at
bold 25.7/1000 with 42 bold-midsentence findings. That is a style-coverage gap for the register's owner,
not a scientific defect, and I did not chase it: a de-bolding pass over this file is exactly the kind of
rewrite that drops a hedge, and the emphasis here is load-bearing on the numbers a reader must not skim.
Recorded alongside the existing `pinned-figures.json` gap the paper already discloses in Appendix A(1).

**R4 — the six figures remain specifications.** §8 states plainly that nothing in its table has been
rendered, and the filesystem confirms no TCIP figure or figure producer exists (`CHECK-39`). No image was
invented. This is disclosed, not hidden, and stays a publication-time decision for the paper's owner.

## 7 · What a final reviewer should decide

1. R1 — the title.
2. Whether §5's new opening paragraph belongs there or higher, given that the operational-filter
   distinction is the paper's central discipline.
3. Whether the SI's new DISAGREES disclosure (§S1) is at the right strength — it reports a status the
   artifact itself glosses more softly, and argues the flag cannot reach any reported number.
4. Nothing else: no quantity is unresolved, and no measurement is missing.
