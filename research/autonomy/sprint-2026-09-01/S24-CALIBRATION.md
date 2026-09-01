---
id: DOC-SPRINT-S24-CALIBRATION
title: "S24-CALIBRATION — §6.1 step 1 written and dispatched: the acceptance threshold against validated epitopes, with the decoy null §7 says the screen lacks"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S24-CALIBRATION — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S24-CALIBRATION — §6.1 step 1 written and dispatched

**Item(s):** S13-VACCINE's proposed ledger row 2 ("Calibrate the vaccine acceptance threshold against
experimentally validated epitopes, or record that no validated fusion-junction set exists"), serving
route `RT-VACCINE-COMBINATION` → publication `PUB-VACCINE-PATH`, strategy `ST-IMMUNO`.

**Owned paths (all created this session, none pre-existing):**
`research/modalities/vaccine_threshold_calibration.py`,
`.github/workflows/vaccine-threshold-calibration.yml`,
`research/autonomy/sprint-2026-09-01/S24-CALIBRATION.md`

**Started (UTC):** 2026-09-01T19:33Z  **Finished (UTC):** _see §7_

---

## Verdict

**PARTIAL — the calibration is built, verified and RUNNING; the scientific result is not in yet.**

S13 wrote that §6.1 step 1 "needs the driver to dispatch". It did not. `ci-escape-hatches` §1 routes
exactly this out of the sandbox, and the work is now on a runner: **workflow run `33551737511`, branch
`claude/s24-threshold-calibration`, commit `fc9a9477616e4616d712ef7712e92de95187d79d`**, started
2026-09-01T19:49:26Z.

⛔ **I have not read the calibration's answer, so I claim none.** What is established here is the
specification quoted, the reading of its one ambiguity resolved in the harder direction, the
calibration set's provenance and its legitimacy argument, the pre-registered sufficiency bar declared
before any datum, three dry-run bugs found and fixed locally, and a dispatched run. The number is the
next session's to read, and §6 below says exactly where from.

---

## 1 · What §6.1 step 1 actually specifies, quoted

`research/manuscripts/neoantigen/emc-vaccine-development-path.md:1131–1135`:

> 1. **Defend the acceptance threshold, or record that it cannot be defended.** Computational, needs
>    nothing but public data. Calibrate the cut against experimentally validated epitopes, and if no
>    validated set restricted to fusion-junction peptides exists, that absence is itself the finding
>    and Section 2.3's curve is the only honest report of coverage. Until this is done every figure in
>    B1 is a point on a curve.

### ⚠ The one ambiguity, named, and the harder reading taken

§6.1 step 1 says *"experimentally validated epitopes"*, unqualified. **§B1 of the same paper
(lines 548–556) says something narrower and stricter**, verbatim:

> Calibrating that cut against a benchmark of experimentally validated neoepitopes is the form that
> settling would take. The experimentally validated fusion-junction epitopes in the literature are
> individual sequences across a few fusions, the HLA-A\*24:02-restricted SYT-SSX junction peptide
> [17,18], the four *EWSR1*::*FLI1* breakpoint peptides of the Ewing sarcoma case report [20] and the
> fusion neoantigens of a head and neck series [21], and **a handful of epitopes is not a set against
> which a threshold can be calibrated; calibrating on point-mutation neoantigens instead would import
> an assumption about junction peptides that is the very thing in question.**

Those two sentences do not select the same calibration set. §6.1 would accept any validated epitope;
§B1 refuses everything but fusion-junction epitopes. **The harder reading — §B1's — is the one the
module takes**, and it takes it in the artifact's own words (`_the_reading_taken`), so a reader cannot
mistake which one was applied:

- **Arm F, fusion-junction validated epitopes, is the only arm permitted to settle the cut.**
- **Arm N, general validated epitopes, is computed but is labelled `⛔ NOT THE CALIBRATION — the
  comparator §B1 refuses`** at the top of its own block. It exists so a reader can see what the refused
  calibration would have said, and quoting it as the answer is the specific error §B1 warns about.

