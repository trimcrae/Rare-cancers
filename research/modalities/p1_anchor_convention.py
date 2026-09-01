#!/usr/bin/env python3
"""
Is position 1 a PRIMARY anchor, a SECONDARY (auxiliary) anchor, or neither, for the class I alleles
that restrict the predicted EWSR1::NR4A3 junction binders?

⚠ "THE FIVE ALLELES" IS THE QUESTION THIS MODULE WAS HANDED AND IT IS THE WRONG NUMBER. The alleles
are DERIVED from `junction-selfsimilarity.json` rather than typed, and there are SIX: HLA-A*30:02
calls the lead peptide NMPCVQAQY on the 34-allele panel alongside HLA-B*15:01, and NMPCVQAQY is
exactly the peptide whose near-self neighbour differs at position 1 alone. See the ALLELES note below.

⛔ WHY THIS EXISTS, AND WHY IT IS NOT A NEW SEARCH.
`junction-selfsimilarity.json` reports that ZERO of the 11 predicted class I junction binders has a
near-self proteome neighbour whose differences fall only at anchor positions, under the general class
I convention {P2, C-terminus}. `junction_anchor_convention_sensitivity.py` then measured how far that
null travels across conventions and found the position it turns on: counting P1 as an anchor takes the
count from 0 hits / 0 binders to 6 hits / 6 binders, three of them differing at P1 ALONE and one of
those three the lead peptide. Both modules stop at the same wall and say so in the same words --
"this repository holds no allele-specific motif source" -- so the null has been carried in four places
in a live manuscript as CONDITIONAL on a question nobody had asked a database.

This module asks it. It is the missing motif source, and nothing else: it adds no proteome hit, runs
no predictor, and re-scores the committed near-self hits only as a downstream consequence of what the
motif data say.

★★ "PRIMARY ANCHOR" IS A DEFINITION, NOT AN OBSERVATION -- SO THE CONVENTION IS DECLARED HERE, BEFORE
ANY DATA IS FETCHED, AND TRAVELS INTO EVERY OUTPUT ROW.
This whole problem exists because a convention went unstated. Two independent conventions are applied,
both read out of a fetched dataset rather than asserted:

  CONVENTION A -- INFORMATION CONTENT OF THE BINDING MOTIF (quantitative, mass-spectrometry derived).
    From the MixMHCpred v3 position weight matrices, which are position probability matrices for
    naturally presented (eluted) ligands divided by the human proteome amino-acid background -- the
    construction the MHC Motif Atlas paper describes for its own motifs (Nucleic Acids Research 2023,
    doi:10.1093/nar/gkac965: "The Position Weight Matrices (PWMs) representing the final motifs were
    computed by normalizing the PPMs with the amino acid background frequencies of the human
    proteome"). For each position p we compute the Kullback-Leibler divergence of the position's
    amino-acid distribution from that same background,

        IC(p) = SUM_aa  f(aa,p) * log2( f(aa,p) / bg(aa) )     [bits]

    a background-corrected information measure of the kind a reader eyeballs on a sequence logo to
    call a position an anchor.
    ⛔ AND THE ATLAS'S OWN LOGO USES A DIFFERENT FUNCTION, WHICH THIS MODULE FIRST GOT WRONG AND NOW
    COMPUTES TOO. An earlier draft of this docstring said the KL divergence above was "exactly the
    stack height" of the Atlas's logo. It is not. The Atlas F.A.Q. — fetched in CI run 33553076455,
    because its host 403s from the dev sandbox — defines that height as `log2(20) + Σ_a p_a log2(p_a)`
    over the background-corrected-then-renormalised distribution, i.e. against a UNIFORM reference,
    with a maximum of log2(20) = 4.3219. Both quantities are reported per position
    (`information_content_bits` and `atlas_logo_information_content_bits`), and whether they grade a
    position the same way is COMPUTED on every row rather than claimed here.

    ⛔ A CUT-OFF ON IC IS ITSELF A CONVENTION, so TWO are applied to every position and both travel
    into every output row:

        RELATIVE   PRIMARY: IC(p) >= 0.50 * max_p IC(p);  SECONDARY: >= 0.15 * max_p IC(p)
        ABSOLUTE   PRIMARY: IC(p) >= 1.0 bits;            SECONDARY: >= 0.5 bits

    ★ THE ABSOLUTE RULE IS THE ONE THE KNOWN-POSITIVE CONTROL VALIDATES, and it is the one the anchor
    sets used for re-scoring are taken from: at >= 1.0 bit it reproduces the canonical primary-anchor
    set of every allele here, HLA-A*01:01's P3 included. The relative rule does not — HLA-A*01:01's
    C-terminal Y is so dominant that P2, an anchor under every published convention, falls to 29 % of
    it. Neither rule was tuned to produce the P1 answer: P1's verdict is identical under both.
    ⚠ Every raw IC value and every ratio is written to the output so any reader can re-apply their own
    cut-off. The finding survives every threshold anyone would choose for the PRIMARY line and is
    threshold-sensitive only at the SECONDARY/NEITHER line; the output says which of the two each row
    is standing on.

  CONVENTION B -- THE CURATED SYFPEITHI MOTIF SCORES (ordinal, pooled-sequencing derived).
    SYFPEITHI's per-allele matrices as redistributed inside epytope. This is the resource that encodes
    the anchor / auxiliary-anchor distinction as an ordinal score rather than leaving it to a reader's
    eye, so it is the closest thing to a direct answer to the question as posed. ⛔ We do NOT assert
    what SYFPEITHI's tiers are called: the output reports the per-position MAXIMUM score, and the claim
    made from it is purely ordinal -- where P1's best score sits relative to P2, the C-terminus, and
    the middle positions, which are the positions every convention agrees are not anchors.

★ THE KNOWN-POSITIVE CONTROL, WHICH IS WHAT MAKES THE P1 VERDICT CREDIBLE.
Two facts this repository already holds must fall out of the measurement before its answer about P1 is
worth anything, and a run that fails either marks itself:
  (1) P2 and the C-terminus must be the dominant positions -- the general class I rule
      `junction-selfsimilarity.json` states it used.
  (2) HLA-A*01:01 must read P3 as a primary anchor -- the caveat that artifact raises against itself.
Neither was fed in. Both are predictions this module can fail.

⛔ WHAT THIS IS NOT.
  - Not a measurement of what a T-cell receptor can see. Motif information content measures the
    selectivity of the GROOVE for a side chain. A position with near-background information content is
    a position whose side chain the allele does not select on; whether that side chain is solvent
    exposed and readable by a receptor is a STRUCTURAL question this module does not touch. The
    manuscript's ranking uses "anchor" as a proxy for "the T cell cannot see it", and the proxy is not
    validated here. Settling it needs per-position solvent accessibility over class I pMHC crystal
    structures -- a different fetch, named in the output as an open question rather than assumed away.
  - Not a safety, immunogenicity or presentation result. Every input to the hits being re-scored is a
    binding prediction plus a sequence-distance search. Sequence distance is not receptor distance.
  - Not a determination for any allele outside those the committed artifact restricts on, and not for
    lengths a source does not cover. A source with no matrix for an allele/length pair reports MISSING
    -- an HTTP 404 recorded as a real absence, never filled in by a guess.

Inputs (fetched over the network, at PINNED commits; every blob's sha256 is recorded):
  * GfellerLab/MixMHCpred  lib/pwm/class1_<L>/PWM_<allele>_<i>.csv, lib/pwm/class1_<L>/alphas.txt,
                           lib/alleles_list.txt, lib/proteome/AA_frequency_human_Methionine.csv
  * KohlbacherLab/epytope  epytope/Data/pssms/syfpeithi/mat/<allele>_<L>.py
Local input (committed, read-only):
  * junction-selfsimilarity.json -- re-scored under the MEASURED anchor sets.
Output: p1-anchor-convention.json
Cost:  $0 -- two public raw.githubusercontent reads and pure-stdlib arithmetic. No predictor, no GPU,
       no rental.
"""

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SELFSIM = os.path.join(HERE, "junction-selfsimilarity.json")
OUT = os.path.join(HERE, "p1-anchor-convention.json")

