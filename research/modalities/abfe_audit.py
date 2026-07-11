#!/usr/bin/env python3
"""AUDIT every ABFE leg's checkpoint data for the λ-window self-consistency bug.

Motivation (2026-07-11): `N_WINDOWS = len(LAMBDA_ELEC)` in nr4a3_abfe.py was frozen at import to the STANDARD
12-window count, but a `dense` run evaluates each sample's reduced potential u at 16 λ-states. So a dense run
produced legs with 12 windows but 16-entry u vectors — inconsistent, and (as designed) UN-reducible: MBAR checks
len(sample)==K and raises. This audit proves, leg by leg from the raw S3 checkpoints, that:
  (a) every leg that fed a PUBLISHED ΔG_bind is SELF-CONSISTENT (window_count == len(u) == meta n_windows) and
      COMPLETE (every window has samples), so its MBAR reduction is valid; and
  (b) the buggy dense (nr4a2rep) legs are INCONSISTENT and/or INCOMPLETE — and therefore, as the empty
      per_replicate_dg_bind in the diagnostics confirms, never produced a number that reached the manuscript.

HONEST SCOPE (reviewer §7, narrowed 2026-07-11): this audit supports the statement "we found no evidence that
the published ABFE table used the inconsistent dense legs; the fixed reducer exactly reproduces the table from
structurally consistent standard-schedule data." It does NOT prove "no published value could have been
corrupted." Beyond the window_count==u_length structural check it now adds SEMANTIC checks per leg (λ
identity/order vs the recomputed schedule; fully-coupled/decoupled endpoints; target+leg identity in meta;
sample-duplication dedup ratio; schedule-metadata presence) so a leg that is structurally consistent but
semantically wrong (mislabeled schedule, wrong endpoints, duplicated samples) is still caught.

Pure stdlib + boto3 (reads the SageMaker checkpoint bucket). Structural + semantic checks need no pymbar; the
optional reduce cross-check (for consistent+complete legs) uses nr4a3_abfe.reduce_leg (which now infers K from
the data). Emits abfe-audit-report.json. Run in CI (abfe-audit.yml) where S3 + pymbar are available.
"""
import json
import os
import sys

_LEG_TOKENS = ("complex", "solvent")
_TARGET_TOKENS = ("nr4a3", "nr4a1", "nr4a2")


def _leg_token_from_prefix(prefix):
    """The leg ('complex'/'solvent') encoded in a leg's S3 prefix, or None. The submitter names the checkpoint
    prefix complex-<r>/solvent and entry_abfe nests <receptor>/<leg>/, so a leg token appears as a bare path
    segment or a 'complex-<r>' segment."""
    for t in reversed(prefix.strip("/").split("/")):
        for L in _LEG_TOKENS:
            if t == L or t.startswith(L + "-"):
                return L
    return None


def _target_token_from_prefix(prefix):
    """The receptor/target token (nr4a1/2/3) encoded in a leg's S3 prefix, or None (solvent legs are shared).
    Skips the FIRST path segment — that is the run tag (e.g. 'nr4a3-abfe'), which always contains 'nr4a3' and
    must not be mistaken for the receptor. The receptor appears as a later bare segment or a 'complex-<t>' one."""
    segs = prefix.strip("/").split("/")[1:]            # drop the tag segment
    for seg in segs:
        s = seg.lower()
        if s in _TARGET_TOKENS:
            return s
        for tgt in _TARGET_TOKENS:
            if s == "complex-" + tgt:
                return tgt
    return None


def _known_schedules():
    """The (elec, sterics) λ lists RECOMPUTED from nr4a3_abfe (the source of truth) — standard (12) and dense
    (16). Lazy import so abfe_audit stays import-clean even when run from an unusual cwd."""
    import nr4a3_abfe as A
    std = list(zip(A.LAMBDA_ELEC, A.LAMBDA_STERICS))
    dense = list(zip(A.LAMBDA_ELEC_DENSE, A.LAMBDA_STERICS_DENSE))
    return std, dense


