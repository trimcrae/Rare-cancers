#!/usr/bin/env bash
# The spot commit prefix MUST carry the RESTRAINT state. A restrained leg that resumes an unrestrained
# trajectory is a silent wrong answer, and it is the WORST instance of this lane's recurring keying bug.
#
# WHY WORSE THAN THE fwd/rev ONE (audit sections H / L.1 / L.5 / L.6). The direction collision was caught -- by
# luck -- by OpenFE's assert_multistate_system_equality, because the fwd and rev hybrid Systems have different
# PARTICLE COUNTS. Restrained and unrestrained systems are IDENTICAL IN COMPOSITION: same atoms, same bonds,
# same particle count, differing only by one extra CustomCentroidBondForce added before the integrator. That
# check cannot fire. A resumed run would look perfectly healthy at every level this lane inspects -- iteration
# counts advance, MBAR converges, the pose diagnostic reads a plausible trajectory -- and be wrong.
#
# ═══ METHOD: THE RULE IS EXTRACTED FROM THE WORKFLOW, NEVER RETYPED HERE ═══
# A test that RE-STATES the workflow's bash and then checks its own copy proves only that the copy agrees with
# itself; it passes just as happily when the workflow is deleted. So this test pulls the ACTUAL
# `DIRSUF=` / `RSTSUF=` / `COMMIT_PREFIX=` lines out of gpu-ternary-fep-gcp.yml, evaluates THOSE lines in a
# controlled shell across the 2x2 of (restrain, direction), and asserts on the resulting strings. If someone
# reorders the components, drops one, or renames a variable, this test evaluates the NEW code and fails on the
# result -- which is the only kind of failure worth having.
#
# (Same reason the sibling test_commit_prefix_direction.sh exists; that one asserts on the workflow's STRUCTURE
# -- where the assignment lives relative to the heredoc -- which is a property extraction cannot check. The two
# are complementary, not duplicates.)

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
WF=.github/workflows/gpu-ternary-fep-gcp.yml
[ -f "$WF" ] || { echo "missing $WF"; exit 2; }

fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }
chkne() { if [ "$2" != "$3" ]; then echo "PASS $1"; else echo "FAIL $1: '$2' must differ from '$3'"; fail=1; fi; }

HD_LINE=$(grep -n 'cat > /tmp/startup.sh <<' "$WF" | head -1 | cut -d: -f1)
chk "the startup heredoc is still found" "$([ -n "$HD_LINE" ] && echo yes)" "yes"

# ---- 1. STRUCTURE: RSTSUF is a RUNNER-side assignment, exactly like DIRSUF -------------------------------
# The 2026-07-25 bug was a variable assigned in the VM's shell and read in the runner's. RESTRAIN is a
# runner-level `env:` var and RSTSUF must be assigned before the heredoc, or it expands to empty in the prefix
# and the whole key silently vanishes -- the identical failure, with no particle-count net underneath it.
RST_LINES=$(grep -nE '^[[:space:]]*RSTSUF=' "$WF" | cut -d: -f1)
chk "RSTSUF is assigned exactly once" "$(printf '%s\n' "$RST_LINES" | sed '/^$/d' | wc -l | tr -d ' ')" "1"
chk "RSTSUF is assigned in the RUNNER (before the heredoc)" \
    "$([ "${RST_LINES:-999999}" -lt "$HD_LINE" ] && echo before || echo inside)" "before"

# ---- 2. The restraint is asserted BEFORE a GPU is provisioned, in BOTH directions ------------------------
chk "a restrained leg with no _rst in the prefix is REFUSED" \
    "$(grep -c 'COMMIT PREFIX LOST THE RESTRAINT' "$WF")" "1"
chk "an unrestrained leg with _rst in the prefix is REFUSED" \
    "$(grep -c 'COMMIT PREFIX CLAIMS A RESTRAINT THAT IS NOT SET' "$WF")" "1"