# ⛔ PINNED. A motif dataset that moves under a published claim is the same defect class as a
# regenerated total nobody re-derived. These are the commits the answer in the output was computed
# from; changing one is a re-run, not an edit.
MIXMHCPRED_REPO = "GfellerLab/MixMHCpred"
MIXMHCPRED_COMMIT = "c29e4db17abe6266bfee72750efb713459540d18"
EPYTOPE_REPO = "KohlbacherLab/epytope"
EPYTOPE_COMMIT = "de6c5bdcb360d59eb13ff5b49b6349502ae81765"
RAW = "https://raw.githubusercontent.com/{repo}/{commit}/{path}"

# ⛔ THE ALLELE LIST IS DERIVED FROM THE COMMITTED ARTIFACT, NEVER TYPED.
# ⚠ THIS IS NOT STYLE. The first version of this module carried a hand-written list of FIVE alleles
# plus a check that the list matched the artifact -- and the check failed on its first run:
# `junction-selfsimilarity.json` restricts on SIX. The sixth, HLA-A*30:02, calls the LEAD peptide
# NMPCVQAQY on the 34-allele panel alongside HLA-B*15:01, and NMPCVQAQY is precisely the peptide whose
# near-self neighbour differs at position 1 alone. A five-allele answer would have left the lead
# peptide's second restriction unexamined while reading as complete -- and A*30:02 turns out to be the
# one allele of the six where position 1 carries a real signal.
# ⛔ AND THE FIVE ARE NOT THIS MODULE'S INVENTION. They are `emc-vaccine-development-path.md` §B3 line
# 675 -- "Whether position 1 is an anchor for HLA-A*01:01, B*07:02, B*15:01, B*35:01 or B*44:02 is not
# established here" -- in a manuscript that names HLA-A*30:02 in its own ABSTRACT as the lead peptide's
# second presenting allele. One-of-a-pair, in the one paragraph that asks the question.
# Names are mapped mechanically (HLA-A*01:01 -> A0101 / A_0101) and every mapping is validated against
# the fetched allele list, so an allele the sources do not carry reports MISSING rather than vanishing.
LENGTHS = [8, 9, 10, 11, 12, 13, 14]

# Two grading rules, both reported for every position, because a threshold is a convention and this
# whole problem exists because a convention went unstated.
#
#   RELATIVE -- a fraction of the allele's own strongest position. Intuitive, and what a reader
#     eyeballing a logo does. ⚠ It mis-grades an allele with one overwhelming position: HLA-A*01:01's
#     C-terminal Y is so dominant that P2 -- an anchor under every published convention -- falls to 29%
#     of it.
#   ABSOLUTE -- a floor in bits. ★ THIS IS THE ONE THE KNOWN-POSITIVE CONTROL VALIDATES: at >= 1.0 bit
#     it reproduces the canonical primary-anchor set of all six alleles, HLA-A*01:01's P3 included,
#     and it is the rule the anchor sets used for re-scoring are taken from. It was not tuned to
#     produce the P1 answer -- P1's verdict is identical under both rules.
PRIMARY_FRACTION = 0.50
SECONDARY_FRACTION = 0.15
PRIMARY_BITS = 1.0
SECONDARY_BITS = 0.5

