#!/usr/bin/env python3
"""WHICH CAVITY DID EACH METHOD ACTUALLY PICK? — the attribution `R5` needs and neither existing
artifact carries.

★★ WHY THIS EXISTS. Two landed results describe the same site from opposite ends and neither can see
the other's question:

  · [`pose-convergence-401.json`](pose-convergence-401.json) measures how far apart six `denovo_401`
    poses are (pocket-superposed median **7.006 Å** on a molecule whose end-for-end flip costs 6.84 Å)
    and records `cross_method_evidence: NONE`.
  · [`pose-second-method.json`](pose-second-method.json) adds the second, scoring-independent engine
    (rDock) and reports the two methods disagree, with the disagreement carried by ORIENTATION rather
    than by location — small centroid separations under large RMSDs.
  · [`r3-site-choice-audit.json`](r3-site-choice-audit.json) then found the thing that makes
    "orientation, not location" ambiguous: the prespecified site is **SPLIT ACROSS TWO REAL CAVITIES**
    — 4 shared residues, pairwise Jaccard 0.21, centroids 9.853 Å apart, further than the frozen gate's
    own 8.0 Å ceiling. Pocket 1 is the helix-3 face; pocket 2 is the helix-11/12 face.

⛔ AND THE SEARCH VOLUME CONTAINS BOTH. `pose_second_method.part_a` centres rDock's cavity mapper on the
Pocket-5 Cα centroid at a radius DERIVED from the pipeline's own docking box (12.0 Å half-edge), and the
pipeline's smina box is that same box. The R3 audit measures pocket 1's centroid 3.478 Å from that
reference centroid and pocket 2's 7.562 Å — **both inside the sphere.** So neither engine was ever asked
to choose one sub-cavity; both were free to answer with either, and a centroid separation of ~2 Å
between two poses says nothing about whether they are in the same sub-pocket, because the two sub-pockets'
own centroids are only 9.853 Å apart and their occupied volumes interpenetrate.

⇒ THE ONE QUESTION THIS MODULE ANSWERS: **for each receptor, does the second method's pose contact the
SAME sub-cavity the first method's pose does?** It is the difference between

    "two engines disagree about which way round the molecule sits in one pocket"        (weaker finding)
    "two engines disagree about which of two pockets the molecule is in"                (stronger finding)

and no committed artifact separates them.

★ HOW, AND WHY IT IS NOT A NEW CRITERION.
  · The contact cutoff is `pose_convergence_401.contact_a()` — which itself reads the default off
    `nr4a3_warhead.handle_contacts`, the pipeline's own. Nothing is defined here.
  · The contact kernel is `pose_convergence_401.contacts`, the same function that produced the census's
    `contact_a`/`contact_b` sets, so these numbers are commensurable with that artifact's.
  · The two cavities' lining sets are READ from `r3-site-choice-audit.json` →
    `question_A_which_cavity_is_the_site.accepted_cavities[].lining_uniprot_labels`. They are not typed
    here and not re-derived; if that audit is re-run, this follows it.
  · ⛔ The call is made on **DISCRIMINATING** contacts only — residues that line exactly one of the two
    cavities. The 4 residues shared by both (and every residue lining neither) carry no information
    about which cavity a pose is in, and counting them would let the overlap decide the answer.
  · ⛔ A pose whose discriminating contacts tie, or that has none, is `AMBIGUOUS` and is reported as
    such. It is never broken by a tiebreak, because a tiebreak here would be inventing the answer.

⛔ WHAT THIS DOES NOT LICENSE. Nothing about binding, affinity, reactivity or correctness. Both engines
can be in the same cavity and both wrong; both can be in different cavities and both wrong. A cavity
call is a statement about where a predicted geometry sits, and `R4` — that anything binds either cavity
— is untouched and still needs a bench.

Output: r5-cross-method-cavity-attribution.json. Free CPU, no GPU, no rental, $0.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "r5-cross-method-cavity-attribution.json")
AUDIT = os.path.join(HERE, "r3-site-choice-audit.json")
SECOND = os.path.join(HERE, "pose-second-method.json")


def cavity_definitions():
    """The two accepted cavities, READ from the R3 audit. One home, per CLAUDE.md rule 1."""
    with open(AUDIT) as fh:
        a = json.load(fh)
    q = a["question_A_which_cavity_is_the_site"]
    out = []
    for c in q["accepted_cavities"]:
        out.append({
            "pocket": c["pocket"],
            "lining_labels": list(c["lining_uniprot_labels"]),
            "lining_resseq": sorted(int("".join(ch for ch in lab if ch.isdigit()))
                                    for lab in c["lining_uniprot_labels"]),
            "druggability": c.get("druggability"),
            "centroid_dist_to_reference_ang": c.get("centroid_dist_ang"),
            "gate_a_verdict_if_this_were_the_site": c.get("gate_a_verdict_if_this_were_the_site"),
        })
    pair = (q.get("contrast") or {}).get("pairs") or [{}]
    return {
        "_read_from": "r3-site-choice-audit.json → question_A_which_cavity_is_the_site",
        "chosen_by_the_frozen_rule": q.get("chosen_by_the_frozen_rule"),
        "reference_lining_labels": q.get("reference_lining_labels"),
        "cavities": out,
        "separation": {
            "pairwise_jaccard": pair[0].get("pairwise_jaccard"),
            "centroid_separation_ang": pair[0].get("centroid_separation_ang"),
            "n_shared_residues": pair[0].get("n_shared"),
            "relationship": pair[0].get("relationship"),
        },
        "_faces": {"1": "the helix-3 face", "2": "the helix-11/12 face"},
    }


def discriminating_sets(cavities):
    """Residues that line exactly ONE cavity. ⛔ Shared residues are dropped — they cannot discriminate,
    and including them would let the overlap between the two cavities decide the call."""
    a = set(cavities[0]["lining_resseq"])
    b = set(cavities[1]["lining_resseq"])
    return {cavities[0]["pocket"]: sorted(a - b), cavities[1]["pocket"]: sorted(b - a),
            "_shared_dropped": sorted(a & b)}


def call_cavity(contact_set, disc):
    """Which cavity does this pose touch? A tie or an empty intersection is AMBIGUOUS, never broken."""
    counts = {p: len(contact_set & set(res)) for p, res in disc.items() if p != "_shared_dropped"}
    best = sorted(counts.items(), key=lambda kv: -kv[1])
    if not best or best[0][1] == 0:
        return {"cavity": "AMBIGUOUS", "_why": "no discriminating contact in either cavity",
                "counts": counts}
    if len(best) > 1 and best[0][1] == best[1][1]:
        return {"cavity": "AMBIGUOUS", "_why": "equal discriminating contact counts — not broken by a "
                                               "tiebreak, because a tiebreak would invent the answer",
                "counts": counts}
    return {"cavity": best[0][0], "counts": counts,
            "margin": best[0][1] - (best[1][1] if len(best) > 1 else 0)}


def measure():
    import pose_convergence_401 as pc
    import pose_second_method as psm

    cavdef = cavity_definitions()
    disc = discriminating_sets(cavdef["cavities"])
    cutoff = pc.contact_a()

    with open(SECOND) as fh:
        second = json.load(fh)
    part_a = second.get("part_a") or {}
    by_id = {r["id"]: r for r in (part_a.get("systems") or [])}

    doc = {
        "_module": "r5_cavity_attribution",
        "_question": "For each receptor, do the two independent pose methods contact the SAME sub-cavity "
                     "of R3's split site — or different ones?",
        "_why_it_matters": "`pose-second-method.json` reads the cross-method disagreement as ORIENTATION "
                           "rather than LOCATION, from small centroid separations. That reading assumes "
                           "one pocket. R3 measured two, 9.853 Å apart, and BOTH lie inside the 12.0 Å "
                           "search sphere both engines were given — so the assumption has to be checked, "
                           "not inherited.",
        "_does_not_license": [
            "that either pose is correct — no experimental structure of this complex exists",
            "that anything binds either cavity — `R4` still needs a bench",
            "that one cavity is the site — that is `C2`'s frozen rule and this module never touches it",
            "reading a contact count as an affinity, a score or a preference",
        ],
        "_contact_cutoff_A": cutoff,
        "_contact_cutoff_source": "pose_convergence_401.contact_a() → nr4a3_warhead.handle_contacts "
                                  "default — the pipeline's own, defined nowhere here",
        "_second_method_source": {
            "artifact": os.path.relpath(SECOND, REPO),
            "provenance": second.get("_provenance"),
            "tooling": second.get("tooling"),
            "n_systems": len((part_a.get("systems") or [])),
        },
        "cavity_definitions": cavdef,
        "discriminating_residues": disc,
        "systems": [],
        "refusals": [],
    }

    for src in pc.SOURCES:
        rec, ref = pc.load_source(src)
        if rec is None:
            doc["refusals"].append(ref)
            continue
        row = {"id": rec["id"], "receptor_provenance": rec.get("receptor_provenance"),
               "receptor": rec["receptor"]}
        residues = rec["residues"]
        first_xyz = pc.heavy_coords(rec["mol"])
        c_first = pc.contacts(first_xyz, residues, cutoff)
        row["first_method"] = {
            "engine": "smina (top pose)", "contacts": sorted(c_first),
            **call_cavity(c_first, disc)}

        srow = by_id.get(rec["id"]) or {}
        sd = srow.get("best_pose_sd")
        if not sd:
            row["second_method"] = {
                "engine": "rDock", "cavity": "UNREAD",
                "_why": "no committed rDock pose for this system in %s — %s"
                        % (os.path.relpath(SECOND, REPO), srow.get("why") or "system absent"),
            }
            doc["systems"].append(row)
            continue
        mol = psm.best_from_sd(os.path.join(REPO, sd))
        if mol is None:
            row["second_method"] = {"engine": "rDock", "cavity": "UNREAD",
                                    "_why": "no scorable pose in %s" % sd}
            doc["systems"].append(row)
            continue
        c_second = pc.contacts(pc.heavy_coords(mol), residues, cutoff)
        row["second_method"] = {
            "engine": "rDock", "pose_file": sd, "contacts": sorted(c_second),
            **call_cavity(c_second, disc)}
        row["contact_jaccard_between_methods"] = pc.jaccard(c_first, c_second)
        row["cross_method_rmsd_A"] = srow.get("cross_method_rmsd_A")
        row["cross_method_band"] = srow.get("cross_method_band")
        row["cross_method_centroid_distance_A"] = srow.get("cross_method_centroid_distance_A")
        a, b = row["first_method"]["cavity"], row["second_method"]["cavity"]
        row["same_cavity"] = (None if "AMBIGUOUS" in (a, b) or "UNREAD" in (a, b) else a == b)
        doc["systems"].append(row)

    doc["rollup"] = _rollup(doc["systems"], cavdef)
    doc["map_edits_required"] = build_map_edits(doc, second)
    doc["_status"] = "ok"
    return doc


def build_map_edits(doc, second):
    """The roadmap edits this result requires — DESCRIBED, NEVER APPLIED.

    Same anchor discipline as `paralogue_pocket_contrast.build_map_edits`: every `current_text` is read
    out of the LIVE map, so an entry that cannot be targeted says so rather than being silently wrong.
    ⛔ Nothing here edits the roadmap. `nr4a3-program-map.md` is trimcrae's, and a session that rewrites
    the plan to match its own result is the outcome-selection defect this repo keeps guarding against."""
    import map_edits as ME
    text = ME.load_map()
    roll = doc.get("rollup") or {}
    cm = ((second.get("part_a") or {}).get("cross_method_same_frame") or {})
    med = (cm.get("rmsd_A") or {}).get("median")
    n_sys = cm.get("n_systems")
    bands = cm.get("bands") or {}
    art = "research/modalities/r5-cross-method-cavity-attribution.json → rollup"

    gradeable = roll.get("n_gradeable") or 0
    same = roll.get("n_same_cavity") or 0
    diff = roll.get("n_different_cavity") or 0
    calls = roll.get("first_method_cavity_calls") or {}
    frozen = roll.get("cavity_chosen_by_the_frozen_rule")
    cavity_line = (
        "⭑ **AND THE CAVITY THE TWO METHODS CHOSE IS NOW MEASURED, WHICH THE ORIENTATION READING "
        "ASSUMED (2026-08-06, $0).** R3 measured this site SPLIT across two real cavities 9.853 Å apart, "
        "and BOTH lie inside the 12.0 Å sphere both engines search — so a small centroid separation "
        "could not by itself establish a shared location. Measured on discriminating lining contacts "
        "(shared residues dropped): **%d of %d gradeable system(s) same cavity, %d different**, and the "
        "FIRST method's own calls across the census are %s against a frozen-rule site of pocket %s "
        "— [`r5-cross-method-cavity-attribution.json`](../modalities/r5-cross-method-cavity-attribution.json). "
        "⛔ A cavity call is a geometry statement: it makes no pose correct and nothing binds either "
        "cavity." % (same, gradeable, diff, json.dumps(calls, sort_keys=True), frozen))

    prov_line = (
        "⚠ **THE ARTIFACT THIS ROW POINTS AT WAS EMPTY WHEN THIS WAS WRITTEN, AND THE ROW'S NUMBERS HAD "
        "NO HOME (measured 2026-08-06).** `pose-second-method.json` on `main` carried "
        "`outcome: UNRUN`, zero systems and no `verdict.what_would_resolve_R5` — the field this row "
        "links to. Root cause: the workflow installed an UNPINNED `rdock`, bioconda satisfied it with "
        "`2013.1`, whose protocol files live at `share/rdock-2013.1-1/` and not the `share/rDock/` the "
        "module probes, so `RBT_ROOT` resolved to `None` and PART A returned UNRUN — and an UNRUN half "
        "was written over a measured one. ✅ Both closed: the version is pinned in "
        "`pose-recovery-check.yml`, `pose_second_method._carry_forward` now refuses to let an unrun half "
        "overwrite a measured one, and the run was reproduced from the committed inputs "
        "(**pose-for-pose coordinate-identical** to the 2026-08-03 poses under "
        "`_pose_second_method_poses/`), so the numbers in this row are re-derived rather than recalled.")

    entries = [
        ME.edit(text, "§5 row R5", "| **R5** | **The binding pose is right.** Node `PS`",
                "The row already records that the two methods DISAGREE. What it could not say is WHICH "
                "cavity each was in — and R3 had measured the site split across two, both inside the "
                "search sphere, which is what makes 'orientation, not location' an assumption rather "
                "than a reading.",
                art, ME.append_after_line(cavity_line)),
        ME.edit(text, "§10.1 row 4",
                "| **4** | **Re-run the pose known-answer test with SITE and DOCKING separated**",
                "Same finding, on the row that owns the ordering. It does not change the row's rank — "
                "`R5` is still the biggest unblocker — but it changes what a reader of this row learns "
                "about the disagreement.",
                art, ME.append_after_line(cavity_line)),
        ME.edit(text, "§3.1 row V22", "| **V22** | **The scoring-independent second pose method**",
                "⛔ PROVENANCE, NOT A NEW RESULT. This row's numbers (median %s Å over %s systems, "
                "bands %s) were quotable from prose only — the artifact they name did not carry them. "
                "That is precisely the failure CLAUDE.md §7 records as branch drift, arriving through a "
                "different door." % (med, n_sys, json.dumps(bands, sort_keys=True)),
                "research/modalities/pose-second-method.json → part_a.cross_method_same_frame",
                ME.append_after_line(prov_line)),
    ]
    return {
        "_reads": "⛔ DESCRIBED, NEVER APPLIED. Every `current_text` was read from the live map at run "
                  "time; an entry whose `status` is not `OK` could not be targeted and must be applied "
                  "by hand at the named section.",
        "_map": "research/manuscripts/nr4a3-program-map.md",
        "entries": entries,
        "verify": ME.verify(entries, text) if hasattr(ME, "verify") else None,
    }


def _rollup(rows, cavdef):
    gradeable = [r for r in rows if r.get("same_cavity") is not None]
    agree = [r for r in gradeable if r["same_cavity"]]
    disagree = [r for r in gradeable if not r["same_cavity"]]
    first_calls, second_calls = {}, {}
    for r in rows:
        first_calls[str(r.get("first_method", {}).get("cavity"))] = \
            first_calls.get(str(r.get("first_method", {}).get("cavity")), 0) + 1
        second_calls[str(r.get("second_method", {}).get("cavity"))] = \
            second_calls.get(str(r.get("second_method", {}).get("cavity")), 0) + 1
    frozen = (cavdef.get("chosen_by_the_frozen_rule") or {}).get("pocket")
    out = {
        "n_systems": len(rows),
        "n_gradeable": len(gradeable),
        "n_same_cavity": len(agree),
        "n_different_cavity": len(disagree),
        "first_method_cavity_calls": first_calls,
        "second_method_cavity_calls": second_calls,
        "cavity_chosen_by_the_frozen_rule": frozen,
        "_ungradeable_is_not_agreement": "a system whose call is AMBIGUOUS or UNREAD is excluded from "
                                         "the denominator, never scored as agreement",
    }
    if not gradeable:
        out["_reads"] = ("NOT GRADEABLE — no system produced a discriminating call from both methods. "
                         "That is a statement about the cavities' overlap, not about the poses.")
        return out
    if disagree and not agree:
        out["_reads"] = (
            "⛔ DIFFERENT CAVITIES ON %d OF %d GRADEABLE SYSTEM(S). The cross-method disagreement is "
            "NOT only about which way round the molecule sits — the two engines are not in the same "
            "sub-pocket of the split site. `pose-second-method.json`'s ORIENTATION reading is measured "
            "in a frame where a ~2 Å centroid shift can move a ligand between two cavities whose own "
            "centroids are 9.853 Å apart, so a small centroid separation does not establish a shared "
            "location here." % (len(disagree), len(gradeable)))
    elif agree and not disagree:
        out["_reads"] = (
            "The two engines are in the SAME sub-cavity on %d of %d gradeable system(s). The "
            "cross-method disagreement recorded in `pose-second-method.json` is therefore about "
            "ORIENTATION WITHIN one cavity, not about which cavity — which is what that artifact's "
            "centroid reading assumed, now checked rather than inherited. ⛔ It does not make either "
            "pose correct." % (len(agree), len(gradeable)))
    else:
        out["_reads"] = (
            "MIXED — same cavity on %d of %d gradeable system(s), different on %d. A per-receptor "
            "split means the cavity call is itself receptor-conformer dependent, so neither the "
            "orientation reading nor a location reading holds across the census."
            % (len(agree), len(gradeable), len(disagree)))
    return out


def main():
    doc = measure()
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1, default=str)
    print(json.dumps({"_status": doc["_status"], "rollup": doc["rollup"]}, indent=1))
    return doc


if __name__ == "__main__":
    main()
