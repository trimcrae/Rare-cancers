---
id: DOC-ASO-GUARD-COVERAGE-AUDIT-2026-08-27
title: "Guard-coverage audit of the ASO journal article — 34 of 42 single-sentence mutations shipped green, and not one claim is held by a linter"
level: L3
kind: manuscript
status: live
canonical_for:
  - the round-10 guard-coverage audit of the fusion-junction ASO journal article
purpose: >
  A blind seat asked one question of every load-bearing sentence in the ASO journal article: WHAT
  READS THIS? It answered by mutation — invert or delete the sentence, run the full manuscripts suite
  and all five linters, attribute every failure. This is its verbatim return. It is a map of what the
  repository's gates actually bind, and it is mostly a map of what they do not.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence. Every sequence named is a research reagent for laboratory
  investigation only and must not be administered to any person or animal.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-27
last_verified: 2026-08-27
---

# Guard-coverage audit — ASO journal article at pin `df2bc4b02`

**Method.** 42 single-sentence mutations against the pinned article, each run through the full
`research/manuscripts/tests` suite (baseline `1287 passed, 3 skipped`) plus `lint_claims`,
`lint_consistency`, `lint_citations`, `lint_style` and `lint_readability`. Every failure attributed
by single-mutation re-run. Staleness catches (build stamps, docx, page budget) are excluded from
coverage — a control confirmed they fire on any reword, so they measure freshness, not meaning.

**The two headline numbers.** **34 of 42 mutations shipped green.** **All five linters returned rc=0
on all 42** — not one claim in this paper is held by a linter; everything that binds is a test module,
and a single module accounts for six of the eight catches.

⛔ **THIS AUDIT CAUSED AN INCIDENT AND IS THE REASON THE RULE EXISTS.** Its first two batches mutated
the SHARED working tree. A commit ran inside that window and pushed 13 inverted claims to `main`
(restored at `b4f086c73`; the article now hashes to the pin). Later batches used a detached
`git worktree`. **The rule is CLAUDE.md §6: a mutation-testing agent works on a copy, never the live
tree; while any subagent runs, stage by path and never `-A`; and diff the paths you did not touch
before every commit.** The seat's own words: *"mutation testing must never use the shared working
tree."*

---

DIGEST_VERIFIED: yes — `sha256(research/manuscripts/aso/fusion-junction-aso-journal-article.md)` = `6be28cc10d72eb36ea04eae0bee110ab422495c9e512f2337932711a60ec8238` at pin `df2bc4b02`, 4,613 words.

VERDICT: 42 single-sentence mutations run against the full manuscripts suite plus all five linters; **34 of 42 shipped green**, including every operative sentence in Statements and Declarations, the AI-use citation-provenance sentence, the do-not-substitute reagent warnings and the Figure 1 legend — and the one guard written specifically to catch deletion of the synthesis denial is satisfied by a *generated table caption*, not by the paper.

⛔ FIRST, AN INCIDENT I CAUSED AND WHICH IS ALREADY REMEDIATED. My first two mutation batches were applied in place in `/home/user/Rare-cancers` and restored afterwards. A concurrent session committed and pushed `748c1f024` **inside that window**, sweeping 31 inverted lines of the manuscript onto `origin/main`. The driver caught it and restored at `b4f086c73` ("INCIDENT: restore 13 inverted claims I pushed to main from a subagent's mutation window"); `HEAD` is now correct and the working tree is clean (`git status` = 0 entries, article sha = the pin). Every mutation after that point ran in a detached `git worktree` under the scratchpad, both of which I have removed. **The lesson for the next seat: mutation testing must never use the shared working tree.**

Method: baseline at the pin = `1287 passed, 3 skipped` (`research/manuscripts/tests`, 250 s) + `lint_claims/lint_consistency/lint_citations/lint_style/lint_readability` all rc=0. Each batch of mutations was applied together, the whole suite and all five linters re-run, and every failure attributed by single-mutation re-run. Build-stamp/docx/page-budget/census-count failures are *staleness* catches (they fire on a one-word reword too, verified by control) and are not counted as coverage.

