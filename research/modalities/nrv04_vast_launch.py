#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — Vast.ai launcher (prereg §6; runs on CI with VAST_API_KEY + AWS creds).

One Vast instance per (leg, seed) unit → genuinely N-wide parallel (no shared-pool wall). Each instance:
clones the repo, builds the MD env, stages its leg from the co-fold CIF in S3 (nrv04_covalent_assemble),
runs the endpoint-MD driver (nrv04_covalent_md) wrapped by autoteardown, uploads the leg JSON to S3, and
self-destroys. GPU/bid targeting come from ResourceSpec + the tuned VastBackend (RTX-4090-class, >=32 GB host
RAM for the 146k-atom ternary, midpoint spot bid).

PILOT-ONE-LEG-FIRST (standing rule): with PILOT_ONLY=1 we submit ONLY the highest-abort-information unit
(cov_nr4a1 seed 0) to calibrate real GPU-h -> $ before fanning out the other 17. The build_jobspec construction
is pure + unit-tested; submit() needs live creds.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend, s3_checkpoint_uri  # noqa: E402
from nrv04_covalent_panel import PANEL, enumerate_units, leg_env, unit_name  # noqa: E402
from nrv04_ligands import LIGANDS  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
# co-fold outputs in the reused S3 bucket (nrv04_ternary.py --run --negatives writes one subdir per system).
# `or DEFAULT` not `get(k, DEFAULT)`: a workflow input that is present-but-EMPTY would otherwise set the prefix
# to "", silently sending every staged read and every result to the bucket ROOT.
COFOLD_PREFIX = os.environ.get("NRV04_COFOLD_PREFIX") or "nrv04-covalent-cofold"
RESULT_PREFIX = os.environ.get("NRV04_RESULT_PREFIX") or "nrv04-covalent-results"

# panel ligand -> the co-fold SYSTEM subdir it comes from (nrv04_ternary.py naming).
_LIGAND_TO_SYSTEM = {"nrv04": "nr4a1", "nrv04_epimer": "neg_inactive", "celastrol": "neg_celastrol"}

# Endpoint-MD host: 4090 24 GB. The solvated complex here is ~50-70k atoms (NOT the 146k-atom FEP hybrid), so
# it does NOT need the FEP's beefy host — over-specifying RAM/vCPU/disk excludes the cheap 4090s and leaves only
# high-demand hosts where the spot floor (min_bid) ~= on-demand. Modest requirements let the bid find a cheap
# 4090 (~$0.10-0.15/hr spot). reliability filter kept (a crash, unlike preemption, we don't tolerate).
# RTX 3090 (24 GB Ampere) is the price/perf sweet spot for these endpoint-MD legs: probe_offers (2026-07-22)
# showed 3090s bidding ~$0.07-0.09/hr vs the cheapest 4090 at $0.144 and the host we first landed at $0.264.
# A 466k-atom system needs <4 GB VRAM so 24 GB is ample, and Ampere/cuda-13 hosts have no PTX-version issue.
# We're not racing (endpoint-MD, checkpointed, parallel), so the 3090's ~0.6x-4090 throughput is fine and it's
# ~70% cheaper than the first host + under GCP L4 spot. _select_cheapest_offer still falls back to any capable
# 24 GB card if 3090s are scarce, always ranked by the true interruptible cost (min_bid).
# ⚠ RAM RAISED 16 -> 48 GB (2026-07-24). 16 GB was not a modest-requirements choice, it was too small: both
# retrospective pilot legs were OOM-KILLED (the co-fold lane's instance log showed the kernel's bare `Killed`
# on the same account the same evening, and these legs died the same way — partial output, no traceback, no
# result). Solvating and parameterizing a ~466k-atom assembly is RAM-bound, and the covalent panel surviving on
# 16 GB was host luck on actual free memory, not headroom. VRAM is NOT the constraint here (<4 GB is used);
# host RAM is. The extra RAM costs cents/hr and buys legs that finish.
TERNARY_RES = ResourceSpec(gpu="rtx3090", min_vram_gb=24, vcpus=4, ram_gb=48, disk_gb=60, interruptible=True)


# =============================================================================================================
# ⛔ THE BUY LINE — this lane rented at ANY price until 2026-07-31
# =============================================================================================================
# WHAT WAS WRONG, measured rather than asserted. `TERNARY_RES` never set `max_usd_per_ns`, so it defaulted to
# `None` and the ceiling clause in `gpu_backend.rank_offers_by_usd_per_ns` was INERT — the lane had no price
# refusal of any kind. Its own recorded rentals are $0.10-0.21/hr on an RTX 3090 (prereg §7 / the 15-leg S3
# ledger). Against the repo's approved rate that band is mostly ABOVE the line: with the 3090's measured
# throughput the line falls at ~$0.126/hr, so $0.13-0.21/hr is 1.98x-3.21x the ladder basis. CLAUDE.md §1's
# ruling is that a row printing `⚠ DRIFT` is a row we do not buy, and §6 extends that to EVERY rental of a new
# host — "resume and cold single unit included".
#
# WHY A FUNCTION AND NOT A CONSTANT ON `TERNARY_RES` (`ResourceSpec.max_usd_per_ns`'s own contract): the two
# callers want opposite things. A market GATE must SEE the expensive offers in order to report how far above
# the line the board sits; only the spec handed to `submit` carries the cap. So the default here is UNSET and
# the cap is added at jobspec-build time.
#
# DERIVED, NEVER TYPED (CLAUDE.md §1 + lint_derived_thresholds.py): the invariant is the absolute
# `inflight_usd_per_ns.APPROVED_USD_PER_NS`, and the multiple of the ladder basis falls out of it. A literal
# here would be a number that silently changes meaning the next time the throughput table is re-anchored.
def buy_ceiling_usd_per_ns():
    """The highest $/ns this lane may PAY for one host. Imported, never re-typed."""
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    return APPROVED_USD_PER_NS


def endpoint_md_resources(max_usd_per_ns=None, exclude=(), gpu=None):
    """The endpoint-MD `ResourceSpec`, optionally carrying the binding per-offer buy line.

    Handing the ceiling to `submit`'s spec makes overpaying STRUCTURALLY impossible rather than procedurally
    discouraged: `rank_offers_by_usd_per_ns` drops every offer above the cap before selection sees it —
    including on every fallback after a `resources_unavailable` capacity refusal, which is exactly where a
    launcher that re-checked one chosen offer would leak.

    Note `gpu` stays a HINT (`require_gpu` is False): ranking is by $/ns, so a 4090 that clears the line wins
    over a 3090 that does not. That is the intended behaviour — the card is not the decision, the offer is."""
    import dataclasses
    spec = dataclasses.replace(TERNARY_RES, max_usd_per_ns=max_usd_per_ns)
    if gpu:
        spec.gpu = gpu
    if exclude:
        spec.exclude_machine_ids = tuple(str(m) for m in exclude)
    return spec

# Boot image. Vast's cheap 4090 hosts have catastrophically slow BOOT-TIME PROVISIONING (Vast apt-installs
# python3/openssh/systemd from archive.ubuntu.com at container start — ~40 min on these hosts, diag-confirmed
# across 4+ hosts; it's Vast's own container init, not our onstart). A Vast-READY base image (ssh + python +
# the provisioning tooling already baked, and commonly cached on Vast hosts) makes that a no-op. Overridable via
# $VAST_IMAGE for A/B testing. The packed conda MD env is still curled from S3 into /opt/mamba/envs/md — we do
# NOT use the image's python, so the image only has to boot fast.
VAST_IMAGE = os.environ.get("VAST_IMAGE") or "docker.io/triskit23/nrv04vast:latest"

# The onstart pipeline. $VARS are exported by _vast_onstart (leg env + forwarded AWS creds + CHECKPOINT_URI +
# ENV_TARBALL_URL). THE BOTTLENECK FIX: instead of a ~25-min `micromamba create` MD solve PER instance (the
# diagnosed stall), each instance extracts a PRE-PACKED conda env (built once on CI via conda-pack, cached in
# S3) from a presigned URL in ~1-2 min. Repo code comes from the public codeload tarball (no git in the base
# image). Everything after that (aws, python) runs out of the extracted env. Phase markers land in S3 for
# `collect`/`diag`.
_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
# curl is already present on the Vast base image (its ssh provisioning installs it) -> only apt if it's genuinely
# missing, and never let a flaky ubuntu mirror abort the boot (diag saw archive.ubuntu.com time out on one host).
command -v curl >/dev/null 2>&1 || { apt-get update -q || true; apt-get install -y -q --no-install-recommends curl ca-certificates || true; }
# --- MD conda env: BAKED into the pre-provisioned image (skip); else fall back to the S3-packed tarball ---
if [ ! -x /opt/mamba/envs/md/bin/python ]; then
  mkdir -p /opt/mamba/envs/md
  curl -Ls "$ENV_TARBALL_URL" | tar xz -C /opt/mamba/envs/md
  /opt/mamba/envs/md/bin/conda-unpack || true
fi
export PATH=/opt/mamba/envs/md/bin:$PATH
PY=/opt/mamba/envs/md/bin/python
AWS=/opt/mamba/envs/md/bin/aws
# mark() used to end in `2>/dev/null || true`, which hid EVERY S3 write failure. A monitoring mechanism that
# swallows its own errors is worse than none: it produced hours of "the leg is silent" with no way to tell a
# dead leg from a broken marker. The FIRST mark is now a hard PREFLIGHT — if we cannot write to $RESULT_S3 the
# leg is unmonitorable and unable to deliver a result, so fail immediately and loudly instead of burning GPU.
mark() { echo "$1 $(date -u +%FT%TZ)" | $AWS s3 cp - "$RESULT_S3/phase.txt" || echo "[mark] WARN could not write phase '$1' to $RESULT_S3"; }
echo "preflight $(date -u +%FT%TZ)" | $AWS s3 cp - "$RESULT_S3/phase.txt" || {
  echo "[preflight] FATAL cannot write to $RESULT_S3 — refusing to run an unmonitorable leg"; exit 4; }
# --- stream this leg's stdout to S3 continuously, so an OOM kill or a crash leaves a POST-MORTEM. Both pilot
# legs died with no traceback because nothing captured stdout and the EXIT trap tore the host down with it.
exec > >(tee -a /tmp/run.log) 2>&1
( while true; do $AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true; sleep 45; done ) &
LOGSYNC_PID=$!
trap '$AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true' EXIT
mark env-ready
# --- repo code (public codeload tarball; the base image has no git) ---
# IDEMPOTENT: Vast restarts the container after an OOM kill and re-runs this script. A stale extraction used to
# leave `cd Rare-cancers-*` matching multiple dirs (and the co-fold lane's `git clone` failing outright), so a
# restart could never recover — it died on setup instead of retrying the work.
rm -rf Rare-cancers-*
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
mark cloned
mkdir -p /tmp/in /tmp/out /tmp/cofold
export INPUT_DIR=/tmp/in OUTPUT_DIR=/tmp/out CKPT_DIR=/tmp/out
# --- stage this leg from its co-fold system in S3 -> INPUT_DIR/<LEG_ID>/{complex.pdb,ligand.sdf} ---
$AWS s3 cp "$COFOLD_PREFIX_S3" /tmp/cofold/ --recursive --exclude '*' --include '*_model_0.cif'
export COFOLD_CIF=$(find /tmp/cofold -name '*_model_0.cif' | sort | head -1)
test -n "$COFOLD_CIF" || { echo "no co-fold CIF found under $COFOLD_PREFIX_S3"; exit 3; }
$PY -c "import os; from nrv04_covalent_panel import leg_by_id; from nrv04_ligands import LIGANDS; \
from nrv04_covalent_assemble import assemble_leg; lg=leg_by_id(os.environ['LEG_ID']); \
assemble_leg(os.environ['COFOLD_CIF'], lg, LIGANDS[lg.ligand], os.environ['INPUT_DIR'])"
mark staged
# Ligand charging is NAGL (md_settings.CHARGE_METHOD) — deterministic + ~seconds even on the 166-atom recruiter,
# assigned in-process by the driver. No charge cache is needed (am1bcc/sqm — the ~40-min bottleneck — is not used).
# --- endpoint-MD driver, teardown-guarded + per-unit checkpointed ---
mark md-running
$PY autoteardown.py $PY nrv04_covalent_md.py
mark md-done
# --- publish the leg readout JSON ---
$AWS s3 cp /tmp/out/ "$RESULT_S3/" --recursive --exclude '*' --include 'leg_*.json'
kill $LOGSYNC_PID 2>/dev/null || true
$AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors || true
mark uploaded
"""

# ★★ THE ATTEMPT MARKER — written by the HOST, which is what makes the breaker's count MEASURED rather than
# remembered (`leg_failure_breaker.__doc__`: "No new state file, and nothing to drift"). Appended to the
# retro pipeline only, in the EXACT layout `leg_failure_breaker.count_attempts` already globs
# (`<prefix>/legs/<unit>/attempts/run-<ts>.log`), so that module is reused verbatim.
#
# ⚠ IT IS WRITTEN AT THE START, NOT AT THE END, and it is a MARKER rather than the log. A leg that dies in
# `build_system` never reaches the end of the script — and that is exactly the failure the breaker exists to
# stop re-buying. An archive written on a clean exit would count precisely the attempts that did not need
# counting; a deferred copy of `run.log` would miss any attempt that died before the timer. One `s3 cp` of a
# few bytes, immediately after the env is up, counts every rental we ever pay for.
_RETRO_ATTEMPT_MARKER = r"""
echo "attempt $(date -u +%FT%TZ) instance=${CONTAINER_ID:-unknown}" | \
  $AWS s3 cp - "$ATTEMPT_S3/run-$(date -u +%Y%m%dT%H%M%SZ).log" || \
  echo "[attempt] WARN could not archive the attempt marker — the failure breaker will undercount"
