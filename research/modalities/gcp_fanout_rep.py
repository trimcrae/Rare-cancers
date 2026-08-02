#!/usr/bin/env python3
"""
GCP L4 — ONE step-1 fan-out REPLICATE unit, on the free (expiring) GCP trial credit.

WHY THIS LANE EXISTS
--------------------
`GPUS_ALL_REGIONS = 1` (gcp-gpu-facts.md #1) makes GCP a **single serial worker**, and trimcrae's standing
instruction for it is *"Treat it as a single GPU in your fleet"* — one unit at a time, never a programme.
This module is that one unit's wiring, and nothing else.

THE UNIT, and why it is this one:
  * nr4a3-program-map.md's `[ ]` item *"Step 1 fan-out · REPLICATES ON THE OPEN CYCLE"* is **unowned** in
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
import re
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
# ★ THE PROGRESS ARITHMETIC IS IMPORTED, NEVER RE-DERIVED (rule 1). `sequential_pct` /
# `sequential_remaining` are the board's one implementation of "how far through a multi-stage unit is
# this", and `parse_targets` is the one parser of the driver's own target line. A second spelling here
# could disagree with the ternary lane's about what 50 % means, which is the whole failure rule 1 names.
from inflight_board import parse_targets, sequential_pct, sequential_remaining  # noqa: E402

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

#: ★ A LEG THAT FAILED IS ALSO TERMINAL, AND SAFELY SO — measured 7:51 PM ET 2026-07-31, when a leg raised
#: `openmm.OpenMMException: No compatible CUDA device is available` and its VM then sat on the account's ONE
#: GPU with its container already exited. The refusal was conservative and WRONG here for a specific,
#: checkable reason: this lane's checkpoints are CONTINUOUS. `GCSCommitStore` writes every generation to GCS
#: as it is produced (manifest last), so by the time a leg's failure marker exists, everything it banked is
#: already durable and off the box. Deleting the VM therefore loses nothing a relaunch cannot resume, which
#: is the whole design. ⚠ This is safe ONLY because of that continuity — a lane that synced at the end
#: instead would lose real sampling here, which is why the rule and the upload mode travel together.
LEG_TERMINAL_PREFIXES = ("leg-",)
LEG_TERMINAL_SUFFIXES = ("-NORESULT",)
LEG_TERMINAL_CONTAINS = ("-FAILED-",)


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
    # ---- a FAILED leg — ANY mode, and safe because the commit store is continuous -----------------------
    if any(ph.startswith(p) for p in LEG_TERMINAL_PREFIXES) and (
            any(c in ph for c in LEG_TERMINAL_CONTAINS)
            or any(ph.split()[0].endswith(sfx) for sfx in LEG_TERMINAL_SUFFIXES)):
        return {"action": "reap", "cause": "leg_failed_terminal", "why":
                f"this VM's own phase marker reads {ph!r} — the leg RAISED and its container has exited. "
                f"Every generation it banked is already in GCS (the commit store uploads as it writes), so "
                f"a relaunch resumes from the last committed iteration and this delete loses nothing."}
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


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE DURABLE CENSUS — what the object store, and only the object store, can prove
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
#
# ★★ WHY A % DONE NEVER NEEDED A MEASURED RATE, AND WHY THE COLUMN WAS BLANK FOR A DAY ANYWAY
# (2026-08-01, after the first real leg banked 20 committed generations and the board still printed `—`).
# The row's own `why` said *"ETA UNKNOWN — this lane has no measured L4 rate for a fan-out leg yet"*, and
# then left `pct` null too. Those are DIFFERENT questions. **How far through is it** is a ratio of two
# integers — the iteration the store says is committed, over the target the driver's own log line states —
# and needs no seconds-per-iteration at all. **When will it land** is the one that needs a rate. Conflating
# them cost the whole progress column: a reader could not tell a leg 14 % in from one that had not started,
# on a lane whose entire reason to exist is that nobody is watching it.
#
# ⚠ AND THE CENSUS IS READ FROM `COMMITTED.json` MARKERS, NOT FROM A LOG. A log line says a process
# *believes* it reached an iteration; a `COMMITTED.json` says the generation is DURABLE IN GCS — the thing
# only a real run can produce, and the only thing a resume can actually start from (CLAUDE.md §4b). The two
# diverge exactly when it matters: at a crash, the log's last `Iteration` line is ahead of the last commit,
# and reporting it would promise a resume point that does not exist.

#: The commit tree is `<ckpt>/<leg>/<phase>/iter-NNNNNNNN/<generation-hash>/COMMITTED.json`.
_CKPT_RE = re.compile(r"/ckpt/([A-Za-z0-9_]+)/([A-Za-z0-9_]+)/iter-(\d+)/[^/]+/COMMITTED\.json$")

#: `gcloud storage ls -l` emits `<size> <RFC3339> <uri>`, plus a trailing `TOTAL:` line.
_LS_RE = re.compile(r"^\s*(\d+)\s+(\S+?Z)\s+(gs://\S+)\s*$")

#: The legs whose commits are SCIENCE. `smoke` writes into the same tree under its own leg name
#: (`RBFE_SPOT_COMMIT_GCS=…/ckpt/smoke`, s1f_rep_gcp_startup.sh) precisely so it can never be resumed into
#: — and for exactly the same reason it must never be counted as progress. A reader that did not exclude it
#: would have seen `smoke/production/iter-4` and concluded the production phase had begun, which is the
#: `100.0%`-off-a-smoke-census failure inflight_board.render already carries a guard for.
SCIENCE_LEGS = ("complex", "solvent")

#: ★ THE STATED THRESHOLD FOR "ENOUGH POINTS TO QUOTE A RATE" — a number in the code, not a judgement call.
#: Below it the ETA cell says so and names the count; at or above it the ETA renders. Three COMPLETED
#: intervals is the smallest number from which you can see whether a rate is still settling (two to compare
#: and one to confirm the comparison) — and the first measured leg proves that is not paranoia: its first
#: interval ran at 18.1 s/iter and it settled near twice that, so a rate quoted off one interval would have
#: promised a landing roughly twice too early. `ETA UNKNOWN` forever is indistinguishable from a broken
#: estimator, so this is a threshold that is REACHED, not a permanent refusal.
MIN_RATE_INTERVALS = 3

#: Only the trailing N completed intervals feed the quoted rate. A whole-run mean would keep the settling
#: transient in the denominator for the entire leg; a trailing window forgets it as soon as it is over, and
#: tracks a real slowdown (a resumed leg on a busier host) instead of averaging it away.
RATE_WINDOW = 5


def parse_ls_long(text):
    """[(size_bytes, updated_iso, uri)] from `gcloud storage ls -l` output. PURE.

    Deliberately tolerant of the `TOTAL:` footer and of blank lines, and deliberately INTOLERANT of a line
    it cannot parse into all three fields — an unparsed object is dropped rather than guessed at, and the
    caller's census then reports what it could read rather than a number built from half a listing."""
    out = []
    for ln in (text or "").splitlines():
        m = _LS_RE.match(ln)
        if m:
            out.append((int(m.group(1)), m.group(2), m.group(3)))
    return out


def checkpoint_marks(rows, legs=SCIENCE_LEGS):
    """{leg: [(phase, iteration, updated_iso)]}, ascending by iteration, smoke excluded. PURE.

    `rows` is `parse_ls_long`'s output (or any iterable of (size, updated, uri))."""
    out = {}
    for _sz, upd, uri in rows or ():
        m = _CKPT_RE.search(uri)
        if not m:
            continue
        leg, phase, it = m.group(1), m.group(2), int(m.group(3))
        if legs is not None and leg not in legs:
            continue
        out.setdefault(leg, []).append((phase, it, upd))
    for leg in out:
        out[leg].sort(key=lambda t: (t[0], t[1]))
    return out


def interval_rates(marks_for_leg, with_phase=False):
    """[(from_iter, to_iter, seconds, s_per_iter)] between CONSECUTIVE commits of one phase. PURE.

    `with_phase=True` appends the phase, because WHICH PHASE a rate was measured in is part of the rate
    (see `_PHASE_CROSS_NOTE`) and a caller that loses it can publish a warmup number as a production one.

    ⚠ Never across a phase boundary: warmup→production restarts the iteration counter, so a pair spanning
    it would divide a real duration by a negative or meaningless iteration delta. Same reason
    `inflight_board.advance_counters` resets on a stage change."""
    out = []
    by_phase = {}
    for phase, it, upd in marks_for_leg or ():
        by_phase.setdefault(phase, []).append((it, upd))
    for phase, seq in by_phase.items():
        seq.sort()
        for (i0, u0), (i1, u1) in zip(seq, seq[1:]):
            t0, t1 = _parse_ts(u0), _parse_ts(u1)
            if t0 is None or t1 is None or i1 <= i0:
                continue
            secs = (t1 - t0).total_seconds()
            if secs <= 0:
                continue
            out.append((i0, i1, secs, secs / (i1 - i0), phase))
    # PRODUCTION after WARMUP whatever the raw integers say — the counter restarts at the boundary.
    out.sort(key=lambda t: ({"warmup": 0, "production": 1}.get(t[4], -1), t[0]))
    return out if with_phase else [t[:4] for t in out]


