#!/usr/bin/env bash
# Body of .github/workflows/ternary-leg-watchdog.yml — kept in a FILE, deliberately.
#
# WHY A FILE. It lived inline in the workflow's `run:` block and outgrew GitHub's limit: a `run:` body is treated
# as a template (it may contain ${{ }}) and is capped at 21,000 characters. At 23,453 the workflow stopped
# parsing, and GitHub's symptom is
#     422 Invalid Argument - failed to parse workflow: Exceeded max expression length 21000
# on the DISPATCH, while a `schedule:` cron on an unparseable file simply never fires. That is the second time
# this workflow was silently disabled by a parse failure (the first was column-0 Python inside the block scalar,
# see watchdog_validate.py) — so the body moves out of the YAML for good. A file has no expression cap, can be
# `bash -n`'d directly instead of scraped back out of YAML, and cannot dedent itself out of a block scalar.
#
# GitHub expressions do NOT work here. The one that was needed, `github.ref_name`, arrives as $WATCH_REF.
#
# Contract: run from the repo root with GH_TOKEN, DRY and WATCH_REF exported, and gcloud already authenticated.
set +e                    # belt and braces: -e must stay OFF even if the caller sets it.
                          # One entry failing must not abandon the others, and a no-match grep in a
                          # census is a normal reading (no commits yet), not an error.
: "${WATCH_REF:?WATCH_REF must be set (the ref to dispatch relaunches on)}"
: "${DRY:=0}"
PROJECT=project-a7ebde30-e2ed-4b8d-9a9
BUCKET="$PROJECT-rbfe-ckpt"
RESULTS="gs://$BUCKET/valB-6hax/results"
WDIR="gs://$BUCKET/valB-6hax/watchdog"
CFG=research/modalities/ternary-watch.json
gcloud config set project "$PROJECT" >/dev/null 2>&1

# VALIDATE FIRST. The watchdog relaunches a leg from these values alone, so an entry missing a
# parameter that KEYS THE COMMIT PREFIX would resume a different trajectory than the one it is
# watching -- the direction-blind-key bug class this lane was audited for, reproduced inside the
# watchdog itself (the first version of this file omitted warmup_timestep_fs, which keys `wu<..>`).
# Refuse to act on an incomplete list rather than relaunching the wrong thing.
if ! python3 research/modalities/watchdog_validate.py "$CFG"; then
  echo "watch list is invalid — see the annotation above. Failing rather than relaunching the wrong run."
  exit 1
fi

N=$(python3 -c "import json;d=json.load(open('$CFG'));print(len([w for w in d['watch'] if w.get('enabled')]))")
echo "enabled watch entries: $N   (dry_run=$DRY)"

# An ::error:: annotation that nobody opens is no better than the silent stall this workflow exists
# to remove. So a stall / cap / failed dispatch also FAILS THE JOB, which makes GitHub send its own
# workflow-failure notification out-of-band — the alert path that does not depend on an agent, a
# session, or anyone thinking to look. RUNNING and DONE stay green so the mailbox stays quiet.
# The entry loop is a pipeline subshell, so the flag has to live in a file, not a variable.
# ⚠ INITIALISED HERE, ABOVE THE IDLE EXIT, DELIBERATELY. It used to be created below the `N = 0`
# branch, which meant the one pass that most needs to raise an alarm — an idle list with a VM still
# up — had no file to write one to. Moving it up is what lets orphan_sweep() run on a COLD pass.
ALERT=/tmp/watchdog-alert; rm -f "$ALERT"
# Units that reached the TERMINAL done state this pass (result + both follow-ups dispatched). Collected here
# and reaped once at the end rather than per-entry, so one commit covers the whole pass.
REAP=/tmp/watchdog-reap; rm -f "$REAP"; : > "$REAP"

# one live-VM listing shared by every entry (the 1-GPU quota means there is at most one anyway)
VMS=$(gcloud compute instances list --filter="name~'^gcp-ternary-'" \
        --format="value(name,status)" 2>/dev/null)
# keep this strictly numeric: a stray space makes `[ "$NVM" -gt 0 ]` throw "integer expression
# expected" and kill the entry mid-loop, which is exactly the silent-skip failure mode this
# workflow exists to remove.
NVM=$(printf '%s' "$VMS" | tr -d '[:space:]' | wc -c | tr -dc '0-9'); NVM=${NVM:-0}
echo "live gcp-ternary VMs: ${VMS:-<none>}"

# AGE of the oldest live VM, in minutes. Needed to tell "no commits yet because it is still in
# env-solve/stage/solvate/minimize" (normal, tens of minutes) from "no commits because it is hung"
# (the ~40-min am1bcc cold-cache stall and the ~15-min 25000-step minimize both looked exactly like
# a healthy VM from the outside). Empty listing -> 0.
VMAGE=0; VMEPOCH=0
CREATED=$(gcloud compute instances list --filter="name~'^gcp-ternary-'" \
            --format="value(creationTimestamp)" 2>/dev/null | sort | head -1)