"""

# The pre-packed conda MD env, built once by the build_env CI job and cached here (conda-pack tar.gz).
MDENV_KEY = os.environ.get("MDENV_KEY", "mdenv/nrv04md.tar.gz")


def cofold_prefix_s3(leg, bucket):
    """The S3 PREFIX of the co-fold system that feeds this leg (the onstart globs it for *_model_0.cif, robust to
    Boltz's nested predictions/ layout). nrv04->nr4a1, celastrol->neg_celastrol, epimer->neg_inactive."""
    system = _LIGAND_TO_SYSTEM[leg.ligand]
    return f"s3://{bucket}/{COFOLD_PREFIX}/{system}/"


def stage_test(bucket):
    """De-risk the staging on REAL Boltz output (free CI, no Vast): pull the cov_nr4a1 co-fold CIF from S3 and
    run assemble_leg, verifying complex.pdb + a bond-order-correct ligand.sdf are produced. Proves the assembler
    handles a real multi-chain co-fold CIF before we rent a GPU."""
    import boto3
    from nrv04_covalent_assemble import assemble_leg
    from nrv04_covalent_panel import leg_by_id
    base = os.environ.get("NRV04_COFOLD_PREFIX", COFOLD_PREFIX).rstrip("/")
    s3 = boto3.client("s3")
    leg = leg_by_id("cov_nr4a1")
    system = _LIGAND_TO_SYSTEM[leg.ligand]
    cifs = _s3_list(s3, bucket, f"{base}/{system}/", suffix="_model_0.cif")
    if not cifs:
        raise SystemExit(f"[stage-test] no co-fold CIF under {base}/{system}/")
    key = sorted(cifs)[0]
    os.makedirs("/tmp/cofold", exist_ok=True)
    s3.download_file(bucket, key, "/tmp/cofold/model_0.cif")
    print(f"[stage-test] pulled {key}", flush=True)
    res = assemble_leg("/tmp/cofold/model_0.cif", leg, LIGANDS[leg.ligand], "/tmp/staged")
    import os.path as _p
    cpdb = _p.join(res["out"], "complex.pdb"); lsdf = _p.join(res["out"], "ligand.sdf")
    n_atom = sum(1 for line in open(cpdb) if line.startswith(("ATOM", "HETATM")))
    print(f"[stage-test] OK: {res['ligand_atoms']} ligand atoms, complex.pdb {n_atom} atoms, "
          f"sdf {_p.getsize(lsdf)} bytes", flush=True)
    if n_atom < 500:
        raise SystemExit(f"[stage-test] complex.pdb too small ({n_atom} atoms) — chain surgery failed")
    print("STAGE-TEST PASS — assembler handles the real co-fold CIF.", flush=True)


def _vast_instance_logs(key, iid, tail=400):
    """Fetch a running instance's onstart/container stdout via Vast's request-logs flow (PUT triggers collection
    to a URL, then we poll that URL). Returns the log text or a status note."""
    import time
    import urllib.request
    r = _vast_request("PUT", f"/instances/request_logs/{iid}/", key, body={"tail": str(tail)})
    url = r.get("result_url")
    if not url:
        return f"(no result_url: {r})"
    for _ in range(12):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                txt = resp.read().decode(errors="replace")
            if txt.strip():
                return txt[-6000:]
        except Exception:  # noqa: BLE001 — log not written yet
            pass
        time.sleep(4)
    return "(logs not ready after polling)"


def leg_cost_usd(uptime_s, dph_total):
    """PURE (unit-tested): $ = wall-clock hours a rented instance was ALIVE x the ACTUAL bid rate paid
    (dph_total, the interruptible bid we won — NOT dph_base on-demand). Returns None if inputs are missing.

    ⚠ THIS IS RENTAL TIME, NOT LEG TIME. See `_update_price_ledger` and `ledger_entry_reading` — the
    2026-07-31 finding was one row of 156.0 h against a leg that computed for 1.04 h."""
    try:
        return round((float(uptime_s) / 3600.0) * float(dph_total), 4)
    except (TypeError, ValueError):
        return None


_PRICE_LEDGER_KEY_SUFFIX = "_price_ledger.json"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⚠ WHAT `uptime_s` IS — READ THIS BEFORE QUOTING A ROW OF THIS LEDGER
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# MEASURED 2026-07-31, from the ledger, the CI logs and the live Vast census (nrv04_retro_price_forensics.py;
# report: nrv04-retro-price-forensics.json). `uptime_s` is written as `now - instance.start_date` at whatever
# poll happened to see the instance. It is therefore:
#
#   • NOT the leg's compute time. Row `nrv04retro-retro_noncov_nr4a2-m1-r0` read 561615 s = 156.0 h against a
#     leg whose own record says prod_wall_s 3730.5 = 1.04 h — 150.5x. That was NOT a units bug: instance
#     45749905 really was rented 6:59 PM ET Fri Jul 24 and really was destroyed 6:59 AM ET Fri Jul 31, six and
#     a half days later, at $0.16556/hr (run 30625438729, job 91139494243, 10:59:45-46 UTC). The leg finished
#     on 07-26 and the host was never reaped, because nothing dispatched this lane's collect for five days.
#   • NOT the whole rental either — it is an age at ONE observation, so it is a LOWER bound on billed
#     wall clock (the poll is at or before teardown) and never an upper one.
#   • MEASURED ON `start_date`, which IS the rental start on this account: the same census that showed the
#     6.5-day row showed three sibling hosts rented 14/31/72 min earlier reading start_date ages of
#     14m/31m/1h12m, while their `duration` field (the HOST MACHINE's uptime, the field
#     `congeneric_fanout_vast._age_min` exists to avoid) read 135d/1958d/30d. So the field means what it says.
#
# The failure this must never repeat is a READER's, not the arithmetic's: a row of this ledger is billed
# rental time and answers "what did this host cost", never "how long did the science take".
#
# A rental that outlives any plausible leg. The lane's own hang-guard is MAX_LEG_MIN (240 min default), so a
# whole leg — provision + stage + run + one poll of lag — cannot approach this. A row above it is idle
# rental, i.e. money with no science, and must be reported as a LEAK rather than averaged into a $/leg.
LEAK_ABOVE_S = 6 * 3600


def ledger_entry_reading(entry, leak_above_s=LEAK_ABOVE_S):
    """PURE (unit-tested). Classify ONE ledger row, so a reader cannot mistake rental time for leg time.

    Returns {"kind": "leg"|"leak"|"unknown", "hours", "usd", "why"}. `leak` means the rental outlived any
    plausible leg and its dollars are idle-host dollars — real money, but not the price of a leg, so
    `_update_price_ledger` keeps it OUT of the per-leg mean and reports it separately."""
    up = entry.get("uptime_s")
    usd = entry.get("cost_usd")
    if up is None:
        return {"kind": "unknown", "hours": None, "usd": usd,
                "why": "no uptime recorded — no host was ever observed for this label"}
    hours = round(float(up) / 3600.0, 4)
    if float(up) > leak_above_s:
        return {"kind": "leak", "hours": hours, "usd": usd,
                "why": (f"the host was alive {hours:.1f} h, past the {leak_above_s / 3600:.0f} h a whole leg "
                        f"can take (MAX_LEG_MIN backstop + provisioning). This is idle rental time, not the "
                        f"price of a leg — see the 2026-07-31 orphan, realised_spend.ATTESTED.")}
    return {"kind": "leg", "hours": hours, "usd": usd,
            "why": "rental age is consistent with one leg (provision + run + poll lag)"}


def _finalizable(label, done_units, start_date, done_mtimes=None):
    """PURE (unit-tested). May this label's cost be FROZEN at the current observation?

    Only if its result was written by THIS rental. `final` used to latch on the mere existence of a
    `leg_*.json`, so re-renting a unit that already had a result froze the cost at the first poll after
    launch — minutes — while the host went on billing for hours. That is the same field over-reporting in one
    direction (the 6.5-day orphan) and under-reporting in the other, and it is why 17 rows of the
    retrospective ledger read $0.01-$0.11 for rentals that were still running.

    `done_mtimes` maps label -> the epoch its result was written. Absent (or absent for this label) we cannot
    tell an old result from a new one, so we keep the old behaviour and finalize — the ledger must not stall
    forever just because a caller did not pass mtimes."""
    if label not in done_units:
        return False
    if not done_mtimes or label not in done_mtimes:
        return True
    try:
        return float(done_mtimes[label]) >= float(start_date)
    except (TypeError, ValueError):
        return True


def _ledger_row_key(label, instance_id):
    """The identity of a LEDGER ROW: one RENTAL, not one unit.

    ★★ KEYING ON THE UNIT MADE EVERY RE-RENTAL INVISIBLE, AND THE PANEL'S REALIZED SPEND DESCRIBED THE WRONG
    EXPERIMENT (measured 2026-07-31, 4:39 PM ET). This function's docstring says "a per-RENTAL measured-cost
    ledger" and the code wrote `ledger[label]`, so a unit contributed exactly ONE row for all time — and
    because `if prev.get("final"): continue` never rewrites a finalized row, that row was whichever rental
    happened to be live when the unit first landed a result.

    What that produced, from the ledger itself: all 18 rows `final: true`, `instance_id: null`,
    `observed_at: null` (they predate the provenance fields and were never touched again), uptimes of
    443-2304 s. Those are the SMOKE rentals. The production fan-out launched at 2:36 PM ET ran for hours
    across up to 13 concurrent hosts and contributed NOTHING, so `measured_total_so_far_usd` was a
    fully-populated, entirely plausible figure for a run nobody was asking about — CLAUDE.md §4b exactly: a
    field's presence is never evidence of its provenance.

    ⚠ LEGACY ROWS KEEP THEIR BARE-LABEL KEY. They have no `instance_id` to key on, and re-keying them would
    change the identity of rows already quoted and risk double-counting the same money under two keys. They
    stay as they are, are still summed, and are distinguishable by their null `instance_id`.
    """
    return "%s#%s" % (label, instance_id) if instance_id not in (None, "") else str(label)


def _ledger_row_unit(key, row=None):
    """Which UNIT a ledger row belongs to — from the row where present, else the key's label half."""
    u = (row or {}).get("unit")
    return u if u else str(key).split("#", 1)[0]


def _update_price_ledger(insts, done_units, bucket=None, path="nrv04-price-ledger.json",
                         result_prefix=None, n_units=None, done_mtimes=None):
    """Maintain a per-RENTAL measured-cost ledger ACROSS collect() polls (the deliverable = a MEASURED price).
    For each instance we see, record `now - start_date` x dph_total; once its result is in S3 we FREEZE that
    cost. The ledger is PERSISTED IN S3 (each collect runs on a fresh ephemeral runner, so a local file would
    reset every poll and only ever see one leg) -> frozen rentals accumulate into the panel mean + total.

    ⚠ A ROW IS RENTAL TIME, NOT LEG TIME — the block above `LEAK_ABOVE_S` is the one home for what that means
    and for the 2026-07-31 measurement behind it. Two consequences are implemented here rather than left to
    the reader, because leaving them to the reader is what went wrong:

      1. A row whose rental outlived any plausible leg is reported as a LEAK, not averaged into $/leg
         (`ledger_entry_reading`). One 6.5-day orphan dragged an 18-row mean to $1.4763/leg while the 17
         genuine rows were $0.01-$0.11 — a mean 20x the thing it claimed to measure.
      2. A cost is frozen only when the result was written by THIS rental (`_finalizable` + `done_mtimes`),
         so re-renting a unit that already had a result can no longer freeze the price at minutes while the
         host bills for hours.

    Each row also carries its PROVENANCE — instance id, start_date, the moment observed, the status seen —
    because reconstructing the orphan above needed CI logs that expire, and the ledger itself said nothing.

    Returns a summary: per-rental costs, measured mean $/leg over NON-leak rows, and the projected panel total."""
    import time
    # `retro_reap` already passes a {unit: newest_record_mtime} MAPPING (retro_record_units) — the same map
    # `teardown_candidates` uses to avoid reaping a fresh host for a stale record. Reuse it rather than
    # re-listing S3: one home for "when did this unit's result land".
    if done_mtimes is None and isinstance(done_units, dict):
        done_mtimes = done_units
    ledger = {}
    # Keyed on the CALLER's prefix so the retrospective's ledger cannot land in — or be read from — the
    # covalent panel's, which would mix two panels' per-leg costs into one mean.
    ledger_key = f"{result_prefix or RESULT_PREFIX}/{_PRICE_LEDGER_KEY_SUFFIX}"
    s3c = None
    def _unwrap(obj):                                          # the persisted doc is {"ledger":..., "summary":...}
        return obj.get("ledger", obj) if isinstance(obj, dict) else {}
    if bucket:
        try:
            import boto3
            s3c = boto3.client("s3")
            ledger = _unwrap(json.loads(s3c.get_object(Bucket=bucket, Key=ledger_key)["Body"].read().decode()))
        except Exception:  # noqa: BLE001 — first poll (no ledger yet) or transient
            ledger = {}
    if not ledger:                                             # fall back to a local file if S3 unavailable
        try:
            ledger = _unwrap(json.load(open(path)))
        except Exception:  # noqa: BLE001
            ledger = {}
    now = time.time()
    for i in insts:
        label = i.get("label")
        if not label:
            continue
        start_date = i.get("start_date")
        try:
            up_s = now - float(start_date or now)
        except (TypeError, ValueError):
            up_s = 0
        cost = leg_cost_usd(up_s, i.get("dph_total"))
        key = _ledger_row_key(label, i.get("id"))
        prev = ledger.get(key, {})
        if prev.get("final"):
            continue                                            # already finalized; don't overwrite
        ledger[key] = {"uptime_s": round(up_s), "dph_total": i.get("dph_total"),
                       "cost_usd": cost,
                       "final": _finalizable(label, done_units, start_date, done_mtimes),
                       # PROVENANCE. Without these, answering "which host was this, and when?" needs CI
                       # logs, which expire — exactly the dig the 2026-07-31 orphan required.
                       "instance_id": i.get("id"), "start_date": start_date,
                       "unit": label,
                       "observed_at": round(now),
                       "status": i.get("actual_status") or i.get("cur_state")}
    rows = {k: v for k, v in ledger.items() if v.get("final") and v.get("cost_usd") is not None}
    readings = {k: ledger_entry_reading(v) for k, v in rows.items()}
    # PER RENTAL (the row), then aggregated PER UNIT (what a reader means by "what did this leg cost").
    rental_legs = {k: v["cost_usd"] for k, v in rows.items() if readings[k]["kind"] == "leg"}
    leaks = {k: v["cost_usd"] for k, v in rows.items() if readings[k]["kind"] == "leak"}
    legs = {}
    for k, v in rental_legs.items():
        legs[_ledger_row_unit(k, rows[k])] = round(legs.get(_ledger_row_unit(k, rows[k]), 0.0) + v, 4)
    n_units = len(units_to_run()) if n_units is None else int(n_units)
    # The mean is over LEG rows only. A leak is real money — it stays in the total below and in
    # `leaked_usd` — but pricing a panel off a row that is 150x a leg projects a fantasy.
    mean = round(sum(legs.values()) / len(legs), 4) if legs else None
    summary = {
        "measured_legs": len(legs),
        "per_leg_usd": legs,
        "measured_mean_usd_per_leg": mean,
        # ⚠ RENTALS, NOT UNITS. `per_leg_usd` sums every rental a unit consumed; these say how many that was.
        # A unit re-placed six times costs six rentals, and until 2026-07-31 five of them were dropped on the
        # floor by a ledger keyed on the unit — see `_ledger_row_key`.
        "rentals_counted": len(rental_legs) + len(leaks),
        "per_rental_usd": rental_legs,
        "legacy_rows_without_instance_id": sorted(k for k in rows if "#" not in k),
        # Every frozen row, leaks included: this is money that left the account.
        "measured_total_so_far_usd": round(sum(rows[k]["cost_usd"] for k in rows), 4) if rows else 0.0,
        "leaked_usd": round(sum(leaks.values()), 4) if leaks else 0.0,
        "leaked_rentals": {k: {"usd": v, "why": readings[k]["why"]} for k, v in leaks.items()},
        "projected_panel_total_usd": round(mean * n_units, 2) if mean is not None else None,
        "panel_units": n_units,
        "uptime_s_means": "age of a LIVE rental at the moment a collect polled it — billed host time, NOT "
                          "the leg's compute time and NOT the rental's full lifetime (it is a lower bound "
                          "on that). See nrv04_vast_launch.LEAK_ABOVE_S.",
        # ⚠ A price is only a price for the PROTOCOL that ran. This ledger sees instances, not leg records,
        # so it cannot tell a 5 ns production leg from a 2 ps smoke — and on 2026-07-31 the retrospective's
        # 17 non-leak rows were ALL smoke (nrv04_retro_panel.production_leg_check). Anyone projecting a
        # panel cost off this mean must first check the mode, or they price 5 ns at the cost of 2 ps.
        "measured_mean_caveat": "over whatever legs ran, at whatever MODE. It is NOT protocol-aware — check "
                                "nrv04_retro_panel.production_leg_check before reading it as a production "
                                "$/leg.",
    }
    for k, v in sorted(leaks.items()):
        print(f"[price] ⚠ LEAK {k}: ${v} over {readings[k]['hours']:.1f} h — {readings[k]['why']}", flush=True)
    doc = {"ledger": ledger, "summary": summary}
    json.dump(doc, open(path, "w"), indent=2)
    if s3c is not None:                                        # persist so the next poll accumulates, not resets
        try:
            s3c.put_object(Bucket=bucket, Key=ledger_key, Body=json.dumps(doc).encode())
        except Exception as e:  # noqa: BLE001
            print(f"[price] WARN could not persist ledger to S3: {e}", flush=True)
    return summary


def diag():
    """Print the onstart log + the FULL status record of each running instance — the diagnostic for a stuck/slow
    Vast run. The status fields (status_msg, cur_state, intended_status, inet_down, image pull state) reveal
    whether a long 'loading' is an image pull on a slow host, a scheduler wait, or an error."""
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    # $DIAG_FILTER = an instance id or a label substring. Without it, diag dumps EVERY instance on the account
    # — including sibling sessions' — and the one you care about gets buried under output you cannot page
    # through (this is exactly what happened chasing the silent retro pilot on 2026-07-24).
    filt = (os.environ.get("DIAG_FILTER") or "").strip()
    if filt:
        insts = [i for i in insts
                 if filt == str(i.get("id")) or filt.lower() in (i.get("label") or "").lower()]
        print(f"[diag] filter={filt!r} -> {len(insts)} matching instance(s)", flush=True)
    print(f"[diag] {len(insts)} instance(s)", flush=True)
    # keys most informative about why an instance is stuck in 'loading'
    status_keys = ["id", "label", "actual_status", "cur_state", "intended_status", "status_msg", "gpu_name",
                   "cuda_max_good", "cuda_version", "driver_version", "inet_down", "reliability2", "start_date",
                   "image_uuid", "image_runtype", "cur_gpu_util", "cpu_util", "disk_util", "dlperf"]
    for i in insts:
        print(f"\n===== instance {i.get('id')} ({i.get('label')}) status={i.get('actual_status')} =====", flush=True)
        print("[diag] status: " + json.dumps({k: i.get(k) for k in status_keys}), flush=True)
        print(_vast_instance_logs(key, i.get("id")), flush=True)


# =============================================================================================================
# CI-SIDE TEARDOWN — the ONE decision function, and its label selector is a hard precondition
# =============================================================================================================
# ★★ CLAUDE.md §6: THE HOST CANNOT STOP ITS OWN BILLING — ONLY THE CONTROL PLANE CAN. The EXIT trap and
# `autoteardown.py` stop the JOB, not the METER, and a container that crash-loops never returns at all, so
# neither ever fires. The guarantee has to be a CI-side reap, where the API key lives.
#
# ⛔ AND A REAPER THAT DESTROYS THE WRONG BOX IS WORSE THAN ONE THAT IS LATE. Until 2026-07-31 `collect`
# listed `owner=me` — EVERY instance on an account that is shared across concurrent sessions — and applied its
# over-age backstop to all of them, so running the NR-V04 collect while another lane was billing would destroy
# that lane's hosts past a 240-min cap it never agreed to. `stop_all` already carries this warning in prose;
# the reaper did not carry it in code.
#
# So the selector is a PRECONDITION, not a filter: an empty or missing `label_prefix` returns NO candidates at
# all rather than falling back to "everything". Fail closed. The two lanes' namespaces are disjoint and neither
# prefixes the other (`nrv04_covalent_panel.LABEL_PREFIX` = "nrv04cov-",
# `nrv04_retro_panel.LABEL_PREFIX` = "nrv04retro-"), and both are DERIVED from the panel modules that mint the
# labels so a rename cannot leave a reaper matching a stale — or a sibling's — prefix.
_TERMINAL_STATES = ("exited", "offline", "stopped")


def teardown_candidates(insts, done_units, now, max_leg_s, label_prefix):
    """PURE: [(instance, why)] this lane may destroy. No API call, no clock read, no S3, so it is unit-tested.

    `done_units` may be a set of unit names, or a {unit: record_mtime_epoch} MAPPING. With the mapping, a host
    that started AFTER its unit's record was written is NOT `result-in-S3`: it is a deliberate re-run of a unit
    whose existing record does not count (a smoke, a blown-up leg), and reaping it on the strength of the very
    artifact it was launched to replace would make the re-run impossible. A bare set keeps the old behaviour.

    An instance is a candidate when, AND ONLY WHEN, its label is inside `label_prefix`'s namespace and one of:
      * `result-in-S3`      — its unit already has a leg_*.json written AFTER this host started, so the GPU
                              has nothing left to do;
      * `terminal-state`    — the container exited/died AND it is not merely OUTBID (an outbid interruptible box
                              looks identical to a dead one but its disk is intact and Vast resumes it, so
                              destroying it throws away a ~20-min image reload we never owed);
      * `duplicate-instance`— a second live instance under one label double-computes the leg and clobbers its
                              checkpoint; keep a `running` one, else the newest;
      * over-age            — the crashed/hung backstop.
    """
    prefix = (label_prefix or "").strip()
    if not prefix:
        return []                       # FAIL CLOSED — no selector means no authority, never "everything"
    mine = [i for i in insts if (i.get("label") or "").startswith(prefix)]
    by_label = {}
    for n, i in enumerate(mine):
        by_label.setdefault(i.get("label"), []).append((n, i))
    keep = set()
    for _lab, grp in by_label.items():
        keep.add(sorted(grp, key=lambda t: ((t[1].get("actual_status") != "running"),
                                            -(t[1].get("start_date") or 0)))[0][0])
    out = []
    for n, i in enumerate(mine):
        label = i.get("label")
        try:
            up_s = now - float(i.get("start_date") or now)
        except (TypeError, ValueError):
            up_s = 0
        done = label in (done_units or set())
        if done and isinstance(done_units, dict):
            try:                                     # a record older than the host is a record the host is
                started = float(i.get("start_date"))  # replacing, not one it produced
                done = float(done_units[label]) >= started
            except (TypeError, ValueError, KeyError):
                done = True                           # unknown timing -> keep the old, billing-safe answer
        terminal = (i.get("actual_status") or "") in _TERMINAL_STATES and not instance_outbid(i)
        extra = n not in keep
        over_age = up_s > max_leg_s
        if done:
            out.append((i, "result-in-S3"))
        elif terminal:
            out.append((i, "terminal-state"))
        elif extra:
            out.append((i, "duplicate-instance"))
        elif over_age:
            out.append((i, f"exceeded {int(max_leg_s // 60)}min (idle/crashed backstop)"))
    return out


def _reap(candidates, key, tag="collect"):
    """Destroy each candidate, throttled under Vast's ~3 req/s DELETE limit. Returns the ids destroyed."""
    import time
    stopped = []
    for n, (i, why) in enumerate(candidates):
        if n:
            time.sleep(0.5)
        try:
            _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
            stopped.append(i.get("id"))
            print(f"[{tag}] auto-stopped {i.get('id')} ({i.get('label')}) — {why}", flush=True)
        except Exception as e:  # noqa: BLE001 — don't let one failed DELETE abort the sweep
            print(f"[{tag}] WARN auto-stop {i.get('id')} failed: {e}", flush=True)
    return stopped


def collect(bucket, autostop=None, result_prefix=None, label_prefix=None, n_units=None):
    """Monitor the panel run: list MY Vast instances (confirm running / torn down — no idle bleed) and the leg
    JSONs already in the result prefix. Prints a status board so we can watch the pilot + fan-out from CI.
    AUTO-STOP (default on, AUTOSTOP=0 disables): destroys any instance whose unit already has a leg_*.json in S3
    — the CI-side anti-idle-GPU teardown, so the API key stays on the trusted CI runner, never on the untrusted
    community hosts. Returns (n_up, n_results) so a monitor loop can decide when the fleet has drained.

    `result_prefix` / `label_prefix` / `n_units` default to the COVALENT feasibility panel's. The retrospective
    passes its own — see `retro_reap`. Getting these two out of sync is not cosmetic: reading `done_units` from
    the covalent prefix while watching retro instances means a finished retro leg is NEVER seen as done and
    never reaped, which is precisely the state this lane was in before 2026-07-31."""
    import boto3
    from nrv04_covalent_panel import LABEL_PREFIX as _COV_LABEL_PREFIX
    autostop = (os.environ.get("AUTOSTOP", "1") == "1") if autostop is None else autostop
    result_prefix = result_prefix or RESULT_PREFIX
    label_prefix = label_prefix or _COV_LABEL_PREFIX
    key = os.environ.get("VAST_API_KEY")
    all_insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", []) if key else []
    # ⛔ SCOPE FIRST. Everything below — the board, the price ledger and the reaper — sees only this lane's
    # labels, so a concurrent session's hosts are neither reported as ours nor reachable by our teardown.
    insts = [i for i in all_insts if (i.get("label") or "").startswith(label_prefix)]
    if len(all_insts) != len(insts):
        print(f"[collect] {len(all_insts)} instance(s) on the account; {len(insts)} carry the {label_prefix!r} "
              f"label and are IN SCOPE. The rest belong to other lanes and are not touched.", flush=True)
    print(f"[collect] Vast instances up: {len(insts)}", flush=True)
    for i in insts:
        msg = (i.get("status_msg") or "").strip().replace("\n", " ")[-90:]
        print(f"[collect]   id={i.get('id')} status={i.get('actual_status')} label={i.get('label')} "
              f"dph=${i.get('dph_total')}/hr :: {msg}", flush=True)
    s3 = boto3.client("s3")
    phases = {}
    for pk in _s3_list(s3, bucket, f"{result_prefix}/", suffix="phase.txt"):
        unit = pk.split("/")[-2]
        phases[unit] = s3.get_object(Bucket=bucket, Key=pk)["Body"].read().decode().strip()
    keys = _s3_list(s3, bucket, f"{result_prefix}/", suffix=".json")
    done_units = {k.split("/")[-2] for k in keys if k.rsplit("/", 1)[-1].startswith("leg_")}
    results = []
    for k in keys:                                             # ONLY the completed leg_*.json are 'results';
        if not k.rsplit("/", 1)[-1].startswith("leg_"):        # skip in-progress ckpt_*.ckpt.json (huge per-frame
            continue                                           # arrays) so the collect output stays compact
        body = s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode()
        try:
            results.append(json.loads(body))
        except Exception:  # noqa: BLE001
            results.append({"key": k, "bytes": len(body)})
    # compact in-progress checkpoint summary (proves checkpointing + shows per-leg production progress + the
    # covalent-pull energies, WITHOUT dumping the giant per-frame arrays the checkpoint JSON carries)
    ckpt_progress = {}
    for ck in keys:
        if not ck.rsplit("/", 1)[-1].endswith(".ckpt.json"):
            continue
        unit = ck.split("/")[-2]
        if unit in done_units:                                 # leg already finished -> checkpoint is stale
            continue
        try:
            cj = json.loads(s3.get_object(Bucket=bucket, Key=ck)["Body"].read().decode())
        except Exception:  # noqa: BLE001
            continue
        dfr, frm = cj.get("done_frames"), cj.get("frames")
        wall, tns = cj.get("wall_accum"), cj.get("timed_ns_accum")
        nsday = round(tns / (wall / 86400.0), 1) if (wall and tns) else None
        ckpt_progress[unit] = {"done_frames": dfr, "frames": frm,
                               "pct": round(100.0 * dfr / frm, 1) if (dfr and frm) else None,
                               "ns_per_day": nsday, "pe_pre_min_kj": cj.get("e_pre"),
                               "pe_post_min_kj": cj.get("e_min")}
    stopped = []
    if autostop and key:                                       # CI-side anti-idle teardown (key stays on CI)
        import time
        # backstop: a real leg finishes well under this. (240 min: a 6 ns leg at the MEASURED ~44-61 ns/day =
        # ~2.3-2.6 h + ~20 min load ~= 155 min, so 240 leaves margin for a spot-wait; the earlier 100 was
        # PREMATURELY killing healthy legs — checkpoints made them recoverable but a re-dispatch was needed.
        # Do NOT drop this below ~180.)
        max_leg_s = int(os.environ.get("MAX_LEG_MIN", "240")) * 60
        stopped = _reap(teardown_candidates(insts, done_units, time.time(), max_leg_s, label_prefix), key)
    price = _update_price_ledger(insts, done_units, bucket=bucket,   # MEASURED per-leg $ ledger (S3-persisted)
                                 result_prefix=result_prefix, n_units=n_units)
    status = {
        "vast_instances": [{"id": i.get("id"), "status": i.get("actual_status"), "label": i.get("label"),
                            "is_bid": i.get("is_bid"), "dph_total": i.get("dph_total"),
                            "dph_base": i.get("dph_base"), "min_bid": i.get("min_bid"),
                            "gpu_name": i.get("gpu_name"), "start_date": i.get("start_date"),
                            "duration": i.get("duration")} for i in insts],
        "phases": phases, "auto_stopped": stopped, "ckpt_progress": ckpt_progress,
        "n_results": len(done_units), "results": results, "price": price,
    }
    json.dump(status, open("nrv04-collect-status.json", "w"), indent=2)
    print("[collect] " + json.dumps(status, indent=2), flush=True)
    if price.get("measured_mean_usd_per_leg") is not None:
        print(f"[price] MEASURED ${price['measured_mean_usd_per_leg']}/leg over {price['measured_legs']} leg(s) "
              f"-> projected panel ({price['panel_units']} units) ≈ ${price['projected_panel_total_usd']}", flush=True)
    # The chain split each leg's readouts were computed against — printed LAST, as a one-liner, because the
    # 2026-07-24 finding was that the panel described the Elongin C interface and its own output could not say
    # so. A number whose meaning depends on a chain assignment must show that assignment where it is read.
    for r in results:
        cs = r.get("chain_split")
        if cs is None:
            print(f"[chain-split] {r.get('leg_id')} s{r.get('seed')}: NOT RECORDED — leg predates the fix; its "
                  f"readouts cannot be confirmed to describe the intended interface", flush=True)
        else:
            print(f"[chain-split] {r.get('leg_id')} s{r.get('seed')}: target={cs.get('target')} "
                  f"e3={cs.get('e3')} explicit={cs.get('explicit')} target_lys_nz={cs.get('target_lys_nz')}",
                  flush=True)
    return len(insts), len(done_units)


def monitor(bucket):
    """One CI job babysits the whole fan-out: loop collect()+auto-stop every MONITOR_EVERY_S until every unit has
    a result (and its instance is torn down) or MONITOR_MAX_S elapses. Bounded so it can never run forever; the
    stop-hook's own timeout is the outer guard. Pure-ish (sleeps + collect)."""
    import time
    n_units = len(units_to_run())
    every = int(os.environ.get("MONITOR_EVERY_S", "60"))
    max_s = int(os.environ.get("MONITOR_MAX_S", "3000"))       # < the job's timeout-minutes
    waited = 0
    while True:
        n_up, n_done = collect(bucket)
        print(f"[monitor] {n_done}/{n_units} results, {n_up} instance(s) up, {waited}s elapsed", flush=True)
        if n_done >= n_units and n_up == 0:
            print("[monitor] fleet drained — all results in, no instances up.", flush=True)
            return
        if waited >= max_s:
            print(f"[monitor] max wait {max_s}s reached ({n_done}/{n_units} done, {n_up} up) — exiting; re-dispatch to continue.", flush=True)
            return
        time.sleep(every); waited += every


def stop_all():
    """Destroy MY Vast instances (stop the bleed). Prints each id it tears down.

    ⚠ $VAST_KILL (an instance id or a label substring) NARROWS this to matching instances, and you almost
    always want it: this account is shared across concurrent sessions, so an unfiltered sweep destroys OTHER
    sessions' live work — on 2026-07-24 a sibling session was mid-run on the protein-mutation FEP benchmark
    while this one needed to kill a single stuck retro leg. Unfiltered remains available for a genuine
    stop-everything, but it is the exception."""
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[stop] VAST_API_KEY not set")
    import time
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    sel = (os.environ.get("VAST_KILL") or "").strip()
    if sel:
        insts = [i for i in insts
                 if sel == str(i.get("id")) or sel.lower() in (i.get("label") or "").lower()]
        print(f"[stop] selector={sel!r} -> {len(insts)} matching instance(s)", flush=True)
    else:
        print("[stop] NO SELECTOR — destroying EVERY instance on this account, including other sessions'. "
              "Set VAST_KILL to narrow.", flush=True)
    print(f"[stop] {len(insts)} instance(s) to destroy", flush=True)
    failed = []
    for n, i in enumerate(insts):
        iid = i.get("id")
        if n:
            time.sleep(0.5)                                    # stay under Vast's ~3 req/s DELETE limit (the 429
        try:                                                   # retry in _vast_request is the backstop for this)
            _vast_request("DELETE", f"/instances/{iid}/", key)
            print(f"[stop] destroyed {iid} ({i.get('label')})", flush=True)
        except Exception as e:  # noqa: BLE001 — don't let one failed DELETE abort the whole sweep
            failed.append(iid); print(f"[stop] WARN destroy {iid} failed: {e}", flush=True)
    print(f"[stop] done ({len(insts) - len(failed)}/{len(insts)} destroyed"
          + (f", {len(failed)} FAILED: {failed}" if failed else "") + ")", flush=True)


def build_jobspec(leg, seed, mode, branch, bucket, env_tarball_url=None):
    """PURE: the JobSpec for one (leg, seed) unit. No I/O -> unit-tested. `env_tarball_url` (a presigned S3 GET
    for the pre-packed conda env) is injected when submitting; the pure unit tests omit it."""
    name = unit_name(leg, seed)
    env = leg_env(leg, seed, mode=mode)
    env.update({
        "GIT_BRANCH": branch,
        "COFOLD_PREFIX_S3": cofold_prefix_s3(leg, bucket),
        "RESULT_S3": f"s3://{bucket}/{RESULT_PREFIX}/{name}",
    })
    if env_tarball_url:
        env["ENV_TARBALL_URL"] = env_tarball_url
    pipeline = _PIPELINE.replace("{repo}", REPO)      # not .format(): the bash has literal {a,b} brace-expansion
    return JobSpec(
        name=name,
        command=["bash", "-lc", pipeline],
        image=VAST_IMAGE,
        checkpoint_uri=s3_checkpoint_uri(name, bucket=bucket),
        resume=True,
        # ⛔ the binding buy line travels WITH the spec — see `buy_ceiling_usd_per_ns`
        resources=endpoint_md_resources(max_usd_per_ns=buy_ceiling_usd_per_ns()),
        max_runtime_s=int(os.environ.get("MAX_RUNTIME_S", "43200")),
        env=env,
    )


def presign_env_tarball(bucket, expires_s=None):
    """Return a presigned S3 GET URL for the pre-packed conda MD env (so instances curl it without awscli, which
    lives inside the env). Fails loudly if the env hasn't been built yet (run the build_env CI job first)."""
    import boto3
    from botocore.exceptions import ClientError
    s3 = boto3.client("s3")
    try:
        head = s3.head_object(Bucket=bucket, Key=MDENV_KEY)
    except ClientError as e:
        raise SystemExit(f"[launch] pre-packed MD env s3://{bucket}/{MDENV_KEY} not found ({e}); "
                         f"run the build_env task first (task=nrv04_vast_launch, mode not needed — see workflow).")
    size_mb = head["ContentLength"] / 1e6
    ttl = expires_s or (int(os.environ.get("MAX_RUNTIME_S", "43200")) + 3600)
    url = s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": MDENV_KEY}, ExpiresIn=ttl)
    print(f"[launch] pre-packed MD env: s3://{bucket}/{MDENV_KEY} ({size_mb:.0f} MB), presigned {ttl}s", flush=True)
    return url


def units_to_run():
    """Pilot-one-leg-first: PILOT_ONLY=1 -> just cov_nr4a1 seed 0 (highest abort info: it's the primary covalent
    ternary model + the R4 sensitivity numerator). Else the full 18-unit fan-out."""
    if os.environ.get("PILOT_ONLY", "1") == "1":
        pilot = next(lg for lg in PANEL if lg.leg_id == "cov_nr4a1")
        return [(pilot, int(os.environ.get("PILOT_SEED", "0")))]   # PILOT_SEED distinguishes parallel bench runs
    return enumerate_units()


# A bench number is only usable if it survives all of these. Encoded as a function so the collector REJECTS bad
# legs instead of printing them next to good ones and leaving the reader to notice (2026-07-24: a 2-second
# window and a fallback-to-Quadro leg were both tabulated as if they ranked cards).
_BENCH_MIN_WALL_S = 30.0     # below this you measure clock ramp + launch overhead, not throughput
_BENCH_MAX_CV = 0.10         # block-to-block scatter above this means a contended/throttled host


def _bench_flags(d):
    """Reasons this bench row must NOT enter a card ranking. Empty list = usable. PURE."""
    flags = []
    if str(d.get("status")) not in ("OK", "SUSPECT"):
        return ["errored"]
    if str(d.get("healthy", "True")).lower() == "false":
        flags.append("unphysical")
    # WRONG-CARD CHECK, on the MARKETPLACE name when the leg recorded one (`market_gpu_name`, forwarded from
    # the rented offer). The CUDA device string is a different vocabulary from the model we request —
    # `rtxpro6000ws` never appears inside "NVIDIA RTX PRO 6000 Blackwell Workstation Edition" — so comparing
    # the request against `device` false-flags every card whose driver name is not a superstring of its
    # marketplace name, and would reject the very benches this exists to collect. Older legs carry no
    # `market_gpu_name`, so they keep the device comparison.
    req = str(d.get("gpu_requested") or d.get("gpu") or "").lower().replace(" ", "")
    mkt = str(d.get("market_gpu_name") or "").lower().replace(" ", "")
    got = mkt or _raw_device(d).lower().replace(" ", "")
    if req and got and got != "unknown" and req not in got:
        flags.append(f"wrong_card(got_{(d.get('market_gpu_name') or _raw_device(d)).replace(' ', '_')})")
    try:
        if float(d.get("wall_s") or 0) < _BENCH_MIN_WALL_S:
            flags.append("window_too_short")
    except (TypeError, ValueError):
        flags.append("no_wall_s")
    cv = d.get("cv")
    if cv is None:
        flags.append("no_replicate_spread")     # pre-2026-07-24 single-shot legs cannot show stability
    else:
        try:
            if float(cv) > _BENCH_MAX_CV:
                flags.append("unstable_cv")
        except (TypeError, ValueError):
            flags.append("bad_cv")
    return flags


def instance_outbid(inst):
    """True when an interruptible instance is PAUSED because someone outbid us — not because it died.

    WHY THIS MATTERS MORE THAN THE BID MULTIPLE (2026-07-25). Vast's own docs are explicit that losing the
    auction is a PAUSE, not a death: "Data preserved when paused but instance not functional. Resume
    automatically when priority returns." Our reaper, however, listed "stopped" in `_terminal` and DELETEd it —
    discarding a preserved disk and forcing a fresh ~6 GiB image pull on the re-rent. That self-inflicted
    ~20-minute reload is the entire evidential basis for bidding `floor x 1.9`: the 2026-07-23 note reads "a
    covalent leg sat at frame 100 for ~3 h, re-bought+reloading repeatedly." Re-bought. It never had to be.

    Discriminated on DATA, not on guessing what a status string means:
      * `is_bid` - only an interruptible rental can be outbid at all;
      * `actual_status == "exited"` - the container ran and left (job done, or self-terminate). Genuinely dead;
      * `intended_status == "running"` - WE still want it up, so a stopped state is the market's doing, not ours;
      * `min_bid > price` - the machine's clearing price has risen above our standing bid. This is the direct
        observation of being outbid and needs no inference at all.

    Unknown/missing price fields resolve to True (assume outbid, do not destroy) because destroying loses a
    preserved disk irreversibly while NOT destroying is caught by the over-age backstop a few minutes later.
    PURE."""
    if not inst.get("is_bid"):
        return False
    actual = str(inst.get("actual_status") or "").lower()
    if actual == "exited":
        return False                       # container exited on its own -> finished or self-terminated
    if actual not in ("stopped", "offline"):
        return False
    if str(inst.get("intended_status") or "running").lower() != "running":
        return False                       # we asked for it to stop; that is ours, not the market's
    try:
        return float(inst.get("min_bid")) > float(inst.get("price"))
    except (TypeError, ValueError):
        return True                        # unknown -> keep the disk; over-age still reaps it


def _raw_device(d):
    """Full CUDA device name, recovered from the stored raw BENCH_RESULT line.

    The launcher's kv parser splits on whitespace, so `device='Quadro RTX 8000'` was stored as `device='Quadro`.
    That truncation is why a leg that fell back to a Quadro was reported under the card we had REQUESTED. Parse
    the quoted value out of `_raw` so historical results are readable too; newer legs underscore the name at the
    source (`gpu_md_bench.py`) and need no repair."""
    dev = str(d.get("device") or "")
    raw = str(d.get("_raw") or "")
    m = re.search(r"device='([^']*)'", raw) or re.search(r"device=(\S+)", raw)
    if m:
        return m.group(1).replace("_", " ")
    return dev.strip("'") or "UNKNOWN"


def _s3_list(s3, bucket, prefix, suffix=None, limit=None):
    keys, tok = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            if suffix is None or o["Key"].endswith(suffix):
                keys.append(o["Key"])
        if limit and len(keys) >= limit:
            return keys[:limit]
        if not r.get("IsTruncated"):
            return keys
        tok = r["NextContinuationToken"]


# Every co-fold prefix that could supply a ternary starting structure. The covalent panel only ever needed
# NR4A1 (+ its two controls), but the RETROSPECTIVE holdout needs the PARALOGUE co-folds too, and those were
# written by the earlier descriptive/shakeout benchmark runs under their own prefixes. discover scans all of
# them so the retrospective's input inventory is read off S3, never assumed.
COFOLD_BASES = [b for b in (os.environ.get("NRV04_COFOLD_BASES") or
                            "nrv04-descriptive-v4,nrv04-covalent-cofold,nrv04-descriptive-v3,nrv04-ternary,nrv04-shakeout").split(",") if b]


def discover_cofold(bucket, base=None):
    """List every candidate co-fold prefix and report which *_model_0.cif exist (reuse existing structures, no
    regen). Also dumps the RAW prefix layout so we can see the actual subdir names if they differ from expected.

    `base` (or $NRV04_COFOLD_PREFIX) restricts the scan to one prefix; the default scans COFOLD_BASES so the
    retrospective's paralogue inputs (nr4a2/nr4a3), which live outside the covalent panel's prefix, are found."""
    import boto3
    bases = [base.rstrip("/")] if base else [b.rstrip("/") for b in COFOLD_BASES]
    s3 = boto3.client("s3")
    per_base, systems = {}, {}
    for b in bases:
        cifs = _s3_list(s3, bucket, b + "/", suffix="_model_0.cif")
        per_base[b] = {"total_model0_cifs": len(cifs),
                       "subdirs": sorted({k[len(b) + 1:].split("/")[0] for k in cifs}),
                       "raw_sample_keys": _s3_list(s3, bucket, b + "/", limit=15),
                       "cif_keys": cifs[:60]}
        for k in cifs:                                  # <base>/<system>/.../*_model_0.cif
            systems.setdefault(k[len(b) + 1:].split("/")[0], []).append(k)
    out = {"bucket": bucket, "bases": bases, "per_base": per_base,
           "per_system": {k: sorted(v) for k, v in sorted(systems.items())},
           "total_model0_cifs": sum(v["total_model0_cifs"] for v in per_base.values())}
    json.dump(out, open("nrv04-cofold-discovery.json", "w"), indent=2)
    print("[discover] " + json.dumps(out, indent=2), flush=True)
    return out


def probe_offers():
    """Evidence for 'can we get cheaper?': list the cheapest eligible Vast offers under several filter variants so
    we can see the true interruptible price floor and which constraint (reliability / cuda_max_good / GPU model) is
    binding. Read-only — no rent. Ranks by min_bid (the interruptible cost) and shows what our bid would be."""
    import copy
    from gpu_backend import (_vast_request, _vast_offer_query, _vast_bid_price, _vast_gpu_ram_gb)
    key = os.environ.get("VAST_API_KEY")
    res = TERNARY_RES

    def _mb(o):
        try:
            return float(o.get("min_bid") if o.get("min_bid") is not None else 1e9)
        except (TypeError, ValueError):
            return 1e9

    def run(q, label, topn=8, only_4090=False):
        offers = _vast_request("GET", "/search/asks/", key, params={"q": json.dumps(q)}).get("offers", [])
        offers = [o for o in offers if int(o.get("num_gpus", 1) or 1) == 1]
        if only_4090:
            offers = [o for o in offers if "4090" in str(o.get("gpu_name", ""))]
        offers.sort(key=_mb)
        print(f"\n=== {label}: {len(offers)} single-GPU offers ===", flush=True)
        for o in offers[:topn]:
            try:
                rel = float(o.get("reliability2") or 0)
            except (TypeError, ValueError):
                rel = 0.0
            print(f"  {str(o.get('gpu_name'))[:16]:16} min_bid=${_mb(o):.3f} base=${float(o.get('dph_base') or 0):.3f} "
                  f"OURBID=${_vast_bid_price(o)} cuda_max={o.get('cuda_max_good')} rel={rel:.2f} "
                  f"vram={_vast_gpu_ram_gb(o):.0f}GB dc={o.get('geolocation')}", flush=True)
        if offers:
            ch = offers[0]
            print(f"  -> cheapest here: {ch.get('gpu_name')} OURBID=${_vast_bid_price(ch)}/hr", flush=True)

    full = _vast_offer_query(res)
    run(full, "FULL query (verified, rel>=%.2f, cuda>=%.1f, vram>=%dGB)" % (res.min_reliability, res.min_cuda, res.min_vram_gb - 1))
    run(full, "FULL query, RTX 4090 only", only_4090=True)
    no_rel = copy.deepcopy(full); no_rel.pop("reliability2", None)
    run(no_rel, "drop reliability filter (see if cheap hosts are low-reliability)")
    no_cuda = copy.deepcopy(full); no_cuda.pop("cuda_max_good", None)
    run(no_cuda, "drop cuda_max_good filter (see the PTX-risky cheap hosts we exclude)")
    relaxed = copy.deepcopy(full); relaxed.pop("reliability2", None); relaxed.pop("cuda_max_good", None)
    run(relaxed, "drop BOTH reliability + cuda (absolute floor for 24GB single-GPU)")


# ---- throughput bench mode: run gpu_md_bench on a chosen Vast card to PRICE $/ns (3090-vs-4090 decision) ----
# Reuses the proven Vast submit + self-destroy EXIT trap (VastBackend._vast_onstart): each bench instance tears
# ITSELF down on exit by its own unique label, so it is safe alongside the live covalent panel (no stop_all).
# gpu_md_bench builds a self-contained TIP3P water box sized by BENCH_EDGE_NM (7.1nm≈36k atoms≈an RBFE complex
# leg; larger edges bracket the ternary ~100k and covalent ~466k systems) and prints one ns_per_day line.
_BENCH_PREFIX = os.environ.get("VAST_BENCH_PREFIX", "vast-bench-results")

_BENCH_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 || { apt-get update -q || true; apt-get install -y -q --no-install-recommends curl ca-certificates || true; }
if [ ! -x /opt/mamba/envs/md/bin/python ]; then
  mkdir -p /opt/mamba/envs/md
  curl -Ls "$ENV_TARBALL_URL" | tar xz -C /opt/mamba/envs/md
  /opt/mamba/envs/md/bin/conda-unpack || true
fi
export PATH=/opt/mamba/envs/md/bin:$PATH
PY=/opt/mamba/envs/md/bin/python
AWS=/opt/mamba/envs/md/bin/aws
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
export OPENMM_REQUIRE_CUDA=1
$PY autoteardown.py $PY gpu_md_bench.py 2>&1 | tee /tmp/bench.out || true
grep BENCH_RESULT /tmp/bench.out | tail -1 > /tmp/bench.line || true
$PY - <<'PYEOF'
import json, os
line = open("/tmp/bench.line").read().strip()
d = {}
for kv in line.split():
    if "=" in kv:
        k, v = kv.split("=", 1)
        d[k] = v
d["_raw"] = line
# The card we ASKED for. _select_cheapest_offer falls back to any capable card when the requested model is
# not offered, so this is NOT the card that ran — read `device` for that. Recording it as "gpu" made a
# fallback-to-Quadro leg get reported as an A10 (2026-07-24).
d["gpu_requested"] = os.environ.get("VAST_GPU_MODEL", "")
d["gpu"] = d["gpu_requested"]  # back-compat for already-written bench.json files
# THE MARKETPLACE NAME OF THE CARD WE ACTUALLY RENTED, forwarded by gpu_backend.submit from the offer. This
# is the string the throughput tables are keyed on (`vast_cost_model.card_of`), and it is the only field that
# can tie a measured ns/day back to the offer that produced it: `gpu_requested` is what we ASKED for and
# `device` is the CUDA driver's own spelling, which differs from both.
d["market_gpu_name"] = os.environ.get("VAST_OFFER_GPU_NAME", "")
d["edge_nm"] = os.environ.get("BENCH_EDGE_NM", "")
json.dump(d, open("/tmp/bench.json", "w"), indent=2)
PYEOF
$AWS s3 cp /tmp/bench.json "$RESULT_S3/bench.json" || true
$AWS s3 cp /tmp/bench.out "$RESULT_S3/bench.out" || true
"""


def build_bench_jobspec(tag, branch, bucket, env_tarball_url=None):
    """PURE: JobSpec for one throughput bench (one card × one system size). No staging, no checkpoint/resume —
    gpu_md_bench is seconds of compute; the instance self-destroys on exit."""
    gpu = os.environ.get("VAST_GPU_MODEL") or "rtx4090"
    env = {
        "GIT_BRANCH": branch,
        "RESULT_S3": f"s3://{bucket}/{_BENCH_PREFIX}/{tag}",
        "BENCH_EDGE_NM": os.environ.get("BENCH_EDGE_NM", "7.1"),
        "BENCH_STEPS": os.environ.get("BENCH_STEPS", "4000"),
        "BENCH_WARMUP": os.environ.get("BENCH_WARMUP", "1000"),
        "BENCH_TAG": tag,
        "VAST_GPU_MODEL": gpu,
    }
    if env_tarball_url:
        env["ENV_TARBALL_URL"] = env_tarball_url
    pipeline = _BENCH_PIPELINE.replace("{repo}", REPO)
    return JobSpec(
        name=tag,
        command=["bash", "-lc", pipeline],
        image=VAST_IMAGE,
        checkpoint_uri=f"s3://{bucket}/{_BENCH_PREFIX}/{tag}/ckpt",
        resume=False,
        # VRAM floor is overridable so a 16 GB card can be BENCHED. Default unchanged at 24. Without this the
        # RTX 4080 (16 GB) — currently the only live candidate that might beat the 4090 on $/ns — is silently
        # filtered out of its own benchmark, which is how a card decision gets made on a proxy forever.
        # ★ require_gpu=True: for a bench the card is the QUESTION, not a preference. Without it
        # `_select_cheapest_offer` hands back the best MEASURED offer first, so `BENCH_GRID=rtx5090:9.5`
        # would rent a 4090 and file its throughput under "rtx5090". An unavailable card must fail the
        # submit, not quietly measure something else.
        resources=ResourceSpec(gpu=gpu, require_gpu=True,
                               min_vram_gb=int(os.environ.get("BENCH_MIN_VRAM_GB", "24")),
                               vcpus=4, ram_gb=16, disk_gb=40, interruptible=True),
        max_runtime_s=int(os.environ.get("BENCH_MAX_RUNTIME_S", "2400")),
        env=env,
    )


def bench(bucket):
    """Submit throughput bench leg(s) to Vast. BENCH_GRID (comma-sep 'gpu:edge_nm' pairs, e.g.
    'rtx4090:9.5,rtx3090:9.5,rtx4090:16.5') submits the whole grid in ONE dispatch (avoids the workflow's
    concurrency group cancelling rapid single dispatches). Else a single (VAST_GPU_MODEL, BENCH_EDGE_NM) leg.
    Each leg self-destroys on exit; idempotent enough for a bench (a stale same-tag bench.json is overwritten)."""
    branch = os.environ.get("GIT_BRANCH", "claude/next-expansion-priorities-t64njy")
    dry = os.environ.get("DRY_RUN", "0") == "1"
    grid_env = (os.environ.get("BENCH_GRID") or "").strip()
    if grid_env:
        grid = []
        for pair in grid_env.split(","):
            pair = pair.strip()
            if not pair:
                continue
            gpu, _, edge = pair.partition(":")
            grid.append((gpu.strip() or "rtx4090", edge.strip() or "7.1"))
    else:
        grid = [(os.environ.get("VAST_GPU_MODEL") or "rtx4090", os.environ.get("BENCH_EDGE_NM", "7.1"))]
    be = get_backend("vast")
    env_url = None if dry else presign_env_tarball(bucket)
    handles = []
    # A REPEATED (gpu, edge) pair is a deliberate control — the same card on two different HOSTS, to measure
    # whether host-to-host variance swamps the card difference. It only works if the legs write to DIFFERENT S3
    # keys. On 2026-07-24 `rtx4090:9.5,rtx4090:9.5` produced one tag, so both legs wrote the same key and one
    # silently overwrote the other: the control returned a single number and could not answer the question it
    # was launched to answer. Suffix repeats so a duplicate is a real replicate.
    _seen = {}
    for gpu, edge_nm in grid:
        _k = (gpu, edge_nm)
        _seen[_k] = _seen.get(_k, 0) + 1
        _rep = "" if _seen[_k] == 1 else f"-r{_seen[_k]}"
        tag = f"bench-{gpu}-{edge_nm}nm{_rep}".replace(".", "p")
        # per-leg overrides consumed by build_bench_jobspec via env
        os.environ["VAST_GPU_MODEL"] = gpu
        os.environ["BENCH_EDGE_NM"] = edge_nm
        spec = build_bench_jobspec(tag, branch, bucket, env_tarball_url=env_url)
        if dry:
            print(f"[bench-dry] {spec.name}: gpu={gpu} edge={edge_nm}nm steps={spec.env['BENCH_STEPS']} "
                  f"-> {spec.env['RESULT_S3']}", flush=True)
            continue
        h = be.submit(spec)
        print(f"[bench-submit] {spec.name} -> instance {h.job_id} gpu={gpu} edge={edge_nm}nm "
              f"dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit": spec.name, "gpu": gpu, "edge_nm": edge_nm, "instance": h.job_id,
                        "dph": h.extra.get("dph")})
    if handles:
        json.dump(handles, open("nrv04-vast-bench-handles.json", "w"), indent=2)
    return 0


def bench_collect(bucket):
    """Read every vast-bench-results/*/bench.json + list live bench-* instances, and print a $/ns table
    (ns_per_day is stamped by gpu_md_bench; combine with the live per-card $/hr from probe_offers for $/ns)."""
    import boto3
    s3 = boto3.client("s3")
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", []) if key else []
    bench_up = [i for i in insts if (i.get("label") or "").startswith("bench-")]
    print(f"[bench-collect] live bench-* instances: {len(bench_up)} "
          f"(each self-destroys on exit; covalent panel untouched)", flush=True)
    for i in bench_up:
        print(f"[bench-collect]   id={i.get('id')} status={i.get('actual_status')} label={i.get('label')} "
              f"dph=${i.get('dph_total')}/hr", flush=True)
    rows = []
    done_tags = set()
    for k in _s3_list(s3, bucket, f"{_BENCH_PREFIX}/", suffix="bench.json"):
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())
        except Exception:  # noqa: BLE001
            continue
        rows.append(d)
        done_tags.add(d.get("tag") or k.split("/")[-2])
    print(f"[bench-collect] {len(rows)} bench result(s):", flush=True)
    for d in sorted(rows, key=lambda r: (str(r.get("gpu")), str(r.get("edge_nm")))):
        flags = _bench_flags(d)
        print(f"  requested={d.get('gpu_requested') or d.get('gpu')} edge={d.get('edge_nm')}nm "
              f"atoms={d.get('atoms')} ACTUAL_DEVICE={_raw_device(d)} platform={d.get('platform')} "
              f"ns_per_day={d.get('ns_per_day')} cv={d.get('cv')} status={d.get('status')} "
              f"{'USABLE' if not flags else 'REJECT:' + ','.join(flags)}", flush=True)
        # ALWAYS print the raw line, not just on failure. A leg that returns status=OK on the WRONG CARD is the
        # dangerous case — it produces a plausible ns/day that gets attributed to the card we asked for.
        print(f"    raw: {d.get('_raw')}", flush=True)
    # TARGETED anti-idle teardown, scoped to the bench-* label namespace (covalent panel NEVER touched, no
    # stop_all). Destroy ONLY: (a) terminal instances (a finished bench self-exits -> exited/stopped), or (b) an
    # over-age instance (stuck/crashed backstop). Do NOT key off "has a bench.json" — a STALE result from a prior
    # run of the same tag would otherwise kill a freshly-LOADING re-dispatch mid-boot (observed 2026-07-23).
    if os.environ.get("BENCH_NO_STOP") != "1" and key:
        import time
        now = time.time()
        max_age = int(os.environ.get("BENCH_MAX_AGE_MIN", "40")) * 60
        _terminal = ("exited", "offline", "stopped")
        for i in bench_up:
            lab = i.get("label") or ""
            try:
                age = now - float(i.get("start_date") or now)
            except (TypeError, ValueError):
                age = 0
            # An outbid interruptible box looks exactly like a dead one ("stopped"), but its disk is intact
            # and Vast resumes it automatically when our bid regains priority. Destroying it throws that away
            # and buys a ~20-min image reload we never owed. Over-age still reaps it, so this cannot leak.
            terminal = (i.get("actual_status") or "") in _terminal and not instance_outbid(i)
            if terminal or age > max_age:
                try:
                    _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
                    print(f"[bench-collect] destroyed {i.get('id')} ({lab}) — "
                          f"{'terminal' if terminal else f'over-age {int(age//60)}min'}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"[bench-collect] WARN destroy {i.get('id')} failed: {e}", flush=True)
    return 0


# ---- FIRM mode: run ONE real RBFE edge + ONE real ternary edge on the Vast RTX 4090 (OpenFE nr4a3fep image) to
# replace the ~1.7x alchemical-overhead ASSUMPTION with a MEASURED per-edge ns/day + confirm the pipelines launch
# on Vast. Both self-stage (RBFE: valA_bench_stage.py public TYK2 edge; ternary: ternary_pdb_stage.py from 8G1Q),
# so no S3 input dependency. The image bakes the rbfe env (openfe+ambertools+lomap/kartograf+gemmi+pdbfixer+awscli).
FEP_IMAGE = os.environ.get("FEP_IMAGE") or "docker.io/triskit23/nr4a3fep:latest"
_FIRM_PREFIX = os.environ.get("VAST_FIRM_PREFIX", "vast-firm-results")

_FIRM_PREAMBLE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 || { apt-get update -q||true; apt-get install -y -q --no-install-recommends curl ca-certificates||true; }
export PATH=/opt/mamba/envs/rbfe/bin:$PATH
# conda-pack relocation breaks OpenMM's compiled-in plugin dir -> OpenFE's internal getPlatformByName("CUDA")
# fails ("no registered Platform called CUDA"). Point OPENMM_PLUGIN_DIR at this env's plugins so auto-load works
# for BOTH our driver AND OpenFE's internal calls (verified root cause on the first firm run, 2026-07-23).
export OPENMM_PLUGIN_DIR=/opt/mamba/envs/rbfe/lib/plugins
# The rbfe conda env has no CA bundle for Python SSL, so ternary_pdb_stage.py's RCSB fetch fails with
# CERTIFICATE_VERIFY_FAILED -> empty ligands.sdf (root-caused on the first firm run, 2026-07-23). Point SSL at
# the system CA bundle the Dockerfile's apt `ca-certificates` installs.
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
PY=/opt/mamba/envs/rbfe/bin/python
AWS=/opt/mamba/envs/rbfe/bin/aws
command -v "$AWS" >/dev/null 2>&1 || AWS="$PY -m awscli"
$PY -c "import openfe,openmm;print('[firm] openfe',openfe.__version__,'plats',[openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])" || true
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
export IN=/tmp/fin OUT=/tmp/fout; mkdir -p "$IN" "$OUT"
"""

_FIRM_RBFE_BODY = r"""
mkdir -p "$IN/ligand" "$IN/receptor"
echo "[firm] staging public TYK2 edge (valA_bench_stage.py)"
VALA_NO_UPLOAD=1 VALA_WORKDIR=/tmp/valA $PY valA_bench_stage.py 2>&1 | tail -12 || true
cp /tmp/valA/staged/docked_nr4a3.sdf "$IN/ligand/" 2>/dev/null || echo "[firm] no docked sdf"
cp /tmp/valA/staged/nr4a3-opened.pdb "$IN/receptor/" 2>/dev/null || echo "[firm] no receptor pdb"
cp /tmp/valA/staged/valA_manifest.json "$IN/" 2>/dev/null || true
export T0=$(date +%s)
env MODE=splittest RBFE_TINY=0 N_WINDOWS="${N_WINDOWS:-12}" N_ITER="${N_ITER:-150}" OPENMM_REQUIRE_CUDA=1 \
    RECEPTOR=nr4a3 LEG=complex LIGAND_A=tyk2_ejm_31 LIGAND_B=tyk2_ejm_42 \
    INPUT_DIR="$IN" OUTPUT_DIR="$OUT" CKPT_DIR="$OUT" $PY nr4a3_rbfe.py 2>&1 | tee /tmp/firm.log || true
export T1=$(date +%s)
"""

_FIRM_TERNARY_BODY = r"""
export T0=$(date +%s)
LEG="${LEG_ID:-calib_hi_to_lo__ternary_vhl}"
# Do NOT re-implement the ternary recipe here — call the SHARED single-source-of-truth runner so the Vast lane
# and the GCP lane stay identical. RBFE_PROD_ITERS is short for a fast timing/cost probe (the NaN, if any, is in
# warmup, so a short production still exercises the full stability path).
{
  echo "[firm] running ternary leg via run_ternary_leg.sh (shared recipe — single source of truth)"
  IN="$IN" OUT="$OUT" LEG_ID="$LEG" SEED=0 PY="$PY" RBFE_PROD_ITERS="${N_ITER:-60}" bash run_ternary_leg.sh
} 2>&1 | tee /tmp/firm.log || true
export T1=$(date +%s)
"""

_FIRM_SUMMARY = r"""
export FIRM_KIND N_WINDOWS N_ITER
$PY - <<'PYEOF'
import json, os, glob
out = os.environ["OUT"]; kind = os.environ.get("FIRM_KIND", "?")
js = sorted(glob.glob(os.path.join(out, "**", "*.json"), recursive=True))
nsd = dg = leg = src = None
for p in js:
    try:
        d = json.load(open(p))
    except Exception:
        continue
    if not isinstance(d, dict):
        continue
    td = d.get("timing_diagnostics") or {}
    cand = td.get("ns_per_day") or d.get("ns_per_day")
    if cand:
        nsd, src, leg = cand, os.path.basename(p), d.get("leg")
        dg = d.get("dg_morph_kcal") or d.get("ddg_coop_kcal") or d.get("dg_kcal")
try:
    wall = int(os.environ.get("T1", "0")) - int(os.environ.get("T0", "0"))
except ValueError:
    wall = None
r = {"kind": kind, "ns_per_day": nsd, "leg": leg, "dg": dg, "result_json": src,
     "n_windows": os.environ.get("N_WINDOWS"), "n_iter": os.environ.get("N_ITER"),
     "wall_s": wall, "n_json": len(js), "status": "OK" if nsd is not None else "NORESULT"}
json.dump(r, open("/tmp/firm.json", "w"), indent=2)
print("FIRM_RESULT", json.dumps(r))
PYEOF
$AWS s3 cp /tmp/firm.json "$RESULT_S3/firm.json" || true
$AWS s3 cp /tmp/firm.log "$RESULT_S3/firm.log" || true
"""


def build_firm_jobspec(kind, branch, bucket):
    """JobSpec for one real firming leg on the OpenFE nr4a3fep image (RTX 4090). kind = rbfe | ternary."""
    body = _FIRM_RBFE_BODY if kind == "rbfe" else _FIRM_TERNARY_BODY
    pipeline = (_FIRM_PREAMBLE + body + _FIRM_SUMMARY).replace("{repo}", REPO)
    tag = f"firm-{kind}-rtx4090"
    env = {
        "GIT_BRANCH": branch,
        "RESULT_S3": f"s3://{bucket}/{_FIRM_PREFIX}/{tag}",
        "FIRM_KIND": kind,
        "N_WINDOWS": os.environ.get("N_WINDOWS") or "12",  # 12 for both: the proven GCP valB ternary default (16 NaN'd at window 5)
        # short production is enough for a stable ns/day (throughput is length-independent) and finishes fast.
        "N_ITER": os.environ.get("N_ITER") or ("60" if kind == "rbfe" else "60"),
        "LEG_ID": os.environ.get("LEG_ID", "calib_hi_to_lo__ternary_vhl"),
    }
    return JobSpec(
        name=tag,
        command=["bash", "-lc", pipeline],
        image=FEP_IMAGE,
        checkpoint_uri=f"s3://{bucket}/{_FIRM_PREFIX}/{tag}/ckpt",
        resume=False,
        resources=ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=60, interruptible=True),
        # a real 12-window HREX leg runs ~2h+ on one GPU; the old 90-min watchdog reaped it mid-run. 4h ceiling.
        max_runtime_s=int(os.environ.get("FIRM_MAX_RUNTIME_S", "86400")),
        env=env,
    )


def firm(bucket):
    """Launch one or more real firming legs (FIRM_KIND = rbfe | ternary | 'rbfe,ternary') on Vast RTX 4090."""
    branch = os.environ.get("GIT_BRANCH", "claude/next-expansion-priorities-t64njy")
    kinds = [k.strip() for k in (os.environ.get("FIRM_KIND") or "rbfe").split(",") if k.strip()]
    dry = os.environ.get("DRY_RUN", "0") == "1"
    be = get_backend("vast")
    handles = []
    for k in kinds:
        spec = build_firm_jobspec(k, branch, bucket)
        if dry:
            print(f"[firm-dry] {spec.name}: image={spec.image} gpu={spec.resources.gpu} "
                  f"N_WINDOWS={spec.env['N_WINDOWS']} N_ITER={spec.env['N_ITER']} -> {spec.env['RESULT_S3']}", flush=True)
            continue
        h = be.submit(spec)
        print(f"[firm-submit] {spec.name} -> instance {h.job_id} gpu=rtx4090 dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit": spec.name, "kind": k, "instance": h.job_id, "dph": h.extra.get("dph")})
    if handles:
        json.dump(handles, open("nrv04-vast-firm-handles.json", "w"), indent=2)
    return 0


def firm_collect(bucket):
    """Read vast-firm-results/*/firm.json (measured ns_per_day per real edge) + reap terminal/over-age firm-*
    instances (scoped to firm-* labels; covalent panel untouched)."""
    import boto3
    s3 = boto3.client("s3")
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", []) if key else []
    firm_up = [i for i in insts if (i.get("label") or "").startswith("firm-")]
    print(f"[firm-collect] live firm-* instances: {len(firm_up)}", flush=True)
    for i in firm_up:
        print(f"[firm-collect]   id={i.get('id')} status={i.get('actual_status')} label={i.get('label')} "
              f"dph=${i.get('dph_total')}/hr", flush=True)
    for k in _s3_list(s3, bucket, f"{_FIRM_PREFIX}/", suffix="firm.json"):
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())
        except Exception:  # noqa: BLE001
            continue
        print(f"  kind={d.get('kind')} ns_per_day={d.get('ns_per_day')} n_windows={d.get('n_windows')} "
              f"n_iter={d.get('n_iter')} wall_s={d.get('wall_s')} dg={d.get('dg')} status={d.get('status')} "
              f"(from {d.get('result_json')}, {d.get('n_json')} json)", flush=True)
        if d.get("status") != "OK":                          # root-cause: dump the run log from S3
            logkey = k.rsplit("/", 1)[0] + "/firm.log"
            try:
                log = s3.get_object(Bucket=bucket, Key=logkey)["Body"].read().decode(errors="replace")
                lines = log.splitlines()
                # surface the NaN/clash diagnostic lines specifically (they may be far above the tail), then a
                # longer tail — a warmup-λ-window NaN's offending-atom dump lives in these, not the last 60 lines.
                diag = [ln for ln in lines if any(t in ln.lower() for t in
                        ("nan", "clash", "offending", "state ", "diverg", "warmup iter", "equilibration iter",
                         "min pair", "force-bearing", "restrain"))]
                if diag:
                    print("    --- firm.log NaN/clash diagnostic lines ---\n"
                          + "\n".join(diag[-80:]) + "\n    --- end diag ---", flush=True)
                tail = "\n".join(lines[-120:])
                print(f"    --- firm.log tail ({logkey}) ---\n{tail}\n    --- end ---", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"    (no firm.log: {e})", flush=True)
    if os.environ.get("BENCH_NO_STOP") != "1" and key:
        import time
        now = time.time()
        max_age = int(os.environ.get("FIRM_MAX_AGE_MIN", "260")) * 60   # > a real ~2h HREX leg + boot; don't reap mid-run
        _terminal = ("exited", "offline", "stopped")
        # keep the NEWEST instance per label; older same-label instances are stale duplicates (an errored run that
        # lingered while a fresh re-dispatch started) -> reap. Also reap terminal + over-age. FIRM_STOP=1 reaps ALL
        # firm-* (explicit cleanup). Never touches non-firm labels.
        # FIRM_STOP=1 force-reaps firm-*; FIRM_STOP_KIND scopes it to one kind (e.g. 'ternary' -> firm-ternary-*
        # only, leaving firm-rbfe-* running). Never touches non-firm labels.
        force_all = os.environ.get("FIRM_STOP") == "1"
        stop_kind = (os.environ.get("FIRM_STOP_KIND") or "").strip()
        newest = {}
        for i in firm_up:
            lab = i.get("label")
            if lab not in newest or (i.get("start_date") or 0) > (newest[lab].get("start_date") or 0):
                newest[lab] = i
        keep = {id(v) for v in newest.values()}
        for i in firm_up:
            lab = i.get("label") or ""
            try:
                age = now - float(i.get("start_date") or now)
            except (TypeError, ValueError):
                age = 0
            forced = force_all and (not stop_kind or lab.startswith(f"firm-{stop_kind}-"))
            dup = id(i) not in keep
            if forced or dup or (i.get("actual_status") or "") in _terminal or age > max_age:
                try:
                    _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
                    why = "force" if forced else ("duplicate" if dup else "terminal/over-age")
                    print(f"[firm-collect] destroyed {i.get('id')} ({lab}) — {why}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"[firm-collect] WARN destroy {i.get('id')} failed: {e}", flush=True)
    return 0


# =============================================================================================================
# CO-FOLD lane on VAST — replaces the SageMaker gpu-ternary-aws path for Boltz-2 ternary predictions.
#
# WHY IT EXISTS. gpu-ternary-aws.yml was the repo's ONLY Boltz co-folding lane, so a co-fold need routed to
# SageMaker by default — which is how the 2026-07-24 v4 regeneration went to a provider nobody chose
# (research/compute/provider-deviation-2026-07-24.md). STRATEGY's GPU economics put production on Vast, so the
# capability has to exist there or the deviation just repeats the next time a co-fold is needed.
#
# It runs the SAME science entry point as the SageMaker lane — `nrv04_ternary.py --run` with the same env
# contract (TERNARY_SCRIPT / TERNARY_EXTRA_ARGS / SEEDS / OUTPUT_DIR) — so the two lanes cannot drift into
# predicting different things. What differs is only the provisioning: a torch base image + pip install instead
# of a SageMaker container, and an explicit background S3 sync instead of SageMaker's Continuous upload mode.
# =============================================================================================================
COFOLD_IMAGE = os.environ.get("COFOLD_IMAGE") or "pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime"
BOLTZ_SPEC = os.environ.get("BOLTZ_SPEC") or "boltz==2.2.1"      # PINNED, same as the SageMaker lane

_COFOLD_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -q >/dev/null 2>&1 || true
apt-get install -y -q --no-install-recommends git curl ca-certificates >/dev/null 2>&1 || true
pip install --quiet awscli $BOLTZ_SPEC cuequivariance-torch cuequivariance-ops-torch-cu12 || \
  { echo "[cofold] pip install FAILED"; exit 3; }
AWS=$(command -v aws || echo /opt/conda/bin/aws)
# Same reasoning as the MD lane: a mark that hides its own failure is worse than no mark. Preflight hard.
mark() { echo "$1 $(date -u +%FT%TZ)" | $AWS s3 cp - "$RESULT_S3/phase.txt" || echo "[mark] WARN could not write phase '$1' to $RESULT_S3"; }
echo "preflight $(date -u +%FT%TZ)" | $AWS s3 cp - "$RESULT_S3/phase.txt" || {
  echo "[preflight] FATAL cannot write to $RESULT_S3 — refusing to run an unmonitorable job"; exit 4; }
# Stream stdout to S3 so an OOM kill leaves a post-mortem. The 2026-07-24 shakeout was OOM-killed in diffusion
# and the only reason we know is that Vast happened to still hold the container log.
exec > >(tee -a /tmp/run.log) 2>&1
( while true; do $AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors >/dev/null 2>&1 || true; sleep 45; done ) &
LOGSYNC_PID=$!
mark deps-ready
nvidia-smi || true
free -g || true
# IDEMPOTENT: after an OOM kill Vast re-runs this script, and a surviving /tmp/repo made `git clone` fail
# outright ("destination path already exists") — so the restart died on setup instead of retrying the work.
rm -rf /tmp/repo
git clone -q https://github.com/trimcrae/Rare-cancers /tmp/repo
git -C /tmp/repo checkout -q "$GIT_BRANCH" || true
RESOLVED=$(git -C /tmp/repo rev-parse HEAD)
mark cloned
export OUTPUT_DIR=/tmp/cofold_out
mkdir -p "$OUTPUT_DIR"
# Provenance stamp mirroring the SageMaker lane, so predictions from either provider are equally auditable.
python - <<PYEOF
import json, os
json.dump({"provider": "vast", "git_branch": os.environ.get("GIT_BRANCH"),
           "resolved_commit": os.environ.get("RESOLVED") or "$RESOLVED",
           "boltz_spec": os.environ.get("BOLTZ_SPEC"), "output_prefix": os.environ.get("OUTPUT_PREFIX"),
           "ternary_script": os.environ.get("TERNARY_SCRIPT"),
           "extra_args": os.environ.get("TERNARY_EXTRA_ARGS"), "seeds": os.environ.get("SEEDS")},
          open(os.path.join(os.environ["OUTPUT_DIR"], "run_provenance.json"), "w"), indent=2)
PYEOF
# CONTINUOUS UPLOAD (standing rule): sync every 60 s in the background, so a preemption or timeout after
# prediction N still leaves predictions 1..N in S3 rather than losing the whole run.
( while true; do $AWS s3 sync "$OUTPUT_DIR" "$RESULT_S3/" --only-show-errors || true; sleep 60; done ) &
SYNC_PID=$!
mark predicting
cd /tmp/repo/research/modalities
set +e
python "$TERNARY_SCRIPT" --run $TERNARY_EXTRA_ARGS 2>&1 | tail -400
RC=$?
set -e
kill $SYNC_PID 2>/dev/null || true
kill $LOGSYNC_PID 2>/dev/null || true
$AWS s3 sync "$OUTPUT_DIR" "$RESULT_S3/" --only-show-errors || true
$AWS s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors || true
mark "done rc=$RC"
exit $RC
"""


def build_cofold_jobspec(branch, bucket, output_prefix, script="nrv04_ternary.py", extra_args="",
                         seeds="1,2,3"):
    """PURE: the JobSpec for one Vast co-fold run. No I/O -> unit-tested."""
    tag = f"cofold-{output_prefix}"
    env = {
        "GIT_BRANCH": branch,
        "RESULT_S3": f"s3://{bucket}/{output_prefix}",
        "OUTPUT_PREFIX": output_prefix,
        "TERNARY_SCRIPT": script,
        "TERNARY_EXTRA_ARGS": extra_args,
        "SEEDS": seeds,
        "BOLTZ_SPEC": BOLTZ_SPEC,
    }
    return JobSpec(
        name=tag,
        command=["bash", "-lc", _COFOLD_PIPELINE],
        image=COFOLD_IMAGE,
        checkpoint_uri=f"s3://{bucket}/{output_prefix}",
        # resume=False: Boltz predictions are idempotent per (system, seed) but the script does not skip
        # completed ones, so a restart re-predicts. The continuous sync is what makes a preemption cheap.
        resume=False,
        # ⚠ RAM RAISED 32 -> 64 GB (2026-07-24): the shakeout run reached MSAs + featurization and was then
        # OOM-KILLED in diffusion — the instance log's bare `Killed` is the kernel OOM killer. Boltz-2 on an
        # ~800-residue ternary is host-RAM-bound, not VRAM-bound.
        resources=ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=64, disk_gb=80,
                               interruptible=True),
        max_runtime_s=int(os.environ.get("COFOLD_MAX_RUNTIME_S", "21600")),
        env=env,
    )


