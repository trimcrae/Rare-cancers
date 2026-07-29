#!/usr/bin/env python3
# =============================================================================================================
# WHICH CHARGE SET DID EACH BANKED LEG'S **SYSTEM** ACTUALLY CARRY? — read it out of the setup cache
# =============================================================================================================
# THE QUESTION THIS FILE EXISTS TO SETTLE (handed over verbatim by the rc=1 diagnosis, 2026-07-29, and
# explicitly NOT resolved there). `nr4a3_rbfe.strip_foreign_partial_charges` documents a THIRD, SILENT failure
# mode: when a pose SDF arrives carrying a COMPLETE per-atom charge set, nothing raises, and OpenFF PREFERS
# user-supplied charges over the configured `partial_charge_method`. The molecule-level strip landed at
# 2026-07-28T00:54Z, so every leg that COMPLETED before that read its pose file with the charges live. That
# puts the banked legs under suspicion of having sampled on RELAXATION charges while their `leg.json` records
# `partial_charge_method = nagl`.
#
# ⚠ WHY IT IS NOT MERELY A LABELLING PROBLEM. ΔΔG_coop = ΔΔG_ternary − ΔΔG_binary. The charge model cancels
# out of that cycle ONLY IF BOTH ARMS USED THE SAME ONE. The two arms are configured independently
# (`use_preequil` is per-leg: the r0 ternary ran v2pe = pre-equilibrated, and a v1 binary arm never sees a
# relaxed SDF at all), so an arm-asymmetric inheritance is exactly the shape that breaks the cancellation.
#
# ★ THE DISCRIMINATING OBSERVATION, and why it is the System XML and not the log. A log line records what the
# protocol was CONFIGURED with; `_protocol()` prints `partial_charge_method = nagl` whether or not OpenFF then
# used it. The serialized hybrid `System` records what was actually PARAMETERIZED. The setup cache
# (`nr4a3_rbfe`, `RBFE_SETUP_CACHE_S3` / `RBFE_SETUP_CACHE_GCS`) persists exactly that object per
# (leg, direction, seed, charge, SETUP_CACHE_VERSION), so the question is answerable from stored bytes with no
# GPU and no re-run.
#
# ★★ AND THE STRONGEST TEST NEEDS NO REFERENCE CHARGE MODEL AT ALL. The two arms of a cycle transform the SAME
# ligand pair. If arm A's ligand charge vector and arm B's are BIT-IDENTICAL, the charge model cancels from
# that cycle whatever it was; if they differ, it does not. That comparison is internal to the stored artifacts
# and cannot be wrong about which nagl model file some host happened to resolve. The pose-SDF probe
# (`atom.dprop.PartialCharge`, the values a relaxed SDF carries in) then NAMES which set won.
#
# $0: reads only. It never rents, never nudges, never destroys, and it writes nothing to either object store.
# =============================================================================================================
from __future__ import annotations

import argparse
import bz2
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The SD tag `openff.toolkit.Molecule.to_rdkit()` stamps a charge model onto, and the one RDKit's SD parser
# expands into a per-atom property. ONE NAME, ONE HOME — imported from the guard it must never disagree with.
try:
    from nr4a3_rbfe import FOREIGN_CHARGE_PROPS
except Exception:  # noqa: BLE001 — the forensic must run on a bare runner with no openfe/rdkit
    FOREIGN_CHARGE_PROPS = ("atom.dprop.PartialCharge", "atom.dprop.PartialCharges")

# Exact-match tolerance for "is this the same charge". Charges are serialized at ~1e-7; two INDEPENDENT
# assignments of the same graph-based model agree to the last printed digit, and two DIFFERENT models
# disagree in the second decimal. 1e-6 therefore separates them with a factor of ~10^4 of margin — it is not
# a tuned threshold, it is the serialization precision.
TOL = 1e-6

# =============================================================================================================
# THE LEGS UNDER AUDIT — every leg whose ΔG is currently banked or quoted
# =============================================================================================================
# `tag` is NOT typed freshly here: it is `nr4a3_ternary_fep`'s own `"%s_%s_r%d" % (LEG_ID, DIRECTION, SEED)`,
# and `cache_dir` is `nr4a3_rbfe`'s own `"%s/%s__%s__%s" % (root, tag, charge, version)`. `store_root` and
# `version` come from the lane that ran the leg (ternary_vast_launch for S3 = v1pe; gpu-ternary-fep-gcp.yml for
# GCS = v1 when use_preequil=0, v2pe when 1). A wrong key here shows up as a MISS, never as a wrong answer.
S3_ROOT = "s3://sagemaker-us-east-2-646605541856/ternary-vast"
GCS_ROOT = "gs://project-a7ebde30-e2ed-4b8d-9a9-rbfe-ckpt/valB-6hax"

