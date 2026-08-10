---
id: DOC-EMC-MTAP-PRMT5-PREPOST
title: Pre-posting checklist — the EMC PRMT5/MTAP preprint
level: L3
kind: runbook
status: live
canonical_for: ["posting readiness of the EMC PRMT5/MTAP preprint"]
purpose: >
  Hold every item that must be cleared before this specific manuscript is posted, separated into what
  an agent can close and what only trimcrae can supply — so the blocking set is a short explicit list
  rather than a vague "needs review".
scope: >
  Pre-posting steps for one manuscript. It posts nothing and authorises nothing.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
related: [DOC-EMC-MTAP-PRMT5, DOC-NR4A3-DEGRADER-PREPRINT-PLAN]
---

# Pre-posting checklist — PRMT5/MTAP

> ⛔ **NOTHING HERE POSTS ANYTHING.** Posting is outward-facing and irreversible, so it is trimcrae's
> call under CLAUDE.md §3, and the standing instruction as of 2026-08-09 is that nothing is posted
> until the papers are developed enough to rank.

## Venue — determined, and it is NOT the degrader paper's venue

⭐ **bioRxiv, not ChemRxiv.** The existing checklist picks ChemRxiv because the degrader paper is a
cryptic-pocket and de-novo-design paper, i.e. med-chem/comp-chem. **This manuscript is biological** —
a target-class hypothesis raised from expression and dependency data, with no chemistry in it. The
same checklist already names the alternative: *"bioRxiv is the alternative if we lean the framing
biological (also free)."* That is this paper.

- **Cost: $0.** bioRxiv posting is free, which satisfies the standing hard constraint (trimcrae,
  2026-07-05: **no pay-to-publish, author pays $0**).
- ⚠ **Journal route is NOT determined and is deliberately left open.** The degrader paper's JCIM plan
  does not transfer — JCIM is a chemical-information journal and this paper has no chemistry. Picking
  a biological journal with a confirmed $0 subscription route is a separate decision and is not made
  here.

## What an agent can close, and its state

| item | state |
|---|---|
| Figures rendered from committed artifacts, provenance-hashed | ✅ five figures; `--check` now hashes the **images** as well as the source artifacts, so a hand-edited or stale figure is detectable. ⚠ *Superseded, retained: the earlier stamp hashed only the five input artifacts while the tool printed "10 files match", which read as a statement about the images.* |
| SI written — methods, full tables, controls, failure modes | ✅ `emc-mtap-prmt5-hypothesis-SI.md` |
| Abstract structured for a preprint server | ✅ with the qualifier in its own paragraph |
| Every prose identifier anchored to a retrieval | ✅ `mtap-prmt5-emc-citations.json`, 0 new unanchored |
| Language rules (no efficacy/safety/window/readiness) | ✅ `lint_claims` 0 ERROR |
| Falsifiers stated, with the likeliest failure named | ✅ F1–F10; F8 names the pan-essentiality route, F7 has **partially fired**, F9 is **partially answered** by the third clear cell junction |
| Data availability — every series and panel identified | ✅ §2 and SI §S1 |
| The gene's own statistic, and an exact test for it | ✅ §3.5 — *t* = 6.24 / 6.67, exact permutation over all 1,623,160 and 8,008 labelings, no RNG |
| The controls the paper named, actually run | ⛔ §3.6, now FOUR of them — run on a full re-fetch. *PRMT5* ranks first of the readable PRMT family on both platforms; the **proliferation control takes *t* from 6.67 to 2.71 on GPL3290** and leaves 6.24 → 5.23 on GPL6244. The platforms disagree and the paper says so |
| Multiple testing, previously an open limit | ✅ §2.3/§3.5 — every gene on each array scored (**18,688** on GPL6244; **14,404 of the 14,932 with a probe** on GPL3290); *PRMT5* top 1.9% / 1.0%, *MTAP* top 74% / 26%. ⭐ **AND A CORRECTION IS NOW RUN, 2026-08-10**: a max-statistic permutation over a merged family of 5,449 / 4,848 symbols (`emc_prmt5_multiplicity.py` → `emc-prmt5-multiplicity.json`), exact on GPL3290. *PRMT5* adjusted *p* **0.21 and 0.24**, *MTAP* **1.00 and 1.00**. ⚠ *Superseded, retained: "18,474 and 14,402 symbols" and "Not a correction, and labelled as not one."* |
| Which half of the fusion carries PRMT5's motif | ✅ §3.7 + figure 5, with double-entry checks against two artifacts that predate this manuscript |
| Superseded numbers registered rather than dropped | ✅ main text Appendix A and SI Appendix S1 |