---

## UNGUARDED

**1. The Declarations synthesis denial.**
SENTENCE: "Every sequence here is a research reagent for laboratory investigation only, and none has been synthesised or tested."
WHY_IT_IS_LOAD_BEARING: it is the scope bound on a paper that names two orderable 16-mers. Inverted, the paper claims wet-lab work this project has never done; deleted, it reads as a wet-lab report.
WHAT_I_SEARCHED: `research/manuscripts/tests/` (all 79 modules), `research/modalities/tests/`, `lint_*.py`. The only instrument that names the subject is `test_the_paper_states_what_its_own_claims_depend_on.py::REQUIRED["that nothing was synthesised or tested"]`, pattern `has been synthesi[sz]ed|nothing (?:here )?(?:has been|was) synthesi[sz]ed`, evaluated over the built PDF's text layer.
MUTATION_I_RAN: (a) inverted to "…and each has been synthesised and tested" (batch 2, full suite); (b) **deleted the clause outright** in a worktree, rebuilt the real PDF (`build_submission_pdf.py --paper aso-journal --style journal`, `BUILD_RC=0`), re-ran the module.
RESULT: (a) green everywhere — 5 linters rc=0, no content guard fired. (b) `10 passed` on the REQUIRED rows including this one. See MISCOVERED A for why.

**2. The AI-use citation-provenance sentence.**
SENTENCE: "Every reference's bibliographic record was retrieved from PubMed rather than written from model output, and each citation was checked against the retrieved record."
WHY_IT_IS_LOAD_BEARING: this is CLAUDE.md §7's core invariant stated to the reader. Inverted it admits fabricated citations; deleted, an AI-written paper ships with no provenance statement. `lint_citations` checks PROVENANCE of identifiers, not this sentence's existence.
WHAT_I_SEARCHED: `grep -rn "retrieved from PubMed"` over the repo → zero hits outside the manuscripts. The nearest guard is `POLARITY["ai-use"]` in `test_the_manuscript_asserts_the_relation_its_artifacts_compute.py`, span `\*\*Use of artificial intelligence\.\*\*[^#]{0,140}`.
MUTATION_I_RAN: inverted to "…written from model output rather than retrieved from PubMed, and no citation was checked against a retrieved record."
RESULT: green. Measured: the span ends 174 chars into the section; this sentence begins at offset 244. The window is 70 characters short — the same "a window is a disguised list" failure that file's own `liability-predicate` comment records.

**3. "All analyses are computational and use public data; no laboratory work was performed."** (Methods, first sentence)
WHY_IT_IS_LOAD_BEARING: the paper's no-wet-lab scope, stated where a Methods reader looks for it. The abstract's companion sentence *is* guarded (REQUIRED row `work is computational…not for administration`); this one is one of the pair.
WHAT_I_SEARCHED: `test_the_paper_states_what_its_own_claims_depend_on.py`, `SAFETY_CLAUSES`, `lint_claims` R1–R6.
MUTATION_I_RAN: → "Analyses are computational and experimental and use private data; laboratory work was performed."
RESULT: green (full suite + 5 linters).

**4. Three of the four Declarations statements.**
SENTENCES: "**Consent to participate.** Not applicable. No participants were enrolled." · "The manuscript contains no data from any individual person." · "**Funding statement.** No external funding; self-funded by the author."
WHY_IT_IS_LOAD_BEARING: each inverts into a fabricated human-subjects or funding claim in a submitted document. `SAFETY_CLAUSES` covers exactly two clauses (no-administration, no-human-subjects); these three sit beside them and nothing reads them.
WHAT_I_SEARCHED: `grep -n "funding\|participants\|individual person\|consent" research/manuscripts/tests/*.py research/manuscripts/lint_*.py` → three hits, all comments.
MUTATION_I_RAN: "Participants were enrolled." / "The manuscript contains data from individual persons." / "External funding was received by the author."
RESULT: all green. (The funding line produced one `test_the_submission_uploads_are_individual_files` failure — a *cut-vs-typed* staleness check against the pre-built title-page docx, not a claim check; it fires identically on any reword.)

