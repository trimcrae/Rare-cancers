---
id: DOC-SPRINT-S36-NULL-DISCLOSURE
title: "S36-NULL-DISCLOSURE — §7 disclosed the absence of a null that now exists and runs against the screen; the disclosure is replaced with the measurement, at its true weight in both directions"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S36-NULL-DISCLOSURE — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S36-NULL-DISCLOSURE — the vaccine paper's missing null is no longer missing, and it runs the other way

**Item(s):** S24-CALIBRATION's proposed ledger row 5 (*"§7 says the screen has no decoy control and no
null expectation. It now has both, and the screen sits BELOW the null."*) and its row 6 (the decoy pass
rate at a presentation percentile of 0.5); route `RT-VACCINE-COMBINATION`, publication
`PUB-VACCINE-PATH`, strategy `ST-IMMUNO`.

**Owned paths:**

1. `research/manuscripts/neoantigen/emc-vaccine-development-path.md`
2. `research/manuscripts/neoantigen/emc-vaccine-path-aixiv-metadata.json` — **conditionally granted, and
   the condition did NOT fire.** My edits do not touch the abstract (proved in §5), so I did not
   regenerate it. ⚠ It is nevertheless STALE at `HEAD`, from somebody else's landed abstract edit — §5.
3. `research/autonomy/sprint-2026-09-01/S36-NULL-DISCLOSURE.md` — this file

**Started (UTC):** 2026-09-01T20:44Z **Finished (UTC):** 2026-09-01T21:22Z **Real-dollar cost: $0.**

---

## Verdict

**FIXED.** §7's sentence *"with no decoy control and no null expectation"* and its consequent *"the calls
that pass are therefore reported as what the screen returned rather than as an enrichment over chance"*
were **replaced** — not annotated, not appended to — with the null that now exists, what it returned,
and what it does and does not license. **The deviation from chance is negative**: the screen presents on
4 of the 34 panel alleles where a random length-matched set of its own size presents on a median of 23,
and no one of 2,000 random sets fell as low as 4.

⛔ **Written at its weight in both directions, which was the hard part.** It is not a refutation of the
four strong calls — a set can fall below a random background and still contain real binders — and it is
not a virtue of conservatism. It says the coverage figure carries no enrichment signal, and it says so
in the section that until now disclosed the control as missing.

Four further defects were found by the sweep the prompt asked for and all four are fixed: the §3 limits
table and §B1 both stated the coverage figure with no reference to the null; §B3 named **five**
restricting alleles where the committed artifact restricts on **six**; and Appendix C's own row carried
the same five, which is the one-of-a-pair defect that appendix already records once against itself.

---

## 1 · What I measured — the headline reproduced, not relayed

⛔ **The prompt's instruction was not to write a figure into a manuscript from a seat report.** Every
number in the new §7 text was recomputed here from committed inputs or from the artifact itself.

### (a) The artifact, and which run wrote it

`research/modalities/vaccine-threshold-calibration.json` is **not in this working tree and not on
`origin/main`** — only its generator is:

```
$ git ls-tree origin/main --name-only research/modalities/ | grep -i threshold
research/modalities/coverage-threshold-curve.json
research/modalities/coverage_threshold_curve.py
research/modalities/lint_derived_thresholds.py
$ git ls-tree origin/main --name-only research/modalities/ | grep vaccine_threshold
research/modalities/vaccine_threshold_calibration.py
```

I fetched the artifact through the GitHub API from the branch that carries it —
`claude/s24-threshold-calibration`, blob at commit `43584e000f10d1386c6f01d47b1c961c39054685`, artifact
`_utc: 2026-09-01T20:31:04Z`. That is a **later run than the one S24 §5(a) reports**, and arm D comes
back identical to it, which is a stronger provenance than a single run: the same decoy null reproduced
across two runs on two commits.

