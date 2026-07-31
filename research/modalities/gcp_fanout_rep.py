#!/usr/bin/env python3
"""
GCP L4 — ONE step-1 fan-out REPLICATE unit, on the free (expiring) GCP trial credit.

WHY THIS LANE EXISTS
--------------------
`GPUS_ALL_REGIONS = 1` (gcp-gpu-facts.md #1) makes GCP a **single serial worker**, and trimcrae's standing
instruction for it is *"Treat it as a single GPU in your fleet"* — one unit at a time, never a programme.
This module is that one unit's wiring, and nothing else.

THE UNIT, and why it is this one:
  * STRATEGY.md's `[ ]` item *"Step 1 fan-out · REPLICATES ON THE OPEN CYCLE"* is **unowned** in
    `work-ledger.json` — no lane, no workflow, no agent is carrying it.
  * `cycle_3carbonyl` does **not** close (`step1-fanout-map.json` → `cycle_closure`, `sum_kcal` vs
    `tol_kcal`), and at n = 1 "one edge is wrong" and "three unlucky draws" are the same observation.
  * The binary RBFE lane owns **no** measured replicate SD; the program transfers the ternary lane's
    everywhere, including onto edges it was never measured on.
  * CLAUDE.md §5 defaults *more replicates* to **NO** — and `congeneric_fanout.replicate_units`' own
    docstring records why this is the exception: the standard-rigor result is ambiguous and the ambiguity is
    decision-relevant (it decides whether those three ddG values may be quoted at all).

WHY GCP RATHER THAN VAST. The replicate axis is fully built on the Vast lane (`FANOUT_REPLICATE_EDGES` /
`FANOUT_REPLICATES`) and has simply never been bought — it costs real dollars there. Here it costs **$0**:
GCP trial credit, a SEPARATE LEDGER that expires 2026-10-10 and is otherwise stranded (CLAUDE.md §6). Vast
capacity stays free for the lanes that need bursts.

★★ WHAT MAKES THIS A REPLICATE AND NOT A DIFFERENT EXPERIMENT — the three things held byte-identical:
  1. **The staged inputs.** `congeneric_pose_stage.py` writes ONE common-mode pose tree, and all 18 landed
     edges read it. This lane MIRRORS that exact tree S3 -> GCS (`mode=mirror`, content-verified by size) and
     reads the copy. It never re-stages, never re-docks, never re-fetches from RCSB. That is the difference
     between this and the cross-lane comparison in STRATEGY Appendix A 45, where two arms each did their own
     solvation and ended up 675 waters apart.
  2. **The container.** The VM runs the SAME `triskit23/nr4a3fep` image the Vast fan-out runs, pulled by
     digest-free tag but from the same repository — so openfe/openmmtools/pymbar are the versions that
     PRODUCED the n=0 numbers. CLAUDE.md §6: analysing (or generating) with a different pymbar can move the
     MBAR numbers, and an ad-hoc conda solve is a silent protocol deviation.
  3. **The engine call.** Every env var comes from `congeneric_fanout.unit_env`, never typed here. The only
     deliberate differences are `SEED` (which IS the replicate) and the object store (GCS, via the engine's
     own long-standing `RBFE_SPOT_COMMIT_GCS` / `RBFE_SETUP_CACHE_GCS` paths — not a port, a config).

⚠ WHAT IS **NOT** HELD IDENTICAL, and must be stated wherever the SD is quoted: the **card**. n=0 ran on
Vast marketplace RTX 4090/5090-class GPUs; this runs on a GCE L4. MD is not bitwise reproducible across GPUs
in any case — that is part of what a replicate averages over — but the resulting SD is a
sampling-plus-hardware scatter, not a pure sampling scatter, and `provenance()` below stamps the venue into
the artifact so no reader has to reconstruct it.

TEARDOWN — the part that must work with no agent awake
------------------------------------------------------
gcp-gpu-facts.md §6: **a GCE VM cannot delete itself** (the in-VM trap runs and GCE refuses it), and §6b:
`gcp-reap-vms.yml` has no `schedule:` and never fires by itself. So this lane has three bounds, in order of
how little they depend on anything being alive:

  1. **`--max-run-duration` + `--instance-termination-action=DELETE`, set at CREATE.** Enforced by GCE
     itself. Depends on no agent, no cron, no CI and no in-VM code. It cannot be raised later
     (gcp-gpu-facts.md §3b), so `max_run_seconds()` sizes it up front and a non-`run` mode never inherits a
     leg's cap — the same rule `gpu-ternary-fep-gcp.yml` learned.
  2. **`reap_decision()`, from CI.** Evidence-based and **age is never consulted**: a VM is deleted only when
     the unit's OWN result object is already in GCS and the VM predates it — i.e. there is provably no
     sampling left to lose. That is the ternary watchdog's DONE test, applied to this lane's key contract.
     Every other shape (no result, result older than the VM, unreadable timestamp, unresolvable unit) is
     REFUSED, loudly, and reaps nothing.
  3. **Per-leg idempotence + a continuous GCS commit store.** A cap boundary or a crash costs the detection
     latency, never the sampling: the next dispatch skips a leg whose JSON is already in GCS and resumes the
     other from its last committed generation.

Usage (CI reads `--shell`, humans read `--json`):
    python3 gcp_fanout_rep.py plan --edge cycle_3carbonyl --replicate 1 --pick 0 --shell
    python3 gcp_fanout_rep.py reap --unit-id <id> --vm-created <RFC3339> --result-updated <RFC3339|''> --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from congeneric_fanout import (  # noqa: E402
    PRIMARY_RECEPTOR,
    checkpoint_prefix,
    replicate_units,
    resolve_edge_ids,
    result_key,
    unit_env,
)

# ---- constants that have ONE home here ---------------------------------------------------------------

#: GCS bucket, derived from the GCP project the WIF identity resolves to. Same bucket the ternary lane uses.
BUCKET_SUFFIX = "-rbfe-ckpt"

#: The staged common-mode pose tree. `STAGE_PREFIX` is the Vast lane's default and is mirrored VERBATIM;
#: `RESULT_PREFIX` is where this lane's replicate results land. Both mirror `congeneric_fanout_vast`'s
#: defaults deliberately — a replicate that wrote somewhere else would be invisible to the collector that
#: eventually reduces it.
STAGE_PREFIX = "nr4a3-step1-fanout/stage"
RESULT_PREFIX = "nr4a3-step1-fanout/results"

#: GCE labels the VM carries so a forgotten instance can be resolved back to its unit WITHOUT age.
#: The unit_id itself is NOT a label: `e_cw_ms_free_acid__cw_bio_primary_amide__neutral_acid__neutral__r1`
#: is 66 characters and GCE caps a label value at 63, so labelling it would truncate — silently, into a
#: value that could collide with a sibling. edge+replicate are short, and `unit_for()` reconstructs the
#: unit_id from them through the same pure function that minted it.
LABEL_LANE = "s1frep"

#: Cap sizes. A full edge is 2 legs x 12 windows; the 18 landed edges cost ~12-68 billed GPU-h EACH on
#: Vast 4090/5090-class hardware (`step1-fanout-map.json` -> `realised_rentals`), and the L4 measures
#: 1/2.7-1/3.5 of a 4090 (gcp-gpu-facts.md §1c). 48 h is therefore an ESTIMATE sized above one complex leg
#: and below the ternary lane's 72 h — stated as an estimate, not a measurement. A boundary is cheap here
#: (per-leg idempotence + commit store), an un-reaped VM is not, so the cap errs short.
MAX_RUN_S_RUN = 172800          # 48 h
MAX_RUN_S_NON_RUN = 25200       # 7 h — a smoke/mirror is minutes; it writes no result object, so no reaper
                                # can key on it and this cap is its ONLY bound (the §6c rule, same reason).

N_WINDOWS = 12

#: Every refusal `reap_decision` can return. A caller that sees anything but "reap" must not delete.
REFUSALS = (
    "no_result_object",
    "result_older_than_vm",
    "unreadable_timestamp",
    "unknown_unit",
    "smoke_not_terminal",
)


# ---- unit resolution ---------------------------------------------------------------------------------

def units_for(edge, replicate):
    """Every replicate unit named by `edge` (an edge id OR a cycle id) at index `replicate`.

    Delegates wholly to `congeneric_fanout.replicate_units`, which fails closed on replicate 0 and on a name
    that resolves to nothing. Nothing about a unit is constructed here — rule 1: the fan-out module is the
    one home of what a unit IS, and this lane only decides which one to buy."""
    return replicate_units([edge], (int(replicate),))


def unit_for(edge_id, replicate):
    """The single unit for one EXACT edge id at one replicate index. Fails closed on a cycle id.

    This is the reaper's path: it is handed `s1f-edge` + `s1f-rep` off a VM's labels and must reconstruct
    exactly the unit that VM was bought for. A cycle id would resolve to three units and there would be no
    principled way to pick one, so it is refused rather than guessed."""
    ids = resolve_edge_ids([edge_id])
    if len(ids) != 1:
        raise ValueError(
            f"{edge_id!r} resolves to {len(ids)} edges; the reaper needs exactly one "
            f"(a cycle id is a launch-time convenience, never a teardown-time one)"
        )
    got = units_for(ids[0], replicate)
    if len(got) != 1:
        raise ValueError(f"{edge_id!r} r{replicate} resolved to {len(got)} units, expected 1")
    return got[0]


def gcs_uris(unit, bucket):
    """Every GCS location this unit touches. Keys come from `congeneric_fanout`, never from a format string
    here, so a GCP replicate is content-addressed identically to a Vast one and the eventual collector finds
    it without being taught a second convention."""
    res = result_key(unit, RESULT_PREFIX)
    ck = checkpoint_prefix(unit, RESULT_PREFIX)
    base = f"{RESULT_PREFIX}/{unit['unit_id']}"
    return {
        "bucket": bucket,
        "stage_uri": f"gs://{bucket}/{STAGE_PREFIX}",
        "result_key": res,
        "result_uri": f"gs://{bucket}/{res}",
        "ckpt_prefix": ck,
        "ckpt_uri": f"gs://{bucket}/{ck}",
        "unit_uri": f"gs://{bucket}/{base}",
        "leg_key": {lg: f"{base}/leg_{unit['receptor']}_{lg}.json" for lg in ("complex", "solvent")},
        "log_uri": f"gs://{bucket}/{base}/run.log",
        "phase_uri": f"gs://{bucket}/{base}/phase.txt",
    }


def leg_env(unit, leg_kind, bucket, n_windows=N_WINDOWS):
    """The full env for one alchemical leg on the VM.

    `unit_env` supplies the science half (MODE/LEG/RECEPTOR/LIGAND_A/LIGAND_B/N_WINDOWS/SEED/...) and is
    NEVER second-guessed. This function adds only the object-store half, and it adds the GCS variables the
    engine has supported since 2026-07-18 (`RBFE_SPOT_COMMIT_GCS`, `RBFE_SETUP_CACHE_GCS`) — the same names
    the GCP ternary lane already uses, so no engine change is involved anywhere in this lane."""
    u = gcs_uris(unit, bucket)
    env = dict(unit_env(unit, leg_kind, n_windows=n_windows))
    env.update({
        "RBFE_SPOT_SAFE": "1",
        "RBFE_SPOT_COMMIT_GCS": f"{u['ckpt_uri']}/{leg_kind}",
        # Commit cadence: identical to the Vast fan-out's (20 warmup / 40 production), so a resumed
        # generation is the same granularity the n=0 edges committed at. CLAUDE.md's checkpoint rule is
        # satisfied by the store itself — `GCSCommitStore` uploads each generation AS IT IS WRITTEN, which
        # is the "Continuous" shape, not an end-of-job sync.
        "RBFE_WARMUP_CKPT_ITERS": "20",
        "RBFE_PROD_CKPT_ITERS": "40",
        "OPENMM_PLUGIN_DIR": "/opt/mamba/envs/rbfe/lib/plugins",
    })
    return env


def provenance(unit, bucket, card="nvidia-l4", machine_type=None):
    """The stamp that goes beside the result so nobody has to reconstruct where it ran.

    ⚠ It records the CARD explicitly, because that is the one axis this replicate does not hold identical to
    n=0 and the SD it feeds must not be read as pure sampling scatter."""
    return {
        "venue": "gcp",
        "zone_region": "us-central1",
        "card": card,
        "machine_type": machine_type,
        "ledger": "GCP trial credit — a SEPARATE LEDGER, never summed into realized or ladder spend "
                  "(CLAUDE.md §6). Expires 2026-10-10.",
        "usd_real": 0.0,
        "container": "docker.io/triskit23/nr4a3fep:latest — the SAME image the Vast fan-out runs, so "
                     "openfe/openmmtools/pymbar match the versions that produced the n=0 edges",
        "inputs": f"gs://{bucket}/{STAGE_PREFIX} — a byte-verified mirror of the S3 common-mode pose tree "
                  f"every n=0 edge read; this lane never re-stages or re-docks",
        "unit_id": unit["unit_id"],
        "replicate": int(unit.get("replicate") or 0),
        "seed": unit_env(unit, "complex").get("SEED"),
        "not_held_identical": ["gpu_card (n=0 ran on Vast 4090/5090-class; this is a GCE L4)"],
        "uncertainty_note": "A replicate SD built from this unit and its n=0 sibling is a "
                            "sampling-AND-hardware scatter, not a pure sampling scatter. Say so.",
    }


# ---- caps ---------------------------------------------------------------------------------------------

def max_run_seconds(mode):
    """The create-time cap. A non-`run` mode NEVER inherits a leg's cap.

    Reason, verbatim from `gpu-ternary-fep-gcp.yml`'s equivalent rule (gcp-gpu-facts.md §6c layer 3): a
    non-run mode writes no leg result object, so neither reap path can retire it and the cap is its ONLY
    bound. Lending it a leg's cap converts a five-minute smoke into a two-day hold on the single GPU."""
    return MAX_RUN_S_RUN if mode == "run" else MAX_RUN_S_NON_RUN


