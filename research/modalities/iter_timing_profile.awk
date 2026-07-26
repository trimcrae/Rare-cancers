# Per-phase iteration timing profile for an rbfe_spot_driver run log (/tmp/tfep_run.log on the GPU VM).
#
# WHY THIS IS A FILE AND NOT A HEREDOC IN THE WORKFLOW. It was a heredoc first, and the closing `AWK`
# terminator has to sit at column 0 -- which dedents it out of the enclosing `run: |` block scalar and makes the
# whole workflow INVALID YAML. GitHub's symptom for that is a 422 "Workflow does not have 'workflow_dispatch'
# trigger" plus a `schedule:` cron that silently never fires, and it has already disabled a workflow in this repo
# twice. A heredoc terminator cannot be indented with spaces (`<<-` strips TABS only), so there is no in-YAML
# arrangement that is both valid and readable. In a file it is also unit-testable
# (tests/test_iter_timing_profile.sh) instead of only reachable through a dispatched CI run.
#
# WHAT IT ANSWERS. Two questions, from the one artifact that can settle either -- the run log of the VM that
# produced the trajectory, which carries both phases' timing lines for the same machine, GPU and system:
#
#   PHASE lines: is a production iteration really ~2x a warmup iteration? Both phases run the SAME number of MD
#     steps per iteration (OpenFE fixes `n_steps` from the production timestep; rbfe_spot_driver builds the
#     warmup move as a copy with only `.timestep` changed), so they should cost the same. ternary-watch.json
#     extrapolated a whole leg from a warmup-measured 33.91 s/iter.
#
#   BLOCK lines: is the production cost CONSTANT or RISING with accumulated iterations? This is the one that
#     changes decisions. A constant cost means an ETA computed from the current rate is sound; a rising one means
#     every such ETA is optimistic, and the further the leg gets the worse the estimate.
#
# Phase attribution keys on rbfe_spot_driver's own transition lines, so it follows the driver rather than
# guessing from iteration numbers (which restart at 0 in each phase and after every resume).

/WARMUP from iter/ {ph="warmup"}
/PRODUCTION created from warmup|resume PRODUCTION at iter/ {ph="production"}

# openmmtools logs "Iteration took 60.691s." -- match the number after "took" rather than a fixed field index,
# because the surrounding text has changed between versions and a positional $N would silently read the wrong
# token (or nothing) instead of failing.
/took [0-9.]+ *s/ {
  if (ph=="") ph="pre-warmup";          # timing lines before any transition line (minimize, setup MD)
  if (match($0, /took [0-9.]+/)) {
    v=substr($0, RSTART+5, RLENGTH-5)+0;
    n[ph]++; s[ph]+=v;
    if (v>mx[ph]) mx[ph]=v;
    if (mn[ph]==0 || v<mn[ph]) mn[ph]=v;
    blk=sprintf("%s/%05d", ph, int((n[ph]-1)/100)*100);
    bn[blk]++; bs[blk]+=v;
  }
}

END {
  # awk hash order is unspecified, so the caller pipes this through `sort`; the fixed-width PHASE/BLOCK prefixes
  # are what make that sort produce a readable grouping.
  for (k in n) printf "PHASE %-12s n=%-5d mean=%6.2fs min=%6.2f max=%6.2f\n", k, n[k], s[k]/n[k], mn[k], mx[k];
  for (k in bn) printf "BLOCK %-19s n=%-4d mean=%6.2fs\n", k, bn[k], bs[k]/bn[k];
  if (length(n)==0) print "PHASE (none) — no \"took Ns\" timing lines in the log at all";
}
