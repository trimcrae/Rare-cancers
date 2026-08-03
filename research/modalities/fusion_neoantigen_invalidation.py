#!/usr/bin/env python3
"""Grade the committed EWSR1::NR4A3 neoantigen artifacts against the CORRECTED junction, and banner them. ($0)

★★ WHY THIS EXISTS.
`fusion_breakpoints.py` addressed NR4A3's exon window by CODING-exon index while labelling it with TRANSCRIPT
exon numbers. NR4A3's canonical transcript `ENST00000395097` has **8 transcript exons of which the first two
carry no coding sequence**, so the two numberings differ by two and every junction the module emitted resumed
NR4A3 two coding exons late. The helpers were fixed at source on 2026-08-02 (`resume_offset` / `cut_offset`,
which now REFUSE a non-coding exon instead of sliding onto its neighbour) and the corrected junction was
reproduced independently from live Ensembl exon structure by rung `R13-a`
(`fusion-object-inventory.json` -> `gate.status == "REPRODUCED"`, junction `EWSR1(1-264)::NR4A3(1-626)`).

⛔ **THE COMMITTED ARTIFACTS PREDATE THE FIX AND WERE NEVER REGENERATED.** Regenerating them needs MHCflurry,
which is that lane's call and is not this module's to make. So this module does the one thing that IS free and
IS owed: it establishes exactly how many predictions are affected, and makes the artifacts SAY SO. A wrong
artifact with a banner is honest; a wrong artifact without one is a landmine.

⛔ NOTHING HERE PREDICTS, RE-PREDICTS, EDITS OR INVENTS A PEPTIDE, A BINDER OR AN AFFINITY. Every peptide and
every number in the banner is COUNTED from what is already committed. The classification is computed by
running the FIXED helpers over the committed exon map (`nr4a3-exon-audit.json`), never from memory and never
from a remembered figure.

WHAT "AFFECTED" MEANS, PRECISELY — and it is not one bucket
----------------------------------------------------------
A committed junction is graded on its NR4A3 CDS resume OFFSET, not on its label, because the label is the
thing that was wrong:
  · `SEAM_NOT_PRODUCED`   — no entry in the declared NR4A3 window produces this offset under the fixed
                            helpers. The seam does not exist. Every peptide crossing it is a sequence no
                            corrected breakpoint yields.
  · `SEAM_RELABELLED`     — the fixed helpers DO produce this offset, but from a different transcript exon
                            than the artifact's label. The peptides are real sequences of that other
                            junction; the label on them is wrong, and R13-a's DBD filter excludes that
                            junction anyway (it deletes AF1 and the whole C4 zinc-finger DBD, which opens at
                            NR4A3 C292 — incompatible with the fusion transactivating the PPARG response
                            element it is reported to act through, Filion 2009 / PMC4429309).
Collapsing the two would be the same class of error as the off-by-two itself, so they are counted separately
and both are reported.
"""
from __future__ import annotations

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

#: The artifact this module grades and banners.
BREAKPOINT_ARTIFACT = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
#: The OTHER committed neoantigen artifact, from `fusion_neoantigen.py`'s single modelled breakpoint.
SINGLE_BREAKPOINT_ARTIFACT = os.path.join(HERE, "fusion-neoantigen-predictions.json")
#: The committed exon map, which is where the corrected numbering has its one home.
EXON_AUDIT = os.path.join(HERE, "nr4a3-exon-audit.json")
#: R13-a's inventory, which owns the corrected junction string and the DBD filter.
INVENTORY = os.path.join(HERE, "fusion-object-inventory.json")
#: Committed UniProt sequences, used only to CHECK a seam, never to build one.
SEQ_CACHE = os.path.join(HERE, "nr4a-sequences-cache.json")

BANNER_KEY = "⛔_RETRACTED_SEAMS"


