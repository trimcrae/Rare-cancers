#!/usr/bin/env python3
"""NEOANTIGEN-7 · independent cross-derivation of the 20, by a route that does NOT use
junction_context placement.

Method 2: for each in-frame junction, take the held canonical EWSR1 sequence and the panel's own
`donor_last_whole_residue`, and rebuild the EWSR1 side of the seam directly from the sequence. A
zero-NR4A3 peptide must then be exactly (a suffix of canonical EWSR1 ending at
donor_last_whole_residue) + the seam residue. If method 1 and method 2 disagree on the membership of
the class, that disagreement is the finding.

No network. No isoform sequence is fetched, substituted or reconstructed.
"""
from __future__ import annotations

import json
import os
import sys

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research", "modalities")
LANE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    panel = json.load(open(os.path.join(MOD, "fusion-breakpoint-neoantigens.json"), encoding="utf-8"))
    ews = json.load(open(os.path.join(MOD, "fet-sequences-cache.json"), encoding="utf-8"))["EWSR1"]
    mine = json.load(open(os.path.join(LANE, "neoantigen7-zero-nr4a3-bounding.json"), encoding="utf-8"))
    method1 = set(mine["step1_zero_NR4A3_peptides"])

    method2 = set()
    detail = []
    for j in panel["junctions"]:
        last = j["donor_last_whole_residue"]          # 1-based residue index into canonical EWSR1
        seam = j["seam_codon_residue"]
        for pep in j["novel_peptides"]:
            body, tail = pep[:-1], pep[-1]
            if tail != seam or not body:
                continue
            # the peptide is zero-NR4A3 iff its body is exactly the canonical EWSR1 window
            # ending at donor_last_whole_residue
            window = ews[last - len(body):last]
            if window == body:
                method2.add(pep)
                detail.append({"peptide": pep, "junction": j["junction_label"],
                               "ewsr1_window_1based": [last - len(body) + 1, last],
                               "seam_residue": seam,
                               "wild_type_residue_after_donor_cut": ews[last] if last < len(ews) else None})

    agree = method1 == method2
    out = {
        "_what": "Independent re-derivation of the zero-NR4A3 class from the held canonical EWSR1 "
                 "sequence plus the panel's own donor_last_whole_residue, without using "
                 "junction_context placement.",
        "n_method1_context_placement": len(method1),
        "n_method2_sequence_anchored": len(method2),
        "agree": agree,
        "only_in_method1": sorted(method1 - method2),
        "only_in_method2": sorted(method2 - method1),
        "per_peptide": sorted(detail, key=lambda d: d["peptide"]),
        "⛔_reading": "This is a composition/placement fact about the held CANONICAL sequence only. "
                     "It says nothing about any isoform, and nothing about presentation or "
                     "immunogenicity.",
    }
    dest = os.path.join(LANE, "neoantigen7-independent-derivation.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("method1 (context placement): %d" % len(method1))
    print("method2 (sequence anchored): %d" % len(method2))
    print("agree:", agree, "| only_in_1:", sorted(method1 - method2), "| only_in_2:", sorted(method2 - method1))
    print("wrote", dest)
    return 0 if agree else 1


if __name__ == "__main__":
    sys.exit(main())
