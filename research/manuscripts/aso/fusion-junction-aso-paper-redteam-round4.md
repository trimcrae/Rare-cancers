---
id: DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND4
title: "Round-4 review of the fusion-junction ASO submission — an editorial pass on register, structure and audience, and the section renumber it produced"
level: L3
kind: manuscript
status: live
canonical_for:
  - the round-4 editorial review of the fusion-junction ASO submission manuscript
  - the §3 and §4 section renumber map that rounds 1-3 predate
purpose: >
  Hold the editorial review of fusion-junction-aso-research-article.md run 2026-08-14, on the
  three axes rounds 1-3 did not cover: whether the prose is comprehensible to its stated audience,
  whether the section structure is balanced, and whether the paper is framed for the reader it is
  written for. Its second reason for existing is mechanical and load-bearing: this pass RENUMBERED
  §3.4-§3.11 and split §4, so every §-reference in rounds 1-3 and in the submission plan now points
  at the old numbering. The map below is what makes those documents resolvable.
scope: >
  Register, structure and framing only. No number was re-derived and no artifact was re-read: rounds
  2 and 3 did the verification pass, and this one is explicitly NOT a re-run of it. No claim, hedge,
  number, sequence or citation was altered — the numeric diff in §4 below is the evidence.
audience: [external reviewers, maintainers, autonomous research agents]
related: [DOC-FUSION-JUNCTION-ASO-SUBMISSION, DOC-FUSION-JUNCTION-ASO-REDTEAM-ROUND3]
date: 2026-08-14
last_verified: 2026-08-14
---

# Round-4 editorial review of the fusion-junction ASO submission

> **Rounds 1-3** are [round 1](./fusion-junction-aso-paper-redteam.md),
> [round 2](./fusion-junction-aso-paper-redteam-round2.md) and
> [round 3](./fusion-junction-aso-paper-redteam-round3.md). Nothing here re-raises a finding from
> any of them, and nothing here re-verifies a number — round 3 did that against the artifacts and
> found no arithmetic error.
>
> **Brief.** Review for writing style (jargon density), formatting (section separation and size),
> and framing, on the stated premise that **the primary audience is a wet lab trying to make an EMC
> drug**. That premise is what makes this a different review rather than a fourth opinion.

---

## 1 · What was wrong, measured

⭐ **The paper already contained everything a wet lab needs. It made none of it findable.** That is
the whole finding, and the three axes in the brief turned out to be three views of it.

| axis | measurement before | what it meant |
|---|---|---|
| **framing** | the entire bench payload — two named sequences, a companion arm, three controls, the falsification threshold — sat in **¶5 and ¶6 of a 7-paragraph Discussion**, ¶5 alone **789 words unbroken**, under no heading, at ~80% depth | a reader scanning headings saw eleven Results subsections about screens and **nothing saying what to make** |
| **structure** | Results subsections ran **104 to 1,364 words**; §3.4 was a 104-word stub, §3.11 a 163-word stub, §3.8 carried 1,364 words doing three jobs its title named two of | the shape of the document did not match the shape of the argument |
| **jargon** | ~11 paper-private terms used **12-43× each** (`near-match` 43, `seam` 41, `hybridisable` 36, `clean` 20, `gap-level margin` 14), defined once in passing in the Methods and **collected nowhere** | a reader who forgot what `hybridisable` means had to go hunting in Methods to read a Results sentence |
| **sentences** | mean **30.8 words**, median 28, **50 over 50 words**, 21 over 60, one at 114 | density on top of vocabulary |

⚠ **`lint_style` passed the whole time, and that is not a defect in it.** It ran clean at bold
2.3/1000 and em-dash 3.9/1000 against limits of 12 and 6. Gate 5 checks *register* — the repository's
own tics leaking into a manuscript — and register is orthogonal to whether a correctly-registered
paper is comprehensible or navigable. A clean gate 5 says the known tics are absent, which its own
header states explicitly, and says nothing about the four rows above.

