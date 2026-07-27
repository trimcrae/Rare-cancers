#!/usr/bin/env python3
"""THE CALIBRATION SWEEP — the only route by which a new card may enter `MEASURED_NS_PER_DAY_84K`.

★ THE PROBLEM, MEASURED ON THE LIVE BOARD (2026-07-27 8:00 AM ET, `step1-fanout-market-hold.json`):

      offers_returned: 48 · qualifying: 48 · **priceable: 10** · needed: 19

Every one of those 48 offers passed the launcher's hard filters and was then dropped at the last step, because
`$/ns` needs a benched `ns/h` and the table holds three cards. We are not short of SUPPLY; we are short of the
ability to GRADE it. `vast_board_census` quantifies the cost of that (the break-even each unbenched card would
have to clear to be worth a bench) and owns the shortlist. **This module is the other half: it turns a
shortlisted card into a MEASUREMENT, or reports honestly that it could not.**

===============================================================================================================
1. THE PROTOCOL — and why "the same protocol" is the whole scientific content of this file
===============================================================================================================
`MEASURED_NS_PER_DAY_84K` is not "how fast is this GPU". It is a specific number produced by a specific run:

    gpu_md_bench.py, BENCH_EDGE_NM=9.5  ->  a cubic TIP3P water box of exactly 84,534 particles
    amber14/tip3p.xml · PME · 1.0 nm cutoff · HBonds constraints · hydrogenMass 4 amu (HMR)
    LangevinMiddleIntegrator 300 K / 1 ps^-1 / dt = 4 fs · CUDA platform, mixed precision
    minimizeEnergy(maxIterations=200) -> 1000 warmup steps (discarded) -> probe -> 3 independent timed blocks
    sized to ~60 s total (BENCH_TARGET_S=60, BENCH_BLOCKS=3), each block reported separately

VERIFIED, not asserted: every anchor's per-block numbers are recorded in `throughput-bench-provenance.json`,
and `tests/test_throughput_provenance.py` recomputes each mean and CV from those blocks and asserts they equal
the table entry. So the anchors are now DERIVED FROM THEIR OWN EVIDENCE rather than typed (CLAUDE.md §1.1), and
no number in this file, this docstring or that JSON is a second copy of a throughput.

★ A NUMBER OBTAINED ANY OTHER WAY IS A DIFFERENT QUANTITY AND MAY NOT SIT IN THE SAME COLUMN. Not a stylistic
preference — the table is divided into `$/ns`, so mixing two quantities silently rescales every purchase
decision and the ladder basis with it. `admit()` below is the gate, and it refuses on protocol identity
(particle count, timestep, platform, block count, block DURATION) before it looks at the number at all.

Two of those gates encode incidents rather than taste:
  * **BLOCK DURATION.** The 2026-07-24 23:08 grid was WITHDRAWN because every timed window was 0.9-4.5 s, which
    measures boost-clock ramp and kernel-launch overhead — it ranked an RTX 4080 SUPER *above* a 4090. So a
    record whose mean block is shorter than `MIN_BLOCK_S` is refused however clean it looks.
  * **DEVICE IDENTITY.** In the same grid a leg fell back to a Quadro RTX 8000 and was tabulated as an A10.
    `require_gpu=True` now makes the card a HARD constraint at selection, and `admit()` additionally requires
    the CUDA device string, the marketplace `gpu_name` and the requested model to normalise to ONE key. A
    disagreement is refused, not reconciled.

===============================================================================================================
2. WHY A DEDICATED RENTAL, WHEN WE ALREADY RENT THESE CARDS EVERY DAY
===============================================================================================================
The obvious cheaper idea — harvest throughput from production legs we have already paid for — was evaluated
first and does not work. The evidence is in `throughput_harvest.py`, which implements the harvest anyway for
what it CAN do; the one-line reason it cannot fill this table is a closed loop:

    an unbenched card has no $/ns  ->  `rank_offers_by_usd_per_ns` sorts it after every benched offer
      ->  `_select_cheapest_offer` returns `measured[0]` whenever anything benched qualifies
      ->  we never rent it  ->  it never produces a log  ->  it stays unbenched

Measured, not argued: 95 instance-observations across the 53 committed fan-out ticks (2026-07-24 -> 2026-07-27)
contain exactly THREE distinct card models — RTX 4090, RTX 4080S, RTX 3090 — every one already in the table,
while the same board carries 20+ models. **A dedicated rental is the only thing that breaks the loop.**

===============================================================================================================
3. THE SPEND GATE — a dollar ceiling, and why it is NOT the `$/ns` gate
===============================================================================================================
CLAUDE.md §6 gates every rental on `$/ns` against the ladder basis. **That gate cannot be applied here, and
saying so is more honest than pretending otherwise: `$/ns` requires the card's ns/h, which is the very thing
this rental exists to measure.** Applying it would be circular — and applying it with the card's throughput
unknown is exactly the fabrication the whole lane is built to avoid.

So a calibration rental is gated on the quantity that IS knowable in advance and is bounded by construction:

    worst-case cost = (bid + storage) x max_runtime_h        # the rental cannot cost more; it self-terminates

with a per-card ceiling (`MAX_USD_PER_CARD`) and a sweep-wide ceiling (`MAX_USD_TOTAL`) that the planner
accumulates against and stops at. The ceilings are checked BEFORE anything is rented, against the offer we
would actually take, so a hold is visible in the plan rather than discovered on a bill.

★ AND THE INFORMATION SIDE IS GATED TOO, by `vast_board_census`: a card is only worth benching if its cheapest
offer's BREAK-EVEN ns/day is plausibly achievable. That screen is imported, never re-derived — a break-even is
a screen and must never become a throughput.

★ ONE MORE CONSTRAINT THAT IS EASY TO MISS: **bench only on hosts that pass the PRODUCTION filters.** A number
measured on a host we could never rent for real work is worthless, so the sweep uses the same `min_cuda`,
`min_reliability` and single-GPU constraints the fan-out uses. Fewer candidate hosts; usable answers.

===============================================================================================================
4. WHAT THIS FILE DELIBERATELY DOES NOT DO
===============================================================================================================
* It does not hold a throughput table. `vast_cost_model.MEASURED_NS_PER_DAY_84K` is THE table; `admit()`
  returns a PROPOSED entry plus its provenance record, and a human edit + a passing provenance test is what
  puts it in. A second table is precisely how a withdrawn 669 ns/day survived for a day.
* It does not touch the three anchors. `tests/test_throughput_provenance.py` pins them bit-identically,
  including `REFERENCE_NS_PER_H`.
* It does not guess. A card that cannot be rented, whose bench fails its physics check, or whose blocks scatter
  past `MAX_CV` stays UNKNOWN and is excluded from ranking — the correct behaviour, not a bug.

Modes (env flags, matching the other launchers):
    PLAN=1     — pure/read-only: which cards, at what worst-case cost, admitted or held and why
    LAUNCH=1   — rent the admitted cards (needs VAST_API_KEY); one instance per card, minutes each
    COLLECT=1  — read the bench records back, validate, print proposed table entries + provenance
    RECORD=1   — ON-HOST: parse gpu_md_bench's output line into a record and upload it
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vast_cost_model as _vcm  # noqa: E402
import vast_board_census as _census  # noqa: E402
from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
BUCKET = os.environ.get("VAST_CKPT_BUCKET", "")
RESULT_PREFIX = os.environ.get("BENCH_RESULT_PREFIX", "vast-bench-calibration")
LABEL_PREFIX = "cal-"
PROVENANCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "throughput-bench-provenance.json")

# The OpenFE image the production lane runs. Chosen deliberately over a bespoke bench image: the bench must
# measure the CUDA/OpenMM build the SCIENCE runs on, or its ns/day prices a stack we do not use.
FEP_IMAGE = os.environ.get("FEP_IMAGE") or "docker.io/triskit23/nr4a3fep:latest"

# ---- the protocol, as constants, so `admit()` and the launcher cannot disagree about it --------------------
BENCH_EDGE_NM = "9.5"          # -> 84,534 particles; the size the three anchors were measured at
BENCH_ATOMS = 84534            # EXACT: addSolvent is deterministic for a fixed box + force field
BENCH_DT_FS = 4.0
BENCH_BLOCKS = 3
BENCH_TARGET_S = 60
BENCH_WARMUP = 1000

# Admission thresholds. Each one is an incident, not a taste — see the module docstring.
MAX_CV = 0.05          # the validated grid rejected a contended host at CV 18.5 %; its worst keeper was 1.31 %
MIN_BLOCK_S = 10.0     # the withdrawn grid's blocks were 0.9-4.5 s; ~20 s is what BENCH_TARGET_S/3 delivers
MIN_BLOCKS = 3

# Spend ceilings. A bench is minutes, so these are deliberately small — they are a brake, not a budget.
MAX_RUNTIME_S = int(os.environ.get("BENCH_MAX_RUNTIME_S", "1800"))     # 30 min hard cap per rental
MAX_USD_PER_CARD = float(os.environ.get("BENCH_MAX_USD_PER_CARD", "0.60"))
MAX_USD_TOTAL = float(os.environ.get("BENCH_MAX_USD_TOTAL", "5.00"))
BENCH_DISK_GB = int(os.environ.get("BENCH_DISK_GB", "40"))

# Hosts we bench on must be hosts we could actually RUN on, or the number prices a machine we cannot buy.
BENCH_RES = ResourceSpec(gpu="", min_vram_gb=int(os.environ.get("BENCH_MIN_VRAM_GB", "16")),
                         vcpus=4, ram_gb=16, disk_gb=BENCH_DISK_GB, interruptible=True,
                         require_gpu=True)


# =============================================================================================================
# PURE — the admission gate
# =============================================================================================================
def parse_bench_line(line):
    """`gpu_md_bench`'s single `BENCH_RESULT ...` line -> a dict. PURE.

    The line is space-separated `k=v`, so ANY VALUE CONTAINING A SPACE IS TRUNCATED AT THE FIRST SPACE — which
    is how `device='Quadro RTX 8000'` arrived as `device='Quadro'` in 2026-07-24. `gpu_md_bench` underscores
    the device name for that reason; this parser restores the spaces so the name can be normalised."""
    out = {}
    for kv in str(line or "").split():
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[k] = v
    for k in ("device",):
        if k in out:
            out[k] = out[k].replace("_", " ").strip()
    for k in ("ns_per_day", "cv", "sd", "wall_s", "dt_fs", "final_temp_k"):
        if k in out:
            try:
                out[k] = float(out[k])
            except (TypeError, ValueError):
                pass
    for k in ("atoms", "steps", "blocks"):
        if k in out:
            try:
                out[k] = int(out[k])
            except (TypeError, ValueError):
                pass
    if "blocks_ns_day" in out:
        try:
            out["blocks_ns_day"] = [float(x) for x in str(out["blocks_ns_day"]).split(",") if x != ""]
        except (TypeError, ValueError):
            pass
    out["healthy"] = str(out.get("healthy", "")).lower() == "true"
    return out


# ★★ DEVICE-NAME EQUIVALENCES — an ALLOW-LIST, because the alternative loosens the 4090D guard (2026-07-27)
#
# THE FALSE NEGATIVE. The identity check requires the marketplace name, the requested model and the CUDA
# device string to resolve to one card by a SUFFIX-anchored match (a vendor PREFIX is free, a trailing
# qualifier is a different SKU). That is right for `RTX 4090` vs `RTX 4090 D`, and wrong for these:
#
#     requested "A100 PCIE"     CUDA device "NVIDIA A100 80GB PCIe"       <- capacity token in the MIDDLE
#     requested "RTX PRO 4000"  CUDA device "NVIDIA RTX PRO 4000 Blackwell" <- architecture token at the END
#
# Both are the same silicon under two naming conventions, and both were refused — costing two admissible
# measurements, including the A100, which is exactly the fast-tier card the sweep exists to settle.
#
# WHY NOT A SMARTER HEURISTIC. The obvious fix is token containment: accept when every token of the requested
# name appears in the device name. It is wrong, and dangerously so — NVIDIA's own string for the cut-down SKU
# is "NVIDIA GeForce RTX 4090 D", whose tokens are a strict SUPERSET of "RTX 4090". Token containment would
# admit a 4090D as a 4090, which is the precise anti-conservative failure the suffix rule was written to stop.
#
# So the equivalence is an explicit, human-checked allow-list keyed on the exact normalised CUDA string, in the
# same spirit as `vast_cost_model.CONSERVATIVE_ALIASES`. Anything not listed FAILS CLOSED and is refused.
DEVICE_NAME_EQUIVALENCES = {
    # normalised CUDA device string : the normalised marketplace/table key it names
    "NVIDIAA10080GBPCIE": "A100PCIE",           # A100 80GB PCIe — capacity+bus tokens, same GA100 part
    "NVIDIAA10040GBPCIE": "A100PCIE",           # the 40GB PCIe variant reports the same way
    "NVIDIARTXPRO4000BLACKWELL": "RTXPRO4000",  # marketplace drops the architecture word
    "NVIDIARTXPRO4500BLACKWELL": "RTXPRO4500",
    "NVIDIARTXPRO5000BLACKWELL": "RTXPRO5000",
    "NVIDIARTXPRO6000BLACKWELLWORKSTATIONEDITION": "RTXPRO6000WS",
}


def _card_keys(rec):
    """Every name in the record that claims to say WHICH CARD ran, normalised. PURE."""
    out = {}
    for k in ("device", "offer_gpu_name", "gpu_requested"):
        if not rec.get(k):
            continue
        n = _vcm.normalise_gpu_name(rec.get(k))
        out[k] = DEVICE_NAME_EQUIVALENCES.get(n, n)
    return out


def admit(rec):
    """(ok, reasons, entry) — may this record become a `MEASURED_NS_PER_DAY_84K` entry? PURE.

    `entry` is `(table_key, ns_per_day)` on success and None otherwise. EVERY refusal is returned, not just the
    first, because a launcher reading one refusal fixes one thing and re-rents.

    The order is deliberate: PROTOCOL IDENTITY first, then physics, then stability, then the number. A record
    that measured a different quantity is not "a noisy measurement of ours" — it is not a measurement of ours
    at all, and looking at its value first is how a different quantity gets averaged into the table."""
    bad = []

    # --- protocol identity ---------------------------------------------------------------------------------
    if rec.get("atoms") != BENCH_ATOMS:
        bad.append(f"particle count {rec.get('atoms')} != {BENCH_ATOMS} — a different system, not a different host")
    if abs(float(rec.get("dt_fs") or 0) - BENCH_DT_FS) > 1e-9:
        bad.append(f"timestep {rec.get('dt_fs')} fs != {BENCH_DT_FS} fs — ns/day is not comparable across dt")
    if str(rec.get("platform")) != "CUDA":
        bad.append(f"platform {rec.get('platform')!r} != 'CUDA' — an OpenCL or CPU run prices a stack we never use")
    blocks = int(rec.get("blocks") or 0)
    if blocks < MIN_BLOCKS:
        bad.append(f"{blocks} timed block(s) < {MIN_BLOCKS} — a single window cannot separate a steady host "
                   f"from a contended one")
    wall = float(rec.get("wall_s") or 0.0)
    if blocks > 0 and wall / blocks < MIN_BLOCK_S:
        bad.append(f"mean block {wall / max(1, blocks):.1f}s < {MIN_BLOCK_S}s — at that duration you measure "
                   f"boost-clock ramp and kernel launches (the WITHDRAWN 2026-07-24 grid)")

    # --- device identity: the requested card, the marketplace card and the CUDA device must be ONE card -----
    keys = _card_keys(rec)
    resolved = {}
    for src, norm in keys.items():
        hit = None
        for k in sorted(set(_vcm.MEASURED_NS_PER_DAY_84K) | set(_vcm.CONSERVATIVE_ALIASES) | {norm},
                        key=len, reverse=True):
            if norm.endswith(k):
                hit = k
                break
        resolved[src] = hit or norm
    if not keys:
        bad.append("no device name recorded — cannot attribute a throughput to a card")
    elif len({v for v in resolved.values()}) != 1:
        # `device` is the CUDA string ("NVIDIA GeForce RTX 4090"); the others are marketplace names. They
        # normalise to the same suffix key when they are the same card, and only then.
        if not _one_card(resolved):
            bad.append(f"card identity disagrees across {resolved} — this is the fallback-to-another-card "
                       f"failure that got the 2026-07-24 grid withdrawn")

    # --- physics -------------------------------------------------------------------------------------------
    if not rec.get("healthy"):
        bad.append(f"physics check FAILED (final T {rec.get('final_temp_k')} K) — a diverged system integrates "
                   f"fast and reports a large, entirely fake ns/day")
    if str(rec.get("status")) not in ("OK",):
        bad.append(f"status {rec.get('status')!r} != 'OK'")

    # --- stability -----------------------------------------------------------------------------------------
    cv = rec.get("cv")
    try:
        cv = float(cv)
    except (TypeError, ValueError):
        cv = None
    if cv is None:
        bad.append("no block-to-block CV — the number arrived without the evidence that it is trustworthy")
    elif cv > MAX_CV:
        bad.append(f"CV {cv * 100:.1f}% > {MAX_CV * 100:.0f}% — contended or throttled host; re-bench elsewhere")

    # --- the number, and it must be the MEAN OF ITS OWN BLOCKS (CLAUDE.md §1.1: derived, never typed) -------
    blocks_ns = rec.get("blocks_ns_day") or []
    ns = rec.get("ns_per_day")
    if not blocks_ns:
        bad.append("per-block values missing — the table entry must be derivable from them, not asserted")
    elif ns is not None:
        derived = sum(blocks_ns) / len(blocks_ns)
        if abs(derived - float(ns)) > 0.02:
            bad.append(f"reported mean {ns} != mean of its own blocks {derived:.2f}")
    if not ns or float(ns) <= 0:
        bad.append(f"non-positive throughput {ns!r}")

    if bad:
        return False, bad, None
    key = sorted(resolved.values(), key=len)[0]
    return True, [], (key, round(sum(blocks_ns) / len(blocks_ns), 2))


def _one_card(resolved):
    """True when the differing normalised names are still the SAME card. PURE.

    The CUDA device string is a superset of the marketplace name ("NVIDIA GeForce RTX 4090" vs "RTX 4090"), so
    equality is the wrong test and `endswith` is the right one — the same suffix-anchored rule
    `vast_cost_model._model_key` uses, and for the same reason: a vendor PREFIX is free, a trailing qualifier
    (`4090D`, `3090 Ti`) is a different SKU and must not match."""
    vals = sorted(set(resolved.values()), key=len, reverse=True)
    longest = vals[0]
    return all(longest.endswith(v) for v in vals)


def _vram_gb(offer):
    """Vast reports `gpu_ram` in MB on some routes and GB on others. PURE."""
    ram = float(offer.get("gpu_ram", 0) or 0)
    return ram / 1024.0 if ram > 1000 else ram


# ★★ THE ESTIMATOR — MEDIAN OVER N INDEPENDENT HOSTS, AND WHY THE TABLE MUST USE ONE STATISTIC
#
# THE FINDING THAT FORCED THIS (2026-07-27). Five independent RTX 4090 hosts spanned 10.3 %; four RTX 4080
# hosts spanned 1.85 %. The original anchors were ONE HOST EACH, and by luck the 4080's sat near the top of
# its distribution while the 4090's sat mid-pack. **So the two anchors were not the same statistic**, and
# every card RATIO in the repo inherited that: the table said 4090/4080 = 1.074 while an internally consistent
# same-env, same-day, fresh-host measurement said 1.145. A 7 % error, and not in a direction anyone chose.
#
# That is not a 4090 problem. It is an INCONSISTENT-ESTIMATOR problem, and the only fix is that every entry is
# the same function of the same kind of sample.
#
# WHY THE MEDIAN AND NOT THE MAX OR THE MEAN:
#   * MAX would be "the best host ever seen", which RATCHETS — it rises every time another host is added, so
#     the table would never converge and would drift anti-conservative (over-stating throughput under-states
#     `$/ns`, which is the direction that BUYS).
#   * MEAN is dragged by the low tail, and the low tail is exactly the population of throttled/co-tenanted
#     hosts we would not knowingly keep. One bad host moves a 3-sample mean by a third of its deficit.
#   * MEDIAN over N>=3 is robust to a single bad host, does not ratchet, and converges. It answers the
#     question the ranking actually asks: what does a typical healthy rental of this card deliver?
MIN_HOSTS_FOR_MEDIAN = 3


def median_over_hosts(values):
    """The table estimator. PURE. `values` is one number per INDEPENDENT host."""
    xs = sorted(float(v) for v in values)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else round((xs[n // 2 - 1] + xs[n // 2]) / 2.0, 2)


def estimator_for(values, min_hosts=MIN_HOSTS_FOR_MEDIAN):
    """(value, estimator_label, n_hosts). PURE.

    A card with fewer than `min_hosts` does NOT silently get a median of two — it is labelled `single_host`
    or `provisional_n<N>` so that no consumer can mistake it for the same statistic as a properly sampled
    entry. That labelling is the whole point: a mixed table is tolerable ONLY while the mixture is visible,
    and an under-sampled entry errs conservatively anyway (every rental confounder is one-sided downward, so
    a small sample under-states throughput and therefore OVER-states `$/ns` — we under-buy, never over-buy)."""
    xs = [float(v) for v in values]
    if not xs:
        return None, "none", 0
    n = len(xs)
    v = median_over_hosts(xs)
    if n >= min_hosts:
        return v, f"median_of_{n}_hosts", n
    return (v, "single_host" if n == 1 else f"provisional_median_of_{n}_hosts", n)


def worst_case_usd(bid_usd_h, storage_usd_h, max_runtime_s=None):
    """The most this rental can cost: it self-terminates at `max_runtime_s`. PURE.

    Deliberately the WORST case and not an expected value. A bench that finishes in 8 minutes is the normal
    outcome, but a ceiling built on the normal outcome is not a ceiling."""
    h = float(max_runtime_s if max_runtime_s is not None else MAX_RUNTIME_S) / 3600.0
    return (float(bid_usd_h) + float(storage_usd_h)) * h


def plan_sweep(offers, cards=None, job=None, max_usd_per_card=None, max_usd_total=None,
               max_runtime_s=None, target_usd_per_ns=None, include_measured=False):
    """PURE: which cards to bench, on which offer, at what worst-case cost, and where the sweep stops.

    Ranks candidate cards by the CHEAPEST worst-case bench cost, so the sweep's budget buys the most cards —
    the fleet is helped by breadth of gradeable supply, not by settling one exotic card beautifully.

    Returns a list of decision dicts (ordered), each with `admit` True/False and a `reason`."""
    job = job or _vcm.JobProfile(disk_gb=BENCH_DISK_GB, min_vram_gb=BENCH_RES.min_vram_gb,
                                 min_reliability=BENCH_RES.min_reliability, min_cuda=BENCH_RES.min_cuda)
    per_card = MAX_USD_PER_CARD if max_usd_per_card is None else float(max_usd_per_card)
    total_cap = MAX_USD_TOTAL if max_usd_total is None else float(max_usd_total)
    runtime = MAX_RUNTIME_S if max_runtime_s is None else int(max_runtime_s)

    best = {}
    for o in offers:
        if not _vcm.passes_filters(o, job):
            continue
        name = str(o.get("gpu_name") or "").strip()
        if not name:
            continue
        if (not include_measured) and _vcm.card_of(name) is not None \
                and _vcm.throughput_provenance(name)[0] == "measured":
            continue                                   # already a measured entry — nothing to buy
        if cards and _vcm.normalise_gpu_name(name) not in {_vcm.normalise_gpu_name(c) for c in cards}:
            continue
        try:
            floor = float(o.get("min_bid") or 0)
        except (TypeError, ValueError):
            continue
        if floor <= 0:
            continue
        bid = _vcm.recommended_bid(floor, None)
        if bid is None:
            continue
        stor = _vcm.storage_usd_per_h(o.get("storage_cost"), job.disk_gb)
        cost = worst_case_usd(bid, stor, runtime)
        cur = best.get(name)
        if cur is None or cost < cur["worst_case_usd"]:
            best[name] = {"gpu_name": name, "offer_id": o.get("id"), "machine_id": o.get("machine_id"),
                          "min_bid": round(floor, 5), "bid": round(bid, 5),
                          "storage_usd_h": round(stor, 5), "all_in_usd_h": round(bid + stor, 5),
                          "worst_case_usd": round(cost, 4),
                          "already_measured": (_vcm.throughput_provenance(name)[0] == "measured"),
                          "n_offers": 0, "vram_gb": round(_vram_gb(o), 1)}
    for o in offers:
        n = str(o.get("gpu_name") or "").strip()
        if n in best and _vcm.passes_filters(o, job):
            best[n]["n_offers"] += 1

    out, spent = [], 0.0
    for row in sorted(best.values(), key=lambda r: r["worst_case_usd"]):
        # The information screen, imported from the census: what would this card have to deliver to be worth
        # buying at this price? A break-even far above anything silicon does is a card not worth benching.
        be = _census.breakeven_ns_per_day(target_usd_per_ns, row["bid"], row["storage_usd_h"]) \
            if target_usd_per_ns else None
        label, mult = _census.plausibility(be)
        row["breakeven_ns_per_day"] = None if be is None else round(be, 1)
        row["breakeven_x_reference"] = mult
        row["breakeven_label"] = label
        if row["worst_case_usd"] > per_card:
            row.update(admit=False, reason=f"worst-case ${row['worst_case_usd']:.3f} > per-card cap "
                                           f"${per_card:.2f}")
        elif spent + row["worst_case_usd"] > total_cap:
            row.update(admit=False, reason=f"sweep cap ${total_cap:.2f} reached (committed "
                                           f"${spent:.3f}) — HELD, not dropped")
        elif label.startswith("skip") and not row["already_measured"]:
            # The census's OWN screen, imported not re-derived: at this price the card would have to be far
            # faster than anything we have ever benched. Five cents is cheap, but buying information that
            # cannot change a decision is still waste.
            #
            # ⚠ AND IT DOES NOT APPLY TO A RE-MEASUREMENT, which is why `already_measured` exempts it. The
            # screen asks "is this unknown card worth DISCOVERING at today's price". A card already in the
            # table is not being discovered — it is being moved onto the same estimator as every other entry,
            # and that value does not depend on whether its price is attractive this minute. Observed
            # 2026-07-27: this screen silently refused to re-bench the RTX 4090, RTX 4080 and A100 PCIe, i.e.
            # it would have left the reference card itself on the old one-host statistic — the exact
            # inconsistency the re-measurement exists to remove. The dollar caps still apply.
            row.update(admit=False, reason=f"break-even {be:.0f} ns/day ({mult:.2f}x the reference card) — "
                                           f"{label}")
        else:
            row.update(admit=True, reason="admitted")
            spent += row["worst_case_usd"]
        row["committed_usd_after"] = round(spent, 4)
        out.append(row)
    return out


# =============================================================================================================
# the rented pipeline
# =============================================================================================================
_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 || { apt-get update -q||true; apt-get install -y -q --no-install-recommends curl ca-certificates||true; }
export PATH=/opt/mamba/envs/rbfe/bin:$PATH
# conda-pack relocation breaks OpenMM's compiled-in plugin dir (root-caused on the first firm run 2026-07-23).
export OPENMM_PLUGIN_DIR=/opt/mamba/envs/rbfe/lib/plugins
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
PY=/opt/mamba/envs/rbfe/bin/python
AWS=/opt/mamba/envs/rbfe/bin/aws
command -v "$AWS" >/dev/null 2>&1 || AWS="$PY -m awscli"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
export OPENMM_REQUIRE_CUDA=1
# autoteardown wraps the bench so a hang cannot hold the GPU past the watchdog. `|| true` so a failed bench
# still reaches the RECORD step below — a refusal with its reasons is worth more than a silent instance.
$PY autoteardown.py $PY gpu_md_bench.py 2>&1 | tee /tmp/bench.out || true
grep BENCH_RESULT /tmp/bench.out | tail -1 > /tmp/bench.line || true
RECORD=1 BENCH_LINE_FILE=/tmp/bench.line BENCH_OUT_FILE=/tmp/bench.out AWSCLI="$AWS" \
  $PY vast_bench_sweep.py || true
"""


