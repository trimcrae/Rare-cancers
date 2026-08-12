#!/usr/bin/env python3
"""
The pan-partner NR4A3 fusion-junction atlas — every partner, every frame-compatible seam, one table.

WHY THIS EXISTS. Until 2026-08-12 this repository's ASO lane could design against exactly one
partner. `junction_aso.py` hard-coded `EWSR1`, so the committed design panel covered EWSR1::NR4A3
and nothing else, while EMC is defined by NR4A3 rearrangement to a VARIABLE partner — EWSR1 in the
large majority, TAF15 in a substantial minority, and TCF12/TFG/FUS rarely. Two things make that
exclusion worse than a scope note:

  (a) ⭐ TAF15 IS THE SUBGROUP WITH THE WORST OPTIONS, NOT AN AFTERTHOUGHT. Every reported objective
      response to an antiangiogenic TKI in advanced EMC — the only systemic class with activity in
      this disease — has occurred in a non-TAF15 patient; the TAF15 arm is 0 events across 3 to 5
      patients. That pooled contrast, its zero-event caveat and the primary authors' own hedge that
      the fusion is a surrogate rather than a mechanism, are owned by
      `research/manuscripts/emc-fusion-partner-pooling.json` and are NOT restated here (rule 1).
      What follows from it for THIS module is only this: the partner-defined subgroup with the
      fewest options was the one a hard-coded gene symbol excluded from the design lane.
  (b) The FET-family donors are PARALOGUES. EWSR1, TAF15 and FUS share genuinely similar
      low-complexity N-termini, so a design against one partner's seam can be a perfect complement
      of another partner's wild-type transcript — a specificity failure invisible to a screen that
      only ever knew about two genes. `junction_aso.design(parents=...)` now takes the whole set.

WHAT THIS PRODUCES (all $0, CPU-only, offline from the committed Ensembl cache):
  1. A grade for EVERY donor-exon x NR4A3-acceptor-exon pair across every partner whose transcript
     model this repository holds — including the refusals, each saying why.
  2. Junction-spanning gapmer panels for the rows graded EMITTABLE, cross-screened against ALL
     partner transcripts rather than the two parents of their own fusion.
  3. The cross-junction coverage question nobody had asked: can one oligo serve more than one
     junction, or does every seam need its own?

⛔ WHAT THIS IS NOT. This enumerates what is FRAME-COMPATIBLE, which is an arithmetic property of
exon structure. It is NOT a claim about which junctions patients carry: breakpoint recurrence is a
clinical observation, this repository holds no partner-and-exon-resolved patient series, and which
exon pair a given patient carries is not decidable from exon structure. Every clinical design must
still be re-derived from that patient's own sequenced fusion transcript. Nothing here addresses
potency, knockdown, delivery, tolerability, safety or clinical use.

Output: nr4a3-fusion-junction-atlas.json
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import junction_aso as ja  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "nr4a3-fusion-junction-atlas.json")

#: The acceptor. In EMC this never varies — the disease is defined by NR4A3 rearrangement.
ACCEPTOR = "NR4A3"

#: 5' partners this repository holds a self-checked transcript model for. TFG is a reported EMC
#: partner and is DELIBERATELY ABSENT rather than quietly dropped: `emc-construct-inputs.json`
#: carries no TFG record, so no seam can be built for it here. It is reported as an unscoreable
#: partner in the artifact's `partners_not_scoreable` block, because a partner nobody could read
#: and a partner with no junctions must never render alike (CLAUDE.md §4).
PARTNERS = ["EWSR1", "TAF15", "TCF12", "FUS"]
PARTNERS_EXPECTED_BUT_ABSENT = {
    "TFG": "no transcript model in emc-construct-inputs.json — cannot be built offline; a "
           "targeted Ensembl fetch would add it and no other input is missing",
}


def _acceptor_window():
    """The declared NR4A3 acceptor exons. ONE HOME: read from `fusion_breakpoints`, never typed."""
    import fusion_breakpoints as fb
    return list(fb.NR4A3_EXON_WINDOW)


def _donor_window(symbol):
    """The declared candidate donor cuts for `symbol`, or None if this repository declares none.

    Only EWSR1 has one (`fusion_breakpoints.EWSR1_EXON_WINDOW`). Returning None rather than an
    empty list is load-bearing: an empty list would grade every TAF15 row `outside the window`,
    manufacturing a negative out of a curation gap.
    """
    import fusion_breakpoints as fb
    return list(fb.EWSR1_EXON_WINDOW) if symbol == "EWSR1" else None


def _mismatches(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def gap_bounds(oligo_len=None, wing=None):
    """The catalytic-gap slice [lo, hi) inside an oligo of this geometry, in oligo coordinates."""
    oligo_len = oligo_len or ja.OLIGO_LEN
    wing = wing or ja.WING
    return wing, oligo_len - wing


def cross_junction_coverage(target, own_label, fusions, seam_index):
    """Which OTHER junctions' chimeric mRNAs this one oligo's target window could also engage.

    Two questions, kept separate because they answer differently and a merged count would hide it:
      `exact_also_in`   — the window occurs verbatim in that junction's fusion mRNA. One oligo,
                          two junctions, full cleavage competence.
      `gap_intact_also_in` — the window occurs with mismatches ONLY in the wings and NONE inside the
                          catalytic gap. RNase-H1 cleaves across the gap, so a gap-intact near-match
                          is the case where cross-junction activity is plausible rather than certain.

    ⛔ AND EVERY MATCH IS CHECKED AGAINST THE OTHER JUNCTION'S OWN SEAM, WHICH IS THE WHOLE
    DIFFERENCE BETWEEN A RESULT AND A COINCIDENCE. A 16-mer occurring somewhere inside a 4-kb
    chimeric mRNA says nothing: it could be a chance match in the middle of the shared NR4A3 body,
    which every one of these fusions contains, and which is not cross-JUNCTION coverage at all — it
    is the same oligo finding the same acceptor twice. The claim is only interesting if the match
    STRADDLES that junction's seam too, i.e. the oligo is junction-spanning at BOTH seams and
    therefore fusion-exclusive at both. So `spans_seam` is recorded per match and a match that does
    not span is reported separately as `body_match_not_junction_spanning` rather than counted.

    ⚠ `gap_intact_also_in` is a SEQUENCE reading under the same gap-mismatch heuristic the paper
    reports as retired-for-clean-calls (§3a-quater): it ranks, it does not certify. It is used here
    to ask a yes/no architectural question — could one oligo serve two seams — not to assert potency.
    """
    lo, hi = gap_bounds()
    n = len(target)
    exact, gap_intact, body_only = [], [], []

    def _spans(start, label):
        """Does a match beginning at `start` straddle THAT junction's seam?"""
        return start < seam_index[label] < start + n

    for label, fusion in fusions.items():
        if label == own_label:
            continue
        starts = []
        s = fusion.find(target)
        while s != -1:
            starts.append(s)
            s = fusion.find(target, s + 1)
        if starts:
            if any(_spans(s, label) for s in starts):
                exact.append(label)
            else:
                body_only.append(label)
            continue
        for s in range(len(fusion) - n + 1):
            win = fusion[s:s + n]
            if _mismatches(win[lo:hi], target[lo:hi]) == 0 and _mismatches(win, target) <= 2:
                (gap_intact if _spans(s, label) else body_only).append(label)
                break
    return sorted(exact), sorted(gap_intact), sorted(set(body_only))


