#!/usr/bin/env python3
"""Is the mechanism-of-death silence measured in EMC's literature a property of THAT
literature, or the base rate of how death is written about in the same retrieval?

Two questions, in order, both about MEASUREMENT and neither about cause or survival:

 Q1 (instrument)  What are the operating characteristics, against the hand-read gold
                  standard, of the only automatic mechanism detector this repository
                  owns -- `has_mechanism_cue` in research/literature/emc-mortality-probe.json?
                  The probe's own README calls it "a retrieval hint, not a finding" and
                  the classified file says a regex must never assign a mechanism. Neither
                  states what the hint actually scores.
 Q2 (comparator)  IF and ONLY IF Q1 supports it, does the cue-positive rate differ between
                  the 34 EMC-titled papers and the 128 same-retrieval papers that are not
                  about this disease?

No new retrieval. Reads two committed artifacts read-only. Writes one JSON.
"""
import json, math, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[6]
PROBE = ROOT / "research/literature/emc-mortality-probe.json"
GOLD = ROOT / "research/manuscripts/emc-terminal-events-classified.json"
OUT = pathlib.Path(__file__).with_name("cue-instrument-check.json")

# Reused verbatim from research/manuscripts/emc_terminal_events.py:56 so the corpus split
# is the paper's own, not a new one.
EMC_TITLE = re.compile(r"myxoid chondrosarcoma|chordoid sarcoma|NR4A3", re.I)

# The instrument under test, reused verbatim from scripts/lit_mortality_probe.py:145.
CUE_SHIPPED = re.compile(
    r"\b("
    r"respiratory (?:failure|insufficiency|distress)|"
    r"pulmonary (?:insufficiency|failure|embolism|haemorrhage|hemorrhage)|"
    r"sepsis|septic|infection|pneumonia|"
    r"cachexia|malnutrition|"
    r"haemorrhage|hemorrhage|bleeding|"
    r"thrombosis|thromboembolism|embolism|"
    r"cord compression|"
    r"obstruction|"
    r"hepatic failure|liver failure|renal failure|"
    r"cardiac|myocardial|"
    r"cerebral|intracranial|"
    r"multi-?organ|"
    r"asphyxia|airway|"
    r"toxicity|complication|postoperative|"
    r"unrelated|other cause|intercurrent|comorbid"
    r")\b",
    re.I,
)

# PRE-SPECIFIED BEFORE LOOKING AT ANY RESULT. A second, strict instrument built to the
# gold standard's OWN tier-1 definition: a named physiological terminal EVENT. Terms that
# name an organ, a site, a treatment setting, a relatedness judgement or a bare
# "complication" are deliberately excluded, because the gold standard tiers exactly those
# as a broad cause category rather than a stated mechanism.
CUE_STRICT = re.compile(
    r"\b("
    r"respiratory (?:failure|insufficiency|arrest)|"
    r"pulmonary (?:failure|insufficiency)|"
    r"cardiac arrest|cardiopulmonary arrest|"
    r"multi-?organ (?:failure|dysfunction)|"
    r"(?:hepatic|liver|renal|heart) failure|"
    r"septic shock|sepsis|"
    r"asphyxia|exsanguinat\w+|"
    r"(?:cerebral|intracranial|intracerebral|subarachnoid) (?:haemorrhage|hemorrhage)|"
    r"pulmonary embolism"
    r")\b",
    re.I,
)

