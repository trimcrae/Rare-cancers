---
id: DOC-ASSESS-EMC-PROGRAM-1-FINDING-20260909
title: "ASSESS-EMC-PROGRAM-1 — independent methods and evidence assessment of the EMC-PROGRAM-1 roadmap audit: structure and arithmetic verified, two of three falsifications over-called"
level: L4
kind: assessment-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ASSESS-EMC-PROGRAM-1
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
subject: research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/EMC-PROGRAM-1
subject_target: research/manuscripts/program/emc-treatment-roadmap.md
---

# ASSESS-EMC-PROGRAM-1

⛔ No wet lab, no EMC observation, no efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim, no treatment recommendation, no patient-specific advice. Every DepMap and
expression figure named below is a screen statistic on a public cell-line panel. No network, no GPU,
no paid API, no publication, no outreach, no `git add/commit/push`, no `preflight.sh`, no subagent.
Every write is inside this directory. **The subject lane's files were read only and not modified;
nothing in `EMC-PROGRAM-1/` was overwritten, and the manuscript was not touched.**

This is an assessment of an audit, not a re-audit of the manuscript and not a review of MF1, P-ST,
TCIP or FP, which are closed.

---

## Verdicts at a glance

| # | Question | Verdict |
|---|---|---|
| 1 | "Owns zero routes, everything is inherited" | **SUPPORTED** |
| 2 | The three FALSIFIED verdicts | **OVERSTATED** (one of three sound; two over-called) |
| 3 | §4.2 rank-not-maximum, and "the conclusion survives" | **SUPPORTED-WITH-QUALIFICATION** |
| 4 | The UNSUPPORTED-BY-CITED-ARTIFACT rows | **SUPPORTED** |
| 5 | Does the diff overreach or underreach | **SUPPORTED-WITH-QUALIFICATION** (one hunk overreaches, one paragraph underreaches) |

---

## 1 · "Owns zero routes; every claim is inherited" — **SUPPORTED**

Verified directly, not taken from the audit.

`systems/graph/publications.json` holds 33 publications. `PUB-EMC-PROGRAM` is one of them
(`state: drafted`, `target_venue: journal_submission`, `document.file:
research/manuscripts/program/emc-treatment-roadmap.md`). The publication record carries **no route
list of its own** — route membership lives in `systems/graph/routes.json`, where a route's
`publication` field is an object `{endpoint, role, contribution}`.

Of the **83** routes in `routes.json`, exactly **two** name `PUB-EMC-PROGRAM`, and both carry
`role: "context"` (check 02, check 03):

* `RT-TRABECTEDIN` — *"Cited to establish current care and the categorical gap. Explicitly not this
  program's contribution."*
* `RT-ICI-TKI` — *"The comparator arm … cited to size the gap rather than analysed. Promoting it to a
  contribution would overstate what was done."*

Owned (non-context) routes: **0**. I also checked the other six graph files that could carry an
alternative ownership edge — `claims.json`, `evidence.json`, `artifacts.json`, `lanes.json`,
`plan.json`, `roadmap.json` — and `PUB-EMC-PROGRAM` appears in **none** of them (0 occurrences each).
There is no second place where this publication could own evidence.

The structural fact is therefore exactly as claimed, and it is load-bearing: an umbrella paper that
owns nothing must be audited by following its citations outward, which is what the subject lane did.
The framing is right.

*(One nuance the audit does not state: `outcome_potential_why` in `publications.json` already records
this correction, dated 2026-08-09. The audit rediscovered a fact the graph had already written down —
which strengthens rather than weakens it, but the audit presents it as its own structural finding.)*

## 2 · The three FALSIFIED verdicts — **OVERSTATED**

One of the three is sound and exact. Two are over-called. Over-calling a falsification is the failure
mode the assessment brief names, and it is present here.

### C12 — the WIP status of the de-novo warhead arm: **SUPPORTED. Falsified is the right word.**

The roadmap says it in three places (check 10): line 38 lists *"de-novo selective-warhead/binder
design"* among *"the in-silico results we are running"*; line 55 heads it *"In progress (pipelines
built, results pending)"*; line 289 repeats *"De-novo selective-warhead/binder design is scored
against NR4A1/2"* under *"What we are running (WIP, pipelines built, results pending)"*.

`nr4a3-program-map.md` says the opposite in the same repository (check 09):

> **Route A — a warhead engaging paralogue-divergent pocket handles · ○ blocked, nothing running**
> ⚠ *Superseded, retained:* this heading read *"◐ in work"*. **Nothing on Route A is running or has
> ever run.**