def quoted_rate(marks_for_leg, window=RATE_WINDOW, min_intervals=MIN_RATE_INTERVALS):
    """The leg's seconds-per-iteration, or a REFUSAL that names the count. PURE.

    Returns {"s_per_iter": float|None, "n_intervals": int, "n_used": int, "spread": float|None,
             "why": str}. `spread` is max/min over the window — reported, never used to suppress the
    number, because a reader who can see the spread can grade the ETA and a hidden refusal teaches nothing.
    """
    iv = interval_rates(marks_for_leg, with_phase=True)
    # ★★ NEVER MIX PHASES INSIDE ONE WINDOW. The moment production banks its first interval a trailing-5
    # window would hold 4 warmup samples and 1 production one, report the mean as `production`, understate
    # the production rate — and, worse, DROP the lower-bound caveat exactly when it starts mattering,
    # because the caveat fires on `rate phase != remaining phase`. So the window is scoped to the CURRENT
    # phase, and when that phase is too young to quote, the PREVIOUS phase's rate is quoted and LABELLED as
    # the previous phase, which is what keeps the caveat armed.
    cur = iv[-1][4] if iv else None
    same = [t for t in iv if t[4] == cur]
    if len(same) >= min_intervals:
        iv = same
    n = len(iv)
    if n < min_intervals:
        return {"s_per_iter": None, "n_intervals": n, "n_used": 0, "spread": None, "phase": cur,
                "why": (f"{n} completed commit interval(s); this lane quotes a rate at "
                        f"{min_intervals} (gcp_fanout_rep.MIN_RATE_INTERVALS). "
                        f"The next commit moves it toward the threshold.")}
    used = iv[-int(window):] if window else iv
    rates = [t[3] for t in used]
    s = sum(rates) / len(rates)
    # ⚠ WHICH PHASE THE RATE WAS MEASURED IN IS PART OF THE RATE. See `_PHASE_CROSS_NOTE`. Every interval
    # in `used` now shares a phase by construction, so this is the window's phase and not a guess about it.
    phase = used[-1][4]
    return {"s_per_iter": s, "n_intervals": n, "n_used": len(used), "phase": phase,
            "spread": (max(rates) / min(rates)) if min(rates) > 0 else None,
            "why": (f"mean of the trailing {len(used)} of {n} completed {phase or '?'} commit intervals "
                    f"(gcp_fanout_rep.RATE_WINDOW)")}


#: ★★ A WARMUP RATE IS NOT A PRODUCTION RATE, AND THIS REPO HAS ALREADY PAID FOR THAT ONE.
#: pricing.md's 2026-07-26 correction: an L4 card ratio was published off **33.91 s/iter measured during
#: WARMUP** and the same leg's consecutive PRODUCTION iterations measured **56.5 s/iter** — a 1.67x
#: understatement, which propagated into a per-leg dollar figure before it was caught. Production adds the
#: online MBAR analysis and the full trajectory write that warmup does not do, so the direction is known
#: even where the magnitude is not.
#: So an ETA whose rate came from one phase and whose remaining work is mostly the other is a LOWER BOUND
#: and must say so in the cell. It is not suppressed — a lower bound is genuinely useful and "unknown" is
#: not — but it is never presented as a symmetric estimate.
_PHASE_CROSS_NOTE = ("⚠ LOWER BOUND: the rate was measured in {measured} and the work left is mostly "
                     "{remaining}. pricing.md's 2026-07-26 correction measured an L4 warmup at 33.91 "
                     "s/iter against 56.5 s/iter in production on the same leg — 1.67x — so this ETA can "
                     "only move later, never earlier. The first {remaining} commit intervals replace it.")


def leg_stage(marks_for_leg):
    """(phase, iteration) the store proves this leg reached, or (None, None). PURE.

    Production outranks warmup whatever the iteration numbers say — the counter restarts at the phase
    boundary, so `max` over the raw integers would report a warmup leg as ahead of a production one."""
    order = {"warmup": 0, "production": 1}
    best = None
    for phase, it, _u in marks_for_leg or ():
        k = (order.get(phase, -1), it)
        if best is None or k > best[0]:
            best = (k, (phase, it))
    return best[1] if best else (None, None)


def unit_stages(targets):
    """The FOUR stages of a unit, in the order they run, as `sequential_pct` wants them. PURE.

    ⚠ THE DENOMINATOR IS THE WHOLE UNIT, NOT THE LEG. The deliverable is `ddg.json`, and it needs
    complex AND solvent; a leg-scoped percentage would read 100 % with half the unit unbought. Same
    argument `inflight_board.pct_complete` makes for warmup-vs-production one level down.
    `targets` is (warmup_target, prod_target) — identical for both legs because the driver derives them
    from the protocol's equilibration/production lengths and timestep, not from the system."""
    if not targets:
        return None
    w, p = targets
    return (("complex-warmup", w), ("complex-production", p),
            ("solvent-warmup", w), ("solvent-production", p))


def _phase_cross(rate_phase, remaining_phase):
    """The lower-bound caveat, or "" when the rate and the remaining work are the same phase. PURE."""
    if not rate_phase or not remaining_phase or rate_phase == remaining_phase:
        return ""
    return " " + _PHASE_CROSS_NOTE.format(measured=rate_phase, remaining=remaining_phase)


def unit_progress(marks, targets, legs_done=(), leg_rates=None, rate_phases=None):
    """% done and ETA for one unit, from the DURABLE census alone. PURE.

    Returns a dict; every refusal names itself rather than rendering as an absent number:
      pct          0-100, or None ONLY when the targets could not be read (see `pct_why`)
      pct_of       a LABEL for the cell when a bare percentage would mislead, else None
      eta_s        seconds to the end of `eta_scope`, or None with `eta_why` saying which input was missing
      eta_scope    "unit" | "<leg> leg" — WHICH terminus the ETA is for, never left to inference

    ⚠ THE SOLVENT LEG'S RATE IS NOT THE COMPLEX LEG'S. The two legs solvate different systems and differ in
    seconds per iteration by a large factor, so projecting the whole unit off the complex rate would be a
    fabricated number in the cell whose job is to be actionable. Until the solvent leg has its own measured
    rate the ETA is scoped to the leg that HAS one, and says so.
    """
    stages = unit_stages(targets)
    legs_done = tuple(legs_done or ())
    leg_rates = dict(leg_rates or {})
    rate_phases = dict(rate_phases or {})
    if not stages:
        return {"pct": None, "pct_of": None, "eta_s": None, "eta_scope": None, "stage": None,
                "iteration": None,
                "pct_why": ("the driver's `warmup_target=… prod_target=…` line has not been read, so the "
                            "denominator is unknown. An unreadable target is not a target of zero "
                            "(CLAUDE.md §4) — the cell refuses rather than guessing a total."),
                "eta_why": "no targets, so no remaining-work count either"}
    w, p = targets
    # A leg whose result JSON is already in GCS is COMPLETE whatever its last committed generation says:
    # the commit tree is not pruned, so a finished leg's newest marker is its last checkpoint, not its end.
    cur_leg, phase, it = None, None, None
    for leg in SCIENCE_LEGS:
        if leg in legs_done:
            continue
        ph, i = leg_stage(marks.get(leg) if marks else None)
        cur_leg, phase, it = leg, ph, i
        break
    if cur_leg is None:                                    # both legs banked; only the reduce remains
        return {"pct": 100.0, "pct_of": None, "eta_s": None, "eta_scope": None,
                "stage": "reduce", "iteration": None,
                "pct_why": "both leg JSONs are in GCS; all sampling is done",
                "eta_why": "sampling complete — the reduce is a CPU step of seconds"}
    stage_key = f"{cur_leg}-{phase}" if phase else None
    # Iterations banked BEFORE the current leg, so the percentage is of the unit and not of the leg.
    prior = sum(w + p for leg in SCIENCE_LEGS if leg in legs_done)
    total = 2 * (w + p)
    done_here = sequential_pct(stages, stage_key, it or 0)
    done_iters = (done_here / 100.0 * total) if done_here is not None else 0.0
    # `prior` is already inside `stages` for a done leg only if that leg precedes the current one; the
    # sequential model handles the ordering, so take the larger of the two readings rather than adding.
    banked = max(done_iters, float(prior))
    pct = min(100.0, 100.0 * banked / total) if total else None
    rem_unit = sequential_remaining(stages, stage_key, it or 0)
    # ---- the ETA ---------------------------------------------------------------------------------------
    rate = leg_rates.get(cur_leg)
    if not rate:
        return {"pct": pct, "pct_of": None, "eta_s": None, "eta_scope": None,
                "stage": stage_key, "iteration": it,
                "pct_why": f"{int(banked)} of {total} committed iterations (unit = 2 legs x (warmup {w} + "
                           f"production {p}))",
                "eta_why": f"no measured rate for the {cur_leg} leg yet"}
    rem_leg = sequential_remaining((("warmup", w), ("production", p)), phase, it or 0)
    # Which phase the REMAINING work of this leg is mostly in. A leg that has finished warmup has all of
    # its production ahead of it, so a warmup-measured rate is being projected across the boundary.
    rem_phase = "production" if (phase == "production" or (phase == "warmup" and (it or 0) >= w)) else phase
    cross = _phase_cross(rate_phases.get(cur_leg), rem_phase)
    others = [lg for lg in SCIENCE_LEGS if lg not in legs_done and lg != cur_leg]
    if others and not all(leg_rates.get(lg) for lg in others):
        return {"pct": pct, "pct_of": None, "eta_s": rem_leg * rate, "eta_scope": f"{cur_leg} leg",
                "stage": stage_key, "iteration": it,
                "pct_why": f"{int(banked)} of {total} committed iterations (unit = 2 legs x (warmup {w} + "
                           f"production {p}))",
                "eta_why": (f"scoped to the {cur_leg} leg: {', '.join(others)} has no measured L4 rate of "
                            f"its own and the two legs solvate different systems, so projecting the unit "
                            f"off this rate would be a fabricated number.{cross}")}
    eta = rem_leg * rate + sum((w + p) * leg_rates[lg] for lg in others)
    return {"pct": pct, "pct_of": None, "eta_s": eta, "eta_scope": "unit",
            "stage": stage_key, "iteration": it,
            "pct_why": f"{int(banked)} of {total} committed iterations (unit = 2 legs x (warmup {w} + "
                       f"production {p}))",
            "eta_why": (f"every remaining leg has its own measured rate; {int(rem_unit)} iterations "
                        f"left.{cross}")}


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE THIRD SIDE — noticing that a LIVE leg has stopped committing
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
#
# ★★ THE LANE COULD START WORK AND END WORK AND NOT NOTICE IT STOPPING (2026-08-01, found by trying to
# answer "is this leg progressing?" by hand and having no reading that could answer it). Between `PHASE
# leg-complex-running` and the first `COMMITTED.json` the lane emits nothing, and on the complex leg those
# are ~23-39 min apart — longer across a system rebuild or a resume's checkpoint fetch. Over that window
# "healthy, rebuilding a 12-replica 112,953-atom system from a 541 MiB checkpoint" and "wedged" produce
# the SAME observation from outside the box. CLAUDE.md §4 requires a PROGRESS check, and a lane whose only
# progress signal arrives on that cadence cannot have one unless something watches the gap.
#
# ⚠ RETRACTED, IN THE SAME COMMIT THAT MADE IT: this docstring first said "a resumed leg ran 63 min past
# PHASE leg-complex-running with no new committed generation". It had run ~19 min; 63 was an ET
# mis-conversion of my own and was never measured. The GAP is real and independently motivates this code —
# but the number is withdrawn and must not be quoted. Superseded, retained (CLAUDE.md §1.2). It is also
# the reason the threshold below is derived from the leg's OWN interval rather than from that anecdote.
#
# ⚠ IT FLAGS; IT NEVER CONDEMNS. No reap path consults this and no launch decision reads it. That is
# deliberate and it is the same boundary `vast_idle_guard` draws: the cost of a false stall flag is a line
# in a readout, the cost of a false stall REAP is destroyed sampling. `reap_decision` still keys only on
# the unit's own terminal evidence.
#
# ⚠ THE THRESHOLD IS DERIVED FROM THE LEG'S OWN MEASURED COMMIT INTERVAL, never typed. A leg that commits
# every 700 s and one that commits every 30 s cannot share a constant, and a typed seconds figure would be
# wrong for the solvent leg the day it is first measured.
#
# ⚠ AND THE CLOCK STARTS AT `max(last commit, leg start)`. Measuring a resumed leg's silence from its
# YESTERDAY commit would flag it the instant it launched — the last committed generation is 21 h old by
# construction and that says nothing about the process running now.

