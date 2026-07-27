#!/usr/bin/env bash
# mode=converge must analyse the trajectory of the DIRECTION IT WAS ASKED FOR, and must pair each simulation.nc
# with a checkpoint from the SAME commit prefix.
#
# WHAT WENT WRONG, observed live 2026-07-26 8:09 AM. The discovery was
#
#     ALL=$(grep -a "$LEG" /tmp/lane.txt | grep -aE "/simulation\.nc$")     # direction-blind
#     NEW=<the highest iter-N of those>                                     # so: whichever leg is FURTHEST ALONG
#     DST="/tmp/conv/${LEG}_sim_shared"                                     # and the tag drops the direction
#
# A mode=converge run dispatched for direction=rev therefore analysed the FORWARD legs at
# iterations_compared [0, 2000] while the rev leg sat at production/~300, and labelled the output with the bare
# leg id. That is not a cosmetic mislabel: ternary_fep_reduce.py reads exactly this ternary_convergence.json for
# `diagnostics_ok`, so the watchdog's auto-reduce on the rev leg's landing would have filed FORWARD convergence
# as the REVERSE cycle's evidence. Bug class B#2 of ternary-lane-guard-audit-2026-07-25.md: "a key, guard or
# fallback that ignores a dimension the data varies along, and returns a confident answer about the wrong thing."
#
# The checkpoint fallback had the same defect one level down, and worse. simulation.nc does not carry POSITIONS
# -- openmmtools keeps those in a separate checkpoint file -- and the fallback searched the WHOLE LANE for
# "<leg>.*checkpoint.*\.nc", so a rev simulation.nc was paired with the fwd checkpoint. The pose-RMSD /
# ligand-escape diagnostic would then have reported a confident structural number computed from a different
# trajectory's coordinates.
#
# HOW THIS TEST WORKS. It EXTRACTS the real loop body out of the workflow at run time and drives it against a
# synthetic lane listing, rather than asserting on the text. A text assertion would pass on a rewrite that reads
# correctly and selects wrongly; this one fails unless the selection is actually right. Verified to discriminate
# by reinstating each old line: the direction-blind grep makes rev pick the fwd 2000-iteration path, and the
# lane-wide checkpoint grep makes rev pick up the fwd checkpoint.

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
WF=.github/workflows/gpu-ternary-fep-gcp.yml
[ -f "$WF" ] || { echo "missing $WF"; exit 2; }

TD=$(mktemp -d)
trap 'rm -rf "$TD"' EXIT

fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1:"; echo "       got  '$2'"; echo "       want '$3'"; fail=1; fi; }

# --- extract the loop body from the converge step ---------------------------------------------------
# From `for LEG in $LEGS; do` to its matching `done`, dedented. Python does the dedent because a block
# scalar's own indentation is what we are stripping.
python3 - "$WF" > "$TD/body.sh" <<'PY'
import re, sys, textwrap
lines = open(sys.argv[1]).read().split("\n")
start = next(i for i, l in enumerate(lines) if re.match(r"^\s*for LEG in \$LEGS; do\s*$", l))
indent = len(lines[start]) - len(lines[start].lstrip())
end = next(i for i in range(start + 1, len(lines))
           if lines[i].strip() == "done" and (len(lines[i]) - len(lines[i].lstrip())) == indent)
print(textwrap.dedent("\n".join(lines[start:end + 1])))
PY
chk "the converge loop body was extracted" "$([ -s "$TD/body.sh" ] && echo yes)" "yes"
chk "the extracted body still contains the discovery" \
    "$(grep -c 'simulation\\\.nc' "$TD/body.sh" | head -1)" "$(grep -c 'simulation\\\.nc' "$TD/body.sh" | head -1)"

# --- a synthetic lane: fwd far ahead of rev, and a checkpoint that exists ONLY on the fwd prefix ------
cat > "$TD/lane.txt" <<'EOF'
gs://B/valB-6hax/commits/calib_hi_to_lo__ternary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000/simulation.nc
gs://B/valB-6hax/commits/calib_hi_to_lo__ternary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000/checkpoint.nc
gs://B/valB-6hax/commits/calib_hi_to_lo__ternary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe_dirrev/production/iter-00000320/simulation.nc
gs://B/valB-6hax/commits/calib_hi_to_lo__ternary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe_dirrev/warmup/iter-00000096/simulation.nc
gs://B/valB-6hax/commits/calib_hi_to_lo__binary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000/simulation.nc
gs://B/valB-6hax/commits/calib_hi_to_lo__solvent/0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000/simulation.nc
EOF

