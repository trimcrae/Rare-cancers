#!/usr/bin/env python3
"""THE $0 PRECHECK that must precede any pmx/GROMACS spend on the SMARCA2/4 selectivity contact.

WHAT IT DECIDES
---------------
STRATEGY.md's tally of built-but-never-run known-answer tests records the pmx lane as:

    A pmx/GROMACS interface point-mutation ddG -- the only physics lane here that has recovered a
    published known answer (barnase-barstar Y29A +4.42 +/- 1.08 vs +3.4 and Y29F -0.370 +/- 0.175 vs
    -0.13, both inside 1.5 kcal/mol, ~$0.21/leg, `triskit23/pmxfep` already baked) and it works on
    **PPI interfaces**. This document's own reading of the selcal null is that SMARCA2/4 selectivity
    *"turns on a single Gln1469 hydrogen bond"* -- i.e. a point mutation. **Conditional on a measured
    mutational value existing in a primary source, which is a $0 check that must precede any spend
    (Open decision 7).**

This module IS that check. It answers one question and refuses to answer any other:

    Does a MEASURED binding ddG for the SMARCA2 Gln1469 selectivity contact -- or for a defensibly
    equivalent single point mutation at the same VHL/VCB-facing interface in this system -- exist in a
    primary source?

If the answer is no, the spend does not happen. A known-answer test whose known answer does not exist
is not a known-answer test; it is an experiment with an unknown result wearing a control's costume,
and this repo has already withdrawn three selectivity claims that came from instruments in exactly
that state (program map section 3).

WHY IT CANNOT RUN IN THE DEV SANDBOX, AND WHY THAT IS NOT A REASON TO DEFER
--------------------------------------------------------------------------
The sandbox egress proxy answers NCBI / PMC / Europe PMC / UniProt with 403 at CONNECT, and
life.bsc.es (SKEMPI) with a transport failure. CLAUDE.md section 6 routes this to a GitHub Actions
runner, which has unrestricted internet. `gpu-protfep-vast.yml task=refcheck` runs it and commits the
artifact. `--offline` exists only so the verdict logic can be unit-tested; it never fabricates data.

TWO INDEPENDENT INSTRUMENTS, BOTH $0
------------------------------------
A. **SKEMPI 2.0** -- the curated database of experimentally measured binding affinities for mutants of
   structurally-resolved protein-protein complexes. It is the same instrument that supplied the
   barnase-barstar references this engine was qualified against (`protfep_refcheck`), so using it here
   is not a new standard of evidence, it is the standing one. Scanned two ways: by the deposited PDB
   entries of this system, and by protein NAME across the whole database, because a curator is free to
   key a record to a different deposit of the same complex.
B. **Europe PMC full text** -- quoted sentences with their source, never a curated number. The rule
   `selcal_reference_selectivity` established and this module inherits: it emits EVIDENCE and concludes
   nothing that a human cannot re-read from the quote.

THE GATE IS OPEN DECISION 7's, APPLIED ON ITS OWN TERMS
-------------------------------------------------------
Open decision 7 resolved the admits-zero gate defect, and its binding consequence for every future
calibrator is stated there: **"no accuracy band wider than the signal being calibrated, and a stated
null-rejection rate up front."** So a bare "a number exists somewhere" does NOT clear it. Three
conditions, checked mechanically by `verdict()`:

  G1  MEASURED and PRIMARY -- a value backed by a reported measurement (Kd/ddG with a method), not
      inferred from a structure figure, a docking score, or a degradation DC50 ratio. ⚠ A DC50 ratio is
      a CELLULAR degradation readout; converting one into an interface binding ddG would fabricate the
      quantitative link this program does not have (the same trap `selcal_reference_selectivity`
      refuses on the Angstrom side).
  G2  SIGNAL WIDER THAN THE BAND -- |ddG_ref| must exceed the engine's demonstrated accuracy band at
      the size of the effect being asked about. `ENGINE_BAND` below is not invented here: it is the
      committed benchmark result, and it is EFFECT-SIZE DEPENDENT by 6.2x, which is the whole
      difficulty (see the caveat block).
  G3  NULL-REJECTION RATE STATED UP FRONT -- what result would count as a refutation, written before
      the run.

THE CAVEAT THIS MODULE EXISTS TO CARRY INTO THE WRITE-UP, NOT DISCOVER AFTERWARDS
--------------------------------------------------------------------------------
The program map records this instrument as **PASSES**. That bare word drops a caveat the paper states
explicitly and pricing.md states again: the pass is on a **+3.4 kcal/mol hot-spot knockout** and a
**~0 near-null control**, with NOTHING measured in between --

    between-replicate SD is 6.2x different at the two ends (+/-1.077 at +4.4, +/-0.175 at ~0) while
    within-leg MBAR SEs are 0.05-0.13, so the scatter is setup/equilibration variance, not sampling
    length. No benchmark yet probes the ~1 kcal/mol regime.

A paralogue-scale difference lives in that unprobed middle. So the honest statement, which belongs in
any write-up of a run this precheck authorises: **pmx is demonstrated to see a large interface effect
and demonstrated not to invent one; it is NOT demonstrated to resolve a paralogue-scale difference,
which is the regime the selectivity route actually needs it for.** `caveat()` returns that sentence so
a report cannot be written without it.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "pmx-mutation-reference-precheck.json")

# ------------------------------------------------------------------------------------------------
# The mutation actually being asked about
# ------------------------------------------------------------------------------------------------
# ⚠ The residue NUMBER is not the identity of this contact and must never be the thing we search on
# alone. `selcal_interface_signature.known_answer_check` makes the point and this module inherits it:
# a deposit numbers its construct however it likes. The contact recovered from the real crystals is
#
#     GLN98 (SMARCA2 arm, deposit numbering) OE1 --- 2.88 A --- ARG12 NH2 (VCB arm)
#     aligned SMARCA4 residue: LEU1545, which makes no side-chain polar contact
#
# i.e. the published Gln1469(SMARCA2)/Leu(SMARCA4) substitution, recovered structurally from
# `selcal-interface-signature.json`. The mutation a pmx leg would compute is therefore SMARCA2 Q->L
# at that position (or the reverse, SMARCA4 L->Q).
TARGET = {
    "contact": "SMARCA2 Gln1469 side chain -> VCB (Arg of the VHL/ElonginC/ElonginB module)",
    "published_claim": ("Kofink et al. 2022, Nat Commun 13:5969, PMC9551036: 'the selectivity-inducing "
                        "hydrogen bonding between Gln1469 of SMARCA2BD and VCB'"),
    "mutation_forward": "SMARCA2 Q1469L",
    "mutation_reverse": "SMARCA4 L1545Q",
    "structurally_recovered_as": ("GLN98 OE1 -> ARG12 NH2 at 2.88 A on the SMARCA2 arm, LEU1545 on the "
                                  "aligned SMARCA4 position with no side-chain polar contact "
                                  "(selcal-interface-signature.json known_answer)"),
    "_the_number_is_not_the_identity": ("the contact is identified by alignment and chemistry, never by "
                                        "the residue number, because a deposit numbers its construct "
                                        "however it likes (selcal_interface_signature.known_answer_check)"),
}

#: Deposited entries of this interface, and the adjacent VHL-PROTAC ternaries whose interface a curator
#: could plausibly have keyed a mutational record to. Every one is a real accession named in a primary
#: source already committed to this repo (selcal-reference-selectivity.json / s-calibrator-survey.json).
CANDIDATE_PDBS = [
    # SMARCA2/4 bromodomain : PROTAC : VCB ternaries
    "6HAX", "6HAY", "6HR2", "7Z6L", "7Z76", "7Z77", "8G1P", "8G1Q", "9DTX", "9DTY", "9HYB", "7S4E",
    # binary bromodomain structures of the same arms
    "6HAZ", "7Z78", "4QY4",
    # the canonical VHL-PROTAC ternary whose interface is the best-characterised of its class
    "5T35",
    # VHL:ElonginC:ElonginB itself -- the E3 side of the contact
    "1LM8", "1LQB", "4W9H",
]

#: Protein-name substrings to scan the WHOLE database for. A PDB-keyed scan alone would miss a record
#: curated against a different deposit of the same proteins, which is an ABSENT READING, not a reading
#: of absence (CLAUDE.md section 4).
#
# ⚠ THE SPLIT BELOW IS LOAD-BEARING AND WAS ADDED AFTER THE GATE GOT IT WRONG (measured 2026-08-02).
# The first version pooled every substring into one list and let ANY name hit satisfy G1. It returned
# PROCEED off a 2.048 kcal/mol record that a promiscuous substring had matched somewhere else in the
# database entirely -- a populated field read as a measured one, which is the failure CLAUDE.md
# section 4(b) names. So the two arms of the interface are now tracked separately, and a name hit only
# counts as ON THIS INTERFACE when one partner is the TARGET arm and the other is the E3 arm.
TARGET_ARM_NAMES = ["smarca", "brg1", "brg-1", "brahma", "brm2", "snf2"]
E3_ARM_NAMES = ["von hippel", "vhl", "elongin", "cul2", "rbx"]
#: Discovery-only. A hit here is a LEAD for a human to read, never a value: the adjacent VHL-PROTAC
#: ternaries are a different neo-interface, and a bromodomain is not this bromodomain.
ADJACENT_NAMES = ["bromodomain", "brd4", "brd2", "brd3", "bet family"]
CANDIDATE_PROTEIN_NAMES = TARGET_ARM_NAMES + E3_ARM_NAMES + ADJACENT_NAMES

#: Europe PMC searches. Each is a QUERY, not a conclusion. They are deliberately layered from the
#: narrowest (the exact residue) to the broadest (any mutational thermodynamics on a PROTAC ternary
#: interface), so that a null result is a null across a real search rather than across one guess.
QUERIES = [
    {"tag": "Q1_residue_exact",
     "why": "the exact published residue, by name and by number, in any full text",
     "query": '("Gln1469" OR "Q1469" OR "Gln 1469")'},
    {"tag": "Q2_residue_smarca4_side",
     "why": "the aligned SMARCA4 residue, in case the mutation was made on the other arm",
     "query": '("Leu1545" OR "L1545" OR "Leu 1545") AND (SMARCA4 OR BRG1)'},
    {"tag": "Q3_smarca_mutant_binding",
     "why": "any SMARCA2/4 bromodomain point mutant with a measured affinity to the E3 or a PROTAC",
     "query": '(SMARCA2 AND (mutant OR mutation OR mutagenesis) AND (SPR OR "surface plasmon resonance" '
              'OR ITC OR "isothermal titration" OR "K D" OR Kd) AND (VHL OR PROTAC OR ternary))'},
    {"tag": "Q4_ternary_interface_mutagenesis",
     "why": "mutational thermodynamics anywhere on a VHL PROTAC-induced neo-interface",
     "query": '((PROTAC OR "degrader") AND ternary AND (VHL OR "von Hippel") AND '
              '("point mutation" OR mutagenesis OR "alanine scan" OR "alanine scanning") AND '
              '(cooperativity OR Kd OR "K D" OR affinity))'},
    {"tag": "Q5_selectivity_mechanism_source",
     "why": "the source of the selectivity claim itself, re-fetched rather than remembered",
     "query": 'TITLE:"A selective and orally bioavailable VHL-recruiting PROTAC achieves SMARCA2 '
              'degradation in vivo"'},
    {"tag": "Q6_smarca_swap_mutant",
     "why": "a paralogue-swap construct is the most likely form such a measurement would take",
     "query": '(SMARCA2 AND SMARCA4 AND (chimera OR "swap mutant" OR "gain of function mutant" OR '
              '"reciprocal mutation") AND (degradation OR ternary OR binding))'},
]

#: A sentence is only interesting if it carries BOTH a mutation token AND a measured-quantity token.
#: Either alone is not a measured mutational value: a mutation with no number is a construct, and a
#: number with no mutation is a wild-type affinity.
_MUT = re.compile(
    r"("
    r"\b[ACDEFGHIKLMNPQRSTVWY]\d{2,4}[ACDEFGHIKLMNPQRSTVWY]\b"          # Q1469L
    r"|\b(Ala|Gln|Leu|Asn|Asp|Glu|Lys|Arg|Ser|Thr|Tyr|Phe|Trp|Val|Ile|Met|His|Cys|Gly|Pro)\s?\d{2,4}"
    r"\s?(Ala|Gln|Leu|Asn|Asp|Glu|Lys|Arg|Ser|Thr|Tyr|Phe|Trp|Val|Ile|Met|His|Cys|Gly|Pro)\b"
    r"|\bmutant\b|\bmutation\b|\bmutagenes|\balanine scan"
    r")", re.I)
_QUANT = re.compile(
    r"(\bK[dD]\b|\bK\s?D\b|dissociation constant|\bddG\b|ΔΔG|ΔΔG|kcal\s?/\s?mol|"
    r"\bITC\b|isothermal titration|\bSPR\b|surface plasmon|cooperativit|\balpha\b|\bα\b|"
    r"\bnM\b|\b[muµ]M\b|\bKi\b|fold)", re.I)

# ------------------------------------------------------------------------------------------------
# The engine's own accuracy band -- READ, never typed
# ------------------------------------------------------------------------------------------------
#: One home for these figures is `protfep-benchmark-result.json`. They are loaded from it rather than
#: restated, so a re-run of the benchmark cannot leave a stale band sitting in this gate (CLAUDE.md
#: rule 1). The fallback constants exist ONLY so the gate logic is unit-testable offline and are
#: labelled as such in the artifact.
BENCH_RESULT = os.path.join(HERE, "protfep-benchmark-result.json")
ENGINE_BAND_FALLBACK = {
    "qualification_tolerance_kcal": 1.5,
    "hot_spot_replicate_sd_kcal": 1.077,
    "near_null_replicate_sd_kcal": 0.175,
    "_source": "fallback constants -- protfep-benchmark-result.json was not readable",
}


def engine_band(path=BENCH_RESULT):
    """The engine's demonstrated accuracy, read off the committed benchmark artifact.

    Returns a dict with the qualification tolerance and BOTH replicate SDs, because the whole point of
    Open decision 7's requirement is that a single 'accuracy' number does not exist for this engine --
    it is 6.2x different at the two ends of the benchmark set.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return dict(ENGINE_BAND_FALLBACK)

    band = {"_source": os.path.basename(path)}
    tol = doc.get("tolerance_kcal")
    rows = doc.get("scores") or doc.get("benchmarks") or doc.get("results") or {}
    if isinstance(rows, dict):
        rows = list(rows.values())
    sds = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        tol = tol or row.get("tolerance_kcal")
        sd = (row.get("calc_sd_kcal") if row.get("calc_sd_kcal") is not None
              else row.get("sd_kcal", row.get("replicate_sd_kcal", row.get("ddg_sd_kcal"))))
        ref = (row.get("ref_ddg_bind_kcal") if row.get("ref_ddg_bind_kcal") is not None
               else row.get("reference_ddg_kcal"))
        if sd is not None and ref is not None:
            sds.append((abs(float(ref)), float(sd)))
    if sds:
        sds.sort()
        band["near_null_replicate_sd_kcal"] = sds[0][1]
        band["hot_spot_replicate_sd_kcal"] = sds[-1][1]
        band["benchmark_effect_sizes_kcal"] = [s[0] for s in sds]
    else:
        band.update({k: v for k, v in ENGINE_BAND_FALLBACK.items() if k != "_source"})
        band["_note"] = ("per-benchmark SDs were not parseable from the artifact; fallback constants "
                         "used and flagged")
    band["qualification_tolerance_kcal"] = float(tol) if tol else 1.5
    band["_effect_size_dependent"] = True
    band["_why_two_numbers"] = (
        "between-replicate SD is effect-size dependent by ~6.2x across this engine's qualified set "
        "(hot spot vs near-null) while within-leg MBAR SEs are 0.05-0.13, so the scatter is "
        "setup/equilibration variance rather than sampling length. There is no single accuracy number "
        "and Open decision 7 forbids pretending there is one.")
    return band


