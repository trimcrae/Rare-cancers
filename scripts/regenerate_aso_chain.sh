#!/usr/bin/env bash
# Regenerate every fusion-junction ASO artifact in DEPENDENCY ORDER, then verify each one.
#
# WHY THIS EXISTS. Twenty-two junction screens were dispatched on 2026-08-13 (runs 31657425546 and
# 31657434781). When they land, SIX artifacts and THREE figures must be re-derived, and the order is
# not obvious: the archive manifest hashes every other artifact, so regenerating it before the
# others leaves the deposit describing files that no longer exist in that form. The submission
# packet reads the metrics; the metrics read the manuscript and its companions; the tables read the
# locus collapse AND the chance baseline. Held together by remembering it, this is a staleness bug
# waiting to be caught by CI after a push -- which is precisely how the endpoint chain next door
# earned its own script.
#
# ⛔ THE ORDER IS THE WHOLE POINT, AND IT IS NOT ALPHABETICAL:
#
#   screens (--rescore)      -> junction-aso-offtarget-*-graded.json
#     -> locus_collapse      reads every screen; owns the orientation verdict
#     -> chance_baseline     reads the exhaustive-scan evaluations
#     -> thermo              reads the atlas (independent of the two above, ordered for readability)
#     -> figures             read the collapse, the chance baseline and the atlas
#     -> svg_to_submission_formats   rasterises whatever the figures just wrote
#     -> submission_tables   reads the atlas, the collapse AND the chance baseline
#     -> submission_citations        renumbers superscripts from the manuscript
#     -> submission_metrics  reads the manuscript and its companion files
#     -> submission_packet   reads the metrics
#     -> priorart_evidence   reads the literature-cache branch
#     -> archive_manifest    hashes ALL of the above, so it must be LAST
#
# ⚠ THE RE-SCORE IS NOT OPTIONAL AFTER A NEW SCREEN. `grade_one` reads each screen's own counters
# and histogram, so a screen that lands without a matching `-graded.json` silently drops out of the
# graded corpus rather than failing -- the Methods claim that every gap-resolved screen was
# re-scored would quietly become false. Screens that are coverage-only are REFUSED by
# `screen_is_gap_resolved` and that refusal is expected, not an error.
#
# ⚠ WHAT THIS DOES NOT DO. It does not run the screens themselves: those need NCBI BLAST over the
# network and are dispatched through .github/workflows/aso-offtarget.yml. This regenerates only what
# is derivable offline from committed artifacts.
#
#   ./scripts/regenerate_aso_chain.sh            # regenerate, in order
#   ./scripts/regenerate_aso_chain.sh --check    # exit 1 if anything is stale, change nothing
set -euo pipefail
cd "$(dirname "$0")/.."

CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1
unverified=""

MOD=research/modalities
MAN=research/manuscripts
FIG=$MAN/figures

say() { printf '\n== %s\n' "$1"; }
fail=0

# ── 0 · the graded re-scores, one per gap-resolved screen ────────────────────────────────────
# Globbed, never listed: a screen added by a dispatch must enter the corpus without anyone
# remembering to add it here. `|| true` on the sweep because a coverage-only screen is REFUSED by
# design and that refusal must not abort the chain.
if [ "$CHECK" = 0 ]; then
  say "graded re-scores (screens -> -graded.json)"
  # shellcheck disable=SC2046
  python3 $MOD/junction_aso_offtarget.py --rescore \
    $(ls $MOD/junction-aso-offtarget-*.json 2>/dev/null | grep -v -- '-graded' | grep -v 'locus-collapse' | tr '\n' ' ') \
    >/dev/null 2>&1 || true
  echo "   $(ls $MOD/junction-aso-offtarget-*-graded.json 2>/dev/null | wc -l | tr -d ' ') graded artifact(s)"

  # ⛔ THIS STEP SILENTLY OVERPRODUCED AGAINST A DOCUMENTED DECISION (measured 2026-08-17).
  # The glob above regrades EVERY screen, so a chain run took the graded corpus from the committed
  # 39 to 92 — 53 new untracked artifacts. The repository does not merely tolerate 39: the SI states
  # a reason for it, that "the 53 deeper re-screens are released ungraded because the graded model
  # adds nothing where no hit list is truncated". So the chain and the submission documents
  # disagreed about what the corpus IS, and running the chain quietly made three released sentences
  # false plus two pinned counts stale.
  # ⚠ AND IT IS NOT PURELY A DENOMINATOR. Grading the deeper re-screens extends the predicted-clean
  # set by one design, GGGCATATCAAGCGCT — the TCF12 exon 7 design section 2.7 discusses by name —
  # because that design had no graded record at all before. Whether it BELONGS there is a question
  # about the paper, not about this script, and it is filed in the round-7 ledger rather than
  # decided here.
  # ⭐ The count guard in test_aso_submission_numbers.py caught this, which is why the state was
  # recoverable. This warning exists so the chain says so at the moment it happens, instead of
  # leaving a later test to discover it.
  _tracked=$(git ls-files "$MOD" 2>/dev/null | grep -c -- '-graded.json' || true)
  _ondisk=$(ls $MOD/junction-aso-offtarget-*-graded.json 2>/dev/null | wc -l | tr -d ' ')
  if [ -n "$_tracked" ] && [ "$_tracked" -gt 0 ] && [ "$_ondisk" != "$_tracked" ]; then
    echo "   ⚠ $_ondisk graded artifacts on disk against $_tracked tracked."
    echo "     The submission documents state a reason for the tracked count, so this is a"
    echo "     DECISION to make and not a diff to commit. Either delete the untracked artifacts"
    echo "     (git clean -n $MOD to see them first), or update the SI's rationale, the three"
    echo "     released sentences that state the count, and the pins in"
    echo "     test_aso_submission_numbers.py — together, in one commit."
    fail=1
  fi
