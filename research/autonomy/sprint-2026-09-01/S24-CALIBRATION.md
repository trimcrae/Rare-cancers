---
id: DOC-SPRINT-S24-CALIBRATION
title: "S24-CALIBRATION — §6.1 step 1 run: the calibration is withheld on an unreachable IEDB, and the decoy null the paper says it lacks now runs against the screen"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S24-CALIBRATION — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S24-CALIBRATION — §6.1 step 1 run: the calibration withheld, and the missing null found and against us

**Item(s):** S13-VACCINE's proposed ledger row 2 ("Calibrate the vaccine acceptance threshold against
experimentally validated epitopes, or record that no validated fusion-junction set exists"), serving
route `RT-VACCINE-COMBINATION` → publication `PUB-VACCINE-PATH`, strategy `ST-IMMUNO`.

**Owned paths (all created this session, none pre-existing):**
`research/modalities/vaccine_threshold_calibration.py`,
`.github/workflows/vaccine-threshold-calibration.yml`,
`research/autonomy/sprint-2026-09-01/S24-CALIBRATION.md`

**Started (UTC):** 2026-09-01T19:33Z  **Finished (UTC):** 2026-09-01T20:20Z (run 2 still in flight — see the board)

---

## Verdict

**PARTIAL, with one real result and one measured non-result.**

1. ⛔ **THE DECOY NULL LANDED, AND IT POINTS AGAINST THE ROUTE.** §7 of the manuscript says the screen
   has *"no decoy control and no null expectation"*. It now has one, and **the screen's junction
   peptides present on FEWER panel alleles than length-matched random human-proteome peptides do, at
   the paper's own cut, on the paper's own predictor and panel.** Observed: **4** presenting alleles.
   Random 174-peptide sets of the same length composition: **median 23, mean 22.6, minimum 7 over
   2,000 draws.** Not one of the 2,000 fell to the screen's 4. Numbers, method and limits in §5.

2. **The calibration proper is WITHHELD on all three completed runs, and that is a measured
   non-result rather than a finding.** Arm F is empty *because the collector could not read* — an
   unreachable host on run 1, a source-antigen column that does not exist on run 2, `offset` without
   `order` on run 3 — never because the set is small. `_fusion_fetch_is_complete: false` gates the
   claim automatically on every one of them, and `verdict.finding` reads `WITHHELD` rather than
   announcing that no validated fusion-junction epitopes exist. ⛔ **Whoever closes this must not
   read a zero arm F as §B1's "a handful".**

3. ⛔ **And one methodological finding against myself, which is the part I would least want dropped.**
   Run 2 returned IEDB's live 85/86-column schema and **falsified a source-antigen column I had
   written from a candidate list** (§5(c)). I then diagnosed that run's 68 HTTP 400s from the status
   code alone — an HLA name's `*` and `:` breaking a filter value — and rewrote a function on it.
   Run 3 kept the response body for the first time and **all 90 failures carried one message that
   refuted it**: `offset` with no `order` (§5(d)). ⚠ The wrong fix looked like it worked, because a
   discarded 400 returns an empty list, and an empty list from a fusion probe is indistinguishable
   from *"no validated fusion-junction epitopes exist"* — the exact claim §6.1 step 1 invites.
   `_fusion_fetch_is_complete` is the only reason three runs said WITHHELD instead of publishing a
   fabricated absence. **47 of 61 `except HTTPError` handlers in this repository discard the body
   the same way**, `await_ci.py` among them (§5(d), ledger row 8).

4. **A fourth run carries the real fix and is running long.** `33556831052`. §5(e) names the two
   hypotheses for the slowness and the terminus that discriminates them, and says why I did not push
   a hedge before that terminus.

S13 wrote that §6.1 step 1 "needs the driver to dispatch". It did not — `ci-escape-hatches` routes
exactly this, and four runs have now gone out from this seat, none of them costing a dollar.

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

**Arm D is not decoration, and it turned out to be the part of this seat that moves the paper.** §7 of
the manuscript, at line 1225, states its own gap verbatim (⚠ quoted from the live file — a concurrent
sprint seat re-punctuated this paragraph mid-session, so an earlier draft of this note quoted a wording
that no longer exists):

> The binder counts and every coverage figure derived from them depend on an acceptance threshold this
> paper does not defend, and no multiplicity correction is applied anywhere. The screen tested 174
> peptides against 10 and then 34 alleles at two thresholds, **with no decoy control and no null
> expectation**. The calls that pass are therefore reported as what the screen returned rather than as
> an enrichment over chance. … a shuffle null for predicted binding would need a defended threshold to
> be a null of anything.

Arm D supplies exactly that null, and it supplies it in the units the paper's headline is stated in:
**how many presenting alleles does a random peptide set of the screen's own size (174 peptides, same
length multiset) buy at the conventional cut?** — 2,000 seeded resamples, compared against the screen's
observed **4** presenting alleles. It also gives the likelihood ratio
`P(pass | validated fusion-junction epitope) / P(pass | decoy)`, which is a calibration statement that
needs no prior on how many junction peptides are real. (⚠ The likelihood ratio needs arm F, so it is
absent from run 1.)

