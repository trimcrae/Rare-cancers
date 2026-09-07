#!/usr/bin/env python3
"""IS ANY HOST BILLING THAT NOBODY IS WATCHING? — asked of the ACCOUNT, not of any lane.

★★ WHY THIS EXISTS, measured 2026-08-01. The selectivity-control lane rented two hosts. Its own census
stopped ticking at 10:14 AM ET. At 10:54 AM ET the account census showed:

    46508454  RTX 4090  running  selcal-cofold-selcal-smarca-cofold-v1-smarca2
    46508511  RTX 4090  exited   selcal-cofold-selcal-smarca-cofold-v1-smarca4

ONE HOST HAD EXITED AND NOTHING NOTICED FOR 40+ MINUTES. The lane's watch job was still `in_progress` with a
successor `pending`, so the supervisor LOOKED alive while producing no ticks — and an `exited` instance still
appears in the account listing.

★★ THE STRUCTURAL GAP, WHICH IS THE ONLY THING THIS MODULE IS ABOUT. Every lane's liveness is watched by that
lane's own supervisor. **When the supervisor stalls, the lane goes silent and the only thing that would notice
is the thing that stopped.** `lane_staleness_watch.py` has exactly this hole too: it is dispatched from
`step1-fanout-supervisor.yml`'s in-job loop, so it inherits that loop's single point of failure — and a lane
built this morning is not registered with it at all, so it renders as nothing rather than as unwatched.

This is the same shape as four earlier incidents, and CLAUDE.md records every one of them:
the retro tick that could reap but never launch; the GCP lane idle 15 h because nothing queued work; the
account census itself running only from a hand-dispatched diagnostic (`step1-fanout-supervisor.yml`'s own
comment: "the one detector that can find a 5-day orphan only ran when somebody already suspected one"); a
heartbeat guard that would have made a dead lane render as an idle one. **Every one was "the guard existed and
nothing drove it."**

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
THE ONE OBSERVATION NO LANE-SCOPED WATCHER CAN MAKE
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
    THIS HOST IS BILLING, AND THE LANE THAT OWNS IT HAS NOT REPORTED IN N MINUTES.

That is mechanically detectable from two artifacts that already exist, and it is exactly today's failure. It
is keyed on the ACCOUNT because the account is the one view that does not disappear when a lane does: a
per-mode board filters to one mode's labels and therefore structurally cannot see a host whose lane stopped
(`ternary-vast-account-census.json`'s own `_what` says this).

★★ THE ALARM IS ON THE **PAIR**, NEVER ON EITHER HALF ALONE. This is the whole design, and getting it wrong in
either direction produces an alarm nobody reads:

    fresh lane + hosts   -> SUPERVISED.  Normal, healthy, the common case. SILENT.
    stale lane + NO hosts -> IDLE.       Also fine — nothing is billing, so silence costs nothing. SILENT.
    stale lane + hosts   -> ★ ALARM.     Money burning with nobody watching. TODAY'S FAILURE.
    host, no lane at all -> ★ ALARM.     The orphan: a prefix no registered lane claims.

Firing on staleness alone would fire on every finished lane forever. Firing on hosts alone would fire on every
healthy fleet. Only the conjunction is an incident, and only the conjunction is quiet the rest of the time.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
WHAT IT DELIBERATELY DOES NOT DO
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
⚠ IT IS REPORT-ONLY. IT NEVER DESTROYS, REAPS, STOPS, NUDGES, RENTS OR BIDS. Not a soft convention:
`tests/test_account_orphan_alarm.py` walks this module's AST and fails if a destructive verb, a Vast mutation
endpoint or an HTTP call ever appears in it. The value here is NOTICING; acting is a separate decision with a
separate blast radius, and a report-only alarm is one that can be trusted to run everywhere, on every lane,
including lanes whose semantics it does not understand. Every destructive act stays where it already lives —
the lanes' own `collect` paths and `vast_idle_guard.py`, which is the ONE thing CLAUDE.md §6 says may condemn
a box. A watcher that could also act would be a SECOND UNREVIEWED CONTROL PATH.

⚠ `gpu_util` IS NEVER READ, AND THAT IS `vast_idle_guard`'s INVIOLABLE RULE, NOT A STYLE CHOICE: **GPU
idleness NEVER condemns a box.** 0.0 is normal for tens of minutes on a legitimately CPU-bound staging phase,
and both of today's selcal instances read `gpu_util: 0.0` — including the one that was working. Only a
measured absence of WRITES may condemn, and this module does not condemn at all; it reports who is not
writing. The AST test asserts the key never appears here.

⚠ IT IMPORTS NOTHING FROM ANY LANE, AND NOTHING FROM `lane_staleness_watch`. An alarm that shares a dependency
with the thing it watches dies with it — that is how the 11:37 AM tick on 2026-07-27 took its own progress
check down. Pure stdlib, no boto3, no Vast key, no network. It reads two files off disk and that is all.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
FAIL CLOSED, AND DISTINGUISH THE TWO ABSENCES (CLAUDE.md §4)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
**AN ABSENT READING IS NOT A READING OF ABSENCE.** A census that cannot be read, or that is itself stale, is
UNKNOWN — never "no hosts". This is not hypothetical: the account census was 155 min stale at one point today,
and a naive check would have read "no instances I can see" as "all clear" at the exact moment two hosts were
up. So:

    census unreadable          -> CENSUS-UNKNOWN, exit non-zero. NOTHING is graded. No lane is called healthy.
    census older than the      -> CENSUS-STALE, exit non-zero, and every lane verdict is suppressed to
      staleness window            UNKNOWN rather than computed off numbers that may no longer be true.
    lane freshness unreadable  -> that LANE is UNKNOWN. If it holds hosts, that is an alarm, because
      AND it holds hosts          "billing but unwatchable" is strictly worse than "billing and stale".

**AND A POPULATED FIELD IS NOT A MEASURED ONE.** Every lane's freshness carries `freshness_basis` naming which
source produced it, because the two are not equally strong and a reader must never assume the strong one ran:

    "in-file stamp"   the lane's tick wrote a timestamp INTO its own artifact. Strong: only a real tick
                      produces it.
    "git commit time" the artifact's last commit. WEAKER, and labelled so, because an unrelated refactor
                      touching the file moves it without any tick having happened — it can only ever make a
                      lane look FRESHER than it is, so it is never allowed to be the sole basis for calling a
                      lane healthy without saying that is what it rested on.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
WHY THE REGISTRY IS EXPLICIT, AND WHY IT IS NOT A SECOND COPY OF `lane_staleness_watch.LANES` (§1)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
A DISCOVERED list silently shrinks: a lane whose artifact went missing would simply not appear, and "not
watched" would render exactly like "healthy". Naming lanes explicitly is what makes a stopped tick LOUD. That
argument is already settled at `lane_staleness_watch.py`'s "WHY THE FIVE LANES ARE NAMED EXPLICITLY".

But this registry owns a DIFFERENT FACT from that one, which is why it is not a duplicate:

    lane_staleness_watch.LANES  ->  "which lanes have repo-visible PROGRESS artifacts, and how to grade them"
    ACCOUNT_LANES (here)        ->  "which VAST LABEL PREFIX belongs to which lane"

The GCP lane has no Vast label at all; a lane can have a prefix and no gradeable progress artifact. Neither
registry can be derived from the other. What §1 requires instead is that the shared parts cannot disagree, and
that is ENFORCED BY TEST rather than by an import: `test_account_orphan_alarm.py` imports the real minting
constants (`congeneric_fanout_vast.LABEL_PREFIX`, `selcal_panel.LABEL_PREFIX`, …) and fails if a prefix here
drifts from the module that actually mints it. **Test-time coupling, run-time independence** — the alarm keeps
working when a lane module is broken, which is precisely when it is needed.

★ AND THIS IS WHY A LANE THAT DOES NOT EXIST YET IS STILL COVERED. An unregistered lane's hosts do not vanish
from the account listing — they land in ORPHAN-HOST, by name, with their instance id. The registry is what
turns an orphan into a named lane; forgetting to register is therefore LOUD, not silent. That is the opposite
of the failure being fixed, where a lane built this morning was invisible to the only cross-lane watcher.

Usage:
    python3 account_orphan_alarm.py [--root DIR] [--census PATH] [--json OUT] [--now ISO8601Z]
                                    [--lane-silent-min N] [--census-stale-min N] [--no-git]
Exit 0 = every billing host belongs to a lane that is reporting. Exit 1 = an alarm, or anything UNKNOWN.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys



#: The board's fragment directory. ⚠ TYPED HERE, AND THAT IS DELIBERATE: this module is PURE STDLIB by
#: design — "it must be pure stdlib so it cannot be taken down by the lanes it watches"
#: (test_account_orphan_alarm) — so it may not import `inflight_board`, which is a lane module. An alarm
#: that dies when the thing it supervises dies is not an alarm.
#: The CONSISTENCY is proven at TEST time instead, where importing anything is free: every `board_lane`
#: declared below must be a real `inflight_board.LANES` id and must compose to that lane's real fragment
#: path. So the runtime stays isolated and the two registries still cannot drift.
BOARD_FRAGMENT_DIR = "inflight-board.d"


def lane_fragment(spec):
    """The repo-relative artifact whose freshness proves this lane reported. DERIVED for board lanes.

    ★★ THE SECOND HOME IS REMOVED, NOT POLICED (2026-08-01, second pass at this bug).

    The first fix re-pointed four typed paths at the board fragments and added a test that this registry
    and `inflight_board.LANES` AGREE. That is DETECTION, not prevention — and the agreement test had three
    escape hatches, any one of which lets the same false `UNSUPERVISED-BILLING` back in:

        a `fragment: None` entry            -> skipped
        a lane id absent from the board     -> skipped ("nothing to reconcile")
        a hand-maintained ALIAS map         -> a renamed lane silently stops being checked

    The bug it was fixed for was two registries naming one fact and only one being updated. Adding a third
    thing that must be kept in step is more of the same disease. So a board-backed entry now declares WHICH
    lane it is (`board_lane`) and the PATH is computed here. There is nothing left to disagree.

    A lane with neither `board_lane` nor `fragment` is genuinely artifact-less; callers already render that
    as UNWATCHABLE-BILLING, which is a declared state and not silence.
    """
    lane = spec.get("board_lane")
    if lane:
        return f"{BOARD_FRAGMENT_DIR}/{lane}.json"
    return spec.get("fragment")

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: always US Eastern, 12-hour.

HERE = os.path.dirname(os.path.abspath(__file__))

# ── thresholds ───────────────────────────────────────────────────────────────────────────────────────────
# ⚠ THESE ARE THIS MODULE'S OWN CONSTANTS AND NOTHING HERE RE-TYPES A THRESHOLD THAT HAS A HOME ELSEWHERE
# (§1). In particular this module does not restate the buy line, the ladder basis, `MAX_STOPPED_MIN`, or any
# dollar figure. It reports dollars only by quoting the census's own `dph_total` / `spend_so_far_usd` back.

#: How long a lane HOLDING HOSTS may go without committing evidence before that is an incident. Set from the
#: measured failure and nothing else: today's lane was silent 40+ min with two hosts up before a human
#: noticed. 40 min is "the shortest silence that incident actually produced", so the alarm would have fired
#: at the moment the incident became one rather than after it had already been diagnosed by hand.
#:
#: ⚠ IT IS DELIBERATELY **NOT** SET FROM SCHEDULED-TICK DELIVERY, and that is the same reasoning
#: `fleet_supervision_alarm.py` reached: an honest threshold against this repo's delivered schedule gaps would
#: have to sit above ~240 min, which is an alarm that cannot see a 40-minute incident. The reason it is
#: allowed to be tight HERE is that the signal is a CONJUNCTION — a lane with no hosts is never graded on it
#: at all, so a quiet finished lane cannot cry wolf no matter how old its artifact gets.
DEFAULT_LANE_SILENT_MIN = 40.0

#: How old the ACCOUNT CENSUS itself may be before it stops being evidence. Measured today: it was 155 min
#: stale at one point, which would have made a naive check report all-clear while two hosts were up. Past
#: this the census is not treated as a weaker reading — it is not treated as a reading at all.
DEFAULT_CENSUS_STALE_MIN = 45.0

#: How far a lane's stamp may sit IN THE FUTURE before it stops being believable.
#: ⚠ WHY THIS EXISTS AT ALL — CAUGHT BY RUNNING THE NEGATIVE CONTROLS, not by review. A stamp ahead of `now`
#: produces a NEGATIVE age, and a negative age passes `age >= lane_silent_min` forever: the lane reads as
#: permanently fresh and this alarm goes permanently silent for it. That is the dangerous direction and it is
#: reachable three ways that have nothing to do with malice — a skewed runner clock, a stamp written from a
#: different timezone as though it were UTC, or a field populated from ENV rather than from what ran (the
#: exact defect CLAUDE.md §4 records: 17 smoke legs echoed `prod_ns: 5.0` from their ENV and a completeness
#: count believed them). A small tolerance absorbs honest CI/commit-time skew; past it, the stamp is not a
#: reading and the lane is graded UNKNOWN rather than fresh.
DEFAULT_FUTURE_SKEW_MIN = 5.0

#: Instance states that are TERMINAL but STILL LIST. Today's host was `exited` and was invisible to every
#: lane-scoped check.
#: ⚠ THIS MODULE DOES NOT CLAIM TO KNOW WHETHER A TERMINAL INSTANCE IS STILL BILLING, and must not: that
#: would be a "probably" (§4). What is MEASURED is that it still appears in `GET /instances/`, i.e. it has not
#: been destroyed, and that the host cannot destroy itself — CLAUDE.md §6, "THE HOST CANNOT STOP ITS OWN
#: BILLING — ONLY THE CONTROL PLANE CAN". So a terminal instance is an object that only the control plane can
#: clear, sitting in the account, and the reason to surface it is that nothing else does.
#:
#: ⚠ IT IS THE UNION OF THE TWO DEFINITIONS THE REPO ALREADY HAS, NOT A NEW ONE (§1):
#:     `congeneric_fanout_vast._TERMINAL` = ("exited", "offline", "error")
#:     `nrv04_vast_launch._TERMINAL_STATES` = ("exited", "offline", "stopped")
#: Neither can be IMPORTED here — this module must not depend on a lane (see the header) — so it is typed
#: once and `test_terminal_states_cover_both_repo_definitions` asserts it stays a superset of both. Same
#: test-time-coupling / run-time-independence discipline as the label prefixes.
#:
#: ⚠ AND `created` IS DELIBERATELY **NOT** HERE, having briefly been. It is an EARLY lifecycle state — a
#: freshly-rented box on its way up — so calling it terminal would print "TERMINAL BUT STILL LISTED" against
#: every new rental, i.e. cry wolf on the healthiest event in the system. Neither repo definition includes it
#: and there was no evidence for it; it was a guess, which is exactly what §4 forbids.
TERMINAL_STATES = ("exited", "stopped", "offline", "error")

_ISO_Z = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the registry — one entry per lane that can put a label on a Vast box
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# FIELDS
#   key             stable id. Where a lane is also in `lane_staleness_watch.LANES` this MATCHES that key, so
#                   the two readouts can be read side by side. The test asserts the ones that must agree.
#   label_prefixes  the fact this registry uniquely owns: what the lane names its boxes.
#   prefix_source   "module.CONSTANT" that MINTS the prefix. Not used at runtime — it is the test's handle,
#                   and it is what keeps this list from drifting from reality without importing a lane here.
#   fragment        repo-visible artifact whose freshness IS the lane's "I am still reporting". None means
#                   the lane has no repo-visible tick evidence AT ALL — stated, never faked, and a lane in
#                   that state holding hosts is graded UNWATCHABLE-BILLING (loud), because "I cannot tell"
#                   about a billing host is strictly worse news than "it is stale".
#   time_keys       keys to try, in order, for the in-file stamp (the STRONG basis).
#   time_mode       "iso"           the value IS an ISO-Z stamp.
#                   "iso_in_string" the value is free text CONTAINING one (selcal's `phase` is
#                                   "done rc=0 2026-08-01T14:41:08Z instance=… attempt=…"). Extracting is
#                                   honest here and beats the git fallback, which cannot tell a tick from a
#                                   refactor.
#   tick_workflow   who is supposed to be driving it. REPORTED so a human knows where to look; never called.
ACCOUNT_LANES: list[dict] = [
    {
        "key": "step1-fanout",
        "label": "Step 1 congeneric RBFE fan-out (Vast)",
        "label_prefixes": ("s1f-",),
        "prefix_source": "congeneric_fanout_vast.LABEL_PREFIX",
        # ★★ THE BOARD FRAGMENT IS THE HEARTBEAT, FOR EVERY LANE (2026-08-01). This keyed on
        # step1-fanout-progress.json (written only by the autoscale tick), which stopped being this lane's heartbeat when the in-flight board
        # became universal — so the alarm graded a file the lane no longer writes on every tick and
        # declared UNSUPERVISED-BILLING while the lane was reporting normally. Measured that evening:
        # the alarm's source last moved 6:32/6:39 PM while each lane's board fragment had moved at
        # 8:43/8:44 PM — the lanes had reported ~2 HOURS more recently than the alarm believed.
        # `nrv04-retro` was already on its board fragment; the others were not. One rule, one site.
        # ⚠ AND IT UPGRADES THE STAMP. A board fragment carries an in-file `generated_epoch`, which this
        # module already prefers over git commit time — its own words: "WEAKER: a refactor touching the
        # file moves this without any tick having run, so it can only make the lane look fresher".
        # ★★ DERIVED, NEVER TYPED (2026-08-01, second pass). The first fix re-pointed these strings at the
        # board fragments and added a test that the two registries AGREE. That is detection, not prevention:
        # a typed path can still diverge, and the agreement test had three escape hatches (a `None` fragment,
        # a lane id absent from the board registry, and a hand-maintained alias map) — any of which lets the
        # same false `UNSUPERVISED-BILLING` back in. So the second home is REMOVED: an entry now names WHICH
        # BOARD LANE it is, and `lane_fragment()` computes the path from `inflight_board`. Divergence is
        # unrepresentable rather than detected (CLAUDE.md §1: a total is DERIVED, never typed).
        "board_lane": "step1-fanout",
        "time_keys": ("_generated_utc",),
        "time_mode": "iso",
        "tick_workflow": "step1-fanout-autoscale.yml",
    },
    {
        # All three ternary lanes (valB replicates, closure triangle, rung 5a-KS) share ONE label prefix and
        # ONE workflow, so the account cannot tell them apart and this module does not pretend to. That is a
        # real limit and it is stated rather than papered over: the per-MODE split is
        # `lane_staleness_watch`'s job, which has the mode-attributed gate snapshots to do it properly. Here
        # the question is only "is SOMETHING reporting for the boxes wearing this prefix", which is exactly
        # the question the account view can answer.
        "key": "ternary-vast",
        "label": "Ternary FEP lanes — valB reps, closure triangle, rung 5a-KS (Vast)",
        "label_prefixes": ("tvast",),
        "prefix_source": "ternary_vast_launch.LABEL_PREFIX",
        # ★★ THE BOARD FRAGMENT IS THE HEARTBEAT, FOR EVERY LANE (2026-08-01). This keyed on
        # ternary-vast-watch.json (a watch LIST, rewritten only when an entry is retired), which stopped being this lane's heartbeat when the in-flight board
        # became universal — so the alarm graded a file the lane no longer writes on every tick and
        # declared UNSUPERVISED-BILLING while the lane was reporting normally. Measured that evening:
        # the alarm's source last moved 6:32/6:39 PM while each lane's board fragment had moved at
        # 8:43/8:44 PM — the lanes had reported ~2 HOURS more recently than the alarm believed.
        # `nrv04-retro` was already on its board fragment; the others were not. One rule, one site.
        # ⚠ AND IT UPGRADES THE STAMP. A board fragment carries an in-file `generated_epoch`, which this
        # module already prefers over git commit time — its own words: "WEAKER: a refactor touching the
        # file moves this without any tick having run, so it can only make the lane look fresher".
        # ★★ DERIVED, NEVER TYPED (2026-08-01, second pass). The first fix re-pointed these strings at the
        # board fragments and added a test that the two registries AGREE. That is detection, not prevention:
        # a typed path can still diverge, and the agreement test had three escape hatches (a `None` fragment,
        # a lane id absent from the board registry, and a hand-maintained alias map) — any of which lets the
        # same false `UNSUPERVISED-BILLING` back in. So the second home is REMOVED: an entry now names WHICH
        # BOARD LANE it is, and `lane_fragment()` computes the path from `inflight_board`. Divergence is
        # unrepresentable rather than detected (CLAUDE.md §1: a total is DERIVED, never typed).
        "board_lane": "ternary",
        "time_keys": ("_generated_utc", "utc", "generated_utc"),
        "time_mode": "iso",
        "tick_workflow": "gpu-ternary-fep-vast.yml",
    },
    {
        "key": "nrv04-retro",
        "label": "NR-V04 retrospective Arm E / R1 endpoint-MD legs (Vast)",
        "label_prefixes": ("nrv04retro-",),
        "prefix_source": "nrv04_retro_panel.LABEL_PREFIX",
        # ★★ DERIVED, NEVER TYPED (2026-08-01, second pass). The first fix re-pointed these strings at the
        # board fragments and added a test that the two registries AGREE. That is detection, not prevention:
        # a typed path can still diverge, and the agreement test had three escape hatches (a `None` fragment,
        # a lane id absent from the board registry, and a hand-maintained alias map) — any of which lets the
        # same false `UNSUPERVISED-BILLING` back in. So the second home is REMOVED: an entry now names WHICH
        # BOARD LANE it is, and `lane_fragment()` computes the path from `inflight_board`. Divergence is
        # unrepresentable rather than detected (CLAUDE.md §1: a total is DERIVED, never typed).
        "board_lane": "nrv04-retro",
        "time_keys": ("generated_utc",),
        "time_mode": "iso",
        "tick_workflow": "fusion-cpu-extras.yml",
    },
    {
        "key": "nrv04-covalent",
        "label": "NR-V04 covalent / co-fold panel (Vast)",
        "label_prefixes": ("nrv04cov-",),
        "prefix_source": "nrv04_covalent_panel.LABEL_PREFIX",
        # ⚠ CAUGHT BY THIS MODULE'S OWN CONTRACT TEST ON ITS FIRST RUN. This entry was first written naming
        # `nrv04-covalent-census.json` and a workflow `nrv04-covalent-vast.yml`, and NEITHER EXISTS — the
        # panel runs from `fusion-cpu-extras.yml` and commits no tick artifact. That is exactly the 2026-07-31
        # defect `test_lane_registry_contract.py` was written for (`nrv04-retro-market-hold.json` was named in
        # three places and had never been committed), reproduced by hand within an hour of writing the rule
        # down — which is why the check exists rather than being left to care.
        "fragment": None,
        "no_fragment_why": ("the covalent panel commits no repo-visible tick artifact — its state lives in "
                            "S3. Stated, not faked: hosts wearing this prefix are graded "
                            "UNWATCHABLE-BILLING rather than quietly assumed healthy."),
        "tick_workflow": "fusion-cpu-extras.yml",
    },
    {
        # ★★ THE LANE TODAY'S FAILURE HAPPENED ON, AND IT WAS REGISTERED WITH NOTHING. Built this morning, it
        # appeared in no cross-lane watcher: `lane_staleness_watch.LANES` did not name it, so its two hosts
        # were invisible to the only thing that looks across lanes. Registering it here is what turns "the
        # selcal tick stopped" into a named alarm instead of an absence — and registering it in
        # `lane_staleness_watch.LANES` too is the other half of the same fix.
        #
        # ⚠ ITS CENSUS CARRIES NO GENERATION STAMP FIELD. `selcal-cofold-census.json` has no `generated_utc`;
        # what it has is `phase`, e.g. "done rc=0 2026-08-01T14:41:08Z instance=46508454 attempt=…". That IS
        # a real tick stamp — only a run that actually executed writes it — so it is extracted rather than
        # falling back to the git commit time, which cannot tell a tick from a refactor. This is why
        # `time_mode` exists at all.
        "key": "selcal-cofold",
        "label": "Selectivity control — SMARCA2/4 co-fold panel (Vast)",
        "label_prefixes": ("selcal-",),
        "prefix_source": "selcal_panel.LABEL_PREFIX",
        # ★★ THE BOARD FRAGMENT IS THE HEARTBEAT, FOR EVERY LANE (2026-08-01). This keyed on
        # selcal-cofold-census.json (the CO-FOLD phase's census, frozen once that phase finished), which stopped being this lane's heartbeat when the in-flight board
        # became universal — so the alarm graded a file the lane no longer writes on every tick and
        # declared UNSUPERVISED-BILLING while the lane was reporting normally. Measured that evening:
        # the alarm's source last moved 6:32/6:39 PM while each lane's board fragment had moved at
        # 8:43/8:44 PM — the lanes had reported ~2 HOURS more recently than the alarm believed.
        # `nrv04-retro` was already on its board fragment; the others were not. One rule, one site.
        # ⚠ AND IT UPGRADES THE STAMP. A board fragment carries an in-file `generated_epoch`, which this
        # module already prefers over git commit time — its own words: "WEAKER: a refactor touching the
        # file moves this without any tick having run, so it can only make the lane look fresher".
        # ★★ DERIVED, NEVER TYPED (2026-08-01, second pass). The first fix re-pointed these strings at the
        # board fragments and added a test that the two registries AGREE. That is detection, not prevention:
        # a typed path can still diverge, and the agreement test had three escape hatches (a `None` fragment,
        # a lane id absent from the board registry, and a hand-maintained alias map) — any of which lets the
        # same false `UNSUPERVISED-BILLING` back in. So the second home is REMOVED: an entry now names WHICH
        # BOARD LANE it is, and `lane_fragment()` computes the path from `inflight_board`. Divergence is
        # unrepresentable rather than detected (CLAUDE.md §1: a total is DERIVED, never typed).
        "board_lane": "selcal-cofold",
        "time_keys": ("phase",),
        "time_mode": "iso_in_string",
        "tick_workflow": "selectivity-control-vast.yml",
    },
    {
        "key": "protfep-bench",
        "label": "Protein-FEP benchmark legs (Vast)",
        "label_prefixes": ("protfep-bench",),
        "prefix_source": "protfep_vast_launch.LABEL_PREFIX",
        "fragment": None,
        "no_fragment_why": ("this lane commits no repo-visible tick artifact — its state lives in S3 and in "
                            "the launch ledger. Stated, not faked (§4): a host wearing this prefix is graded "
                            "UNWATCHABLE-BILLING rather than quietly assumed healthy."),
        "tick_workflow": "gpu-protfep-vast.yml",
    },
    {
        "key": "vast-bench-sweep",
        "label": "Vast card-calibration sweep (throughput benchmarking)",
        "label_prefixes": ("cal-",),
        "prefix_source": "vast_bench_sweep.LABEL_PREFIX",
        "fragment": None,
        "no_fragment_why": ("a short-lived calibration rental with no committed tick artifact. Stated, not "
                            "faked: hosts wearing this prefix are graded UNWATCHABLE-BILLING."),
        "tick_workflow": "vast-bench-sweep.yml",
    },
    {
        "key": "nr4a-paralogue-md",
        "label": "NR4A paralogue MD (Vast)",
        "label_prefixes": ("nr4a-pdyn",),
        "prefix_source": "nr4a_paralogue_md_ops.LABEL_PREFIX",
        "fragment": None,
        "no_fragment_why": ("no committed tick artifact for this lane. Stated, not faked: hosts wearing this "
                            "prefix are graded UNWATCHABLE-BILLING."),
        "tick_workflow": "gpu-nr4a-paralogue-md-vast.yml",
    },
]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# time helpers
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _et(ts: datetime.datetime | None) -> str | None:
    """CLAUDE.md §1: every time reported is US Eastern, 12-hour. Converted here so no caller can forget."""
    return ts.astimezone(ET).strftime("%I:%M %p ET %b %d, %Y").lstrip("0").replace(" 0", " ") if ts else None


def _z(ts: datetime.datetime | None) -> str | None:
    return ts.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None


def parse_z(s) -> datetime.datetime | None:
    """ISO-Z -> aware datetime, or None. NEVER raises and never guesses: a malformed stamp is UNREADABLE, not
    'the epoch'. A silently-defaulted timestamp is an unmeasured state wearing a measured one's clothes."""
    if not isinstance(s, str):
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            t = datetime.datetime.strptime(s.strip(), fmt)
            return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def _age_min(then: datetime.datetime | None, now: datetime.datetime) -> float | None:
    return None if then is None else (now - then).total_seconds() / 60.0


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# reading — every reader returns (value, why_not); NOTHING coalesces an error into a default
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def load_json(path: str) -> tuple[dict | None, str | None]:
    """`(doc, why_not)`. A missing OR corrupt file returns a REASON, so nothing downstream can read the
    absence as an empty document. This is the `_load_ledger` defect that once reported a swallowed S3 error
    as "realised $0.0, breached=False" — absent is never a legal good value."""
    if not os.path.exists(path):
        return None, f"{os.path.basename(path)}: not present at {path}"
    try:
        with open(path) as fh:
            doc = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{os.path.basename(path)}: unreadable ({type(e).__name__}: {e})"
    if not isinstance(doc, dict):
        return None, f"{os.path.basename(path)}: not a JSON object"
    return doc, None


