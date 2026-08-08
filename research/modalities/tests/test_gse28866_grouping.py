"""GSE28866's column-role derivation, exercised against the REAL header. ($0, stdlib, offline)

⛔ WHY THIS TEST EXISTS AND WHAT IT ALREADY CAUGHT. `_groups` and `_extract` were both committed to
`gse28866_tumour_vs_normal.py` while `main()` called NEITHER — the artifact went on reporting a bare
header read and the commit message claimed a grouping. Wiring them up then exposed a second defect the
same minute: `main` hands `_groups` the 96 columns `_classify_columns` labelled samples, `_extract`
hands it the raw 100-field header, and a name-only annotation drop returned **93 libraries for one
caller and 97 for the other**. Same function, same file, two groupings, one of them wrong.

⚠ THE HEADER IS NOT SYNTHESISED. It is read from the CI-published artifact, so the derivation is
tested against the exact strings the deposit carries — including the trailing `\\r` on the final
column, which a `$`-anchored pattern silently drops. Values ARE synthetic and are only ever used to
check the arithmetic, never quoted anywhere.
"""
import gzip
import io
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import gse28866_tumour_vs_normal as m  # noqa: E402

ARTIFACT = os.path.join(MOD, "gse28866-tumour-vs-normal.json")

#: The seven annotation columns, in the order the deposit carries them.
ANN = ["peak", "hg18_coords", "classification", "gene_id", "gene_symbol",
       "peak_exon_gene_symbol", "differentially_expressed_cancer_type"]


def _real_header():
    if not os.path.exists(ARTIFACT):
        pytest.skip("artifact not published yet")
    doc = json.load(open(ARTIFACT, encoding="utf-8"))
    nrm = [s for s in doc["sources"] if s["id"] == "normalized_36048_peaks"]
    if not nrm or not nrm[0].get("columns"):
        pytest.skip("normalized table not read in the published artifact")
    # `sample_columns` opens with the three annotation columns `_classify_columns` could not shape-
    # detect; the libraries follow.
    return ANN + nrm[0]["columns"]["sample_columns"][3:]


def test_the_grouping_is_identical_for_both_callers():
    """⛔ The regression that motivated the whole file: 93 vs 97 depending on who asked."""
    header = _real_header()
    # `_extract` hands over the raw header; `main` hands over what `_classify_columns` called
    # samples, which is the header minus the four shape-detectable annotation columns.
    as_extract_sees_it = m._groups(header)
    as_main_sees_it = m._groups(m._classify_columns(header)["sample_columns"])
    assert len(as_extract_sees_it["normal_columns"]) == 27
    for k in ("n_libraries", "n_tumour", "n_normal", "n_emc", "matches_series_description"):
        assert as_extract_sees_it[k] == as_main_sees_it[k], (
            k, as_extract_sees_it[k], as_main_sees_it[k])


def test_both_halves_of_the_series_description_land():
    """66 cancer + 27 normal, derived from the header and matched against the series description.

    Either half alone would be a coincidence worth distrusting; the point is that both land.
    """
    g = m._groups(_real_header())
    assert g["n_libraries"] == 93, g["n_libraries"]
    assert g["n_tumour"] == 66, g["n_tumour"]
    assert g["n_normal"] == 27, g["n_normal"]
    assert g["n_emc"] == 4, g["emc_columns"]
    assert g["matches_series_description"] is True


def test_the_normal_panel_is_visceral_and_the_module_says_so():
    """⭐ THE PANEL'S COMPOSITION IS THE CEILING ON EVERY READING THIS DEPOSIT CAN PRODUCE.

    Six normal tissues, all visceral organs, none soft tissue. A gene high in EMC against THIS panel
    is therefore not shown to be EMC-specific rather than mesenchymal-lineage-specific — it is a
    normal-ORGAN exposure reading. The docstring must keep saying so, because the number this arm
    produces reads exactly like a specificity number and is not one.
    """
    g = m._groups(_real_header())
    assert g["normal_tissues"] == ["bowel", "breast", "colon", "kidney", "lung", "uterus"]
    assert "lineage" in m._extract.__doc__ and "exposure" in m._extract.__doc__


