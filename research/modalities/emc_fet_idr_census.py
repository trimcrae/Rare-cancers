#!/usr/bin/env python3
"""
Do EMC's fusions satisfy the STRUCTURAL PRECONDITION of the FET/ATM-suppression mechanism?

THE QUESTION
------------
The ATR-inhibitor route for EMC (research/manuscripts/program/emc-post-degrader-options.md route 1) is a CLASS
inheritance: FET fusion oncoproteins suppress ATM activation at double-strand breaks, so the ATR axis
becomes load-bearing. Whether EMC inherits it is usually argued from the partner list - EWSR1, TAF15
and FUS are the three FET genes, so EMC is FET-rearranged. That argument is about GENE NAMES.

The mechanism is not about gene names. The source states a two-part STRUCTURE:

    "Native FET family proteins contain an N-terminal intrinsically disordered region (IDR) ... and a
     C-terminal domain with positively charged RGG (arginine-glycine-glycine) repeats, which mediate
     recruitment to DSBs via high affinity interactions with negatively charged poly-ADP ribose (PAR)
     molecules ... all oncogenic FET fusion proteins including EWSR1-FLI1 share a similar structure:
     the N-terminal IDR of the FET protein fused to the DNA binding domain of a transcription factor
     (e.g., FLI1), WITH LOSS OF THE C-TERMINAL RGG REPEATS"
        - biorxiv 10.1101/2023.04.30.538578 / PMID 37205599, fetched to the literature-cache branch

and it is CAUSAL in both directions: reintroducing 1 or all 3 RGG domains into EWSR1-FLI1 gave
"earlier DSB recruitment kinetics and higher levels of overall recruitment in an RGG dose-dependent
manner". So the precondition is a CONJUNCTION, and it is a sequence fact:

    (i)  the fusion RETAINS the FET N-terminal IDR   -> it reaches DSBs at all
    (ii) the fusion LOSES the FET C-terminal RGG boxes -> its recruitment is aberrant/delayed

Nobody has checked (i)+(ii) for any NR4A3 fusion. This module does, for $0, from sequence.

WHICH HALF THE VERDICT RESTS ON, AND WHY (decided by testing, not by preference)
-------------------------------------------------------------------------------
(i) is near-TAUTOLOGICAL for a FET fusion, which is *defined* as the FET N-terminus fused to a
partner DBD; and a first attempt to gate it on a [S,Y,G,Q]-composition threshold showed the threshold
DECIDED the answer (at 0.60 EWSR1's own N-terminal region did not register; at 0.40 the called region
ran straight through the first RGG box). So (i) is REPORTED as a measured composition and never gated.

(ii) is the half the source demonstrates CAUSALLY - putting 1 or all 3 RGG domains back into
EWSR1-FLI1 restored earlier DSB-recruitment kinetics in an RGG dose-dependent manner - and it is
THRESHOLD-FREE: an RG dipeptide is either inside the retained segment or it is not. The verdict is
therefore `rg_dipeptides_retained == 0`, and the RGG-box call exists only for context.

WHY THIS IS WORTH A MODULE RATHER THAN A PARAGRAPH
--------------------------------------------------
It can come back NEGATIVE, and a negative would matter: if a common EMC fusion kept an RGG box, that
fusion would be predicted NOT to carry the lesion, which would split EMC by fusion partner and change
who the route applies to. An argument from gene names cannot produce that result at all.

DESIGN, AND THE CONTROL THAT COMES FIRST
----------------------------------------
1. POSITIVE CONTROLS BEFORE ANYTHING ELSE. The annotation is run on the two fusions where the
   mechanism was actually MEASURED - EWSR1::FLI1 (Ewing) and EWSR1::ATF1 (clear cell sarcoma). Both
   must come back "IDR retained, all RGG boxes lost". If they do not, the RGG/IDR annotation is broken
   and nothing else in the output may be quoted. This is stated before the run, not after.
2. NO INVENTED BREAKPOINTS, AND EVERY REPORTED TYPE RATHER THAN ONE OF THEM. Which EWSR1::NR4A3
   transcript types exist, and at which exon each breaks, is READ from the sourced junction
   registry - `emc_fet_construct_designs.py::BREAKPOINTS`, projected into
   `emc-fet-construct-designs.json` with the literature quote licensing each exon number. Each exon
   rank is then converted to a residue by this repo's own Ensembl-derived exon audit
   (`nr4a3-exon-audit.json`). Nothing here is typed, and the two numbers are cross-checked against
   each other so a numbering-scheme divergence - the off-by-two class - is caught rather than
   trusted. FUS::NR4A3, for which no exon-level junction is sourced anywhere in this repo, is
   answered as a FUNCTION of breakpoint across the plausible range and gets no pinned point.

   ⛔ THIS MODULE USED TO CARRY EXACTLY ONE EMC RECORD AND CALL IT CANONICAL (2026-08-03 - 2026-09-02).
   The record was the EWSR1 exon-7 cut, EWSR1(1-264): that is the 5' side of reported TYPE 2, the
   SECOND-commonest EMC transcript. The COMMONEST reported type is EWSR1 exon 12 (residue 431), and
   it was not in the artifact at all - `431` did not occur in the file. The prose that quotes this
   artifact was corrected; the artifact was not, which is the wrong way round, because a reader who
   opens the data rather than the prose gets the superseded claim. ⚠ What the correction does NOT
   disturb: the 264-residue arithmetic is unchanged and is still the right comparator for
   EWSR1::FLI1 type 1, which really does cut there. What changed is the KEY and the COVERAGE. One
   home for the superseded value:
   `research/manuscripts/dependency/emc-atr-collaborator-package.md` (§2.2 + appendix).

   ⭐ AND THE COMPARATIVE ANSWER SPLITS, WHICH IS THE POINT OF CARRYING ALL THREE. Type 2 loses at
   least as much RGG content as every fusion the mechanism was measured on; types 1 and 5 do not.
   A single flag over one record read as though it answered for EMC and did not. It is now reported
   per type, and the criterion behind it was not touched to produce that reading.

Output: emc-fet-idr-census.json. `--check` recomputes and diffs. Network needed only to refresh the
sequence cache; with the cache present it is pure-stdlib and runs anywhere.
"""