def _model(audit, symbol):
    """A `fusion_breakpoints`-shaped gene model built from the COMMITTED exon audit — no network."""
    g = audit[symbol]
    return {"symbol": symbol,
            "coding_ranks": [e["transcript_exon_rank"] for e in g["exons"] if e["is_coding"]],
            "offsets": g["coding_offsets"]}


def corrected_windows(audit=None):
    """`(nr4a3_resumes, ewsr1_cuts, skipped)` under the FIXED helpers over the DECLARED windows.

    ⛔ The helpers are IMPORTED, not reimplemented: this has to fail if the fix is ever reverted, and a
    private copy of the arithmetic could not.
    """
    import fusion_breakpoints as FB
    audit = audit or json.load(open(EXON_AUDIT, encoding="utf-8"))
    nr4, ews = _model(audit, "NR4A3"), _model(audit, "EWSR1")
    resumes, skipped = {}, []
    for n in FB.NR4A3_EXON_WINDOW:
        try:
            resumes[n] = FB.resume_offset(nr4, n)
        except ValueError as exc:
            skipped.append({"transcript_exon": n, "why": str(exc)})
    cuts = {}
    for e in FB.EWSR1_EXON_WINDOW:
        try:
            cuts[e] = FB.cut_offset(ews, e)
        except ValueError as exc:                                # pragma: no cover - EWSR1 is fully coding
            skipped.append({"transcript_exon": e, "why": str(exc)})
    return resumes, cuts, skipped


def residue_of(cds_nt_offset):
    """The 1-based protein residue a CDS nt OFFSET resumes at — `fusion_breakpoints`' own `q // 3 + 1`."""
    return cds_nt_offset // 3 + 1


def classify(artifact=None, audit=None):
    """The complete count. Pure over committed inputs; returns the banner body."""
    art = artifact or json.load(open(BREAKPOINT_ARTIFACT, encoding="utf-8"))
    resumes, cuts, skipped = corrected_windows(audit)
    produced = set(resumes.values())

    rows, dead_keys, relabelled_keys = [], set(), set()
    for j in art["junctions"]:
        q, p = j["nr4_cds_nt"], j["ews_cds_nt"]
        key = (j["EWSR1_exon_end"], j["NR4A3_exon_start"], q)
        label_exon = j["NR4A3_exon_start"]
        produced_by = sorted(n for n, off in resumes.items() if off == q)
        status = "SEAM_RELABELLED" if produced_by else "SEAM_NOT_PRODUCED"
        (relabelled_keys if produced_by else dead_keys).add(key)
        rows.append({
            "committed_label": "EWSR1 exon %s :: NR4A3 exon %s" % (j["EWSR1_exon_end"], label_exon),
            "ews_cds_nt": p,
            "nr4_cds_nt": q,
            "nr4a3_resumes_at_residue": residue_of(q),
            "junction_context": j["junction_context"],
            "status": status,
            "ewsr1_cut_reproduced": cuts.get(j["EWSR1_exon_end"]) == p,
            "nr4a3_label_reproduced": resumes.get(label_exon) == q,
            "corrected_transcript_exon_that_produces_this_offset": produced_by or None,
            "n_novel_peptides": j["n_novel_peptides"],
            "n_binders": j["n_binders"],
        })

    pep_at, bind_at = {}, {}
    for j in art["junctions"]:
        key = (j["EWSR1_exon_end"], j["NR4A3_exon_start"], j["nr4_cds_nt"])
        for pep in j["novel_peptides"]:
            pep_at.setdefault(pep, set()).add(key)
        for b in j["binders"]:
            bind_at.setdefault(b["peptide"], set()).add(key)

    ranked = [b["peptide"] for b in art.get("predicted_binders_ranked") or []]
    counts = {
        "n_junctions_committed": len(art["junctions"]),
        "n_junctions_seam_not_produced": sum(1 for r in rows if r["status"] == "SEAM_NOT_PRODUCED"),
        "n_junctions_seam_relabelled": sum(1 for r in rows if r["status"] == "SEAM_RELABELLED"),
        "n_junctions_with_a_reproduced_nr4a3_label": sum(1 for r in rows if r["nr4a3_label_reproduced"]),
        "n_junctions_with_a_reproduced_ewsr1_cut": sum(1 for r in rows if r["ewsr1_cut_reproduced"]),
        "n_distinct_novel_peptides": len(pep_at),
        "n_distinct_novel_peptides_only_at_seams_not_produced":
            sum(1 for s in pep_at.values() if s <= dead_keys),
        "n_distinct_novel_peptides_at_a_relabelled_seam":
            sum(1 for s in pep_at.values() if s & relabelled_keys),
        "n_junction_level_peptide_rows": sum(j["n_novel_peptides"] for j in art["junctions"]),
        "n_distinct_predicted_binders": len(ranked),
        "n_distinct_predicted_binders_only_at_seams_not_produced":
            sum(1 for s in bind_at.values() if s <= dead_keys),
        "n_distinct_predicted_binders_at_a_relabelled_seam":
            sum(1 for s in bind_at.values() if s & relabelled_keys),
        "n_junction_level_binder_rows": sum(j["n_binders"] for j in art["junctions"]),
    }
    # ⛔ The two artifact-level totals must agree with what the rows actually contain, or the count is not a
    # count. `n_distinct_binders` is the artifact's own field and is checked, never trusted.
    counts["_selfcheck_ranked_equals_junction_level_binders"] = set(ranked) == set(bind_at)
    counts["_selfcheck_artifact_n_distinct_binders"] = art.get("n_distinct_binders") == len(ranked)
    counts["binders_at_a_relabelled_seam"] = sorted(p for p, s in bind_at.items() if s & relabelled_keys)

    return {"rows": rows, "counts": counts,
            "corrected_nr4a3_resumes": {str(n): {"cds_nt": off, "residue": residue_of(off)}
                                        for n, off in sorted(resumes.items())},
            "corrected_nr4a3_window_entries_skipped_as_non_coding": skipped}


