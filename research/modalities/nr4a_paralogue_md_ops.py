#!/usr/bin/env python3
"""CI-side operations for the LANE-13 paralogue MD ensembles: status, reap, collect, stop.

WHY THE STATUS BOARD IS A PROGRESS CHECK, NOT A LIVENESS PING. A rented Vast box can sit up with a dead
container or an idle GPU and look perfectly healthy — that failure mode has bitten this repo three times on the
ternary lane. So `status` reports, per leg, the PHASE marker, its AGE, and the tail of the host log, and it
reports the biased-ns counter the job writes, so two consecutive polls can be compared for ADVANCE. An instance
being up is never reported as progress.

WHY THE REAP LIVES HERE AND NOT ON THE HOST. `VAST_API_KEY` is never forwarded to a community host (it can
spend the account's credit). The host stops its own GPU billing key-free by exiting its container; only CI,
which holds the key, can DESTROY the exited instance. So teardown is two-layer by design and this is the
control-plane half.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time


class Tee:
    """Write to two streams at once, so a watch tick both STREAMS to the CI log and is captured for the
    published board. (A board that only existed in a buffer would go dark exactly when the run hangs.)"""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self.streams:
            try:
                st.flush()
            except Exception:  # noqa: BLE001
                pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import _vast_request  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LABEL_PREFIX = "nr4a-pdyn"
RESULT_PREFIX = os.environ.get("PDYN_RESULT_PREFIX", "nr4a-paralogue-ensemble")
DEFAULT_BUCKET = "sagemaker-us-east-2-646605541856"
# Anti-idle backstop. A leg that has been up this long without a result is destroyed regardless of what it
# claims to be doing: 60 ns metad + 3 x 5 ns release is ~5-6 h on a 4090 and ~11-12 h on a 3090, so 14 h is
# comfortably past any legitimate single-host run and a preempted leg resumes from its checkpoint anyway.
# RAISED 14 -> 26 h once the NR4A2 leg landed on an RTX 3090. The $/ns ranking is right to take it (3090 at
# $0.0451/hr is $0.0030/ns against $0.0043/ns for the $0.136/hr 4090), but the card is 2.10x slower, so 75 ns
# of MD is ~16 h rather than ~8 h and a 14 h backstop would have destroyed a perfectly healthy leg mid-release.
# The real anti-idle guarantee is not this number: it is the onstart EXIT trap, which exits the container the
# moment the pipeline finishes or dies. This backstop only catches a HUNG container, and at $0.045-0.14/hr its
# worst case is about a dollar.
BACKSTOP_H = float(os.environ.get("PDYN_BACKSTOP_H", "26"))


def bucket():
    return os.environ.get("VAST_CKPT_BUCKET") or DEFAULT_BUCKET


def leg_names(targets):
    """Both the real and the smoke leg name for each target.

    The launcher names a smoke leg `nr4a-pdyn-nr4a1-smoke` and gives it its own S3 prefix, so a board that
    only knew the real name reported "no phase yet, no run.log yet" for a leg that was demonstrably running at
    60 % GPU — a monitoring check that measures nothing, which is the exact failure class this repo keeps
    paying for. Listing both is harmless: a prefix with nothing under it just reports absent."""
    out = []
    for t in targets.split(","):
        t = t.strip().lower()
        if t:
            out += [f"{LABEL_PREFIX}-{t}", f"{LABEL_PREFIX}-{t}-smoke"]
    return out


def target_of(name):
    """`nr4a-pdyn-nr4a1` / `nr4a-pdyn-nr4a1-smoke` -> `nr4a1`. A bare rsplit('-') returns 'smoke' for the
    second form and would look for a tarball that never exists."""
    parts = name.split("-")
    for p in reversed(parts):
        if p.startswith("nr4a") and p != "nr4a":
            return p
    return parts[-1]


def _s3():
    import boto3
    return boto3.client("s3")


def _get(s3, key):
    try:
        return s3.get_object(Bucket=bucket(), Key=key)["Body"].read().decode(errors="replace")
    except Exception:  # noqa: BLE001
        return None


def _exists(s3, key):
    try:
        s3.head_object(Bucket=bucket(), Key=key)
        return True
    except Exception:  # noqa: BLE001
        return False


def instances():
    key = os.environ.get("VAST_API_KEY")
    if not key:
        print("[ops] no VAST_API_KEY — instance half of the board skipped")
        return []
    try:
        insts = _vast_request("GET", "/instances/", key).get("instances", [])
    except Exception as e:  # noqa: BLE001
        print(f"[ops] instance list FAILED ({e}) — refusing to act on instances this pass")
        return None
    return [i for i in insts if (i.get("label") or "").startswith(LABEL_PREFIX)]


def result_key(name):
    return f"{RESULT_PREFIX}/{name}/{target_of(name)}-pocket-ensemble.tar.gz"


def status(targets):
    s3 = _s3()
    print(f"[ops] bucket={bucket()} prefix={RESULT_PREFIX}")
    for name in leg_names(targets):
        base = f"{RESULT_PREFIX}/{name}"
        print(f"\n=== {name}")
        done = _exists(s3, result_key(name))
        print(f"  deliverable in S3: {'YES' if done else 'no'}")
        ph = _get(s3, f"{base}/phase.json")
        if ph:
            try:
                d = json.loads(ph)
                age = None
                try:
                    age = (time.time() - time.mktime(time.strptime(d["utc"], "%Y-%m-%dT%H:%M:%SZ"))
                           + time.timezone) / 60.0
                except Exception:  # noqa: BLE001
                    pass
                print(f"  phase: {d.get('phase')} {d.get('extra')}  "
                      f"(written {d.get('utc')}, {f'{age:.0f} min ago' if age is not None else 'age unknown'})")
            except Exception:  # noqa: BLE001
                print(f"  phase: (unparseable) {ph[:200]}")
        else:
            print("  phase: (none yet)")
        log = _get(s3, f"{base}/run.log")
        if log:
            lines = [ln for ln in log.strip().splitlines() if ln.strip()][-15:]
            for ln in lines:
                print(f"    | {ln[:170]}")
        else:
            print("    | (no run.log yet)")
    insts = instances()
    print("\n=== Vast instances")
    if insts is None:
        return 0
    if not insts:
        print("  (none up)")
    for i in insts:
        up_h = (time.time() - float(i.get("start_date") or time.time())) / 3600.0
        print(f"  {i.get('id')} {i.get('label')} intended={i.get('intended_status')} "
              f"actual={i.get('actual_status')} gpu={i.get('gpu_name')} "
              f"dph={i.get('dph_total')} up={up_h:.2f} h "
              f"gpu_util={i.get('gpu_util')} status_msg={str(i.get('status_msg'))[:80]}")
    return 0


def nudge_start(insts):
    """Re-issue `state=running` for any instance Vast left at intended=stopped.

    Creating an ask does NOT reliably launch the container: the start PUT races Vast finishing the create, and
    on some hosts it is lost, leaving the box `intended=stopped` forever. `VastBackend._ensure_running` retries
    for ~50 s at submit time, which is not long enough when the host is still PULLING a multi-GB image — the
    launcher warned exactly that for the NR4A2 leg. This is the same idempotent PUT, retried from the watch
    for as long as the leg matters.

    Deliberately distinct from a CAPACITY REFUSAL: a start answered `{"success": false,
    "error": "resources_unavailable"}` means that host's GPU is taken and the answer is destroy + exclude +
    pick another host, never retry. That is reported here so the two are never confused."""
    key = os.environ.get("VAST_API_KEY")
    if not key:
        return
    for i in insts or []:
        if i.get("intended_status") == "running":
            continue
        if i.get("actual_status") in ("exited",):
            continue
        try:
            r = _vast_request("PUT", f"/instances/{i.get('id')}/", key, body={"state": "running"})
            if isinstance(r, dict) and r.get("success") is False:
                print(f"::warning title=LANE13 START REFUSED::{i.get('id')} {i.get('label')} "
                      f"{r.get('error')}: {r.get('msg')} — if this is resources_unavailable, DESTROY the "
                      f"instance, add machine {i.get('machine_id')} to exclude_machines and relaunch; "
                      f"do NOT wait and do NOT raise the bid")
            else:
                print(f"[ops] nudged start on {i.get('id')} {i.get('label')} "
                      f"(intended={i.get('intended_status')} actual={i.get('actual_status')})")
        except Exception as e:  # noqa: BLE001
            print(f"[ops] start nudge {i.get('id')} failed: {e}")


def reap(targets, force=False):
    """Destroy instances whose deliverable is already in S3, whose state is terminal, or which are past the
    anti-idle backstop. Refuses to act if the instance list could not be read."""
    insts = instances()
    if insts is None:
        return 1
    key = os.environ.get("VAST_API_KEY")
    s3 = _s3()
    done_names = {n for n in leg_names(targets) if _exists(s3, result_key(n))}
    for i in insts:
        label = i.get("label") or ""
        iid = i.get("id")
        up_h = (time.time() - float(i.get("start_date") or time.time())) / 3600.0
        actual = i.get("actual_status")
        why = None
        if force:
            why = "force"
        elif label in done_names:
            why = "deliverable already in S3"
        elif actual in ("exited", "stopped") and up_h > 0.25:
            why = f"terminal state {actual}"
        elif up_h > BACKSTOP_H:
            why = f"past the {BACKSTOP_H:.0f} h anti-idle backstop"
        if not why:
            print(f"[ops] keep {iid} {label} (actual={actual}, up {up_h:.2f} h)")
            continue
        print(f"[ops] DESTROY {iid} {label}: {why}")
        try:
            _vast_request("DELETE", f"/instances/{iid}/", key)
        except Exception as e:  # noqa: BLE001
            print(f"[ops]   destroy {iid} failed: {e}")
    return 0


def collect(targets):
    """Pull each finished ensemble tarball and unpack it into results/nr4a{1,2}-pocket-ensemble/, which is the
    layout nr4a_paralogue_dynamics.py reads and the same one the committed NR4A3 ensemble uses."""
    s3 = _s3()
    got = []
    for name in leg_names(targets):
        # ⚠ NEVER unpack a smoke leg. Its tarball has the SAME basename as the real one and unpacks to the
        # SAME results/<target>-pocket-ensemble directory, so collecting it would quietly mix 12 frames from
        # a 0.4 ns metadynamics run into the ensemble the categorical verdict is computed on — a silently
        # wrong answer with nothing to notice it. The smoke exists to prove plumbing and is discarded.
        if name.endswith("-smoke"):
            if _exists(s3, result_key(name)):
                print(f"[ops] {name}: SKIPPED — smoke output is never collected (toy lengths)")
            continue
        target = target_of(name)
        k = result_key(name)
        if not _exists(s3, k):
            print(f"[ops] {name}: no deliverable yet at s3://{bucket()}/{k}")
            continue
        dest = os.path.join(REPO, "results", f"{target}-pocket-ensemble")
        os.makedirs(dest, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            tgz = os.path.join(td, "e.tar.gz")
            subprocess.run(["aws", "s3", "cp", f"s3://{bucket()}/{k}", tgz, "--only-show-errors"], check=True)
            with tarfile.open(tgz) as tf:
                # the tarball holds frames/<ensemble>/fp_*/frame.pdb + release_summary.json
                tf.extractall(td)
            src = os.path.join(td, "frames")
            n = 0
            for ens in sorted(os.listdir(src)) if os.path.isdir(src) else []:
                sd = os.path.join(src, ens)
                dd = os.path.join(dest, ens)
                os.makedirs(dd, exist_ok=True)
                for fr in sorted(os.listdir(sd)):
                    os.makedirs(os.path.join(dd, fr), exist_ok=True)
                    fp = os.path.join(sd, fr, "frame.pdb")
                    if os.path.exists(fp):
                        with open(fp, "rb") as a, open(os.path.join(dd, fr, "frame.pdb"), "wb") as b:
                            b.write(a.read())
                        n += 1
            rs = os.path.join(td, "release_summary.json")
            if os.path.exists(rs):
                with open(rs) as a, open(os.path.join(dest, "release_summary.json"), "w") as b:
                    b.write(a.read())
            print(f"[ops] {name}: unpacked {n} frame PDBs into {os.path.relpath(dest, REPO)}")
            got.append({"target": target, "n_frames": n})
    print(json.dumps({"collected": got}, indent=1))
    return 0


def _progress_signature(targets):
    """A tuple that MUST change while the science is advancing: per leg, the phase name and the biased-ns the
    job reports with it. Deliberately NOT 'is an instance up' — a rented box can sit with a dead container or
    an idle GPU and look perfectly healthy, which is the failure class this repo keeps paying for."""
    s3 = _s3()
    sig = {}
    for name in leg_names(targets):
        ph = _get(s3, f"{RESULT_PREFIX}/{name}/phase.json")
        try:
            d = json.loads(ph) if ph else {}
        except Exception:  # noqa: BLE001
            d = {}
        extra = d.get("extra") or {}
        # DELIBERATELY NOT the marker's timestamp. The host publishes a heartbeat every 2 min, so a
        # signature containing `utc` would change on every tick whether or not the science advanced —
        # a stall detector that can never fire, which is worse than none. Phase + ns + deliverable only.
        sig[name] = (d.get("phase"), extra.get("done_ns") if isinstance(extra, dict) else None,
                     _exists(s3, result_key(name)))
    return sig


WATCH_BRANCH = os.environ.get("PDYN_WATCH_BRANCH", "lane13-watch")


def publish_board(text, branch=WATCH_BRANCH):
    """Force-push the current board to a one-commit cache branch so it is READABLE WHILE THE RUN IS STILL
    GOING.

    GitHub's job-logs API returns 404 for an in-progress job and annotations are capped per step, so a
    long-running watch job is otherwise a black box for exactly as long as it matters — which would make the
    repo's "tight monitoring of an unproven pipeline" rule unenforceable from outside CI. A cache branch is the
    pattern this repo already uses for CI outputs (`modalities-cache`), and one orphan commit per tick keeps it
    from growing. Best-effort: a failed publish never interrupts the watch."""
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "trimcrae/Rare-cancers")
    if not tok:
        return
    d = tempfile.mkdtemp(prefix="pdynboard")
    try:
        with open(os.path.join(d, "board.md"), "w") as fh:
            fh.write(text)
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        for cmd in (["git", "init", "-q", "-b", branch],
                    ["git", "config", "user.name", "Claude"],
                    ["git", "config", "user.email", "noreply@anthropic.com"],
                    ["git", "add", "board.md"],
                    ["git", "commit", "-q", "-m", f"lane13 watch board {time.strftime('%FT%TZ', time.gmtime())}"],
                    ["git", "push", "-q", "--force",
                     f"https://x-access-token:{tok}@github.com/{repo}", f"{branch}:{branch}"]):
            r = subprocess.run(cmd, cwd=d, env=env, capture_output=True)
            if r.returncode:
                print(f"[watch] board publish step {cmd[1]} failed: {r.stderr.decode()[:200]}")
                return
    finally:
        subprocess.run(["rm", "-rf", d])


def watch(targets, interval_s=180, max_minutes=330, stall_ticks=8):
    """ONE CI run that monitors the legs continuously, so monitoring survives this session dying.

    Every `interval_s` it prints a full progress board and compares the progress signature with the previous
    tick. Finished legs are reaped (their host has already stopped its own GPU billing; this destroys the
    exited instance). The loop exits when every leg's deliverable is in S3. `stall_ticks` consecutive ticks
    with NO change to a running leg's signature is reported as a STALL and fails the job, because a relaunch
    would hang the same way — an alert is the correct action, not a retry."""
    t_end = time.time() + max_minutes * 60
    prev, frozen = None, {}
    tick = 0
    while time.time() < t_end:
        tick += 1
        head = (f"\n########## tick {tick}  {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
                f"##########")
        print(head, flush=True)
        buf = io.StringIO()
        # capture the WHOLE tick — status, the start nudge and the reap — because the board is the only
        # thing readable while the run is in progress, and "did the nudge fire?" is exactly the question
        # a stuck intended=stopped leg raises.
        with contextlib.redirect_stdout(Tee(sys.stdout, buf)):
            status(targets)
            insts = instances()
            nudge_start(insts)
            reap(targets)
        sig = _progress_signature(targets)
        one_line = " | ".join(f"{n}: phase={v[0]} ns={v[1]} done={v[-1]}" for n, v in sig.items())
        print(f"::notice title=LANE13 TICK {tick}::{one_line}", flush=True)
        publish_board(f"# LANE 13 watch board\n\n`{head.strip('# ')}`\n\n**{one_line}**\n\n```\n"
                      + buf.getvalue()[-40000:] + "\n```\n")
        for name, v in sig.items():
            if v[-1]:
                frozen[name] = 0
                continue
            if prev and prev.get(name) == v:
                frozen[name] = frozen.get(name, 0) + 1
                print(f"::warning title=LANE13 NO PROGRESS::{name} unchanged for "
                      f"{frozen[name]} tick(s): {v}")
            else:
                frozen[name] = 0
        prev = sig
        if all(v[-1] for v in sig.values()):
            print("::notice title=LANE13 ALL LEGS DONE::every deliverable is in S3")
            return 0
        stalled = [n for n, c in frozen.items() if c >= stall_ticks]
        if stalled:
            print(f"::error title=LANE13 STALL::{stalled} made no progress for {stall_ticks} ticks "
                  f"({stall_ticks * interval_s / 60:.0f} min) — diagnose, do not relaunch blindly")
            return 2
        time.sleep(interval_s)
    print("::warning title=LANE13 WATCH WINDOW ENDED::re-fire task=watch to keep monitoring")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["status", "reap", "collect", "stop", "watch"])
    ap.add_argument("--targets", default="NR4A1,NR4A2")
    ap.add_argument("--interval-s", type=int, default=180)
    ap.add_argument("--max-minutes", type=int, default=330)
    a = ap.parse_args()
    if a.action == "status":
        return status(a.targets)
    if a.action == "watch":
        return watch(a.targets, interval_s=a.interval_s, max_minutes=a.max_minutes)
    if a.action == "reap":
        return reap(a.targets)
    if a.action == "stop":
        return reap(a.targets, force=True)
    return collect(a.targets)


if __name__ == "__main__":
    raise SystemExit(main())
