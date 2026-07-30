#!/usr/bin/env python3
# =============================================================================================================
# WHY THE TERNARY REPLICATE LEGS COMMIT NOTHING — read from the CONTAINER'S OWN OUTPUT, not from exit status
# =============================================================================================================
# THE OBSERVATION THIS EXISTS TO EXPLAIN (measured 2026-07-27, three consecutive cohorts of RUNG 2b's
# valB_mini replicates). Every cohort rents four hosts for four units. Every cohort, the two BINARY legs
# advance normally and the two TERNARY legs commit ABSOLUTELY NOTHING — not a slow first checkpoint, zero:
#
#   cohort 3, `task=collect` 6:17 PM ET
#     ternary_vhl_r1  46040507  exited   committed=none/0        phase md-running, log froze 3 min in
#     binary_vhl_r1   46040514  running  committed=warmup/832    6.0 s/iter, committing every 64 iterations
#     ternary_vhl_r2  46040577  exited   committed=none/0        phase md-running, log froze 2 min in
#     binary_vhl_r2   46040659  exited   committed=warmup/256    committed, then lost its host
#
# Three cohorts of the same asymmetry is a PATTERN, not spot churn — preemption does not preferentially kill
# one leg type six times out of six. And it is not cosmetic: `ternary_fep_reduce.per_replicate_ddg_coop`
# forms ΔΔG_coop over `set(ternary) & set(binary)`, so while the ternary side never commits, n_paired stays 1
# and `calibration_gate` returns INDETERMINATE no matter how well the binary legs run. Every dollar spent on
# binary-only replicates buys nothing.
#
# ⛔ WHY NOT THE EXIT STATUS, AND WHY NOT S3 (CLAUDE.md §4 — a plausible story is a HYPOTHESIS, not a
# diagnosis). The on-host log reaches S3 through a `while true; sleep 120` copy loop in the onstart script.
# So the last TWO MINUTES of output — which for a leg that dies is the entire interesting part, including
# whatever the kernel or the runtime said on the way out — is exactly the part S3 never receives. The
# instance's `actual_status` says `exited`; it cannot say why, and the three candidate mechanisms
# (an out-of-memory kill on the ~142k-particle system where the binary's ~94k fits; a missing or mis-keyed
# stage-cache entry; a host reclaim that the ternary leg loses because it takes longer to reach its first
# checkpoint) all produce the same `exited`.
#
# So this reads the two sources that CAN discriminate:
#
#   1. `request_logs` — the container's console, straight from the provider, including the part S3 never got.
#      Vast's flow is PUT-then-poll-a-URL; that path is already implemented and reviewed in
#      `nrv04_vast_launch._vast_instance_logs`, so it is IMPORTED here rather than re-typed (CLAUDE.md §1).
#   2. The `attempts/` archive in S3. The onstart script copies the previous attempt's `run.log` aside before
#      truncating it, so every cohort's failure is still on disk under `legs/<uid>/attempts/`. Reading the
#      LAST LINE of every attempt for every unit turns "it failed three times" into "it failed three times AT
#      THE SAME LINE", which is the difference between a deterministic defect and bad luck — and it costs $0.
#
# Plus the host spec each unit actually landed on (RAM/disk/GPU), because if the ternary legs are being
# refused by hosts the binary legs clear, that is a SPEC problem — `resource_spec` asking for too little —
# and no number of retries fixes it.
#
# $0: reads only. It never rents, never destroys, never nudges.
# =============================================================================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ternary_vast_launch as tv  # noqa: E402

# The tail of an attempt log that is worth printing. Long enough to carry a Python traceback with its frames,
# short enough that four units x several attempts still fits inside a job log GitHub truncates from the tail.
ATTEMPT_TAIL_LINES = int(os.environ.get("TVAST_DIAG_TAIL") or "25")

