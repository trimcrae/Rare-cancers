#!/usr/bin/env python3
"""The genome screen must find every site, once, at the right coordinate, and grade it honestly.

⛔ WHY THESE TESTS AND NOT "DOES IT RUN". This screen's output will be quoted in a manuscript that
already concedes a genome-wide blind spot, so the failures that matter are the ones that produce a
NUMBER rather than an error, and every one of them is in the flattering direction:

  * a MISSED hit — a dropped chunk-boundary window, an N-window rule that is too wide, a
    neighbourhood one code short — reports the genome as cleaner than it is;
  * a DOUBLE-COUNTED hit — the chunk overlap counted twice — inflates a design's load and would be
    read as an excess over chance;
  * a KERNEL that counts BITS rather than BASES grades a transversion as two mismatches and a
    transition as one, admitting and rejecting the wrong sites;
  * a REVERSE-COMPLEMENT match called hybridisable invents a liability that no transcript carries;
  * a DENOMINATOR that is approximately right makes every observed-over-expected ratio wrong by the
    same factor, silently, in whichever direction the error went;
  * and a RAW TOTAL published as a finding restates 4**16, which is the error
    `offtarget_chance_baseline.py` already had to kill once at transcriptome scale.

Each of those has a test below whose failure names it. The strongest is
`test_the_scan_agrees_with_a_brute_force_scan_of_the_same_genome`: a deliberately dumb reference
implementation over the same synthetic sequence, compared hit for hit. It subsumes most of the
others, and the others are kept anyway because a subsumed failure is much harder to read.
"""
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
sys.path.insert(0, MOD)

m = pytest.importorskip("aso_genome_offtarget")
np = pytest.importorskip("numpy")

K = m.OLIGO_LEN
GAP_LO, GAP_HI = m.GAP_1BASED

#: Four real target windows from the atlas, chosen because they are what the screen will actually
#: see. A test genome built from invented sequence would not exercise the tiled, one-nucleotide-
#: shifted registers that make these designs near-neighbours of each other.
TARGETS = ["GTCCACGGATATGCCC", "AAAGATGAAGATATGC", "CATTCTAGATATGCCC", "GGGCATATCCGACATG"]
TARGETS = [t[:K].ljust(K, "A") for t in TARGETS]


def _atlas_targets(n):
    """`n` real, distinct target windows from the committed atlas — never invented sequence."""
    _designs, windows, _atlas = m.designs_from_atlas()
    return windows[:n]


def _inputs(targets=None):
    """`(designs, windows, atlas)` for the real `scan_genome`, over a handful of windows."""
    targets = TARGETS if targets is None else targets
    designs = [{"_key": f"J{i}|x", "junction_label": f"J{i}", "antisense_5to3": m.rc(t),
                "target_mRNA_5to3": t, "gap_specificity_margin": 2, "gc_percent": 50.0}
               for i, t in enumerate(targets)]
    atlas = {"transcripts": {"EWSR1": {}, "NR4A3": {}}}
    return designs, sorted({t for t in targets}), atlas


def _write_fasta(path, seqs, width=60):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="ascii") as fh:
        for name, s in seqs.items():
            fh.write(f">{name} dna_sm:test\n")
            for i in range(0, len(s), width):
                fh.write(s[i:i + width] + "\n")
    return path


def _rand(n, seed):
    """Uniform ACGT — the null's own assumption, which is what makes the chance test meaningful."""
    v = np.random.default_rng(seed).integers(0, 4, n, dtype=np.uint8)
    return np.frombuffer(np.array(list(b"ACGT"), dtype=np.uint8)[v].tobytes(),
                         dtype=np.uint8).tobytes().decode("ascii")


def _plant(s, at, text):
    return s[:at] + text + s[at + len(text):]


# --------------------------------------------------------------------------------------------
# the kernel — the one thing that must be exactly right
# --------------------------------------------------------------------------------------------
def test_the_kernel_reproduces_brute_force_hamming_distance_over_random_pairs():
    """Catches a kernel that counts BITS instead of BASES, which grades transversions as two."""
    import random  # noqa: PLC0415
    r = random.Random(4242)
    bad = []
    for _ in range(20000):
        a = "".join(r.choice("ACGT") for _ in range(K))
        b = "".join(r.choice("ACGT") for _ in range(K))
        got = int(m.mismatches(np, m.pack(a), m.pack(b)))
        want = m.brute_mismatches(a, b)
        if got != want:
            bad.append((a, b, got, want))
    assert not bad, f"{len(bad)} disagreement(s) with brute force, e.g. {bad[:3]}"


def test_the_kernel_is_exact_over_every_variant_at_and_around_the_threshold():
    """Exhaustive rather than sampled at the distances that decide admission."""
    import itertools  # noqa: PLC0415
    ref = TARGETS[0]
    bad, n = [], 0
    for k in range(0, m.MAX_MM + 2):
        for pos in itertools.combinations(range(K), k):
            for subs in itertools.product("ACGT", repeat=k):
                lst = list(ref)
                for p, s in zip(pos, subs):
                    lst[p] = s
                b = "".join(lst)
                n += 1
                if int(m.mismatches(np, m.pack(ref), m.pack(b))) != m.brute_mismatches(ref, b):
                    bad.append(b)
    assert n > 30000 and not bad, f"{len(bad)} of {n} variants disagree, e.g. {bad[:3]}"


def test_the_masked_kernel_gives_the_catalytic_gap_sub_distance():
    """A wrong mask would resolve the wrong six nucleotides and mislabel every gap_fully_paired."""
    import random  # noqa: PLC0415
    r = random.Random(99)
    bad = []
    for _ in range(20000):
        a = "".join(r.choice("ACGT") for _ in range(K))
        b = "".join(r.choice("ACGT") for _ in range(K))
        got = int(m.mismatches(np, m.pack(a), m.pack(b), m.GAP_MASK))
        want = m.brute_mismatches(a[GAP_LO - 1:GAP_HI], b[GAP_LO - 1:GAP_HI])
        if got != want:
            bad.append((a, b, got, want))
    assert not bad, f"{len(bad)} gap-distance disagreement(s), e.g. {bad[:3]}"


