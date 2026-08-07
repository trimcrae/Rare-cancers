#!/usr/bin/env python3
"""C05 / Q7 — THE $0 KNOWN-ANSWER PRECHECK FOR `V18`, THE TRANSFER-ZONE LYSINE-IDENTITY INSTRUMENT.

WHAT IT DECIDES
---------------
Roadmap §3.1 records `V18` as having **"none exists"** for its known-answer test. `V18` is one of the
three categorical axes the program stands on and the ONLY one with no known-answer test of any kind
(`instrument-options.json` → `candidates[C05].why_it_is_high_value`). This module answers exactly one
question and refuses to answer any other:

    For a PROTAC/molecular-glue substrate that has a SOLVED TERNARY, does a MEASURED reference exist
    that NAMES WHICH LYSINE matters -- an MS-mapped ubiquitination site, or a lysine-mutant rescue?

If the answer is no, `V18` is closed on EVIDENCE rather than left as an untested instrument, and that
is a strictly better state than the one it is in (the register says so in those words).

⛔ AND A `found` VERDICT IS NOT A WIN. THE REGISTER PREDICTED THE ANSWER BEFORE THE SEARCH RAN
-----------------------------------------------------------------------------------------------
`instrument-options.json` → `candidates[C05].does_not_license` states, written before any retrieval:

    "that the paralogue is spared -- real degraders often ubiquitinate several lysines and
     lysine-less substrates can still be degraded; this raises the odds, it does not guarantee"

So the honest verdict space has FOUR values, not two, and the third is the one the register expects:

  FOUND_AND_DIAGNOSTIC            a measured reference exists AND it names ONE lysine, so a model that
                                  predicts one lysine can be scored right or wrong against it.
  FOUND_BUT_WEAKLY_DIAGNOSTIC     a measured reference exists and names SEVERAL lysines, or the source
                                  itself reports redundancy / lysine-less degradation. ⚠ THE REGISTER'S
                                  OWN PREDICTION. A reference that cannot separate a right answer from
                                  a wrong one is not a known answer for THIS purpose, however real the
                                  measurement is -- the same argument that disqualifies `V10`'s
                                  qualified set from speaking to paralogue scale.
  STOP_NO_REFERENCE               the corpus read cleanly and no measured lysine-naming reference on a
                                  ternary-solved substrate is in it. Close `V18` on evidence.
  UNDETERMINED                    the corpus could not be read. NOT a negative -- re-run the retrieval.
                                  An absent reading is not a reading of absence (CLAUDE.md §4).

⚠ THE GRADE IS APPLIED TO THE FIND, NOT INSTEAD OF IT. This module never suppresses a hit; it reports
every candidate span with its source and then states what the find can and cannot license.

WHY THE RETRIEVAL IS NOT IN THIS FILE, AND WHY THAT IS NOT A DEFERRAL
---------------------------------------------------------------------
The dev sandbox's egress proxy answers `www.ebi.ac.uk` with 403 at CONNECT, so Europe PMC cannot be
read here (CLAUDE.md §6). The retrieval is routed to the on-main `fetch-literature.yml` `query` path,
which pages the ENTIRE Europe PMC result set with `cursorMark` (`scripts/fetch-paper.mjs sync`),
writes `_index.json` plus one `PMCxxxxxxx.txt` per open-access hit, and publishes the corpus to the
`literature-cache` branch under `literature/<slug>/`. This module then reads that corpus OFFLINE and
is pure -- which is deliberate, because it means the gate can be unit-tested without a network and a
future reader can re-run the adjudication over the same committed corpus and get the same verdict.

  retrieval  ->  fetch-literature.yml (CI, $0)  ->  origin/literature-cache
  adjudication -> this module (pure, offline)   ->  v18-lysine-reference-precheck.json

⛔ A CORPUS THAT WAS NOT RETRIEVED IS `UNDETERMINED`, NEVER `STOP_NO_REFERENCE`. `load_corpus` reports
a missing or empty index as a LOAD FAILURE and `verdict()` refuses to emit a negative on one.

THE PRE-REGISTRATION
--------------------
Every threshold below is fixed before a record is read and is echoed into the artifact beside the
result, so a reader can check that no cut was chosen after seeing data (the same discipline
`ddddg_known_answer_search.PREREG` applies to C01).

  G1  MEASURED and PRIMARY, and it must NAME A RESIDUE. A sentence saying a substrate "is
      ubiquitinated" is not a mapped site; a sentence saying "K456 and K470 carried diGly remnants"
      is. The residue token is the discriminator and it is required, because the whole quantity
      `V18` produces is a lysine IDENTITY.
  G2  THE SUBSTRATE MUST HAVE A SOLVED TERNARY. Without one the transfer-zone model has nothing to be
      pointed at, so a mapped site on it cannot score the instrument even if the measurement is
      perfect. The gene list is READ from `s-calibrator-survey.json` -- the repo's own RCSB-derived
      survey of PROTAC ternaries -- and never typed here (rule 1).
  G3  DIAGNOSTICITY, judged against the register's prediction. Count the DISTINCT lysines a candidate
      span names, and detect whether the same source reports redundancy (lysine-less degradation,
      "multiple lysines", "no single lysine"). Either condition drops the verdict to
      FOUND_BUT_WEAKLY_DIAGNOSTIC.

WHAT THIS MODULE DOES NOT DO
----------------------------
It does not raise any claim ceiling. Roadmap §2.3 is untouched: `V18` is at `proposed`, no requirement
may be claimed above it, and finding a benchmark is not passing one. It computes no geometry, no
distance, no free energy, and it says nothing about NR4A3, about paralogue sparing, about degradation,
efficacy or safety.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "v18-lysine-reference-precheck.json")
SURVEY = os.path.join(HERE, "s-calibrator-survey.json")

#: How many NON-qualifying spans to emit as context. Qualifying spans are never capped — see `build`.
NON_QUALIFYING_SPAN_CAP = 60

#: Where the CI retrieval lands. Slugs are the ones dispatched; each is a separate Europe PMC query so
#: that a null is a null across two real searches rather than across one guess.
CORPUS_SLUGS = [
    ("v18-ubiquitination-site-known-answer",
     "MS / diGly site-mapping for degrader substrates -- the 'which lysine carried the remnant' arm"),
    ("v18-lysine-mutant-rescue-known-answer",
     "lysine-to-arginine mutants and lysine-less constructs -- the 'which lysine, by rescue' arm"),
]

# =================================================================================================
# PRE-REGISTRATION -- fixed before any record is read
# =================================================================================================
PREREG = {
    "require_named_residue": True,
    "_why_named_residue": (
        "the quantity V18 produces is a lysine IDENTITY, so a reference that establishes only THAT a "
        "substrate is ubiquitinated cannot score it. A residue token (K123 / Lys123) in the same "
        "sentence as a measurement token is the minimum that could."),
    "require_solved_ternary_substrate": True,
    "_why_solved_ternary": (
        "the transfer-zone model is built ON a ternary geometry. A mapped site on a substrate with no "
        "solved ternary has nothing to be predicted against, so it is a real measurement and not a "
        "known answer for this instrument. The gene list is READ from s-calibrator-survey.json."),
    "diagnosticity_max_distinct_lysines": 1,
    "_why_one_lysine": (
        "⚠ THE REGISTER PREDICTED THIS BEFORE THE SEARCH RAN. C05.does_not_license says real degraders "
        "often ubiquitinate SEVERAL lysines and lysine-less substrates can still be degraded. A model "
        "that names one lysine cannot be scored right-or-wrong against a reference naming five: every "
        "prediction hits. That is the same defect that stops V10's hot-spot pass from speaking to "
        "paralogue scale -- a control whose answer cannot discriminate is not a control."),
    "redundancy_drops_to_weak": True,
    "_why_redundancy_drops": (
        "if the SOURCE ITSELF reports that removing the mapped lysine does not stop degradation, then "
        "the mapped site is not the causal site, and predicting it correctly would license nothing."),
    "span_min_chars": 25,
    "span_max_chars": 700,
    "max_spans_per_paper": 25,
}


def null_rejection_rule():
    """What result would count as a refutation, written down before the search. One home."""
    return (
        "This precheck REFUTES the premise that V18 can be bought a known answer if, across both "
        "retrieved corpora read in full, no span names a specific lysine of a ternary-solved degrader "
        "substrate together with a measurement token -- in which case V18 is closed on evidence and "
        "its 'none exists' row in roadmap §3.1 becomes a measured finding rather than an unchecked "
        "one. It SUPPORTS the premise only if such a span exists AND the source names a SINGLE "
        "lysine AND does not itself report redundancy. Anything between is reported as "
        "FOUND_BUT_WEAKLY_DIAGNOSTIC and is explicitly NOT a usable known answer for V18, however "
        "real the underlying measurement is."
    )


def caveat():
    """The sentence any use of this artifact MUST carry. One home, so it cannot be dropped."""
    return (
        "Finding a mapped ubiquitination site is not passing a known-answer test, and a WEAKLY "
        "DIAGNOSTIC find is not a partial pass -- it is a reference that cannot separate a right "
        "answer from a wrong one, which is the same state V18 was already in. Nothing here licenses "
        "any statement about NR4A3, about paralogue sparing, about degradation, efficacy or safety, "
        "and roadmap §2.3's claim ceiling is unchanged: V18 remains at `proposed`."
    )


# =================================================================================================
# G2 -- the substrates that HAVE a solved ternary, READ from the repo's own survey
# =================================================================================================
def ternary_solved_substrates(path=SURVEY):
    """Genes with at least one solved PROTAC ternary, read off s-calibrator-survey.json. Pure-ish.

    Returns {"genes": [...], "by_gene": {gene: {"n_ternary": n, "pdb_ids": [...]}}, "error": ...}.
    An unreadable survey is an ERROR, never an empty gene list -- an empty list would silently make
    G2 reject everything and the run would report STOP_NO_REFERENCE off a load failure, which is the
    absent-reading-as-absence failure this repo has already paid for twice.
    """
    out = {"_source": os.path.basename(path), "genes": [], "by_gene": {}, "error": None}
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out
    for cand in doc.get("candidates") or []:
        for arm_key in ("arm_a", "arm_b"):
            arm = cand.get(arm_key) or {}
            gene, n = arm.get("gene"), arm.get("n_ternary") or 0
            if not gene or not n:
                continue
            rec = out["by_gene"].setdefault(gene, {"n_ternary": 0, "pdb_ids": []})
            rec["n_ternary"] = max(rec["n_ternary"], int(n))
            for p in arm.get("ternary_pdb_ids") or []:
                if p not in rec["pdb_ids"]:
                    rec["pdb_ids"].append(p)
    out["genes"] = sorted(out["by_gene"])
    if not out["genes"]:
        out["error"] = ("the survey parsed but named ZERO ternary-solved substrates -- treat as a LOAD "
                        "FAILURE, not as the finding that none exists")
    return out


#: Aliases a paper may use for a survey gene. Deliberately small and explicit: a loose alias list is
#: how a promiscuous substring match returned a value from an unrelated system in the pmx precheck
#: (`pmx_mutation_reference`, measured 2026-08-02), and the same trap is available here.
GENE_ALIASES = {
    "SMARCA2": ["smarca2", "brm", "brahma"],
    "SMARCA4": ["smarca4", "brg1", "brg-1"],
    "BRD4": ["brd4"],
    "IKZF1": ["ikzf1", "ikaros"],
    "IKZF3": ["ikzf3", "aiolos"],
    "FKBP51": ["fkbp51", "fkbp5"],
    "WEE1": ["wee1"],
}

# =================================================================================================
# The tokens. A span qualifies only when it carries ALL THREE, because each alone is insufficient:
#   a residue with no measurement is a construct description;
#   a measurement with no residue is a degradation curve;
#   either with no ubiquitin context is a binding experiment.
# =================================================================================================
_LYS = re.compile(r"\b(?:K|Lys|lysine[ -]?)\s?(\d{1,4})\b")
_UBI_CONTEXT = re.compile(
    r"(ubiquitinat|ubiquitylat|ubiquitin\b|diGly|di-Gly|di-glycine|GG remnant|K-GG|KGG|"
    r"polyubiquit|neddylat)", re.I)

#: ⛔ THE UBIQUITIN CHAIN-LINKAGE LYSINES ARE NOT SUBSTRATE SITES, AND COUNTING THEM AS SUCH WAS A
#: REAL DEFECT IN THE FIRST DRAFT OF THIS MODULE (caught on the first dry run, 2026-08-07). K48 and
#: K63 are positions on UBIQUITIN ITSELF, naming the linkage type of the chain; a sentence saying
#: "K48-linked ubiquitination of IRE1" names ZERO substrate sites, and the draft scored it as one.
#: Left in, the artifact would have reported dozens of spurious "named lysines" — a populated field
#: read as a measured one, which is the failure CLAUDE.md §4(b) names.
#:
#: ⚠ IT IS NOT ENOUGH TO BLACKLIST THE NUMBERS, because a substrate can genuinely have a Lys48. The
#: exclusion therefore requires BOTH the canonical position AND a linkage cue in the same span, and
#: every exclusion is REPORTED rather than silently dropped, so a reader can disagree with it.
UBIQUITIN_LINKAGE_POSITIONS = (6, 11, 27, 29, 33, 48, 63)
_LINKAGE_CUE = re.compile(
    r"(-?link(ed|age)|chain|polyubiquit|poly-?Ub\b|branched|K\d{1,2}\s?/\s?K\d{1,2})", re.I)


def linkage_lysines(text):
    """Numbers in `text` that are ubiquitin CHAIN-LINKAGE positions rather than substrate sites. Pure."""
    if not _LINKAGE_CUE.search(text or ""):
        return []
    return sorted({int(m) for m in _LYS.findall(text or "")
                   if int(m) in UBIQUITIN_LINKAGE_POSITIONS})
_MEASURED = re.compile(
    r"(mass spectrom|\bMS/MS\b|\bLC-MS\b|proteomic|remnant profil|site-?mapping|mapped to\b|"
    r"identified .{0,30}\bsite|\bK\d{1,4}R\b|lysine[- ]to[- ]arginine|arginine substitut|"
    r"lysine[- ]less|lysine[- ]free|rescu|abolish|abrogat|\bmutant\b|mutagenes)", re.I)

#: The source reporting its OWN redundancy. These are the phrases that drop a find to WEAK regardless
#: of how many lysines a single span names, because they say the mapped site is not decisive.
_REDUNDANCY = re.compile(
    r"(lysine[- ]less|lysine[- ]free|without any lysine|no single lysine|multiple lysines|"
    r"several lysines|redundan|still (?:degraded|ubiquitinated|ubiquitylated)|"
    r"did not (?:prevent|abolish|block) degradation|not required for degradation)", re.I)


def spans(text, prereg=None):
    """Sentences carrying a lysine number AND a ubiquitin context AND a measurement token. Pure.

    Returns raw sentences so a human re-reads the source rather than trusting a parse -- the rule
    `selcal_reference_selectivity` established and every precheck in this repo inherits.
    """
    p = prereg or PREREG
    out, seen = [], set()
    for sent in re.split(r"(?<=[.!?])\s+", text or ""):
        s = " ".join(sent.split())
        if not (p["span_min_chars"] <= len(s) <= p["span_max_chars"]):
            continue
        if not (_LYS.search(s) and _UBI_CONTEXT.search(s) and _MEASURED.search(s)):
            continue
        key = s[:160].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= p["max_spans_per_paper"]:
            break
    return out


def lysines_named(text):
    """Distinct SUBSTRATE lysine residue numbers named in a text. Pure. Sorted, deduplicated.

    Ubiquitin chain-linkage positions in a linkage context are excluded — see
    `UBIQUITIN_LINKAGE_POSITIONS`. Use `linkage_lysines` to see what was removed.
    """
    excluded = set(linkage_lysines(text))
    return sorted({int(m) for m in _LYS.findall(text or "")} - excluded)


def substrate_hits(text, genes, aliases=None):
    """Which ternary-solved substrate genes a text names. Pure.

    ⚠ Matched on explicit aliases only, never on a bare gene substring, and returned as a LIST so a
    reader can see WHICH substrate the span is about. A span mentioning three substrates is reported
    with three, and the adjudication of which one the measurement belongs to is a human's.

    ⛔ G2 CALLS THIS ON THE SPAN, NEVER ON THE PAPER, AND THE DIFFERENCE IS NOT COSMETIC (caught on
    the first dry run, 2026-08-07). Called paper-wide, a sentence measuring ubiquitination of IRE1
    scored as a BRD4 hit because the paper's introduction mentioned BRD4 somewhere — the measurement
    and the substrate came from different sentences and the gate could not tell. Paper-level hits are
    still reported, as `substrates_named_anywhere_in_paper`, and are explicitly NOT the gate: they
    are context for a human, and treating context as evidence is how a promiscuous substring returned
    a value from an unrelated system in `pmx_mutation_reference` (measured 2026-08-02).
    """
    aliases = aliases or GENE_ALIASES
    low = (text or "").lower()
    hits = []
    for gene in genes:
        for alias in aliases.get(gene, [gene.lower()]):
            if re.search(_alias_pattern(alias), low):
                hits.append(gene)
                break
    return hits


#: Structural-domain suffixes a paper glues straight onto a gene name: `Brd4BD2`, `BRD4BD1`,
#: `SMARCA2BD`, `BCL6BTB`. ⛔ A PLAIN `\balias\b` MISSES ALL OF THEM, and that is a false NEGATIVE in
#: the gate's favour, which is the dangerous direction (dry run, 2026-08-07): the first fix to the
#: paper-vs-span defect above dropped the two most decisive spans in the whole corpus — the eight
#: mapped sites on Brd4BD2 and the K456R single-mutant result — because both write the domain form.
#: A gate that silently loses its own best evidence and reports STOP is exactly the absent-reading
#: failure, arriving from inside the parser instead of from the network.
_DOMAIN_SUFFIX = r"(?:bd|brd|btb|lbd|dom)\d?"


def _alias_pattern(alias):
    """Word-bounded alias that also matches an immediately-suffixed structural domain. Pure."""
    return r"\b%s(?:\b|(?=%s))" % (re.escape(alias), _DOMAIN_SUFFIX)


# =================================================================================================
# Corpus loading -- from the literature-cache checkout, offline
# =================================================================================================
def load_corpus(root, slugs=None):
    """Read `literature/<slug>/_index.json` + its full texts. Pure w.r.t. the network.

    `root` is a checkout (or export) of the `literature-cache` branch. A missing or empty index is
    reported as `loaded: False` with the reason, and NEVER as zero records.
    """
    corpora = []
    for slug, why in (slugs or CORPUS_SLUGS):
        d = os.path.join(root, "literature", slug)
        row = {"slug": slug, "why_this_query": why, "dir": d, "loaded": False,
               "n_records": 0, "n_full_texts_on_disk": 0, "records": [], "error": None}
        index_path = os.path.join(d, "_index.json")
        if not os.path.isdir(d):
            row["error"] = ("corpus directory absent -- the CI retrieval has not landed on "
                            "literature-cache yet. An ABSENT reading, not an absence.")
            corpora.append(row)
            continue
        try:
            with open(index_path, encoding="utf-8") as fh:
                index = json.load(fh)
        except (OSError, ValueError) as e:
            row["error"] = "%s reading %s: %s" % (type(e).__name__, os.path.basename(index_path), e)
            corpora.append(row)
            continue
        if not isinstance(index, list) or not index:
            row["error"] = ("_index.json is empty or not a list -- a query that matched nothing is a "
                            "LOAD FAILURE for this gate, not a negative finding")
            corpora.append(row)
            continue
        row["loaded"] = True
        row["n_records"] = len(index)
        for rec in index:
            ft = rec.get("fullTextFile")
            text = ""
            if ft:
                try:
                    with open(os.path.join(d, ft), encoding="utf-8") as fh:
                        text = fh.read()
                    row["n_full_texts_on_disk"] += 1
                except OSError:
                    text = ""
            row["records"].append({
                "pmid": rec.get("pmid"), "pmcid": rec.get("pmcid"), "doi": rec.get("doi"),
                "year": rec.get("year"), "title": rec.get("title"),
                "journal": rec.get("journal"),
                "abstract": rec.get("abstract") or "",
                "full_text": text,
                "has_full_text": bool(text),
            })
        corpora.append(row)
    return corpora


def scan(corpora, ternary):
    """Every candidate span in the corpus, with its source and its diagnosticity fields. Pure."""
    genes = ternary.get("genes") or []
    candidates, n_scanned, n_with_ft = [], 0, 0
    for c in corpora:
        if not c.get("loaded"):
            continue
        for rec in c["records"]:
            n_scanned += 1
            n_with_ft += 1 if rec["has_full_text"] else 0
            body = (rec["abstract"] + "\n" + rec["full_text"]).strip()
            found = spans(body)
            if not found:
                continue
            paper_subs = substrate_hits(body, genes)
            for s in found:
                lys = lysines_named(s)
                span_subs = substrate_hits(s, genes)
                candidates.append({
                    "slug": c["slug"],
                    "pmid": rec["pmid"], "pmcid": rec["pmcid"], "doi": rec["doi"],
                    "year": rec["year"], "title": rec["title"], "journal": rec["journal"],
                    "read_from": "full_text" if rec["has_full_text"] else "abstract_only",
                    "quoted_span": s,
                    "lysines_named_in_span": lys,
                    "n_lysines_named_in_span": len(lys),
                    "ubiquitin_linkage_lysines_excluded_from_that_count": linkage_lysines(s),
                    "ternary_solved_substrates_named_IN_THE_SPAN": span_subs,
                    "substrates_named_anywhere_in_paper": paper_subs,
                    "_paper_level_is_context_not_evidence": (
                        "G2 is decided on the SPAN. A substrate named elsewhere in the paper does not "
                        "make this sentence a measurement about it."),
                    "passes_G2_ternary_solved_substrate": bool(span_subs) and bool(lys),
                    "source_reports_redundancy": bool(_REDUNDANCY.search(body)),
                    "_adjudication_is_a_humans": (
                        "this span was selected by token co-occurrence, not understood. Whether the "
                        "named lysine is THE ubiquitinated residue of THAT substrate under THAT "
                        "degrader is a judgement to be made against the quoted text and the source."),
                })
    return {"n_records_scanned": n_scanned, "n_with_full_text": n_with_ft,
            "n_candidate_spans": len(candidates), "candidates": candidates}


# =================================================================================================
# The gate
# =================================================================================================
def verdict(corpora, ternary, scanned, prereg=None):
    """Apply G1/G2/G3 mechanically. Pure. Four-valued, and the third value is the register's guess."""
    p = prereg or PREREG
    gates, blockers = {}, []

    loaded = [c for c in corpora if c.get("loaded")]
    failed = [{"slug": c["slug"], "error": c["error"]} for c in corpora if not c.get("loaded")]
    if not loaded:
        blockers.append("no corpus loaded: %s" % json.dumps(failed))
    elif failed:
        blockers.append("%d of %d corpora did not load, so a negative would be a partial read: %s"
                        % (len(failed), len(corpora), json.dumps(failed)))
    if ternary.get("error"):
        blockers.append("the ternary-solved substrate list could not be read (%s), so G2 cannot be "
                        "applied and its rejections would be meaningless" % ternary["error"])

    g1 = [c for c in scanned["candidates"]]
    g2 = [c for c in g1 if c["passes_G2_ternary_solved_substrate"]]
    gates["G1_measured_and_names_a_residue"] = {
        "n_spans": len(g1),
        "pass": bool(g1),
        "_what": "a span carrying a lysine number AND a ubiquitin context AND a measurement token",
    }
    gates["G2_substrate_has_a_solved_ternary"] = {
        "n_spans": len(g2),
        "n_distinct_spans": len({c["quoted_span"] for c in g2}),
        "n_distinct_papers": len({(c["pmcid"] or c["pmid"] or c["title"] or "?") for c in g2}),
        "distinct_papers": sorted({(c["pmcid"] or c["pmid"] or c["title"] or "?") for c in g2}),
        "_why_three_counts": ("a paper matching BOTH queries is retrieved into both corpora, so the "
                              "raw span count double-counts it. Quote the distinct figures."),
        "pass": bool(g2),
        "_what": "the paper names a substrate the repo's own RCSB survey records a solved ternary for",
        "_gene_list_source": ternary.get("_source"),
        "_genes": ternary.get("genes"),
    }

    # ⚠ A PAPER THAT MATCHES BOTH QUERIES IS RETRIEVED INTO BOTH CORPORA, so the same sentence can
    # appear twice and the raw span count over-states the evidence. The counts below are reported
    # BOTH ways rather than one being quietly chosen: `n_spans` is what the scan produced, and the
    # distinct figures are what a reader should quote.
    distinct_papers = sorted({(c["pmcid"] or c["pmid"] or c["title"] or "?") for c in g2})
    distinct_spans = {c["quoted_span"] for c in g2}
    distinct = sorted({n for c in g2 for n in c["lysines_named_in_span"]})
    redundant = [c for c in g2 if c["source_reports_redundancy"]]
    multi = [c for c in g2 if c["n_lysines_named_in_span"] > p["diagnosticity_max_distinct_lysines"]]
    gates["G3_diagnosticity"] = {
        "n_spans_naming_more_than_one_lysine": len(multi),
        "n_spans_whose_source_reports_redundancy": len(redundant),
        "⚠_the_redundancy_count_UNDER-DETECTS_and_a_zero_is_not_an_absence": (
            "`_REDUNDANCY` is a keyword matcher over a fixed phrase list, so it catches 'lysine-less' "
            "and 'still degraded' and misses redundancy stated in other words. MEASURED on this very "
            "corpus: a qualifying span reads 'the single K456R mutant had comparable ubiquitination "
            "and degradation relative to wild-type Brd4BD2' — which IS the mapped site failing to be "
            "decisive — and this detector does not fire on it. ⛔ So a zero here means THIS DETECTOR "
            "SAW NOTHING, not that no source reports redundancy; read the quoted spans. The phrase "
            "list was deliberately NOT widened after seeing that sentence, because tuning a "
            "pre-registered criterion to the data it is about to judge is how a gate stops being a "
            "gate. It does not change this verdict, which the multi-lysine criterion already "
            "decides — and had redundancy been the ONLY route to WEAK, this under-detection would "
            "have flipped the answer, which is exactly why it is recorded rather than left implicit."),
        "distinct_lysine_numbers_across_qualifying_spans": distinct[:60],
        "pass": bool(g2) and not multi and not redundant,
        "_what": ("whether a find could SCORE a model that names one lysine, or whether every "
                  "prediction would hit"),
    }

    if blockers:
        decision = "UNDETERMINED"
        sentence = ("The instruments could not be read cleanly, so this run establishes NOTHING about "
                    "whether a reference exists. Re-run the retrieval. " + " | ".join(blockers))
    elif not g2:
        decision = "STOP_NO_REFERENCE"
        sentence = (
            "Across %d records read in full from %d Europe PMC corpora, no span names a specific "
            "lysine of a ternary-solved degrader substrate together with a ubiquitin context and a "
            "measurement token. V18's known-answer test is CLOSED ON EVIDENCE: roadmap §3.1's 'none "
            "exists' becomes a measured finding rather than an unchecked assumption. This forecloses "
            "nothing about the instrument's correctness -- it establishes that it cannot be scored."
            % (scanned["n_records_scanned"], len(loaded)))
    elif not gates["G3_diagnosticity"]["pass"]:
        decision = "FOUND_BUT_WEAKLY_DIAGNOSTIC"
        sentence = (
            "A measured lysine-naming reference on a ternary-solved substrate EXISTS (%d distinct "
            "span(s) across %d distinct paper(s)), and it is NOT a usable known answer for V18: %d "
            "span(s) name more than one lysine and %d sit in a source that reports redundancy "
            "(lysine-less or multi-lysine degradation). Across the qualifying spans %d DISTINCT "
            "lysine positions are named. ⚠ THIS IS THE OUTCOME THE REGISTER PREDICTED BEFORE THE "
            "SEARCH RAN (C05.does_not_license). A reference that every prediction hits cannot "
            "separate a right answer from a wrong one, so V18 stays at `proposed` and no claim "
            "ceiling moves."
            % (len(distinct_spans), len(distinct_papers), len(multi), len(redundant), len(distinct)))
    else:
        decision = "FOUND_AND_DIAGNOSTIC"
        sentence = (
            "A measured reference exists on a ternary-solved substrate and names a single lysine in "
            "every qualifying span, with no redundancy reported by the source. ⚠ This is a CANDIDATE "
            "known answer, not a passed test: the adjudication of whether the named lysine is the "
            "ubiquitinated residue of that substrate under that degrader is a human's, against the "
            "quoted spans. Finding a benchmark is not passing one.")

    return {
        "decision": decision,
        "sentence": sentence,
        "gates": gates,
        "blockers": blockers,
        "corpora_that_failed_to_load": failed,
        "register_prediction_being_graded_against": (
            "instrument-options.json candidates[C05].does_not_license: 'real degraders often "
            "ubiquitinate several lysines and lysine-less substrates can still be degraded; this "
            "raises the odds, it does not guarantee'"),
        "prediction_outcome": (
            "CONFIRMED" if decision == "FOUND_BUT_WEAKLY_DIAGNOSTIC" else
            "NOT REACHED (no reference to grade)" if decision == "STOP_NO_REFERENCE" else
            "NOT CONFIRMED -- a single-lysine reference survived the gate, which the register did not "
            "expect; read the spans before believing it" if decision == "FOUND_AND_DIAGNOSTIC" else
            "UNTESTED -- the corpus did not load"),
    }


