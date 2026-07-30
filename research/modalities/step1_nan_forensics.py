#!/usr/bin/env python3
"""IS A REPEATING LEG FAILURE A PROPERTY OF THE EDGE OR OF THE HOSTS IT KEEPS LANDING ON? — from the
per-attempt archive, on a free runner. $0, reads S3 only, rents nothing, writes nothing to S3.

★ WHY THIS EXISTS (2026-07-28). `e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral` had been
diagnosed RETRY on 2026-07-27: a CPU reproduction of the production `sampler.setup()` — the very call that
raised `openmm.OpenMMException: Particle coordinate is NaN` — completed over every lambda state without a
NaN, and every force term was finite at the handed-over coordinates
(`step1-setup-energy-probe.json`). Under `step1_setup_energy_probe.verdict` that is, correctly, "the edge is
not the fault". RETRY is a hypothesis about the NEXT rental, though, not a measurement of it, and the lane
acted on it: the unit was re-placed, re-placed, and re-placed again.

The thing nobody had counted was HOW MANY TIMES. Each container start archives the previous attempt's log
under `<unit>/attempts/run-<UTC>.log` (`congeneric_fanout_vast._PREAMBLE`), so the object store holds a
durable, timestamped count of starts and — because the preamble runs `nvidia-smi
--query-gpu=name,memory.total,driver_version` before anything else — the CARD AND DRIVER each attempt ran
on. That turns the open question into an arithmetic one:

  HOST-INCIDENTAL   one or two attempts, on one or two hosts. Another rental is a reasonable purchase.
  DETERMINISTIC     many attempts, on many DISTINCT cards/drivers, all dying at the same call with the same
                    message. Every further rental buys the same failure, and CLAUDE.md §6's `_blocked_units`
                    exists precisely to stop that unbounded loop of short rentals.

⚠ THIS DOES NOT CONTRADICT THE CPU PROBE — IT COMPLETES IT. Both readings are true at once and together they
say something neither says alone: the system is sound (CPU minimises it), and the minimiser diverges anyway
on every GPU we can rent. That is a PLATFORM-CONDITIONAL failure, and the only reason it looked like a
retryable one is that "the edge is not the fault" was read as "so the next host will work". The retry count
is the observation that separates them, and it costs nothing to make.

The second thing this measures is whether the failing unit is CHEMICALLY special. `_clash_report` runs on
every leg at `[clash-diag:initial]`, so every unit's `complex.log` carries the same four numbers — atom
count, non-finite atoms, force-bearing contacts under 0.90 A, and the closest non-bonded distance. Nine
units reached a ddG. If the failing one's geometry readings sit inside the range the nine successes span,
"a bad starting structure" is measured NOT to be the mechanism rather than argued not to be.

Usage (needs only boto3):
    python step1_nan_forensics.py                       # every unit
    NAN_FORENSIC_UNITS=cw_bio_primary_amide python step1_nan_forensics.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT_JSON = os.path.join(HERE, "step1-nan-forensics.json")
OUT_TXT = os.path.join(HERE, "step1-nan-forensics.txt")

BUCKET = os.environ.get("VAST_CKPT_BUCKET", "sagemaker-us-east-2-646605541856")
RESULT_PREFIX = os.environ.get("FANOUT_RESULT_PREFIX", "nr4a3-step1-fanout/results")

# ★ THE THRESHOLD IS NOT A TASTE CALL — IT IS THE POINT AT WHICH ANOTHER RENTAL STOPS BEING EVIDENCE.
# One failure is noise. Two on one machine is a machine. The interesting quantity is DISTINCT hosts: a
# failure reproduced on N independent cards, with the same exception at the same call, is a statement about
# the system and no longer about any host. Three is the smallest N for which "unlucky twice" is not the
# simpler story, and it is the same standard the lane's own starved-host guard uses before it condemns.
MIN_DISTINCT_HOSTS_FOR_DETERMINISM = 3

_GPU = re.compile(r"^\s*(NVIDIA[^,]*|[A-Za-z][^,]*),\s*(\d+)\s*MiB,\s*([\d.]+)\s*$", re.M)
_NAN = "Particle coordinate is NaN"
_CLASH_HEAD = re.compile(
    r"\[clash-diag:(\w+)\] atoms=(\d+) nonfinite_atoms=(\d+) coords>1000nm_atoms=(\d+)")
_CLASH_SUM = re.compile(
    r"\[clash-diag:(\w+)\] non-bonded pairs < ([\d.]+) A: (\d+) force-bearing \(REAL\) \+ (\d+) "
    r"excluded-everywhere \(benign\); closest non-bonded = ([\d.]+) A")
_ETOT = re.compile(r"\[force-diag:(\w+)\] TOTAL potential energy = (-?[\d.eE+]+) kJ/mol")
_PLAT = re.compile(r"\[s1f\] openfe (\S+) plats \[([^\]]*)\]")
_FAILED_AT = re.compile(r'File "([^"]+)", line (\d+), in (\S+)')


def parse_attempt(text):
    """Everything a single attempt log says about WHERE it ran and HOW it died. PURE — no S3, no OpenMM,
    so the classification below is unit-testable without a network or a GPU.

    Every field is a measurement or None. None means "this log did not record it", which is deliberately
    NOT rendered as a benign value anywhere downstream: an attempt whose card we cannot read must not be
    counted towards 'distinct hosts', because that would let unreadable logs manufacture determinism."""
    g = _GPU.search(text or "")
    plat = _PLAT.search(text or "")
    row = {
        "gpu_name": g.group(1).strip() if g else None,
        "gpu_mem_mib": int(g.group(2)) if g else None,
        "driver": g.group(3) if g else None,
        "openfe": plat.group(1) if plat else None,
        "platforms": [p.strip().strip("'\"") for p in plat.group(2).split(",")] if plat else None,
        "setup_nan": _NAN in (text or ""),
        "bytes": len(text or ""),
    }
    tb = _FAILED_AT.findall(text or "")
    row["failed_at"] = ("%s:%s in %s" % (os.path.basename(tb[-1][0]), tb[-1][1], tb[-1][2])) if tb else None
    heads = {m.group(1): {"atoms": int(m.group(2)), "nonfinite_atoms": int(m.group(3)),
                          "coords_gt_1000nm": int(m.group(4))} for m in _CLASH_HEAD.finditer(text or "")}
    sums = {m.group(1): {"thresh_A": float(m.group(2)), "force_bearing": int(m.group(3)),
                         "excluded_benign": int(m.group(4)), "closest_A": float(m.group(5))}
            for m in _CLASH_SUM.finditer(text or "")}
    row["clash"] = {t: {**heads.get(t, {}), **sums.get(t, {})} for t in set(heads) | set(sums)}
    e = _ETOT.search(text or "")
    row["total_energy_kj_mol"] = float(e.group(2)) if e else None
    return row


def host_key(row):
    """What counts as ONE host for the determinism test. (card, driver) rather than a machine id, because
    the archived log is written by the container and never sees the Vast machine id — and because the
    scientific question is whether the failure survives a change of HARDWARE, which is what the card and
    its driver name. Unreadable -> None, and None is excluded from the count rather than lumped together."""
    if not row.get("gpu_name"):
        return None
    return f"{row['gpu_name']} / driver {row.get('driver')}"


def classify(unit_row):
    """(verdict, why) for one unit, from its attempt rows alone. PURE.

    Verdicts:
      NOT_FAILING              no attempt in the archive died at the pre-MD minimiser.
      HOST_INCIDENTAL          it died, but on too few distinct cards to be a statement about the system.
      DETERMINISTIC_ON_GPU     it died the same way on >= MIN_DISTINCT_HOSTS_FOR_DETERMINISM distinct
                               cards. Another rental buys the identical failure.
      UNREADABLE               attempts exist but none records its card, so nothing can be concluded. This
                               is a first-class answer and must never collapse into HOST_INCIDENTAL: 'we
                               could not tell' and 'we told, and it was one host' are different states.
    """
    nan_rows = [a for a in unit_row["attempts"] if a.get("setup_nan")]
    if not nan_rows:
        return "NOT_FAILING", (f"no archived attempt raised {_NAN!r} "
                               f"({len(unit_row['attempts'])} attempt log(s) read)")
    hosts = sorted({h for h in (host_key(a) for a in nan_rows) if h})
    if not hosts:
        return "UNREADABLE", (f"{len(nan_rows)} attempt(s) raised the setup NaN but none recorded a card, "
                              f"so the distinct-host count is unmeasured — not low")
    if len(hosts) >= MIN_DISTINCT_HOSTS_FOR_DETERMINISM:
        return "DETERMINISTIC_ON_GPU", (
            f"{len(nan_rows)} archived attempt(s) died with {_NAN!r} inside the pre-MD "
            f"`sampler.setup()` minimiser, across {len(hosts)} DISTINCT card/driver combinations "
            f"({hosts}). A failure that survives that many independent hosts is a property of the system on "
            f"this platform, not of any host, so a further rental buys the identical failure")
    return "HOST_INCIDENTAL", (
        f"{len(nan_rows)} attempt(s) raised the setup NaN but only on {len(hosts)} distinct card(s) "
        f"({hosts}), below the {MIN_DISTINCT_HOSTS_FOR_DETERMINISM} needed to call it host-independent")


def geometry_comparison(rows):
    """Is the failing unit's STARTING GEOMETRY unusual against the units that succeeded?

    Uses `[clash-diag:initial]`, which every leg logs before it does anything — so this compares like with
    like. Returns the band the successful units span and each failing unit's readings against it, because
    'the structure is bad' is the obvious story and it deserves to be measured rather than dismissed."""
    def initial(r):
        return (r.get("head") or {}).get("clash", {}).get("initial") or {}

    ok = [r for r in rows if r["verdict"] == "NOT_FAILING" and initial(r)]
    bad = [r for r in rows if r["verdict"] in ("DETERMINISTIC_ON_GPU", "HOST_INCIDENTAL") and initial(r)]
    if not ok:
        return {"note": "no successful unit logged a [clash-diag:initial] line — nothing to compare against"}
    def band(key):
        vals = [initial(r)[key] for r in ok if key in initial(r)]
        return {"min": min(vals), "max": max(vals), "n": len(vals)} if vals else None
    out = {"successful_units_band": {k: band(k) for k in
                                     ("atoms", "nonfinite_atoms", "force_bearing", "closest_A")},
           "failing_units": {r["unit_id"]: initial(r) for r in bad}}
    verdicts = {}
    for r in bad:
        ini, notes = initial(r), []
        for k in ("nonfinite_atoms", "force_bearing", "closest_A"):
            b = band(k)
            if b is None or k not in ini:
                continue
            if ini[k] < b["min"] or ini[k] > b["max"]:
                notes.append(f"{k}={ini[k]} is OUTSIDE the successful band [{b['min']}, {b['max']}]")
        verdicts[r["unit_id"]] = (notes or
                                  ["every [clash-diag:initial] reading sits INSIDE the band spanned by the "
                                   "units that reached a ddG — a bad starting structure is measured not to "
                                   "be what distinguishes this unit"])
    out["verdicts"] = verdicts
    return out


# ---- S3 side (not pure; everything above is) ---------------------------------------------------------

def _s3():
    import boto3
    return boto3.client("s3")


def _text(s3, key):
    try:
        return s3.get_object(Bucket=BUCKET, Key=key)["Body"].read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 — a missing log is a real answer
        return None


def _attempt_keys(s3, prefix):
    keys, tok = [], None
    while True:
        kw = {"Bucket": BUCKET, "Prefix": prefix}
        if tok:
            kw["ContinuationToken"] = tok
        page = s3.list_objects_v2(**kw)
        for o in page.get("Contents", []) or []:
            keys.append((o["Key"], o["LastModified"].isoformat(), o["Size"]))
        if not page.get("IsTruncated"):
            break
        tok = page.get("NextContinuationToken")
    return sorted(keys)


def collect(units):
    s3 = _s3()
    rows = []
    for u in units:
        uid = u["unit_id"]
        base = f"{RESULT_PREFIX}/{uid}"
        atts = _attempt_keys(s3, f"{base}/attempts/")
        parsed = []
        for key, mtime, size in atts:
            a = parse_attempt(_text(s3, key))
            a["key"] = key.rsplit("/", 1)[-1]
            a["mtime_utc"] = mtime
            a["size"] = size
            parsed.append(a)
        # The LIVE (unarchived) pair too — the newest attempt has not been rolled into attempts/ yet, so
        # omitting it would systematically undercount by exactly one and always the most recent one.
        head = parse_attempt((_text(s3, f"{base}/complex.log") or "") + "\n"
                             + (_text(s3, f"{base}/run.log") or ""))
        head["key"] = "complex.log + run.log (current)"
        if head["bytes"]:
            parsed.append(head)
        row = {"unit_id": uid, "edge": f"{u['ligand_a']}->{u['ligand_b']}",
               "n_attempt_logs": len(atts), "attempts": parsed, "head": head,
               "phase": (_text(s3, f"{base}/phase.txt") or "").strip() or None,
               "has_ddg": _text(s3, f"{base}/ddg.json") is not None}
        row["verdict"], row["why"] = classify(row)
        rows.append(row)
    return rows


def render(rows, geo):
    L = [f"[s1f-nan] bucket s3://{BUCKET}  prefix {RESULT_PREFIX}",
         "[s1f-nan] $0 — reads the per-attempt archive only; rents nothing, destroys nothing, writes nothing "
         "to S3", "",
         "=== PER-UNIT ATTEMPT COUNT AND VERDICT ===",
         f"  {'unit':58s} {'ddg':4s} {'atts':5s} {'nan':4s} {'hosts':6s} verdict"]
    for r in rows:
        nan = sum(1 for a in r["attempts"] if a.get("setup_nan"))
        hosts = len({h for h in (host_key(a) for a in r["attempts"] if a.get("setup_nan")) if h})
        L.append(f"  {r['unit_id'][:58]:58s} {'YES' if r['has_ddg'] else 'no':4s} "
                 f"{r['n_attempt_logs']:<5d} {nan:<4d} {hosts:<6d} {r['verdict']}")
    for r in rows:
        if r["verdict"] == "NOT_FAILING":
            continue
        L += ["", f"=== {r['unit_id']} — {r['verdict']} ===", f"  {r['why']}",
              f"  phase: {r['phase']}", "  attempts that raised the setup NaN:"]
        for a in r["attempts"]:
            if not a.get("setup_nan"):
                continue
            L.append(f"    {a.get('mtime_utc') or '(current)':26s} {str(host_key(a)):46s} "
                     f"failed_at={a.get('failed_at')}")
    L += ["", "=== STARTING GEOMETRY — the failing unit against the ones that reached a ddG ===",
          json.dumps(geo, indent=2)]
    return "\n".join(L) + "\n"


def main():
    import congeneric_fanout as cf
    want = (os.environ.get("NAN_FORENSIC_UNITS") or "").strip()
    units = [u for u in cf.default_units() if (not want or any(
        w.strip() and w.strip() in u["unit_id"] for w in want.split(",")))]
    if not units:
        raise SystemExit(f"[s1f-nan] no unit matches NAN_FORENSIC_UNITS={want!r}")
    rows = collect(units)
    geo = geometry_comparison(rows)
    txt = render(rows, geo)
    print(txt, flush=True)
    with open(OUT_TXT, "w") as f:
        f.write(txt)
    with open(OUT_JSON, "w") as f:
        json.dump({"_what": "per-attempt forensics of the step 1 fan-out legs: how many container starts "
                            "each unit has burned, on how many distinct cards, and how each died",
                   "_no_spend": "reads S3 only; no GPU, no instance, no S3 writes",
                   "_bucket": BUCKET, "_prefix": RESULT_PREFIX,
                   "min_distinct_hosts_for_determinism": MIN_DISTINCT_HOSTS_FOR_DETERMINISM,
                   "units": rows, "geometry_comparison": geo}, f, indent=2, default=str)
    print(f"[s1f-nan] wrote {OUT_JSON} and {OUT_TXT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