**5. The requirement that makes an undecided acceptor safe.**
SENTENCE: "the breakpoint of the test article must be established at nucleotide resolution by RNA sequencing before any oligonucleotide is ordered, every design here being specific to the exon pair it was tiled at."
WHY_IT_IS_LOAD_BEARING: `test_the_exon2_reading_stands_without_an_unpublished_sequence.py`'s own docstring names it as property (4) of four, and trimcrae's 2026-08-25 ruling not to gate the paper on an unpublished junction sequence rests on it.
WHAT_I_SEARCHED: that module; `POLARITY["order-after-sequencing"]` (anchored on the *Declarations* copy, `Order from the canonical record…sequencing\.`).
MUTATION_I_RAN: → "need not be established at nucleotide resolution by RNA sequencing before an oligonucleotide is ordered, no design here being specific to the exon pair it was tiled at."
RESULT: green — including `test_the_breakpoint_must_be_sequenced_before_anything_is_ordered`, the guard written for it. See MISCOVERED E.

**6. "Neither may be substituted for the other."** (the one-base-slide condemned design, §2)
WHY_IT_IS_LOAD_BEARING: it sits directly after `5′-AGGGCATATCTTGTGT-3′`, one slide from the *TAF15* reagent and paired at 11 bp through its whole gap. Inverted, the paper tells a laboratory it may order the condemned molecule.
WHAT_I_SEARCHED: `test_every_ordering_route_carries_the_same_verdict.py`, `test_condemned_designs_are_absent_from_the_tables.py`, `test_named_reagents_carry_the_acceptor_the_csv_gives_them.py`, `POLARITY`.
MUTATION_I_RAN: → "Either may be substituted for the other."
RESULT: green (full suite; and `63 passed` on the five ordering/reagent modules run alone).

**7. "Neither reaches the ten-base-pair criterion"** (the two exon-2 reagents, §4).
WHY_IT_IS_LOAD_BEARING: it is the disclosure that the reagents the paper offers for the cell models' reported acceptor do *not* clear its own cut — "a closer call than either exon-3 reagent presents".
MUTATION_I_RAN: → "Both reach the ten-base-pair criterion…" RESULT: green. (`POLARITY["named-reagents-clear-the-cut"]` binds only the §2 exon-3 pair.)

**8. The Figure 1 legend's two scope sentences.**
SENTENCES: "…only one of the three is a junction any patient is reported to carry." · "No reagent is named at it."
WHY_IT_IS_LOAD_BEARING: the legend shows a 16-mer spanning *EWSR1* e12, *TAF15* e11 and *FUS* e10. Without "No reagent is named at it", the exon-11 row reads as orderable; inverting the first turns three mostly-unreported junctions into reported patient junctions.
WHAT_I_SEARCHED: `test_aso_figure_provenance.py`, `test_aso_figure_chain_is_complete.py`, `test_figure_text_carries_no_markdown.py`, `test_display_items_are_cited_in_order.py` — all check provenance, rendering or ordering, none the legend's claims.
MUTATION_I_RAN: → "A reagent is named at it." and "…all three are junctions patients are reported to carry."
RESULT: both green.

**9. "It is not named for synthesis"** (the third design, `5′-GGGCATATCTCCACGG-3′` at *EWSR1* e13).
WHY_IT_IS_LOAD_BEARING: the paper prints a third orderable sequence and this clause is the only thing keeping it out of the order. `_synthesis_reagents()` in `test_the_unbound_claims_the_coverage_census_found.py` reads "The **two** reagents named for synthesis are…(Table 1)" and counts two — a sentence this mutation does not touch.
MUTATION_I_RAN: → "It is also named for synthesis: …the selection above takes the first three." RESULT: green.

