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
# Orthologs are fetched by UniProt gene+organism QUERY (not hardcoded accessions, which are error-prone) so
# we always get the actual reviewed NR4A3 for each species. taxon ids: mouse/rat/bovine/pig/chicken/xenopus.
ORTHOLOG_TAXA = [("NR4A3_MOUSE", 10090), ("NR4A3_RAT", 10116), ("NR4A3_BOVIN", 9913),
                 ("NR4A3_PIG", 9823), ("NR4A3_CHICK", 9031)]
MIN_IDENTITY_FOR_DURABILITY = 0.70   # below this overall identity, the alignment is untrustworthy → exclude


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
    """Global-align ref vs other; return (mapping, overall_identity). mapping: ref_position(1-based) ->
    aligned other residue. overall_identity: fraction of ref positions matching (alignment-quality guard —
    a genuine ortholog LBD should be high; a low value flags a wrong/garbage sequence, not real divergence)."""
    from Bio import Align
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"
    aligner.open_gap_score = -10
    aligner.extend_gap_score = -0.5
    aligner.substitution_matrix = _blosum62()
    aln = aligner.align(ref_seq, other_seq)[0]
    ref_idx = 0
    mapping = {}
    match = 0
    a_ref, a_oth = str(aln[0]), str(aln[1])
    for cr, co in zip(a_ref, a_oth):
        if cr != "-":
            ref_idx += 1
            mapping[ref_idx] = co
            if cr == co:
                match += 1
    identity = match / ref_idx if ref_idx else 0.0
    return mapping, identity


def _blosum62():
    from Bio.Align import substitution_matrices
    return substitution_matrices.load("BLOSUM62")


def _fetch_ortholog(taxon, timeout=60):
    """Fetch the reviewed NR4A3 for a taxon by UniProt query (robust to my not knowing the accession)."""
    url = ("https://rest.uniprot.org/uniprotkb/search?query="
           f"gene:NR4A3+AND+organism_id:{taxon}+AND+reviewed:true&format=fasta&size=1")
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                lines = r.read().decode().splitlines()
            seq = "".join(l for l in lines if not l.startswith(">"))
            if seq:
                return seq
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i+1} taxon {taxon}: {e}", file=sys.stderr)
            import time
            time.sleep(2 ** i)
    return None


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
                 if (s := _fetch_fasta(acc))}                      # {name: (mapping, identity)}
    orth_maps_all = {name: _align_and_map(ref_seq, s) for name, tax in ORTHOLOG_TAXA
                     if (s := _fetch_ortholog(tax))}
    # alignment-quality guard: drop any "ortholog" whose overall identity is too low to trust (wrong/garbage
    # sequence) — this is exactly the check that caught the first bad-accession run.
    identities = {name: round(iden, 3) for name, (_m, iden) in orth_maps_all.items()}
    orth_maps = {name: m for name, (m, iden) in orth_maps_all.items() if iden >= MIN_IDENTITY_FOR_DURABILITY}
    dropped = {name: identities[name] for name in orth_maps_all if name not in orth_maps}
    para_maps = {name: m for name, (m, _iden) in para_maps.items()}

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
        "ortholog_alignment_identity": identities,
        "orthologs_used": sorted(orth_maps.keys()),
        "orthologs_dropped_low_identity": dropped,
        "_alignment_note": f"orthologs with overall identity < {MIN_IDENTITY_FOR_DURABILITY} are dropped as "
                           "untrustworthy (guards against wrong sequences). Durability is scored only over the "
                           "retained, high-identity orthologs. If few are retained, treat durability as weak.",
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
