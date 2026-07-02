#!/usr/bin/env python3
"""
NR4A3-degrader SAFETY evidence (H1) from human/mouse genetics databases — the gap DepMap can't fill.

WHY. DepMap tells us whether the NR4A family is essential in *dividing cancer lines*. It is blind to
the real on-target risk for a nuclear-receptor degrader: tolerability in POST-MITOTIC / tissue-specific
contexts (classically NR4A2/Nurr1 in dopaminergic neurons). This script pulls three orthogonal,
no-wet-lab database sources that DO speak to in-vivo tolerability of losing a single NR4A paralogue:

  1. gnomAD LoF constraint (LOEUF / pLI) — is NR4A3 loss-of-function TOLERATED in the human population?
     LOEUF is the upper bound of the observed/expected LoF ratio. Low LOEUF (< ~0.35) or high pLI
     (> 0.9) => LoF-INTOLERANT (losing the gene is selected against). High LOEUF / low pLI =>
     LoF-tolerant => direct human-genetic support that heterozygous NR4A3 loss is benign.
  2. IMPC single-gene knockout viability + phenotypes — is the mouse Nr4a3 single-KO viable/healthy?
     Resolves the exact "which single KO is NOT tolerated" question (the Nurr1 neonatal-lethal issue)
     with a standardized, modern in-vivo source instead of an assumption.
  3. Human Protein Atlas RNA tissue expression — WHERE are NR4A1/2/3 co-expressed (paralogue
     compensation available) vs where NR4A3 is expressed without its paralogues (candidate risk tissue)?

MEDICAL INTEGRITY. Every value is pulled live and tagged with its source + query date-independent
provenance. Where a database has NO record for a gene, we write an explicit "_status":"no record"
rather than inventing a value. Nothing here is fabricated; unverifiable items are flagged, not guessed.

Output: nr4a-safety-genetics.json. Internet required -> runs in CI (GitHub Actions has open egress).
"""

import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a-safety-genetics.json")

# Ensembl gene IDs (GRCh38) for the three paralogues.
ENSEMBL = {"NR4A1": "ENSG00000123358", "NR4A2": "ENSG00000153234", "NR4A3": "ENSG00000119508"}
MOUSE_SYMBOL = {"NR4A1": "Nr4a1", "NR4A2": "Nr4a2", "NR4A3": "Nr4a3"}
GENES = ["NR4A1", "NR4A2", "NR4A3"]

# gnomAD constraint interpretation thresholds (gnomAD documentation).
LOEUF_INTOLERANT = 0.35    # < this => LoF-intolerant (constrained)
PLI_INTOLERANT = 0.9       # > this => LoF-intolerant