# Fields of the instance record this may print. ALLOW-LIST, for the same reason
# `ternary_vast_launch.rented_rate_row`'s is: the record carries `jupyter_token`, `ssh_host` and
# `public_ipaddr`, and a diagnostic's output gets pasted into issues and commit messages. The four capacity
# fields are the point of the exercise — they are what answers "did the ternary leg land somewhere smaller".
SAFE_INSTANCE_FIELDS = ("id", "machine_id", "label", "actual_status", "cur_state", "intended_status",
                        "status_msg", "gpu_name", "num_gpus", "gpu_ram", "cpu_ram", "cpu_cores_effective",
                        "disk_space", "disk_util", "mem_usage", "mem_limit", "gpu_util", "dph_total",
                        "start_date", "image_uuid")


def safe_instance(inst):
    """The printable projection of an instance record. PURE."""
    return {k: inst.get(k) for k in SAFE_INSTANCE_FIELDS if k in inst}


def arm_of(unit_id):
    """`ternary` / `binary` / `solvent` / None. PURE. The whole diagnosis is a comparison BETWEEN ARMS, so
    the grouping key has to come from the unit id rather than from a hand-maintained list that can go stale
    the next time a mode is added.

    ★ ONE HOME (CLAUDE.md §1): the split itself is `ternary_vast_launch.arm_of_leg`, which is also what the
    per-arm CHECKPOINT CADENCE keys off. Two implementations of "which arm is this" could disagree, and the
    disagreement would show up as a leg silently given the other arm's interval — so this delegates rather
    than re-deriving. It keeps its own `None`, because a diagnostic that cannot classify a unit should say so
    rather than default it to `binary`.
    """
    for arm in ("ternary", "binary", "solvent"):
        if f"__{arm}_" in unit_id or unit_id.endswith(f"__{arm}"):
            return tv.arm_of_leg(unit_id)
    return None


def last_meaningful_line(text):
    """The last line that is not blank. PURE. This is the whole comparison in one value: if every ternary
    attempt across every cohort ends on the SAME line and the binary attempts do not, the failure is
    deterministic and lives at that line."""
    for ln in reversed((text or "").splitlines()):
        if ln.strip():
            return ln.strip()
    return ""


