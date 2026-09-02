---
id: DOC-SPRINT-S46-EIGHT-QUANTITIES-BOUND
title: "S46-EIGHT-QUANTITIES-BOUND — the eight blind word-quantities S40 found, each tied to the artifact that owns it, proved by ablation rather than by assertion"
level: L3
kind: incident
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Close the coverage red the honest way — by making the paper more guarded, not by shrinking the
  gate's population — and record, per sentence, what its number is a count OF, which committed
  artifact now owns it, and the before/after ablation verdict that proves the binding.
scope: >
  The eight sentences `S40-COVERAGE-INFLATION.md` measured as covered-but-blind: seven in
  `research/manuscripts/aso/fusion-junction-aso-journal-article.md`, one in
  `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md`. Two new guard modules
  and the regenerated census artifact. No manuscript byte was changed, and no crediting rule,
  scorer or sample size was touched.
last_verified: 2026-09-02
---

# S46 — eight quantities bound, and four numbers that have nowhere to be bound to

**8 of 8 sentences flipped BLIND → RED**, measured with the repository's own harness
(`research/manuscripts/claim_ablation.py`) on this tree, with `already_red: 0` at baseline on every
one of the sixteen runs — so no verdict here rests on a subtraction.

## ⛔ WHAT WAS NOT DONE, FIRST, BECAUSE IT IS THE POINT