# ---- the reaper ---------------------------------------------------------------------------------------

def _parse_ts(s):
    if not s:
        return None
    s = str(s).strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


#: The markers a SMOKE writes as its last act, one per outcome. Both are terminal: the container has
#: returned and there is nothing left on the box. Matched as a prefix of the phase line.
SMOKE_TERMINAL = ("SMOKE-OK", "SMOKE-FAIL")

#: ★★ TERMINAL IN **EVERY** MODE — the gap the first real leg found, at 7:20 PM ET 2026-07-31.
#: The parity guard refused, the startup script exited 3, and the VM went on holding the account's ONE GPU
#: with nothing running on it: a `run` writes no ddg.json, so the result-object clause could never retire it,
#: and its only bound was the 48 h create-time cap — for a job that had died in four minutes.
#: `BOOTSTRAP-FAIL` is a DISTINCT prefix from the smoke's own SMOKE-OK/SMOKE-FAIL for exactly that reason:
#: it is written ONLY on paths that exit BEFORE `run_leg` is ever called, in either mode. So no sampling has
#: started, no checkpoint exists, and reaping on it can never destroy work — which is what lets it apply to
#: a `run`, where a phase marker is otherwise progress and must never license a delete.
BOOTSTRAP_TERMINAL = ("BOOTSTRAP-FAIL",)


