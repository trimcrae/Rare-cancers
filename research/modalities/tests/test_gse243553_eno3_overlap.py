"""Offline guards for the GSE243553 x ENO3-NBRE overlap module.

Everything asserted here is arithmetic or bookkeeping that can be checked with NO network, and
each one corresponds to a way the module could emit a number nobody could grade:

  * a coordinate that was TYPED rather than derived from the committed motif scan;
  * a strand convention assumed rather than read (this already failed once — see the module);
  * a build mismatch that would make an intersection meaningless;
  * a failed fetch rendering as an empty result, i.e. an absent reading read as absence
    (CLAUDE.md §4).
"""

import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD_DIR))
assert os.path.isdir(os.path.join(REPO, ".github")), (
    f"REPO resolved to {REPO}, which has no .github/ — the path arithmetic is wrong and every "
    f"test in this file would be testing a missing file")

import sys                                                            # noqa: E402
sys.path.insert(0, MOD_DIR)
import gse243553_eno3_overlap as M                                    # noqa: E402


# ───────────────────────────────────────────────────────────────────────────────────────────────
# the coordinates
# ───────────────────────────────────────────────────────────────────────────────────────────────

def test_the_eno3_coordinates_are_derived_from_the_committed_scan_not_typed():
    """⛔ The one home for these coordinates is `emc-ret-target-scan.json`. If this module ever
    carries a literal chr17 coordinate, the two can drift and the paper would quote whichever
    copy the reader found first (CLAUDE.md §1)."""
    src = open(os.path.join(MOD_DIR, "gse243553_eno3_overlap.py"), encoding="utf-8").read()
    # 4,9xx,xxx — any ENO3-locus-shaped literal in the source is the failure this catches
    import re
    bad = re.findall(r"\b49[0-9]{5}\b", src)
    assert not bad, f"a literal ENO3-locus coordinate is typed into the module: {bad}"


def test_every_derived_site_round_trips_against_the_artifacts_own_offset():
    e = M.load_nbre_sites("ENO3")
    scan = json.load(open(M.MOTIF_SCAN_ARTIFACT, encoding="utf-8"))
    hits = scan["part_1_nbre_scan"]["focus_genes"]["ENO3"]["nbre_exact"]["hits"]
    assert len(e["sites"]) == len(hits) == e["n_exact_nbre"]
    for site, hit in zip(e["sites"], hits):
        assert site["offset_from_tss"] == hit["offset_from_tss"]
        assert site["end"] - site["start"] == M.NBRE_LEN


def test_the_strand_of_the_window_is_read_not_assumed():
    """The scan's window is strand-aware (upstream 10 kb / downstream 15 kb, mirrored on the minus
    strand) while its `offset_from_tss` is a plain genomic difference. Both conventions are
    load-bearing and neither is written down anywhere else, so they are pinned here.

    ENO3, PPARG, RET, NR4A3, NR4A1 and VEGFA are plus-strand in the artifact's own window
    arithmetic; SEMA3C and KDR are minus-strand. A change to either convention flips one of these
    and fails the build rather than silently moving every coordinate."""
    strands = {g: M.load_nbre_sites(g)["gene_strand_derived"]
               for g in ("ENO3", "PPARG", "SEMA3C", "RET", "NR4A3", "NR4A1", "VEGFA", "KDR")}
    assert strands == {"ENO3": "+", "PPARG": "+", "SEMA3C": "-", "RET": "+",
                       "NR4A3": "+", "NR4A1": "+", "VEGFA": "+", "KDR": "-"}, strands


def test_a_gene_whose_window_matches_no_orientation_raises_rather_than_guessing():
    scan = json.load(open(M.MOTIF_SCAN_ARTIFACT, encoding="utf-8"))
    import copy, tempfile
    broken = copy.deepcopy(scan)
    g = broken["part_1_nbre_scan"]["focus_genes"]["ENO3"]
    g["window"] = [g["window"][0] + 7, g["window"][1]]      # not a -10k/+15k window either way
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(broken, fh)
        path = fh.name
    try:
        with pytest.raises(AssertionError):
            M.load_nbre_sites("ENO3", artifact=path)
    finally:
        os.unlink(path)


def test_the_declared_build_is_grch38_so_a_cross_build_intersection_is_detectable():
    """An overlap computed across builds is meaningless. The scan's build must be READABLE from
    the artifact — never defaulted — so the analysis can refuse when the deposit disagrees."""
    e = M.load_nbre_sites("ENO3")
    assert e["assembly"] == "GRCh38"
    assert e["chrom"] == "chr17"


# ───────────────────────────────────────────────────────────────────────────────────────────────
# an absent reading is not a reading of absence
# ───────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("rec", [
    {"state": "not_retrieved", "http": 502, "text": None},
    {"state": "not_retrieved", "http": 404, "text": '<a href="GSM1_peaks.bed.gz">peaks</a>'},
    {"state": "budget_exhausted", "http": None, "text": None},
])
def test_a_failed_fetch_never_renders_as_an_empty_file_listing(rec):
    assert M._dir_listing(rec) == [], (
        "a non-OK fetch produced a file listing; 'GEO holds no peak call' and 'we could not read "
        "GEO' would then be indistinguishable")


def test_an_ok_fetch_does_parse_its_listing():
    rec = {"state": "ok", "http": 200,
           "text": '<a href="../">up</a><a href="GSM1_peaks.bed.gz">x</a>'
                   '<a href="GSM1_fragments.tsv.gz">y</a>'}
    assert M._dir_listing(rec) == ["GSM1_fragments.tsv.gz", "GSM1_peaks.bed.gz"]


def test_the_build_scanner_counts_it_does_not_decide():
    c = M.scan_for_build("aligned with cellranger-atac to hg38; earlier runs used hg19")
    assert c["hg38"] == 1 and c["hg19"] == 1 and c["GRCh37"] == 0


def test_truncation_of_a_stored_response_is_marked_never_silent():
    out = M._slim({"url": "u", "state": "ok", "http": 200, "bytes": 10, "text": "x" * 50}, 10)
    assert out["text"] == "x" * 10
    assert out["text_truncated_at_chars"] == 10 and out["text_full_len"] == 50


def test_the_two_constraints_are_carried_in_the_artifact_not_only_in_prose():
    """⛔ Both must survive into the machine-readable output, because a reader who quotes only the
    result is exactly the reader who would drop them."""
    src = open(os.path.join(MOD_DIR, "gse243553_eno3_overlap.py"), encoding="utf-8").read()
    i = src.index("_constraints_that_travel_with_every_result")
    block = src[i:i + 1400]
    assert "HEK293T" in block and "not EMC" in block
    assert "POSITIVE CONTROL" in block and "VALIDATES" in block
