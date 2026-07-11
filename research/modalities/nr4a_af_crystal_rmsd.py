#!/usr/bin/env python3
"""AF-model-vs-experimental-crystal Cα RMSD for the NR4A paralogues (NR4A1, NR4A2), matched to the §2.1
NR4A3 AF2↔8XTT-NMR benchmark so AF-vs-experiment fold fidelity is reported for ALL THREE paralogues, not
NR4A3 alone.

WHY. §2.1 benchmarks the AF2 NR4A3 model against the experimental 8XTT NMR ensemble. A reviewer can ask
"you validated AF against experiment for only one of the three receptors your selectivity claim compares."
NR4A1 (Nur77) and NR4A2 (Nurr1) DO have experimental LBD structures, so we can close that asymmetry.

NUANCE — stated, not hidden (this is an AF-vs-CRYSTAL FOLD check, not a pocket-state validation).
The paralogue experimental structures are COLLAPSED apo crystals whose orthosteric pocket is occluded and
filled with bulky side chains (Nurr1 1OVL; Nur77 3V3E), whereas NR4A3's 8XTT is a solution-NMR ensemble that
samples cavity-bearing conformers. So:
  * a SMALL global-LBD Cα RMSD confirms AF reproduces the experimental FOLD for the paralogue;
  * the pocket-local Cα RMSD is expected to be LARGER (AF's working pocket vs a collapsed crystal) and is
    itself informative about the collapsed→open displacement — it is NOT a validation of the open state.
We report both, alongside the NR4A3 AF2↔8XTT numbers for context, and never claim the crystals show an open
druggable pocket.

METHOD. Pure-numpy Kabsch superposition (reused from nr4a3_af2_nmr_rmsd). Residue correspondence by global
BLOSUM62 pairwise alignment (biopython) — two alignments composed:
  A: NR4A3 AF sequence ↔ paralogue AF sequence  -> maps the NR4A3 Pocket-5 residues onto paralogue numbering
  B: paralogue AF sequence ↔ crystal author seq -> maps paralogue numbering onto the crystal's author numbering
The alignment step is injectable (`align_fn`) so the residue-mapping logic is unit-tested with a stub; the
default aligner uses biopython, installed by the workflow. Structure fetch + run in af-crystal-rmsd-aws.yml
(ubuntu CPU; RCSB/AFDB reachable). Emits nr4a-af-crystal-rmsd.json (committed to git, durability rule).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nr4a3_af2_nmr_rmsd import _THREE_TO_ONE, kabsch_rmsd, _fetch, _fetch_af2  # noqa: E402

# NR4A3 reference: the AF2 accession and the Pocket-5 lining residues (UniProt numbering), same as §2.1.
NR4A3_ACC = "Q92570"
POCKET5 = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]

# Paralogue AF accession + a canonical apo LBD crystal (both cited in the paper: 1OVL = Nurr1/Wang 2003).
PARALOGUES = {
    "NR4A1": {"acc": "P22736", "pdb": "3V3E", "chain": "A", "name": "Nur77"},
    "NR4A2": {"acc": "P43354", "pdb": "1OVL", "chain": "A", "name": "Nurr1"},
}
MIN_ALIGN_IDENTITY_SAME = 0.90   # paralogue AF ↔ its own crystal: essentially the same sequence
MIN_ALIGN_IDENTITY_CROSS = 0.45  # NR4A3 ↔ paralogue: homologous but divergent LBDs (>~50% identity)


# --------------------------------------------------------------------------------------------------------
# parsing (chain-aware; pure stdlib) — a crystal may have several chains, so unlike the NMR parser we filter
# --------------------------------------------------------------------------------------------------------
def parse_ca_chain(pdb_text, chain=None, first_model_only=True):
    """Cα records of one chain in FILE ORDER: returns (seq_str, resnums, coords) where coords maps
    resSeq(int) -> (x,y,z). `chain=None` takes the first chain encountered. Skips altloc B+. Pure."""
    seq_chars, resnums, coords = [], [], {}
    seen_chain = None
    for line in pdb_text.splitlines():
        rec = line[:6].strip()
        if first_model_only and rec == "ENDMDL":
            break
        if rec != "ATOM" or line[12:16].strip() != "CA" or line[16] not in (" ", "A"):
            continue
        ch = line[21]
        if chain is not None and ch != chain:
            continue
        if chain is None:
            if seen_chain is None:
                seen_chain = ch
            elif ch != seen_chain:
                continue                                  # lock to the first chain we saw
        try:
            rs = int(line[22:26]); x = float(line[30:38]); y = float(line[38:46]); z = float(line[46:54])
        except ValueError:
            continue
        if rs in coords:
            continue                                      # first altloc wins
        coords[rs] = (x, y, z)
        resnums.append(rs)
        seq_chars.append(_THREE_TO_ONE.get(line[17:20].strip(), "X"))
    return "".join(seq_chars), resnums, coords


# --------------------------------------------------------------------------------------------------------
# alignment-based residue map (align_fn injectable for tests)
# --------------------------------------------------------------------------------------------------------
def _biopython_align(seq_a, seq_b):
    """Global BLOSUM62 alignment -> (blocks_a, blocks_b), biopython's Alignment.aligned index blocks."""
    from Bio.Align import PairwiseAligner, substitution_matrices
    aligner = PairwiseAligner()
    aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
    aligner.open_gap_score = -11
    aligner.extend_gap_score = -1
    aligner.mode = "global"
    aln = aligner.align(seq_a, seq_b)[0]
    return aln.aligned[0], aln.aligned[1]