---

## 2 · What was changed

**Framing.** The bench payload was promoted out of the Discussion into its own numbered
**§5 · Reagents, controls and the decisive experiment**, in four subsections (the two reagents; the
5-8-5 gap-length arm; the predicted load of each; controls and the decision threshold). The three
required controls became a list rather than a 76-word sentence. The Introduction gained a closing
paragraph saying what the paper hands a laboratory, and the abstract's Conclusions gained one
sentence naming the deliverable — previously the abstract ended on *"no computation here resolves"*
and a skimming reader learned only that the question was open.

**Structure.** Results went from 11 subsections spanning 104-1,364 words to **10 spanning 205-815**.
The 104-word orientation stub was folded into the clean-design section it was setup for; the
1,364-word §3.8 was split at the seam between the parent compartments and the genome-wide scan; the
163-word expression stub was merged into the section on what a near-match count represents, which is
the same argument. §3 gained a lead-in paragraph. The Limitations became **§6** with six labelled
paragraphs instead of one 724-word block, using the run-in labels the Methods already use.

**Jargon.** A nine-term **Terms used here** list closes the Introduction, pinning the paper-private
senses of *seam*, *frame-compatible*, *gap-level margin*, *near-match*, *hybridisable*,
*gap-paired*, *clean*, *search ceiling* and *load*. Eight argument-chaining sentences were split.
Pure enumerations — the sequence lists, the citation lineage's tail — were left long, because
splitting a list buys nothing.

**Result:** mean sentence **30.8 → 28.9**, over-50-word **50 → 35**, over-60-word **21 → 9**.

⛔ **THE HEADINGS I FIRST WROTE FAILED GATE 5, AND THE GATE WAS RIGHT.** Five of them
(*"…and why a low count is only a lower bound"*, *"What survives every screen…"*) were sentences
rather than noun phrases, which `lint_style.HEADING_VERBS` catches at >10 words or a finite verb.
The temptation is to read a gate that fires on new work as an obstacle to it. It was enforcing
journal register on headings written in the register of a findings memo, which is exactly the
failure the gate exists for. All five were rewritten as noun phrases; the gate was not touched.

---

## 3 · ⚠ THE SECTION RENUMBER — READ THIS BEFORE FOLLOWING ANY §-REFERENCE IN ROUNDS 1-3

Rounds 1-3, the [submission plan](./fusion-junction-aso-submission-plan.md) and
[the prior-art note](./aso-citations-priorart-2026-08-08.md) all cite the **old** numbering.

| old | new | note |
|---|---|---|
| §3.1 – §3.3 | unchanged | |
| **§3.4** (strand orientation) | **folded into §3.4** | was a 104-word stub; now the opening of the section it set up |
| **§3.5** (clean designs) | **§3.4** | |
| **§3.6** (chance + censoring) | **§3.5** | |
| **§3.7** (records vs loci) | **§3.6** | |
| **§3.11** (expression) | **merged into §3.6** | |
| **§3.8** (parent classes) | **split → §3.7 + §3.8** | §3.7 = pre-mRNA and mature parent; §3.8 = surviving candidates and the genome-wide scan |
| §3.9, §3.10 | unchanged | |
| **§4** (Discussion) | **split → §4 + §5 + §6** | §4 = discussion proper; §5 = the bench section; §6 = Limitations, previously a bold run-in inside §4 |

All 19 internal cross-references in the manuscript were remapped and verified.
`test_aso_parent_gap_pairing.py` pinned the string `"Five of the nine designs of §3.5 carry such"`
and was updated to `§3.4` — **that is a renumber tracked, not an assertion relaxed**: the test still
pins the same sentence to the same cross-reference, and a stale pointer there would let the paper
cite a section that no longer holds the designs it counts.

---

## 4 · Verification — the property that matters is that nothing moved but the prose

