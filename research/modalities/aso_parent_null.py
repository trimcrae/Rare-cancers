#!/usr/bin/env python3
"""What gap-pairing rate would ARBITRARY 16-mers show against the same six parent transcripts?

⛔ WHY THIS EXISTS. `aso_parent_gap_pairing.py` (the manuscript's screen 4) reports that 87 of 190
junction designs let a mature wild-type parent pair the whole catalytic gap at >= 10 contiguous base
pairs, 61 of them against wild-type NR4A3. That count had **no null**. The genome scan (screen 5)
has one — it states a chance expectation per 16-mer and reads its observations against it — and
screen 4 did not, so 87/190 was a number with nothing to be large or small relative to. An
external reviewer put it as the cheapest addition that would materially strengthen the paper, and
they were right: the whole instrument is a lookup over 20,011 nucleotides of parent transcript, so
the null costs one CPU-minute and nothing else.

⚠ AND THE ANSWER IS NOT OBVIOUS IN EITHER DIRECTION, WHICH IS WHY IT HAD TO BE MEASURED. Two
readings were defensible before the run:
  · "87/190 is trivially high, because a junction design's acceptor half IS wild-type NR4A3
    sequence, so of course NR4A3 pairs it" — which would make the count a restatement of the design
    rule rather than a finding; or
  · "10 contiguous base pairs is 4^-10, so nothing arbitrary ever reaches it" — which would make
    87/190 enormous.
Neither survives contact with the arithmetic. A run of >= 10 that CONTAINS the six gap positions can
sit at five offsets inside a 16-mer window, so an arbitrary 16-mer meets one at roughly
5 x 4^-10 x 20,011 ~ 0.10 expected sites, i.e. of order one in ten arbitrary 16-mers is "liable"
by chance alone. That is small against 87/190 and it is emphatically not zero, and no reader could
have derived which without being told the span.

WHAT THIS MEASURES. Six null ensembles, every one of them pushed through the SAME instrument as the
real designs — `aso_parent_gap_pairing.longest_run_through_gap`, the same six mature parents spliced
from the same committed record, forward orientation only, the same `MIN_DUPLEX_BP`. Only the query
changes; nothing about the screen does.

  scrambled_mononucleotide   each design's target window shuffled, base composition preserved. This
                             is the reviewer's "scrambled" null. ⛔ IT IS *NOT* THE CONTROL THE
                             MANUSCRIPT ASKS FOR — that pointer used to sit here, naming a section
                             5.4 that does not exist, and it sent both papers' §4.4/§5 prescription
                             to the wrong arm's rate for two rounds (round 8, seats J/C/D/B).
  scrambled_dinucleotide     ⭐ THE CONTROL THE MANUSCRIPT ASKS A LABORATORY TO MAKE (§4.4 of the
                             extended report, §5 of the journal article). Shuffled preserving
                             DINUCLEOTIDE composition (Altschul-Erikson
                             Eulerian-path shuffle), which is the stricter sequence null: it holds
                             local base-stacking structure fixed and lets only the arrangement move.
  random_uniform             16-mers drawn i.i.d. from equal base frequencies — the "randomly-chosen
                             16-mer" reading, and the ensemble the analytic expectation describes.
  random_composition_matched 16-mers drawn i.i.d. from the pooled base composition of the 190 real
                             target windows, which are GC-richer than uniform.

⭐ AND THREE THAT ARE NOT NULLS BUT A DECOMPOSITION, because "is 87 more than chance" is a weaker
question than "WHERE does 87 come from", and the second is answerable on the same instrument:

  wings_scrambled_gap_held   the six catalytic-gap bases are held EXACTLY where they are and the
                             ten wing bases are shuffled. Screen 4 admits a window only if all six
                             gap positions pair, so this arm asks how much of the liability is the
                             gap 6-mer finding a parent at all, as against the flanking run that
                             carries it to ten base pairs.
  gap_scrambled_wings_held   the mirror, and the discriminating one: real wings, scrambled gap.
  random_parent_chimera      ⭐ THE STRONGEST FORM OF THE ANCHOR. A 16-mer built by joining a random
                             window of a real donor parent to a random window of real NR4A3, split
                             at the same offset as the design it is matched to — a fake junction
                             between two real transcripts. It reproduces the design rule's whole
                             structure (donor sequence 5', NR4A3 sequence 3', junction inside the
                             gap) while destroying the one thing that makes a design a design: that
                             the two pieces meet at a REPORTED breakpoint. If the observed rate is
                             merely what any parent-to-parent chimera gives, this arm returns it,
                             and screen 4's headline is a restatement of the design rule rather
                             than a finding about EMC breakpoints.

⚠ A DECOMPOSITION THAT COULD NOT DISCRIMINATE WAS RUN FIRST AND IS RECORDED SO IT IS NOT RETRIED.
The first version of this module scrambled the DONOR half and the ACCEPTOR half of each window,
predicting that holding the real NR4A3 half would keep the rate near the observed one. Both arms
collapsed to ~8%, and the prediction was not merely wrong but unanswerable by that experiment: at a
16-mer 5-6-5 the gap spans positions 5 to 10 and the junction sits at position 6, 8 or 10, so BOTH
halves contribute bases to the gap and scrambling EITHER destroys the gap 6-mer outright. The arms
were measuring the same thing twice and neither was measuring the intended quantity. The wing/gap
split above is the version of that question the instrument can actually answer.

⛔ WHAT THIS IS NOT.
  · Not a significance test. Every rate below is a proportion with a Wilson interval; no p-value is
    computed and none should be read in, because the 190 design records are not independent draws —
    they are 176 distinct molecules tiled at overlapping registers across 38 junctions, so any test
    treating them as 190 independent trials would be wrong about its own denominator. The
    per-design paired rate below is the honest version of the comparison and is reported instead.
  · Not a measurement of off-target activity. A duplex is necessary for RNase-H1 cleavage and is not
    sufficient. Nothing here is a cleavage assay, and a scrambled oligonucleotide that clears this
    screen is not thereby safe.
  · Not transcriptome-wide. Six parent transcripts, the same bound screen 4 itself carries.
  · Not a statement about the OTHER screens. The alignment screen, the exhaustive transcript scan
    and the genome scan have their own nulls or their own bounds; this one is screen 4's.

DETERMINISM. The pseudo-random stream is a splitmix64 written out in this file rather than
`random.Random`, so the committed artifact is bit-stable against any interpreter that can run the
module at all. `random.seed` is reproducible in practice and its guarantee is a CPython
implementation detail; an artifact that CI re-checks with `--check` should not rest on one.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aso_parent_gap_pairing as pgp  # noqa: E402  — the instrument, imported not re-implemented
# ⚠ Imported for its PUBLISHED_BREAKPOINTS map ONLY, so the ladder can report the subset a
# laboratory would actually be choosing at: the panel's junctions that any patient is reported to
# carry. Reading it from the canonical CSV instead would point this instrument at a file it is
# upstream of.
import aso_per_junction_table as pjt  # noqa: E402

OUT = os.path.join(HERE, f"aso-parent-null{os.environ.get('OUT_SUFFIX', '')}.json")

#: Draws per design per ensemble. 200 x 190 = 38,000 queries per ensemble; the whole run is under a
#: minute because the gap lookup is an index rather than a scan (see `_gap_index`).
N_DRAWS = int(os.environ.get("NULL_DRAWS") or 200)

#: ⚠ ONE SEED, RECORDED IN THE ARTIFACT. Changing it changes every number below, so it is a
#: configuration value in the sense CLAUDE.md gives that word, not a tuning knob.
SEED = int(os.environ.get("NULL_SEED") or 20260815)

#: ⛔ THE SECOND CUT, MEASURED RATHER THAN LEFT AS "THE MORE INCLUSIVE READING". The manuscript
#: reports the mature-parent screen at 10 contiguous base pairs and discloses that at 7 — the loose
#: end of the same cited range — the same screen returns 175 of 190 rather than 87. That disclosure
#: was written as though the looser reading were simply a larger liability, and it is not: every
#: null in this file was computed at 10, so the 7-base-pair count had no anchor at all, in a module
#: whose entire reason for existing is that a count without a null cannot be large or small.
#: Measuring it settles the question in the direction the disclosure did not anticipate — at 7 the
#: exon-terminus chimera null is 91.4% against 92.1% observed, so the loose reading is at chance and
#: is not a larger finding. Both cuts are therefore carried through every ensemble, in one pass, and
#: the manuscript states both.
SECONDARY_CUT_BP = int(os.environ.get("NULL_SECONDARY_CUT") or 7)

#: ⭐⭐ THE WHOLE CUT LADDER, BECAUSE TWO CUTS IS STILL A CHOICE OF TWO CUTS. Reporting 10 and 7
#: answers "what happens at the other end of the cited range" and leaves the question a reader
#: actually asks — *is 87 of 190 a finding, or an artefact of where the cut was put?* — resting on
#: two points of a curve nobody printed. Two independent reviewers on 2026-08-19, an RNase-H1
#: enzymologist and a hostile competitor read, converged on the same remedy from opposite
#: directions: print the sensitivity of observed AND of every null across the whole reachable range
#: and let the separation be read off it.
#:
#: ⛔ 6 IS THE MECHANISTIC FLOOR AND IS WHY THE LADDER STARTS THERE. A run counted by this
#: instrument spans the design's whole catalytic gap, so the shortest possible counted run is the
#: gap itself — six base pairs at 5-6-5, of which six are the RNA:DNA hybrid RNase-H1 acts on. A cut
#: of 6 is therefore "a wild-type parent pairs the whole gap, at any flanking length", which is the
#: criterion with an enzymological referent; 10 adds four LNA:RNA wing pairs that add occupancy and
#: no catalytic content. 13 is the ceiling: no counted run in any arm exceeds it.
#:
#: ⚠ IT COSTS NOTHING. The runs are already measured; every cut is a threshold on a histogram of
#: them, so the ladder is a cumulative sum over counts this module already had and throws away.
CUT_LADDER = tuple(int(x) for x in (os.environ.get("NULL_CUT_LADDER")
                                    or "6,7,8,9,10,11,12,13").split(","))

BASES = "ACGT"


# ─────────────────────────────────────────────────────────────────────────── deterministic stream
class Rng:
    """splitmix64. Written out so the artifact does not depend on CPython's PRNG staying put."""

    __slots__ = ("s",)

    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFFFFFFFFFF

    def next_u64(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def below(self, n):
        """Uniform on [0, n) by rejection, so no modulo bias enters a count reported as a rate."""
        if n <= 1:
            return 0
        limit = (1 << 64) - ((1 << 64) % n)
        while True:
            v = self.next_u64()
            if v < limit:
                return v % n

    def shuffled(self, items):
        a = list(items)
        for i in range(len(a) - 1, 0, -1):
            j = self.below(i + 1)
            a[i], a[j] = a[j], a[i]
        return a

    def choice_weighted(self, keys, cum, total):
        v = self.below(total)
        for k, c in zip(keys, cum):
            if v < c:
                return k
        return keys[-1]


# ───────────────────────────────────────────────────────────────────────────── the null ensembles
def scramble_mono(seq, rng):
    return "".join(rng.shuffled(seq))


def scramble_dinucleotide(seq, rng, tries=64):
    """Altschul-Erikson Eulerian-path shuffle: same first base, last base and dinucleotide counts.

    The sequence is an Eulerian path through a graph whose vertices are the four bases and whose
    edges are its dinucleotides. Any other Eulerian path over the same edge multiset is a shuffle
    with identical dinucleotide composition. The construction is the standard one: choose, for each
    vertex other than the terminal one, a random outgoing edge to place LAST; retry until those
    last-edges form a tree rooted at the terminal vertex (otherwise the walk strands itself); then
    permute each vertex's remaining edges freely.

    Returns `(shuffled, fell_back)`. ⚠ It falls back to the mononucleotide shuffle if the tree
    condition is not met within `tries`. With a four-letter alphabet that is vanishingly rare, and
    the artifact RECORDS how often it happened rather than letting a silent fallback quietly change
    what the ensemble means — a dinucleotide null that is secretly part mononucleotide would be
    reported as the stricter test while being the looser one.
    """
    n = len(seq)
    if n < 3:
        return seq, False
    last = seq[-1]
    edges = {}
    for a, b in zip(seq, seq[1:]):
        edges.setdefault(a, []).append(b)
    verts = list(edges)
    for _ in range(tries):
        chosen = {}
        for v in verts:
            if v == last:
                continue
            chosen[v] = edges[v][rng.below(len(edges[v]))]
        # every non-terminal vertex must reach `last` by following its chosen last-edge
        ok = True
        for v in chosen:
            seen, cur = set(), v
            while cur != last:
                if cur in seen or cur not in chosen:
                    ok = False
                    break
                seen.add(cur)
                cur = chosen[cur]
            if not ok:
                break
        if not ok:
            continue
        order = {}
        for v in verts:
            rest = list(edges[v])
            if v in chosen:
                rest.remove(chosen[v])
                order[v] = rng.shuffled(rest) + [chosen[v]]
            else:
                order[v] = rng.shuffled(rest)
        out, cur, idx = [seq[0]], seq[0], {v: 0 for v in verts}
        for _ in range(n - 1):
            nxt = order[cur][idx[cur]]
            idx[cur] += 1
            out.append(nxt)
            cur = nxt
        return "".join(out), False
    return scramble_mono(seq, rng), True


def scramble_positions(seq, positions, rng):
    """Shuffle only the listed positions among themselves; every other base stays put."""
    pool = rng.shuffled([seq[p] for p in positions])
    out = list(seq)
    for p, ch in zip(positions, pool):  # noqa: B905 — equal length by construction
        out[p] = ch
    return "".join(out)


def draw_uniform(rng, k):
    return "".join(BASES[rng.below(4)] for _ in range(k))


def draw_composition(rng, k, keys, cum, total):
    return "".join(rng.choice_weighted(keys, cum, total) for _ in range(k))


def draw_parent_chimera(rng, parents, donor, offset):
    """A fake junction: `offset` bases from a random donor window, the rest from a random NR4A3 one.

    ⛔ THE POINT IS WHAT IT KEEPS, NOT WHAT IT RANDOMISES. It keeps the donor gene, the acceptor
    gene, the 5'-donor/3'-NR4A3 order and the split offset — the entire design rule — and randomises
    only WHERE in each transcript the two pieces are taken from. So it answers the question a
    reviewer actually asks of screen 4: is 87 of 190 a fact about reported EMC breakpoints, or is it
    what any chimera of these two transcripts would give?
    """
    ds, ns = parents[donor], parents["NR4A3"]
    tail = pgp.OLIGO_LEN - offset
    left = right = ""
    if offset:
        p = rng.below(len(ds) - offset + 1)
        left = ds[p:p + offset]
    if tail:
        p = rng.below(len(ns) - tail + 1)
        right = ns[p:p + tail]
    return left + right


# ─────────────────────────────────────────── exon termini: what the interior-window chimera destroys
def mature_exon_boundaries():
    """gene -> (internal exon 3' termini, internal exon 5' termini), in MATURE coordinates.

    ⛔ WHY THIS EXISTS, AND IT IS THE ROUND-7 FINDING B5-F1. `draw_parent_chimera` above takes the
    donor half at a UNIFORM INTERIOR OFFSET (`p = rng.below(len(ds) - offset + 1)`). A real design's
    donor half does not sit at an arbitrary interior position: it ENDS at an exon 3' terminus,
    because that is what a splice donor is. So the interior-window chimera destroys 5'-splice-donor
    consensus at the same time as it destroys the breakpoint, and the excess of the observed rate
    over that arm cannot be read as "specific to where the disease joins them" — some unmeasured part
    of it is a property of exon termini that every exon-exon junction in the genome shares.

    ⚠ MEASURED, NOT ASSERTED, and the measurement is what the two arms below exist to take.

    Boundaries are derived from the SAME committed record the mature transcripts are spliced from
    (`exon_spans_0based_inclusive` in aso-premrna-sequences.json), by cumulative exon length, so a
    terminus here is the same nucleotide the splice uses and nothing is re-derived from coordinates
    this module owns.

    ⛔ THE FIRST AND LAST BOUNDARIES ARE EXCLUDED ON PURPOSE. The final exon's 3' end is the
    transcript's 3' end, not a splice donor, and the first exon's 5' end is the transcript's 5' end,
    not a splice acceptor. Including them would put transcript ends into an ensemble whose whole
    subject is splice junctions.
    """
    genes = json.load(open(pgp.SEQS, encoding="utf-8"))["genes"]
    out = {}
    for g, v in genes.items():
        ends, acc = [], 0
        for a, b in v["exon_spans_0based_inclusive"]:
            acc += b - a + 1
            ends.append(acc)
        # ends[:-1] are internal 3' termini; the same cut points are the internal 5' termini.
        out[g] = (ends[:-1], ends[:-1])
    return out


def draw_donor_terminus_chimera(rng, parents, donor, donor_len, bounds):
    """Chimera whose donor half ENDS AT A REAL EXON 3' TERMINUS; NR4A3 half uniform interior.

    This is `draw_parent_chimera` with exactly one thing changed — the donor window is no longer
    drawn uniformly over the interior, it is drawn over the real splice donors. Everything else is
    held: the donor gene, the acceptor gene, the 5'-donor/3'-NR4A3 order, the split.
    """
    ds, ns = parents[donor], parents["NR4A3"]
    tail = pgp.OLIGO_LEN - donor_len
    left = right = ""
    if donor_len:
        ends = [e for e in bounds[donor][0] if e >= donor_len]
        e = ends[rng.below(len(ends))]
        left = ds[e - donor_len:e]
    if tail:
        p = rng.below(len(ns) - tail + 1)
        right = ns[p:p + tail]
    return left + right


#: The mature-coordinate 5' terminus of NR4A3 exon 3 — the acceptor EVERY ONE of the 38 reported
#: in-frame junctions uses. `exon_terminus_chimera_novel_acceptor` excludes it, so that arm cannot
#: draw the disease's own acceptor even by accident. ⚠ DERIVED, NOT TYPED: asserted against the
#: designs themselves in test_aso_parent_null.py rather than trusted as a constant here.
NR4A3_EXON3_START = 697


def draw_exon_terminus_chimera(rng, parents, donor, donor_len, bounds, exclude_real_acceptor=False):
    """⭐ THE STRICTEST NULL: a chimera between two REAL exon termini of the two real parents.

    Donor half ends at a real donor exon 3' terminus; NR4A3 half begins at a real NR4A3 exon 5'
    terminus. It is a syntactically valid exon-exon junction between the same two genes that is
    NOT a reported EMC breakpoint. If the observed rate is what THIS arm gives, then screen 4's
    excess is a property of joining two exon termini and not of where the disease joins them.
    """
    ds, ns = parents[donor], parents["NR4A3"]
    tail = pgp.OLIGO_LEN - donor_len
    left = right = ""
    if donor_len:
        ends = [e for e in bounds[donor][0] if e >= donor_len]
        e = ends[rng.below(len(ends))]
        left = ds[e - donor_len:e]
    if tail:
        starts = [s for s in bounds["NR4A3"][1]
                  if s + tail <= len(ns)
                  and not (exclude_real_acceptor and s == NR4A3_EXON3_START)]
        s = starts[rng.below(len(starts))]
        right = ns[s:s + tail]
    return left + right


# ───────────────────────────────────────────────────────────────────── the instrument, made fast
def _gap_index(parents):
    """gap 6-mer -> [(gene, window_start)], so a query touches ~5 candidates instead of 20,011.

    ⛔ THIS IS AN INDEX OVER THE SAME COMPARISON, NOT A DIFFERENT ONE. A window can only pair the
    whole gap if the parent carries that exact gap 6-mer at the matching offset, so keying on it
    loses no hit; `_best_run` then calls screen 4's own `longest_run_through_gap` on the survivors.
    `test_aso_parent_null.py` asserts the indexed path and the brute-force path agree design for
    design over the real 190, because an index that silently drops hits would make every null rate
    below too low, which is the direction that flatters the paper.
    """
    idx = {}
    g0, g1 = pgp.GAP.start, pgp.GAP.stop
    for gene, seq in parents.items():
        for i in range(len(seq) - pgp.OLIGO_LEN + 1):
            idx.setdefault(seq[i + g0:i + g1], []).append((gene, i))
    return idx


def _best_run(target, parents, idx):
    """(longest run through the gap, gene) — the screen-4 quantity, via the index."""
    best = (0, None)
    for gene, i in idx.get(target[pgp.GAP.start:pgp.GAP.stop], ()):  # noqa: B905
        seq = parents[gene]
        run = pgp.longest_run_through_gap(seq[i:i + pgp.OLIGO_LEN], target)
        if run > best[0]:
            best = (run, gene)
    return best


# ─────────────────────────────────────────────────────────────────────────────────────── stats
def analytic_p_site(gap_nt):
    """(P all gap positions pair, P the run then reaches MIN_DUPLEX_BP | gap paired), exactly.

    ⛔ THE OBVIOUS FORMULA IS WRONG AND WAS WRITTEN FIRST, so it is spelled out here rather than
    left as a one-liner. Counting the placements of a 10-wide run inside a 16-mer gives
    `OLIGO_LEN - MIN_DUPLEX_BP + 1` = 7, but screen 4 does not admit any 10-run: it admits one that
    CONTAINS all six gap positions, which is 5 of those 7. Summing 4^-10 over placements then
    overcounts again, because adjacent placements share nine positions and are nowhere near
    independent. Both errors inflate the null, i.e. both make the observed excess look smaller than
    it is — the direction that would have flattered a reviewer's objection rather than answering it.

    The exact statement instead: the gap must pair (4^-gap_nt), and the perfect run then extends L
    positions left and R right, each geometric with success 1/4 and truncated by the wing length.
    The site counts when gap_nt + L + R >= MIN_DUPLEX_BP.
    """
    left_max, right_max = pgp.GAP.start, pgp.OLIGO_LEN - pgp.GAP.stop

    def tail(n_max):
        d = [0.75 * 0.25 ** k for k in range(n_max)]
        d.append(0.25 ** n_max)          # ran out of wing: no mismatch can stop it
        return d

    dl, dr = tail(left_max), tail(right_max)
    need = pgp.MIN_DUPLEX_BP - gap_nt
    p_extend = sum(pl * pr
                   for l, pl in enumerate(dl)
                   for r, pr in enumerate(dr)
                   if l + r >= need)
    return 0.25 ** gap_nt, p_extend


def wilson(k, n, z=1.96):
    """Wilson 95% interval — the repository's fixed convention for a proportion."""
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(max(0.0, c - h), 5), round(min(1.0, c + h), 5)]


