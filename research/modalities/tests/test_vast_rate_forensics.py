#!/usr/bin/env python3
"""The rate-forensics probe, pinned against the REAL records it was written to grade.

★ WHY THIS FILE IS MOSTLY MEASURED DATA. The question it settles is whether a Vast rental's charged rate can
rise after rental. That premise was about to justify giving the relaunch gate reach over LIVE hosts — killing
or migrating work already executing — which CLAUDE.md §6 explicitly forbids. A mechanism that powerful must
not rest on an inference, so the records below are the ones the live probe actually returned (run
30265697399, 2026-07-27 8:23 AM ET, four of six live instances) rather than constructed examples. If Vast's
billing model ever changes, these fixtures stop matching reality and the argument has to be re-made.

WHAT IS PINNED:
  1. `dph_total` is `dph_base + storage_total_cost`, and the `inet_*_cost` pair is NOT in it. Measured on
     every record. The first pass of the probe summed inet in and produced six UNKNOWNs; the residual came
     back as exactly minus the inet lines on all six, which is the answer rather than a coincidence.
  2. On the one instance with a recorded bid, the GPU line EQUALS that bid while the machine's `min_bid` has
     moved away from it — the market moved, the charged rate did not.
  3. The offer→instance gap is fully explained by floor→bid plus a disk line quoted for a smaller volume than
     the one rented. This is the actual mechanism behind "the rate rose".
  4. The probe never emits a credential. An allow-list, checked against the field names a real record carries.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)

from _skip_guard import skip_module    # noqa: E402

try:
    import vast_rate_forensics as F    # noqa: E402
except ImportError as e:               # pragma: no cover - env probe
    skip_module(f"needs vast_rate_forensics: {e}")

fails = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


# ---- the measured records (run 30265697399, 2026-07-27 8:23 AM ET) -------------------------------------
# Allow-listed fields only, exactly as the probe printed them. Note what is NOT here: the same API response
# carries `jupyter_token`, `ssh_host`, `ssh_port` and `public_ipaddr`, and none of them reached the output.
LIVE = [
    # the step-1 fan-out shakeout, running at 96 % GPU, rented 20 min earlier at a recorded bid of $0.1805
    dict(id=46000463, machine_id=55559, label="s1f-02-cw_ev_5cooh", gpu_name="RTX 4090", disk_space=80.0,
         is_bid=True, cur_state="running", dph_base=0.1805, dph_total=0.20272222222222222,
         storage_cost=0.19999999999999998, storage_total_cost=0.02222222222222222,
         inet_up_cost=0.00390625, inet_down_cost=0.00390625, min_bid=0.1733333, gpu_util=95.999908),
    # The probe reported this one's inet as a single combined $0.0026041666666666665/hr; the up/down split is
    # not recoverable from that line, so it is carried on one field rather than invented across two.
    dict(id=45751606, machine_id=55547, is_bid=True, dph_base=0.22666666666666668,
         dph_total=0.23185185185185186, storage_total_cost=0.005185185185185185,
         inet_up_cost=0.0026041666666666665, min_bid=0.1666667),
    dict(id=45751616, machine_id=43503, gpu_name="RTX 3090", disk_space=40.0, is_bid=True,
         dph_base=0.10666666666666667, dph_total=0.15481481481481482,
         storage_cost=0.8666666666666666, storage_total_cost=0.04814814814814815,
         inet_up_cost=0.016927083333333332, inet_down_cost=0.015625, min_bid=0.09333333),
    dict(id=45751620, machine_id=109523, gpu_name="L4", disk_space=40.0, is_bid=True,
         dph_base=0.32, dph_total=0.3459259259259259,
         storage_cost=0.46666666666666673, storage_total_cost=0.02592592592592593,
         inet_up_cost=0.013020833333333334, inet_down_cost=0.013020833333333334, min_bid=0.2666667),
]

# The ledger row the fan-out recorded when it rented 46000463 (launch readout, 2026-07-27 8:00 AM ET:
# "instance 46000463 machine 55559 dph≈$0.1792222222222222/hr (floor $0.177/hr -> bid $0.1805/hr)").
LEDGER_46000463 = {"bid": 0.1805, "min_bid": 0.177, "dph": 0.1792222222222222}


print("== dph_total = dph_base + storage_total_cost, on every measured record")
for r in LIVE:
    d = F.decompose(r)
    check(d["explained"] and abs(d["residual_usd_h"]) < 1e-9,
          f"instance {r['id']}: ${d['gpu_usd_h']:.6f} GPU + ${d['storage_usd_h']:.6f} storage = "
          f"${d['all_in_usd_h']:.6f} total, residual {d['residual_usd_h']}")

print("== ...and the inet lines are NOT part of that total (the first pass of the probe assumed they were)")
r = LIVE[2]                                          # the largest inet lines of the four
d = F.decompose(r)
check(d["inet_usd_h_not_in_total"] > 0.03,
      "this record carries a substantial inet figure, so its exclusion is a real test and not a vacuous one")
check(abs(d["all_in_usd_h"] - (d["gpu_usd_h"] + d["storage_usd_h"])) < 1e-9,
      "the total closes WITHOUT it — adding inet in would have made the residual non-zero")

print("== the charged GPU rate has NOT moved from the bid agreed at rental")
moved, doc = F.verdict(LIVE[0], LEDGER_46000463["bid"])
check(moved is False, "verdict on the live shakeout host is NO MOVE, and it is graded rather than UNKNOWN")
check(doc["gpu_minus_bid_usd_h"] == 0.0,
      "dph_base equals the recorded bid EXACTLY ($0.1805), not merely within tolerance")
check(doc["hypothesis_supported"].startswith("H2"),
      "the two-different-quantities hypothesis is the one the record supports")

print("== the SECOND discriminator: the market moved and the charged rate did not")
# If the charged rate tracked the market, an instance whose machine's floor has moved since rental would show
# dph_base moving with it. This machine's floor fell from $0.177 (at rental) to $0.1733333 (20 min later)
# while dph_base stayed at the bid. One record, two independent ways of being wrong, neither of them taken.
check(abs(float(LIVE[0]["min_bid"]) - LEDGER_46000463["min_bid"]) > 1e-3,
      "the machine's floor DID move between rental and this read — so the test is not vacuous")
check(abs(F.decompose(LIVE[0])["gpu_usd_h"] - LEDGER_46000463["bid"]) < 1e-9,
      "...and the GPU line did not follow it")

print("== an instance with no recorded bid is UNKNOWN, never 'no move'")
moved, doc = F.verdict(LIVE[1], None)
check(moved is None and "UNKNOWN" in doc["verdict"],
      "an ungradeable rental is reported as ungradeable — absence of evidence is not evidence of absence")

print("== the offer -> instance gap is FULLY explained by floor->bid plus the disk line")
ov = F.offer_vs_instance(LIVE[0], LEDGER_46000463)
check(ov["fully_explained"], "the apparent rise decomposes exactly, with nothing left over")
check(abs(ov["apparent_rise_usd_h"] - 0.0235) < 1e-6,
      f"apparent rise ${ov['apparent_rise_usd_h']}/hr (offer $0.17922 -> instance $0.20272)")
check(abs(ov["explained_by"]["floor_to_bid_usd_h"] - 0.0035) < 1e-6,
      "$0.0035/hr of it is our own bid premium over the floor")
check(abs(ov["explained_by"]["disk_line_growth_usd_h"] - 0.0200) < 1e-6,
      "$0.0200/hr of it is the disk line, quoted small in the search and billed at the real volume")
check(abs(ov["disk_line_ratio_instance_over_offer"] - 10.0) < 1e-6 and ov["offer_disk_gb_implied"] == 8.0,
      "the search priced 8 GB against the 80 GB actually rented — a 10.0x under-quote of the storage line")

print("== the probe cannot emit a credential")
row = F.safe_row(dict(LIVE[0], jupyter_token="SECRET", ssh_host="1.2.3.4", ssh_port=40100,
                      public_ipaddr="5.6.7.8", local_ipaddrs="10.0.0.1"))
for leaked in ("jupyter_token", "ssh_host", "ssh_port", "public_ipaddr", "local_ipaddrs"):
    check(leaked not in row, f"{leaked} is not in the allow-listed view")
check("SECRET" not in repr(row) and "1.2.3.4" not in repr(row),
      "...and no credential VALUE appears anywhere in the emitted row")
check(row["dph_base"] == 0.1805 and row["machine_id"] == 55559,
      "the price and identity fields that ARE evidence survive — this is an allow-list, not a blanket redaction")
check(all(k in F.SAFE_FIELDS for k in row),
      "every emitted key is on the allow-list, so a field Vast adds tomorrow is excluded by default")

print("== a rate this module cannot account for is refused, not rationalised")
bogus = dict(LIVE[0], dph_total=0.5)                 # a total the named lines do not sum to
moved, doc = F.verdict(bogus, LEDGER_46000463["bid"])
check(moved is None and "UNKNOWN" in doc["verdict"],
      "an unexplained total yields UNKNOWN — no drift conclusion is drawn from a number that does not close")

print("== ★ THE UNDER-QUOTE MUST NOT REACH THE PURCHASE DECISION")
# The serious version of the same defect. A wrong rate in a readout misleads a reader; the same rate inside
# the $/ns gate would approve every rental against a number below its true one. These offers are shaped like
# the live board of 2026-07-27 12:45 PM UTC: a cheap-storage host and an expensive-storage one, where the
# quote's fixed-size disk line hides a per-machine storage cost that differs by 4.5x.
try:
    import congeneric_fanout_vast as _cfv                      # noqa: E402
    _RES = _cfv.FANOUT_RES
except ImportError:                                            # pragma: no cover
    _RES = None

if _RES is None:
    check(True, "(skipped: congeneric_fanout_vast not importable in this env)")
else:
    def _offer(mid, min_bid, storage_cost):
        # dph_total as the SEARCH quotes it: the floor plus a disk line for a disk we do not rent.
        return dict(id=mid, machine_id=mid, gpu_name="RTX 4090", num_gpus=1, gpu_ram=24600, rentable=True,
                    reliability2=0.99, cuda_max_good=13.0, min_bid=min_bid, dph_base=min_bid,
                    dph_total=round(min_bid + storage_cost * 8 / 720.0, 6), storage_cost=storage_cost,
                    disk_space=200, cpu_ram=64000, cpu_cores=16)

    board = [_offer(101, 0.16, 0.20), _offer(102, 0.19, 0.90)]
    rp = F.reprice(res=_RES, n_fleet=2, offers=board, readout_path=os.devnull)
    check(all(r["gate_usd_per_ns"] > r["quote_usd_per_ns"] for r in rp["rows"]),
          "the gate's $/ns is ABOVE the quote's on every offer — it is not consuming the quote")
    check("NOT READING THE QUOTE" in rp["verdict"], "and the verdict says so in those terms")
    check(rp["quote_understates_gate_by_pct"]["max"] > rp["quote_understates_gate_by_pct"]["min"],
          "the under-read is NOT a constant offset — it scales with the machine's own storage_cost, "
          "which is why a flat correction would not have fixed it")
    # The row that matters: cheap GPU, expensive disk. The quote says buyable, the true rate says no.
    expensive_disk = [r for r in rp["rows"] if r["machine_id"] == 102][0]
    check(expensive_disk["understated_by_pct"] > 30,
          "a high-storage_cost host is understated by >30 % — the worst case, and invisible on the quote")

print("== ...and a board with nothing priceable is UNKNOWN, not a clean bill of health")
if _RES is not None:
    empty = F.reprice(res=_RES, n_fleet=2, offers=[], readout_path=os.devnull)
    check("UNKNOWN" in empty["verdict"] and "not a clean bill of health" in empty["verdict"],
          "no priceable offer cannot be reported as 'the gate is fine' — the same discipline the gate "
          "applies to an unreadable market")

print("== a short fleet says it is short rather than quoting a mean whose name is a lie")
if _RES is not None:
    short = F.reprice(res=_RES, n_fleet=19, offers=board, readout_path=os.devnull)
    check("fleet_mean_is_short" in short["gate_derived"],
          "2 priceable offers against 19 units is flagged, not averaged into a 'best19 mean'")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all vast rate-forensics tests passed")
