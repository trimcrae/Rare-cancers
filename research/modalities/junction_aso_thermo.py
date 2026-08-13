#!/usr/bin/env python3
"""Nearest-neighbour duplex thermodynamics for the junction gapmers, and the design-rule audit.

⛔ WHY THIS EXISTS. The manuscript's central open question is DISCRIMINATION: whether an
oligonucleotide complementary to a fusion seam engages the fusion transcript in preference to the two
parent transcripts that supply its own two halves. Until now the paper answered that with a
gap-level MARGIN — a count of junction-unique bases inside the six-nucleotide catalytic gap — bounded
by two literature measurements of RNase-H1 single-mismatch discrimination. A count is a proxy. The
standard instrument for the same question is a free-energy calculation, it needs no wet lab and no
GPU, and a reviewer of an oligonucleotide-design paper will ask why it was not done. This module does
it.

★ WHAT IS ACTUALLY COMPUTED, AND WHY IT IS A FAIR COMPARISON. A junction gapmer is a perfect
complement of the fusion across all 16 positions. Against a PARENT transcript it can only pair the
half of itself that parent contributes, because the other half is sequence the parent does not carry.
So the honest comparison is:

    ΔG(oligo : fusion)        — the full 16-mer Watson-Crick duplex
    ΔG(oligo : donor parent)  — the donor-side run only
    ΔG(oligo : acceptor)      — the acceptor-side run only

and the discrimination is ΔΔG = ΔG(best parent) − ΔG(fusion), positive when the fusion duplex is the
more stable one. ⚠ This is a THERMODYNAMIC statement about duplex formation and NOT a prediction of
RNase-H1 cleavage: the enzyme requires a paired DNA gap, which is a geometric requirement the free
energy does not encode. The two instruments answer adjacent questions, which is exactly why their
agreement or disagreement is informative.

⛔ THE PARAMETERS ARE READ FROM A PACKAGE THAT CITES ITS SOURCE, NEVER TYPED. Sixteen nearest-
neighbour pairs for a DNA:RNA hybrid, from Sugimoto et al. (1995) Biochemistry 34:11211-11216
(PMID 7545436), reached through Biopython's `MeltingTemp.R_DNA_NN1`, whose own source comment names
that paper. This repository's first golden rule is never to fabricate a citation, and a thermodynamic
table recited from memory is precisely that failure in numeric form — gate 4 exists because an agent
once wrote a PMID from recollection. The package version is recorded in the artifact so a reader can
reproduce the exact table.

⛔⛔ AND THE KEYING CONVENTION IS VALIDATED, NOT ASSUMED. A nearest-neighbour table is a dictionary of
"XY/WZ" keys, and getting the strand convention backwards produces numbers that are wrong and look
entirely plausible — the failure mode this repository keeps paying for. So `_validate_against_biopython`
recomputes Tm from this module's own ΔH and ΔS and checks it against Biopython's independent
`Tm_NN` over the real design set. If the convention were wrong the two would diverge; agreement to
0.01 °C is what licenses every number below.

⚠ LNA IS NOT MODELLED, AND THAT IS A REAL LIMIT. These designs are 5-6-5 LNA/DNA/LNA. Sugimoto's
table is for an unmodified DNA:RNA hybrid, so what is computed here is the duplex the DNA backbone
would form. LNA wings raise affinity substantially. The effect is applied to BOTH the fusion duplex
and the parent duplex, so it is not neutral — it compresses ΔΔG, meaning the discrimination reported
here is an UPPER bound on the modified oligonucleotide's, not an estimate of it. Stated in the
artifact and in the manuscript rather than buried.

    python3 research/modalities/junction_aso_thermo.py            # write the artifact
    python3 research/modalities/junction_aso_thermo.py --check    # exit 1 if it would change
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS = os.path.join(HERE, "nr4a3-fusion-junction-atlas.json")
OUT = os.path.join(HERE, "junction-aso-thermo.json")

R = 1.987          # cal / (mol K)
T37 = 310.15       # K
CONC_NM = 250.0    # oligonucleotide strand concentration assumed for Tm, nM

#: Design rules quoted from the antisense-oligonucleotide design literature, each with the property
#: it tests and the direction that is unfavourable. ⛔ THESE ARE CONVENTIONS, NOT LAWS, and the point
#: of the audit is NOT to grade the designs against them — it is to ask whether the paper's gap-level
#: margin ranking and conventional triage would pick the same molecules. A design that fails a
#: convention is not thereby bad; a ranking that inverts under conventional rules is a finding.
DESIGN_RULES = {
    "gc_in_band": {
        "what": "GC content within the conventional 40-60% gapmer window",
        "why": "the band most gapmer design guidance uses; outside it, affinity or specificity "
               "is usually the reason",
    },
    "no_g_quadruplex_motif": {
        "what": "no G-quadruplex motif (four runs of >=2 G)",
        "why": "G-quadruplex-forming oligonucleotides aggregate and show sequence-independent "
               "protein binding",
    },
    "no_run_of_four": {
        "what": "no homopolymer run of four or more identical bases",
        "why": "long runs, G-runs especially, are a standard exclusion in oligonucleotide design",
    },
    "no_cpg": {
        "what": "no CpG dinucleotide",
        "why": "unmethylated CpG is the canonical TLR9 immunostimulatory motif and is routinely "
               "avoided in therapeutic oligonucleotides",
    },
}


def _nn_table():
    """The DNA:RNA hybrid nearest-neighbour table, with its provenance, or a refusal.

    ⛔ NO FALLBACK TABLE. If Biopython is absent this returns None and the module writes nothing.
    A hand-entered approximation would produce an artifact indistinguishable from a real one.
    """
    try:
        import Bio
        from Bio.SeqUtils import MeltingTemp as mt
    except Exception:  # noqa: BLE001
        return None, None
    return mt.R_DNA_NN1, {
        "table": "Bio.SeqUtils.MeltingTemp.R_DNA_NN1",
        "biopython_version": Bio.__version__,
        "primary_source": "Sugimoto N, Nakano S, Katoh M, Matsumura A, Nakamuta H, Ohmichi T, "
                          "Yoneyama M, Sasaki M. Thermodynamic parameters to predict stability of "
                          "RNA/DNA hybrid duplexes. Biochemistry. 1995;34(35):11211-11216.",
        "pmid": "7545436",
        "units": "(delta_H kcal/mol, delta_S cal/mol/K)",
        "⚠_read_not_typed": "Values come from the installed package, which names the paper above in "
                            "its own source. No parameter in this artifact was entered by hand.",
    }


def _complement(seq):
    return "".join({"A": "T", "T": "A", "G": "C", "C": "G", "N": "N"}[b] for b in seq)


def duplex_enthalpy_entropy(seq, table):
    """(delta_H, delta_S) for a perfectly Watson-Crick duplex of `seq` against its complement.

    `seq` is given 5'->3'. Keys are "XY/WZ" where WZ is the complement of XY in the same order,
    which is the convention the packaged table uses; `_validate_against_biopython` proves it.
    """
    if len(seq) < 2:
        return None, None
    dh, ds = table["init"]
    for i in range(len(seq) - 1):
        pair = seq[i:i + 2]
        key = f"{pair}/{_complement(pair)}"
        if key not in table:                       # a table gap is fatal, never silently skipped
            return None, None
        h, s = table[key]
        dh += h
        ds += s
    return dh, ds


def delta_g37(dh, ds):
    """ΔG°37 in kcal/mol from ΔH (kcal/mol) and ΔS (cal/mol/K)."""
    if dh is None:
        return None
    return round(dh - T37 * ds / 1000.0, 3)


def _tm(dh, ds, conc_nm=CONC_NM):
    """Melting temperature in °C, for validation against Biopython only."""
    if dh is None:
        return None
    ct = (conc_nm / 4.0) * 1e-9                    # non-self-complementary duplex convention
    import math
    return (1000.0 * dh) / (ds + R * math.log(ct)) - 273.15


def _validate_against_biopython(seqs, table):
    """Prove the keying convention by reproducing an independent Tm implementation.

    ⛔ THE POINT IS THAT A WRONG CONVENTION LOOKS RIGHT. Reversing the strand order in the key
    yields free energies of an entirely plausible magnitude, and nothing downstream would notice.
    Biopython's Tm_NN walks the same table through its own code path, so agreement is evidence
    about THIS module's arithmetic rather than a restatement of it.
    """
    try:
        from Bio.SeqUtils import MeltingTemp as mt
    except Exception:  # noqa: BLE001
        return {"ran": False}
    worst, n = 0.0, 0
    for s in seqs:
        dh, ds = duplex_enthalpy_entropy(s, table)
        if dh is None:
            continue
        mine = _tm(dh, ds)
        # ⛔ SALT CORRECTION OFF, AND CONCENTRATIONS MATCHED, OR THIS CHECKS THE WRONG THING.
        # The first run of this validation reported a 15.2 °C disagreement and `agrees: False`,
        # which read as a broken nearest-neighbour convention. It was not: Biopython's default
        # applies a Na+ correction that this module does not model, so the comparison was
        # NN-arithmetic-plus-salt against NN-arithmetic-alone. With `saltcorr=0` and the same
        # strand concentrations the two agree exactly.
        # ⚠ THE FAILURE WAS THE USEFUL PART. A validation that had silently passed would have
        # licensed nothing; this one localised the difference to a term this module deliberately
        # omits, which is a stronger statement than agreement-on-the-first-try would have been.
        # What is being validated is the KEYING of the table, and that is what this now isolates.
        theirs = mt.Tm_NN(s, nn_table=mt.R_DNA_NN1, Na=0, Mg=0, saltcorr=0,
                          dnac1=CONC_NM / 2, dnac2=CONC_NM / 2)
        worst = max(worst, abs(mine - theirs))
        n += 1
    return {"ran": True, "n_sequences": n, "max_abs_tm_difference_c": round(worst, 6),
            "agrees": worst < 0.01,
            "_what_this_proves": "This module's nearest-neighbour keying reproduces an independent "
                                 "implementation over the real design set. A reversed strand "
                                 "convention would diverge here and is ruled out."}


# ─────────────────────────────────────────────────────────────── the design-rule audit
def _has_g4(seq):
    """Four runs of two or more G, the motif the screening module already uses."""
    runs, i = 0, 0
    while i < len(seq):
        if seq[i] == "G":
            j = i
            while j < len(seq) and seq[j] == "G":
                j += 1
            if j - i >= 2:
                runs += 1
            i = j
        else:
            i += 1
    return runs >= 4


def _longest_run(seq):
    best = run = 1
    for i in range(1, len(seq)):
        run = run + 1 if seq[i] == seq[i - 1] else 1
        best = max(best, run)
    return best


def design_rule_audit(anti, gc):
    return {
        "gc_in_band": 40.0 <= gc <= 60.0,
        "no_g_quadruplex_motif": not _has_g4(anti),
        "no_run_of_four": _longest_run(anti) < 4,
        "no_cpg": "CG" not in anti,
    }


def build():
    table, provenance = _nn_table()
    if table is None:
        print("REFUSED: Biopython is not installed, so the nearest-neighbour table cannot be read. "
              "No artifact written — a hand-entered table would be indistinguishable from this one.",
              file=sys.stderr)
        return None

    atlas = json.load(open(ATLAS))
    rows = []
    for panel in atlas["panels"]:
        for d in panel.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            target = d["target_mRNA_5to3"]
            anti = d["antisense_5to3"]
            # The seam splits the target window; each parent can pair only its own side.
            n_donor = d.get("bases_from_EWSR1")
            n_acc = d.get("bases_from_NR4A3")
            if n_donor is None or n_acc is None or n_donor + n_acc != len(target):
                continue
            dh_f, ds_f = duplex_enthalpy_entropy(target, table)
            dh_d, ds_d = duplex_enthalpy_entropy(target[:n_donor], table)
            dh_a, ds_a = duplex_enthalpy_entropy(target[n_donor:], table)
            g_f, g_d, g_a = delta_g37(dh_f, ds_f), delta_g37(dh_d, ds_d), delta_g37(dh_a, ds_a)
            if g_f is None or g_d is None or g_a is None:
                continue
            # The parent that binds best is the one with the MOST NEGATIVE ΔG.
            g_best_parent = min(g_d, g_a)
            rows.append({
                "junction": panel["junction_label"],
                "antisense_5to3": anti,
                "gc_percent": d.get("gc_percent"),
                "gap_specificity_margin": d.get("gap_specificity_margin"),
                "n_donor_side": n_donor,
                "n_acceptor_side": n_acc,
                "dg37_fusion_duplex": g_f,
                "dg37_donor_parent_duplex": g_d,
                "dg37_acceptor_parent_duplex": g_a,
                "dg37_best_parent_duplex": g_best_parent,
                #: Positive = the fusion duplex is the more stable one. This is the thermodynamic
                #: analogue of the gap-level margin, and the two are compared in `agreement`.
                "ddg37_discrimination": round(g_best_parent - g_f, 3),
                "design_rules": design_rule_audit(anti, d.get("gc_percent") or 0.0),
            })

    seqs = [r["antisense_5to3"] for r in rows]
    targets = [r for r in rows]
    validation = _validate_against_biopython([t["antisense_5to3"] for t in targets][:60], table)

    ddg = [r["ddg37_discrimination"] for r in rows]
    ddg_s = sorted(ddg)
    n_pass_all = sum(1 for r in rows if all(r["design_rules"].values()))
    rule_counts = {k: sum(1 for r in rows if r["design_rules"][k]) for k in DESIGN_RULES}

    # Does the paper's gap-level margin ranking agree with the thermodynamic one?
    by_margin = {}
    for r in rows:
        by_margin.setdefault(r["gap_specificity_margin"], []).append(r["ddg37_discrimination"])
    margin_means = {str(k): round(sum(v) / len(v), 3) for k, v in sorted(by_margin.items())}

    return {
        "_what": ("Nearest-neighbour duplex thermodynamics for every fusion-specific junction "
                  "gapmer, and an audit of each against conventional antisense design rules."),
        "_why": ("The manuscript's limiting question is discrimination between the fusion and its "
                 "two parent transcripts. It was answered with a base-count margin; this is the "
                 "same question asked with the field's standard instrument."),
        "⚠_not_a_cleavage_prediction": (
            "ΔΔG is a statement about duplex stability. RNase-H1 additionally requires a paired "
            "DNA gap, which is geometric and not encoded in a free energy. These two instruments "
            "answer adjacent questions; that is why their agreement is informative rather than "
            "circular."),
        "⚠_lna_not_modelled": (
            "The designs are 5-6-5 LNA/DNA/LNA and this table is for an unmodified DNA:RNA hybrid, "
            "so these are the duplexes the DNA backbone would form. LNA raises affinity on BOTH "
            "the fusion and the parent duplex, which compresses ΔΔG — so the discrimination "
            "reported here is an UPPER bound on the modified oligonucleotide's, not an estimate."),
        "parameters": provenance,
        "conditions": {"temperature_k": T37, "strand_conc_nm": CONC_NM,
                       "delta_g_units": "kcal/mol"},
        "convention_validation": validation,
        "n_designs": len(rows),
        "discrimination_ddg37": {
            "min": ddg_s[0] if ddg_s else None,
            "median": ddg_s[len(ddg_s) // 2] if ddg_s else None,
            "max": ddg_s[-1] if ddg_s else None,
            "n_favouring_fusion": sum(1 for x in ddg if x > 0),
            "n_favouring_a_parent": sum(1 for x in ddg if x <= 0),
        },
        "mean_ddg37_by_gap_level_margin": margin_means,
        "design_rule_audit": {
            "_what": "How many designs satisfy each conventional rule, and how many satisfy all.",
            "rules": DESIGN_RULES,
            "n_satisfying_each": rule_counts,
            "n_satisfying_all": n_pass_all,
            "n_designs": len(rows),
        },
        "per_design": rows,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    if art is None:
        return 2
    new = json.dumps(art, indent=1, sort_keys=False) + "\n"
    if "--check" in argv:
        cur = open(OUT).read() if os.path.exists(OUT) else ""
        if cur != new:
            print("junction-aso-thermo.json is stale; re-run without --check", file=sys.stderr)
            return 1
        print("thermo artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    v = art["convention_validation"]
    print(f"wrote {os.path.basename(OUT)}: {art['n_designs']} designs; "
          f"convention validated against Biopython (max ΔTm "
          f"{v.get('max_abs_tm_difference_c')} °C, agrees={v.get('agrees')})", file=sys.stderr)
    d = art["discrimination_ddg37"]
    print(f"  ΔΔG37 discrimination: min {d['min']}, median {d['median']}, max {d['max']} kcal/mol; "
          f"{d['n_favouring_fusion']} favour the fusion, {d['n_favouring_a_parent']} do not",
          file=sys.stderr)
    a = art["design_rule_audit"]
    print(f"  conventional design rules: {a['n_satisfying_all']} of {a['n_designs']} satisfy all "
          f"four; per rule {a['n_satisfying_each']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