# =================================================================================================
# Routed roadmap edits -- DESCRIBED, NOT APPLIED (verified by verify_map_edits.py)
# =================================================================================================
def map_edits_required(v):
    """The roadmap edits this precheck's outcome calls for, ready for `verify_map_edits.py`.

    ⛔ This module does not touch nr4a3-program-map.md. Per CLAUDE.md the map is held elsewhere, and
    per the categorical audit's nine dead-on-arrival edits every anchor here is checked against the
    LIVE map before hand-off rather than after.
    """
    return [
        {
            "section": "§10.1a row Q7",
            "anchor": ("**Instrument candidate `C05` — the `V18` known-answer precheck**: does a "
                       "measured ubiquitination-site / lysine-mutant reference exist at all?"),
            "current_text": None,
            "proposed_text": (
                "Q7 has RUN. Verdict `%s` — see "
                "[`v18-lysine-reference-precheck.json`](../modalities/v18-lysine-reference-precheck.json) "
                "`verdict.decision`, with the register's own prior graded beside it in "
                "`verdict.prediction_outcome`. ⛔ No claim ceiling moves either way: `V18` stays at "
                "`proposed` (§2.3)." % v["decision"]),
            "why": ("the row is the open question; the precheck answers it and the answer needs a home "
                    "on the row rather than only in an artifact"),
            "artifact": "research/modalities/v18-lysine-reference-precheck.json:verdict.decision",
        },
        {
            "section": "§3.1 row `V18`",
            "anchor": None,
            "where": ("the `V18` row of the instrument table in §3.1, whose known-answer column reads "
                      "that none exists. That column entry should now point at this precheck rather "
                      "than assert an unchecked absence — the finding is the same, its EVIDENTIAL "
                      "STATUS is what changed."),
            "current_text": None,
            "proposed_text": (
                "known answer: **%s** — measured by the $0 precheck, not assumed "
                "([`v18-lysine-reference-precheck.json`](../modalities/v18-lysine-reference-precheck.json))"
                % v["decision"]),
            "why": ("'none exists' as an unchecked row and 'none exists, and here is the search that "
                    "establishes it' are different epistemic states, and only the second is citable"),
            "artifact": "research/modalities/v18-lysine-reference-precheck.json:verdict",
        },
    ]