⚠ **And note what §B1 already asserts without having measured it:** that the validated fusion-junction
literature is "individual sequences across a few fusions". That is a claim about the size of a set, made
from three citations, and **nobody in this repository has ever queried the epitope databases to check
it.** Arm F is that check. Confirming §B1 would be a result; finding materially more than a handful
would be a bigger one, because it would mean the step the paper defers as impossible is runnable.

---

## 2 · The inputs, and why they are a legitimate calibration set rather than a convenient one

### The source

**IEDB, through the IEDB Query API (IQ-API) at `https://query-api.iedb.org`** — a PostgREST layer over
the Immune Epitope Database, endpoints `mhc_search` (MHC-ligand assays) and `tcell_search` (T-cell
assays). The endpoint form was verified at rung 0 (`WebSearch`), not recalled: the documented example
is `https://query-api.iedb.org/mhc_search?linear_sequence=eq.SIINFEKL`.

**Why IEDB and not something else.** It is the field's curated record of *experimentally validated*
epitopes with their MHC restriction and assay outcome — which is precisely the object §6.1 step 1 names.
The realistic alternatives and why each is worse:

| alternative | why not |
|---|---|
| A hand-assembled list from the manuscript's own citations [17,18,20,21] | It would make the calibration set a restatement of the paper's own reading. Arm F exists to *test* §B1's "a handful", and seeding it from §B1's three citations guarantees the answer. |
| The predictor's own published benchmarks | Reports a model's accuracy on its own evaluation split, not what THIS cut admits on THIS peptide class. |
| Point-mutation neoantigen sets (TESLA, NEPdb and similar) | §B1 refuses them explicitly. They are arm N's territory at best. |
| A mass-spectrometry immunopeptidome atlas | Eluted ligands are presentation evidence, but the paper's B2 is the "measured presentation" step (step 3), not step 1, and an atlas restricted to normal tissue answers a different question. |

⛔ **What makes this a calibration set rather than a convenient one, stated as a property of the query
and not as an assurance.** The fusion arm is defined by an *inclusion rule declared in the module*
(`FUSION_NAME_PATTERNS`) — generic terms `fusion` / `chimeric` / `breakpoint`, plus 27 named fusion
oncoproteins including the four the manuscript cites — and **every source-antigen name that matched is
enumerated in the artifact**, so the rule is auditable rather than asserted. A record returned by a
fusion probe whose antigen name does not match the rule is moved into arm N rather than counted as a
fusion epitope; a probe hit is not itself evidence of anything.

### ⚠ Circularity, stated at full strength rather than buried

**MHCflurry is trained on IEDB.** An arm F or arm N epitope may be in its training set. This is not
fixable with the data available and is not glossed: the bias runs in **one direction**, so

> every sensitivity this calibration reports is an **UPPER BOUND** on the cut's true sensitivity, and a
> cut that fails to capture validated epitopes here fails a fortiori.

That sentence is in the module docstring and in the artifact's `⚠_circularity` field, beside the numbers
rather than in a footnote. **The asymmetry is what makes a negative result here strong and a positive
result here weak**, which is the correct way round for this step.

### The pre-registered sufficiency bar, declared before any datum is read

§B1's own phrase — "a handful of epitopes is not a set against which a threshold can be calibrated" —
names a bar without a number. The module supplies one **at the top of the file, above every import that
touches data**, because "is this set big enough?" answered after the count is known is how a handful
becomes a calibration:

```python
MIN_N_FOR_A_CALIBRATION = 30          # distinct validated fusion-junction epitopes
MAX_CI_WIDTH_FOR_A_CALIBRATION = 0.20 # exact 95% CI on the pass rate at the conventional cut
```

Both are reported against their achieved values either way. CLAUDE.md's anti-gaming invariant: a bar may
not be moved by the result it blocked. ⛔ **If the run comes back with 12 epitopes, the answer is "not a
calibration set", and the fix is not to lower the floor.**

---

## 3 · What the run computes — three arms