#: How many of the leg's own commit intervals of silence before the row says so. The FIRST commit after a
#: leg starts legitimately takes longer than a steady-state one: it spans the OpenFE system build, and on a
#: resume also the download and validation of the committed generation. Measured on the cold run — VM
#: created 8:00:17 PM ET, first commit 8:23:12 PM, of which ~700 s was the 20 iterations themselves — the
#: build is worth roughly one extra interval, and a resume adds the checkpoint fetch on top. 4 and 3 leave
#: room for both without leaving a genuinely wedged leg unremarked for hours.
STALL_INTERVALS_FIRST = 4
STALL_INTERVALS_STEADY = 3

#: The phase marker a running leg writes, and the timestamp it carries: `leg-complex-running <RFC3339>`.
_PHASE_TS_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s*$")


def phase_started(phase):
    """The RFC3339 stamp a phase marker carries, or None. PURE."""
    m = _PHASE_TS_RE.search(str(phase or "").strip())
    return m.group(1) if m else None


def commit_interval_seconds(marks_for_leg, window=RATE_WINDOW):
    """The leg's own recent seconds-per-commit, or None. PURE. DERIVED from the markers, never typed."""
    iv = interval_rates(marks_for_leg)
    if not iv:
        return None
    used = iv[-int(window):] if window else iv
    return sum(t[2] for t in used) / len(used)


def stall_verdict(marks_for_leg, leg_started, now_utc, live):
    """Has a LIVE leg gone quiet for longer than its own commit interval explains? PURE.

    Returns {"stalled": bool, "silent_s": float|None, "budget_s": float|None, "why": str}.
    `stalled` False with a `why` is the normal case and the `why` still says what was measured — a guard
    that only speaks when it fires is a guard nobody can tell is working.
    """
    if not live:
        return {"stalled": False, "silent_s": None, "budget_s": None,
                "why": "no host, so there is nothing that could be committing"}
    iv = commit_interval_seconds(marks_for_leg)
    started, now = _parse_ts(leg_started), _parse_ts(now_utc)
    last = _parse_ts((marks_for_leg or [(None, None, None)])[-1][2]) if marks_for_leg else None
    if iv is None or now is None or (started is None and last is None):
        return {"stalled": False, "silent_s": None, "budget_s": None,
                "why": ("no measured commit interval for this leg yet, so there is no derived budget to "
                        "compare a silence against. NOT a reading of health — a reading that was not "
                        "taken (CLAUDE.md §4).")}
    # ⚠ max(), for the reason in the section header: a resume's newest marker is the PREVIOUS attempt's.
    since = max([t for t in (started, last) if t is not None])
    silent = (now - since).total_seconds()
    first = last is None or (started is not None and started >= last)
    k = STALL_INTERVALS_FIRST if first else STALL_INTERVALS_STEADY
    budget = k * iv
    return {"stalled": silent > budget, "silent_s": silent, "budget_s": budget,
            "why": (f"{silent / 60.0:.0f} min since {'the leg started' if first else 'the last commit'} "
                    f"against a budget of {k} x its own measured {iv / 60.0:.1f} min commit interval"
                    f"{' — FLAGGED, and a flag is not a condemnation: nothing reaps or refuses on this' if silent > budget else ''}")}


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE MEASURED L4 RATE — the first one this program has for a step-1 fan-out leg
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
#
# ★★ WHY THIS IS A RESULT AND NOT BOOKKEEPING. Until 2026-08-01 no fan-out leg had ever been TIMED on an
# L4, so `congeneric_fanout.cost_estimate`'s hours came from Vast 4090/5090-class hosts and a GCP leg could
# not be priced at all — the lane's own cap comment says as much and calls its 48 h an ESTIMATE. This
# measurement replaces that estimate with a number, and it is what makes fan-out legs on an L4 priceable.
#
# ⚠ IT IS A REALIZED WALL-CLOCK RATE, NOT A PURE MD THROUGHPUT. Each interval spans 20 HREX iterations AND
# the GCS commit barrier that closes them, because that is what the `COMMITTED.json` timestamps bracket.
# That is the RIGHT quantity for an ETA and for GPU-hours-per-leg — those are what the lane spends — and
# the WRONG one to compare against a bare MD benchmark. Both readings are published below; the units say
# which is which.
#
# ⚠ AND IT IS ON FREE CREDIT. CLAUDE.md §6: GCP trial credit is a SEPARATE LEDGER, never summed into
# realized or ladder spend, and pricing.md's standing refusal applies — the L4 list rate is NOT a
# go-forward cost basis, so this artifact deliberately carries hours and iterations and NO dollars.

#: Where the measurement lives. Written by CI from the commit markers; never hand-edited (rule 1).
RATE_ARTIFACT = "gcp-s1f-rep-rate.json"

#: ★★ THE DOCUMENTED TABLE IS REGENERATED BY WHOEVER WRITES THE ARTIFACT, IN THE SAME CALL — it is NOT a
#: separate step somebody has to remember (measured 2026-08-01, and it is the failure CLAUDE.md §1 predicts
#: for any figure with two homes). `write_rate_artifact` used to write the JSON alone and leave §1e of
#: gcp-gpu-facts.md to a human running `rate --markdown-table`. That works exactly until the next marker
#: lands: at 9:30:55 AM ET the leg committed `production 80`, the rate window moved fully out of warmup, and
#: the measurement legitimately went 35.19 s/iter *(warmup)* → 35.26 *(production)*, 73.66 → 73.52 ns/day
#: aggregate. Nothing was wrong with either file; they were simply written by different events. CI went red
#: 3 min 41 s after the doc was last regenerated by hand, and a hand regeneration would have bought only
#: until the next commit marker. So the fence below is now filled in by `sync_rate_table_doc`, called from
#: `write_rate_artifact`, and re-applied by the lane's publish step after its `reset --hard` — the artifact
#: and the paragraph quoting it cannot be written by different events any more.
FACTS_DOC = os.path.join("..", "compute", "gcp-gpu-facts.md")

#: ONE HOME for the fence that delimits the generated block. The doc, the writer and the test all read
#: these; a marker string typed independently in three places is the same second-home bug one level down.
RATE_TABLE_BEGIN = "<!-- GCP-S1F-REP-RATE-TABLE:BEGIN -->"
RATE_TABLE_END = "<!-- GCP-S1F-REP-RATE-TABLE:END -->"

#: The protocol's MD lengths have ONE home and it is `nr4a3_rbfe.py`, which sets them on the OpenFE
#: settings object. This reads them from there rather than restating them, so a protocol change cannot
#: leave a stale ns/day behind in this file. Fails closed: an unparseable source yields None and every
#: derived nanosecond figure is then absent WITH A REASON rather than guessed.
_LEN_RE = re.compile(r"\.(equilibration|production)_length\s*=\s*([\d.]+)\s*\*\s*_ou\.nanosecond")


def protocol_lengths_ns(source_path=None):
    """{"equilibration": ns, "production": ns} as `nr4a3_rbfe.py` sets them, or None. PURE-ish (reads a file).

    ⚠ The `nanosecond` in the pattern is load-bearing: the RBFE_TINY shakeout branch sets the same two
    attributes in PICOseconds, and picking that one up would divide the real iteration count into a
    plumbing test's MD length and report a rate ~200x wrong."""
    p = source_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "nr4a3_rbfe.py")
    try:
        with open(p) as fh:
            got = dict((k, float(v)) for k, v in _LEN_RE.findall(fh.read()))
    except Exception:                                          # noqa: BLE001
        return None
    return got if {"equilibration", "production"} <= set(got) else None