def test_technical_replicates_are_surfaced_and_none_is_an_emc_library():
    g = m._groups(_real_header())
    assert g["technical_replicate_columns"] == [
        "ESS_STT5520_rep1", "ESS_STT5520_rep2", "LMS_STT516_rep1", "LMS_STT516_rep2"]
    assert not any(c.startswith("EMC_") for c in g["technical_replicate_columns"])


def _synthetic_table(header, rows):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as fh:
        fh.write(("\t".join(header) + "\r\n" + "\r\n".join(rows) + "\r\n").encode())
    return buf.getvalue()


def test_extract_medians_per_gene_across_peaks_then_across_libraries():
    header = _real_header()
    g = m._groups(header)
    idx = {c.strip().strip('"'): i for i, c in enumerate(header)}
    emc, nor = set(g["emc_columns"]), set(g["normal_columns"])

    def row(peak, sym, e, n, o):
        f = [""] * len(header)
        f[0], f[1], f[3], f[4], f[5] = peak, "chr1:1-40_+", "NM_x", sym, sym
        for c, i in idx.items():
            if i >= len(ANN):
                f[i] = "%.3f" % (e if c in emc else n if c in nor else o)
        return "\t".join(f)

    data = _synthetic_table(header, [row("1", "ALCAM", 5.0, 1.0, 4.0),
                                     row("2", "ALCAM", 7.0, 1.0, 4.0),
                                     row("3", "NR4A3", 9.0, 0.1, 0.2)])
    per, missing, _ = m._extract(data, m.WANTED)
    assert per["ALCAM"]["n_peaks"] == 2
    assert per["ALCAM"]["emc_median"] == 6.0          # median of the two per-peak EMC medians
    assert per["ALCAM"]["normal_median"] == 1.0
    assert per["ALCAM"]["sarcoma_median"] == 4.0
    assert per["ALCAM"]["_n_emc_libs"] == 4
    assert per["ALCAM"]["_n_normal_libs"] == 27
    assert per["ALCAM"]["_n_sarcoma_libs"] == 32      # DDLPS+ESS+EWS+GIST+LMS+MLPS+SS columns
    # ⚠ A GENE WITH NO PEAK IS REPORTED AS SUCH, NEVER AS A ZERO. An absent reading is not a
    # reading of absence, and a `0.0` here would read as "not expressed".
    assert "SSTR2" in missing and "ALCAM" not in missing


def test_the_sarcoma_arm_excludes_carcinomas():
    """`Lung_SCC_STT5547`, `HNSCC_*`, `NPC_*`, `PUC_*`, `Skin_SCC_*` are carcinomas.

    They belong to neither the lineage comparator nor the normal arm, and folding them into the
    sarcoma median would make the lineage contrast meaningless.
    """
    header = _real_header()
    sar = [c for c in header if any(c.startswith(p + "_STT") for p in
           ("DDLPS", "ESS", "EWS", "GIST", "LMS", "MLPS", "SS"))]
    assert len(sar) == 32, sar
    assert not any("SCC" in c or "HNSCC" in c or "NPC" in c or "PUC" in c for c in sar)
    assert not any(c.startswith("EMC_") for c in sar)


def test_main_actually_calls_the_grouping_and_the_extraction():
    """⛔ THE DEFECT THAT STARTED THIS: both functions existed, `main` called neither.

    A function's PRESENCE in a module is not evidence that it ran — the same class as a populated
    field that was never measured. This asserts the wiring rather than describing it.
    """
    src = open(os.path.join(MOD, "gse28866_tumour_vs_normal.py"), encoding="utf-8").read()
    body = src.split("def main(", 1)[1]
    assert "_groups(" in body, "main() does not call _groups"
    assert "_extract(" in body, "main() does not call _extract"
    assert "matches_series_description" in body, "the extraction is not gated on the grouping"


# =================================================================================================
# THE RATIO CALIBRATION -- "is 2.5x unusual here?", which the 3SEQ arm was reported without.
# =================================================================================================
def test_a_zero_comparator_median_is_an_unreadable_ratio_not_a_huge_one():
    """The failure mode that would invert the whole ranking.

    A gene undetected in the comparator arm has NO ratio. Treating 0 as a denominator would put
    every such gene at the top, which is precisely backwards: those are the genes the deposit says
    least about."""
    assert m._ratio(5.0, 0.0) is None
    assert m._ratio(5.0, None) is None
    assert m._ratio(None, 2.0) is None
    assert m._ratio(5.0, 2.0) == 2.5


