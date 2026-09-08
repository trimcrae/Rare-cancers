# COLLECTION DG1, MV1, FP1 and NA1 — four more distinct papers

Collected 2026-09-08 by the campaign parent. All four `claude-opus-5` throughout, all transcripts
retained and `cmp`-verified.

| worker | paper | tool pairs (observed) | self-reported |
|---|---|---|---|
| DG1 | `degrader/nr4a3-degrader-paper.md` | 42 / 42 | 36 |
| MV1 | `occupancy/nr4a3-monovalent-pocket-route.md` | 23 / 23 | 16 |
| FP1 | `fusion-partner/emc-fusion-partner-stratification.md` | 29 / 29 | 22 |
| NA1 | `neoantigen/fusion-junction-neoantigen-paper.md` | 25 / 25 | 24 |

Observed counts govern.

---

## DG1 — the degrader paper's gate structure

DG1 was sent to hunt a gate that failed as registered and is reported as a pass. **It found the
opposite**, and that is worth recording: Gate 1's own deviation log scores the outcome "a weaker,
basin-breathing pass", and the manuscript reports it as **fail, reformulated**, saying explicitly
"not as a 'weak pass'". The paper is stricter than its own registration. Gate 3B's three replicas at
16.03 / 0.06 / 0.83 kcal/mol are reported as unresolved, matching the artifact's own verdict.

What DG1 did find, and the parent re-derived:

| claim | parent's read | outcome |
|---|---|---|
| the Tier 3 causal test is reported "not run" in three places after it ran | `nr4a3-5aks-reduction.json` → `decision` = **COMPUTED**, `S_kcal` = **−0.1297**, `S_err_kcal` = **0.3264**, `S_err_kind` = `replicate_sd` | **CONFIRMED** |
| the prereg deviation log contains no 3A/3B or harmonization entry | `grep -nE '3A|3B|harmoniz|persistence'` over `nr4a3-druggability-prereg.md` returns **nothing**; the log's last entry is 2026-07-01 | **CONFIRMED** |

**Applied, five.** The Abstract, the §5 falsification table and §4's Limitations all said the causal
test had not been run; all three now report that it ran on 2026-08-02 and returned its pre-registered
null, with the value, the 2σ bound of ≈0.65 kcal/mol, and the statement that because the known-answer
control did not pass this is a null from a method whose resolving power is unestablished — weaker than
a null. §5's two provenance sentences no longer claim the deviation log carries the Gate 3 split and
the post-hoc diagnostics; they say the split is disclosed in the paper and has no entry in that log,
and that the pre-registration itself is unaltered. **No preregistration was edited.**

**DG1's D3 was not applied.** The 8XTT ABFE triple (+8.17 ± 0.98, r1/r2/r3 7.95/9.24/7.32) is cited
only to git `632010e6`, which this shallow clone cannot resolve, and no live leaf holds it. The
comparator resolves cleanly. Supplying the real committed path is an owner act; inventing one is not
available to me. **Recorded, not repaired.**

`lint_style` 1176 before and after — this paper has never had a style pass and does not pass one.

**Coverage is partial and DG1 said so.** §1, §3 Methods, most of §2, most of §4, the references and
the entire SI were not reached. Nothing here clears them.

---

## MV1 — the monovalent pocket route

Two of the three hunted failure modes are **absent**: the paper asserts no functional consequence from
occupancy (it names that gap as its own blocker) and asserts no paralogue selectivity from sequence
divergence (§4.2 argues the opposite way). Recorded as findings, not passed over.

| claim | parent's read | outcome |
|---|---|---|
| the AF-1-retention correction is cited to a leaf that does not hold it | `target-route-census.json.af1_to_lc_swap` holds only lysine/cysteine counts, under a `_question` that still reads "What does the chimera trade when EWSR1-LC **replaces** NR4A3's own AF1?" — the superseded premise | **CONFIRMED** |
| "the two that branch 1b closed" closes one, not two | `nr4a3-program-map.md:2413`: C420 refuted everywhere (0 of 60), **"C559 is NOT"** — surviving at exactly one cell, and the artifact's label is "stronger than its own data" | **CONFIRMED** |
| the test count is stale | `test_nr4a3_monovalent_reach.py` defines **31** tests; the paper said 18 | **CONFIRMED** |
| the corridor collapse | `nr4a3-monovalent-reach.json` → 0 / 37 / 0 / 23 | **CONFIRMED** |

**Applied, five.** The retention correction now points at `nr4a3-exon-audit.json` and names the
residue-composition census as a different measurement built on the superseded premise. §6 states that
only C420 is closed and C559 survives at one cell under through-space, quoting the roadmap's own
"stronger than its own data". The test count is 31, dated and pointed at the file. §2 now states the
cryptic-pocket ceiling in the text rather than only by link — Gate 1 failed as registered, Gate 3B
unresolved, one of five permutation nulls unsupportive, and what survives is basin-internal breathing,
not a demonstrated two-state opening. §6 carries the 8XTT "minority sub-state of unknown weight"
qualifier the owning memo attaches and the paper had dropped.