def ps_per_iteration(targets, lengths_ns=None):
    """MD picoseconds one HREX iteration advances EACH replica, or None. PURE.

    Derived from the run's OWN target line and the protocol's OWN lengths — `equilibration_ns / warmup
    iterations`. The production pair is computed too and must AGREE: they are the same
    `time_per_iteration` in OpenFE and a disagreement means one of the two readings is not what it claims,
    which is a refusal rather than a number to average."""
    if not targets or not lengths_ns:
        return None
    w, p = targets
    if not w or not p:
        return None
    a = lengths_ns["equilibration"] * 1000.0 / w
    b = lengths_ns["production"] * 1000.0 / p
    return a if abs(a - b) <= 1e-6 * max(a, b) else None


def rate_report(marks, targets, n_windows=N_WINDOWS, lengths_ns=None, window=RATE_WINDOW):
    """Everything derivable about this lane's throughput, from the markers alone. PURE.

    Every field is a quotient of things measured or read; nothing here is typed."""
    lengths_ns = lengths_ns or protocol_lengths_ns()
    ps = ps_per_iteration(targets, lengths_ns)
    out = {"targets": list(targets) if targets else None,
           "n_windows": int(n_windows),
           "protocol_ns": lengths_ns,
           "ps_per_iteration_per_replica": ps,
           "legs": {}}
    for leg in SCIENCE_LEGS:
        m = marks.get(leg) or []
        q = quoted_rate(m, window=window)
        s = q["s_per_iter"]
        row = {"commits": len(m), "stage": leg_stage(m)[0], "iteration": leg_stage(m)[1],
               "s_per_iteration": s, "rate_phase": q.get("phase"),
               "n_intervals": q["n_intervals"], "n_used": q["n_used"],
               "spread": q["spread"], "why": q["why"],
               "intervals": [{"from": a0, "to": b0, "seconds": sec, "s_per_iter": r}
                             for a0, b0, sec, r in interval_rates(m)]}
        if s and targets:
            row["leg_hours"] = (targets[0] + targets[1]) * s / 3600.0
        if s and ps:
            # ⚠ TWO DIFFERENT ns/day, and conflating them is the whole reason both are printed.
            # PER-REPLICA is what one alchemical window advances; AGGREGATE is the sampling the leg buys
            # per wall-clock day across all `n_windows` of them. A single-simulation MD benchmark (the
            # card probe) is neither of these — see gcp-gpu-facts.md §1e for what may be compared.
            row["ns_per_day_per_replica"] = ps / 1000.0 * 86400.0 / s
            row["ns_per_day_aggregate"] = row["ns_per_day_per_replica"] * int(n_windows)
        out["legs"][leg] = row
    if targets and all(out["legs"][lg].get("s_per_iteration") for lg in SCIENCE_LEGS):
        out["unit_hours"] = sum(out["legs"][lg]["leg_hours"] for lg in SCIENCE_LEGS)
    return out


def rate_markdown_table(report):
    """The table that goes in gcp-gpu-facts.md §1e. DERIVED — regenerate, never hand-edit."""
    ps = report.get("ps_per_iteration_per_replica")
    head = ("| leg | commits | last committed | s / HREX iteration *(phase measured in)* | "
            "leg wall-clock h | ns/day per replica | ns/day aggregate (%s windows) |"
            % report.get("n_windows"))
    out = [head, "|---|---|---|---|---|---|---|"]
    for leg, r in (report.get("legs") or {}).items():
        s = r.get("s_per_iteration")
        out.append("| **%s** | %d | %s | %s | %s | %s | %s |" % (
            leg, r.get("commits") or 0,
            (f"{r.get('stage')} {r.get('iteration')}" if r.get("stage") else "—"),
(f"**{s:.2f}** *({r.get('rate_phase') or '?'})*" if s else "— *(%s)*" % r.get("why", "")),
            (f"{r['leg_hours']:.1f}" if r.get("leg_hours") else "—"),
            (f"{r['ns_per_day_per_replica']:.2f}" if r.get("ns_per_day_per_replica") else "—"),
            (f"{r['ns_per_day_aggregate']:.2f}" if r.get("ns_per_day_aggregate") else "—")))
    out.append("")
    out.append("*%s ps of MD per replica per iteration, derived from the run's own "
               "`warmup_target=%s prod_target=%s` line and `nr4a3_rbfe.py`'s protocol lengths "
               "(%s ns equilibration / %s ns production).*"
               % (("%.2f" % ps) if ps else "—",
                  (report.get("targets") or ["?", "?"])[0], (report.get("targets") or ["?", "?"])[1],
                  (report.get("protocol_ns") or {}).get("equilibration", "?"),
                  (report.get("protocol_ns") or {}).get("production", "?")))
    return "\n".join(out)


def facts_doc_path(root=None):
    """Where §1e lives, relative to this module (or to a test's `root`)."""
    return os.path.normpath(os.path.join(root or os.path.dirname(os.path.abspath(__file__)), FACTS_DOC))


def sync_rate_table_doc(report, path=None, root=None):
    """Rewrite gcp-gpu-facts.md §1e's fenced block from `report`. Returns True if the file changed, False if
    it was already current, None if there is no doc or no usable fence.

    ★ SURGICAL BY CONSTRUCTION: it replaces the bytes BETWEEN the fences and nothing else. That is not a
    nicety — the lane's publish step runs this *after* `git reset --hard FETCH_HEAD`, so it is editing
    whatever upstream currently holds. gcp-gpu-facts.md has many writers (§1f and §3b were both edited by
    hand the same morning), so stamping a whole file the way the lane legitimately does for its own two
    single-writer artifacts would silently discard someone else's paragraph.

    ⚠ FAILS CLOSED, NEVER PARTIALLY. A missing file, a missing fence, a duplicated fence or an END before a
    BEGIN all return None and write nothing. A doc this function could not confidently edit is one the test
    must be allowed to fail on — mangling it into agreement would destroy the evidence of the disagreement.
    """
    p = path or facts_doc_path(root)
    try:
        with open(p) as fh:
            md = fh.read()
    except Exception:                                          # noqa: BLE001
        return None
    if md.count(RATE_TABLE_BEGIN) != 1 or md.count(RATE_TABLE_END) != 1:
        return None
    a = md.index(RATE_TABLE_BEGIN) + len(RATE_TABLE_BEGIN)
    b = md.index(RATE_TABLE_END)
    if b < a:
        return None
    block = "\n" + rate_markdown_table(report).strip() + "\n"
    if md[a:b] == block:
        return False
    with open(p, "w") as fh:
        fh.write(md[:a] + block + md[b:])
    return True


def write_rate_artifact(marks, targets, unit_id, machine_type=None, root=None, n_windows=N_WINDOWS):
    """Persist the RAW marker series plus the derived report. Returns the path, or None if nothing to say.

    ★ THE RAW MARKERS ARE THE ARTIFACT'S REASON TO EXIST. Storing only the derived rate would make the
    figure unauditable and unrecomputable when `RATE_WINDOW` or the arithmetic changes; storing the
    `(leg, phase, iteration, utc)` tuples means every number above can be re-derived from evidence, which
    is what `--markdown-table` does and what the test re-checks."""
    if not any((marks or {}).get(lg) for lg in SCIENCE_LEGS):
        return None
    rep = rate_report(marks, targets, n_windows=n_windows)
    doc = {
        "_what": ("The FIRST measured throughput of a step-1 fan-out RBFE leg on a GCE L4. Written by CI "
                  "from the unit's own COMMITTED.json markers; NEVER hand-edited. gcp-gpu-facts.md §1e's "
                  "table is regenerated from this file BY THIS WRITE (`sync_rate_table_doc`), so the two "
                  "cannot be authored by different events; `rate --sync-doc` re-applies it."),
        "_ledger": ("GCP trial credit — a SEPARATE LEDGER, never summed into realized or ladder spend "
                    "(CLAUDE.md §6), expires 2026-10-10. No dollars are recorded here on purpose: the L4 "
                    "list rate is NOT a go-forward cost basis (pricing.md)."),
        "_caveat": ("A REALIZED WALL-CLOCK rate: each interval brackets 20 HREX iterations AND the GCS "
                    "commit barrier that closes them. Right for an ETA and for GPU-hours-per-leg; wrong "
                    "to compare against a bare single-simulation MD benchmark."),
        "unit_id": unit_id,
        "card": "nvidia-l4",
        "machine_type": machine_type,
        "measured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "marks": [[lg, ph, it, utc] for lg in SCIENCE_LEGS for ph, it, utc in (marks.get(lg) or [])],
        "derived": rep,
    }
    path = os.path.join(root or os.path.dirname(os.path.abspath(__file__)), RATE_ARTIFACT)
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")
    # THE SAME CALL, DELIBERATELY. A separate "and then regenerate the doc" step is the defect, not the fix:
    # it is correct only until the next marker lands. Best-effort — a doc this cannot edit must fail the
    # test, never block the measurement from being persisted.
    #
    # ★★ SYNCED FROM THE ARTIFACT'S OWN ROUND-TRIP, NOT FROM `rep` — and that distinction is the whole bug
    # (root-caused 2026-08-02, SECOND occurrence; the first, 35.66 vs 35.67, was never diagnosed).
    # `test_the_documented_table_is_the_measured_table` asserts
    #     doc_table == rate_markdown_table(rate_report(marks_from_artifact(artifact)))
    # i.e. the doc must be a function of the ARTIFACT. Syncing from `rep` made it a function of the LIVE
    # marks instead, and the two are not bit-identical: `rate_report(marks)` gave `s_per_iteration =
    # 36.085` while `rate_report(marks_from_artifact(doc))` gave `36.084999999999994` — one ULP apart, and
    # straddling a `.xx5` boundary, so `%.2f` rendered 36.09 against 36.08 and CI went red on a figure
    # nobody had touched. Both prior occurrences were `.xx5` values (35.665, 36.085), which is exactly the
    # measure-zero set where one ULP changes the printed digit — so this was never going to be rare enough
    # to ignore, and re-running `--sync-doc` only ever fixed it until the next marker landed.
    # ⛔ THE REAL DEFECT WAS TWO HOMES FOR ONE FIGURE (CLAUDE.md §1). Reading it back makes the doc a
    # function of the committed bytes by construction, so the invariant the test checks is the invariant
    # the writer maintains — and any future round-trip loss fails loudly here rather than as a mystery.
    written = load_rate_artifact(root=root)
    sync_rate_table_doc(
        rate_report(marks_from_artifact(written),
                    tuple(written["derived"]["targets"] or ()) or None,
                    n_windows=written["derived"]["n_windows"])
        if written else rep,
        root=root)
    return path


