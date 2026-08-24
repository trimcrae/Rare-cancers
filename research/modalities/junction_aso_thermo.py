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

⛔⛔ AND THE KEYING IS VALIDATED, NOT ASSUMED — BUT VALIDATED IS NOT THE SAME AS "THE STRAND IS
RIGHT", AND THIS BLOCK CLAIMED BOTH UNTIL 2026-08-13. A nearest-neighbour table is a dictionary of
"XY/WZ" keys, and mis-keying it produces numbers that are wrong and look entirely plausible — the
failure mode this repository keeps paying for. So `_validate_against_biopython` recomputes Tm from
this module's own ΔH and ΔS and checks it against Biopython's independent `Tm_NN`, which walks the
same table through its own code path. That is a real check of the SUMMATION AND KEYING, and
`tests/test_junction_aso_thermo.py` shows it has power by mis-keying the table and watching it break.
⚠ *Superseded, retained: "If the convention were wrong the two would diverge; agreement to 0.01 °C is
what licenses every number below."* It licenses the arithmetic and nothing else. Both
implementations build the key the same way from whatever sequence they are handed, so they agree on
EITHER strand and the check cannot see a strand swap. MEASURED, on design GGGCATATCCGTGGAC: the
target strand GTCCACGGATATGCCC gives ΔG°37 −21.371 and the antisense strand −22.975 — a 1.6 kcal/mol
difference — and at BOTH the two implementations agree to 0.0000 °C. A validation that passes equally
under the right and the wrong strand says nothing about the strand.
⭐ WHAT ACTUALLY FIXES THE STRAND is Biopython's documented convention for `R_DNA_NN1`: the sequence
supplied must be the RNA one. This module passes `target_mRNA_5to3`, which is that sequence, and the
committed `dg37_fusion_duplex` of −21.371 reproduces from it. The strand is right for a reason that
is documented, not for a reason this check tested.

⚠ LNA IS NOT MODELLED, AND THAT IS A REAL LIMIT. These designs are 5-6-5 LNA/DNA/LNA. Sugimoto's
table is for an unmodified DNA:RNA hybrid, so what is computed here is the duplex the DNA backbone
would form.

⛔ THE DIRECTION OF THAT LIMIT WAS STATED BACKWARDS UNTIL 2026-08-13, HERE, IN THE ARTIFACT AND IN
THE MANUSCRIPT. ⚠ *Superseded, retained: "The effect is applied to BOTH the fusion duplex and the
parent duplex, so it is not neutral — it compresses ΔΔG, meaning the discrimination reported here is
an UPPER bound on the modified oligonucleotide's."* Two things are wrong with that. Equal ABSOLUTE
stabilisation of both duplexes leaves a DIFFERENCE of free energies unchanged rather than compressed
— ΔΔG is in kcal/mol, not a ratio. And the stabilisation is not equal, because the retention rule
puts the seam strictly inside the gap: `n_donor` and `n_acceptor` are both in {6,…,10}, so the
donor-side run always covers the whole 5′ LNA wing and never the 3′ one, and the acceptor-side run
the reverse. THE FUSION DUPLEX PAIRS ALL TEN LNA RESIDUES AND EACH PARENT DUPLEX EXACTLY FIVE, for
all 190 designs by construction. LNA therefore adds roughly twice as much affinity to the fusion
duplex, and ΔΔG GROWS: what is computed here is a conservative FLOOR on the modified
oligonucleotide's binding discrimination, not a ceiling.
The compression intuition is right for a different comparison — a transcriptome near-match that
pairs both wings and mismatches inside the DNA gap — and it was carried over to the parent
comparison, where the geometry is the opposite. ⚠ The floor direction is argued from the
architecture, NOT computed: no LNA nearest-neighbour parameters are applied anywhere in this module.

    python3 research/modalities/junction_aso_thermo.py            # write the artifact
    python3 research/modalities/junction_aso_thermo.py --check    # exit 1 if it would change
