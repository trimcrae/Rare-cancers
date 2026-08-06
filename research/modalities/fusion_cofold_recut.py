#!/usr/bin/env python3
"""
`R13-b` PRE-LAUNCH: re-cut the two `fusion_cofold.py` constructs to the CORRECTED junction, from COMMITTED
sequence only, and REFUSE unless every cut reproduces a committed artifact byte-for-byte.

⛔ THIS DISPATCHES NOTHING AND RENTS NOTHING. $0, pure stdlib, no network. It is the missing $0 precheck for
rung `R13-b` — the paid sibling `R14-b` has one and `R13-b` had none, so the only thing standing between a
mis-cut construct and 12 billed Boltz models was a runtime AFDB fetch on the rented host.

WHY A RE-CUT IS OWED (finding X9, systems/AUDIT-2026-08-06-routes.md, SETTLED 2026-08-06 at $0):
  NR4A3 transcript exons 1 and 2 are entirely NON-CODING, so "NR4A3 exon 3" IS residue 1. The chimera
  therefore RETAINS NR4A3's AF-1, DBD, hinge and LBD; the "AF1 -> EWSR1-LC swap" premise the repo carried is
  false, and EWSR1-LC is ADDITIVE. `fusion_cofold.py` resumes NR4A3 at residue **2**, which drops M1 — one
  residue, but it is the residue the whole correction is about, and the cut must state 1.

WHY THE CUT IS NOT FULLY DETERMINED, AND WHY THIS MODULE BUILDS TWO OBJECTS INSTEAD OF CHOOSING (OC-2,
systems/graph/integrity.json, OPEN, owner = the roadmap's `R13`):
  "the canonical EMC fusion" names two incompatible objects and this module's parent is built on the one that
  is NOT a reported fusion type.
    * `OBJ-MODEL-E7E3`  EWSR1(1-264)::NR4A3(1-626)                      status `modelled_not_reported`
    * `OBJ-FUS-T1`      EWSR1(1-431) :: 1 junction residue :: NR4A3(1-626)   status `reported`, commonest
  Both are built here, both verified, and NEITHER is a default: `--object` is REQUIRED at build time, because
  a co-fold's whole question is about the seam and the two objects have DIFFERENT seams. Choosing between
  them is the science decision OC-2 registers as not-a-navigation-layer call, and `R13-b` needs a nod anyway.

WHAT IS *NOT* RE-CUT, and why that is a reading rather than an omission: `EWS_SEAM_LEN` (120), the AF-1 end
(260) and the folded-core start (261) are unchanged. The last two are READ from
`fusion-object-inventory.json` -> `domains` rather than typed, and they already agree with `fusion_cofold.py`.
So the priced sizes hold: seam ~380, composite ~486 residues (scope-rung-cost.json
`bases.cofold_per_model._why_this_is_an_UPPER_bound_twice_over`).

SCOPE. Sequence only. No structure, pose, affinity, selectivity, efficacy, safety, therapeutic-window or
clinical claim is made or implied anywhere in this module or its artifact.

Reads (all committed, all in-repo, no network):
  research/modalities/nr4a-sequences-cache.json        UniProt full-length NR4A3 / EWSR1
  research/modalities/emc-fet-construct-designs.json   the reported junctions + their FULL chimera sequences
  research/modalities/fusion-object-inventory.json     domain boundaries + the R13-a gate string
  systems/graph/objects.json                           OBJ-FUS-T1 / OBJ-MODEL-E7E3 residue-level definitions

Writes:
  research/modalities/fusion-cofold-constructs.json
  research/modalities/fusion_cofold_inputs/<object>/{seam,composite}.yaml   (Boltz-2 apo, one chain)
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

SEQ_CACHE = os.path.join(HERE, "nr4a-sequences-cache.json")
DESIGNS = os.path.join(HERE, "emc-fet-construct-designs.json")
INVENTORY = os.path.join(HERE, "fusion-object-inventory.json")
OBJECTS = os.path.join(REPO, "systems", "graph", "objects.json")

RUNG_COST = os.path.join(HERE, "scope-rung-cost.json")
COMPUTE = os.path.join(REPO, "research", "compute")
VAST_LAUNCH = os.path.join(HERE, "nrv04_vast_launch.py")

OUT_JSON = os.path.join(HERE, "fusion-cofold-constructs.json")
OUT_DIR = os.path.join(HERE, "fusion_cofold_inputs")

# The seam-proximal window of the 5' partner. UNCHANGED from fusion_cofold.EWS_SEAM_LEN — the distal LC
# cannot reach a junction fold and only inflates the ~N^2 Boltz cost. Re-typed here rather than imported
# because fusion_cofold.py imports nr4a3_structure, which reaches the network at import time in some paths.
EWS_SEAM_LEN = 120

# The priced ensemble: 12 models = 2 constructs x 6 seeds (scope-rung-cost.json rung R13-b `units`).
SEEDS = [1, 2, 3, 4, 5, 6]

# The two objects R13-b could mean. `designs_id` names the committed construct whose full chimera sequence
# this object's halves must reproduce; None means the object is not a reported type and its halves are
# cross-checked against a reported neighbour instead (named in `verified_against`).
OBJECT_SPECS = {
    "t1_reported_canonical": {
        "graph_object": "OBJ-FUS-T1",
        "designs_id": "EWSR1_NR4A3_type1",
        "what": "reported EWSR1::NR4A3 type 1 (EWSR1 exon 12 :: NR4A3 exon 3) — the commonest reported "
                "transcript type, and the object the 2026-08-03 correction assigns the name 'canonical'",
        "status": "reported",
    },
    "e7e3_plan_literal": {
        "graph_object": "OBJ-MODEL-E7E3",
        "designs_id": None,
        "verified_against": ["EWSR1_NR4A3_type2"],  # shares the EWSR1(1-264) cut and the NR4A3(1-626) half
        "what": "the modelled EWSR1 e7 :: NR4A3 e3 construct — the junction string the R13-a gate reproduced "
                "and the one `fusion_cofold.py` already models, but NOT a reported fusion type: it pairs "
                "type 2's 5' cut with type 1's 3' exon and omits type 2's 59 UTR-encoded residues",
        "status": "modelled_not_reported",
    },
}


# --------------------------------------------------------------------------------------------- loading
def _load(path):
    with open(path) as fh:
        return json.load(fh)


def load_inputs():
    return {
        "sequences": _load(SEQ_CACHE),
        "designs": _load(DESIGNS),
        "inventory": _load(INVENTORY),
        "objects": {o["id"]: o for o in _load(OBJECTS)},
    }


def designs_by_id(designs):
    return {c["id"]: c for c in designs["constructs"]}


def nr4a3_domains(inventory):
    """AF-1 / DBD / hinge / LBD boundaries READ from the R13-a inventory, never typed here."""
    d = inventory["domains"]
    return {
        "af1": tuple(d["AF1/N-terminal (disordered)"]),
        "dbd": tuple(d["DNA-binding domain (zinc fingers)"]),
        "hinge": tuple(d["hinge"]),
        "lbd": tuple(d["ligand-binding domain"]),
    }


# --------------------------------------------------------------------------------------------- cutting
def five_prime_half(designs_entry, ewsr1):
    """(sequence of the retained 5' half, n_residues_fully_encoded, junction-encoded residues).

    The junction residues are DERIVED, never typed: they are whatever the committed chimera carries between
    the 5' partner's last fully-encoded residue and the start of the 3' partner.
    """
    n5 = designs_entry["junction_in_residue_numbering"]["five_prime_residues_fully_encoded"]
    n_extra = designs_entry["domains_retained_and_lost"]["n_extra_junction_encoded_residues"]
    chimera = designs_entry["protein_sequence"]
    junction = chimera[n5:n5 + n_extra] if n_extra else ""
    return ewsr1[:n5], n5, junction


def build_object(key, inp):
    """Cut `seam` and `composite` for one object. Returns the record; raises on any inconsistency."""
    spec = OBJECT_SPECS[key]
    seqs, designs = inp["sequences"], designs_by_id(inp["designs"])
    dom = nr4a3_domains(inp["inventory"])
    nr4a3, ewsr1 = seqs["NR4A3"], seqs["EWSR1"]

    if spec["designs_id"]:
        entry = designs[spec["designs_id"]]
        five, n5, junction = five_prime_half(entry, ewsr1)
        full_chimera = entry["protein_sequence"]
    else:
        # OBJ-MODEL-E7E3 is not a reported type, so no committed chimera exists for it. Its residue-level
        # definition is read from the graph and its two halves are verified against a reported neighbour.
        resid = inp["objects"][spec["graph_object"]]["definition"]["residue_level"]
        if resid != "EWSR1(1–264) :: NR4A3(1–626), with no UTR-encoded segment":
            raise SystemExit("REFUSE: %s residue_level moved: %r" % (spec["graph_object"], resid))
        n5, junction = 264, ""
        five = ewsr1[:n5]
        full_chimera = five + junction + nr4a3

    af1_end = dom["af1"][1]        # 260 — read, not typed
    core_start = dom["dbd"][0]     # 261 — read, not typed
    nr4a3_end = len(nr4a3)

    ews_seam = five[-EWS_SEAM_LEN:]
    nr4a3_af1 = nr4a3[0:af1_end]                      # residues 1..260 — RESIDUE 1, the X9 correction
    nr4a3_core = nr4a3[core_start - 1:nr4a3_end]      # residues 261..626

    constructs = {
        "seam": {
            "chain": ews_seam + junction + nr4a3_af1,
            "five_prime_range": [n5 - EWS_SEAM_LEN + 1, n5],
            "five_prime_len": len(ews_seam),
            "junction_encoded_residues": junction,
            "nr4a3_range": [1, af1_end],
            "nr4a3_len": len(nr4a3_af1),
            "block_boundary": len(ews_seam) + len(junction),
            "hypothesis": "true junction geometry (EWS-LC :: NR4A3 AF-1, which the fusion RETAINS) — does "
                          "anything order AT the fused seam?",
        },
        "composite": {
            "chain": ews_seam + junction + nr4a3_core,
            "five_prime_range": [n5 - EWS_SEAM_LEN + 1, n5],
            "five_prime_len": len(ews_seam),
            "junction_encoded_residues": junction,
            "nr4a3_range": [core_start, nr4a3_end],
            "nr4a3_len": len(nr4a3_core),
            "block_boundary": len(ews_seam) + len(junction),
            "hypothesis": "generous upper bound — the disordered AF-1 spacer is DELIBERATELY removed so the "
                          "EWS tail gets the best possible chance to pack onto the NR4A3 folded core",
        },
    }
    for c in constructs.values():
        c["total_len"] = len(c["chain"])
        c["sha256"] = hashlib.sha256(c["chain"].encode()).hexdigest()[:16]

    return {
        "graph_object": spec["graph_object"],
        "object_status": spec["status"],
        "what": spec["what"],
        "junction": " :: ".join(
            ["EWSR1(1-%d)" % n5] + ([junction] if junction else []) + ["NR4A3(1-%d)" % nr4a3_end]),
        "five_prime_residues_fully_encoded": n5,
        "junction_encoded_residues": junction,
        "full_chimera_len": len(full_chimera),
        "full_chimera_sha256": hashlib.sha256(full_chimera.encode()).hexdigest()[:16],
        "verified_against": spec.get("verified_against") or ([spec["designs_id"]] if spec["designs_id"] else []),
        "constructs": constructs,
        "_full_chimera": full_chimera,   # stripped before write; used only by the checks
    }


# ----------------------------------------------------------------------------------------------- gate
def run_checks(inp, built):
    """Every check that must pass before a cent is spent. Returns (checks, ok)."""
    seqs, designs = inp["sequences"], designs_by_id(inp["designs"])
    inv, dom = inp["inventory"], nr4a3_domains(inp["inventory"])
    nr4a3, ewsr1 = seqs["NR4A3"], seqs["EWSR1"]
    checks = []

    def chk(name, got, want, note=""):
        checks.append({"check": name, "got": got, "want": want, "ok": got == want, "note": note})

    # -- the sequences themselves
    xc = inv["sequence_cross_check"]
    chk("NR4A3 UniProt cache is the canonical 626 aa", len(nr4a3), 626)
    chk("EWSR1 UniProt cache is the canonical 656 aa", len(ewsr1), 656)
    chk("NR4A3 UniProt cache == Ensembl translation (R13-a cross-check)", xc["NR4A3"]["identical"], True)
    chk("EWSR1 UniProt cache == Ensembl translation (R13-a cross-check)", xc["EWSR1"]["identical"], True)

    # -- the residue the whole correction is about, and the residues the program's claims turn on
    chk("NR4A3 residue 1 is the initiator methionine", nr4a3[0], "M",
        "X9: NR4A3 exon 3 begins at residue 1, so the fusion retains it")
    chk("NR4A3 C166 is a cysteine (the NR4A3-unique one outside every structure here)", nr4a3[165], "C")
    chk("NR4A3 C397 is a cysteine (inside the modelled LBD construct)", nr4a3[396], "C")

    # -- domain boundaries are READ, and they agree with what the parent module hard-codes
    chk("AF-1 ends at 260, read from the R13-a inventory", dom["af1"][1], 260)
    chk("the folded core (DBD) starts at 261, read from the R13-a inventory", dom["dbd"][0], 261)
    chk("LBD is 373-626, read from the R13-a inventory", list(dom["lbd"]), [373, 626])

    # -- the decisive one: every reported chimera must be reproducible from the two cached parents
    for cid, entry in sorted(designs.items()):
        if not entry.get("protein_sequence") or not entry["id"].startswith("EWSR1_NR4A3"):
            continue
        n5 = entry["junction_in_residue_numbering"]["five_prime_residues_fully_encoded"]
        n_extra = entry["domains_retained_and_lost"]["n_extra_junction_encoded_residues"]
        chimera = entry["protein_sequence"]
        chk("%s: 5' half == EWSR1(1-%d) from the UniProt cache" % (cid, n5), chimera[:n5], ewsr1[:n5])
        chk("%s: 3' half == NR4A3(1-626) from the UniProt cache" % cid, chimera[n5 + n_extra:], nr4a3)
        chk("%s: length == 5' + junction + 3'" % cid, len(chimera), n5 + n_extra + len(nr4a3))
        chk("%s: retains AF-1 (the X9 finding, read from the artifact)" % cid,
            entry["domains_retained_and_lost"]["three_prime_NR4A3_half"]["retains_AF1"], True)
        chk("%s: NR4A3 first residue retained == 1" % cid,
            entry["domains_retained_and_lost"]["three_prime_NR4A3_half"]["nr4a3_first_residue_retained"], 1)
        chk("%s: the reported junction is in frame" % cid, entry["self_checks"]["in_frame"], True)

    # -- the R13-a gate string still says what the plan says it says
    chk("R13-a gate reproduced its junction", inv["gate"]["status"], "REPRODUCED")
    chk("R13-a gate junction string", inv["gate"]["junction"], "EWSR1(1-264)::NR4A3(1-626)")

    # -- and the cuts we are about to spend money on
    for key, rec in sorted(built.items()):
        full = rec["_full_chimera"]
        for name, c in sorted(rec["constructs"].items()):
            chk("%s/%s: the built chain is a contiguous slice of the full chimera" % (key, name),
                c["chain"] in full if name == "seam" else True, True,
                "composite is deliberately discontiguous — the AF-1 spacer is removed by design")
            chk("%s/%s: chain length == 5' window + junction + NR4A3 block" % (key, name),
                c["total_len"], c["five_prime_len"] + len(c["junction_encoded_residues"]) + c["nr4a3_len"])
            chk("%s/%s: no non-standard residue letter" % (key, name),
                set(c["chain"]) <= set("ACDEFGHIKLMNPQRSTVWY"), True)
        seam = rec["constructs"]["seam"]
        chk("%s/seam: begins the NR4A3 block at residue 1 (M) — AF-1 RETAINED" % key,
            seam["chain"][seam["block_boundary"]], "M")
        chk("%s/seam: priced size band (~380 residues)" % key, 375 <= seam["total_len"] <= 390, True,
            "scope-rung-cost.json bases.cofold_per_model — SIZE upper-bound argument")
        comp = rec["constructs"]["composite"]
        chk("%s/composite: priced size band (~486 residues)" % key, 480 <= comp["total_len"] <= 495, True)
        chk("%s/composite: NR4A3 block starts at the DBD" % key, comp["nr4a3_range"][0], dom["dbd"][0])

    # -- the modelled object's halves, checked against a REPORTED neighbour rather than against itself
    t2 = designs["EWSR1_NR4A3_type2"]
    chk("OBJ-MODEL-E7E3's 5' cut is type 2's, verified against type 2's committed chimera",
        t2["junction_in_residue_numbering"]["five_prime_residues_fully_encoded"], 264)
    chk("OBJ-MODEL-E7E3 omits type 2's 59 UTR-encoded residues (so it is NOT type 2)",
        t2["domains_retained_and_lost"]["n_extra_junction_encoded_residues"], 59)

    return checks, all(c["ok"] for c in checks)


# ----------------------------------------------------------------------------------------------- boltz
def boltz_yaml_apo(chains):
    """Minimal Boltz-2 YAML for an apo (ligand-free) prediction. Same shape as fusion_cofold.boltz_yaml_apo;
    the seed is passed to the CLI at run time, not written into the YAML."""
    lines = ["version: 1", "sequences:"]
    for cid, seq in chains:
        lines += ["  - protein:", "      id: %s" % cid, "      sequence: %s" % seq]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------- the DOLLAR ceiling (this rung has no $/ns)
def dollar_ceiling():
    """R13-b's buy ceiling, DERIVED from scope-rung-cost.json — never typed.

    ⛔ There is no `$/ns` row here and its absence is a REFUSAL, not a missing field: a co-fold integrates no
    dynamics, so there is no nanosecond denominator. The rate line (CLAUDE.md §1) therefore cannot bind on
    this rung at all, and the ONLY ceiling is the rung's authorised dollar band. A refusal must say so.
    """
    r = _load(RUNG_COST)["rungs"]["R13-b · apo co-fold of the two corrected fusion constructs"]
    lo, hi = r["range_usd"]
    return {
        "plan_usd": r["plan_usd"],
        "band_usd": [lo, hi],
        "units": r["units"],
        "unit": r["unit"],
        "ceiling_usd_total": hi,
        "ceiling_usd_per_model": round(hi / r["units"], 6),
        "plan_usd_per_model": round(r["plan_usd"] / r["units"], 6),
        "usd_per_ns": r["usd_per_ns"],
        "_why_no_usd_per_ns": r["_why_no_usd_per_ns"],
        "which_ceiling_binds": "DOLLAR — the rate line has no denominator on this rung and does not apply. "
                               "A refusal here must name the dollar ceiling and must not be reported as "
                               "$/ns drift.",
        "_source": "research/modalities/scope-rung-cost.json -> rungs -> R13-b (range_usd, units)",
    }


# ----------------------------------------------------- can this be launched the way the plan says it can?
def launch_path_check():
    """$0, read-only: does the launch path the rung's own cell asserts actually EXIST in this repo?

    CLAUDE.md §6: never build an environment on a machine we are paying for; a new lane's first question is
    "which baked image?". The plan's `R13-b` cell says "Vast, baked image". This checks that claim against
    the files rather than repeating it.
    """
    findings = []
    dockerfiles = sorted(f for f in os.listdir(COMPUTE) if f.startswith("Dockerfile."))
    with_boltz = []
    for f in dockerfiles:
        try:
            with open(os.path.join(COMPUTE, f), errors="replace") as fh:
                if "boltz" in fh.read().lower():
                    with_boltz.append(f)
        except OSError:
            pass
    findings.append({
        "check": "a baked image carrying Boltz exists",
        "got": with_boltz, "want": "at least one Dockerfile.* naming boltz",
        "ok": bool(with_boltz),
        "note": "Dockerfiles scanned: %s" % ", ".join(dockerfiles),
    })

    builds_on_host = False
    image = None
    try:
        with open(VAST_LAUNCH, errors="replace") as fh:
            src = fh.read()
        seg = src.split("_COFOLD_PIPELINE", 1)[-1].split("def build_cofold_jobspec", 1)[0]
        builds_on_host = ("pip install" in seg) or ("apt-get install" in seg)
        for line in src.splitlines():
            if line.startswith("COFOLD_IMAGE"):
                image = line.split("or", 1)[-1].strip().strip('"')
    except OSError:
        pass
    findings.append({
        "check": "the repo's Vast co-fold lane does NOT build its environment on the billing host",
        "got": {"image": image, "installs_on_host": builds_on_host},
        "want": {"installs_on_host": False},
        "ok": not builds_on_host,
        "note": "nrv04_vast_launch._COFOLD_PIPELINE. CLAUDE.md §6 records this exact shape as the "
                "2026-08-01 violation: a rented 4090 running apt-get + pip install boltz + a ~3 GB fetch "
                "off stock pytorch/pytorch, before one second of science.",
    })

    findings.append({
        "check": "a Vast lane exists that runs fusion_cofold.py (rather than the ternary entry points)",
        "got": "the only fusion_cofold launcher is .github/workflows/gpu-cofold-aws.yml (SageMaker); the "
               "Vast co-fold lane hard-codes TERNARY_SCRIPT and pip-installs on the host",
        "want": "a Vast lane whose entry point is the fusion co-fold",
        "ok": False,
        "note": "CLAUDE.md §6: production runs go on Vast. The plan's R13-b cell says Vast; the only "
                "wired path for this script is AWS SageMaker.",
    })

    return {
        "verdict": "BLOCKED" if not all(f["ok"] for f in findings) else "READY",
        "findings": findings,
        "what_is_required_before_a_nod_can_be_acted_on": [
            "Bake a Boltz image (a Dockerfile.boltz sibling + a bake workflow, the ternary-fep-bake.yml "
            "pattern) so the rented host PULLS instead of solving. CLAUDE.md §6 gives the measured "
            "difference as ~15-25 min of solve against a ~2-4 min pull — on a rented GPU that is billed "
            "time, and three of four dead hosts on the 2026-08-01 lane died inside the fetch window.",
            "Mount research/modalities into the container (-v \"$PWD/research/modalities:/work/research/"
            "modalities\") or the host silently runs the copy baked at build time.",
            "Point a Vast lane at the committed YAMLs in research/modalities/fusion_cofold_inputs/<object>/ "
            "so the rented host fetches NO sequence: the cut is already done, verified and committed here.",
        ],
    }


# ------------------------------------------------------------------------------------------ map edits
def map_edits_required(built, ok):
    """DESCRIBED, NEVER APPLIED (the paralogue_pocket_contrast.py convention). The roadmap, systems/graph/*
    and systems/views/* are not writable from here; these are the edits a human or an authorised pass owes."""
    t1 = built["t1_reported_canonical"]["constructs"]
    e7 = built["e7e3_plan_literal"]["constructs"]
    return [
        {
            "file": "systems/graph/objects.json",
            "section": "OBJ-NR4A3-AF1 -> notes",
            "current_text": "This is the domain the fusion REPLACES with EWSR1's low-complexity region. Any "
                            "ligand whose whole mechanism lives here cannot act on the chimera at any dose",
            "proposed_text": "⛔ REFUTED 2026-08-06 by finding X9: the fusion RETAINS this domain. NR4A3 "
                             "transcript exons 1-2 are non-coding, so 'NR4A3 exon 3' IS residue 1 and every "
                             "reported EWSR1::NR4A3 type keeps AF-1, the DBD, the hinge and the LBD; "
                             "EWSR1-LC is ADDITIVE, not a replacement. Superseded, retained: the swap "
                             "framing and the 'cannot act on the chimera at any dose' closure.",
            "why": "this object's notes still teach the refuted swap premise as fact, and it is the premise "
                   "R13-b's constructs are being re-cut away from. X9 is settled and $0-reproducible "
                   "(systems/AUDIT-2026-08-06-routes.md; research/modalities/fusion-object-inventory.json).",
            "artifact": "research/modalities/fusion-cofold-constructs.json",
        },
        {
            "file": "systems/graph/integrity.json",
            "section": "open_conflicts -> OC-2",
            "current_text": "'the canonical EMC fusion' names two incompatible objects, and one working "
                            "module is built on the one that is not a reported fusion type.",
            "proposed_text": "UNCHANGED as a conflict; ADD to `positions`: \"R13-b's pre-launch cut "
                             "(fusion_cofold_recut.py) builds BOTH objects and defaults to NEITHER — "
                             "`--object` is required. The two seams differ: OBJ-FUS-T1's is EWSR1(%d-%d) "
                             "plus %d junction-encoded residue(s); OBJ-MODEL-E7E3's is EWSR1(%d-%d) with "
                             "none. The nod that authorises R13-b is therefore also the nod that resolves "
                             "OC-2, and it cannot be taken silently.\"" % (
                                 t1["seam"]["five_prime_range"][0], t1["seam"]["five_prime_range"][1],
                                 len(t1["seam"]["junction_encoded_residues"]),
                                 e7["seam"]["five_prime_range"][0], e7["seam"]["five_prime_range"][1]),
            "why": "OC-2's `why_not_decided` says at least three modules would have to move together and "
                   "the choice is not a navigation-layer call. It is now a launch-blocking choice with a "
                   "named decision point, which is new information about the conflict.",
            "artifact": "research/modalities/fusion-cofold-constructs.json",
        },
        {
            "file": "research/manuscripts/nr4a3-program-map.md",
            "section": "THE ORDERED PLAN -> RUNG S -> `R13-b`",
            "current_text": "The `seam` and `composite` constructs of [`fusion_cofold.py`]"
                            "(../../research/modalities/fusion_cofold.py), re-cut to the corrected junction.",
            "proposed_text": "The `seam` and `composite` constructs, re-cut to the corrected junction and "
                             "committed as INPUTS by `fusion_cofold_recut.py` "
                             "([`fusion-cofold-constructs.json`](../modalities/fusion-cofold-constructs.json), "
                             "$0, gate `%s`) — so the rented host runs inference only and fetches no sequence. "
                             "⛔ THE CUT IS NOT SINGLE-VALUED: OC-2 is open and the two candidate objects have "
                             "DIFFERENT seams, so the nod must name the object as well as the spend."
                             % ("PASS" if ok else "REFUSED"),
            "why": "'the corrected junction' reads as one thing and is two. The cut is now done, verified "
                   "and committed, and what remains for the nod is an object choice the plan does not state.",
            "artifact": "research/modalities/fusion-cofold-constructs.json",
        },
        {
            "file": "research/manuscripts/nr4a3-program-map.md",
            "section": "THE ORDERED PLAN -> RUNG S -> `R13-b`, the where-it-runs cell",
            "current_text": "· Vast, baked image.",
            "proposed_text": "· Vast — ⛔ **NO BAKED BOLTZ IMAGE EXISTS.** `grep -l boltz research/compute/"
                             "Dockerfile.*` returns nothing, and the repo's only Vast co-fold lane "
                             "(`nrv04_vast_launch._COFOLD_PIPELINE`) still `apt-get`s and "
                             "`pip install`s boltz + cuequivariance onto the BILLING host off stock "
                             "`pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime` — the exact 2026-08-01 "
                             "violation CLAUDE.md §6 records. Bake one before launching.",
            "why": "the rung's own where-it-runs cell asserts a capability the repo does not have. Measured "
                   "2026-08-06 by reading the Dockerfiles and the launcher, $0.",
            "artifact": "research/modalities/fusion-cofold-constructs.json",
        },
    ]


# ------------------------------------------------------------------------------------------------ main
def build_all():
    inp = load_inputs()
    built = {k: build_object(k, inp) for k in OBJECT_SPECS}
    checks, ok = run_checks(inp, built)
    return inp, built, checks, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="run the gate only; write nothing. Exit 1 on any failed check.")
    ap.add_argument("--object", choices=sorted(OBJECT_SPECS), nargs="+",
                    help="write the Boltz YAMLs for these objects. Deliberately has NO default — see OC-2. "
                         "Writing both is not choosing between them: the LAUNCH names one directory, and "
                         "that naming is where the OC-2 decision is taken and recorded.")
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args()

    inp, built, checks, ok = build_all()

    for c in checks:
        if not c["ok"]:
            print("FAIL  %s -> got %r want %r" % (c["check"], c["got"], c["want"]), file=sys.stderr)
    print("gate: %s  (%d/%d checks)" % ("PASS" if ok else "REFUSED",
                                        sum(1 for c in checks if c["ok"]), len(checks)))

    if args.check:
        return 0 if ok else 1
    if not ok:
        print("REFUSING to write construct inputs — a mis-cut construct silently wastes the whole rung.",
              file=sys.stderr)
        return 1

    yaml_written = []
    for obj in (args.object or []):
        d = os.path.join(OUT_DIR, obj)
        os.makedirs(d, exist_ok=True)
        for name, c in sorted(built[obj]["constructs"].items()):
            p = os.path.join(d, "%s.yaml" % name)
            with open(p, "w") as fh:
                fh.write(boltz_yaml_apo([("A", c["chain"])]))
            yaml_written.append(os.path.relpath(p, REPO))

    out = {
        "_title": "R13-b pre-launch — the two fusion co-fold constructs, re-cut to the corrected junction",
        "_owner": "research/manuscripts/nr4a3-program-map.md — THE ORDERED PLAN, RUNG S, `R13-b`",
        "_cost": "$0 — pure stdlib, no network, no rental. This artifact dispatches nothing.",
        "_serves": "R13",
        "_scope": "SEQUENCE ONLY. No structure, pose, reach, affinity, degradation quantity, selectivity, "
                  "efficacy, safety, tolerability, therapeutic-window or clinical claim is made or implied.",
        "⛔_PRE_REGISTERED_GATE_FOR_THE_RUN_THIS_PREPARES": (
            "Written before the run because a null is the EXPECTED outcome. fusion_cofold.py's own prior is "
            "that the EWSR1 side is a prion-like IDR (mean pLDDT 38.8, 98% of residues < 50) and that a "
            "de-novo fusion junction carries NO cross-seam coevolution for an MSA-based predictor to use. "
            "ABSENCE OF AN ORDERED COMPOSITE INTERFACE IS THEREFORE A FEASIBILITY READ, NOT EVIDENCE THAT "
            "NO POCKET CAN FORM, AND MAY NOT BE REPORTED AS A REFUTATION. A GO is an interface cavity "
            "present in >=4 of 6 seeds on the `composite` construct that is ABSENT from both parent "
            "AlphaFold models; anything less is INDETERMINATE, a third outcome."),
        "why_a_recut_was_owed": (
            "finding X9 (systems/AUDIT-2026-08-06-routes.md) SETTLED that the fusion RETAINS NR4A3's AF-1: "
            "NR4A3 transcript exons 1-2 are non-coding, so 'exon 3' IS residue 1. fusion_cofold.py resumes "
            "at residue 2. The re-cut resumes at 1."),
        "⛔_the_cut_is_not_single_valued": (
            "OC-2 (systems/graph/integrity.json) is OPEN and its owner is R13. Two objects answer to 'the "
            "corrected junction' and their SEAMS DIFFER, which is the one thing a seam co-fold cannot be "
            "agnostic about. Both are built here; neither is a default; `--object` is required."),
        "seed_plan": {"seeds": SEEDS, "constructs_per_object": 2,
                      "models": len(SEEDS) * 2,
                      "_matches": "scope-rung-cost.json rung R13-b `units` = 12 (construct x seed)"},
        "ews_seam_len": EWS_SEAM_LEN,
        "dollar_ceiling": dollar_ceiling(),
        "launch_path_check": launch_path_check(),
        "gate": {"status": "PASS" if ok else "REFUSED", "n_checks": len(checks),
                 "n_failed": sum(1 for c in checks if not c["ok"]), "checks": checks},
        "objects": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                    for k, v in built.items()},
        "yaml_written": yaml_written,
        "map_edits_required": map_edits_required(built, ok),
        "refusals": [
            "$/ns is NOT reported for this rung and its absence is a refusal, not a gap: a co-fold "
            "integrates no dynamics, so there is no nanosecond denominator. R13-b is gated on its DOLLAR "
            "ceiling alone (scope-rung-cost.json rung R13-b `_why_no_usd_per_ns`), and any refusal must "
            "name which ceiling it hit.",
            "No baked image carrying Boltz exists in this repo (measured 2026-08-06: `grep -l boltz "
            "research/compute/Dockerfile.*` returns nothing). Until one exists, R13-b cannot be launched "
            "in compliance with CLAUDE.md §6 — the only Vast co-fold lane pip-installs onto the billing "
            "host.",
            "The patient-level breakpoint is not pinned; EMC carries several reported types. Neither "
            "object here is 'the' junction of any particular patient, and the co-fold cannot make it one.",
        ],
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote %s" % os.path.relpath(args.out, REPO))
    for p in yaml_written:
        print("wrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
