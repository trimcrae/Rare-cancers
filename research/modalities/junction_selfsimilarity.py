#!/usr/bin/env python3
"""Near-self search: which human peptides come within one or two substitutions of a junction binder?

WHAT QUESTION THIS SETTLES, AND WHY IT IS NOT THE ONE `junction_proteome_novelty.py` ANSWERS.
That script asks whether a junction peptide IS a human peptide — exact substring, and its own
docstring says what a miss does not license: "a T-cell receptor sees a surface, not a string, and a
peptide differing from a self peptide at a non-contact position can still be cross-recognised."
That sentence names a failure mode and then leaves it unmeasured. This script measures it. An
external reviewer asked for exactly this (aiXiv review 1364, suggestion 4: "search the reviewed
proteome using a tolerant alignment ... assess whether any self-peptides could be cross-recognized,
and report these as potential safety flags").

⛔ WHAT A CLEAN RESULT HERE DOES NOT LICENCE. Sequence distance is not TCR distance. Two peptides at
Hamming distance 3 can present near-identical surfaces, and two at distance 1 can present different
ones; substitution matrices approximate chemistry, not recognition. A null result excludes ONE more
failure mode — a close self-peptide nobody had looked for — and is not evidence of safety, of
tolerance, or that any construct may be given to a person.

⚠ THE ANCHOR CLASSIFICATION IS A CONVENTION AND IS FLAGGED AS ONE. Class I peptides are anchored
principally at P2 and the C-terminus, which point INTO the groove; the residues between them face
the TCR. So a self-peptide differing from a neoepitope ONLY at anchors presents nearly the same
surface to a T cell — that is the concerning case, not the reassuring one — while differences in the
middle change the surface the TCR reads. ⛔ But the anchor set is allele-specific and this script
applies the P2/PΩ convention uniformly: HLA-A*01:01 in particular reads P3 as a primary anchor, so
its rows must be read with that caveat, which the artifact carries per row rather than in a footnote.

⚠ AND THE COUNT NEEDS A NULL, because "we found k near-self peptides" means nothing without how many
a peptide of this length and composition finds by chance. Each query is shuffled `N_NULL` times and
re-searched; the null mean and max are reported beside the observed count. This is the decoy control
whose absence the manuscript's own §7 concedes.

Needs numpy (CI). The search is a vectorised Hamming scan over the whole reviewed proteome: for a
query of length L, L equality tests over the ~2e7-residue array, which is seconds rather than the
hours a Python loop would take.

Output: junction-selfsimilarity.json
"""
import json
import os
import sys

import junction_proteome_novelty as jpn

HERE = os.path.dirname(os.path.abspath(__file__))
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
MATRIX = os.path.join(HERE, "epitope-allele-matrix.json")
OUT = os.path.join(HERE, "junction-selfsimilarity.json")

#: Substitutions tolerated. 1 and 2 are the reviewer's ask, and they are also where the search stays
#: informative: for a 9-mer against ~2e7 proteome 9-mers the chance expectation is ~0.5 hits at
#: distance <=2 and ~24 at distance 3, so 3 would return noise and read as a finding.
MAX_MISMATCH = 2
#: Shuffles per query for the chance baseline. Each shuffle is a full proteome scan, so this is the
#: run's cost centre: 50 is enough to separate "one hit" from "none expected" at an expected rate
#: near 0.5, and 200 would quadruple the runtime to sharpen a decimal nobody reads.
N_NULL = 50