def test_the_gap_mask_is_derived_from_the_geometry_and_not_typed():
    """⛔ `aso_premrna_offtarget` imports a `GAP_REGION_1BASED` that exists nowhere and silently
    falls back to a literal `(6, 11)`. It has never been wrong because the default geometry is
    5-6-5/16 — and `aso-offtarget.yml` carries a `gapmer_geometry` input, so a `20,5` dispatch would
    make the true gap `(6, 15)` while the fallback kept saying `(6, 11)`. This asserts the
    derivation rather than the value."""
    assert m.GAP_1BASED == (m.WING + 1, m.OLIGO_LEN - m.WING)
    assert m.GAP_MASK == m.gap_mask(m.OLIGO_LEN, m.GAP_1BASED)
    # A different geometry must move the mask, or the derivation is decorative.
    assert m.gap_mask(20, (6, 15)) != m.GAP_MASK
    assert bin(m.GAP_MASK).count("1") == 2 * (GAP_HI - GAP_LO + 1)


def test_pack_and_unpack_round_trip_and_the_first_base_is_in_the_high_bits():
    """The bit order is what makes the gap a contiguous mask; a reversal would still round-trip."""
    for s in ("A" * K, "T" * K, TARGETS[0], m.rc(TARGETS[0])):
        assert m.unpack(m.pack(s)) == s
    assert m.pack("A" + "A" * (K - 1)) == 0
    # 'C' (code 1) in position 1 must land in the top two bits.
    assert m.pack("C" + "A" * (K - 1)) == 1 << (2 * (K - 1))


# --------------------------------------------------------------------------------------------
# the neighbourhood and the bitmap
# --------------------------------------------------------------------------------------------
def test_the_neighbourhood_is_exactly_the_combinatorial_size():
    """One code short is one class of near-match this screen can never see, silently."""
    for t in TARGETS:
        nb = m.neighbourhood(t)
        assert len(nb) == m.n_within(K, m.MAX_MM) == 1129
        assert len(set(nb)) == len(nb)
        assert all(m.brute_mismatches(m.unpack(c), t) <= m.MAX_MM for c in nb)


def test_a_sequence_beyond_the_threshold_is_not_in_the_neighbourhood():
    t = TARGETS[0]
    nb = set(m.neighbourhood(t))
    far = list(t)
    for i in (0, 4, 9):
        far[i] = "A" if far[i] != "A" else "C"
    assert m.brute_mismatches("".join(far), t) == m.MAX_MM + 1
    assert m.pack("".join(far)) not in nb


def test_the_null_arithmetic_agrees_with_the_committed_chance_baseline():
    """⛔ ONE FACT, ONE PLACE applies to a FORMULA too. `offtarget_chance_baseline.n_within` is what
    the manuscript's chance-expectation panel (Supplementary Figure S1) and section 3.6 are
    computed from; a genome arm that quietly used a
    different combinatorial would put two incompatible nulls in one paper."""
    base = pytest.importorskip("offtarget_chance_baseline")
    for k in (0, 1, 2, 3):
        assert m.n_within(16, k) == base.n_within(16, k)
    # Gap-paired: every substitution must fall outside the six-nucleotide gap.
    assert m.n_gap_paired_within(16, (6, 11), 2) == 436
    assert m.n_gap_paired_within(16, (6, 11), 0) == 1


def test_the_bitmap_admits_every_neighbour_of_every_target_and_both_orientations():
    """Membership may over-admit and must never miss; resolution can then only remove."""
    designs, windows, _atlas = _inputs()
    bitmap, code_index, slots, stats = m.build_bitmap(np, windows)
    assert stats["n_slots"] == 2 * len(windows)
    for t in windows:
        for probe in (t, m.rc(t)):
            for code in m.neighbourhood(probe):
                assert bitmap[code >> 3] & (1 << (code & 7)), (
                    f"{m.unpack(code)} is within {m.MAX_MM} of {probe} and the bitmap misses it")
                assert code in code_index


def test_every_bitmap_hit_resolves_to_a_real_slot_within_the_threshold():
    """A candidate the resolver cannot place would mean the index and the bitmap disagree."""
    designs, windows, _atlas = _inputs()
    _bitmap, code_index, slots, _stats = m.build_bitmap(np, windows)
    for code, slot_ids in list(code_index.items())[:5000]:
        assert slot_ids
        assert any(m.brute_mismatches(m.unpack(code), slots[s]["seq"]) <= m.MAX_MM
                   for s in slot_ids)


# --------------------------------------------------------------------------------------------
# the scan — planted sites, and a brute-force reference
# --------------------------------------------------------------------------------------------
def _brute_scan(seqs, windows, max_mm=None, gap=None):
    """The deliberately dumb reference: every position, every window, both orientations."""
    max_mm = m.MAX_MM if max_mm is None else max_mm
    lo, hi = (m.GAP_1BASED if gap is None else gap)
    out = set()
    for name, s in seqs.items():
        for i in range(len(s) - K + 1):
            w = s[i:i + K].upper()
            if set(w) - set("ACGT"):
                continue
            for t in windows:
                for orient, probe in (("sense", t), ("antisense", m.rc(t))):
                    mm = m.brute_mismatches(w, probe)
                    if mm <= max_mm:
                        gmm = m.brute_mismatches(w[lo - 1:hi], probe[lo - 1:hi])
                        out.add((t, name, i, orient, mm, gmm))
    return out


def _scanned_set(rec):
    out = set()
    for row in rec["per_design"]:
        for h in row["sites"] + row["exact_sites"] + row["named_target_sites"]:
            out.add((row["target_mRNA_5to3"], h["seq"], h["start"], h["orientation"],
                     h["mismatches"], h["gap_mismatches"]))
    return out


