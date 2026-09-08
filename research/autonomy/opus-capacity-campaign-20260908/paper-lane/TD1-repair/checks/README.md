# TD1 repair — executed checks, every attempt preserved

⚠ **Every attempt is retained, failures included. Nothing was overwritten, and no exit code was
altered.** Exits below are the real exits of the real commands, recorded with each stream. A skipped
test is not recorded as a pass anywhere in this directory.

⛔ Scope of these checks: **focused source/text bindings and annotation numeric/membership invariance
only**. None of them executes a scientific producer, reads a raw biological matrix, performs a
reanalysis, acquires a source, or constitutes a publication gate or scientific clearance.

## What each script does

| script | purpose |
|---|---|
| `td1_source_bindings.py` | Binds every quantitative and membership claim in the repaired manuscript to the live artifacts (E, D, G, C, `fet-ddr-axis-scan.json`), and independently re-derives the conditional arithmetic — two-sided Student-*t* tail from the regularized incomplete beta, and the Δ ÷ *t* interval — from the same rounded published summaries, checking agreement with the **retained reviewer attempt-2 output** rather than assuming it. Numerically calibrated on the Cauchy identity (*t*=1, df=1 → *p*=0.5, error 7.8e-16). |
| `build_shared_patches.py` | Builds the six annotation-only shared-file patches. JSON structurally by field path with a byte-exact round-trip verified before editing; generator sources by bounded single-entry replacement guarded by an AST constant comparison. Leaves the working tree unchanged. |
| `verify_invariance.py` | Applies each patch to a pristine copy **outside** the repository, then walks original against patched asserting structure, every non-string leaf, and that every string change is a declared edit; plus named spot-invariants and generator/annotation agreement. |

## Attempt log

| # | command | exit | outcome |
|---|---|---|---|
| 01 | `python3 checks/td1_source_bindings.py` | **1** | ❌ `TypeError: 'NoneType' object is not subscriptable` — the eleven-gene proliferation control was looked for under `instrument_controls.proliferation_reference`, which is the **one-gene MKI67 group** that emits no score. Real defect in the check, corrected by pointing at `mtap_prmt5.proliferation_confound_control` and adding an assertion about the MKI67 group. |
| 02 | `python3 checks/td1_source_bindings.py` | **1** | ❌ 230 checks, 3 failed — two withdrawn phrases matched inside their own explicit negations, and one required phrase spanned a line break. Checker corrected (negation-scoped assertions, whitespace-flattened view); the manuscript was not weakened to pass. |
| 03 | `python3 checks/td1_source_bindings.py` | **1** | ❌ 232 checks, 4 failed — same class, one further negated phrase (`abundance and dependency disagree`, which survives only in "makes **no claim that** …"). |
| 04 | `python3 checks/td1_source_bindings.py` | **0** | ✅ 230 checks, 0 failed. |
| 05 | `python3 checks/build_shared_patches.py` | **1** | ❌ 16 problems — byte-literal replacement against JSON- and Python-escaped text was unreliable. Approach replaced with structural JSON editing. |
| 06 | `python3 checks/build_shared_patches.py` | **0** | ⚠ Exit 0 but **later found unsound**: the generator-source block replacement anchored on a non-unique marker and destroyed a span of `census_route_expression_grading.py`. Caught by attempt 07. **Retained as a failure of judgement that a passing exit did not reveal.** |
| 07 | `python3 checks/verify_invariance.py` | **1** | ❌ 4 failures — three generator literals no longer matched the displayed annotation (the attempt-06 clobber), and E's duplicate copies of two strings had not moved together. |
| 08 | `python3 checks/build_shared_patches.py` | **1** | ❌ `NameError: py_literal is not defined` after the rewrite. |
| 09 | `python3 checks/build_shared_patches.py` | **1** | ❌ both patched generator sources failed to parse — the last entry of a dict block swallowed its closing brace. |
| 10 | `python3 checks/build_shared_patches.py` | **0** | ✅ patches build; entry-end detection now dedent-aware. |
| 11 | `python3 checks/build_shared_patches.py` | **0** | ✅ rebuilt after adding E's three duplicate string copies to the edit plan. |
| 12 | `python3 checks/verify_invariance.py` | **0** | ✅ 441,596 checks, 0 failed. ⚠ Its report file was 95 MB; the checker was changed to emit category counts plus all failures, and to reconstruct patched bytes by **applying the patch** rather than storing large copies. |
| 13 | `python3 checks/verify_invariance.py` | **0** | ✅ 441,602 checks, 0 failed, patches applied out-of-tree. |
| 14 | `python3 checks/build_shared_patches.py` | **0** | ✅ final build; stores patches only. |
| 15 | `python3 checks/verify_invariance.py` | **0** | ✅ final: 441,602 checks, 0 failed. |
| 20 | `python3 research/manuscripts/lint_{claims,citations,citation_types,style,asymmetry,consistency,readability,submission_residue}.py <manuscript>` | 1, **2**, **2**, 1, **2**, **2**, 0, **2** | ⚠ The five exit-**2** results are **my own CLI errors**: those five tools take no path argument. They are the same mistake recorded historically in this lane and are preserved as failures, not repeated as passes. `lint_claims` exit 1 was a real finding (see 21). |
| 21 | `lint_{claims,changed_prose,readability,style}.py <manuscript>` | 0, 0, 0, **1** | ✅ after correcting two words of prose that tripped `lint_claims` R2/R4 (the statistical sense of "treats"; "well-validated"). `lint_style` exit 1 — see 23. |
| 22 | `lint_{citations,citation_types,consistency,asymmetry,submission_residue}.py` (repo mode) | 1, 1, 1, 0, 0 | ⚠ Correct invocations. **No hard ERROR line names this manuscript** in any of them. `lint_consistency`'s 3 errors are in `emc-fusion-partner-pooling.json` (another lane). `lint_citations`/`lint_citation_types` exit 1 on repo-wide totals; the manuscript's own fifteen identifiers appear only as `NOT SWEPT (advisory)` against the 2026-09-01 retraction sweep — **UNKNOWN, not clean**, and sweeping them needs a network call this repair is fenced from. |
| 23 | `lint_style.py` before vs after | **1** / **1** | ⚠ Exit 1 on **both** the frozen input and the repaired candidate, for the repository's decorative-glyph convention. Em-dash density fell 10.4 → 4.0 per 1000; heading-style errors 4 → 2. House style, not a scientific blocker. |
| 24 | `python3 checks/td1_source_bindings.py` (final, against the frozen candidate) | **0** | ✅ 230 checks, 0 failed. |

## What was deliberately NOT run

`scripts/preflight.sh`, `PREFLIGHT_FULL=1`, pytest, any producer (`emc_expression_panels.py`,
`depmap_sarcoma_dependency.py`, `census_route_expression_grading.py`), any network fetch, any retraction
sweep, and any publication path. ⛔ These are outside this repair's fences. **Nothing here is a current
commit gate or a scientific clearance**, and the historical failures — the author's failed preflight with
its skipped pytest and its style/citation issues, the three historical CLI exit-2 attempts, and the
reviewer's attempt-1 exit 1 — remain historical and are not substituted for anything.