`lint_style` 127 → 128; one bold emphasis remains from the applied text.

---

## FP1 — fusion-partner stratification

62 quantities dispositioned: 59 MATCH, 2 MISMATCH, 1 NO SOURCE LOCATED. **The known denominator trap
is not present where it was expected**: the prevalence pool is correctly built on partner-assigned
denominators (24 / 57 / 11 / 62 = 154) and labelled as such in all six places, with the 2/1/1/5
residues stated. That is a negative finding worth recording.

The defect is elsewhere, and the parent confirmed it exactly:

| claim | parent's read | outcome |
|---|---|---|
| the outcome pool is not "partner-assigned" | prevalence assigned for Agaram is **24**; the outcome cohort carries **23** (EWSR1 + TAF15), the difference being one TCF12 case | **CONFIRMED** |
| Agaram has no follow-up figure at all | `cohorts[agaram-2014-outcome]` keys are `id, endpoint, label, n_assessable, sourceId, provenance, populationKey, strata, pool, pool_note, follow_up_warning` — **no `n_with_followup`** | **CONFIRMED**; "23 partner-assigned with follow-up" was two errors in one phrase |
| Huang's 50 is not partner-assigned-with-follow-up either | `n_assessable` 58, `n_with_followup` 53; the 50 excludes 2 TCF12 and 1 unidentified | **CONFIRMED** |

**Applied, four.** §3.2's two rows and §3.3's pooled-cohort paragraph now say EWSR1- or TAF15-assigned
rather than partner-assigned, state that the outcome denominator is narrower than §3.5's, and give
n = 73 as 23 + 50 rather than 24 + 57. §4.7's self-contradicting sentence — which called the 50 "the
partner-assigned ones" and then named two TCF12 cases among the excluded — is fixed.

**Not applied.** FP1's D2 (§5 stating the non-overlap argument as established), D3 (the two different
58s) and D4 (what a Wilson interval on summed counts assumes) are all sound and all editorial
judgements about how much caveat a claims section should carry; they go to the paper's owner. FP1 also
notes that the same wording lives in the generator and the artifact, which is a `COHORTS`-table change
requiring regeneration — **not attempted here**, and the prose half is landed knowing the artifact
still carries the old phrasing.

`lint_style` 189 before and after.

---

## NA1 — the fusion-junction neoantigen paper

| claim | parent's read | outcome |
|---|---|---|
| §6 limitation 5 carries the retracted coverage figures as unmarked live prose | the paper's own abstract banner and §3 banner declare ~30% / ~58% / ~16% / 36-79% withdrawn; the artifacts hold 8.51% / 27.37% / 1.78% and a regional range of 1.4–60.4% | **CONFIRMED** |
| the class-II panel is 23 alleles, not 3 | `hla-coverage.json._class_ii_note` | **CONFIRMED**, and the paper's own §3 already said so |
| §4 makes a safety claim its own §1 forbids | §1 warns the novelty filter "compares the junction peptides against those two parent proteins only … never against the human proteome, and no safety claim is made or supported"; §4 said toxicity "is, in principle, not possible" | **CONFIRMED** |

**Applied, four.** §6's limitation 5 now carries the current figures with the retracted ones marked
superseded-and-retained, and names the 23-allele panel. §4(a)'s "acceptability" clause — which the
abstract banner explicitly withdrew — is replaced by a feasibility claim about the platform, with the
withdrawn wording retained as superseded and the bound sized at 8.5% and 27.4%. §4's toxicity sentence
is now a sequence-level rationale that states plainly it is not a safety claim and not a proteome-wide
absence claim, and that off-target risk is untested and a wet-lab question.

**The `TBD` is gone.** The author block follows the sibling convention exactly — name, "Independent
researcher, unaffiliated", correspondence, ORCID — and the **affiliation slot was deleted rather than
filled**, because the repository records no institution, city or country. `Draft (2026-06)` was
removed rather than redated: the frontmatter is `_backfilled: true` with `last_verified: unverified`,
so substituting its date would assert something the file does not support. The satisfied row was
dropped from `submission-residue-baseline.json`, which now reports `2 findings, 2 baselined, 0 NEW,
0 stale`.

**Not applied.** NA1's D5: "~90%" and "~16% TAF15" are true against repository sources (Bangerter
PMID 36316541 says **>90%**, for NR4A3 rearrangement with *any* partner; the 16% comes with PMID
36948401) but neither citation is in this paper's reference list. That is a citation decision for the
owner.

`lint_style` 108 before and after, after seven bold emphases from my first pass were stripped.

---

Across all four: `lint_consistency` 0 ERROR across 29 files; `lint_claims` 0 ERROR with 31
pre-existing WARNs; `lint_submission_residue` exits 0 with no stale rows. No producer, figure
generator, MD or docking job was run; no artifact, preregistration or guard was edited. No verdict
generalises beyond its own paper.
