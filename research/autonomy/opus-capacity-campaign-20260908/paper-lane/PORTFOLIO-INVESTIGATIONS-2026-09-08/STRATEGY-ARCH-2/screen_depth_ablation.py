#!/usr/bin/env python3
"""Screen-depth ablation: does giving a keyword screen the POSTED ELIGIBILITY TEXT
make it safer?

The reachability manuscript's remedy (SS6) tells tool-builders to read criteria
rather than match strings. The PUB-STRATEGY-ARCH benchmark scored screens that see
only titles + listed conditions. This ablation holds the lexicons and the ground
truth fixed and varies ONE thing -- how deep the string matcher reads -- over the
four records whose posted criterion text is committed verbatim in the adjudication
deposit.

  depth_A_index_only    brief_title + official_title + listed_conditions
  depth_B_index_plus_criterion   depth A + the verbatim posted criterion
  depth_C_criterion_only         the verbatim posted criterion alone

Falsifiable criterion stated in advance: if 'read the criteria' is protective for a
STRING screen, then depth B must be at least as precise as depth A for every
lexicon. A single lexicon whose precision falls refutes that.

Inputs (committed, read-only; nothing is fetched):
  research/literature/emc-trial-reachability-adjudication-2026-08-09.json

Not medical advice, not a trial-matching service. Every label is a statement about
registry text on the retrieval date recorded in the deposit. No patient, referral,
enrolment or outcome is involved, and nothing here says any trial would accept any
patient. No efficacy, safety, selectivity or therapeutic-window claim is made or
implied.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
ADJ = os.path.join(ROOT, "research/literature/emc-trial-reachability-adjudication-2026-08-09.json")

# admit/refuse read off adjudications[].verdict, transcribed here.
VERDICT_TOKEN = {"NCT06571734": ("admits", "ADMITS"),
                 "NCT04151342": ("admits", "ADMITS BY WORDING"),
                 "NCT06094101": ("refuses", "DOES NOT ADMIT"),
                 "NCT07188532": ("refuses", "DOES NOT ADMIT")}

LEXICONS = {
    "histology_only": ["extraskeletal", "extra-skeletal", "extra skeletal",
                       "myxoid", "chondrosarcoma"],
    "molecular_only": ["nr4a3", "ewsr1", "fet fusion", "fusion", "translocation"],
}
LEXICONS["union"] = LEXICONS["histology_only"] + LEXICONS["molecular_only"]


def build():
    adj = {a["nct_id"]: a for a in json.load(open(ADJ))["adjudications"]}
    recs = {}
    for nct, (verdict, token) in VERDICT_TOKEN.items():
        a = adj[nct]
        # Validate the verdict against the deposit's own wording; do not assume it.
        if token not in a["verdict"]:
            print("FAIL: %s verdict %r does not carry %r" % (nct, a["verdict"], token),
                  file=sys.stderr)
            sys.exit(2)
        index = " | ".join(
            [a.get("brief_title_verbatim") or "", a.get("official_title_verbatim") or ""]
            + list(a.get("listed_conditions") or []))
        crit = (a.get("the_admitting_criterion_verbatim")
                or a.get("the_restricting_criterion_verbatim") or "")
        if not crit:
            print("FAIL: %s carries no verbatim criterion text" % nct, file=sys.stderr)
            sys.exit(2)
        recs[nct] = dict(verdict=verdict,
                         criterion_field=("the_admitting_criterion_verbatim"
                                          if a.get("the_admitting_criterion_verbatim")
                                          else "the_restricting_criterion_verbatim"),
                         depth_A_index_only=index.lower(),
                         depth_B_index_plus_criterion=(index + " | " + crit).lower(),
                         depth_C_criterion_only=crit.lower())
    return recs


DEPTHS = ["depth_A_index_only", "depth_B_index_plus_criterion", "depth_C_criterion_only"]


def main():
    recs = build()
    results, table = {}, []
    for lname, lex in LEXICONS.items():
        for depth in DEPTHS:
            tp = fp = tn = fn = 0
            for nct, r in recs.items():
                hit = any(t in r[depth] for t in lex)
                adm = r["verdict"] == "admits"
                if hit and adm: tp += 1
                elif hit and not adm: fp += 1
                elif (not hit) and adm: fn += 1
                else: tn += 1
            p = tp / (tp + fp) if (tp + fp) else None
            rc = tp / (tp + fn) if (tp + fn) else None
            results["%s@%s" % (lname, depth)] = dict(
                lexicon=lex, depth=depth, n=tp + fp + tn + fn, true_positive=tp,
                false_positive=fp, true_negative=tn, false_negative=fn,
                precision=p, recall=rc)
            table.append((lname, depth, tp + fp + tn + fn, tp, fp, tn, fn, p, rc))

    w = lambda x: "undefined" if x is None else "%.2f" % x
    print("%-16s %-30s %-2s %-2s %-2s %-2s %-2s %-10s %-10s"
          % ("lexicon", "depth", "n", "TP", "FP", "TN", "FN", "precision", "recall"))
    for row in table:
        print("%-16s %-30s %-2d %-2d %-2d %-2d %-2d %-10s %-10s"
              % (row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                 w(row[7]), w(row[8])))

    # The stated falsifiable criterion, evaluated.
    print("\n-- falsifiable criterion: depth B precision >= depth A precision, every lexicon --")
    refuted = []
    for lname in LEXICONS:
        a = results["%s@depth_A_index_only" % lname]["precision"]
        b = results["%s@depth_B_index_plus_criterion" % lname]["precision"]
        if a is None and b is None:
            verdict = "both undefined (screen never fires) - no evidence"
        elif a is None and b is not None:
            verdict = ("depth A never fires; depth B fires and is %.2f precise -> "
                       "reading criteria CREATED this screen's only hit" % b)
            if b < 1.0:
                verdict += " and that hit is wrong"
                refuted.append(lname)
        elif b is None:
            verdict = "depth B never fires"
        else:
            verdict = "A=%.2f B=%.2f -> %s" % (a, b, "held" if b >= a else "REFUTED")
            if b < a:
                refuted.append(lname)
        print("  %-16s %s" % (lname, verdict))
    print("\nlexicons where deeper string reading did NOT improve precision:",
          refuted or "none")

    # Per-record hit deltas, so the table is auditable one record at a time.
    print("\n-- per-record hits --")
    per_record = {}
    for nct, r in sorted(recs.items()):
        entry = dict(verdict=r["verdict"], criterion_field=r["criterion_field"])
        for lname, lex in LEXICONS.items():
            if lname == "union":
                continue
            for depth in DEPTHS:
                entry["%s@%s" % (lname, depth)] = [t for t in lex if t in r[depth]]
        entry["depth_C_criterion_only_text"] = r["depth_C_criterion_only"]
        entry["depth_A_index_only_text"] = r["depth_A_index_only"]
        per_record[nct] = entry
        print("  %s %-8s hist A=%s B=%s | mol A=%s B=%s" % (
            nct, r["verdict"],
            entry["histology_only@depth_A_index_only"],
            entry["histology_only@depth_B_index_plus_criterion"],
            entry["molecular_only@depth_A_index_only"],
            entry["molecular_only@depth_B_index_plus_criterion"]))

    out = dict(
        _what=("Screen-depth ablation: keyword screens scored against eligibility-read "
               "adjudications at three reading depths, EMC trial reachability."),
        _not_medical_advice=(
            "Not medical advice, not a trial-matching service. Labels are statements "
            "about registry text on the retrieval date in the source deposit. No "
            "patient, referral, enrolment or outcome is involved. No efficacy, safety, "
            "selectivity or therapeutic-window claim is made or implied."),
        generated_by=("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                      "PORTFOLIO-INVESTIGATIONS-2026-09-08/STRATEGY-ARCH-2/"
                      "screen_depth_ablation.py"),
        inputs=[os.path.relpath(ADJ, ROOT)],
        ground_truth_definition=(
            "admit/refuse on the record's POSTED eligibility text, as adjudicated in "
            "adjudications[].verdict; each label is re-checked against the deposit's "
            "own verdict wording at run time and the script exits 2 on any mismatch."),
        depth_definitions=dict(
            depth_A_index_only="brief_title + official_title + listed_conditions",
            depth_B_index_plus_criterion="depth A plus the verbatim posted criterion",
            depth_C_criterion_only="the verbatim posted criterion alone"),
        falsifiable_criterion=(
            "If reading criteria is protective for a STRING screen, depth B precision "
            "must be >= depth A precision for every lexicon."),
        criterion_outcome_lexicons_not_improved=refuted,
        truncation_direction=(
            "The committed criterion text is ONE quoted criterion per record, not the "
            "full eligibility section, so depths B and C are a LOWER BOUND on what a "
            "real matcher would read. The bound is directional: more criterion text can "
            "only ADD hits, so on a refusing record it can only add false positives and "
            "on an admitting record it can only add true positives. The histology false "
            "positive reported here is therefore robust to truncation -- more text "
            "cannot remove it -- while the depth-C molecular recall of 0.50 is an upper "
            "bound on how bad recall gets, not a measurement of it."),
        denominator=("Four records -- every adjudicated record whose posted criterion "
                     "text is committed verbatim. Not a sample of the registry."),
        results=results, records=per_record)
    dest = os.path.join(HERE, "screen-depth-ablation.json")
    json.dump(out, open(dest, "w"), indent=2)
    print("\nwrote", os.path.relpath(dest, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