def build_jobspec(gpu_name, branch, bucket, exclude_machine_ids=(), replicate=1, wave=None,
                  max_runtime_s=None):
    """PURE: the JobSpec for ONE card's calibration bench.

    `require_gpu=True` is the load-bearing flag: without it `_select_cheapest_offer` returns the best MEASURED
    offer, so a request to bench an RTX 5090 lands on a 4090 and the result is filed under the 5090. With it,
    an unavailable card fails the submit cleanly instead of quietly measuring something else."""
    import dataclasses
    base = _vcm.normalise_gpu_name(gpu_name).lower() or "unknown"
    # ★★ EVERY MEASUREMENT MUST GET ITS OWN S3 KEY — AND "EVERY" INCLUDES ACROSS LAUNCHES.
    #
    # This has now bitten three times in one day, each time destroying evidence that had already been paid for:
    #   1. 2026-07-24: two same-card bench legs shared one tag, so the host-variance control returned a single
    #      number and could not answer the question it was launched for;
    #   2. `nrv04_vast_launch.bench()`'s deterministic `bench-<gpu>-<edge>nm` key, which is how a re-run on
    #      2026-07-27 OVERWROTE the validated 2026-07-24 grid's raw artifacts — the reason the 726.79-vs-anchor
    #      disagreement could never be reconciled as two readings of one object, because one object was gone;
    #   3. two RTX 5090 rentals from two different LAUNCHES were both `replicate=1`, so the per-launch suffix
    #      did not save them and the second overwrote the first.
    #
    # `wave` closes the third case: it scopes the tag to the launch, so a later sweep ACCUMULATES hosts instead
    # of replacing them. That is load-bearing for a median-of-N estimator, which is only as good as the number
    # of independent hosts that survive in the store.
    # ⛔ ENV IS A DEFAULT, NEVER A HIDDEN INPUT (2026-07-27). This read used to be inline
    # `os.environ.get("BENCH_WAVE")`, which made a function documented as PURE depend on the process it ran
    # in — and the CI gate caught it the only way that matters: the same call returned `rtx4090-w2` under the
    # launch job's env and `rtx4090` in a bare shell. For a SPEND gate that is disqualifying: `plan_sweep`
    # and `worst_case_usd` decide what to rent, so an env-dependent answer means the ceiling that was tested
    # is not the ceiling that runs. Every such value is now an explicit parameter whose default is the env.
    wave = ((os.environ.get("BENCH_WAVE") if wave is None else wave) or "").strip().lower()
    suffix = (f"-{wave}" if wave else "") + (f"-r{replicate}" if replicate > 1 else "")
    tag = f"{base}{suffix}"
    label = f"{LABEL_PREFIX}{tag}"[:64]
    res = dataclasses.replace(BENCH_RES, gpu=gpu_name,
                              exclude_machine_ids=tuple(sorted(str(m) for m in exclude_machine_ids)))
    env = {
        "GIT_BRANCH": branch,
        "RESULT_S3": f"s3://{bucket}/{RESULT_PREFIX}/{tag}",
        "BENCH_TAG": tag,
        "BENCH_EDGE_NM": BENCH_EDGE_NM,
        "BENCH_DT_FS": str(BENCH_DT_FS),
        "BENCH_BLOCKS": str(BENCH_BLOCKS),
        "BENCH_TARGET_S": str(BENCH_TARGET_S),
        "BENCH_WARMUP": str(BENCH_WARMUP),
        "BENCH_GPU_REQUESTED": gpu_name,
    }
    return JobSpec(name=label, command=["bash", "-lc", _PIPELINE.replace("{repo}", REPO)],
                   image=FEP_IMAGE, checkpoint_uri="", resume=False, resources=res,
                   max_runtime_s=(MAX_RUNTIME_S if max_runtime_s is None else int(max_runtime_s)),
                   env=env)


