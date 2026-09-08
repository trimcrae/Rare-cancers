#!/usr/bin/env python3
"""Focused post-correction checks for the P-ST correction batch.

Scope, stated honestly: this checks (a) that every printed statistic in the revised main and SI
still binds to the value in the committed artifact it is read from, (b) that the Figure 1 omission
is complete and the original figure bytes are untouched, (c) that the claim-scope corrections of
F01-F13 are present and the withdrawn formulations are gone from live prose, and (d) that the
reproducibility packet manifest reproduces. It is NOT a scientific verification of the paper, not a
reproduction of any producer, and not a publication gate. Nothing here re-derives biology.

Usage: python3 check_pst_correction.py <repo_root> <revised_dir> <packet_manifest.json>
Exit 0 only if every check passes.
"""
import hashlib
import json
import pathlib
import re
import sys

FAILURES = []
PASSED = 0


def check(name, ok, detail=""):
    global PASSED
    if ok:
        PASSED += 1
        print("PASS  %s %s" % (name, detail))
    else:
        FAILURES.append(name)
        print("FAIL  %s %s" % (name, detail))


def sha256(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    root = pathlib.Path(sys.argv[1])
    rev = pathlib.Path(sys.argv[2])
    manifest_path = pathlib.Path(sys.argv[3])
    main_t = (rev / "emc-surface-target-landscape.md").read_text(encoding="utf-8")
    si_t = (rev / "emc-surface-target-landscape-si.md").read_text(encoding="utf-8")
    both = main_t + "\n" + si_t

    # Live prose = everything before the Appendix A correction register in the main text,
    # plus the whole SI. The register retains superseded wording on purpose.
    live = main_t.split("## Appendix A. Correction and supersession register")[0] + "\n" + si_t

    # ---- (a) numeric bindings against committed artifacts -------------------
    stats = json.loads((root / "research/modalities/emc-tissue-read-statistics.json").read_text())
    seq = json.loads((root / "research/modalities/gse28866-tumour-vs-normal.json").read_text())
    scan = json.loads((root / "research/modalities/emc-surfaceome-scan.json").read_text())
    prior = json.loads((root / "research/modalities/emc-surface-normal-window.json").read_text())

    prim = stats["primary"]
    # every q printed in Tables 3-5 for these genes must match the artifact
    q_bindings = [
        ("GPL6244", "ALCAM", 0.000373), ("GPL3290", "ALCAM", 0.161652),
        ("GPL6244", "CSPG4", 0.0017), ("GPL3290", "CSPG4", 0.764),
        ("GPL6244", "FGFR1", 0.0163), ("GPL3290", "FGFR1", 1.0e-06),
        ("GPL6244", "PTK7", 0.0127), ("GPL3290", "PTK7", 0.0104),
        ("GPL6244", "CDH11", 0.0551), ("GPL3290", "CDH11", 0.0337),
        ("GPL6244", "CD276", 0.0876),
        ("GPL6244", "GPC1", 0.0667), ("GPL3290", "GPC1", 0.0231),
        ("GPL6244", "BGN", 0.0033), ("GPL6244", "CD44", 4.7e-05),
        ("GPL6244", "VCAN", 0.0110), ("GPL3290", "VCAN", 0.0104),
    ]
    bad = []
    for plat, gene, printed in q_bindings:
        row = prim[plat][gene]
        if abs(row["q"] - printed) > max(5e-5, abs(printed) * 0.01):
            bad.append("%s/%s printed %s artifact %s" % (plat, gene, printed, row["q"]))
    check("table-q-bindings", not bad, "%d rows; %s" % (len(q_bindings), bad or "all match"))

    # significance flags decided by q >= 0.05, as the corrected text now states
    mism = [(p, g) for p in ("GPL6244", "GPL3290") for g, r in prim[p].items()
            if r.get("significant") != (r["q"] < 0.05)]
    check("q-decides-significance", not mism, "%d rows checked" % sum(len(prim[p]) for p in prim))

    # the 14 / 8 counts of non-significant rows whose ordinary interval excludes zero
    def excl(plat):
        return sum(1 for r in prim[plat].values()
                   if not r["significant"] and r["ci_lo"] * r["ci_hi"] > 0)
    check("F05-nonsig-intervals-excluding-zero", (excl("GPL6244"), excl("GPL3290")) == (14, 8),
          "GPL6244=%d GPL3290=%d; text says 14 and 8" % (excl("GPL6244"), excl("GPL3290")))

    # half-widths printed as half-widths
    hw6 = sorted((r["ci_hi"] - r["ci_lo"]) / 2 for r in prim["GPL6244"].values())
    hw3 = sorted((r["ci_hi"] - r["ci_lo"]) / 2 for r in prim["GPL3290"].values())

    def med(x):
        return x[len(x) // 2] if len(x) % 2 else (x[len(x) // 2 - 1] + x[len(x) // 2]) / 2
    check("F05-halfwidth-values", round(med(hw6), 3) == 0.259 and round(med(hw3), 6) == 0.952475,
          "median half-widths %.5f / %.6f" % (med(hw6), med(hw3)))
    check("F05-halfwidth-wording",
          "median **half-width**" in live and "full widths of about 0.52" in live
          and "0.952475" in live,
          "half-width and full width stated separately")

    # sequencing values in Table S6 bind to the artifact, and only to summaries
    vals = seq["per_gene"]["values"]
    seq_bind = {"CSPG4": (1, 8.730, 2.636, 3.484), "ALCAM": (2, 0.578, 0.631, 0.377),
                "VCAN": (8, 0.473, 0.142, 0.235), "CD44": (7, 0.433, 0.256, 0.265),
                "BGN": (4, 1.225, 0.641, 0.491), "CD248": (2, 1.767, 2.107, 2.715)}
    bad = []
    for g, (npk, e, n, s) in seq_bind.items():
        r = vals[g]
        if r["n_peaks"] != npk or round(r["emc_median"], 3) != e or \
           round(r["normal_median"], 3) != n or round(r["sarcoma_median"], 3) != s:
            bad.append(g)
    check("tableS6-sequencing-bindings", not bad, "%d genes; %s" % (len(seq_bind), bad or "all match"))
    check("F11-sequencing-not-per-sample",
          all(set(v) >= {"n_peaks", "emc_median"} and "per_sample" not in v for v in vals.values())
          and "group-level peak summaries and not per-sample values" in main_t,
          "artifact stores grouped summaries; text says so")

    # F01: null quantitative fields for every classified record
    ant = prior["antigens"]
    classified = [a for a, r in ant.items() if r.get("window")]
    nulls = [a for a in classified
             if ant[a].get("rna_tissue_specific_nTPM") is None and ant[a].get("rna_blood_cell_specific_nTPM") is None]
    check("F01-null-quantitative-fields", len(classified) == 45 and len(nulls) == 45,
          "%d classified, %d with both quantitative fields null" % (len(classified), len(nulls)))
    liab = [a for a in classified if ant[a]["window"] == "VITAL_OR_IMMUNE_LIABILITY"]
    check("F01-nine-liability-labels", len(liab) == 9, "%d liability labels" % len(liab))
    restr_many = [a for a in classified if ant[a]["window"] == "RESTRICTED"
                  and "many" in str(ant[a].get("rna_tissue_distribution", "")).lower()]
    check("F01-restricted-detected-in-many", sorted(restr_many) == ["ALCAM", "B4GALNT1", "GPC3"],
          str(sorted(restr_many)))

    # F07: denominators
    act = scan["actionable_antigens"]
    sel = [g for g, r in act.items() if r.get("selectivity_significant")]
    check("F07-denominators", len(act) == 47 and len(sel) == 18,
          "%d actionable, %d flagged" % (len(act), len(sel)))
    both_p = [g for g in sel if g in prim["GPL6244"] and g in prim["GPL3290"]]
    one_p = [g for g in sel if (g in prim["GPL6244"]) != (g in prim["GPL3290"])]
    none_p = [g for g in sel if g not in prim["GPL6244"] and g not in prim["GPL3290"]]
    check("F02-eligibility-split", (len(both_p), len(one_p), len(none_p)) == (10, 3, 5),
          "%d/%d/%d; one-platform %s" % (len(both_p), len(one_p), len(none_p), sorted(one_p)))
    up_both = [g for g in both_p if prim["GPL6244"][g]["significant"] and prim["GPL3290"][g]["significant"]
               and prim["GPL6244"][g]["delta"] > 0 and prim["GPL3290"][g]["delta"] > 0]
    dn_both = [g for g in both_p if prim["GPL6244"][g]["significant"] and prim["GPL3290"][g]["significant"]
               and prim["GPL6244"][g]["delta"] < 0 and prim["GPL3290"][g]["delta"] < 0]
    check("F02-zero-up-two-down", up_both == [] and sorted(dn_both) == ["FGFR1", "PTK7"],
          "up=%s down=%s" % (up_both, sorted(dn_both)))
    check("F07-arrays-arithmetic", "leaves **7** remaining arrays" in live
          and "remaining 13 arrays" not in live, "42 - 6 - 29 = 7 in live prose")

    # ---- (b) figure omission ----------------------------------------------
    png = root / "research/modalities/emc-surface-prioritization.png"
    check("F08-original-png-untouched",
          sha256(png) == "130042b6afab8aea28874d37dd684cde96886ab25b488ab65b83dac391c439bd",
          "sha256 matches the reviewed bytes")
    check("F08-no-figure-display-item",
          "**Figure 1.**" not in main_t and "**Figure 1 is omitted" in main_t,
          "no Figure 1 display item; omission stated")
    check("F08-no-figure-call",
          not re.search(r"\(Figure 1\)|see Figure 1|Figure 1 shows", main_t),
          "no in-text call to Figure 1")
    # The figure's printed assertions may appear ONLY inside the paragraph that records the
    # omission (as quotations of what was withdrawn), never as assertions of the paper.
    omission = live.split("**Figure 1 is omitted from this version")[1].split("\n\n")[0] \
        if "**Figure 1 is omitted from this version" in live else ""
    stray = [s for s in ("clean window", "target-worthy", "NOT EVALUATED")
             if live.count(s) != omission.count(s)]
    check("F08-no-pixel-assertions", not stray,
          "printed assertions appear only inside the omission record; stray=%s" % stray)

    # ---- (c) claim-scope corrections present, withdrawn wording gone -------
    must_be_absent = {
        "F01-window": ["and given a verdict with\nHuman Protein Atlas semantics",
                       "Controls behaved as specified"],
        "F01-decisive": ["The normal-tissue prior is the decisive filter"],
        "F02-transfer": ["an estimate of how far a lineage-surrogate surface ranking transfers"],
        "F02-notreproduced": ["were not reproduced in EMC\ntumour tissue"],
        "F03-readdensity": ["Read densities from 3'-end sequencing"],
        "F04-pointdifferent": ["The two normal-tissue instruments in this study point different ways"],
        "F05-ns-definition": ["95 % interval includes zero after correction"],
        "F05-exactp": ["carries an exact two-sided *p*"],
        "F06-knownanswers": ["Three genes with known answers were read on the same platforms before any antigen"],
        "F06-licence": ["A\nworking control licenses reading the other rows",
                        "A working control licenses reading the other rows"],
        "F06-prespecified": ["Three prespecified sensitivity analyses accompany"],
        "F07-neverevaluated": ["not evaluated | RESTRICTED", "which the original search never evaluated"],
        "F09-floor": ["PRAME reads at the floor of every readable cohort"],
        "F09-saturated": ["The background is saturated"],
        "F10-artefact": ["the disagreement is partly a coverage\nartefact",
                         "the disagreement is partly a coverage artefact"],
        "F12-discontinued": ["was clinically\ndeveloped and discontinued"],
        "F12-238": ["238 of them with full text"],
        "F13-independent": ["Three independent readouts, recorded in"],
    }
    for name, needles in must_be_absent.items():
        hits = [n for n in needles if n in live]
        check("absent/" + name, not hits, "" if not hits else "still present: %r" % hits[:1])

    must_be_present = {
        "F01": "custom category heuristic",
        "F01b": "null for **all 45 classified records**",
        "F02": "no transfer-accuracy or\nranking estimand is defined or estimated",
        "F03": "taking the square root of each value",
        "F03b": "median across the libraries within an arm for each peak",
        "F04": "**17 adult and 10 fetal**",
        "F04b": "come from **30 specimens**",
        "F05": "ordinary\npointwise 95 % confidence interval",
        "F06": "regression checks, not an independent known-answer calibration",
        "F07": "no retained selectivity result",
        "F08": "**Figure 1 is omitted from this version",
        "F09": "ranks across probes and not evidence of\ndetector saturation",
        "F10": "joint replicability false-discovery rate",
        "F11": "no independent reproduction of any analysis from its original public source",
        "F12": "PMID 21536545",
        "F13": "not verified biological absence",
        "A7": "Appendix A7 — Final-review correction batch",
    }
    for name, needle in must_be_present.items():
        hay = both if name in ("F11", "F13", "A7") else both
        check("present/" + name, needle.lower() in hay.lower(), "")

    # ---- (d) packet manifest -----------------------------------------------
    man = json.loads(manifest_path.read_text())
    bad = []
    for e in man["entries"]:
        p = root / e["path"]
        if not p.exists():
            bad.append(e["path"] + " MISSING")
        elif p.stat().st_size != e["bytes"] or sha256(p) != e["sha256"]:
            bad.append(e["path"] + " CHANGED")
    check("packet-manifest-reproduces", not bad,
          "%d entries; %s" % (len(man["entries"]), bad or "all match"))

    print("\n%d passed, %d failed" % (PASSED, len(FAILURES)))
    if FAILURES:
        print("FAILED: " + ", ".join(FAILURES))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