def attempt_logs(uid, bucket=None, prefix=None):
    """[{key, utc, bytes, last_line, tail}] for every archived attempt of this unit, oldest first, plus the
    CURRENT run.log last. One entry per cohort this unit has been through."""
    b = bucket or tv.DEFAULT_BUCKET
    p = (prefix or tv.RESULT_PREFIX).rstrip("/")
    s3 = tv._s3()
    out = []
    for key in (f"{p}/legs/{uid}/attempts/", None):
        if key is None:
            keys = [f"{p}/legs/{uid}/run.log"]
        else:
            keys = []
            try:
                for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=key):
                    keys += [o["Key"] for o in page.get("Contents", []) if o["Key"].endswith(".log")]
            except Exception as e:  # noqa: BLE001 — a unit with no archive is a legitimate first attempt
                print(f"    (attempts unreadable for {uid}: {type(e).__name__}: {e})")
            keys.sort()
        for k in keys:
            try:
                o = s3.get_object(Bucket=b, Key=k)
                txt = o["Body"].read().decode(errors="replace")
            except Exception:  # noqa: BLE001 — run.log may not exist yet
                continue
            lines = [ln for ln in txt.splitlines() if ln.strip()]
            out.append({"key": k, "utc": o["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "bytes": o["ContentLength"], "n_lines": len(lines),
                        "last_line": last_meaningful_line(txt),
                        "tail": lines[-ATTEMPT_TAIL_LINES:]})
    return out


def console(iid, key=None, tail=600):
    """The container's own console for a still-listed instance, via the reviewed `request_logs` path.

    IMPORTED, NOT RE-IMPLEMENTED (CLAUDE.md §1). `nrv04_vast_launch._vast_instance_logs` already encodes the
    two things that are easy to get wrong here — that the PUT only TRIGGERS collection and returns a URL, and
    that the URL is empty for several seconds afterwards so it must be polled rather than read once.
    """
    from nrv04_vast_launch import _vast_instance_logs
    return _vast_instance_logs(key or os.environ["VAST_API_KEY"], iid, tail=tail)


def diagnose(mode="edge_reps", bucket=None, prefix=None, key=None, want_console=True):
    """The full picture for one mode's units: host spec, S3 phase/commit state, every archived attempt's last
    line, and — for anything still listed — the container's own console.

    Returns the structured record so a caller can commit it; prints the human-readable version, because the
    thing a person actually needs at 3 AM is the two arms' last lines side by side.
    """
    b = bucket or tv.DEFAULT_BUCKET
    p = (prefix or tv.RESULT_PREFIX).rstrip("/")
    key = key or os.environ.get("VAST_API_KEY")
    uids = [tv.build_jobspec(l, s, d, mode=mode).env["UNIT_ID"] for (l, s, d) in tv.units_for(mode)]

    hosts = {"live": {}, "dead": {}}
    try:
        hosts = tv.unit_hosts(uids, key=key)
    except Exception as e:  # noqa: BLE001 — the S3 half of this diagnostic stands on its own
        print(f"[diag] instance list unreadable ({type(e).__name__}: {e}) — S3 evidence only")
    listed = dict(hosts["dead"])
    listed.update(hosts["live"])

    recs = tv.leg_records(b, p)
    doc = {"_what": "why the ternary replicate legs commit nothing, measured from the container's own "
                    "output rather than inferred from exit status (CLAUDE.md §4)",
           "mode": mode, "utc": tv.time.strftime("%Y-%m-%dT%H:%M:%SZ", tv.time.gmtime()), "units": {}}

    for uid in uids:
        arm = arm_of(uid)
        inst = listed.get(uid)
        phase, it, scalar = tv.committed_progress(uid, b, p)
        marker, marker_age, _tail, log_age = tv.phase_and_log(uid, b, p)
        atts = attempt_logs(uid, b, p)
        rec = recs.get(uid) or {}
        # ★ THE BREAKER'S VERDICT AND THE TIMESTAMPS THAT PRODUCE IT (added 2026-07-29). Without this, the
        # diagnostic showed `leg_record_status: failed` + `n_attempts_archived: 51` and left a reader to
        # infer the block — and gave no way at all to see the fact that decides it: whether that record is
        # still the NEWEST thing about the unit. Three units' worth of guessing came out of that gap.
        try:
            import leg_failure_breaker as _lfb
            _s3c = tv._s3()
            _commit_utc = _lfb.newest_commit_utc(_s3c, b, p, uid)
            _evic = _lfb.read_eviction(_s3c, b, p, uid)
            _sup = _lfb.superseding_evidence(rec, newest_commit_utc=_commit_utc, eviction=_evic)
            # `since_utc` = the last commit: the streak, not the lifetime count. The diagnostic must read
            # the SAME number the launcher gates on, or it would explain a block that is not the one taken.
            _brk = _lfb.decide(rec or None,
                               _lfb.count_attempts(_s3c, b, p, uid, since_utc=_commit_utc),
                               superseding=_sup)
            breaker = {"verdict": _brk.get("verdict"), "block": _brk.get("block"),
                       "n_attempts": _brk.get("n_attempts"),
                       "record_utc": rec.get("updated_utc") or rec.get("_s3_last_modified"),
                       "newest_commit_utc": _commit_utc,
                       "eviction": _evic, "superseded_by": _sup}
        except Exception as e:  # noqa: BLE001 — a diagnostic must never crash the board it prints
            breaker = {"error": f"{type(e).__name__}: {e}"}
        u = {"arm": arm, "leg_record_status": rec.get("status"), "breaker": breaker,
             "committed": {"phase": phase, "iteration": it, "scalar": scalar},
             "phase_marker": marker, "phase_marker_age_min": marker_age, "log_age_min": log_age,
             "n_attempts_archived": len(atts),
             "attempts": [{k: a[k] for k in ("key", "utc", "bytes", "n_lines", "last_line")} for a in atts],
             "instance": safe_instance(inst) if inst else None,
             "instance_is_working": bool(inst) and uid in hosts["live"]}

        print("=" * 108)
        print(f"{uid}   arm={arm}")
        if inst:
            print(f"  host {inst.get('id')} machine={inst.get('machine_id')} {inst.get('gpu_name')} "
                  f"actual={inst.get('actual_status')!r} cur={inst.get('cur_state')!r}")
            # ★ THE CAPACITY LINE. If the ternary legs are landing on hosts that cannot hold their system,
            # that is a SPEC problem (`resource_spec` asking for too little RAM/disk) and retries cannot fix
            # it — which is the one candidate mechanism whose remedy is different from all the others.
            print(f"  capacity: cpu_ram={inst.get('cpu_ram')} mem_usage={inst.get('mem_usage')} "
                  f"mem_limit={inst.get('mem_limit')} disk_space={inst.get('disk_space')} "
                  f"disk_util={inst.get('disk_util')} gpu_ram={inst.get('gpu_ram')} "
                  f"cores={inst.get('cpu_cores_effective')}")
            print(f"  status_msg: {str(inst.get('status_msg') or '')[:160]!r}")
        else:
            print("  host: none listed (destroyed, or never rented)")
        print(f"  committed: {phase or 'NOTHING'}/{it}  scalar={scalar}  "
              f"phase_marker={marker!r} ({'%.0f min old' % marker_age if marker_age is not None else 'n/a'})"
              f"  log {'%.1f min old' % log_age if log_age is not None else 'n/a'}")
        print(f"  attempts archived: {len(atts)}")
        print(f"  BREAKER: {breaker.get('verdict') or breaker.get('error')}  block={breaker.get('block')}  "
              f"record={breaker.get('record_utc')}  newest_commit={breaker.get('newest_commit_utc')}  "
              f"evicted={(breaker.get('eviction') or {}).get('utc')}  "
              f"superseded_by={(breaker.get('superseded_by') or {}).get('kind')}")
        for a in atts:
            print(f"    {a['utc']}  {a['bytes']:>8} B  {a['n_lines']:>5} lines  {a['key'].split('/')[-1]}")
            print(f"      LAST: {a['last_line'][:160]}")
        if atts:
            print(f"  --- tail of the newest attempt ({atts[-1]['key'].split('/')[-1]}) ---")
            for ln in atts[-1]["tail"]:
                print(f"    | {ln[:180]}")

        # THE CONSOLE — the only source that carries the last two minutes before the container died, because
        # the S3 sync loop runs on a 120 s timer. Attempted for every LISTED instance, live or exited: Vast
        # keeps serving logs for an instance that has exited but not been destroyed, and that window is
        # exactly the one worth catching.
        if want_console and inst and key:
            try:
                txt = console(inst.get("id"), key=key)
                lines = [ln for ln in txt.splitlines() if ln.strip()]
                u["console_last_line"] = last_meaningful_line(txt)
                u["console_tail"] = lines[-40:]
                print(f"  --- CONTAINER CONSOLE (request_logs, instance {inst.get('id')}) ---")
                for ln in lines[-40:]:
                    print(f"    > {ln[:180]}")
            except Exception as e:  # noqa: BLE001 — a destroyed instance serves no logs; say so, don't crash
                u["console_error"] = f"{type(e).__name__}: {e}"
                print(f"  console unavailable: {type(e).__name__}: {e}")
        doc["units"][uid] = u

    # ---- THE COMPARISON, LAST AND COMPACT. GitHub truncates a job log from the tail, and this is the line
    # anyone reading the run is actually after: what each arm's last words were.
    print("=" * 108)
    print("---- ARM COMPARISON (the diagnosis is the difference between these two blocks) ----")
    for arm in ("ternary", "binary", "solvent"):
        rows = [(u, d) for u, d in doc["units"].items() if d["arm"] == arm]
        if not rows:
            continue
        print(f"  {arm}:")
        for u, d in rows:
            last = (d["attempts"][-1]["last_line"] if d["attempts"] else "(no log at all)")
            print(f"    {u}")
            print(f"      committed={d['committed']['phase']}/{d['committed']['iteration']} "
                  f"attempts={d['n_attempts_archived']} working={d['instance_is_working']}")
            print(f"      last S3 line : {last[:150]}")
            if d.get("console_last_line"):
                print(f"      last CONSOLE : {d['console_last_line'][:150]}")
    print("---- END ARM COMPARISON ----")
    return doc


def watch_memory(mode="edge_reps", minutes=25, every_s=20, bucket=None, prefix=None, key=None):
    """Trace each unit's CONTAINER MEMORY against its limit, through the phase where the ternary legs die.

    ★★ THIS IS THE OBSERVATION THAT DISCRIMINATES, AND IT IS WHY THE STORY ABOVE IS NOT YET A DIAGNOSIS
    (CLAUDE.md §4). What the attempts archive proves is that the ternary legs die DETERMINISTICALLY, at
    `HybridTopologyFactory` construction ("Creating hybrid system / Setting force field terms / Adding forces
    / No CMAPTorsionForce found"), ~2 min into `md-running`, on every host and in every cohort, while the
    matched binary legs sail past the same point. It also proves the death takes the WHOLE CONTAINER and not
    just the Python process: `_vast_onstart` runs the MD under `timeout` with `set +e` and then unconditionally
    walks the deliverable path — `mark md-done`, write `leg.json`, upload `run.log`. A Python process killed on
    its own leaves that record. There is no such record for any ternary replicate, and `phase.txt` is still
    `md-running`, so bash itself never got another instruction. A cgroup-wide kill is what does that.

    What it does NOT prove is WHICH cgroup-wide kill: an out-of-memory kill on the ~142k-particle ternary
    system (the binary's is ~94k, and HTF construction is the most allocation-heavy step in the pipeline) and
    a provider-side stop look identical from outside. The remedies are opposite — the first is a SPEC problem
    that `resource_spec` must fix by asking for more RAM, and no number of retries touches it; the second is
    churn. So: poll `mem_usage` against `mem_limit` across the window in which the leg dies. Memory climbing
    into the limit at the moment the container disappears is an OOM and says so; a container that vanishes at a
    few GB of a 60+ GB limit rules OOM out and sends the search elsewhere.

    $0 and read-only — it polls the same instance list `collect` already polls, and touches nothing.
    """
    import time as _t
    b = bucket or tv.DEFAULT_BUCKET
    p = (prefix or tv.RESULT_PREFIX).rstrip("/")
    key = key or os.environ.get("VAST_API_KEY")
    uids = [tv.build_jobspec(l, s, d, mode=mode).env["UNIT_ID"] for (l, s, d) in tv.units_for(mode)]
    trace = {u: [] for u in uids}
    deadline = _t.monotonic() + minutes * 60
    print(f"[watch] tracing container memory for {len(uids)} unit(s) every {every_s}s for up to {minutes} min")
    print("[watch]   t_et   unit(arm)  status/cur  mem_usage/mem_limit GB  gpu_util  disk_util  phase  log_lines")
    while _t.monotonic() < deadline:
        try:
            hosts = tv.unit_hosts(uids, key=key)
        except Exception as e:  # noqa: BLE001 — a transient provider error must not end the trace
            print(f"[watch] instance list unreadable ({type(e).__name__}: {e}); retrying")
            _t.sleep(every_s)
            continue
        listed = dict(hosts["dead"])
        listed.update(hosts["live"])
        et = _t.strftime("%I:%M:%S %p", _t.localtime(_t.time() - 4 * 3600))  # ET = UTC-4 (EDT), CLAUDE.md §1
        for u in uids:
            i = listed.get(u)
            marker, _ma, _tail, _la = tv.phase_and_log(u, b, p)
            n_lines = None
            try:
                n_lines = len(tv._s3().get_object(Bucket=b, Key=f"{p}/legs/{u}/run.log")["Body"]
                              .read().decode(errors="replace").splitlines())
            except Exception:  # noqa: BLE001 — no log yet
                pass
            row = {"et": et, "utc": _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime()),
                   "listed": i is not None,
                   "actual_status": (i or {}).get("actual_status"), "cur_state": (i or {}).get("cur_state"),
                   "mem_usage_gb": (i or {}).get("mem_usage"), "mem_limit_gb": (i or {}).get("mem_limit"),
                   "gpu_util": (i or {}).get("gpu_util"), "disk_util": (i or {}).get("disk_util"),
                   "phase_marker": marker, "run_log_lines": n_lines}
            trace[u].append(row)
            frac = ""
            try:
                frac = "  (%.0f%% of limit)" % (100.0 * float(row["mem_usage_gb"]) / float(row["mem_limit_gb"]))
            except (TypeError, ValueError, ZeroDivisionError):
                pass
            # `or '?'` is load-bearing: `arm_of` returns None for a unit id it does not recognise, and a
            # TypeError here would end a 35-minute trace at its first poll — losing the measurement in order
            # to complain about a cosmetic label.
            print(f"[watch] {et}  {u.split('__')[-1][:34]:<34} ({(arm_of(u) or '?')[:7]:<7}) "
                  f"{str(row['actual_status']):<9}/{str(row['cur_state']):<8} "
                  f"mem={row['mem_usage_gb']}/{row['mem_limit_gb']}{frac}  gpu={row['gpu_util']}  "
                  f"disk={row['disk_util']}  phase={str(marker)[:22]!r}  log_lines={n_lines}")
        _t.sleep(every_s)

    out = {"_what": "container memory against its limit through the window in which the ternary replicate "
                    "legs die — the observation that separates an OOM kill from a provider-side stop, which "
                    "have opposite remedies (CLAUDE.md §4)",
           "mode": mode, "poll_every_s": every_s, "minutes": minutes, "trace": trace, "peak": {}}
    print("---- PEAK CONTAINER MEMORY PER UNIT (the discriminator) ----")
    for u in uids:
        seen = [r for r in trace[u] if isinstance(r.get("mem_usage_gb"), (int, float))]
        peak = max((r["mem_usage_gb"] for r in seen), default=None)
        lim = next((r["mem_limit_gb"] for r in reversed(seen)
                    if isinstance(r.get("mem_limit_gb"), (int, float))), None)
        pct = (100.0 * peak / lim) if (peak is not None and lim) else None
        out["peak"][u] = {"arm": arm_of(u), "peak_mem_usage_gb": peak, "mem_limit_gb": lim,
                          "pct_of_limit": None if pct is None else round(pct, 1),
                          "n_polls_with_a_reading": len(seen)}
        print(f"  {arm_of(u):<8} {u}")
        print(f"      peak {peak} GB of limit {lim} GB"
              + ("" if pct is None else f" = {pct:.1f}%") + f"  ({len(seen)} poll(s) with a reading)")
    print("---- END PEAK CONTAINER MEMORY ----")
    return out


