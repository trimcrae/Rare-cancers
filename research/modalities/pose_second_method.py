#!/usr/bin/env python3
"""A SECOND, SCORING-INDEPENDENT POSE METHOD — rDock — run on the same systems as the first.

★★ WHY THIS EXISTS. `R5` ("the binding pose is right") is inherited by more of the board than anything
else — `Q1`, `Q2`, `Q5`, rung `5b-T`, and every pose-conditional sentence in the paper — and it is
currently UN-ATTRIBUTABLE. `pose-convergence-401.json` measured the spread of the six `denovo_401`
poses this program holds and found them not to converge, and its own decisive field is
`cross_method_evidence: NONE` — every one of those six is the SAME method (smina, top pose) run on a
different receptor conformer. A 7 A disagreement inside one method cannot be attributed to
conformational breadth, to a scoring failure, or to a genuinely multi-modal binding surface, because
there is nothing to attribute it AGAINST.

⛔ THE TRAP THIS MODULE IS BUILT TO AVOID, AND IT IS ALREADY IN THE RECORD. §3b.4 item 1 of the roadmap
records `V14`: BioEmu was sold as an orthogonal cross-check on `R1` and turned out to be orthogonal in
its SAMPLING while sharing the whole `C1`–`C5` detector chain — so a move in a shared configuration item
moves the original number and its "independent" confirmation TOGETHER AND IN THE SAME DIRECTION. An
orthogonal axis that shares a detector is a weaker corroboration than it reads as. So this module states,
per arm, which `C*` items it shares with the first method and which it does not, and the answer is
computed from the arm's definition rather than asserted in prose.

★ THE METHOD, AND WHY IT IS INDEPENDENT WHERE IT COUNTS.

    first method   smina  (an AutoDock Vina fork) via `nr4a3_warhead.dock_into`
                   SEARCH  : iterated-local-search Monte Carlo with BFGS local minimisation, inside an
                             axis-aligned box (24 A cube, exhaustiveness 8, num_modes 1).
                   SCORING : the Vina empirical function — gauss1, gauss2, repulsion, hydrophobic and
                             non-directional H-bond terms in interatomic distance, normalised by the
                             rotatable-bond count.
                   TYPING  : Vina's own X-Score-derived atom typing, read straight off the PDB/SDF.

    second method  rDock  (`rbcavity` + `rbdock`, conda-forge/bioconda build; version recorded at run
                   time, never typed here)
                   SEARCH  : a three-stage genetic algorithm -> Monte Carlo -> Simplex protocol
                             (`dock.prm`), restrained to a pre-computed CAVITY rather than to a box.
                   SCORING : rDock's function — a piecewise vdW term, an explicitly DIRECTIONAL polar
                             term over annotated donor/acceptor/ionic interaction types, an aromatic
                             term, a weighted-SASA desolvation term, plus intramolecular and cavity
                             restraint penalties. It shares no term, no functional form and no
                             parameter with Vina's.
                   TYPING  : Sybyl types + Gasteiger charges assigned by Open Babel from the same PDB.

    ⇒ The two share NO source code, NO scoring term, NO search algorithm and NO atom typing. What they
      deliberately DO share is the receptor coordinates, the ligand file, the evaluation frame and the
      pre-registered criterion — because a comparison that did not share those would be comparing two
      different questions. ⛔ Sharing a THRESHOLD is comparability; sharing a MEASUREMENT CHAIN is
      pseudo-independence. `V14` shared the chain. This does not.

★ WHAT A FAVOURABLE RESULT LICENSES, STATED BEFORE THE RUN.
    Only this: that two methods with disjoint scoring agree on the pose to within a stated tolerance.
    ⛔ NOT that the pose is correct. NOT that anything binds. NOT that any downstream free-energy or
    selectivity number inherits validity. A convergent wrong answer is still wrong, and both methods
    could share the same systematic error through the receptor conformer they are both given.

★ TWO PARTS, TWO QUESTIONS.

    PART A  `MODE=cross`  — the same system `pose-convergence-401.json` measured: `denovo_401` in the
            NR4A3 LBD, over all six receptor conformers that census holds. There is NO known answer
            here, so nothing is graded as correct; what is measured is INTER-METHOD agreement, in the
            same receptor frame, and whether the two methods disagree in the same DIRECTION the six
            smina poses already do.

    PART B  `MODE=panel` — the pre-registered apo/holo known-answer panel, where a crystallographic
            answer DOES exist, so every number can be reported in `C14`'s own vocabulary. rDock is run
            at the SAME boxes the first method used, through `apo_pose_recovery`'s own hook, and is
            graded by `apo_pose_recovery`'s own `score_pose`. It writes ONLY this module's artifact and
            never `apo-pose-recovery.json`.

⛔ NO CRITERION, BOX OR THRESHOLD IS TUNED HERE, AND NONE IS DEFINED HERE. `C14`'s 2.0 / 4.0 A bands and
the `_band()` function that applies them are IMPORTED from `apo_pose_recovery`, so this module cannot
drift from the line `R5` and `R14` both stand on. The search radius handed to rDock is DERIVED from the
pipeline's own box size (`pipeline_dock_params`), not chosen.

Output: pose-second-method.json. Free CPU, no GPU, no rental, $0.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "pose-second-method.json")
WORK = os.environ.get("SECOND_METHOD_WORK", os.path.join(HERE, "_second_method_work"))
#: ★ THE SECOND METHOD'S POSES ARE COMMITTED, NOT LEFT IN A RUNNER'S TEMP. `results/PROVENANCE.md`
#: already records the ORIGINAL docking-matrix poses as LOST to a bucket lifecycle rule, and the four
#: 8XTT re-dock legs are classified `scratch`. These files ARE the new evidence; a verdict whose
#: coordinates evaporate with the runner is a verdict nobody can re-grade. ~10 kB each.
POSE_DIR = os.path.join(HERE, "_pose_second_method_poses")

# --------------------------------------------------------------------------- rDock run configuration
#: Independent docking runs per system. rDock's own documentation runs 50–100 for a production dock and
#: 5–15 for a fast triage; 50 is the standard-depth figure and PART B uses fewer only because it docks
#: four boxes per pair rather than one. Neither is a threshold — they set how hard the SEARCH tries, and
#: the search effort is reported beside every number so a thin search cannot be mistaken for a result.
RDOCK_RUNS_CROSS = int(os.environ.get("RDOCK_RUNS_CROSS", "50"))
RDOCK_RUNS_PANEL = int(os.environ.get("RDOCK_RUNS_PANEL", "25"))
#: rDock IS seedable, unlike the pipeline's smina call. Fixed and declared, so this module's own numbers
#: are reproducible even though the arm it is compared against is one Monte-Carlo draw.
RDOCK_SEED = int(os.environ.get("RDOCK_SEED", "20260803"))
#: Cavity-mapper parameters. SMALL_SPHERE/LARGE_SPHERE/MIN_VOLUME are rDock's documented defaults for
#: the two-sphere method; they are the tool's settings, not a criterion of this program.
SMALL_SPHERE_A, LARGE_SPHERE_A = 1.0, 4.0
MIN_CAVITY_VOLUME_A3 = 100
GRIDSTEP_A = 0.5
#: The radius of the sphere rDock maps cavities inside, for the SITE-MATCHED arms. ⛔ DERIVED, never
#: typed: it is half the pipeline's own docking box edge, so both methods search the same volume about
#: the same centre. `pipeline_dock_params()` reads that edge out of `nr4a3_warhead.dock_into`'s source.
def site_matched_radius_A():
    import apo_pose_recovery as apr
    p = apr.pipeline_dock_params()
    return round(max(float(p.get(k, 24)) for k in ("size_x", "size_y", "size_z")) / 2.0, 3)


#: The radius for the RECEPTOR-WIDE arm, in which rDock is told nothing about where to look and picks
#: its own largest cavity. Large enough to enclose an NR4A LBD from its own centroid.
OWN_CAVITY_RADIUS_A = float(os.environ.get("RDOCK_OWN_CAVITY_RADIUS", "25.0"))

#: Wall-clock guards. A unit that blows its budget is recorded UNRUN with the budget named — never
#: silently dropped, and never allowed to take the rest of the panel down with it (CLAUDE.md §6).
UNIT_BUDGET_S = int(os.environ.get("SECOND_METHOD_UNIT_BUDGET_S", "1500"))
TOTAL_BUDGET_S = int(os.environ.get("SECOND_METHOD_TOTAL_BUDGET_S", "16200"))

_T0 = time.time()


def _time_left():
    return TOTAL_BUDGET_S - (time.time() - _T0)


# ==================================================================================================
# THE CRITERION — IMPORTED, NEVER DEFINED HERE.
# ==================================================================================================

def criterion():
    """`C14` and `C15`, read from the module that owns them. One home, per CLAUDE.md rule 1."""
    import apo_pose_recovery as apr
    return {
        "_C14": "the pose-recovery criterion — symmetry-corrected heavy-atom RMSD bands",
        "recovered_A": apr.RECOVER_RMSD_A,
        "partial_A": apr.PARTIAL_RMSD_A,
        "secondary_fnat": apr.FNAT_SUCCESS,
        "_C15": "the null-power rule for the pose panel",
        "n_null": apr.N_NULL,
        "null_power_max": apr.NULL_POWER_MAX,
        "_read_from": "apo_pose_recovery.RECOVER_RMSD_A / PARTIAL_RMSD_A / FNAT_SUCCESS / N_NULL / "
                      "NULL_POWER_MAX — this module defines no threshold of its own",
        "_vocabulary": "RECOVERED (<= recovered_A) · PARTIAL (<= partial_A) · NOT RECOVERED. ⛔ PARTIAL "
                       "IS NOT RECOVERY. Every number below is reported in these words.",
    }


def band(rms):
    """`C14`'s banding, applied by `apo_pose_recovery`'s own function."""
    import apo_pose_recovery as apr
    return apr._band(rms)


# ==================================================================================================
# THE INDEPENDENCE DECLARATION — computed from each arm's definition, not asserted.
# ==================================================================================================
#
# ⛔ READ THIS BEFORE READING ANY NUMBER. An arm's value is only as independent as its SHARED column is
# short. `V14`'s failure was that nobody wrote this table down for BioEmu, so a shared `C1`–`C5` chain
# read as an orthogonal axis for months.
#
# Meanings:
#   REQUIRED  — shared on purpose. Removing it would make the two methods answer different questions,
#               so it is not a defect; it IS the reason a change to that item moves both numbers.
#   AVOIDABLE — shared only in this arm; another arm in this artifact does not share it. That other arm
#               is what separates "the two methods agree" from "the two methods were pointed the same
#               way".
#   NOT SHARED— the second method does not touch it at all.

C_ITEMS_BY_ARM = {
    "site_matched": {
        "REQUIRED": {
            "C14": "the recovery criterion. Both methods are graded by the same 2.0/4.0 A bands — that "
                   "is comparability, not a shared instrument. ⚠ It is also the coupling §3b.4 item 5 "
                   "records: the same line produces V3's INCONCLUSIVE and V21's panel_readable=false.",
            "C15": "the random-in-box null and its power line. ⛔ ENGINE-INDEPENDENT BY CONSTRUCTION — "
                   "`apo_pose_recovery.random_in_box_null` places the CRYSTAL ligand at random inside "
                   "the box and never docks anything, so its power is a property of (box, molecule, "
                   "criterion). rDock inherits the panel's null verbatim and could not have its own.",
        },
        "AVOIDABLE": {
            "C5": "the site's own definition — NR4A3's Pocket-5 lining set, transferred onto the "
                  "receptor. This arm hands rDock the SAME centre smina was given, which is the whole "
                  "point: holding the site fixed is what isolates search+scoring. The "
                  "`receptor_wide` arm below does not share it.",
        },
        "NOT SHARED": {
            "C1": "D* — the druggability threshold. rDock's cavity mapper has no druggability score.",
            "C2": "the cavity-selection rule. Not consulted: the centre is handed over.",
            "C3": "the cavity acceptance gate. Not consulted.",
            "C4": "the fpocket build. rDock's two-sphere/grid mapper is not fpocket.",
        },
    },
    "fpocket_box": {
        "REQUIRED": {"C14": "as above.", "C15": "as above."},
        "AVOIDABLE": {
            "C4": "the fpocket build — this arm docks into the box fpocket's top-ranked pocket defines, "
                  "so it shares the DETECTOR that drew the box (and only that).",
        },
        "NOT SHARED": {
            "C1": "D* is not applied by `apo_pose_recovery.fpocket_boxes`, which ranks by fpocket's own "
                  "druggability and alpha-sphere count — verified in source, not assumed.",
            "C2": "the cavity-selection rule is `pocket_tracking.match_pocket`; this ranking is not it.",
            "C3": "the acceptance gate is not applied on this path either.",
            "C5": "Pocket-5 is not used to draw this box.",
        },
    },
    "receptor_wide": {
        "REQUIRED": {"C14": "as above.", "C15": "as above."},
        "AVOIDABLE": {},
        "NOT SHARED": {
            "C1": "no druggability threshold exists in rDock's mapper.",
            "C2": "rDock picks its own largest cavity by VOLUME; the frozen best-matching rule is not "
                  "consulted and cannot be, because there is no reference site in this arm.",
            "C3": "no acceptance gate.",
            "C4": "not fpocket.",
            "C5": "⭑ THE POINT OF THIS ARM. Nothing about NR4A3's Pocket-5 reaches it: rDock is given "
                  "the receptor and its own centroid and finds a cavity by itself. It is the only arm "
                  "here that shares no site-selection configuration with the first method at all.",
        },
        "_measured_limitation": (
            "⛔ AND IT DOES NOT DELIVER A SITE ON THIS FOLD — measured 2026-08-03, before the panel ran. "
            "rDock's two-sphere mapper on an NR4A3 LBD inside a 25 Å sphere returns ONE region of "
            "10369 Å³ with extent 47×46×47.5 Å: the whole concave envelope, which any ligand centroid "
            "lies inside trivially and which no affordable run count can sample. So the arm that owes "
            "the pipeline nothing is ALSO the arm that cannot answer the site question, and every arm "
            "that CAN be graded shares the site with the first method. ⇒ **this comparison is "
            "independent in SCORING, SEARCH and ATOM TYPING, and deliberately not in SITE SELECTION** — "
            "the site question has its own instrument (`apo-pose-site-in-regime.json`). Each arm's own "
            "`cavity_degeneracy` records whether this happened on that receptor."),
    },
    "oracle_box": {
        "REQUIRED": {"C14": "as above.", "C15": "as above."},
        "AVOIDABLE": {},
        "NOT SHARED": {"C1": "—", "C2": "—", "C3": "—", "C4": "—",
                       "C5": "the box is centred on the crystallographic ligand itself, so no site "
                             "selection of any kind is involved. ⛔ Decomposition only, never a "
                             "headline — the same rule `C3` (the control, not the config item) carries "
                             "in the pre-registered panel."},
    },
}

#: `C6` is a PART-A-only inheritance and belongs to the RECEPTOR, not to either docking method.
C6_NOTE = ("⚠ `C6` (the receptor-frame selection criterion) is inherited by BOTH methods on the two "
           "metadynamics-opened receptors and by NEITHER on the four experimental 8XTT NMR conformers — "
           "it is a property of the receptor a pose was generated in, not of the engine that placed the "
           "ligand. So a cross-method agreement measured on an 8XTT conformer is free of `C6`; one "
           "measured on `dock/metad-opened/*` is not, and §3b.2 records `C6` as CONTESTED.")


# ==================================================================================================
# rDOCK PLUMBING. Every failure returns a refusal with the tool's own stderr attached; nothing here
# guesses why something did not run (CLAUDE.md §4).
# ==================================================================================================

def rdock_tools():
    """Resolve rDock + Open Babel, or return a refusal naming exactly what is missing.

    `RDOCK_ROOT` lets CI install rDock into its own micromamba prefix WITHOUT putting that prefix on
    PATH — which matters, because rDock pulls a python of its own and a prefix on PATH would shadow the
    interpreter that holds rdkit. Falls back to PATH for a local checkout."""
    root = os.environ.get("RDOCK_ROOT")
    cand_dirs = [os.path.join(root, "bin")] if root else []
    found = {}
    for exe in ("rbcavity", "rbdock"):
        p = None
        for d in cand_dirs:
            if os.path.exists(os.path.join(d, exe)):
                p = os.path.join(d, exe)
                break
        found[exe] = p or shutil.which(exe)
    obabel = os.environ.get("OBABEL") or (
        (os.path.join(root, "bin", "obabel") if root and os.path.exists(os.path.join(root, "bin", "obabel"))
         else None) or shutil.which("obabel"))
    missing = [k for k, v in found.items() if not v] + ([] if obabel else ["obabel"])
    if missing:
        return None, "second method UNRUN — not on PATH and not under RDOCK_ROOT=%r: %s" % (
            root, ", ".join(missing))
    env = dict(os.environ)
    rbt = os.environ.get("RBT_ROOT")
    if not rbt and root:
        for cand in (os.path.join(root, "share", "rDock"), os.path.join(root, "share", "rdock")):
            if os.path.isdir(cand):
                rbt = cand
                break
    if rbt:
        env["RBT_ROOT"] = rbt
    if root:
        env["LD_LIBRARY_PATH"] = os.path.join(root, "lib") + ":" + env.get("LD_LIBRARY_PATH", "")
        # Open Babel finds its data through env vars that a conda ACTIVATION script normally sets. This
        # prefix is deliberately NOT activated and NOT on PATH (it carries a python of its own, which
        # would shadow the interpreter holding rdkit), so the two variables are set here from the
        # prefix's own layout. An absent data dir makes obabel emit an empty MOL2 with no error, which
        # would look like a receptor problem.
        import glob as _glob
        for var, pattern in (("BABEL_DATADIR", os.path.join(root, "share", "openbabel", "*")),
                             ("BABEL_LIBDIR", os.path.join(root, "lib", "openbabel", "*"))):
            if not env.get(var):
                hits = sorted(p for p in _glob.glob(pattern) if os.path.isdir(p))
                if hits:
                    env[var] = hits[-1]
    ver = ""
    try:
        pr = subprocess.run([found["rbdock"]], capture_output=True, text=True, env=env, timeout=120)
        for ln in (pr.stdout + pr.stderr).splitlines():
            if "Executable:" in ln or "Library:" in ln:
                ver += ln.strip() + "  "
    except Exception as e:                                    # noqa: BLE001
        ver = "version unread: %s" % e
    obver = ""
    try:
        pr = subprocess.run([obabel, "-V"], capture_output=True, text=True, env=env, timeout=120)
        obver = (pr.stdout + pr.stderr).strip().splitlines()[0] if (pr.stdout or pr.stderr) else ""
    except Exception as e:                                    # noqa: BLE001
        obver = "version unread: %s" % e
    return {"rbcavity": found["rbcavity"], "rbdock": found["rbdock"], "obabel": obabel,
            "env": env, "rdock_version": ver.strip(), "openbabel_version": obver,
            "RBT_ROOT": env.get("RBT_ROOT")}, None


def to_mol2(pdb_path, out_mol2, tools):
    """Receptor PDB -> Sybyl-typed MOL2, which is the only receptor format rDock reads."""
    pr = subprocess.run([tools["obabel"], "-ipdb", pdb_path, "-omol2", "-O", out_mol2],
                        capture_output=True, text=True, env=tools["env"], timeout=600)
    if not os.path.exists(out_mol2) or os.path.getsize(out_mol2) < 100:
        return None, "obabel produced no usable MOL2: %s" % (pr.stderr or pr.stdout)[-400:]
    return out_mol2, None


def write_prm(path, mol2, center, radius, title):
    text = (
        "RBT_PARAMETER_FILE_V1.00\n"
        "TITLE %s\n\n"
        "RECEPTOR_FILE %s\n"
        "RECEPTOR_FLEX 3.0\n\n"
        "SECTION MAPPER\n"
        "    SITE_MAPPER RbtSphereSiteMapper\n"
        "    CENTER (%.4f,%.4f,%.4f)\n"
        "    RADIUS %.2f\n"
        "    SMALL_SPHERE %.2f\n"
        "    LARGE_SPHERE %.2f\n"
        "    MAX_CAVITIES 1\n"
        "    MIN_VOLUME %d\n"
        "    VOL_INCR 0.0\n"
        "    GRIDSTEP %.2f\n"
        "END_SECTION\n\n"
        "SECTION CAVITY\n"
        "    SCORING_FUNCTION RbtCavityGridSF\n"
        "    WEIGHT 1.0\n"
        "END_SECTION\n"
        % (title, os.path.basename(mol2), center[0], center[1], center[2], radius,
           SMALL_SPHERE_A, LARGE_SPHERE_A, MIN_CAVITY_VOLUME_A3, GRIDSTEP_A))
    with open(path, "w") as fh:
        fh.write(text)
    return path


def make_cavity(prm_path, tools, cwd, timeout=None):
    """`rbcavity -was` — writes the .as docking site beside the prm. Returns (info, why).

    ⚠ THE TIMEOUT IS A REFUSAL, NOT AN EXCEPTION. Cavity mapping cost scales with the sphere volume, so
    the receptor-wide arm is ~9× the site-matched one; a raise here would lose the WHOLE pair's
    second-method block rather than the one arm that ran long."""
    t0 = time.time()
    try:
        pr = subprocess.run([tools["rbcavity"], "-was", "-r", os.path.basename(prm_path)],
                            capture_output=True, text=True, env=tools["env"], cwd=cwd,
                            timeout=timeout or UNIT_BUDGET_S)
    except subprocess.TimeoutExpired:
        return None, ("rbcavity exceeded its %ds budget mapping this sphere — UNRUN, not failed"
                      % (timeout or UNIT_BUDGET_S))
    out = pr.stdout + pr.stderr
    as_file = prm_path[:-4] + ".as"
    if not os.path.exists(as_file):
        return None, "rbcavity wrote no docking site: %s" % out.strip()[-500:]
    info = {"n_cavities": 0}
    for ln in out.splitlines():
        s = ln.strip()
        if s.startswith("Total volume"):
            try:
                info["total_volume_A3"] = round(float(s.split()[2]), 2)
            except (IndexError, ValueError):
                pass
        if s.startswith("Cavity #"):
            info["n_cavities"] += 1
            for part in s.split(";"):
                part = part.strip()
                if part.startswith("Vol="):
                    try:                      # "Vol=1376.88 A^3" — the unit is part of the token
                        info.setdefault("cavity_volume_A3", round(float(part[4:].split()[0]), 2))
                    except (ValueError, IndexError):
                        pass
                if part.startswith("Center="):
                    try:
                        info.setdefault("cavity_center", [
                            round(float(v), 3) for v in part[7:].strip("()").split(",")])
                    except ValueError:
                        pass
                if part.startswith("Extent="):
                    try:
                        info.setdefault("cavity_extent_A", [
                            round(float(v), 2) for v in part[7:].strip("()").split(",")])
                    except ValueError:
                        pass
    info["elapsed_s"] = round(time.time() - t0, 1)
    return info, None


#: A mapped "cavity" whose mean extent reaches this fraction of the RECEPTOR'S OWN bounding box is not a
#: pocket — it is the whole concave envelope, merged into one region by the two-sphere method. ⛔ A
#: REPORTING flag that gates nothing: it removes no arm, it labels one. Measured separation on this fold
#: is 0.93 (envelope) against 0.44 (a real pocket), so nothing turns on where inside that gap it sits.
ENVELOPE_FRAC = 0.85


def bbox_extent(points):
    if not points:
        return None
    return [round(max(p[i] for p in points) - min(p[i] for p in points), 2) for i in range(3)]


def cavity_degeneracy(info, receptor_extent_A):
    """Did the mapper return a SITE, or the whole surface? Measured, because it decides what an arm means.

    ⛔ MEASURED ON 2026-08-03, BEFORE THE PANEL RAN, AND IT IS NOT HYPOTHETICAL: rDock's two-sphere
    mapper, given an NR4A3 LBD and a 25 Å sphere on its own Cα centroid, returns ONE region of
    **10369 Å³** with extent **47×46×47.5 Å** against a receptor Cα box of 47.7×45.9×59.8 Å — the whole
    concave envelope of the fold. A ligand centroid lies inside that trivially, so the arm cannot carry a
    SITE verdict; and a 10^4 Å³ search volume is under-sampled at any run count this test can afford, so
    its RMSD is a statement about sampling before it is one about scoring.
    ⛔ THE FIX IS NOT TO SHRINK THE SPHERE UNTIL A POCKET APPEARS — that would be choosing the site after
    seeing the answer, which is the tuning this whole panel is pre-registered against. The radius stays
    blind and the degeneracy is reported.
    ⚠ The comparison is against the RECEPTOR's box and not the SEARCH SPHERE's, because a real pocket
    fills a small sphere too: at radius 12 the NR4A1 site cavity spans 23×22×21 Å, which is ~96 % of that
    sphere's diameter and only ~44 % of the protein."""
    ext = (info or {}).get("cavity_extent_A")
    if not ext or len(ext) != 3 or not receptor_extent_A or len(receptor_extent_A) != 3:
        return {"is_whole_surface_envelope": None,
                "_why": "no cavity extent and/or no receptor extent recorded — UNREAD, not absent"}
    frac = [round(e / r, 3) for e, r in zip(ext, receptor_extent_A) if r]
    mean_frac = round(sum(frac) / len(frac), 3) if frac else None
    env = mean_frac is not None and mean_frac >= ENVELOPE_FRAC
    return {
        "is_whole_surface_envelope": bool(env),
        "cavity_extent_A": ext, "receptor_ca_extent_A": receptor_extent_A,
        "extent_over_receptor": frac, "mean_extent_over_receptor": mean_frac,
        "_flag_at": ENVELOPE_FRAC, "_gates_nothing": True,
        "_reads": ("⛔ NOT A SITE — the mapped region is the size of the whole protein (mean extent %s of "
                   "the receptor's own box, %s Å³). This arm carries NO site verdict, and its RMSD is a "
                   "statement about sampling that volume before it is one about scoring."
                   % (mean_frac, (info or {}).get("cavity_volume_A3"))
                   if env else
                   "the mapper returned a bounded region (mean extent %s of the receptor's box), so this "
                   "arm is about a cavity the tool actually chose" % mean_frac)}