# =============================================================================================================
# modes
# =============================================================================================================
def _s3():
    import boto3
    return boto3.client("s3")


def _live_offers(key):
    from gpu_backend import _vast_offer_query
    q = _vast_offer_query(BENCH_RES)
    return _vast_request("GET", "/search/asks/", key, params={"q": json.dumps(q)}).get("offers", [])


def _target_usd_per_ns(offers):
    """The `$/ns` a new card has to beat: the best the board can ALREADY be bought at. PURE-ish (no I/O).

    Deliberately the best gradeable offer rather than the ladder basis — the question a bench answers is
    "would this card have widened TODAY's cheap end", and the honest comparator is what today's board offers."""
    job = _vcm.JobProfile(disk_gb=BENCH_DISK_GB, min_vram_gb=BENCH_RES.min_vram_gb,
                          min_reliability=BENCH_RES.min_reliability, min_cuda=BENCH_RES.min_cuda)
    scored = [s for s in (_vcm.score_offer(o, job) for o in offers
                          if _vcm.passes_filters(o, job)) if s is not None]
    return min((s.usd_per_ns for s in scored), default=None)


def mode_plan(offers=None):
    key = os.environ.get("VAST_API_KEY")
    if offers is None:
        src = os.environ.get("BENCH_OFFERS_JSON")
        if src:
            offers = json.load(open(src))
        elif key:
            offers = _live_offers(key)
        else:
            print("[cal] no offers: set BENCH_OFFERS_JSON or VAST_API_KEY", flush=True)
            return 2
    target = _target_usd_per_ns(offers)
    rows = plan_sweep(offers, cards=_env_cards(), target_usd_per_ns=target)
    admitted = [r for r in rows if r["admit"]]
    print(f"[cal] board: {len(offers)} offers; best gradeable $/ns = "
          f"{'n/a' if target is None else f'{target:.5f}'}", flush=True)
    print(f"[cal] unbenched models on the board that pass the PRODUCTION filters: {len(rows)}", flush=True)
    for r in rows:
        flag = "ADMIT " if r["admit"] else "HOLD  "
        be = "" if r["breakeven_ns_per_day"] is None else \
            f" breakeven {r['breakeven_ns_per_day']:.0f} ns/day ({r['breakeven_x_reference']:.2f}x ref)"
        print(f"  {flag}{r['gpu_name']:<18} n={r['n_offers']:<2} bid ${r['bid']:.4f}/hr "
              f"+ storage ${r['storage_usd_h']:.4f} -> worst case ${r['worst_case_usd']:.3f}{be}"
              f"   {'' if r['admit'] else '<- ' + r['reason']}", flush=True)
    print(f"[cal] ADMITTED {len(admitted)} card(s); worst-case total "
          f"${sum(r['worst_case_usd'] for r in admitted):.3f} against the ${MAX_USD_TOTAL:.2f} sweep cap",
          flush=True)
    doc = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "n_offers": len(offers), "best_gradeable_usd_per_ns": target,
           "max_runtime_s": MAX_RUNTIME_S, "max_usd_per_card": MAX_USD_PER_CARD,
           "max_usd_total": MAX_USD_TOTAL, "rows": rows}
    with open("vast-bench-sweep-plan.json", "w") as f:
        json.dump(doc, f, indent=2)
    print("[cal] wrote vast-bench-sweep-plan.json", flush=True)
    return 0