**10. "Three designs clear every screen applied here, none at a junction any patient is reported to carry, which makes them mechanism controls rather than candidates."**
WHY_IT_IS_LOAD_BEARING: it is the sentence that stops the three clean designs reading as the paper's best candidates.
MUTATION_I_RAN: → "…each at a junction patients are reported to carry, which makes them candidates rather than mechanism controls." RESULT: green.

**11. The cell-model identity and availability facts.**
SENTENCES: "USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2 (RRID:CVCL_C6MY)" · "They are available on request with no repository deposit, and are slow, at reported doubling times of five to six days."
WHY_IT_IS_LOAD_BEARING: RRIDs are how a laboratory obtains the only fusion-positive EMC cells identified; a swap sends it to the wrong line, and the availability/doubling-time facts price the whole test-article route.
MUTATION_I_RAN: swapped the two RRIDs; and "available from a public repository on deposit… one to two days."
RESULT: both green. `research/modalities/emc-test-article-routes.json` holds these facts and nothing joins the paper to it.

**12. The hepatotoxicity premise.**
SENTENCE: "High affinity is taken to carry a risk of sequence-dependent hepatotoxicity; that is a premise adopted here rather than a retrieved finding, and nothing here measures it."
WHY_IT_IS_LOAD_BEARING: the only toxicity statement in the paper, and its hedge is what keeps it from being a safety claim (CLAUDE.md §1 language discipline, `lint_claims` R1–R5).
MUTATION_I_RAN: → "High affinity is measured here to carry a risk…that is a retrieved finding rather than a premise adopted here, and this work measures it." RESULT: green, `lint_claims` rc=0 included.

**13. The novelty/priority pair.**
SENTENCES: "no survey of design pipelines was performed, so the screen-before-synthesis claim is about this literature as retrieved and not a priority claim." · "The method-level novelty is nil: junction-directed oligonucleotides are long established."
WHY_IT_IS_LOAD_BEARING: `lint_claims` R6 exists *because* of exactly this class (trimcrae 2026-08-15, "we're claiming we invented it?"), and the second sentence is quoted verbatim inside R6's own comment as the working-record evidence.
MUTATION_I_RAN: → "a survey of design pipelines was performed, so the screen-before-synthesis claim is a priority claim…" and "The method-level novelty is high: junction-directed oligonucleotides are newly established."
RESULT: green. R6's regex requires `standard|common|…\s+practice` + a negation, or `screens|pipelines|…` + `routinely` + `exclude|omit|…`; tested directly against the inverted sentence → `False`. R6 catches the *negative* generalisation and not its positive twin.

