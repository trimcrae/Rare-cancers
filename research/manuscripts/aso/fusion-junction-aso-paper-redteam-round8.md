---
id: DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND8
title: "Round-8 swarm review of the fusion-junction ASO JOURNAL ARTICLE — the first review this document has ever had, and the gate-scope defect that explains it"
level: L3
kind: manuscript
status: live
canonical_for:
  - the round-8 swarm review of the fusion-junction ASO journal article
  - the round-8 wrong-leads record
purpose: >
  Hold the eighth adversarial review of the fusion-junction ASO work — and the FIRST of
  fusion-junction-aso-journal-article.md, the ~2,900-word journal submission. Rounds 1-7 all reviewed
  fusion-junction-aso-research-article.md, a different document. Its reason for existing is the one
  rounds 5, 6 and 7 state: a review whose findings are recorded nowhere gets re-run from scratch and
  its wrong leads get re-raised. Its most important content is not the finding list but the root
  cause in section 2: the journal article sits OUTSIDE the file scope of the repository's own gates,
  which is why a document with 24 blocker-grade charges against it has never turned a build red.
scope: >
  Claims, arithmetic, chemistry, statistics, clinical record, citation provenance, built artefact,
  standalone readability and bench executability of research/manuscripts/aso/fusion-junction-aso-journal-article.md
  and its two companions at commit 4cc0799. Ten reviewers, no cross-talk. NOTHING HERE IS APPLIED: no
  manuscript file was edited for this round; the ledger is the deliverable and application is a separate
  pass. "The wet-lab experiment was not done", "delivery is unsolved", "no cell line was tested",
  "nothing was synthesised" and "the method is not novel" are never findings here.
audience: [maintainers, external reviewers, autonomous research agents]
related:
  - DOC-FUSION-JUNCTION-ASO-JOURNAL
  - DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND7
date: 2026-08-21
last_verified: unverified
---
# Round-8 swarm review of the fusion-junction ASO JOURNAL ARTICLE

> **Rounds 1-7** are [round 1](./fusion-junction-aso-paper-redteam.md) through
> [round 7](./fusion-junction-aso-paper-redteam-round7.md). ⛔ **Every one of them reviewed a DIFFERENT
> DOCUMENT** — `fusion-junction-aso-research-article.md`, the ~39,000-word extended report. This round is
> the first review of `fusion-junction-aso-journal-article.md`, the ~2,900-word journal submission, which
> had **zero prior coverage**. That asymmetry is the single most important fact about this ledger: a
> finding "already dispositioned" in rounds 1-7 was dispositioned against the long form, and in almost
> every case the disposition rested on a disclosure that exists ONLY in the long form.
>
> **Reviewed:** `fusion-junction-aso-journal-article.md`, `-journal-tables.md` (GENERATED),
> `-journal-references.md` (hand-maintained), and both built PDFs, at commit `4cc0799`.
>
> **Method.** Ten reviewers, no cross-talk, ten distinct lenses: condensation fidelity · arithmetic vs
> artifacts · nucleic-acid chemistry and RNase-H1 · statistics and the falsification experiment · clinical
> sarcoma and test articles · citation provenance and the built artefact · standalone readability ·
> claim-strength discipline · bench executability · hostile referee. Each was required to cite an artifact
> field, a code line or a recomputation for every finding, forbidden to write "probably", required to read
> rounds 2/3/5/7 wrong-leads before filing, and required to attempt its own refutation first.
>
> **137 findings: 24 filed BLOCKER, 47 P1, 45 P2, 12 P3, plus 9 recorded non-landing attacks.**
>
> ⚠ **BLOCKER-AS-FILED IS NOT BLOCKER-AS-VERIFIED.** Round 7's own record is that four of five
> blocker-grade charges did not stand at the grade they were filed. **No adversarial verification pass has
> been run on this round's 24.** What section 3 carries instead is INDEPENDENT CONVERGENCE — how many blind
> seats reached the same defect by different routes — which is weaker than verification and stronger than a
> single opinion. Section 7 names the five that must be verified before anything is applied.

---

## 1 · What the round did NOT find, and it matters more than any single defect

**The arithmetic backbone of this paper is sound.** Four seats re-derived it independently, from the
artifacts rather than the prose, and it holds:

- `190 = 38 x 5` exactly; 87 liable, 61 against wild-type *NR4A3*, 85 of 87 own-parent, 93 as a correct
  union with 13 overlapping, 19 precursor-liable, 35 of 38 junctions clearing, 5 of 5 published junctions.
- Both named sequences, their margins, their 8 bp and 9 bp *TFG* runs, and every Table 1 and Table 2 cell,
  character-exact against the canonical CSV and FASTA. **780 records reconciled, 0 mismatches** (seat I).