| arm | what | status in the argument |
|---|---|---|
| **F** | Validated class I epitopes from fusion/chimeric source antigens, 4-digit HLA-A/B/C restriction, length 8–11 (`coverage_threshold_curve.LENGTHS`, imported), positive assay outcome. Scored on the **same predictor and the same `presentation_percentile` column** as `epitope-allele-matrix.json`, so the calibration and the screen cannot be on different scales. Reported as an empirical CDF over a threshold grid with exact Clopper–Pearson 95% intervals. | **THE CALIBRATION** |
| **N** | The same, non-fusion antigens, on the paper's own 34-allele panel. Bounded sample (≤5,000 pairs, seeded). | **⛔ the comparator §B1 refuses** |
| **D** | Length-matched random peptides from the **same reviewed human proteome fetch `junction_proteome_novelty.py` uses** (imported, not re-implemented), 10 per junction peptide, scored across the whole panel. | **the null §7 says the screen lacks** |

**Arm D is not decoration, and it is the part of this seat most likely to move the paper.** §7 of the
manuscript, at line 1202–1208, states its own gap verbatim:

> The binder counts and every coverage figure derived from them depend on an acceptance threshold this
> paper does not defend, and no multiplicity correction is applied anywhere: 174 peptides were screened
> against 10 and then 34 alleles at two thresholds, **with no decoy control and no null expectation**, so
> the calls that pass are reported as what the screen returned rather than as an enrichment over chance.
> … a shuffle null for predicted binding would need a defended threshold to be a null of anything.

Arm D supplies exactly that null, and it supplies it in the units the paper's headline is stated in:
**how many presenting alleles does a random peptide set of the screen's own size (174 peptides, same
length multiset) buy at the conventional cut?** — 2,000 seeded resamples, compared against the screen's
observed **4** presenting alleles. It also gives the likelihood ratio
`P(pass | validated fusion-junction epitope) / P(pass | decoy)`, which is a calibration statement that
needs no prior on how many junction peptides are real.

⛔ **Both directions of that null are results and the unfavourable one is the more valuable.** If a
random 174-peptide set routinely presents on ≥4 panel alleles at 0.5, then B1's coverage figure is not
distinguishable from chance and the paper must say so. That must be reported at full strength, not
softened — it is the finding this route needs *before* anything is published, not after.

⛔ **What none of it can support.** A calibrated binding threshold is a calibrated binding threshold.
Nothing here is evidence of presentation on a tumour, immunogenicity, efficacy, safety, a therapeutic
window or clinical readiness. Arm F's epitopes were validated on OTHER fusions in OTHER diseases; that
they were seen does not mean this junction's peptides will be.

---

## 4 · What I measured

### (a) The two blockers S13 named are real, and each was checked rather than assumed

```
$ python3 -c "import mhcflurry"
ModuleNotFoundError: No module named 'mhcflurry'

$ curl -sS -o /dev/null -w "%{http_code}" https://query-api.iedb.org/mhc_search?limit=1
curl: (56) CONNECT tunnel failed, response 403          000
$ curl -sS -o /dev/null -w "%{http_code}" https://www.iedb.org/
curl: (56) CONNECT tunnel failed, response 403          000
```

Both halves of the job are outside the sandbox, exactly as S13 recorded. **That is a routing problem,
not a blocker** — CLAUDE.md §6's first tripwire.

### (b) Rung discipline (ci-escape-hatches §0)

`WebSearch` (rung 0) settled the IQ-API's base URL, its endpoint names and one verbatim example query.
`WebFetch` on `help.iedb.org` and `discuss.iedb.org` both returned `EGRESS_BLOCKED`, so the **column
names could not be read from documentation this session can reach.**

⛔ **I did not guess them into a constant and call it done.** The module carries `COLUMN_CANDIDATES` and
resolves each logical field against the **live PostgREST OpenAPI schema at run time**, records which
name it resolved to, and treats a column it cannot resolve as a hard failure that dumps the real column
list. The workflow additionally runs a **schema probe as its first step, without MHCflurry**, so even if
the pip install or the model download fails, the run still lands the one fact this session could not
obtain. An unknown is measured rather than remembered.

### (c) Three defects found by dry-running the module locally before dispatch

Stubbed the network and the predictor, redirected the outputs into the scratchpad (never the live tree),
and ran `main()` end to end. Three real bugs, all fixed before the push:

