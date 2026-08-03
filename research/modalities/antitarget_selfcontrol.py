#!/usr/bin/env python3
"""RUNG `R14-a` — complete the anti-target panel, and run the self-control it has never run. ($0, CPU)

★★ WHY THIS EXISTS, AND WHY THE ORDER IS NOT NEGOTIABLE. The anti-target panel is an INSTRUMENT that has
never been calibrated. It has already produced a published number: SI §S1 states that every repurposing
survivor binds at least one panel target more tightly than NR4A3, that PXR and HSA are engaged within
2 kcal/mol in every case, and that `denovo_401` "tops out at −9.1 (VDR)". Every one of those sentences is a
comparison ACROSS panel receptors, so every one of them assumes each receptor in the panel is a receptor the
protocol can dock into at all. Nobody has ever checked. This module checks, and the roadmap's rung `R14-a`
fixes the consequence in advance:

    ⛔ THE COGNATE-LIGAND SELF-CONTROL RUNS FIRST, AND UNTIL IT PASSES NO ANTI-TARGET MARGIN FROM THIS
       PANEL MAY BE READ — INCLUDING THE ONE SI §S1 ALREADY PUBLISHES.

That is why a failure here is the deliverable and not an obstacle: it would reach a result the paper carries.

★ WHAT THE CONTROL IS. Each panel target is a HOLO crystal structure: a receptor solved WITH a reference
ligand, and the panel's docking box is centred on that ligand's centroid. So the panel already contains,
for free, the easiest known-answer test in structural biology — re-dock each receptor's OWN co-crystallised
ligand, through the IDENTICAL protocol (`antitarget_prep.prep_target_full` builds the receptor, the box size
and exhaustiveness are read out of the panel spec and `antitarget_dock.py`'s own source, never re-typed), and
ask whether the crystallographic pose comes back. A protocol that cannot recover a pose when handed the very
conformer the ligand was solved in, inside a box centred on the answer, is not measuring binding at that
receptor; whatever ΔG it reports there is a number about the software.

⚠ AND THIS PANEL HAS A SPECIFIC, PREDICTABLE PLACE TO FAIL, WHICH IS WHY THE CONTROL IS NOT A FORMALITY.
`antitarget_prep` emits *standard-amino-acid ATOM records only*. That deliberately drops waters, ions and
buffers — and it also drops COFACTORS. CYP3A4 (2V0M) without its haem is a cavity with a hole where the iron
was, and ketoconazole's measured binding mode is a direct Fe–N coordination. The control cannot know that in
advance and does not assume it: it measures, per target, and reports.

──────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ PRE-REGISTERED CRITERION — WRITTEN BEFORE THE FIRST RUN. DO NOT TUNE.
──────────────────────────────────────────────────────────────────────────────────────────────────────
PRIMARY, per target. Symmetry-corrected heavy-atom RMSD of the TOP-RANKED re-docked pose to the
crystallographic copy of the same ligand, in the receptor's own coordinate frame (no superposition is
performed or needed — the same coordinates are docked into).

    PASS       RMSD <= 2.00 A          (`apo_pose_recovery.RECOVER_RMSD_A`)
    PARTIAL    2.00 < RMSD <= 4.00 A   (`apo_pose_recovery.PARTIAL_RMSD_A`)
    FAIL       RMSD > 4.00 A
    UNSCORED   the pose or the crystal copy could not be built — a REFUSAL, never a pass

⚠ THE TWO BANDS ARE NOT RE-TYPED HERE. They are imported from `apo_pose_recovery`, which fixed them in
writing before this program's other known-answer test, and which cites their provenance (the Astex / CASF /
PDBbind redocking-success and wrong-pose boundaries). One home; if that module's thresholds ever move, this
control moves with them and says so.

POWER CONTROL, per target (C2). `N_NULL` random rigid placements of the same ligand inside the same box. If
P(random <= 2.00 A) exceeds `NULL_POWER_MAX`, then passing means nothing at that target and the verdict is
NO_POWER, not PASS. Reused verbatim from `apo_pose_recovery.random_in_box_null` — a criterion whose power
was never measured is the failure that module was written to stop repeating.

SECONDARY, reported and never gating: `fnat`, the fraction of native ligand-contacting receptor residues
recovered, and the self-dock ΔG. Neither may overturn the primary.

PANEL VERDICT. `panel_readable` is TRUE only if EVERY target scores PASS. This is deliberately strict and
the reason is arithmetic, not taste: every published statement is a MAXIMUM or an "every survivor" over the
whole panel, so one unreadable receptor can change a best-off-target and therefore every gap computed from
it. `si_s1_statements` names, per published clause, exactly which targets it consumes — so a partial failure
says which sentences fall and which survive, instead of collapsing to "the panel is broken".

⛔ WHAT THIS MODULE MAY NOT DO. It may not drop a failing target from the panel to make a margin readable;
it may not re-centre a box; it may not lower a band. A target that fails is reported as failing and the
statements that consume it are reported as not currently readable.

──────────────────────────────────────────────────────────────────────────────────────────────────────
MODES
──────────────────────────────────────────────────────────────────────────────────────────────────────
  resolve      Resolve the missing flagged receptor — NR3C2 / MR — from its UniProt accession by a LIVE
               RCSB query (never a remembered PDB id: CLAUDE.md §7, no fabricated coordinate or citation),
               under selection rules fixed below, and write the resolved row into `antitarget_panel.json`.
               Idempotent: an MR row that already carries a pdb_id is kept and re-verified, not replaced.
  selfcontrol  THE GATE. The cognate re-dock above, over every target in the panel.
  flagged      Dock `denovo_401` + the carried repurposing candidates into the FLAGGED receptors (AR and
               MR — the two the 47-receptor sequence screen returned). Emits absolute ΔG only; see
               `margin_refusal` for why no margin is computed here.
  all          resolve -> selfcontrol -> flagged, in that order.
  --check      Offline self-test of every pure function. No network, no smina, no rdkit required.

Env: SELFCONTROL_WORK (scratch dir), EXHAUSTIVENESS override is DELIBERATELY NOT read — the protocol is
whatever the panel dock uses, or this is not a control of the panel.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(HERE, "antitarget_panel.json")
OUT = os.path.join(HERE, "antitarget-selfcontrol.json")
OUT_MD = os.path.join(HERE, "antitarget-selfcontrol.md")
#: The SI edit list, standalone, so `route_map_edits.py --target ...paper-SI.md` can consume it directly.
OUT_SI = os.path.join(HERE, "antitarget-selfcontrol-si-edits.json")
SI_PATH = os.path.join(HERE, "..", "manuscripts", "nr4a3-degrader-paper-SI.md")
WORK = os.environ.get("SELFCONTROL_WORK", os.path.join(HERE, "_antitarget_selfcontrol_work"))

#: The receptor the 47-receptor sequence screen flagged and the panel does not carry.
#: `nr4a-superfamily-selectivity.json` -> `flagged_liabilities` is the one home of the flag itself; the
#: accession is repeated here only as the query key, and `resolve` asserts it against that artifact.
MR_ACCESSION = "P08235"
MR_NAME = "MR"
MR_GENE = "NR3C2"

#: Per-dock wall-clock hang-guard. CLAUDE.md §6: the per-unit timeout is the real hang-guard, and a
#: pathological ligand must cost its own dock and no more, surfacing as a refusal with its elapsed time.
PER_DOCK_TIMEOUT_S = int(os.environ.get("SELFCONTROL_DOCK_TIMEOUT_S", "600"))

#: What each published SI §S1 clause consumes. Not decoration: it is how a partial failure reports which
#: sentence falls. `"*"` means the clause is a maximum/every-survivor statement over the WHOLE panel.
SI_S1_STATEMENTS = [
    {"id": "S1.3a",
     "clause": "every survivor binds >=1 off-target more tightly than NR4A3 (gap -0.3 to -5.7 kcal/mol)",
     "consumes": ["*"],
     "why": "a MAX over the panel: one unreadable receptor can be the max, or can hide it"},
    {"id": "S1.3b",
     "clause": "5-8 panel targets within 2 kcal, and PXR + HSA engaged within 2 kcal in every case",
     "consumes": ["PXR", "HSA", "*"],
     "why": "counts targets within a window, so it consumes every target; the named pair additionally"},
    {"id": "S1.3c",
     "clause": "denovo_401 through the same panel tops out at -9.1 (VDR), 1.7-5 kcal weaker than any "
               "repurposed survivor and not a PXR/HSA hit",
     "consumes": ["VDR", "PXR", "HSA", "*"],
     "why": "a MAX over the panel whose argmax is named, plus a negative claim about two named targets"},
    {"id": "S1.3d",
     "clause": "the panel DISCRIMINATES rather than merely saturates",
     "consumes": ["*"],
     "why": "a claim about the instrument itself, which is exactly what the self-control measures"},
]

#: Selection rules for `resolve`, fixed before the query so the pick cannot be steered to a convenient
#: structure. Applied in order; every candidate and its score is emitted as evidence.
RESOLVE_RULES = [
    "R1 the entry must reference the requested UniProt accession on a protein polymer entity",
    "R2 X-ray diffraction (a docking box centred on a solution-NMR model's ligand has no single frame)",
    "R3 at least one drug-like ligand by apo_pose_recovery.drug_like (MW 200-800, not an additive, not "
    "a peptide/saccharide/nucleic acid)",
    "R4 prefer an entry whose title does NOT declare an engineered mutant "
    "(apo_pose_recovery.engineered_flag) — the MR LBD is very often deposited as the S810L mutant, and a "
    "mutant receptor is a different anti-target",
    "R5 then best (lowest) resolution",
    "R6 then lowest pdb id, purely to make the pick deterministic",
]


# ==================================================================================================
# PURE LOGIC — no network, no rdkit, no smina. Everything here is exercised by `--check`.
# ==================================================================================================

def bands():
    """The two pre-registered RMSD bands and the null-power ceiling, READ from their one home."""
    import apo_pose_recovery as apr
    return {"recovered_rmsd_A": apr.RECOVER_RMSD_A, "partial_rmsd_A": apr.PARTIAL_RMSD_A,
            "null_power_max": apr.NULL_POWER_MAX, "n_null": apr.N_NULL,
            "_read_from": "apo_pose_recovery (RECOVER_RMSD_A / PARTIAL_RMSD_A / NULL_POWER_MAX / N_NULL)"}


def target_verdict(rmsd_A, null_frac, recovered_A, partial_A, null_power_max):
    """PASS / PARTIAL / FAIL / NO_POWER / UNSCORED for one target. Pure.

    NO_POWER outranks PASS deliberately: a criterion a random placement clears is not a criterion, so a
    pass under it is not evidence. It does NOT outrank FAIL — a failure under a powerless criterion is
    still a failure, and calling it 'no power' would be an excuse rather than a reading.
    """
    if rmsd_A is None:
        return "UNSCORED"
    if rmsd_A <= recovered_A:
        if null_frac is not None and null_frac > null_power_max:
            return "NO_POWER"
        return "PASS"
    if rmsd_A <= partial_A:
        return "PARTIAL"
    return "FAIL"


def panel_verdict(rows, statements=None):
    """Is the panel readable, and which published clauses fall if not? Pure.

    `rows` = [{"name":..., "verdict":...}]. A clause is readable only if every target it consumes is PASS;
    `"*"` consumes the whole panel.
    """
    statements = SI_S1_STATEMENTS if statements is None else statements
    by_name = {r["name"]: r.get("verdict") for r in rows}
    passing = {n for n, v in by_name.items() if v == "PASS"}
    blocking = sorted(n for n, v in by_name.items() if v != "PASS")
    out_statements = []
    for st in statements:
        needed = set()
        for c in st["consumes"]:
            needed |= set(by_name) if c == "*" else {c}
        missing = sorted(n for n in needed if n not in passing)
        out_statements.append({"id": st["id"], "clause": st["clause"], "readable": not missing,
                               "blocked_by": missing, "why_it_consumes_those": st["why"]})
    return {
        "n_targets": len(rows),
        "n_pass": len(passing),
        "blocking_targets": blocking,
        "panel_readable": not blocking and len(rows) > 0,
        "si_s1_statements": out_statements,
        "_rule": "panel_readable is TRUE only if EVERY target PASSes. Every published clause is a maximum "
                 "or an every-survivor statement over the whole panel, so one unreadable receptor can "
                 "change a best-off-target and therefore every gap computed from it.",
        "_what_a_failure_licenses": "NOTHING is licensed by a failure except the statement that the "
                                    "margin is not currently readable. A failing target may not be "
                                    "dropped, its box may not be re-centred, and no band may be lowered.",
    }


def engineered_title(title):
    """(bool, why) — does this deposit title declare an engineered construct? Pure.

    Two signals, deliberately: `apo_pose_recovery.engineered_flag`'s word list (one home for the shared
    vocabulary), PLUS a bare point-mutation token like `S810L`, which that list cannot see. The MR LBD is
    very often deposited as the S810L gain-of-function mutant, and a title reading
    "MR LBD S810L in complex with ..." carries no word from the list at all. This is a PREFERENCE (R4),
    never a filter — it can reorder candidates, it can never reject one.
    """
    import re
    import apo_pose_recovery as apr
    t = (title or "")
    flagged, hits = apr.engineered_flag(t)
    muts = re.findall(r"\b[ACDEFGHIKLMNPQRSTVWY]\d{2,4}[ACDEFGHIKLMNPQRSTVWY]\b", t.upper())
    if muts:
        flagged = True
        hits = list(hits) + ["point-mutation token(s): %s" % ",".join(sorted(set(muts)))]
    return flagged, hits


def rank_resolve_candidates(entries, accession):
    """[(score, rec)] for `resolve`, applying RESOLVE_RULES to classified RCSB entries. Pure."""
    out = []
    for e in entries:
        why = []
        method = (e.get("method") or "").upper()
        if not e.get("sequence"):
            why.append("R1 no polymer entity referencing %s" % accession)
        if "X-RAY" not in method:
            why.append("R2 method %r is not X-ray" % e.get("method"))
        ligs = e.get("ligands") or []
        if not ligs:
            why.append("R3 no drug-like ligand")
        engineered, eng_why = engineered_title(e.get("title") or "")
        res = e.get("resolution_A")
        rec = {"pdb": e.get("pdb"), "title": e.get("title"), "method": e.get("method"),
               "resolution_A": res, "engineered_title": engineered, "engineered_why": eng_why,
               "ligands": [{k: l.get(k) for k in ("comp_id", "name", "mw")} for l in ligs],
               "rejected_because": why}
        if why:
            out.append(((9, 9, 9.9, e.get("pdb") or "ZZZZ"), rec))
            continue
        lig = max(ligs, key=lambda l: l.get("mw") or 0)
        rec["cognate"] = {"comp_id": lig.get("comp_id"), "name": lig.get("name"), "mw": lig.get("mw"),
                          "smiles": lig.get("smiles")}
        out.append(((0, 1 if engineered else 0, res if res is not None else 9.9,
                     e.get("pdb") or "ZZZZ"), rec))
    out.sort(key=lambda t: t[0])
    return out


def dock_protocol():
    """The panel's OWN docking settings, read from the panel spec and `antitarget_dock.py`'s source.

    Never re-typed. A control that docks with different settings from the thing it controls is not a
    control — and a hard-coded 8 here would keep passing after someone changed the panel dock.
    """
    import inspect
    import antitarget_dock as ad
    spec = json.load(open(PANEL))
    src = inspect.getsource(ad)
    exh = None
    marker = 'os.environ.get("EXHAUSTIVENESS", "'
    i = src.find(marker)
    if i >= 0:
        exh = src[i + len(marker):src.find('"', i + len(marker))]
    nm = None
    marker = '"--num_modes", "'
    i = src.find(marker)
    if i >= 0:
        nm = src[i + len(marker):src.find('"', i + len(marker))]
    return {"box_size": spec.get("box_size"), "exhaustiveness": exh, "num_modes": nm,
            "_read_from": "antitarget_panel.json box_size + antitarget_dock.py source"}


# ==================================================================================================
# THE RUN
# ==================================================================================================

def _refusal(where, why, **extra):
    r = {"where": where, "why": why}
    r.update(extra)
    return r


def _checkpoint(doc):
    """Write the artifact AFTER EVERY UNIT. CLAUDE.md's standing checkpoint rule, applied to a $0 job.

    ⚠ THE RULE IS NOT ABOUT MONEY, WHICH IS WHY IT APPLIES HERE. A single end-of-run `json.dump` means a
    wall-clock timeout on the flagged fan-out (38 docks, single-threaded) publishes NOTHING — not a
    partial panel, not the self-control that had already finished and is the GATE. The publish step is
    `if: always()`, so the only thing standing between a timeout and a lost verdict is whether the file
    exists on disk. Nine self-docks that completed are a result; losing them because a tenth ligand was
    slow is a bug, and it costs one `json.dump` per unit to prevent.
    """
    try:
        json.dump(doc, open(OUT, "w"), indent=2)
    except Exception as e:                                     # noqa: BLE001
        print("  [checkpoint] could not write %s: %s" % (OUT, e), file=sys.stderr)


def mode_resolve(doc):
    """Resolve MR / NR3C2 from UniProt by a live RCSB query and write it into the panel."""
    import apo_pose_recovery as apr
    spec = json.load(open(PANEL))
    names = [t["name"] for t in spec["targets"]]
    res = {"accession": MR_ACCESSION, "gene": MR_GENE, "name": MR_NAME, "rules": RESOLVE_RULES,
           "already_present": MR_NAME in names, "panel_before": names}

    # The flag itself has ONE home. Assert against it rather than trusting the constant above.
    try:
        screen = json.load(open(os.path.join(HERE, "nr4a-superfamily-selectivity.json")))
        flagged = {f["gene"]: f.get("accession") for f in screen.get("flagged_liabilities") or []}
        res["screen_flagged"] = flagged
        if flagged.get(MR_GENE) != MR_ACCESSION:
            doc["refusals"].append(_refusal(
                "resolve", "nr4a-superfamily-selectivity.json does not flag %s at %s (it has %r) — the "
                "panel addition would not be the receptor the screen flagged"
                % (MR_GENE, MR_ACCESSION, flagged.get(MR_GENE))))
            res["status"] = "REFUSED_flag_mismatch"
            doc["resolve"] = res
            return
        res["flag_confirmed_against"] = "nr4a-superfamily-selectivity.json flagged_liabilities"
    except Exception as e:                                     # noqa: BLE001
        doc["refusals"].append(_refusal("resolve", "could not read the sequence screen: %s" % e))

    if MR_NAME in names:
        row = [t for t in spec["targets"] if t["name"] == MR_NAME][0]
        res["status"] = "ALREADY_PRESENT"
        res["row"] = row
        doc["resolve"] = res
        return

    ids, why = apr.entries_for_accession(MR_ACCESSION)
    if not ids:
        doc["refusals"].append(_refusal("resolve", "RCSB returned no entries for %s: %s"
                                        % (MR_ACCESSION, why)))
        res["status"] = "REFUSED_no_entries"
        doc["resolve"] = res
        return
    res["n_entries"] = len(ids)
    entries, why2 = apr.entry_details(ids)
    if why2:
        doc["refusals"].append(_refusal("resolve", "RCSB metadata partially unavailable: %s" % why2))
    classified = [apr.classify_entry(e, MR_ACCESSION) for e in entries]
    ranked = rank_resolve_candidates(classified, MR_ACCESSION)
    res["candidates_ranked"] = [r for _s, r in ranked[:12]]
    usable = [(s, r) for s, r in ranked if not r["rejected_because"]]
    if not usable:
        doc["refusals"].append(_refusal(
            "resolve", "no %s entry satisfies R1-R3 (X-ray, references %s, carries a drug-like ligand); "
            "the panel is NOT extended and MR stays missing rather than being filled with a guess"
            % (MR_GENE, MR_ACCESSION)))
        res["status"] = "REFUSED_no_usable_entry"
        doc["resolve"] = res
        return
    pick = usable[0][1]
    row = {"name": MR_NAME, "class": "nuclear-receptor", "pdb_id": pick["pdb"],
           "ligand_resname": pick["cognate"]["comp_id"],
           "note": ("Mineralocorticoid receptor (%s, UniProt %s) LBD + %s. RESOLVED BY LIVE RCSB QUERY on "
                    "%s under antitarget_selfcontrol.RESOLVE_RULES, never from memory; %d entries "
                    "considered. Flagged by the 47-receptor sequence screen "
                    "(nr4a-superfamily-selectivity.json flagged_liabilities) alongside AR."
                    % (MR_GENE, MR_ACCESSION, pick["cognate"]["comp_id"],
                       time.strftime("%Y-%m-%d", time.gmtime()), len(ids)))}
    spec["targets"].append(row)
    spec.setdefault("_provenance", {})[MR_NAME] = {
        "resolved_by": "antitarget_selfcontrol.py mode=resolve",
        "accession": MR_ACCESSION, "n_entries_considered": len(ids),
        "title": pick["title"], "resolution_A": pick["resolution_A"],
        "engineered_title": pick["engineered_title"], "rules": RESOLVE_RULES,
        "cognate_ligand": pick["cognate"],
    }
    json.dump(spec, open(PANEL, "w"), indent=2)
    res["status"] = "ADDED"
    res["row"] = row
    res["resolution_A"] = pick["resolution_A"]
    res["title"] = pick["title"]
    doc["resolve"] = res


def _top_pose_mol(sdf_path):
    """(mol, dG, why) for the top-ranked smina pose."""
    from rdkit import Chem
    if not os.path.exists(sdf_path):
        return None, None, "no pose file"
    supp = Chem.SDMolSupplier(sdf_path, removeHs=True, sanitize=True)
    mol = None
    for m in supp:
        if m is not None:
            mol = m
            break
    if mol is None:
        return None, None, "pose file has no parsable molecule"
    dg = None
    for b in open(sdf_path).read().split("$$$$"):
        ls = b.splitlines()
        for j, ln in enumerate(ls):
            if "minimizedAffinity" in ln:
                try:
                    dg = float(ls[j + 1].strip())
                except (ValueError, IndexError):
                    pass
                break
        if dg is not None:
            break
    return mol, dg, None


def _smina(receptor_pdb, center, box, lig_sdf, out_sdf, exh, num_modes):
    import nr4a3_dock as ndock
    smina = ndock._which("smina")
    if not smina:
        return "smina not on PATH"
    cmd = [smina, "-r", receptor_pdb, "-l", lig_sdf,
           "--center_x", str(center[0]), "--center_y", str(center[1]), "--center_z", str(center[2]),
           "--size_x", str(box), "--size_y", str(box), "--size_z", str(box),
           "--exhaustiveness", str(exh), "--num_modes", str(num_modes), "-o", out_sdf]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=PER_DOCK_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return "dock exceeded PER_DOCK_TIMEOUT_S=%ds" % PER_DOCK_TIMEOUT_S
    if p.returncode != 0:
        return "smina rc=%d: %s" % (p.returncode, (p.stderr or "")[-300:])
    return None


def _ccd_smiles(comp_id):
    """CCD reference SMILES for a component id, from RCSB. (smiles, why)."""
    import apo_pose_recovery as apr
    body = json.dumps({
        "query": "query($id:String!){chem_comp(comp_id:$id){"
                 "rcsb_chem_comp_descriptor{SMILES_stereo} chem_comp{id name formula_weight}}}",
        "variables": {"id": comp_id.upper()}}).encode()
    try:
        doc = apr._get(apr.RCSB_GRAPHQL, data=body)
    except Exception as e:                                     # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)
    cc = ((doc.get("data") or {}).get("chem_comp")) or {}
    smi = ((cc.get("rcsb_chem_comp_descriptor") or {}).get("SMILES_stereo"))
    if not smi:
        return None, "RCSB returned no SMILES_stereo for %s" % comp_id
    return smi, None


def _pick_copy(lig_lines, center):
    """The single ligand copy whose centroid is nearest the box centre (a chain may hold several)."""
    groups = {}
    for ln in lig_lines:
        groups.setdefault((ln[17:20].strip(), ln[21], ln[22:27]), []).append(ln)
    if not groups:
        return [], None
    def _d(gl):
        n = len(gl)
        cx = sum(float(l[30:38]) for l in gl) / n
        cy = sum(float(l[38:46]) for l in gl) / n
        cz = sum(float(l[46:54]) for l in gl) / n
        return (cx - center[0]) ** 2 + (cy - center[1]) ** 2 + (cz - center[2]) ** 2
    gid = min(groups, key=lambda g: _d(groups[g]))
    return groups[gid], gid


def _all_cognate_copies(all_lines, comp_id):
    """{gid: [lines]} for EVERY copy of the cognate component in the file, all chains. Pure."""
    g = {}
    for ln in all_lines or []:
        if ln.startswith("HETATM") and ln[17:20].strip() == (comp_id or "").strip():
            if ln[16] not in (" ", "A"):
                continue
            g.setdefault((ln[17:20].strip(), ln[21], ln[22:27]), []).append(ln)
    return g


def _centroid(mol):
    c = mol.GetConformer()
    n = mol.GetNumAtoms()
    return tuple(sum(getattr(c.GetAtomPosition(i), a) for i in range(n)) / n for a in ("x", "y", "z"))


def _score_target(t, keep_cofactors, doc, arm):
    """Re-dock ONE panel target's own cognate ligand and diagnose the result. Returns the row.

    ⛔ NO `continue`s AND NO SHORT-CIRCUITS: every exit path returns a row, so a target can never vanish
    from the panel by failing early. An absent row and a failing row are different claims.
    """
    import apo_pose_recovery as apr
    import nr4a3_dock as ndock
    import antitarget_prep as prep
    from rdkit.Chem import rdMolAlign

    b = bands()
    proto = dock_protocol()
    box, exh, nmodes = proto["box_size"], proto["exhaustiveness"], proto["num_modes"]
    t0 = time.time()
    row = {"name": t["name"], "class": t.get("class"), "pdb_id": t.get("pdb_id"),
           "ligand_resname_declared": t.get("ligand_resname"), "arm": arm}

    def _fail(why, **extra):
        row.update({"verdict": "UNSCORED", "why": why})
        row.update(extra)
        doc["refusals"].append(_refusal("selfcontrol[%s]/%s" % (arm, t["name"]), why))
        row["elapsed_s"] = round(time.time() - t0, 1)
        return row

    try:
        f = prep.prep_target_full(t, keep_cofactors=keep_cofactors)
    except Exception as e:                                     # noqa: BLE001
        return _fail("receptor prep failed: %s" % e)

    all_lines = f.pop("all_lines", None)          # never serialised — it is the whole PDB
    row.update({
        "center": f["center"], "chain": f["chain"], "n_res": f["n_res"],
        "cognate_comp_id": f["lig_resname"], "centre_source": f["centre_source"],
        # ⚠ THE SILENT FALLBACK, NOW VISIBLE. False means the panel's declared ligand code is not in the
        # file and the prep centred the box on a different molecule of its own choosing.
        "ligand_resname_matched": f["ligand_resname_matched"],
        "cofactors_kept": f["cofactors"]["kept"],
        "stripped_in_pocket": f["cofactors"]["dropped_in_pocket"],
        "keep_cofactors": f["keep_cofactors"],
    })
    if not f["ligand_resname_matched"]:
        doc["refusals"].append(_refusal(
            "panel/%s" % t["name"],
            "antitarget_panel.json declares ligand_resname %r, which is NOT in %s; the prep fell back to "
            "the largest drug-like HETATM group (%s) and the box is centred on THAT. The panel row is a "
            "data error — reported, not silently accepted."
            % (f["ligand_resname_declared"], t.get("pdb_id"), f["lig_resname"])))

    copy_lines, gid = _pick_copy(f["lig_lines"], f["center"])
    row["n_copies_in_chain"] = len({(l[17:20].strip(), l[21], l[22:27]) for l in f["lig_lines"]})
    row["copy_used"] = "".join(gid).strip() if gid else None
    if not copy_lines:
        return _fail("no crystallographic ligand copy to score against")

    smi, why = _ccd_smiles(f["lig_resname"])
    row["cognate_smiles"] = smi
    if not smi:
        return _fail("no CCD SMILES: %s" % why)

    xtal, why = apr.crystal_mol(copy_lines, smi)
    if xtal is None:
        return _fail("crystal pose not buildable: %s" % why)
    row["n_heavy_atoms"] = xtal.GetNumAtoms()

    rec_pdb = os.path.join(WORK, "%s_%s_receptor.pdb" % (arm, t["name"]))
    open(rec_pdb, "w").write(f["receptor_pdb"])
    row["receptor_atom_lines"] = f["receptor_pdb"].count("\n")
    lig_sdf = os.path.join(WORK, "%s_%s_cognate.sdf" % (arm, t["name"]))
    pose_sdf = os.path.join(WORK, "%s_%s_cognate_pose.sdf" % (arm, t["name"]))
    if not ndock.make_sdf([(f["lig_resname"], f["lig_resname"], smi)], lig_sdf):
        return _fail("rdkit could not embed the cognate ligand")
    err = _smina(rec_pdb, f["center"], box, lig_sdf, pose_sdf, exh, nmodes)
    if err:
        return _fail("dock failed: %s" % err)
    mol, dg, why = _top_pose_mol(pose_sdf)
    row["self_dock_dG"] = dg
    if mol is None:
        return _fail("no scorable pose: %s" % why)
    try:
        row["rmsd_A"] = round(float(rdMolAlign.CalcRMS(mol, xtal)), 3)
    except Exception as e:                                     # noqa: BLE001
        return _fail("RMSD failed: %s: %s" % (type(e).__name__, e))

    # ------------------------------------------------------------------ diagnostics, on every row
    # (1) SAME SITE, WRONG ORIENTATION vs WRONG SITE. A large RMSD with a small centroid displacement is
    #     a flipped/reoriented ligand in the same cavity; a large displacement is a different subsite.
    #     These have different causes and different repairs, and RMSD alone cannot tell them apart.
    try:
        cx, cy, cz = _centroid(mol)
        xx, xy, xz = _centroid(xtal)
        row["centroid_shift_A"] = round(((cx - xx) ** 2 + (cy - xy) ** 2 + (cz - xz) ** 2) ** 0.5, 3)
    except Exception:                                          # noqa: BLE001
        row["centroid_shift_A"] = None
    # (2) IS THE DOCKED POSE A DIFFERENT *CRYSTALLOGRAPHIC* COPY? Some deposits place the same ligand in
    #     several orientations in one cavity. Scoring against one copy would then call a genuinely
    #     observed pose a miss. Report the BEST RMSD over every copy in the file, and which copy it was.
    best_any, best_gid, n_copies = row["rmsd_A"], row.get("copy_used"), row["n_copies_in_chain"]
    copies = _all_cognate_copies(all_lines, f["lig_resname"])
    n_copies = max(n_copies, len(copies))
    for cgid, clines in copies.items():
        cm, cwhy = apr.crystal_mol(clines, smi)
        if cm is None:
            continue
        try:
            r = float(rdMolAlign.CalcRMS(mol, cm))
        except Exception:                                      # noqa: BLE001
            continue
        if r < best_any:
            best_any, best_gid = round(r, 3), "".join(cgid).strip()
    row["n_cognate_copies_in_file"] = n_copies
    row["rmsd_to_best_crystal_copy_A"] = round(best_any, 3)
    row["best_crystal_copy"] = best_gid
    row["a_different_copy_would_pass"] = bool(
        row["rmsd_A"] > b["recovered_rmsd_A"] >= row["rmsd_to_best_crystal_copy_A"])

    # (3) POWER CONTROL — the same box the dock searched.
    try:
        null = apr.random_in_box_null(xtal, f["center"], (float(box), float(box), float(box)))
        row["null"] = null
        row["null_frac_under_criterion"] = null.get("p_within_criterion")
    except Exception as e:                                     # noqa: BLE001
        row["null_frac_under_criterion"] = None
        doc["refusals"].append(_refusal("selfcontrol[%s]/%s/null" % (arm, t["name"]),
                                        "power control failed: %s: %s" % (type(e).__name__, e)))

    # (4) fnat — secondary, never gating.
    try:
        xconf = xtal.GetConformer()
        xpts = [(xconf.GetAtomPosition(i).x, xconf.GetAtomPosition(i).y, xconf.GetAtomPosition(i).z)
                for i in range(xtal.GetNumAtoms())]
        pconf = mol.GetConformer()
        ppts = [(pconf.GetAtomPosition(i).x, pconf.GetAtomPosition(i).y, pconf.GetAtomPosition(i).z)
                for i in range(mol.GetNumAtoms())]
        cut = apr._contact_a()
        nat = set(apr.residues_near(f["receptor_pdb"], xpts, cut))
        got = set(apr.residues_near(f["receptor_pdb"], ppts, cut))
        row["fnat"] = round(len(nat & got) / len(nat), 3) if nat else None
    except Exception as e:                                     # noqa: BLE001
        row["fnat"] = None
        doc["refusals"].append(_refusal("selfcontrol[%s]/%s/fnat" % (arm, t["name"]),
                                        "%s: %s" % (type(e).__name__, e)))

    row["verdict"] = target_verdict(row.get("rmsd_A"), row.get("null_frac_under_criterion"),
                                    b["recovered_rmsd_A"], b["partial_rmsd_A"], b["null_power_max"])
    row["elapsed_s"] = round(time.time() - t0, 1)
    for p in (lig_sdf, pose_sdf):
        try:
            os.remove(p)
        except OSError:
            pass
    return row


def _run_arm(doc, arm, keep_cofactors):
    """One full pass of the panel on one receptor build. Checkpoints after every target."""
    spec = json.load(open(PANEL))
    rows = []
    doc.setdefault("arms", {})[arm] = {
        "keep_cofactors": keep_cofactors, "targets": rows, "_partial": True,
        "_partial_note": "the run had not reached this arm's panel verdict when this was written; "
                         "per-target rows are complete, the verdict is absent",
    }
    _checkpoint(doc)
    for t in spec["targets"]:
        row = _score_target(t, keep_cofactors, doc, arm)
        rows.append(row)
        _checkpoint(doc)
        print("  [%s] %-8s %-9s rmsd %-8s (best copy %-8s) shift %-8s dG %-9s cofactors_kept %s" % (
            arm, row.get("name"), row.get("verdict"), row.get("rmsd_A"),
            row.get("rmsd_to_best_crystal_copy_A"), row.get("centroid_shift_A"),
            row.get("self_dock_dG"),
            [k["resname"] for k in row.get("cofactors_kept", [])]), flush=True)
    v = panel_verdict([{"name": r["name"], "verdict": r.get("verdict")} for r in rows])
    doc["arms"][arm]["_partial"] = False
    doc["arms"][arm].pop("_partial_note", None)
    doc["arms"][arm].update(v)
    _checkpoint(doc)
    return doc["arms"][arm]


def mode_selfcontrol(doc):
    """THE GATE — re-dock every panel target's own cognate ligand through the identical protocol.

    ★ RUN AS AN A/B OVER THE RECEPTOR BUILD, NOT AS A REPLACEMENT (2026-08-03). The first run of this
    control FAILED — 7 of 10, with CYP3A4 / PPARG / PXR at 9.503 / 6.761 / 6.87 A against a 2.00 A
    criterion — and the repair is `antitarget_prep`'s cofactor retention. Simply switching the receptor
    over and re-reporting would have destroyed the only evidence that says WHICH receptor produced the
    numbers already published in SI §S1. So both are run:

        arm `stripped` — the receptor as it was when SI §S1's margins were computed (no cofactors)
        arm `repaired` — the same predicate applied to all ten: retain a cofactor or metal ion that the
                         cognate ligand actually contacts

    The HEADLINE verdict is the repaired arm, because that is the instrument going forward. The stripped
    arm is retained as the provenance of the published numbers, and the per-target delta between them is
    what attributes any change to the repair rather than to chance.
    """
    os.makedirs(WORK, exist_ok=True)
    doc["criterion"] = bands()
    doc["protocol"] = dock_protocol()
    stripped = _run_arm(doc, "stripped", keep_cofactors=False)
    repaired = _run_arm(doc, "repaired", keep_cofactors=True)

    by_name = {}
    for r in stripped["targets"]:
        by_name.setdefault(r["name"], {})["stripped"] = r
    for r in repaired["targets"]:
        by_name.setdefault(r["name"], {})["repaired"] = r
    delta = []
    for name, pair in by_name.items():
        s, k = pair.get("stripped") or {}, pair.get("repaired") or {}
        delta.append({
            "name": name,
            "stripped_rmsd_A": s.get("rmsd_A"), "repaired_rmsd_A": k.get("rmsd_A"),
            "stripped_verdict": s.get("verdict"), "repaired_verdict": k.get("verdict"),
            "cofactors_kept": [c["resname"] for c in k.get("cofactors_kept", [])],
            "still_stripped_in_pocket": [c["resname"] for c in k.get("stripped_in_pocket", [])],
            "repair_changed_the_receptor": bool(k.get("cofactors_kept")),
            "centroid_shift_A": k.get("centroid_shift_A"),
            "rmsd_to_best_crystal_copy_A": k.get("rmsd_to_best_crystal_copy_A"),
            "a_different_copy_would_pass": k.get("a_different_copy_would_pass"),
            "ligand_resname_matched": k.get("ligand_resname_matched"),
        })
    delta.sort(key=lambda d: d["name"])

    # THE HEADLINE IS THE REPAIRED ARM. `selfcontrol` keeps the shape every downstream reader already
    # parses, so nothing has to learn about arms to read the verdict.
    doc["selfcontrol"] = dict(repaired)
    doc["selfcontrol"]["_arm"] = "repaired"
    doc["selfcontrol"]["_the_other_arm"] = {
        "arm": "stripped", "panel_readable": stripped.get("panel_readable"),
        "n_pass": stripped.get("n_pass"), "blocking_targets": stripped.get("blocking_targets"),
        "_why_it_is_kept": "it is the receptor build that produced SI §S1's published margins; deleting "
                           "it would delete the provenance of a published number",
    }
    doc["repair_delta"] = delta
    doc["repair_rule"] = {
        "what": "retain a HETATM group iff it is a recognised prosthetic group/cofactor OR a metal ion, "
                "AND it lies within antitarget_prep.COFACTOR_CONTACT_A of the cognate ligand copy the "
                "box is centred on",
        "uniform": "one predicate, evaluated identically for all ten targets — it is not a list of "
                   "exceptions, and for a target with nothing in contact it is a no-op",
        "why_it_is_not_tuning": "the frozen rule forbids dropping a failing target, re-centring its box "
                                "or lowering a band. This does none of those: it makes the RECEPTOR more "
                                "complete, not the CRITERION more forgiving, and it is applied to "
                                "passing targets too",
        "one_home": "antitarget_prep.COFACTORS / METAL_IONS / COFACTOR_CONTACT_A",
    }
    _checkpoint(doc)


def mode_flagged(doc):
    """Dock denovo_401 + the carried candidates into the flagged receptors (AR and MR)."""
    import nr4a3_dock as ndock
    import antitarget_prep as prep

    proto = dock_protocol()
    box, exh, nmodes = proto["box_size"], proto["exhaustiveness"], proto["num_modes"]
    os.makedirs(WORK, exist_ok=True)
    spec = json.load(open(PANEL))
    flagged_names = {"AR", MR_NAME}
    targets = [t for t in spec["targets"] if t["name"] in flagged_names]
    mols = []
    for fn in ("nr4a3-antitarget-denovo401.json", "nr4a3-antitarget-candidates.json"):
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            doc["refusals"].append(_refusal("flagged", "missing candidate file %s" % fn))
            continue
        d = json.load(open(p))
        for c in d.get("candidates", []):
            if c.get("name") and c.get("smiles"):
                mols.append({"name": c["name"], "drug": c.get("drug"), "smiles": c["smiles"],
                             "source": fn})
    doc["flagged"] = {"receptors": [t["name"] for t in targets], "n_molecules": len(mols), "rows": []}
    if len(targets) < 2:
        doc["refusals"].append(_refusal(
            "flagged", "only %d of the 2 flagged receptors are in the panel (%s) — run mode=resolve first"
            % (len(targets), [t["name"] for t in targets])))
    for t in targets:
        try:
            f = prep.prep_target_full(t)
        except Exception as e:                                 # noqa: BLE001
            doc["refusals"].append(_refusal("flagged/%s" % t["name"], "receptor prep failed: %s" % e))
            continue
        rec_pdb = os.path.join(WORK, "%s_receptor.pdb" % t["name"])
        open(rec_pdb, "w").write(f["receptor_pdb"])
        for m in mols:
            lig_sdf = os.path.join(WORK, "%s_%s.sdf" % (t["name"], m["name"]))
            pose_sdf = os.path.join(WORK, "%s_%s.pose.sdf" % (t["name"], m["name"]))
            row = {"target": t["name"], "label": m["name"], "drug": m.get("drug"),
                   "source": m["source"]}
            if not ndock.make_sdf([(m["name"], m["name"], m["smiles"])], lig_sdf):
                row.update({"dG": None, "note": "embed_failed"})
                doc["flagged"]["rows"].append(row)
                _checkpoint(doc)
                continue
            err = _smina(rec_pdb, f["center"], box, lig_sdf, pose_sdf, exh, nmodes)
            if err:
                row.update({"dG": None, "note": err})
                doc["flagged"]["rows"].append(row)
                _checkpoint(doc)
                continue
            _mol, dg, why = _top_pose_mol(pose_sdf)
            row.update({"dG": dg, "note": "ok" if dg is not None else (why or "no_affinity")})
            doc["flagged"]["rows"].append(row)
            _checkpoint(doc)
            for p in (lig_sdf, pose_sdf):
                try:
                    os.remove(p)
                except OSError:
                    pass
        print("  flagged %s: %d rows" % (t["name"], len(doc["flagged"]["rows"])), flush=True)

    doc["flagged"]["margin_refusal"] = {
        "refused": True,
        "what": "no NR4A3-vs-off-target MARGIN is computed here, for either flagged receptor",
        "why": [
            "GATE: the cognate-ligand self-control governs whether ANY margin from this panel may be "
            "read, and it is reported in `selfcontrol` — a margin emitted beside a failing control would "
            "be exactly the number the rung exists to stop.",
            "PROVENANCE: the NR4A3 column the published margins subtract is NOT COMMITTED ANYWHERE IN "
            "THIS REPO. `nr4a3-antitarget.json` / `nr4a3-antitarget.jsonl` — the raw (drug x target) dG "
            "matrix `antitarget_dock.py` writes — exist only under the S3 output prefix; the repo carries "
            "the candidate lists and the prose, not the numbers. Recomputing an NR4A3 dG here would need "
            "the release receptor and box that lane used, and inventing either would fabricate the "
            "denominator of a published figure.",
        ],
        "what_is_emitted_instead": "absolute smina dG per (molecule, flagged receptor), under the panel's "
                                   "own protocol, with the receptor's provenance on every row",
    }


# ==================================================================================================
# REPORT
# ==================================================================================================

def render_markdown(doc):
    L = []
    L.append("# Anti-target panel — the cognate-ligand SELF-CONTROL (rung `R14-a`)\n")
    L.append("_Generated by `antitarget_selfcontrol.py`. $0 — free CI runner, no GPU, no rental._\n")
    sc = doc.get("selfcontrol") or {}
    if sc:
        L.append("## Verdict\n")
        L.append("**`panel_readable` = %s** — %d of %d targets PASS.%s\n"
                 % (sc.get("panel_readable"), sc.get("n_pass", 0), sc.get("n_targets", 0),
                    ("  Blocking: **%s**." % ", ".join(sc["blocking_targets"]))
                    if sc.get("blocking_targets") else ""))
        L.append("\n⛔ Until every target PASSes, **no anti-target margin from this panel may be read — "
                 "including the one SI §S1 already publishes.**\n")
        other = sc.get("_the_other_arm") or {}
        if other:
            L.append("\nReceptor build reported above: **`%s`**. The **`%s`** arm — the build that "
                     "produced SI §S1's published margins — returns `panel_readable = %s` (%s of %s "
                     "pass, blocking %s).\n"
                     % (sc.get("_arm"), other.get("arm"), other.get("panel_readable"),
                        other.get("n_pass"), sc.get("n_targets"),
                        ", ".join(other.get("blocking_targets") or []) or "none"))
        rr = doc.get("repair_rule") or {}
        if rr:
            L.append("\n**The repair, stated as one predicate applied to all ten targets:** %s. "
                     "*Why this is not tuning:* %s\n" % (rr.get("what"), rr.get("why_it_is_not_tuning")))
        delta = doc.get("repair_delta") or []
        if delta:
            L.append("\n### Stripped → repaired, per target\n")
            L.append("| target | stripped RMSD | repaired RMSD | stripped | repaired | cofactor kept | "
                     "still stripped in pocket | centroid shift (Å) | best crystal copy (Å) |")
            L.append("|---|---|---|---|---|---|---|---|---|")
            for d in delta:
                L.append("| %s | %s | %s | %s | **%s** | %s | %s | %s | %s |" % (
                    d["name"], d.get("stripped_rmsd_A", "—"), d.get("repaired_rmsd_A", "—"),
                    d.get("stripped_verdict"), d.get("repaired_verdict"),
                    ", ".join(d.get("cofactors_kept") or []) or "—",
                    ", ".join(d.get("still_stripped_in_pocket") or []) or "—",
                    d.get("centroid_shift_A", "—"), d.get("rmsd_to_best_crystal_copy_A", "—")))
        L.append("\n| target | class | PDB | cognate | RMSD (Å) | verdict | self-dock ΔG | fnat | "
                 "P(random ≤ 2 Å) |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for r in sc.get("targets", []):
            L.append("| %s | %s | %s | %s | %s | **%s** | %s | %s | %s |" % (
                r.get("name"), r.get("class"), r.get("pdb_id"), r.get("cognate_comp_id"),
                r.get("rmsd_A", "—"), r.get("verdict"), r.get("self_dock_dG", "—"),
                r.get("fnat", "—"), r.get("null_frac_under_criterion", "—")))
        L.append("\n### What each published SI §S1 clause can still say\n")
        L.append("| clause | readable | blocked by |")
        L.append("|---|---|---|")
        for st in sc.get("si_s1_statements", []):
            L.append("| %s — %s | %s | %s |" % (st["id"], st["clause"], st["readable"],
                                                ", ".join(st["blocked_by"]) or "—"))
    rv = doc.get("resolve") or {}
    if rv:
        L.append("\n## MR / NR3C2 — the missing flagged receptor\n")
        L.append("- status: **%s**%s" % (rv.get("status"),
                                         ("  ·  %s" % rv["row"]["pdb_id"]) if rv.get("row") else ""))
        if rv.get("title"):
            L.append("- %s (%s Å)" % (rv["title"], rv.get("resolution_A")))
        L.append("- resolved by a live RCSB query over %s entries for UniProt %s, never from memory"
                 % (rv.get("n_entries", "?"), rv.get("accession")))
    fl = doc.get("flagged") or {}
    if fl.get("rows"):
        L.append("\n## `denovo_401` + carried candidates in the flagged receptors\n")
        # `.get`, because a CARRIED-FORWARD flagged block may predate the refusal field, and a renderer
        # that raises on an old block would make the merge that preserved it look like the bug.
        L.append("⛔ **No margin is computed.** %s\n"
                 % "; ".join((fl.get("margin_refusal") or {}).get("why") or ["see the artifact"]))
        # DERIVED from the rows rather than read from a sibling field, so a carried-forward block that
        # predates `receptors` still renders instead of taking the whole report down with it.
        recs = fl.get("receptors") or sorted({r["target"] for r in fl["rows"]})
        L.append("| molecule | drug | %s |" % " | ".join(recs))
        L.append("|---|---|%s" % ("---|" * len(recs)))
        by = {}
        for r in fl["rows"]:
            by.setdefault(r["label"], {})[r["target"]] = r.get("dG")
        for lab in sorted(by):
            drug = next((r.get("drug") for r in fl["rows"] if r["label"] == lab), "")
            L.append("| %s | %s | %s |" % (lab, drug or "—",
                                           " | ".join(str(by[lab].get(t, "—")) for t in recs)))
    if doc.get("refusals"):
        L.append("\n## Refusals\n")
        for r in doc["refusals"]:
            L.append("- **%s** — %s" % (r["where"], r["why"]))
    return "\n".join(L) + "\n"


def map_edits(doc):
    """Roadmap edits this run REQUIRES — routed, never applied. This module does not own the map."""
    sc = doc.get("selfcontrol") or {}
    if not sc:
        return []
    readable = sc.get("panel_readable")
    blocking = ", ".join(sc.get("blocking_targets") or []) or "none"
    verdict_txt = ("the self-control **PASSES on all %d targets**, so the panel's margins are readable"
                   % sc.get("n_targets", 0)) if readable else (
        "the self-control **FAILS on %s**, so no anti-target margin from this panel may be read — "
        "including SI §S1's" % blocking)
    return [{
        "section": "THE ORDERED PLAN → RUNG S",
        "anchor": "**`[ ]` `R14-a` · Complete the anti-target panel, and run the self-control it has "
                  "never run**",
        "current_text": "**`[ ]` `R14-a` · Complete the anti-target panel, and run the self-control it "
                        "has never run**",
        "proposed_text": "**`[x]` `R14-a` · Complete the anti-target panel, and run the self-control it "
                         "has never run — RAN 2026-08-03, $0**",
        "why": "the rung ran on a free CI runner at $0; %s" % verdict_txt,
        "artifact": "research/modalities/antitarget-selfcontrol.json",
    }, {
        "section": "§10.1 row 10",
        "anchor": "⭑ **`R14-a` IS AN ASSEMBLY JOB, NOT A BUILD, AND IT IS THE HIGHER-VALUE HALF**",
        "current_text": "⭑ **`R14-a` IS AN ASSEMBLY JOB, NOT A BUILD, AND IT IS THE HIGHER-VALUE HALF**",
        "proposed_text": "✅ **`R14-a` RAN 2026-08-03 ($0, CI) — %s.** ⭑ It was an ASSEMBLY JOB, NOT A "
                         "BUILD, AND IT WAS THE HIGHER-VALUE HALF" % verdict_txt,
        "why": "row 10 records R14-a as not started; it has now run and returned a verdict that governs "
               "a number the paper already publishes",
        "artifact": "research/modalities/antitarget-selfcontrol.json",
    }] + criterion_decision_edits(doc) + [{
        # The state cell is a different cell from the next-action cell; updating only the latter leaves
        # the row reading "○ not started" beside "✅ RAN". `R14` stays partial because `R14-b` is unrun
        # and registered DO-NOT-LAUNCH.
        "section": "§10.1 row 10 — the state cell",
        "anchor": "| `R14` | ○ **not started** |",
        "current_text": "| `R14` | ○ **not started** |",
        "proposed_text": "| `R14` | ◐ **`R14-a` ran 2026-08-03 · `R14-b` not started (⛔ DO-NOT-LAUNCH)** |",
        "why": "the row's next-action cell records R14-a as run while its state cell still says nothing "
               "has started; R14-b remains unrun and rate-line blocked, so the row is partial, not done",
        "artifact": "research/modalities/antitarget-selfcontrol.json",
    }, {
        "section": "THE ORDERED PLAN → RUNG S — R14-a's 'never-run' clause",
        "anchor": "and that the panel has a **never-run cognate-ligand self-control.**",
        "current_text": "and that the panel has a **never-run cognate-ligand self-control.**",
        "proposed_text": ("and that the panel has a cognate-ligand self-control **which has now RUN "
                          "(2026-08-03, $0): %s** "
                          "([`antitarget-selfcontrol.json`](../modalities/antitarget-selfcontrol.json))."
                          % verdict_txt),
        "why": "the rung text still describes the control as never run, and it has run — leaving that "
               "sentence in place would make the program's own plan a stale fact",
        "artifact": "research/modalities/antitarget-selfcontrol.json",
    }]


def criterion_decision_edits(doc):
    """⛔ REGISTER THE ONE THING THIS RUN CANNOT DECIDE FOR ITSELF, so it is not lost in an artifact.

    CYP3A4's failure is not a docking failure. 2V0M carries EIGHT copies of ketoconazole, TWO of them in
    the docked chain, and with the haem restored the top pose lands **1.108 Å from a different deposited
    copy** than the one it is scored against. The pre-registered criterion says "the crystallographic
    copy", and for a multi-copy site that phrase has no referent.

    ★ WHY THIS IS A ROUTED DECISION AND NOT A FIX I APPLY. Amending the criterion after seeing which
    amendment passes is exactly the tuning the frozen rule forbids — the difference between "scored
    against any deposited copy" and "scored against the nearest copy" is invisible until you know the
    answer, and by then it is not a pre-registration. So the run reports both numbers, leaves the verdict
    FAIL, and puts the amendment on the board where it can be decided in writing BEFORE it is used.
    """
    sc = doc.get("selfcontrol") or {}
    rows = {r["name"]: r for r in sc.get("targets", [])}
    multi = [r for r in rows.values()
             if r.get("a_different_copy_would_pass") and r.get("verdict") != "PASS"]
    if not multi:
        return []
    detail = "; ".join(
        "%s: scored %s Å against copy %s, but %s Å from copy %s (%s copies in the deposit)"
        % (r["name"], r.get("rmsd_A"), r.get("copy_used"), r.get("rmsd_to_best_crystal_copy_A"),
           r.get("best_crystal_copy"), r.get("n_cognate_copies_in_file")) for r in multi)
    return [{
        "section": "Open decisions",
        "anchor": "## Open decisions",
        "current_text": "## Open decisions",
        "proposed_text": (
            "## Open decisions\n\n"
            "- ⛔ **NEW 2026-08-03 — the anti-target self-control's criterion is UNDER-SPECIFIED for a "
            "multi-copy deposit, and it is currently deciding a FAIL.** %s. The pre-registered criterion "
            "reads *\"the crystallographic copy of the same ligand\"*, which has no referent when a "
            "deposit places several copies of the cognate in one site. ⚠ **The verdict was left FAIL and "
            "must stay there until this is ruled on**, because choosing the copy after seeing which one "
            "passes is the tuning the rung's own frozen rule forbids. The decision is one sentence — "
            "score against *any* deposited copy, or against a *named* one — and it must be written down "
            "BEFORE it is applied. Evidence: "
            "[`antitarget-selfcontrol.json`](../modalities/antitarget-selfcontrol.json) → "
            "`repair_delta`.\n" % detail),
        "why": "the run produced a finding it is not entitled to act on. Leaving it only in the artifact "
               "is how a caveat with nowhere to go gets silently dropped",
        "artifact": "research/modalities/antitarget-selfcontrol.json",
    }]


def si_edits(doc):
    """⛔ THE PUBLICATION-INTEGRITY EDIT. Emitted ONLY while the panel is unreadable.

    This is the edit that matters and it is not a checkbox. Four sentences are already written into
    SI §S1, and each is a maximum or an every-survivor statement across the whole panel, so a single
    unreadable receptor changes all four. A rung marked done beside an SI that still asserts them would
    be the worst possible outcome of running the control at all.

    ⚠ It is emitted against the SI, not the roadmap, and `route_map_edits.py` is told so by `file`. The
    edit does not delete the result — deleting it would lose a real screen — it CONDITIONS it, which is
    what the frozen rule permits: "nothing is licensed by a failure except the statement that the margin
    is not currently readable."
    """
    sc = doc.get("selfcontrol") or {}
    if not sc or sc.get("panel_readable"):
        return []
    blocking = sc.get("blocking_targets") or []
    rows = {r["name"]: r for r in sc.get("targets", [])}
    detail = "; ".join("%s %s Å" % (n, rows.get(n, {}).get("rmsd_A")) for n in blocking)
    band = (doc.get("criterion") or {}).get("recovered_rmsd_A")
    return [{
        "file": "research/manuscripts/nr4a3-degrader-paper-SI.md",
        "section": "SI §S1 — the anti-target panel paragraph (3)",
        "anchor": "*(3) The anti-target panel disqualifies all of them.*",
        "current_text": "*(3) The anti-target panel disqualifies all of them.*",
        "proposed_text": (
            "*(3) The anti-target panel disqualifies all of them.* ⛔ **NOT CURRENTLY READABLE "
            "(2026-08-03).** The panel's cognate-ligand self-control — each target's own "
            "co-crystallised ligand re-docked through the identical protocol — recovers %d of %d "
            "crystallographic poses; **%s** miss the %.2f Å field-standard redocking criterion (%s). "
            "Every claim in this paragraph is a maximum or an every-survivor statement across the whole "
            "panel, so an unreadable receptor propagates into all of them. The screen was run and is "
            "reported; the *margins* below may not be quoted until the control passes "
            "([`antitarget-selfcontrol.json`](../modalities/antitarget-selfcontrol.json))."
            % (sc.get("n_pass", 0), sc.get("n_targets", 0), ", ".join(blocking), band or 2.0, detail)),
        "why": "a sentence already written into the SI asserts a panel-wide maximum over receptors the "
               "panel's own self-control cannot dock into. The number is not deleted — it is "
               "conditioned, which is the only thing the failure licenses",
        "artifact": "research/modalities/antitarget-selfcontrol.json",
    }, {
        # ⛔ IT IS NOT ONLY THE SI. The same panel-wide maximum is asserted in the MAIN TEXT, and an SI
        # caveat beside an unqualified main-text claim is worse than neither: a reader who never opens
        # the SI sees only the unconditioned sentence. Found by grepping the paper for "anti-target"
        # rather than by trusting the brief's scoping to the SI.
        "file": "research/manuscripts/nr4a3-degrader-paper.md",
        "section": "main text — the counter-screen sentence",
        "anchor": "**At marketed-library scale, no repurposing candidate survives the counter-screen**",
        "current_text": "**Full screen and target panel: SI §S1.**",
        "proposed_text": ("**Full screen and target panel: SI §S1.** ⛔ **The counter-screen comparison "
                          "is NOT CURRENTLY READABLE (2026-08-03):** the panel's cognate-ligand "
                          "self-control recovers %d of %d crystallographic poses (%s miss the %.2f Å "
                          "criterion), and this sentence is a maximum across the whole panel — see "
                          "SI §S1 and "
                          "[`antitarget-selfcontrol.json`](../modalities/antitarget-selfcontrol.json)."
                          % (sc.get("n_pass", 0), sc.get("n_targets", 0), ", ".join(blocking),
                             band or 2.0)),
        "why": "the main text asserts the same panel-wide maximum as SI §S1 paragraph 3. Conditioning "
               "only the SI would leave a reader who never opens it with the unqualified claim",
        "artifact": "research/modalities/antitarget-selfcontrol.json",
    }]


# ==================================================================================================
# SELF-TEST (offline)
# ==================================================================================================

def check():
    b = {"recovered_rmsd_A": 2.0, "partial_rmsd_A": 4.0, "null_power_max": 0.05}
    assert target_verdict(1.2, 0.0, 2.0, 4.0, 0.05) == "PASS"
    assert target_verdict(1.2, 0.4, 2.0, 4.0, 0.05) == "NO_POWER"
    assert target_verdict(3.0, 0.0, 2.0, 4.0, 0.05) == "PARTIAL"
    assert target_verdict(3.0, 0.9, 2.0, 4.0, 0.05) == "PARTIAL", "no-power must not excuse a miss"
    assert target_verdict(9.0, 0.0, 2.0, 4.0, 0.05) == "FAIL"
    assert target_verdict(None, None, 2.0, 4.0, 0.05) == "UNSCORED"

    allp = [{"name": n, "verdict": "PASS"} for n in ("RXRA", "PXR", "HSA", "VDR")]
    pv = panel_verdict(allp)
    assert pv["panel_readable"] is True
    assert all(s["readable"] for s in pv["si_s1_statements"])
    one_bad = allp[:-1] + [{"name": "VDR", "verdict": "FAIL"}]
    pv = panel_verdict(one_bad)
    assert pv["panel_readable"] is False
    assert pv["blocking_targets"] == ["VDR"]
    assert not any(s["readable"] for s in pv["si_s1_statements"]), \
        "every published clause is a panel-wide max, so one failure blocks all four"
    assert panel_verdict([])["panel_readable"] is False, "an empty panel is not a readable panel"

    assert engineered_title("MR LBD S810L in complex with X")[0] is True, \
        "a bare point-mutation token must be caught — the word list alone cannot see S810L"
    assert engineered_title("Crystal structure of the mineralocorticoid receptor LBD")[0] is False

    ranked = rank_resolve_candidates([
        {"pdb": "AAAA", "title": "MR LBD", "method": "X-RAY DIFFRACTION", "resolution_A": 2.4,
         "sequence": "MSEQ", "ligands": [{"comp_id": "LIG", "name": "x", "mw": 400, "smiles": "C"}]},
        {"pdb": "BBBB", "title": "MR LBD S810L mutant", "method": "X-RAY DIFFRACTION",
         "resolution_A": 1.9, "sequence": "MSEQ",
         "ligands": [{"comp_id": "LIG", "name": "x", "mw": 400, "smiles": "C"}]},
        {"pdb": "CCCC", "title": "MR NMR", "method": "SOLUTION NMR", "resolution_A": None,
         "sequence": "MSEQ", "ligands": [{"comp_id": "LIG", "name": "x", "mw": 400, "smiles": "C"}]},
        {"pdb": "DDDD", "title": "MR apo", "method": "X-RAY DIFFRACTION", "resolution_A": 1.5,
         "sequence": "MSEQ", "ligands": []},
    ], "P08235")
    assert ranked[0][1]["pdb"] == "AAAA", \
        "R4 must beat R5: a non-engineered 2.4 A entry outranks an S810L mutant at 1.9 A"
    assert [r["pdb"] for _s, r in ranked][-2:] == ["CCCC", "DDDD"] or \
        all(ranked[i][1]["rejected_because"] for i in (2, 3))

    lines = ["HETATM    1  C1  LIG A 501       0.000   0.000   0.000  1.00  0.00           C",
             "HETATM    2  C2  LIG A 501       1.000   0.000   0.000  1.00  0.00           C",
             "HETATM    3  C1  LIG A 601      50.000  50.000  50.000  1.00  0.00           C"]
    copy, gid = _pick_copy(lines, [0.5, 0.0, 0.0])
    assert len(copy) == 2 and gid[2].strip() == "501", "the copy nearest the box centre must be chosen"

    assert {s["id"] for s in SI_S1_STATEMENTS} == {"S1.3a", "S1.3b", "S1.3c", "S1.3d"}
    assert b["partial_rmsd_A"] > b["recovered_rmsd_A"]
    print("antitarget_selfcontrol --check: OK")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default=os.environ.get("MODE", "all"),
                    choices=["resolve", "selfcontrol", "flagged", "all", "edits"])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        return check()

    doc = {
        "_title": "Anti-target panel completion + the cognate-ligand self-control (rung R14-a)",
        "_owner": "research/manuscripts/nr4a3-program-map.md THE ORDERED PLAN -> RUNG S, and §10.1 row 10",
        "_cost": "$0 — free GitHub CPU runner. No GPU, no SageMaker, no Vast rental, nothing billed.",
        "_gate": "The cognate-ligand self-control runs FIRST. Until it passes, no anti-target margin from "
                 "this panel may be read, including the one already published in SI §S1.",
        "_limits": [
            "Docking scores are screening-grade smina affinities, not measured affinities, and no "
            "affinity, efficacy, safety, therapeutic-window or clinical claim is made or implied.",
            "A PASS here licenses reading the panel's own margins. It does NOT make the panel a "
            "proteome-wide selectivity measurement — it is 10 receptors.",
            "The receptors are protein-only by construction (antitarget_prep emits standard-amino-acid "
            "ATOM records), so any cofactor-dependent binding mode is outside what this panel can model.",
            "This module does not touch the SI or the roadmap. Required edits are ROUTED in map_edits.",
        ],
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "refusals": [],
    }
    # ⛔ A PARTIAL MODE MERGES INTO THE PRIOR ARTIFACT — IT DOES NOT REPLACE IT (2026-08-03, after it
    # already cost a table). `mode=selfcontrol` built a fresh doc and wrote it over the artifact, and the
    # `flagged` block from an earlier `mode=all` run — denovo_401 plus 18 carried candidates docked into
    # AR and MR — vanished from the record without a word. Nothing detected it: the run was green, the
    # file was newer, and the block it deleted was simply not one this mode produces.
    # This is the branch-drift failure of CLAUDE.md §7 inside a single file: a measured fact overwritten
    # by a job that never measured it. The blocks a mode DID produce are overwritten as intended; the
    # blocks it did not are carried forward, and `_carried_forward` names them so a reader can never
    # mistake a carried block for a fresh one.
    prior_doc = {}
    if os.path.exists(OUT):
        try:
            prior_doc = json.load(open(OUT))
        except (ValueError, OSError) as e:                     # noqa: BLE001
            doc["refusals"].append(_refusal("merge", "prior artifact unreadable, nothing carried: %s" % e))
    PRODUCED_BY = {"resolve": ["resolve"],
                   "selfcontrol": ["criterion", "protocol", "arms", "selfcontrol", "repair_delta",
                                   "repair_rule"],
                   "flagged": ["flagged"]}
    ran = {"all": ["resolve", "selfcontrol", "flagged"]}.get(args.mode, [args.mode])
    fresh = {k for m in ran for k in PRODUCED_BY.get(m, [])}
    carried = []
    for key, val in prior_doc.items():
        if key.startswith("_") or key in ("refusals", "map_edits_required", "map_edit_anchor_check",
                                          "si_edits_required", "si_edit_anchor_check",
                                          "manuscript_edits_required"):
            continue
        if key in fresh or key in doc:
            continue
        doc[key] = val
        carried.append(key)
    if carried:
        doc["_carried_forward"] = {
            "blocks": sorted(carried),
            "from_utc": prior_doc.get("_utc"),
            "_why": "this run's mode does not produce these blocks. They are the PREVIOUS run's "
                    "measurements, carried so a partial re-run cannot delete a measured table.",
        }

    if args.mode == "edits":
        # ⛔ RE-ROUTE WITHOUT RE-MEASURING. The routing blocks are a pure function of the measurement,
        # and the manuscripts they point at move independently of it. Re-docking 20 targets to
        # regenerate a paragraph of anchors would be re-running an experiment to fix a citation — and
        # worse, it would produce a NEW measurement while claiming to re-route the old one.
        # ⚠ It REFUSES if there is no measurement to route: a routing block computed from an absent
        # verdict would assert "the panel is readable" by the shape of an empty dict.
        if not os.path.exists(OUT):
            sys.exit("mode=edits needs an existing %s to re-route; there is none" % OUT)
        prior = json.load(open(OUT))
        if not (prior.get("selfcontrol") or {}).get("targets"):
            sys.exit("mode=edits refuses: %s carries no scored panel, so there is no verdict to route"
                     % OUT)
        doc = prior
        doc["refusals"] = [r for r in doc.get("refusals", [])
                           if not str(r.get("where", "")).startswith(("map_edits_required",
                                                                      "si_edits_required",
                                                                      "manuscript_edits_required"))]
        doc["_rerouted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if args.mode in ("resolve", "all"):
        mode_resolve(doc)
    if args.mode in ("selfcontrol", "all"):
        mode_selfcontrol(doc)
    if args.mode in ("flagged", "all"):
        mode_flagged(doc)
    # ⛔ THE ANCHOR CHECK IS PART OF THE RUN, NOT A HUMAN'S LAST STEP. The roadmap is edited concurrently;
    # a routed edit whose `current_text` has been reworded fails SILENTLY when someone tries to apply it.
    import map_edit_anchors as mea
    doc["map_edits_required"], doc["map_edit_anchor_check"] = mea.verify(map_edits(doc))
    if not doc["map_edit_anchor_check"]["all_accounted"]:
        doc["refusals"].append({
            "where": "map_edits_required",
            "why": "at least one routed edit's anchor is NOT_FOUND, AMBIGUOUS or UNREAD against the live "
                   "roadmap — see map_edit_anchor_check. Those edits must be rewritten, not applied by "
                   "judgement. (An APPLIED edit is NOT one of these: it already landed.)"})
    # ⛔ THE SI EDIT IS ROUTED SEPARATELY BECAUSE IT TARGETS A DIFFERENT FILE. `route_map_edits.py` takes
    # ONE `--target`, so mixing an SI edit into `map_edits_required` would make it report DEAD against the
    # roadmap — a real edit reading as a stale one, which is the failure that tool exists to end. The list
    # is also written standalone so the router can consume it with `--target ...paper-SI.md` directly.
    # Grouped by target FILE, because `route_map_edits.py` takes one `--target` and an edit checked
    # against the wrong file reports DEAD — a real edit reading as a stale one.
    by_file = {}
    for e in si_edits(doc):
        by_file.setdefault(e["file"], []).append(e)
    doc["manuscript_edits_required"] = {}
    for path, group in by_file.items():
        abspath = os.path.join(HERE, "..", "..", path)
        checked, summary = mea.verify(group, abspath)
        doc["manuscript_edits_required"][path] = {"edits": checked, "anchor_check": summary}
        out = os.path.join(HERE, "antitarget-selfcontrol-%s-edits.json"
                           % ("si" if "SI" in path else "paper"))
        json.dump(checked, open(out, "w"), indent=2)
        if not summary["all_accounted"]:
            doc["refusals"].append({
                "where": "manuscript_edits_required/%s" % path,
                "why": "the edit that conditions this file's anti-target claim does NOT resolve against "
                       "it — see anchor_check. The panel is unreadable and the file still asserts the "
                       "margin, so this edit must be relocated by hand rather than dropped."})
    # kept for readers that already parse the SI-only field
    si_block = doc["manuscript_edits_required"].get("research/manuscripts/nr4a3-degrader-paper-SI.md")
    doc["si_edits_required"] = (si_block or {}).get("edits", [])
    doc["si_edit_anchor_check"] = (si_block or {}).get("anchor_check")
    json.dump(doc, open(OUT, "w"), indent=2)
    open(OUT_MD, "w").write(render_markdown(doc))
    print("wrote", OUT)
    sc = doc.get("selfcontrol") or {}
    if sc:
        print("PANEL READABLE:", sc.get("panel_readable"), "blocking:", sc.get("blocking_targets"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