- `aso_journal_tables.py` regenerates the committed tables **byte-identically** (seats I and B, independently).
- The null rates 6.2 / 45.8 / 40.6 / 1.8 %, and "four sign changes" recomputed exactly as `-,+,-,-,+,+,+,-`.
- 68.4 % and both Wilson endpoints, reproducing to four decimal places (39.887-82.791 %).
- ⭐ **The §5 power arithmetic is correct AND is the power of the rule the paper actually prescribes**
  (seat D): 81.28 % / 30.42 % by exact noncentral t, corroborated at 81.316 % / 30.442 % by a
  4,000,000-draw Monte Carlo that never touches `nct`. A launch hypothesis that it powered a different
  test is **refuted**.
- ⭐ **The citation chain inside the document is intact** (seats F and B, independently): 24/24 superscript
  pairs resolve identically in markdown and in the built PDF, contiguous 1->21, every PMID matching,
  including the out-of-order `<sup>7,17,8,9</sup>` group. **The renumbering bug the references banner warns
  about is genuinely fixed.**
- ⭐ **The exon-numbering convention is clean everywhere** (seats A and E, independently). E computed the
  leading non-coding exon counts directly — *EWSR1* 0, *TAF15* 0, *FUS* 0, *TCF12* 1, *TFG* 1, *NR4A3* 2 —
  and the three genes the article flags are exactly the three that differ. **The withdrawn version's error
  class has not recurred.**
- Both named reagents carry **no conventional sequence liability** (seat C): GC 43.8 % / 50.0 %, zero CpG,
  no G-quadruplex motif, homopolymer <= 3, self-dimer 4 bp.

**So the defects below are not arithmetic errors.** With two exceptions (B1 and C1) they are defects in what
the paper SAYS ABOUT its numbers, what it SHIPS, and what it silently leaves behind in the long form.

---

## 2 · ⭐ THE ROOT CAUSE — this document is outside the blast radius of its own repository's gates

> **Seat F ran every gate. All green. Both of its BLOCKERs stand anyway.**

`test_journal_references_match_the_prose.py` -> 0 (6 passed) · `lint_citations.py` -> 0 ·
`lint_claims.py` -> 0 (0 ERROR, 166 WARN) · `lint_consistency.py` -> 0 · `lint_style.py` -> 0 ·
the three PDF test files -> 0 (**39 passed**) · `test_aso_deposition_doi_is_one_fact.py` -> 0.
Build stamps **fresh** — all four sha256 match, so nothing here is staleness.

The mechanism, measured rather than inferred:

| gate | binding | consequence |
|---|---|---|
| `test_build_submission_pdf.py::test_the_repo_frontmatter_is_stripped` | bound to `PAPERS["aso"]` at line 22; **never sees `aso-journal`** | point it at the journal article and **2 of its 3 assertions fail**. No test reads this document's assembled body at all. |
| `lint_changed_prose.py` | `DEFAULT_TARGETS` omits the journal article (`:44-47`) | the one linter built for dropped-qualifier defects does not cover the document `lint_claims.py:92-94` itself calls "the riskier half" |
| deposition-DOI single-fact gate | reads only the extended report | F3 below stands unseen |
| journal PDFs | no pytest staleness gate (chain-only) | — |
| the tables caption's two bare PMIDs | read by no citation gate | — |

Seat H then measured the blast radius from the other side: it corrupted **14 quantities** in a shadow tree.
The **2** that are pinned in `pinned-figures.json` were caught. The other **12 passed silently** — including
`123 -> 999`, `margin of three -> six`, `8 bp / 9 bp -> two / one`, and the counts 19, 93, 85/87, 35/38,
47/183, 87-88-87, 1.8 %, 39.9-82.8 %.

**This is why a document can carry 24 blocker-grade charges and never turn a build red.** Every other finding
in this ledger is downstream of it, and fixing the gates is what stops round 9 from finding a fresh crop.

---

## 3 · P0 — the blocker-grade findings, ordered by independent convergence

⚠ Convergence is **not** verification. The "seats" column says how many blind reviewers reached it separately.

### 3.1 · CONVERGED AT FOUR OR MORE SEATS

