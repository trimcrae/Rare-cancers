#!/usr/bin/env python3
"""Unit tests for the LANE-13 categorical-dynamics lane (pure helpers only — no network, no GPU, no MD).

The load-bearing pieces are exactly the ones a wrong answer would be invisible in:
  * `coverage_probability` replaces a Monte-Carlo sampler with a closed form, so if it is wrong every
    per-conformer term-(b) number is wrong and nothing complains;
  * `dcd_n_frames` decides how much metadynamics still has to run on a RESUME, so if it over-reports, biased
    sampling is silently skipped, and if it errors it must return 0 (re-run work) rather than a wrong count;
  * `build_jobspec` fixes every parameter that keys the S3 checkpoint prefix, and the empty-string-input hole
    (`os.environ.get(k, default)` where CI passes "") has already cost this repo one rented host that would
    have uploaded to `s3:///`.
"""
import math
import os
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import nr4a_paralogue_dynamics as P     # noqa: E402
import nr4a_paralogue_md_job as J       # noqa: E402
import nr4a_paralogue_md_vast_launch as L  # noqa: E402

fails = []


def check(cond, msg):
    if cond:
        print(f"  ok   {msg}")
    else:
        print(f"  FAIL {msg}")
        fails.append(msg)


print("== lens_volume / coverage_probability")
# containment: the mobility ball entirely inside the transfer ball -> probability 1
check(abs(P.lens_volume(8.0, 17.09, 0.0) - 4 / 3 * math.pi * 8.0 ** 3) < 1e-6, "r=0 -> whole mobility ball")
check(P.coverage_probability(0.0, 8.0, 17.09, 48) == 1.0, "r=0 -> covered with probability 1")
# disjoint: beyond mobility + transfer nothing can reach
check(P.lens_volume(8.0, 17.09, 25.1) == 0.0, "r > R+d -> empty lens")
check(P.coverage_probability(30.0, 8.0, 17.09, 48) == 0.0, "far lysine never covered")
# monotone non-increasing in r
prev = 1.1
mono = True
for r in [x * 0.5 for x in range(0, 70)]:
    p = P.coverage_probability(r, 8.0, 17.09, 48)
    mono = mono and p <= prev + 1e-12
    prev = p
check(mono, "coverage is monotone non-increasing in distance")
# zero mobility degenerates to the hard cutoff the sampler uses when mob == 0
check(P.coverage_probability(17.0, 0.0, 17.09, 48) == 1.0, "mob=0 inside cutoff -> 1")
check(P.coverage_probability(17.2, 0.0, 17.09, 48) == 0.0, "mob=0 outside cutoff -> 0")
# and it must agree with the committed Monte-Carlo sampler
v = P.validate_coverage(n_trials=1500, seed=3)
check(v["passes"], f"analytic == transfer_zone Monte Carlo (max |diff| {v['max_abs_diff']})")

print("== wilson95")
lo, hi = P.wilson95(72, 75)
check(lo < 72 / 75 < hi and hi <= 1.0, f"72/75 interval brackets the point estimate ({lo}, {hi})")
check(P.wilson95(0, 0) is None, "n=0 -> None rather than a divide-by-zero")

print("== quantiles")
q = P.quantiles([1, 2, 3, 4, 5])
check(q["median"] == 3 and q["n"] == 5 and q["min"] == 1 and q["max"] == 5, "quantiles on a known list")
check(P.quantiles([]) == {}, "empty -> {}")

print("== dcd_n_frames")
with tempfile.TemporaryDirectory() as td:
    good = os.path.join(td, "g.dcd")
    with open(good, "wb") as fh:
        fh.write(struct.pack("<i", 84) + b"CORD" + struct.pack("<i", 1234) + b"\x00" * 4)
    check(J.dcd_n_frames(good) == 1234, "reads the frame count from a little-endian DCD header")
    bad = os.path.join(td, "b.dcd")
    with open(bad, "wb") as fh:
        fh.write(b"not a dcd file at all")
    check(J.dcd_n_frames(bad) == 0, "non-DCD -> 0 (re-run work, never skip it)")
    check(J.dcd_n_frames(os.path.join(td, "missing.dcd")) == 0, "missing file -> 0")

