#!/usr/bin/env python3
"""
Broader NR-superfamily selectivity liability screen for the NR4A3 warhead pocket (ledger A4 / D4).

WHY. The selectivity claim for an NR4A3-degrader warhead has so far been tested against **only the two
paralogues** NR4A1/NR4A2. That is under-powered: the human nuclear-receptor (NR) superfamily is ~48 proteins
that all share the LBD fold, so a warhead that binds an NR4A3 LBD pocket could in principle cross-react with a
non-paralogue NR whose pocket happens to resemble NR4A3's. This module screens the WHOLE human NR superfamily
for pocket-lining-residue resemblance to NR4A3 and ranks the nearest neighbours as the NRs that most warrant an
energetic (docking / FEP) cross-binding follow-up.

WHAT. For each human NR:
  1. global-align its sequence to human NR4A3 (Q92570) with BLOSUM62 (same aligner as nr4a3_resistance_map);
  2. map the 10 NR4A3 warhead-pocket residues (Q92570 numbering) onto it;
  3. score pocket_identity (fraction of the 10 that are IDENTICAL) and pocket_similarity (same coarse
     chemical group), plus overall LBD identity as an alignment-confidence proxy.
Rank descending by pocket_identity. NR4A1/NR4A2 are included as POSITIVE CONTROLS (they must top the ranking —
if they don't, the method is broken). Every other NR that scores near them is a flagged liability.

HONEST LIMITS (stated in the output JSON, not buried):
  - Sequence pocket-residue resemblance is NECESSARY-not-sufficient for cross-binding — it prioritises which
    NRs need the energetic follow-up; it does NOT prove (or exclude) cross-binding on its own.
  - The warhead targets a CRYPTIC pocket, so even a sequence-similar NR may not FORM the same pocket — a second
    reason this screen only prioritises, and cannot conclude selectivity by itself.
  - Distant NRs share only ~20-30% overall identity; where overall identity is low the pocket-residue mapping is
    less reliable, so each NR carries a `mapping_confidence` flag and low-confidence hits are caveated.

Sequences fetched live from UniProt -> runs in CI (internet). Output: nr4a-superfamily-selectivity.json.
The pure scoring core (pocket_conservation) is import-safe and unit-tested without network/biopython.
"""

import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a-superfamily-selectivity.json")

# NR4A3 warhead-pocket lining residues (Q92570 numbering) — identical set used by nr4a3_resistance_map.py.
POCKET_RESIDUES = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]
HANDLES = {406, 407, 410, 412, 484, 531, 534}       # the paralogue-selectivity handles among them

REF = ("NR4A3_HUMAN", "Q92570")
# Positive controls: the two paralogues MUST rank at/near the top. Always included even if the family query is
# imperfect, so the screen is self-validating regardless of what UniProt returns for the family search.
CONTROLS = [("NR4A1_HUMAN", "P22736"), ("NR4A2_HUMAN", "P43354")]

# Coarse chemical-similarity groups (standard) — pure, no biopython, so pocket_similarity is testable offline.
_GROUP = {}
for _grp in ("AVLIM", "FWY", "KRH", "DE", "STNQ", "C", "G", "P"):
    for _a in _grp:
        _GROUP[_a] = _grp
# Overall identity below this => the global alignment is in low-homology territory and the pocket mapping for
# that NR is less trustworthy (reported, but flagged low-confidence). NR-superfamily LBDs cluster ~20-35%.
MIN_CONFIDENT_IDENTITY = 0.30


def _similar(a, b):
    """Identical OR same coarse chemical group (conservative substitution)."""
    if a == b:
        return True
    ga = _GROUP.get(a)
    return ga is not None and ga == _GROUP.get(b)


def pocket_conservation(ref_seq, pocket_residues, mapping):
    """PURE core (no network / no biopython). Given the NR4A3 reference sequence, the 1-based pocket positions,
    and a mapping {ref_pos -> aligned residue in the other NR ('-' if gapped}}, return per-residue detail plus
    pocket_identity / pocket_similarity fractions over the in-range positions."""
    rows, ident, simil, n = [], 0, 0, 0
    for pos in pocket_residues:
        if pos > len(ref_seq):
            rows.append({"position": pos, "_status": "out of range"})
            continue
        ref_aa = ref_seq[pos - 1]
        oth = mapping.get(pos, "-")
        n += 1
        is_id = oth == ref_aa
        is_sim = _similar(ref_aa, oth)
        ident += 1 if is_id else 0
        simil += 1 if is_sim else 0
        rows.append({"position": pos, "nr4a3_residue": ref_aa, "other_residue": oth,
                     "identical": is_id, "similar": is_sim, "is_handle": pos in HANDLES})
    return {"rows": rows, "n": n,
            "pocket_identity": round(ident / n, 3) if n else None,
            "pocket_similarity": round(simil / n, 3) if n else None}


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


def _fetch_human_nr_family(timeout=90):
    """Query UniProt for the reviewed human nuclear-receptor superfamily (accession + gene) — no hardcoded
    accession list (error-prone, per the resistance_map convention). Returns [(gene_or_acc, accession)]."""
    q = ('(family:"nuclear hormone receptor family") AND (organism_id:9606) AND (reviewed:true)')
    url = ("https://rest.uniprot.org/uniprotkb/search?query=" + urllib.parse.quote(q)
           + "&fields=accession,gene_primary&format=tsv&size=200")
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode()
            out = []
            for line in txt.strip().splitlines()[1:]:      # skip header
                parts = line.split("\t")
                acc = parts[0].strip()
                gene = (parts[1].strip() if len(parts) > 1 and parts[1].strip() else acc)
                if acc:
                    out.append((gene, acc))
            return out
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i+1} family query: {e}", file=sys.stderr)
            import time
            time.sleep(2 ** i)
    return []