def reap_decision(unit_id, vm_created, result_updated, vm_mode="run", phase=None):
    """May this VM be deleted? **AGE IS NEVER CONSULTED.**

    The one condition that permits a delete is the ternary watchdog's DONE test, transplanted: the unit's own
    result object is in GCS **and** the VM was created before that object was last written. Both halves are
    load-bearing —
      * without the object, a running leg would be destroyed mid-sampling;
      * without the ordering, a VM launched to compute the NEXT thing would be destroyed because a
        PREVIOUS run's result happens to sit at the same key. That is the shape `gcp-reap-vms.yml` records a
        dry_run of: an age rule that would have killed a healthy mid-production leg.
    Anything unreadable REFUSES. A reaper that guesses is worse than no reaper, because it looks like one.
    """
    if not unit_id:
        return {"action": "refuse", "cause": "unknown_unit", "why":
                "no unit id resolved for this VM — nothing to key a result on, so nothing may be deleted"}
    vm = _parse_ts(vm_created)
    if vm is None:
        return {"action": "refuse", "cause": "unreadable_timestamp", "why":
                f"VM creationTimestamp {vm_created!r} did not parse; refusing rather than assuming an order"}
    # ---- the BOOTSTRAP path — ANY mode ----------------------------------------------------------------
    ph = (phase or "").strip()
    if any(ph.startswith(t) for t in BOOTSTRAP_TERMINAL):
        return {"action": "reap", "cause": "bootstrap_terminal_marker", "why":
                f"this VM's own phase marker reads {ph!r} — a PRE-MD failure, written only on paths that "
                f"exit before any leg starts. No sampling began and no checkpoint exists, so there is "
                f"nothing this delete can destroy."}
    # ---- the SMOKE path -------------------------------------------------------------------------------
    # A smoke writes no result object, so the clause below can never retire it and its ONLY bound would be
    # the 7 h non-run cap — 7 h of the account's single GPU for a job that finished in twenty minutes. It
    # does, however, write a TERMINAL marker as its last act, and that marker is evidence of the same kind
    # as the result object: the container returned, there is nothing left on the box. Scoped strictly to
    # `s1f-mode=smoke` VMs, because a RUN's markers are progress, not termination, and reaping a run on one
    # would destroy live sampling.
    if str(vm_mode) == "smoke":
        if any(ph.startswith(t) for t in SMOKE_TERMINAL):
            return {"action": "reap", "cause": "smoke_terminal_marker", "why":
                    f"this VM is labelled s1f-mode=smoke and its own phase marker reads {ph!r} — a terminal "
                    f"state it writes as its last act. A smoke holds no science and never will."}
        return {"action": "refuse", "cause": "smoke_not_terminal", "why":
                f"s1f-mode=smoke with phase {ph or '<none>'!r}, which is not one of {SMOKE_TERMINAL}. It may "
                f"still be pulling the image or building the system. AGE IS NOT A REASON; the create-time "
                f"{MAX_RUN_S_NON_RUN}s cap is this VM's bound."}
    if not result_updated:
        return {"action": "refuse", "cause": "no_result_object", "why":
                f"no result object for {unit_id} in GCS — the leg may be sampling right now. "
                f"AGE IS NOT A REASON: a healthy fan-out leg legitimately runs for many hours."}
    res = _parse_ts(result_updated)
    if res is None:
        return {"action": "refuse", "cause": "unreadable_timestamp", "why":
                f"result object timestamp {result_updated!r} did not parse; refusing"}
    if res <= vm:
        return {"action": "refuse", "cause": "result_older_than_vm", "why":
                f"the result for {unit_id} ({res.isoformat()}) predates this VM ({vm.isoformat()}), so it is "
                f"a PREVIOUS run's output and says nothing about what this VM is doing"}
    return {"action": "reap", "cause": "result_landed_after_vm", "why":
            f"{unit_id}'s result object was written at {res.isoformat()}, after this VM was created at "
            f"{vm.isoformat()} — the science is banked in GCS and there is no sampling left to lose"}


