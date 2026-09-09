#!/usr/bin/env python3
"""STRATEGY-ARCH-3 -- three things, in order, over the committed deposits only.

1. RE-DERIVATION. Rebuild STRATEGY-ARCH-2's nine-row screen-depth ablation from the
   committed deposit with independent code (this file imports neither
   screen_depth_ablation.py nor keyword_screen_benchmark.py) and compare cell by cell
   against STRATEGY-ARCH-2/screen-depth-ablation.json. Any non-reproducing cell is
   reported digit for digit and the script stops there.

2. FRAGILITY. The headline is a precision LOSS from depth A to depth B on the union
   lexicon (0.67 -> 0.50) over n = 4 records. Enumerate every subset of ground-truth
   label flips and report the minimum number of flips that reverses the direction of
   that loss, and which flips they are.

3. EXTENSION. STRATEGY-ARCH-2 recorded that the four FET-deposit records cannot be
   scored at depth B/C because the deposit stores a BOOLEAN, not the text. Test that
   claim against the whole checkout: the fetched ClinicalTrials.gov payloads live in
   the local git ref origin/literature-cache. Where a payload exists, read
   eligibilityModule.eligibilityCriteria out of it and score the enlarged table.

Read-only. No network: git show reads objects already in this clone.

Not medical advice, not a trial-matching service. Every label is a statement about
registry text on the retrieval date recorded in the source deposit. No patient,
referral, enrolment or outcome is involved, and nothing here says any trial would
accept any patient. No efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim is made or implied.
"""
import itertools, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
ADJ = os.path.join(ROOT, "research/literature/emc-trial-reachability-adjudication-2026-08-09.json")
FET = os.path.join(ROOT, "research/literature/fet-fusion-trial-eligibility-2026-08-07.json")
PRIOR = os.path.join(ROOT, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                     "PORTFOLIO-INVESTIGATIONS-2026-09-08/STRATEGY-ARCH-2/screen-depth-ablation.json")

LEX = {"histology_only": ["extraskeletal", "extra-skeletal", "extra skeletal",
                          "myxoid", "chondrosarcoma"],
       "molecular_only": ["nr4a3", "ewsr1", "fet fusion", "fusion", "translocation"]}
LEX["union"] = LEX["histology_only"] + LEX["molecular_only"]
DEPTHS = ["depth_A_index_only", "depth_B_index_plus_criterion", "depth_C_criterion_only"]

# admit/refuse read off the deposit; re-validated against the deposit's own wording below.
ADJ_TOKEN = {"NCT06571734": ("admits", "ADMITS"), "NCT04151342": ("admits", "ADMITS BY WORDING"),
             "NCT06094101": ("refuses", "DOES NOT ADMIT"), "NCT07188532": ("refuses", "DOES NOT ADMIT")}


def score(recs, lex, depth, flips=()):
    tp = fp = tn = fn = 0
    for nct, r in recs.items():
        hit = any(t in r[depth] for t in lex)
        adm = (r["verdict"] == "admits") ^ (nct in flips)
        if hit and adm: tp += 1
        elif hit: fp += 1
        elif adm: fn += 1
        else: tn += 1
    p = tp / (tp + fp) if (tp + fp) else None
    rc = tp / (tp + fn) if (tp + fn) else None
    return dict(n=tp + fp + tn + fn, true_positive=tp, false_positive=fp,
                true_negative=tn, false_negative=fn, precision=p, recall=rc)


def build_adjudicated():
    adj = {a["nct_id"]: a for a in json.load(open(ADJ))["adjudications"]}
    recs = {}
    for nct, (verdict, token) in ADJ_TOKEN.items():
        a = adj[nct]
        if token not in a["verdict"]:
            print("FAIL: %s verdict %r lacks %r" % (nct, a["verdict"], token), file=sys.stderr)
            sys.exit(2)
        idx = " | ".join([a.get("brief_title_verbatim") or "", a.get("official_title_verbatim") or ""]
                         + list(a.get("listed_conditions") or []))
        crit = a.get("the_admitting_criterion_verbatim") or a.get("the_restricting_criterion_verbatim") or ""
        if not crit:
            print("FAIL: %s has no verbatim criterion" % nct, file=sys.stderr); sys.exit(2)
        recs[nct] = {"verdict": verdict,
                     "depth_A_index_only": idx.lower(),
                     "depth_B_index_plus_criterion": (idx + " | " + crit).lower(),
                     "depth_C_criterion_only": crit.lower()}
    return recs