def build():
    acceptor = ja.transcript_model(ACCEPTOR)
    lo_res, hi_res = ja.plausible_nr4a3_resume_residues()
    acc_window = _acceptor_window()

    models, unreadable = {}, {}
    for sym in PARTNERS:
        try:
            models[sym] = ja.transcript_model(sym)
        except Exception as exc:                                        # noqa: BLE001
            unreadable[sym] = str(exc)

    # ── 1. grade every pair, refusals included ────────────────────────────────────────────────
    rows, emittable = [], []
    for sym, donor in models.items():
        for d_end in range(1, donor["n_transcript_exons"] + 1):
            for a_start in acc_window:
                try:
                    j = ja.mrna_junction_generic(donor, acceptor, d_end, a_start)
                except Exception as exc:                                # noqa: BLE001
                    rows.append({"junction_label": f"{sym}_e{d_end}__{ACCEPTOR}_e{a_start}",
                                 "donor_symbol": sym, "donor_exon_end": d_end,
                                 "acceptor_exon_start": a_start,
                                 "grade": "UNREADABLE", "why": str(exc)})
                    continue
                grade, why = ja.grade_junction(j, lo_res, hi_res)
                keep = {k: v for k, v in j.items() if not k.startswith("_")}
                keep["grade"], keep["why"] = grade, why
                # ⚠ FRAME-COMPATIBLE IS NOT CLINICALLY REPORTED, AND THE TABLE MUST SAY WHICH IT IS.
                # `fusion_breakpoints.EWSR1_EXON_WINDOW` is this repository's declared window of
                # candidate EWSR1 cuts; rows outside it (EWSR1 exon 1, 4, 15) are arithmetic, not
                # clinical. ⛔ NO SUCH WINDOW EXISTS FOR ANY OTHER PARTNER — nobody has curated one
                # here — so their flag is null rather than false. A null and a false must not render
                # alike: false says "outside the declared window", null says "there is no window to
                # be outside of", and only the second is an absent reading.
                keep["within_declared_donor_window"] = (
                    d_end in _donor_window(sym) if _donor_window(sym) is not None else None)
                rows.append(keep)
                if grade == ja.EMITTABLE:
                    emittable.append((sym, d_end, a_start, j))

    # ── 2. design on the emittable rows, screened against EVERY partner transcript ────────────
    # The parent set is the whole partner panel plus the acceptor — strictly stricter than the
    # two-parent test, and the reason is (b) in the module docstring.
    parents = {sym: m["cdna"] for sym, m in models.items()}
    parents[ACCEPTOR] = acceptor["cdna"]

    fusions = {j["junction_label"]: j["_fusion"] for _, _, _, j in emittable}
    #: seam position in each chimeric mRNA — the index of the first acceptor base.
    seam_index = {j["junction_label"]: len(j["_left"]) for _, _, _, j in emittable}
    panels = []
    for sym, d_end, a_start, j in emittable:
        oligos = ja.design(j["_left"], j["_right"], j["_fusion"], parents=parents)
        specific = [o for o in oligos if o["fusion_specific"]]
        for o in specific:
            ex, gi, body = cross_junction_coverage(
                o["target_mRNA_5to3"], j["junction_label"], fusions, seam_index)
            o["also_exact_in_junctions"] = ex
            o["also_gap_intact_in_junctions"] = gi
            o["body_match_not_junction_spanning"] = body
        panels.append({
            "junction_label": j["junction_label"],
            "donor_symbol": sym, "donor_exon_end": d_end, "acceptor_exon_start": a_start,
            "seam_mRNA": j["junction_context_mRNA"],
            "nr4a3_first_residue": j["nr4a3_first_residue"],
            "chimeric_protein_length": j["chimeric_protein_length"],
            "n_tiled": len(oligos),
            "n_fusion_specific": len(specific),
            # ⚠ A design refused for hitting a parent names WHICH parent. A bare count would make a
            # paralogue collision (the thing this module widened the screen to catch) invisible.
            "exact_parent_hits_seen": sorted({p for o in oligos for p in o["exact_parent_hits"]}),
            "gc_range_fusion_specific": (
                [min(o["gc_percent"] for o in specific), max(o["gc_percent"] for o in specific)]
                if specific else None),
            "best_gap_specificity_margin": (
                max(o["gap_specificity_margin"] for o in specific) if specific else None),
            "designs": specific,
        })

    # ── 3. the isoform-coverage question ─────────────────────────────────────────────────────
    def _partners_of(labels):
        return sorted({lab.split("_e")[0] for lab in labels})

    shared_exact, shared_gap = {}, {}
    for p in panels:
        for o in p["designs"]:
            if o["also_exact_in_junctions"]:
                covered = [p["junction_label"]] + o["also_exact_in_junctions"]
                shared_exact.setdefault(o["antisense_5to3"], {
                    "designed_for": p["junction_label"],
                    "also_covers": o["also_exact_in_junctions"],
                    "partners_covered": _partners_of(covered),
                    "n_junctions_covered": len(covered),
                    "gc_percent": o["gc_percent"],
                    "gap_specificity_margin": o["gap_specificity_margin"]})
            if o["also_gap_intact_in_junctions"]:
                shared_gap.setdefault(o["antisense_5to3"], {
                    "designed_for": p["junction_label"],
                    "also_plausible_at": o["also_gap_intact_in_junctions"],
                    "partners_covered": _partners_of(
                        [p["junction_label"]] + o["also_gap_intact_in_junctions"])})

    multi_partner = {seq: v for seq, v in shared_exact.items() if len(v["partners_covered"]) > 1}

    # ⭐ NAME THE MECHANISM, DO NOT LEAVE IT TO BE INFERRED (CLAUDE.md §4 — produce the evidence
    # that proves the mechanism, never a plausible story). A design covering two partners is only
    # interesting if one can say WHY, and the why is checkable in one line: the donors' bases
    # immediately 5' of the breakpoint are IDENTICAL over the stretch the oligo uses. So for each
    # multi-partner design, record the shared donor run and the per-junction seam split. If the
    # shared run were shorter than the oligo's donor-side contribution the coverage claim would be
    # arithmetically impossible, which makes this a self-check and not decoration.
    for seq, v in multi_partner.items():
        labels = [v["designed_for"]] + v["also_covers"]
        target = ja.revcomp(seq)
        splits, donor_sides = {}, set()
        for lab in labels:
            fusion, seam = fusions[lab], seam_index[lab]
            s = fusion.find(target)
            while s != -1 and not (s < seam < s + len(target)):
                s = fusion.find(target, s + 1)
            splits[lab] = {"donor_bases": seam - s, "acceptor_bases": s + len(target) - seam}
            donor_sides.add(fusion[s:seam])
        v["seam_split_per_junction"] = splits
        v["shared_donor_run"] = sorted(donor_sides)[0] if len(donor_sides) == 1 else None
        v["_mechanism"] = (
            "the donor transcripts are IDENTICAL over the "
            f"{len(sorted(donor_sides)[0])} bases immediately 5' of their breakpoints"
            if len(donor_sides) == 1 else
            "donor-side sequence differs between these junctions — coverage is not explained by a "
            "shared donor run and this row needs a look before it is quoted")
        # The acceptor side is shared by construction (one acceptor exon), so it explains nothing.
        v["_acceptor_side_is_not_evidence"] = (
            "All these junctions use the same NR4A3 acceptor exon, so their acceptor-side bases "
            "agree trivially. The load-bearing half is the donor run above.")

    by_partner = {}
    for sym in PARTNERS:
        pans = [p for p in panels if p["donor_symbol"] == sym]
        graded = [r for r in rows if r.get("donor_symbol") == sym]
        by_partner[sym] = {
            "in_model_set": sym in models,
            "n_pairs_graded": len(graded),
            "grade_counts": {g: sum(1 for r in graded if r.get("grade") == g)
                             for g in sorted({r.get("grade") for r in graded})},
            "n_emittable_junctions": len(pans),
            "n_junctions_with_a_fusion_specific_design": sum(1 for p in pans
                                                             if p["n_fusion_specific"]),
            "gc_range_across_designs": (
                [min(p["gc_range_fusion_specific"][0] for p in pans if p["gc_range_fusion_specific"]),
                 max(p["gc_range_fusion_specific"][1] for p in pans if p["gc_range_fusion_specific"])]
                if any(p["gc_range_fusion_specific"] for p in pans) else None),
            "provenance_gate": ja.PROVENANCE_GATE_USED.get(sym),
        }

    result = {
        "_title": "Pan-partner NR4A3 fusion-junction atlas — every frame-compatible seam, graded, "
                  "with junction-spanning gapmer panels and cross-junction coverage",
        "_generated_by": "research/modalities/nr4a3_fusion_atlas.py",
        "_cost": "$0 — CPU only, no GPU, no rental, no network when the committed transcript cache "
                 "answers. Sequence arithmetic over committed Ensembl transcript models.",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_what_this_is_not": [
            "NOT a claim about which junctions patients carry. This enumerates what is "
            "FRAME-COMPATIBLE — an arithmetic property of exon structure. Breakpoint recurrence is "
            "a clinical observation and no partner-and-exon-resolved patient series is held here.",
            "NOT a potency, knockdown, delivery, tolerability, safety or clinical-readiness claim, "
            "and no such quantity is computed anywhere in this file.",
            "NOT a specificity certification. `fusion_specific` is an EXACT-complement test against "
            "the partner transcripts; the transcriptome-wide near-match screen is a separate, "
            "network-bound analysis (junction_aso_offtarget.py) and is not run here.",
            "NOT a statement that a partner absent from `partners_not_scoreable` has no junctions — "
            "an absent transcript model is an absent reading, never a reading of absence.",
        ],
        "_provenance_gate_note": (
            "`nr4a3-exon-audit.json` grades NR4A3 and EWSR1 only — the two genes the 2026-08-06 "
            "off-by-two correction was derived against. For TAF15, TCF12 and FUS that gate CANNOT "
            "RUN, and the weaker one that can (emc-construct-inputs.json's four recorded "
            "self-checks plus three sequence self-checks) is what stands behind their seams. Which "
            "gate ran is recorded per gene below and must be read with every partner result."),
        "_transcript_source": ja.transcript_source_provenance(),
        "provenance_gate_per_gene": dict(ja.PROVENANCE_GATE_USED),
        "acceptor": ACCEPTOR,
        "acceptor_exon_window": acc_window,
        "_acceptor_window_source": "fusion_breakpoints.NR4A3_EXON_WINDOW",
        "plausible_nr4a3_resume_range": [lo_res, hi_res],
        "oligo_geometry": {"length": ja.OLIGO_LEN, "wing": ja.WING, "gap": ja.GAP,
                           "architecture": f"{ja.WING}-{ja.GAP}-{ja.WING} (LNA-DNA-LNA)"},
        "partners_scored": sorted(models),
        "partners_not_scoreable": {**PARTNERS_EXPECTED_BUT_ABSENT, **unreadable},
        "transcripts": {s: {"transcript": m["transcript"], "cdna_nt": len(m["cdna"]),
                            "cds_nt": len(m["cds"]), "utr5_nt": m["utr5_len"],
                            "n_transcript_exons": m["n_transcript_exons"]}
                        for s, m in list(models.items()) + [(ACCEPTOR, acceptor)]},
        "n_pairs_graded": len(rows),
        "grade_counts": {g: sum(1 for r in rows if r.get("grade") == g)
                         for g in sorted({r.get("grade") for r in rows})},
        "n_emittable_junctions": len(panels),
        "n_junctions_with_a_fusion_specific_design": sum(1 for p in panels
                                                         if p["n_fusion_specific"]),
        "declared_donor_window": {
            "EWSR1": list(_donor_window("EWSR1")),
            "_source": "fusion_breakpoints.EWSR1_EXON_WINDOW",
            "_others": "No declared donor window exists in this repository for TAF15, TCF12, FUS "
                       "or TFG. Their rows carry `within_declared_donor_window: null` — a curation "
                       "gap, not a negative finding, and naming it is the point.",
            "n_emittable_inside_the_EWSR1_window": sum(
                1 for r in rows if r.get("grade") == ja.EMITTABLE
                and r.get("within_declared_donor_window") is True),
            "n_emittable_outside_the_EWSR1_window": sum(
                1 for r in rows if r.get("grade") == ja.EMITTABLE
                and r.get("within_declared_donor_window") is False),
        },
        "by_partner": by_partner,
        "isoform_coverage": {
            "_question": "Can one oligo serve more than one junction, or does every seam need its "
                         "own? This is the difference between a per-patient panel and a stock "
                         "reagent, and it had never been computed.",
            "_what_counts": (
                "A match counts ONLY if it straddles the OTHER junction's own seam. A 16-mer that "
                "merely occurs somewhere inside another chimera is finding the shared NR4A3 body, "
                "which every one of these fusions contains — that is the same acceptor twice, not "
                "cross-junction coverage, and it is reported separately as "
                "`body_match_not_junction_spanning` on each design."),
            "n_designs_covering_a_second_junction_exactly": len(shared_exact),
            "n_designs_with_a_gap_intact_match_at_a_second_junction": len(shared_gap),
            "n_designs_covering_MORE_THAN_ONE_PARTNER_exactly": len(multi_partner),
            "_why_multi_partner_is_the_interesting_number": (
                "Two junctions of the SAME partner sharing an oligo is a within-gene observation. "
                "Two junctions of DIFFERENT partners sharing one is a statement about FET-family "
                "paralogy: the donors' low-complexity sequence immediately 5' of the breakpoint is "
                "similar enough that one junction-spanning oligo can be exclusive at both seams. "
                "That same paralogy is why `design(parents=...)` had to be widened to screen every "
                "partner — the identical sequence property is a specificity liability and a "
                "coverage asset at once, and a reader must be able to see both from this file."),
            "exact": shared_exact,
            "multi_partner_exact": multi_partner,
            "gap_intact": shared_gap,
        },
        "graded_pairs": rows,
        "panels": panels,
    }
    return result


def main():
    res = build()
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    skip = {"graded_pairs", "panels"}
    print(json.dumps({k: v for k, v in res.items() if k not in skip}, indent=2))
    for p in res["panels"]:
        print(f"  {p['junction_label']:<22} specific={p['n_fusion_specific']:<3} "
              f"GC={p['gc_range_fusion_specific']} seam={p['seam_mRNA']}")


if __name__ == "__main__":
    main()