⛔ **Both directions of that null are results and the unfavourable one is the more valuable.** The
measured answer is in §5 and it is the unfavourable one: **a random 174-peptide set presents on a
median of 23 panel alleles at the conventional cut, against the screen's 4**, so B1's coverage figure
is not an enrichment over chance in any direction — the deviation is negative. Reported at full
strength rather than softened; it is the finding this route needs *before* anything is published, not
after.

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

### (e) A guard caught my own new workflow, and it was right — fixed, not registered

`research/modalities/tests/test_no_hand_rolled_publish.py` is a repo-wide invariant: **no NEW workflow
step may hand-roll "commit these artifacts and push them"**; there is one primitive,
`research/compute/publish_artifacts.sh`. Its registry of existing offenders is explicitly *"NOT an
allow-list, and not an exemption"*.

**My first draft of the workflow published with a hand-rolled `git checkout -B` onto a side branch
(`vaccine-calibration-cache`) plus `git push`, and the guard went red on it**, locally, before anything
was merged:

```
$ python3 -m pytest research/modalities/tests/test_no_hand_rolled_publish.py -q -p no:randomly
...............................................F..........        # the F is my step
```

⛔ **The tempting fix was to add one line to `KNOWN_HAND_ROLLED`. That would have been the wrong fix and
the file is not mine to edit anyway.** The publish step now calls the primitive against the triggering
branch, with `PUBLISH_IF_CHANGED=1` because this is an event publish rather than a lane heartbeat — a
commit asserting a calibration ran on a run that produced nothing is worse than no commit. Re-checked by
calling the guard's own detector directly rather than by trusting the edit:

```
my workflow flagged as hand-rolled: []
UNREGISTERED violations repo-wide:  []
my workflow in side_branch_publishes: []
```

⚠ **This changes where the results land, and run `33551737511` predates the fix.** It ran the ORIGINAL
workflow, so its committed copy is on `vaccine-calibration-cache`; run `33554351704` and everything
after publish to the triggering branch instead. Both locations are named in this file's §7, and the
run-artifact upload is unaffected and identical in both.

### (f) The dispatch, and the verification that what runs is what I wrote

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
`fc9a9477616e4616d712ef7712e92de95187d79d`, `run_started_at` 2026-09-01T19:49:26Z.** A second push
(head `3f5c1269a52dcde97c49949ae0adcb596d8c08fd`) carrying the §4(e) publish fix and the §5(b)
reachability diagnosis triggered **run `33554351704`** at 2026-09-01T20:16:32Z; both pushed copies were
re-fetched and confirmed byte-identical to the local files the same way.

⭐ **Why a `push:` trigger and not `workflow_dispatch`.** `ci-escape-hatches`: a **new** workflow file
cannot be dispatched from a feature branch, because dispatch reads the workflow from the *default*
branch and 404s on a file that is not there. A `push:` trigger reads the workflow from the *pushed
commit*, which is how `modalities-run.yml` fires on its own branch. The file also carries a
`workflow_dispatch` block with `mode` and `skip_decoys` inputs, which becomes usable the moment the file
reaches `main`.

---

## 5 · The results — four runs

| run | head | what it settled |
|---|---|---|
| `33551737511` | `fc9a947761` | **Arm D landed** (§5(a)) — the decoy null, and the screen sits below it. IEDB unreachable, so the calibration is WITHHELD (§5(b)). |
| `33554351704` | `3f5c1269a5` | **IEDB reachable in 2 s**, so run 1's nine-minute timeout was intermittent. The live 85/86-column schema came back and named two defects in my own queries (§5(c)). Calibration still WITHHELD. |
| `33555613485` | `6f1f18e1b8` | Fusion probes sent for the first time — and **all 90 queries 400'd with one message that refuted my own run-2 diagnosis** (§5(d)). Calibration still WITHHELD. |
| `33556831052` | `976e79c1e5` | The real fix: `order` on every paged query. **Running long at hand-off** — §5(e). |

Everything below is read from the published artifacts, not from a log.

### (a) ⛔ Arm D — the null §7 says the screen lacks, and the screen is BELOW it

The manuscript's §7 (line 1225), verbatim:

> The screen tested 174 peptides against 10 and then 34 alleles at two thresholds, with no decoy
> control and no null expectation. The calls that pass are therefore reported as what the screen
> returned rather than as an enrichment over chance.