⚠ Its calibration arm is still **WITHHELD** and I quoted none of it:
`_fusion_fetch_is_complete: false`, `verdict.finding: "WITHHELD. The IEDB fetch did not complete…"`, and
the recorded errors are a **new** IEDB failure mode (`"Query string appears to include an offset
parameter without an order parameter"` — HTTP 400, PostgREST refusing unordered paging), not the
`Errno 110` of run 1 nor the two schema defects of run 2. §6.1 step 1 of the manuscript is therefore
untouched and still open.

### (b) The screen's own side, recomputed from the committed tree

```
$ python3 -c "…epitope-allele-matrix.json…"
rank_column: presentation_percentile   n_peptides: 174   panel size: 34
presenting_alleles: ['HLA-A*01:01', 'HLA-A*30:02', 'HLA-B*07:02', 'HLA-B*15:01']   -> 4
```

The 174 peptides and their length multiset were rebuilt from `fusion-breakpoint-neoantigens.json`
through `coverage_threshold_curve.LENGTHS`, not read from S24's prose:

```
LENGTHS [8, 9, 10, 11]   CONVENTIONAL 0.5   LOOSE 5.0
n peptides 174   by length [(8, 36), (9, 41), (10, 46), (11, 51)]
```

So the decoy pool's 360/410/460/510 = 1,740 is exactly ten times the screen's own composition, and
1,740 × 34 = **59,160** peptide-allele tests. Both checked arithmetically against the artifact's own
`n_peptide_allele_tests`.

### (c) The null, recomputed

| quantity | my computation | artifact |
|---|---|---|
| pass rate at the conventional cut | 381 / 59,160 = **0.6440%** | `0.00644` |
| exact 95% CI (Clopper–Pearson, `scipy.stats.beta`) | **0.58114% – 0.71180%** | `[0.005811, 0.007118]` |
| mean presenting alleles over 2,000 draws | **22.619** (recomputed from the draw histogram) | `22.619` |
| median / min / max | **23 / 7 / 33** | `23 / 7 / 33` |
| closed form `34 × (1 − (1 − p)^174)` | **22.95** | — (S24 quotes 22.95) |
| draws at or below the observed 4 | **0 of 2,000** | `p = 1.0` |

⭐ The closed form and the bootstrap agree to 0.33 alleles, which is what makes this arithmetic rather
than a resampling artefact — and the Clopper–Pearson interval reproduces from an independent
implementation (`scipy`) against S24's hand-rolled regularised incomplete beta, which is the check its
own §4(c) says that code most needed.

⚠ **The 0.5 row read twice, because it is a second finding and not decoration.** A *presentation
percentile* of 0.5 is by construction meant to admit about 0.5% of random peptides. On this
length-matched human-proteome background it admits **0.644%, with the interval excluding 0.5%**. Small,
measured, and in the direction that makes the cut more permissive than its name.

### (d) Six restricting alleles, from the committed artifact rather than from S25's report

```
$ python3 -c "…junction-selfsimilarity.json → every predicted_binders[].allele and
              strong_on_34_allele_panel[].allele…"
ALLELES: ['HLA-A*01:01', 'HLA-A*30:02', 'HLA-B*07:02', 'HLA-B*15:01', 'HLA-B*35:01', 'HLA-B*44:02']  -> 6
{'HLA-A*01:01': 5, 'HLA-B*07:02': 4, 'HLA-B*15:01': 4, 'HLA-A*30:02': 1, 'HLA-B*35:01': 1, 'HLA-B*44:02': 1}
```

§B3 named five of those six. The missing one, **HLA-A\*30:02**, is the allele the paper's own abstract
names as the lead peptide's second presenting allele.

---

## 2 · The sweep the prompt asked for — every place the coverage figure is stated

⛔ *"A corrected §7 beside an uncorrected abstract is worse than neither."* The sweep was run over the
whole file rather than over the sections I expected to find it in.

```
$ grep -n -i "chance|enrich|null|decoy|random|expectation" emc-vaccine-development-path.md
```

