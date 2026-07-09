#!/usr/bin/env python3
"""Dock the repurposing-survivor drug set into the off-target / anti-target panel — the promiscuity control.

Uses the IDENTICAL smina protocol as the NR4A dock (24 Angstrom box, exhaustiveness 8, num_modes 1) so each
drug's panel delta-G is directly comparable to its NR4A delta-G. Docks every (drug, target) pair, appending to
a JSONL checkpoint after each pair (continuous S3 upload) so a spot kill/timeout loses <=1 pair and resumes.

Env: PANEL_DIR (mounted channel with panel-manifest.json + <name>.pdb), CANDIDATE_JSON (survivors: name+smiles),
OUTPUT_DIR, RESUME_DIR, EXHAUSTIVENESS (default 8), PER_LIGAND_TIMEOUT (default 300), SMINA_CPU (default 1),
N_WORKERS (default nproc).
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import nr4a3_dock as dock

PANEL_DIR = os.environ.get("PANEL_DIR", ".")
CANDIDATE_JSON = os.environ.get("CANDIDATE_JSON")
OUT = os.environ.get("OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
RESUME = os.environ.get("RESUME_DIR", OUT)
EXHAUSTIVENESS = os.environ.get("EXHAUSTIVENESS", "8")
PER_LIGAND_TIMEOUT = int(os.environ.get("PER_LIGAND_TIMEOUT", "300"))
SMINA_CPU = os.environ.get("SMINA_CPU", "1")
N_WORKERS = int(os.environ.get("N_WORKERS", str(os.cpu_count() or 4)))

JSONL = os.path.join(OUT, "nr4a3-antitarget.jsonl")
SUMMARY = os.path.join(OUT, "nr4a3-antitarget.json")


def _dock(receptor_pdb, center, box, smi, label, lig_sdf, pose_sdf):
    kept = dock.make_sdf([(label, label, smi)], lig_sdf)
    if not kept:
        return None, "embed_failed"
    smina = dock._which("smina")
    if not smina:
        raise RuntimeError("smina not on PATH")
    cmd = [smina, "-r", receptor_pdb, "-l", lig_sdf,
           "--center_x", str(center[0]), "--center_y", str(center[1]), "--center_z", str(center[2]),
           "--size_x", str(box), "--size_y", str(box), "--size_z", str(box), "--cpu", SMINA_CPU,
           "--exhaustiveness", EXHAUSTIVENESS, "--num_modes", "1", "-o", pose_sdf]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=PER_LIGAND_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, "dock_timeout"
    if not os.path.exists(pose_sdf):
        return None, "no_pose"
    for b in open(pose_sdf).read().split("$$$$"):
        for j, ln in enumerate(b.splitlines()):
            if "minimizedAffinity" in ln:
                try:
                    return float(b.splitlines()[j + 1].strip()), "ok"
                except (ValueError, IndexError):
                    return None, "parse_failed"
    return None, "no_affinity"


def _load_candidates(path):
    d = json.load(open(path))
    out = []
    for c in d.get("candidates", d if isinstance(d, list) else []):
        nm, smi = c.get("name") or c.get("label"), c.get("smiles")
        if nm and smi:
            out.append((nm, smi))
    return out


def _done_pairs():
    done = set()
    for p in (os.path.join(RESUME, "nr4a3-antitarget.jsonl"), JSONL):
        if os.path.exists(p):
            for ln in open(p):
                ln = ln.strip()
                if ln:
                    try:
                        r = json.loads(ln)
                        done.add((r["label"], r["target"]))
                    except (ValueError, KeyError):
                        pass
    return done


def main():
    manifest = json.load(open(os.path.join(PANEL_DIR, "panel-manifest.json")))
    box = manifest.get("box_size", 24)
    targets = manifest["targets"]
    cands = _load_candidates(CANDIDATE_JSON)
    os.makedirs(OUT, exist_ok=True)
    done = _done_pairs()
    pairs = [(t, nm, smi) for t in targets for (nm, smi) in cands if (nm, t["name"]) not in done]
    print(f"panel {len(targets)} targets x {len(cands)} drugs = {len(targets)*len(cands)} pairs; "
          f"{len(done)} already done, {len(pairs)} to run (exh {EXHAUSTIVENESS}, box {box})", flush=True)

    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    lock_jsonl = open(JSONL, "a")

    def work(item):
        t, nm, smi = item
        rec = os.path.join(PANEL_DIR, f"{t['name']}.pdb")
        lig = os.path.join(tmp, f"{t['name']}_{nm}.lig.sdf")
        pose = os.path.join(tmp, f"{t['name']}_{nm}.pose.sdf")
        try:
            dg, note = _dock(rec, t["center"], box, smi, nm, lig, pose)
        except Exception as e:  # noqa: BLE001
            dg, note = None, str(e)[:80]
        for f in (lig, pose):
            try:
                os.remove(f)
            except OSError:
                pass
        return {"label": nm, "target": t["name"], "class": t.get("class"), "dG": dg, "note": note}

    n_ok = 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(work, it): it for it in pairs}
        for fut in as_completed(futs):
            r = fut.result()
            lock_jsonl.write(json.dumps(r) + "\n")
            lock_jsonl.flush()
            n_ok += 1
            if n_ok % 20 == 0:
                print(f"  [{n_ok}/{len(pairs)}] {r['target']}/{r['label']} dG={r['dG']}", flush=True)
    lock_jsonl.close()

    # pool into a per-drug summary: {label: {target: dG}}
    rows = {}
    for p in (os.path.join(RESUME, "nr4a3-antitarget.jsonl"), JSONL):
        if os.path.exists(p):
            for ln in open(p):
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                rows.setdefault(r["label"], {})[r["target"]] = r.get("dG")
    summary = {"panel": [t["name"] for t in targets], "box_size": box,
               "exhaustiveness": EXHAUSTIVENESS,
               "candidates": [{"label": k, "dG_by_target": v} for k, v in rows.items()]}
    json.dump(summary, open(SUMMARY, "w"), indent=2)
    print(f"wrote {SUMMARY}: {len(rows)} drugs x {len(targets)} targets", flush=True)


if __name__ == "__main__":
    main()