def fetch_stage(dest, mode="edge_reps", seed=1, legs=("calib_hi_to_lo__ternary_vhl",)):
    """Unpack each arm's staged tree from THE SAME cache key the rented hosts read, into `dest`.

    ⚠ THE SAME KEY, NOT A FRESH STAGE. The controlled reproduction is only worth running if it starts from the
    identical structures the legs died on; re-staging locally would build a different SMARCA2 homology model
    and measure a different system. `stage_cache_key` is the one home for that key (it is `build_jobspec`'s
    own `STAGE_CACHE`), so this cannot drift from what the host fetches.
    """
    import hashlib
    import io
    import tarfile
    os.makedirs(dest, exist_ok=True)
    got = {}
    for leg in legs:
        uri = tv.stage_cache_key(leg, mode, seed=seed)
        b, k = uri[len("s3://"):].split("/", 1)
        body = tv._s3().get_object(Bucket=b, Key=k)["Body"].read()
        tarfile.open(fileobj=io.BytesIO(body)).extractall(dest)
        inner = os.path.join(dest, leg)
        # ★ A HASH, NOT JUST A SIZE. The first census reported all three seeds' tars at exactly 1402880 B with
        # identical atom, chain and residue counts — which is consistent with "the same structure" and equally
        # consistent with "three different structures of the same topology", because tar pads to 512 B blocks
        # and an atom count says nothing about coordinates. Those two readings support opposite conclusions
        # about whether the staged input can be the cause, so the difference has to be measured rather than
        # inferred from a coincidence of sizes.
        got[leg] = {"uri": uri, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()[:16],
                    "files": sorted(os.listdir(inner)) if os.path.isdir(inner) else []}
        print(f"[rss] staged {leg} seed {seed} from {uri} ({len(body)} B): {got[leg]['files']}", flush=True)
    return got


