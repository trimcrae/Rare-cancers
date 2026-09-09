#!/usr/bin/env python3
"""End-to-end check of the UNAPPLIED zero-partner diff, run against a PATCHED COPY of
`fusion_breakpoints.py` on a symlink mirror of `research/modalities` — the shared tracked file in
the checkout is NOT modified.

It drives the real `emit_junction` over the real transcript model (TRANSCRIPT_SOURCE=cache, no
network) and requires that the patched code reproduces, from the code path itself, exactly what
`refiltered-panel.json` computed from the committed artifact: the same 5 junctions, the same 174
distinct novel peptides, the same 8 zero-EWSR1 and 20 zero-NR4A3 peptides, and `novel_peptides`
byte-for-byte unchanged against the committed artifact.

⛔ Screen configuration only. No presentation, immunogenicity, safety or clinical claim.
"""
import json
import os
import sys

MIRROR = sys.argv[1]
sys.path.insert(0, os.path.join(MIRROR, "research/modalities"))
os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")

import fusion_breakpoints as fb            # noqa: E402  (the PATCHED copy)
import junction_aso as ja                  # noqa: E402

assert os.path.realpath(fb.__file__).startswith(os.path.realpath(MIRROR)), fb.__file__
assert hasattr(fb, "partner_residue_split")

committed = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        *[".."] * 6,
                                        "research/modalities/fusion-breakpoint-neoantigens.json")))
panel = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "refiltered-panel.json")))

ews, nr4 = ja.transcript_model("EWSR1"), ja.transcript_model("NR4A3")
graded = ja.graded_window(ews, nr4, keep_sequences=True)
rows = [fb.emit_junction(ews, nr4, j) for j in graded if j["grade"] == ja.EMITTABLE]
print("emitted junctions:", len(rows))

old = {j["junction_label"]: j for j in committed["junctions"]}
assert sorted(old) == sorted(r["junction_label"] for r in rows)
for r in rows:
    assert r["novel_peptides"] == old[r["junction_label"]]["novel_peptides"], (
        r["junction_label"] + ": the diff changed novel_peptides, which it must not")
    assert r["n_novel_peptides"] == old[r["junction_label"]]["n_novel_peptides"]
    assert (r["n_junction_specific_peptides"] + r["n_zero_partner_peptides"]
            == r["n_novel_peptides"])

zero5 = sorted({p for r in rows for p, why in r["zero_partner_peptides"].items()
                if why == "zero_from_5p_partner"})
zero3 = sorted({p for r in rows for p, why in r["zero_partner_peptides"].items()
                if why == "zero_from_3p_partner"})
both = sorted({p for r in rows for p, why in r["zero_partner_peptides"].items()
               if why == "zero_from_both_partners"})
all_peps = sorted({p for r in rows for p in r["novel_peptides"]})
print("distinct novel peptides:", len(all_peps))
print("zero-EWSR1 (5' partner):", len(zero5), zero5)
print("zero-NR4A3 (3' partner):", len(zero3))
print("zero from both:", len(both), both)

assert len(all_peps) == panel["_denominators"]["junction_peptides"] == 174
assert zero5 == panel["peptide_arm"]["zero_from_EWSR1"], (zero5, panel["peptide_arm"]["zero_from_EWSR1"])
assert zero3 == panel["peptide_arm"]["zero_from_NR4A3"], (zero3, panel["peptide_arm"]["zero_from_NR4A3"])
assert not both
print("PATCHED CODE PATH AGREES WITH refiltered-panel.json ON EVERY COUNT")
