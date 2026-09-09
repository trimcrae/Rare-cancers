#!/usr/bin/env python3
"""Byte-level backward-compatibility proof.

Deletes ONLY the two new keys from the regenerated document and serialises what is left with the
same writer settings the detector uses. If the additive change touched nothing else, the result is
byte-for-byte the unpatched re-run (`census-baseline-unpatched.json`), whose own comparison against
the committed artifact showed 0 field differences.
"""
import hashlib, json, sys

NEW = ("y0", "y1")


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in NEW}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def ser(o):
    return json.dumps(o, indent=2, ensure_ascii=False).encode()


base = json.load(open(sys.argv[1]))
regen = json.load(open(sys.argv[2]))
b, s = ser(base), ser(strip(regen))
print("baseline_unpatched_bytes", len(b), hashlib.sha256(b).hexdigest())
print("regenerated_minus_y0y1  ", len(s), hashlib.sha256(s).hexdigest())
print("BYTE_IDENTICAL", b == s)

# cy must remain the midpoint the new fields imply, WITHIN THE RECORDING PRECISION. cy is
# round((y0+y1)/2, 1) of the raw floats, while y0/y1 are each rounded to 1 dp first, so the
# reconstructed midpoint can differ by up to 0.1 px by construction. That is a property of the
# 1 dp record the artifact already uses for cx/cy/w, not of this change. (A first run of this
# check used a 0.05 tolerance and reported 29 "mismatches"; that run is preserved under
# checks/08b-byte-identity-FAILED-tolerance and its finding was the tolerance, not the data.)
TOL = 0.1
bad = n = 0
worst = 0.0
for src in regen["sources"]:
    for f in src["figures"]:
        for bd in f.get("bands", []):
            for m in bd["marks"]:
                n += 1
                dev = abs(round(0.5 * (m["y0"] + m["y1"]), 1) - m["cy"])
                worst = max(worst, dev)
                if dev > TOL + 1e-9:
                    bad += 1
print("marks_checked", n, "cy_midpoint_deviations_over_%.2f" % TOL, bad,
      "worst_deviation_px", round(worst, 4))
sys.exit(0 if (b == s and bad == 0) else 1)