def load_rate_artifact(root=None):
    """The committed measurement, or None."""
    path = os.path.join(root or os.path.dirname(os.path.abspath(__file__)), RATE_ARTIFACT)
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:                                          # noqa: BLE001
        return None


def marks_from_artifact(doc):
    """{leg: [(phase, iteration, utc)]} back out of the artifact's raw series. PURE."""
    out = {}
    for lg, ph, it, utc in (doc or {}).get("marks") or ():
        out.setdefault(lg, []).append((ph, int(it), utc))
    for lg in out:
        out[lg].sort(key=lambda t: (t[0], t[1]))
    return out


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# SELF-FEEDING — the launch side of the supervision tick
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
#
# ★★ A TICK THAT CAN END WORK BUT NEVER START IT GUARANTEES THE GPU IDLES THE MOMENT A UNIT FINISHES
# (measured 2026-08-01; the second idle in two days, and the first one that was structural rather than a
# misconfigured watcher). Both this workflow's `schedule:` cron and the supervisor's ~8-minute loop
# dispatch it with NO inputs, and the reap sweep runs unconditionally at the head of every dispatch — so
# every tick reaped correctly and not one of them could ever provision, because the create step was gated
# on `github.event.inputs.mode`, which a `schedule:` event leaves empty. Launching therefore required a
# human or an agent to type `mode=run`, and when the agent stopped, launching stopped: 8 h 11 m of a free
# GPU sitting idle against credit that expires 2026-10-10, with every tick's board row honestly reporting
# it and nothing acting on the report.
#
# This function is the other half. It is PURE and it is the only place the decision is made, so what the
# lane will buy is testable without a cloud.
#
# ⚠ THREE REFUSALS, AND THEY ARE THE POINT — a feeder that only ever says "launch" is worse than none:
#   1. GPUS_ALL_REGIONS = 1 (gcp-gpu-facts.md #1). ANY live instance in the project — this lane's or the
#      ternary lane's — means there is no GPU to buy, and the quota error a create would return is a worse
#      way to learn that than not making the call. This is not a failure state and must never render as
#      one: it is the serial constraint working.
#   2. A unit whose ddg.json is already in GCS is DONE. The queue is walked in map order and the first
#      not-done unit is the candidate, so the lane feeds itself through the whole cycle without anyone
#      choosing an order.
#   3. THE NO-PROGRESS BREAKER. A leg that dies without banking a single new generation, three launches
#      running, is not a transient — and an unattended feeder that keeps buying is how a lane converts a
#      systematic fault into a silent burn of the whole credit balance. The counter is keyed on the
#      COMMITTED ITERATION, not on time or on attempt count alone, so a launch that advanced the work by
#      even one generation resets it: retrying is cheap when it makes progress and unbounded when it does
#      not.
#      ⚠ AND AN UNREADABLE CENSUS IS NOT A NON-ADVANCE (CLAUDE.md §4). `iteration is None` means the store
#      did not answer; counting that as "did not move" would let one throttled `ls` trip the breaker on a
#      perfectly healthy lane. It holds for that tick and says which reading was missing.

#: Consecutive launches that bank NO new committed generation before the feeder stops buying.
#: Not 1: the fault this breaker was written for (`openmm.OpenMMException: No compatible CUDA device is
#: available`, raised 3 h 45 min into a leg that had banked 20 generations) is exactly the shape that a
#: single retry ought to clear. Not 10: every attempt holds the account's only GPU for as long as it takes
#: to fail. Three is the smallest count that can distinguish "unlucky" from "systematic".
MAX_NOPROGRESS_LAUNCHES = 3

#: The lane's queue. ONE cycle, ONE replicate index, in the frozen map's own edge order — `cycle_3carbonyl`
#: is the cycle that does not close, which is the entire reason this axis was authorised
#: (`congeneric_fanout.replicate_units`' docstring is the one home of that argument).
QUEUE_CYCLE = "cycle_3carbonyl"
QUEUE_REPLICATE = 1


def queue_units(cycle=QUEUE_CYCLE, replicate=QUEUE_REPLICATE):
    """The units this lane will work through, in order. PURE. Delegates entirely to `replicate_units`."""
    return units_for(cycle, replicate)


#: ★★ THE OPERATOR HOLD — the ONE lever that pauses this lane whoever dispatches it.
#: Disabling the workflow's `schedule:` does NOT pause the lane: `step1-fanout-supervisor.yml` dispatches
#: `mode=autofeed` explicitly on its own tick, so a cron edit would leave the lane feeding and look like a
#: pause. The hold therefore lives in the DECISION, not in the trigger.
#: Reversible by deleting one file, and it is deliberately a committed artifact rather than a code edit or a
#: workflow-disable so that (a) the reason travels with it, (b) `git log` says who paused it and when, and
#: (c) reap and supervision keep running — a paused lane must still tear down an idle VM, or "paused" quietly
#: becomes "billing unwatched", which is this repo's most expensive recurring failure.
OPERATOR_HOLD = "gcp-s1f-rep-OPERATOR-HOLD.json"


def operator_hold(root=None):
    """The operator hold, or None. An UNREADABLE hold file HOLDS — the safe direction is not buying."""
    p = os.path.join(root or os.path.dirname(os.path.abspath(__file__)), OPERATOR_HOLD)
    if not os.path.exists(p):
        return None
    try:
        with open(p) as fh:
            doc = json.load(fh)
    except Exception as e:  # noqa: BLE001
        return {"reason": f"the hold file exists but could not be parsed ({type(e).__name__}) — HOLDING, "
                          f"because an unreadable instruction to stop is not permission to spend"}
    return doc if isinstance(doc, dict) else {"reason": "hold file is not an object — HOLDING"}


def feed_decision(queue, done, live_instances, attempts=None, progress=None,
                  max_noprogress=MAX_NOPROGRESS_LAUNCHES, hold=None):
    """Should the tick buy a GPU, and for which unit? PURE.

    queue           [unit_id] in the order they should run
    done            iterable of unit_ids whose ddg.json is already in GCS
    live_instances  how many GCE instances are RUNNING/PROVISIONING/STAGING/REPAIRING, project-wide
    attempts        {unit_id: {"iteration": int|None, "count": int}} — the durable launch ledger
    progress        {unit_id: int|None} — highest committed iteration the store proves RIGHT NOW

    Returns {"action": "launch"|"hold"|"idle", "unit_id": str|None, "cause": str, "why": str}.
    Only `launch` may provision. Every other action must leave the account untouched.
    """
    done = set(done or ())
    attempts = dict(attempts or {})
    progress = dict(progress or {})
    # ⛔ THE OPERATOR HOLD OUTRANKS EVERYTHING, INCLUDING `queue_complete`. It is checked FIRST so that a
    # paused lane says "paused, by a person, for this reason" rather than reporting whatever it would have
    # said anyway — the two look identical in a log and mean opposite things. Nothing below may provision.
    if hold:
        return {"action": "hold", "unit_id": None, "cause": "operator_hold",
                "why": ("⏸ PAUSED BY OPERATOR — this lane will not buy a GPU until "
                        f"{OPERATOR_HOLD} is deleted. Reason on record: "
                        f"{str(hold.get('reason') or '(none given)')[:400]}"
                        + (f" · paused {hold['paused_utc']}" if hold.get("paused_utc") else "")
                        + ". Banked work is untouched — the GCS commit store is continuous, so a resume "
                          "re-enters at the last COMMITTED.json and nothing is lost by waiting.")}
    if int(live_instances or 0) > 0:
        return {"action": "hold", "unit_id": None, "cause": "gpu_busy",
                "why": (f"{live_instances} GCE instance(s) live. GPUS_ALL_REGIONS = 1 is the binding cap "
                        f"(gcp-gpu-facts.md #1), so this lane is strictly serial and there is no second "
                        f"GPU to buy. Not a fault — the constraint working.")}
    remaining = [u for u in queue if u not in done]
    if not remaining:
        return {"action": "idle", "unit_id": None, "cause": "queue_complete",
                "why": (f"every unit in the queue has a ddg.json in GCS ({len(done)} of {len(queue)}). "
                        f"Nothing left to buy; the lane is finished, not stopped.")}
    # ★★ RESUME BEFORE START — the most-advanced unbanked unit wins, and map order is only the tiebreak.
    # (2026-08-01, caught by the first real tick: map order alone would have started a COLD edge while
    # `…cw_ms_free_acid__…__r1` sat on 400 committed iterations and 6.2 GiB of durable checkpoints.)
    # Three reasons, and the first is the one that matters:
    #   1. On a strictly serial GPU (GPUS_ALL_REGIONS = 1) a partially-sampled unit that keeps losing the
    #      queue is a partial that never lands — the "unrecorded partial gets restarted from zero" failure,
    #      arrived at by a different route. Banked MD is credit already spent; finishing it is the cheapest
    #      path to a result the lane can produce.
    #   2. A resume re-enters the leg exactly where it stopped, so it is also the launch that tests the
    #      failure the unit stopped ON — the highest-information one to run next (CLAUDE.md §6's
    #      early-abort rule, applied to a queue rather than a fan-out).
    #   3. It cannot starve the cold units: a resumed unit either lands (leaves the queue) or trips the
    #      no-progress breaker (holds), and both hand the GPU to the next one.
    # ⚠ An UNREADABLE census sorts as 0, not as "most advanced" — a listing that did not answer must never
    # win the queue on the strength of not having been read.
    remaining.sort(key=lambda u: (-(progress.get(u) or 0), queue.index(u)))
    unit = remaining[0]
    a = attempts.get(unit) or {}
    count = int(a.get("count") or 0)
    if count >= int(max_noprogress):
        it_now = progress.get(unit, None)
        if it_now is None:
            return {"action": "hold", "unit_id": unit, "cause": "census_unreadable",
                    "why": (f"{unit} is at the breaker threshold ({count} launches) and its committed "
                            f"census could not be READ this tick. An absent reading is not a reading of "
                            f"absence (CLAUDE.md §4): holding until the store answers, rather than "
                            f"counting a throttle as a failure to progress.")}
        it_last = a.get("iteration")
        if it_last is not None and int(it_now) <= int(it_last):
            return {"action": "hold", "unit_id": unit, "cause": "no_progress_breaker",
                    "why": (f"{unit} has been launched {count} times with its committed iteration frozen "
                            f"at {it_now} — no generation banked since. That is systematic, not unlucky, "
                            f"and an unattended feeder that kept buying would spend the credit balance on "
                            f"it. Holding. Clear it by fixing the cause, or by dispatching mode=run "
                            f"explicitly, which is not gated on this breaker.")}
    banked = progress.get(unit)
    return {"action": "launch", "unit_id": unit, "cause": "next_in_queue",
            "why": (f"{unit} leads {QUEUE_CYCLE} r{QUEUE_REPLICATE}'s unlanded units "
                    f"({'RESUMING from committed iteration %d' % banked if banked else 'a COLD start'}"
                    f"; most-advanced-first, map order as the tiebreak), no GCE instance is live, and it "
                    f"is under the {max_noprogress}-launch no-progress breaker (attempt {count + 1}).")}


