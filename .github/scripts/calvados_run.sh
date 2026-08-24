#!/usr/bin/env bash
# One (construct, replicate) at the frozen protocol, then analyse it.
#
# ⚠ THE WALL TIME IS RECORDED BY THIS SCRIPT AND NOT BY THE PYTHON. It is one of the fields the
# scorer checks precisely because a default cannot fabricate it: an env-echoed record once carried a
# fabricated verdict all the way out of this repository.
set -euo pipefail
CONSTRUCT="$1"; REPLICATE="$2"; OUTDIR="${3:-runs}"
RUN_ID="${CONSTRUCT}_r${REPLICATE}"

python research/modalities/emc_condensate_calvados.py --prepare "$CONSTRUCT" "$REPLICATE" \
    --outdir "$OUTDIR"
RUNDIR="$OUTDIR/$RUN_ID"

T0=$(date +%s)
python "$RUNDIR/run.py" --path "$RUNDIR"
T1=$(date +%s)
echo "$((T1 - T0))" > "$RUNDIR/wall_seconds.txt"
echo "wall: $((T1 - T0)) s for $RUN_ID"

python research/modalities/emc_condensate_calvados.py --analyse "$RUNDIR"