⛔ **The outstanding item is now a scientific one, not a build step.** The re-fetch landed, and what
it produced is a **disagreement between the two platforms about whether route 1's transcript reading
survives its proliferation control**. Nothing in this repository can settle that: the two series
measure different quantities, have different comparator arms, and there is no third readable EMC
series. It is a reason to post the paper saying so — not a reason to wait.

## Venue, fee route and format — moved here from the manuscript, 2026-08-10

⛔ **THE MANUSCRIPT USED TO CARRY THIS AS AN HTML COMMENT BETWEEN ITS SCOPE STATEMENT AND ITS
ABSTRACT, AND THAT IS A SUBMISSION HAZARD.** An HTML comment is invisible in rendered Markdown and
visible in a converted `.docx` or `.pdf`; it contained venue reasoning, fee-route notes and
instructions to the author. It is deleted from the manuscript and lives here, which is where a
pre-posting checklist belongs.

- **VENUE.** bioRxiv (Cancer Biology) as the free open copy, then *Genes, Chromosomes and Cancer*
  (Wiley), Research Article. (a) Audience: GCC is the field journal for the genetics and genomics of
  neoplasia and specifically for fusion-driven sarcomas, which is the readership for EWSR1::NR4A3,
  EWSR1::ATF1 and EWSR1::FLI1 biology; the transcript-type and breakpoint content of §3.7 has no
  better home. (b) Fee: GCC is hybrid, so the open-access charge is optional and the subscription
  route carries no author charge. (c) Precedent: `nr4a3-fusion-transcriptional-output-submission-checklist.md`
  selected GCC on the same two grounds on 2026-08-08.
- **FEE ROUTE — verified at primary source 2026-08-10**, from a GitHub Actions runner because the
  per-journal pages return HTTP 403 to the sandbox. Record with verbatim quotations, URLs and HTTP
  statuses: `research/literature/venue-fee-routes-2026-08-10.json`. Wiley states that under open
  access "the author pays an Article Publication Charge", that hybrid open access is selected by the
  corresponding author AFTER acceptance, and that a subscription article requires only a Copyright
  Transfer or Exclusive License Agreement. Declining the optional open-access selection is the $0
  route.
- ⚠ **STILL NOT VERIFIED:** the per-journal author-guideline pages return 403 from CI as well, so the
  word, abstract and display-item limits the manuscript is written to remain search-derived. Those
  affect FORMAT, which an editor returns, not COST, which is billed.
- ⛔ **ARTICLE TYPE — OPEN, AND THE PREVIOUS REASON DOES NOT SURVIVE INSPECTION (2026-08-10).**
  *Superseded, retained: "Research Article rather than Brief Report, because the paper carries five
  figures and the Brief Report limit is two display items."* Two things are wrong with that.
  **(a) It chose the type to fit the figure count, which is backwards** — content selects the type
  and the type then constrains display items. **(b) The display-item count it rested on was wrong
  in the permissive direction.** `submission_metrics.py` counted figures only; counting the numbered
  tables as an editor would, the paper carries **five figures and eight tables**. The gate now counts
  both and reports 13 items. ⚠ **The choice itself is trimcrae's**, because article type travels with
  venue and venue is an author decision. What an agent can say: the paper generates no new data, and
  after this revision it reports a bounded negative, a sequence observation and two named experiments,
  which is the content profile of a short-format or Hypothesis article. **Record whichever type is
  chosen with a CONTENT reason, never a figure count.**
