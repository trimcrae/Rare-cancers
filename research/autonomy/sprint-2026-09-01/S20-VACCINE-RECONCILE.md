---
id: DOC-SPRINT-S20-VACCINE-RECONCILE
title: "S20-VACCINE-RECONCILE — the anchor/contact contradiction is real, it originates inside §B3, and the null it protects is conditional on position 1"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S20-VACCINE-RECONCILE — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S20-VACCINE-RECONCILE — the anchor/contact contradiction is real, it originates inside §B3, and the null it protects is conditional on position 1

**Item(s):** the reconciliation S13-VACCINE §4(c) flagged and refused to adjudicate (its proposed
ledger row 7); route `RT-VACCINE-COMBINATION`, publication `PUB-VACCINE-PATH`, strategy `ST-IMMUNO`

**Owned paths, named before either was edited (charter §2):**

1. `research/manuscripts/neoantigen/emc-vaccine-development-path.md` — the manuscript, §B3 and the
   three other homes of the same claim
2. `research/manuscripts/neoantigen/shared-vs-individualized-neoantigen-evidence.md` — the memo,
   falsifier 3 and the two other homes of the same claim
3. `research/manuscripts/neoantigen/emc-vaccine-path-aixiv-metadata.json` — **not in the original
   owned list**; taken only because it is a GENERATED artifact whose generator derives it from the
   manuscript abstract I edited, its guard went red on my edit, and CLAUDE.md §1(1) says a derived
   value is regenerated rather than left stale. Regenerated with its own generator; the diff is
   exactly and only the abstract sentence I changed, verified below.
4. `research/autonomy/sprint-2026-09-01/S20-VACCINE-RECONCILE.md` — this file

**Started (UTC):** 2026-09-01T19:26Z **Finished (UTC):** 2026-09-01T19:40Z **Real-dollar cost: $0.**

---

## Verdict

**FIXED — and the contradiction is REAL rather than two questions, with a measurable consequence.**
The two documents classify the *same* 13 near-self hits from the *same* committed artifact and
disagree about which bucket is the failing one, so under §B3's direction the failing bucket holds
**0 of 11 binders** and under the memo's direction it holds **4 of 11**. That is not two questions
wearing similar words; it is one question with two opposite answers.

**But the diagnosis S13 reported is one level too shallow, and the deeper one changes what needed
fixing.** §B3 states **both directions itself, one sentence apart** — the memo's falsifier 3 is a
faithful restatement of §B3's own inverted clause, written the day after it. The defect was never
"two documents disagree"; it was one manuscript sentence, quoted onward.

The direction is resolved **from repository evidence, not by preferring the newer document and not
by softening either statement**: §B3's own definitions, its own next sentence, and the producing
artifact's own instrumentation all say **anchor-only is the failing configuration**. The clause that
says otherwise is withdrawn in the manuscript's Appendix C, and the memo's falsifier is corrected to
match.

**What is NOT settled, and is not upgraded here:** whether position 1 is an anchor for the five
restricting alleles. S13 marked it UNKNOWN; it stays UNKNOWN, and I confirmed the repository holds
no allele-specific motif source. Both statements now carry the convention they depend on, and the
6-of-11 figure is carried in the manuscript at full strength rather than in a findings file.

---

## What I measured

### 1 · The two statements, verbatim and in their own context

⚠ Charter: *a contradiction reported second-hand is a hypothesis; two quoted sentences are a
measurement.* Both were read in full paragraphs, not grepped out.

**(A) `emc-vaccine-development-path.md` §B3, at HEAD, lines 647–655**, one sentence apart, both
inside the same paragraph:

> **Neither difference is at an anchor.** Position 1 and position 5 face outward or into the groove's
> middle rather than serving as the primary anchors at position 2 and the C-terminus, so a T cell
> raised against the neoepitope reads a surface that differs from the self peptide's at the positions
> it actually contacts — **which is the configuration in which cross-recognition is most plausible and
> in which central tolerance is most likely to have acted.**

