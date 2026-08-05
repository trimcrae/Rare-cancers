#!/usr/bin/env python3
"""
GSE299349 — "Targeting ATR signaling in sarcoma with homologous recombination deficiency".

WHY THIS MODULE EXISTS, stated before anything it computes.

The EMC ATR route (`emc-post-degrader-options.md` route 1) rests on ONE published mechanism
(PMID 37205599): FET fusion oncoproteins are recruited to double-strand breaks through their
N-terminal IDR, they IMPAIR ATM activation, and the compensatory ATR axis becomes load-bearing.
That paper's own framing is explicitly NOT a homologous-recombination-deficiency framing.

`emc_atr_vulnerability.py`'s four-archive search surfaced a 2026 GEO deposit whose title selects
sarcoma on the OTHER biomarker — homologous recombination deficiency — and nobody had read it. Three
questions follow, and this module answers each with evidence or an explicit CANNOT_DETERMINE:

  Q1  Does it supply ATR-inhibitor RESPONSE data in sarcoma?  (part D of the assessment had no
      instrument; a sarcoma ATRi response panel would be one.)
  Q2  Does it contain EMC / any NR4A3-rearranged sample?      (there has never been one.)
  Q3  Does it select on HRD rather than on FET-fusion status? (potentially ADVERSE to route 1:
      a competing biomarker hypothesis, or a different patient population.)

⚠ THE DISCIPLINE THIS MODULE IS BUILT AROUND. A GEO series TITLE is a claim by its depositors, not
a measurement, and this repo has been bitten twice by treating one as the latter: GSE24369 is titled
"low-grade fibromyxoid sarcoma" and silently contains six EMC tumours, and DepMap's one EMC-labelled
model is recorded by the curated record as carrying no EWSR1 fusion. So EVERY verdict below is
computed from SAMPLE-LEVEL metadata — per-sample title, source, characteristics, treatment and
growth protocols — and every hit is reported with the sample and the field it came from, verbatim.

⚠ AND THE SECOND DISCIPLINE (CLAUDE.md §4). An absent reading is not a reading of absence. Every
fetch records its HTTP outcome; a field that could not be READ is `CANNOT_DETERMINE` with the reason,
never a `false`. `derive()` refuses to answer any question whose input document did not arrive.

$0 — pure stdlib, CPU only, no GPU and no rental. The dev sandbox's egress proxy 403s NCBI on
CONNECT, so the fetch half runs in CI (`.github/workflows/emc-expression-datasets.yml`,
`mode: gse-series`) and the derive half is offline-reproducible from the committed inputs cache:

    python3 research/modalities/atr_hrd_sarcoma_series.py --fetch    # CI only (needs NCBI)
    python3 research/modalities/atr_hrd_sarcoma_series.py --check    # offline, re-derives + diffs

No efficacy, potency, dose, safety, therapeutic-window or clinical-readiness claim is made or
implied anywhere in this module or its artifact.
"""

import argparse
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "atr-hrd-sarcoma-series.json")
INPUTS = os.path.join(HERE, "atr-hrd-sarcoma-series-inputs.json")
QUANT_INPUTS = os.path.join(HERE, "atr-hrd-sarcoma-series-quant-inputs.json")

SERIES = "GSE299349"
# The mechanism paper route 1 rests on. Fetched here for ONE reason: Q3 asks whether a 2026 sarcoma
# ATR programme is selecting on a biomarker that paper argues AGAINST, and that comparison has to be
# made against the paper's own words rather than against this repo's summary of them.
MECHANISM_PMID = "37205599"

UA = {"User-Agent": "rare-cancers/1.0", "Accept": "text/plain, application/json, */*"}


# =============================================================================================
# fetch half — network. CI only.
# =============================================================================================
def _get(url, timeout=120, tries=4, note=""):
    """Returns (bytes_or_None, status_string). NEVER raises: a failed fetch must be RECORDED,
    because a verdict computed over a document that did not arrive is the exact failure mode this
    module exists to avoid."""
    last = ""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            if url.endswith(".gz"):
                try:
                    body = gzip.decompress(body)
                except Exception as e:      # noqa: BLE001
                    return None, f"gunzip failed: {type(e).__name__}: {e}"
            return body, f"HTTP 200, {len(body)} bytes"
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (400, 404):        # deterministic; retrying a 404 is just slower
                break
        except Exception as e:              # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
        time.sleep(2 * (i + 1))
    return None, f"FAILED after {tries} tries: {last}" + (f" ({note})" if note else "")


def _ftp_dir(gse):
    grp = gse[:-3] + "nnn"
    return f"https://ftp.ncbi.nlm.nih.gov/geo/series/{grp}/{gse}/"


# ⚠ MEASURED, not guessed: GSE299349's `targ=all` SOFT came back at 40,732,275 bytes across
# 1,194,948 lines, and 399,893 of those lines are `!Platform_sample_id` — GEO listing EVERY sample
# ever deposited on the Illumina NovaSeq 6000 platform, which has nothing to do with this series.
# Dropping them is what makes the inputs cache committable; the derive half reads only the
# platform's title/technology/organism, so the artifact is byte-identical either way.
_SOFT_DROP = ("!Platform_sample_id", "!Platform_series_id")


def _trim_soft(txt):
    kept, dropped, in_table = [], 0, False
    for line in txt.splitlines(True):
        if line.startswith("!") and line.split("=", 1)[0].strip() in _SOFT_DROP:
            dropped += 1
            continue
        if "_table_begin" in line:
            in_table = True
            kept.append(line)
            continue
        if "_table_end" in line:
            in_table = False
            kept.append(line)
            continue
        if in_table:
            dropped += 1
            continue
        kept.append(line)
    return "".join(kept), dropped


