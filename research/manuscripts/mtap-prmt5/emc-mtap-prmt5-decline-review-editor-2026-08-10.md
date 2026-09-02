---
id: DOC-EMC-MTAP-PRMT5-DECLINE-EDITOR
title: "Grounds to decline — editorial and fit lens (emc-mtap-prmt5-hypothesis.md)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: An adversarial editorial assessment hunting every ground on which the PRMT5 manuscript would be declined.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Grounds to decline — editorial and fit lens

> **THIS IS A SIMULATED INTERNAL REVIEW, WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S REQUEST. IT IS NOT
> CORRESPONDENCE FROM *GENES, CHROMOSOMES AND CANCER*, NOT A REAL EDITORIAL DECISION, AND NOT A
> REJECTION BY ANY JOURNAL. No editor, no journal and no external referee has seen this manuscript.
> Its purpose is adversarial: to find every ground on which the paper would be declined, before a
> real editor finds them.**

Manuscript under review: `research/manuscripts/emc-mtap-prmt5-hypothesis.md`
Also read: the SI, the cover letter, the pre-posting checklist, the five figures at full resolution,
the figure-generating code, the round-one simulated review and its response, and the committed
artifacts behind the load-bearing numbers.

**Lens.** Editorial triage and fit: would this be desk-rejected, on what ground, is it the right
article type, does it deliver its title, is it presentable, and what does the author's own package do
to its chances. Statistics and biology are another reviewer's job and I have not re-litigated them —
where I touch a number it is because a *document* disagrees with another document, not because I
think the number is wrong. Round one traced the numbers and found them to reproduce; I take that as
read.

---

## Verdict

**Desk reject.** Realistic outcome at *Genes, Chromosomes and Cancer*: returned by the handling editor
without external review, with an invitation to resubmit as a short-format or hypothesis-type article
elsewhere. The single strongest ground is **insufficient advance for a Research Article**: the paper
generates no new data, and after the correction the authors themselves ran and reported, it retains no
positive finding — what remains is a hypothesis transferred from two other diseases plus one negative,
which is not a Research Article's worth of claim.

The paper is honest, careful and better documented than most of what crosses an editor's desk. None of
that is the question the desk asks. The desk asks what the field gains, and the answer here is one
negative in sixteen archival tumours.

**Count: 10 fixable grounds, 3 structural.**

---

## GROUNDS TO DECLINE

### 1. Insufficient advance for a Research Article — no new data, and after the paper's own correction, no positive result — **STRUCTURAL**

*Sections: 3.5, 3.6, 3.3, 4.1, 5.*

Lay the Results end to end as an editor does:

- §3.5. The primary contrast is a *t* of 6.24 and 6.67 on two archival platforms, at a family-wise
  adjusted *p* of 0.21 and 0.24. The paper states, correctly and in the abstract, that this does not
  clear conventional thresholds on either platform. The only reading in the paper that falls below
  0.05 after correction is an instrument control.
- §3.6. The same contrast loses most of its magnitude to a proliferation adjustment on one of the two
  platforms (6.67 to 2.71), and the pre-specified cellularity control moves on that same platform. The
  paper says the platforms disagree and that nothing available decides between them.
- §3.3. The nominated target is a dependency in 94.5% of screened sarcoma lines and 94.1% of
  non-sarcoma lines, a selectivity of 0.013. The panel contains no EMC line at all.
- §3.7. The genuinely new computation is an exact string scan for a three-residue motif in committed
  public protein sequences, and the paper correctly refuses to read it as a response predictor,
  because the one disease where the mechanism was actually measured retains zero sites.
- §3.2. The *MTAP* rationale is closed. This is real and it is the paper's only clean deliverable.

