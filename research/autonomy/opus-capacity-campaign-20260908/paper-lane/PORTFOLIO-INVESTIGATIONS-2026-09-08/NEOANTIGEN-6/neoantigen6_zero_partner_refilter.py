#!/usr/bin/env python3
"""NEOANTIGEN-6 — the EWSR1::NR4A3 junction-neoantigen panel re-emitted with an EXPLICIT,
separately reported zero-partner filter, pre- and post-filter ranks side by side.

WHAT THIS IS. `fusion_breakpoints.py` calls a peptide "novel" when it contains the seam and does
not occur verbatim in either canonical parent. NEOANTIGEN-3 and NEOANTIGEN-4 showed that this
admits peptides that draw NO residue at all from one parent: 8 of the 174 take zero residues from
EWSR1, and 2 of the 11 ranked binders are in that class, including the rank-1 binder DMPCVQAQY,
which is recorded verbatim at residue 11 of NR4A3 isoform Q92570-3. A peptide contributed entirely
by one parent plus the single hybrid seam residue is not junction-specific in any useful sense.
This script applies that discriminator SYMMETRICALLY (zero-EWSR1 and zero-NR4A3 arms), re-emits the
ranked panel, and keeps every pre-filter rank beside its post-filter position so the filter is
auditable and can never be silent.

⛔ WRITTEN BEFORE THE FIRST EXECUTION — what any outcome here does and does not license.
It licenses exactly one kind of statement: a SCREEN-CONFIGURATION statement about which candidates
a junction-neoantigen screen should have ranked as fusion-specific. It licenses NOTHING about
immunogenicity, antigen presentation, tolerance, TCR cross-reactivity, efficacy, safety,
selectivity, therapeutic window or clinical readiness, in EITHER direction. A filtered prediction is
still a prediction. A removed peptide is not thereby shown to be tolerated or unsafe to target; a
retained peptide is not thereby shown to be presented or immunogenic. No count here is evidence
about a patient.

⛔ THE FILTER MAY ONLY EVER REMOVE. It is asserted, not asserted-by-comment: the post-filter panel
must be a SUBSEQUENCE of the pre-filter panel in the pre-filter order, no candidate may appear that
was not already ranked, and no retained candidate's ranking key (in_n_junctions,
presentation_percentile) may be touched. Positive control: DMPCVQAQY MUST be removed.

INPUTS — all committed, read in place, read-only, no network:
  · research/modalities/fusion-breakpoint-neoantigens.json   (the panel: 5 junctions, 174 distinct
    novel peptides, 11 ranked binders, _utc 2026-08-19T16:26:49Z)
  · .../NEOANTIGEN-4/neoantigen4-novelty-audit.json          (independent per-peptide parent split,
    used ONLY as a cross-check against this script's own recomputation)
  · research/modalities/junction-proteome-novelty.json       (the isoform hit for DMPCVQAQY)

HOW THE SPLIT IS RECOMPUTED HERE (not copied from NEOANTIGEN-4). Each junction row carries
`junction_context` = prot[j0-10:j0] + "|" + prot[j0:j0+11], i.e. a 21-residue window with the seam
residue at window index 10. `fusion_breakpoints.junction_peptides` builds every k-mer (k in 8..11)
that starts in [j0-k+1, j0], so every novel peptide lies inside that window and its placement is
recovered by searching it. For a peptide placed at window index s with length L:
    n_from_EWSR1 = max(0, 10 - s)          residues strictly 5' of the seam
    n_seam       = 1                        (the hybrid residue at index 10; all five junctions here
                                             have a seam codon, which is asserted)
    n_from_NR4A3 = max(0, s + L - 1 - 10)  residues strictly 3' of the seam
"""
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
PANEL = os.path.join(REPO, "research/modalities/fusion-breakpoint-neoantigens.json")
NOVELTY = os.path.join(REPO, "research/modalities/junction-proteome-novelty.json")
N4 = os.path.join(os.path.dirname(__file__), "..", "NEOANTIGEN-4",
                  "neoantigen4-novelty-audit.json")
OUT = os.path.join(os.path.dirname(__file__), "refiltered-panel.json")
POSITIVE_CONTROL = "DMPCVQAQY"


def placements(window, pep):
    """Every window index at which `pep` occurs AND covers the seam at index 10."""
    out, i = [], window.find(pep)
    while i != -1:
        if i <= 10 < i + len(pep):
            out.append(i)
        i = window.find(pep, i + 1)
    return out


