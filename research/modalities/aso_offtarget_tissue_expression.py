#!/usr/bin/env python3
"""Where are the junction gapmer's off-target loci EXPRESSED — in the dosed organs, and on site?

⛔ WHY THIS EXISTS, AND WHY IT IS A SEPARATE QUESTION FROM EVERY SCREEN THAT PRECEDED IT.
Five screens stand behind this panel and all five ask the same kind of question: does a SEQUENCE
somewhere in the transcriptome resemble this oligonucleotide closely enough to hybridise. None of
them asks the question that decides whether such a resemblance can matter in a patient, which is
whether the transcript carrying it is PRESENT in a tissue the drug reaches. A perfect match in a
transcript no dosed organ expresses is a different object from a weak match in one the liver runs
at hundreds of TPM, and a screen that reports both as "a near-match" cannot tell them apart.

⭐ THE COMPARTMENT SPLIT IS THE WHOLE POINT, AND COLLAPSING IT WOULD DESTROY THE ANSWER.
Systemically dosed phosphorothioate gapmers distribute predominantly to liver and kidney, so those
two organs carry the EXPOSURE question — what the drug will sit in at concentration. The tumour
compartment (deep soft tissue of the extremities, myxoid stroma) carries a different question
entirely — what is present where the intended target is. A gene can be a serious exposure liability
and irrelevant on site, or the reverse. The two are held in separate blocks of this artifact for
that reason and are never summed, never averaged, and never reduced to one score.

WHAT THIS IS NOT — and each line is a claim this artifact must never be read as making:
  · NOT a cleavage prediction. Every hit behind this file sits at 14/16 identity: TWO mismatches in
    a 16-mer, the loosest thing the screen admits. Whether such a duplex is a substrate at all is an
    AFFINITY question, and no screen here and no expression value anywhere can answer it. Expression
    is a NECESSARY condition for an off-target effect, never a sufficient one.
  · NOT a safety, efficacy, therapeutic-window or clinical-readiness statement about any sequence.
    A gene turning out to be unexpressed in liver does not make an oligonucleotide safe; it removes
    ONE hypothetical liability from a list nobody has measured the rest of.
  · NOT a risk ranking by record count. ANKS1B and ZNF667 carry most of the transcript records
    between them, and that is ANNOTATION DEPTH — how many variants RefSeq happens to list — not
    expression, not affinity and not risk. The record count is carried here only so a reader can see
    that it does NOT track the expression answer.
  · NOT a reading of absence. A locus with no row in a reference matrix is `readable: false` with the
    reason stated. It is NEVER rendered as "not expressed" (CLAUDE.md §4).

METHOD. The locus set is DERIVED from the committed deep screen rather than typed: the reagent's
hits are filtered to the screen's own `true_cleavage_risk` class and recounted per gene. Expression
is then read from three independent arms, each of which records its own failure separately:
  A · GTEx v8 median gene TPM across all tissues — the exposure arm. Liver and kidney are read from
      the same matrix as every other tissue, so the comparison is within one instrument.
  B · The two readable EMC array series — the on-site arm, via `emc_expression_panels._read_target`,
      so this cannot disagree with the panels lane about what a probe mapping is.
  C · NCBI Gene identity for all six loci — the arm that says what the uncharacterised `LOC` entries
      actually are, so their absence from arm A can be attributed rather than guessed.
"""
from __future__ import annotations

import gzip
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.path.join(HERE, "junction-aso-offtarget-e12n3-deep500-b1.json")
OUT = os.path.join(HERE, "aso-offtarget-tissue-expression.json")
INPUTS = os.path.join(HERE, "aso-offtarget-tissue-expression-inputs.json")

sys.path.insert(0, HERE)

#: The one clinically-relevant reagent in the panel: the 16-mer 5-6-5 LNA/DNA/LNA gapmer spanning
#: the EWSR1 exon 12 / TAF15 exon 11 / FUS exon 10 seam joined to NR4A3 exon 3.
REAGENT = "GGGCATATCATCAAAC"

#: ⭐ THE EXPOSURE TISSUES, and this list is the reason the artifact exists rather than a detail.
#: Named as GTEx v8 `SMTSD` tissue labels exactly, because a label that does not match a column
#: silently reads as "no data" — which is the fail-quiet direction. `_tissue_block` asserts that
#: every one of these resolved to a real column and records any that did not.
EXPOSURE_TISSUES = ["Liver", "Kidney - Cortex", "Kidney - Medulla"]

#: ⚠ PROXIES, AND THE ARTIFACT MUST SAY SO EVERY TIME IT PRINTS THEM. GTEx contains no
#: extraskeletal myxoid chondrosarcoma, no sarcoma of any kind and no myxoid stroma. These are the
#: normal tissues of the anatomical compartment EMC arises in — deep soft tissue of the extremities
#: — and they bound what a normal cell of that region expresses. They are NOT a tumour reading; the
#: tumour reading is arm B, in six and ten archival tumours, and the two are reported apart.
TUMOUR_COMPARTMENT_PROXY_TISSUES = [
    "Muscle - Skeletal",
    "Adipose - Subcutaneous",
    "Nerve - Tibial",
    "Cells - Cultured fibroblasts",
    "Artery - Tibial",
    "Skin - Sun Exposed (Lower leg)",
]