The alternative fix was to tighten `claim_coverage.covered` so a sentence stating a quantity is
credited only to a witness that binds a quantity. A previous seat measured it over 34 ablated
sentences: recall 8/8 and **precision 8/27 = 30 %**, destroying about two genuinely-bound sentences
per real defect caught — and it clears the red by REMOVING sentences from the gate's own population,
which is the anti-gaming case `research/autonomy/amendment_guard.py:190` names ("a bar may not be
changed by the cycle it blocked").

⭐ **This change moves the number in the other direction.** The population is untouched, the
crediting rule is untouched, the sample size is untouched, and the manuscripts are untouched. What
changed is that eight sentences the census called covered are now covered in fact.

⚠ **AND THE `covered` COUNTS DID NOT MOVE AT ALL.** Measured before and after on every one of the
27 censused documents: **zero change to `sentences`, `covered`, `with_a_number`,
`with_a_number_covered` or `uncovered`.** All eight sentences were already inside `covered`; what
was false was the word, not the count. A fix that had raised `covered` would have been the
suspicious one.

## The eight, with what each number counts

⛔ Every expected value below is READ FROM THE ARTIFACT AT RUN TIME. A guard asserting that the word
"six" appears would pin a spelling and survive the artifact changing underneath it, which is the
defect rather than a fix for it.

| # | where | the quantity | what it is a count OF | artifact that now owns it |
|---|---|---|---|---|
| 1 | article §1 | `six`, `seven`, `ten` | RNase-H1's minimum DNA gap and its optimal range, as PMID 24981949 is **quoted** stating them | `aso/lit-targets-aso-gap-length.json` — the verbatim quotes ported from `literature-cache` |
| 1 | article §1 | `ten` (2nd) | the hybrid length at which THIS panel counts a liability (`MIN_DUPLEX_BP`) | `modalities/aso-parent-gap-pairing.json` → `method.min_duplex_bp` |
| 2 | article §2 | `six` | wild-type parent transcripts the mature-parent screen searched | same file → `method.parents_searched` (EWSR1, FUS, NR4A3, TAF15, TCF12, TFG) |
| 2 | article §2 | `fourth` | position of one screen in a five-item enumeration | ⛔ **NONE** — see "left open" |
| 3 | article §2 | `second` | which stage of the PMID 39912803 framework the energy re-score is | `modalities/aso-offtarget-duplex-energy.json` → `_why`: *"This panel had the first stage and not the second."* |
| 4 | article §2 | `ten`, `five` | locked residues the intended duplex pairs (`2 × wing`), and the one wing a parent can reach (`wing`) | `aso-parent-gap-pairing.json` → `_geometry.wing`, cross-checked against the energy re-score's own `method.geometry.wing` |
| 5 | article §3 | `five` | the reagents' locked wing length | same `_geometry.wing` |
| 5 | article §3 | `two`, `four` | locked residues per wing in a conventional gapmer | ⛔ **NONE** — see "left open" |
| 6 | article §3 | `two` | the mismatch ceiling both near-match screens run at | `aso-premrna-offtarget.json` → `method.max_mismatches`, cross-checked as `16 − 14` from `junction-aso-offtarget.json` → `method.near_match_threshold` |
| 7 | article §3 | `two` | reagents the paper names, which the 68.4 % coverage figure is a percentage FOR | `aso-offtarget-duplex-energy.json` → `named_reagents`, cross-checked against `aso/fusion-junction-aso-reagent-coverage.json` → `arms` |
| 8 | stratification §2.3 | `Two` | sentences the same paragraph then enumerates and quotes | ⚠ **no artifact; the paragraph's own enumeration** — see "the one document-internal binding" |
| 8 | stratification §2.3 | `second` (reader) | nothing — the PRISMA dual-screening idiom | ⛔ **NONE** — see "left open" |

## The ablation, per sentence

Run with the FULL witness set `claim_ablation.guards_reading` returns for each document (27 → 28
guards for the article, 7 → 8 for the stratification). **BEFORE is the same tree with the two new
modules removed from the witness set**, which is precisely what `guards_reading` returned on
2026-09-02 before this change — one commit, two readings, no file-move race with a sibling seat.

| # | sentence (opening) | before | perturbations tried before | after |
|---|---|---|---|---|
| 1 | *Its length requirement is reported as a DNA gap …* | BLIND | `six->ten, seven->three, ten->six, ten->six` | **RED** on `six -> ten` |
| 2 | *The fourth records the longest contiguous duplex …* | BLIND | `fourth->eighth, six->ten` | **RED** on `six -> ten` |
| 3 | *Each alignment was re-scored on the nearest-neighbour …* | BLIND | `second->fourth` | **RED** on `second -> fourth` |
| 4 | *Only the fusion-versus-parent separation is, and as a floor …* | BLIND | `ten->six, five->nine` | **RED** on `ten -> six` |
| 5 | *Both reagents are phosphorothioate throughout, with wings of five …* | BLIND | `five->nine, two->six, four->nine` | **RED** on `five -> nine` |
| 6 | *That cuts against the screens: a high-affinity chemistry …* | BLIND | `two->six` | **RED** on `two -> six` |
| 7 | *That prices which published junctions the two reagents …* | BLIND | `two->six` | **RED** on `two -> six` |
| 8 | *No database (PubMed, Europe PMC, Embase) was queried …* | BLIND | `second->fourth, Two->Six` | **RED** on `Two -> Six` |

★ **ROW 8 IS THE ONE TO READ CLOSELY, AND IT IS RED ON THE RIGHT PERTURBATION.** The first
perturbation the harness offers that sentence is `second -> fourth`, on "no **second** reader checked
the inclusion decisions" — an idiom, not a count. The guard's first draft located the paragraph by
that clause and therefore went red on it: **a red earned by pinning a spelling**, which is a FALSE
RED in the reassuring direction and is the thing `claim_ablation` exists to detect one level down.
The locator was moved onto the PRISMA clause, which carries no perturbable quantity, and the
sentence now reddens on `Two -> Six` — its actual count — while `second -> fourth` passes through
untouched, as it honestly should.

## ⛔ FOUR NUMBERS LEFT OPEN, AND WHY INVENTING A HOME FOR THEM WOULD BE WORSE

Each of these is stated in a manuscript and reproducible from nothing in this repository. Writing a
guard that hardcodes the current value would make the ablation gate green while binding nothing —
the same failure the gate exists to catch, one level up.

1. **"the two to four per wing taken here as usual"** (article §3). An ADOPTED convention with no
   retrieved record anywhere under `research/`.
   `aso/review-backlog-2026-08-19.md` A5 already names it as one of three uncited literature claims
   in that section, and the prose says "taken here as usual" for exactly that reason. ⭐ The fix, if
   one is wanted, is a RETRIEVAL — the conventional locked content per wing, cited — not a guard.
2. **"The fourth records …"** (article §2). The ordinal of one screen inside a five-item enumeration
   that exists only in that paragraph. No committed artifact orders the five screens, so binding the
   ordinal would mean pinning the paragraph to itself. The sentence is bound through its parent
   COUNT instead, which does have an artifact.
3. **"no second reader"** (stratification §2.3). The PRISMA dual-screening idiom. There is nothing
   for it to be a count of, and asserting the word would prove nothing.
4. ⚠ **A weaker binding, declared rather than counted as a win:** row 3's ordinal is read out of the
   energy artifact's `_why` PROSE, because the stage index is not carried as a field anywhere. If
   `aso_offtarget_duplex_energy.py` ever emits it as a value, this guard should move onto it.

## The count, stated plainly

  · **8 of 8 sentences bound** — every one flips BLIND → RED under its own perturbation.
  · **16 individual quantities** across those eight sentences.
  · **11 derived from a committed artifact** (one of them from artifact prose rather than a field).
  · **1 derived from the document's own enumeration** with no artifact anywhere (row 8's `Two`).
  · **4 left open**, listed above, with the retrieval that would close the first of them named.