**Finding: no other sentence in the paper claims or implies enrichment over chance.** The words
"enrichment over chance" occur exactly once, in the §7 sentence I replaced. The abstract does not claim
it; §B1's proposition does not claim it; §2.2 compares the out-of-frame calls to the in-frame calls and
not to a background. So there was no second home of a *false* claim to correct — but there were two
homes of the coverage figure that a reader would now meet without knowing a null exists, and both are
now pointed at §7 **without restating its numbers** (CLAUDE.md §1: one fact, one place):

| where | what changed |
|---|---|
| §3 limits table, row B1, "Best available answer today" | gains `; below a length-matched decoy null, per Section 7` |
| §B1, **Evidence** | gains one sentence: Section 7 reports the null these figures are measured against, and the screen falls below it rather than above it |

⚠ **One thing the sweep found that I did NOT write into the paper, deliberately.** §2.2 reports the
out-of-frame screen — 97 peptides, 10 strong calls across 8 alleles — and says those calls are "tighter
than anything the in-frame junctions produce". That relative statement is unaffected. But **the
out-of-frame screen has no null of its own**: arm D was drawn to the in-frame set's size and length
composition, so extrapolating its pass rate to a differently-composed 97-peptide set would be an
unmeasured claim. Proposed as a ledger row in §7 below rather than asserted here.

---

## 3 · What I changed, path by path

### `research/manuscripts/neoantigen/emc-vaccine-development-path.md` — 6 edits

1. **§7, the replacement.** The two sentences disclosing the missing control and the one asserting the
   B3 search is "the one analysis here that carries a null" are **gone**, replaced by: the null's
   construction (10 decoys per junction peptide, same reviewed proteome as the novelty search,
   length-matched to 36/41/46/51, same panel, same percentile column); its pass rate with its exact
   interval and the instrument reading that falls out of it; the 2,000-draw resample against the closed
   form; the observed 4; the negative deviation; and then, in the same paragraph rather than in a
   footnote, **four things it does not license** — it bounds the screen and not any peptide in it, it
   does not say the four strong calls are false, it is predicted binding against predicted binding
   rather than evidence about presentation, immunogenicity, safety or benefit, and it is computed at
   the same undefended cut as the calls it is a null for.
   ⭐ **Two limits of the null are stated that S24 flagged and that a softer write-up would have
   dropped:** its decoys are arbitrary peptides of matched length and not composition-matched shuffles,
   so it does not separate this junction from the amino-acid composition of the peptides spanning it;
   and its decoys are self peptides drawn from the very proteome those peptides were filtered against,
   which is the background the percentile scale is defined against and is not a background of
   neoantigens.
   ★ The B3-null sentence is retained in substance and rewritten: B3 "carries its own null for the same
   reason a binding screen needs one", which is true where "is the one analysis here that carries a
   null" is now false.
2. **§3 limits table, row B1** — points at the null (above).
3. **§B1, Evidence** — points at the null (above).
4. **§B3** — `HLA-A\*01:01, B\*07:02, B\*15:01, B\*35:01 or B\*44:02` → the same list **with
   `A\*30:02`**, six alleles. The sentence's claim ("is not established here") is untouched: this seat
   corrected the *count*, and applying S25-P1-ANCHOR's measured answer is a separate queued row that I
   did not take.
5. **Appendix C, last row** — "no allele-specific motif for the **five** restricting alleles" →
   **six**. Second home of the same defect, in the appendix whose own text records the one-of-a-pair
   failure mode.
6. **Appendix C, new row** — the §7 withdrawal, recorded under the paper's own convention that *"a
   correction that leaves no trace is indistinguishable from a claim that was never made"*, and stating
   in the row itself that the finding bears on the screen and not on whether any of the four strong
   calls is real.
7. **§8 Methods** — names `vaccine_threshold_calibration.py` and `vaccine-threshold-calibration.json`,
   and records that the module imports its lengths and its cut from `coverage_threshold_curve.py` and
   its proteome fetch from `junction_proteome_novelty.py`, so the null and the screen it is a null for
   cannot be computed against different conventions.