_FETCHES = []


def fetch(repo, commit, path):
    """GET one file at a pinned commit and record url + sha256 + byte count."""
    url = RAW.format(repo=repo, commit=commit, path=path)
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-p1-anchor/1.0"})
    with urllib.request.urlopen(req, timeout=90) as fh:
        blob = fh.read()
    _FETCHES.append({
        "url": url,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "bytes": len(blob),
    })
    return blob.decode("utf-8")


def try_fetch(repo, commit, path):
    try:
        return fetch(repo, commit, path)
    except Exception as exc:                                    # noqa: BLE001
        _FETCHES.append({"url": RAW.format(repo=repo, commit=commit, path=path),
                         "error": f"{type(exc).__name__}: {exc}"})
        return None


# ─────────────────────────── convention A: motif information content ───────────────────────────

def read_background(text):
    rows = list(csv.reader(io.StringIO(text)))
    bg = {r[0]: float(r[1]) for r in rows[1:] if r and r[0]}
    total = sum(bg.values())
    return {k: v / total for k, v in bg.items()}


def read_pwm(text):
    """PWM_<allele>_<i>.csv -> {aa: [ratio per position]}. Values are PPM / background."""
    rows = list(csv.reader(io.StringIO(text)))
    return {r[0]: [float(x) for x in r[1:]] for r in rows[1:] if r and r[0]}


def read_tsv(text):
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def information_content(ppm, bg):
    """KL divergence of the position's amino-acid distribution from the background, in bits."""
    return sum(v * math.log2(v / bg[k]) for k, v in ppm.items() if v > 0 and bg.get(k, 0) > 0)


def atlas_logo_information_content(ppm, bg):
    """The MHC Motif Atlas's OWN logo stack height, in bits, computed from its published definition.

    ⛔ THIS IS A DIFFERENT FUNCTION FROM `information_content`, AND THE MODULE ORIGINALLY CLAIMED THEY
    WERE THE SAME ONE. That claim was wrong and is corrected here rather than in prose. The Atlas
    F.A.Q., fetched in CI run 33553076455 because the host 403s from the dev sandbox, defines it
    verbatim as: "the frequency (f_a) of each amino acid (a) is computed. These frequencies are then
    renormalized by the background amino acid frequencies (from the human proteome), and normalized
    again to 1 ... The total height of the letters at a given position represents the information
    content: log(20) + SUM_a p_a log(p_a) ... The logarithm is typically taken in base 2, hence the
    maximum at log2(20) = 4.3219."

    So it is log2(20) minus the entropy of the BACKGROUND-CORRECTED distribution, against a uniform
    reference -- not the KL divergence of the raw distribution from the background. Both are
    background-corrected information measures and they track each other closely on this data, but
    they are not the same function and this file reports both rather than picking one and calling it
    the other.
    """
    ratio = {k: ppm[k] / bg[k] for k in ppm if bg.get(k, 0) > 0}
    total = sum(ratio.values())
    if total <= 0:
        return 0.0
    p = {k: v / total for k, v in ratio.items()}
    return math.log2(20) + sum(v * math.log2(v) for v in p.values() if v > 0)


def motif_profile(allele, length, bg, n_motifs, alphas, pwms):
    """Weighted PPM per position, its IC in bits, and the top residues -- for one allele and length.

    ⚠ MULTIPLE SPECIFICITY IS MIXED, NOT DROPPED. Several of these alleles carry more than one motif
    (HLA-B*07:02 has four at length 9). Taking motif 1 alone would silently answer a different
    question, so the motifs are combined with the library's own mixture weights (alphas.txt), and the
    per-motif profiles are also reported so a reader can see whether the P1 verdict rests on the
    mixing.
    """
    n_pos = len(next(iter(pwms[0].values())))
    total_w = sum(alphas)
    rows = []
    for p in range(n_pos):
        ppm = {}
        for aa in bg:
            ppm[aa] = sum(w * m[aa][p] * bg[aa] for w, m in zip(alphas, pwms)) / total_w
        s = sum(ppm.values())
        ppm = {k: v / s for k, v in ppm.items()}
        top = sorted(ppm.items(), key=lambda kv: -kv[1])[:4]
        rows.append({
            "position": p + 1,
            "information_content_bits": round(information_content(ppm, bg), 4),
            "atlas_logo_information_content_bits":
                round(atlas_logo_information_content(ppm, bg), 4),
            "top_residues": [[k, round(v, 4)] for k, v in top],
        })
    mx = max(r["information_content_bits"] for r in rows)
    order = sorted(rows, key=lambda r: -r["information_content_bits"])
    rank = {r["position"]: i + 1 for i, r in enumerate(order)}
    for r in rows:
        bits = r["information_content_bits"]
        frac = bits / mx if mx > 0 else 0.0
        r["fraction_of_strongest_position"] = round(frac, 4)
        r["rank_by_information_content"] = rank[r["position"]]
        r["grade_relative"] = ("PRIMARY" if frac >= PRIMARY_FRACTION
                               else "SECONDARY" if frac >= SECONDARY_FRACTION
                               else "NEITHER")
        r["grade_absolute"] = ("PRIMARY" if bits >= PRIMARY_BITS
                               else "SECONDARY" if bits >= SECONDARY_BITS
                               else "NEITHER")
        ab = r["atlas_logo_information_content_bits"]
        r["grade_absolute_atlas_formula"] = ("PRIMARY" if ab >= PRIMARY_BITS
                                             else "SECONDARY" if ab >= SECONDARY_BITS
                                             else "NEITHER")
        # ⛔ MACHINE-CHECKED, NOT ASSERTED IN PROSE. "the two information measures give the same
        # grade" is a claim about the data, so it is computed on every row rather than written down.
        r["the_two_information_measures_agree"] = (
            r["grade_absolute"] == r["grade_absolute_atlas_formula"])
        r["grades_agree"] = r["grade_relative"] == r["grade_absolute"]
    return {
        "allele": allele,
        "length": length,
        "n_motifs_mixed": n_motifs,
        "mixture_weights": [round(a, 5) for a in alphas],
        "positions": rows,
    }