def queries():
    """The peptides worth asking about: every predicted binder, strong ones marked.

    ⚠ NOT all 174 junction peptides. A near-self hit only matters for a peptide that could be
    presented at all, and searching the whole set would bury four rows that carry the safety
    question in 174 that do not. The strong binders are the paper's leads and are flagged as such.
    """
    bp = json.load(open(BREAKPOINTS))
    strong = {}
    if os.path.exists(MATRIX):
        for c in json.load(open(MATRIX))["strong_binders"]:
            strong.setdefault(c["peptide"], []).append(
                {"allele": c["allele"], "percentile": c["percentile"]})
    out = {}
    for b in bp.get("predicted_binders_ranked", []):
        p = b["peptide"]
        rec = out.setdefault(p, {"peptide": p, "length": len(p), "predicted_binders": []})
        rec["predicted_binders"].append({"allele": b.get("allele"), "class": b.get("class"),
                                         "affinity_nM": b.get("affinity_nM")})
    for p, rec in out.items():
        rec["strong_on_34_allele_panel"] = strong.get(p, [])
    return sorted(out.values(), key=lambda r: (not r["strong_on_34_allele_panel"], r["peptide"]))


def anchor_positions(length):
    """P2 and the C-terminus, 1-indexed. The convention, with the caveat in the module docstring."""
    return {2, length}


def scan(np, arr, bounds, query, max_mm):
    """Every proteome L-mer within `max_mm` substitutions of `query`. Returns list of (index, mm)."""
    L = len(query)
    n = arr.shape[0] - L + 1
    if n <= 0:
        return []
    mm = np.zeros(n, dtype=np.uint8)   # <=11 mismatches; half the memory traffic of int16
    for i, ch in enumerate(query.encode()):
        mm += (arr[i:i + n] != ch)
    hits = np.nonzero(mm <= max_mm)[0]
    # ⛔ A WINDOW STRADDLING TWO PROTEINS IS NOT A HUMAN PEPTIDE. The sentinel byte never equals a
    # residue so it always counts as a mismatch, but at max_mm>=1 a window carrying ONE sentinel can
    # still pass. Dropping those is not an optimisation; keeping them would invent self-peptides.
    return [(int(i), int(mm[i])) for i in hits
            if not bounds(int(i), L)]