def fmt(x):
    return "undefined" if x is None else "%.4f" % x


def main():
    out = {}
    # ---------------- 1 · RE-DERIVATION ----------------
    print("=" * 78)
    print("1 . RE-DERIVATION of STRATEGY-ARCH-2's nine-row ablation, independent code")
    print("=" * 78)
    recs = build_adjudicated()
    mine, mismatches = {}, []
    prior = json.load(open(PRIOR))["results"]
    print("%-16s %-30s %2s %2s %2s %2s %2s %-10s %-10s %s"
          % ("lexicon", "depth", "n", "TP", "FP", "TN", "FN", "precision", "recall", "vs prior"))
    for lname, lex in LEX.items():
        for depth in DEPTHS:
            m = score(recs, lex, depth)
            key = "%s@%s" % (lname, depth)
            mine[key] = m
            p = prior.get(key)
            bad = []
            for f in ("n", "true_positive", "false_positive", "true_negative",
                      "false_negative", "precision", "recall"):
                if p is None or p.get(f) != m[f]:
                    bad.append("%s: mine=%r prior=%r" % (f, m[f], None if p is None else p.get(f)))
            if bad:
                mismatches.append((key, bad))
            print("%-16s %-30s %2d %2d %2d %2d %2d %-10s %-10s %s"
                  % (lname, depth, m["n"], m["true_positive"], m["false_positive"],
                     m["true_negative"], m["false_negative"], fmt(m["precision"]),
                     fmt(m["recall"]), "MISMATCH" if bad else "reproduces"))
    print("\nMISMATCHES: %d" % len(mismatches))
    for key, bad in mismatches:
        print("  %s" % key)
        for b in bad:
            print("     %s" % b)
    out["rederivation"] = {"rows": mine, "mismatch_count": len(mismatches),
                           "mismatches": [{"cell": k, "detail": b} for k, b in mismatches]}
    if mismatches:
        print("\nA cell did not reproduce. Stopping here, as instructed.", file=sys.stderr)
        json.dump(out, open(os.path.join(HERE, "depth-fragility-and-extension.json"), "w"), indent=2)
        return 3

    # ---------------- 2 · FRAGILITY ----------------
    print()
    print("=" * 78)
    print("2 . FRAGILITY of the headline: union precision falls depth A -> depth B, n = 4")
    print("=" * 78)
    base_a = mine["union@depth_A_index_only"]["precision"]
    base_b = mine["union@depth_B_index_plus_criterion"]["precision"]
    print("as scored:  union A precision = %s , B = %s , delta = %s"
          % (fmt(base_a), fmt(base_b), fmt(base_b - base_a)))
    print("direction as published: B < A  (deeper string reading LOSES precision)\n")
    order = sorted(recs)
    frag = {}
    for lname in LEX:
        rows = []
        for k in range(1, len(order) + 1):
            for combo in itertools.combinations(order, k):
                a = score(recs, LEX[lname], "depth_A_index_only", combo)["precision"]
                b = score(recs, LEX[lname], "depth_B_index_plus_criterion", combo)["precision"]
                if a is None or b is None:
                    verdict = "undefined"
                elif b < a:
                    verdict = "loss preserved"
                elif b == a:
                    verdict = "loss ERASED (equal)"
                else:
                    verdict = "loss REVERSED (B > A)"
                rows.append(dict(flips=list(combo), k=k, precision_A=a, precision_B=b,
                                 outcome=verdict))
        frag[lname] = rows
        killers = [r for r in rows if r["outcome"] != "loss preserved"]
        min_k = min([r["k"] for r in killers], default=None)
        print("  lexicon %s" % lname)
        if min_k is None:
            print("     no combination of label flips removes the loss (or it is undefined "
                  "throughout)")
        else:
            print("     MINIMUM FLIPS that remove the published direction: %d" % min_k)
            for r in killers:
                if r["k"] == min_k:
                    print("        flip %-12s -> A=%s B=%s  %s"
                          % (",".join(r["flips"]), fmt(r["precision_A"]),
                             fmt(r["precision_B"]), r["outcome"]))
    out["fragility"] = frag

    # ---------------- 3 · EXTENSION ----------------
    print()
    print("=" * 78)
    print("3 . DOES THE ELIGIBILITY TEXT EXIST ANYWHERE IN THIS CHECKOUT?")
    print("=" * 78)
    fet = json.load(open(FET))
    # the four FET-deposit-labelled records used by the prior benchmark
    fet_truth = {"NCT05918640": "admits", "NCT05275426": "admits",
                 "NCT07695311": "refuses", "NCT07328425": "refuses"}
    ls = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "origin/literature-cache",
                         "--name-only"], capture_output=True, text=True)
    print("git ls-tree origin/literature-cache exit=%d, %d paths"
          % (ls.returncode, len(ls.stdout.splitlines())))
    paths = ls.stdout.splitlines()
    found = {}
    for nct in list(ADJ_TOKEN) + list(fet_truth):
        cands = [p for p in paths if nct.lower() in p.lower()]
        found[nct] = cands
        print("  %-12s payloads in ref: %s" % (nct, cands or "NONE"))

    def criteria_from(path):
        blob = subprocess.run(["git", "-C", ROOT, "show", "origin/literature-cache:" + path],
                              capture_output=True, text=True)
        if blob.returncode != 0:
            return None, "git show exit %d" % blob.returncode
        body = blob.stdout.split("=" * 70, 1)
        if len(body) != 2:
            return None, "no payload separator"
        try:
            j = json.loads(body[1].strip())
        except Exception as e:
            return None, "unparseable: %s" % e
        try:
            return j["protocolSection"]["eligibilityModule"]["eligibilityCriteria"], "ok"
        except KeyError:
            return None, "no eligibilityModule.eligibilityCriteria"

    print("\n  extracting eligibilityModule.eligibilityCriteria:")
    ext = {}
    for nct, cands in found.items():
        pick = None
        for p in cands:
            if "/ct_nct" in p.lower():
                pick = p
                break
        if pick is None:
            ext[nct] = dict(payload=None, status="no per-record payload in ref")
            print("     %-12s -> NO per-record payload" % nct)
            continue
        text, status = criteria_from(pick)
        ext[nct] = dict(payload=pick, status=status,
                        chars=None if text is None else len(text),
                        orphan_gt=None if text is None else text.count(">"),
                        literal_lt=None if text is None else text.count("<"),
                        text=text)
        print("     %-12s -> %-58s %s (%s chars, %s orphaned '>')"
              % (nct, pick, status, ext[nct]["chars"], ext[nct]["orphan_gt"]))
    out["eligibility_text_search"] = {k: {kk: vv for kk, vv in v.items() if kk != "text"}
                                      for k, v in ext.items()}

    # enlarged table, full criteria from payload, for every record where text was found
    idx_text = {}
    for nct, (verdict, _t) in ADJ_TOKEN.items():
        idx_text[nct] = None  # filled below from the adjudication deposit
    adj = {a["nct_id"]: a for a in json.load(open(ADJ))["adjudications"]}
    for nct in ADJ_TOKEN:
        a = adj[nct]
        idx_text[nct] = " | ".join([a.get("brief_title_verbatim") or "",
                                    a.get("official_title_verbatim") or ""]
                                   + list(a.get("listed_conditions") or []))
    prior_bench = json.load(open(os.path.join(
        ROOT, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
        "PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-STRATEGY-ARCH/keyword-screen-benchmark.json")))
    for r in prior_bench["records"]:
        if r["nct"] in fet_truth:
            idx_text[r["nct"]] = r["visible_fields"]

    big, skipped = {}, []
    for nct, truth in list(ADJ_TOKEN.items()) + list(fet_truth.items()):
        truth = truth[0] if isinstance(truth, tuple) else truth
        e = ext.get(nct) or {}
        if not e.get("text"):
            skipped.append((nct, e.get("status", "n/a")))
            continue
        idx = (idx_text[nct] or "").lower()
        crit = e["text"].lower()
        big[nct] = {"verdict": truth, "depth_A_index_only": idx,
                    "depth_B_index_plus_criterion": idx + " | " + crit,
                    "depth_C_criterion_only": crit}
    print("\n  ENLARGED SET: %d records scorable at depth B/C (%s)"
          % (len(big), ", ".join(sorted(big))))
    print("  excluded: %s" % (skipped or "none"))
    enl = {}
    print("\n%-16s %-30s %2s %2s %2s %2s %2s %-10s %-10s"
          % ("lexicon", "depth", "n", "TP", "FP", "TN", "FN", "precision", "recall"))
    for lname, lex in LEX.items():
        for depth in DEPTHS:
            m = score(big, lex, depth)
            enl["%s@%s" % (lname, depth)] = m
            print("%-16s %-30s %2d %2d %2d %2d %2d %-10s %-10s"
                  % (lname, depth, m["n"], m["true_positive"], m["false_positive"],
                     m["true_negative"], m["false_negative"], fmt(m["precision"]),
                     fmt(m["recall"])))
    out["enlarged"] = {"records_scored": sorted(big), "excluded": skipped,
                       "rows": enl,
                       "criterion_source": "full eligibilityModule.eligibilityCriteria from the "
                                           "per-record ClinicalTrials.gov payload stored in the "
                                           "local git ref origin/literature-cache"}
    print("\n-- enlarged-set criterion, same test: depth B precision >= depth A precision? --")
    for lname in LEX:
        a = enl["%s@depth_A_index_only" % lname]["precision"]
        b = enl["%s@depth_B_index_plus_criterion" % lname]["precision"]
        print("  %-16s A=%s B=%s -> %s" % (lname, fmt(a), fmt(b),
              "undefined" if (a is None or b is None) else
              ("held" if b >= a else "REFUTED")))

    # fragility of the enlarged headline too
    order2 = sorted(big)
    frag2 = {}
    for lname in LEX:
        killers = []
        for k in range(1, len(order2) + 1):
            for combo in itertools.combinations(order2, k):
                a = score(big, LEX[lname], "depth_A_index_only", combo)["precision"]
                b = score(big, LEX[lname], "depth_B_index_plus_criterion", combo)["precision"]
                if a is None or b is None or b >= a:
                    killers.append(dict(flips=list(combo), k=k, precision_A=a, precision_B=b))
            if killers:
                break
        frag2[lname] = dict(min_flips=(killers[0]["k"] if killers else None),
                            flip_sets=killers)
    out["enlarged_fragility"] = frag2
    print("\n-- enlarged-set fragility (minimum label flips that remove the loss) --")
    for lname, v in frag2.items():
        print("  %-16s min_flips=%s  e.g. %s" % (
            lname, v["min_flips"],
            ", ".join(",".join(f["flips"]) for f in v["flip_sets"][:4]) or "n/a"))

    out["_not_medical_advice"] = (
        "Not medical advice, not a trial-matching service. Labels are statements about "
        "registry text on the retrieval dates recorded in the source deposits. No patient, "
        "referral, enrolment, treatment or outcome is involved. No efficacy, safety, "
        "selectivity, therapeutic-window or clinical-readiness claim is made or implied. "
        "The cost of a false hit remains UNKNOWN, not zero.")
    out["generated_by"] = os.path.relpath(os.path.abspath(__file__), ROOT)
    out["inputs"] = [os.path.relpath(ADJ, ROOT), os.path.relpath(FET, ROOT),
                     os.path.relpath(PRIOR, ROOT),
                     "git ref origin/literature-cache (already in this clone; no network)"]
    dest = os.path.join(HERE, "depth-fragility-and-extension.json")
    json.dump(out, open(dest, "w"), indent=2)
    print("\nwrote", os.path.relpath(dest, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