def fetch(series=SERIES):
    """One network pass. Everything it reads is stored verbatim so `--check` can re-derive offline."""
    inp = {
        "_what": (
            "Raw records for the GEO series characterisation. Stored verbatim so the derive half is "
            "reproducible with no network — the reproduce mode is a real one, not a re-run of the "
            "same call."
        ),
        "series": series,
        "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fetches": {},
    }

    def grab(key, url, decode=True):
        body, status = _get(url)
        inp["fetches"][key] = {"url": url, "status": status}
        if body is None:
            inp[key] = None
            return None
        txt = body.decode("utf-8", "replace") if decode else body
        inp[key] = txt
        return txt

    # 1 · SAMPLE-LEVEL metadata for the whole series in one request.
    #     `targ=all&view=brief` returns the SERIES, every SAMPLE and the PLATFORM header WITHOUT the
    #     platform's probe table — which on an array platform is the large half and is not wanted.
    grab("soft_all_brief",
         "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
         f"?acc={series}&targ=all&form=text&view=brief")

    # Fallback if acc.cgi refuses: the FTP family SOFT carries the same sample records.
    if not inp.get("soft_all_brief"):
        grab("soft_family_gz", _ftp_dir(series) + f"soft/{series}_family.soft.gz")

    for k in ("soft_all_brief", "soft_family_gz"):
        if inp.get(k):
            raw_len = len(inp[k])
            inp[k], dropped = _trim_soft(inp[k])
            inp["fetches"][k]["trimmed"] = (
                f"{raw_len} bytes on the wire -> {len(inp[k])} stored; {dropped} platform-roster "
                "and data-table lines dropped (see _trim_soft: they are not read by derive())")

    # 2 · Does a PROCESSED matrix exist, or only raw reads? Two directory listings answer it.
    grab("ftp_matrix_listing", _ftp_dir(series) + "matrix/")
    grab("ftp_suppl_listing", _ftp_dir(series) + "suppl/")

    # 3 · The GEO DataSets summary — carries the PubMed link, sample count and assay types as GEO
    #     itself indexes them, independently of the SOFT record.
    esearch, st = _get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                       f"?db=gds&retmode=json&term={series}[Accession]")
    inp["fetches"]["gds_esearch"] = {"status": st}
    uid = None
    if esearch:
        try:
            ids = json.loads(esearch)["esearchresult"]["idlist"]
            uid = ids[0] if ids else None
        except Exception as e:      # noqa: BLE001
            inp["fetches"]["gds_esearch"]["parse_error"] = f"{type(e).__name__}: {e}"
    inp["gds_uid"] = uid
    if uid:
        grab("gds_esummary",
             "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
             f"?db=gds&retmode=json&id={uid}")

    # 4 · The publication, if the series names one — and if it does not, ask Europe PMC whether any
    #     paper cites the accession, which is how a deposit-before-publication series is found.
    pmids = sorted(set(re.findall(r"!Series_pubmed_id\s*=\s*(\d+)", inp.get("soft_all_brief") or "")))
    if not pmids and inp.get("gds_esummary"):
        pmids = sorted(set(re.findall(r'"pubmedids":\s*\[\s*"?(\d+)', inp["gds_esummary"])))
    inp["series_pmids"] = pmids
    for p in pmids:
        grab(f"europepmc_{p}",
             "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
             f"?query=EXT_ID:{p}%20AND%20SRC:MED&resultType=core&format=json")
    grab("europepmc_accession_search",
         "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
         f"?query=%22{series}%22&resultType=core&format=json&pageSize=25")

    # ⭑ A series with no declared PMID is not a series with no paper. Ask three more ways: the
    #   depositing authors, the signature the summary names, and the title's own words. Recorded
    #   verbatim so "no publication found" is a SEARCH with a record, not an assertion.
    contribs = re.findall(r"!Series_contributor\s*=\s*(.+)", inp.get("soft_all_brief") or "")
    # ⚠ GEO writes a contributor as `First,Middle,Last` — so the SURNAME is the LAST field, not the
    # first. Taking the first produced `AUTH:"Chantal" AND AUTH:"Lara"`, which returned 0 hits on a
    # paper that exists. A search that fails for a formatting reason is indistinguishable, in the
    # artifact, from one that found nothing.
    surnames = sorted({c.strip().split(",")[-1].strip() for c in contribs if c.strip()})
    sig = re.findall(r"\b([A-Z]{3,8}-HRD|SARC-[A-Z]+)\b", inp.get("soft_all_brief") or "")
    queries = {}
    if len(surnames) >= 2:
        queries["by_authors"] = " AND ".join(f'AUTH:"{s}"' for s in surnames[:3])
    for s in sorted(set(sig))[:2]:
        queries[f"by_signature_{s}"] = f'"{s}"'
    queries["by_title_words"] = 'TITLE:"ATR" AND TITLE:sarcoma AND TITLE:"homologous recombination"'
    inp["publication_queries"] = queries
    for name, q in queries.items():
        grab(f"europepmc_pub_{name}",
             "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
             f"?query={urllib.parse.quote(q)}&resultType=core&format=json&pageSize=25")

    # 4b · If a candidate publication was found by search, pull its record and OA full text. The
    #      series declares no PMID, so this is the only route to what the authors actually claim.
    cand = set()
    for name in list(queries):
        raw = inp.get(f"europepmc_pub_{name}")
        if not raw:
            continue
        try:
            for h in json.loads(raw).get("resultList", {}).get("result") or []:
                t = (h.get("title") or "").lower()
                if "atr" in t and "sarcoma" in t and "homologous recombination" in t:
                    cand.add(h.get("pmid"))
                    if h.get("pmcid"):
                        inp.setdefault("candidate_pmcids", {})[h.get("pmid")] = h["pmcid"]
        except Exception:       # noqa: BLE001
            pass
    inp["candidate_publication_pmids"] = sorted(x for x in cand if x)
    for p, pmc in sorted((inp.get("candidate_pmcids") or {}).items()):
        grab(f"candidate_fulltext_{p}",
             f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML")

    # 5 · The mechanism paper, for Q3. Its own words about HR deficiency are the comparison.
    grab(f"europepmc_{MECHANISM_PMID}",
         "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
         f"?query=EXT_ID:{MECHANISM_PMID}%20AND%20SRC:MED&resultType=core&format=json")
    mech = inp.get(f"europepmc_{MECHANISM_PMID}")
    pmcid = None
    if mech:
        m = re.search(r'"pmcid":"(PMC\d+)"', mech)
        pmcid = m.group(1) if m else None
    inp["mechanism_pmcid"] = pmcid
    if pmcid:
        grab("mechanism_fulltext_xml",
             f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML")

    return inp


# =============================================================================================
# The identity check on the EMC-labelled model.
#
# ⭐ WHY IT IS NOT OPTIONAL. This repo's most consequential recent finding is that the model it
# called "the one real EMC line in DepMap" is recorded by Cellosaurus as NOT carrying an EWSR1
# fusion (assessment §2). An EMC LABEL is not an EMC FUSION, and a new EMC-labelled sample must
# face the same question the old one failed — before anything is built on it, not after.
#
# ⛔ WHAT THIS CANNOT BE. A transcript quantification cannot call a fusion: a Salmon index has no
# fusion transcript in it, and NR4A3 expression is a CONSEQUENCE that other things can produce.
# So this is CORROBORATION OR ITS ABSENCE, never a call. What makes it worth doing anyway is that
# the comparator is unusually good: 67 other sarcoma samples quantified by the same submitter in
# the same deposit, which is a far better background than the pan-cancer percentile that gave
# H-EMC-SS its weak corroboration.
# =============================================================================================
GENE_PANEL = {
    # the question
    "NR4A3": ["NM_006981", "NM_173198", "NM_173199", "NM_173200"],
    # paralogue context — an EMC fusion drives the NR4A3 body specifically, not the family
    "NR4A1": ["NM_002135", "NM_173157", "NM_173158"],
    "NR4A2": ["NM_006186", "NM_173171", "NM_173172", "NM_173173"],
    # ⭑ instrument controls, both directions. Without these a zero is unreadable: it could be the
    #   biology or it could be that the panel matched nothing.
    "ACTB": ["NM_001101"],
    "GAPDH": ["NM_002046", "NM_001256799", "NM_001289745", "NM_001289746"],
    "ALB": ["NM_000477"],            # liver-restricted: must be ~0 in every sarcoma sample
    "INS": ["NM_000207", "NM_001185097", "NM_001185098", "NM_001291897"],
}
_ACC2GENE = {a: g for g, accs in GENE_PANEL.items() for a in accs}


def _parse_quant_sf(raw):
    """Salmon quant.sf -> ({gene: summed TPM}, n_rows, first_names, matched_by).

    Two naming conventions are handled and the one used is RECORDED, because a panel that silently
    matched nothing and a gene that is genuinely off both look like 0.0."""
    txt = raw.decode("utf-8", "replace")
    lines = txt.splitlines()
    if not lines:
        return {}, 0, [], "EMPTY_FILE"
    header = lines[0].split("\t")
    try:
        i_name, i_tpm = header.index("Name"), header.index("TPM")
    except ValueError:
        return {}, len(lines) - 1, lines[:2], f"UNEXPECTED_HEADER: {header[:6]}"

    tot, first, by_symbol, by_acc = {}, [], 0, 0
    for line in lines[1:]:
        f = line.split("\t")
        if len(f) <= max(i_name, i_tpm):
            continue
        name = f[i_name]
        if len(first) < 3:
            first.append(name)
        try:
            tpm = float(f[i_tpm])
        except ValueError:
            continue
        parts = name.split("|")
        gene = None
        for p in parts:
            if p in GENE_PANEL:
                gene, by_symbol = p, by_symbol + 1
                break
        if gene is None:
            for p in parts:
                acc = p.split(".")[0]
                if acc in _ACC2GENE:
                    gene, by_acc = _ACC2GENE[acc], by_acc + 1
                    break
        if gene:
            tot[gene] = tot.get(gene, 0.0) + tpm
    matched = ("SYMBOL_IN_NAME" if by_symbol else
               "REFSEQ_ACCESSION" if by_acc else "NOTHING_MATCHED")
    return tot, len(lines) - 1, first, matched


def fetch_quant(art_path=ART):
    """Download every sample's processed quantification and reduce it to the gene panel.

    Only the panel is stored — 68 samples x 7 genes — so the inputs cache stays committable while
    the read stays reproducible."""
    with open(art_path) as f:
        art = json.load(f)
    out = {"_what": "Per-sample gene-panel TPM from each sample's own Salmon quantification.",
           "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "panel": {g: accs for g, accs in GENE_PANEL.items()},
           "per_sample": {}}
    for rec in art.get("samples", []):
        gsm = rec["accession"]
        urls = [u.replace("ftp://ftp.ncbi.nlm.nih.gov", "https://ftp.ncbi.nlm.nih.gov")
                for u in rec.get("supplementary_files", []) if "quant.sf" in u]
        if not urls:
            out["per_sample"][gsm] = {"status": "no quant.sf supplementary file listed"}
            continue
        body, status = _get(urls[0], timeout=300, tries=3)
        if body is None:
            out["per_sample"][gsm] = {"status": status, "url": urls[0]}
            continue
        # ⚠ DO NOT gunzip here. `_get` already decompresses any URL ending in `.gz`, and gunzipping
        # a second time failed all 68 samples on run 31006439097 with
        # `BadGzipFile: Not a gzipped file (b'Na')` — where `Na` is the start of the quant.sf
        # header `Name\tLength\t…`, i.e. the file had arrived intact and was destroyed on the way
        # in. Kept as a tolerant branch rather than deleted, because a future GEO URL without a
        # `.gz` suffix would arrive still compressed.
        if body[:2] == b"\x1f\x8b":
            try:
                body = gzip.decompress(body)
            except Exception as e:      # noqa: BLE001
                out["per_sample"][gsm] = {"status": f"gunzip failed: {type(e).__name__}: {e}"}
                continue
        tpm, nrows, first, matched = _parse_quant_sf(body)
        out["per_sample"][gsm] = {
            "status": status, "url": urls[0], "n_transcript_rows": nrows,
            "first_names_verbatim": first, "matched_by": matched,
            "panel_tpm": {g: round(tpm.get(g, 0.0), 4) for g in GENE_PANEL},
        }
        print(f"  {gsm} {rec['title']}: rows={nrows} matched_by={matched} "
              f"NR4A3={tpm.get('NR4A3', 0.0):.2f}")
    return out


def derive_quant(q, art):
    """Where does the EMC-labelled model sit for NR4A3 against the 67 others?"""
    per = q.get("per_sample") or {}
    titles = {r["accession"]: r["title"] for r in art.get("samples", [])}
    emc = (art.get("q2_emc_or_nr4a3_sample") or {}).get("samples_with_a_strong_EMC_or_NR4A3_term") or []

    read = {g: v for g, v in per.items() if isinstance(v.get("panel_tpm"), dict)}
    failed = sorted(set(per) - set(read))
    res = {
        "_what": "NR4A3 expression in the EMC-labelled model against every other sample in the "
                 "same deposit, quantified by the same submitter with the same tool.",
        "_cannot": ("⛔ This CANNOT call a fusion. A Salmon index contains no fusion transcript, "
                    "and NR4A3 expression is a consequence other things can produce. It is "
                    "corroboration of a LABEL or the absence of it — nothing more."),
        "n_samples_read": len(read),
        "n_samples_that_failed_to_read": len(failed),
        "samples_that_failed_to_read": failed,
        "matched_by": sorted({v.get("matched_by") for v in read.values()}),
        "n_transcript_rows_range": [min((v["n_transcript_rows"] for v in read.values()), default=0),
                                    max((v["n_transcript_rows"] for v in read.values()), default=0)],
    }
    if not read:
        res["verdict"] = "CANNOT_DETERMINE — no quantification file was readable"
        return res
    if res["matched_by"] == ["NOTHING_MATCHED"]:
        res["verdict"] = "CANNOT_DETERMINE — the gene panel matched no transcript name"
        res["observed_name_format"] = sorted({tuple(v["first_names_verbatim"])
                                              for v in read.values()})[:3]
        return res

    # instrument controls first: a panel that cannot see ACTB cannot be trusted about NR4A3
    def vals(g):
        return sorted(v["panel_tpm"].get(g, 0.0) for v in read.values())

    def med(xs):
        n = len(xs)
        return 0.0 if not n else (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2)

    res["instrument_controls"] = {
        "ACTB_median_TPM": round(med(vals("ACTB")), 2),
        "GAPDH_median_TPM": round(med(vals("GAPDH")), 2),
        "ALB_median_TPM": round(med(vals("ALB")), 4),
        "INS_median_TPM": round(med(vals("INS")), 4),
        "_pass_condition": ("housekeeping genes high in every sample AND the tissue-restricted "
                            "negatives near zero. Without both, a zero for NR4A3 is unreadable."),
    }
    hk_ok = med(vals("ACTB")) > 100 and med(vals("GAPDH")) > 100
    neg_ok = med(vals("ALB")) < 5 and med(vals("INS")) < 5
    res["instrument_controls"]["state"] = "PASS" if (hk_ok and neg_ok) else "FAIL"

    # ⭐ THE CONFOUND THAT DECIDES HOW MUCH THE RANKING IS WORTH, and it is MEASURED rather than
    #   assumed. TPM is normalised across whatever transcriptome the sample was quantified against,
    #   so a sample run on a different index is not on the same scale as the rest. The tell is the
    #   row count and the transcript-name convention, both of which are already in the cache.
    groups = {}
    for g, v in read.items():
        fmt = "REFSEQ_BARE" if any(str(n).startswith(("NM_", "NR_", "XM_", "XR_"))
                                   for n in v.get("first_names_verbatim") or []) else "OTHER"
        groups.setdefault((v["n_transcript_rows"], fmt), []).append(g)
    res["reference_index_groups"] = [
        {"n_transcript_rows": k[0], "name_convention": k[1], "n_samples": len(v),
         "example_names_verbatim": read[v[0]].get("first_names_verbatim"),
         "samples": v if len(v) <= 8 else v[:8] + ["…"]}
        for k, v in sorted(groups.items(), key=lambda kv: -len(kv[1]))]
    emc_group = next((k for k, v in groups.items() if emc and emc[0] in v), None)
    biggest = max(groups, key=lambda k: len(groups[k])) if groups else None
    res["emc_sample_shares_the_majority_index"] = (
        None if emc_group is None else emc_group == biggest)
    res["_index_confound_note"] = (
        "If the EMC-labelled sample was quantified against a DIFFERENT index from its comparators, "
        "a cross-sample TPM rank is not an apples-to-apples comparison and must not be reported as "
        "one. The within-sample NR4A family FRACTION below is the index-robust statistic: it is a "
        "ratio of three genes measured in the same file under the same normalisation.")

    ranked = sorted(((v["panel_tpm"].get("NR4A3", 0.0), g) for g, v in read.items()), reverse=True)
    res["NR4A3_TPM_ranking_top10"] = [
        {"rank": i + 1, "sample": g, "title": titles.get(g), "NR4A3_TPM": round(t, 3)}
        for i, (t, g) in enumerate(ranked[:10])]
    res["NR4A3_median_TPM_across_all_samples"] = round(med(vals("NR4A3")), 3)

    # index-robust statistic: NR4A3 as a fraction of the whole NR4A family, within each file
    def frac(g):
        p = read[g]["panel_tpm"]
        tot = sum(p.get(x, 0.0) for x in ("NR4A1", "NR4A2", "NR4A3"))
        return (p.get("NR4A3", 0.0) / tot) if tot > 0 else None

    fr = {g: frac(g) for g in read}
    fr_ranked = sorted(((v, g) for g, v in fr.items() if v is not None), reverse=True)
    res["NR4A3_family_fraction"] = {
        "_what": "NR4A3 / (NR4A1 + NR4A2 + NR4A3) TPM, within each sample's own file.",
        "_why": ("Index-robust. A cross-sample TPM rank is not, when the samples were quantified "
                 "against different transcriptomes — and here they were."),
        "median_across_all_samples": round(med(sorted(v for v in fr.values() if v is not None)), 4),
        "top5": [{"sample": g, "title": titles.get(g), "fraction": round(v, 4)}
                 for v, g in fr_ranked[:5]],
    }

    per_emc = []
    for g in emc:
        if g not in read:
            per_emc.append({"sample": g, "state": "CANNOT_DETERMINE — file not read"})
            continue
        t = read[g]["panel_tpm"].get("NR4A3", 0.0)
        rank = 1 + sum(1 for tt, _ in ranked if tt > t)
        f = fr.get(g)
        per_emc.append({
            "sample": g, "title": titles.get(g), "NR4A3_TPM": round(t, 3),
            "rank_of_%d" % len(ranked): rank,
            "n_samples_above_it": rank - 1,
            "_rank_bound": ("⚠ cross-sample TPM; see reference_index_groups"
                            if res["emc_sample_shares_the_majority_index"] is False
                            else "same index as the comparators"),
            "fold_over_panel_median": (round(t / med(vals("NR4A3")), 1)
                                       if med(vals("NR4A3")) > 0 else None),
            "NR4A1_TPM": round(read[g]["panel_tpm"].get("NR4A1", 0.0), 3),
            "NR4A2_TPM": round(read[g]["panel_tpm"].get("NR4A2", 0.0), 3),
            "NR4A3_family_fraction": None if f is None else round(f, 4),
            "family_fraction_rank_of_%d" % len(fr_ranked): (
                None if f is None else 1 + sum(1 for v, _ in fr_ranked if v > f)),
        })
    res["emc_labelled_samples"] = per_emc

    conf = res["emc_sample_shares_the_majority_index"] is False
    if res["instrument_controls"]["state"] != "PASS":
        res["verdict"] = "CANNOT_DETERMINE — the instrument controls did not pass"
    elif not per_emc:
        res["verdict"] = "NOT_APPLICABLE — no EMC-labelled sample in this series"
    elif per_emc[0].get("rank_of_%d" % len(ranked)) == 1 and not conf:
        res["verdict"] = "LABEL_CORROBORATED — the EMC-labelled sample is the panel's top NR4A3 expressor"
    elif (per_emc[0].get("n_samples_above_it") or 0) <= 3 and conf:
        res["verdict"] = ("LABEL_WEAKLY_CORROBORATED_AND_THE_COMPARISON_IS_CONFOUNDED — NR4A3 is "
                          "elevated but not dominant in the EMC-labelled sample, and that sample "
                          "was quantified against a different reference index from its 67 "
                          "comparators, so its cross-sample rank is not apples-to-apples")
    elif (per_emc[0].get("n_samples_above_it") or 0) <= 3:
        res["verdict"] = "LABEL_CORROBORATED_WEAKLY — near the top of the panel for NR4A3"
    else:
        res["verdict"] = "LABEL_NOT_CORROBORATED_BY_NR4A3_EXPRESSION"
    res["_sensitivity_bound"] = {
        "_headline": ("⚠ THIS TEST HAS LOW SENSITIVITY FOR THE QUESTION IT IS ASKED, BY "
                      "CONSTRUCTION — so a null here is much weaker evidence against the label "
                      "than a positive would have been for it, and it must not be read "
                      "symmetrically."),
        "the_index_has_no_fusion_entry": (
            "An EWSR1::NR4A3 transcript is EWSR1 exons 1-12 joined to NR4A3 exon 3. Quantified "
            "against a WILD-TYPE transcript index, reads spanning the junction map to neither "
            "entry cleanly and the EWSR1-derived 5' half never counts toward NR4A3 at all. The "
            "fusion's contribution to an NR4A3 TPM is therefore systematically UNDER-counted."),
        "the_family_is_immediate_early": (
            "NR4A1/2/3 are immediate-early genes driven by serum, stress and handling. 6 of the "
            "68 samples are cultured cells and 62 are tumour material, so both the absolute TPM "
            "and the family fraction carry a culture-versus-tissue confound on top of the index "
            "one."),
        "what_a_positive_would_have_meant": (
            "A conspicuous NR4A3 — top of the panel, dominating its own family — would have been "
            "real corroboration despite both confounds. That is not what was found."),
    }
    res["_what_would_settle_it"] = (
        "RT-PCR or targeted sequencing across the fusion junction, or a fusion caller run on the "
        "raw reads in SRA (BioProject PRJNA1273954). The first needs a bench; the second is real "
        "compute this document does not spend. Neither is an expression measurement, which is the "
        "point: expression can raise or lower a suspicion and can never close it.")
    return res


# =============================================================================================
# derive half — offline. Everything below runs from the inputs cache.
# =============================================================================================
def _parse_soft(txt):
    """SOFT -> {'series': {...}, 'platforms': {...}, 'samples': {gsm: {...}}}.

    Values are kept as LISTS because SOFT repeats a key per value (a sample has several
    `!Sample_characteristics_ch1` lines and dropping any of them is how metadata gets lost)."""
    out = {"series": {}, "platforms": {}, "samples": {}}
    cur = out["series"]
    for line in txt.splitlines():
        if line.startswith("^SAMPLE"):
            acc = line.split("=", 1)[1].strip()
            cur = out["samples"].setdefault(acc, {"_accession": acc})
            continue
        if line.startswith("^PLATFORM"):
            acc = line.split("=", 1)[1].strip()
            cur = out["platforms"].setdefault(acc, {"_accession": acc})
            continue
        if line.startswith("^SERIES"):
            cur = out["series"]
            continue
        if line.startswith("!") and "=" in line:
            k, v = line[1:].split("=", 1)
            cur.setdefault(k.strip(), []).append(v.strip())
    return out


def _sample_text(s):
    """Every free-text field of one sample, joined. The searchable body of that sample."""
    keys = [k for k in s
            if k != "_accession" and not k.startswith("Sample_supplementary_file")
            and not k.startswith("Sample_relation")]
    return " | ".join(f"{k}: {v}" for k in sorted(keys) for v in s[k])


# Term banks. Every one is a LITERAL to be found in submitter free text, and every hit is reported
# with the sample and field it came from — a count with no quotation is not evidence.
ATRI_TERMS = [
    "ceralasertib", "azd6738", "azd-6738", "berzosertib", "ve-822", "ve822", "vx-970", "m6620",
    "ve-821", "ve821", "elimusertib", "bay 1895344", "bay1895344", "bay-1895344", "m4344",
    "gartisertib", "m1774", "tuvusertib", "camonsertib", "rp-3500", "rp3500", "art0380",
    "atrn-119", "atri", "atr inhibitor", "atr inhibition", "atrx-inhibitor",
]
RESPONSE_TERMS = [
    "ic50", "gi50", "ec50", "viability", "cell titer", "celltiter", "dose", "dose-response",
    "dose response", "sensitivity", "resistant", "resistance", "survival fraction", "drug screen",
    "treated", "treatment", "vehicle", "dmso", "untreated", "control", "µm", "umol", "nm ",
]
EMC_TERMS = [
    "extraskeletal myxoid chondrosarcoma", "myxoid chondrosarcoma", "emc", "nr4a3", "nor-1",
    "nor1", "chn", "tec ", "csmf",
]
FET_TERMS = [
    "ewsr1", "ews-", "ews::", "fus", "taf15", "fli1", "erg", "atf1", "wt1", "ddit3", "chop",
    "creb3l2", "creb3l1", "nfatc2", "pbx1", "fusion", "translocation", "rearrange", "fet ",
]
HRD_TERMS = [
    "homologous recombination deficiency", "homologous recombination-deficient",
    "homologous recombination", "hrd", "hr-deficient", "hr deficient", "hr-proficient",
    "hr proficient", "brca1", "brca2", "brca", "palb2", "rad51", "rad51c", "rad51d", "bard1",
    "brip1", "atm", "hrdetect", "loh", "signature 3", "sbs3", "genomic instability", "parp",
]

_WORDY = re.compile(r"[a-z0-9]")


def _hits(text_by_sample, terms):
    """{term: [(gsm, snippet), ...]} — the SAMPLE and a verbatim window around the match."""
    found = {}
    for gsm, txt in sorted(text_by_sample.items()):
        low = txt.lower()
        for t in terms:
            i = low.find(t)
            if i < 0:
                continue
            # ⚠ Guard the short tokens. "emc" inside "chemical", "atm" inside "treatment",
            # "fus" inside "fusion", "hrd" inside "third" are the kind of hit that turns a scan
            # into a fabricator. Require non-word neighbours for tokens of 4 characters or fewer.
            if len(t.strip()) <= 4:
                before = low[i - 1] if i > 0 else " "
                after = low[i + len(t)] if i + len(t) < len(low) else " "
                if _WORDY.match(before) or _WORDY.match(after):
                    j, ok = i, False
                    while True:
                        j = low.find(t, j + 1)
                        if j < 0:
                            break
                        b = low[j - 1] if j > 0 else " "
                        a = low[j + len(t)] if j + len(t) < len(low) else " "
                        if not _WORDY.match(b) and not _WORDY.match(a):
                            i, ok = j, True
                            break
                    if not ok:
                        continue
            found.setdefault(t, []).append(
                (gsm, txt[max(0, i - 70): i + len(t) + 70].replace("\n", " ")))
    return found


def _flat(hitmap, limit=12):
    return [{"term": t, "sample": g, "verbatim": s}
            for t, hs in sorted(hitmap.items()) for g, s in hs[:limit]]


PROCESSED_SUFFIX_RE = re.compile(
    r"(quant\.sf|\.genes\.results|counts?|tpm|fpkm|rpkm|cpm|abundance|expression|matrix|deseq|"
    r"normali[sz]ed|processed|\.csv|\.tsv|\.xlsx?)", re.I)


def _processed_matrix_state(inp, per_sample_files):
    """Is processed expression data downloadable, or only raw reads?

    ⚠ THE EVIDENCE THAT COUNTS IS THE PER-SAMPLE SUPPLEMENTARY FILE, NOT THE SERIES MATRIX.
    GEO auto-generates a `*_series_matrix.txt.gz` for EVERY series, and for `Sample_type = SRA`
    series it routinely contains the sample METADATA with no value matrix at all — the values
    living in SRA as reads. Deriving "a processed matrix exists" from that file's existence would
    be reading a populated field as a measured one, which is the failure this repo polices. So the
    series-matrix listing is recorded as context and the STATE is derived from what the samples
    themselves carry."""
    ev = {}
    matrix = inp.get("ftp_matrix_listing")
    suppl = inp.get("ftp_suppl_listing")
    ev["matrix_listing_status"] = (inp.get("fetches", {}).get("ftp_matrix_listing") or {}).get("status")
    ev["suppl_listing_status"] = (inp.get("fetches", {}).get("ftp_suppl_listing") or {}).get("status")

    mfiles = sorted(set(re.findall(r"(GSE\d+[-_][^\"'<>\s]*?series_matrix\.txt\.gz)", matrix or "")))
    ev["series_matrix_files_listed"] = mfiles
    ev["_series_matrix_caveat"] = (
        "Listed for completeness only. A series_matrix is auto-generated for every GEO series and "
        "for an SRA-type series it is commonly metadata-only. It is NOT the evidence this state "
        "rests on.")
    sfiles = sorted(set(re.findall(r'href="([^"]+)"', suppl or "")))
    sfiles = [f for f in sfiles if f not in ("/", "..") and not f.startswith("/")]
    ev["series_supplementary_files"] = sfiles

    ev["n_samples_with_a_supplementary_file"] = sum(1 for v in per_sample_files.values() if v)
    ev["n_samples_total"] = len(per_sample_files)
    procs = {g: [f for f in v if PROCESSED_SUFFIX_RE.search(f)] for g, v in per_sample_files.items()}
    n_proc = sum(1 for v in procs.values() if v)
    ev["n_samples_with_a_PROCESSED_looking_supplementary_file"] = n_proc
    ev["example_per_sample_files"] = [v[0] for v in list(per_sample_files.values())[:3] if v]

    # A positive is a positive whatever else failed to load.
    if per_sample_files and n_proc == len(per_sample_files) and n_proc > 0:
        return "PER_SAMPLE_PROCESSED_QUANTIFICATION_FOR_EVERY_SAMPLE", ev
    if n_proc:
        return "PER_SAMPLE_PROCESSED_QUANTIFICATION_FOR_SOME_SAMPLES", ev
    if any(PROCESSED_SUFFIX_RE.search(f) for f in sfiles):
        return "SERIES_LEVEL_PROCESSED_SUPPLEMENT_ONLY", ev
    # ⚠ Only NOW may a negative be returned — and only if BOTH halves were actually readable.
    # A listing that 404'd or timed out leaves the series-level half unread, and reporting that as
    # "raw reads only" would be a reading of absence built out of an absent reading (CLAUDE.md §4).
    if matrix is None or suppl is None:
        return "CANNOT_DETERMINE", dict(
            ev, why=("no per-sample processed file was found, but at least one FTP listing was not "
                     "readable, so the series-level half of the question was never asked"))
    if not per_sample_files:
        return "CANNOT_DETERMINE", dict(ev, why="no sample records were readable")
    return "NO_PROCESSED_DATA_FOUND_RAW_READS_ONLY", ev


def derive(inp, quant=None):
    series = inp.get("series", SERIES)
    soft_txt = inp.get("soft_all_brief") or inp.get("soft_family_gz")
    res = {
        "_what": (
            f"Sample-level characterisation of GEO series {series}, and the three questions it was "
            "read to answer for the EMC ATR route."
        ),
        "_discipline": (
            "A GEO series TITLE is a claim by its depositors, not a measurement. Every verdict here "
            "is computed from per-sample metadata and every hit is reported with the sample and the "
            "verbatim text it came from. A field that could not be READ is CANNOT_DETERMINE, never "
            "false — an absent reading is not a reading of absence (CLAUDE.md §4)."
        ),
        "_no_clinical_claim": (
            "No efficacy, potency, dose, safety, therapeutic-window or clinical-readiness claim is "
            "made or implied. This is a metadata characterisation of a public deposit."
        ),
        "series": series,
        "fetched_utc": inp.get("fetched_utc"),
        "fetch_status": {k: v.get("status") for k, v in sorted((inp.get("fetches") or {}).items())},
    }

    if not soft_txt:
        res["readable"] = False
        res["verdict"] = "SERIES_METADATA_NOT_READABLE"
        res["why"] = ("Neither acc.cgi nor the FTP family SOFT returned a document, so NOTHING about "
                      "this series' samples was read. This is an instrument failure and carries no "
                      "information about the series' contents.")
        for q in ("q1_atr_inhibitor_response_data", "q2_emc_or_nr4a3_sample",
                  "q3_selection_biomarker"):
            res[q] = {"answer": "CANNOT_DETERMINE", "why": "series metadata never arrived"}
        return res

    soft = _parse_soft(soft_txt)
    res["readable"] = True

    # ---- series-level record, quoted rather than paraphrased ----------------------------------
    sr = soft["series"]
    res["series_record"] = {
        "title": (sr.get("Series_title") or [None])[0],
        "summary": " ".join(sr.get("Series_summary") or []),
        "overall_design": " ".join(sr.get("Series_overall_design") or []),
        "type": sr.get("Series_type") or [],
        "submission_date": (sr.get("Series_submission_date") or [None])[0],
        "last_update_date": (sr.get("Series_last_update_date") or [None])[0],
        "contributors": sr.get("Series_contributor") or [],
        "contact_institute": sr.get("Series_contact_institute") or [],
        "platforms": sr.get("Series_platform_id") or [],
        "pubmed_ids": inp.get("series_pmids") or [],
        "relations": sr.get("Series_relation") or [],
        "n_sample_ids_listed": len(sr.get("Series_sample_id") or []),
    }
    res["platform_records"] = {
        p: {"title": (d.get("Platform_title") or [None])[0],
            "technology": (d.get("Platform_technology") or [None])[0],
            "organism": d.get("Platform_organism") or []}
        for p, d in sorted(soft["platforms"].items())
    }

    # ---- sample-level ------------------------------------------------------------------------
    samples = soft["samples"]
    text_by_sample = {g: _sample_text(s) for g, s in samples.items()}
    res["n_samples_parsed"] = len(samples)

    def _one(g, s):
        return {
            "accession": g,
            "title": (s.get("Sample_title") or [None])[0],
            "source_name": s.get("Sample_source_name_ch1") or [],
            "organism": s.get("Sample_organism_ch1") or [],
            "characteristics": s.get("Sample_characteristics_ch1") or [],
            "treatment_protocol": s.get("Sample_treatment_protocol_ch1") or [],
            "growth_protocol": s.get("Sample_growth_protocol_ch1") or [],
            "description": s.get("Sample_description") or [],
            "type": s.get("Sample_type") or [],
            "library_strategy": s.get("Sample_library_strategy") or [],
            "library_source": s.get("Sample_library_source") or [],
            "library_selection": s.get("Sample_library_selection") or [],
            "molecule": s.get("Sample_molecule_ch1") or [],
            "platform": s.get("Sample_platform_id") or [],
            "supplementary_files": [v for k in sorted(s)
                                    if k.startswith("Sample_supplementary_file")
                                    for v in s[k]],
        }

    res["samples"] = [_one(g, s) for g, s in sorted(samples.items())]
    per_sample_files = {r["accession"]: r["supplementary_files"] for r in res["samples"]}

    # ---- WHAT THE SAMPLES ACTUALLY ARE --------------------------------------------------------
    # ⭑ The load-bearing split, and it is structural rather than keyword-based: GEO characteristics
    #   carry `tissue: <subtype>` for a tumour and `tissue: cells` + `cell type: <subtype>` for a
    #   patient-derived cell model. Read from that pair, not from the series' overall_design —
    #   which on this series names only part of what the series contains.
    cohort = {"tumour_samples": {}, "patient_derived_cell_models": {}, "unclassified": []}
    for rec in res["samples"]:
        ch = {c.split(":", 1)[0].strip().lower(): c.split(":", 1)[1].strip()
              for c in rec["characteristics"] if ":" in c}
        tissue, ctype = ch.get("tissue"), ch.get("cell type")
        if tissue and tissue.lower() == "cells" and ctype:
            cohort["patient_derived_cell_models"].setdefault(ctype.lower(), []).append(
                {"accession": rec["accession"], "title": rec["title"]})
        elif tissue:
            cohort["tumour_samples"].setdefault(tissue.lower(), []).append(
                {"accession": rec["accession"], "title": rec["title"]})
        else:
            cohort["unclassified"].append(rec["accession"])
    res["cohort_composition"] = {
        "n_tumour_samples": sum(len(v) for v in cohort["tumour_samples"].values()),
        "n_patient_derived_cell_models": sum(
            len(v) for v in cohort["patient_derived_cell_models"].values()),
        "n_unclassified": len(cohort["unclassified"]),
        "tumour_subtypes": {k: len(v) for k, v in sorted(cohort["tumour_samples"].items())},
        "cell_model_subtypes": {k: len(v) for k, v in
                                sorted(cohort["patient_derived_cell_models"].items())},
        "members": cohort,
        "_how": ("From each sample's own `tissue:` / `cell type:` characteristics. The series' "
                 "overall_design is NOT used for this — see `design_vs_contents` below."),
    }
    design = res["series_record"]["overall_design"]
    res["design_vs_contents"] = {
        "overall_design_verbatim": design,
        "n_samples_the_design_accounts_for": sum(
            int(n) for n in re.findall(r"(\d+)\s+[a-z]", design.lower())) if design else None,
        "n_samples_actually_in_the_series": len(samples),
        "_why_this_field_exists": (
            "A GEO series title and design are claims by its depositors, not measurements. This "
            "repo has been bitten twice by reading one as the other, so the arithmetic is done "
            "rather than trusted."),
    }

    # FET-fusion sarcoma subtypes — present or absent, because the biomarker question in Q3 turns
    # on WHICH sarcomas a programme selected, not only on which biomarker it named.
    fet_disease_terms = {
        "ewing": "Ewing sarcoma (EWSR1::FLI1/ERG)",
        "clear cell sarcoma": "clear cell sarcoma (EWSR1::ATF1)",
        "desmoplastic small round cell": "DSRCT (EWSR1::WT1)",
        "myxoid liposarcoma": "myxoid liposarcoma (FUS/EWSR1::DDIT3)",
        "myxoid chondrosarcoma": "extraskeletal myxoid chondrosarcoma (EWSR1/TAF15/FUS::NR4A3)",
        "fibromyxoid": "low-grade fibromyxoid sarcoma (FUS::CREB3L2)",
        "angiomatoid fibrous histiocytoma": "AFH (EWSR1::CREB1/ATF1)",
        "sclerosing epithelioid fibrosarcoma": "SEF (EWSR1/FUS::CREB3L1)",
    }
    all_sub = {k: v for k, v in list(res["cohort_composition"]["tumour_subtypes"].items())
               + list(res["cohort_composition"]["cell_model_subtypes"].items())}
    present, absent = {}, []
    for frag, label in sorted(fet_disease_terms.items()):
        hit = {s: n for s, n in all_sub.items() if frag in s or frag in s.replace("skelletal", "skeletal")}
        if hit:
            present[label] = hit
        else:
            absent.append(label)
    res["fet_fusion_sarcoma_subtypes"] = {
        "present_in_this_cohort": present,
        "absent_from_this_cohort": absent,
        "_bound": ("Presence of a DISEASE whose defining fusion is a FET fusion. It is not a "
                   "per-sample fusion call, and this series carries none — see "
                   "`fet_fusion_status_recoverable`."),
    }

    # tumour vs cell line, from the submitter's own words rather than from the title
    def _material(rec):
        t = " ".join(str(x) for x in
                     (rec["source_name"] + rec["characteristics"] + rec["growth_protocol"]
                      + rec["description"] + [rec["title"] or ""])).lower()
        cell = any(k in t for k in ("cell line", "cell-line", "cells", "culture", "passage",
                                    "dmem", "rpmi", "fbs", "in vitro"))
        tumour = any(k in t for k in ("tumor", "tumour", "patient", "biopsy", "resect", "ffpe",
                                      "specimen", "primary tissue", "pdx", "xenograft"))
        if cell and not tumour:
            return "cell_line_or_culture"
        if tumour and not cell:
            return "tumour_or_patient_material"
        if cell and tumour:
            return "ambiguous_both_words_present"
        return "not_stated"

    mats = {}
    for rec in res["samples"]:
        mats.setdefault(_material(rec), []).append(rec["accession"])
    res["material_type_counts"] = {k: len(v) for k, v in sorted(mats.items())}
    res["material_type_members"] = {k: v for k, v in sorted(mats.items())}

    res["assay_types"] = {}
    for rec in res["samples"]:
        key = "/".join(rec["type"] + rec["library_strategy"]) or "unstated"
        res["assay_types"][key] = res["assay_types"].get(key, 0) + 1

    # ---- processed matrix? --------------------------------------------------------------------
    state, ev = _processed_matrix_state(inp, per_sample_files)
    res["processed_matrix"] = {"state": state, "evidence": ev}

    # ---- the three questions ------------------------------------------------------------------
    atri = _hits(text_by_sample, ATRI_TERMS)
    resp = _hits(text_by_sample, RESPONSE_TERMS)
    emc = _hits(text_by_sample, EMC_TERMS)
    fet = _hits(text_by_sample, FET_TERMS)
    hrd = _hits(text_by_sample, HRD_TERMS)

    series_blob = " ".join([res["series_record"]["title"] or "",
                            res["series_record"]["summary"],
                            res["series_record"]["overall_design"]])
    series_hits = {
        "atri": _flat(_hits({"_SERIES_": series_blob}, ATRI_TERMS)),
        "emc": _flat(_hits({"_SERIES_": series_blob}, EMC_TERMS)),
        "fet": _flat(_hits({"_SERIES_": series_blob}, FET_TERMS)),
        "hrd": _flat(_hits({"_SERIES_": series_blob}, HRD_TERMS)),
    }
    res["series_level_term_hits"] = series_hits

    # Q1 — ATR-inhibitor RESPONSE data
    atri_samples = sorted({g for hs in atri.values() for g, _ in hs})
    resp_samples = sorted({g for hs in resp.values() for g, _ in hs})
    both = sorted(set(atri_samples) & set(resp_samples))
    if atri_samples and both:
        q1 = ("ATR_INHIBITOR_TREATMENT_ANNOTATED_AT_SAMPLE_LEVEL"
              if len(both) >= 2 else "SINGLE_SAMPLE_ONLY")
    elif atri_samples:
        q1 = "ATR_INHIBITOR_NAMED_BUT_NO_RESPONSE_OR_TREATMENT_ANNOTATION"
    elif series_hits["atri"]:
        q1 = "ATR_NAMED_ONLY_AT_SERIES_LEVEL_NOT_PER_SAMPLE"
    else:
        q1 = "NO_ATR_INHIBITOR_ANNOTATION_IN_SAMPLE_METADATA"
    n_treat_field = sum(1 for r in res["samples"] if r["treatment_protocol"])
    res["q1_atr_inhibitor_response_data"] = {
        "answer": q1,
        "n_samples_naming_an_ATR_inhibitor_or_ATRi": len(atri_samples),
        "samples_naming_an_ATR_inhibitor": atri_samples,
        "n_samples_with_a_treatment_or_response_word_ANYWHERE": len(resp_samples),
        "n_samples_with_a_NON_EMPTY_treatment_protocol_field": n_treat_field,
        "_why_those_two_numbers_differ": (
            "⚠ The first is a keyword count over ALL free text and is dominated by boilerplate — "
            "on GSE299349 the shared growth protocol says 'cell culture-treated flasks', so the "
            "word 'treated' appears on every sample including the untreated tumours. The count "
            "that means what a reader would assume is the second one: how many samples carry a "
            "populated `!Sample_treatment_protocol_ch1`. A populated field is not a measured one, "
            "and a keyword count is not a populated field."),
        "hits_verbatim": _flat(atri),
        "_bound": ("A viability or IC50 READOUT is a different object from a treated RNA sample. "
                   "This field says what the sample metadata names; it does not assert that a "
                   "dose-response measurement is deposited."),
    }

    # Q2 — EMC / NR4A3
    emc_samples = sorted({g for hs in emc.values() for g, _ in hs})
    strong = sorted({g for t in ("extraskeletal myxoid chondrosarcoma", "myxoid chondrosarcoma",
                                 "nr4a3", "nor-1", "nor1")
                     for g, _ in emc.get(t, [])})
    res["q2_emc_or_nr4a3_sample"] = {
        "answer": ("EMC_OR_NR4A3_SAMPLE_PRESENT" if strong else
                   "WEAK_TOKEN_ONLY" if emc_samples else "NO_EMC_OR_NR4A3_SAMPLE"),
        "samples_with_a_strong_EMC_or_NR4A3_term": strong,
        "samples_with_any_EMC_token": emc_samples,
        "hits_verbatim": _flat(emc),
    }

    # FET-fusion status recoverable?
    fet_samples = sorted({g for hs in fet.values() for g, _ in hs})
    res["fet_fusion_status_recoverable"] = {
        "answer": ("FUSION_TERMS_PRESENT_IN_SAMPLE_METADATA" if fet_samples
                   else "NO_FUSION_TERM_IN_ANY_SAMPLE"),
        "n_samples": len(fet_samples),
        "samples": fet_samples,
        "hits_verbatim": _flat(fet),
        "_bound": ("A gene name in a sample's free text is not a per-sample fusion CALL. Whether "
                   "FET status is recoverable for an ANALYSIS depends on a per-sample annotation, "
                   "which this field reports the presence of and nothing more."),
    }

    # Q3 — HRD vs FET as the selection biomarker
    hrd_samples = sorted({g for hs in hrd.values() for g, _ in hs})
    hrd_series = bool(series_hits["hrd"])
    fet_series = bool(series_hits["fet"])
    if hrd_series and not fet_series:
        q3 = "SELECTS_ON_HRD_NOT_ON_FET_FUSION_STATUS"
    elif hrd_series and fet_series:
        q3 = "BOTH_BIOMARKERS_NAMED"
    elif fet_series and not hrd_series:
        q3 = "SELECTS_ON_FET_FUSION_STATUS"
    else:
        q3 = "NEITHER_BIOMARKER_NAMED_AT_SERIES_LEVEL"
    res["q3_selection_biomarker"] = {
        "answer": q3,
        "n_samples_with_an_HRD_term": len(hrd_samples),
        "samples_with_an_HRD_term": hrd_samples,
        "sample_level_hits_verbatim": _flat(hrd),
        "series_level_hits_verbatim": series_hits["hrd"],
        "_why_this_matters": (
            "Route 1 rests on PMID 37205599, which nominates FET-fusion-driven ATM SUPPRESSION as "
            "the lesion and is not an HR-deficiency argument. A sarcoma ATR programme selecting on "
            "HRD is either a competing biomarker hypothesis or a different patient population."
        ),
    }

    # ---- the publication, if any --------------------------------------------------------------
    pubs = []
    for p in inp.get("series_pmids") or []:
        raw = inp.get(f"europepmc_{p}")
        if not raw:
            pubs.append({"pmid": p, "record": "CANNOT_DETERMINE — Europe PMC record not fetched"})
            continue
        try:
            hit = (json.loads(raw).get("resultList", {}).get("result") or [{}])[0]
        except Exception as e:      # noqa: BLE001
            pubs.append({"pmid": p, "record": f"parse error {type(e).__name__}: {e}"})
            continue
        pubs.append({"pmid": p, "doi": hit.get("doi"), "title": hit.get("title"),
                     "journal": (hit.get("journalInfo") or {}).get("journal", {}).get("title"),
                     "year": hit.get("pubYear"), "authors": hit.get("authorString"),
                     "abstract": hit.get("abstractText")})
    res["associated_publication"] = {
        "pmids_declared_by_the_series": inp.get("series_pmids") or [],
        "records": pubs,
    }
    acc_search = inp.get("europepmc_accession_search")
    if acc_search:
        try:
            hits = json.loads(acc_search).get("resultList", {}).get("result") or []
            res["associated_publication"]["europepmc_papers_citing_the_accession"] = [
                {"pmid": h.get("pmid"), "doi": h.get("doi"), "title": h.get("title"),
                 "year": h.get("pubYear"), "journal": (h.get("journalInfo") or {})
                 .get("journal", {}).get("title")}
                for h in hits[:15]
            ]
        except Exception as e:      # noqa: BLE001
            res["associated_publication"]["europepmc_accession_search"] = f"parse error: {e}"
    else:
        res["associated_publication"]["europepmc_papers_citing_the_accession"] = (
            "CANNOT_DETERMINE — the accession search did not return")

    # ⭑ A series with no declared PMID is not a series with no paper. Three further searches, and
    #   their RECORD is the deliverable when the answer is "none found".
    searches = {}
    for name, q in sorted((inp.get("publication_queries") or {}).items()):
        raw = inp.get(f"europepmc_pub_{name}")
        if raw is None:
            searches[name] = {"query": q, "result": "CANNOT_DETERMINE — the query did not return"}
            continue
        try:
            hits = json.loads(raw).get("resultList", {}).get("result") or []
        except Exception as e:      # noqa: BLE001
            searches[name] = {"query": q, "result": f"parse error: {type(e).__name__}: {e}"}
            continue
        searches[name] = {
            "query": q, "n_hits": len(hits),
            "hits": [{"pmid": h.get("pmid"), "doi": h.get("doi"), "title": h.get("title"),
                      "year": h.get("pubYear"), "authors": h.get("authorString"),
                      "journal": (h.get("journalInfo") or {}).get("journal", {}).get("title")}
                     for h in hits[:10]],
        }
    res["associated_publication"]["further_searches"] = searches
    named = bool(inp.get("series_pmids")) or any(
        s.get("n_hits") for s in searches.values() if isinstance(s, dict))
    res["associated_publication"]["state"] = (
        "PMID_DECLARED_BY_THE_SERIES" if inp.get("series_pmids") else
        "NO_PMID_DECLARED_CANDIDATES_FOUND_BY_SEARCH" if named else
        "NO_PMID_DECLARED_AND_NO_CANDIDATE_FOUND")
    res["associated_publication"]["_bound"] = (
        "A search that returns nothing is a search, not a proof that no paper exists. The queries "
        "are recorded verbatim so the next look starts from what was already asked.")

    # What the candidate publication itself says — quoted, for the two facts the metadata cannot
    # settle: whether the EMC model was in the drug-tested panel, and what SARC-HRD is.
    cands = {}
    for p in inp.get("candidate_publication_pmids") or []:
        rec = {"pmid": p}
        xml = inp.get(f"candidate_fulltext_{p}")
        if not xml:
            rec["fulltext"] = ("CANNOT_DETERMINE — no open-access full text was retrievable; only "
                               "the search record above was read")
        else:
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))
            rec["fulltext_chars"] = len(text)
            for label, rx in (
                ("sentences_naming_the_EMC_model",
                 r"[^.]*?\b(EMC[0-9]?|myxoid chondrosarcoma|NR4A3)\b[^.]*\."),
                ("sentences_defining_SARC_HRD", r"[^.]*?\bSARC-HRD\b[^.]*\."),
                ("sentences_naming_an_ATR_inhibitor",
                 r"[^.]*?\b(ceralasertib|AZD6738|berzosertib|VE-822|elimusertib|BAY ?1895344|"
                 r"M4344|gartisertib|M1774|camonsertib|RP-3500|ATRi)\b[^.]*\."),
            ):
                seen, uniq = set(), []
                for m in re.finditer(rx, text, re.I):
                    s = m.group(0).strip()
                    k = s.lower()[:110]
                    if k not in seen:
                        seen.add(k)
                        uniq.append(s)
                rec[label] = uniq[:25]
        cands[p] = rec
    res["associated_publication"]["candidate_publication_read"] = cands

    # ---- the mechanism paper's own words about HR deficiency (Q3's comparison) -----------------
    res["mechanism_paper_on_hr_deficiency"] = _mechanism_hr_stance(inp)

    # ---- is the EMC LABEL corroborated? --------------------------------------------------------
    if quant:
        res["emc_model_identity_check"] = derive_quant(quant, res)
    else:
        res["emc_model_identity_check"] = {
            "state": "NOT_RUN",
            "_why": ("The per-sample quantifications were not fetched. This is an ABSENT READING "
                     "and says nothing about the model's identity — run `--fetch-quant` in CI."),
        }

    # ---- one overall verdict, DERIVED from the answers above, never typed ----------------------
    usable = res["processed_matrix"]["state"].startswith("PER_SAMPLE_PROCESSED")
    res["verdict"] = "READ_AND_CHARACTERISED"
    res["usable_for_a_reanalysis_here"] = {
        "state": "PROCESSED_EXPRESSION_DOWNLOADABLE" if usable
                 else res["processed_matrix"]["state"],
        "_bound": ("Usable means processed expression can be downloaded without aligning FASTQ. It "
                   "does NOT mean the data answers any of the three questions — a transcriptome "
                   "cannot supply a drug-response readout that was never deposited, and it cannot "
                   "supply a fusion call the submitter did not make."),
        "_what_a_reanalysis_here_could_and_could_not_do": {
            "could": ("score the EMC cell model's DDR/replication-stress transcripts against 62 "
                      "sarcoma tumours and 5 non-EMC cell models, with proliferation subtracted — "
                      "the same read part B performs, on a third instrument"),
            "could_not": ("re-cut ATR-inhibitor sensitivity by FET status, because no sensitivity "
                          "readout is deposited here; or confirm any sample's fusion, because no "
                          "per-sample fusion call is deposited here"),
            "_n_bound": ("n = 1 for EMC. A single cell model against a 67-sample comparator is a "
                         "position on a distribution, not a group contrast, and no p-value over "
                         "n = 1 would mean what a reader would take it to mean."),
        },
    }
    return res