def _run(tmp_path, seqs, chunk_nt=1000, gtf=None, targets=None, resume=False):
    fa = _write_fasta(str(tmp_path / "g.fa"), seqs)
    return m.scan_genome(fa, gtf, ckpt_dir=str(tmp_path / "ck"), chunk_nt=chunk_nt,
                         resume=resume, progress=False, inputs=_inputs(targets))


def test_the_scan_agrees_with_a_brute_force_scan_of_the_same_genome(tmp_path):
    """★ THE LOAD-BEARING TEST. Every hit, both orientations, exact coordinates and both mismatch
    counts, against an implementation that shares no code with the one under test.

    The retention cap is lifted for this test only: a capped comparison could pass while silently
    dropping sites, which is the one thing it is here to rule out.
    """
    seqs = {"C1": _rand(9000, 11), "C2": _rand(4000, 12)}
    seqs["C1"] = _plant(seqs["C1"], 1200, TARGETS[0])
    seqs["C1"] = _plant(seqs["C1"], 3300, m.rc(TARGETS[1]))
    seqs["C2"] = _plant(seqs["C2"], 900, TARGETS[2])
    old = m.RETAINED_SITES_PER_WINDOW
    m.RETAINED_SITES_PER_WINDOW = 10_000
    try:
        rec = _run(tmp_path, seqs, chunk_nt=777)
    finally:
        m.RETAINED_SITES_PER_WINDOW = old
    want = _brute_scan(seqs, sorted(set(TARGETS)))
    got = _scanned_set(rec)
    assert got == want, (
        f"missed {sorted(want - got)[:5]} ; invented {sorted(got - want)[:5]}")
    assert len(want) >= 3


def test_a_planted_hit_is_found_at_its_coordinate_with_its_mismatch_count(tmp_path):
    """Named separately from the brute-force test because a coordinate error reads differently."""
    s = _rand(4000, 21)
    s = _plant(s, 1000, TARGETS[0])
    one = list(TARGETS[0])
    one[0] = "A" if one[0] != "A" else "C"
    s = _plant(s, 2000, "".join(one))
    two = list(TARGETS[0])
    g = GAP_LO - 1
    two[g] = "A" if two[g] != "A" else "C"
    two[g + 1] = "T" if two[g + 1] != "T" else "G"
    s = _plant(s, 3000, "".join(two))
    rec = _run(tmp_path, {"C1": s}, chunk_nt=613)
    by = {(h["start"]): h for row in rec["per_design"] if row["target_mRNA_5to3"] == TARGETS[0]
          for h in row["sites"]}
    assert by[1000]["mismatches"] == 0 and by[1000]["gap_mismatches"] == 0
    assert by[2000]["mismatches"] == 1 and by[2000]["gap_mismatches"] == 0, \
        "a wing mismatch must not be counted inside the catalytic gap"
    assert by[3000]["mismatches"] == 2 and by[3000]["gap_mismatches"] == 2
    assert by[3000]["gap_fully_paired"] is False
    assert by[1000]["end"] == 1000 + K - 1


@pytest.mark.parametrize("boundary_offset", [0, 1, 7, 14, 15])
def test_a_hit_across_a_chunk_boundary_is_found_exactly_once(tmp_path, boundary_offset):
    """⛔ THE CLASSIC BUG IN THIS DESIGN. A window starting in a chunk's last k-1 positions extends
    past its end; scanning chunks independently drops it, and the loss is uniform, invisible and
    flattering. Planted so its start sits `boundary_offset` before the boundary, i.e. straddling
    it for every offset below k."""
    chunk = 1000
    at = chunk - boundary_offset
    s = _plant(_rand(4000, 33), at, TARGETS[0])
    rec = _run(tmp_path, {"C1": s}, chunk_nt=chunk)
    hits = [h for row in rec["per_design"] if row["target_mRNA_5to3"] == TARGETS[0]
            for h in row["sites"] if h["mismatches"] == 0]
    starts = [h["start"] for h in hits]
    assert starts.count(at) == 1, (
        f"a hit straddling the chunk boundary at {chunk} (start {at}) was found "
        f"{starts.count(at)} time(s); starts={sorted(starts)}")


def test_chunking_is_invariant(tmp_path):
    """★ THE STRONGER FORM OF THE BOUNDARY TEST: the whole hit set must be identical however the
    genome is cut, including chunk sizes that are not multiples of anything and one larger than the
    genome itself."""
    seqs = {"C1": _plant(_rand(6000, 44), 2993, TARGETS[0]),
            "C2": _plant(_rand(2500, 45), 1017, m.rc(TARGETS[1]))}
    ref = None
    for chunk in (17, 101, 1000, 1024, 3001, 999999):
        rec = _run(tmp_path / f"c{chunk}", seqs, chunk_nt=chunk)
        got = _scanned_set(rec)
        den = (rec["denominator"]["windows_scanned"], rec["denominator"]["total_nt"],
               rec["denominator"]["softmasked_nt"])
        if ref is None:
            ref = (got, den)
        assert got == ref[0], f"chunk_nt={chunk} changed the hit set"
        assert den == ref[1], f"chunk_nt={chunk} changed the denominator to {den} from {ref[1]}"


def test_a_window_containing_N_is_excluded_and_counted_as_excluded(tmp_path):
    """An N-window admitted as ACGT would be a fabricated site; one silently dropped from the
    denominator would move every expectation."""
    good = TARGETS[0]
    withn = good[:3] + "N" + good[4:]
    s = _rand(3000, 55)
    s = _plant(s, 500, good)
    s = _plant(s, 1500, withn)
    rec = _run(tmp_path, {"C1": s}, chunk_nt=700)
    starts = [h["start"] for row in rec["per_design"] for h in row["sites"]]
    assert 500 in starts and 1500 not in starts
    d = rec["denominator"]
    assert d["windows_with_N"] == K, f"exactly {K} windows contain the single N, got {d['windows_with_N']}"
    assert d["windows_scanned"] == d["windows_total"] - d["windows_with_N"]
    assert d["windows_total"] == len(s) - K + 1