def _align_and_map(ref_seq, other_seq):
    """Global-align ref vs other (BLOSUM62); return (mapping, overall_identity). Identical aligner settings to
    nr4a3_resistance_map._align_and_map so the two conservation screens are methodologically consistent."""
    from Bio import Align
    from Bio.Align import substitution_matrices
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"
    aligner.open_gap_score = -10
    aligner.extend_gap_score = -0.5
    aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
    aln = aligner.align(ref_seq, other_seq)[0]
    ref_idx, mapping, match = 0, {}, 0
    a_ref, a_oth = str(aln[0]), str(aln[1])
    for cr, co in zip(a_ref, a_oth):
        if cr != "-":
            ref_idx += 1
            mapping[ref_idx] = co
            if cr == co:
                match += 1
    return mapping, (match / ref_idx if ref_idx else 0.0)


def main():
    try:
        import Bio  # noqa: F401
    except ImportError:
        json.dump({"_status": "biopython missing"}, open(OUT, "w"), indent=2)
        print("biopython missing", file=sys.stderr)
        return

    ref_seq = _fetch_fasta(REF[1])
    if not ref_seq:
        json.dump({"_status": "could not fetch reference NR4A3"}, open(OUT, "w"), indent=2)
        return

    # Build the target set: the queried human NR family + the two controls, de-duplicated, ref removed.
    family = _fetch_human_nr_family()
    by_acc = {}
    for gene, acc in family + CONTROLS:
        if acc != REF[1]:
            by_acc.setdefault(acc, gene)
    control_accs = {acc for _n, acc in CONTROLS}

    scored = []
    for acc, gene in sorted(by_acc.items(), key=lambda kv: kv[1]):
        s = _fetch_fasta(acc)
        if not s:
            continue
        mapping, overall = _align_and_map(ref_seq, s)
        pc = pocket_conservation(ref_seq, POCKET_RESIDUES, mapping)
        scored.append({
            "gene": gene, "accession": acc,
            "is_control_paralogue": acc in control_accs,
            "overall_identity": round(overall, 3),
            "mapping_confidence": "ok" if overall >= MIN_CONFIDENT_IDENTITY else "low (distant homology)",
            "pocket_identity": pc["pocket_identity"],
            "pocket_similarity": pc["pocket_similarity"],
            "pocket_residues": pc["rows"],
        })

    # Rank by pocket_identity (then similarity, then overall) descending — nearest pocket neighbours first.
    scored.sort(key=lambda r: (r["pocket_identity"] or 0, r["pocket_similarity"] or 0,
                               r["overall_identity"]), reverse=True)

    controls = [r for r in scored if r["is_control_paralogue"]]
    non_ctrl = [r for r in scored if not r["is_control_paralogue"]]
    ctrl_min_id = min((r["pocket_identity"] or 0 for r in controls), default=None)
    # A non-paralogue is a flagged liability if its pocket identity reaches into the controls' range AND the
    # alignment is confident. (If it beats the controls it is a hard flag.)
    liabilities = [r for r in non_ctrl
                   if r["mapping_confidence"] == "ok" and ctrl_min_id is not None
                   and (r["pocket_identity"] or 0) >= ctrl_min_id]

    result = {
        "_title": "NR4A3 warhead-pocket selectivity liability screen across the human NR superfamily (A4/D4)",
        "_method": "Global BLOSUM62 alignment of each human NR to NR4A3 (Q92570); the 10 warhead-pocket residues "
                   "(Q92570 numbering) are mapped and scored for identity / coarse-chemical similarity. Ranked "
                   "by pocket identity; NR4A1/NR4A2 are positive controls that must top the list.",
        "_honest_limits": [
            "Pocket-residue sequence resemblance is NECESSARY-not-sufficient for cross-binding: it prioritises "
            "which NRs need an energetic (docking/FEP) follow-up, it does not by itself prove or exclude "
            "cross-reactivity.",
            "The warhead targets a CRYPTIC pocket — a sequence-similar NR may still not FORM the same pocket, so "
            "this screen can only prioritise, never conclude selectivity alone.",
            f"Overall NR-superfamily LBD identity is low (~20-35%); where overall identity < "
            f"{MIN_CONFIDENT_IDENTITY} the pocket mapping is flagged low-confidence.",
        ],
        "reference": REF[0],
        "pocket_residues_q92570": POCKET_RESIDUES,
        "n_receptors_screened": len(scored),
        "family_query_hits": len(family),
        "controls_paralogues": [{"gene": r["gene"], "pocket_identity": r["pocket_identity"],
                                 "pocket_similarity": r["pocket_similarity"]} for r in controls],
        "control_min_pocket_identity": ctrl_min_id,
        "flagged_liabilities": [{"gene": r["gene"], "accession": r["accession"],
                                 "pocket_identity": r["pocket_identity"],
                                 "pocket_similarity": r["pocket_similarity"],
                                 "overall_identity": r["overall_identity"]} for r in liabilities],
        "ranking": scored,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({"n_screened": len(scored), "family_hits": len(family),
                      "controls": result["controls_paralogues"],
                      "flagged_liabilities": [r["gene"] for r in liabilities]}, indent=2))


if __name__ == "__main__":
    main()