with Route B *"blocked on `R5`, nothing running"* and Route C *"parked, nothing running"*. This is a
status claim, it is binary, the two repository documents contradict each other outright, and the
program map is the arm's own page. **FALSIFIED is correct and the evidence is exact.** This is the
strongest result in the subject audit.

### C03 — the FET-fusion class prior: **OVERSTATED. The right verdict is NARROWED or UNSUPPORTED.**

The numbers reproduce. `PUB-MTAP-PRMT5/fet-class-transfer-test.json` (check 08) gives, for PRMT5,
`fet_comparator_vs_nonfet`: t = **−0.16**, Δ mean z = **−0.0075**, 95% CI **[−0.1008, +0.0859]**,
Monte-Carlo two-sided p = **0.87255** (200,000 draws, seed 20260908), n = 17 vs 12. Every figure the
ledger quotes is in the artifact. That part is clean.

The problem is the **construct**, and it is a real one:

1. **The test does not measure fusion addiction.** It measures whether a *PRMT5 transcript-abundance*
   z-score differs between a FET-fusion comparator and non-FET comparators on GSE24369/GPL6244.
   Fusion addiction is a *dependency* property — whether removing the fusion kills the cell. A null
   on a metabolic-axis expression contrast is not evidence against a dependency premise. Absence of a
   class-level PRMT5 signal and presence of class-level fusion addiction are entirely compatible.
2. **The FET comparator class is one disease.** `fet_comparator: "LGFMS"` — a single entity
   (FUS::CREB3L2). A class prior over FET-fusion sarcomas is not falsified by one member of the class
   failing to separate on one gene.
3. **The roadmap already fences the claim.** Its actual §4.1 text (check 13) reads: *"we report a
   class-level prior, and we are explicit that it is only that … the analogy raises the prior without
   proving the case. The decisive experiment we hand to others is the dTAG acute-degradation
   viability test."* The subject audit records the roadmap's other explicit refusals as STANDS; this
   one it does not credit. A prior that the paper itself declares unproven and gates on a named wet
   experiment is not falsified by a null on a different axis — its support is weakened, which is what
   NARROWED means.

The subject FINDING's own wording concedes the boundary — *"carries no class-level signal **on the one
axis this program can test**"* — but then lists the row as FALSIFIED in the ledger, in §4.2 of the
FINDING and in the document title. The qualifier and the verdict do not agree. Furthermore, **"the one
axis this program can test" is itself wrong**: the roadmap's primary support for the class prior is a
DepMap *dependency* axis (FLI1 gene effect −0.934, 0.741 dependent, n = 27), which the same audit
re-derives and marks STANDS at C02. That axis is both testable in this repository and far closer to
fusion addiction than PRMT5 mRNA. The audit leaves it standing and simultaneously asserts no testable
axis exists.

**Assessed verdict for C03: NARROWED — the FET class prior is a stated, self-fenced prior whose one
available class-transfer probe on an adjacent axis returned null (p = 0.873, CI spanning zero).** The
correct headline is "the class step has no positive support and one adjacent null", not "falsified".

### C16 — the inherited no-overlap selectivity sentence: **OVERSTATED as attributed.**

The underlying DEGRADER-2 result is sound and I do not dispute it (check 11): three NR4A3 C397 frames
sit at or below the paralogue reference, pairwise dominance 0.9993 against 825 paralogue observations,
and that fraction is a geometric ranking statement, not evidence of selective labelling. DEGRADER-2
falsified a "no overlap" sentence with an exact count.

But that sentence **is not in the roadmap.** Grepping the manuscript for *overlap*, *separation* and
*paralogue* (check 12) returns exactly two hits, neither of which is a separation claim: line 275, the
asymmetric NR4A1-hard / NR4A2-soft design constraint, and line 284, *"This is a specification for the
warhead, not a demonstrated property."* Both are the correctly fenced sentences the audit itself
records as STANDS at C14. The roadmap's only contact with the degrader paper's selectivity output is a
blanket citation — *"cites that paper for the degrader's in-silico outputs"* (line 292).

So the exposure is real but it is **citation hygiene**, not a falsified roadmap claim: an umbrella that
cites a paper wholesale inherits a sentence that paper has since retracted. Listing it as one of "three
falsified roadmap claims" attributes to this manuscript a sentence it does not contain, and
double-counts DEGRADER-2's result as a second lane's finding.