def cofold(bucket):
    """Launch a Boltz co-fold run on Vast. OUTPUT_PREFIX must be a FRESH prefix — co-fold outputs are inputs to
    a preregistered panel, so overwriting one in place would silently change a panel's structures."""
    branch = os.environ.get("GIT_BRANCH", "claude/nr-v04-retrospective-testing-6ywxye")
    output_prefix = os.environ.get("COFOLD_OUTPUT_PREFIX", "")
    if not output_prefix:
        raise SystemExit("[cofold] set COFOLD_OUTPUT_PREFIX (a FRESH S3 prefix; never overwrite an existing "
                         "co-fold set — it is a preregistered panel's input)")
    spec = build_cofold_jobspec(branch, bucket,
                                output_prefix,
                                script=os.environ.get("TERNARY_SCRIPT", "nrv04_ternary.py"),
                                extra_args=os.environ.get("TERNARY_EXTRA_ARGS", ""),
                                seeds=os.environ.get("SEEDS", "1,2,3"))
    if os.environ.get("DRY_RUN", "0") == "1":
        print(f"[cofold-dry] {spec.name}: image={spec.image} gpu={spec.resources.gpu} "
              f"script={spec.env['TERNARY_SCRIPT']} args={spec.env['TERNARY_EXTRA_ARGS']!r} "
              f"seeds={spec.env['SEEDS']} -> {spec.env['RESULT_S3']}", flush=True)
        return 0
    import boto3
    s3 = boto3.client("s3")
    if _s3_list(s3, bucket, output_prefix.rstrip("/") + "/", limit=1):
        raise SystemExit(f"[cofold] {output_prefix} already has objects — refusing to write into an existing "
                         f"co-fold prefix. Use a fresh one.")
    be = get_backend("vast")
    h = be.submit(spec)
    print(f"[cofold-submit] {spec.name} -> instance {h.job_id} dph≈${h.extra.get('dph')}/hr "
          f"-> {spec.env['RESULT_S3']}", flush=True)
    json.dump([{"unit": spec.name, "instance": h.job_id, "prefix": output_prefix}],
              open("nrv04-cofold-handles.json", "w"), indent=2)
    return 0