# ---- 3. RBFE_RESTRAIN actually reaches the engine --------------------------------------------------------
# A perfectly-keyed prefix with the flag never exported would produce an UNRESTRAINED run living at a
# restrained prefix: the guard would be intact and the science still wrong.
# EXTRACT the PRODUCTION engine invocation block itself (`env MODE=$TMODE ... nr4a3_ternary_fep.py`) and look
# inside THAT, rather than counting occurrences file-wide -- the workflow also echoes RBFE_RESTRAIN into its
# log, and a check that counted both would pass on the echo alone with the flag never exported.
# NB the file has a SECOND invocation, `env MODE=endpoint_smoke`, which is deliberately NOT included: that mode
# runs plain MD through ternary_endpoint_stability and never reaches rbfe_spot_driver.run_spot_safe, so the
# flag would be inert there. The restraint lives on the alchemical sampling path only.
ENVBLOCK=$(awk '/env MODE=\\\$TMODE/{on=1} on{print} on && /nr4a3_ternary_fep\.py/{exit}' "$WF")
chk "the engine invocation block was found" "$([ -n "$ENVBLOCK" ] && echo yes)" "yes"
chk "RBFE_RESTRAIN=\$RESTRAIN is inside the engine's env invocation" \
    "$(printf '%s\n' "$ENVBLOCK" | grep -c 'RBFE_RESTRAIN=\$RESTRAIN')" "1"
chk "RESTRAIN is a runner-level env: var (so \$RESTRAIN expands runner-side)" \
    "$(grep -cE '^[[:space:]]+RESTRAIN:[[:space:]]' "$WF")" "1"

# ---- 4. BEHAVIOUR: evaluate the workflow's OWN lines, do not restate them --------------------------------
DIRSUF_SRC=$(grep -E '^[[:space:]]*DIRSUF=' "$WF" | head -1)
RSTSUF_SRC=$(grep -E '^[[:space:]]*RSTSUF=' "$WF" | head -1)
PREFIX_SRC=$(grep -E '^[[:space:]]*COMMIT_PREFIX=' "$WF" | head -1)
for v in DIRSUF_SRC RSTSUF_SRC PREFIX_SRC; do
  eval "s=\$$v"
  [ -n "$s" ] || { echo "FAIL could not extract $v from $WF"; fail=1; }
done
[ "$fail" = 0 ] || { echo "extraction failed — not evaluating"; exit "$fail"; }

# Build the prefix the way the workflow does, with the workflow's own text. Everything the lines reference is
# supplied here as the runner would supply it; nothing about the RULE is re-typed.
build_prefix() {
  ( set +u
    RESTRAIN="$1"; DIRECTION="$2"
    BUCKET=proj-rbfe-ckpt; LEG_ID=calib_hi_to_lo__binary_vhl; SEED=0
    TIMESTEP_FS=2.0; CONSTRAIN_LIG=0; WARMUP_TS=1.0; SALT=""
    eval "$DIRSUF_SRC" >/dev/null 2>&1
    eval "$RSTSUF_SRC" >/dev/null 2>&1
    eval "$PREFIX_SRC"
    printf '%s' "$COMMIT_PREFIX" )
}

P_off_fwd=$(build_prefix 0 fwd)
P_on_fwd=$(build_prefix 1 fwd)
P_off_rev=$(build_prefix 0 rev)
P_on_rev=$(build_prefix 1 rev)

echo "  restrain=0 dir=fwd -> $P_off_fwd"
echo "  restrain=1 dir=fwd -> $P_on_fwd"
echo "  restrain=0 dir=rev -> $P_off_rev"
echo "  restrain=1 dir=rev -> $P_on_rev"

# 4a. THE POINT OF THE WHOLE EXERCISE: all four are distinct storage locations.
n_distinct=$(printf '%s\n%s\n%s\n%s\n' "$P_off_fwd" "$P_on_fwd" "$P_off_rev" "$P_on_rev" | sort -u | wc -l | tr -d ' ')
chk "restrain x direction gives FOUR distinct commit prefixes" "$n_distinct" "4"

# 4b. Unrestrained fwd must be BYTE-IDENTICAL to the pre-restraint form, or every committed generation in the
#     bucket is orphaned and the change quietly throws away finished GPU hours. This is the one string in the
#     file that is deliberately hard-coded: it is the historical contract, not a copy of the current rule.
chk "restrain=0 fwd is byte-identical to the historical prefix" \
    "$P_off_fwd" "gs://proj-rbfe-ckpt/valB-6hax/commits/calib_hi_to_lo__binary_vhl/0_dt2.0fs_clig0_wu1.0"