⛔ **What I did NOT touch, and why.** The abstract (no false claim there, and its P1 conditional belongs
to S25's queued row); §6.1 step 1 (the calibration proper is still WITHHELD, so the step is still open
exactly as written); §B3's inverted-clause correction and its conditional near-self null, both landed
tonight by S20 and left intact; `shared-vs-individualized-neoantigen-evidence.md` (not mine).

### Nothing else

No other file was written. **No git write command was run at any point.**

---

## 4 · Measurements the prompt asked to be reported

### Word count

| | words (`wc -w`) | main text (`lint_style`) |
|---|---|---|
| before | 20,848 | 17,888 |
| after | **21,350** | **18,257** |
| delta | **+502** | **+369** |

⚠ **This paper is not under a word ceiling** — `test_a_hardening_round_may_not_grow_the_paper.py`'s
`WORD_CEILING` names only `fusion-junction-aso-journal-article.md`, read from the file rather than
assumed. The growth is nonetheless real and named: a disclosure of an absent control is one clause,
and a measured null with its interval, its resample, its closed-form cross-check and its four
non-licences is not. The Appendix C row and the §8 provenance paragraph are the rest.

### Caution-marker census, every delta located

`lint_readability.py --caution`, before → after: **200 → 205 markers**, 11.6 per 1,000 words in both.

| marker | before | after | delta | where it came from |
|---|---|---|---|---|
| `is not` | 58 | 59 | **+1** | §7: "is not evidence about presentation, immunogenicity, safety or benefit" |
| `does not` | 38 | 40 | **+2** | §7: "the null does not say the four strong calls are false"; "does not separate this junction from the amino-acid composition…" |
| `cannot` | 29 | 30 | **+1** | §8: "cannot be computed against different conventions" |
| `limitation` | 0 | 1 | **+1** | §7: "so it inherits that limitation rather than removing it" |
| every other marker | — | — | **0** | unchanged, all 16 others |

⛔ **No marker fell.** The two sentences I removed were themselves caution sentences, and each hedge in
them is carried forward in a stronger form: "no decoy control and no null expectation" became a null
that exists and a stated direction; "reported as what the screen returned rather than as an enrichment
over chance" became "not an enrichment over chance in either direction: the deviation is negative";
"a shuffle null … would need a defended threshold to be a null of anything" became the surviving,
narrower and now *true* caveat that this null is computed at the same undefended cut and is not a
composition-matched shuffle. The `scientific-writing` §4 failure — readability bought by dropping
caution — did not occur, and the direction of travel is the opposite one.

### Over-ceiling sentences (`lint_readability.py --check`, >60 words)

**4 → 3.** The one removed is the 63-word §7 sentence beginning *"The near-self search of B3 is the one
analysis here that carries a null…"*, split in the replacement.

The three remaining, unchanged by me and each named:

| line | words | what it is |
|---|---|---|
| 640 | 87 | §B3, the anchor/contact ordering sentence — **corrected tonight by S20** and due to be rewritten again by S25's queued P1 row. Splitting it now risks disturbing a landed correction and collides with that row. |
| 71 | 85 | the abstract's near-self sentence, carrying the P1 conditional S25's row replaces. Same reason. |
| 1272 | 64 | Figure 1's legend, the seam-codon description. Unrelated to this seat. |

Readability screen overall: 729 → 742 sentences, mean 23.7 → 23.8 words, max 87 unchanged, FKGL 12.9
unchanged.

---

## 5 · Gates (charter §6 — scoped to my change, never the whole tree while other seats mutate it)

```
python3 research/manuscripts/lint_claims.py <the paper>       0 ERROR, 8 WARN
python3 research/manuscripts/lint_style.py <the paper>        0 ERROR   ("clean")
python3 research/manuscripts/lint_consistency.py              0 ERROR across 26 target file(s)
python3 research/manuscripts/lint_readability.py --check      3 sentence(s) over 60 words  (was 4)
```

⛔ **The 8 `lint_claims` WARNs are not mine, and that was checked rather than assumed.** The same linter
run against `git show HEAD:…` piped to a scratch copy returns **`0 ERROR, 8 WARN`** as well — identical
count, identical rules (`R4-confirms` on pre-existing prose). My edit adds no claim warning.