#: ⛔ KNOWN-ANSWER CONTROLS, AND THEY ARE NOT DECORATION. A GCT is a wide tab matrix; a column
#: off-by-one produces a completely plausible artifact in which every gene's tissue profile is
#: shifted by one tissue, and nothing about the numbers looks wrong. These three genes have
#: textbook tissue restriction, so `_control_verdict` can assert that the matrix's own maximum for
#: each falls where it must. A run whose controls fail must not be allowed to emit a locus verdict.
#: (`ALB` -> Liver, `UMOD` -> a kidney tissue, `MYH7` -> a muscle/heart tissue.)
GTEX_CONTROLS = {
    "ALB": {"expect_max_in": ["Liver"],
            "why": "albumin is the canonical hepatocyte-restricted transcript"},
    "UMOD": {"expect_max_in": ["Kidney - Medulla", "Kidney - Cortex"],
             "why": "uromodulin is made only by the thick ascending limb of the nephron"},
    "MYH7": {"expect_max_in": ["Muscle - Skeletal", "Heart - Left Ventricle"],
             "why": "beta-myosin heavy chain is restricted to slow skeletal muscle and ventricle"},
}

#: The GTEx v8 gene-level median TPM matrix, the published release file. A flat matrix is used in
#: preference to the portal's per-gene API on purpose: it is one request whose parse either works or
#: throws, rather than 6 requests against a schema that has moved between versions, and it is the
#: same object a reader can download to check this artifact.
GTEX_MEDIAN_TPM_URL = ("https://storage.googleapis.com/gtex_analysis_v8/rna_seq_data/"
                       "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz")

#: ⚠ FALLBACK ONLY, and it answers a DIFFERENT shape of question, so a run that used it says so.
#: Recorded rather than silently substituted (`arm_a.endpoint_used`).
GTEX_API_MEDIAN = "https://gtexportal.org/api/v2/expression/medianGeneExpression"
GTEX_API_GENE = "https://gtexportal.org/api/v2/reference/gene"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
HPA_SEARCH = "https://www.proteinatlas.org/api/search_download.php"

UA = {"User-Agent": "rare-cancers-aso-offtarget-expression/1.0"}

#: A median TPM at or above this is called `present` for the purpose of the readout below. ⚠ STATED,
#: NOT MEASURED, and deliberately not called a threshold of concern: it is the level at which a
#: transcript is conventionally taken to be detected at all in bulk RNA-seq, and it is applied only
#: to make the table legible. Every raw median is released so any other cut can be applied without
#: re-running this, and no verdict in this file changes across the range 0.5 to 2.
PRESENT_TPM = 1.0

#: The screen's own risk class for a hit whose catalytic gap is fully paired. Read from the screen
#: rather than re-derived, so this module cannot disagree with `junction_aso_offtarget` about what a
#: gap-paired hit is.
GAP_PAIRED_CLASS = "true_cleavage_risk"

_PAREN = re.compile(r"\(([^()]+)\)")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The locus set — DERIVED from the committed screen, never typed
# ─────────────────────────────────────────────────────────────────────────────────────────────

def gene_of(entry):
    """The gene symbol a hit belongs to, resolving the accession fallbacks `locus_of` leaves.

    ⛔ THIS IS A DOCUMENTED SECOND PASS OVER `junction_aso_locus_collapse.locus_of`, NOT A
    REPLACEMENT, AND THE DIFFERENCE IS A REAL DEFECT THAT THIS MODULE MUST NOT HIDE.
    `locus_of` reads only `defn.split(",")[0]` — the text before the FIRST comma — and looks for a
    parenthesised symbol in it. That works whenever the gene's description carries no comma, which
    is almost always. It fails whenever the description itself contains one, because the symbol is
    then past the split point and never seen:

        "Homo sapiens germ cell-less 1, spermatogenesis associated (GMCL1), mRNA"
         └──────────── head, no parenthesis ─────────┘

    so all nine GMCL1 records fall to the `acc:` fallback and read as NINE separate loci. That
    fallback is deliberate and is the SAFE direction — `locus_of`'s own docstring says a shared
    sentinel would merge unrelated hits and undercount — but it means a raw `locus_of` count of this
    reagent returns 14 pseudo-loci where six genes exist, and the two figures are not comparable.

    This pass takes `locus_of`'s answer whenever it resolved a symbol, and only for the `acc:`
    fallbacks re-reads the FULL definition. `_locus_rows` records how many pseudo-loci were merged
    (`n_accession_fallbacks_resolved`), so the defect stays VISIBLE in the artifact instead of being
    silently repaired by the module that depends on it. `locus_of` itself is left alone on purpose:
    `junction-aso-offtarget-locus-collapse.json` and the manuscript figures derived from it are
    owned elsewhere, and quietly changing a shared counter under them is how one lane's fix becomes
    another lane's unexplained number.
    """
    from junction_aso_locus_collapse import locus_of  # noqa: E402  (one home for the primary rule)
    primary = locus_of(entry)
    if not primary.startswith("acc:"):
        return primary, "locus_of"
    for cand in _PAREN.findall(str(entry.get("defn") or "")):
        cand = cand.strip()
        if cand and " " not in cand and not cand.isdigit():
            return cand.upper(), "full_definition_second_pass"
    return primary, "unresolved"