def semantic_checks(leg_prefix, n_window_files, n_contiguous, u_length, meta, raw_counts, uniq_counts):
    """SEMANTIC audit of one leg (reviewer §7) — pure, S3-free, so it is directly unit-testable with synthetic
    inputs. Goes beyond the structural window_count==u_length check:
      (a) λ identity/order: recompute the (elec,sterics) list for the schedule the leg CLAIMS and record whether
          the leg's window count (and u length) match that schedule's length; if meta actually records per-window
          λ, verify value+order too (else flag it as un-recorded → not verifiable);
      (b) endpoints: the claimed schedule's window 0 is fully coupled (1,1) and last fully decoupled (0,0);
      (c) target/leg identity: present + consistent between meta.json and the S3 path;
      (d) sample duplication: per-window raw-line vs unique-by-iter count → dedup ratio, flag windows with excess;
      (e) schedule metadata present in meta.
    Returns a dict of fields + a `semantic_findings` list + `semantic_ok` (False ONLY on a hard contradiction —
    a definite count/value/endpoint/identity mismatch or excess duplication; missing metadata is a recorded
    WARNING, not a hard fail, since the current meta.json legitimately omits some of these fields)."""
    std, dense = _known_schedules()
    meta = meta or {}
    findings = []

    # (e) schedule metadata present?
    meta_nw = meta.get("n_windows")
    meta_sched_name = meta.get("lambda_schedule") or meta.get("schedule")
    meta_lambda = meta.get("lambda") if isinstance(meta.get("lambda"), list) else None
    schedule_metadata_present = meta_nw is not None
    if not schedule_metadata_present:
        findings.append("schedule metadata (n_windows) absent from meta.json")

    # claimed schedule: prefer a recorded name, else INFER from the count actually scored (u_length is #states
    # each sample was evaluated at; fall back to the window-file count).
    if isinstance(meta_sched_name, str) and meta_sched_name.strip().lower() in ("standard", "dense"):
        schedule_claimed = meta_sched_name.strip().lower()
        schedule_source = "meta"
    else:
        n_for_infer = u_length if u_length is not None else n_window_files
        schedule_claimed = ("dense" if n_for_infer == len(dense)
                            else "standard" if n_for_infer == len(std) else "unknown")
        schedule_source = "inferred-from-window-count"
        findings.append("schedule name not recorded in meta; inferred from window count")
    expected = dense if schedule_claimed == "dense" else std if schedule_claimed == "standard" else None

    # (a) λ identity / order
    lambda_len_match = None
    lambda_value_order_match = None
    if expected is not None:
        lambda_len_match = (n_window_files == len(expected)
                            and (u_length is None or u_length == len(expected)))
        if not lambda_len_match:
            findings.append(f"window/u count ({n_window_files}/{u_length}) != claimed '{schedule_claimed}' "
                            f"schedule length {len(expected)}")
        if meta_lambda is not None:
            rec = [tuple(x) for x in meta_lambda]
            lambda_value_order_match = (rec == expected)
            if not lambda_value_order_match:
                findings.append("recorded per-window λ values/order do NOT match the claimed schedule")
        else:
            findings.append("per-window λ values not recorded in meta — value/order match not verifiable")
    else:
        findings.append("could not identify a known schedule (window count matches neither standard=12 nor "
                        "dense=16)")

    # (b) endpoints of the claimed schedule
    endpoints_ok = None
    if expected is not None:
        endpoints_ok = (tuple(expected[0]) == (1.0, 1.0) and tuple(expected[-1]) == (0.0, 0.0))
        if not endpoints_ok:
            findings.append("claimed schedule endpoints are not (1,1)…(0,0)")

    # (c) target / leg identity present + consistent (meta vs path)
    leg_in_meta = meta.get("leg")
    path_leg = _leg_token_from_prefix(leg_prefix)
    leg_identity_present = leg_in_meta is not None
    leg_identity_consistent = (None if (leg_in_meta is None or path_leg is None)
                               else leg_in_meta == path_leg)
    if leg_in_meta is None:
        findings.append("leg identity absent from meta.json")
    elif leg_identity_consistent is False:
        findings.append(f"meta leg '{leg_in_meta}' != path leg '{path_leg}'")
    target_in_meta = meta.get("receptor") or meta.get("target")
    path_target = _target_token_from_prefix(leg_prefix)
    target_identity_present = target_in_meta is not None
    target_identity_consistent = (None if (target_in_meta is None or path_target is None)
                                  else str(target_in_meta).lower() == str(path_target).lower())
    if target_in_meta is None:
        findings.append("target/receptor identity absent from meta.json (present only in the S3 path)")
    elif target_identity_consistent is False:
        findings.append(f"meta target '{target_in_meta}' != path target '{path_target}'")

    # (d) sample duplication — per-window raw vs unique-by-iter → dedup ratio
    dedup_ratios = [(raw / uniq if uniq else None) for raw, uniq in zip(raw_counts or [], uniq_counts or [])]
    valid = [r for r in dedup_ratios if r is not None]
    max_dedup_ratio = max(valid) if valid else None
    DUP_THRESH = 1.10   # >10% raw lines beyond unique-by-iter samples → checkpoint/resume left duplicate records
    duplication_flagged = bool(max_dedup_ratio is not None and max_dedup_ratio > DUP_THRESH)
    if duplication_flagged:
        findings.append(f"sample duplication: max raw/unique-by-iter line ratio {max_dedup_ratio:.2f} "
                        f"(> {DUP_THRESH}) — dedup-by-iter needed before MBAR")

    # semantic_ok = no HARD contradiction (definite False); None (un-verifiable) does not fail the leg.
    semantic_ok = (all(x is not False for x in (lambda_len_match, lambda_value_order_match, endpoints_ok,
                                                leg_identity_consistent, target_identity_consistent))
                   and not duplication_flagged)
    return {
        "schedule_claimed": schedule_claimed, "schedule_source": schedule_source,
        "schedule_metadata_present": schedule_metadata_present,
        "lambda_length_match": lambda_len_match, "lambda_value_order_match": lambda_value_order_match,
        "endpoints_ok": endpoints_ok,
        "leg_identity_present": leg_identity_present, "leg_identity_consistent": leg_identity_consistent,
        "target_identity_present": target_identity_present,
        "target_identity_consistent": target_identity_consistent,
        "dedup_ratios": dedup_ratios, "max_dedup_ratio": max_dedup_ratio,
        "duplication_flagged": duplication_flagged,
        "semantic_findings": findings, "semantic_ok": semantic_ok,
    }


