#!/usr/bin/env python3
"""Pin the census target picker against the REAL path shapes, including the one that broke the shell version.

The shell first cut assumed `<prefix>/<phase>/iter-N/simulation.nc`. Production is
`<prefix>/<phase>/iter-N/<uuid>/simulation.nc` — a UUID directory in between — so its prefix-stripping matched
nothing and every object became its own "prefix". These paths are copied from the listing in GH run
30353268519, so the fixture is the reality that falsified the first implementation, not a restatement of it.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import ternary_census_targets as T  # noqa: E402

FAILS, RUN = [], []


def check(cond, msg):
    RUN.append(msg)
    if not cond:
        FAILS.append(msg)
    print(("  ok   " if cond else "  FAIL ") + msg)


S3 = [
    "ternary-vast/commits/calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_edge/production/iter-00000040/e2cd2250e0754a78a23d850fb7950cff/simulation.nc",
    "ternary-vast/commits/calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_edge/production/iter-00002000/bf0a4165492147ff93ce6530d0cfddaa/simulation.nc",
    "ternary-vast/commits/calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_edge/production/iter-00000280/856825dfa39b4d62a1a225407683aba1/simulation.nc",
    "ternary-vast/commits/calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_probe/production/iter-00000200/96960e6badbd4558834406740799fd9f/simulation.nc",
    "ternary-vast/commits/calib_hi_to_lo2__ternary_vhl_r0_dt2.0fs_wu1.0_triangle_smoke/production/iter-00000012/2e2d074384264eb988726e6a4f8ddcb9/simulation.nc",
    "ternary-vast/commits/calib_hi_to_lo__binary_vhl_r0_dt4.0fs_wu1.0_edge/warmup/iter-00001600/aaaa/simulation.nc",
]
# The GCP lane writes the same shape without the UUID level on some generations; both must work.
GCS = [
    "valB-6hax/commits/calib_hi_to_lo__ternary_vhl_0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000/simulation.nc",
    "valB-6hax/commits/calib_hi_to_lo__ternary_vhl_0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00000040/simulation.nc",
    "valB-6hax/commits/calib_hi_to_lo__ternary_vhl_0_dt4.0fs_clig0_wu1.0_pe1/production/iter-00000120/simulation.nc",
]

s3 = T.pick(S3, include=("ternary_vhl", "binary_vhl", "solvent"), exclude=("_smoke",))
check(len(s3) == 3, "S3 fixture groups into 3 commit prefixes (edge, probe, binary edge), not 6 objects")
edge = [v for k, v in s3.items() if k.endswith("_dt4.0fs_wu1.0_edge") and "ternary_vhl" in k]
check(len(edge) == 1 and "iter-00002000" in edge[0],
      "the NEWEST generation wins within a prefix (iter-2000, not iter-40 or iter-280)")
check(not any("triangle_smoke" in k for k in s3), "--exclude _smoke drops the triangle smoke prefix")

gcs = T.pick(GCS, include=("ternary_vhl",))
check(len(gcs) == 2, "the no-UUID GCS shape groups correctly too (2 prefixes)")
check(any("iter-00002000" in v for v in gcs.values()), "newest generation wins on the GCS shape as well")

# phase ordering: production beats warmup even at a smaller iteration index
both = T.pick([
    "p/x/warmup/iter-00001600/simulation.nc",
    "p/x/production/iter-00000040/simulation.nc",
], include=())
check(len(both) == 1 and "production" in list(both.values())[0],
      "production outranks warmup regardless of iteration index — a warmup snapshot is not the leg's result")

check(T.pick(["nonsense", "", "a/b/c.txt"]) == {},
      "junk lines yield nothing rather than a bogus target")


# --- LABEL UNIQUENESS: the bug that silently destroyed two measurements ---------------------------------------
# GH run 30353705917 labelled on the last path segment. The GCP layout is
# `valB-6hax/commits/<leg>/<seed>_dt…`, so the ternary, binary and solvent legs of ONE cycle all end in the
# same segment — three legs, one label, and each census overwrote the last. These are the real paths.
GCS_ONE_CYCLE = [
    "valB-6hax/commits/calib_hi_to_lo__ternary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000/simulation.nc",
    "valB-6hax/commits/calib_hi_to_lo__binary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000/simulation.nc",
    "valB-6hax/commits/calib_hi_to_lo__solvent/0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000/simulation.nc",
]
cyc = T.pick(GCS_ONE_CYCLE, include=("ternary_vhl", "binary_vhl", "solvent"))
check(len(cyc) == 3, "the three arms of one cycle are three distinct commit prefixes")
labels = [T.label_for(p) for p in cyc]
check(len(set(labels)) == 3,
      "and they get THREE DISTINCT LABELS — the last-segment label gave all three the same name and two "
      "censuses were silently overwritten")
check(all("calib_hi_to_lo__" in lab for lab in labels), "the label carries the leg id, not just the seed/dt dir")
check(T.label_for("valB-6hax/commits/calib_hi_to_lo__ternary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe")
      == "calib_hi_to_lo__ternary_vhl__0_dt2.0fs_clig0_wu1.0_v2pe",
      "everything after `commits/` is joined into the label")
check(T.label_for("ternary-vast/commits/calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_edge")
      == "calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_edge",
      "the Vast layout (leg id IS the last segment) is unchanged — which is why the bug showed on one store only")
check(T.label_for("no/commits/here/at/all"), "a prefix without a `commits` segment still yields a label")

print("\n%d checks, %d failures" % (len(RUN), len(FAILS)))
if FAILS:
    sys.exit(1)
print("test_ternary_census_targets: PASS")