def _screen_hits(path=SCREEN, reagent=REAGENT):
    """The reagent's gap-paired hits, straight out of the committed screen."""
    d = json.load(open(path, encoding="utf-8"))
    match = [o for o in d.get("oligos", []) if o.get("antisense_5to3") == reagent]
    if len(match) != 1:
        raise RuntimeError(f"{reagent}: expected exactly one record in {os.path.basename(path)}, "
                           f"found {len(match)}")
    o = match[0]
    hits = o.get("offtargets") or []
    # ⛔ THE CENSORING GUARD. `junction_aso_offtarget` stores `ranked[:15]` on a default-depth run
    # while reporting the FULL count separately, so a truncated list would silently under-report the
    # locus set. A locus census over a truncated list is a lower bound wearing the costume of a
    # count, and this module must refuse rather than emit one.
    if len(hits) != o.get("n_offtarget_near_matches"):
        raise RuntimeError(
            f"{reagent}: the stored hit list holds {len(hits)} of "
            f"{o.get('n_offtarget_near_matches')} reported near-matches — this screen is truncated "
            f"and a locus census over it would be a lower bound, not a count")
    return o, [h for h in hits if h.get("risk") == GAP_PAIRED_CLASS]


def _locus_rows(path=SCREEN, reagent=REAGENT):
    """(oligo record, ordered locus rows, provenance) — the six loci and what they rest on."""
    oligo, gap_paired = _screen_hits(path, reagent)
    per = {}
    n_second_pass = 0
    for h in gap_paired:
        sym, how = gene_of(h)
        if how == "full_definition_second_pass":
            n_second_pass += 1
        row = per.setdefault(sym, {"locus": sym, "n_transcript_records": 0,
                                   "n_curated_records": 0, "n_predicted_records": 0,
                                   "accessions": [], "definition_example": None,
                                   "symbol_resolved_by": how})
        row["n_transcript_records"] += 1
        acc = str(h.get("acc") or "")
        row["accessions"].append(acc)
        if acc.startswith(("NM_", "NR_")):
            row["n_curated_records"] += 1
        elif acc.startswith(("XM_", "XR_")):
            row["n_predicted_records"] += 1
        if row["definition_example"] is None:
            row["definition_example"] = h.get("defn")

    rows = sorted(per.values(), key=lambda r: (-r["n_transcript_records"], r["locus"]))
    for r in rows:
        r["accessions"] = sorted(set(r["accessions"]))
        r["identity_of_every_record"] = "14/16 (two mismatches), the loosest the screen admits"
    prov = {
        "screen": os.path.basename(path),
        "reagent_antisense_5to3": reagent,
        "junction_label": json.load(open(path, encoding="utf-8")).get("junction_label"),
        "n_near_matches_reported": oligo.get("n_offtarget_near_matches"),
        "n_minus_strand_not_hybridisable": oligo.get("n_minus_strand_not_hybridisable"),
        "n_gap_disrupted_no_cleavage": oligo.get("n_gap_disrupted_no_cleavage"),
        "n_gap_paired_hybridisable": len(gap_paired),
        "risk_class_read": GAP_PAIRED_CLASS,
        "n_loci": len(rows),
        "n_accession_fallbacks_resolved": n_second_pass,
        "_why_that_last_number_matters": (
            "`junction_aso_locus_collapse.locus_of` truncates each definition at its first comma "
            "before looking for a parenthesised symbol, so a gene whose DESCRIPTION contains a "
            "comma falls to a per-accession fallback and reads as one pseudo-locus per record. "
            "That many records were merged back onto their real gene here. A raw `locus_of` count "
            "of this reagent therefore returns more loci than exist, and the two counts must not be "
            "quoted against each other. See `gene_of`."),
    }
    return oligo, rows, prov


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Fetch — every arm records its own failure, and no arm can fail into a biological statement
# ─────────────────────────────────────────────────────────────────────────────────────────────

def _get(url, timeout=600, headers=None):
    req = urllib.request.Request(url, headers=dict(UA, **(headers or {})))
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read()


def _parse_gct(raw_gz, wanted):
    """Rows of a GCT whose `Description` is in `wanted`, plus the tissue column order.

    ⛔ THE SHAPE IS ASSERTED, NOT ASSUMED. A GCT declares its own row and column counts on line 2,
    and a header that disagrees with them means the file is not what this parser thinks it is —
    which, on a wide tab matrix, produces a shifted-by-one artifact that looks entirely normal.
    """
    text = gzip.GzipFile(fileobj=io.BytesIO(raw_gz)).read().decode("utf-8", "replace")
    lines = text.split("\n")
    if not lines or not lines[0].startswith("#1.2"):
        raise RuntimeError(f"not a GCT: first line is {lines[0][:60]!r}")
    n_rows, n_cols = (int(x) for x in lines[1].split("\t")[:2])
    header = lines[2].split("\t")
    if header[0] != "Name" or header[1] != "Description":
        raise RuntimeError(f"unexpected GCT header: {header[:3]}")
    tissues = header[2:]
    if len(tissues) != n_cols:
        raise RuntimeError(f"GCT declares {n_cols} data columns, header carries {len(tissues)}")
    want = {w.upper() for w in wanted}
    found, seen = {}, 0
    for ln in lines[3:]:
        if not ln.strip():
            continue
        seen += 1
        parts = ln.split("\t")
        sym = parts[1].strip()
        if sym.upper() not in want:
            continue
        if len(parts) != n_cols + 2:
            raise RuntimeError(f"{sym}: row has {len(parts) - 2} values against {n_cols} columns")
        vals = []
        for p in parts[2:]:
            try:
                vals.append(float(p))
            except ValueError:
                vals.append(None)
        # A symbol can appear on more than one gene model; keep every row rather than the first.
        found.setdefault(sym.upper(), []).append({"gencode_id": parts[0], "symbol": sym,
                                                  "values": vals})
    if seen != n_rows:
        raise RuntimeError(f"GCT declares {n_rows} rows, parsed {seen}")
    return {"tissues": tissues, "n_rows": n_rows, "rows": found}