def caveat():
    """The sentence any write-up of a pmx run MUST carry. One home, so it cannot be dropped.

    The program map records this instrument as PASSES. That word is true and incomplete, and the
    incompleteness is exactly the regime the selectivity route needs.
    """
    return ("pmx/GROMACS is demonstrated to SEE a large interface effect (barnase-barstar Y29A "
            "+4.42 +/- 1.08 vs a published +3.4) and demonstrated NOT to invent one (Y29F "
            "-0.370 +/- 0.175 vs -0.13). It is NOT demonstrated to resolve a paralogue-scale "
            "difference: no benchmark yet probes the ~1 kcal/mol regime, and between-replicate SD is "
            "6.2x larger at hot-spot scale than at near-null scale. A pass on the hot spot therefore "
            "licenses no claim about paralogue-scale resolution.")


# ------------------------------------------------------------------------------------------------
# Instrument A -- SKEMPI 2.0
# ------------------------------------------------------------------------------------------------
def skempi_scan(csv_text, pdbs=None, name_substrings=None):
    """Every SKEMPI record touching this system, by PDB and by protein NAME. Pure.

    THREE BUCKETS, AND THE DIFFERENCE BETWEEN THEM IS THE WHOLE POINT:

      `pdb_hits`         -- keyed to a deposited entry of THIS interface. On-interface by construction.
      `name_hits_paired` -- one partner is the TARGET arm (SMARCA/BRG/BRM) and the other is the E3 arm
                            (VHL/Elongin/Cul2). On-interface by identity even if curated against a
                            deposit this module does not list. These are the ones the name scan exists
                            to catch.
      `name_leads`       -- a single substring matched. A LEAD for a human to read, never a value: a
                            bromodomain is not this bromodomain, and a promiscuous substring matching
                            somewhere else in the database is exactly how the first version of this
                            gate returned PROCEED off an unrelated 2.048 kcal/mol record.

    Returns a dict. An unparseable or empty table is reported as a LOAD FAILURE and never as the
    finding that no record exists -- that distinction is the one that made this repo apply a card
    floor to a live lane on a misread (CLAUDE.md section 4).
    """
    import protfep_refcheck as rc

    pdbs = [p.upper() for p in (pdbs or CANDIDATE_PDBS)]
    names = [n.lower() for n in (name_substrings or CANDIDATE_PROTEIN_NAMES)]
    out = {"source": rc.SKEMPI_URL, "pdbs_queried": pdbs, "name_substrings_queried": names,
           "target_arm_names": TARGET_ARM_NAMES, "e3_arm_names": E3_ARM_NAMES,
           "n_rows_scanned": 0, "pdb_hits": [], "name_hits_paired": [], "name_leads": [],
           "errors": [], "loaded": False}

    rows, columns, errors = rc.parse_skempi(csv_text or "")
    out["n_rows_scanned"] = len(rows)
    out["errors"].extend(errors)
    if not rows:
        out["errors"].append(
            "SKEMPI parsed to ZERO rows -- the database did not load. This is a LOAD FAILURE, not the "
            "finding that no measured mutation exists for this interface.")
        return out
    if errors:
        return out
    out["loaded"] = True

    c_pdb, c_mut = columns["pdb"], columns["mutation"]
    c_kdm, c_kdw, c_t = columns["kd_mut"], columns["kd_wt"], columns["temperature"]
    # Protein-name columns are not load-bearing for parse_skempi, so resolve them leniently here.
    header = list(rows[0].keys())

    def _col(*cands):
        for c in cands:
            for actual in header:
                if actual.strip().lower() == c.lower():
                    return actual
        return None

    c_p1, c_p2 = _col("Protein 1", "Protein1"), _col("Protein 2", "Protein2")

    def _record(row, how):
        temp, assumed = rc.parse_temperature(row.get(c_t) if c_t else None)
        rec = {"pdb_entry": row.get(c_pdb), "mutation_cell": row.get(c_mut),
               "protein_1": row.get(c_p1) if c_p1 else None,
               "protein_2": row.get(c_p2) if c_p2 else None,
               "kd_mut_M": row.get(c_kdm), "kd_wt_M": row.get(c_kdw),
               "temperature_k": temp, "temperature_assumed": assumed, "matched_by": how}
        try:
            rec["ddg_kcal"] = round(rc.ddg_from_kd(row.get(c_kdm), row.get(c_kdw), temp), 3)
        except (TypeError, ValueError) as e:
            rec["ddg_kcal"] = None
            rec["ddg_unavailable_because"] = str(e)
        return rec

    def _arm(text, family):
        t = (text or "").lower()
        return [n for n in family if n in t]

    for row in rows:
        entry = str(row.get(c_pdb, "") or "").upper()
        if any(entry.startswith(p) for p in pdbs):
            out["pdb_hits"].append(_record(row, "pdb"))
            continue
        p1 = str(row.get(c_p1) or "") if c_p1 else ""
        p2 = str(row.get(c_p2) or "") if c_p2 else ""
        blob = (p1 + " " + p2).lower()
        if not blob.strip() or not any(n in blob for n in names):
            continue
        # PAIRED means the two partners are the two arms of THIS interface, in either order.
        paired = ((_arm(p1, TARGET_ARM_NAMES) and _arm(p2, E3_ARM_NAMES)) or
                  (_arm(p2, TARGET_ARM_NAMES) and _arm(p1, E3_ARM_NAMES)))
        rec = _record(row, "protein_name_paired" if paired else "protein_name_lead")
        rec["matched_substrings"] = sorted(set(_arm(blob, names)))
        (out["name_hits_paired"] if paired else out["name_leads"]).append(rec)

    out["n_pdb_hits"] = len(out["pdb_hits"])
    out["n_name_hits_paired"] = len(out["name_hits_paired"])
    out["n_name_leads"] = len(out["name_leads"])
    # Cap the emitted rows so one promiscuous name substring cannot bloat the artifact; the COUNTS
    # above are complete and are what the verdict reads. Leads are capped hardest because they are the
    # bucket that is allowed to be noisy -- their job is to be read, not to be counted.
    out["pdb_hits"] = out["pdb_hits"][:200]
    out["name_hits_paired"] = out["name_hits_paired"][:200]
    out["name_lead_complexes"] = sorted({
        "%s | %s / %s" % (r.get("pdb_entry"), r.get("protein_1"), r.get("protein_2"))
        for r in out["name_leads"]})[:100]
    out["name_leads"] = out["name_leads"][:60]
    return out