LEGS = [
    # ---- the r0 cycle the manuscript §2.11 / SI §S11 rest on (GCP lane, GCS-backed) ----
    {"id": "r0_ternary_fwd", "leg": "calib_hi_to_lo__ternary_vhl", "direction": "fwd", "seed": 0,
     "root": GCS_ROOT, "charge": "nagl", "versions": ["v2pe", "v1"], "arm": "ternary", "cycle": "r0",
     "banked": "ΔG_morph 47.511 ± 0.045 (SI S11); the ternary arm of the published ΔΔG_coop = −0.522"},
    {"id": "r0_ternary_rev", "leg": "calib_hi_to_lo__ternary_vhl", "direction": "rev", "seed": 0,
     "root": GCS_ROOT, "charge": "nagl", "versions": ["v2pe", "v1"], "arm": "ternary", "cycle": "r0",
     "banked": "the |ΔG_fwd + ΔG_rev| = 0.325 antisymmetry check (SI S11)"},
    {"id": "r0_binary_fwd", "leg": "calib_hi_to_lo__binary_vhl", "direction": "fwd", "seed": 0,
     "root": GCS_ROOT, "charge": "nagl", "versions": ["v1", "v2pe"], "arm": "binary", "cycle": "r0",
     "banked": "the binary arm — BOTH the original (ΔΔG_coop −0.534) and the restrained re-run (−0.522) "
               "carry this tag; they differ only by SETUP_CACHE_VERSION, so both versions are probed"},
    # ---- the edge_reps replicates (Vast lane, S3-backed) ----
    {"id": "r1_binary", "leg": "calib_hi_to_lo__binary_vhl", "direction": "fwd", "seed": 1,
     "root": S3_ROOT, "charge": "nagl", "versions": ["v1pe"], "arm": "binary", "cycle": "r1",
     "banked": "ΔG_morph 48.274 ± 0.109 (ternary-vast-watch.json, landed 2026-07-28T05:08:46Z)"},
    {"id": "r1_ternary", "leg": "calib_hi_to_lo__ternary_vhl", "direction": "fwd", "seed": 1,
     "root": S3_ROOT, "charge": "nagl", "versions": ["v1pe"], "arm": "ternary", "cycle": "r1",
     "banked": "the r1 ternary partner — its arm-mate is banked, so its charge set is decision-relevant"},
    {"id": "r2_binary", "leg": "calib_hi_to_lo__binary_vhl", "direction": "fwd", "seed": 2,
     "root": S3_ROOT, "charge": "nagl", "versions": ["v1pe"], "arm": "binary", "cycle": "r2",
     "banked": "ΔG_morph 47.951 ± 0.102"},
    {"id": "r2_ternary", "leg": "calib_hi_to_lo__ternary_vhl", "direction": "fwd", "seed": 2,
     "root": S3_ROOT, "charge": "nagl", "versions": ["v1pe"], "arm": "ternary", "cycle": "r2",
     "banked": "the r2 ternary partner"},
    # ---- the closure-triangle smoke (Vast lane) ----
    {"id": "tri_smoke_ternary", "leg": "calib_hi_to_lo2__ternary_vhl", "direction": "fwd", "seed": 0,
     "root": S3_ROOT, "charge": "nagl", "versions": ["v1pe"], "arm": "ternary", "cycle": "triangle_smoke",
     "banked": "ΔG 44.807 ± 0.582 (the closing edge, end to end)"},
]


# =============================================================================================================
# part A — object stores, read-only
# =============================================================================================================
def _is_s3(uri):
    return uri.startswith("s3://")


def _s3():
    import boto3
    return boto3.client("s3")


def _split(uri):
    rest = uri.split("://", 1)[1]
    b, _, k = rest.partition("/")
    return b, k


def listing(root):
    """Every object under `root`, as {key_relative_to_root: {"bytes":, "mtime":}}. Read-only."""
    out = {}
    if _is_s3(root):
        b, k = _split(root)
        pag = _s3().get_paginator("list_objects_v2")
        for page in pag.paginate(Bucket=b, Prefix=k.rstrip("/") + "/"):
            for o in page.get("Contents", []) or []:
                out[o["Key"][len(k.rstrip("/")) + 1:]] = {"bytes": o["Size"],
                                                          "mtime": o["LastModified"].isoformat()}
        return out
    r = subprocess.run(["gcloud", "storage", "ls", "--recursive", "--long", root.rstrip("/") + "/"],
                       capture_output=True, text=True)
    if r.returncode:
        return {"_error": (r.stderr or "")[-400:]}
    for ln in (r.stdout or "").splitlines():
        parts = ln.split()
        if len(parts) >= 3 and parts[-1].startswith("gs://"):
            key = parts[-1][len(root.rstrip("/")) + 1:]
            try:
                sz = int(parts[0])
            except ValueError:
                continue
            out[key] = {"bytes": sz, "mtime": parts[1]}
    return out