def resnum_map(seq_a, resnums_a, seq_b, resnums_b, align_fn=None):
    """Map {resnum_a -> resnum_b} plus aligned-column identity, by globally aligning seq_a to seq_b.
    Each aligned block pairs equal-length ungapped runs; column k of a block maps index a0+k to b0+k, and
    those indices carry the author residue numbers resnums_a/resnums_b. Pure given align_fn."""
    if align_fn is None:
        align_fn = _biopython_align
    blocks_a, blocks_b = align_fn(seq_a, seq_b)
    mapping = {}
    matched = total = 0
    for (a0, a1), (b0, b1) in zip(blocks_a, blocks_b):
        if (a1 - a0) != (b1 - b0):
            raise ValueError(f"aligned block spans differ: ({a0},{a1}) vs ({b0},{b1})")
        for k in range(a1 - a0):
            ia, ib = a0 + k, b0 + k
            if ia >= len(resnums_a) or ib >= len(resnums_b):
                raise ValueError("alignment index exceeds residue-number list length")
            mapping[resnums_a[ia]] = resnums_b[ib]
            total += 1
            if seq_a[ia] == seq_b[ib]:
                matched += 1
    identity = (matched / total) if total else 0.0
    return mapping, identity


# --------------------------------------------------------------------------------------------------------
# compute (offline-testable: takes parsed structures + an align_fn, no network)
# --------------------------------------------------------------------------------------------------------
def compare_paralogue(af_para, crystal, af_nr4a3, pocket_nr4a3=POCKET5, align_fn=None,
                      min_id_same=MIN_ALIGN_IDENTITY_SAME, min_id_cross=MIN_ALIGN_IDENTITY_CROSS):
    """AF-vs-crystal global + pocket-local Cα RMSD for one paralogue.
    af_para / crystal / af_nr4a3 are each (seq_str, resnums, coords) from parse_ca_chain.
    Returns a result dict. Raises on implausible alignment identity (fail-loud: wrong chain / bad download)."""
    import numpy as np

    af_seq, af_res, af_xyz = af_para
    cr_seq, cr_res, cr_xyz = crystal
    n3_seq, n3_res, n3_xyz = af_nr4a3

    # B: paralogue AF -> crystal author numbering (same protein; identity must be high)
    para_to_crystal, id_same = resnum_map(af_seq, af_res, cr_seq, cr_res, align_fn=align_fn)
    if id_same < min_id_same:
        raise ValueError(f"paralogue-AF↔crystal identity {id_same:.3f} < {min_id_same} — wrong chain/download?")

    # A: NR4A3 AF -> paralogue AF numbering (homologous; maps the Pocket-5 residues across)
    nr4a3_to_para, id_cross = resnum_map(n3_seq, n3_res, af_seq, af_res, align_fn=align_fn)
    if id_cross < min_id_cross:
        raise ValueError(f"NR4A3↔paralogue identity {id_cross:.3f} < {min_id_cross} — not homologous LBDs?")

    # global: every paralogue residue present in AF, in the crystal (via map), and resolved in crystal coords
    global_pairs = [(r, para_to_crystal[r]) for r in af_res
                    if r in para_to_crystal and r in af_xyz and para_to_crystal[r] in cr_xyz]
    # pocket: NR4A3 pocket residues -> paralogue numbering -> crystal numbering, present in both structures
    pocket_para = [nr4a3_to_para[p] for p in pocket_nr4a3 if p in nr4a3_to_para]
    pocket_pairs = [(r, para_to_crystal[r]) for r in pocket_para
                    if r in para_to_crystal and r in af_xyz and para_to_crystal[r] in cr_xyz]

    def _rmsd(pairs):
        if len(pairs) < 3:
            return None, len(pairs)
        P = np.array([af_xyz[a] for a, _ in pairs], float)
        Q = np.array([cr_xyz[b] for _, b in pairs], float)
        return kabsch_rmsd(P, Q), len(pairs)

    g_rmsd, g_n = _rmsd(global_pairs)
    p_rmsd, p_n = _rmsd(pocket_pairs)
    return {
        "align_identity_af_vs_crystal": round(id_same, 4),
        "align_identity_nr4a3_vs_paralogue": round(id_cross, 4),
        "global_ca_rmsd": None if g_rmsd is None else round(g_rmsd, 3),
        "global_ca_n": g_n,
        "pocket_ca_rmsd": None if p_rmsd is None else round(p_rmsd, 3),
        "pocket_ca_n": p_n,
        "pocket_residues_paralogue_numbering": pocket_para,
    }


