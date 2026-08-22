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
                     "research/manuscripts/lint_style.py"],
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
                        "FLAG IS ON 252 OF THE 780 RECORDS, NOT ON THREE: 249 pair a wild-type "
                        "parent through the whole catalytic gap at the ten-base-pair criterion, "
                        "and 3 more pair the patient's own un-rearranged NR4A3 allele. This "
                        "sentence named only the second class until 2026-08-19, which described "
                        "the smaller hazard and left the larger one sounding like a clean file. "
                        "The generator "
                        "refuses to build if any sequence the documents print is absent, so the "
                        "file cannot quietly stop being canonical."),
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-sequences.csv",
                     "research/manuscripts/aso/fusion-junction-aso-sequences.fasta",
                     "research/manuscripts/aso_sequence_manifest.py",
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
                     "research/modalities/tests/test_junction_seam_retraction.py"],
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
        # ⚠ NO STAMP EXISTS FOR THE SUPPORTING-INFORMATION PDF, and the glob will pick one up the
        # day the builder writes one. That gap is reported in `gaps` rather than papered over here.
        "promise": "Two renderings of this manuscript travel with it and their text is the same",
        "contributes": ("The built documents a depositor uploads: the version of record in "
                        "submission format, the typeset preview of the same text, the Supporting "
                        "Information rendered from the same builder, and the build stamps that "
                        "record the SHA-256 of every source each PDF was rendered from."),
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-research-article*.pdf",
                     "research/manuscripts/aso/fusion-junction-aso-research-article*"
                     ".build-stamp.json"],
    },
    {
        "id": "manuscript_and_figures",
        # ⚠ NOT A PROMISE THE PAPER MAKES — a deposit that omitted the paper and its figures would
        # be useless, so this row exists for the depositor rather than for the availability
        # statement. Kept in the same table so there is one list, not two.
        "verbatim": False,
        "promise": "the manuscript itself and the figures it prints",
        "contributes": ("The submission text, its Supporting Information, its cover letter, and "
                        "the figure generators with their vector and raster output. The figures "
                        "are generated from the same artifacts as the tables, so a reader can "
                        "regenerate them."),
        # ⛔ THE SUPPORTING INFORMATION WAS ABSENT FROM THIS ROW UNTIL 2026-08-16, AND A DEPOSIT
        # MISSING IT IS THE WORST KIND OF HOLE: the main text points into it ("SI §S1") from six
        # places, so a reader following a cross-reference finds nothing and cannot tell whether the
        # method was withdrawn or never written. The row's globs are literal paths, so the split
        # that CREATED the SI could not add it — which is this table's own hand-list warning,
        # firing on the one row whose patterns cannot glob.
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-research-article.md",
                     "research/manuscripts/aso/fusion-junction-aso-supplementary-information.md",
                     "research/manuscripts/aso/fusion-junction-aso-cover-letter.md",
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
                     "research/manuscripts/aso_archive_manifest.py"],
    },
]

# The manifest never lists itself: its own hash would depend on its own content, and the file could
# then never be idempotent. It is named here so a reader can see the omission is a decision.
SELF_EXCLUDE = {os.path.relpath(OUT, REPO)}

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
            rel = os.path.relpath(p, REPO)
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
            graded = os.path.relpath(s.path[:-5] + "-graded.json", REPO)
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
    gaps = {
        "_what": ("Every question a reviewer would put to the availability statement, answered "
                  "from the artifacts rather than from a note. An empty list here is a reading, "
                  "not a reassurance."),
        "promises_resolving_to_no_file": unmapped,
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
            os.path.relpath(p, REPO)
            for p in glob.glob(os.path.join(ASO, "*.pdf"))
            if not os.path.exists(p[:-4] + ".build-stamp.json")
            and os.path.relpath(p, REPO) in seen),
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
            "a human uses to make the deposit and mint the DOI that fills the manuscript's two "
            "remaining placeholders."),
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
            "Not a deposit. Nothing here has been uploaded, registered or reserved, and this "
            "module makes no network call of any kind.",
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
        "deposition_doi": "10.5281/zenodo.22028916",
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
            "path": os.path.relpath(OUT, REPO),
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
            "6. Paste the reserved DOI into the manuscript's two '[ARCHIVE DOI]' placeholders — "
            "one in Methods -> Availability, one in Declarations -> Data and code availability. "
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
#: session has edits in progress. Neither says anything about whether the hash list is right.
_REPO_STATE_FIELDS = ("git_revision", "git_tree_is_clean_apart_from_this_manifest")


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
    art = build()
    text = json.dumps(art, indent=2, ensure_ascii=False) + "\n"
    if "--check" in argv or "--check-archive" in argv:
        old_text = open(OUT, "r", encoding="utf-8").read() if os.path.exists(OUT) else None
        if old_text is None:
            print("STALE: no manifest on disk", file=sys.stderr)
            return 1
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
    unmapped = art["gaps"]["promises_resolving_to_no_file"]
    print(f"wrote {os.path.relpath(OUT, REPO)}: {art['n_files']} files, "
          f"{art['total_mib']} MiB", file=sys.stderr)
    if unmapped:
        print(f"⛔ UNMAPPED PROMISES: {unmapped}", file=sys.stderr)
    if unchecked:
        print("⛔ screen-coverage classifier did not run — gaps are UNKNOWN", file=sys.stderr)
    return 1 if (unmapped or unchecked) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