# ------------------------------------------------------------------------------------------------
# Instrument B -- Europe PMC
# ------------------------------------------------------------------------------------------------
def mutational_spans(text, max_spans=40):
    """Sentences carrying BOTH a mutation token and a measured-quantity token. Pure.

    Neither condition is sufficient alone -- see the module docstring. Returns raw sentences so a
    human re-reads the source rather than trusting a parse.
    """
    out = []
    for sent in re.split(r"(?<=[.!?])\s+", text or ""):
        s = sent.strip()
        if len(s) < 25 or len(s) > 700:
            continue
        if _MUT.search(s) and _QUANT.search(s):
            out.append(s)
    seen, uniq = set(), []
    for s in out:
        k = s[:160].lower()
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return uniq[:max_spans]


#: The papers a negative has to survive. These are the primary sources that WOULD carry an interface
#: mutational measurement if one existed: the paper the selectivity claim itself comes from, the two
#: earlier ternary-structure papers on the same arms, and the commentary that reviews the mechanism.
#: Named as PMCIDs so the read is reproducible, and every one is already cited elsewhere in this repo.
DECISIVE_PMCIDS = [
    ("PMC9551036", "Kofink et al. 2022 (ACBI2) -- the source of the Gln1469 selectivity claim"),
    ("PMC6600871", "Farnaby et al. 2019 (ACBI1) -- the earlier SMARCA2/4:VCB ternary structures"),
    ("PMC10344917", "Wurz et al. 2023 -- affinity/cooperativity across the same arms"),
    ("PMC9889305", "Wang & Zhou 2023 commentary -- 'A two-faced selectivity solution' on this mechanism"),
]