| # | seats | finding |
|---|---|---|
| **P0-1** | **7** (G,I,A,J,D,B + maintainer) | §2: *"Table 1 carries it beside the sequences: 123 … against eight"*. **Table 1 has five columns and no load column** — not in the markdown, not in the generator (`aso_journal_tables.py:110-116`), not in the CSV, and not in either shipped PDF. The 123/8 values are themselves correct; the pointer is false. `--check` exits 0, so it is not staleness. |
| **P0-2** | **4** (G,I,A,F) | **Both built journal PDFs print the references file's raw YAML frontmatter as body text** — `id: DOC-…`, `level: L3`, `last_verified:` — plus two `<hr/>` and a duplicate `<h1>`, between the References heading and reference 1. Cause: `assemble()` applies `strip_frontmatter` to the manuscript at `build_submission_pdf.py:488` and **not** to the references file at `:490`; `strip_generated_banner` is `^`-anchored and cannot match a file starting `---\n`. The extended report's builds are clean, so this is unique to the never-reviewed document. **This is what a journal portal would receive.** |
| **P0-3** | **4** (G,I,J,F) | Masthead and Declarations assert the extended report *"is deposited as a preprint on bioRxiv"*. `PUB-ASO.state` = `complete_unposted`; the preprint checklist says *"⏳ Awaiting bioRxiv screening"*; the extended report's own masthead prints *"Prepared for deposit; not yet posted."* The builder comment at `:149-155` records this exact defect **and its fix, for the other paper**. Compounding it: the extended report is invoked 6x in reader-visible text and carries **no identifier a reader can reach** — no entry, no DOI, no accession — while four load-bearing claims delegate their evidence to it. |
| **P0-4** | **4** (J,C,D,B) | §5 prescribes a **dinucleotide-preserving** scramble and then quotes the **mononucleotide** ensemble's rates to justify the pre-screen: 6.2 % / 1.8 % against the prescribed ensemble's measured **10.0 % / 3.9 %** (`aso-parent-null.json`). Wilson intervals disjoint on both arms. It understates the wild-type *NR4A3* rate — the one a control must not engage — by **2.15x**, in the clause telling a lab why the screen is mandatory. `aso_parent_null.py:31-33` makes the wrong identification, and the pinned-figure guard pins the wrong value to that sentence, so the guard chain is blind to it. Seat C adds a second measured defect in the same sentence: *"the 5′ run is held"* is **false** — 4,000 draws through the repo's own shuffle retain GGG 100 % of the time for the *EWSR1* reagent and only **10.6 %** for the *TAF15* one. |
| **P0-5** | **4** (A,J,C,B) | §3's *"flat at 87, 88 and 87"* omits that the denominators are **190 / 266 / 342**. The shares fall **45.8 % -> 33.1 % -> 25.4 %**; junctions with a clearing design go **35/38 -> 38/38 -> 38/38**; and **the lead reagent's own parent duplex goes 8 bp -> 0 bp -> 0 bp** with margin 3 -> 5. Only the raw count is flat. Seat C then showed the stated mechanism cannot do the work claimed: the tiling identity is **true** (verified exhaustively at 190/190, 266/266, 342/342) but holds identically at every gap length, so it cannot explain flatness — while the artifact's own `improves_with_a_longer_gap` gives **181/190 -> 130/266 -> 87/342**. The extended report prints both series in one sentence. |

### 3.2 · CONVERGED AT TWO OR THREE SEATS

| # | seats | finding |
|---|---|---|
| **P0-6** | **2** (E,F) | ⛔ **A CITATION THAT SAYS THE OPPOSITE OF WHAT IT IS CITED FOR.** *"The disease responds poorly to conventional cytotoxic chemotherapy"* -> PMID 24345066, whose **Conclusions** read *"By contrast to what reported so far, anthracycline-based chemotherapy is active in a distinct proportion of EMC patients"* — **PR 4/10 = 40 %**. Only that paper's Background restates the low-sensitivity claim, so the article cites the setup and not the finding: `POLICY-evidence.md` §1.3 laundering. **The extended report handles it correctly and cites this same paper as the counter-example**, putting the low-ORR claim on entry 15 — so condensation introduced it. **Zero hits for this PMID across all seven prior rounds.** It is the first substantive clinical sentence in the paper, and this repository's first golden rule is the one it touches. Fix is a citation swap: the correct source (PMID 41055792) is already reference 15. |
| **P0-7** | **3** (H,J,B) | Declarations: *"Every quantitative claim is tied by automated guard to the committed artefact that produces it."* **False.** Only 12 pins covering 8 values name this file. Seat B lands the decisive half: §5's 80 % / 30 % / ~0.65 / ~2.4 have **no producing artefact anywhere** — `grep noncentral|scipy.stats` across every `.py` in the repository returns **zero**. Combined with seat D's verification that the arithmetic is correct, the true state is: *the numbers are right and are not reproducible from anything committed.* A false statement in Declarations is its own category of defect. |
| **P0-8** | **1** (F, systemic) | The gate that tests P0-2 is bound to the wrong paper — see section 2. Filed as a blocker in its own right because it is the reason the others survived. |

### 3.3 · SINGLE-SEAT BLOCKERS — highest verification priority