def _post_json(url, payload, timeout=60, headers=None):
    h = {"User-Agent": "rare-cancers/1.0", "Content-Type": "application/json",
         "Accept": "application/json"}
    if headers:
        h.update(headers)
    body = json.dumps(payload).encode()
    for i in range(4):
        try:
            req = urllib.request.Request(url, data=body, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i+1} POST {url[:60]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return None


def _get_json(url, timeout=60, headers=None):
    h = {"User-Agent": "rare-cancers/1.0", "Accept": "application/json"}
    if headers:
        h.update(headers)
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i+1} GET {url[:70]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return None


# ---------------------------------------------------------------------------------------------------
# 1. gnomAD loss-of-function constraint (LOEUF / pLI) via the public GraphQL API.
# ---------------------------------------------------------------------------------------------------
GNOMAD_API = "https://gnomad.broadinstitute.org/api"
GNOMAD_QUERY = """
query Constraint($symbol: String!) {
  gene(gene_symbol: $symbol, reference_genome: GRCh38) {
    gene_id
    symbol
    gnomad_constraint {
      pli
      oe_lof
      oe_lof_lower
      oe_lof_upper
      oe_mis
      mis_z
      lof_z
      exp_lof
      obs_lof
    }
  }
}
"""


def gnomad_constraint():
    out = {}
    for g in GENES:
        data = _post_json(GNOMAD_API, {"query": GNOMAD_QUERY, "variables": {"symbol": g}})
        rec = (((data or {}).get("data") or {}).get("gene") or {}) if data else {}
        con = rec.get("gnomad_constraint") if rec else None
        if not con:
            out[g] = {"_status": "no gnomAD constraint record"}
            continue
        loeuf = con.get("oe_lof_upper")
        pli = con.get("pli")
        out[g] = {
            "pli": pli,
            "loeuf": loeuf,                       # oe_lof_upper = LOEUF
            "oe_lof": con.get("oe_lof"),
            "obs_lof": con.get("obs_lof"),
            "exp_lof": con.get("exp_lof"),
            "mis_z": con.get("mis_z"),
            "lof_z": con.get("lof_z"),
            "lof_intolerant": bool(
                (loeuf is not None and loeuf < LOEUF_INTOLERANT)
                or (pli is not None and pli > PLI_INTOLERANT)),
            "interpretation": (
                "LoF-intolerant (constrained)"
                if ((loeuf is not None and loeuf < LOEUF_INTOLERANT)
                    or (pli is not None and pli > PLI_INTOLERANT))
                else "LoF-tolerant"),
        }
    return {
        "_note": "gnomAD v-latest GraphQL constraint. LOEUF (oe_lof_upper): < 0.35 => LoF-intolerant; "
                 "higher => LoF-tolerant. pLI: > 0.9 => intolerant. LoF-TOLERANT for NR4A3 is direct "
                 "human-genetic support that losing one allele/gene is not strongly selected against. "
                 "Caveat: population constraint reflects reproductive fitness, not adult drug "
                 "tolerability — a supporting datum, not proof.",
        "source": "gnomAD (gnomad.broadinstitute.org GraphQL API)",
        "thresholds": {"loeuf_intolerant_below": LOEUF_INTOLERANT, "pli_intolerant_above": PLI_INTOLERANT},
        "genes": out,
    }


# ---------------------------------------------------------------------------------------------------
# 2. IMPC single-KO viability + phenotypes via the public solr API.
# ---------------------------------------------------------------------------------------------------
IMPC_GP = ("https://www.ebi.ac.uk/mi/impc/solr/genotype-phenotype/select"
           "?q=marker_symbol:{sym}&rows=500&wt=json"
           "&fl=mp_term_name,top_level_mp_term_name,zygosity,parameter_name,p_value")
IMPC_VIA = ("https://www.ebi.ac.uk/mi/impc/solr/experiment/select"
            "?q=marker_symbol:{sym}+AND+parameter_name:*iability*&rows=50&wt=json"
            "&fl=parameter_name,category,zygosity")


def _lethal_flag(terms):
    joined = " ; ".join(terms).lower()
    if "lethal" in joined:
        return "lethal-phenotype-reported"
    if "subviable" in joined:
        return "subviable"
    return "no lethal term reported"


def impc_phenotypes():
    out = {}
    for g in GENES:
        sym = MOUSE_SYMBOL[g]
        gp = _get_json(IMPC_GP.format(sym=sym))
        docs = (((gp or {}).get("response") or {}).get("docs") or []) if gp else []
        if not docs:
            out[g] = {"_status": "no IMPC genotype-phenotype record (KO not phenotyped or no calls)"}
            continue
        terms = sorted({d.get("mp_term_name") for d in docs if d.get("mp_term_name")})
        top = sorted({d.get("top_level_mp_term_name") for d in docs
                      if d.get("top_level_mp_term_name")})
        zyg = sorted({d.get("zygosity") for d in docs if d.get("zygosity")})
        # viability category (IMPC_VIA procedure) if present
        via = _get_json(IMPC_VIA.format(sym=sym))
        via_docs = (((via or {}).get("response") or {}).get("docs") or []) if via else []
        via_cats = sorted({d.get("category") for d in via_docs if d.get("category")})
        out[g] = {
            "n_significant_calls": len(docs),
            "zygosities_tested": zyg,
            "viability_categories": via_cats or "not separately reported",
            "top_level_phenotype_systems": top,
            "phenotype_terms": terms[:40],
            "lethality_flag": _lethal_flag(terms + via_cats),
        }
    return {
        "_note": "IMPC (International Mouse Phenotyping Consortium) single-gene KO calls. "
                 "The key safety datum is whether the Nr4a3 single-KO is VIABLE (no lethal term) — "
                 "if so, in-vivo evidence that losing NR4A3 alone is tolerated in a mammal. Absence of "
                 "an IMPC record means the KO was not phenotyped there (fall back to primary literature "
                 "PMIDs), NOT that the gene is dispensable. Zygosity matters: homozygous = full KO.",
        "source": "IMPC solr (www.ebi.ac.uk/mi/impc)",
        "genes": out,
    }


# ---------------------------------------------------------------------------------------------------
# 3. Human Protein Atlas RNA tissue expression (co-expression / compensation map).
# ---------------------------------------------------------------------------------------------------
def hpa_expression():
    out = {}
    for g in GENES:
        ensg = ENSEMBL[g]
        # HPA per-gene JSON; request the RNA tissue fields explicitly.
        url = (f"https://www.proteinatlas.org/api/search_download.php?"
               f"search={ensg}&format=json&columns=g,gs,rnats,rnatd,rnatss&compress=no")
        data = _get_json(url)
        rec = data[0] if isinstance(data, list) and data else None
        if not rec:
            out[g] = {"_status": "no HPA record", "ensembl": ensg}
            continue
        out[g] = {
            "ensembl": ensg,
            "rna_tissue_specificity": rec.get("RNA tissue specificity")
            or rec.get("rnats"),
            "rna_tissue_distribution": rec.get("RNA tissue distribution")
            or rec.get("rnatd"),
            "rna_tissue_specific_nTPM": rec.get("RNA tissue specific nTPM")
            or rec.get("rnatss"),
        }
    return {
        "_note": "Human Protein Atlas RNA tissue expression. Question: where do NR4A1/2/3 co-express "
                 "(paralogue compensation available => losing NR4A3 is buffered) vs where is NR4A3 "
                 "expressed without NR4A1/2 (candidate on-target risk tissue). 'Low tissue "
                 "specificity' co-expression across many tissues supports broad buffering. NR4A2's "
                 "CNS/dopaminergic enrichment is the exception to watch.",
        "source": "Human Protein Atlas (proteinatlas.org)",
        "genes": out,
    }


def main():
    result = {
        "_title": "NR4A3-degrader safety evidence (H1) — human/mouse genetics beyond DepMap",
        "_purpose": "Fill the tolerability gap DepMap cannot (post-mitotic / tissue-specific loss). "
                    "Three orthogonal database sources; all values pulled live; gaps flagged not guessed.",
        "gnomad_lof_constraint": gnomad_constraint(),
        "impc_single_ko": impc_phenotypes(),
        "hpa_tissue_expression": hpa_expression(),
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