- **ORCID — resolved 2026-08-10.** The manuscript's title block carried a bracketed placeholder while
  the cover letter stated that no ORCID accompanies the submission. The placeholder is deleted and the
  cover letter's statement stands. If trimcrae creates one, add it to both in the same edit.
- **IDENTIFIER FORMS.** Several references carry a PMCID and a DOI but no bare PMID, deliberately.
  `lint_citations.py` anchors a PMID only when a tracked artifact writes it as `PMID nnnnnnnn`, as a
  pubmed.ncbi.nlm.nih.gov URL, or as `EXT_ID`; the citation artifacts store it as a JSON field named
  `pmid`, which none of those patterns match, so writing such a PMID in prose fails gate 4 as if it
  had been recalled. The DOI and PMCID of each do anchor and are given instead. Add the PMIDs at
  submission once they anchor.
- **OPEN AT SUBMISSION: two bibliographic checks that need network this sandbox does not have.**
  1. Reference 2's published version was identified by literature search on 2026-08-10
     (`research/literature/prmt5-ccs-preprint-publication-status-2026-08-10.json`). Neither the
     publisher page nor the PMC record was reachable, so the author list, volume, issue, article
     number and DOI come from a search index and must be confirmed at the publisher. The finding
     itself — that a peer-reviewed version exists — is what the manuscript now asserts.
  2. GSE24369's source publication is not identified. GEO's own esummary for it carries a null
     PubMed field and no retrieval record here names a publication, so the manuscript cites the
     accession alone rather than inventing an attribution. GSE4303 is attributed to reference 12 on
     the strength of its deposited summary. A Europe PMC search from CI would settle the first.

## ⛔ What only trimcrae can supply — the actual blocking set

1. ✅ **RESOLVED 2026-08-09 — the details were already in the repository and I did not look.**
   Author, affiliation and corresponding email are now in the manuscript: Tristan McRae, independent
   researcher, unaffiliated, trimcrae@gmail.com — read from
   `research/compute/access-allocation-request.md`, and the unaffiliated status is what
   `emc-post-degrader-options.md` and `emc-atr-vulnerability-assessment.md` already state in prose.
   ⚠ **ORCID is the one piece genuinely absent from the repository.** It is optional on bioRxiv but
   worth having; only trimcrae can create or supply one. ✅ **The manuscript no longer carries a
   bracketed placeholder for it (2026-08-10)** — the placeholder and the cover letter contradicted
   each other, and the cover letter's "no ORCID accompanies this submission" is now the single
   statement.
2. **The decision to post at all**, and whether this paper goes first among the portfolio.
3. **Licence choice** (bioRxiv offers CC-BY among others). The degrader plan chose CC-BY for ChemRxiv;
   it is not automatic here.
4. **Whether to contact the holders of the two published EMC models before or after posting.** §4 of
   the manuscript names an addition to a screen those holders already run — that is an outreach act,
   and outreach is outward-facing.

## ⚠ Honest statements that must survive to the posted version

These are in the manuscript and must not be softened during any formatting pass:

- **No EMC cell line carrying the fusion appears in any public dependency dataset.** Every dependency
  figure is a transfer from other sarcomas.
