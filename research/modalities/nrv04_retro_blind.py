#!/usr/bin/env python3
"""
NR-V04 RETROSPECTIVE holdout — arm-label BLINDING (prereg §8).

Leg results are written under opaque tokens so that any manual inspection while the panel is running (log
tails, S3 listings, monitoring) is ARM-BLIND: you can see that a leg is progressing without seeing whether it is
the degraded paralogue or a spared one.

WHAT THIS IS, PRECISELY — and what it is not (prereg §8, stated the same way in the manuscript):
  * It IS a procedural guard against incidental bias during monitoring, and a way to keep the unblinding EVENT
    explicit and timestamped rather than diffuse.
  * It is NOT adversarial blinding. This is a single-operator study; whoever generates the token map could
    invert it. The real guarantee is that the criteria, thresholds, statistical test and scoring CODE are frozen
    in git before any data exists (nrv04_retro_gate.py + its tests), not this module.
Do not let a result section describe this study as blinded without that caveat.

Mechanics: tokens are HMAC-SHA256(salt, arm_id) truncated — deterministic given the salt, so a rerun reproduces
the same mapping and a leg can always be re-associated. The salt is generated once and written to the key file;
the key file's SHA-256 is committed to the run manifest at panel launch, so a later swap of the mapping is
detectable.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets

TOKEN_LEN = 10
KEY_FILENAME = "nrv04-retro-blind-key.json"


def make_salt() -> str:
    """A fresh 128-bit salt. Called ONCE per panel, at launch, before any leg result exists."""
    return secrets.token_hex(16)


def token_for(arm_id: str, salt: str, token_len: int = TOKEN_LEN) -> str:
    """Deterministic opaque token for one arm. Same (arm, salt) -> same token, always."""
    digest = hmac.new(salt.encode(), arm_id.encode(), hashlib.sha256).hexdigest()
    return "arm_" + digest[:token_len]


def build_key(arm_ids, salt: str) -> dict:
    """The full arm <-> token mapping. Fails closed on a token collision (astronomically unlikely, but a silent
    collision would merge two arms' results, which must never happen quietly)."""
    fwd = {a: token_for(a, salt) for a in arm_ids}
    if len(set(fwd.values())) != len(fwd):
        raise ValueError("blind token collision — regenerate the salt")
    return {"salt": salt, "arm_to_token": fwd, "token_to_arm": {v: k for k, v in fwd.items()}}


def write_key(key: dict, path: str = KEY_FILENAME) -> str:
    """Persist the key and return its SHA-256 — the commitment recorded in the run manifest. Committing the
    HASH (not the key) at launch is what makes a post-hoc swap of the mapping detectable."""
    blob = json.dumps(key, indent=2, sort_keys=True)
    with open(path, "w") as f:
        f.write(blob + "\n")
    return hashlib.sha256(blob.encode()).hexdigest()


def key_digest(path: str = KEY_FILENAME) -> str:
    with open(path) as f:
        return hashlib.sha256(f.read().rstrip("\n").encode()).hexdigest()


def load_key(path: str = KEY_FILENAME) -> dict:
    with open(path) as f:
        return json.load(f)


def blind_leg_records(legs, key: dict):
    """Replace `arm_id` with its token in a list of leg records (the form the monitoring path sees)."""
    fwd = key["arm_to_token"]
    out = []
    for leg in legs:
        rec = dict(leg)
        rec["arm_id"] = fwd[leg["arm_id"]]
        rec["blinded"] = True
        out.append(rec)
    return out


def unblind_leg_records(legs, key: dict):
    """Map tokens back to arm ids — the UNBLINDING step, performed once, after all legs have landed and
    immediately before nrv04_retro_gate.verdict() is applied."""
    rev = key["token_to_arm"]
    out = []
    for leg in legs:
        rec = dict(leg)
        arm = leg["arm_id"]
        rec["arm_id"] = rev.get(arm, arm)      # already-unblinded records pass through unchanged
        rec["blinded"] = False
        out.append(rec)
    return out


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="NR-V04 retrospective blinding key (generate / digest / unblind).")
    ap.add_argument("--generate", action="store_true", help="make a fresh key for the frozen panel arms")
    ap.add_argument("--key", default=KEY_FILENAME)
    ap.add_argument("--unblind", default="", help="path to a blinded leg-records JSON to unblind")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    if args.generate:
        import nrv04_retro_panel as panel
        if os.path.exists(args.key):
            raise SystemExit(f"[blind] {args.key} already exists — refusing to overwrite an in-flight key")
        key = build_key([a.arm_id for a in panel.ARMS], make_salt())
        digest = write_key(key, args.key)
        print(json.dumps({"key_path": args.key, "sha256": digest,
                          "arms": sorted(key["arm_to_token"])}, indent=2))
        return 0
    if args.unblind:
        key = load_key(args.key)
        with open(args.unblind) as f:
            legs = json.load(f)
        recs = unblind_leg_records(legs, key)
        txt = json.dumps(recs, indent=2)
        if args.out:
            with open(args.out, "w") as f:
                f.write(txt + "\n")
        print(txt)
        return 0
    print(json.dumps({"key_sha256": key_digest(args.key)}, indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