def run_rbdock(prm_path, ligand_sd, out_root, n_runs, tools, cwd, seed=RDOCK_SEED, timeout=None):
    """`rbdock` -> [(score, mol), ...] sorted best-first, or (None, why). Never raises."""
    from rdkit import Chem
    t0 = time.time()
    try:
        pr = subprocess.run([tools["rbdock"], "-r", os.path.basename(prm_path), "-p", "dock.prm",
                             "-n", str(n_runs), "-i", ligand_sd, "-o", out_root, "-s", str(seed)],
                            capture_output=True, text=True, env=tools["env"], cwd=cwd,
                            timeout=timeout or UNIT_BUDGET_S)
    except subprocess.TimeoutExpired:
        return None, "rbdock exceeded its %ds unit budget — UNRUN, not failed" % (timeout or UNIT_BUDGET_S)
    sd = os.path.join(cwd, out_root + ".sd")
    if not os.path.exists(sd):
        return None, "rbdock wrote no poses: %s" % (pr.stdout + pr.stderr).strip()[-500:]
    poses = []
    for m in Chem.SDMolSupplier(sd, removeHs=True, sanitize=True):
        if m is None:
            continue
        try:
            poses.append((float(m.GetProp("SCORE")), m))
        except (KeyError, ValueError):
            continue
    if not poses:
        return None, "rbdock's SD file held no scorable pose"
    poses.sort(key=lambda t: t[0])
    return {"poses": poses, "n_poses": len(poses), "elapsed_s": round(time.time() - t0, 1),
            "best_score": round(poses[0][0], 4),
            "score_spread": _spread([p[0] for p in poses])}, None