```
python3 -m pytest research/manuscripts/tests/test_vaccine_path_numbers.py -q -p no:randomly   24 passed
python3 -m pytest test_pinned_figures_every_home.py test_readability_screen_cannot_be_satisfied_by_saying_less.py \
                  test_display_items_are_cited_in_order.py test_a_display_item_cell_is_not_clipped.py -q  308 passed
```

### ⚠ ONE RED THAT IS NOT MINE, WITH THE OBSERVATION THAT PROVES IT

```
research/manuscripts/tests/test_vaccine_path_aixiv_metadata.py::
  test_the_committed_metadata_reproduces_from_its_generator   FAILED
  -> emc-vaccine-path-aixiv-metadata.json is STALE — rerun without --check
```

⛔ **It was already stale at `HEAD`, before my first keystroke.** The discriminating observation, taken
rather than reasoned: I ran `build_aixiv_metadata.markdown_to_plain` over the `## Abstract` span of
(i) the live file and (ii) `git show HEAD:` of the same file, and diffed both against the committed
metadata.

```
live abstract == HEAD abstract:  True        # my edits do not touch the abstract
committed     == HEAD-derived:   False       # so the staleness predates them
```

The whole of the difference is **sentence-splitting punctuation** from one of the prose seats
(`…for the coverage scan, calling a peptide strong at…` → `…for the coverage scan; a peptide is called
strong at…`, and eight more of the same shape). **No claim, number or hedge differs.**

⛔ **I did not regenerate it, and that is charter §2 rather than laziness.** My prompt grants me that
path *"if your edit changes the abstract"*; it does not. The abstract change is another seat's landed
work and the regeneration belongs with it. **The fix is one deterministic command and no hand-edit:**

```
python3 research/manuscripts/build_aixiv_metadata.py --paper vaccine-path
```

---

## 6 · ⛔ What the driver MUST sequence with this edit — one hard requirement

**`research/modalities/vaccine-threshold-calibration.json` is not on `main`.** The manuscript now names
it in §8, and every number in the new §7 comes from it. CLAUDE.md §7 is explicit that a branch a
workflow runs from must never be the only home of an artifact, and this is that case:

- the **generator** `research/modalities/vaccine_threshold_calibration.py` **is** on `origin/main`
  (verified with `git ls-tree origin/main`);
- the **artifact** is only on `claude/s24-threshold-calibration` (blob at commit
  `43584e000f10d1386c6f01d47b1c961c39054685`), which is S24's proposed ledger row 2.