def next_attempt(attempt, iteration_now):
    """The launch ledger entry to write AFTER a successful create. PURE.

    Resets the counter when the store proves the previous launch banked a new generation, and carries an
    UNREADABLE census forward without incrementing — the same asymmetry `feed_decision` applies, in the one
    place that could otherwise quietly poison it."""
    prev = dict(attempt or {})
    prev_it = prev.get("iteration")
    if iteration_now is None:
        return {"iteration": prev_it, "count": int(prev.get("count") or 0) + 1,
                "note": "census unreadable at launch; iteration carried forward unchanged"}
    if prev_it is None or int(iteration_now) > int(prev_it):
        return {"iteration": int(iteration_now), "count": 1,
                "note": "the previous launch banked new generations; counter reset"}
    return {"iteration": int(prev_it), "count": int(prev.get("count") or 0) + 1,
            "note": "no new generation banked since the last launch"}


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
#: the same one.
#:
#: ★★ A CELL, NOT A PARAGRAPH (2026-08-01). This was three sentences long, and `inflight_board.render`
#: sizes the `$/ns` column to its widest cell — so one lane's footnote set the width of that column for the
#: WHOLE board, pushing STATE and WHY far off to the right and making every other lane's rows harder to
#: read than this one's. The same string then blew out the markdown table
#: (`orchestrator_readout.board_table`), which is the form trimcrae actually reads.
#: The reasoning did not disappear: it is the lane's `note`, rendered ONCE in the section header where a
#: standing fact belongs, instead of being repeated on every row of a per-row column (CLAUDE.md §1 — the
#: ledger rule has one home, and `BOARD_LEDGER_NOTE` is it).
BOARD_USD_PER_NS = "— free GCP trial credit (separate ledger)"

#: The standing ledger caveat, for the lane's section note. Kept beside the cell it was extracted from so
#: the pair cannot drift, and carrying pricing.md's standing refusal to treat the L4 list rate as a
#: go-forward basis — the thing a reader could otherwise wrongly infer from a free row.
BOARD_LEDGER_NOTE = ("$0 real dollars: GCP trial credit is a SEPARATE LEDGER (expires 2026-10-10) and is "
                     "never summed into realized or ladder spend. L4 list $0.708/h is NOT a go-forward cost "
                     "basis (pricing.md); no $/ns is quoted against the ladder because no ladder dollar is "
                     "being spent.")


def _progress_cells(progress, live=True):
    """(pct, pct_of, eta_s, sentence) for a row, from `unit_progress`'s output. PURE.

    ★ % DONE AND ETA ARE ANSWERED SEPARATELY, AND THAT SEPARATION IS THE FIX. The percentage is two
    integers out of the store and needs no rate; the ETA needs a rate and says which input it is missing
    when it has none. The old row left BOTH blank on the strength of the second one's excuse.

    ⚠ `live=False` SUPPRESSES THE ETA BUT NOT THE PERCENTAGE, AND SAYS THE REMAINING HOURS ANYWAY.
    A wall-clock completion time for a unit holding no GPU would be a promise about a machine nobody has
    rented — but the WORK left is a measured quantity whatever the host situation, so it is reported as a
    duration ("~19.5 h of L4 wall clock left") rather than as a time of day. Rendering an absolute ETA
    there is the mistake; rendering nothing is the other one."""
    if not progress:
        return None, None, None, ("% DONE UNKNOWN and ETA UNKNOWN — no committed-checkpoint census was "
                                  "read this tick, so neither cell has an input. The store was not "
                                  "ASKED, which is not the same as the store being empty (CLAUDE.md §4).")
    bits = []
    if progress.get("pct") is None:
        bits.append("% DONE UNKNOWN — " + str(progress.get("pct_why") or ""))
    else:
        bits.append(str(progress.get("pct_why") or "") + ".")
    eta = progress.get("eta_s")
    if eta is None:
        bits.append("ETA UNKNOWN — " + str(progress.get("eta_why") or "") + ".")
    elif live:
        bits.append(f"ETA is for the {progress.get('eta_scope')} — {progress.get('eta_why') or ''}.")
    else:
        bits.append(f"NO ETA while it holds no host, but the work left IS measured: ~{eta / 3600.0:.1f} h "
                    f"of L4 wall clock for the {progress.get('eta_scope')} once one is running "
                    f"({progress.get('eta_why') or ''}).")
    return progress.get("pct"), progress.get("pct_of"), (eta if live else None), " ".join(b for b in bits if b)


def board_rows(unit, vm_status, vm_created, result_updated, phase=None, progress=None, feed=None,
               stall=None):
    """This lane's row for ONE unit. PURE.

    ★ AN IDLE LANE SAYS SO. The row is emitted in every state, including "nothing running" and including
    DONE — a lane that renders only while busy looks finished when it is merely stopped, and a row that
    VANISHES on completion is the same failure with the sign flipped: three queued units of which two have
    landed should read as `2/3 done`, not as a lane that shrank.

    `feed` is `feed_decision`'s verdict, and it is what makes a HOLD legible: an idle lane that decided not
    to buy and an idle lane that nothing is driving render identically without it, and those want opposite
    responses (CLAUDE.md §6's board-depth rule, in miniature).
    """
    name = f"{unit['edge_id'].replace('e_', '', 1)} r{unit['replicate']}"
    if result_updated:
        row = {"name": name, "pct": 100.0, "pct_of": None, "eta_s": None,
               "usd_per_ns": BOARD_USD_PER_NS, "state": "DONE",
               "why": f"ddg.json in GCS at {result_updated}. Holding no GPU; nothing left to buy."}
        return [row], (f"{unit['unit_id']} is DONE — ddg.json in GCS at {result_updated}. Nothing running; "
                       f"this lane holds no GPU.")
    live = str(vm_status or "").upper() in ("RUNNING", "PROVISIONING", "STAGING", "REPAIRING")
    pct, pct_of, eta_s, psent = _progress_cells(progress, live=live)
    if live:
        # ⚠ `⚠ NO NEW COMMIT` is a DIFFERENT STATE from RUNNING, for the same reason a paying row and a
        # refused row must never render alike: "advancing" and "up but producing nothing" want opposite
        # responses, and printing both as RUNNING is what made 63 minutes of silence unreadable.
        flagged = bool((stall or {}).get("stalled"))
        row = {"name": name, "pct": pct, "pct_of": pct_of, "eta_s": eta_s,
               "usd_per_ns": BOARD_USD_PER_NS,
               "state": "⚠ NO NEW COMMIT" if flagged else "RUNNING",
               "why": (f"GCE L4, {vm_status}, created {vm_created}. phase='{phase or '<none>'}'. {psent} "
                       + (f"[{(stall or {}).get('why')}] " if stall else "")
                       + f"Bounded at CREATE by --max-run-duration={MAX_RUN_S_RUN}s.")}
        note = (f"{unit['unit_id']} running on the single GCP GPU (GPUS_ALL_REGIONS=1 — strictly serial)."
                if not flagged else
                f"{unit['unit_id']} holds the single GCP GPU and has committed NOTHING for "
                f"{(stall or {}).get('silent_s', 0) / 60.0:.0f} min — flagged, not condemned; no reaper "
                f"acts on this.")
        return [row], note
    # ---- not running -----------------------------------------------------------------------------------
    # An ETA is meaningless with no host, but the PERCENTAGE is not: it is banked, durable work and it is
    # what tells a reader whether a relaunch resumes at 400 iterations or starts from zero.
    fed = (feed or {}).get("unit_id") == unit["unit_id"]
    if feed and feed.get("action") == "hold" and (fed or feed.get("cause") == "gpu_busy"):
        state, why = "HELD — NOT BUYING", f"[{feed.get('cause')}] {feed.get('why')} {psent}"
    elif feed and feed.get("action") == "launch" and fed:
        # ⚠ "NEXT UP", never "LAUNCHING". The fragment is written on both sides of the create and cannot
        # know which — a row that claimed a purchase it might not have made would be the board asserting an
        # act on the strength of having considered it. Once the VM exists the row renders RUNNING off the
        # instance list, which is evidence rather than intent.
        state, why = "IDLE — NEXT UP", (f"the autofeed tick buys this one next: {feed.get('why')} {psent}")
    else:
        state, why = "IDLE — NO HOST", (
            "no GCE VM and no ddg.json: this lane is holding no GPU and computing nothing. "
            "The autofeed tick (mode=autofeed, run by the schedule and by the supervisor) relaunches it "
            "and it resumes from its last committed generation in GCS (per-leg idempotent). " + psent)
    row = {"name": name, "pct": pct, "pct_of": pct_of, "eta_s": None,
           "usd_per_ns": "—", "state": state, "why": why}
    return [row], f"{unit['unit_id']} NOT running. The free GCP GPU is idle — that is expiring credit unspent."


