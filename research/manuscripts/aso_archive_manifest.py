#!/usr/bin/env python3
"""Derive the deposit manifest for the fusion-junction ASO submission. ($0, offline.)

⚠ *Superseded, retained: "the fusion-junction ASO short communication". The short-communication
    framing was withdrawn on 2026-08-15; the submission is a full research article. Neither the
    title nor the article type is restated here any longer — both have one home, the manuscript
    itself at research/manuscripts/aso/fusion-junction-aso-research-article.md, and a description
    that repeats them drifts the moment either changes.
    Round 5 found this string still saying "short communication" 186 commits after the retitle.*

⛔ WHY THIS EXISTS. The submission manuscript carries two unresolved placeholders — "[ARCHIVE DOI]"
in Methods -> Availability and "[ARCHIVE DOI]" in Declarations -> Data and code availability — and
around them two sentences that PROMISE a specific archive
contents: "All code, graded artefacts and per-design tables", and "the graded junction atlas,
per-junction design panels, both specificity screens per junction, the graded re-scores under both
discrimination bounds, and the retrieval records for every literature claim". Minting a DOI is an
outward-facing act only the repository owner can perform. Everything BEFORE that act — deciding
which files the promise names, proving each one exists, and pricing the upload — is not, and until
this module existed it was an unwritten job that would have been done by hand at the worst possible
moment: the hour of submission.

★★ A HAND-TYPED FILE LIST IS THE FAILURE THIS PREVENTS, NOT THE WORK IT SAVES. A deposit is the one
artifact a reader is invited to check the paper against, so a list that has quietly fallen behind
the repository is worse than no list: the reader finds a promised file missing and cannot tell
whether the analysis was withdrawn, renamed, or never run. Every path below is resolved by GLOB
from the promise it serves, so a screen added tomorrow enters the manifest without anyone
remembering to add it, and a screen deleted leaves a visible hole rather than a stale entry.

★★ AND THE GAPS ARE PART OF THE PRODUCT. A manifest that lists only what it found reads as complete
whether or not it is. The `gaps` block below is derived the same way as the file list — from the
artifacts themselves, never from a note — and answers the questions a reviewer would ask of the
availability statement: does every promise resolve to a file, does every screened junction actually
carry BOTH of the two screens the Methods claim, and does every screen that CAN be re-scored under
the two discrimination bounds actually have that re-score committed. Where the answer is no, the
manifest says so in the deposit itself. Publishing a hole is honest; publishing a list that hides
one is not.

⚠ THIS MODULE DEPOSITS NOTHING AND CALLS NOTHING OVER THE NETWORK. It reads the working tree, hashes
it, and writes one JSON. The deposit steps are instructions for a human, printed into the artifact
so they travel with it rather than living in a chat message that scrolls away.

⚠ NO TIMESTAMP FIELD, DELIBERATELY. An `_utc` here would make two runs of an unchanged tree produce
two different files, which destroys the only cheap check a reader has that the manifest is derived
rather than edited: run it again, diff, expect nothing. The archive's identity is carried by the git
revision instead, which is a fact about the content rather than about when someone happened to look.

Usage:
    python3 research/manuscripts/aso_archive_manifest.py            # write the manifest
    python3 research/manuscripts/aso_archive_manifest.py --check    # exit 1 if it would change
"""
from __future__ import annotations

import ast
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))          # research/
REPO = os.path.abspath(os.path.join(ROOT, ".."))          # repository root
MOD = os.path.join(ROOT, "modalities")
sys.path.insert(0, os.path.abspath(MOD))
import aso_screen_sets as ass                                            # noqa: E402
LIT = os.path.join(ROOT, "literature")
ASO = os.path.join(HERE, "aso")
OUT = os.path.join(ASO, "fusion-junction-aso-archive-manifest.json")

PAPER = os.path.join(ASO, "fusion-junction-aso-research-article.md")