# ---- reading a VM's labels -----------------------------------------------------------------------------

#: The order `vms` emits, and the order the workflow's `read` consumes.
VM_FIELDS = ("name", "zone", "status", "creationTimestamp", "s1f-edge", "s1f-rep", "s1f-mode")


def vm_rows(gcloud_json):
    """TSV rows from `gcloud compute instances list --format=json`. PURE.

    ⚠ WHY NOT `--format="value(labels.s1f-edge)"`. gcloud's projection grammar and its filter grammar are
    different parsers, and a HYPHEN in a label key is exactly where they diverge — a projection can return
    EMPTY for a label the filter matches perfectly well. That matters here more than anywhere else in the
    lane, because this reaper's correct and deliberate response to an unlabelled VM is to **REFUSE**. An
    empty projection would therefore produce a teardown that declines to work, forever, while every log line
    says it ran: the identical shape to the watchdog that was scheduled, running and green while a finished
    leg held the only GPU (gcp-gpu-facts.md §6b). JSON has ONE grammar and the label is a dict lookup.
    """
    if isinstance(gcloud_json, str):
        gcloud_json = json.loads(gcloud_json or "[]")
    out = []
    for v in gcloud_json or []:
        labels = v.get("labels") or {}
        out.append("\t".join([
            v.get("name", ""), (v.get("zone") or "").split("/")[-1], v.get("status", ""),
            v.get("creationTimestamp", ""), labels.get("s1f-edge", ""), labels.get("s1f-rep", ""),
            labels.get("s1f-mode", ""),
        ]))
    return out


