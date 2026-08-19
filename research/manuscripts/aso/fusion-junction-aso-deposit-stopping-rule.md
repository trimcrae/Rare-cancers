---
id: DOC-FUSION-JUNCTION-ASO-STOPPING-RULE
title: "The pre-registered stopping rule for the fusion-junction ASO deposit — written before the final round, so the result cannot be rationalised into it"
level: L3
kind: manuscript
status: live
canonical_for:
  - the termination condition for adversarial review of the fusion-junction ASO submission
purpose: >
  Fix, IN ADVANCE, the condition under which review of fusion-junction-aso-research-article.md stops
  and the preprint is deposited. It exists because the alternative — deciding after the fact whether
  a round's findings were "serious enough" to warrant another — has no stopping point, and seven
  rounds have demonstrated that this method finds something every time.
scope: >
  The termination condition for adversarial review of the three fusion-junction ASO submission
  documents — the research article, its supplementary information and the generated submission
  tables — for a bioRxiv deposit specifically. ⛔ It governs WHEN REVIEW STOPS and nothing else: it
  is not a quality claim about the manuscript, not a checklist of deposit steps (that is
  fusion-junction-aso-preprint-checklist.md), and it says nothing about any other paper in the
  portfolio. Its five conditions and its one headline-falsifying exception are binding; everything
  else here is the reasoning that produced them.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-16
last_verified: unverified
---
# The stopping rule, pre-registered

> ⛔ **WRITTEN AND COMMITTED BEFORE THE FINAL ROUND RUNS.** That ordering is the whole point. A
> stopping rule written after the results are known is not a stopping rule, it is a justification.

## 1 · Why a rule is needed at all

Seven adversarial rounds have run on this manuscript. Round 7 pre-registered the prediction that no
coverage gap remained in text six prior rounds and eighteen reviewers had walked past, and **that
prediction was falsified** — B5-F1 found one, in text no prior round had touched.

The honest reading of that is **not** "run round 8". It is that this method has a floor above zero:
the same model family, reviewing the same document, with the same blind spots, will keep returning
findings for as long as it is asked to, and the marginal finding gets smaller while the marginal cost
does not. "No problems left" is not a reachable state and is not the target.

What *is* reachable is a **defined done-state**: every known finding dispositioned, the recurring
defect classes converted into gates that make them structurally impossible, and the stopping
condition fixed in advance.

## 2 · The rule

### ⭐ CONDITION 6 — TWO READERS, AND ONLY THE OVERLAP COUNTS (added 2026-08-19, trimcrae)

#### ⛔ Round 15 — condition 6 FAILS on one shared major, and TWO of the findings were fixes from round 14

Same 57-page deposit PDF, two readers. A swept linearly; B chased every pointer, referent and term-sense.

| | reader A | reader B |
|---|---|---|
| blockers | 0 | 0 |
| majors | 1 — §4.4's discrimination clause mis-points to §4.2's gap-length arm | 4 — the same clause; "every design here is specific to one exon pair"; §3's pre-mRNA scope; §5 resting the claim on the one-mismatch scan |
| minors | §2.7's inverted mismatch pairing; justification blowout | Table 6's dropped scope; "load" carrying two senses; Declarations naming a scrambled sequence that does not exist |

**⛔⛔ TWO OF THESE WERE INTRODUCED BY ROUND-14 FIXES. THIS IS THE COST OF REPAIR, MEASURED.**

1. **§3's pre-mRNA scope (major, B).** Round 14 fixed A's "two disjoint nines" minor by writing
   *"none of which carries a parent pre-mRNA site **at all** (§2.5)"*. §2.5 supports only the strict
   class — line 433 says so in terms, *"the 19, not the 53 or the 40"* — and is silent on the wider
   forty. **The paper's own lead reagent sits in that forty** (§4.3). A scope-widening defect was
   introduced by a fix for a referent defect, in the very class the 251-claim audit existed to close.