# ---------------------------------------------------------------------------------------------
# The promise table.
#
# ★ ONE ROW PER SENTENCE THE MANUSCRIPT ACTUALLY WRITES, QUOTED VERBATIM. The rows are keyed by the
# promise, not by directory, because the question a reviewer asks is "you said X is released — where
# is it?", and a manifest organised by folder cannot answer that. Quoting the phrase verbatim also
# makes the manifest fail loudly if the manuscript's wording changes: `_promise_text_found_in_paper`
# below re-reads the paper and marks any phrase that is no longer there.
#
# `patterns` are globs relative to the repository root. A row whose globs resolve to ZERO files is
# an UNMAPPED PROMISE and is reported as such rather than dropped — see the `gaps` block.
# ---------------------------------------------------------------------------------------------
PROMISES = [
    {
        # ⛔⛔ THE COMMAND THE PAPER TELLS A READER TO RUN WAS NOT IN THIS MANIFEST (2026-08-19). A
        # reproducibility reviewer cloned HEAD, ran the chain, and then checked the archive: 383
        # files, no `scripts/` entry of any kind. The Availability statement names
        # `./scripts/regenerate_aso_chain.sh` as the way to check every other promise here, so an
        # archive that carries all the data and not the command is an archive a reader cannot use
        # as instructed. Nothing failed, because there was no promise row for it to fail against —
        # the manifest's self-check can only verify promises it has been given.
        "id": "reproduction_command",
        "promise": "the regeneration chain the Availability statement names",
        # ⚠ THE LABEL WAS NEVER A QUOTATION AND THE WORDING CHECK WAS READING IT AS ONE, so this row
        # reported `_promise_still_in_manuscript: false` from the day it was added — a flag crying
        # wolf on a row nobody had mis-set. `quote` carries the fragment actually checked; see
        # `_promise_text_found_in_paper`.
        "quote": "re-derives, in dependency order, the artefacts its own step list names",
        "contributes": ("Re-derives every offline-derivable artefact below in dependency order and "
                        "re-runs the consistency, citation and style gates; the command a reader "
                        "is told to run to establish that this archive is current. The script AND "
                        "every step it invokes that no other row here already carries."),
        # ⛔⛔ THE SCRIPT WAS IN THE ARCHIVE AND HALF THE STEPS IT RUNS WERE NOT (2026-08-19). The
        # promise is not "the file exists"; it is that a reader who runs this command against the
        # archive gets `ASO CHAIN OK`. Measured against the step list: the per-junction table and
        # its generator, the non-canonical-acceptor table, the rasteriser, the figure-provenance
        # RECORD (its checker was released, the record it checks was not), the submission metrics
        # and their artifact, the packet builder, and all three gates the last block runs were
        # absent — so the named command would have died at step 1 on a clean download.
        # ⚠ SHIPPING THE PRODUCER AND NOT ITS OUTPUT IS THE SAME DEFECT IN THE OTHER DIRECTION, so
        # each generator here travels with the artifact it writes. The one deliberate exception is
        # `SUBMISSION-PACKET.md`, which `submission_packet.py` WRITES and never reads: it is a
        # repository status document about submission logistics, not a result, and it is excluded
        # on purpose rather than by oversight.
        "patterns": ["scripts/regenerate_aso_chain.sh",
                     "research/modalities/aso_per_junction_table.py",
                     "research/modalities/aso-per-junction-table.json",
                     "research/modalities/tests/test_aso_per_junction_table.py",
                     "research/modalities/aso_noncoding_acceptor_screened_table.py",
                     "research/modalities/noncoding-acceptor/"
                     "aso-noncoding-acceptor-screened-table.json",
                     "research/manuscripts/figures/svg_to_submission_formats.py",
                     "research/manuscripts/figures/aso-figure-provenance.json",
                     "research/manuscripts/submission_metrics.py",
                     "research/manuscripts/submission-metrics.json",
                     "research/manuscripts/submission_packet.py",
                     "research/manuscripts/lint_consistency.py",
                     "research/manuscripts/lint_citations.py",
                     "research/manuscripts/lint_style.py",
                     # ⛔⛔ FIVE MORE STEPS THE SCRIPT INVOKES WERE ABSENT (round 23, 2026-08-30),
                     # and the row's own `contributes` promised "the script AND every step it
                     # invokes that no other row here already carries" while they were missing —
                     # so the manifest made a false statement about itself, INSIDE the deposit.
                     # ⚠ THIS IS THE SAME DEFECT THE 2026-08-19 COMMENT ABOVE RECORDS, RECURRING
                     # ON THE STEPS ADDED SINCE. The 2026-08-19 sweep enumerated the steps that
                     # existed then; every step added afterwards arrived outside every promise
                     # glob, because nothing measures the script's step list against the
                     # inventory. `aso_offtarget_duplex_energy.py` is the one that matters — see
                     # the `duplex_energy_rescore` row, which owns it and its output — and these
                     # four are the packaging half.
                     "research/manuscripts/claim_coverage.py",
                     "research/manuscripts/build_submission_parts.py",
                     "research/manuscripts/build_submission_docx.py",
                     "research/manuscripts/figures/svg_to_print_formats.py",
                     # ⛔ AND FOUR ARTIFACTS A DEPOSITED TEST OPENS BY NAME. Found by the guard
                     # written for the missing STEPS, on its first run — a step present in the
                     # archive whose INPUT is not is the same failure one level in, and the archive
                     # carries the tests, so a reader running them hits it.
                     # ⚠ A CHAIN STEP THE GUARD'S REGEX MISSED, because the chain invokes it with
                     # a bare `pytest` rather than `python3 -m pytest` — documented in the chain
                     # itself. The regex is widened; the file belongs here, with the other steps.
                     "research/manuscripts/tests/test_the_word_manuscript_is_current_and_whole.py",
                     "research/modalities/aso-genome-offtarget-noncoding-acceptor.json",
                     "research/modalities/fusion-neoantigen-retraction.json",
                     "research/modalities/hybrid-intron-model.json",
                     "research/modalities/nr4a3-deposited-junctions.json"],
    },
    {
        "id": "noncanonical_acceptor_screens",
        "promise": "the screens behind the non-canonical acceptor table",
        # ⚠ THE LABEL IS NOT A QUOTATION AND THE WORDING CHECK WAS READING IT AS ONE — the fourth
        # instance of the 2026-08-19 class, found on 2026-09-02 the moment `gaps` started reporting
        # this flag. The paper writes "non-canonical-acceptor" with a hyphen; the label above writes
        # it without. So the probe missed on punctuation and reported a promise the paper very much
        # still makes, which is a RED ON TRUE INPUT — worse than the reverse, because the first
        # thing anyone does to a guard that cries wolf is loosen it (`paper-hardening`, the red-on-true-
        # input rule).
        # ⛔ THE WRONG FIX IS `verbatim: False`, and this module already says so: that silences the
        # flag on a row whose promise IS quotable. The right one is a probe that is an actual
        # fragment of the paper, which is what `quote` is for.
        # ⚠ AND THE HYPHEN IS NOT NORMALISED AWAY IN THE MATCHER ON PURPOSE. "non-canonical acceptor"
        # and "non-canonical-acceptor" are different strings, and a matcher that folds punctuation
        # would also fold the difference between a compound modifier and two separate words — which
        # is exactly the kind of quiet widening that makes a guard vacuous.
        "quote": "the non-canonical-acceptor designs reported beside that panel",
        "contributes": ("The four screen artifacts and the design/alignment panels that "
                        "`aso_noncoding_acceptor_screened_table.py` joins into "
                        "`aso-noncoding-acceptor-screened-table.json` — the deposited table's own "
                        "inputs, without which the chain step rebuilds it as an empty table."),
        # ⛔⛔ THE TABLE WAS DEPOSITED AND ITS INPUTS WERE NOT, WHICH IS WORSE THAN DEPOSITING
        # NEITHER (round 26's citations seat, 2026-08-31). `aso_noncoding_acceptor_screened_table.py`
        # and its OUTPUT were both in the 496-path archive; the atlas, the mature-parent screen and
        # the pre-mRNA screen it names as module-level constants were not, and neither was a single
        # file of the `noncoding-acceptor/` directory the panel rows are built from. So the command
        # the Availability statement tells a reader to run exited 0, printed `wrote …`, and
        # REPLACED the deposited exon-2 rows — the 8 bp and 9 bp parent duplexes the paper's
        # Test-articles section rests on — with a table carrying no junctions at all.
        # ⚠ AND THE GUARD WRITTEN FOR EXACTLY THIS CLASS PASSED. `test_the_deposited_chain_can_run_
        # from_the_deposit.py` parses the chain for MODULE invocations and checks those against the
        # inventory; the module was deposited, so it saw nothing. That is the third iteration of one
        # blindness — first the invocation verb, then the nested shell variable, now the module's
        # own inputs — and it is closed by `test_every_input_an_invoked_module_names_is_in_the_
        # archive`, which resolves each invoked module's module-level path constants by AST.
        # ⭐ THE WHOLE DIRECTORY, NOT THE THREE THE PROBE NAMED. The rows are built by
        # `aso_per_junction_table.junction_rows` over screens DISCOVERED BY PATTERN in `SCREEN_DIR`,
        # so a hand-list of the files a static read happened to name would leave the table empty
        # just as reliably — a glob is what makes this row survive the next screen added there.
        "patterns": ["research/modalities/nr4a3-fusion-junction-atlas-noncoding-acceptor.json",
                     "research/modalities/aso-parent-gap-pairing-noncoding-acceptor.json",
                     "research/modalities/aso-premrna-offtarget-noncoding-acceptor.json",
                     "research/modalities/junction-aso-thermo-noncoding-acceptor.json",
                     "research/modalities/pgr-parent-engagement-noncoding-acceptor.json",
                     "research/modalities/noncoding-acceptor/*.json"],
    },
    {
        "id": "graded_junction_atlas",
        "promise": "the graded junction atlas",
        "contributes": ("Grades all 231 donor-exon x acceptor-exon pairs across the five 5' "
                        "partners for frame compatibility and carries the 38 emitted design "
                        "panels inline; the source of Table 1 and of every count in section 3.1."),
        # ⛔ `fusion-object-inventory.json` is not optional: `junction_aso.plausible_nr4a3_resume_
        # residues()` opens it unconditionally, so an archive without it cannot regenerate the
        # atlas at all (measured 2026-08-13 — `nr4a3_fusion_atlas.py` dies with FileNotFoundError).
        # It was missing from this row until a data-integrity review ran the regeneration rather
        # than reading the file list.
        "patterns": ["research/modalities/nr4a3-fusion-junction-atlas.json",
                     "research/modalities/fusion-object-inventory.json",
                     "research/modalities/nr4a3_fusion_atlas.py"],
    },
    {
        "id": "per_junction_design_panels",
        "promise": "per-junction design panels",
        "contributes": ("Per-junction gapmer panel: the 16-mer 5-6-5 LNA/DNA/LNA registers whose "
                        "seam falls inside the DNA gap, with the gap-level specificity margin the "
                        "paper ranks on."),
        "patterns": ["research/modalities/junction-aso-designs*.json",
                     "research/modalities/junction_aso.py"],
    },
    {
        "id": "specificity_screen_blast",
        # ⚠ NOT VERBATIM. The manuscript promises "both specificity screens per junction" in one
        # phrase; the two arms are different files produced by different modules, so the promise is
        # split across two rows here and neither row's label is a quotation. `verbatim: False`
        # suppresses the wording check rather than letting it print a false alarm — a flag that
        # cries wolf on rows it was never meant to check is a flag that gets ignored on the row
        # that matters.
        "verbatim": False,
        "promise": "both specificity screens per junction (arm 1: gap-resolved BLAST screen)",
        "contributes": ("Gap-resolved near-match screen against human RefSeq RNA (blastn-short, "
                        ">=14/16 identity), classifying each near-match by whether the six-"
                        "nucleotide catalytic gap is fully base-paired."),
        "patterns": ["research/modalities/junction-aso-offtarget-*n3.json",
                     "research/modalities/junction-aso-offtarget-bp200-8.json",
                     "research/modalities/junction-aso-offtarget-bp200-8-gapres.json",
                     "research/modalities/junction_aso_offtarget.py"],
        # ⚠ The `-graded` siblings match `*n3.json` only through their own row below; the exclusion
        # is applied in `_resolve` so a re-score is never double-counted as a screen.
    },
    {
        "id": "specificity_screen_exhaustive",
        "verbatim": False,   # the other half of the split promise above
        "promise": "both specificity screens per junction (arm 2: exhaustive seed-and-extend scan)",
        "contributes": ("Exhaustive seed-and-extend scan of 186,185 GRCh38.p14 transcripts for "
                        "exact and <=1-mismatch matches, complete for substitutions by "
                        "construction; also carries the 180-nt local-fold accessibility estimate."),
        "patterns": ["research/modalities/aso-insilico-evaluation*.json",
                     "research/modalities/aso_insilico.py"],
    },
    {
        "id": "graded_rescores",
        "promise": "the graded re-scores under both discrimination bounds",
        "contributes": ("Re-score of a committed screen under both literature discrimination "
                        "bounds (5-fold; and no efficient discrimination at 16-mer), holding the "
                        "hit set fixed so only the scoring moves. Produced offline by "
                        "`junction_aso_offtarget.py --rescore`; no network, no re-BLAST."),
        "patterns": ["research/modalities/junction-aso-offtarget-*-graded.json"],
    },
    {
        "id": "per_design_tables",
        "promise": "per-design tables",
        # ⚠ THE PANEL IS NAMED BY CONTENT, NOT BY NUMBER. This read "Figure 3", which stopped being
        # the chance-baseline panel on 2026-08-15 (it became Supplementary Figure S1) and named a
        # different panel again after the 2026-08-17 renumber to citation order. A figure number is
        # owned by the manuscript's `Figure legends` section and nowhere else.
        "contributes": ("The manuscript tables and the generator that derives every cell of "
                        "them from the artifacts, plus the per-locus re-count and the chance "
                        "baseline the tables and the chance-expectation panel are read from."),
        # ⛔ TWO OF THE SEVEN TABLES READ AN ARTIFACT THE ARCHIVE DID NOT CARRY (2026-08-19).
        # `submission_tables.py` opens `fusion-junction-aso-coverage-ladder.json` to build the
        # coverage-ladder table, and the reagent-coverage record behind it was released only as a
        # module inside a test's import. The row's own promise is that a cell and its source cannot
        # diverge; a source outside the deposit makes that uncheckable rather than false, which is
        # worse, because the table still prints.
        # ⛔ THE JOURNAL ARTICLE'S OWN DISPLAY-ITEM CHAIN WAS OUTSIDE THE DEPOSIT (round 9, two
        # seats). The article names `fusion-junction-aso-journal-tables.md` in its Tables section
        # and the deposit did not contain it, nor the generator behind it — the same
        # source-outside-the-deposit defect this row's comment above describes, one document over.
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-submission-tables.md",
                     "research/manuscripts/submission_tables.py",
                     "research/manuscripts/aso/fusion-junction-aso-journal-tables.md",
                     "research/manuscripts/aso_journal_tables.py",
                     "research/manuscripts/aso/fusion-junction-aso-journal-references.md",
                     "research/manuscripts/aso/fusion-junction-aso-coverage-ladder.json",
                     "research/manuscripts/aso_coverage_ladder.py",
                     "research/manuscripts/aso/fusion-junction-aso-reagent-coverage.json",
                     "research/manuscripts/aso_reagent_coverage.py",
                     "research/modalities/junction-aso-offtarget-locus-collapse.json",
                     "research/modalities/junction_aso_locus_collapse.py",
                     "research/modalities/offtarget-chance-baseline.json",
                     "research/modalities/offtarget_chance_baseline.py"],
    },
    {
        "id": "retrieval_records",
        "promise": "the retrieval records for every literature claim",
        "contributes": ("Bibliographic record each numbered reference was rendered from, and the "
                        "retrieval products those records were harvested out of. No field in the "
                        "reference list is typed from recollection."),
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-references.json",
                     "research/manuscripts/aso/fusion-junction-aso-references.md",
                     "research/manuscripts/aso/fusion-junction-aso-submission-references.json",
                     "research/manuscripts/aso/fusion-junction-aso-submission-references.md",
                     "research/manuscripts/submission_citations.py",
                     "research/literature/fusion-consensus-probe.json",
                     "research/literature/submission-reference-metadata-2026-08-09.json",
                     "research/manuscripts/fusion-partner/lit-targets-partner-events.json",
                     "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json",
                     "research/data/emc-clinical-registry.json",
                     # ⛔⛔ A HAND-LIST OF FOUR AGAINST TWELVE ON DISK (2026-08-19). This row named
                     # `lit-targets-aso-{verify,thermo,gap-length,round7-precedents}.json` one at a
                     # time, and eight further retrieval products sat in the same directory
                     # unreleased — among them the two the reference builder itself HARVESTS
                     # (`submission_citations.HARVEST_SOURCES` opens `lit-targets-nr4a-redundancy`
                     # and `lit-targets-aso-bibliography-completion`), the breakpoint census five
                     # producers read, and the delivery-route corpus behind the Discussion. The row
                     # above the table warns in terms that a hand-list falls behind the repository;
                     # this is the row it fell behind on.
                     # ⚠ SO IT IS A GLOB NOW, over the manuscript's own directory: a retrieval
                     # product committed there tomorrow enters the deposit without anyone
                     # remembering. Files this row claims that a later row describes more
                     # specifically keep their specific `contributes` line through `also_serves`.
                     "research/manuscripts/aso/lit-targets-*.json",
                     # The data-source register the reference builder reads, the live-resolution
                     # records for the three 2026 references ("those records travel with the
                     # archive"), and the primary sources the TCF12 breakpoint assignment is made
                     # against.
                     "research/manuscripts/aso/fusion-junction-aso-data-sources.json",
                     "research/manuscripts/aso/fusion-junction-aso-2026-citation-resolution.json",
                     "research/literature/tcf12-nr4a3-breakpoint-primary-sources.json",
                     # ⛔ FOURTH INSTANCE IN ONE DAY OF A CLAIM RELEASED WITHOUT ITS EVIDENCE
                     # (2026-08-17). This file is the committed CI-fetch evidence behind B6-F1's
                     # in-vivo precedent scope, B6-F2's liver-restricted GalNAc route, C2-F4's GEO
                     # sample identity, D2-U1's citation marker, and — added the same day — the two
                     # verbatim windows for the paper's one previously unanchored quotation. Every
                     # one of those is a statement the manuscript makes; none was in the deposit.
                     "research/manuscripts/aso/lit-targets-aso-round7-precedents.json",
                     "research/manuscripts/aso/aso-citations-priorart-2026-08-08.md"],
    },
    {
        "id": "correction_record",
        "promise": ("The complete correction record, including every superseded value, is "
                    "released with the archive."),
        "contributes": ("The acceptor-seam exon-indexing correction: the grader that banners every "
                        "affected artifact, the frame audit and regeneration record that show "
                        "which junctions were re-emitted and which were refused, and the working "
                        "record and red-team pass that narrate the withdrawal."),
        "patterns": ["research/modalities/junction_seam_retraction.py",
                     "research/modalities/junction-mrna-frame-audit.json",
                     "research/modalities/junction-aso-regen-manifest.json",
                     "research/manuscripts/aso/fusion-junction-aso-working-record.md",
                     "research/manuscripts/aso/fusion-junction-aso-paper-redteam.md",
                     # ⚠ THE PROMISE SAYS "INCLUDING EVERY SUPERSEDED VALUE", AND THIS IS THE FILE
                     # THAT HOLDS THEM. `pinned-figures.json` is the register a corrected number is
                     # entered in — the machine-readable half of the correction record, and the
                     # input the consistency gate reads. Released without it, the narrative record
                     # travels and the values it narrates do not.
                     "research/manuscripts/pinned-figures.json"],
    },
    {
        "id": "inputs_that_make_it_offline",
        # ⚠ RE-QUOTED 2026-08-13 AFTER THE MANUSCRIPT WAS REWRITTEN, AND THE FLAG IS WHAT CAUGHT IT.
        # The earlier quotation ("No result in this manuscript requires network access or
        # credentials to reproduce from that archive.") went `false` the moment the Availability
        # paragraph was rewritten to enumerate WHICH artefacts recompute. That is the wording check
        # doing precisely its job, so the row is re-quoted rather than the check loosened.
        # ⛔ AND THE NEW SENTENCE IS THE STRONGER CLAIM: it names five recomputations by name, so it
        # is now falsifiable item by item rather than in aggregate — see `gaps.⚠_known_and_deliberate`,
        # where one of the five is currently measured NOT to recompute.
        "promise": ("Every result reported here is re-derived from the committed artefacts in that "
                    "archive without network access or credentials"),
        # ⚠ RE-QUOTED 2026-08-19, THE SECOND TIME THIS FLAG HAS CAUGHT THE SAME PARAGRAPH MOVING.
        # The Availability sentence now reads "...re-derived, without network access or credentials,
        # from the committed artefacts in that repository": the qualifier moved inside the clause and
        # "archive" became "repository", which is the stronger and more checkable statement (the
        # repository is what a reader can check TODAY, before any DOI exists). The label above is
        # kept as the row's readable promise; the fragment below is what is checked.
        "quote": ("Every result reported here is re-derived, without network access or credentials, "
                  "from the committed artefacts in that repository"),
        "contributes": ("The committed inputs that let the pipeline run with the network off: the "
                        "transcript cache the atlas reads instead of calling Ensembl, and the "
                        "independent exon audit the per-gene provenance gate is checked against."),
        "patterns": ["research/modalities/emc-construct-inputs.json",
                     "research/modalities/nr4a3-exon-audit.json",
                     "research/modalities/junction-breakpoint-scan.json",
                     "research/modalities/junction_breakpoint_scan.py"],
    },
    {
        "id": "duplex_thermodynamics",
        "verbatim": False,
        "promise": "the nearest-neighbour duplex thermodynamics and the design-rule audit",
        "contributes": ("ΔG37 for each design against the fusion and against the best duplex "
                        "either parent can form, the ΔΔG discrimination that follows, and the "
                        "audit of every design against four conventional antisense design rules. "
                        "Carries the convention validation that licenses the energies."),
        "patterns": ["research/modalities/junction-aso-thermo.json",
                     "research/modalities/junction_aso_thermo.py",
                     "research/manuscripts/aso/lit-targets-aso-thermo.json"],
    },
    {
        "id": "premrna_compartment_screen",
        "verbatim": False,
        "promise": ("the pre-mRNA screen behind §2.5, and the sequence it ran against, so the "
                    "compartment the transcript screens cannot see is re-derivable offline"),
        "contributes": ("The exhaustive ≤2-mismatch scan of every design against the unspliced "
                        "sequence of all six parent transcripts, gap-resolved, orientation-filtered "
                        "and classified as intronic / exonic / intron–exon-spanning. ⭐ THE RETRIEVED "
                        "SEQUENCE TRAVELS WITH IT, which is what makes this the one screen in the "
                        "paper that recomputes with no network at all: the other two need NCBI BLAST "
                        "and a RefSeq download. Re-running the module with --offline against the "
                        "committed cache reproduces every number in §2.5 exactly."),
        "patterns": ["research/modalities/aso-premrna-offtarget.json",
                     "research/modalities/aso-premrna-sequences.json",
                     "research/modalities/aso_premrna_offtarget.py",
                     "research/modalities/tests/test_aso_premrna_offtarget.py"],
    },
    {
        "id": "mature_parent_gap_pairing_screen",
        "verbatim": False,
        "promise": ("the mature-parent screen behind §2.5's second class — the liability that "
                    "none of the other three screens is able to see"),
        "contributes": ("For every design, the longest contiguous duplex a MATURE wild-type parent "
                        "transcript can form that pairs the whole six-nucleotide catalytic gap. "
                        "⭐ IT EXISTS BECAUSE THE OTHER THREE SCREENS STRUCTURALLY CANNOT ANSWER IT: "
                        "the alignment screen excludes parent records and filters at ≥14/16 "
                        "identity, the exhaustive scan admits ≤1 mismatch, and the pre-mRNA arm "
                        "searches unspliced sequence and so cannot reach a mature exon–exon "
                        "junction. It is fully offline against the same cached sequence the "
                        "pre-mRNA arm uses, and `--check` re-derives it."),
        "patterns": ["research/modalities/aso-parent-gap-pairing.json",
                     "research/modalities/aso_parent_gap_pairing.py",
                     "research/modalities/tests/test_aso_parent_gap_pairing.py"],
    },
    {
        "id": "genome_wide_screen",
        "verbatim": False,
        "promise": ("the exhaustive genome-wide screen, which removes the six-transcript bound every "
                    "other arm carries, and the retrieved evidence for the RNase-H1 gap and hybrid "
                    "lengths the Methods now cite"),
        "contributes": ("Every distinct target window and its reverse complement tested against every "
                        "position of GRCh38 in both orientations at ≤2 mismatches — a measured "
                        "3.10e9 nt, no seed and no word size, so completeness is definitional rather "
                        "than argued. ⛔ THE RAW TOTAL IS NOT THE DELIVERABLE and the artifact says so "
                        "first: at this threshold chance predicts of order 10^3 near-matches per "
                        "16-mer for ANY 16-mer. The readings are stratified — exact matches, where "
                        "chance is of order one; observed-over-expected, which discriminates between "
                        "designs; the named-target lookup, which one hit settles; and the repeat "
                        "split, free from a soft-masked reference. Also carries the gap-length "
                        "anchors, ported from the literature-cache branch where gate 4 cannot see "
                        "them."),
        "patterns": ["research/modalities/aso-genome-offtarget.json",
                     "research/modalities/aso_genome_offtarget.py",
                     "research/modalities/tests/test_aso_genome_offtarget.py",
                     "research/manuscripts/aso/lit-targets-aso-gap-length.json"],
    },
    {
        # ⛔⛔ THE SCREEN BEHIND FOUR NUMBERS THE PAPER PRINTS WAS NOT IN THIS ARCHIVE, AND THE
        # AVAILABILITY STATEMENT PROMISED IT WAS (round 23, 2026-08-30). Found by the
        # citations-and-instruments seat. "All code, graded artefacts, per-design tables, every
        # screen's parameters and the complete bounds on each claim are deposited under
        # doi:10.5281/zenodo.22180100" — and neither `aso_offtarget_duplex_energy.py` nor
        # `aso-offtarget-duplex-energy.json` was among the 484 paths. A reader who downloaded the
        # DOI to check "8 designs carry a fully paired sixteen-base-pair off-target duplex and 45
        # one inside 2 kcal/mol of their own", or the 3.2 and 3.0 kcal/mol margins the two named
        # reagents rest on, found neither the numbers nor the code that produces them.
        # ⚠ IT SURVIVED EVERY EARLIER VERSION: 482, 483 and 484 paths, none carrying it — including
        # the 2026-08-19 sweep that fixed exactly this defect for five OTHER artifacts, whose own
        # comment says withholding an ensemble "leaves the one number a sceptical reader most wants
        # to recompute uncheckable". Same defect, one screen over, three published versions long.
        # ⛔ AND THE ARCHIVE WAS INTERNALLY BROKEN BY IT, which is what makes this reader-facing
        # rather than merely incomplete: `research/modalities/tests/test_aso_submission_numbers.py`
        # IS deposited and loads the missing JSON, and `scripts/regenerate_aso_chain.sh` IS
        # deposited and invokes the missing module at step "offtarget duplex energy" — so the
        # command the paper tells a reader to run died on a clean download.
        "id": "duplex_energy_rescore",
        "verbatim": False,
        "promise": ("the off-target screen re-scored on duplex stability rather than on mismatch "
                    "count, and the margins the two named reagents rest on"),
        "quote": "every screen's parameters and the complete bounds on each claim",
        "contributes": ("The fifth screen's re-scoring arm: every design's closest gap-paired "
                        "off-target duplex by free energy rather than by mismatch count, with the "
                        "two named reagents' separations from theirs, and the producer that writes "
                        "it. ⚠ ITS TWO BOUNDS POINT OPPOSITE WAYS and the artifact says so in its "
                        "own headers rather than leaving a reader to find out — the manuscript "
                        "states one of them, and the deposit is where the other lives."),
        "patterns": ["research/modalities/aso-offtarget-duplex-energy.json",
                     "research/modalities/aso_offtarget_duplex_energy.py",
                     # ⚠ TWO FILES WERE APPENDED HERE ON 2026-08-31 AND MOVED OUT AGAIN THE SAME
                     # DAY (round 25's regression seat). Appending them to the nearest existing
                     # pattern list got them INTO the archive and gave them this promise's `serves`
                     # and `contributes`, so the deposited manifest described a power calculation
                     # and a Word-file staleness check as "the fifth screen's re-scoring arm …
                     # closest gap-paired off-target duplex by free energy". The files were present
                     # and the index lied about them — which is the narrowed rule's own carve-out,
                     # "misdescribe what the archive contains", and therefore still a blocker.
                     # ★ THE LESSON IS THE CHECK I DID NOT RUN: I regenerated the manifest and
                     # confirmed the PATHS were present. I never read what the ENTRIES said. They
                     # now sit under `reproduction_guards` and `reproduction_command`, whose
                     # promises actually describe them.
],
    },
    {
        "id": "censoring_test_and_genomic_attempt",
        "verbatim": False,
        "promise": ("the test of the censoring restriction the cleanliness claim depends on, and the "
                    "genome-wide screen that was attempted and did not work"),
        "contributes": ("⭐ THE EVIDENCE THAT THE CENSORING GUARD IS LOAD-BEARING RATHER THAN MERELY "
                        "CAUTIOUS. Seven design-and-junction records had no hybridisable retained hit "
                        "and a raw count above the retention depth but below the search ceiling, so "
                        "retention alone withheld a verdict; re-screened at a tenfold deeper ceiling, "
                        "six are decided and NONE is clean (one design's 21 near-matches become 196 "
                        "with 119 hybridisable). Relaxing the restriction would have promoted six "
                        "records a deeper look refutes. ⚠ These are a SEPARATE measurement under "
                        "their own suffix: a count at a deeper ceiling does not correct the shallower "
                        "one, and no number in the manuscript is restated from them. Also included: "
                        "the genome-wide arm's output, which ran against NCBI core_nt and saturated "
                        "the hit ceiling on every query over a mixed corpus of assemblies, clones and "
                        "patents — released so a reader need not repeat an attempt that did not "
                        "yield an interpretable result."),
        # ⛔ THE GLOB ENDED `-deep500.json` AND THE RE-SCREENS WERE DISPATCHED IN BATCHES, so every
        # file named `...-deep500-b1.json` or `-b2.json` fell outside it — 28 of the 53 deeper
        # screens, silently. The row's own text calls these "a SEPARATE measurement under their own
        # suffix"; the suffix grew a batch tag and the pattern did not follow. Matching `-deep500*`
        # takes the batch tags and any future one.
        "patterns": ["research/modalities/junction-aso-offtarget-*-deep500*.json",
                     "research/modalities/aso-insilico-evaluation-*-deep500*.json",
                     "research/modalities/aso-premrna-offtarget-genomic.json"],
    },
    {
        "id": "priorart_first_in_kind_evidence",
        "verbatim": False,
        "promise": "the retrieval evidence behind the first-in-kind statement",
        "contributes": ("Every identifier in the two Europe PMC corpora the Introduction's "
                        "'5,153 unique records' rests on, with the per-corpus counts and their "
                        "overlap, so the count is re-derivable rather than taken on trust. The "
                        "corpora themselves live on the literature-cache branch; this is the "
                        "evidence the claim actually needs."),
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-priorart-evidence.json",
                     "research/manuscripts/aso_priorart_evidence.py"],
    },
    {
        "id": "test_articles_and_cell_models",
        "verbatim": False,
        # ⛔ THE THIRD INSTANCE OF THE SAME DEFECT IN ONE DAY, AND IT ARRIVED WITH THE FIX FOR THE
        # FIRST TWO (2026-08-17). Section 3 was given pointers naming the artifacts behind its
        # cell-model and test-article readings — which is right, and is what a reader needs — but
        # naming an artifact as RELEASED while it sits outside the manifest converts a helpful
        # pointer into a broken promise. Two of the three named files were not in the deposit.
        # ⚠ THE PATTERN IS WORTH STATING: every time a claim gains its evidence pointer, the
        # manifest is the second half of that edit. A pointer and a promise are the same sentence to
        # a reader; only one of them was being kept.
        # ⭐ `emc-test-article-routes.json` is included although no section names it: it is where the
        # three published constructs' exon spans are quoted verbatim, which is the evidence behind
        # section 3's construct-to-lead mapping. An unnamed source that a stated fact rests on still
        # has to travel with the deposit.
        "promise": "the test articles and cell models section 3 names, and what is known about each",
        "contributes": ("The evidence behind section 3: the three published constructs with their "
                        "author-stated exon spans, the two identity-clean patient-derived models "
                        "with their RRIDs and the figure-legend fusion calls they rest on, the "
                        "third line whose availability could not be established, and the fusion "
                        "caller, expression reading and registry caution behind the statement that "
                        "no NR4A3 fusion is detectable in H-EMC-SS on the public record. "
                        "H-EMC-SS identity is DISPUTED (OBJ-LINE-HEMCSS): the evidence in this row "
                        "is what makes that dispute checkable, and section 3's operative "
                        "conclusion -- that the line cannot serve as a test article for any reagent "
                        "named here -- does not rest on the line being EMC."),
        "patterns": ["research/modalities/emc-test-article-routes.json",
                     "research/modalities/emc-model-junction-evidence.json",
                     "research/modalities/emc_model_junction_evidence.py",
                     "research/modalities/emc-atr-vulnerability.json"],
    },
    {
        "id": "unrearranged_allele_scan",
        "verbatim": False,
        # ⛔ THE DEPOSIT SHIPPED THE TEST AND NOT THE CODE UNDER TEST (found 2026-08-17, D4-F4).
        # `test_aso_submission_numbers.py` is in this manifest and pins the scan's positive control,
        # so the archive proved a result whose producer it did not contain. Section 2.6's central
        # negative — three designs pairing their whole catalytic gap against the patient's own
        # un-rearranged NR4A3 allele — rested on five artifacts none of which was released.
        # ⚠ BOTH MODULES, NOT ONE. The grader has exactly one implementation, in
        # `aso_taf15_intron2_designs.py`, which `aso_noncoding_acceptor_designs.py` reaches through a
        # LAZY import — so an import-closure walk over the five procedure modules of section 4.5
        # finds neither, which is why this stayed invisible.
        "promise": "the un-rearranged-allele scan and the designs it condemns",
        "contributes": ("The scan that asks whether a design whose acceptor half is not exonic in "
                        "the mature transcript pairs its whole catalytic gap against the patient's "
                        "un-rearranged NR4A3 allele, at both seams it can reach: within intron 2 "
                        "for the cryptic-exon acceptor and across the intron-1/exon-2 boundary for "
                        "the exon-2 acceptors. Carries the three condemned designs, the two seams "
                        "that keep a reagent, and the positive control the released tests pin."),
        "patterns": ["research/modalities/aso_taf15_intron2_designs.py",
                     "research/modalities/aso_noncoding_acceptor_designs.py",
                     "research/modalities/aso-taf15-intron2-designs.json",
                     "research/modalities/aso-ewsr1-intron2-designs.json",
                     "research/modalities/aso-noncoding-acceptor-designs.json",
                     "research/modalities/nr4a3-fusion-junction-atlas-taf15intron2.json",
                     "research/modalities/nr4a3-fusion-junction-atlas-ewsr1intron2.json"],
    },
    {
        "id": "delivery_antigen_negative",
        # ⛔ ADDED WITH THE CLAIM, NOT AFTER IT (2026-08-17). The Discussion now reports that no
        # surface antigen could be named when the two-axis question was put to EMC tissue. That is a
        # released NEGATIVE, and a negative without its evidence in the deposit is the worst kind of
        # promise to break: a reader cannot check what was looked at, so cannot tell a bounded search
        # from an unbounded conclusion. The producer, the screen and its four named inputs travel
        # together because the artifact's own `_inputs` block names all four and it is $0 to run.
        "promise": "No such antigen could be named when the question was put to the disease's own",
        "contributes": ("The two-axis surface-antigen screen behind the Discussion's delivery "
                        "negative: the twelve antigens scoreable on both axes, the measured EMC "
                        "tumour-versus-normal-organ exposure contrast from GSE28866, the three "
                        "that clear the measured axes and the reason each is still refused, and "
                        "the ceiling field recording that 86 further surface-board genes are "
                        "unmeasured rather than excluded. Released so the bound on what was "
                        "examined is checkable rather than taken on trust."),
        "patterns": ["research/modalities/aso-delivery-antigen.json",
                     "research/modalities/aso_delivery_antigen.py",
                     "research/modalities/gse28866-tumour-vs-normal.json",
                     "research/modalities/emc-expression-panels.json",
                     "research/modalities/emc-surface-normal-window.json",
                     "research/modalities/emc-surfaceome-scan.json",
                     "research/manuscripts/aso/aso-delivery-antigen-2026-08-08.md"],
    },
    {
        "id": "canonical_sequence_record",
        # ⛔ THE DEPOSIT MUST CARRY A COPY OF THE SEQUENCES THAT WAS NEVER TYPESET (2026-08-17).
        # A blind screen of the built PDF found table sequences printed with no 5′-/-3′ delimiters,
        # sitting against a numeric cell, so one extractor returned a 16-mer with a trailing digit.
        # For a paper whose deliverable is orderable oligos that is a wrong-reagent hazard, and
        # padding the cells only fixes the extractor we happened to test.
        "promise": "the canonical machine-readable record of every sequence this deposit names",
        # ⚠ LABEL, NOT QUOTATION — re-anchored 2026-08-19 to the sentence the Sequences paragraph
        # actually writes, which names both files.
        "quote": "Every sequence named here travels with the archive as",
        "contributes": ("Every design the three deposit documents name, in CSV and FASTA, with its "
                        "geometry, junction, gap-level margin, longest wild-type-parent duplex and "
                        "an explicit do-not-order flag on every record the paper condemns. ⚠ THAT "
                        "FLAG IS ON 257 OF THE 780 RECORDS, NOT ON THREE: 249 pair a wild-type "
                        "parent through the whole catalytic gap at the ten-base-pair criterion, "
                        "5 carry a sense-strand near-match in parent precursor RNA that pairs the "
                        "gap in full, and 3 more pair the patient's own un-rearranged NR4A3 "
                        "allele. ⛔ THIS COUNT IS HARD-TYPED AND HAS BEEN WRONG ONCE: it said 252 "
                        "after the pre-mRNA class was added to the file, so the deposit's own "
                        "description under-reported the flag a laboratory reads first. This "
                        "sentence named only the second class until 2026-08-19, which described "
                        "the smaller hazard and left the larger one sounding like a clean file. "
                        "The generator "
                        "refuses to build if any sequence the documents print is absent, so the "
                        "file cannot quietly stop being canonical."),
        # ⛔⛔ THE GENERATOR'S RUNTIME INPUT, WHICH THE IMPORT CLOSURE CANNOT SEE. Round 22's
        # arithmetic seat found `aso-control-oligos.json` and its producer absent from the deposit
        # while the DEPOSITED `aso_sequence_manifest.py` reads that JSON at runtime (`_load(
        # "aso-control-oligos.json")`) to write Table 2's two control rows into the deposited
        # sequences CSV. So a reader holding only the archive could not regenerate the canonical
        # file the Declarations tell them to order from, and could not re-derive the two controls
        # (drawn under a recorded seed) — while `gaps.promises_resolving_to_no_file` read empty.
        # ★ THE MECHANISM IS WORTH THE COMMENT: `gaps.import_closure` follows IMPORTS, and this is a
        # DATA read. A closure over one edge type reports completeness it has not checked, which is
        # the same "reports while measuring nothing" shape this repository has now hit in a
        # workflow, a census lane and a citation-type gate.
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-sequences.csv",
                     "research/manuscripts/aso/fusion-junction-aso-sequences.fasta",
                     "research/manuscripts/aso_sequence_manifest.py",
                     "research/modalities/aso-control-oligos.json",
                     "research/modalities/aso_control_oligos.py",
                     "research/manuscripts/tests/test_pdf_text_layer_is_orderable.py"],
    },
    {
        "id": "reproduction_guards",
        "promise": ("Every quantitative statement here is produced by code in the released "
                    "archive and is reproducible from it"),
        # ⚠ RE-QUOTED 2026-08-19: the AI-use declaration now SCOPES the claim — "Every quantitative
        # statement DERIVED FROM SEQUENCE OR FROM A SCREEN is produced by code in the released
        # archive", with the clinical figures excluded as transcribed from their publications. That
        # is a narrowing of the promise, so the row is re-quoted rather than the check loosened.
        "quote": ("Every quantitative statement derived from sequence or from a screen is produced "
                  "by code in the released archive"),
        "contributes": ("Test that re-derives a manuscript number from the artifacts and fails if "
                        "the two diverge; this is the check a reader runs to confirm the archive "
                        "reproduces the paper."),
        "patterns": ["research/modalities/tests/test_aso_submission_numbers.py",
                     "research/modalities/tests/test_junction_aso_graded.py",
                     "research/modalities/tests/test_junction_aso_locus_collapse.py",
                     "research/modalities/tests/test_junction_aso_seam.py",
                     "research/modalities/tests/test_junction_seam_retraction.py",
                     ],
    },
    {
        # ⛔⛔ FILED TWICE WRONG BEFORE IT WAS FILED RIGHT, AND THE SECOND MISFILING WAS A BLOCKER.
        # Round 24's statistics seat found this module absent from the archive while it produces
        # FIVE numbers the Discussion prints. The first repair appended it to the duplex-energy
        # screen's pattern list, so the deposited manifest described a power calculation as "the
        # fifth screen's re-scoring arm … by free energy" — round 25's regression seat caught that.
        # The second attempt put it under `reproduction_guards`, whose per-file description is
        # "Test that re-derives a manuscript number", and it is not a test.
        # ★ THE CHECK THAT FOUND BOTH: regenerate the manifest and READ THE ENTRY, not just confirm
        # the path is present. A file inherits its group's prose, so filing is a description.
        # ⚠ IT IS THE ONE PRODUCER IN THIS ARCHIVE THAT WRITES NO ARTIFACT — the figures are
        # computed and printed, held in no committed JSON — so if this module is missing, the
        # numbers behind the pre-registered experiment's replicate count cannot be checked at all.
        # That is also why the chain guard cannot see it: it is not a step of the chain.
        "id": "falsification_power",
        "verbatim": False,
        "promise": ("the power and void-variance calculation behind the replicate count the "
                    "pre-registrable experiment names"),
        "quote": "every screen's parameters and the complete bounds on each claim",
        "contributes": ("The falsification experiment's power and void-standard-deviation figures, "
                        "DERIVED rather than typed: about 80% power at six biological replicates "
                        "and about 30% at three to falsify a true selectivity of 3, and the "
                        "realised standard deviations above which such a test is void — 0.65 at "
                        "three replicates, 1.53 at six, 2.25 at ten. ⚠ It writes no artifact, so "
                        "this module is the only place those five numbers can be reproduced from."),
        "patterns": ["research/manuscripts/aso_falsification_power.py"],
    },
    {
        "id": "where_each_number_lives",
        # ⛔⛔ THE AVAILABILITY STATEMENT NAMES FIFTEEN FILES BY PATH, AND FIVE OF THEM WERE NOT IN
        # THIS MANIFEST (2026-08-19). "Which file holds which number is given here rather than left
        # to a search" is the most literally checkable promise the paper makes — a reader can put
        # the two lists side by side in a minute — and it named `aso-parent-null.json` (the null
        # ensembles the central negative is read against), `aso_parent_null.py`,
        # `aso-offtarget-tissue-expression.json`, `aso-gap-length-tradeoff.json` and
        # `tcf12-breakpoint-assignment.json`, none of which the deposit carried.
        # ⚠ THE NULLS ARE THE WORST OF THE FIVE TO HAVE OMITTED. The paper's headline reading is an
        # observed rate against an ensemble of nulls; releasing the observation and withholding the
        # ensemble leaves the one number a sceptical reader most wants to recompute uncheckable.
        # ⭐ EACH ARTIFACT TRAVELS WITH ITS PRODUCER, ITS COMMITTED INPUT CACHE AND ITS GUARD, which
        # is what makes "re-derived without network access" true of it rather than merely stated:
        # the tissue-expression arm reads `-inputs.json` instead of calling the expression API, and
        # the TCF12 assignment is made against a committed primary-source record.
        "promise": "the files the Availability statement names one by one",
        "quote": "Which file holds which number is given here rather than left to a search.",
        "contributes": ("The artefacts the Availability statement names by path that no other "
                        "promise row resolves: the parent-null ensembles the observed liability "
                        "rate is read against, the off-target expression readings, the gap-length "
                        "comparison, and the base-level TCF12 breakpoint assignment — each with "
                        "its producer, its committed offline input and its guard."),
        "patterns": ["research/modalities/aso-parent-null.json",
                     "research/modalities/aso_parent_null.py",
                     "research/modalities/tests/test_aso_parent_null.py",
                     "research/modalities/aso-offtarget-tissue-expression.json",
                     "research/modalities/aso-offtarget-tissue-expression-inputs.json",
                     "research/modalities/aso_offtarget_tissue_expression.py",
                     "research/modalities/tests/test_aso_offtarget_tissue_expression.py",
                     "research/modalities/aso-gap-length-tradeoff.json",
                     "research/modalities/aso_gap_length_tradeoff.py",
                     "research/modalities/tests/test_aso_gap_length_tradeoff.py",
                     "research/manuscripts/aso/tcf12-breakpoint-assignment.json",
                     "research/manuscripts/tcf12_breakpoint_assignment.py"],
    },
    {
        "id": "reimplementation_crosscheck",
        # ⛔ A NEGATIVE'S STRONGEST DEFENCE, RELEASED AS A SENTENCE AND NOT AS CODE (2026-08-19).
        # Declarations -> Provenance describes a second implementation sharing no code with the
        # first, differing on four named axes, agreeing on all 231 graded pairs and on all 190
        # designs — and ends "Both implementations, the comparison and its deliberate-corruption
        # tests are in the archive." Neither implementation-comparison file was in the archive. Of
        # every promise in this table that is the one whose breach costs most: the claim exists
        # precisely to answer a reader who suspects the instrument, and such a reader is the one
        # certain to look for it.
        "promise": "Both implementations, the comparison and its deliberate-corruption tests are "
                   "in the archive.",
        "contributes": ("The independent second implementation of the frame grading and the "
                        "mature-parent screen, the field-by-field comparison against the "
                        "original over all 231 graded exon pairs and all 190 designs, and the "
                        "deliberate-corruption tests that show the comparison can fail."),
        "patterns": ["research/modalities/aso_independent_verification.py",
                     "research/modalities/aso-independent-verification.json",
                     "research/modalities/tests/test_aso_independent_verification.py"],
    },
    {
        "id": "deposited_documents",
        # ⛔⛔ THE MANIFEST LISTED NEITHER OF THE DOCUMENTS A DEPOSITOR ACTUALLY UPLOADS (2026-08-19).
        # 384 entries, four figure PDFs among them, and not one of the three built PDFs — the two
        # full renderings and the Supporting Information — nor either build stamp. The Declarations
        # promise "a manifest listing every archived file with its SHA-256", so the file whose
        # entire job is to be checkable against the download omitted the download's centrepiece.
        # ⚠ THE STAMPS ARE NOT OPTIONAL AND ARE NOT METADATA. `build_submission_pdf.py` writes into
        # each stamp the SHA-256 of every source document the PDF was rendered from, which is the
        # ONLY way a reader can tell a current PDF from one built before the last edit — mtimes are
        # not evidence, because the regeneration chain rewrites unchanged files. A deposit carrying
        # the PDFs without the stamps ships an assertion with its falsifier removed.
        # ⛔⛔ THIS ROW PROMISED A SUPPORTING-INFORMATION PDF THAT IS NOT BUILT, AND THE PROMISE WAS
        # PUBLISHED. Round 30's regression seat, 2026-09-02: the research article's claim that "two
        # renderings travel with it" was deleted as false in 879284f57 — and this row, which the
        # deposit script writes INTO the published zip, kept saying it. So the archive at
        # 10.5281/zenodo.22229096 carried a manifest promising a document it does not hold, beside a
        # paper stating that document is not built.
        # ★ IT IS THE ONE-OF-A-PAIR CLASS AGAIN (`paper-hardening`, the one-of-a-pair section): the
        # repair was bound to the
        # occurrence in the manuscript rather than to the CLAIM, which had three homes — the paper,
        # this promise, and the SI's own description of itself. Two of the three were missed.
        # ⚠ AND THE INSTRUMENT FOR EXACTLY THIS EXISTS AND NOTHING READS IT: `_promise_still_in_
        # manuscript` flipped true→false when the sentence was deleted, and the manifest was then
        # regenerated, committed, zipped and PUBLISHED with that flag red — `gaps` reports only
        # `promises_resolving_to_no_file`, so a promise whose sentence has left the paper is
        # computed, recorded, and read by no one. Filed rather than fixed inline.
        # ⚠ Superseded, retained (rule 1.2): "Two renderings of this manuscript travel with it and
        # their text is the same", and a `contributes` naming "the Supporting Information rendered
        # from the same builder".
        # ⭐ THE PROMISE TEXT IS THE PAPER'S OWN SENTENCE, VERBATIM, AND THAT IS WHAT MAKES THE
        # `_promise_still_in_manuscript` FLAG MEAN ANYTHING. A paraphrase — however true — is a
        # sentence the manuscript does not contain, so the flag reads False and the row promises
        # something no reader of the paper was ever told. Measured on the first attempt at this
        # repair: a reworded promise flipped the flag red exactly as a deleted one does.
        "promise": "The PDFs in the archive are renderings of the condensed journal article, which "
                   "is a different paper with its own title, abstract and reference list",
        "contributes": ("The built documents a depositor uploads: the version of record in "
                        "submission format, the typeset previews of the same text, and the build "
                        "stamps that record the SHA-256 of every source each PDF was rendered "
                        "from. ⚠ The Supporting Information travels as markdown only — no PDF of "
                        "it is built, which is what the research article now states."),
        # ⛔⛔ AND THEN IT MISSED THE SECOND PAPER ENTIRELY (round 15 seat 4, 2026-08-22). These
        # globs said `-research-article*`, written the day before the condensed journal article was
        # registered — so the deposit carried that article's tables, its references and its
        # generator while omitting the article itself and both of its built PDFs. The submission's
        # own Data and code availability points a NAT editor at this archive.
        # ⚠ THE PATTERN IS NOW `-*article*`, WHICH REACHES BOTH PAPERS AND ANY THIRD. A hand-kept
        # list is what produced both this hole and the 2026-08-19 one recorded above; the fix for a
        # list that goes stale is not a longer list.
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-*article*.pdf",
                     "research/manuscripts/aso/fusion-junction-aso-*article*"
                     ".build-stamp.json"],
    },
    {
        "id": "manuscript_and_figures",
        # ⚠ NOT A PROMISE THE PAPER MAKES — a deposit that omitted the paper and its figures would
        # be useless, so this row exists for the depositor rather than for the availability
        # statement. Kept in the same table so there is one list, not two.
        "verbatim": False,
        "promise": "the manuscript itself and the figures it prints",
        "contributes": ("The submission text, its Supporting Information, and the figure generators "
                        "with their vector and raster output. The figures are generated from the "
                        "same artifacts as the tables, so a reader can regenerate them."),
        # ⛔⛔ THE COVER LETTER CAME OUT OF THE DEPOSIT ON 2026-08-30, AND IT SHOULD NEVER HAVE BEEN
        # IN IT. trimcrae, in session: "We don't need a cover letter until it's time to submit to a
        # publisher. Makes no sense to make one for a preprint." This row's own promise is "the
        # manuscript itself and the figures it prints", and a letter to an editor is neither; the
        # letter's own front matter says so — "It is a submission document, not a scientific record".
        # ⚠ AND DEPOSITING IT COST THIS REPOSITORY THREE SEPARATE INCIDENTS, all the same shape: a
        # status sentence about an outside system, frozen into an immutable public record. Round 21
        # found the deposited copy asserting "every archive link in both papers now resolves" after
        # that claim had been withdrawn. Round 22 found it reading "NOT SENDABLE ... resolves to
        # nothing" inside the very archive whose DOI had just gone live. And for a stretch it was the
        # SINGLE drifted file, which is the whole reason §3-iv of the checklist existed.
        # ★ A READER FOLLOWING THE PUBLIC DOI WAS BEING HANDED A LETTER ADDRESSED TO A JOURNAL
        # EDITOR. Nothing in the Data availability statement promises it, no result depends on it,
        # and removing it deletes a recurring source of false statements in an immutable record
        # rather than merely tidying the archive.
        # ⛔ THE SUPPORTING INFORMATION WAS ABSENT FROM THIS ROW UNTIL 2026-08-16, AND A DEPOSIT
        # MISSING IT IS THE WORST KIND OF HOLE: the main text points into it ("SI §S1") from six
        # places, so a reader following a cross-reference finds nothing and cannot tell whether the
        # method was withdrawn or never written. The row's globs are literal paths, so the split
        # that CREATED the SI could not add it — which is this table's own hand-list warning,
        # firing on the one row whose patterns cannot glob.
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-research-article.md",
                     "research/manuscripts/aso/fusion-junction-aso-supplementary-information.md",
                     "research/manuscripts/figures/aso_*_figure.py",
                     "research/manuscripts/figures/aso-*.pdf",
                     "research/manuscripts/figures/aso-*.png",
                     "research/manuscripts/figures/aso-*.svg",
                     # ⛔ THE FIGURES' TWO GUARDS SHIP WITH THE FIGURES (added 2026-08-17). The
                     # deposit asserts that these PDFs are vector with live text, and that each was
                     # drawn from the artifact currently on disk. An archive carrying the assertion
                     # and not the check leaves a reader unable to falsify either — the same defect
                     # as shipping a test whose code under test is absent, in the other direction.
                     "research/manuscripts/figures/aso_figure_provenance.py",
                     "research/manuscripts/tests/test_aso_figure_provenance.py",
                     "research/manuscripts/tests/test_aso_figures_are_vector_not_raster.py",
                     # ⛔ THE CONDENSED SUBMISSION AND ITS COMPANIONS (round 15 seat 4). This row
                     # names literal paths, so the paper split that created the journal article
                     # could not add it — the row's own warning above, firing a second time.
                     "research/manuscripts/aso/fusion-junction-aso-journal-article.md",
                     "research/manuscripts/aso_archive_manifest.py"],
    },
]