# ---------------------------------------------------------------------------------------------------------
# Who still quotes them
# ---------------------------------------------------------------------------------------------------------

#: Directories scanned for citations. Worktrees and VCS internals are excluded — a stale checkout is not a
#: citation, and counting one would inflate the blast radius.
_SCAN_ROOTS = ("research",)
_SCAN_EXTS = (".md", ".json", ".py", ".txt", ".html")
_EXCLUDE = ("/mainwt2/", "/.git/", "/.claude/", "/__pycache__/", "/node_modules/",
            "/fusion_neoantigen_invalidation.py", "/fusion-neoantigen-retraction.json")


def peptides_of(art):
    """Every peptide string the artifact asserts, junction-level and ranked."""
    peps = {p for j in art.get("junctions") or [] for p in j.get("novel_peptides") or []}
    peps |= {b["peptide"] for j in art.get("junctions") or [] for b in j.get("binders") or []}
    peps |= {b["peptide"] for b in art.get("predicted_binders_ranked") or []}
    peps |= set(art.get("novel_peptides") or [])
    for k in ("binders", "top_predictions"):
        peps |= {r["peptide"] for r in (art.get(k) or []) if isinstance(r, dict) and "peptide" in r}
    return {p for p in peps if p}


def consumers(artifact_basename, self_paths=()):
    """`[{path, kind}]` — every committed file that READS or NAMES the artifact by filename.

    ⛔ A DIFFERENT AND MORE SERIOUS CLASS THAN A QUOTED PEPTIDE. A prose file quoting a peptide is one wrong
    sentence; a module that LOADS this artifact recomputes its own numbers from it, so its outputs inherit
    the defect whether or not they ever print a peptide. `hla_coverage.py` and `vaccine_construct.py` are
    both in this class, and neither would have appeared in a peptide-string scan of their outputs alone.
    """
    selves = {os.path.abspath(p) for p in self_paths}
    out = []
    for root in _SCAN_ROOTS:
        for path in sorted(glob.glob(os.path.join(REPO, root, "**", "*"), recursive=True)):
            if not os.path.isfile(path) or os.path.splitext(path)[1] not in _SCAN_EXTS:
                continue
            if any(x in path.replace(os.sep, "/") for x in _EXCLUDE) or os.path.abspath(path) in selves:
                continue
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:                                       # pragma: no cover
                continue
            if artifact_basename not in text:
                continue
            out.append({"path": os.path.relpath(path, REPO),
                        "kind": _reference_kind(path, text, artifact_basename)})
    return sorted(out, key=lambda r: (r["kind"], r["path"]))