2. **§2.7's inverted pairing (minor, A).** Audit fix 5 transcribed the diagnosis's *"4–5 mismatches"*
   — true as a RANGE over {11, 12} — into a sentence already enumerating *"eleven- or twelve-"*. A
   range became a mapping, and because run length and unpaired count are anti-correlated, writing both
   lists ascending inverted it: 11+4=15, 12+5=17, in a 16-mer. Now guarded by
   [`test_paired_numeric_lists_are_bound_in_the_right_order.py`](../tests/test_paired_numeric_lists_are_bound_in_the_right_order.py),
   which was **proved against the original defective sentence** before being kept.

★ **AND MY ROUND-15 FIX OF THE SHARED MAJOR WAS ITSELF WRONG.** Reader A flagged §4.4's clause; I
re-pointed it at the margin-contrast arm. B, arriving later, showed the right target is the
**fusion-negative isogenic comparator** — §4.2 says outright *"Both arms therefore need the
fusion-negative comparator below"*, and the comparator is §4.4's own third control. Re-fixed to B's
target. ⚠ Two readers disagreeing about the REMEDY, where both agreed on the DEFECT, is an argument
for the overlap rule and against acting on one reader's proposed wording.

⭐ **THE HONEST READING OF THE ROUND.** Zero blockers from two independent readers is real progress —
that is four consecutive readers finding none beyond the author-only ORCID/DOI pair. But the majors
did not go to zero, condition 6 fails on the shared §4.4 clause, and **the repair process is now a
measurable source of defects**: 2 of 7 findings this round were created by the previous round's
repairs, and one of this round's repairs was wrong on first attempt. A round is not evidence of
convergence if the round's own fixes generate the next round's findings.

#### ⭐ Round 14 — condition 6 MET with ZERO overlap, condition 5 open on the author-only block alone

Two readers, the same deposit PDF (58 pages), different angles: A swept the document linearly, B worked
**backwards from every display item to the prose that cites it**. Between them, **1 blocker, 0 majors,
4 minors — and not one minor in common.**

| | reader A | reader B |
|---|---|---|
| blocker | ORCID + archive-DOI placeholders | the same three placeholders |
| majors | 0 | 0 |
| minors | §3's two disjoint "nine designs" sets | §2.4 attaching the 21's property to the count 40; "A sixty-second design"; Table 6's one-line page |

**The only blocker is the author-only set** — ORCID and the reserved archive DOI, open since round 1 and
listed in §5 as the three things only trimcrae can supply. Both readers independently derived that it
blocks deposit *from the document's own text*, which is the placeholder doing its job.

**All four minors are fixed**, per trimcrae's rule that the overlap is the stopping test and not a repair
filter. Two were substantive (a count conflation and a referent left open), one readability, one layout.

⭐ **AND B FOUND A CONTRADICTION INSIDE THE BLOCKER THAT WAS MINE TO FIX.** Availability read that the
artefacts "are released under a single archived version, **deposited** from the public repository" with a
bracket appended to the same clause saying "the archive **has not been deposited**". The DOI is the
author's; the tense was not. Both Availability and Data-and-code availability now read in the tense the
deposit is actually in.

##### ⛔⛔ THE LAYOUT MINOR EXPOSED A FIX THAT HAD NEVER WORKED

B's one-line page (110 characters against a median of 4,235) already had a fix in the stylesheet, written
that morning, whose comment named *that exact sentence and that exact character count* and added
`orphans: 3; widows: 3` as the remedy. **It could not have worked.** Only the paragraph matching
`**Table n.` was ever given the `legend` class; every caption footnote — including the one that orphaned
— rendered as a bare `<p>` the rule never reached.

Two further attempts were made and **refuted by measurement**, not by argument:

| attempt | result |
|---|---|
| class the footnote `legend` | page 42 still 110 chars — Chromium ignores `widows`/`orphans` inside a box already abandoned for `break-inside: avoid` |
| tighten `p.legend.note` margins | page 42 still 110 chars — the class was still never applied: **manuscript style never calls `render_float`**, so a flag keyed to the float path was False for every table in the deposit artefact |
| track the caption span in `markdown_to_html`, opener → first pipe row | 9 footnotes classed, page gone, **58 → 57 pages**, no page under 400 characters |