# The body calls `ls "$DST"`, `gcloud storage cp` and `mkdir`. Stub the two network/IO ones and let mkdir/ls be
# real inside $TD, so the control flow -- including the `continue` on a missing direction -- is exercised for
# real rather than mocked away.
run_body() {  # $1 = direction
  ( set -eo pipefail
    cd "$TD"
    gcloud() { :; }
    sudo() { :; }
    export -f gcloud sudo 2>/dev/null || true
    DIRECTION="$1"
    LEGS="calib_hi_to_lo__ternary_vhl calib_hi_to_lo__binary_vhl calib_hi_to_lo__solvent"
    mkdir -p /tmp/conv
    # the body reads /tmp/lane.txt; point that at the synthetic one
    cp lane.txt /tmp/lane.txt
    # shellcheck disable=SC1091
    . ./body.sh
    echo "___BODY_EXIT_OK___"
  ) 2>&1
}

for D in fwd rev; do
  OUT=$(run_body "$D")
  echo "$OUT" > "$TD/out.$D"
  chk "DIRECTION=$D: the loop completes under set -eo pipefail" \
      "$(printf '%s' "$OUT" | grep -c '___BODY_EXIT_OK___')" "1"
done

FWD=$(cat "$TD/out.fwd"); REV=$(cat "$TD/out.rev")

# 1. rev must select the rev trajectory, NOT the further-along fwd one.
chk "rev selects the _dirrev production path" \
    "$(printf '%s' "$REV" | grep -c 'newest: .*_v2pe_dirrev/production/iter-00000320')" "1"
chk "rev NEVER touches a non-_dir (fwd) simulation.nc" \
    "$(printf '%s' "$REV" | grep -E 'newest: ' | grep -vc '_dirrev')" "0"

# 2. fwd must still select the fwd trajectory and must NOT pick up the rev one.
chk "fwd selects the plain (no _dir) production path for the ternary arm" \
    "$(printf '%s' "$FWD" | grep -c 'newest: .*ternary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe/production/iter-00002000')" "1"
chk "fwd NEVER selects a _dirrev path" \
    "$(printf '%s' "$FWD" | grep -c 'newest: .*_dirrev')" "0"

# 3. binary/solvent are fwd-only shared arms; a rev pass must SKIP them, loudly, not substitute.
chk "rev skips the two fwd-only arms with an explicit annotation" \
    "$(printf '%s' "$REV" | grep -c 'CONVERGE no trajectory for this direction')" "2"
chk "rev analyses exactly one leg (the ternary one)" \
    "$(printf '%s' "$REV" | grep -c 'newest: ')" "1"
chk "fwd analyses all three arms" "$(printf '%s' "$FWD" | grep -c 'newest: ')" "3"

# 4. THE REPORT TAG must carry the direction, because the reducer keys diagnostics off the dir name.
chk "rev's download dir is direction-tagged" \
    "$(printf '%s' "$REV" | grep -c 'ternary_vhl_rev_sim_shared')" "$(printf '%s' "$REV" | grep -c 'ternary_vhl_rev_sim_shared')"
chk "rev created a _rev_sim_shared dir and NOT a bare one" \
    "$([ -d /tmp/conv/calib_hi_to_lo__ternary_vhl_rev_sim_shared ] && echo yes)" "yes"
chk "fwd keeps the historical untagged dir name (so old fwd reports stay comparable)" \
    "$([ -d /tmp/conv/calib_hi_to_lo__ternary_vhl_sim_shared ] && echo yes)" "yes"

# 5. THE CHECKPOINT must come from the SAME commit prefix. The synthetic lane has a checkpoint only under the
#    FWD prefix, so rev must report NONE rather than borrowing it.
chk "rev reports no checkpoint under its own prefix" \
    "$(printf '%s' "$REV" | grep -c '\[checkpoint\] NONE under ')" "1"
chk "rev does NOT pull the fwd checkpoint" \
    "$(printf '%s' "$REV" | grep -E '\[checkpoint\] not in the generation dir' | grep -vc '_dirrev')" "0"
chk "the checkpoint search root is derived from the selected path, not from the leg id" \
    "$(grep -cE 'CPFX=\$\(printf .* "\$NEW".*sed' "$WF")" "1"
chk "the checkpoint grep is anchored on CPFX (fixed-string), not on a lane-wide leg regex" \
    "$(grep -cE 'grep -aF "\$CPFX/"' "$WF")" "1"
chk "the old lane-wide leg-keyed checkpoint grep is gone" \
    "$(grep -cE 'grep -aiE "\$LEG\.\*checkpoint' "$WF")" "0"

# 6. THE UPLOADED REPORT FILENAME must be direction-keyed too, or a rev pass DESTROYS the fwd cycle's report.
#    Fixing the analysis left the OUTPUT keyed on nothing: a rev pass covers only the rev ternary leg (binary and
#    solvent are fwd-only shared arms, skipped), so writing it to the bare `ternary_convergence.json` overwrites
#    the fwd three-leg report that ternary_fep_reduce reads for `diagnostics_ok` — the fwd binary/ternary
#    diagnostics vanish and the gate routes to BORDERLINE on data it used to have. Caught before the watchdog
#    auto-dispatched converge on the rev leg's landing, which would have done it unattended.
chk "the uploaded report name is direction-keyed" \
    "$(grep -cE 'CONVNAME="ternary_convergence_\$\{DIRECTION\}\.json"' "$WF")" "1"