def test_a_window_never_spans_two_records(tmp_path):
    """A hit at a coordinate that exists in no genome looks exactly like a real one."""
    half = len(TARGETS[0]) // 2
    seqs = {"C1": _rand(500, 66) + TARGETS[0][:half],
            "C2": TARGETS[0][half:] + _rand(500, 67)}
    rec = _run(tmp_path, seqs, chunk_nt=97)
    exact = [h for row in rec["per_design"] for h in row["sites"] if h["mismatches"] == 0]
    assert not exact, f"a window spanned the record boundary: {exact}"
    assert rec["denominator"]["total_nt"] == len(seqs["C1"]) + len(seqs["C2"])


# --------------------------------------------------------------------------------------------
# the denominator, which the manuscript currently has to assume
# --------------------------------------------------------------------------------------------
def test_soft_masked_nucleotides_are_not_double_counted_across_chunk_boundaries(tmp_path):
    """Chunks overlap by k-1 bases; the window arithmetic is exact under that and the NUCLEOTIDE
    arithmetic is not unless the overlap is subtracted. A denominator that is approximately right
    makes every observed-over-expected ratio wrong by the same silent factor."""
    s = (_rand(1000, 77) + _rand(1000, 78).lower()) * 3
    rec = _run(tmp_path, {"C1": s}, chunk_nt=250)
    assert rec["denominator"]["softmasked_nt"] == sum(1 for c in s if c.islower())
    assert rec["denominator"]["total_nt"] == len(s)


def test_the_per_sequence_denominators_sum_to_the_total(tmp_path):
    seqs = {"C1": _rand(2000, 81), "C2": _rand(1500, 82), "C3": _rand(30, 83)}
    rec = _run(tmp_path, seqs, chunk_nt=311)
    d = rec["denominator"]
    assert sum(r["nt"] for r in d["per_sequence"]) == d["total_nt"] == 3530
    assert sum(r["windows_scanned"] for r in d["per_sequence"]) == d["windows_scanned"]
    # A record shorter than the oligo contributes nucleotides and no windows.
    short = [r for r in d["per_sequence"] if r["name"] == "C3"][0]
    assert short["nt"] == 30 and short["windows_total"] == 30 - K + 1


def test_expectations_are_computed_from_the_measured_denominator(tmp_path):
    """⛔ The manuscript carries an ASSUMED 3e8-8e8 transcriptome span because the screens record
    transcripts rather than nucleotides. If this arm's expectation were a constant rather than a
    function of what it actually scanned, it would inherit exactly that defect."""
    small = _run(tmp_path / "a", {"C1": _rand(4000, 91)}, chunk_nt=1000)
    big = _run(tmp_path / "b", {"C1": _rand(4000, 91), "C2": _rand(4000, 92)}, chunk_nt=1000)
    es, eb = (r["null_model"]["expected_per_design"] for r in (small, big))
    ratio = big["denominator"]["windows_scanned"] / small["denominator"]["windows_scanned"]
    assert eb["le2"] == pytest.approx(es["le2"] * ratio, rel=1e-4)
    # And the expectation is 2 * n_within * W / 4**K, both orientations, computed not typed.
    w = big["denominator"]["windows_scanned"]
    assert eb["le2"] == pytest.approx(2 * m.n_within(K, m.MAX_MM) * w / 4 ** K, rel=1e-5)
    assert eb["exact"] == pytest.approx(2 * w / 4 ** K, rel=1e-5)
    # ⚠ AND IT SURVIVES ROUNDING. `round(x, 2)` would send this stratum to 0.0 on any subset,
    # which is the one the artifact leads on, so the ratio would divide by zero or read as null.
    assert eb["exact"] > 0, "the exact-match expectation was rounded away"


def test_observed_matches_chance_on_uniform_random_sequence(tmp_path):
    """★ THE NULL AND THE SCAN VALIDATE EACH OTHER, AND NEITHER COULD DO IT ALONE. On sequence drawn
    from the null's own assumption the observed count per design must land on the expectation. A
    scan that missed windows, one that double-counted the chunk overlap, and an expectation off by
    the two-orientation factor of 2 all fail here — and none of them would fail a test that merely
    checked the code runs.

    ⚠ AND IT IS THE ONE TEST THAT WOULD CATCH THE OPPOSITE ERROR TOO: if this came back far BELOW
    chance it would mean the screen was silently restricting what it scanned, which is the defect
    that made the manuscript's mature-only screens look clean by construction.

    Sized so the Poisson noise on the mean is a few percent: 24 Mb over 20 target windows.
    """
    targets = _atlas_targets(20)
    seqs = {"C1": _rand(24_000_000, 4242)}
    rec = _run(tmp_path, seqs, chunk_nt=2_000_000, targets=targets)
    exp = rec["null_model"]["expected_per_design"]["le2"]
    obs = [r["counts"]["le2"] for r in rec["per_design"]]
    mean = sum(obs) / len(obs)
    assert exp > 8, f"the fixture is too small to test this: expected only {exp}"
    assert mean == pytest.approx(exp, rel=0.20), (
        f"uniform random sequence returned {mean:.1f} near-matches per design against an "
        f"expectation of {exp:.1f}; the scan and the null disagree")
    # The gap-paired sub-stratum has its own combinatorial and must land too.
    gexp = rec["null_model"]["expected_per_design"]["gap_paired_le2"]
    gmean = sum(r["counts"]["gap_paired_le2"] for r in rec["per_design"]) / len(obs)
    assert gmean == pytest.approx(gexp, rel=0.30)