★ **THE LESSON IS NOT THE CSS.** It is that a comment naming a symptom is not evidence the symptom is
gone, and that two of three plausible fixes changed the stylesheet without changing the artefact.
[`test_no_page_is_nearly_empty.py`](../tests/test_no_page_is_nearly_empty.py) therefore measures the
**rendered PDF**, and a second guard asserts the class is actually emitted — the join whose absence made
the original fix inert.

#### Round 13 — condition 6 MET, condition 5 not

Two readers, same build, same briefs as round 12. **Zero minors were raised by both** — reader A's
three and reader B's two are entirely disjoint sets. That is condition 6 satisfied for the first
time.

⛔ **THE ROUND STILL DOES NOT PASS, BECAUSE READER B RETURNED A MAJOR.** Condition 5 requires nothing
above `minor`, and both conditions have to hold. §3 said three designs "every parent screen passed"
pair their whole catalytic gap against the un-rearranged allele — but this paper has TWO parent
screens, and §2.6 says in terms that only the mature-parent one passed them: "The same three were
returned independently by an exhaustive scan of the *NR4A3* unspliced sequence, by the pre-mRNA
screen and by the genome scan." Box 1 had it right and narrow ("Each cleared the spliced-cDNA parent
screen"); §3 generalised it into a falsehood about the designs this paper condemns.

⚠ **AND ONE OF READER B'S MINORS TRACES TO A ROUND-11 REPAIR.** §2.4 pointed at §2.5 for "none of the
nine has a sense-strand site in parent pre-mRNA". Round 11 NARROWED §2.5 to the strict 19-design
class — correctly, on a different finding — which left the §2.4 pointer claiming more than its target
now says. Fixing a section can invalidate a cross-reference into it, and nothing in the build checks
that.

All six findings of round 13 are fixed. Round 14 is the next test.

#### Round 13 — condition 6 MET, condition 5 not

Two readers, same build, same briefs as round 12. **Zero minors were raised by both** — reader A's
three and reader B's two are disjoint sets. Condition 6 satisfied for the first time.

⛔ **THE ROUND STILL FAILS, BECAUSE READER B RETURNED A MAJOR**, and condition 5 requires nothing
above `minor`. §3 said three designs "every parent screen passed" pair their whole catalytic gap
against the un-rearranged allele. This paper has TWO parent screens, and §2.6 says only the
mature-parent one passed them: "The same three were returned independently by an exhaustive scan of
the *NR4A3* unspliced sequence, by the pre-mRNA screen and by the genome scan." Box 1 had it right
and narrow — "Each cleared the spliced-cDNA parent screen" — and §3 generalised it into a falsehood
about the three designs this paper condemns.

⚠ **ONE OF READER B'S MINORS TRACES TO A ROUND-11 REPAIR.** §2.4 cited §2.5 for "none of the nine has
a sense-strand site in parent pre-mRNA". Round 11 NARROWED §2.5 to the strict 19-design class —
correctly, on a different finding — leaving the §2.4 pointer claiming more than its target now says.
Fixing a section can invalidate a cross-reference INTO it, and nothing in the build checks that.

#### ⛔⛔ WHY THE MAJORS APPEARED LATE, AND WHAT THAT SAYS ABOUT THE EARLIER CLEAN ROUNDS

trimcrae, 2026-08-19: *"Where are all these majors coming from all of a sudden? Why were these missed
so many times before?"* The answer is not that the paper got worse. **The brief got wider.**

From round 11 the screening scope gained: *a universal or counted claim ("no other", "only",
"every", "none", "the two", "the three", "the same screens") that the paper's own content
contradicts.* Every major since is that class — "clean" carrying four senses, "the same screens"
where four of five ran, "every parent screen passed" where one screen caught all three. Two of the
three PREDATE this session; only the "clean" collision involved a sentence written during it.

