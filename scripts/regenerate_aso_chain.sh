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
#     -> build_submission_pdf  BOTH styles: journal AND --style manuscript are different deposited
#                              files, and the bare command writes only the first
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
  # ⛔ THE DEEPER RE-SCREENS ARE EXCLUDED BY THE RELEASE'S OWN RULE, NOT BY AN OVERSIGHT.
  # The SI states the reason: the deeper re-screens "are released ungraded because the graded model
  # adds nothing where no hit list is truncated". Sweeping them in took the corpus from the
  # committed 39 to 92 and made three released sentences false; the round-7 ledger §2b traced it to
  # the end and CLOSED it as "keep 39", having confirmed the deeper screens' one extra clean design
  # (GGGCATATCAAGCGCT at TCF12 exon 7) is already reported in the manuscript and in the
  # best-available-design-per-junction table. ⚠ NAMED BY CONTENT, NOT BY NUMBER: this read "Table 7"
  # and the design has never been in that table — it is the TCF12 e7 row of what is now Table 2.
  # ⚠ SO THE EXCLUSION BELONGS HERE, AT THE GENERATOR. Leaving the sweep wide and catching it with
  # the guard below meant a referee cloning the archive and running this script got exit 1 and 53
  # untracked files on a repository that was CORRECT. A verification command that fails on a clean
  # clone cannot be the one the paper names.
  # ⭐ THE GLOB'S VIRTUE SURVIVES: a new junction screen still enters the corpus with nobody
  # remembering to add it here. Only the depth variant the release deliberately leaves ungraded is
  # filtered, the skip is COUNTED AND PRINTED so the decision stays visible at the moment it is
  # taken, and the count guard below still fires if the corpus diverges for any other reason.
  _sweep=$(ls $MOD/junction-aso-offtarget-*.json 2>/dev/null \
    | grep -v -- '-graded' | grep -v 'locus-collapse' | grep -v 'deep500' || true)
  _skipped=$(ls $MOD/junction-aso-offtarget-*.json 2>/dev/null \
    | grep -v -- '-graded' | grep -v 'locus-collapse' | grep -c 'deep500' || true)
  # shellcheck disable=SC2046,SC2086
  python3 $MOD/junction_aso_offtarget.py --rescore $(echo $_sweep | tr '\n' ' ') \
    >/dev/null 2>&1 || true
  echo "   $(ls $MOD/junction-aso-offtarget-*-graded.json 2>/dev/null | wc -l | tr -d ' ') graded artifact(s)"
  echo "   $_skipped deeper re-screen(s) skipped — released ungraded by SI §S4's stated rule"

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
  # ⚠ THE SWEEP ABOVE NOW EXCLUDES THE DELIBERATELY-UNGRADED SCREENS, SO THIS GUARD NO LONGER FIRES
  # ON A CORRECT TREE — and that is the point. It is kept, not retired, because it is the only check
  # that reads the corpus rather than the rule: it catches a graded artifact arriving by any route
  # the filter above does not model.
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
    # ⛔ THE `ok` USED TO BE UNCONDITIONAL (2026-08-19). A step that failed printed
    #     == prior-art evidence
    #        FAILED: python3 .../aso_priorart_evidence.py
    #        ok
    # The final verdict was still right, but a reader scanning the per-step column saw `ok` against
    # the step that had just failed — and this script is what the manuscript's Availability
    # statement tells a reader to run and read.
    if eval "$cmd" >/dev/null 2>&1; then
      echo "   ok"
    else
      echo "   FAILED: $cmd"
      fail=1
    fi
  fi
}

