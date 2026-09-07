---
id: DOC-IPD-PUBLISHED-BASELINES-20260906
title: Actual published IPD reconstruction baseline checkpoint
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Establish executable published comparators and their information-model limits.
scope: Existing synthetic toy and eighteen synthetic development releases only.
audience: [maintainers, autonomous research agents]
---

Both original R packages now execute locally. Across the eighteen supplied development releases, CIFresolve returned reconstructed IPD and logrank results in 18 cases; IPDfromKM returned results in 15 and errors in three dense-risk-table cases. Independent SciPy logrank calculations reproduce all 33 returned p values with maximum absolute discrepancy 9.99e-16. No held-out cases or empirical outcome files were opened. These are development executions, not evidence that one method is superior or that a paper is ready.

## Original methods and runtime

[IPDfromKM 0.1.10](https://cran.r-project.org/web/packages/IPDfromKM/index.html) is GPL-2. The CRAN source archive, primary HTML manual and index are preserved in `sources/`, with acquisition hashes and timestamps. The actual installed CRAN binary is used by `preprocess()` and `getIPD()`; there is no reconstruction port or replacement implementation.

[CIFresolve](https://github.com/andrewtitman/CIFresolve), version 0.1.1 at commit `2295c0d32b3bb5595fb38a32030f773daa47091d`, is GPL (>=2). Original source files, DESCRIPTION and documentation are preserved. `KM_resolve()` followed by `make_data()` executes the default approximate continuous quadratic program and integer rounding, using quadprog. This is the published ordinary-survival interface, not a competing-risk surrogate. The optional full MIQP implementation requires Rcplex and was not executed. That restriction must accompany any future comparator claim. The primary method is [Titman 2026](https://doi.org/10.1002/sim.70474).

R 4.6.1 was downloaded from CRAN and installed into this isolated worktree's `.cache/R-4.6.1`. The installer used current-user mode, no shortcuts, and ultimately `main,x64` components. Initial main-only attempts lacked the executables; original installer logs are retained. The installer created its normal current-user uninstall registration. Package and dependency versions and original install output are in `install.log`; cached package archives and R installer sizes and SHA256 values are in `runtime-acquisition.json`. The source is unmodified. No paid services, GPU work, outreach, main-branch mutation or publication occurred.

## Interface and repair

`runner.R` accepts only a released-summary JSON, a local library path and an output path. It records the actual numeric package inputs, package versions, warnings, errors, elapsed time and reconstructed rows. It supplies sample size, right-continuous KM coordinates, pre-event numbers at risk and total events to both packages. No censor ticks, original p value or hidden records are provided.

For `discrete-km-release-v1`, coordinates include (0,1), every grid point, and the unchanged final survival at K+1. All observations exit by K in the public model, so risk(K+1)=0 is implied and appended explicitly. Supplied risk(1)=n is replaced with the equivalent risk(0)=n because no observation can occur before time1. This replacement is necessary for CIFresolve's interface: original `sources/CIFresolve/R/routines.R` lines72-76 remove duplicate risk counts by retaining their latest time; its later rounding assumes a risk origin at0. The initial additive-origin adapter led to negative censor counts and `make_data()` errors. The complete before-repair outputs and original runner are retained. The repair changes no package source and uses no hidden outcome information.

Neither original package enforces the present discrete-support model or treats reported probabilities as rounding intervals. Their censor times may fall between grid points. No returned records are silently rounded to make them compatible. `verify_results.py` independently checks sample size, event total, every supplied pre-event risk count, rounded KM values and discrete support. None of the 33 returned reconstructions meets all five properties for both arms. Per-property findings are in `validation.json`; incompatibility is not automatically algorithmic error, since the original methods solve a different reconstruction problem. A fair paper-level comparison needs to acknowledge this distinction, assess utility under a common estimand and include abstention/failure handling.

## Actual executions and limitations

The eighteen releases are nine explicitly synthetic development datasets, each with sparse and dense risk tables, copied byte-for-byte from the bounds worker. They have both-arm censoring, ties and rounded probabilities. Parent case linkage is preserved in `development-releases.json`. All commands, exit codes, package outputs and original logs are retained under `development/` and `development-runs.json`. Every process completed; nothing remains running.

IPDfromKM errors occurred in the dense versions of the three hazard-b-0.65 cases: `missing value where TRUE/FALSE needed`. They remain failures; no parameter tuning or source patch was used to force completion. Original package preprocessing can alter supplied coordinates, and its returned preprocessing table is retained for inspection. CIFresolve's default QP result is a point reconstruction, not a compatibility certificate.

On the previously selected exact synthetic toy, IPDfromKM returned p approximately0.05324745. CIFresolve's all-event arm failed QP feasibility; the documented tolerance values 1e-8, 1e-6, 1e-4, .001 and .01 all failed for that arm. These diagnostic attempts and errors are preserved separately. They do not establish a general method defect. No further tuning was performed. The old toy is a development counterexample, not a prevalence estimate.

## Named existing benchmark

The [KM-PoPiGo developer documentation](https://kmpopigo.github.io/doc/datasets/index.html) points to [Zenodo18320575](https://zenodo.org/records/18320575). This round recovered the full API metadata and downloaded RealIPD.zip (11,066,903 bytes), matching publisher MD5 `588b4eb567f5f6a25ffa56b476740fd6`; SHA256 is `60d8ea495aa958fb53cd63de807325026fd89184f980349221ec76ebe6890f40`. The record declares CC-BY4.0. Only archive member names were inspected (467 entries); CSV contents, outcome records and images remain unopened. The archive stays in cache, with metadata/inventory committed by the coordinator if accepted. Metadata describes single-curve TCGA/GEO material; it is not verified paired randomized-trial IPD. Any later constructed contrast must be labeled a reconstruction benchmark, not a treatment-effect analysis. Dataset-level provenance and an appropriate prespecified split still require review.

## Reproduction and next action

From this worktree, invoke the cached `Rscript.exe --vanilla` with `runner.R`, `.cache/R-library`, one release JSON, and a fresh result JSON. The precise executed commands are in `development-runs.json`. `run_development.py` is the development-only batch harness; it points to the separately owned development release file and never opens original IPD. `verify_results.py` needs SciPy (this run used the existing repository dependency cache through PYTHONPATH). Its findings concern returned statistics and released-summary consistency, not hidden-reference decision accuracy.

The next scientific step belongs to the coordinator: combine these comparator outputs with independently checked bounds under explicitly matched assumptions, evaluate original-development decisions and design the frozen held-out/abstention experiment. This checkpoint stops before that evaluation. Normal repository preflight, integration, independent ultra review and full publication checks were not performed by this worker.
