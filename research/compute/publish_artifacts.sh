#!/usr/bin/env bash
# ONE HOME FOR "COMMIT THESE ARTIFACTS AND PUSH THEM" — because the repo learned this rule four times.
#
# Usage:  publish_artifacts.sh <branch> <commit-message> <path> [<path>...]
# Env:
#   PUBLISH_REGEN      command run AFTER the reset and BEFORE the commit, for DERIVED files (see below)
#   PUBLISH_REGEN_ADD  space-separated paths the regen command produces, staged if they exist
#   PUBLISH_FAIL_HARD  1 = exit non-zero when every attempt failed. Default 0 = ::error:: annotation only.
#   PUBLISH_TRIES      attempts (default 5)
#
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⛔ WHY `git pull --rebase` IS THE WRONG OPERATION, AND WHY A COMMENT SAYING SO WAS NOT ENOUGH
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# One conflict leaves the repo MID-REBASE. Every subsequent retry then dies on the wreckage of the first
# rather than on anything new — `error: Pulling is not possible because you have unmerged files.` — so a
# retry loop repeats instead of recovering, and in the common shape it ends on a `::warning::` while the
# step reports SUCCESS. The job ran, measured, decided, and published nothing.
#
# MEASURED, three separate lanes, each fixed in place with a long comment and each leaving the others broken:
#   GCP     run 30701290485  CONFLICT in gcp-s1f-rep-rate.json; `git push HEAD:main` pushed upstream back to
#                            itself -> exit 0, printed "fragment published", main's fragment stayed 67 s old
#   selcal  run 30710853581  CONFLICT in selcal-cofold-census.json; that tick's REAP READOUT was lost
#   step-1  run 30714482049  CONFLICT in inflight-board-all.md; the market-hold artifact sat 14 min stale
#                            while the step was GREEN — and the supervision alarm fired on that staleness and
#                            was CORRECT, which is how a green tick and a screaming alarm coexisted in one run
#
# A MERGE WAS NEVER RIGHT FOR A SINGLE-WRITER ARTIFACT: there is nothing of anyone else's in it to preserve,
# so "ours, always" is the correct semantics rather than a shortcut. Rewriting onto upstream makes a conflict
# UNREPRESENTABLE instead of handled — and because HEAD then sits exactly one commit ahead of the ref it
# pushes to, a successful push cannot be a silent no-op either.
#
# ⚠ DERIVED FILES GO THROUGH `PUBLISH_REGEN`, NEVER THROUGH THE PATH LIST. A file with MANY writers (the
# all-lane board, gcp-gpu-facts.md) must not be stamped from a pre-reset snapshot: the copy this job holds
# was built against its own checkout's stale view of everybody else's inputs, so stamping it reverts their
# work. Regenerating it after the reset reads upstream's freshest inputs plus ours. A file we regenerate
# cannot carry another writer's work backwards; a file we stamp from a stale checkout can.
#
# ⚠ AND THE COMMIT IS UNCONDITIONAL (`--allow-empty`). The timestamp IS the heartbeat: it is the only input
# to every `_As of … STALE` readout and to the supervision alarms. A `git diff --cached --quiet && exit 0`
# guard never fires in practice (the stamp changes every tick), which is exactly what makes it a LANDMINE
# rather than a bug — it does nothing until someone stabilises the timestamp as an "optimisation", and from
# that moment a healthy idle job becomes byte-identical to a dead one.
set -uo pipefail

BRANCH="${1:?usage: publish_artifacts.sh <branch> <message> <path>...}"; shift
MSG="${1:?usage: publish_artifacts.sh <branch> <message> <path>...}"; shift
TRIES="${PUBLISH_TRIES:-5}"

git config user.name  "${PUBLISH_AUTHOR_NAME:-Claude}"
git config user.email "${PUBLISH_AUTHOR_EMAIL:-noreply@anthropic.com}"