#: Names a Python binding that a later `open(...)`/`json.load(...)` uses. Kept deliberately narrow — a broad
#: "the file mentions `open(` somewhere" test put SIX modules in the CODE class that only NAME the artifact
#: in a comment, which would have overstated the blast radius. Overstating it is not the safe direction:
#: it is what makes a list nobody trusts, and an untrusted list is not acted on.
_BINDING = ("=", ":")


def _reference_kind(path, text, basename):
    """How `path` refers to the artifact — WRITES / LOADS / names it. Conservative by construction."""
    if not path.endswith(".py"):
        return "names the artifact (prose or data)"
    lines = text.split("\n")
    hit_lines = [l for l in lines if basename in l]
    # bound to a module constant, then that constant is opened/loaded elsewhere
    consts = set()
    for l in hit_lines:
        head = l.split("=")[0].strip()
        if "=" in l and head.isidentifier():
            consts.add(head)
    _READS = ("open(", "json.load", "_load(", "read_text(", "loads(")
    opens_const = any(c in l and any(r in l for r in _READS) for c in consts for l in lines)
    writes = any(('"w"' in l or "'w'" in l) and any(c in l for c in consts) for l in lines) or \
        any(c in ("OUT", "OUTPUT", "DEST") for c in consts)
    # ⚠ ALSO the literal-argument shape — `_load("fusion-breakpoint-neoantigens.json")`. Missing it left
    # `fusion_object_inventory.py`, which is the module that FLAGGED this defect, off its own consumer list.
    direct = any(any(r in l for r in _READS) for l in hit_lines)
    if writes:
        return "CODE — WRITES this artifact (its producer)"
    if opens_const or direct:
        # ⛔ A GUARD IS NOT A CONSUMER. A test that opens the artifact to assert the banner is there does not
        # inherit the defect, and counting it would inflate the blast radius — which is the fastest way to
        # make this list untrusted, and an untrusted list is not acted on.
        if "/tests/" in path.replace(os.sep, "/") or os.path.basename(path).startswith("test_"):
            return "TEST — loads it as a guard (does not inherit the defect)"
        return "CODE — LOADS this artifact and recomputes from it"
    return "code comment / docstring reference only"


def citations(peps, self_paths=()):
    """`[{path, n_peptides_quoted, examples}]` — every committed file quoting one of `peps`.

    ⛔ EXACT SUBSTRING, never fuzzy. A peptide is a literal string; a near-match is not a citation, and
    pretending it is would put files on this list that do not belong there.
    """
    selves = {os.path.abspath(p) for p in self_paths}
    out = []
    for root in _SCAN_ROOTS:
        for path in sorted(glob.glob(os.path.join(REPO, root, "**", "*"), recursive=True)):
            if not os.path.isfile(path) or os.path.splitext(path)[1] not in _SCAN_EXTS:
                continue
            if any(x in path.replace(os.sep, "/") for x in _EXCLUDE) or os.path.abspath(path) in selves:
                continue
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:                                       # pragma: no cover
                continue
            hits = sorted(p for p in peps if p in text)
            if hits:
                out.append({"path": os.path.relpath(path, REPO),
                            "n_peptides_quoted": len(hits),
                            "examples": hits[:6]})
    return sorted(out, key=lambda r: (-r["n_peptides_quoted"], r["path"]))


