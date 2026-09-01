#!/usr/bin/env python3
"""Section 6.1 STEP 1 of `emc-vaccine-development-path.md`: defend the acceptance threshold, or
record that it cannot be defended.

═══════════════════════════════════════════════════════════════════════════════════════════════
WHAT THE MANUSCRIPT ASKS FOR, QUOTED, BECAUSE THE DESIGN IS ITS DESIGN AND NOT A NEW ONE
═══════════════════════════════════════════════════════════════════════════════════════════════

§6.1 step 1, verbatim:

    "Defend the acceptance threshold, or record that it cannot be defended. Computational, needs
     nothing but public data. Calibrate the cut against experimentally validated epitopes, and if
     no validated set restricted to fusion-junction peptides exists, that absence is itself the
     finding and Section 2.3's curve is the only honest report of coverage. Until this is done
     every figure in B1 is a point on a curve."

§B1, which says what "calibrate" is allowed to mean here, verbatim:

    "Calibrating that cut against a benchmark of experimentally validated neoepitopes is the form
     that settling would take. The experimentally validated fusion-junction epitopes in the
     literature are individual sequences across a few fusions ... and a handful of epitopes is not
     a set against which a threshold can be calibrated; calibrating on point-mutation neoantigens
     instead would import an assumption about junction peptides that is the very thing in question."

⚠ THE ONE AMBIGUITY, AND THE READING TAKEN. §6.1 step 1 says "experimentally validated epitopes"
unqualified; §B1 says a calibration on anything other than fusion-junction epitopes imports the very
assumption under test. Those two sentences do not pick the same calibration set. **This module takes
the HARDER reading — §B1's.** Only the fusion-junction arm can settle the cut. The general-epitope
arm is computed, is reported, and is labelled as the comparator §B1 refuses, never as the answer.

═══════════════════════════════════════════════════════════════════════════════════════════════
WHAT IS PRE-REGISTERED, AND WHY IT IS AT THE TOP OF THE FILE
═══════════════════════════════════════════════════════════════════════════════════════════════

The question "is this set big enough to calibrate on?" can be answered after the count is known, and
answering it then is how a handful of epitopes becomes a calibration. So the bar is declared here,
before any datum is read, and the module reports the achieved numbers against it either way.
CLAUDE.md's anti-gaming invariant: a bar may not be moved by the result it blocked.

═══════════════════════════════════════════════════════════════════════════════════════════════
THE THREE ARMS
═══════════════════════════════════════════════════════════════════════════════════════════════

  F  FUSION-JUNCTION VALIDATED EPITOPES — the calibration proper. IEDB records of experimentally
     validated MHC class I epitopes whose source antigen is a fusion/chimeric protein, restricted to
     a 4-digit HLA-A/B/C allele, length 8-11, positive assay outcome. For each: where does it fall
     on the SAME predictor and the SAME scale the paper's screen uses? The fraction at or below the
     conventional cut is the cut's sensitivity to real fusion-junction epitopes.

  N  NON-FUSION VALIDATED EPITOPES — the comparator §B1 refuses as a calibration. Same query shape,
     fusion antigens excluded. Reported so the reader can see what the refused calibration would
     have said, marked `⛔_not_the_calibration` at every level.

  D  DECOY NULL — length-matched random peptides from the reviewed human proteome, scored against
     the paper's own 34-allele panel. §7 of the manuscript: "no decoy control and no null
     expectation ... the calls that pass are reported as what the screen returned rather than as an
     enrichment over chance." This is that null. It also yields the likelihood ratio
     P(pass | validated) / P(pass | decoy), which is a calibration statement that needs no prior.

⛔ WHAT NONE OF THIS CAN SUPPORT. A calibrated binding threshold is a calibrated binding threshold.
Nothing here is evidence of presentation on a tumour, of immunogenicity, of efficacy, of safety, of
a therapeutic window, or of clinical readiness. Arm F's epitopes are validated on OTHER fusions in
OTHER diseases; that they were seen does not mean this junction's peptides will be.

⚠ CIRCULARITY, STATED RATHER THAN BURIED. MHCflurry is trained on IEDB. An epitope in arm F or N may
be in its training set, which inflates the measured sensitivity. That bias runs in ONE direction, so
every sensitivity here is an UPPER BOUND on the cut's true sensitivity, and a cut that fails to
capture validated epitopes here fails a fortiori. The artifact says so beside every number.

═══════════════════════════════════════════════════════════════════════════════════════════════
WHY THIS IS A CI JOB
═══════════════════════════════════════════════════════════════════════════════════════════════
`python3 -c "import mhcflurry"` -> ModuleNotFoundError in the dev sandbox, and
`curl https://query-api.iedb.org/` -> "CONNECT tunnel failed, response 403" at the egress proxy.
Both measured 2026-09-01. It runs in `.github/workflows/vaccine-threshold-calibration.yml`.

Outputs:
  vaccine-threshold-calibration.json  — the result
  iedb-validated-epitope-cache.json   — the normalised IEDB records the calibration ran on,
                                        so it is auditable and re-runnable without re-fetching
"""
import argparse
import datetime
import json
import math
import os
import random
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import coverage_threshold_curve as ctc  # noqa: E402  (CONVENTIONAL, LENGTHS, LOOSE - one home)