def _env_cards():
    v = (os.environ.get("BENCH_CARDS") or "").strip()
    return [c.strip() for c in v.split(",") if c.strip()] or None


def mode_launch():
    key = os.environ.get("VAST_API_KEY")
    if not key:
        print("[cal] LAUNCH needs VAST_API_KEY", flush=True)
        return 2
    bucket = BUCKET or os.environ.get("VAST_CKPT_BUCKET") or ""
    if not bucket:
        print("[cal] LAUNCH needs VAST_CKPT_BUCKET", flush=True)
        return 2
    branch = os.environ.get("GIT_BRANCH", "claude/max-effort-2dq11l")
    offers = _live_offers(key)
    include_measured = os.environ.get("BENCH_INCLUDE_MEASURED") == "1"
    replicates = max(1, int(os.environ.get("BENCH_REPLICATES", "1")))
    rows = plan_sweep(offers, cards=_env_cards(), target_usd_per_ns=_target_usd_per_ns(offers),
                      include_measured=include_measured)
    admitted = [r for r in rows if r["admit"]]
    if not admitted:
        print("[cal] nothing admitted — the plan is the readout; NOT a silent no-op", flush=True)
        for r in rows:
            print(f"  HOLD {r['gpu_name']}: {r['reason']}", flush=True)
        return 0
    be = get_backend("vast")
    launched, committed = [], 0.0
    for r in admitted:
        # DISTINCT HOSTS PER REPLICATE. A replicate that lands on the same machine measures the same host
        # twice and answers nothing about host variance — which is the entire question a replicate exists for.
        #
        # BENCH_EXCLUDE_MACHINES seeds the set with hosts already known to be a waste of a rental. §6: a host
        # that will not deliver has infinite realised $/ns, which the $/ns ranking cannot see, so it keeps
        # winning selection and keeps failing. Observed 2026-07-27: three 4090 rentals sat at `loading` past
        # 13 minutes while three siblings on the identical image finished in five — slow-downlink hosts, and
        # the right answer on Vast is another host, not a longer wait.
        excluded = {m.strip() for m in (os.environ.get("BENCH_EXCLUDE_MACHINES") or "").split(",")
                    if m.strip()}
        for rep in range(1, replicates + 1):
            if committed + r["worst_case_usd"] > MAX_USD_TOTAL:
                print(f"[cal] sweep cap ${MAX_USD_TOTAL:.2f} reached — HOLDING {r['gpu_name']} r{rep}",
                      flush=True)
                break
            spec = build_jobspec(r["gpu_name"], branch, bucket, exclude_machine_ids=tuple(excluded),
                                 replicate=rep)
            try:
                h = be.submit(spec)
            except Exception as e:  # noqa: BLE001
                # §6: a capacity refusal means pick another host, not wait. At sweep scale the simplest
                # correct response is to record it and move on — the next tick re-plans on a fresh board.
                print(f"[cal] {r['gpu_name']} r{rep}: submit refused ({type(e).__name__}: {e})", flush=True)
                r.setdefault("submit_errors", []).append(f"r{rep}: {type(e).__name__}: {e}")
                continue
            mid = (h.extra or {}).get("machine_id")
            if mid is not None:
                excluded.add(str(mid))
            committed += r["worst_case_usd"]
            launched.append({"gpu_name": r["gpu_name"], "replicate": rep, "instance": h.job_id,
                             "machine_id": mid, "dph": h.extra.get("dph"),
                             "worst_case_usd": r["worst_case_usd"]})
            print(f"[cal] {r['gpu_name']} r{rep}: instance {h.job_id} machine {mid} "
                  f"dph=${h.extra.get('dph')}/hr worst case ${r['worst_case_usd']:.3f}", flush=True)
    print(f"[cal] launched {len(launched)}/{len(admitted)}; worst-case committed ${committed:.3f}", flush=True)
    with open("vast-bench-sweep-launched.json", "w") as f:
        json.dump({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "launched": launched, "plan": rows}, f, indent=2)
    return 0