★ **Land the artifact in the same commit as this manuscript edit, or the paper cites a file the trunk
does not have.** Registering it in `emc-systems-map.json` and `run_manifest.EXPECTED` (S24's rows 3)
follows; both are paths I do not own.

⚠ Note for whoever merges: the run that wrote the fetched copy is **later** than the runs S24 §5
reports, and its arm D is **identical**. Its arm F is still `_fusion_fetch_is_complete: false` with a
**new** failure (PostgREST 400: offset without order), so **nothing about the calibration proper may be
quoted from it**, and §6.1 step 1 of the manuscript stays as written.

---

## 6b · ⛔ A CONCURRENT PROCESS REVERTED THIS SEAT'S EDITS ONCE, MID-SESSION

⚠ **Recorded because it is a measured concurrency defect and not a story about me.** All six edits
were applied and had passed every gate. Minutes later, with `HEAD` unmoved at `38f8627c5`:

```
$ git status --porcelain          # taken first
 M research/manuscripts/neoantigen/emc-vaccine-development-path.md
$ git diff --stat  <the paper>    # taken minutes later, no commit in between
                                  # (empty)
$ git log --oneline -1
38f8627c5  the vaccine screen's coverage figure sits below random chance, …
$ grep -c "decoy null" <the paper>
0
$ grep -n "no decoy control" <the paper>
1225:with no decoy control and no null expectation. …
```

The file was **restored to `HEAD` without a commit**, so the work was not committed and was not
merged — it was discarded. `HEAD` did not move, which ruled out a driver commit; the tree had 18 other
files dirty from concurrent seats at the same moment.

⭐ **THE CAUSE IS NOW NAMED, AND IT CAME FROM THE DRIVER RATHER THAN FROM MY INFERENCE.** The
coordinator reported, unprompted and before I could have asked: *"THE DRIVER RAN `git reset --hard
HEAD` IN THE SHARED TREE AT ~21:20Z. If you had uncommitted edits to a TRACKED file at that moment,
they were discarded. This is my error, not yours."* That matches the signature exactly and supersedes
the guess I had recorded here — which was that a seat had run one of the three git write commands
charter §1 forbids. ⛔ **My guess was wrong, and it accused the wrong party.** It is retained in this
sentence rather than deleted, because a seat that infers a cause and turns out to be wrong should
leave that on the record beside the measurement that corrected it.

★ **THE INDEPENDENT READING THE COORDINATOR ASKED FOR, TAKEN FROM DISK AFTER THE NOTICE.** The
coordinator noted it could not tell from `git status` whether the file's MODIFIED state meant "the
edits survived" or "this seat wrote again after the reset". **It is the second: the edits did NOT
survive the reset, and what is on disk now is a reapplication I made at ~21:22Z**, before the notice
arrived, having detected the loss myself in the `git diff --stat` above. Verified from disk rather
than from any buffer, all six edits present:

```
$ git diff --stat <the paper>                     41 insertions(+), 15 deletions(-)
$ git diff -U0 <the paper> | grep "^@@"           6 hunks: 510, 541, 675, 1224, 1316, 1548
$ grep -c "decoy null" <the paper>                5
$ grep -n "no decoy control" <the paper>          1574:  (Appendix C's withdrawal row, and nowhere else)
$ grep -c "six restricting alleles" <the paper>   1
$ grep -c "five restricting alleles" <the paper>  0
```

⚠ **AND THE REPRODUCTION WAS RE-RUN AGAINST THE POST-RESET TREE, NOT ASSUMED TO HAVE SURVIVED IT** —
a `reset --hard` reverts every tracked file, so the committed artifacts my §1 numbers were derived
from could in principle have moved under me. They did not, and this is the reading rather than the
assumption:

```
n peptides 174   by length [(8, 36), (9, 41), (10, 46), (11, 51)]
panel 34   n_peptides 174   rank presentation_percentile
presenting_alleles ['HLA-A*01:01','HLA-A*30:02','HLA-B*07:02','HLA-B*15:01']  -> 4
restricting alleles  [the same four, plus 'HLA-B*35:01','HLA-B*44:02']        -> 6
1740*34 = 59160   |  381/59160 = 0.644016%   |  CP 95% CI 0.58114% - 0.71180%
closed form 34*(1-(1-0.00644)^174) = 22.95
```

Every figure in §7 still derives from the tree as it stands.

★ **Every edit was reapplied from a single atomic script with an `assert count == 1` on each of the
six anchors, and re-verified twice — once on reapplication and again from disk after the
coordinator's notice.** The post-reapply readings are identical to the pre-reset ones (21,350 words,
18,257 main text, 205 caution markers, 3 over-ceiling sentences, `0 ERROR` on all four linters, and
318 tests passed on the final run), which is how I know the restoration is complete rather than
approximately complete.

⛔ **Three things follow.** First, **verify this file's six edits are present before staging** —
`grep -c "decoy null"` on the manuscript should return 5 and `grep -n "no decoy control"` should
return exactly one line, in Appendix C. Second, this is the same class CLAUDE.md §6 already records
from the other end (`git add -A` inside a mutation window): **a shared working tree loses work in
both directions, and the loss is silent both times** — `git add -A` commits what a seat is mid-way
through writing, `git reset --hard` discards what a seat has finished writing, and neither raises an
error. Third, ⭐ **the recovery worked only because charter §3 says the findings file is the
deliverable and must be written as you go.** It is untracked, so `reset --hard` did not touch it,
and every number needed to rebuild the manuscript edit was already in it. Had I written it at the
end, as a report of finished work, the reset would have destroyed the work and the record of it in
one move — which is the 107-agent fan-out's failure mode reached by a different route.

## 7 · Ledger rows the driver should write

I may not write these (charter §2). Proposed:

1. **Close S24's proposed row 5** — *"§7 says the screen has no decoy control and no null expectation.
   It now has both, and the screen sits BELOW the null."* `kind: hardening`, `state: done`,
   `cost_class: free`, `last_evidence_utc: 2026-09-01`. Evidence: this file and the six edits in §3.

2. **Close S24's proposed row 6** — the 0.644% decoy pass rate at a presentation percentile of 0.5
   (95% CI 0.581–0.712%). `state: done`. It landed inside the §7 replacement as an instrument reading
   rather than as a separate paragraph.

3. **Close S25's proposed row 3** — *"§B3 line 675 names five restricting alleles; there are six."*
   `state: done`. ⚠ **Amend its `what` to say the defect had TWO homes**: §B3's sentence and Appendix
   C's own last row, which carried the same five. Both are fixed.

4. ⛔ **Raise S24's proposed row 2 in priority — "Merge `claude/s24-threshold-calibration` so the
   calibration artifact reaches `main`."** `kind: hardening`, `state: queued`, `cost_class: free`.
   It is now a **manuscript dependency** rather than a convenience: see §6.

5. **New row — "The out-of-frame screen of §2.2 has no null."** `kind: experiment`, `state: queued`,
   `cost_class: free`, CI. Arm D is length-matched to the 174 in-frame peptides; §2.2's 97 out-of-frame
   peptides and their 10 strong calls across 8 alleles have no background of their own, and the
   in-frame pass rate must not be extrapolated to a differently-composed set. ⚠ The paper makes no
   claim that needs it today — §2.2's comparison is in-frame against out-of-frame — so this is an
   opportunity, not an open defect.

6. ⛔ **New row — "`git reset --hard` in a shared tree silently discards every seat's uncommitted
   work, and nothing warns."** `kind: hardening`, `state: queued`, `cost_class: free`. §6b has the
   signature, the driver's own account of the cause, and the independent post-reset reading. ⚠ The
   charter's §1 forbids seats the git write commands; **it says nothing about the driver running one
   mid-wave**, which is the gap this incident found. The same class as CLAUDE.md §6's `git add -A`
   incident, seen from the other side.

7. **New row — "Regenerate `emc-vaccine-path-aixiv-metadata.json`."** `kind: hardening`,
   `state: queued`, `cost_class: free`, local. Stale at `HEAD` from a prose seat's abstract
   repunctuation; proven in §5 not to be this seat's. One command, no hand-edit.

8. **Carry forward, unchanged: S24's row 7** (a composition-matched shuffle null, to separate *this
   junction* from *this composition*). §7 of the manuscript now states that gap in the paper's own
   words — *"does not separate this junction from the amino-acid composition of the peptides spanning
   it"* — so the row is now a named limitation in a published text rather than only a ledger item.

---

## What I could not do, and what it is actually waiting on

Nothing here is blocked.

1. **The calibration proper (§6.1 step 1)** is still WITHHELD and is S24's item, not mine. The latest
   run's arm F failed on a *third* distinct IEDB defect (PostgREST refusing `offset` without `order`),
   which is a one-line query fix in a file I do not own, and is worth recording as such rather than as
   "IEDB is unreachable" — it is reachable and it is answering.
2. **The three remaining over-ceiling sentences** are deliberately left (§4), because two of them are
   the exact text a queued row will rewrite and splitting them now would collide.
3. **Applying S25-P1-ANCHOR's measured P1 answer to the four homes of the conditioned null** is a
   different edit from this one, is S25's proposed row 2, and was not taken here.

## In flight

Nothing in flight. **Total real-dollar cost of this seat: $0** — no CI dispatch, no GPU, no paid API.