| # | seat | finding |
|---|---|---|
| **P0-9** | C | ⛔ **THE ONLY FINDING THAT WOULD CHANGE WHAT THE PAPER RECOMMENDS.** The mature-parent screen implements `fold = inf` per gap mismatch (`aso_parent_gap_pairing.py:126`) — one mismatch anywhere in the gap kills the duplex outright. `junction_aso_offtarget.py:665` **retires that exact model by name** as *"not a model the literature supports"*. Relaxed by one gap mismatch with a >= 5-nt surviving DNA run: liable designs **87 -> 168 of 190**, and against wild-type *NR4A3* **61 -> 112**. ⛔ **The *TAF15* reagent — one of the two named for synthesis — acquires a 12-bp duplex spanning its whole catalytic gap against the wild-type *NR4A3* exon-2/exon-3 seam.** The *EWSR1* reagent stays clean. Invisible to all five screens at 13/16 identity on a mature junction. The journal cites none of PMID 23963702 / 7567450 / 35664704 / 39126066 / 28624195; the extended report carries all five. |
| **P0-10** | B | §3 says *"the two screens condemn 93 of the 190"*, but the canonical CSV that Declarations tell readers to **order from** carries `do_not_order` on only **87**. The 6 pre-mRNA-only records (5 molecules, **including 2 at *TCF12* e5, a published-breakpoint junction**) are blank. Cause: `aso_sequence_manifest.py` never reads the pre-mRNA screen — grep returns zero hits. A design the paper condemns is unflagged in the file a lab orders from. |
| **P0-11** | I | §5 mandates screening the scramble before it is made and gives **no module, no strand and no rejection rule**. Run on the paper's own condemned `CAGGGCATATCATCAA`: as a target window it returns **11 bp, *NR4A3*, liable=True**; as the antisense string a lab would actually order, **0 bp, liable=False**. **A silent false pass.** The extended report carries the strand warning verbatim at lines 1709-1711; the journal does not, and the released module has no user-sequence entry point at all. Seats A and C reached the same defect from their own lenses (3 seats total). |
| **P0-12** | I | **Purification grade and synthesis scale appear in neither the article, the canonical CSV, the extended report, nor the SI** (grep returns nothing) — while Declarations instruct the reader to order from that CSV. Seat C adds: 5-methylcytosine appears **zero** times in the article, and the CSV's own header warns that a vendor default *"would ship two molecules"*. |
| **P0-13** | A | §7 states *"both compartments are searched here"*. The extended report names a **third** — the patient's own un-rearranged *NR4A3* allele — which condemns two designs at *EWSR1* e13::*NR4A3* e2, **the acceptor of USZ20-EMC1, a test article this article names**. No trace of the third compartment in the journal form. |
| **P0-14** | A,C | The paper adopts 5-6-5 while **its own cited enzymology source** (PMID 24981949, its reference 21) states that a six-nucleotide gap gives *incomplete* activity and that **7-10 is optimal**. The journal never says the geometry is below optimum and carries no 5-8-5 control arm (`grep -c '5-8-5'` -> 0); the extended report calls it the leads' *"first risk"*. ⚠ **Read with seat J's finding** that the actual reason for 16-mer/5-6-5 is a tooling limit — the genome screen is *"UNAVAILABLE BY CONSTRUCTION"* above 16 nt, which is in the artifact and not in the paper. So the geometry is chosen for a tooling constraint while the cited enzymology argues against it, and neither fact reaches the reader. |

---

## 4 · P1 — wrong, unsupported or unexecutable; not submission-blocking

**The experiment (§5).**
- The **0.65 void figure** is a threshold on the *realised sample SD* of the confirmatory run
  (`s* = log5*sqrt(n)/t_{.975,n-1}` = 0.647886 at n=3); the gate applies it to an *upper confidence bound on
  a pilot's population SD*. At the paper's own floor and own sigma = 0.35, a 95 %-UCB gate passes only
  **16.1 %** of pilots, and the unstated confidence level swings the pass rate **ninefold** (30.3 % -> 3.4 %).
  The threshold also scales with n (0.648 / 1.534 / 2.250 at n = 3 / 6 / 10), so applying one number to a
  pilot whose job is choosing n is circular. The extended report's escape clause (L1823-1826) is dropped, so
  *"void"* reads as terminal — and *"void"* is used undefined. [D]
- §5 defines a **closed** family — two named reagents plus a three-design fourth arm — read against one cut,
  then declines multiplicity on the extended report's **open-ended** reason. The citation is accurate but
  does not reach this case. **FWER 11.89 % against a nominal 2.5 %.** [D]
- ⛔ **"A fourth arm is free" is not free.** Its three designs sit at *FUS* e8, *TAF15* e1 and *TCF12* e7, and
  **none of the five test articles carries any of those junctions** — the paper says so itself at L143-144.
  The arm needs three constructs that do not exist. [D, with J and B converging on its membership]
- Table 2's caption says *"neither is a reagent this paper names for synthesis"*, but `GGGCATATCAAGCGCT` **is**
  one of the three designs §5 prescribes as that fourth arm. [J, B]
- *"Three designs clear every screen applied here"* drops the extended report's *"two of them at any
  parent-duplex threshold"*; the third is 8 bp against wild-type *NR4A3* and fails at any cut <= 8. [H, A]
- The limit-of-quantification condition is absent, so the decision rule as printed can pass by default. [A]

**Coverage and the nulls.**
- The 39.9-82.8 % range is called *"its interval"*; the extended report states in terms that it is **not a
  confidence interval**. Only two of four inputs are varied — partner shares are held at point estimates,
  undisclosed — and the 21-year cross-cohort transfer assumption is dropped. Its true posterior mass is
  **97.4 %**, so conservative rather than 95 %. [J, A, D, E]
