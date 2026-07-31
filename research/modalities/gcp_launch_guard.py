#!/usr/bin/env python3
"""Refuse to provision a DETACHED GCP leg that nothing is able to reap.

★ THE GAP THIS CLOSES, and why it is a launcher check rather than a monitoring one.

A GCP VM **cannot delete itself**. The in-VM EXIT trap fires and GCE refuses the call
(`Required 'compute.instances.delete' permission`, measured 2026-07-27 on
`gcp-ternary-30215419909` — the verbatim serial console is in `research/compute/gcp-gpu-facts.md` §6).
So the ONLY thing that removes a finished leg's VM is the control plane: the ternary watchdog's
DONE branch in `watchdog_run.sh`.

That branch is inside a loop over the **enabled** entries of `ternary-watch.json`
(`watchdog_run.sh`, the `python3 -c ... if w.get('enabled')` generator feeding the `while read`).
With no enabled entry for a running leg the watchdog takes its N=0 early exit, prints
`WATCHDOG ORPHAN VM, NOTHING WATCHING IT`, and **deliberately refuses to delete** — correctly, because
a watchdog that reaps whatever it does not recognise is a worse failure than the one it prevents.
`gcp-reap-vms.yml` is not a backstop either: it has no `schedule:` and never fires by itself.

So a detached `mode=run` dispatched with no enabled watch entry runs to its **create-time cap** —
`--max-run-duration=259200s`, 72 h on the on-demand branch — holding `GPUS_ALL_REGIONS = 1`, which is
every GCP GPU job on the account, and burning ~72 L4-hours of expiring trial credit. A red workflow is
the only signal.

**THE WATCH ENTRY IS THE TEARDOWN MECHANISM, NOT BOOKKEEPING.** That is the whole idea here: the
launcher will not buy a GPU until the thing that can switch it off exists. The check is $0, runs
before `gcloud compute instances create`, and cannot be forgotten the way a runbook step can.

★ WHY IT VALIDATES `main`'s COPY, NOT THE CHECKED-OUT ONE.

`ternary-leg-watchdog.yml` runs `actions/checkout@v4` with **no `ref`**, so it always reads the DEFAULT
BRANCH's `ternary-watch.json` regardless of which ref the leg was dispatched from. A leg launched from a
feature branch whose watch entry exists only on that branch is therefore unwatched in exactly the way
this guard exists to prevent — the branch-drift data-loss bug class of CLAUDE.md §7, where an artifact
lived on the only ref the running workflow does not read. The authoritative file is whatever `main`
holds; a checked-out copy that disagrees is reported as a WARNING, because it is a real hazard for the
*relaunch* path even when the reap is safe.

★ WHY THE COMPARISON IS EXACT STRING EQUALITY.

`_required_run_params` is `ternary-watch.json`'s own authoritative list (ONE FACT, ONE PLACE) and every
one of its members is a **literal component of the GCS commit prefix** or selects the setup cache:

    <seed>_dt<timestep_fs>fs_clig0_wu<warmup_timestep_fs>[_<commit_salt>][_rst][_dir<direction>]

`timestep_fs=2.0` and `timestep_fs=2` are DIFFERENT PREFIXES, so treating them as equal would bless a
watch entry that censuses a trajectory the running leg is not writing — which is how the watchdog would
raise a phantom SETUP STALL on a healthy leg, and relaunch the wrong prefix on a dead one. Numeric
coercion here would be a bug, not a convenience.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

# The four values that key the leg RESULT object `leg_<leg>_<dir>_r<seed>[_rst].json`, which is the
# object the watchdog's DONE branch `ls`es and therefore the only thing that decides whether a VM gets
# reaped. A mismatch on any of these means the entry is watching a different calculation entirely.
REAP_KEYING = ("leg_id", "direction", "seed", "restrain")

# Defaults applied to a watch entry that omits an optional key, matching watchdog_run.sh's own
# `w.get(...)` defaults exactly so this guard and the watchdog can never disagree about what an entry means.
ENTRY_DEFAULTS = {
    "commit_salt": "",
    "timestep_fs": "2.0",
    "warmup_timestep_fs": "",
    "use_preequil": "0",
    "restrain": "0",
}


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def required_params(doc: dict) -> list[str]:
    """The authoritative list, read from the file rather than restated here (CLAUDE.md rule 1)."""
    return list(doc.get("_required_run_params") or doc.get("_prefix_keying_params") or [])


def entry_value(entry: dict, key: str) -> str:
    return str(entry.get(key, ENTRY_DEFAULTS.get(key, ""))).strip()


def result_key(params: dict) -> str:
    rst = "_rst" if params.get("restrain") == "1" else ""
    return f"leg_{params['leg_id']}_{params['direction']}_r{params['seed']}{rst}.json"


def match(doc: dict, params: dict) -> tuple[list[dict], list[tuple[dict, list[str]]]]:
    """Return (fully matching enabled entries, near-misses with the fields that differ).

    A NEAR-MISS IS REPORTED SEPARATELY AND ON PURPOSE. "No entry at all" and "an entry for this leg
    whose timestep does not match what you dispatched" need completely different fixes, and an error
    that cannot tell them apart sends the operator to add a duplicate entry when the real problem is a
    typo in the one already there.
    """
    required = required_params(doc)
    exact: list[dict] = []
    near: list[tuple[dict, list[str]]] = []
    for entry in doc.get("watch", []):
        if not entry.get("enabled"):
            continue
        diffs = [k for k in required if entry_value(entry, k) != str(params.get(k, "")).strip()]
        if not diffs:
            exact.append(entry)
        elif not any(k in diffs for k in REAP_KEYING):
            # same result key -> the reap WOULD work, but the census/relaunch would not
            near.append((entry, diffs))
    return exact, near


def check(doc: dict, params: dict, where: str) -> tuple[bool, list[str]]:
    msgs: list[str] = []
    required = required_params(doc)
    if not required:
        return False, [
            f"::error title=WATCH LIST HAS NO REQUIRED-PARAM LIST::{where} declares neither "
            "`_required_run_params` nor `_prefix_keying_params`, so this guard cannot tell whether any "
            "entry reproduces the dispatched run. Refusing to provision rather than guessing."
        ]
    missing = [k for k in required if k not in params]
    if missing:
        return False, [
            f"::error title=LAUNCH GUARD CALLED WITHOUT {', '.join(missing)}::the watch list requires "
            f"{required}, and this invocation supplied no value for {missing}. Refusing to provision."
        ]

    exact, near = match(doc, params)
    if exact:
        note = exact[0].get("note", "")
        msgs.append(
            f"::notice title=WATCHER PRESENT::{where} has an enabled entry reproducing this dispatch "
            f"({result_key(params)}). That entry IS the teardown mechanism: the watchdog's DONE branch "
            f"reaps this VM once the result object lands. {note[:180]}"
        )
        return True, msgs

    detail = ""
    if near:
        entry, diffs = near[0]
        detail = (
            " AN ENTRY FOR THIS LEG EXISTS BUT DOES NOT REPRODUCE THE DISPATCH — it differs on "
            + ", ".join(
                f"{k}: entry={entry_value(entry, k)!r} vs dispatch={str(params.get(k, '')).strip()!r}"
                for k in diffs
            )
            + ". Those values are literal components of the GCS commit prefix, so the watchdog would "
            "census a trajectory this leg is not writing (phantom SETUP STALL) and relaunch the wrong "
            "prefix if it died. FIX THE ENTRY — do not add a second one."
        )
    enabled = [
        f"{e.get('leg_id')}/{e.get('direction')}/r{e.get('seed')}"
        for e in doc.get("watch", [])
        if e.get("enabled")
    ]
    msgs.append(
        "::error title=REFUSING TO PROVISION — NOTHING WOULD REAP THIS VM::"
        f"a DETACHED leg was dispatched ({result_key(params)}) but {where} has no enabled watch entry "
        f"that reproduces it (enabled entries: {enabled or 'NONE'})."
        + detail
        + " A GCP VM CANNOT DELETE ITSELF — the in-VM EXIT trap runs and GCE refuses it "
        "(gcp-gpu-facts.md §6) — so the watchdog's DONE branch is the only thing that removes a "
        "finished leg's VM, and it only ever looks at ENABLED entries. With none, the watchdog takes "
        "its idle exit, prints WATCHDOG ORPHAN VM and deliberately refuses to delete; gcp-reap-vms.yml "
        "has no schedule and never fires by itself. This VM would therefore run to its create-time "
        "--max-run-duration cap holding GPUS_ALL_REGIONS=1 (every GCP GPU job on the account) and "
        "burning expiring trial credit. FIX: add the entry to research/modalities/ternary-watch.json "
        "ON main with enabled=true and all of "
        f"{required}, then re-dispatch."
    )
    return False, msgs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--watch", required=True, help="AUTHORITATIVE watch list (main's copy)")
    ap.add_argument("--also-watch", help="the checked-out ref's copy, compared for divergence only")
    ap.add_argument("--where", default="main's ternary-watch.json")
    for key in ("leg-id", "seed", "direction", "commit-salt", "timestep-fs",
                "warmup-timestep-fs", "use-preequil", "restrain"):
        ap.add_argument(f"--{key}", default="")
    args = ap.parse_args(argv)

    params = {
        "leg_id": args.leg_id.strip(),
        "seed": args.seed.strip(),
        "direction": args.direction.strip(),
        "commit_salt": args.commit_salt.strip(),
        "timestep_fs": args.timestep_fs.strip(),
        "warmup_timestep_fs": args.warmup_timestep_fs.strip(),
        "use_preequil": args.use_preequil.strip(),
        "restrain": args.restrain.strip(),
    }

    path = pathlib.Path(args.watch)
    if not path.is_file():
        print(
            f"::error title=WATCH LIST MISSING::{args.where} ({path}) does not exist, so no watcher "
            "can be proven and nothing would reap this VM. Refusing to provision."
        )
        return 1
    try:
        doc = load(path)
    except Exception as exc:  # noqa: BLE001 — any parse failure is a refusal, not a traceback
        print(
            f"::error title=WATCH LIST UNREADABLE::could not parse {args.where} ({path}): {exc}. "
            "Refusing to provision, because an unreadable watch list is one the watchdog also cannot act on."
        )
        return 1

    ok, msgs = check(doc, params, args.where)
    for m in msgs:
        print(m)

    # DIVERGENCE IS A WARNING, NOT A REFUSAL. The reap is safe as long as main's copy matches, which is
    # what was just checked; a stale local copy only misleads a human reading the branch. Failing on it
    # would block a legitimate launch for a bookkeeping difference.
    if ok and args.also_watch:
        other = pathlib.Path(args.also_watch)
        if other.is_file():
            try:
                ok2, _ = check(load(other), params, "the checked-out ref's ternary-watch.json")
            except Exception:  # noqa: BLE001
                ok2 = False
            if not ok2:
                print(
                    "::warning title=WATCH LIST DIVERGES FROM main::main's copy authorises this launch "
                    "and the reap will work, but the checked-out ref's ternary-watch.json does not carry "
                    "a matching enabled entry. The watchdog only ever reads main (its checkout takes no "
                    "`ref`), so this is not a safety problem — it is branch drift, and CLAUDE.md §7 says "
                    "to reconcile it rather than let a branch be the only home of an artifact."
                )
    return 0 if ok else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