def main():
    panel = json.load(open(PANEL))
    n4 = json.load(open(N4))
    novelty = json.load(open(NOVELTY))

    junctions = panel["junctions"]
    assert panel["n_inframe_junctions"] == len(junctions) == 5

    # ---- per (junction, peptide) residue split, recomputed here -------------------------------
    rows, per_pep = [], {}
    for jn in junctions:
        label = jn["junction_label"]
        assert jn["seam_codon_residue"], f"{label}: no seam codon; this script assumes one"
        left, right = jn["junction_context"].split("|")
        assert len(left) == 10 and right[0] == jn["seam_codon_residue"]
        window = left + right
        for pep in jn["novel_peptides"]:
            pl = placements(window, pep)
            assert len(pl) == 1, f"{label}/{pep}: {len(pl)} seam-covering placements, need exactly 1"
            s, L = pl[0], len(pep)
            assert 8 <= L <= 11 and 10 - L + 1 <= s <= 10
            row = {"peptide": pep, "junction": label,
                   "n_from_EWSR1": max(0, 10 - s), "n_seam_hybrid": 1,
                   "n_from_NR4A3": max(0, s + L - 1 - 10)}
            assert row["n_from_EWSR1"] + row["n_seam_hybrid"] + row["n_from_NR4A3"] == L
            rows.append(row)
            per_pep.setdefault(pep, []).append(row)

    peptides = sorted(per_pep)
    assert len(peptides) == 174, len(peptides)

    # ---- the discriminator, stated as a rule ---------------------------------------------------
    # A candidate is JUNCTION-SPECIFIC if there is at least one emitting junction at which it draws
    # >= 1 residue from EWSR1 AND >= 1 residue from NR4A3. Retention is the permissive direction, so
    # a peptide is removed only when it is zero-partner at EVERY junction that emits it.
    def verdict(pep):
        specific = [r for r in per_pep[pep] if r["n_from_EWSR1"] >= 1 and r["n_from_NR4A3"] >= 1]
        if specific:
            return "retained", None
        zero_e = all(r["n_from_EWSR1"] == 0 for r in per_pep[pep])
        zero_n = all(r["n_from_NR4A3"] == 0 for r in per_pep[pep])
        if zero_e and zero_n:
            return "removed", "zero_from_both_parents"
        return "removed", "zero_from_EWSR1" if zero_e else "zero_from_NR4A3"

    verdicts = {p: verdict(p) for p in peptides}
    removed = {p: v[1] for p, v in verdicts.items() if v[0] == "removed"}
    zero_e = sorted(p for p, r in removed.items() if r == "zero_from_EWSR1")
    zero_n = sorted(p for p, r in removed.items() if r == "zero_from_NR4A3")

    # ---- cross-check against NEOANTIGEN-4's independent split ----------------------------------
    # NEOANTIGEN-4 emitted ONE row per distinct peptide (174), each labelled with a single
    # emitting junction; this script emits one row per (peptide, junction) pair (190, because the
    # DMPCVQAQ... family is emitted at several junctions). The comparison is therefore made on
    # NEOANTIGEN-4's keys, every one of which must be present here and agree exactly.
    n4_rows = {(r["peptide"], r["junction"]): r
               for r in n4["C_partner_residue_split_all_174"]["all_rows"]}
    mine = {(r["peptide"], r["junction"]): r for r in rows}
    assert len(n4_rows) == 174 and set(n4_rows) <= set(mine), "NEOANTIGEN-4 rows not reproduced here"
    disagreements = [k for k in n4_rows
                     if (mine[k]["n_from_EWSR1"], mine[k]["n_seam_hybrid"], mine[k]["n_from_NR4A3"])
                     != (n4_rows[k]["n_from_EWSR1"], n4_rows[k]["n_seam_hybrid"],
                         n4_rows[k]["n_from_NR4A3"])]
    assert not disagreements, disagreements[:5]
    n4_zero_e = sorted(r["peptide"] for r in
                       n4["C_partner_residue_split_all_174"]["zero_EWSR1_peptides"])
    assert sorted(set(n4_zero_e)) == zero_e, (n4_zero_e, zero_e)

    # ---- re-emit the ranked panel ---------------------------------------------------------------
    pre = panel["predicted_binders_ranked"]
    assert len(pre) == panel["n_distinct_binders"] == 11
    assert set(b["peptide"] for b in pre) <= set(peptides)
    key = lambda b: (-b["in_n_junctions"], b["presentation_percentile"])
    assert [key(b) for b in pre] == sorted(key(b) for b in pre), "input panel is not in rank order"

    # A ranked binder emitted at several junctions must have the SAME split at each of them, or
    # the single split reported beside its rank below would be ambiguous. Asserted, not assumed.
    for b in pre:
        splits = {(r["n_from_EWSR1"], r["n_seam_hybrid"], r["n_from_NR4A3"])
                  for r in per_pep[b["peptide"]]}
        assert len(splits) == 1, (b["peptide"], splits)

    table, post_pos = [], 0
    for i, b in enumerate(pre, start=1):
        pep = b["peptide"]
        v, reason = verdicts[pep]
        entry = {"peptide": pep, "pre_filter_rank": i, "allele": b["allele"],
                 "affinity_nM": b["affinity_nM"],
                 "presentation_percentile": b["presentation_percentile"],
                 "class": b["class"], "in_n_junctions": b["in_n_junctions"],
                 "n_from_EWSR1": per_pep[pep][0]["n_from_EWSR1"],
                 "n_seam_hybrid": per_pep[pep][0]["n_seam_hybrid"],
                 "n_from_NR4A3": per_pep[pep][0]["n_from_NR4A3"],
                 "filter_verdict": v, "removal_reason": reason,
                 "post_filter_rank": None}
        if v == "retained":
            post_pos += 1
            entry["post_filter_rank"] = post_pos
        table.append(entry)

    post = [e for e in table if e["filter_verdict"] == "retained"]

    # ---- the filter may only ever remove: asserted ---------------------------------------------
    checks = {}
    checks["no_candidate_added"] = ([e["peptide"] for e in post]
                                    == [e["peptide"] for e in table if e["filter_verdict"] == "retained"])
    pre_order = [b["peptide"] for b in pre]
    checks["post_panel_is_a_subsequence_of_the_pre_panel"] = (
        [p for p in pre_order if p in {e["peptide"] for e in post}] == [e["peptide"] for e in post])
    checks["post_panel_is_a_subset_of_the_pre_panel"] = (
        set(e["peptide"] for e in post) <= set(pre_order))
    checks["pre_filter_ranks_strictly_increase_with_post_filter_rank"] = all(
        post[i]["pre_filter_rank"] < post[i + 1]["pre_filter_rank"] for i in range(len(post) - 1))
    checks["no_retained_candidate_moved_ahead_of_a_retained_candidate_it_was_behind"] = all(
        e["post_filter_rank"] <= e["pre_filter_rank"] for e in post)
    by_pep = {b["peptide"]: b for b in pre}
    checks["ranking_key_untouched_for_every_retained_candidate"] = all(
        (e["in_n_junctions"], e["presentation_percentile"])
        == (by_pep[e["peptide"]]["in_n_junctions"], by_pep[e["peptide"]]["presentation_percentile"])
        for e in post)
    checks["n_removed_plus_n_retained_equals_11"] = len(post) + sum(
        1 for e in table if e["filter_verdict"] == "removed") == 11

    # positive control
    pc = next((e for e in table if e["peptide"] == POSITIVE_CONTROL), None)
    control = {
        "peptide": POSITIVE_CONTROL,
        "why": "carries zero EWSR1 residues (NEOANTIGEN-3) and is recorded verbatim at residue 11 "
               "of NR4A3 isoform Q92570-3 in junction-proteome-novelty.json",
        "was_rank_1_pre_filter": bool(pc and pc["pre_filter_rank"] == 1),
        "must_be_removed": True,
        "was_removed": bool(pc and pc["filter_verdict"] == "removed"),
        "removal_reason": pc["removal_reason"] if pc else None,
        "recorded_isoform_hit": [h for h in novelty.get("peptides_found_in_proteome", [])
                                 if h.get("peptide") == POSITIVE_CONTROL],
    }
    control["pass"] = control["was_removed"]
    checks["positive_control_DMPCVQAQY_removed"] = control["pass"]

    result = {
        "_what": "EWSR1::NR4A3 junction-neoantigen panel re-emitted under an explicit, separately "
                 "reported zero-partner filter, with pre- and post-filter ranks side by side.",
        "⛔_what_this_is_not": "Not an immunogenicity, presentation, tolerance, efficacy, safety, "
                              "selectivity, therapeutic-window or clinical-readiness claim. A "
                              "filtered prediction is still a prediction. This is a screen "
                              "configuration result and nothing more.",
        "_lane": "NEOANTIGEN-6",
        "_cost": {"network": "none", "gpu": "none", "paid_api": "none", "usd": 0},
        "_inputs": {
            "fusion-breakpoint-neoantigens.json": {"_utc": panel["_utc"],
                                                   "n_inframe_junctions": panel["n_inframe_junctions"],
                                                   "n_distinct_binders": panel["n_distinct_binders"],
                                                   "rank_column": panel.get("_rank_column_used")},
            "neoantigen4-novelty-audit.json": {"used_for": "independent cross-check of the split only"},
            "junction-proteome-novelty.json": {"used_for": "the recorded Q92570-3 hit for the control"},
        },
        "_filter_rule": {
            "statement": "A junction candidate is retained only if it draws at least one residue "
                         "from EWSR1 AND at least one residue from NR4A3 at some junction that "
                         "emits it. The hybrid seam residue counts for neither parent.",
            "direction": "REMOVE-ONLY. It cannot add a candidate and cannot re-rank one upward "
                         "relative to another retained candidate; both are asserted below.",
            "reported": "Never silent: every removed candidate is listed with its pre-filter rank "
                        "and reason, and every retained candidate keeps its pre-filter rank.",
        },
        "_denominators": {"junction_peptides": len(peptides), "ranked_binders": len(pre)},
        "peptide_arm": {
            "n_tested": len(peptides),
            "n_removed": len(removed),
            "n_retained": len(peptides) - len(removed),
            "n_zero_from_EWSR1": len(zero_e),
            "n_zero_from_NR4A3": len(zero_n),
            "zero_from_EWSR1": zero_e,
            "zero_from_NR4A3": zero_n,
            "note": "NEOANTIGEN-4 reported the zero-EWSR1 arm (8/174). The zero-NR4A3 arm is the "
                    "symmetric class — a peptide ending AT the seam, all of whose non-seam residues "
                    "are EWSR1's — and is reported here for the first time.",
        },
        "ranked_binder_arm": {
            "n_pre_filter": len(pre),
            "n_post_filter": len(post),
            "n_removed": len(pre) - len(post),
            "panel_side_by_side": table,
            "post_filter_panel": [{"post_filter_rank": e["post_filter_rank"],
                                   "pre_filter_rank": e["pre_filter_rank"],
                                   "peptide": e["peptide"], "allele": e["allele"],
                                   "affinity_nM": e["affinity_nM"],
                                   "presentation_percentile": e["presentation_percentile"],
                                   "class": e["class"], "in_n_junctions": e["in_n_junctions"]}
                                  for e in post],
        },
        "controls": {"positive_control": control},
        "monotonicity_assertions": checks,
        "per_junction_peptide_split": rows,
        "cross_check_against_NEOANTIGEN_4": {
            "n_rows_here": len(rows), "n_rows_compared": len(n4_rows),
            "disagreements": disagreements,
            "zero_EWSR1_sets_identical": True,
        },
        "⛔_limitations": [
            "The panel's binding predictions are MHCflurry screen output and were NOT recomputed "
            "here; MHCflurry is not importable in this checkout and the ranking keys are read "
            "verbatim from the committed artifact.",
            "The filter is a sequence-composition rule about the screen's own peptide construction. "
            "It says nothing about whether a retained peptide is presented or immunogenic.",
            "Removal for zero-partner composition is INDEPENDENT of proteome novelty: the two "
            "coincide on DMPCVQAQY but the filter does not test wild-type occurrence.",
            "No isoform sequence is present in this checkout; where an isoform sequence would be "
            "needed it is UNKNOWN here and is not assumed.",
        ],
    }
    if not all(checks.values()):
        json.dump(result, open(OUT, "w"), indent=2, ensure_ascii=False)
        print("FAILED assertions:", [k for k, v in checks.items() if not v], file=sys.stderr)
        return 1
    json.dump(result, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in result.items()
                      if k in ("peptide_arm", "ranked_binder_arm", "controls",
                               "monotonicity_assertions")},
                     indent=2, ensure_ascii=False)[:4000])
    print("wrote", OUT, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