# --------------------------------------------------------------------------------------------
# annotation: hybridisable is MEASURED, not assumed
# --------------------------------------------------------------------------------------------
def _gtf(tmp_path, rows):
    os.makedirs(str(tmp_path), exist_ok=True)
    p = str(tmp_path / "a.gtf")
    with open(p, "w", encoding="ascii") as fh:
        for seq, feat, a, b, st, attrs in rows:
            fh.write(f"{seq}\ttest\t{feat}\t{a}\t{b}\t.\t{st}\t.\t{attrs}\n")
    return p


PLUS_GENE = [
    ("C1", "gene", 1, 3000, "+", 'gene_id "G1"; gene_name "PLUSG"; gene_biotype "protein_coding";'),
    ("C1", "exon", 1, 300, "+", 'gene_id "G1"; transcript_id "T1"; gene_name "PLUSG";'),
    ("C1", "exon", 2000, 3000, "+", 'gene_id "G1"; transcript_id "T1"; gene_name "PLUSG";'),
]


def test_a_sense_hit_needs_a_plus_strand_transcription_unit_to_be_hybridisable(tmp_path):
    """★ THIS IS WHAT MAKES `hybridisable` A MEASURED PROPERTY GENOME-WIDE RATHER THAN AN
    ASSUMPTION. A plus-strand match to the target sequence is only reachable by the gapmer if an
    annotated transcript runs in the direction that puts that sequence into an RNA."""
    s = _plant(_rand(4000, 101), 1000, TARGETS[0])          # sense, inside the + gene's intron
    s = _plant(s, 3500, TARGETS[0])                          # sense, outside every gene
    gtf = _gtf(tmp_path, PLUS_GENE)
    rec = _run(tmp_path, {"C1": s}, chunk_nt=700, gtf=gtf)
    by = {h["start"]: h for row in rec["per_design"] for h in row["sites"]
          if h["mismatches"] == 0}
    assert by[1000]["hybridisable"] is True and by[1000]["compartment"] == "intronic"
    assert by[1000]["genes"] == ["PLUSG"] and by[1000]["biotypes"] == ["protein_coding"]
    assert by[3500]["hybridisable"] is False and by[3500]["compartment"] == "intergenic"
    assert by[3500]["genes"] == []


def test_a_reverse_complement_hit_inside_a_plus_strand_gene_is_not_hybridisable(tmp_path):
    """The mirror case, and the one that would invent a liability no transcript carries."""
    s = _plant(_rand(4000, 102), 1000, m.rc(TARGETS[0]))
    gtf = _gtf(tmp_path, PLUS_GENE)
    rec = _run(tmp_path, {"C1": s}, chunk_nt=700, gtf=gtf)
    h = [x for row in rec["per_design"] for x in row["sites"] if x["start"] == 1000][0]
    assert h["orientation"] == "antisense"
    assert h["required_transcript_strand"] == "-"
    assert h["hybridisable"] is False


def test_the_compartment_is_computed_against_the_strand_that_could_be_engaged(tmp_path):
    """⚠ A position can be a + gene's intron and a - gene's exon at once. Calling it exonic because
    SOME annotated exon covers it would attribute an exonic liability to a design whose
    hybridisable partner is intronic — backwards for the question section 3.8 asks."""
    rows = PLUS_GENE + [
        ("C1", "gene", 900, 1200, "-", 'gene_id "G2"; gene_name "MINUSG"; gene_biotype "lncRNA";'),
        ("C1", "exon", 900, 1200, "-", 'gene_id "G2"; transcript_id "T2"; gene_name "MINUSG";'),
    ]
    s = _plant(_rand(4000, 103), 1000, TARGETS[0])           # sense -> needs the + gene
    rec = _run(tmp_path, {"C1": s}, chunk_nt=700, gtf=_gtf(tmp_path, rows))
    h = [x for row in rec["per_design"] for x in row["sites"] if x["start"] == 1000][0]
    assert h["hybridisable"] is True
    assert h["genes"] == ["PLUSG"], "the strand-matched gene is the one the compartment is about"
    assert h["compartment"] == "intronic", (
        "the overlapping minus-strand EXON must not make a plus-strand intronic hit read as exonic")


def test_a_hit_straddling_an_exon_boundary_is_classified_as_spanning(tmp_path):
    s = _plant(_rand(4000, 104), 290, TARGETS[0])            # exon ends at 1-based 300 -> 0-based 299
    rec = _run(tmp_path, {"C1": s}, chunk_nt=700, gtf=_gtf(tmp_path, PLUS_GENE))
    h = [x for row in rec["per_design"] for x in row["sites"] if x["start"] == 290][0]
    assert h["compartment"] == "intron_exon_spanning"


def test_the_splice_distance_excludes_transcript_terminal_boundaries(tmp_path):
    """⚠ A transcript's first exon start is a TSS and its last exon end a polyA site, not splice
    sites. Counting them would put a spurious `0 nt from a splice site` on every hit in a
    single-exon gene, and this arm exists partly to check a splice-site-spanning liability."""
    s = _plant(_rand(4000, 105), 400, TARGETS[0])
    rec = _run(tmp_path, {"C1": s}, chunk_nt=700, gtf=_gtf(tmp_path, PLUS_GENE))
    h = [x for row in rec["per_design"] for x in row["sites"] if x["start"] == 400][0]
    # Real splice sites here are 0-based 299 (donor) and 1999 (acceptor); 0 and 2999 are terminal.
    assert h["nt_to_nearest_splice_site"] == 400 - 299
    single = [("C1", "gene", 1, 3000, "+", 'gene_id "S1"; gene_name "SOLO"; gene_biotype "lncRNA";'),
              ("C1", "exon", 1, 3000, "+", 'gene_id "S1"; transcript_id "TS"; gene_name "SOLO";')]
    rec2 = _run(tmp_path / "b", {"C1": s}, chunk_nt=700, gtf=_gtf(tmp_path / "b", single))
    h2 = [x for row in rec2["per_design"] for x in row["sites"] if x["start"] == 400][0]
    assert h2["nt_to_nearest_splice_site"] is None, (
        "a single-exon transcript has no splice site; reporting a distance to its TSS would be a "
        "measurement of the wrong thing")