HR_SENTENCE_RE = re.compile(
    r"[^.]*?\b(homologous recombination|HR[- ]deficien|HR[- ]proficien|BRCA|BRCAness|"
    r"HRD\b|PARP)[^.]*\.", re.I)


def _mechanism_hr_stance(inp):
    """Verbatim sentences from PMID 37205599 that mention HR/BRCA/PARP. Quoted, never summarised —
    Q3 turns on what that paper actually claims, and a paraphrase of a paraphrase is how a framing
    drifts."""
    out = {"pmid": MECHANISM_PMID,
           "_role": "route 1's mechanism source; fetched to compare biomarker framings, not re-graded here"}
    raw = inp.get(f"europepmc_{MECHANISM_PMID}")
    if raw:
        try:
            hit = (json.loads(raw).get("resultList", {}).get("result") or [{}])[0]
            out["title"] = hit.get("title")
            out["doi"] = hit.get("doi")
            out["journal"] = (hit.get("journalInfo") or {}).get("journal", {}).get("title")
            out["year"] = hit.get("pubYear")
            abstract = hit.get("abstractText") or ""
            out["abstract_sentences_mentioning_HR_or_BRCA_or_PARP"] = [
                m.group(0).strip() for m in HR_SENTENCE_RE.finditer(abstract)]
        except Exception as e:      # noqa: BLE001
            out["record"] = f"parse error {type(e).__name__}: {e}"
    else:
        out["record"] = "CANNOT_DETERMINE — Europe PMC record for the mechanism paper not fetched"

    xml = inp.get("mechanism_fulltext_xml")
    if xml:
        text = re.sub(r"<[^>]+>", " ", xml)
        text = re.sub(r"\s+", " ", text)
        sents = [m.group(0).strip() for m in HR_SENTENCE_RE.finditer(text)]
        seen, uniq = set(), []
        for s in sents:
            k = s.lower()[:120]
            if k not in seen:
                seen.add(k)
                uniq.append(s)
        out["fulltext_pmcid"] = inp.get("mechanism_pmcid")
        out["fulltext_sentences_mentioning_HR_or_BRCA_or_PARP"] = uniq[:40]
        out["n_such_sentences"] = len(uniq)
    else:
        out["fulltext"] = ("CANNOT_DETERMINE — no open-access full text was fetched; the abstract "
                           "sentences above are all that was read")
    return out