#: Raw tokens counted verbatim in each decisive full text. Counts, not judgements: a zero count for
#: `mutagenesis` in the paper that makes the selectivity claim is a fact a reader can check in seconds.
DEEP_TOKENS = ["1469", "Gln1469", "Q1469", "mutant", "mutation", "mutagenesis", "alanine scan",
               "SPR", "surface plasmon", "ITC", "isothermal titration", "KD", "Kd", "kcal/mol"]


def deep_read(pmcids=None, window=1, max_windows=25):
    """Every mention of a mutation in the DECISIVE papers, with context, regardless of co-located number.

    ★ WHY THIS EXISTS AND WHY THE QUERY LAYER IS NOT ENOUGH. `mutational_spans` requires a mutation
    token and a quantity token in the SAME sentence, which is the right filter for scanning hundreds of
    hits and the wrong one for concluding a negative -- a measurement split across two sentences would
    be invisible to it. An absent reading is not a reading of absence (CLAUDE.md section 4), so before
    this module says "no measured value exists", it reads the papers that would carry one and emits
    EVERY mutation mention with its neighbours, plus verbatim token counts. A human can then disagree
    with the conclusion by reading the same text, which is the only kind of negative worth publishing.
    """
    import selcal_reference_selectivity as srs

    out = []
    for pmcid, why in (pmcids or DECISIVE_PMCIDS):
        row = {"pmcid": pmcid, "why_decisive": why,
               "_source": "%s/%s/fullTextXML" % (srs.EPMC, pmcid),
               "fulltext_chars": 0, "token_counts": {}, "mutation_context_windows": [],
               "error": None}
        try:
            xml = srs.epmc_fulltext_xml(pmcid)
        except Exception as e:                                    # noqa: BLE001
            row["error"] = "%s: %s" % (type(e).__name__, e)
            out.append(row)
            continue
        if not xml:
            row["error"] = ("full text did not return -- an ABSENT reading, not an absence; this paper "
                            "cannot contribute to a negative until it is read")
            out.append(row)
            continue
        txt = srs._strip_tags(xml)
        row["fulltext_chars"] = len(txt)
        low = txt.lower()
        row["token_counts"] = {t: low.count(t.lower()) for t in DEEP_TOKENS}
        sents = re.split(r"(?<=[.!?])\s+", txt)
        for i, s in enumerate(sents):
            if not _MUT.search(s):
                continue
            lo, hi = max(0, i - window), min(len(sents), i + window + 1)
            row["mutation_context_windows"].append(" ".join(x.strip() for x in sents[lo:hi])[:1200])
            if len(row["mutation_context_windows"]) >= max_windows:
                break
        row["n_mutation_mentions"] = len(row["mutation_context_windows"])
        out.append(row)
    return out