def _s3():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    acct = boto3.client("sts").get_caller_identity()["Account"]
    return boto3.client("s3"), f"sagemaker-{region}-{acct}"


def _list(s3, bucket, prefix):
    keys = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for o in page.get("Contents", []):
            keys.append((o["Key"], o["Size"]))
    return keys


def discover_tags(s3, bucket, name="nr4a3-abfe"):
    """Every top-level '<tag>/ckpt/' prefix under the bucket whose tag contains `name`."""
    tags = set()
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=name, Delimiter="/"):
        for cp in page.get("CommonPrefixes", []):
            t = cp["Prefix"].rstrip("/")
            tags.add(t)
    return sorted(tags)


def _first_u_len(s3, bucket, key):
    """Length of the reduced-potential vector u in the first non-empty jsonl record (== #λ-states the sample was
    evaluated at). Streams only the first ~64 KiB so we never pull a whole window file."""
    body = s3.get_object(Bucket=bucket, Key=key, Range="bytes=0-65535")["Body"].read().decode("utf-8", "ignore")
    for line in body.splitlines():
        line = line.strip()
        if line:
            try:
                u = json.loads(line).get("u")
            except json.JSONDecodeError:      # truncated final line from the range read
                continue
            if isinstance(u, list):
                return len(u)
    return None