# =============================================================================================================
# RETROSPECTIVE holdout lane (prereg: nr4a3-nrv04-retrospective-prereg.md)
#
# Same proven endpoint-MD machinery as the covalent feasibility panel — same image, same pre-packed conda env,
# same driver (nrv04_covalent_md.py is target-agnostic: it splits E3 from target by topology, so NR4A2/NR4A3
# need no engine change) — with exactly ONE difference that matters: the co-fold MODEL SEED is PINNED per leg
# instead of globbing a system directory. That is not a detail. The co-fold model is the unit of independence in
# the frozen statistics (prereg §4a), so a leg that silently picked a different model would corrupt the
# model-level means the verdict is computed from.
# =============================================================================================================
RETRO_RESULT_PREFIX = os.environ.get("NRV04_RETRO_RESULT_PREFIX") or "nrv04-retro-results"

_RETRO_PIPELINE = _PIPELINE.replace(
    "mark env-ready\n", "mark env-ready\n" + _RETRO_ATTEMPT_MARKER.strip() + "\n"
).replace(
    """$AWS s3 cp "$COFOLD_PREFIX_S3" /tmp/cofold/ --recursive --exclude '*' --include '*_model_0.cif'
export COFOLD_CIF=$(find /tmp/cofold -name '*_model_0.cif' | sort | head -1)
test -n "$COFOLD_CIF" || { echo "no co-fold CIF found under $COFOLD_PREFIX_S3"; exit 3; }
$PY -c "import os; from nrv04_covalent_panel import leg_by_id; from nrv04_ligands import LIGANDS; \\
from nrv04_covalent_assemble import assemble_leg; lg=leg_by_id(os.environ['LEG_ID']); \\
assemble_leg(os.environ['COFOLD_CIF'], lg, LIGANDS[lg.ligand], os.environ['INPUT_DIR'])\"""",
    """$AWS s3 cp "$COFOLD_PREFIX_S3" /tmp/cofold/ --recursive --exclude '*' --include '*_model_0.cif'
export COFOLD_CIF=$(find /tmp/cofold -name '*_model_0.cif' | sort | head -1)
test -n "$COFOLD_CIF" || { echo "no co-fold CIF found under $COFOLD_PREFIX_S3"; exit 3; }
# exactly ONE CIF must be under the pinned model prefix — two would mean the seed pin failed and the leg would
# silently start from an unknown model, corrupting the model-level statistics (prereg 4a). Fail, never guess.
test "$(find /tmp/cofold -name '*_model_0.cif' | wc -l)" = 1 || { echo "expected exactly 1 co-fold CIF under the pinned model prefix $COFOLD_PREFIX_S3"; exit 3; }
$PY -c "import os; from nrv04_ligands import LIGANDS; \\
from nrv04_covalent_assemble import assemble_unit; \\
assemble_unit(os.environ['COFOLD_CIF'], os.environ['LEG_ID'], LIGANDS[os.environ['LIGAND']], os.environ['INPUT_DIR'])\"""",
)

# A str.replace that stops matching is a SILENT no-op: the retrospective would fall back to the feasibility
# panel's leg_by_id staging, every retro leg would die on an unknown LEG_ID (or worse, glob an unpinned model),
# and nothing would say so. Fail at import instead — this is exactly the class of drift the shared-recipe rule
# exists to prevent.
if _RETRO_PIPELINE == _PIPELINE or "assemble_unit" not in _RETRO_PIPELINE:
    raise RuntimeError("nrv04_vast_launch: the retrospective staging patch no longer matches _PIPELINE — "
                       "re-sync _RETRO_PIPELINE with the covalent staging block before launching any leg")


def build_retro_jobspec(arm, model_seed, replica, mode, branch, bucket, env_tarball_url=None,
                        exclude=()):
    """PURE: the JobSpec for one retrospective unit (arm, co-fold model, MD replica). No I/O -> unit-tested."""
    import nrv04_retro_panel as retro
    name = retro.unit_name(arm, model_seed, replica)
    env = retro.leg_env(arm, model_seed, replica, mode=mode)
    env.update({
        "GIT_BRANCH": branch,
        "COFOLD_PREFIX_S3": retro.cofold_prefix_s3(arm, bucket, model_seed),
        "RESULT_S3": f"s3://{bucket}/{RETRO_RESULT_PREFIX}/{name}",
        # The breaker's evidence. The path is `leg_failure_breaker.count_attempts`' own glob, not a spelling
        # of ours — a marker written anywhere else is a marker that module cannot count.
        "ATTEMPT_S3": f"s3://{bucket}/{RETRO_RESULT_PREFIX}/legs/{name}/attempts",
    })
    if env_tarball_url:
        env["ENV_TARBALL_URL"] = env_tarball_url
    pipeline = _RETRO_PIPELINE.replace("{repo}", REPO)
    return JobSpec(
        name=name,
        command=["bash", "-lc", pipeline],
        image=VAST_IMAGE,
        checkpoint_uri=s3_checkpoint_uri(name, bucket=bucket),
        resume=True,
        # ⛔ the binding buy line travels WITH the spec — see `buy_ceiling_usd_per_ns`. Every rental this lane
        # makes (fan-out, resume, cold single unit) is refused above the approved $/ns at SELECTION, which is
        # what CLAUDE.md §6's "a relaunch is a new purchase" actually requires.
        resources=endpoint_md_resources(max_usd_per_ns=buy_ceiling_usd_per_ns(), exclude=exclude),
        max_runtime_s=int(os.environ.get("MAX_RUNTIME_S", "43200")),
        env=env,
    )


#: The prereg §7 pilot: `retro_noncov_nr4a2` m1 r0 — NOT an NR4A1 leg. Its one home, because
#: `retro_pilot_unit` and the tests both need it and a second copy is how a pilot silently moves arm.
RETRO_DEFAULT_PILOT = ("retro_noncov_nr4a2", 1, 0)


def retro_pilot_force(sel):
    """PURE: does this selector ask for an ALREADY-LANDED unit to be re-run? Returns (selector_without_flag, bool).

    Folded into the selector string rather than given its own `workflow_dispatch` input because
    `fusion-cpu-extras.yml` is AT GitHub's hard 25-input cap and a 26th 422s the entire workflow
    (`tests/test_workflow_input_cap.py`). Spelling: a leading `!` or a standalone `force` token —
    `!nr4a2 m1 r0` / `nr4a2 m1 r0 force`.

    Forcing only ever clears the *result-in-S3* skip. It NEVER clears the live-instance skip (two hosts sharing
    one checkpoint prefix is a race, not a re-run) and it deletes nothing: the re-run overwrites its own
    `leg_*.json` in place. To keep the old object byte-for-byte instead, point the lane at a fresh
    `NRV04_RETRO_RESULT_PREFIX` — that is the non-destructive path and the one to use when the landed result is
    evidence about something."""
    raw = (sel or "").strip()
    if not raw:
        return "", False
    force = raw.startswith("!")
    raw = raw.lstrip("!").strip()
    toks = raw.split()
    kept = [t for t in toks if t.lower() != "force"]
    return " ".join(kept), (force or len(kept) != len(toks))


def _parse_retro_pilot_selector(sel, units):
    """PURE: resolve a human-typed unit selector against the AUTHORIZED unit list. Returns (arm, model, replica).

    Accepted, because a selector nobody can type from memory is a selector nobody uses:
      `nrv04retro-retro_noncov_nr4a3-m2-r1` · `retro_noncov_nr4a3 m2 r1` · `nr4a3:m2:r1` · `nr4a3-2-1` · `nr4a3`
    (bare arm = that arm's first authorized unit). Separators `-`, `:`, `_`(only around m/r), whitespace and
    commas are equivalent; the `m`/`r` prefixes are optional but must not be reordered.

    ⛔ THE MEMBERSHIP CHECK IS THE POINT, NOT THE PARSING. It resolves against `units` — what
    `enumerate_units()` authorizes — never against `ARMS`. `arm_by_id` happily returns `retro_cov_nr4a1`, the
    arm AMENDMENT 3 RETIRED for being unbuildable and crash-looping on a live meter, and the epimer R3 arms
    that no GO covers. Before this function the pilot was `arm_by_id(os.environ["RETRO_PILOT_ARM"])` with no
    such check, so one env var could have rented a retired unit past the authorization. Refuse loudly instead.
    """
    raw, _forced = retro_pilot_force(sel)
    toks = [t for t in raw.replace(",", " ").replace(":", " ").replace("-", " ").split() if t]
    # `retro_noncov_nr4a3` survives the split intact (underscores are untouched); `nrv04retro` is a namespace
    # prefix, not a token, so drop it when someone pastes a whole Vast label.
    if toks and toks[0] == "nrv04retro":
        toks = toks[1:]
    if not toks:
        raise SystemExit("[retro-pilot] empty unit selector")

    def _num(tok, letter):
        t = tok.lower()
        t = t[1:] if t.startswith(letter) else t
        return int(t) if t.isdigit() else None

    head = toks[0].lower()
    cand = [(a, m, r) for a, m, r in units
            if head in (a.arm_id.lower(), a.target.lower(), a.cofold_system.lower())]
    if not cand:
        raise SystemExit(
            f"[retro-pilot] {raw!r} names no AUTHORIZED unit. Authorized arms: "
            f"{sorted({a.arm_id for a, _m, _r in units})} (or their targets). A retired/conditional arm is "
            f"deliberately unreachable from here — see nrv04_retro_panel.RETIRED_STAGES.")
    model = _num(toks[1], "m") if len(toks) > 1 else None
    replica = _num(toks[2], "r") if len(toks) > 2 else None
    if model is not None:
        cand = [c for c in cand if c[1] == model]
    if replica is not None:
        cand = [c for c in cand if c[2] == replica]
    if not cand:
        raise SystemExit(f"[retro-pilot] {raw!r} resolves to no authorized unit (model={model}, replica={replica}). "
                         f"Authorized model seeds/replicas come from nrv04_retro_panel, not from this string.")
    return cand[0]


def retro_pilot_unit(done=(), selector=None, arm_id=None, model=None, replica=None):
    """PURE: the ONE unit a `retro_pilot` dispatch runs, given the units that already have a result.

    ★★ WHY THIS IS NOT A CONSTANT (measured 2026-07-31, run 30633508333 + the 6:56 AM ET `md_mode=smoke`
    dispatch). The pilot was hardcoded to `retro_noncov_nr4a2` m1 r0 and that is the ONE unit of 18 that had
    already landed, so `retro_launch` printed `[skip] … result already in S3`, `to_rent=0`, rented nothing, and
    returned 0 — indistinguishable in the Actions list from a pilot that succeeded. A pilot pinned to a
    finished unit can never prove a pipeline, so the lane could not take §6's `smoke → one real leg → fleet`
    first step AT ALL, and the 17 remaining legs stayed unbuyable behind it. The fix is that the pilot is a
    SELECTION over unrun units, not a constant:

      1. an explicit selector (`RETRO_PILOT_UNIT`, or the legacy `RETRO_PILOT_ARM`/`_MODEL`/`_REPLICA`) wins —
         it is honoured even if that unit is already done, because "re-run exactly this one" is a real need;
      2. else the prereg §7 default, if it is still unrun;
      3. else the first unrun unit **of the default pilot's arm**, then the first unrun unit anywhere. The arm
         preference keeps prereg §7's intent (the pilot exercises a PARALOGUE — the staging path the assembler
         had never read) rather than silently falling back to the NR4A1 arm the prereg excluded.

    Returns None when every authorized unit already has a result — the caller says so instead of renting.
    """
    import nrv04_retro_panel as retro
    units = retro.enumerate_units()
    done = set(done or ())

    if selector:
        return _parse_retro_pilot_selector(selector, units)
    if arm_id or model is not None or replica is not None:
        # legacy triple; routed through the same membership check so it cannot reach a retired arm either
        parts = [arm_id or RETRO_DEFAULT_PILOT[0]]
        parts.append(f"m{RETRO_DEFAULT_PILOT[1] if model is None else model}")
        parts.append(f"r{RETRO_DEFAULT_PILOT[2] if replica is None else replica}")
        return _parse_retro_pilot_selector(" ".join(parts), units)

    d_arm, d_model, d_replica = RETRO_DEFAULT_PILOT
    unrun = [(a, m, r) for a, m, r in units if retro.unit_name(a, m, r) not in done]
    if not unrun:
        return None
    for a, m, r in unrun:
        if a.arm_id == d_arm and m == d_model and r == d_replica:
            return (a, m, r)
    for a, m, r in unrun:                                  # same arm as the prereg pilot -> still a paralogue
        if a.arm_id == d_arm:
            return (a, m, r)
    return unrun[0]


def retro_units_to_run(done=()):
    """Pilot-one-leg-first (prereg §7), else the whole authorized panel.

    `done` = unit names that must not be piloted again (results already in S3, or a live host). Passing it is
    what makes the pilot ADVANCE instead of skipping forever; `retro_launch` supplies it from the same two
    lookups it uses for `skip_done`/`skip_live`, so the pilot and the fan-out can never disagree about what
    has landed."""
    import nrv04_retro_panel as retro
    if os.environ.get("RETRO_PILOT_ONLY", "1") == "1":
        pick = retro_pilot_unit(
            done=done,
            selector=os.environ.get("RETRO_PILOT_UNIT"),
            arm_id=os.environ.get("RETRO_PILOT_ARM"),
            model=(int(os.environ["RETRO_PILOT_MODEL"]) if os.environ.get("RETRO_PILOT_MODEL") else None),
            replica=(int(os.environ["RETRO_PILOT_REPLICA"]) if os.environ.get("RETRO_PILOT_REPLICA") else None),
        )
        return [pick] if pick else []
    return retro.enumerate_units()


def _chain_role_census(pdb_path):
    """Per-chain residue counts from an assembled complex.pdb, in FILE ORDER (not sorted).

    This exists because the MD driver splits E3 from target POSITIONALLY — nrv04_covalent_md._topology_indices
    calls the LAST sorted protein chain the target — while the co-fold YAML builder (nrv04_ternary.run) writes
    `proteins = [("A", target_lbd)] + e3`, i.e. the target FIRST. If those two conventions disagree, every
    interface readout in the panel is silently computed against the wrong chain pair and nothing errors. So the
    census is measured from the real file rather than assumed."""
    counts, order = {}, []
    for line in open(pdb_path):
        if not line.startswith(("ATOM", "HETATM")):
            continue
        ch, resseq = line[21], line[22:27]
        key = (ch, resseq)
        if ch not in counts:
            counts[ch] = set()
            order.append(ch)
        counts[ch].add(key)
    return [{"chain": c, "residues": len(counts[c])} for c in order]