## What landed

  · `research/manuscripts/tests/test_the_journal_articles_word_quantities_are_derived.py` — 7 tests.
  · `research/manuscripts/tests/test_the_census_bound_names_the_sentences_it_counts.py` — 1 test.
  · `research/manuscripts/claim-coverage.json` regenerated. ⛔ **It was ALREADY stale when this seat
    started**, on `care-delivery/emc-trial-reachability.md` (committed 41 sentences, live census 43)
    — a sibling seat's manuscript edit, not this one's. The regeneration therefore carries that seat's
    delta too; that is the correct content of the file, and it is named here so the driver is not
    surprised by a path it did not expect in this change.
  · Declared in `research/autonomy/amendments.jsonl` (`**/tests/**` is on `amendment_guard.GOVERNED`).

## The gate readings, and what they are readings OF

`python3 -m pytest research/manuscripts/tests -q` — **1 797 tests, 1 786 passed, 3 failed, 5 errored,
3 skipped, 882 s.** ⛔ **NONE OF THE EIGHT IS ATTRIBUTABLE TO THIS CHANGE, AND THAT IS CHECKED RATHER
THAN ASSERTED — every failure message names a path this seat never opened**, each of which
`git status` shows as modified by a sibling seat in the same checkout:

  · 7 of 8 name `research/manuscripts/care-delivery/emc-trial-reachability.md`, whose sentence count
    moved **43 → 69 while the suite was running**, so `claim-coverage.json` was stale again by the
    time the census-pair guard read it (`test_check_passes_on_the_committed_artifact`,
    `test_claim_coverage_has_not_regressed`, and five setup errors in the same module).
  · 1 of 8 names a `pytest.skip` at `scripts/tests/test_a_promise_with_no_commit_stops_the_turn.py:235`
    (`test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_took`).

⭐ **THE OPERATIONAL CONSEQUENCE FOR THE DRIVER, STATED BECAUSE IT WILL RECUR:** `claim-coverage.json`
is the census's pair with the WHOLE manuscript and test corpus, so any seat editing any censused
manuscript stales it. It was regenerated twice here and went stale between the two runs through no
edit of this seat's. **Regenerate it LAST, after the sibling seats' paths are settled, or the commit
carries a red the tree earned after the run that cleared it.**

The two new modules alone: **8 passed.** The two censused documents' counts are byte-identical to the
pre-change baseline, which is the measurement in the section above.

`./scripts/preflight.sh` (default tier) — **FAILED, exit 1, on two gates, and BOTH are sibling
seats', established by naming the file rather than by inference:**

  · **archive manifest STALE.** Its inventory carries content digests for 515 curated files. Two of
    them are dirty in this checkout — `research/manuscripts/lint_style.py` and
    `research/manuscripts/pinned-figures.json` — and neither was opened by this seat.
    `research/manuscripts/claim-coverage.json`, the one generated file this seat did rewrite, is
    **not in the manifest at all**, so the regeneration contributes nothing to the staleness.
    ⛔ Regenerating the manifest requires a clean tree (`git_tree_is_clean_apart_from_this_manifest`)
    and is the driver's call, not a worker seat's, in a checkout five seats are writing to.
  · **`systems_check` ERROR [D4]:** `research/autonomy/sprint-2026-09-01/S49-BLOCKER-LEVERAGE.md` has
    no frontmatter — another seat's memo. This one has frontmatter and `systems_check` does not
    name it.

Everything else in that run was green, including `lint_consistency` (0 ERROR across 29 files) and
gate 13 (1 107 passed, 65.3 s).
⚠ `PREFLIGHT_TESTS=1` was NOT run separately: its manuscripts suite is the 882 s run reported above,
and re-running it on a tree that moved twice underneath the first one would buy a second reading of
the same sibling-seat failures rather than any new information.

## What this unblocks, and what it does not

It binds the **eight** sentences the ledger row and `s40/ablate-word-only.json` name as blind on
this tree. ⛔ **THAT IS EIGHT, AND S40's HEADLINE IS TWELVE, AND THIS MEMO DOES NOT RECONCILE THEM.**
S40 measured 11 + 1 at full depth on commit `ad87aa4c7`; the word-only re-run this seat inherited
scored 28 sentences on a later tree and found 8 blind, the other 20 already red. Whether the
difference is guards added in between or a different sentence population is an OPEN question, and
answering it costs one `PREFLIGHT_FULL` run rather than an argument.
⛔ So this does **not** by itself license re-stamping `scripts/selector-validation.json`: S40's
condition is a `PREFLIGHT_FULL` that exits 0. Read that run, not this memo, before touching the
record.