def _ladder(runs, runs_nr4a3, runs_nr4a3_specific=None):
    """Liability counts at every cut of `CUT_LADDER`, from the runs already measured.

    ⭐ THE POINT OF THE LADDER IS THAT ONE CUT IS NOT A RESULT. The manuscript's central negative
    is a count at a threshold this work ADOPTS rather than measures, so a reader cannot tell from
    the count alone whether it is a property of the designs or a property of the cut. The answer is
    the whole curve: at 6 — the design's own catalytic gap, the only cut with an enzymological
    referent — observed and every null are within a few points of each other; the separation opens
    as the cut rises and is widest at the strict end. That is a statement about the criterion, and
    it can only be made by printing the criterion's whole range.

    Costs nothing: `runs` was already measured for every draw and thrown away after two thresholds.
    """
    n = len(runs)
    out = {}
    for cut in CUT_LADDER:
        k = sum(1 for r in runs if r >= cut)
        kn = sum(1 for r in runs_nr4a3 if r >= cut)
        row = {
            "n_liable": k,
            "rate_liable": round(k / n, 5) if n else None,
            "rate_liable_wilson95": wilson(k, n),
            # ⛔ ATTRIBUTED, NOT PER-GENE, AND THE TWO DIVERGE BADLY AS THE CUT LOOSENS. This counts
            # designs whose LONGEST run over all six parents happens to fall in NR4A3 — an argmax —
            # which is exactly what the manuscript's "61 of those 87 are against wild-type NR4A3"
            # means, and at the ten-base-pair cut the two readings differ by one design (61 against
            # 62), which §2.5 already discloses. At six they differ by eighty-one (77 against 158),
            # because a design whose longest run is against some other parent can still pair NR4A3
            # through its whole gap. A field named "against_NR4A3" reads as the second and is the
            # first, so both are emitted and neither is left to be inferred.
            "n_liable_attributed_to_NR4A3": kn,
            "rate_liable_attributed_to_NR4A3": round(kn / n, 5) if n else None,
        }
        if runs_nr4a3_specific is not None:
            ks = sum(1 for r in runs_nr4a3_specific if r >= cut)
            row["n_pairing_NR4A3_specifically"] = ks
            row["rate_pairing_NR4A3_specifically"] = round(ks / n, 5) if n else None
        out[str(cut)] = row
    return out