def test_the_soft_mask_fraction_is_read_from_letter_case(tmp_path):
    s = _rand(3000, 106)
    s = _plant(s, 500, TARGETS[0].lower())
    s = _plant(s, 1500, TARGETS[0][:8].lower() + TARGETS[0][8:])
    s = _plant(s, 2500, TARGETS[0])
    rec = _run(tmp_path, {"C1": s}, chunk_nt=400)
    by = {h["start"]: h for row in rec["per_design"] for h in row["sites"] if h["mismatches"] == 0}
    assert by[500]["softmask_fraction"] == 1.0
    assert by[1500]["softmask_fraction"] == pytest.approx(0.5)
    assert by[2500]["softmask_fraction"] == 0.0
    split = rec["headline"]["stratum_4_repeat_split"]["hits_by_softmask"]
    assert split["full"] >= 1 and split["partial"] >= 1 and split["none"] >= 1


# --------------------------------------------------------------------------------------------
# named targets, the headline, and the scientific constraint
# --------------------------------------------------------------------------------------------
def test_the_nr4a_family_is_matched_from_the_annotation_rather_than_typed(tmp_path):
    """One fact, one place: the paralogue set is whatever the GTF calls NR4A*, so a screen against
    a newer annotation picks up a renamed or added paralogue without an edit here."""
    rows = [("C1", "gene", 1, 3000, "+",
             'gene_id "N2"; gene_name "NR4A2"; gene_biotype "protein_coding";'),
            ("C1", "exon", 1, 3000, "+", 'gene_id "N2"; transcript_id "TN"; gene_name "NR4A2";')]
    s = _plant(_rand(4000, 107), 1000, TARGETS[0])
    rec = _run(tmp_path, {"C1": s}, chunk_nt=700, gtf=_gtf(tmp_path, rows))
    st3 = rec["headline"]["stratum_3_named_targets"]
    assert "NR4A2" in st3["nr4a_family_matched_from_annotation"]
    assert "NR4A2" in st3["named_gene_set"]
    # The six parents come from the atlas, not from a list in this module.
    assert set(st3["parent_genes"]) <= set(st3["named_gene_set"])
    assert st3["n_named_sites_gap_paired_and_hybridisable"] >= 1
    assert "NR4A2" in st3["genes_hit_gap_paired_and_hybridisable"]


def test_a_named_target_hit_is_retained_in_full_even_beyond_the_retention_cap(tmp_path):
    """"One named hit outranks the entire total" is only true if the cap cannot swallow one."""
    rows = [("C1", "gene", 1, 6000, "+",
             'gene_id "N3"; gene_name "NR4A3"; gene_biotype "protein_coding";'),
            ("C1", "exon", 1, 200, "+", 'gene_id "N3"; transcript_id "TN"; gene_name "NR4A3";')]
    s = _plant(_rand(6000, 108), 3000, TARGETS[0])
    old = m.RETAINED_SITES_PER_WINDOW
    m.RETAINED_SITES_PER_WINDOW = 0
    try:
        rec = _run(tmp_path, {"C1": s}, chunk_nt=700, gtf=_gtf(tmp_path, rows))
    finally:
        m.RETAINED_SITES_PER_WINDOW = old
    rows_with = [r for r in rec["per_design"] if r["n_named_target_sites"]]
    assert rows_with and all(r["n_sites_retained"] == 0 for r in rec["per_design"])
    assert any(h["start"] == 3000 for r in rows_with for h in r["named_target_sites"])
    assert any(h["start"] == 3000 for r in rec["per_design"] for h in r["exact_sites"])


def test_counts_are_complete_even_where_site_records_are_capped(tmp_path):
    """⛔ `junction_aso_offtarget` paid for this lesson: a retention depth that is invisible in the
    output turns a censored count into a measurement. Counts here are never capped and the artifact
    reports n_counted beside n_retained."""
    s = _rand(20_000, 109)
    for i in range(10):
        s = _plant(s, 500 + 700 * i, TARGETS[0])
    old = m.RETAINED_SITES_PER_WINDOW
    m.RETAINED_SITES_PER_WINDOW = 3
    try:
        rec = _run(tmp_path, {"C1": s}, chunk_nt=1500)
    finally:
        m.RETAINED_SITES_PER_WINDOW = old
    capped = [r for r in rec["per_design"] if r["n_sites_counted"] > 3]
    assert capped, "the fixture did not produce enough hits to exercise the cap"
    for r in capped:
        assert r["n_sites_retained"] == 3
        assert r["n_sites_counted"] == r["counts"]["le2"]
    assert rec["method"]["retained_sites_per_window"] == 3


def test_the_headline_is_stratified_and_says_a_raw_total_is_not_a_finding(tmp_path):
    """⛔⛔ THE SCIENTIFIC CONSTRAINT, ASSERTED. `offtarget_chance_baseline.py` had to kill exactly
    this error once already: a count at this threshold is a property of 4**16 and the size of the
    corpus, not of EMC, NR4A3 or fusion junctions. A future edit that reduced this artifact to a
    total would pass every other test in this file."""
    rec = _run(tmp_path, {"C1": _rand(4000, 110)}, chunk_nt=1000)
    h = rec["headline"]
    for stratum in ("stratum_1_exact_matches", "stratum_2_observed_over_expected",
                    "stratum_3_named_targets", "stratum_4_repeat_split"):
        assert stratum in h, f"{stratum} is what makes this readable as anything but a total"
    assert "4**" in h["_read_this_first"] or "4**" in rec["null_model"]["_read_this_first"]
    assert any("NOT a safety assessment" in x for x in rec["_what_this_is_not"])
    assert any("scrambled control" in x for x in rec["_what_this_is_not"])
    # Every per-design row carries its ratio to chance, which is what discriminates between designs.
    for r in rec["per_design"]:
        assert set(r["observed_over_expected"]) == {"exact", "le1", "le2", "gap_paired_le2"}
    assert h["stratum_1_exact_matches"]["expected_per_design"] is not None


