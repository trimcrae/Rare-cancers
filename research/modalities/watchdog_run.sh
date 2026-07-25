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
if [ "$N" = "0" ]; then
  echo "::notice title=WATCHDOG idle::No enabled entries in ternary-watch.json — nothing to watch."
  exit 0
fi

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

# An ::error:: annotation that nobody opens is no better than the silent stall this workflow exists
# to remove. So a stall / cap / failed dispatch also FAILS THE JOB, which makes GitHub send its own
# workflow-failure notification out-of-band — the alert path that does not depend on an agent, a
# session, or anyone thinking to look. RUNNING and DONE stay green so the mailbox stays quiet.
# The entry loop is a pipeline subshell, so the flag has to live in a file, not a variable.
ALERT=/tmp/watchdog-alert; rm -f "$ALERT"

python3 -c "import json;d=json.load(open('$CFG'));[print('%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s'%(w['leg_id'],w['seed'],w['direction'],w.get('commit_salt',''),w.get('timestep_fs','2.0'),w.get('warmup_timestep_fs',''),w.get('use_preequil','0'),w.get('charge_method','nagl'),w.get('n_windows','12'),w.get('template_pdb','8G1Q'),w.get('max_relaunches_per_day',8))) for w in d['watch'] if w.get('enabled')]" \
| while IFS='|' read -r LEG SEED DIR SALT DT WUDT UPE CHG NWIN TPL MAXRL; do
    TAG="$LEG dir=$DIR seed=$SEED"
    echo "=============== $TAG ==============="

    # 1. DONE? the leg's own direction-keyed result object is the only authority on completion.
    if gcloud storage ls "$RESULTS/leg_${LEG}_${DIR}_r${SEED}.json" >/dev/null 2>&1; then
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
               -f use_preequil="$UPE" 2>&1; then
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
        echo "::notice title=WATCHDOG DONE::$TAG — result JSON present and both converge+reduce already dispatched. Nothing left to do: set enabled=false in ternary-watch.json."
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
         -f n_windows="$NWIN" -f template_pdb="$TPL" \
         -f refuse_if_vm_live=1 -f provisioning=spot 2>&1; then
      printf '%s' "$((CNT+1))" > /tmp/cnt.txt
      gcloud storage cp /tmp/cnt.txt "$CNTOBJ" >/dev/null 2>&1 \
        || echo "::warning::counter write failed — the relaunch cap may under-count"
      echo "::notice title=WATCHDOG RELAUNCHED::$TAG — was dead (no result, no VM); re-dispatched, attempt $((CNT+1))/$MAXRL today. Resumes from checkpoint."
    else
      echo "::error title=WATCHDOG DISPATCH FAILED::$TAG — died AND the re-dispatch call failed. Needs a human."
      echo "DISPATCH FAILED $TAG" >> "$ALERT"
    fi
  done
echo "watchdog pass complete"
if [ -s "$ALERT" ]; then
  echo "=== watchdog raised $(wc -l < "$ALERT" | tr -d ' ') alert(s) ==="
  cat "$ALERT"
  echo "failing the job so GitHub's workflow-failure notification fires (see the annotations above)."
  exit 1
fi