- ⭐ **A free improvement the paper leaves on the table.** A third reagent, `GGGCATATCTCCACGG` at
  *EWSR1* e13::*NR4A3* e3, is **already designed and screened** at the same top margin with a **lighter**
  off-target load (24 against 123), and adding it takes stated coverage **68.4 % -> 79.0 %** for one
  oligonucleotide, no new screen and no new retrieval. The article mentions exon 13 exactly once, as the
  cell line's donor, never as an orderable design. [E and J converging]
- 68.4 % prices the *TAF15* arm at 3/3 while the article's own reference 13 reports **two** major
  TAF15::NR4A3 isoforms; the ladder and the extended report both call that arm an upper bound. [E]
- *"45.8 % for designs at real breakpoints"* — **165 of the 190 sit at junctions no patient is reported to
  carry**, the same property used to discount the 40.6 % chimera null. Within-panel: 44.0 % at the five
  published junctions against 46.1 % elsewhere. [B]
- *"stores at most 50 hits per query, so only 47 of the 183"* is **the wrong ceiling and a non-sequitur**.
  The code's hitlist is 50 but **retention is 15** (`junction_aso_offtarget.py:218,230,378`); no
  default-depth design stores more than 15, 141 store exactly 15, and 47 is the count at <= 15. At a true
  ceiling of 50 the assessable set would be **148**. [B]

**Clinical and citation.**
- *"the evidence is not decisive either way"* on *NR4A3* paralogue redundancy cites **only the permissive
  side**; the restrictive records the repository holds (PMIDs 21205929, 24005216) appear in none of the 21
  references. [J, A, E, F — four seats]
- *"Junction-directed oligonucleotides … reported against six fusion oncogenes"* — **only 2 of the 6 are
  antisense oligonucleotides**; entry 7 is shRNA and entry 8 is lentiviral-vector siRNA, with no
  oligonucleotide administered. The extended report labels each modality separately. [G, A, F]
- The TKI *"disease control"* figure is sourced to entry 15, not entry 4; the extended report states that no
  disease-control figure was read from any of these reports. Plural subject, one single-arm trial cited. [F]
- ⛔ *"**NR4A3** exon 2 **rather than** exon 3"* is stated as settled where the repository's own
  `_USZ_ACCEPTOR_AMBIGUITY` records *"THE ACCEPTOR EXON INDEX IS NOT SETTLED … Two readings survive"* — and a
  prior retraction of this exact class (EWSR1_e11) is on record. **Same error class as the withdrawn
  version.** [E]
- Competing interests declares only **financial** interests and drops the survivorship disclosure the
  extended report makes. Never raised in rounds 1-7. [G]

**Executability and framing.**
- The released builder **refuses** an *NR4A3* exon-2 acceptor — `RuntimeError … NOT on the
  published-breakpoint whitelist. Refusing to emit.` — which is the exact acceptor class **both** EMC cell
  models carry, against the abstract's unqualified *"The design pipeline is released for breakpoints outside
  the panel."* [I]
- The exon-2-acceptor reagents for the only two fusion-positive EMC cell models are prescribed but never
  named. **They exist and are findable** — `AGTGGGCTCTCCACGG` (8 bp vs wild-type *EWSR1*) and
  `AGTGGGCTCTTGTGTG` (**9 bp vs wild-type *NR4A3***, the acceptor parent §5's entire ratio is defined on) —
  so this is a routing gap, not a dead end. The favourable *TFG* numbers for the two named reagents are
  printed twice; these are printed nowhere. [G,H,I,J — resolved by maintainer against the CSV]
- Novelty is located in *"the screen applied before synthesis"* two sentences after *"no survey of published
  design pipelines was performed"*. [J]
- *"Predicted transcriptome load separates the two"*: recomputed, **82 of the 123 are predicted models** and
  32 of the 41 curated are one gene — the exposure axis runs the other way. [A]
- *"RNase-H1 does not require the whole duplex, only that the gap be paired"* is **uncited**, stated as fact,
  and needs 6 bp where §8's criterion needs 10; the extended report calls it *"a premise adopted here"* and
  states the unit mismatch. The 10-bp criterion itself carries **no citation** in this document. [C, A]
- The fifth test article's reagent is **uncertifiable under the journal's own §6 definition**; neither the
  third construct (T-N) nor the limit is named. [A]

---

## 5 · P2 and P3 — wording, placement, and deferred with a trigger

**P2.** The abstract says *"Five test articles are named:"* and enumerates **four** — six seats, distinguished
from round 7 §6.3 because there the charge failed for want of any stated total and here the total is in the
same sentence · the printed reference-list note *"Numbering follows the extended report … same number in
each"* is **false for 20 of 21 entries** and contradicts the banner three lines above it (see section 6 for
its true scope) · `SUBMISSION-PACKET.md` is stale at 3,217 words / 197-word abstract against a measured
**2,914 / 185** · §5 (the unrun experiment) is the largest section at 23.6 % of the text, larger than §3
which carries the result, while §6 is a 72-word stub whose only unique content is used nowhere else ·
*"test article"* carries two incompatible referents, colliding inside a control specification a lab acts on ·
the 2.4 ceiling is a property of the **dose** and reaches the cut of 5 at exactly **80 % knockdown** ·
*"the test can fail only where the reagent is anti-selective"* describes the observed ratio, not the reagent ·
*"All five screens address hybridisation rather than cleavage"* is wrong — screen 1 computes
`cleavage_weight()` · the 473-file Zenodo manifest contains **neither** `fusion-junction-aso-journal-tables.md`
**nor** `aso_journal_tables.py`, both named in the article · twelve standalone-comprehension breaks, about one
per 240 words, four of them dead-end hand-offs to the unidentified extended report · Figure 1 shows a
curiosity while the screen's result has no display item, and its legend attributes the discrimination problem
to FET paralogy where the paper attributes it to self-parent identity · margin-as-ranking fails at **8 of 42**
seams, at 5 of which a clean register existed.