chk "restrain=0 rev is byte-identical to the historical rev prefix" \
    "$P_off_rev" "gs://proj-rbfe-ckpt/valB-6hax/commits/calib_hi_to_lo__binary_vhl/0_dt2.0fs_clig0_wu1.0_dirrev"

# 4c. The restrained prefix must actually carry _rst, and the direction must stay TERMINAL so the sibling
#     test's end-anchored `*_dir$DIRECTION` assertion in the workflow keeps holding.
case "$P_on_fwd" in *_rst) echo "PASS restrain=1 fwd ends in _rst" ;; *) echo "FAIL restrain=1 fwd: '$P_on_fwd'"; fail=1 ;; esac
case "$P_on_rev" in *_rst_dirrev) echo "PASS restrain=1 rev is _rst then _dirrev (direction stays terminal)" ;;
  *) echo "FAIL restrain=1 rev: '$P_on_rev' — the direction must remain the LAST component"; fail=1 ;; esac

# 4d. A restrained prefix is not merely a suffix of an unrestrained one, and vice versa: no `ls` prefix scan can
#     confuse the two directories.
chkne "restrained and unrestrained fwd prefixes differ" "$P_on_fwd" "$P_off_fwd"
chkne "restrained and unrestrained rev prefixes differ" "$P_on_rev" "$P_off_rev"

# 4e. A commit_salt containing the letters 'rst' must NOT masquerade as a restraint key. The workflow's
#     assertion is end-anchored through $DIRSUF for exactly this reason; check the built prefix agrees.
salted() {
  ( set +u
    RESTRAIN="$1"; DIRECTION=fwd
    BUCKET=proj-rbfe-ckpt; LEG_ID=leg; SEED=0
    TIMESTEP_FS=2.0; CONSTRAIN_LIG=0; WARMUP_TS=""; SALT=rstest
    eval "$DIRSUF_SRC" >/dev/null 2>&1
    eval "$RSTSUF_SRC" >/dev/null 2>&1
    eval "$PREFIX_SRC"
    printf '%s' "$COMMIT_PREFIX" )
}
S_off=$(salted 0); S_on=$(salted 1)
case "$S_off" in *_rst) echo "FAIL a salt of 'rstest' made an unrestrained prefix end in _rst: $S_off"; fail=1 ;;
  *) echo "PASS a salt containing 'rst' does not fake the restraint key" ;; esac
chkne "salted restrained vs unrestrained still differ" "$S_on" "$S_off"

