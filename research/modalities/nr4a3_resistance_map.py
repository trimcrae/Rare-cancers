#!/usr/bin/env python3
"""
Resistance / escape-liability map of the NR4A3 warhead pocket (audit KEEP, high; ledger new).

WHY. Escape mutation is the documented clinical failure mode of a fusion-oncogene-directed agent: the tumour
mutates a drug-contact residue to abolish binding *while preserving the oncoprotein's function*. A resistance
mutation is therefore only viable where the drug-contact residue is NOT itself functionally essential. The
in-silico forecast: overlay (a) which pocket residues the warhead engages with (b) how conserved each is —
across the NR4A paralogues and across NR4A3 orthologs. A drug anchor on a HIGHLY-conserved residue is DURABLE
(mutating it costs fitness); an anchor on a VARIABLE residue is RESISTANCE-LIABLE (the tumour can mutate it
cheaply). This is the conservation half of the resistance forecast; the energetic ΔΔG half (MM-GBSA/FEP on
point mutants) is the GPU follow-up that consumes the same pocket-residue list.

Pocket-5 lining residues (fpocket on the AF2 model; incl. all 7 selectivity handles), NR4A3/Q92570 numbering:
    406, 407, 410, 411, 412, 481, 484, 485, 531, 534

Sequences fetched live from UniProt (paralogues NR4A1 P22736 / NR4A2 P43354; NR4A3 orthologs across species).
Internet required -> runs in CI. Output: nr4a-resistance-map.json.
"""

import json
import os
import sys
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a-resistance-map.json")

POCKET_RESIDUES = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]
HANDLES = {406, 407, 410, 412, 484, 531, 534}       # the paralogue-selectivity handles among them

# NR4A3 human is the reference (numbering anchor). Paralogues + orthologs for the two conservation axes.
REF = ("NR4A3_HUMAN", "Q92570")
PARALOGUES = [("NR4A1_HUMAN", "P22736"), ("NR4A2_HUMAN", "P43354")]
ORTHOLOGS = [("NR4A3_MOUSE", "Q9QZB6"), ("NR4A3_RAT", "Q9WU45"), ("NR4A3_BOVIN", "Q0VCX8"),
             ("NR4A3_XENTR", "Q6NU29")]


def _fetch_fasta(acc, timeout=60):
    url = f"https://rest.uniprot.org/uniprotkb/{acc}.fasta"
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                lines = r.read().decode().splitlines()
            return "".join(l for l in lines if not l.startswith(">"))
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i+1} {acc}: {e}", file=sys.stderr)
            import time
            time.sleep(2 ** i)
    return None


def _align_and_map(ref_seq, other_seq):
    """Global-align ref vs other; return dict ref_position(1-based) -> aligned other residue (or '-')."""
    from Bio import Align
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"
    aligner.open_gap_score = -10
    aligner.extend_gap_score = -0.5
    aligner.substitution_matrix = _blosum62()
    aln = aligner.align(ref_seq, other_seq)[0]
    # walk the aligned columns, tracking ref index
    ref_idx = 0
    mapping = {}
    a_ref, a_oth = str(aln[0]), str(aln[1])
    for cr, co in zip(a_ref, a_oth):
        if cr != "-":
            ref_idx += 1
            mapping[ref_idx] = co
    return mapping


def _blosum62():
    from Bio.Align import substitution_matrices
    return substitution_matrices.load("BLOSUM62")


def main():
    try:
        import Bio  # noqa: F401
    except ImportError:
        json.dump({"_status": "biopython missing"}, open(OUT, "w"), indent=2)
        print("biopython missing", file=sys.stderr); return

    ref_seq = _fetch_fasta(REF[1])
    if not ref_seq:
        json.dump({"_status": "could not fetch reference NR4A3"}, open(OUT, "w"), indent=2); return

    para_maps = {name: _align_and_map(ref_seq, s) for name, acc in PARALOGUES
                 if (s := _fetch_fasta(acc))}
    orth_maps = {name: _align_and_map(ref_seq, s) for name, acc in ORTHOLOGS
                 if (s := _fetch_fasta(acc))}

    rows = []
    for pos in POCKET_RESIDUES:
        if pos > len(ref_seq):
            rows.append({"position": pos, "_status": "out of range"}); continue
        ref_aa = ref_seq[pos - 1]
        para = {name: m.get(pos, "?") for name, m in para_maps.items()}
        orth = {name: m.get(pos, "?") for name, m in orth_maps.items()}
        orth_conserved = sum(1 for v in orth.values() if v == ref_aa)
        orth_total = len(orth)
        para_conserved = sum(1 for v in para.values() if v == ref_aa)
        # durability: conserved across species = evolutionarily constrained = costly to mutate = durable anchor
        ortho_frac = orth_conserved / orth_total if orth_total else None
        if ortho_frac is None:
            durability = "unknown"
        elif ortho_frac >= 0.99:
            durability = "durable anchor (fully ortholog-conserved)"
        elif ortho_frac >= 0.5:
            durability = "moderately durable"
        else:
            durability = "resistance-liable (ortholog-variable)"
        rows.append({
            "position": pos,
            "nr4a3_residue": ref_aa,
            "is_selectivity_handle": pos in HANDLES,
            "paralogue_residues": para,
            "paralogue_conserved_count": f"{para_conserved}/{len(para)}",
            "ortholog_residues": orth,
            "ortholog_conserved_fraction": round(ortho_frac, 2) if ortho_frac is not None else None,
            "resistance_durability": durability,
        })

    result = {
        "_title": "NR4A3 warhead-pocket resistance / escape-liability map (conservation half)",
        "_note": "Durable anchor = ortholog-conserved pocket residue (mutating it costs oncoprotein fitness → "
                 "escape unlikely); resistance-liable = ortholog-variable (cheap to mutate). A robust warhead "
                 "should anchor on the DURABLE residues. The energetic ΔΔG half (MM-GBSA/FEP on point mutants "
                 "of these positions) is the GPU follow-up. Note: selectivity handles are DIVERGENT across "
                 "paralogues BY DESIGN (that is what gives selectivity) — durability is the orthogonal, "
                 "ortholog-conservation axis, so a residue can be both a good selectivity handle AND a durable "
                 "anchor if it is paralogue-divergent yet ortholog-conserved.",
        "reference": REF[0],
        "pocket_residues": rows,
        "summary": {
            "durable_anchors": [r["position"] for r in rows
                                if str(r.get("resistance_durability", "")).startswith("durable")],
            "resistance_liable": [r["position"] for r in rows
                                  if str(r.get("resistance_durability", "")).startswith("resistance")],
        },
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