def build(corpus_root, survey=SURVEY, slugs=None, corpus_ref=None):
    """The whole precheck, offline. Returns the artifact dict."""
    ternary = ternary_solved_substrates(survey)
    corpora = load_corpus(corpus_root, slugs)
    scanned = scan(corpora, ternary)
    v = verdict(corpora, ternary, scanned)
    return {
        "_what": ("C05 / roadmap §10.1a row Q7 — the $0 known-answer precheck for V18, the "
                  "transfer-zone lysine-identity instrument. Does a MEASURED ubiquitination-site or "
                  "lysine-mutant reference exist for a substrate with a SOLVED TERNARY?"),
        "_cost": "$0 — CI retrieval (fetch-literature.yml) + CPU adjudication. No GPU, no rental.",
        "_scope": ("Nothing here is a result about binding, reactivity, degradation, selectivity, "
                   "efficacy or safety, and nothing here concerns NR4A3."),
        "_claim_ceiling": ("roadmap §2.3 unchanged — V18 is at `proposed` and no requirement may be "
                           "claimed above it. Finding a benchmark is not passing one."),
        "prereg": PREREG,
        "null_rejection_rule": null_rejection_rule(),
        "caveat": caveat(),
        # ⚠ EPHEMERAL, AND SAID SO. This is a scratch export directory that will not exist for the
        # next reader; the DURABLE pointer is `corpus_provenance.commit`. An absolute path in a
        # committed artifact reads like a location and is not one.
        "corpus_root_at_generation": {
            "path": corpus_root,
            "_is_ephemeral": ("a scratch export of the literature-cache branch, not a repository "
                              "location. Use corpus_provenance.commit to reproduce."),
        },
        "corpus_provenance": {
            "branch": "literature-cache",
            "commit": corpus_ref,
            "_why_this_is_here": (
                "⚠ THE CORPUS IS NOT COMMITTED BESIDE THIS ARTIFACT — it lives on the literature-cache "
                "branch, which is where every CI-fetched full text in this repo lives. Without the "
                "commit sha this verdict would be unreproducible: the branch is rewritten by every "
                "sweep, so `literature/<slug>/` is a moving target and 'I read the corpus' would be "
                "an unfalsifiable sentence. Re-run: "
                "`git archive <commit> literature/<slug> | tar -x -C <dir>` then point --corpus-root "
                "at <dir>."),
            "retrieved_by": (
                ".github/workflows/fetch-literature.yml `query` path (scripts/fetch-paper.mjs sync), "
                "dispatched on main at $0"),
        },
        "corpora": [{k: c[k] for k in ("slug", "why_this_query", "loaded", "n_records",
                                       "n_full_texts_on_disk", "error")} for c in corpora],
        "ternary_solved_substrates": {k: ternary[k] for k in ("_source", "genes", "by_gene", "error")},
        "scan": {k: scanned[k] for k in ("n_records_scanned", "n_with_full_text", "n_candidate_spans")},
        # ⛔ QUALIFYING SPANS ARE NEVER TRUNCATED AWAY (caught 2026-08-07: a flat [:200] cap emitted
        # 10 of the 12 spans the verdict had counted, so a reader tallying the artifact got a
        # different number from the verdict and could not tell which was wrong). The gate reads the
        # complete list; the artifact must therefore carry every span the gate counted, and the cap
        # applies only to the non-qualifying remainder, which is context rather than evidence.
        "candidate_spans": (
            [c for c in scanned["candidates"] if c["passes_G2_ternary_solved_substrate"]]
            + [c for c in scanned["candidates"]
               if not c["passes_G2_ternary_solved_substrate"]][:NON_QUALIFYING_SPAN_CAP]),
        "_non_qualifying_spans_truncated": max(
            0, sum(1 for c in scanned["candidates"]
                   if not c["passes_G2_ternary_solved_substrate"]) - NON_QUALIFYING_SPAN_CAP),
        "_non_qualifying_span_cap": NON_QUALIFYING_SPAN_CAP,
        "_why_non_qualifying_spans_are_capped": (
            "they are CONTEXT — a sample of what the tokenizer matched but G2 rejected, kept so a "
            "reader can judge whether the filter is sane. The complete count is in `scan"
            ".n_candidate_spans`; the complete EVIDENCE is the qualifying set, which is never cut."),
        "_qualifying_spans_are_never_truncated": True,
        "verdict": v,
        "map_edits_required": map_edits_required(v),
    }


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--corpus-root", required=True,
                    help="checkout/export of the literature-cache branch (contains literature/<slug>/)")
    ap.add_argument("--survey", default=SURVEY)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--corpus-ref", default=None,
                    help="commit sha of literature-cache the corpus was exported from (provenance)")
    args = ap.parse_args(argv)
    doc = build(args.corpus_root, args.survey, corpus_ref=args.corpus_ref)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: doc[k] for k in ("corpora", "scan")}, indent=1))
    print("\nVERDICT: %s\n%s" % (doc["verdict"]["decision"], doc["verdict"]["sentence"]),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
