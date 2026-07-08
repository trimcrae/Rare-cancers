#!/usr/bin/env python3
"""Pure helpers for the interruption-robust NR4A3-only repurposing dock.

The driver (`nr4a3_repurpose_dock.py`) docks one drug at a time and appends a JSON line per drug to a
results JSONL that lives in the SageMaker checkpoint dir (continuously synced to S3 + re-downloaded on a
spot restart). These are the pure, stdlib-only, unit-tested pieces of that loop:

  - `done_labels`   : which drugs are already recorded (resume set) — tolerant of a half-written trailing
                      line left by a spot kill mid-append.
  - `rank_rows`     : rank docked drugs best-first (most-negative NR4A3 dG, then most handle contacts).
  - `summarize`     : fold the JSONL rows into the ranked summary JSON the promote/MM-GBSA tier reads.

Kept free of RDKit/smina/IO so it imports and tests without the heavy dock env.
"""
import json


def done_labels(jsonl_lines):
    """Set of drug labels already persisted in a results JSONL (one JSON object per line).

    Skips blank lines and any line that does not parse — a spot interruption can truncate the final
    append mid-write, so the last line may be partial; that drug is simply re-docked on resume."""
    done = set()
    for ln in jsonl_lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            rec = json.loads(ln)
        except ValueError:
            continue                      # partial/corrupt trailing line from an interrupted write
        lab = rec.get("label")
        if lab:
            done.add(lab)
    return done


def remaining(all_labels, done):
    """Ordered labels still to dock (preserves library order; skips the resume set)."""
    ds = set(done)
    return [lab for lab in all_labels if lab not in ds]


def rank_rows(rows):
    """Docked rows best-first: most-negative NR4A3 dG, ties broken by more engageable-handle contacts.
    Rows with no dG (embed/dock failure or timeout) sink to the bottom, order otherwise preserved."""
    def key(r):
        dg = r.get("dG_NR4A3")
        return (dg is None, dg if dg is not None else 0.0, -(r.get("handle_contacts") or 0))
    return sorted(rows, key=key)


def summarize(rows, meta=None):
    """Fold docked rows into the ranked summary dict written as nr4a3-repurpose-<tag>.json.

    Reports how many drugs actually docked vs failed so a resumed/partial run is self-describing (a
    timeout leaves a valid partial with n_docked < n_total, never a silent truncation)."""
    ranked = rank_rows(rows)
    n_total = len(rows)
    n_docked = sum(1 for r in rows if r.get("dG_NR4A3") is not None)
    out = {
        "_note": "NR4A3-only repurposing triage: each drug docked into the unbiased druggable-release "
                 "NR4A3 Pocket-5. dG is a screening PRIOR, not an affinity; top hits promote to the "
                 "3-receptor + MM-GBSA + decoy-null selectivity tier.",
        "n_candidates": n_total,
        "n_docked": n_docked,
        "n_failed": n_total - n_docked,
        "candidates": ranked,
    }
    if meta:
        out.update(meta)
    return out
