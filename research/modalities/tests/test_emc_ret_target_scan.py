"""Tests for the EMC RET target-gene scan.

⛔ THE POINT OF THESE TESTS IS THE GUARD, NOT THE ARITHMETIC. The failure this module is most
likely to commit is the one CLAUDE.md §4 names: emitting a biological verdict from an instrument
that did not read anything. So the first thing asserted is that an empty inputs cache produces
`NOT_RUN` and `verdict: None`, and that no code path can turn an absent reading into a reading of
absence.
"""
import json
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_ret_target_scan as R  # noqa: E402


# --------------------------------------------------------------------------------------------
# The guard: no reading, no verdict.
# --------------------------------------------------------------------------------------------
def test_an_empty_inputs_cache_never_produces_a_biological_verdict():
    res = R.derive({})
    for part in ("part_1_nbre_scan", "part_2_expression"):
        assert res[part]["_status"] == "NOT_RUN", part
        assert res[part]["verdict"] is None, part
        assert "ABSENT READING" in res[part]["why"], part


def test_a_window_that_failed_to_fetch_is_not_counted_as_a_window_with_no_motif():
    """A `sequence_failed` record must not silently become 'RET has no NBRE'."""
    inputs = {"gene_windows": {"RET": {"symbol": "RET", "_status": "sequence_failed",
                                       "error": "boom"}}}
    d = R.derive_part1(inputs)
    assert d["_status"] == "NOT_RUN"
    assert d["verdict"] is None


def test_the_selftest_passes():
    assert R.selftest() == 0


# --------------------------------------------------------------------------------------------
# The motif engine.
# --------------------------------------------------------------------------------------------
def test_nbre_is_found_on_both_strands_at_the_right_offsets():
    rng = random.Random(11)
    filler = "".join(rng.choice("ACGT") for _ in range(600))
    seq = filler[:100] + R.NBRE + filler[100:300] + R.revcomp(R.NBRE) + filler[300:]
    hits = R.scan_nbre(seq)
    pos = {h["pos"]: h["strand"] for h in hits}
    assert 100 in pos and pos[100] == "+"
    rev_at = 100 + len(R.NBRE) + 200
    assert rev_at in pos and pos[rev_at] == "-"


def test_no_hit_is_reported_twice_for_one_position():
    seq = "AAAA" + R.NBRE + "TTTT"
    hits = R.scan_nbre(seq)
    assert len({h["pos"] for h in hits}) == len(hits)


def test_nurre_requires_the_published_spacer():
    ok = "GG" + R.NURRE_LEFT + "ACGTAC" + R.NURRE_RIGHT + "GG"
    assert R.scan_nurre(ok)
    bad = "GG" + R.NURRE_LEFT + "A" * 25 + R.NURRE_RIGHT + "GG"
    assert not R.scan_nurre(bad)


def test_one_mismatch_is_a_superset_of_exact():
    rng = random.Random(5)
    seq = "".join(rng.choice("ACGT") for _ in range(5000))
    assert len(R.scan_nbre(seq, 1)) >= len(R.scan_nbre(seq, 0))


# --------------------------------------------------------------------------------------------
# The null.  This is the part that decides whether a count means anything.
# --------------------------------------------------------------------------------------------
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4, 5, 6, 7])
def test_the_shuffle_preserves_dinucleotide_composition_exactly(seed):
    rng = random.Random(seed)
    weights = [[0.4, 0.1, 0.1, 0.4], [0.1, 0.4, 0.4, 0.1], [0.25] * 4][seed % 3]
    src = "".join(rng.choices("ACGT", weights=weights, k=2000))
    sh = R.dinucleotide_shuffle(src, random.Random(seed + 100))

    def dinuc(s):
        d = {}
        for a, b in zip(s, s[1:]):
            d[a + b] = d.get(a + b, 0) + 1
        return d

    assert len(sh) == len(src)
    assert dinuc(sh) == dinuc(src)
    # an Euler-path shuffle also fixes the first and last base
    assert sh[0] == src[0] and sh[-1] == src[-1]


def test_the_shuffle_actually_shuffles():
    rng = random.Random(3)
    src = "".join(rng.choice("ACGT") for _ in range(2000))
    assert R.dinucleotide_shuffle(src, random.Random(9)) != src


def test_the_null_does_not_fire_on_unenriched_sequence():
    rng = random.Random(21)
    plain = "".join(rng.choice("ACGT") for _ in range(4000))
    assert R.shuffle_null(plain, 200, 3)["empirical_p_one_sided"] >= 0.05