The null: 1,740 peptides drawn at random from the reviewed human proteome (UniProt UP000005640,
42,547 records — the same fetch `junction_proteome_novelty.py` uses), length-matched to the screen's
own multiset (8:360, 9:410, 10:460, 11:510 = 10× the screen's 36/41/46/51), scored on the paper's own
34-allele panel and the same `presentation_percentile` column. **59,160 peptide-allele tests.**

**Decoy pass rate against the acceptance threshold:**

| cut | decoys passing | pass rate | exact 95% CI |
|---|---|---|---|
| 0.2 | 155 / 59,160 | 0.262% | 0.222 – 0.307% |
| 0.37 | 284 | 0.480% | 0.426 – 0.539% |
| 0.4061 *(the paper's own highest-percentile call)* | 310 | 0.524% | 0.467 – 0.586% |
| **0.5** *(the conventional cut)* | **381** | **0.644%** | **0.581 – 0.712%** |
| 2.0 | 1,436 | 2.427% | 2.305 – 2.554% |
| 5.0 | 3,260 | 5.511% | 5.328 – 5.697% |

⚠ Read the 0.5 row twice: a *presentation percentile* of 0.5 is by construction meant to admit ~0.5%
of random peptides. **It admits 0.644% here (95% CI excludes 0.5%)**, so on a human-proteome-derived
background of these lengths the cut is slightly more permissive than its own scale advertises. Small,
but it is a calibration observation about the instrument and it moves in the unhelpful direction.

**The null in the units the paper's headline is stated in.** 2,000 seeded resamples of 174 decoy
peptides, counting how many of the 34 panel alleles present at least one at the conventional cut:

```
mean 22.619   median 23   5th pct 14   95th pct 29   min 7   max 33
observed in the screen: 4
p(a random set reaches the observed count) = 1.0     (2000 / 2000)
```

⛔ **Not one of 2,000 random peptide sets scored as low as the screen. The lowest was 7 — nearly
double the screen's 4.** The bootstrap agrees with the closed form to within resampling noise
(34 × [1 − (1 − 0.00644)^174] = **22.95** against a measured mean of **22.62**), so the null is a
property of the arithmetic and not of the resampling.

**What this licenses, exactly.**

- ✅ **B1's coverage figure cannot be read as an enrichment over chance in any direction, and the
  deviation from chance is NEGATIVE.** The EWSR1::NR4A3 junction peptide set is a *worse* source of
  predicted class I binders than length-matched random human protein sequence. §7's own sentence —
  "reported as what the screen returned rather than as an enrichment over chance" — is now not merely
  a caveat about a missing control; the control exists and it runs the other way.
- ✅ It is mechanistically unsurprising and that does not weaken it: the seam sits in a
  glutamine/proline-rich low-complexity stretch (`SYGQQNMPCVQAQYS`), and such sequence is poor at
  generating class I binders. **The point is that the paper asserted neither direction and now can.**
- ⛔ **It does NOT say the four calls are false.** A set can underperform a random background and
  still contain genuine binders. This is a null for the SCREEN — how many alleles a peptide set of
  that size buys — not a test of any peptide.
- ⛔ It is not evidence about presentation, immunogenicity, efficacy, safety, a therapeutic window or
  clinical readiness. It is predicted binding versus predicted binding.
- ⚠ The decoy pool excludes the 174 junction peptides and any IEDB epitope already in hand, which on
  run 1 meant **the 174 alone** (arm F and arm N were empty). Against a reviewed proteome of 42,547
  records that exclusion removes on the order of 1 in 10^4 of the candidate draws, so it cannot move
  a pass rate quoted to three significant figures. Stated because a reviewer will ask, not because it
  is close.
- ⚠ One caveat I cannot remove: the decoys are drawn from the proteome the junction peptides were
  *filtered against* for novelty, so they are self peptides. A self peptide is not a neoantigen, but
  for the question asked — "does this cut, on this predictor, admit these 174 peptides more often
  than 174 arbitrary peptides of the same lengths?" — that is the right background, and it is the
  background the percentile scale is itself defined against.

### (b) The calibration proper: WITHHELD, and why that is not "a handful of epitopes"

```
_fetch_provenance:          "none — schema discovery failed"
_fusion_fetch_is_complete:  false
errors: ["schema discovery failed: https://query-api.iedb.org/ ->
          URLError: <urlopen error [Errno 110] Connection timed out>"]
verdict.finding: "WITHHELD. The IEDB fetch did not complete, so the size of the validated
                  fusion-junction set was not measured on this run."
```

⛔ **Arm F is 0 and that number means nothing.** The design's one job here was to stop a failed
collection from being reported as an absence, and it did: `_fusion_fetch_is_complete` is false, so
the verdict withholds rather than announcing "0 validated fusion-junction epitopes exist". §B1's
"a handful" is still unmeasured.

**Root cause, as far as the evidence goes, and no further.** `Errno 110` is `ETIMEDOUT` **on
connect** — which already excludes a DNS failure (`Errno -2`) and excludes a slow response body (a
read timeout raises differently). Three attempts × a 180 s timeout accounts for the step's ~9 minutes.
⚠ **What it does not settle** is whether the host refuses GitHub-hosted runners specifically, whether
IEDB was down at 19:57Z, or whether only the PostgREST root path is affected. Those are three
different remedies, so run 2 (this file's §7) takes the discriminating observation instead of guessing:
`diagnose_reachability()` probes DNS, raw TCP-443 and HTTP **separately**, per host, with
`www.iedb.org` as the control, and `discover_schema()` now falls back to one sample row per table —
a returned row's keys ARE that table's column list, so the fallback is exact, and it does not need
the root path at all.

⭐ **And the first reading from run 2 already narrows it, from a step time rather than from a guess.**
Run 2's schema-probe step completed in **2 seconds**; run 1's IEDB attempt burned ~9 minutes on three
connect timeouts. Two seconds is shorter than a single one of the new code's 45 s timeouts, and
shorter than any path through `diagnose_reachability()` in which a probe times out — so **on run 2 the
IEDB host answered promptly.** That makes run 1's failure intermittent (IEDB-side, or that runner's
egress at 19:57Z) rather than a standing refusal of GitHub-hosted runners. ⚠ Which of those two it was
is still UNKNOWN and one run does not settle it; what is settled is that the question is worth
retrying rather than routing around. The artifact's `_schema_discovery.schema_source` will say which
source answered.

Exercised in this sandbox before pushing, where it correctly names a different layer:

```
query-api.iedb.org  dns ['8.37.117.201']  tcp_443 connected in 0.1s
www.iedb.org        dns ['8.37.117.163']  tcp_443 connected in 0.0s
https://query-api.iedb.org/  FAILED URLError: <urlopen error Tunnel connection failed: 403 Forbidden>
```

### (c) Run `33554351704` — the schema probe paid for itself, and found two defects in my own queries

Completed `success` 2026-09-01T20:22Z. **The IEDB schema probe took 2 seconds** against run 1's
~9 minutes of connect timeouts, and returned the live PostgREST schema: **39 tables, 85 columns on
`mhc_search`, 86 on `tcell_search`.** That is the one fact this session could not obtain from the
sandbox, and it immediately falsified a column name I had written from a candidate list rather than
from the source. Two defects, and ⚠ **my first reading of the second one was wrong — §5(d) corrects
it, and the correction is left visible below rather than tidied away.**

1. ⛔ **`antigen` resolved to NOTHING, so arm F's fusion probes were never sent.** My candidate list
   had the plural `source_antigen_names`; the live column is **`parent_source_antigen_name`**, and a
   fusion may instead be named on **`r_object_source_molecule_name`**. Both are now probed and both
   are read into the audit blob. Verified on constructed rows where the two fusions are named on
   *different* columns — both are found:
   `distinct_fusion_source_antigen_names: ['EWSR1-FLI1 chimeric protein', 'SS18-SSX1 fusion protein']`.

2. ⛔ **All 68 arm N queries returned HTTP 400** — and the artifact recorded 68 identical
   `HTTPError: HTTP Error 400` lines with **none of the response bodies**, because `_get` discarded
   them. The run named the symptom and destroyed the explanation. `_get` now keeps the body.
   *A failure whose own explanation is discarded is the same defect as the errno with no layer, one
   level up.*

   ⚠⚠ **AND WHAT I WROTE HERE FIRST WAS WRONG — SEE §5(d).** With no body to read, I diagnosed the
   400s from the status code as an HLA name's `*` and `:` breaking a PostgREST filter value, and
   rewrote `fetch_general` on that basis. **Run 3's captured bodies refuted it:** the cause was
   `offset` with no `order`, on every query including page 0, and it had nothing to do with the
   allele string. This paragraph is corrected rather than deleted because the correction is the
   finding. ⭐ The length-based arm N query is **kept** — one bounded query per table instead of 34,
   and `ALLELE_RE` already restricts to 4-digit HLA-A/B/C, which are class I by construction — but it
   is kept on its own merits, not on the rationale it was written with. Arm N remains a bounded
   sample and remains the comparator §B1 refuses; it was never the calibration.

⚠ **What run 2 did NOT settle.** Whether run 1's timeout was IEDB-side or that runner's egress: two
observations from two runs cannot separate them, and one success does not prove a stable route. The
honest entry is that it is **intermittent**, and `diagnose_reachability()` will name the layer if it
recurs.

⭐ **The point worth carrying past this seat:** the schema probe was added as insurance against a
broken pip install, and it is the step that produced the session's most useful measurement. Its value
was not "the run still half-worked" — it was that **the unknown I had honestly labelled UNKNOWN came
back as a fact, and the fact contradicted my candidates.** That is the whole argument for measuring a
schema at run time instead of writing column names from a doc you could not open.

### (d) ⛔ Run `33555613485` — I made a "probably X" and the measured body refuted it

Completed `success` 2026-09-01T20:36Z. The antigen column resolved correctly this time
(`parent_source_antigen_name` + `r_object_source_molecule_name`), so **the fusion probes were sent for
the first time** — and all 90 queries returned 400. But this run kept the HTTP response body, which
run 2 had discarded, and every one of the 90 carried the same message:

```
{"message":"Unsupported request",
 "details":"Query string appears to include an offset parameter without an order parameter.
            Please resubmit the query with an order parameter to ensure consistent paging.
            The query was not sent to the API."}
```

⛔ **That refutes what I wrote after run 2.** I had diagnosed the 68 arm N 400s as an HLA name's `*`
and `:` breaking a PostgREST filter value, and rewrote `fetch_general` on that basis. **It was a
plausible reading of a status code with no body behind it — a "probably X" — and it was wrong.** The
cause is `offset` with no `order`, on *every* query including page 0, and it has nothing to do with
the allele string. It was never a filter-syntax problem; it is a paging guard on IEDB's gateway,
which says in its own words that *the query was not sent to the API*.

**Four things follow, and I am recording all of them rather than only the fix.**

1. **The fix is `ORDER_BY`** — one parameter on every paged query. Verified locally against the URL
   builder rather than assumed: every constructed URL now carries `order=linear_sequence` beside
   `offset=`. Run `33556831052` is testing it.
2. **The wrong comment is corrected in place, not deleted.** `fetch_general`'s docstring now opens by
   saying the diagnosis it used to carry was wrong and what the real one is. The length-based query
   is **kept** — genuinely better, one bounded query per table instead of 34 — but for a different
   reason than the one it was written for, and the file says so. A fix that survives on a false
   rationale is a landmine for the next reader.
3. ⛔ **AND IT IS NOT MY BUG ALONE — IT IS THE REPOSITORY'S DEFAULT.** Measured over every `.py`
   under `research/` and `scripts/`, by matching each `except ... HTTPError` handler against whether
   its next eight lines call `.read()`:

   ```
   except-HTTPError handlers that KEEP the body:    14
   except-HTTPError handlers that DISCARD the body: 47
   ```

   ⚠ **`research/autonomy/await_ci.py:175` is one of the 47**, and so is
   `research/autonomy/gates_verdict.py:198` — the wake mechanism this findings file tells the driver
   to arm, and the gate-verdict reader. This is the class trimcrae named on 2026-08-01 (*"fix the
   underlying root cause, not just address it as a one off"*), and it cost this seat two of its four
   runs. Ledger row 8.
4. ⭐ **The methodological point is the one worth carrying.** CLAUDE.md §4 says to root-cause with a
   real diagnostic and never a "probably X". I violated that on run 2 — and the violation was *cheap
   to make and expensive to spot*, because the wrong fix looked like it worked: it changed the query
   shape, the run completed, the step went green. It only failed to produce data. **What caught it
   was not reasoning; it was four lines that keep an error body.**

### (e) ⚠ Run `33556831052` is running LONG, and that is recorded as a signal rather than reassured away

CLAUDE.md §4: materially slower than predicted is evidence something is wrong, and the first
divergence is the one to dig at. The free reading — step 7's duration on all four runs, from their
completed records rather than from a live poll — is this:

| run | step 7 | what its IEDB fetch did |
|---|---|---|
| `33551737511` | **624 s** | three 180 s connect timeouts (540 s), then arm D |
| `33554351704` | **219 s** | 68 instant 400s, then arm D |
| `33555613485` | **199 s** | 90 instant 400s, then arm D |
| `33556831052` | **1796 s and counting** | ? |

⭐ **Runs 2 and 3 bound the cost of everything that is not the IEDB fetch at ~200 s** — that figure
covers the UniProt proteome pull, the 59,160 decoy predictions and the 2,000-draw null, because in
both runs the IEDB half failed instantly. So run 4 has spent roughly **1,600 s inside the IEDB
fetch**, against 0 s and 540 s on the runs before it.

**Two hypotheses, and I am not picking one:**

- **(H1) The `order` fix worked and the fetch is pulling data.** 88 probe-column combinations, each
  paged up to 60 × 1000 rows, with a server-side sort now forced on every page. Slow *is* the
  predicted signature of success here, because every previous run's fetch was fast precisely by
  failing.
- **(H2) The queries are now timing out rather than 400ing.** Each combination costs 3 tries ×
  180 s = 540 s before the page loop breaks, so ~1,600 s is about three combinations in.

⛔ **I cannot discriminate them from here** — GitHub returns 404 for a job's logs until the job
completes, so the step's own output is unreadable while it runs, and the artifact is not written
until the step ends. ⚠ **This is exactly the case where a "probably it's just slow" would be the same
defect §5(d) already caught me in, so it is left UNKNOWN.**

★ **The observation that will discriminate, at no cost, is the run's own terminus.** Under H2 the job
needs 88 × 540 s ≈ 13 hours and must therefore die on the workflow's `timeout-minutes: 120`; under H1
it completes. **So: a completed run means H1 and the calibration is in hand; a run cancelled at the
120-minute cap means H2.** Either terminus is a reading.

⛔ **And I deliberately did NOT push a fix before that terminus.** The obvious hedge — a wall-clock
budget on the whole IEDB fetch, so a dead endpoint cannot eat a 120-minute job, with a partial fetch
correctly leaving `_fusion_fetch_is_complete: false` — is defensible on its own merits and is a real
hardening. But pushing it now would queue a fifth run behind a fourth whose answer is minutes away
and would truncate a legitimately slow fetch under H1. **Acting on an undiscriminated hypothesis is
the same move §5(d) already caught me making.** The local file is therefore byte-identical to branch
head `976e79c1e5`; the budget is written down here, not in the code, until the terminus says which
hypothesis it is for.

---

## 6 · What I changed

Two new files plus this one. **No pre-existing file was edited, and no git write command was run.**

| path | what |
|---|---|
| `research/modalities/vaccine_threshold_calibration.py` | new — §6.1 step 1: the three-arm calibration, its pre-registered sufficiency bar, run-time IEDB schema discovery, exact binomial intervals, and the decoy null §7 names as missing |
| `.github/workflows/vaccine-threshold-calibration.yml` | new — the runner. Schema probe first (no MHCflurry), then MHCflurry + the calibration; every compute step `continue-on-error` with an mtime-against-`RUN_STARTED` manifest so a green tick is never mistaken for output; results uploaded as a run artifact AND committed through `artifact_stub_guard.py` into `research/compute/publish_artifacts.sh`, the repository's one publish primitive (see §4(e)) |
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

### ⚠ A `git reset --hard` in this working tree destroyed part of this seat's work, twice over

Detected 2026-09-01T21:14Z, and only because I re-compared my local files against the copies I had
pushed to the branch. `git reflog` shows five `reset: moving to HEAD` entries and a sibling seat's
commit titled, verbatim, *"the driver destroyed a seat's finished work with `git reset --hard`, and
the charter did not forbid it"* — so this is a known sprint incident and mine is another instance of
it, not a new one.

**What it cost here, specifically.** Once the driver committed my files they became *tracked*, so my
later working-tree edits were reset away:

| lost | state after the reset |
|---|---|
| the `ORDER_BY` fix in `vaccine_threshold_calibration.py` | local file reverted to the pre-fix 52,314-byte version |
| §5(d) of this file, in full | the document ran straight from §5(c) to §5(e) |
| §5(c)'s correction | ⛔ **the REFUTED `*`-and-`:` diagnosis was left standing as if current** |
| the repo-wide error-body measurement and its ledger row | gone without trace |

⛔ **The third row is the dangerous one.** A destructive reset does not merely lose work — it can
*restore a superseded claim to apparent currency*, which is worse than losing it, because the next
reader has no signal that it was ever corrected.

**Why nothing was actually lost to the world, and what that says.** The code was safe because every
version went to GitHub through the API, so the branch and all four CI runs are unaffected; the prose
was recoverable because it was still in this session's context. ⭐ **The recovery check is worth
generalising: compare each owned file against the copy you pushed, not against your memory of it.**
And the error-body count was **re-measured rather than restored** — it had moved from 46 to 47 and the
line numbers had shifted, because concurrent seats kept editing those files while this seat worked.
Restoring the remembered number would have committed a stale one.

---

## 7 · What I could not do, and what it is actually waiting on

⚠ **A CI run does not wake a session by itself.** Nothing here is "blocked"; one thing is pending a
second reading.

1. **The calibration proper — arm F.** Three runs failed to produce it for three *different* reasons
   — an unreachable host (§5(b)), a source-antigen column that does not exist (§5(c)), and `offset`
   with no `order` (§5(d)) — each diagnosed from a measurement and each fixed. The fourth is in
   flight: **`33556831052`, branch `claude/s24-threshold-calibration`, head
   `976e79c1e5ce2a62c035cef827fd6190ac141075`**, started 2026-09-01T20:41:53Z, and running long
   (§5(e)). **`research/autonomy/await_ci.py` is keyed by SHA, not by run id** (read from its own
   `--sha` interface, not assumed):

   ```
   python3 research/autonomy/await_ci.py --sha 976e79c1e5ce2a62c035cef827fd6190ac141075
   ```

   launched with `run_in_background` so its exit is the wake. Read the result from, in order of
   convenience: the run's `::notice title=calibration verdict::` annotation; the workflow artifact
   `vaccine-threshold-calibration`; the committed copy on the branch itself (runs 2 onward publish to
   the triggering branch — ⚠ run 1's copy is on `vaccine-calibration-cache`, which predates the
   §4(e) publish fix).

   ⛔ **Read `_fusion_fetch_is_complete` FIRST.** If it is `false`, a small arm F is a reading the
   collector could not take, **not** a reading of absence, and `verdict.finding` says `WITHHELD` for
   exactly that reason. Do not quote a small arm F over an incomplete fetch, and do not lower
   `MIN_N_FOR_A_CALIBRATION` to make one speak.

2. **If a later run cannot reach IEDB**, the finding is a routing one and should be recorded as such:
   *IEDB's query API is not reachable from GitHub-hosted runners*, which closes rung 1 for this
   question and makes the next rung a different runner or a bulk export. `_iedb_reachability` will
   say which layer failed, so that sentence will be a measurement rather than an inference.

3. **A local test file** (`research/modalities/tests/test_vaccine_threshold_calibration.py`) pinning
   the pre-registered constants and the exact-binomial reference values of §4(c). Not written: it is
   outside the paths my prompt named as mine. Its content is fully specified by §4(c) and §4(d).

4. **Arm D's consequence for the manuscript.** §7 of `emc-vaccine-development-path.md` currently says
   the screen has no decoy control and no null expectation. It now has both, and the null runs
   *against* the screen. Revising that paragraph is a manuscript edit and belongs to whoever owns the
   paper — see the ledger rows. ⛔ Nothing from this seat has been written into any manuscript.

5. **The three defects S13 found in files neither of us owns** — the stale `hla-coverage.json`
   class-II note, the self-contradicting `emc-systems-map.json` panel size, and above all
   **S13-VACCINE §4(c): `emc-vaccine-development-path.md` §B3 and
   `shared-vs-individualized-neoantigen-evidence.md` falsifier 3 name OPPOSITE anchor configurations
   as the one that deletes the repertoire.** Still open, unrelated to this seat's result, and still
   sequenced before anything is written into the manuscript from S13's anchor-convention artifact.

---

## 8 · Gates

Charter §6 — scoped to my change, never the whole tree while eleven seats mutate it.

```
python3 -m py_compile research/modalities/vaccine_threshold_calibration.py     # clean
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/vaccine-threshold-calibration.yml'))"
YAML OK — jobs ['calibrate'], triggers ['workflow_dispatch', 'push'], 9 steps
```

```
python3 -m pytest research/modalities/tests/test_every_lane_pulls_a_baked_image.py \
  research/modalities/tests/test_lane_registry_contract.py \
  research/modalities/tests/test_artifact_stub_guard.py \
  research/modalities/tests/test_coverage_threshold_curve.py -q -p no:randomly
88 passed in 1.85s
```

```
python3 -m pytest research/modalities/tests/test_publish_does_not_revert_another_jobs_artifact.py \
  research/modalities/tests/test_lane_registry_contract.py \
  research/modalities/tests/test_heredoc_two_shell.py \
  research/modalities/tests/test_lint_optional_input_guards.py -q -p no:randomly
103 passed
```

and the repo-wide publish invariant, called through its own detector rather than through a test id
(a parametrised guard emits no test for a file it does not flag, so "no failure" would otherwise be
indistinguishable from "not checked"):

```
my workflow flagged as hand-rolled: []
UNREGISTERED violations repo-wide:  []
```

It found a real defect in my own workflow before any of this landed, and now passes (§4(e)).

Plus the constructed-input runs of §4(c) and §4(d), which are the real check: a linter cannot tell
whether a Clopper–Pearson interval is right, and the reference values can.

⚠ **Sprint hazard confirmed, and it is NOT a red of mine.** A wider pytest run in this tree ended with
`tracked_tree_guard.assert_tree_unchanged` raising on `research/autonomy/research-ledger.json` and
`scripts/regenerate_aso_chain.sh` — two files this seat never touched, mutated by concurrent seats
mid-run. Scope runs narrowly; do not read that traceback as a failure of the tests it interrupts.

⛔ No pre-existing file was modified, so no existing linter or guard is in scope. `preflight.sh` is the
driver's, on a settled tree. **Total real-dollar cost of this seat: $0** — a GitHub-hosted CPU runner,
no GPU, no paid API.

---

## 9 · Ledger rows the driver should write

I may not write these. Proposed:

1. **Advance S13's proposed row 2** ("Calibrate the vaccine acceptance threshold against
   experimentally validated epitopes, or record that no validated fusion-junction set exists") from
   `queued` to **`in_progress`**, `attempts: 2`, `cost_class: free`. Evidence: runs `33551737511`
   (completed; calibration **WITHHELD** on an unreachable IEDB, arm D landed) and `33554351704` (in
   flight on the diagnosis), code `research/modalities/vaccine_threshold_calibration.py`.
   ⛔ **Do not close it on run 1.** Arm F is 0 there and that 0 is a failed read, not a small set —
   `_fusion_fetch_is_complete: false`. Close it only against a run whose fusion fetch completed, with
   `verdict.finding` quoted.

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

5. ⛔ **New row, and it should outrank the rest — "§7 says the screen has no decoy control and no
   null expectation. It now has both, and the screen sits BELOW the null."** `kind: hardening`,
   `state: queued`, `cost_class: free`, **local**. Evidence:
   `research/modalities/vaccine-threshold-calibration.json` → `arm_D_decoy_null`. Observed 4
   presenting alleles against a random-set median of 23 (min 7 over 2,000 draws), on the paper's own
   predictor, panel and cut. **This is a manuscript edit and belongs to whoever owns the paper**; it
   must be written at full strength, because the paper currently discloses the *absence* of a null
   and would otherwise keep doing so after one exists that runs against it. ⚠ A correction REPLACES
   text; it does not append (charter §8).

6. **New row — "The decoy pass rate at a presentation percentile of 0.5 is 0.644% (95% CI
   0.581–0.712%), not 0.5%."** `kind: hardening`, `state: queued`, `cost_class: free`. A small
   instrument-calibration observation about MHCflurry's percentile scale on a length-matched human
   proteome background, in the direction that makes the cut more permissive than its name. Worth a
   line in §2.2 or §7 if anyone quotes the scale as if it were exact. Evidence:
   `arm_D_decoy_null.pass_rate_by_threshold`.

7. **New row — "Second null: composition-matched shuffle, to separate *this junction* from *this
   amino-acid composition*."** `kind: experiment`, `state: queued`, `cost_class: free`, CI.
   Arm D's decoys are arbitrary human peptides, so it answers "does this cut admit the junction
   peptides more often than arbitrary peptides of the same lengths?" — and the answer is no. It does
   **not** separate two explanations: the junction region is a poor binder source *because* it is
   glutamine/proline-rich, or *independently of* that. Shuffling each junction peptide's own residues
   preserves composition and destroys sequence, which discriminates them. ⚠ **Not built here**
   (CLAUDE.md §5: run a test to its field standard and stop; this is a different axis, not more
   sampling of the same one), and it does not change arm D's reading either way — a set that
   underperforms arbitrary peptides underperforms them whatever the reason.

8. ⛔ **New row — "47 of 61 `except HTTPError` handlers in this repository discard the response
   body, `await_ci.py` and `gates_verdict.py` among them."** `kind: hardening`, `state: queued`,
   `cost_class: free`, local. Measured 2026-09-01 by matching each handler against whether its next
   eight lines call `.read()`; the count and site list are reproducible from that rule, and ⚠ the
   line numbers move as concurrent seats edit those files, so **re-run the rule rather than quoting
   a stale offset**. **This is not a style complaint — it cost this seat two of its four CI runs**
   (§5(d)): a 400 whose body is thrown away returns an empty list, and an empty list from a database
   query is indistinguishable from a true absence. ⚠ `await_ci.py` is on the list and is the
   mechanism this file asks the driver to arm, so a failed poll there reports its status code and
   destroys the server's explanation of it. A guard asserting that a networked fetcher keeps the
   body would be the durable fix, in the shape of `test_no_hand_rolled_publish.py`. Not written
   here: not my paths, and 47 sites is a task to sequence, not to absorb.

9. **New row — "A `git reset --hard` in the shared sprint tree destroyed tracked-file edits from at
   least two seats."** `kind: hardening`, `state: queued`, `cost_class: free`, local. A sibling seat
   has already filed the general case; this row records that **S24 was hit too**, and adds the
   detail that matters most: because the reset reverted a *correction*, it left a refuted diagnosis
   reading as current (§6, last subsection). Charter §1 forbids seats from git-writing and says
   nothing about the driver; that asymmetry is the gap.

⛔ **Not proposed, deliberately: lowering `MIN_N_FOR_A_CALIBRATION` if arm F comes back small.** That is
the bar the run was pre-registered against, and moving it after seeing the count is the exact
anti-gaming violation the pre-registration exists to prevent. A small arm F over a complete fetch **is**
the result §6.1 step 1 names as acceptable: *"that absence is itself the finding and Section 2.3's curve
is the only honest report of coverage."*

---

## In flight

| item | state | cost | where to read it |
|---|---|---|---|
| Actions run **`33556831052`** — §6.1 step 1, fourth attempt (`order` on every paged query). Branch `claude/s24-threshold-calibration`, head `976e79c1e5`. | started 2026-09-01T20:41:53Z; **step 7 at 1,796 s and counting** against 199–624 s on runs 1–3 — see §5(e), which names the two hypotheses and the terminus that discriminates them | **$0** (GitHub-hosted CPU) | `::notice title=calibration verdict::`; artifact `vaccine-threshold-calibration`; the committed copy on the branch. Wake with `python3 research/autonomy/await_ci.py --sha 976e79c1e5ce2a62c035cef827fd6190ac141075` under `run_in_background`. |

⚠ **Read the terminus, not just the verdict.** A run that COMPLETES means the fetch finally worked;
a run CANCELLED at the workflow's `timeout-minutes: 120` means the queries are timing out rather than
returning, and the fix is in §5(e).

Runs `33551737511`, `33554351704` and `33555613485` are **finished** (all `success`) and are reported
in §5; none is in flight. **Total real-dollar cost of this seat: $0** — four GitHub-hosted CPU runs,
no GPU, no paid API.