**P3.** H-EMC-SS not named as a measured negative (trigger: next clinical-claims pass) · the title carries no
scope marker where the sibling opens *"In silico,"* · `<sup>7,17,8,9</sup>` printed out of ascending order ·
three of seven keywords duplicate title words and *locked nucleic acid* appears in none of title, running
title or keywords · the 190 designs are **176 distinct molecules**, and de-duplication moves the rate **up**
to 46.6 % (trigger: next deposit) · the packet still lists ORCID as *"THE ONE REMAINING ITEM"* though the
article carries `0000-0002-1823-1451` (trigger: next portal upload) · no alpha convention is attached to the
power figures, and under a one-sided 95 % bound n=3 gives **50.9 %**, not 30 % (recoverable two sentences
later) · `test_journal_references_match_the_prose.py` docstrings still describe the retired numbering scheme.

---

## 6 · ⛔ WRONG LEADS AND REFUTATIONS — recorded so round 9 does not re-raise them

### 6.1 · ⭐ The renumbering bug is FIXED — and two seats measuring a different thing looked like they disagreed
Seats G and I reported the reference numbering wrong (19 of 21; 4 of 5 spot-checked PMIDs mismatching).
Seat F went to the built PDF and found **24/24 superscript pairs resolve identically in markdown and in the
PDF, contiguous 1->21, with the out-of-order group correctly paired**; seat B corroborated independently.
**Both are right about different claims.** The within-document superscript -> entry -> PMID chain is intact;
what is false is the printed sentence claiming that a reference shared with the extended report carries the
**same number in both documents** (journal 11 is extended-report 22, and so on). Seat A drew the same
distinction unprompted. ⭐ **Consequence: this is a false sentence in a caption, not a broken citation chain.
No reader is sent to the wrong paper. Severity is "delete one sentence", not "blocker".**

### 6.2 · The exon-2 reagents are NOT unreachable, and a "contradiction" between seats was a definition
Seats G, H and J filed the exon-2-acceptor reagents as unnamed; seat I filed them as identifiable and clean.
Settled by the maintainer against `fusion-junction-aso-sequences.csv`: `AGTGGGCTCTTGTGTG` carries
`mature_parent_duplex_through_gap_bp = 9`, `mature_parent_duplex_gene = NR4A3`,
`pairs_a_wild_type_parent_through_the_gap = False`. **All three seats read real fields.** I read the boolean
(not liable at the 10-bp cut) and called it clean; H and J read the run length and the gene. That is exactly
the split the paper itself concedes when Table 1 prints the length *"rather than a pass mark"*. Not a
contradiction, and **not a blocker** — the routing gap and the 9-bp-vs-*NR4A3* asymmetry both stand as P1.

### 6.3 · The power figures are NOT computed for a different test
A launch hypothesis, refuted by seat D with two independent methods (exact noncentral t and a
4,000,000-draw Monte Carlo avoiding `nct` entirely). Do not re-raise.

### 6.4 · Nine attacks the hostile referee tried and abandoned, with the observation that killed each
68.4 % is **not in the abstract at all** · the *EWSR1* reagent is **not** among the 19 precursor-liable
(`gap_fully_paired: false`, one gap mismatch) · e12 and e6 **are** the top two breakpoints (52.9 % / 15.5 %
against 10.6 % for the next) · the extended report **is** inside the cited Zenodo deposit, though the paper
never says so · the research-use-only declaration **does** reach the reader in four places · the ORCID passes
MOD 11-2 and is registry-recovered · **93 is a correct union** with 13 overlapping · de-duplication moves the
rate **against** the attacker · the *"at or above one"* void fix is present, and the 10-bp cut's sign-change
ladder is disclosed by the paper itself.

### 6.5 · Two charges seat H filed and then refuted itself
*"Candidate" is not used in two senses* — §6's subject is a user's own sequenced breakpoint, which by
construction is a patient's junction, so §3's exclusion does not apply. And **there is no
"recommend-and-disown" blocker**: §2's claim is a within-junction ranking on margin and parent-run length,
neither of which moves with the cut, and the paper discloses exactly how the verdict moves at eight, nine and
ten. That axis is coherent.