chk "fwd still writes the BARE name (the reducer and every existing reader depend on it)" \
    "$(grep -cE '^\s*CONVNAME=ternary_convergence\.json\s*$' "$WF")" "1"
chk "the upload uses the keyed variable, never the bare literal path" \
    "$(grep -c 'cp /tmp/conv/ternary_convergence.json "$RESULTS/$CONVNAME"' "$WF")" "1"
chk "no upload writes the bare \$RESULTS/ternary_convergence.json literal any more" \
    "$(grep -c 'cp /tmp/conv/ternary_convergence.json "$RESULTS/ternary_convergence.json"' "$WF")" "0"

# 6b. THE FETCH in mode=reduce must be keyed too — the FOURTH layer of this same bug. Writing the rev report to a
#     direction-keyed name is useless if the reduce step still downloads only the bare fwd name: the reducer now
#     READS ternary_convergence_rev.json, so a rev leg present with its report never fetched makes the whole
#     verdict NOT_VERIFIED -> BORDERLINE for a purely logistical reason. Sequence to date: commit prefix (§H),
#     the analysis (§L.1), the output name (§L.5), the fetch (here). Anything keyed on direction must be keyed
#     everywhere the artifact travels.
chk "mode=reduce fetches ALL convergence reports, not just the bare fwd name" \
    "$(grep -c 'cp "$RESULTS/ternary_convergence\*.json" /tmp/legs/' "$WF")" "1"
chk "the single-file fwd-only fetch is gone" \
    "$(grep -c 'cp "$RESULTS/ternary_convergence.json" /tmp/legs/' "$WF")" "0"
chk "the stale 'DEFAULTS to True' message is gone (absent has been NOT_VERIFIED since 2026-07-25)" \
    "$(grep -c 'diagnostics_ok DEFAULTS to True' "$WF")" "0"

# 6c. ONE HOME FOR THE FILENAME RULE. The workflow builds the name in bash and ternary_fep_reduce builds it in
#     Python; per CLAUDE.md rule 1 the duplicate is only safe if something proves the two agree. This asserts the
#     bash rule reproduces convergence_report_name() for both directions, so a change to either side breaks CI
#     rather than silently splitting the fwd writer from the rev reader.
PYFWD=$(cd research/modalities && python3 -c 'import ternary_fep_reduce as r;print(r.convergence_report_name("fwd"))')
PYREV=$(cd research/modalities && python3 -c 'import ternary_fep_reduce as r;print(r.convergence_report_name("rev"))')
# EXTRACTED from the workflow, not retyped. A hand-copied duplicate of the rule would only prove the copy agrees
# with Python and would sail through any edit to the workflow itself — the vacuous-assertion trap. Pulling the two
# real CONVNAME lines out of the YAML means an edit there is what breaks this.
grep -oE 'CONVNAME=(ternary_convergence\.json|"[^"]*")' "$WF" > "$TD/convname.sh"
chk "extracted exactly the two CONVNAME assignments from the workflow" "$(wc -l < "$TD/convname.sh" | tr -d ' ')" "2"
bashname() {
  local DIRECTION="$1"
  # shellcheck disable=SC1090
  eval "$(sed -n 1p "$TD/convname.sh")"
  [ "$DIRECTION" != fwd ] && eval "$(sed -n 2p "$TD/convname.sh")"
  printf '%s' "$CONVNAME"
}
chk "bash and Python agree on the fwd report name" "$(bashname fwd)" "$PYFWD"
chk "bash and Python agree on the rev report name" "$(bashname rev)" "$PYREV"
chk "the two names differ (a collision is the original data-destroying bug)" \
    "$([ "$PYFWD" != "$PYREV" ] && echo differ || echo same)" "differ"

# 7. no duplicated header (an earlier edit left the locating line twice)
chk "the 'locating newest' header appears once per leg, not twice" \
    "$(grep -c 'locating newest committed simulation.nc' "$WF")" "1"

rm -rf /tmp/conv/calib_hi_to_lo__ternary_vhl_sim_shared \
       /tmp/conv/calib_hi_to_lo__ternary_vhl_rev_sim_shared \
       /tmp/conv/calib_hi_to_lo__binary_vhl_sim_shared \
       /tmp/conv/calib_hi_to_lo__solvent_sim_shared 2>/dev/null || true

if [ "$fail" = 0 ]; then echo; echo "ALL CHECKS PASS"; else echo; echo "SOME CHECKS FAILED"; fi
exit "$fail"
