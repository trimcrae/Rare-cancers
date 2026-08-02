#!/usr/bin/env python3
"""CROSS-LANE STALENESS WATCH — has each billing lane produced NEW EVIDENCE, and if not, is that EXPECTED?

WHY THIS EXISTS, and why it is a WORKFLOW rather than an agent (trimcrae, 2026-07-27: *"Might be worth
having another subagent watching whose sole job is to make sure none of the vast jobs / lanes get stale."*).
A subagent ends when its turn ends. The thing that survives a turn is a workflow — and 2026-07-27 proved the
point in the most expensive way available: 25 of that day's 30 step-1 autoscale runs were `workflow_dispatch`,
i.e. an agent remembering. Every gap in that memory cost money.

★★ THE QUESTION THIS ASKS IS NOT "IS SOMETHING ALIVE". Liveness is what every existing check already asks,
and liveness is what missed all five of the day's failures:

  1. A valB cohort was DEAD for ~85 min while the cron watchdog printed "advancing at warmup/512 … Leaving it
     alone" — `classify` was handed `instance_alive = inst is not None` and never read `cur_state`. All four
     hosts had been reclaimed; `collect` then got `resources_unavailable` on every one.
  2. The step-1 fan-out decayed 18 -> 5 hosts over ~2 h across SEVEN GREEN TICKS, because a placement guard
     inverted on a null input. The market snapshot froze at 12:43 PM ET and nothing noticed.
  3. Two 5a-KS legs crash-looped at 0 % GPU for ~53 min on a dead credential. The host cannot stop its own
     billing (CLAUDE.md §6), so only the control plane could have.
  4. ⚠ THE ONE NOTHING DETECTS: the closure triangle sat IDLE for ~3 h after `triangle-prime` succeeded,
     because the lane that would dispatch the next step ended its turn. There was NO LIVE INSTANCE AT ALL, so
     every liveness check read it as "nothing to watch" — indistinguishable from finished.
  5. `fleet-supervision-alarm.yml` covers step-1 ONLY, and its own hourly cron delivered essentially nothing.

So the question here is: **did this lane produce new evidence recently, and if not, is that expected?** Three
outcomes, reported separately because they need different responses:

    BILLING-NOT-ADVANCING  hosts up, evidence flat. The EXPENSIVE failure — money out, science not moving.
    IDLE-UNEXPECTED        no hosts AND unfinished work AND nothing holding it. The triangle case, the gap.
    PARKED-*/FINISHED      held on price with a visible snapshot, parked behind a real gate, or done. QUIET.

★★ THE DISTINCTION BETWEEN THE LAST TWO IS THE ENTIRE VALUE. An alarm that fires on a correct price hold is
an alarm nobody reads by tomorrow, and this repo's §6 rules make a correct price hold a NORMAL, DESIRABLE
state — "I'd rather pause until availability opens than pay double per ns". A hold is a success, so it is
green here — and it is green ONLY when the snapshot proving the market was actually consulted is present.

★★ AND "HELD" IS NOT ONE STATE. The ternary gate sets `hold: true` for FOUR different situations and only one
of them is a price decision that time will clear:
    a genuine price hold      -> `depth` + `offers` populated, a ratio/dollar ceiling named       -> QUIET
    `nothing_to_launch: true` -> nothing needed buying; `reason` literally ends "this is NOT a price hold."
    the board was unreadable  -> "an unreadable market is not a cheap one" — no snapshot exists   -> UNKNOWN
    `hold_cause == "exclusions_or_spec_not_price"` (relaunch gate) -> the host blacklist has outgrown the
        market or the ResourceSpec is unsatisfiable. RE-PRICING WILL NEVER CLEAR THIS. Grading it as a price
        hold is how a lane sleeps through a night waiting for a market that was never the problem. -> LOUD

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
WHAT IT DELIBERATELY DOES NOT DO
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
⚠ IT NEVER RENTS, DESTROYS, REAPS, NUDGES, PRICES OR CONDEMNS A BOX. It reads and it complains. Every
destructive act stays in the lanes' own `collect` paths, which read the start response that separates "outbid,
restartable" from "GPU gone, destroy it" (`ternary_vast_launch.collect`, `ResourceSpec.exclude_machine_ids`,
`vast_idle_guard.py`). A watcher that could also act would be a SECOND UNREVIEWED CONTROL PATH — the exact
shape this repo keeps paying for. It also imports nothing from the lanes it watches: an alarm that shares a
dependency with the thing it watches dies with it, which is how the 11:37 AM tick took its own progress check
down on 2026-07-27. The one import is `fleet_supervision_alarm`, which is itself dependency-free by the same
rule, and which is imported precisely so its throttle-immune test is not reimplemented here (§1).

⚠ `gpu_util` IS NOT DIAGNOSTIC AND IS NEVER READ. 0.0 has been observed on genuinely advancing hosts (a
CPU-bound staging phase reads 0.0 for tens of minutes), and `vast_idle_guard.py`'s one inviolable rule is that
GPU idleness NEVER condemns a box. `step1-fanout-progress.json` carries a `gpu_util` array right next to the
census this module does read; `test_lane_staleness_watch.py` asserts by AST that the key never appears here.

⚠ ABSENT IS NEVER A LEGAL GOOD VALUE. This bit six times on 2026-07-27 alone: `hysteresis_kcal or 0.0` wrote
"no reverse leg ran" as perfect antisymmetry; `_load_ledger` swallowed an S3 error into an empty doc and
reported "realised $0.0, breached=False"; `live_instances` 0 and null rendered identically. So every field
here is TRI-STATE — read, or unreadable-with-a-reason — and a lane whose state cannot be read is
**UNKNOWN and loud**, never OK. `LaneState.unreadable` carries the reason; nothing coalesces to a default.

⚠ TWO ARTIFACTS ARE SHARED BETWEEN LANES AND MUST BE ATTRIBUTED BEFORE THEY ARE BELIEVED.
`ternary-vast-market-hold.json` is the `--gate-out` for every non-triangle ternary mode, so its `mode` key —
not its filename — says which lane it describes (`ternary_vast_launch._gate_what` exists because "a snapshot
naming the wrong experiment makes a triangle hold look like a replicate hold that had already been decided").
`relaunch-market-hold.json` is ONE file written by both the step-1 fan-out and the ternary watchdog, so its
`lane` key names the last writer, not a fixed lane. Reading either without checking attributes one lane's
health to another — a quiet way to vouch for a lane nobody measured.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
WHY THE SIGNAL IS NOT ARTIFACT AGE (the design constraint that shapes everything below)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
Measured scheduled delivery on 2026-07-27 was 141-238 min between ticks, so an honest AGE threshold must sit
above ~240 min — yet the real incident was 115 min stale and would have read FRESH throughout. Age alone
cannot detect this failure class, not as a tuning problem but by construction. `fleet_supervision_alarm.py`
already solved this for step-1 with a comparison that is immune to throttle:

    DID THE LAST COMPLETED RUN ADVANCE THE ARTIFACT'S OWN GENERATION STAMP PAST ITS OWN START?

This module REUSES that module rather than inventing a second answer to the same question — one fact, one
home (§1) — and applies it to every lane that has BOTH a dedicated tick workflow AND a repo-visible artifact
that tick writes. ONLY STEP-1 HAS BOTH. For the rest this module says so IN THE VERDICT
(`supervision.applicable: false`, with the reason) instead of substituting a weaker check and letting a
reader assume the strong one ran.

For lanes whose per-iteration census lives in the object store rather than in git, the condemning signal is
instead "this lane has hosts up and has produced NO new ledger/gate evidence in `active_evidence_min`" —
exactly the shape of failure 1 above (85 min of reassurance, zero new evidence). Every verdict carries
`census_basis` naming which of the two it rested on, because they are not equally strong.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
WHERE ITS VERDICT SURFACES
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
`.github/workflows/lane-staleness-watch.yml`, dispatched from `step1-fanout-supervisor.yml`'s in-job loop and
from the tail of `step1-fanout-autoscale.yml` under `if: always()` — NOT from a `schedule:`. CLAUDE.md §6: a
`schedule:` cron does not supervise a billing fleet. The cron on that workflow is a COLD-START path only and
says so. A FAILING verdict fails the run (GitHub emails the repo owner) and, when credentials are present,
also sends mail via `mailer.send_email`.

Usage:
    python3 lane_staleness_watch.py [--root DIR] [--history PATH] [--json OUT] [--now ISO8601Z]
                                    [--lane KEY]... [--no-api] [--write-history]
Exit 0 = every lane is either advancing or correctly parked. Exit 1 = at least one lane is stale or UNKNOWN.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: always US Eastern, 12-hour.

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HISTORY = os.path.join(HERE, "lane-staleness-history.json")

# ── thresholds ───────────────────────────────────────────────────────────────────────────────────────────
# ⚠ THESE ARE THIS MODULE'S OWN CONSTANTS, and nothing here re-types a threshold that already has a home
# (§1). In particular this module does NOT re-state `MAX_STOPPED_MIN` (it belongs to
# `ternary_vast_watchdog.stopped_and_billing` and the collector that acts on it), the buy line, the ladder
# basis, or any dollar figure — duplicating any of them would give one fact two homes free to disagree. The
# "has a tick even started" window is IMPORTED from `fleet_supervision_alarm` for the same reason.

# How long a lane WITH HOSTS UP may go without producing new evidence before that is an incident. Set from
# the measured failure, not from a cron: the valB cohort was dead for 85 minutes while its watchdog printed
# reassurance. 90 min is "the longest silence that incident could have produced and still been called normal".
DEFAULT_ACTIVE_EVIDENCE_MIN = 90.0
# How long a lane with NO hosts, unfinished work and nothing holding it may sit before that is an incident.
# The closure triangle sat 3 h. Every $0 stage in these lanes completes in minutes, so 45 min of nothing is
# already far outside any normal hand-off.
DEFAULT_IDLE_MIN = 45.0
# How long a REAL committed-iteration census may stay bit-identical while hosts are up. This is the strongest
# available signal and gets the tightest window: the step-1 census moves every few minutes per live unit.
DEFAULT_CENSUS_FLAT_MIN = 60.0

REPO = "trimcrae/Rare-cancers"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# tri-state reading
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
class LaneState:
    """Everything the watcher managed to learn about one lane, WITH the things it failed to learn.

    ★ THE `unreadable` DICT IS THE POINT. A field that could not be read is recorded as field -> why, and a
    lane with any DECISION-CRITICAL field in there is UNKNOWN, never OK. The alternative — defaulting to 0 /
    False / [] — is the defect that on 2026-07-27 turned a swallowed S3 error into "realised $0.0,
    breached=False" and a missing reverse leg into perfect antisymmetry.
    """

    def __init__(self, key: str, label: str, provider: str):
        self.key, self.label, self.provider = key, label, provider
        self.unreadable: dict[str, str] = {}
        self.live_hosts: int | None = None
        self.hosts_knowable = True                  # False when host liveness is provably not in git (GCP)
        self.host_states: dict[str, int] = {}       # cur_state histogram, REPORTED, never condemning
        self.unfinished: int | None = None
        self.finished: bool | None = None
        self.hold: bool | None = None
        self.hold_kind: str | None = None           # "price" | "needs-a-human" | "operator" — see _apply_hold
        self.hold_snapshot: str | None = None       # what PROVES the market was consulted
        self.hold_reason: str | None = None
        self.parked: list[str] = []                 # units deliberately off the watch list, with their reason
        self.last_evidence_utc: datetime.datetime | None = None
        self.last_evidence_what: str | None = None
        self.census: str | None = None            # a fingerprint, not a total — see read_step1
        self.census_what: str | None = None
        self.census_is_true_iteration_count = False  # only a real committed-iteration census condemns hard
        self.tick_workflow: str | None = None
        self.generation_artifact: str | None = None
        self.warnings: list[str] = []               # loud, but not by themselves a verdict
        self.notes: list[str] = []

    def as_dict(self) -> dict:
        return {
            "lane": self.key, "label": self.label, "provider": self.provider,
            "live_hosts": self.live_hosts, "hosts_knowable_from_git": self.hosts_knowable,
            "host_states": self.host_states or None,
            "unfinished": self.unfinished, "finished": self.finished,
            "hold": self.hold, "hold_kind": self.hold_kind,
            "hold_snapshot": self.hold_snapshot, "hold_reason": self.hold_reason,
            "parked_units": self.parked or None,
            "last_evidence_utc": _z(self.last_evidence_utc), "last_evidence_et": _et(self.last_evidence_utc),
            "last_evidence_what": self.last_evidence_what,
            "census": self.census, "census_what": self.census_what,
            "census_is_true_iteration_count": self.census_is_true_iteration_count,
            "tick_workflow": self.tick_workflow, "generation_artifact": self.generation_artifact,
            "unreadable": self.unreadable or None,
            "warnings": self.warnings or None, "notes": self.notes or None,
        }


def _et(ts: datetime.datetime | None) -> str | None:
    return ts.astimezone(ET).strftime("%-I:%M %p ET %b %-d, %Y") if ts else None


def _z(ts: datetime.datetime | None) -> str | None:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None


def _parse_z(s) -> datetime.datetime | None:
    """ISO-Z -> aware datetime, or None. Never raises: a malformed stamp is UNREADABLE, not 'the epoch'."""
    if not isinstance(s, str):
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            t = datetime.datetime.strptime(s, fmt)
            return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def load_json(root: str, name: str) -> tuple[dict | None, str | None]:
    """`(doc, why_not)`. A missing OR corrupt file returns a REASON, so nothing downstream can read the
    absence as an empty document — the `_load_ledger` defect, which reported a swallowed S3 error as
    "realised $0.0, breached=False"."""
    path = os.path.join(root, name)
    if not os.path.exists(path):
        return None, f"{name}: not present in the repo"
    try:
        with open(path) as fh:
            doc = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{name}: unreadable ({type(e).__name__}: {e})"
    if not isinstance(doc, dict):
        return None, f"{name}: not a JSON object"
    return doc, None


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# lane registry — declarative, so adding a lane is data, not a new code path
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★ WHY THE FIVE LANES ARE NAMED EXPLICITLY RATHER THAN DISCOVERED. A discovered list silently shrinks: a
# lane whose artifact is missing would simply not appear, and "not watched" would render exactly like
# "healthy". Naming them means a lane with no readable state produces UNKNOWN — loud — instead of nothing.
#
# ★ WHY `*_smoke` MODES ARE NOT LANE WORK. A smoke is the plumbing shakeout §6 requires before a fan-out
# (`mode=smoke` -> one real leg -> fleet). It is not a deliverable unit, so a spent smoke sitting disabled
# must not read as unfinished work — otherwise every lane that ever shook out would look permanently idle.
LANES: list[dict] = [
    {
        "key": "step1-fanout",
        "artifact_source": "fleet",
        "label": "Step 1 congeneric RBFE fan-out (Vast)",
        "provider": "vast",
        "tick_workflow": "step1-fanout-autoscale.yml",
        "generation_artifact": "step1-fanout-progress.json",
        "hold_artifact": "step1-fanout-market-hold.json",
        "relaunch_lane": "step1_fanout",
        "reader": "step1",
    },
    {
        "key": "ternary-valb-reps",
        "artifact_source": "ternary",
        "label": "valB_mini replicate legs r1+r2 (Vast)",
        "provider": "vast",
        "tick_workflow": "gpu-ternary-fep-vast.yml",
        "generation_artifact": None,   # the per-iteration census lives in S3, not in git — stated, not faked
        "hold_artifact": "ternary-vast-market-hold.json",
        "hold_modes": ["edge_reps"],
        "watch_modes": ["edge_reps"],
        "ledger_tokens": ["edge-reps", "reps-prime", "reduce-reps"],
        "terminal_artifact": "valb-replicate-reduction.json",
        # ★ PRODUCED SINCE 2026-08-01 by `gpu-ternary-fep-vast.yml`'s `reduce` job under `task=reduce-reps`,
        # which now copies `/tmp/tred/ternary_coop_reduction.json` into the repo and pushes it. Until that
        # step existed this name appeared at EXACTLY ONE site in the whole repo — the line above — so
        # `read_ternary_family`'s terminal-artifact route to FINISHED was unreachable for this lane alone,
        # and the reduction died with the runner. The `terminal_artifact_unbacked` marker that recorded the
        # gap is DELETED rather than left as a comment: the contract test fails a marker whose producer
        # exists, precisely so it cannot outlive the bug. Superseded, retained here in one line.
        "relaunch_lane": "ternary",
        "reader": "ternary_family",
    },
    {
        "key": "closure-triangle",
        "artifact_source": "ternary",
        "label": "valB closure triangle, 4 legs (Vast)",
        "provider": "vast",
        "tick_workflow": "gpu-ternary-fep-vast.yml",
        "generation_artifact": None,
        "hold_artifact": "valb-triangle-market-hold.json",
        "hold_modes": ["triangle"],
        "watch_modes": ["triangle"],
        "ledger_tokens": ["triangle-prime", "triangle-gate", "triangle-smoke", "triangle-reduce",
                          "task=triangle"],
        "terminal_artifact": "valb-triangle-reduction.json",
        "reader": "ternary_family",
    },
    {
        "key": "rung-5aks",
        "artifact_source": "ternary",
        "label": "RUNG 5a-KS ternary legs, NR4A3 + NR4A1 (Vast)",
        "provider": "vast",
        "tick_workflow": "gpu-ternary-fep-vast.yml",
        "generation_artifact": None,
        "hold_artifact": "ternary-vast-market-hold.json",
        "hold_modes": ["5aks"],
        "watch_modes": ["5aks"],
        "ledger_tokens": ["5aks"],
        "terminal_artifact": "nr4a3-5aks-reduction.json",
        "reader": "ternary_family",
    },
    {
        # ★★ ADDED 2026-07-31 — the lane that had NO automation at all. `fusion-cpu-extras.yml` is
        # dispatch-only and is the only workflow that runs it, `vast_idle_guard` had never been pointed at
        # `nrv04retro-`, and nothing re-placed a hostless leg. It now ticks from
        # `step1-fanout-supervisor.yml` (the cadence GitHub's scheduler does not deliver) via
        # `retro_collect`, which reaps, nudges, guards, re-places and writes the fragment read here.
        # Registering it is what makes "the retro tick stopped" LOUD instead of merely absent — the exact
        # property this module's docstring says a discovered list silently loses.
        "key": "nrv04-retro",
        "artifact_source": "fleet",
        "label": "NR-V04 retrospective Arm E / R1, 18 endpoint-MD legs (Vast)",
        "provider": "vast",
        "tick_workflow": "fusion-cpu-extras.yml",
        "generation_artifact": "inflight-board.d/nrv04-retro.json",
        "hold_artifact": "nrv04-retro-market-hold.json",
        "reader": "nrv04_retro",
    },
    {
        # ★★ ADDED 2026-08-01, THE DAY IT FAILED — the lane that was registered with NOTHING. Built that
        # morning, it appeared in no cross-lane watcher, so when its tick stopped at 10:14 AM ET with two
        # hosts rented (one of which had `exited` by 10:54 AM) there was nothing that could have said so.
        # Registering it is what turns "the selcal tick stopped" into a LOUD verdict instead of an absence —
        # the exact property this registry's docstring says a discovered list silently loses. See
        # `read_selcal` for why its hosts are not knowable from git and which module covers that side.
        "key": "selcal-cofold",
        "artifact_source": "ternary",
        "label": "Selectivity control — SMARCA2/4 co-fold panel (Vast)",
        "provider": "vast",
        "tick_workflow": "selectivity-control-vast.yml",
        # Deliberately absent, stated not faked: `selcal-cofold-census.json` carries no `_generated_utc`, so
        # `fleet_supervision_alarm`'s FULL generation-advance test cannot run against it and claiming it
        # would be claiming a check that did not happen. `supervision_for` reports the REDUCED question.
        "generation_artifact": None,
        "hold_artifact": "selcal-market-hold.json",
        "reader": "selcal",
    },
    {
        # ★★ ADDED 2026-08-02, THE NIGHT IT COST 4.5 BILLED HOURS. The lane above covers the CO-FOLD stage
        # only. The 24-unit endpoint-MD panel that follows it — 55 rentals and every dollar this lane has
        # ever spent — was registered NOWHERE, so while three hosts sat at `gpu_util: 0.0` producing nothing,
        # the only selcal row on the board read `FINISHED … nothing is billing`. That sentence was true of
        # the co-fold stage and false of the lane, and a true sentence about the wrong half is worse than
        # silence: it is a green light with evidence attached. Registering the MD panel is what turns
        # "3 hosts, 0 landed, hours" into a row instead of an absence.
        "key": "selcal-md",
        "artifact_source": "ternary",
        "label": "Selectivity control — SMARCA2/4 endpoint-MD panel (Vast)",
        "provider": "vast",
        "tick_workflow": "selectivity-control-vast.yml",
        # Deliberately absent, stated not faked — and for a DIFFERENT reason than the co-fold lane's. The
        # artifacts here do carry a stamp, but `selectivity-control-vast.yml` is MULTIPLEXED across ~20
        # modes: a `diag` or `manifest` run completes green and writes no reap artifact, so the generation-
        # advance test would read "a completed run did not refresh the artifact" and cry FAILING at a
        # workflow behaving exactly as designed. An alarm that fires on correct behaviour is the same end
        # state as no alarm, so `supervision_for` reports the REDUCED question with its own label.
        "generation_artifact": None,
        "hold_artifact": "selcal-market-hold.json",
        "reader": "selcal_md",
    },
    {
        "key": "gcp-ternary-watch",
        "artifact_source": "ternary",
        "label": "GCP ternary watch list — reverse leg now, restrained binary re-run next (us-central1 only)",
        "provider": "gcp",
        "tick_workflow": "ternary-leg-watchdog.yml",
        "generation_artifact": None,
        "watch_file": "ternary-watch.json",
        "reader": "gcp_watch",
    },
]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# readers — one per artifact shape. Each is PURE over already-loaded dicts, so it is testable without files.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def read_step1(spec: dict, progress: dict | None, prog_err: str | None,
               hold: dict | None, hold_err: str | None) -> LaneState:
    """The one lane with a TRUE committed-iteration census in git: `sum(units[].committed_scalar)`.

    That sum is the only signal in this whole module allowed to condemn a lane hard, and it is exactly the
    signal CLAUDE.md §6 names — "only the committed-iteration census condemns". `gpu_util` and
    `instance_states` sit in the same file and `gpu_util` is deliberately never touched.
    """
    st = LaneState(spec["key"], spec["label"], spec["provider"])
    st.tick_workflow, st.generation_artifact = spec["tick_workflow"], spec["generation_artifact"]

    if progress is None:
        st.unreadable["progress"] = prog_err or "unknown"
        return st

    gen = _parse_z(progress.get("_generated_utc"))
    if gen is None:
        st.unreadable["_generated_utc"] = "absent or unparseable in step1-fanout-progress.json"
    else:
        st.last_evidence_utc, st.last_evidence_what = gen, "step1-fanout-progress.json `_generated_utc`"

    # `_vast_unreadable` is the lane's OWN admission that it could not read the Vast board this tick. If it
    # is set, `live_instances` is not a measurement and must not be treated as one.
    if progress.get("_vast_unreadable"):
        st.unreadable["live_hosts"] = (f"the tick recorded `_vast_unreadable`: {progress['_vast_unreadable']}"
                                       f" — live_instances is not a measurement this tick")
    else:
        live = progress.get("live_instances")
        if isinstance(live, int):
            st.live_hosts = live
        else:
            st.unreadable["live_hosts"] = "`live_instances` absent or non-integer (0 and null are NOT the same)"

    n_units, n_done = progress.get("n_units"), progress.get("n_complete")
    if isinstance(n_units, int) and isinstance(n_done, int):
        st.unfinished = n_units - n_done
        st.finished = st.unfinished <= 0
    else:
        st.unreadable["unfinished"] = "`n_units` / `n_complete` absent or non-integer"

    states = progress.get("instance_states")
    if isinstance(states, dict):
        st.host_states = {k: v for k, v in states.items() if isinstance(v, int)}

    units = progress.get("units")
    if isinstance(units, list) and units:
        # ★ THE CENSUS IS A PER-UNIT FINGERPRINT, NOT A SUM. Two reasons, both learned here:
        #   1. A SUM CANNOT REPRESENT A NULL. A unit that has not committed anything yet legitimately carries
        #      `committed_scalar: null`, and there is almost always at least one — so a sum that refuses nulls
        #      is unavailable exactly when the fleet is busiest, and a sum that coerces them to 0 is the
        #      absent-as-a-value defect again. Nulls are carried verbatim here and compare equal to nulls.
        #   2. A SUM CAN HIDE A REGRESSION. One unit going backwards while another advances leaves the total
        #      unchanged. Element-wise, any movement anywhere changes the fingerprint, which is the question
        #      being asked: HAS ANYTHING ADVANCED.
        pairs = sorted((str(u.get("unit_id")), u.get("committed_scalar"))
                       for u in units if isinstance(u, dict))
        committing = sum(1 for _, s in pairs if isinstance(s, (int, float)))
        # Stored as a DIGEST, not as the pairs themselves. The history file is committed back to the fleet
        # branch on every run, and a 19-unit blob would rewrite ~2 kB of JSON each time — a diff nobody can
        # read, on the branch three lanes are already pushing to. The digest compares exactly and the human
        # summary lives beside it in `census_what`.
        st.census = hashlib.sha256(json.dumps(pairs, sort_keys=True).encode()).hexdigest()[:16]
        st.census_what = (f"per-unit committed_scalar fingerprint over {len(pairs)} units "
                          f"({committing} with commits so far)")
        st.census_is_true_iteration_count = True
    else:
        st.unreadable["census"] = "`units` absent or empty in step1-fanout-progress.json"

    _apply_hold(st, hold, hold_err, held_key="held", reason_key="held_reason",
                depth_key="board_depth", offers_key="offers_priced", source=spec.get("hold_artifact"))
    return st


def read_ternary_family(spec: dict, watch: dict | None, watch_err: str | None,
                        hold: dict | None, hold_err: str | None,
                        ledger: dict | None, ledger_err: str | None,
                        terminal_present: bool | None) -> LaneState:
    """The three Vast lanes that share `ternary-vast-watch.json` and the launch ledger.

    ★ THE WATCH LIST IS THE PARKED/FINISHED ORACLE, and it already encodes the distinction this module needs.
    `ternary-vast-watch.json` -> `_parked_is_not_finished`: `_disabled_why` names a LANDED artifact (the unit
    is done); `_parked_why` means the unit is INTERRUPTED, its checkpoint intact, its work NOT done, and it is
    off the watch list only because a relaunch is a new purchase facing the buy line. Those are opposite
    states wearing the same `enabled: false`, and reading them as one is how a parked-but-unfinished lane
    would render as finished — the failure this module exists to catch. An entry carrying NEITHER key is
    graded UNREADABLE rather than guessed at.

    ⚠ NO PER-ITERATION CENSUS IS AVAILABLE HERE. The Vast ternary watchdog keeps its progress counters in S3
    (`<prefix>/watchdog/progress-<uid>.json`), not in git, and this module will not grow an S3 credential to
    reach them — that would make the alarm die with the same credential the lanes die with, and a dead
    credential is one of the failures it exists to report (5a-KS, 53 min at 0 % GPU). So the condemning
    signal for these lanes is the WEAKER one, and `census_basis` says so on every run rather than letting a
    reader assume the strong check ran.
    """
    st = LaneState(spec["key"], spec["label"], spec["provider"])
    st.tick_workflow, st.generation_artifact = spec["tick_workflow"], spec.get("generation_artifact")
    st.notes.append("no committed-iteration census in git for this lane (it lives in S3) — condemnation here "
                    "rests on evidence age with hosts up, which is a weaker signal and is labelled as one")

    modes = set(spec.get("watch_modes") or [])
    if watch is None:
        st.unreadable["watch_list"] = watch_err or "unknown"
    else:
        entries = watch.get("watch")
        if not isinstance(entries, list):
            st.unreadable["watch_list"] = "`watch` key absent or not a list"
        else:
            mine = [e for e in entries if isinstance(e, dict) and e.get("mode") in modes]
            enabled = [e for e in mine if e.get("enabled") is True]
            parked = [e for e in mine if e.get("enabled") is not True and e.get("_parked_why")]
            landed = [e for e in mine if e.get("enabled") is not True and e.get("_disabled_why")]
            ambiguous = [e for e in mine if e.get("enabled") is not True
                         and not e.get("_parked_why") and not e.get("_disabled_why")]
            st.parked = [f"{e.get('unit_id')}: {str(e.get('_parked_why'))[:180]}" for e in parked]
            if ambiguous:
                st.unreadable["watch_entry_intent"] = (
                    f"{len(ambiguous)} unit(s) are enabled=false with neither `_parked_why` nor "
                    f"`_disabled_why`: " + ", ".join(str(e.get("unit_id")) for e in ambiguous[:4]) +
                    " — parked-but-unfinished and finished are opposite states (see the watch list's own "
                    "`_parked_is_not_finished`) and cannot be told apart here")
            st.notes.append(f"watch list: {len(enabled)} enabled, {len(parked)} parked, {len(landed)} landed "
                            f"(modes {sorted(modes)})")
            if mine:
                st.unfinished = len(enabled) + len(parked)
                st.finished = (st.unfinished == 0)

    # The gate snapshot is the live-host and price-hold oracle. It is per-MODE, so a snapshot written for a
    # DIFFERENT lane must not be read as this lane's state — that would let one lane's healthy gate vouch for
    # another's silence. `_gate_what` in the writer exists for exactly this reason.
    hold_modes = set(spec.get("hold_modes") or [])
    gate_utc: datetime.datetime | None = None
    if hold is None:
        st.hold, st.hold_kind = False, None
        st.hold_reason = f"{spec.get('hold_artifact')}: {hold_err or 'not present'} — no gate snapshot exists"
        st.notes.append(st.hold_reason)
    elif hold.get("mode") not in hold_modes:
        st.hold, st.hold_kind = False, None
        st.hold_reason = (f"the most recent {spec.get('hold_artifact')} is stamped mode="
                          f"{hold.get('mode')!r}, which is NOT this lane ({sorted(hold_modes)}) — not read "
                          f"as this lane's state")
        st.notes.append(st.hold_reason)
    else:
        _apply_hold(st, hold, hold_err, held_key="hold", reason_key="reason",
                    depth_key="depth", offers_key="offers", source=spec.get("hold_artifact"))
        live = hold.get("units_live")
        if isinstance(live, list):
            st.live_hosts = len(live)
            rates = hold.get("live_host_rates")
            if isinstance(rates, list):
                hist: dict[str, int] = {}
                for r in rates:
                    if isinstance(r, dict):
                        hist[str(r.get("cur_state"))] = hist.get(str(r.get("cur_state")), 0) + 1
                st.host_states = hist
        else:
            st.unreadable["live_hosts"] = "`units_live` absent or not a list in the gate snapshot"
        gate_utc = _parse_z(hold.get("utc"))
        if gate_utc:
            st.last_evidence_utc, st.last_evidence_what = gate_utc, f"{spec.get('hold_artifact')} `utc`"

    # ★ THE LEDGER IS THE PER-LANE "NEW EVIDENCE" CLOCK. `ternary-vast-launch-attempts.json` records every
    # gate evaluation, rental and dispatch with a `stage` and a `reason` naming the task, so a lane's own
    # activity can be separated from a sibling's on the SAME workflow — which matters because
    # `gpu-ternary-fep-vast.yml` serves all three of these lanes, and a triangle run must not vouch for the
    # replicate lane's silence.
    tokens = [t.lower() for t in (spec.get("ledger_tokens") or [])]
    ledger_seen, newest_outcome = False, ""
    if ledger is None:
        st.unreadable["ledger"] = ledger_err or "unknown"
    else:
        attempts = ledger.get("attempts")
        if not isinstance(attempts, list):
            st.unreadable["ledger"] = "`attempts` key absent or not a list"
        else:
            best, best_e = None, None
            for a in attempts:
                if not isinstance(a, dict):
                    continue
                blob = " ".join(str(a.get(k) or "") for k in ("stage", "reason", "outcome")).lower()
                if not any(t in blob for t in tokens):
                    continue
                t = _parse_z(a.get("utc"))
                if t and (best is None or t > best):
                    best, best_e = t, a
            ledger_seen = best is not None
            newest_outcome = str((best_e or {}).get("outcome") or "").lower()
            if best and (st.last_evidence_utc is None or best > st.last_evidence_utc):
                st.last_evidence_utc = best
                st.last_evidence_what = (f"launch ledger: stage={best_e.get('stage')!r} "
                                         f"outcome={best_e.get('outcome')!r}")
            elif best:
                st.notes.append(f"launch ledger last touched this lane {_et(best)} "
                                f"(stage={best_e.get('stage')!r} outcome={best_e.get('outcome')!r})")
            else:
                st.notes.append("the launch ledger has never recorded a stage for this lane")

    # ★★ A GATE SNAPSHOT OLDER THAN THE LANE'S LAST RENTAL IS NOT A HOST COUNT. Measured while building this
    # module: `ternary-vast-market-hold.json` read `units_live: []` at 3:38 PM ET, and the ledger recorded a
    # successful rental for the same lane at 4:00 PM ET. Believing the snapshot would have announced a lane
    # with four freshly-rented hosts as IDLE-UNEXPECTED — a false alarm on the exact verdict this module
    # exists to make trustworthy. A superseded count is UNREADABLE, not zero; the same rule as everywhere
    # else here, applied to staleness rather than to absence.
    if (gate_utc is not None and st.live_hosts is not None
            and st.last_evidence_utc is not None and st.last_evidence_utc > gate_utc):
        if newest_outcome in ("launched", "dispatched"):
            # ★ THE SNAPSHOT WAS SUPERSEDED **UPWARD**, AND THAT IS NOT AN ABSENCE OF KNOWLEDGE. A
            # successful rental is the strongest positive evidence of a host there is — so the count is a
            # LOWER BOUND, not an unknown, and the lane is billing whatever the exact number.
            #
            # CAUGHT BY RUNNING IT (first CI dispatch, 6:42 PM ET 2026-07-27): the replicate lane went red
            # because its gate snapshot was stamped 6:20 PM and its ledger recorded a successful rental at
            # 6:25 PM. It had JUST RENTED FOUR HOSTS — the healthiest thing a lane can do — and the watcher
            # announced that it could not tell billing from idle. Every rental would have produced a red
            # window until the next gate evaluation, which is exactly the cry-wolf failure this module is
            # supposed to avoid. Being loud about a genuine unknown is the rule; manufacturing one is not.
            st.live_hosts = max(st.live_hosts, 1)
            st.notes.append(f"host count is a LOWER BOUND: the gate snapshot ({_et(gate_utc)}) predates a "
                            f"successful rental at {_et(st.last_evidence_utc)}, so there are at least this "
                            f"many hosts and possibly more — enough to know the lane is billing")
        else:
            st.unreadable["live_hosts"] = (
                f"the gate snapshot giving the host count is stamped {_et(gate_utc)}, but this lane produced "
                f"newer evidence at {_et(st.last_evidence_utc)} ({st.last_evidence_what}, outcome="
                f"{newest_outcome or 'unknown'!r}) — something changed after the snapshot and it was not a "
                f"rental, so `units_live` is superseded and is NOT a current host count")
            st.live_hosts = None

    # `terminal_present` is tri-state on purpose: None means "the caller could not check", which is not the
    # same as "the lane has not finished".
    if terminal_present is True:
        st.finished, st.unfinished = True, 0
        st.notes.append(f"terminal artifact {spec.get('terminal_artifact')} is present — lane complete")
    elif terminal_present is None:
        st.unreadable["finished"] = f"could not determine whether {spec.get('terminal_artifact')} exists"
    elif st.unfinished is None and ledger_seen:
        # ★★ THE CLOSURE-TRIANGLE SHAPE, AND THE REASON THIS BRANCH EXISTS. No watch entry, no terminal
        # artifact — but the ledger PROVES this lane was started. A lane with no live instance at all is what
        # every liveness check reads as "nothing to watch", and it is indistinguishable from finished unless
        # someone asks whether its terminus landed. Asserting unfinished here is what lets the idle branch
        # fire on the failure that currently has no detector.
        st.unfinished, st.finished = 1, False
        st.notes.append(f"no watch entry and no {spec.get('terminal_artifact')}, but the launch ledger shows "
                        f"this lane ran — so it is STARTED AND NOT FINISHED, with nothing watching it")
        if st.live_hosts is None:
            st.live_hosts = 0
    return st


def read_nrv04_retro(spec: dict, frag: dict | None, frag_err: str | None,
                     hold: dict | None, hold_err: str | None) -> LaneState:
    """The NR-V04 retrospective (Arm E / R1). Graded off the lane's own in-flight-board FRAGMENT, which its
    tick (`nrv04_vast_launch.retro_collect`) commits on every pass.

    ⚠ WHY THE FRAGMENT AND NOT A LEG COUNT. The leg records live in S3; nothing about them is in git. The
    fragment is the only repo-visible fact, and it carries exactly the two things that matter: WHEN the tick
    last ran (`generated_utc` — so a lane whose supervision stopped is loud rather than absent, which is the
    whole reason this lane is registered) and WHICH units still have no host (`rows[].state`).

    ⚠ `live_hosts` IS COUNTED FROM ROW STATE, NOT ASSUMED. A row is only emitted for a unit that has NOT
    landed, so `len(rows)` is the outstanding count and the non-`NO HOST` rows are the placed ones. A landed
    leg is deliberately not rowed (`retro_board_rows`), so this can never read a finished panel as idle —
    `note` carries the landed count and `finished` is decided by there being no rows left.
    """
    st = LaneState(spec["key"], spec["label"], spec["provider"])
    st.tick_workflow, st.generation_artifact = spec["tick_workflow"], spec["generation_artifact"]
    if frag is None:
        st.unreadable["board_fragment"] = frag_err or "unknown"
        return st
    gen = _parse_z(frag.get("generated_utc"))
    if gen is None:
        st.unreadable["generated_utc"] = "absent or unparseable in the board fragment"
    else:
        st.last_evidence_utc = gen
        st.last_evidence_what = "the lane's own tick wrote its in-flight-board fragment"
    rows = frag.get("rows")
    if not isinstance(rows, list):
        st.unreadable["rows"] = "`rows` absent or not a list"
        return st
    states = {}
    for r in rows:
        if isinstance(r, dict):
            states[str(r.get("state"))] = states.get(str(r.get("state")), 0) + 1
    st.host_states = states
    st.unfinished = len(rows)
    st.finished = (len(rows) == 0)
    st.live_hosts = sum(n for s, n in states.items() if s not in ("NO HOST", "None"))
    # A fingerprint, NOT a total — same discipline as read_step1: it says whether the picture CHANGED
    # between ticks, and it is explicitly not a committed-iteration census, so it never condemns hard.
    st.census = "%d outstanding / %s" % (len(rows), ",".join(f"{k}:{v}" for k, v in sorted(states.items())))
    st.census_what = "outstanding legs by board state (NOT an iteration census)"
    st.census_is_true_iteration_count = False
    if frag.get("note"):
        st.notes.append(str(frag["note"])[:200])
    st.notes.append("re-placement is automatic: retro_collect nudges, guards, and re-buys hostless unrun "
                    "units behind the same $/ns buy line, bounded by nrv04_vast_launch.retro_breaker")
    if hold is None:
        st.hold, st.hold_reason = False, (hold_err or "no market-hold snapshot committed — the lane has not "
                                                      "held on price since its last tick")
    else:
        st.hold = bool(hold.get("hold"))
        st.hold_kind = "price" if st.hold else None
        st.hold_snapshot = spec.get("hold_artifact")
        st.hold_reason = str(hold.get("reason") or "")[:240]
    return st


def read_selcal(spec: dict, census: dict | None, census_err: str | None,
                hold: dict | None, hold_err: str | None) -> LaneState:
    """The selectivity-control co-fold lane (SMARCA2/4), graded off `selcal-cofold-census.json`.

    ★★ WHY THIS LANE IS HERE AT ALL (2026-08-01). It was built that morning and registered with NOTHING. On
    the day it went live it rented two hosts, stopped reporting at 10:14 AM ET, and nothing noticed for 40+
    minutes — by 10:54 AM one of the two had already `exited` while the other still ran. Its watch job was
    `in_progress` with a successor `pending`, so its supervisor LOOKED alive while producing no ticks. This
    module could not have caught it, because an unregistered lane does not render as unwatched — it renders
    as nothing at all, which is exactly the property the registry docstring says a discovered list loses.

    ⚠ ITS HOST COUNT IS NOT IN GIT, AND THAT IS STATED RATHER THAN GUESSED. The co-fold census carries a
    `phase` string naming ONE instance and no host list; `selcal-market-hold.json`'s `n_hosts` is what the
    gate wanted to BUY, not what is up, and reading it as a host count would be a populated field masquerading
    as a measured one (§4). So `hosts_knowable` is False and this lane is graded on whether its tick is
    DELIVERING, exactly like the GCP lane — grading it UNKNOWN on every run instead would be an alarm that is
    always red, which is the same end state as no alarm.

    ★ THE HOST SIDE IS COVERED, BUT NOT BY THIS MODULE. `account_orphan_alarm.py` reads the same lane from the
    VAST ACCOUNT (`ternary-vast-account-census.json`), where the hosts are visible whatever this lane commits,
    and alarms on the pair "stale lane WITH hosts". The two are complementary by construction and neither is
    sufficient alone: this one knows what the lane is SUPPOSED to be doing, that one knows what the account is
    actually holding. Deliberately no import in either direction — an alarm that shares a dependency with the
    thing it watches dies with it, and that module is the backstop for THIS module's driver stalling.

    ⚠ THE FRESHNESS STAMP IS EXTRACTED FROM `phase`, NOT FROM A TIMESTAMP KEY, because the census has none:
    `"done rc=0 2026-08-01T14:41:08Z instance=46508454 attempt=20260801T144027Z"`. That IS a real tick stamp —
    only a run that executed writes it — which is why it is read rather than defaulted. It is also why this
    lane declares `generation_artifact: None`: `fleet_supervision_alarm`'s FULL generation-advance test keys
    on `_generated_utc`, which this artifact does not have, so claiming the strong test would be claiming a
    check that cannot run. The registry's existing "deliberately absent, stated not faked" convention is used
    instead, and `supervision_for` reports the REDUCED question with its own label.
    """
    st = LaneState(spec["key"], spec["label"], spec["provider"])
    st.tick_workflow, st.generation_artifact = spec["tick_workflow"], spec.get("generation_artifact")
    st.hosts_knowable = False
    st.notes.append("host liveness is NOT in git for this lane (the co-fold census carries no host list, and "
                    "the gate's `n_hosts` is what it wanted to buy, not what is up) — graded on whether its "
                    "tick is delivering; the ACCOUNT-keyed view of its hosts is account_orphan_alarm.py")

    if census is None:
        st.unreadable["progress"] = census_err or "unknown"
    else:
        phase = census.get("phase")
        stamp = None
        if isinstance(phase, str):
            m = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", phase)
            stamp = _parse_z(m.group(0)) if m else None
        if stamp is None:
            st.unreadable["progress"] = ("`phase` in selcal-cofold-census.json carries no parseable ISO-Z "
                                         "stamp, so when this lane last ticked cannot be read")
        else:
            st.last_evidence_utc = stamp
            st.last_evidence_what = "selcal-cofold-census.json `phase` (the tick's own completion stamp)"
            if isinstance(phase, str):
                st.notes.append(f"last tick phase: {phase[:120]}")

        missing = census.get("missing")
        complete = census.get("complete")
        if isinstance(missing, list) and isinstance(complete, bool):
            # `complete` is the writer's own verdict and `missing` is its evidence; they are read TOGETHER so
            # a disagreement surfaces instead of one silently winning.
            st.unfinished = len(missing)
            st.finished = complete and not missing
            if complete and missing:
                st.warnings.append(f"⚠ the co-fold census says `complete: true` while still listing "
                                   f"{len(missing)} missing model(s) — the writer's verdict and its own "
                                   f"evidence disagree, and neither is believed over the other here")
            per_arm = census.get("n_models_per_arm")
            if isinstance(per_arm, dict):
                st.census = ",".join(f"{k}:{v}" for k, v in sorted(per_arm.items()))
                st.census_what = "models landed per arm (NOT an iteration census)"
                st.census_is_true_iteration_count = False
                st.notes.append(f"models per arm: {st.census}")
        else:
            st.unreadable["unfinished"] = ("`missing` / `complete` absent or of the wrong type in "
                                           "selcal-cofold-census.json")

    _apply_hold(st, hold, hold_err, held_key="hold", reason_key="reason",
                depth_key="board_depth", offers_key="offers_priced", source=spec.get("hold_artifact"))
    return st


def banked_leg_minutes(rentals: list | None) -> list:
    """The rentals that BANKED a leg, as sorted durations in minutes. Generic ledger arithmetic — no lane
    knowledge, so it stays on the safe side of this module's no-lane-imports rule while being the ONE home
    of the selection rule that both `overrun_budget_min` (the watcher's warning) and `selcal_board.md_rows`
    (the board's ETA) stand on. If those two ever selected differently, the board would promise an ETA the
    watcher was simultaneously calling an overrun."""
    return sorted(r["uptime_s"] / 60.0 for r in (rentals or ())
                  if isinstance(r, dict) and "work banked" in str(r.get("why") or "")
                  and isinstance(r.get("uptime_s"), (int, float)) and r["uptime_s"] > 0)


def p90_minutes(mins: list) -> float | None:
    """p90 of an already-sorted duration list. Trivial, and it has one home for exactly that reason: it is
    quoted in a board cell AND in a lane warning, and two copies would drift by an off-by-one nobody reads."""
    return mins[min(len(mins) - 1, int(round(0.9 * (len(mins) - 1))))] if mins else None


def overrun_budget_min(rentals: list | None) -> tuple[float | None, str]:
    """This lane's OWN measured rental duration, p90, from its price ledger -> (minutes, how) or (None, why).

    ⛔ DERIVED, NEVER TYPED (CLAUDE.md §1). The obvious implementation is a constant — "warn past 90 min" —
    and it would be wrong within a week: leg length depends on the card, the system size and the sampling
    length, all of which move. The lane already records the duration of every rental it has ever made, so the
    honest budget is its own distribution. On the night this was written the ledger held 55 rentals with
    median 30.3 min and p90 69.4 min, against which the three dead hosts sat at 275, 122 and 40.

    ⚠ IT REFUSES ON A SHORT LEDGER rather than returning a shape read off three points. A budget computed
    from too little data is a number that LOOKS measured, which §4 says is the more dangerous kind.

    ⚠⚠ AND IT COUNTS ONLY RENTALS THAT BANKED WORK — the first draft counted ALL of them, and that was the
    same populated-vs-measured error one layer up. Measured on this lane: 58 rentals give median 34.1 / p90
    69.5 min, but 36 of those never produced a leg (median 13.2 min — hosts that refused, crash-looped or
    died), and the 22 that actually finished one give median 42.3 / p90 55.8. "How long does the work take"
    is a question only the rentals that did the work can answer; the failures drag the median DOWN, which
    makes the budget look tighter while being built mostly from things that never ran.
    """
    if not isinstance(rentals, list):
        return None, "the price ledger is unreadable, so this lane has no measured duration to judge against"
    ups = banked_leg_minutes(rentals)
    if len(ups) < 8:
        return None, (f"only {len(ups)} rental(s) that BANKED A LEG are on record (of {len(rentals)} total) — "
                      f"too few to derive a duration budget, and a p90 of three points is a guess wearing a "
                      f"statistic's clothes. Rentals that never produced a leg are deliberately excluded: "
                      f"they measure how fast this lane FAILS, not how long its work takes")
    p90 = p90_minutes(ups)
    return p90, (f"p90 of the {len(ups)} rental(s) that BANKED a leg in selcal-price-ledger.json "
                 f"(median {ups[len(ups)//2]:.1f} min); {len(rentals) - len(ups)} non-banking rental(s) "
                 f"excluded as measuring failure rather than work")


def read_selcal_md(spec: dict, reap: dict | None, reap_err: str | None,
                   coll: dict | None, coll_err: str | None,
                   ledger: dict | None, ledger_err: str | None,
                   hold: dict | None, hold_err: str | None) -> LaneState:
    """The selectivity-control ENDPOINT-MD panel — the half of this lane that actually bills.

    ★★ HOST LIVENESS *IS* KNOWABLE HERE, unlike the co-fold lane above, and that difference is the point.
    `selcal-reap.json` names every instance the reaper saw on its last tick, with its label, status and
    uptime, so this lane can be graded on hosts rather than only on whether its tick is alive. It is the one
    selcal row that can answer "what is billing right now".

    ⚠ AND IT WARNS ON A HOST THAT HAS OUTLIVED THE LANE'S OWN p90 WITHOUT LANDING — the observation that had
    to be made BY HAND on 2026-08-02, from a median and a p90 computed ad hoc at a terminal, four and a half
    hours after the first host stopped working. Nothing in the repo was going to say it. A warning is NOT a
    condemnation and reaps nothing: `reap_decision` destroys on host-written evidence only, and an overrun is
    a reason to go and LOOK (`--mode diag`), which is exactly what turned this one into a diagnosis.
    """
    st = LaneState(spec["key"], spec["label"], spec["provider"])
    st.tick_workflow, st.generation_artifact = spec["tick_workflow"], spec.get("generation_artifact")

    if reap is None:
        st.unreadable["hosts"] = reap_err or "unknown"
    else:
        stamp = _parse_z(reap.get("utc"))
        if stamp is None:
            st.unreadable["reap_utc"] = "`utc` absent or unparseable in selcal-reap.json"
        else:
            st.last_evidence_utc = stamp
            st.last_evidence_what = "selcal-reap.json `utc` (the reaper writes it on every tick, reaping "
            st.last_evidence_what += "nothing included)"
        spared = reap.get("spared") if isinstance(reap.get("spared"), list) else []
        st.live_hosts = len(spared)
        states: dict = {}
        for s in spared:
            if isinstance(s, dict):
                states[str(s.get("status"))] = states.get(str(s.get("status")), 0) + 1
        st.host_states = states

        budget, how = overrun_budget_min([] if ledger is None else ledger.get("rentals"))
        if budget is None:
            if spared:
                st.notes.append(f"no overrun budget could be derived — {how}")
        else:
            st.notes.append(f"overrun budget {budget:.0f} min ({how})")
            for s in spared:
                if not isinstance(s, dict):
                    continue
                up = s.get("uptime_min")
                if isinstance(up, (int, float)) and up > budget:
                    st.warnings.append(
                        f"⚠ {s.get('label')} (instance {s.get('instance')}) has been up {up:.0f} min against "
                        f"this lane's own {budget:.0f} min p90 and has landed nothing — that is "
                        f"{up / budget:.1f}x. NOT a condemnation and nothing reaps on it; it is a reason to "
                        f"run `--mode diag` and read the host's banked run.log, which is what found a "
                        f"deterministic input-audit refusal on 2026-08-02.")

    if coll is None:
        st.unreadable["progress"] = coll_err or "unknown"
    else:
        exp, landed = coll.get("expected"), coll.get("landed")
        missing = coll.get("missing")
        if isinstance(exp, int) and isinstance(landed, int):
            st.unfinished = max(0, exp - landed)
            st.census = f"{landed}/{exp} legs banked in S3"
            st.census_what = "landed production-conforming legs (NOT an iteration census)"
            st.census_is_true_iteration_count = False
        else:
            st.unreadable["landed"] = "`expected` / `landed` absent or of the wrong type in selcal-collect.json"
        # `panel_complete` is the collector's own verdict and `missing` is its evidence — read TOGETHER, so a
        # disagreement surfaces rather than one silently winning. Same discipline as `read_selcal`.
        complete = coll.get("panel_complete")
        if isinstance(complete, bool):
            st.finished = complete
            if complete and missing:
                st.warnings.append(f"⚠ selcal-collect.json says `panel_complete: true` while still listing "
                                   f"{len(missing)} missing unit(s) — the writer's verdict and its own "
                                   f"evidence disagree, and neither is believed over the other here")
        if isinstance(missing, list) and missing:
            st.notes.append("still owed: " + ", ".join(str(m) for m in missing[:6])
                            + ("…" if len(missing) > 6 else ""))

    # What was DELIBERATELY dropped, so a shrunken panel never reads as a finished one.
    # ⛔ READ FROM THE ARTIFACT, NEVER BY IMPORTING `selcal_panel`. This watcher imports nothing from the
    # lanes it watches (`test_it_imports_nothing_from_the_lanes_it_watches`) for a reason that is exactly the
    # point of a watcher: a module that can be taken down by the lane it is watching goes dark at the moment
    # the lane breaks. The collector knows the exclusions and writes them into its own record; this only
    # reports them. (Caught by that test on the first draft of this reader, which did import it.)
    excl = (coll or {}).get("excluded_cofold_models")
    if isinstance(excl, dict):
        for k, why in sorted(excl.items()):
            st.parked.append(f"{k} — {str(why)[:180]}")
    elif coll is not None:
        st.notes.append("selcal-collect.json names no `excluded_cofold_models` — either nothing is excluded "
                        "or the collector predates recording it; the two are NOT distinguished here")

    _apply_hold(st, hold, hold_err, held_key="hold", reason_key="reason",
                depth_key="board_depth", offers_key="offers_priced", source=spec.get("hold_artifact"))
    return st


def read_gcp_watch(spec: dict, watch: dict | None, watch_err: str | None) -> LaneState:
    """The GCP lane. Its watchdog (`ternary-leg-watchdog.yml`) keeps ALL state in GCS and commits nothing to
    git, so the only repo-visible facts are the declarative watch list's entries.

    ⚠ HOST LIVENESS IS PROVABLY NOT IN GIT HERE, IN BOTH DIRECTIONS. CLAUDE.md §6, measured 2026-07-27: GCE
    REFUSES the in-VM self-delete, so a FINISHED leg leaves a RUNNING VM holding the single GPU; and an
    enabled watch entry can equally correspond to no VM at all. So `hosts_knowable` is False and this lane is
    graded on whether its watchdog is TICKING, not on a host count nobody can read from here. Grading it
    UNKNOWN on every run instead would be an alarm that is always red, which is the same end state as no
    alarm.

    ⚠ AND MONEY IS NOT THE CONSTRAINT ON GCP — WALL CLOCK IS (`ternary-watch.json` -> `_gcp_cost_frame`), and
    the trial credit is a SEPARATE LEDGER (§6). So this lane's failure mode is lost days, not lost dollars,
    and it is reported as such. `GPUS_ALL_REGIONS = 1` is the binding cap, so ONE enabled entry is the
    normal healthy shape, not a decayed fleet.
    """
    st = LaneState(spec["key"], spec["label"], spec["provider"])
    st.tick_workflow = spec["tick_workflow"]
    st.hosts_knowable = False
    st.notes.append("GCP watchdog state lives in GCS, not in git — no repo-visible census, and VM liveness is "
                    "not knowable from here in either direction; graded on whether its watchdog is ticking")
    st.notes.append("GCP failure mode is LOST WALL CLOCK, not lost dollars (free credit, separate ledger)")
    if watch is None:
        st.unreadable["watch_list"] = watch_err or "unknown"
        return st
    entries = watch.get("watch")
    if not isinstance(entries, list):
        st.unreadable["watch_list"] = "`watch` key absent or not a list"
        return st
    enabled = [e for e in entries if isinstance(e, dict) and e.get("enabled") is True]
    parked = [e for e in entries
              if isinstance(e, dict) and e.get("enabled") is not True and e.get("_parked_why")]
    st.parked = [f"{e.get('unit_id') or e.get('leg_id')}: {str(e.get('_parked_why'))[:180]}" for e in parked]
    st.unfinished = len(enabled) + len(parked)
    st.finished = (st.unfinished == 0)
    st.hold, st.hold_kind = False, None
    st.hold_reason = "the GCP lane has no $/ns market gate — it is quota-bound, not price-bound"
    st.notes.append(f"watch list: {len(enabled)} enabled, {len(parked)} parked, "
                    f"{len(entries) - len(enabled) - len(parked)} off")
    return st


# ── holds ────────────────────────────────────────────────────────────────────────────────────────────────
# ★★ "HELD" IS THREE DIFFERENT STATES WEARING ONE BOOLEAN, AND CONFLATING THEM IS AN INCIDENT EITHER WAY.
# Grading them all quiet lets a lane sleep through a night waiting for a market that was never the problem;
# grading them all loud teaches the reader to ignore the alarm, which is the same as not having one. The
# reason string is the writer's own words and is the only thing that separates them.
#
#   "needs-a-human"  waiting cannot clear it: the board could not be read at all, the live-instance list
#                    could not be read, the host exclusion set has outgrown the market, or the ResourceSpec
#                    is unsatisfiable (`hold_cause == "exclusions_or_spec_not_price"`).
#   "operator"       a deliberate configuration choice, not the market: e.g. the fan-out tick run with
#                    placement switched off to measure/collect/reap only. Benign, and named rather than
#                    silently filed under "price hold", which would misattribute an operator decision to a
#                    thin board and quietly excuse the lane from the advancement check.
#   "price"          the real §6 pause, and the only one that requires a market snapshot to be believed.
_HOLD_NEEDS_A_HUMAN = ("could not read the board", "could not list live instances")
_HOLD_OPERATOR = ("fanout_placement_enabled", "placement disabled", "release_fanout")


def _apply_hold(st: LaneState, hold: dict | None, hold_err: str | None, *,
                held_key: str, reason_key: str, depth_key: str, offers_key: str, source: str | None) -> None:
    """Record a hold, classify WHY, and refuse to accept a price hold the market did not cause.

    ★★ CLAUDE.md §6's one prohibition on a gate that declines to buy is that declining must never be SILENT:
    "a fleet that never launched looks identical to one that finished, and the only thing that tells them
    apart is a hold readout carrying the market snapshot that caused it". So a "price" hold with no `depth`
    and no `offers` is not a legitimate park — the market was never consulted — and it is graded UNKNOWN
    rather than quietly accepted.

    The two hold artifacts genuinely use different key names (`held` in the step-1 readout, `hold` in the
    ternary gate, with `board_depth`/`offers_priced` against `depth`/`offers`). They are passed in explicitly
    rather than probed, so a renamed key surfaces as unreadable instead of silently reading False.
    """
    if hold is None:
        st.hold, st.hold_kind = False, None
        st.hold_reason = f"{source or 'gate snapshot'}: {hold_err or 'not present'} — no hold on record"
        return
    val = hold.get(held_key)
    if val is None:
        st.unreadable["hold"] = (f"{source}: `{held_key}` is absent — absent is not False, and a lane that "
                                 f"cannot say whether it is holding cannot be graded")
        return
    reason = str(hold.get(reason_key) or hold.get("reason") or hold.get("decision_why") or "")
    st.hold_reason = reason or None
    if not val:
        st.hold, st.hold_kind = False, None
        return

    st.hold = True
    low = reason.lower()
    # ⚠ ORDER: `needs-a-human` IS TESTED FIRST, AND THE BARE PHRASE "not a price hold" IS NOT A DISCRIMINATOR.
    # BOTH writers use it — the ternary gate ends its `nothing_to_launch` reason with "this is NOT a price
    # hold.", and the relaunch gate OPENS its exclusion-set reason with "NOT A PRICE HOLD — ...". Keying on
    # the phrase filed a hold that re-pricing can never clear under "nothing to do here", which is the
    # quietest possible way to lose a night. The STRUCTURED keys (`hold_cause`, `nothing_to_launch`) are what
    # separate them; the phrase is only ever corroborating.
    if hold.get("hold_cause") == "exclusions_or_spec_not_price" or any(m in low for m in _HOLD_NEEDS_A_HUMAN):
        st.hold_kind, st.hold_snapshot = "needs-a-human", None
        return
    # `nothing_to_launch` is the gate saying nothing needed buying. It sets `hold: false` in the writer
    # today, but it is checked here too so a future writer that flips it cannot turn "nothing to do" into a
    # park that excuses the lane from anything.
    if hold.get("nothing_to_launch") is True:
        st.hold, st.hold_kind = False, None
        return
    if any(m in low for m in _HOLD_OPERATOR):
        st.hold_kind, st.hold_snapshot = "operator", None
        return
    present = [k for k in (depth_key, offers_key) if hold.get(k) not in (None, [], {})]
    st.hold_kind = "price"
    st.hold_snapshot = (f"{source}: " + ", ".join(present)) if len(present) == 2 else None


def read_relaunch_escalation(doc: dict | None, err: str | None) -> dict:
    """`relaunch-market-hold.json` -> a per-unit warning set, attributed to the lane that WROTE it.

    ★ TWO TRAPS, BOTH IN ONE FILE. (1) It is a SINGLE path written by both the step-1 fan-out (`lane:
    "step1_fanout"`) and the ternary watchdog (`lane: "ternary"`), so whichever relaunched last owns it; the
    `lane` key is the only attribution and reading the file without it credits one lane's health to another.
    (2) `escalation_clock: "UNAVAILABLE"` means the hold state could not be persisted, so `held_hours`
    restarts every pass and the unit CAN NEVER SELF-ESCALATE — a permanently silent hold, which is precisely
    the failure mode §6 forbids. It is surfaced as a warning on the owning lane.
    """
    if doc is None:
        return {"lane": None, "warnings": [], "why": err}
    lane, out = doc.get("lane"), []
    units = doc.get("units")
    if isinstance(units, dict):
        for uid, u in units.items():
            if not isinstance(u, dict):
                continue
            if u.get("escalation_clock") == "UNAVAILABLE" or \
                    str(u.get("escalation_clock") or "").startswith("UNAVAILABLE"):
                out.append(f"⚠ {uid}: the relaunch gate could not persist its hold state, so `held_hours` "
                           f"restarts every pass and this unit can NEVER self-escalate — a permanently "
                           f"silent hold (relaunch-market-hold.json)")
            if u.get("hold_cause") == "exclusions_or_spec_not_price":
                out.append(f"⚠ {uid}: the relaunch gate is holding for a reason RE-PRICING WILL NEVER CLEAR "
                           f"(`hold_cause=exclusions_or_spec_not_price`) — the host exclusion set has "
                           f"outgrown the market, or the ResourceSpec is unsatisfiable. Waiting is the wrong "
                           f"response.")
    return {"lane": lane, "warnings": out, "why": None}


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# classification — PURE, so both directions are testable without touching a filesystem or a network
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
OK_VERDICTS = {"ADVANCING", "PARKED-PRICE-HOLD", "PARKED-GATE", "PARKED-BY-OPERATOR", "FINISHED",
               "IDLE-WITHIN-GRACE", "TICKING"}

# Fields without which no honest verdict can be reached. `census` is deliberately NOT here: four of the five
# lanes legitimately have none, and demanding one would make them permanently UNKNOWN — an alarm that is
# always red is the same end state as no alarm.
CRITICAL = ("progress", "watch_list", "unfinished", "hold", "watch_entry_intent", "ledger", "finished")


def classify_lane(st: LaneState, hist: dict | None, now: datetime.datetime, *,
                  active_evidence_min: float = DEFAULT_ACTIVE_EVIDENCE_MIN,
                  idle_min: float = DEFAULT_IDLE_MIN,
                  census_flat_min: float = DEFAULT_CENSUS_FLAT_MIN) -> dict:
    """One lane -> one verdict. ORDER MATTERS and is the whole discrimination:

        UNKNOWN            first, because a lane we cannot read must never be graded green by a later branch
        FINISHED           before anything that could call a completed lane idle
        TICKING            lanes whose host count is provably not in git are graded on ticks, not on hosts
        BILLING-*          ★ BEFORE EVERY HOLD BRANCH. A hold means "we declined to BUY"; it says nothing
                           about hosts already running, so it must never excuse a lane from the advancement
                           check while it is billing. The first draft had this backwards and graded a
                           15-host, actively-advancing fan-out as a quiet price hold.
        HOLD-NOT-PRICE     a hold waiting cannot clear is an incident, not a park
        PARKED-*           a correct hold or an explicitly parked unit is a SUCCESS under §6, not a stall
        IDLE-UNEXPECTED    no hosts, unfinished work, and none of the above explains it
        UNKNOWN            last: unfinished work could not be counted. NEVER falls through to FINISHED —
                           the first draft did, and graded a lane with no readable state at all as complete,
                           which is precisely "absent rendered as a legal good value".
    """
    v: dict = {
        "lane": st.key, "label": st.label, "provider": st.provider,
        "now_utc": _z(now), "now_et": _et(now),
        "thresholds": {"active_evidence_min": active_evidence_min, "idle_min": idle_min,
                       "census_flat_min": census_flat_min},
        "state": st.as_dict(),
    }
    age = ((now - st.last_evidence_utc).total_seconds() / 60.0) if st.last_evidence_utc else None
    v["evidence_age_min"] = round(age, 1) if age is not None else None
    v["census_basis"] = ("committed-iteration census (the strong signal)"
                         if st.census_is_true_iteration_count
                         else "NO committed-iteration census in git for this lane — evidence age with hosts "
                              "up is the strongest available signal, and it is weaker")

    # ── flatness of a TRUE census, measured against this module's own history ──
    flat_for = None
    if st.census_is_true_iteration_count and st.census is not None and isinstance(hist, dict):
        prev_census, since = hist.get("census"), _parse_z(hist.get("census_since_utc"))
        if prev_census == st.census and since is not None:
            flat_for = (now - since).total_seconds() / 60.0
    v["census_flat_for_min"] = round(flat_for, 1) if flat_for is not None else None

    # ── 1. UNKNOWN, and loud ──
    bad = {k: why for k, why in st.unreadable.items() if k in CRITICAL}
    if bad:
        v["verdict"], v["ok"] = "UNKNOWN", False
        v["detail"] = ("this lane's state could not be read, so it CANNOT be called healthy: "
                       + "; ".join(f"{k} — {why}" for k, why in bad.items())
                       + ". An unreadable lane is reported UNKNOWN rather than OK because an unmeasured state "
                         "rendered as a measured zero is this repo's most expensive defect class.")
        return v

    # ── 2. finished ──
    if st.finished is True:
        v["verdict"], v["ok"] = "FINISHED", True
        v["detail"] = "every unit of this lane is landed; silence is the correct state and nothing is billing."
        return v

    # ── 3. lanes whose host count is provably not in git are graded on TICKS, not on hosts ──
    if not st.hosts_knowable:
        v["verdict"], v["ok"] = "TICKING", True
        v["detail"] = (f"{st.unfinished} unit(s) on the watch list and host liveness is not knowable from git "
                       f"for this provider, so this lane is graded on whether its watchdog "
                       f"({st.tick_workflow}) is still delivering completed runs — see `supervision` below, "
                       f"which is the verdict that matters for this lane.")
        return v

    if st.live_hosts is None and "live_hosts" in st.unreadable:
        # Reached only when the lane is neither finished nor parked: we cannot say whether it is billing, and
        # that is precisely the case where guessing costs money.
        v["verdict"], v["ok"] = "UNKNOWN", False
        v["detail"] = (f"this lane has unfinished work and its host count could not be read "
                       f"({st.unreadable['live_hosts']}), so 'billing but not advancing' and 'idle' cannot be "
                       f"separated. Not graded OK.")
        return v

    # ── 5. billing but not advancing — the expensive failure ──
    if (st.live_hosts or 0) > 0:
        if flat_for is not None and flat_for >= census_flat_min:
            v["verdict"], v["ok"] = "BILLING-NOT-ADVANCING", False
            v["detail"] = (f"{st.live_hosts} host(s) up and the committed-iteration census has not moved off "
                           f"its last value for {flat_for:.0f} min ({st.census_what}). This is the expensive "
                           f"failure: money is going out and the science is not. NOTE the host cannot stop "
                           f"its own billing (§6) — only the control plane can, and this module is not it: "
                           f"act through the lane's own collect path.")
            _annotate_hosts(v, st)
            return v
        if age is None:
            v["verdict"], v["ok"] = "UNKNOWN", False
            v["detail"] = (f"{st.live_hosts} host(s) up and this lane has NO evidence timestamp at all, so "
                           f"whether it is advancing cannot be established. Hosts up with nothing to read is "
                           f"the worst combination to grade green.")
            return v
        if age >= active_evidence_min:
            v["verdict"], v["ok"] = "BILLING-NOT-ADVANCING", False
            v["detail"] = (f"{st.live_hosts} host(s) up and this lane has produced NO new evidence for "
                           f"{age:.0f} min (last: {st.last_evidence_what} at {_et(st.last_evidence_utc)}, "
                           f"threshold {active_evidence_min:.0f} min). A valB cohort was dead for 85 min under "
                           f"exactly this shape while its watchdog printed 'advancing … Leaving it alone'. "
                           f"{v['census_basis']}.")
            _annotate_hosts(v, st)
            return v
        v["verdict"], v["ok"] = "ADVANCING", True
        v["detail"] = (f"{st.live_hosts} host(s) up and new evidence {age:.0f} min ago "
                       f"({st.last_evidence_what}). {v['census_basis']}.")
        _annotate_hosts(v, st)
        return v

    # ── 6. holds — one state name per meaning, and ONLY now that we know nothing is billing ──
    if st.hold is True and st.hold_kind == "needs-a-human":
        v["verdict"], v["ok"] = "HOLD-NOT-PRICE", False
        v["detail"] = (f"this lane is HELD, but not by the market — so waiting will not clear it and a human "
                       f"has to act. Reason on record: {st.hold_reason or '(none given)'}. §6's pause rule is "
                       f"about a thin, expensive MARKET; an unreadable board, an unreadable instance list, an "
                       f"outgrown exclusion set and an unsatisfiable ResourceSpec are none of those, and "
                       f"filing them under 'price hold' is how a lane sleeps through a night waiting for "
                       f"something that was never the problem.")
        return v
    if st.hold is True and st.hold_kind == "operator":
        v["verdict"], v["ok"] = "PARKED-BY-OPERATOR", True
        v["detail"] = (f"held by a deliberate configuration choice, not by the market: "
                       f"{st.hold_reason or '(none given)'}. Named rather than filed under 'price hold' — "
                       f"misattributing an operator decision to a thin board would excuse this lane from the "
                       f"advancement check on a reason nobody chose.")
        return v
    if st.hold is True:
        if st.hold_snapshot:
            v["verdict"], v["ok"] = "PARKED-PRICE-HOLD", True
            v["detail"] = (f"held on price with the snapshot that caused it ({st.hold_snapshot}). CLAUDE.md §6 "
                           f"— a thin, expensive market is a reason to PAUSE, not to pay — so this is the gate "
                           f"working, not a stall. Reason on record: {st.hold_reason or '(none given)'}")
            return v
        v["verdict"], v["ok"] = "UNKNOWN", False
        v["detail"] = ("the lane claims a price hold but carries NO market snapshot to prove the market was "
                       "consulted. §6 requires that declining to buy is never silent, because a fleet that "
                       "never launched looks identical to one that finished — an unevidenced hold is exactly "
                       "that ambiguity, so it is graded UNKNOWN rather than accepted.")
        return v

    if st.parked and st.unfinished is not None and len(st.parked) >= st.unfinished:
        v["verdict"], v["ok"] = "PARKED-GATE", True
        v["detail"] = ("every unfinished unit is deliberately parked with a stated reason, so nothing is "
                       "billing and nothing is expected to advance: " + " | ".join(st.parked[:3]))
        return v

    # ── 7. idle — no hosts. THE GAP NOTHING ELSE DETECTS. ──
    if (st.unfinished or 0) > 0:
        if age is None:
            v["verdict"], v["ok"] = "UNKNOWN", False
            v["detail"] = ("no hosts, unfinished work, and no evidence timestamp to say how long that has been "
                           "true. Cannot be graded.")
            return v
        if age >= idle_min:
            v["verdict"], v["ok"] = "IDLE-UNEXPECTED", False
            v["detail"] = (f"NO HOSTS, {st.unfinished} unit(s) unfinished, NO price hold and NO parked reason "
                           f"— and nothing has happened for {age:.0f} min (threshold {idle_min:.0f} min; last: "
                           f"{st.last_evidence_what} at {_et(st.last_evidence_utc)}). This is the closure-"
                           f"triangle shape: a lane with no live instance at all, which every liveness check "
                           f"reads as 'nothing to watch' and which is indistinguishable from finished. It is "
                           f"NOT finished. Someone has to dispatch its next step.")
            return v
        v["verdict"], v["ok"] = "IDLE-WITHIN-GRACE", True
        v["detail"] = (f"no hosts and {st.unfinished} unit(s) unfinished, but the last evidence is only "
                       f"{age:.0f} min old (grace {idle_min:.0f} min) — a hand-off in progress looks like this.")
        return v

    # ── 8. unfinished could not be counted. ★ THIS MUST NOT FALL THROUGH TO FINISHED. The first draft did,
    # and graded the closure triangle — no watch entry, no gate snapshot, no ledger record, no terminus — as
    # COMPLETE, on a lane whose 3 h of silence is the reason this module was commissioned. "Nothing is known
    # about it" and "it is done" are opposite states, and rendering the first as the second is the exact
    # defect class §4 and the absent-is-not-a-value rule exist to stop.
    if st.unfinished is None:
        v["verdict"], v["ok"] = "UNKNOWN", False
        v["detail"] = ("nothing readable says how much of this lane is left: no watch entry, no gate snapshot "
                       "attributable to it, and no launch-ledger record. That is NOT the same as finished — a "
                       "lane that quietly stopped between stages leaves exactly this footprint, and it is the "
                       "shape the closure triangle sat in for ~3 h. Either dispatch its next step or park it "
                       "explicitly with a stated reason; both silence this verdict honestly.")
        return v

    v["verdict"], v["ok"] = "FINISHED", True
    v["detail"] = "no hosts and no unfinished units."
    return v


def _annotate_hosts(v: dict, st: LaneState) -> None:
    """Report the host-state histogram WITHOUT letting it condemn.

    ⚠ WHY IT ONLY ANNOTATES. `cur_state: stopped` is genuinely ambiguous — a fresh rental reads
    `stopped/loading` while its image pulls (2 h 57 min observed on this account), so alerting on first sight
    would be noise at every launch. The line past which `stopped` IS worth acting on is `MAX_STOPPED_MIN`,
    which belongs to `ternary_vast_watchdog.stopped_and_billing` and to the collector that acts on it.
    Copying it here would give one threshold two homes free to drift (§1), and acting on it here would make
    this a second control path. So it is surfaced, loudly, and the decision stays where it lives.
    """
    if not st.host_states:
        return
    running = st.host_states.get("running", 0)
    if running == 0 and sum(st.host_states.values()) > 0:
        v["host_state_note"] = (f"⚠ NOT ONE host is `running` in this lane's last snapshot: {st.host_states}. "
                                f"That is the shape of the 2026-07-27 valB cohort whose four hosts had all "
                                f"been reclaimed while the watchdog printed reassurance. This module does NOT "
                                f"condemn on it (a fresh rental legitimately reads stopped/loading while its "
                                f"image pulls) — check it with the lane's own `collect`, which reads the start "
                                f"response that separates outbid from GPU-gone.")
    else:
        v["host_state_note"] = f"host states: {st.host_states}"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# gathering
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ LANES DO NOT ALL LIVE ON ONE BRANCH, AND READING THEM AS IF THEY DID MANUFACTURES FALSE ALARMS
# (2026-07-27, 8:06 PM ET — the second branch-mismatch misdiagnosis of the same evening).
#
# WHAT HAPPENED. This watcher took a single `fleet_branch` and read every lane's artifacts from it. But the
# step 1 fan-out commits to that branch (`step1-fanout-autoscale.yml`'s `GIT_BRANCH` input) while the ternary
# family is dispatched with `ref=main` and commits to **main**. Measured at 8:06 PM:
#
#   branch                      enabled watch modes            latest launch-ledger entry
#   main                        edge_reps 4, triangle 4        8:03 PM ET
#   claude/max-effort-2dq11l    edge_reps 4, triangle_smoke 1  6:25 PM ET
#
# So the watcher was 100 minutes behind on the ternary lanes and **could not see the closure triangle at all**.
# It reported `IDLE-UNEXPECTED — NO HOSTS, someone has to dispatch its next step` for a lane that had 4 of 4
# legs hosted and billing, and `BILLING-NOT-ADVANCING` for a cohort that had been re-placed 20 minutes earlier.
# Both reds were artefacts of where it looked, not of what was happening.
#
# WHY THIS IS THE WORST CLASS OF BUG HERE. A monitor whose false alarms are indistinguishable from its true
# ones trains its reader to ignore it, which is strictly worse than having no monitor — the same argument the
# landed-leg reap in `ternary_vast_watchdog` rests on.
#
# THE FIX, AND WHY IT IS SYMBOLIC. A lane declares an `artifact_source` — a NAME, not a branch. The mapping
# from name to directory is supplied by the caller (`--source-root ternary=/path`), so a branch rename is a
# workflow edit and never a code edit, and this module keeps its stdlib-only, knows-nothing-about-git
# property. An unmapped source falls back to `--root`, which is exactly the old behaviour, so a caller that
# passes nothing is no worse off than before.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def gather(root: str, specs: list[dict] | None = None,
           source_roots: dict[str, str] | None = None) -> tuple[list[LaneState], dict]:
    """Load every artifact once and build one LaneState per lane. All file I/O lives here.

    `source_roots` maps a lane's `artifact_source` to the directory holding THAT lane's artifacts. Lanes
    whose source is absent from the map read from `root`.
    """
    specs = specs if specs is not None else LANES
    source_roots = source_roots or {}
    cache: dict[tuple[str, str], tuple[dict | None, str | None]] = {}
    # The cache key carries the root as well as the filename. Two lanes on different branches legitimately
    # read the SAME filename (`ternary-vast-market-hold.json`) with different contents, so a filename-only
    # key would serve one branch's bytes for the other's lane — a subtler replay of the very bug above.
    current_root = [root]

    def get(name: str | None):
        if not name:
            return None, "no artifact configured"
        key = (current_root[0], name)
        if key not in cache:
            cache[key] = load_json(current_root[0], name)
        return cache[key]

    esc = read_relaunch_escalation(*get("relaunch-market-hold.json"))

    out = []
    for spec in specs:
        current_root[0] = source_roots.get(spec.get("artifact_source"), root)
        if spec["reader"] == "step1":
            prog, perr = get(spec["generation_artifact"])
            hold, herr = get(spec.get("hold_artifact"))
            st = read_step1(spec, prog, perr, hold, herr)
        elif spec["reader"] == "ternary_family":
            watch, werr = get("ternary-vast-watch.json")
            hold, herr = get(spec.get("hold_artifact"))
            ledger, lerr = get("ternary-vast-launch-attempts.json")
            term = spec.get("terminal_artifact")
            # `current_root[0]`, not `root`: a terminal artifact is the lane's own deliverable and
            # lives wherever that lane commits. Checking the fallback root would report a landed
            # ternary reduction as absent.
            present = os.path.exists(os.path.join(current_root[0], term)) if term else None
            st = read_ternary_family(spec, watch, werr, hold, herr, ledger, lerr, present)
        elif spec["reader"] == "nrv04_retro":
            frag, ferr = get(spec["generation_artifact"])
            hold, herr = get(spec.get("hold_artifact"))
            st = read_nrv04_retro(spec, frag, ferr, hold, herr)
        elif spec["reader"] == "selcal":
            census, cerr = get("selcal-cofold-census.json")
            hold, herr = get(spec.get("hold_artifact"))
            st = read_selcal(spec, census, cerr, hold, herr)
        elif spec["reader"] == "selcal_md":
            reap, rerr = get("selcal-reap.json")
            coll, cerr2 = get("selcal-collect.json")
            ledger, lerr = get("selcal-price-ledger.json")
            hold, herr = get(spec.get("hold_artifact"))
            st = read_selcal_md(spec, reap, rerr, coll, cerr2, ledger, lerr, hold, herr)
        elif spec["reader"] == "gcp_watch":
            watch, werr = get(spec.get("watch_file"))
            st = read_gcp_watch(spec, watch, werr)
        else:  # pragma: no cover - the registry is code, so an unknown reader is a programming error
            raise ValueError(f"unknown reader {spec['reader']!r} for lane {spec['key']!r}")
        # The relaunch gate's warnings attach to the lane that WROTE the file, never to all lanes.
        if esc["warnings"] and spec.get("relaunch_lane") and esc["lane"] == spec["relaunch_lane"]:
            st.warnings.extend(esc["warnings"])
        out.append(st)
    return out, esc


def supervision_for(spec: dict, root: str, now: datetime.datetime, use_api: bool) -> dict:
    """REUSE, not reinvent: apply `fleet_supervision_alarm`'s throttle-immune generation test where the lane
    has BOTH a dedicated tick workflow AND a repo-visible artifact that tick writes.

    Where it does not, this returns `applicable: False` with the reason, rather than substituting a weaker
    check and letting the reader assume the strong one ran. Same honesty rule as `census_basis`.

    ⚠ THE THRESHOLDS ARE THE IMPORTED ONES. `DEFAULT_STALE_MIN` / `DEFAULT_ABSENT_MIN` were set from measured
    GitHub delivery (141-238 min gaps) and have one home; re-typing them here is exactly the drift §1 forbids.
    """
    wf, art = spec.get("tick_workflow"), spec.get("generation_artifact")
    if not use_api:
        return {"applicable": False, "why": "--no-api: the Actions API was not consulted"}
    try:
        import fleet_supervision_alarm as fsa
    except ImportError as e:  # pragma: no cover
        return {"applicable": False, "why": f"fleet_supervision_alarm unavailable ({e})"}

    runs, ferr = fsa.fetch_runs(REPO, wf)
    if not art:
        # No repo-visible artifact this tick writes -> the generation test cannot run. Report the WEAKER
        # question it can still answer (is the workflow producing completed runs at all) and label it.
        started = [t for t in (_parse_z(r.get("run_started_at") or r.get("created_at"))
                               for r in (runs or []) if isinstance(r, dict)) if t]
        last = max(started, default=None)
        since = (now - last).total_seconds() / 60.0 if last else None
        out = {"applicable": True, "workflow": wf, "artifact": None, "fetch_error": ferr,
               "test": "REDUCED — this lane commits no artifact its tick writes, so the generation-advance "
                       "test cannot run. Only 'has the workflow started a run recently' is answerable, and "
                       "that is a weaker question: a run that starts and measures nothing looks identical.",
               "last_run_started_et": _et(last),
               "min_since_any_run_started": round(since, 1) if since is not None else None}
        if runs is None:
            out["verdict"], out["ok"] = "TICKS-UNREADABLE", True
            out["detail"] = (f"the Actions API could not be read ({ferr}) — an unreadable API is NOT a dead "
                             f"scheduler, so this is not treated as an outage.")
        elif since is None or since > fsa.DEFAULT_ABSENT_MIN:
            out["verdict"], out["ok"] = "NO-TICKS", False
            out["detail"] = (f"no run of {wf} has started in "
                             f"{'ever' if since is None else f'{since:.0f} min'} (window "
                             f"{fsa.DEFAULT_ABSENT_MIN:.0f} min, set from measured delivery) while this lane "
                             f"still has unfinished units. Nothing is supervising it.")
        else:
            out["verdict"], out["ok"] = "TICKS-FLOWING", True
            out["detail"] = (f"{wf} last started a run {since:.0f} min ago, so the lane is still being "
                             f"visited — though see `test` for what this does and does not prove.")
        return out

    doc, err = load_json(root, art)
    fsa.TICK_WORKFLOW = wf
    v = fsa.classify(doc, runs, now, fsa.DEFAULT_STALE_MIN, fsa.DEFAULT_ABSENT_MIN, fetch_error=ferr)
    v.update({"applicable": True, "artifact": art, "workflow": wf,
              "test": "FULL — did the last COMPLETED run advance the artifact's `_generated_utc` past its "
                      "own start? Throttle-immune; the one signal that catches a tick which went green "
                      "without measuring."})
    if err:
        v["artifact_load_error"] = err
    return v


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# history — the only state this module keeps, and it is used ONLY to age a census
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def update_history(prev: dict, states: list[LaneState], now: datetime.datetime) -> dict:
    """`census_since_utc` moves ONLY when the census value changes.

    ★ WHY A FAILED HISTORY WRITE CANNOT MANUFACTURE AN ALARM. If the commit-back fails, the stored census
    stays old. Either the real census has since advanced — in which case it differs from the stored one and
    `census_since_utc` resets to now, UNDER-reporting flatness — or it genuinely has not moved, in which case
    the growing flat time is correct. Both directions fail safe, and the safe direction is the quiet one.
    """
    out = {k: v for k, v in (prev or {}).items() if k.startswith("_")}
    out.setdefault("_what", "Per-lane census history for lane_staleness_watch.py. `census_since_utc` is when "
                            "the census last CHANGED — the only thing this file is for. It is NOT a source of "
                            "truth about any lane: delete it and the watcher simply cannot age a census until "
                            "it has two observations again.")
    out["_updated_utc"] = _z(now)
    lanes = dict((prev or {}).get("lanes") or {})
    for st in states:
        if st.census is None:
            continue
        old = lanes.get(st.key) or {}
        since = old.get("census_since_utc") if old.get("census") == st.census else _z(now)
        lanes[st.key] = {"census": st.census, "census_since_utc": since or _z(now),
                         "census_what": st.census_what, "observed_utc": _z(now)}
    out["lanes"] = lanes
    return out


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# rendering + entry point
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
_GLYPH = {"ADVANCING": "✅", "FINISHED": "✅", "TICKING": "✅", "PARKED-PRICE-HOLD": "⏸", "PARKED-GATE": "⏸",
          "PARKED-BY-OPERATOR": "⏸",
          "IDLE-WITHIN-GRACE": "⏳", "BILLING-NOT-ADVANCING": "🔴", "IDLE-UNEXPECTED": "🔴",
          "HOLD-NOT-PRICE": "🔴", "TICK-NOT-MEASURING": "🔴", "UNKNOWN": "❓"}


def render(report: dict) -> str:
    lines = [f"[lane-watch] read at {report['now_et']}",
             f"[lane-watch] {report['n_lanes']} lane(s) watched; "
             f"{report['n_bad']} need attention, {report['n_ok']} advancing or correctly parked"]
    for v in report["lanes"]:
        g = _GLYPH.get(v["verdict"], "?")
        lines.append(f"[lane-watch] {g} {v['lane']:<22} {v['verdict']:<22} {v['label']}")
        lines.append(f"[lane-watch]      {v['detail']}")
        if v.get("host_state_note"):
            lines.append(f"[lane-watch]      {v['host_state_note']}")
        sup = v.get("supervision") or {}
        if sup.get("applicable"):
            lines.append(f"[lane-watch]      tick supervision ({sup.get('workflow')}): "
                         f"{sup.get('verdict')} — {sup.get('detail')}")
        elif sup.get("why"):
            lines.append(f"[lane-watch]      tick supervision: NOT RUN — {sup['why']}")
        for w in (v["state"].get("warnings") or []):
            lines.append(f"[lane-watch]      {w}")
        for note in (v["state"].get("notes") or [])[:3]:
            lines.append(f"[lane-watch]      · {note}")
    return "\n".join(lines)


# Lanes in these states are actively expected to be visited by their tick. A FINISHED or correctly-parked
# lane SHOULD have no ticks, and failing it for having none is precisely how an alarm teaches people to
# ignore it.
_ACTIVE = ("ADVANCING", "BILLING-NOT-ADVANCING", "IDLE-UNEXPECTED", "IDLE-WITHIN-GRACE", "TICKING",
           # UNKNOWN is included on purpose: when a lane's own state is unreadable, whether its tick is still
           # running is the most useful thing left to say about it. It cannot make the verdict worse — the
           # escalation below only fires on a lane that was otherwise OK.
           "UNKNOWN")


def build_report(root: str, now: datetime.datetime, *, history: dict | None = None,
                 use_api: bool = True, only: set[str] | None = None,
                 active_evidence_min: float = DEFAULT_ACTIVE_EVIDENCE_MIN,
                 idle_min: float = DEFAULT_IDLE_MIN,
                 census_flat_min: float = DEFAULT_CENSUS_FLAT_MIN,
                 source_roots: dict[str, str] | None = None) -> tuple[dict, list[LaneState]]:
    specs = [s for s in LANES if not only or s["key"] in only]
    source_roots = source_roots or {}
    states, _esc = gather(root, specs, source_roots)
    hist_lanes = (history or {}).get("lanes") or {}
    verdicts = []
    for spec, st in zip(specs, states):
        v = classify_lane(st, hist_lanes.get(st.key), now, active_evidence_min=active_evidence_min,
                          idle_min=idle_min, census_flat_min=census_flat_min)
        if v["verdict"] in _ACTIVE:
            # The freshness check compares a WORKFLOW RUN against THAT LANE'S artifact stamp, so it
            # must read the lane's own root. Handing it the fallback is what produced
            # 'STALE-BUT-RUNS-GREEN — the tick went green WITHOUT measuring' against a tick that had
            # measured perfectly well, one branch over.
            sup = supervision_for(spec, source_roots.get(spec.get('artifact_source'), root),
                                  now, use_api)
            v["supervision"] = sup
            if sup.get("applicable") and sup.get("ok") is False and v["ok"]:
                v["ok"] = False
                v["verdict"] = "TICK-NOT-MEASURING"
                v["detail"] = (f"the lane's own state looks fine, but its tick is not measuring it: "
                               f"[{sup.get('verdict')}] {sup.get('detail')}")
        else:
            v["supervision"] = {"applicable": False,
                                "why": f"lane is {v['verdict']} — a lane that should have no ticks is not "
                                       f"failed for having none"}
        verdicts.append(v)
    bad = [v for v in verdicts if not v["ok"]]
    report = {
        "_what": "Cross-lane staleness verdict. Has each billing lane produced NEW EVIDENCE, and if not, is "
                 "that expected? Reports only — it never rents, destroys, reaps or condemns a box.",
        "now_utc": _z(now), "now_et": _et(now),
        "n_lanes": len(verdicts), "n_bad": len(bad), "n_ok": len(verdicts) - len(bad),
        "ok": not bad,
        "needs_attention": [v["lane"] for v in bad],
        "lanes": verdicts,
    }
    return report, states


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=HERE, help="directory holding the lane artifacts")
    ap.add_argument("--history", default=DEFAULT_HISTORY)
    ap.add_argument("--json", default=None)
    ap.add_argument("--now", default=None, help="ISO8601Z override, for deterministic verification")
    ap.add_argument("--lane", action="append", default=None, help="restrict to these lane keys")
    ap.add_argument("--no-api", action="store_true", help="skip the Actions API (offline / unit runs)")
    ap.add_argument("--write-history", action="store_true", help="persist the census history for next run")
    ap.add_argument("--active-evidence-min", type=float, default=DEFAULT_ACTIVE_EVIDENCE_MIN)
    ap.add_argument("--idle-min", type=float, default=DEFAULT_IDLE_MIN)
    ap.add_argument("--census-flat-min", type=float, default=DEFAULT_CENSUS_FLAT_MIN)
    ap.add_argument("--source-root", action="append", default=None, metavar="SOURCE=DIR",
                    help="where a lane's artifacts actually live, e.g. `ternary=/tmp/roots/main`. "
                         "Lanes declare a SYMBOLIC `artifact_source`; this maps it to a directory, so "
                         "a branch rename never touches this module. Unmapped sources use --root.")
    a = ap.parse_args(argv)

    source_roots = {}
    for item in (a.source_root or []):
        if "=" not in item:
            print(f"::error::--source-root {item!r} must be SOURCE=DIR", file=sys.stderr)
            return 2
        name, _, path = item.partition("=")
        # A mapping that points nowhere would silently read an EMPTY directory, and an absent artifact
        # reads as "no evidence" — i.e. a stale lane. Refusing here turns a typo into a config error
        # instead of a fleet-wide false alarm.
        if not os.path.isdir(path):
            print(f"::error::--source-root {name}={path!r} is not a directory", file=sys.stderr)
            return 2
        source_roots[name.strip()] = path

    now = _parse_z(a.now) if a.now else datetime.datetime.now(datetime.timezone.utc)
    if now is None:
        print(f"::error::--now {a.now!r} is not an ISO8601 Z timestamp", file=sys.stderr)
        return 2

    try:
        with open(a.history) as fh:
            history = json.load(fh)
    except (OSError, json.JSONDecodeError):
        history = {}

    report, states = build_report(a.root, now, history=history, use_api=not a.no_api,
                                  only=set(a.lane) if a.lane else None,
                                  active_evidence_min=a.active_evidence_min, idle_min=a.idle_min,
                                  census_flat_min=a.census_flat_min, source_roots=source_roots)
    print(render(report))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(report, fh, indent=2)
            fh.write("\n")
    if a.write_history:
        with open(a.history, "w") as fh:
            json.dump(update_history(history, states, now), fh, indent=2)
            fh.write("\n")

    if report["ok"]:
        return 0
    for v in report["lanes"]:
        if not v["ok"]:
            print(f"::error title=LANE {v['lane']} {v['verdict']}::{v['detail']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