**14. The two "this is a prediction, not a measurement" qualifiers.**
SENTENCES: "Both loads are predictions from sequence search rather than measured activity." · "That is not a locked phosphorothioate oligonucleotide, so no absolute melting point is reported."
WHY_IT_IS_LOAD_BEARING: the first converts "123 gap-paired near-matches … against eight" from a search result into an activity measurement; the second is what stops the Tm being read as the reagents' own.
MUTATION_I_RAN: inverted both. RESULT: green. ("absolute melting point" appears in `aso_journal_tables.py` as a *caption constant* — the tables file asserts it, the manuscript's copy is unread.)

**15. The statistics-honesty cluster (7 sentences, all green).**
· "Each null rate is 38,000 draws with a Wilson 95% interval." → "380 draws with a normal-approximation 95% interval". (`38,000` appears in `test_journal_article_numbers.py` only inside a comment, which is why the census credits that module and nothing binds the number.)
· "The range 39.9% to 82.8% quoted with it is not a confidence interval and carries no nominal level" → "is a confidence interval and carries a nominal level".
· "A design whose gap carries a mismatch is scored zero rather than short, so the 87 bound the fully-paired class, not the whole parent liability." → reversed.
· "Neither restates the other, and their counts may not be added: a design condemned in both is one design." → "Each restates the other, and their counts may be added…two designs."
· "Second, most designs clean at the default search ceiling are not clean at a deeper one." → "are also clean".
· "At eight, both fall inside the class this work marks as not to be ordered; at nine, the *TAF15* reagent alone does; only at ten does neither." → reversed.
· "those partial duplexes are not counted here and have not been measured" → "are counted here and have been measured".
WHY_IT_IS_LOAD_BEARING: every one converts a stated bound into a stated result while leaving every number in the paper arithmetically correct. WHAT_I_SEARCHED: `pinned-figures.json` (19 pins home to this article — all bind *values*, none bind these predicates), `test_journal_article_numbers.py` (12 tests, all quantity-checks), `test_the_printed_cut_ladder_is_the_measured_one.py`. RESULT: all green.

**16. The scope-of-work claims (4 sentences, all green).**
· "This work performs the in-silico half of the first step and stops there" → "performs all five of those steps and stops nowhere".
· "…none 3′ of exon 3, so nothing is designed there because no patient is reported there." → "several 3′ of exon 3…although patients are reported there".
· "Its 38 junctions were graded for a fusion protein, so an acceptor upstream of the *NR4A3* initiation codon was dropped as non-coding." → "graded for a transcript…was retained as coding".
· "a complementary DNA over-expressed in a heterologous background speaks to junction-selective knockdown of the intended transcript, not to activity at an endogenous locus." → reversed.
· "Every source of a test article named here ends at someone culturing cells." → "reaches an animal model of the disease." (`grep -rn "culturing cells"` → zero hits in any guard.)

**17. "This work's own withdrawn version arose from an error of exactly this class."**
WHY_IT_IS_LOAD_BEARING: the in-text acknowledgement of the withdrawal; the Data availability copy is its pair, and neither is bound.
MUTATION_I_RAN: → "This work's own earlier version was never affected by an error of this class." RESULT: green.

---

## MISCOVERED

**A. `test_the_paper_states_what_its_own_claims_depend_on.py::REQUIRED["that nothing was synthesised or tested"]` — the branch is satisfied by a generated table caption, and the manuscript's own sentence is invisible to the fixture.**
The fixture reads the built PDF's pdfminer text. In that text there is exactly **one** match for the row's pattern: `"Nothing here has been synthesised or tested, and no sequence may be administered to any person or animal"` — the Table 1 caption constant at `research/manuscripts/aso_journal_tables.py:194`. The manuscript's own clause does **not** appear as a match at all: two-column typesetting scatters it, so the extracted text reads `"…and none has been record, fusion-junction-aso-sequences.csv, … by RNA sequencing. tested. Order canonical"` (`t.count("none has been synthesised") == 0`).
MUTATION_I_RAN: deleted the manuscript clause outright in a worktree, rebuilt the real PDF (`BUILD_RC=0`), re-ran the module.
RESULT: **green** — `test_the_article_states_it[that nothing was synthesised or tested]` passed on a paper that no longer says it. Two independent defects: the alternation's weaker branch is owned by a different file, and the row could not bind the manuscript sentence even if that branch were removed. Second-order: the row was tightened on 2026-08-27 *precisely* to stop `not for administration` satisfying it from elsewhere — the same fix was not applied to this branch.

**B. Same file, `REQUIRED["where the artefacts are"]`, pattern `zenodo|doi:`.** The reference list is spliced into the PDF and carries 22 `doi:` strings; the delivered text yields 24 matches, 22 of them publisher DOIs. The row therefore cannot fail while a reference list exists. Evidence is match-count on the delivered PDF, not a green mutation — deleting the Zenodo pointer *is* independently caught by `test_aso_deposition_doi_is_one_fact.py` (I watched that go red), so the claim survives; the row itself binds nothing.

**C. Same file, `REQUIRED["the threshold the falsification experiment turns on"]`, pattern `cut of \d|threshold`.** `threshold` matches the Abstract's "a pre-registrable selectivity threshold" and §4's "The threshold is defined on the acceptor parent alone", so the §5 decision rule could be deleted with the row green. Residual only: `test_the_falsification_cut_is_the_stated_value` (added 2026-08-27, reads the `.md`) pins `cut of 5\.0` and does bind it.

**D. `test_aso_deposition_doi_is_one_fact.py::test_no_archive_doi_placeholder_survives_in_the_article` and `::test_both_availability_statements_carry_it` — one of a pair, in the file whose own comment records that class.** `ARTICLES` was widened to both papers for the first function; `ARTICLE = ARTICLES[0]` (the extended report) is still what these two read.
MUTATION_I_RAN: shipped `[ARCHIVE DOI — PLACEHOLDER: this citation does not resolve]` in the journal article's Methods while leaving the real DOI in place.
RESULT: `3 passed`. An unresolvable placeholder ships in the submitted paper with the guard green. (Control: removing the DOI *and* adding the placeholder went red — but on the *other* function, for the missing DOI, not the placeholder.)

**E. `test_the_exon2_reading_stands_without_an_unpublished_sequence.py::test_the_breakpoint_must_be_sequenced_before_anything_is_ordered` — a keyword that survives its own negation, present twice.** The assertion is `re.search(r"established\s+at\s+nucleotide\s+resolution\s+by\s+RNA\s+sequencing", body)`. "need **not** be established at nucleotide resolution by RNA sequencing" still matches, and the Declarations copy matches independently.
MUTATION_I_RAN: mutation 5 above. RESULT: green — the guard named as property (4) of the four that let this submission proceed without an unpublished junction sequence does not detect that property being inverted.

**F. `POLARITY["ai-use"]`, span `\*\*Use of artificial intelligence\.\*\*[^#]{0,140}`.** Measured at the pin: span ends at char 174; the citation-provenance sentence starts at char 244. Proven by mutation 2 (green).

**G. `test_universal_claims_are_scoped_to_what_was_measured.py` reads only the extended report.** `ARTICLE = …/fusion-junction-aso-research-article.md`; no journal-article path in the module. Its own docstring reasons about "the manuscript" and the class it polices (open quantifiers over a subset measurement) is live in the journal article. Proven by mutations 16 (`none 3′ of exon 3` → `several`; `Every source … ends at someone culturing cells` → `reaches an animal model`; "performs the in-silico half" → "performs all five") — all green in a run that included this module.

**H. Reported, not re-proved:** `research/modalities/tests/test_aso_submission_numbers.py` sets `PAPER` to the extended report alone, so the censoring derivation behind "seven of the 190 … leaving 47 of 183" is committed against the companion document only. `test_the_numbered_claims_no_instrument_read.py`'s docstring already states this; I did not mutate it.

---

## STALE_GUARD_TEXT

1. **`research/manuscripts/lint_style.py` (~line 115):** *"It is no longer a manuscript: the submission is `fusion-junction-aso-research-article.md`."* The extended report was removed from this gate's `TARGETS` on 2026-08-25 (trimcrae: "Remove any checks requiring it from the gate") and the comment 45 lines **above** says so — "the file stays in the tree as history". Two comments in one file describe two different regimes; the submission is the journal article.
2. **`research/manuscripts/tests/test_aso_abstract_is_bounded.py`, module docstring:** *"★ THE BOUND HERE IS THE DEPOSIT TARGET'S. bioRxiv sets no abstract word limit, so this is not a venue constraint."* The `JOURNAL_ABSTRACT_DRIFT_BOUND` comment 45 lines below states "NAT is the targeted venue". The docstring's deposit-target framing is retired, and its instruction ("IF A JOURNAL IS EVER TARGETED, replace this…") reads as unfired when the same file records that it cannot be followed because NAT's page returns 403.
3. **Same file:** *"The abstract stands at 227, so the bound buys one qualification and no more."* Measured at the pin by the file's own `_abstract()` splitter: **220**.
4. **`research/manuscripts/claim_coverage.py::ABLATION_BLOCKED_BY_A_KNOWN_FALSE_POSITIVE` and the `COVERAGE_FLOOR` note above it** — the regime is gone. The note says the fusion-partner manuscript "now reads 46 of 259 (46 of 192 numbered)"; the committed census reads **269 sentences, 77 covered, 201 numbered, 76 numbered-covered**, and the floor is still `1`. The exemption's stated cause is one sentence credited to `HTTP \d{3}`. MUTATION_I_RAN: reproduced the gate's own sampling (`SAMPLE=6`, even spacing over covered numbered sentences) and ran `claim_ablation.ablate` on each. RESULT: `applied=6 blind=0` — every sampled sentence goes red. The exemption removes a whole floored manuscript from `test_the_census_word_covered_survives_ablation.py` on a reading that no longer reproduces.
5. **Lower severity, flagged for completeness:** `test_the_unbound_claims_the_coverage_census_found.py`'s docstring cites "76 of 124 sentences … 47 of the 66 that state a number" against a live 82/174 and 53/81. It is explicitly labelled "its first honest run", so it is history rather than a stale assertion — but it is the only coverage figure a reader of that file meets.

---

## WHAT_IS_PROPERLY_BOUND

Eight of the 42 mutations went red, each watched:

| Sentence | Guard that caught it | Mutation |
|---|---|---|
| "Ten is a convention, not a measurement" (Abstract) | `test_aso_abstract_is_bounded.py::test_the_condensed_abstract_carries_the_two_scope_bounds_every_abstract_of_this_work_owes` — needle `a convention[^.]{0,60}not a measurement` | → "Ten is a measurement, not a convention" |
| "Most of the 123 are predicted transcript models rather than curated records…not a census of expressed transcripts" | `test_the_numbered_claims_no_instrument_read.py::test_most_of_that_load_really_is_predicted_models` | reversed the two halves |
| "…the report carries no sequenced exon-exon boundary, no transcript accession and no junction sequence…not decidable from what is published" | `test_the_exon2_reading_stands_without_an_unpublished_sequence.py::test_the_manuscript_says_the_published_report_carries_no_sequence` | all three negations flipped |
| "This is an inference and not a determination" | same module, `::test_the_parsimony_reading_is_labelled_an_inference` | → "a determination and not an inference" |
| "No such design is reported for any *NR4A3* fusion in the literature retrieved here" | `test_the_manuscript_asserts_the_relation_its_artifacts_compute.py` — 3 tests red (`no-prior-nr4a3-design` site, the main polarity check, and the positive-control) | → "No such design was needed…" |
| "Exon numbers throughout are transcript exon indices…including non-coding exons" | `test_the_numbered_claims_no_instrument_read.py::test_the_exon_convention_is_the_acceptors_own_model` | → coding-exon convention |
| "All five screens address hybridisation rather than cleavage, and none establishes that a predicted duplex forms or is cut" | `test_the_paper_states_what_its_own_claims_depend_on.py::test_the_article_states_it[that the screens address hybridisation, not cleavage]` | → "cleavage as well as hybridisation…each establishes"; **required a real PDF rebuild to fire** |
| "And systemic delivery to a solid tumour remains unsolved…" | same module, `[the delivery gate the modality still faces]` | → "systemic transport…is solved"; **also only after rebuild** |

Two notes on that table. The last two bind only through the built PDF, so an editor working in the `.md` sees nothing until the artifact is rebuilt — the stale-build-stamp guards do force that rebuild before a commit, so the chain holds, but the binding is indirect and the same indirection is what lets MISCOVERED A hide. And `test_the_manuscript_asserts_the_relation_its_artifacts_compute.py` is the only instrument in the repository that reads *verbs*; its 16 rows are the reason six of these eight caught anything, and the 34 unguarded sentences above are all outside those 16 spans.

Finally: **`lint_claims`, `lint_consistency`, `lint_citations`, `lint_style` and `lint_readability` returned rc=0 on all 42 mutations.** Not one claim in this paper is held by a linter; everything that binds is a test module.

Nothing in flight.