def retro_stage_test(bucket):
    """FREE CI de-risking: assemble a leg from a REAL NR4A2 and NR4A3 co-fold CIF and verify a complex.pdb +
    bond-order-correct ligand.sdf come out. The paralogue co-folds have only ever been read by the co-fold
    REPORTER, never by the MD assembler, so this is the one staging risk the retrospective carries. Proves it
    on a free runner before renting any GPU."""
    import boto3
    import nrv04_retro_panel as retro
    import nrv04_covalent_assemble as asm_mod
    from nrv04_covalent_assemble import assemble_unit
    s3 = boto3.client("s3")
    results = []
    for arm_id in ("retro_noncov_nr4a2", "retro_noncov_nr4a3", "retro_noncov_nr4a1"):
        arm = retro.arm_by_id(arm_id)
        prefix = retro.cofold_prefix_s3(arm, bucket, retro.COFOLD_MODEL_SEEDS[0]).replace(f"s3://{bucket}/", "")
        cifs = _s3_list(s3, bucket, prefix, suffix="_model_0.cif")
        if len(cifs) != 1:
            raise SystemExit(f"[retro-stage-test] expected exactly 1 co-fold CIF under {prefix}, found {len(cifs)}")
        local = f"/tmp/retro_cofold_{arm_id}.cif"
        s3.download_file(bucket, cifs[0], local)
        res = assemble_unit(local, arm_id, LIGANDS[arm.ligand], "/tmp/retro_staged")
        cpdb = os.path.join(res["out"], "complex.pdb")
        n_atom = sum(1 for line in open(cpdb) if line.startswith(("ATOM", "HETATM")))
        if n_atom < 500:
            raise SystemExit(f"[retro-stage-test] {arm_id}: complex.pdb too small ({n_atom}) — chain surgery failed")
        roles = _chain_role_census(cpdb)
        results.append({"arm": arm_id, "key": cifs[0], "ligand_atoms": res["ligand_atoms"],
                        "complex_atoms": n_atom, "chains": roles, "identified": res["chains"]})
        print(f"[retro-stage-test] {arm_id}: {res['ligand_atoms']} ligand atoms, {n_atom} complex atoms, "
              f"chains {roles}", flush=True)
    # the three arms must assemble to comparable systems — a paralogue that lost a chain would silently become a
    # different experiment, and the identical-protocol requirement (prereg 2c) would be violated invisibly.
    sizes = [r["complex_atoms"] for r in results]
    if max(sizes) > 1.25 * min(sizes):
        raise SystemExit(f"[retro-stage-test] arms differ in size by >25% {sizes} — not protocol-matched")
    ligs = {r["ligand_atoms"] for r in results}
    if len(ligs) != 1:
        raise SystemExit(f"[retro-stage-test] ligand atom counts differ across arms {ligs} — same ligand expected")

    # THE CHAIN-SPLIT CHECK. What must hold is that the IDENTIFIED split (nrv04_covalent_assemble.identify_chains,
    # written to chains.json and consumed by the driver) resolves the NR4A LBD as the degradation target.
    #
    # It must NOT be "does the legacy positional rule agree?" — that was this check's first form, and it is
    # exactly backwards: the positional rule ("target = last sorted protein chain") picks Elongin C in these
    # co-folds, which is the defect the identifier exists to replace. Requiring the two to agree would block
    # every correct assembly forever. The positional answer is still computed and REPORTED, because seeing what
    # the old rule would have said is how the historical readouts stay interpretable.
    split = []
    for r in results:
        chains = r["chains"]
        identified = r["identified"]
        positional = sorted(chains, key=lambda c: c["chain"])[-1]     # what _topology_indices WOULD have picked
        target_res = next(c["residues"] for c in chains if c["chain"] == identified["target_chain"])
        ok = target_res == asm_mod.NR4A_LBD_RESIDUES
        split.append({"arm": r["arm"], "identified_target": identified["target_chain"],
                      "identified_target_residues": target_res, "e3_roles": identified["e3_roles"],
                      "legacy_positional_would_pick": positional["chain"],
                      "legacy_was_wrong": positional["chain"] != identified["target_chain"], "ok": ok})
        print(f"[retro-stage-test] {r['arm']}: identified target={identified['target_chain']} "
              f"({target_res} res, expected {asm_mod.NR4A_LBD_RESIDUES}) e3={identified['e3_roles']}; "
              f"legacy positional rule would have picked {positional['chain']} -> {'OK' if ok else 'BAD'}",
              flush=True)
    json.dump({"results": results, "protocol_matched": True, "chain_split": split},
              open("nrv04-retro-stage-test.json", "w"), indent=2)
    if not all(s["ok"] for s in split):
        raise SystemExit("[retro-stage-test] the identified target chain is not the frozen NR4A LBD construct. "
                         "Refusing to launch.")
    if len({s["identified_target"] for s in split}) != 1:
        raise SystemExit("[retro-stage-test] arms resolved DIFFERENT target chains — not protocol-matched. "
                         "Refusing to launch.")
    print("RETRO-STAGE-TEST PASS — the assembler handles NR4A1/NR4A2/NR4A3 co-folds, the arms are matched, and "
          "the identified chain split resolves the NR4A LBD as the degradation target.", flush=True)
    return 0


RETRO_MARKET_READOUT = "nrv04-retro-market-hold.json"


def retro_market_gate(n_hosts, bucket=None, s3=None, offers=None, key=None, readout_path=None, price=True):
    """(hold, doc) — may this lane rent `n_hosts` right now? Reads the LIVE board unless `offers` is given.

    ⛔ `price=False` IS THE "NOTHING TO BUY" EVALUATION, AND IT EXISTS BECAUSE THIS SNAPSHOT HAD NEVER ONCE
    BEEN COMMITTED (measured 2026-07-31). `nrv04-retro-market-hold.json` was declared in three places — this
    module's `RETRO_MARKET_READOUT`, `fusion-cpu-extras.yml`'s artifact list, and
    `lane_staleness_watch.LANES`' `hold_artifact` — and `git cat-file -e origin/main:…` failed on it while
    all four other lanes' hold artifacts existed and were minutes old. Two independent causes, both read from
    the code rather than inferred:

      (a) The commit step staged only the board fragment and the merged board. This file appeared solely in
          the `actions/upload-artifact` list — an ephemeral run artifact, not a commit — so even the ticks
          that DID price the board (run 30653531960 printed `[retro-market] ✅ CLEAR`) never put it on main.
      (b) Worse, and this is the one that explains the ten silent declines: the gate's ONLY production call
          site is inside `retro_launch`, behind `if not dry and todo and RETRO_MARKET_GATE == "1"`, and
          `retro_supervise` RETURNS before calling `retro_launch` whenever `needed` is empty. On every one of
          the ticks that declined to re-place the pilot, the breaker had emptied `needed` — so the gate never
          ran and there was nothing to write. The visibility mechanism was structurally unreachable on
          exactly the code path where a decline needed explaining.

    So the snapshot is now written on EVERY tick, which is the ternary lane's contract: a file that only
    appears when the lane is buying cannot distinguish "the gate ran and was happy" from "the gate never
    ran". `price=False` records the evaluation WITHOUT reading the board, because there is no purchase to
    price — and says so in `reason` rather than emitting a hold nobody caused.

    ★★ CLAUDE.md §6, BOTH HALVES, and they are one decision here:
      * "A THIN, EXPENSIVE MARKET IS A REASON TO PAUSE, NOT TO PAY — gate every fleet launch on $/ns." Priced
        at `n_hosts`, because a fan-out of N buys the N CHEAPEST offers, not the single best one N times. The
        best offer on a 5-deep board says nothing about what the 18th rental costs.
      * "A RELAUNCH IS A NEW PURCHASE, so it faces the same ceiling" — which is why this runs on the pilot and
        on a 1-unit resume too, not only on the fan-out. Neither `relaunch_market_gate.EXEMPTIONS` case
        applies: nothing here restarts an instance we already hold, and the checkpoints are S3 objects with no
        lifecycle expiry (`relaunch_market_gate --durability-probe`).

    NOTHING IS REIMPLEMENTED (rule 1). `relaunch_market_gate.price_offers` delegates to the SAME
    `gpu_backend.rank_offers_by_usd_per_ns` the renting path calls, and `relaunch_market_gate.verdict` owns the
    comparison against the ladder basis, so a board this gate prices is a board the launcher would actually buy
    from and the two can never disagree.

    ⚠ THE SPEC HANDED HERE IS UNCAPPED ON PURPOSE (`ResourceSpec.max_usd_per_ns`): a gate must SEE the
    expensive offers in order to say how far above the line the board sits. The cap lives on the spec handed to
    `submit`, where it binds the offer actually bought — including on every fallback after a capacity refusal.
    The two are the same number by construction, `buy_ceiling_usd_per_ns()`.

    A HOLD IS NEVER SILENT (the failure mode §6 names as worse than the problem): the snapshot that caused it
    is written to `nrv04-retro-market-hold.json`, printed, and annotated with `::notice::`."""
    import relaunch_market_gate as rmg
    res = endpoint_md_resources()                 # UNCAPPED — see the docstring
    n_hosts = max(1, int(n_hosts))
    # ★★ THE TIER IS PART OF THE READOUT, BECAUSE A HOLD THAT DOES NOT NAME IT IS UNREADABLE. Carried from
    # the ternary gate's 2026-07-31 finding rather than re-derived: there, two boards were writing one
    # snapshot file — bid-tier ticks clearing at 1.13-1.54x interleaved with on-demand ticks holding at
    # 2.04-2.28x — and read from a distance that said "the market doubled". It had not; the UNINTERRUPTIBLE
    # tier is small and dear by construction and was simply the one being priced. This lane writes a single
    # snapshot path too (`RETRO_MARKET_READOUT`), so it can acquire the identical ambiguity the moment
    # anything here ever prices on-demand — and a property that only holds while a field happens to be
    # constant is not a property. Same principle as CLAUDE.md §1's "a row we are paying and a row the gate
    # refused must never render alike", one level up: two holds about DIFFERENT MARKETS must not either.
    tier = "bid (interruptible)" if res.interruptible else \
           "on-demand (UNINTERRUPTIBLE — small and dear by construction; NOT the market the ladder is " \
           "costed on)"
    doc = {"_what": "Whether the NR-V04 retrospective may rent %d host(s) right now, priced in $/ns." % n_hosts,
           "_rule": "CLAUDE.md §6 — a thin, expensive market is a reason to PAUSE, not to pay; and a relaunch "
                    "is a NEW PURCHASE, not a continuation.",
           "lane": "nrv04_retro", "n_hosts": n_hosts, "utc": rmg._utcnow(),
           "tier": tier, "interruptible": bool(res.interruptible),
           "buy_line_usd_per_ns": round(buy_ceiling_usd_per_ns(), 6)}
    if not price:
        doc.update({"priced": False, "hold": False, "best_usd_per_ns": None,
                    "basis_usd_per_ns": None, "ratio_vs_basis": None, "board_depth": None,
                    "offers_priced": [],
                    "reason": "NOT PRICED — no unit needed a host this tick, so there was no purchase to "
                              "price. This is an EVALUATION, not a hold: nothing was refused and nothing "
                              "was bought. Which units were skipped, and why, is in "
                              + RETRO_GATE_READOUT + "."})
        try:
            with open(readout_path or RETRO_MARKET_READOUT, "w") as fh:
                json.dump(doc, fh, indent=2)
                fh.write("\n")
        except OSError as e:
            print(f"[retro-market] readout not written: {e}", flush=True)
        print(f"[retro-market] — NOT PRICED this tick ({doc['reason'].split('.')[0]}). Tier that WOULD be "
              f"priced: {tier}.", flush=True)
        return False, doc
    if offers is None:
        try:
            from gpu_backend import _vast_offer_query
            api = key or os.environ.get("VAST_API_KEY")
            if not api:
                raise RuntimeError("no VAST_API_KEY — the board cannot be read")
            offers = (_vast_request("GET", "/search/asks/", api,
                                    params={"q": json.dumps(_vast_offer_query(res))}) or {}).get("offers", [])
        except Exception as e:  # noqa: BLE001 — an UNREADABLE market is not a cheap one. Refuse, and say why.
            offers, doc["board_error"] = None, f"{type(e).__name__}: {e}"
    if offers is None:
        best, depth, rows = None, {"offers_returned": 0, "qualifying": 0, "priceable": 0,
                                   "needed": n_hosts, "used_for_mean": 0}, []
    else:
        best, depth, rows = rmg.price_offers(offers, res, n_hosts=n_hosts)
    hold, ratio, basis, reason = rmg.verdict(best)
    if doc.get("board_error"):
        reason = (f"could not read the board ({doc['board_error']}) — an unreadable market is not a cheap one, "
                  f"and this gate exists precisely for the case where nobody is awake to check")
    # The tier rides on the hold SENTENCE, not only in a field — the sentence is what gets quoted into a
    # status report, and a ratio quoted with no tier is how "the on-demand tier is dear" became "the market
    # is at 2x basis" on the ternary lane. Only on a hold: a CLEAR verdict bought at this tier is not a
    # number anyone will misread, and appending it everywhere is noise that trains the eye to skip it.
    if hold:
        reason = "%s; priced on the %s tier%s" % (
            reason, "bid/interruptible" if res.interruptible else "ON-DEMAND/UNINTERRUPTIBLE",
            "" if res.interruptible else " — this is NOT a reading of the interruptible market the ladder "
                                         "is costed on")
    doc.update({"priced": True,
                "hold": hold, "reason": reason, "best_usd_per_ns": (round(best, 6) if best else None),
                "basis_usd_per_ns": round(basis, 6), "ratio_vs_basis": ratio,
                "board_depth": depth, "offers_priced": rows})
    try:
        with open(readout_path or RETRO_MARKET_READOUT, "w") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
    except OSError as e:
        print(f"[retro-market] readout not written: {e}", flush=True)
    if hold:
        print(f"[retro-market] ⛔ HELD ON PRICE — {reason}. NOTHING was rented, nothing was dropped, and every "
              f"checkpoint is untouched in S3; re-dispatch to re-check. Board: {json.dumps(depth)}", flush=True)
        print(f"::notice title=NR-V04 RETRO HELD ON PRICE::{n_hosts} host(s) refused — best achievable "
              f"{ratio}x the ladder basis against a buy line of ${doc['buy_line_usd_per_ns']}/ns. "
              f"Snapshot: {RETRO_MARKET_READOUT}.", flush=True)
    else:
        print(f"[retro-market] ✅ CLEAR — {reason}. Board: {json.dumps(depth)}", flush=True)
    return hold, doc


def retro_launch(bucket, authorize=True, only_units=None):
    """Launch retrospective units on Vast. Idempotent: skips units with a LANDED leg already in S3 or a live
    instance, so a re-dispatch RESUMES the killed/preempted ones without ever racing a checkpoint.

    ⛔ `only_units` IS THE HOLD, MADE BINDING (measured 2026-07-31, 1:54 PM ET — the tick BOUGHT a held leg).
    `retro_supervise` computes exactly which units it may re-place: authorised, hostless, unlanded, past the
    breaker. It then printed that list and handed control to this function, which RE-DERIVED its own list
    from the whole panel and knows nothing about the authorization record. So the readout said

        ⏸ 16 unit(s) NOT re-placed — they have never been authorised to launch, so they are HELD

    and eight seconds later the same job rented one of those sixteen
    (`nrv04retro-retro_noncov_nr4a2-m2-r0 -> instance 46424247`). A hold that prints without binding is worse
    than no hold: it reads as a guard doing its job while money goes out — CLAUDE.md §1's "a row we are
    paying and a row the gate refused must never render alike", arriving one level up.

    The defect was latent until today's breaker fix let supervision reach this call at all, which is exactly
    why the fix ships with it. `None` means "the caller has not scoped this" (an operator dispatch, whose
    scope is its own selector); an EMPTY set means "nothing may be bought" and is honoured as such, never
    read as "no filter".

    Gated on $/ns before anything is rented (`retro_market_gate`) and again per offer inside `submit` (the
    spec's `max_usd_per_ns`). RETRO_MARKET_GATE=0 disables the board-level gate for a deliberate, recorded
    exception; the per-offer ceiling on the spec is NOT disableable, because that is the one that binds.

    `authorize` is the ladder's consent, not a flag: an OPERATOR dispatch (True, the default) records the
    units it launches in `RETRO_AUTHORIZED_UNITS_KEY`, which is the ONLY thing `retro_supervise` is allowed to
    re-place later. Supervision passes False — it may heal what was authorised and may never authorise more."""
    import nrv04_retro_panel as retro
    branch = os.environ.get("GIT_BRANCH", "claude/nr-v04-retrospective-testing-6ywxye")
    mode = os.environ.get("MODE", "run")
    dry = os.environ.get("DRY_RUN", "0") == "1"

    # ⚠ ORDER MATTERS: what has already landed is looked up BEFORE the units are chosen, because the PILOT's
    # choice depends on it (`retro_pilot_unit`). Reversing these two — which is how this lane shipped — pins the
    # pilot to a unit that may already be finished, and every dispatch then skips it and rents nothing.
    skip_done, skip_live = set(), set()
    if not dry:
        vk = os.environ.get("VAST_API_KEY")
        try:
            live = _vast_request("GET", "/instances/", vk, params={"owner": "me"}).get("instances", [])
            _alive = ("running", "loading", "created", "scheduling", "starting")
            skip_live = {i.get("label") for i in live if i.get("label") and (i.get("actual_status") or "") in _alive}
        except Exception as e:  # noqa: BLE001
            print(f"[retro] WARN could not list live instances ({e}); not skipping any", flush=True)
        try:
            import boto3
            s3 = boto3.client("s3")
            # A unit is skippable only when it has a LANDED leg. A smoke record is not one — skipping on it is
            # how a "finished" panel came to be 18 legs of 0.002 ns (`retro.production_leg_check`).
            skip_done = retro_done_units(s3, bucket)
        except Exception as e:  # noqa: BLE001
            print(f"[retro] WARN could not list S3 results ({e}); not skipping any", flush=True)

    pilot_only = os.environ.get("RETRO_PILOT_ONLY", "1") == "1"
    _sel, _force = retro_pilot_force(os.environ.get("RETRO_PILOT_UNIT"))
    explicit = bool(_sel or os.environ.get("RETRO_PILOT_ARM") or os.environ.get("RETRO_PILOT_MODEL")
                    or os.environ.get("RETRO_PILOT_REPLICA"))

    units = retro_units_to_run(done=skip_done | skip_live)
    # ⛔ THE CALLER'S SCOPE BINDS HERE, BEFORE THE PILOT LOGIC, THE MARKET GATE AND EVERY SUBMIT — because
    # every one of those is downstream of "which units are we buying". `None` = unscoped; a set = exactly
    # these and nothing else, empty included. See the docstring for the rental this let through.
    if only_units is not None:
        allowed = set(only_units)
        dropped = [retro.unit_name(a, m, r) for a, m, r in units if retro.unit_name(a, m, r) not in allowed]
        units = [(a, m, r) for a, m, r in units if retro.unit_name(a, m, r) in allowed]
        if dropped:
            print(f"[retro] scoped to {len(units)} unit(s) by the caller; {len(dropped)} NOT bought this "
                  f"dispatch: {dropped[:6]}{'…' if len(dropped) > 6 else ''}. This is the caller's hold "
                  f"binding, not a market or breaker refusal — $0 was spent on them and nothing was dropped "
                  f"from the panel.", flush=True)
        if not units:
            print("[retro] caller scoped this dispatch to NO units — nothing rented, nothing changed.",
                  flush=True)
            return 0
    if pilot_only and explicit and _force:
        # A NAMED unit is being re-run on purpose. Clear only its result-skip; `skip_live` is untouched, so a
        # forced re-run can still never race a host that is already writing that checkpoint.
        for _a, _m, _r in units:
            skip_done.discard(retro.unit_name(_a, _m, _r))
        print(f"[retro] FORCE: {[retro.unit_name(a, m, r) for a, m, r in units]} will re-run even though a "
              f"result exists; its leg_*.json is OVERWRITTEN in place (nothing is deleted). Use a fresh "
              f"NRV04_RETRO_RESULT_PREFIX instead if the existing object must be preserved.", flush=True)
    if not units:
        # Only reachable in pilot mode with every authorized unit already landed. Say it — a pilot that finds
        # nothing left to pilot is the fan-out's cue, not a failure, and it must not read as one.
        print("[retro] pilot: every authorized unit already has a result in S3 — nothing to pilot. The next "
              "step is `retro_full` (idempotent) or `retro_collect`, not another pilot.", flush=True)
        return 0

    todo = [(a, m, r) for a, m, r in units
            if dry or (retro.unit_name(a, m, r) not in skip_done and retro.unit_name(a, m, r) not in skip_live)]
    if not dry and pilot_only and explicit and not todo:
        # The operator NAMED a unit and it was skipped. Returning 0 here is how this lane spent the morning
        # looking like a pilot that worked: green run, `to_rent=0`, no host, no leg. Fail instead.
        print(f"[retro] ⛔ the selected pilot unit(s) {[retro.unit_name(a, m, r) for a, m, r in units]} were "
              f"SKIPPED (result already in S3, or a live host holds the checkpoint) — nothing was rented. "
              f"Prefix `!` to the selector (or append ` force`) to re-run one that already has a result; a "
              f"live host is never overridden. Failing so this cannot read as a pilot that ran.", flush=True)
        return 1
    print(f"[retro] {len(units)} unit(s) [{', '.join(retro.unit_name(a, m, r) for a, m, r in units)[:200]}], "
          f"mode={mode}, dry_run={dry}, pilot_only="
          f"{os.environ.get('RETRO_PILOT_ONLY', '1')}, skip_done={len(skip_done)}, skip_live={len(skip_live)}, "
          f"to_rent={len(todo)}", flush=True)

    # ⛔ AUTHORIZATION IS RECORDED HERE, BEFORE THE MARKET GATE AND BEFORE ANY RENTAL — because it records the
    # LADDER'S CONSENT, not the purchase. An operator who dispatches these units has authorised them even if
    # tonight's board is too thin to buy them; that is precisely the case where the next supervision tick
    # SHOULD re-check and place them. Supervision itself never reaches this line (`authorize=False`).
    if authorize and not dry and todo:
        try:
            import boto3
            retro_authorize_units(boto3.client("s3"), bucket,
                                  [retro.unit_name(a, m, r) for a, m, r in todo], mode=mode)
        except Exception as e:  # noqa: BLE001
            print(f"[retro] WARN could not record authorization ({e}); supervision will treat these units as "
                  f"UNAUTHORIZED and will not re-place them if this dispatch's hosts die", flush=True)

    # ⛔ THE MARKET GATE, BEFORE A SINGLE PRESIGN OR SUBMIT. Priced at the number of hosts we are ABOUT TO RENT
    # (not the panel size), because that is the purchase being made. A hold rents nothing and drops nothing.
    if not dry and todo and os.environ.get("RETRO_MARKET_GATE", "1") == "1":
        hold, _gdoc = retro_market_gate(len(todo), bucket=bucket)
        if hold:
            print("[retro] launch HELD — see the snapshot above. The panel is unchanged and every checkpoint "
                  "is intact; re-dispatch when the board improves.", flush=True)
            return 0

    env_url = None if dry else presign_env_tarball(bucket)
    be = None if dry else get_backend("vast")
    handles, refused = [], []
    # ★★ THE WAVE REMEMBERS WHICH HOSTS JUST REFUSED IT — MEASURED 2026-07-31, 2:36 PM ET FAN-OUT.
    #
    # 11 of 16 units failed to place against a board of 89 PRICEABLE offers, which cannot be thinness. The
    # per-offer submit lines say why: 33 refusal events across only EIGHT distinct machines, and
    #     machine 29706 refused ALL 11 units · 33657 refused 8 · 34670 refused 6
    # — three dead hosts account for 25 of the 33. `gpu_backend.submit`'s refusal skip is scoped to ONE CALL,
    # so all 16 units independently start at the top of the SAME $/ns ranking, hit the SAME stale hosts, and
    # burn their whole `_VAST_START_REFUSAL_TRIES` budget on them. Unit 16 re-discovers what unit 1 learned.
    #
    # ⚠ THIS IS NOT A BLACKLIST, AND THE DISTINCTION IS THE ONE CLAUDE.md §6 DRAWS EXPLICITLY. That rule
    # retires the cross-lane, never-ageing, host-scoped set — "no evidence could ever retire an entry, so it
    # only ratcheted the board narrower" — while KEEPING two bounded forms: `used_machines`, which "dies with
    # the wave", and submit's in-call skip, which lasts "the remaining offers of that same call". What was
    # missing is exactly the middle of those two. This set is built from refusals THIS WAVE just measured,
    # is passed only to the specs this wave builds, and is discarded when `retro_launch` returns — it cannot
    # accumulate and cannot outlive the call, and re-learning a host costs one FREE failed submit next wave.
    wave_refused = set()
    for arm, model_seed, replica in units:
        name = retro.unit_name(arm, model_seed, replica)
        if not dry and name in skip_done:
            print(f"[skip] {name} — result already in S3", flush=True); continue
        if not dry and name in skip_live:
            print(f"[skip] {name} — live instance already running", flush=True); continue
        spec = build_retro_jobspec(arm, model_seed, replica, mode, branch, bucket, env_tarball_url=env_url,
                                   exclude=tuple(sorted(wave_refused)))
        if dry:
            print(f"[retro-dry] {spec.name}: gpu={spec.resources.gpu} cofold={spec.env['COFOLD_PREFIX_S3']} "
                  f"covalent={spec.env['COVALENT']} max_usd_per_ns={spec.resources.max_usd_per_ns} "
                  f"-> {spec.env['RESULT_S3']}", flush=True)
            continue
        try:
            h = be.submit(spec)
        except Exception as e:  # noqa: BLE001 — one unit must not abort the other 17
            # A per-offer ceiling refusal arrives here as "no offer qualifies". Name it as a REFUSAL rather
            # than an error: $0 was spent and the unit is untouched, which is the opposite of a failed launch.
            # WHAT THIS UNIT LEARNED, HANDED TO THE NEXT ONE. `CapacityRefusedAtStart` carries one row per
            # host that declined; without this the next unit re-tries the same dead hosts (29706 refused all
            # 11 units in the 2:36 PM ET wave). Bounded to this call — see `wave_refused` above.
            for _r in getattr(e, "refusals", ()) or ():
                _m = str((_r or {}).get("machine_id") or "").strip()
                if _m:
                    wave_refused.add(_m)
            refused.append(spec.name)
            print(f"[retro-submit] ⛔ {spec.name} NOT RENTED — {type(e).__name__}: {e}. If the board simply had "
                  f"nothing at or under ${spec.resources.max_usd_per_ns:.6f}/ns, this is the buy line doing its "
                  f"job: $0 spent, checkpoint intact, re-dispatch to retry.", flush=True)
            continue
        print(f"[retro-submit] {spec.name} -> instance {h.job_id} dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit": spec.name, "arm": arm.arm_id, "model": model_seed, "replica": replica,
                        "instance": h.job_id})
    if handles:
        json.dump(handles, open("nrv04-retro-handles.json", "w"), indent=2)
    if refused:
        print(f"::notice title=NR-V04 RETRO — {len(refused)} UNIT(S) NOT RENTED::{sorted(refused)}. Nothing was "
              f"spent on them and their checkpoints are intact.", flush=True)
    # ⛔ A LAUNCH THAT RENTED NOTHING MUST NOT REPORT SUCCESS. `todo` was non-empty and not one unit started, so
    # the run looks identical to a completed fan-out in the Actions list — the exact "holding silently" failure
    # CLAUDE.md §6 names as worse than the problem it solves. A PARTIAL launch is a real launch and stays green.
    if not dry and todo and not handles:
        print(f"[retro] ⛔ {len(todo)} unit(s) were due and NONE was rented. Failing the job so this cannot "
              f"read as a finished fan-out.", flush=True)
        return 1
    return 0