def fetch_gtex(symbols, controls=tuple(GTEX_CONTROLS)):
    rec = {"source": "GTEx v8 gene-level median TPM",
           "url": GTEX_MEDIAN_TPM_URL,
           "release": "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm",
           "unit": "median TPM across that tissue's donors",
           "endpoint_used": None}
    want = sorted(set(symbols) | set(controls))
    try:
        raw = _get(GTEX_MEDIAN_TPM_URL, timeout=1800)
        rec["compressed_bytes"] = len(raw)
        rec.update(_parse_gct(raw, want))
        rec["endpoint_used"] = "release_gct"
        rec["_status"] = "read"
    except Exception as exc:  # noqa: BLE001 — an unread arm is UNKNOWN and says which arm and why
        rec["_status"] = f"fetch or parse failed: {type(exc).__name__}: {str(exc)[:300]}"
    return rec


def fetch_ncbi_gene(symbols):
    """What each locus IS. The arm that lets an absence from GTEx be attributed rather than guessed.

    ⭐ THIS IS THE ARM THAT ANSWERS THE `LOC` QUESTION. An uncharacterised NCBI-only locus has no
    GENCODE gene model under that symbol, so it CANNOT appear in arm A — and without this arm, that
    absence is indistinguishable from a gene GTEx measured at zero. One is "no instrument covered
    it", the other is a reading; conflating them is exactly the failure CLAUDE.md §4 names.
    """
    out = {"source": "NCBI Gene (E-utilities esearch + esummary)", "genes": {}}
    for sym in sorted(symbols):
        g = {"query": sym}
        try:
            q = urllib.parse.urlencode({"db": "gene", "retmode": "json",
                                        "term": f"{sym}[Gene Name] AND human[ORGN]"})
            hits = json.loads(_get(f"{EUTILS}/esearch.fcgi?{q}", timeout=120).decode())
            ids = hits.get("esearchresult", {}).get("idlist", [])
            g["gene_ids"] = ids
            if not ids:
                g["_status"] = "no NCBI Gene record matched this symbol"
                out["genes"][sym] = g
                continue
            q2 = urllib.parse.urlencode({"db": "gene", "retmode": "json", "id": ids[0]})
            summ = json.loads(_get(f"{EUTILS}/esummary.fcgi?{q2}", timeout=120).decode())
            doc = summ.get("result", {}).get(ids[0], {})
            g["gene_id"] = ids[0]
            for k in ("name", "description", "chromosome", "maplocation", "genomicinfo",
                      "summary", "otheraliases", "status"):
                if k in doc:
                    g[k] = doc[k]
            g["_status"] = "read"
        except Exception as exc:  # noqa: BLE001
            g["_status"] = f"fetch failed: {type(exc).__name__}: {str(exc)[:200]}"
        out["genes"][sym] = g
    return out


def fetch_hpa(symbols):
    """Human Protein Atlas consensus tissue RNA — a cross-check on arm A, best effort.

    ⚠ NOT INDEPENDENT OF GTEx. HPA's consensus tissue data incorporates GTEx among its sources, so
    agreement between this arm and arm A is a transport check, not a second measurement. It is
    fetched because it carries tissue calls and protein-level evidence GTEx does not, and it is
    labelled here so no reader can take concordance as replication.
    """
    out = {"source": "Human Protein Atlas search_download API",
           "_not_independent_of_gtex": (
               "HPA consensus tissue RNA incorporates GTEx; agreement with arm A is a transport "
               "check, not an independent measurement."),
           "genes": {}}
    cols = "g,gs,eg,gd,rnatsm,rnatd,rnats,rnacas,scml"
    for sym in sorted(symbols):
        try:
            q = urllib.parse.urlencode({"search": sym, "format": "json", "columns": cols,
                                        "compress": "no"})
            body = _get(f"{HPA_SEARCH}?{q}", timeout=180).decode("utf-8", "replace")
            rows = json.loads(body)
            exact = [r for r in rows if str(r.get("Gene", "")).upper() == sym.upper()]
            out["genes"][sym] = {"_status": "read", "n_rows": len(rows),
                                 "exact_symbol_rows": exact[:3]}
        except Exception as exc:  # noqa: BLE001
            out["genes"][sym] = {"_status": f"fetch failed: {type(exc).__name__}: "
                                            f"{str(exc)[:200]}"}
    return out


def fetch_emc_series(symbols):
    """The on-site arm: the six loci read in the two readable EMC series.

    ⭐ IT REUSES `emc_expression_panels._read_target` RATHER THAN RE-IMPLEMENTING IT, and that is a
    correctness argument, not laziness. Probe-to-symbol mapping on these two platforms is the part
    that has actually been hard here — GPL3290 needs an accession bridge whose completeness is
    budget-bound — and a second implementation would be free to disagree with the panels lane about
    whether a gene is readable at all. One mapping, one answer.
    ⛔ It writes NOTHING that lane owns: `_read_target` is a pure read, and the output lands only in
    this module's own inputs cache.
    """
    out = {"source": "GEO series matrices, read through emc_expression_panels._read_target",
           "targets": {}}
    try:
        from emc_expression_panels import TARGETS, _read_target  # noqa: E402
    except Exception as exc:  # noqa: BLE001
        out["_status"] = f"import failed: {type(exc).__name__}: {str(exc)[:200]}"
        return out
    want = {s.upper() for s in symbols}
    for tgt in TARGETS:
        try:
            rec = _read_target(tgt, want)
        except Exception as exc:  # noqa: BLE001
            rec = {"_status": f"read failed: {type(exc).__name__}: {str(exc)[:200]}",
                   "gse": tgt.get("gse")}
        # the full probe matrix is not ours to keep; only the wanted genes and the readability facts
        keep = {k: rec.get(k) for k in (
            "gse", "platform", "platform_matches_expected", "n_samples", "n_probes",
            "n_probes_mapped_to_a_symbol", "measured_probe_mapping_rate", "value_kind",
            "samples", "genes", "probe_symbol_mapping", "_status")}
        out["targets"][tgt["matrix_file"]] = keep
    return out