def fragment_stamp(spec: dict, doc: dict | None) -> tuple[datetime.datetime | None, str | None]:
    """PURE. The lane's own in-file tick stamp -> `(when, why_not)`. The STRONG freshness basis: only a run
    that actually executed writes one, which is the property CLAUDE.md §4 demands — check the thing only a
    real run can produce, never the thing a default can fill in."""
    keys = tuple(spec.get("time_keys") or ())
    if not keys:
        return None, "no in-file time key is declared for this lane"
    if doc is None:
        return None, "the fragment could not be read"
    mode = spec.get("time_mode") or "iso"
    tried = []
    for k in keys:
        if k not in doc:
            tried.append(f"{k}: absent")
            continue
        raw = doc.get(k)
        if mode == "iso_in_string":
            m = _ISO_Z.search(raw) if isinstance(raw, str) else None
            got = parse_z(m.group(0)) if m else None
            if got:
                return got, None
            tried.append(f"{k}: present but contains no ISO-Z stamp")
            continue
        got = parse_z(raw)
        if got:
            return got, None
        tried.append(f"{k}: present but unparseable ({raw!r})")
    return None, "; ".join(tried)


def git_commit_time(root: str, rel: str) -> tuple[datetime.datetime | None, str | None]:
    """The WEAK freshness basis: when git last committed this path.

    ⚠ WHY IT IS WEAK AND IS ALWAYS LABELLED AS SUCH. An unrelated refactor that touches the file moves this
    stamp without any tick having run, so its error direction is always "looks fresher than it is" — the
    dangerous direction. It exists because it is the ONLY freshness source that works for a lane that has not
    adopted any stamp convention, i.e. for the lanes this alarm is most likely to be surprised by. A verdict
    resting on it says so in `freshness_basis` (§4: a populated field is not a measured one).
    """
    try:
        p = subprocess.run(["git", "-C", root, "log", "-1", "--format=%cI", "--", rel],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError) as e:
        return None, f"git log failed ({type(e).__name__}: {e})"
    if p.returncode != 0:
        return None, f"git log exited {p.returncode}: {(p.stderr or '').strip()[:160]}"
    out = (p.stdout or "").strip()
    if not out:
        return None, "git has no commit touching this path"
    try:
        return datetime.datetime.fromisoformat(out).astimezone(datetime.timezone.utc), None
    except ValueError:
        return None, f"git returned an unparseable date {out!r}"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# attribution — which lane owns which box
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def match_lane(label: str | None, lanes: list[dict]) -> dict | None:
    """PURE. Label -> the lane whose prefix claims it, or None (the ORPHAN case).

    ★ LONGEST PREFIX WINS. Prefixes are not guaranteed disjoint forever, and a shorter one silently
    swallowing a longer one's boxes would misattribute a live lane's hosts to a quiet lane — which reads as
    healthy and is the exact class of error this module exists to stop. Deterministic by construction rather
    than by registry ordering, so adding a lane cannot re-attribute an existing one.
    """
    if not isinstance(label, str) or not label:
        return None
    best, best_len = None, -1
    for spec in lanes:
        for pref in spec.get("label_prefixes") or ():
            if label.startswith(pref) and len(pref) > best_len:
                best, best_len = spec, len(pref)
    return best


