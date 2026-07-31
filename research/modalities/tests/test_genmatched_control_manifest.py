#!/usr/bin/env python3
"""The generation-matched null's control-(c) receptor manifest — is it boxed on the RIGHT residues?

★ THE TRAP THIS GUARDS, WHICH IS NOT HYPOTHETICAL. The control pocket has to be the NR4A1 homologue of the
NR4A3 pocket the real campaign generated into, or the control is not matched and its false-positive rate
means nothing. Two committed NR4A1 artifacts describe that pocket — the LANE-13 release ensemble (which
carries `cv_residues` in UniProt numbering) and the matrix's opened conformer (which is renumbered) — and
THEY DO NOT SHARE A NUMBERING. Feeding one artifact's residue numbers to the other silently boxes ten wrong
residues and reports success, which is the same shape as the positional chain split that cost the NR-V04
covalent panel its whole spend.

So the box is not carried as a remembered list: it is RE-DERIVED here by matching residue IDENTITIES, and
the test asserts that exactly one alignment reproduces all ten. One hit out of hundreds of candidate offsets
is a resolution; several hits, or a partial match, would be a fit and must fail.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))

ENSEMBLE = os.path.join(REPO, "results", "nr4a1-pocket-ensemble", "release_summary.json")
RECEPTOR = os.path.join(REPO, "results", "nr4a3-genmatched-control-c", "nr4a1-opened.pdb")
MANIFEST = os.path.join(REPO, "results", "nr4a3-genmatched-control-c", "nr4a3-release-druggable.json")

pytestmark = pytest.mark.skipif(not os.path.exists(RECEPTOR), reason="control receptor not staged")


def _ca_names(pdb):
    out = {}
    with open(pdb) as fh:
        for ln in fh:
            if ln.startswith("ATOM") and ln[12:16].strip() == "CA":
                out[int(ln[22:26])] = ln[17:20].strip()
    return out


def _matching_offsets():
    ens = json.load(open(ENSEMBLE))
    cv, ident = ens["cv_residues"], ens["cv_identities"]
    want = [ident[str(c)] for c in cv]
    names = _ca_names(RECEPTOR)
    return cv, want, [o for o in range(400)
                      if all((c - o) in names for c in cv)
                      and [names[c - o] for c in cv] == want]


def test_exactly_one_alignment_reproduces_all_ten_pocket_residues():
    """A UNIQUE offset is the whole basis for trusting the box. If a second one appears, identity matching has
    stopped discriminating and the box must be re-derived some other way — not picked."""
    cv, want, hits = _matching_offsets()
    assert len(hits) == 1, f"expected exactly one alignment, got {hits} (a fit, not a resolution)"
    assert len(want) == len(cv) == 10


def test_the_committed_manifest_boxes_exactly_those_residues():
    """The manifest must agree with what the identities say, not with what someone typed."""
    cv, _want, hits = _matching_offsets()
    derived = [c - hits[0] for c in cv]
    man = json.load(open(MANIFEST))
    box = man["receptors"][0]["box_residues"]
    assert box == derived, f"manifest boxes {box}, identity matching says {derived}"


def test_the_box_residues_exist_in_the_receptor_it_names():
    man = json.load(open(MANIFEST))
    rec = man["receptors"][0]
    assert rec["pdb"] == os.path.basename(RECEPTOR)
    names = _ca_names(RECEPTOR)
    missing = [r for r in rec["box_residues"] if r not in names]
    assert not missing, f"manifest boxes residues absent from its own receptor: {missing}"


def test_the_manifest_records_that_the_control_is_NR4A1_and_says_how_the_box_was_derived():
    """Provenance is the point: a control pocket with no recorded derivation is indistinguishable from a
    guessed one, and this manifest feeds a generation job that nothing downstream re-checks."""
    man = json.load(open(MANIFEST))
    g = man["_genmatched_null"]
    assert g["target"] == "NR4A1"
    assert "offset" in g["source"] and "identity" in g["source"].lower()
