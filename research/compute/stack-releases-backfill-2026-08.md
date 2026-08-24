---
id: DOC-STACK-RELEASES-BACKFILL-2026-08
title: In-silico stack releases, 2026-06-15 → 2026-08-24 — backfill for the missed method-watch window
level: —
kind: register
status: live
canonical_for: [stack-release-window-2026-06-15-to-2026-08-24]
purpose: >
  Close the release-reading gap left when the weekly field-scan Routine stopped delivering after
  2026-07-13. Reads every release of the libraries this program actually runs in the window
  2026-06-15 → 2026-08-24 and classifies each as (a) changes a default that moves our numbers or
  cost, (b) a capability we could adopt, (c) a bug fix that could have affected results we already
  hold, or (d) routine.
scope: >
  GitHub releases and in-repo CHANGELOGs only, for the named stack. NOT a decision to upgrade
  anything — no pin was changed and no past result was re-graded. NOT a cost document
  (pricing.md owns cost evidence) and NOT the method-watch config (method-watch.md owns that).
audience: [maintainers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---
# In-silico stack releases, 2026-06-15 → 2026-08-24

## The answer, first

**Nothing in this window changes a default that moves our numbers or our cost, and nothing
invalidates a result we already hold.**

That verdict survived three specific scares, each checked against source rather than a release
note, because all three looked like (a) or (c) from the summary alone:

1. **OpenFE v1.12.0 did change how uncertainty is computed** — `np.std(vals)` → `np.std(vals, ddof=1)`.
   It does **not** touch our numbers, because our production analysis path never calls that
   estimator. Detail in [§OpenFE](#openfe--v1120-2026-06-29--c-watch-not-c).
2. **LOMAP v3.3.0 genuinely changes a default** — `charge_changes_score` 0.0 → 0.1. It lives in the
   `gufe`-bindings **network planner**, which this repo does not use; our edges are enumerated
   explicitly. Detail in [§LOMAP2](#lomap2--v330-2026-06-15--a-real-default-change-no-consequence-here).
3. **OpenMM 8.6.0 added per-atom barostat scaling** — but the constructor default is
   `scaleMoleculesAsRigid = true`, i.e. the pre-8.6.0 behaviour. Opt-in, not a default change.
   Detail in [§OpenMM](#openmm--860-2026-08-10--b).

**Two things are worth adopting** (both class (b), neither urgent): bioemu v1.4.0's new steering
package, and OpenMM 8.6.0's native multistate samplers.

**One thing needs a human call, and it is the only item on this page that touches a committed
artifact:** RDKit's 2026.03.4/2026.03.5 patches changed ETKDG distance-geometry bounds. A conformer
panel regenerated today will not be bit-identical to one embedded on ≤2026.03.3. See
[§RDKit](#rdkit-etkdg-bounds-changes) — **flagged for
trimcrae, not acted on.**

> **Method.** Versions and dates are `git for-each-ref --sort=-creatordate` against each upstream
> remote — the tag's own creator date, not a release-page summary. Release notes are the in-repo
> `CHANGELOG`/`ReleaseNotes` at the tag, and every behavioural claim below was confirmed by reading
> the diff between the two tags rather than the note describing it. Two notes were checked this way
> and found to overstate their impact for us (OpenFE, OpenMM); one was found to understate it (RDKit,
> whose ETKDG changes are listed as ordinary bug fixes).

---

## Per-package table

Window is inclusive of both endpoints. "No release in window" means the package's newest tag
predates 2026-06-15 — a real reading, not a gap.

| Package | Release(s) in window | Class | One line |
|---|---|---|---|
| **OpenFE** (`OpenFreeEnergy/openfe`) | **v1.12.0** (2026-06-29) | (c)-watch → **(d) for us** | Uncertainty estimator became unbiased (`ddof=1`); our path does not use it. |
| **gufe** (`OpenFreeEnergy/gufe`) | **v1.12.0** (2026-06-23) | (d) | Py3.14 support, pickling/serialization fixes, a deprecation timeline moved. |
| **OpenMM** (`openmm/openmm`) | **8.6.0** (2026-08-10) | **(b)** | Native `ReplicaExchangeSampler` / `ExpandedEnsembleSampler`; barostat scaling is opt-in. |
| **openmmtools** (`choderalab/openmmtools`) | **no release in window** (latest 0.26.0, 2026-01-07) | — | Unchanged for 7½ months. |
| **OpenFF toolkit** (`openforcefield/openff-toolkit`) | **0.19.0** (2026-08-12) | (d) | One behaviour change, in XML round-tripping of `None`-valued vsite attributes. |
| **openff-nagl** (`openforcefield/openff-nagl`) | **no release in window** (latest v0.5.5, 2026-04-02) | — | No change to the NAGL charge path. |
| **LOMAP2** (`OpenFreeEnergy/Lomap`) | **v3.3.0** (2026-06-15) | **(a)** — no consequence here | `charge_changes_score` default 0.0 → 0.1, in the network planner we don't use. |
| **Kartograf** (`OpenFreeEnergy/kartograf`) | **no release in window** (v2.0.0, 2026-06-03 — 12 days early) | — | ⚠ A major version just outside the window; see [note](#adjacent-out-of-window-but-material). |
| **RDKit** (`rdkit/rdkit`) | **Release_2026_03_4** (2026-07-09), **Release_2026_03_5** (2026-08-01) | **(c)** | ETKDG bounds-matrix fixes; regenerated conformer panels will differ. |
| **Boltz** (`jwohlwend/boltz`) | **no release in window** (latest v2.2.1, 2025-09-08) | — | No tagged release in ~11½ months. |
| **AlphaFold3** (`google-deepmind/alphafold3`) | **v3.0.4** (2026-07-28) | **(b)** | Infra only: JAX bump fixes Blackwell unified memory; CPU/Mac path; `gs://` I/O. |
| **chai-lab** (`chaidiscovery/chai-lab`) | **no release in window** (latest v0.6.1, 2025-03-18) | — | No tagged release in ~17 months. |
| **protenix** (`bytedance/protenix`) | **no release in window** (latest v2.0.0, 2026-04-08) | — | Quiet since April. |
| **bioemu** (`microsoft/bioemu`) | **v1.4.0** (2026-07-20) | **(b)** — highest adopt value | `steering` rewritten into a package: SMC + Feynman-Kac correctors, CV/potential API. |
| **alphaflow** (`bjing2016/alphaflow`) | **no releases, ever** | — | Repository has **zero tags**. Pin by commit or not at all. |
| **RFdiffusion** (`RosettaCommons/RFdiffusion`) | **no release in window** (latest v1.1.0, 2023-04-03) | — | No tagged release in ~3½ years. |
| **PocketMiner** (`bowman-lab/PocketMiner`) | **UNKNOWN — could not check** | UNKNOWN | Repository is not readable anonymously; see [§What I could not check](#what-i-could-not-check). |

---

## The three that needed a source read

### OpenFE — v1.12.0 (2026-06-29) — (c)-watch, **not (c)**

Release: <https://github.com/OpenFreeEnergy/openfe/releases/tag/v1.12.0> ·
changelog: <https://docs.openfree.energy/en/latest/CHANGELOG.html#v1-12-0>

The note that reads like a (c):

> *"The `RelativeHybridTopologyProtocol` and `SepTopProtocol` now return an unbiased estimate of the
> standard deviation via the `get_uncertainty` method, reported uncertainties are expected to be
> larger than before"* ([PR #2000](https://github.com/OpenFreeEnergy/openfe/pull/2000))

The actual diff in `src/openfe/protocols/openmm_rfe/hybridtop_protocol_results.py`:

```python
-        return np.std(vals) * u
+        std = np.std(vals, ddof=1)
+        if np.isnan(std):
+            std = 0.0
+        return std * u
```

`vals` is the list of per-**repeat** ΔG estimates. At n repeats the reported SD is now larger by
exactly √(n/(n−1)) — **1.2247× at n=3**, the replicate count CLAUDE.md §5 names as the ABFE/RBFE
field standard. That is why this looked like it would inflate every error bar we hold by 22.5%.

**It does not, and here is the observation that settles it.** Two facts, both from our own source:

1. `research/modalities/nr4a3_rbfe.py` sets `s.protocol_repeats = 1` (deliberately — the inline
   comment records trimcrae's 2026-07-06 call that a single repeat with MBAR error is the field
   standard for one congeneric edge). With one repeat the estimator sees a length-1 list:
   `np.std([x])` = 0.0 before, `np.std([x], ddof=1)` = `nan` → coerced to 0.0 after. **Identical.**
2. The number actually written to our artifacts does not come from that estimator at all. The
   production `analyze` path reads `unit_estimate_error` — the within-run MBAR standard error —
   directly from the ProtocolUnit outputs. `step1-fanout-map.json` says so in its own
   `uncertainty_note`: *"within-run MBAR standard errors, propagated in quadrature. NOT a replicate
   SD."* MBAR's error is untouched by v1.12.0.

The `est.get_uncertainty()` call at `nr4a3_rbfe.py:985` is on the older single-process `run_leg()`
path, and at `protocol_repeats = 1` it returns 0.0 on either version.

**So: no committed number changes, and no re-grade is warranted.** Two forward consequences worth
holding:

- **If we ever escalate to `protocol_repeats = 3`** — which §5 contemplates — then on openfe ≥1.12.0
  `get_uncertainty()` is now the *correct* unbiased estimator and matches what this repo already
  computes by hand elsewhere (`nr4a3_abfe_diagnostics.py:313` uses `ddof=1`). The upgrade removes a
  discrepancy rather than creating one.
- **⚠ A trap to note:** at one repeat the method now returns a hard `0.0` where the honest answer is
  "undefined". A `± 0.00` from a single-repeat run is not a measurement of zero spread.

The other v1.12.0 changes, checked and not applicable: the 191-line rewrite of
`_rfe_utils/topologyhelpers.py` is entirely the **alchemical charge-correction** path
(`_get_ion_parameters`, keyed on `charge_difference`) and is only entered when state A and state B
differ in formal charge — our committed fan-out legs are `neutral__neutral`. `PersesAtomMapper` was
removed; we use LOMAP and Kartograf. The new `MultiStateAnalysisSettings` in upstream OpenFE's `omm_settings.py` is
purely additive. **`time_per_iteration` (2.5 ps), `timestep` (4.0 fs), `equilibration_length`
(1.0 ns) and `production_length` (5.0 ns) are byte-identical between v1.11.1 and v1.12.0** — verified
by grep at both tags. No repeat of the v1.7.0 `time_per_iteration` event.

### LOMAP2 — v3.3.0 (2026-06-15) — (a) real default change, no consequence here

Changelog: <https://lomap.openfree.energy/en/latest/CHANGELOG.html#v3-3-0>

> *"Changed the default `charge_changes_score` from 0.0 to 0.1 in the gufe bindings to enable
> connected networks for ligands of different net charge by default"*
> ([PR #83](https://github.com/OpenFreeEnergy/Lomap/pull/83))

This is a genuine (a): a scorer default moved, and the effect is that charge-changing edges become
*selectable* into a planned network by default where before they were scored out. A second
behavioural change in the same release: `generate_lomap_network` **now fails by default** when it
cannot produce a connected network, controlled by a new `allow_disconnected` keyword
([PR #154](https://github.com/OpenFreeEnergy/Lomap/pull/154)).

**Neither reaches us.** Both live in the network-planning bindings. This repo calls
`LomapAtomMapper` per-edge (`nr4a3_rbfe.py:328,347`) and `KartografAtomMapper`
(`nr4a3_rbfe.py:484`) on **edges that are enumerated explicitly** in the fan-out map; `grep` finds no
use of `generate_lomap_network`, `charge_changes_score`, or `allow_disconnected` anywhere in the
repository. The MNCAR `>` → `>=` fix ([Issue #147](https://github.com/OpenFreeEnergy/Lomap/issues/147))
is likewise in the gufe scoring bindings.

⚠ **One thing to be aware of rather than act on:** openfe v1.12.0's changelog states it *"incorporates
changes made to the OpenFE Ecosystem with the following releases"*, naming Lomap v3.3.0 and
kartograf v2.0. Our images pin `openfe>=1.12` with `lomap2`/`kartograf` unpinned, so a rebuild today
is expected to resolve these versions. That is fine given the above, but it means **the Lomap 3.3.0
and Kartograf 2.0 behaviour is probably already live in our images** rather than being a pending
upgrade decision. The `LomapAtomMapper(time=N)` MCS-timeout behaviour that
`research/modalities/valb_map_preflight.py` guards against is unchanged in v3.3.0; the only
`LomapAtomMapper` signature change is `seed` defaulting to `None` instead of `""`, which the
changelog states is behaviourally identical and *"purely an aesthetic change"*.

### OpenMM — 8.6.0 (2026-08-10) — (b)

Release: <https://github.com/openmm/openmm/releases/tag/8.6.0> (tag creator date 2026-08-10)

Headline, and it is a real capability: **multistate sampling is now native to OpenMM** —
`ReplicaExchangeSampler` and `ExpandedEnsembleSampler` for collections of thermodynamic states
differing in temperature, pressure or Hamiltonian. That is the job `openmmtools.multistate`
currently does underneath OpenFE's HREX sampler. Nothing to do today (OpenFE imports
`openmmtools.multistate` and would have to migrate upstream), but it is the kind of consolidation
that eventually changes both performance and who maintains our sampler.

**The barostat item is not a default change, and I checked rather than assumed.** The note says
`MonteCarloBarostat` and friends *"now support independent particle scaling rather than rigid
molecule scaling"*, which would move densities and therefore results. The header diff:

```cpp
-    MonteCarloBarostat(double defaultPressure, double defaultTemperature, int frequency = 25);
+    MonteCarloBarostat(double defaultPressure, double defaultTemperature, int frequency = 25, bool scaleMoleculesAsRigid = true);
```

`scaleMoleculesAsRigid = true` is the pre-8.6.0 behaviour, so **the default is unchanged and per-atom
scaling is opt-in.** Class (b). (Coupled detail if we ever opt in: the instantaneous pressure is then
computed from the *atomic* rather than the *molecular* virial.)

Other 8.6.0 items, none of which touch us today: `CustomNonbondedForce` long-range-correction
coefficient caching (helps simulations that frequently change global parameters — which alchemical
lambda schedules do, so a free speedup is plausible but **unmeasured by us**); `PythonForce`
restrictable to particle subsets; a stress-tensor function on `MonteCarloFlexibleBarostat`.

---

## The one that touches a committed artifact

### RDKit ETKDG bounds changes

**Releases in window: `Release_2026_03_4` (2026-07-09) and `Release_2026_03_5` (2026-08-01). Class (c).**

Notes: <https://github.com/rdkit/rdkit/releases/tag/Release_2026_03_4> ·
<https://github.com/rdkit/rdkit/releases/tag/Release_2026_03_5>

Both are patch releases in the 2026.03 series, and their notes read as routine. They are not, for
us, because this repo embeds 3D conformers with ETKDGv3 — `nr4a3_pose_validity.py:52,125`
(`EmbedMultipleConfs`, the receptor-free conformational-accessibility panel) and
`rbfe_edge_timestep_scan.py:82`.

**2026.03.4** added *"All-In-One coordinate refinement for ETKDG"*
([PR #9292](https://github.com/rdkit/rdkit/pull/9292)).

**2026.03.5** then fixed, in the distance-geometry machinery specifically:

- *"Inconsistent stereochemistry of ring-bonds in BoundsMatrixBuilder"* ([issue #9403](https://github.com/rdkit/rdkit/issues/9403))
- *"Inconsistent bounds for 1-4 distances of 6-membered rings"* ([issue #9404](https://github.com/rdkit/rdkit/issues/9404))
- *"RDKit 2026.03.4: testDistGeomHelpers fails"* ([issue #9406](https://github.com/rdkit/rdkit/issues/9406)) — a
  regression **introduced by 2026.03.4** and corrected here
- *"Refactoring, bug fixes, and cleanup of `setTopolBounds()`"* ([PR #9412](https://github.com/rdkit/rdkit/pull/9412))
- *"Validate coordinate map entries before distance geometry embedding"* ([PR #9420](https://github.com/rdkit/rdkit/pull/9420))
- *"Aromaticity perception in polycyclic conjugated system"* ([issue #9398](https://github.com/rdkit/rdkit/issues/9398))

**Concrete consequence for this repo.** The bounds matrix is the input to ETKDG embedding, so these
change the geometries produced for a given molecule and seed. Any conformer panel regenerated on
2026.03.5 will differ from one embedded on ≤2026.03.3 — **not by a random-seed amount, but because
the 1-4 distance bounds and ring-bond stereo handling were wrong before.** The exposed artifacts are
`nr4a3_pose_validity.py` mode A (the ETKDG ensemble → energy landscape) and anything downstream that
scores a fixed conformer panel, e.g. `ensemble_robust_score.py`, whose population SD is defined over
*"a fixed, prespecified set"* — a set that is only fixed as long as the embedder is.

**What I am NOT claiming:** that any existing pose-validity result is *wrong*. These are bounds
corrections, and every conformer that goes into MD is subsequently minimised and equilibrated, which
washes out much of a starting-geometry difference. The honest statement is that **the panel is no
longer reproducible across the RDKit bump**, and whether that matters depends on whether a panel is
being quoted as a fixed population.

⛔ **Flagged for trimcrae, not acted on.** Per the constraints on this task I did not re-run or
re-grade anything. The decision to make is whether `nr4a3_pose_validity.py` mode A carries a
recorded RDKit version, and whether a regenerate-and-compare is worth it. Note that
`rbfe_edge_timestep_scan.py:87` already falls back to `useRandomCoords=True` for molecules ETKDG
cannot seed, so that lane never promised embedder-stable geometry in the first place.

---

## Worth adopting

### bioemu — v1.4.0 (2026-07-20) — (b), the highest-value item here

Release: <https://github.com/microsoft/bioemu/releases/tag/v1.4.0>

The diff v1.3.1 → v1.4.0 is 8,796 insertions, and the substance is that the single
`src/bioemu/steering.py` module (358 lines, deleted) became a `src/bioemu/steering/` package:

| new module (all paths below are upstream, inside `microsoft/bioemu` — not this repository) | what it adds |
|---|---|
| upstream `dpm_smc.py` (287 lines) | Sequential Monte Carlo over the diffusion sampler |
| upstream `dpm_fkc.py` (370 lines) | Feynman-Kac correctors |
| upstream `collective_variables.py` (262 lines) | A CV abstraction |
| upstream `potentials.py` (136 lines) | Biasing potentials against those CVs |
| upstream `utils.py` (458 lines) | Supporting machinery |

Upstream `denoiser.py` (+436 lines) and `sample.py` (+94) were reworked to match, and the test suite grew a
whole `tests/steering/` tree including a chignolin end-to-end.

**Why this is the item to look at.** This repo already runs bioemu
(`nr4a3_bioemu_vast_launch.py`, `nr4a3_bioemu_pocket.py`) for pocket-state sampling. Unbiased
generative sampling gives whatever the model's prior gives; a **steerable** sampler lets you bias
toward a collective variable — e.g. a pocket-opening coordinate — and reweight. That is a *new axis
of evidence* rather than more sampling of an existing test, which is the case §5 says should
**default YES** for a GPU spend.

⛔ **Not adopted, not costed, not pinned here.** No version was changed. This is a pointer for
whoever picks up the bioemu lane, and the honest unknown is that **I have not verified the steering
API works on our pinned model weights or our baked image** — that is a smoke-test question, not a
release-note question.

### AlphaFold3 — v3.0.4 (2026-07-28) — (b), infrastructure only

Release: <https://github.com/google-deepmind/alphafold3/releases/tag/v3.0.4>

No model, weights, or numerics change. Reading the 24 commits in `v3.0.3..v3.0.4`, the substance is
platform and I/O:

- *"Bump JAX and Tokamax to newer versions to fix unified memory on **Blackwell**"* — the one item
  with a compute consequence: it is what makes AF3 usable on Blackwell-class rentals.
- CPU-only and Apple Silicon execution; `--use_cpu_only` replaced by `--jax_backend`; *"Fix numerical
  instability that prevents AF3 from running without a GPU"*.
- *"Use less memory in the `OuterProductMean`"* — headroom on long inputs.
- `gs://` path support via `etils.epath`; chain IDs in the summary confidence JSON; early validation
  that RNG seeds are `uint32`.

⚠ **The `--use_cpu_only` → `--jax_backend` rename is a CLI break.** Any of our launchers passing the
old flag would fail against v3.0.4. I did not find that flag in this repository, but I did not audit
every launcher for it.

---

## Adjacent, out of window, but material

Recorded because they were found while reading the window and would otherwise be lost. **Both are
outside 2026-06-15 → 2026-08-24 and neither is a finding of this backfill.**

- **openff-toolkit 0.18.1 (2026-06-10 — 5 days before the window) drops support for Python 3.11**
  ([PR #2174](https://github.com/openforcefield/openff-toolkit/pull/2174)). `Dockerfile.ternaryfep`
  pins `python=3.11` while leaving `openff-toolkit` unpinned. A rebuild that resolves
  openff-toolkit ≥0.18.1 must therefore either refuse to solve or silently hold the toolkit back at
  ≤0.18.0 — and the second outcome is the dangerous one, because it would break the cross-provider
  version parity that `research/modalities/ternary-env-parity.json` asserts. **I did not test a
  rebuild**; this is a hypothesis about the solver, flagged for whoever next touches that image.
- **Kartograf v2.0.0 (2026-06-03 — 12 days before the window)** is a major version bump, pulled in by
  openfe v1.12.0's ecosystem set, and our images leave `kartograf` unpinned. Its changelog is outside
  this window and **I have not read it.** `nr4a3_rbfe.py:484` uses `KartografAtomMapper()` with all
  defaults, which is exactly the shape that a major bump can change underneath us.
- A preprint titled *"AE-PocketMiner Uses Attention to Simultaneously Predict Cryptic Pockets"*
  (bioRxiv, dated 2026-05-21) surfaced while trying to locate the PocketMiner repository. **UNVERIFIED
  — I did not fetch or read it**, and I am recording only that the search result exists.

---

## What I could not check

- **PocketMiner — UNKNOWN.** `bowman-lab/PocketMiner` returns 404 to anonymous git
  (`git ls-remote` → *"could not read Username"*, the signature of a private-or-absent repo), as do
  the lowercase and `Mickdub/` variants I tried. This repository contains **no GitHub URL for
  PocketMiner** to check against, so I could not confirm the correct coordinates. Its release status
  in this window is genuinely unread — not "no release".
- **Release *pages* vs tags.** Dates above are **tag creator dates**. For OpenMM 8.6.0 a fetch of the
  release page reported a publication date of "August 19" against a tag date of 2026-08-10; I did not
  reconcile the two and have quoted only the tag date, which I verified directly. This affects no
  classification — 8.6.0 is inside the window either way.
- **Anything not released through GitHub tags.** conda-forge and PyPI can carry builds that no tag
  describes, and `alphaflow` demonstrates the general case: it has **never** cut a tag, so "no release
  in window" for it means "no release mechanism", not "no change". Repositories that ship from `main`
  — chai-lab and protenix among them — may have moved without tagging.
- **Kartograf v2.0.0's changelog** (see above) — out of window, unread.
- **Whether any of this is live in our images already.** Our Dockerfiles pin `openfe>=1.12` with
  `lomap2`, `kartograf` and `openff-toolkit` unpinned, so what a rebuild resolves is a **solver
  question I did not run.** The last measured resolution on record is `ternary-env-parity.json`
  (openfe 1.12.0). I did not dispatch a parity rebuild for this task.

## What was NOT done

Per the scope of this backfill: **no dependency was upgraded, installed, or re-pinned; no past
result was re-run or re-graded; `method-watch.md` was not edited.** The RDKit ETKDG item and the
openff-toolkit Python 3.11 item are raised for trimcrae as decisions, not absorbed as work.