def queue_board(entries, feed=None):
    """(rows, note) for the WHOLE queue — one row per unit, in run order. PURE.

    `entries` is [{"unit", "vm_status", "vm_created", "result_updated", "phase", "progress"}].

    ★ THE QUEUE IS THE LANE, NOT THE UNIT IN FRONT OF IT. Rendering only the current unit made a
    three-unit programme look like a one-unit job that had stopped, and gave a reader no way to see that
    two more were waiting behind it — which is exactly what nobody noticed was not being fed."""
    rows, done, running = [], 0, None
    for e in entries or ():
        r, _n = board_rows(e["unit"], e.get("vm_status"), e.get("vm_created"), e.get("result_updated"),
                           phase=e.get("phase"), progress=e.get("progress"), feed=feed,
                           stall=e.get("stall"))
        rows.extend(r)
        if e.get("result_updated"):
            done += 1
        elif str(e.get("vm_status") or "").upper() in ("RUNNING", "PROVISIONING", "STAGING", "REPAIRING"):
            running = e["unit"]["unit_id"]
    n = len(list(entries or ()))
    head = f"{QUEUE_CYCLE} r{QUEUE_REPLICATE}: {done} of {n} units have a ddg.json in GCS."
    if running:
        note = f"{head} {running} is on the single GCP GPU (GPUS_ALL_REGIONS=1 — strictly serial)."
    elif feed and feed.get("action") == "launch":
        note = f"{head} Nothing on a GPU; {feed.get('unit_id')} is next up and the autofeed tick buys it."
    elif feed and feed.get("action") == "idle":
        note = f"{head} Queue complete — the lane is finished, not stopped."
    elif feed:
        note = (f"{head} NOT buying this tick [{feed.get('cause')}]: {feed.get('why')} "
                f"The free GCP GPU is idle — that is expiring credit unspent.")
    else:
        note = f"{head} No feed decision was recorded this tick. The free GCP GPU is idle."
    # The ledger caveat is a fact about the LANE, so it is stated once here rather than repeated in every
    # row's `$/ns` cell — see `BOARD_USD_PER_NS` for the width damage that repetition did.
    return rows, f"{note} {BOARD_LEDGER_NOTE}"


# ★★ `publish`, NOT `write_fragment` — A LANE THAT ONLY WRITES ITS FRAGMENT RENDERS ITSELF STALE
# (measured 2026-08-01, 2:44 PM ET). Both functions below called `ib.write_fragment`, which writes
# `inflight-board.d/gcp-s1f-rep.json` and NOTHING else; the merged `inflight-board-all.md` is regenerated
# only by whoever calls `write_merged_board`, and the other two lanes get that for free because they call
# `ib.publish`. So this lane's fragment was 1.8 min old and carrying an ETA of 4:36 AM Aug 2 while the
# merged board showed the lane at **16 min ago, STALE (> 15 min)** with a blank ETA — because `stale_rows`
# had, correctly, refused to project a completion time from a reading nobody had re-taken.
#
# ⚠ THE DAMAGE IS THE CLASS OF ERROR, NOT THE 16 MINUTES. STALE is this board's alarm for "a lane stopped
# reporting while it was billing" (CLAUDE.md §6: the schedules are throttled and an agent has been
# dispatching ticks by hand, so that condition is real and must be visible). A lane that raises that alarm
# about ITSELF, on every tick, from full health, is an alarm being trained into background noise — and the
# blank ETA is the same defect one cell over: the safety rule that stops a stale rate becoming a promise
# fired against a rate measured 100 seconds earlier.
#
# The merged board is DERIVED IN FULL from every lane's fragment, so any lane may safely regenerate it —
# whoever writes it last rebuilds every section and no lane's rows live there (`inflight_board.__doc__`).
# In CI this in-process merge is then discarded by the publish step's `reset --hard FETCH_HEAD` and redone
# against upstream's fragments; both are needed, and the workflow comment says why.
def write_board(unit, vm_status, vm_created, result_updated, phase=None, root=None, progress=None,
                feed=None):
    """Publish the fragment through inflight_board's own writer, so the document shape has one home."""
    import inflight_board as ib
    rows, note = board_rows(unit, vm_status, vm_created, result_updated, phase=phase, progress=progress,
                            feed=feed)
    frag, _board = ib.publish(BOARD_LANE, rows, note=note, root=root)
    return frag


def write_queue_board(entries, feed=None, root=None):
    """Publish the WHOLE queue's fragment through inflight_board's own writer."""
    import inflight_board as ib
    rows, note = queue_board(entries, feed=feed)
    frag, _board = ib.publish(BOARD_LANE, rows, note=note, root=root)
    return frag


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# THE TICK — gather, decide, publish. The ONLY impure function in this module.
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════

def _gcloud(args, timeout=120):
    """stdout of a gcloud call, or None if it could not be read. NEVER "" on failure.

    ⚠ THE None IS LOAD-BEARING. `""` is a legitimate answer (an empty listing); a failed call is not an
    answer at all, and the difference decides whether the breaker counts a non-advance or holds
    (CLAUDE.md §4). Collapsing the two is the exact bug this module's docstrings keep naming."""
    import subprocess
    try:
        p = subprocess.run(["gcloud"] + list(args), capture_output=True, text=True, timeout=timeout)
    except Exception:                                          # noqa: BLE001
        return None
    return p.stdout if p.returncode == 0 else None


def gather_facts(bucket, vm_prefix="gcp-s1frep-", cycle=QUEUE_CYCLE, replicate=QUEUE_REPLICATE):
    """Everything the tick needs, read from GCE and GCS. IMPURE — the cloud edge, and nothing else."""
    import json as _json
    vms_raw = _gcloud(["compute", "instances", "list", "--format=json"])
    vms = _json.loads(vms_raw) if vms_raw else []
    live_states = ("RUNNING", "PROVISIONING", "STAGING", "REPAIRING")
    live = [v for v in vms if str(v.get("status") or "").upper() in live_states]
    facts = {"live_instances": len(live),
             "live_names": [v.get("name") for v in live],
             "vms_readable": vms_raw is not None,
             "units": []}
    for u in queue_units(cycle, replicate):
        uris = gcs_uris(u, bucket)
        base, rec = uris["unit_uri"], u["receptor"]
        vm = next((v for v in vms if (v.get("labels") or {}).get("s1f-edge") == u["edge_id"]
                   and str((v.get("labels") or {}).get("s1f-rep") or "1") == str(u["replicate"])), None)
        upd = _gcloud(["storage", "objects", "describe", uris["result_uri"], "--format=value(updated)"])
        legs_done = [lg for lg in SCIENCE_LEGS
                     if _gcloud(["storage", "objects", "describe", f"{base}/leg_{rec}_{lg}.json",
                                 "--format=value(name)"])]
        ls = _gcloud(["storage", "ls", "-l", f"{base}/**"])
        # The driver's own target line, from whichever leg log exists. One home for the denominator
        # (`inflight_board.parse_targets`); this only fetches the text it parses.
        tgt = ""
        for lg in SCIENCE_LEGS:
            txt = _gcloud(["storage", "cat", f"{base}/{lg}.log"], timeout=180)
            if txt and parse_targets(txt):
                tgt = txt
                break
        att = _gcloud(["storage", "cat", f"{base}/attempts.json"])
        try:
            attempts = _json.loads(att) if att else {}
        except Exception:                                      # noqa: BLE001
            attempts = {}
        facts["units"].append({
            "unit_id": u["unit_id"], "edge_id": u["edge_id"], "replicate": u["replicate"],
            "result_updated": (upd or "").strip() or None,
            "vm_status": (vm or {}).get("status") or "", "vm_created": (vm or {}).get("creationTimestamp") or "",
            "machine_type": ((vm or {}).get("machineType") or "").split("/")[-1] or None,
            "phase": (_gcloud(["storage", "cat", f"{base}/phase.txt"]) or "").strip().split("\n")[-1],
            "ls": ls, "ls_readable": ls is not None,
            "targets_line": tgt, "legs_done": legs_done, "attempts": attempts,
        })
    return facts