| defect | how it showed | fix |
|---|---|---|
| `urllib.request.quote` used for URL escaping | works by accident (CPython re-exports it) but is not the API | `urllib.parse.quote` |
| `fetch_proteome()` unpacked as a 2-tuple | it returns `[(accession, name, seq)]` — read from `junction_proteome_novelty._parse_fasta`, not assumed | 3-tuple unpack |
| **`clopper_pearson` raised `int too large to convert to float`** | the first implementation summed `math.comb(n, i) * p**i`; exact for arm F's tens of epitopes, **fatal at arm D's ~59,000 decoy tests** | replaced with the regularised incomplete beta via a Lentz continued fraction, then beta quantiles |

**The third is the one worth recording**: a tail that works on the small arm and dies on the large one is
precisely the shape that would otherwise have been found by a 40-minute CI run. The comment naming it
lives in `betainc`'s docstring.

The replacement was then verified against reference exact-binomial intervals rather than merely "not
crashing":

```
k=0  n=10     -> [0.0,      0.308497]   expected [0,      0.3085]
k=5  n=10     -> [0.187086, 0.812914]   expected [0.1871, 0.8129]
k=10 n=10     -> [0.691503, 1.0]        expected [0.6915, 1]
k=1  n=30     -> [0.000844, 0.172169]   expected [0.0008, 0.1722]
k=300 n=59160 -> [0.004515, 0.005677]   (the case that used to raise)
```

### (d) The rest of the pure logic, exercised on constructed inputs

`normalise_rows` was run on six hand-built rows covering each rejection path, and each was rejected for
the right reason and no other:

```
kept: 3 peptide-allele pairs
dropped: {'assay outcome not positive': 1,
          'length 5 outside [8, 9, 10, 11]': 1,
          'no 4-digit HLA-A/B/C restriction': 1}
fusion split: KTWGQYWQV False | QRPYGYDQIM True | SLLQHLIGL True
```

⚠ Note the third rejection reason: a record whose assay outcome field is **absent** is dropped as
`assay outcome absent (not assumed positive)`, never silently kept. An absent reading is not a reading of
a positive assay.

The threshold grid is **derived, never typed** — the fixed conventional tiers plus every percentile at
which the committed screen actually steps, read out of `epitope-allele-matrix.json`:

```
[0.05, 0.1, 0.2, 0.3, 0.37, 0.3736, 0.4, 0.4033, 0.4061, 0.45, 0.458, 0.4986, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
```

`CONVENTIONAL`, `LOOSE` and `LENGTHS` are **imported from `coverage_threshold_curve`** rather than
re-declared, so this calibration and the curve it is calibrating cannot disagree about what the cut is
(CLAUDE.md §1: one fact, one place).

### (e) The dispatch, and the verification that what runs is what I wrote

Branch `claude/s24-threshold-calibration` created from `main` (all five inputs the module reads were
confirmed present on `main` first: `epitope-allele-matrix.json` — 34-allele panel, 4 presenting alleles —
`fusion-breakpoint-neoantigens.json`, `coverage_threshold_curve.py`, `junction_proteome_novelty.py`,
`artifact_stub_guard.py`). Both files pushed through the GitHub API tooling; **no git write command was
run by this seat**, and the raw-`curl` write path is closed anyway:

```
POST /repos/trimcrae/Rare-cancers/git/blobs
-> 403 {"message":"Write access to this GitHub API path is not permitted through this proxy."}
```

After the push, the branch copies were fetched back and compared byte-for-byte against the local files:

```
research/modalities/vaccine_threshold_calibration.py   IDENTICAL
.github/workflows/vaccine-threshold-calibration.yml    IDENTICAL
```

**Run `33551737511`, event `push`, branch `claude/s24-threshold-calibration`, head
`fc9a9477616e4616d712ef7712e92de95187d79d`, `run_started_at` 2026-09-01T19:49:26Z.**

⭐ **Why a `push:` trigger and not `workflow_dispatch`.** `ci-escape-hatches`: a **new** workflow file
cannot be dispatched from a feature branch, because dispatch reads the workflow from the *default*
branch and 404s on a file that is not there. A `push:` trigger reads the workflow from the *pushed
commit*, which is how `modalities-run.yml` fires on its own branch. The file also carries a
`workflow_dispatch` block with `mode` and `skip_decoys` inputs, which becomes usable the moment the file
reaches `main`.

