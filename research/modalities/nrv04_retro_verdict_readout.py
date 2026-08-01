#!/usr/bin/env python3
"""Pull the EMITTED NR-V04 retrospective R1 verdict out of S3 and give it a home in the repo.

★★ WHY THIS EXISTS (2026-08-01). The verdict is the entire deliverable of this lane, and until now its only
durable home was `s3://<bucket>/nrv04-retro-results/collect/nrv04-retro-collect-latest.json` —
`persist_retro_collect` fixed the worse problem (it used to live only on an ephemeral runner) but the result
is still invisible to anyone reading the repo. Measured consequence, the same day the panel completed: a
reader looking for the verdict found `nrv04-retro-criteria-audit.json` instead and read its
**pre-registered** reference set as the emitted outcome. Those are different documents — one says what the
test WOULD do, the other says what it DID — and a repo where only the first is present invites exactly that
substitution.

⚠ IT COPIES, IT NEVER COMPUTES. The scorer is `nrv04_retro_gate.verdict`, frozen and applied by
`retro_collect`; re-deriving a tier or a p here would be a second implementation of a preregistered rule
(CLAUDE.md rule 1) and could silently disagree with the run of record. This module reads the emitted object
and republishes it verbatim, carrying the S3 key and LastModified so the copy can always be traced back.

Read-only against S3. Rents nothing, computes no statistic.
"""
from __future__ import annotations

import json
import os
import sys

BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
PREFIX = os.environ.get("NRV04_RETRO_RESULT_PREFIX") or "nrv04-retro-results"
LATEST_KEY = f"{PREFIX}/collect/nrv04-retro-collect-latest.json"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nrv04-retro-verdict.json")

#: Keys copied from the collect readout. `legs` and `raw_keys` are deliberately NOT among them — they are
#: bulk, and the leg records already have a home under the lane prefix.
_CARRY = ("utc", "panel_complete", "panel_completable", "reachable_units", "quarantined_units",
          "n_expected", "n_landed", "have", "expected", "note", "nonconforming_records", "verdict")


def fetch(s3=None):
    """(readout, meta) from the durable `-latest` object. Raises if it cannot be read — an unreadable verdict
    must never be reported as an absent one (CLAUDE.md §4b)."""
    if s3 is None:
        import boto3
        s3 = boto3.client("s3")
    o = s3.get_object(Bucket=BUCKET, Key=LATEST_KEY)
    body = o["Body"].read().decode()
    lm = o.get("LastModified")
    return json.loads(body), {
        "source_key": f"s3://{BUCKET}/{LATEST_KEY}",
        "source_last_modified_utc": lm.strftime("%Y-%m-%dT%H:%M:%SZ") if lm else None,
        "source_bytes": len(body.encode()),
    }


def summarise(readout, meta):
    """The repo-side document: provenance + the carried fields, nothing recomputed. PURE."""
    doc = {
        "_what": "The EMITTED NR-V04 retrospective R1 verdict, copied verbatim from the lane's durable "
                 "collect readout. NOT the preregistered scoring description — that is "
                 "nrv04-retro-criteria-audit.json, which says what the test WOULD do, not what it DID.",
        "_scorer": "nrv04_retro_gate.verdict (frozen), applied by nrv04_vast_launch.retro_collect. Nothing "
                   "in this file is recomputed here.",
        "_amendment": "The authorized panel is AMENDMENT 4's: 16 legs, model-level n = 3 / 3 / 2. Read every "
                      "reference set below against §4.3, not against the pre-amendment enumeration.",
    }
    doc.update(meta)
    for k in _CARRY:
        if k in readout:
            doc[k] = readout[k]
    v = readout.get("verdict") or {}
    # A flat, quotable header — the fields a human asks for first. Copied, never derived.
    doc["headline"] = {
        "tier": v.get("tier"),
        "reason": v.get("reason"),
        "primary": v.get("primary"),
        "alpha": v.get("alpha"),
        "pairwise": v.get("pairwise"),
        "extension_triggered": v.get("extension_triggered") or v.get("extend"),
    }
    return doc


def main():
    try:
        readout, meta = fetch()
    except Exception as e:  # noqa: BLE001 — loud, and NOT written as "no verdict exists"
        print("[retro-verdict] COULD NOT READ %s: %s: %s — this is an unreadable verdict, NOT an absent one; "
              "the repo copy is left untouched" % (LATEST_KEY, type(e).__name__, e), flush=True)
        return 1
    doc = summarise(readout, meta)
    print(json.dumps(doc, indent=1, default=str)[:120000], flush=True)
    try:
        with open(OUT_JSON, "w") as fh:
            json.dump(doc, fh, indent=1, default=str)
        print(f"[retro-verdict] wrote {OUT_JSON}", flush=True)
    except OSError as e:
        print(f"[retro-verdict] could not write artifact: {e}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