def mode_record():
    """ON-HOST: parse the bench line, stamp the offer/device identity onto it, upload. Never raises."""
    line = ""
    try:
        line = open(os.environ.get("BENCH_LINE_FILE", "/tmp/bench.line")).read().strip()
    except OSError:
        pass
    rec = parse_bench_line(line)
    rec["_raw"] = line
    rec["gpu_requested"] = os.environ.get("BENCH_GPU_REQUESTED", "")
    # What the MARKETPLACE said we rented, forwarded by gpu_backend. The CUDA device string and this must
    # agree or `admit()` refuses — that disagreement is the mislabelled-card failure.
    rec["offer_gpu_name"] = os.environ.get("VAST_OFFER_GPU_NAME", "")
    rec["edge_nm"] = os.environ.get("BENCH_EDGE_NM", "")
    rec["protocol"] = "gpu_md_bench.py TIP3P/PME 84,534 particles, 4 fs HMR, 3 timed blocks ~60 s total"
    rec["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ok, reasons, entry = admit(rec)
    rec["admitted"] = ok
    rec["admission_reasons"] = reasons
    rec["proposed_entry"] = None if entry is None else {"card": entry[0], "ns_per_day": entry[1]}
    print("[cal-record] " + json.dumps({k: v for k, v in rec.items() if k != "_raw"}), flush=True)
    path = "/tmp/bench-record.json"
    with open(path, "w") as f:
        json.dump(rec, f, indent=2)
    dest = os.environ.get("RESULT_S3")
    aws = (os.environ.get("AWSCLI") or "aws").split()
    if dest:
        for src, name in ((path, "bench-record.json"),
                          (os.environ.get("BENCH_OUT_FILE", "/tmp/bench.out"), "bench.out")):
            try:
                subprocess.run(aws + ["s3", "cp", src, f"{dest}/{name}", "--only-show-errors"], check=False)
            except Exception as e:  # noqa: BLE001
                print(f"[cal-record] upload {name} failed: {e}", flush=True)
    return 0


LEGACY_PREFIX = os.environ.get("BENCH_LEGACY_PREFIX", "vast-bench-results")


def mode_forensic():
    """READ-ONLY: dump EVERY bench artifact ever written, with the fields that could explain a disagreement.

    ★ WHY THIS EXISTS (2026-07-27). S3 `vast-bench-results/bench-rtx4090-9p5nm/bench.json` reads 726.79 ns/day
    at CV 0.27 % — about 3.9 % BELOW the RTX 4090 anchor in the table, which is itself internally tight. Two
    runs of the same nominal protocol, both stable, disagreeing. `REFERENCE_NS_PER_H` is derived from the
    anchor, so it sets the basis every `$/ns` multiple in the repo is judged against, including the 1.5x buy
    line. An error there is systematic and points the same way everywhere.

    CLAUDE.md §4 forbids a "probably" here, so this prints the observations that DISCRIMINATE rather than a
    story: the CUDA device string (a 4090D is a cut-down SKU and would explain a deficit), `nvidia-smi`'s
    reported name/driver, the OpenMM platform and plugin-load failures, the particle count, the timestep, the
    per-block spread, the wall time per block, and the object's own S3 LastModified. It rents nothing."""
    bucket = BUCKET or os.environ.get("VAST_CKPT_BUCKET") or ""
    if not bucket:
        print("[forensic] needs VAST_CKPT_BUCKET", flush=True)
        return 2
    s3 = _s3()
    pag = s3.get_paginator("list_objects_v2")
    out = []
    for prefix in (LEGACY_PREFIX, RESULT_PREFIX):
        for page in pag.paginate(Bucket=bucket, Prefix=f"{prefix}/"):
            for o in page.get("Contents", []):
                k = o["Key"]
                if not (k.endswith(".json") or k.endswith(".out")):
                    continue
                try:
                    body = s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode("utf-8", "replace")
                except Exception as e:  # noqa: BLE001
                    print(f"[forensic] unreadable {k}: {e}", flush=True)
                    continue
                out.append({"key": k, "size": o["Size"], "last_modified": o["LastModified"].isoformat(),
                            "body": body})
    print(f"[forensic] {len(out)} artifact(s) under {LEGACY_PREFIX}/ and {RESULT_PREFIX}/", flush=True)
    for a in sorted(out, key=lambda x: x["key"]):
        print("=" * 110, flush=True)
        print(f"{a['key']}   {a['size']} B   {a['last_modified']}", flush=True)
        if a["key"].endswith(".json"):
            print(a["body"][:4000], flush=True)
        else:
            # The .out carries nvidia-smi (real card name + driver), the OpenMM platform list, any
            # plugin-load failure, and every timed block — i.e. every condition that could differ.
            lines = [ln for ln in a["body"].splitlines() if ln.strip()]
            keep = [ln for ln in lines if any(t in ln for t in
                    ("bench]", "BENCH_RESULT", "NVIDIA", "GeForce", "RTX", "Driver", "CUDA", "MiB",
                     "plugin", "platform", "Error", "error", "WARN"))]
            for ln in (keep or lines)[:80]:
                print("   " + ln[:200], flush=True)
    with open("vast-bench-forensic.json", "w") as f:
        json.dump({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "bucket": bucket, "artifacts": out}, f, indent=2)
    print("[forensic] wrote vast-bench-forensic.json", flush=True)
    return 0


def board_impact(offers, extra_entries=None, n_units=19, min_vram_gb=24, disk_gb=80):
    """BEFORE/AFTER on a real board: priceable count, best single `$/ns`, best fleet `$/ns` for `n_units`.

    THE NUMBER THAT SAYS WHETHER THE SWEEP WAS WORTH DOING, so it is computed with the SAME machinery that
    rents — `gpu_backend.rank_offers_by_usd_per_ns` and `congeneric_fanout.place_units` — rather than a
    parallel scorer that would be free to flatter the result.

    `extra_entries` is a `{card: ns_per_day}` overlay applied to the throughput table for the AFTER pass.
    Mutating the module table temporarily (and restoring it in a `finally`) is deliberate: the alternative is
    a second scoring path that could disagree with the one that actually buys, and rule 1 forbids that. The
    overlay never persists — a card only becomes permanently priceable by being edited into the table with a
    passing provenance test."""
    import copy
    import dataclasses
    from gpu_backend import rank_offers_by_usd_per_ns
    import congeneric_fanout as _cf

    res = dataclasses.replace(BENCH_RES, gpu="any", require_gpu=False,
                              min_vram_gb=min_vram_gb, disk_gb=disk_gb)

    def _snapshot(label):
        measured, capable = rank_offers_by_usd_per_ns(offers, res)
        ranked = [m[0] for m in measured]
        ceiling = _cf.unit_usd_per_ns_ceiling()
        n_placed, placed, _held = _cf.place_units(ranked, n_units, ceiling)
        fleet = (sum(placed) / len(placed)) if placed else None
        basis = _cf.basis_usd_per_ns()
        return {"label": label, "qualifying": len(capable), "priceable": len(measured),
                "unpriceable": len(capable) - len(measured),
                "best_usd_per_ns": (round(ranked[0], 6) if ranked else None),
                "best_x_basis": (round(ranked[0] / basis, 3) if ranked and basis else None),
                "n_units_placeable": n_placed,
                "fleet_mean_usd_per_ns_of_placed": (round(fleet, 6) if fleet else None),
                "fleet_x_basis": (round(fleet / basis, 3) if fleet and basis else None),
                "per_unit_ceiling_usd_per_ns": round(ceiling, 6), "basis_usd_per_ns": round(basis, 6)}

    # ★ THE BASELINE IS THE TABLE **MINUS** THIS SWEEP'S ADDITIONS, NOT THE TABLE AS IT SITS.
    #
    # Got this wrong once and it produced a flat, meaningless answer: by the time the impact runs, the new
    # entries are already committed, so "before = table as committed" IS the after and the comparison shows
    # nothing. The honest baseline is reconstructed by removing exactly what the sweep added — and by
    # restoring the CONSERVATIVE_ALIAS that a measurement retired, because deleting the measurement without
    # putting its stand-in back would overstate the gain by counting a card that was already priceable.
    after = _snapshot("after — table with this sweep's measurements")
    if not extra_entries:
        return {"before": None, "after": after, "n_units": n_units, "min_vram_gb": min_vram_gb}
    saved = copy.deepcopy(_vcm.MEASURED_NS_PER_DAY_84K)
    saved_alias = copy.deepcopy(_vcm.CONSERVATIVE_ALIASES)
    try:
        for k in extra_entries:
            _vcm.MEASURED_NS_PER_DAY_84K.pop(k, None)
        for k, v in (RETIRED_ALIASES_FOR_BASELINE or {}).items():
            if k not in _vcm.MEASURED_NS_PER_DAY_84K and v[0] in _vcm.MEASURED_NS_PER_DAY_84K:
                _vcm.CONSERVATIVE_ALIASES[k] = v
        before = _snapshot("before — table without this sweep")
    finally:
        _vcm.MEASURED_NS_PER_DAY_84K.clear()
        _vcm.MEASURED_NS_PER_DAY_84K.update(saved)
        _vcm.CONSERVATIVE_ALIASES.clear()
        _vcm.CONSERVATIVE_ALIASES.update(saved_alias)
    return {"before": before, "after": after, "n_units": n_units, "min_vram_gb": min_vram_gb,
            "added": dict(extra_entries)}


# The alias state a measurement retired, kept ONLY so the before/after baseline is honest. Never read by any
# ranking path — `vast_cost_model.CONSERVATIVE_ALIASES` is the live allow-list.
RETIRED_ALIASES_FOR_BASELINE = {
    "RTX3090TI": ("RTX3090", "conservative alias retired 2026-07-27 when the card was measured"),
}
# The cards this sweep put in the table that were NOT there before. A re-measurement of an existing entry
# (RTX 4090, RTX 4080) is not a widening and must not be counted as one.
ADDED_BY_THIS_SWEEP = ("RTX5090", "RTX5080", "A100PCIE", "RTXPRO4000", "RTX3090TI", "RTX5060TI", "RTXA4000")


def mode_impact():
    """Live before/after. `BENCH_IMPACT_ENTRIES` is a JSON `{card: ns_per_day}` overlay (blank = read the
    admitted entries out of `vast-bench-sweep-results.json`)."""
    key = os.environ.get("VAST_API_KEY")
    src = os.environ.get("BENCH_OFFERS_JSON")
    offers = json.load(open(src)) if src else (_live_offers(key) if key else [])
    raw = (os.environ.get("BENCH_IMPACT_ENTRIES") or "").strip()
    if raw:
        extra = json.loads(raw)
    else:
        try:
            extra = json.load(open("vast-bench-sweep-results.json")).get("admitted") or {}
        except (OSError, ValueError):
            extra = {}
    # Only the cards this sweep ADDED define the baseline; a re-measurement of a card that was already in the
    # table (RTX 4090, RTX 4080) was priceable before and after, so removing it would invent a gain.
    extra = {k: v for k, v in extra.items() if k in ADDED_BY_THIS_SWEEP}
    out = {}
    for vram in (int(os.environ.get("BENCH_IMPACT_VRAM", "24")), 16):
        out[f"min_vram_{vram}gb"] = board_impact(offers, extra, min_vram_gb=vram)
    doc = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "n_offers": len(offers),
           "added": extra, "views": out,
           "_what": "What widening MEASURED_NS_PER_DAY_84K does to a real board. Computed with the SAME "
                    "rank_offers_by_usd_per_ns + place_units the launcher uses, so it cannot flatter itself. "
                    "The overlay is temporary and never persists."}
    for name, v in out.items():
        b, a = v["before"], v["after"]
        print(f"--- {name} ({v['n_units']} units) ---", flush=True)
        for s in (b, a):
            if not s:
                continue
            print(f"  {s['label']:<42} qualifying {s['qualifying']:<3} priceable {s['priceable']:<3} "
                  f"best $/ns {s['best_usd_per_ns']} ({s['best_x_basis']}x basis)  placeable "
                  f"{s['n_units_placeable']}/{v['n_units']}  fleet $/ns "
                  f"{s['fleet_mean_usd_per_ns_of_placed']} ({s['fleet_x_basis']}x)", flush=True)
    with open("vast-bench-board-impact.json", "w") as f:
        json.dump(doc, f, indent=2)
    print("[cal] wrote vast-bench-board-impact.json", flush=True)
    return 0