# ---------------------------------------------------------------------------------------------------------
# The banners
# ---------------------------------------------------------------------------------------------------------


def _corrected_junction():
    """The corrected junction string, READ from the artifact that reproduced it (rule 1: one home)."""
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    gate = inv["gate"]
    if gate.get("status") != "REPRODUCED":
        raise SystemExit("REFUSED: %s's gate is %r, not REPRODUCED — nothing may be graded against it"
                         % (os.path.basename(INVENTORY), gate.get("status")))
    return gate["junction"], gate


def breakpoint_banner(stamp_utc, stamp_et):
    art = json.load(open(BREAKPOINT_ARTIFACT, encoding="utf-8"))
    art.pop(BANNER_KEY, None)                                     # idempotent: regrade, never stack banners
    junction, gate = _corrected_junction()
    graded = classify(art)
    c = graded["counts"]
    cits = citations(peptides_of(art), self_paths=(BREAKPOINT_ARTIFACT,))
    cons = consumers(os.path.basename(BREAKPOINT_ARTIFACT), self_paths=(BREAKPOINT_ARTIFACT,))
    banner = {
        "status": "RETRACTED — DO NOT QUOTE ANY PEPTIDE, BINDER OR AFFINITY IN THIS FILE",
        "one_line": ("all %d junctions carry an NR4A3 exon label the corrected exon map does not reproduce; "
                     "%d of them resume at an offset no corrected window entry produces at all, and %d of "
                     "the %d distinct predicted binders exist only at those non-existent seams."
                     % (c["n_junctions_committed"], c["n_junctions_seam_not_produced"],
                        c["n_distinct_predicted_binders_only_at_seams_not_produced"],
                        c["n_distinct_predicted_binders"])),
        "corrected_junction": junction,
        "corrected_junction_source": {
            "artifact": "fusion-object-inventory.json",
            "gate_status": gate.get("status"),
            "checks": gate.get("checks"),
            "_phase_caveat_has_one_home_there": gate.get("_phase_note"),
        },
        "the_defect": (
            "`fusion_breakpoints.py` indexed NR4A3's `offsets` array (CODING exons) with numbers from a "
            "window written in TRANSCRIPT exon numbers. NR4A3 ENST00000395097 has 8 transcript exons of "
            "which exons 1 and 2 carry no coding sequence, so the label \"NR4A3 exon 3\" addressed the "
            "THIRD CODING exon (transcript exon 5, residue 361) instead of transcript exon 3 (residue 1). "
            "Every junction in this file therefore deleted NR4A3's AF1 and the first zinc finger of the C4 "
            "DBD, which opens at C292."),
        "fixed_at_source": "fusion_breakpoints.resume_offset / cut_offset (2026-08-02) — they now RAISE on a "
                           "non-coding exon rather than sliding onto its neighbour",
        "⛔_not_regenerated": ("regenerating this artifact requires MHCflurry-2.0, which is the neoantigen "
                              "lane's call and not this module's. NOTHING here was re-predicted: every "
                              "number in this banner is COUNTED from the committed content below."),
        "counts": c,
        "junctions_graded": graded["rows"],
        "corrected_nr4a3_resumes_over_the_declared_window": graded["corrected_nr4a3_resumes"],
        "corrected_nr4a3_window_entries_skipped_as_non_coding":
            graded["corrected_nr4a3_window_entries_skipped_as_non_coding"],
        "⚠_how_this_reconciles_with_R13a": (
            "`fusion-object-inventory.json` -> `neoantigen_lane_flag` reports `all_seams_stale: true` and "
            "`stale_resume_residues: [318, 361, 419]`. That is CORRECT as written and this grading does not "
            "contradict it — the two use different reference sets ON PURPOSE. R13-a compares against the "
            "PLAUSIBLE corrected breakpoints, i.e. after its DBD filter, which leaves only NR4A3 residue 1; "
            "this module compares against every offset the corrected windows ARITHMETICALLY produce, which "
            "is residues 1 and 318. Residue 318 is therefore stale to R13-a (implausible) and produced to "
            "this module (arithmetic), and BOTH conclusions are the same: none of these binders may be "
            "quoted. Recording the split rather than collapsing it is what stops the next reader deciding "
            "the two artifacts disagree."),
        "⚠_the_one_relabelled_seam": (
            "one committed junction (EWSR1 exon 11 :: NR4A3 CDS nt 951, residue 318) resumes at an offset "
            "the corrected helpers DO produce — but from transcript exon 4, not the \"exon 2\" this file "
            "labels it. Its %d peptides and %d binders are real sequences of THAT junction under a wrong "
            "label, and that junction is itself excluded by R13-a's DBD filter (residue 318 deletes AF1 and "
            "the whole C4 zinc-finger DBD). It is counted separately above and is still not quotable here."
            % (c["n_distinct_novel_peptides_at_a_relabelled_seam"],
               c["n_distinct_predicted_binders_at_a_relabelled_seam"])),
        "downstream_citations": cits,
        "downstream_consumers": cons,
        "⛔_downstream_note": ("`downstream_citations` are files quoting peptide STRINGS from this artifact; "
                              "`downstream_consumers` are files that LOAD it and recompute — the more "
                              "serious class, because their numbers inherit the defect without ever "
                              "printing a peptide. A retracted input still quoted downstream is the more "
                              "serious half of the defect: each needs its own correction, and NONE of them "
                              "is fixed by this banner. ⚠ Two of the loaders — `nr4a3_exon_audit.py` and "
                              "`fusion_object_inventory.py` — read it in order to AUDIT it and are the "
                              "modules that diagnosed the defect; they are listed because they load it, not "
                              "because they inherit it. Test files that load it as a guard are classed "
                              "separately for the same reason."),
        "⛔_scope": ("exon arithmetic and sequence composition only. No affinity, presentation, "
                    "immunogenicity, efficacy, safety or clinical claim is made, repaired or implied here, "
                    "and none was ever established by this artifact."),
        "graded_utc": stamp_utc,
        "graded_et": stamp_et,
        "graded_by": "research/modalities/fusion_neoantigen_invalidation.py",
    }
    return banner, art