# ─────────────────────────── convention B: curated SYFPEITHI scores ───────────────────────────

_MAT_RE = re.compile(r"\{[^{}]*\}")


def read_syfpeithi(text, varname):
    """Parse `<NAME> = {0: {'A': 1, ...}, 1: {...}, ...}` without executing the module.

    ⛔ NOT `import`ed AND NOT `eval`ed. The file is a Python source file fetched over the network;
    running it would execute whatever it contains. json-decoding the literal after a quote swap keeps
    a hostile or malformed file from becoming code.
    """
    if not text.startswith(varname):
        head = text.split("=", 1)[0].strip()
        if head != varname:
            raise ValueError(f"expected `{varname} = ...`, found `{head}`")
    body = text.split("=", 1)[1].strip()
    body = body.replace("'", '"')
    body = re.sub(r"(?m)^\s*(\d+)\s*:", r'"\1":', body)
    body = re.sub(r"([{,]\s*)(\d+)(\s*:)", r'\1"\2"\3', body)
    obj = json.loads(body)
    return {int(k): v for k, v in obj.items()}


def syfpeithi_profile(allele, length, mat):
    rows = []
    for p in sorted(mat):
        d = {k: v for k, v in mat[p].items() if k != "X"}
        mx = max(d.values())
        rows.append({
            "position": p + 1,
            "max_score": mx,
            "residues_at_max": sorted([k for k, v in d.items() if v == mx and v > 0]),
        })
    overall = max(r["max_score"] for r in rows)
    # The definitionally non-anchor middle: everything strictly between P3 and the C-terminal residue.
    middle = [r["max_score"] for r in rows if 3 < r["position"] < length]
    for r in rows:
        r["fraction_of_strongest_position"] = round(r["max_score"] / overall, 4) if overall else 0.0
    return {
        "allele": allele,
        "length": length,
        "positions": rows,
        "strongest_position_score": overall,
        "middle_position_scores_P4_to_Cminus1": middle,
        "highest_middle_position_score": max(middle) if middle else None,
    }


# ─────────────────────────── the near-self re-scoring ───────────────────────────

def restricting_alleles(query):
    out = []
    for b in query.get("predicted_binders", []) or []:
        if b.get("allele"):
            out.append(b["allele"])
    for b in query.get("strong_on_34_allele_panel", []) or []:
        if b.get("allele") and b["allele"] not in out:
            out.append(b["allele"])
    return out


def mismatch_positions(query, self_peptide):
    if len(query) != len(self_peptide):
        return None
    return [i + 1 for i, (a, b) in enumerate(zip(query, self_peptide)) if a != b]


def collect_hits(selfsim):
    """Every committed near-self hit, with its mismatch positions RECOMPUTED from the peptide strings.

    ⛔ RECOMPUTED, NOT READ. The artifact records `mismatch_positions`; deriving them again from the
    two sequences makes the input's own bookkeeping falsifiable here, and a disagreement is reported
    as a defect rather than propagated.
    """
    rows, disagreements = [], []
    for q in selfsim["queries"]:
        peptide = q["peptide"]
        alleles = restricting_alleles(q)
        for h in q.get("hits", []):
            recomputed = mismatch_positions(peptide, h["self_peptide"])
            recorded = h.get("mismatch_positions")
            if recomputed is not None and recorded is not None and recomputed != list(recorded):
                disagreements.append({"query": peptide, "self_peptide": h["self_peptide"],
                                      "recorded": recorded, "recomputed": recomputed})
            rows.append({
                "query": peptide,
                "length": len(peptide),
                "self_peptide": h["self_peptide"],
                "accession": h.get("accession"),
                "restricting_alleles": alleles,
                "mismatch_positions": recomputed if recomputed is not None else list(recorded or []),
            })
    return rows, disagreements


def rescore(hits, anchor_set_for):
    """Bucket every hit under ONE anchor-set definition.

    `anchor_set_for(allele, length)` returns the anchor positions, or None when that definition has
    nothing to say for the pair. ⚠ THE CONSERVATIVE DIRECTION when a peptide is called on more than
    one allele: a hit is anchor-only if ANY restricting allele makes it anchor-only, and contact-only
    only if EVERY restricting allele makes it contact-only. Taking the union of anchor sets instead
    would hide the adverse case behind the allele with the narrowest one.
    """
    buckets = {"anchor_only": [], "contact_only": [], "mixed": [], "exact_self": [], "unscored": []}
    for h in hits:
        mm = h["mismatch_positions"]
        row = dict(h)
        if not mm:
            buckets["exact_self"].append(row)
            continue
        sets = [anchor_set_for(a, h["length"]) for a in h["restricting_alleles"]]
        sets = [s for s in sets if s is not None]
        if not sets:
            row["_why_unscored"] = "this definition names no anchor set for any restricting allele"
            buckets["unscored"].append(row)
            continue
        row["anchor_sets_applied"] = [sorted(s) for s in sets]
        if any(set(mm) <= s for s in sets):
            buckets["anchor_only"].append(row)
        elif all(not (set(mm) & s) for s in sets):
            buckets["contact_only"].append(row)
        else:
            buckets["mixed"].append(row)
    return buckets