if [ -n "$CREATED" ]; then
  CS=$(date -u -d "$CREATED" +%s 2>/dev/null | tr -dc '0-9')
  [ -n "$CS" ] && { VMEPOCH=$((10#$CS)); VMAGE=$(( ( $(date -u +%s) - VMEPOCH ) / 60 )); }; true
fi
case "$VMAGE" in ""|*[!0-9]*) VMAGE=0 ;; esac
echo "oldest live VM age: ${VMAGE} min (created ${CREATED:-<none>})"

# Grace period before "no commits at all" is called a stall, and the number of consecutive
# no-advance passes before a frozen iteration counter is called a stall.
#
# STALL_PASSES=3, RAISED FROM 2 ON A MEASURED RATE (2026-07-25). The leg logs 33.91 s/iteration, so with
# RBFE_PROD_CKPT_ITERS=40 a HEALTHY production leg commits only every ~22.6 min. At cron */15, two consecutive
# no-advance passes is ~30 min — uncomfortably close to that 22.6, so a slow resume or a chunk boundary would
# raise a FALSE stall. Three passes is ~45 min, comfortably clear of one commit interval while still catching a
# real stall within the hour. The earlier value of 2 was chosen against a guessed "~20-min" granularity before
# the rate was measured; 22.6 min is the measurement.
#
# A false positive here costs an email, not a leg — STALLED neither relaunches nor reaps — but an alarm that
# cries wolf is one people stop reading, which is the failure this whole watchdog exists to avoid.
SETUP_GRACE_MIN=75
STALL_PASSES=3

# `provisioning` defaults to spot, matching the standing rule. It is read from config rather than hardcoded so
# a switch to on-demand is a one-line config edit -- gpu-ternary-fep-gcp.yml gates 'standard' on being
# "explicitly authorized for a time-sensitive one-off", so the VALUE is a human decision, but the PLUMBING
# should not also require a code change. This was the third hardcoded value found in this dispatch after
# DIRECTION and use_preequil.
# `restrain` is read here for the same reason, and it is the FOURTH hardcoded value found in this dispatch.
# It is not cosmetic: `restrain=1` adds a flat-bottom pocket restraint, which is a DIFFERENT HAMILTONIAN, and
# it keys BOTH the spot commit prefix (`_rst`) and the leg result file. A watchdog that does not carry it
# fails in two directions at once on a restrained leg:
#   * the DONE check below would `ls` the UNRESTRAINED result -- which, for the r0 binary arm, is ALREADY IN
#     THE BUCKET -- and declare a leg done that had not started, chaining converge+reduce off a stale file;
#   * a relaunch would dispatch restrain=0, i.e. an UNRESTRAINED leg at an UNRESTRAINED prefix, so it would
#     not resume the restrained trajectory it was supposed to rescue -- it would quietly start a different
#     calculation and the watch entry would report it as the same leg.
# Defaults to '0', so every existing entry behaves byte-identically.
# ===== CAPABILITY HANDSHAKE: A WATCHDOG THAT CANNOT HONOUR THIS CONFIG MUST REFUSE, NOT IMPROVISE =====
# WHAT IT DEFENDS AGAINST, stated precisely so nobody over-trusts it. `actions/checkout@v4` in
# ternary-leg-watchdog.yml takes NO `ref`, so this script and ternary-watch.json are ALWAYS checked out
# together from one ref -- a config-new/code-old pair cannot arise from a normal run. The paths that CAN
# produce one are (a) a selective merge that forwards the JSON without the script, and (b) the divergent
# private copies this repo already knows about (ternary-watch.json's own `_required_keys_are_enforced` note
# warns that another session may hold an older watchdog_validate.py).
#
# The danger in those cases is specific and expensive: an older watchdog reads an entry it does not
# understand, silently drops the field, and then measures the WRONG ARTIFACT -- for restrain=1 it would `ls`
# the UNRESTRAINED result, which for the r0 binary arm is already in the bucket, and report a green DONE for
# a leg that never ran while leaving its VM holding GPUS_ALL_REGIONS=1.
#
# HONEST LIMIT: this cannot protect against a watchdog older than the handshake itself, because such a copy
# does not read the key. It closes the window from here forward, which is the only thing a handshake can do.
# The python below is deliberately ONE LINE. A multi-line `python3 -c "..."` here is indentation-fragile in
# both directions and this file has been bitten by that class twice: watchdog_validate.py exists at all
# because inline python at column 0 dedented out of a YAML block scalar and made the workflow unparseable
# (GitHub then reports a MISSING TRIGGER, so the cron silently never fires), and the first cut of this very
# block was re-indented by the test that extracts it and died with IndentationError. A single line cannot be
# re-indented into invalidity by anything that quotes it.
WATCHDOG_FEATURES="restraint_keyed_result_v1"
MISSING=$(python3 -c "import json;d=json.load(open('$CFG'));have=set('$WATCHDOG_FEATURES'.split());print(' '.join(f for f in (d.get('_requires_watchdog_features') or []) if f not in have))") || { echo "::error title=WATCHDOG CONFIG UNREADABLE::could not parse $CFG for its feature requirements — refusing to act on a config this script cannot read."; exit 1; }
if [ -n "$MISSING" ]; then
  echo "::error title=WATCHDOG TOO OLD FOR THIS CONFIG::$CFG requires watchdog feature(s) '$MISSING' that this copy of watchdog_run.sh does not implement (it provides '$WATCHDOG_FEATURES'). REFUSING to act. Acting anyway would measure the wrong artifact — e.g. without restraint_keyed_result_v1 a restrain=1 entry resolves the UNRESTRAINED result key, which for the r0 binary arm already exists, and reports a green DONE for a leg that never ran while its VM keeps holding the single GPU. Fix: run the watchdog from a ref whose watchdog_run.sh matches this watch list."
  exit 1
fi

# ============================================================================================================
# ★★ ORPHAN SWEEP — the bounded reap for a VM that NO enabled entry covers.
#
# THE GAP. The DONE branch below reaps a finished leg's VM, and it is the ONLY thing that does — a GCP VM
# cannot delete itself (the in-VM trap runs and GCE refuses the call, gcp-gpu-facts.md §6) and
# gcp-reap-vms.yml has no `schedule:`. But the DONE branch lives inside the loop over ENABLED entries. Disable
# the entry — which `gcp_watch_reap` now does automatically the moment a unit reaches its terminal state — and
# the reap disappears with it. The pass that most needs to look at a VM is the one with nothing left to watch.
#
# WHY IT COULD NOT SIMPLY BE REAPED BEFORE, and why nothing here weakens that. The refusal was correct: a VM
# name is `gcp-ternary-<GITHUB_RUN_ID>`, which says NOTHING about which calculation is inside it, so an orphan
# could only be killed on AGE — and age inverts, because a healthy ternary leg legitimately runs ~44 h
# (gcp-reap-vms.yml records a dry_run that would have destroyed a mid-production leg at age 860 min).
# "A reaper that destroys a live leg is far worse than one that is late" is the governing rule and it stands.
#
# WHAT CHANGED IS THE EVIDENCE, NOT THE RULE. gpu-ternary-fep-gcp.yml now stamps GCE LABELS on every VM it
# creates (`tfep-leg`, `tfep-dir`, `tfep-seed`, `tfep-rst`, `tfep-mode`), so an orphan can be asked what it is
# and answer. That lets this sweep apply the DONE branch's OWN test, unchanged, to a VM the watch list has
# forgotten: delete only when THAT VM's own direction- and restraint-keyed result object is ALREADY IN GCS,
# and only when the VM predates it. Both halves matter — the first says there is no sampling left to lose, the
# second says this VM is the one that produced it rather than a newer run.
#
# EVERYTHING ELSE STILL GETS THE LOUD REFUSAL: an unlabelled VM (created before labels existed, or by hand), a
# non-`run` mode (no leg result exists for it to be judged on — its bound is the shortened --max-run-duration
# the launcher now gives it), a missing result, an unreadable timestamp, a result that PREDATES the VM. None
# of those is reaped here, ever. Age is never consulted.
# ============================================================================================================
orphan_sweep() {
  local _vms _vm _zone _json _leg _dir _seed _rst _mode _created _ce _okey _ort _oe _e _claimed _tuple
  _vms=$(gcloud compute instances list --filter="name~'^gcp-ternary-'" --format="value(name)" 2>/dev/null)
  if [ -z "${_vms:-}" ]; then
    echo "orphan sweep: no gcp-ternary VM is up"
    return 0
  fi
  # tuples an ENABLED entry already covers — those VMs are the per-entry loop's business, not this sweep's.
  _claimed=$(python3 -c "import json;d=json.load(open('$CFG'));[print('%s|%s|%s|%s'%(w['leg_id'],w['direction'],w['seed'],w.get('restrain','0'))) for w in d['watch'] if w.get('enabled')]" 2>/dev/null)
  for _vm in $_vms; do
    _zone=$(gcloud compute instances list --filter="name=$_vm" --format="value(zone.basename())" 2>/dev/null | head -1)
    [ -z "${_zone:-}" ] && continue
    # ONE describe, parsed in python: gcloud projection keys containing '-' are awkward to address, and a
    # mis-addressed key would silently return empty, which here reads as "unlabelled" and would turn a
    # reapable zombie into a permanent loud refusal.
    _json=$(gcloud compute instances describe "$_vm" --zone="$_zone" --format="json(labels,creationTimestamp)" 2>/dev/null)
    [ -z "${_json:-}" ] && _json='{}'
    read -r _leg _dir _seed _rst _mode _created <<<"$(printf '%s' "$_json" | python3 -c "
import sys,json
try: d=json.load(sys.stdin) or {}
except Exception: d={}
l=d.get('labels') or {}
print(l.get('tfep-leg','-'), l.get('tfep-dir','-'), l.get('tfep-seed','-'), l.get('tfep-rst','-'), l.get('tfep-mode','-'), d.get('creationTimestamp','-'))" 2>/dev/null)"
    _leg=${_leg:--}; _dir=${_dir:--}; _seed=${_seed:--}; _rst=${_rst:--}; _mode=${_mode:--}; _created=${_created:--}

    _tuple="$_leg|$_dir|$_seed|$_rst"
    if printf '%s\n' "${_claimed:-}" | grep -Fxq "$_tuple" 2>/dev/null; then
      echo "orphan sweep: $_vm is $_tuple, which an enabled entry already watches — leaving it to that entry"
      continue
    fi

    if [ "$_leg" = "-" ] || [ "$_dir" = "-" ] || [ "$_seed" = "-" ]; then
      echo "::error title=WATCHDOG ORPHAN VM, NOTHING WATCHING IT::$_vm ($_zone) is up, no enabled watch entry covers it, and it carries NO tfep-* labels, so this pass cannot learn which calculation is inside it. It is NOT being reaped — age is not evidence, and a healthy ternary leg legitimately runs ~44 h. A GCP VM cannot delete itself and GPUS_ALL_REGIONS=1 means this box holds the project's only GPU. Confirm it is not a live manual run (gpu-ternary-fep-gcp.yml mode=tail), then dispatch gcp-reap-vms.yml mode=reap exclude=<anything live>."
      echo "ORPHAN VM (unlabelled) $_vm ($_zone)" >> "$ALERT"
      continue
    fi
    if [ "$_mode" != "run" ]; then
      echo "::error title=WATCHDOG ORPHAN VM (non-run mode)::$_vm ($_zone) is a mode=$_mode VM with no enabled watch entry. A non-run mode writes no leg result object, so there is no artifact that can prove it has nothing left to do and it is NOT being reaped here. Its bound is the shortened --max-run-duration the launcher gives non-run modes. Reap by hand if it is idle: gcp-reap-vms.yml mode=reap."
      echo "ORPHAN VM (mode=$_mode) $_vm ($_zone)" >> "$ALERT"
      continue
    fi

    # the VM's OWN result key, restraint included — the same expression the DONE branch uses, sourced from
    # the VM's self-declaration instead of from a watch entry that no longer exists.
    _okey="$RESULTS/leg_${_leg}_${_dir}_r${_seed}"; [ "$_rst" = "1" ] && _okey="${_okey}_rst"; _okey="${_okey}.json"
    _ort=$(gcloud storage ls -l "$_okey" 2>/dev/null | awk 'NF>=3 && $3 ~ /^gs:/ {print $2}' | head -1)
    if [ -z "${_ort:-}" ]; then
      echo "::error title=WATCHDOG ORPHAN VM, RESULT NOT IN GCS::$_vm ($_zone) says it is running $_leg dir=$_dir seed=$_seed restrain=$_rst, and that leg's result object ($_okey) is NOT in GCS — so it may still be sampling and is NOT being reaped. But nothing is watching it either: with no enabled entry there is no census, no stall detection and no relaunch. Either re-enable its entry in research/modalities/ternary-watch.json ON main, or confirm it is dead and reap it (gcp-reap-vms.yml mode=reap)."
      echo "ORPHAN VM (no result yet) $_vm ($_zone) $_leg/$_dir/r$_seed" >> "$ALERT"
      continue
    fi
    _oe=0; _ce=0
    _e=$(date -u -d "$_ort" +%s 2>/dev/null | tr -dc '0-9'); [ -n "${_e:-}" ] && _oe=$((10#$_e))
    _e=$(date -u -d "$_created" +%s 2>/dev/null | tr -dc '0-9'); [ -n "${_e:-}" ] && _ce=$((10#$_e))
    if [ "$_oe" = 0 ] || [ "$_ce" = 0 ]; then
      echo "::warning title=WATCHDOG ORPHAN — REAP SKIPPED::$_vm ($_zone): its leg result exists but a timestamp could not be read (result='${_ort:-?}', created='${_created:-?}'), so this pass cannot prove the VM predates it. Sparing it; re-checked next pass. Sparing a zombie costs one pass, reaping a live leg costs hours of MD."
      continue
    fi
    if [ "$_ce" -ge "$_oe" ]; then
      echo "::notice title=WATCHDOG ORPHAN SPARED (newer than its result)::$_vm ($_zone) was created at $_created, which is NOT before $_leg/$_dir/r$_seed's result was written ($_ort). It is a different, later run against an existing result — possibly a force_rerun — so it is left alone."
      continue
    fi
    if [ "$DRY" = "1" ]; then
      echo "::warning title=WATCHDOG ORPHAN + FINISHED LEG::dry_run=1: would DELETE $_vm ($_zone). It is labelled $_leg/$_dir/r$_seed restrain=$_rst, its result object is already in GCS ($_ort) and the VM predates it ($_created), so there is no sampling left to lose."
    elif gcloud compute instances delete "$_vm" --zone="$_zone" --quiet 2>/tmp/wd-osweep-err; then
      echo "::warning title=WATCHDOG REAPED AN ORPHANED FINISHED LEG::deleted $_vm ($_zone). It carried labels $_leg/$_dir/r$_seed restrain=$_rst, no enabled watch entry covered it, and its own result object was already in GCS ($_ort) with the VM created earlier ($_created) — an idle box holding GPUS_ALL_REGIONS=1. Its presence also means the in-VM self-delete did NOT fire successfully (gcp-gpu-facts.md §6)."
    else
      echo "::error title=WATCHDOG ORPHAN REAP FAILED::$_vm ($_zone) is a finished, unwatched leg and delete failed: $(tail -2 /tmp/wd-osweep-err | tr '\n' ' '). It holds the ONLY GPU; remove it by hand (gcp-reap-vms.yml mode=reap)."
      echo "ORPHAN REAP FAILED $_vm ($_zone)" >> "$ALERT"
    fi
  done
}

# ★ THE COLD PASS. An empty (or fully auto-reaped) watch list is EXACTLY when an orphan VM is invisible, so
# this exit looks first. It used to be safe only by accident — entries were never disabled, so the VM listing
# further down always ran — and auto-reaping landed units removed that accident.
if [ "$N" = "0" ]; then
  orphan_sweep
  if [ -s "$ALERT" ]; then
    echo "=== watchdog raised $(wc -l < "$ALERT" | tr -d ' ') alert(s) on an idle list ==="
    cat "$ALERT"
    echo "watchdog pass complete (idle list, orphan VM present)"
    exit 1
  fi
  echo "::notice title=WATCHDOG idle::No enabled entries in ternary-watch.json and nothing unaccounted-for is holding the GPU quota."
  exit 0
fi

python3 -c "import json;d=json.load(open('$CFG'));[print('%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s'%(w['leg_id'],w['seed'],w['direction'],w.get('commit_salt',''),w.get('timestep_fs','2.0'),w.get('warmup_timestep_fs',''),w.get('use_preequil','0'),w.get('charge_method','nagl'),w.get('n_windows','12'),w.get('template_pdb','8G1Q'),w.get('provisioning','spot'),w.get('max_relaunches_per_day',8),w.get('restrain','0'))) for w in d['watch'] if w.get('enabled')]" \
| while IFS='|' read -r LEG SEED DIR SALT DT WUDT UPE CHG NWIN TPL PROV MAXRL RST; do
    # Every downstream use is `${RST:-0}` / `${RSTTAG:-}`, NOT a bare `$RST`. Two of this file's branches
    # are EXTRACTED and executed in isolation by tests (tests/test_watchdog_done_reaps_vm.sh runs the DONE
    # branch under `set -u` against stubbed gcloud/gh), so the loop header that assigns these is not in
    # scope there and a bare reference is an unbound-variable abort. It aborts inside a command
    # substitution, which swallows it into an empty string -- so the symptom is a test reporting
    # "got ''" rather than an error, and the shell dying outright on the first call made outside one.
    # The defaults are also the correct values, so this is not merely defensive syntax.
    RSTTAG=""; [ "$RST" = "1" ] && RSTTAG="_rst"
    TAG="$LEG dir=$DIR seed=$SEED${RSTTAG:+ restrained}"
    echo "=============== $TAG ==============="

    # ===== THE DONE VERDICT MUST PROVE IT RESOLVED THE RIGHT ARTIFACT =====
    # The handshake above catches a STALE watchdog. This catches the other half: a FUTURE EDIT to this file
    # that drops the restraint component while leaving everything looking correct. It asserts the property
    # rather than the spelling -- a restrained entry's result key must actually carry `_rst` -- so it fires
    # inside the very code that has the bug, before any DONE verdict, reap or converge/reduce chain.
    # A mismatch is refused LOUDLY and the entry is SKIPPED: not-verified must never render as done.
    RESULT_KEY="$RESULTS/leg_${LEG}_${DIR}_r${SEED}${RSTTAG:-}.json"
    if [ "${RST:-0}" = "1" ]; then
      case "$RESULT_KEY" in
        *_rst.json) : ;;
        *) echo "::error title=WATCHDOG RESULT KEY LOST THE RESTRAINT::$TAG declares restrain=1 but this pass resolved '$RESULT_KEY', which carries no _rst component. That key points at the UNRESTRAINED result — already in the bucket for the r0 binary arm — so trusting it would report a green DONE for a leg that never ran and leave its VM holding the single GPU. SKIPPING this entry rather than measuring the wrong artifact."
           continue ;;
      esac
    fi

    # 1. DONE? the leg's own direction- AND restraint-keyed result object is the only authority on completion.
    if gcloud storage ls "$RESULT_KEY" >/dev/null 2>&1; then
      # ===== FIRST: A DONE LEG MUST NOT LEAVE A VM HOLDING THE ONLY GPU =====
      #
      # MEASURED 2026-07-27, gcp-ternary-30215419909 (us-central1-a). The leg finished cleanly --
      # "[barrier] committed checkpoint at iteration 2000/2000", then
      # "[tfep] LEG DONE calib_hi_to_lo__ternary_vhl: ΔG_morph=-47.79 ± 0.09 (MBAR SE)" -- the startup
      # script reached its end and its EXIT trap DID run, and the trap's delete FAILED:
      #
      #   === SELF-DELETE (trap on EXIT): deleting gcp-ternary-30215419909 in us-central1-a ===
      #   ERROR: (gcloud.compute.instances.delete) Could not fetch resource:
      #    - Required 'compute.instances.delete' permission for
      #      'projects/project-a7ebde30-e2ed-4b8d-9a9/zones/us-central1-a/instances/gcp-ternary-30215419909'
      #   self-delete no-op (already gone / no perm)
      #   startup-script exit status 0
      #
      # so a finished, idle VM sat RUNNING and held GPUS_ALL_REGIONS=1 -- which blocks EVERY other GCP GPU
      # job on the account -- until a human noticed. THE HOST CANNOT DELETE ITSELF; ONLY THE CONTROL PLANE
      # CAN. That is the same rule this repo already paid to learn on Vast (CLAUDE.md §6), and this branch
      # IS the control plane. It used to `continue` past a live VM without ever looking at one: the reap
      # lived only in the CRASHED branch below, which a DONE leg can never reach.
      #
      # SAFE BY CONSTRUCTION, and this is why it belongs here rather than in gcp-reap-vms.yml. The
      # condition of this branch is that the leg's own direction-keyed result JSON is ALREADY in GCS, so
      # there is no sampling left for a VM to do and nothing at risk in deleting it. gcp-reap-vms.yml can
      # only ask "how old is it", and age cannot tell a healthy 40 h leg from a wedged one -- which is
      # exactly why that workflow is manual-only and must stay that way.
      #
      # ⚠ AND IT MUST NOT REAP SOMEBODY ELSE'S LEG. $VMS is the LANE-WIDE listing (name~'^gcp-ternary-'),
      # and a VM name carries a dispatch run id, not a leg id — so "this entry is DONE" says nothing about
      # which leg the live VM is running. Caught by a dry_run on 2026-07-27 at 2:22 PM ET, which reported it
      # WOULD delete gcp-ternary-30293029231 — a leg another session had launched six minutes earlier. That
      # is bug class B#2 of ternary-lane-guard-audit-2026-07-25.md ("a guard that ignores a dimension the data
      # varies along") reintroduced by the fix for a different bug, and on a live GPU it would have destroyed
      # real sampling.
      #
      # THE DISCRIMINATOR IS TIME, and it is exact rather than heuristic: only a VM created BEFORE this leg's
      # result object was written can be the VM that produced it. A VM created after that instant is by
      # definition a different run and is never touched. Anything unparseable fails SAFE (spare, and say so) —
      # the cost of sparing a zombie is one more watchdog pass, the cost of reaping a live leg is hours of MD.
      RESEP=0
      # ${RSTTAG} here too, and it is load-bearing: this timestamp is what decides whether a live VM PREDATES
      # the result (idle zombie -> reap) or POSTDATES it (a newer leg -> spare). Reading the UNRESTRAINED
      # result's write time while watching a RESTRAINED leg compares the running VM against a different
      # calculation's clock, which is a coin toss dressed up as evidence.
      _rj=$(gcloud storage ls -l "$RESULTS/leg_${LEG}_${DIR}_r${SEED}${RSTTAG:-}.json" 2>/dev/null | awk 'NF>=3 && $3 ~ /^gs:/ {print $2}' | head -1)
      if [ -n "${_rj:-}" ]; then
        _rs=$(date -u -d "$_rj" +%s 2>/dev/null | tr -dc '0-9'); [ -n "$_rs" ] && RESEP=$((10#$_rs))
      fi
      if [ "$NVM" -gt 0 ] && [ "$RESEP" = 0 ]; then
        echo "::warning title=WATCHDOG DONE — REAP SKIPPED::$TAG — a VM is live but the result object's write time could not be read, so this pass cannot prove the VM predates it. Sparing it; re-checked next pass."
      fi
      if [ "$NVM" -gt 0 ] && [ "$RESEP" -gt 0 ]; then
        for _dvm in $(printf '%s\n' "$VMS" | awk '{print $1}' | sed '/^$/d'); do
          _dz=$(gcloud compute instances list --filter="name=$_dvm" --format="value(zone.basename())" 2>/dev/null | head -1)
          [ -z "$_dz" ] && continue
          _dc=$(gcloud compute instances describe "$_dvm" --zone="$_dz" --format="value(creationTimestamp)" 2>/dev/null | head -1)
          _de=0; [ -n "${_dc:-}" ] && { _dx=$(date -u -d "$_dc" +%s 2>/dev/null | tr -dc '0-9'); [ -n "$_dx" ] && _de=$((10#$_dx)); }
          if [ "$_de" = 0 ] || [ "$_de" -ge "$RESEP" ]; then
            echo "::notice title=WATCHDOG SPARED A NEWER VM::$TAG — $_dvm ($_dz) was created at ${_dc:-<unreadable>}, not before this leg's result object (${_rj}). It is a DIFFERENT run, so it is not this leg's orphan and is left alone."
            continue
          fi
          if [ "$DRY" = "1" ]; then
            echo "::warning title=WATCHDOG DONE + LIVE VM::$TAG — dry_run=1: would DELETE $_dvm ($_dz). The leg's result JSON is in GCS, so the VM is idle and holding the single GPU."
          # stderr is KEPT. Sending it to /dev/null is how the in-VM trap's failure stayed unreadable for
          # ~2 h: one message, "no perm / already gone", covering two opposite outcomes and naming neither.
          elif gcloud compute instances delete "$_dvm" --zone="$_dz" --quiet 2>/tmp/wd-reap-err; then
            echo "::warning title=WATCHDOG REAPED A FINISHED LEG'S VM::$TAG — deleted $_dvm ($_dz). The result JSON was already in GCS, so this VM was idle and holding GPUS_ALL_REGIONS=1. Its presence also means the in-VM self-delete did NOT fire successfully — see gcp-gpu-facts.md §6."
          else
            echo "::error title=WATCHDOG REAP FAILED::$TAG — $_dvm ($_dz) is up with the leg already finished, and delete failed: $(tail -2 /tmp/wd-reap-err | tr '\n' ' '). It is holding the ONLY GPU and every other GCP job is blocked until it is removed by hand (gcp-reap-vms.yml mode=reap)."
            echo "DONE-REAP FAILED for $_dvm ($TAG)" >> "$ALERT"
          fi
        done
      fi
      # A finished leg is not a finished RESULT. The leg JSON holds one ΔG; the deliverable is
      # ΔΔG_coop, the gate verdict, and |ΔG_fwd + ΔG_rev| — all produced by mode=converge (diagnostics)
      # and mode=reduce (the cycle + gate). Both are CPU-only, $0, no GPU. Without this the number sits
      # uncomputed until a human happens to look, which defeats a session-independent watchdog just as
      # much as an unnoticed preemption does.
      #
      # Sequenced across passes rather than in one: workflow_dispatch is fire-and-forget, so there is no
      # way to wait for converge here. Pass N dispatches converge, pass N+1 (15 min later) dispatches
      # reduce — by which time the convergence report exists, so the reducer's diagnostics are MEASURED
      # rather than defaulted. GCS markers make each dispatch happen exactly once; without them this
      # would re-dispatch every 15 minutes forever.
      CVM="$WDIR/done-converge-${LEG}-${DIR}-r${SEED}.txt"
      RDM="$WDIR/done-reduce-${LEG}-${DIR}-r${SEED}.txt"
      : > /tmp/marker.txt
      if ! gcloud storage ls "$CVM" >/dev/null 2>&1; then
        if [ "$DRY" = "1" ]; then
          echo "::notice title=WATCHDOG DONE::$TAG — result JSON present. dry_run=1: would dispatch mode=converge now (diagnostics), then mode=reduce next pass."
        elif gh workflow run gpu-ternary-fep-gcp.yml --ref "${WATCH_REF}" \
               -f mode=converge -f leg_id="$LEG" -f seed="$SEED" -f direction="$DIR" \
               -f commit_salt="$SALT" -f timestep_fs="$DT" -f warmup_timestep_fs="$WUDT" \
               -f use_preequil="$UPE" -f restrain="${RST:-0}" 2>&1; then
          gcloud storage cp /tmp/marker.txt "$CVM" >/dev/null 2>&1 || echo "::warning::converge marker write failed — it may re-dispatch next pass"
          echo "::notice title=WATCHDOG DONE -> CONVERGE::$TAG — result JSON present; dispatched mode=converge (CPU, \$0) for the convergence diagnostics. mode=reduce follows on the next pass, once the report exists."
        else
          echo "::error title=WATCHDOG CONVERGE DISPATCH FAILED::$TAG — the leg finished but mode=converge could not be dispatched; the result will not be reduced automatically."
          echo "CONVERGE DISPATCH FAILED $TAG" >> "$ALERT"
        fi
      elif ! gcloud storage ls "$RDM" >/dev/null 2>&1; then
        if [ "$DRY" = "1" ]; then
          echo "::notice title=WATCHDOG DONE::$TAG — converge already dispatched. dry_run=1: would dispatch mode=reduce now."
        elif gh workflow run gpu-ternary-fep-gcp.yml --ref "${WATCH_REF}" -f mode=reduce 2>&1; then
          gcloud storage cp /tmp/marker.txt "$RDM" >/dev/null 2>&1 || echo "::warning::reduce marker write failed — it may re-dispatch next pass"
          echo "::notice title=WATCHDOG DONE -> REDUCE::$TAG — dispatched mode=reduce (CPU, \$0). Its [REDUCE-VERDICT] annotation carries the gate decision and the fwd/rev hysteresis. Set enabled=false in ternary-watch.json once you have read it."
        else
          echo "::error title=WATCHDOG REDUCE DISPATCH FAILED::$TAG — converge ran but mode=reduce could not be dispatched."
          echo "REDUCE DISPATCH FAILED $TAG" >> "$ALERT"
        fi
      else
        # TERMINAL. Result JSON present AND both follow-ups dispatched — there is genuinely nothing left for
        # this unit. This branch used to print "set enabled=false in ternary-watch.json" and loop, so the entry
        # stayed enabled until a human read a cron log; on 2026-07-28 one had sat here ~14 h. Name it for the
        # reap instead of instructing someone. It is named ONLY here, never in the two branches above, because
        # those still owe a dispatch and disabling the entry there would lose the reduce.
        echo "$LEG|$DIR|$SEED" >> "$REAP"
        echo "::notice title=WATCHDOG DONE::$TAG — result JSON present and both converge+reduce already dispatched. Nothing left to do; queuing it to be disabled in ternary-watch.json (its verdict stays on the mode=reduce run's [REDUCE-VERDICT] annotation)."
      fi
      continue
    fi

    # 2. RUNNING? any live gcp-ternary VM means the single GPU is in use; with a 1-GPU quota it is this leg.
    #
    #    A LIVENESS ping is not enough. On 2026-07-25 three separate silent stalls all presented as a
    #    perfectly healthy RUNNING VM: an am1bcc cold-cache wait (~40 min at 0% GPU), a 25000-step
    #    minimize (~15 min at ~0% GPU), and a warmup NaN. So ask whether the leg is ADVANCING, using
    #    the only durable progress signal outside the VM: the furthest COMMITTED iteration in the spot
    #    commit store. State is kept in GCS, so the comparison survives restarts like everything else.
    if [ "$NVM" -gt 0 ]; then
      # CRASHED-BUT-VM-ALIVE. The in-VM self-delete trap cannot fire (the VM's compute service
      # account lacks compute.instances.delete), so a leg that dies mid-run leaves a RUNNING billing
      # zombie holding the single GPU. Liveness therefore cannot distinguish "running" from "crashed
      # 40 minutes ago" — on 2026-07-25 the rev leg died on a warmup NaN at 12:55 PM ET and the VM
      # was still RUNNING at 1:30. Without this check the leg only surfaces at the 75-min setup grace.
      #
      # The engine uploads its run log on NORESULT as postmortem/<leg>_<dir>_seed<n>_<epoch>.log. That
      # epoch, compared against the VM's OWN creation time, is the discriminator: a postmortem newer
      # than this VM means THIS run crashed, while the previous attempt's postmortem is older and is
      # correctly ignored. (Existence alone would be wrong — there is always an older one.) Scope
      # note: this runs in the RUNNING branch only, where a real VM creation time exists. In the DIED
      # branch a preemption leaves no postmortem (abrupt DELETE) and relaunching is right, so the
      # per-day cap is the bound there.
      PMEP=$(gcloud storage ls "gs://$BUCKET/valB-6hax/postmortem/${LEG}_${DIR}_seed${SEED}_*.log" 2>/dev/null \
             | sed -nE "s#.*_${DIR}_seed${SEED}_([0-9]+)\\.log\$#\\1#p" | sort -n | tail -1 || true)
      # the sed anchors on _${DIR}_seed${SEED}_ as well, not just the seed: otherwise its correctness
      # would rest ENTIRELY on the glob above, and a fwd post-mortem in the listing would win on
      # recency and be read as this rev leg's crash. Defence in depth, same as the census.
      PMEP=${PMEP:-0}; case "$PMEP" in ""|*[!0-9]*) PMEP=0 ;; esac; PMEP=$((10#$PMEP))
      if [ "$PMEP" -gt 0 ] && [ "$PMEP" -gt "$VMEPOCH" ]; then
        # REAP IT HERE, do not ask a human to. A crashed leg's VM holds the ONLY GPU and burns credit
        # for as long as nobody notices, which defeats the point of a session-independent watchdog.
        # This is safe, and differs in a principled way from the evidence-destroying reap earlier on
        # 2026-07-25: the detector fires *because* the post-mortem is already in GCS, so the full run
        # log is preserved off-VM BY CONSTRUCTION before this line can ever run. Still no relaunch —
        # a crash repeats, and the per-day cap is not the right bound for a deterministic failure.
        REAPED="not attempted"
        if [ "$DRY" = "1" ]; then
          REAPED="dry_run — would delete"
        else
          for _vm in $(printf '%s\n' "$VMS" | awk '{print $1}' | sed '/^$/d'); do
            _z=$(gcloud compute instances list --filter="name=$_vm" --format="value(zone.basename())" 2>/dev/null | head -1)
            if [ -n "$_z" ] && gcloud compute instances delete "$_vm" --zone="$_z" --quiet 2>/dev/null; then
              REAPED="deleted $_vm"
            else
              REAPED="DELETE FAILED for $_vm — reap manually (gcp-reap-vms mode=reap)"
            fi
          done
        fi
        echo "::error title=WATCHDOG CRASHED::$TAG — the VM was RUNNING but the leg is DEAD: it uploaded a post-mortem at epoch $PMEP, after this VM was created ($VMEPOCH). The in-VM self-delete trap cannot fire (no compute.instances.delete on the VM's SA), so it was an idle billing zombie holding the single GPU — $REAPED. The post-mortem is in gs://$BUCKET/valB-6hax/postmortem/ (read it with gpu-ternary-fep-gcp mode=tail). NOT relaunching: a crash repeats, so this needs a fix, not a retry."
        echo "CRASHED $TAG (postmortem epoch $PMEP > vm epoch $VMEPOCH; $REAPED)" >> "$ALERT"
        continue
      fi

      # Furthest committed iteration for THIS direction. The commit prefix is
      #   commits/<leg>/<seed>_dt<dt>fs_clig0_wu<..>[_<salt>][_dir<rev>]
      # so a direction-blind census would read the fwd leg's much-further trajectory and declare a
      # dead-stopped rev leg to be racing ahead — the same direction-blind bug class as the rest.
      CALL=$(gcloud storage ls --recursive "gs://$BUCKET/valB-6hax/commits/$LEG/" 2>/dev/null || true)
      SEL=$(printf '%s\n' "$CALL" | grep -aE "/${SEED}_dt" || true)
      if [ "$DIR" = fwd ]; then
        SEL=$(printf '%s\n' "$SEL" | grep -av '_dir' || true)     # fwd carries NO suffix
      else
        SEL=$(printf '%s\n' "$SEL" | grep -a "_dir$DIR" || true)
      fi
      [ -n "$SALT" ] && SEL=$(printf '%s\n' "$SEL" | grep -a "_$SALT" || true); true
      # `wu<warmup_dt>` keys the prefix as well, so a census blind to it would read the 2.0 fs
      # warmup attempt's commits while watching the 1.0 fs one (or vice versa).
      SEL=$(printf '%s\n' "$SEL" | grep -aE "_wu${WUDT}(_|/)" || true)
      # `|| true` on both: a leg with no commits yet is the NORMAL early reading, not a failure, and
      # with pipefail a no-match grep would otherwise propagate 1 out of the pipeline.
      MAXW=$(printf '%s\n' "$SEL" | grep -aoE "warmup/iter-[0-9]+"     | grep -aoE "[0-9]+$" | sort -n | tail -1 || true)
      MAXP=$(printf '%s\n' "$SEL" | grep -aoE "production/iter-[0-9]+" | grep -aoE "[0-9]+$" | sort -n | tail -1 || true)
      # FORCE BASE 10. The commit store pads to 8 digits (iter-00000520), and bash reads a
      # leading-zero literal as OCTAL: 00000520 would silently become 336, and 00000999 is not octal
      # at all, so $((1000000 + MAXP)) ERRORS — leaving PROG unset, which under `set -u` kills this
      # entry mid-loop. Exactly the silent-skip this workflow exists to remove; caught by
      # tests/test_watchdog_census.sh, not by review.
      # `; true` is defensive only: a failing NON-final command in an && list is exempt from -e
      # (verified empirically), so `[ -n "" ] && ...` is already safe -- but it stops being safe the
      # moment someone reorders the line so the test is last. The construct that actually killed the
      # run was the bare `MAXW=$(pipeline)` assignment above, whose status IS the pipeline's.
      [ -n "$MAXW" ] && MAXW=$((10#$MAXW)); true
      [ -n "$MAXP" ] && MAXP=$((10#$MAXP)); true
      # one monotonic scalar to compare passes on: production dominates warmup, and warmup is
      # offset so a warmup->production transition can never look like a regression.
      if [ -n "$MAXP" ]; then PROG=$((1000000 + MAXP)); PHASE="production/$MAXP"
      elif [ -n "$MAXW" ]; then PROG=$MAXW; PHASE="warmup/$MAXW"
      else PROG=0; PHASE="none (setup/env-solve/minimize)"; fi

      POBJ="$WDIR/progress-${LEG}-${DIR}-r${SEED}.txt"
      PREV=$(gcloud storage cat "$POBJ" 2>/dev/null | tr -dc '0-9 ' | tr -s ' ')
      PPROG=$(printf '%s' "$PREV" | awk '{print $1+0}'); PPROG=${PPROG:-0}
      PSTALL=$(printf '%s' "$PREV" | awk '{print $2+0}'); PSTALL=${PSTALL:-0}
      case "$PPROG" in ""|*[!0-9]*) PPROG=0 ;; esac
      case "$PSTALL" in ""|*[!0-9]*) PSTALL=0 ;; esac

      if [ "$PROG" -gt "$PPROG" ]; then STALL=0; else STALL=$((PSTALL + 1)); fi
      echo "progress: $PHASE  (scalar $PROG, previous $PPROG, no-advance passes $STALL)"
      if [ "$DRY" != "1" ]; then
        printf '%s %s' "$PROG" "$STALL" > /tmp/prog.txt
        gcloud storage cp /tmp/prog.txt "$POBJ" >/dev/null 2>&1 \
          || echo "::warning::progress write failed — stall detection will restart from zero next pass"
      fi

      if [ "$PROG" = "0" ] && [ "$VMAGE" -ge "$SETUP_GRACE_MIN" ]; then
        echo "::error title=WATCHDOG SETUP STALL::$TAG — VM live ${VMAGE} min with ZERO committed iterations (grace ${SETUP_GRACE_MIN} min). Setup is hung, not slow: check am1bcc/charge cache, minimize step count, and GPU utilisation. NOT relaunching (a relaunch would hang the same way)."
        echo "SETUP STALL $TAG" >> "$ALERT"
      elif [ "$STALL" -ge "$STALL_PASSES" ] && [ "$PROG" -gt 0 ]; then
        echo "::error title=WATCHDOG STALLED::$TAG — VM live but the committed iteration has been frozen at $PHASE for $STALL consecutive passes (~$((STALL * 15)) min, vs a ~23-min healthy commit interval). MD is not advancing. NOT relaunching — diagnose (GPU util, NaN, run log) before spending more."
        echo "STALLED $TAG at $PHASE" >> "$ALERT"
      else
        echo "::notice title=WATCHDOG RUNNING::$TAG — advancing at $PHASE, VM live ${VMAGE} min ($(printf '%s' "$VMS" | tr '\n' ' ')). Leaving it alone."
      fi
      continue
    fi

    # 3. DIED. Cap re-dispatch per UTC day using a counter object in GCS (durable across restarts,
    #    unlike anything held in a process). Read-modify-write is racy in principle; the concurrency
    #    group above means only one watchdog runs at a time, so in practice it is not.
    DAY=$(date -u +%Y%m%d)
    CNTOBJ="$WDIR/relaunch-${DAY}-${LEG}-${DIR}-r${SEED}.txt"
    CNT=$(gcloud storage cat "$CNTOBJ" 2>/dev/null | tr -dc '0-9')
    CNT=${CNT:-0}; case "$CNT" in ""|*[!0-9]*) CNT=0 ;; esac
    CNT=$((10#$CNT))   # base 10, never octal — see the MAXW/MAXP note above; free insurance
    case "$MAXRL" in ""|*[!0-9]*) MAXRL=8 ;; esac
    if [ "$CNT" -ge "$MAXRL" ]; then
      echo "::error title=WATCHDOG CAPPED::$TAG — died again but already relaunched $CNT times today (cap $MAXRL). NOT relaunching; something is failing repeatedly and needs a human."
      echo "RELAUNCH CAP $TAG ($CNT/$MAXRL today)" >> "$ALERT"
      continue
    fi

    if [ "$DRY" = "1" ]; then
      echo "::notice title=WATCHDOG would-relaunch::$TAG — died (no result, no VM), relaunch $((CNT+1))/$MAXRL. dry_run=1 so taking no action."
      continue
    fi

    # PRECONDITION: the primed setup cache must EXIST before buying a VM. The GPU lane already refuses
    # to solvate+parameterize on an idle GPU (RBFE_REQUIRE_PRIMED_SETUP), but it does so ON the VM --
    # so a relaunch into a missing cache still provisions, bails after ~2.6 min, and leaves a zombie
    # holding the single GPU because the self-delete trap has no permission. That happened at 3:18 PM
    # on 2026-07-25: this watchdog relaunched the rev leg 4 minutes before its v2pe prime finished.
    # The check is one `ls`, and it moves the guard to BEFORE the spend. The cache key mirrors the
    # engine's: <leg>_<dir>_r<seed>__<charge>__<setup_version>, where use_preequil=1 forces v2pe.
    SETUPVER=v1; [ "$UPE" = "1" ] && SETUPVER=v2pe
    SCACHE="gs://$BUCKET/valB-6hax/setupcache/${LEG}_${DIR}_r${SEED}__${CHG}__${SETUPVER}"
    if ! gcloud storage ls "$SCACHE/" >/dev/null 2>&1; then
      echo "::error title=WATCHDOG SETUP CACHE MISSING::$TAG — NOT relaunching: the primed setup cache $SCACHE does not exist, so a GPU run would provision, refuse to build on the idle GPU, and leave a billing zombie. Pre-bake it first: dispatch ternary-setup-prime-cpu.yml with leg_id=$LEG direction=$DIR seed=$SEED charge_method=$CHG use_preequil=$UPE (free CPU). Not counting this against the relaunch cap."
      echo "SETUP CACHE MISSING $TAG ($SCACHE)" >> "$ALERT"
      continue
    fi

    echo "relaunching $TAG (attempt $((CNT+1))/$MAXRL today) — resumes from the last committed checkpoint"
    if gh workflow run gpu-ternary-fep-gcp.yml --ref "${WATCH_REF}" \
         -f mode=run -f leg_id="$LEG" -f seed="$SEED" -f direction="$DIR" \
         -f commit_salt="$SALT" -f timestep_fs="$DT" -f warmup_timestep_fs="$WUDT" \
         -f use_preequil="$UPE" -f charge_method="$CHG" \
         -f n_windows="$NWIN" -f template_pdb="$TPL" -f restrain="${RST:-0}" \
         -f refuse_if_vm_live=1 -f provisioning="$PROV" 2>&1; then
      printf '%s' "$((CNT+1))" > /tmp/cnt.txt
      gcloud storage cp /tmp/cnt.txt "$CNTOBJ" >/dev/null 2>&1 \
        || echo "::warning::counter write failed — the relaunch cap may under-count"
      echo "::notice title=WATCHDOG RELAUNCHED::$TAG — was dead (no result, no VM); re-dispatched, attempt $((CNT+1))/$MAXRL today. Resumes from checkpoint."
    else
      echo "::error title=WATCHDOG DISPATCH FAILED::$TAG — died AND the re-dispatch call failed. Needs a human."
      echo "DISPATCH FAILED $TAG" >> "$ALERT"
    fi
  done
# ★ AND SWEEP AGAIN ON A NON-IDLE PASS. The per-entry loop only ever looks at a VM through the lens of an
# ENABLED entry; a VM belonging to a unit that was disabled while it was still up is invisible to it. Running
# the sweep here as well means the reap does not depend on the watch list being in any particular state —
# which is the whole failure this pass exists to remove. It skips anything an enabled entry already covers,
# so it can never race the loop above for the same box.
orphan_sweep
# ============================================================================================================
# REAP THE LANDED UNITS. See gcp_watch_reap.py for why the proof is the terminal state and not merely
# "the result exists" — reaping on the result alone would disable an entry before the pass that dispatches
# its reducer, and the verdict would never be computed.
#
# WHY IT PUSHES TO main. The watch list is a REPO file and this workflow always runs main's copy (it takes no
# `ref`), so the only way a disable survives to the next pass is a commit on main. It touches exactly one
# path, writes only when something changed, and never re-enables anything.
#
# WHY A FAILED PUSH IS A WARNING, NOT AN ALERT. The cost of not reaping is a stale entry — the very state
# that existed before this code, and one the next pass retries for free. Failing the job for it would page a
# human about bookkeeping and, worse, would fire the workflow-failure notification that is reserved for a leg
# actually being in trouble. A race with another push is the expected case here, not an incident.
# ============================================================================================================
if [ -s "$REAP" ]; then
  REAPED=$(tr '\n' ' ' < "$REAP")
  echo "=== reaping landed unit(s): $REAPED ==="
  if [ "$DRY" = "1" ]; then
    python3 research/modalities/gcp_watch_reap.py --dry-run $REAPED
  elif python3 research/modalities/gcp_watch_reap.py \
         --verdict-url "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/workflows/gpu-ternary-fep-gcp.yml" \
         $REAPED && ! git diff --quiet -- "$CFG"; then
    git config user.name  "github-actions[bot]"
    git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
    git add "$CFG"
    git commit -q -m "watchdog: disable landed watch entr(ies) $REAPED" \
      -m "Result JSON in GCS and both follow-ups dispatched — the terminal state. Auto-reaped so the lane stops reading as having unfinished work."
    PUSHED=0
    for try in 1 2 3; do
      git pull --rebase --quiet origin main >/dev/null 2>&1
      if git push --quiet origin HEAD:main >/dev/null 2>&1; then PUSHED=1; break; fi
      sleep $((try * 4))
    done
    if [ "$PUSHED" = "1" ]; then
      echo "reaped and pushed: $REAPED"
    else
      echo "::warning title=WATCHDOG REAP NOT PERSISTED::disabled $REAPED locally but could not push to main after 3 tries. The entry stays enabled for now; the next pass retries. This costs a stale entry, not a leg."
    fi
  else
    echo "nothing to commit — the named unit(s) were already disabled."
  fi
fi
echo "watchdog pass complete"
if [ -s "$ALERT" ]; then
  echo "=== watchdog raised $(wc -l < "$ALERT" | tr -d ' ') alert(s) ==="
  cat "$ALERT"
  echo "failing the job so GitHub's workflow-failure notification fires (see the annotations above)."
  exit 1
fi