def instance_row(inst: dict, lane_key: str | None) -> dict:
    """One census instance -> the fields a human needs to act, and NOTHING inferred.

    ⚠ `gpu_util` IS NOT COPIED HERE AND MUST NEVER BE. `vast_idle_guard`'s inviolable rule is that GPU
    idleness NEVER condemns a box; both of today's selcal instances read 0.0 including the working one. The
    dollar fields are the census's OWN values quoted back, not a computed rate (§1: one fact, one home).
    """
    status = str(inst.get("actual_status") or "").lower()
    cur = str(inst.get("cur_state") or "").lower()
    return {
        "instance": inst.get("id"),
        "machine_id": inst.get("machine_id"),
        "label": inst.get("label"),
        "lane": lane_key,
        "actual_status": inst.get("actual_status"),
        "cur_state": inst.get("cur_state"),
        "intended_status": inst.get("intended_status"),
        "gpu_name": inst.get("gpu_name"),
        "uptime_h": inst.get("uptime_h"),
        # Quoted from the census, never recomputed. `occupies_slot` is REPORTED and is deliberately not
        # interpreted as "is billing" — that would be a "probably" (§4).
        "dph_total": inst.get("dph_total"),
        "spend_so_far_usd": inst.get("spend_so_far_usd"),
        "occupies_slot": inst.get("occupies_slot"),
        "terminal_but_listed": (status in TERMINAL_STATES) or (cur in TERMINAL_STATES),
    }


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# classification — PURE over already-loaded state, so every branch is testable with no filesystem
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
OK_VERDICTS = {"SUPERVISED", "IDLE", "IDLE-STALE-NO-HOSTS"}
ALARM_VERDICTS = {"UNSUPERVISED-BILLING", "ORPHAN-HOST", "UNWATCHABLE-BILLING", "LANE-UNKNOWN"}


