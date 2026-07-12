#!/usr/bin/env python3
"""
Interruption-robust, NR4A3-ONLY drug-repurposing dock (Option-1 triage tier), PARALLEL within the job.

Docks a shard of the Broad Repurposing Hub library into the unbiased druggable-**release** NR4A3 Pocket-5,
**many drugs at a time** (a thread pool over drugs; each smina pinned to SMINA_CPU cores), appending a result
line to a JSONL checkpoint as *each* drug finishes. That checkpoint lives in the SageMaker managed-spot
checkpoint dir, so it is uploaded to S3 continuously and re-downloaded on a spot interruption or re-dispatch —
a kill loses at most the drugs in flight, and on start the driver skips every drug already recorded.

WHY parallel-in-the-job: the binding constraint is the account quota "instances across all spot training jobs"
(=10), NOT vCPUs. So the way to cut wall-clock is to make each instance do more work — run N concurrent docks
on a big-vCPU box — rather than launch more jobs. On a 16-vCPU box a 550-drug shard finishes in minutes.

dG here is a **screening prior, not an affinity**.

Env inputs:
  CANDIDATE_JSON, NR4A3_RECEPTOR, NR4A3_BOX_RES, OUTPUT_DIR, RESUME_DIR, TAG   (as before)
  EXHAUSTIVENESS       smina exhaustiveness (default 4)
  PER_LIGAND_TIMEOUT   seconds before a single smina dock is abandoned (default 300)
  N_WORKERS            concurrent docks (default = os.cpu_count()); each uses SMINA_CPU cores
  SMINA_CPU            cores per smina dock (default 1 — so N_WORKERS docks saturate the box)
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import nr4a3_dock as dock
import nr4a3_warhead as wh
import residue_map as rm
import repurpose_dock_core as core

OUT = os.environ.get("OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
RESUME = os.environ.get("RESUME_DIR", OUT)
TAG = os.environ.get("TAG", "shard")
NR4A3_RECEPTOR = os.environ.get("NR4A3_RECEPTOR")
NR4A3_BOX_RES = os.environ.get("NR4A3_BOX_RES", "")
CANDIDATE_JSON = os.environ.get("CANDIDATE_JSON")
EXHAUSTIVENESS = os.environ.get("EXHAUSTIVENESS", "4")
PER_LIGAND_TIMEOUT = int(os.environ.get("PER_LIGAND_TIMEOUT", "300"))
SMINA_CPU = os.environ.get("SMINA_CPU", "1")
N_WORKERS = int(os.environ.get("N_WORKERS", str(os.cpu_count() or 4)))
CHECKPOINT_EVERY_SUMMARY = int(os.environ.get("CHECKPOINT_EVERY_SUMMARY", "50"))

ENGAGEABLE_HANDLES = [406, 410, 484, 531, 534]   # divergent + pocket-facing (NR4A3 numbering)
CONSERVED_CV = [411, 481, 485]
LBD_FIRST_NR4A3 = 373

wh.OUT = OUT


def _pdb_resseqs(pdb):
    seen, out = set(), []
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                rs = int(line[22:26])
            except ValueError:
                continue
            if rs not in seen:
                seen.add(rs); out.append(rs)
    return out


def _box_residues(resseqs):
    """NR4A3_BOX_RES env, else the release manifest's box_residues for this receptor, else Pocket-5."""
    if NR4A3_BOX_RES.strip():
        return [int(x) for x in NR4A3_BOX_RES.split(",") if x.strip()]
    man = os.path.join(os.path.dirname(NR4A3_RECEPTOR), "nr4a3-release-druggable.json")
    if os.path.exists(man):
        try:
            m = json.load(open(man))
            want = os.path.basename(NR4A3_RECEPTOR)
            for r in m.get("receptors", []):
                if r.get("pdb") == want and r.get("box_residues"):
                    return list(r["box_residues"])
        except Exception:  # noqa: BLE001 — fall through to Pocket-5
            pass
    pos, _ = rm.resolve_positions(resseqs, range(406, 535), LBD_FIRST_NR4A3)
    return [resseqs[i] for i in pos]