def reap(key=None, max_age_min=None, done_labels=()):
    """DESTROY every `cal-*` instance. The only guaranteed way the meter stops.

    ⛔ NOT OPTIONAL, and not something the host can do for itself. Measured 2026-07-27: an unprivileged
    container cannot end itself — `poweroff`/`shutdown` need an init it does not have, `kill -9 1` returns
    SUCCESS while being ignored — so the onstart EXIT trap stops the JOB and the rental keeps billing. The
    destroy is control-plane only. A calibration sweep that forgets this converts a $0.05 measurement into an
    open-ended rental, which is the single most expensive mistake available in this lane.

    TWO INDEPENDENT REASONS TO DESTROY, and a box needs only one: (a) its record is already in S3, so the
    rental has delivered everything it will ever deliver; or (b) it is older than `max_age_min`, which for a
    minutes-long bench means it finished without uploading or it wedged — both wanting the same action.
    Keeping (a) separate from (b) is what lets a collect run reap a finished bench IMMEDIATELY without also
    killing a sibling that is still timing its blocks. Nothing here can touch another lane's instance — the
    label prefix is checked, never the age alone."""
    key = key or os.environ.get("VAST_API_KEY")
    if not key:
        print("[cal-reap] no VAST_API_KEY — cannot destroy; the meter is still running", flush=True)
        return []
    age = int(os.environ.get("BENCH_REAP_AGE_MIN", "0") if max_age_min is None else max_age_min)
    done = {str(x) for x in done_labels}
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    killed = []
    now = time.time()
    for i in insts:
        if not str(i.get("label") or "").startswith(LABEL_PREFIX):
            continue
        try:
            started = float(i.get("start_date") or 0)
        except (TypeError, ValueError):
            started = 0
        age_min = (now - started) / 60.0 if started else 1e9
        if age_min < age and str(i.get("label")) not in done:
            print(f"[cal-reap] keep {i.get('id')} ({i.get('label')}) age {age_min:.1f} min < {age} "
                  f"and no record yet — still measuring", flush=True)
            continue
        try:
            _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
            killed.append(i.get("id"))
            print(f"[cal-reap] DESTROYED {i.get('id')} ({i.get('label')}) age {age_min:.1f} min "
                  f"dph=${i.get('dph_total')}/hr", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[cal-reap] FAILED to destroy {i.get('id')}: {e}  ** STILL BILLING **", flush=True)
    if not killed:
        print("[cal-reap] no cal-* instances to destroy", flush=True)
    return killed


def realised_spend(key=None):
    """What the sweep has ACTUALLY cost so far, from the live instance records. Returns (usd, rows).

    Reads `dph_total` x elapsed for every `cal-*` box currently visible. A destroyed instance disappears from
    the API, so this is a LIVE view and not a ledger — `mode_collect` prints it before it reaps, which is the
    only moment both facts exist at once."""
    key = key or os.environ.get("VAST_API_KEY")
    if not key:
        return 0.0, []
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    now, total, rows = time.time(), 0.0, []
    for i in insts:
        if not str(i.get("label") or "").startswith(LABEL_PREFIX):
            continue
        try:
            h = max(0.0, (now - float(i.get("start_date") or now)) / 3600.0)
            usd = h * float(i.get("dph_total") or 0.0)
        except (TypeError, ValueError):
            h, usd = 0.0, 0.0
        total += usd
        # ★ THE FIELDS THAT DISCRIMINATE A SLOW IMAGE PULL FROM A WEDGED BOX (2026-07-27). Three 4090
        # rentals sat at `loading` for >11 min while three siblings on the identical image finished. A bare
        # status cannot tell those apart; `status_msg` says which layer the container is on, `inet_down` says
        # whether bytes are actually arriving, and `gpu_util` says whether anything is running yet.
        rows.append({"instance": i.get("id"), "label": i.get("label"), "hours": round(h, 4),
                     "dph": i.get("dph_total"), "usd": round(usd, 4),
                     "status": i.get("actual_status") or i.get("cur_state"),
                     "status_msg": i.get("status_msg"), "inet_down": i.get("inet_down"),
                     "gpu_util": i.get("gpu_util"), "machine_id": i.get("machine_id")})
    return round(total, 4), rows


SPEND_LEDGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "vast-bench-spend-ledger.json")


