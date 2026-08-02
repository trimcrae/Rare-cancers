#!/usr/bin/env python3
"""Domain-resolved census behind `manuscripts/target-route-options.md` (CPU, stdlib only, $0).

WHY THIS EXISTS
---------------
The route memo asks a target question rather than a method question: *must the molecule be
NR4A3-selective at all, and if so against what?*  Three of its findings are numbers, and
CLAUDE.md rule 1 / the roadmap's banner say a status or figure is READ from a committed
artifact and never typed into prose.  So this module owns them:

  1. **Domain-resolved paralogue identity.**  The claim "NR4A3 must discriminate two
     ~80%-identical paralogues" is a *blend* across domains that are nothing like each other.
     The roadmap already retracted the bare "~80% identical pocket" figure -- it was
     SMARCA2/SMARCA4, transplanted onto NR4A (map section 8, Route B).  This computes the
     per-domain numbers directly from the cached UniProt sequences so the memo can point at
     them instead of quoting a borrowed one.

  2. **The junction residue census.**  The EMC fusion swaps NR4A3's own N-terminal AF1 for
     EWSR1's low-complexity domain while keeping the LBD byte-identical.  Which lysines and
     cysteines that trades is a set-membership fact, and set membership is the one
     selectivity axis this program can state without a free-energy instrument.

  3. **The unreconciled fusion model.**  Two committed objects disagree about where NR4A3
     resumes in the chimera (`fusion_cofold.py` says residue 2; `fusion-breakpoint-
     neoantigens.json`'s exon-derived junctions say 318 / 361 / 419).  Under the second
     family NR4A3's AF1 -- and part or all of the zinc-finger DBD -- is absent from the
     fusion.  This emits both readings side by side so the disagreement is a value in an
     artifact rather than a sentence someone has to notice.

⛔ SCOPE.  Sequence arithmetic only.  Nothing here is a structure, an affinity, a
reachability, a reactivity or a degradation claim, and no efficacy, safety or clinical
statement follows from any of it.  The alignment is a plain affine-gap global alignment with
an identity/mismatch score -- adequate for a percent-identity readout between close
paralogues, and deliberately NOT used for residue-level correspondence (the committed
`nr4a-paralogue-unique-residues.json` owns that, with two independent aligners).

Run:  python3 research/modalities/target_route_census.py [--check]
Out:  research/modalities/target-route-census.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEQS = os.path.join(HERE, "nr4a-sequences-cache.json")
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
OUT = os.path.join(HERE, "target-route-census.json")

# Domain boundaries as the repo already calls them, from the AlphaFold/fpocket assessment
# (`nr4a3-structure-assessment.json` -> NR4A3.regions).  Kept byte-identical to that file so
# the two cannot drift.
NR4A3_REGIONS = {
    "AF1_N_terminal_disordered": (1, 260),
    "DNA_binding_domain": (261, 337),
    "hinge": (338, 372),
    "ligand_binding_domain": (373, 626),
}

# The DBD boundary above is an AlphaFold-confidence call and is offset from the actual zinc
# fingers, so identity over it understates the DBD's conservation.  The motif-anchored window
# below starts at the first C-x2-C-x2-C of the C4 zinc finger in each paralogue and runs 69
# residues, which is the same structural object in all three.
ZF_MOTIF = re.compile(r"C..C.{10,20}C..C")
ZF_WINDOW_LEN = 69

# The EWSR1 low-complexity / transactivation domain kept in the chimera, as
# `fusion_idr_features.py` defines it (Q01844, 1-264) and `fusion_cofold.py` cuts it.
EWSR1_LC = (1, 264)


# ---------------------------------------------------------------------------
# alignment
# ---------------------------------------------------------------------------
def align(a: str, b: str, match: int = 2, mis: int = -1, gap: int = -6, ext: int = -1):
    """Affine-gap global alignment (Gotoh).  Returns the two gapped strings."""
    n, m = len(a), len(b)
    neg = float("-inf")
    M = [[neg] * (m + 1) for _ in range(n + 1)]
    Ix = [[neg] * (m + 1) for _ in range(n + 1)]
    Iy = [[neg] * (m + 1) for _ in range(n + 1)]
    M[0][0] = 0
    for i in range(1, n + 1):
        Ix[i][0] = gap + ext * (i - 1)
    for j in range(1, m + 1):
        Iy[0][j] = gap + ext * (j - 1)
    for i in range(1, n + 1):
        ai = a[i - 1]
        Mi, Mp, Ixi, Ixp, Iyi = M[i], M[i - 1], Ix[i], Ix[i - 1], Iy[i]
        Iyp = Iy[i - 1]
        for j in range(1, m + 1):
            sc = match if ai == b[j - 1] else mis
            Mi[j] = max(Mp[j - 1], Ixp[j - 1], Iyp[j - 1]) + sc
            Ixi[j] = max(Mp[j] + gap, Ixp[j] + ext)
            Iyi[j] = max(Mi[j - 1] + gap, Iyi[j - 1] + ext)

    i, j = n, m
    state = max((("M", M[n][m]), ("X", Ix[n][m]), ("Y", Iy[n][m])), key=lambda t: t[1])[0]
    A: list[str] = []
    B: list[str] = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and state == "M":
            A.append(a[i - 1])
            B.append(b[j - 1])
            sc = match if a[i - 1] == b[j - 1] else mis
            prev = M[i][j] - sc
            i -= 1
            j -= 1
            if M[i][j] == prev:
                state = "M"
            elif Ix[i][j] == prev:
                state = "X"
            else:
                state = "Y"
        elif i > 0 and state == "X":
            A.append(a[i - 1])
            B.append("-")
            cur = Ix[i][j]
            i -= 1
            state = "M" if M[i][j] + gap == cur else "X"
        elif j > 0 and state == "Y":
            A.append("-")
            B.append(b[j - 1])
            cur = Iy[i][j]
            j -= 1
            state = "M" if M[i][j] + gap == cur else "Y"
        elif i > 0:
            A.append(a[i - 1])
            B.append("-")
            i -= 1
        else:
            A.append("-")
            B.append(b[j - 1])
            j -= 1
    return "".join(reversed(A)), "".join(reversed(B))


def identity(A: str, B: str, lo=None, hi=None):
    """Percent identity over aligned columns, optionally restricted to a residue range of A."""
    ia = 0
    n_col = 0
    n_id = 0
    for x, y in zip(A, B):
        if x != "-":
            ia += 1
        if lo is not None and (x == "-" or not (lo <= ia <= hi)):
            continue
        if x == "-" and y == "-":
            continue
        n_col += 1
        if x == y and x != "-":
            n_id += 1
    return {
        "n_identical": n_id,
        "n_aligned_columns": n_col,
        "pct_identity": round(100.0 * n_id / n_col, 1) if n_col else None,
    }


def zinc_finger_window(seq: str):
    m = ZF_MOTIF.search(seq)
    if not m:
        return None
    start = m.start()
    return {"start_residue": start + 1, "seq": seq[start:start + ZF_WINDOW_LEN]}


def positions(seq: str, aa: str, lo: int, hi: int):
    return [i + 1 for i, c in enumerate(seq) if c == aa and lo <= i + 1 <= hi]


# ---------------------------------------------------------------------------
def build():
    seqs = json.load(open(SEQS))
    n3, n1, n2, ews = seqs["NR4A3"], seqs["NR4A1"], seqs["NR4A2"], seqs["EWSR1"]

    # --- 1. domain-resolved identity -------------------------------------------------
    ident = {}
    for name, other in (("NR4A1", n1), ("NR4A2", n2)):
        A, B = align(n3, other)
        row = {"full_length": identity(A, B)}
        for dom, (lo, hi) in NR4A3_REGIONS.items():
            row[dom] = identity(A, B, lo, hi)
        ident[f"NR4A3_vs_{name}"] = row

    zf = {p: zinc_finger_window(s) for p, s in (("NR4A3", n3), ("NR4A1", n1), ("NR4A2", n2))}
    zf_ident = {}
    for name in ("NR4A1", "NR4A2"):
        a, b = zf["NR4A3"]["seq"], zf[name]["seq"]
        k = sum(1 for x, y in zip(a, b) if x == y)
        zf_ident[f"NR4A3_vs_{name}"] = {
            "n_identical": k,
            "n_aligned_columns": min(len(a), len(b)),
            "pct_identity": round(100.0 * k / min(len(a), len(b)), 1),
        }

    # --- 2. junction residue census --------------------------------------------------
    census = {"NR4A3": {}, "EWSR1_LC_kept_in_fusion": {}}
    for dom, (lo, hi) in NR4A3_REGIONS.items():
        census["NR4A3"][dom] = {
            "residues": f"{lo}-{hi}",
            "lysines": positions(n3, "K", lo, hi),
            "cysteines": positions(n3, "C", lo, hi),
            "n_lysines": len(positions(n3, "K", lo, hi)),
            "n_cysteines": len(positions(n3, "C", lo, hi)),
        }
    lo, hi = EWSR1_LC
    census["EWSR1_LC_kept_in_fusion"] = {
        "residues": f"{lo}-{hi}",
        "source": "fusion_idr_features.py (Q01844 1-264, prion-like LC/TAD); fusion_cofold.py EWS_CUT=264",
        "lysines": positions(ews, "K", lo, hi),
        "cysteines": positions(ews, "C", lo, hi),
        "n_lysines": len(positions(ews, "K", lo, hi)),
        "n_cysteines": len(positions(ews, "C", lo, hi)),
    }
    swap = {
        "_question": "What does the chimera trade when EWSR1-LC replaces NR4A3's own AF1?",
        "nr4a3_af1_lysines": census["NR4A3"]["AF1_N_terminal_disordered"]["n_lysines"],
        "ewsr1_lc_lysines": census["EWSR1_LC_kept_in_fusion"]["n_lysines"],
        "nr4a3_af1_cysteines": census["NR4A3"]["AF1_N_terminal_disordered"]["n_cysteines"],
        "ewsr1_lc_cysteines": census["EWSR1_LC_kept_in_fusion"]["n_cysteines"],
        "nr4a3_af1_cysteine_positions": census["NR4A3"]["AF1_N_terminal_disordered"]["cysteines"],
        "_reading": (
            "Byte-identical LBD, different N-terminal acceptor set. This is the only "
            "categorical fusion-vs-wild-type difference a shared-LBD binder could exploit, "
            "and whether it is reachable is a ternary-geometry question, not a binding one."
        ),
    }

    # --- 3. the unreconciled fusion model --------------------------------------------
    bp = json.load(open(BREAKPOINTS))
    exon_derived = sorted({j["nr4_cds_nt"] // 3 + 1 for j in bp["junctions"]})
    models = {
        "_question": "Where does NR4A3 resume in the chimera? Two committed objects disagree.",
        "model_A_fusion_cofold": {
            "source": "fusion_cofold.py (EWS_CUT=264, 'NR4A3 resumed at res 2')",
            "nr4a3_first_residue": 2,
            "self_declared_status": (
                "fusion_breakpoints.py's own docstring calls this 'an assumption, not a "
                "sourced breakpoint'"
            ),
            "nr4a3_af1_present": True,
            "nr4a3_dbd_present": True,
            "c166_present_in_fusion": True,
        },
        "model_B_exon_derived": {
            "source": "fusion-breakpoint-neoantigens.json (Ensembl exon structure, 7 in-frame junctions)",
            "nr4a3_first_residues": exon_derived,
            "nr4a3_af1_present": False,
            "nr4a3_dbd_present": "partial or absent (the C4 zinc finger begins at NR4A3 C292)",
            "c166_present_in_fusion": False,
        },
        "_discriminating_evidence_already_in_repo": (
            "The fusion binds a response element in the PPARG promoter and transactivates it "
            "(Filion 2009, PMC4429309, cited in nr4a3-emc-biology-evidence.md hypothesis 2 "
            "pillar 2) -- a DNA-binding-domain-dependent function. Model B's resume points "
            "(>=318) truncate or delete the zinc-finger DBD, so the two models cannot both "
            "be right and the DBD evidence bears against model B as written."
        ),
        "_why_it_matters": (
            "Requirement R13 on the roadmap ('the modelled object is the real biological "
            "object') has no rung, no gate and no price. Which model holds decides whether "
            "NR4A3's C166 exists in the disease protein at all, and every junction-derived "
            "neoepitope in fusion-breakpoint-neoantigens.json is conditional on it."
        ),
        "_named_zero_dollar_test": (
            "Re-derive NR4A3's coding-exon offsets from the MANE transcript in CI and check "
            "fusion_breakpoints.py's resume index (`offsets[n-2]`), which assumes exon 2 is "
            "the first coding exon; then pin the EMC junction against a primary breakpoint "
            "report rather than either model. Networked, so GitHub Actions, not the sandbox."
        ),
    }

    return {
        "_title": "Target-route census -- domain-resolved paralogue identity, the junction residue swap, and the unreconciled fusion model",
        "_owner": "research/manuscripts/target-route-options.md",
        "_method": (
            "Pure-stdlib. Sequences read from nr4a-sequences-cache.json (UniProt Q92570 / "
            "P22736 / P43354 / Q01844). Identity from an affine-gap global alignment "
            "(match +2 / mismatch -1 / open -6 / extend -1), reported per NR4A3 domain "
            "using the boundaries in nr4a3-structure-assessment.json. The zinc-finger row "
            "is a motif-anchored ungapped window (first C-x2-C-x2-C, 69 aa) because the "
            "AlphaFold-confidence DBD boundary is offset from the actual fingers."
        ),
        "_limits": [
            "Percent identity only. No structure, affinity, reach, reactivity or degradation quantity is computed.",
            "Residue-level paralogue correspondence is NOT taken from this alignment -- nr4a-paralogue-unique-residues.json owns that, with two independent aligners and an alignment-robustness rule.",
            "The fusion-model section reports a disagreement between two committed objects. It does not resolve it, and neither reading may be quoted as the fusion's structure.",
            "No efficacy, safety, tolerability, therapeutic-window or clinical claim is made or implied.",
        ],
        "sequence_lengths": {k: len(v) for k, v in seqs.items()},
        "paralogue_identity_by_domain": ident,
        "zinc_finger_window": {
            "window_length": ZF_WINDOW_LEN,
            "starts": {p: v["start_residue"] for p, v in zf.items()},
            "identity": zf_ident,
        },
        "junction_residue_census": census,
        "af1_to_lc_swap": swap,
        "fusion_model_disagreement": models,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="regenerate and fail if the committed artifact differs")
    args = ap.parse_args(argv)

    result = build()
    text = json.dumps(result, indent=1) + "\n"

    if args.check:
        if not os.path.exists(OUT):
            print(f"MISSING: {OUT}", file=sys.stderr)
            return 1
        if open(OUT).read() != text:
            print(f"STALE: {OUT} differs from a fresh run", file=sys.stderr)
            return 1
        print(f"OK: {os.path.basename(OUT)} reproduces")
        return 0

    with open(OUT, "w") as fh:
        fh.write(text)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