**Assessed verdict for C16: SUPPORTED as a DEGRADER-2 result; OVERSTATED as a roadmap claim.** The
honest row is "the roadmap's blanket citation of `nr4a3-degrader-paper.md` now carries a sentence
DEGRADER-2 falsified; the roadmap should cite the corrected statement rather than the paper".

### Net effect

The headline "three FALSIFIED" should read **one falsified (C12, a status contradiction, exact and
undeniable), one narrowed (C03), one inherited-by-citation (C16)**. The audit's substantive concerns
survive in every case — nothing here restores support the audit removed — but the strength of the word
is wrong on two of three, and the paper's title and abstract carry the wrong count.

## 3 · The §4.2 rank-not-maximum finding — **SUPPORTED-WITH-QUALIFICATION**

Re-derived independently from `research/modalities/aso-insilico-evaluation.json` (checks 04, 05).

The five `top_designs` carry `site_accessibility` **0.353, 0.369, 0.417, 0.338, 0.381** — the audit's
list, in order, digit for digit. **Maximum = 0.417.** The manuscript (line 322, check 06) reads *"The
junction sites are **poorly accessible** (best ≈0.35 unpaired probability)"*. Under the natural reading
of "best" — the most accessible site in the set — the stated statistic is wrong; 0.353 belongs to
`top_designs[0]`, the top-**ranked** entry.

The `ranking_key` is stored verbatim in the file:

> `"fewest gapmer off-targets > most accessible site > fusion-specific siRNA seed > lower RISC seed
> load > balanced junction > mid-GC > no G4 > fewer CpG"`

Off-target count is the **first** sort key, accessibility only the second, and the designs' `offtarget_le1mm`
values run **8, 16, 17, 58, 95** in file order — strictly ascending, confirming the file is sorted on
off-target count, not accessibility. The audit's mechanism is exactly right: the sentence reports a
rank, not a maximum.

**"The conclusion survives" — supported, with one qualification the audit does not state.** All five
values lie in 0.338–0.417, so the maximum is only ~0.06 above the quoted figure and the qualitative
reading is unchanged by the correction. However, **no calibrated threshold for "poorly accessible"
exists anywhere in the artifact**: the `accessibility` block records only `status: "ok"`,
`window_mRNA_span [702, 882]`, `window_len 180` — no cutoff, no comparator distribution, no reference
set. "Poorly accessible" is an unbenchmarked judgement in both the original and the corrected text.
That is a pre-existing weakness of the manuscript, not one the audit introduced, but "the conclusion
survives" is a statement about a conclusion that has no stated bar to survive against, and the audit
should say so.

The audit's related observation is also correct: `n_candidates_fusion_specific_sirna_seed = 2`, and the
two designs with `sirna_seed_spans_junction: true` are exactly the two at 81.2 % GC carrying 58 and 95
one-mismatch off-targets. The design goal and the specificity bar are anti-correlated in this set.

## 4 · The UNSUPPORTED-BY-CITED-ARTIFACT rows — **SUPPORTED**

Three spot-checked, including the one named in the brief. I specifically looked for support living in
an artifact the ledger did not follow. In every case, it does not.

**C18, "B7-H3 internalises" — fair, and in fact stronger than the ledger states.** The manuscript's
§4.2 (line 335) says B7-H3 *"internalises (§5)"*; §5 (line 356) says B7-H3 *"supplies the internalising
handle the §4.2 delivery proposal borrows"* and cites only the DepMap expression read plus the IHC
prior and the existence of clinical B7-H3 agents. The chain is circular (§4.2 → §5 → §4.2) and
terminates in an expression measurement, which cannot report endocytosis.

Searching the whole repository for *internalis/internaliz* (check 14) turned up the artifacts that
could have carried the support, and they say the opposite (check 15):

* `research/modalities/aso-delivery-antigen.json`, `_language_discipline`: *"⛔ NOTHING HERE ASSERTS
  EFFICACY, SAFETY, SELECTIVITY, A THERAPEUTIC WINDOW, ANTIGEN DENSITY, **INTERNALISATION** OR CLINICAL
  READINESS, AND NO SUCH QUANTITY IS COMPUTED ANYWHERE IN THIS MODULE."* Its explicit limits list:
  *"**INTERNALISATION.** An AOC must be endocytosed to release its oligonucleotide; **nothing in this
  repository measures endocytic rate for any antigen**."* Its `still_cannot_say`: *"That any antigen is
  a delivery handle."*