# --------------------------------------------------------------------------------------------------------
# job (fetch + run; ubuntu CPU)
# --------------------------------------------------------------------------------------------------------
def main():
    n3_txt = _fetch_af2(NR4A3_ACC)
    af_nr4a3 = parse_ca_chain(n3_txt, chain=None)

    out = {
        "_title": "AF-model vs experimental-crystal Cα RMSD for the NR4A paralogues (matched to §2.1 NR4A3 "
                  "AF2↔8XTT)",
        "_method": "pure-numpy Kabsch; BLOSUM62 global alignment (biopython) for the NR4A3↔paralogue and "
                   "paralogue-AF↔crystal residue maps; two alignments composed to carry Pocket-5 across.",
        "_caveat": "Paralogue experimental structures are COLLAPSED apo crystals (occluded orthosteric "
                   "pocket); this is an AF-vs-crystal FOLD check, NOT a pocket-state validation. A small "
                   "global RMSD confirms the fold; the larger pocket RMSD reflects the collapsed→open "
                   "displacement and is not evidence of an open crystal state.",
        "nr4a3_reference_af2_vs_8xtt_nmr": {
            "note": "from §2.1 (nr4a3_8xtt_benchmark / nr4a3_af2_nmr_rmsd), for context on a matched footing",
            "global_ca_rmsd_median_A": 7.63, "pocket_ca_rmsd_median_A": 3.56,
            "af2_within_nmr_spread": True, "experimental_data_type": "solution-NMR ensemble (20 models)"},
        "nr4a3_acc": NR4A3_ACC, "pocket5_nr4a3": POCKET5,
        "paralogues": {},
    }
    for name, spec in PARALOGUES.items():
        af_txt = _fetch_af2(spec["acc"])
        cr_txt = _fetch(f"https://files.rcsb.org/download/{spec['pdb']}.pdb")
        af_para = parse_ca_chain(af_txt, chain=None)
        crystal = parse_ca_chain(cr_txt, chain=spec["chain"])
        res = compare_paralogue(af_para, crystal, af_nr4a3)
        res.update({"acc": spec["acc"], "crystal_pdb": spec["pdb"], "crystal_chain": spec["chain"],
                    "name": spec["name"], "experimental_data_type": "apo crystal (collapsed pocket)"})
        out["paralogues"][name] = res
        print(f"[{name}/{spec['name']}] AF vs {spec['pdb']}: global {res['global_ca_rmsd']} Å "
              f"(n={res['global_ca_n']}), pocket {res['pocket_ca_rmsd']} Å (n={res['pocket_ca_n']}); "
              f"id af↔crystal {res['align_identity_af_vs_crystal']}, id nr4a3↔para "
              f"{res['align_identity_nr4a3_vs_paralogue']}", flush=True)

    out_dir = os.environ.get("OUT_DIR", os.path.join("results", "nr4a-af-crystal-rmsd"))
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "nr4a-af-crystal-rmsd.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=2)
    print("[af-crystal-rmsd] wrote", p)


if __name__ == "__main__":
    main()
