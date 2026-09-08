# R2 · Environment precondition — CHECKED, NOT MET

Owner: R2 (OPUS-CAPACITY-CAMPAIGN-20260908). Checked 2026-09-08T22:52Z on branch
`claude/confident-bardeen-ji76cd`, container `Linux 6.18.44-fc-v24`, Python 3.11.15, 4 CPUs.

## Verdict

**The retained CALVADOS 2 simulation environment is NOT present in this container and cannot be
reproduced here under this task's fences.** No simulation was run. Per the task's ⭐ precondition
rule this is a complete and valid result, not a failure.

## The retained protocol that had to be reproducible

CALVADOS 2, 293.15 K, 0.19 M, pH 7.5, 150 nm box, 10 fs step, 7,000 steps/frame, 1,010 frames
(7,070,000 steps), 10 frames discarded, CPU, 4 threads, `calvados` 0.8.1 @ `c16f59a6`,
OpenMM 8.4.0.post2, MDAnalysis 2.10.0, mdtraj 1.11.1.post2, pandas 2.3.3, numpy 2.4.6;
wall 3,392 s for `C161_r1`.

## What was actually run (every attempt is in `checks/`, with its real exit code)

| # | check | command | exit | result |
|---|---|---|---|---|
| 01 | `calvados` importable? | `python3 -c "import calvados; ..."` | **1** | `ModuleNotFoundError: No module named 'calvados'` |
| 02 | OpenMM importable? | `python3 -c "import openmm; ..."` | **1** | `ModuleNotFoundError: No module named 'openmm'` |
| 03 | MDAnalysis importable? | `python3 -c "import MDAnalysis; ..."` | **1** | `ModuleNotFoundError: No module named 'MDAnalysis'` |
| 04 | mdtraj importable? | `python3 -c "import mdtraj; ..."` | **1** | `ModuleNotFoundError: No module named 'mdtraj'` |
| 05 | pip list, relevant packages | `python3 -m pip list \| grep -Ei ...` | 0 | only `numpy 2.4.6`, `scipy 1.17.1`. No `calvados`, `openmm`, `mdtraj`, `MDAnalysis`, **no `pandas`** |
| 06 | any CALVADOS install on disk | `find / -xdev -iname "*calvados*" ...` | 0 | only this repository's own source files and a copy of the repo under `/tmp/claim-ablation-_6455tok/`. **No installed package anywhere.** |
| 07 | conda / micromamba present? | `command -v conda micromamba mamba; ls /opt/conda ...` | **2** | none; `/opt/conda` and `/opt/miniconda*` do not exist |
| 08 | CPU / GPU | `nproc; command -v nvidia-smi` | 0 | 4 CPUs; `nvidia-smi absent` (consistent with the CPU-only fence) |
| 09 | egress configuration | `env \| grep -i proxy` | 0 | `pypi.org` and `files.pythonhosted.org` are in `no_proxy` with `https_proxy=http://127.0.0.1:39285`, i.e. they are excluded from the only egress path |
| 10 | frozen module contract | `python3 research/modalities/emc_condensate_calvados.py --selftest` | **0** | `78/78 checks pass across 13 guard groups` |

## Exact missing components and their version requirements

1. **`calvados` — absent.** Required: 0.8.1 at commit `c16f59a67679cd78f83ff666f8ba2319ca7c1ce9`
   (pinned in `.github/workflows/emc-condensate-calvados.yml`). Not on PyPI at that pin; the
   retained runs installed it from `https://github.com/KULL-Centre/CALVADOS.git`.
2. **`openmm` — absent.** Required: 8.4.0.post2. This is the integrator; nothing else substitutes.
3. **`MDAnalysis` — absent.** Required: 2.10.0.
4. **`mdtraj` — absent.** Required: 1.11.1.post2.
5. **`pandas` — absent.** Required: **<3**, measured (the workflow header records
   `calvados.analysis.get_masses` raising `ValueError: assignment destination is read-only`
   under pandas 3.0.5, absent under 2.3.3). The retained runs used 2.3.3.

## Why this is not fixable inside this task's fences

Acquiring any of the five would be a source acquisition over the network, which this task forbids
outright (⛔ *no network, no source acquisition*). It is also not merely a policy matter:
`pypi.org` and `files.pythonhosted.org` sit in `no_proxy` while all egress is via
`https_proxy=127.0.0.1:39285`, and the CALVADOS pin is a git commit rather than a PyPI release.
Installing anything else — a different `calvados`, a different OpenMM, a substitute force field —
is forbidden and would in any case produce a number under a protocol that is not the retained one,
which may not be reported.

The **scoring half is fully reproducible here**: check 10 shows the frozen module's own contract
passing 78/78, and `score()` reproduces the committed panel exactly from the retained per-run ν
(check 11). Only the **simulation half** is missing.

## What the next action would be

The retained runs were not produced in a container like this one. They were produced by
`.github/workflows/emc-condensate-calvados.yml` on GitHub Actions `ubuntu-latest`, which installs
the pinned stack via `.github/scripts/calvados_install.sh` and runs `matrix` then `reduce`. The
next action is therefore **not** a local install; it is:

1. Have the parent integrate this branch and dispatch that workflow at `ref=<branch>` in
   `matrix` mode with the extended sampling, then `reduce`. That path is CPU-only and needs no
   paid compute.
2. **But the wall-clock arithmetic in `PLAN-AND-COST.md` rules that out before the campaign stop
   as well** — the smallest honest extension is 13.2 CPU-hours against 3.75 h remaining. The
   environment gap and the budget gap are independent, and each alone is sufficient to stop.

So the next action is a decision for the user or a later session, not a step available now:
dispatch the pinned Actions workflow with an increased `n_frames` (and/or `discard_frames`) for a
convergence-extension block, on a clock that is not this campaign's.