def tick(facts, root=None):
    """Decide, publish the fragment, and return the verdict. PURE given `facts`.

    The whole reason `gather_facts` and this are separate: every judgement the lane makes about buying a
    GPU is exercisable from a canned document, with no cloud and no credit."""
    entries, done, progress_by_unit, attempts = [], [], {}, {}
    order = []
    for f in facts.get("units") or ():
        u = unit_for(f["edge_id"], f.get("replicate") or QUEUE_REPLICATE)
        order.append(u["unit_id"])
        marks = checkpoint_marks(parse_ls_long(f.get("ls") or "")) if f.get("ls_readable", True) else None
        targets = parse_targets(f.get("targets_line") or "")
        rates, phases = {}, {}
        for lg in SCIENCE_LEGS:
            q = quoted_rate((marks or {}).get(lg) or [])
            if q["s_per_iter"]:
                rates[lg], phases[lg] = q["s_per_iter"], q.get("phase")
        prog = unit_progress(marks or {}, targets, legs_done=f.get("legs_done") or (), leg_rates=rates,
                             rate_phases=phases)
        prog["rates"] = {lg: quoted_rate((marks or {}).get(lg) or []) for lg in SCIENCE_LEGS}
        # ★ THE MEASUREMENT IS RECORDED BY THE SAME PASS THAT READS IT. A rate produced only by a
        # hand-dispatched forensic run is a rate that goes stale the moment nobody dispatches one — which
        # is the failure this whole lane is a correction for. Every tick that can see markers refreshes
        # the artifact, so the committed measurement can never lag the store by more than one tick.
        if marks and targets and any(marks.get(lg) for lg in SCIENCE_LEGS):
            write_rate_artifact(marks, targets, u["unit_id"], machine_type=f.get("machine_type"),
                                root=root)
        live_now = str(f.get("vm_status") or "").upper() in ("RUNNING", "PROVISIONING", "STAGING",
                                                              "REPAIRING")
        cur = next((lg for lg in SCIENCE_LEGS if lg not in (f.get("legs_done") or ())), SCIENCE_LEGS[0])
        st = stall_verdict((marks or {}).get(cur) or [], phase_started(f.get("phase")),
                           datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), live_now)
        entries.append({"unit": u, "vm_status": f.get("vm_status"), "vm_created": f.get("vm_created"),
                        "result_updated": f.get("result_updated"), "phase": f.get("phase"),
                        "progress": prog, "stall": st})
        if f.get("result_updated"):
            done.append(u["unit_id"])
        # ⚠ `None`, not 0, when the listing could not be read — `feed_decision` distinguishes them.
        progress_by_unit[u["unit_id"]] = None if marks is None else (leg_stage((marks or {}).get("complex"))[1]
                                                                     or 0)
        attempts[u["unit_id"]] = f.get("attempts") or {}
    live = facts.get("live_instances") if facts.get("vms_readable", True) else 1
    # ⛔ The hold is read HERE, at the one call site, so `feed_decision` stays PURE and testable.
    d = feed_decision(order, done, live, attempts=attempts, progress=progress_by_unit,
                      hold=operator_hold(root=root))
    if not facts.get("vms_readable", True):
        d = {"action": "hold", "unit_id": None, "cause": "instance_list_unreadable",
             "why": ("`gcloud compute instances list` did not answer this tick. An unreadable list is not "
                     "an empty one (CLAUDE.md §4), and buying on it could put a second GPU against a "
                     "GPUS_ALL_REGIONS = 1 cap. Holding until it reads.")}
    path = write_queue_board(entries, feed=d, root=root)
    d["fragment"] = path
    d["queue"] = order
    d["done"] = done
    d["progress"] = progress_by_unit
    if d["action"] == "launch":
        d["next_attempt"] = next_attempt(attempts.get(d["unit_id"]), progress_by_unit.get(d["unit_id"]))
        d["edge_id"] = next(f["edge_id"] for f in facts["units"]
                            if unit_for(f["edge_id"], f.get("replicate") or QUEUE_REPLICATE)["unit_id"]
                            == d["unit_id"])
        d["replicate"] = next(f.get("replicate") or QUEUE_REPLICATE for f in facts["units"]
                              if unit_for(f["edge_id"], f.get("replicate") or QUEUE_REPLICATE)["unit_id"]
                              == d["unit_id"])
    return d


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


def _census(ls_text, targets_line="", legs_done=()):
    marks = checkpoint_marks(parse_ls_long(ls_text))
    targets = parse_targets(targets_line or "")
    rates = {lg: quoted_rate(marks.get(lg) or []) for lg in SCIENCE_LEGS}
    prog = unit_progress(marks, targets, legs_done=legs_done,
                         leg_rates={lg: r["s_per_iter"] for lg, r in rates.items() if r["s_per_iter"]},
                         rate_phases={lg: r.get("phase") for lg, r in rates.items()})
    return {
        "targets": list(targets) if targets else None,
        "legs": {lg: {"stage": leg_stage(marks.get(lg) or [])[0],
                      "iteration": leg_stage(marks.get(lg) or [])[1],
                      "commits": len(marks.get(lg) or []),
                      "rate": rates[lg],
                      "intervals": [{"from": a0, "to": b0, "seconds": s, "s_per_iter": r}
                                    for a0, b0, s, r in interval_rates(marks.get(lg) or [])]}
                 for lg in SCIENCE_LEGS},
        "progress": prog,
    }


def _cmd_census(a):
    d = _census(sys.stdin.read(), a.targets_line, a.legs_done or ())
    if a.json:
        print(json.dumps(d, indent=1))
    else:
        for lg, v in d["legs"].items():
            print(f"{lg}: stage={v['stage']} iteration={v['iteration']} commits={v['commits']} "
                  f"s_per_iter={v['rate']['s_per_iter']}")
        _shell({"PCT": d["progress"]["pct"], "ETA_S": d["progress"]["eta_s"],
                "ETA_SCOPE": d["progress"]["eta_scope"], "TARGETS": d["targets"]})
    return 0


def _cmd_rate(a):
    doc = load_rate_artifact()
    if not doc:
        raise SystemExit(f"no {RATE_ARTIFACT} — no fan-out leg has been measured on an L4 yet")
    rep = rate_report(marks_from_artifact(doc), tuple(doc["derived"]["targets"] or ()) or None,
                      n_windows=doc["derived"]["n_windows"])
    if a.sync_doc:
        # The lane's publish step calls this AFTER its `reset --hard`, so it edits the doc upstream is
        # actually holding. Prints which of the three outcomes happened — "unchanged" is a pass, not a
        # silence, because a sync that quietly did nothing is how the drift got here in the first place.
        r = sync_rate_table_doc(rep)
        print({True: "§1e regenerated from " + RATE_ARTIFACT,
               False: "§1e already current",
               None: "§1e NOT synced — no doc or no usable fence at " + facts_doc_path()}[r])
        return 0 if r is not None else 1
    if a.markdown_table:
        print(rate_markdown_table(rep))
    elif a.json:
        print(json.dumps(rep, indent=1))
    else:
        for lg, r in rep["legs"].items():
            print(f"{lg}: s/iter={r.get('s_per_iteration')} leg_h={r.get('leg_hours')} "
                  f"ns/day agg={r.get('ns_per_day_aggregate')}")
    return 0


def _cmd_tick(a):
    bucket = a.bucket or (os.environ.get("PROJECT", "") + BUCKET_SUFFIX)
    facts = json.load(open(a.facts)) if a.facts else gather_facts(bucket, vm_prefix=a.vm_prefix)
    if a.dump_facts:
        with open(a.dump_facts, "w") as fh:
            json.dump(facts, fh, indent=1)
    d = tick(facts)
    print(json.dumps({k: v for k, v in d.items() if k != "progress"}, indent=1), file=sys.stderr)
    _shell({"FEED_ACTION": d["action"], "FEED_CAUSE": d["cause"],
            "FEED_UNIT_ID": d.get("unit_id") or "", "FEED_EDGE": d.get("edge_id") or "",
            "FEED_REP": d.get("replicate") or "", "FRAGMENT": d.get("fragment") or ""})
    print(f"FEED_WHY={d['why']}")
    if d.get("next_attempt"):
        print(f"NEXT_ATTEMPT_JSON={json.dumps(d['next_attempt'])}")
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

    rt = sub.add_parser("rate", help="the measured L4 throughput, DERIVED from the committed artifact")
    rt.add_argument("--markdown-table", dest="markdown_table", action="store_true")
    rt.add_argument("--sync-doc", dest="sync_doc", action="store_true",
                    help="rewrite gcp-gpu-facts.md §1e's fenced block from the artifact (what CI runs)")
    rt.add_argument("--json", action="store_true")
    rt.set_defaults(func=_cmd_rate)

    cs = sub.add_parser("census", help="derived per-leg progress from `gcloud storage ls -l` on stdin")
    cs.add_argument("--targets-line", dest="targets_line", default="",
                    help="text containing the driver's `warmup_target=… prod_target=…` line")
    cs.add_argument("--legs-done", dest="legs_done", nargs="*", default=[])
    cs.add_argument("--json", action="store_true")
    cs.set_defaults(func=_cmd_census)

    tk = sub.add_parser("tick", help="gather, decide whether to launch, publish the fragment")
    tk.add_argument("--bucket", default=None)
    tk.add_argument("--vm-prefix", dest="vm_prefix", default="gcp-s1frep-")
    tk.add_argument("--facts", default=None, help="read a canned facts document instead of the cloud")
    tk.add_argument("--dump-facts", dest="dump_facts", default=None)
    tk.set_defaults(func=_cmd_tick)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