# ---- the in-flight board fragment ---------------------------------------------------------------------

#: The lane id this fragment is published under.
#:
#: ⚠ NOT YET IN `inflight_board.LANES`, and that is a REPORTED gap, not an oversight. `merge_board` iterates
#: that registry and never the fragments it happens to find — deliberately, so a lane that has never
#: published still renders a section saying so. Until a one-line entry is added there (that module is owned
#: by another agent, so this lane does not edit it) the fragment below is written and simply not rendered.
#: It is written anyway because the alternative is worse in exactly the way that registry exists to prevent:
#: a lane with no artifact at all is indistinguishable from a lane with nothing to say.
BOARD_LANE = "gcp-s1f-rep"

#: What this lane costs. Free credit NAMED AS SUCH (CLAUDE.md §1), and no `$/ns` against the Vast ladder
#: basis, because there is no realized dollar to divide: this is a different ledger, not a cheap rate on
#: the same one. The L4 list rate is shown only so the row is not blank, and carries pricing.md's standing
#: refusal to treat it as a go-forward cost basis.
BOARD_USD_PER_NS = ("— $0 real dollars (GCP trial credit, a SEPARATE LEDGER, expires 2026-10-10). "
                    "L4 list $0.708/h is NOT a go-forward cost basis (pricing.md); no $/ns is quoted "
                    "against the ladder because no ladder dollar is being spent.")