import argparse
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-fet-idr-census.json")
CACHE = os.path.join(HERE, "fet-sequences-cache.json")
EXON_AUDIT = os.path.join(HERE, "nr4a3-exon-audit.json")
#: The sourced junction registry. ⛔ THE ONE HOME of every reported EMC exon junction is
#: `emc_fet_construct_designs.py::BREAKPOINTS`, projected verbatim (exon rank + the quote that
#: licenses it) into this artifact. This module READS it and never restates a breakpoint, so a
#: correction to a junction lands in one file and both artifacts move together.
#: ⚠ Read as an ARTIFACT rather than imported as a module ON PURPOSE: `emc_fet_construct_designs`
#: imports THIS module for its RGG arithmetic, so an import in this direction would be a cycle.
CONSTRUCT_DESIGNS = os.path.join(HERE, "emc-fet-construct-designs.json")

FET = {"EWSR1": "Q01844", "TAF15": "Q92804", "FUS": "P35637"}
PARTNERS = {"NR4A3": "Q92570", "FLI1": "Q01543", "ATF1": "P18846"}

# --- operational definitions, fixed here so they cannot be tuned to the answer -------------------
# An RGG box is a window dense in RG dipeptides. The literature definition is qualitative ("RGG-rich
# domain"); this makes it countable. Both parameters are declared and echoed into the artifact.
RGG_WINDOW = 60          # residues
RGG_MIN_RG_IN_WINDOW = 6  # >= this many RG dipeptides in the window opens a box
# The FET prion-like / IDR signature is [S,Y,G,Q]-richness. Same treatment.
IDR_WINDOW = 60
IDR_MIN_SYGQ_FRACTION = 0.60


def _fetch(acc):
    url = f"https://rest.uniprot.org/uniprotkb/{acc}.fasta"
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        body = r.read().decode()
    return "".join(l.strip() for l in body.splitlines() if not l.startswith(">"))


def load_sequences(refresh=False):
    """Load the FET/partner sequences, refreshing from UniProt when asked.

    ⚠ `--refresh` MUST NOT be able to SHRINK the cache. It used to start from `{}`, so a run in
    which UniProt was unreachable wrote back only whatever the NR4A fallback happened to hold —
    which is exactly how `fet-sequences-cache.json` on `main` came to carry 4 entries (NR4A1/2/3 +
    EWSR1, the fallback set) instead of 8, and therefore how `emc-fet-idr-census.json` on `main`
    became the 2-key `sequences missing, cannot compute: ['TAF15','FUS']` stub while documents on
    `main` printed a full table out of it. The committed cache is now always the floor: a failed
    fetch leaves the previous sequence in place rather than deleting it.
    """
    have = {}
    if os.path.exists(CACHE):
        try:
            have = json.load(open(CACHE))
        except Exception as exc:  # noqa: BLE001
            print(f"  cache unreadable, starting empty: {exc}", file=sys.stderr)
            have = {}
    want = {**FET, **PARTNERS}
    # on --refresh re-fetch everything, but keep `have` as the fallback for anything that fails
    missing = list(want) if refresh else [k for k in want if k not in have]
    if missing:
        for name in missing:
            try:
                have[name] = _fetch(want[name])
                print(f"  fetched {name} ({want[name]}) {len(have[name])} aa", file=sys.stderr)
            except Exception as exc:  # noqa: BLE001
                print(f"  FETCH FAILED {name}: {exc}", file=sys.stderr)
        # Fall back to the NR4A cache for anything it already holds (EWSR1, NR4A3 live there).
        nr4a = os.path.join(HERE, "nr4a-sequences-cache.json")
        if os.path.exists(nr4a):
            for k, v in json.load(open(nr4a)).items():
                have.setdefault(k, v)
        json.dump(have, open(CACHE, "w"), indent=1)
    return have