"""
from __future__ import annotations

import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
#: ⛔ BOTH PATHS FOLLOW `OUT_SUFFIX`, SO A SECOND GEOMETRY CANNOT LAND ON THE FIRST ONE'S FILE
#: (2026-08-13). Nothing in this module is 16-mer-specific — the nearest-neighbour sum walks whatever
#: window it is handed, and the donor/acceptor split comes from the atlas row — so it produced a
#: correct 5-10-5 answer and wrote it over the 5-6-5 artifact the manuscript's ΔΔG sentences quote.
#: A module that is length-agnostic in its arithmetic and length-blind in its filenames is the more
#: dangerous of the two, because the numbers inside are right.
_SUFFIX = os.environ.get("OUT_SUFFIX", "")
ATLAS = os.path.join(HERE, os.environ.get("ATLAS_JSON")
                     or f"nr4a3-fusion-junction-atlas{_SUFFIX}.json")
OUT = os.path.join(HERE, f"junction-aso-thermo{_SUFFIX}.json")

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
    """Melting temperature in °C at `conc_nm` total strand concentration.

    ⭐ ALSO WRITTEN PER DESIGN SINCE 2026-08-24. It was computed for the Biopython cross-check only,
    and external review of the condensed article asked for predicted Tm — which a laboratory
    ordering these oligonucleotides needs and which this module was already computing and throwing
    away. Same ΔH/ΔS, same table, same conditions block as every ΔG in this artifact, so a Tm and a
    ΔG here can never come from different arithmetic.
    ⚠ THE `⚠_lna_not_modelled` CAVEAT APPLIES TO Tm EXACTLY AS IT DOES TO ΔG, AND MATTERS MORE:
    these are the values for an UNMODIFIED DNA:RNA hybrid, and a 5-6-5 LNA gapmer's real Tm is
    substantially higher. The fusion duplex pairs all ten locked residues and each parent duplex
    exactly five, so LNA raises the fusion Tm more than the parent Tm — the Tm SEPARATION below is
    a floor on the modified oligonucleotide's, not an estimate of it.
    """
    if dh is None:
        return None
    ct = (conc_nm / 4.0) * 1e-9                    # non-self-complementary duplex convention
    import math
    return (1000.0 * dh) / (ds + R * math.log(ct)) - 273.15


def _validate_against_biopython(seqs, table):
    """Prove the KEYING AND SUMMATION by reproducing an independent Tm implementation.

    ⛔ THE POINT IS THAT A WRONG KEY LOOKS RIGHT. Mis-keying the table — pairing "XY" with something
    other than the complement of XY in the same order — yields free energies of an entirely plausible
    magnitude, and nothing downstream would notice. Biopython's `Tm_NN` walks the same table through
    its own code path, so agreement is evidence about THIS module's arithmetic rather than a
    restatement of it, and `test_a_reversed_convention_would_be_caught` shows the check has power.

    ⛔ WHAT IT CANNOT DO, STATED HERE BECAUSE THE ARTIFACT USED TO CLAIM IT COULD. Both
    implementations derive the key from whatever sequence they are given, so they agree on the target
    strand and on the antisense strand alike. This check therefore has NO power over the strand
    choice; see the module docstring for the measurement, and for the documented convention that
    actually fixes it.
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
            "_what_this_proves": (
                f"This module's nearest-neighbour SUMMATION AND KEYING reproduce an independent "
                f"implementation (Biopython's Tm_NN, walking the same table through its own code "
                f"path) over {n} of the design set's 16-mers, to within 0.01 °C. That is the whole "
                f"of what it establishes."),
            "⛔_what_this_does_NOT_prove": (
                "It does NOT rule out a reversed strand convention, and this field said it did "
                "until 2026-08-13. Both implementations build the nearest-neighbour key the same "
                "way from whatever sequence they are handed, so they agree on either strand. "
                "Measured on design GGGCATATCCGTGGAC: the target strand gives ΔG°37 -21.371 and the "
                "antisense strand -22.975, and at BOTH the two implementations agree to 0.0000 °C. "
                "The strand is fixed instead by Biopython's documented convention for R_DNA_NN1 — "
                "the sequence supplied must be the RNA one — and this module supplies "
                "target_mRNA_5to3, which is that sequence."),
            "⚠_superseded_what_this_proves": (
                "Rule 1.2, retained: 'This module's nearest-neighbour keying reproduces an "
                "independent implementation over the real design set. A reversed strand convention "
                "would diverge here and is ruled out.' Both halves were wrong. The check ran on a "
                "[:60] slice of the 190 designs while the artifact's own n_sequences read 60, and "
                "it has no power over the strand at all. The slice is gone and the claim is now "
                "scoped to what was measured.")}


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
            t_f, t_d, t_a = _tm(dh_f, ds_f), _tm(dh_d, ds_d), _tm(dh_a, ds_a)
            #: ⛔ THE WORST CASE IS THE HOTTEST PARENT, AND IT IS SELECTED ON Tm RATHER THAN
            #: INHERITED FROM THE ΔG CHOICE. The two orderings agree for every design in this panel,
            #: but they are different questions — ΔG ranks at 37 °C and Tm ranks the melting point —
            #: and taking `min(ΔG)`'s parent would silently make the Tm column a ΔG result.
            t_best_parent = max(t_d, t_a)
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
                "tm_fusion_duplex_c": round(t_f, 1),
                "tm_donor_parent_duplex_c": round(t_d, 1),
                "tm_acceptor_parent_duplex_c": round(t_a, 1),
                "tm_best_parent_duplex_c": round(t_best_parent, 1),
                #: Positive = the fusion duplex melts higher than the closest parent duplex.
                "dtm_discrimination_c": round(t_f - t_best_parent, 1),
                "design_rules": design_rule_audit(anti, d.get("gc_percent") or 0.0),
            })

    # ⛔ NO SLICE. This read `[...][:60]` while the artifact's `_what_this_proves` said the check ran
    # "over the real design set" and its own `n_sequences` said 60 — a scope claim contradicted by
    # the field beside it. Nothing selected those 60 and nothing quotes the number; the check is
    # arithmetic over 16-mers and costs nothing, so it now runs over every design and the claim is
    # simply true. (Measured 2026-08-13: at n=60 and at n=190 the worst disagreement is 0.0 °C
    # alike, so this widens the evidence without moving it.)
    validation = _validate_against_biopython([r["antisense_5to3"] for r in rows], table)

    ddg = [r["ddg37_discrimination"] for r in rows]
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
            "so these are the duplexes the DNA backbone would form. Because the seam lies inside "
            "the gap, the fusion duplex pairs all TEN LNA residues while each parent duplex pairs "
            "exactly FIVE, for every design by construction — so LNA widens ΔΔG rather than "
            "compressing it, and the discrimination reported here is a conservative FLOOR on the "
            "modified oligonucleotide's, not a ceiling. Argued from the architecture, not computed: "
            "no LNA parameters are applied. ⚠ Superseded, retained: this field previously said the "
            "opposite, that LNA 'compresses ΔΔG' and the value is an UPPER bound."),
        "parameters": provenance,
        "conditions": {"temperature_k": T37, "strand_conc_nm": CONC_NM,
                       "delta_g_units": "kcal/mol"},
        "convention_validation": validation,
        "n_designs": len(rows),
        "discrimination_ddg37": {
            "min": min(ddg) if ddg else None,
            #: ⛔ THIS WAS `ddg_s[len(ddg_s) // 2]`, WHICH IS NOT A MEDIAN ON AN EVEN-SIZED SET
            #: (2026-08-13). With 190 values it returns the UPPER of the two central ones rather
            #: than their mean, so a field labelled `median` held a value the label does not
            #: describe. ⚠ THE LABEL IS THE DEFECT, NOT THE ROUNDED PROSE: the manuscript's "a
            #: median of 9.6" is right either way, which is exactly why nothing caught it — a
            #: mislabelled field is quotable at full precision by any consumer that reads the
            #: artifact rather than the paper. Read from `statistics`, not reimplemented, because
            #: reimplementing it is what produced the bug.
            "median": round(statistics.median(ddg), 4) if ddg else None,
            "⚠_superseded_median": (
                "Rule 1.2, retained: 9.603, the value this field carried until 2026-08-13. It was "
                "`sorted(ddg)[len(ddg) // 2]` over 190 values — the upper of the two central values "
                "(9.582 and 9.603), not their mean. The corrected median is 9.5925; both round to "
                "the 9.6 the manuscript prints, so no sentence changes."),
            "max": max(ddg) if ddg else None,
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