def _keep_pose(poses, name):
    """Write the run's poses into the committed pose directory, BEST FIRST; return a repo-relative path.

    ⛔ SORTED, AND THAT IS A BUG FIX, NOT A CONVENIENCE (measured 2026-08-03). `rbdock` writes its poses
    in RUN order, not in score order — on the 8XTT-model2 system record 1 scored **+10.795** while the
    best of the 50 scored **−18.519**. Two readers here took "the first molecule in the file" and were
    therefore comparing run #1 rather than the best pose. The tell was that a 5-run job and a 50-run job
    at the same seed produced BYTE-IDENTICAL cross-conformer numbers, which a deeper search cannot do:
    run #1 is the same in both. Sorting at the point of writing means the file's order and the in-memory
    ranking cannot disagree again, for any future reader.

    ⚠ All poses are kept, not just the best — the run-to-run spread IS the second method's own measure of
    how hard the search had to look, and dropping it would hide a thin search behind a single number."""
    from rdkit import Chem
    try:
        os.makedirs(POSE_DIR, exist_ok=True)
        dst = os.path.join(POSE_DIR, name)
        w = Chem.SDWriter(dst)
        for score, m in sorted(poses, key=lambda t: t[0]):     # sorted HERE, not at the call site
            m.SetProp("SCORE", "%.4f" % score)
            w.write(m)
        w.close()
        return os.path.relpath(dst, REPO)
    except Exception:                                         # noqa: BLE001 — never fail the science
        return None


def best_from_sd(path):
    """The best-scoring pose in an SD file, read by SCORE and never by file position."""
    from rdkit import Chem
    best = None
    for m in Chem.SDMolSupplier(path, removeHs=True, sanitize=True):
        if m is None:
            continue
        try:
            s = float(m.GetProp("SCORE"))
        except (KeyError, ValueError):
            continue
        if best is None or s < best[0]:
            best = (s, m)
    return best[1] if best else None