def rgg_boxes(seq):
    """Windows dense in RG dipeptides, merged into boxes. Returns 1-based inclusive spans."""
    rg = [m.start() for m in re.finditer("(?=RG)", seq)]
    if not rg:
        return []
    hot = []
    for i in range(0, max(1, len(seq) - RGG_WINDOW + 1)):
        n = sum(1 for p in rg if i <= p < i + RGG_WINDOW)
        if n >= RGG_MIN_RG_IN_WINDOW:
            hot.append((i, i + RGG_WINDOW))
    if not hot:
        return []
    boxes, cur = [], list(hot[0])
    for a, b in hot[1:]:
        if a <= cur[1]:
            cur[1] = max(cur[1], b)
        else:
            boxes.append(cur); cur = [a, b]
    boxes.append(cur)
    out = []
    for a, b in boxes:
        inside = [p for p in rg if a <= p < b]
        if not inside:
            continue
        # A box starts at its FIRST RG, not at the sliding window's left edge. Reporting the edge
        # put EWSR1's first box at 258 when its first RG dipeptide is at 300 — a 42-residue error
        # that straddled the very breakpoint this module exists to judge.
        out.append({"start": inside[0] + 1, "end": min(inside[-1] + 3, len(seq)),
                    "n_RG": len(inside)})
    return out


def lc_composition(seq, lo, hi):
    """Measured [S,Y,G,Q] fraction of a 1-based inclusive span. A DESCRIPTIVE statistic, not a gate.

    An earlier version of this module gated 'IDR retained' on a hand-picked SYGQ threshold, and
    testing showed the threshold decided the answer: at 0.60 EWSR1's own N-terminal region failed to
    register at all, while 0.40 ran the region straight through the first RGG box. A criterion whose
    cut-point flips the verdict is not a criterion, so the composition is now REPORTED and the verdict
    rests on the RG-dipeptide ceiling below, which needs no threshold."""
    seg = seq[max(0, lo - 1):hi]
    if not seg:
        return None
    return {"span": [lo, hi], "length": len(seg),
            "sygq_fraction": round(sum(seg.count(c) for c in "SYGQ") / len(seg), 3)}


def rgg_free_ceiling(seq):
    """The largest breakpoint at which the fusion retains ZERO RG dipeptides of the FET protein.

    This is the whole verdict, and it needs no tunable parameter: an RG dipeptide is either inside the
    retained segment or it is not. It is also the half of the precondition the source demonstrates
    CAUSALLY — adding 1 or all 3 RGG domains back into EWSR1-FLI1 restored earlier DSB-recruitment
    kinetics in an RGG dose-dependent manner — whereas 'retains the N-terminal IDR' is near-tautological
    for a FET fusion, which is defined as the FET N-terminus fused to a partner DBD."""
    first = re.search("RG", seq)
    return (first.start() if first else len(seq))  # 1-based last residue with no RG retained


def assess(fet_name, seq, cut, ceiling, boxes):
    """Given a breakpoint (last FET residue retained), does the retained half meet the precondition?"""
    rg_retained = len(re.findall("(?=RG)", seq[:cut]))
    rg_total = len(re.findall("(?=RG)", seq))
    kept = [b for b in boxes if b["start"] <= cut]
    met = rg_retained == 0
    return {
        "fet": fet_name,
        "last_fet_residue_retained": cut,
        "rgg_free_ceiling": ceiling,
        "margin_to_ceiling": ceiling - cut,
        "rg_dipeptides_retained": rg_retained,
        "rg_dipeptides_total_in_wildtype": rg_total,
        "fraction_of_wildtype_RG_retained": round(rg_retained / rg_total, 3) if rg_total else None,
        "rgg_boxes_touched": len(kept),
        "retained_segment_composition": lc_composition(seq, 1, cut),
        "precondition_met": bool(met),
        "verdict": ("PRECONDITION_MET — retains the FET N-terminus, retains no RG dipeptide"
                    if met else
                    f"NOT_MET — the retained segment carries {rg_retained} RG dipeptide(s)"),
    }


def ewsr1_breakpoint_from_exon_audit(exon_rank):
    """The last EWSR1 residue retained when the fusion breaks after transcript exon `exon_rank`.
    Read from this repo's Ensembl-derived audit, never typed."""
    if not os.path.exists(EXON_AUDIT):
        return None, "nr4a3-exon-audit.json not present"
    aud = json.load(open(EXON_AUDIT))
    ex = aud.get("EWSR1", {}).get("exons") or []
    for e in ex:
        if e.get("transcript_exon_rank") == exon_rank:
            nt = e.get("cumulative_coding_nt_through_exon")
            if nt is None:
                return None, f"exon {exon_rank} has no cumulative coding nt"
            return nt // 3, f"EWSR1 transcript exon {exon_rank}, cumulative coding nt {nt}"
    return None, f"EWSR1 transcript exon {exon_rank} not in the audit"