print("== metad_done_ns takes the MAX of manifest and trajectory")
with tempfile.TemporaryDirectory() as td:
    open(os.path.join(td, "metad_manifest.json"), "w").write('{"cumulative_ns": 20.0}')
    with open(os.path.join(td, "nr4a3-lbd-metad.dcd"), "wb") as fh:
        fh.write(struct.pack("<i", 84) + b"CORD" + struct.pack("<i", 900) + b"\x00" * 4)
    # 900 frames x 50 ps = 45 ns, which is MORE than the manifest's 20 ns (an interrupted segment advances
    # the trajectory but never writes the manifest) — the larger value must win or the resume redoes 25 ns.
    check(abs(J.metad_done_ns(td) - 45.0) < 1e-9, "interrupted segment: trajectory beats a stale manifest")

print("== build_jobspec")
os.environ.pop("VAST_CKPT_BUCKET", None)
s = L.build_jobspec("NR4A1", mode="real", metad_ns=60, release_ns=5, n_rep=3, git_branch="br")
check(s.name == "nr4a-pdyn-nr4a1", "leg name derives from the target")
check(s.checkpoint_uri.startswith(f"s3://{L.DEFAULT_BUCKET}/"), "checkpoint URI carries a real bucket")
check(s.resume is True, "resume on by default (spot-safe)")
check(s.env["METAD_NS"] == "60" and s.env["RELEASE_NS"] == "5" and s.env["N_REP"] == "3",
      "the ns/replica parameters reach the host env")
check(s.env["GIT_BRANCH"] == "br", "the branch the host pulls code from is explicit")
check("s3:///" not in s.env["RESULT_S3"], "no empty-bucket URI")
os.environ["VAST_CKPT_BUCKET"] = ""      # CI passes a blank optional input as an EMPTY STRING
s2 = L.build_jobspec("NR4A2")
check("s3:///" not in s2.env["RESULT_S3"] and L.DEFAULT_BUCKET in s2.env["RESULT_S3"],
      "an EMPTY-STRING bucket env falls back to the default rather than producing s3:///")
os.environ.pop("VAST_CKPT_BUCKET", None)
sm = L.build_jobspec("NR4A1", mode="smoke")
check(float(sm.env["METAD_NS"]) < 1 and sm.name.endswith("-smoke"),
      "smoke runs the whole chain at toy length under its own name")
check(sm.max_runtime_s <= 3600 < s.max_runtime_s, "the anti-idle cap is scaled to the mode")

print("== ops leg naming / smoke segregation")
import nr4a_paralogue_md_ops as O  # noqa: E402
names = O.leg_names("NR4A1,NR4A2")
check(names == ["nr4a-pdyn-nr4a1", "nr4a-pdyn-nr4a1-smoke",
                "nr4a-pdyn-nr4a2", "nr4a-pdyn-nr4a2-smoke"],
      "leg_names covers both the real and the smoke prefix (a board that knew only the real name "
      "reported 'no phase yet' for a leg running at 60 % GPU)")
check(O.target_of("nr4a-pdyn-nr4a1-smoke") == "nr4a1" and O.target_of("nr4a-pdyn-nr4a2") == "nr4a2",
      "target_of survives the -smoke suffix (a bare rsplit returns 'smoke')")
check(O.result_key("nr4a-pdyn-nr4a1-smoke").endswith("nr4a-pdyn-nr4a1-smoke/nr4a1-pocket-ensemble.tar.gz"),
      "the smoke tarball has the SAME basename as the real one under a DIFFERENT prefix — which is exactly "
      "why collect must skip it rather than unpack it over the real ensemble")
# REGRESSION, 2026-07-26. leg_names() synthesises a -smoke name per target whether or not a smoke leg was ever
# launched, so a phantom's progress signature (None, None, False) can never change. The stall detector fired on
# it and KILLED the watch at 00:28:55Z while both real legs advanced at 60-69 % GPU util — leaving two billed
# legs with no session-independent monitoring. real_done already excluded smoke legs; the stall test did not.
check(O.watched_for_stalls("nr4a-pdyn-nr4a1") and not O.watched_for_stalls("nr4a-pdyn-nr4a2-smoke"),
      "a never-launched smoke leg is frozen BY DEFINITION and must never be the reason the watch fails")

print("== species offsets are derived, not hardcoded")
try:
    import json
    import nr4a3_basin_search as B
    seqs = json.load(open(os.path.join(HERE, "..", "nr4a-sequences-cache.json")))
    for sp, want in (("NR4A3", 372), ("NR4A1", 347), ("NR4A2", 343)):
        m = B.load_paralogue(P.STATIC_MODEL[sp])
        check(P.species_offset(m, sp, seqs) == want, f"{sp} local->UniProt offset == {want}")
except FileNotFoundError as e:
    print(f"  SKIP structural checks: {e}")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all paralogue-dynamics unit tests passed")