# The manifest never lists itself: its own hash would depend on its own content, and the file could
# then never be idempotent. It is named here so a reader can see the omission is a decision.
SELF_EXCLUDE = {os.path.relpath(OUT, REPO).replace(os.sep, "/")}

#: Distinguishes "work it out yourself" from `None`, which here means "git could not answer".
_MISSING = object()


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tracked_files():
    """Every path git is tracking, repo-relative, or None if git cannot answer.

    ⛔ A DEPOSIT IS WHAT A CHECKOUT CONTAINS, NOT WHAT A WORKING TREE HAPPENS TO HOLD (2026-08-14).
    Step 0 of `scripts/regenerate_aso_chain.sh` re-scores every screen it finds, which materialises
    the 53 deeper re-screens' graded artifacts — files the Methods explicitly release UNGRADED and
    which are therefore never committed. This module globbed the filesystem, so a chain run made it
    hash them: measured that night, `n_files` went 352 -> 405 and 53 untracked files were listed
    with SHA-256s in a deposit manifest, in a commit that was pushed. Nobody can reproduce that
    deposit — the files are in no revision — and the manifest's own step 1 tells a depositor to
    "check out the revision named in `git_revision` and confirm `git status` is clean", which would
    leave 53 of its rows unresolvable.

    ⚠ FAIL-OPEN, AND IT SAYS SO. Without git there is no way to tell tracked from untracked, so the
    inventory falls back to every file it can see and `inventory_limited_to_tracked_files` goes
    false rather than the manifest quietly claiming a property it did not check.
    """
    out = _git("ls-files", "-z")
    if out is None:
        return None
    return frozenset(p for p in out.split("\0") if p)


