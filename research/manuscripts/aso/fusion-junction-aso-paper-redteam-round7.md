---
id: DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND7
title: "Round-7 swarm review of the fusion-junction ASO submission — the verification results, the one charge that survived them, and the four that did not"
level: L3
kind: manuscript
status: live
canonical_for:
  - the round-7 swarm review of the fusion-junction ASO submission manuscript
  - the round-7 wrong-leads record
purpose: >
  Hold the seventh adversarial review of fusion-junction-aso-research-article.md — the first review of
  the manuscript as restructured and shortened by the 2026-08-16 editorial pass. Its reason for
  existing is the one rounds 5 and 6 state: a review whose findings are recorded nowhere gets re-run
  from scratch and its wrong leads get re-raised. ⭐ Its most important content is the verification
  layer, not the finding list: five findings were filed at blocker grade, four did not stand at the
  grade they were filed, and two of the five were never verified at all.
scope: >
  Claims, arithmetic, nulls, citation semantics, deliverable executability, narrative and deposit
  apparatus of the three submission documents at commit 100816ab3, against the artefacts under
  research/modalities/. Nineteen reviewers, no cross-talk, refute-by-default verification on the
  blocker-grade charges only. ⛔ NOTHING HERE IS APPLIED. No manuscript file was edited for this
  round; the ledger is the deliverable and application is a separate pass. "The wet-lab experiment
  was not done", "delivery is unsolved", "no cell line was tested" and "not validated in patients"
  are never findings here.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-16
last_verified: unverified
---
# Round-7 swarm review of the fusion-junction ASO submission

> **Rounds 1–6** are [round 1](./fusion-junction-aso-paper-redteam.md),
> [round 2](./fusion-junction-aso-paper-redteam-round2.md),
> [round 3](./fusion-junction-aso-paper-redteam-round3.md),
> [round 4](./fusion-junction-aso-paper-redteam-round4.md),
> [round 5](./fusion-junction-aso-paper-redteam-round5.md) and
> [round 6](./fusion-junction-aso-paper-redteam-round6.md). ⚠ **Section numbering has now drifted five
> times.** Every finding below is anchored on a verbatim quote and a line number at commit
> `100816ab3`, never on a § number.
>
> **Reviewed:** `fusion-junction-aso-research-article.md`, `-submission-tables.md` (GENERATED) and
> `-supplementary-information.md`, as left by the 2026-08-16 editorial restructure.
> **Method:** nineteen reviewers in four families — five diff-armed regression hunters (A), seven
> firewalled fresh referees who saw the paper and nothing else (B), five wet-lab lenses (C), four
> integrity and narrative lenses (D). Refute-by-default verification, three refuters per charge,
> survives on ≥2 of 3 non-refutations.
> **Yield:** **134 findings — 5 blocker, 70 major, 59 minor.** One reviewer (A1) returned zero
> findings, which is itself the round's cleanest result: 16 of 16 protected items present.
> ⚠ **That split is counted from the per-finding `severity:` fields, not from the reviewers' own
> summary lines** — B1's header says "5 major, 6 minor" against its own six major fields, and D4's says
> "5 major · 3 minor" against its own six. Two hand-typed totals drifting from their parts, in a round
> whose brief specified the field that carries the truth. Neither changes a finding.

---

## 1 · ⭐ THE VERIFICATION RESULTS — the part of this round that matters

**Five findings were filed at blocker grade**, and one further charge — filed `major` but
blocker-shaped, because it accused the abstract of stating a false total — was escalated into the same
layer. **Four did not survive at the grade they were filed: three were refuted on the artefacts, and
the one that survived verification was downgraded. Two of the five were never verified at all.**

| # | charge | filed | verdict | outcome |
|---|---|---|---|---|
| **B5-F1** | the chimera null does not hold exon-terminal context fixed | blocker | **SURVIVES — 3 refuters of 3** | ⬇ **downgraded to major** |
| **D1-F1** | the three condemned sequences are in no table, and Table 7 prints a 15/16 neighbour of one | blocker | **REFUTED** | dropped |
| **D1-F2** | the *TAF15*-response sentence drops a caveat the repository's artefacts require | blocker | **REFUTED** | residual minor |
| **B2-F1** | the abstract's "another 19" implies a false total | major | **REFUTED** | minor clarity, re-aimed |
| **C3-F1** | the pre-registered selectivity estimator is undefined between two readings | blocker | **REFUTED — 3 refuters of 3** (2026-08-16) | dropped; residual P2 (§6.5) |
| **C3-F2** | the limit-of-quantification guard emits a failed assay as a selectivity success | blocker | **REFUTED — 3 refuters of 3** (2026-08-16) | dropped; it would reinstate a round-6 fix (§6.6) |

⭐ **UPDATE, 2026-08-16 — the two unverified blockers were verified and both fell.** §1.3 below is
retained as written because it is the record of the state this round shipped in; what it asks for has
since been done. **Six refuters, three per charge, distinct lenses, refute-by-default: 6 of 6 returned
REFUTED.** So the round's final verification tally is **1 of 6 blocker-grade charges surviving, and
that one downgraded** — and the measured base rate for confident, quantitative, well-evidenced charges
at blocker grade in this project moves from roughly one in two to **five of six failing**. **P0.10 is
closed and does not reach the deposit.**

### 1.1 · B5-F1 — SURVIVES, and it is the round's most important finding

**The charge.** `research/modalities/aso_parent_null.py::draw_parent_chimera` draws the donor half as
a *uniform interior window* of the donor transcript (`p = rng.below(len(ds) - offset + 1)`, line 251).
It therefore destroys exon-terminal context along with the breakpoint, so the excess of the observed
rate over the chimera null is not isolating "where the disease joins the two genes" — it is a property
of 5′ splice-donor consensus that every exon–exon junction in the genome shares.

**All three refuters re-derived it independently, and this ledger re-derived it a fourth time before
recording it:**

- `grep -i 'exon|splice|boundary' aso_parent_null.py` returns **one** hit, at line 27, in a docstring
  saying the parents are spliced. The module has no concept of an exon terminus.
- Donor exons of the 38 in-frame junctions end **G at 36 of 38, AG at 18, CAG at 5** — computed here
  from `aso-premrna-sequences.json` exon spans, and `NR4A3` mature\[689:697\] is `CCCTCCAG`, so
  *NR4A3* exon 2 ends `…CAG`.
- `aso-parent-gap-pairing.json` puts the wild-type-*NR4A3* liabilities at `parent_start_0based`
  **{691: 36, 690: 18, 689: 5, 3412: 1, 3413: 1}** — re-derived here, exact. **36 / 18 / 5 match the
  terminal-base counts junction-for-junction.**
- One refuter rebuilt the whole class from sequence alone: **59 of 59 true positives, 131 of 131 true
  negatives**, with no screen involved.

**Magnitude.** A donor-terminus-preserving null puts the seam arm at **≈30.8%** against the uniform
draw's **6.7%**. The observed seam arm is ~31%. So the residual on that arm is about **0.3 points**,
not half, and the "about half generic, about half specific to the real junctions" split does not
survive as a decomposition.

**⭐ IT DOES NOT OVERTURN THE RESULT, AND THAT MUST BE SAID PLAINLY.** 87 of 190 stands. 61 against
wild-type *NR4A3* stands. The title is untouched. The designs still pair the parent, and a laboratory
ordering from Table 7 faces exactly the liability the paper describes. What the finding supplies is a
**mechanism**, and what it invalidates is a **label**. Four sentences become false — article lines
~437–438, 439–441, 711 and 713–715 — and the correct replacement names the cause rather than the
disease.

**⭐ It arguably strengthens the paper.** An exon-boundary cause predicts the same liability at
breakpoints nobody has reported yet, which generalises the negative from 38 tiled junctions to any
in-frame exon pair — and that is precisely the claim §4.5's released procedure needs in order to mean
something for a patient whose breakpoint is outside the panel.

**⚠ AND IT IS CLASS B.** The anchor sentences are text no prior round touched and the editorial pass
did not rewrite. **This falsifies the round-7 pre-registration's central prediction that class B would
be ≈0.** The pre-registration committed to a consequence in advance — *"If round 7 comes back with a
pile of class-B blockers in text the editorial pass did not touch, then the excuse above is wrong"* —
and this is not a pile, but it is not zero either, and it is the round's highest-severity finding. The
honest reading is the one the pre-registration named: **six prior rounds had a real coverage gap on
the null models' construction, and the restructure is not what created it.**

**⚠ Two reviewers reached the same conclusion by opposite routes, and they disagree on the sign.**
B2-F3 randomised one half at a time on the identical instrument, 200 draws per design, three seeds,
and found the chimera arm sits *above* both arms that retain more real structure (real donor half
0.172; real *NR4A3* half 0.165; chimera 0.239) — a null whose rate rises when real structure is
removed is not ordered by "how much of the design is real", so subtracting it partitions nothing.
B2 reads the specific share as **larger** than stated (62–64%); B5 reads the seam arm's residual as
**≈0**. They agree the apportionment sentence is unsupportable. They do not agree which way it moves.
**Any fix must not silently pick a side**; the smallest honest edit deletes the apportionment and
reports the chimera as the strictest null, which §2.5 already calls it.

### 1.1a · ⭐ B5-F1, MEASURED — the corrected null, and what it does to the apportionment

**Run 2026-08-16, $0, 4.4 s of CPU, offline.** The ledger above argued the mechanism; this is the
measurement, and it was taken before any sentence was rewritten so the result could not be chosen to
fit the prose. Three arms were added to `research/modalities/aso_parent_null.py`; the seven existing
arms are **bit-identical** (each ensemble seeds its own stream from its name), which is asserted rather
than asked for on trust.

| arm | what it holds fixed | rate liable | 95% CI | against wild-type *NR4A3* |
|---|---|---|---|---|
| **OBSERVED** (87/190) | the real reported breakpoints | **0.4579** | [0.3886, 0.5289] | 0.3211 |
| `random_parent_chimera` (published) | donor + acceptor at **uniform interior** windows | 0.2376 | [0.2333, 0.2419] | 0.0933 |
| `donor_terminus_chimera` | donor half ends at a **real exon 3′ terminus** | 0.2253 | [0.2212, 0.2296] | 0.0849 |
| `exon_terminus_chimera` | **both** halves at real exon termini | **0.4057** | [0.4008, 0.4106] | 0.2876 |
| `exon_terminus_chimera_novel_acceptor` | both termini, and **never** *NR4A3* exon 3 | **0.4051** | [0.4002, 0.4101] | 0.2832 |

**⭐ THE APPORTIONMENT IS DELETED, NOT RE-STATED.** A null that joins two real exon termini of the same
two transcripts at a junction **no patient is reported to carry** reproduces **0.405 of the observed
0.458** — about 88% of it — and the observed rate's own 95% interval **contains** the null's. The
residual is not resolved at this panel's n. So "roughly half is inherent in joining these two
transcripts, roughly half is specific to where the disease joins them" is false in both directions it
could be read: the specific share is neither a half nor demonstrably non-zero.

