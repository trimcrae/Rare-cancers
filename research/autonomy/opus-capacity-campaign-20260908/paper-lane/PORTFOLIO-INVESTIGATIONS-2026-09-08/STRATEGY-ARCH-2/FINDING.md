---
id: DOC-PORTFOLIO-INVESTIGATION-STRATEGY-ARCH-2-20260909
title: "Portfolio investigation — STRATEGY-ARCH-2: reading eligibility criteria with a string matcher makes the screen worse, measured"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: STRATEGY-ARCH-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
endpoint: PUB-STRATEGY-ARCH
---

# STRATEGY-ARCH-2 — the depth at which a keyword screen fails

⛔ Not medical advice, not a trial-matching service. Everything below is a statement about
registry text on the retrieval dates recorded in the cited deposits. No patient, referral,
enrolment, treatment or outcome is involved, and nothing here says any trial would accept any
patient. No efficacy, safety, selectivity or therapeutic-window claim is made or implied, and
none could be made from this kind of evidence.

## 1 · The question

The reachability manuscript's §6 remedy tells tool-builders to **"read criteria rather than match
strings"**, and its §6.2 separately asks registries to **"index eligibility text, not only
conditions."** The first-round lane scored keyword screens that see only titles and listed
conditions — the index a matcher reads today.

**Question.** If a string screen is given the posted eligibility criterion as well, does it get
**better or worse**? Concretely: over the records this programme has adjudicated by reading their
posted eligibility text, does adding the criterion text to the matched field set raise or lower
precision, for the histology-name lexicon a patient would type and for the molecular lexicon §6
recommends building?

This is answerable, it has a stated pass/fail, and it can come out against the manuscript.

## 2 · Paper-level merit

The manuscript's two operational recommendations to third parties are §6.2 (index the criteria)
and §6.3 (read the criteria, do not match strings). They are currently stated as independently
good. If indexing eligibility text makes a *string* screen strictly worse for the exact term a
patient types — their own histology name — then §6.2 and §6.3 are in **tension**, and a
tool-builder who implements §6.2 without §6.3 has been told to build the failure the paper
exists to warn about. That is a non-trivial, checkable, patient-relevant correction to a
methodological recommendation, it needs no bench, and it is falsifiable from data already
committed to this repository.

## 3 · The exact evidence gap, and what makes it new

`PUB-STRATEGY-ARCH` fixed the screen's field set by construction: *"case-insensitive substring
match over `brief_title` + `official_title` + `listed_conditions` only — the fields a string
matcher sees. Eligibility text is deliberately withheld from the screen."* Reading depth was
therefore **held constant and never varied**, so no measurement exists of what changing it does.

The unfinished input is specific: the adjudication deposit carries a **verbatim posted criterion**
for each of its four records (`the_admitting_criterion_verbatim` /
`the_restricting_criterion_verbatim`) — text that has been committed since 2026-08-09 and that no
screen has ever been scored against. Nothing needed to be fetched.

**Reconciliation with `research/autonomy/portfolio-2026-09-05/recommendation.md`.** Re-read in
full. Its five ranked prospects are the expression validation map (rank 1), the care-delivery
*denominator* resource on surgical margins and follow-up (rank 2), the FET construct-to-mechanism
map (3), fusion-partner synthesis (deferred, 4) and NR4A3 degrader optimisation (deferred, 5).
**None concerns trial reachability**, and rank 2 — the nearest — is about comparing surgical
margin and follow-up denominators, not about findability. The memo is therefore neither an
authority for nor an obstacle to this step; it is orthogonal, and it is recorded as such rather
than cited as support. Its rank-5 deferral (no paid GPU, no expanded docking) remains in force and
is untouched here.

## 4 · Re-derivation of the prior lane's numbers — FIRST, before building on them

`rederive_prior_benchmark.py` re-reads both deposits, re-transcribes the eight ground-truth labels
from the deposit fields independently, rebuilds the visible-field text and the confusion matrices
with its own code — it does **not** import `keyword_screen_benchmark.py` — and then compares its
own numbers against `PUB-STRATEGY-ARCH/keyword-screen-benchmark.json` field by field.

**All six rows reproduce exactly. MISMATCHES: 0** (`checks/01-rederive-prior-benchmark/`, exit 0).
The prior lane's histology recall 0.00, molecular precision 0.50 / recall 0.75, and the
recruiting-interventional stratum (recall 1.00, precision 0.50) are confirmed digit for digit.
No discrepancy was found, so this lane could build on them.

## 5 · The bounded step taken

A **screen-depth ablation**: lexicons and ground truth held fixed, one variable changed — how deep
the string matcher reads — over the four adjudicated records whose posted criterion is committed
verbatim (NCT06571734, NCT04151342 admit; NCT06094101, NCT07188532 refuse).

* `depth_A_index_only` — `brief_title` + `official_title` + `listed_conditions`
* `depth_B_index_plus_criterion` — depth A **plus** the verbatim posted criterion
* `depth_C_criterion_only` — the criterion alone

**Criterion stated in advance, before scoring:** *if "read the criteria" is protective for a
string screen, depth B precision must be ≥ depth A precision for every lexicon.* One lexicon whose
precision falls refutes it.

### Result

