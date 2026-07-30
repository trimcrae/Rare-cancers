#!/usr/bin/env python3
"""Audit a unit's commit store: which committed generations can the RESTORER actually use?

★★ WHY THIS EXISTS (measured 2026-07-30, on the valB closure triangle's T3 ternary leg).
The board printed `committed: production/1800` while the host that had just been rented printed
`[spot-driver] restore -> production@iter 1760`. Both were correct, and that is the bug: they read the
commit store through DIFFERENT rules.

  * `ternary_vast_launch.committed_progress` counts a generation the moment ANY object appears under
    `.../<phase>/iter-<N>/` — it globs keys and takes the max N.
  * `rbfe_spot_checkpoint._BaseCommitStore.restore_latest` walks `list_committed`, which only returns a
    generation that HAS its `COMMITTED.json` manifest, and then additionally REJECTS it if
    `fingerprint_mismatch_reason` says it belongs to a different system configuration.

`_persist` uploads the .nc, then the .chk, then "manifest LAST" — deliberately, so a torn upload is never
mistaken for a durable commit. That contract is right. What was missing is that the REPORTING side did not
share it, so a generation that is half-uploaded (or fully uploaded and fingerprint-rejected) still moved the
board's percentage. The visible symptom is a leg that appears to advance and then resumes below where it
appeared to be, over and over — which reads as "the host is slow" or "the host wedged" when it is neither.

So this module answers one question per generation, with the evidence, and never guesses:
    can restore_latest use this, and if not, WHICH of the two rules refused it?

$0, read-only, boto3-only (no MD stack): it lists keys and reads manifests. Safe to run against a live leg.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MANIFEST = "COMMITTED.json"

# The reasons a generation the board counts is NOT restorable. Ordered by where the pipeline stops.
NO_MANIFEST = "no-manifest"
BAD_MANIFEST = "unreadable-manifest"
FINGERPRINT = "fingerprint-rejected"
RESTORABLE = "restorable"


_ENTRY_DEFAULT_RE = re.compile(r'^\s*export\s+([A-Z_0-9]+)="?\$\{\1:-([^}"]*)\}"?\s*$', re.M)


def entrypoint_defaults(script_text):
    """{VAR: default} for every `export VAR="${VAR:-default}"` in the leg entry script. PURE.

    ★ THE HOST'S ENV IS NOT THE JOBSPEC'S ENV, AND THE DIFFERENCE IS NOT COSMETIC (measured
    2026-07-30). `system_fingerprint_fields` renders an ABSENT variable as `''`, and `run_ternary_leg.sh`
    exports `RBFE_CONSTRAIN_LIGAND_CH="${RBFE_CONSTRAIN_LIGAND_CH:-0}"` — so the host hashes `'0'` where a
    JobSpec-only reconstruction hashes `''`. Those are different strings and therefore different
    fingerprints. Audited without this overlay, EVERY generation of all four triangle legs reported
    `fingerprint-rejected`, including three legs that had already finished and banked a ΔG — a total false
    positive that would have read as "the checkpoints are all poisoned".

    Parsed from the script rather than transcribed into a table here, because a transcribed default is a
    second home for a fact (CLAUDE.md rule 1) and would go stale the first time the script changed.
    """
    return dict(_ENTRY_DEFAULT_RE.findall(script_text or ""))


def host_env(jobspec_env, script_text, *, fields=None):
    """The env the CONTAINER actually runs with: entry-script defaults, overridden by the JobSpec. PURE.

    `fields` restricts the overlay to the variables the fingerprint hashes, so an unrelated default
    (OPENMM_REQUIRE_CUDA, RBFE_MIN_STEPS) can never perturb it.
    """
    out = dict(entrypoint_defaults(script_text))
    if fields is not None:
        out = {k: v for k, v in out.items() if k in set(fields)}
    out.update({k: v for k, v in dict(jobspec_env).items() if v not in (None, "")})
    return out


def _iter_and_gen(key: str, base: str):
    """('production', 1800, '<gen>') from '<base>/production/iter-00001800/<gen>/COMMITTED.json'. PURE."""
    rest = key[len(base):].lstrip("/") if key.startswith(base) else key
    m = re.match(r"(warmup|production)/iter-(\d+)/([^/]+)/", rest)
    if not m:
        return None
    return m.group(1), int(m.group(2)), m.group(3)


def group_keys(keys, base):
    """{(phase, iter, gen): [object-name, ...]} from a flat key listing. PURE — the whole listing shape
    lives here so the audit itself is testable without S3."""
    out = {}
    for k in keys:
        pig = _iter_and_gen(k, base)
        if pig is None:
            continue
        name = k.rsplit("/", 1)[-1]
        if not name:
            continue
        out.setdefault(pig, []).append(name)
    return out


def classify(names, manifest, mismatch_reason):
    """Why can (or can't) the restorer use this generation? PURE.

    `manifest` is the parsed COMMITTED.json or None; `mismatch_reason` is
    `fingerprint_mismatch_reason(manifest)` — None meaning "belongs to this configuration".
    Mirrors restore_latest's order exactly: manifest present -> readable -> fingerprint -> usable.
    """
    if MANIFEST not in names:
        return NO_MANIFEST, ("the manifest is absent, so _persist did not finish. The data objects "
                             f"present are {sorted(n for n in names if n != MANIFEST)} — uploaded but "
                             "not yet declared, which is exactly what 'manifest LAST' is for.")
    if manifest is None:
        return BAD_MANIFEST, "the manifest key exists but did not parse as JSON"
    if mismatch_reason is not None:
        return FINGERPRINT, f"restore_latest would reject it: {mismatch_reason}"
    return RESTORABLE, "manifest present and the fingerprint matches this configuration"


def frontiers(rows):
    """(counted_frontier, restorable_frontier) per phase, from classified rows. PURE.

    `counted` is what the board's `committed_progress` reports (any object under iter-N).
    `restorable` is what a freshly rented host would actually resume from. A GAP between them is the
    defect this module was written to make visible — and it is a number, not an impression.
    """
    counted, restorable = {}, {}
    for r in rows:
        ph, it = r["phase"], r["iteration"]
        counted[ph] = max(counted.get(ph, 0), it)
        if r["verdict"] == RESTORABLE:
            restorable[ph] = max(restorable.get(ph, 0), it)
    return counted, restorable


def audit(s3, bucket, base_prefix, *, env=None, fingerprint_reason=None):
    """List one unit's commit store and classify every generation. `base_prefix` is the unit's commit
    base (…/commits/<unit_id>). Returns {"rows": [...], "counted": {...}, "restorable": {...}}.

    ⚠ `env` IS NOT OPTIONAL IN PRACTICE, AND DEFAULTING IT TO os.environ WOULD MAKE THIS LIE. The
    fingerprint is a hash over SYSTEM_FINGERPRINT_ENV — LEG_ID, SEED, timesteps, N_WINDOWS and friends —
    none of which are set on a CI runner. Audited with the runner's own environment, every correctly
    stamped generation would hash against a fingerprint of empty strings and be reported
    `fingerprint-rejected`: a total false positive, and precisely the "plausible story" §4 forbids. So the
    caller passes the env the HOST runs with, which `build_jobspec` constructs purely.
    """
    base = base_prefix.rstrip("/")
    keys = []
    pag = s3.get_paginator("list_objects_v2")
    for page in pag.paginate(Bucket=bucket, Prefix=base + "/"):
        for o in page.get("Contents", []):
            keys.append(o["Key"])
    groups = group_keys(keys, base)

    if fingerprint_reason is None:
        from rbfe_spot_checkpoint import fingerprint_mismatch_reason as _fmr  # noqa: PLC0415

        def fingerprint_reason(man):
            return _fmr(man, env=env)

    rows = []
    for (phase, it, gen), names in sorted(groups.items(), key=lambda kv: (kv[0][0], -kv[0][1], kv[0][2])):
        man = None
        if MANIFEST in names:
            try:
                body = s3.get_object(Bucket=bucket, Key=f"{base}/{phase}/iter-{it:08d}/{gen}/{MANIFEST}")
                man = json.loads(body["Body"].read())
            except Exception as e:  # noqa: BLE001 — an unreadable manifest is a FINDING, not a crash
                man = None
                names = [n for n in names if n != MANIFEST] + [MANIFEST]
                print(f"[audit] manifest unreadable at iter {it} gen {gen[:8]}: {type(e).__name__}: {e}")
        why_fp = fingerprint_reason(man) if man is not None else None
        verdict, why = classify(names, man, why_fp)
        rows.append({"phase": phase, "iteration": it, "generation": gen,
                     "objects": sorted(names), "verdict": verdict, "why": why})
    counted, restorable = frontiers(rows)
    return {"rows": rows, "counted": counted, "restorable": restorable}


def render(unit_id, result):
    """Human-readable report. The GAP line is the point of the whole module."""
    out = [f"=== commit-store audit: {unit_id} ==="]
    for r in result["rows"]:
        mark = "OK " if r["verdict"] == RESTORABLE else "XX "
        # `.get` throughout: a diagnostic must never be the thing that raises. A row missing a field is
        # itself information, and printing "gen=?" beats a KeyError that hides the frontier lines below.
        out.append(f"  {mark}{r['phase']}/{r['iteration']:>6}  gen={str(r.get('generation') or '?')[:8]}  "
                   f"{r['verdict']}")
        if r["verdict"] != RESTORABLE and r.get("why"):
            out.append(f"        {r['why']}")
    for ph in sorted(set(list(result["counted"]) + list(result["restorable"]))):
        c = result["counted"].get(ph, 0)
        rr = result["restorable"].get(ph, 0)
        if c == rr:
            out.append(f"  {ph}: board counts {c}, restorer would use {rr} — AGREE")
        else:
            out.append(f"  ⚠ {ph}: board counts {c}, restorer would use {rr} — GAP OF {c - rr} ITERATIONS. "
                       f"Every host rented from here re-runs those iterations and the board never says so.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    # The unit is named the way the LAUNCHER names it, not by hand: build_jobspec then yields both the
    # unit id and the exact env whose fingerprint the restorer will compare against.
    ap.add_argument("--leg", required=True, help="leg id, e.g. calib_hi_to_lo2__ternary_vhl")
    ap.add_argument("--mode", required=True, help="mode, e.g. triangle")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--direction", default="fwd")
    ap.add_argument("--timestep-fs", default=None)
    ap.add_argument("--warmup-timestep-fs", default=None)
    ap.add_argument("--bucket", default=None)
    ap.add_argument("--prefix", default=None, help="lane result prefix (default: the ternary lane's)")
    ap.add_argument("--out", default=None, help="also write the JSON here")
    a = ap.parse_args(argv)

    import boto3  # noqa: PLC0415 — CLI-only; the library functions above take an injected client
    from ternary_vast_launch import DEFAULT_BUCKET, RESULT_PREFIX, build_jobspec  # noqa: PLC0415

    bucket = a.bucket or DEFAULT_BUCKET
    prefix = (a.prefix or RESULT_PREFIX).rstrip("/")
    spec = build_jobspec(a.leg, seed=a.seed, direction=a.direction, mode=a.mode,
                         timestep_fs=a.timestep_fs, warmup_timestep_fs=a.warmup_timestep_fs,
                         bucket=bucket, prefix=prefix)
    # JobSpec is a dataclass, not a mapping — `spec["env"]` raised TypeError on the first CI run.
    spec_env = dict(spec.env)
    unit = spec_env["UNIT_ID"]
    # …and the JobSpec alone is not the host's env: the entry script fills in defaults the fingerprint
    # hashes. See entrypoint_defaults for the false positive this removes.
    from rbfe_spot_checkpoint import SYSTEM_FINGERPRINT_ENV  # noqa: PLC0415

    entry = Path(__file__).with_name("run_ternary_leg.sh")
    env = host_env(spec_env, entry.read_text() if entry.exists() else "",
                   fields=SYSTEM_FINGERPRINT_ENV)
    res = audit(boto3.client("s3"), bucket, f"{prefix}/commits/{unit}", env=env)
    print(render(unit, res))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"unit": unit, "bucket": bucket,
                       "fingerprint_env": {k: env.get(k, "") for k in sorted(env)}, **res},
                      fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