def _summary(hits, nr4a3, runs, n):
    return {
        "n_draws": n,
        "n_liable": hits,
        "rate_liable": round(hits / n, 5) if n else None,
        "rate_liable_wilson95": wilson(hits, n),
        "n_liable_against_NR4A3": nr4a3,
        "rate_liable_against_NR4A3": round(nr4a3 / n, 5) if n else None,
        "rate_liable_against_NR4A3_wilson95": wilson(nr4a3, n),
        "mean_longest_run_bp": round(sum(runs) / n, 4) if n else None,
        "max_longest_run_bp": max(runs) if runs else 0,
        "n_pairing_the_gap_at_any_length": sum(1 for r in runs if r > 0),
    }


def build():
    parents = pgp.mature_parents()
    idx = _gap_index(parents)
    atlas = json.load(open(pgp.ATLAS, encoding="utf-8"))

    designs = []
    for panel in atlas["panels"]:
        for d in panel.get("designs") or []:
            if d.get("fusion_specific"):
                # ⚠ `junction_offset_in_oligo` IS AN OFFSET IN THE ANTISENSE OLIGO, NOT A DONOR
                # BASE COUNT, and the two differ for 152 of the 190 designs. The oligo is the
                # reverse complement of the target, so the NR4A3 half comes FIRST in it: the field
                # equals `bases_from_NR4A3` for all 190 records, which is asserted below rather
                # than described. The donor half of the TARGET is therefore the complement,
                # `OLIGO_LEN - junction_offset_in_oligo`.
                # ⛔ `draw_parent_chimera` above is called with the offset and takes that many
                # bases from the DONOR, i.e. it builds each design's MIRROR split. Its ensemble
                # totals are unaffected — every junction's five designs tile offsets 6..10, which
                # is symmetric about 8, so the multiset of donor lengths drawn per junction is
                # identical either way (asserted in test_aso_parent_null.py) — but the two arms
                # below take the split they mean, because a per-design terminus draw is not
                # symmetric and the mirror would silently pair the wrong window length.
                donor_len = pgp.OLIGO_LEN - d["junction_offset_in_oligo"]
                if "bases_from_NR4A3" in d:
                    assert d["junction_offset_in_oligo"] == d["bases_from_NR4A3"], panel["junction_label"]
                designs.append({
                    "junction": panel["junction_label"],
                    "donor": panel["donor_symbol"],
                    "antisense_5to3": d["antisense_5to3"],
                    "target": d["target_mRNA_5to3"],
                    "junction_offset": d["junction_offset_in_oligo"],
                    "donor_len": donor_len,
                    "margin": d["gap_specificity_margin"],
                })

    # the observed arm, re-measured here through the index so the comparison is instrument-identical
    obs_hits = obs_nr4a3 = 0
    obs_hits_2 = obs_nr4a3_2 = 0
    obs_runs = []
    obs_runs_nr4a3 = []
    obs_runs_nr4a3_specific = []
    runs_by_junction = {}
    # ⚠ The same instrument restricted to ONE parent, so "does NR4A3 pair this design's whole gap"
    # is answered directly rather than inferred from which gene won an argmax over all six.
    nr4a3_only = {"NR4A3": parents["NR4A3"]}
    idx_nr4a3 = _gap_index(nr4a3_only)
    for d in designs:
        run, gene = _best_run(d["target"], parents, idx)
        obs_runs.append(run)
        obs_runs_nr4a3.append(run if gene == "NR4A3" else 0)
        obs_runs_nr4a3_specific.append(_best_run(d["target"], nr4a3_only, idx_nr4a3)[0])
        runs_by_junction.setdefault(d["junction"], []).append(run)
        if run >= pgp.MIN_DUPLEX_BP:
            obs_hits += 1
            obs_nr4a3 += 1 if gene == "NR4A3" else 0
        if run >= SECONDARY_CUT_BP:
            obs_hits_2 += 1
            obs_nr4a3_2 += 1 if gene == "NR4A3" else 0
    n_obs = len(designs)

    # ⛔ The panel junctions any patient is reported to carry, from the curation map rather than
    # from a list typed here. `runs_by_junction` keys are panel junction labels; the map also
    # carries non-panel seams, so the intersection is taken rather than the map's own keys.
    _pub_panel = set(pjt.PUBLISHED_BREAKPOINTS) & set(runs_by_junction)
    _pub_runs = [r for d, r in zip(designs, obs_runs) if d["junction"] in _pub_panel]
    _pub_runs_nr4a3 = [r for d, r in zip(designs, obs_runs_nr4a3)
                       if d["junction"] in _pub_panel]
    _pub_runs_nr4a3_specific = [r for d, r in zip(designs, obs_runs_nr4a3_specific)
                                if d["junction"] in _pub_panel]

    # pooled base composition of the real target windows, for the composition-matched ensemble
    counts = {b: 0 for b in BASES}
    for d in designs:
        for ch in d["target"]:
            if ch in counts:
                counts[ch] += 1
    keys = list(BASES)
    total = sum(counts[k] for k in keys)
    cum, acc = [], 0
    for k in keys:
        acc += counts[k]
        cum.append(acc)

    ensembles = {}
    per_design = []
    fallbacks = 0

    gap_pos = list(pgp.GAP)
    wing_pos = [p for p in range(pgp.OLIGO_LEN) if p not in pgp.GAP]

    bounds = mature_exon_boundaries()

    for name in ("scrambled_mononucleotide", "scrambled_dinucleotide",
                 "random_uniform", "random_composition_matched",
                 "wings_scrambled_gap_held", "gap_scrambled_wings_held",
                 "random_parent_chimera",
                 "donor_terminus_chimera", "exon_terminus_chimera",
                 "exon_terminus_chimera_novel_acceptor"):
        # ⚠ One stream per ensemble, seeded from the ensemble NAME, so adding or removing an
        # ensemble cannot shift the draws of the ones either side of it.
        rng = Rng(SEED ^ sum((i + 1) * ord(c) for i, c in enumerate(name)))
        hits = nr4a3 = 0
        hits_2 = nr4a3_2 = 0
        runs = []
        runs_nr4a3 = []
        runs_nr4a3_specific = []
        per_design_rows = []
        for di, d in enumerate(designs):
            t, j = d["target"], d["junction_offset"]
            dh = dn = 0
            for _ in range(N_DRAWS):
                if name == "scrambled_mononucleotide":
                    q = scramble_mono(t, rng)
                elif name == "scrambled_dinucleotide":
                    q, fell_back = scramble_dinucleotide(t, rng)
                    fallbacks += 1 if fell_back else 0
                elif name == "wings_scrambled_gap_held":
                    q = scramble_positions(t, wing_pos, rng)
                elif name == "gap_scrambled_wings_held":
                    q = scramble_positions(t, gap_pos, rng)
                elif name == "random_uniform":
                    q = draw_uniform(rng, pgp.OLIGO_LEN)
                elif name == "random_composition_matched":
                    q = draw_composition(rng, pgp.OLIGO_LEN, keys, cum, total)
                elif name == "donor_terminus_chimera":
                    q = draw_donor_terminus_chimera(rng, parents, d["donor"], d["donor_len"], bounds)
                elif name == "exon_terminus_chimera":
                    q = draw_exon_terminus_chimera(rng, parents, d["donor"], d["donor_len"], bounds)
                elif name == "exon_terminus_chimera_novel_acceptor":
                    q = draw_exon_terminus_chimera(rng, parents, d["donor"], d["donor_len"], bounds,
                                                   exclude_real_acceptor=True)
                else:  # random_parent_chimera
                    q = draw_parent_chimera(rng, parents, d["donor"], j)
                run, gene = _best_run(q, parents, idx)
                runs.append(run)
                runs_nr4a3.append(run if gene == "NR4A3" else 0)
                runs_nr4a3_specific.append(_best_run(q, nr4a3_only, idx_nr4a3)[0])
                if run >= pgp.MIN_DUPLEX_BP:
                    hits += 1
                    dh += 1
                    if gene == "NR4A3":
                        nr4a3 += 1
                        dn += 1
                if run >= SECONDARY_CUT_BP:
                    hits_2 += 1
                    nr4a3_2 += 1 if gene == "NR4A3" else 0
            per_design_rows.append(round(dh / N_DRAWS, 4))
            if name == "scrambled_mononucleotide":
                per_design.append({
                    "junction": d["junction"],
                    "antisense_5to3": d["antisense_5to3"],
                    "gap_specificity_margin": d["margin"],
                    "observed_liable": obs_runs[di] >= pgp.MIN_DUPLEX_BP,
                    "observed_longest_run_bp": obs_runs[di],
                    "scrambled_rate_liable": round(dh / N_DRAWS, 4),
                    "scrambled_rate_liable_against_NR4A3": round(dn / N_DRAWS, 4),
                })
        s = _summary(hits, nr4a3, runs, len(runs))
        s["expected_n_liable_designs_if_null"] = round(sum(per_design_rows), 2)
        s[f"at_{SECONDARY_CUT_BP}bp"] = {
            "n_liable": hits_2,
            "rate_liable": round(hits_2 / len(runs), 5) if runs else None,
            "rate_liable_wilson95": wilson(hits_2, len(runs)),
            "n_liable_against_NR4A3": nr4a3_2,
            "rate_liable_against_NR4A3": round(nr4a3_2 / len(runs), 5) if runs else None,
        }
        s["cut_ladder"] = _ladder(runs, runs_nr4a3, runs_nr4a3_specific)
        ensembles[name] = s
        if name == "scrambled_dinucleotide":
            s["_mononucleotide_fallbacks"] = fallbacks

    # the analytic expectation, stated so the measured rate has something to be checked against
    parent_nt = sum(len(s) for s in parents.values())
    n_windows = sum(max(0, len(s) - pgp.OLIGO_LEN + 1) for s in parents.values())
    gap_nt = len(pgp.GAP)
    p_gap, p_extend = analytic_p_site(gap_nt)
    p_site = p_gap * p_extend
    exp_sites = n_windows * p_site

    return {
        "_what": ("The rate at which ARBITRARY 16-mers let a mature wild-type parent transcript "
                  "pair the whole catalytic gap at >= "
                  f"{pgp.MIN_DUPLEX_BP} contiguous base pairs — the null that screen 4's "
                  f"{obs_hits} of {n_obs} had been reported without."),
        "_why": ("A count with no null cannot be large or small. The genome scan states a chance "
                 "expectation per 16-mer; the mature-parent screen did not, so its headline had no "
                 "anchor. Raised by external review of the submission manuscript, 2026-08-15."),
        "_what_this_is_not": [
            "Not a significance test. The 190 design records are 176 distinct molecules tiled at "
            "overlapping registers across 38 junctions, so they are not independent draws and no "
            "test treating them as such would be right about its own denominator. Proportions "
            "carry Wilson intervals; the per-design paired rate is the honest comparison.",
            "Not a measurement of off-target activity. A duplex is necessary for RNase-H1 cleavage "
            "and is not sufficient, and a scrambled oligonucleotide clearing this screen is not "
            "thereby safe.",
            "Not transcriptome-wide — six parent transcripts, the bound screen 4 itself carries.",
            "Not a null for any other screen. Screens 1, 2, 3 and 5 have their own bounds.",
        ],
        "_cost": "$0 — offline, over two committed artifacts, no network and no credentials.",
        "method": {
            "instrument": ("aso_parent_gap_pairing.longest_run_through_gap, unchanged — same six "
                           "mature parents, forward orientation only, same MIN_DUPLEX_BP. Only the "
                           "query changes."),
            "draws_per_design_per_ensemble": N_DRAWS,
            "seed": SEED,
            "prng": "splitmix64, written out in aso_parent_null.py for bit-stability",
            "min_duplex_bp": pgp.MIN_DUPLEX_BP,
            "oligo_len": pgp.OLIGO_LEN,
            "wing": pgp.WING,
            "gap_nt": gap_nt,
            "parents_searched": sorted(parents),
            "parent_nt_searched": parent_nt,
            "parent_windows_searched": n_windows,
            "pooled_base_composition_of_real_targets": counts,
            "sources": ["aso-premrna-sequences.json", os.path.basename(pgp.ATLAS)],
        },
        "analytic_expectation": {
            "_what": ("What an independent-uniform-base 16-mer should meet, computed rather than "
                      "assumed, so the measured ensembles have something to be checked against."),
            "p_all_gap_positions_pair": p_gap,
            "p_run_reaches_min_duplex_given_gap_paired": round(p_extend, 8),
            "p_site_per_parent_window": p_site,
            "expected_sites_per_16mer": round(exp_sites, 5),
            "expected_rate_liable_poisson": round(1 - pow(2.718281828459045, -exp_sites), 5),
            "_checks_the_measured_ensembles": ("This is the quantity `random_uniform` estimates by "
                                               "sampling, so the two are a check on each other; "
                                               "Poisson sits slightly high because sites within one "
                                               "transcript overlap rather than arriving "
                                               "independently."),
            "_caveat": ("Independent uniform bases. Real transcript sequence is composition-skewed "
                        "and repetitive, so this separates 'more than chance' from 'at chance' and "
                        "nothing finer — the same qualification the manuscript's genome-scan null "
                        "carries."),
        },
        "observed": {
            "n_designs": n_obs,
            "n_liable": obs_hits,
            "rate_liable": round(obs_hits / n_obs, 5),
            "rate_liable_wilson95": wilson(obs_hits, n_obs),
            "n_liable_against_NR4A3": obs_nr4a3,
            "rate_liable_against_NR4A3": round(obs_nr4a3 / n_obs, 5),
            "mean_longest_run_bp": round(sum(obs_runs) / n_obs, 4),
            "_agrees_with_screen_4": ("This arm is re-measured through the index rather than copied "
                                      "from aso-parent-gap-pairing.json; the two agree by test."),
        },
        "cut_sensitivity": {
            "_what": (f"The same instrument read at {SECONDARY_CUT_BP} contiguous base pairs, the "
                      f"loose end of the cited range, beside {pgp.MIN_DUPLEX_BP}, the strict end "
                      f"the manuscript reports throughout."),
            "_why": ("The manuscript disclosed the loose reading as the more inclusive reading of "
                     "the liability. Measured, it is not a reading of the liability at all: at "
                     f"{SECONDARY_CUT_BP} the exon-terminus chimera null is within a percentage "
                     "point of the observed rate, so the loose count is what any chimera between "
                     "two real transcripts gives and carries no information about this disease's "
                     "breakpoints. ⛔ THIS FIELD USED TO END 'the strict cut is the one on which "
                     "the observed rate stands clear of every null, which is why it is the one "
                     "reported', AND THAT WAS FALSE — see `cut_ladder`, which was written to check "
                     "it. Across cuts 6-13 the excess over the strongest null changes sign four "
                     "times, and the strongest null lies INSIDE the observed rate's nominal Wilson "
                     "interval at every cut except 6 (where the null is above it) and 11 (where it "
                     "is below). Ten is the cut this work adopts and reports; it is not the cut at "
                     "which the observed rate separates, and no cut in the reachable range "
                     "resolves an excess over a chimera of two real exon termini."),
            "cuts_bp": [SECONDARY_CUT_BP, pgp.MIN_DUPLEX_BP],
            "observed_n_liable": {str(SECONDARY_CUT_BP): obs_hits_2,
                                  str(pgp.MIN_DUPLEX_BP): obs_hits},
            # ⛔ THE RATE AT EACH CUT NEEDS A MACHINE HOME OF ITS OWN. `observed.rate_liable` is the
            # rate at the STRICT cut only, and the abstract quotes the loose cut's rate beside it.
            # Without this field the only pin available for the loose reading resolved to the strict
            # rate, which is how a correct, measured 92.1% came to fail lint_consistency against
            # 45.8 (CLAUDE.md rule 1: one fact, one place — and the loose rate is a different fact).
            "observed_rate_liable": {str(SECONDARY_CUT_BP): round(obs_hits_2 / n_obs, 5),
                                     str(pgp.MIN_DUPLEX_BP): round(obs_hits / n_obs, 5)},
            "observed_n_liable_against_NR4A3": {str(SECONDARY_CUT_BP): obs_nr4a3_2,
                                                str(pgp.MIN_DUPLEX_BP): obs_nr4a3},
            "observed_rate_liable_against_NR4A3": {
                str(SECONDARY_CUT_BP): round(obs_nr4a3_2 / n_obs, 5),
                str(pgp.MIN_DUPLEX_BP): round(obs_nr4a3 / n_obs, 5)},
            "n_designs": n_obs,
            "n_junctions": len(runs_by_junction),
            # ⛔ THE JUNCTION-LEVEL READING, WHICH RUNS THE OTHER WAY AND WAS THE ONE MISSING. The
            # design-level count grows when the cut loosens (175 against 87) and the junction-level
            # count of "somewhere at this junction a design clears" COLLAPSES (9 against 35). The
            # manuscript stated the first at both cuts and the second at one, which put the
            # deflating reading on the count that protects the modality and not on the count that
            # protects the negative.
            "n_junctions_with_a_clearing_design": {
                str(cut): sum(1 for runs_j in runs_by_junction.values()
                              if any(r < cut for r in runs_j))
                for cut in (SECONDARY_CUT_BP, pgp.MIN_DUPLEX_BP)
            },
            # ⭐⭐ THE LADDER. Every arm at every cut of the criterion, so the question "is this a
            # finding or an artefact of the cut?" is answered by a curve rather than by the two
            # points the manuscript previously chose. Read the observed row against
            # `null_ensembles[*].cut_ladder` at the same cut.
            "cut_ladder_bp": list(CUT_LADDER),
            "observed_cut_ladder": _ladder(obs_runs, obs_runs_nr4a3,
                                           obs_runs_nr4a3_specific),
            "n_junctions_with_a_clearing_design_by_cut": {
                str(cut): sum(1 for runs_j in runs_by_junction.values()
                              if any(r < cut for r in runs_j))
                for cut in CUT_LADDER
            },
            "n_junctions": len(runs_by_junction),
            # ⛔ THE SUBSET THAT DECIDES ANYTHING. 33 of the 38 panel junctions are arithmetically
            # in-frame exon pairs no patient is reported to carry, so the panel-wide rate is not
            # the rate a laboratory choosing a reagent for a real breakpoint faces. This row is
            # that rate, at every cut.
            "published_breakpoint_junctions": sorted(_pub_panel),
            "observed_cut_ladder_at_published_breakpoint_junctions":
                _ladder(_pub_runs, _pub_runs_nr4a3, _pub_runs_nr4a3_specific),
            "n_published_breakpoint_junctions_with_a_clearing_design_by_cut": {
                str(cut): sum(1 for j, runs_j in runs_by_junction.items()
                              if j in _pub_panel and any(r < cut for r in runs_j))
                for cut in CUT_LADDER
            },
            "_read_with": ("null_ensembles[*]['at_%dbp'], which carries every ensemble at the loose "
                           "cut so neither count is quoted without its anchor." % SECONDARY_CUT_BP),
        },
        "null_ensembles": ensembles,
        "per_design_scrambled_mononucleotide": per_design,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    new = json.dumps(art, indent=1, sort_keys=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("aso-parent-null.json is stale; re-run without --check", file=sys.stderr)
            return 1
        print("parent-null artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    o, e = art["observed"], art["null_ensembles"]
    print(f"wrote {os.path.basename(OUT)}: observed {o['n_liable']}/{o['n_designs']} "
          f"({o['rate_liable']:.1%}); scrambled {e['scrambled_mononucleotide']['rate_liable']:.1%}; "
          f"uniform {e['random_uniform']['rate_liable']:.1%}; "
          f"gap held {e['wings_scrambled_gap_held']['rate_liable']:.1%}; "
          f"gap scrambled {e['gap_scrambled_wings_held']['rate_liable']:.1%}; "
          f"parent chimera {e['random_parent_chimera']['rate_liable']:.1%}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