def collect():
    _, rows, prov = _locus_rows()
    symbols = [r["locus"] for r in rows]
    print(f"loci from the screen: {symbols}", file=sys.stderr)
    inp = {
        "_what": ("Raw retrievals behind aso-offtarget-tissue-expression.json. One block per arm; "
                  "an arm that failed says so here and its verdict downstream is `readable: false`."),
        "_generated_utc": datetime.now(timezone.utc).isoformat(),
        "loci_provenance": prov,
        "loci": rows,
        "arm_a_gtex": fetch_gtex(symbols),
        "arm_b_emc_series": fetch_emc_series(symbols),
        "arm_c_ncbi_gene": fetch_ncbi_gene(symbols),
        "arm_d_hpa": fetch_hpa(symbols),
    }
    with open(INPUTS, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(inp, indent=1, sort_keys=False) + "\n")
    print(f"wrote {os.path.basename(INPUTS)}", file=sys.stderr)
    return inp


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Derive — pure, offline, and unable to turn a failed arm into a biological statement
# ─────────────────────────────────────────────────────────────────────────────────────────────

def _control_verdict(gtex):
    """Did the matrix parse land the known-answer controls where they must be?

    ⛔ A RUN THAT FAILS THIS MUST NOT EMIT A LOCUS VERDICT. A column shift in a wide matrix is
    invisible in the numbers and fatal to every conclusion drawn from them; these three genes are
    the cheapest observation that discriminates a correct parse from a shifted one.
    """
    if gtex.get("_status") != "read":
        return {"ran": False, "why": "arm A was not read", "passed": None, "controls": {}}
    tissues = gtex.get("tissues") or []
    res, ok = {}, True
    for sym, spec in GTEX_CONTROLS.items():
        got = (gtex.get("rows") or {}).get(sym.upper())
        if not got:
            res[sym] = {"found": False, "passed": False, "why": spec["why"]}
            ok = False
            continue
        vals = got[0]["values"]
        pairs = [(t, v) for t, v in zip(tissues, vals) if v is not None]
        top = max(pairs, key=lambda p: p[1]) if pairs else (None, None)
        passed = top[0] in spec["expect_max_in"]
        res[sym] = {"found": True, "max_tissue": top[0], "max_median_tpm": top[1],
                    "expected_max_in": spec["expect_max_in"], "passed": passed,
                    "why": spec["why"]}
        ok = ok and passed
    return {"ran": True, "passed": ok, "controls": res,
            "_meaning": ("These assert that the tissue COLUMNS are aligned to the values. A failure "
                         "means the parse is shifted and every tissue figure below is wrong; it "
                         "does not mean the genes are unusual.")}


def _tissue_block(gtex, sym, tissues, label):
    """Median TPM for one locus across one named tissue list, or an explicit unreadable state."""
    if gtex.get("_status") != "read":
        return {"readable": False,
                "reason": f"arm A was not read ({gtex.get('_status')})",
                "block": label, "values": None}
    got = (gtex.get("rows") or {}).get(sym.upper())
    if not got:
        return {"readable": False,
                "reason": ("no row for this symbol in the GTEx v8 gene model — the locus is not "
                           "measured by this instrument. ⚠ THIS IS NOT A READING OF ZERO."),
                "block": label, "values": None}
    order = gtex.get("tissues") or []
    idx = {t: i for i, t in enumerate(order)}
    missing = [t for t in tissues if t not in idx]
    vals, per_model = {}, []
    for row in got:
        v = row["values"]
        one = {t: (v[idx[t]] if t in idx and idx[t] < len(v) else None) for t in tissues}
        per_model.append({"gencode_id": row["gencode_id"], "median_tpm": one})
    for t in tissues:
        seen = [m["median_tpm"][t] for m in per_model if m["median_tpm"][t] is not None]
        vals[t] = max(seen) if seen else None       # the highest model, the conservative direction
    return {"readable": True, "block": label, "values": vals,
            "n_gene_models": len(per_model), "per_gene_model": per_model,
            "tissue_labels_not_found": missing,
            "max_tissue_in_block": (max((t for t in tissues if vals.get(t) is not None),
                                        key=lambda t: vals[t], default=None)),
            "any_present_at_cut": any(v is not None and v >= PRESENT_TPM for v in vals.values())}


