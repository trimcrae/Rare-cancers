#!/usr/bin/env python3
"""ROADMAP ROW 26 — bound the NR4A2 half of the selectivity requirement, at $0, from public data.

WHAT IT DECIDES
---------------
Roadmap section 2.4 establishes that the selectivity requirement is ASYMMETRIC:

    NR4A1 -- a HARD constraint, because the combined Nr4a1-/-;Nr4a3-/- mouse is a named AML
             genotype (PMID 17515897, PMID 29343483) and it is precisely the pair a non-selective
             NR4A3 degrader reconstitutes.
    NR4A2 -- UNBOUNDED IN BOTH DIRECTIONS: the most constrained paralogue in human population
             genetics (gnomAD pLI 1.0) and the most tissue-enhanced, but with NO phenotyped KO --
             the repo's IMPC query returned nothing for any of the three, and the widely-repeated
             "Nurr1 single-KO is neonatal-lethal" is flagged UNCONFIRMED in
             nr4a3-emc-biology-evidence.md.

"Unbounded" is not "safe". It means the liability could be LARGER than NR4A1's, not smaller. The
design brief today therefore cannot say how much NR4A2 sparing is required. This module is the $0
observation that either bounds it or converts "unbounded" from an unanswered question into a
MEASURED ABSENCE -- which roadmap row 26 states in advance is an equally useful outcome.

TWO INSTRUMENTS, BOTH PUBLIC, BOTH $0
-------------------------------------
A. **MGI (Mouse Genome Informatics) public reports** -- the named remaining source after IMPC
   returned nothing. Four flat reports, parsed rather than queried, so the whole corpus is scanned
   instead of one guessed query:
     MRK_List2.rpt              markers -> MGI accession IDs (symbol resolution)
     MGI_PhenoGenoMP.rpt        genotype -> Mammalian Phenotype term + PubMed ID
     VOC_MammalianPhenotype.rpt MP ID -> term name (so lethality is matched on TERMS, not on a
                                guessed list of MP IDs)
     MGI_PhenotypicAllele.rpt   allele -> type/attributes (is this allele actually a null?)
   This gives single-KO phenotypes for Nr4a1/Nr4a2/Nr4a3, the double/triple genotypes if recorded,
   and a PubMed ID on every annotation -- i.e. a citation or an explicit not-found, never a memory.

B. **Human Protein Atlas consensus per-tissue nTPM** -- the field `nr4a-safety-genetics.json`
   records as `rna_tissue_specific_nTPM: null` for all three genes today, which is why tissue
   overlap is currently an ASSUMPTION ("broadly co-expressed", "CNS exception") rather than a
   measured quantity. The bulk consensus table carries nTPM for every gene in every tissue, so the
   overlap becomes arithmetic.

WHY NAME-MATCHING ALONE IS NOT ALLOWED TO ESTABLISH ANYTHING HERE
-----------------------------------------------------------------
`pmx_mutation_reference` first returned a false PROCEED off a promiscuous substring that matched an
unrelated record elsewhere in a 7,085-row database (see its `skempi_scan` docstring). The same trap
exists here in a different costume: an MGI genotype string mentioning `Nr4a2` may be a compound
genotype carrying four other mutations, a transgene, or a conditional driver, and counting it as a
"Nr4a2 single-KO phenotype" would be exactly that error. So a genotype is admitted as SINGLE-GENE
only when TWO INDEPENDENT PARSES AGREE:

    (1) every allele symbol parsed out of the Allelic Composition resolves to the same one gene, and
    (2) the report's own MGI marker-accession column lists exactly that one marker.

A disagreement between the two is recorded as `ambiguous` and counted nowhere. This is not
ceremony: a genotype string is free text and a marker column is curated, and the failure mode is a
populated field being read as a measured one (CLAUDE.md section 4b).

THE GATE, PRE-REGISTERED
------------------------
The verdict vocabulary is four-valued because "we could not read the source" and "we read it and it
is empty" are different facts:

    BOUNDED            -- a phenotyped Nr4a2 single-gene genotype exists AND carries a
                          survival/viability phenotype with a primary citation. The lethality claim
                          resolves to a citation and the required sparing has a floor.
    PARTIALLY_BOUNDED  -- Nr4a2 single-gene phenotypes exist and are citable, but no
                          survival/viability term among them: loss is phenotyped and not shown
                          lethal. A weaker but real bound.
    STILL_UNBOUNDED    -- both sources read cleanly and MGI carries no Nr4a2 single-gene phenotype
                          at all. The measured absence roadmap row 26 asks for.
    UNDETERMINED       -- a source could not be read. NOT a negative; re-run it.

THE CAVEAT THAT MUST TRAVEL WITH ANY VERDICT
--------------------------------------------
A germline mouse knockout bounds DEVELOPMENTAL loss of a gene. A degrader is an ADULT, TRANSIENT,
INCOMPLETE loss of a protein. `caveat()` returns that sentence so no write-up can quietly upgrade a
KO phenotype into a statement about a molecule -- and this repo holds no measured or predicted
CNS-penetration datum for any NR4A candidate, so the exposure lever remains a property of a
molecule that does not exist.

USAGE (CI; the dev sandbox's egress proxy cannot reach any of these hosts)
    python3 nr4a2_sparing_bound.py            # fetch, gate, write nr4a2-sparing-bound.json
    python3 nr4a2_sparing_bound.py --offline  # exercise the gate logic only; verdict is
                                              # UNDETERMINED by construction, no data invented
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
import time
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nr4a2-sparing-bound.json")

UA = {"User-Agent": "rare-cancers-nr4a2-bound/1.0 (research; github.com/trimcrae/Rare-cancers)"}

GENES_MOUSE = ["Nr4a1", "Nr4a2", "Nr4a3"]
GENES_HUMAN = ["NR4A1", "NR4A2", "NR4A3"]
ENSEMBL = {"NR4A1": "ENSG00000123358", "NR4A2": "ENSG00000153234", "NR4A3": "ENSG00000119508"}

# ---------------------------------------------------------------------------------------------------
# PRE-REGISTERED THRESHOLDS. Written before any value is fetched; the artifact echoes them beside the
# result so a reader can check that the cut was not chosen after seeing the data.
# ---------------------------------------------------------------------------------------------------
PREREG = {
    "expressed_ntpm_min": 1.0,
    "_why_1_0": ("HPA's own conventional detection floor for consensus nTPM. Pre-registered rather "
                 "than tuned: every tissue-overlap count below is reported at this one cut, and the "
                 "artifact additionally emits the full per-tissue table so any other cut can be "
                 "applied by a reader without re-running anything."),
    "enriched_fold_min": 4.0,
    "_why_4_0": ("a paralogue is called DOMINANT in a tissue when its nTPM exceeds 4x the larger of "
                 "the other two. This is the 'no compensation available' shape: it is HPA's own "
                 "tissue-enriched fold convention applied between paralogues instead of between "
                 "tissues."),
    "lethality_term_pattern": r"(lethal|viab|survival|died|death|premature death)",
    "_why_term_pattern": ("lethality is matched on MP TERM NAMES read live out of "
                          "VOC_MammalianPhenotype.rpt, never on a hard-coded list of MP IDs. A "
                          "hard-coded ID list is a memory, and a memory is what this row exists to "
                          "replace."),
    "single_gene_requires_two_agreeing_parses": True,
}

LETHAL_RE = re.compile(PREREG["lethality_term_pattern"], re.I)

# ---------------------------------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------------------------------
MGI_BASE = "https://www.informatics.jax.org/downloads/reports/"
MGI_REPORTS = {
    "markers": "MRK_List2.rpt",
    "phenogeno": "MGI_PhenoGenoMP.rpt",
    "mp_vocab": "VOC_MammalianPhenotype.rpt",
    "alleles": "MGI_PhenotypicAllele.rpt",
}

#: Tried in order; the FIRST that returns a parseable table wins and is recorded. HPA has moved this
#: path between releases, so a single hard-coded URL would turn a live dataset into an absent reading.
HPA_CONSENSUS_URLS = [
    "https://www.proteinatlas.org/download/tsv/rna_tissue_consensus.tsv.zip",
    "https://www.proteinatlas.org/download/rna_tissue_consensus.tsv.zip",
    "https://www.proteinatlas.org/download/tsv/rna_tissue_hpa.tsv.zip",
    "https://www.proteinatlas.org/download/rna_tissue_hpa.tsv.zip",
]


def _fetch(url, timeout=300, tries=4):
    """Bytes, with backoff. Raises on final failure so the caller records an ABSENT READING."""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:                                    # noqa: BLE001 -- transport of any kind
            last = e
            print("  retry %d %s: %s" % (i + 1, url[:80], e), file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError("%s: %s" % (type(last).__name__, last))


# ---------------------------------------------------------------------------------------------------
# Instrument A -- MGI
# ---------------------------------------------------------------------------------------------------
#: An allele token inside an MGI Allelic Composition string: `Nr4a1<tm1Jmi>`, `Nr4a2<tm1Ddm>`.
#: Transgenes look like `Tg(Th-cre)1Tmd<Tg/0>` and are deliberately captured too, because a genotype
#: carrying one is NOT a clean single-gene knockout and must be excluded rather than silently kept.
_ALLELE_TOKEN = re.compile(r"([A-Za-z0-9][A-Za-z0-9\-\.\(\)/,:+']*?)<([^<>]*)>")


def genes_in_composition(comp):
    """Every distinct gene/transgene symbol named in an Allelic Composition string. Pure.

    Returns a sorted list. `Nr4a1<tm1Jmi>/Nr4a1<tm1Jmi>` -> ['Nr4a1'];
    `Nr4a1<tm1Jmi>/Nr4a1<tm1Jmi>,Nr4a3<tm1Jmi>/Nr4a3<tm1Jmi>` -> ['Nr4a1', 'Nr4a3'].
    """
    return sorted({m.group(1) for m in _ALLELE_TOKEN.finditer(comp or "")})


def _split_ids(cell):
    return [x.strip() for x in re.split(r"[|,;]", cell or "") if x.strip().startswith("MGI:")]


def parse_marker_list(text):
    """symbol -> MGI accession id, from MRK_List2.rpt. Pure.

    The header is READ rather than assumed: MGI has added columns to this report before, and a
    positional parse that silently shifts is how a symbol resolves to the wrong accession.
    """
    out, acc2sym, errors = {}, {}, []
    lines = (text or "").splitlines()
    if not lines:
        return out, acc2sym, ["MRK_List2.rpt was empty"]
    header = [h.strip() for h in lines[0].split("\t")]
    low = [h.lower() for h in header]
    try:
        i_acc = next(i for i, h in enumerate(low) if h.startswith("mgi accession"))
        i_sym = next(i for i, h in enumerate(low) if h == "marker symbol")
    except StopIteration:
        return out, acc2sym, ["MRK_List2.rpt header did not carry the expected columns: %s"
                              % header[:14]]
    i_status = next((i for i, h in enumerate(low) if h == "status"), None)
    i_type = next((i for i, h in enumerate(low) if h == "marker type"), None)
    for line in lines[1:]:
        f = line.split("\t")
        if len(f) <= max(i_acc, i_sym):
            continue
        acc, sym = f[i_acc].strip(), f[i_sym].strip()
        if not acc.startswith("MGI:") or not sym:
            continue
        acc2sym[acc] = sym
        # ⚠ PREFER THE OFFICIAL GENE ROW. A symbol can appear more than once (withdrawn or
        # non-gene markers), and taking whichever came first is how a symbol silently resolves to
        # an accession the phenotype report never uses.
        official = ((i_status is None or f[i_status].strip().upper().startswith("O"))
                    and (i_type is None or f[i_type].strip() == "Gene"))
        if official or sym not in out:
            if official or sym not in out:
                out[sym] = acc if official else out.get(sym, acc)
            if official:
                out[sym] = acc
    return out, acc2sym, errors


def parse_mp_vocab(text):
    """MP id -> term name, from VOC_MammalianPhenotype.rpt (id <TAB> term <TAB> definition). Pure."""
    out = {}
    for line in (text or "").splitlines():
        f = line.split("\t")
        if len(f) >= 2 and f[0].startswith("MP:"):
            out[f[0].strip()] = f[1].strip()
    return out


def parse_allele_report(text, symbols):
    """allele symbol -> {type, attributes, pmid} for the genes of interest, from
    MGI_PhenotypicAllele.rpt. Pure. Used to say whether an allele is actually a NULL/KNOCKOUT rather
    than a reporter, a conditional-ready or a spontaneous variant -- a distinction a genotype string
    does not carry."""
    want = {s.lower() for s in symbols}
    out = {}
    for line in (text or "").splitlines():
        if line.startswith("#"):
            continue
        f = [x.strip() for x in line.split("\t")]
        if len(f) < 8 or not f[0].startswith("MGI:"):
            continue
        allele_symbol = f[1]
        gene = allele_symbol.split("<")[0]
        if gene.lower() not in want:
            continue
        rec = {"allele_accession": f[0], "allele_symbol": allele_symbol, "allele_name": f[2],
               "gene": gene}
        # Type / attribute columns move between releases, so classify by CONTENT: find the field
        # that looks like an allele type and the one that looks like an attribute list.
        for cell in f[3:10]:
            low = cell.lower()
            if low in ("targeted", "spontaneous", "gene trapped", "chemically induced",
                       "transgenic", "radiation induced", "endonuclease-mediated",
                       "transposon induced", "other", "not specified", "qtl"):
                rec["allele_type"] = cell
            elif "null/knockout" in low or "reporter" in low or "hypomorph" in low \
                    or "conditional ready" in low or "inserted expressed sequence" in low:
                rec["allele_attributes"] = cell
        rec["is_null_knockout"] = "null/knockout" in (rec.get("allele_attributes") or "").lower()
        out[allele_symbol] = rec
    return out


def parse_phenogeno(text, marker_ids, symbols, acc2sym=None):
    """Every MGI_PhenoGenoMP.rpt annotation touching Nr4a1/Nr4a2/Nr4a3. Pure.

    MGI_PhenoGenoMP.rpt has no header. Columns are resolved BY CONTENT, not by position, so a
    release that inserts a column cannot silently shift the parse:

        field 0                     Allelic Composition (free text)
        the field starting `MP:`    the Mammalian Phenotype term -- the pivot everything else is
                                    located relative to
        `MGI:` ids after the pivot  MARKER accessions -- but ONLY those the marker report itself
                                    lists as markers. ⚠ MEASURED 2026-08-03 (run 30776301160): the
                                    trailing column of this report is an MGI **GENOTYPE** accession,
                                    also `MGI:`-prefixed, so a naive "collect every MGI: token"
                                    parse read the one-gene genotype
                                    `Nr4a3<tm1Omc>/Nr4a3<tm1Omc>` as TWO markers
                                    (MGI:1352457 the marker + MGI:3037447 the genotype) and threw
                                    it out as ambiguous. It threw out ALL 122 NR4A records that
                                    way, and the gate then reported STILL_UNBOUNDED off a parse
                                    that had read nothing -- an absent reading wearing a reading of
                                    absence's costume. `acc2sym` (built from MRK_List2 in the same
                                    run) is the authority for what is a marker, and the cross-check
                                    stays honest because it compares the curated marker column
                                    against the free-text composition, not against itself.
        digits after the pivot      PubMed ID

    ⚠ THE BEFORE/AFTER SPLIT IS LOAD-BEARING. Allele IDs and marker IDs are BOTH `MGI:`-prefixed, so
    a scan that merely collected every `MGI:` token would count a one-gene genotype as two-gene
    (one allele + one marker) and drop it -- or, worse, count a two-allele single-gene genotype as
    a multi-gene one. The MP field is the only unambiguous landmark in a headerless report.

    ★ THE SINGLE-GENE TEST IS THE POINT OF THIS FUNCTION. A row is `single_gene` only when the
    symbols parsed out of the free-text composition AND the curated marker-accession column BOTH say
    exactly one gene, and it is one of ours. Anything else is `multi_gene` or `ambiguous` and is
    counted nowhere -- see the module docstring for why a name hit alone is not allowed to establish
    anything here.
    """
    want_syms = {s.lower() for s in symbols}
    want_ids = {marker_ids[s] for s in symbols if s in marker_ids}
    acc2sym = acc2sym or {}
    rows, errors = [], []
    n_scanned = 0
    for line in (text or "").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        n_scanned += 1
        f = [x.strip() for x in line.split("\t")]
        if len(f) < 5:
            continue
        comp = f[0]
        syms = genes_in_composition(comp)
        low = {s.lower() for s in syms}
        i_mp = next((i for i, cell in enumerate(f) if cell.startswith("MP:")), None)
        if i_mp is None:
            continue
        mp = f[i_mp]
        allele_ids, ids, pmid = [], [], None
        for cell in f[1:i_mp]:
            allele_ids.extend(_split_ids(cell))
        for cell in f[i_mp + 1:]:
            got = _split_ids(cell)
            if got:
                # Only accessions the marker report calls markers. Everything else on this side of
                # the pivot is a genotype accession and is kept separately, never counted as a gene.
                ids.extend([a for a in got if not acc2sym or a in acc2sym])
                allele_ids.extend([a for a in got if acc2sym and a not in acc2sym])
                continue
            if pmid is None and re.fullmatch(r"\d{4,9}", cell or ""):
                pmid = cell
        ids = sorted(set(ids))
        allele_ids = sorted(set(allele_ids))
        # The CURATED cross-check: what genes does the marker column ITSELF name? This, and not the
        # accession we happened to resolve from MRK_List2, is the independent second opinion. ⚠ An
        # earlier version required `set(ids) <= want_ids`, which made the whole classification hinge
        # on OUR symbol->accession resolution being right; a symbol that resolved to a withdrawn
        # duplicate would then have made every real record unclassifiable, which is a silent way to
        # manufacture an absence.
        genes_from_markers = {acc2sym[a] for a in ids if a in acc2sym} if acc2sym else set()
        touches_by_symbol = bool(low & want_syms)
        touches_by_id = bool({g.lower() for g in genes_from_markers} & want_syms) or \
            bool(set(ids) & want_ids)
        if not (touches_by_symbol or touches_by_id):
            continue
        agree = (not acc2sym) or (genes_from_markers == set(syms))
        if len(syms) == 1 and low <= want_syms and agree:
            kind = "single_gene"
        elif agree and len(syms) > 1 and touches_by_symbol:
            kind = "multi_gene"
        else:
            # symbol parse and curated marker column disagree on how many genes are involved
            kind = "ambiguous"
        rows.append({
            "allelic_composition": comp,
            "genes_parsed_from_composition": syms,
            "marker_accessions_in_record": ids,
            "genes_named_by_the_marker_column": sorted(genes_from_markers),
            "non_marker_mgi_ids_in_record": allele_ids,
            "mp_id": mp,
            "pubmed_id": pmid,
            "classification": kind,
        })
    if n_scanned == 0:
        errors.append("MGI_PhenoGenoMP.rpt parsed to ZERO lines -- a LOAD FAILURE, not the finding "
                      "that no phenotype exists.")
    return rows, n_scanned, errors


def summarise_mgi(rows, mp_names, marker_ids, alleles, symbols):
    """Per-gene single-KO summary + the multi-gene genotypes, with citations. Pure."""
    per_gene = {}
    for sym in symbols:
        single = [r for r in rows
                  if r["classification"] == "single_gene"
                  and r["genes_parsed_from_composition"] == [sym]]
        terms = {}
        for r in single:
            name = mp_names.get(r["mp_id"] or "", None)
            if not name:
                continue
            slot = terms.setdefault(name, {"mp_id": r["mp_id"], "pubmed_ids": set(),
                                           "genotypes": set()})
            if r["pubmed_id"]:
                slot["pubmed_ids"].add(r["pubmed_id"])
            slot["genotypes"].add(r["allelic_composition"])
        lethal = {k: v for k, v in terms.items() if LETHAL_RE.search(k)}
        gene_alleles = {k: v for k, v in alleles.items() if v.get("gene") == sym}
        per_gene[sym] = {
            "mgi_marker_accession": marker_ids.get(sym),
            "n_single_gene_annotations": len(single),
            "n_distinct_phenotype_terms": len(terms),
            "n_genotypes_annotated": len({r["allelic_composition"] for r in single}),
            "n_alleles_in_allele_report": len(gene_alleles),
            "n_null_knockout_alleles": sum(1 for v in gene_alleles.values()
                                           if v.get("is_null_knockout")),
            "survival_or_viability_terms": sorted(
                [{"term": k, "mp_id": v["mp_id"], "pubmed_ids": sorted(v["pubmed_ids"]),
                  "genotypes": sorted(v["genotypes"])[:8]} for k, v in lethal.items()],
                key=lambda d: d["term"]),
            "phenotype_terms": sorted(
                [{"term": k, "mp_id": v["mp_id"], "pubmed_ids": sorted(v["pubmed_ids"])}
                 for k, v in terms.items()], key=lambda d: d["term"])[:200],
            "_note_if_empty": ("no MGI single-gene genotype-phenotype annotation was found for this "
                               "marker. That is a reading of the whole MGI phenotype corpus, not a "
                               "failed query -- but it is still an absence of a RECORD, never "
                               "evidence that the knockout is healthy."),
        }

    multi = {}
    for r in rows:
        if r["classification"] != "multi_gene":
            continue
        key = " + ".join(r["genes_parsed_from_composition"])
        slot = multi.setdefault(key, {"genes": r["genes_parsed_from_composition"],
                                      "n_annotations": 0, "terms": {}, "pubmed_ids": set(),
                                      "genotypes": set()})
        slot["n_annotations"] += 1
        slot["genotypes"].add(r["allelic_composition"])
        if r["pubmed_id"]:
            slot["pubmed_ids"].add(r["pubmed_id"])
        name = mp_names.get(r["mp_id"] or "")
        if name:
            slot["terms"][name] = r["mp_id"]
    multi_out = []
    for key, v in sorted(multi.items()):
        multi_out.append({
            "genotype_genes": key,
            "involves_only_nr4a": all(g in symbols for g in v["genes"]),
            "n_annotations": v["n_annotations"],
            "pubmed_ids": sorted(v["pubmed_ids"]),
            "example_genotypes": sorted(v["genotypes"])[:5],
            "survival_or_viability_terms": sorted(k for k in v["terms"] if LETHAL_RE.search(k)),
            "phenotype_terms": sorted(v["terms"])[:80],
        })
    return per_gene, multi_out


def mgi_scan(texts, symbols=None):
    """Run instrument A over already-fetched report texts. Pure, so it is unit-testable offline."""
    symbols = symbols or GENES_MOUSE
    out = {"source": MGI_BASE, "reports": dict(MGI_REPORTS), "errors": [], "loaded": False}
    marker_ids, acc2sym, err = parse_marker_list(texts.get("markers", ""))
    out["errors"].extend(err)
    out["n_markers_in_marker_report"] = len(acc2sym)
    resolved = {s: marker_ids.get(s) for s in symbols}
    out["marker_resolution"] = resolved
    missing = [s for s, v in resolved.items() if not v]
    if missing:
        out["errors"].append("markers not resolved in MRK_List2.rpt: %s" % ", ".join(missing))

    mp_names = parse_mp_vocab(texts.get("mp_vocab", ""))
    out["n_mp_terms_in_vocabulary"] = len(mp_names)
    if not mp_names:
        out["errors"].append("VOC_MammalianPhenotype.rpt parsed to ZERO terms -- a LOAD FAILURE. "
                             "Without the vocabulary a lethality term cannot be recognised at all, "
                             "so no negative may be drawn from this run.")

    alleles = parse_allele_report(texts.get("alleles", ""), symbols)
    out["n_alleles_found"] = len(alleles)
    out["alleles"] = sorted(alleles.values(), key=lambda d: d["allele_symbol"])[:120]

    rows, n_scanned, err2 = parse_phenogeno(texts.get("phenogeno", ""),
                                            {k: v for k, v in resolved.items() if v}, symbols,
                                            acc2sym=acc2sym)
    out["errors"].extend(err2)
    out["n_phenogeno_lines_scanned"] = n_scanned
    out["n_records_touching_nr4a"] = len(rows)
    out["n_ambiguous_records_counted_nowhere"] = sum(1 for r in rows
                                                     if r["classification"] == "ambiguous")
    out["ambiguous_records"] = [r for r in rows if r["classification"] == "ambiguous"][:40]

    per_gene, multi = summarise_mgi(rows, mp_names, {k: v for k, v in resolved.items() if v},
                                    alleles, symbols)
    out["single_gene"] = per_gene
    out["multi_gene_genotypes"] = multi
    n_classified = sum(1 for r in rows if r["classification"] in ("single_gene", "multi_gene"))
    out["n_classified_records"] = n_classified
    all_ambiguous = bool(rows) and n_classified == 0
    if all_ambiguous:
        # ⛔ MEASURED 2026-08-03, run 30776301160: 122 of 122 NR4A records came back `ambiguous`
        # because the report's trailing MGI GENOTYPE accession was being counted as a second
        # marker -- and the gate then published STILL_UNBOUNDED off a parse that had read nothing.
        # A classifier that rejects 100% of its input has not measured an absence; it has failed.
        # This makes that state a LOAD FAILURE, so the verdict can only be UNDETERMINED.
        out["errors"].append(
            "PARSE FAILURE: %d records touch these markers and NONE could be classified as "
            "single-gene or multi-gene. A classifier that rejects every record has not found an "
            "absence, it has failed to read -- see the ambiguous_records sample. No negative may be "
            "drawn from this run." % len(rows))
    out["loaded"] = bool(n_scanned and mp_names and not err and not all_ambiguous
                         and not missing and acc2sym)
    return out


def fetch_mgi():
    texts, errors = {}, []
    for key, name in MGI_REPORTS.items():
        try:
            texts[key] = _fetch(MGI_BASE + name).decode("utf-8", "replace")
        except Exception as e:                                    # noqa: BLE001
            texts[key] = ""
            errors.append("%s could not be fetched: %s" % (name, e))
    return texts, errors


# ---------------------------------------------------------------------------------------------------
# Instrument B -- Human Protein Atlas consensus per-tissue nTPM
# ---------------------------------------------------------------------------------------------------
def parse_hpa_tsv(text, ensembl=None):
    """gene -> {tissue: nTPM} for our three genes, from the HPA consensus TSV. Pure.

    Columns are located by NAME from the header; a release that reorders them cannot shift the parse.
    """
    ensembl = ensembl or ENSEMBL
    want = {v: k for k, v in ensembl.items()}
    per = {g: {} for g in ensembl}
    lines = (text or "").splitlines()
    if not lines:
        return per, ["HPA table was empty"]
    header = [h.strip().strip('"') for h in lines[0].split("\t")]
    low = [h.lower() for h in header]
    try:
        i_gene = low.index("gene")
        i_tis = low.index("tissue")
        i_ntpm = low.index("ntpm")
    except ValueError:
        return per, ["HPA header did not carry Gene/Tissue/nTPM: %s" % header[:10]]
    for line in lines[1:]:
        f = line.split("\t")
        if len(f) <= max(i_gene, i_tis, i_ntpm):
            continue
        ensg = f[i_gene].strip().strip('"')
        g = want.get(ensg)
        if not g:
            continue
        try:
            per[g][f[i_tis].strip().strip('"')] = float(f[i_ntpm])
        except ValueError:
            continue
    errors = [("no rows for %s in the HPA table" % g) for g, v in per.items() if not v]
    return per, errors


def hpa_overlap(per_gene, prereg=None):
    """The tissue-overlap arithmetic. Pure, and every count is derived from `per_gene`.

    This is the quantity roadmap 2.4 says is currently an assumption. It answers, per tissue:
    is NR4A2 present at all (so a non-sparing degrader would act there); is NR4A2 present WITHOUT a
    paralogue (so its loss is unbuffered); and are NR4A3 and NR4A2 present together (so tissue
    distribution cannot separate target from anti-target and selectivity must be molecular).
    """
    prereg = prereg or PREREG
    cut = float(prereg["expressed_ntpm_min"])
    fold = float(prereg["enriched_fold_min"])
    tissues = sorted(set().union(*[set(v) for v in per_gene.values()]) if per_gene else set())
    rows = []
    for t in tissues:
        n1 = per_gene.get("NR4A1", {}).get(t)
        n2 = per_gene.get("NR4A2", {}).get(t)
        n3 = per_gene.get("NR4A3", {}).get(t)
        if n1 is None or n2 is None or n3 is None:
            continue
        others = max(n1, n3)
        rows.append({
            "tissue": t, "NR4A1_nTPM": n1, "NR4A2_nTPM": n2, "NR4A3_nTPM": n3,
            "nr4a2_expressed": n2 >= cut,
            "nr4a3_expressed": n3 >= cut,
            "nr4a2_unbuffered": bool(n2 >= cut and n1 < cut and n3 < cut),
            "nr4a2_dominant": bool(n2 >= cut and others > 0 and n2 >= fold * others),
            "nr4a2_and_nr4a3_co_expressed": bool(n2 >= cut and n3 >= cut),
        })
    n = len(rows)

    def _cnt(k):
        return sum(1 for r in rows if r[k])

    return {
        "n_tissues_with_all_three_measured": n,
        "expressed_cut_ntpm": cut,
        "dominance_fold": fold,
        "counts": {
            "nr4a2_expressed": _cnt("nr4a2_expressed"),
            "nr4a3_expressed": _cnt("nr4a3_expressed"),
            "nr4a2_and_nr4a3_co_expressed": _cnt("nr4a2_and_nr4a3_co_expressed"),
            "nr4a2_unbuffered": _cnt("nr4a2_unbuffered"),
            "nr4a2_dominant": _cnt("nr4a2_dominant"),
        },
        "fractions": {
            k: (round(v / n, 4) if n else None) for k, v in {
                "nr4a2_expressed": _cnt("nr4a2_expressed"),
                "nr4a2_and_nr4a3_co_expressed": _cnt("nr4a2_and_nr4a3_co_expressed"),
                "nr4a2_unbuffered": _cnt("nr4a2_unbuffered"),
                "nr4a2_dominant": _cnt("nr4a2_dominant"),
            }.items()},
        "nr4a2_unbuffered_tissues": [r["tissue"] for r in rows if r["nr4a2_unbuffered"]],
        "nr4a2_dominant_tissues": [r["tissue"] for r in rows if r["nr4a2_dominant"]],
        "top_20_tissues_by_nr4a2": sorted(rows, key=lambda r: -r["NR4A2_nTPM"])[:20],
        "per_tissue": rows,
        "_what_this_does_not_say": (
            "mRNA nTPM is not protein, and a tissue average is not a cell type. A tissue where the "
            "paralogues co-express does not thereby demonstrate functional compensation; it only "
            "shows the compensating protein could be present. The counts above bound where a "
            "non-sparing degrader WOULD act, not what would happen if it did."),
    }


def fetch_hpa():
    attempts = []
    for url in HPA_CONSENSUS_URLS:
        try:
            blob = _fetch(url, tries=2)
        except Exception as e:                                    # noqa: BLE001
            attempts.append({"url": url, "ok": False, "error": str(e)})
            continue
        try:
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                names = [n for n in z.namelist() if n.lower().endswith((".tsv", ".txt"))]
                if not names:
                    attempts.append({"url": url, "ok": False,
                                     "error": "zip carried no .tsv: %s" % z.namelist()[:5]})
                    continue
                text = z.read(names[0]).decode("utf-8", "replace")
            attempts.append({"url": url, "ok": True, "bytes": len(blob), "member": names[0]})
            return text, attempts
        except Exception as e:                                    # noqa: BLE001
            attempts.append({"url": url, "ok": False, "error": "unzip failed: %s" % e})
    return "", attempts


# ---------------------------------------------------------------------------------------------------
# The caveat and the gate
# ---------------------------------------------------------------------------------------------------
def caveat():
    """The sentence any use of this artifact MUST carry. One home, so it cannot be dropped."""
    return ("A germline mouse knockout bounds DEVELOPMENTAL, COMPLETE, LIFELONG loss of a gene. A "
            "degrader is an ADULT, TRANSIENT, INCOMPLETE loss of a protein, and no source read here "
            "measures that. So a KO phenotype -- lethal or not -- sets the ceiling of concern, never "
            "the expected effect of a molecule; and an absent KO record is an absence of evidence, "
            "not evidence of tolerability. This repo additionally holds no measured or predicted "
            "CNS-penetration datum for any NR4A candidate, so the exposure argument that would "
            "otherwise narrow the NR4A2 question is a property of a molecule that does not exist.")


def verdict(mgi, hpa, prereg=None):
    """Apply the pre-registered gate mechanically. Pure."""
    prereg = prereg or PREREG
    gates, blockers = {}, []

    mgi_loaded = bool(mgi.get("loaded"))
    hpa_loaded = bool(hpa.get("loaded"))
    if not mgi_loaded:
        blockers.append("MGI did not load (%s)" % "; ".join(mgi.get("errors") or ["unknown"]))
    if not hpa_loaded:
        blockers.append("HPA did not load (%s)" % "; ".join(hpa.get("errors") or ["unknown"]))

    sg = (mgi.get("single_gene") or {})
    nr4a2 = sg.get("Nr4a2") or {}
    n_ann = nr4a2.get("n_single_gene_annotations", 0)
    leth = nr4a2.get("survival_or_viability_terms") or []
    cited = [t for t in leth if t.get("pubmed_ids")]

    gates["B1_nr4a2_single_ko_phenotyped"] = {
        "requirement": ("at least one MGI genotype-phenotype annotation whose genotype involves "
                        "Nr4a2 AND NO OTHER GENE, admitted only when the free-text composition parse "
                        "and the curated marker-accession column agree (see module docstring)"),
        "n_single_gene_annotations": n_ann,
        "n_distinct_phenotype_terms": nr4a2.get("n_distinct_phenotype_terms", 0),
        "n_null_knockout_alleles_on_record": nr4a2.get("n_null_knockout_alleles", 0),
        "met": bool(n_ann),
    }
    gates["B2_lethality_claim_resolved_to_a_citation"] = {
        "requirement": ("the repo's UNCONFIRMED 'Nurr1 single-KO is neonatal-lethal' resolves to a "
                        "survival/viability MP term on an Nr4a2-only genotype WITH a PubMed ID, or "
                        "to an explicit not-found"),
        "survival_or_viability_terms_found": leth,
        "terms_with_a_primary_citation": len(cited),
        "met": bool(cited),
        "_matched_on": prereg["lethality_term_pattern"],
    }
    ov = hpa.get("overlap") or {}
    gates["B3_tissue_overlap_measured"] = {
        "requirement": ("per-tissue nTPM for all three paralogues from a named public source, so "
                        "tissue overlap is a measured quantity rather than the assumption roadmap "
                        "2.4 currently carries"),
        "n_tissues": ov.get("n_tissues_with_all_three_measured", 0),
        "counts": ov.get("counts"),
        "fractions": ov.get("fractions"),
        "source": hpa.get("source"),
        "met": bool(ov.get("n_tissues_with_all_three_measured", 0) >= 10),
    }

    if blockers:
        decision = "UNDETERMINED"
        sentence = ("UNDETERMINED -- a source could not be read (%s). This is an ABSENT READING, not "
                    "a reading of absence: re-run on a CI runner before drawing any conclusion, and "
                    "change nothing in the brief in the meantime." % "; ".join(blockers))
    elif gates["B2_lethality_claim_resolved_to_a_citation"]["met"]:
        decision = "BOUNDED"
        sentence = (
            "BOUNDED -- MGI carries %d phenotype annotation(s) on Nr4a2-ONLY genotypes, including %d "
            "survival/viability term(s) with a primary citation. Complete germline loss of Nr4a2 has "
            "a phenotyped, citable consequence in a mammal, so the NR4A2 half of the selectivity "
            "requirement is no longer unbounded in the direction that matters for a design brief: "
            "there is a floor under how much sparing is required." % (n_ann, len(cited)))
    elif gates["B1_nr4a2_single_ko_phenotyped"]["met"]:
        decision = "PARTIALLY_BOUNDED"
        sentence = (
            "PARTIALLY BOUNDED -- MGI carries %d phenotype annotation(s) on Nr4a2-ONLY genotypes "
            "across %d distinct terms, but NONE of them is a survival/viability term. The single-KO "
            "is phenotyped and is not recorded as lethal, so the repo's UNCONFIRMED neonatal-lethal "
            "claim does not resolve to a citation and must not be repeated. The bound that exists is "
            "the phenotype list itself." % (n_ann, nr4a2.get("n_distinct_phenotype_terms", 0)))
    else:
        decision = "STILL_UNBOUNDED"
        sentence = (
            "STILL UNBOUNDED -- MGI's whole phenotype corpus (%d annotation lines scanned) carries NO "
            "genotype-phenotype annotation for an Nr4a2-only genotype. Combined with the IMPC null "
            "already on record, the two standardized in-vivo phenotype sources both return nothing, "
            "so 'unbounded' is now a MEASURED ABSENCE rather than an unanswered question. The repo's "
            "'Nurr1 single-KO is neonatal-lethal' does NOT resolve to a citation here and must not be "
            "repeated as fact." % mgi.get("n_phenogeno_lines_scanned", 0))

    return {"decision": decision, "gates": gates, "sentence": sentence,
            "caveat_that_must_travel_with_any_result": caveat(),
            "tolerance_statement": tolerance_statement(decision, mgi, hpa)}


def tolerance_statement(decision, mgi, hpa):
    """THE PLAIN ANSWER row 26 asks for: how much NR4A2 sparing is required?

    Written as a function of what was actually read, so it cannot drift from the artifact.
    """
    ov = hpa.get("overlap") or {}
    c = ov.get("counts") or {}
    f = ov.get("fractions") or {}
    n = ov.get("n_tissues_with_all_three_measured")
    sg = (mgi.get("single_gene") or {})
    parts = []

    if decision == "UNDETERMINED":
        return ("NOT ANSWERED THIS RUN -- a source could not be read. No change to the brief.")

    if decision == "BOUNDED":
        parts.append(
            "A FLOOR EXISTS AND IT IS CITED. Complete germline Nr4a2 loss produces a phenotyped, "
            "primary-cited survival/viability consequence in the mouse, so NR4A2 sparing is a "
            "requirement with evidence behind it rather than a precaution. It is still a WEAKER "
            "constraint than NR4A1's, because NR4A1's is a combination genotype a non-selective "
            "NR4A3 degrader RECONSTITUTES, whereas this one is complete developmental loss of a "
            "single gene, which no degrader delivers.")
    elif decision == "PARTIALLY_BOUNDED":
        parts.append(
            "A PARTIAL BOUND. The Nr4a2 single knockout IS phenotyped in MGI and the phenotypes are "
            "cited, but none of them is a survival or viability term. So the widely-repeated "
            "neonatal-lethal framing is NOT supported by the standardized source, and the honest "
            "brief is: spare NR4A2 to the extent the divergent handles allow, and carry the "
            "phenotype list -- not a lethality claim -- as the stated liability.")
    else:
        parts.append(
            "STILL UNBOUNDED, AND NOW MEASURABLY SO. Both standardized in-vivo phenotype sources "
            "(IMPC previously, MGI here) return no single-gene Nr4a2 phenotype record. The design "
            "brief therefore cannot state a required degree of NR4A2 sparing from mouse genetics at "
            "all, and any statement that it can is unsupported.")

    if n:
        parts.append(
            "WHAT IS NOW MEASURED INSTEAD OF ASSUMED: across %d tissues with all three paralogues "
            "quantified, NR4A2 is expressed in %s, NR4A2 and NR4A3 are co-expressed in %s (so tissue "
            "distribution cannot separate target from anti-target -- selectivity has to be "
            "molecular), NR4A2 is expressed with NEITHER paralogue present in %s (unbuffered), and "
            "NR4A2 is the dominant family member in %s. Those four numbers replace the qualitative "
            "'broadly co-expressed / CNS exception' reading the brief carried."
            % (n, c.get("nr4a2_expressed"), c.get("nr4a2_and_nr4a3_co_expressed"),
               c.get("nr4a2_unbuffered"), c.get("nr4a2_dominant")))
        if ov.get("nr4a2_unbuffered_tissues"):
            parts.append("UNBUFFERED TISSUES (NR4A2 present, both paralogues below the cut): %s."
                         % ", ".join(ov["nr4a2_unbuffered_tissues"][:15]))

    other = []
    for sym in ("Nr4a1", "Nr4a3"):
        g = sg.get(sym) or {}
        other.append("%s: %d single-gene annotations, %d survival/viability terms"
                     % (sym, g.get("n_single_gene_annotations", 0),
                        len(g.get("survival_or_viability_terms") or [])))
    parts.append("FOR CONTRAST, THE OTHER TWO SINGLE KNOCKOUTS -- " + "; ".join(other) + ".")

    parts.append(
        "WHAT WOULD ACTUALLY CLOSE IT, AND IS NOT AVAILABLE AT $0: an adult conditional or "
        "inducible Nr4a2 deletion with a survival/behaviour readout, and a CNS-exposure measurement "
        "for a real candidate molecule. Neither exists here; the first is a wet-lab experiment and "
        "the second is a property of a molecule this program has not built.")
    return " ".join(parts)


# ---------------------------------------------------------------------------------------------------
# VERBATIM SPANS OF THE LIVE ROADMAP, held as literals so the routed edits are `grep -F`-checkable.
# ⚠ These are QUOTATIONS, not restatements: `verify_map_edits.py` fails the build if any of them stops
# matching nr4a3-program-map.md exactly. The categorical audit shipped nine edits written against a
# map that had been restructured underneath them and all nine failed to apply; this is the guard.
# ---------------------------------------------------------------------------------------------------
MAP_2_4_NR4A2_CELL = (
    "\u26a0 the *most* constrained paralogue in human population genetics and the most "
    "tissue-enhanced, but **no phenotyped KO** \u2014 the repo's IMPC query returned nothing for any "
    "of the three, and the widely-repeated *\"Nurr1 single-KO is neonatal-lethal\"* is flagged "
    "**UNCONFIRMED** in [`nr4a3-emc-biology-evidence.md`](nr4a3-emc-biology-evidence.md). "
    "**Strongly selected against in humans; unbounded for adult transient loss.**")

MAP_2_4_TWO_OBSERVATIONS = (
    "- **The two $0 observations that would bound the open half** \u2014 MGI single-KO phenotypes for "
    "*Nr4a1/2/3*\n  (the named source after IMPC returned nothing) and HPA per-tissue nTPM (the field "
    "is `null` today) \u2014 are\n  [\u00a710.1 row 26](#101--open-rows-ordered-by-what-unblocks-the-most).")

MAP_10_1_ROW_26 = (
    "| **26** | **Bound the NR4A2 half of the selectivity requirement** \u2014 MGI single-KO "
    "phenotypes for *Nr4a1/2/3*, and HPA per-tissue nTPM |")


# ---------------------------------------------------------------------------------------------------
# Roadmap edits -- routed, never applied. This module does not own nr4a3-program-map.md.
# ---------------------------------------------------------------------------------------------------
def map_edits_required(doc):
    """Verbatim, ready-to-apply edits the roadmap needs, as a machine-readable list.

    Each entry carries `anchor` (a currently-present unique substring of the map), `current_text`
    (verbatim, so `grep -F` can verify it still applies), `proposed_text`, `why` and `artifact` (the
    file:field that OWNS the number, so the map links rather than restates -- CLAUDE.md rule 1).

    ⚠ `anchor: null` means the edit needs a place that does not exist yet, and `where` says where.
    """
    v = doc["verdict"]
    mgi = doc["mgi"]
    ov = (doc["hpa"] or {}).get("overlap") or {}
    c = ov.get("counts") or {}
    n2 = (mgi.get("single_gene") or {}).get("Nr4a2") or {}
    leth = n2.get("survival_or_viability_terms") or []
    cite = sorted({p for t in leth for p in (t.get("pubmed_ids") or [])})

    if v["decision"] == "BOUNDED":
        new_bound = ("**NR4A2 — BOUNDED as of 2026-08-03**, by MGI single-gene phenotype records "
                     "(%d annotations on Nr4a2-only genotypes; survival/viability terms cited to "
                     "PMID %s). Still the weaker of the two constraints: NR4A1's is a combination "
                     "genotype a non-selective degrader reconstitutes, this one is complete "
                     "developmental loss."
                     % (n2.get("n_single_gene_annotations", 0), ", ".join(cite[:4]) or "—"))
    elif v["decision"] == "PARTIALLY_BOUNDED":
        new_bound = ("**NR4A2 — PARTIALLY BOUNDED as of 2026-08-03.** MGI phenotypes the Nr4a2 "
                     "single knockout (%d annotations, %d distinct terms) but records NO "
                     "survival/viability term, so the repeated *\"Nurr1 single-KO is "
                     "neonatal-lethal\"* does **not** resolve to a citation and must not be repeated."
                     % (n2.get("n_single_gene_annotations", 0),
                        n2.get("n_distinct_phenotype_terms", 0)))
    elif v["decision"] == "STILL_UNBOUNDED":
        new_bound = ("**NR4A2 — STILL UNBOUNDED, and now MEASURABLY so (2026-08-03).** MGI's whole "
                     "phenotype corpus (%d annotation lines scanned) carries no Nr4a2-only "
                     "genotype-phenotype record, so both standardized in-vivo sources (IMPC, MGI) "
                     "return nothing. *Unbounded* is now a measured absence rather than an "
                     "unanswered question." % mgi.get("n_phenogeno_lines_scanned", 0))
    else:
        new_bound = None

    edits = []
    if new_bound:
        edits.append({
            "section": "2.4",
            "anchor": "the repo's IMPC query returned nothing for any of the three",
            "current_text": MAP_2_4_NR4A2_CELL,
            "proposed_text": (
                "⚠ the *most* constrained paralogue in human population genetics and the most "
                "tissue-enhanced. " + new_bound + " Evidence, verdict and the full per-tissue table: "
                "[`nr4a2-sparing-bound.json`](../modalities/nr4a2-sparing-bound.json) → "
                "`verdict.decision` / `verdict.tolerance_statement`. **Adult transient loss remains "
                "unbounded by any source read** — a germline KO bounds developmental loss, not a "
                "degrader (`caveat_that_must_travel_with_any_result`)."),
            "why": ("row 26 ran; the NR4A2 half now has a measured answer, and the UNCONFIRMED "
                    "lethality claim resolved one way or the other"),
            "artifact": "research/modalities/nr4a2-sparing-bound.json:verdict",
        })

    if ov.get("n_tissues_with_all_three_measured"):
        edits.append({
            "section": "2.4",
            "anchor": "The two $0 observations that would bound the open half",
            "current_text": MAP_2_4_TWO_OBSERVATIONS,
            "proposed_text": (
                "- ✅ **Both $0 observations have been taken (2026-08-03, row 26).** MGI's four "
                "public reports were scanned in full and HPA per-tissue nTPM is now measured for all "
                "three paralogues across %d tissues: NR4A2 and NR4A3 are co-expressed in %s of them, "
                "so **tissue distribution cannot separate target from anti-target and the "
                "selectivity has to be molecular**; NR4A2 is unbuffered (both paralogues below the "
                "cut) in %s. One home for every figure: "
                "[`nr4a2-sparing-bound.json`](../modalities/nr4a2-sparing-bound.json) → "
                "`hpa.overlap.counts`."
                % (ov.get("n_tissues_with_all_three_measured"),
                   c.get("nr4a2_and_nr4a3_co_expressed"), c.get("nr4a2_unbuffered"))),
            "why": ("the per-tissue nTPM field the roadmap calls `null` is no longer null, and the "
                    "overlap it was needed for is now arithmetic instead of an assumption"),
            "artifact": "research/modalities/nr4a2-sparing-bound.json:hpa.overlap",
        })

    edits.append({
        "section": "10.1 row 26",
        "anchor": "the *only* thing that would bound the unbounded half of the requirement",
        "current_text": MAP_10_1_ROW_26,
        "proposed_text": ("| **26** | ✅ **DONE 2026-08-03 — the NR4A2 half is bounded to the extent "
                          "public data allows** ([`nr4a2-sparing-bound.json`](../modalities/"
                          "nr4a2-sparing-bound.json), verdict `%s`) |" % v["decision"]),
        "why": "row 26 has run; leaving it ○ would make a taken $0 observation look outstanding",
        "artifact": "research/modalities/nr4a2-sparing-bound.json:verdict.decision",
    })
    return edits


# ---------------------------------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------------------------------
def run(out_path=OUT, offline=False, mgi_texts=None, hpa_text=None):
    doc = {
        "_what": ("ROADMAP ROW 26 — the $0 observation that bounds (or measurably fails to bound) "
                  "the NR4A2 half of the asymmetric selectivity requirement, from MGI single-KO "
                  "phenotypes and HPA per-tissue nTPM."),
        "_this_is_evidence_not_a_conclusion": (
            "Every MGI value is parsed out of the public flat reports named below, with the PubMed "
            "ID the curator attached. Every nTPM is read from the HPA consensus table. Nothing is "
            "curated, averaged or remembered, and the verdict is a mechanical function of the two, "
            "printed beside them."),
        "_prereg": PREREG,
        "_asymmetry_this_serves": (
            "roadmap §2.4: NR4A1 is a HARD constraint (the Nr4a1-/-;Nr4a3-/- AML genotype, PMID "
            "17515897 / PMID 29343483); NR4A2 was UNBOUNDED in both directions. This module answers "
            "only the NR4A2 half and changes nothing about the NR4A1 half."),
        "caveat_that_must_travel_with_any_result": caveat(),
    }

    if offline:
        doc["mgi"] = {"loaded": False, "errors": ["--offline: no fetch attempted"],
                      "n_phenogeno_lines_scanned": 0, "single_gene": {}, "multi_gene_genotypes": []}
        doc["hpa"] = {"loaded": False, "errors": ["--offline: no fetch attempted"],
                      "source": None, "overlap": {}}
    else:
        if mgi_texts is None:
            mgi_texts, fetch_errors = fetch_mgi()
        else:
            fetch_errors = []
        doc["mgi"] = mgi_scan(mgi_texts)
        doc["mgi"]["errors"] = list(doc["mgi"].get("errors") or []) + fetch_errors
        if fetch_errors:
            doc["mgi"]["loaded"] = False

        if hpa_text is None:
            hpa_text, attempts = fetch_hpa()
        else:
            attempts = [{"url": "supplied", "ok": True}]
        per, hpa_errors = parse_hpa_tsv(hpa_text)
        ok = next((a for a in attempts if a.get("ok")), None)
        doc["hpa"] = {
            "source": (ok or {}).get("url"),
            "url_attempts": attempts,
            "errors": hpa_errors + ([] if ok else ["no HPA URL returned a parseable table"]),
            "loaded": bool(ok and not hpa_errors),
            "per_gene_tissue_ntpm": per,
            "overlap": hpa_overlap(per),
        }

    doc["verdict"] = verdict(doc["mgi"], doc["hpa"])
    doc["map_edits_required"] = map_edits_required(doc)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(doc, indent=1, default=str) + "\n")
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Roadmap row 26: bound the NR4A2 half of the "
                                             "selectivity requirement from MGI + HPA. $0.")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--offline", action="store_true",
                    help="exercise the gate logic with no network. NEVER emits a scientific "
                         "verdict: the decision is UNDETERMINED by construction.")
    args = ap.parse_args(argv)
    doc = run(out_path=args.out, offline=args.offline)
    v = doc["verdict"]
    print(json.dumps({k: v[k] for k in ("decision", "sentence", "tolerance_statement")}, indent=2))
    print("\nDECISION: %s" % v["decision"], file=sys.stderr)
    print(v["sentence"], file=sys.stderr)
    print("\nCAVEAT: %s" % doc["caveat_that_must_travel_with_any_result"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