def _resolve(patterns, tracked=_MISSING):
    """Globs -> sorted repo-relative paths, de-duplicated, TRACKED ONLY where git can say.

    ⚠ `-graded.json` is stripped from every row except the graded row. The screen glob
    `junction-aso-offtarget-*n3.json` matches the re-scores too, and a re-score counted as a screen
    would inflate the screen coverage check below into saying every junction has both arms.
    """
    tracked = _tracked_files() if tracked is _MISSING else tracked
    graded_row = any("-graded" in p for p in patterns)
    out = set()
    for pat in patterns:
        for p in glob.glob(os.path.join(REPO, pat)):
            if not os.path.isfile(p):
                continue
            rel = os.path.relpath(p, REPO).replace(os.sep, "/")
            if rel in SELF_EXCLUDE:
                continue
            if not graded_row and rel.endswith("-graded.json"):
                continue
            if tracked is not None and rel not in tracked:
                continue
            out.add(rel)
    return sorted(out)


def _git(*args):
    """Repository revision, or None. Never fatal: a manifest is still useful in a bare copy."""
    try:
        r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:  # noqa: BLE001
        return None


def _tree_clean_apart_from_this_manifest():
    """Is every file in the archive at its committed content — ignoring the manifest itself?

    ⛔ THE NAIVE VERSION OF THIS FIELD IS A SELF-REFERENCE TRAP, AND IT DEFEATS THE ONE PROPERTY THE
    MODULE HEADER PROMISES. `git status --porcelain == ""` was measured before the write, so on a
    CLEAN tree the sequence was: run 1 reads clean -> writes `true` -> the write itself dirties the
    tree -> run 2 reads dirty -> writes `false`. Two consecutive runs over an unchanged repository
    produced two different files, which is exactly the "run it again, diff, expect nothing" check
    the no-timestamp rule above exists to protect. The trap is invisible on a dirty tree — which is
    how it survived: it was first exercised while a concurrent session held four unrelated files
    modified, so both runs read dirty, agreed, and the hazard read as a passing test.

    ⚠ AND THE STORED VALUE WAS MISLEADING IN THE DIRECTION THAT MATTERS. Any regeneration that
    actually changes the manifest gets committed together with the manifest, so the committed copy
    of a real update permanently recorded `false` — "these hashes were taken against a dirty tree,
    do not trust them" — at precisely the moment they were trustworthy. A provenance field that
    reads its own shadow is worse than no field, because a depositor at step 1 believes it.

    So the manifest's own path is excluded. The question the depositor actually needs answered is
    "are the files I am about to hash and upload at their committed content", and the manifest is
    not one of those files — it is the answer sheet, and it is regenerated at step 2 by definition.
    Porcelain paths are compared against the manifest's repo-relative path; a rename or a
    `-z`-worthy pathological filename would fall through to reporting dirty, which is the safe
    direction (it tells the depositor to look, rather than telling them not to bother).
    """
    porcelain = _git("status", "--porcelain")
    if porcelain is None:
        return None                       # no git here; "unknown", never "clean"
    for line in porcelain.splitlines():
        # ⛔ SPLIT, DO NOT SLICE — `_git` STRIPS ITS OUTPUT AND THE COLUMNS ARE NOT FIXED-WIDTH BY
        # THE TIME THEY ARRIVE (2026-08-13). Porcelain v1 emits "XY <path>", so an unstaged
        # modification is " M <path>" with a LEADING SPACE — which `_git`'s `.strip()` removes
        # before this function ever sees it. `line[3:]` then ate the first character of every such
        # path: "research/…" arrived as "esearch/…", the SELF_EXCLUDE membership test could never
        # match, and the field reported a dirty tree unconditionally.
        # ⚠ WHICH IS THE SAME DEFECT THIS FUNCTION WAS WRITTEN TO REMOVE, one layer down. The
        # docstring above warns that a permanently-false reading is worse than no field because a
        # depositor believes it; the exclusion meant to prevent that was itself inert. A guard that
        # no-ops into the behaviour it replaced produces no symptom — the field simply kept saying
        # what it had always said.
        # `split(maxsplit=1)` handles " M p", "M p", "?? p" and paths containing spaces alike. A
        # rename ("R  old -> new") lands in the else-branch below and reports dirty, which is the
        # safe direction: it tells the depositor to look rather than not to bother.
        parts = line.split(maxsplit=1)
        path = parts[1].strip().strip('"') if len(parts) == 2 else ""
        if path and path not in SELF_EXCLUDE:
            return False
    return True