def _whole_body_context(gtex, sym):
    """Where this locus is HIGHEST across all 54 tissues, so a compartment figure has a scale.

    Without it a reader cannot tell 3 TPM in liver from "3 TPM in liver and 300 in brain", and those
    are different objects for a drug that does not cross the blood-brain barrier.
    """
    if gtex.get("_status") != "read":
        return None
    got = (gtex.get("rows") or {}).get(sym.upper())
    if not got:
        return None
    order = gtex.get("tissues") or []
    best = {}
    for row in got:
        for t, v in zip(order, row["values"]):
            if v is None:
                continue
            if t not in best or v > best[t]:
                best[t] = v
    top = sorted(best.items(), key=lambda kv: -kv[1])[:6]
    return {"top_tissues": [{"tissue": t, "median_tpm": v} for t, v in top],
            "n_tissues_at_or_above_cut": sum(1 for v in best.values() if v >= PRESENT_TPM),
            "n_tissues_read": len(best)}


def _emc_block(emc, sym):
    """The on-site arm for one locus: was a probe there at all, and what did it read."""
    per = {}
    readable_anywhere = False
    for mf, tgt in (emc.get("targets") or {}).items():
        if (tgt or {}).get("_status") != "read":
            per[mf] = {"readable": False,
                       "reason": f"series not read ({(tgt or {}).get('_status')})"}
            continue
        genes = tgt.get("genes") or {}
        g = genes.get(sym.upper()) or genes.get(sym)
        if not g:
            per[mf] = {"readable": False, "platform": tgt.get("platform"),
                       "reason": ("no probe on this platform maps to this symbol — the READ could "
                                  "not be taken. ⚠ THIS IS NOT A STATEMENT THAT THE GENE IS OFF."),
                       "probe_mapping_rate": tgt.get("measured_probe_mapping_rate")}
            continue
        readable_anywhere = True
        pct = [p for p in (g.get("array_percentile") or []) if p is not None]
        per[mf] = {"readable": True, "platform": tgt.get("platform"),
                   "n_probes_mapping": g.get("n_probes_mapping"),
                   "n_samples": tgt.get("n_samples"),
                   "value_kind": tgt.get("value_kind"),
                   "array_percentile": g.get("array_percentile"),
                   "median_array_percentile": (sorted(pct)[len(pct) // 2] if pct else None),
                   "_percentile_is_the_readout": (
                       "the gene's rank within THIS array's own probe distribution, which is the "
                       "only 'is it on at all' reading an array supports; the raw value is "
                       "platform-relative and is not comparable to a TPM.")}
    return {"readable_on_any_platform": readable_anywhere, "per_series": per}


def _locus_verdict(row, exposure, tumour_proxy, emc, ncbi):
    """One sentence per locus, and it is allowed to say that nothing can be concluded."""
    sym = row["locus"]
    ident = (ncbi.get("genes") or {}).get(sym) or {}
    uncharacterised = "uncharacterized" in str(ident.get("description", "")).lower() \
        or sym.startswith("LOC")

    if not exposure["readable"]:
        if uncharacterised:
            return ("NOT_MEASURABLE_UNCHARACTERISED",
                    "An uncharacterised locus with no GTEx v8 gene model, so no exposure-organ "
                    "expression figure exists in this instrument. Nothing here says it is absent "
                    "from liver or kidney — only that public bulk expression data as retrieved "
                    "cannot answer the question for it.")
        return ("NOT_MEASURED",
                "No expression reading could be taken in the exposure arm; the reason is recorded "
                "and is not a reading of absence.")

    vals = {k: v for k, v in exposure["values"].items() if v is not None}
    hi = max(vals.values()) if vals else None
    if hi is None:
        return ("NOT_MEASURED", "The exposure arm carried no value for this locus.")
    if hi >= 10:
        return ("EXPRESSED_IN_AN_EXPOSURE_ORGAN",
                f"Median TPM reaches {hi:g} in {exposure['max_tissue_in_block']}. A transcript at "
                f"this level in a dosed organ is where an off-target hypothesis would have to be "
                f"tested; whether a two-mismatch duplex engages it is not answered by any screen "
                f"here.")
    if hi >= PRESENT_TPM:
        return ("LOW_IN_EXPOSURE_ORGANS",
                f"Median TPM peaks at {hi:g} in {exposure['max_tissue_in_block']} — detectable and "
                f"low against the whole-body maximum recorded alongside it.")
    return ("BELOW_DETECTION_IN_EXPOSURE_ORGANS",
            f"Median TPM is below {PRESENT_TPM:g} in every exposure tissue (highest {hi:g}). This "
            f"is a measured low reading in GTEx v8, not a safety statement.")


def derive(inp):
    gtex = inp.get("arm_a_gtex") or {}
    emc = inp.get("arm_b_emc_series") or {}
    ncbi = inp.get("arm_c_ncbi_gene") or {}
    hpa = inp.get("arm_d_hpa") or {}
    controls = _control_verdict(gtex)

    per_locus = []
    for row in inp.get("loci") or []:
        sym = row["locus"]
        exposure = _tissue_block(gtex, sym, EXPOSURE_TISSUES, "exposure_liver_kidney")
        proxy = _tissue_block(gtex, sym, TUMOUR_COMPARTMENT_PROXY_TISSUES,
                              "tumour_compartment_normal_tissue_proxy")
        # ⛔ THE CONTROL GATE. A shifted parse must not be able to produce a locus verdict.
        if controls["ran"] and controls["passed"] is False:
            tier, sentence = ("NOT_MEASURED",
                              "The GTEx known-answer controls failed, so the tissue columns of this "
                              "parse are not trusted and no exposure figure is emitted.")
            exposure = {"readable": False, "block": "exposure_liver_kidney", "values": None,
                        "reason": "withheld: arm A's known-answer controls failed"}
            proxy = {"readable": False, "block": "tumour_compartment_normal_tissue_proxy",
                     "values": None, "reason": "withheld: arm A's known-answer controls failed"}
        else:
            tier, sentence = _locus_verdict(row, exposure, proxy, emc, ncbi)
        ident = (ncbi.get("genes") or {}).get(sym) or {}
        per_locus.append({
            "locus": sym,
            "screen_records": {
                "n_transcript_records": row["n_transcript_records"],
                "n_curated_records": row["n_curated_records"],
                "n_predicted_records": row["n_predicted_records"],
                "identity_of_every_record": row["identity_of_every_record"],
                "⚠_record_count_is_annotation_depth": (
                    "how many transcript variants RefSeq lists for this gene, not expression, not "
                    "affinity and not risk. A locus with many records is not thereby a larger "
                    "liability, and one with a single record is not thereby a smaller one."),
            },
            "identity": {
                "ncbi_status": ident.get("_status"),
                "ncbi_gene_id": ident.get("gene_id"),
                "description": ident.get("description"),
                "map_location": ident.get("maplocation"),
                "ncbi_summary": ident.get("summary"),
            },
            "exposure_compartment_liver_kidney": exposure,
            "tumour_compartment_normal_tissue_proxy": proxy,
            "tumour_compartment_emc_tumours": _emc_block(emc, sym),
            "whole_body_context": _whole_body_context(gtex, sym),
            "hpa_cross_check": (hpa.get("genes") or {}).get(sym),
            "tier": tier,
            "sentence": sentence,
        })

    readable = [p for p in per_locus if p["exposure_compartment_liver_kidney"]["readable"]]
    concern = [p["locus"] for p in per_locus if p["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN"]
    unmeasurable = [p["locus"] for p in per_locus
                    if p["tier"] in ("NOT_MEASURED", "NOT_MEASURABLE_UNCHARACTERISED")]

    return {
        "_what": ("Tissue expression of every gene locus the clinically-relevant junction gapmer's "
                  "deep off-target screen returns, split into the organs a systemically dosed "
                  "phosphorothioate reaches and the compartment the tumour occupies."),
        "_framing": (
            "⛔ NOTHING IN THIS FILE IS AN EFFICACY, SELECTIVITY, SAFETY, THERAPEUTIC-WINDOW OR "
            "CLINICAL-READINESS CLAIM FOR ANY SEQUENCE. Every hit behind it sits at 14/16 identity "
            "— two mismatches in a 16-mer — and whether such a duplex is an RNase-H1 substrate at "
            "all is an affinity question no screen here answers. Expression is a NECESSARY "
            "condition for an off-target effect and never a sufficient one, so a gene being "
            "expressed is not a predicted cleavage event and a gene being unexpressed is not "
            "safety."),
        "_what_this_is_not": [
            "Not a cleavage assay, and not a prediction of one. No hit was re-aligned, no duplex "
            "stability was computed, and no thermodynamic threshold separates these hits from each "
            "other — they are the screen's loosest admitted class, all at two mismatches.",
            "Not a risk ranking by transcript-record count. Record count is annotation depth.",
            "Not a tumour measurement where it says proxy. GTEx contains no EMC and no sarcoma; the "
            "soft-tissue block is the NORMAL tissue of the compartment EMC arises in.",
            "Not a reading of absence anywhere. Every unreadable locus carries the reason the read "
            "could not be taken, and no absence is rendered as a zero.",
            f"PRESENT_TPM = {PRESENT_TPM:g} is a STATED legibility cut, not a threshold of concern, "
            f"and every raw median is released so another cut can be applied without re-running.",
        ],
        "_cost": "$0 — public reference data on a CPU runner. No GPU, no rental, no wet lab.",
        "_generated_utc": inp.get("_generated_utc"),
        "reagent": inp.get("loci_provenance"),
        "method": {
            "exposure_tissues": EXPOSURE_TISSUES,
            "_why_those": ("Systemically dosed phosphorothioate gapmers distribute predominantly to "
                           "liver and kidney, so those organs carry the exposure question."),
            "tumour_compartment_proxy_tissues": TUMOUR_COMPARTMENT_PROXY_TISSUES,
            "_why_a_proxy": ("EMC arises in deep soft tissue of the extremities and has a myxoid "
                             "stroma. No reference expression atlas contains that tumour, so these "
                             "are the normal tissues of that anatomical compartment, and the actual "
                             "tumour reading is the EMC array arm beside them."),
            "present_tpm_cut": PRESENT_TPM,
            "arms": {
                "A_gtex": {"status": gtex.get("_status"), "url": gtex.get("url"),
                           "release": gtex.get("release"), "unit": gtex.get("unit"),
                           "endpoint_used": gtex.get("endpoint_used"),
                           "n_tissues": len(gtex.get("tissues") or []) or None},
                "B_emc_series": {"targets": {k: (v or {}).get("_status")
                                             for k, v in (emc.get("targets") or {}).items()}},
                "C_ncbi_gene": {"status": {k: (v or {}).get("_status")
                                           for k, v in (ncbi.get("genes") or {}).items()}},
                "D_hpa": {"status": {k: (v or {}).get("_status")
                                     for k, v in (hpa.get("genes") or {}).items()},
                          "_not_independent": hpa.get("_not_independent_of_gtex")},
            },
            "known_answer_controls": controls,
        },
        "summary": {
            "n_loci": len(per_locus),
            "n_loci_with_a_readable_exposure_reading": len(readable),
            "loci_expressed_in_an_exposure_organ": concern,
            "loci_whose_exposure_question_is_unanswerable_from_public_data": unmeasurable,
            "⚠_what_a_clean_exposure_column_does_and_does_not_buy": (
                "It removes one hypothetical liability from a list. It does not make the reagent "
                "clean, because the same list holds loci this instrument cannot measure at all, and "
                "because none of these hits has been shown to be cleavable in the first place."),
        },
        "per_locus": per_locus,
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────

def _empty_inputs():
    """A coherent not-yet-fetched state, so the derive half is exercisable with no network."""
    _, rows, prov = _locus_rows()
    return {"_what": "placeholder: no retrieval has been run yet",
            "_generated_utc": None,
            "loci_provenance": prov, "loci": rows,
            "arm_a_gtex": {"_status": "not fetched", "url": GTEX_MEDIAN_TPM_URL},
            "arm_b_emc_series": {"targets": {}},
            "arm_c_ncbi_gene": {"genes": {}},
            "arm_d_hpa": {"genes": {}}}


def _load_inputs():
    if os.path.exists(INPUTS):
        return json.load(open(INPUTS, encoding="utf-8"))
    return _empty_inputs()


def selftest():
    """Offline assertions of the guards, run BEFORE the fetch so a broken derive costs seconds.

    ⛔ EVERY ONE OF THESE IS A WAY THIS ARTIFACT COULD LIE, and all four are pure arithmetic over
    constructed inputs, so none of them needs a network.
    """
    # (1) the locus set derives from the screen and the censoring guard is live
    _, rows, prov = _locus_rows()
    assert prov["n_gap_paired_hybridisable"] == sum(r["n_transcript_records"] for r in rows)
    assert prov["n_loci"] == len(rows) >= 1

    # (2) an unfetched arm can never become a biological statement
    art = derive(_empty_inputs())
    for p in art["per_locus"]:
        assert p["exposure_compartment_liver_kidney"]["readable"] is False
        assert p["tier"] in ("NOT_MEASURED", "NOT_MEASURABLE_UNCHARACTERISED")
        assert "not a reading of absence" in p["sentence"] or "cannot answer" in p["sentence"]

    # (3) a shifted parse cannot emit a locus verdict — the control gate really gates
    bad = _empty_inputs()
    bad["arm_a_gtex"] = {"_status": "read", "tissues": ["Liver", "Kidney - Cortex"],
                         "rows": {"ALB": [{"gencode_id": "x", "symbol": "ALB",
                                           "values": [1.0, 900.0]}],
                                  rows[0]["locus"].upper(): [
                                      {"gencode_id": "y", "symbol": rows[0]["locus"],
                                       "values": [500.0, 500.0]}]}}
    shifted = derive(bad)
    assert shifted["method"]["known_answer_controls"]["passed"] is False
    for p in shifted["per_locus"]:
        assert p["tier"] == "NOT_MEASURED", "a failed control still emitted a verdict"
        assert p["exposure_compartment_liver_kidney"]["readable"] is False

    # (4) a real high liver reading, with controls passing, IS reported as one
    good = _empty_inputs()
    tis = EXPOSURE_TISSUES + ["Heart - Left Ventricle", "Muscle - Skeletal"]
    def _row(sym, mapping):
        return [{"gencode_id": "g", "symbol": sym,
                 "values": [mapping.get(t, 0.0) for t in tis]}]
    good["arm_a_gtex"] = {"_status": "read", "tissues": tis, "rows": {
        "ALB": _row("ALB", {"Liver": 999.0}),
        "UMOD": _row("UMOD", {"Kidney - Medulla": 800.0}),
        "MYH7": _row("MYH7", {"Heart - Left Ventricle": 700.0}),
        rows[0]["locus"].upper(): _row(rows[0]["locus"], {"Liver": 120.0}),
    }}
    ok = derive(good)
    assert ok["method"]["known_answer_controls"]["passed"] is True
    first = [p for p in ok["per_locus"] if p["locus"] == rows[0]["locus"]][0]
    assert first["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN", first["tier"]
    assert first["exposure_compartment_liver_kidney"]["values"]["Liver"] == 120.0
    # and a locus with no row is unreadable rather than zero
    other = [p for p in ok["per_locus"] if p["locus"] != rows[0]["locus"]]
    assert other, "the screen must return more than one locus for this assertion to mean anything"
    assert all(not p["exposure_compartment_liver_kidney"]["readable"] for p in other)
    assert all("NOT A READING OF ZERO" in
               p["exposure_compartment_liver_kidney"]["reason"].upper() for p in other)

    print("selftest ok: locus derivation, unfetched-arm refusal, control gate, and the "
          "unreadable-is-not-zero rule all hold", file=sys.stderr)
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    inp = collect() if "--fetch" in argv else _load_inputs()
    art = derive(inp)
    new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("aso-offtarget-tissue-expression.json is stale; re-run without --check",
                  file=sys.stderr)
            return 1
        print("off-target tissue-expression artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    s = art["summary"]
    print(f"wrote {os.path.basename(OUT)}: {s['n_loci']} loci, "
          f"{s['n_loci_with_a_readable_exposure_reading']} with a readable exposure reading; "
          f"expressed in an exposure organ: {s['loci_expressed_in_an_exposure_organ']}; "
          f"unanswerable: {s['loci_whose_exposure_question_is_unanswerable_from_public_data']}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