def _spread(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return {"n": 0, "min": None, "median": None, "max": None, "mean": None}
    n = len(vals)
    med = vals[n // 2] if n % 2 else 0.5 * (vals[n // 2 - 1] + vals[n // 2])
    return {"n": n, "min": round(vals[0], 3), "median": round(med, 3), "max": round(vals[-1], 3),
            "mean": round(sum(vals) / n, 3)}


def _centroid(points):
    n = float(len(points))
    return tuple(sum(p[i] for p in points) / n for i in range(3))


def _heavy(mol):
    conf = mol.GetConformer()
    return [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
            for i, a in enumerate(mol.GetAtoms()) if a.GetAtomicNum() > 1]


def in_frame_rmsd(mol_a, mol_b):
    """Symmetry-corrected heavy-atom RMSD **without re-aligning** — the same kernel, and the same
    reasoning, as `pose_convergence_401.symmetry_rmsd`: `GetBestRMS` would superpose the two ligands
    onto each other and throw away the placement, which is the only thing being measured."""
    from rdkit.Chem import rdMolAlign
    try:
        return round(float(rdMolAlign.CalcRMS(mol_a, mol_b)), 3), None
    except Exception as e:                                    # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)


def internal_rmsd(mol_a, mol_b):
    """The CONFORMER half of a disagreement, so a reader is never asked to take the split on trust."""
    from rdkit import Chem
    from rdkit.Chem import rdMolAlign
    try:
        return round(float(rdMolAlign.GetBestRMS(Chem.Mol(mol_a), Chem.Mol(mol_b))), 3), None
    except Exception as e:                                    # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)


def part_a(tools, runs=None):
    """rDock every receptor `pose-convergence-401.json` holds, and compare method to method.

    ⛔ THERE IS NO KNOWN ANSWER IN THIS PART. Nothing here is graded as correct; `C14`'s bands are used
    only as the shared VOCABULARY for how far apart two placements are, which is exactly what they
    measure. A pair inside `recovered_A` means the two methods put the molecule in the same place to
    within the line the program elsewhere calls recovery — never that either is right."""
    import nr4a3_8xtt_benchmark as bm
    import pose_convergence_401 as pc
    runs = RDOCK_RUNS_CROSS if runs is None else runs
    radius = site_matched_radius_A()
    out = {
        "_asks": "Do a scoring-independent method and the pipeline's own method put denovo_401 in the "
                 "same place, in the same receptor frame?",
        "_no_known_answer": "⛔ THIS PART GRADES NOTHING AS CORRECT. Both methods could be wrong "
                            "together; agreement here is a statement about the two methods, not about "
                            "the pose. The known-answer question is PART B.",
        "_site_definition": "rDock maps its cavity inside a sphere of radius %.2f A centred on the "
                            "Pocket-5 Ca centroid of THAT receptor. ⛔ The radius is DERIVED from the "
                            "pipeline's own box edge (`pipeline_dock_params`), so both methods search "
                            "the same volume about the same centre." % radius,
        "_C6": C6_NOTE,
        "n_rdock_runs_per_system": runs, "rdock_seed": RDOCK_SEED,
        "systems": [], "refusals": [],
    }
    loaded = []
    for src in pc.SOURCES:
        rec, ref = pc.load_source(src)
        if rec is None:
            out["refusals"].append(ref)
            continue
        loaded.append(rec)
    out["n_sources_readable"] = len(loaded)
    out["n_sources_known"] = len(pc.SOURCES)
    if not loaded:
        out["_status"] = "UNRUN — no readable pose source"
        return out

    work = os.path.join(WORK, "cross")
    os.makedirs(work, exist_ok=True)
    dock_prm = _stage_dock_prm(tools, work)
    if dock_prm is None:
        out["_status"] = "UNRUN — rDock's dock.prm protocol file is not readable under RBT_ROOT=%r" % (
            tools.get("RBT_ROOT"),)
        return out

    lig_sd, lig_why = _ligand_from_pose(loaded[0]["mol"], os.path.join(work, "denovo_401.sd"))
    if lig_sd is None:
        out["_status"] = "UNRUN — %s" % lig_why
        return out
    out["_ligand"] = {"label": pc.LIGAND_LABEL, "smiles": loaded[0].get("smiles"),
                      "_prepared": "a fresh ETKDGv3 conformer built from the census SMILES, NOT the "
                                   "smina pose — starting rDock from the pose it is being compared "
                                   "against would bias the comparison toward agreement."}

    rows = []
    for rec in loaded:
        if _time_left() < UNIT_BUDGET_S:
            out["refusals"].append({"id": rec["id"], "stage": "budget",
                                    "evidence": "total budget %ds spent before this system — UNRUN, "
                                                "not failed" % TOTAL_BUDGET_S})
            continue
        row = _part_a_system(rec, lig_sd, tools, work, radius, runs, bm, pc)
        rows.append(row)
        out["systems"] = rows
        _checkpoint({"part_a_partial": out})
    out["systems"] = rows

    ok = [r for r in rows if r.get("cross_method_rmsd_A") is not None]
    # ⭑ THE SCALE, MEASURED ON THIS MOLECULE, so "6.8 A" is readable rather than merely large. Same
    # kernel `pose-convergence-401.json` uses, recomputed here rather than quoted (rule 1).
    scale = pc.scale_reference(loaded[0]["mol"]) if loaded else {}
    out["scale_reference"] = scale
    out["cross_method_same_frame"] = {
        "_asks": "In each receptor's OWN frame — no superposition, nothing to fudge — how far is the "
                 "second method's best pose from the first method's committed pose?",
        "n_systems": len(ok),
        "rmsd_A": _spread([r["cross_method_rmsd_A"] for r in ok]),
        "centroid_distance_A": _spread([r.get("cross_method_centroid_distance_A") for r in ok]),
        "internal_conformer_rmsd_A": _spread(
            [r.get("cross_method_internal_conformer_rmsd_A") for r in ok]),
        "bands": {b: sum(1 for r in ok if r.get("cross_method_band") == b)
                  for b in ("RECOVERED", "PARTIAL", "NOT RECOVERED")},
        "_reads": "counted in `C14`'s own words. ⛔ RECOVERED here means 'the two methods placed it "
                  "within the recovery line of each other', NOT that either placement is correct.",
    }
    out["orientation_or_location"] = _decompose(out["cross_method_same_frame"], scale)
    # the second method's own cross-conformer spread, measured the same way the first method's was
    out["within_second_method_spread"] = _cross_conformer_spread(rows, loaded, bm, pc)
    return out


def _decompose(cm, scale):
    """WHERE vs WHICH WAY ROUND — the two disagreements a single RMSD cannot tell apart.

    ⛔ These are readings against MEASURED scales, not thresholds: `flip_rmsd_A` is this molecule's own
    cost of being turned end-for-end in place, and `random_reorient_mean_A` is the ceiling for
    'same location, orientation carries no information'. Both come from
    `pose_convergence_401.scale_reference` and neither gates anything."""
    rms = (cm.get("rmsd_A") or {}).get("median")
    cen = (cm.get("centroid_distance_A") or {}).get("median")
    internal = (cm.get("internal_conformer_rmsd_A") or {}).get("median")
    flip = scale.get("flip_rmsd_A")
    rnd = scale.get("random_reorient_mean_A")
    length = scale.get("length_A")
    out = {"median_rmsd_A": rms, "median_centroid_distance_A": cen,
           "median_internal_conformer_rmsd_A": internal,
           "molecule_length_A": length, "flip_rmsd_A": flip, "random_reorient_mean_A": rnd}
    if rms is None or cen is None:
        out["_reads"] = "not decomposable — no comparable pair"
        return out
    parts = []
    if flip is not None and cen is not None and cen < (flip or 0) / 2.0 and rms >= 0.75 * flip:
        parts.append("SAME LOCATION, DIFFERENT ORIENTATION — the median centroid separation (%.2f A) is "
                     "small beside a median RMSD (%.2f A) that is ~the cost of turning this molecule "
                     "end-for-end in place (%.2f A). The two methods are arguing about which way round "
                     "it sits, not about which pocket." % (cen, rms, flip))
    elif cen is not None and rms is not None and cen >= 0.5 * rms:
        parts.append("DIFFERENT LOCATION — the disagreement is carried by the centroid (%.2f A of a "
                     "%.2f A RMSD), so the two methods are not placing the molecule in the same "
                     "sub-site." % (cen, rms))
    else:
        parts.append("MIXED — %.2f A of the %.2f A median RMSD is centroid separation; the rest is "
                     "orientation and conformer." % (cen, rms))
    if internal is not None and rms is not None and internal >= 0.5 * rms:
        parts.append("⚠ AND THE CONFORMER IS IN PLAY: the two methods do not even agree on the "
                     "molecule's own shape (median internal RMSD %.2f A of %.2f A), so this is not "
                     "purely a placement disagreement." % (internal, rms))
    elif internal is not None:
        parts.append("The conformer is NOT the explanation — median internal RMSD %.2f A against a "
                     "%.2f A in-frame RMSD, so both methods found similar shapes and put them "
                     "differently." % (internal, rms))
    out["_reads"] = " ".join(parts)
    return out


def _part_a_system(rec, lig_sd, tools, work, radius, runs, bm, pc):
    """One receptor: map the cavity, dock, and compare to the committed first-method pose."""
    rid = rec["id"].replace("/", "_")
    d = os.path.join(work, rid)
    os.makedirs(d, exist_ok=True)
    row = {"id": rec["id"], "kind_first_method": rec["kind"],
           "receptor_provenance": rec.get("receptor_provenance"),
           "receptor": rec["receptor"], "first_method_pose": rec["poses"],
           "first_method_score_kcalmol": rec.get("docking_score_kcalmol"),
           "inherits_C6": "metadynamics" in (rec.get("receptor_provenance") or "").lower()}
    res = rec["residues"]
    p5 = [r for r in bm.POCKET5 if r in res and res[r].get("ca")]
    row["n_pocket5_mapped"] = len(p5)
    row["n_pocket5_source"] = len(bm.POCKET5)
    if len(p5) < 3:
        row["why"] = "only %d Pocket-5 Ca on this receptor — no site to centre on" % len(p5)
        return row
    center = _centroid([res[r]["ca"] for r in p5])
    row["site_center"] = [round(v, 3) for v in center]
    rec_path = rec["receptor"] if os.path.isabs(rec["receptor"]) else os.path.join(REPO, rec["receptor"])
    mol2, why = to_mol2(rec_path, os.path.join(d, "rec.mol2"), tools)
    if mol2 is None:
        row["why"] = why
        return row
    prm = write_prm(os.path.join(d, "rec.prm"), mol2, center, radius, rid)
    info, why = make_cavity(prm, tools, d)
    if info is None:
        row["why"] = why
        return row
    row["cavity"] = info
    shutil.copy(lig_sd, os.path.join(d, "lig.sd"))
    # ⚠ EXPLICIT, not left to rDock's search path. `-p dock.prm` resolves against the cwd and only THEN
    # against $RBT_ROOT/data/scripts — so without this copy the protocol in force depends on which of the
    # two rDock happened to find, and two runs could use different protocols with nothing saying so.
    shutil.copy(os.path.join(work, "dock.prm"), os.path.join(d, "dock.prm"))
    res_, why = run_rbdock(prm, "lig.sd", "out", runs, tools, d)
    if res_ is None:
        row["why"] = why
        return row
    row["n_rdock_poses"] = res_["n_poses"]
    row["rdock_best_score"] = res_["best_score"]
    row["rdock_score_spread"] = res_["score_spread"]
    row["rdock_elapsed_s"] = res_["elapsed_s"]
    best = res_["poses"][0][1]
    row["best_pose_sd"] = _keep_pose(res_["poses"], "cross_%s.sd" % rid)
    rms, why = in_frame_rmsd(best, rec["mol"])
    row["cross_method_rmsd_A"] = rms
    row["cross_method_band"] = band(rms)
    if rms is None:
        row["why"] = why
    irms, _ = internal_rmsd(best, rec["mol"])
    row["cross_method_internal_conformer_rmsd_A"] = irms
    row["cross_method_centroid_distance_A"] = round(
        math.dist(_centroid(_heavy(best)), _centroid(_heavy(rec["mol"]))), 3)
    # what the SECOND method's own runs did among themselves, in the same frame — the second method's
    # internal spread is the fair comparator for the first method's, and it is measured, not assumed.
    others = [p[1] for p in res_["poses"][1:]]
    self_rms = [in_frame_rmsd(best, m)[0] for m in others]
    row["second_method_self_agreement_A"] = _spread(self_rms)
    row["second_method_top_vs_runner_up_A"] = self_rms[0] if self_rms else None
    # ⭑ and how far is the second method's best pose from the FIRST method's box centre? A pose that
    # left the site entirely is a different finding from one that stayed and turned round.
    row["rdock_pose_to_site_center_A"] = round(math.dist(_centroid(_heavy(best)), center), 3)
    row["first_method_pose_to_site_center_A"] = round(
        math.dist(_centroid(_heavy(rec["mol"])), center), 3)
    return row


def _cross_conformer_spread(rows, loaded, bm, pc):
    """The second method's own pose spread ACROSS receptors, by the first method's own procedure.

    ⛔ THE COMPARATOR MUST BE MEASURED, NOT REMEMBERED. `pose-convergence-401.json` owns the first
    method's spread; this recomputes the SAME quantity for the second method, using
    `pose_convergence_401`'s superposition and RMSD kernels, so the two are commensurable. The first
    method's figure is NOT restated here — the artifact is pointed at instead (CLAUDE.md rule 1)."""
    by_id = {r["id"]: r for r in rows}
    have = [rec for rec in loaded
            if by_id.get(rec["id"], {}).get("best_pose_sd")
            and by_id[rec["id"]].get("cross_method_rmsd_A") is not None]
    out = {"_asks": "Does the SECOND method converge across receptor conformers any better than the "
                    "first did? Same superposition (Pocket-5 Ca), same symmetry-corrected RMSD kernel.",
           "_first_method_home": "research/modalities/pose-convergence-401.json → "
                                 "verdict.pocket_fit_ligand_rmsd_spread_A (not restated here)",
           "n_systems": len(have), "n_pairs": 0}
    if len(have) < 2:
        out["_status"] = "INSUFFICIENT — needs at least two systems the second method could dock"
        return out
    poses = {}
    for rec in have:
        # ⛔ BY SCORE, NEVER BY FILE POSITION — see `_keep_pose`. rbdock writes run order.
        m = best_from_sd(os.path.join(REPO, by_id[rec["id"]]["best_pose_sd"]))
        if m is not None:
            poses[rec["id"]] = m
    vals, cvals, pairs = [], [], []
    for i in range(len(have)):
        for j in range(i + 1, len(have)):
            a, b = have[i], have[j]
            if a["id"] not in poses or b["id"] not in poses:
                continue
            common = sorted(set(a["residues"]) & set(b["residues"]))
            fit = [r for r in bm.POCKET5 if r in set(common)]
            try:
                R, t, n_fit, fit_rms = pc.superpose(b["residues"], a["residues"], fit)
            except Exception as e:                            # noqa: BLE001
                pairs.append({"a": a["id"], "b": b["id"], "error": "%s: %s" % (type(e).__name__, e)})
                continue
            moved = pc.transformed_copy(poses[b["id"]], R, t)
            rms, why = in_frame_rmsd(moved, poses[a["id"]])
            cd = round(math.dist(_centroid(_heavy(moved)), _centroid(_heavy(poses[a["id"]]))), 3)
            pairs.append({"a": a["id"], "b": b["id"], "n_fit_residues": n_fit,
                          "receptor_fit_rmsd_A": round(float(fit_rms), 3),
                          "ligand_rmsd_A": rms, "band": band(rms),
                          "ligand_centroid_distance_A": cd, "why": why})
            if rms is not None:
                vals.append(rms)
                cvals.append(cd)
    out["pairs"] = pairs
    out["n_pairs"] = len(vals)
    out["ligand_rmsd_A"] = _spread(vals)
    out["ligand_centroid_distance_A"] = _spread(cvals)
    import apo_pose_recovery as apr
    out["n_pairs_within_recovered_A"] = sum(1 for v in vals if v <= apr.RECOVER_RMSD_A)
    out["n_pairs_within_partial_A"] = sum(1 for v in vals if v <= apr.PARTIAL_RMSD_A)
    return out


def _ligand_from_pose(mol, out_sd):
    """A fresh 3D conformer of the SAME molecule, built from its canonical SMILES.

    ⛔ NOT THE POSE ITSELF. Handing rDock the smina pose as its starting conformer would seed the search
    inside the answer it is being asked to check independently."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    try:
        smi = Chem.MolToSmiles(Chem.RemoveHs(mol))
        m = Chem.AddHs(Chem.MolFromSmiles(smi))
        ps = AllChem.ETKDGv3()
        ps.randomSeed = RDOCK_SEED
        if AllChem.EmbedMolecule(m, ps) != 0:
            return None, "RDKit could not embed a 3D conformer of %s" % smi
        AllChem.MMFFOptimizeMolecule(m, maxIters=500)
        m.SetProp("_Name", mol.GetProp("_Name") if mol.HasProp("_Name") else "ligand")
        w = Chem.SDWriter(out_sd)
        w.write(m)
        w.close()
    except Exception as e:                                    # noqa: BLE001
        return None, "ligand prep failed: %s: %s" % (type(e).__name__, e)
    return out_sd, None


def _stage_dock_prm(tools, work):
    """Copy rDock's own three-stage docking protocol into the working directory.

    ⛔ THE STOCK PROTOCOL, UNMODIFIED. Editing `dock.prm` would make this a bespoke method rather than
    a second published one, and the independence claim rests on it being rDock's own."""
    rbt = tools.get("RBT_ROOT")
    for cand in ([os.path.join(rbt, "data", "scripts", "dock.prm")] if rbt else []) + \
                [os.path.join(os.path.dirname(os.path.dirname(tools["rbdock"])),
                              "share", "rDock", "data", "scripts", "dock.prm")]:
        if cand and os.path.exists(cand):
            dst = os.path.join(work, "dock.prm")
            shutil.copy(cand, dst)
            return dst
    return None


# ==================================================================================================
# PART B — THE SECOND METHOD ON THE KNOWN-ANSWER PANEL, GRADED BY `C14`
# ==================================================================================================

_HOOK_STATE = {"tools": None, "runs": RDOCK_RUNS_PANEL, "rows": []}


def second_method_hook(ctx):
    """Called by `apo_pose_recovery.run_benchmark` with its own prepared inputs. Returns a dict.

    ⛔ IT MAY NOT MOVE ANY PRE-REGISTERED NUMBER, and structurally cannot: it receives `score_pose` and
    the boxes read-only, writes into its own key, and `verdict()` reads neither."""
    tools = _HOOK_STATE["tools"]
    if tools is None:
        return {"_status": "UNRUN — no rDock tools resolved"}
    return panel_pair(ctx, tools, _HOOK_STATE["runs"])


def panel_pair(ctx, tools, runs):
    """rDock, on ONE apo/holo pair, at the same boxes the first method used — graded by `C14`."""
    cand = ctx["cand"]
    tag = "%s_%s" % (cand.get("apo"), cand.get("holo"))
    work = os.path.join(ctx["work"], "rdock_" + tag)
    os.makedirs(work, exist_ok=True)
    dock_prm = _stage_dock_prm(tools, work)
    out = {
        "_method": "rDock (rbcavity + rbdock, stock three-stage dock.prm)",
        "_graded_by": "apo_pose_recovery.score_pose — the SAME scorer, contacts and frame the "
                      "pre-registered arms use, so the two methods differ only in how the pose was "
                      "produced",
        "criterion": criterion(),
        "n_rdock_runs": runs, "rdock_seed": RDOCK_SEED,
        "site_matched_radius_A": site_matched_radius_A(),
        "shared_configuration_by_arm": C_ITEMS_BY_ARM,
        "arms": {}, "refusals": [],
    }
    if dock_prm is None:
        out["_status"] = "UNRUN — rDock's dock.prm is not readable"
        return out
    boxes, sdf = ctx["boxes"], ctx["sdf"]
    score_pose = ctx["score_pose"]
    radius = site_matched_radius_A()

    prepared, rec_extent = {}, {}

    def receptor(kind, path):
        if kind in prepared:
            return prepared[kind]
        m2, why = to_mol2(path, os.path.join(work, kind + ".mol2"), tools)
        prepared[kind] = (m2, why)
        rec_extent[kind] = bbox_extent(_receptor_ca(path))
        return prepared[kind]

    def arm(name, kind, rec_path, center, rad, transform, shared_arm):
        if center is None:
            out["arms"][name] = {"rmsd_A": None, "why": "no box centre for this route",
                                 "shared_configuration": shared_arm}
            return
        if _time_left() < 120:
            out["arms"][name] = {"rmsd_A": None, "why": "total budget spent — UNRUN, not failed",
                                 "shared_configuration": shared_arm}
            return
        m2, why = receptor(kind, rec_path)
        if m2 is None:
            out["arms"][name] = {"rmsd_A": None, "why": why, "shared_configuration": shared_arm}
            return
        d = os.path.join(work, name)
        os.makedirs(d, exist_ok=True)
        shutil.copy(m2, os.path.join(d, "rec.mol2"))
        shutil.copy(dock_prm, os.path.join(d, "dock.prm"))
        shutil.copy(sdf, os.path.join(d, "lig.sd"))
        prm = write_prm(os.path.join(d, "rec.prm"), os.path.join(d, "rec.mol2"), center, rad, name)
        info, why = make_cavity(prm, tools, d)
        if info is None:
            out["arms"][name] = {"rmsd_A": None, "why": why, "shared_configuration": shared_arm}
            return
        degen = cavity_degeneracy(info, rec_extent.get(kind))
        res_, why = run_rbdock(prm, "lig.sd", "out", runs, tools, d)
        if res_ is None:
            out["arms"][name] = {"rmsd_A": None, "why": why, "cavity": info,
                                 "cavity_degeneracy": degen, "shared_configuration": shared_arm}
            return
        best = res_["poses"][0][1]
        rec = dict(score_pose(best, transform=transform))
        rec.update({"cavity": info, "cavity_degeneracy": degen, "rdock_score": res_["best_score"],
                    "rdock_score_spread": res_["score_spread"], "n_rdock_poses": res_["n_poses"],
                    "elapsed_s": res_["elapsed_s"], "box_center": [round(v, 3) for v in center],
                    "search_radius_A": rad, "shared_configuration": shared_arm})
        rec["pose_sd"] = _keep_pose(res_["poses"], "panel_%s_%s.sd" % (tag, name))
        out["arms"][name] = rec

    apo, holo = ctx["apo_rec"], ctx["holo_rec"]
    arm("blind_apo_pipeline_box", "apo", apo, (boxes.get("pipeline_apo") or {}).get("center"),
        radius, True, "site_matched")
    arm("blind_apo_fpocket_top_box", "apo", apo, (boxes.get("fpocket_top_apo") or {}).get("center"),
        radius, True, "fpocket_box")
    arm("C3_oracle_box_apo", "apo", apo, ctx.get("oracle_center_apo"), radius, True, "oracle_box")
    # the ceiling: the receptor the ligand was solved in, box on the ligand itself. This is the arm that
    # decides whether the pair may be graded at all — the same role C1c plays for the first method.
    arm("C1c_self_dock_holo_oracle_box", "holo", holo, ctx.get("oracle_center_holo"),
        radius, False, "oracle_box")
    # ⭑ THE ARM THAT SHARES NO SITE CONFIGURATION AT ALL: rDock is given the receptor and its own
    # centroid, and finds a cavity by itself. This is the second method's answer to Q-SITE.
    try:
        pts = _receptor_ca(apo)
        if pts:
            arm("receptor_wide_own_cavity_apo", "apo", apo, _centroid(pts),
                OWN_CAVITY_RADIUS_A, True, "receptor_wide")
    except Exception as e:                                    # noqa: BLE001
        out["refusals"].append({"stage": "receptor_wide", "evidence": "%s: %s" % (type(e).__name__, e)})

    # inter-method agreement ON THIS PAIR — the same box, the same ligand file, two engines.
    out["cross_method"] = _panel_cross_method(ctx, out["arms"])
    out["first_method_arms_this_run"] = {
        k: {kk: v.get(kk) for kk in ("rmsd_A", "fnat", "verdict", "centroid_distance_A")}
        for k, v in (ctx.get("arms") or {}).items()}
    out["_first_method_home"] = ("research/modalities/apo-pose-recovery.json → result.arms — the "
                                 "PRE-REGISTERED draw. The block above is THIS run's draw of the same "
                                 "unseeded search and is not a correction of it.")
    out["induced_fit"] = ctx.get("induced_fit")
    return out


def _receptor_ca(pdb_path):
    pts = []
    for line in open(pdb_path, errors="replace"):
        if line.startswith("ENDMDL"):
            break
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                pts.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
            except ValueError:
                continue
    return pts


#: Which second-method arm is compared with which first-method arm. Same box, same ligand file, so the
#: only difference is the engine — which is the whole design.
_ARM_PAIRING = {
    "blind_apo_pipeline_box": "PRIMARY_blind_apo_pipeline_box",
    "blind_apo_fpocket_top_box": "blind_apo_fpocket_top_box",
    "C3_oracle_box_apo": "C3_oracle_box_apo",
    "C1c_self_dock_holo_oracle_box": "C1c_self_dock_holo_oracle_box",
}


def _panel_cross_method(ctx, rdock_arms):
    """Second-method pose vs first-method pose, box for box, in the receptor's own frame."""
    import apo_pose_recovery as apr
    work, comp = ctx["work"], ctx["comp"]
    tags = {"PRIMARY_blind_apo_pipeline_box": "apo_pipeline",
            "blind_apo_fpocket_top_box": "apo_fpocket",
            "C3_oracle_box_apo": "apo_oracle",
            "C1c_self_dock_holo_oracle_box": "holo_self_oracle"}
    rows = {}
    for rd_name, sm_name in _ARM_PAIRING.items():
        rd = rdock_arms.get(rd_name) or {}
        sd = rd.get("pose_sd")
        smina_sdf = os.path.join(work, "docked_%s.sdf" % tags[sm_name])
        row = {"first_method_arm": sm_name, "second_method_arm": rd_name}
        if not sd or not os.path.exists(os.path.join(REPO, sd)):
            row["why"] = "the second method produced no pose in this arm"
            rows[rd_name] = row
            continue
        sm_mol, why = apr._top_pose(smina_sdf, comp)
        if sm_mol is None:
            row["why"] = "the first method produced no pose in this arm: %s" % why
            rows[rd_name] = row
            continue
        rd_mol = best_from_sd(os.path.join(REPO, sd))   # by SCORE, never by file position
        if rd_mol is None:
            row["why"] = "the second method's SD file held no readable pose"
            rows[rd_name] = row
            continue
        rms, why = in_frame_rmsd(rd_mol, sm_mol)
        row.update({"inter_method_rmsd_A": rms, "band": band(rms), "why": why,
                    "inter_method_internal_conformer_rmsd_A": internal_rmsd(rd_mol, sm_mol)[0],
                    "inter_method_centroid_distance_A": round(
                        math.dist(_centroid(_heavy(rd_mol)), _centroid(_heavy(sm_mol))), 3),
                    "first_method_rmsd_to_crystal_A": (ctx.get("arms") or {}).get(sm_name, {}).get("rmsd_A"),
                    "second_method_rmsd_to_crystal_A": rd.get("rmsd_A")})
        rows[rd_name] = row
    return {"_asks": "SAME box, SAME ligand file, two engines — how far apart are their best poses?",
            "_frame": "the receptor's own coordinates; no superposition, symmetry-corrected CalcRMS",
            "by_arm": rows}


def part_b(tools, runs=None, limit=None):
    """Run the pre-registered panel with the second-method hook armed. Writes only this artifact."""
    import apo_pose_recovery as apr
    _HOOK_STATE["tools"] = tools
    _HOOK_STATE["runs"] = RDOCK_RUNS_PANEL if runs is None else runs
    pool, why = panel_pool()
    out = {
        "_asks": "On systems where the crystallographic answer IS known, what does a scoring-independent "
                 "method recover — and does it agree with the first method?",
        "_panel_source": "research/modalities/apo-pose-recovery.json → selection.panel_pool. ⛔ The "
                         "panel is READ, not re-sourced: re-running the RCSB query could return a "
                         "different set and the comparison would no longer be on the same systems.",
        "criterion": criterion(),
        "shared_configuration_by_arm": C_ITEMS_BY_ARM,
        "_confound_carried": pipeline_box_confound(),
        "pairs": [], "refusals": [],
    }
    if not pool:
        out["_status"] = "UNRUN — %s" % why
        return out
    if limit:
        pool = pool[:limit]
    out["n_pairs_attempted"] = len(pool)
    # the SAME reference resolution `apo_pose_recovery.main()` uses — the committed model the pipeline
    # itself worked from, never a freshly-fetched one that might have been re-predicted since.
    repo_af2 = os.path.join(REPO, "results", "nr4a3-metad-r2", "ckpt", "AF-Q92570.pdb")
    af2 = os.environ.get("AF2_REFERENCE_PDB") or (repo_af2 if os.path.exists(repo_af2) else "")
    out["_af2_reference"] = os.path.relpath(af2, REPO) if af2.startswith(REPO) else af2
    work_root = os.path.join(WORK, "panel")
    os.makedirs(work_root, exist_ok=True)
    apr.SECOND_METHOD_HOOK = second_method_hook
    try:
        for cand in pool:
            if _time_left() < UNIT_BUDGET_S:
                out["refusals"].append({"pair": "%s->%s" % (cand.get("apo"), cand.get("holo")),
                                        "stage": "budget",
                                        "evidence": "total budget %ds spent — UNRUN, not failed"
                                                    % TOTAL_BUDGET_S})
                continue
            w = os.path.join(work_root, "%s_%s" % (cand.get("apo"), cand.get("holo")))
            res = apr.run_benchmark(cand, w, af2, replicates=0, ceiling_replicates=0)
            out["pairs"].append(_panel_row(cand, res))
            _checkpoint({"part_b_partial": out})
    finally:
        apr.SECOND_METHOD_HOOK = None
    out["rollup"] = _panel_rollup(out["pairs"])
    out["induced_fit_panel"] = induced_fit_panel(out["pairs"])
    return out


def _panel_row(cand, res):
    sm = res.get("second_method") or {}
    row = {
        "apo": cand.get("apo"), "holo": cand.get("holo"),
        "protein": cand.get("protein"), "accession": cand.get("accession"),
        "ligand": (cand.get("ligand") or {}).get("comp_id"),
        "excluded_by": res.get("excluded_by"),
        "refusals": res.get("refusals"),
        "first_method_verdict": (res.get("verdict") or {}).get("outcome"),
        "second_method": sm,
        "induced_fit": res.get("induced_fit"),
        "declared_allosteric": (res.get("declared_allosteric") or {}).get("declared_in_holo_title"),
        "apo_and_holo_same_construct": (res.get("engineered_construct") or {}).get(
            "apo_and_holo_are_the_same_construct"),
        "C2_random_in_box_null": {
            k: (res.get("C2_random_in_box_null") or {}).get(k)
            for k in ("p_within_criterion", "has_power", "n")},
    }
    return row


def _panel_rollup(pairs):
    """Counts, in `C14`'s vocabulary, with the gradeability rule the first method's panel already uses.

    ⛔ THE CEILING RULE IS INHERITED, NOT INVENTED. A pair whose own protocol ceiling misses cannot grade
    the docking — that is the pre-registered C1/C1c logic, and applying it to the second method is what
    makes the two counts comparable rather than merely adjacent."""
    import apo_pose_recovery as apr
    rows = []
    for p in pairs:
        sm = p.get("second_method") or {}
        arms = sm.get("arms") or {}
        ceil = (arms.get("C1c_self_dock_holo_oracle_box") or {}).get("rmsd_A")
        gradeable = ceil is not None and ceil <= apr.RECOVER_RMSD_A
        rows.append({
            "pair": "%s->%s" % (p.get("apo"), p.get("holo")), "protein": p.get("protein"),
            "excluded_by": p.get("excluded_by"),
            "ceiling_rmsd_A": ceil, "ceiling_band": band(ceil), "gradeable": gradeable,
            "blind_apo_pipeline_box": {
                "rmsd_A": (arms.get("blind_apo_pipeline_box") or {}).get("rmsd_A"),
                "band": (arms.get("blind_apo_pipeline_box") or {}).get("verdict")},
            "blind_apo_fpocket_top_box": {
                "rmsd_A": (arms.get("blind_apo_fpocket_top_box") or {}).get("rmsd_A"),
                "band": (arms.get("blind_apo_fpocket_top_box") or {}).get("verdict")},
            "C3_oracle_box_apo": {
                "rmsd_A": (arms.get("C3_oracle_box_apo") or {}).get("rmsd_A"),
                "band": (arms.get("C3_oracle_box_apo") or {}).get("verdict")},
            "receptor_wide_own_cavity_apo": {
                "rmsd_A": (arms.get("receptor_wide_own_cavity_apo") or {}).get("rmsd_A"),
                "band": (arms.get("receptor_wide_own_cavity_apo") or {}).get("verdict")},
            "inter_method": {k: (v or {}).get("inter_method_rmsd_A")
                             for k, v in ((sm.get("cross_method") or {}).get("by_arm") or {}).items()},
        })
    scored = [r for r in rows if r["ceiling_rmsd_A"] is not None]
    grade = [r for r in scored if r["gradeable"]]

    def _count(key, bandname):
        return sum(1 for r in grade if r[key]["band"] == bandname)

    inter = [v for r in rows for v in r["inter_method"].values() if v is not None]
    return {
        "rows": rows,
        "n_pairs": len(rows), "n_with_ceiling": len(scored), "n_gradeable": len(grade),
        "_gradeability_rule": "a pair whose own protocol ceiling (self-dock into the holo receptor, box "
                              "on the crystallographic ligand) does not reach `recovered_A` cannot grade "
                              "the docking — the pre-registered C1/C1c rule, applied unchanged",
        "bands_over_gradeable_pairs": {
            arm_: {b: _count(arm_, b) for b in ("RECOVERED", "PARTIAL", "NOT RECOVERED")}
            for arm_ in ("blind_apo_pipeline_box", "blind_apo_fpocket_top_box",
                         "C3_oracle_box_apo", "receptor_wide_own_cavity_apo")},
        "inter_method_rmsd_A": _spread(inter),
        "inter_method_bands": {b: sum(1 for v in inter if band(v) == b)
                               for b in ("RECOVERED", "PARTIAL", "NOT RECOVERED")},
    }


def induced_fit_panel(pairs):
    """★ POINT 5 — the size of the problem each pair actually poses, for EVERY pair.

    ⛔ THE HEADLINE PAIR IS A WEAK TEST AND THE ARTIFACT MUST SAY SO. Its site Ca RMSD is a fraction of
    an Angstrom, so a cross-dock between its two structures is close to a rigid re-dock: it can show
    that a protocol reproduces a pose, and it cannot show that a protocol survives apo->holo
    rearrangement. A panel with no genuinely rearranging pair could not test the thing `R5` needs, and
    that is a limitation of the whole test rather than a caveat on one row."""
    import apo_pose_recovery as apr
    regime = apr._REGIME_ACCESSIONS()
    rows = []
    for p in pairs:
        f = p.get("induced_fit") or {}
        rows.append({"pair": "%s->%s" % (p.get("apo"), p.get("holo")), "protein": p.get("protein"),
                     "accession": p.get("accession"),
                     "in_pipeline_regime": p.get("accession") in regime,
                     "declared_allosteric": p.get("declared_allosteric"),
                     "site_ca_rmsd_A": f.get("site_ca_rmsd_A"),
                     "global_ca_rmsd_A": f.get("global_ca_rmsd_A"),
                     "n_site_residues": f.get("n_site"),
                     "large_rearrangement": f.get("large_rearrangement"),
                     "apo_and_holo_same_construct": p.get("apo_and_holo_same_construct")})
    vals = [r["site_ca_rmsd_A"] for r in rows if r["site_ca_rmsd_A"] is not None]
    n_large = sum(1 for r in rows if r.get("large_rearrangement"))
    # ⭑ THE QUESTION A PANEL-WIDE COUNT CANNOT ANSWER, AND IT IS THE ONE THAT MATTERS. "4 of 6 pairs
    # rearrange" is true and reassuring; what `R5` needs is a pair that rearranges AND is one the
    # pipeline actually transfers Pocket-5 onto. Those are different sets and they are computed here
    # rather than eyeballed, because eyeballing them is what made the reassuring count quotable.
    in_regime = [r for r in rows if r["in_pipeline_regime"] and r["site_ca_rmsd_A"] is not None]
    both = [r for r in in_regime if r.get("large_rearrangement")]
    return {
        "_threshold_A": apr.LARGE_INDUCED_FIT_A,
        "_measured_by": "apo_pose_recovery.run_benchmark — the same apo->holo site-Ca RMSD the "
                        "pre-registered panel reports, not a second definition",
        "rows": rows, "n_pairs": len(rows), "site_ca_rmsd_A": _spread(vals),
        "n_with_large_rearrangement": n_large,
        "panel_contains_a_large_rearrangement": n_large > 0,
        "in_regime_and_rearranging": {
            "_asks": "is there a pair that BOTH rearranges AND is a protein the pipeline actually "
                     "transfers Pocket-5 onto? A rearranging pair outside the regime tests the docking "
                     "engines and cannot test the pipeline's own transfer.",
            "_regime": sorted(regime),
            "n_in_regime_measured": len(in_regime),
            "n_in_regime_and_rearranging": len(both),
            "pairs": [r["pair"] for r in both],
            "in_regime_site_ca_rmsd_A": _spread([r["site_ca_rmsd_A"] for r in in_regime]),
            "_reads": (
                "⛔ NO PAIR IN THIS PANEL BOTH REARRANGES AND IS IN REGIME. Every rearranging pair is a "
                "receptor the pipeline never transfers Pocket-5 onto, and every in-regime pair is a "
                "near-rigid re-dock. So the panel's reassuring '%d of %d rearrange' does NOT mean the "
                "apo→holo transfer was tested where it matters — it was not tested there at all, by "
                "either method. ⇒ this is a limitation of the TEST, not a caveat on a row, and it is "
                "the cheapest thing on the list of what would resolve `R5`."
                % (n_large, len(vals))
                if in_regime and not both else
                "at least one pair both rearranges and is in regime, so the apo→holo transfer is "
                "genuinely exercised in the regime the claim needs"
                if both else
                "⚠ NO IN-REGIME PAIR CARRIES AN INDUCED-FIT MEASUREMENT AT ALL — that is an UNREAD "
                "quantity, not a finding of rigidity.")},
        "_limitation": (
            "⛔ A PAIR BELOW %.2f A OF SITE Ca MOVEMENT IS A NEAR-RIGID RE-DOCK AND IS A WEAK TEST OF "
            "APO->HOLO TRANSFER. It must not be quoted as one, in either method. If no pair in this "
            "panel rearranges, the panel cannot answer whether either method survives induced fit, and "
            "that is a limitation of the TEST, not a caveat on a row."
            % apr.LARGE_INDUCED_FIT_A),
        "_construct_caveat": (
            "⚠ AND WHERE `apo_and_holo_same_construct` IS FALSE THE NUMBER IS NOT PURE CONFORMATIONAL "
            "CHANGE — the two deposits are different engineered constructs, so the site-Ca RMSD "
            "contains whatever the substitution did as well."),
    }


def panel_pool():
    """The panel, READ from the pre-registered artifact so both methods run on the same systems."""
    src = os.path.join(HERE, "apo-pose-recovery.json")
    if not os.path.exists(src):
        return None, "apo-pose-recovery.json is not committed — no panel to read"
    try:
        d = json.load(open(src))
    except Exception as e:                                    # noqa: BLE001
        return None, "apo-pose-recovery.json unreadable: %s: %s" % (type(e).__name__, e)
    pool = ((d.get("selection") or {}).get("panel_pool")) or []
    return (pool, None) if pool else (None, "selection.panel_pool is empty in apo-pose-recovery.json")


# ==================================================================================================
# THE CONFOUND — ESTABLISHED FROM SOURCE, BEFORE ANY NUMBER IS INTERPRETED.
# ==================================================================================================

def pipeline_box_confound():
    """★ POINT 4 — what IS "the pipeline's box" on a panel receptor? Read out of the code, not recalled.

    ⛔ THIS MUST BE SETTLED BEFORE ANY SITE NUMBER IS READ. If the pipeline's box is NR4A3's own
    Pocket-5 dragged onto a distant nuclear receptor by a global sequence alignment, then that box
    missing PPARG's canonical ligand site is CLOSE TO EXPECTED and is NOT evidence that site selection
    is broken. The opposite reading — "the pipeline cannot find a site" — is the one this program has
    made before, and it is a different claim with a different remedy."""
    import inspect
    import nr4a3_8xtt_benchmark as bm
    import nr4a3_warhead as wh
    out = {
        "_question": "On a benchmark receptor, what does `the pipeline's box` mean?",
        "site_definition_C5": {
            "pocket5_lining_uniprot_Q92570": list(bm.POCKET5),
            "span": [bm.POCKET5_FIRST, bm.POCKET5_LAST],
            "_home": "nr4a3_8xtt_benchmark.POCKET5 (= `C5` in the map's configuration register)",
        },
        "transfer_kernel": {
            "function": "nr4a3_warhead.map_pocket_to_paralogue",
            "how": "a global Cα-sequence alignment of NR4A3's LBD onto the target receptor; the "
                   "Pocket-5 residue numbers are carried across that alignment",
            "boxed_by": "nr4a3_warhead.pocket_box — the Cα centroid of the carried residues",
            "_called_from": "apo_pose_recovery.pipeline_box",
        },
        "regime": {
            # ⚠ NAMES *AND* ACCESSIONS. `nr4a3_warhead.PARALOGUES` is a {name: accession} MAP, so
            # `sorted(...)` yields the names alone — and the panel is keyed by ACCESSION, so a reader
            # matching the two lists by eye would find no overlap and conclude the regime is empty.
            # Read the same way `apo_pose_recovery._REGIME_ACCESSIONS` reads it.
            "proteins_the_pipeline_actually_transfers_onto": sorted(getattr(wh, "PARALOGUES", {})),
            "accessions": sorted(set((getattr(wh, "PARALOGUES", {}) or {}).values()) | {"Q92570"}),
            "_plus": "NR4A3's own 8XTT (Q92570)",
            "_reads": "⛔ A RECEPTOR OUTSIDE THIS LIST IS OUT OF THE PIPELINE'S REGIME. Running the "
                      "transfer onto it and finding the ligand elsewhere is the benchmark's design, "
                      "not a demonstrated defect of site selection.",
        },
        "independent_check_that_separates_the_two_readings": {
            "function": "apo_pose_recovery.pocket5_structure_transfer",
            "how": "the SAME Pocket-5 set carried across by CE structural superposition "
                   "(Bio.PDB.cealign) instead of by sequence — so 'the alignment failed' and 'the "
                   "ligand is not in this receptor's Pocket-5-equivalent site' can be told apart",
            "_pre_declared_reading": "the two transfers AGREEING that the ligand is elsewhere reads as "
                                     "(b) — the ligand is not in the Pocket-5-equivalent site",
        },
        "_verified_by_reading": [],
    }
    try:
        src = inspect.getsource(wh.map_pocket_to_paralogue)
        out["_verified_by_reading"].append(
            {"function": "nr4a3_warhead.map_pocket_to_paralogue", "n_source_lines": len(src.splitlines()),
             "uses_pairwise_sequence_alignment": ("align" in src.lower())})
    except Exception as e:                                    # noqa: BLE001
        out["_verified_by_reading"].append({"function": "nr4a3_warhead.map_pocket_to_paralogue",
                                            "unread": "%s: %s" % (type(e).__name__, e)})
    try:
        src = inspect.getsource(wh.pocket_box)
        out["_verified_by_reading"].append(
            {"function": "nr4a3_warhead.pocket_box", "n_source_lines": len(src.splitlines()),
             "centroid_of_CA": ('"CA"' in src)})
    except Exception as e:                                    # noqa: BLE001
        out["_verified_by_reading"].append({"function": "nr4a3_warhead.pocket_box",
                                            "unread": "%s: %s" % (type(e).__name__, e)})
    return out


# ==================================================================================================
# THE VERDICT — a plain answer about `R5`, with the ceiling on what it licenses attached.
# ==================================================================================================

def verdict(doc):
    import apo_pose_recovery as apr
    a = doc.get("part_a") or {}
    b = doc.get("part_b") or {}
    cm = a.get("cross_method_same_frame") or {}
    roll = b.get("rollup") or {}
    rec_A, part_A = apr.RECOVER_RMSD_A, apr.PARTIAL_RMSD_A

    n_sys = cm.get("n_systems") or 0
    bands = cm.get("bands") or {}
    n_agree = bands.get("RECOVERED", 0)
    med = (cm.get("rmsd_A") or {}).get("median")

    out = {
        "_asks": "Can `R5` be resolved now?",
        "second_method": "rDock",
        "cross_method_evidence": ("PRESENT — %d system(s) carry a pose from two methods with disjoint "
                                  "scoring" % n_sys) if n_sys else
                                 "STILL NONE — the second method produced no comparable pose",
        "part_a_n_systems": n_sys,
        "part_a_agreement_within_recovered_A": n_agree,
        "part_a_median_inter_method_rmsd_A": med,
        "part_b_n_gradeable": roll.get("n_gradeable"),
        "part_b_bands": roll.get("bands_over_gradeable_pairs"),
        "part_b_inter_method_rmsd_A": roll.get("inter_method_rmsd_A"),
    }
    if not n_sys:
        out["R5_resolved"] = False
        out["outcome"] = "UNRUN"
        out["sentence"] = ("The second method did not produce a comparable pose on any system, so "
                           "`cross_method_evidence` is still NONE and `R5` is exactly where it was.")
        return out

    agreed = n_agree == n_sys
    partial_only = (n_agree + bands.get("PARTIAL", 0)) == n_sys
    out["R5_resolved"] = False                       # set below only if everything lines up
    if agreed:
        out["outcome"] = "TWO METHODS AGREE, WITHIN THE RECOVERY LINE"
        out["sentence"] = (
            "On %d of %d system(s) a scoring-independent method placed the molecule within %.2f A of "
            "the pose this program holds (median %s A). ⛔ THAT IS AGREEMENT, NOT CORRECTNESS: both "
            "methods are given the same receptor conformer and could share its error, and a convergent "
            "wrong answer is still wrong." % (n_agree, n_sys, rec_A, med))
    elif partial_only:
        out["outcome"] = "PARTIAL AGREEMENT ONLY — NOT RECOVERY"
        out["sentence"] = (
            "Every comparable system lands between %.2f and %.2f A, which is `C14`'s PARTIAL band. "
            "⛔ PARTIAL IS NOT RECOVERY: the two methods put the molecule in the same neighbourhood and "
            "not in the same place, so the pose is not attributable to method-independent evidence."
            % (rec_A, part_A))
    else:
        out["outcome"] = "THE TWO METHODS DISAGREE"
        out["sentence"] = (
            "%d of %d system(s) agree within %.2f A; the median inter-method disagreement is %s A. "
            "⛔ A disagreement of this size between two methods with disjoint scoring means the pose "
            "this program holds is NOT attributable — and it is now attributable-to-nothing for a "
            "measured reason rather than for the absence of a second opinion."
            % (n_agree, n_sys, rec_A, med))
    out["what_this_does_not_license"] = [
        "that the pose is correct — no experimental structure of this complex exists",
        "that anything binds — `R4` still needs a bench and nothing here touches it",
        "that any downstream free-energy or selectivity number inherits validity",
        "that either method's search was exhaustive — the run counts are reported beside every number",
    ]
    out["what_would_resolve_R5"] = _what_would_resolve(doc)
    return out


def _what_would_resolve(doc):
    """The honest list, stated whether or not the result was favourable."""
    b = doc.get("part_b") or {}
    roll = b.get("rollup") or {}
    ind = b.get("induced_fit_panel") or {}
    items = [
        {"item": "a known answer IN REGIME with a real apo->holo rearrangement",
         "why": "the panel's gradeable pairs are the test's own evidence about whether either method "
                "survives induced fit; a panel of near-rigid re-docks cannot answer it",
         "measured_here": {"n_gradeable": roll.get("n_gradeable"),
                           "n_with_large_rearrangement": ind.get("n_with_large_rearrangement"),
                           "site_ca_rmsd_A": ind.get("site_ca_rmsd_A")},
         "cost": "$0 — CPU/CI; it is a sourcing question, not a compute one"},
        {"item": "a third method that is generative rather than a docking search "
                 "(a co-fold with COMMITTED COORDINATES)",
         "why": "both methods here place a ligand into a fixed receptor. A co-fold predicts the complex, "
                "so it fails differently again — and `pose-convergence-401.json` already records that "
                "the binary co-fold this program ran committed CONFIDENCE SCORES ONLY and no "
                "coordinates, which is why it could not enter the comparison",
         "cost": "GPU — priced nowhere yet; the $0 half is committing coordinates from a run that "
                 "already happened, if any survive"},
        {"item": "a decision on `C6`",
         "why": "two of the six systems inherit the contested frame-selection criterion; agreement "
                "measured in a frame whose selection datum does not reproduce inherits that dispute",
         "cost": "$0 — but it is trimcrae's call, not an agent's (§3b.2)"},
    ]
    return items


# ==================================================================================================
# ORCHESTRATION
# ==================================================================================================

def _checkpoint(partial):
    """Write what exists so far. A crash or a timeout must leave the partial result, never nothing."""
    try:
        tmp = OUT + ".partial"
        with open(tmp, "w") as fh:
            json.dump({"_status": "PARTIAL — a run is in progress or was interrupted", **partial},
                      fh, indent=1, default=str)
    except Exception:                                         # noqa: BLE001 — never fail the science
        pass


def main():
    mode = os.environ.get("MODE", "both").strip().lower()
    os.makedirs(WORK, exist_ok=True)
    doc = {
        "_module": "pose_second_method",
        "_mode": mode,
        "_question": "Is the pose this program holds for denovo_401 supported by a SECOND method whose "
                     "scoring is independent of the first — and on systems with a known answer, what "
                     "does that second method recover under `C14`?",
        "_licenses": ["two methods with disjoint scoring agreeing on a placement, to a stated tolerance"],
        "_does_not_license": ["that the pose is correct", "that anything binds",
                              "that any downstream free-energy or selectivity number inherits validity"],
        "criterion": criterion(),
        "shared_configuration_by_arm": C_ITEMS_BY_ARM,
        "_C6": C6_NOTE,
        "_confound_carried": pipeline_box_confound(),
        "_budgets_s": {"unit": UNIT_BUDGET_S, "total": TOTAL_BUDGET_S},
    }
    # ⚠ WHERE THIS RAN, SO A COMMITTED ARTIFACT CANNOT BE MISTAKEN FOR ANOTHER RUN'S. A CI publish and a
    # local reproduction produce the same file name; without this the only difference is a scratch path
    # buried in `tooling`, and "which run is this" becomes a question nobody can answer from the artifact.
    doc["_provenance"] = {
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_ref": os.environ.get("GITHUB_REF_NAME"),
        "github_sha": os.environ.get("GITHUB_SHA"),
        "where": "GitHub Actions" if os.environ.get("GITHUB_RUN_ID") else "local reproduction",
    }
    tools, why = rdock_tools()
    doc["tooling"] = ({"rdock_version": tools["rdock_version"],
                       "openbabel_version": tools["openbabel_version"],
                       "RBT_ROOT": tools["RBT_ROOT"]} if tools else {"unavailable": why})
    if tools is None:
        doc["_status"] = "UNRUN — %s" % why
        _emit(doc)
        return doc
    if mode in ("both", "cross"):
        doc["part_a"] = part_a(tools)
        _checkpoint(doc)
    if mode in ("both", "panel"):
        doc["part_b"] = part_b(tools, limit=int(os.environ.get("PANEL_LIMIT", "0")) or None)
    # the verdict is computed over BOTH halves, including one carried from an earlier run — which is
    # why the carry has to happen before it, and why each carried half says so in its own record.
    doc = _carry_forward(doc)
    doc["verdict"] = verdict(doc)
    doc["_status"] = "ok"
    doc["_elapsed_s"] = round(time.time() - _T0, 1)
    _emit(doc)
    return doc


def _carry_forward(doc):
    """A single-mode run must never DELETE the half it did not run.

    ⛔ THE FAILURE THIS CLOSES, caught before it happened: `MODE=panel` builds a document with no
    `part_a` key, and `_emit` overwrites the artifact — so a panel-only re-run would silently replace a
    committed cross-method result with nothing, and the artifact would then say `cross_method_evidence:
    NONE` again for a bookkeeping reason. Carrying the half forward is honest ONLY if it is labelled, so
    each carried half is stamped with the run that actually produced it and the fact that this run did
    not. ⚠ A carried half is not a fresh measurement and the stamp is what stops it reading as one."""
    if not os.path.exists(OUT):
        return doc
    try:
        prev = json.load(open(OUT))
    except Exception:                                         # noqa: BLE001
        return doc
    for half in ("part_a", "part_b"):
        if half in doc or half not in prev:
            continue
        carried = prev[half]
        if isinstance(carried, dict):
            carried = dict(carried)
            carried["_carried_forward"] = {
                "_reads": "⚠ NOT MEASURED IN THIS RUN. This half was produced by an earlier run and is "
                          "carried so a single-mode re-run cannot delete it; treat it as that run's "
                          "result, not this one's.",
                "produced_by": prev.get("_provenance"),
                "produced_at_status": prev.get("_status"),
                "this_run_mode": doc.get("_mode"),
            }
        doc[half] = carried
    return doc


def _emit(doc):
    doc = _carry_forward(doc)
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in doc.items()
                      if k in ("_status", "_mode", "tooling", "verdict")}, indent=1, default=str)[:6000])
    try:
        os.remove(OUT + ".partial")
    except OSError:
        pass
    return OUT


if __name__ == "__main__":
    main()