def _promise_text_found_in_paper(text, phrase):
    """Is this promise still a sentence the manuscript writes?

    ⛔ THE POINT IS THE FALSE DIRECTION. If an editor softens or deletes a promise, the manifest
    would go on shipping files for a claim nobody makes, and — worse — a promise ADDED in revision
    would be invisible here. This flag cannot catch the second case, so it is reported as a flag
    rather than trusted as a guarantee. Matching is on a distinctive fragment, not the whole
    sentence, because the manuscript hard-wraps and a line break is not a wording change.

    ⛔⛔ THE LABEL AND THE PROBE ARE DIFFERENT JOBS, AND CONFLATING THEM MADE THIS FLAG CRY WOLF
    (2026-08-19). Four rows reported `false` at once — `reproduction_command`,
    `inputs_that_make_it_offline`, `canonical_sequence_record`, `reproduction_guards` — and only one
    was a real wording drift. Two of the four had never held a quotation at all: their `promise`
    read as a description ("the regeneration chain the Availability statement names"), so the check
    was comparing a caption against the manuscript and could only ever fail. A row with a `quote`
    key is now checked on THAT and displayed as its `promise`, which keeps `promise_text` readable
    while making the probe an actual fragment of the paper.
    ⚠ THE WRONG FIX WOULD HAVE BEEN TO SET `verbatim: False` ON THE FOUR. That silences the flag on
    exactly the rows whose promises are the most quotable — the offline claim and the reproducibility
    claim are the two sentences a reviewer will test first — and this module's own note says a flag
    that cries wolf is a flag that gets ignored on the row that matters. The prose is right; the
    probe was reading the wrong string.
    """
    probe = " ".join(phrase.split())[:48].lower()
    flat = " ".join(text.split()).lower()
    return probe in flat


#: ⛔ THE SHAPE OF A JUNCTION LABEL, WHICH IS THE VOCABULARY THE `junctions_*` FIELDS SPEAK.
#: `<PARTNER>_e<exon>__NR4A3_e<exon>` — two spliced-transcript coordinates joined by a double
#: underscore, as `junction_label` states it in every screen, panel and design artifact. A filename
#: tag (`taf15e11n3-18mer-deep500-b2`) cannot match it, which is the entire point: the two
#: vocabularies were interchangeable for as long as every seam was screened exactly once, and a
#: deposit field silently changed languages the moment that stopped being true.
JUNCTION_LABEL_RE = re.compile(r"^[A-Z][A-Z0-9]*_e\d+__NR4A3_e\d+$")
JUNCTION_LABEL_EXAMPLE = "EWSR1_e12__NR4A3_e3"


def _labels_only(field, values, res):
    """Sorted junction labels, or a LOUD refusal if anything else tried to enter a junction field.

    ⛔ ASSERTED, NOT CONVENTIONAL, AND THAT IS THE FIX RATHER THAN THE NEW READER ABOVE IT. Swapping
    tags for labels repairs today's values; it does nothing about tomorrow, because the next author
    to add a source here sees a set of strings going into a set of strings and has no way to know
    the field has a vocabulary. This makes the vocabulary a checked property of the artifact.

    ⚠ IT RECORDS AND EXITS NON-ZERO RATHER THAN RAISING, matching this module's rule that a check it
    could not complete is reported in the deposit instead of vanishing into a traceback — a manifest
    that silently omits a field reads as "no gaps".
    """
    bad = sorted(v for v in values if not JUNCTION_LABEL_RE.match(str(v)))
    if bad:
        res["ok"] = False
        res.setdefault("⛔_wrong_vocabulary", {})[field] = {
            "n_rejected": len(bad),
            "rejected": bad[:10],
            "_why": (f"`{field}` holds junction labels like `{JUNCTION_LABEL_EXAMPLE}`. These are "
                     f"not labels — almost certainly filename tags, which is the defect this guard "
                     f"was added for on 2026-08-14. Read the `junction_label` each artifact states "
                     f"rather than slicing its basename."),
        }
    return sorted(v for v in values if JUNCTION_LABEL_RE.match(str(v)))


#: Vendored third-party trees. Their basenames collide with each other (`entry.py`, `sm_io.py`) and
#: nothing in this deposit imports them, so they are kept out of the module index rather than
#: allowed to make a resolution ambiguous.
_VENDORED = "_src/"


def _module_index(tracked):
    """Importable module name -> the tracked repository paths that could satisfy it."""
    idx = {}
    for p in tracked or ():
        if p.endswith(".py") and p.startswith("research/") and _VENDORED not in p:
            idx.setdefault(os.path.basename(p)[:-3], []).append(p)
    return idx


def _imported_names(path):
    """Every top-level module name this file imports, at any nesting depth. [] if unparseable.

    ⚠ LAZY IMPORTS COUNT. `aso_noncoding_acceptor_designs` reaches its grader through an import
    inside a function, and the round-7 finding that the deposit shipped a test without its code
    under test turned on exactly that: an import-closure walk that only read module level found
    neither module. A file needed on one code path is a file the archive has to carry.
    """
    try:
        tree = ast.parse(open(os.path.join(REPO, path), encoding="utf-8").read())
    except (OSError, SyntaxError, ValueError):
        return []
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
            names.add(n.module.split(".")[0])
    return sorted(names)


def _import_closure(seeds, tracked):
    """Repository modules a released module imports but no promise row resolves to.

    ⛔⛔ THIS IS THE ONE HOLE A PROMISE TABLE CANNOT SEE, AND IT HAS OPENED FOUR TIMES. Every row
    above names FILES; what a reader downloads and runs is CODE, and code reaches other code by
    import. Measured 2026-08-19 over the 384-entry manifest: eight modules were imported by a
    released file and absent from the release. `aso_screen_sets.py` was imported by twelve of them —
    including this module — so the archive contained the manifest generator and not what the
    manifest generator imports. `fusion_breakpoints.py` was imported by `junction_aso.py` and
    `nr4a3_fusion_atlas.py`, the two producers the Availability statement names first, so neither
    the design panel nor the junction atlas could be regenerated from the archive at all.
    ⚠ THE FAILURE MODE IS AN ImportError ON A CLEAN DOWNLOAD, which is the worst shape a deposit
    defect can take: it does not look like a missing file, it looks like broken code, and a reviewer
    reasonably concludes the pipeline never ran.
    ⭐ SO IT IS COMPUTED, NOT LISTED. Adding an import tomorrow adds its target to the deposit with
    nobody remembering, which is the same property every glob above has and the reason a hand-list
    was the failure this module exists to prevent. Iterated to a fixed point, because a module
    pulled in this way imports things too.
    ⚠ AND AN AMBIGUOUS NAME IS REPORTED, NEVER GUESSED. Two tracked files with one basename cannot
    be told apart from an import statement, so the name is recorded in the gaps block and no file is
    added — a wrong file in a deposit is worse than a named hole in one.
    """
    idx = _module_index(tracked)
    have, added, ambiguous = set(seeds), [], {}
    queue = [p for p in seeds if p.endswith(".py")]
    while queue:
        cur = queue.pop()
        for name in _imported_names(cur):
            cands = idx.get(name)
            if not cands:
                continue                      # stdlib, third-party, or nothing tracked by that name
            # Python resolves a sibling first, so a same-directory match settles the name outright.
            pick = [c for c in cands if os.path.dirname(c) == os.path.dirname(cur)] or cands
            if len(pick) > 1:
                ambiguous[name] = sorted(pick)
                continue
            if pick[0] not in have:
                have.add(pick[0])
                added.append(pick[0])
                queue.append(pick[0])
    return sorted(added), ambiguous


def _screen_coverage():
    """Which junctions carry BOTH screens, and which gap-resolved screens lack a graded re-score.

    ⚠ DERIVED BY ASKING THE OWNING MODULE, NOT BY COUNTING FILENAMES. Whether a screen can be graded
    at all is `junction_aso_offtarget.screen_is_gap_resolved`, and it exists because a sweep that
    graded a coverage-only screen once announced "4 of 4 with zero predicted cleavage load" — the
    strongest possible claim, manufactured from the absence of the data needed to test it. Re-
    implementing that predicate here would be a second home for it and would eventually disagree.

    ⛔ IF THE IMPORT FAILS THE ANSWER IS NOT "no gaps". A manifest that silently reports a clean
    bill because it could not run the check is the same defect one level up, so the failure is
    recorded in the artifact and the exit code goes non-zero.
    """
    res = {"classifier": "junction_aso_offtarget.screen_is_gap_resolved", "ok": True}
    try:
        sys.path.insert(0, MOD)
        from junction_aso_offtarget import (  # noqa: PLC0415
            screen_is_gap_resolved, screen_orientation_status, ORIENTATION_FILTERED)
    except Exception as exc:  # noqa: BLE001
        res.update({"ok": False,
                    "⛔_unchecked": f"could not import the classifier ({exc}); the coverage and "
                                   "grading gaps below are UNKNOWN, not empty."})
        return res

    # ⭐ THE DEPOSIT INVENTORY IS DELIBERATELY EVERY GEOMETRY, and that is the one place in this
    # repository where pooling is right: this block counts what the ARCHIVE SHIPS, and a deposit
    # that silently stopped listing a geometry would be a worse defect than the one the loader
    # exists to prevent. What it must not do is discover those files by a pattern of its own — the
    # scan goes through `aso_screen_sets`, which measures each screen's geometry and checks it
    # against whatever the screen states, so the inventory is a considered union of named
    # per-geometry sets rather than a glob nobody has looked at since the corpus widened.
    # ⚠ AND THE UNION IS WRITTEN OUT HERE, VISIBLY, which is the property `iter_geometries` is for.
    screens, gap_resolved, ungraded, unfiltered = [], [], [], []
    by_geom = dict(ass.iter_geometries(ass.BLAST_SCREEN, root=os.path.abspath(MOD)))
    every = sorted((s for ss in by_geom.values() for s in ss), key=lambda s: s.name)
    # ⛔ "HAS A COMMITTED GRADED RE-SCORE" IS A QUESTION ABOUT THE REPOSITORY, NOT ABOUT THE DISK
    # (2026-08-14). The field is named `..._with_no_committed_graded_rescore` and was answered with
    # `os.path.exists`, so a chain run — which re-scores every screen it finds — made all 53 gaps
    # disappear the instant the files appeared in the working tree, while the deposit still shipped
    # none of them. That is the fail-quiet direction: the manifest would report a clean bill at
    # precisely the moment its inventory and its gap list disagreed most.
    tracked = _tracked_files()
    for s in every:
        base, screen = s.name, s.artifact
        screens.append(base)
        if screen_orientation_status(screen) != ORIENTATION_FILTERED:
            unfiltered.append(base)
        ok, _why = screen_is_gap_resolved(screen)
        if ok:
            gap_resolved.append(base)
            graded = os.path.relpath(s.path[:-5] + "-graded.json", REPO).replace(os.sep, "/")
            if not (os.path.exists(os.path.join(REPO, graded))
                    and (tracked is None or graded in tracked)):
                ungraded.append(base)

    # ⛔⛔ THE THREE `junctions_*` FIELDS BELOW HOLD JUNCTION LABELS, AND UNTIL 2026-08-14 THEY HELD
    # FILENAME TAGS. The old reader stripped a prefix and `.json` off a basename, so a re-dispatch
    # committed as `...-taf15e1n3-20mer-deep500-b2.json` entered a field named "junctions" as the
    # "junction" `taf15e1n3-20mer-deep500-b2`. That was invisible while every seam was screened once
    # under one name: 38 junctions, 38 tags, and the two vocabularies agreed by coincidence. The
    # gap-length work broke the coincidence — 93 tags against 38 labels — and
    # `junctions_screened_by_blast_arm_only` went from `[]` to three tags, and
    # `junctions_screened_by_exhaustive_arm_only` to one. Both read as coverage GAPS in a deposit
    # manifest. There are none: every one of the 38 junctions carries all three arms.
    #
    # ⭐ THE LABEL IS WHAT THE ARTIFACT STATES ABOUT ITSELF; THE TAG IS WHAT SOMEONE NAMED THE FILE.
    # Only the first can answer "which junctions have one arm of evidence and not the other", which
    # is the question these fields exist for. A tag-space answer is a fact about naming conventions
    # that changes whenever a re-dispatch picks a new suffix, and nobody has ever wanted it.
    #
    # ⚠ POOLED ACROSS GEOMETRIES ON PURPOSE, matching the deposit inventory above it: a seam
    # screened at 16-mer and evaluated at 18-mer has both arms, and reporting it as a gap because
    # the two readings came from different reagent lengths would invent one.
    #
    # ⛔ AND THE VOCABULARY IS ASSERTED RATHER THAN TRUSTED — see `_labels_only`. The old code was
    # not wrong about any single name; it was wrong about which *kind* of name belonged in the
    # field, and nothing could tell, because a set of strings looks like a set of strings.
    def _design_panel_labels():
        """Design panels state their seam under `_breakpoint_model`, not at the top level.

        ⚠ THIS FAMILY IS NOT IN `aso_screen_sets` and is globbed here, which is allowed and is not
        the defect that loader exists for: `junction-aso-designs-*.json` is ONE geometry-agnostic
        family with no gap span applied to it, so there is no window to count over wrongly. What is
        read from it is a label, and the label is what it states.
        """
        out = set()
        for p in sorted(glob.glob(os.path.join(MOD, "junction-aso-designs-*.json"))):
            try:
                with open(p, encoding="utf-8") as fh:
                    lab = (json.load(fh).get("_breakpoint_model") or {}).get("junction_label")
            except (OSError, ValueError):
                continue
            if lab:
                out.add(lab)
        return out

    # ⚠ AN UNLABELLED SCREEN DROPS OUT BY CONSTRUCTION, WHICH RETIRED A HARD-CODED EXCLUSION. This
    # line used to end `- {"bp200-8-gapres"}`: the modelled-seam control screens are not built from
    # a spliced transcript and state no `junction_label`, so in tag space they had to be named and
    # subtracted by hand, and the OTHER one (`bp200-8`) was never subtracted at all. In label space
    # neither is a junction and neither needs mentioning — which is the tell that the vocabulary,
    # not the exclusion list, was the thing that was wrong.
    blast_labels = {s.junction_label for s in every if s.junction_label}
    exhaustive_labels = {s.junction_label
                         for _g, ss in ass.iter_geometries(ass.DESIGN_EVALUATION,
                                                           root=os.path.abspath(MOD))
                         for s in ss if s.junction_label}
    design_labels = _design_panel_labels()

    res.update({
        "n_screens_committed": len(screens),
        "n_screens_gap_resolved": len(gap_resolved),
        "n_screens_coverage_only_cannot_be_graded": len(screens) - len(gap_resolved),
        "n_screens_not_orientation_filtered_counts_are_upper_bounds": len(unfiltered),
        "screens_not_orientation_filtered": sorted(unfiltered),
        "gap_resolved_screens_with_no_committed_graded_rescore": sorted(ungraded),
        "_junction_fields_vocabulary": (
            "The three `junctions_*` fields below are JUNCTION LABELS as each artifact states them "
            f"(`{JUNCTION_LABEL_EXAMPLE}`), never filename tags. `n_junctions_known` is the size of "
            "that vocabulary; a value in any of those fields that is not one of them fails the "
            "build rather than being deposited."),
        "n_junctions_known": len(blast_labels | exhaustive_labels | design_labels),
        "junctions_with_a_design_panel_but_no_screen": _labels_only(
            "junctions_with_a_design_panel_but_no_screen", design_labels - blast_labels, res),
        "junctions_screened_by_blast_arm_only": _labels_only(
            "junctions_screened_by_blast_arm_only", blast_labels - exhaustive_labels, res),
        "junctions_screened_by_exhaustive_arm_only": _labels_only(
            "junctions_screened_by_exhaustive_arm_only", exhaustive_labels - blast_labels, res),
    })
    return res