---

## 5 · What I changed

Two new files plus this one. **No pre-existing file was edited, and no git write command was run.**

| path | what |
|---|---|
| `research/modalities/vaccine_threshold_calibration.py` | new — §6.1 step 1: the three-arm calibration, its pre-registered sufficiency bar, run-time IEDB schema discovery, exact binomial intervals, and the decoy null §7 names as missing |
| `.github/workflows/vaccine-threshold-calibration.yml` | new — the runner. Schema probe first (no MHCflurry), then MHCflurry + the calibration; every compute step `continue-on-error` with an mtime-against-`RUN_STARTED` manifest so a green tick is never mistaken for output; results both uploaded as a run artifact and published to `vaccine-calibration-cache` through `artifact_stub_guard.py` |
| `research/autonomy/sprint-2026-09-01/S24-CALIBRATION.md` | this file |

**Deliberately NOT edited, and each is a real requirement for someone who owns the path:**

1. `.github/workflows/modalities-run.yml` — explicitly not mine, and adding a step there would have been
   wrong anyway: its publish step does `rm -f research/modalities/*.json` on the cache branch and copies
   back only its own enumerated list, so an artifact added without editing that list is deleted on the
   next run. Recorded in the new workflow's header.
2. `research/modalities/run_manifest.py` → `EXPECTED` — the new artifacts are not watched by the
   modalities manifest. The new workflow carries its own equivalent check, so nothing is unwatched; but
   if these artifacts ever move into `modalities-run.yml`, they must be added there in the same commit.
3. `research/manuscripts/emc-systems-map.json` — a new artifact will want a registry entry before it is
   cited from a manuscript. Not written here.
4. **The manuscript itself.** §6.1 step 1 stays unchanged until the run's answer is read. ⛔ Nothing from
   this seat may be written into `emc-vaccine-development-path.md` before that.

---

## 6 · What I could not do, and what it is actually waiting on

⚠ **A CI run does not wake this session by itself.** Nothing here is "blocked"; one thing is *pending a
result I have not read*.

1. **The calibration's answer.** Waiting on run **`33551737511`** (branch
   `claude/s24-threshold-calibration`). **The driver should arm `research/autonomy/await_ci.py` for that
   run id.** Three places to read it, in order of convenience:
   - the run's `::notice title=calibration verdict::` annotation, which prints `verdict.finding`;
   - the workflow artifact `vaccine-threshold-calibration` (survives a failed push);
   - `git fetch origin vaccine-calibration-cache && git checkout vaccine-calibration-cache -- research/modalities/`.

   ⛔ **Read `_fusion_fetch_is_complete` FIRST.** If it is `false`, arm F's size is a reading the
   collector could not take, **not** a reading of absence, and `verdict.finding` says `WITHHELD` for that
   reason. Do not quote a small arm F over an incomplete fetch.

2. **The IEDB column names.** Genuinely unknown to this session — `help.iedb.org` and `discuss.iedb.org`
   are both blocked at the egress proxy. The schema probe step resolves them on the runner and records
   the real list in `_schema_discovery.columns_of_tables_used`. **If `_resolved_columns` shows an
   unresolved required field, the fix is a one-line edit to `COLUMN_CANDIDATES` against the recorded
   list** — that is what the probe exists to make cheap.

3. **A local test file** (`research/modalities/tests/test_vaccine_threshold_calibration.py`) pinning the
   pre-registered constants and the exact-binomial values in §4(c). Not written: it is outside the paths
   my prompt named as mine. It is worth adding, and its content is the checks in §4(c) and §4(d), which
   are reproducible from this file.

4. **The three defects S13 found in files neither of us owns** — the stale `hla-coverage.json`
   class-II note, the self-contradicting `emc-systems-map.json` panel size, and above all **§4(c) of
   S13-VACCINE: `emc-vaccine-development-path.md` §B3 and `shared-vs-individualized-neoantigen-evidence.md`
   falsifier 3 name OPPOSITE anchor configurations as the one that deletes the repertoire.** Still open.
   Unrelated to this seat's result, and still sequenced before anything is written into the manuscript
   from S13's anchor-convention artifact.

