#!/usr/bin/env python3
"""Direct text / package / annotation integrity checks for the P-ST residual batch R1-R8.

No scientific calculation. Every check either reads stored fields or compares text.
Run from the repository root. Exits non-zero if any check fails; no check is skipped.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(".").resolve()
LANE = ROOT / "research/autonomy/opus-capacity-campaign-20260908/paper-lane"
REV = LANE / "P-ST-correction/revised"
BEFORE = LANE / "PST-residual/BEFORE-2026-09-08"
CANON = ROOT / "research/manuscripts/surface-targets"

fails = []
TOTAL = [0]


def check(name, ok, detail=""):
    TOTAL[0] += 1
    print("%-4s %-42s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


main_t = (REV / "emc-surface-target-landscape.md").read_text(encoding="utf-8")
si_t = (REV / "emc-surface-target-landscape-si.md").read_text(encoding="utf-8")
main_b = (BEFORE / "revised--emc-surface-target-landscape.md").read_text(encoding="utf-8")
si_b = (BEFORE / "revised--emc-surface-target-landscape-si.md").read_text(encoding="utf-8")

# live prose = everything before the dated appendix registers that retain superseded quotations
A7 = "### Appendix A7 — Final-review correction batch"
live_main = main_t.split(A7)[0]
live_si = si_t

# ---- R6: sixteen panels, measured from the artifact and stated in the text
stats = json.load(open("research/modalities/emc-tissue-read-statistics.json"))
rows = stats["panel_scores_with_p"]["rows"]
scored = {"GPL6244": 0, "GPL3290": 0}
unscored = {"GPL6244": [], "GPL3290": []}
for panel, per in rows.items():
    for plat, rec in per.items():
        if rec.get("scored"):
            scored[plat] += 1
        else:
            unscored[plat].append(panel)
check("R6-artifact-scored-9-plus-7",
      scored == {"GPL6244": 9, "GPL3290": 7} and unscored["GPL6244"] == []
      and sorted(unscored["GPL3290"]) == ["hla_presented_intracellular_antigens_NOT_surface",
                                          "somatostatin_receptor_family"],
      "GPL6244=%d GPL3290=%d; unscored GPL3290=%s" % (scored["GPL6244"], scored["GPL3290"],
                                                      sorted(unscored["GPL3290"])))
# Expected occurrences, corrected 2026-09-08 after RUN-10 measured the tree (RUN-10 preserved as a
# failure): main live prose 1 (Results), main dated registers 2 (Appendix A7 erratum row, Appendix A8
# R6 row), SI 2 (Table S5 caption, Note S5). Five live/summary locations state 16 in total.
check("R6-text-says-16",
      live_main.count("16 scored panel contrasts") == 1
      and main_t.count("16 scored") == 3
      and si_t.count("16 scored panel contrasts") == 2,
      "main live prose=%d, main incl. dated registers=%d, SI=%d"
      % (live_main.count("16 scored panel contrasts"), main_t.count("16 scored"),
         si_t.count("16 scored panel contrasts")))
check("R6-17-only-in-dated-register",
      "17 available panel" not in live_main and "17 available panel" not in si_t
      and main_t.count("17 available panel") == 1,
      "the single surviving '17 available panel' is inside the dated Appendix A8 erratum row")
check("R6-both-unscored-states-preserved",
      si_t.count("no score: 1 of 5 readable, coverage 0.20") == 1
      and si_t.count("no score: 4 of 10 readable, coverage 0.40") == 1,
      "Table S5 still shows both GPL3290 panels as unscored")

# ---- every Table S5 panel value byte-identical before/after
def table_rows(text, header):
    out, on = [], False
    for line in text.splitlines():
        if header in line:
            on = True
            continue
        if on:
            if line.startswith("|"):
                out.append(line)
            elif out:
                break
    return out


s5_before = table_rows(si_b, "| Panel | GPL6244")
s5_after = table_rows(si_t, "| Panel | GPL6244")
check("R6-panel-values-unchanged", s5_before == s5_after and len(s5_after) >= 10,
      "%d Table S5 rows, byte-identical to the pre-residual candidate" % len(s5_after))

# ---- R8: the parent's applied receipt, verified against the live tree
R8 = {
    "research/modalities/gse28866-tumour-vs-normal.json":
        (28606, "386a035175d94ef8eccd3719d74ef39cff5e93461ed2470983777333a1962cee"),
    "research/modalities/gse28866_tumour_vs_normal.py":
        (31856, "404fe28582d9891a498b5407dc980e5ce7a16ac94a11eee267f7f6b7d8d4b46a"),
}
for p, (nb, h) in R8.items():
    got = pathlib.Path(p).stat().st_size, sha(p)
    check("R8-receipt-binds " + pathlib.Path(p).name, got == (nb, h), "%d B %s" % got)

# ---- R8: the annotation keys are present and the superseded string is retained verbatim
gse = json.load(open("research/modalities/gse28866-tumour-vs-normal.json"))
pg = gse["per_gene"]
check("R8-three-annotation-keys",
      "_contrast" in pg and "_contrast_superseded_2026-09-08" in pg
      and "_annotation_correction_2026-09-08" in pg,
      "corrected literal plus the verbatim superseded string plus the dated note")

# ---- R4: the artifact really holds final gene-level medians, not per-sample values
vals = pg["values"]
ok = all({"n_peaks", "emc_median", "normal_median", "sarcoma_median"} <= set(v)
         and not any("per_sample" in k or "per_library" in k or "per_peak" in k for k in v)
         for v in vals.values())
check("R4-artifact-holds-final-gene-medians", ok,
      "%d genes; each carries n_peaks and the three arm medians, and no per-sample, per-library or per-peak field"
      % len(vals))
check("R4-text-states-that-boundary",
      "final gene-level arm medians" in main_t and "cannot" in main_t
      and "the median across libraries per peak" in main_t
      and "per-library values and the separate per-peak arm medians are not retained" in main_t
      and "per-library values and the separate per-peak arm medians are not retained" in si_t,
      "main and SI both state retrieval plus ratio/band arithmetic and the unavailable two-stage reduction")
check("R4-accession-cache-is-provenance",
      "upstream\nprobe-to-symbol mapping provenance" in main_t
      and "not a runtime dependency of this statistics step" in main_t
      and "depends on `accession-symbol-cache.json` for probe-to-symbol" not in live_main,
      "accession cache described as upstream mapping provenance")

# ---- withdrawn wording absent from live prose
withdrawn = {
    "R1/stromal-floor-demonstrated": "demonstrated by LRRC15",
    "R1/L2-heading": "the stromal floor demonstrated",
    "R1/reads-at-the-floor": "reads at the floor",
    "R2/removes-a-transcriptomic-rationale": "removes a transcriptomic rationale",
    "R2/removes-the-transcriptomic-case": "remove the\ntranscriptomic case",
    "R2/no-striking-absolute-signal": "no striking\nabsolute signal",
    "R2/cheap-decisive-measurement": "cheap decisive measurement",
    "R2/silent-there": "silent there",
    "R2/flat-in-magnitude": "flat in magnitude",
    "R2/PRAME-absent-normal-organs": "absent from normal organs",
    "R3/two-nested-sets": "Two nested sets",
    "R3/outside-the-stage-1-scan": "outside the stage-1 scan",
    "R3/surrogate-stage-never-evaluated": "surrogate stage never\nevaluated",
    "R3/absent-from-the-selectivity-scan": "absent from the\n**selectivity scan**",
    "R4/every-number-reproducible": "Every number in this manuscript is reproducible",
    "R4/sequencing-reductions-promise": "sequencing reductions from the retained grouped summaries",
    "R4/group-level-peak-summaries": "group-level peak summaries and not per-sample values",
    "R5/routinely-built-for-rare-tumours": "Surrogate-based target lists are routinely built",
    "R5/absent-from-previous-EMC": "absent from previous EMC",
    "R5/first-EMC-transcript-readings": "first EMC transcript readings",
}
for name, phrase in withdrawn.items():
    check("absent/" + name, phrase not in live_main and phrase not in live_si, "")

# ---- corrected wording present
present = {
    "R1/compatible-explanation": ("compatible explanation" in main_t.lower()
                                  or "explanation compatible" in main_t.lower()),
    "R1/FAP-culture-fractions": "0.16" in main_t and "0.56 detectable" in main_t,
    "R1/threshold-not-floor": "not a calibrated detector floor" in main_t and "not a calibrated\ndetector floor" in si_t or "not a calibrated detector floor" in si_t,
    "R1/line-authentication-separate": "is stated in Appendix A and is not merged into this one" in main_t,
    "R2/no-equivalence-test": "no equivalence test was performed" in main_t,
    "R2/half-width-not-per-gene": "does not determine any particular gene's interval" in main_t
                                  and "does not\ndetermine any particular gene's interval" in si_t,
    "R2/pooled-zero-not-absence": "not evidence that\nPRAME is absent from every contributing library or organ" in si_t,
    "R3/overlap-15": "overlap in 15 antigens and\nneither contains the other" in main_t,
    "R3/no-retained-selectivity-result": main_t.count("no retained selectivity result") >= 2
                                         and si_t.count("no retained selectivity result") >= 1,
    "R3/classic-scoped-intersection": "of the **classic subset**" in main_t
                                      and "contains DLL3" in main_t and "contains\nDLL3" in si_t,
    "R3/significant-decrease-is-negative": "a significant decrease is a measured negative contrast" in main_t,
    "R5/localised-to-programme": "prioritisation in this\nprogramme" in main_t,
    "R7/appendix-A8-register": "### Appendix A8" in main_t,
}
for name, ok in present.items():
    check("present/" + name, bool(ok), "")

# ---- nine-classic / 18-total flags preserved
check("R3-flags-preserved",
      "selectivity was significant for nine antigens" in main_t and "18 of the 47 were selectivity" in main_t,
      "nine classic and 18 total selectivity flags still stated")

# ---- R7: current pair identity, and the already-held source locator
for name, nb, h in [
    ("emc-surface-target-landscape.md", 146042,
     "371ec8d92c3238b09f2117e14613184c422db1f094e83f431bad07d46e93179e"),
    ("emc-surface-target-landscape-si.md", 56124,
     "290212776b2f103d64a270f12936245be00bfc6c97f5678b492589bc3680ad16"),
]:
    c = CANON / name
    r = REV / name
    check("R7-current-pair " + name,
          c.stat().st_size == nb and sha(c) == h and sha(r) == h,
          "%d B %s (canonical and candidate identical)" % (c.stat().st_size, sha(c)[:16]))

loc = LANE / "PST-source-locators/geo_esummary_emc.txt"
check("R7-esummary-locator",
      loc.exists() and loc.stat().st_size == 30740
      and sha(loc) == "1726d018625bd4d4afdadd9364a7447d650ae5c88e9a2c228fe4463845aaac0c",
      str(loc.relative_to(ROOT)))

# ---- F08 stays: the historical PNG is untouched
png = ROOT / "research/modalities/emc-surface-prioritization.png"
check("F08-original-png-untouched",
      sha(png) == "130042b6afab8aea28874d37dd684cde96886ab25b488ab65b83dac391c439bd",
      "historical bytes unchanged")
check("F08-figure-still-omitted",
      "**Figure 1.**" not in main_t, "no Figure 1 display item")

print()
print("%d passed, %d failed" % (TOTAL[0] - len(fails), len(fails)))
if fails:
    print("FAILED: " + ", ".join(fails))
sys.exit(1 if fails else 0)