# ---- 4f. The REFUSAL itself, evaluated -------------------------------------------------------------------
# Checks 2 above only prove the error strings are present. This runs the workflow's OWN assertion block against
# a prefix/flag pair that disagrees, and requires a non-zero exit -- i.e. that the gate actually refuses to
# provision a GPU rather than merely containing a scary message. Extracted from `case "$COMMIT_PREFIX"` down to
# the end of the second `if`, again without restating the rule.
ASSERT_SRC=$(awk '/^[[:space:]]*case "\$COMMIT_PREFIX" in$/{buf="";on=1}
                  on{buf=buf $0 "\n"}
                  on && /HAS_RST/{seen=1}
                  on && seen && /^[[:space:]]*fi$/{n++; if(n==2){printf "%s", buf; exit}}' "$WF")
chk "the restraint assertion block was extracted" "$([ -n "$ASSERT_SRC" ] && echo yes)" "yes"
assert_exit() {  # $1=RESTRAIN $2=COMMIT_PREFIX $3=DIRSUF -> the block's exit status
  # `echo $?` must sit OUTSIDE the subshell: the block's refusal is a bare `exit 1`, which ends the subshell
  # before any statement after the eval could run. (First cut had it inside and every refusal read as '').
  ( set +u; RESTRAIN="$1"; COMMIT_PREFIX="$2"; DIRSUF="$3"
    eval "$ASSERT_SRC" ) >/dev/null 2>&1
  echo $?
}
chk "consistent restrained pair is ACCEPTED"      "$(assert_exit 1 "gs://b/leg/0_wu_rst" "")"        "0"
chk "consistent unrestrained pair is ACCEPTED"    "$(assert_exit 0 "gs://b/leg/0_wu" "")"            "0"
chk "restrain=1 with an unrestrained prefix is REFUSED (exit 1)" \
    "$(assert_exit 1 "gs://b/leg/0_wu" "")" "1"
chk "restrain=0 with a restrained prefix is REFUSED (exit 1)" \
    "$(assert_exit 0 "gs://b/leg/0_wu_rst" "")" "1"
chk "the rev form is recognised through DIRSUF"   "$(assert_exit 1 "gs://b/leg/0_wu_rst_dirrev" "_dirrev")" "0"
chk "a rev prefix missing _rst is REFUSED"        "$(assert_exit 1 "gs://b/leg/0_wu_dirrev" "_dirrev")" "1"

# ---- 5. The commit-manifest fingerprint is the SECOND guard, and it must move with the flag ---------------
# The prefix is the primary key; the fingerprint is what still holds if a prefix is reused by hand or by a lane
# that builds its own. Checked here by running the real function, not by reading the source.
python3 - "$PWD" <<'PY'
import sys, os
sys.path.insert(0, os.path.join(sys.argv[1], "research", "modalities"))
import rbfe_spot_checkpoint as ck

base = {"LEG_ID": "leg", "DIRECTION": "fwd", "SEED": "0", "CHARGE_METHOD": "nagl",
        "SETUP_CACHE_VERSION": "v1", "N_WINDOWS": "12", "RBFE_TIMESTEP_FS": "2.0",
        "RBFE_WARMUP_TIMESTEP_FS": "", "RBFE_CONSTRAIN_LIGAND_CH": "0"}
fp_off = ck.system_fingerprint(base)[0]
fp_on = ck.system_fingerprint(dict(base, RBFE_RESTRAIN="1"))[0]
fp_zero = ck.system_fingerprint(dict(base, RBFE_RESTRAIN="0"))[0]
bad = 0
if fp_on == fp_off:
    print("FAIL RBFE_RESTRAIN=1 does not change the system fingerprint"); bad = 1
else:
    print("PASS RBFE_RESTRAIN=1 changes the system fingerprint")
if fp_zero != fp_off:
    print("FAIL RBFE_RESTRAIN=0 changed the legacy fingerprint (orphans every committed generation)"); bad = 1
else:
    print("PASS RBFE_RESTRAIN=0/unset keeps the legacy fingerprint byte-stable")
# a restrained run must REFUSE an unrestrained committed generation, and say why by name
man = {"schema": 2, "system_fingerprint": fp_off,
       "system_fingerprint_fields": ck.system_fingerprint(base)[1]}
why = ck.fingerprint_mismatch_reason(man, dict(base, RBFE_RESTRAIN="1"))
if not why:
    print("FAIL a restrained run accepted an UNRESTRAINED committed generation"); bad = 1
elif "RBFE_RESTRAIN" not in why:
    print("FAIL the refusal does not name RBFE_RESTRAIN: %s" % why); bad = 1
else:
    print("PASS a restrained run refuses an unrestrained generation and names RBFE_RESTRAIN")
man_on = {"schema": 2, "system_fingerprint": fp_on,
          "system_fingerprint_fields": ck.system_fingerprint(dict(base, RBFE_RESTRAIN="1"))[1]}
if not ck.fingerprint_mismatch_reason(man_on, base):
    print("FAIL an unrestrained run accepted a RESTRAINED committed generation"); bad = 1
else:
    print("PASS an unrestrained run refuses a restrained generation")
if ck.fingerprint_mismatch_reason(man, base) is not None:
    print("FAIL a matching unrestrained generation was refused"); bad = 1
else:
    print("PASS a matching unrestrained generation still restores")
# the well width and wall stiffness are not workflow inputs, so the fingerprint is their only record
for var in ("RBFE_RESTRAIN_TOL_NM", "RBFE_RESTRAIN_K"):
    if ck.system_fingerprint(dict(base, RBFE_RESTRAIN="1", **{var: "0.5"}))[0] == fp_on:
        print("FAIL %s does not change the fingerprint" % var); bad = 1
    else:
        print("PASS %s changes the fingerprint" % var)
sys.exit(bad)
PY
[ $? = 0 ] || fail=1

[ "$fail" = 0 ] && echo "commit-prefix restraint: all checks pass"
exit "$fail"