STRICT = os.path.join(HERE, "epitope-allele-matrix.json")
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
IEDB_CACHE = os.path.join(HERE, "iedb-validated-epitope-cache.json")
OUT = os.path.join(HERE, "vaccine-threshold-calibration.json")

# ══════════════════════════ PRE-REGISTERED, BEFORE ANY DATUM IS READ ══════════════════════════

#: A proportion estimated from fewer than this many independent epitopes cannot be reported to
#: better than roughly +/-0.18 at ANY true value, which is wider than the whole span of cuts the
#: manuscript's §2.3 sensitivity covers. Below it, the honest verdict is "not a calibration set".
MIN_N_FOR_A_CALIBRATION = 30

#: And even above that floor, the exact 95% interval on the pass rate at the conventional cut must
#: be no wider than this for the reading to discriminate one candidate cut from another.
MAX_CI_WIDTH_FOR_A_CALIBRATION = 0.20

#: Decoys per junction peptide. 174 x this many peptides are drawn from the proteome, length-matched
#: to the screen's own length multiset, then resampled to build the null.
DECOY_MULTIPLE = 10

#: Bootstrap draws for the "how many presenting alleles does a random peptide set buy?" null.
NULL_DRAWS = 2000

#: Fixed so the null is reproducible; recorded in the artifact.
RANDOM_SEED = 20260901

# ══════════════════════════════════════ IEDB ══════════════════════════════════════════════════

#: PostgREST root. Verified as the documented form of an IQ-API query 2026-09-01 via the example
#: `https://query-api.iedb.org/mhc_search?linear_sequence=eq.SIINFEKL` (IEDB help / IQ-API docs).
#: ⛔ The COLUMN names below are NOT quoted from documentation this session could reach
#: (help.iedb.org and discuss.iedb.org are both blocked at the egress proxy). They are CANDIDATES;
#: `resolve_columns` picks whichever exists in the live OpenAPI schema and records the choice, and a
#: column it cannot resolve is a hard failure that dumps the real schema rather than a guess.
IEDB_ROOT = "https://query-api.iedb.org"
IEDB_TABLES = ["mhc_search", "tcell_search"]

COLUMN_CANDIDATES = {
    "sequence": ["linear_sequence", "epitope_linear_sequence", "linear_peptide_seq"],
    "allele": ["mhc_allele_name", "mhc_allele_names", "allele_name", "mhc_restriction"],
    "outcome": ["qualitative_measure", "assay_qualitative_measure", "qualitative_measures"],
    "antigen": ["source_antigen_names", "source_antigen_name", "parent_source_antigen_names",
                "antigen_name", "source_molecule_name", "source_antigen_source_org_names"],
    "mhc_class": ["mhc_allele_class", "mhc_class", "class"],
    "host": ["host_organism_names", "host_organism_name", "r_object_source_organism_names"],
}
#: Only `sequence` and `allele` are structurally required — the rest degrade to "not filtered on",
#: which is recorded rather than silently assumed.
REQUIRED_COLUMNS = ["sequence", "allele"]

#: A source-antigen name is treated as a fusion if it matches any of these. Deliberately broad on
#: the generic terms and explicit on the fusions the manuscript itself names, so the arm cannot be
#: quietly narrowed to whatever happened to be easy to find. Every matched name is enumerated in the
#: artifact for audit — an unauditable inclusion rule is not a rule.
FUSION_NAME_PATTERNS = [
    r"fusion", r"chimeri", r"\bbreakpoint\b",
    r"bcr[\W_]*abl", r"ss18[\W_]*ssx", r"syt[\W_]*ssx", r"ews\w*[\W_]*fli",
    r"ews\w*[\W_]*wt1", r"ews\w*[\W_]*erg", r"ews\w*[\W_]*nr4a3", r"ews\w*[\W_]*atf1",
    r"pml[\W_]*rar", r"etv6[\W_]*runx", r"pax[37][\W_]*foxo", r"npm[\W_]*alk",
    r"dnajb1[\W_]*prkaca", r"cbf[\W_]*myh11", r"runx1[\W_]*runx1t1", r"aml1[\W_]*eto",
    r"tmprss2[\W_]*erg", r"eml4[\W_]*alk", r"fus[\W_]*ddit3", r"tls[\W_]*chop",
    r"aspscr1[\W_]*tfe3", r"col1a1[\W_]*pdgfb", r"cic[\W_]*dux4", r"bcor[\W_]*ccnb3",
    r"myb[\W_]*nfib", r"kiaa1549[\W_]*braf", r"nab2[\W_]*stat6", r"tpm3[\W_]*ntrk",
]

#: PostgREST `ilike` probes actually sent. `*fusion*` and `*chimeri*` do the general sweep; the rest
#: exist because a curator may name a fusion antigen only by its partners.
IEDB_ANTIGEN_PROBES = [
    "*fusion*", "*chimeric*", "*BCR*ABL*", "*SS18*SSX*", "*SYT*SSX*", "*EWS*FLI*", "*EWS*WT1*",
    "*EWS*ATF1*", "*EWS*NR4A3*", "*PML*RAR*", "*ETV6*RUNX*", "*PAX3*FOXO*", "*NPM*ALK*",
    "*DNAJB1*PRKACA*", "*RUNX1*RUNX1T1*", "*TMPRSS2*ERG*", "*EML4*ALK*", "*FUS*DDIT3*",
    "*CIC*DUX4*", "*BCOR*CCNB3*", "*ASPSCR1*TFE3*", "*COL1A1*PDGFB*",
]

