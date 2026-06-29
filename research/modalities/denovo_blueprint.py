#!/usr/bin/env python3
"""Pure selectivity-blueprint logic for the NR4A3 de-novo warhead campaigns (de-novo plan Step 1).

WHY. De-novo generation (DiffSBDD / Pocket2Mol) is pocket-conditioned: it places atoms to complement the
residues lining the binding site. To bias generation toward NR4A3-SELECTIVE chemotypes we must tell it
WHICH lining residues are the selectivity levers — the DIVERGENT handles that differ between NR4A3 and the
paralogues NR4A1/NR4A2 — versus the CONSERVED core that any NR4A binder will engage. A complementary PAN
campaign conditions on the conserved core. This module is the pure classification behind both; it has no
IO/structure dependency so it is unit-tested directly (TESTING.md #3).

KEY NUANCE (the selectivity asymmetry, already seen in the matrix run). A residue can be divergent vs ONE
paralogue but conserved vs the other — e.g. NR4A3 I531 is V in NR4A1 (divergent) but I in NR4A2 (identical).
Such a handle buys NR4A3-vs-NR4A1 selectivity only. So each engageable handle is tagged with which
paralogue(s) it discriminates; the selective campaign should weight handles that discriminate BOTH
(L406, T410, I484, L534) over single-paralogue levers (I531 → NR4A1 only). This is exactly the
"5 engageable vs NR4A1 but only 4 vs NR4A2" asymmetry recorded in nr4a3-degrader-next-steps.md.

WHAT. Given the orthosteric Pocket-5 residue records (from nr4a-selectivity.json) and the engageable set
(pocket-facing handles confirmed by the handle-facing run), classify_pocket() returns:
  - selective_handles: divergent AND engageable, each with the paralogue(s) it discriminates and a weight
    (2 = both paralogues, 1 = one) — the conditioning set for the SELECTIVE campaign.
  - divergent_non_engageable: divergent handles that splay out (T407, R412) — selectivity levers we CANNOT
    rely on for warhead contact; recorded so the generator is not conditioned on unreachable atoms.
  - conserved_core: non-divergent lining residues — the PAN campaign's conditioning set + the scaffold
    anchor residues for the selective campaign.
"""

PARALOGUES = ("nr4a1", "nr4a2")


def _resnum(label):
    """'I531' -> 531 (the integer residue number); None if no trailing digits."""
    digits = "".join(ch for ch in label if ch.isdigit())
    return int(digits) if digits else None


def classify_pocket(residues, engageable):
    """Classify orthosteric-pocket lining residues for de-novo conditioning.

    residues: list of {"nr4a3": "I531", "nr4a1": "V", "nr4a2": "I", "divergent": bool}
    engageable: iterable of NR4A3 residue LABELS (e.g. {"L406","T410","I484","I531","L534"}) confirmed
                pocket-facing in the druggable frames (handle-facing run). Matching is by residue NUMBER so
                a label like "I531" matches whether the engageable set uses "I531" or just 531.
    Returns a dict with selective_handles / divergent_non_engageable / conserved_core (+ summary counts).
    """
    eng_nums = set()
    for e in engageable:
        n = _resnum(e) if isinstance(e, str) else int(e)
        if n is not None:
            eng_nums.add(n)

    selective, div_non_eng, conserved = [], [], []
    for r in residues:
        label = r["nr4a3"]
        num = _resnum(label)
        nr4a3_aa = label[0] if label and label[0].isalpha() else None
        # Which paralogues this residue discriminates (differs from NR4A3 identity).
        discriminates = [p.upper() for p in PARALOGUES
                         if r.get(p) and r.get(p) != "-" and r.get(p) != nr4a3_aa]
        is_div = bool(r.get("divergent")) or bool(discriminates)
        if not is_div:
            conserved.append({"residue": label, "num": num})
            continue
        entry = {"residue": label, "num": num, "discriminates": discriminates,
                 "weight": len(discriminates),
                 "nr4a1": r.get("nr4a1"), "nr4a2": r.get("nr4a2")}
        if num in eng_nums:
            selective.append(entry)
        else:
            div_non_eng.append(entry)

    # Selective handles ranked: discriminate-both first (weight 2), then by residue number for determinism.
    selective.sort(key=lambda e: (-e["weight"], e["num"] if e["num"] is not None else 0))
    return {
        "selective_handles": selective,
        "divergent_non_engageable": div_non_eng,
        "conserved_core": conserved,
        "summary": {
            "n_selective_handles": len(selective),
            "n_discriminate_both": sum(1 for e in selective if e["weight"] == 2),
            "n_discriminate_nr4a1_only": sum(1 for e in selective
                                             if e["discriminates"] == ["NR4A1"]),
            "n_discriminate_nr4a2_only": sum(1 for e in selective
                                             if e["discriminates"] == ["NR4A2"]),
            "n_divergent_non_engageable": len(div_non_eng),
            "n_conserved_core": len(conserved),
        },
    }


def find_pocket(selectivity, pocket_number=5):
    """Return the residue records for a given fpocket pocket number from a loaded nr4a-selectivity.json
    dict, or None if absent."""
    for p in selectivity.get("nr4a3_lbd_pockets", []):
        if p.get("pocket") == pocket_number:
            return p
    return None