# =============================================================================================
def _load_quant():
    if os.path.exists(QUANT_INPUTS):
        with open(QUANT_INPUTS) as f:
            return json.load(f)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch", action="store_true",
                    help="network pass (CI only: the dev sandbox's proxy 403s NCBI)")
    ap.add_argument("--fetch-quant", action="store_true",
                    help="network pass over every sample's quant.sf (CI only). Needs --fetch first")
    ap.add_argument("--check", action="store_true",
                    help="offline: re-derive from the inputs cache and diff against the artifact")
    ap.add_argument("--series", default=SERIES)
    args = ap.parse_args()

    if args.fetch_quant:
        if not os.path.exists(ART):
            print("no artifact yet — run --fetch first", file=sys.stderr)
            return 2
        q = fetch_quant()
        with open(QUANT_INPUTS, "w") as f:
            json.dump(q, f, indent=1, sort_keys=True)
        with open(INPUTS) as f:
            inp = json.load(f)
        res = derive(inp, q)
        with open(ART, "w") as f:
            json.dump(res, f, indent=1, sort_keys=True)
        print(json.dumps(res["emc_model_identity_check"], indent=1)[:2500])
        return 0

    if args.fetch:
        inp = fetch(args.series)
        with open(INPUTS, "w") as f:
            json.dump(inp, f, indent=1, sort_keys=True)
        res = derive(inp, _load_quant())
        with open(ART, "w") as f:
            json.dump(res, f, indent=1, sort_keys=True)
        print(json.dumps({k: res.get(k) for k in
                          ("verdict", "readable", "n_samples_parsed", "material_type_counts",
                           "assay_types")}, indent=1))
        for q in ("q1_atr_inhibitor_response_data", "q2_emc_or_nr4a3_sample",
                  "q3_selection_biomarker", "fet_fusion_status_recoverable"):
            if q in res:
                print(q, "->", res[q]["answer"])
        print("processed_matrix ->", (res.get("processed_matrix") or {}).get("state"))
        return 0

    if not os.path.exists(INPUTS):
        print(f"no inputs cache at {INPUTS} — run --fetch in CI first", file=sys.stderr)
        return 2
    with open(INPUTS) as f:
        inp = json.load(f)
    fresh = derive(inp, _load_quant())
    if not os.path.exists(ART):
        with open(ART, "w") as f:
            json.dump(fresh, f, indent=1, sort_keys=True)
        print("artifact written from the cache")
        return 0
    with open(ART) as f:
        committed = json.load(f)
    a = json.dumps(fresh, indent=1, sort_keys=True)
    b = json.dumps(committed, indent=1, sort_keys=True)
    if a == b:
        print("OK — the artifact re-derives byte-identically from the committed inputs cache")
        return 0
    print("DRIFT — the derive half no longer reproduces the committed artifact", file=sys.stderr)
    for k in sorted(set(fresh) | set(committed)):
        if json.dumps(fresh.get(k), sort_keys=True) != json.dumps(committed.get(k), sort_keys=True):
            print("  differs:", k, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