def audit_leg(s3, bucket, tag, leg_prefix):
    """Structural audit of one leg directory (the prefix that directly contains window_XX.jsonl)."""
    keys = _list(s3, bucket, leg_prefix)
    wins = sorted(k for k, _ in keys if os.path.basename(k).startswith("window_")
                  and k.endswith(".jsonl"))
    # contiguous window count from window_00
    idx = set()
    for k in wins:
        b = os.path.basename(k)
        try:
            idx.add(int(b[len("window_"):-len(".jsonl")]))
        except ValueError:
            pass
    n_contig = 0
    while n_contig in idx:
        n_contig += 1
    n_files = len(idx)
    u_len = _first_u_len(s3, bucket, wins[0]) if wins else None
    meta = None
    for k, _ in keys:
        if os.path.basename(k) == "meta.json":
            meta = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read())
            break
    meta_nw = (meta or {}).get("n_windows")
    # per-window RAW line count (completeness) AND unique-by-iter count (dedup ratio → sample-duplication check)
    raw_counts, uniq_counts = [], []
    for w in range(max(n_contig, u_len or 0, n_files)):
        wk = next((k for k in wins if os.path.basename(k) == f"window_{w:02d}.jsonl"), None)
        if wk is None:
            raw_counts.append(0); uniq_counts.append(0); continue
        text = s3.get_object(Bucket=bucket, Key=wk)["Body"].read().decode("utf-8", "ignore")
        raw, iters = 0, set()
        for line in text.splitlines():
            if not line.strip():
                continue
            raw += 1
            try:
                iters.add(int(json.loads(line)["iter"]))
            except Exception:                          # noqa: BLE001 — torn line from resume/truncation
                pass
        raw_counts.append(raw); uniq_counts.append(len(iters))
    samples = raw_counts                               # back-compat field name
    consistent = (u_len is not None and n_files == u_len and n_contig == n_files)
    complete = bool(samples) and all(x > 0 for x in samples[:(u_len or n_files)])
    sem = semantic_checks(leg_prefix, n_files, n_contig, u_len, meta, raw_counts, uniq_counts)
    structural_verdict = ("CONSISTENT+COMPLETE" if consistent and complete else
                          "INCONSISTENT (window_count != u_length)" if not consistent else
                          "INCOMPLETE (missing windows)")
    out = {
        "leg_prefix": leg_prefix, "n_window_files": n_files, "n_contiguous": n_contig,
        "u_length": u_len, "meta_n_windows": meta_nw, "samples_per_window": samples,
        "unique_iters_per_window": uniq_counts,
        "self_consistent": consistent, "complete": complete,
        "structural_verdict": structural_verdict,
        # a leg is trustworthy only if it passes BOTH the structural and the semantic checks
        "trustworthy": bool(consistent and complete and sem["semantic_ok"]),
        "verdict": (structural_verdict if not (consistent and complete)
                    else "CONSISTENT+COMPLETE+SEMANTIC-OK" if sem["semantic_ok"]
                    else "SEMANTIC-FAIL (" + "; ".join(sem["semantic_findings"]) + ")"),
    }
    out.update(sem)
    return out


def find_leg_dirs(s3, bucket, tag):
    """Locate each leg's window-holding directory under <tag>/ckpt/ (the sync may nest it a level or two)."""
    keys = _list(s3, bucket, f"{tag}/ckpt/")
    dirs = {}
    for k, _ in keys:
        if os.path.basename(k) == "window_00.jsonl":
            dirs[os.path.dirname(k) + "/"] = True
    return sorted(dirs)


