#!/usr/bin/env python3
"""Run a command and report its PEAK RESIDENT SET — sampled, so a child that is KILLED still yields a number.

⚠ WHY NOT `/usr/bin/time -v`. It is not in `triskit23/ternary-fep` (measured 2026-07-27; the step that tried
it printed `bash: /usr/bin/time: No such file or directory` for both arms and measured nothing), and adding it
would mean re-baking the image for a diagnostic. More importantly `time` reports at EXIT, and the whole point
of this measurement is a process that may not get to exit: an OOM kill is a SIGKILL, and a reporter that only
speaks at the end says nothing about the run that was killed.

⚠ AND WHY NOT `resource.getrusage` IN THE CHILD, for the same reason — a SIGKILLed process runs no atexit
handler. So this samples `/proc/<pid>/status: VmHWM` (the kernel's own high-water mark) from the PARENT and
PRINTS EVERY NEW HIGH-WATER MARK AS IT HAPPENS. Even a hard kill therefore leaves the last observed peak in
the log, which is exactly the datum the diagnosis turns on. `/sys/fs/cgroup/memory.peak` is read too where it
exists (cgroup v2): it counts page cache and kernel memory against the same limit the OOM killer enforces,
so it — not RSS — is the number a container limit is actually compared against.

Pure stdlib. Exit code is the child's; 137 is a SIGKILL, which under a memory limit is the OOM killer.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

SAMPLE_S = float(os.environ.get("PEAK_RSS_SAMPLE_S") or "0.2")


def _read_kb(pid):
    """VmHWM in kB from /proc/<pid>/status, or None if the process is gone. PURE-ish (one read)."""
    try:
        with open(f"/proc/{pid}/status") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return None


def _cgroup_peak_bytes():
    """cgroup v2's own peak, which is what a container memory limit is enforced against. None if absent."""
    for p in ("/sys/fs/cgroup/memory.peak", "/sys/fs/cgroup/memory/memory.max_usage_in_bytes"):
        try:
            with open(p) as fh:
                return int(fh.read().strip())
        except (OSError, ValueError):
            continue
    return None


def _cgroup_limit_bytes():
    """The limit the OOM killer enforces, or None when there isn't one.

    ⚠ "NO LIMIT" HAS TWO SPELLINGS AND ONE OF THEM IS A NUMBER. cgroup v2 writes the literal `max`; cgroup v1
    writes `9223372036854771712`, which parses fine and then renders as "8589934592.00 GiB" — a limit no
    reader would believe and every reader would have to stop and work out. Anything past a petabyte is the
    sentinel, not a limit.
    """
    for p in ("/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        try:
            with open(p) as fh:
                v = fh.read().strip()
            if v == "max":
                return None
            n = int(v)
            return None if n > 2 ** 50 else n
        except (OSError, ValueError):
            continue
    return None


def run(cmd):
    """Run `cmd`, printing each new peak as it is reached. Returns (rc, peak_kb, cgroup_peak_bytes)."""
    lim = _cgroup_limit_bytes()
    print(f"[peak-rss] cgroup limit: {'none' if lim is None else '%.2f GiB' % (lim / 2**30)}", flush=True)
    proc = subprocess.Popen(cmd)
    peak = 0
    t0 = time.time()
    while proc.poll() is None:
        kb = _read_kb(proc.pid)
        if kb and kb > peak:
            peak = kb
            cg = _cgroup_peak_bytes()
            print(f"[peak-rss] t={time.time() - t0:7.1f}s  VmHWM={peak / 2**20:7.2f} GiB"
                  + (f"  cgroup_peak={cg / 2**30:7.2f} GiB" if cg else ""), flush=True)
        time.sleep(SAMPLE_S)
    rc = proc.returncode
    cg = _cgroup_peak_bytes()
    # ★ THE VERDICT LINE, and it names the signal. A negative returncode is a signal; -9/137 is SIGKILL, and a
    # SIGKILL that nobody sent is the OOM killer. Saying so here is what stops the next reader inferring it.
    sig = -rc if rc is not None and rc < 0 else (rc - 128 if rc and rc > 128 else None)
    print(f"[peak-rss] EXIT rc={rc}"
          + (f" (signal {sig}{' = SIGKILL — under a memory limit that is the OOM killer' if sig == 9 else ''})"
             if sig else "")
          + f"  peak VmHWM={peak / 2**20:.2f} GiB"
          + (f"  cgroup_peak={cg / 2**30:.2f} GiB" if cg else "")
          + (f"  of limit {lim / 2**30:.2f} GiB" if lim else ""), flush=True)
    return rc, peak, cg


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: peak_rss.py <cmd> [args...]")
    raise SystemExit(run(sys.argv[1:])[0] or 0)