**No number, sequence, hedge or citation was altered.** Evidence, not assertion: every numeral and
every `5′-…-3′` sequence in the committed file was diffed against `HEAD` with PMID comments,
citation superscripts and section numbers excluded. **Numbers present before and absent after: one,
`1997,` → `1997.`**, a comma becoming a full stop where a 77-word citation sentence was split.
Sequences removed: **none**. Everything added traces to the glossary (`14`, `16`) or the §3 lead-in's
own section numbers.

**Gates.** All nine preflight gates pass. `lint_claims` — CI-only, so invisible to a routine
preflight — reports **0 ERROR and 0 findings against this manuscript**, which matters because the new
framing text is exactly the kind that could acquire an efficacy claim. `submission_citations --check`
reports 39 annotated citations over 35 PMIDs with 0 unannotated superscripts.
**The ASO and manuscripts suites run 503 passed, 0 failed**, against a pre-edit baseline of the same
503.

⚠ **One guard fired during the work and was correct to.**
`test_minus_strand_fraction_matches_the_manuscript` failed when a paragraph rewrap moved a line break
inside `(738 of 1,677)`, which the test tolerates in one position only. The count never changed; the
wrap did. It is recorded because it is the cheapest possible demonstration that these
substring-pinned tests catch edits that a reader would never notice.

⚠ **And the sandbox understated coverage until the dependencies were installed**, exactly as round 3
recorded. `pytest`, `numpy`, `biopython` and `jsonschema` are absent from this container as found;
without them the suite cannot run at all and `systems_check` fails closed with a message saying so.
Round 3's warning is now measured twice.

---

## 5 · What this review did not do

- **No number was re-derived and no artifact re-read.** Round 3 did that pass and found no
  arithmetic error; repeating it would test the copy, not the claim.
- **The abstract was cut to 199 words, clearing every cap in play.** ⚠ *Superseded, retained: "The
  abstract was restructured, not cut … taking it 459 → 507 words … the cut is still an author
  decision at the venue step, not an editorial one."* That was true for about an hour and was the
  wrong call twice over. Restructuring a 459-word abstract into paragraphs made it readable and left
  round 3's actual finding — that it is more than double every journal cap — untouched, and adding
  the deliverable sentence made it worse. Deferring the cut to "the venue step" also assumed the cut
  was venue-specific, and it is not: **200 clears all four**, so there is no version of this decision
  where a longer abstract buys anything.
  **What went, and it is recoverable from the body if a venue allows more:** the multi-partner
  16-mer, the genome-wide 20-of-176 stratum, the gap-length arithmetic in full (the Conclusions keep
  the finding), the ≥10-base-pair duplex threshold, and "three designs survive every screen, two at
  any parent-duplex threshold". Every number kept is unchanged and every hedge is intact.
  ⛔ **Three of the phrasings the cut first reached for were pinned by tests and existed ONLY in the
  abstract** — `All 38 were screened with alignment orientation filtered`, `87 of 190 pair`, and
  `61 of those against wild-type *NR4A3*`, each worded differently where §3.4 and §3.7 carry the same
  fact. Two more were broken not by deletion but by **line rewrapping**, which split a frozen phrase
  across a newline in a test that reads raw text rather than flattened. A test right beside one of
  them carries a `⚠ WHITESPACE-TOLERANT` comment for exactly that reason, so the inconsistency is in
  the assertions rather than in the prose; that is worth closing before the next person rewraps a
  paragraph.
- **The three pre-deposit blockers from round 3 are untouched and still author-only**: `ORCID:
  [to be inserted]` and the two `[ARCHIVE DOI]` placeholders, with the Zenodo DOI to be reserved
  *before* the deposit so the manuscript cites the DOI it will actually have.
- **The venue/label mismatch round 3 raised is unchanged**: the filename and running title still say
  *short communication* while the cover letter asks for the Article type, at 10,785 words.