- **PRMT5 and MAT2A are dependencies in 94.5% and 96.7% of the 91 SCREENED sarcoma lines** (⚠
  *superseded, retained: "of 176 sarcoma lines"* — 176 is the model count, 91 the screened count, and
  the manuscript's own Appendix A registers that correction). The proliferation half of the
  transferred result is therefore close to expected. ⭐ **And PRMT5 is a dependency in 94.1% of the
  NON-sarcoma lines too, selectivity 0.013** — the sharper statement of the same limit, now in §3.3
  and SI §S4.
- ⛔ **ROUTE 2 IS NOT SUPPORTED BY THIS PAPER'S DATA, AND THE ARGUMENT FOR THAT IS A PER-SAMPLE ONE
  THAT MUST NOT BE REPLACED BY A GROUP MEAN.** *MTAP* is flat where the read is powered (**+0.053
  SD**, 1.09-fold, CI 0.86–1.38); what signal the locus group score has is carried by *CDKN2A*
  (**−0.481 SD**), which reverses on the second platform (**+0.175**). ⚠ *Superseded, retained:
  "−0.02 SD", "−0.40 SD" and "+0.17" — main text Appendix A registers all three, and records that
  the −0.023 appears in no committed artifact anywhere in this repository.* ⭐ **AND THE CLOSURE
  LANGUAGE IS ALSO SUPERSEDED:** *"Route 2 is CLOSED by this paper's own data"* overstated a group
  mean, which cannot test a subset event. The live statement is that five of ten EMC tumours on
  GPL3290 read below every comparator for *MTAP* and **none of them carries the low *CDKN2A* that
  9p21 co-deletion requires**, that no tumour of sixteen is deletion-consistent, and that this bounds
  the frequency at **17%** rather than excluding it
  (`emc_mtap_locus_persample.py` → `emc-mtap-locus-persample.json`).
- ⚠ **The methylosome GROUP does not separate this disease** — pooled, EMC ranks **third of the five
  tumour classes**, below desmoid fibromatosis and solitary fibrous tumour. ⚠ *Superseded, retained:
  "second of four comparator classes"; both manuscript appendices register it, and it was still live
  in three files after the previous revision corrected it in the main text.* On *PRMT5* alone EMC has
  the highest class median. Route 1's claim is stated on the gene, not the group, and must stay that
  way — and "separates" is superseded too, because 9 of 34 comparator tumours read at or above the
  lowest EMC tumour.
- **16 tumours, two decade-old array platforms.** The genome-wide placement in §3.5 is context for
  that limit, not a correction of it, and must not be re-labelled as one — the correction is a
  SEPARATE procedure (§2.3) and both are reported. ⛔ **THE ADJUSTED VALUES MUST SURVIVE ANY EDITING
  PASS, IN THE ABSTRACT AS WELL AS THE RESULTS.** *PRMT5* does not clear 0.05 on either platform
  (0.21, 0.24). Reporting 0.000142 without its adjusted counterpart beside it is the edit that would
  most misrepresent this paper, and it is the one a copy-editor trimming for length would make.
- ⛔ **THE EXCLUSIONS AND THE REFERENCE CHANNEL MUST STAY DISCLOSED.** GSE24369 deposits 42 samples
  and 35 are analysed (five solitary fibrous tumours dropped by a classifier with no pattern for
  them, two pooled normal-muscle samples dropped by design); on GPL3290 the EMC arm and half the
  comparator arm were hybridised against different reference pools. Both are in §2.1 and both were
  undisclosed until 2026-08-10.
- ⛔ **MKI67 IS A PRE-SPECIFIED CONTROL THAT FIRES ON ONE PLATFORM AND MUST BE REPORTED.** *t* = 0.53
  on GPL6244 as specified, *t* = 2.30 on GPL3290. It was run and unreported until 2026-08-10.
- ⛔ **The proliferation control disagrees between platforms and the disagreement must survive.**
  *PRMT5* goes 6.24 → 5.23 on the 35-tumour platform and 6.67 → 2.71 on the 16-tumour one. Reporting
  only the platform that agrees would be the single most damaging edit anyone could make to this
  paper.
- **Route 1's ORIGINAL source is a preprint that states it is not certified by peer review.** ⭐ It is
  no longer the only support — the Ewing sarcoma result (PMC12354397) is peer-reviewed and shows a
  *fusion-dependent* PRMT5 requirement — but the preprint's status must still travel with every use
  of it.
- ⛔ **§3.7's motif analysis must not be presented as a response predictor OR as evidence for the
  fusion-class transfer, and the second half of that is new.** ⚠ *Superseded, retained: "§3.4's motif
  analysis" — the motif section is §3.7, not §3.4 — and "The commonest EMC fusion and the commonest
  clear cell fusion retain the same four PRMT5-motif sites", which was narrowed once to two of three
  reported clear cell junctions and is now **withdrawn as an inference altogether**.* EWSR1's GRG
  sites cluster at 301, 303, 316 and 320 with the next at 463, so **every** breakpoint in residues
  321–462 retains exactly four: a 142-residue plateau covering 21.6% of the protein, with both
  matched breakpoints inside it 107 residues apart. **What must survive is the plateau disclosure and
  the one durable observation** — the segment every EWSR1 fusion retains carries no site. EWSR1::FLI1
  retains none and PRMT5 still acts there in a fusion-dependent way, and that pair must survive too.
- ⚠ **Elevated PRMT5 is not specific to this disease on the published comparison.** PRMT5, PRMT1 and
  MEP50 read higher across multiple sarcoma types than in breast and lung cancer (PMC12354397). This
  paper's comparator arm is other sarcomas, which is harder — but the two statements are not
  exclusive and the manuscript says so.

## ⛔ Round two of simulated adversarial review — what it changed, 2026-08-10

Four independent simulated reviews (editorial, statistical, biological, integrity) were run against
the revised manuscript. Three of the four recommended **decline**; the fourth recommended minor
revision. The consolidated response is
[`emc-mtap-prmt5-decline-review-response-2026-08-10.md`](./emc-mtap-prmt5-decline-review-response-2026-08-10.md)
and it lists every ground applied and every ground declined. The three things a future session must
not undo:

1. ⛔ **THE TITLE NO LONGER CLAIMS A SURVIVAL.** *Superseded, retained: "a fusion-class rationale
   that survives and an MTAP-locus rationale that does not".* Three reviewers independently found
   that nothing bearing on the fusion rationale cleared 0.05 after the correction the paper itself
   elected to apply, and that the only reading which does is an instrument control. The live title
   is **"two rationales tested against the available public data, neither supported"**, and the
   claim structure changed in the abstract, §1, §3, §4.1, §5, the cover letter and here — not just
   the adjectives.
2. ⛔ **THE ADJUSTED *p* IS A PROPERTY OF ITS FAMILY AND THE RANGE MUST TRAVEL WITH IT.** The same
   code path gives **0.00015 / 0.000125** over the reported genes, **0.097 / 0.064** over the panel
   cache, **0.208 / 0.238** over the merged array-wide family, and **0.031** on GPL3290
   complete-cases. The array-wide family is the one quoted and §2.7 gives the reason it is the right
   one. Quoting a single value without naming its family is the edit that would most misrepresent
   this paper.
3. ⛔ **GPL3290 IS STRUCTURALLY CONFOUNDED AND IS NOT REPLICATION.** Disease class is collinear with
   GEO submission block, with the two-colour reference pool and with within-study platform
   assignment; all 10 EMC and only 6 of that deposit's 26 comparator sarcomas landed on the array.
   No re-analysis fixes it. Every sentence calling the two series a replication is withdrawn.

⭐ **AND ONE FREE ANALYSIS CHANGED A CONCLUSION'S FOUNDATION RATHER THAN ITS SIGN.** The biology
review found that the *MTAP* closure rested on a group-mean test that cannot see a subset event, and
that the committed per-sample data held a candidate one. Running the discriminating check cost
nothing and is now `emc_mtap_locus_persample.py` → `emc-mtap-locus-persample.json`, with a `--check`.
It came back **for** the authors: the five MTAP-low tumours all carry *CDKN2A* at or above their
array median, which is the opposite of co-deletion. The closure is stronger than it was and it now
rests on the right test — and it is stated as a bound (17% at 95%) rather than as an exclusion.

## Re-check before any posting pass

```bash
python3 research/modalities/emc_prmt5_multiplicity.py --check    # the correction reproduces
python3 research/modalities/emc_mtap_locus_persample.py --check  # the per-sample 9p21 reading
python3 research/modalities/emc_prmt5_effect_sizes.py --check    # effect sizes and family sensitivity
python3 research/modalities/emc_mtap_prmt5_figures.py --check    # figures AND images match
python3 research/manuscripts/lint_claims.py                     # language rules (CI-only gate)
python3 research/manuscripts/lint_citations.py                  # every identifier traces to a fetch
python3 research/manuscripts/submission_metrics.py              # abstract and display-item limits
./scripts/preflight.sh                                          # every gate, in order
```