fi

# ── 1 · producers, in dependency order ───────────────────────────────────────────────────────
# Each entry: "label|command|check-command". An empty check-command means the producer has no
# --check mode and is verified by regenerating and diffing the tree instead.
# ⛔ THIS FUNCTION USED TO PRINT A VERIFICATION THAT DID NOT EXIST (fixed 2026-08-16).
# For every producer with no --check mode it printed "(no --check mode; verified by the tree diff
# below)" -- and there was NO tree diff, anywhere in this file. `grep -n "git " ` returned nothing.
# So `--check` reported a clean chain while silently vouching for artifacts it had never compared,
# which is the same shape as the gates round 7 found reporting green over stale deposit files.
# ⚠ Fixed by making the gap VISIBLE rather than by inventing a diff: an unverifiable step is now
# named as unverified, counted, and reprinted in the summary, so `--check` can no longer end in an
# unqualified OK while producers remain uninspected.
run_step() {
  local label="$1" cmd="$2" chk="$3"
  say "$label"
  if [ "$CHECK" = 1 ]; then
    if [ -n "$chk" ]; then
      if eval "$chk" >/dev/null 2>&1; then echo "   current"; else echo "   STALE"; fail=1; fi
    else
      echo "   ⚠ NOT VERIFIED -- this producer has no --check mode"
      unverified="$unverified $label"
    fi
  else
    eval "$cmd" >/dev/null 2>&1 || { echo "   FAILED: $cmd"; fail=1; }
    echo "   ok"
  fi
}

run_step "locus collapse"      "python3 $MOD/junction_aso_locus_collapse.py --write" ""
run_step "chance baseline"     "python3 $MOD/offtarget_chance_baseline.py"           ""
run_step "duplex thermodynamics" "python3 $MOD/junction_aso_thermo.py"   "python3 $MOD/junction_aso_thermo.py --check"
run_step "figure 1 junction space"   "python3 $FIG/aso_junction_space_figure.py"     ""
run_step "figure 2 multipartner seam" "python3 $FIG/aso_multipartner_seam_figure.py" ""
run_step "figure 3 chance baseline"  "python3 $FIG/aso_chance_baseline_figure.py"    ""
run_step "figure submission formats" "python3 $FIG/svg_to_submission_formats.py"     ""
# ⛔ RECORD THE FIGURES' PROVENANCE IMMEDIATELY AFTER DRAWING THEM, AND BEFORE ANYTHING HASHES THEM.
# Omitted until 2026-08-14, which made this script report `ASO CHAIN OK` while leaving a gate red:
# `aso_figure_provenance.py` pins the hash of every artifact the figures were drawn from, so any
# chain run that moved one of those artifacts — that day, `offtarget-chance-baseline.json` gaining
# its published geometry exclusions — left the record naming the OLD hash, and
# `research/manuscripts/tests/test_aso_figure_provenance.py` failed in preflight straight after a
# green chain. A regeneration script that leaves a checker stale is worse than no script: it is the
# one place a maintainer trusts not to have to remember the order.
run_step "figure provenance"   "python3 $FIG/aso_figure_provenance.py" "python3 $FIG/aso_figure_provenance.py --check"
run_step "submission tables"   "python3 $MAN/submission_tables.py"   "python3 $MAN/submission_tables.py --check"
run_step "submission references" "python3 $MAN/submission_citations.py --write" "python3 $MAN/submission_citations.py --check"
run_step "submission metrics"  "python3 $MAN/submission_metrics.py"  "python3 $MAN/submission_metrics.py --check"
run_step "submission packet"   "python3 $MAN/submission_packet.py"                   ""
run_step "prior-art evidence"  "python3 $MAN/aso_priorart_evidence.py" "python3 $MAN/aso_priorart_evidence.py --check"
# ⛔ LAST, ALWAYS. It hashes every artifact above; run it earlier and the deposit describes a tree
# that no longer exists.
run_step "archive manifest"    "python3 $MAN/aso_archive_manifest.py" "python3 $MAN/aso_archive_manifest.py --check"

# ── 2 · the gates that read what was just written ────────────────────────────────────────────
say "gates"
for g in "python3 $MAN/lint_consistency.py" "python3 $MAN/lint_citations.py" "python3 $MAN/lint_style.py"; do
  if eval "$g" >/dev/null 2>&1; then echo "   OK   ${g##*/}"; else echo "   FAIL ${g##*/}"; fail=1; fi
done

if [ "$fail" != 0 ]; then
  printf '\nASO CHAIN: something is stale or failed -- see above.\n'
  exit 1
fi
if [ "$CHECK" = 1 ] && [ -n "$unverified" ]; then
  printf '\nASO CHAIN: every checkable producer is current, but --check CANNOT VOUCH FOR:%s\n' "$unverified"
  printf 'Give each of those a --check mode; until then a green --check is a partial answer.\n'
  exit 0
fi
printf '\nASO CHAIN OK\n'
