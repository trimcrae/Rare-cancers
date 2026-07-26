#!/usr/bin/env bash
# iter_timing_profile.awk is the diagnostic that decides whether the ternary leg's ETA is trustworthy, so it must
# be exercised somewhere cheaper than a dispatched CI run against a live GPU VM.
#
# It answers two questions and this test pins both:
#   SEGMENT lines -- whether per-iteration cost is CONSTANT or RISING with accumulated iterations. This is what
#                    makes an ETA computed from a current rate sound or optimistic, and it is phase-FREE, which is
#                    why it is the line to trust (see case 7).
#   PHASE lines   -- warmup vs production cost. These are DERIVED FROM A LAGGING STREAM and can be wrong; case 7
#                    reproduces the real failure and pins that the profile says so out loud rather than presenting
#                    a buffer artifact as a phase boundary. The authoritative phase source is the GCS census.
#
# It also pins the delivery path. The program is base64'd into `gcloud compute ssh --command` because embedding
# it literally cannot work: that argument is single-quoted, so the program could contain no single quote at all,
# and double-quoting it instead would have $0/NF eaten by the remote shell. Encoding removes both constraints --
# the program's own bytes stop mattering entirely, which is the point. What DOES still matter is that the encoded
# token is safe to pass unquoted, so that is what is asserted (a first draft of this test asserted the file had no
# single quote; that was a leftover of the pre-encoding design and the encoding makes it vacuous).

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
PROG=iter_timing_profile.awk
[ -f "$PROG" ] || { echo "missing $PROG"; exit 2; }

TD=$(mktemp -d); trap 'rm -rf "$TD"' EXIT
fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1:"; echo "       got  '$2'"; echo "       want '$3'"; fail=1; fi; }

# --- delivery-path constraints ------------------------------------------------------------------------
chk "the base64 token is safe to pass UNQUOTED in the ssh --command (base64 alphabet only)" \
    "$(base64 -w0 < "$PROG" | grep -cE '^[A-Za-z0-9+/=]+$')" "1"
chk "the program is never inlined into the ssh --command (only the encoded token is)" \
    "$(grep -c 'WARMUP from iter' ../../.github/workflows/gpu-ternary-fep-gcp.yml)" "0"
chk "the program survives a base64 round-trip byte-for-byte" \
    "$(base64 -w0 < "$PROG" | base64 -d | cmp -s - "$PROG" && echo same)" "same"
chk "the workflow ships the FILE, not an inline heredoc" \
    "$(grep -c 'base64 -w0 < research/modalities/iter_timing_profile.awk' ../../.github/workflows/gpu-ternary-fep-gcp.yml)" "1"
chk "no heredoc terminator for the awk program remains in the workflow (it broke the YAML)" \
    "$(grep -cE "^AWK$" ../../.github/workflows/gpu-ternary-fep-gcp.yml)" "0"

# --- CASE 1: warmup ~34 s, production ~66 s, both CONSTANT --------------------------------------------
{
  echo "[spot-driver] WARMUP timestep overridden to 1.0 fs"
  echo "[spot-driver] WARMUP from iter 0 -> 400 (interval=8)"
  for i in $(seq 1 120); do echo "Iteration took 34.0s."; done
  echo "[spot-driver] PRODUCTION created from warmup; run -> 2000"
  for i in $(seq 1 250); do echo "Iteration took 66.0s."; done
} > "$TD/const.log"
OUT=$(awk -f "$PROG" "$TD/const.log" | sort)
printf '%s\n' "$OUT" | sed 's/^/    /'
chk "C1 warmup mean is 34.00s over 120 iterations" \
    "$(printf '%s\n' "$OUT" | grep -c 'PHASE warmup .*n=120 .*mean= 34.00s')" "1"
chk "C1 production mean is 66.00s over 250 iterations" \
    "$(printf '%s\n' "$OUT" | grep -c 'PHASE production .*n=250 .*mean= 66.00s')" "1"
chk "C1 production is split into 3 blocks of 100/100/50" \
    "$(printf '%s\n' "$OUT" | grep -c '^BLOCK production/')" "3"
chk "C1 every production block reads 66.00s (constant cost is visible AS constant)" \
    "$(printf '%s\n' "$OUT" | grep '^BLOCK production/' | grep -c 'mean= 66.00s')" "3"

# --- CASE 2: production cost RISES with iteration count -- the case that invalidates an ETA ------------
{
  echo "[spot-driver] WARMUP from iter 0 -> 400 (interval=8)"
  for i in $(seq 1 50); do echo "Iteration took 34.0s."; done
  echo "[spot-driver] PRODUCTION created from warmup; run -> 2000"
  for i in $(seq 1 100); do echo "Iteration took 40.0s."; done
  for i in $(seq 1 100); do echo "Iteration took 60.0s."; done
  for i in $(seq 1 100); do echo "Iteration took 90.0s."; done
} > "$TD/rising.log"
OUT2=$(awk -f "$PROG" "$TD/rising.log" | sort)
printf '%s\n' "$OUT2" | sed 's/^/    /'
chk "C2 block 0 is 40.00s" "$(printf '%s\n' "$OUT2" | grep -c 'BLOCK production/00000 .*mean= 40.00s')" "1"
chk "C2 block 100 is 60.00s" "$(printf '%s\n' "$OUT2" | grep -c 'BLOCK production/00100 .*mean= 60.00s')" "1"
chk "C2 block 200 is 90.00s" "$(printf '%s\n' "$OUT2" | grep -c 'BLOCK production/00200 .*mean= 90.00s')" "1"
# THE POINT of the block breakdown: the phase mean HIDES the trend. 63.33 looks like a healthy constant rate.
chk "C2 the phase mean (63.33s) would have concealed a 40->90s rise" \
    "$(printf '%s\n' "$OUT2" | grep -c 'PHASE production .*mean= 63.33s')" "1"