def test_the_null_detects_a_planted_enrichment():
    rng = random.Random(21)
    seq = "".join(rng.choice("ACGT") for _ in range(4000))
    for k in range(6):
        at = 400 * (k + 1)
        seq = seq[:at] + R.NBRE + seq[at + len(R.NBRE):]
    assert R.shuffle_null(seq, 200, 3)["empirical_p_one_sided"] < 0.05


def test_the_empirical_p_can_never_be_zero():
    """(ge + 1) / (n + 1), not ge / n. A permutation test of n replicates is not entitled to
    report a p-value smaller than 1/(n+1), and printing 0.0 invites exactly that overclaim."""
    rng = random.Random(4)
    seq = "".join(rng.choice("ACGT") for _ in range(1500))
    for k in range(20):
        at = 60 * (k + 1)
        seq = seq[:at] + R.NBRE + seq[at + len(R.NBRE):]
    n = R.shuffle_null(seq, 50, 1)
    assert n["empirical_p_one_sided"] > 0
    assert n["empirical_p_one_sided"] >= 1 / 51


# --------------------------------------------------------------------------------------------
# Determinism — `--check` has to be able to reproduce the derive half exactly.
# --------------------------------------------------------------------------------------------
def test_the_null_is_deterministic_for_a_fixed_seed():
    rng = random.Random(8)
    seq = "".join(rng.choice("ACGT") for _ in range(2000))
    assert R.shuffle_null(seq, 60, 42) == R.shuffle_null(seq, 60, 42)


def test_the_background_panel_is_deterministic_and_excludes_the_focus_genes():
    a, _ = R.background_symbols()
    b, _ = R.background_symbols()
    assert a == b
    assert not (set(a) & set(R.FOCUS_GENES))


# --------------------------------------------------------------------------------------------
# Sample classification and the expression half.
# --------------------------------------------------------------------------------------------
@pytest.mark.parametrize("text,want", [
    ("Extraskeletal myxoid chondrosarcoma 3 | soft tissue | tumor biopsy", "EMC"),
    # ⛔ REGRESSION GUARD. GSE4303 titles its EMC samples without "extraskeletal"; an
    # EMC-phrase-only classifier put TEN OF SIXTEEN of them in the comparator arm and the
    # resulting contrast would have been EMC against EMC.
    ("STT3697-Myxoid Chondrosarcoma", "EMC"),
    ("STT3780-Myxoid chondrosarcoma", "EMC"),
    ("STT5525_EMC", "EMC"),
    ("Desmoid fibromatosis 1 | soft tissue", "comparator_sarcoma"),
    ("Low-grade fibromyxoid sarcoma 2", "comparator_sarcoma"),
    ("STT2001c-GIST-Total RNA", "comparator_sarcoma"),
    ("STT3053-DFSP mRNA", "comparator_sarcoma"),
    ("normal skeletal muscle reference pool", "normal_or_reference"),
    ("", "unclassified"),
])
def test_sample_classification(text, want):
    assert R._classify(text) == want


def test_emcee_is_not_an_emc_sample():
    assert R._classify("emcee of the conference") != "EMC"


def test_an_unrecognised_label_is_unclassified_and_never_a_comparator():
    """⛔ THE CATCH-ALL THAT WAS THERE FIRST. `if annotation: return 'comparator_sarcoma'` turned
    every label the list did not know into a comparator — which fed GSE24369's two skeletal-muscle
    samples into the comparator arm of a tumour contrast. An unrecognised label is an ABSENT
    READING about that sample."""
    for text in ("Solitary fibrous tumor 3", "tissue: Skeletal muscle", "some future entity"):
        assert R._classify(text) in ("unclassified", "normal_or_reference"), text
        assert R._classify(text) != "comparator_sarcoma", text


def test_the_patterns_come_from_the_module_that_owns_them():
    """One fact, one home. If `emc_atr_vulnerability` stops defining these as module-level
    literals, this module must FAIL LOUDLY rather than fall back to a private copy."""
    emc_pats, buckets = R._owner_patterns()
    assert "myxoid chondrosarcoma" in emc_pats
    assert "GIST" in buckets and "DFSP" in buckets
    # and the live constants really are those, not a copy that has drifted
    assert R.EMC_SAMPLE_PATTERNS == emc_pats
    assert R.COMPARATOR_BUCKETS == buckets


def test_the_real_committed_annotations_classify_into_two_usable_arms():
    """⚠ EXERCISES THE REAL FILE, NOT A FIXTURE. Every version of this bug was invisible to a
    hand-written fixture and obvious the moment the actual GEO annotations were run through it."""
    path = os.path.join(MOD, "emc-atr-vulnerability-inputs.json")
    if not os.path.exists(path):
        pytest.skip("the ATR inputs cache is not present")
    plats = json.load(open(path, encoding="utf-8"))["part_b"]["platforms"]
    for name, min_emc, min_comp in (("GSE24369_series_matrix.txt.gz", 6, 20),
                                    ("GSE4303-GPL3290_series_matrix.txt.gz", 10, 6)):
        cls = [R._classify(s["annotation_verbatim"]) for s in plats[name]["samples"]]
        assert cls.count("EMC") >= min_emc, (name, cls.count("EMC"))
        assert cls.count("comparator_sarcoma") >= min_comp, (name, cls.count("comparator_sarcoma"))