def retro_reap(bucket, autostop=None):
    """CI-side teardown for the RETROSPECTIVE lane. Returns (n_in_scope, stopped_ids).

    ⛔ THE TWO BUGS THIS EXISTS TO CLOSE, both measured in `nrv04_vast_launch` before 2026-07-31:
      1. `collect()` derived `done_units` from `RESULT_PREFIX` (the COVALENT panel's `nrv04-covalent-results`)
         while the retrospective writes to `RETRO_RESULT_PREFIX` (`nrv04-retro-results`). A finished retro leg
         was therefore never seen as done and never reaped — it billed until the 240-min backstop, or forever
         if the container crash-looped and kept resetting nothing.
      2. `collect()` had NO label selector, so running it while a sibling lane was billing destroyed that
         lane's hosts past a cap it never agreed to.
    Both are structural here: the prefix and the label namespace are passed together and the selector is a hard
    precondition of `teardown_candidates` (empty selector -> zero candidates, never "everything")."""
    import boto3
    import nrv04_retro_panel as retro
    autostop = (os.environ.get("AUTOSTOP", "1") == "1") if autostop is None else autostop
    key = os.environ.get("VAST_API_KEY")
    if not (autostop and key):
        print("[retro-reap] skipped (AUTOSTOP=0 or no VAST_API_KEY) — NOTE: with no control-plane reap the "
              "host cannot stop its own billing (CLAUDE.md §6).", flush=True)
        return 0, []
    import time
    all_insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    mine = [i for i in all_insts if (i.get("label") or "").startswith(retro.LABEL_PREFIX)]
    print(f"[retro-reap] {len(all_insts)} instance(s) on the account; {len(mine)} carry {retro.LABEL_PREFIX!r} "
          f"and are IN SCOPE. Other lanes are never touched.", flush=True)
    for i in mine:
        msg = (i.get("status_msg") or "").strip().replace("\n", " ")[-90:]
        print(f"[retro-reap]   id={i.get('id')} status={i.get('actual_status')} label={i.get('label')} "
              f"dph=${i.get('dph_total')}/hr :: {msg}", flush=True)
    s3 = boto3.client("s3")
    # ⛔ THE LOOSE SET, ON PURPOSE, AND ONLY HERE. Stopping the meter comes first: a box that wrote ANY record
    # is finished with its GPU whatever protocol it ran. The mtime map is what keeps that from also killing a
    # FRESH host launched to redo a unit whose record does not count — see `teardown_candidates`.
    done_units = retro_record_units(s3, bucket)
    max_leg_s = int(os.environ.get("MAX_LEG_MIN", "240")) * 60
    cands = teardown_candidates(mine, done_units, time.time(), max_leg_s, retro.LABEL_PREFIX)
    stopped = _reap(cands, key, tag="retro-reap")
    # The MEASURED per-leg $ ledger, keyed on THIS lane's prefix so it cannot mix with the covalent panel's.
    try:
        _update_price_ledger(mine, done_units, bucket=bucket, path="nrv04-retro-price-ledger.json",
                             result_prefix=RETRO_RESULT_PREFIX, n_units=len(retro.enumerate_units()))
    except Exception as e:  # noqa: BLE001 — a cost ledger must never break a teardown
        print(f"[retro-reap] WARN price ledger not updated: {e}", flush=True)
    return len(mine), stopped


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# SUPERVISION — the tick that keeps this lane running WITHOUT an agent watching it
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ WHAT WAS MISSING, MEASURED 2026-07-31. `fusion-cpu-extras.yml` is `workflow_dispatch`-only and is the
# ONLY workflow that runs this lane; the lane is absent from `lane_staleness_watch.LANES`; `vast_idle_guard`
# is invoked from `step1-fanout-supervisor.yml` and `gpu-ternary-fep-vast.yml` and never against the
# `nrv04retro-` namespace; and `retro_reap` destroyed a `stopped` host as `terminal-state` with no nudge and
# nothing to re-place it afterwards. So a preempted or capacity-refused leg simply stopped existing, silently,
# until a human dispatched `retro_full`. Sixteen legs behind that is the shape that stranded three of four
# 5a-KS legs the same morning.
#
# THE FOUR THINGS A TICK MUST DO, and the order is load-bearing:
#   1. NUDGE a `stopped` box we already hold back to `running` BEFORE condemning it — a fresh Vast create
#      settles back to `stopped` after provisioning (`gpu_backend.py` `_VAST_START` docstring), and
#      `relaunch_market_gate.EXEMPTIONS` correctly treats restarting a host we hold as NOT a new purchase.
#      Bounded, because an unbounded retry against a box that has refused IS waiting it out, which §6 forbids.
#   2. DESTROY what is provably not working — `vast_idle_guard.classify_idle`, whose inviolable rule (GPU
#      idleness NEVER condemns) is what stops it reaping a legitimately CPU-bound build phase.
#   3. RE-PLACE every unrun, hostless unit, behind the SAME buy line and market gate as any other rental.
#   4. REFUSE to re-place a unit that keeps failing, so step 3 cannot turn a build defect into unbounded
#      spend. That is `retro_breaker` below and it is not optional.
#
# NOTHING HERE IS A SECOND IMPLEMENTATION (rule 1): the threshold is `leg_failure_breaker.DEFAULT_THRESHOLD`,
# the attempt count is `leg_failure_breaker.count_attempts` over the layout that module already defines, the
# idle verdict is `vast_idle_guard.classify_idle`, the price test is `retro_market_gate` +
# `buy_ceiling_usd_per_ns`, and the rental is `retro_launch`'s own `build_retro_jobspec`.
RETRO_SUPERVISE_STATE_KEY = "_supervise_state.json"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ THE AUTHORIZATION RECORD — what separates "lost its host" from "never authorised to start yet"
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⛔ MEASURED 2026-07-31. The tick above re-placed EVERY unit that was neither done nor alive. That test cannot
# tell a preempted leg (re-place it: the work is authorised and half-paid-for) from a unit the ladder is
# deliberately HOLDING (do not touch it: nobody has agreed to buy it). trimcrae held the 16-leg fan-out pending
# the pilot clearing `build_system`; the first supervision tick at 10:04 AM ET re-placed all of them anyway,
# because "unrun and hostless" describes a held unit perfectly. §6's `smoke -> one real leg -> fleet` cannot
# survive a healer that treats "not started" as "needs restarting".
#
# THE FIX IS A DURABLE AUTHORIZATION RECORD, and the asymmetry is the whole point:
#   * a HUMAN dispatch (`retro_pilot` / `retro_full`) AUTHORIZES the units it launches and records them here;
#   * SUPERVISION may re-place ONLY units in that record. A unit outside it is `awaiting_authorization` — it
#     is printed and returned every tick (never held silently), and it is never bought.
# Fail-closed by construction: an empty/absent record means supervision buys NOTHING, which is the correct
# default for a lane whose fan-out has not been authorised.
RETRO_AUTHORIZED_UNITS_KEY = "_authorized_units.json"


def retro_leg_records(s3, bucket):
    """[(unit, key, record, last_modified_epoch)] for every `leg_*.json` under this lane's prefix.

    ONE walk, ONE spelling of "a leg record lives here" — the launcher's skip-set, the supervisor's done-set
    and the reaper all used to open-code `startswith("leg_")` against a raw key list, which is how three call
    sites came to disagree about what "done" means."""
    out = []
    for k in _s3_list(s3, bucket, f"{RETRO_RESULT_PREFIX}/", suffix=".json"):
        if not k.rsplit("/", 1)[-1].startswith("leg_"):
            continue
        try:
            o = s3.get_object(Bucket=bucket, Key=k)
            rec = json.loads(o["Body"].read().decode())
            mt = o["LastModified"].timestamp()
        except Exception as e:  # noqa: BLE001 — unreadable is UNKNOWN, never "conforming"
            print(f"[retro-legs] WARN unreadable {k}: {e}", flush=True)
            continue
        out.append((k.split("/")[-2], k, rec, mt))
    return out


def retro_done_units(s3, bucket, records=None):
    """Units with a LANDED leg — i.e. one that passes `nrv04_retro_panel.production_leg_check`.

    ⛔ NOT "a leg_*.json exists". That looser test is what let 18 smoke records complete the panel; see the
    predicate's docstring for the measurement. A unit whose only record is a smoke is UNRUN, and this function
    is what says so to the launcher's skip-set and the supervisor's re-placer alike."""
    import nrv04_retro_panel as retro
    recs = retro_leg_records(s3, bucket) if records is None else records
    return {u for u, _k, rec, _mt in recs if retro.is_production_leg(rec)}


def retro_record_units(s3, bucket, records=None):
    """Units with ANY leg record, conforming or not, plus the newest record mtime per unit.

    Deliberately the LOOSE test, and only the REAPER uses it: a box that wrote a record has nothing left to do
    and must stop billing whatever protocol it ran (CLAUDE.md §6 — only the control plane can stop the meter).
    The mtime is what keeps that from reaping a FRESH host for the same unit: see `teardown_candidates`."""
    recs = retro_leg_records(s3, bucket) if records is None else records
    at = {}
    for u, _k, _rec, mt in recs:
        at[u] = max(at.get(u, 0.0), mt)
    return at


#: A minimized explicit-solvent system of this size is always strongly negative (the working legs sit near
#: -4e6 to -5.7e6 kJ/mol). A POSITIVE post-minimization potential energy is not a slow leg or a bad host —
#: it is atoms on top of each other, and no host can fix it. Zero is the physical boundary, not a tuned cut.
_NONPHYSICAL_PE_KJ = 0.0


def retro_input_quarantine(rec):
    """(quarantined, why) — is this unit's INPUT broken in a way no further rental can fix? PURE.

    ★★ ROOT-CAUSED 2026-07-31, 3:38 PM ET, on `nrv04retro-retro_noncov_nr4a3-m3-r0` — five hours of hosts,
    md-running every time, never one banked frame, while 16 siblings on the same image and the same lane
    banked fine. The discriminating observation is the potential energy, and it is unambiguous:

        FAILING  nr4a3 m3 r0  (co-fold .../nr4a3/seed_3)
          PE pre-min = +2.109e+15   post-min = +2.207e+15 kJ/mol
          openmm.OpenMMException: Particle coordinate is NaN.
          blew_up=true  blow_phase="prod@frame0/5"  n_frames=0  prod_wall_s=4.4

        WORKING  nr4a3 m1 r0  (co-fold .../nr4a3/seed_1), same image, same code, same lane
          PE pre-min = -4.025e+06  post-min = -5.667e+06 kJ/mol
          blew_up=false  n_frames=5

    +2e15 kJ/mol is ~21 orders of magnitude above physical and it is present BEFORE minimization, so it is a
    property of the BUILT SYSTEM inherited from the co-fold: atoms overlapping badly enough that the
    Lennard-Jones term diverges. Minimization cannot escape it (post-min is no better than pre-min), and the
    first integration step therefore yields NaN coordinates — which is exactly `prod@frame0`, in 4.4 s, every
    time. BOTH replicas drawing on `nr4a3/seed_3` (`m3-r0` and `m3-r1`) show it; every other model does not.
    So the fault is the seed-3 co-folded structure, and buying a fourth host tests nothing.

    ⚠ DELIBERATELY NARROW — ALL THREE CONDITIONS. A leg that blows up LATER (a transient at frame 300, a bad
    host, a preemption mid-write) must stay eligible: `leg_failure_breaker.__doc__`'s "one failure is noise"
    applies to those and this predicate must not swallow them. Only the conjunction — it blew up, it blew up
    at the FIRST production step, and its minimized energy is non-physical — identifies a static property of
    the input rather than an event during the run.

    ⚠ AND IT IS DERIVED FROM THE ARTIFACT, NOT A HAND-TYPED UNIT LIST. A list would need a human to retire an
    entry, which is the exact defect CLAUDE.md §6 retired the machine blacklist over. This releases itself:
    regenerate the co-fold, and the next leg record has no such signature, so the unit is eligible again with
    no edit anywhere.
    """
    if not (rec or {}).get("blew_up"):
        return False, ""
    phase = str((rec or {}).get("blow_phase") or "")
    if not phase.startswith("prod@frame0"):
        return False, ""
    pe = (rec or {}).get("pe_post_min_kj")
    if pe is None or float(pe) <= _NONPHYSICAL_PE_KJ:
        return False, ""
    return True, (
        "INPUT QUARANTINE — this unit's built system is non-physical, so no host can run it. It blew up at "
        "%s with a post-minimization potential energy of %+.3e kJ/mol; a minimized explicit-solvent system "
        "is always strongly negative (working legs on this lane sit near -5e6). MEASURED CAUSE (not inferred): "
        "the co-fold nr4a3/seed_3 places A:GLU13:O and A:LYS181:NZ 0.181 A apart — two heavy atoms on the same "
        "point, both positioned by Boltz. The staged single-point probe finds NonbondedForce carrying "
        "+2.109e15 kJ/mol already at `protein_after_pdbfixer`, before the ligand exists and before one water "
        "is placed, so ligand placement and addSolvent are excluded (nrv04_pe_stage_probe, 2026-07-31). "
        "Renting another host reproduces it in seconds and tests nothing. RELEASE: a different co-fold for "
        "this unit — the quarantine is read from the leg record, so a clean record clears it with no edit. "
        "⚠ THAT IS A PREREGISTRATION QUESTION, NOT A CODE FIX: the input, not the pipeline, is what would "
        "change." % (phase, float(pe)))


def retro_committed_at(s3, bucket, unit):
    """When this unit last BANKED PRODUCTION WORK: the mtime of its newest production checkpoint. None if it
    has never committed one, or on a read error (unreadable is UNKNOWN, never "it committed").

    ★★ THIS IS `KIND_COMMIT` FOR THIS LANE, AND OMITTING IT DEADLOCKED A LEG THAT WAS 40 % DONE
    (measured 2026-07-31, 3:17 PM ET — my own defect, one level in from the one it replaced).

    The first version of `retro_streak_since_utc` anchored the streak at the unit's newest LEG RECORD. For
    `nrv04retro-retro_noncov_nr4a3-m1-r0` that record is the SMOKE leg written at 10:53 AM ET, and the board
    read:

        40.0% · NO HOST · THIS TICK: BLOCKED by the failure breaker — blocked: repeated failure on
        distinct hosts. Counted since this unit's last completed leg record (2026-07-31T14:53:10Z).

    A unit that is 40 % through production has by definition not completed a leg record and never will while
    it is refused a host, so that anchor can never advance and the block is permanent. I replaced an
    un-advanceable COUNTER with an un-advanceable ANCHOR — the identical shape, and exactly what
    `leg_failure_breaker.__doc__` already records for the ternary leg blocked at 88 % done with
    `n_attempts=55`.

    ⚠ AND THE FIX IS NOT A HIGHER THRESHOLD, which only delays the same deadlock by three rentals. The
    honest question is `leg_failure_breaker`'s own: **is the failure still the NEWEST fact about this unit?**
    A production checkpoint written after an attempt started proves that attempt BANKED WORK, which is
    superseding evidence in precisely the sense `KIND_COMMIT` means.

    WHY THIS OBJECT AND NOT ANOTHER. `nrv04_covalent_md._save_ckpt` writes `ckpt_<leg>_s<seed>.ckpt.json`
    (with the portable `.state.xml`) every `CKPT_EVERY_FRAMES` frames and mirrors it to S3, and
    `_load_resume` only accepts it when `phase == "production"` and `0 < done_frames < frames`. So its
    existence means real production frames are banked and resumable — it cannot be produced by a leg that
    died in staging or build, and `_rm_ckpt` deletes it when the leg FINISHES, so it never lingers to
    forgive a later failure. That is the opposite of the three candidates `leg_failure_breaker.__doc__`
    rejects (`phase.txt`, `run.log` mtime, a bare `committed > 0`), each of which is renewed by an attempt on
    its way IN and so would forgive a crash-loop forever.

    SELF-LIMITING, unchanged: superseding evidence buys one more rental. If that rental banks nothing, the
    checkpoint stops moving, the streak grows from the same stamp, and the block re-applies at the same count.
    """
    import time as _t
    newest = None
    try:
        for k in _s3_list(s3, bucket, f"{RETRO_RESULT_PREFIX}/{unit}/", suffix=".ckpt.json"):
            if not k.rsplit("/", 1)[-1].startswith("ckpt_"):
                continue
            try:
                mt = s3.head_object(Bucket=bucket, Key=k)["LastModified"].timestamp()
            except Exception:  # noqa: BLE001 — one unreadable object must not hide another's evidence
                continue
            newest = mt if newest is None else max(newest, mt)
    except Exception as e:  # noqa: BLE001 — reported, never swallowed into "it never committed"
        print(f"[retro-commit] could not list checkpoints for {unit}: {type(e).__name__}: {e}", flush=True)
        return None
    if newest is None:
        return None
    return _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime(newest))


def retro_streak_since_utc(record_at, unit, committed_utc=None):
    """When this unit's CURRENT failure streak starts: the NEWEST of its last completed leg record and its
    last banked production checkpoint. `None` when it has neither, which is the case the lifetime count was
    written for. PURE.

    ⚠ THE MAX OF THE TWO, NOT THE LEG RECORD ALONE. Either one is superseding evidence — a finished leg and
    a banked production checkpoint both prove the unit worked after the attempt that preceded them — so the
    streak starts at whichever is later. Anchoring on the leg record alone is what deadlocked a leg at 40 %;
    see `retro_committed_at` for the measurement and why a checkpoint is the right `KIND_COMMIT` analogue.

    ★★ THE ORIGINAL DEFECT THIS FUNCTION EXISTS FOR, retained (measured 2026-07-31, 1:40 PM ET).
    `retro_supervise` called `leg_failure_breaker.count_attempts` with no `since_utc`, so it got the LIFETIME
    attempt count while `retro_breaker` reads it as "how many times has this unit failed IN A ROW".
    `count_attempts.__doc__` documents that divergence and the fix it received for the ternary lane on
    2026-07-30; this call site never got it. The pilot's archive held three objects — two smoke attempts at
    10:46 and 10:50 AM ET, the second of which SUCCEEDED and wrote a leg record at 10:53, and the production
    pilot at 12:00 PM ET — so `3 >= 3` blocked it on every 8-minute tick while its host sat unreplaced.
    """
    import calendar
    import time as _t
    stamps = []
    mt = (record_at or {}).get(unit)
    if mt:
        stamps.append(float(mt))
    if committed_utc:
        try:
            stamps.append(float(calendar.timegm(_t.strptime(committed_utc, "%Y-%m-%dT%H:%M:%SZ"))))
        except (TypeError, ValueError):
            pass                                    # undateable is UNKNOWN — it simply does not supersede
    if not stamps:
        return None
    return _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime(max(stamps)))


def retro_read_authorized(s3, bucket):
    """Units a human dispatch has authorised to run. Absent record -> empty set (fail closed, never 'all')."""
    try:
        doc = json.loads(s3.get_object(Bucket=bucket,
                                       Key=f"{RETRO_RESULT_PREFIX}/{RETRO_AUTHORIZED_UNITS_KEY}"
                                       )["Body"].read().decode())
    except Exception:  # noqa: BLE001 — no record yet is not an error, it is "nothing authorised"
        return set()
    u = doc.get("units", doc)
    return set(u) if isinstance(u, (list, set, dict)) else set()


def retro_authorize_units(s3, bucket, names, mode="run"):
    """Record `names` as authorised to run. Called ONLY from an operator-dispatched launch — never from the
    supervision tick, which is exactly the privilege it must not have. Additive: authorising a pilot does not
    de-authorise a fan-out that was authorised earlier."""
    have = retro_read_authorized(s3, bucket)
    doc = {"units": sorted(have | set(names)), "utc": _utcnow(), "last_mode": mode,
           "_what": "Units an OPERATOR dispatch authorised. nrv04_vast_launch.retro_supervise re-places only "
                    "these; anything else is awaiting_authorization and is never bought unattended."}
    try:
        s3.put_object(Bucket=bucket, Key=f"{RETRO_RESULT_PREFIX}/{RETRO_AUTHORIZED_UNITS_KEY}",
                      Body=json.dumps(doc, indent=2).encode())
        print(f"[retro-auth] authorised {len(names)} unit(s); {len(doc['units'])} authorised in total",
              flush=True)
    except Exception as e:  # noqa: BLE001 — a bookkeeping failure must not abort a launch already paid for
        print(f"[retro-auth] WARN authorization record not saved: {e}", flush=True)
    return doc

#: Minutes a `stopped` box may sit before a strike counts. Not a fresh number — it is the guard's own
#: cold-start line, imported at use, because a box mid-image-pull is exactly what must NOT be condemned.
def _retro_stuck_grace_min():
    import vast_idle_guard as vig
    return vig.MIN_INSTANCE_AGE_MIN


def retro_breaker(has_result, n_attempts, threshold=None, since_utc=None):
    """PURE: may we rent a host for this unit? Returns a `leg_failure_breaker`-shaped verdict dict.

    ⚠ `n_attempts` MUST BE A STREAK, NOT A LIFETIME COUNT. `since_utc` is carried here only so the verdict
    can SAY which denominator produced the number — the caller measures it (`retro_streak_since_utc`, whose
    docstring holds the 2026-07-31 incident this parameter exists because of). A verdict that prints a bare
    count is unauditable: 3 lifetime attempts and 3 consecutive failures are opposite facts.

    ⚠ WHY `leg_failure_breaker.decide` CANNOT BE CALLED DIRECTLY HERE, stated so nobody "simplifies" it back.
    `decide` keys on `record["status"] == "failed"`. This lane's driver (`nrv04_covalent_md.run_leg`) writes
    no `status` field at all — its record is `R1_interface`/`n_frames`/`blew_up` — so every retro record
    lands in `decide`'s fail-open `ALLOW_UNDER` branch. Worse, the failure this breaker must stop writes NO
    record whatsoever: a leg that dies in `build_system` raises before `json.dump`, so `decide` sees
    `record is None` and returns `ALLOW_NO_RECORD` — allow, forever, on every tick. Pointing an autonomous
    re-placer at that is precisely the unbounded re-buy loop `leg_failure_breaker.__doc__` was written about.
    So the DISCRIMINATOR is adapted while the RULE, the threshold and the evidence source are reused verbatim.

    THE DISCRIMINATOR FOR THIS LANE: **no result after N paid hosts.** A retro leg that works writes
    `leg_*.json`; one that dies in staging or build writes nothing. So "attempts archived, still no record"
    IS the consecutive-failure count, with no bookkeeping of ours to drift — `n_attempts` is measured from
    the host-written `attempts/` archive (`leg_failure_breaker.count_attempts`), never remembered.

    FAILS OPEN on an unreadable count (`n_attempts is None`), for `count_attempts`' own stated reason: the
    worst case is one extra rental, whereas failing closed on a transient listing error stalls the lane.

    NOT PERMANENT: clear the archive (`leg_failure_breaker.reset_for`) once the cause is fixed and the next
    tick rents normally. A landed result clears it implicitly — a unit with a record is never in `needed`.
    """
    import leg_failure_breaker as lfb
    threshold = lfb.DEFAULT_THRESHOLD if threshold is None else int(threshold)
    span = ("since this unit last banked work — a completed leg record or a production checkpoint (%s)"
            % since_utc) if since_utc else \
           ("over this unit's whole life — it has never written a leg record NOR banked a production "
            "checkpoint, so lifetime IS the streak")
    base = {"n_attempts": n_attempts, "threshold": threshold,
            "streak_since_utc": since_utc, "counted": span}
    if has_result:
        return dict(base, block=False, verdict=lfb.ALLOW_DONE)
    if n_attempts is None:
        return dict(base, block=False,
                    verdict="allow: attempt count unreadable — failing OPEN (one extra "
                            "rental beats a lane halted by a listing error)")
    if n_attempts >= threshold:
        return dict(base, block=True, verdict=lfb.BLOCK,
                    why=("this unit has been rented %d times %s (threshold %d) and has still written NO leg "
                         "record. A retro leg that runs writes leg_*.json as its last act, so %d paid hosts "
                         "with no record is a reproducing staging/build fault, not bad luck — buying another "
                         "tests nothing. NOT permanent: fix the cause, then leg_failure_breaker.reset_for() "
                         "clears the archive and the next tick rents normally."
                         % (n_attempts, span, threshold, n_attempts)))
    return dict(base, block=False, verdict=lfb.ALLOW_UNDER)


NUDGE, CONDEMN, LEAVE = "nudge", "condemn", "leave"


def retro_stuck_decision(cur_state, status_msg, age_min, strikes, refused=False, grace_min=None):
    """PURE: what to do with ONE box of ours that is not `running`. Returns (action, why).

    Mirrors the step-1 fan-out's escalation (`congeneric_fanout_vast`, 2026-07-27) rather than inventing one,
    because that shape was arrived at by fixing two real bugs in it:
      * a box still PULLING the ~6 GiB image is also not running, and advertises the pull in `status_msg`.
        Condemning on age alone reaps healthy slow starts — the false positive that is worse than the bug.
      * so condemnation needs BOTH the stuck signature AND two consecutive checks past the grace (§4: one
        unlucky sample — an API blip, a listing mid-transition — must never destroy a rental).
    `refused` short-circuits both: Vast answering `resources_unavailable` is the provider's own verdict, and
    CLAUDE.md §6's standing rule for it is destroy and pick another host, never wait it out.
    """
    grace = _retro_stuck_grace_min() if grace_min is None else float(grace_min)
    if refused:
        return CONDEMN, ("Vast replied resources_unavailable — the machine is declining us. §6: destroy and "
                         "pick another host, never wait it out.")
    if (cur_state or "") == "running":
        return LEAVE, ""
    stuck_sig = not (status_msg or "").strip()
    if age_min is None:
        return NUDGE, "age unknown — nudged, never condemned on a fact we do not have"
    if stuck_sig and age_min >= grace and int(strikes or 0) >= 1:
        return CONDEMN, ("stopped with an EMPTY status_msg for %.0f min (grace %.0f) on two consecutive "
                         "checks — not an image pull, a host that will not start" % (age_min, grace))
    return NUDGE, ("stopped %.0f min, status_msg %r — nudging; %s"
                   % (age_min, (status_msg or "")[:60],
                      "strike recorded" if stuck_sig and age_min >= grace else "no strike (pull in progress "
                      "or inside the grace)"))