---

## 7 · Gates

Charter §6 — scoped to my change, never the whole tree while eleven seats mutate it.

```
python3 -m py_compile research/modalities/vaccine_threshold_calibration.py     # clean
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/vaccine-threshold-calibration.yml'))"
YAML OK — jobs ['calibrate'], triggers ['workflow_dispatch', 'push'], 9 steps
```

Plus the constructed-input runs of §4(c) and §4(d), which are the real check: a linter cannot tell
whether a Clopper–Pearson interval is right, and the reference values can.

⛔ No pre-existing file was modified, so no existing linter or guard is in scope. `preflight.sh` is the
driver's, on a settled tree. **Total real-dollar cost of this seat: $0** — a GitHub-hosted CPU runner,
no GPU, no paid API.

---

## 8 · Ledger rows the driver should write

I may not write these. Proposed:

1. **Advance S13's proposed row 2** ("Calibrate the vaccine acceptance threshold against experimentally
   validated epitopes, or record that no validated fusion-junction set exists") from `queued` to
   **`in_progress`**, `cost_class: free`, evidence: workflow run `33551737511` on branch
   `claude/s24-threshold-calibration`, code `research/modalities/vaccine_threshold_calibration.py`.
   ⚠ **It is not done until the artifact is read.** Whoever reads it closes the row with
   `verdict.finding` quoted, and with `_fusion_fetch_is_complete` checked first.

2. **New row — "Merge `claude/s24-threshold-calibration` so the calibration workflow reaches `main` and
   becomes `workflow_dispatch`-able at any ref."** `kind: hardening`, `state: queued`,
   `cost_class: free`. Until then it can only be re-run by pushing to that one branch. CLAUDE.md §7:
   never let a branch a workflow runs from be the only home of an artifact.

3. **New row — "Register the calibration artifacts."** `kind: hardening`, `state: queued`,
   `cost_class: free`. `vaccine-threshold-calibration.json` and `iedb-validated-epitope-cache.json` need
   an `emc-systems-map.json` entry before either is cited from a manuscript, and they are not in
   `run_manifest.EXPECTED`. Paths I do not own.

4. **New row — "Write `research/modalities/tests/test_vaccine_threshold_calibration.py`."**
   `kind: hardening`, `state: queued`, `cost_class: free`, local. It should pin
   `MIN_N_FOR_A_CALIBRATION` and `MAX_CI_WIDTH_FOR_A_CALIBRATION` against silent movement — the
   anti-gaming property is the whole point of pre-registering them — and pin the exact-binomial
   reference values in §4(c). ⚠ Mutation-test it: move the floor in a **scratch copy** and confirm the
   test goes red.

5. **New row — "Read arm D and decide what §7 must say."** `kind: hardening`, `state: queued`,
   `cost_class: free`. §7 currently states its own gap ("no decoy control and no null expectation"). Once
   arm D lands, that sentence is either **out of date** (a null now exists) or **understated** (the null
   says the screen's presenting alleles are not distinguishable from chance). ⛔ **Either way it must be
   revised at full strength, and the second case is the one that matters.** This is a manuscript edit and
   belongs to whoever owns the paper.

⛔ **Not proposed, deliberately: lowering `MIN_N_FOR_A_CALIBRATION` if arm F comes back small.** That is
the bar the run was pre-registered against, and moving it after seeing the count is the exact
anti-gaming violation the pre-registration exists to prevent. A small arm F over a complete fetch **is**
the result §6.1 step 1 names as acceptable: *"that absence is itself the finding and Section 2.3's curve
is the only honest report of coverage."*

---

## In flight

| item | state | where to read it |
|---|---|---|
| Actions run `33551737511` — §6.1 step 1 calibration, branch `claude/s24-threshold-calibration` | dispatched 2026-09-01T19:49:26Z, `in_progress` at hand-off | `::notice` annotation; artifact `vaccine-threshold-calibration`; branch `vaccine-calibration-cache`. Cost **$0** (GitHub-hosted CPU). |
