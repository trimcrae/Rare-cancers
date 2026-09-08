import subprocess, sys, pathlib, difflib
SRC = pathlib.Path("research/manuscripts/nr4a3-program-map.md")
text = SRC.read_text(encoding="utf-8")
orig = text

REPL = [
("Q1 · roadmap V11 result — 'adequately powered' withdrawn",
 "*p* = 0.393 (DISCORDANT) · *p* = 0.747 (NULL, adequately powered)",
 "*p* = 0.393 (DISCORDANT) · *p* = 0.747 (NULL) — ⛔ **corrected 2026-09-08 (MF1 residual R1): NOT \"adequately powered\".** The attainable *p* floor 1/462 is a discreteness property of the exact reference set, **not statistical power**, and no effect size is established for this observable; the recorded fact is an **executed calibration attempt that did not meet its registered directional criterion**"),

("Q2 · roadmap V16 result — advance registration attributed, not asserted",
 "— its **preregistered null**, registered in advance as the LIKELY outcome and explicitly **not** a stop.",
 "— its **preregistered null**; ⚠ **corrected 2026-09-08 (MF1 residual R2): the retained protocol DESCRIBES it as registered in advance as the LIKELY outcome and explicitly not a stop — the actual chronology is unestablished.**"),

("Q3 · roadmap V16 scope_limit — bound and absent-wedge readings withdrawn",
 "⛔ **`S` may be read as a bound and may NOT be reported as calibrated** (Open decision 13). `S` is non-covalent and therefore **structurally incapable** of testing the categorical mechanism; `S ≈ 0` means the *marginal* wedge is absent, and STOP applies only if the categorical axis has ALSO failed",
 "⛔ **corrected 2026-09-08 (MF1 residual R1): `S` may NOT be read as a bound and may NOT be reported as calibrated.** Open decision 13's \"may be read as a bound\" is **withdrawn** (F02): the recorded uncertainty is a two-seed between-seed dispersion, not a confidence, equivalence or effect bound. `S` is non-covalent and therefore **structurally incapable** of testing the categorical mechanism. ⛔ **`S ≈ 0` does NOT mean the marginal wedge is absent** — an uncalibrated instrument returning ≈ 0 cannot separate \"no effect\" from \"cannot resolve\". STOP applies only if the categorical axis has ALSO failed"),

("Q4 · roadmap V20 scope_limit — universal no-downstream-recovery claim withdrawn",
 "⛔ nothing. A signal smaller than its own noise is not recoverable by any downstream method — [§6a](#6a--dead--conclusively-unworkable-never-retry)",
 "⛔ nothing beyond its own scope: **22 of 38 is a POSITIVE-CALL RATE among these selected decoys under this scoring configuration**, not a measured biological false-positive rate. ⛔ **Corrected 2026-09-08 (MF1 residual R1): the universal claim that \"a signal smaller than its own noise is not recoverable by any downstream method\" is WITHDRAWN** (F07), and no design class is excluded — [§6a](#6a--dead--conclusively-unworkable-never-retry)"),

("Q5 · roadmap :3246 dependency row — 'with a quantified bound' removed",
 "returned a preregistered null **with a quantified bound** — the design's recorded uncertainty is a two-seed between-seed dispersion —",
 "returned a preregistered null with **NO** quantified bound — ⛔ **corrected 2026-09-08 (MF1 residual R1): the preceding \"with a quantified bound\" wording is withdrawn**, and the design's recorded uncertainty is a two-seed between-seed dispersion —"),

("Q6 · roadmap :986 reading row — 'S ≈ 0 → the marginal wedge is absent' withdrawn",
 "| reading (fixed in advance) | **S ≈ 0 → the marginal wedge is absent.** Registered as the LIKELY outcome and NOT a stop |",
 "| reading (as the retained protocol describes it) | ⛔ **corrected 2026-09-08 (MF1 residual R1/R2): the reading \"S ≈ 0 → the marginal wedge is absent\" is WITHDRAWN** — an uncalibrated instrument returning ≈ 0 cannot separate \"no effect\" from \"cannot resolve\". ⚠ The retained protocol **describes** this outcome as registered in advance as the LIKELY one and NOT a stop; the chronology itself is unestablished |"),
]

fail = False
for name, old, new in REPL:
    n = text.count(old)
    print(f"{name}: OLD occurrences = {n}")
    if n != 1:
        print("  !! NOT UNIQUE — refusing", file=sys.stderr)
        fail = True
        continue
    text = text.replace(old, new, 1)
if fail:
    sys.exit(2)

a = orig.splitlines(keepends=True)
b = text.splitlines(keepends=True)
diff = "".join(difflib.unified_diff(
    a, b,
    fromfile="a/research/manuscripts/nr4a3-program-map.md",
    tofile="b/research/manuscripts/nr4a3-program-map.md",
    n=3))
out = pathlib.Path(sys.argv[1])
out.write_text(diff, encoding="utf-8")
print(f"wrote {out} ({len(diff.encode())} bytes)")
print("changed lines:", sum(1 for l in diff.splitlines() if l.startswith('+') and not l.startswith('+++')))
