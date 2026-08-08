#!/usr/bin/env python3
"""
Transcriptome-wide off-target screen for the fusion-junction gapmer ASOs.

WHY: junction_aso.py only checks that a gapmer's target window is not a *perfect*
substring of the two parent CDSs. A real specificity claim needs a transcriptome-wide
near-match search: could the antisense oligo hybridise (with a few mismatches) to some
OTHER human transcript and trigger RNase-H cleavage there? This script answers that for
the committed fusion-specific designs.

HOW: for each top fusion-specific gapmer, take its 16-mer target_mRNA (sense) window and
BLAST it (blastn-short, low-complexity filter OFF — these SYGQ-derived windows are
GC/repeat-biased) against human RefSeq RNA via the NCBI BLAST URL API. We then flag, per
oligo, any near-complementary off-target transcript that is NOT EWSR1 or NR4A3, and — the
RNase-H-relevant part — whether the match covers the central DNA-gap region (positions
WING..LEN-WING), since RNase-H cleavage needs the DNA:RNA duplex contiguous across the gap;
a match confined to a wing is a weaker (affinity-only) liability than a gap-spanning match.

INTERNET REQUIRED (NCBI). The dev sandbox blocks outbound HTTPS, so this is meant to run on
a GitHub-hosted runner (.github/workflows/aso-offtarget.yml), which publishes the result JSON
to the `modalities-cache` branch — the same pattern as depmap_sarcoma_dependency.py.

Graceful degradation: if a BLAST query fails/times out, that oligo is recorded with
status="screen_failed" rather than crashing the run, so partial results still publish.

Output: junction-aso-offtarget.json
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import junction_aso as ja   # reuse the committed design logic (no duplication)

# Breakpoint is parameterisable (env) so the SAME screen can be run on the canonical breakpoint
# OR on a favorable one identified by the per-breakpoint scan, to test whether the GC/complexity
# "favorable" triage actually yields off-target cleanliness under the full BLAST screen.
if os.environ.get("EWSR1_KEEP_AA"):
    ja.EWSR1_KEEP_AA = int(os.environ["EWSR1_KEEP_AA"])
if os.environ.get("NR4A3_KEEP_AA_FROM"):
    ja.NR4A3_KEEP_AA_FROM = int(os.environ["NR4A3_KEEP_AA_FROM"])
_SUFFIX = os.environ.get("OUT_SUFFIX", "")
OUT = os.path.join(os.path.dirname(__file__), f"junction-aso-offtarget{_SUFFIX}.json")

BLAST = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
PARENT_ACCS = {"NM_005243", "NM_006981"}          # EWSR1, NR4A3 (the intended on-/parent hits)
PARENT_GENES = ("EWSR1", "EWS RNA", "NR4A3", "NOR-1", "nuclear receptor subfamily 4 group A member 3")
N_OLIGOS = 6                                       # screen the top N fusion-specific designs
# near match = allow up to 2 mismatches over the oligo length (14/16 at len 16, 18/20 at len 20)
NEAR_MATCH_MIN_IDENT = ja.OLIGO_LEN - 2
POLL_MAX_S = 600                                   # cap per-query polling at 10 min


def _http(url, data=None, timeout=120):
    req = urllib.request.urlopen(url if data is None else urllib.request.Request(url, data=data),
                                 timeout=timeout)
    return req.read().decode("utf-8", "replace")


def blast_put(seq):
    """Submit a short blastn search restricted to human RefSeq RNA; return the RID."""
    params = {
        "CMD": "Put", "PROGRAM": "blastn", "DATABASE": "refseq_rna",
        "QUERY": seq, "WORD_SIZE": "7", "EXPECT": "1000", "HITLIST_SIZE": "50",
        "FILTER": "F", "MEGABLAST": "off", "ENTREZ_QUERY": "txid9606[ORGN]",
    }
    html = _http(BLAST, data=urllib.parse.urlencode(params).encode())
    m = re.search(r"^\s*RID = (\S+)", html, re.M)
    if not m:
        raise RuntimeError("no RID returned from BLAST Put")
    return m.group(1)


def blast_poll(rid):
    """Poll until the search is READY; raise on FAILED/UNKNOWN or timeout."""
    waited = 0
    while waited < POLL_MAX_S:
        html = _http(BLAST + "?" + urllib.parse.urlencode(
            {"CMD": "Get", "RID": rid, "FORMAT_OBJECT": "SearchInfo"}))
        m = re.search(r"Status=(\w+)", html)
        status = m.group(1) if m else "UNKNOWN"
        if status == "READY":
            return
        if status in ("FAILED", "UNKNOWN"):
            raise RuntimeError(f"BLAST status {status} for RID {rid}")
        time.sleep(20)
        waited += 20
    raise RuntimeError(f"BLAST poll timeout for RID {rid}")


def blast_hits(rid):
    """Fetch XML results and return parsed HSPs."""
    xml = _http(BLAST + "?" + urllib.parse.urlencode(
        {"CMD": "Get", "RID": rid, "FORMAT_TYPE": "XML"}), timeout=180)
    root = ET.fromstring(xml)
    hits = []
    for hit in root.iter("Hit"):
        hid = (hit.findtext("Hit_accession") or "")
        hdef = (hit.findtext("Hit_def") or "")
        for hsp in hit.iter("Hsp"):
            ident = int(hsp.findtext("Hsp_identity") or 0)
            alen = int(hsp.findtext("Hsp_align-len") or 0)
            qfrom = int(hsp.findtext("Hsp_query-from") or 0)
            qto = int(hsp.findtext("Hsp_query-to") or 0)
            hits.append({"acc": hid, "defn": hdef, "identity": ident, "align_len": alen,
                         "q_from": qfrom, "q_to": qto,
                         "qseq": hsp.findtext("Hsp_qseq") or "",
                         "midline": hsp.findtext("Hsp_midline") or ""})
    return hits


def is_parent(h):
    acc = h["acc"].split(".")[0]
    if acc in PARENT_ACCS:
        return True
    d = h["defn"].upper()
    return any(g.upper() in d for g in PARENT_GENES)


def gap_mismatch_profile(h):
    """(reaches_gap, gap_fully_covered, n_gap_mismatches or None) for one BLAST HSP.

    Cleavage needs a contiguous DNA:RNA duplex across the central DNA gap (query positions
    [WING+1 .. LEN-WING]). This walks the alignment, maps each column to a query position and
    counts mismatches inside the gap. `n_gap_mismatches` is None when the alignment strings are
    absent, which is the coverage-only fallback case and must never be read as zero."""
    gap_lo, gap_hi = ja.WING + 1, ja.OLIGO_LEN - ja.WING       # 1-based inclusive gap span
    if not (h["q_from"] <= gap_lo and h["q_to"] >= gap_hi):
        return False, False, None
    qseq, mid = h.get("qseq", ""), h.get("midline", "")
    if not qseq or not mid or len(qseq) != len(mid):
        return True, False, None                               # reaches it; cannot resolve it
    qpos = h["q_from"]
    gap_mismatches, gap_covered = 0, set()
    for qc, mc in zip(qseq, mid):
        if qc == "-":                                          # insertion in target; query pos unchanged
            continue
        if gap_lo <= qpos <= gap_hi:
            gap_covered.add(qpos)
            if mc != "|":
                gap_mismatches += 1
        qpos += 1
    if len(gap_covered) < (gap_hi - gap_lo + 1):
        return False, False, None
    return True, True, gap_mismatches


def classify(h):
    """RNase-H cleavage relevance, resolved to the gap-mismatch level.

      - gap not fully covered  -> "wing_only_affinity_risk"  (no gap duplex; weak liability)
      - gap covered, 0 gap mismatches -> "true_cleavage_risk" (the real RNase-H liability)
      - gap covered, >=1 gap mismatch -> "gap_disrupted_no_cleavage" (mismatch falls in the gap)
      - alignment strings absent      -> "gap_spanning_cleavage_risk" (coverage-only fallback)

    ⛔ THESE LABELS ARE A PARTITION, NOT A VERDICT. `gap_disrupted_no_cleavage` says where the
    mismatch fell; it does NOT say the transcript is safe, and reading it as zero risk is the
    defect `grade_panel()` below exists to correct — see DISCRIMINATION_MODELS."""
    reaches, covered, n_mm = gap_mismatch_profile(h)
    if not reaches:
        return "wing_only_affinity_risk"
    if not covered:
        return "gap_spanning_cleavage_risk"                    # coverage-only fallback
    if n_mm == 0:
        return "true_cleavage_risk"
    if n_mm is None:                                           # unreachable; defensive
        return "gap_spanning_cleavage_risk"
    return "gap_disrupted_no_cleavage"


# ─────────────────────────────────────────────────────────────────────────────────────────
# THE DISCRIMINATION MODEL — why "gap mismatch ⇒ 0 predicted-cleavable" is not a call we may make
# ─────────────────────────────────────────────────────────────────────────────────────────
# ⛔ THE PANEL'S ORIGINAL HEADLINE COUNTED EVERY GAP-DISRUPTED NEAR-MATCH AS ZERO-CLEAVABLE, AND
# THE PRIMARY LITERATURE DOES NOT SUPPORT THAT. Two retrieved sources, both anchored in
# research/manuscripts/lit-targets-aso-verify.json and both re-verified against PubMed, Europe PMC
# and Crossref on 2026-08-08 (Actions run 31276141296):
#
#   * PMID 23963702 (Østergaard ME, Southwell AL, Kordasiewicz H, Watt AT, Skotte NH, Doty CN,
#     Vaid K, Villanueva EB, Swayze EE, Bennett CF, Hayden MR, Seth PP; Nucleic Acids Res
#     41(21):9634-50, 2013; doi 10.1093/nar/gkt725) — "ASOs have been previously shown to
#     discriminate single nucleotide changes in targeted RNAs with ~5-fold selectivity … The
#     resulting oligonucleotides demonstrate >100-fold discrimination …" where "the resulting"
#     means ASOs carrying POSITIONAL CHEMICAL MODIFICATIONS placed to limit RNase H cleavage of
#     the non-targeted transcript. So an UNMODIFIED gapmer — which is all this panel's designs are
#     — buys ~5-fold, and the >100-fold figure requires chemistry these designs do not carry.
#     REDUCTION, NOT ABOLITION.
#
#   * PMID 7567450 (Duroux I, Godard G, Boidot-Forget M, Schwab G, Hélène C, Saison-Behmoaras T;
#     Nucleic Acids Res 23(17):3411-3418, 1995; doi 10.1093/nar/23.17.3411) — "Short
#     oligonucleotides (12- or 13mers) centered on the mutation had a very high discriminatory
#     efficiency. Longer oligonucleotides (16mers) DID NOT DISCRIMINATE EFFICIENTLY between the
#     mutated and the normal mRNA." ⚠ THIS PANEL'S DESIGNS ARE 16-MERS (ja.OLIGO_LEN). The one
#     retrieved result that speaks to this geometry speaks against it, and it is a length effect —
#     so it cannot be argued away by choosing a better mismatch position.
#
# Consequence: there is no defensible fold value, only a RANGE whose two ends are these two papers.
# The panel is therefore scored under BOTH, and neither end is reported alone.
DISCRIMINATION_MODELS = {
    "ostergaard_5fold": {
        "fold_per_gap_mismatch": 5.0,
        "source": "PMID 23963702 (doi 10.1093/nar/gkt725)",
        "what": ("~5-fold discrimination per single-nucleotide change for an UNMODIFIED "
                 "RNase-H-active ASO. The OPTIMISTIC end: it is the figure for a gapmer chosen "
                 "and positioned for allele selectivity, which these designs were not."),
    },
    "duroux_16mer_none": {
        "fold_per_gap_mismatch": 1.0,
        "source": "PMID 7567450 (doi 10.1093/nar/23.17.3411)",
        "what": ("16-mers 'did not discriminate efficiently'; discrimination in that assay was "
                 "confined to 12-13mers centred on the mismatch. The PESSIMISTIC end, and the "
                 "one matching this panel's oligo LENGTH: a gap-internal mismatch buys nothing, "
                 "so every near-match counts at full weight."),
    },
}

# ⛔ RETIRED, KEPT NAMED SO THE OLD FIGURE STAYS TRACEABLE. `fold = inf` is the assumption that
# produced "2 of 5 predicted off-target-clean". It is not in DISCRIMINATION_MODELS because it is
# not a model the literature supports — it is the thing being corrected.
RETIRED_ABOLITION_MODEL = {
    "name": "all_gap_mismatch_blocks_cleavage",
    "fold_per_gap_mismatch": float("inf"),
    "why_retired": ("no retrieved source supports abolition; both sources above measure or imply "
                    "a finite fold, and the one that matches the 16-mer length implies ~none."),
}

# Total mismatches over a near-match are bounded by (OLIGO_LEN - NEAR_MATCH_MIN_IDENT), so a
# gap-disrupted hit carries at least 1 and at most that many gap-internal mismatches. That bound is
# what lets a TRUNCATED off-target list still yield an exact interval rather than a guess.
MAX_MISMATCHES_PER_NEAR_MATCH = ja.OLIGO_LEN - NEAR_MATCH_MIN_IDENT


def cleavage_weight(n_gap_mismatches, fold):
    """Residual predicted cleavage of one off-target, relative to a perfect gap duplex (= 1.0).

    fold**-n. ⚠ Independence across mismatches is an ASSUMPTION — neither source measures two
    gap-internal mismatches — and it is recorded as one in the artifact rather than buried here."""
    if n_gap_mismatches <= 0:
        return 1.0
    if fold == float("inf"):
        return 0.0
    return float(fold) ** (-int(n_gap_mismatches))


def grade_one(oligo, fold):
    """Residual predicted cleavage LOAD for one screened oligo, as a closed interval.

    The interval is not a confidence interval. Its width is TRUNCATION: `screen_one` saves only
    the strongest 15 off-targets, while the per-oligo counters are complete, so hits beyond the
    saved list are known to be gap-disrupted but not to what depth. Each such hit is bounded by
    `cleavage_weight(MAX_MISMATCHES_PER_NEAR_MATCH, fold) .. cleavage_weight(1, fold)`.
    Where the saved list covers every near-match, lo == hi and `exact` is True."""
    n_true = int(oligo.get("n_true_cleavage_risk") or 0)
    n_gapdis = int(oligo.get("n_gap_disrupted_no_cleavage") or 0)
    n_fallback = int(oligo.get("n_coverage_only_fallback") or 0)
    n_wing = int(oligo.get("n_wing_only_affinity") or 0)
    saved = oligo.get("offtargets") or []

    hist = oligo.get("gap_mismatch_histogram")
    if hist:
        # ⭐ COMPLETE histogram over every ranked hit — written by screens run after 2026-08-08.
        # No truncation, so the interval collapses to a point.
        resolved = sum(int(v) for k, v in hist.items() if int(k) > 0)
        resolved_load = sum(int(v) * cleavage_weight(int(k), fold)
                            for k, v in hist.items() if int(k) > 0)
    else:
        # ⚠ PRE-2026-08-08 SCREEN: only the strongest 15 off-targets carry alignments, so the
        # tail is known to be gap-disrupted but not to what depth. Bounded, never guessed.
        resolved, resolved_load = 0, 0.0
        for h in saved:
            _, covered, n_mm = gap_mismatch_profile(h)
            if covered and n_mm and n_mm > 0:
                resolved += 1
                resolved_load += cleavage_weight(n_mm, fold)
    unresolved = max(0, n_gapdis - resolved)
    w_hi = cleavage_weight(1, fold)
    w_lo = cleavage_weight(MAX_MISMATCHES_PER_NEAR_MATCH, fold)

    # a full-gap-duplex hit and a coverage-only fallback both count at full weight
    base = float(n_true + n_fallback)
    lo = base + resolved_load + unresolved * w_lo
    hi = base + resolved_load + unresolved * w_hi
    return {
        "n_offtarget_near_matches": int(oligo.get("n_offtarget_near_matches") or 0),
        "n_full_gap_duplex": n_true,
        "n_gap_disrupted": n_gapdis,
        "n_gap_disrupted_resolved_from_saved_alignments": resolved,
        "n_gap_disrupted_unresolved_by_truncation": unresolved,
        "n_coverage_only_fallback_counted_at_full_weight": n_fallback,
        "n_wing_only_not_counted": n_wing,
        "residual_cleavage_load_lo": round(lo, 4),
        "residual_cleavage_load_hi": round(hi, 4),
        "exact": unresolved == 0,
        "zero_predicted_cleavage_load": hi == 0.0,
    }


def grade_panel(screen):
    """Re-score a committed screen artifact under the graded models. NO NETWORK, NO RE-BLAST.

    ⛔ DELIBERATELY DERIVED FROM THE COMMITTED SCREEN RATHER THAN A FRESH ONE. A new BLAST would
    return a different hit set, and the old and new headline figures would then differ for two
    reasons at once — the model change and the retrieval change — which is exactly the comparison
    a corrected headline must not be muddied by. The hit set is held fixed; only the scoring moves."""
    graded, per_model = {}, {}
    ok = [o for o in screen.get("oligos", []) if o.get("status") == "screened"]
    for name, m in DISCRIMINATION_MODELS.items():
        fold = m["fold_per_gap_mismatch"]
        rows = {o["antisense_5to3"]: grade_one(o, fold) for o in ok}
        graded[name] = rows
        per_model[name] = {
            **m,
            "n_oligos_with_zero_predicted_cleavage_load": sum(
                1 for r in rows.values() if r["zero_predicted_cleavage_load"]),
            "rank_best_first": [k for k, _ in sorted(
                rows.items(), key=lambda kv: (kv[1]["residual_cleavage_load_hi"],
                                              kv[1]["residual_cleavage_load_lo"], kv[0]))],
        }
    retired = sum(1 for o in ok if int(o.get("n_true_cleavage_risk") or 0) == 0)
    return {
        "_what": ("Graded re-score of a committed gap-resolved off-target screen. Replaces the "
                  "binary 'a mismatch in the DNA gap abolishes RNase-H cleavage' assumption with "
                  "the fold-discrimination the primary literature actually reports."),
        "_the_correction": (
            f"Under the retired abolition assumption {retired} of {len(ok)} oligos scored "
            f"'0 predicted-cleavable off-targets' and were called predicted off-target-clean. "
            "Under BOTH literature-supported models that count is 0 of "
            f"{len(ok)}: every design retains a non-zero predicted residual cleavage load, "
            "because every design has at least one gap-disrupted near-match and a gap-disrupted "
            "near-match is reduced, not abolished. What survives is a RANK ORDER, not a "
            "clean/dirty call."),
        "_what_this_is_not": [
            "Not a measurement. No RNase-H1 cleavage was measured here or anywhere in this "
            "repository; this re-weights a BLAST-derived prediction under a literature prior.",
            "Not a safety, efficacy or selectivity claim, and not a therapeutic-window statement.",
            "Wing-only near-matches (alignment does not reach the DNA gap) are scored 0 for "
            "CLEAVAGE and are not thereby harmless — they remain affinity liabilities, counted "
            "separately as n_wing_only_not_counted.",
            "Independence across two gap-internal mismatches is an assumption. Neither source "
            "measures it, which is why the pessimistic model (fold 1.0) is reported alongside.",
            "The interval width is TRUNCATION of the saved off-target list, not statistical "
            "uncertainty. Where `exact` is true there is no truncation.",
        ],
        "retired_model": RETIRED_ABOLITION_MODEL,
        "retired_model_headline": f"{retired} of {len(ok)} predicted off-target-clean",
        "near_match_threshold": f">= {NEAR_MATCH_MIN_IDENT}/{ja.OLIGO_LEN} identical",
        "oligo_len": ja.OLIGO_LEN,
        "gap_region_1based": [ja.WING + 1, ja.OLIGO_LEN - ja.WING],
        "max_mismatches_per_near_match": MAX_MISMATCHES_PER_NEAR_MATCH,
        "models": per_model,
        "per_oligo": graded,
        "source_screen": screen.get("junction_label"),
        "source_breakpoint": screen.get("breakpoint"),
    }


def rescore(paths):
    """`--rescore <screen.json> ...` -> writes `<screen>-graded.json` beside each. $0, offline."""
    for p in paths:
        with open(p, "r", encoding="utf-8") as fh:
            screen = json.load(fh)
        out = p[:-5] + "-graded.json" if p.endswith(".json") else p + "-graded.json"
        art = grade_panel(screen)
        art["_generated_from"] = os.path.basename(p)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(art, fh, indent=2)
        print("wrote", out, file=sys.stderr)
        print(json.dumps({"source": os.path.basename(p),
                          "retired_headline": art["retired_model_headline"],
                          "correction": art["_the_correction"],
                          "models": {k: {"zero_load": v["n_oligos_with_zero_predicted_cleavage_load"],
                                         "rank": v["rank_best_first"]}
                                     for k, v in art["models"].items()}}, indent=2))
    return 0


def screen_one(design):
    target = design["target_mRNA_5to3"]
    rec = {"antisense_5to3": design["antisense_5to3"], "target_mRNA_5to3": target,
           "gc_percent": design["gc_percent"], "specificity_margin": design["specificity_margin"]}
    try:
        rid = blast_put(target)
        blast_poll(rid)
        hits = blast_hits(rid)
        offt = [h for h in hits
                if h["identity"] >= NEAR_MATCH_MIN_IDENT and not is_parent(h)]
        # dedup by accession, keep the strongest HSP
        best = {}
        for h in offt:
            k = h["acc"]
            if k not in best or h["identity"] > best[k]["identity"]:
                h["risk"] = classify(h)
                # ⭐ CARRIED PER HIT so a graded re-score never has to re-walk the alignment, and
                # so the DEPTH of gap disruption survives the `[:15]` truncation for saved hits.
                h["gap_mismatches"] = gap_mismatch_profile(h)[2]
                best[k] = h
        ranked = sorted(best.values(), key=lambda h: (-h["identity"], h["acc"]))
        rec.update({
            "status": "screened",
            "blast_rid": rid,
            "n_parent_or_intended_hits": sum(1 for h in hits if is_parent(h)),
            "n_offtarget_near_matches": len(ranked),
            "n_true_cleavage_risk": sum(1 for h in ranked if h["risk"] == "true_cleavage_risk"),
            "n_gap_disrupted_no_cleavage": sum(1 for h in ranked
                                               if h["risk"] == "gap_disrupted_no_cleavage"),
            "n_wing_only_affinity": sum(1 for h in ranked if h["risk"] == "wing_only_affinity_risk"),
            "n_coverage_only_fallback": sum(1 for h in ranked
                                            if h["risk"] == "gap_spanning_cleavage_risk"),
            # ⛔ COMPLETE HISTOGRAM OVER ALL RANKED HITS, not just the 15 saved below. Without it a
            # graded re-score can only BOUND the truncated tail; with it the bound is exact.
            "gap_mismatch_histogram": {
                str(n): sum(1 for h in ranked if h.get("gap_mismatches") == n)
                for n in range(0, MAX_MISMATCHES_PER_NEAR_MATCH + 1)},
            "n_gap_mismatch_unresolvable": sum(1 for h in ranked
                                               if h.get("gap_mismatches") is None),
            "offtargets": ranked[:15],
        })
    except Exception as e:  # noqa: BLE001 — never crash the whole screen on one query
        rec.update({"status": "screen_failed", "error": str(e)})
    return rec


def main():
    ews, nr4, left, right, fusion = ja.build_parents_and_fusion()
    label, prov = ja.junction_label()
    designs = [o for o in ja.design(left, right, fusion) if o["fusion_specific"]][:N_OLIGOS]

    screened = []
    for i, d in enumerate(designs):
        print(f"  screening oligo {i+1}/{len(designs)}: {d['target_mRNA_5to3']}", file=sys.stderr)
        screened.append(screen_one(d))
        time.sleep(3)   # be polite to NCBI between submissions

    n_ok = sum(1 for r in screened if r["status"] == "screened")
    n_clean = sum(1 for r in screened
                  if r.get("status") == "screened" and r.get("n_true_cleavage_risk", 1) == 0)
    result = {
        "junction_label": label,
        # ⛔ IN REAL MODE, `ja.EWSR1_KEEP_AA` / `ja.NR4A3_KEEP_AA_FROM` ARE NOT WHAT WAS BUILT.
        # They are the codon-space MODELLED-reference constants (264 / from-2) and they are ignored by the
        # real-mode builder — yet the regenerated e12n3/e7n3 panels emitted `NR4A3_from_aa: 2` beside a
        # measured resume residue of 1, i.e. the artifact contradicted itself in adjacent keys and the
        # stale number was the more quotable one (measured 2026-08-06 on the corrected regeneration run).
        # In real mode carry the MEASURED grading; keep the constants only where they are what ran.
        "breakpoint": {**prov,
                       **({"measured_junction": {k: v for k, v in ja.LAST_JUNCTION.items()
                                                 if not k.startswith("_")}}
                          if ja.LAST_JUNCTION else
                          {"EWSR1_keep_aa": ja.EWSR1_KEEP_AA,
                           "NR4A3_from_aa": ja.NR4A3_KEEP_AA_FROM}),
                       "junction_context_mRNA": (left[-12:] + "|" + right[:12]),
                       "_transcript_source": ja.transcript_source_provenance()},
        "_note": ("Transcriptome-wide off-target screen of the fusion-junction gapmer ASOs "
                  "(blastn-short vs human RefSeq RNA, NCBI BLAST URL API), resolved to the "
                  "gap-mismatch level. A TRUE cleavage risk = an off-target near-match whose "
                  "central DNA gap is fully matched (RNase-H can cleave); a gap-disrupted hit "
                  "(mismatch inside the gap) does NOT cleave; wing-only hits are weak affinity "
                  "liabilities. A clean oligo has zero true_cleavage_risk off-targets. Predicted "
                  "specificity, not validated; confirm by the parental-/off-target-sparing assays."),
        "method": {
            "db": "refseq_rna (txid9606[ORGN])", "program": "blastn (short, FILTER off)",
            "near_match_threshold": f">= {NEAR_MATCH_MIN_IDENT}/{ja.OLIGO_LEN} identical",
            "gap_region_1based": [ja.WING + 1, ja.OLIGO_LEN - ja.WING],
            "breakpoint_model": prov["note"],
        },
        "n_oligos_screened": len(screened),
        "n_screened_ok": n_ok,
        "n_oligos_no_true_cleavage_risk": n_clean,
        "oligos": screened,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "oligos"}, indent=2))


if __name__ == "__main__":
    # `--rescore <screen.json> ...` re-grades committed screens offline ($0, no BLAST); bare
    # invocation runs the network screen as before.
    if "--rescore" in sys.argv:
        i = sys.argv.index("--rescore")
        sys.exit(rescore(sys.argv[i + 1:]))
    main()