def single_breakpoint_banner(stamp_utc, stamp_et):
    """The OTHER artifact. A weaker, accurate label — it is not the off-by-two, and must not be called it."""
    art = json.load(open(SINGLE_BREAKPOINT_ARTIFACT, encoding="utf-8"))
    art.pop(BANNER_KEY, None)
    junction, _gate = _corrected_junction()
    seqs = json.load(open(SEQ_CACHE, encoding="utf-8"))
    nr4 = seqs["NR4A3"]
    model = art["_breakpoint_model"]
    right10 = model["junction_context_right10"]
    kept_from = 2 if right10 == nr4[1:11] else (1 if right10 == nr4[0:10] else None)
    cits = citations(peptides_of(art), self_paths=(SINGLE_BREAKPOINT_ARTIFACT, BREAKPOINT_ARTIFACT))
    return {
        "status": "NOT VERIFIED AGAINST THE CORRECTED JUNCTION — its seam is one residue off",
        "⛔_this_is_a_different_defect_from_the_off_by_two": (
            "this artifact was NOT built by `fusion_breakpoints.py` and does not carry the coding/transcript "
            "exon slip. It models ONE declared breakpoint, and its EWSR1 half (kept to residue 264) matches "
            "the corrected junction exactly."),
        "corrected_junction": junction,
        "modelled_junction": "EWSR1(1-%s)::NR4A3(%s-%s)" % (len(seqs["EWSR1"][:264]), kept_from, len(nr4)),
        "the_difference": (
            "the corrected junction retains NR4A3 from residue 1; this artifact resumes at residue %s, "
            "dropping NR4A3 Met1 (the initiator methionine, which is an INTERNAL residue in a fusion). "
            "Measured against the committed UniProt cache: NR4A3[1:11] == %r, and this artifact's own "
            "`junction_context_right10` is %r. Every junction-SPANNING peptide therefore differs from the "
            "corrected-junction peptide of the same length." % (kept_from, nr4[1:11], right10)),
        "⚠_what_this_does_NOT_settle": (
            "whether Met1 survives is a splice-PHASE question, not an arithmetic one: EWSR1 exon 7 ends at "
            "coding phase 1, so residue 265 is split across the junction and how it completes depends on the "
            "acceptor exon's 5' phase. That caveat has its one home in fusion-object-inventory.json -> "
            "gate._phase_note and is NOT resolved here. So this artifact is flagged UNVERIFIED, not "
            "retracted — the honest state, and the two must not be conflated."),
        "n_spanning_peptides_affected": art.get("n_spanning_peptides"),
        "n_predicted_binders_affected": art.get("n_predicted_binders_by_percentile"),
        "downstream_citations": cits,
        "⛔_scope": "sequence composition only. No affinity, immunogenicity, efficacy or clinical claim.",
        "graded_utc": stamp_utc,
        "graded_et": stamp_et,
        "graded_by": "research/modalities/fusion_neoantigen_invalidation.py",
    }, art