* `research/modalities/alcam-precedent.json` treats internalisation as a *literature* property
  requiring a dedicated antibody-uptake study (PMID 15769845, for ALCAM) and contains **no** CD276
  record at all.

So the support does not exist in the cited artifact, in any adjacent artifact, or anywhere in the
repository — and the repository already carries a standing statement that the quantity is unmeasured.
C18 is correct and could have been stated more strongly.

**C19, the vital-tissue screen — fair, verified exactly (check 19).**
`research/modalities/emc-surface-normal-window.json` contains **45** `"vital_tissue"` keys and **45**
occurrences of `"vital_tissue": []`. Every scored row is empty; none has ever been screened. The CD276
record shows the mechanism: `"rna_tissue_specific_nTPM": null` → `"vital_tissue": []`. The file's
`vital_tissues_flagged` list (heart, cerebral cortex, …) is a list of tissues the producer *intended*
to flag, which is easy to mistake for a screen result and is not one. The audit's claim is precise.

**C13, "4 of the 5 engageable distinguish NR4A2" — fair (checks 17, 20).** In
`research/modalities/nr4a-selectivity.json` the pocket spanning resid 406 has `n_divergent: 7` with
`selectivity_handles` L406, T407, T410, R412, I484, I531, L534. The per-residue records show I531 as
`nr4a1: "V"`, `nr4a2: "I"` — divergent from NR4A1, identical in NR4A2. So 7 differ from NR4A1 and
**6 of 7** from NR4A2, as the ledger says. The string `"engageable"` occurs **nowhere** in the file, so
the 5-member subset and the 4-of-5 step genuinely cannot be derived from the cited artifact. The ledger
is also fair in the other direction: it flags the row as *"consistent with program-map §2.4"* rather
than calling the claim wrong. That is the correct treatment of support living in a different file, and
it is the pattern I was checking for elsewhere.

The rows are fair. On this item the audit did the work it claims to have done.

## 5 · Does the diff overreach or underreach — **SUPPORTED-WITH-QUALIFICATION**

The diff is seven hunks over 107 lines, patching C25, C23, C24, C03/C04/C05, C12, C09 and C18/C19. All
corrections are additive with `(Superseded, retained: …)` markers preserving the original wording,
which matches the repository's house convention and is the right form for a correction to a document
others cite.

**The split is broadly defensible.** The unpatched rows divide cleanly: C13 and C22 are cases where
support exists in a *different* artifact or is *narrowed* rather than absent, so a citation fix rather
than a prose correction is the appropriate remedy; C06 is a direction that holds at the stated cut.
Patching only where the cited support fails outright, and leaving citation-hygiene items to the owner,
is a coherent rule.

**Two defects, one in each direction.**

*Overreach — hunk 4, the FET block.* Its bolded heading reads *"the FET-class step of this prior is
**FALSIFIED** in owned data"* and its body asserts *"not supported on the one axis this program can
test."* Both inherit the item-2 problem: the evidence is a PRMT5 transcript contrast with a
single-disease FET comparator, and the roadmap's own DepMap dependency axis — retained two paragraphs
above in the same patched file — is a more direct test of the same premise. Applied as written, the
manuscript would carry, in adjacent paragraphs, a retained FLI1 dependency reading supporting the class
prior and a new paragraph asserting the prior is falsified with no testable axis. The other two limbs
of the hunk are good: the EWSR1 pan-essential correction (selectivity +0.373 but dependency in 96.7 %
of sarcoma and 91.5 % of other lines) and the fixed-threshold caveat (`dependent_threshold = −0.5`, no
interval) are accurate and well-labelled. **Recommendation: retitle the hunk to a narrowing and delete
"the one axis this program can test."** Nothing else in the diff needs to change for that.

*Underreach — the §4.2 results paragraph.* The diff opens that paragraph to correct the accessibility
figure (C09) and leaves the two sentences immediately after it untouched: the flat *"~75 %"* (C10 —
the artifact holds two values, 75.0 on three designs and 81.2 on two) and the bare *"only 2 of 5 place
the RISC seed across the junction"* (C11 — which the ledger itself marks *"STANDS (materially
incomplete as written)"* because those two are exactly the 81.2 % GC designs carrying 58 and 95
one-mismatch hits). This is the flagship tumour-specific route, the anti-correlation is the most
actionable single fact in the section, and the diff is already editing the same three lines. Leaving
them produces a paragraph that is precise about the third decimal of accessibility and silent about the
design trade-off. **This is the weakest editorial judgement in the package.**