#: An explicit point-mutation construct code: R69A, Q1469L, Y29F. Distinct from `_MUT`, which also
#: matches the words "mutant"/"mutation" and so fires on cancer genetics and reference titles.
_MUT_CODE = re.compile(r"\b([ACDEFGHIKLMNPQRSTVWY])(\d{2,4})([ACDEFGHIKLMNPQRSTVWY])\b")

#: Quantities that would make a mutation mention a MEASUREMENT rather than a construct description.
_MEASURED = re.compile(r"(\bK[dD]\b|\bK\s?D\b|\bITC\b|isothermal titration|\bSPR\b|surface plasmon|"
                       r"\bTR-?FRET\b|cooperativit|\balpha\b|\bα\b|\bIC\s?50\b|kcal\s?/\s?mol|"
                       r"dissociation constant)", re.I)


def near_misses(deep, window=2, max_per_paper=12):
    """Point mutations that WERE measured in the decisive papers -- surfaced, and NOT counted. Pure.

    ★ THE MOST USEFUL THING A NEGATIVE CAN CARRY IS THE NEAREST THING TO A POSITIVE. "No measured
    mutational value exists" invites the reasonable question "are you sure nobody has ever mutated
    anything at this interface?" -- and the honest answer is more interesting than the verdict: an
    interface point mutation HAS been measured here, on the OTHER arm and in a DIFFERENT quantity.
    Emitting it makes the negative checkable and stops the next session re-deriving it.

    A near miss is a context window carrying an explicit mutation CODE (R69A, not the word "mutant",
    which fires on cancer genetics) together with a measurement token. It is reported with the reason
    it does not satisfy G1, and the adjudication -- is this quantity a binding ddG? is it on the
    residue in question? -- is left to a human, exactly as the quoted-span rule requires.
    """
    out = []
    for d in deep or []:
        codes, rows = set(), []
        for w in d.get("mutation_context_windows") or []:
            found = {"".join(m) for m in _MUT_CODE.findall(w)}
            if not found or not _MEASURED.search(w):
                continue
            codes |= found
            rows.append({"mutation_codes": sorted(found), "quoted_window": w[:900]})
            if len(rows) >= max_per_paper:
                break
        if rows:
            out.append({
                "pmcid": d["pmcid"], "why_decisive": d.get("why_decisive"),
                "mutation_codes_seen": sorted(codes), "n_windows": len(rows), "windows": rows,
                "_why_this_is_not_a_reference": (
                    "a measured point mutation at this interface is NOT automatically the reference "
                    "this precheck needs. It qualifies only if BOTH hold, and both are human "
                    "judgements made against the quoted text: (a) it is on the residue whose "
                    "selectivity is being calibrated, and (b) the reported quantity is a binding ddG "
                    "or a Kd pair one is computable from. A cooperativity ratio, a TR-FRET IC50 shift "
                    "or a cellular DC50 is a different quantity, and converting one into an interface "
                    "binding ddG would fabricate a link this program does not have."),
            })
    return out