POSITIVE_OUTCOME = re.compile(r"positive", re.I)
ALLELE_RE = re.compile(r"HLA-[ABC]\*\d{2}:\d{2}")
PAGE = 1000
#: Paging caps. Arm F's probes are narrow and must be exhaustive; arm N's are broad and are
#: deliberately bounded so the job's runtime does not depend on how large IEDB has grown.
MAX_PAGES = 60
MAX_PAGES_GENERAL = 3
#: Hard cap on arm N peptide-allele pairs scored, sampled with RANDOM_SEED and recorded as a
#: sample. Arm N is a comparator; spending an hour of CPU to narrow a CI on a comparator §B1
#: refuses would be deepening a test past its purpose (CLAUDE.md §5).
ARM_N_MAX_PAIRS = 5000


def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get(url, tries=3, timeout=180):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Rare-cancers/vaccine_threshold_calibration (research; contact via repo)",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=timeout) as fh:
                return json.loads(fh.read().decode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
    raise RuntimeError(f"{url} -> {last}")


def discover_schema():
    """The live PostgREST OpenAPI document. Recorded in the artifact whatever else happens.

    ⚠ THE POINT IS THAT NOTHING HERE IS A REMEMBERED COLUMN NAME. If IEDB renames a field, this run
    fails with the real list in hand instead of returning an empty set that reads like an absence.
    """
    doc = _get(IEDB_ROOT + "/")
    defs = doc.get("definitions") or (doc.get("components") or {}).get("schemas") or {}
    tables = {}
    for name, spec in defs.items():
        props = sorted((spec or {}).get("properties", {}).keys())
        if props:
            tables[name] = props
    return {"n_tables": len(tables), "tables": tables,
            "info": (doc.get("info") or {}).get("title")}


def resolve_columns(schema, table):
    """Map each logical field to a column that actually exists on `table`. Records the choice."""
    have = set(schema["tables"].get(table, []))
    resolved, unresolved = {}, []
    for logical, candidates in COLUMN_CANDIDATES.items():
        pick = next((c for c in candidates if c in have), None)
        if pick:
            resolved[logical] = pick
        else:
            unresolved.append(logical)
    return resolved, unresolved


def fetch_table(table, cols, probes):
    """Every row of `table` matching any antigen probe, paged. Returns (rows, errors).

    ⛔ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). Every probe that errors is
    returned, and a non-empty error list makes the caller withhold the absence claim entirely.
    """
    rows, errors, seen = [], [], set()
    select = ",".join(sorted(set(cols.values())))
    antigen_col = cols.get("antigen")
    if not antigen_col:
        return [], [f"{table}: no resolvable source-antigen column; cannot run the fusion probes"]
    for probe in probes:
        for page in range(MAX_PAGES):
            url = (f"{IEDB_ROOT}/{table}?select={select}"
                   f"&{antigen_col}=ilike.{urllib.parse.quote(probe, safe='*')}"
                   f"&limit={PAGE}&offset={page * PAGE}")
            try:
                batch = _get(url)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{table} probe {probe!r} page {page}: {exc}")
                break
            if not batch:
                break
            for r in batch:
                key = json.dumps(r, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    r["_iedb_table"] = table
                    rows.append(r)
            if len(batch) < PAGE:
                break
    return rows, errors


def fetch_general(table, cols, alleles):
    """Arm N's pool: validated epitopes on the paper's own panel alleles, no antigen filter.

    Queried per allele so the request stays bounded and so an allele that returns nothing is
    distinguishable from an allele that was never asked about.
    """
    rows, errors = [], []
    select = ",".join(sorted(set(cols.values())))
    allele_col = cols.get("allele")
    if not allele_col:
        return [], [f"{table}: no resolvable allele column"]
    for allele in alleles:
        for page in range(MAX_PAGES_GENERAL):
            url = (f"{IEDB_ROOT}/{table}?select={select}"
                   f"&{allele_col}=ilike.{urllib.parse.quote('*' + allele + '*', safe='*')}"
                   f"&limit={PAGE}&offset={page * PAGE}")
            try:
                batch = _get(url)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{table} allele {allele} page {page}: {exc}")
                break
            if not batch:
                break
            for r in batch:
                r["_iedb_table"] = table
                rows.append(r)
            if len(batch) < PAGE:
                break
    return rows, errors


def _text(value):
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return " | ".join(_text(v) for v in value)
    return str(value)


def normalise_rows(rows, cols, lengths):
    """(kept, dropped-with-reason). One record per (peptide, allele) pair, deduplicated."""
    kept, dropped = {}, {}

    def drop(reason):
        dropped[reason] = dropped.get(reason, 0) + 1

    for r in rows:
        seq = _text(r.get(cols.get("sequence"))).strip().upper()
        if not seq or not seq.isalpha():
            drop("no linear sequence")
            continue
        if len(seq) not in lengths:
            drop(f"length {len(seq)} outside {sorted(lengths)}")
            continue
        outcome_col = cols.get("outcome")
        if outcome_col:
            outcome = _text(r.get(outcome_col))
            if outcome and not POSITIVE_OUTCOME.search(outcome):
                drop("assay outcome not positive")
                continue
            if not outcome:
                drop("assay outcome absent (not assumed positive)")
                continue
        alleles = ALLELE_RE.findall(_text(r.get(cols.get("allele"))))
        if not alleles:
            drop("no 4-digit HLA-A/B/C restriction")
            continue
        antigen = _text(r.get(cols.get("antigen")))
        for allele in sorted(set(alleles)):
            key = (seq, allele)
            rec = kept.setdefault(key, {"peptide": seq, "allele": allele,
                                        "source_antigens": set(), "tables": set()})
            if antigen:
                rec["source_antigens"].add(antigen)
            rec["tables"].add(r.get("_iedb_table", "?"))
    out = []
    for rec in kept.values():
        rec["source_antigens"] = sorted(rec["source_antigens"])
        rec["tables"] = sorted(rec["tables"])
        out.append(rec)
    out.sort(key=lambda d: (d["peptide"], d["allele"]))
    return out, dropped


def is_fusion(rec):
    blob = " ".join(rec["source_antigens"]).lower()
    return any(re.search(p, blob) for p in FUSION_NAME_PATTERNS)


# ═══════════════════════════════════ EXACT BINOMIAL CI ════════════════════════════════════════

def _log_beta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _betacf(a, b, x, maxit=400, eps=3e-16, fpmin=1e-300):
    """Lentz continued fraction for the incomplete beta. Stable where a factorial sum is not."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, maxit + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a, b).

    ⛔ WHY NOT A BINOMIAL SUM. The first implementation here summed `math.comb(n, i) * p**i`, which
    is exact for the tens of epitopes arm F holds and raises `int too large to convert to float` for
    arm D's ~59,000 decoy tests — measured on a stubbed dry run, 2026-09-01, before the job was
    dispatched. A tail that works on the small arm and dies on the large one is exactly the shape
    that gets discovered in CI, so it is fixed here.
    """
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front_log = a * math.log(x) + b * math.log1p(-x) - _log_beta(a, b)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(front_log) * _betacf(a, b, x) / a
    back_log = b * math.log1p(-x) + a * math.log(x) - _log_beta(b, a)
    return 1.0 - math.exp(back_log) * _betacf(b, a, 1.0 - x) / b


def _beta_quantile(target, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if betainc(a, b, mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def clopper_pearson(k, n, alpha=0.05):
    """Exact 95% interval, via beta quantiles — no scipy, and stable at any n this job reaches."""
    if n == 0:
        return [None, None]
    lo = 0.0 if k == 0 else _beta_quantile(alpha / 2.0, k, n - k + 1)
    hi = 1.0 if k == n else _beta_quantile(1.0 - alpha / 2.0, k + 1, n - k)
    return [round(lo, 6), round(hi, 6)]


# ═════════════════════════════════════ PREDICTION ═════════════════════════════════════════════

def load_predictor():
    from mhcflurry import Class1PresentationPredictor  # noqa: PLC0415
    return Class1PresentationPredictor.load()


def supported_alleles(predictor):
    """Which alleles this predictor build actually carries a model for.

    ⛔ AN ALLELE WITHOUT A MODEL IS UNSCREENED, NEVER A MISS. The attribute has lived in two places
    across MHCflurry versions, so both are tried and a failure to determine it is raised rather than
    silently treated as "supports everything" — which would score an allele the model cannot score
    and report the result as a negative.
    """
    for holder in (predictor, getattr(predictor, "affinity_predictor", None)):
        vals = getattr(holder, "supported_alleles", None)
        if vals:
            return list(vals)
    raise RuntimeError("cannot determine MHCflurry supported_alleles on this build")


def score(predictor, pairs):
    """pairs: [(peptide, allele)]. Returns {(peptide, allele): percentile} on the SAME column the
    committed matrix used, so this calibration and the screen cannot be on different scales."""
    import pandas as pd  # noqa: PLC0415, F401  (mhcflurry brings it)
    by_allele = {}
    for pep, allele in pairs:
        by_allele.setdefault(allele, set()).add(pep)
    out, column = {}, None
    for allele, peps in sorted(by_allele.items()):
        df = predictor.predict(peptides=sorted(peps), alleles={allele: [allele]}, verbose=0)
        col = ("presentation_percentile" if "presentation_percentile" in df.columns
               else "affinity_percentile")
        column = column or col
        for _, r in df.iterrows():
            out[(str(r["peptide"]), allele)] = round(float(r[col]), 4)
    return out, column


def ecdf(percentiles, grid):
    n = len(percentiles)
    rows = []
    for t in grid:
        k = sum(1 for p in percentiles if p <= t)
        ci = clopper_pearson(k, n)
        rows.append({"threshold": t, "n_at_or_below": k, "n": n,
                     "fraction": round(k / n, 4) if n else None,
                     "exact_95ci": ci,
                     "ci_width": round(ci[1] - ci[0], 4) if n else None})
    return rows


# ═══════════════════════════════════════ DECOYS ═══════════════════════════════════════════════

def decoy_pool(length_counts, exclude, multiple, seed):
    """Length-matched random peptides from the reviewed human proteome.

    Same proteome, same fetch and same scope as `junction_proteome_novelty.py` — imported rather
    than re-implemented so a decoy cannot be drawn from a different universe than the novelty test.
    """
    import junction_proteome_novelty as jpn  # noqa: PLC0415
    records = jpn.fetch_proteome()
    seqs = [s for _acc, _name, s in records if len(s) >= 12 and set(s) <= set("ACDEFGHIKLMNPQRSTVWY")]
    if not seqs:
        raise RuntimeError("proteome fetch returned no usable sequences")
    rng = random.Random(seed)
    pool, guard = [], 0
    want = {L: n * multiple for L, n in length_counts.items()}
    have = {L: 0 for L in want}
    while any(have[L] < want[L] for L in want) and guard < 5_000_000:
        guard += 1
        L = rng.choice([k for k in want if have[k] < want[k]])
        s = rng.choice(seqs)
        if len(s) < L:
            continue
        i = rng.randrange(0, len(s) - L + 1)
        pep = s[i:i + L]
        if pep in exclude:
            continue
        pool.append(pep)
        have[L] += 1
        exclude.add(pep)
    return pool, {"n_proteome_records": len(records), "n_usable_sequences": len(seqs),
                  "draws_attempted": guard, "per_length": have,
                  "proteome_source": jpn.PROTEOME_URL}


def presenting_allele_null(pool, panel, scored, n_peptides, threshold, draws, seed):
    """How many presenting alleles does a RANDOM peptide set of the screen's size buy at this cut?

    §7: "no decoy control and no null expectation ... the calls that pass are reported as what the
    screen returned rather than as an enrichment over chance." This is the missing null.
    """
    rng = random.Random(seed)
    counts = []
    for _ in range(draws):
        sample = rng.sample(pool, n_peptides)
        n = 0
        for allele in panel:
            if any(scored.get((p, allele), 101.0) <= threshold for p in sample):
                n += 1
        counts.append(n)
    counts.sort()
    mean = sum(counts) / len(counts)
    return {"draws": draws, "mean": round(mean, 3),
            "median": counts[len(counts) // 2],
            "p05": counts[int(0.05 * len(counts))], "p95": counts[int(0.95 * len(counts))],
            "max": counts[-1], "distribution": {str(v): counts.count(v) for v in sorted(set(counts))}}


# ═══════════════════════════════════════ MAIN ════════════════════════════════════════════════

def build_grid(strict):
    pts = {0.05, 0.1, 0.2, 0.3, 0.37, 0.4, 0.45, ctc.CONVENTIONAL, 0.75, 1.0, 1.5, 2.0, 3.0,
           ctc.LOOSE}
    for b in strict.get("strong_binders", []):
        pts.add(round(float(b["percentile"]), 4))
    return sorted(pts)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dump-schema-only", action="store_true",
                    help="fetch and record the live IEDB schema, then stop (a first-run probe)")
    ap.add_argument("--no-decoys", action="store_true", help="skip arm D (proteome fetch)")
    ap.add_argument("--use-cache", action="store_true",
                    help="reuse iedb-validated-epitope-cache.json instead of re-fetching")
    args = ap.parse_args(argv)

    strict = json.load(open(STRICT))
    panel = strict["panel"]
    grid = build_grid(strict)
    lengths = set(ctc.LENGTHS)

    result = {
        "_utc": _utcnow(),
        "_cost": "$0 — GitHub-hosted CPU runner; no GPU, no paid API.",
        "_what": ("Section 6.1 step 1 of emc-vaccine-development-path.md: the acceptance threshold "
                  "calibrated against experimentally validated epitopes, or the record that it "
                  "cannot be."),
        "_the_specification_quoted": (
            "Defend the acceptance threshold, or record that it cannot be defended. Computational, "
            "needs nothing but public data. Calibrate the cut against experimentally validated "
            "epitopes, and if no validated set restricted to fusion-junction peptides exists, that "
            "absence is itself the finding and Section 2.3's curve is the only honest report of "
            "coverage. Until this is done every figure in B1 is a point on a curve."),
        "_the_reading_taken": (
            "§6.1 step 1 says 'experimentally validated epitopes' unqualified; §B1 says calibrating "
            "on anything but fusion-junction epitopes 'would import an assumption about junction "
            "peptides that is the very thing in question'. Those pick different sets. The HARDER "
            "reading is taken: only arm F can settle the cut; arm N is the comparator §B1 refuses."),
        "⛔_what_this_is_not": (
            "A calibrated binding threshold is a calibrated binding threshold. Nothing here is "
            "evidence of presentation on a tumour, immunogenicity, efficacy, safety, a therapeutic "
            "window or clinical readiness. Arm F's epitopes were validated on OTHER fusions in "
            "OTHER diseases."),
        "⚠_circularity": (
            "MHCflurry is trained on IEDB, so an arm F or arm N epitope may be in its training set. "
            "The bias runs one way: every sensitivity here is an UPPER BOUND on the cut's true "
            "sensitivity, and a cut that misses validated epitopes here misses them a fortiori."),
        "_preregistered": {
            "min_n_for_a_calibration": MIN_N_FOR_A_CALIBRATION,
            "max_ci_width_for_a_calibration": MAX_CI_WIDTH_FOR_A_CALIBRATION,
            "declared": ("at the top of vaccine_threshold_calibration.py, before any datum is read, "
                         "so the sufficiency of the set cannot be decided by the count it returns"),
        },
        "_conventional_threshold": ctc.CONVENTIONAL,
        "_panel": panel,
        "_grid": grid,
        "_random_seed": RANDOM_SEED,
        "_sources": [
            "IEDB Query API (IQ-API), https://query-api.iedb.org — PostgREST over the Immune "
            "Epitope Database. Schema discovered at run time and recorded below.",
            "MHCflurry 2.x Class1PresentationPredictor, the same predictor and the same "
            "presentation-percentile column as epitope-allele-matrix.json.",
        ],
        "errors": [],
    }

    # ── schema ────────────────────────────────────────────────────────────────────────────────
    try:
        schema = discover_schema()
        result["_schema_discovery"] = {
            "info": schema["info"], "n_tables": schema["n_tables"],
            "columns_of_tables_used": {t: schema["tables"].get(t, []) for t in IEDB_TABLES},
        }
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"schema discovery failed: {exc}")
        result["_schema_discovery"] = None
        schema = None

    if args.dump_schema_only:
        json.dump(result, open(OUT, "w"), indent=2, ensure_ascii=False)
        print(f"  schema dumped to {OUT}")
        return 0 if schema else 1

    # ── fetch ─────────────────────────────────────────────────────────────────────────────────
    # ⛔ THE TWO ARMS ARE FETCHED SEPARATELY AND THEIR COMPLETENESS IS TRACKED SEPARATELY.
    # Arm F's probes are meant to be EXHAUSTIVE, so any error on them makes the absence claim
    # unclaimable (§4: an absent reading is not a reading of absence). Arm N is a bounded sample by
    # construction — the general validated-epitope pool is far larger than this job needs — and it
    # is labelled a sample rather than reported as if it were the population.
    kept_f, kept_n, dropped_f, dropped_n = [], [], {}, {}
    fusion_errors, general_errors, resolved_by_table = [], [], {}
    n_raw_fusion = n_raw_general = 0

    if args.use_cache and os.path.exists(IEDB_CACHE):
        cache = json.load(open(IEDB_CACHE))
        kept_f = cache["arm_F_records"]
        kept_n = cache["arm_N_records"]
        dropped_f = cache.get("dropped_fusion", {})
        dropped_n = cache.get("dropped_general", {})
        fusion_errors = cache.get("fusion_errors", [])
        general_errors = cache.get("general_errors", [])
        resolved_by_table = cache.get("resolved_columns", {})
        n_raw_fusion = cache.get("n_raw_fusion_rows", 0)
        n_raw_general = cache.get("n_raw_general_rows", 0)
        result["_fetch_provenance"] = f"cached {os.path.basename(IEDB_CACHE)} ({cache.get('_utc')})"
    elif schema:
        result["_fetch_provenance"] = "live IEDB fetch (this run)"
        raw_f, raw_g = [], []
        for table in IEDB_TABLES:
            if table not in schema["tables"]:
                fusion_errors.append(f"{table} not present in the live schema")
                continue
            cols, unresolved = resolve_columns(schema, table)
            resolved_by_table[table] = {"resolved": cols, "unresolved": unresolved}
            missing_required = [c for c in REQUIRED_COLUMNS if c not in cols]
            if missing_required:
                fusion_errors.append(
                    f"{table}: cannot resolve required column(s) {missing_required}; "
                    f"available = {schema['tables'][table]}")
                continue
            rows, errs = fetch_table(table, cols, IEDB_ANTIGEN_PROBES)
            raw_f.extend(rows)
            fusion_errors.extend(errs)
            grows, gerrs = fetch_general(table, cols, panel)
            raw_g.extend(grows)
            general_errors.extend(gerrs)
        n_raw_fusion, n_raw_general = len(raw_f), len(raw_g)
        cols_any = {}
        for t in IEDB_TABLES:
            cols_any.update((resolved_by_table.get(t) or {}).get("resolved", {}))
        all_f, dropped_f = normalise_rows(raw_f, cols_any, lengths) if raw_f else ([], {})
        all_g, dropped_n = normalise_rows(raw_g, cols_any, lengths) if raw_g else ([], {})
        # A record captured by a fusion probe but whose antigen name does not match the inclusion
        # rule falls back into the general pool rather than being discarded — a probe hit is not
        # itself evidence the antigen is a fusion.
        kept_f = [r for r in all_f if is_fusion(r)]
        kept_n = [r for r in all_g + [r for r in all_f if not is_fusion(r)] if not is_fusion(r)]
        seen = set()
        deduped = []
        for r in kept_n:
            key = (r["peptide"], r["allele"])
            if key not in seen:
                seen.add(key)
                deduped.append(r)
        kept_n = deduped
        # ⚠ THE CACHE HOLDS THE NORMALISED RECORDS, NOT THE RAW ROWS. The raw general pull is
        # hundreds of megabytes of assay metadata this calibration does not read; committing it
        # would be an artifact nobody diffs. Everything the calibration actually uses is here.
        json.dump({"_utc": _utcnow(),
                   "_note": ("the normalised IEDB records this calibration ran on — peptide, "
                             "4-digit HLA restriction, source antigen and which IEDB table it came "
                             "from. Raw assay rows are not kept; the counts of what was read and "
                             "what was dropped, with reasons, are."),
                   "resolved_columns": resolved_by_table,
                   "fusion_errors": fusion_errors, "general_errors": general_errors,
                   "n_raw_fusion_rows": n_raw_fusion, "n_raw_general_rows": n_raw_general,
                   "dropped_fusion": dropped_f, "dropped_general": dropped_n,
                   "arm_F_records": kept_f, "arm_N_records": kept_n},
                  open(IEDB_CACHE, "w"), indent=2, ensure_ascii=False)
    else:
        result["_fetch_provenance"] = "none — schema discovery failed"

    result["errors"].extend(fusion_errors + general_errors)
    result["_resolved_columns"] = resolved_by_table
    # ⛔ THE ABSENCE CLAIM HANGS ON THIS FLAG AND ON NOTHING ELSE.
    result["_fusion_fetch_is_complete"] = (not fusion_errors) and n_raw_fusion > 0

    # ── split, and bound arm N so the job's runtime is deterministic ───────────────────────────
    if len(kept_n) > ARM_N_MAX_PAIRS:
        rng = random.Random(RANDOM_SEED)
        kept_n = sorted(rng.sample(kept_n, ARM_N_MAX_PAIRS),
                        key=lambda d: (d["peptide"], d["allele"]))
        arm_n_sampled = True
    else:
        arm_n_sampled = False
    arm_f, arm_n = kept_f, kept_n
    result["_ingest"] = {
        "n_raw_fusion_rows": n_raw_fusion, "n_raw_general_rows": n_raw_general,
        "dropped_fusion_with_reason": dropped_f, "dropped_general_with_reason": dropped_n,
        "n_fusion_pairs": len(arm_f), "n_nonfusion_pairs": len(arm_n),
        "arm_N_is_a_bounded_sample": arm_n_sampled,
        "arm_N_max_pairs": ARM_N_MAX_PAIRS,
        "distinct_fusion_source_antigen_names": sorted(
            {a for r in arm_f for a in r["source_antigens"]}),
        "_inclusion_rule": ("a source-antigen name matching any of FUSION_NAME_PATTERNS; every "
                            "matched name is listed above so the rule is auditable, and a record "
                            "returned by a fusion probe whose name does not match is moved to arm "
                            "N rather than counted as a fusion epitope"),
        "_general_pool_is_not_exhaustive": (
            f"arm N pages at most {MAX_PAGES_GENERAL * PAGE} rows per allele per IEDB table. It is "
            f"a comparator, not a population estimate, and §B1 refuses it as a calibration anyway."),
    }

    # ── predict ───────────────────────────────────────────────────────────────────────────────
    try:
        predictor = load_predictor()
        supported = set(supported_alleles(predictor))
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"MHCflurry unavailable: {exc}")
        json.dump(result, open(OUT, "w"), indent=2, ensure_ascii=False)
        print("  MHCflurry unavailable; wrote what was fetched and stopped", file=sys.stderr)
        return 1

    def arm(records, label, note):
        scoreable = [r for r in records if r["allele"] in supported]
        unscreened = sorted({r["allele"] for r in records if r["allele"] not in supported})
        pairs = [(r["peptide"], r["allele"]) for r in scoreable]
        pct, column = score(predictor, pairs) if pairs else ({}, None)
        vals, rows = [], []
        for r in scoreable:
            p = pct.get((r["peptide"], r["allele"]))
            if p is None:
                continue
            vals.append(p)
            rows.append({"peptide": r["peptide"], "allele": r["allele"], "percentile": p,
                         "source_antigens": r["source_antigens"], "iedb_tables": r["tables"]})
        rows.sort(key=lambda d: d["percentile"])
        n = len(vals)
        conv = next((e for e in ecdf(vals, grid) if abs(e["threshold"] - ctc.CONVENTIONAL) < 1e-9),
                    None) if n else None
        return {
            "_label": label, "_note": note,
            "rank_column": column,
            "n_pairs": n,
            "n_distinct_peptides": len({r["peptide"] for r in rows}),
            "alleles_mhcflurry_cannot_score": unscreened,
            "⚠_unscreened_is_not_negative": ("an allele MHCflurry carries no model for is absent "
                                             "from these counts, never counted as a miss"),
            "ecdf": ecdf(vals, grid) if n else [],
            "at_the_conventional_cut": conv,
            "calls": rows,
        }

    result["arm_F_fusion_junction_validated"] = arm(
        arm_f, "THE CALIBRATION",
        "Experimentally validated MHC class I epitopes from fusion/chimeric source antigens. This "
        "is the only arm §B1 permits to settle the cut.")
    result["arm_N_nonfusion_validated"] = arm(
        arm_n, "⛔ NOT THE CALIBRATION — the comparator §B1 refuses",
        "Validated epitopes from non-fusion antigens on the paper's own panel. Reported so a reader "
        "can see what the refused calibration would have said. Quoting it as the calibration "
        "imports exactly the assumption about junction peptides that is under test.")

    # ── verdict on arm F ──────────────────────────────────────────────────────────────────────
    f = result["arm_F_fusion_junction_validated"]
    n_f = f["n_distinct_peptides"]
    conv = f["at_the_conventional_cut"]
    width = conv["ci_width"] if conv else None
    enough_n = n_f >= MIN_N_FOR_A_CALIBRATION
    enough_precision = width is not None and width <= MAX_CI_WIDTH_FOR_A_CALIBRATION
    result["verdict"] = {
        "n_distinct_validated_fusion_junction_epitopes": n_f,
        "meets_preregistered_min_n": enough_n,
        "ci_width_at_the_conventional_cut": width,
        "meets_preregistered_ci_width": enough_precision,
        "the_set_is_a_calibration_set": bool(enough_n and enough_precision),
        "_the_fusion_probe_fetch_was_complete": result["_fusion_fetch_is_complete"],
        "⛔_absence_is_only_claimable_if_the_fetch_was_complete": (
            "If _fusion_fetch_is_complete is false, a small arm F is a reading the collector could not "
            "take, NOT a reading of absence, and the finding below must not be quoted."),
    }
    if not result["_fusion_fetch_is_complete"]:
        result["verdict"]["finding"] = (
            "WITHHELD. The IEDB fetch did not complete, so the size of the validated "
            "fusion-junction set was not measured on this run.")
    elif enough_n and enough_precision:
        result["verdict"]["finding"] = (
            f"A validated fusion-junction set of {n_f} epitopes exists and the acceptance threshold "
            f"is calibratable against it. See arm_F.at_the_conventional_cut for what the "
            f"conventional cut of {ctc.CONVENTIONAL} captures, read as an UPPER BOUND (see "
            f"⚠_circularity).")
    else:
        result["verdict"]["finding"] = (
            f"THE THRESHOLD CANNOT BE DEFENDED BY CALIBRATION. {n_f} distinct experimentally "
            f"validated fusion-junction epitopes are scoreable here, against a pre-registered floor "
            f"of {MIN_N_FOR_A_CALIBRATION}. Section 6.1 step 1's own fallback therefore applies: "
            f"'that absence is itself the finding and Section 2.3's curve is the only honest report "
            f"of coverage.' Every figure in B1 remains a point on a curve.")

    # ── arm D: the decoy null §7 says the screen lacks ────────────────────────────────────────
    if not args.no_decoys:
        try:
            bp = json.load(open(BREAKPOINTS))
            junction_peps = sorted({p for j in bp.get("junctions", [])
                                    for p in j.get("novel_peptides", []) if len(p) in lengths})
            length_counts = {}
            for p in junction_peps:
                length_counts[len(p)] = length_counts.get(len(p), 0) + 1
            exclude = set(junction_peps) | {r["peptide"] for r in arm_f + arm_n}
            pool, prov = decoy_pool(length_counts, exclude, DECOY_MULTIPLE, RANDOM_SEED)
            pairs = [(p, a) for p in pool for a in panel]
            pct, column = score(predictor, pairs)
            per_threshold = []
            for t in grid:
                k = sum(1 for v in pct.values() if v <= t)
                ci = clopper_pearson(k, len(pct))
                per_threshold.append({"threshold": t, "n_pass": k, "n_peptide_allele_tests": len(pct),
                                      "pass_rate": round(k / len(pct), 6) if pct else None,
                                      "exact_95ci": ci})
            null = presenting_allele_null(pool, panel, pct, len(junction_peps),
                                          ctc.CONVENTIONAL, NULL_DRAWS, RANDOM_SEED + 1)
            observed = len(strict["presenting_alleles"])
            dist = null["distribution"]
            ge = sum(v for k2, v in dist.items() if int(k2) >= observed)
            result["arm_D_decoy_null"] = {
                "_label": "THE NULL §7 SAYS THE SCREEN LACKS",
                "_note": ("§7: 'no decoy control and no null expectation ... the calls that pass are "
                          "reported as what the screen returned rather than as an enrichment over "
                          "chance.' These are length-matched random peptides from the same reviewed "
                          "human proteome the novelty search uses, over the same panel."),
                "rank_column": column,
                "n_decoy_peptides": len(pool), "decoy_multiple": DECOY_MULTIPLE,
                "provenance": prov,
                "pass_rate_by_threshold": per_threshold,
                "presenting_alleles_under_the_null_at_the_conventional_cut": null,
                "observed_presenting_alleles_in_the_screen": observed,
                "p_value_random_set_reaches_the_observed_count": round(ge / NULL_DRAWS, 5),
                "⚠_what_this_p_value_is": (
                    "the fraction of random length-matched peptide sets of the screen's own size "
                    "that present on at least as many panel alleles as the screen did, at the "
                    "conventional cut. It is a null for the SCREEN, not a test of any peptide."),
            }
            fconv = f["at_the_conventional_cut"]
            dconv = next((r for r in per_threshold
                          if abs(r["threshold"] - ctc.CONVENTIONAL) < 1e-9), None)
            if fconv and fconv["fraction"] is not None and dconv and dconv["pass_rate"]:
                result["arm_D_decoy_null"]["likelihood_ratio_at_the_conventional_cut"] = {
                    "value": round(fconv["fraction"] / dconv["pass_rate"], 2),
                    "_meaning": ("P(pass | validated fusion-junction epitope) / P(pass | decoy). A "
                                 "calibration statement that needs no prior on how many junction "
                                 "peptides are real epitopes."),
                    "⚠": ("carries arm F's sample size, so read it beside verdict.the_set_is_a_"
                          "calibration_set; a ratio from a handful of epitopes is a ratio from a "
                          "handful of epitopes."),
                }
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"arm D (decoy null) failed: {exc}")
            result["arm_D_decoy_null"] = None

    json.dump(result, open(OUT, "w"), indent=2, ensure_ascii=False)
    v = result["verdict"]
    print(f"  arm F: {v['n_distinct_validated_fusion_junction_epitopes']} distinct validated "
          f"fusion-junction epitopes (floor {MIN_N_FOR_A_CALIBRATION}); "
          f"calibration set = {v['the_set_is_a_calibration_set']}; "
          f"fusion fetch complete = {result['_fusion_fetch_is_complete']}")
    print(f"  -> {v['finding']}")
    if result["errors"]:
        print(f"  {len(result['errors'])} error(s) recorded in the artifact", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
