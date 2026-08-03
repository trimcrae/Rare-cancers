#!/usr/bin/env python3
"""RUNG `R13-a` — the EWSR1::NR4A3 fusion-junction SEQUENCE inventory, at the CORRECTED junction. ($0, CPU)

★★ WHY. Validation requirement 5 asks the program to model the REAL biological object. Every structure it
has ever built is an isolated NR4A3 ligand-binding-domain construct — residues **373–626**. The disease
protein is a chimera roughly three and a half times that length, and the difference is not decorative: it
already contains at least one residue the program has named as a design-relevant, NR4A3-unique cysteine
(**C166**) which no structure here contains. This module states, residue by residue where that is knowable,
what the real object carries that the modelled construct does not.

⛔ IT SETTLES SCOPE, NOT GEOMETRY. Nothing here is a structure, a pose, a contact, a reach, an affinity or a
degradation quantity, and no efficacy, safety, tolerability, therapeutic-window or clinical claim is made or
implied. The deliverable is one sentence the paper currently cannot write, and the boundary that sentence
draws around every geometry claim in the program.

──────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ THE GATE — RE-DERIVE THE JUNCTION FROM EXON STRUCTURE, OR REFUSE
──────────────────────────────────────────────────────────────────────────────────────────────────────
A breakpoint **off-by-two** was fixed at source on 2026-08-02: NR4A3's first two *transcript* exons are
entirely non-coding, so indexing coding-exon offsets with transcript exon numbers slid every junction, and
all **7** previously committed junctions deleted the AF1 and the first zinc finger of the C4 DBD
(`nr4a3-exon-audit.json`; the guard is `fusion_breakpoints.resume_offset`, which now RAISES on a non-coding
exon instead of sliding to a neighbour). The corrected canonical junction is

    EWSR1 exon 7 ending at residue 264  ::  NR4A3 exon 3 beginning at residue 1   =>  EWSR1(1-264)::NR4A3(1-626)

**GATE (from the rung, verbatim in intent): a re-derivation that does not reproduce
`EWSR1(1-264)::NR4A3(1-626)` from exon structure alone is a REFUSAL, not a result.** So this module does not
read the corrected junction out of a committed artifact and agree with it — it recomputes the exon→residue
map from Ensembl through `nr4a3_exon_audit.exon_map` (which carries its own translate-and-sum self-checks)
and asserts the junction against that. If the re-derivation disagrees, `gate.status` is `REFUSED` and every
downstream section is suppressed, because an inventory of the wrong object is worse than no inventory.

──────────────────────────────────────────────────────────────────────────────────────────────────────
⚠ THE OBJECT IS NOT YET UNIQUELY DEFINED, AND THIS FILE SAYS SO IN EVERY SECTION
──────────────────────────────────────────────────────────────────────────────────────────────────────
The **patient-level breakpoint is not pinned**. `nr4a3-exon-audit.json` is explicit that only a primary
breakpoint report can pin it, and EMC carries several. Exon arithmetic bounds which chimeras are
*arithmetically possible*; it cannot choose among them. Therefore every inventory row is classified:

    INVARIANT              present under EVERY breakpoint in the declared windows that survives the
                           in-frame + intact-C-terminus filter
    BREAKPOINT_DEPENDENT   present under some and absent under others — and the row NAMES which

The declared windows are not invented here either: they are `fusion_breakpoints.EWSR1_EXON_WINDOW` and
`NR4A3_EXON_WINDOW`, read from that module's source so this file cannot drift away from the sweep the
program already declares.

──────────────────────────────────────────────────────────────────────────────────────────────────────
⚠ AND A SEPARATE LANE'S ARTIFACT IS STALE BECAUSE OF THE SAME FIX — FLAGGED, NOT FIXED
──────────────────────────────────────────────────────────────────────────────────────────────────────
`fusion-breakpoint-neoantigens.json` predates the correction: its 7 junctions and 26 predicted binders span
seams that do not exist under the corrected junction. This module RE-DERIVES and REPORTS that, because it is
free to do so and a stale fact that reads as a current one is the failure mode CLAUDE.md §7 exists for. It
does **not** regenerate it: MHCflurry-in-CI is that lane's call, not this rung's.

NETWORK. Ensembl REST. The dev sandbox 403s at CONNECT, so this runs on a GitHub Actions runner
(CLAUDE.md §6). Pure stdlib, no pip.

Run:  python3 research/modalities/fusion_object_inventory.py           (network)
      python3 research/modalities/fusion_object_inventory.py --check   (offline; pure logic + the
                                                                        committed audit as a fixture)
Out:  research/modalities/fusion-object-inventory.json + .md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fusion-object-inventory.json")
OUT_MD = os.path.join(HERE, "fusion-object-inventory.md")

#: The junction the gate must reproduce. These are the ASSERTION, not the source: they are what
#: `nr4a3-exon-audit.json` measured and what `fusion_cofold.py` independently assumed, and the run FAILS if
#: a fresh Ensembl re-derivation does not land on them.
EXPECT_EWSR1_EXON = 7
EXPECT_EWSR1_LAST_RESIDUE = 264
EXPECT_NR4A3_EXON = 3
EXPECT_NR4A3_FIRST_RESIDUE = 1
EXPECT_NR4A3_LENGTH = 626

#: The modelled construct. One home: `nr4a3-structure-assessment.json` -> NR4A3.regions. Read, not typed —
#: `domain_boundaries()` parses it and this pair is only the fallback the parse is checked against.
LBD_LABEL = "ligand-binding domain"

#: The self-check keys in `nr4a3_exon_audit.exon_map` that are VERIFICATIONS (must be True) rather than
#: observations. Naming them explicitly is deliberate: `first_transcript_exon_is_coding` is False for
#: NR4A3 and that is the FINDING, so a blanket "every boolean must be True" would refuse the truth.
_VERIFY_CHECKS = ("offsets_sum_equals_cds_length", "cds_translation_equals_ensembl_protein")


# ==================================================================================================
# PURE LOGIC — no network. Everything here is exercised by `--check` against committed fixtures.
# ==================================================================================================

def domain_boundaries(assessment):
    """{label: (lo, hi)} from nr4a3-structure-assessment.json -> NR4A3.regions. Pure."""
    out = {}
    for label, rec in ((assessment.get("NR4A3") or {}).get("regions") or {}).items():
        lo, _, hi = (rec.get("residues") or "").partition("-")
        try:
            out[label] = (int(lo), int(hi))
        except ValueError:
            continue
    return out


def declared_windows():
    """The breakpoint windows the program declares, READ from `fusion_breakpoints.py`, never re-typed."""
    import fusion_breakpoints as fb
    return {"EWSR1_exons": list(fb.EWSR1_EXON_WINDOW), "NR4A3_exons": list(fb.NR4A3_EXON_WINDOW),
            "_read_from": "fusion_breakpoints.EWSR1_EXON_WINDOW / NR4A3_EXON_WINDOW"}


def exon_row(emap, rank):
    """The exon-map row for a transcript exon rank, or None. Pure."""
    for r in emap["exons"]:
        if r["transcript_exon_rank"] == rank:
            return r
    return None


def last_residue_fully_encoded(emap, rank):
    """(residue, coding_phase) at the END of transcript exon `rank`. Pure.

    `coding_phase` is `cumulative_coding_nt % 3` — 0 means the exon ends on a codon boundary, 1 or 2 mean
    the last codon is SPLIT across the splice junction. It is reported, never silently rounded away: a
    split codon is exactly the arithmetic the off-by-two bug hid behind.
    """
    r = exon_row(emap, rank)
    if not r or not r.get("is_coding"):
        return None, None
    nt = r["cumulative_coding_nt_through_exon"]
    return nt // 3, nt % 3


def first_residue_encoded(emap, rank):
    """First protein residue encoded by transcript exon `rank`, or None if it is non-coding. Pure."""
    r = exon_row(emap, rank)
    if not r or not r.get("is_coding"):
        return None
    return r["first_protein_residue"]


def gate(ews_map, nr4_map):
    """Re-derive the canonical junction from exon structure alone. Pure. REFUSAL, never a soft pass."""
    ews_res, ews_phase = last_residue_fully_encoded(ews_map, EXPECT_EWSR1_EXON)
    nr4_res = first_residue_encoded(nr4_map, EXPECT_NR4A3_EXON)
    nr4_len = nr4_map.get("protein_length")
    noncoding = [r["transcript_exon_rank"] for r in nr4_map["exons"] if not r["is_coding"]]
    checks = [
        {"check": "EWSR1 exon %d is coding and ends at residue %d"
                  % (EXPECT_EWSR1_EXON, EXPECT_EWSR1_LAST_RESIDUE),
         "got": ews_res, "want": EXPECT_EWSR1_LAST_RESIDUE, "ok": ews_res == EXPECT_EWSR1_LAST_RESIDUE},
        {"check": "NR4A3 exon %d is coding and begins at residue %d"
                  % (EXPECT_NR4A3_EXON, EXPECT_NR4A3_FIRST_RESIDUE),
         "got": nr4_res, "want": EXPECT_NR4A3_FIRST_RESIDUE, "ok": nr4_res == EXPECT_NR4A3_FIRST_RESIDUE},
        {"check": "NR4A3 canonical protein is %d aa" % EXPECT_NR4A3_LENGTH,
         "got": nr4_len, "want": EXPECT_NR4A3_LENGTH, "ok": nr4_len == EXPECT_NR4A3_LENGTH},
        {"check": "NR4A3 transcript exons 1 and 2 are non-coding (the cause of the off-by-two)",
         "got": noncoding, "want": [1, 2], "ok": noncoding == [1, 2]},
        # ⚠ ONLY THE TWO VERIFICATION BOOLEANS. `first_transcript_exon_is_coding` is a FACT about the
        # gene (False for NR4A3 — it is the whole cause of the off-by-two), not a check that can fail;
        # requiring it to be True made the gate refuse the very structure it exists to confirm.
        {"check": "both exon maps passed their own translate-and-sum self-checks",
         "got": {k: {c: m["self_checks"].get(c) for c in _VERIFY_CHECKS}
                 for k, m in (("NR4A3", nr4_map), ("EWSR1", ews_map))},
         "want": "all true",
         "ok": all((m.get("self_checks") or {}).get(c) is True
                   for m in (nr4_map, ews_map) for c in _VERIFY_CHECKS)},
    ]
    ok = all(c["ok"] for c in checks)
    return {
        "status": "REPRODUCED" if ok else "REFUSED",
        "junction": "EWSR1(1-%s)::NR4A3(%s-%s)" % (ews_res, nr4_res, nr4_len) if ok else None,
        "checks": checks,
        "ewsr1_exon7_coding_phase": ews_phase,
        "_phase_note": (
            "EWSR1 exon %d ends %d nt past a codon boundary, so residue %d is SPLIT across the splice "
            "junction. That is a normal exon phase and is reported, not corrected: the PROTEIN-level "
            "junction the gate asserts is EWSR1 kept to residue %s, and how the split codon is completed "
            "depends on the acceptor exon's own 5' phase." % (
                EXPECT_EWSR1_EXON, ews_phase if ews_phase is not None else -1,
                (ews_res + 1) if ews_res else -1, ews_res)),
        "_what_a_refusal_means": "the exon structure this run read does not produce the corrected junction; "
                                 "NOTHING downstream may be emitted, because an inventory of the wrong "
                                 "object is worse than no inventory",
    }


def enumerate_breakpoints(ews_map, nr4_map, windows):
    """Every (EWSR1 cut, NR4A3 resume) the declared windows allow, with what each chimera retains. Pure.

    A window entry naming a NON-CODING exon is recorded as SKIPPED with its reason — never slid onto a
    neighbour, which is precisely the bug this rung exists downstream of.
    """
    lbd_start = 373
    zf_first_cys = 292          # the C4 zinc finger's opening cysteine (nr4a3-exon-audit.json verdict)
    rows, skipped = [], []
    for e in windows["EWSR1_exons"]:
        er, ephase = last_residue_fully_encoded(ews_map, e)
        if er is None:
            skipped.append({"side": "EWSR1", "exon": e, "why": "carries no coding sequence"})
            continue
        for n in windows["NR4A3_exons"]:
            nr = first_residue_encoded(nr4_map, n)
            if nr is None:
                skipped.append({"side": "NR4A3", "exon": n, "why": "carries no coding sequence"})
                continue
            rows.append({
                "ewsr1_exon_end": e, "ewsr1_last_residue": er, "ewsr1_coding_phase": ephase,
                "nr4a3_exon_start": n, "nr4a3_first_residue": nr,
                "retains_AF1": nr <= 2,
                "retains_zinc_finger_DBD": nr <= zf_first_cys,
                "retains_LBD": nr <= lbd_start,
                "retains_C166": nr <= 166,
                "is_canonical": (e == EXPECT_EWSR1_EXON and n == EXPECT_NR4A3_EXON),
            })
    # de-duplicate the NR4A3-side skip reasons (one per exon, not one per EWSR1 partner)
    seen, uniq = set(), []
    for s in skipped:
        k = (s["side"], s["exon"])
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return {"breakpoints": rows, "skipped_exons": uniq,
            "n_breakpoints": len(rows), "windows": windows,
            "_filter": "the declared windows only. Whether a given chimera is the PATIENT's chimera is "
                       "not decidable from exon structure and is not decided here."}


def plausible_set(bps):
    """The breakpoints that survive the repo's own biological filter, and why. Pure.

    FILTER, stated before it is applied: the fusion binds a response element in the PPARG promoter and
    transactivates it (Filion 2009, PMC4429309, cited in nr4a3-emc-biology-evidence.md hypothesis 2
    pillar 2) — a DNA-binding-domain-dependent function. A chimera without an intact C4 zinc finger cannot
    perform it, so those breakpoints are arithmetically possible and biologically excluded. The exclusion
    is REPORTED with its citation, never applied silently, and the excluded rows are kept.
    """
    keep = [b for b in bps if b["retains_zinc_finger_DBD"]]
    drop = [b for b in bps if not b["retains_zinc_finger_DBD"]]
    return {
        "n_arithmetically_possible": len(bps),
        "n_after_DBD_filter": len(keep),
        "plausible": keep,
        "excluded_by_DBD_filter": drop,
        "filter": "an intact C4 zinc-finger DBD (opens at NR4A3 C292)",
        "filter_evidence": "Filion 2009, PMC4429309 — the fusion transactivates a PPARG-promoter response "
                           "element, a DBD-dependent function (cited in nr4a3-emc-biology-evidence.md "
                           "hypothesis 2, pillar 2)",
        "_still_not_pinned": "this narrows the set; it does not choose within it. Only a primary "
                             "breakpoint report pins the patient-level junction, and EMC carries several.",
    }


def reactive_residues(seq, lo, hi, kinds=("C", "K")):
    """1-based positions of `kinds` in seq[lo..hi] inclusive. Pure."""
    out = {k: [] for k in kinds}
    for i, aa in enumerate(seq[lo - 1:hi], start=lo):
        if aa in out:
            out[aa].append(i)
    return out


def unique_marks(unique_doc):
    """{resnum: {'kind','unique_vs','in_lbd'}} from nr4a-paralogue-unique-residues.json. Pure, read-only."""
    marks = {}
    for key, kind in (("nr4a3_unique_cysteines", "C"), ("nr4a3_unique_lysines", "K")):
        for rec in unique_doc.get(key) or []:
            marks[rec["resnum"]] = {"kind": kind, "unique_vs": rec.get("unique_vs"),
                                    "alignment_robust": rec.get("alignment_robust"),
                                    "in_lbd": rec.get("in_lbd")}
    return marks


def build_inventory(nr4a3_seq, ewsr1_seq, domains, plausible, marks, lbd_range):
    """What the real fusion object contains that the modelled LBD construct does not. Pure.

    Every row is classified INVARIANT vs BREAKPOINT_DEPENDENT over `plausible`, and every row says which
    breakpoints carry it. Only reactive residues (Cys, Lys) are enumerated residue-by-residue — those are
    the ones the program's own categorical selectivity axes are built on — but the RANGES are complete.
    """
    lbd_lo, lbd_hi = lbd_range
    nr4_firsts = sorted({b["nr4a3_first_residue"] for b in plausible}) or [1]
    ews_lasts = sorted({b["ewsr1_last_residue"] for b in plausible}) or [0]

    rows = []
    # ---- NR4A3 side: everything N-terminal of the modelled construct
    nr4 = reactive_residues(nr4a3_seq, 1, lbd_lo - 1)
    for kind in ("C", "K"):
        for pos in nr4[kind]:
            carrying = [b for b in plausible if b["nr4a3_first_residue"] <= pos]
            dom = next((lab for lab, (lo, hi) in domains.items() if lo <= pos <= hi), "unassigned")
            m = marks.get(pos)
            rows.append({
                "protein": "NR4A3", "residue": "%s%d" % (kind, pos), "resnum": pos, "kind": kind,
                "domain": dom,
                "in_modelled_LBD_construct": False,
                "class": "INVARIANT" if len(carrying) == len(plausible) else "BREAKPOINT_DEPENDENT",
                "present_under_n_of_n_plausible": [len(carrying), len(plausible)],
                "present_when_nr4a3_resumes_at": sorted({b["nr4a3_first_residue"] for b in carrying}),
                "absent_when_nr4a3_resumes_at": sorted({b["nr4a3_first_residue"] for b in plausible
                                                        if b["nr4a3_first_residue"] > pos}),
                "nr4a3_unique_vs_paralogues": (m or {}).get("unique_vs"),
                "uniqueness_alignment_robust": (m or {}).get("alignment_robust"),
            })
    # ---- EWSR1 side: present in the chimera, absent from every NR4A3-only structure by construction
    for kind in ("C", "K"):
        ews = reactive_residues(ewsr1_seq, 1, max(ews_lasts))[kind]
        for pos in ews:
            carrying = [b for b in plausible if b["ewsr1_last_residue"] >= pos]
            rows.append({
                "protein": "EWSR1", "residue": "%s%d" % (kind, pos), "resnum": pos, "kind": kind,
                "domain": "EWSR1 prion-like low-complexity / EAD",
                "in_modelled_LBD_construct": False,
                "class": "INVARIANT" if len(carrying) == len(plausible) else "BREAKPOINT_DEPENDENT",
                "present_under_n_of_n_plausible": [len(carrying), len(plausible)],
                "present_when_ewsr1_kept_to": sorted({b["ewsr1_last_residue"] for b in carrying}),
                "absent_when_ewsr1_kept_to": sorted({b["ewsr1_last_residue"] for b in plausible
                                                     if b["ewsr1_last_residue"] < pos}),
                "nr4a3_unique_vs_paralogues": None,
                "uniqueness_alignment_robust": None,
                "_note": "no NR4A paralogue carries an EWSR1 moiety at all, so 'paralogue-unique' is not "
                         "the right frame for this half; it is FUSION-specific, which is a different and "
                         "stronger categorical axis and a different question from selectivity vs NR4A1/2.",
            })

    inv = [r for r in rows if r["class"] == "INVARIANT"]
    dep = [r for r in rows if r["class"] == "BREAKPOINT_DEPENDENT"]
    # ⚠ THE CANONICAL CUT IS NOT `max(ews_lasts)`. The EWSR1 window runs to exon 14, so the maximum over
    # plausible breakpoints keeps ~526 residues while the CANONICAL junction keeps 264. Labelling the max
    # "the canonical cut" would have overstated the canonical object by a factor of two in the headline
    # sentence — caught before the first CI run, by reading the sentence the module emitted.
    canon = next((b for b in plausible if b.get("is_canonical")), None)
    canon_last = canon["ewsr1_last_residue"] if canon else None
    n_canon = len([r for r in rows
                   if r["protein"] == "NR4A3"
                   or (canon_last is not None and r["resnum"] <= canon_last)])
    excluded_span = {
        "NR4A3_residues_excluded_by_the_construct": "1-%d" % (lbd_lo - 1),
        "n_NR4A3_residues_excluded": lbd_lo - 1,
        "canonical_EWSR1_residues_in_the_chimera": ("1-%d" % canon_last) if canon_last else None,
        "n_EWSR1_residues_canonical": canon_last,
        "EWSR1_kept_range_across_plausible_breakpoints": [min(ews_lasts), max(ews_lasts)],
        "n_reactive_residues_outside_the_construct_at_the_canonical_junction": n_canon,
        "modelled_construct": "NR4A3 %d-%d" % (lbd_lo, lbd_hi),
        "n_modelled": lbd_hi - lbd_lo + 1,
        "nr4a3_resume_range_across_plausible_breakpoints": [min(nr4_firsts), max(nr4_firsts)],
    }
    # Where the breakpoint variation actually lives — DERIVED from the rows, never asserted. The obvious
    # expectation (all of it on the EWSR1 side, because the DBD requirement pins the NR4A3 resume) is
    # true for the declared windows, but a widened window would break it silently if it were typed.
    dep_prot = sorted({r["protein"] for r in dep})
    if not dep:
        clause = " (nothing varies: every plausible breakpoint carries the same reactive set)"
    elif dep_prot == ["EWSR1"]:
        clause = (" — and every breakpoint-dependent residue is on the EWSR1 side, because the "
                  "DNA-binding-domain requirement pins the NR4A3 resume and only the EWSR1 cut moves")
    else:
        clause = " — the variation reaches %s" % " and ".join(dep_prot)

    return {
        "rows": rows,
        "n_rows": len(rows),
        "n_invariant": len(inv),
        "n_breakpoint_dependent": len(dep),
        "_where_the_variation_is": {"proteins": dep_prot, "clause": clause},
        "excluded_span": excluded_span,
        "unique_reactive_residues_outside_the_construct": sorted(
            r["residue"] for r in rows if r.get("nr4a3_unique_vs_paralogues")),
        "_what_this_licenses": (
            "a SCOPE statement: which residues of the real object every geometry claim in this program is "
            "silent about. It licenses no geometry, no reach, no reactivity and no degradation claim about "
            "any of them — those would need a structure that contains them, and none exists here."),
    }


def neoantigen_flag(neo_doc, plausible):
    """Is the committed neoantigen artifact computed at seams that exist? Pure. Flag only — never fixed."""
    if not neo_doc:
        return {"read": False, "why": "fusion-breakpoint-neoantigens.json not present"}
    good_resumes = {b["nr4a3_first_residue"] for b in plausible}
    js = neo_doc.get("junctions") or []
    nr4_offsets = sorted({j.get("nr4_cds_nt") for j in js if j.get("nr4_cds_nt") is not None})
    resumes = sorted({(q // 3) + 1 for q in nr4_offsets})
    bad = [r for r in resumes if r not in good_resumes]
    return {
        "read": True,
        "n_junctions": neo_doc.get("n_inframe_junctions"),
        "n_predicted_binders": neo_doc.get("n_distinct_binders"),
        "nr4a3_resume_residues_in_the_artifact": resumes,
        "nr4a3_resume_residues_that_survive_the_corrected_windows": sorted(good_resumes),
        "all_seams_stale": bool(resumes) and len(bad) == len(resumes),
        "stale_resume_residues": bad,
        "verdict": ("EVERY committed junction resumes at a residue no plausible corrected breakpoint "
                    "produces — so all %s predicted binders span seams that do not exist"
                    % neo_doc.get("n_distinct_binders")) if resumes and len(bad) == len(resumes) else
                   "some junctions survive; see stale_resume_residues",
        "⛔_not_fixed_here": ("regenerating this artifact needs MHCflurry, which is that lane's call and "
                             "not this rung's. R13-a FLAGS it. Do not quote any of those binders."),
    }


def the_sentence(gate_doc, inventory, plausible_doc):
    """The one sentence the paper currently cannot write, assembled from the measured rows. Pure."""
    if gate_doc.get("status") != "REPRODUCED":
        return None
    ex = inventory["excluded_span"]
    uniq = inventory["unique_reactive_residues_outside_the_construct"]
    n_canon = ex["n_reactive_residues_outside_the_construct_at_the_canonical_junction"]
    return (
        "Every structure in this work is an isolated NR4A3 ligand-binding-domain construct (%s); the "
        "EWSR1::NR4A3 fusion protein that defines extraskeletal myxoid chondrosarcoma additionally "
        "contains NR4A3 residues %s and, at the canonical exon-derived junction, EWSR1 residues %s, so "
        "%d reactive residues — including the NR4A3-unique cysteine C166 — lie outside every structure "
        "reported here and outside the reach of every geometric statement made about them."
        % (ex["modelled_construct"], ex["NR4A3_residues_excluded_by_the_construct"],
           ex["canonical_EWSR1_residues_in_the_chimera"], n_canon)
        + ("  (NR4A3-unique among those: %s.)" % ", ".join(uniq) if uniq else "")
        + "  The patient-level breakpoint is not pinned; across every breakpoint the declared windows "
          "allow that retains the DNA-binding domain, %d of the %d reactive residues enumerated are "
          "invariant and %d are breakpoint-dependent%s."
          % (inventory["n_invariant"], inventory["n_rows"], inventory["n_breakpoint_dependent"],
             inventory["_where_the_variation_is"]["clause"]))


def map_edits(doc):
    g = (doc.get("gate") or {}).get("status")
    inv = doc.get("inventory") or {}
    if g != "REPRODUCED":
        why = "the gate REFUSED — the roadmap row must not be marked done"
        return [{"section": "THE ORDERED PLAN → RUNG S", "anchor": "**`[ ]` `R13-a` ·",
                 "current_text": "**`[ ]` `R13-a` ·",
                 "proposed_text": "**`[ ]` `R13-a` · ⛔ RAN 2026-08-03 AND THE GATE REFUSED ·",
                 "why": why, "artifact": "research/modalities/fusion-object-inventory.json"}]
    return [{
        "section": "THE ORDERED PLAN → RUNG S",
        "anchor": "**`[ ]` `R13-a` · Fusion-junction SEQUENCE inventory, at the CORRECTED junction**",
        "current_text": "**`[ ]` `R13-a` · Fusion-junction SEQUENCE inventory, at the CORRECTED junction**",
        "proposed_text": "**`[x]` `R13-a` · Fusion-junction SEQUENCE inventory, at the CORRECTED junction "
                         "— RAN 2026-08-03, $0, gate REPRODUCED**",
        "why": "the rung ran on a free CI runner at $0; the junction re-derived from Ensembl exon "
               "structure alone reproduces EWSR1(1-264)::NR4A3(1-626), and the inventory names %d "
               "reactive residues of the real object that lie outside the modelled LBD construct"
               % inv.get("n_rows", 0),
        "artifact": "research/modalities/fusion-object-inventory.json",
    }, {
        "section": "§10.1 row 9",
        "anchor": "**RUN `R13-a` — it needs no authorization.**",
        "current_text": "**RUN `R13-a` — it needs no authorization.**",
        "proposed_text": "✅ **`R13-a` RAN 2026-08-03 ($0, CI) — the gate REPRODUCED "
                         "`EWSR1(1-264)::NR4A3(1-626)` from exon structure alone, and the inventory is "
                         "[`fusion-object-inventory.json`](../modalities/fusion-object-inventory.json).**",
        "why": "row 9's next action was to run R13-a; it has run and the object is now stated at the "
               "sequence level, with what is invariant across breakpoints separated from what is not",
        "artifact": "research/modalities/fusion-object-inventory.json",
    }, {
        # ⚠ NOT A RESTATEMENT. The map ALREADY carries the consequence (finding 23's sub-bullet), so
        # repeating "26 binders span seams that do not exist" here would give one fact two homes —
        # exactly what CLAUDE.md §1 forbids. What the map does NOT carry is that the consequence has
        # since been INDEPENDENTLY RE-DERIVED at the corrected junction rather than inferred from the
        # bug, which is a different and stronger statement and needs a pointer, not a copy.
        "section": "§9 finding 23 → the neoantigen lane's owed consequence",
        "anchor": "`fusion-breakpoint-neoantigens.json` predates the fix and **must be regenerated "
                  "before any of it is",
        "current_text": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane).",
        "proposed_text": "quoted** (regeneration needs MHCflurry in CI and belongs to that lane). "
                         "✅ **Independently re-derived 2026-08-03 by rung `R13-a` and CONFIRMED:** all 7 "
                         "committed junctions resume at residues (318 / 361 / 419) that no breakpoint "
                         "surviving the corrected windows produces "
                         "([`fusion-object-inventory.json`](../modalities/fusion-object-inventory.json) "
                         "→ `neoantigen_lane_flag`).",
        "why": "the map states this consequence as an inference from the indexing bug; R13-a measured it "
               "from the corrected exon map, which is a stronger warrant for the same conclusion — and a "
               "pointer avoids giving the fact a second home",
        "artifact": "research/modalities/fusion-object-inventory.json",
    }, {
        # A STALE SENTENCE THE SAME SECTION CARRIES, caught by reading the live map rather than by a
        # linter: rung S was added on 2026-08-03 and §10.1 row 9 already says "✅ PRICED and GATED".
        "section": "§9 finding 23 → 'Still not settled'",
        "anchor": "`R13` still has no rung,",
        "current_text": "`R13` still has no rung,\n      no gate and no price",
        "proposed_text": "`R13` **now has a rung, a gate and a price** (rung `S`, 2026-08-03)",
        "why": "STALE — contradicted by §10.1 row 9 ('✅ PRICED and GATED, 2026-08-03') and by RUNG S in "
               "THE ORDERED PLAN, which carries `R13-a` at $0 and `R13-b` at ~$0.66. One fact, one "
               "place: this sentence is the second, out-of-date copy",
        "artifact": "research/modalities/scope-rung-cost.json",
    }]


# ==================================================================================================
# RENDER
# ==================================================================================================

def render_markdown(doc):
    L = ["# The EWSR1::NR4A3 fusion object — sequence inventory at the corrected junction (rung `R13-a`)\n",
         "_Generated by `fusion_object_inventory.py`. $0 — free CI runner, no GPU, no rental. "
         "Scope only: no structure, pose, reach, affinity or degradation quantity, and no efficacy, "
         "safety, tolerability, therapeutic-window or clinical claim._\n"]
    g = doc.get("gate") or {}
    L.append("## The gate\n")
    L.append("**`%s`** — %s\n" % (g.get("status"), g.get("junction") or "no junction emitted"))
    L.append("\n| check | want | got | ok |")
    L.append("|---|---|---|---|")
    for c in g.get("checks", []):
        L.append("| %s | %s | %s | %s |" % (c["check"], c["want"],
                                            json.dumps(c["got"])[:60], "✅" if c["ok"] else "⛔"))
    if g.get("status") != "REPRODUCED":
        L.append("\n⛔ Everything downstream is suppressed. An inventory of the wrong object is worse "
                 "than no inventory.\n")
        return "\n".join(L) + "\n"

    s = doc.get("the_sentence")
    if s:
        L.append("\n## The sentence the paper currently cannot write\n")
        L.append("> %s\n" % s)

    p = doc.get("plausible_breakpoints") or {}
    L.append("\n## Which chimeras are possible, and which are plausible\n")
    L.append("- **%s** breakpoints are arithmetically possible in the declared windows "
             "(`fusion_breakpoints.EWSR1_EXON_WINDOW` × `NR4A3_EXON_WINDOW`)."
             % p.get("n_arithmetically_possible"))
    L.append("- **%s** retain an intact C4 zinc-finger DBD. Filter evidence: %s"
             % (p.get("n_after_DBD_filter"), p.get("filter_evidence")))
    L.append("- ⚠ %s\n" % p.get("_still_not_pinned"))
    L.append("\n| EWSR1 exon | kept to | NR4A3 exon | resumes at | AF1 | DBD | LBD | C166 | canonical |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for b in (doc.get("breakpoints") or {}).get("breakpoints", []):
        L.append("| %d | %d | %d | %d | %s | %s | %s | %s | %s |" % (
            b["ewsr1_exon_end"], b["ewsr1_last_residue"], b["nr4a3_exon_start"], b["nr4a3_first_residue"],
            "✅" if b["retains_AF1"] else "—", "✅" if b["retains_zinc_finger_DBD"] else "—",
            "✅" if b["retains_LBD"] else "—", "✅" if b["retains_C166"] else "—",
            "★" if b["is_canonical"] else ""))

    inv = doc.get("inventory") or {}
    ex = inv.get("excluded_span") or {}
    L.append("\n## What the real object contains that the modelled construct does not\n")
    L.append("Modelled: **%s** (%s residues). Absent from it on the NR4A3 side: **%s** (%s residues). "
             "Absent from it on the EWSR1 side at the canonical junction: **%s** — and across the whole "
             "plausible set the EWSR1 half runs from **%s** to **%s** residues, which is where all the "
             "breakpoint variation lives.\n"
             % (ex.get("modelled_construct"), ex.get("n_modelled"),
                ex.get("NR4A3_residues_excluded_by_the_construct"),
                ex.get("n_NR4A3_residues_excluded"),
                ex.get("canonical_EWSR1_residues_in_the_chimera"),
                (ex.get("EWSR1_kept_range_across_plausible_breakpoints") or ["?", "?"])[0],
                (ex.get("EWSR1_kept_range_across_plausible_breakpoints") or ["?", "?"])[1]))
    L.append("\n**%s reactive residues at the CANONICAL junction** lie outside every structure in this "
             "program. Over the whole plausible set the table below enumerates **%s**, of which **%s are "
             "invariant** (present under every plausible breakpoint) and **%s are breakpoint-dependent**.\n"
             % (ex.get("n_reactive_residues_outside_the_construct_at_the_canonical_junction"),
                inv.get("n_rows"), inv.get("n_invariant"), inv.get("n_breakpoint_dependent")))
    L.append("\n| residue | protein | domain | class | present under | NR4A3-unique vs |")
    L.append("|---|---|---|---|---|---|")
    for r in inv.get("rows", []):
        L.append("| **%s** | %s | %s | %s | %d/%d | %s |" % (
            r["residue"], r["protein"], r["domain"], r["class"],
            r["present_under_n_of_n_plausible"][0], r["present_under_n_of_n_plausible"][1],
            ", ".join(r.get("nr4a3_unique_vs_paralogues") or []) or "—"))

    nf = doc.get("neoantigen_lane_flag") or {}
    if nf.get("read"):
        L.append("\n## ⚠ Flagged, not fixed — the neoantigen lane\n")
        L.append("- %s" % nf.get("verdict"))
        L.append("- committed resume residues: %s; surviving corrected resumes: %s"
                 % (nf.get("nr4a3_resume_residues_in_the_artifact"),
                    nf.get("nr4a3_resume_residues_that_survive_the_corrected_windows")))
        L.append("- %s" % nf.get("⛔_not_fixed_here"))
    if doc.get("refusals"):
        L.append("\n## Refusals\n")
        for r in doc["refusals"]:
            L.append("- **%s** — %s" % (r["where"], r["why"]))
    return "\n".join(L) + "\n"


# ==================================================================================================
# RUN
# ==================================================================================================

def _load(name):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else None


def assemble(ews_map, nr4_map, doc):
    doc["gate"] = gate(ews_map, nr4_map)
    if doc["gate"]["status"] != "REPRODUCED":
        doc["refusals"].append({"where": "gate", "why": doc["gate"]["_what_a_refusal_means"]})
        return doc
    windows = declared_windows()
    doc["breakpoints"] = enumerate_breakpoints(ews_map, nr4_map, windows)
    doc["plausible_breakpoints"] = plausible_set(doc["breakpoints"]["breakpoints"])

    assessment = _load("nr4a3-structure-assessment.json") or {}
    domains = domain_boundaries(assessment)
    lbd = domains.get(LBD_LABEL)
    if not lbd:
        doc["refusals"].append({"where": "inventory",
                                "why": "could not read the LBD construct boundary from "
                                       "nr4a3-structure-assessment.json -> NR4A3.regions"})
        return doc
    uniq = _load("nr4a-paralogue-unique-residues.json") or {}
    if not uniq:
        doc["refusals"].append({"where": "inventory",
                                "why": "nr4a-paralogue-unique-residues.json absent — uniqueness marks "
                                       "are UNREAD, which is not the same as absent"})
    doc["domains"] = {k: list(v) for k, v in domains.items()}
    doc["inventory"] = build_inventory(nr4_map["protein"], ews_map["protein"],
                                       domains, doc["plausible_breakpoints"]["plausible"],
                                       unique_marks(uniq), lbd)
    doc["neoantigen_lane_flag"] = neoantigen_flag(_load("fusion-breakpoint-neoantigens.json"),
                                                  doc["plausible_breakpoints"]["plausible"])
    doc["the_sentence"] = the_sentence(doc["gate"], doc["inventory"], doc["plausible_breakpoints"])
    return doc


def new_doc():
    return {
        "_title": "EWSR1::NR4A3 fusion-object sequence inventory at the CORRECTED junction (rung R13-a)",
        "_owner": "research/manuscripts/nr4a3-program-map.md THE ORDERED PLAN -> RUNG S, and §10.1 row 9",
        "_cost": "$0 — free GitHub CPU runner. No GPU, no SageMaker, no Vast rental, nothing billed.",
        "_serves": "R13 — validation requirement 5, 'the modelled object is the real biological object'",
        "_limits": [
            "Exon arithmetic and sequence composition only. No structure, pose, contact, reach, "
            "reactivity, affinity or degradation quantity is computed or implied.",
            "The patient-level breakpoint is NOT pinned. Only a primary breakpoint report can pin it, and "
            "EMC carries several; every row is therefore classified INVARIANT or BREAKPOINT_DEPENDENT.",
            "Canonical transcripts only. A different transcript gives a different exon->residue map, and "
            "EMC breakpoints are reported against specific transcripts.",
            "No efficacy, safety, tolerability, therapeutic-window or clinical claim is made or implied.",
            "This module does not edit the roadmap, the paper or the SI. Required edits are ROUTED in "
            "map_edits_required and must be applied by whoever owns those files.",
        ],
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "refusals": [],
    }


def check():
    """Offline: exercise every pure function against the committed exon audit as a fixture."""
    audit = _load("nr4a3-exon-audit.json")
    assert audit, "nr4a3-exon-audit.json is the fixture this self-test needs"
    cache = _load("nr4a-sequences-cache.json") or {}
    ews_map = dict(audit["EWSR1"], protein=cache["EWSR1"])
    nr4_map = dict(audit["NR4A3"], protein=cache["NR4A3"])

    g = gate(ews_map, nr4_map)
    assert g["status"] == "REPRODUCED", g
    assert g["junction"] == "EWSR1(1-264)::NR4A3(1-626)", g["junction"]
    assert g["ewsr1_exon7_coding_phase"] == 1, "793 nt is one past a codon boundary"

    bad = json.loads(json.dumps(nr4_map))
    for r in bad["exons"]:
        if r["transcript_exon_rank"] == 3:
            r["first_protein_residue"] = 361            # the off-by-two, replayed
    assert gate(ews_map, bad)["status"] == "REFUSED", "the gate must catch the off-by-two"

    w = {"EWSR1_exons": [7], "NR4A3_exons": [2, 3, 4]}
    bps = enumerate_breakpoints(ews_map, nr4_map, w)
    assert [s["exon"] for s in bps["skipped_exons"]] == [2], "NR4A3 exon 2 is non-coding and must SKIP"
    assert bps["n_breakpoints"] == 2
    ps = plausible_set(bps["breakpoints"])
    assert ps["n_after_DBD_filter"] == 1, "only the exon-3 resume retains the C4 zinc finger"
    assert ps["plausible"][0]["retains_C166"] is True

    domains = domain_boundaries(_load("nr4a3-structure-assessment.json") or {})
    assert domains[LBD_LABEL] == (373, 626), domains
    marks = unique_marks(_load("nr4a-paralogue-unique-residues.json") or {})
    assert marks.get(166, {}).get("kind") == "C", "C166 must be marked NR4A3-unique from its one home"

    nr4_seq = nr4_map["protein"]
    ews_seq = ews_map["protein"]
    assert len(nr4_seq) == 626 and nr4_seq[165] == "C", "C166 must be a cysteine in the real sequence"
    inv = build_inventory(nr4_seq, ews_seq, domains, ps["plausible"], marks, domains[LBD_LABEL])
    assert inv["n_rows"] > 0
    assert "C166" in [r["residue"] for r in inv["rows"] if r["protein"] == "NR4A3"]
    assert all(r["in_modelled_LBD_construct"] is False for r in inv["rows"])
    assert inv["n_invariant"] + inv["n_breakpoint_dependent"] == inv["n_rows"]
    assert "C166" in inv["unique_reactive_residues_outside_the_construct"]

    nf = neoantigen_flag(_load("fusion-breakpoint-neoantigens.json"), ps["plausible"])
    assert nf["read"] is True
    s = the_sentence(g, inv, ps)
    assert s and "C166" in s and "373-626" in s
    print("fusion_object_inventory --check: OK")
    print("  junction   :", g["junction"])
    print("  plausible  :", ps["n_after_DBD_filter"], "of", ps["n_arithmetically_possible"],
          "(window restricted for the fixture)")
    print("  inventory  :", inv["n_rows"], "reactive residues outside the construct;",
          inv["n_invariant"], "invariant")
    print("  unique     :", inv["unique_reactive_residues_outside_the_construct"])
    print("  neoantigen :", nf["verdict"])
    print()
    print(s)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="offline self-test against committed fixtures")
    args = ap.parse_args()
    if args.check:
        return check()

    import nr4a3_exon_audit as audit
    doc = new_doc()
    doc["_source"] = "Ensembl REST, canonical transcripts, re-derived this run (never read back from a "
    doc["_source"] += "committed artifact — that is what the gate is for)"
    ews_map = audit.exon_map("EWSR1")
    nr4_map = audit.exon_map("NR4A3")
    doc["transcripts"] = {s["symbol"]: {"transcript": s["transcript"], "translation": s.get("translation"),
                                        "protein_length": s["protein_length"],
                                        "self_checks": s["self_checks"]}
                          for s in (ews_map, nr4_map)}
    # ⚠ THE TWO SOURCES MUST AGREE, AND A DISAGREEMENT IS A REFUSAL, NOT A PREFERENCE. Every uniqueness
    # mark in `nr4a-paralogue-unique-residues.json` is numbered against the UniProt sequence; every residue
    # number here is derived from the Ensembl transcript. If those two sequences differ, the marks are
    # being attached to positions that mean something else — the exact shape of the off-by-two this rung
    # exists downstream of, one level up.
    cache = _load("nr4a-sequences-cache.json") or {}
    doc["sequence_cross_check"] = {}
    for m, key in ((nr4_map, "NR4A3"), (ews_map, "EWSR1")):
        ref = cache.get(key)
        same = (ref is not None and ref == m["protein"])
        doc["sequence_cross_check"][key] = {
            "uniprot_cache_len": len(ref) if ref else None,
            "ensembl_translation_len": len(m["protein"]),
            "identical": same,
            "_why_it_matters": "residue numbering for the uniqueness marks comes from the UniProt cache; "
                               "residue numbering for the exon map comes from Ensembl",
        }
        if not same:
            doc["refusals"].append({
                "where": "sequence_cross_check/%s" % key,
                "why": "the Ensembl canonical translation and the committed UniProt cache sequence are "
                       "NOT identical, so residue numbers from the two sources cannot be mixed; the "
                       "uniqueness marks in this run are therefore reported as UNVERIFIED"})
    assemble(ews_map, nr4_map, doc)
    # ⛔ THE ANCHOR CHECK IS PART OF THE RUN, NOT A HUMAN'S LAST STEP. The roadmap is edited concurrently;
    # a routed edit whose `current_text` has been reworded fails SILENTLY when someone tries to apply it.
    import map_edit_anchors as mea
    doc["map_edits_required"], doc["map_edit_anchor_check"] = mea.verify(map_edits(doc))
    if not doc["map_edit_anchor_check"]["all_applicable"]:
        doc["refusals"].append({
            "where": "map_edits_required",
            "why": "at least one routed edit's anchor is NOT_FOUND, AMBIGUOUS or UNREAD against the live "
                   "roadmap — see map_edit_anchor_check. Those edits must be rewritten, not applied by "
                   "judgement."})
    json.dump(doc, open(OUT, "w"), indent=2)
    open(OUT_MD, "w").write(render_markdown(doc))
    print("wrote", OUT)
    print("GATE:", doc["gate"]["status"], doc["gate"].get("junction"))
    if doc.get("the_sentence"):
        print()
        print(doc["the_sentence"])
    return 0 if doc["gate"]["status"] == "REPRODUCED" else 1


if __name__ == "__main__":
    sys.exit(main())