def build():
    with open(PAPER, "r", encoding="utf-8") as fh:
        paper = fh.read()

    seen, files, promise_rows = {}, [], []
    for row in PROMISES:
        resolved = _resolve(row["patterns"])
        for rel in resolved:
            # ★ FIRST PROMISE WINS THE CONTRIBUTION LINE, and the rest are recorded as also-serves.
            # A file that answers two promises is normal (the screen module both screens and
            # re-scores); listing it twice with two sizes would make the totals wrong.
            if rel in seen:
                seen[rel]["also_serves"].append(row["id"])
                continue
            full = os.path.join(REPO, rel)
            entry = {"path": rel,
                     "bytes": os.path.getsize(full),
                     "sha256": _sha256(full),
                     "serves": row["id"],
                     "also_serves": [],
                     "contributes": row["contributes"]}
            seen[rel] = entry
            files.append(entry)
        promise_rows.append({
            "id": row["id"],
            "promise_text": row["promise"],
            "n_files": len(resolved),
            "files": resolved,
            # ⚠ `quote` WHERE THE ROW HAS ONE, `promise` OTHERWISE — see
            # `_promise_text_found_in_paper`. The displayed `promise_text` above stays the readable
            # label either way, so a reader of the manifest is never shown a sentence fragment
            # where a promise belongs.
            "_promise_still_in_manuscript": (
                _promise_text_found_in_paper(paper, row.get("quote", row["promise"]))
                if row.get("verbatim", True) else "n/a — descriptive label, not a quotation"),
            "⛔_UNMAPPED": not resolved,
        })

    # ★ THE CLOSURE IS RESOLVED LAST AND ENTERS AS ITS OWN ROW, so a reader can see exactly which
    # files are here because a promise names them and which are here because released code imports
    # them. Folding them into the nearest promise row would have hidden the distinction and made
    # the row's file list stop being the answer to "you said X is released — where is it?".
    tracked_now = _tracked_files()
    closure, ambiguous_imports = _import_closure([e["path"] for e in files], tracked_now)
    for rel in closure:
        full = os.path.join(REPO, rel)
        entry = {"path": rel,
                 "bytes": os.path.getsize(full),
                 "sha256": _sha256(full),
                 "serves": "import_closure",
                 "also_serves": [],
                 "contributes": ("Imported by a released module. Not named by any availability "
                                 "promise; present because the code the promises DO name cannot "
                                 "be imported without it.")}
        seen[rel] = entry
        files.append(entry)
    promise_rows.append({
        "id": "import_closure",
        "promise_text": ("the modules released code imports (derived from the code, not promised "
                         "by a sentence)"),
        "n_files": len(closure),
        "files": closure,
        "_promise_still_in_manuscript": "n/a — derived from the released code, not a quotation",
        "⛔_UNMAPPED": False,
    })

    files.sort(key=lambda e: e["path"])
    coverage = _screen_coverage()
    total = sum(e["bytes"] for e in files)

    # ★ THE IDENTITY OF THE ARCHIVE, AS DISTINCT FROM THE IDENTITY OF THE REPOSITORY. A digest over
    # the sorted (path, sha256) pairs answers the depositor's real question — "is this the same set
    # of bytes I looked at yesterday?" — which `git_revision` cannot, because the revision moves
    # whenever anything in the repository moves, archived or not. Two manifests sharing this digest
    # describe identical payloads no matter how many commits separate them, so a DOI minted against
    # one is valid for the other. Derived from the file hashes already computed above, never from a
    # re-read, so it cannot disagree with the list it summarises.
    # ⛔ THE PAYLOAD IS MOSTLY FILE TYPES A MANUSCRIPT UPLOADER DOES NOT TAKE, and that is the one
    # deposit defect that stops the submission at the form rather than at review. A preprint
    # server's supplementary uploader accepts a short list of document, image and container types;
    # `.json`, `.csv`, `.fasta`, `.md` and `.sh` are not documents to it. This census is DERIVED
    # from the file list so the depositor sees the shape of the problem before meeting it, and the
    # answer is already step 3 below: one container, uploaded once.
    # ⚠ NO ACCEPTED-TYPE LIST IS RESTATED HERE. Which extensions a given server takes is a fact
    # about that server's current form, it changes without notice, and a list typed into this file
    # from memory would be exactly the kind of unsourced claim the rest of this repository refuses.
    # The depositor reads it off the uploader.
    by_ext = {}
    for e in files:
        ext = os.path.splitext(e["path"])[1].lower() or "(no extension)"
        row = by_ext.setdefault(ext, {"n_files": 0, "bytes": 0})
        row["n_files"] += 1
        row["bytes"] += e["bytes"]
    payload_file_types = {
        "_what": ("Extension census of the payload, derived from the file list. A preprint or "
                  "journal uploader that accepts only document, image and container types cannot "
                  "take most of these one by one; step 3 below builds the single container that "
                  "sidesteps the question entirely. Check the accepted types on the uploader "
                  "itself — none is asserted here."),
        "by_extension": dict(sorted(by_ext.items(),
                                    key=lambda kv: (-kv[1]["n_files"], kv[0]))),
        "_readme_for_the_container": (
            "Give the zip a plain-text README carrying the deposit title, the author, the statement "
            "that the manuscript is a preprint, and the archive DOI once reserved — the same four "
            "facts step 4 puts in the deposition record. Compose it from `_what_this_is` and "
            "`how_to_reproduce_offline` above rather than typing it: those are derived and this "
            "would not be."),
    }

    digest = hashlib.sha256()
    for e in files:
        digest.update(f"{e['path']}\0{e['sha256']}\n".encode("utf-8"))
    content_digest = digest.hexdigest()

    unmapped = [r["id"] for r in promise_rows if r["⛔_UNMAPPED"]]
    # ⛔⛔ A PROMISE WHOSE SENTENCE HAS LEFT THE PAPER IS A GAP, AND UNTIL 2026-09-02 IT WAS COMPUTED
    # AND READ BY NOBODY. `_promise_still_in_manuscript` is derived for every row; `gaps` reported
    # only `promises_resolving_to_no_file`, so the flag could go red and nothing anywhere failed.
    # ⚠ MEASURED, and it reached a PUBLISHED record: round 29 deleted the research article's false
    # claim that two renderings travel with the deposit, this flag flipped true→false on the
    # `deposited_documents` row, and the manifest was then regenerated, committed, zipped and
    # published at 10.5281/zenodo.22229096 still promising a Supporting Information PDF that is not
    # built. Round 30's regression seat found it; the flag had known for three commits.
    # ★ THE TWO GAPS ARE DIFFERENT QUESTIONS AND BOTH BELONG HERE: `promises_resolving_to_no_file`
    # asks "does the archive HOLD what this row promises?", and this one asks "does the PAPER still
    # MAKE the promise this row is keeping?". A row can pass either and fail the other.
    # ⛔ `n/a` IS NOT FALSE. Rows whose promise is derived from released code rather than quoted from
    # the manuscript record a string beginning "n/a"; only an explicit False counts, so a row that
    # never claimed to be quotable is not reported as drifted.
    promises_not_in_manuscript = [r["id"] for r in promise_rows
                                  if r.get("_promise_still_in_manuscript") is False]
    gaps = {
        "_what": ("Every question a reviewer would put to the availability statement, answered "
                  "from the artifacts rather than from a note. An empty list here is a reading, "
                  "not a reassurance."),
        "promises_resolving_to_no_file": unmapped,
        "promises_whose_sentence_is_no_longer_in_the_manuscript": promises_not_in_manuscript,
        "screen_coverage": coverage,
        "import_closure": {
            "_what": ("Modules pulled in because released code imports them rather than because a "
                      "promise names them. A non-empty list is not a defect in this manifest; it is "
                      "the measure of how far the promise table falls short of an importable "
                      "archive, and it is why the closure is computed rather than listed."),
            "n_added": len(closure),
            "added": closure,
            # ⚠ AN AMBIGUOUS IMPORT IS A NAMED HOLE, NOT A GUESS — see `_import_closure`. Non-empty
            # here means the archive may be missing a module and this file says which name.
            "⛔_ambiguous_and_therefore_not_added": ambiguous_imports,
        },
        "documents_with_no_build_stamp": sorted(
            os.path.relpath(p, REPO).replace(os.sep, "/")
            for p in glob.glob(os.path.join(ASO, "*.pdf"))
            if not os.path.exists(p[:-4] + ".build-stamp.json")
            and os.path.relpath(p, REPO).replace(os.sep, "/") in seen),
        "_documents_with_no_build_stamp_why": (
            "A deposited PDF whose stamp is absent cannot be shown current: the stamp is the only "
            "record of which source documents it was rendered from, and mtimes are not evidence "
            "because the regeneration chain rewrites unchanged files. Listed rather than "
            "assumed-fine; the fix belongs in build_submission_pdf.py, not here."),
        "⚠_known_and_deliberate": [
            "✅ CLOSED 2026-08-13. The Europe PMC prior-art corpora behind the '5,153 unique "
            "records' first-in-kind statement live on the `literature-cache` branch and so were "
            "outside a deposit built from this one. The identifiers, per-corpus counts and their "
            "overlap are now exported to fusion-junction-aso-priorart-evidence.json and are in "
            "this manifest. The arithmetic re-derives: 4,252 + 1,133 = 5,385 raw, minus 232 in "
            "both corpora, gives 5,153 unique, matching the Introduction. The full texts are NOT "
            "exported and are not what the claim rests on.",
            "✅ CLOSED 2026-08-13. The Availability paragraph names five recomputations that "
            "run offline, and the fifth — the chance baseline — did not run at all: `_uniform` "
            "raised on a panel set holding both two- and three-seam multi-junction oligos. The "
            "field is now a scalar when the set is uniform and a range when it is not, and the "
            "module runs. Verified in both directions: the plain invocation exits 0, and the "
            "pinned invocation reproduces the committed content byte-identically.",
            "The BLAST arm of the specificity screen calls NCBI over the network when SCREENING. "
            "Nothing in the manuscript re-runs it: every reported count is read from the committed "
            "screen artifacts, and the graded re-score is explicitly offline "
            "(`junction_aso_offtarget.grade_panel`: 'NO NETWORK, NO RE-BLAST'). Re-deriving the "
            "paper from the archive is offline; re-generating the screens from scratch is not.",
        ],
    }

    return {
        "_what_this_is": (
            "The deposit manifest for the fusion-junction ASO submission, whose title and article "
            "type are not restated here — they have one home, "
            "research/manuscripts/aso/fusion-junction-aso-research-article.md. "
            "It names every file the manuscript's "
            "availability statements promise, proves each one exists at a stated size and SHA-256, "
            "says in one line what each contributes, and records the gaps. It is the working list "
            "the deposit is built from, and the record against which a published version's "
            "contents can be checked. ⚠ Corrected 2026-08-31 (round 24): this said the DOI it "
            "mints \"fills the manuscript's two remaining placeholders\", and no placeholder has "
            "survived since the first version — each new DOI REPLACES the one both papers "
            "print."),
        "_generated_by": "research/manuscripts/aso_archive_manifest.py",
        "_derived_never_typed": (
            "Every path is resolved by glob from the promise it serves; every size and hash is "
            "read from the working tree. Nothing in the file list is hand-entered, so a screen "
            "added or deleted after this was written changes the manifest without anyone "
            "remembering to."),
        "_cost": "$0 — reads the working tree, hashes it, writes one JSON. No network, no rental.",
        "_no_timestamp_on_purpose": (
            "Two runs over an unchanged tree must produce byte-identical output; that is the only "
            "cheap check a reader has that this file is derived rather than edited. The archive's "
            "identity is the git revision below, which is a fact about content."),
        "_what_this_is_not": [
            # ⚠ CORRECTED 2026-08-31 (round 24, hostile referee). This read "Nothing here has been
            # uploaded, registered or reserved" while `deposition_doi` above names a RESERVED DOI
            # and `emc-aso-archive.zip` is already uploaded to its draft — and `self_entry`
            # marks this file as travelling WITH the deposit, so the false half rode into the
            # archive. ★ THE TRUE STATEMENT IS ABOUT THIS MODULE, NOT ABOUT THE RECORD: the module
            # reserves nothing and calls nothing; `scripts/zenodo_deposit.py` does both, and
            # `research/manuscripts/aso/deposit-state.json` is where what-is-reserved lives.
            "Not a deposit, and not a record of one. THIS MODULE uploads nothing, registers "
            "nothing and makes no network call of any kind — it hashes the working tree and "
            "writes JSON. ⚠ The DOI in `deposition_doi` above IS reserved, and may already be "
            "published; scripts/zenodo_deposit.py performs those acts and "
            "research/manuscripts/aso/deposit-state.json records which of them has happened.",
            "Not a claim that the archived predictions are correct. Every count in the deposit is "
            "a prediction from sequence search; no off-target activity and no RNase-H cleavage was "
            "measured anywhere in this work.",
            "Not a licence statement. The depositor chooses the licence at step 4 below.",
        ],
        # ⛔ THE DEPOSITION'S OWN DOI, AND THE MANUSCRIPT MUST NOT TYPE IT TWICE FROM MEMORY. It is
        # printed in two places in the article — Methods → Availability and Declarations → Data and
        # code availability — which is exactly the shape CLAUDE.md rule 1 exists for, so it lives
        # here and `pinned-figures.json` holds the copies together. Reserved on Zenodo before the
        # deposition was published (`scripts/zenodo_deposit.py`), which is what lets the archive
        # carry the manuscript that cites it rather than the citation trailing the deposit.
        # ⚠ NOT DERIVED — it is issued by Zenodo and can only be transcribed. It is pinned so that
        # a transcription error appears as a linter failure rather than as a citation that resolves
        # to somebody else's record.
        # ⚠ VERSION FOUR, 2026-09-01. Read out of Actions run 33523360707's log — "reserved DOI :
        # 10.5281/zenodo.22229096" — and NOT inferred from the deposition number, even though all
        # four versions have now matched that way. Four matches is a pattern, not a reading, and
        # CLAUDE.md's repo-basics rule forbids writing an identifier from recollection.
        # ⚠ THAT SENTENCE FIRST CITED THE RULE WITH A BARE SECTION MARK AND TURNED A GUARD RED.
        # Every section-mark reference in this file resolves against the ARTICLE's own sections
        # (`test_every_section_cross_reference_resolves`), because three such pointers here once
        # survived a renumber that made their target not exist. The guard was right and the citation
        # was ambiguous; this file's convention is "CLAUDE.md rule 1", with no section mark.
        # ⛔ AND WRITING THIS NOTE REINTRODUCED THE FAULT ONCE: quoting the offending reference
        # verbatim is itself a reference, and the guard reads the whole file. It went red a second
        # time on the explanation of why it went red the first time. Describe the shape, never
        # reproduce it — the same lesson the ledger's price guard taught the same day.
        # ⚠ SUPERSEDED, RETAINED (rule 1.2): 10.5281/zenodo.22182180, version three, published
        # 2026-08-31. It remains published and resolves; the concept DOI 10.5281/zenodo.22028915
        # always points at the newest version. It is superseded because round 28 repaired two
        # DEPOSITED files — the journal article's `need`→`prefer` correction and the
        # `aso_parent_null.py` header that contradicted the paper's "Ten" — so the archive it holds
        # is no longer the archive this paper describes.
        "deposition_doi": "10.5281/zenodo.22229096",
        "git_revision": _git("rev-parse", "HEAD"),
        # ⚠ EXCLUDES THE MANIFEST ITSELF, AND THE EXCLUSION IS THE WHOLE POINT — see
        # `_tree_clean_apart_from_this_manifest`. `null` means "no git available", never "clean".
        "git_tree_is_clean_apart_from_this_manifest": _tree_clean_apart_from_this_manifest(),
        # ⚠ `git_revision` MOVES ON EVERY COMMIT, INCLUDING COMMITS THAT TOUCH NO ARCHIVED FILE, so
        # `--check` goes red after any commit and must NOT be wired into preflight as a gate: it
        # would cry wolf on every push and be switched off, which is how a real staleness would then
        # be missed. It is a PRE-DEPOSIT check (step 2), run deliberately by a human at the moment
        # the hashes have to be true. The field below is what makes that distinction checkable —
        # a reader comparing it against the file list can tell "the archive moved" from "the
        # repository moved around a stationary archive".
        # ⛔ THE INVENTORY IS TRACKED FILES ONLY — see `_tracked_files`. `false` means git could not
        # answer and the inventory therefore includes whatever was in the working tree, which is a
        # deposit nobody can reproduce from a revision. It is stated rather than assumed because
        # this manifest once shipped 53 untracked files with SHA-256s beside them.
        "inventory_limited_to_tracked_files": _tracked_files() is not None,
        "archive_content_digest": content_digest,
        "n_files": len(files),
        # ⛔⛔ THE FILE LISTING EVERY ARCHIVED FILE OMITTED ONE, AND SAID SO NOWHERE A READER LOOKS
        # (2026-08-19). `SELF_EXCLUDE` carried a one-line reason in the SOURCE; the deposit carried
        # none, so a reviewer diffing the download against `files` found the manifest missing and
        # had no way to tell a deliberate exclusion from a stale list. The Declarations promise is
        # "a manifest listing every archived file with its SHA-256" — an omission that is correct
        # and unexplained reads exactly like one that is not.
        "self_entry": {
            "path": os.path.relpath(OUT, REPO).replace(os.sep, "/"),
            "travels_with_the_deposit": True,
            "in_the_files_list_below": False,
            "sha256": None,
            "_why_no_hash": (
                "A file cannot state its own SHA-256: appending the hash changes the bytes that "
                "were hashed, so there is no fixed point to write. A second pass would produce a "
                "manifest whose recorded self-hash is the hash of the manifest before that hash "
                "was recorded — a value that is wrong about the only file it describes."),
            "_why_not_counted": (
                "It is excluded from `files`, `n_files`, `total_bytes` and "
                "`archive_content_digest` for the same reason, which is also what keeps two runs "
                "over an unchanged tree byte-identical — the property this module's header calls "
                "the only cheap check a reader has that the file is derived rather than edited."),
            "how_a_reader_checks_it_anyway": (
                "Two ways, neither needing a self-hash. (1) Re-derive it: check out `git_revision` "
                "and run `python3 research/manuscripts/aso_archive_manifest.py --check`, which "
                "rebuilds the whole file and exits non-zero on any difference. (2) Compare the "
                "downloaded copy's `sha256sum` against the value the deposition record states — "
                "step 4 below tells the depositor to record it there, which is the one place it "
                "can live without being self-referential."),
        },
        "total_bytes": total,
        "total_mib": round(total / (1024 * 1024), 3),
        "payload_file_types": payload_file_types,
        "how_to_deposit_and_mint_the_doi": [
            "1. Check out the revision named in `git_revision` and confirm `git status` is clean. "
            "The manifest's hashes are only meaningful against that tree.",
            "2. Re-run this module (`python3 research/manuscripts/aso_archive_manifest.py "
            "--check`). A non-zero exit means the tree moved after the manifest was written; "
            "regenerate before depositing.",
            "3. Build the payload from the `files` list below — for example: "
            "`python3 -c \"import json,zipfile;m=json.load(open('research/manuscripts/aso/"
            "fusion-junction-aso-archive-manifest.json'));z=zipfile.ZipFile('emc-aso-archive.zip',"
            "'w',zipfile.ZIP_DEFLATED);[z.write(f['path']) for f in m['files']];z.write("
            "'research/manuscripts/aso/fusion-junction-aso-archive-manifest.json');z.close()\"` "
            "— then verify the archive's own SHA-256 list against `files` before uploading.",
            "3b. Record the manifest's OWN SHA-256 outside the manifest — "
            "`sha256sum research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` — and "
            "paste it into the deposition description at step 4. See `self_entry` above: this file "
            "cannot carry its own hash, so the deposition record is where that hash lives.",
            "4. Create the deposition (Zenodo: New upload -> Dataset/Software; upload the zip; "
            "title 'Code and artefacts for: fusion-junction antisense oligonucleotides in "
            "extraskeletal myxoid chondrosarcoma'; author and ORCID; licence — CC-BY-4.0 for the "
            "artefacts and MIT or Apache-2.0 for the code is the usual pairing; keywords "
            "'extraskeletal myxoid chondrosarcoma', 'EWSR1::NR4A3', 'antisense oligonucleotide', "
            "'gapmer', 'fusion junction'). Attach `README` = the `_what_this_is` and "
            "`how_to_reproduce_offline` blocks of this file.",
            "5. RESERVE the DOI before publishing the deposition (Zenodo: 'Reserve DOI'). This is "
            "what makes step 6 possible: the manuscript can cite the DOI in the same version that "
            "is deposited, instead of citing a DOI that does not exist yet.",
            # ⚠ CORRECTED 2026-08-31 (round 24). This instructed pasting into "two '[ARCHIVE DOI]'
            # placeholders", and no placeholder survives in either paper — both print a real DOI,
            # which every version since has REPLACED rather than filled. An instruction naming a
            # slot that no longer exists sends its reader looking for one.
            "6. Replace the archive DOI the manuscripts currently print with the newly reserved "
            "one — in the condensed article's Data availability, in the extended report's two "
            "availability statements, and in the sequence files. "
            "Record it as `deposition_doi` in this module, which is where the article transcribes "
            "it from. ⚠ Superseded, retained: \"Register the DOI in "
            "research/manuscripts/pinned-figures.json so the consistency linter holds the two "
            "copies together\" — it cannot. lint_consistency.py reads every `artifact_figures` "
            "entry through float(), so that registry holds NUMBERS, and pinning a DOI there fails "
            "as `A-key-missing ... (ValueError)`, naming a missing key that is present. The two "
            "copies are held together by "
            "research/manuscripts/tests/test_aso_deposition_doi_is_one_fact.py instead.",
            "7. Publish the deposition, then re-run "
            "`PREFLIGHT_FULL=1 ./scripts/preflight.sh` before submitting. Publishing is "
            "irreversible on Zenodo: the files of a published version cannot be edited, only "
            "superseded by a new version under the same concept DOI.",
            "8. If the gaps block below is non-empty, decide each one BEFORE step 7 — either "
            "close it (generate the missing artefact) or narrow the manuscript's wording. A "
            "promise that outruns the deposit is the one defect a reader will find first.",
        ],
        "how_to_reproduce_offline": [
            "Re-derive the tables from the artifacts: "
            "`python3 research/manuscripts/submission_tables.py` — reads the atlas, the locus "
            "collapse, the chance baseline and the per-junction screens; writes no network call.",
            "Re-derive the graded re-scores under both discrimination bounds: "
            "`python3 research/modalities/junction_aso_offtarget.py --rescore "
            "research/modalities/junction-aso-offtarget-<junction>.json` — the hit set is read "
            "from the committed screen and held fixed; only the scoring is recomputed.",
            "Re-derive the junction atlas: `python3 research/modalities/nr4a3_fusion_atlas.py` — "
            "reads the committed transcript cache (emc-construct-inputs.json) rather than "
            "Ensembl.",
            "Re-run the reproduction guards: "
            "`python3 -m pytest research/modalities/tests/test_aso_submission_numbers.py "
            "research/modalities/tests/test_junction_aso_graded.py`.",
            "⚠ What is NOT offline: re-running the BLAST arm of the specificity screen from "
            "scratch (`junction_aso_offtarget.py` screening mode) queries NCBI, and re-running the "
            "exhaustive arm from scratch downloads the GRCh38.p14 RefSeq RNA set. Neither is "
            "needed to reproduce any number reported in the manuscript, all of which are read from "
            "the committed screen artifacts in this archive.",
        ],
        "gaps": gaps,
        "promises": promise_rows,
        "files": files,
    }