**⭐ AND THE MECHANISM IS NARROWER THAN THE CHARGE SAID — it is the ACCEPTOR terminus, not the donor.**
B5-F1 named 5′ splice-**donor** consensus. The donor-terminus arm moves the rate **not at all** (0.2253
against the uniform draw's 0.2376 — if anything slightly down). Everything happens when the *NR4A3*
half is required to begin at a real exon 5′ terminus: 0.2253 → 0.4057. That is a **more specific and
more useful** statement than the one filed, and it points where the paper's own argument does: the
liability tracks the acceptor boundary of **wild-type *NR4A3*, the transcript the modality exists to
spare.**

**⚠ The sensitivity that had to be taken before any of this could be said.** Every one of the 38
reported junctions uses the *NR4A3* exon-3 acceptor, and that acceptor is one of the seven internal
*NR4A3* exon starts the arm draws from — so ~1 in 7 draws could have been landing on the disease's own
acceptor and inflating the null toward the observed. Excluding it entirely changes the rate by **0.0006**
(0.4057 → 0.4051). The result does not rest on it.

**⚠ B5 and B2 disagreed on the sign and this does not adjudicate their arm.** B2 randomised one half at
a time; the arms above randomise *position* while holding both genes, both termini and the split. The
two measure different things and the ledger's instruction not to silently pick a side is honoured by
reporting the corrected null as the strictest comparator rather than by re-deriving a split.

**⛔ A SEPARATE DEFECT FOUND WHILE BUILDING THIS, AND IT IS NOT IN ANY ROUND'S FINDING LIST.**
`junction_offset_in_oligo` is an offset in the **antisense oligo**, where the *NR4A3* half comes first —
it equals `bases_from_NR4A3` for all 190 records and differs from the donor base count for **152 of
them**. `draw_parent_chimera` is called with it and takes that many bases **from the donor**, so every
published chimera draw is its design's **mirror** split. ⭐ **Its totals are unaffected and that is
measurable, not arguable:** each junction tiles offsets 6–10, symmetric about 8, so the multiset of
donor lengths drawn per junction is identical either way — verified for all 38 junctions. The published
23.8% therefore stands. The three new arms take the split they mean, because a per-design terminus draw
is **not** symmetric and the mirror would pair the wrong window length.

### 1.2 · The three refutations, with the observation that decided each

**D1-F1 — REFUTED on four independent legs.** The "15 of 16" is a **one-base register shift within a
1-nt tiling**, which is what a tiling is; column-wise the two sequences share 4 of 16. Table 7 prints
the design the artefact *passes* — `⛔_cleaves_wild_type_NR4A3: false`, and it is the top-margin design
at that seam. The warning naming all three condemned sequences sits in the same paragraph a reader
reaches the seam through. And the proposed fix — printing the condemned sequences as table rows — would
put three RNase-H1-competent-on-wild-type oligonucleotides onto an order form, which is the opposite of
the safety gain claimed for it. ⚠ **The underlying observation is real and the inference from it is
not.** Do not re-raise it in the form "the forbidden set should travel in the same object as the
ordered set".

**D1-F2 — REFUTED, residual minor.** Protected item 12's Wilson clause is in the same sentence as the
claim, not elsewhere. The pooling artefact's instruction that *"any paper on this lane must carry the
hedge in its own abstract"* targets a different manuscript — the fusion-partner paper — and this
paper's abstract makes **no partner-response claim at all**, so there is nothing there for the hedge to
bound. What survives is a minor: the surrogate-versus-mechanism reading is a fair sentence to add to
the Introduction, and it is P2, not a blocker.

**B2-F1 — REFUTED to minor clarity.** The set arithmetic is right — 13 of the 19 pre-mRNA designs are
already among the 87, so the union is 93 of 190 and not 106 — but **no total is stated anywhere in the
article, the SI or the tables**, so there is no false total to correct. ⭐ **The refuter found a sharper
defect and it is worth more than the charge it replaced:** in *"another 19 pair **it** in precursor
RNA"*, the nearest antecedent of *it* makes the sentence assert 19 designs against wild-type *NR4A3*
in pre-mRNA where the artefacts give **9**. That is the item to fix, and it is a different sentence
problem from the one filed.

### 1.3 · ⚠ C3's two blockers are UNVERIFIED, and are recorded as OPEN rather than as confirmed

No refuter was run on **C3-F1** (the pre-registered estimator is undefined between a relative and an
absolute reading of "half-maximal knockdown concentration", and both readings break on the paper's own
reagents) or on **C3-F2** (the limit-of-quantification guard gates the change and disclaims the
abundance, so a failed assay, an undetectable transcript and a perfectly spared transcript all emit the
same unfalsifiable one-sided bound). Both are internally worked, both cite artefact fields, and C3
argues explicitly against the recorded round-6 disposition rather than re-raising it. **None of that is
verification.** They stand at blocker grade because nobody has tried to knock them down, which is a
statement about this round's coverage and not about their truth. ⛔ **Do not report them as confirmed
findings, and do not apply them without running the three refuters first** — this paper's history is
that confident, quantitative, well-evidenced charges at this grade fail at roughly one in two.

### 1.4 · ⭐ The fourth near-miss, and it is evidence about the method rather than about the paper

**D2 nearly filed a confident quantitative finding that a gap-length characterisation was inverted,
and the cached full text refuted it outright.** The manuscript says a series shortening a 5-10-5 gapmer
to 5-6-5 reported *lower off-target knockdown but also lower on-target activity and lower allele
selectivity*. D2 read that as inverted; the cached full text `PMC11312655` settles all three clauses in
the manuscript's favour, verbatim. **D2 recorded the near-miss itself, unprompted**, which is the
behaviour the evidence standard is meant to produce.

**That is the fourth instance of this shape in the paper's review history** — after the three findings
rounds 5 and 6 measured as confident, quantitative and wrong on the data. The pattern is stable and it
is the reason refute-by-default is in the method: **the failure mode is not sloppiness, it is
confidence.** Every one of the four was precisely argued and wrong on data already on disk.

⭐ **What makes this one different is that no verification layer caught it — the reviewer caught
itself, before filing.** That is the evidence standard working one layer earlier than designed, and it
is worth more than a refutation, because a finding never filed costs nothing to refute.

### 1.5 · The four numbers the pre-registration asked for

| number | reading | what it means |
|---|---|---|
| `restores_cut: true` survivors — **the yo-yo, measured** | **2, arguably 3**, and every one self-flagged by the reviewer that filed it (A2-F5, A3-F7; A2-F1 arguable) | **The review loop and the editorial loop are complementary, not fighting.** Six reviewers certified in writing that none of their fixes restores deleted duplication; A3's six deletion findings each concern text that had exactly **one** home, which is a loss and not a redundancy. |
| class A split — severed caveats vs destroyed results | ~3 severed caveats (A2-F1, A2-F5, A2-F7), ~2 material losses (A3-F1, A3-F2), 4 minor losses, **2 defects newly created by the pass** (A2-F2, A5-F1) | Predicted: ≤3 class-A blockers, each a severed caveat. **Actual: zero class-A blockers.** The system worked; the shortening pass did what a shortening pass does wrong, at minor grade, and `manuscript_inventory.py` is why it was findable. |
| class B count | **≥3 — B5-F1 (the round's top finding), A2-F3, A2-F6**, plus the substantive half of A2-F7 | Predicted ≈0. **FALSIFIED.** See §1.1. |
| verification survival, vs 3-in-80 across rounds 5–6 | **1 of 4 verified charges survived, and that one was downgraded** | The base rate is measured over *all* findings; only the top of the severity scale was verified, and that is exactly where confident-and-wrong lives. **No evidence the swarm is manufacturing noise at volume** — evidence that blocker-grade charges need the verification layer every time. |

**Also predicted and met:** all sixteen protected items survive (A1, 16/16, one checked byte-for-byte
against the pre-cut baseline). **And predicted and met:** reviewers report the paper as clearer — the
desk-reject simulator returned **SEND FOR REVIEW** and called the framing the paper's strongest
editorial quality.

---

## 2 · P0 — fix before anything is deposited

Each becomes permanent and citable the moment the deposit lands, or ships wrong inside it.

| # | finding | evidence |
|---|---|---|
| **P0.1** | **The chimera null's apportionment is a label the null cannot support** (B5-F1, corroborated in the opposite direction by B2-F3). Four sentences become false. **Does not touch 87, 61 or the title.** ⭐ **MEASURED 2026-08-16 — see §1.1a.** The corrected null reproduces **40.5%** of the observed **45.8%**, so the apportionment is deleted rather than re-stated. | §1.1, §1.1a |
| **P0.2** | **The archive manifest is both stale and wrong.** `aso_archive_manifest.py --check` exits **1**; `git_revision` is 77 commits behind HEAD, so the recorded manuscript hash is a pre-restructure file. Separately, `.files[*].contributes` pairs *"one design's 21 near-matches become 196 with 119 hybridisable"* — the artefacts give **47 → 196 (119 sense)** and **21 → 161 (5 sense)**, two different records conflated. The correct statement of that measurement left the paper in the cut, so the manifest is now its **only** home. | D3-F2 + A3-F1 |
| **P0.3** | **`submission-metrics.json` under-counts by 263 main words and 9 abstract words**, and every other deposit document points at it as "the one home" for those counts. | D3-F1 |
| **P0.4** | **The registry's `PUB-ASO` record states the opposite of the paper's headline** — *"specificity screening finds no competing match"* — and its `document.file` points at the working record, whose own first line disclaims it as not the submission. Propagates verbatim into two generated views. `systems/graph/*.json` is the repo's source of truth. | D3-F3 |
| **P0.5** | **The file that would be submitted is a repository document.** YAML front matter naming a venue the author eliminated *with its page charges*, two internal planning links, `ORCID: [to be inserted]`, two `[ARCHIVE DOI]` placeholders, and an SI HTML comment reading "EDITORIAL, NOT FOR SUBMISSION". | B4-F4 |
| **P0.6** | **Nothing in the three documents says these are research reagents rather than a medicine.** Zero hits for *not for human*, *must not be administered*, *in vitro use*, *not a medicine*. The paper supplies a complete synthesis order — sequence, chemistry, backbone, controls, dose–response — and custom oligonucleotide synthesis is commercially available to anyone. The nearest existing sentences are statements of past fact, not statements about use. | D1-F5 |
| **P0.7** | **The abstract's coverage sentence, found independently by four reviewers.** (a) *"reaching 68.4% of molecularly confirmed cases"* is the reading its own artefact forbids in terms — `_what_this_is_not[0]`: "Not a coverage measurement. No patient was screened." (b) The basis clause — that partner prevalence is discounted by a *different* 18-case series' breakpoint distribution — was in the baseline abstract and is now ~800 lines away. (c) The parenthetical propagates no partner-share uncertainty. (d) Three significant figures rest on a *TAF15* arm of **n = 3**, whose own quantum is ~5.2 points. (e) The denominator's own denominator — what fraction of EMC is molecularly confirmed — is stated nowhere. | D1-F3, A2-F1, B7-F2, B3-F5 |
| **P0.8** | **The abstract names two orderable sequences roughly five sentences ahead of the clause saying nothing has been made, and the YAML `scope:` block is stripped from both PDFs by the builder.** Every venue that truncates an abstract keeps the sequences and the percentage and drops the disclaimer, because the disclaimer is last. This is the round-5 P0.6 defect in its new position. The fix is a **move**, not a copy. | D1-F4, B4-F6 |
| **P0.9** | **A released genome-wide screen ships with no statement that it is uninterpretable.** The disclosure was deleted; `aso-premrna-offtarget-genomic.json` is still in the manifest and carries per-design 16/16 hits to BAC clones and immunoglobulin variable regions, which read as off-target findings. The paper's *other* genome scan is described at length, so the two are easy to conflate. | A3-F2 |
| ~~**P0.10**~~ | ⛔ **CLOSED — REFUTED 6 refuters of 6, 2026-08-16.** The §4.4 estimator (C3-F1) and its limit-of-quantification guard (C3-F2) both stand. **Nothing in §4.4 is edited for this item**, and C3-F2's remedy would have reinstated a defect round 6 fixed. Full reasoning: **§6.5 and §6.6**. | C3-F1, C3-F2 |

---

### 2a · Dispositions — what was applied to the manuscript, 2026-08-17

⛔ **NOTHING BELOW IS COMMITTED.** These are working-tree edits to
`fusion-junction-aso-research-article.md` and `fusion-junction-aso-supplementary-information.md`,
plus the two test re-pins each move forced. Every row names the fix and every other home of the fact
it changed.

| # | disposition | where it landed |
|---|---|---|
| **P0.5** | **APPLIED.** The `purpose:` block's eliminated-venue sentence and its per-page charge, and the two internal planning links, are gone; the SI's `EDITORIAL, NOT FOR SUBMISSION` comment is deleted and the SI's `purpose:` trimmed of editorial-process narration. `ORCID:` and both `[ARCHIVE DOI]` placeholders are **kept and flagged** — each now reads `PLACEHOLDER — AUTHOR TO SUPPLY BEFORE DEPOSIT` with the reason it blocks, because deleting them would hide a required author action. Both YAML `scope:` blocks now state in terms that they are stripped (article) or shipped whole (SI), so neither can be mistaken for the operative statement. | article frontmatter, author block, Methods → Availability, Declarations; SI frontmatter and head |
| **P0.6** | **APPLIED, four homes in the article and one in the SI**, each a statement about USE rather than about past fact. Box 1 opens with **Research use only — read before ordering anything**; §4.1 carries a **Research use only** block immediately ahead of the two sequences; Declarations carries the full **Research use only, and not for administration to any person or animal**; the abstract carries the short form ahead of the sequences; the SI carries it at its head. Each says the sequences are research reagents, not a medicine and not a candidate drug, that none may be administered to a person or animal or supplied for that purpose, and that commercial synthesis availability is a fact about access and not about fitness. `grep -in "must not be administered\|not a medicine\|research reagent"` now returns 10 lines across the two files, against 0 before. | Box 1, §4.1, Abstract, Declarations, SI head |
| **P0.7** | **APPLIED, all five defects.** (a) The abstract no longer says "reaching 68.4% of molecularly confirmed cases"; it says the figure "is arithmetic over two published cohorts and not a screening result: no patient was screened with either sequence". (b) The basis clause travels with the number in the abstract now, not 800 lines away. (c) §4.1 states that the interval propagates the **breakpoint fractions only** and gives the two partner-share Wilson intervals that are *not* propagated (67.2–87.8% and 8.4–26.9%). (d) Three significant figures are gone from the abstract — "roughly two thirds", with the *TAF15* arm's ~5.2-point quantum stated in §4.1 and "about five points" in the abstract. (e) The denominator's denominator is now stated in the abstract, §4.1 and §5: what fraction of EMC reaches molecular confirmation is **stated by no source retrieved here**. ⚠ **Other homes of 68.4%:** §4.1 keeps it (it is the derivation home, and `test_aso_submission_numbers.py` pins "the two are 68.4%"); §5 keeps it and now opens with the not-a-measurement framing; SI §S6 keeps all three (the ladder's basis, and a test pins "68.4% remains the coverage of the two reagents") and now points at §4.1 for what the figure is not. Generated Table 7 is untouched. | Abstract, §4.1, §5, SI §S6 |
| **P0.8** | **APPLIED as a MOVE.** "The work is computational: no wet-lab experiment was performed, no sequence named has been synthesised or tested, and nothing here asserts efficacy, safety, delivery to a tumour or clinical readiness." was the abstract's **last** sentence and is now the sentence **immediately preceding** the two named sequences; the research-use statement follows it and still precedes them. Verified through the PDF path rather than asserted: `parse_front_matter` on the built body puts the disclaimer at flattened offset 1274 and the research-use clause at 1586, against 1702 for `5′-GGGCATATCATCAAAC-3′`. `build_submission_pdf.py::strip_frontmatter` drops the YAML block from **both** styles, which is why the frontmatter copy is now labelled as routing-only. `test_build_submission_pdf.py` was re-pinned to the new tail **and given an ordering assertion**, so a future edit that moves either clause back behind the sequences fails the gate. | Abstract; `research/manuscripts/tests/test_build_submission_pdf.py` |
| **P0.9** | **APPLIED, restored in the restructured document's voice.** The deleted sentence at `c131f5a30` read *"An earlier genome-wide attempt against a mixed public corpus returned nothing interpretable and is released with the artefacts; it could not have done otherwise, having no defined nucleotide span to form a null against."* It is back in §5 as a two-paragraph block that also does what the deletion made necessary: **it names the file** (`aso-premrna-offtarget-genomic.json`), gives **both** structural reasons (no defined nucleotide span; a retrieval ceiling below chance — of nine designs queried, one failed at the service, seven returned exactly 50 records and the eighth 52), and states in terms that the per-design rows **look like off-target findings and are none**. ⭐ Counts re-derived from the artifact rather than from the ledger: 402 retained rows; six exact 16-of-16, four to genomic clone records and two to chromosome-6 annotation records; 55 immunoglobulin heavy-chain variable-region rows, **every one at 14 or fewer of 16** — the ledger's "16/16 hits to … immunoglobulin variable regions" is not what the file contains. The two genome scans are separated explicitly: screen 5 is the exhaustive GRCh38 scan with a measured 3.10 × 10⁹-nucleotide denominator and no scan-time cap. | §5 |

**The four P1 fixes verified by the parallel refuter, all APPLIED:**

| # | disposition |
|---|---|
| **B3-F3 + B2-F2** | **APPLIED as one abstract edit, reconciled with the P0.7/P0.8 rewrite.** "the five **known** partners" → "the five **modelled** partners", which is what `:503` ("a sixth partner, outside the five modelled here") and `:1166` ("the five partners are not the catalogue") already say. "another 19" → "19 pair a parent in precursor RNA … **and 13 of those 19 are already among the 87**". ⭐ The intersection was **re-derived here** rather than taken on trust, keying `aso-premrna-offtarget.json` and `aso-parent-gap-pairing.json` on (junction, antisense): 19 ∩ 87 = **13**, union **93**, so the compartment adds **six**. That union is now stated at its own home in §2.5 as well as in the abstract. The four correct "the five partners" scoping statements at `:207`, `:268`, `:320` and `:707` are untouched. |
| **C3-F7 / C4-F7** | **APPLIED at both sites**, Box 1 and §4.4. "no observed ratio can place a 95% upper bound below that cut" → "no observed ratio **at or above one** can place a 95% upper bound below that cut … so the test **can fail only where the reagent is anti-selective** and the design is otherwise void rather than negative". ⭐ The algebra was re-derived: t(0.975, df 2) = 4.302653, t/√3 = 2.484138, exp(2.484138 × 0.65) = 5.0263, so UCL < 5 whenever R̂ < 0.99476 — and R̂ = 0.50 gives UCL = 2.513. The paper's own "about 0.65" is exactly log 5 / 2.484138 = 0.64789, i.e. it is *defined* at R̂ = 1, which is where the dropped qualifier lived. |
| **B3-F1, first half** | **APPLIED.** The 98.3% bound now names **two** reasons and not one: the *TCF12* arm priced at its ceiling (+3.4 points) and the assumption that every remaining *EWSR1* breakpoint is covered (+15.9 points, needing three further reagents the retrieved record does not resolve to an exon). Both deltas and the reagent count are read from `fusion-junction-aso-coverage-ladder.json`, and `test_aso_submission_numbers.py` was re-pinned to derive them from that artifact rather than to spell them. ⚠ This is now consistent with `submission_tables.py`, which another agent had already fixed to print a bound's increment. The second half — "the 94.8% row is invisible in Table 7" — was **not acted on** and no generated table was touched. |
| **B6-F1 / B6-F2** | **APPLIED, both.** B6-F1: "were made in cells, on molecules already synthesised" was wrong for three of four, and now names each — an shRNA to the *FGFR3* side of *FGFR3::TACC3* improving survival in glioma-bearing mice (PMID 33241214), a *PML::RARα* siRNA preventing disease in NOD/SCID mice (PMID 21846246), and liposomal siRNAs against *TMPRSS2::ERG* in orthotopic and subcutaneous xenografts (PMID 23052253), with only PMID 36265509 describing no in vivo model. The paragraph's point survives and is stated: every one of those readouts needed the molecule to exist first. Every identifier and fusion name was copied from `lit-targets-aso-round7-precedents.json`, none written from recollection. B6-F2: the GalNAc precedent (PMID 37980543) now carries its scope at the one place it is cited — it reached patient-derived xenografts, the route works through the asialoglycoprotein receptor, which is a liver receptor, its applicability rests on fibrolamellar tumours retaining that receptor at hepatocyte levels, and an extraskeletal soft-tissue sarcoma satisfies neither premise. |

**The Table 6 record-count noun — APPLIED at all four article sites, and one more.** The column
`n_transcript_records` is incremented once per gap-paired hit per design
(`aso_offtarget_tissue_expression.py::_seam_rows`), so it is a **hit count summed over designs**, not
annotation depth. ⭐ **Re-derived here rather than taken on report**, by calling `_seam_rows` directly:
*NRP1* is 5 records over **1 distinct accession** returned by **5 designs**, and *HNRNPA2B1* is 100
records over **50 accessions** returned by **2 designs** — annotation depth cannot depend on how many
designs were run. The panel total re-sums to 649. Fixed: "123 of the panel's 649 **transcript
records**" → "**gap-paired hits**", with the distinction stated once at its home in §2.8 and both
extremes named; "smallest of the six by **record count**" → "**by hit count**"; "on five **transcript
records**" → "on five **gap-paired hits to a single accession**"; and the false explanation "the count
is a property of how densely the returned loci are annotated" → "the count says only how many
gap-paired windows the screen returned there". ⚠ **A fifth site, not in the list and wrong the same
way:** "robustness to register orders the loci differently again" implied an independent axis, and the
two are coupled by construction — a locus returned by more registers accrues more hits — so the
sentence now says so and names *NRP1* as the case that makes the orderings diverge anyway. **No figure
was changed: 123, 649, 67, 24 and the rest all stand.** ⛔ **This breaks one pin and the break is
expected and left in place:** `test_aso_submission_numbers.py::test_section_3_11_expression_figures_are_the_artifacts`
(line ~1171) asserts the old noun verbatim. It is the coordinator's to re-pin, and the new sentence
reads *"The \*EWSR1\* exon 12 reagent's six loci carry 123 of the panel's 649 gap-paired hits, and none
of the four measurable ones reaches the upper cut in liver or either kidney compartment"*.

⛔ **A CROSS-AGENT COLLISION THAT IS NOT MINE TO RESOLVE, LEFT UNTOUCHED AND FLAGGED (2026-08-17,
00:29).** While this pass was finishing, another agent regenerated the graded re-scores: **53 new
untracked `research/modalities/junction-aso-offtarget-*-graded.json` files**, all with mtime `00:29`,
taking the graded count from **39 to 92 of 93**. Evidence, not inference: `ls research/modalities/*-graded.json | wc -l`
returns 92, `git status` shows all 53 as `??`, and every one post-dates the last edit in this pass.
**Two tests are red because of it and neither is caused by anything here:**

- `test_aso_submission_numbers.py::test_the_released_screen_and_graded_counts_are_the_ones_on_disk`
  — `assert (len(screens), len(graded)) == (93, 39)` now gets `(93, 92)`.
- `test_junction_aso_graded.py::test_exactly_the_orientation_clean_designs_reach_zero_predicted_cleavage_load`
  — the predicted-clean set gained **`GGGCATATCAAGCGCT`**, the *TCF12* exon 7 design §2.7 discusses by
  name.

⚠ **Three sentences in the submission go stale the moment that regeneration lands, and they were
deliberately NOT edited here** — restating a count off a half-written, untracked artifact set is the
error rule 1 exists to stop, and the second failure suggests a *result* may move and not merely a
denominator:

- article `:1451` — *"and 39 of the 93 screens released in total (SI §S4)"*
- SI `:91` — *"The re-score of §6 covers all 38 junction screens, and 39 of the 93 screens released in total."*
- SI `:93` — *"the 53 deeper re-screens are released ungraded because the graded model adds nothing where no hit list is truncated"* — the whole rationale, retired if they are now graded.

**Whoever owns that regeneration owns these three sentences and the two pins**, and must check whether
the abstract's "six of the nine with no sense-strand near-match … lose the property at ten times the
search depth" still holds against the new graded set before the deposit.

**Other homes updated for these facts, outside the three documents:** the stale abstract quotation in
`research/modalities/tests/test_aso_parent_gap_pairing.py` (a comment, not an assertion), and the
`"another 19"` quotation in `fusion-junction-aso-preprint-checklist.md`. Nothing under
`submission_tables.py`, `lint_*.py`, `pinned-figures.json` or `test_round6_fixes_landed.py` was
touched, and no generated file was hand-edited.

---

### 2b · ⭐ NEW — a defect found by RUNNING the repository's own chain, in no round's finding list

**Found 2026-08-17, during the application pass, by `./scripts/regenerate_aso_chain.sh`.** It is
recorded here because it is a finding about the paper, not only about the tooling, and because no
reviewer in seven rounds could have seen it: it is invisible until the chain is actually run.

**What happened.** The chain's step 0 regrades **every** screen by glob — deliberately so, per its own
comment: *"Globbed, never listed: a screen added by a dispatch must enter the corpus without anyone
remembering to add it here."* Running it took the graded corpus from the committed **39** to **92**,
writing 53 untracked artifacts.

**⛔ The repository does not merely happen to hold 39 — it states a REASON for 39.** The SI says the
53 deeper re-screens *"are released ungraded because the graded model adds nothing where no hit list
is truncated"*. So the chain and the submission documents disagree about what the released corpus is,
and running the chain quietly makes three released sentences false (article §6 and SI §S4 twice) and
two pinned counts stale.

**⚠ IT LOOKED LIKE MORE THAN A DENOMINATOR, AND IT IS NOT. RESOLVED 2026-08-17.** With the 53
graded, the predicted-clean set gains one design, **`GGGCATATCAAGCGCT`** at *TCF12* exon 7 —
`test_junction_aso_graded.py::test_exactly_the_orientation_clean_designs_reach_zero_predicted_cleavage_load`
fails with *"Extra items in the left set"*. That was escalated here as a possible open question about
the paper. **It is not one, and the escalation was wrong.** Traced:

- In the base screen `junction-aso-offtarget-tcf12e7n3.json` the design carries
  `status: screen_failed`, `n_true_cleavage_risk: null` and no histogram — the remote service failed
  for that oligo, so `screen_is_gap_resolved` correctly refuses it and it was never graded there.
- Its successful record is in `junction-aso-offtarget-tcf12e7n3-clean9-deep500.json`:
  `status: screened`, `n_true_cleavage_risk: 0`, histogram present.
- ⭐ **And the manuscript already reports exactly that**, at the sentence beginning *"all seven
  returned at the deeper ceiling"*: *"six of them dirty and one — 5′-GGGCATATCAAGCGCT-3′ at *TCF12*
  exon 7 — with three near-matches and none on the sense strand. So the set of designs with a
  complete hit list and no sense-strand near-match is **four at this depth rather than three**: a
  design the shallower pass never screened joins the three."* It is discussed again where its
  eight-base-pair parent run is given, named among the three mechanism controls, and printed in
  generated Table 7 with `0 → 0`. **Round 3 verified the same fact independently** — *"the seven
  default-depth failures all return at depth | six dirty, one clean (`GGGCATATCAAGCGCT`)"*.

**So grading the 53 adds no FINDING the paper does not already state — it adds artifacts.** The SI's
rationale stands as written, and the correct reading of the test is narrower than it first appeared:
its expected set describes the GRADED CORPUS, which is a smaller object than the paper's clean set,
and the paper's clean set is the one that carries the claim.

**Disposition: CLOSED — keep 39, and the reason is positive rather than an omission.** Every result
the deeper re-screens carry is already reported, with its depth caveat, in the manuscript and in
Table 7. The 53 untracked artifacts were deleted. ⛔ **What remains is a real hazard and is fixed:**
the chain regenerated them silently, and a reader comparing the graded corpus against the paper's
clean set would have found a discrepancy with no note explaining it.

**Instrument.** The class — *a regeneration script silently producing artifacts that contradict a
documented decision* — was already caught, by
`test_aso_submission_numbers.py::test_the_released_screen_and_graded_counts_are_the_ones_on_disk`,
which is why the state was recoverable at all. What was missing is a warning at the moment of
overproduction rather than a test failure later, so the chain now compares on-disk against tracked and
**fails** with the decision spelled out.

---


### 2c · ⭐ THE FULL DISPOSITION RECORD — every finding ID, 2026-08-17

⛔ **CORRECTION FIRST, because it is the reason this section exists.** The commit
`533386f55` is titled *"all 93 remaining findings dispositioned"*. **That was wrong when written.**
Three disposition passes were commissioned; **only one returned**, covering 28 IDs. Completion was
inferred from having *commissioned* three rather than from having *received* three — an absent
reading treated as a reading of absence, which is the same defect this round's own P0.9 and the PGR
finding below are about. The two missing passes were recoverable and were recovered. The table below
is the real record; the commit title is not.

**Key:** APPLIED — landed in the working tree. REFUTED — the charge does not stand on the artifacts.
DECLINE — real observation, deliberately not acted on, reason given. AUTHOR — decided here rather
than deferred (see §2d).

| id | disposition | note |
|---|---|---|
| **A1** (16 items) | REFUTED as a class | A1 returned zero findings: 16 of 16 protected items present, one checked byte-for-byte. |
| A2-F1 | APPLIED | abstract coverage sentence rewritten (P0.7). |
| A2-F2 | APPLIED | the strict-end label collision is gone. |
| A2-F3 | APPLIED | both leads' parent runs now named — 8 bp and 9 bp, both against wild-type *TFG*. |
| A2-F4 | APPLIED | Box 1 states the 5.0 cut as a convention. |
| A2-F5 | APPLIED | the hit-cap's direction restored in §6. |
| A2-F6 | APPLIED | the deeper-ceiling depth label, plus a new *PGR* absent-reading caveat. |
| A2-F7 | APPLIED | the abstract now carries the corrected exon-terminus null at 40.6%. |
| A3-F1 | APPLIED | the 47 → 196 / 21 → 161 records separated (P0.2). |
| A3-F2 | APPLIED | the uninterpretable genome screen's disclosure restored (P0.9). |
| A3-F3 | APPLIED | the censoring worked examples restored in measured form — 47 untruncated, 37 rose, none fell. |
| A3-F4 | APPLIED | the 1,129-neighbour derivation behind 2.6 × 10⁻⁷ stated. |
| A3-F5 | APPLIED | *H2AP* now carries NM_012274. |
| A3-F6 | APPLIED | the 13 unread loci carry their attribution again. |
| A3-F7 | APPLIED | abstract loads (see B4-F1). |
| A4-F1 | APPLIED | "Supporting" → "Supplementary" everywhere. |
| A4-F2 | APPLIED | Table 7's caption scope, at the generator. |
| A5-F1 | APPLIED | §2.7 now composes the mature-parent screen, which is what excludes the fourth design. |
| A5-F2 | APPLIED | Table 7 gained the *TFG* e7::*NR4A3* e3 row, plus a build gate against the spec diverging. |
| A5-F3 | DECLINE | the chain survives at its single home in §4.1; a second copy is the drift this pass removed. |
| B1-F1 | REFUTED | 181 of 190 **is** in Results (§2.9), and the threshold's stated-not-measured character has three homes. |
| B1-F2 | APPLIED | "exactly what RNase-H1 requires" was false — §6 records this architecture at six RNA:DNA nt, below the source's 7–10. |
| B1-F3 | APPLIED | the free-energy claim scoped to the measured 19.9% cross-margin discordance. |
| B1-F4 | DECLINE | the −8.66 median has a home in §2.10's artifact; adding it to prose duplicates a fact without changing a conclusion. |
| **B1-F5** | **REFUTED — and inverted** | the artifact field is a wild-type-parent LIABILITY counter, so the omitted 6-nt reading is the count that **flatters** the paper. The paper printed the pessimistic series. |
| B1-F6 | APPLIED | the CpG numeral now attaches to what it counts. |
| B1-F7 | DECLINE | the 5-8-5 confound is real but §4.2 already calls the arm a control rather than a test of gap length alone. |
| B1-F8 | DECLINE | a direction would be an LNA claim §6 explicitly declines to compute; the current form is the pessimistic reading. |
| B1-F9 | APPLIED | the biodistribution premise now states that no measurement or citation was retrieved for it. |
| B1-F10 | DECLINE | discretionary generator column; the liability audit has homes at §2.10 and §6. |
| B1-F11 | DECLINE | the 5-8-5 datum is real; it strengthens §4.2 and is held for a refuter rather than added on one reading. |
| B2-F1 | REFUTED | no total is stated anywhere; the sharper replacement was taken instead. |
| B2-F2 | APPLIED | 13 of the 19 pre-mRNA designs are already among the 87; the abstract says so. |
| B2-F3 | APPLIED | corroborated B5-F1 in the opposite direction; superseded by the measurement in §1.1a. |
| B2-F4 | APPLIED | the null intervals now carry the same clustering caveat as the observed rate. |
| B2-F5 | APPLIED | Table 6's column renamed to gap-paired hits; the annotation-depth claim removed. |
| B3-F1 | **half APPLIED, half REFUTED** | the 98.3% bound has two reasons, and that is now stated. ⛔ "the 94.8% row is invisible in Table 7" is **false** — the row prints in full. |
| B3-F2 | APPLIED | ⭐ the two *TAF15* series are not shown to be independent cohorts; the arm may be as few as three. |
| B3-F3 | APPLIED | "five known partners" → "five modelled partners". |
| B3-F4 | REFUTED | the quotation is anchored on `origin/literature-cache`; a locality item, not a provenance failure. |
| B3-F5 | APPLIED | folded into P0.7. |
| B3-F6 | APPLIED | candidates/controls reconciled. |
| B4-F1 | APPLIED | the abstract promised loads and gave none. |
| B4-F2 | APPLIED | the ten-base-pair threshold is named as adopted. |
| B4-F3 | P3 | venue-triggered; bioRxiv has no IMRaD template. |
| B4-F4 | APPLIED | the repository document stripped (P0.5). |
| B4-F5 | APPLIED | the abstract's do-not-use clause no longer attaches the controls to the condemned three. |
| B4-F6 | APPLIED | the disclaimer moved ahead of the sequences (P0.8). |
| B4-F7 | P3 | ⚔ direct conflict with D4; recorded, not resolved. |
| B4-F8 | P3 | venue-triggered. |
| B4-F9 | DECLINE | the re-derivation command is right, but its wall time must be measured, not typed; held rather than asserted. |
| **B5-F1** | **APPLIED — measured** | the round's top finding. See §1.1a: the apportionment is deleted, not restated. |
| **B5-F2** | **APPLIED** | ⭐ the *PGR* seam's pre-mRNA compartment is UNMEASURED, not clean. Three homes, one of which this pass had added. |
| B5-F3 | APPLIED | the cleavage claim lowered to hybridisation. |
| B5-F4 | DECLINE | the procedure's two unreachable classes are stated at §2.6; a second statement in §4.5 duplicates it. |
| B5-F5 | DECLINE | Table 6's "1 of 1" denominator is honest as printed; the caption change risks more confusion than it removes. |
| B5-F6 | DECLINE | Table 2's margin cell follows the screened set by design, and Table 4 prints the margin-3 designs. |
| B6-F1 | **APPLIED — CI fetch** | three of the four precedents reached in vivo mouse models. Committed evidence. |
| B6-F2 | **APPLIED — CI fetch** | the GalNAc route is liver-restricted via ASGPR and does not transfer. |
| B6-F3 | DECLINE | the 12-antigen negative is real and worth citing; held for a refuter because it adds a released claim. |
| B6-F4 | REFUTED | all four sites already condition on systemic dosing. |
| B6-F5 | REFUTED | the two sentences are adjacent and reconciled by the next one. |
| B7-F1 | DECLINE | see B1-F5 — the charge is inverted; both series may be worth printing, but not on this reading. |
| B7-F2 | APPLIED | folded into P0.7. |
| B7-F3 | APPLIED | the Discussion's four rounded figures returned to their artifact values. |
| B7-F4 | APPLIED | 95% → 94.8%, matching the SI and Table 7. |
| B7-F5 | APPLIED | same clustering caveat as B2-F4. |
| B7-F6 | APPLIED | the gap-paired ranks (5th, 1st) added; the ≤2-mismatch ranks re-attached to their own axis. |
| C1-F1 | DECLINE | the exon-label ambiguity is real and is stated at §2.3; the second half is refuted — the alternative-reading reagents are Table 7 rows. |
| C1-F2 | DECLINE | same as B5-F6. |
| C1-F3 | P3 | the paper deliberately prescribes no assay. |
| C1-F4 | DECLINE | naming a curve-fit model prescribes the assay §4.4 declines to prescribe. |
| C1-F5 | DECLINE | the scramble is specified as an orderable class; naming one sequence would oblige it through all five screens. |
| C2-F1 | REFUTED | every number the charge says is unstated is printed — §2.6 and Table 7. |
| C2-F2 | APPLIED | "sits at floor" replaced by the measured 0.941 at the 83rd percentile of 1,673 lines. |
| C2-F3 | DECLINE | "exactly one route" is refuted by the paper's own cited analogue. |
| C2-F4 | **APPLIED — CI read** | `GSE299349` is public; `GSM9037837` is a patient-derived EMC cell model. ⚠ its series' own design lists five sarcoma types and not EMC — recorded, and no fusion call made. |
| C2-F5 | DECLINE | the two usable models are named in the artifact with RRIDs; adding them to the paper is C5-F1's edit and lands there. |
| C2-F6 | APPLIED | the cryptic-exon test article's reagent cannot be certified under §4.5's own rule, and now says so. |
| C2-F7 | APPLIED | the STR profile is concordant at every locus but one, which is now named. |
| C2-F8 | APPLIED | "no third party who can decline" was false; the backbone is academic and non-profit only. |
| C2-F9 | APPLIED | the fusion caller is named — DepMap 24Q4, model ACH-001519, both calls quoted. ⚠ **H-EMC-SS identity is DISPUTED** (OBJ-LINE-HEMCSS): the model ID is cited only to make the caller checkable, and §3's conclusion that the line cannot serve as a test article does not rest on it. |
| C2-F10 | DECLINE | §4.4's nucleotide-resolution rule already closes the line independently; a second reason is redundant. |
| C3-F1 | **REFUTED — 3 of 3** | §6.5. |
| C3-F2 | **REFUTED — 3 of 3** | §6.6. Its remedy would have reinstated a defect round 6 fixed. |
| C3-F3 | DECLINE | the placement contradiction is stated; prescribing one is outside §4.4's scope. |
| C3-F4 | APPLIED | the cut now states it reads only the acceptor parent, and requires the donor measurement beside it against no threshold. |
| C3-F5 | DECLINE | the comparator is the fallback where the ratio is void; the charge's 1× figure is not verifiable on disk. |
| C3-F6 | APPLIED | the scrambled control is now routed to the parent screen this paper generated the number for. |
| C3-F7 | APPLIED | "no observed ratio" → "no observed ratio at or above one". Two sites. |
| C4-F1 | APPLIED | the falsification claim is scoped to the top margin, in all four homes. |
| C4-F2 | DECLINE | the unguarded fusion direction is real; guarding it prescribes an assay §4.4 declines to prescribe. |
| C4-F3 | APPLIED | a multiplicity paragraph, stating why no correction is imposed. |
| C4-F4 | DECLINE | "independent biological replicates" already carries the variance structure. |
| C4-F5 | REFUTED | the 30% figure at three replicates is already stated. |
| C4-F6 | APPLIED | the pilot's required return and a stop rule, without inventing an n. |
| C4-F7 | APPLIED | with C3-F7. |
| C5-F1 | DECLINE | the construct-to-lead mapping is the highest-value edit in the ledger and is held for a refuter, not dropped. |
| C5-F2 | REFUTED | panel coverage, not ordering; §4.4's rule is unqualified. |
| C5-F3 | REFUTED | all four numbers are printed in Table 7 and §2.6. |
| C5-F4 | APPLIED | with A2-F3. |
| C5-F5 | APPLIED | the modal-outcome contradiction resolved. |
| C5-F6 | REFUTED | the comparator establishes the void state; it is not claimed to raise abundance. |
| C5-F7 | APPLIED | with C4-F6. |
| C5-F8 | APPLIED | the §4 heading no longer claims a decisiveness the section disclaims. |
| C5-F9 | DECLINE | stating experiment scale needs prices this repository has deliberately not retrieved. |
| C5-F10 | APPLIED | Table 7's title narrowed at the generator, with the three controls named. |
| C5-F11 | DECLINE | ⛔ would commit the author to run the pipeline for third parties — an outward-facing commitment this pass may not make. |
| D1-F1 | REFUTED | §6.1. |
| D1-F2 | REFUTED | §6.2. |
| D1-F3 | APPLIED | P0.7. |
| D1-F4 | APPLIED | P0.8. |
| D1-F5 | APPLIED | P0.6 — research-use statements, now including the generated tables file. |
| D1-F6 | APPLIED | candidates/controls. |
| D1-F7 | APPLIED | the cleavage claim. |
| D1-F8 | APPLIED | "reagent" → "candidate". |
| D1-F9 | APPLIED | "where the drug goes" → "in the organs a systemic dose reaches", four sites. |
| D1-F10 | APPLIED | the abstract's do-not-use clause. |
| D2-F1 | APPLIED | the ~5-fold figure is disclosed as a restatement. |
| D2-F2 | APPLIED | the "We previously discovered" clause disclosed. |
| D2-F3 | APPLIED | two of the four paralogue sources are reviews. |
| D2-U1 | **UNVERIFIED** | ref 39 is not open access; a full-text fetch was dispatched and its result is not in hand. Recorded as unverified rather than guessed. |
| D3-F1 | APPLIED | P0.3. |
| D3-F2 | APPLIED | P0.2. |
| D3-F3 | APPLIED | P0.4. |
| D4-F1 | APPLIED | beat 3 promoted qualitatively; 82.9% stays at its single home. |
| D4-F2 | APPLIED | with D1-F6. |
| D4-F3 | P3 | figure budget. |
| D4-F4 | DECLINE | naming the two modules is right; held with B4-F9, which shares its verification. |
| D4-F5 | APPLIED | the Introduction's second question no longer excludes the paper's own answer. |
| D4-F6 | **DECIDED** | title half declined with reason; keywords half applied. |
| D4-F7 | DECLINE | a closing renewal is advocacy the language discipline forbids. |
| D4-F8 | APPLIED | §4.5 now points at its one worked case outside the panel. |

**ZERO OPEN**, with one honest exception: **D2-U1 is UNVERIFIED**, not dispositioned, because its
source is not open access and the fetch has not returned. It is recorded that way rather than
guessed, which is the rule this repository is built on.

---

## 3 · P1 — wrong, unsupported or unexecutable; not deposit-blocking

### 3.1 · The lead reagents' own parent liability — four reviewers, one defect

- **Both named reagents pair a wild-type parent through the whole catalytic gap** — 8 bp and 9 bp
  against *TFG* — and are clean only because the cut is 10. `longest_run_through_gap` returns 0 unless
  every gap position is paired, so the field name is the proof. §2.7 applies exactly this caveat to a
  control at 8 bp; §4.1 applies it to one lead and not the other, at the sentence a laboratory reads
  immediately before ordering. At seven — the other end of the paper's own cited range — **both** leads
  cross the criterion, and §4.1 flags only one. (A2-F3, C5-F4)
- **181 of 190 designs pair a mature parent's whole six-nucleotide DNA gap**, which already meets every
  catalytic minimum the paper cites; the 10-bp cut is an occupancy criterion the on-target mechanism
  does not require, and the paper says so in Methods and not in Results. (B1-F1)
- **The two reagents for the only fusion-positive EMC cells are worse**: 25 → 6 and 128 → 6 gap-paired
  loci, with 8 bp against wild-type *EWSR1* and **9 bp against wild-type *NR4A3* itself** — the
  transcript the modality exists to spare. §3 hands a laboratory both and states none of it.
  (C2-F1, C5-F3)

### 3.2 · "Candidates" vs "controls" — three reviewers

§2.7 calls three designs *"candidates in the whole panel"* and *"the honest size of the candidate
set"*, under a heading promising candidates; §4.4 says the same three molecules *"are mechanism
controls rather than candidates"*. A reader navigating Results by heading for "what do I make?" finds
the one heading that offers it, reads that none of the three sits at a junction a patient is reported
to carry, and takes away the opposite of what §4.1 says. (D1-F6, B3-F6, D4-F2)

### 3.3 · A cleavage claim above its evidence — two reviewers

§2.6's bolded lead — the sentence a skimming reader quotes — states *cleave*, where §5 says all five
screens address hybridisation only and the artefact's own verdict string is a hybridisation statement.
The abstract and Box 1 both get it right with *"pairs its whole catalytic gap against"*. The error runs
in the cautious direction, which makes it an integrity defect rather than a safety one, and it is still
the paper's hazard claim stated above its evidence. (D1-F7, B5-F3)

### 3.4 · The decisive experiment — the round's largest cluster (C1, C3, C4, C5)

- **The threshold is registered for a claim it does not test.** §4.4 says the two reagents *"measure
  the level of selectivity at the top margin rather than whether selectivity orders by margin"*, while
  the Introduction and §4 twice say the threshold would falsify *the ranking*; the one arm that would
  test the ordinal claim is explicitly exempted from any rule. (C4-F1)
- **The void condition is one-directional.** An unresolvable *fusion* knockdown drives the ratio down,
  which the one-sided rule reads as evidence against the reagent — so an assay failure can present as a
  falsifying result. The wild-type direction is guarded; the fusion direction is not. (C4-F2)
- **"No observed ratio can place a 95% upper bound below 5" is false below a ratio of 1**, and the error
  protects an anti-selective reagent. Two reviewers, identical algebra, five-word fix. (C3-F7, C4-F7)
- **The pre-registration leaves its own measurement free.** *"No assay is prescribed here"* sits beside
  *"the pre-registrable threshold"*; and under the upstream placement the numerator and denominator are
  measured with structurally opposite sensitivity to the event being counted, which is not a bias to
  report but an invalid estimator. C3 shows the downstream placement is prescribable at zero cost for
  all 38 exon-3-acceptor junctions, including both leads. (C3-F3)
- **The cut sees only wild-type *NR4A3***, while §3 argues the modality's whole advantage is sparing the
  *donor* parents — and §2.7 excludes a design precisely for an 11-bp duplex with its own donor. That
  failure mode is invisible to the registered statistic. (C3-F4)
- **The comparator is justified by a failure mode it cannot fix.** *Isogenic* means the same promoter,
  so the largest possible difference in wild-type *NR4A3* abundance is 2×, and in the cited precedent's
  construction it is 1×. Two reviewers. (C3-F5, C5-F6)
- **The scrambled control is not required to clear the parent screen**, on the paper's own measurement
  that 6.2% of scrambles fail it and 1.8% hit wild-type *NR4A3* — a number this paper generated and did
  not route to the control it generated it for. (C3-F6)
- **The pilot that gates everything has no design** — no n, no test article, no proceed/stop rule — and
  an SD is the one statistic three replicates cannot estimate. (C5-F7, C4-F6)
- **The modal outcome has no home.** §4.4 names the margin-contrast arm as what resolves a reading
  inside the 1–5 span, then twelve lines later says a difference between those arms is not attributable
  to margin alone. A laboratory is asked for months of work and told in advance the likeliest result
  cannot be read. C5 calls this the single strongest argument against taking the paper on. (C5-F5)
- **Between-batch variance is never named**, so no replicate count samples it. (C4-F4)
- **No multiplicity rule** for an open-ended stream of reagents against one fixed cut. (C4-F3)
- **n = 3 is powered against "no effect", not against the paper's own worked near-miss** — ~30% at the
  paper's own illustrative SD, reaching ~80% only at SD ≲ 0.15. (C4-F5)
- **No curve-fit model and no CI-construction method for the ratio** — Fieller, delta and bootstrap
  disagree most at n = 3–6, which is where the void analysis lives. (C1-F4)
- **The scrambled control is specified as a 200-draw statistical procedure, not an orderable
  sequence.** (C1-F5)

### 3.5 · Test articles and cell models (C2, C5)

- **The mapping that makes the ask fundable is in the artefact and not in the paper**: the two published
  constructs are *EWSR1* e12::*NR4A3* e3 and *TAF15* e6::*NR4A3* e3 — exactly the two lead junctions. A
  PI who reads only the paper concludes the leads are untestable. **C5 names this the one fix that
  changes its answer from no to yes.** (C5-F1)
- **§3 names the line that cannot be used and names neither of the two that can**, nor the third; the
  names, RRIDs and a named contact are all on disk. A reader cannot request a line it cannot name.
  (C2-F5)
- **A public RNA-seq deposit carries 176 reads across a seam identical to the lead reagent's target
  window** (`SRR33903995`, sample `USZ-23_EMC3`), and no document mentions it — while the paper does
  report the read-archive *negative* it found. Whether that sample is a model or a tumour is not
  established anywhere readable, and one deposit is not a distribution. (C2-F4)
- **"Its *NR4A3* expression sits at floor" drops the number, the percentile and the generator's own
  grading of that leg as weak corroboration.** (C2-F2)
- **The fusion caller behind the paper's central cell-line caution is unnamed and therefore
  uncheckable** — no resource, no release, no model accession. (C2-F9)
- **The acceptor ambiguity is declared neutralised by holding two reagents, where §4.4 forbids ordering
  against an unsequenced junction.** (C5-F2)
- **The mandatory comparator is obtainable on exactly one route — the one the paper says is not the
  disease** — and that asymmetry decides whether the experiment is a month or a year. (C2-F3)

### 3.6 · Chemistry and thermodynamics (B1, B7)

- **"The free energy is not an independent ranking" is refuted by the paper's own thermo artefact**:
  the length identity holds for 190 of 190, but 19.9% of cross-margin design pairs are discordant, and
  margin-3 ΔΔG is entirely nested inside margin-1's range. (B1-F3)
- **The artefact names the absolute parent ΔG as the decision-relevant column and it is not reported** —
  a −8.7 kcal/mol parent duplex before any LNA contribution forms readily, so "binding discrimination is
  not what constrains the modality" mis-locates the question. (B1-F4)
- **The second cited DNA minimum is omitted, and it is the architecture-matched one.** The artefact
  carries both series; the 6-nt reading gives **0 of 190** at the geometry both leads use, against the
  reported 76 of 190 at 5 nt, and the artefact's own `_why_two` says the choice "would decide the
  headline". Two reviewers. (B1-F5, B7-F1)
- **"A base substitution removes" is the wrong remedy for a CpG**, and in six of seven cases the
  substitution lands inside the catalytic gap — the positions the whole margin ranking is built on. The
  field's mitigation is 5-methylcytosine, which the artefact's own rule text points at and no document
  names. (B1-F6)
- **The 5-8-5 arm confounds gap length with oligonucleotide length and target affinity** (3.8 kcal/mol
  at the lead seam), and the paper names every co-varying variable for the margin arm and none for this
  one. (B1-F7)
- Minor: the "exactly what RNase-H1 requires" contradiction (B1-F2); the pre-mRNA mismatches all falling
  at LNA positions, direction unstated (B1-F8); the phosphorothioate biodistribution premise being the
  paper's one uncited pharmacological claim (B1-F9); Table 4 carrying no sequence-liability column
  (B1-F10); the one empirical gap-length series' 5-8-5 datum dropped where the source is characterised
  (B1-F11).

### 3.7 · Nulls, denominators, the coverage ladder and the generated tables (B2, B7, A5, B3)

- **The nine pre-mRNA *NR4A3* designs are a strict subset of the 87 and of the 61**, presented as a
  second population; the pre-mRNA arm adds **zero** designs the mature screen had not already flagged.
  (B2-F2)
- **Table 6's "transcript records" column is the screen's per-locus gap-paired hit count, not annotation
  depth**, which is what its caption tells a reader it is — and it is the quantity §4.3 uses to compare
  the two reagents. Generated: the fix belongs in `submission_tables.py`. (B2-F5)
- **Wilson intervals are applied to 200-draw-per-design clusters**, and the "nominal" caveat the paper
  already writes is attached to one of the six or seven numbers in the comparison. Two reviewers; both
  state explicitly that this is not the junction-clustered CI declined in prior coverage. (B2-F4, B7-F5)
- **Table 7 omits *TFG* e7::*NR4A3* e3**, the one in-panel published-breakpoint junction the prose
  reads as structurally identical to a row the table keeps, under a caption claiming completeness.
  (A5-F2)
- **"Ranking 26th and 13th of 176" attaches to the wrong antecedent** and is wrong under the natural
  reading — the true gap-paired ranks are 1st and 5th and appear nowhere. (B7-F6)
- **The coverage ladder's 98.3% silently prices the whole *EWSR1* arm at 100% of its breakpoints**,
  while the sentence blames only the *TCF12* distribution; 15.9 of the 19.3 points come from an
  assumption never mentioned, and the 94.8% row is invisible in Table 7 because a `setdefault` had
  already claimed its junctions. (B3-F1)

### 3.8 · Restructure defects introduced by the pass (A2, A5)

- **§2.7 now composes the wrong section.** A demonstrative that always meant the parent-liability
  screens was resolved to the section newly inserted ahead of it, whose exclusions are inapplicable to
  the three designs the sentence derives. Fresh, and introduced by this restructure. (A5-F1)
- **"Strict end" now labels opposite ends of the same 7–10 range** in the two places the paper points
  between, so which direction is conservative is unrecoverable from the text. (A2-F2)
- **The hit cap's direction was lost where the screen is defined** — the text names the effect and not
  its sign, and the sign survives only as a §5 heading 250 lines later. ⚠ A2 self-flagged this as the
  round's clearest yo-yo risk: three copies reduced to one. (A2-F5)
- **Four exon-2-acceptor counts carry no depth label** and are deeper-ceiling numbers, in the one
  paragraph where every neighbouring count is labelled. **Class B.** (A2-F6)
- Minor deletions with a single home: the untruncated-list demonstration (A3-F3), the 1,129-16-mer
  derivation behind the 2.6 × 10⁻⁷ chance probability (A3-F4), the `NM_` accession in the sentence whose
  whole point is the `NM_`/`XM_` namespace (A3-F5), the attribution of thirteen blank expression
  readings to what the loci are (A3-F6), the *TCF12*-recurrence provenance chain (A5-F3).

### 3.9 · Disease, clinical and citation semantics (B3, B6, D2)

- **"The five known partners" is a false statement about the disease** in the abstract, contradicted
  twice in the paper's own body, which names a sixth and says the five are not the catalogue. One-word
  fix. (B3-F3)
- **The two *TAF15* TKI arms may be the same patients.** The pooling artefact records `"CANNOT BE SHOWN
  NON-OVERLAPPING WITH THE PAZOPANIB TRIAL"` and sets `"pool": false` on that cohort; the manuscript's
  "three to five" comes from that overlap bound and never states the overlap. "Across the two series"
  reads as two independent cohorts concurring. (B3-F2)
- **Two undisclosed citation restatements**, in a paper that discloses this class correctly everywhere
  else: the ~5-fold discrimination figure is attributed to earlier work in its source's own abstract and
  Results while the manuscript calls it *measured*; and one clause of the paralogue block is its
  source's "We previously discovered", asserted flat beside a sibling sentence that flags exactly this.
  (D2-F1, D2-F2)
- **The paper's own 12-antigen delivery screen is not cited where the antigen prerequisite is named**,
  though it returned a named negative and costs $0 to reference. (B6-F3)
- ⚠ **Two B6 findings rest on uncommitted retrieval and must not be applied as written.** B6-F1 (three
  of the four cited parental-sparing precedents reached in vivo mouse models, so *"were made in cells"*
  is wrong for them) and B6-F2 (the GalNAc/ASGPR route is liver-restricted and does not transfer to
  extraskeletal soft tissue) were sourced from WebSearch snippets, because the proxy blocks PMC. Under
  this repository's citation rule they need a committed fetch product first — see P3.

### 3.10 · Narrative and referee-facing (D4, B4)

- **Beat 3's strongest form is SI-only**: that every junction at which a published report places a
  patient's breakpoint now carries a screened design, and that those nine reach 82.9% on a pooled basis.
  A main-text reader never learns it. (D4-F1)
- **The released procedure omits the two tools a new breakpoint may need.** §4.5 names five `.py` files;
  the un-rearranged-allele scan it says "applies as well" is produced by two modules named nowhere,
  among six hundred. It is the one step of the released procedure a reader cannot run. (D4-F4)
- **The Introduction poses the second question and pre-commits to an answer space that excludes the
  paper's own answer** — "a stock reagent or a panel", where §4.5's deliverable is neither. (D4-F5)
- **Nothing tells a referee which numbers to verify or how**, while four separate sentences correctly
  establish that a language model wrote and ran the pipeline, that a prior version was withdrawn in
  full, and that no independent review exists. B4 names this the single most likely cause of a referee
  declining, and the fix — one sentence naming the command and its wall time — costs nothing that is not
  already true. (B4-F9)
- **The abstract says "with their off-target loads" and then gives no load**, so a reader concludes the
  two reagents named are the paper's clean designs, which they are not. (B4-F1) ⚠ A3-F7 is the same
  defect from the deletion side and **its** fix restores text removed as duplication; B4's does not,
  because it asks for the numbers, which live in §4.3.
- **The abstract carries 87 of 190 without the paper's own "stated, not measured"**, so "nearly half"
  reads as a property of the design space rather than of the design space at one chosen cut. This is
  placement of a caveat the paper already writes, not the withdrawn charge about how the cut was chosen.
  (B4-F2)

### 3.11 · Seams the five-screen criterion cannot reach, and two tables scoped narrower than they read (B5, C1)

- **The *PGR* seam is reported as graded by all five screens; two artefacts record its donor parent was
  never scanned.** `⛔_parents_in_the_atlas_that_were_NOT_scanned` names *PGR* explicitly and says the
  genes there are "UNMEASURED — not clean", so that row's zero is an absent reading, not a reading of
  absence. §2.6's stated *PGR* caveat is about the transcript model, not about a screen that could not
  run. (B5-F2)
- **§4.5's acceptance criterion cannot be evaluated on two real, published breakpoint classes** — the
  cryptic-exon acceptor, where three of five instruments return an absent count, and a partner outside
  the six modelled transcripts, which loses two screens on its own donor gene. §4.5 states its limit as
  "a candidate, not a validated reagent" and not as this. (B5-F4)
- Minor: Table 6's register-robustness column has a denominator of one at the lead reagent's own
  junction while printing "x of 5" elsewhere (B5-F5); Table 2's "highest gap-level margin" is the
  highest among *screened* designs, and the true top-margin register at two junctions failed at the
  remote service (B5-F6, C1-F2 — two reviewers).
- **Table 7's *TAF15* e6::*NR4A3* e2 row rests on an acceptor reading the artefact says is not settled**
  — `⚠_read_this_before_using_the_sequence`: "THE ACCEPTOR EXON INDEX IS NOT SETTLED … Two readings
  survive" — while the text calls those four seams "a published exon-resolved breakpoint" without
  qualification, and the alternative-reading reagent never reaches any table. (C1-F1)

---

## 4 · P2 — wording, placement and register

The abstract's do-not-use clause attaches the controls and the falsification cut to the three condemned
designs by proximity (D1-F10, B4-F5 — **two reviewers**) · *"a reagent can be designed"* where the body
twice refuses that word (D1-F8) · *"the drug"* as a definite noun four times, where Table 6's legend
already owns the hedged form (D1-F9) · the abstract renders "arbitrary sequence" as the lowest of four
chance nulls (A2-F7) · Box 1 states the cut as a bare number without the fact that it is a convention
(A2-F4) · the Discussion rounds three figures to whole per cent in the one paragraph that compares them
(B7-F3) · "is 95%" in the main text against the SI's "does not reach 95%" for the same fraction (B7-F4)
· the *TAF15*-response sentence's surrogate-versus-mechanism hedge, the residual of refuted D1-F2
· "Supporting Information" for a document called Supplementary everywhere else (A4-F1) · Table 7's
caption claims a narrower scope than its own rows and self-corrects two sentences later (A4-F2) · the
exposure-organ premise stated as settled fact in four places while the delivery route is a live
three-way question elsewhere (B6-F4) · "the exposure reading is the one that speaks to the question a
count cannot" four sentences from "neither axis is a risk ranking" (B6-F5) · the "decisive experiment"
heading against a control set the same section says cannot decide the mechanism (C5-F8) · §4 declared
the paper's output for a laboratory with no statement of scale, its one cost sentence about the cheapest
item (C5-F9) · Table 7 titled "every reagent named in §4" while omitting two of the three required
controls (C5-F10) · §4.5 releases a design procedure and never offers to run it (C5-F11) · beat 1 never
renewed against the evidence, so the paper's last word on the route's worth is discouraging (D4-F7) ·
beat 4's only worked demonstration filed under Bounds rather than cited from §4.5 (D4-F8) · two of four
paralogue references are reviews under a caveat calling them all studies (D2-F3) · unqualified STR
"concordant" against a record that splits one locus (C2-F7) · "no third party who can decline" against
the artefact's own academic-only and MTA terms (C2-F8) · the reason given for writing off the only
purchasable line is not the reason that closes it (C2-F10) · the T-N construct's reagent cannot be
certified under §4.5's own rule (C2-F6) · two keywords that would make the released procedure findable
(D4-F6, keywords half).

---

## 5 · P3 — deferred, each with a named trigger

| finding | trigger that reopens it |
|---|---|
| **B4-F3** — the Discussion is split across three non-contiguous top-level sections, which no IMRaD template accepts | **A venue is chosen.** The merge is free in text and is the venue's call, not the author's. |
| **B4-F7** — delete four of Box 1's five blocks as conclusions asserted ahead of their evidence | ⚔ **Direct conflict with D4**, which measures Box 1 as the only home of beats 2, 3 and 4 ahead of line 825 of 1499, and warns that a journal cutting the box moves the reader's first encounter with all three behind everything withdrawal-shaped. **Recorded as a conflict, not resolved.** Trigger: a venue that cuts or relocates boxes. |
| **B4-F8** — the Introduction is 687 words against §4's 3,074 | Same trigger as B4-F3. No cut is proposed; the brief excludes length. |
| **D4-F3** — no figure carries beats 2, 3 or 4; promote the coverage ladder to a fourth main figure | Costs a new figure plus a provenance regeneration. Trigger: the figure budget at the chosen venue. |
| **D4-F6, title half** — a third title clause naming the released procedure | ⛔ **DECIDED: DECLINED, not deferred (2026-08-17).** §4.5 grades its own output *"a candidate, not a validated reagent"*, so a title clause would headline an unvalidated deliverable on a paper whose value is a well-made negative; and the title has eight homes, three of them generated views under `systems/views/` where a hand-edit fails the build. The discoverability this finding is actually about is bought by the keywords half at P2 and at no claim cost. Do not re-raise without a new argument that is not discoverability. |
| **C1-F3** — supply an actual primer/probe pair and name a platform | The paper deliberately prescribes no assay; **C3-F3's half is P1 because it is a contradiction, not a request for new work.** Trigger: a decision that the paper prescribes an assay at all. |
| **C2-F4's fix** — cite `SRR33903995` | ⚠ **The stated release date of the parent GEO series has passed, so the read is now $0 and has not been taken.** Nothing may be written about that deposit until its status is read. |
| **B6-F1, B6-F2** — the precedent-scope corrections | **A committed CI fetch** of the four PMIDs. Both were retrieved via WebSearch snippets because PMC is proxy-blocked, and this repository's rule is that a claim needs a committed fetch product. |
| **D2-U1** — whether ref 39's source carries a citation marker on the sentence the paper says it does | The full text is not open access and the proxy blocks Europe PMC. Recorded as unverified rather than guessed. |
| **B3-F4's residual** — the one manuscript quotation whose verbatim window lives on `origin/literature-cache` rather than beside the manuscript | See §6.4. A locality problem, not a provenance failure. |

---

## 6 · ⛔ WRONG LEADS — recorded so round 8 does not re-raise them

### 6.1 · D1-F1 — "the condemned sequences are in no table, and Table 7 prints a 15/16 neighbour"

**REFUTED.** Four legs, any one sufficient: the 15/16 is a one-base register shift inside a 1-nt tiling
(column-wise 4 of 16); Table 7 prints the design the artefact **passes**; the warning naming all three
condemned sequences is in the same paragraph; and the proposed fix would put RNase-H1-competent-on-
wild-type sequences onto an order form. ⛔ Do not re-raise as "the forbidden set should travel with the
ordered set".

### 6.2 · D1-F2 — "the *TAF15* response sentence drops a required caveat"

**REFUTED, residual minor.** Protected item 12's Wilson clause is in the same sentence. The pooling
artefact's "must carry the hedge in its own abstract" instruction is aimed at a different manuscript,
and **this paper's abstract makes no partner-response claim at all.**

### 6.3 · B2-F1 — "the abstract's 'another 19' implies a false total"

**REFUTED to minor clarity.** The set arithmetic is right — 13 overlap, union 93 not 106 — but **no
total is stated anywhere** in the article, SI or tables. ⭐ The refuter's replacement is sharper and is
the item to carry forward: *"pair **it** in precursor RNA"* has a nearest antecedent under which the
sentence asserts 19 rather than the true 9.

### 6.4 · B3-F4 — "a direct quotation is anchored nowhere in the repository"

**SUBSTANTIALLY REFUTED, by two other reviewers rather than by a refuter.** B3 searched the working
tree, found no committed window, and correctly recorded the charge as UNVERIFIED after both egress
routes returned blocked. **D1 and D2 independently located the verbatim string** in the cached full
text on the `origin/literature-cache` branch, which reads exactly the phrase the manuscript quotes. The
quotation is sound. What survives is a **locality** item: this paper's one quotation whose anchor lives
on a branch rather than beside the manuscript is invisible to a reviewer reading the working tree —
which is the branch-drift shape this repository already names as a data-loss risk. P3.

### 6.5 · C3-F1 — "the §4.4 estimator is undefined between a relative and an absolute reading"

**REFUTED, 3 refuters of 3, run 2026-08-16** — the verification §1.3 said had to happen before this
could be applied. Filed blocker; **P0.10's first half is closed and does not reach the deposit.**

Three independent legs, any one sufficient. **(a)** *"Half-maximal"* is the term of art for the fitted
midpoint; the absolute variant is called *absolute* IC50 precisely because the unqualified term already
means the midpoint. **(b) The limit-of-quantification clause is coherent under one reading only.** It
gates on the wild-type knockdown *amplitude* — "the change in wild-type transcript and not its
vehicle-well abundance". Under the absolute reading that clause is dead text, because an absolute IC50
only exists once the wild-type plateau exceeds 50%, orders of magnitude above any LOQ on a fractional
change; under the relative reading it is exactly the identifiability condition for the midpoint. A
clause written to guard one reading's only failure mode is evidence of which reading is meant.
**(c) Provenance closes it.** `git show 0108074dd` — the pre-fix sentence carried **two** estimators in
explicit contrast, *"a ratio of half-maximal knockdown concentrations … and otherwise of residual
transcript at a stated dose"*, and round 6 (item 6.7) deleted the amplitude-axis fallback and wrote the
exclusion clause in its place. **The charge re-imports, as a live reading of the survivor, the exact
amplitude contamination that commit was written to remove.**

⭐ **And the charge's own crux arithmetic is what refutes it.** Working the ratio gives
`S_abs = S_rel · [(E_F − 0.5)/(E_W − 0.5)]^(1/h)`, so the two readings genuinely do **not** cancel —
the reviewer was right about that. But the divergence runs entirely through knockdown *depth*: at
`m_W = m_F` with plateaus 0.90 and 0.55, the absolute reading scores a reagent of **zero potency
separation** at **8.0** and clears the cut of 5.0. That is verbatim the *"falsification as arithmetic
rather than as biology"* the paper forbids three lines earlier, so **the paper's own stated
commensurability test already excludes the absolute reading.** The second conjunct — that both readings
break *on the paper's own reagents* — is unfalsifiable as filed: nothing has been synthesised, no assay
is prescribed, and no dose–response exists.

⛔ Do not re-raise as *"the estimator must say whether it is relative or absolute"*. The residual is a
discretionary four-word gloss. **Two genuine adjacent gaps were surfaced and are carried forward:**
C1-F4 (no curve-fit model or CI-construction method) is already filed at P1; and a **new minor** — the
dose series is nowhere required to *bracket* the wild-type midpoint, so an unreached midpoint yields an
extrapolated ratio that the amplitude gate cannot catch. Logged at P2 below.

### 6.6 · C3-F2 — "the limit-of-quantification guard collapses three states into one bound"

**REFUTED, 3 refuters of 3, run 2026-08-16. P0.10's second half is closed.** ⚠ **It is a request to
reinstate a defect round 6 fixed**, and all three refuters found that independently.

`git log -S "vehicle-well abundance"` returns exactly one commit, `0108074dd`, whose body lists *"Its
limit-of-quantification guard named the wrong term"* — round-6 finding 6.6. Round 5 had gated the ratio
on **abundance**: *"reportable only where vehicle-treated wild-type *NR4A3* exceeds a pre-stated limit
of quantification"*. Round 6 established that the quantity which can approach zero is the *denominator*
— the **change** — not the abundance, because a well-expressed transcript that is perfectly spared
returns an unbounded ratio the abundance gate lets pass by default. **C3-F2's own words, "gates the
change and disclaims the abundance", are a neutral description of that correction; applying it would
restore the pass-by-default hole round 6 closed.**

The three-state conflation fails on text forty lines above the clause, which states outright that *"a
knockdown assay alone distinguishes none of them"* and then mandates a control for each: a positive-
control gapmer against a housekeeping transcript for the **failed-assay** state, and a fusion-negative
isogenic comparator for the **too-weakly-expressed** state, whose stated consequence is that the
readout is *"not defined at all"* — the paper's *void* category, not a bound. Only genuine perfect
sparing reaches the guard, where a one-sided lower bound is the arithmetically correct report and
non-falsifiability is the desired behaviour: falsifying a perfectly selective reagent would be a Type I
error against a criterion defined as a CI upper bound below the cut. The escalated framing *"emits a
failed assay as a selectivity success"* is contradicted by the clause's own closing words, *"which
cannot falsify"*, and by the fact that the paper defines **no** success endpoint at all.

⭐ **The live defect on this ground is C4-F2, already filed at P1** — the *fusion* direction is
unguarded, and C3-F2 aims at the direction that is guarded. **Residual carried forward:** round-6
finding 6.6 is **not machine-pinned**, so the round-5 abundance wording can return silently. That gate
is added in this pass.

### 6.7 · D2's own near-miss — a gap-length characterisation read as inverted

**REFUTED by the cached full text, and self-recorded before filing.** See §1.4. **The fourth instance
of this shape in the paper's review history, and the first one a reviewer caught on itself.**

### 6.8 · Prior coverage, honoured — and four reviewers re-derived rather than deferring

**No reviewer re-raised a settled item.** Four went further and re-tested rather than taking the
disposition on trust:

- **B2 reproduced the threshold sweep in full** (obs/scramble 1.05 → 45.75 across thresholds 6 → 12
  while the observed count falls) and reports the prior disposition as sound: the charge is a theorem,
  and **no dataset with a real effect could fail it**.
- **B5 re-derived nothing that disturbs the gap-length disposition** and reports Table 5's flat row as
  what the artefact holds. It also notes the 10-bp unit mismatch is **inert** for the wild-type-*NR4A3*
  class specifically, every run there being ≥11 bp.
- **B7 checked explicitly that every threshold it raises is a different parameter** from the settled one
  before writing anything up.
- **A2 re-checked the declined junction-clustered CI and found no new reason to reopen it.**

### 6.9 · Attacks tried by the hostile reviewer and abandoned, with its reasons

Recorded so the same ground is not re-walked. **De-duplicating the headline moves the number the wrong
way for the attacker**: 176 distinct molecules, 82 liable, **46.6% against 45.8%**, because the
multi-partner molecules that repeat are mostly non-liable. "Three designs survive every screen" is
unscreened at default depth, and §2.4 says so verbatim while §5 owns it. The 10-bp unit mismatch is
disclosed twice with "what relation the one criterion bears to the other is not established here", so
raising it would be re-raising a disclosed limitation. The 68.4% upper-bound caveat *is* carried in the
abstract as an interval.

---

## 7 · Checked and found CORRECT — six reviewers recorded these, and that is what stops round 8

**This section is a deliverable, not filler.** B1, B2, C3, C4, D2 and A2 each wrote out what they
tested and cleared, and D1, B3, C2, D3, A3 and A4 each did the same in part. Re-walking any of it is
wasted effort.

- **All sixteen protected items are present, quoted and positioned beside the claim each bounds** — A1,
  16 of 16, zero severances, with the abstract's computational-scope sentence checked **byte-for-byte**
  against the pre-cut baseline despite the abstract being cut from 593 to ~306 words around it.
- **Denominator and censoring bookkeeping is complete and exact** (B2): 183 records with a count, 35 at
  the cap, 101 between 15 and 50, 47 at or below; no deep screen reaches its ceiling; stored equals
  reported for all 303 deep records; 190/176/183/187/180 reconcile; the margin strata sum correctly.
- **Strand statistics, threshold sensitivity, the "62nd" design, the off-target load census and the
  coverage interval arithmetic all reproduce verbatim** (B2), including the composed Wilson endpoints.
- **The replicate and power arithmetic is right** — reproduced twice, independently, by Monte Carlo
  (C3 §V and C4's appendix): 0.6497 for the void SD, 81.3% at n = 6, 30.6/30.4% at n = 3, 2.381 for the
  single-dose ceiling. ⚠ Both note the paper is using a two-sided convention it never names, and C3
  records that its **own** earlier normal approximation was wrong and the paper was right. **Do not
  raise the power figures as inconsistent.**
- **The chemistry is sound on nine separately-checked axes** (B1): the margin/parent-duplex identity
  holds 190 of 190 at every geometry; the central negative is chemically right and B1 could not break
  it; RNase-H1 substrate requirements are correctly stated *and correctly bounded*; every enzymology
  identifier resolves to the paper the text describes; the thermodynamic cross-check is scoped exactly
  right; the LNA direction argument for ΔΔG is correct; the GC and sequence-liability audit reproduces
  design by design, with the G-quadruplex test **looser** than canonical, so that claim is conservative.
- **Citation semantics are unusually strong** (D2): 52 of 52 PMIDs matched to a retrieved record, 41
  verified against a read abstract or cached full text, ten full texts read end to end. **No claim
  stronger than its source, no source cited for a number it does not contain, no review cited as
  primary.** Every priority class — response rates and their denominators, partner prevalence,
  breakpoint distribution, the gap-length basis, the duplex-length threshold, the junction-targeting
  precedents — clean, including the *TAF15*-arm claim D2 flagged as most likely to fail.
- **Clinical numbers reproduce independently** (B3, D1): the pazopanib and anthracycline denominators,
  the 46/9/2/1 of 58 partner split, type 1 in 10 of 15, *TAF15* exon 6 in 3 of 3, and the coverage
  envelope recomputed from the repository's own Wilson implementation. **No fabricated or misattributed
  identifier found by any of the three reviewers who looked.**
- **The generators reproduce their committed output** (D3): `submission_tables.py` → zero diff;
  `submission_citations.py --check` current; `aso_figure_provenance.py --check` exit 0;
  `lint_consistency.py` 0 ERROR; `lint_citations.py` exit 0 with all 81 unanchored identifiers already
  baselined and none new. **The drift D3 found is entirely in the deposit apparatus and the registry,
  not in the manuscript body.**
- **Every cross-reference, display item and citation number resolves** (A4): ~90 pointers checked
  against the destination *content* and not merely the number; every table, figure and box cited from
  body text; first-citation order contiguous 1 → 52; the historical off-by-seventeen SI bug not
  reproduced; an automated Hamming-distance-1 sweep over all 68 oligonucleotide sequences returning two
  flagged pairs, both of them distinct designs at different junctions rather than typos.
- **Every relocation A3 and A2 chased landed where the text says it lands** — twelve destinations
  quoted before being cleared, and several bounds were **added** by the pass rather than lost.
- **The 5-6-5 / 5-8-5 / 5-10-5 comparison is like-for-like on depth** (A2, with the artefact's own
  `depth_evidence` field). **The 41-vs-43 curated-record pair is two different classes, not a
  contradiction.**
- **The construct route's specification, the paper's honesty about what that route loses, the "no
  problematic-line flag" statement, the two fusion calls, and the fusion-negative-EMC framing all check
  out** (C2), and C2 records the construct-route passage as "the paper at its best".
- **The core readout is designable** (C3): reconstructing both lead junctions from the manuscript's own
  stated exon ends shows a fusion-specific assay needs no junction-spanning oligonucleotide at all.
  **The measurement can be made.** Everything C3 files is about what the number means, not whether it
  can be obtained.
- **The desk decision is SEND FOR REVIEW** (B4), with novelty conceded rather than claimed, the negative
  framed as a finding rather than a failure, the unfavourable readings volunteered, and the declarations
  called exemplary. **The only thing holding back an unqualified send is P0.5, a housekeeping return.**

---

## 8 · What this review did not do

- **Nothing was applied.** No manuscript, SI, table, generator or artefact was edited for this round.
  This file is the ledger; application is a separate pass behind the human decision gate, because the
  deposit is outward-facing.
- **No screen was re-run to change an artefact.** Where a reviewer recomputed — the null's single-side
  arms, the power Monte Carlo, the CpG positions, the ΔΔG discordance, the terminal-base census — it was
  to test a claim, and the result is reported here rather than committed. This ledger re-derived B5-F1's
  two load-bearing counts a fourth time before recording them, and no other finding's arithmetic.
- **Only four charges were verified**, all at the top of the severity scale. **130 of the 134 findings
  carry a reviewer's evidence and no refuter's.** ⚠ **Two filed blockers were not verified at all**
  (§1.3), which is a gap in this round rather than a property of those findings.
- **Two reviewers could not reach the literature.** Europe PMC and PMC are blocked at the egress proxy;
  D2 worked entirely from the `origin/literature-cache` branch and B6 from search snippets, which is why
  B6's two precedent findings sit at P3 behind a committed fetch.
- **The paper's length was never a finding**, by brief. B4's three structural findings are about
  distribution and section order; none proposes a target length.
- **No reviewer was told the editorial plan's rationale.** Family B saw the paper and nothing else — no
  diff, no mention that a cut had happened — which is what makes their verdicts usable as evidence that
  the cut did not damage the paper.
- **The confound the pre-registration named has not gone away**: round 7 used the same method, model
  family and lenses as rounds 5 and 6, so it is systematically blind in the same places. A quiet result
  on an axis these reviewers share is weak evidence about the paper and strong evidence only about what
  this method can see.