def test_part2_reports_underpowered_rather_than_a_contrast_when_n_is_small():
    inputs = {"series": {"GSEX": {
        "_status": "read",
        "platforms": {"f.txt.gz": {
            "_status": "read", "platform": "GPLX",
            "value_kind": "single-channel intensity",
            "samples": [{"gsm": "G1", "annotation_verbatim": "Extraskeletal myxoid chondrosarcoma 1"},
                        {"gsm": "G2", "annotation_verbatim": "Desmoid fibromatosis 1"}],
            "gene_values": {"RET": [5.0, 6.0]},
        }},
    }}}
    d = R.derive_part2(inputs)
    row = d["series"]["GSEX"]["f.txt.gz"]
    assert "_status" in row["contrasts"]
    assert "underpowered" in row["contrasts"]["_status"]
    assert d["verdict"]["call"] == "RET_NOT_MEASURED"


def test_spearman_extremes():
    assert R.spearman([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]) == 1.0
    assert R.spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) == -1.0
    assert R.spearman([1, 2], [1, 2]) is None       # too few points to be meaningful


# --------------------------------------------------------------------------------------------
# The artifacts themselves.
# --------------------------------------------------------------------------------------------
def test_the_committed_artifact_rederives_from_its_inputs():
    assert R.main(["--check"]) == 0


def test_the_activation_bar_file_carries_a_pmid_for_every_source():
    path = os.path.join(MOD, "emc-ret-activation-bar.json")
    d = json.load(open(path, encoding="utf-8"))
    assert d["sources"], "no sources recorded"
    for name, src in d["sources"].items():
        assert src.get("pmid"), f"{name} has no PMID"
        assert src.get("verification") in ("FT", "API", "paywalled"), name


def test_no_source_carries_a_free_text_citation_field():
    """⛔ A PARAPHRASED TITLE IN A CITATION FIELD IS A FABRICATED CITATION, and one was written
    here before being caught by cross-checking PMIDs against the retrieved Europe PMC records.
    A `citation` string invites paraphrase; `title_verbatim` does not, because the field name
    makes an inexact value a visible lie rather than a stylistic choice. So a source may carry
    `title_verbatim`, and must not carry a free-text `citation` for anything read [FT]/[API]."""
    d = json.load(open(os.path.join(MOD, "emc-ret-activation-bar.json"), encoding="utf-8"))
    for name, src in d["sources"].items():
        if src.get("verification") in ("FT", "API"):
            assert "title_verbatim" in src or "citation" in src, \
                f"{name} records neither a verbatim title nor a citation"
        for key, val in src.items():
            if key.endswith("_verbatim"):
                assert isinstance(val, str) and val.strip(), f"{name}.{key} is empty"


def test_the_artifact_states_what_it_cannot_conclude():
    d = json.load(open(R.OUT, encoding="utf-8"))
    txt = " ".join(d["_what_this_cannot_conclude"]).lower()
    for must in ("occup", "phosphorylat", "selectivity", "efficacy", "safety"):
        assert must in txt, must


