#!/usr/bin/env python3
"""
Candidate vaccine construct for the EWSR1::NR4A3 fusion junction.

This turns the epitope predictions into something a wet lab could actually order: the
minimal junction-spanning synthetic long peptide (SLP) that carries the strong CD8 and CD4
epitopes, plus a multi-epitope "string-of-beads" alternative. It is an ENGINEERING PROPOSAL,
not a validated immunogen — predicted binding is a screen, not proof of immunogenicity.

Inputs (committed, no network):
  - fusion-breakpoint-neoantigens.json : per-junction CD8/class-I strong binders.
  - patient-cd4-demo.json              : CD4/class-II (DRB1) strong helpers (e7::e3 junction).

Method:
  1. Reconstruct the local fusion sequence around each junction by greedy overlap-assembly
     of all junction-spanning peptides (they are substrings of one contiguous window).
  2. SLP: the shortest contiguous span of that window containing every selected strong
     epitope. A single junction-spanning SLP keeps CD8 + CD4 epitopes in their native
     context (so processing can recreate them) and is the simplest real immunogen.
  3. String-of-beads: distinct strong epitopes concatenated with cleavage-favouring
     linkers (AAY between CD8 minimal epitopes; GPGPG flanking CD4 epitopes) — the standard
     multi-epitope design [Livingston 2002 (AAY); used widely for GPGPG class-II spacers].

Output: vaccine-construct.json
"""

import json
import os
import sys

HERE = os.path.dirname(__file__)
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
CD4_DEMO = os.path.join(HERE, "patient-cd4-demo.json")
OUT = os.path.join(HERE, "vaccine-construct.json")

CD8_LINKER = "AAY"      # favours C-terminal proteasomal cleavage between class-I epitopes
CD4_SPACER = "GPGPG"    # flexible spacer that limits junctional (neo-)epitopes for class II


def _overlap(a, b):
    for k in range(min(len(a), len(b)), 0, -1):
        if a[-k:] == b[:k]:
            return k
    return 0


def assemble(peptides):
    """Greedy overlap-assembly of substrings of one contiguous window -> the window."""
    seqs = sorted(peptides, key=len, reverse=True)
    contig = seqs[0]
    changed = True
    while changed:
        changed = False
        for s in seqs:
            if s in contig:
                continue
            oab, oba = _overlap(contig, s), _overlap(s, contig)
            if oab >= 4 and oab >= oba:
                contig, changed = contig + s[oab:], True
            elif oba >= 4:
                contig, changed = s + contig[oba:], True
    return contig


def min_span(contig, epitopes):
    """Shortest substring of contig covering all epitope peptides (all must be present)."""
    idx = [(contig.find(p), contig.find(p) + len(p)) for p in epitopes]
    if any(i[0] < 0 for i in idx):
        return None
    lo, hi = min(i[0] for i in idx), max(i[1] for i in idx)
    return {"sequence": contig[lo:hi], "length": hi - lo, "start_in_window": lo}


def string_of_beads(cd8, cd4):
    """Distinct strong epitopes -> linker-joined multi-epitope construct."""
    cd8_eps = sorted({p for p, _ in cd8})
    cd4_eps = sorted({p for p, _ in cd4})
    parts = []
    if cd8_eps:
        parts.append(CD8_LINKER.join(cd8_eps))
    seq = (CD8_LINKER.join([p for p in cd8_eps]) if cd8_eps else "")
    # CD4 epitopes flanked by GPGPG spacers, appended after the CD8 block
    cd4_block = CD4_SPACER + CD4_SPACER.join(cd4_eps) + CD4_SPACER if cd4_eps else ""
    construct = (seq + cd4_block) if seq else cd4_block.strip(CD4_SPACER)
    return {"sequence": construct, "length": len(construct),
            "cd8_epitopes": cd8_eps, "cd4_epitopes": cd4_eps,
            "linkers": {"cd8": CD8_LINKER, "cd4_spacer": CD4_SPACER}}


def main():
    bp = json.load(open(BREAKPOINTS))
    cd4d = json.load(open(CD4_DEMO))

    # CD4 strong helpers (the demo is the EWSR1 e7 :: NR4A3 e3 junction)
    cd4_strong = [(r["peptide"], r["allele"]) for r in cd4d.get("all_predictions", [])
                  if r.get("call") == "strong"]
    cd4_peps_all = {r["peptide"] for r in cd4d.get("all_predictions", [])}
    cd4_src = cd4d.get("source", {})

    constructs = []
    for jn in bp.get("junctions", []):
        cd8_strong = [(b["peptide"], b["allele"]) for b in jn.get("binders", [])
                      if b.get("class") == "strong"]
        if not cd8_strong:
            continue
        is_e7e3 = (jn.get("EWSR1_exon_end") == 7 and jn.get("NR4A3_exon_start") == 3)
        # window = junction-spanning CD8 peptides (+ CD4 peptides for the e7::e3 junction)
        window_peps = set(jn.get("novel_peptides", []))
        these_cd4 = cd4_strong if is_e7e3 else []
        if is_e7e3:
            window_peps |= cd4_peps_all
        contig = assemble(window_peps)
        seam = None
        ctx = jn.get("junction_context", "")
        if "|" in ctx:
            right = ctx.split("|", 1)[1][:6]
            seam = contig.find(right) if right and right in contig else None
        selected = cd8_strong + these_cd4
        slp = min_span(contig, [p for p, _ in selected])
        constructs.append({
            "junction": f"EWSR1 e{jn['EWSR1_exon_end']} :: NR4A3 e{jn['NR4A3_exon_start']}",
            "is_public_lead": is_e7e3,
            "assembled_window": contig,
            "seam_index": seam,
            "seam_context": ctx,
            "cd8_strong_epitopes": [{"peptide": p, "allele": a} for p, a in cd8_strong],
            "cd4_strong_epitopes": [{"peptide": p, "allele": a} for p, a in these_cd4],
            "minimal_SLP": slp,
            "string_of_beads": string_of_beads(cd8_strong, these_cd4),
        })

    lead = next((c for c in constructs if c["is_public_lead"]), None)
    result = {
        "_note": "Candidate vaccine constructs for EWSR1::NR4A3 junction neoepitopes. "
                 "ENGINEERING PROPOSAL from in-silico epitope predictions — NOT a validated "
                 "immunogen; predicted binding is a screen, not proof of immunogenicity. The "
                 "minimal SLP keeps CD8+CD4 epitopes in native junction context; the "
                 "string-of-beads is an alternative multi-epitope design with cleavage "
                 "linkers (AAY for class I, GPGPG spacers for class II).",
        "_inputs": {"cd8": os.path.basename(BREAKPOINTS), "cd4": os.path.basename(CD4_DEMO),
                    "cd4_junction": cd4_src},
        "lead_public_construct": lead,
        "all_junction_constructs": constructs,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    print("wrote", OUT, file=sys.stderr)
    if lead:
        slp = lead["minimal_SLP"]
        print(json.dumps({
            "lead_junction": lead["junction"],
            "minimal_SLP": slp["sequence"] if slp else None,
            "SLP_length": slp["length"] if slp else None,
            "carries_CD8": [e["allele"] for e in lead["cd8_strong_epitopes"]],
            "carries_CD4": [e["allele"] for e in lead["cd4_strong_epitopes"]],
            "string_of_beads_len": lead["string_of_beads"]["length"],
        }, indent=2))


if __name__ == "__main__":
    main()