def pdb_census(path):
    """Atom/chain/residue census of a PDB. PURE, pure-stdlib — no gemmi, no rdkit, so it runs anywhere.

    Column positions are the PDB fixed-format standard: chain id at 21, residue name 17:20, residue seq 22:26.
    """
    n_atom = n_het = 0
    chains, residues, resnames = {}, set(), {}
    try:
        with open(path, errors="replace") as fh:
            for line in fh:
                if not line.startswith(("ATOM", "HETATM")):
                    continue
                n_atom += 1
                n_het += line.startswith("HETATM")
                ch = line[21:22]
                chains[ch] = chains.get(ch, 0) + 1
                rn = line[17:20].strip()
                residues.add((ch, line[22:27]))
                if line.startswith("HETATM"):
                    resnames[rn] = resnames.get(rn, 0) + 1
    except OSError as e:
        return {"error": str(e)}
    return {"atoms": n_atom, "hetatms": n_het, "chains": dict(sorted(chains.items())),
            "n_chains": len(chains), "n_residues": len(residues),
            "het_resnames": dict(sorted(resnames.items(), key=lambda kv: -kv[1])[:12])}


def compare_stage(mode="edge_reps", leg="calib_hi_to_lo__ternary_vhl", seeds=(0, 1, 2), workdir="/tmp/cmpstage"):
    """Structural diff of ONE leg's staged inputs ACROSS SEEDS — the follow-on question to the setup matrix.

    ★ WHY THIS IS THE RIGHT NEXT MEASUREMENT IF SEED 0 PASSES WHERE SEEDS 1 AND 2 DIE. That result would say
    the ternary system is not too big for the memory it gets — the same system ran to completion at seed 0 —
    and would move the whole question onto what `reps-prime` actually built for the other two. `ternary_pdb_stage`
    takes `starting_model_index = seed % n_models` with n_models=2, so seed 1 is a DIFFERENT relaxed SMARCA2
    model and seed 2 is nominally the SAME model as seed 0. If seed 2's tree differs from seed 0's, the seed
    keying is not doing what its own comment says, and no amount of memory fixes that.

    $0, pure-stdlib after the S3 fetch: atom/chain/residue census per seed, printed side by side.
    """
    out = {"_what": "structural census of one leg's staged inputs across seeds — is what reps-prime built for "
                    "seeds 1 and 2 the same KIND of thing it built for seed 0?",
           "leg": leg, "mode": mode, "seeds": {}}
    for s in seeds:
        d = os.path.join(workdir, f"seed{s}")
        try:
            got = fetch_stage(d, mode=mode, seed=s, legs=(leg,))
        except Exception as e:  # noqa: BLE001 — a missing seed is a finding, not a crash
            out["seeds"][s] = {"error": f"{type(e).__name__}: {e}"}
            print(f"  seed {s}: NO STAGE CACHE — {type(e).__name__}: {e}")
            continue
        inner = os.path.join(d, leg)
        import hashlib

        def _sha(fp):
            try:
                with open(fp, "rb") as fh:
                    return hashlib.sha256(fh.read()).hexdigest()[:16]
            except OSError:
                return None
        rec = {"tar_bytes": got[leg]["bytes"], "tar_sha256": got[leg]["sha256"], "uri": got[leg]["uri"],
               "files": got[leg]["files"],
               "complex_pdb": pdb_census(os.path.join(inner, "complex.pdb")),
               "complex_pdb_sha256": _sha(os.path.join(inner, "complex.pdb")),
               "ligands_sdf_sha256": _sha(os.path.join(inner, "ligands.sdf"))}
        man = os.path.join(inner, "staging_manifest.json")
        if os.path.exists(man):
            try:
                rec["staging_manifest"] = json.load(open(man))
            except Exception as e:  # noqa: BLE001
                rec["staging_manifest_error"] = str(e)
        for extra in ("ligands.sdf", "ligand.sdf"):
            p = os.path.join(inner, extra)
            if os.path.exists(p):
                rec[extra + "_bytes"] = os.path.getsize(p)
        out["seeds"][s] = rec
    print("---- STAGED INPUT CENSUS BY SEED ----")
    for s, rec in out["seeds"].items():
        if rec.get("error"):
            print(f"  seed {s}: {rec['error']}")
            continue
        c = rec["complex_pdb"]
        sm = (rec.get("staging_manifest") or {}).get("starting_model") or {}
        print(f"  seed {s}: tar={rec['tar_bytes']} B sha={rec['tar_sha256']}  "
              f"complex.pdb atoms={c.get('atoms')} sha={rec['complex_pdb_sha256']} "
              f"het={c.get('hetatms')} chains={c.get('n_chains')} residues={c.get('n_residues')} "
              f"ligands.sdf sha={rec['ligands_sdf_sha256']}")
        print(f"      chains: {c.get('chains')}")
        print(f"      het resnames: {c.get('het_resnames')}")
        print(f"      starting_model_index={sm.get('starting_model_index')} "
              f"of n_models_available={sm.get('n_models_available')}  files={rec['files']}")
    print("---- END STAGED INPUT CENSUS ----")
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", default="edge_reps")
    ap.add_argument("--compare-stage", action="store_true",
                    help="structural census of one leg's staged inputs across seeds 0/1/2")
    ap.add_argument("--fetch-stage", metavar="DIR", default=None,
                    help="unpack both arms' staged trees from the hosts' own stage cache into DIR")
    ap.add_argument("--seed", type=int, default=1, help="which replicate's stage cache to fetch")
    ap.add_argument("--leg", action="append", default=None,
                    help="restrict --fetch-stage to this leg id (repeatable)")
    ap.add_argument("--out", default=None, help="write the structured record here (committed by CI)")
    ap.add_argument("--no-console", action="store_true",
                    help="S3 evidence only — skip the provider round trip")
    ap.add_argument("--watch-memory", type=float, metavar="MIN", default=None,
                    help="instead of a one-shot forensic, TRACE container memory vs its limit for MIN "
                         "minutes — the measurement that separates an OOM kill from a provider stop")
    ap.add_argument("--every", type=int, default=20, help="seconds between polls of the memory trace")
    a = ap.parse_args(argv)
    if a.compare_stage:
        doc = compare_stage(mode=a.mode, leg=(a.leg or ["calib_hi_to_lo__ternary_vhl"])[0])
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(doc, fh, indent=2, default=str)
                fh.write("\n")
            print(f"[diag] wrote {a.out}")
        return 0
    if a.fetch_stage:
        kw = {"legs": tuple(a.leg)} if a.leg else {}
        print(json.dumps(fetch_stage(a.fetch_stage, mode=a.mode, seed=a.seed, **kw), indent=2))
        return 0
    if a.watch_memory:
        doc = watch_memory(mode=a.mode, minutes=a.watch_memory, every_s=a.every)
    else:
        doc = diagnose(mode=a.mode, want_console=not a.no_console)
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(doc, fh, indent=2, default=str)
            fh.write("\n")
        print(f"[diag] wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