def test_percentile_is_a_rank_over_the_supplied_distribution():
    dist = [1.0, 2.0, 3.0, 4.0]
    assert m._percentile_of(0.5, dist) == 0.0
    assert m._percentile_of(2.0, dist) == 50.0
    assert m._percentile_of(4.0, dist) == 100.0
    assert m._percentile_of(None, dist) is None
    assert m._percentile_of(2.0, []) is None


def test_calibration_ranks_a_wanted_gene_against_every_gene_in_the_deposit():
    """A gene with the largest EMC/comparator ratio in the table must rank at the top, and a gene
    in the middle must not. Built with known answers so the arithmetic is checkable."""
    header = _real_header()
    g = m._groups(header)
    idx = {c.strip().strip('"'): i for i, c in enumerate(header)}
    emc, nor = set(g["emc_columns"]), set(g["normal_columns"])

    def row(peak, sym, e, n, o):
        f = [""] * len(header)
        f[0], f[1], f[3], f[4], f[5] = peak, "chr1:1-40_+", "NM_x", sym, sym
        for c, i in idx.items():
            if i >= len(ANN):
                f[i] = "%.3f" % (e if c in emc else n if c in nor else o)
        return "\t".join(f)

    rows = [row(str(i), "BG%d" % i, 1.0, 1.0, 1.0) for i in range(20)]   # 20 genes at ratio 1.0
    rows.append(row("90", "ENO3", 10.0, 1.0, 1.0))                       # the top of the table
    rows.append(row("91", "SEMA3C", 1.0, 1.0, 1.0))                      # indistinguishable
    rows.append(row("92", "PPARG", 4.0, 0.0, 2.0))                       # zero normal denominator
    cal = m._calibrate(_synthetic_table(header, rows), m.WANTED)

    assert cal["n_genes_in_deposit"] == 23
    assert cal["per_gene"]["ENO3"]["emc_over_normal"] == 10.0
    assert cal["per_gene"]["ENO3"]["emc_over_normal_percentile"] == 100.0
    # ⚠ THE POINT OF THE WHOLE BLOCK: a gene that moves exactly as much as everything else is not
    # a finding, however large its fold-change happens to be.
    assert cal["per_gene"]["SEMA3C"]["emc_over_normal"] == 1.0
    assert cal["per_gene"]["SEMA3C"]["emc_over_normal_percentile"] < 100.0
    # PPARG has no normal ratio (zero denominator) but does have a sarcoma one.
    assert cal["per_gene"]["PPARG"]["emc_over_normal"] is None
    assert cal["per_gene"]["PPARG"]["emc_over_normal_percentile"] is None
    assert cal["per_gene"]["PPARG"]["emc_over_sarcoma"] == 2.0
    assert cal["n_genes_with_a_normal_ratio"] == 22        # 23 minus the zero-denominator gene
    assert cal["distribution_emc_over_normal"]["median"] == 1.0


def test_a_gene_absent_from_the_deposit_is_null_and_says_what_null_means():
    header = _real_header()
    g = m._groups(header)
    idx = {c.strip().strip('"'): i for i, c in enumerate(header)}
    emc, nor = set(g["emc_columns"]), set(g["normal_columns"])

    def row(peak, sym, e, n, o):
        f = [""] * len(header)
        f[0], f[1], f[3], f[4], f[5] = peak, "chr1:1-40_+", "NM_x", sym, sym
        for c, i in idx.items():
            if i >= len(ANN):
                f[i] = "%.3f" % (e if c in emc else n if c in nor else o)
        return "\t".join(f)

    cal = m._calibrate(_synthetic_table(header, [row("1", "ENO3", 3.0, 1.0, 1.0)]), m.WANTED)
    assert cal["per_gene"]["MSLN"]["emc_over_normal"] is None
    assert "NOT a ratio of zero" in cal["per_gene"]["MSLN"]["_absent_means"]


def test_the_calibration_says_it_is_not_a_test():
    header = _real_header()
    cal = m._calibrate(_synthetic_table(header, []), m.WANTED)
    assert "not a p-value" in cal["_not_a_test"]
    assert "n_EMC = 4" in cal["_not_a_test"]