#: The one predicate for "this file LOADS the artifact and its numbers inherit the defect". Used by the
#: banner text, the routed map edit AND the console readout — a second copy is how they disagreed once.
def _n_loaded(banner):
    return sum(1 for r in banner["downstream_consumers"] if r["kind"].startswith("CODE — LOADS"))


def map_edits(banner, banner2=None):
    """The roadmap edits this grading requires.

    ⛔ EVERY EDIT POINTS AND RESTATES NOTHING (rule 1). The map already carries finding 23's consequence —
    "26 predicted binders span seams that do not exist" — so repeating the count here would give one fact a
    second home. What the map does NOT carry is (a) that the artifact is now BANNERED IN PLACE, so a reader
    who opens it is stopped rather than trusted to remember, and (b) that the retraction has a measured
    DOWNSTREAM BLAST RADIUS. Both are pointers.
    """
    c = banner["counts"]
    n_cited = len(banner["downstream_citations"])
    n_loaded = _n_loaded(banner)
    edits = [
        {"section": "§9 finding 23 → the neoantigen lane's owed consequence",
         "anchor": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane).",
         "current_text": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane).",
         "proposed_text": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane). "
                          "✅ **BANNERED IN PLACE 2026-08-03, since regeneration is still not this lane's "
                          "to do:** the artifact now leads with a `%s` block that refuses quotation, grades "
                          "every junction against the corrected windows, and — the part nothing carried "
                          "before — names its **downstream blast radius**: **%d committed files quote its "
                          "peptide strings and %d modules LOAD it and recompute from it**, so `hla-coverage`, "
                          "`vaccine-construct` and the two patient demos all inherit the defect without ever "
                          "printing a seam. Per-file list and per-junction grading: "
                          "[`fusion-breakpoint-neoantigens.json`](../modalities/fusion-breakpoint-neoantigens.json) "
                          "→ `%s`, mirrored in "
                          "[`fusion-neoantigen-retraction.json`](../modalities/fusion-neoantigen-retraction.json)."
                          % (BANNER_KEY, n_cited, n_loaded, BANNER_KEY),
         "why": "the defect was diagnosed and then unowned; a known defect that is not visible AT THE "
                "ARTIFACT reads as a handled one, and the downstream consumers were never enumerated at all",
         "artifact": "fusion-breakpoint-neoantigens.json:%s" % BANNER_KEY},
    ]
    if banner2:
        edits.append(
            # ⚠ APPENDED AT THE END OF THE BULLET, NOT SPLICED INTO ITS OPENING SENTENCE. A first attempt
            # anchored on "`fusion_cofold.py` resumed NR4A3 at residue 2;" and REPLACED it, which dropped a
            # long clause into the middle of a sentence whose second half then read as a non-sequitur. An
            # edit that applies cleanly and reads badly is still a defect in the map.
            {"section": "§9 finding 23 → the OTHER neoantigen artifact",
             "anchor": "because C166 would not have been in the fusion at all.",
             "current_text": "because C166 would not have been in the fusion at all.",
             "proposed_text": "because C166 would not have been in the fusion at all. ⚠ **But "
                              "\"residue 2 is the exon-correct one\" holds for a FOLD model and not for a "
                              "PEPTIDE one, and this page did not draw that distinction:** the corrected "
                              "junction retains NR4A3 from residue **1**, so "
                              "`fusion-neoantigen-predictions.json` — which uses the same residue-2 seam — "
                              "has all %s of its junction-spanning peptides differing from the corrected "
                              "junction's by NR4A3 **Met1**, and its lead epitope is quoted in "
                              "`research/README.md` and three manuscripts. It is flagged **UNVERIFIED, not "
                              "retracted**, because whether Met1 survives is a splice-PHASE question that "
                              "[`fusion-object-inventory.json`](../modalities/fusion-object-inventory.json) "
                              "→ `gate._phase_note` explicitly leaves open."
                              % banner2.get("n_spanning_peptides_affected"),
             "why": "the page treats the residue-2 model as simply vindicated; that holds for the co-fold "
                    "lane and does not hold for the peptide lane, where one residue at the seam changes "
                    "every spanning peptide",
             "artifact": "fusion-neoantigen-predictions.json:%s" % BANNER_KEY})
    return edits