def _merge_spend_ledger(rows, path=None):
    """(cumulative_usd, merged_rows). Keyed on instance id, keeping the LARGEST cost ever seen for each.

    A destroyed Vast instance is gone from the API, so a live snapshot silently forgets every rental the
    previous reap destroyed — which is precisely the money already spent. Max-per-instance is the right merge:
    the last reading before a box vanished is its final cost, and a re-read of a live box only ever grows."""
    path = path or SPEND_LEDGER_PATH
    try:
        led = json.load(open(path))
    except (OSError, ValueError):
        led = {"_what": "Cumulative realised spend on cal-* calibration rentals, keyed on instance id. A "
                        "destroyed instance vanishes from the Vast API, so a live snapshot under-reports; "
                        "this keeps the largest cost ever observed for each rental.", "instances": {}}
    inst = led.setdefault("instances", {})
    for r in rows:
        k = str(r["instance"])
        prev = inst.get(k)
        if prev is None or float(r.get("usd") or 0) >= float(prev.get("usd") or 0):
            inst[k] = dict(r)          # keep every diagnostic field; a whitelist here silently dropped the
            #                            status_msg/inet_down/gpu_util added to diagnose a stuck rental
    total = round(sum(float(v.get("usd") or 0) for v in inst.values()), 4)
    led["cumulative_usd"] = total
    led["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        with open(path, "w") as f:
            json.dump(led, f, indent=2)
    except OSError:
        pass
    return total, sorted(inst.values(), key=lambda v: str(v.get("label")))


def mode_collect():
    bucket = BUCKET or os.environ.get("VAST_CKPT_BUCKET") or ""
    if not bucket:
        print("[cal] COLLECT needs VAST_CKPT_BUCKET", flush=True)
        return 2
    s3 = _s3()
    recs = []
    pag = s3.get_paginator("list_objects_v2")
    for page in pag.paginate(Bucket=bucket, Prefix=f"{RESULT_PREFIX}/"):
        for o in page.get("Contents", []):
            if not o["Key"].endswith("bench-record.json"):
                continue
            try:
                recs.append(json.loads(s3.get_object(Bucket=bucket, Key=o["Key"])["Body"].read()))
            except Exception as e:  # noqa: BLE001
                print(f"[cal] unreadable {o['Key']}: {e}", flush=True)
    print(f"[cal] {len(recs)} bench record(s) under s3://{bucket}/{RESULT_PREFIX}/", flush=True)
    entries, refused, admitted_by_card = {}, [], {}
    for r in sorted(recs, key=lambda x: str(x.get("tag"))):
        ok, reasons, entry = admit(r)
        if ok:
            admitted_by_card.setdefault(entry[0], []).append((entry[1], r.get("tag")))
        head = (f"  {str(r.get('gpu_requested') or r.get('tag')):<18} device={r.get('device')!r} "
                f"atoms={r.get('atoms')} ns/day={r.get('ns_per_day')} cv={r.get('cv')} "
                f"blocks={r.get('blocks_ns_day')}")
        if ok:
            print(head + "  -> ADMIT", flush=True)
        else:
            refused.append((r.get("gpu_requested") or r.get("tag"), reasons))
            print(head + "  -> REFUSED", flush=True)
            for x in reasons:
                print(f"       - {x}", flush=True)
    # ★ THE HOST DISTRIBUTION PER CARD, when replicates exist — the thing two points cannot give you.
    # A card constant is a CAPABILITY. Every confounder a rental can carry (power cap, thermal throttle,
    # co-tenant, a host CPU too slow to feed kernel launches) is ONE-SIDED DOWNWARD, and none of them raises a
    # reading. A tight CV proves the host was STEADY, not that it was unthrottled — a power-limited card runs
    # steadily slow. So the spread across independent hosts is the only evidence that separates "this card is
    # this fast" from "this rental was this fast", and it is printed rather than silently averaged away.
    by_card = admitted_by_card
    print("\n[cal] === THE ESTIMATOR: median over independent hosts (see `median_over_hosts`) ===", flush=True)
    for card, vals in sorted(by_card.items()):
        xs = sorted(v for v, _t in vals)
        val, label, n = estimator_for(xs)
        entries[card] = val
        spread = (100 * (xs[-1] - xs[0]) / xs[-1]) if len(xs) > 1 and xs[-1] else 0.0
        flag = "" if n >= MIN_HOSTS_FOR_MEDIAN else "   ** UNDER-SAMPLED — not the same statistic **"
        print(f"  {card:<12} {val:>8.2f}  {label:<22} n={n}  "
              f"min {xs[0]:.2f} / max {xs[-1]:.2f}  spread {spread:.1f}%{flag}", flush=True)
        for v, t in sorted(vals, reverse=True):
            print(f"       {t}: {v:.2f}", flush=True)

    if entries:
        print("\n[cal] PROPOSED entries for vast_cost_model.MEASURED_NS_PER_DAY_84K "
              "(paste them there; nothing else may hold a throughput):", flush=True)
        for k, v in sorted(entries.items(), key=lambda kv: -kv[1]):
            xs = sorted(x for x, _t in by_card[k])
            _v, label, n = estimator_for(xs)
            print(f'    "{k}": {v},   # {label}  hosts {" / ".join("%.2f" % x for x in xs)}', flush=True)
    _write_provenance(recs)

    # REALISED SPEND, then the reap — in that order, because a destroyed instance vanishes from the API and
    # this is the only moment both facts exist at once.
    usd, rows = realised_spend()
    for r in rows:
        print(f"[cal-spend] {r['instance']} {r['label']} {r['status']} {r['hours']:.2f} h x "
              f"${r['dph']}/hr = ${r['usd']:.4f}", flush=True)
    # ★ CUMULATIVE, NOT A SNAPSHOT. A DESTROYED INSTANCE DISAPPEARS FROM THE VAST API, so `realised_spend`
    # alone under-reports by exactly the rentals the previous collect reaped — i.e. it forgets the money it
    # just finished spending. The ledger is keyed on instance id and keeps the LARGEST cost ever seen for
    # each, which is the last reading before it vanished.
    usd, rows = _merge_spend_ledger(rows)
    print(f"[cal-spend] REALISED CUMULATIVE across every cal-* rental ever seen: ${usd:.4f} "
          f"(sweep cap ${MAX_USD_TOTAL:.2f})", flush=True)
    with open("vast-bench-sweep-results.json", "w") as f:
        json.dump({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "n_records": len(recs), "admitted": entries,
                   "refused": [{"card": c, "reasons": r} for c, r in refused],
                   "realised_usd": usd, "instances": rows,
                   "records": recs}, f, indent=2)
    print("[cal] wrote vast-bench-sweep-results.json", flush=True)
    if os.environ.get("BENCH_NO_REAP") != "1":
        # A box whose record is already in S3 has delivered everything it will; anything else gets the age
        # gate, so a collect run can never destroy a sibling that is still timing its blocks.
        done = {LABEL_PREFIX + str(r.get("tag")) for r in recs if r.get("tag")}
        reap(max_age_min=int(os.environ.get("BENCH_REAP_AGE_MIN", "25")), done_labels=done)
    return 0


def _write_provenance(recs):
    """Append ADMITTED records to `throughput-bench-provenance.json`.

    TWO LISTS, AND THE SPLIT IS LOAD-BEARING:
      * `records`          — ONE per card: the evidence the table's own test recomputes that card's mean from.
                             Never rewritten. Adding a card here is what makes it priceable.
      * `host_observations` — every OTHER admitted measurement of a card already in `records`. These are the
                             replicate hosts. They are deliberately kept OUT of `records` so that nothing can
                             quietly average a second host into the anchor: a card constant is a capability
                             and the spread is separate evidence about hosts, not about the card.
    """
    try:
        doc = json.load(open(PROVENANCE_PATH))
    except (OSError, ValueError):
        return
    have = {r["card"] for r in doc.get("records", [])}
    obs = doc.setdefault("host_observations", [])
    seen_obs = {(o.get("card"), o.get("tag")) for o in obs}
    added = 0
    for r in recs:
        ok, _reasons, entry = admit(r)
        if not ok:
            continue
        if entry[0] in have:
            if (entry[0], r.get("tag")) in seen_obs:
                continue
            obs.append({"card": entry[0], "tag": r.get("tag"), "ns_per_day": entry[1],
                        "blocks_ns_per_day": r.get("blocks_ns_day"), "cv": r.get("cv"),
                        "cuda_device": r.get("device"), "gpu_name_as_offered": r.get("offer_gpu_name"),
                        "final_temp_k": r.get("final_temp_k"), "wall_s": r.get("wall_s"),
                        "utc": r.get("utc"),
                        "_role": "INDEPENDENT HOST of a card already in `records`. Evidence about host "
                                 "spread, NOT an input to the table entry."})
            seen_obs.add((entry[0], r.get("tag")))
            added += 1
            continue
        doc["records"].append({
            "card": entry[0], "gpu_name_as_offered": r.get("offer_gpu_name") or r.get("gpu_requested"),
            "cuda_device": r.get("device"), "blocks_ns_per_day": r.get("blocks_ns_day"),
            "cv": r.get("cv"), "final_temp_k": r.get("final_temp_k"), "atoms": r.get("atoms"),
            "dt_fs": r.get("dt_fs"), "blocks": r.get("blocks"), "wall_s": r.get("wall_s"),
            "platform": r.get("platform"), "utc": r.get("utc"),
            "source": "vast_bench_sweep.py calibration rental (Vast interruptible)",
        })
        have.add(entry[0])
        added += 1
    if added:
        with open(PROVENANCE_PATH, "w") as f:
            json.dump(doc, f, indent=2)
        print(f"[cal] added {added} provenance record(s) to {os.path.basename(PROVENANCE_PATH)}", flush=True)


def main(argv=None):
    if os.environ.get("RECORD") == "1":
        return mode_record()
    if os.environ.get("REAP") == "1":
        reap()
        return 0
    if os.environ.get("IMPACT") == "1":
        return mode_impact()
    if os.environ.get("FORENSIC") == "1":
        return mode_forensic()
    if os.environ.get("LAUNCH") == "1":
        return mode_launch()
    if os.environ.get("COLLECT") == "1":
        return mode_collect()
    return mode_plan()


if __name__ == "__main__":
    raise SystemExit(main())