def main():
    try:
        import numpy as np
    except ImportError:
        print("  numpy absent — this scan is CI-only; nothing written", file=sys.stderr)
        return 1
    import random

    qs = queries()
    if not qs:
        print("  no predicted binders to test", file=sys.stderr)
        return 1
    print(f"  {len(qs)} predicted binders to search at Hamming <= {MAX_MISMATCH}", file=sys.stderr)

    try:
        entries = jpn.fetch_proteome(tries=3)
    except Exception as e:  # noqa: BLE001 — the failure text IS the record
        json.dump({"⛔_STATUS": "FETCH FAILED — THIS ARTIFACT CARRIES NO RESULT",
                   "⚠_do_not_quote": ("Replaced so a stale result could not read as current. "
                                      "Re-run when UniProt is reachable."),
                   "error": f"{type(e).__name__}: {e}", "url": jpn.PROTEOME_URL,
                   "generated_utc": jpn._utcnow()}, open(OUT, "w"), indent=2)
        print(f"  PROTEOME FETCH FAILED: {e}", file=sys.stderr)
        return 1

    hay = jpn.SENTINEL.join(seq for _, _, seq in entries)
    arr = np.frombuffer(hay.encode("ascii", "replace"), dtype=np.uint8)
    offsets, pos = [], 0
    for acc, name, seq in entries:
        offsets.append((pos, pos + len(seq), acc, name))
        pos += len(seq) + 1
    starts = [o[0] for o in offsets]
    sentinels = np.nonzero(arr == ord(jpn.SENTINEL))[0]

    def straddles(i, L):
        k = np.searchsorted(sentinels, i)
        return bool(k < sentinels.shape[0] and sentinels[k] < i + L)

    def locate(i):
        import bisect
        k = bisect.bisect_right(starts, i) - 1
        if k < 0:
            return None, None, None
        s, e, acc, name = offsets[k]
        return (acc, name, i - s + 1) if s <= i < e else (None, None, None)

    rng = random.Random(20260823)   # fixed: the null is part of the result and must reproduce
    rows, n_flagged = [], 0
    for q in qs:
        p = q["peptide"]
        anchors = anchor_positions(len(p))
        hits = []
        for i, mm in scan(np, arr, straddles, p, MAX_MISMATCH):
            acc, name, at = locate(i)
            if acc is None:
                continue
            self_pep = hay[i:i + len(p)]
            diffs = [k + 1 for k in range(len(p)) if self_pep[k] != p[k]]
            hits.append({
                "self_peptide": self_pep, "accession": acc, "protein": name, "position": at,
                "n_mismatches": mm, "mismatch_positions": diffs,
                "all_mismatches_at_anchors": bool(diffs) and set(diffs) <= anchors,
                "⚠_anchor_convention": ("P2 and the C-terminus, applied uniformly; HLA-A*01:01 "
                                        "reads P3 as a primary anchor, so read its rows with that"),
            })
        # ⚠ THE NULL IS PER QUERY, because chance depends on the query's own length and composition.
        null_counts = []
        for _ in range(N_NULL):
            shuf = list(p)
            rng.shuffle(shuf)
            null_counts.append(len(scan(np, arr, straddles, "".join(shuf), MAX_MISMATCH)))
        exact = [h for h in hits if h["n_mismatches"] == 0]
        flagged = [h for h in hits if h["n_mismatches"] > 0 and h["all_mismatches_at_anchors"]]
        n_flagged += len(flagged)
        rows.append(dict(q,
                         n_near_self=len([h for h in hits if h["n_mismatches"] > 0]),
                         n_exact_self=len(exact),
                         n_anchor_only_near_self=len(flagged),
                         null_mean=round(sum(null_counts) / len(null_counts), 3),
                         null_max=max(null_counts),
                         hits=sorted(hits, key=lambda h: (h["n_mismatches"], h["accession"]))))

    result = {
        "_what": ("Near-self search: human proteome peptides within "
                  f"{MAX_MISMATCH} substitutions of each predicted EWSR1::NR4A3 junction binder, "
                  "with the mismatch positions classified against the class I anchor convention."),
        "_why": ("Exact-match novelty (junction-proteome-novelty.json) leaves TCR cross-reactivity "
                 "with near-self peptides untested, and says so. This is that test."),
        "⛔_what_this_is_not": (
            "Not a safety result. Sequence distance is not TCR distance: peptides at Hamming "
            "distance 3 can present near-identical surfaces and peptides at distance 1 can present "
            "different ones. A null result excludes one more failure mode and nothing else. Nothing "
            "here supports administration of any construct to a person."),
        "_method": (f"vectorised Hamming scan of every proteome L-mer against each query, "
                    f"mismatches <= {MAX_MISMATCH}; windows straddling a record boundary dropped; "
                    f"per-query chance baseline from {N_NULL} residue shuffles of the same query, "
                    "re-searched identically (seed 20260823)."),
        "⚠_anchor_convention": ("Anchors taken as P2 and the C-terminus for every length, which is "
                               "the general class I rule and not an allele-specific motif. "
                               "HLA-A*01:01 reads P3 as a primary anchor; rows for peptides called "
                               "on it are marked and should be read with that caveat."),
        "generated_utc": jpn._utcnow(),
        "_proteome": {"source": "UniProtKB REST", "url": jpn.PROTEOME_URL,
                      "proteome_id": "UP000005640", "reviewed_only": True,
                      "isoforms_included": True, "trembl_included": False,
                      "n_sequences": len(entries), "n_residues": int(arr.shape[0])},
        "_cost": "$0 — CI only, one public UniProt fetch, no GPU and no rental.",
        "max_mismatches": MAX_MISMATCH,
        "n_queries": len(rows),
        "n_queries_with_any_near_self": sum(1 for r in rows if r["n_near_self"]),
        "n_anchor_only_near_self_total": n_flagged,
        "queries": rows,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print(f"  near-self: {result['n_queries_with_any_near_self']}/{len(rows)} binders have a "
          f"human peptide within {MAX_MISMATCH} substitutions; {n_flagged} of those differ only at "
          f"anchor positions", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