*One bookkeeping error.* FINDING.md limitation 4 lists **C05** among the rows *"deliberately not
patched"*. C05 **is** patched — it is limb (iii) of hunk 4 (*"the 74 % figure above is recorded at one
fixed cut … carries no interval"*). Five rows are unpatched, not six.

**No patched wording overstates the correction elsewhere.** The C09 hunk keeps *"poorly accessible"*
and adds the five values — accurate and not overreaching. The C18/C19 hunk removes *"internalises"* and
*"a logical EMC delivery vector"*, keeps the near-universal expression that C17 verifies, and states
the 45-row vital-tissue fact exactly as the artifact holds it. The C23 rewrite (*"the framework
identifies exactly one EMC target test … as the next check on the route"*) genuinely removes the
clinical-readiness ordering without asserting anything new. The C24 and C25 removals are supported
independently of the contested C03 — C12 (nothing running) and C19 (unfired vital-tissue screen) alone
justify striking *"de-risked"*.

---

## What I checked, and what I did not

**Checked** (20 attempt directories, all preserved, including one failure): the graph structure in
`publications.json` and `routes.json` plus six other graph files; the three FALSIFIED verdicts against
their cited establishing evidence (`fet-class-transfer-test.json`, `nr4a3-program-map.md` Routes A/B/C,
DEGRADER-2's FINDING) *and* against the roadmap's actual sentences; the five ASO accessibility values,
the `ranking_key`, the off-target ordering and the GC/seed structure; the vital-tissue tally at row
level and the CD276 mechanism; the NR4A2 residue identity at I531 and the absence of "engageable" from
the cited artifact; a repository-wide search for internalisation support; and every hunk of the diff
against the manuscript text it edits.

**Not checked — limitations.**

1. **Nine of the 28 ledger rows were not independently re-derived** (C01, C02, C07, C08, C14, C15, C17,
   C20, C21, C26–C28). The subject lane's `checks/01` reports them reproducing exactly and the four I
   sampled indirectly were consistent; I did not re-run `rederive_roadmap_numbers.py`.
2. **`git apply --check` was not re-run.** The subject lane records exit 0 at its read time; I could not
   confirm it independently because the Bash tool became unusable (below). Whether the diff still
   applies to the current tree is **unknown**, not verified.
3. **The Bash tool failed permanently mid-lane** with ENOSPC on the harness temp filesystem
   (`/tmp/claude-0/…/tasks`, 0 MB free) — every invocation from that point, including `echo ok`,
   returned no output. Recorded verbatim as `checks/18-FAILED-bash-enospc/`. **Nothing was deleted to
   free space**: CLAUDE.md §8 forbids freeing disk by removing campaign evidence, and the resource
   problem is reported here instead. Checks 19 and 20 were completed with the Read/Grep tools; they
   carry a `command.txt` describing the tool invocation rather than a shell line.
4. **I assessed support, not biology.** Where I disagree with a FALSIFIED verdict I am saying the word
   is too strong for the evidence offered, **not** that the underlying claim is true. Nothing in this
   lane is an EMC observation, and no route is stated to be or not to be viable.
5. **I did not assess C28** (the categorical-gap claim) or open `emc-clinical-registry.json`; editing or
   reading the clinical registry is outside this lane and `systems/POLICY-evidence.md` governs it.
6. Concurrent writers share this checkout; every reading above is one read at 2026-09-09.

## Bottom line for the subject lane

The audit is a real result and most of it holds. Its structural premise is independently verified, its
arithmetic re-derivations are exact where I sampled them, its §4.2 rank-not-maximum finding is right
and correctly mechanised, and its UNSUPPORTED rows are fair — the B7-H3 internalisation row is
understated if anything. The defect is verbal and it is concentrated: **two of the three
falsifications are over-called**, one because the counter-evidence tests a different construct from
the claim (C03) and one because the falsified sentence is not in the audited manuscript (C16). That
error propagates into the audit's title, its abstract, and the heading of the diff's largest hunk.
Fixing it costs three sentences and does not weaken a single one of the audit's substantive findings.

## Stop condition

Reached. Five verdicts returned with evidence, every attempt preserved including the tool failure, no
subject-lane or manuscript file modified, nothing published. The next step belongs to the subject
lane's owner or the coordinator: retitle C03 and C16, correct the C05 bookkeeping line, decide whether
to extend the §4.2 hunk over C10 and C11, and re-run `git apply --check` before any application. **This
lane recommends no application of the diff and takes no publication act.**