### 6.6 · Prior-round coverage, honoured
No finding here re-raises round 7 §6.1-§6.9, round 5 §5.1-§5.2, or round 3's applied binary-rule finding.
Where a round-8 finding shares ground with one (the unit mismatch, gap length, strand convention, de-dup),
the seat named the prior item and stated what is new — and **in every such case the prior disposition rested
on a disclosure that exists only in the extended report**, which is precisely why round 8 exists.

---

## 7 · What this review did NOT do

1. ⚠ **No adversarial verification pass was run on the 24 blocker-grade charges.** Round 7's record is that
   four of five did not stand at the grade filed. **Verify before applying**, in this order:
   **P0-9** (the retired-model screen — the only finding that would change what the paper *recommends*,
   not merely what it says), **P0-10**, **P0-6**, **P0-11**, **P0-1**.
2. **No primary source was re-read for the two clinical citation findings.** Europe PMC is blocked at the
   egress proxy (`curl: (56) CONNECT tunnel failed, response 403`), so P0-6 and the TKI finding rest on this
   repository's committed records of those sources, not on the papers themselves. Route via the Actions
   runner before applying.
3. **Nothing was applied.** No manuscript, table, reference, code or artifact file was edited. `git status`
   was clean at every seat's exit and at the maintainer's merge.
4. **No screen was re-run to change an artifact.** Where a seat recomputed — the relaxed-mismatch sweep, the
   4,000-draw shuffle, the Monte Carlo power check, the null ladder — it was to test a claim, and the
   recomputation is reported in the seat's file rather than committed.
5. **Whether bioRxiv has posted since 2026-08-20 is unrecorded anywhere in the tree**, and bears on P0-3.


---

# ⭐ THE VERIFICATION LAYER — five refuters, and what happened to the blockers

> Section 7.1 above said no verification pass had been run. **It has now.** Five refuters, each told
> to default to REFUTED and to attack the charge rather than confirm it. Round 7's record held: the
> round's most-promoted blocker did not survive, and one charge changed character entirely.

| charge | filed | verdict | applied? |
|---|---|---|---|
| **P0-9** retired-model screen / *TAF15* 12-bp duplex | BLOCKER, 1 seat | ⛔ **BLOCKER REFUTED** — survives only as a condensation defect | partly |
| **P0-10** 93 condemned in prose, 87 flagged in the file | BLOCKER, 1 seat | ✅ **SURVIVES AT BLOCKER** | ✅ code fix |
| **P0-11** scramble strand trap | BLOCKER, 3 seats | ▽ **SURVIVES AT LOWER GRADE (major)** | ✅ §5 sentence |
| **P0-6** chemotherapy citation | BLOCKER, 2 seats | ✅ **SURVIVES AT BLOCKER**, character corrected | ✅ citation swap |
| **P0-4** scramble ensemble mismatch | BLOCKER, 4 seats | ✅ **UPHELD, both halves** | ✅ prose + pins |
| **P0-5** "flat at 87, 88 and 87" | BLOCKER, 4 seats | ✅ **UPHELD** | ✅ paragraph rewritten |
| third reagent `GGGCATATCTCCACGG` | proposal, 2 seats | ⚠ **ADD WITH STATED CAVEAT** | ⛔ **NOT applied — see below** |

## V1 · P0-9 — the blocker this ledger promoted hardest, and it is wrong

§3.3 called this "the only finding that would change what the paper RECOMMENDS". **It does not.**