def retro_supervise(bucket, s3=None, key=None, now=None, launch=True):
    """THE TICK. Nudge → condemn → re-place, and return a readout of every decision.

    Runs inside `retro_collect` (after the reap, before the board) so ONE dispatch both supervises and heals.
    Every rental it makes goes through `retro_launch`, so it faces the identical market gate and the
    identical `buy_ceiling_usd_per_ns` on the spec — there is no privileged path into this lane's wallet.

    A HOLD, A BLOCK AND A REFUSAL ARE ALL VISIBLE (CLAUDE.md §6's "holding silently" failure mode): each
    lands in the returned dict and is printed, so a tick that bought nothing can never be mistaken for a lane
    that finished.
    """
    import time
    import boto3
    import leg_failure_breaker as lfb
    import nrv04_retro_panel as retro
    import vast_idle_guard as vig
    s3 = s3 or boto3.client("s3")
    key = key or os.environ.get("VAST_API_KEY")
    now = time.time() if now is None else now
    out = {"utc": _utcnow(), "nudged": [], "condemned": [], "blocked": [], "replaced": [],
           "held": None, "unreadable": None, "awaiting_authorization": [], "quarantined": [],
           "quarantine_eligible_running": []}
    if not key:
        out["unreadable"] = "no VAST_API_KEY — cannot read the fleet, so nothing is nudged, condemned or bought"
        print("[retro-super] " + out["unreadable"], flush=True)
        return out

    try:
        live_all = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    except Exception as e:  # noqa: BLE001 — "could not ask" is NEVER "asked and the answer was none"
        out["unreadable"] = f"{type(e).__name__}: {e}"[:200]
        print(f"[retro-super] fleet UNREADABLE ({out['unreadable']}) — nothing condemned, nothing bought. "
              f"Condemning a host is irreversible and must require a read we actually got.", flush=True)
        return out
    mine = [i for i in live_all if (i.get("label") or "").startswith(retro.LABEL_PREFIX)]

    # ONE walk of the leg records, shared by the done-set and by the breaker's denominator below. Two walks
    # could disagree about what landed and what the streak is measured from, which is the class of bug
    # `retro_leg_records` was factored out to end.
    records = retro_leg_records(s3, bucket)
    done_units = retro_done_units(s3, bucket, records)
    record_at = retro_record_units(s3, bucket, records)
    # The newest record PER UNIT, off the same walk — the quarantine predicate reads its energies.
    newest_rec = {}
    for _u, _k, _rec, _mt in records:
        if _u not in newest_rec or _mt >= newest_rec[_u][0]:
            newest_rec[_u] = (_mt, _rec)
    newest_rec = {_u: _v[1] for _u, _v in newest_rec.items()}
    state = {}
    try:
        state = json.loads(s3.get_object(Bucket=bucket,
                                         Key=f"{RETRO_RESULT_PREFIX}/{RETRO_SUPERVISE_STATE_KEY}"
                                         )["Body"].read().decode())
    except Exception:  # noqa: BLE001 — a first tick has no strikes; that is a first tick, not an error
        state = {}
    new_state = {}

    # ── 1 + 2 · NUDGE what we hold, DESTROY what is provably not working ────────────────────────────────
    for inst in mine:
        label, iid = inst.get("label") or "", str(inst.get("id"))
        if label in done_units:
            continue                                   # finished; `retro_reap` owns that teardown
        try:
            age_min = max(0.0, (now - float(inst.get("start_date"))) / 60.0)
        except (TypeError, ValueError):
            age_min = None
        cur = inst.get("cur_state") or inst.get("actual_status")
        prev_strikes = int(((state.get(label) or {}).get("stuck_strikes")) or 0)

        if (cur or "") != "running":
            refused = False
            try:                                       # the nudge IS the diagnostic: it returns the verdict
                resp = _vast_request("PUT", f"/instances/{iid}/", key, body={"state": "running"})
                refused = str((resp or {}).get("error") or "") == "resources_unavailable"
            except Exception as e:  # noqa: BLE001
                print(f"[retro-super] nudge {iid} failed: {e}", flush=True)
            action, why = retro_stuck_decision(cur, inst.get("status_msg"), age_min, prev_strikes,
                                               refused=refused)
            if action == CONDEMN:
                try:
                    _vast_request("DELETE", f"/instances/{iid}/", key)
                    out["condemned"].append({"instance": iid, "unit": label, "why": why})
                    print(f"[retro-super] ⛔ DESTROYED {iid} ({label}) — {why}. Billing stopped; the "
                          f"checkpoint is intact in S3 and the re-placer below re-prices this unit.",
                          flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"[retro-super] destroy {iid} FAILED ({e}) — it may still be billing", flush=True)
                continue                               # destroyed -> no strike to carry
            out["nudged"].append({"instance": iid, "unit": label, "why": why})
            print(f"[retro-super] nudged {iid} ({label}) — {why}", flush=True)
            stuck_sig = not (inst.get("status_msg") or "").strip()
            if stuck_sig and age_min is not None and age_min >= _retro_stuck_grace_min():
                new_state[label] = {"stuck_strikes": prev_strikes + 1, "utc": out["utc"]}
            continue

        # RUNNING: the guard's question is not "is the GPU busy" (it never condemns on that) but "is there
        # any positive evidence of work?" — the log's freshness, which is durable and lives in S3.
        log_age = None
        try:
            h = s3.head_object(Bucket=bucket, Key=f"{RETRO_RESULT_PREFIX}/{label}/run.log")
            log_age = max(0.0, (now - h["LastModified"].timestamp()) / 60.0)
        except Exception:  # noqa: BLE001 — absent and unreadable are BOTH unknown, never zero
            log_age = None
        verdict, reason = vig.classify_idle(
            instance_running=True, gpu_util=_inst_gpu_util(inst), log_age_min=log_age,
            instance_age_min=age_min)
        if vig.should_destroy(verdict):
            try:
                _vast_request("DELETE", f"/instances/{iid}/", key)
                out["condemned"].append({"instance": iid, "unit": label, "why": f"{verdict}: {reason}"})
                print(f"[retro-super] ⛔ DESTROYED {iid} ({label}) — idle guard says {verdict}: {reason}",
                      flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[retro-super] destroy {iid} FAILED ({e}) — it may still be billing", flush=True)
        else:
            print(f"[retro-super] {label} ({iid}) {verdict}: {reason}", flush=True)

    try:                                               # strikes saved AFTER they are read, never before
        s3.put_object(Bucket=bucket, Key=f"{RETRO_RESULT_PREFIX}/{RETRO_SUPERVISE_STATE_KEY}",
                      Body=json.dumps(new_state, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[retro-super] strike state not saved: {e}", flush=True)

    # ── 4 · THE BREAKER, BEFORE ANYTHING IS BOUGHT ─────────────────────────────────────────────────────
    alive = {(i.get("label") or "") for i in mine
             if (i.get("actual_status") or "") in ("running", "loading", "created", "scheduling", "starting")
             and str(i.get("id")) not in {c["instance"] for c in out["condemned"]}}
    # ⛔ THE HOLD, ENFORCED. Supervision heals what was AUTHORISED; it does not start what nobody has agreed to
    # buy. See `RETRO_AUTHORIZED_UNITS_KEY` for the measurement that made this necessary.
    authorized = retro_read_authorized(s3, bucket)
    out["n_authorized"] = len(authorized)
    needed = []
    for a, m, r in retro.enumerate_units():
        name = retro.unit_name(a, m, r)
        if name in done_units or name in alive:
            # ⚠ VISIBILITY ONLY, AND DELIBERATELY NOT A KILL (trimcrae's coordinator, 2026-07-31: leave the
            # count as it is, make the reason visible). The quarantine is a PURCHASING gate — it stops us
            # renting a host for an input no host can run — and CLAUDE.md §6 draws the same boundary for the
            # market gate: "work already executing is never touched". A unit whose newest record is
            # non-physical but which is on a host RIGHT NOW is therefore left alone; what was wrong is that it
            # rendered as an ordinary running unit, so the board showed 1 QUARANTINE while the diagnosis named
            # two units. The reason existed and was simply unreachable for anything not hostless.
            # It clears itself: this reads the NEWEST leg record, so the moment the live leg writes a clean
            # one the flag is gone with no edit.
            if name in alive:
                _aq, _aqwhy = retro_input_quarantine(newest_rec.get(name))
                if _aq:
                    out["quarantine_eligible_running"].append({"unit": name, "why": _aqwhy})
                    print(f"[retro-super] ⚠ {name} is RUNNING on a host and its newest leg record is "
                          f"quarantine-eligible — not stopped (the quarantine gates PURCHASES, never work "
                          f"already executing), but it is expected to reproduce: {_aqwhy}", flush=True)
            continue
        if name not in authorized:
            out["awaiting_authorization"].append(name)
            continue
        # ⚠ THE DENOMINATOR IS THE STREAK, NOT THE LIFETIME COUNT. Passing no `since_utc` here is what
        # blocked the pilot on every tick from 12:07 PM ET on 2026-07-31 while its host sat unreplaced —
        # `retro_streak_since_utc` holds the measurement and why a leg record is the superseding fact.
        # ⛔ A BROKEN INPUT IS REFUSED BEFORE THE BREAKER, so it costs $0 instead of three rentals. The
        # breaker measures REPETITION; this measures the CAUSE, and when the cause is a non-physical built
        # system there is nothing to repeat. See `retro_input_quarantine` for the 3:38 PM ET root cause.
        _q, _qwhy = retro_input_quarantine(newest_rec.get(name))
        if _q:
            out["quarantined"].append({"unit": name, "why": _qwhy})
            print(f"[retro-super] ⛔ QUARANTINED {name} — {_qwhy}", flush=True)
            continue
        # BANKED WORK SUPERSEDES, or a leg that is part-done can never be re-placed — the 40 % deadlock in
        # `retro_committed_at`. The checkpoint read is one prefix list per hostless unit, on a tick that is
        # already reading S3, and only for units that got this far (not done, not alive, authorised).
        since = retro_streak_since_utc(record_at, name, retro_committed_at(s3, bucket, name))
        n_att = lfb.count_attempts(s3, bucket, RETRO_RESULT_PREFIX, name, since_utc=since)
        d = retro_breaker(has_result=False, n_attempts=n_att, since_utc=since)
        if d["block"]:
            out["blocked"].append(dict(d, unit=name))
            print(f"[retro-super] ⛔ BLOCKED {name} — {d['why']}", flush=True)
            continue
        needed.append(name)
    out["needed"] = needed
    if out["awaiting_authorization"]:
        # VISIBLE, EVERY TICK. CLAUDE.md §6's "holding silently" failure mode: a lane that never launches must
        # not look like a lane that finished. This says which units are held and what would release them.
        print(f"[retro-super] ⏸ {len(out['awaiting_authorization'])} unit(s) NOT re-placed — they have never "
              f"been authorised to launch, so they are HELD, not hostless: "
              f"{out['awaiting_authorization']}. Supervision heals units an operator dispatch authorised; it "
              f"does not open a fan-out. Release them with a `retro_pilot` / `retro_full` dispatch "
              f"(md_mode=run), which is what writes {RETRO_AUTHORIZED_UNITS_KEY}.", flush=True)
    if not needed:
        print("[retro-super] nothing to re-place — every authorized unit has a result, a live host, is "
              "blocked by the breaker, or is awaiting authorization (see above).", flush=True)
        return out

    # ── 3 · RE-PLACE, through the lane's OWN launcher so the gate and the buy line are the same ones ────
    if not launch:
        out["would_replace"] = needed
        print(f"[retro-super] would re-place {len(needed)}: {needed}", flush=True)
        return out
    print(f"[retro-super] re-placing {len(needed)} hostless AUTHORIZED unit(s): {needed}", flush=True)
    prev_pilot = os.environ.get("RETRO_PILOT_ONLY")
    prev_mode = os.environ.get("MODE")
    os.environ["RETRO_PILOT_ONLY"] = "0"               # the tick heals the WHOLE panel, never one unit
    # ⛔ AND IT HEALS AT THE PANEL'S PROTOCOL, NEVER AT AN AMBIENT DEFAULT (measured 2026-07-31). This tick is
    # dispatched by `step1-fanout-supervisor.yml`, which passes no `md_mode`, so `fusion-cpu-extras.yml`'s
    # choice input defaulted to `smoke` and every leg supervision bought ran 500 steps with no equilibration.
    # The protocol a heal runs is a property of the PANEL (prereg §2b), not of whichever workflow woke us.
    if prev_mode not in (None, "run"):
        print(f"[retro-super] MODE={prev_mode!r} in the environment is IGNORED for re-placement — a heal runs "
              f"the preregistered production protocol (mode=run) or it produces an artifact that cannot enter "
              f"the panel. Dispatch `retro_full` explicitly if a smoke fleet is genuinely wanted.", flush=True)
    os.environ["MODE"] = "run"
    try:
        # ⛔ `only_units=needed` IS WHAT MAKES THE HOLD ABOVE BINDING RATHER THAN DECORATIVE. Without it this
        # call re-derives the whole panel and buys anything the market will sell — which it did, at 1:54 PM
        # ET on 2026-07-31, eight seconds after printing that sixteen units were HELD.
        rc = retro_launch(bucket, authorize=False, only_units=set(needed))
    finally:
        if prev_pilot is None:
            os.environ.pop("RETRO_PILOT_ONLY", None)
        else:
            os.environ["RETRO_PILOT_ONLY"] = prev_pilot
        if prev_mode is None:
            os.environ.pop("MODE", None)
        else:
            os.environ["MODE"] = prev_mode
    out["replace_rc"] = rc
    try:
        out["replaced"] = json.load(open("nrv04-retro-handles.json"))
    except Exception:  # noqa: BLE001
        out["replaced"] = []
    if not out["replaced"]:
        # Distinguish the two reasons, because they call for opposite responses: a price hold re-checks
        # itself on the next tick; a breaker block needs a human to fix a defect.
        try:
            out["held"] = json.load(open(RETRO_MARKET_READOUT))
        except Exception:  # noqa: BLE001
            out["held"] = None
        print("[retro-super] re-placement rented NOTHING this tick — see the market snapshot above. "
              "Every checkpoint is intact; the next tick re-checks.", flush=True)
    return out


RETRO_COLLECT_READOUT = "nrv04-retro-collect.json"

#: The per-tick record of WHY each hostless unit was or was not bought. Its one home; committed every tick.
RETRO_GATE_READOUT = "nrv04-retro-gate.json"


def retro_gate_reasons(sup):
    """{unit: one-sentence REASON it was not bought this tick}, from a `retro_supervise` readout. PURE.

    ★★ A DECLINE THAT DOES NOT SAY WHY IS INDISTINGUISHABLE FROM A BROKEN RE-PLACER (measured 2026-07-31).
    The pilot `nrv04retro-retro_noncov_nr4a3-m1-r0` was hostless from 12:07 PM to 2:02 PM ET — 1 h 55 min
    across TEN consecutive ticks of a supervisor that runs every 8 minutes and is permitted to buy. Every one
    of those ticks declined, and every board row it wrote said only

        no live host — phase marker md-running 2026-07-31T16:01:11Z; a re-dispatch resumes this leg from
        its checkpoint

    which is a description of the STATE, not a reason for the DECISION. The reason (the breaker was blocking
    the unit on a lifetime attempt count) existed only in a job log that GitHub ages out, so from the durable
    record a correctly-refusing gate and a dead re-placer looked identical — which is why it took a human
    noticing rather than the board saying so. CLAUDE.md §6: a hold must be visible, with the snapshot that
    caused it, and the ternary lane satisfies that by committing its market snapshot on EVERY evaluation,
    clear or hold.

    So this maps every unit the tick did not buy to the reason it did not, and `retro_collect` both commits it
    (`RETRO_GATE_READOUT`) and threads it into the board row's `why`.
    """
    out = {}
    for name in (sup or {}).get("awaiting_authorization") or ():
        out[name] = ("HELD — never authorised to launch. Supervision heals only units an operator dispatch "
                     "authorised; release with a retro_pilot / retro_full dispatch (md_mode=run).")
    for q in (sup or {}).get("quarantined") or ():
        out[q.get("unit")] = q.get("why")
    # A unit on a host whose newest record is already quarantine-eligible. NOT a decline — it is running and
    # we are paying for it — so it is worded as an expectation, not a refusal. Same distinction CLAUDE.md §1
    # draws between "⚠ PAYING" and "⛔ REFUSED": one glyph, one meaning.
    for q in (sup or {}).get("quarantine_eligible_running") or ():
        out[q.get("unit")] = ("RUNNING, and expected to reproduce its blow-up — its newest leg record is "
                              "quarantine-eligible, but the quarantine gates PURCHASES and never touches work "
                              "already executing, so this host was not stopped. " + (q.get("why") or ""))
    for b in (sup or {}).get("blocked") or ():
        out[b.get("unit")] = ("BLOCKED by the failure breaker — %s. Counted %s. Clear with "
                              "leg_failure_breaker.reset_for() once the cause is fixed."
                              % (b.get("verdict"), b.get("counted") or "an unstated denominator"))
    held = (sup or {}).get("held") or {}
    # ⛔ A UNIT WE JUST RENTED IS NOT A UNIT WE DECLINED (measured 2026-07-31, 3:25 PM ET tick). `needed` is
    # what the tick SET OUT to buy; `replaced` is what it actually got. Reading only the first made the
    # 40 %-done pilot print `NOT BOUGHT — none was rented` in the same tick whose submit line reads
    # `nrv04retro-retro_noncov_nr4a3-m1-r0 -> instance 46431866 dph≈$0.2182/hr`. That is CLAUDE.md §1's
    # named failure exactly — a row we are paying rendering identically to a row the gate refused.
    bought = {h.get("unit") for h in ((sup or {}).get("replaced") or []) if isinstance(h, dict)}
    for name in (sup or {}).get("needed") or ():
        if name in out:
            continue
        if name in bought:
            out[name] = "BOUGHT this tick — a host was rented for it; see the submit line for the rate."
            continue
        if held:
            out[name] = ("NOT BOUGHT — the market gate %s (%s). Board: %s. $0 spent, checkpoint intact, the "
                         "next tick re-prices."
                         % ("HELD on price" if held.get("hold") else "cleared but no offer was rentable",
                            held.get("reason") or "no reason recorded", json.dumps(held.get("board_depth"))))
        else:
            out[name] = ("NOT BOUGHT — it was due for a host this tick and none was rented; see the tick's "
                         "submit lines for the per-offer refusal (a capacity refusal is not a price hold).")
    if (sup or {}).get("unreadable"):
        for name in list(out) or ():
            out[name] = "fleet UNREADABLE (%s) — nothing was condemned or bought" % sup["unreadable"]
    return out


def persist_retro_gate(sup, reasons, path=None, bucket=None, s3=None):
    """Write the per-tick gate record locally (committed by CI) and durably to S3. Returns the local path.

    Written on EVERY tick, including one that bought everything it wanted — the ternary lane's property that
    a CLEAR evaluation is recorded too, because a snapshot that only appears on a hold cannot distinguish
    "the gate ran and was happy" from "the gate never ran"."""
    doc = {"_what": "NR-V04 retrospective — why each hostless unit was or was not bought on this tick.",
           "_rule": "CLAUDE.md §6 — a hold is never silent, and it carries the snapshot that caused it.",
           "utc": _utcnow(), "lane": "nrv04_retro",
           "n_authorized": (sup or {}).get("n_authorized"),
           "needed": (sup or {}).get("needed") or [],
           "replaced": [h.get("unit") for h in ((sup or {}).get("replaced") or []) if isinstance(h, dict)],
           "blocked": (sup or {}).get("blocked") or [],
           "quarantined": (sup or {}).get("quarantined") or [],
           # Separate key, never merged into `quarantined` — one is "$0, we declined to buy", the other is
           # "we are paying for this right now and expect it to fail". Summing them would misreport spend.
           "quarantine_eligible_running": (sup or {}).get("quarantine_eligible_running") or [],
           "awaiting_authorization": (sup or {}).get("awaiting_authorization") or [],
           "condemned": (sup or {}).get("condemned") or [],
           "nudged": (sup or {}).get("nudged") or [],
           "fleet_unreadable": (sup or {}).get("unreadable"),
           # The market snapshot the decision was taken against — tier included, so a dear ON-DEMAND read
           # can never be mistaken for the interruptible market the ladder is costed on.
           "market": (sup or {}).get("held"),
           "reasons": reasons}
    local = path or RETRO_GATE_READOUT
    try:
        with open(local, "w") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
    except OSError as e:
        print(f"[retro-gate] WARN local record not written to {local}: {e}", flush=True)
    if bucket:
        try:
            if s3 is None:
                import boto3
                s3 = boto3.client("s3")
            s3.put_object(Bucket=bucket, Key=f"{RETRO_RESULT_PREFIX}/gate/nrv04-retro-gate-latest.json",
                          Body=json.dumps(doc, indent=2).encode())
        except Exception as e:  # noqa: BLE001 — a persistence failure is reported, never swallowed
            print(f"[retro-gate] WARN not persisted to S3: {e}", flush=True)
    for u, why in sorted(reasons.items()):
        print(f"[retro-gate] {u}: {why}", flush=True)
    return local

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE IN-FLIGHT BOARD — this lane's 18 endpoint-MD legs, in the renderer every lane shares
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⚠ NOTHING HERE RENDERS A TABLE. `inflight_board` owns the columns, the `—` discipline and the stall rule.
# This lane supplies the facts `retro_collect` already reads; a second table built here is exactly the
# hand-assembled board `inflight_board.__doc__` exists to end.
#
# ★ THE BOARD KEEPS ITS OWN POLL CENSUS. Two consecutive checks with no advance is CLAUDE.md §4's stall rule
# and it needs a memory that survives the runner, so the counters live in S3 beside this lane's results —
# under the BOARD's own key, never inside a file another step overwrites.
_RETRO_BOARD_PREV_KEY = "_board_prev.json"
# Bytes of `run.log` read from the END. The driver's frame census is the most recent thing it printed, and
# these logs grow for hours; a full GET of 18 of them on every collect would make the progress check the
# slowest part of the tick.
_RETRO_LOG_TAIL_BYTES = int(os.environ.get("RETRO_LOG_TAIL_BYTES", "65536"))


def _utcnow():
    """The stamp every durable census in this repo carries. One spelling, so two files can be differenced."""
    import time as _t
    return _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime())


def _inst_gpu_util(inst):
    """GPU utilisation %, or None. BOTH SPELLINGS: the Vast payload carries the live figure as `gpu_util` on
    some responses and `cur_gpu_util` on others, and reading only one silently yields None on the other —
    a guard whose only health signal can go absent is a guard that watches nothing. None is NOT zero."""
    for k in ("gpu_util", "cur_gpu_util"):
        v = (inst or {}).get(k)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def _s3_tail(s3, bucket, key, nbytes=None):
    """The last `nbytes` of an object as text, or None. Absent and unreadable are BOTH None: the caller then
    renders `—` and names the missing fact, never a default."""
    try:
        body = s3.get_object(Bucket=bucket, Key=key,
                             Range=f"bytes=-{int(nbytes or _RETRO_LOG_TAIL_BYTES)}")["Body"].read()
        return body.decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None


def retro_board_price_cell(inst):
    """The `$/ns` cell for one endpoint-MD leg. DELIBERATELY UNPRICEABLE IN $/ns, and it says so.

    ⚠ `vast_cost_model.MEASURED_NS_PER_DAY_84K` is "THE ONLY THROUGHPUT TABLE" and it is a table of **84k-atom
    RBFE** throughput — HREX across 12 windows on the fan-out's hybrid system. These legs are plain endpoint
    MD on a ~466k-atom assembly, a different workload on a different system: nothing in this repo has measured
    their ns/h. Running their `$/hr` through the RBFE table would emit a confident-looking `$/ns` describing a
    calculation nobody benched, which is the substitution `vast_cost_model.card_of` was tightened to prevent
    one level down ("worse than being unpriceable — an UNKNOWN is visibly absent, a substitution produces a
    figure nothing downstream can distinguish from a measurement").

    So the cell carries the rate this lane IS paying, which is measured, and refuses the conversion out loud.
    The lane's price DISCIPLINE is unaffected and lives where it binds: `buy_ceiling_usd_per_ns()` on the spec
    handed to `submit`, which refuses an offer above the approved $/ns before selection ever sees it.
    """
    import inflight_board as ifb
    if inst is None:
        return None
    return ifb.unpriceable_usd_cell(inst.get("dph_total"),
                                    "endpoint MD, not the 84k-atom RBFE the throughput table benches")


def _phase_marker_provenance(phase, inst):
    """' (from a PREVIOUS host…)' when the phase marker predates the host currently holding this unit. PURE.

    ★★ AN OLD MARKER ON A FRESH HOST IS NOT A WEDGE (CLAUDE.md §4 — an absent reading is not a reading of
    absence, and a populated field is not a measured one). `phase.txt` is written by whichever attempt was
    last in the unit's prefix and SURVIVES that host's death, so a leg re-placed at 2:02 PM ET still shows
    `md-running 16:01:11Z` from the host it lost at 12:07 PM. Read without provenance that is a two-hour
    wedge; read with it, it is a normal cold start. The discriminator is the instance's own `start_date`,
    which is the only fact that can date the marker against the rental it is being read beside.
    """
    import calendar
    import re as _re
    import time as _t
    if inst is None or not phase:
        return ""
    m = _re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", str(phase))
    if not m:
        return ""
    try:
        marker = calendar.timegm(_t.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ"))
        started = float(inst.get("start_date"))
    except (TypeError, ValueError):
        return ""                                   # undateable is UNKNOWN — never asserted either way
    if marker >= started:
        return ""
    return (" — ⚠ that marker was written by a PREVIOUS host and survived it; the host holding this unit "
            "now started %.0f min later, so the marker is not evidence about this rental"
            % ((started - marker) / 60.0))


def retro_board_rows(s3, bucket, phases, have, live, unreadable, prev_state, now=None, reasons=None,
                     quarantine_running=None):
    """(rows, new_state) for this lane's in-flight board. Finished legs are counted, not rowed.

    ⚠ NO UNIT IS DROPPED FOR BEING UNMEASURABLE — an unknown `%` or ETA renders `—` with the WHY naming which
    fact is missing. A unit that vanishes reads as a unit that does not exist, which on an 18-leg panel is
    the difference between "the fan-out is running" and "13 legs are unaccounted for".
    """
    import inflight_board as ifb
    import nrv04_retro_panel as retro
    import vast_idle_guard as vig
    import time as _t
    now = _t.time() if now is None else now
    by_label = {(i.get("label") or ""): i for i in (live or ())}
    units = [retro.unit_name(a, m, r) for a, m, r in retro.enumerate_units()]
    census, pending = {}, []
    for name in units:
        if name in (have or set()):
            continue                                    # landed — counted in the note, not rowed
        log = _s3_tail(s3, bucket, f"{RETRO_RESULT_PREFIX}/{name}/run.log")
        frames = ifb.parse_md_frames(log) if log else None
        # The progress SCALAR is the driver's own frame count. `phase.txt` is context around it: a phase
        # marker says which phase was entered and can sit at `md-running` forever on a wedged box, which is
        # precisely why it cannot be the thing "did it advance?" is asked of.
        census[name] = {"stage": "md", "iteration": (frames[0] if frames else None), "utc": _utcnow()}
        pending.append((name, frames, (phases or {}).get(name)))
    new_state = ifb.advance_counters(prev_state, census)
    rows = []
    for name, frames, phase in pending:
        inst = by_label.get(name)
        try:
            total = frames[1] if frames else None
            pct = ifb.sequential_pct((("md", total),), "md", frames[0]) if total else None
            # ★★ THE PERCENTAGE MUST NAME ITS DENOMINATOR WHEN THE DENOMINATOR IS NOT THE PROTOCOL
            # (2026-07-31). Sixteen rows of this board rendered `100.0%` for legs that are not landed legs:
            # their census came from a `mode=smoke` run.log, which reaches `frame 5/5` in 4-20 s. The
            # arithmetic was correct and the EXPERIMENT was a different one, and `100.0%` is exactly the cell
            # that gets quoted away from the banner that says so.
            #
            # ⚠ THE DISCRIMINATOR IS THE CENSUS'S OWN TOTAL, NOT THE UNIT'S LEG RECORD. A record is a fact
            # about some PAST attempt; the moment a smoke-recorded unit is re-placed at mode=run its live
            # run.log is production while its newest record is still the stale smoke one, and keying off the
            # record would then label a real production leg `smoke`. The frame total is written by the run
            # that is producing the number — CLAUDE.md §4b's rule, that a field's presence is never evidence
            # of its provenance, applied to the denominator itself. One home for the expected count:
            # `nrv04_retro_panel.expected_production_frames()`.
            pct_of = None
            if total and int(total) != retro.expected_production_frames():
                pct_of = "smoke" if int(total) <= 5 else "%d fr" % int(total)
                pct = None
            rate = ifb.measured_rate_per_h((prev_state or {}).get(name), census.get(name))
            # The ETA falls with the percentage, and for the same reason: `remaining` off a 5-frame smoke
            # total is "0 frames left" of an experiment we are not running, which would render an imminent
            # completion time for a leg that has not started its production sampling.
            remaining = (ifb.sequential_remaining((("md", total),), "md", frames[0])
                         if (total and not pct_of) else None)
            eta_s = (remaining / rate * 3600.0) if (remaining is not None and rate) else None
            # TWO reasons, kept apart: `cell_why` explains a `—` cell (true of a healthy leg), `state_why`
            # justifies a non-RUNNING verdict. Handing the first to `state_of` is how a STALLED row ends up
            # carrying an explanation that denies the stall — the exact defect that shipped twice on the
            # ternary board.
            cell_why = ""
            if frames is None:
                cell_why = ("no frame census yet: the driver prints `checkpoint @ frame N/M` into run.log "
                            "and this leg has not reached its first checkpoint (phase %s)%s"
                            % (phase or "none", _phase_marker_provenance(phase, inst)))
            elif pct_of:
                cell_why = ("%% DONE withheld: the newest run.log census is frame %d/%d, and %d is not this "
                            "panel's production frame count (%d) — that census is a %s run, so a percentage "
                            "of it would describe a different experiment"
                            % (frames[0], frames[1], frames[1], retro.expected_production_frames(),
                               "smoke" if int(total) <= 5 else "non-production"))
            elif rate is None:
                cell_why = ("no measured frame rate across two board polls yet — ETA unknowable, progress is "
                            "real (frame %d/%d)" % (frames[0], frames[1]))
            try:
                age_min = max(0.0, (now - float(inst.get("start_date"))) / 60.0) if inst else None
            except (TypeError, ValueError):
                age_min = None
            cold = age_min is not None and age_min < vig.MIN_INSTANCE_AGE_MIN
            pre_first = frames is None and age_min is not None and age_min < vig.SETUP_GRACE_MIN
            no_adv = int((new_state.get(name) or {}).get("no_advance_polls") or 0)
            if inst is None and unreadable:
                state_why = ("host state UNKNOWN — the Vast instance list did not read this tick (%s), so "
                             "this is NOT a host death; phase marker %s" % (unreadable, phase or "none"))
            elif inst is None:
                # ⛔ THE DECISION, NOT JUST THE STATE. "no live host" describes the row; it does not say
                # whether the re-placer declined, why, or whether it is even trying. Ten consecutive rows
                # carrying only the former is how a blocked pilot went unnoticed for 1 h 55 min — see
                # `retro_gate_reasons`.
                state_why = ("no live host — phase marker %s; a re-dispatch resumes this leg from its "
                             "checkpoint. THIS TICK: %s"
                             % (phase or "none",
                                (reasons or {}).get(name)
                                or "no gate decision recorded for this unit — if that persists, the "
                                   "re-placer is not evaluating it at all, which is a defect, not a hold"))
            elif no_adv >= ifb.STALL_POLLS:
                # `None` is "the host is not telling us", NOT an idle GPU — the two must not render alike,
                # because only the second is evidence of anything.
                _u = _inst_gpu_util(inst)
                # ⚠ THE POLL COUNT IS A UNIT-LIFETIME FIGURE AND MUST NOT READ AS ONE RENTAL'S (2026-07-31,
                # 3:17 PM ET). `no_advance_polls` accumulates on the UNIT and survives every re-placement, so
                # `nr4a1 m1 r1` rendered "22 consecutive board polls with no new frame" — the wedge signature
                # — on a host that was ONE MINUTE OLD. Twenty-one of those polls were other rentals'. Same
                # family as the phase-marker defect fixed alongside it: a fact about the unit presented as a
                # fact about this rental. The host's own age is the discriminator, and it is stated here so
                # nobody has to infer it.
                _age = "age unknown" if age_min is None else "this host is %.0f min old" % age_min
                _pre = ("" if (age_min is None or not cold) else
                        " — ⚠ MOST OF THOSE POLLS PREDATE THIS RENTAL: the counter is on the unit and "
                        "survives re-placement, and this host is still inside the %g min cold-start floor, "
                        "so this is a fresh host carrying an old count, not a wedge"
                        % vig.MIN_INSTANCE_AGE_MIN)
                state_why = ("%d consecutive board polls with no new frame (%s)%s; phase marker %s%s, GPU %s"
                             % (no_adv, _age, _pre, phase or "none",
                                _phase_marker_provenance(phase, inst),
                                "utilisation not reported by the host" if _u is None else "%.1f%%" % _u))
            else:
                state_why = cell_why
            # ⚠ A UNIT ON A HOST WHOSE NEWEST RECORD IS ALREADY QUARANTINE-ELIGIBLE SAYS SO ON ITS ROW
            # (2026-07-31). The quarantine only ever reached HOSTLESS units, so the board showed 1 QUARANTINE
            # while the diagnosis named two — `m3-r0` was hostless and refused, `m3-r1` was mid-rental and
            # rendered as an ordinary running leg with nothing to distinguish it. The gate is unchanged and
            # this host is NOT stopped (it gates purchases, not executing work); what changes is that the row
            # now carries the expectation. Appended rather than substituted, because the host-state reason is
            # still true and still the reason for the RUNNING verdict.
            if inst is not None and name in (quarantine_running or set()):
                state_why = ((state_why + " · " if state_why else "")
                             + "⚠ QUARANTINE-ELIGIBLE INPUT: this unit's newest leg record is non-physical "
                               "(blew up at the first production step). It is not stopped — the quarantine "
                               "gates PURCHASES, never work already executing — but this rental is expected "
                               "to reproduce the blow-up in seconds. See retro_input_quarantine.")
            # ADVANCEMENT, from two independent POSITIVE signals and never from the absence of one: the
            # driver's own frame census moved since the previous poll, or the guard's GPU-busy rule observes
            # this box doing work. See `inflight_board.gpu_is_busy` — a low or absent reading never condemns.
            advanced = (ifb.advanced_since_last_poll((prev_state or {}).get(name), census.get(name))
                        or ifb.gpu_is_busy(_inst_gpu_util(inst)))
            state, swhy = ifb.state_of(
                inst is not None, advanced, no_adv, bool(cold), why_not_running=state_why or None,
                pre_first_commit=bool(pre_first),
                host_list_readable=(not unreadable or inst is not None))
            eta_out = None if inst is None else eta_s
            rows.append({"name": _retro_short_name(name), "pct": pct, "pct_of": pct_of, "eta_s": eta_out,
                         "usd_per_ns": retro_board_price_cell(inst), "state": state,
                         "why": swhy or (cell_why if (pct is None or eta_out is None) else "")})
        except Exception as e:  # noqa: BLE001 — per ROW, never per table: one bad leg must not blank the board
            rows.append({"name": _retro_short_name(name), "pct": None, "eta_s": None, "usd_per_ns": None,
                         "state": ifb.UNKNOWN,
                         "why": "row could not be built: %s: %s" % (type(e).__name__, e)})
    return rows, new_state


def _retro_short_name(unit_name):
    """`nrv04retro-retro_noncov_nr4a2-m1-r0` -> `nr4a2 m1 r0`. The paralogue is what distinguishes the arms."""
    import nrv04_retro_panel as retro
    s = str(unit_name or "")
    if s.startswith(retro.LABEL_PREFIX):
        s = s[len(retro.LABEL_PREFIX):]
    return s.replace("retro_noncov_", "").replace("retro_epi_", "epi ").replace("retro_cov_", "cov ") \
            .replace("-", " ")


def persist_retro_collect(out, bucket=None, s3=None, path=None, utc=None):
    """Write the collect readout locally AND durably to S3. Returns the S3 keys written (may be empty).

    ⛔ WHY THIS EXISTS. The verdict is the entire deliverable of a paid-for 18-leg panel, and until 2026-07-31
    it lived ONLY as a file on an ephemeral GitHub runner: `fusion-cpu-extras.yml`'s upload step lists the
    `*-handles.json` and does not even run in `retro_collect` mode, so every collect threw its own output away
    and the only surviving copy was whatever a human happened to scroll past in a job log that GitHub truncates.
    A result that expensive cannot have a home that disappears when the runner does.

    S3 is the DURABLE home — the same bucket the leg JSONs, the checkpoints and this file's own price ledger
    already use, and deliberately NOT a feature branch (CLAUDE.md §7: an artifact whose only home is a branch a
    workflow runs from is a data-loss bug). Two keys, on purpose: a timestamped one that is never overwritten,
    so re-running a collect cannot erase what an earlier one said, and a `-latest` pointer for readers."""
    import time
    txt = json.dumps(out, indent=2)
    local = path or RETRO_COLLECT_READOUT
    try:
        with open(local, "w") as fh:
            fh.write(txt + "\n")
    except OSError as e:
        print(f"[retro-collect] WARN local readout not written to {local}: {e}", flush=True)
    if not bucket:
        return []
    if s3 is None:
        import boto3
        s3 = boto3.client("s3")
    stamp = utc or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    base = f"{RETRO_RESULT_PREFIX}/collect"
    written = []
    for k in (f"{base}/nrv04-retro-collect-{stamp}.json", f"{base}/nrv04-retro-collect-latest.json"):
        try:
            s3.put_object(Bucket=bucket, Key=k, Body=txt.encode())
            written.append(k)
        except Exception as e:  # noqa: BLE001 — a persistence failure must be LOUD, never silent
            print(f"[retro-collect] WARN verdict NOT persisted to s3://{bucket}/{k}: {e}", flush=True)
    if written:
        print(f"[retro-collect] verdict persisted -> " + ", ".join(f"s3://{bucket}/{k}" for k in written),
              flush=True)
    return written


def retro_collect(bucket, reap=None):
    """Pull every landed retrospective leg JSON, map it onto the frozen leg-record schema, and — only when the
    panel is COMPLETE — apply the frozen gate. Prereg §4f forbids an interim look at the arm ordering, so an
    incomplete panel reports coverage ONLY and refuses to compute the contrast.

    This is also the lane's SUPERVISION TICK: it reaps first (the control plane is the only thing that can stop
    the meter — CLAUDE.md §6) and persists its readout to S3 last."""
    import time as _t
    _tick_started = _t.time()
    import boto3
    import nrv04_retro_panel as retro
    import nrv04_retro_gate as gate
    # ⛔ REAP FIRST, so the meter stops at the earliest point in the tick rather than after the (slower) S3
    # walk below. Scoped to this lane's label namespace; other lanes are unreachable from here.
    if (os.environ.get("RETRO_REAP", "1") == "1") if reap is None else reap:
        try:
            retro_reap(bucket)
        except Exception as e:  # noqa: BLE001 — a reap failure must not suppress the science readout
            print(f"[retro-collect] WARN reap failed ({type(e).__name__}: {e}); instances may still be "
                  f"billing — check them before assuming the fleet drained", flush=True)
    s3 = boto3.client("s3")
    # ⛔ THEN SUPERVISE: nudge what we hold, destroy what is provably not working, and re-place every
    # hostless unrun unit behind the same buy line — so ONE dispatch both watches and heals this lane.
    # Before this existed the tick only reaped, and a preempted leg simply stopped existing until a human
    # noticed. Failure here must never suppress the science readout below.
    _sup, _gate_reasons = None, {}
    if os.environ.get("RETRO_SUPERVISE", "1") == "1":
        try:
            _sup = retro_supervise(bucket, s3=s3)
        except Exception as e:  # noqa: BLE001
            print(f"[retro-collect] WARN supervision failed ({type(e).__name__}: {e}); hostless units were "
                  f"NOT re-placed this tick — dispatch retro_full if this repeats", flush=True)
            _gate_reasons = {"_tick": "supervision RAISED (%s: %s) — nothing was re-placed and the reason "
                                      "is a crash, not a refusal" % (type(e).__name__, e)}
    # ⛔ THE DECISION IS RECORDED WHETHER OR NOT IT SPENT ANYTHING — see `retro_gate_reasons` for the ten
    # silent declines that made this necessary. Never allowed to abort the science readout below.
    try:
        if _sup is not None:
            _gate_reasons = retro_gate_reasons(_sup)
        # ⛔ THE MARKET SNAPSHOT EXISTS ON EVERY TICK, CLEAR OR HOLD — the ternary lane's contract, and the
        # property this lane only DECLARED until 2026-07-31 (see `retro_market_gate`'s `price` docstring for
        # the two causes, both read from the code). `retro_launch` writes it whenever it actually priced a
        # purchase; when supervision had nothing to buy, nothing priced it, so record THAT rather than
        # leaving the file to age or vanish. `os.path.getmtime` is the discriminator: a file this tick wrote
        # is newer than this tick started.
        _priced_this_tick = False
        try:
            _priced_this_tick = os.path.getmtime(RETRO_MARKET_READOUT) >= _tick_started
        except OSError:
            _priced_this_tick = False
        if not _priced_this_tick:
            retro_market_gate(max(1, len((_sup or {}).get("needed") or [])), price=False)
        persist_retro_gate(_sup, _gate_reasons, bucket=bucket, s3=s3)
    except Exception as e:  # noqa: BLE001
        print(f"[retro-collect] WARN gate record not written ({type(e).__name__}: {e})", flush=True)
    keys = [k for k in _s3_list(s3, bucket, f"{RETRO_RESULT_PREFIX}/", suffix=".json")
            if k.rsplit("/", 1)[-1].startswith("leg_")]
    legs, raw, nonconforming = [], [], []
    for k in keys:
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())
        except Exception as e:  # noqa: BLE001
            print(f"[retro-collect] WARN unreadable {k}: {e}", flush=True); continue
        raw.append({"key": k, "leg": d.get("leg_id"), "seed": d.get("seed")})
        # ⛔ THE PROTOCOL CHECK, BEFORE THE RECORD IS MAPPED. A `leg_*.json` proves a leg WROTE something, not
        # that the preregistered protocol RAN — `retro.production_leg_check` is where that distinction lives
        # and why. A non-conforming record is recorded and reported, never deleted and never counted.
        _ok, _why = retro.production_leg_check(d)
        if not _ok:
            nonconforming.append({"key": k, "unit": k.split("/")[-2], "leg_id": d.get("leg_id"),
                                  "mode": d.get("mode"), "n_frames": d.get("n_frames"),
                                  "timed_ns": d.get("timed_ns"), "why": _why})
            continue
        _done_ok, _done_why = retro.completed_production_check(d)
        leg_id = d.get("leg_id") or ""
        arm_id, _, mtag = leg_id.partition("__m")
        # ⚠ THE DRIVER'S KEYS ARE `R1_interface` / `R2_recruitment` / `R3_lys` (nrv04_covalent_md.run_leg's
        # result dict), NOT `R1` / `R2`. This mapping read `R1`/`R2` until 2026-07-25, which made EVERY
        # e1_plateau_A None, marked EVERY leg `technical_failure`, and drove the frozen gate to INDETERMINATE
        # on a panel of 24 flawless legs — verified by a controlled reproduction that fed retro_collect
        # driver-shaped leg JSONs through a stubbed S3. The failure was silent and, post-hoc, would have looked
        # like a physics result. The legacy short names are kept as a fallback (no artifact in the bucket uses
        # them) and the schema check below refuses to let a repeat be silent.
        r1 = d.get("R1_interface") or d.get("R1") or {}
        r2 = d.get("R2_recruitment") or d.get("R2") or {}
        r3 = d.get("R3_lys") or d.get("R3") or {}
        rec = {
            "arm_id": arm_id,
            "cofold_model_seed": int(mtag) if mtag.isdigit() else None,
            "replica": d.get("seed"),
            "e1_plateau_A": r1.get("plateau_A"),
            "e2_stable": r1.get("stable"),
            "e3_mean_contacts": r2.get("mean_contacts"),
            "e4_lys_min_A": r3.get("min_A"),            # prereg §3: E2-E4 reported alongside E1 in every result
            "blew_up": bool(d.get("blew_up")),
            # A leg of the right protocol that did not FINISH is a prereg §4e technical failure — it stays in
            # the panel and the frozen gate counts it against MAX_FAILED_LEGS_PER_ARM. That is deliberately a
            # different thing from a smoke record, which is not a leg of this panel at all and is dropped above.
            "complete": _done_ok,
            "incomplete_why": None if _done_ok else _done_why,
            "technical_failure": bool(d.get("blew_up")) or (r1.get("plateau_A") is None) or not _done_ok,
            "source_key": k,
        }
        legs.append(rec)

    # PROGRESS, not liveness. A retro leg writes a phase marker (env-ready -> cloned -> staged -> md-running ->
    # md-done -> uploaded) as it goes. This lane has never run an MD leg end-to-end, so "is it advancing?" has
    # to be answerable between checks — a frozen phase across two consecutive collects is a stall, and without
    # this the only signal would be a result appearing hours later or never.
    phases = {}
    for pk in _s3_list(s3, bucket, f"{RETRO_RESULT_PREFIX}/", suffix="phase.txt"):
        unit = pk.split("/")[-2]
        try:
            phases[unit] = s3.get_object(Bucket=bucket, Key=pk)["Body"].read().decode().strip()
        except Exception as e:  # noqa: BLE001
            phases[unit] = "unreadable: %s" % e

    # `expected` follows AUTHORIZED_STAGES, which AMENDMENT 3 defect 1 reduced to R1 only. That is what makes
    # `panel_complete` reachable at all: while the retired covalent arm was still enumerable, its 6 units could
    # never land (build_system raises before a leg JSON is written), so `missing` was permanently non-empty and
    # prereg §4f suppressed the R1 verdict FOREVER.
    expected = {retro.unit_name(a, m, r) for a, m, r in retro.enumerate_units()}
    # LABEL_PREFIX, not a typed "nrv04retro-": this reconstruction must agree with `unit_name` by construction,
    # or every landed leg silently reads as missing.
    have = {f"{retro.LABEL_PREFIX}{l['arm_id']}-m{l['cofold_model_seed']}-r{l['replica']}" for l in legs}
    missing = sorted(expected - have)
    out = {"n_legs": len(legs), "expected_units": len(expected), "missing_units": missing,
           "panel_complete": not missing, "authorized_stages": list(retro.AUTHORIZED_STAGES),
           "retired_stages": list(retro.RETIRED_STAGES), "phases": phases, "legs": legs, "raw_keys": raw,
           "nonconforming_records": nonconforming}

    for unit, ph in sorted(phases.items()):          # PROGRESS first: a monitoring check must still print the
        print(f"[retro-phase] {unit}: {ph}", flush=True)   # phase markers even if the schema guard then fires
    # SAID OUT LOUD, EVERY TICK. A record that exists but does not count is the failure mode that produced a
    # "18 of 18 landed" board off 18 smoke legs; silence about it is what made that readable as progress.
    for nc in nonconforming:
        print(f"[retro-collect] ⛔ NOT A LANDED LEG {nc['unit']}: {nc['why']} (key {nc['key']})", flush=True)

    # ── THE IN-FLIGHT BOARD ────────────────────────────────────────────────────────────────────────────
    # One row per pending leg, in the SAME renderer the ternary and fan-out lanes use. Published as THIS
    # lane's fragment only; the merged all-lane board is then regenerated from every fragment. This lane
    # never writes another lane's rows, which is the whole write-race resolution (`inflight_board.__doc__`).
    #
    # BEFORE the schema guard and the §4f verdict suppression below, and inside a catch: those two paths
    # `return` early, and a monitoring board that disappears exactly when the science verdict is withheld is
    # a board that is absent whenever something is wrong. A reporting failure must likewise never suppress
    # the readout it reports on.
    try:
        import inflight_board as _ifb
        import nrv04_retro_panel as _retro_lane
        _live, _unreadable = [], None
        try:
            _all = _vast_request("GET", "/instances/", os.environ.get("VAST_API_KEY"),
                                 params={"owner": "me"}).get("instances", [])
            _live = [i for i in _all if (i.get("label") or "").startswith(_retro_lane.LABEL_PREFIX)]
        except Exception as e:  # noqa: BLE001 — "could not ask" is NEVER "asked and the answer was none"
            _unreadable = f"{type(e).__name__}: {e}"[:200]
        _prev_board = {}
        try:
            _prev_board = json.loads(s3.get_object(
                Bucket=bucket,
                Key=f"{RETRO_RESULT_PREFIX}/{_RETRO_BOARD_PREV_KEY}")["Body"].read().decode())
        except Exception:  # noqa: BLE001 — a first tick has no previous census; that is a first census
            _prev_board = {}
        _rows, _new_board = retro_board_rows(
            s3, bucket, phases, have, _live, _unreadable, _prev_board, reasons=_gate_reasons,
            quarantine_running={q.get("unit") for q
                                in ((_sup or {}).get("quarantine_eligible_running") or ())})
        _n_expected = len(expected)
        _frag, _board = _ifb.publish(
            _ifb.NRV04_RETRO, _rows,
            note="%d of %d authorized R1 leg(s) landed (rows below are the rest).%s"
                 % (len(have), _n_expected,
                    "" if not nonconforming else
                    " ⛔ %d further record(s) exist but are NOT landed legs (%s) — they do not count toward "
                    "the panel and cannot reach the frozen gate."
                    % (len(nonconforming), nonconforming[0]["why"].split(" — ")[0])))
        try:                                          # counters saved AFTER they are read, never before
            s3.put_object(Bucket=bucket, Key=f"{RETRO_RESULT_PREFIX}/{_RETRO_BOARD_PREV_KEY}",
                          Body=json.dumps(_new_board, indent=2).encode())
        except Exception as e:  # noqa: BLE001
            print(f"[retro-board] census not saved: {e}", flush=True)
        print(f"[retro-board] wrote {os.path.basename(_frag)} + {os.path.basename(_board)}", flush=True)
        print("\n---- NRV04-RETRO-BOARD ----", flush=True)
        print(_ifb.render(_rows), end="", flush=True)
        print("---- END NRV04-RETRO-BOARD ----\n", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[retro-board] in-flight board not published ({type(e).__name__}: {e}) — the phase census "
              f"above is unaffected; the merged board renders this lane STALE rather than dropping it.",
              flush=True)

    # SCHEMA GUARD. A key-name drift between the driver and this mapping is invisible in the verdict — it
    # arrives as "every leg technically failed", which reads as a physics/stability result. So: if legs landed,
    # none blew up, and yet not one produced an E1, that is a SCHEMA mismatch, and it is said out loud.
    landed = [l for l in legs if not l["blew_up"]]
    if landed and not any(l["e1_plateau_A"] is not None for l in landed):
        out["schema_mismatch"] = (
            "%d leg JSON(s) landed with no blow-up, yet NONE yielded an E1 plateau. That is a leg-JSON schema "
            "mismatch, not a physics outcome — check that the driver's readout keys (R1_interface / "
            "R2_recruitment / R3_lys) still match what this collector reads. Verdict suppressed." % len(landed))
        print("[retro-collect] FATAL " + out["schema_mismatch"], flush=True)
        out["verdict"] = None
        persist_retro_collect(out, bucket=bucket, s3=s3)
        return 1
    if missing:
        out["verdict"] = None
        out["note"] = ("panel INCOMPLETE (%d/%d units) — prereg §4f forbids computing the paralogue contrast "
                       "before every leg has landed. Coverage only.%s"
                       % (len(have), len(expected),
                          "" if not nonconforming else
                          " %d record(s) exist that are NOT landed legs (see nonconforming_records)."
                          % len(nonconforming)))
        print(f"[retro-collect] {len(have)}/{len(expected)} units landed; contrast NOT computed (prereg §4f)",
              flush=True)
    else:
        out["verdict"] = gate.verdict(legs)
        print("[retro-collect] panel complete — frozen gate applied", flush=True)
    persist_retro_collect(out, bucket=bucket, s3=s3)
    print(json.dumps({k: v for k, v in out.items() if k not in ("legs", "raw_keys", "phases")}, indent=2),
          flush=True)
    return 0


def main():
    bucket = os.environ.get("VAST_CKPT_BUCKET")
    if not bucket:
        raise SystemExit("[nrv04-launch] set VAST_CKPT_BUCKET (the reused S3 bucket)")
    if os.environ.get("BENCH") == "1":
        return bench(bucket)
    if os.environ.get("BENCH_COLLECT") == "1":
        return bench_collect(bucket)
    if os.environ.get("FIRM") == "1":
        return firm(bucket)
    if os.environ.get("FIRM_COLLECT") == "1":
        return firm_collect(bucket)
    if os.environ.get("COFOLD") == "1":
        return cofold(bucket)
    if os.environ.get("RETRO_STAGE_TEST") == "1":
        return retro_stage_test(bucket)
    if os.environ.get("RETRO") == "1":
        return retro_launch(bucket)
    if os.environ.get("RETRO_COLLECT") == "1":
        return retro_collect(bucket)
    if os.environ.get("DISCOVER") == "1":
        discover_cofold(bucket)
        return 0
    if os.environ.get("STAGE_TEST") == "1":
        stage_test(bucket)
        return 0
    if os.environ.get("COLLECT") == "1":
        collect(bucket)
        return 0
    if os.environ.get("MONITOR") == "1":
        monitor(bucket)
        return 0
    if os.environ.get("STOP_ALL") == "1":
        stop_all()
        return 0
    if os.environ.get("DIAG") == "1":
        diag()
        return 0
    if os.environ.get("PROBE_OFFERS") == "1":
        probe_offers()
        return 0
    branch = os.environ.get("GIT_BRANCH", "claude/alternative-gpu-providers-wx4r2c")
    mode = os.environ.get("MODE", "run")
    dry = os.environ.get("DRY_RUN", "0") == "1"
    gpu_override = os.environ.get("VAST_GPU_MODEL")               # e.g. rtx8000 for the $/ns bench (default: rtx3090)
    if gpu_override:
        TERNARY_RES.gpu = gpu_override
        print(f"[nrv04-launch] GPU override -> {gpu_override}", flush=True)

    be = get_backend("vast")
    units = units_to_run()
    # IDEMPOTENT launch: skip units that already have a result in S3 (done) or a live Vast instance (running).
    # So re-dispatching 'full' safely RESUMES only the killed/preempted legs (from their S3 checkpoints) without
    # duplicating the ones still running — no two instances ever share a leg's checkpoint (which would race).
    skip_done, skip_live = set(), set()
    if not dry:
        vk = os.environ.get("VAST_API_KEY")
        try:
            live = _vast_request("GET", "/instances/", vk, params={"owner": "me"}).get("instances", [])
            # only skip ACTIVELY-alive instances; an 'exited'/'stopped' one isn't doing the work (the mock
            # teardown leaves crashed/preempted containers lingering as 'exited'), so it SHOULD be relaunched
            _alive = ("running", "loading", "created", "scheduling", "starting")
            skip_live = {i.get("label") for i in live if i.get("label") and (i.get("actual_status") or "") in _alive}
        except Exception as e:  # noqa: BLE001
            print(f"[nrv04-launch] WARN could not list live instances ({e}); not skipping any", flush=True)
        try:
            import boto3
            s3 = boto3.client("s3")
            dk = _s3_list(s3, bucket, f"{RESULT_PREFIX}/", suffix=".json")
            skip_done = {k.split("/")[-2] for k in dk if k.rsplit("/", 1)[-1].startswith("leg_")}
        except Exception as e:  # noqa: BLE001
            print(f"[nrv04-launch] WARN could not list S3 results ({e}); not skipping any", flush=True)
    # presign the pre-packed env once (all instances share it); skipped on dry runs (no live submit).
    env_url = None if dry else presign_env_tarball(bucket)
    print(f"[nrv04-launch] {len(units)} unit(s), mode={mode}, dry_run={dry}, "
          f"skip_done={len(skip_done)}, skip_live={len(skip_live)}", flush=True)
    handles = []
    for leg, seed in units:
        name = unit_name(leg, seed)
        if not dry and name in skip_done:
            print(f"[skip] {name} — result already in S3", flush=True); continue
        if not dry and name in skip_live:
            print(f"[skip] {name} — live instance already running", flush=True); continue
        spec = build_jobspec(leg, seed, mode, branch, bucket, env_tarball_url=env_url)
        if dry:
            print(f"[dry] {spec.name}: gpu={spec.resources.gpu} ram>={spec.resources.ram_gb}GB "
                  f"ckpt={spec.checkpoint_uri} cofold={spec.env['COFOLD_PREFIX_S3']}", flush=True)
            continue
        h = be.submit(spec)
        print(f"[submit] {spec.name} -> instance {h.job_id} dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit": spec.name, "instance": h.job_id, "offer": h.extra.get("offer")})
    if handles:
        json.dump(handles, open("nrv04-vast-handles.json", "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