def classify_lane(spec: dict, rows: list[dict], stamp: datetime.datetime | None, basis: str | None,
                  why_not: str | None, now: datetime.datetime, *,
                  lane_silent_min: float = DEFAULT_LANE_SILENT_MIN,
                  future_skew_min: float = DEFAULT_FUTURE_SKEW_MIN) -> dict:
    """One lane + the boxes wearing its prefix -> one verdict. ORDER IS THE DISCRIMINATION:

        no hosts        FIRST and unconditionally OK. A lane with nothing billing costs nothing while it is
                        silent, so its staleness is NOT an incident — this is the half of the pair that keeps
                        the alarm quiet on every finished and every parked lane, forever. Grading staleness
                        before hosts is how an alarm becomes noise nobody reads by tomorrow.
        no fragment     a lane holding hosts with no repo-visible tick evidence at all. NOT gradeable, and
                        "not gradeable while billing" is louder than stale, not quieter.
        unreadable      holding hosts and its freshness could not be read -> LANE-UNKNOWN. Never OK: an
                        unmeasured state rendered as a measured zero is this repo's most expensive defect.
        stale + hosts   ★ THE ALARM. Today's failure.
        fresh + hosts   SUPERVISED.
    """
    live = [r for r in rows if not r["terminal_but_listed"]]
    terminal = [r for r in rows if r["terminal_but_listed"]]
    age = _age_min(stamp, now)
    v: dict = {
        "lane": spec["key"], "label": spec.get("label"),
        "tick_workflow": spec.get("tick_workflow"),
        "fragment": lane_fragment(spec),
        "label_prefixes": list(spec.get("label_prefixes") or ()),
        "n_instances": len(rows), "n_live": len(live), "n_terminal_but_listed": len(terminal),
        "instances": rows,
        "last_report_utc": _z(stamp), "last_report_et": _et(stamp),
        "freshness_basis": basis,
        "silent_for_min": round(age, 1) if age is not None else None,
        "threshold_min": lane_silent_min,
        "future_skew_tolerance_min": future_skew_min,
    }

    # ── 1. no hosts: OK whatever the age. THE HALF OF THE PAIR THAT BUYS THE SILENCE. ──
    if not rows:
        v["verdict"], v["ok"] = "IDLE", True
        v["detail"] = ("no instance in the account wears this lane's prefix, so nothing is billing for it. "
                       "Its artifact age is NOT graded here on purpose: a finished or parked lane is silent "
                       "forever and firing on that would make this alarm unreadable within a day. Whether "
                       "the lane SHOULD have work running is `lane_staleness_watch`'s question, not this "
                       "one — this module only asks whether money is moving unwatched.")
        return v

    # ── 2. holding hosts with no tick artifact at all ──
    if not lane_fragment(spec):
        v["verdict"], v["ok"] = "UNWATCHABLE-BILLING", False
        v["detail"] = (f"{len(rows)} instance(s) wear this lane's prefix, and the lane commits NO repo-visible "
                       f"tick artifact, so whether anything is watching them cannot be determined from here. "
                       f"{spec.get('no_fragment_why') or ''} This is reported as an alarm rather than as OK "
                       f"because 'I cannot tell' about a billing host is worse news than 'it is stale', not "
                       f"better (§4: an absent reading is not a reading of absence).").strip()
        return v

    # ── 3. holding hosts and freshness unreadable ──
    if stamp is None:
        v["verdict"], v["ok"] = "LANE-UNKNOWN", False
        v["detail"] = (f"{len(rows)} instance(s) wear this lane's prefix and its last-report time could not "
                       f"be read ({why_not or 'unknown'}), so 'billing and watched' cannot be separated from "
                       f"'billing and abandoned'. Not graded OK — guessing is precisely where this costs "
                       f"money.")
        return v

    # ── 3b. a stamp from the FUTURE is not a fresh lane, it is an unbelievable reading ──
    # It must be checked BEFORE the staleness branch, because a negative age passes that branch silently and
    # would make this alarm permanently quiet for the lane — failing open, in the one place the whole module
    # is supposed to fail closed.
    if age is not None and age < -future_skew_min:
        v["verdict"], v["ok"] = "LANE-UNKNOWN", False
        v["detail"] = (f"{len(rows)} instance(s) wear this lane's prefix and its last report is stamped "
                       f"{_et(stamp)}, which is {-age:.0f} min IN THE FUTURE (tolerance "
                       f"{future_skew_min:.0f} min). A future stamp is not a fresh lane — it is a reading "
                       f"that cannot be believed, from a skewed clock, a mis-zoned timestamp, or a field "
                       f"populated from ENV rather than from what ran. Graded UNKNOWN rather than fresh "
                       f"because a negative age would otherwise silence this alarm for this lane forever.")
        return v

    # ── 4. ★ THE ALARM: stale AND holding hosts ──
    if age is not None and age >= lane_silent_min:
        v["verdict"], v["ok"] = "UNSUPERVISED-BILLING", False
        ids = ", ".join(str(r["instance"]) for r in rows)
        v["detail"] = (
            f"{len(rows)} instance(s) [{ids}] wear this lane's prefix and the lane has not reported for "
            f"{age:.0f} min (threshold {lane_silent_min:.0f}); last report {_et(stamp)} via {basis}. "
            f"MONEY IS MOVING AND NOTHING IS WATCHING IT. The lane's own supervisor cannot report this — "
            f"when it stalls, the only thing that would notice is the thing that stopped, which is why this "
            f"check is keyed on the ACCOUNT. Check {spec.get('tick_workflow')} for a run that is "
            f"`in_progress` but producing no ticks. ⚠ THIS MODULE HAS NOT ACTED AND WILL NOT: it never "
            f"destroys, stops or rents. Only the control plane may end a rental "
            f"(`vast_idle_guard.py`), and only on a measured absence of WRITES — never on GPU idleness.")
        if any(r["terminal_but_listed"] for r in rows):
            v["detail"] += (" NOTE some of these are TERMINAL BUT STILL LISTED — see `terminal_but_listed`; "
                            "a host cannot destroy itself (§6), so a terminal instance persists until the "
                            "control plane clears it.")
        return v

    # ── 5. fresh, holding hosts ──
    v["verdict"], v["ok"] = "SUPERVISED", True
    v["detail"] = (f"{len(rows)} instance(s) up and the lane reported {age:.0f} min ago ({_et(stamp)}, via "
                   f"{basis}) — inside the {lane_silent_min:.0f} min window. Something is watching this money.")
    if terminal:
        # Reported, not alarmed: a fresh lane's own tick is the thing that reaps, and this module must not
        # duplicate that judgement. But it is never FILTERED OUT — today's host was `exited` and invisible.
        v["detail"] += (f" ⚠ {len(terminal)} instance(s) are TERMINAL BUT STILL LISTED "
                        f"({', '.join(str(r['instance']) for r in terminal)}): they have not been destroyed. "
                        f"Not alarmed because the lane IS reporting and its own tick owns the reap — but "
                        f"surfaced, because nothing else surfaces them.")
    return v