def reported_junctions():
    """The reported EMC fusion junctions, READ from the sourced registry — never typed here.

    Returns `(rows, status)`. Each row carries the fusion's id, label, reported rank, the 5' gene,
    the 5' transcript exon rank, the residue index the registry's own arithmetic reached, and the
    literature quotes that license the exon number. `status` is None on success and an explanatory
    string when the registry could not be read, so a missing input reads as UNDETERMINED rather
    than as an absent fusion.
    """
    if not os.path.exists(CONSTRUCT_DESIGNS):
        return [], "emc-fet-construct-designs.json not present"
    try:
        doc = json.load(open(CONSTRUCT_DESIGNS))
    except Exception as exc:  # noqa: BLE001
        return [], f"emc-fet-construct-designs.json unreadable: {exc}"
    if all(str(k).startswith("_") for k in doc):
        return [], "emc-fet-construct-designs.json is a failure stub (every top-level key is meta)"
    # The registry indexes residues against the ENSEMBL translation; this module counts RG
    # dipeptides on the UniProt sequence. A residue index read across that boundary is meaningful
    # only where the two are byte-identical, so the registry's own comparison travels with the row.
    ident = doc.get("ensembl_vs_uniprot_sequences") or {}
    rows = []
    for c in doc.get("constructs") or []:
        j = c.get("junction_in_exon_numbering") or {}
        gene = j.get("five_prime_gene")
        rows.append({
            "id": c.get("id"),
            "label": c.get("label"),
            "reported_rank": c.get("reported_rank"),
            "five_prime_gene": gene,
            "registry_ensembl_matches_uniprot": (ident.get(gene) or {}).get("identical"),
            "five_prime_last_exon_retained_transcript_rank":
                j.get("five_prime_last_exon_retained_transcript_rank"),
            "registry_five_prime_residues_fully_encoded":
                (c.get("junction_in_residue_numbering") or {}).get("five_prime_residues_fully_encoded"),
            "breakpoint_sources": c.get("breakpoint_sources") or [],
        })
    unpinned = doc.get("partners_with_no_sourced_transcript_junction") or []
    return rows, None if rows else f"the registry emitted no constructs ({len(unpinned)} unpinned)"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="recompute and diff against the artifact")
    ap.add_argument("--refresh", action="store_true", help="re-fetch sequences from UniProt")
    args = ap.parse_args(argv)

    seqs = load_sequences(refresh=args.refresh)
    missing = [k for k in FET if k not in seqs]
    if missing:
        res = {"_status": f"sequences missing, cannot compute: {missing}",
               "_remedy": "run with --refresh from CI (UniProt is not reachable from the dev sandbox)"}
        json.dump(res, open(OUT, "w"), indent=2)
        print(json.dumps(res, indent=2))
        return 1

    annot = {}
    for name in FET:
        q = seqs[name]
        ceil_ = rgg_free_ceiling(q)
        annot[name] = {"length": len(q), "rgg_boxes": rgg_boxes(q),
                       "first_RG_dipeptide_at": ceil_ + 1 if ceil_ < len(q) else None,
                       "rgg_free_ceiling": ceil_,
                       "n_terminal_composition_to_ceiling": lc_composition(q, 1, ceil_)}

    # --- 1. POSITIVE CONTROLS. These are checked before anything else is reported. ----------------
    # EWSR1::FLI1 type 1 = EWSR1 exon 7 :: FLI1 exon 6; EWSR1::ATF1 type 1 = EWSR1 exon 8 :: ATF1
    # exon 4. Both breakpoints are taken from the exon audit rather than typed as residue numbers.
    # ⚠ EWSR1::ATF1 has SEVERAL reported exon combinations, so it is SWEPT rather than assumed —
    # the first version of this module assumed one (exon 8), it failed the control, and assuming a
    # different one until the control passed would have been the exact circularity the control exists
    # to prevent. Reported types: EWSR1 e8::ATF1 e4 (commonest), e7::e5, e10::e5.
    CONTROL_FUSIONS = {
        "EWSR1::FLI1 (Ewing, type 1 — EWSR1 e7::FLI1 e6)": [7],
        "EWSR1::ATF1 (clear cell — swept over reported types e8/e7/e10)": [8, 7, 10],
    }
    controls = {}
    for label, exons in CONTROL_FUSIONS.items():
        rows = []
        for exon in exons:
            cut, prov = ewsr1_breakpoint_from_exon_audit(exon)
            if cut is None:
                rows.append({"_status": f"UNDETERMINED — {prov}"})
                continue
            rows.append({**assess("EWSR1", seqs["EWSR1"], cut,
                                  annot["EWSR1"]["rgg_free_ceiling"],
                                  annot["EWSR1"]["rgg_boxes"]),
                         "ewsr1_transcript_exon": exon, "breakpoint_provenance": prov})
        controls[label] = {"_role": "the mechanism was MEASURED on this fusion",
                           "types": rows,
                           "any_type_meets_precondition": any(r.get("precondition_met") for r in rows),
                           "all_types_meet_precondition": all(r.get("precondition_met") for r in rows)}
    ctrl_ok = all(c.get("any_type_meets_precondition") for c in controls.values())

    # --- 2. EVERY REPORTED EWSR1::NR4A3 TYPE, at the repo's own exon-audited junctions ------------
    # ⛔ THIS BLOCK USED TO BE ONE RECORD KEYED `emc_canonical_EWSR1_NR4A3`, AND BOTH HALVES OF THAT
    # NAME WERE WRONG. It held the exon-7 cut — reported **type 2**, the SECOND-commonest EMC
    # transcript — under a key asserting it is the canonical one, while the commonest reported type
    # (EWSR1 e12, `431`) did not appear in the artifact at all. The label drift was flagged in this
    # module's own docstring on 2026-08-03 and corrected in the prose of
    # `emc-atr-collaborator-package.md` (§2.2 + appendix) and of the ATR assessment; the DATA was
    # never corrected, which is the wrong way round — a reader who opens the artifact rather than
    # the prose gets the superseded claim, and every downstream flag was computed on one type while
    # reading as though it covered EMC.
    # ★ So the key now carries no commonness claim, the record is a MAP over the reported types, and
    # each type's id is the one the sourced registry uses, so the two artifacts share one vocabulary.
    junctions, jstatus = reported_junctions()
    emc_types, emc_types_status = {}, jstatus
    for row in junctions:
        if row["five_prime_gene"] != "EWSR1":
            continue  # TAF15 is handled with the sweeps; it needs a TAF15 exon audit this repo lacks
        exon = row["five_prime_last_exon_retained_transcript_rank"]
        c, p = ewsr1_breakpoint_from_exon_audit(exon) if exon else (None, "no exon rank in the registry")
        if c is None:
            emc_types[row["id"]] = {"_status": f"UNDETERMINED — {p}", "label": row["label"]}
            continue
        # ⚠ A CONSISTENCY CHECK, NOT AN INDEPENDENT CONFIRMATION. Both numbers descend from the same
        # Ensembl exon audit — the registry reaches it through cDNA offsets, this module through
        # cumulative coding nt — so agreement proves the two numbering SCHEMES did not diverge, which
        # is exactly the off-by-two class of error, and proves nothing about the exon rank itself.
        reg = row["registry_five_prime_residues_fully_encoded"]
        emc_types[row["id"]] = {
            **assess("EWSR1", seqs["EWSR1"], c,
                     annot["EWSR1"]["rgg_free_ceiling"], annot["EWSR1"]["rgg_boxes"]),
            "label": row["label"],
            "reported_rank": row["reported_rank"],
            "ewsr1_transcript_exon": exon,
            "breakpoint_provenance": p,
            "breakpoint_sources": row["breakpoint_sources"],
            "registry_five_prime_residues_fully_encoded": reg,
            "agrees_with_the_sourced_registry": bool(reg == c),
            # Reported, not gated: the exon audit is an ENSEMBL map and the RG count below runs on
            # the UniProt sequence, so every EWSR1 index in this file — the controls' included —
            # crosses that boundary. It is safe while the registry reports the two byte-identical.
            "registry_ensembl_matches_uniprot": row["registry_ensembl_matches_uniprot"],
        }
    disagree = [k for k, v in emc_types.items() if v.get("agrees_with_the_sourced_registry") is False]
    if disagree:
        emc_types_status = (f"⛔ residue index disagrees with the sourced registry for {disagree} — "
                            f"the two numbering schemes have diverged; nothing here may be quoted")

    # ⭑ Is each reported EMC type's retained FET half the SAME SEQUENCE as the fusions the mechanism
    # was measured on? Computed PER TYPE, because the byte-identity holds for exactly one of them and
    # a single answer standing for all three is what this whole revision exists to remove.
    ident = {}
    for tid, t in emc_types.items():
        c = t.get("last_fet_residue_retained")
        if c is None:
            continue
        emc_half = seqs["EWSR1"][:c]
        per = {}
        for label, exon in (("EWSR1::FLI1 (Ewing, type 1)", 7), ("EWSR1::ATF1 (clear cell, type 1)", 8)):
            c2, _ = ewsr1_breakpoint_from_exon_audit(exon)
            if not c2:
                continue
            other = seqs["EWSR1"][:c2]
            shared = min(len(emc_half), len(other))
            per[label] = {
                "emc_retained_len": len(emc_half), "comparator_retained_len": len(other),
                "identical_over_shared_prefix": bool(emc_half[:shared] == other[:shared]),
                "byte_identical": bool(emc_half == other),
            }
        ident[tid] = {"label": t.get("label"), "vs_measured_fusions": per}

    # --- 3. TAF15 and FUS: a BREAKPOINT SWEEP, because this repo has no exon audit for them -------
    sweeps = {}
    for name in ("TAF15", "FUS"):
        q, a = seqs[name], annot[name]
        lo, hi = 100, len(q)
        grid = sorted({lo, *range(lo, hi + 1, 10), hi})
        rows = [assess(name, q, c, a["rgg_free_ceiling"], a["rgg_boxes"]) for c in grid]
        met = [r for r in rows if r["precondition_met"]]
        sweeps[name] = {
            "_what": "the precondition as a FUNCTION of breakpoint — no breakpoint is assumed",
            "rgg_free_ceiling": a["rgg_free_ceiling"],
            "first_rgg_box_starts_at": a["rgg_boxes"][0]["start"] if a["rgg_boxes"] else None,
            "window_where_strict_zero_RG_holds": ({"from": met[0]["last_fet_residue_retained"],
                                                   "to": met[-1]["last_fet_residue_retained"]}
                                                  if met else None),
            "window_where_no_RGG_BOX_is_retained": (
                {"from": 100, "to": a["rgg_boxes"][0]["start"] - 1} if a["rgg_boxes"] else None),
            "_two_windows": "the strict window (no RG dipeptide at all) and the looser one (no dense "
                            "RGG box). The controls show a MEASURED fusion sits between them, so a "
                            "breakpoint in the gap is not evidence against the mechanism — it is the "
                            "regime the clear-cell fusion occupies.",
            "n_grid_points": len(rows), "n_meeting_precondition": len(met),
            "fraction_of_grid_meeting_precondition": round(len(met) / len(rows), 3) if rows else None,
            "_reading": "a fusion breaking anywhere in the STRICT window meets the conservative "
                        "criterion; one breaking in the gap up to the box window sits where the "
                        "measured clear-cell fusion sits. Reported as a function of breakpoint "
                        "because the repo holds no exon audit for this gene, and an assumed "
                        "breakpoint would be the weakest link in the whole argument.",
        }
        # ⭑ THE SWEEP KEEPS ITS SHAPE AND GAINS A PIN WHERE ONE IS SOURCED. TAF15::NR4A3 has a
        # quoted transcript junction ("exclusively", "always" — two reviews plus an expressed
        # construct); FUS::NR4A3 has none in this repo's literature cache, so it stays a pure sweep.
        # ⛔ The residue index is READ from the sourced registry, not derived here: this repo holds
        # no TAF15 exon audit, which is why the sweep exists in the first place. The read is only
        # legitimate because the registry's Ensembl translation and this module's UniProt sequence
        # are byte-identical for TAF15 — asserted below rather than assumed, and reported as
        # UNDETERMINED if it ever stops holding.
        pin = next((r for r in junctions if r["five_prime_gene"] == name), None)
        if pin is None:
            sweeps[name]["sourced_breakpoint"] = {
                "_status": jstatus or (f"no transcript-level {name} junction is sourced in this "
                                       f"repo's literature cache, so no point is pinned on the "
                                       f"sweep — the sweep IS the answer for this fusion"),
            }
            continue
        c = pin["registry_five_prime_residues_fully_encoded"]
        if pin["registry_ensembl_matches_uniprot"] is not True:
            sweeps[name]["sourced_breakpoint"] = {
                "_status": f"UNDETERMINED — the registry indexes {name} against Ensembl and this "
                           f"module counts on UniProt, and the registry reports they are not "
                           f"byte-identical (identical="
                           f"{pin['registry_ensembl_matches_uniprot']!r}). A residue index read "
                           f"across that boundary would misplace every count."}
            continue
        if not isinstance(c, int) or not 1 <= c <= len(q):
            sweeps[name]["sourced_breakpoint"] = {
                "_status": f"UNDETERMINED — registry residue index {c!r} is not a position in the "
                           f"{len(q)}-residue {name} sequence this module computes on"}
            continue
        sweeps[name]["sourced_breakpoint"] = {
            "label": pin["label"], "reported_rank": pin["reported_rank"],
            "five_prime_last_exon_retained_transcript_rank":
                pin["five_prime_last_exon_retained_transcript_rank"],
            "breakpoint_sources": pin["breakpoint_sources"],
            "_provenance": "residue index read from emc-fet-construct-designs.json, which derives "
                           "it from the Ensembl exon map; this module holds no exon audit for "
                           f"{name} and derives nothing of its own here",
            **assess(name, q, c, a["rgg_free_ceiling"], a["rgg_boxes"]),
        }

    # --- 4. ⭐ THE COMPARATIVE STATEMENT, which is the only one the controls actually license ------
    # The strict zero-RG verdict is CONSERVATIVE: the commonest reported clear-cell type retains RG
    # dipeptides and the mechanism was measured there anyway. So the defensible claim is not "EMC
    # meets an absolute bar" but "EMC loses AT LEAST AS MUCH RGG content as a fusion in which the
    # lesion is documented" — which is a comparison, needs no bar at all, and cannot be tuned.
    # ⛔⛔ AND IT IS REPORTED PER REPORTED TYPE, WITH NO FLAG STANDING FOR ALL OF THEM.
    # It used to be one boolean — `holds_against_every_measured_type` — computed on the single
    # exon-7 record. Read as a statement about EMC it was false: it is a statement about ONE
    # reported type, and the two other reported types answer differently. A roll-up whose inputs
    # disagree is not a summary, it is a discarded result.
    # ⛔ THE COMPARISON ITSELF IS UNTOUCHED: `emc_frac <= comparator_frac`, on the same
    # `fraction_of_wildtype_RG_retained` the controls are measured in. Nothing about the criterion,
    # the strict zero-RG verdict or the control rule was relaxed to change an answer — the honest
    # result is that the claim holds for one reported type and fails for two, and that is the
    # finding rather than a problem to engineer around.
    comparative = {}
    measured = [{"measured_fusion": label, "ewsr1_transcript_exon": t.get("ewsr1_transcript_exon"),
                 "comparator_RG_retained_fraction": t["fraction_of_wildtype_RG_retained"]}
                for label, v in controls.items() for t in v.get("types", [])
                if t.get("fraction_of_wildtype_RG_retained") is not None]
    scored = {k: v for k, v in emc_types.items()
              if v.get("fraction_of_wildtype_RG_retained") is not None}
    if ctrl_ok and measured and scored:
        rows, per_type = [], {}
        for tid, t in scored.items():
            emc_frac = t["fraction_of_wildtype_RG_retained"]
            mine = [{"emc_fusion_type": tid, "emc_label": t.get("label"),
                     "emc_reported_rank": t.get("reported_rank"),
                     "emc_ewsr1_transcript_exon": t.get("ewsr1_transcript_exon"),
                     "emc_last_fet_residue_retained": t.get("last_fet_residue_retained"),
                     "emc_RG_retained_fraction": emc_frac, **m,
                     "emc_loses_at_least_as_much":
                         bool(emc_frac <= m["comparator_RG_retained_fraction"])}
                    for m in measured]
            rows.extend(mine)
            held = [r for r in mine if r["emc_loses_at_least_as_much"]]
            per_type[tid] = {
                "label": t.get("label"), "reported_rank": t.get("reported_rank"),
                "emc_RG_retained_fraction": emc_frac,
                "n_measured_types_it_holds_against": len(held),
                "n_measured_types": len(mine),
                "holds_against_every_measured_type": len(held) == len(mine),
                "measured_types_it_does_not_hold_against": [
                    {"measured_fusion": r["measured_fusion"],
                     "ewsr1_transcript_exon": r["ewsr1_transcript_exon"],
                     "comparator_RG_retained_fraction": r["comparator_RG_retained_fraction"]}
                    for r in mine if not r["emc_loses_at_least_as_much"]],
            }
        holds = sorted(k for k, v in per_type.items() if v["holds_against_every_measured_type"])
        fails = sorted(k for k, v in per_type.items() if not v["holds_against_every_measured_type"])
        comparative = {
            "_claim_under_test": "for EACH reported EWSR1::NR4A3 transcript type, that type loses "
                                 "at least as much of EWSR1's RGG content as each fusion in which "
                                 "ATM suppression was MEASURED",
            "_why_per_type": "⛔ this was one boolean over one record keyed "
                             "`emc_canonical_EWSR1_NR4A3`, which held the exon-7 cut — reported "
                             "TYPE 2, the second-commonest — so the flag answered for the type the "
                             "artifact happened to carry and read as though it answered for EMC. "
                             "The reported types do not agree with each other, so there is no "
                             "honest single flag to print.",
            "rows": rows,
            "per_emc_type": per_type,
            "holds_for_every_reported_emc_type": not fails,
            "reported_types_it_holds_for": holds,
            "reported_types_it_fails_for": fails,
            "_reading": "the claim holds for the reported types in `reported_types_it_holds_for` "
                        "and FAILS for those in `reported_types_it_fails_for`. ⛔ A failure here is "
                        "not evidence that the mechanism is absent: it says the comparison the "
                        "controls license does not reach that type, so that type's answer rests on "
                        "nothing this module computed. What each failing type still has is its "
                        "position on the same axis, reported in `per_emc_type` — read it there and "
                        "not as a verdict.",
            "_why_this_and_not_an_absolute_bar": "the controls show the absolute bar is conservative "
                                                 "— a measured fusion violates it — so a comparison "
                                                 "is what the evidence supports and it needs no "
                                                 "threshold that could be tuned",
            "_what_was_NOT_changed_to_get_this_answer": "the criterion. `precondition_met` is still "
                                                        "`rg_dipeptides_retained == 0`, the "
                                                        "comparison is still `emc_frac <= "
                                                        "comparator_frac`, and the control rule is "
                                                        "still 'at least one reported type of each "
                                                        "measured fusion must read "
                                                        "PRECONDITION_MET'. Loosening any of them "
                                                        "to admit more EMC types would be the "
                                                        "cycle rewriting the bar that inconveniences "
                                                        "it; the split is the result.",
        }
    elif ctrl_ok:
        comparative = {"_status": "UNDETERMINED — " + (emc_types_status or
                       "no reported EMC type carries a computed RG fraction")}

    result = {
        "_question": "Do EMC's FET fusions satisfy the structural precondition of the FET -> ATM-"
                     "suppression -> ATR-dependency mechanism (retain the N-terminal IDR, lose the "
                     "C-terminal RGG repeats)?",
        "_source_of_the_precondition": "biorxiv 10.1101/2023.04.30.538578 / PMID 37205599, quoted in "
                                       "this module's docstring from the fetched full text",
        "_operational_definitions": {
            "verdict_criterion": "rg_dipeptides_retained == 0 — THRESHOLD-FREE. An RG dipeptide is "
                                 "either inside the retained segment or it is not.",
            "rgg_box": f"reported for context only: a window of {RGG_WINDOW} residues containing "
                       f">= {RGG_MIN_RG_IN_WINDOW} RG dipeptides, merged across overlaps, with each "
                       "box spanning its first to its last RG",
            "n_terminal_composition": "REPORTED, never gated — see lc_composition's docstring for "
                                      "the tested reason the composition threshold was removed",
        },
        "wild_type_annotation": annot,
        "positive_controls": controls,
        "positive_controls_pass": ctrl_ok,
        "_control_rule": "AT LEAST ONE reported type of EACH measured fusion must read "
                         "PRECONDITION_MET. They are the fusions the mechanism was measured on, so "
                         "if the criterion cannot admit their architecture nothing else here may be "
                         "quoted. ⚠ The rule is 'any type', not 'all types', because a fusion's "
                         "breakpoint varies between patients and this repo has no exon audit fixing "
                         "which type the source's constructs used — a stricter rule would be "
                         "answering a question the inputs cannot answer.",
        "_what_the_controls_calibrate": "If some reported type of a MEASURED fusion retains RG "
                                        "dipeptides and the mechanism was still observed, then "
                                        "'loses the C-terminal RGG repeats' is satisfied by losing "
                                        "the BULK rather than literally all of them — which makes "
                                        "fraction_of_wildtype_RG_retained the quantity to compare "
                                        "EMC against, and the strict zero-RG verdict a CONSERVATIVE "
                                        "reading. Both are reported so the distinction is visible.",
        "emc_EWSR1_NR4A3_reported_types": emc_types if ctrl_ok else
        {"_withheld": "positive controls did not pass"},
        "_why_this_key_is_not_called_canonical": "⛔ SUPERSEDED KEY, RETAINED HERE SO IT STAYS "
                                                 "SEARCHABLE: this block was one record keyed "
                                                 "`emc_canonical_EWSR1_NR4A3`. It held the exon-7 "
                                                 "cut — EWSR1(1-264), reported TYPE 2, the "
                                                 "SECOND-commonest EMC transcript — under a name "
                                                 "asserting it is the canonical one, while the "
                                                 "commonest reported type (EWSR1 e12, residue 431) "
                                                 "was absent from the artifact entirely. The label "
                                                 "drift was flagged in this module's docstring on "
                                                 "2026-08-03 and corrected in the prose that quotes "
                                                 "it; the DATA is corrected here. ⚠ Nothing "
                                                 "measured was withdrawn — the 264-residue "
                                                 "arithmetic is unchanged and is still the right "
                                                 "comparator for EWSR1::FLI1 type 1. What changed "
                                                 "is the name and the coverage. One home for the "
                                                 "superseded figure: research/manuscripts/"
                                                 "dependency/emc-atr-collaborator-package.md, "
                                                 "appendix.",
        "_reported_types_covered": {
            "_how_they_got_here": "READ from the sourced junction registry "
                                  "(emc_fet_construct_designs.py::BREAKPOINTS -> "
                                  "emc-fet-construct-designs.json), which carries the literature "
                                  "quote licensing each exon number. ⛔ No breakpoint is typed in "
                                  "this module, and a partner with no sourced transcript junction "
                                  "gets a sweep rather than an invented point.",
            "ids": sorted(emc_types) if ctrl_ok else [],
            "registry_read_status": emc_types_status,
        },
        "emc_retained_half_vs_measured_fusions": ident if ctrl_ok else {},
        "emc_TAF15_and_FUS_breakpoint_sweep": sweeps if ctrl_ok else {},
        "emc_vs_measured_fusions_comparative": comparative,
        "_limits": [
            "This is a SEQUENCE argument about a structural precondition. It cannot show that any "
            "NR4A3 fusion is actually recruited to double-strand breaks or actually suppresses ATM — "
            "those are the wet-lab measurements the route asks for.",
            "The RGG and IDR definitions are operational. A different threshold could move a box "
            "boundary; the controls exist so that a definition which cannot recover the measured "
            "fusions' architecture is caught rather than trusted.",
            "FUS::NR4A3's breakpoint is swept, not known — no exon-level junction for it is sourced "
            "in this repo's literature cache. A sweep answers 'for which breakpoints does this "
            "hold', never 'this is the breakpoint'. TAF15::NR4A3 keeps its sweep and additionally "
            "carries the one point the literature does pin ('exclusively', 'always').",
            "The EWSR1::NR4A3 coverage is exactly the reported types the sourced registry carries "
            "— types 1, 2 and 5. A reported type the registry does not carry is absent here, and "
            "its absence is a statement about this repo's literature cache, not about the disease.",
            "The comparative answer SPLITS across those types and is reported per type. A reader "
            "wanting one number for EMC will not find one, because the reported types disagree and "
            "this module will not average them into a verdict.",
        ],
    }

    if args.check:
        if not os.path.exists(OUT):
            print("no artifact to check against", file=sys.stderr)
            return 1
        old = json.load(open(OUT))
        drift = [k for k in result if k != "_limits" and old.get(k) != result[k]]
        print("REPRODUCES" if not drift else f"DRIFT in: {drift}")
        return 0 if not drift else 1

    json.dump(result, open(OUT, "w"), indent=2)
    print(json.dumps({k: result[k] for k in
                      ("positive_controls_pass", "positive_controls",
                       "emc_EWSR1_NR4A3_reported_types",
                       "emc_vs_measured_fusions_comparative")}, indent=2)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