def test_the_artifact_records_the_geometry_and_threshold_it_was_produced_under(tmp_path):
    """⛔ `junction_aso_offtarget` records that inferring a run's parameters from its output FAILED
    IN PRINT. Four knobs here are environment-overridable, so the artifact states all of them."""
    rec = _run(tmp_path, {"C1": _rand(2000, 111)}, chunk_nt=500)
    meth = rec["method"]
    assert meth["oligo_len"] == m.OLIGO_LEN and meth["wing"] == m.WING
    assert meth["max_mismatches"] == m.MAX_MM
    assert meth["gap_region_1based"] == list(m.GAP_1BASED)
    assert "junction_aso_offtarget" in meth["max_mismatches_source"]
    assert meth["chunk_nt"] == 500 and meth["chunk_overlap_nt"] == K - 1
    assert meth["retained_sites_per_window"] == m.RETAINED_SITES_PER_WINDOW


# --------------------------------------------------------------------------------------------
# checkpoint and resume
# --------------------------------------------------------------------------------------------
def test_a_partial_checkpoint_resumes_and_reproduces_the_uninterrupted_result(tmp_path):
    """CLAUDE.md section 6: the partial checkpoint is the deliverable on a timeout. A resume that
    silently restarted the record would be slow; one that silently skipped it would be wrong."""
    seqs = {"C1": _plant(_rand(9000, 121), 5500, TARGETS[0]),
            "C2": _plant(_rand(3000, 122), 1200, TARGETS[1])}
    fa = _write_fasta(str(tmp_path / "g.fa"), seqs)
    ck = str(tmp_path / "ck")
    whole = m.scan_genome(fa, None, ckpt_dir=str(tmp_path / "ck0"), chunk_nt=1000,
                          resume=False, progress=False, inputs=_inputs())

    # Force a checkpoint after every chunk, then truncate the run by hand: keep C1's partial
    # checkpoint and delete C2's entirely, which is what a killed runner leaves behind.
    old = m.CKPT_MIN_INTERVAL_S
    m.CKPT_MIN_INTERVAL_S = -1
    try:
        m.scan_genome(fa, None, ckpt_dir=ck, chunk_nt=1000, resume=False, progress=False,
                      inputs=_inputs())
        st = json.load(open(os.path.join(ck, "C1.json")))
        assert st["complete"] is True and st["chunks_done"] >= 5
        st["complete"] = False
        st["chunks_done"] = 2
        st["next_start"] = 2000
        st["windows_total"] = 2000
        st["windows_with_N"] = 0
        st["softmasked_nt"] = 0
        st["nt"] = 0
        for row in st["rows"].values():
            for key in row["counts"]:
                row["counts"][key] = 0
            for key in row["by_compartment"]:
                row["by_compartment"][key] = 0
            for key in row["by_softmask"]:
                row["by_softmask"][key] = 0
            row["n_counted"] = 0
            row["sites"] = []
            row["exact_sites"] = []
            row["named_sites"] = []
        with open(os.path.join(ck, "C1.json"), "w") as fh:
            json.dump(st, fh)
        os.remove(os.path.join(ck, "C2.json"))
        resumed = m.scan_genome(fa, None, ckpt_dir=ck, chunk_nt=1000, resume=True,
                                progress=False, inputs=_inputs())
    finally:
        m.CKPT_MIN_INTERVAL_S = old

    assert _scanned_set(resumed) == _scanned_set(whole)
    assert resumed["denominator"] == whole["denominator"]


def test_a_completed_checkpoint_is_not_rescanned(tmp_path):
    seqs = {"C1": _plant(_rand(4000, 131), 1000, TARGETS[0])}
    fa = _write_fasta(str(tmp_path / "g.fa"), seqs)
    ck = str(tmp_path / "ck")
    first = m.scan_genome(fa, None, ckpt_dir=ck, chunk_nt=1000, resume=False, progress=False,
                          inputs=_inputs())
    # Rewrite the FASTA with different sequence; a resume must return the CHECKPOINT's answer.
    _write_fasta(str(tmp_path / "g.fa"), {"C1": _rand(4000, 999)})
    again = m.scan_genome(fa, None, ckpt_dir=ck, chunk_nt=1000, resume=True, progress=False,
                          inputs=_inputs())
    assert _scanned_set(again) == _scanned_set(first)


def test_a_corrupt_checkpoint_is_discarded_rather_than_trusted(tmp_path):
    seqs = {"C1": _plant(_rand(4000, 141), 1000, TARGETS[0])}
    fa = _write_fasta(str(tmp_path / "g.fa"), seqs)
    ck = str(tmp_path / "ck")
    good = m.scan_genome(fa, None, ckpt_dir=ck, chunk_nt=1000, resume=False, progress=False,
                         inputs=_inputs())
    with open(os.path.join(ck, "C1.json"), "w") as fh:
        fh.write('{"name": "C1", "rows": {"AC')
    again = m.scan_genome(fa, None, ckpt_dir=ck, chunk_nt=1000, resume=True, progress=False,
                          inputs=_inputs())
    assert _scanned_set(again) == _scanned_set(good)


def test_a_truncated_fasta_refuses_to_reduce_rather_than_reporting_a_whole_denominator(tmp_path):
    """An unfinished record must not be stamped complete; a denominator that reads as whole and is
    not would move every ratio in the artifact by an unknown factor."""
    fa = str(tmp_path / "g.fa")
    _write_fasta(fa, {"C1": _rand(2000, 151)})
    real_iter = m.iter_fasta_chunks

    def truncating(*a, **kw):
        for item in real_iter(*a, **kw):
            if item[0] == "eor":
                return                       # the reader dies before the record ends
            yield item

    m.iter_fasta_chunks = truncating
    try:
        with pytest.raises(RuntimeError, match="never reached their end marker"):
            m.scan_genome(fa, None, ckpt_dir=str(tmp_path / "ck"), chunk_nt=500, resume=False,
                          progress=False, inputs=_inputs())
    finally:
        m.iter_fasta_chunks = real_iter