def board_rows(unit, vm_status, vm_created, result_updated, phase=None):
    """This lane's rows for the all-lane board. PURE.

    ★ AN IDLE LANE SAYS SO. The row is emitted in every state, including "nothing running" — a lane that
    renders only while busy looks finished when it is merely stopped, which is the failure the board's own
    docstring is built around."""
    name = f"{unit['edge_id'].replace('e_', '', 1)} r{unit['replicate']}"
    if result_updated:
        return [], (f"{unit['unit_id']} is DONE — ddg.json in GCS at {result_updated}. Nothing running; "
                    f"this lane holds no GPU.")
    live = str(vm_status or "").upper() in ("RUNNING", "PROVISIONING", "STAGING", "REPAIRING")
    if live:
        row = {"name": name, "pct": None, "pct_of": None, "eta_s": None,
               "usd_per_ns": BOARD_USD_PER_NS, "state": "RUNNING",
               "why": (f"GCE L4, {vm_status}, created {vm_created}. phase='{phase or '<none>'}'. "
                       f"ETA UNKNOWN — this lane has no measured L4 rate for a fan-out leg yet; the first "
                       f"one produces it. Bounded at CREATE by --max-run-duration={MAX_RUN_S_RUN}s.")}
        return [row], f"{unit['unit_id']} running on the single GCP GPU (GPUS_ALL_REGIONS=1 — strictly serial)."
    row = {"name": name, "pct": None, "pct_of": None, "eta_s": None,
           "usd_per_ns": "—", "state": "IDLE — NO HOST",
           "why": ("no GCE VM and no ddg.json: this lane is holding no GPU and computing nothing. "
                   "A re-dispatch of gpu-fanout-rep-gcp.yml mode=run resumes it from its last committed "
                   "generation in GCS (per-leg idempotent).")}
    return [row], f"{unit['unit_id']} NOT running. The free GCP GPU is idle — that is expiring credit unspent."