| lexicon | depth | n | TP | FP | TN | FN | precision | recall |
|---|---|---|---|---|---|---|---|---|
| histology-name | A index only | 4 | 0 | 0 | 2 | 2 | undefined (never fires) | 0.00 |
| histology-name | B index + criterion | 4 | 0 | **1** | 1 | 2 | **0.00** | 0.00 |
| histology-name | C criterion only | 4 | 0 | 1 | 1 | 2 | 0.00 | 0.00 |
| molecular | A index only | 4 | 2 | 1 | 1 | 0 | 0.67 | 1.00 |
| molecular | B index + criterion | 4 | 2 | 1 | 1 | 0 | 0.67 | 1.00 |
| molecular | C criterion only | 4 | 1 | 1 | 1 | 1 | 0.50 | 0.50 |
| union | A index only | 4 | 2 | 1 | 1 | 0 | **0.67** | 1.00 |
| union | B index + criterion | 4 | 2 | **2** | 0 | 0 | **0.50** | 1.00 |
| union | C criterion only | 4 | 1 | 2 | 0 | 1 | 0.33 | 0.50 |

**The criterion is REFUTED**, for two of three lexicons.

1. **The histology-name screen's only hit, at any depth, is a refusal.** The single record that
   changes is NCT07188532. Its adjective *extra-skeletal* is **not** in its title and **not** in
   its listed conditions (`Ewing Sarcoma`, `Round Cell Sarcoma With EWSR1-non-ETS Fusion`) — it is
   in `the_restricting_criterion_verbatim`: *"Histological confirmation of Ewing sarcoma, including
   both skeletal and extra-skeletal primary tumors."* A histology screen on the index never fires
   at all; extended over the criterion it fires exactly once, wrongly. Precision goes from
   *undefined* to **0.00**. Deeper string reading did not prevent the paper's keyword trap — it
   **created** it.
2. **The union lexicon loses precision outright, 0.67 → 0.50.** This is the plain refutation of the
   stated criterion: the added criterion text contributes a false positive and no true positive.
3. **§6.2 and §6.3 are in measurable tension.** "Registries could index eligibility text" and
   "read criteria rather than match strings" are not independent goods. Indexing the criteria
   helps a human reader and, on this evidence, hurts a string matcher — for precisely the term a
   patient is most likely to type, the name of their own histology.

### Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `screen-depth-ablation.json` — nine scored rows, per-record hit lists at all three
  depths, the criterion text scored, and the stated falsifiable criterion with its outcome.
  Generated by `screen_depth_ablation.py`.
* **Validation / baseline.** The **baseline is depth A**, which is the prior lane's own published
  configuration; the ablation is scored against it, not against nothing. Ground truth is validated
  at run time: each label is re-checked against the deposit's own `verdict` wording and the script
  exits 2 on mismatch or on any record lacking verbatim criterion text. Separately,
  `rederive_prior_benchmark.py` confirms the prior table 6/6 rows, 0 mismatches, before any of this
  was built on.
* **Provenance.** `research/literature/emc-trial-reachability-adjudication-2026-08-09.json` (whose
  own `retrieval` block records CI workflow_dispatch of `fetch-literature.yml`, Actions run
  31311027104, HTTP 200 for all four) and
  `research/literature/fet-fusion-trial-eligibility-2026-08-07.json`. **Nothing was fetched, no
  network egress was attempted, no refusal was encountered or worked around.** No shared file,
  graph, registry, gate or acceptance criterion was touched; every write is inside this lane
  directory.
* **Limitations — stated, not managed.**
  * **n = 4.** Only the adjudication deposit stores criterion text verbatim; the four FET-deposit
    records flagged `eligibility_text_retrieved: true` store a boolean and an assessment, **not the
    text**, so they cannot be scored at depth B or C. This is not a sample of the registry and no
    interval is quoted.
  * **The criterion text is one quoted criterion per record, not the full eligibility section**, so
    depths B and C are a **lower bound** on what a real matcher would read. The bound is
    directional and that direction matters: more criterion text can only **add** hits, so on a
    refusing record it can only add false positives. **The histology false positive is therefore
    robust to truncation — more text cannot remove it.** The depth-C molecular recall of 0.50 is
    the opposite case and is an **upper bound on the harm**, not a measurement of it.
  * **Lexicons are a priori and small.** A different lexicon re-scores the table; that is the point
    of publishing the lexicons and the per-record hits rather than only the rates.
  * A registry record is not a protocol, and "admits"/"refuses" is a reading of posted criteria,
    never a trial team's decision.
  * **UNKNOWN, not zero:** what a false hit costs the person it reaches is still unmeasured and is
    not a registry quantity. The prior lane's no-go on that stands unchanged and is not weakened
    here.
* **Stop condition.** Stop. The ablation is complete over every record whose posted criterion text
  is committed. It cannot be enlarged without storing eligibility text for more records, which
  needs the CI-routed `clinicaltrials.gov` fetch the prior lane recorded as refused at this
  sandbox's egress proxy (`checks/01-connectivity-probe/`, curl exit 56). **Do not** enlarge the
  set by paraphrasing criteria from assessments — the assessments are the adjudicators' prose, not
  the registry's text, and scoring a screen against prose the adjudicator wrote is circular.

## 6 · What did NOT happen

No network call was made from this lane, so there is no failed-fetch check to preserve here; the
prior lane's refused probe is the standing record and was not retried, reworded, model-switched or
proxied around. No manuscript, graph, registry or gate was edited. No claim of efficacy, safety,
selectivity, therapeutic window or clinical readiness appears in any artifact produced here.

## 7 · Unapplied suggestion for the manuscript (NOT applied)

`UNAPPLIED-emc-trial-reachability-section4-depth.diff` — two hunks against
`research/manuscripts/care-delivery/emc-trial-reachability.md`: a measured paragraph closing §4,
and a caveat on §6 item 2 so the two recommendations are no longer stated as independent goods.
**It is not applied.** `git apply --check` exits **0** (`checks/03-git-apply-check/`). The paper
owner decides; this lane owns none of those files.