★ **SO ROUNDS 4, 7, 8 AND 10 WERE PARTLY MEASURING THE PROMPT, NOT THE PAPER.** They were reported at
the time as evidence of convergence. They were weaker evidence than that: the instrument was not
looking for this class. ⚠ **A "0 majors" round is only as strong as the categories the reader was
asked to check** — which is an argument for widening a brief when a new class appears, and against
reading a clean round as a property of the document.

The class is also structurally hard to see linearly: §3's universal contradicts §2.6 four pages back,
and only a reader holding both at once catches it. The copy-editor brief — *follow every
cross-reference to see whether the target says what the pointer promises* — found two of the three;
the scope-list screener found one.

⭐ **SO THE CLASS IS NOW BEING AUDITED EXHAUSTIVELY RATHER THAN SAMPLED.** The body carries **251**
sentences with a universal or counted quantifier (104 "every", 94 "all", 48 "none", and the rest).
A dedicated agent checks every one against the rest of the manuscript and its tables, with each
finding required to quote the text that contradicts it. That converts "how many more are there?"
from a worry into a number.

##### ⭐ THE AUDIT RAN, AND THE NUMBER IS SIX (2026-08-19)

**AUDITED: 251 universal/counted claims examined, 6 findings** — two CONFIRMED CONTRADICTIONS, three
NARROWER-THAN-STATED, one UNSUPPORTED. All six are fixed. Every one was a scope defect rather than a
wrong number: the arithmetic held in all six, which is why no numeric test had ever fired on them.

| # | severity | where | the open quantifier | what it actually covered |
|---|---|---|---|---|
| 1 | contradiction | §2.10, Table 4 caption | ΔΔG°37 is the margin over "the best duplex **either parent can form**" | the generator scores only the two **seam** runs, ≤10 bp by the paper's own identity; 87 designs pair a mature parent at ≥10 bp elsewhere |
| 2 | contradiction | §4.3, §5 | "falls outside **every parent count**" / "**Every parent count** requires the gap paired in full" | the hit is sense-strand, intron–exon-spanning, one gap mismatch short — inside §2.5's 53, forty and 21. §5 named "the 21 designs of §2.5" as a count in the sentence denying such counts exist |
| 3 | narrower | §2.9 | "**the** 16-mer surviving at that junction" | two survive at *TCF12* exon 7, returning three and two |
| 4 | unsupported | §4.4 | the margin arm, "and **only** at *EWSR1* exon 12" | defended against *TAF15* exon 6 alone; Table 2 shows 3-of-5 and 4-of-5 at the other two §4.1 junctions |
| 5 | narrower | §2.7 | "The genome scan, screen 5, **removes that bound**" (of both classes) | screen 5 runs at ≤2 mismatches; an 11–12 bp run inside a 16-mer carries 4–5, so the mature-duplex class stays bounded |
| 6 | narrower | §5 | "**Every** screened count outside §2.9 is for one architecture" | §4.2 and Table 5 both print 5-8-5 counts |

**★ A SEVENTH AND AN EIGHTH WERE FOUND BY THE INSTRUMENT, NOT THE AUDIT.** Converting the class into
[`test_universal_claims_are_scoped_to_what_was_measured.py`](../tests/test_universal_claims_are_scoped_to_what_was_measured.py)
fired immediately on §5's *"**Every parent count** — 87 of 190, 61 of them against wild-type NR4A3 — is
taken at a contiguous duplex of ten base pairs"*, which the 251-claim audit had not flagged. That is the
argument for the instrument over the audit: **the audit is a sample of one reader's attention; the test
runs on every build.**

The **eighth** came from generalising that same governs-the-noun pattern by hand across the paper's
other counted nouns (*screen*, *design*, *criterion*, *duplex*, *site*, *register*, …) — 877 sentences,
103 candidates, 102 correctly scoped and one not: §6 excluded the six parent genes' records from
*"**every near-match count** reported here"*, while §2.5 opens *"Of the 190 designs, **53 have a
near-match somewhere in parent pre-mRNA**"*. The exclusion belongs to screen 1; screen 3's near-match
counts **are** counts of parent sites. ⚠ **Both late finds were in the same sentence shape the audit
was built to catch** — which is the measure of how thin the audit's coverage of one reading actually is.
Nine guards now hold the corrected scope of all eight.