def write_board(unit, vm_status, vm_created, result_updated, phase=None, root=None):
    """Publish the fragment through inflight_board's own writer, so the document shape has one home."""
    import inflight_board as ib
    rows, note = board_rows(unit, vm_status, vm_created, result_updated, phase=phase)
    return ib.write_fragment(BOARD_LANE, rows, note=note, root=root)


# ---- CLI ----------------------------------------------------------------------------------------------

def _shell(d):
    for k, v in d.items():
        if isinstance(v, (dict, list)):
            continue
        print(f"{k}={'' if v is None else v}")


def _cmd_plan(a):
    bucket = a.bucket or (os.environ.get("PROJECT", "") + BUCKET_SUFFIX)
    units = units_for(a.edge, a.replicate)
    if a.pick is not None:
        if not (0 <= a.pick < len(units)):
            raise SystemExit(f"--pick {a.pick} out of range: {a.edge} r{a.replicate} has {len(units)} unit(s)")
        units = [units[a.pick]]
    out = []
    for u in units:
        uris = gcs_uris(u, bucket)
        out.append({
            "unit_id": u["unit_id"],
            "edge_id": u["edge_id"],
            "leg_id": u["leg_id"],
            "receptor": u["receptor"],
            "frame": u["frame"],
            "cycle_id": u.get("cycle_id"),
            "replicate": u["replicate"],
            "ligand_a": u["ligand_a"],
            "ligand_b": u["ligand_b"],
            "labels": {"lane": LABEL_LANE, "s1f-edge": u["edge_id"], "s1f-rep": str(u["replicate"])},
            "max_run_s": max_run_seconds(a.mode_for_cap),
            "uris": uris,
            "env": {lg: leg_env(u, lg, bucket) for lg in ("complex", "solvent")},
            "provenance": provenance(u, bucket),
        })
    if a.shell:
        if len(out) != 1:
            raise SystemExit(f"--shell needs exactly one unit; got {len(out)} (use --pick N)")
        o = out[0]
        _shell({
            "UNIT_ID": o["unit_id"], "EDGE_ID": o["edge_id"], "LEG_ID": o["leg_id"],
            "RECEPTOR": o["receptor"], "REPLICATE": o["replicate"], "FRAME": o["frame"],
            "LIGAND_A": o["ligand_a"], "LIGAND_B": o["ligand_b"],
            "N_WINDOWS": o["env"]["complex"]["N_WINDOWS"], "SEED": o["env"]["complex"].get("SEED", ""),
            "MAXRUN": f"{o['max_run_s']}s",
            "STAGE_URI": o["uris"]["stage_uri"], "UNIT_URI": o["uris"]["unit_uri"],
            "RESULT_KEY": o["uris"]["result_key"], "CKPT_URI": o["uris"]["ckpt_uri"],
            "LABELS": f"lane={LABEL_LANE},s1f-edge={o['edge_id']},s1f-rep={o['replicate']}",
        })
        for lg in ("complex", "solvent"):
            for k, v in o["env"][lg].items():
                print(f"ENV_{lg.upper()}_{k}={v}")
    else:
        print(json.dumps(out if a.pick is None else out[0], indent=1))
    return 0