run_step "locus collapse"      "python3 $MOD/junction_aso_locus_collapse.py --write" ""
run_step "chance baseline"     "python3 $MOD/offtarget_chance_baseline.py"           ""
run_step "duplex thermodynamics" "python3 $MOD/junction_aso_thermo.py"   "python3 $MOD/junction_aso_thermo.py --check"
# ⛔ THE ENERGY RE-EVALUATION RUNS AFTER THE SCREENS AND READS THEIR OUTPUT, SO IT BELONGS HERE
# AND NOT EARLIER. It re-scores every alignment `junction_aso_offtarget.py` returned, which is the
# second stage the 2025 industry recommendations (PMID 39912803) prescribe after an over-sensitive
# similarity search. Its figures are quoted by the condensed article and pinned, so a screen that
# moves without this step rerunning would leave the manuscript quoting a stale separation.
run_step "offtarget duplex energy" "python3 $MOD/aso_offtarget_duplex_energy.py" "python3 $MOD/aso_offtarget_duplex_energy.py --check"
# ⛔ THE PER-JUNCTION TABLE WAS NOT IN THIS CHAIN, AND FIVE ARTIFACTS DOWNSTREAM READ IT (2026-08-17).
# `aso-per-junction-table.json` supplies every clinical tier, best-available design and parent-duplex
# figure that Tables 2, 3 and 5, the coverage ladder and the canonical sequence file are built from —
# and editing its generator changed nothing, because nothing regenerated it. The tier correction two
# blind screens filed as a MAJOR reached the submission tables (which re-read the refs) and NOT the
# artifact, so the deposit would have shipped with the two halves of one fix disagreeing. Runs
# offline in 0.3 s and is byte-deterministic on rerun; it belongs before every consumer below.
run_step "per-junction table"  "python3 $MOD/aso_per_junction_table.py"              ""
run_step "non-canonical acceptor table" "python3 $MOD/aso_noncoding_acceptor_screened_table.py" ""
# ⚠ LABELLED BY WHAT EACH PANEL SHOWS, NEVER BY ITS FIGURE NUMBER (re-anchored 2026-08-17). These
# read "figure 1/2/3" until the numbering moved twice underneath them — the chance-baseline panel
# became Supplementary Figure S1 on 2026-08-15, and the seam and gap-length panels swapped on
# 2026-08-17 when the deposit was renumbered to citation order — leaving a step label that named a
# figure this chain was not drawing. A title travels with its content; a number does not, and the
# manuscript's `Figure legends` section is the one home for which number each panel carries.
#
# ⛔ ALL FOUR PANELS, NOT THREE (2026-08-17). The gap-length panel was missing from this list and
# from the `_regenerate` recipe inside `aso-figure-provenance.json`, while the provenance step
# BELOW re-pinned its source hashes on every run. A chain that redraws three figures and blesses
# four is worse than one that redraws none: it makes `--check` pass over a stale panel. The set of
# steps here is now asserted against `aso_figure_provenance.GENERATORS` by
# `research/manuscripts/tests/test_aso_figure_chain_is_complete.py`, so adding a fifth figure
# without adding its step here fails preflight rather than shipping a figure nobody redrew.
run_step "figure · junction space"     "python3 $FIG/aso_junction_space_figure.py"     ""
run_step "figure · gap-length tradeoff" "python3 $FIG/aso_gap_length_figure.py"        ""
run_step "figure · multipartner seam"  "python3 $FIG/aso_multipartner_seam_figure.py"  ""
run_step "figure · chance baseline"    "python3 $FIG/aso_chance_baseline_figure.py"    ""
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
# ⛔ THE CANONICAL SEQUENCE FILE IS DERIVED, AND IT RUNS BEFORE THE MANIFEST HASHES IT. Added
# 2026-08-17: the deposited PDF prints table sequences without their delimiters, so whether a
# copy-pasted oligo carries a trailing digit is a property of the reader's PDF extractor. The
# durable fix is a machine-readable copy that was never typeset, and its generator ASSERTS that
# every sequence the three documents name is present -- so this step fails rather than shipping a
# "canonical" file that is missing a sequence the paper prints.
run_step "canonical sequences" "python3 $MAN/aso_sequence_manifest.py" "python3 $MAN/aso_sequence_manifest.py --check"
run_step "prior-art evidence"  "python3 $MAN/aso_priorart_evidence.py" "python3 $MAN/aso_priorart_evidence.py --check"
# ⛔ THE TWO DEPOSITED PDFs WERE NOT IN THIS CHAIN, AND THEY ARE THE FILES A READER DOWNLOADS
# (added 2026-08-19). Measured that day: a prose fix to §2.10 was followed by `build_submission_pdf.py`
# with no arguments, which writes the JOURNAL format and the SI and NOTHING ELSE — the submission
# format silently stayed at the previous revision and was caught only by reading `git diff --stat`.
# A one-command regeneration that does not produce the deposit is the staleness bug this script
# exists to prevent, wearing the costume of a green chain.
# ⚠ AFTER the tables, references and canonical sequence file, because the PDFs are rendered FROM
# those; BEFORE the archive manifest, because it hashes the PDFs. `--style` is not a formatting
# preference — each invocation writes a DIFFERENT deposited file, so both are required.
# ⭐ AND THEY GET A REAL --check, NOT AN "unverified" LINE. Each build writes a stamp holding the
# sha256 of every source it rendered, so staleness is decidable without rebuilding: compare each
# recorded hash against the file on disk. ⚠ MTIME WOULD NOT DO — a rebuild that changes nothing
# still moves the timestamp, and `git checkout` moves it backwards.
# ⚠ A FUNCTION, NOT A QUOTED STRING. The first attempt inlined this python into a shell variable and
# the nested quotes broke the script at parse time — a chain that cannot be parsed verifies nothing.
_pdf_stamps_current() {
  python3 - <<'PDFSTAMP'
import glob, hashlib, json, os, sys
base = "research/manuscripts"
stamps = sorted(glob.glob(os.path.join(base, "aso", "*.build-stamp.json")))
if not stamps:
    print("no build stamp exists, so no deposited PDF can be shown current")
    sys.exit(1)
stale = []
for st in stamps:
    for rel, want in json.load(open(st))["built_from"].items():
        p = os.path.join(base, rel)
        got = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
        if got != want:
            stale.append(f"{os.path.basename(st)} <- {rel}")
for s in stale:
    print("STALE:", s)
sys.exit(1 if stale else 0)
PDFSTAMP
}
run_step "deposited PDF · journal format"    "python3 $MAN/build_submission_pdf.py" "_pdf_stamps_current"
run_step "deposited PDF · submission format" "python3 $MAN/build_submission_pdf.py --style manuscript" "_pdf_stamps_current"
# ⛔ THE ANONYMIZED UPLOAD IS BUILT EVERY TIME, BECAUSE THE VENUE WILL NOT SAY WHICH IT WANTS.
# NAT's guidelines state single-anonymized twice and double-anonymized once, on one page, and the
# journal returns a non-conforming manuscript for amendments BEFORE peer review. Building both
# turns that contradiction into a choice made at the upload form instead of a discovery made
# after a rejection. It is a mechanical derivation of the finished manuscript, guarded by
# research/manuscripts/tests/test_the_anonymized_build_hides_only_identity.py, which pins that it
# removes identity and changes nothing else.
run_step "anonymized upload · journal format" "python3 $MAN/build_submission_pdf.py --paper aso-journal --anonymized" ""
# ⛔ AND THE WORD FILE, WHICH IS THE ONE A JOURNAL ACTUALLY ACCEPTS (added 2026-08-23). Nucleic
# Acid Therapeutics: "The preferred format for your manuscript is Word … The LaTeX files are also
# accepted." PDF is not on that list, so the .docx is a deposit artifact on exactly the same footing
# as the two PDFs above and goes stale the same silent way. It is built from the same HTML as the
# submission-format PDF, so it belongs immediately after them and BEFORE the archive manifest, which
# hashes it.
# ⚠ NEEDS `libreoffice-writer` ON THE MACHINE. `libreoffice-core` alone reports every input as
# unloadable, including a two-line .txt, which reads as a corrupt manuscript rather than a missing
# filter. If this step fails for that reason the fix is to install the package, NOT to drop the step:
# a submission whose only manuscript formats are PDF is returned before peer review.
run_step "Word manuscript · submission format" "python3 $MAN/build_submission_docx.py" \
         "python3 -m pytest $MAN/tests/test_the_word_manuscript_is_current_and_whole.py -q"
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