# Only paths that exist. `git add A B` fails atomically if either pathspec matches nothing, so one absent
# file would stage NEITHER and the step would report "nothing to commit" while swallowing the rest.
PATHS=()
for p in "$@"; do [ -e "$p" ] && PATHS+=("$p"); done
if [ ${#PATHS[@]} -eq 0 ] && [ -z "${PUBLISH_REGEN:-}" ]; then
  echo "[publish] nothing to stage — none of the requested paths exist"
  exit 0
fi

SNAP="$(mktemp -d)"
for p in "${PATHS[@]:-}"; do [ -n "$p" ] && cp --parents "$p" "$SNAP/"; done

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⛔ A JOB MAY ONLY PUBLISH WHAT IT ACTUALLY WROTE. MEASURED 2026-08-01, five seconds wide.
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# `selcal-collect.json` was published by the `collect` mode at 22:16:43Z carrying `landed: 5`. The `status`
# mode — which does not compute collect at all — pushed at 22:16:50Z and put it BACK to `landed: 0` with a
# `utc` of 19:51:35Z: a three-hour-old artifact re-published as current, by a job that had merely checked the
# file out and listed it in its path list. Downstream, "0 of 24 landed" was then the lane's official state
# while five legs sat banked in S3.
#
# The rewrite-onto-upstream loop below CANNOT catch this: there is no conflict to resolve. Our copy is a
# clean, older version of a file upstream moved past, so it applies perfectly and silently reverts.
# `PUBLISH_REGEN` is the answer only for files this job can REGENERATE; it is not the answer for a file this
# job has no business touching in the first place.
#
# The discriminator is exact and needs no bookkeeping from the caller: compare our copy against the commit
# this job CHECKED OUT. Identical => this run did not write it => leave upstream's version alone. Different
# => this run produced it => publish it, which is the whole point. A file that did not exist at checkout is
# new work and always publishes.
#
# ⚠ NOT A HEURISTIC ABOUT STALENESS, and deliberately not one: "ours is older" would be a timestamp race, and
# timestamps are exactly what a heartbeat commit rewrites every tick. This asks a question with one answer —
# *did this job change the file?* — so it cannot mis-fire on a job that legitimately rewrites an artifact to
# a value it happens to already have (skipping there is a no-op: the content is identical either way).
BASE="$(git rev-parse HEAD 2>/dev/null || true)"

_this_run_wrote_it() {                      # $1 = path. 0 = yes/unknowable (publish), 1 = untouched (skip)
  local p="$1" base_blob
  [ "${PUBLISH_STAMP_UNTOUCHED:-0}" = "1" ] && return 0
  [ -n "$BASE" ] || return 0                # no checkout ref to compare against: never silently drop work
  base_blob="$(mktemp)"
  if ! git show "$BASE:$p" >"$base_blob" 2>/dev/null; then
    rm -f "$base_blob"; return 0            # absent at checkout => created by this run
  fi
  if cmp -s "$base_blob" "$SNAP/$p"; then
    rm -f "$base_blob"; return 1            # byte-identical to what we checked out => we did not write it
  fi
  rm -f "$base_blob"; return 0
}

PUBLISHED=0
for attempt in $(seq 1 "$TRIES"); do
  # Clear any wedge left by an earlier step in the same job before doing anything else.
  git rebase --abort  >/dev/null 2>&1 || true
  git merge  --abort  >/dev/null 2>&1 || true
  if ! git fetch -q origin "$BRANCH"; then sleep $((attempt * 3)); continue; fi
  git reset -q --hard FETCH_HEAD

  SKIPPED=()
  for p in "${PATHS[@]:-}"; do
    [ -n "$p" ] || continue
    if ! _this_run_wrote_it "$p"; then
      # Upstream's version stays. Say so — a file silently dropped from a publish is how the reverse bug
      # (an artifact that never lands) would look, and the two must not be told apart by guesswork.
      SKIPPED+=("$p")
      continue
    fi
    mkdir -p "$(dirname "$p")"
    cp "$SNAP/$p" "$p" 2>/dev/null || true
    git add -f -- "$p" 2>/dev/null || true
  done
  [ ${#SKIPPED[@]} -gt 0 ] && echo "[publish] not ours to publish, upstream's kept: ${SKIPPED[*]}"

  if [ -n "${PUBLISH_REGEN:-}" ]; then
    # Failure here must not lose the artifacts above: the regen is a DERIVED convenience, they are the work.
    eval "$PUBLISH_REGEN" >/dev/null 2>&1 \
      || echo "::warning title=PUBLISH REGEN FAILED::\`$PUBLISH_REGEN\` did not run; the primary artifacts are still being published."
    for p in ${PUBLISH_REGEN_ADD:-}; do [ -e "$p" ] && git add -f -- "$p" 2>/dev/null || true; done
  fi

  git commit -q --allow-empty -m "$MSG"
  if git push -q origin "HEAD:$BRANCH"; then PUBLISHED=1; break; fi
  echo "[publish] push race on attempt $attempt — rewriting onto the new tip"
  sleep $((attempt * 3))
done

if [ "$PUBLISHED" = 1 ]; then
  echo "[publish] published to $BRANCH at $(git log -1 --format=%cI): ${PATHS[*]:-<regen only>}"
  exit 0
fi

# ⛔ A PUBLISH THAT DID NOT HAPPEN MUST NEVER READ LIKE ONE. `::error::` rather than a `::warning::`, and
# `exit 1` only on request: several callers are `schedule:`-triggered, and a red scheduled run emails the
# repo owner — the push channel `alarm_state.py` and `fleet-supervision-alarm.yml` both exist to remove, and
# which trimcrae asked to stop. The durable detection of a failed publish is the artifact staleness the
# supervision alarms already watch, so annotating loses nothing that matters.
echo "::error title=ARTIFACTS NOT PUBLISHED::$TRIES attempts failed for ${PATHS[*]:-<regen only>} on $BRANCH. The job RAN and produced them; they never left the runner, so every downstream reader will see the PREVIOUS values and any staleness alarm on them will fire — correctly. Do not silence that alarm; fix the push."
[ "${PUBLISH_FAIL_HARD:-0}" = "1" ] && exit 1
exit 0