def _ungraded(rep: dict) -> None:
    """Mark a fail-closed report as HAVING GRADED NOTHING — with `null`, never with `[]`.

    ★★ THE DISTINCTION IS THE WHOLE POINT OF THE FAIL-CLOSED PATH, AND IT WAS BRIEFLY LOST HERE. These keys
    were first set to `[]`, which reads as "I looked and there were no lanes in trouble, no orphans, and no
    terminal instances" — a READING OF ABSENCE. What actually happened is that nothing was looked at, which
    is an ABSENT READING (§4). A consumer cannot tell those apart from `[]`, and the whole reason this branch
    exists is that the two are opposite facts. `null` + `graded: false` says the true thing.

    ⚠ CAUGHT IN PRODUCTION ON THE FIRST CI RUN, not in review: the run went CENSUS-STALE, returned early, and
    the artifact simply had no `terminal_but_listed` key at all — a reader indexing it got a KeyError, and a
    reader using `.get(..., [])` would have been told there were no terminal instances on a census nobody had
    read. Both keys are now always present, and always honest about which of the two they mean.
    """
    rep["graded"] = False
    rep["lanes"] = None
    rep["orphans"] = None
    rep["terminal_but_listed"] = None


def build_report(census: dict | None, census_err: str | None, lane_reads: dict, now: datetime.datetime, *,
                 lanes: list[dict] | None = None,
                 lane_silent_min: float = DEFAULT_LANE_SILENT_MIN,
                 census_stale_min: float = DEFAULT_CENSUS_STALE_MIN,
                 future_skew_min: float = DEFAULT_FUTURE_SKEW_MIN) -> dict:
    """PURE. The whole verdict, from already-loaded state.

    `lane_reads` maps lane key -> `(stamp, basis, why_not)`, so every filesystem and git touch happens in the
    caller and every branch below is testable without either.

    ★★ FAIL CLOSED, IN BOTH ABSENCES, BEFORE ANY LANE IS GRADED (§4). An unreadable census and a census
    reporting zero instances are OPPOSITE facts that a naive check renders identically, and today the census
    was 155 min stale at one point — a moment when "I see no instances" was true of the FILE and false of the
    ACCOUNT. So neither absence is allowed to reach the lane loop at all: nothing is graded, and no lane is
    called healthy on a reading that does not exist.
    """
    lanes = lanes if lanes is not None else ACCOUNT_LANES
    rep: dict = {
        "_what": ("cross-lane, ACCOUNT-KEYED alarm: is any host billing whose lane has stopped reporting? "
                  "Keyed on the Vast account because a lane-scoped watcher structurally cannot see a host "
                  "whose lane stopped. REPORT-ONLY: this never destroys, stops, reaps, nudges or rents."),
        "generated_utc": _z(now), "generated_et": _et(now),
        "thresholds": {"lane_silent_min": lane_silent_min, "census_stale_min": census_stale_min,
                       "future_skew_min": future_skew_min},
        "report_only": True,
    }

    if census is None:
        rep["verdict"], rep["ok"] = "CENSUS-UNKNOWN", False
        rep["detail"] = (
            f"the account census could not be read ({census_err or 'unknown'}), so NOTHING is graded and no "
            f"lane is called healthy. An absent reading is not a reading of absence (§4): 'I cannot see any "
            f"instance' and 'there is no instance' are opposite facts and only one of them is good news. "
            f"Fix the census before believing any all-clear.")
        _ungraded(rep)
        return rep

    c_utc = parse_z(census.get("utc"))
    c_age = _age_min(c_utc, now)
    rep["census_utc"], rep["census_et"] = _z(c_utc), _et(c_utc)
    rep["census_age_min"] = round(c_age, 1) if c_age is not None else None
    rep["census_n_instances"] = census.get("n_instances")

    if c_utc is None:
        rep["verdict"], rep["ok"] = "CENSUS-UNKNOWN", False
        rep["detail"] = ("the account census carries no parseable `utc`, so its age is unknown and it cannot "
                         "be used as evidence of what the account holds. NOTHING is graded.")
        _ungraded(rep)
        return rep

    if c_age is not None and c_age >= census_stale_min:
        rep["verdict"], rep["ok"] = "CENSUS-STALE", False
        rep["detail"] = (
            f"the account census is {c_age:.0f} min old (stamped {_et(c_utc)}; threshold "
            f"{census_stale_min:.0f} min), so it is NOT treated as a weaker reading — it is not treated as a "
            f"reading at all, and every lane verdict is suppressed. Measured today: it went 155 min stale, a "
            f"window in which a naive check would have reported all-clear while two hosts were up. The "
            f"census writer is a diagnostic task dispatched from a supervisor loop; if it has stopped, that "
            f"is the incident.")
        _ungraded(rep)
        return rep

    insts = census.get("instances")
    if not isinstance(insts, list):
        rep["verdict"], rep["ok"] = "CENSUS-UNKNOWN", False
        rep["detail"] = ("the account census has no `instances` list, so what the account holds is unknown. "
                         "NOTHING is graded — an unparseable census is not an empty account.")
        _ungraded(rep)
        return rep

    # ── attribute every instance ──
    by_lane: dict[str, list[dict]] = {s["key"]: [] for s in lanes}
    orphans: list[dict] = []
    for inst in insts:
        if not isinstance(inst, dict):
            continue
        spec = match_lane(inst.get("label"), lanes)
        row = instance_row(inst, spec["key"] if spec else None)
        (by_lane[spec["key"]] if spec else orphans).append(row)

    rep["graded"] = True
    lane_verdicts = []
    for spec in lanes:
        stamp, basis, why_not = lane_reads.get(spec["key"], (None, None, "no read was attempted"))
        lane_verdicts.append(classify_lane(spec, by_lane[spec["key"]], stamp, basis, why_not, now,
                                           lane_silent_min=lane_silent_min,
                                           future_skew_min=future_skew_min))
    rep["lanes"] = lane_verdicts

    # ── orphans: a box whose prefix NO registered lane claims ──
    rep["orphans"] = orphans
    if orphans:
        rep["orphan_detail"] = (
            f"{len(orphans)} instance(s) wear a label prefix that NO registered lane claims: "
            + "; ".join(f"{o['instance']} {o['label']!r} ({o['actual_status']})" for o in orphans)
            + ". Either a lane was built without being registered here — which is what made today's failure "
              "invisible — or these are leftovers nothing owns. A host cannot destroy itself (§6), so an "
              "unclaimed instance persists until the control plane clears it. REPORTED ONLY; nothing here "
              "acts on it.")

    # ── terminal-but-listed, gathered across every lane AND the orphans, because nothing else gathers them ──
    terminal_all = [r for lv in lane_verdicts for r in lv["instances"] if r["terminal_but_listed"]]
    terminal_all += [o for o in orphans if o["terminal_but_listed"]]
    rep["terminal_but_listed"] = terminal_all
    if terminal_all:
        rep["terminal_detail"] = (
            f"{len(terminal_all)} instance(s) are in a TERMINAL state and STILL LISTED in the account: "
            + "; ".join(f"{r['instance']} {r['label']!r} actual_status={r['actual_status']!r} "
                        f"cur_state={r['cur_state']!r} occupies_slot={r['occupies_slot']!r}"
                        for r in terminal_all)
            + ". They have not been destroyed. Whether they are still billing is NOT knowable from this "
              "record and is not claimed here (§4); what IS measured is that they persist, and that the host "
              "cannot end its own rental — only the control plane can (§6). Today's failure was exactly "
              "this: an `exited` instance that every lane-scoped check filtered out of view. WHO CLEARS "
              "THEM: `vast_account_reaper.py` (RULE 1), which is account-keyed like this alarm and destroys "
              "on terminal state alone — one central actor rather than each lane's private teardown path, "
              "four of which were broken at once on 2026-08-01. ⚠ THIS MODULE STILL ACTS ON NOTHING; the "
              "reaper is a SEPARATE module with a separate workflow and the separate blast radius that "
              "justifies, and the dependency runs one way (reaper imports this alarm's readers, never the "
              "reverse) so this alarm stays trustworthy on every lane.")

    bad = [lv for lv in lane_verdicts if not lv["ok"]]
    rep["ok"] = not bad and not orphans
    if bad:
        rep["verdict"] = sorted({lv["verdict"] for lv in bad})[0] if len(
            {lv["verdict"] for lv in bad}) == 1 else "MULTIPLE"
        rep["detail"] = "; ".join(f"{lv['lane']}: {lv['verdict']}" for lv in bad)
        if orphans:
            rep["detail"] += f"; plus {len(orphans)} orphan instance(s)"
    elif orphans:
        rep["verdict"] = "ORPHAN-HOST"
        rep["detail"] = rep["orphan_detail"]
    else:
        rep["verdict"] = "ALL-SUPERVISED"
        rep["detail"] = (f"every instance in the account belongs to a lane that has reported inside "
                         f"{lane_silent_min:.0f} min, and no instance wears an unclaimed prefix.")
    return rep


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# impure edges
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def read_lane_freshness(root: str, spec: dict, *, use_git: bool = True
                        ) -> tuple[datetime.datetime | None, str | None, str | None]:
    """`(stamp, basis, why_not)` for one lane. The ONLY impure lane read.

    Order is strong-then-weak, and the basis string always names which one actually produced the answer, so
    no reader can mistake the fallback for a tick (§4: a populated field is not a measured one)."""
    frag = lane_fragment(spec)
    if not frag:
        return None, None, "this lane declares no repo-visible tick artifact"
    path = os.path.join(root, frag)
    doc, err = load_json(path)
    stamp, why = fragment_stamp(spec, doc)
    if stamp is not None:
        return stamp, f"in-file stamp ({', '.join(spec.get('time_keys') or ())}) in {frag}", None
    if not use_git:
        return None, None, f"{err or why}; git fallback disabled"
    g, gerr = git_commit_time(root, frag)
    if g is not None:
        return g, (f"git commit time of {frag} — WEAKER: a refactor touching the file moves this without any "
                   f"tick having run, so it can only make the lane look fresher than it is "
                   f"(in-file stamp unavailable: {err or why})"), None
    return None, None, f"in-file: {err or why}; git: {gerr}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=HERE, help="repo dir holding the lane artifacts")
    ap.add_argument("--census", default=None, help="path to ternary-vast-account-census.json")
    ap.add_argument("--json", dest="out", default=None, help="write the full report here")
    ap.add_argument("--now", default=None, help="ISO8601Z override, for tests")
    ap.add_argument("--lane-silent-min", type=float, default=DEFAULT_LANE_SILENT_MIN)
    ap.add_argument("--census-stale-min", type=float, default=DEFAULT_CENSUS_STALE_MIN)
    ap.add_argument("--future-skew-min", type=float, default=DEFAULT_FUTURE_SKEW_MIN,
                    help="how far a lane stamp may sit in the future before it is disbelieved")
    ap.add_argument("--no-git", action="store_true", help="disable the weak git-commit-time freshness basis")
    a = ap.parse_args(argv)

    now = parse_z(a.now) if a.now else datetime.datetime.now(datetime.timezone.utc)
    if now is None:
        print(f"[account-orphan-alarm] --now {a.now!r} is not ISO8601Z", file=sys.stderr)
        return 2

    census_path = a.census or os.path.join(a.root, "ternary-vast-account-census.json")
    census, census_err = load_json(census_path)
    reads = {s["key"]: read_lane_freshness(a.root, s, use_git=not a.no_git) for s in ACCOUNT_LANES}
    rep = build_report(census, census_err, reads, now,
                       lane_silent_min=a.lane_silent_min, census_stale_min=a.census_stale_min,
                       future_skew_min=a.future_skew_min)

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
        with open(a.out, "w") as fh:
            json.dump(rep, fh, indent=1, sort_keys=False)
            fh.write("\n")

    print(render(rep))
    return 0 if rep.get("ok") else 1


