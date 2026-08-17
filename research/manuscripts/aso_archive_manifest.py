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
        "contributes": ("The two manuscript tables and the generator that derives every cell of "
                        "them from the artifacts, plus the per-locus re-count and the chance "
                        "baseline the tables and Figure 3 are read from."),
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-submission-tables.md",
                     "research/manuscripts/submission_tables.py",
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
                     "research/manuscripts/aso/lit-targets-aso-verify.json",
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
                     "research/manuscripts/aso/fusion-junction-aso-paper-redteam.md"],
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
        "patterns": ["research/modalities/junction-aso-offtarget-*-deep500.json",
                     "research/modalities/aso-insilico-evaluation-*-deep500.json",
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
        "id": "reproduction_guards",
        "promise": ("Every quantitative statement here is produced by code in the released "
                    "archive and is reproducible from it"),
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
            "_promise_still_in_manuscript": (
                _promise_text_found_in_paper(paper, row["promise"])
                if row.get("verbatim", True) else "n/a — descriptive label, not a quotation"),
            "⛔_UNMAPPED": not resolved,
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
        "total_bytes": total,
        "total_mib": round(total / (1024 * 1024), 3),
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
            "Register the DOI in research/manuscripts/pinned-figures.json so the consistency "
            "linter holds the two copies together.",
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


def main(argv):
    art = build()
    text = json.dumps(art, indent=2, ensure_ascii=False) + "\n"
    if "--check" in argv:
        old = open(OUT, "r", encoding="utf-8").read() if os.path.exists(OUT) else None
        if old != text:
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