So the article's positive content is: *a target class that has not been looked at in this disease
might be worth looking at, on evidence that does not survive its own correction, in a disease with no
cell line to test it in.* That is a hypothesis. The negative is a genuine contribution and the field
does under-publish negatives — but a single negative in sixteen archival tumours, on a locus the paper
then says transcript could never have measured anyway (§4.1: "protein loss is what the window selects
on in any case, so a transcript could not have seen it"), is a short-format finding.

**Why structural.** No revision produces a positive result from this data, and the paper is already at
the honest end of what the data supports — the round-one revision moved it there and should not be
moved back. The only route through is a change of article type and a change of lead (grounds 2 and 4),
which converts this from a decline to a smaller, defensible paper. It is survivable in that form and
not in this one.

---

### 2. Research Article is the wrong article type, and the paper's own reason for choosing it does not survive inspection — **FIXABLE**

*Sections: article type; figures 1–3; `emc-mtap-prmt5-prepost.md` → "ARTICLE TYPE".*

The pre-posting checklist records the decision verbatim:

> **ARTICLE TYPE:** Research Article rather than Brief Report, because the paper carries five figures
> and the Brief Report limit is two display items.

Three things are wrong with that.

**(a) The article type was chosen to fit the figure count.** That is backwards. Content selects type;
type then constrains display items. The paper's own front matter calls it "A hypothesis-generating
re-analysis of public data", its frontmatter scope says "This document raises a hypothesis and names
its falsifiers. It reports no experiment in EMC cells, no drug exposure and no patient", and §4.1
describes both surviving supports as "arguments about plausibility; neither is an observation in EMC".
A manuscript that says four separate times that it is a hypothesis is a Hypothesis or Brief Report.

**(b) Figure 2 contains no datum that is not already in Figure 1.** This is not a judgement call; it
is verifiable in the figure code. `research/modalities/emc_mtap_prmt5_figures.py`:

- `fig_readings` (figure 1) builds a 2×2 grid and calls
  `_gene_panel(axes[r][1], panel, LOCUS, ..., plat, kind)` for both platforms — that is the
  right-hand column.
- `fig_locus_genewise` (figure 2) builds a 1×2 grid and calls `_gene_panel(axes[c], panel, LOCUS,
  ..., plat, kind)` for the same two platforms.

Same function, same gene set, same panel object, same two platforms. Rendered side by side the two are
identical point-for-point: on GPL6244, *MTAP* comparator median ≈ 0.57 against EMC ≈ 0.55, *CDKN2A*
≈ 0.55 against ≈ 0.15, *CDKN2B* ≈ 0.35 against ≈ 0.26; on GPL3290, *MTAP* ≈ −0.72 against ≈ −1.10,
*CDKN2A* ≈ 0.30 against ≈ 0.48, *CDKN2B* marked unreadable. Only the title and the footnote differ.
Figure 2 is figure 1's right column with a different caption.

**(c) Figure 3 is three numbers.** It carries three percentages and three means on a horizontal bar
chart whose x-axis runs to 120% on a percentage scale. It is a table.

Delete the duplicate and demote the bar chart and the paper has three figures, which is within a short
format on any reading. The stated reason for Research Article then evaporates.

**And the display-item count the decision rests on is itself wrong.** `submission_metrics.py` reports
`items= 5` and "within believed limits". Counting the main text, the paper carries **five figures and
eight tables** — §2.1 (series), §3.2 (locus), §3.5 (two), §3.6 (controls), §3.7 (fusions), §4.3
(falsifiers F1–F10), §8 (data availability) — that is **13 display items**, before Appendix A's
nineteen-row table. The gate counts figures only. An editor counts tables.

---

### 3. Concurrent, overlapping submissions to the same journal on the same sixteen tumours, undisclosed in the cover letter — **STRUCTURAL**

*Cover letter, paragraph 7; `nr4a3-fusion-transcriptional-output.md`; `emc-atr-collaborator-package.md`.*

This is the ground most likely to end the matter, and it is the one only someone with the whole folder
can see. An editor sees it too, because the submissions arrive in the same week from the same name.

`research/manuscripts/nr4a3-fusion-transcriptional-output.md`, dated 2026-08-10, same sole author,
same simulated-review-and-response cycle, states in its own header:

> Primary target : Genes, Chromosomes & Cancer (Wiley) — Original Research Article (subscription/$0 route)

It reads **the same two GEO series** (GSE24369 and GSE4303 appear fourteen times in it) through **the
same committed artifact** (`emc-expression-panels.json`) and **the same analysis pipeline**, and its
`canonical_for` block claims, among others, "the confound audit of the EMC expression contrast —
comparator composition, muscle admixture, reference pool and matrix content" — the same reference-pool
confound this manuscript audits in §2.1 and SI §S5a. `submission_metrics.py` scores it as
`GCC-Research-Article`, 9,015 words, 47 references. `emc-atr-collaborator-package.md` is likewise
scored `GCC-Research-Article`, and `research/literature/ai-disclosure-policies-2026-08-10.json` lists
exactly two manuscripts under "Wiley (Genes, Chromosomes and Cancer)": this one and the ATR package.

The cover letter says:

> The work is original, has not been published, and is not under consideration elsewhere.

That sentence is true as written and it is not the disclosure the situation requires. What an editor
needs to know is that a second and third Research Article, from the same author, are being prepared or
submitted to the same journal, and that one of them re-analyses the identical sixteen tumours from the
identical two deposits with the identical code on a different four-gene panel. That is the textbook
shape of least-publishable-unit division, and COPE-aligned publishers ask about related manuscripts
precisely to catch it.

**Why structural.** Disclosure is a one-paragraph fix and must be made. The underlying problem is not:
if one re-analysis of two archival series yields three Research Articles, the honest answer is that it
yields one, and the editor will say so. The survivable form is a single paper on the EMC expression
record that reports every panel read against it, with the PRMT5 and fusion-target readings as sections
rather than as separate articles. That is a better paper than any of the three and it is achievable
with no new data.

---

### 4. The title names a unit the Results disqualify, and the paper leads with the wrong clause — **FIXABLE**

*Title; abstract; §3.4; §4.1; §5; cover letter paragraph 3.*

The title is "**The PRMT5 methylosome** in extraskeletal myxoid chondrosarcoma: a fusion-class
rationale that survives and an MTAP-locus rationale that does not".

§3.4 and figure 4 report that pooled across the four methylosome genes, EMC ranks third of the five
tumour classes, below desmoid fibromatosis and solitary fibrous tumour, "so the group does not
separate this disease". §4.1 restates the surviving rationale "on *PRMT5* rather than on the
methylosome group", and adds that "the other three members are flat or lower in EMC and dilute it".
Appendix A registers the change of unit as a correction.

So the title's grammatical subject is a four-gene group the paper's own Results retract as a unit of
evidence, and the abstract keeps it as its subject too ("We tested two independent rationales… No
indexed study examines the PRMT5 methylosome in this histology"). A reader arriving on the title
expecting a methylosome finding gets a single-gene finding on one member and an explicit statement
that the group does not separate the disease.

**The second inversion is worse and the author already knows it.** The cover letter says:

> The result that a reader is most likely to use is a negative: an MTAP-directed rationale that reads
> plausibly from the general oncology literature does not hold in this disease at transcript level,
> and the manuscript says which single stain would close the question.

That is correct, and the title, the abstract's opening, §4.1's ordering and §5's ordering all lead
with the survivor instead. The cover letter and the paper disagree about what the paper is for. Lead
with the negative — it is clean, it is checkable, it is the thing that changes someone's decision, and
it is the only claim in the paper that the multiplicity correction strengthens rather than weakens
(§3.2: adjusted *p* of 1.00 on both platforms).

---

### 5. §4.4 contradicts §4.1 and itself about the one thing the paper says survives correction — **FIXABLE**

*§4.1 and §4.4.*

§4.1, on what is left after the correction:

> What survives correction is the replication, which no single-platform correction addresses: two
> independently collected series, on different technologies with different comparator arms, both put
> *PRMT5* first of the readable PRMT family and both put the contrast in the same direction.

§4.4, fifteen lines into the Limitations section that immediately follows:

> The evidence base is sixteen tumours on two decade-old array platforms. **Two series are not a
> replication set**, and the locus result rests on six tumours from one of them.

And then §4.4 again, twenty lines later:

> And a correction on one platform does not see **the replication across two**, which is the part of
> the evidence that a single-platform procedure cannot express.

The paper's one surviving positive claim is "the replication". One section denies that a replication
set exists. The denial and the reliance are in the same section. A referee will quote these three
sentences in that order and nothing else.

Two further things a reader cannot check and the paper does not address. Neither series is reported
as checked for **patient overlap** with the other, anywhere in the manuscript or the SI — "two
independently collected series" is asserted, not shown. And §2.1 states that "Neither GEO record links
a publication", with GSE4303 attributed to [12] on the strength of a deposited summary and **GSE24369
attributed to nothing at all**. GSE24369 is the 35-sample platform on which the surviving contrast
survives its proliferation control. The paper's one positive result therefore rests on a deposit with
no primary description in the literature, cross-checked against a second deposit that has not been
shown to contain different patients.

Fix: delete the replication claim, or restate it as directional concordance between two deposits and
say plainly that overlap could not be excluded and that the larger series carries no linked
publication.

---

### 6. The Data Availability statement is unresolvable, and the Introduction's novelty claim rests on unpublished internal documents — **FIXABLE**

*§2.6, §8, §1.1, §1.3.*

§2.6: "Every figure, table and number is regenerable from public data by scripts in **the accompanying
repository**". §8 then gives a thirteen-row table of relative filesystem paths —
`../modalities/emc-expression-panels.json`, `../literature/emc-prior-art-2026-08-09.json`, and so on.

**The repository is never named anywhere in the manuscript.** There is no URL, no DOI, no archived
release, no accession. I checked: the strings `github`, `zenodo` and `http` do not occur in the file.
A reader who accepts the paper's invitation to check a number has nowhere to go. For a journal that
requires a data availability statement, a statement whose objects cannot be located is a returnable
defect on its own, and it is unusually damaging here because the paper's whole rhetorical strategy is
"every number traces to an artifact".

The same gap undermines the originality claim, which is the paper's reason for existing:

- §1.1: "The modality census described in section 1.3 counts eight systemic classes in clinical use
  for this disease" — cited to `cancer-modality-census.md`, an unpublished internal markdown file.
- §1.3: "A modality census … enumerated 217 categories of cancer treatment"; "A corpus of 591
  open-access full texts retrieved for this work contains no *MTAP*, *PRMT5* or *MAT2A* datum for
  this histology"; "A separate Europe PMC prior-art screen of 322 records, 238 of them with full
  text".

None of those four is a citable source. All are internal artifacts in an unnamed repository. The
abstract's flat assertion "No indexed study examines the PRMT5 methylosome in this histology" is
therefore unverifiable by the editor, by a referee, and by a reader. That is not a small thing for a
paper whose contribution is that nobody has asked the question.

Fixable at zero cost: name the public repository, mint an archived release identifier for the state
the paper is built on, and either deposit the census and the two screens as supplementary files or
label their claims explicitly as the author's own unpublished analyses.

One related seam, stated for completeness because it bears on the novelty claim's strength rather than
its verifiability. The 591-text corpus was retrieved on a target-side query — per
`research/literature/mtap-prmt5-emc-citations.json`, `(MTAP OR "methylthioadenosine phosphorylase")
AND (PRMT5 OR MAT2A OR "synthetic lethal" OR "synthetic lethality")` — so a report of PRMT5 in this
histology that never mentions MTAP or synthetic lethality would not be in it. The disease-side screen
that would catch such a paper is the 322-record one, and §1.3 states that it "matched titles and
abstracts rather than full text". So neither screen is a full-text, disease-to-target search, and the
paper does not say so. It says the weaker thing about each screen separately. This is a wording fix,
not a defect of the work.

---

### 7. Repository maintenance apparatus is inside the submission text — **FIXABLE**

*Frontmatter; Appendix A; SI Appendix S1.*

Round one deleted an editorial HTML comment from the manuscript (m15) on the reasoning that it "is
invisible in rendered Markdown and visible in a converted `.docx` or `.pdf`". The same reasoning
applies to material that is still there and was not touched.

- **Manuscript line 831 and SI line 405 cite the repository's agent-instruction file by name and
  relative path**: "Per [CLAUDE.md](../../../CLAUDE.md) rule 1.2, a corrected value is registered rather
  than dropped". A journal Research Article that cites its own repository's maintenance rules as the
  authority for one of its appendices is not a submission-ready document, and it appears twice across
  the two files.
- **Appendix A names "the pre-posting checklist" twice** as the place a claim lives (rows 1 and 14).
- **The 23-line YAML frontmatter sits above the title** with `canonical_for: ["the 2026-08-09 EMC
  PRMT5/MTAP reading and its hypothesis"]` and `audience: [maintainers, external reviewers,
  autonomous research agents, collaborators]`, and **nothing in the file says it is stripped at
  submission**. The sibling GCC-targeted manuscript in the same directory carries exactly such a note
  in a repository-note block; this one had its comment block deleted and nothing put in its place, so
  the safeguard was removed along with the hazard.
- **Appendix A's final row** describes the manuscript's own conversion from repository memo to journal
  article ("The register was correct for a maintainer and wrong for a journal reader"). That row is
  about the file's editorial history, not about the science, and is meaningless to a journal reader.

Every item here is deletable in one pass and none affects a result. But an editor reads the first page
and the last page, and both currently carry repository furniture.

---

### 8. Figures: one duplicate, one false caption, one mislabelled axis, two greyscale failures on load-bearing elements — **FIXABLE**

*Figures 1–5 and their captions.*

**(a) Figure 2 duplicates figure 1's right column.** Evidenced under ground 2.

**(b) Figure 1's caption is false.** It reads "**Every tumour** on both platforms." It is not every
tumour. §2.1 states that GSE24369 deposits 42 samples and 35 were analysed, of which five solitary
fibrous tumours are tumours that the classifier dropped. Figure 1 draws the panel's arms only; the five
appear for the first time in figure 4. So the caption asserts completeness in exactly the place the
round-one revision added an incompleteness disclosure. Fix: "Every tumour in the analysed arms".

**(c) Figure 4's axis labels report gene-by-sample counts as *n*.** The label string is built at
`emc_mtap_prmt5_figures.py` line 288 as `f"{CLASS_LABEL.get(k, k)} (n={len(rows[k])})"`, and in the
left panel `rows[k]` holds four genes × the class's samples. The rendered axis therefore reads "EMC
(n=24)" for six tumours, "LGFMS (n=68)" for seventeen, "desmoid fibromatosis (n=24)" for six. In a
paper whose entire evidence base is sixteen tumours, a figure axis that appears to show n=24 in one
arm is the single most misreadable object in the package. The caption's closing sentence discloses the
pooling ("Left-panel points are gene-by-sample values pooled across four genes, so they are not
independent observations and no test is run on them") but never says the *n* is not a tumour count.
Fix: label the left panel `6 tumours × 4 genes` or drop the *n* from it.

**(d) Two greyscale failures, both on the element that carries the qualifier.** Figures 1, 2 and 4's
right panel are greyscale-safe, because EMC is a filled circle and comparators are open squares —
shape carries the distinction. Two are not:

- **Figure 4, left panel.** Pooled normal muscle is drawn in mustard **open squares**; the comparator
  tumour classes are drawn in slate **open squares**. Same marker, colour only. In greyscale the
  normal-tissue column becomes indistinguishable from the tumour comparators — and normal muscle is
  the class the paper says reads *above* EMC on *PRMT5* (+1.34 against +1.30), which §3.4 calls "the
  plainest available statement of what this measurement does not show". The qualifier the paper is
  proudest of is the one that disappears in print.
- **Figure 5.** EMC fusions are drawn as red bars, comparator fusions as slate bars, and the GRG sites
  as red ticks on both. In greyscale the EMC/comparator distinction collapses, and on the EMC rows the
  red ticks on red bars are already low-contrast in colour and vanish entirely without it. The tick
  positions on EWSR1::NR4A3 type 1 and type 5 are the entire content of §3.7.

**(e) Figure 3's title overstates against the paper's own text.** The title reads "PRMT5 and MAT2A are
pan-essential across sarcoma lines", while §3.3 uses MAT2A's selectivity of −0.285 as the contrast
that makes PRMT5's +0.013 look like nothing. If MAT2A is pan-essential in the same sense, the contrast
in §3.3 has no force. Also the x-axis runs to 120% on a percentage scale.

**(f) Table/figure ordering mismatch in §3.7.** The table lists the fusions in the order type 1, type
5, type 2, TAF15, ATF1 e8, ATF1 e10, ATF1 e7, FLI1; figure 5 plots them type 1, type 2, type 5, FLI1,
ATF1 e8, ATF1 e7, ATF1 e10. A reader checking one against the other has to re-sort. And §3.7's table
column headed "fraction of EWSR1's 11" carries the cell "0.000, of TAF15's 9" — a different
denominator inside a column whose header names one.

---

### 9. The abstract asserts flatly what the body qualifies, and sits two words under a limit nobody has verified — **FIXABLE**

*Abstract; §1.3; `emc-mtap-prmt5-prepost.md` → "STILL NOT VERIFIED".*

The abstract's third sentence: "**No indexed study examines the PRMT5 methylosome in this histology.**"

§1.3, on the screen that sentence comes from: "The screen matched titles and abstracts rather than
full text, so an absence in it means that nothing is indexed on a pairing and not that no such work
exists; a result inside a supplementary table of a larger paper would be invisible to it."

The body is careful and the abstract is not, and the abstract is what the desk reads. One qualifier
fixes it.

**On length.** `submission_metrics.py` reports the abstract at 248 words and flags nothing. The
pre-posting checklist records why that reassurance is thin:

> ⚠ **STILL NOT VERIFIED:** the per-journal author-guideline pages return 403 from CI as well, so the
> word, abstract and display-item limits the manuscript is written to remain search-derived.

So the abstract is two words inside a limit that has never been read from the journal, and the
article-type decision of ground 2 rests on a Brief Report display-item limit from the same unverified
source. Both are cheap to settle before submitting and neither has been.

---

### 10. §4.2 promises two experiments and describes three; the abstract promises two and names a different two — **FIXABLE**

*§4.2 heading and body; abstract, final sentence; §4.3 F10.*

The heading is "### 4.2 **Two** decisive experiments". The body has three:

1. line 617 — "For the fusion rationale, a PRMT5 inhibitor in a patient-derived EMC model."
2. line 627 — "For the mechanism behind that rationale, two constructs in one experiment."
3. line 636 — "For the *MTAP* rationale, MTAP immunohistochemistry on archival EMC tissue."

The abstract's closing sentence names only the first and third: "Two inexpensive experiments would
settle each: MTAP immunohistochemistry on archival tissue, and one clinical-stage PRMT5 inhibitor
added to a screen already running on published EMC models." The two-construct experiment — which §4.2
calls the one that separates the mechanisms, and which F10 calls the thing that "would settle it in EMC
directly" — is absent from the abstract entirely.

This is revision damage: round one's m12 deleted §4.2's outcome table and folded its branches into
F2/F6/F10, and the heading's count was not re-checked afterwards. Fix the heading to "Three decisive
experiments" and add the third to the abstract, or drop it from §4.2.

---

### 11. Eighteen references, with four structural gaps and two malformed entries — **FIXABLE**

*§9.*

Eighteen is thin for a paper that positions itself against a synthetic-lethality literature, a
fusion-biology literature and a methylosome literature. Thin is survivable; the specific gaps are not,
because each sits under a load-bearing claim. Every gap below is checkable by reading the list, and I
name no work the repository does not already hold.

**Gaps.**

1. **No primary report of the *MTAP*-deletion/PRMT5 synthetic lethality itself.** The second rationale
   — half the paper, half the title — is supported by [4], an MTA-cooperative inhibitor paper, and [5],
   a genomic-landscape paper on a different disease. The discovery literature that established the
   lethality is absent. An editor at a cancer-genetics journal will notice within seconds.
2. **No primary description of the EWSR1::NR4A3 fusion.** The disease-defining event is cited to
   nothing. The breakpoints in §2.5 and figure 5 come from two reviews [13], [14], one primary paper
   [15], and [16].
3. **No method citation for the dependency score.** §3.3's entire instrument — the Chronos gene-effect
   scale and the −0.5 dependency threshold — is uncited; §2.2 and §8 identify the release by figshare
   article number only. The round-one response declines this explicitly for want of a committed record.
   That is a defensible internal rule and it is not an answer an editor accepts.
4. **No publication for GSE24369.** §2.1 says so. As noted under ground 5, that is the series carrying
   the paper's one surviving result.

**Malformed entries.**

- **[7]** carries journal and year but **no volume, issue or pages**. It is the paper's only prior-art
  hit and is discussed for a full paragraph in §1.3.
- **[16]** is "*Biology*. *Sarcoma* 2001;5(S1):S37-43", **with no authors**, annotated in the reference
  itself as "A conference abstract collection; the retrieval record carries no author list for it." A
  reference whose title is the single word "Biology" and whose author field is empty, cited as one of
  four sources for the fusion breakpoints that produce figure 5 and an abstract claim, is the kind of
  entry that turns an editorial scan into an integrity question. Either source that junction elsewhere
  or drop the junction.
- **[2] and [16]** carry multi-clause editorial annotations inside the reference entry. Reference
  entries are bibliographic; the caveats belong in Methods, where §2.5 and §4.4 already carry them.

---

### 12. The Declarations do not answer the third element of the publisher's AI requirement — **FIXABLE**

*§6; §2.6.*

The publisher's own wording is committed at source in
`research/literature/ai-disclosure-policies-2026-08-10.json`, retrieved 2026-08-10 with HTTP 200:

> Authors should document all AI Technology used, including its **purpose**, whether it **influenced
> key arguments or conclusions**, and **how they personally reviewed and verified** any AI-generated
> content.

Against those three:

- **Purpose** — answered, well. §2.6 names the tool, the mode of use and the scope.
- **Influence on conclusions** — answered, unusually well. §2.6 records that two corrections "were
  found during figure preparation, after the prose had been written the other way".
- **How the author personally reviewed and verified** — **not answered.** Every verification sentence
  in §2.6 is agentless passive: "Every statistic, percentile, count and dependency figure reported
  here was checked against the committed artifact that owns it"; "Every bibliographic identifier below
  was taken from a retrieval record and is checked against a tracked artifact by an automated linter".
  Both describe machine reconciliation. Neither says what the human did. The repository's own artifact
  records this element as having been "added"; the sentence that was added does not name the author as
  the verifier.

This is one sentence to fix and it should be fixed, because it is the element a publisher's integrity
screen actually checks. Separately, §6's entry reads "**Generative AI.** Section 2.6." — a
cross-reference where a declaration is expected. The publisher prescribes no location, so this is
style rather than breach, but a declarations block that points elsewhere reads as evasive on exactly
the topic where it must not.

Declarations otherwise complete and correctly worded: competing interests, funding, ethics, author
contributions all present and unambiguous. No acknowledgements section; not required.

---

### 13. Author-side risk factors — **STRUCTURAL, and none of them disqualifying**

*Title block; cover letter.*

Asked to price these honestly, individually:

| factor | what it actually costs |
|---|---|
| Sole author, unaffiliated, no institutional address | Little at a Wiley title. It is not a screening criterion. It raises the probability of a routine identity check and it removes the reviewer-suggestion goodwill an affiliated author gets. Cost: small and real. |
| Gmail correspondence address | Marginal on its own. In combination with the row above it is what triggers the check rather than causing the decline. |
| No funding | Neutral to positive. Nobody declines a paper for having no grant. |
| No ORCID | The one that can physically block a submission, because many Wiley journals require ORCID for the corresponding author at the portal. Costs nothing to fix and is not fixed. The pre-posting checklist correctly identifies it as the single item only the author can supply. |
| Declared AI assistance | Costs credibility with some editors and is nonetheless mandatory. Concealing it would be far worse and would be an integrity matter. Declare it, and fix ground 12 so the declaration is complete rather than partial. |
| No new data | Priced under ground 1. This is the expensive one, not any of the above. |

**None is disqualifying and none should be softened.** What costs is the *combination* — a sole
unaffiliated author, no ORCID, no funding, declared substantial AI assistance in the analysis, no new
experiment, and (ground 3) two further Research Articles from the same author on the same sixteen
tumours arriving at the same journal. Any one of those is unremarkable. Together they form the profile
an editorial office screens for, and they will be read together.

**Why structural.** The author is who they are, and the honest disclosures must stay. The only lever is
to make the science large enough that the profile stops mattering, which points back to ground 3's
consolidated single paper.

---

## Claims in the round-one response that I checked and found overstated

I traced every "accepted and fixed" in `emc-mtap-prmt5-hypothesis-review-response-2026-08-10.md` to
the section it names. Most check out exactly — M1's Methods counts, M2's abstract wording, M3's
reference-channel disclosure in §2.1 and SI §S5a, M4's annotated *NR4A3* row, M6's three clear cell
junctions in both table and figure, M7(b)'s *MKI67* control in §3.6 and SI §S5, M7(c)'s deleted
control-block sentence, m3, m5, m10, m13, m14 and m15 are all as described, and the gate table
reproduces (I re-ran `lint_consistency.py`, `lint_style.py`, `systems_check.py --check` and
`emc_systems_map_check.py --check`; all 0 ERROR). Three claims do not hold.

### R1. M5's ranking correction reached the main text and the figure but not the SI, which now contradicts itself

Response M5, point 2:

> The ranking claim in §3.4 therefore becomes "third of the five tumour classes, below desmoid
> fibromatosis and solitary fibrous tumour", not a change of leader.

True of §3.4 and of figure 4's caption. **Not true of the SI.** `emc-mtap-prmt5-hypothesis-SI.md` §S4,
live running text, unchanged:

> For the methylosome, the group score hid a signal its decisive gene (PRMT5) does have, **since pooled
> across four genes EMC ranks second of four comparator classes** while PRMT5 alone is highest.

That is the retracted claim, verbatim, in the supplement. And SI §S6's table, in the same file, says
"pooled, EMC is third of five tumour classes". The SI now contradicts itself on the ranking, and the
correction registered in SI Appendix S1 is scoped to §S6 alone, so the register does not record that
§S4 was missed. A referee who reads the SI reads both sentences.

### R2. The pre-posting checklist is listed among "Files changed" and still carries four superseded values, three of them under "must survive to the posted version"

Response header: "Files changed: … `emc-mtap-prmt5-prepost.md` …".

`emc-mtap-prmt5-prepost.md`, under the heading **"⚠ Honest statements that must survive to the posted
version"**:

> *MTAP* is flat where the read is powered (**−0.02 SD**); the entire locus signal is *CDKN2A*
> (**−0.40 SD**), which reverses on the second platform (**+0.17**).

Manuscript Appendix A registers all three as superseded — "*MTAP* −0.023 / −0.389; *CDKN2A* −0.399 /
+0.173; *CDKN2B* −0.096" corrected to "+0.053 / −0.607; −0.481 / +0.175; −0.136" — and says of the
first that "The −0.023 appears in no committed artifact, so it entered the prose from a source the
repository cannot show."

Two lines below, the same checklist:

> ⚠ **The methylosome GROUP does not separate this disease** — pooled, EMC ranks **second of four
> comparator classes**.

That is R1's retracted ranking again, in a third file.

And four bullets down:

> ⚠ **§3.4's motif analysis** must not be presented as a response predictor … The commonest EMC fusion
> and the commonest clear cell fusion retain **the same four PRMT5-motif sites**

The motif analysis is §3.7, not §3.4; and Appendix A registers the single-junction statement as
narrowed to "two of the three reported clear cell junctions retain four sites and one retains none".

The document that exists to protect the manuscript's honest statements through a formatting pass is
now instructing that pass to preserve four values the manuscript has formally retracted, one of which
its own appendix says has no source anywhere in the repository. That is the exact failure mode the
appendix mechanism was built to prevent, one file downstream of where it was checked.

### R3. M8's "each from a committed retrieval record with full bibliographic metadata" is contradicted by the manuscript's own reference [16]

Response M8:

> Added, **each from a committed retrieval record with full bibliographic metadata**: GSE4303's source
> publication [12]; the four sourced records behind the *NR4A3*-fusion breakpoints [13–16] …

Reference [16], as printed in §9:

> 16. Biology. *Sarcoma* 2001;5(S1):S37-43. [three identifiers, elided here] **A conference abstract
> collection; the retrieval record carries no author list for it.**

"Full bibliographic metadata" and "the retrieval record carries no author list for it" cannot both be
true of the same entry, and the second is the manuscript's own words. The identifiers anchor; the
metadata is not full. Reference [7] in the same list carries no volume, issue or pages.

This is a small overstatement and I record it because of what it is attached to: [16] is one of four
sources for the fusion breakpoints that produce figure 5, §3.7's table and a sentence of the abstract.

---

## What would change my recommendation

Nothing in the fix list changes ground 1, and ground 1 is the decision. What the fix list changes is
what the paper becomes: with grounds 2, 4 and 5 addressed the same evidence supports a short, clean,
publishable article whose claim is the negative, whose title says so, and whose two supporting
arguments are stated as the transfers they are. With ground 3 addressed by consolidation rather than
by disclosure alone, it supports something larger. Both are better outcomes than the present draft
receiving a desk reject and taking two sibling manuscripts down with it.

---

## Fix list

Ordered. Only the FIXABLE grounds appear here; grounds 1, 3 and 13 are not on it because revision
does not close them.

1. **Change the article type.** `emc-mtap-prmt5-prepost.md` → "ARTICLE TYPE", and the cover letter's
   first sentence. Submit as a Brief Report / short-format or Hypothesis article, not a Research
   Article, and record the reason as the content (a hypothesis-generating re-analysis with no new
   data), never as the figure count. [Ground 2]
2. **Delete figure 2.** `research/modalities/emc_mtap_prmt5_figures.py` → remove
   `fig_locus_genewise` from the build map; manuscript §3.2 → drop the figure call and fold its
   caption's one substantive sentence (CDKN2A loss can leave MTAP intact, so a locus score cannot
   separate them) into the §3.2 text. Re-stamp
   `research/manuscripts/figures/mtap-prmt5-figure-provenance.json`. [Ground 2, 8a]
3. **Demote figure 3 to a table.** Manuscript §3.3 — the three percentages, three means and three
   selectivities already exist as SI §S4's table. Re-number the remaining figures. [Ground 2, 8e]
4. **Retitle on the gene and lead on the negative.** Manuscript title, abstract opening, §4.1 and §5
   ordering, cover letter paragraph 1. Replace "The PRMT5 methylosome" with *PRMT5*, and put the
   *MTAP*-locus closure first in the title, the abstract and the Conclusion. Register the old title in
   Appendix A. [Ground 4]
5. **Resolve the replication contradiction.** Manuscript §4.1 (line 597) and §4.4 (lines 668 and 683).
   Delete "What survives correction is the replication" or restate it as directional concordance
   between two deposits; in §4.4 add that patient overlap between GSE24369 and GSE4303 was not
   checked and that GSE24369 carries no linked publication. [Ground 5]
6. **Make the Data Availability statement resolvable.** Manuscript §2.6 and §8. Name the public
   repository, give an archived release identifier for the state the paper is built on, and either
   deposit `cancer-modality-census.md`, the 591-text corpus record and the 322-record prior-art screen
   as supplementary files or relabel the §1.1 and §1.3 claims as the author's unpublished analyses.
   [Ground 6]
7. **Qualify the abstract's novelty sentence.** Manuscript abstract, sentence 3. Carry §1.3's own
   qualifier ("nothing is indexed on a pairing") into the abstract instead of asserting absence flat.
   Add one clause to §1.3 saying that neither screen is a full-text disease-to-target search. [Ground
   6, 9]
8. **Strip the repository apparatus.** Manuscript line 831 and SI line 405 — delete both `CLAUDE.md`
   citations and reword the appendix preambles without them. Appendix A rows 1 and 14 — remove the
   references to "the pre-posting checklist". Add a note (as the sibling GCC manuscript carries) that
   the YAML frontmatter and the appendices are repository record and are stripped at submission, or
   move both appendices to the SI. [Ground 7]
9. **Fix the three figure captions and one axis.** Figure 1 caption → "Every tumour in the analysed
   arms" (five deposited solitary fibrous tumours are not drawn). Figure 4 left panel → replace the
   `(n=…)` axis labels built at `emc_mtap_prmt5_figures.py` line 288 with tumour counts, or label them
   `6 tumours × 4 genes`. Figure 3 x-axis → cap at 100%. [Ground 8b, 8c, 8e]
10. **Make figures 4 and 5 greyscale-safe.** Figure 4 left panel → give pooled normal muscle a distinct
    marker shape, not just a distinct colour. Figure 5 → distinguish EMC from comparator fusions by
    hatch or outline rather than by red-versus-slate fill, and draw the GRG ticks in a colour that
    contrasts with both bar fills. [Ground 8d]
11. **Align §3.7's table with figure 5.** Manuscript §3.7 — put the table rows in figure 5's plotting
    order, and either split the "fraction of EWSR1's 11" column so TAF15 has its own denominator or
    move TAF15 to a footnote. [Ground 8f]
12. **Fix the experiment count.** Manuscript §4.2 heading → "Three decisive experiments", and add the
    two-construct experiment to the abstract's closing sentence; or fold it into experiment 1 and keep
    "two". [Ground 10]
13. **Repair the reference list.** Manuscript §9. Complete [7] with volume, issue and pages. Replace
    [16] with a sourced record or delete the junction it supports from §2.5, §3.7 and figure 5. Move
    the annotations in [2] and [16] into §2.5 and §4.4. Add, from committed retrieval records only, a
    primary report of the *MTAP*-deletion/PRMT5 lethality, a primary description of the EWSR1::NR4A3
    fusion, and the method citation for the dependency score; where no committed record exists, run
    the fetch rather than declining the citation. [Ground 11]
14. **Complete the AI declaration.** Manuscript §2.6 — add one sentence in the first person naming what
    the author personally re-derived, re-read and confirmed, which is the publisher's third required
    element. Manuscript §6 — replace "Generative AI. Section 2.6." with the statement itself. [Ground
    12]
15. **Disclose the related manuscripts.** Cover letter, paragraph 7. Name every manuscript from this
    author drawing on GSE24369 / GSE4303 that is under consideration or in preparation for this
    journal, and say what distinguishes each. This does not cure ground 3; omitting it converts ground
    3 from a scope problem into an integrity problem. [Ground 3]
16. **Verify the journal's limits before submitting.** `emc-mtap-prmt5-prepost.md` → "STILL NOT
    VERIFIED". Read the author guidelines for word count, abstract length, display-item count and
    reference style from the journal itself, and re-run `submission_metrics.py` against real limits
    with tables counted as display items. [Ground 2, 9]
17. **Supply an ORCID.** Manuscript title block and cover letter, in the same edit. The only
    author-side item that can block a portal submission, and the only one on this list the author
    cannot delegate. [Ground 13]
18. **Propagate the round-one corrections that were missed.** SI §S4 — "second of four comparator
    classes" → "third of the five tumour classes", and add the row to SI Appendix S1.
    `emc-mtap-prmt5-prepost.md` → replace −0.02 / −0.40 / +0.17 with +0.053 / −0.481 / +0.175, replace
    "second of four comparator classes", correct "§3.4's motif analysis" to §3.7, and narrow "the same
    four PRMT5-motif sites" to two of three reported clear cell junctions. [R1, R2]