⚠ **AND THE FIRST DRAFT OF THAT GUARD OVER-FIRED.** Its regex matched any universal ANYWHERE in a
sentence containing "parent count", so it flagged the corrected form ("the mature-parent counts … so
**each** is a floor"). It was narrowed to require the quantifier to GOVERN the noun — then re-checked
against all three original defect strings, which it still catches. Narrowing a check until it passes is
the failure mode; narrowing it and re-proving it on the defects it exists to catch is not.

#### Round 12 — the first round run under this condition, and what it filtered

Two readers, same build, different briefs (one a bioRxiv screener working a scope list, one a
copy-editor reading for sense), neither seeing the other. Between them they raised **two majors and
five distinct minors. Exactly one minor was raised by both.**

| finding | reader A | reader B | action |
|---|---|---|---|
| "clean" carries four senses in §2.6 | MAJOR | — | FIXED — a major stands on one reader |
| Methods says the longer geometries went through "the same screens" | — | MAJOR | FIXED — a major stands on one reader |
| "Two of those three sources" followed by a three-item list | MINOR | MINOR | **FIXED — the overlap** |
| Figure 2 not standalone-readable without §2.2's correction | MINOR | — | FIXED |
| "shown to be sufficient and not to be necessary" | — | MINOR | FIXED |
| Declarations enumeration misses the five non-panel designs | — | MINOR | FIXED |

⚠ **ALL THREE SINGLE-READER MINORS WERE SUBSEQUENTLY FIXED**, under the corrected reading of this
condition. They are listed as "held" above only because that was their status for the hour between
the round landing and the correction. Nothing from round 12 is unrepaired.

★ **THE FILTER DID WHAT IT WAS ADDED TO DO.** Under the old rule all five minors would have been
fixed, and on the measured rate of this loop roughly one of those five repairs would have seeded the
next round's finding. ⛔ And the one that survived was itself a repair: the "two of those three
sources" sentence was written in round 11 to fix a DIFFERENT antecedent defect in the same sentence,
and both readers independently found the replacement worse than what it replaced. That is the
clearest evidence in this ledger for why single-reader minors are not worth chasing — and for why
the overlap is worth fixing.


**Every minor raised is fixed. The two-reader test is the STOPPING condition, not a filter on what
gets repaired:** the loop ends when a two-reader round returns no minor that BOTH readers raise.
A minor only one reader sees is still fixed; it simply does not, on its own, keep the loop open.

⚠ *Superseded, retained: this condition was first written as "a minor one reader raises and the
other does not is recorded and NOT fixed" — a filter on repairs. trimcrae corrected it the same
day: "You should still try to fix every minor that is raised. Just don't let a minor that isn't
shared by both agents block you." The distinction matters — under the first reading three real
observations would have been left in the deposit because only one reader happened to see each.*

⛔ **WHY, AND IT IS MEASURED RATHER THAN ARGUED.** Across nine screened rounds of both built formats:

| round | blockers | majors | minors |
|---|---|---|---|
| 3 | 1 | 3 | 8 |
| 4 | 0 | 0 | 11 |
| 5 | 0 | 1 | 8 |
| 6 | 2 | 1 | 5 |
| 7 | 0 | 0 | 7 |
| 8 | 0 | 0 | 5 |
| 9 | 0 | 2 | 6 |
| 10 | 0 | 0 | 5 |
| 11 | 0 | 0 | 4 |

Blockers and majors CONVERGED — zero of both in six of the last seven format-rounds. **Minors did
not.** They oscillate between 4 and 7 with no trend that survives the noise, and the mechanism is
visible in the ledger: **roughly one finding per round was created by the previous round's fix**
(round 6's blocker, round 7's fragment, round 8's all-caps emphasis, round 9's precedent major,
round 11's "the two reagents"). The screener finds ~4, the repair introduces ~1, and the count sits
at a fixed point. That is a sampling rate, not a defect count.

★ **THIS IS WHAT §1 ALREADY PREDICTED**, and the prediction is now quantified rather than asserted:
"the same model family, reviewing the same document, with the same blind spots, will keep returning
findings for as long as it is asked to." Chasing single-reader minors is an indefinite loop whose
marginal finding was, by the end, a gene abbreviation left unexpanded and a source set not announced
as three.

⚠ **THE CRITERION WAS FIXED BEFORE THE ROUND THAT TESTS IT.** Written while round 12's two readers
were still reading and their findings were unknown — a stopping rule chosen after seeing the data is
not a stopping rule. Both readers get the same build and neither sees the other.

⚠ **THIS RELAXES NOTHING ABOVE MINOR.** A blocker or a major from EITHER reader is actionable on its
own; the two-reader test applies to minors only, which is exactly the class that stopped converging.


**Deposit when all six hold.** ⚠ *Superseded, retained: "all five", and before it "all four" — condition 6 was added 2026-08-19 after the minor count was measured across nine rounds and found not to converge; condition 5 was added 2026-08-17 after conditions 1-4 all held and an outside screen of the built PDF found a wrong-reagent hazard none of them could see.*

1. **Every P0 and P1 item has a recorded disposition** — applied, declined with a stated reason, or
   refuted with evidence. **Zero OPEN.** A deferred item is only permissible where its trigger is
   named and outside this repository's control (see §4).
2. **Every gate is green**, including `PREFLIGHT_FULL=1` and all four generated-artifact `--check`
   modes (`submission_tables.py`, `submission_citations.py`, `submission_metrics.py`,
   `aso_archive_manifest.py`).
3. **One firewalled cold reader** — given the three documents and nothing else, no history, no diff,
   no plan — **returns nothing above `minor`.**
4. **One adversarial reviewer with artifact access**, explicitly permitted to report that it found
   nothing, returns findings that are all either refuted or already in the ledger.
5. **⭐ ONE BLIND SCREEN OF THE BUILT PDF** — the artifact a depositor actually uploads — returns
   nothing above `minor`. **Added 2026-08-17, and it was earned the expensive way.** Conditions 1–4
   were all met, this rule declared the paper deposit-ready, and an outside screen of the PDF then
   found a **wrong-reagent hazard**: table sequences printed with no `5′-`/`-3′` delimiters against a
   numeric cell, so one extractor returned a 16-mer carrying a trailing digit. Nothing in conditions
   1–4 could have seen it, because **every seat read the Markdown** and the defect is created by
   typesetting.
   ⛔ **The lesson is not "add a reader", it is that VERIFYING A SOURCE AND INFERRING THE DELIVERABLE
   IS FINE is the inference this repository forbids everywhere else.** A PDF is derived, and a
   derivation can change what a sequence *is*.
   ⚠ The screen must cover, at minimum: the text layer as a reader copy-pastes it; display-item
   numbering against citation order; what the front matter looks like to a screener skimming it; and
   whether anything a laboratory would order from survives extraction intact. The standing instrument
   is `tests/test_pdf_text_layer_is_orderable.py`, which asserts the document's property rather than
   one extractor's behaviour — ⛔ because the fusion is **extractor-dependent**, and a guard written
   against the tool that happened to be at hand would have gone green on a corrupting document.
   ⛔⛔ **BOTH BUILT FORMATS, SCREENED SEPARATELY, AND THE SCREEN RE-RUN AFTER EVERY FIX ROUND**
   (added 2026-08-17, second revision). Two things were learned the same way the condition itself
   was. **First, one format is not the other document.** The build emits a journal typesetting and a
   submission-format manuscript from the same sources; page geometry differs, so float placement,
   page breaks and what a caption sits beside all differ. A round that screened only one returned six
   minors the other did not have, and a later round's blocker — a caption misstating the architecture
   of a named oligonucleotide — was visible in the manuscript format and not the journal one.
   **Second, a fix round is a new document and needs its own screen.** The blocker just described
   was CREATED by the previous round's remedy for a different finding: a chemistry clause written
   for the all-5-6-5 tables, pasted onto two tables whose subject is that the geometry varies. A
   screen that ran before the fixes cannot see the fixes' own defects, and "we already screened it"
   is the inference that let it through.

### Why those seats specifically

- **The cold reader was the highest-yield seat in round 7.** It found that `gap-level margin` — the
  statistic the entire ranking rests on — is first used at character 9,605 and defined at 92,817, and
  that "EMC" is never defined at all. Every reviewer carrying memory of the older draft read straight
  past both. A reader with no context is the only instrument that can see this class.
- **The permission to find nothing is load-bearing.** It produced a real result twice. Without it the
  seat manufactures an objection, because a reviewer asked for findings supplies findings.

### ⭐ CONDITION 7 — WHAT GETS ADMITTED TO THE BACKLOG, AND WHY IT IS NOT A VOTE (added 2026-08-19, trimcrae)

trimcrae, on the 2026-08-19 round: *"we need to start being more judicious about which reviewer
reported 'defects' we actually add to our backlog if you think the reviewers are just padding to
fill a quota."* The premise was mine and it was WRONG, so the rule that comes out of it is not the
one the question implied. Recorded here because the wrong version is the tempting one.

**THE PADDING HYPOTHESIS DOES NOT SURVIVE ITS OWN LEDGER.** Nine briefs returned 236 deduplicated
entries and 176 of them were raised by exactly one reader, which I reported as mostly noise. Measured
against the ledger instead of asserted:

| class | n | what it actually is |
|---|---|---|
| single-reader **with** a recomputation behind it | 132 | a reviewer computed a number; reader count says nothing about whether it is right |
| single-reader, no number, **guard-suite** | 12 | the most verifiable class in the ledger — each is a code fact, and all twelve were proved by construction and fixed |
| single-reader, no number, non-numeric **claim** | 15 | checkable against the text or an artifact; not numeric is not unverifiable |
| single-reader, no number, **taste** | 11 | the only genuinely discretionary class |

So the volume came from BREADTH OF BRIEF, not from quota-filling, and an admission filter keyed on
reader count would have discarded ~132 findings whose backing is a computation. ⛔ **Reader count is
the STOPPING test (condition 6). It is not, and must not become, an ADMISSION test** — those are
different jobs, and the second one is how a measured defect gets thrown away for being unpopular.

**THE GATE IS VERIFICATION, NOT POPULARITY.** Every finding is recomputed before it is applied; one
that fails is recorded REFUTED with the numbers that refuted it. On this round that gate rejected
eleven findings, including one filed as a BLOCKER — and it rejected two of my own repairs. That is
the filter doing the work an admission rule was being asked to do, and it is the right one, because
it asks whether the finding is TRUE rather than whether it is POPULAR.

**WHAT IS DECLINED, AND IT IS A SMALL SET.** Eight entries, each with its reason recorded beside it:
placement and ordering preferences; two whose fix would need a source this repo has not retrieved,
so writing it would mean inventing one; one thirteen-page structural rewrite whose cost is far above
its defect; and — ⛔ **on safety grounds rather than cost** — thinning the repeated order-safety
footer, which would trade a real hazard against a cosmetic one.

⚠ **THE COST THAT JUSTIFIES DECLINING ANYTHING AT ALL IS MEASURED, NOT ASSUMED**: this ledger records
roughly one finding per round CREATED by the previous round's repairs, and this session created two
of its own. Repair is not free, which is why a taste-class item with no measurement behind it is
worth declining — and why a measured one never is, however few readers saw it.

### ⭐ CONDITION 8 — CORRECTNESS GATES THE DEPOSIT; IMPROVEMENT DOES NOT (added 2026-08-19, trimcrae)

trimcrae, on the 2026-08-19 round, with the ledger showing 40 open defects beside 38 open
improvements: *"I don't want you chasing improvements that expand the scope. If we do that, we'll
never submit. We have to make sure what we post is correct."*

**THE LEDGER IS SPLIT AND ONLY ONE HALF GATES.** A finding blocks the deposit if, and only if, it is
one of these:

| gates | does not gate |
|---|---|
| a statement that is **wrong as printed** | an omission — something true the paper could also say |
| a claim **wider than the measurement** supports | prose that is thin, unclear, or better organised another way |
| an assertion with **no retrieved source** | vocabulary carrying more than one sense where nothing printed is wrong |
| a **pointer** that sends a reader where the thing is not | layout, label size, ordering, legibility |
| an **order-safety** defect — a condemned sequence without its verdict, a marker without its key, a near-twin without its warning | a table column that is undefined but not misdescribed |
| a **guard that cannot fail**, or that has never run | a guard that could be stronger |
| a **stale deposit artefact** — a PDF, manifest or metric that no longer matches its sources | — |

⛔ **THE RIGHT-HAND COLUMN IS NOT DISMISSED, IT IS PARKED.** Each entry keeps its recorded finding
and its proposed fix. **A preprint is revisable — that is why this venue was chosen (§3)** — so an
improvement costs nothing by waiting and costs real risk by being made now, because this ledger
measures roughly one NEW defect for every round of repair, and five were introduced by the
coordinating session in this round alone.

⚠ **THE TRAP THIS CLOSES.** The two classes were being reported as one number, which made a
repairable paper look like a broken one and made "how much is left?" unanswerable — 236 findings of
which 47 were never in the paper at all. Worse, an improvement queue has no natural end: every
reader supplies more, the marginal one gets smaller, and the deposit recedes. Correctness has an
end, and it is the only half that can make a posted paper wrong.

★ **THIS DOES NOT LOOSEN CONDITIONS 1–6.** A blocker or a major from any reader is still actionable
on its own; the overlap rule still governs when review STOPS; every finding is still recomputed
before it is applied and recorded REFUTED with numbers when it fails. What changes is which half of
a dispositioned ledger has to reach zero before the deposit goes.

## 3 · ⚠ The corollary, which must not be flinched from

**If the final round returns a class-B finding — a real defect in text no prior round touched — that
is NOT a reason to run another round.**

It is evidence that this method has a floor above zero, which is already known. The correct response
is: record the finding, fix it, and **deposit anyway.**

A preprint is revisable. That is what preprints are for, and it is the reason the author chose a
preprint over journal submission. Treating a bioRxiv deposit as though it were irreversible imports
exactly the cost model the venue exists to avoid.

⛔ **The one exception, stated so it cannot be stretched:** a finding that would make the paper's
*headline* false — 87 of 190, 61 against wild-type *NR4A3*, or the claim that a longer catalytic gap
cannot separate them — stops the deposit regardless of what this rule says. Nothing else does.
Round 7's B5-F1 is the worked example of the boundary: it invalidated an *apportionment label* and
left the headline untouched, so it was a fix, not a stop.

## 4 · What will still be open at deposit, and is stated rather than hidden

- **No reviewer in seven rounds has been a wet-lab scientist who has run one of these experiments.**
  Every bench perspective is simulated. This is the largest gap in the review history and **no amount
  of further simulated review closes it.**
- **Same method, same model family, same blind spots.** A quiet round is weak evidence that the paper
  is good and strong evidence only about what this method can see.
- **Four venue-triggered P3 items stay deferred** by the author's decision to target bioRxiv, which
  has no length cap and no IMRaD template. Each names the trigger that reopens it.
- **Anything the CI fetches could not reach** is marked UNVERIFIED. Never guessed.

## 5 · The three things only the author can supply

These are not review findings and no round can close them.

1. An **ORCID** — the manuscript carries `ORCID: [to be inserted]`.
2. A **reserved archive DOI**. The checklist requires reserving it *before* publishing the deposit, so
   the manuscript cites the DOI it will have. Two `[ARCHIVE DOI]` placeholders await it.
3. **The go-ahead to post.** Outward-facing and irreversible, and therefore a human's call.