#: Fields that move with the REPOSITORY rather than with the archive. `git_revision` advances on
#: every commit, including commits touching no archived file, and the cleanliness flag flips while a
#: session has edits in progress. Excluding both from the INVENTORY DIFF is what stops the
#: cry-wolf failure documented in `_archive_only`, and that part is unchanged.
#: ⚠ SUPERSEDED, RETAINED: this note used to end "Neither says anything about whether the hash list
#: is right." That is true of `git_revision` and FALSE of the cleanliness flag, and the difference
#: is AUT-PD-016. A `false` flag says the hash list was taken while files were uncommitted, so a
#: hash in it may describe content that is in no commit at all — which is precisely a statement
#: about whether the hash list is right. Being wrong about that is why the flag sat on `main`
#: reading `false` with nothing listening. It is still dropped from the diff; it is now checked
#: SEPARATELY, as a precondition, by `_dirty_tree_refusal` below.
_REPO_STATE_FIELDS = ("git_revision", "git_tree_is_clean_apart_from_this_manifest")

#: The one value of the cleanliness flag under which the hash list is verifiable against a commit.
#: ⛔ THE TEST IS `is True`, NOT TRUTHINESS, AND NOT `!= False`. The field is tri-state by design
#: (`_tree_clean_apart_from_this_manifest` returns None for "no git here", explicitly documented as
#: "unknown, never clean"), and a manifest missing the key entirely is the shape this guard would
#: take if someone deleted the field to clear a red. Unknown provenance and absent provenance are
#: both refused, because a deposit artifact whose hashes cannot be tied to a commit is not
#: depositable whatever the reason.
_CLEAN_FLAG = "git_tree_is_clean_apart_from_this_manifest"


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# ⛔⛔ A REVISION RECORDED BEFORE THE PUSH DIES IN THE REBASE THAT PUSHES IT (AUT-PD-141, -175, -195)
# ═══════════════════════════════════════════════════════════════════════════════════════════════
# `git_revision` is stamped from HEAD at generation time and five deposited PDFs print it as their
# provenance line. `git rebase origin/main` before a push — the routine move when a concurrent
# session has moved the trunk — rewrites every local commit, so a revision recorded at a LOCAL HEAD
# reaches the trunk naming a commit that exists only in this container's reflog.
#
# ★ THE MECHANISM, MEASURED RATHER THAN ARGUED (2026-09-01, S7-CHAIN, two-clone A/B race):
#     recorded a LOCAL-ONLY HEAD  -> after one racing rebase: `git cat-file -e` still RESOLVES (the
#                                    reflog), `git branch -a --contains` is EMPTY, and
#                                    `git merge-base --is-ancestor <rev> origin/main` exits non-zero.
#     recorded a PUSHED tip       -> after TWO racing rebases: still contained in `origin/main`, still
#                                    an ancestor. Nothing rewrote it, because origin's history is
#                                    never rewritten.
#
# ★★ SO THE DESIGN DECISION IS: KEEP THE COMMIT SHA, AND MAKE THE MOMENT IT IS TAKEN CHECKABLE.
# The alternative on the table (AUT-PD-195 candidate 3) was to record a content digest instead,
# "the only option immune to the mechanism rather than defending against it". That reasoning is
# wrong in two ways and the second is decisive:
#   (1) A PUSHED SHA IS EQUALLY IMMUNE. `origin/main` is append-only in this repository, so a commit
#       that is on origin at recording time is an ancestor of every later origin tip, forever. It is
#       not a defence against the rebase; the rebase cannot reach it.
#   (2) THE CONTENT DIGEST ALREADY EXISTS AND ANSWERS A DIFFERENT QUESTION. `archive_content_digest`
#       is right there in this manifest and is what `deposit-state.json` corroborates against.
#       Replacing the sha with a digest would duplicate that field (CLAUDE.md rule 1: one fact, one
#       place) while DESTROYING the only thing the sha does — name a point in history a reader can
#       check out. The deposit's own step 1 is "check out the revision named in `git_revision`", and
#       a tree hash is not checkoutable.
#
# ⛔ AND IT IS A CHECK, NOT A CONVENTION. AUT-PD-141 is explicit that "regenerate after every rebase"
# fails as a remembered pairing (AUT-PD-130). The single bit that separates the two measured cases is
# available AT RECORDING TIME — `git branch -r --contains HEAD` was `origin/main` in one and empty in
# the other, before any rebase happened — so it is computed here and reported, at the moment the
# mistake is made rather than after CI has paid for it.
_REVISION_DURABILITY_FIX = (
    "Fetch and rebase FIRST, then regenerate: `git fetch origin && git rebase origin/main && "
    "python3 research/manuscripts/aso_archive_manifest.py`. That records a commit that is already "
    "on origin, which no later rebase can rewrite. If the push then races, rebase and regenerate "
    "again — a retry alone re-pushes the dead sha.")