def summarise(buckets):
    return {
        "counts": {k: len(v) for k, v in buckets.items()},
        "binders_with_an_anchor_only_neighbour":
            sorted({r["query"] for r in buckets["anchor_only"]}),
        "n_binders_with_an_anchor_only_neighbour":
            len({r["query"] for r in buckets["anchor_only"]}),
    }


def derive_alleles(selfsim):
    """The alleles this module must answer for, READ OFF the committed artifact.

    ⛔ A HARDCODED ALLELE LIST IS A CLAIM ABOUT ANOTHER FILE, and a list that quietly disagrees with
    the artifact reads as complete while leaving a restriction unexamined -- which is exactly what
    happened on this module's first run.
    """
    found = set()
    for q in selfsim["queries"]:
        found.update(restricting_alleles(q))
    out = []
    for hla in sorted(found):
        short = hla.replace("HLA-", "").replace("*", "").replace(":", "")
        out.append({"hla": hla, "mixmhcpred": short,
                    "syfpeithi": short[0] + "_" + short[1:]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    # ⚠ Both paths default to this module's own directory and are overridable ONLY so the module can
    # be mutation-tested from a scratch copy (charter §7: break the thing the guard protects in a
    # COPY, never in the live tree). Nothing in the repository passes them.
    ap.add_argument("--selfsim", default=SELFSIM)
    args = ap.parse_args()

    with open(args.selfsim, encoding="utf-8") as fh:
        selfsim = json.load(fh)
    alleles = derive_alleles(selfsim)

    bg_text = fetch(MIXMHCPRED_REPO, MIXMHCPRED_COMMIT,
                    "lib/proteome/AA_frequency_human_Methionine.csv")
    bg = read_background(bg_text)
    alleles_list = {r["Allele"]: r for r in read_tsv(
        fetch(MIXMHCPRED_REPO, MIXMHCPRED_COMMIT, "lib/alleles_list.txt"))}

    alphas_by_length = {}
    for L in LENGTHS:
        text = try_fetch(MIXMHCPRED_REPO, MIXMHCPRED_COMMIT, f"lib/pwm/class1_{L}/alphas.txt")
        alphas_by_length[L] = ({r["Allele"]: float(r["ratio"]) for r in read_tsv(text)}
                               if text else {})

    ic_profiles, syf_profiles, missing = [], [], []
    for a in alleles:
        for L in LENGTHS:
            row = alleles_list.get(a["mixmhcpred"])
            n = int(row[str(L)]) if row and row.get(str(L)) else 0
            if n:
                pwms, ws = [], []
                for i in range(n):
                    t = try_fetch(MIXMHCPRED_REPO, MIXMHCPRED_COMMIT,
                                  f"lib/pwm/class1_{L}/PWM_{a['mixmhcpred']}_{i + 1}.csv")
                    if t is None:
                        break
                    pwms.append(read_pwm(t))
                    ws.append(alphas_by_length[L].get(f"{a['mixmhcpred']}_{i + 1}", 1.0))
                if len(pwms) == n:
                    ic_profiles.append(motif_profile(a["hla"], L, bg, n, ws, pwms))
                else:
                    missing.append({"source": "MixMHCpred", "allele": a["hla"], "length": L,
                                    "why": "a PWM file for this allele and length did not fetch"})
            else:
                missing.append({"source": "MixMHCpred", "allele": a["hla"], "length": L,
                                "why": "the library's allele list carries no motif for this pair"})

            name = f"{a['syfpeithi']}_{L}"
            t = try_fetch(EPYTOPE_REPO, EPYTOPE_COMMIT,
                          f"epytope/Data/pssms/syfpeithi/mat/{name}.py")
            if t is None:
                missing.append({"source": "SYFPEITHI/epytope", "allele": a["hla"], "length": L,
                                "why": "no matrix for this allele and length (HTTP 404)"})
            else:
                syf_profiles.append(syfpeithi_profile(a["hla"], L, read_syfpeithi(t, name)))

    ic_by = {(p["allele"], p["length"]): p for p in ic_profiles}

    # ── the known-positive control ───────────────────────────────────────────────────────────
    # ⛔ RUN BEFORE THE VERDICT IS READ. Two facts this repository already holds must fall out of the
    # measurement, and neither was fed in: (1) P2 and the C-terminus are the dominant positions;
    # (2) HLA-A*01:01 reads P3 as a primary anchor. A run that fails either says so here.
    control = []
    for p in ic_profiles:
        if p["length"] != 9:
            continue
        pos = {r["position"]: r for r in p["positions"]}
        cterm = p["length"]
        primary_abs = sorted(r["position"] for r in p["positions"]
                             if r["grade_absolute"] == "PRIMARY")
        top2 = sorted(p["positions"], key=lambda r: -r["information_content_bits"])[:2]
        control.append({
            "allele": p["allele"],
            "length": p["length"],
            "two_strongest_positions": sorted(r["position"] for r in top2),
            "P2_and_C_terminus_are_the_two_strongest":
                sorted(r["position"] for r in top2) == [2, cterm],
            "primary_positions_under_the_absolute_rule": primary_abs,
            "P2_and_C_terminus_are_both_primary_under_the_absolute_rule":
                2 in primary_abs and cterm in primary_abs,
            "A0101_P3_is_primary_under_the_absolute_rule": (
                None if p["allele"] != "HLA-A*01:01"
                else pos[3]["grade_absolute"] == "PRIMARY"),
        })
    # ⛔ THE CONTROL IS REPORTED PER ALLELE, NOT AS ONE BOOLEAN, because it does not pass for all of
    # them and a single flag would either hide that or condemn five good rows for a sixth. An allele
    # whose control fails carries the failure on its own verdict row.
    control_failed = sorted(c["allele"] for c in control
                            if not c["P2_and_C_terminus_are_both_primary_under_the_absolute_rule"]
                            or c["A0101_P3_is_primary_under_the_absolute_rule"] is False)
    control_pass = not control_failed

    # ── the verdict on P1, per allele, under both conventions and both threshold rules ───────
    verdicts = []
    for a in alleles:
        ic_rows = [p for p in ic_profiles if p["allele"] == a["hla"]]
        syf_rows = [p for p in syf_profiles if p["allele"] == a["hla"]]
        ic_p1 = []
        for p in sorted(ic_rows, key=lambda r: r["length"]):
            r = p["positions"][0]
            strongest = max(x["information_content_bits"] for x in p["positions"])
            ic_p1.append({
                "length": p["length"],
                "P1_bits": r["information_content_bits"],
                "P1_bits_atlas_formula": r["atlas_logo_information_content_bits"],
                "strongest_position_bits": round(strongest, 4),
                "fraction_of_strongest_position": r["fraction_of_strongest_position"],
                "rank_of_P1_among_positions": r["rank_by_information_content"],
                "grade_relative": r["grade_relative"],
                "grade_absolute": r["grade_absolute"],
                "grade_absolute_atlas_formula": r["grade_absolute_atlas_formula"],
            })
        syf_p1 = []
        for p in sorted(syf_rows, key=lambda r: r["length"]):
            r = p["positions"][0]
            syf_p1.append({
                "length": p["length"],
                "P1_max_score": r["max_score"],
                "strongest_position_score": p["strongest_position_score"],
                "highest_middle_position_score": p["highest_middle_position_score"],
                "P1_exceeds_the_highest_middle_position": (
                    None if p["highest_middle_position_score"] is None
                    else r["max_score"] > p["highest_middle_position_score"]),
            })
        grades_rel = {r["grade_relative"] for r in ic_p1}
        grades_abs = {r["grade_absolute"] for r in ic_p1}
        if not ic_p1:
            verdict = "NO_MOTIF_SOURCE_FOR_THIS_ALLELE"
        elif "PRIMARY" in grades_rel or "PRIMARY" in grades_abs:
            verdict = "PRIMARY_AT_SOME_LENGTH"
        elif grades_abs == {"NEITHER"} and grades_rel == {"NEITHER"}:
            verdict = "NEITHER_PRIMARY_NOR_SECONDARY_AT_ANY_LENGTH"
        else:
            verdict = "SECONDARY_AT_SOME_LENGTH_NEVER_PRIMARY"
        best_rank = min((r["rank_of_P1_among_positions"] for r in ic_p1), default=None)
        v = {
            "allele": a["hla"],
            "position_1_verdict": verdict,
            "primary_under_either_threshold_rule_at_any_length":
                "PRIMARY" in (grades_rel | grades_abs),
            "best_rank_of_P1_across_lengths": best_rank,
            "n_independent_sources": 1 + (1 if syf_p1 else 0),
            "convention_A_information_content_per_length": ic_p1,
            "convention_B_syfpeithi_per_length": syf_p1 or "NO SYFPEITHI MATRIX FOR THIS ALLELE",
        }
        if a["hla"] in control_failed:
            v["⚠_known_positive_control_failed_for_this_allele"] = (
                "The absolute rule does NOT recover P2 as a primary anchor for this allele, so the "
                "one check that licenses reading this module's grades has failed here. Either the "
                "allele genuinely carries a non-canonical anchor layout or its motif is less well "
                "determined than the others'. Read this row's P1 grade with that, and do not let it "
                "carry a claim on its own.")
        if not syf_p1:
            v["⚠_single_source"] = ("No SYFPEITHI matrix exists for this allele, so this row rests on "
                                    "ONE motif dataset. The other rows rest on two that agree.")
        verdicts.append(v)

    # ── the near-self hits, re-scored under FIVE named anchor-set definitions ────────────────
    # ⛔ NO SINGLE THRESHOLD IS ALLOWED TO DRIVE THIS COUNT SILENTLY. The point of the exercise is
    # that the answer moved with the convention, so every convention that has been used on this
    # question in this repository is scored side by side, including the P1-inclusive one whose count
    # made the question urgent.
    hits, disagreements = collect_hits(selfsim)

    def measured(kind):
        def f(allele, length):
            p = ic_by.get((allele, length))
            if p is None:
                return None
            if kind == "primary":
                return {r["position"] for r in p["positions"] if r["grade_absolute"] == "PRIMARY"}
            return {r["position"] for r in p["positions"]
                    if r["grade_absolute"] in ("PRIMARY", "SECONDARY")}
        return f

    def fixed(positions_from_n, c_offsets):
        def f(allele, length):
            s = {p for p in positions_from_n if 1 <= p <= length}
            s |= {length - o for o in c_offsets if 1 <= length - o <= length}
            return s
        return f

    definitions = [
        ("measured_primary_absolute_rule", measured("primary"),
         "The positions this module measures as PRIMARY for the hit's own restricting allele at the "
         "hit's own peptide length, under the absolute >= 1.0 bit rule the known-positive control "
         "validates. THIS IS THE ANSWER ROW."),
        ("measured_primary_or_secondary_absolute_rule", measured("primary_or_secondary"),
         "The same, widened to include SECONDARY positions (>= 0.5 bits). The most permissive reading "
         "the measurement supports, and an upper bound on the anchor-only count."),
        ("P2_and_C_terminus", fixed([2], [0]),
         "The convention junction-selfsimilarity.json states it used -- the general class I rule."),
        ("P2_P3_and_C_terminus", fixed([2, 3], [0]),
         "That convention widened by the P3 clause the same artifact raises against itself for "
         "HLA-A*01:01, applied to every peptide."),
        ("P1_P2_and_C_terminus", fixed([1, 2], [0]),
         "⛔ THE UNSOURCED VARIANT whose count made this question urgent: 6 hits across 6 binders. It "
         "is scored here so the comparison is visible, NOT because any source supports it -- the "
         "verdicts above are what say whether it is supported."),
    ]
    rescored = {}
    for name, fn, why in definitions:
        b = rescore(hits, fn)
        rescored[name] = {"_definition": why, **summarise(b), "buckets": b}

    out = {
        "_what": ("Whether position 1 is a primary anchor, a secondary (auxiliary) anchor, or "
                  "neither, for every class I allele restricting the predicted EWSR1::NR4A3 junction "
                  "binders -- answered from two fetched allele-specific motif datasets under two "
                  "DECLARED conventions, then applied to the committed near-self hits."),
        "_why": ("junction-selfsimilarity.json's anchor-only null, and the four places the vaccine "
                 "manuscript carries it, are conditional on this question. "
                 "junction-anchor-convention-sensitivity.json located the null on position 1 and "
                 "could not settle it: no allele-specific motif source existed in this repository."),
        "⛔_what_this_is_not": (
            "Not a measurement of what a T-cell receptor can see. Motif information content measures "
            "how selective the MHC groove is for a side chain at a position; whether that side chain "
            "is exposed to a receptor is a structural question this module does not touch, and the "
            "manuscript's use of 'anchor' as a proxy for 'the T cell cannot see it' is NOT validated "
            "here. Not a safety, immunogenicity or presentation result. Every input to the re-scored "
            "hits is a binding prediction plus a sequence-distance search, and sequence distance is "
            "not receptor distance. Not an answer for any allele a source does not carry: those "
            "report MISSING."),
        "_conventions": {
            "A_information_content": {
                "definition": ("Kullback-Leibler divergence, in bits, of each position's amino-acid "
                               "distribution from the human proteome background. ⛔ Reported ALONGSIDE "
                               "the MHC Motif Atlas's own logo stack height, which is a DIFFERENT "
                               "function -- log2(20) + SUM_a p_a log2(p_a) over the "
                               "background-corrected, renormalised distribution, per the Atlas F.A.Q. "
                               "fetched in CI run 33553076455. An earlier draft of this module called "
                               "them the same thing; they are not, they track each other closely on "
                               "this data, and every row carries both plus whether they grade it the "
                               "same way."),
                "source": f"{MIXMHCPRED_REPO} @ {MIXMHCPRED_COMMIT} (MixMHCpred v3 PWM library; "
                          "position probability matrices of naturally presented mass-spectrometry "
                          "eluted ligands, divided by the human proteome background)",
                "source_citation": ("Tadros et al., Predicting MHC-I ligands across alleles and "
                                    "species: How far can we go?, Genome Medicine (2025), "
                                    "doi:10.1186/s13073-025-01450-8 -- the citation the fetched "
                                    "repository's own README asks for"),
                "background": "lib/proteome/AA_frequency_human_Methionine.csv, fetched with the PWMs",
                "multiple_specificity": ("Alleles with more than one motif are MIXED with the "
                                         "library's own weights (alphas.txt), not reduced to motif 1."),
                "grading_rules": {
                    "relative": {"PRIMARY": f">= {PRIMARY_FRACTION} x the allele's strongest position",
                                 "SECONDARY": f">= {SECONDARY_FRACTION} x the strongest position"},
                    "absolute": {"PRIMARY": f">= {PRIMARY_BITS} bits",
                                 "SECONDARY": f">= {SECONDARY_BITS} bits"},
                    "⚠_both_are_conventions": (
                        "Every raw bit value and ratio is in this file so a reader can re-apply their "
                        "own. The absolute rule is the one the known-positive control validates and "
                        "the one the anchor sets are taken from; the relative rule mis-grades "
                        "HLA-A*01:01's P2 because its C-terminal Y is so dominant. The P1 verdict is "
                        "the same under both."),
                },
                "license_note": ("MixMHCpred is free for academic use; for-profit use requires a "
                                 "separate license from the Ludwig Institute for Cancer Research, "
                                 "per the fetched repository's README."),
            },
            "B_syfpeithi_scores": {
                "definition": ("Per-position maximum score in the curated SYFPEITHI matrix for the "
                               "allele and length. ⛔ Used ORDINALLY only: this file makes no claim "
                               "about what SYFPEITHI's score tiers are named. The comparison is P1's "
                               "best score against the strongest position's, and against the highest "
                               "of the middle positions P4..P(Omega-1), which every convention agrees "
                               "are not anchors."),
                "source": f"{EPYTOPE_REPO} @ {EPYTOPE_COMMIT} "
                          "(epytope/Data/pssms/syfpeithi/mat, SYFPEITHI matrices as redistributed)",
            },
            "general_class_I_statement_this_is_tested_against": (
                "'Primary anchor residues are mainly found at the second and last positions of these "
                "peptides' -- The MHC Motif Atlas, Nucleic Acids Research 2023, "
                "doi:10.1093/nar/gkac965 (PMC9825574). A general class I statement, not an allele-specific one, "
                "and the statement junction-selfsimilarity.json's convention encodes."),
        },
        "_provenance": {
            "pinned_commits": {MIXMHCPRED_REPO: MIXMHCPRED_COMMIT, EPYTOPE_REPO: EPYTOPE_COMMIT},
            "⚠_every_404_is_a_real_absence": ("A 404 here means the source carries no matrix for that "
                                              "allele and length. It is recorded in "
                                              "`missing_source_rows` and never filled in by a guess."),
            "n_fetches": len(_FETCHES),
            "n_fetch_errors": sum(1 for f in _FETCHES if "error" in f),
            "fetches": _FETCHES,
        },
        "_cost": "$0 -- public raw.githubusercontent reads and pure-stdlib arithmetic.",
        "alleles_answered_for": [a["hla"] for a in alleles],
        "⚠_allele_list_is_derived_not_typed": (
            "Read off junction-selfsimilarity.json's own restricting alleles (predicted_binders and "
            "strong_on_34_allele_panel). The five-allele list this module was first written with was "
            "SHORT ONE: HLA-A*30:02 calls the lead peptide NMPCVQAQY on the 34-allele panel. ⛔ Those "
            "five are emc-vaccine-development-path.md §B3 line 675's own list -- in a manuscript that "
            "names HLA-A*30:02 in its abstract as that same peptide's second presenting allele -- so "
            "the omission is in the paragraph that asks the question, not in this module."),
        "_headline": {
            "question": ("Is position 1 a primary or a secondary anchor for the alleles restricting "
                         "the predicted EWSR1::NR4A3 junction binders?"),
            "answer_primary": ("NO for every allele, under both threshold rules, both motif sources "
                               "and every peptide length either source carries. Position 1 is never "
                               "among the two most informative positions except in HLA-A*30:02, and "
                               "is never primary anywhere."),
            "answer_secondary": ("MIXED, and allele-dependent -- this is the half that does not "
                                 "reduce to one word. See position_1_verdicts."),
            "n_alleles_where_P1_is_primary": sum(
                1 for v in verdicts if v["primary_under_either_threshold_rule_at_any_length"]),
            "n_alleles_answered": len(verdicts),
            "n_positions_where_the_two_information_measures_disagree": sum(
                1 for p in ic_profiles for r in p["positions"]
                if not r["the_two_information_measures_agree"]),
            "n_positions_graded": sum(len(p["positions"]) for p in ic_profiles),
            "consequence_for_the_anchor_only_null": (
                "Under the anchor sets this module MEASURES (primary positions, absolute rule) the "
                "anchor-only count is 0 hits across 0 of the 11 binders -- identical to the committed "
                "{P2, C-terminus} convention. Widening to include secondary positions gives 2 hits "
                "across 2 binders, NOT the 6 the unsourced P1-inclusive variant gives. Read the "
                "counts in near_self_hits_rescored rather than this sentence."),
            "⛔_what_still_is_not_settled": (
                "Whether 'not an anchor' implies 'a T-cell receptor can read it'. That inference is "
                "the manuscript's, it is structural, and nothing here tests it."),
        },
        "known_positive_control": {
            "_what": ("Two facts this repository already holds, neither fed in, both predictions this "
                      "measurement could have failed: (1) P2 and the C-terminus are primary anchors; "
                      "(2) HLA-A*01:01 reads P3 as a primary anchor."),
            "passes_for_every_allele": control_pass,
            "alleles_where_the_control_FAILED": control_failed,
            "⚠_a_failed_row_is_not_smoothed": (
                "A failing allele keeps its measured numbers and carries the failure on its own "
                "verdict row. The threshold was not moved to make the control pass -- moving a bar "
                "because it failed is the one edit this repository refuses."),
            "rows": control,
        },
        "position_1_verdicts": verdicts,
        "motif_information_content_profiles": ic_profiles,
        "syfpeithi_score_profiles": syf_profiles,
        "missing_source_rows": missing,
        "near_self_hits_rescored": {
            "_method": ("Every hit in junction-selfsimilarity.json bucketed under each anchor-set "
                        "definition below. Mismatch positions recomputed from the peptide strings; "
                        "disagreements with the artifact's recorded field are listed, not smoothed."),
            "recomputed_vs_recorded_mismatch_disagreements": disagreements,
            "n_hits": len(hits),
            "by_definition": rescored,
        },
        "open_question_this_does_not_answer": (
            "Whether a position with near-background motif information content is a position a T-cell "
            "receptor can read. Low groove selectivity and receptor accessibility are different "
            "properties, and the manuscript's ranking rests on the second. Settling it needs "
            "per-position solvent accessibility over class I pMHC crystal structures."),
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    print(f"wrote {args.out}")
    print(f"alleles: {[a['hla'] for a in alleles]}")
    print(f"fetches: {len(_FETCHES)} ({out['_provenance']['n_fetch_errors']} 404/errors)")
    print(f"known-positive control passes for every allele: {control_pass}"
          f"{'  FAILED: ' + ', '.join(control_failed) if control_failed else ''}")
    for c in control:
        print(f"  {c['allele']} L9 primary={c['primary_positions_under_the_absolute_rule']} "
              f"P2+Cterm_primary={c['P2_and_C_terminus_are_both_primary_under_the_absolute_rule']} "
              f"A0101_P3_primary={c['A0101_P3_is_primary_under_the_absolute_rule']}")
    for v in verdicts:
        print(f"  {v['allele']}: {v['position_1_verdict']}")
    for name, block in rescored.items():
        print(f"  {name:<45} anchor_only={block['counts']['anchor_only']:<2} "
              f"binders={block['n_binders_with_an_anchor_only_neighbour']} "
              f"contact_only={block['counts']['contact_only']} mixed={block['counts']['mixed']} "
              f"unscored={block['counts']['unscored']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