> **And no binder in the screen has an anchor-only neighbour.** Zero of the 11 has a near-self peptide
> whose differences are confined to anchor positions, **which would have been the worst case: an
> identical TCR-facing surface distinguished only by residues the T cell cannot see.**

**(B) `shared-vs-individualized-neoantigen-evidence.md` §6.3 falsifier 3, at HEAD, lines 332–334:**

> 3. **The seam residues fall at T-cell-receptor contact positions rather than anchors**, such that
>    central tolerance to the near-self *NR4A3*-isoform neighbour has deleted the repertoire. This is a
>    computable Stage 0 item, not a blocked one.

**The finding S13 could not see from outside the manuscript: (B) is a restatement of the first half
of (A), not an independent position.** Dates, read with `git show -s`, are consistent with that and
with nothing else:

| statement | commit | date (UTC) |
|---|---|---|
| §B3's clause | `c6c7cd297` *"Vaccine paper: four CI results written in…"* | 2026-08-23 15:15 |
| falsifier 3 | `30f3c9aaf` *"Grade shared vs individualized neoantigen vaccines…"* | 2026-08-24 12:59 |

`git log -S` on each string returns exactly one commit, so neither has been touched since. The memo
was written a day later, cites the vaccine paper's §B1–B10 as its source for what bounds the route
(its §4, line 199), and reproduces §B3's clause in §B3's own direction. **The memo did nothing wrong that
the manuscript did not do first.**

### 2 · It is a real contradiction, and here is the observation that discriminates

The competing hypotheses were (i) two different questions wearing similar words — the charter's
stated most-likely outcome — and (ii) one question, two answers. The discriminating observation is
that **both statements are about the same 13 scored hits in the same committed artifact**, so the
"bad bucket" can be counted under each reading. Recomputed from
`research/modalities/junction-selfsimilarity.json` (read-only, no network, $0), classifying every hit
by whether its mismatch positions fall inside the anchor set {P2, C-terminus}:

```
mixed (anchor + contact)  8
contact-only              5
EXACT-SELF                1     (DMPCVQAQY vs itself — the §B5 withdrawal, not scored here)
anchor-only               0
```

- Under **§B3's direction** the failing configuration is `anchor-only`: **0 hits, 0 of 11 binders.**
- Under **falsifier 3's direction** the failing configuration is `contact-only`: **5 hits across 4 of
  the 11 binders** — NMPCVQAQY (twice), DMPCVQAQY, GDMPCVQAQY, LDMPCVQAQY.

Same artifact, same peptides, same convention, and the route is either clear of the failure mode or
has four of eleven binders sitting in it. **Two different questions cannot produce that.** It is one
question with opposite answers, so it had to be adjudicated rather than filed as a false alarm.

### 3 · Which direction is right, decided from the repository rather than asserted

Three independent lines in this repository point the same way, and none of them is "the newer
document wins":

1. **§B3's own definition of the filter**, thirty lines earlier at line 628 — *"whether the
   differences from self fall at anchor positions, **which affect binding**, or at positions
   contacting the T-cell receptor, **which affect recognition**"*. Central tolerance deletes T cells
   by *recognition*. A difference at the positions a receptor reads is therefore a difference the
   receptor can use; a difference at the positions it cannot read is not. The ordering follows from
   the manuscript's own definitions.
2. **§B3's own next sentence**, quoted above, which spells the mechanism out: *"an identical
   TCR-facing surface distinguished only by residues the T cell cannot see."* That is a mechanism;
   the clause it contradicts is an assertion with no mechanism attached.
3. **The producing artifact's own instrumentation.** `junction-selfsimilarity.json` computes a
   per-hit field `all_mismatches_at_anchors` and a headline field
   `n_anchor_only_near_self_total`. The search was *built* to count the anchor-only configuration,
   which is what a search built around a failing case looks like. Nothing in it counts the
   contact-only configuration; I had to compute that number myself for §2 above.

