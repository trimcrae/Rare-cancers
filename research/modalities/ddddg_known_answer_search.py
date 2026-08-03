#!/usr/bin/env python3
"""ROADMAP ROW 27 — the two $0 searches for a PARALOGUE-SCALE KNOWN ANSWER for a ligand-side ddddG.

    C01a  the ligand-side wedge-band scan: ChEMBL (+ BindingDB confirmation) joined against the PDB,
          for the shape *two homologous proteins x a matched congeneric ligand pair x FOUR measured
          affinities x structures on both arms*, with the between-protein double difference in the
          paralogue-scale band.
    C01b  the CREBBP/BRD4 congeneric-analogue precheck: does a measured congeneric pair exist ACROSS
          the designated binary control's two arms? Returns a reference or STOP_NO_REFERENCE.

WHAT IS ACTUALLY BEING DECIDED
------------------------------
The program's central gap (roadmap section 3.2) is that **no instrument here is validated at ~1
kcal/mol between near-identical proteins**. `instrument-options.md` section 2 argues that a ligand-side
double difference is the best-conditioned candidate instrument -- and that it does NOT inherit `V6`'s
within-pocket validation, because `err(V6)` and `err(ddddG)` are different linear combinations of
DISJOINT error terms. So ddddG needs its OWN known-answer test, whose shape is exactly specifiable:

    a public pair of homologous proteins + a matched congeneric ligand pair + FOUR measured
    affinities + a structural basis on both arms, scored as ddddG_calc vs ddddG_exp.

These two searches decide whether such a system can be BOUGHT. They decide nothing else. In
particular:

  ⛔ A PROCEED HERE RAISES NO CEILING. It says a benchmark EXISTS, not that any instrument passed it.
     A ddddG route needs its own validation and inherits none (roadmap section 3.4 fact 3).
  ⛔ A STOP_NO_REFERENCE IS A RESULT, NOT A FAILURE. The pmx arm already demonstrated that a refusal
     on evidence is better than a budget hold, because a nod cannot reverse it.

WHY NAME MATCHING IS NOT ALLOWED TO ESTABLISH ANYTHING
------------------------------------------------------
`pmx_mutation_reference` first returned a FALSE PROCEED off a promiscuous substring: a SOCS2-EloBC
record at 2.048 kcal/mol that a protein-name pattern matched somewhere else in a 7,085-row database
entirely. The equivalent trap here has three heads, and each is closed by a MEASUREMENT rather than
by a string:

  (1) "these two proteins are homologous"  -> NEVER from a shared family name or a shared ChEMBL
      protein class. Sequence identity is COMPUTED by alignment between the two targets' own ChEMBL
      component sequences, and the number is printed beside every candidate. The class grouping is
      used only as a cheap prefilter, and a prefilter can only lose candidates, never admit one.
  (2) "these two ligands are congeneric"   -> NEVER from a shared compound-series name or a shared
      prefix. Identical Bemis-Murcko scaffold, Morgan-fingerprint Tanimoto and heavy-atom delta are
      computed with RDKit from the deposited SMILES.
  (3) "this target IS that protein"        -> NEVER from `pref_name`. Targets are resolved through
      the UniProt ACCESSION carried in their ChEMBL target_components, and the accession is echoed.

Every one of the three is recorded per candidate, so a reader can reject a candidate this module
accepted without re-running anything.

THE GATE, PRE-REGISTERED (roadmap Open decision 7: no accuracy band wider than the signal being
calibrated, and a stated null-rejection rate up front)
-------------------------------------------------------------------------------------------------
    A1  homology MEASURED by alignment, >= PREREG identity floor
    A2  FOUR measured affinities, all ChEMBL binding assays with a pchembl value, `standard_relation`
        '=', and the SAME standard_type across all four
    A3  congeneric BY STRUCTURE (RDKit), not by name
    A4  |ddddG_exp| inside the pre-registered paralogue-scale search band -- and separately graded
        against the ENGINE band read out of instrument-options.json, because a reference smaller
        than the engine's own demonstrated error cannot distinguish a right answer from a wrong one
    A5  an experimental HOLO PDB entry on EACH arm, fetched live from RCSB
    A6  the null-rejection rule, stated before any spend

    PROCEED / STOP_BAND / STOP_NO_REFERENCE / UNDETERMINED -- and a STOP is only reachable when every
    instrument READ CLEANLY. A search-shaped null across a scan that hit transport errors is
    UNDETERMINED, never STOP: an absent reading is not a reading of absence (CLAUDE.md section 4).

USAGE (CI; the dev sandbox's egress proxy reaches none of these hosts)
    python3 ddddg_known_answer_search.py c01b                  # the CREBBP/BRD4 precheck
    python3 ddddg_known_answer_search.py c01a --stage all      # the wide scan, staged + checkpointed
    python3 ddddg_known_answer_search.py c01a --stage universe # one stage at a time
    python3 ddddg_known_answer_search.py c01b --offline        # gate logic only; UNDETERMINED
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_C01A = os.path.join(HERE, "ddddg-benchmark-scan.json")
OUT_C01B = os.path.join(HERE, "ddddg-crebbp-brd4-precheck.json")
CKPT = os.environ.get("DDDDG_CKPT", os.path.join(HERE, "_ddddg_ckpt"))

UA = {"User-Agent": "rare-cancers-ddddg-search/1.0 (research; github.com/trimcrae/Rare-cancers)"}

CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"
RCSB_SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
BINDINGDB = "https://bindingdb.org/axis2/services/BDBService/getLigandsByUniprots"

#: RT at 298.15 K in kcal/mol, and the conversion from a log10 affinity unit to kcal/mol.
RT_KCAL = 0.0019872041 * 298.15
LOG10_TO_KCAL = math.log(10.0) * RT_KCAL          # 1.3642 kcal/mol per pChEMBL unit

# ---------------------------------------------------------------------------------------------------
# PRE-REGISTRATION. Every threshold below is fixed before a single value is fetched and is echoed into
# both artifacts beside the result, so a reader can check that no cut was chosen after seeing data.
# ---------------------------------------------------------------------------------------------------
PREREG = {
    "identity_min_percent": 40.0,
    "_why_identity": ("'homologous' has to be a measured quantity or it is a family name. 40% pairwise "
                      "identity is the conventional floor for confident homology and is applied to "
                      "the ChEMBL component sequences themselves. NOTE this is DELIBERATELY LOOSER "
                      "than the NR4A paralogue case the instrument is wanted for -- a benchmark that "
                      "is only 40% identical is a weaker analogue than one at 80%, so identity is "
                      "reported per candidate and never collapsed into a pass/fail alone."),
    "mcs_fraction_min": 0.70,
    "tanimoto_reported_but_not_gating": True,
    "heavy_atom_delta_max": 6,
    "require_identical_murcko_scaffold": True,
    "_why_congeneric": ("a matched congeneric pair is the whole premise of the double difference: it "
                        "is what makes the ligand and atom-mapping error terms cancel ALGEBRAICALLY "
                        "(instrument-options.md section 2.1). Two unrelated actives measured on both "
                        "proteins would give a number and not a benchmark."),
    "_why_mcs_and_not_tanimoto_alone": (
        "⚠ THE PRIMARY STRUCTURAL CRITERION IS THE MCS FRACTION, NOT THE TANIMOTO, AND THE REASON IS "
        "A SIZE BIAS THAT WOULD HAVE BEEN INVISIBLE. A Morgan-fingerprint Tanimoto falls as molecules "
        "get smaller for a FIXED chemical difference: measured here, acetaminophen -> its propionyl "
        "analogue (one heavy atom, identical Murcko scaffold, unambiguously congeneric) scores 0.593, "
        "and toluene -> ethylbenzene scores 0.389, while a 40-heavy-atom drug pair differing by the "
        "same single methyl scores 0.847. A 0.60 Tanimoto floor would therefore have silently "
        "excluded small-molecule congeneric series from the scan and reported the result as an "
        "absence of references rather than as a filter. The MCS fraction -- shared maximum common "
        "substructure as a fraction of the SMALLER molecule -- is size-robust and is also the thing "
        "a relative FEP actually needs: a small perturbation on a large common core. Tanimoto is "
        "still computed and printed on every candidate, and retained as a loose sanity floor only."),
    "band_kcal": [0.5, 2.0],
    "_why_band": ("the paralogue-scale wedge band C01a is specified against "
                  "(instrument-options.md section 2.5). Below it the effect is not resolvable; above "
                  "it the system is a hot spot and brackets the regime instead of covering it -- the "
                  "exact defect that leaves V10's qualified set unable to speak to paralogue scale."),
    "engine_band_kcal_fallback": 0.61,
    "_why_engine_band": ("Open decision 7: no accuracy band wider than the signal being calibrated. "
                         "The engine that would run a ddddG is the same relative-FEP machinery whose "
                         "known-answer test V6 passed at 0.61 kcal/mol absolute error, so a reference "
                         "at or below that cannot distinguish a right answer from a wrong one. READ "
                         "from instrument-options.json rather than typed -- the fallback is used only "
                         "when that artifact is unreadable, and it is flagged when it is."),
    "min_pchembl_activities_per_target": 20,
    "assay_type": "B",
    "standard_relation": "=",
    "allowed_standard_types": ["Ki", "Kd", "IC50"],
    "_why_same_type_across_all_four": (
        "a Ki on one arm against an IC50 on the other is not a double difference, it is two "
        "different quantities subtracted. ChEMBL's pchembl_value normalises the LOG but not the "
        "OBSERVABLE, so requiring one standard_type across all four values is the only way the "
        "cancellation the instrument depends on is real."),
    "kmer_prefilter_k": 4,
    "kmer_prefilter_containment_min": 0.15,
    "_why_prefilter": ("an all-vs-all alignment over every human single-protein ChEMBL target is "
                       "wasteful, so a 4-mer containment prefilter selects which pairs get aligned. "
                       "A PREFILTER CAN ONLY LOSE CANDIDATES, NEVER ADMIT ONE -- every surviving "
                       "pair is still confirmed by a real alignment, and the number of pairs the "
                       "prefilter dropped is reported so the loss is visible."),
}


def null_rejection_rule():
    """A6 -- what result would count as a refutation, written down before any spend. One home."""
    return ("A ddddG leg-pair run on a system this search returns REFUTES the claim that the "
            "relative-FEP machinery resolves a paralogue-scale between-protein difference if the "
            "computed |ddddG_calc - ddddG_exp| exceeds the reference's own magnitude at n>=3 "
            "replicates with replicate-SD error bars -- i.e. the calculation is no better than "
            "reporting zero. It SUPPORTS that claim only if the computed value has the SAME SIGN as "
            "the reference AND |ddddG_calc - ddddG_exp| is below the engine's demonstrated band. "
            "Anything between those is reported as UNRESOLVED, never as partial support. A negative "
            "control -- a matched pair expected to show NO selectivity shift -- must ship with the "
            "benchmark; without it the instrument has no null.")


def caveat():
    """The sentence any use of either artifact MUST carry. One home, so it cannot be dropped."""
    return ("Finding a benchmark is not passing one. A system returned here supplies a KNOWN ANSWER "
            "at paralogue scale; it says nothing about whether this program's machinery recovers it, "
            "and it raises no claim ceiling (roadmap section 2.3). Two scope facts travel with any "
            "candidate: (a) V6's validation covers the am1bcc BINARY lane only, so a benchmark must "
            "be run in the lane it will be used in or the charge model pinned across benchmark and "
            "application (instrument-options.md section 2.6); and (b) a benchmark pair's sequence "
            "identity is reported per candidate precisely because a 40%-identical pair is a weaker "
            "analogue for the NR4A paralogues than an 80%-identical one.")


def engine_band(path=None):
    """The engine's demonstrated accuracy, READ off instrument-options.json rather than typed.

    Its one home is `the_regime_gap.what_brackets_it[] -> instrument V6 -> passed_at`, which reads
    '0.61 kcal/mol absolute error on TYK2 ejm_31->ejm_42'. Parsing the number out of the sentence
    keeps a single home for it; a fallback constant exists only so the gate is unit-testable and is
    FLAGGED in the artifact whenever it is used.
    """
    path = path or os.path.join(HERE, "instrument-options.json")
    out = {"_source": os.path.basename(path)}
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        for row in (doc.get("the_regime_gap") or {}).get("what_brackets_it") or []:
            if row.get("instrument") == "V6":
                m = re.search(r"([0-9]*\.?[0-9]+)\s*kcal/mol", row.get("passed_at") or "")
                if m:
                    out["band_kcal"] = float(m.group(1))
                    out["quoted"] = row.get("passed_at")
                    out["scope"] = row.get("why_it_does_not_close_the_gap")
                    out["home"] = row.get("home")
                    return out
    except (OSError, ValueError, TypeError) as e:
        out["_read_error"] = "%s: %s" % (type(e).__name__, e)
    out["band_kcal"] = float(PREREG["engine_band_kcal_fallback"])
    out["_fallback_used"] = ("instrument-options.json did not yield V6's passed_at figure; the "
                             "fallback constant was used and this run's STOP_BAND grading must be "
                             "re-checked against the real artifact")
    return out


# ---------------------------------------------------------------------------------------------------
# Transport. Every failure is RECORDED, never swallowed -- a query that could not run is an absent
# reading and may not be counted toward a negative.
# ---------------------------------------------------------------------------------------------------
class Transport:
    def __init__(self, delay=0.12):
        self.delay = delay
        self.errors = []
        self.n_calls = 0

    def get_json(self, url, timeout=120, tries=4):
        last = None
        for i in range(tries):
            try:
                self.n_calls += 1
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                time.sleep(self.delay)
                return json.loads(body)
            except Exception as e:                                # noqa: BLE001
                last = e
                time.sleep(min(2 ** i, 8))
        self.errors.append({"url": url[:300], "error": "%s: %s" % (type(last).__name__, last)})
        return None

    def post_json(self, url, payload, timeout=120, tries=3):
        last = None
        data = json.dumps(payload).encode()
        h = dict(UA)
        h["Content-Type"] = "application/json"
        for i in range(tries):
            try:
                self.n_calls += 1
                req = urllib.request.Request(url, data=data, headers=h)
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                time.sleep(self.delay)
                return json.loads(body)
            except urllib.error.HTTPError as e:
                if e.code == 204:                                 # RCSB: a valid "no hits"
                    return {"total_count": 0, "result_set": []}
                last = e
                time.sleep(min(2 ** i, 8))
            except Exception as e:                                # noqa: BLE001
                last = e
                time.sleep(min(2 ** i, 8))
        self.errors.append({"url": url[:200], "error": "%s: %s" % (type(last).__name__, last)})
        return None


# ---------------------------------------------------------------------------------------------------
# ChEMBL
# ---------------------------------------------------------------------------------------------------
def chembl_targets_by_accession(tp, accession):
    """Every human SINGLE PROTEIN ChEMBL target whose component carries this UniProt accession.

    ⚠ Resolution is by ACCESSION, never by pref_name. That is trap (3) in the module docstring.
    """
    url = ("%s/target.json?target_components__accession=%s&limit=100"
           % (CHEMBL, urllib.parse.quote(accession)))
    doc = tp.get_json(url)
    out = []
    for t in (doc or {}).get("targets", []):
        accs = sorted({c.get("accession") for c in t.get("target_components") or []
                       if c.get("accession")})
        out.append({"target_chembl_id": t.get("target_chembl_id"),
                    "pref_name": t.get("pref_name"),
                    "target_type": t.get("target_type"),
                    "organism": t.get("organism"),
                    "accessions": accs,
                    "resolved_by": "target_components__accession=%s" % accession})
    return out


def chembl_activity_count(tp, target_id):
    url = ("%s/activity.json?target_chembl_id=%s&pchembl_value__isnull=false&assay_type=%s"
           "&limit=1&only=molecule_chembl_id" % (CHEMBL, target_id, PREREG["assay_type"]))
    doc = tp.get_json(url)
    if doc is None:
        return None
    return ((doc.get("page_meta") or {}).get("total_count"))


ACT_FIELDS = ("molecule_chembl_id,standard_type,standard_relation,standard_value,standard_units,"
              "pchembl_value,assay_chembl_id,target_chembl_id,assay_type,document_chembl_id")


def chembl_activities(tp, target_id, cap=20000):
    """All binding activities with a pchembl value for one target. Paged, field-restricted."""
    rows, offset = [], 0
    while offset < cap:
        url = ("%s/activity.json?target_chembl_id=%s&pchembl_value__isnull=false&assay_type=%s"
               "&limit=1000&offset=%d&only=%s"
               % (CHEMBL, target_id, PREREG["assay_type"], offset, ACT_FIELDS))
        doc = tp.get_json(url)
        if doc is None:
            return rows, False
        batch = doc.get("activities") or []
        rows.extend(batch)
        total = (doc.get("page_meta") or {}).get("total_count") or 0
        offset += 1000
        if offset >= total or not batch:
            break
    return rows, True


def chembl_smiles(tp, molecule_ids, batch=40):
    out = {}
    ids = sorted(set(molecule_ids))
    ok = True
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        url = ("%s/molecule.json?molecule_chembl_id__in=%s&limit=%d"
               "&only=molecule_chembl_id,molecule_structures,pref_name"
               % (CHEMBL, ",".join(chunk), len(chunk)))
        doc = tp.get_json(url)
        if doc is None:
            ok = False
            continue
        for mol in doc.get("molecules") or []:
            s = (mol.get("molecule_structures") or {}).get("canonical_smiles")
            if s:
                out[mol["molecule_chembl_id"]] = {"smiles": s, "pref_name": mol.get("pref_name")}
    return out, ok


def chembl_all_human_components(tp, cap=40000):
    """Every human ChEMBL target component WITH ITS SEQUENCE. ~10-20 paged calls, not thousands."""
    out, offset = {}, 0
    while offset < cap:
        url = ("%s/target_component.json?organism=Homo%%20sapiens&limit=1000&offset=%d"
               "&only=component_id,accession,sequence,component_type,description"
               % (CHEMBL, offset))
        doc = tp.get_json(url)
        if doc is None:
            return out, False
        batch = doc.get("target_components") or []
        for c in batch:
            if c.get("accession") and c.get("sequence"):
                out[c["accession"]] = {"component_id": c.get("component_id"),
                                       "sequence": c["sequence"],
                                       "description": c.get("description")}
        total = (doc.get("page_meta") or {}).get("total_count") or 0
        offset += 1000
        if offset >= total or not batch:
            break
    return out, True


def chembl_human_single_protein_targets(tp, cap=40000):
    out, offset = [], 0
    while offset < cap:
        url = ("%s/target.json?target_type=SINGLE%%20PROTEIN&organism=Homo%%20sapiens"
               "&limit=1000&offset=%d&only=target_chembl_id,pref_name,target_components,species_group_flag"
               % (CHEMBL, offset))
        doc = tp.get_json(url)
        if doc is None:
            return out, False
        batch = doc.get("targets") or []
        for t in batch:
            accs = sorted({c.get("accession") for c in t.get("target_components") or []
                           if c.get("accession")})
            if len(accs) != 1:
                continue                                   # a single-protein target has exactly one
            out.append({"target_chembl_id": t.get("target_chembl_id"),
                        "pref_name": t.get("pref_name"), "accession": accs[0]})
        total = (doc.get("page_meta") or {}).get("total_count") or 0
        offset += 1000
        if offset >= total or not batch:
            break
    return out, True


# ---------------------------------------------------------------------------------------------------
# Homology -- MEASURED, never assumed (trap 1)
# ---------------------------------------------------------------------------------------------------
def kmer_set(seq, k):
    s = (seq or "").upper()
    return {s[i:i + k] for i in range(max(0, len(s) - k + 1))}


def kmer_containment(a, b):
    """|A n B| / min(|A|,|B|) -- a cheap upper-bound-ish proxy used ONLY as a prefilter."""
    if not a or not b:
        return 0.0
    return len(a & b) / float(min(len(a), len(b)))


def pairwise_identity(seq_a, seq_b):
    """Percent identity from a real global alignment. Returns (percent, method).

    Biopython's PairwiseAligner when available (C-accelerated, BLOSUM62-style global); otherwise a
    pure-Python banded Needleman-Wunsch so the module never silently degrades to a string heuristic.
    """
    try:
        from Bio import Align                                     # noqa: PLC0415

        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.open_gap_score = -11
        aligner.extend_gap_score = -1
        try:
            from Bio.Align import substitution_matrices           # noqa: PLC0415
            aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
        except Exception:                                         # noqa: BLE001
            aligner.match_score, aligner.mismatch_score = 1, -1
        aln = aligner.align(seq_a, seq_b)[0]
        a, b = str(aln[0]), str(aln[1])
        aligned = sum(1 for x, y in zip(a, b) if x != "-" and y != "-")
        ident = sum(1 for x, y in zip(a, b) if x == y and x != "-")
        if not aligned:
            return 0.0, "biopython-global"
        return 100.0 * ident / aligned, "biopython-global"
    except Exception:                                             # noqa: BLE001
        return _nw_identity(seq_a, seq_b), "pure-python-nw"


def _nw_identity(a, b, band=None):
    """Fallback global alignment identity. Simple, correct, slow -- only for small candidate sets."""
    n, m = len(a), len(b)
    if not n or not m:
        return 0.0
    band = band or max(64, abs(n - m) + 64)
    NEG = -10 ** 9
    prev = [0] * (m + 1)
    prev_id = [0] * (m + 1)
    prev_al = [0] * (m + 1)
    for j in range(1, m + 1):
        prev[j] = -j
    for i in range(1, n + 1):
        cur = [NEG] * (m + 1)
        cur_id = [0] * (m + 1)
        cur_al = [0] * (m + 1)
        cur[0] = -i
        lo, hi = max(1, i - band), min(m, i + band)
        for j in range(lo, hi + 1):
            diag = prev[j - 1] + (1 if a[i - 1] == b[j - 1] else -1)
            up = prev[j] - 1
            left = cur[j - 1] - 1 if j - 1 >= lo - 1 else NEG
            best = max(diag, up, left)
            cur[j] = best
            if best == diag:
                cur_id[j] = prev_id[j - 1] + (1 if a[i - 1] == b[j - 1] else 0)
                cur_al[j] = prev_al[j - 1] + 1
            elif best == up:
                cur_id[j], cur_al[j] = prev_id[j], prev_al[j]
            else:
                cur_id[j], cur_al[j] = cur_id[j - 1], cur_al[j - 1]
        prev, prev_id, prev_al = cur, cur_id, cur_al
    return 100.0 * prev_id[m] / prev_al[m] if prev_al[m] else 0.0


# ---------------------------------------------------------------------------------------------------
# Congeneric -- MEASURED by structure, never by name (trap 2)
# ---------------------------------------------------------------------------------------------------
def congeneric_report(smiles_a, smiles_b, prereg=None):
    """Is this a matched congeneric pair? RDKit; returns a dict with every computed quantity.

    RDKit missing is reported as `available: False` and BLOCKS a positive -- it never degrades to a
    string comparison, because a string comparison is exactly trap 2.
    """
    prereg = prereg or PREREG
    out = {"smiles_a": smiles_a, "smiles_b": smiles_b, "available": False}
    try:
        from rdkit import Chem, RDLogger                          # noqa: PLC0415
        from rdkit.Chem import rdFingerprintGenerator             # noqa: PLC0415
        from rdkit.Chem.Scaffolds import MurckoScaffold           # noqa: PLC0415
        RDLogger.DisableLog("rdApp.*")
    except Exception as e:                                        # noqa: BLE001
        out["error"] = "rdkit unavailable: %s" % e
        return out
    ma, mb = Chem.MolFromSmiles(smiles_a or ""), Chem.MolFromSmiles(smiles_b or "")
    if ma is None or mb is None:
        out["error"] = "one or both SMILES did not parse"
        out["available"] = True
        out["is_congeneric"] = False
        return out
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fa, fb = gen.GetFingerprint(ma), gen.GetFingerprint(mb)
    from rdkit import DataStructs                                 # noqa: PLC0415
    tan = float(DataStructs.TanimotoSimilarity(fa, fb))
    sa = Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(ma))
    sb = Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(mb))
    ha, hb = ma.GetNumHeavyAtoms(), mb.GetNumHeavyAtoms()
    same_scaffold = bool(sa and sa == sb)
    identical = Chem.MolToSmiles(ma) == Chem.MolToSmiles(mb)

    # The PRIMARY structural criterion: shared maximum common substructure as a fraction of the
    # smaller molecule. Size-robust where a fingerprint Tanimoto is not -- see PREREG.
    mcs_atoms, mcs_frac, mcs_note = None, None, None
    try:
        from rdkit.Chem import rdFMCS                             # noqa: PLC0415
        res = rdFMCS.FindMCS([ma, mb], timeout=5, ringMatchesRingOnly=True,
                             completeRingsOnly=False,
                             atomCompare=rdFMCS.AtomCompare.CompareElements,
                             bondCompare=rdFMCS.BondCompare.CompareAny)
        if res and not res.canceled and res.numAtoms:
            mcs_atoms = int(res.numAtoms)
            mcs_frac = round(mcs_atoms / float(min(ha, hb) or 1), 4)
        elif res and res.canceled:
            mcs_note = ("MCS search hit its 5 s timeout -- an ABSENT reading of the MCS, not a "
                        "finding that the two molecules share no core. This candidate cannot be "
                        "accepted on structure and is reported so a human can look.")
    except Exception as e:                                        # noqa: BLE001
        mcs_note = "MCS unavailable: %s" % e

    out.update({
        "available": True,
        "tanimoto_morgan_r2_2048": round(tan, 4),
        "murcko_scaffold_a": sa, "murcko_scaffold_b": sb,
        "identical_murcko_scaffold": same_scaffold,
        "heavy_atoms_a": ha, "heavy_atoms_b": hb, "heavy_atom_delta": abs(ha - hb),
        "mcs_heavy_atoms": mcs_atoms, "mcs_fraction_of_smaller": mcs_frac, "mcs_note": mcs_note,
        "identical_molecules": identical,
        "is_congeneric": bool(
            not identical and same_scaffold
            and mcs_frac is not None and mcs_frac >= prereg["mcs_fraction_min"]
            and abs(ha - hb) <= prereg["heavy_atom_delta_max"]),
        "_criteria": {"mcs_fraction_min": prereg["mcs_fraction_min"],
                      "tanimoto_is_reported_not_gating": True,
                      "heavy_atom_delta_max": prereg["heavy_atom_delta_max"],
                      "require_identical_murcko_scaffold": True},
    })
    return out


# ---------------------------------------------------------------------------------------------------
# The affinity arithmetic
# ---------------------------------------------------------------------------------------------------
def _median(xs):
    s = sorted(xs)
    n = len(s)
    if not n:
        return None
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def index_activities(rows, allowed_types=None, relation=None):
    """(target, molecule, standard_type) -> {pchembl values, assays}. Pure.

    Only rows that are a MEASUREMENT of the kind the double difference needs survive: an exact
    relation, a pchembl value, and one of the allowed standard types. A '>' or '<' row is a bound,
    not a value, and subtracting bounds would fabricate a difference.
    """
    allowed = set(allowed_types or PREREG["allowed_standard_types"])
    rel = relation or PREREG["standard_relation"]
    idx = {}
    for r in rows:
        st = r.get("standard_type")
        if st not in allowed:
            continue
        if (r.get("standard_relation") or "").strip() != rel:
            continue
        try:
            p = float(r.get("pchembl_value"))
        except (TypeError, ValueError):
            continue
        key = (r.get("target_chembl_id"), r.get("molecule_chembl_id"), st)
        slot = idx.setdefault(key, {"pchembl": [], "assays": set(), "documents": set()})
        slot["pchembl"].append(p)
        if r.get("assay_chembl_id"):
            slot["assays"].add(r["assay_chembl_id"])
        if r.get("document_chembl_id"):
            slot["documents"].add(r["document_chembl_id"])
    return idx


def measurement(idx, target, molecule, std_type):
    slot = idx.get((target, molecule, std_type))
    if not slot:
        return None
    vals = slot["pchembl"]
    return {"pchembl_median": round(_median(vals), 3), "n_measurements": len(vals),
            "pchembl_min": round(min(vals), 3), "pchembl_max": round(max(vals), 3),
            "pchembl_spread": round(max(vals) - min(vals), 3),
            "assay_chembl_ids": sorted(slot["assays"])[:12],
            "document_chembl_ids": sorted(slot["documents"])[:12],
            "standard_type": std_type}


def ddddg_from_four(m_dA, m_d0A, m_dB, m_d0B):
    """ddddG in kcal/mol from four pChEMBL measurements. Pure, and the sign convention is stated.

        dG_bind        = -2.303 RT * pChEMBL
        ddG(d0->d | P) = dG(d,P) - dG(d0,P)          = -2.303 RT (p_dP - p_d0P)
        ddddG          = ddG(...|A) - ddG(...|B)
    """
    ddg_a = -LOG10_TO_KCAL * (m_dA["pchembl_median"] - m_d0A["pchembl_median"])
    ddg_b = -LOG10_TO_KCAL * (m_dB["pchembl_median"] - m_d0B["pchembl_median"])
    return {
        "ddG_arm_a_kcal": round(ddg_a, 3),
        "ddG_arm_b_kcal": round(ddg_b, 3),
        "ddddG_kcal": round(ddg_a - ddg_b, 3),
        "abs_ddddG_kcal": round(abs(ddg_a - ddg_b), 3),
        "_convention": ("dG = -2.303*R*T*pChEMBL at T=298.15 K (%.4f kcal/mol per log unit); "
                        "ddddG = ddG_bind(d0->d | arm A) - ddG_bind(d0->d | arm B). A pChEMBL is a "
                        "log10 affinity, so this conversion is exact given the measurement; it "
                        "inherits whatever systematic the underlying assay carries."
                        % LOG10_TO_KCAL),
    }


# ---------------------------------------------------------------------------------------------------
# RCSB -- structures on both arms, fetched not remembered
# ---------------------------------------------------------------------------------------------------
def rcsb_holo_entries(tp, accession, rows=50):
    """Experimental PDB entries for this UniProt accession that contain at least one non-polymer
    (i.e. holo). Returns {'entries': [...], 'total': n, 'read': bool}."""
    q = {"query": {"type": "group", "logical_operator": "and", "nodes": [
        {"type": "terminal", "service": "text", "parameters": {
            "attribute": ("rcsb_polymer_entity_container_identifiers."
                          "reference_sequence_identifiers.database_accession"),
            "operator": "exact_match", "value": accession}},
        {"type": "terminal", "service": "text", "parameters": {
            "attribute": ("rcsb_polymer_entity_container_identifiers."
                          "reference_sequence_identifiers.database_name"),
            "operator": "exact_match", "value": "UniProt"}},
        {"type": "terminal", "service": "text", "parameters": {
            "attribute": "rcsb_entry_info.nonpolymer_entity_count",
            "operator": "greater", "value": 0}},
    ]},
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": rows},
                            "results_content_type": ["experimental"]}}
    doc = tp.post_json(RCSB_SEARCH, q)
    if doc is None:
        return {"accession": accession, "read": False, "total": None, "entries": [],
                "_absent_reading": ("RCSB did not answer; this is NOT the finding that no holo "
                                    "structure exists")}
    ids = [r.get("identifier") for r in doc.get("result_set") or []]
    return {"accession": accession, "read": True, "total": doc.get("total_count", len(ids)),
            "entries": ids[:rows], "_query": "rcsbsearch/v2 UniProt accession + nonpolymer>0"}


# ---------------------------------------------------------------------------------------------------
# BindingDB -- the second, independent affinity instrument (confirmation only)
# ---------------------------------------------------------------------------------------------------
def bindingdb_probe(tp, accession, affinity_cutoff=10000):
    """A LEAD-level confirmation read, never the source of a value that enters the gate.

    BindingDB's public service returns ligand records for a UniProt accession. It is used here to
    say whether an INDEPENDENT database also holds affinity data for both arms -- a candidate that
    only one database has seen is a weaker candidate, and that is worth printing. A transport
    failure is recorded and never counted as absence.
    """
    url = ("%s?uniprot=%s&code=0&response=application/json&cutoff=%d"
           % (BINDINGDB, urllib.parse.quote(accession), affinity_cutoff))
    doc = tp.get_json(url, tries=2)
    if doc is None:
        return {"accession": accession, "read": False,
                "_absent_reading": "BindingDB did not answer; not a finding of absence"}
    try:
        hits = (((doc.get("getLigandsByUniprotsResponse") or {}).get("affinities")) or [])
        if isinstance(hits, dict):
            hits = [hits]
        return {"accession": accession, "read": True, "n_affinity_records": len(hits)}
    except Exception as e:                                        # noqa: BLE001
        return {"accession": accession, "read": True, "n_affinity_records": None,
                "parse_note": "unexpected response shape: %s" % e}


# ---------------------------------------------------------------------------------------------------
# Candidate construction and the gate
# ---------------------------------------------------------------------------------------------------
def build_candidates(idx, target_a, target_b, smiles, prereg=None, max_pairs=200000):
    """Every (d0, d) pair measured on BOTH arms in the SAME standard_type, scored. Pure.

    Returns candidates sorted by |ddddG|, each carrying its congeneric report and its four
    measurements. Nothing is filtered out here except the structural congenericity test -- the band
    is applied by the gate so that near misses stay visible.
    """
    prereg = prereg or PREREG
    by_type = {}
    for (tid, mid, st) in idx:
        if tid in (target_a, target_b):
            by_type.setdefault(st, {}).setdefault(tid, set()).add(mid)
    cands = []
    for st, per_t in by_type.items():
        shared = sorted(per_t.get(target_a, set()) & per_t.get(target_b, set()))
        if len(shared) < 2:
            continue
        for i in range(len(shared)):
            for j in range(i + 1, len(shared)):
                if len(cands) >= max_pairs:
                    break
                d0, d = shared[i], shared[j]
                s0 = (smiles.get(d0) or {}).get("smiles")
                s1 = (smiles.get(d) or {}).get("smiles")
                if not s0 or not s1:
                    continue
                cong = congeneric_report(s0, s1, prereg)
                if not cong.get("is_congeneric"):
                    continue
                m_dA = measurement(idx, target_a, d, st)
                m_d0A = measurement(idx, target_a, d0, st)
                m_dB = measurement(idx, target_b, d, st)
                m_d0B = measurement(idx, target_b, d0, st)
                if not all((m_dA, m_d0A, m_dB, m_d0B)):
                    continue
                energy = ddddg_from_four(m_dA, m_d0A, m_dB, m_d0B)
                cands.append({
                    "standard_type": st,
                    "arm_a_target": target_a, "arm_b_target": target_b,
                    "ligand_reference": d0, "ligand_variant": d,
                    "ligand_reference_smiles": s0, "ligand_variant_smiles": s1,
                    "congeneric": cong,
                    "measurements": {"variant_on_a": m_dA, "reference_on_a": m_d0A,
                                     "variant_on_b": m_dB, "reference_on_b": m_d0B},
                    "energy": energy,
                    "max_pchembl_spread": max(m["pchembl_spread"] for m in
                                              (m_dA, m_d0A, m_dB, m_d0B)),
                })
    cands.sort(key=lambda c: -c["energy"]["abs_ddddG_kcal"])
    return cands


def grade(candidates, band=None, engine=None):
    """Split candidates into in-band/gradeable, in-band/inside-the-engine-band, and out-of-band."""
    band = band or PREREG["band_kcal"]
    eb = float((engine or engine_band())["band_kcal"])
    lo, hi = float(band[0]), float(band[1])
    in_band, inside_engine, out = [], [], []
    for c in candidates:
        a = c["energy"]["abs_ddddG_kcal"]
        if lo <= a <= hi:
            (in_band if a > eb else inside_engine).append(c)
        else:
            out.append(c)
    return {"gradeable": in_band, "inside_engine_band": inside_engine, "out_of_band": out,
            "search_band_kcal": [lo, hi], "engine_band_kcal": eb}


def verdict(graded, structures, instruments_read, notes=None):
    """The pre-registered four-valued gate. Pure.

    `instruments_read` is a dict of instrument -> bool. A STOP is unreachable unless every one is
    True, because a search-shaped null across a scan that hit transport errors is UNDETERMINED.
    """
    notes = notes or []
    unread = sorted(k for k, v in instruments_read.items() if not v)
    gradeable = graded["gradeable"]
    with_structs = []
    for c in gradeable:
        sa = structures.get(c.get("arm_a_accession")) or {}
        sb = structures.get(c.get("arm_b_accession")) or {}
        c["structures"] = {"arm_a": sa, "arm_b": sb}
        c["structures_on_both_arms"] = bool(sa.get("entries") and sb.get("entries"))
        if c["structures_on_both_arms"]:
            with_structs.append(c)

    gates = {
        "A1_homology_measured_by_alignment": {
            "requirement": ("sequence identity computed by alignment between the two arms' own "
                            "ChEMBL component sequences, >= %.0f%%. A shared family name or ChEMBL "
                            "protein class NEVER satisfies this."
                            % PREREG["identity_min_percent"]),
            "met": bool(gradeable),
            "identities_of_gradeable_candidates": sorted(
                {round(c.get("pair_identity_percent") or 0.0, 1) for c in gradeable}),
        },
        "A2_four_measured_affinities_same_observable": {
            "requirement": ("four ChEMBL binding measurements with pchembl values, standard_relation "
                            "'=', and ONE standard_type across all four"),
            "met": bool(gradeable),
            "standard_types_seen": sorted({c["standard_type"] for c in gradeable}),
        },
        "A3_congeneric_by_structure": {
            "requirement": ("identical Bemis-Murcko scaffold AND MCS covering >= %.0f%% of the "
                            "smaller molecule AND |delta heavy atoms| <= %d, computed with RDKit "
                            "from the deposited SMILES. A shared series name NEVER satisfies this. "
                            "Morgan Tanimoto is computed and printed on every candidate but does NOT "
                            "gate -- see PREREG._why_mcs_and_not_tanimoto_alone."
                            % (100 * PREREG["mcs_fraction_min"],
                               PREREG["heavy_atom_delta_max"])),
            "met": bool(gradeable),
        },
        "A4_band": {
            "requirement": ("|ddddG_exp| inside the pre-registered paralogue-scale search band "
                            "%s kcal/mol AND above the engine's own demonstrated band (Open "
                            "decision 7)" % (graded["search_band_kcal"],)),
            "engine_band_kcal": graded["engine_band_kcal"],
            "n_gradeable": len(gradeable),
            "n_inside_engine_band": len(graded["inside_engine_band"]),
            "n_out_of_band": len(graded["out_of_band"]),
            "met": bool(gradeable),
        },
        "A5_structures_on_both_arms": {
            "requirement": "at least one experimental HOLO PDB entry per arm, fetched live from RCSB",
            "n_gradeable_with_structures_on_both_arms": len(with_structs),
            "met": bool(with_structs),
        },
        "A6_null_rejection_stated_up_front": {
            "requirement": "what result would count as a refutation, written before any spend",
            "statement": null_rejection_rule(),
            "met": True,
            "_but": ("stating a rejection rule does not manufacture a reference. A6 is necessary and "
                     "nowhere near sufficient."),
        },
    }

    if unread:
        decision = "UNDETERMINED"
        sentence = ("UNDETERMINED -- an instrument could not be read (%s). This is an ABSENT READING, "
                    "not a reading of absence: re-run on a CI runner before drawing any conclusion, "
                    "and spend nothing in the meantime." % ", ".join(unread))
    elif with_structs:
        best = with_structs[0]
        decision = "PROCEED"
        sentence = (
            "PROCEED -- a paralogue-scale ligand-side known answer EXISTS. %d candidate system(s) "
            "clear every pre-registered criterion; the strongest is %s vs %s (%s / %s), "
            "|ddddG_exp| = %.3f kcal/mol on %s values, congeneric at Tanimoto %.2f with an identical "
            "Murcko scaffold, holo structures on both arms. Transcribe the specific record into the "
            "benchmark BY HAND with its ChEMBL assay and document ids before any leg is launched -- "
            "this module emits evidence and does not curate."
            % (len(with_structs), best.get("arm_a_label") or best["arm_a_target"],
               best.get("arm_b_label") or best["arm_b_target"], best["ligand_reference"],
               best["ligand_variant"], best["energy"]["abs_ddddG_kcal"], best["standard_type"],
               best["congeneric"]["tanimoto_morgan_r2_2048"]))
    elif gradeable:
        decision = "UNDETERMINED"
        sentence = (
            "UNDETERMINED -- %d candidate system(s) clear the affinity, congenericity and band "
            "criteria but NONE has a holo experimental structure on both arms in the RCSB read. A "
            "ddddG benchmark with no structural basis on one arm cannot be set up, so this is not a "
            "PROCEED; and because the structural arm is the one that came up empty rather than the "
            "measurement arm, it is not the STOP either." % len(gradeable))
    elif graded["inside_engine_band"]:
        decision = "STOP_BAND"
        sentence = (
            "STOP -- candidate systems exist but every one of them sits INSIDE the engine's own "
            "demonstrated accuracy band (%.2f kcal/mol, %d candidates below it). Open decision 7 "
            "binds: no accuracy band wider than the signal being calibrated. A benchmark smaller "
            "than the engine's error cannot distinguish a right answer from a wrong one, so it buys "
            "nothing." % (graded["engine_band_kcal"], len(graded["inside_engine_band"])))
    else:
        decision = "STOP_NO_REFERENCE"
        sentence = (
            "STOP -- NO PARALOGUE-SCALE LIGAND-SIDE KNOWN ANSWER WAS FOUND. Every instrument read "
            "cleanly and no system satisfies the shape the ddddG instrument needs: two homologous "
            "proteins (identity measured by alignment), a structurally-congeneric ligand pair "
            "(RDKit, not a name), four measured affinities in ONE observable, and a between-protein "
            "double difference inside the paralogue-scale band. %d out-of-band candidates were found "
            "and are listed so the negative can be disagreed with. A ddddG benchmark run would "
            "therefore have no known answer to be scored against -- it would be an experiment "
            "wearing a control's costume. SPEND NOTHING." % len(graded["out_of_band"]))

    return {"decision": decision, "gates": gates, "sentence": sentence,
            "instruments_read": instruments_read,
            "n_candidates_with_structures_on_both_arms": len(with_structs),
            "notes": notes,
            "caveat_that_must_travel_with_any_result": caveat()}


# ---------------------------------------------------------------------------------------------------
# C01b -- the CREBBP/BRD4 congeneric-analogue precheck
# ---------------------------------------------------------------------------------------------------
#: Read from selectivity-benchmark.json rather than typed: the designated binary control's two arms,
#: their UniProt accessions and their holo deposits are already committed there.
BENCH = os.path.join(HERE, "selectivity-benchmark.json")


def c01b_arms(path=BENCH):
    """The two arms of the designated binary control, READ from the committed benchmark artifact."""
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    arms = []
    for p in doc.get("proteins") or []:
        arms.append({"receptor_token": p.get("receptor_token"), "name": p.get("name"),
                     "uniprot": p.get("uniprot"), "committed_holo_pdb": p.get("holo_pdb"),
                     "committed_kd_nM": p.get("kd_nM")})
    return arms, {
        "ligand": (doc.get("ligand") or {}).get("name"),
        "experimental_ddG_kcal": (doc.get("experimental_selectivity") or {}).get("ddg_kcal_per_mol"),
        "_source": os.path.basename(path),
        "_note": ("this is the ONE-ligand/two-protein ABSOLUTE-difference form. C01b asks whether a "
                  "congeneric ANALOGUE measured in BOTH proteins exists, which is what would turn it "
                  "into a RELATIVE ddddG. Do not assume one does."),
    }


def run_c01b(out_path=OUT_C01B, offline=False, tp=None):
    doc = {
        "_what": ("ROADMAP ROW 27 / candidate C01b -- the $0 precheck asking whether a measured "
                  "CONGENERIC ligand pair exists across the designated binary selectivity control's "
                  "two arms, which is the only missing ingredient for a RELATIVE ddddG version of it."),
        "_this_is_evidence_not_a_conclusion": (
            "Every affinity is a ChEMBL activity record with its assay and document ids. Every "
            "congenericity judgement is an RDKit computation on the deposited SMILES. Every PDB "
            "entry is a live RCSB search result. Nothing is curated or remembered."),
        "_prereg": PREREG,
        "engine_band": engine_band(),
        "null_rejection_rule": null_rejection_rule(),
        "caveat_that_must_travel_with_any_result": caveat(),
    }
    try:
        arms, bench = c01b_arms()
        doc["arms"] = arms
        doc["committed_binary_control"] = bench
    except (OSError, ValueError) as e:
        doc["arms"] = []
        doc["_error"] = "selectivity-benchmark.json unreadable: %s" % e

    if offline or not doc.get("arms"):
        doc["verdict"] = verdict({"gradeable": [], "inside_engine_band": [], "out_of_band": [],
                                  "search_band_kcal": PREREG["band_kcal"],
                                  "engine_band_kcal": doc["engine_band"]["band_kcal"]},
                                 {}, {"chembl": False, "rcsb": False},
                                 notes=["--offline: no fetch attempted" if offline
                                        else "the committed benchmark artifact could not be read"])
        doc["map_edits_required"] = c01_map_edits(doc, which="C01b")
        if out_path:
            _write(out_path, doc)
        return doc

    tp = tp or Transport()
    accs = [a["uniprot"] for a in arms if a.get("uniprot")]

    resolved, targets = {}, []
    for acc in accs:
        got = chembl_targets_by_accession(tp, acc)
        resolved[acc] = got
        targets.extend([g for g in got
                        if g.get("target_type") == "SINGLE PROTEIN"
                        and (g.get("organism") or "").startswith("Homo")])
    doc["chembl_target_resolution"] = resolved
    doc["_resolution_rule"] = ("targets are resolved by UniProt ACCESSION carried in "
                               "target_components, never by pref_name -- see module docstring trap "
                               "(3). Every ChEMBL target on each accession is kept, including the "
                               "separate bromodomain-domain constructs, and the arm identity of each "
                               "is printed so a domain mismatch is visible rather than averaged away.")

    acts, read_ok = {}, True
    for t in targets:
        rows, ok = chembl_activities(tp, t["target_chembl_id"])
        read_ok = read_ok and ok
        acts[t["target_chembl_id"]] = rows
    all_rows = [r for rows in acts.values() for r in rows]
    doc["n_activity_rows"] = len(all_rows)
    doc["targets_scanned"] = [{"target_chembl_id": t["target_chembl_id"],
                               "pref_name": t["pref_name"], "accession": t["accessions"][0],
                               "n_activity_rows": len(acts[t["target_chembl_id"]])}
                              for t in targets]
    idx = index_activities(all_rows)

    a_targets = [t["target_chembl_id"] for t in targets if t["accessions"][0] == accs[0]]
    b_targets = [t["target_chembl_id"] for t in targets if t["accessions"][0] == accs[1]]

    mol_ids = {mid for (_t, mid, _s) in idx}
    smiles, sm_ok = chembl_smiles(tp, mol_ids)
    read_ok = read_ok and sm_ok
    doc["n_molecules_with_smiles"] = len(smiles)

    candidates = []
    for ta in a_targets:
        for tb in b_targets:
            for c in build_candidates(idx, ta, tb, smiles):
                c["arm_a_accession"] = accs[0]
                c["arm_b_accession"] = accs[1]
                c["arm_a_label"] = next((t["pref_name"] for t in targets
                                         if t["target_chembl_id"] == ta), ta)
                c["arm_b_label"] = next((t["pref_name"] for t in targets
                                         if t["target_chembl_id"] == tb), tb)
                c["pair_identity_percent"] = None       # filled below, measured not assumed
                candidates.append(c)

    # A1 for C01b: the two arms' identity is MEASURED, not assumed from "both are bromodomains".
    comps, comp_ok = {}, True
    for acc in accs:
        d = tp.get_json("%s/target_component.json?accession=%s&limit=5&only=accession,sequence"
                        % (CHEMBL, acc))
        if d is None:
            comp_ok = False
            continue
        for c in d.get("target_components") or []:
            if c.get("sequence"):
                comps[acc] = c["sequence"]
    read_ok = read_ok and comp_ok
    ident, method = (None, None)
    if len(comps) == 2:
        ident, method = pairwise_identity(comps[accs[0]], comps[accs[1]])
    doc["arm_identity"] = {"percent_identity": None if ident is None else round(ident, 2),
                           "method": method, "accessions": accs,
                           "_why": ("'both are bromodomains' is a family name. The number is the "
                                    "evidence, and for these two full-length proteins it is expected "
                                    "to be LOW even though the READER DOMAINS are close -- which is "
                                    "itself a finding worth printing, because it means a "
                                    "full-sequence identity is the wrong statistic for a "
                                    "domain-level benchmark and the domain construct is what a run "
                                    "would actually use.")}
    for c in candidates:
        c["pair_identity_percent"] = None if ident is None else round(ident, 2)

    structures = {}
    for acc in accs:
        structures[acc] = rcsb_holo_entries(tp, acc)
    doc["structures"] = structures
    rcsb_ok = all(s.get("read") for s in structures.values())

    doc["bindingdb_confirmation"] = {acc: bindingdb_probe(tp, acc) for acc in accs}

    graded = grade(candidates, engine=doc["engine_band"])
    doc["n_congeneric_candidates"] = len(candidates)
    doc["candidates"] = {
        "gradeable": graded["gradeable"][:40],
        "inside_engine_band": graded["inside_engine_band"][:40],
        "out_of_band": graded["out_of_band"][:40],
        "_counts": {k: len(graded[k]) for k in
                    ("gradeable", "inside_engine_band", "out_of_band")},
    }
    doc["verdict"] = verdict(graded, structures,
                             {"chembl": read_ok, "rcsb": rcsb_ok},
                             notes=["transport errors: %d" % len(tp.errors)] if tp.errors else [])
    doc["transport_errors"] = tp.errors[:40]
    doc["n_api_calls"] = tp.n_calls
    doc["map_edits_required"] = c01_map_edits(doc, which="C01b")
    if out_path:
        _write(out_path, doc)
    return doc


# ---------------------------------------------------------------------------------------------------
# C01a -- the wide scan, staged and checkpointed
# ---------------------------------------------------------------------------------------------------
def _ck(name):
    os.makedirs(CKPT, exist_ok=True)
    return os.path.join(CKPT, name)


def _save(name, obj):
    with open(_ck(name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


def _load(name, default=None):
    try:
        with open(_ck(name), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def stage_universe(tp):
    """Every human single-protein ChEMBL target with an accession, plus its sequence and its count
    of binding activities carrying a pchembl value."""
    targets, ok1 = chembl_human_single_protein_targets(tp)
    comps, ok2 = chembl_all_human_components(tp)
    kept = []
    for t in targets:
        c = comps.get(t["accession"])
        if not c or len(c["sequence"] or "") < 80:
            continue
        kept.append(dict(t, sequence=c["sequence"], description=c.get("description")))
    out = {"n_targets_listed": len(targets), "n_with_sequence": len(kept),
           "read_ok": bool(ok1 and ok2), "targets": kept}
    _save("universe.json", out)
    return out


def stage_counts(tp, universe, min_count=None):
    min_count = min_count or PREREG["min_pchembl_activities_per_target"]
    have = _load("counts.json", {}) or {}
    ok = True
    for t in universe["targets"]:
        tid = t["target_chembl_id"]
        if tid in have:
            continue
        n = chembl_activity_count(tp, tid)
        if n is None:
            ok = False
            continue
        have[tid] = n
        if len(have) % 200 == 0:
            _save("counts.json", have)
    _save("counts.json", have)
    kept = [t for t in universe["targets"] if have.get(t["target_chembl_id"], 0) >= min_count]
    out = {"read_ok": ok, "n_counted": len(have), "min_count": min_count,
           "n_targets_over_min": len(kept),
           "targets": [dict(t, n_pchembl_activities=have[t["target_chembl_id"]]) for t in kept]}
    _save("counted.json", out)
    return out


def stage_pairs(counted, prereg=None):
    """Homologous pairs, prefiltered by k-mer containment then CONFIRMED by real alignment."""
    prereg = prereg or PREREG
    k = prereg["kmer_prefilter_k"]
    targets = counted["targets"]
    ksets = [kmer_set(t["sequence"], k) for t in targets]
    post = {}
    for i, ks in enumerate(ksets):
        for km in ks:
            post.setdefault(km, []).append(i)
    shared = {}
    for i, ks in enumerate(ksets):
        counter = {}
        for km in ks:
            for j in post.get(km, ()):
                if j <= i:
                    continue
                counter[j] = counter.get(j, 0) + 1
        for j, n in counter.items():
            cont = n / float(min(len(ksets[i]), len(ksets[j])) or 1)
            if cont >= prereg["kmer_prefilter_containment_min"]:
                shared[(i, j)] = cont
    pairs, dropped = [], 0
    for (i, j), cont in sorted(shared.items(), key=lambda kv: -kv[1]):
        ident, method = pairwise_identity(targets[i]["sequence"], targets[j]["sequence"])
        if ident < prereg["identity_min_percent"]:
            dropped += 1
            continue
        pairs.append({
            "arm_a": {k2: targets[i][k2] for k2 in
                      ("target_chembl_id", "pref_name", "accession", "n_pchembl_activities")},
            "arm_b": {k2: targets[j][k2] for k2 in
                      ("target_chembl_id", "pref_name", "accession", "n_pchembl_activities")},
            "identity_percent": round(ident, 2), "identity_method": method,
            "kmer_containment": round(cont, 4),
        })
    pairs.sort(key=lambda p: -p["identity_percent"])
    out = {"n_prefiltered_pairs": len(shared), "n_pairs_over_identity_floor": len(pairs),
           "n_dropped_below_identity_floor": dropped,
           "identity_floor_percent": prereg["identity_min_percent"],
           "_prefilter_note": prereg["_why_prefilter"], "pairs": pairs}
    _save("pairs.json", out)
    return out


def stage_activities(tp, pairs, max_targets=None):
    """Activities for every target appearing in a qualifying pair. Checkpointed per target."""
    all_tids = sorted({p[arm]["target_chembl_id"] for p in pairs["pairs"]
                       for arm in ("arm_a", "arm_b")})
    tids = all_tids[:max_targets] if max_targets else all_tids
    done = set(os.path.splitext(f)[0] for f in os.listdir(_ck("")) if f.startswith("CHEMBL")
               and f.endswith(".json")) if os.path.isdir(CKPT) else set()
    ok = True
    for tid in tids:
        if tid in done:
            continue
        rows, got = chembl_activities(tp, tid)
        ok = ok and got
        _save("%s.json" % tid, rows)
    meta = {"read_ok": ok, "n_targets": len(tids), "n_targets_required": len(all_tids),
            "capped": len(tids) < len(all_tids)}
    # ⚠ PERSISTED, because the verdict stage runs in a LATER process. A cap that is not carried
    # forward becomes a complete scan by amnesia, and a complete scan may return STOP.
    _save("acts_meta.json", meta)
    return dict(meta, targets=tids)


def stage_candidates(tp, pairs, targets_done, max_pairs=None):
    """Congeneric candidates with a computed ddddG, per qualifying protein pair."""
    out, ok = [], True
    plist = pairs["pairs"][:max_pairs] if max_pairs else pairs["pairs"]
    capped = len(plist) < len(pairs["pairs"])
    for p in plist:
        ta = p["arm_a"]["target_chembl_id"]
        tb = p["arm_b"]["target_chembl_id"]
        ra, rb = _load("%s.json" % ta), _load("%s.json" % tb)
        if ra is None or rb is None:
            ok = False
            continue
        idx = index_activities(ra + rb)
        by_type = {}
        for (tid, mid, st) in idx:
            by_type.setdefault(st, {}).setdefault(tid, set()).add(mid)
        shared_ids = set()
        for st, per_t in by_type.items():
            shared_ids |= (per_t.get(ta, set()) & per_t.get(tb, set()))
        if len(shared_ids) < 2:
            continue
        smiles, sm_ok = chembl_smiles(tp, shared_ids)
        ok = ok and sm_ok
        for c in build_candidates(idx, ta, tb, smiles):
            c["arm_a_accession"] = p["arm_a"]["accession"]
            c["arm_b_accession"] = p["arm_b"]["accession"]
            c["arm_a_label"] = p["arm_a"]["pref_name"]
            c["arm_b_label"] = p["arm_b"]["pref_name"]
            c["pair_identity_percent"] = p["identity_percent"]
            c["n_shared_compounds"] = len(shared_ids)
            out.append(c)
        _save("candidates.json", out)
    out.sort(key=lambda c: -c["energy"]["abs_ddddG_kcal"])
    _save("candidates.json", out)
    meta = {"read_ok": ok, "n_candidates": len(out), "n_pairs_examined": len(plist),
            "n_pairs_qualifying": len(pairs["pairs"]), "capped": capped}
    _save("cand_meta.json", meta)
    return dict(meta, candidates=out)


def run_c01a(out_path=OUT_C01A, stage="all", offline=False, tp=None, max_pairs=None,
             max_targets=None):
    doc = {
        "_what": ("ROADMAP ROW 27 / candidate C01a -- the ligand-side wedge-band scan. The exact "
                  "analogue of the SKEMPI scan that returned barnase_barstar_W35F from 7,085 rows, "
                  "run on the LIGAND side: two homologous proteins x a matched congeneric ligand "
                  "pair x four measured affinities x holo structures on both arms, with the "
                  "between-protein double difference in the paralogue-scale band."),
        "_this_is_evidence_not_a_conclusion": (
            "Homology is an alignment, congenericity is an RDKit computation, every affinity is a "
            "ChEMBL activity row with its assay and document ids, and every structure is a live "
            "RCSB search result. The verdict is a mechanical function of those and is printed "
            "beside them."),
        "_prereg": PREREG,
        "engine_band": engine_band(),
        "null_rejection_rule": null_rejection_rule(),
        "caveat_that_must_travel_with_any_result": caveat(),
    }
    if offline:
        doc["verdict"] = verdict({"gradeable": [], "inside_engine_band": [], "out_of_band": [],
                                  "search_band_kcal": PREREG["band_kcal"],
                                  "engine_band_kcal": doc["engine_band"]["band_kcal"]},
                                 {}, {"chembl": False, "rcsb": False},
                                 notes=["--offline: no fetch attempted"])
        doc["map_edits_required"] = c01_map_edits(doc, which="C01a")
        if out_path:
            _write(out_path, doc)
        return doc

    tp = tp or Transport()
    want = ("universe", "counts", "pairs", "activities", "candidates", "verdict")
    stages = want if stage == "all" else (stage,)

    universe = _load("universe.json")
    if "universe" in stages or universe is None:
        universe = stage_universe(tp)
    counted = _load("counted.json")
    if "counts" in stages or counted is None:
        counted = stage_counts(tp, universe)
    pairs = _load("pairs.json")
    if "pairs" in stages or pairs is None:
        pairs = stage_pairs(counted)
    acts = _load("acts_meta.json") or {"read_ok": False, "n_targets": 0, "n_targets_required": None,
                                       "capped": True,
                                       "_note": ("the activities stage has not run in this "
                                                 "checkpoint directory")}
    if "activities" in stages:
        acts = stage_activities(tp, pairs, max_targets=max_targets)
    cands = _load("cand_meta.json") or {"read_ok": False, "n_candidates": 0, "n_pairs_examined": 0,
                                        "n_pairs_qualifying": len(pairs.get("pairs") or []),
                                        "capped": True}
    cands = dict(cands, candidates=_load("candidates.json", []) or [])
    if "candidates" in stages:
        cands = stage_candidates(tp, pairs, acts, max_pairs=max_pairs)

    doc["scan"] = {
        "universe": {k: universe[k] for k in ("n_targets_listed", "n_with_sequence", "read_ok")},
        "counts": {k: counted[k] for k in
                   ("read_ok", "n_counted", "min_count", "n_targets_over_min")},
        "pairs": {k: pairs[k] for k in
                  ("n_prefiltered_pairs", "n_pairs_over_identity_floor",
                   "n_dropped_below_identity_floor", "identity_floor_percent")},
        "activities": {k: acts.get(k) for k in
                       ("read_ok", "n_targets", "n_targets_required", "capped")},
        "candidates": {"n_congeneric_candidates": cands.get("n_candidates"),
                       "read_ok": cands.get("read_ok"),
                       "n_pairs_examined": cands.get("n_pairs_examined"),
                       "n_pairs_qualifying": cands.get("n_pairs_qualifying"),
                       "capped": cands.get("capped")},
        "_completeness_rule": (
            "⛔ A CAPPED SCAN CANNOT SUPPORT A STOP. If either cap truncated the work, "
            "`scan_covered_every_qualifying_pair` below is False and the gate returns UNDETERMINED "
            "no matter how empty the candidate list is -- a search-shaped null across a scan that "
            "did not finish is an absent reading, not a reading of absence."),
    }
    doc["top_homologous_pairs"] = pairs["pairs"][:60]

    graded = grade(cands["candidates"], engine=doc["engine_band"])
    accs = sorted({c[k] for c in graded["gradeable"] for k in ("arm_a_accession", "arm_b_accession")})
    structures = {acc: rcsb_holo_entries(tp, acc) for acc in accs[:80]}
    doc["structures"] = structures
    rcsb_ok = all(s.get("read") for s in structures.values()) if structures else True

    doc["candidates"] = {
        "gradeable": graded["gradeable"][:60],
        "inside_engine_band": graded["inside_engine_band"][:40],
        "out_of_band": graded["out_of_band"][:40],
        "_counts": {k: len(graded[k]) for k in
                    ("gradeable", "inside_engine_band", "out_of_band")},
    }
    doc["bindingdb_confirmation"] = {
        acc: bindingdb_probe(tp, acc)
        for acc in sorted({c[k] for c in graded["gradeable"][:10]
                           for k in ("arm_a_accession", "arm_b_accession")})}

    read = {
        "chembl_universe": bool(universe.get("read_ok")),
        "chembl_counts": bool(counted.get("read_ok")),
        "chembl_activities": bool(acts.get("read_ok")),
        "chembl_molecules": bool(cands.get("read_ok")),
        "rcsb": rcsb_ok,
        "scan_covered_every_qualifying_pair": not (acts.get("capped") or cands.get("capped")),
    }
    doc["verdict"] = verdict(graded, structures, read,
                             notes=["transport errors: %d" % len(tp.errors)] if tp.errors else [])
    doc["transport_errors"] = tp.errors[:60]
    doc["n_api_calls"] = tp.n_calls
    doc["map_edits_required"] = c01_map_edits(doc, which="C01a")
    if out_path:
        _write(out_path, doc)
    return doc


# ---------------------------------------------------------------------------------------------------
# VERBATIM SPANS OF THE LIVE ROADMAP, held as literals so the routed edits are `grep -F`-checkable.
# ⚠ QUOTATIONS, not restatements. `verify_map_edits.py` fails the build if any stops matching
# nr4a3-program-map.md exactly -- the guard the categorical audit did not have when all nine of its
# verbatim edits turned out to have been written against a map that had moved underneath them.
# ---------------------------------------------------------------------------------------------------
MAP_10_1_ROW_27 = ("| **27** | **The two $0 searches for a paralogue-scale known answer for the "
                   "ligand-side \u0394\u0394\u0394G** |")

MAP_REGIME_GAP_SENTENCE = ("and 0 requirements standing on an instrument validated in the regime "
                           "the claim needs.**")

MAP_ROW_27_STOP_CLAUSE = "A `STOP_NO_REFERENCE` is a good outcome and not a failure"


# ---------------------------------------------------------------------------------------------------
# Roadmap edits -- routed, never applied. This module does not own nr4a3-program-map.md.
# ---------------------------------------------------------------------------------------------------
def c01_map_edits(doc, which="C01a"):
    """Verbatim, ready-to-apply roadmap edits, as a machine-readable list. See row-26 module for the
    field contract; `anchor` must be `grep -F`-verifiable against the live map."""
    v = doc.get("verdict") or {}
    dec = v.get("decision", "UNDETERMINED")
    counts = (doc.get("candidates") or {}).get("_counts") or {}
    artifact = ("research/modalities/ddddg-benchmark-scan.json" if which == "C01a"
                else "research/modalities/ddddg-crebbp-brd4-precheck.json")

    if dec == "PROCEED":
        headline = ("✅ **A paralogue-scale ligand-side known answer EXISTS** (%s, 2026-08-03): %d "
                    "candidate system(s) clear homology-by-alignment, structural congenericity, four "
                    "measured affinities in one observable, the wedge band and holo structures on "
                    "both arms." % (which, v.get("n_candidates_with_structures_on_both_arms", 0)))
    elif dec == "STOP_NO_REFERENCE":
        headline = ("⛔ **`STOP_NO_REFERENCE` (%s, 2026-08-03)** — no ligand-side paralogue-scale "
                    "known answer exists in ChEMBL joined against the PDB. This is a RESULT: the "
                    "ddddG route cannot be bought a benchmark at the right size today, and that "
                    "closes it on evidence rather than on budget." % which)
    elif dec == "STOP_BAND":
        headline = ("⛔ **`STOP_BAND` (%s, 2026-08-03)** — candidate systems exist but every one is "
                    "INSIDE the engine's own demonstrated accuracy band, so none can distinguish a "
                    "right answer from a wrong one (Open decision 7)." % which)
    else:
        headline = ("⚠ **`UNDETERMINED` (%s, 2026-08-03)** — a decisive source could not be "
                    "retrieved, so no STOP may be recorded. Re-run before concluding." % which)

    edits = [{
        "section": "10.1 row 27",
        "anchor": MAP_10_1_ROW_27,
        "current_text": MAP_10_1_ROW_27,
        "proposed_text": ("| **27** | ✅ **RUN 2026-08-03 — %s returned `%s`** (%s) |"
                          % (which, dec, artifact)),
        "why": ("row 27 has run; a search that returned a verdict must not keep reading as an open "
                "○ row"),
        "artifact": "%s:verdict.decision" % artifact,
    }, {
        "section": "3.1 (the instrument table)",
        "anchor": None,
        "where": ("a new row in §3.1's instrument table for the ligand-side ΔΔΔG candidate (C01), "
                  "whose known-answer column now has a MEASURED value instead of "
                  "`candidate_unverified`. There is no existing row to anchor to because the "
                  "instrument has never been given a `V` number — roadmap §0.8 says an OPTIONS "
                  "register may not mint one, so the row has to be added by the map's owner."),
        "current_text": None,
        "proposed_text": (
            "| `C01` (unnumbered) | ligand-side selectivity RBFE, ΔΔΔG between two proteins for a "
            "matched congeneric ligand pair | **known answer: %s** — %s | ⛔ **the instrument itself "
            "is unvalidated; a benchmark existing is not a benchmark passed** |" % (dec, headline)),
        "why": ("§3 is where an instrument's known-answer STATE lives, and a `STOP_NO_REFERENCE` is "
                "a state, not a silent absence — the pmx precheck's STOP closed an authorized arm "
                "and is recorded that way"),
        "artifact": "%s:verdict" % artifact,
    }, {
        "section": "3.2 / the regime gap",
        "anchor": MAP_REGIME_GAP_SENTENCE,
        "current_text": MAP_REGIME_GAP_SENTENCE,
        "proposed_text": ("and 0 requirements standing on an instrument validated in the regime the "
                          "claim needs.** As of 2026-08-03 the cheapest candidate route to changing "
                          "that has been SEARCHED rather than assumed: %s" % headline),
        "why": ("the regime-gap sentence is the program's central finding and now has a measured "
                "answer attached to the one candidate that could close it"),
        "artifact": "%s:verdict.sentence" % artifact,
    }]
    if counts:
        edits.append({
            "section": "10.1 row 27 (the ⛔ clause)",
            "anchor": MAP_ROW_27_STOP_CLAUSE,
            "current_text": MAP_ROW_27_STOP_CLAUSE,
            "proposed_text": ("A `STOP_NO_REFERENCE` is a good outcome and not a failure — and on "
                              "2026-08-03 the search returned `%s` with %d gradeable, %d inside the "
                              "engine band and %d out-of-band candidates (%s)"
                              % (dec, counts.get("gradeable", 0),
                                 counts.get("inside_engine_band", 0),
                                 counts.get("out_of_band", 0), artifact)),
            "why": "the row states in advance that a null is useful; the null (or not) now exists",
            "artifact": "%s:candidates._counts" % artifact,
        })
    return edits


def _write(path, doc):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, indent=1, default=str) + "\n")


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Roadmap row 27: the two $0 searches for a "
                                             "paralogue-scale ligand-side ddddG known answer.")
    ap.add_argument("mode", choices=["c01a", "c01b"])
    ap.add_argument("--stage", default="all",
                    choices=["all", "universe", "counts", "pairs", "activities", "candidates",
                             "verdict"])
    ap.add_argument("--out")
    ap.add_argument("--offline", action="store_true",
                    help="exercise the gate logic with no network. NEVER emits a scientific "
                         "verdict: the decision is UNDETERMINED by construction.")
    ap.add_argument("--max-pairs", type=int, default=None)
    ap.add_argument("--max-targets", type=int, default=None)
    args = ap.parse_args(argv)

    if args.mode == "c01b":
        doc = run_c01b(out_path=args.out or OUT_C01B, offline=args.offline)
    else:
        doc = run_c01a(out_path=args.out or OUT_C01A, stage=args.stage, offline=args.offline,
                       max_pairs=args.max_pairs, max_targets=args.max_targets)
    v = doc["verdict"]
    print(json.dumps({"decision": v["decision"], "sentence": v["sentence"]}, indent=2))
    print("\nDECISION: %s" % v["decision"], file=sys.stderr)
    print(v["sentence"], file=sys.stderr)
    print("\nCAVEAT: %s" % doc["caveat_that_must_travel_with_any_result"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