# --- CASE 3: a RESUME must be attributed to production, not left as pre-warmup -------------------------
{
  echo "[spot-driver] resume PRODUCTION at iter 280 (interval=40)"
  for i in $(seq 1 10); do echo "Iteration took 66.0s."; done
} > "$TD/resume.log"
OUT3=$(awk -f "$PROG" "$TD/resume.log" | sort)
chk "C3 a resumed leg's iterations count as production" \
    "$(printf '%s\n' "$OUT3" | grep -c 'PHASE production .*n=10')" "1"
chk "C3 nothing is misfiled as pre-warmup" "$(printf '%s\n' "$OUT3" | grep -c 'pre-warmup')" "0"

# --- CASE 4: timing lines before any phase transition are labelled, not silently dropped ---------------
printf 'Iteration took 12.0s.\nIteration took 12.0s.\n' > "$TD/pre.log"
chk "C4 pre-transition timings are reported as pre-warmup rather than vanishing" \
    "$(awk -f "$PROG" "$TD/pre.log" | grep -c 'PHASE pre-warmup .*n=2')" "1"

# --- CASE 5: a log with no timing lines says so, instead of printing nothing ---------------------------
printf '[spot-driver] WARMUP from iter 0 -> 400\nsome other line\n' > "$TD/none.log"
chk "C5 a log with no timing lines is reported explicitly (silence would read as 'fine')" \
    "$(awk -f "$PROG" "$TD/none.log" | grep -c 'no "took Ns" timing lines')" "1"

# --- CASE 6: the value is matched by NAME, not by field position ---------------------------------------
# openmmtools has changed this line's surrounding text between versions; a positional $N would read the wrong
# token and report a confident wrong number. Prefixing the line must not change the parsed value.
printf '[spot-driver] PRODUCTION created from warmup\n2026-07-26 08:00:00 INFO mpiplus: Iteration took 66.0s.\n' > "$TD/prefixed.log"
chk "C6 a differently-prefixed timing line still parses to 66.00s" \
    "$(awk -f "$PROG" "$TD/prefixed.log" | grep -c 'PHASE production .*mean= 66.00s')" "1"

# --- CASE 7: THE BUFFERING LAG, reproduced from the real log ------------------------------------------
# rbfe_spot_driver logged via bare `print`, block-buffered into the `| tee` pipe, while openmmtools' per-iteration
# lines go through `logging` and flush per record. On the live rev leg (GH run 30202433547) the result was 448
# timing lines before the first driver phase marker ever appeared, and no production marker at all -- while GCS
# held production at 320/2000. So the profile split at 448 and labelled 320 production iterations "warmup".
# The driver default is fixed, but logs already written still carry it, so the profile must SAY SO rather than
# present the artifact as a phase boundary.
{
  for i in $(seq 1 448); do echo "Iteration took 46.5s."; done
  echo "[spot-driver] WARMUP from iter 200 -> 800 (interval=8)"
  for i in $(seq 1 490); do echo "Iteration took 56.5s."; done
} > "$TD/lag.log"
OUT7=$(awk -f "$PROG" "$TD/lag.log" | sort)
chk "C7 the buffering lag is called out, not presented as a pre-phase" \
    "$(printf '%s\n' "$OUT7" | grep -c 'WARNING buffering-lag: 448 timing lines')" "1"
chk "C7 a missing production marker is called out too" \
    "$(printf '%s\n' "$OUT7" | grep -c 'WARNING no production marker')" "1"
# The SEGMENT lines are the trustworthy view: phase-free ordinal blocks that show the drift regardless of labels.
chk "C7 SEGMENT blocks span the whole log independently of phase labels" \
    "$(printf '%s\n' "$OUT7" | grep -c '^SEGMENT')" "10"
chk "C7 SEGMENT shows the early cost (46.50s)" \
    "$(printf '%s\n' "$OUT7" | grep -c 'SEGMENT iters 00000-00099 .*mean= 46.50s')" "1"
chk "C7 SEGMENT shows the later cost (56.50s)" \
    "$(printf '%s\n' "$OUT7" | grep -c 'SEGMENT iters 00800-00899 .*mean= 56.50s')" "1"
# and a clean log must NOT cry wolf
chk "C7 a clean log (marker first) raises NO buffering warning" \
    "$(awk -f "$PROG" "$TD/const.log" | grep -c 'WARNING buffering-lag')" "0"
chk "C7 a log WITH a production marker raises no missing-production warning" \
    "$(awk -f "$PROG" "$TD/const.log" | grep -c 'WARNING no production marker')" "0"

# --- the driver default must be a FLUSHING log, or every future log has the same artifact ---------------
chk "rbfe_spot_driver defaults log to the flushing wrapper, not bare print" \
    "$(grep -c 'log=_flushing_log' rbfe_spot_driver.py)" "1"
chk "no bare 'log=print' default remains" \
    "$(grep -c 'log=print' rbfe_spot_driver.py)" "0"
chk "the flushing wrapper actually sets flush" \
    "$(grep -c 'kwargs.setdefault("flush", True)' rbfe_spot_driver.py)" "1"

if [ "$fail" = 0 ]; then echo; echo "ALL CHECKS PASS"; else echo; echo "SOME CHECKS FAILED"; fi
exit "$fail"