def download(uri, dest):
    """Fetch one object. Raises on failure — a MISS is a finding, not something to swallow."""
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    if _is_s3(uri):
        b, k = _split(uri)
        _s3().download_file(b, k, dest)
        return dest
    r = subprocess.run(["gcloud", "storage", "cp", uri, dest], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("cp %s: %s" % (uri, (r.stderr or "")[-300:]))
    return dest


# =============================================================================================================
# part B — what charges does a serialized OpenMM System carry?
# =============================================================================================================
def system_charges(path):
    """(base_charges, offsets) read out of the serialized System's NonbondedForce.

    ★ WHY BOTH. In a perses/OpenFE hybrid topology the alchemical ligand's electrostatics are carried as
    NonbondedForce PARTICLE PARAMETER OFFSETS keyed to `lambda_electrostatics_*`, with the base `q` holding
    one endpoint (often zero for a unique atom). Reading only the base column would report "the ligand has no
    charges" on a system that is fully charged — a false negative on the exact question being asked. So the
    offsets are read too, grouped by their global-parameter name, and every probe is run against BOTH columns.

    Streams via iterparse: the ternary hybrid is ~142k particles and the XML does not fit comfortably in
    memory on a free runner.
    """
    base, offsets = [], {}
    op = bz2.open if path.endswith(".bz2") else open
    with op(path, "rb") as fh:
        stack, in_nb, sect = [], False, None
        for ev, el in ET.iterparse(fh, events=("start", "end")):
            if ev == "start":
                stack.append(el.tag)
                if el.tag == "Force" and (el.get("type") or "") == "NonbondedForce":
                    in_nb = True
                elif in_nb and el.tag in ("Particles", "ParticleOffsets", "Exceptions", "ExceptionOffsets"):
                    sect = el.tag
                elif in_nb and sect == "Particles" and el.tag == "Particle":
                    q = el.get("q")
                    if q is not None:
                        base.append(float(q))
                elif in_nb and sect == "ParticleOffsets" and el.tag == "Offset":
                    nm = el.get("parameter") or el.get("name") or el.get("param") or "?"
                    idx = el.get("particle") or el.get("index") or el.get("p1") or "-1"
                    q = el.get("q") or el.get("chargeScale")
                    if q is not None:
                        offsets.setdefault(nm, []).append((int(idx), float(q)))
            else:
                if stack:
                    stack.pop()
                if el.tag in ("Particles", "ParticleOffsets", "Exceptions", "ExceptionOffsets"):
                    sect = None
                if el.tag == "Force" and (el.get("type") or "") == "NonbondedForce":
                    in_nb = False
                el.clear()
    for nm in offsets:
        offsets[nm] = sorted(offsets[nm])          # (particle_index, q), index-ordered
    return base, offsets


def endpoint_vectors(base, offsets):
    """(indices, q_A, q_B) for the alchemical region — BOTH λ endpoints, not just the one in the base column.

    ★ WHY THIS EXISTS, and it is the difference between measuring the reverse leg and guessing about it.
    A perses/OpenFE hybrid stores the λ=0 endpoint as the NonbondedForce base charge and the λ=1 endpoint as
    `base + offset`. So a pose-file probe against the base column can only ever see endpoint A — which is why
    the FORWARD legs (A = the charged record) matched and the REVERSE leg (A = the record the pose file
    carries no charges for) matched nothing. Reconstructing q_B makes the reverse leg measurable from the same
    bytes: its endpoints are the forward leg's, swapped.
    """
    idx, qb = [], {}
    for lst in offsets.values():
        for i, q in lst:
            qb[i] = qb.get(i, 0.0) + q
    idx = sorted(qb)
    qA = [base[i] for i in idx if i < len(base)]
    qB = [base[i] + qb[i] for i in idx if i < len(base)]
    return idx, qA, qB


def compare_endpoints(ea, eb, tol=TOL):
    """Do two Systems' alchemical endpoints describe the SAME charge assignment?

    Compared as SORTED MULTISETS, deliberately. A reverse leg builds its hybrid around the other molecule, so
    its atom ORDER is not the forward leg's; an element-wise comparison would report a difference that is a
    relabelling, not a charge model. The values themselves are what a charge model determines, and two
    different models disagree in the second decimal — four orders of magnitude above this tolerance.
    """
    out = {}
    for nm, (va, vb) in {"A_vs_A": (ea[1], eb[1]), "B_vs_B": (ea[2], eb[2]),
                         "A_vs_B": (ea[1], eb[2]), "B_vs_A": (ea[2], eb[1])}.items():
        sa, sb = sorted(va), sorted(vb)
        if len(sa) != len(sb):
            out[nm] = {"len_a": len(sa), "len_b": len(sb), "SAME": False, "why": "different atom counts"}
            continue
        mx = max((abs(p - q) for p, q in zip(sa, sb)), default=0.0)
        out[nm] = {"n": len(sa), "max_abs_diff": float(mx), "SAME": bool(mx <= tol)}
    return out


def _qs(offset_list):
    """Charges only, from an index-ordered [(particle_index, q), ...] offset column."""
    return [q for _i, q in offset_list]


def best_window(hay, needle, tol=TOL):
    """Best contiguous alignment of `needle` inside `hay`: (start, max_abs_diff, n_exact).

    Contiguity is the strong form of the test. A hybrid topology keeps a ligand's atoms in one index run, so a
    charge vector that came from the pose file appears as a RUN of exact matches, not as a scatter of
    coincidences. Returns start=-1 when `hay` is shorter than `needle`.
    """
    n, m = len(hay), len(needle)
    if m == 0 or n < m:
        return -1, None, 0
    best = (-1, float("inf"), 0)
    first = needle[0]
    cands = [i for i in range(n - m + 1) if abs(hay[i] - first) <= tol]
    if not cands:
        # NO EXACT ANCHOR -> no exact run is possible, so the remaining job is only to report HOW FAR the
        # closest alignment is. That is a diagnostic, not the verdict, and it must not cost more than the
        # verdict did: an exhaustive O(n·m) sweep of a 142k-particle system is ~15 s per probe per column and
        # there are dozens of both, which is how a $0 forensic turns into a job that times out and measures
        # NOTHING. Sample a bounded, evenly spaced set of starts instead.
        span = n - m + 1
        step = max(1, span // 2000)
        cands = range(0, span, step)
    for i in cands:
        mx, nex = 0.0, 0
        for j in range(m):
            d = abs(hay[i + j] - needle[j])
            if d <= tol:
                nex += 1
            if d > mx:
                mx = d
                if mx > 1e3:
                    break
        if mx < best[1]:
            best = (i, mx, nex)
        if mx <= tol:
            break
    return best


def probe(sysq, offs, vec, tol=TOL):
    """Run one candidate charge vector against every column of a System. Reports the strongest hit.

    ★ THE NEGATED VECTOR IS TESTED TOO, and it is not defensive padding. An offset column carries the
    DIFFERENCE between the two λ endpoints, so a ligand whose charges are `q` at λ=0 and 0 at λ=1 appears in
    that column as `−q`. Testing only `+q` would report "no match" on a system carrying exactly those charges
    — the same false negative shape as reading only the base column.
    """
    res = {"n": len(vec), "columns": {}}
    cols = {"base": sysq}
    for nm, v in offs.items():
        cols["offset:" + nm] = _qs(v)
    neg = [-x for x in vec]
    for nm, col in cols.items():
        st, mx, nex = best_window(col, vec, tol)
        stn, mxn, nexn = best_window(col, neg, tol)
        sign = "+"
        if (mxn if mxn is not None else float("inf")) < (mx if mx is not None else float("inf")):
            st, mx, nex, sign = stn, mxn, nexn, "-"
        res["columns"][nm] = {"len": len(col), "start": st, "sign": sign,
                              "max_abs_diff": (None if mx is None else float(mx)),
                              "n_exact_of_%d" % len(vec): nex,
                              "EXACT_RUN": bool(st >= 0 and mx is not None and mx <= tol)}
    res["matched"] = any(c["EXACT_RUN"] for c in res["columns"].values())
    res["best_column"] = min(res["columns"].items(),
                             key=lambda kv: (kv[1]["max_abs_diff"] if kv[1]["max_abs_diff"] is not None
                                             else float("inf")))[0] if res["columns"] else None
    return res


def _compare_offsets(offs_a, offs_b, tol=TOL):
    """Element-wise comparison of two Systems' alchemical charge columns — the verdict this file is FOR.

    The alchemical (ligand) atoms are exactly the ones carrying a `lambda_electrostatics_*` particle-parameter
    offset, so an offset column IS the ligand's charge signature, already separated from the protein/water/ion
    background by the engine itself. Two arms of one thermodynamic cycle transform the SAME ligand pair, so:
    identical columns ⇒ the charge model cancels from ΔΔG_coop whatever that model was; different columns ⇒
    it does not, and the cancellation argument fails.
    """
    out = {"columns": {}}
    for nm in sorted(set(offs_a) & set(offs_b)):
        va, vb = _qs(offs_a[nm]), _qs(offs_b[nm])
        if len(va) != len(vb):
            out["columns"][nm] = {"len_a": len(va), "len_b": len(vb),
                                  "IDENTICAL": False, "why": "different lengths"}
            continue
        mx = max((abs(p - q) for p, q in zip(va, vb)), default=0.0)
        out["columns"][nm] = {"len": len(va), "max_abs_diff": float(mx),
                              "n_exact": sum(1 for p, q in zip(va, vb) if abs(p - q) <= tol),
                              "IDENTICAL": bool(mx <= tol)}
    out["only_in_a"] = sorted(set(offs_a) - set(offs_b))
    out["only_in_b"] = sorted(set(offs_b) - set(offs_a))
    out["ARMS_SHARE_ONE_CHARGE_SET"] = bool(
        out["columns"] and all(c["IDENTICAL"] for c in out["columns"].values()))
    return out


# ★ AN ABSENT ARTIFACT IS A FINDING. Every non-"READ" status a leg can end with is named here so a report can
# separate "measured clean" from "could not be measured" — CLAUDE.md §4: "unmeasured" is a valid answer and is
# much better than a plausible story, but only if it is SAID rather than rendered as a blank.
UNMEASURED_STATUSES = ("NO SETUP CACHE", "MANIFEST CARRIES NO SYSTEM FILE",
                       "MANIFEST PRESENT BUT SYSTEM OBJECT UNREADABLE")


# =============================================================================================================
# part C — what charges does a POSE FILE carry in? (stdlib SDF, no RDKit — this must run on a bare runner)
# =============================================================================================================
def sdf_records(path):
    """[{name, n_atoms, charges:[...] or None}] for every record in an SDF. Pure text, no toolkit.

    Deliberately NOT RDKit: this is the measurement that says what the FILE contains, and reading it through
    the same library whose property-list expansion caused the incident would make the forensic evidence about
    itself. The tag name is imported from the guard (`FOREIGN_CHARGE_PROPS`) so the two cannot drift.
    """
    out = []
    with open(path, "r", errors="replace") as fh:
        text = fh.read()
    for block in text.split("$$$$"):
        if not block.strip():
            continue
        lines = block.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        if len(lines) < 4:
            continue
        name = lines[0].strip()
        n_atoms = None
        try:
            n_atoms = int(lines[3][0:3])
        except Exception:  # noqa: BLE001
            m = re.match(r"\s*(\d+)\s+\d+", lines[3] or "")
            n_atoms = int(m.group(1)) if m else None
        charges = None
        for i, ln in enumerate(lines):
            if ln.startswith(">") and any(p in ln for p in FOREIGN_CHARGE_PROPS):
                vals = []
                for nxt in lines[i + 1:]:
                    if not nxt.strip():
                        break
                    vals.extend(nxt.split())
                try:
                    charges = [float(v) for v in vals]
                except ValueError:
                    charges = None
                break
        out.append({"name": name, "n_atoms": n_atoms,
                    "n_charges": (None if charges is None else len(charges)),
                    "charges": charges})
    return out


def pose_sdfs(root, leg, seed, template="8G1Q", tmp="/tmp/cpf"):
    """Both pose files a leg could have read: the STAGE cache's and the PRE-EQUIL cache's, whichever exist.

    The host runs the pre-equil one when it exists (`run_ternary_leg.sh` step 2 / the GCP overlay), so a hit
    there is what a leg actually read. Keys mirror the lanes verbatim — see ternary_vast_launch.build_jobspec
    and gpu-ternary-fep-gcp.yml.
    """
    got = {}
    if _is_s3(root):
        cands = [("stage", f"{root}/stagecache/{leg}__{template}__seed{seed}__v1.tar", f"{leg}/ligands.sdf"),
                 ("preequil", f"{root}/preequilcache/{leg}__seed{seed}__nagl__ns0.5__v1.tar", "ligands.sdf")]
    else:
        cands = [("stage", f"{root}/stagecache/{leg}__{template}__seed{seed}__v1.tar", f"{leg}/ligands.sdf"),
                 ("preequil", f"{root}/preequilcache/{leg}__{template}__seed{seed}__v2.tar", "ligands.sdf")]
    for which, uri, member in cands:
        d = os.path.join(tmp, which, leg, str(seed))
        tar = os.path.join(d, "c.tar")
        info = {"uri": uri}
        try:
            download(uri, tar)
            with tarfile.open(tar) as tf:
                tf.extractall(d)
        except Exception as e:  # noqa: BLE001
            info["cache"] = "MISS(%s)" % type(e).__name__
            got[which] = info
            continue
        info["cache"] = "HIT"
        p = os.path.join(d, member)
        if not os.path.exists(p):
            hits = [os.path.join(dp, f) for dp, _dn, fs in os.walk(d) for f in fs if f == "ligands.sdf"]
            p = hits[0] if hits else None
        info["records"] = sdf_records(p) if p else "NO ligands.sdf IN TAR"
        got[which] = info
    return got


# =============================================================================================================
# part D — the audit
# =============================================================================================================
def audit(legs, tmp, keep_vectors=False):
    rows = []
    for spec in legs:
        tag = "%s_%s_r%d" % (spec["leg"], spec["direction"], spec["seed"])
        row = {"id": spec["id"], "tag": tag, "arm": spec["arm"], "cycle": spec["cycle"],
               "leg": spec["leg"], "direction": spec["direction"], "seed": spec["seed"],
               "banked": spec["banked"], "store": spec["root"], "setup_caches": {}}
        for ver in spec["versions"]:
            cache = "%s/setupcache/%s__%s__%s" % (spec["root"], tag, spec["charge"], ver)
            ent = {"cache_dir": cache}
            d = os.path.join(tmp, spec["id"], ver)
            try:
                download(cache + "/manifest.json", os.path.join(d, "manifest.json"))
            except Exception as e:  # noqa: BLE001
                ent["status"] = "NO SETUP CACHE (%s)" % type(e).__name__
                row["setup_caches"][ver] = ent
                continue
            man = json.load(open(os.path.join(d, "manifest.json")))
            ent["manifest_keys"] = {k: v[1] for k, v in man.items() if v[0] == "file"}
            sysfile = None
            for k, v in man.items():
                if v[0] == "file" and "system" in (v[1] or "").lower():
                    sysfile = v[1]
                    break
            if sysfile is None:
                ent["status"] = "MANIFEST CARRIES NO SYSTEM FILE"
                row["setup_caches"][ver] = ent
                continue
            local = os.path.join(d, sysfile)
            try:
                download(cache + "/" + sysfile, local)
            except Exception as e:  # noqa: BLE001
                ent["status"] = "MANIFEST PRESENT BUT SYSTEM OBJECT UNREADABLE (%s)" % type(e).__name__
                row["setup_caches"][ver] = ent
                continue
            ent["system_bytes"] = os.path.getsize(local)
            base, offs = system_charges(local)
            ent["status"] = "READ"
            ent["n_particles_nonbonded"] = len(base)
            ent["offset_columns"] = {k: len(v) for k, v in offs.items()}
            ep = endpoint_vectors(base, offs)
            ent["alchemical_atom_count"] = len(ep[0])
            ent["alchemical_index_range"] = [ep[0][0], ep[0][-1]] if ep[0] else None
            ent["endpoint_A_first_three"] = ep[1][:3]
            ent["endpoint_B_first_three"] = ep[2][:3]
            ent["_base"] = base
            ent["_offs"] = offs
            ent["_ep"] = ep
            row["setup_caches"][ver] = ent
        row["pose_files"] = pose_sdfs(spec["root"], spec["leg"], spec["seed"], tmp=os.path.join(tmp, "pose"))
        rows.append(row)
        print("[audit] %s: %s" % (spec["id"], json.dumps(
            {v: {k2: v2 for k2, v2 in e.items() if not k2.startswith("_")}
             for v, e in row["setup_caches"].items()})), flush=True)

    # ---- probe every System with every pose-file charge vector that exists anywhere in the audit ----
    probes = []
    for row in rows:
        for which, info in row["pose_files"].items():
            for rec in (info.get("records") or []):
                if isinstance(rec, dict) and rec.get("charges"):
                    probes.append({"source": "%s/%s/%s" % (row["id"], which, rec["name"]),
                                   "n": len(rec["charges"]), "vec": rec["charges"]})
    for row in rows:
        for ver, ent in row["setup_caches"].items():
            if ent.get("status") != "READ":
                continue
            ent["pose_charge_probes"] = {
                p["source"]: probe(ent["_base"], ent["_offs"], p["vec"]) for p in probes}
            ent["carries_a_pose_charge_set"] = any(
                r["matched"] for r in ent["pose_charge_probes"].values())

    # ---- ★ THE ARM-TO-ARM COMPARISON: does the cycle mix? ----
    # Needs NO reference charge model, which is the point. The alchemical (ligand) atoms are exactly the ones
    # carrying a `lambda_electrostatics_*` particle-parameter offset, so an offset column IS the ligand's
    # charge signature, already isolated from the protein/water/ion background by the engine itself. Two arms
    # of one cycle transform the SAME ligand pair: if their offset columns are element-wise identical the
    # charge model cancels from ΔΔG_coop whatever that model was, and if they are not, it does not.
    cycles, by_id = {}, {}
    for row in rows:
        for ver, ent in row["setup_caches"].items():
            if ent.get("status") == "READ":
                cycles.setdefault(row["cycle"], []).append(
                    (row["id"], row["arm"], row["direction"], ver, ent))
                by_id["%s/%s" % (row["id"], ver)] = (row, ent)
    cycle_report = {}
    for cyc, members in cycles.items():
        rep = {"members": ["%s (%s, %s, %s)" % (i, a, d, v) for i, a, d, v, _ in members], "pairwise": []}
        for x in range(len(members)):
            for y in range(x + 1, len(members)):
                ix, ax, dx, vx, ex = members[x]
                iy, ay, dy, vy, ey = members[y]
                if ax == ay:
                    continue                       # same arm — not a cycle pair
                # ★ ONLY SAME-DIRECTION ARMS FORM A CYCLE. Pairing a fwd arm with a rev one compares
                # `insert` against `delete` and reports a "difference" that is the alchemical direction, not
                # a charge model — a false positive on the exact question this file answers. The fwd/rev
                # relationship is measured separately, and correctly, by `directions` below.
                if dx != dy:
                    continue
                cmp_ = _compare_offsets(ex["_offs"], ey["_offs"])
                cmp_["endpoints"] = compare_endpoints(ex["_ep"], ey["_ep"])
                cmp_.update({"a": "%s/%s" % (ix, vx), "b": "%s/%s" % (iy, vy),
                             "arms": [ax, ay], "direction": dx})
                rep["pairwise"].append(cmp_)
        cycle_report[cyc] = rep

    # ---- ★ THE FORWARD/REVERSE PAIR, which the pose probe is structurally unable to see ----
    # A reverse leg's endpoint A is the molecule the relaxed pose file carries NO charges for, so no probe
    # can hit its base column. Reconstructing both endpoints makes it measurable anyway: if fwd and rev used
    # one charge assignment, rev's A endpoint is fwd's B endpoint and vice versa.
    dir_report = []
    for row_a in rows:
        for row_b in rows:
            if row_a["leg"] != row_b["leg"] or row_a["seed"] != row_b["seed"]:
                continue
            if not (row_a["direction"] == "fwd" and row_b["direction"] == "rev"):
                continue
            for va, ea in row_a["setup_caches"].items():
                for vb, eb in row_b["setup_caches"].items():
                    if ea.get("status") != "READ" or eb.get("status") != "READ":
                        continue
                    cmp_ = compare_endpoints(ea["_ep"], eb["_ep"])
                    dir_report.append({
                        "fwd": "%s/%s" % (row_a["id"], va), "rev": "%s/%s" % (row_b["id"], vb),
                        "endpoints": cmp_,
                        "SAME_CHARGE_ASSIGNMENT_SWAPPED": bool(
                            cmp_["A_vs_B"]["SAME"] and cmp_["B_vs_A"]["SAME"])})

    # ---- the per-leg verdict, stated so an absent artifact cannot render as a clean one ----
    verdicts = {}
    for row in rows:
        read = {v: e for v, e in row["setup_caches"].items() if e.get("status") == "READ"}
        if not read:
            why = "; ".join("%s: %s" % (v, e.get("status")) for v, e in row["setup_caches"].items())
            verdicts[row["id"]] = {"verdict": "UNMEASURED", "why": why, "banked": row["banked"]}
            continue
        for ver, ent in read.items():
            hits = [k for k, p in (ent.get("pose_charge_probes") or {}).items() if p["matched"]]
            # A leg whose λ=0 endpoint is the record the pose file carries NO charges for (every REVERSE
            # leg) can never be hit by a probe, and reporting that as "clean" would be the false negative
            # this whole file exists to avoid. Say WHY there is no hit, and point at what did measure it.
            if hits:
                v = "SYSTEM CARRIES A POSE-FILE CHARGE SET"
            elif row["direction"] == "rev":
                v = ("no pose-file charge vector CAN match: this leg's λ=0 endpoint is the record the "
                     "relaxed SDF carries no charges for — see `directions` for the endpoint reconstruction "
                     "that does measure it")
            else:
                v = "no pose-file charge vector matches this System"
            verdicts["%s/%s" % (row["id"], ver)] = {
                "verdict": v,
                "matching_pose_vectors": hits,
                "n_particles_nonbonded": ent.get("n_particles_nonbonded"),
                "alchemical_columns": ent.get("offset_columns"),
                "alchemical_index_range": ent.get("alchemical_index_range"),
                "endpoint_A_first_three": ent.get("endpoint_A_first_three"),
                "endpoint_B_first_three": ent.get("endpoint_B_first_three"),
                "banked": row["banked"]}

    if not keep_vectors:
        for row in rows:
            for ent in row["setup_caches"].values():
                ent.pop("_base", None)
                ent.pop("_offs", None)
                ent.pop("_ep", None)
    return {"legs": rows, "cycles": cycle_report, "directions": dir_report, "verdicts": verdicts}


# =============================================================================================================
# part E — is any OTHER lane exposed to the same inheritance?
# =============================================================================================================
# `nr4a3_rbfe._sdf_mol` is shared by every alchemical lane, so "did a banked result inherit charges" is a
# question about the POSE FILE each lane stages, not about the ternary code. The STEP 1 congeneric fan-out
# (RUNG 4) banks 14 ΔΔG values and stages a DOCKED SDF rather than a pre-equilibrated one — and a docked file
# is written by `nr4a3_dock.make_sdf`, which never assigns charges. That is a claim about code; this measures
# the actual staged object instead, because the fan-out has NO setup cache configured (no
# `RBFE_SETUP_CACHE_S3`), so its Systems were never persisted and the pose file is the only stored evidence
# there is. If it carries no charge tag, the lane had nothing to inherit and needs no marking.
FANOUT_POSE = "s3://sagemaker-us-east-2-646605541856/nr4a3-step1-fanout/stage/ligand"


def fanout_exposure(tmp="/tmp/cpf/fanout"):
    out = {"_what": "does the STEP 1 fan-out's staged pose file carry a charge model to inherit?",
           "_why_no_system": "the fan-out configures no setup cache, so no hybrid System was persisted; the "
                             "staged SDF is the only stored artifact that can answer this",
           "files": {}}
    b, k = _split(FANOUT_POSE)
    try:
        pag = _s3().get_paginator("list_objects_v2")
        keys = [o["Key"] for page in pag.paginate(Bucket=b, Prefix=k.rstrip("/") + "/")
                for o in page.get("Contents", []) or [] if o["Key"].endswith(".sdf")]
    except Exception as e:  # noqa: BLE001
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out
    for key in keys:
        dest = os.path.join(tmp, os.path.basename(key))
        try:
            download("s3://%s/%s" % (b, key), dest)
            recs = sdf_records(dest)
        except Exception as e:  # noqa: BLE001
            out["files"][key] = "UNREADABLE(%s)" % type(e).__name__
            continue
        out["files"][key] = {"n_records": len(recs),
                             "n_records_carrying_charges": sum(1 for r in recs if r.get("charges")),
                             "names": [r["name"] for r in recs[:8]]}
    out["ANY_CHARGE_TO_INHERIT"] = any(
        isinstance(v, dict) and v.get("n_records_carrying_charges") for v in out["files"].values())
    return out


def main():
    ap = argparse.ArgumentParser(description="Which charge set did each banked leg's System actually carry?")
    ap.add_argument("--list-caches", action="store_true",
                    help="enumerate every setup/stage/pre-equil cache object in both stores (settles which "
                         "SETUP_CACHE_VERSION each leg was built under, from presence rather than inference)")
    ap.add_argument("--audit", action="store_true", help="read the charges out of each leg's System XML")
    ap.add_argument("--tmp", default="/tmp/cpf")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    doc = {"_what": "which charge set each banked valB leg's serialized hybrid System actually carried",
           "_method": "read from the stored setup-cache System XML; $0, read-only, no GPU",
           "_tolerance": TOL}
    if a.list_caches:
        for root in (S3_ROOT, GCS_ROOT):
            ls = listing(root)
            keep = {k: v for k, v in ls.items()
                    if k.startswith(("setupcache/", "stagecache/", "preequilcache/"))}
            # setup caches are directories of many objects; report the DIRECTORIES, not every blob
            dirs = {}
            for k, v in keep.items():
                d = "/".join(k.split("/")[:2])
                g = dirs.setdefault(d, {"n_objects": 0, "bytes": 0, "first_mtime": v["mtime"],
                                        "last_mtime": v["mtime"]})
                g["n_objects"] += 1
                g["bytes"] += v["bytes"]
                g["first_mtime"] = min(g["first_mtime"], v["mtime"])
                g["last_mtime"] = max(g["last_mtime"], v["mtime"])
            doc.setdefault("caches", {})[root] = dirs
            print("\n########## %s ##########" % root, flush=True)
            for d in sorted(dirs):
                print("  %-90s n=%-4d %10.1f MB  %s .. %s"
                      % (d, dirs[d]["n_objects"], dirs[d]["bytes"] / 1e6,
                         dirs[d]["first_mtime"], dirs[d]["last_mtime"]), flush=True)
    if a.audit:
        doc.update(audit(LEGS, a.tmp))
        doc["fanout_exposure"] = fanout_exposure(os.path.join(a.tmp, "fanout"))
        print("\n########## PER-LEG VERDICT ##########", flush=True)
        print(json.dumps(doc["verdicts"], indent=2), flush=True)
        print("\n########## CYCLE ARM COMPARISON — does ΔΔG_coop mix charge models? ##########", flush=True)
        print(json.dumps(doc["cycles"], indent=2), flush=True)
        print("\n########## FORWARD vs REVERSE — one charge assignment, swapped? ##########", flush=True)
        print(json.dumps(doc["directions"], indent=2), flush=True)
        print("\n########## STEP 1 FAN-OUT — anything to inherit at all? ##########", flush=True)
        print(json.dumps(doc["fanout_exposure"], indent=2), flush=True)
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(doc, fh, indent=2, sort_keys=False)
        print("\n[forensic] wrote %s" % a.out, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
