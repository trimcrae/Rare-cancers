#!/usr/bin/env python3
"""GCP card throughput probe — the machinery that turns "which GCP GPU" from SPEC-DERIVED into MEASURED.

★ WHAT THIS EXISTS TO SETTLE.

`research/compute/gcp-gpu-facts.md` §1b and nr4a3-program-map.md Open decision 5 both carry a table claiming that a
**P100 is faster than an L4 AND +18 % better on science-per-dollar**, and that a **T4 is 2.2× better on
science-per-dollar** — and both mark every row ⚠ *SPEC-DERIVED, NOT MEASURED, do not plan on these rows yet*.
The heuristic behind them is memory bandwidth, validated on exactly ONE pair (L4 vs Vast RTX 4090) where
bandwidth and FP32 scale together, so it cannot separate a bandwidth-bound workload from a compute-bound one.
**T4 vs L4 is precisely the discriminating case** — 320 vs 300 GB/s of bandwidth but 8.1 vs 30 TFLOPS of FP32 —
and is therefore the least trustworthy row in the table. This repo has already retracted one card ratio built
from spec reasoning (the 2.06× that compared a warmup rate to a production rate, `pricing.md` §CORRECTION
2026-07-26).

So the answer has to be measured, and measuring it is cheap: a short production probe per card, on the real
protocol, on free trial credit.

★ WHY THE SYSTEM SIZE IS THE PART THAT DECIDES WHETHER THE ANSWER IS WORTH ANYTHING.

`gpu_md_bench.py` defaults to `BENCH_EDGE_NM=7.1` ≈ 36k atoms and `gpu-bench-gcp.yml` never passed the
variable at all, so every prior GCP bench measured a **36k-atom** box. The question is about the ternary
lane's real system, which is **141,968 particles** (the v2pe build — `ternary-watch.json`'s
`_required_run_params_note`, `watchdog_validate.py`, and the particle census in
`research/compute/ternary-4fs-vast-findings.md`). PME cost, occupancy and the bandwidth-vs-FLOPs balance all
move with particle count, so a 36k probe answers a *different question* with an equally confident-looking
number. That is the exact error class `gcp-gpu-facts.md` exists to prevent.

`edge_nm_for_particles()` therefore derives the box edge from the ONE exact anchor the repo already owns —
`vast_bench_sweep.BENCH_EDGE_NM = 9.5` ↔ `BENCH_ATOMS = 84534`, both imported, never re-typed — by cube-root
scaling, because `addSolvent` fills at a fixed water density. Nothing here restates a density constant.

★ WHY EVERY PROBE RUNS **TWO** SIZES, AND WHY THAT IS NOT GOLD-PLATING.

The expensive part of a probe is the boot + conda solve (~5-10 min of billed GPU idle); a second timed
measurement adds ~2-3 min. For that we get both halves of the question:

  * **11.29 nm ≈ 141,887 particles** — the lane's real system, which is what decides which card the next GCP
    leg buys. Run FIRST, so a VM that dies early still yields the decision-relevant number.
  * **9.5 nm = 84,534 particles** — the protocol of `vast_cost_model.MEASURED_NS_PER_DAY_84K`, described
    in-repo as THE ONLY THROUGHPUT TABLE. Running it makes a GCP card commensurable with every Vast card in
    one currency, instead of producing a GCP-only number nobody can compare to anything.

★ WHERE THE RESULT LIVES, AND WHERE IT MUST NOT.

`MEASURED_NS_PER_DAY_84K` is a **Vast market-ranking table**: a median over N ≥ 3 independent *marketplace*
hosts, used to grade rental offers. A GCP figure is one dedicated VM (N = 1) from a different provider, and
inserting it there would let a single-draw number ride in a column whose whole point is that it is not one.
GCP measurements therefore live in **`gcp-card-bench.json`**, written by CI from the probe's own result lines
and never hand-edited, with `gcp-gpu-facts.md` §1b pointing at it. The 9.5 nm arm is what makes the two
tables comparable without merging them.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ONE FACT, ONE PLACE: the protocol constants and the (edge ↔ particle count) anchor are the calibration
# sweep's, imported rather than copied. A second copy is exactly how the withdrawn 669 ns/day survived a day.
from vast_bench_sweep import (  # noqa: E402
    BENCH_ATOMS as ANCHOR_ATOMS,
    BENCH_BLOCKS,
    BENCH_DT_FS,
    BENCH_EDGE_NM as ANCHOR_EDGE_NM,
    BENCH_TARGET_S,
    BENCH_WARMUP,
)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULT_PATH = os.path.join(HERE, "gcp-card-bench.json")

# The ternary lane's REAL system. Not a round number and not typed from memory: it is the v2pe build's
# measured particle count, the physical fingerprint that `ternary_fep_reduce._SYSTEM_IDENTITY_FIELDS` and
# `watchdog_validate` both key on, and the count in the authoritative census (GH run 30443804729).
TERNARY_N_PARTICLES = 141968


def edge_nm_for_particles(n_particles: int, anchor_atoms: int = ANCHOR_ATOMS,
                          anchor_edge_nm: float = float(ANCHOR_EDGE_NM)) -> float:
    """PURE. Cubic-box edge (nm) whose `addSolvent` fill lands at ~`n_particles`.

    DERIVED from the anchor pair, never from a typed water density: `addSolvent` fills a box at a fixed
    number density for a fixed force field, so N ∝ edge³ and edge = edge_ref · (N/N_ref)^(1/3).
    """
    if n_particles <= 0 or anchor_atoms <= 0 or anchor_edge_nm <= 0:
        raise ValueError("particle counts and the anchor edge must be positive")
    return anchor_edge_nm * (float(n_particles) / float(anchor_atoms)) ** (1.0 / 3.0)


def predicted_particles(edge_nm: float, anchor_atoms: int = ANCHOR_ATOMS,
                        anchor_edge_nm: float = float(ANCHOR_EDGE_NM)) -> int:
    """PURE. Inverse of `edge_nm_for_particles`, so a chosen edge can be checked against what it will build."""
    return int(round(anchor_atoms * (float(edge_nm) / float(anchor_edge_nm)) ** 3))


# The edge actually dispatched for the ternary-sized arm. Rounded to 0.01 nm because the workflow input, the
# result line and this file must agree on a literal string; the rounding error is recorded, not hidden.
TERNARY_EDGE_NM = round(edge_nm_for_particles(TERNARY_N_PARTICLES), 2)
ANCHOR_EDGE_NM_F = float(ANCHOR_EDGE_NM)

# Ternary-sized arm FIRST: if a VM dies mid-probe, the surviving number is the decision-relevant one.
DEFAULT_EDGES = f"{TERNARY_EDGE_NM},{ANCHOR_EDGE_NM_F}"


# =============================================================================================================
# THE CARD MAP — and why one input names the card rather than two naming a machine and an accelerator
# =============================================================================================================
# `gpu-ternary-fep-gcp.yml` pins `g2-standard-*`, which are L4-ONLY machine types carrying a built-in
# accelerator. P100/V100/T4 are the opposite shape: an `n1-*` machine plus an explicit
# `--accelerator=type=...,count=1`. Those two facts are not independent — an `n1-*` with no accelerator boots
# a CPU-only VM that will happily run the bench on the CPU platform and report a real-looking ns/day, and a
# `g2-*` with an `--accelerator` flag is a create-time error. So the workflow takes ONE input (`card`) and
# derives both, which makes the mismatch unrepresentable instead of merely discouraged.
#
# `require_cuda` is belt-and-braces on the same hazard: `gpu_md_bench` raises rather than measuring if the
# CUDA platform is absent (`OPENMM_REQUIRE_CUDA`), so a silent CPU-platform fallback cannot be mistaken for a
# slow card.
class Card:
    __slots__ = ("key", "gce_name", "machine", "accelerator", "quota_metric", "vram_gb", "zones", "note")

    def __init__(self, key, gce_name, machine, accelerator, quota_metric, vram_gb, zones, note=""):
        self.key = key
        self.gce_name = gce_name
        self.machine = machine
        self.accelerator = accelerator      # None = built into the machine type
        self.quota_metric = quota_metric
        self.vram_gb = vram_gb
        self.zones = zones                  # ORDERING HINT ONLY — see `zone_order()`
        self.note = note


# us-central1 zone ordering per card. ⚠ THIS IS A HINT, NOT A FILTER. GCP's published per-zone GPU
# availability moves, and `gcp-gpu-facts.md` §4 is explicit that a launcher which *concludes* from its own
# guesses is how a malformed request got mislabelled "stocked out" for months. Every zone in `ALL_ZONES` is
# tried regardless; this only decides the order, so a card is attempted first where it is most likely to be.
ALL_ZONES = ("us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f")

CARDS = {
    "l4": Card("l4", "NVIDIA L4", "g2-standard-4", None, "NVIDIA_L4_GPUS", 24,
               ("us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"),
               "THE CONTROL ARM. The only GCP card this repo has ever measured, and the denominator of every "
               "ratio here; a probe without it measures speeds nobody can convert into a decision."),
    "t4": Card("t4", "NVIDIA T4", "n1-standard-4", "nvidia-tesla-t4", "NVIDIA_T4_GPUS", 16,
               ("us-central1-b", "us-central1-a", "us-central1-f", "us-central1-c"),
               "THE DISCRIMINATING ARM: bandwidth ~320 GB/s (≈ L4's 300) but FP32 8.1 TFLOPS (vs L4's 30). "
               "If PME here is even partly compute-bound the spec table's 2.2× science/$ row collapses."),
    "p100": Card("p100", "NVIDIA Tesla P100", "n1-standard-4", "nvidia-tesla-p100", "NVIDIA_P100_GPUS", 16,
                 ("us-central1-c", "us-central1-f", "us-central1-a", "us-central1-b"),
                 "The row that would change plans if true: HBM2 ~732 GB/s, claimed faster than L4 AND +18 % "
                 "science/$."),
    "v100": Card("v100", "NVIDIA Tesla V100", "n1-standard-4", "nvidia-tesla-v100", "NVIDIA_V100_GPUS", 16,
                 ("us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"),
                 "HBM2 ~900 GB/s. Priced roughly in proportion to its speed, so it is the arm that tests "
                 "whether the bandwidth heuristic holds at the top end."),
}


def zone_order(card_key: str, preferred: str = "") -> list[str]:
    """PURE. Full zone list, `preferred` first, then the card's hint order, then anything left.

    Never DROPS a zone (see the ⚠ on `ALL_ZONES`): a wrong hint costs one failed create and an echoed error,
    while a hint used as a filter costs a card we actually hold quota for.
    """
    card = CARDS[card_key]
    out: list[str] = []
    for z in (preferred,) + tuple(card.zones) + ALL_ZONES:
        if z and z not in out and z in ALL_ZONES:
            out.append(z)
    return out


def accelerator_flag(card_key: str) -> str:
    """PURE. The `--accelerator` flag this card needs, or '' when the machine type carries it."""
    card = CARDS[card_key]
    return f"--accelerator=type={card.accelerator},count=1" if card.accelerator else ""


# =============================================================================================================
# PRICES — labelled, because they are the one input here that is NOT measured
# =============================================================================================================
# ⚠ THESE ARE PUBLISHED LIST RATES, NOT AN INVOICE. GCP exposes no "credit remaining" or per-run cost API
# without a BigQuery billing export (`credit-status.json` says so and that is still true), so a probe cannot
# measure what it was charged. The workflow's `--parse-skus` mode reads the Cloud Billing Catalog API and
# OVERRIDES these when it succeeds, recording which path was used in `price_provenance`; these constants are
# the fallback and every consumer is expected to carry the label rather than quote the number bare.
#
# They are per-COMPONENT rather than per-machine on purpose: a bundled "g2-standard-4 = $X" number cannot be
# checked against anything, whereas cores/RAM/GPU can each be matched to a SKU.
LIST_PRICE_USD_PER_H = {
    # component            $/h    what it is
    "n1_core":            0.031611,   # N1 Predefined Instance Core, Americas, on-demand
    "n1_ram_gb":          0.004237,   # N1 Predefined Instance Ram (per GB), Americas, on-demand
    "gpu_t4":             0.35,       # Nvidia Tesla T4 GPU, Americas, on-demand
    "gpu_p100":           1.46,       # Nvidia Tesla P100 GPU, Americas, on-demand
    "gpu_v100":           2.48,       # Nvidia Tesla V100 GPU, Americas, on-demand
    "g2_standard_4":      0.708,      # G2 bundles its L4; billed as G2 core+RAM, not as a separate GPU SKU
}
LIST_PRICE_SOURCE = ("GCP published us-central1 ON-DEMAND list rates. NOT a measured invoice — GCP exposes no "
                     "per-run cost without a BigQuery billing export (credit-status.json). Superseded "
                     "automatically whenever the Cloud Billing Catalog probe succeeds.")

# vCPU / RAM of each machine type used above, so a machine price is DERIVED from components.
MACHINE_SHAPE = {
    "n1-standard-4": (4, 15.0),
    "n1-standard-8": (8, 30.0),
    "g2-standard-4": (4, 16.0),
}


def machine_usd_per_h(card_key: str, prices: dict | None = None) -> float:
    """PURE. On-demand $/h for the whole VM (machine + its GPU). DERIVED from components, never typed."""
    p = dict(LIST_PRICE_USD_PER_H)
    if prices:
        p.update({k: v for k, v in prices.items() if isinstance(v, (int, float))})
    card = CARDS[card_key]
    if card.machine == "g2-standard-4":
        return float(p["g2_standard_4"])
    cores, ram_gb = MACHINE_SHAPE[card.machine]
    return cores * float(p["n1_core"]) + ram_gb * float(p["n1_ram_gb"]) + float(p[f"gpu_{card_key}"])


def science_per_dollar(ns_per_day: float, usd_per_h: float) -> float:
    """PURE. ns of MD per dollar per hour of wall clock = ns/day ÷ (24 · $/h). The figure of merit for a
    DOLLAR-bound lane (Open decision 5): calendar is not scarce on GCP, money is."""
    if usd_per_h <= 0:
        raise ValueError("usd_per_h must be positive")
    return (ns_per_day / 24.0) / usd_per_h


def usd_per_ns(ns_per_day: float, usd_per_h: float) -> float:
    """PURE. The reciprocal, in the units the rest of the repo grades rentals in (CLAUDE.md §1)."""
    return usd_per_h / (ns_per_day / 24.0)


# =============================================================================================================
# RESULT PARSING — the probe's own output line is the only source of a number here
# =============================================================================================================
def parse_result_line(line: str) -> dict:
    """PURE. `gpu_md_bench`'s single `BENCH_RESULT ...` line -> dict. Values are `k=v`, space separated, so a
    value containing a space is already underscored by the producer (see its own comment)."""
    out: dict = {}
    for kv in str(line).split():
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        out[k] = v
    for k in ("atoms", "steps", "blocks", "attempt", "minimize_iters"):
        if k in out:
            try:
                out[k] = int(out[k])
            except ValueError:
                pass
    for k in ("ns_per_day", "sd", "cv", "wall_s", "dt_fs", "final_temp_k"):
        if k in out:
            try:
                out[k] = float(out[k])
            except ValueError:
                pass
    return out


# A measurement is admitted only if it carries its own evidence of being trustworthy. Same three gates the
# Vast calibration sweep applies, for the same reason: a diverged system integrates fast and reports a large,
# entirely fake ns/day, and a contended host reports a mean that hides 2× block-to-block scatter.
MAX_CV = 0.05


def admit(rec: dict) -> tuple[bool, str]:
    """PURE. (admissible, why-not). Rejects rather than averaging a bad measurement into a ranking."""
    if rec.get("status") != "OK":
        return False, f"status={rec.get('status')!r} (physics check failed or the bench errored)"
    if not rec.get("ns_per_day"):
        return False, "no ns_per_day on the result line"
    if rec.get("platform") != "CUDA":
        return False, f"platform={rec.get('platform')!r} — a non-CUDA run prices a stack we do not use"
    cv = rec.get("cv")
    if cv is None or cv > MAX_CV:
        return False, f"cv={cv} exceeds {MAX_CV:.0%} — block-to-block scatter, not a steady-state rate"
    return True, ""


def card_from_device(device: str) -> str | None:
    """PURE. The card key a reported CUDA `DeviceName` corresponds to, or None.

    ⚠ VERIFY, NEVER ASSUME. The `--accelerator` flag says what we ASKED for; `DeviceName` says what OpenMM is
    actually running on. `vast_cost_model`'s variant-SKU block records what a name-based guess costs when the
    two disagree, and a card ratio built on a mislabelled card is worse than no ratio at all.
    """
    d = re.sub(r"[^A-Z0-9]", "", str(device or "").upper())
    for key, pat in (("l4", "L4"), ("t4", "T4"), ("p100", "P100"), ("v100", "V100")):
        if pat in d:
            return key
    return None


def merge_record(doc: dict, rec: dict, *, card: str, edge_nm: float, run_id: str = "",
                 zone: str = "", machine: str = "", provisioning: str = "") -> dict:
    """Fold one admitted result line into the artifact. LAST WRITE WINS per (card, edge) and the whole
    history is kept, so a re-probe supersedes visibly instead of silently."""
    doc.setdefault("_schema", 1)
    doc.setdefault("measurements", [])
    entry = dict(rec)
    entry.update({"card": card, "edge_nm": float(edge_nm), "run_id": str(run_id), "zone": zone,
                  "machine": machine, "provisioning": provisioning,
                  "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    doc["measurements"].append(entry)
    return doc


def latest_by_card_edge(doc: dict) -> dict:
    """PURE. {(card, edge_nm_str): most recent admitted measurement}."""
    out: dict = {}
    for m in doc.get("measurements", []):
        ok, _ = admit(m)
        if not ok:
            continue
        out[(m.get("card"), f"{float(m.get('edge_nm', 0)):.2f}")] = m
    return out


def ratio_table(doc: dict, edge_nm: float, prices: dict | None = None, reference: str = "l4") -> list[dict]:
    """PURE. One row per card at `edge_nm`, with the ratio to the reference card and science-per-dollar.

    DERIVED, never typed: every number is computed from the admitted result lines plus `machine_usd_per_h`.
    Cards with no admitted measurement at this size are ABSENT rather than estimated — the same rule
    `MEASURED_NS_PER_DAY_84K` applies, and for the same reason.
    """
    latest = latest_by_card_edge(doc)
    key = f"{float(edge_nm):.2f}"
    ref = latest.get((reference, key))
    rows = []
    for card_key in CARDS:
        m = latest.get((card_key, key))
        if not m:
            continue
        nsd = float(m["ns_per_day"])
        uph = machine_usd_per_h(card_key, prices)
        rows.append({
            "card": card_key,
            "gce_name": CARDS[card_key].gce_name,
            "machine": CARDS[card_key].machine,
            "ns_per_day": round(nsd, 2),
            "ns_per_h": round(nsd / 24.0, 3),
            "cv": m.get("cv"),
            "atoms": m.get("atoms"),
            "x_reference": round(nsd / float(ref["ns_per_day"]), 3) if ref else None,
            "usd_per_h": round(uph, 4),
            "usd_per_ns": round(usd_per_ns(nsd, uph), 6),
            "science_per_usd": round(science_per_dollar(nsd, uph), 3),
        })
    rows.sort(key=lambda r: -(r["science_per_usd"]))
    for r in rows:
        base = next((x for x in rows if x["card"] == reference), None)
        r["x_reference_science_per_usd"] = (
            round(r["science_per_usd"] / base["science_per_usd"], 3) if base else None)
    return rows


# =============================================================================================================
# Cloud Billing Catalog probe (best-effort, $0, runner-side)
# =============================================================================================================
# Turns the list-price constants above into MEASURED rates when it works. It is best-effort on purpose: the
# catalog needs `cloudbilling.googleapis.com` enabled and its SKU descriptions are free text, so an
# unavailable or ambiguous match must degrade to the labelled fallback rather than fail a probe that is
# otherwise fine. Ambiguity is treated as failure — two SKUs matching one component means we do not know the
# price, and a confidently-wrong price is the failure mode this whole file is about.
SKU_PATTERNS = {
    "n1_core":       (r"^N1 Predefined Instance Core running in Americas$", 1.0),
    "n1_ram_gb":     (r"^N1 Predefined Instance Ram running in Americas$", 1.0),
    "gpu_t4":        (r"^Nvidia Tesla T4 GPU running in Americas$", 1.0),
    "gpu_p100":      (r"^Nvidia Tesla P100 GPU running in Americas$", 1.0),
    "gpu_v100":      (r"^Nvidia Tesla V100 GPU running in Americas$", 1.0),
    "g2_core":       (r"^G2 Instance Core running in Americas$", 1.0),
    "g2_ram_gb":     (r"^G2 Instance Ram running in Americas$", 1.0),
}


# Compute Engine's service id in the catalog. Stable and public; the SKUs under it are what a Compute bill is
# itemised from.
COMPUTE_SERVICE_ID = "6F81-5844-456A"


def fetch_skus(token: str, max_pages: int = 6) -> list:
    """Page the Cloud Billing Catalog with stdlib urllib. Returns [] on any failure — see the ⚠ above: this
    path exists to REPLACE typed constants when it works, never to invent a price when it does not."""
    import urllib.error
    import urllib.request

    out: list = []
    page = ""
    for _ in range(max_pages):
        url = (f"https://cloudbilling.googleapis.com/v1/services/{COMPUTE_SERVICE_ID}/skus"
               f"?currencyCode=USD&pageSize=5000" + (f"&pageToken={page}" if page else ""))
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as fh:
                doc = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            print(f"[prices] catalog request failed ({type(exc).__name__}: {exc}) — falling back")
            return out
        out.extend(doc.get("skus") or [])
        page = doc.get("nextPageToken") or ""
        if not page:
            break
    print(f"[prices] catalog returned {len(out)} SKUs")
    return out


def _sku_unit_price(sku: dict) -> float | None:
    try:
        tr = sku["pricingInfo"][0]["pricingExpression"]["tieredRates"][-1]["unitPrice"]
        return int(tr.get("units", 0)) + int(tr.get("nanos", 0)) / 1e9
    except Exception:  # noqa: BLE001
        return None


def parse_skus(payload: list, region: str = "us-central1") -> tuple[dict, list[str]]:
    """PURE. (prices, notes) from a Cloud Billing Catalog SKU list. On-demand only."""
    prices: dict = {}
    notes: list[str] = []
    hits: dict = {}
    for sku in payload:
        if region not in (sku.get("serviceRegions") or []):
            continue
        cat = sku.get("category") or {}
        if cat.get("usageType") != "OnDemand":
            continue
        desc = str(sku.get("description", "")).strip()
        for comp, (pat, _mult) in SKU_PATTERNS.items():
            if re.match(pat, desc):
                price = _sku_unit_price(sku)
                if price is not None:
                    hits.setdefault(comp, set()).add(round(price, 8))
    for comp, vals in hits.items():
        if len(vals) == 1:
            prices[comp] = next(iter(vals))
        else:
            notes.append(f"{comp}: {len(vals)} distinct SKU prices {sorted(vals)} — AMBIGUOUS, not used")
    if "g2_core" in prices and "g2_ram_gb" in prices:
        cores, ram = MACHINE_SHAPE["g2-standard-4"]
        prices["g2_standard_4"] = cores * prices["g2_core"] + ram * prices["g2_ram_gb"]
    missing = [c for c in ("n1_core", "n1_ram_gb", "gpu_t4", "gpu_p100", "gpu_v100", "g2_standard_4")
               if c not in prices]
    if missing:
        notes.append(f"missing components {missing} — falling back to the labelled list rates for those")
    return prices, notes


# =============================================================================================================
# CLI
# =============================================================================================================
def provisional_rows(doc: dict, edge_nm: float, reference: str = "l4") -> list[dict]:
    """PURE. Measurements the admission gate REFUSED, with the reason and the ratio they imply.

    ★★ A REFUSED MEASUREMENT MUST NOT SIMPLY VANISH (CLAUDE.md §1, the rule that a guard doing its job and a
    guard being ignored must never render alike — here in its measurement form).

    `admit()` exists so an untrustworthy number never enters a rate table, and that must not be weakened. But
    "not table-grade" and "tells us nothing" are different claims, and conflating them throws away the most
    decision-relevant observation of 2026-07-31: the T4 was refused on CV = 5.6 % against a 5 % ceiling, while
    reading **0.31× the L4** where the planning table claimed **1.1×**. A 3.5× discrepancy cannot be
    manufactured by 5.6 % of block scatter, so the RANKING it implies is safe even though the RATE is not.

    So refused measurements are reported here, separately, labelled, and never merged into `ratio_table`.
    """
    latest: dict = {}
    for m in doc.get("measurements", []):
        if m.get("admitted"):
            continue
        latest[(m.get("card"), f"{float(m.get('edge_nm', 0)):.2f}")] = m
    key = f"{float(edge_nm):.2f}"
    ref = latest_by_card_edge(doc).get((reference, key))
    out = []
    for card_key in CARDS:
        m = latest.get((card_key, key))
        if not m or not m.get("ns_per_day"):
            continue
        nsd = float(m["ns_per_day"])
        out.append({
            "card": card_key,
            "ns_per_day": round(nsd, 2),
            "x_reference": round(nsd / float(ref["ns_per_day"]), 3) if ref else None,
            "rejected_because": m.get("rejected_because", ""),
            "device": m.get("device", ""),
            "provisioning": m.get("provisioning", ""),
        })
    return out


def markdown_table(doc: dict, prices: dict | None = None) -> str:
    """The §1b table, GENERATED from the artifact so the document cannot drift from the measurement.

    CLAUDE.md rule 1: a table a human reads before choosing a card is exactly the kind of derived value that
    must not be hand-carried. `tests/test_gcp_card_bench.py::test_the_documented_table_is_the_measured_table`
    re-checks the pasted result against the artifact on every CI run.
    """
    out = [
        "| card | machine | ns/day @141,887p | ×L4 | ns/day @84,534p | $/h | $/ns @141,887p | ns per $ | ×L4 ns/$ |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    big = {r["card"]: r for r in ratio_table(doc, TERNARY_EDGE_NM, prices)}
    small = {r["card"]: r for r in ratio_table(doc, ANCHOR_EDGE_NM_F, prices)}
    for card in sorted(big, key=lambda c: -big[c]["science_per_usd"]):
        r = big[card]
        s = small.get(card)
        # A card can legitimately have one size and not the other (a VM that died between the two arms), so
        # the anchor cell degrades to an em dash rather than crashing the generator.
        anchor = f"{s['ns_per_day']:.2f}" if s else "—"
        out.append(
            f"| **{card.upper()}** | `{r['machine']}` | **{r['ns_per_day']:.2f}** | "
            f"**{r['x_reference']:.2f}×** | {anchor} | {r['usd_per_h']:.3f} | "
            f"{r['usd_per_ns']:.4f} | **{r['science_per_usd']:.2f}** | "
            f"**{r['x_reference_science_per_usd']:.2f}×** |")
    prov = provisional_rows(doc, TERNARY_EDGE_NM)
    if prov:
        out.append("")
        out.append("**⚠ REFUSED BY THE ADMISSION GATE — a RANKING, not a rate.** These are not in the table "
                   "above and must never be quoted as throughput. They are shown because "
                   "`admit()`-refused is not the same claim as uninformative: where the implied ratio dwarfs "
                   "the reason for refusal, the ordering it gives is still safe.")
        out.append("")
        out.append("| card | ns/day @141,887p (PROVISIONAL) | implied ×L4 | refused because |")
        out.append("|---|---|---|---|")
        for r in prov:
            out.append(f"| {r['card'].upper()} (`{r['device']}`, {r['provisioning']}) | {r['ns_per_day']:.2f} "
                       f"| **~{r['x_reference']:.2f}×** | {r['rejected_because']} |")
    return "\n".join(out)


def _emit_env(card_key: str, zone: str, edges: str) -> int:
    card = CARDS[card_key]
    lines = [
        f"BENCH_CARD={card.key}",
        f"BENCH_GCE_NAME={card.gce_name}",
        f"MACHINE={card.machine}",
        f"ACCEL={accelerator_flag(card.key)}",
        f"QUOTA_METRIC={card.quota_metric}",
        f"ZONES={' '.join(zone_order(card.key, zone))}",
        f"BENCH_EDGES={edges}",
        f"BENCH_DT_FS={BENCH_DT_FS}",
        f"BENCH_BLOCKS={BENCH_BLOCKS}",
        f"BENCH_TARGET_S={BENCH_TARGET_S}",
        f"BENCH_WARMUP={BENCH_WARMUP}",
        f"BENCH_VRAM_GB={card.vram_gb}",
    ]
    for ln in lines:
        print(ln)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-env", action="store_true", help="print KEY=VALUE for $GITHUB_ENV")
    ap.add_argument("--card", default="l4", choices=sorted(CARDS))
    ap.add_argument("--zone", default="")
    ap.add_argument("--edges", default=DEFAULT_EDGES)
    ap.add_argument("--record", help="a BENCH_RESULT line to fold into the artifact")
    ap.add_argument("--edge-nm", type=float, help="edge the --record line was measured at")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--machine", default="")
    ap.add_argument("--provisioning", default="")
    ap.add_argument("--parse-skus", help="Cloud Billing Catalog JSON (a list, or {'skus': [...]})")
    ap.add_argument("--fetch-prices", action="store_true",
                    help="page the Cloud Billing Catalog using $GCP_ACCESS_TOKEN, then --parse-skus it")
    ap.add_argument("--prices-out", default=os.path.join(HERE, "gcp-price-probe.json"))
    ap.add_argument("--report", action="store_true", help="print the measured table")
    ap.add_argument("--markdown-table", action="store_true",
                    help="emit the gcp-gpu-facts.md §1b table, generated from the artifact")
    ap.add_argument("--artifact", default=RESULT_PATH)
    args = ap.parse_args(argv)

    if args.emit_env:
        return _emit_env(args.card, args.zone, args.edges)

    if args.parse_skus or args.fetch_prices:
        if args.fetch_prices:
            token = os.environ.get("GCP_ACCESS_TOKEN", "").strip()
            if not token:
                print("[prices] no GCP_ACCESS_TOKEN — keeping the labelled list rates")
                return 0
            skus = fetch_skus(token)
            if not skus:
                print("::warning title=PRICE PROBE FELL BACK::the Cloud Billing Catalog returned nothing; "
                      "science-per-dollar uses gcp_card_bench.LIST_PRICE_USD_PER_H, which are PUBLISHED LIST "
                      "RATES and not a measured invoice. Every consumer must carry that label.")
                return 0
        else:
            raw = json.load(open(args.parse_skus))
            skus = raw.get("skus", raw) if isinstance(raw, dict) else raw
        prices, notes = parse_skus(skus)
        doc = {"_note": "MEASURED from the Cloud Billing Catalog API; supersedes gcp_card_bench."
                        "LIST_PRICE_USD_PER_H for the components present here.",
               "region": "us-central1", "usage_type": "OnDemand",
               "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "prices_usd_per_h": prices, "notes": notes}
        with open(args.prices_out, "w") as fh:
            json.dump(doc, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print(f"[prices] wrote {args.prices_out}: {len(prices)} components; notes={notes or 'none'}")
        return 0

    doc = {}
    if os.path.isfile(args.artifact):
        doc = json.load(open(args.artifact))

    if args.record:
        rec = parse_result_line(args.record)
        ok, why = admit(rec)
        seen = card_from_device(rec.get("device", ""))
        if seen and seen != args.card:
            print(f"::error title=CARD MISMATCH::asked for {args.card} but OpenMM reports device="
                  f"{rec.get('device')!r} (={seen}). NOT recorded — a ratio built on a mislabelled card is "
                  f"worse than no ratio.")
            return 1
        if not ok:
            print(f"::warning title=MEASUREMENT REJECTED::{args.card} @ {args.edge_nm} nm: {why}. "
                  f"Recorded as rejected so the attempt is visible, but it enters no table.")
        rec["admitted"] = ok
        rec["rejected_because"] = why
        merge_record(doc, rec, card=args.card, edge_nm=args.edge_nm or 0.0, run_id=args.run_id,
                     zone=args.zone, machine=args.machine, provisioning=args.provisioning)
        with open(args.artifact, "w") as fh:
            json.dump(doc, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print(f"[record] {args.card} @ {args.edge_nm} nm -> {args.artifact} (admitted={ok})")

    prices = {}
    pp = os.path.join(HERE, "gcp-price-probe.json")
    if os.path.isfile(pp):
        prices = (json.load(open(pp)) or {}).get("prices_usd_per_h") or {}

    if args.markdown_table:
        print(markdown_table(doc, prices))

    if args.report:
        for edge in (TERNARY_EDGE_NM, ANCHOR_EDGE_NM_F):
            rows = ratio_table(doc, edge, prices)
            if not rows:
                continue
            print(f"\n=== measured @ edge {edge} nm (~{predicted_particles(edge):,} particles) ===")
            print(f"{'card':6} {'ns/day':>9} {'ns/h':>8} {'xL4':>6} {'$/h':>8} {'$/ns':>10} "
                  f"{'ns/$':>8} {'xL4 ns/$':>9}")
            for r in rows:
                print(f"{r['card']:6} {r['ns_per_day']:9.2f} {r['ns_per_h']:8.3f} "
                      f"{(r['x_reference'] or 0):6.2f} {r['usd_per_h']:8.4f} {r['usd_per_ns']:10.6f} "
                      f"{r['science_per_usd']:8.3f} {(r['x_reference_science_per_usd'] or 0):9.2f}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