def epmc_probe(queries=None, page_size=8):
    """Run every query, pull open-access full text, and emit quoted mutational spans.

    Transport failures are RECORDED, never swallowed: a query that could not be run is an absent
    reading and must not be counted as a negative.
    """
    import selcal_reference_selectivity as srs

    results = []
    for q in (queries or QUERIES):
        row = {"tag": q["tag"], "why": q["why"], "query": q["query"],
               "_source": "%s/search?query=%s" % (srs.EPMC, q["query"]),
               "n_hits": None, "records": [], "error": None}
        try:
            hits = srs.epmc_search(q["query"], page_size=page_size)
        except Exception as e:                                    # noqa: BLE001 -- transport of any kind
            row["error"] = "%s: %s" % (type(e).__name__, e)
            results.append(row)
            continue
        row["n_hits"] = len(hits)
        for rec in hits:
            entry = {"title": rec.get("title"), "journal": (rec.get("journalInfo") or {}).get(
                "journal", {}).get("title") or rec.get("journalTitle"),
                "year": rec.get("pubYear"), "doi": rec.get("doi"), "pmid": rec.get("pmid"),
                "pmcid": rec.get("pmcid"), "isOpenAccess": rec.get("isOpenAccess")}
            spans = mutational_spans(rec.get("abstractText") or "")
            entry["abstract_mutational_spans"] = spans
            if rec.get("pmcid") and rec.get("isOpenAccess") == "Y":
                xml = srs.epmc_fulltext_xml(rec["pmcid"])
                if xml:
                    txt = srs._strip_tags(xml)
                    entry["fulltext_chars"] = len(txt)
                    entry["fulltext_mutational_spans"] = mutational_spans(txt)
                else:
                    entry["fulltext_chars"] = 0
                    entry["fulltext_unavailable"] = ("open-access flag set but fullTextXML did not "
                                                     "return -- an ABSENT reading, not an absence")
            row["records"].append(entry)
        results.append(row)
    return results