# --------------------------------------------------------------------------------------------
# the CLI contract
# --------------------------------------------------------------------------------------------
def test_check_mode_passes_and_writes_nothing():
    """⛔ `offtarget_chance_baseline.py` records the day a missing `--check` fell through to the
    write path and OVERWROTE the artifact it was asked to verify, exiting 0."""
    before = os.path.exists(m.OUT) and open(m.OUT, "rb").read()
    r = subprocess.run([sys.executable, os.path.join(MOD, "aso_genome_offtarget.py"), "--check"],
                       capture_output=True, text=True, cwd=MOD)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "checks pass" in r.stderr
    after = os.path.exists(m.OUT) and open(m.OUT, "rb").read()
    assert before == after, "--check wrote to the artifact it was asked to verify"


def test_the_self_check_actually_checks_the_kernel_and_would_fail_on_a_broken_one(monkeypatch):
    """A green self-check that cannot go red is a report, not a gate."""
    assert all(c["pass"] for c in m.self_check(verbose=False))
    monkeypatch.setattr(m, "brute_mismatches", lambda a, b: 99)
    res = m.self_check(verbose=False)
    assert any(not c["pass"] for c in res), "self_check passed with a sabotaged reference"


def test_running_with_no_fasta_explains_where_the_screen_runs_instead_of_failing_silently():
    r = subprocess.run([sys.executable, os.path.join(MOD, "aso_genome_offtarget.py")],
                       capture_output=True, text=True, cwd=MOD)
    assert r.returncode == 2
    assert "dna_sm" in r.stderr and "--synthetic" in r.stderr


def test_the_module_refuses_rather_than_substituting_when_numpy_is_missing(monkeypatch):
    """★ THE PRECEDENT IS `junction_aso_thermo.py`. There is no honest degraded mode here: a pure
    Python fallback would be a different instrument under the same artifact name, and far too slow
    to finish, so it would leave a partial scan that reads as a whole one."""
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) \
        else __builtins__.__import__

    def blocked(name, *a, **kw):
        if name == "numpy":
            raise ImportError("blocked for this test")
        return real_import(name, *a, **kw)

    monkeypatch.setitem(sys.modules, "numpy", None)
    monkeypatch.setattr("builtins.__import__", blocked)
    with pytest.raises(SystemExit) as e:
        m._require_numpy()
    assert "REFUSED" in str(e.value) and "numpy" in str(e.value)


def test_the_module_contains_no_network_code_at_all():
    """★ WHAT MAKES `--offline` AN ASSERTION RATHER THAN A MODE. The reference is always passed in,
    so there is no fetch to disable — and the honest way to say that is to hold the property rather
    than to document it. If a fetcher is ever added, `--offline` stops being a restatement and this
    test is where that has to be noticed."""
    src = open(os.path.join(MOD, "aso_genome_offtarget.py"), encoding="utf-8").read()
    code = "\n".join(l for l in src.splitlines()
                     if not l.lstrip().startswith("#") and not l.lstrip().startswith("⚠"))
    for token in ("urllib", "requests", "http.client", "socket", "ftplib", "subprocess"):
        assert f"import {token}" not in code, f"{token} appeared in a module that must not fetch"


def test_an_unsupported_gapmer_geometry_is_refused_rather_than_allocating_137_GB(monkeypatch):
    """⛔ `aso-offtarget.yml` has a `gapmer_geometry` input and `junction_aso` reads OLIGO_LEN from
    the environment. At length 20 the bitmap is 4**20/8 bytes and the code no longer fits a uint32,
    so the verified kernel would not be the kernel that ran."""
    monkeypatch.setattr(m, "OLIGO_LEN", 20)
    with pytest.raises(SystemExit) as e:
        m._require_supported_geometry()
    assert "REFUSED" in str(e.value) and "uint32" in str(e.value)


def test_a_run_without_an_annotation_says_so_in_the_artifact(tmp_path, capsys):
    """⚠ Without a GTF every hit is intergenic and not hybridisable — the cleanest-looking artifact
    this module can emit, and a statement about the missing annotation rather than about the genome.
    An absent reading is not a reading of absence."""
    rec = _run(tmp_path, {"C1": _plant(_rand(3000, 161), 500, TARGETS[0])}, chunk_nt=700)
    assert rec["reference"]["gtf"] is None
    assert rec["reference"]["annotation"].startswith("NONE")
    assert "NOT of the genome" in rec["reference"]["annotation"]
    assert "::warning::no GTF" in capsys.readouterr().err
    assert all(not h["hybridisable"] for r in rec["per_design"] for h in r["sites"])


def test_the_workflow_offers_the_genome_mode_without_adding_a_dispatch_input():
    """⛔ `aso-offtarget.yml` sits AT GitHub's cap of 10 dispatch inputs. An 11th does not fail: it
    silently delivers EVERY input as empty (`test_workflow_dispatch_input_cap.py`). So the genome
    screen has to be a new value on the existing `screen_mode` choice, and this asserts the shape
    stayed that way rather than trusting a comment."""
    yaml = pytest.importorskip("yaml")
    p = os.path.join(REPO, ".github/workflows/aso-offtarget.yml")
    d = yaml.safe_load(open(p, encoding="utf-8"))
    on = d.get(True, d.get("on"))
    ins = on["workflow_dispatch"]["inputs"]
    assert len(ins) <= 10, f"{len(ins)} dispatch inputs: every -f flag would arrive empty"
    assert "genome" in ins["screen_mode"]["options"]
    text = open(p, encoding="utf-8").read()
    assert "aso_genome_offtarget.py" in text
    assert "dna_sm.primary_assembly" in text, "the soft-masked reference is what the repeat split needs"