**The asymmetry that makes this more than a vote**, stated because it is the reason the two are not
symmetric claims: an anchor-only difference is *sufficient* for the surfaces to be indistinguishable
to a receptor, given presentation. A contact-position difference is at most a *risk factor* — it
leaves at least one residue the receptor can read, and whether that is enough is a question about
receptor degeneracy, which §B3 itself says is not answerable from sequence (*"sequence distance is
not receptor distance"*). So falsifier 3's *"such that … has deleted the repertoire"* does not follow
from its own premise, and its cost grade — *"a computable Stage 0 item"* — is wrong for the same
reason.

⛔ **What I did NOT do: soften both until they agree.** Falsifier 3 is not hedged into vagueness; it
is turned around to name the configuration that actually is the worst case, and its false "computable"
grade is replaced with what is computable and what is not.

### 4 · Independent reproduction of S13's position-1 result, before carrying it into a paper

Refute-by-default (charter §4). I did not take S13's numbers on trust; I recomputed them from the
committed artifact with my own script, recomputing every mismatch position **from the two peptide
strings** and asserting agreement with the artifact's recorded `mismatch_positions` on all 14 records
(0 disagreements). Anchor set = {P2, C-terminus} plus the named extras:

```
P2+Cterm         hits=0 binders=0
P2,P3,Cterm      hits=0 binders=0        <- the caveat the artifact raises against itself does not bite
P1,P2,Cterm      hits=6 binders=6
P1,P2,P3,Cterm   hits=6 binders=6
```

```
NMPCVQAQY    DMPCVQAQY    Q92570-3  mm=(1,)    HLA-B*15:01   <- the LEAD peptide, strong binder
GDMPCVQAQY   VDMPCVQAQY   Q92570-3  mm=(1,)    HLA-B*44:02
LDMPCVQAQY   VDMPCVQAQY   Q92570-3  mm=(1,)    HLA-A*01:01
RGDMPCVQAQY  NVDMPCVQAQY  Q92570-3  mm=(1,2)   HLA-A*01:01   <- strong binder
DLDMPCVQAQY  NVDMPCVQAQY  Q92570-3  mm=(1,2)   HLA-A*01:01
FDDMPCVQAQY  NVDMPCVQAQY  Q92570-3  mm=(1,2)   HLA-A*01:01
```

**S13's 6-of-11 reproduces exactly**, as does the single accession (Q92570-3) and every allele call.

**Two refinements S13 did not make, both of which I carried into the manuscript rather than only
here.** ⛔ They sharpen the finding; neither weakens it, and both numbers are reported.

- **Three of the six differ at position 1 alone** — NMPCVQAQY, GDMPCVQAQY, LDMPCVQAQY — and one of
  the three is the lead peptide. For these three every other position, including both primary
  anchors, is identical to the self neighbour, so the self neighbour's own presentation is not in
  doubt and they are the clean worst case *if* P1 is an anchor.
- **The other three differ at positions 1 and 2**, and P2 is a primary anchor under every convention.
  They are anchor-only only under a P1-inclusive convention, and their P2 difference is exactly the
  thing that would put the *self* peptide's presentation in doubt.
- **That second point exposes an unstated premise in §B3's ranking itself**, which I named in the
  manuscript rather than assumed: "anchor-only is the worst case" holds where the near-self peptide
  is *itself presented on the same allele*, and an anchor difference is precisely what would put that
  in doubt. Presentation of these self peptides is measured nowhere in this work. This is stated as a
  premise, not resolved — resolving it needs presentation data this programme does not have.

### 5 · The UNKNOWN, checked rather than inherited

S13 recorded the P1-anchor question as UNKNOWN in-repo. I checked rather than repeating it:

```
python3 -c "import mhcflurry"   -> ModuleNotFoundError
python3 -c "import mhcnuggets"  -> ModuleNotFoundError
ls research/modalities/ | grep -i "motif|anchor"
  emc-prmt5-substrate-motif-map.json      (a PRMT5 substrate motif — unrelated)
  junction-anchor-convention-sensitivity.json / .py   (S13's, which computes over conventions and
                                                       sources none of them)
  map_edit_anchors.py, transfer-anchor-diagnostic.json  (unrelated senses of "anchor")
```

**No allele-specific class I binding motif for HLA-A\*01:01, B\*07:02, B\*15:01, B\*35:01 or B\*44:02
exists anywhere in this repository.** The UNKNOWN stands and is not upgraded. Settling it costs one
networked fetch of an allele motif dataset, therefore a CI dispatch, therefore $0 — but a seat cannot
dispatch one.

### 6 · Gates (charter §6 — scoped, not the whole thing)

```
python3 research/manuscripts/lint_claims.py
  lint_claims: 0 ERROR, 170 WARN across 129 file(s)
```
All 7 WARNs on my two files are `R4-confirms` at lines 173, 293, 550, 553, 1050, 1099 and 1123 of the
manuscript, and **every one is outside every hunk I touched** (`git diff --unified=0` gives my hunks
as 94, 507, 647–680, 1524). The memo carries none. **I introduced no new WARN.**

```
python3 research/manuscripts/lint_consistency.py
  lint_consistency: 0 ERROR across 26 target file(s)
```

```
python3 -m pytest research/manuscripts/tests/test_vaccine_path_numbers.py \
                  research/manuscripts/tests/test_vaccine_path_aixiv_metadata.py -q -p no:randomly
  33 passed in 0.20s
```
⚠ **This suite went red first, and the red was correct.**
`test_the_committed_metadata_reproduces_from_its_generator` failed with *"…aixiv-metadata.json is
STALE"* because my abstract edit changed a value that file derives. `git status` showed the JSON
clean beforehand, so the staleness was mine and not pre-existing. Regenerated with its own generator;
`git diff` on it is exactly and only the abstract sentence I changed, no other field moved.

```
python3 research/manuscripts/emc_systems_map_check.py
  155 registry items · 0 ERROR · 0 WARN
```

`preflight.sh` is the driver's, on a settled tree.

### 7 · A file moving under me that is not mine

`git diff --stat` shows `research/manuscripts/neoantigen/hla-coverage-emc.md` with 26 changed lines
that **I did not make** — another seat is editing it concurrently. I did not touch it and did not
stage anything (no git write command was run at any point). Flagged so the driver stages by path.

---

## What I changed

### `research/manuscripts/neoantigen/emc-vaccine-development-path.md` — 4 edits + 2 appendix rows

1. **§B3, the inverted clause (was line 651).** *"— which is the configuration in which
   cross-recognition is most plausible and in which central tolerance is most likely to have acted"*
   → *"— which is the **less** adverse of the two configurations, and that ordering is what the
   filter is for: a difference the receptor can read leaves open that a repertoire exists, while a
   difference it cannot read does not"*, plus a pointer to the Appendix C withdrawal. The two
   headline sentences now also name the convention (*"under the convention applied here"*, *"under
   that convention"*), so the zero is no longer stated as a property of the peptides.
2. **§B3, the caveats paragraph.** *"Two caveats"* → *"Three caveats … and the first of them is
   load-bearing"*, **replacing** the old anchor-convention sentence rather than appending to it. It
   now states: adding P3 leaves the count at zero (the genuine strengthening); counting P1 makes it
   six of 13 hits across six of 11 binders, all against Q92570-3; the three-differ-at-P1-alone /
   three-differ-at-P1-and-P2 split with the lead peptide named; that P1's anchor status for the five
   alleles is not established here; and, as the third caveat, the presentation premise the ordering
   rests on.
3. **Abstract (line 94).** The null now reads *"…differing only at anchors under that convention,
   though six of the 11 would if position 1 counted as an anchor, which no allele-specific motif held
   here can settle."*
4. **§3 limits table, row B3.** *"0 of 11 binders has an anchor-only near-self neighbour"* → *"…under
   that convention, 6 of 11 if position 1 counts, which is not established here"*.
5. **Appendix C, two new rows** — the manuscript's own convention for a statement that stood and no
   longer stands (*"a correction that leaves no trace is indistinguishable from a claim that was
   never made"*): one for the inverted clause, one for the unconditional form of the null.

⚠ **Edits 3 and 4 are outside §B3 and were deliberate.** The abstract and the limits table are the
second and third homes of the same null. Appendix C of this very manuscript already records this
exact failure — *"It is the one-of-a-pair defect: correcting B8 alone would have left the claim
standing where a reader meets it first"* — so fixing §B3 alone would have reproduced a defect the
paper has already paid for once.

### `research/manuscripts/neoantigen/shared-vs-individualized-neoantigen-evidence.md` — 3 edits

1. **§6.3 falsifier 3** — turned around to name the anchor-only configuration, with the mechanism
   attached; a dated ⚠ correction note saying what it used to say, why that was inverted, and where
   it came from; the near-self search recorded as **run** with its `[REPO]` grade and a link; and the
   false *"computable Stage 0 item"* grade replaced with what is computable (done) and what is not
   (needs a motif source that has to be fetched).
2. **§5.3, the open-questions bullet** *"Whether the novel seam residues fall at anchor positions or
   at T-cell-receptor contact positions"* — stale since 2026-08-23, because that search has been run.
   Replaced with the question that is actually still open: whether the convention applies to the five
   restricting alleles, and that P1 flips six of the 11.
3. **§4, the self-adjacency bullet (line 209)** — now says *"under the general class I convention of
   position 2 and the C-terminus"*. Fourth home of the same claim, same reason as above.

### `research/manuscripts/neoantigen/emc-vaccine-path-aixiv-metadata.json` — regenerated

Not hand-edited. `python3 research/manuscripts/build_aixiv_metadata.py --paper vaccine-path`. Its
guard now passes.

---

## What I could not do, and what it is actually waiting on

1. **Whether position 1 is an anchor for HLA-A\*01:01, B\*07:02, B\*15:01, B\*35:01 and B\*44:02.**
   Waiting on an allele-specific class I binding-motif dataset — a networked fetch, therefore a CI
   dispatch, therefore $0 and not a rental and not trimcrae. A seat may not dispatch a workflow.
   **This is the single blocking question for everything downstream of S13's artifact.** Confirmed by
   direct check (§5), not inherited from S13.
2. **Whether the near-self neighbours are themselves presented on the same allele** — the premise
   under §B3's ranking. Not resolvable by any computation in this repository: it is the same
   presentation question B2 is bounded by, and B2 needs tissue and a proteomics facility. It is now
   *stated* in §B3 rather than assumed, which is the whole of what can be done here.
3. **`research/modalities/junction-anchor-convention-sensitivity.json` is not cited by either
   manuscript.** Deliberate — see the driver's answer below. The manuscript now carries the *numbers*
   that artifact establishes, derived independently by me from the committed
   `junction-selfsimilarity.json`, so nothing in the paper depends on an uncited artifact. Citing it
   is a separate step for whoever adds it to §8's artifact list, a path I do not own.
4. **The posted aiXiv version of this paper (`aixiv.260822.000005`, latest reviews on disk are v1.7)
   now differs from the repository on a claim.** Not mine, not urgent, and not gated on trimcrae —
   CLAUDE.md §3 says the aiXiv grant is standing and `PUB-VACCINE-PATH` is not the excluded paper —
   but it is gated on every clause in `publish_bar.py::CLAUSES` and on `PREFLIGHT_FULL=1`. Raised for
   the driver, not taken.

---

## THE DRIVER'S ANSWER: can anything from S13's artifact go into a paper now?

**Yes — but only the two statements below, and only in the conditional form they now have in §B3.
The third statement S13 listed still cannot go in.**

**✅ CLEARED, and now written into the manuscript.** *"Adding position 3 — the position the producing
artifact flags for HLA-A\*01:01 — to every peptide leaves the anchor-only count at zero."* This
closes a caveat the paper had raised against itself, it does not depend on the reconciliation, and I
reproduced it independently. It is a genuine strengthening and it is narrow: still a sequence-distance
result under a convention, not a measurement.

**✅ CLEARED, and now written in at full strength — this is the load-bearing one and it points against
the route.** *"Counting position 1 as an anchor makes six of the 11 binders carry an anchor-only
near-self neighbour, all six against the same NR4A3 isoform, and whether position 1 is an anchor for
these five alleles is not established here."* S13 was right to hold this back: **in the direction
falsifier 3 stated, this finding would have read as reassurance** — "the seam residues are at
anchors, not contact positions, so the falsifier does not fire" — which is the exact opposite of what
it means. The reconciliation is what makes it safe to write, and the direction is now fixed at all
four of its homes.

**⛔ STILL BLOCKED, and it is not this contradiction.** *"The class II peptides, including the one
strong call, are absent from the reviewed human proteome."* That is S13's third result, from
`class2-novelty-inheritance.json`, and this seat did not examine it. It is a different artifact on a
different question and needs its own check before it goes into a paper.

**The blocking question, stated exactly.** For the anchor result the blocker was never the
contradiction — that is now resolved from repository evidence, at zero cost, and the manuscript says
so. The one question that remains open is:

> **Is position 1 a primary or secondary anchor for HLA-A\*01:01, HLA-B\*07:02, HLA-B\*15:01,
> HLA-B\*35:01 and HLA-B\*44:02?**

It costs **one networked fetch of an allele-specific binding-motif dataset — $0, one CI dispatch, no
rental, no human**. It cannot be answered in this sandbox: no motif source is present and neither
predictor imports here. Until it is answered, every statement in the paper about the anchor-only null
is conditional, and the paper now says that in the abstract, in the §3 limits table, and twice in §B3.

⛔ **And a boundary that does not move whichever way that question resolves.** None of this is a
presentation, immunogenicity or safety result. Sequence distance is not receptor distance. An
anchor-only near-self neighbour is a hypothesis about why a repertoire might have been deleted, never
a measurement that it was, and a binding prediction is a binding prediction.

---

## Ledger rows the driver should write

I may not write these (charter §2). Proposed:

1. **Close S13's proposed row 7** — *"Reconcile the anchor/contact falsifier"* — before it is opened,
   or open and immediately close it. `kind: hardening`, `state: done`, `cost_class: free`,
   `last_evidence_utc: 2026-09-01`, evidence `research/autonomy/sprint-2026-09-01/S20-VACCINE-RECONCILE.md`.
   Resolved from repository evidence; both documents corrected; the manuscript's Appendix C carries
   the withdrawal.
2. **Raise the priority of S13's proposed row 3** — *"Resolve the anchor convention for the five
   restricting alleles from an allele-specific motif source"*, `kind: experiment`, `state: queued`,
   `cost_class: free`, CI. It is now the **only** thing standing between the position-1 result and a
   settled statement, and four separate places in a live manuscript are conditional on it. Evidence:
   `research/modalities/junction-anchor-convention-sensitivity.json` and §4 above.
3. **New row — "Cite `junction-anchor-convention-sensitivity.json` in the vaccine paper's §8 artifact
   list."** `kind: hardening`, `state: queued`, `cost_class: free`, local. §B3 now carries figures
   this artifact establishes; the artifact itself is not yet in the paper's deposit list. A path this
   seat did not own.
4. **New row — "The posted aiXiv version of `PUB-VACCINE-PATH` predates the §B3 correction."**
   `kind: hardening`, `state: queued`, `cost_class: free`. Not gated on trimcrae (CLAUDE.md §3, and
   this is not `PUB-ASO`), gated on `publish_bar.py::CLAUSES` and `PREFLIGHT_FULL=1`. A driver call,
   not a seat's.
5. ⚠ **Note against S13's proposed row 3, for whoever writes it:** its framing *"whether P1 is an
   anchor"* is necessary but not sufficient. §B3 now also names a second premise — that the near-self
   peptide is itself presented on the same allele — which no motif dataset answers and which is the
   same presentation question `B2` is bounded by. The row should not be closed by a motif fetch alone
   as though it settled the whole ranking.