def _load_candidates(path):
    """(label, smiles, meta) per drug, preserving the repurposing metadata for the results."""
    d = json.load(open(path))
    out = []
    for c in d.get("candidates", []):
        smi, name = c.get("smiles"), c.get("name")
        if not smi or not name or "error" in c:
            continue
        out.append((name, smi, {"drug": c.get("drug"), "moa": c.get("moa"),
                                 "phase": c.get("phase"), "target": c.get("target")}))
    return out, d


def _dock_one(receptor_pdb, center, smi, label, lig_sdf, pose_sdf):
    """Embed + smina-dock ONE drug (pinned to SMINA_CPU cores). Returns (dG or None, note); writes pose_sdf."""
    kept = dock.make_sdf([(label, label, smi)], lig_sdf)
    if not kept:
        return None, "embed_failed"
    smina = dock._which("smina")
    if not smina:
        raise RuntimeError("smina not on PATH")
    cmd = [smina, "-r", receptor_pdb, "-l", lig_sdf,
           "--center_x", str(center[0]), "--center_y", str(center[1]), "--center_z", str(center[2]),
           "--size_x", "24", "--size_y", "24", "--size_z", "24", "--cpu", SMINA_CPU,
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


def main():
    os.makedirs(OUT, exist_ok=True)
    if not NR4A3_RECEPTOR or not os.path.exists(NR4A3_RECEPTOR):
        _fail(f"NR4A3_RECEPTOR missing ({NR4A3_RECEPTOR})"); return
    if not CANDIDATE_JSON or not os.path.exists(CANDIDATE_JSON):
        _fail(f"CANDIDATE_JSON missing ({CANDIDATE_JSON})"); return

    # 1) receptor + box (once).
    import shutil
    conf = os.path.join(OUT, "nr4a3-opened.pdb")
    shutil.copy(NR4A3_RECEPTOR, conf)
    resseqs = _pdb_resseqs(conf)
    box_res = [rs for rs in _box_residues(resseqs) if rs in set(resseqs)]
    if not box_res:
        _fail("no NR4A3 box residues resolved"); return
    center, _ = wh.pocket_box(conf, box_res)
    h_res = [resseqs[i] for i in rm.resolve_positions(resseqs, ENGAGEABLE_HANDLES, LBD_FIRST_NR4A3)[0]]
    c_res = [resseqs[i] for i in rm.resolve_positions(resseqs, CONSERVED_CV, LBD_FIRST_NR4A3)[0]]
    print(f"[repurpose] receptor {os.path.basename(NR4A3_RECEPTOR)}: {len(resseqs)} res, "
          f"box on {len(box_res)} residues, {len(h_res)} handles, exh {EXHAUSTIVENESS}, "
          f"{N_WORKERS} workers x {SMINA_CPU} cpu", flush=True)

    # 2) candidates + resume set.
    cands, lib = _load_candidates(CANDIDATE_JSON)
    labels = [c[0] for c in cands]
    jsonl = os.path.join(OUT, f"{TAG}.results.jsonl")
    resume_jsonl = os.path.join(RESUME, f"{TAG}.results.jsonl")
    prior_lines = []
    if os.path.exists(resume_jsonl):
        prior_lines = open(resume_jsonl).read().splitlines()
        if os.path.abspath(resume_jsonl) != os.path.abspath(jsonl):
            with open(jsonl, "w") as fh:
                fh.write("\n".join(prior_lines) + ("\n" if prior_lines else ""))
    done = core.done_labels(prior_lines)
    todo = core.remaining(labels, done)
    by_label = {c[0]: c for c in cands}
    print(f"[repurpose] {TAG}: {len(labels)} drugs, {len(done)} already done, {len(todo)} to dock "
          f"({N_WORKERS}-way parallel)", flush=True)

    meta = {"tag": TAG, "receptor": os.path.basename(NR4A3_RECEPTOR), "source": lib.get("source"),
            "exhaustiveness": EXHAUSTIVENESS, "box_residues": box_res,
            "engageable_handles": ENGAGEABLE_HANDLES}

    # 3) parallel per-drug dock; append + flush as EACH drug finishes (thread-safe: append only in main thread).
    def _work(label):
        _lab, smi, m = by_label[label]
        lig = os.path.join(OUT, f"_lig_{label}.sdf")
        pose = os.path.join(OUT, f"_pose_{label}.sdf")
        try:
            dg, note = _dock_one(conf, center, smi, label, lig, pose)
            hc = wh.handle_contacts(conf, pose, h_res).get(label, 0) if dg is not None else 0
            cc = wh.handle_contacts(conf, pose, c_res).get(label, 0) if dg is not None else 0
        except Exception as e:  # noqa: BLE001 — one bad drug must never kill the shard
            dg, note, hc, cc = None, f"error:{e}", 0, 0
        if os.environ.get("KEEP_POSES") != "1":     # keep the box clean under high fan-out (default)
            for p in (lig, pose):
                try:
                    os.remove(p)
                except OSError:
                    pass
        return {"label": label, "drug": m["drug"], "moa": m["moa"], "phase": m["phase"],
                "smiles": smi, "dG_NR4A3": dg, "handle_contacts": hc, "conserved_contacts": cc, "note": note}

    t0, n = time.time(), 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex, open(jsonl, "a") as fh:
        futures = [ex.submit(_work, lab) for lab in todo]
        for fut in as_completed(futures):
            rec = fut.result()
            fh.write(json.dumps(rec) + "\n"); fh.flush(); os.fsync(fh.fileno())
            n += 1
            if n % 25 == 0 or n == len(todo):
                rate = n / max(1e-6, time.time() - t0)
                print(f"[repurpose] {TAG} {n}/{len(todo)} (~{rate:.1f} drug/s)", flush=True)
            if n % CHECKPOINT_EVERY_SUMMARY == 0:
                _write_summary(jsonl, meta, status="in_progress")

    _write_summary(jsonl, meta, status="ok")

    if os.environ.get("KEEP_POSES") == "1":
        # RBFE staging: assemble a combined docked_<receptor>.sdf (each pose retitled to its label) in OUT so
        # the checkpoint prefix is a ready RBFE receptor input (<r>-opened.pdb already written above). The
        # receptor tag defaults to nr4a3 (RBFE's RECEPTOR); override via DOCKED_RECEPTOR.
        rcpt = os.environ.get("DOCKED_RECEPTOR", "nr4a3")
        combined = os.path.join(OUT, f"docked_{rcpt}.sdf")
        n_written = 0
        with open(combined, "w") as cf:
            for label in [b for b in by_label]:
                pose = os.path.join(OUT, f"_pose_{label}.sdf")
                if not os.path.exists(pose):
                    continue
                for blk in open(pose).read().split("$$$$"):
                    blk = blk.strip("\n")
                    if not blk.strip():
                        continue
                    lines = blk.split("\n")
                    lines[0] = label                 # set the SDF title -> RBFE resolves the pose by _Name
                    cf.write("\n".join(lines) + "\n$$$$\n")
                    n_written += 1
        print(f"[repurpose] KEEP_POSES: wrote {combined} ({n_written} pose record(s)) for RBFE staging",
              flush=True)
    print(f"[repurpose] {TAG} DONE {len(todo)} drugs in {time.time() - t0:.0f}s", flush=True)


def _write_summary(jsonl, meta, status):
    rows = []
    for ln in open(jsonl).read().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except ValueError:
            continue
    res = core.summarize(rows, meta={**meta, "_status": status})
    with open(os.path.join(OUT, f"nr4a3-repurpose-{TAG}.json"), "w") as fh:
        json.dump(res, fh, indent=2)


def _fail(msg):
    with open(os.path.join(OUT, f"nr4a3-repurpose-{TAG}.json"), "w") as fh:
        json.dump({"_status": "error", "error": msg}, fh, indent=2)
    print("ERROR:", msg, file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic; do NOT exit non-zero so the
        import traceback       # continuously-uploaded JSONL checkpoint is preserved as the deliverable.
        _fail(f"{exc}\n{traceback.format_exc()[-1500:]}")