def _cmd_reap(a):
    unit_id = a.unit_id
    if not unit_id and a.edge_id:
        try:
            unit_id = unit_for(a.edge_id, a.replicate)["unit_id"]
        except Exception as e:                                   # noqa: BLE001 — a refusal, not a crash
            d = {"action": "refuse", "cause": "unknown_unit", "why": str(e)}
            print(json.dumps(d, indent=1) if a.json else f"action={d['action']}\ncause={d['cause']}")
            return 0
    d = reap_decision(unit_id, a.vm_created, a.result_updated, vm_mode=a.vm_mode, phase=a.phase)
    d["unit_id"] = unit_id
    if a.json:
        print(json.dumps(d, indent=1))
    else:
        _shell({"ACTION": d["action"], "CAUSE": d["cause"], "UNIT_ID": unit_id or ""})
        print(f"WHY={d['why']}")
    return 0


def _cmd_board(a):
    unit = unit_for(a.edge, a.replicate)
    path = write_board(unit, a.vm_status, a.vm_created, a.result_updated, phase=a.phase)
    print(f"wrote {path}")
    with open(path) as fh:
        print(fh.read())
    return 0


def _cmd_vms(a):
    for ln in vm_rows(sys.stdin.read()):
        print(ln)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("plan", help="resolve the unit(s) and print the wiring CI needs")
    pl.add_argument("--edge", required=True, help="edge id OR cycle id (e.g. cycle_3carbonyl)")
    pl.add_argument("--replicate", type=int, default=1)
    pl.add_argument("--pick", type=int, default=None, help="index into the resolved units (0-based)")
    pl.add_argument("--bucket", default=None)
    pl.add_argument("--mode-for-cap", dest="mode_for_cap", default="run", choices=["run", "smoke", "mirror"])
    pl.add_argument("--shell", action="store_true")
    pl.set_defaults(func=_cmd_plan)

    rp = sub.add_parser("reap", help="evidence-based teardown decision (age is never consulted)")
    rp.add_argument("--unit-id", default=None)
    rp.add_argument("--edge-id", default=None, help="from the VM's s1f-edge label")
    rp.add_argument("--replicate", type=int, default=1, help="from the VM's s1f-rep label")
    rp.add_argument("--vm-created", default="")
    rp.add_argument("--result-updated", default="")
    rp.add_argument("--vm-mode", default="run", help="from the VM's s1f-mode label")
    rp.add_argument("--phase", default="", help="the VM's own phase marker (smoke terminus only)")
    rp.add_argument("--json", action="store_true")
    rp.set_defaults(func=_cmd_reap)

    bd = sub.add_parser("board", help="publish this lane's in-flight fragment (an IDLE lane says so)")
    bd.add_argument("--edge", required=True)
    bd.add_argument("--replicate", type=int, default=1)
    bd.add_argument("--bucket", default=None)
    bd.add_argument("--vm-status", default="")
    bd.add_argument("--vm-created", default="")
    bd.add_argument("--result-updated", default="")
    bd.add_argument("--phase", default="")
    bd.set_defaults(func=_cmd_board)

    vm = sub.add_parser("vms", help="TSV of gcp-s1frep VMs, read from `instances list --format=json` on stdin")
    vm.set_defaults(func=_cmd_vms)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