INSTRUMENTS = {"shipped_has_mechanism_cue": CUE_SHIPPED, "strict_terminal_event": CUE_STRICT}


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def main():
    probe = json.loads(PROBE.read_text())
    gold = json.loads(GOLD.read_text())
    papers = probe["terminal_events"]
    emc = [p for p in papers if EMC_TITLE.search(p.get("title") or "")]
    other = [p for p in papers if not EMC_TITLE.search(p.get("title") or "")]

    # --- integrity: the artifact's stored flag must equal the shipped regex re-run ---
    mismatches = [
        {"pmid": p.get("pmid"), "i": i, "stored": s["has_mechanism_cue"]}
        for p in papers for i, s in enumerate(p["sentences"])
        if bool(CUE_SHIPPED.search(s["sentence"])) != bool(s["has_mechanism_cue"])
    ]

    by_pmid = {p.get("pmid"): p for p in papers}

    # --- Q1: instrument against the hand-read gold rows (unit = gold row = patient) ---
    rows = []
    for r in gold["individual_events"]:
        p = by_pmid.get(r["pmid"])
        sents = [p["sentences"][i]["sentence"] for i in r["sentence_indices"]] if p else []
        rows.append({
            "pmid": r["pmid"],
            "n_patients": r["n_patients"],
            "death_status": r["death_status"],
            "mechanism_tier": r["mechanism_tier"],
            "stated_type": r.get("stated_type"),
            "has_stored_label": r["mechanism_tier"] != "no_cause_stated" and r["label"] not in ("mechanism_unstated", "ambiguous"),
            "label": r["label"],
            "flags": {n: any(bool(rx.search(s)) for s in sents) for n, rx in INSTRUMENTS.items()},
            "quote": r["quote"],
        })

    def tier_table(name):
        t = {}
        for r in rows:
            key = r["mechanism_tier"] + ("/" + r["stated_type"] if r.get("stated_type") else "")
            b = t.setdefault(key, {"rows": 0, "flagged_rows": 0, "patients": 0, "flagged_patients": 0})
            b["rows"] += 1
            b["patients"] += r["n_patients"]
            if r["flags"][name]:
                b["flagged_rows"] += 1
                b["flagged_patients"] += r["n_patients"]
        return t

    # --- false-positive load: EMC death sentences the instrument flags that no gold row cites ---
    cited = {(r["pmid"], i) for r in gold["individual_events"] for i in r["sentence_indices"]}
    fp = {n: [] for n in INSTRUMENTS}
    for p in emc:
        for i, s in enumerate(p["sentences"]):
            for n, rx in INSTRUMENTS.items():
                if rx.search(s["sentence"]) and (p.get("pmid"), i) not in cited:
                    fp[n].append({"pmid": p.get("pmid"), "i": i, "sentence": s["sentence"]})

    # --- Q2: corpus comparison, sentence level ---
    def rate(ps, name):
        rx = INSTRUMENTS[name]
        n = sum(len(p["sentences"]) for p in ps)
        k = sum(1 for p in ps for s in p["sentences"] if rx.search(s["sentence"]))
        pk = sum(1 for p in ps if any(rx.search(s["sentence"]) for s in p["sentences"]))
        return {"sentences": n, "flagged": k, "rate": round(k / n, 4) if n else None,
                "wilson95": wilson(k, n), "papers": len(ps),
                "papers_with_ge1_flag": pk,
                "paper_rate": round(pk / len(ps), 4) if ps else None,
                "paper_wilson95": wilson(pk, len(ps)),
                "flagged_sentences": [s["sentence"] for p in ps for s in p["sentences"] if rx.search(s["sentence"])]}

    def fisher(a, b, c, d):
        """Two-sided Fisher exact on [[a,b],[c,d]]; exact rationals, no SciPy."""
        from math import comb
        n = a + b + c + d
        r1, c1 = a + b, a + c
        def pr(x):
            return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)
        p0 = pr(a)
        lo = max(0, c1 - (n - r1)); hi = min(r1, c1)
        return round(sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-9)), 6)

    comparison = {}
    for n in INSTRUMENTS:
        a = rate(emc, n); b = rate(other, n)
        comparison[n] = {
            "emc_titled": a, "not_emc_titled": b,
            "fisher_exact_two_sided_sentence_level": fisher(
                a["flagged"], a["sentences"] - a["flagged"],
                b["flagged"], b["sentences"] - b["flagged"]),
            "direction": ("emc_higher" if a["rate"] > b["rate"] else
                          "emc_lower" if a["rate"] < b["rate"] else "equal"),
        }

    out = {
        "_what_this_is": __doc__.strip(),
        "_not_a_clinical_claim": (
            "Nothing here says what any patient died of, and nothing here is a survival, "
            "causal or clinical statement. Every number is a property of TEXT: which "
            "sentences a regular expression matches, and how those matches line up with a "
            "hand-read tier. A flagged sentence is not a death and not a mechanism."
        ),
        "inputs": {
            "probe": str(PROBE.relative_to(ROOT)),
            "gold": str(GOLD.relative_to(ROOT)),
            "emc_title_regex": EMC_TITLE.pattern,
        },
        "integrity_stored_flag_vs_rerun": {
            "sentences_checked": sum(len(p["sentences"]) for p in papers),
            "mismatches": len(mismatches),
            "examples": mismatches[:5],
        },
        "corpus": {
            "papers_with_death_sentences": len(papers),
            "emc_titled_papers": len(emc), "emc_titled_sentences": sum(len(p["sentences"]) for p in emc),
            "other_papers": len(other), "other_sentences": sum(len(p["sentences"]) for p in other),
        },
        "q1_instrument_vs_gold": {
            n: {
                "by_tier": tier_table(n),
                "gold_rows_flagged": sum(1 for r in rows if r["flags"][n]),
                "gold_rows_total": len(rows),
                "flagged_emc_sentences_no_gold_row_cites": len(fp[n]),
                "false_positive_examples": fp[n][:6],
            } for n in INSTRUMENTS
        },
        "q2_corpus_comparison": comparison,
        "gold_rows": rows,
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("integrity_stored_flag_vs_rerun", "corpus", "q2_corpus_comparison")}, indent=1))
    for n in INSTRUMENTS:
        print("\n==", n)
        print(json.dumps(out["q1_instrument_vs_gold"][n]["by_tier"], indent=1))
        print("flagged EMC sentences no gold row cites:", out["q1_instrument_vs_gold"][n]["flagged_emc_sentences_no_gold_row_cites"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
