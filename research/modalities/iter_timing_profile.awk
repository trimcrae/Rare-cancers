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

/WARMUP from iter/ {ph="warmup"; seen_marker=1}
/PRODUCTION created from warmup|resume PRODUCTION at iter/ {ph="production"; seen_marker=1; seen_prod=1}

# openmmtools logs "Iteration took 60.691s." -- match the number after "took" rather than a fixed field index,
# because the surrounding text has changed between versions and a positional $N would silently read the wrong
# token (or nothing) instead of failing.
/took [0-9.]+ *s/ {
  if (ph=="") ph="pre-warmup";          # NB usually the buffer lag, not a real phase -- see the END warning
  if (match($0, /took [0-9.]+/)) {
    v=substr($0, RSTART+5, RLENGTH-5)+0;
    if (!seen_marker) npre++;           # count the lag so END can call it out
    n[ph]++; s[ph]+=v;
    if (v>mx[ph]) mx[ph]=v;
    if (mn[ph]==0 || v<mn[ph]) mn[ph]=v;
    blk=sprintf("%s/%05d", ph, int((n[ph]-1)/100)*100);
    bn[blk]++; bs[blk]+=v;
    # PHASE-FREE ordinal blocks over the whole log. These are the trustworthy view: the drift in per-iteration
    # cost is visible in them whether or not the phase markers arrived on time.
    tot++;
    seg=sprintf("%05d-%05d", int((tot-1)/100)*100, int((tot-1)/100)*100+99);
    sn[seg]++; ss[seg]+=v;
  }
}

END {
  # awk hash order is unspecified, so the caller pipes this through `sort`; the fixed-width prefixes are what make
  # that sort produce a readable grouping.
  #
  # SEGMENT lines come FIRST in sort order on purpose (S < P/B is not why -- the prefix widths make it read), and
  # they are the ones to trust. They are ordinal blocks over the whole log with NO phase attribution at all, so
  # they show the drift in per-iteration cost regardless of whether the phase labels are right.
  for (k in sn) printf "SEGMENT iters %-14s n=%-4d mean=%6.2fs\n", k, sn[k], ss[k]/sn[k];
  for (k in n) printf "PHASE %-12s n=%-5d mean=%6.2fs min=%6.2f max=%6.2f\n", k, n[k], s[k]/n[k], mn[k], mx[k];
  for (k in bn) printf "BLOCK %-19s n=%-4d mean=%6.2fs\n", k, bn[k], bs[k]/bn[k];
  if (length(n)==0 && length(sn)==0) print "PHASE (none) — no \"took Ns\" timing lines in the log at all";

  # ⚠ THE PHASE LABELS COME FROM A LAGGING STREAM AND CAN BE WRONG. The driver's phase lines are written by
  # `print` (block-buffered to the tee pipe) while openmmtools' per-iteration lines go through `logging` (flushed
  # per record), so on a live log the phase markers land thousands of iterations late. Measured on the rev leg
  # (GH run 30202433547): GCS had production at 320/2000 while the log's newest driver line still said warmup
  # 640/800 and had no production-creation line at all — so 320 production iterations were labelled "warmup", and
  # a large "pre-warmup" block appeared that is nothing but the lag before the first marker was flushed.
  # rbfe_spot_driver now defaults `log` to a flushing print, which fixes logs written from here on; this warning
  # exists because logs ALREADY WRITTEN (including the leg running right now) still carry the artifact.
  # THE AUTHORITATIVE PHASE SOURCE IS THE GCS OBJECT LISTING, which the caller prints beside this.
  w1 = "WARNING buffering-lag: %d timing lines precede the FIRST driver phase marker. That is NOT a real";
  w1 = w1 " pre-phase, it is the block-buffer lag. Treat every PHASE/BLOCK label as unreliable and read the";
  w1 = w1 " SEGMENT lines plus the GCS census instead.\n";
  if (npre > 50) printf(w1, npre);
  w2 = "WARNING no production marker in the log. If the GCS census shows production commits, those iterations";
  w2 = w2 " are MISLABELLED above -- they were folded into the last phase seen.";
  if (length(n) > 0 && !seen_prod) print w2;
}