# ------------------------------------------------------------------------------------------------
# The gate
# ------------------------------------------------------------------------------------------------
def verdict(skempi, epmc, band=None, deep=None):
    """Apply Open decision 7's three conditions mechanically. Pure.

    Returns {"decision": ..., "gates": {...}, "sentence": ...}. The decision vocabulary is deliberately
    three-valued, because "we could not read the instruments" and "we read them and found nothing" are
    different facts and collapsing them is the exact error CLAUDE.md section 4 names.

      PROCEED             -- a measured, primary-source value exists AND clears the band.
      STOP_NO_REFERENCE   -- both instruments read cleanly and no measured value exists. Spend nothing.
      STOP_BAND           -- a value exists but is inside the engine's own accuracy band, so the run
                             could not distinguish a right answer from a wrong one (decision 7).
      UNDETERMINED        -- an instrument could not be read. NOT a negative; re-run it.
    """
    band = band or engine_band()
    gates, blockers = {}, []

    skempi_loaded = bool(skempi.get("loaded"))
    epmc_ok = [r for r in epmc if r.get("error") is None]
    epmc_failed = [r["tag"] for r in epmc if r.get("error")]

    if not skempi_loaded:
        blockers.append("SKEMPI did not load (%s)" % "; ".join(skempi.get("errors") or ["unknown"]))
    if not epmc_ok:
        blockers.append("no Europe PMC query completed")

    # ⚠ A NEGATIVE MUST SURVIVE THE PAPERS THAT WOULD CARRY THE POSITIVE. A search-shaped null across
    # queries is weaker than a read of the decisive sources, so an unread decisive paper BLOCKS the
    # STOP verdict rather than being quietly absorbed into it. This is the same rule as above, pointed
    # at ourselves: an absent reading is not a reading of absence.
    # It only blocks a NEGATIVE. A positive needs no deep read -- the measured value is already in
    # hand — so requiring one there would be ceremony rather than evidence.
    deep = deep if deep is not None else []
    unread = [d["pmcid"] for d in deep if d.get("error") or not d.get("fulltext_chars")]
    negative_blockers = []
    if not deep:
        negative_blockers.append("the decisive-paper deep read did not run")
    elif unread:
        negative_blockers.append("decisive papers not read: %s" % ", ".join(unread))

    # G1 -- is there a measured, primary-source mutational value ON THIS INTERFACE at all?
    #
    # ⚠ ONLY `pdb_hits` AND `name_hits_paired` COUNT. `name_leads` are a single promiscuous substring
    # match somewhere in a 7,000-row database and are leads for a human, not values — pooling them in
    # is what made the first run of this gate return PROCEED off an unrelated record (see skempi_scan).
    on_interface = (skempi.get("pdb_hits") or []) + (skempi.get("name_hits_paired") or [])
    skempi_measured = [r for r in on_interface if r.get("ddg_kcal") is not None]
    n_spans = sum(len(rec.get("fulltext_mutational_spans") or []) +
                  len(rec.get("abstract_mutational_spans") or [])
                  for row in epmc for rec in row.get("records") or [])
    gates["G1_measured_primary_source"] = {
        "requirement": ("a binding ddG (or a Kd pair it is computable from) for a single point mutation "
                        "at this interface, reported as a MEASUREMENT in a primary source"),
        "skempi_on_interface_records": len(on_interface),
        "skempi_records_with_computable_ddg": len(skempi_measured),
        "skempi_offinterface_name_leads": skempi.get("n_name_leads", 0),
        "epmc_candidate_sentences": n_spans,
        "decisive_papers_read": [{"pmcid": d["pmcid"], "chars": d.get("fulltext_chars"),
                                  "mutation_mentions": d.get("n_mutation_mentions"),
                                  "token_counts": d.get("token_counts")} for d in deep],
        "met": bool(skempi_measured),
        "measured_point_mutations_found_but_NOT_counted": [
            {"pmcid": n["pmcid"], "mutation_codes_seen": n["mutation_codes_seen"],
             "n_windows": n["n_windows"]} for n in near_misses(deep)],
        "_what_counts": ("a record keyed to a deposited entry of this interface, or one whose two named "
                         "partners ARE the two arms of it (target-side SMARCA/BRG/BRM against E3-side "
                         "VHL/Elongin/Cul2). A single-substring name match elsewhere in the database is "
                         "a LEAD and is reported in name_leads, never counted here."),
        "_why_spans_alone_do_not_meet_it": (
            "a quoted sentence is a lead, not a value. It meets G1 only after a human transcribes a "
            "specific number from it with the quote attached, which is the standing rule "
            "(selcal_reference_selectivity, extract_smarca2_ic50). Candidate sentences are emitted so "
            "that transcription is possible; the gate does not perform it."),
    }

    # G2 -- is the signal wider than the engine's band at that signal's own size?
    tol = float(band.get("qualification_tolerance_kcal", 1.5))
    values = [abs(r["ddg_kcal"]) for r in skempi_measured]
    biggest = max(values) if values else None
    gates["G2_signal_exceeds_band"] = {
        "requirement": ("Open decision 7: no accuracy band wider than the signal being calibrated. "
                        "|ddG_ref| must exceed the engine's demonstrated band at that effect size."),
        "engine_band_kcal": band,
        "largest_measured_ddg_found_kcal": biggest,
        "met": bool(biggest is not None and biggest > tol),
        "_the_hard_case": (
            "a paralogue-scale difference is expected around ~1 kcal/mol, which is BELOW the engine's "
            "%.1f kcal/mol qualification tolerance and inside its hot-spot replicate SD of %.3f. So even "
            "a real measured value at that size FAILS this gate until a wedge-sized benchmark exists. "
            "That is the gate working, not the gate being pedantic."
            % (tol, float(band.get("hot_spot_replicate_sd_kcal", 1.077)))),
    }

    # G3 -- the null-rejection rate, stated before the run rather than after it.
    gates["G3_null_rejection_stated_up_front"] = {
        "requirement": "what result would count as a refutation, written down before any spend",
        "statement": (
            "A pmx leg set on this mutation REFUTES the single-hydrogen-bond reading of SMARCA2/4 "
            "selectivity if the computed |ddG| is below the engine's near-null replicate SD (0.175 "
            "kcal/mol) at n>=3 with replicate-SD error bars -- i.e. the mutation is indistinguishable "
            "from the Y29F near-null control. It SUPPORTS it only if the computed ddG exceeds the "
            "measured reference by less than the qualification tolerance AND has the same sign. Any "
            "outcome between those is reported as UNRESOLVED, never as partial support."),
        "met": True,
        "_but": ("stating a rejection rule does not manufacture the reference value G1 needs. G3 is "
                 "necessary and nowhere near sufficient."),
    }

    if blockers:
        decision = "UNDETERMINED"
        sentence = ("UNDETERMINED -- an instrument could not be read (%s). This is an ABSENT READING, "
                    "not a reading of absence: re-run on a CI runner before drawing any conclusion, and "
                    "spend nothing in the meantime." % "; ".join(blockers))
    elif not gates["G1_measured_primary_source"]["met"] and negative_blockers:
        decision = "UNDETERMINED"
        sentence = ("UNDETERMINED -- no measured value was found, but the negative is not yet readable: "
                    "%s. A search-shaped null is weaker than a read of the sources that would carry the "
                    "positive, so this does NOT become STOP_NO_REFERENCE until they are read. Spend "
                    "nothing either way." % "; ".join(negative_blockers))
    elif not gates["G1_measured_primary_source"]["met"]:
        decision = "STOP_NO_REFERENCE"
        sentence = (
            "STOP -- NO MEASURED REFERENCE EXISTS. Both instruments read cleanly (%d SKEMPI rows "
            "scanned across %d deposited entries and %d protein-name patterns; %d of %d Europe PMC "
            "queries completed) and neither yields a measured binding ddG for a single point mutation "
            "at the SMARCA2/SMARCA4 - VCB interface (%d off-interface name LEADS were found and are "
            "listed for reading; a lead is not a value). The selectivity contact is documented "
            "STRUCTURALLY (a hydrogen bond seen in a crystal) and FUNCTIONALLY (cellular degradation "
            "DC50 ratios); neither is a measured interface mutational ddG, and converting a DC50 ratio "
            "into one would fabricate the quantitative link this program does not have. A pmx run here "
            "would therefore have NO known answer to be scored against -- it would be an experiment "
            "wearing a control's costume, which is the exact defect that cost this program three "
            "withdrawn selectivity claims. The %d decisive primary sources were READ IN FULL, not just "
            "searched, and their mutation mentions are emitted verbatim below so the negative can be "
            "disagreed with from the same text. SPEND NOTHING."
            % (skempi.get("n_rows_scanned", 0), len(skempi.get("pdbs_queried") or []),
               len(skempi.get("name_substrings_queried") or []), len(epmc_ok), len(epmc),
               skempi.get("n_name_leads", 0), len(deep)))
    elif not gates["G2_signal_exceeds_band"]["met"]:
        decision = "STOP_BAND"
        sentence = (
            "STOP -- a measured value exists but it is inside the engine's own accuracy band "
            "(largest |ddG| found %.3f kcal/mol against a %.1f kcal/mol qualification tolerance). "
            "Open decision 7 binds: no accuracy band wider than the signal being calibrated. The run "
            "could not distinguish a correct answer from an incorrect one, so it buys nothing."
            % (biggest or 0.0, tol))
    else:
        decision = "PROCEED"
        sentence = (
            "PROCEED -- a measured, primary-source mutational ddG exists on this interface and exceeds "
            "the engine's demonstrated band (largest |ddG| %.3f kcal/mol vs %.1f kcal/mol tolerance). "
            "Transcribe the specific record into the benchmark by hand, with its citation, before any "
            "leg is launched." % (biggest or 0.0, tol))

    return {"decision": decision, "gates": gates, "sentence": sentence,
            "epmc_queries_that_failed": epmc_failed,
            "caveat_that_must_travel_with_any_result": caveat()}