def _revision_durability(rev):
    """Will `rev` still name a commit after the rebase that pushes it? Returns (state, detail).

    ★ FOUR STATES, AND THE UNCHECKABLE ONE IS NAMED RATHER THAN FOLDED INTO "fine". CLAUDE.md §4:
    an absent reading is not a reading of absence.

      PUBLISHED    a remote-tracking ref contains it. A rebase cannot rewrite it — origin's history
                   is append-only — so it survives whatever happens to the local branch.
      LOCAL_ONLY   it resolves here and NO remote-tracking ref contains it. This is the defect: the
                   next rebase orphans it and every guard downstream still reads a well-formed sha.
      ORPHANED     it does not resolve at all. The rebase already happened.
      UNCHECKED    git could not answer, or this clone has no remote-tracking refs, or the commit is
                   outside a shallow clone's graft boundary.

    ⚠ SHALLOWNESS IS NOT A BLANKET DEGRADE HERE, AND THAT IS DELIBERATE. This sandbox reports
    `--is-shallow-repository: true` while holding 10,974 commits back to 2026-08-04, so degrading on
    that flag alone would make the check answer UNCHECKED in the one place it most needs to run. The
    honest boundary is the OBJECT: if the commit resolves, `--contains` walked a graph that holds it
    and its answer is exact; if it does not resolve, shallowness is a live explanation and the
    reading is refused instead of reported as ORPHANED.
    """
    if _git("rev-parse", "--git-dir") is None:
        return "UNCHECKED", "git cannot answer here"
    remote_refs = _git("for-each-ref", "--format=%(refname)", "refs/remotes")
    if not remote_refs:
        return "UNCHECKED", ("this clone has no remote-tracking refs, so there is nothing a "
                             "revision could be published to")
    resolves = _git("cat-file", "-e", "%s^{commit}" % rev) is not None
    if not resolves:
        if _git("rev-parse", "--is-shallow-repository") == "true":
            return "UNCHECKED", ("%s is outside this shallow clone's graft boundary, so whether it "
                                 "exists cannot be decided here" % rev[:12])
        return "ORPHANED", ("%s is not a commit in this repository at all — the rebase that would "
                            "orphan it has already happened" % rev[:12])
    containing = _git("for-each-ref", "--contains", rev, "--format=%(refname)", "refs/remotes")
    if containing:
        return "PUBLISHED", containing.splitlines()[0]
    return "LOCAL_ONLY", ("%s resolves here but no remote-tracking ref contains it, so it exists "
                          "only in this clone" % rev[:12])


def _revision_durability_report(rev):
    """The human-readable line for `rev`'s durability, or None when it is PUBLISHED."""
    state, detail = _revision_durability(rev)
    if state == "PUBLISHED":
        return None
    if state == "UNCHECKED":
        return ("⚠ REVISION DURABILITY UNCHECKED: %s. The manifest records git_revision %s; whether "
                "it survives a rebase was NOT decided here." % (detail, rev[:12]))
    return (
        "⛔ %s REVISION: %s.\n"
        "  Every deposited PDF prints this sha as its provenance line and the deposit's own step 1\n"
        "  is `git checkout` it. A rebase before the push rewrites any commit that is not already on\n"
        "  origin, so this manifest is one `git push` away from naming a commit no clone can\n"
        "  resolve — and nothing downstream can tell, because an orphaned sha is still a well-formed\n"
        "  sha.\n"
        "  ⭐ %s" % (state, detail, _REVISION_DURABILITY_FIX))


def _dirty_tree_refusal(old_text):
    """The refusal message for a manifest generated against a dirty tree, or None if it is sound.

    ⛔ AUT-PD-016, MEASURED ON `main` 2026-08-27 RATHER THAN HYPOTHESISED. The manifest committed at
    ae7930ddb names `git_revision` 21c733cd and asserts sha256 d6c41c2e… for
    research/manuscripts/submission-metrics.json. At 21c733cd that file is d971b2f9…. The asserted
    bytes were uncommitted working-tree content at generation time, committed only later — inside
    ae7930ddb itself. So a reader who does the one thing this artifact invites, `git checkout` the
    revision it names and verify, gets a mismatch on a file that revision cannot produce.
    ⚠ THE MANIFEST SAID SO ITSELF THE WHOLE TIME. It recorded that flag as `false`, whose meaning
    (see `_tree_clean_apart_from_this_manifest`) is "these hashes were taken against a dirty tree,
    do not trust them" — and NOTHING READ IT. `_archive_only` dropped it from the comparison for a
    good reason and no other caller looked, so the only honest field in the defect governed nothing.

    ⭐ THIS READS THE MANIFEST ON DISK, NEVER THE FRESHLY BUILT ONE, AND THE DISTINCTION IS THE
    WHOLE GUARD. The on-disk file is the artifact that ships; its flag is a fact about how it was
    made. The freshly built flag is a fact about the CURRENT tree, which is dirty during any
    ordinary commit loop — gating on that would paint preflight red for every session with an edit
    in flight, which is the cry-wolf pattern this module has already been burned by twice.
    """
    try:
        old = json.loads(old_text)
    except ValueError:
        return None                       # unreadable JSON is the callers' existing failure to report
    if not isinstance(old, dict):
        return None
    flag = old.get(_CLEAN_FLAG, "__missing__")
    if flag is True:
        return None
    if flag == "__missing__":
        detail = ("the manifest on disk has no `%s` field at all" % _CLEAN_FLAG)
    elif flag is None:
        detail = ("the manifest on disk records `%s: null` — the generator could not consult git, "
                  "so the provenance of its hashes is UNKNOWN, which is not the same as clean"
                  % _CLEAN_FLAG)
    else:
        detail = ("the manifest on disk records `%s: %s`" % (_CLEAN_FLAG, json.dumps(flag)))
    return (
        "REFUSED: %s.\n"
        "  Its hash list was taken while tracked files were uncommitted, so a hash in it may\n"
        "  describe content that is in NO COMMIT. A reader who checks out the `git_revision` this\n"
        "  manifest names and verifies gets a mismatch on a file nobody can produce. That is not a\n"
        "  staleness — the inventory may well be current — it is a provenance failure, and it is\n"
        "  why this is refused rather than reported as STALE.\n"
        "  ⭐ THE FIX IS AN ORDERING, NOT A REGENERATION, AND REGENERATING NOW MAKES IT WORSE.\n"
        "  Running `python3 research/manuscripts/aso_archive_manifest.py` against the tree you have\n"
        "  right now re-hashes the same uncommitted edits and writes `false` again — that is the\n"
        "  obvious response to a STALE line and it is what produced the bad artifact on `main`.\n"
        "  Instead: commit (or stash) every other change FIRST, then regenerate the manifest\n"
        "  against the clean tree as the session's LAST commit. Same generator, same inputs; only\n"
        "  the ordering differs, and the ordering is the whole content of this field."
        % detail
    )


def _archive_only(art):
    """The manifest with the two repository-state fields dropped.

    ⛔ THIS EXISTS BECAUSE `--check` WAS WIRED INTO PREFLIGHT AND CRIED WOLF ON THE FIRST COMMIT
    AFTER IT (2026-08-17). The header above this function's caller had already predicted it in
    words — "`--check` goes red after any commit and must NOT be wired into preflight as a gate: it
    would cry wolf on every push and be switched off, which is how a real staleness would then be
    missed" — and a session added it to preflight's generated-artifact gate anyway, then watched
    PREFLIGHT_FULL fail on a manifest that had been regenerated and committed minutes earlier.
    ⚠ THE PREDICTED CONSEQUENCE WAS THE DANGEROUS ONE, NOT THE FAILURE. A gate that is red for a
    reason nobody can act on gets relaxed, and the next relaxation would have been to drop the
    manifest from the gate entirely — leaving a real hash-list staleness unwatched.
    ⭐ So the two questions are separated instead of one being dropped:
      * `--check-archive` asks "does the FILE LIST still describe the tree?" — stable across
        commits, safe in preflight, and it is the question that catches a real staleness.
      * `--check` keeps asking the strict question, including the revision, and stays the
        PRE-DEPOSIT check a human runs at the moment the hashes have to be true.
    """
    return {k: v for k, v in art.items() if k not in _REPO_STATE_FIELDS}


def main(argv):
    # ⛔ `--check-revision-published` READS THE FILE ON DISK AND NEVER BUILDS. It answers one
    # question — will the revision this artifact already records survive the push? — so re-deriving
    # 483 hashes to answer it would be both slow and wrong: the durability of the RECORDED sha is a
    # fact about the committed artifact, not about the tree right now.
    # ⭐ IT IS SEPARATE FROM `--check` AND `--check-archive` ON PURPOSE. `--check-archive` is the
    # preflight gate and deliberately drops the repository-state fields (see `_archive_only`);
    # folding a revision check into it would reintroduce the 2026-08-17 cry-wolf failure that
    # separation exists to prevent. This is the PUSH-TIME question and belongs on the push path.
    # ⛔⛔ "IS THIS PATH IN THE ARCHIVE?" — THE QUERY 33 WORKFLOWS NEED AND NONE COULD ASK
    # (AUT-PD-168). A workflow that commits a tracked file has no cheap way to know whether that
    # file is one of the 483 the deposit manifest hashes, so it pushes, the manifest goes stale
    # invisibly, and the trunk goes red on the NEXT commit — which is always somebody else's.
    # Measured 2026-08-29: aa6d9d9a9 rewrote `research/modalities/emc-expression-panels.json`, an
    # inventoried file, and the two commits after it went red on both jobs having touched nothing
    # archived.
    # ⭐ THE AUDIT THAT ROW ASKED FOR SAYS THE ANSWER IS NOT "ADD A STEP TO EACH WORKFLOW": 33 of 34
    # can write an inventoried file and adding the regeneration to each is 31 more chances to
    # forget. The answer is ONE shared publish step that owns it — and a shared step needs exactly
    # this predicate, which is why it lives here, at the module that defines the inventory, rather
    # than as a list somebody maintains next to the publisher.
    # ⚠ IT READS THE MANIFEST ON DISK AND DOES NOT BUILD. The inventory is resolved by glob from the
    # promises, so rebuilding it to answer a membership question would take ~483 hashes to learn
    # something the committed artifact already states — and would answer about the tree as it is
    # mid-publish rather than as it was committed.
    if "--is-inventoried" in argv:
        paths = [a for a in argv[argv.index("--is-inventoried") + 1:] if not a.startswith("--")]
        if not paths:
            print("--is-inventoried needs at least one repository-relative path", file=sys.stderr)
            return 2
        if not os.path.exists(OUT):
            # ⛔ FAIL LOUD, NOT QUIET. "I could not read the inventory" must not answer "no" — a
            # caller wiring this into a publish step would then skip the regeneration exactly when
            # the manifest is most broken.
            print("no manifest on disk, so archive membership is UNKNOWN", file=sys.stderr)
            return 2
        try:
            inventory = {f["path"] for f in json.load(open(OUT, encoding="utf-8"))["files"]}
        except (ValueError, KeyError, TypeError):
            print("the manifest on disk carries no readable file list, so archive membership is "
                  "UNKNOWN", file=sys.stderr)
            return 2
        hits = [p for p in (os.path.normpath(x) for x in paths) if p in inventory]
        for h in hits:
            print(h)
        return 0 if hits else 1
    if "--check-revision-published" in argv:
        if not os.path.exists(OUT):
            print("no manifest on disk, so it records no revision at all", file=sys.stderr)
            return 1
        try:
            rev = json.load(open(OUT, encoding="utf-8")).get("git_revision")
        except ValueError:
            print("the manifest on disk is not readable JSON", file=sys.stderr)
            return 1
        if not (isinstance(rev, str) and len(rev) == 40):
            print("the manifest records no usable git_revision: %r" % (rev,), file=sys.stderr)
            return 1
        report = _revision_durability_report(rev)
        if report is None:
            print("git_revision %s is on a remote-tracking ref; a rebase cannot rewrite it"
                  % rev[:12])
            return 0
        print(report, file=sys.stderr)
        # ⚠ UNCHECKED IS NOT A FAILURE AND IS NOT A PASS — it exits 0 with the weakening ANNOUNCED,
        # the same choice `test_the_manifest_revision_is_a_commit_a_reader_can_resolve` makes for a
        # shallow clone. A check that cannot look must say so; making it red would get it switched
        # off in exactly the clones (fresh, remote-less, CI) where it can never answer.
        return 0 if report.startswith("⚠") else 1
    checking = "--check" in argv or "--check-archive" in argv
    old_text = None
    if checking:
        # ⛔ PROVENANCE IS CHECKED BEFORE CONTENT, IT GATES BOTH MODES, AND IT RUNS BEFORE `build()`
        # (AUT-PD-016). A manifest generated against a dirty tree is untrustworthy by construction
        # whether or not its inventory still matches, so this cannot live inside the
        # `--check-archive` branch and cannot become a field of the diff — `_archive_only` must keep
        # dropping it, or the 2026-08-17 cry-wolf failure returns.
        # ⭐ AND IT PRECEDES THE BUILD FOR TWO REASONS, ONE OF WHICH IS THE DEFECT ITSELF. The
        # question "was this file made against a clean tree?" is answered entirely by the bytes on
        # disk; re-deriving 483 hashes first answers nothing it needs. More to the point, the tree
        # that produces a `false` flag is a tree mid-write — exactly the state in which `build()` is
        # least likely to survive — and a provenance refusal that only prints after a successful
        # build is a refusal that the failure it describes can suppress.
        old_text = open(OUT, "r", encoding="utf-8").read() if os.path.exists(OUT) else None
        if old_text is None:
            print("STALE: no manifest on disk", file=sys.stderr)
            return 1
        refusal = _dirty_tree_refusal(old_text)
        if refusal is not None:
            print(refusal, file=sys.stderr)
            return 1
    art = build()
    text = json.dumps(art, indent=2, ensure_ascii=False) + "\n"
    if checking:
        if "--check-archive" in argv:
            try:
                old = json.loads(old_text)
            except ValueError:
                print("STALE: manifest on disk is not readable JSON", file=sys.stderr)
                return 1
            if _archive_only(old) != _archive_only(art):
                print("STALE: the archive inventory would change — re-run without --check",
                      file=sys.stderr)
                return 1
            print("manifest inventory is current (repository-state fields not compared)")
            return 0
        if old_text != text:
            print("STALE: manifest would change — re-run without --check", file=sys.stderr)
            return 1
        print("manifest is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    # ⛔ A COVERAGE CHECK THAT COULD NOT RUN EXITS NON-ZERO. The manifest is still written — a
    # partial manifest is useful — but "I could not look" must never be reported as "nothing found".
    unchecked = not art["gaps"]["screen_coverage"].get("ok", False)
    drifted = art["gaps"].get("promises_whose_sentence_is_no_longer_in_the_manuscript") or []
    unmapped = art["gaps"]["promises_resolving_to_no_file"]
    print(f"wrote {os.path.relpath(OUT, REPO)}: {art['n_files']} files, "
          f"{art['total_mib']} MiB", file=sys.stderr)
    # ⛔ SAY IT AT THE MOMENT THE MISTAKE IS MADE (AUT-PD-141, -175, -195). The revision just
    # stamped is the one a later rebase orphans, and the bit that decides it is available NOW —
    # afterwards the only witness is CI, a commit later, on somebody else's push.
    # ⚠ IT WARNS AND DOES NOT REFUSE, AND THE ENFORCEMENT IS `--check-revision-published` ON THE
    # PUSH PATH. Refusing here would break the legitimate case where a session regenerates on a
    # branch it is about to push for the first time. Measured 2026-09-01: three workflows invoke this
    # module by name (`aso-submission-parts.yml`, `emc-expression-datasets.yml`, and `tests.yml`
    # which only checks it) and every interactive session runs it through
    # `scripts/regenerate_aso_chain.sh`. A generator that starts exiting non-zero on a normal flow
    # gets its exit code ignored, which is how a real refusal stops being read. ⛔ A warning is NOT the fix — CLAUDE.md's "recorded is not enforced"
    # — it is the early signal beside it.
    _rev = art.get("git_revision")
    if isinstance(_rev, str) and len(_rev) == 40:
        _durability = _revision_durability_report(_rev)
        if _durability:
            print(_durability, file=sys.stderr)
    if unmapped:
        print(f"⛔ UNMAPPED PROMISES: {unmapped}", file=sys.stderr)
    if drifted:
        # ⛔ NON-ZERO EXIT, because a promise the paper no longer makes is what got PUBLISHED once.
        print(f"⛔ PROMISES WHOSE SENTENCE HAS LEFT THE MANUSCRIPT: {drifted}\n"
              "   Either the row's `promise` is stale prose to correct, or the paper dropped a "
              "commitment the archive still keeps. Both are decisions; neither is a regeneration.",
              file=sys.stderr)
    if unchecked:
        print("⛔ screen-coverage classifier did not run — gaps are UNKNOWN", file=sys.stderr)
    return 1 if (unmapped or unchecked or drifted) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
