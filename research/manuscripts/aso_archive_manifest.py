#!/usr/bin/env python3
"""Derive the deposit manifest for the fusion-junction ASO short communication. ($0, offline.)

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
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))          # research/
REPO = os.path.abspath(os.path.join(ROOT, ".."))          # repository root
MOD = os.path.join(ROOT, "modalities")
LIT = os.path.join(ROOT, "literature")
ASO = os.path.join(HERE, "aso")
OUT = os.path.join(ASO, "fusion-junction-aso-archive-manifest.json")

PAPER = os.path.join(ASO, "fusion-junction-aso-short-communication.md")

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
        "patterns": ["research/modalities/nr4a3-fusion-junction-atlas.json",
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
        "contributes": ("The submission text, its cover letter, and the figure generators with "
                        "their vector and raster output. The figures are generated from the same "
                        "artifacts as the tables, so a reader can regenerate them."),
        "patterns": ["research/manuscripts/aso/fusion-junction-aso-short-communication.md",
                     "research/manuscripts/aso/fusion-junction-aso-short-communication-cover-letter.md",
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


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve(patterns):
    """Globs -> sorted repo-relative paths, de-duplicated.

    ⚠ `-graded.json` is stripped from every row except the graded row. The screen glob
    `junction-aso-offtarget-*n3.json` matches the re-scores too, and a re-score counted as a screen
    would inflate the screen coverage check below into saying every junction has both arms.
    """
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

    screens, gap_resolved, ungraded, unfiltered = [], [], [], []
    for p in sorted(glob.glob(os.path.join(MOD, "junction-aso-offtarget-*.json"))):
        base = os.path.basename(p)
        if base.endswith("-graded.json") or "locus-collapse" in base:
            continue
        with open(p, "r", encoding="utf-8") as fh:
            screen = json.load(fh)
        screens.append(base)
        if screen_orientation_status(screen) != ORIENTATION_FILTERED:
            unfiltered.append(base)
        ok, _why = screen_is_gap_resolved(screen)
        if ok:
            gap_resolved.append(base)
            if not os.path.exists(p[:-5] + "-graded.json"):
                ungraded.append(base)

    def _tags(pattern, prefix):
        out = set()
        for p in glob.glob(os.path.join(MOD, pattern)):
            b = os.path.basename(p)
            if b.endswith("-graded.json"):
                continue
            out.add(b[len(prefix):-len(".json")])
        return out

    blast = _tags("junction-aso-offtarget-*.json", "junction-aso-offtarget-")
    blast.discard("locus-collapse")
    exhaustive = _tags("aso-insilico-evaluation-*.json", "aso-insilico-evaluation-")
    designs = _tags("junction-aso-designs-*.json", "junction-aso-designs-")

    res.update({
        "n_screens_committed": len(screens),
        "n_screens_gap_resolved": len(gap_resolved),
        "n_screens_coverage_only_cannot_be_graded": len(screens) - len(gap_resolved),
        "n_screens_not_orientation_filtered_counts_are_upper_bounds": len(unfiltered),
        "screens_not_orientation_filtered": sorted(unfiltered),
        "gap_resolved_screens_with_no_committed_graded_rescore": sorted(ungraded),
        "junctions_with_a_design_panel_but_no_screen": sorted(designs - blast),
        "junctions_screened_by_blast_arm_only": sorted(blast - exhaustive - {"bp200-8-gapres"}),
        "junctions_screened_by_exhaustive_arm_only": sorted(exhaustive - blast),
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
            "The Europe PMC prior-art corpora behind the '5,153 unique records' first-in-kind "
            "statement are published to the `literature-cache` branch, not to this branch. The "
            "audited summary travels in the archive (aso-citations-priorart-2026-08-08.md); the "
            "row-level corpora do not, and must be exported from that branch if the deposit is to "
            "carry them.",
            "⛔ MEASURED 2026-08-13, NOT YET CLOSED: the Availability paragraph names five "
            "recomputations that run offline — the tables, the junction atlas, the locus collapse, "
            "the chance baseline and the graded re-scores. Four were verified by execution with "
            "the network hard-blocked and reproduced their committed artefacts byte-identically. "
            "The FIFTH does not run at all: `offtarget_chance_baseline.py` raises "
            "`ValueError: expected one shared value, got [2, 3]` at line 276, where "
            "`multi_junction_span` is built with `_uniform()` over each multi-junction oligo's "
            "`n_junctions`. The committed artefact records `multi_junction_span: 3` from a panel "
            "set in which every multi-junction oligo spanned exactly three seams; the current panel "
            "set contains both two- and three-seam oligos, and `_uniform` refuses by design rather "
            "than silently picking one. The module already carries `_span()` ('[min, max] ... for "
            "captions that quote a range') for exactly this shape. This is a re-derivation failure, "
            "NOT a network failure, and it does not affect any reported number — the tables read "
            "the committed baseline — but it does make the enumerated offline claim false for one "
            "of its five items until either the module is fixed or the sentence is narrowed.",
            "The BLAST arm of the specificity screen calls NCBI over the network when SCREENING. "
            "Nothing in the manuscript re-runs it: every reported count is read from the committed "
            "screen artifacts, and the graded re-score is explicitly offline "
            "(`junction_aso_offtarget.grade_panel`: 'NO NETWORK, NO RE-BLAST'). Re-deriving the "
            "paper from the archive is offline; re-generating the screens from scratch is not.",
        ],
    }

    return {
        "_what_this_is": (
            "The deposit manifest for 'Fusion-junction antisense oligonucleotides in extraskeletal "
            "myxoid chondrosarcoma' (short communication). It names every file the manuscript's "
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