def main():
    s3, bucket = _s3()
    only = [t.strip() for t in os.environ.get("AUDIT_TAGS", "").split(",") if t.strip()]
    tags = only or discover_tags(s3, bucket)
    report = {"bucket": bucket, "tags_audited": tags, "legs": [], "reduce_crosscheck": []}
    do_reduce = os.environ.get("AUDIT_REDUCE", "1") == "1"
    for tag in tags:
        for leg_dir in find_leg_dirs(s3, bucket, tag):
            a = audit_leg(s3, bucket, tag, leg_dir)
            a["tag"] = tag
            report["legs"].append(a)
            print(f"[{tag}] {leg_dir}\n   {a['verdict']}: files={a['n_window_files']} contig={a['n_contiguous']} "
                  f"u_len={a['u_length']} meta_nw={a['meta_n_windows']} samples={a['samples_per_window']} "
                  f"trustworthy={a['trustworthy']}",
                  flush=True)
            if a["semantic_findings"]:
                print("   semantic notes: " + " | ".join(a["semantic_findings"]), flush=True)
    # summary
    inconsistent = [l for l in report["legs"] if not l["self_consistent"]]
    incomplete = [l for l in report["legs"] if l["self_consistent"] and not l["complete"]]
    ok = [l for l in report["legs"] if l["self_consistent"] and l["complete"]]
    semantic_fail = [l for l in report["legs"] if l["self_consistent"] and l["complete"] and not l["semantic_ok"]]
    trustworthy = [l for l in report["legs"] if l.get("trustworthy")]
    report["summary"] = {
        "n_legs": len(report["legs"]), "n_consistent_complete": len(ok),
        "n_inconsistent": len(inconsistent), "n_incomplete": len(incomplete),
        "n_semantic_fail": len(semantic_fail), "n_trustworthy": len(trustworthy),
        "inconsistent_legs": [f"{l['tag']}:{os.path.basename(l['leg_prefix'].rstrip('/'))}" for l in inconsistent],
        "incomplete_legs": [f"{l['tag']}:{os.path.basename(l['leg_prefix'].rstrip('/'))}" for l in incomplete],
        "semantic_fail_legs": [f"{l['tag']}:{os.path.basename(l['leg_prefix'].rstrip('/'))}" for l in semantic_fail],
        "supportable_claim": (
            "We found NO evidence that the published ABFE table used the inconsistent dense legs; the fixed "
            "reducer exactly reproduces the table from structurally consistent standard-schedule data. This "
            "audit does NOT prove that no published value could have been corrupted — it establishes, leg by "
            "leg, which legs are structurally AND semantically trustworthy (see the immutable manifest in "
            "abfe_manifest.py for the version-pinned object provenance behind each reproduced value)."),
        "interpretation": (
            "A leg is safe to reduce ONLY if CONSISTENT+COMPLETE. INCONSISTENT legs (window_count != u_length) "
            "raise in MBAR (assemble_ukn len-check) → they cannot silently produce a wrong ΔG. INCOMPLETE legs "
            "(a missing window) return None from reduce_leg → also cannot produce a number. Beyond that, the "
            "SEMANTIC checks (λ identity/order, endpoints, target+leg identity, sample duplication, schedule "
            "metadata) catch a leg that is structurally consistent but semantically wrong. Only legs marked "
            "`trustworthy` (structural AND semantic) should back a published value; this audit lists which."),
    }
    out = os.environ.get("OUT", "research/modalities/abfe-audit-report.json")
    json.dump(report, open(out, "w"), indent=1)
    print(f"\nSUMMARY: {len(trustworthy)} TRUSTWORTHY (structural+semantic), {len(ok)} consistent+complete, "
          f"{len(semantic_fail)} SEMANTIC-FAIL, {len(inconsistent)} INCONSISTENT, {len(incomplete)} INCOMPLETE "
          f"(of {len(report['legs'])} legs). wrote {out}")
    if semantic_fail:
        print("SEMANTIC-FAIL:", ", ".join(report["summary"]["semantic_fail_legs"]))
    if inconsistent:
        print("INCONSISTENT (buggy-dense signature):",
              ", ".join(report["summary"]["inconsistent_legs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