- **Line 126 is not the retired model.** `RETIRED_ABOLITION_MODEL` (`junction_aso_offtarget.py:668`)
  is a per-mismatch multiplier on cleavage *rate*, consumed by `cleavage_weight` at ≥14/16 identity.
  Line 126 defines a duplex-*length* metric with its own anchors in `lit-targets-aso-gap-length.json`
  (PMID 24981949 "a gap of six DNA nucleotides is necessary"; 28290206 "at least 6"; 41614678 "six or
  more"). **Different quantity, different citation.** The charge conflated them.
- **The *TAF15* 12-bp claim is false as stated.** At the *NR4A3* exon-2/exon-3 seam, gap position 5 is
  a C:A **mismatch** — the whole gap is not spanned. It is a **10-bp** contiguous duplex; 12 was a
  span containing a mismatch. The *EWSR1* lead pairs 4 of 6 over 9 bp at the same window, so the two
  are one base apart rather than clean-versus-dirty.
- **The relaxed count is not news.** The committed model already gives **181/190 at a cut of six** and
  **175/190 at seven** — both larger than the charge's 168, and both already printed in the paper.
  The charge's 112 mixed two different bases (any-*NR4A3*-window, baseline 62) with the best-parent
  pair (61→100).
- ✅ **The *TAF15* reagent can still be named.** No change to Table 1 or 2, to §5's ratio, or to which
  reagents are named.

**What did survive, and was applied:** the journal article asserted "87 … the single largest liability
class" with none of the fully-paired-class qualifier the extended report carries twice. §2 now states
that the criterion counts only whole-gap windows, that a single gap mismatch reduces rather than
abolishes cleavage, and gives the cut ladder (175 at seven, 181 at six).

⚠ **AND THE FIX ITSELF CARRIED A REGRESSION, CAUGHT BY V5.** The refuter's proposed sentence said
"at any run length 181 of the 190 pair a parent". **181 is the count at a SIX-base-pair cut**
(`aso-parent-null.json` → `cut_sensitivity.observed_cut_ladder.6.n_liable`), and
`aso_sequence_manifest.py:717-718` records this exact correction having been made once already. It was
applied verbatim and then corrected. Its companion sentence quoted seam figures with no committed
artifact behind them; those were removed rather than printed. **A verifier's pasteable fix is not
pre-verified prose.**

## V2 · P0-10 — survives, and the fix was code

The escape route does not exist: the CSV's own preamble defines the column as "…**or another screen
condemned the row**", plural. `grep -i premrna` over `aso_sequence_manifest.py` returned **zero**.
Six records — five molecules, two at `TCF12_e5__NR4A3_e3`, a junction the same file grades
`published_exon_resolved_breakpoint` — were blank in the file the Declarations tell a laboratory to
order from. **Applied:** `_PREMRNA_DO_NOT_ORDER` + `_stamp_the_premrna_liability()`, run before the
twin pass so a condemned row can never be offered as the clean member of a near-identical pair.
**252 → 257, exactly the delta V2 predicted independently.** §3's prose needed no change: it was
arithmetically right and the artifact was wrong.

## V3 · P0-6 — survives, but it is MIS-SOURCING, not a fabricated fact

`research/literature/rt-lung-mets-probe.json` holds the abstract. Conclusions: *"By contrast to what
reported so far, anthracycline-based chemotherapy is active in a distinct proportion of EMC
patients."* Background: *"Its sensitivity to chemotherapy **is reported to be** low"* — hearsay, and
the exact proposition the Conclusions overturn. PR 4 (40%), SD 3, PD 3 of 10 evaluable.
**The claim itself is true**: the repository's own pooling gives cytotoxic ORR **4/33 = 12.1%**
(Wilson 4.8–27.3). The article had cited the one cohort in the class that runs against it.
Three escapes tested and killed: full-content (only the Background hearsay supports it), scope (the
pooling files this study under `regimen_class: "cytotoxic chemotherapy"`, so in-scope *and*
contradictory), and nearby-rescue (one line in the whole article mentions chemotherapy).
**Applied:** the review (PMID 41055792) now carries the general claim and the series carries its own
finding; the list renumbered by order of first citation, 21 entries, guard green.
⛔ **Do not re-point at PMID 31331701** — its low-sensitivity line is that trial's own Background,
the same defect one document over.

## V4 · P0-4 and P0-5 — both upheld

`aso-parent-null.json`: `scrambled_mononucleotide` = 0.06179/0.01818, `scrambled_dinucleotide` =
0.09987/0.03911, all arms at n=38000; Wilson intervals disjoint on both. The attachment escape does
not exist. Seat C's GGG test reproduces exactly: **4000/4000 (100.0%)** for the *EWSR1* reagent,
**424/4000 (10.6%)** for the *TAF15* one — only the first base is preserved by an Altschul-Erikson
shuffle. ⚠ **One sub-claim corrected: the pin did not pin a wrong value — no pin covered §5 at all**,
and `rate_liable_against_NR4A3` was unpinned for *every* ensemble in the repository. Both are pinned
now. Flatness: 190/266/342 confirmed, shares 45.79/33.08/25.44%, clearing junctions 35→38→38, lead
reagent 8 bp→0→0, margin **3→4→5** (the charge said 3→5).

## ⚠ The third reagent — verified sound, deliberately NOT added

V5 returned **ADD WITH STATED CAVEAT** and every claim checked out: the row exists with `do_not_order`
empty, margin 3, 8 bp against *TCF12* (not *NR4A3*), full five-screen parity, and the coverage
arithmetic reproduces exactly at **68.4% (39.9–82.8) → 79.0% (50.3–89.2), +10.6 points**, with the
interval moving up and narrowing. *EWSR1* e13 is published exon-resolved four ways, and the
`_USZ_ACCEPTOR_AMBIGUITY` trap does not fire — that ambiguity is about the USZ lines' **acceptor**,
while e13 is the **donor** under both readings.

**It is still not added, for three reasons that are the paper's, not the reagent's:**
1. **It has no test article.** It would be the only named reagent without one, and §4 is built on the
   reagent↔test-article pairing.
2. **Adding it would create a fresh asymmetry.** Its own *NR4A3* precursor site (2 mismatches, 1 in
   gap, intron-exon spanning) has no committed measurement of the kind §2 now prints for the other
   two — so it would read clean by omission, which is the exact defect this round is closing.
3. **The coverage integration is not mechanical.** A naive third arm in `aso_reagent_coverage.py`
   gives the right point (79.0%) and a **broken interval (42.9–112.8%)**, because
   `wilson(10,15) + wilson(2,15) ≠ wilson(12,15)`; it must aggregate per partner first.

**Ready for the next pass, with the work named.** This is a scoped improvement with a verified
payoff, not an open question.