def render(rep: dict) -> str:
    """Human readout. Times US Eastern 12-hour (§1) because `_et` is the only formatter used anywhere here."""
    L = [f"═══ ACCOUNT-KEYED CROSS-LANE ALARM — {rep.get('verdict')} ═══",
         f"as of {rep.get('generated_et')}   (REPORT-ONLY: destroys nothing, rents nothing)"]
    if rep.get("census_et"):
        L.append(f"account census: {rep.get('census_n_instances')} instance(s), stamped "
                 f"{rep['census_et']} ({rep.get('census_age_min')} min old)")
    L.append("")
    for lv in rep.get("lanes") or []:
        mark = "  ok " if lv["ok"] else "★ ALARM"
        L.append(f"{mark}  {lv['lane']:<18} {lv['verdict']:<22} "
                 f"{lv['n_instances']} host(s), silent {lv['silent_for_min']} min")
        L.append(f"          {lv['detail']}")
        for r in lv["instances"]:
            flag = "  ⚠ TERMINAL-BUT-LISTED" if r["terminal_but_listed"] else ""
            L.append(f"            {r['instance']}  {r['gpu_name']}  {r['actual_status']}/{r['cur_state']}  "
                     f"{r['label']}{flag}")
    if rep.get("orphans"):
        L.append("")
        L.append(f"★ ALARM  ORPHAN HOSTS — {rep.get('orphan_detail')}")
        for o in rep["orphans"]:
            L.append(f"            {o['instance']}  {o['gpu_name']}  {o['actual_status']}/{o['cur_state']}  "
                     f"{o['label']}")
    if rep.get("terminal_detail"):
        L.append("")
        L.append(f"⚠ TERMINAL BUT STILL LISTED — {rep['terminal_detail']}")
    if not rep.get("ok"):
        L.append("")
        L.append(f"VERDICT: {rep.get('verdict')} — {rep.get('detail')}")
    return "\n".join(L)


if __name__ == "__main__":
    raise SystemExit(main())