def main(argv=None):
    import argparse
    import datetime
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="stamp the banners into the artifacts")
    ap.add_argument("--edits-out", default=os.path.join(HERE, "fusion-neoantigen-retraction.json"))
    a = ap.parse_args(argv)

    utc = datetime.datetime.now(datetime.timezone.utc)
    stamp_utc = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    et = utc - datetime.timedelta(hours=4)                        # EDT; CLAUDE.md §1 reports in ET
    stamp_et = et.strftime("%Y-%m-%d %-I:%M %p ET")

    banner, art = breakpoint_banner(stamp_utc, stamp_et)
    banner2, art2 = single_breakpoint_banner(stamp_utc, stamp_et)
    print(banner["one_line"])
    print("  downstream files quoting it: %d" % len(banner["downstream_citations"]))
    for row in banner["downstream_citations"]:
        print("    %-58s %3d peptides" % (row["path"], row["n_peptides_quoted"]))
    # ⛔ THE SAME PREDICATE THE BANNER AND THE MAP EDIT USE. This read `startswith("CODE")`, which swept in
    # the artifact's own PRODUCER and printed 7 where the committed data said 6 — a console line disagreeing
    # with the artifact beside it, which is the exact defect class this module exists to close.
    print("  files that LOAD it and recompute: %d" % _n_loaded(banner))
    for row in banner["downstream_consumers"]:
        print("    %-58s %s" % (row["path"], row["kind"]))
    print(banner2["status"])
    for row in banner2["downstream_citations"]:
        print("    %-58s %3d peptides" % (row["path"], row["n_peptides_quoted"]))

    doc = {"_title": "EWSR1::NR4A3 neoantigen artifacts graded against the corrected junction",
           "_cost": "$0 — committed inputs only, no network, no model, no prediction",
           "_utc": stamp_utc, "_et": stamp_et,
           "breakpoint_artifact": banner, "single_breakpoint_artifact": banner2,
           "map_edits_required": map_edits(banner, banner2)}
    with open(a.edits_out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print("wrote", os.path.relpath(a.edits_out, REPO))

    if a.write:
        for path, b, target in ((BREAKPOINT_ARTIFACT, banner, art),
                                (SINGLE_BREAKPOINT_ARTIFACT, banner2, art2)):
            out = {BANNER_KEY: b}
            out.update(target)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
            print("bannered", os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