def run(out_path=OUT, offline=False, skempi_csv=None):
    """Fetch both instruments, apply the gate, write the artifact."""
    doc = {
        "_what": ("THE $0 PRECHECK required before any pmx/GROMACS spend on the SMARCA2/4 selectivity "
                  "contact. STRATEGY.md makes that spend 'conditional on a measured mutational value "
                  "existing in a primary source, which is a $0 check that must precede any spend "
                  "(Open decision 7)'. This artifact is that check."),
        "_this_is_evidence_not_a_conclusion": (
            "Every SKEMPI row is recomputed from the deposited Kd pair, never read off a remembered "
            "table cell. Every Europe PMC field is an API response or a verbatim sentence from an "
            "open-access full text. Nothing here is curated, averaged or interpreted; the verdict is a "
            "mechanical function of the two, printed beside them."),
        "_decision_7": ("STRATEGY Open decision 7 binds every future calibrator: 'no accuracy band "
                        "wider than the signal being calibrated, and a stated null-rejection rate up "
                        "front.' Both are checked below, and neither is waivable here."),
        "target": TARGET,
        "engine_band": engine_band(),
        "caveat_that_must_travel_with_any_result": caveat(),
    }

    if offline:
        doc["skempi"] = {"loaded": False, "errors": ["--offline: no fetch attempted"],
                         "n_rows_scanned": 0, "pdbs_queried": CANDIDATE_PDBS,
                         "name_substrings_queried": CANDIDATE_PROTEIN_NAMES,
                         "pdb_hits": [], "name_hits": []}
        doc["europe_pmc"] = []
        doc["deep_read"] = []
        doc["near_misses"] = []
    else:
        import protfep_refcheck as rc
        try:
            text = skempi_csv if skempi_csv is not None else rc.fetch_skempi(
                cache_path=os.environ.get("SKEMPI_CACHE"))
        except Exception as e:                                    # noqa: BLE001
            text = ""
            doc.setdefault("_transport_errors", []).append(
                "SKEMPI fetch failed: %s: %s" % (type(e).__name__, e))
        doc["skempi"] = skempi_scan(text)
        doc["europe_pmc"] = epmc_probe()
        doc["deep_read"] = deep_read()
        doc["near_misses"] = near_misses(doc["deep_read"])

    doc["verdict"] = verdict(doc["skempi"], doc["europe_pmc"], band=doc["engine_band"],
                             deep=doc.get("deep_read"))

    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(doc, indent=1) + "\n")
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="$0 precheck: does a measured mutational ddG exist for the "
                                             "SMARCA2/4 selectivity contact?")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--offline", action="store_true",
                    help="exercise the gate logic with no network. NEVER emits a scientific verdict: "
                         "the decision is UNDETERMINED by construction.")
    args = ap.parse_args(argv)

    doc = run(out_path=args.out, offline=args.offline)
    v = doc["verdict"]
    print(json.dumps(v, indent=2))
    print("\nDECISION: %s" % v["decision"], file=sys.stderr)
    print(v["sentence"], file=sys.stderr)
    print("\nCAVEAT: %s" % doc["caveat_that_must_travel_with_any_result"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
