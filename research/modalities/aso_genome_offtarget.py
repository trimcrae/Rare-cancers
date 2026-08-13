#!/usr/bin/env python3
"""Screen every junction gapmer against the WHOLE GENOME — every intron of every gene, exhaustively.

⭐ WHY THIS EXISTS. `aso_premrna_offtarget.py` closed the compartment the manuscript concedes is
unmeasured, but only for the six parent transcripts — a span of order 5e5 nt, which is the sum of
`genes[].premrna_nt` in `aso-premrna-offtarget.json` and is not restated here. Its own
`_what_this_is_not` says the rest in as many words: "it covers six parent transcripts' pre-mRNA
exhaustively and says nothing about the other ~20,000 genes' introns". RNase-H1 is nuclear, and §3.8
of the manuscript found this modality's most interesting liability IN INTRONIC SEQUENCE (a route to
wild-type *NR4A3* across the intron-2/exon-3 boundary, reachable without passing through the fusion
at all). A liability class that has already produced the paper's most decision-relevant finding,
measured over four orders of magnitude less sequence than it lives in, is not a screen: it is a
pilot. ⚠ That ratio is deliberately stated as an order and not as a percentage, because its
denominator — the scanned span of the genome — is the thing THIS module measures rather than
assumes, and it lands in `denominator.windows_scanned` of the artifact this file writes.

⛔ AND THE ONE PRIOR ATTEMPT AT EVERYTHING THE PILOT MISSED COULD NOT HAVE PRODUCED AN ANSWER. It is
recorded, released so nobody repeats it, in `aso-premrna-offtarget-genomic.json`: NCBI's URL service
answered on `core_nt`, a mixed corpus of assemblies, BAC clones, patent sequence and transcripts
rather than a genome reference. Two defects, and the second is the instructive one.
  (a) `core_nt` HAS NO DEFINED NUCLEOTIDE SPAN, so no null can be formed against it. A count with no
      denominator cannot be graded, and grading against chance is the only thing that makes an
      off-target count mean anything at this threshold (`offtarget_chance_baseline.py`).
  (b) THE 50-HIT CAP SAT BELOW THE NULL'S OWN LOWER BOUND. §3.6 of the manuscript works this out for
      the transcriptome arm — the cap is 50 and chance alone predicts 79 on one strand and 158 on
      two — so every query saturates whatever the corpus contains. The arm could not have returned an
      interpretable number under ANY outcome. It was not a failed measurement; it was an instrument
      that had no reading to give.
Both defects are structural, and this module is built to have neither: the denominator is MEASURED
(every scanned nucleotide is counted, and the artifact records it), and nothing is capped at scan
time — every position of every sequence is tested and every hit is COUNTED, with only the per-window
retention of individual site RECORDS bounded, which the artifact states as a number rather than
leaving to be inferred.

★ WHAT THIS DOES, EXACTLY.
For every distinct 16-mer target window in the atlas AND its reverse complement, the complete
≤2-substitution neighbourhood is enumerated as 2-bit-packed `uint32` codes and set in a `4**16`-bit
membership bitmap. The genome FASTA is then streamed once, a `uint32` code rolled per position, and
one bitmap probe taken per position. Because the reverse complements are in the bitmap, scanning the
plus strand once covers both orientations.

⭐ EXHAUSTIVENESS IS DEFINITIONAL HERE, NOT ARGUED. Every position is tested against the complete
neighbourhood; there is no seed, no word size, no heuristic and therefore no sensitivity to quantify.
That is a real improvement on the manuscript's BLAST arm, whose sensitivity the paper concedes is
unquantified, and on the pre-mRNA arm, whose completeness rests on a pigeonhole argument that has to
be re-earned every time the threshold moves. Here the threshold can move and the guarantee does not.

⛔⛔ THE MISTAKE THIS FILE IS SHAPED TO AVOID, AND IT HAS ALREADY BEEN MADE ONCE IN THIS REPOSITORY.
A raw genome-wide count at this threshold IS NOT A FINDING. It is a restatement of 4**16.
`offtarget_chance_baseline.py` killed exactly this error at transcriptome scale, in its own words:
"'Zero near-matches at >= 14/16' is not an achievable state, so a count of zero-clean designs is a
property of the threshold and the size of the transcriptome, not a property of EMC, NR4A3, or fusion
junctions." Over a genome, both orientations, the same independent-uniform null predicts of ORDER ONE
exact 16/16 site per design, of order 10^1-10^2 at >= 15/16, and of order 10^3 at >= 14/16 — FOR ANY
16-MER WHATSOEVER, a scrambled control or a random string included. Publishing a four-figure count as
"off-target sites per candidate" would re-commit the killed error at genome scale, and a reader would
take it for a safety finding when it is a fact about arithmetic. ⛔ NOTE THAT THOSE THREE ORDERS ARE
THE ONLY FORM THIS PARAGRAPH IS ALLOWED TO STATE THEM IN: every expectation the artifact reports is
COMPUTED at run time from the denominator this module MEASURES, and pinning a figure here would give
it a second home that the next assembly release silently falsifies.

★ SO THE HEADLINE IS STRATIFIED AND NULL-REFERENCED, in four parts, and the artifact is built in
this order deliberately:
  1. STRATA WHERE CHANCE EXPECTATION IS O(1). Exact 16/16 is ~1 expected per design over the whole
     genome and both orientations, so an individual exact site is checkable by hand and an excess is
     real. This is the class to lead on, and it is exactly the class the `core_nt` arm could never
     reach, because its cap sat two orders of magnitude below where these sites live in the ranking.
  2. OBSERVED VERSUS EXPECTED, PER DESIGN — the grammar §3.6 and Figure 3 already use. A ratio near 1
     means "no worse than an arbitrary 16-mer", which is the defensible statement and the one a
     chemist wants; a ratio of 5 is an excess that needs explaining. This is what discriminates
     BETWEEN designs, which a total never can.
  3. THE NAMED-TARGET QUESTION, WHICH IS A LOOKUP AND NOT A COUNT. Does any design have a gap-paired,
     sense-strand site in wild-type *NR4A3*, in any of the six parent genes, or in the *NR4A*
     paralogues? One named hit outranks the entire total, and the total cannot answer it.
  4. THE REPEAT SPLIT, free from a soft-masked reference. Hits partitioned by soft-mask state convert
     the null's single largest inflation source from a caveat into a measurement.

⚠ WHAT A HIT IS AND IS NOT. `hybridisable` is MEASURED here rather than assumed, which is the whole
point of pairing the scan with an annotation: a plus-strand match is hybridisable only if an
annotated transcription unit runs in the orientation that would put the target sequence into an RNA.
A hit in unannotated sequence is reported as intergenic and NOT hybridisable, because no annotated
RNA carries it — that is a statement about the annotation, not about the DNA, and unannotated
transcription is real and is a stated blind spot. And as everywhere in this work: a paired
six-nucleotide gap is NECESSARY for RNase-H1 cleavage and is not SUFFICIENT, and nothing here
measures activity.

    python3 research/modalities/aso_genome_offtarget.py --check        # offline, writes nothing
    python3 research/modalities/aso_genome_offtarget.py --synthetic    # end-to-end, no network
    python3 research/modalities/aso_genome_offtarget.py \
        --fasta Homo_sapiens.GRCh38.dna_sm.primary_assembly.fa.gz \
        --gtf   Homo_sapiens.GRCh38.<release>.gtf.gz                   # the real screen (CI)
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import sys
import time
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
#: ⛔ THE DESIGN SET IS A KNOB, BECAUSE `GENOME_OUT` ALREADY WAS AND HALF A PARAMETERISATION IS THE
#: DANGEROUS HALF (2026-08-13). The output filename could already be moved aside while the INPUT
#: could not, so a run asked for a second geometry's output would have written the 16-mer designs'
#: genome hits under the longer geometry's name — a correct scan, filed as a measurement of designs
#: it never saw. Everything downstream of here derives its window length and gap mask from the
#: designs themselves, so pointing this at another atlas is all a different geometry needs.
ATLAS = os.path.join(HERE, os.environ.get("ATLAS_JSON") or "nr4a3-fusion-junction-atlas.json")
OUT = os.path.join(HERE, os.environ.get("GENOME_OUT", "aso-genome-offtarget.json"))
CKPT_DIR = os.environ.get("GENOME_CKPT_DIR") or os.path.join(HERE, "aso-genome-offtarget-ckpt")

_BASES = "ACGT"


# --------------------------------------------------------------------------------------------
# numpy, and an honest refusal in its absence
# --------------------------------------------------------------------------------------------
def _require_numpy():
    """numpy or a REFUSAL — never a hand-rolled substitute.

    ⛔ THE PRECEDENT IS `junction_aso_thermo.py`, WHICH REFUSES RATHER THAN INVENTS. This screen's
    entire correctness argument is that the packed-Hamming kernel reproduces brute force EXACTLY over
    the whole 16-mer alphabet, and that argument is about `np.bitwise_count` over `uint32`. A pure
    Python fallback would be a DIFFERENT instrument wearing the same artifact name and the same
    provenance string, and it would be ~100x too slow to finish, so it would be abandoned mid-genome
    and leave a partial artifact that reads as a whole one. There is no honest degraded mode here.

    ⚠ `np.bitwise_count` arrived in numpy 2.0. An older numpy is refused by NAME rather than
    silently routed through a `popcount` written here, for the same reason.
    """
    try:
        import numpy as np  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        raise SystemExit(
            "REFUSED: numpy is not installed, so the genome scan cannot run. This screen is a "
            "2-bit-packed bitmap probe over 3.1e9 positions; a pure-Python substitute would be a "
            "different instrument and far too slow to finish, and a partial scan published under "
            "this artifact's name would read as a whole one. Install numpy>=2.0 (it is present on "
            "the CI runner this is meant to run on) and re-run.\n"
            f"  import error: {type(e).__name__}: {e}") from e
    if not hasattr(np, "bitwise_count"):
        raise SystemExit(
            f"REFUSED: numpy {np.__version__} has no `bitwise_count`, which arrived in numpy 2.0 "
            "and is the operation this screen's mismatch kernel is verified against. A popcount "
            "written here would be an unverified second implementation of the one thing that must "
            "be exactly right. Upgrade to numpy>=2.0.")
    return np


# --------------------------------------------------------------------------------------------
# geometry and threshold — DERIVED from the owning modules, never re-typed
# --------------------------------------------------------------------------------------------
def _max_mismatches():
    """The mismatch ceiling, taken from the module that owns it.

    ⛔ SAME REASON `aso_premrna_offtarget._max_mismatches` GIVES: the arms have to ask the same
    question or the comparison between them is an artefact. Ask the genome a stricter question than
    the transcriptome and it comes back cleaner for that reason alone, which would read as "the rest
    of the genome is fine" and is the most flattering possible way to be wrong.
    """
    sys.path.insert(0, HERE)
    from junction_aso_offtarget import MAX_MISMATCHES_PER_NEAR_MATCH  # noqa: PLC0415
    return int(MAX_MISMATCHES_PER_NEAR_MATCH)


def _geometry():
    """`(oligo_len, wing, (gap_lo, gap_hi) 1-based inclusive, provenance)` from `junction_aso`.

    ⛔⛔ THIS IS DERIVED FROM `WING` AND `OLIGO_LEN` BECAUSE THE OBVIOUS IMPORT IS A DEAD ONE, AND
    THAT WAS MEASURED HERE RATHER THAN ASSUMED (2026-08-13). `aso_premrna_offtarget._gap_region()`
    docstring says the gap is "imported rather than re-typed where possible" and tries
    `from junction_aso_offtarget import GAP_REGION_1BASED`. That name EXISTS NOWHERE IN THIS
    REPOSITORY — `grep -rn GAP_REGION_1BASED research/modalities/*.py` returns only the import
    statement and the line that returns it. So the import has always raised, the bare `except`
    has always swallowed it, and the value in every pre-mRNA artifact is the module's own literal
    fallback `(6, 11)`.
    ⚠ IT HAS NEVER BEEN WRONG, WHICH IS WHY NOBODY NOTICED: `(6, 11)` is what a 5-6-5 16-mer
    yields. But `aso-offtarget.yml` carries a `gapmer_geometry` input, and a `20,5` dispatch makes
    the true gap `(6, 15)` while the fallback keeps saying `(6, 11)` — a screen that would silently
    resolve two thirds of a 5-10-5 gapmer's gap and report it as the whole one. A fallback that is
    only correct for the default is not a fallback; it is a second definition waiting for a
    dispatch. So this derives the gap from the two constants that genuinely own it, and the
    artifact records WHICH route produced the value.
    """
    sys.path.insert(0, HERE)
    import junction_aso as ja  # noqa: PLC0415
    length, wing = int(ja.OLIGO_LEN), int(ja.WING)
    # The catalytic DNA gap is the centre block: 0-based half-open [wing, length - wing), which is
    # 1-based inclusive (wing + 1, length - wing). Same arithmetic as `junction_aso`'s own
    # `gap_start, gap_end = start + WING, end - WING`.
    return length, wing, (wing + 1, length - wing), "derived from junction_aso.OLIGO_LEN and .WING"


OLIGO_LEN, WING, GAP_1BASED, GAP_SOURCE = _geometry()
MAX_MM = _max_mismatches()

#: The only oligo length whose complete code space fits a `uint32` and a 512 MiB bitmap.
#: ⛔ THIS IS A REFUSAL, NOT A DEFAULT, AND IT IS NEEDED BECAUSE THE GEOMETRY IS DISPATCHABLE.
#: `aso-offtarget.yml` carries a `gapmer_geometry` input, and `junction_aso` reads `OLIGO_LEN` from
#: the environment. At length 20 the membership bitmap is `4**20 / 8` bytes — 137 GB — and the
#: rolling code no longer fits the `uint32` the kernel is verified over. There is no honest degraded
#: mode: a wider oligo needs a different data structure, not a bigger allocation. Refusing by name
#: is the alternative to an `np.zeros` that dies with a MemoryError nobody can attribute, or worse,
#: a silently truncated code space in which every position matches something.
BITMAP_OLIGO_LEN = 16


def _require_supported_geometry():
    if OLIGO_LEN != BITMAP_OLIGO_LEN:
        raise SystemExit(
            f"REFUSED: this screen is a 2-bit-packed uint32 bitmap over the complete {4 ** 16:,}-code "
            f"space of a {BITMAP_OLIGO_LEN}-mer, and OLIGO_LEN is {OLIGO_LEN} "
            f"(from junction_aso, which reads it from the environment). At length {OLIGO_LEN} the "
            f"bitmap would be {4 ** OLIGO_LEN // 8:,} bytes and the code would not fit a uint32, so "
            f"the kernel this module verifies would not be the kernel it ran. A wider gapmer needs a "
            f"different data structure, not a bigger allocation — unset OLIGO_LEN/WING or build one.")

#: How many individual SITE RECORDS are kept per target window beyond the always-retained classes.
#: ⛔ NAMED, AND REPORTED IN THE ARTIFACT, BECAUSE `junction_aso_offtarget` PAID FOR THAT LESSON:
#: a bare `[:15]` in one place and a typed "15" in four others made a censoring depth into a fact
#: nobody could read off the output. Counts here are NEVER capped — every hit is counted into the
#: stratified table — so this bounds only what a reader can inspect individually, and the artifact
#: records `n_counted` beside `n_retained` per window so the censoring is a measurement.
RETAINED_SITES_PER_WINDOW = int(os.environ.get("GENOME_RETAINED_SITES", "40"))

#: Bases of sequence held in memory at once. Chunks OVERLAP by `OLIGO_LEN - 1` and each chunk owns
#: exactly `CHUNK_NT` window START positions, so no window is missed at a boundary and none is
#: counted twice — see `iter_fasta_chunks`, and `test_a_hit_across_a_chunk_boundary_is_found_once`.
#: ⭐ 2 Mb IS MEASURED, NOT CHOSEN FOR TIDINESS, AND IT BEAT THE OBVIOUS ANSWER. Over a 40 Mb
#: synthetic genome in this sandbox (45.6 % soft-masked, 5.5 % N), one core, plain FASTA:
#:     20 Mb chunks  4.04 Mb/s   1.20 GB peak RSS
#:      8 Mb chunks  4.30 Mb/s   0.88 GB
#:      2 Mb chunks  5.98 Mb/s   0.70 GB      <- default
#:    500 kb chunks  4.77 Mb/s   0.69 GB
#: The scan is memory-bandwidth bound: at 20 Mb a chunk's `codes` array alone is 80 MB and every one
#: of the 16 packing passes streams it through cache. Smaller chunks also lower the ceiling on peak
#: RSS, which is what a shared CI runner actually cares about. Below ~1 Mb the per-chunk overhead
#: starts winning again, which is why this is not simply "as small as possible".
#: ⚠ The hit set is IDENTICAL at every size tested — that is the chunking-invariance property
#: `test_chunking_is_invariant` asserts, measured here across a 40x range before it was asserted.
CHUNK_NT = int(os.environ.get("GENOME_CHUNK_NT", str(2_000_000)))

#: Seconds between mid-record checkpoint writes. A checkpoint is ALWAYS written when a record ends.
#: ⛔ WHY THIS IS A CLOCK AND NOT "EVERY CHUNK", AND THE NUMBER THAT DECIDED IT. CLAUDE.md §6 says
#: checkpoint after each unit of work; the honest reading of that rule is "never lose more than a
#: little", not "write regardless of cost". MEASURED here: one checkpoint at the default retention
#: is 2.77 MB and 138 ms to serialise and fsync-rename. At the 2 Mb chunk above that is 1,550 writes
#: over the genome — 3.6 minutes of pure bookkeeping against a ~9-minute scan, i.e. the checkpoint
#: would cost 40 % of the work it protects. On a clock the exposure is bounded at this many seconds
#: of re-scanning and the overhead is a fraction of a percent.
CKPT_MIN_INTERVAL_S = float(os.environ.get("GENOME_CKPT_INTERVAL_S", "30"))

#: The paralogue family the selectivity question is about, matched from the ANNOTATION's own gene
#: names rather than typed as a list. NR4A1/NR4A2/NR4A3 are what this pattern finds in an Ensembl
#: GTF; writing the symbols here instead would be a second home for a set the GTF already holds.
NR4A_FAMILY_PREFIX = "NR4A"


# --------------------------------------------------------------------------------------------
# packing, the kernel, and the neighbourhood
# --------------------------------------------------------------------------------------------
def pack(seq):
    """A 16-mer as a 2-bit-packed `uint32`, FIRST base in the HIGH bits.

    The bit order is load-bearing and is why `gap_mask` below can be a constant: base `i` (1-based)
    occupies bits `2*(K-i)` and `2*(K-i)+1`, so a contiguous run of bases is a contiguous run of
    bits. At K=16 a code fills a `uint32` exactly, which is the whole reason this design is cheap —
    no masking after the shift, and the membership bitmap is `4**16` bits, 512 MiB, which fits.
    """
    code = 0
    for ch in seq:
        code = (code << 2) | _BASES.index(ch)
    return code


def unpack(code, length=None):
    """The inverse of `pack`, for error messages and tests — a code nobody can read is a bad witness."""
    length = OLIGO_LEN if length is None else length
    return "".join(_BASES[(code >> (2 * (length - 1 - i))) & 3] for i in range(length))


def gap_mask(length=None, gap=None):
    """The bit mask selecting the catalytic gap, DERIVED from the geometry.

    ⚠ At the 5-6-5 16-mer this evaluates to `0x003ffc00`. That value is not typed anywhere: it is
    what the geometry yields, and `test_the_gap_mask_is_derived_not_typed` re-derives it. A geometry
    change moves the mask instead of silently resolving the wrong six nucleotides.
    """
    length = OLIGO_LEN if length is None else length
    lo, hi = GAP_1BASED if gap is None else gap
    m = 0
    for i in range(lo, hi + 1):
        m |= 0b11 << (2 * (length - i))
    return m


GAP_MASK = gap_mask()


def mismatches(np, a, b, mask=None):
    """Hamming distance in BASES between two packed codes, elementwise over arrays.

    ★ THE KERNEL, AND IT IS VERIFIED RATHER THAN ASSERTED. `(x | (x >> 1)) & 0x55555555` sets the low
    bit of every 2-bit group in which `a` and `b` differ, so `bitwise_count` of that is the number of
    differing BASES rather than of differing bits — a distinction that matters, because a
    transversion flips two bits and a transition one, and a bit-count would grade them differently.
    Restricting the same expression with `GAP_MASK` gives the sub-distance over the catalytic gap.
    `--check` re-verifies both against a brute-force implementation over an exhaustive
    <=3-substitution variant set and over random pairs; `tests/test_aso_genome_offtarget.py` does the
    same in CI.
    """
    x = np.asarray(a, dtype=np.uint32) ^ np.asarray(b, dtype=np.uint32)
    d = (x | (x >> np.uint32(1))) & np.uint32(0x55555555)
    if mask is not None:
        d = d & np.uint32(mask)
    return np.bitwise_count(d)


def brute_mismatches(a, b):
    """The reference implementation the kernel is checked against. Deliberately dumb."""
    return sum(1 for x, y in zip(a, b) if x != y)


def n_within(length, k):
    """How many distinct strings lie within `k` substitutions of one string of `length`.

    Same function, same name, same arithmetic as `offtarget_chance_baseline.n_within`. Repeated here
    rather than imported ONLY so this module has no import-time dependency on an artifact-writing
    sibling; `test_the_null_arithmetic_agrees_with_the_committed_chance_baseline` asserts the two
    agree, which is what "one fact, one place" actually requires of a formula.
    """
    return sum(comb(length, j) * 3 ** j for j in range(k + 1))


def n_gap_paired_within(length, gap, k):
    """Neighbourhood size with EVERY substitution outside the catalytic gap.

    This is the null for "pairs the gap in full and is within `k` mismatches overall": the gap's
    `hi - lo + 1` positions must match exactly, so the substitutions are drawn from the remaining
    positions only. At 5-6-5/16 and k=2 it is 436, which is why the gap-paired expectation is
    436/1129 of the >= 14/16 one rather than some fraction assumed by eye.
    """
    lo, hi = gap
    free = length - (hi - lo + 1)
    return sum(comb(free, j) * 3 ** j for j in range(k + 1))


def neighbourhood(seq, max_mm=None):
    """Every packed code within `max_mm` substitutions of `seq`, as a sorted list of ints.

    ⚠ EXACT, NOT SAMPLED, AND THAT IS THE ENTIRE COMPLETENESS ARGUMENT. `|neighbourhood(s)|` must
    equal `n_within(len(s), max_mm)` for every sequence, which is asserted in `--check` and in the
    tests. A neighbourhood that is one code short is a screen that silently cannot see one class of
    near-match, and nothing downstream would ever notice.
    """
    max_mm = MAX_MM if max_mm is None else max_mm
    length = len(seq)
    base = pack(seq)
    out = {base}
    cur = {base}
    for _ in range(max_mm):
        nxt = set()
        for code in cur:
            for i in range(length):
                sh = 2 * (length - 1 - i)
                have = (code >> sh) & 3
                for b in range(4):
                    if b != have:
                        nxt.add((code & ~(0b11 << sh)) | (b << sh))
        out |= nxt
        cur = nxt
    return sorted(out)


def rc(seq):
    return seq.translate(str.maketrans("ACGTN", "TGCAN"))[::-1]


# --------------------------------------------------------------------------------------------
# the membership bitmap
# --------------------------------------------------------------------------------------------
def build_bitmap(np, windows, max_mm=None):
    """`(bitmap, code_index, stats)` — the 4**K-bit membership set and the code -> slot map.

    A SLOT is `(window_index, orientation)`, orientation being `sense` (the plus strand carries the
    design's target sequence, so a plus-strand transcript would carry it into RNA) or `antisense`
    (the plus strand carries the target's reverse complement, so a MINUS-strand transcript carries
    the target). Putting both in one bitmap is what lets the genome be read once, plus strand only,
    while covering both orientations — the scan cost is halved and no reverse-complement pass can
    fall out of step with the forward one.

    ⚠ THE BITMAP IS A FILTER, NOT THE ANSWER. A set bit says "some slot is within `max_mm` of this
    code"; it does not say which, or how far. `code_index` resolves that exactly, and the kernel
    re-measures the distance for every candidate rather than trusting membership. Membership can
    only over-admit (it never misses), so the resolution step can only ever remove candidates —
    which is the safe direction and is asserted by `test_every_bitmap_hit_resolves_to_a_real_slot`.
    """
    _require_supported_geometry()
    max_mm = MAX_MM if max_mm is None else max_mm
    length = len(windows[0])
    t0 = time.time()
    nbytes = (4 ** length) // 8
    bitmap = np.zeros(nbytes, dtype=np.uint8)

    code_index = {}
    slots = []
    for wi, w in enumerate(windows):
        for orient, s in (("sense", w), ("antisense", rc(w))):
            slot = len(slots)
            slots.append({"window_index": wi, "orientation": orient, "seq": s, "code": pack(s)})
            for code in neighbourhood(s, max_mm):
                code_index.setdefault(code, []).append(slot)

    codes = np.fromiter(code_index.keys(), dtype=np.uint64, count=len(code_index))
    np.bitwise_or.at(bitmap, (codes >> np.uint64(3)).astype(np.int64),
                     (np.uint8(1) << (codes & np.uint64(7)).astype(np.uint8)))
    stats = {
        "n_target_windows": len(windows),
        "n_slots": len(slots),
        "n_codes_per_sequence": n_within(length, max_mm),
        "n_distinct_codes": len(code_index),
        "bitmap_bytes": int(nbytes),
        "build_seconds": round(time.time() - t0, 2),
    }
    return bitmap, {k: tuple(v) for k, v in code_index.items()}, slots, stats


# --------------------------------------------------------------------------------------------
# FASTA streaming
# --------------------------------------------------------------------------------------------
def _open_maybe_gz(path):
    return gzip.open(path, "rb") if str(path).endswith(".gz") else open(path, "rb")


def iter_fasta_chunks(path, chunk_nt=None, k=None):
    """Yield `("seq", name, start, raw)` and `("eor", name, total_nt)` over a (possibly gzipped) FASTA.

    ⛔⛔ THE CHUNK BOUNDARY IS THE CLASSIC BUG IN THIS DESIGN AND IT IS SOLVED HERE BY CONSTRUCTION,
    NOT BY CARE. A window starting in the last `k-1` positions of a chunk extends past its end. The
    naive fix — scan each chunk independently — silently DROPS every such window, and the loss is
    invisible: the counts are simply a little low, uniformly, in the flattering direction, with no
    error and no artefact anywhere saying so. Roughly `(k-1)/chunk_nt` of the genome would vanish.
    So each chunk is READ with `chunk_nt + k - 1` bases and OWNS exactly `chunk_nt` window start
    positions; the next chunk begins at the first start position this one did not own. Missed and
    duplicated are then both arithmetically impossible rather than tested for.
    `test_a_hit_across_a_chunk_boundary_is_found_once` plants a hit at a boundary and
    `test_chunking_is_invariant` asserts the whole hit set is identical at chunk sizes that split the
    same genome many different ways, which is the stronger of the two checks.

    ⚠ CHUNKS NEVER CROSS RECORDS. A window spanning the end of chr1 and the start of chr2 would be a
    fabricated site at a coordinate that exists in no genome, and it would look exactly like a real
    one. Records are flushed at every header, and `test_a_window_never_spans_two_records` plants the
    two halves of a target either side of a record boundary and asserts nothing is found.
    """
    chunk_nt = CHUNK_NT if chunk_nt is None else chunk_nt
    k = OLIGO_LEN if k is None else k
    overlap = k - 1
    name, buf, base = None, bytearray(), 0

    def flush_tail():
        # The record's remaining bases: whatever windows start inside them, then the record total.
        if name is None:
            return
        if len(buf) >= k:
            yield ("seq", name, base, bytes(buf))
        yield ("eor", name, base + len(buf))

    with _open_maybe_gz(path) as fh:
        for line in fh:
            if line[:1] == b">":
                yield from flush_tail()
                name = line[1:].split()[0].decode("ascii", "replace")
                buf, base = bytearray(), 0
                continue
            if name is None:
                continue
            buf += line.strip()
            while len(buf) >= chunk_nt + overlap:
                yield ("seq", name, base, bytes(buf[:chunk_nt + overlap]))
                del buf[:chunk_nt]
                base += chunk_nt
        yield from flush_tail()


# --------------------------------------------------------------------------------------------
# the scan
# --------------------------------------------------------------------------------------------
def _lut(np):
    """ASCII byte -> 2-bit base code, with 255 for everything else (N, IUPAC codes, anything)."""
    t = np.full(256, 255, dtype=np.uint8)
    for i, ch in enumerate(_BASES):
        t[ord(ch)] = i
        t[ord(ch.lower())] = i
    return t


def scan_chunk(np, bitmap, raw, k=None, first_chunk=True):
    """`(candidate_offsets, candidate_codes, n_windows, n_windows_with_N, n_new_softmasked_nt)`.

    `raw` is the chunk's ASCII bytes, `chunk_nt + k - 1` of them for every chunk but the last of a
    record; the windows returned are those STARTING inside the owned range, by construction.

    ⚠ SOFT-MASK STATE IS READ FROM CASE, WHICH IS WHY THE REFERENCE MUST BE `dna_sm`. Ensembl's
    `dna_sm` files are soft-masked BY NAME, so the repeat annotation arrives verified rather than
    assumed; a `dna` (unmasked) or `dna_rm` (hard-masked) file would silently make every hit read as
    non-repetitive or delete the repeats from the denominator. `check_reference_looks_soft_masked`
    reads the file and warns rather than trusting the filename.

    ⛔ AND THE SOFT-MASK TOTAL IS DE-OVERLAPPED HERE, NOT LATER. Chunks overlap by `k-1` bases so no
    window is lost at a boundary; the WINDOW arithmetic is exact under that overlap and the
    NUCLEOTIDE arithmetic is not, because those `k-1` bases appear in two chunks. The denominator
    this screen reports is the number the manuscript currently has to ASSUME, so it does not get to
    be approximately right: every chunk after a record's first contributes only the lowercase bases
    OUTSIDE its leading overlap, which are exactly the ones its predecessor did not see.
    """
    k = OLIGO_LEN if k is None else k
    arr = np.frombuffer(raw, dtype=np.uint8)
    is_lower = arr >= 0x61
    lower_new = int(np.count_nonzero(is_lower if first_chunk else is_lower[k - 1:]))
    if arr.size < k:
        return (np.empty(0, dtype=np.int64), np.empty(0, dtype=np.uint32), 0, 0, lower_new)
    v = _lut(np)[arr]
    bad = v > 3
    vc = np.where(bad, np.uint8(0), v).astype(np.uint32)

    nwin = arr.size - k + 1
    codes = np.zeros(nwin, dtype=np.uint32)
    for i in range(k):
        codes <<= np.uint32(2)
        codes |= vc[i:i + nwin]

    # int32 rather than int64: a chunk never holds more than 2**31 bases, and the two prefix arrays
    # are the largest allocations in the scan.
    pre = np.zeros(arr.size + 1, dtype=np.int32)
    np.cumsum(bad, out=pre[1:])
    per_window_bad = pre[k:] - pre[:-k]
    n_bad_windows = int(np.count_nonzero(per_window_bad))

    sel = bitmap[codes >> np.uint32(3)]
    bit = np.uint8(1) << (codes & np.uint32(7)).astype(np.uint8)
    cand = np.flatnonzero(((sel & bit) != 0) & (per_window_bad == 0))
    return cand, codes[cand], nwin, n_bad_windows, lower_new


def check_reference_looks_soft_masked(np, path, k=None, probe_records=2):
    """Refuse a reference whose case says it is not soft-masked.

    ⛔ AN ASSUMPTION ABOUT A FILENAME IS NOT A READING OF A FILE. The repeat split is one of the four
    headline strata and it is derived entirely from letter case, so a reference that is unmasked
    would report every hit as non-repetitive — a clean, plausible, entirely wrong measurement, and
    the flattering direction again. A genome with essentially no lowercase is either `dna` or
    `dna_rm`, and either way the split cannot be made; say so rather than emit it.
    """
    k = OLIGO_LEN if k is None else k
    seen_nt = seen_lower = 0
    records = 0
    for kind, _name, _start, payload in _iter4(iter_fasta_chunks(path, chunk_nt=2_000_000, k=k)):
        if kind == "eor":
            records += 1
            if records >= probe_records and seen_nt:
                break
            continue
        arr = np.frombuffer(payload, dtype=np.uint8)
        seen_nt += int(arr.size)
        seen_lower += int(np.count_nonzero(arr >= 0x61))
        if seen_nt > 20_000_000:
            break
    frac = (seen_lower / seen_nt) if seen_nt else 0.0
    return {"probed_nt": seen_nt, "lowercase_fraction": round(frac, 4),
            "looks_soft_masked": frac > 0.05}


def _iter4(gen):
    """Normalise the two tuple shapes `iter_fasta_chunks` yields to a common 4-tuple."""
    for item in gen:
        if item[0] == "seq":
            yield item
        else:
            yield ("eor", item[1], item[2], None)


# --------------------------------------------------------------------------------------------
# annotation
# --------------------------------------------------------------------------------------------
def _attr(s, key):
    """`key "value"` out of a GTF attribute column, without a regex."""
    i = s.find(key + ' "')
    if i < 0:
        return None
    i += len(key) + 2
    j = s.find('"', i)
    return s[i:j] if j > 0 else None


def load_annotation(path):
    """Per-sequence gene intervals, exon intervals and true splice sites, from an Ensembl GTF.

    ⭐ WHY ENSEMBL FOR BOTH SIDES. The FASTA and the GTF share a naming convention (`1`, `X`, `MT`,
    `KI270728.1`), so a hit's chromosome is the annotation's chromosome with no mapping table in
    between — and a mapping table is a place where a silent mismatch turns every hit intergenic,
    which is the failure mode that would look most like a clean result. It is also the coordinate
    system the committed pre-mRNA screen already uses, so compartment calls from the two arms are
    comparable rather than merely similar.

    ⚠ A SPLICE SITE IS NOT EVERY EXON BOUNDARY. A transcript's first exon start and last exon end
    are a TSS and a polyA site, not splice sites, and counting them would put a spurious "0 nt from a
    splice site" on every hit in a single-exon gene. Exons are therefore grouped by transcript and
    the two terminal coordinates of each transcript are excluded. This matters for exactly the
    finding §3.8 turns on — a design pairing across the real *NR4A3* intron-2/exon-3 splice site —
    so the field has to mean what it says.
    """
    genes, exons, sites = {}, {}, {}
    tx = {}
    with _open_maybe_gz(path) as fh:
        for line in fh:
            if line[:1] == b"#":
                continue
            f = line.decode("utf-8", "replace").rstrip("\n").split("\t")
            if len(f) < 9:
                continue
            feat = f[2]
            if feat not in ("gene", "exon"):
                continue
            seq, start, end, strand, attrs = f[0], int(f[3]) - 1, int(f[4]) - 1, f[6], f[8]
            if feat == "gene":
                genes.setdefault(seq, []).append(
                    (start, end, strand, _attr(attrs, "gene_id"),
                     _attr(attrs, "gene_name") or _attr(attrs, "gene_id"),
                     _attr(attrs, "gene_biotype")))
            else:
                exons.setdefault(seq, []).append((start, end, strand))
                t = _attr(attrs, "transcript_id")
                if t:
                    rec = tx.get(t)
                    if rec is None:
                        tx[t] = [seq, start, end]
                    else:
                        rec[1] = min(rec[1], start)
                        rec[2] = max(rec[2], end)

    terminal = {}
    for seq, lo, hi in tx.values():
        terminal.setdefault(seq, set()).update((lo, hi))
    for seq, rows in exons.items():
        term = terminal.get(seq, set())
        s = set()
        for a, b, _st in rows:
            if a not in term:
                s.add(a)
            if b not in term:
                s.add(b)
        sites[seq] = sorted(s)
        rows.sort()
    for rows in genes.values():
        rows.sort()
    return {"genes": genes, "exons": exons, "splice_sites": sites,
            "n_genes": sum(len(v) for v in genes.values()),
            "n_exons": sum(len(v) for v in exons.values()),
            "n_splice_sites": sum(len(v) for v in sites.values())}


class Annotator:
    """Resolve `(seq, start, end)` to genes, compartment, strand agreement and splice distance.

    ⚠ THE COMPARTMENT IS COMPUTED AGAINST THE TRANSCRIPTION UNITS THAT COULD ACTUALLY BE ENGAGED,
    AND THE RULE IS STATED RATHER THAN LEFT TO BE INFERRED. A position can sit inside a `+` gene's
    intron and a `-` gene's exon at once. Calling that "exonic" because SOME annotated exon covers
    it would attribute an exonic liability to a design whose hybridisable partner is intronic, which
    is precisely backwards for the question §3.8 asks. So: if any gene runs in the orientation this
    hit would need, the compartment is computed over THOSE genes' exons and `hybridisable` is true;
    if not, it is computed over the overlapping genes on the other strand and `hybridisable` is
    false; if no gene overlaps at all it is `intergenic`.
    """

    def __init__(self, ann):
        self.genes = ann["genes"]
        self.exons = ann["exons"]
        self.sites = ann["splice_sites"]
        self._gstart = {s: [r[0] for r in rows] for s, rows in self.genes.items()}
        self._gmaxend = {}
        for s, rows in self.genes.items():
            run, acc = [], -1
            for r in rows:
                acc = max(acc, r[1])
                run.append(acc)
            self._gmaxend[s] = run
        self._estart = {s: [r[0] for r in rows] for s, rows in self.exons.items()}
        self._emaxend = {}
        for s, rows in self.exons.items():
            run, acc = [], -1
            for r in rows:
                acc = max(acc, r[1])
                run.append(acc)
            self._emaxend[s] = run

    @staticmethod
    def _overlaps(rows, starts, maxend, lo, hi):
        import bisect  # noqa: PLC0415
        j = bisect.bisect_right(starts, hi)
        out = []
        for i in range(j - 1, -1, -1):
            if maxend[i] < lo:
                break
            a, b = rows[i][0], rows[i][1]
            if a <= hi and b >= lo:
                out.append(rows[i])
        return out

    def genes_at(self, seq, lo, hi):
        rows = self.genes.get(seq)
        if not rows:
            return []
        return self._overlaps(rows, self._gstart[seq], self._gmaxend[seq], lo, hi)

    def exon_cover(self, seq, lo, hi, strands=None):
        rows = self.exons.get(seq)
        if not rows:
            return 0
        hits = self._overlaps(rows, self._estart[seq], self._emaxend[seq], lo, hi)
        covered = set()
        for a, b, st in hits:
            if strands is not None and st not in strands:
                continue
            covered.update(range(max(a, lo), min(b, hi) + 1))
        return len(covered)

    def splice_distance(self, seq, lo, hi):
        import bisect  # noqa: PLC0415
        s = self.sites.get(seq)
        if not s:
            return None
        i = bisect.bisect_left(s, lo)
        best = None
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(s):
                p = s[j]
                d = 0 if lo <= p <= hi else (lo - p if p < lo else p - hi)
                best = d if best is None else min(best, d)
        return best

    def annotate(self, seq, lo, hi, required_strand):
        over = self.genes_at(seq, lo, hi)
        matched = [g for g in over if g[2] == required_strand]
        use = matched or over
        hybridisable = bool(matched)
        if not over:
            return {"genes": [], "biotypes": [], "gene_strands": [],
                    "hybridisable": False, "compartment": "intergenic",
                    "nt_to_nearest_splice_site": None}
        cover = self.exon_cover(seq, lo, hi, strands={required_strand} if matched else None)
        span = hi - lo + 1
        compartment = "intronic" if cover == 0 else ("exonic" if cover >= span
                                                     else "intron_exon_spanning")
        return {
            "genes": sorted({g[4] for g in use if g[4]}),
            "biotypes": sorted({g[5] for g in use if g[5]}),
            "gene_strands": sorted({g[2] for g in use}),
            "hybridisable": hybridisable,
            "compartment": compartment,
            "nt_to_nearest_splice_site": self.splice_distance(seq, lo, hi),
        }


# --------------------------------------------------------------------------------------------
# design inputs
# --------------------------------------------------------------------------------------------
def designs_from_atlas(path=ATLAS):
    """`(designs, distinct target windows, atlas)` — the same selection the pre-mRNA arm makes.

    ⚠ THE SCAN IS KEYED ON DISTINCT TARGET WINDOWS, NOT ON DESIGNS, and the artifact reports both.
    190 fusion-specific designs carry 176 distinct windows because several oligonucleotides are
    junction-spanning at more than one partner's seam — one PHYSICAL molecule at several junctions.
    Scanning per design would screen those windows repeatedly and then report the duplicates as
    independent observations, which is exactly the pseudoreplication `offtarget_chance_baseline`
    documents in its `dedupe_sequences`, reappearing one level up.
    """
    atlas = json.load(open(path))
    out, seen = [], set()
    for pan in atlas["panels"]:
        for d in pan.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            key = f"{pan['junction_label']}|{d['antisense_5to3']}"
            if key in seen:
                continue
            seen.add(key)
            out.append({"_key": key, "junction_label": pan["junction_label"],
                        "antisense_5to3": d["antisense_5to3"],
                        "target_mRNA_5to3": d["target_mRNA_5to3"],
                        "gap_specificity_margin": d.get("gap_specificity_margin"),
                        "gc_percent": d.get("gc_percent")})
    windows = sorted({d["target_mRNA_5to3"] for d in out})
    # ⛔ A LENGTH DISAGREEMENT IS A GEOMETRY REFUSAL AND MUST SAY SO, NOT READ AS DIRTY SEQUENCE
    # (2026-08-13). Pointing `ATLAS_JSON` at a 5-8-5 or 5-10-5 atlas raised "target window(s) are not
    # clean 16-mers" and listed three perfectly clean 20-mers — a message that sends the reader
    # hunting for an N or a lower-case base in the atlas, when the real answer is that this screen is
    # a complete 4**16 bitmap and CANNOT run at that length at all (`BITMAP_OLIGO_LEN`). Two
    # different refusals were sharing one sentence, and the wrong one was the louder.
    wrong_length = sorted({len(w) for w in windows} - {OLIGO_LEN})
    if wrong_length:
        raise ValueError(
            f"the atlas {os.path.basename(ATLAS)} carries {wrong_length}-mer target windows and this "
            f"screen is built for {OLIGO_LEN}-mers. This is a GEOMETRY refusal, not malformed "
            f"sequence: the membership test is a complete 2-bit-packed {4 ** BITMAP_OLIGO_LEN:,}-code "
            f"bitmap, so a longer window needs a different data structure rather than a larger "
            f"allocation (see BITMAP_OLIGO_LEN). The exhaustive genome arm is therefore UNAVAILABLE "
            f"at that geometry and its absence must be reported as unmeasured, never as clean.")
    bad = [w for w in windows if set(w) - set(_BASES)]
    if bad:
        raise ValueError(f"{len(bad)} target window(s) carry non-ACGT characters, e.g. {bad[:3]}")
    return out, windows, atlas


def parent_symbols(atlas):
    """The six parent genes, read from the atlas rather than listed here (one fact, one place)."""
    return sorted(atlas["transcripts"].keys())


# --------------------------------------------------------------------------------------------
# checkpointing
# --------------------------------------------------------------------------------------------
def _ckpt_path(ckpt_dir, name):
    safe = "".join(c if (c.isalnum() or c in "._-") else "_" for c in name)
    return os.path.join(ckpt_dir, f"{safe}.json")


def _save_ckpt(ckpt_dir, name, payload):
    """Write one sequence's checkpoint ATOMICALLY, mid-record and at every record end.

    ⛔ CLAUDE.md §6: checkpoint after each unit of work and treat the partial checkpoint as the
    deliverable on a timeout. The unit here is finer than a chromosome, because chromosome 1 alone
    is a twelfth of the genome and losing it to a runner death would mean re-reading it; how much
    finer is set by `CKPT_MIN_INTERVAL_S`, whose comment carries the measurement that chose it.
    Written to a temp file and renamed, so a process killed mid-write leaves the PREVIOUS complete
    checkpoint rather than a truncated JSON that resume would read as authoritative.
    ⚠ In CI these live in `$RUNNER_TEMP` and are uploaded by an `if: always()` step, which is the
    finest granularity Actions offers — this is NOT a continuous upload, and the workflow says so
    rather than claiming one it does not have.
    """
    os.makedirs(ckpt_dir, exist_ok=True)
    p = _ckpt_path(ckpt_dir, name)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    os.replace(tmp, p)


def _load_ckpt(ckpt_dir, name):
    p = _ckpt_path(ckpt_dir, name)
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except ValueError:
        # A corrupt checkpoint is discarded rather than trusted: re-scanning a chromosome costs
        # minutes, and resuming from half a JSON would produce a denominator nobody can defend.
        print(f"  checkpoint for {name} is unreadable — rescanning that sequence", file=sys.stderr)
        return None


# --------------------------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------------------------
def _blank_counts():
    return {"exact": 0, "le1": 0, "le2": 0, "gap_paired_le2": 0,
            "hybridisable_le2": 0, "hybridisable_gap_paired_le2": 0}


def _blank_window_row():
    return {
        "counts": _blank_counts(),
        "by_compartment": {"intronic": 0, "exonic": 0, "intron_exon_spanning": 0, "intergenic": 0},
        "by_softmask": {"none": 0, "partial": 0, "full": 0},
        "n_counted": 0, "n_retained": 0,
        "sites": [], "exact_sites": [], "named_sites": [],
    }


def _softmask_class(frac):
    return "none" if frac == 0 else ("full" if frac >= 1.0 else "partial")


def _merge_window_row(dst, src):
    for k in dst["counts"]:
        dst["counts"][k] += src["counts"][k]
    for k in dst["by_compartment"]:
        dst["by_compartment"][k] += src["by_compartment"][k]
    for k in dst["by_softmask"]:
        dst["by_softmask"][k] += src["by_softmask"][k]
    dst["n_counted"] += src["n_counted"]
    dst["exact_sites"].extend(src["exact_sites"])
    dst["named_sites"].extend(src["named_sites"])
    dst["sites"].extend(src["sites"])


def _trim_sites(row, cap=None):
    """Keep the most decision-relevant `cap` inspectable sites per window; count them all regardless.

    Ranked by mismatch, then gap pairing, then hybridisability, then how repetitive the window is —
    i.e. the order in which a reader would want to see them. Exact and named-target sites are held
    in their own uncapped lists and are never subject to this.
    """
    cap = RETAINED_SITES_PER_WINDOW if cap is None else cap
    row["sites"].sort(key=lambda h: (h["mismatches"], 0 if h["gap_fully_paired"] else 1,
                                     0 if h["hybridisable"] else 1, h["softmask_fraction"],
                                     h["seq"], h["start"]))
    row["sites"] = row["sites"][:cap]
    row["n_retained"] = len(row["sites"])


def scan_genome(fasta, gtf=None, ckpt_dir=None, chunk_nt=None, resume=True,
                atlas_path=ATLAS, progress=True, inputs=None):
    """The whole screen. Returns the reduced record; checkpoints as it goes.

    `inputs` is `(designs, windows, atlas)` and exists so a test can drive the REAL scan over a
    handful of target windows instead of all 176. ⚠ It is a seam for the INPUT, never for the
    mechanism: every test that uses it exercises the same packing, the same bitmap, the same kernel
    and the same annotator the genome run uses. CLAUDE.md §6 — mock the thing under test and you
    test the mock.
    """
    np = _require_numpy()
    chunk_nt = CHUNK_NT if chunk_nt is None else chunk_nt
    ckpt_dir = CKPT_DIR if ckpt_dir is None else ckpt_dir

    designs, windows, atlas = inputs if inputs else designs_from_atlas(atlas_path)
    bitmap, code_index, slots, bstats = build_bitmap(np, windows)
    slot_codes = np.array([s["code"] for s in slots], dtype=np.uint32)
    parents = parent_symbols(atlas)

    # ⛔ NO GTF IS A LOUD STATE, NOT A QUIET ONE. Without an annotation every hit is `intergenic` and
    # `hybridisable: false`, which is the cleanest-looking artifact this module can emit and is a
    # statement about the MISSING ANNOTATION rather than about the genome. That is the exact shape of
    # "an absent reading is not a reading of absence" (CLAUDE.md §4), so it is announced at run time
    # and recorded in the artifact rather than being inferable only from a null field.
    if gtf:
        ann = load_annotation(gtf)
    else:
        print("::warning::no GTF — every hit will be reported as intergenic and NOT hybridisable. "
              "That is a property of the missing annotation, not of the genome, and the artifact "
              "records it as `annotation: NONE`.", file=sys.stderr)
        ann = {"genes": {}, "exons": {}, "splice_sites": {},
               "n_genes": 0, "n_exons": 0, "n_splice_sites": 0}
    annotator = Annotator(ann)
    named = set(parents)
    for rows in ann["genes"].values():
        for g in rows:
            if g[4] and g[4].upper().startswith(NR4A_FAMILY_PREFIX):
                named.add(g[4])

    print(f"targets: {len(windows)} distinct windows over {len(designs)} designs; "
          f"{bstats['n_distinct_codes']:,} distinct codes in a {bstats['bitmap_bytes']:,}-byte "
          f"bitmap built in {bstats['build_seconds']}s", file=sys.stderr)

    per_seq = {}
    #: Every record header the reader announced. ⛔ THE COMPLETENESS GUARD BELOW HAS TO COMPARE
    #: SEEN AGAINST FINISHED, AND ITS FIRST VERSION DID NOT — it looked for an unfinished entry in
    #: `per_seq`, and a record whose end marker never arrives never ENTERS `per_seq`, so it simply
    #: vanished from the denominator with nothing to find. A truncated FASTA is the one input
    #: failure this screen cannot otherwise notice: it produces a smaller `windows_scanned`, every
    #: expectation shrinks with it, and every observed-over-expected ratio stays plausible. Caught
    #: by `test_a_truncated_fasta_refuses_to_reduce_rather_than_reporting_a_whole_denominator`,
    #: which failed against the first implementation — a guard nobody tried to break is a comment.
    seen_records = []
    t0 = time.time()
    last_ckpt = t0
    cur = None

    def _new_seq_state(name):
        return {"name": name, "nt": 0, "softmasked_nt": 0, "windows_total": 0,
                "windows_with_N": 0, "chunks_done": 0, "next_start": 0, "complete": False,
                "rows": {w: _blank_window_row() for w in windows}}

    def _finish(state, total_nt):
        state["nt"] = total_nt
        state["complete"] = True
        for row in state["rows"].values():
            _trim_sites(row)
        _save_ckpt(ckpt_dir, state["name"], state)
        per_seq[state["name"]] = state

    for kind, name, start, payload in _iter4(iter_fasta_chunks(fasta, chunk_nt, OLIGO_LEN)):
        if kind == "eor":
            # `start` carries the record's total length on this tuple shape (see `_iter4`).
            if cur is not None and cur["name"] == name and not cur.get("_skip"):
                _finish(cur, total_nt=start)
            cur = None
            continue
        if cur is None or cur["name"] != name:
            if name not in seen_records:
                seen_records.append(name)
            done = _load_ckpt(ckpt_dir, name) if resume else None
            if done and done.get("complete"):
                per_seq[name] = done
                cur = {"name": name, "_skip": True}
                print(f"  {name}: complete in the checkpoint, skipped", file=sys.stderr)
                continue
            # ⭐ A PARTIAL CHECKPOINT IS RESUMED, NOT DISCARDED. Chromosome 1 is a quarter of the
            # scan; treating "not complete" as "not started" would make a runner death cost the
            # whole chromosome, which is the guess-and-lose shape CLAUDE.md §6 forbids.
            cur = done if (done and done.get("rows")) else _new_seq_state(name)
            if done and done.get("rows"):
                print(f"  {name}: resuming at {cur['next_start']:,} nt "
                      f"({cur['chunks_done']} chunk(s) already done)", file=sys.stderr)
        if cur.get("_skip") or start < cur["next_start"]:
            continue

        cand, ccodes, nwin, nbad, lower_new = scan_chunk(
            np, bitmap, payload, OLIGO_LEN, first_chunk=(start == 0))
        cur["windows_total"] += nwin
        cur["windows_with_N"] += nbad
        cur["softmasked_nt"] += lower_new

        if cand.size:
            arr = np.frombuffer(payload, dtype=np.uint8)
            # ⭐ RESOLVED VECTORISED, ONE CALL FOR THE WHOLE CHUNK. Calling the kernel per candidate
            # builds two numpy scalars per call and dominated the profile; flattening to
            # (candidate, slot) pairs makes it one `bitwise_count` over an array, and it is the
            # SAME kernel `--check` verifies rather than a second implementation for speed.
            pair_code, pair_slot, pair_off = [], [], []
            for off, code in zip(cand.tolist(), ccodes.tolist()):
                for slot in code_index.get(code, ()):
                    pair_code.append(code)
                    pair_slot.append(slot)
                    pair_off.append(off)
            if pair_code:
                pc = np.array(pair_code, dtype=np.uint32)
                ps = slot_codes[np.array(pair_slot, dtype=np.int64)]
                mms = mismatches(np, pc, ps)
                gmms = mismatches(np, pc, ps, GAP_MASK)
                for off, slot, mm, gmm in zip(pair_off, pair_slot,
                                              mms.tolist(), gmms.tolist()):
                    if mm > MAX_MM:
                        # Membership can over-admit and never miss, so this only ever removes.
                        continue
                    s = slots[slot]
                    lo = start + off
                    hi = lo + OLIGO_LEN - 1
                    need = "+" if s["orientation"] == "sense" else "-"
                    a = annotator.annotate(name, lo, hi, need)
                    sm = int(np.count_nonzero(arr[off:off + OLIGO_LEN] >= 0x61)) / OLIGO_LEN
                    hit = {
                        "seq": name, "start": lo, "end": hi,
                        "orientation": s["orientation"],
                        "required_transcript_strand": need,
                        "mismatches": mm, "gap_mismatches": gmm,
                        "gap_fully_paired": gmm == 0,
                        "softmask_fraction": round(sm, 4),
                        **a,
                    }
                    row = cur["rows"][windows[s["window_index"]]]
                    c = row["counts"]
                    c["le2"] += 1
                    if mm == 0:
                        c["exact"] += 1
                    if mm <= 1:
                        c["le1"] += 1
                    if gmm == 0:
                        c["gap_paired_le2"] += 1
                    if a["hybridisable"]:
                        c["hybridisable_le2"] += 1
                        if gmm == 0:
                            c["hybridisable_gap_paired_le2"] += 1
                    row["by_compartment"][a["compartment"]] += 1
                    row["by_softmask"][_softmask_class(sm)] += 1
                    row["n_counted"] += 1
                    if mm == 0:
                        row["exact_sites"].append(hit)
                    if named & set(a["genes"]):
                        row["named_sites"].append(hit)
                    row["sites"].append(hit)

        cur["chunks_done"] += 1
        cur["next_start"] = start + chunk_nt
        # Trim only what has grown past a working buffer: sorting all 176 rows every chunk is pure
        # overhead, and the ranking is total, so trimming later can only keep the same top slice.
        for row in cur["rows"].values():
            if len(row["sites"]) > 4 * RETAINED_SITES_PER_WINDOW:
                _trim_sites(row)
        if time.time() - last_ckpt >= CKPT_MIN_INTERVAL_S:
            for row in cur["rows"].values():
                _trim_sites(row)
            _save_ckpt(ckpt_dir, name, cur)
            last_ckpt = time.time()
        if progress:
            el = time.time() - t0
            done_nt = sum(v["nt"] for v in per_seq.values()) + cur["next_start"]
            print(f"  {name}: {cur['next_start']:,} nt   "
                  f"[{done_nt / 1e6:.0f} Mb, {done_nt / 1e6 / max(el, 1e-9):.2f} Mb/s]",
                  file=sys.stderr)

    # ⛔ NO FINAL SWEEP THAT MARKS EVERYTHING COMPLETE. A record is complete when its `eor` arrived
    # and `_finish` ran; a loop that stamped `complete: True` over whatever survived would turn a
    # truncated FASTA — the one input failure this screen cannot otherwise notice — into a
    # full-looking denominator, which is the "a populated field is not a measured one" failure
    # CLAUDE.md §4 records. An unfinished record simply does not appear in `per_seq`.
    incomplete = [n for n in seen_records
                  if not (per_seq.get(n) or {}).get("complete")]
    if incomplete:
        raise RuntimeError(
            f"{len(incomplete)} record(s) never reached their end marker: {incomplete[:5]}. The "
            f"FASTA is truncated or the reader stopped early; refusing to reduce a denominator "
            f"that would read as whole.")

    return reduce_records(list(per_seq.values()), designs, windows, atlas, ann, bstats,
                          sorted(named), fasta, gtf, chunk_nt, round(time.time() - t0, 1))


# --------------------------------------------------------------------------------------------
# reduce
# --------------------------------------------------------------------------------------------
def reduce_records(states, designs, windows, atlas, ann, bstats, named, fasta, gtf,
                   chunk_nt, seconds):
    """Merge per-sequence checkpoints into the artifact, and grade every count against the null."""
    per_window = {w: _blank_window_row() for w in windows}
    seq_rows = []
    tot_nt = tot_soft = tot_win = tot_badwin = 0
    for st in sorted(states, key=lambda s: s["name"]):
        hits = 0
        for w, row in st["rows"].items():
            _merge_window_row(per_window[w], row)
            hits += row["counts"]["le2"]
        tot_nt += st["nt"]
        tot_soft += st["softmasked_nt"]
        tot_win += st["windows_total"]
        tot_badwin += st["windows_with_N"]
        seq_rows.append({"name": st["name"], "nt": st["nt"],
                         "softmasked_nt": st["softmasked_nt"],
                         "windows_total": st["windows_total"],
                         "windows_with_N": st["windows_with_N"],
                         "windows_scanned": st["windows_total"] - st["windows_with_N"],
                         "n_hits_le2": hits})
    for row in per_window.values():
        _trim_sites(row)

    scanned = tot_win - tot_badwin
    denom = 4 ** OLIGO_LEN
    n2, n1, n0 = n_within(OLIGO_LEN, MAX_MM), n_within(OLIGO_LEN, 1), 1
    ngp = n_gap_paired_within(OLIGO_LEN, GAP_1BASED, MAX_MM)

    def expect(nstrings):
        # Two orientations per position: the plus strand is read once and both the sense and the
        # antisense code of every design are in the bitmap, so each scanned window is two trials.
        return 2.0 * nstrings * scanned / denom

    exp = {"exact": expect(n0), "le1": expect(n1), "le2": expect(n2),
           "gap_paired_le2": expect(ngp)}

    def _sig(v, n=6):
        """Six significant figures, not `round(v, 2)`.

        ⚠ THE OBVIOUS ROUNDING DESTROYS THE STRATUM THIS ARTIFACT LEADS ON. `round(x, 2)` sends any
        expectation below 0.005 to `0.0`, and the exact-match expectation is O(1) genome-wide but
        O(10^-3) on any shard or subset — so a per-chromosome or per-subset artifact would print
        `expected 0.0` beside a real observed count and invite a division by zero or an infinite
        ratio. Significant figures keep the small strata readable and the ratios computable.
        """
        return float(f"{v:.{n}g}")

    parents = parent_symbols(atlas)
    win_designs = {}
    for d in designs:
        win_designs.setdefault(d["target_mRNA_5to3"], []).append(d)

    per_design, exact_sites, named_sites = [], [], []
    for w in windows:
        row = per_window[w]
        c = row["counts"]
        ratios = {k: (_sig(c[k] / exp[k], 4) if exp[k] else None) for k in exp}
        ds = win_designs.get(w, [])
        exact_sites.extend(row["exact_sites"])
        named_sites.extend(row["named_sites"])
        per_design.append({
            "target_mRNA_5to3": w,
            "antisense_5to3": ds[0]["antisense_5to3"] if ds else rc(w),
            "junction_labels": sorted({d["junction_label"] for d in ds}),
            "n_junctions": len({d["junction_label"] for d in ds}),
            "gap_specificity_margin": sorted({d["gap_specificity_margin"] for d in ds
                                              if d["gap_specificity_margin"] is not None}),
            "gc_percent": ds[0]["gc_percent"] if ds else None,
            "counts": c,
            "observed_over_expected": ratios,
            "by_compartment": row["by_compartment"],
            "by_softmask": row["by_softmask"],
            "n_sites_counted": row["n_counted"],
            "n_sites_retained": row["n_retained"],
            "n_exact_sites": len(row["exact_sites"]),
            "n_named_target_sites": len(row["named_sites"]),
            "named_target_genes": sorted({g for h in row["named_sites"] for g in h["genes"]
                                          if g in set(named)}),
            "exact_sites": row["exact_sites"],
            "named_target_sites": row["named_sites"],
            "sites": row["sites"],
        })
    per_design.sort(key=lambda r: (-r["counts"]["exact"],
                                   -(r["observed_over_expected"]["le2"] or 0),
                                   r["target_mRNA_5to3"]))

    ratios = [r["observed_over_expected"]["le2"] for r in per_design
              if r["observed_over_expected"]["le2"] is not None]
    ratios_sorted = sorted(ratios)

    def _median(v):
        if not v:
            return None
        n = len(v)
        return v[n // 2] if n % 2 else round((v[n // 2 - 1] + v[n // 2]) / 2, 3)

    gap_named = [h for h in named_sites if h["gap_fully_paired"] and h["hybridisable"]]
    nr4a3_named = sorted({g for h in gap_named for g in h["genes"]
                          if g.upper().startswith(NR4A_FAMILY_PREFIX)})

    soft_tot = {k: sum(r["by_softmask"][k] for r in per_design) for k in ("none", "partial", "full")}
    soft_all = sum(soft_tot.values())

    return {
        "_title": "Genome-wide off-target screen for junction-spanning gapmers (exhaustive, GRCh38)",
        "_generated_by": "research/modalities/aso_genome_offtarget.py",
        "_what": (
            f"Exhaustive <={MAX_MM}-mismatch screen of every distinct fusion-specific junction "
            f"gapmer target window, and its reverse complement, against every position of the "
            f"reference genome. Every hit is annotated with overlapping gene and biotype, strand "
            f"agreement with the transcription unit, compartment, distance to the nearest true "
            f"splice site, and soft-mask fraction."),
        "_why": (
            "The committed pre-mRNA screen covers six parent transcripts' unspliced sequence, "
            f"which is a small fraction of the genome, and the manuscript's most decision-relevant "
            "off-target finding was in intronic sequence. RNase-H1 is nuclear, so every other "
            "gene's introns were an unmeasured compartment of the same kind. The one prior attempt "
            "at this ran against NCBI core_nt, which has no defined nucleotide span and therefore "
            "no null, at a 50-hit cap below the null's own lower bound."),
        "_what_this_is_not": [
            "NOT a safety assessment, and the raw totals here are NOT a finding. At this threshold "
            "the expected number of genomic near-matches is of order 10^3 per design for ANY 16-mer "
            "whatever, a scrambled control included. Read the stratified headline and the "
            "observed-over-expected ratios; a total is a restatement of 4**16.",
            "NOT a measurement of cleavage. A fully paired catalytic gap is necessary for RNase-H1 "
            "and is not sufficient, and no wet-lab experiment has been performed.",
            "NOT a significance test. The null assumes independent uniform bases; real genomic "
            "sequence is composition-skewed, massively repetitive and full of paralogues, which is "
            "why the soft-mask split is reported beside every ratio rather than as a caveat.",
            "NOT complete for insertions or deletions. The neighbourhood is substitutions only, "
            "which is the same restriction both committed screens carry.",
            "NOT a statement about unannotated transcription. `hybridisable` is measured against an "
            "annotation; a hit in unannotated sequence is reported as intergenic and not "
            "hybridisable, which is a statement about the annotation rather than about the DNA.",
            "NOT a claim about any sequence absent from the reference. A screen against one "
            "assembly says nothing about a patient's private variation.",
        ],
        "_cost": "$0 - one CI runner, CPU only, no GPU and no rental.",
        "method": {
            "algorithm": (
                "2-bit-packed uint32 codes; the complete <=%d-substitution neighbourhood of every "
                "target window AND its reverse complement is set in a 4**%d-bit membership bitmap; "
                "the plus strand is streamed once with one rolling code and one bitmap probe per "
                "position, and every candidate's distance is re-measured exactly." % (MAX_MM,
                                                                                      OLIGO_LEN)),
            "completeness": (
                "definitional: every position is tested against the complete neighbourhood. There "
                "is no seed, no word size and no heuristic, so there is no search sensitivity to "
                "quantify - unlike the manuscript's BLAST arm, whose sensitivity it concedes is "
                "unquantified."),
            "kernel": "bitwise_count(((a^b) | ((a^b)>>1)) & 0x55555555), verified against brute force",
            "gap_mask": hex(GAP_MASK),
            "oligo_len": OLIGO_LEN,
            "wing": WING,
            "gap_region_1based": list(GAP_1BASED),
            "gap_region_source": GAP_SOURCE,
            "max_mismatches": MAX_MM,
            "max_mismatches_source": "junction_aso_offtarget.MAX_MISMATCHES_PER_NEAR_MATCH",
            "restriction_rule": (
                "scanned unrestricted and restricted only at labelling time, so the denominator "
                "stays complete and any future restriction is re-appliable from this artifact "
                "without re-running the scan"),
            "orientation_rule": (
                "a plus-strand match to the target sequence needs a plus-strand transcription unit "
                "to be hybridisable; a match to the reverse complement needs a minus-strand one. "
                "Strand agreement is therefore MEASURED per hit rather than assumed."),
            "compartment_rule": (
                "computed over the exons of the genes running in the orientation the hit would "
                "need; if none, over the overlapping genes on the other strand; if no gene "
                "overlaps, intergenic"),
            "splice_site_rule": (
                "transcript-terminal exon boundaries (TSS, polyA) are excluded, so the distance is "
                "to a real splice site rather than to any exon edge"),
            "chunk_nt": chunk_nt,
            "chunk_overlap_nt": OLIGO_LEN - 1,
            "checkpoint_interval_s": CKPT_MIN_INTERVAL_S,
            "retained_sites_per_window": RETAINED_SITES_PER_WINDOW,
            "retention_rule": (
                "counts are complete and uncapped; exact and named-target sites are retained in "
                "full; other individual site records are capped per window and both n_counted and "
                "n_retained are reported"),
            "blind_to": ["insertions and deletions", "unannotated transcription",
                         "sequence absent from this assembly", "any question about cleavage activity",
                         "chromatin accessibility and nuclear concentration"],
            "wall_seconds": seconds,
        },
        "reference": {
            "fasta": os.path.basename(str(fasta)),
            "gtf": os.path.basename(str(gtf)) if gtf else None,
            "annotation": "Ensembl GTF" if gtf else (
                "NONE — every hit below is reported as intergenic and NOT hybridisable, which is a "
                "property of the missing annotation and NOT of the genome. Compartment, strand "
                "agreement, biotype and splice distance are unmeasured in this artifact."),
            "n_sequences": len(seq_rows),
            "n_genes_annotated": ann["n_genes"],
            "n_exons_annotated": ann["n_exons"],
            "n_splice_sites_annotated": ann["n_splice_sites"],
            "_why_soft_masked": (
                "a dna_sm reference is soft-masked by name, so the repeat annotation arrives "
                "verified rather than assumed, and the repeat split below is free"),
        },
        "bitmap": bstats,
        "denominator": {
            "_why_this_matters": (
                "the manuscript currently carries an ASSUMED 3e8-8e8 nucleotide transcriptome span "
                "because the screens record transcripts scanned rather than nucleotides. This "
                "screen measures its own denominator, so every expectation below is referred to a "
                "number that was counted."),
            "total_nt": tot_nt,
            "softmasked_nt": tot_soft,
            "softmask_fraction": round(tot_soft / tot_nt, 4) if tot_nt else None,
            "windows_total": tot_win,
            "windows_with_N": tot_badwin,
            "windows_scanned": scanned,
            "n_fraction": round(tot_badwin / tot_win, 4) if tot_win else None,
            "per_sequence": seq_rows,
        },
        "null_model": {
            "assumption": "independent, uniformly distributed bases; both orientations per position",
            "n_strings_within_max_mismatches": n2,
            "n_strings_within_1": n1,
            "n_strings_gap_paired_within_max_mismatches": ngp,
            "p_per_position_le_max_mismatches": n2 / denom,
            "expected_per_design": {k: _sig(v) for k, v in exp.items()},
            "_read_this_first": (
                "these expectations are what ANY 16-mer returns against a genome of this measured "
                "size, including a scrambled control. They are the reason a raw count is not a "
                "finding and the reason every count below is reported as a ratio to them."),
        },
        "headline": {
            "_read_this_first": (
                "A raw genome-wide count at this threshold is a restatement of 4**%d, not a "
                "result. offtarget_chance_baseline.py killed exactly that error at transcriptome "
                "scale. The four strata below are what this screen can actually say." % OLIGO_LEN),
            "stratum_1_exact_matches": {
                "_what": ("exact %d/%d matches, where chance expectation is O(1) per design over "
                          "the whole genome and both orientations, so an individual site is "
                          "checkable by hand and an excess is real. This is the class the core_nt "
                          "arm could never reach." % (OLIGO_LEN, OLIGO_LEN)),
                "expected_per_design": _sig(exp["exact"]),
                "n_designs_with_at_least_one": sum(1 for r in per_design if r["counts"]["exact"]),
                "n_target_windows": len(per_design),
                "total_exact_sites": len(exact_sites),
                "max_per_design": max((r["counts"]["exact"] for r in per_design), default=0),
                "sites": exact_sites,
            },
            "stratum_2_observed_over_expected": {
                "_what": ("the grammar section 3.6 and Figure 3 already use. A ratio near 1 means "
                          "no worse than an arbitrary 16-mer of this length, which is the "
                          "defensible statement; a ratio well above 1 is an excess to explain. "
                          "This is what discriminates BETWEEN designs, which a total cannot."),
                "median_ratio_le2": _median(ratios_sorted),
                "min_ratio_le2": ratios_sorted[0] if ratios_sorted else None,
                "max_ratio_le2": ratios_sorted[-1] if ratios_sorted else None,
                "n_at_or_below_1": sum(1 for r in ratios if r <= 1.0),
                "n_above_2": sum(1 for r in ratios if r > 2.0),
                "n_windows": len(ratios),
            },
            "stratum_3_named_targets": {
                "_what": ("a LOOKUP, not a count: does any design have a gap-paired, "
                          "strand-agreeing site in wild-type NR4A3, in any of the six parent "
                          "genes, or in the NR4A paralogues? One named hit outranks the entire "
                          "total, and the total cannot answer it."),
                "parent_genes": parents,
                "nr4a_family_matched_from_annotation": sorted(
                    g for g in named if g.upper().startswith(NR4A_FAMILY_PREFIX)),
                "named_gene_set": sorted(named),
                "n_named_sites_any": len(named_sites),
                "n_named_sites_gap_paired_and_hybridisable": len(gap_named),
                "genes_hit_gap_paired_and_hybridisable": sorted(
                    {g for h in gap_named for g in h["genes"] if g in named}),
                "nr4a_family_genes_hit_gap_paired": nr4a3_named,
                "n_designs_with_a_named_gap_paired_site": len(
                    {r["target_mRNA_5to3"] for r in per_design
                     for h in r["named_target_sites"]
                     if h["gap_fully_paired"] and h["hybridisable"]}),
                "sites": gap_named,
            },
            "stratum_4_repeat_split": {
                "_what": ("free from a soft-masked reference: hits partitioned by the repeat "
                          "annotation the assembly already carries, which converts the null's "
                          "single largest inflation source from a caveat into a measurement."),
                "genome_softmask_fraction": round(tot_soft / tot_nt, 4) if tot_nt else None,
                "hits_by_softmask": soft_tot,
                "fraction_of_hits_fully_softmasked": (round(soft_tot["full"] / soft_all, 4)
                                                      if soft_all else None),
                "_reading": (
                    "if the fully soft-masked share of hits far exceeds the genome's soft-masked "
                    "share, the excess over the uniform null is repeat structure rather than "
                    "anything about these designs"),
            },
        },
        "per_design": per_design,
    }


# --------------------------------------------------------------------------------------------
# self-verification
# --------------------------------------------------------------------------------------------
def self_check(verbose=True):
    """Everything that can be verified without a genome. Writes nothing, ever.

    ⛔ A `--check` THAT WRITES IS NOT A CHECK — `offtarget_chance_baseline.py` records the day its
    missing `--check` fell through to the write path and OVERWROTE the artifact it was asked to
    verify, exiting 0. This one has no write path at all.

    ⚠ AND IT CANNOT BE A STALENESS DIFF, WHICH IS WHAT THE SIBLINGS' `--check` MEANS. This artifact
    is produced by a ~20-minute stream over a 900 MB reference that the dev sandbox cannot reach, so
    "regenerate and compare bytes" is not available offline and pretending otherwise would make the
    gate a no-op. What IS checkable offline is every invariant the scan's correctness rests on, plus
    whether the committed artifact was produced under today's constants — and the second of those is
    the failure that would actually reach print, because a geometry or threshold change silently
    re-bases every count in the file while leaving it looking current.
    """
    np = _require_numpy()
    out = []

    def ok(name, cond, detail=""):
        out.append({"check": name, "pass": bool(cond), "detail": detail})
        if verbose:
            print(f"  [{'ok' if cond else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")

    random.seed(20260813)
    bad = 0
    for _ in range(20000):
        a = "".join(random.choice(_BASES) for _ in range(OLIGO_LEN))
        b = "".join(random.choice(_BASES) for _ in range(OLIGO_LEN))
        if brute_mismatches(a, b) != int(mismatches(np, pack(a), pack(b))):
            bad += 1
    ok("kernel reproduces brute-force Hamming distance over random pairs", bad == 0,
       f"{bad} disagreement(s) over 20,000 pairs")

    import itertools  # noqa: PLC0415
    ref = "GTCCACGGATATGCCC"[:OLIGO_LEN].ljust(OLIGO_LEN, "A")
    bad = n = 0
    for k in range(0, MAX_MM + 2):
        for pos in itertools.combinations(range(OLIGO_LEN), k):
            for subs in itertools.product(_BASES, repeat=k):
                lst = list(ref)
                for p, s in zip(pos, subs):
                    lst[p] = s
                b = "".join(lst)
                n += 1
                if brute_mismatches(ref, b) != int(mismatches(np, pack(ref), pack(b))):
                    bad += 1
    ok(f"kernel is exact over every <= {MAX_MM + 1}-substitution variant", bad == 0,
       f"{n:,} variants, {bad} disagreement(s)")

    lo, hi = GAP_1BASED
    bad = 0
    for _ in range(20000):
        a = "".join(random.choice(_BASES) for _ in range(OLIGO_LEN))
        b = "".join(random.choice(_BASES) for _ in range(OLIGO_LEN))
        if brute_mismatches(a[lo - 1:hi], b[lo - 1:hi]) != int(
                mismatches(np, pack(a), pack(b), GAP_MASK)):
            bad += 1
    ok(f"masked kernel gives the gap sub-distance over 1-based {lo}-{hi}", bad == 0,
       f"{bad} disagreement(s), mask={hex(GAP_MASK)}")

    ok("the gap mask is derived from the geometry, not typed",
       GAP_MASK == gap_mask(OLIGO_LEN, GAP_1BASED) and GAP_1BASED == (WING + 1, OLIGO_LEN - WING),
       f"OLIGO_LEN={OLIGO_LEN} WING={WING} gap={GAP_1BASED} ({GAP_SOURCE})")

    seq = "ACGTACGTACGTACGT"[:OLIGO_LEN]
    nb = neighbourhood(seq)
    ok("the neighbourhood is complete and exact in size",
       len(nb) == n_within(OLIGO_LEN, MAX_MM),
       f"{len(nb)} codes vs {n_within(OLIGO_LEN, MAX_MM)} expected")
    ok("every neighbourhood member really is within the threshold",
       all(brute_mismatches(unpack(c), seq) <= MAX_MM for c in nb))

    ok("pack/unpack round-trips", all(unpack(pack(s)) == s for s in
                                      ("A" * OLIGO_LEN, "T" * OLIGO_LEN, seq, rc(seq))))

    try:
        designs, windows, atlas = designs_from_atlas()
        ok("the atlas still yields clean target windows",
           bool(windows), f"{len(windows)} distinct windows over {len(designs)} designs")
    except Exception as e:  # noqa: BLE001
        ok("the atlas still yields clean target windows", False, f"{type(e).__name__}: {e}")

    if os.path.exists(OUT):
        try:
            art = json.load(open(OUT, encoding="utf-8"))
            m = art.get("method") or {}
            same = (m.get("oligo_len") == OLIGO_LEN and m.get("max_mismatches") == MAX_MM
                    and list(m.get("gap_region_1based") or []) == list(GAP_1BASED))
            ok("the committed artifact was produced under today's geometry and threshold", same,
               f"artifact: len={m.get('oligo_len')} mm={m.get('max_mismatches')} "
               f"gap={m.get('gap_region_1based')}; now: len={OLIGO_LEN} mm={MAX_MM} "
               f"gap={list(GAP_1BASED)}")
            d = art.get("denominator") or {}
            tot = sum(r["windows_scanned"] for r in d.get("per_sequence") or [])
            ok("the artifact's per-sequence denominators sum to its own total",
               tot == d.get("windows_scanned"),
               f"per-sequence {tot} vs recorded {d.get('windows_scanned')}")
        except Exception as e:  # noqa: BLE001
            ok("the committed artifact is readable", False, f"{type(e).__name__}: {e}")
    else:
        out.append({"check": "committed artifact present", "pass": True,
                    "detail": "absent — nothing to grade, the scan has not been run here"})
        if verbose:
            print("  [ok] committed artifact absent — nothing to grade")

    return out


# --------------------------------------------------------------------------------------------
# synthetic genome, so the module is provable with no network
# --------------------------------------------------------------------------------------------
def write_synthetic(dirpath, windows, seed=7, seq_nt=6000, n_seqs=2):
    """A tiny soft-masked genome + GTF with hits planted at KNOWN positions and mismatch counts.

    ⭐ THIS EXISTS BECAUSE `mode=smoke` CANNOT CATCH WHAT MATTERS HERE (CLAUDE.md §6). A run that
    merely completes proves the plumbing; the failure modes that would reach print are a MISSED hit,
    a hit counted twice, a boundary window dropped, a reverse-complement match called hybridisable
    and an N-containing window admitted. Each is planted here at a coordinate a test can assert.
    """
    os.makedirs(dirpath, exist_ok=True)
    rnd = random.Random(seed)
    fa = os.path.join(dirpath, "synthetic.fa")
    gtf = os.path.join(dirpath, "synthetic.gtf")
    w0 = windows[0]
    w1 = windows[1] if len(windows) > 1 else windows[0]
    planted = []
    seqs = {}
    for si in range(n_seqs):
        name = f"S{si + 1}"
        s = [rnd.choice(_BASES) for _ in range(seq_nt)]

        def plant(at, text, note, mm, seqname=name, buf=s):
            for i, ch in enumerate(text):
                buf[at + i] = ch
            planted.append({"seq": seqname, "start": at, "end": at + len(text) - 1,
                            "note": note, "mismatches": mm})

        if si == 0:
            plant(500, w0, "exact sense, intronic", 0)
            plant(1500, rc(w0), "exact antisense, intronic", 0)
            plant(2500, w1, "exact sense, exonic", 0)
            mm1 = list(w0)
            mm1[0] = "A" if mm1[0] != "A" else "C"
            plant(3500, "".join(mm1), "one mismatch in a wing", 1)
            mm2 = list(w0)
            g = GAP_1BASED[0] - 1
            mm2[g] = "A" if mm2[g] != "A" else "C"
            mm2[g + 1] = "T" if mm2[g + 1] != "T" else "G"
            plant(4000, "".join(mm2), "two mismatches, both inside the gap", 2)
            # An N inside an otherwise exact window: it must NOT be found.
            nseq = list(w0)
            nseq[3] = "N"
            plant(4500, "".join(nseq), "exact but for an N — must be excluded", None)
            # Soft-masked copy: found, and flagged as fully repeat-masked.
            plant(5000, w0.lower(), "exact sense, fully soft-masked", 0)
        else:
            plant(700, w0, "exact sense on a second record", 0)
        seqs[name] = "".join(s)

    with open(fa, "w", encoding="ascii") as fh:
        for name, s in seqs.items():
            fh.write(f">{name} dna_sm:synthetic\n")
            for i in range(0, len(s), 60):
                fh.write(s[i:i + 60] + "\n")

    # Two genes on S1: a plus-strand gene with an intron covering the intronic plants, and a
    # minus-strand gene, so strand agreement is exercised in both directions.
    rows = [
        ("S1", "gene", 1, 3000, "+", 'gene_id "G1"; gene_name "PLUSGENE"; gene_biotype "protein_coding";'),
        ("S1", "exon", 1, 200, "+", 'gene_id "G1"; transcript_id "T1"; gene_name "PLUSGENE";'),
        ("S1", "exon", 2400, 3000, "+", 'gene_id "G1"; transcript_id "T1"; gene_name "PLUSGENE";'),
        ("S1", "gene", 3300, 5200, "-", 'gene_id "G2"; gene_name "MINUSGENE"; gene_biotype "lncRNA";'),
        ("S1", "exon", 3300, 3600, "-", 'gene_id "G2"; transcript_id "T2"; gene_name "MINUSGENE";'),
        ("S1", "exon", 4900, 5200, "-", 'gene_id "G2"; transcript_id "T2"; gene_name "MINUSGENE";'),
    ]
    with open(gtf, "w", encoding="ascii") as fh:
        fh.write("#!synthetic\n")
        for seq, feat, a, b, st, attrs in rows:
            fh.write(f"{seq}\tsyn\t{feat}\t{a}\t{b}\t.\t{st}\t.\t{attrs}\n")
    return fa, gtf, planted


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------
ENSEMBL_FASTA_DEFAULT = "Homo_sapiens.GRCh38.dna_sm.primary_assembly.fa.gz"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true",
                   help="verify every offline invariant and the committed artifact's constants; "
                        "writes nothing")
    p.add_argument("--synthetic", action="store_true",
                   help="build a small synthetic genome with planted hits and run end to end")
    p.add_argument("--fasta", help="genome FASTA (.fa or .fa.gz), soft-masked (dna_sm)")
    p.add_argument("--gtf", help="matching Ensembl GTF (.gtf or .gtf.gz)")
    p.add_argument("--out", default=OUT)
    p.add_argument("--ckpt-dir", default=CKPT_DIR)
    p.add_argument("--chunk-nt", type=int, default=CHUNK_NT)
    p.add_argument("--no-resume", action="store_true",
                   help="ignore existing checkpoints and rescan every sequence")
    p.add_argument("--offline", action="store_true",
                   help="refuse to fetch anything; --fasta must already be on disk")
    args = p.parse_args(argv)

    if args.check:
        res = self_check()
        nbad = sum(1 for r in res if not r["pass"])
        print(f"{len(res) - nbad}/{len(res)} checks pass", file=sys.stderr)
        return 1 if nbad else 0

    if args.synthetic:
        import tempfile  # noqa: PLC0415
        _designs, windows, _atlas = designs_from_atlas()
        with tempfile.TemporaryDirectory() as d:
            fa, gtf, planted = write_synthetic(d, windows)
            rec = scan_genome(fa, gtf, ckpt_dir=os.path.join(d, "ckpt"), chunk_nt=1000,
                              resume=False, progress=False)
        rec["_what"] = "SYNTHETIC end-to-end proof of the genome screen. NOT a result about GRCh38."
        rec["_synthetic_planted_sites"] = planted
        print(json.dumps({k: v for k, v in rec.items() if k != "per_design"}, indent=1)[:4000])
        found = rec["headline"]["stratum_1_exact_matches"]["total_exact_sites"]
        print(f"\nsynthetic run: {found} exact site(s) found; "
              f"{rec['denominator']['windows_scanned']} windows scanned", file=sys.stderr)
        return 0

    fasta = args.fasta or os.environ.get("GENOME_FASTA")
    if not fasta:
        print("no --fasta given. This screen needs a soft-masked reference "
              f"({ENSEMBL_FASTA_DEFAULT} from Ensembl) and the matching GTF; the fetch needs "
              "network, so run it in CI (aso-offtarget.yml, screen_mode=genome). "
              "`--synthetic` proves the module end to end with no network, and `--check` verifies "
              "every offline invariant.", file=sys.stderr)
        return 2
    if not os.path.exists(fasta):
        # ⚠ `--offline` IS AN ASSERTION ABOUT THIS MODULE, NOT A MODE OF IT. There is no network code
        # anywhere in this file — no urllib, no requests, no socket — so EVERY path is offline and
        # the flag can only ever restate that. It is accepted because a reader looking for the
        # offline path should find one rather than having to prove a negative, and
        # `test_the_module_contains_no_network_code_at_all` is what actually holds the property.
        print(f"{fasta} is not on disk. This module never fetches anything: it has no network code, "
              f"so the reference is always passed in — the workflow downloads it "
              f"(aso-offtarget.yml, screen_mode=genome). `--synthetic` proves the module end to end "
              f"with no network at all.", file=sys.stderr)
        return 2

    np = _require_numpy()
    sm = check_reference_looks_soft_masked(np, fasta)
    if not sm["looks_soft_masked"]:
        print(f"::warning::the reference does not look soft-masked "
              f"(lowercase fraction {sm['lowercase_fraction']} over {sm['probed_nt']:,} probed nt). "
              f"The repeat split is derived from letter case, so on an unmasked or hard-masked "
              f"reference it would report every hit as non-repetitive. Use "
              f"{ENSEMBL_FASTA_DEFAULT}.", file=sys.stderr)

    rec = scan_genome(fasta, args.gtf, ckpt_dir=args.ckpt_dir, chunk_nt=args.chunk_nt,
                      resume=not args.no_resume)
    rec["reference"]["soft_mask_probe"] = sm
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
        fh.write("\n")
    h = rec["headline"]
    print(f"\nwrote {args.out}")
    print(f"  {rec['denominator']['windows_scanned']:,} windows scanned over "
          f"{rec['denominator']['total_nt']:,} nt "
          f"({rec['denominator']['softmask_fraction']} soft-masked)")
    print(f"  exact {OLIGO_LEN}/{OLIGO_LEN} sites: "
          f"{h['stratum_1_exact_matches']['total_exact_sites']} over "
          f"{h['stratum_1_exact_matches']['n_designs_with_at_least_one']} window(s), against "
          f"{h['stratum_1_exact_matches']['expected_per_design']} expected per design")
    print(f"  observed/expected at <= {MAX_MM} mm: median "
          f"{h['stratum_2_observed_over_expected']['median_ratio_le2']}, "
          f"max {h['stratum_2_observed_over_expected']['max_ratio_le2']}")
    print(f"  named-target gap-paired hybridisable sites: "
          f"{h['stratum_3_named_targets']['n_named_sites_gap_paired_and_hybridisable']} in "
          f"{h['stratum_3_named_targets']['genes_hit_gap_paired_and_hybridisable']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