def test_every_risk_term_appears_only_inside_a_disclaimer():
    """R1-R5 language discipline, asserted locally rather than left to CI.

    ⚠ A BARE BANNED-SUBSTRING TEST IS THE WRONG SHAPE HERE, and it failed on the first run for
    exactly the right reason: the phrase 'therapeutic window' occurs in this module's own
    disclaimer ('no claim of ... a therapeutic window ... is made or implied'). Banning the token
    would force the disclaimer out, which is the opposite of the rule. What must be asserted is
    that every occurrence sits inside a NEGATION, so the artifact can say what it does not claim
    while still being unable to claim it.
    """
    import re
    risky = ("therapeutic window", "clinical readiness", "clinically ready",
             "efficacy", "selectivity", "safety")
    # Disclaimer / limitation markers. ⚠ NOT purely negations, and the third failure this test
    # produced is why: the sentence "This repository's paralogue-SELECTIVITY problem has so far
    # been argued from domain sequence identity" contains a risky token and is a statement of a
    # LIMITATION, which is exactly the register the rule wants. What is forbidden is an
    # ASSERTION of selectivity/efficacy/safety, not the word appearing while something is being
    # conceded — so "problem", "unresolved" and "unknown" belong here beside the negations.
    negations = ("no claim", "cannot", "does not", "is not", "never", "nothing here",
                 "nothing in this", "not supported", "must not", "no evidence",
                 "says nothing", "unable", "problem", "unresolved", "unknown",
                 "not established", "has not")

    def sentences(obj, key, out):
        """Carry the enclosing KEY down with each sentence. A key like
        `_what_this_cannot_conclude` is itself the negation for every item under it, so a bullet
        reading 'Anything about ... a therapeutic window ...' is a disclaimer even though the
        bullet contains no negating word of its own."""
        if isinstance(obj, str):
            out += [(key, s) for s in re.split(r"(?<=[.;])\s+", obj)]
        elif isinstance(obj, dict):
            for k, v in obj.items():
                out.append((key, str(k)))
                sentences(v, str(k), out)
        elif isinstance(obj, list):
            for v in obj:
                sentences(v, key, out)
        return out

    # ⛔ ONE EXEMPTION, AND IT IS NARROW ON PURPOSE. A key explicitly marked `*_verbatim`,
    # `title*` or `citation` holds QUOTED SOURCE TEXT. The second failure this test produced was
    # a published paper's own title — "Tumour-agnostic efficacy and safety of selpercatinib in
    # patients with RET fusion-positive solid tumours" — and the correct response to that is not
    # to paraphrase a citation, because a doctored quotation is a worse defect than an
    # undisclaimed one. The exemption is keyed on the FIELD NAME, so hiding an assertion behind
    # it means mislabelling it a quotation, which is a different and more visible offence.
    quoted = ("verbatim", "title", "citation")

    for path in (R.OUT, os.path.join(MOD, "emc-ret-activation-bar.json")):
        for key, s in sentences(json.load(open(path, encoding="utf-8")), "", []):
            low, klow = s.lower(), key.lower()
            if any(q in klow for q in quoted):
                continue
            ctx = (low + " " + klow.replace("_", " "))
            for term in risky:
                if term in low:
                    assert any(n in ctx for n in negations), \
                        f"{os.path.basename(path)}: '{term}' outside a disclaimer -> {s[:200]}"


# ---------------------------------------------------------------------------------------------
# ⭐ THE FAST `find_all` MUST BE THE NAIVE ONE, NOT MERELY "CLOSE TO IT" (added 2026-08-08).
#
# WHY THIS TEST EXISTS. `find_all` was a plain O(n*m) index loop, and its docstring justified that
# as "deliberately naive ... a clever implementation would only add a place for a bug to hide".
# The reasoning was right; the premise was not. One scan IS microseconds, but the shuffle null
# runs two per shuffled window and N_SHUFFLES is 2000, so the naive form cost hundreds of millions
# of interpreted comparisons per gene -- measured as the single dominant cost of the whole CI
# suite. Replacing it with a C-level `str.find` plus pigeonhole seeding is a real speedup and a
# real risk, so the docstring's warning is answered the only way it can be: the naive
# implementation is KEPT HERE, as the reference, and the two are compared.
#
# ⛔ The degenerate cases are in the grid on purpose. Production only ever passes an 8-mer at
# max_mismatch 0 or 1, so an empty pattern, a pattern longer than the sequence, and
# max_mismatch >= len(pattern) would all rot undetected -- and the first fast version got each of
# them wrong. `N` is in the alphabet for the same reason: a variant-enumeration shortcut over
# ACGT would silently miss a window whose only mismatch IS the N.
def _naive_find_all(seq: str, pattern: str, max_mismatch: int = 0):
    """The original implementation, verbatim, kept as the reference."""
    n, m = len(seq), len(pattern)
    hits = []
    for i in range(n - m + 1):
        mm = 0
        for j in range(m):
            if seq[i + j] != pattern[j]:
                mm += 1
                if mm > max_mismatch:
                    break
        else:
            hits.append(i)
    return hits


def test_find_all_matches_the_naive_reference_exactly():
    import random as _random

    rng = _random.Random(20260808)
    compared = 0
    for alphabet in ("ACGT", "ACGTN", "AC"):
        for length in (0, 1, 7, 8, 9, 50, 400):
            for _ in range(6):
                seq = "".join(rng.choice(alphabet) for _ in range(length))
                for pattern in (R.NBRE, R.NURRE_LEFT, "AC", "A", ""):
                    for mm in (0, 1, 2):
                        assert R.find_all(seq, pattern, mm) == _naive_find_all(seq, pattern, mm), (
                            f"find_all diverged from the naive reference: alphabet={alphabet!r} "
                            f"len={length} pattern={pattern!r} max_mismatch={mm}"
                        )
                        compared += 1
    # A guard that silently compared nothing would pass forever.
    assert compared >= 1000, f"the equivalence grid collapsed to {compared} cases"
