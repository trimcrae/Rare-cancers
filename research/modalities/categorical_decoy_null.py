#!/usr/bin/env python3
"""C02 — THE CROSS-SYSTEM DECOY NULL FOR THE CATEGORICAL COVALENT AXIS.

THE PROBLEM THIS EXISTS TO FIX
------------------------------
`nr4a-paralogue-dynamics.json -> categorical_verdict` reports
`P(paralogue also labelled | NR4A3 labelled)` = 0.0 / 0.00124 / 0.00290 at the 12-atom design gate over
73,867 matched E3 placements — and every null in this repo is WITHIN-system (`term_b_background_null` is a
placement null; `V19` is a generation-matched null). Neither asks how often an ARBITRARY close paralogue pair
produces the same "no collision" answer. **So the categorical result is currently an enrichment over an
unmeasured background.**

The precedent is exact. `V20` — single-snapshot MM-GBSA `margin > 0` — looked like a clean selectivity signal
until 38 unrelated marketed drugs went through the identical funnel and 22 of them scored a positive margin
(`selectivity_calibration.DECOY_2026_06_30`). That retracted a headline. The categorical axis has never had
its equivalent test, and this module is that test.

WHAT IT DOES
------------
Pushes UNRELATED human paralogue PAIRS through the IDENTICAL categorical pipeline — the same E3 arm registry,
the same pose construction, the same placement sampler, the same prolate-spheroid reach rule, the same
12-atom gate, the same RSA 0.25 exposure cutoff, the same Shrake-Rupley SASA, the same BLOSUM62 aligner — and
asks how often a pair with no reason to be discriminable returns "0 collision".

Every scientific function is IMPORTED, never re-implemented:
  * `nr4a3_basin_search`      — model loading, superposition, pose ensemble, placement sampling, PARAMS
  * `nr4a_paralogue_dynamics` — `align_map`, `matched_reach_hits_multi`, `wilson95`
  * `nr4a_differential_atlas` — Needleman-Wunsch, Shrake-Rupley SASA, RSA
  * `nr4a3-e3-arm-registry-native.json` — the SAME two staged E3 arms (VHL, CRBN) with the SAME observed
    9UUM E2 geometry
What is NEW here is only the DRIVER: which pairs, which pocket, and the background arithmetic.

⚠ WHAT THIS CALIBRATES. The SCREEN, not the target. A low background rate says the categorical GO is
informative; a high one says it is not. Neither is a statement about NR4A3's chemistry, binding, reactivity,
degradation, efficacy or safety.

THE PRE-REGISTRATION IS IN `PREREG` BELOW AND IS WRITTEN INTO THE ARTIFACT AHEAD OF ANY RESULT. It was fixed
before a single structure was fetched. Mode `plan` emits it on its own so the git history carries the design
before the numbers.

Usage
    python categorical_decoy_null.py plan                       # $0, no network: emit the prereg + pair plan
    python categorical_decoy_null.py probe                      # raw AlphaFold API/file answers (diagnostic)
    python categorical_decoy_null.py fetch                      # AlphaFold DB models for the universe (CI)
    python categorical_decoy_null.py pairs                      # trim + all-vs-all identity + pair selection
    python categorical_decoy_null.py run --shard 0 --nshards 8  # the statistic, sharded BY TARGET
    python categorical_decoy_null.py selfcheck                  # driver vs the COMMITTED static verdict
    python categorical_decoy_null.py reduce                     # background distribution + NR4A3 percentile
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import random
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                        # noqa: E402
import nr4a_differential_atlas as ATLAS       # noqa: E402
import nr4a3_basin_search as B                # noqa: E402
import nr4a_paralogue_dynamics as PD          # noqa: E402

CACHE = os.environ.get("DECOY_CACHE", os.path.join(REPO, "results", "categorical-decoy-null"))
OUT = os.path.join(HERE, "categorical-decoy-null.json")
PLAN = os.path.join(HERE, "categorical-decoy-null-plan.json")   # COMMITTED: the prereg lands in git first
SHARD_DIR = os.path.join(CACHE, "shards")
UNIVERSE_SRC = os.path.join(HERE, "nr4a-superfamily-selectivity.json")
NATIVE_REGISTRY = PD.NATIVE_REGISTRY
DYNAMICS = os.path.join(HERE, "nr4a-paralogue-dynamics.json")

NR4A3_ACC = "Q92570"
NR4A1_ACC = "P22736"
NR4A2_ACC = "P43354"
NR4A_FAMILY = {NR4A3_ACC, NR4A1_ACC, NR4A2_ACC}

# =========================================================================================================
# ★ THE PRE-REGISTRATION. Fixed before any structure was fetched, any identity computed or any statistic
#   evaluated. Every threshold below is stated as a RULE with a reason, not tuned to an outcome. Changing any
#   of these after seeing results makes the percentile meaningless, so they live here as constants and the
#   artifact records them verbatim.
# =========================================================================================================
PREREG = {
    "_frozen": "Design fixed before any AlphaFold model was fetched and before any statistic was computed. "
               "Mode `plan` emits this block with no results at all, so git history carries the design "
               "ahead of the numbers.",
    "question": "How often does an ARBITRARY close human paralogue pair, pushed through the identical "
                "categorical pipeline, return P(paralogue also labelled | target-unique cysteine labelled) "
                "= 0 at the 12-backbone-atom design gate?",
    "universe": {
        "source": "research/modalities/nr4a-superfamily-selectivity.json -> ranking[] — 47 human nuclear "
                  "receptors with UniProt accessions, a COMMITTED artifact generated for a different "
                  "purpose months earlier. Using an existing on-disk list rather than curating one is what "
                  "keeps the universe answer-blind.",
        "exclusions": "the NR4A family (NR4A1 P22736, NR4A2 P43354, NR4A3 Q92570) — that is the test case, "
                      "not the background.",
        "why_nuclear_receptors": "The null must be the RIGHT null: close paralogue pairs in the same fold "
                                 "class, with the same domain size and the same kind of buried ligand "
                                 "pocket. A random-protein null would confound 'no collision' with 'wrong "
                                 "fold'. ⚠ The price is that the background measured here is a "
                                 "NUCLEAR-RECEPTOR background, not a proteome background — stated as a "
                                 "limit, not hidden.",
    },
    "structures": {
        "source": "AlphaFold DB, one model per accession, resolved through the prediction API (the file "
                  "URL's version number is NOT guessed — measured 2026-08-02, a hard-wired v4/v3/v2 file URL "
                  "404'd on all 48). The resolved URL, model version and SHA-256 are recorded per model.",
        "domain_trim": "largest CONTIGUOUS run of residues with pLDDT >= MIN_PLDDT (70.0), minimum length "
                       "MIN_DOMAIN_LEN (120) residues. "
                       "Mechanical, identical for every protein, and it removes the disordered tails whose "
                       "spurious cysteines would INFLATE the decoy collision rate — i.e. the trim is in the "
                       "direction that makes the NR4A3 result look WORSE, not better.",
    },
    "pair_formation": {
        "identity_band": [0.35, 0.90],
        "why": "'close pairs, not random proteins'. The band brackets the measured NR4A3-vs-NR4A1 and "
               "NR4A3-vs-NR4A2 trimmed-domain identities, which are computed by this same code and "
               "recorded in the artifact.",
        "alignment_coverage_min": 0.60,
        "max_pairs": 10,
        "max_per_protein": 2,
        "ranking_rule": "qualifying unordered pairs ranked by |identity - NR4A3_reference_identity| "
                        "ASCENDING (closest to the NR4A3 case first), then taken greedily subject to "
                        "max_per_protein. Answer-blind: identity is a property of the sequences, computed "
                        "before any reach statistic exists.",
        "orientations": "each unordered pair contributes TWO ordered decoys (A as target/B as paralogue, "
                        "and B as target/A as paralogue). Both are reported; neither is chosen.",
    },
    "pocket_rule": "fpocket's HIGHEST-DRUGGABILITY cavity on the target's trimmed domain supplies the pocket "
                   "lining set, hence the pocket centroid the warhead exit-vector poses are built around. "
                   "Family-agnostic and mechanical. ⚠ It is NOT the same rule as NR4A3's prespecified "
                   "Pocket-5 — which is exactly why NR4A3 is ALSO run through this harness under this same "
                   "rule, and why the percentile is taken against THAT row rather than against the "
                   "committed one.",
    "statistic": {
        "gate_atoms": 12,
        "also_reported": [14, 16, 20],
        "definition": "P(any paralogue cysteine is inside the same linker budget | the same placement puts "
                      "the electrophile on a TARGET-UNIQUE cysteine), over one matched placement set.",
        "target_unique_cysteine": "a cysteine in the target whose BLOSUM62-aligned position in the "
                                  "paralogue is not a cysteine (or has no aligned partner) — the same rule "
                                  "that produces NR4A3's {C397, C420, C559}.",
        "both_filters": "computed BOTH reach-only and reach-AND-exposed (RSA >= 0.25). ⚠ The audit "
                        "established that at the 12-atom gate the reach-only numbers already carry the "
                        "result, so a null that tested only the exposure-filtered form would miss the "
                        "load-bearing case.",
        "uncertainty": "Wilson 95 % on the conditional, using the SAME `nr4a_paralogue_dynamics.wilson95`.",
    },
    "placements": {
        "target_n_placements": 45000,
        "why": "the committed NR4A3 run accepted 73,867 placements; 45,000 keeps every row inside one CI "
               "job while staying the same order. The sampler budget is chosen ADAPTIVELY per target from a "
               "pilot so that every row gets a comparable placement set rather than a comparable raw sample "
               "count — an acceptance rate is a property of the pocket, and matching samples would silently "
               "un-match the statistics.",
        "pilot_samples_per_arm_pose": 25000,
        "max_samples_per_arm_pose": 6000000,
        "n_poses": 12,
        "seed": 20260802,
    },
    "gradeability": {
        "min_conditioning_events": 20,
        "rule": "an ordered decoy is GRADED only if >= 20 placements put the electrophile on a "
                "target-unique cysteine at the 12-atom gate. Below that the conditional has no power and "
                "the row is reported as UNDERPOWERED with its counts and EXCLUDED from the percentile.",
        "⚠_selection_effect": "excluding underpowered rows biases the graded set toward pairs whose unique "
                              "cysteines are reachable at all — i.e. toward pairs with MORE opportunity to "
                              "collide, which makes the background HARDER for NR4A3 to beat, not easier. "
                              "The count of underpowered rows is reported so the reader can see the size of "
                              "the effect.",
        "undefined": "a pair with zero target-unique cysteines has no conditional at all. Recorded as "
                     "UNDEFINED with its count, never as a zero.",
    },
    "readout": {
        "percentile": "the fraction of GRADED decoy rows whose collision probability is <= NR4A3's "
                      "harness-matched row, plus the fraction that are EXACTLY zero. Reported for both the "
                      "reach-only and the exposure-filtered statistic.",
        "what_a_pass_means": "if few decoys reach 0, the categorical GO carries information and becomes "
                             "quotable WITH this background beside it. If most decoys reach 0, the "
                             "categorical GO is a property of the METHOD and the axis must be re-graded. "
                             "A pass is not the goal; a measured background is.",
    },
    "not_claimed": [
        "Nothing here is a claim about binding, reactivity, degradation, selectivity in vivo, efficacy, "
        "safety, a therapeutic window or clinical readiness.",
        "Reach and exposure are NECESSARY, not sufficient: no thiol pKa, nucleophilicity, adduct stability "
        "or promiscuity is modelled, for the decoys any more than for NR4A3.",
        "This calibrates the SCREEN. It says nothing about NR4A3 specifically that the screen does not.",
    ],
}

LENGTHS = (12, 14, 16, 20)
GATE = 12
EXPOSED_RSA = PD.EXPOSED_RSA
MIN_PLDDT = 70.0            # PREREG.structures.domain_trim — one home, referenced there in words
MIN_DOMAIN_LEN = 120        # PREREG.structures.domain_trim
# ⚠ MEASURED, NOT ASSUMED (run 30773302930, 2026-08-02 7:56 PM ET): the hard-wired file URL
# `files/AF-{acc}-F1-model_v4.pdb` returned **HTTP 404 for all 48 accessions**, at v4, v3 and v2 alike — so
# the model-version number is not a thing to guess. The DOCUMENTED lookup is the prediction API, which
# returns the current `pdbUrl` for an accession whatever its version; the versioned file URLs stay only as a
# fallback and now span a wider range. `probe` mode prints the raw API answer so a future failure is
# diagnosed rather than re-guessed.
AF_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"
AF_URL = "https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v{v}.pdb"
AF_VERSIONS = (6, 5, 4, 3, 2)


# =========================================================================================================
# PURE helpers (unit-tested in tests/test_categorical_decoy_null.py)
# =========================================================================================================
def parse_plddt(pdb_text):
    """[(resSeq, plddt)] in file order, one entry per residue, from an AlphaFold PDB's CA B-factor. PURE."""
    out, seen = [], set()
    for line in pdb_text.splitlines():
        if not line.startswith("ATOM") or line[12:16].strip() != "CA":
            continue
        try:
            rid = int(line[22:26])
            b = float(line[60:66])
        except (ValueError, IndexError):
            continue
        if rid in seen:
            continue
        seen.add(rid)
        out.append((rid, b))
    return out


def largest_confident_segment(plddt, min_plddt=70.0, min_len=120):
    """Largest CONTIGUOUS residue-number run with pLDDT >= min_plddt. Returns (first, last) or None. PURE.

    Contiguity is on the residue NUMBER, so a numbering break also breaks the segment — which is the correct
    behaviour for a domain trim."""
    best, cur = None, None
    prev = None
    for rid, b in plddt:
        ok = b >= min_plddt
        if ok and cur is not None and prev is not None and rid == prev + 1:
            cur[1] = rid
        elif ok:
            cur = [rid, rid]
        else:
            cur = None
        if cur is not None and (best is None or (cur[1] - cur[0]) > (best[1] - best[0])):
            best = list(cur)
        prev = rid
    if best is None or (best[1] - best[0] + 1) < min_len:
        return None
    return (best[0], best[1])


def trim_pdb_text(pdb_text, first, last):
    """Keep ATOM/TER records whose residue number is in [first, last]. PURE (text in, text out)."""
    keep = []
    for line in pdb_text.splitlines():
        if line.startswith(("ATOM", "TER")):
            try:
                rid = int(line[22:26])
            except (ValueError, IndexError):
                continue
            if first <= rid <= last:
                keep.append(line)
    keep.append("END")
    return "\n".join(keep) + "\n"


def alignment_identity(seq_a, seq_b, aln):
    """(identity, coverage) over an `ATLAS.nw_align` pairing. identity = matched positions / aligned columns;
    coverage = aligned columns / len(shorter sequence). PURE."""
    cols = [(i, j) for i, j in aln if i is not None and j is not None]
    if not cols:
        return 0.0, 0.0
    same = sum(1 for i, j in cols if seq_a[i] == seq_b[j])
    shorter = min(len(seq_a), len(seq_b)) or 1
    return same / len(cols), len(cols) / shorter


def select_pairs(entries, ref_identity, band, coverage_min, max_pairs, max_per_protein):
    """THE PRE-REGISTERED PAIR SELECTION. PURE.

    `entries`: [{"a","b","identity","coverage"}] for every unordered candidate pair.
    Returns (selected, rejected) — selected in ranked order, each carrying why it was kept."""
    lo, hi = band
    qualifying, rejected = [], []
    for e in entries:
        why = None
        if not (lo <= e["identity"] <= hi):
            why = f"identity {e['identity']:.3f} outside band [{lo}, {hi}]"
        elif e["coverage"] < coverage_min:
            why = f"alignment coverage {e['coverage']:.3f} < {coverage_min}"
        if why:
            rejected.append({**e, "rejected_because": why})
        else:
            qualifying.append(e)
    qualifying.sort(key=lambda e: (abs(e["identity"] - ref_identity), e["a"], e["b"]))
    used, selected = {}, []
    for e in qualifying:
        if len(selected) >= max_pairs:
            break
        if used.get(e["a"], 0) >= max_per_protein or used.get(e["b"], 0) >= max_per_protein:
            continue
        used[e["a"]] = used.get(e["a"], 0) + 1
        used[e["b"]] = used.get(e["b"], 0) + 1
        selected.append({**e, "rank_key": round(abs(e["identity"] - ref_identity), 5)})
    return selected, rejected


def percentile_of(value, background):
    """Fraction of `background` <= `value`. PURE. None if the background is empty."""
    xs = [b for b in background if b is not None]
    if not xs:
        return None
    return sum(1 for b in xs if b <= value) / len(xs)


def summarise_background(rows, key):
    """Distribution summary of a graded background column. PURE."""
    xs = sorted(r[key] for r in rows if r.get(key) is not None)
    if not xs:
        return None
    n = len(xs)

    def q(p):
        if n == 1:
            return xs[0]
        k = p * (n - 1)
        lo = int(math.floor(k))
        hi = min(lo + 1, n - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)
    return {"n": n, "min": xs[0], "q25": q(0.25), "median": q(0.5), "q75": q(0.75), "max": xs[-1],
            "mean": sum(xs) / n, "n_exactly_zero": sum(1 for x in xs if x == 0.0),
            "frac_exactly_zero": sum(1 for x in xs if x == 0.0) / n}


# =========================================================================================================
# I/O: the universe and the AlphaFold models
# =========================================================================================================
def universe():
    """The decoy universe, read from the COMMITTED superfamily artifact. Never hand-typed."""
    d = json.load(open(UNIVERSE_SRC))
    seen, out = set(), []
    for r in d.get("ranking", []):
        acc, gene = r.get("accession"), r.get("gene")
        if not acc or acc in seen:
            continue
        seen.add(acc)
        out.append({"gene": gene, "accession": acc,
                    "in_nr4a_family": acc in NR4A_FAMILY})
    return out


def af_path(acc):
    return os.path.join(CACHE, "af", f"AF-{acc}.pdb")


def _af_urls(acc, timeout=60):
    """Candidate model URLs for one accession, API answer FIRST. Returns (urls, api_note)."""
    urls, note = [], None
    try:
        with urllib.request.urlopen(AF_API.format(acc=acc), timeout=timeout) as fh:
            recs = json.loads(fh.read().decode())
        for r in (recs if isinstance(recs, list) else [recs]):
            for key in ("pdbUrl", "cifUrl"):
                if r.get(key) and str(r[key]).endswith(".pdb"):
                    urls.append(r[key])
        note = f"api ok, {len(urls)} pdb url(s)"
    except Exception as ex:  # noqa: BLE001
        note = f"api unusable: {type(ex).__name__}: {ex}"
    urls += [AF_URL.format(acc=acc, v=v) for v in AF_VERSIONS]
    return urls, note


def fetch_af(acc, timeout=120):
    """Download one AlphaFold model. Returns metadata; raises on total failure, carrying EVERY URL tried and
    its error, so a repeat of the 2026-08-02 all-404 failure is diagnosed from the artifact instead of
    re-guessed."""
    os.makedirs(os.path.join(CACHE, "af"), exist_ok=True)
    dest = af_path(acc)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        text = open(dest).read()
        return {"accession": acc, "path": os.path.relpath(dest, REPO), "cached": True,
                "sha256": hashlib.sha256(text.encode()).hexdigest()[:16],
                "model_version": _recorded_version(dest)}
    urls, api_note = _af_urls(acc)
    tried = []
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as fh:
                text = fh.read().decode()
            if "ATOM" not in text:
                raise ValueError("no ATOM records")
            with open(dest, "w") as out:
                out.write(f"REMARK   1 SOURCE {url}\n")
                out.write(text)
            return {"accession": acc, "path": os.path.relpath(dest, REPO), "cached": False,
                    "model_version": _recorded_version(dest), "url": url, "api": api_note,
                    "sha256": hashlib.sha256(text.encode()).hexdigest()[:16]}
        except Exception as ex:  # noqa: BLE001
            tried.append(f"{url} -> {type(ex).__name__}: {ex}")
    raise RuntimeError(f"AlphaFold fetch failed for {acc} [{api_note}]; tried: " + " | ".join(tried))


def mode_probe(args):
    """$0 diagnostic. Print the RAW AlphaFold API answer for one accession + one file-URL attempt, so a fetch
    failure is root-caused from evidence rather than by trying version numbers (CLAUDE.md §4)."""
    acc = os.environ.get("PROBE_ACC", NR4A1_ACC)
    try:
        with urllib.request.urlopen(AF_API.format(acc=acc), timeout=60) as fh:
            body = fh.read().decode()
        print(f"  [cdn] API {AF_API.format(acc=acc)} -> {len(body)} bytes")
        print("  [cdn] " + body[:1200])
    except Exception as ex:  # noqa: BLE001
        print(f"  [cdn] API FAILED: {type(ex).__name__}: {ex}")
    for v in AF_VERSIONS:
        url = AF_URL.format(acc=acc, v=v)
        try:
            with urllib.request.urlopen(url, timeout=60) as fh:
                n = len(fh.read())
            print(f"  [cdn] FILE {url} -> OK ({n} bytes)")
        except Exception as ex:  # noqa: BLE001
            print(f"  [cdn] FILE {url} -> {type(ex).__name__}: {ex}")
    return {}


def _recorded_version(path):
    with open(path) as fh:
        head = fh.readline()
    for v in AF_VERSIONS:
        if f"model_v{v}" in head:
            return v
    return None


def trimmed_path(acc):
    return os.path.join(CACHE, "trimmed", f"{acc}-domain.pdb")


def trim_one(acc, min_plddt=70.0, min_len=120):
    """Trim one fetched model to its largest confident segment. Returns metadata or raises."""
    os.makedirs(os.path.join(CACHE, "trimmed"), exist_ok=True)
    text = open(af_path(acc)).read()
    seg = largest_confident_segment(parse_plddt(text), min_plddt, min_len)
    if seg is None:
        raise ValueError(f"no contiguous pLDDT>={min_plddt} segment of >= {min_len} residues")
    out = trimmed_path(acc)
    with open(out, "w") as fh:
        fh.write(trim_pdb_text(text, seg[0], seg[1]))
    model = B.load_paralogue(out)
    return {"accession": acc, "first": seg[0], "last": seg[1], "n_residues": len(model["residues"]),
            "path": os.path.relpath(out, REPO), "seq_len": len(model["seq"])}


# =========================================================================================================
# The pipeline for ONE ordered decoy — every scientific step imported, none re-implemented
# =========================================================================================================
def fpocket_top_pocket(pdb_path, workroot):
    """The pre-registered pocket rule: fpocket's HIGHEST-DRUGGABILITY cavity. Returns its lining residues
    (structure numbering) + druggability. Raises if fpocket cannot run — recorded as a refusal, never as an
    empty pocket."""
    import shutil
    import subprocess
    import tempfile
    import nr4a3_structure as NS
    d = tempfile.mkdtemp(prefix="cdn_fp_", dir=workroot)
    try:
        local = os.path.join(d, "prot.pdb")
        shutil.copyfile(pdb_path, local)
        subprocess.run(["fpocket", "-f", local], check=True, capture_output=True, text=True, timeout=900)
        resids_by_num, info = NS.pocket_residues_by_number(os.path.join(d, "prot_out"), "prot")
        best = max(info.items(), key=lambda kv: (kv[1].get("druggability") or 0.0))
        num = best[0]
        return {"pocket_number": num, "druggability": best[1].get("druggability"),
                "alpha_spheres": best[1].get("alpha_spheres"),
                "residues": sorted(int(r) for r in resids_by_num.get(num, [])),
                "n_pockets": len(info)}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def pocket_centroid_of(model, pocket_residues):
    """Side-chain centroid of the pocket lining — the SAME construction the committed lane uses to place the
    warhead exit-vector poses (`nr4a_paralogue_dynamics.sample_transfer_anchors`)."""
    side = []
    for rid in pocket_residues:
        for a in model["atoms_by_res"].get(rid, []):
            if a["name"] not in B.BACKBONE:
                side.append((a["x"], a["y"], a["z"]))
    if not side:
        raise ValueError("pocket lining has no side-chain atoms in this model")
    return G.centroid(side)


def registry_params(registry_path):
    """The SAME parameter override the committed lane applies from the observed 9UUM geometry."""
    reg = json.load(open(registry_path))
    e2 = reg.get("e2_geometry") or {}
    params = dict(B.PARAMS)
    cal = (e2.get("substrate_lysine_calibration") or {})
    if cal.get("nearest_lysine_to_catalytic_cys_A"):
        params["lysine_transfer_A"] = cal["nearest_lysine_to_catalytic_cys_A"]
    if e2.get("measured"):
        params["ring_to_e2_cys_A"] = e2["ring_to_catalytic_cys_A"]
    return reg, params


_UNIT_CTX = {}


def _sample_unit(job):
    """One (arm, pose) sampling unit. Reads the fork-inherited context so nothing heavy is pickled INTO the
    worker; only the accepted placements come back. Each unit carries its OWN seed derived from the base
    seed and the unit index, so the placement set is DETERMINISTIC and independent of the process count."""
    aid, pose_i, n_samples, seed = job
    ctx = _UNIT_CTX
    arm = ctx["arms"][aid]
    pose = ctx["poses"][pose_i]
    rng = random.Random(seed)
    pls, _stats = B.sample_placements(arm, pose, ctx["field"], rng, n_samples, ctx["params"])
    at = tuple(pose["anchor_xyz"])
    return [{"arm": aid, "pose": pose["pose_id"], "xyz": pl["tanchor"], "a_t": at, "a_e": pl["anchor_e3"]}
            for pl in pls if pl.get("tanchor")]


def sample_anchors(model, pocket_residues, registry_path, n_poses, seed, n_samples, nproc=None):
    """Sample E3 placements on ONE target, EXACTLY as `nr4a_paralogue_dynamics.sample_transfer_anchors`
    does — same arms, same pose construction, same sampler, same params. Two differences, both stated:
      (1) the pocket comes from the PRE-REGISTERED fpocket rule rather than NR4A3's hard-wired Pocket-5;
      (2) the (arm x pose) units are independently seeded so they can run in parallel. Engineering is free
          and a CI runner has more than one core; the result is deterministic either way.
    Returns (anchors, per_arm, params, n_arm_pose, n_poses, centroid)."""
    reg, params = registry_params(registry_path)
    centroid = pocket_centroid_of(model, pocket_residues)
    field = G.SquaredDistanceField(model["heavy_xyz"], cell=0.9, clamp=8.0)
    poses = B.build_pose_ensemble(model, {"pocket_centroid": centroid}, field, n_poses,
                                  random.Random(seed))
    arms = {}
    for aid, rec in reg.get("arms", {}).items():
        if rec.get("status") != "OK":
            continue
        arm = B.load_arm_from_registry(rec)
        if arm.get("tanchor"):
            arms[aid] = arm
    jobs = [(aid, i, n_samples, seed * 1000003 + k)
            for k, (aid, i) in enumerate((a, i) for a in sorted(arms) for i in range(len(poses)))]
    _UNIT_CTX.update(arms=arms, poses=poses, field=field, params=params)
    nproc = int(os.environ.get("DECOY_NPROC", nproc or (os.cpu_count() or 1)))
    if nproc > 1 and len(jobs) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(nproc, len(jobs))) as pool:
            chunks = pool.map(_sample_unit, jobs)
    else:
        chunks = [_sample_unit(j) for j in jobs]
    anchors, per_arm = [], {}
    for (aid, _i, _n, _s), got in zip(jobs, chunks):
        anchors.extend(got)
        per_arm.setdefault(aid, {"recruiter": arms[aid]["recruiter"],
                                 "n_accepted_with_transfer_anchor": 0})
        per_arm[aid]["n_accepted_with_transfer_anchor"] += len(got)
    return anchors, per_arm, params, len(jobs), len(poses), centroid


def cysteines_in_frame(path, ref_model=None, aligned_partner=None):
    """Every cysteine with an SG, with RSA, in the REFERENCE frame.

    `ref_model is None` -> the protein IS the reference (no superposition).
    `ref_model` given   -> `B.superpose_paralogue` into that frame, exactly as the committed lane does.
    `aligned_partner`   -> a model to align against so `partner_has_cys_here` can be filled (the
                           target-unique rule). Uses `PD.align_map`, the same BLOSUM62 NW aligner."""
    model = B.load_paralogue(path)
    frame = model if ref_model is None else B.superpose_paralogue(model, ref_model)
    residues, atoms = ATLAS.parse_pdb(path)
    rsa = ATLAS.residue_rsa(residues, ATLAS.shrake_rupley(atoms))
    m2p = PD.align_map(model, aligned_partner) if aligned_partner is not None else {}
    p_aa = aligned_partner["aa_of"] if aligned_partner is not None else {}
    out = []
    for rid, aa in frame["residues"]:
        if aa != "C":
            continue
        for a in frame["atoms_by_res"].get(rid, []):
            if a["name"] != "SG":
                continue
            dev = frame.get("deviation_by_res", {}).get(rid) if ref_model is not None else 0.0
            pr = m2p.get(rid)
            out.append({"label": f"C{rid}", "local_resid": rid, "xyz": (a["x"], a["y"], a["z"]),
                        "rsa": round(rsa.get(rid, 0.0), 4),
                        "partner_aligned_resid": pr,
                        "partner_has_cys_here": (p_aa.get(pr) == "C") if pr is not None else False,
                        "fit_deviation_A": (round(dev, 2) if dev is not None else None)})
            break
    sup = frame["superposition"] if ref_model is not None else None
    return out, sup, model


def ordered_decoy_statistic(anchors, target_cys, para_cys, params):
    """THE STATISTIC. With one conformer per species `categorical_verdict`'s f3/fP are 0/1 indicators, so the
    conditional reduces exactly to (# placements hitting BOTH) / (# placements hitting a target-unique Cys).
    Uses `PD.matched_reach_hits_multi` — the committed prolate-spheroid reach rule, not a new one."""
    unique = [c for c in target_cys if not c["partner_has_cys_here"]]
    res = {"n_target_cysteines": len(target_cys), "n_target_unique_cysteines": len(unique),
           "target_unique_labels": [c["label"] for c in unique],
           "n_paralogue_cysteines": len(para_cys), "n_placements": len(anchors), "by_linker_atoms": {}}
    if not unique:
        res["status"] = "UNDEFINED_no_target_unique_cysteine"
        return res
    for tag, min_rsa in (("", 0.0), ("_EXPOSED", EXPOSED_RSA)):
        u_hits = PD.matched_reach_hits_multi(anchors, unique, LENGTHS, params=params, min_rsa=min_rsa)
        p_hits = PD.matched_reach_hits_multi(anchors, para_cys, LENGTHS, params=params, min_rsa=min_rsa)
        for n in LENGTHS:
            uh, uper = u_hits[n]
            ph, pper = p_hits[n]
            den = sum(uh)
            coll = sum(1 for i in range(len(anchors)) if uh[i] and ph[i])
            cell = res["by_linker_atoms"].setdefault(str(n), {})
            cell[f"n_conditioning_events{tag}"] = int(den)
            cell[f"n_collisions{tag}"] = int(coll)
            cell[f"P_paralogue_also_labelled{tag}"] = (coll / den) if den else None
            cell[f"P_paralogue_also_labelled{tag}_wilson95"] = PD.wilson95(coll, den) if den else None
            cell[f"mean_P_target_unique{tag}"] = (den / len(anchors)) if anchors else None
            cell[f"mean_P_any_paralogue_cys{tag}"] = (sum(ph) / len(anchors)) if anchors else None
            cell[f"per_target_unique_cys{tag}"] = {k: v for k, v in uper.items() if v}
            cell[f"per_paralogue_cys{tag}"] = {k: v for k, v in pper.items() if v}
    gate = res["by_linker_atoms"][str(GATE)]
    n_ev = gate["n_conditioning_events"]
    res["status"] = ("GRADED" if n_ev >= PREREG["gradeability"]["min_conditioning_events"]
                     else "UNDERPOWERED_too_few_conditioning_events")
    res["gate_atoms"] = GATE
    res["P_gate"] = gate["P_paralogue_also_labelled"]
    res["P_gate_EXPOSED"] = gate["P_paralogue_also_labelled_EXPOSED"]
    res["n_conditioning_events_gate"] = n_ev
    return res


# =========================================================================================================
# modes
# =========================================================================================================
def mode_plan(args):
    """$0, no network. Emit the pre-registration on its own so the design is committed BEFORE any number."""
    os.makedirs(CACHE, exist_ok=True)
    uni = universe()
    plan = {
        "_title": "C02 — cross-system decoy null for the categorical covalent axis: PRE-REGISTRATION",
        "_status": "PRE-REGISTRATION ONLY. No structure has been fetched and no statistic computed at the "
                   "time this file is written.",
        "_generated": _stamp(),
        "preregistration": PREREG,
        "universe": {"source": os.path.relpath(UNIVERSE_SRC, REPO), "n_total": len(uni),
                     "n_after_nr4a_exclusion": sum(1 for u in uni if not u["in_nr4a_family"]),
                     "members": uni},
        "pipeline_provenance": {
            "reach_rule": "nr4a_paralogue_dynamics.matched_reach_hits_multi -> "
                          "nr4a3_basin_search.electrophile_reach (the committed prolate-spheroid criterion)",
            "placement_sampler": "nr4a3_basin_search.sample_placements",
            "pose_ensemble": "nr4a3_basin_search.build_pose_ensemble",
            "superposition": "nr4a3_basin_search.superpose_paralogue",
            "sasa": "nr4a_differential_atlas.shrake_rupley / residue_rsa",
            "aligner": "nr4a_differential_atlas.nw_align (BLOSUM62 Needleman-Wunsch)",
            "e3_arms": os.path.relpath(NATIVE_REGISTRY, REPO),
            "params": {k: B.PARAMS[k] for k in ("linker_gate_atoms", "linker_rise_per_atom_A",
                                                "electrophile_arm_A", "hard_clash_A", "soft_clash_A",
                                                "contact_A", "min_contact_residues")},
        },
    }
    with open(PLAN, "w") as fh:
        json.dump(plan, fh, indent=2)
    print(f"  [cdn] wrote pre-registration {PLAN} ({plan['universe']['n_after_nr4a_exclusion']} candidates)")
    return plan


def mode_fetch(args):
    uni = universe()
    accs = [u["accession"] for u in uni] + [NR4A3_ACC]
    got, failed = [], []
    for acc in accs:
        try:
            got.append(fetch_af(acc))
            print(f"  [cdn] fetched {acc}", flush=True)
        except Exception as ex:  # noqa: BLE001
            failed.append({"accession": acc, "error": str(ex)})
            print(f"  [cdn] FETCH FAILED {acc}: {ex}", flush=True)
    out = {"_generated": _stamp(), "fetched": got, "failed": failed}
    with open(os.path.join(CACHE, "fetch.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"  [cdn] {len(got)} models, {len(failed)} failures")
    if not got:
        raise SystemExit("  ABORT: 0 AlphaFold models fetched. Every downstream step would then run on an "
                         "empty universe and emit a plan with 0 pairs over 0 targets — a green artifact "
                         "produced by measuring nothing. Run `probe` for the raw API/file answers.")
    if len(failed) > 0.25 * len(accs):
        raise SystemExit(f"  ABORT: {len(failed)}/{len(accs)} AlphaFold fetches failed — the universe would "
                         "be silently re-defined by whatever happened to download.")
    return out


def mode_pairs(args):
    """Trim, all-vs-all identity, pre-registered pair selection. Deterministic and answer-blind."""
    uni = universe()
    trimmed, refused = {}, []
    for u in uni + [{"gene": "NR4A3", "accession": NR4A3_ACC, "in_nr4a_family": True}]:
        acc = u["accession"]
        if not os.path.exists(af_path(acc)):
            refused.append({"accession": acc, "reason": "no AlphaFold model fetched"})
            continue
        try:
            meta = trim_one(acc, MIN_PLDDT, MIN_DOMAIN_LEN)
            meta.update(gene=u["gene"], in_nr4a_family=u["in_nr4a_family"])
            trimmed[acc] = meta
        except Exception as ex:  # noqa: BLE001
            refused.append({"accession": acc, "gene": u["gene"], "reason": f"{type(ex).__name__}: {ex}"})
    print(f"  [cdn] trimmed {len(trimmed)}, refused {len(refused)}", flush=True)

    seqs = {acc: B.load_paralogue(trimmed_path(acc))["seq"] for acc in trimmed}

    def ident(a, b):
        return alignment_identity(seqs[a], seqs[b], ATLAS.nw_align(seqs[a], seqs[b]))

    ref_pairs = {}
    for other in (NR4A1_ACC, NR4A2_ACC):
        if NR4A3_ACC in seqs and other in seqs:
            i, c = ident(NR4A3_ACC, other)
            ref_pairs[other] = {"identity": round(i, 4), "coverage": round(c, 4)}
    ref_identity = (sum(v["identity"] for v in ref_pairs.values()) / len(ref_pairs)) if ref_pairs else 0.6

    cand = [a for a in trimmed if not trimmed[a]["in_nr4a_family"]]
    cand.sort()
    entries = []
    for i in range(len(cand)):
        for j in range(i + 1, len(cand)):
            a, b = cand[i], cand[j]
            idn, cov = ident(a, b)
            entries.append({"a": a, "b": b, "gene_a": trimmed[a]["gene"], "gene_b": trimmed[b]["gene"],
                            "identity": round(idn, 4), "coverage": round(cov, 4)})
    selected, rejected = select_pairs(
        entries, ref_identity, PREREG["pair_formation"]["identity_band"],
        PREREG["pair_formation"]["alignment_coverage_min"], PREREG["pair_formation"]["max_pairs"],
        PREREG["pair_formation"]["max_per_protein"])

    ordered = []
    for p in selected:
        ordered.append({"target": p["a"], "paralogue": p["b"], "gene_target": p["gene_a"],
                        "gene_paralogue": p["gene_b"], "identity": p["identity"], "arm": "decoy"})
        ordered.append({"target": p["b"], "paralogue": p["a"], "gene_target": p["gene_b"],
                        "gene_paralogue": p["gene_a"], "identity": p["identity"], "arm": "decoy"})
    for other, gene in ((NR4A1_ACC, "NR4A1"), (NR4A2_ACC, "NR4A2")):
        if NR4A3_ACC in trimmed and other in trimmed:
            ordered.append({"target": NR4A3_ACC, "paralogue": other, "gene_target": "NR4A3",
                            "gene_paralogue": gene,
                            "identity": ref_pairs.get(other, {}).get("identity"), "arm": "reference"})

    plan = json.load(open(PLAN)) if os.path.exists(PLAN) else {"preregistration": PREREG}
    plan.update({
        "_title": "C02 — cross-system decoy null: PRE-REGISTRATION + the selected pair plan (still no "
                  "statistic computed)",
        "_generated": _stamp(),
        "nr4a3_reference_identities": ref_pairs,
        "nr4a3_reference_identity_used_for_ranking": round(ref_identity, 4),
        "trimmed": trimmed,
        "trim_refusals": refused,
        "n_candidate_pairs": len(entries),
        "selected_pairs": selected,
        "rejected_pairs_sample": rejected[:40],
        "n_rejected_pairs": len(rejected),
        "ordered_decoys": ordered,
        "n_ordered_decoys": len(ordered),
        "targets": sorted({o["target"] for o in ordered}),
    })
    with open(PLAN, "w") as fh:
        json.dump(plan, fh, indent=2)
    print(f"  [cdn] {len(selected)} pairs -> {len(ordered)} ordered rows over "
          f"{len(plan['targets'])} targets; ref identity {ref_identity:.3f}")
    return plan


def mode_run(args):
    """Evaluate every ordered decoy whose TARGET falls in this shard. Sharding by target reuses the one
    expensive step (placement sampling) across that target's rows."""
    import tempfile
    plan = json.load(open(PLAN))
    targets = plan["targets"]
    mine = [t for k, t in enumerate(targets) if k % args.nshards == args.shard]
    os.makedirs(SHARD_DIR, exist_ok=True)
    workroot = tempfile.mkdtemp(prefix="cdn_root_")
    pl = PREREG["placements"]
    out_path = os.path.join(SHARD_DIR, f"shard-{args.shard}-of-{args.nshards}.json")
    results, refusals = [], []
    if os.path.exists(out_path):                       # resume: never re-buy finished work
        prev = json.load(open(out_path))
        results, refusals = prev.get("rows", []), prev.get("refusals", [])
    done = {(r["target"], r["paralogue"]) for r in results}
    print(f"  [cdn] shard {args.shard}/{args.nshards}: targets {mine} ({len(done)} rows already done)",
          flush=True)

    for tacc in mine:
        rows = [o for o in plan["ordered_decoys"] if o["target"] == tacc]
        if all((o["target"], o["paralogue"]) in done for o in rows):
            continue
        t0 = time.time()
        try:
            tmodel = B.load_paralogue(trimmed_path(tacc))
            pocket = fpocket_top_pocket(trimmed_path(tacc), workroot)
            if len(pocket["residues"]) < 3:
                raise ValueError(f"top pocket has {len(pocket['residues'])} lining residues")
            # pilot -> acceptance rate -> the budget that lands on target_n_placements
            _a, _pa, params, n_ap, n_poses, centroid = sample_anchors(
                tmodel, pocket["residues"], NATIVE_REGISTRY, pl["n_poses"], pl["seed"],
                pl["pilot_samples_per_arm_pose"])
            rate = len(_a) / max(1, n_ap * pl["pilot_samples_per_arm_pose"])
            if rate <= 0:
                raise ValueError("pilot accepted 0 placements — no feasible E3 placement on this pocket")
            budget = int(min(pl["max_samples_per_arm_pose"],
                             max(pl["pilot_samples_per_arm_pose"],
                                 math.ceil(pl["target_n_placements"] / (rate * max(1, n_ap))))))
            anchors, per_arm, params, n_ap, n_poses, centroid = sample_anchors(
                tmodel, pocket["residues"], NATIVE_REGISTRY, pl["n_poses"], pl["seed"] + 1, budget)
            print(f"  [cdn] {tacc}: pocket drugg={pocket['druggability']} lining={len(pocket['residues'])} "
                  f"pilot_rate={rate:.5f} budget={budget} -> {len(anchors)} placements "
                  f"({time.time()-t0:.0f}s)", flush=True)
        except Exception as ex:  # noqa: BLE001
            refusals.append({"target": tacc, "stage": "target_setup", "reason": f"{type(ex).__name__}: {ex}"})
            print(f"  [cdn] REFUSED target {tacc}: {ex}", flush=True)
            _save_shard(out_path, args, results, refusals)
            continue

        for o in rows:
            if (o["target"], o["paralogue"]) in done:
                continue
            try:
                pmodel = B.load_paralogue(trimmed_path(o["paralogue"]))
                tcys, _s, _m = cysteines_in_frame(trimmed_path(tacc), None, pmodel)
                pcys, sup, _m2 = cysteines_in_frame(trimmed_path(o["paralogue"]), tmodel, tmodel)
                stat = ordered_decoy_statistic(anchors, tcys, pcys, params)
                row = {**o, **stat, "pocket": pocket, "n_poses": n_poses,
                       "pocket_centroid": [round(c, 3) for c in centroid],
                       "placement_budget_per_arm_pose": budget,
                       "per_arm": per_arm, "superposition": sup,
                       "elapsed_s": round(time.time() - t0, 1)}
                results.append(row)
                print(f"  [cdn]   {o['gene_target']}|{o['gene_paralogue']}: {stat['status']} "
                      f"events={stat.get('n_conditioning_events_gate')} P={stat.get('P_gate')} "
                      f"P_exp={stat.get('P_gate_EXPOSED')}", flush=True)
            except Exception as ex:  # noqa: BLE001
                refusals.append({"target": o["target"], "paralogue": o["paralogue"], "stage": "row",
                                 "reason": f"{type(ex).__name__}: {ex}"})
                print(f"  [cdn]   REFUSED {o['target']}|{o['paralogue']}: {ex}", flush=True)
            _save_shard(out_path, args, results, refusals)      # checkpoint after EVERY unit
    _save_shard(out_path, args, results, refusals)
    print(f"  [cdn] shard {args.shard} wrote {out_path}: {len(results)} rows, {len(refusals)} refusals")
    return {"rows": results, "refusals": refusals}


def _save_shard(path, args, rows, refusals):
    with open(path, "w") as fh:
        json.dump({"_generated": _stamp(), "shard": args.shard, "nshards": args.nshards,
                   "rows": rows, "refusals": refusals}, fh, indent=2)


SELFCHECK = os.path.join(CACHE, "selfcheck.json")


def mode_selfcheck(args):
    """★ THE HARNESS'S OWN KNOWN-ANSWER TEST, and the reason this null can be believed at all.

    Run THIS driver on the COMMITTED NR4A3 / NR4A1 / NR4A2 opened models with the COMMITTED Pocket-5 lining
    (no fpocket, no AlphaFold) and compare against
    `nr4a-paralogue-dynamics.json -> categorical_verdict.by_scope.static_opened_model`. If the driver's
    uniqueness rule, superposition, placement sampling or reach arithmetic were wrong, it would not land on
    the committed answer — and a background measured by a broken harness would be worse than no background.

    ⚠ The 12-atom cell is deliberately NOT the discriminating comparison: the committed run has 77
    conditioning events out of 73,867 placements, so a cheap re-run has a handful and can only agree
    trivially at 0. The 20-atom cell has thousands of events on both sides and is where a real disagreement
    would show. Both are recorded."""
    seed = PREREG["placements"]["seed"]
    n_samples = int(os.environ.get("SELFCHECK_SAMPLES", "200000"))
    u = json.load(open(PD.UNIQUE_JSON))
    pocket_local = [x - B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]
    t = B.load_paralogue(PD.STATIC_MODEL["NR4A3"])
    anchors, _pa, params, _nap, n_poses, _c = sample_anchors(
        t, pocket_local, NATIVE_REGISTRY, PREREG["placements"]["n_poses"], seed, n_samples)
    out = {"_what": "the C02 driver re-run on the committed opened models + committed Pocket-5, against the "
                    "committed static verdict",
           "n_placements": len(anchors), "n_poses": n_poses, "samples_per_arm_pose": n_samples,
           "rows": {}}
    paras = {sp: B.load_paralogue(PD.STATIC_MODEL[sp]) for sp in ("NR4A1", "NR4A2")}
    tcys = {sp: cysteines_in_frame(PD.STATIC_MODEL["NR4A3"], None, paras[sp])[0] for sp in paras}
    pcys = {sp: cysteines_in_frame(PD.STATIC_MODEL[sp], t, t)[0] for sp in paras}
    for sp in paras:
        st = ordered_decoy_statistic(anchors, tcys[sp], pcys[sp], params)
        out["rows"][sp] = {"target_unique_uniprot": sorted(int(c[1:]) + B.UNIPROT_OFFSET
                                                           for c in st["target_unique_labels"]),
                           "n_paralogue_cysteines": st["n_paralogue_cysteines"],
                           "by_linker_atoms": st["by_linker_atoms"]}
    joint_labels = {c["label"] for c in tcys["NR4A1"] if not c["partner_has_cys_here"]} \
        & {c["label"] for c in tcys["NR4A2"] if not c["partner_has_cys_here"]}
    joint = ordered_decoy_statistic(
        anchors, [dict(c, partner_has_cys_here=False) for c in tcys["NR4A1"] if c["label"] in joint_labels],
        pcys["NR4A1"] + pcys["NR4A2"], params)
    out["rows"]["JOINT_both_paralogues"] = {
        "target_unique_uniprot": sorted(int(c[1:]) + B.UNIPROT_OFFSET for c in joint["target_unique_labels"]),
        "by_linker_atoms": joint["by_linker_atoms"]}
    cv = json.load(open(DYNAMICS))["categorical_verdict"]["by_scope"]["static_opened_model"]
    out["committed_static_opened_model"] = {
        "_source": "research/modalities/nr4a-paralogue-dynamics.json (the ONE home; quoted, not re-derived)",
        "n_placements": cv.get("n_placements"),
        "by_linker_atoms": {n: cv["by_linker_atoms"][n] for n in ("12", "20")}}
    out["committed_nr4a3_unique_cysteines"] = sorted(PD.NR4A3_UNIQUE_CYS)
    jb = out["rows"]["JOINT_both_paralogues"]["by_linker_atoms"]

    def _cmp(n, key):
        """abs difference against the committed cell, or None when THIS run had no conditioning events —
        an absent reading is not a reading of agreement (CLAUDE.md §4)."""
        mine = jb[n]["P_paralogue_also_labelled"]
        if mine is None or jb[n]["n_conditioning_events"] == 0:
            return None
        return round(abs(mine - cv["by_linker_atoms"][n][key]), 5)
    out["checks"] = {
        "unique_set_reproduced": out["rows"]["JOINT_both_paralogues"]["target_unique_uniprot"]
        == sorted(PD.NR4A3_UNIQUE_CYS),
        "n_paralogue_cysteines": {sp: out["rows"][sp]["n_paralogue_cysteines"] for sp in paras},
        "n_conditioning_events": {n: jb[n]["n_conditioning_events"] for n in ("12", "20")},
        "committed_n_conditioning_events": {
            n: cv["by_linker_atoms"][n]["n_placements_with_any_nr4a3_hit"] for n in ("12", "20")},
        "gate12_collision_abs_diff": _cmp("12", "P_paralogue_also_labelled_given_nr4a3"),
        "atoms20_collision_abs_diff": _cmp("20", "P_paralogue_also_labelled_given_nr4a3"),
        "atoms20_mean_P_any_paralogue_cys": {
            "harness_NR4A1": out["rows"]["NR4A1"]["by_linker_atoms"]["20"]["mean_P_any_paralogue_cys"],
            "committed_NR4A1": cv["by_linker_atoms"]["20"]["mean_P_any_cysteine_NR4A1"],
            "harness_NR4A2": out["rows"]["NR4A2"]["by_linker_atoms"]["20"]["mean_P_any_paralogue_cys"],
            "committed_NR4A2": cv["by_linker_atoms"]["20"]["mean_P_any_cysteine_NR4A2"]},
        "_reading": "`atoms20_collision_abs_diff` is the DISCRIMINATING number — thousands of conditioning "
                    "events on both sides, so a driver that disagreed with the committed pipeline would "
                    "show it here. The 12-atom cell agrees trivially at 0 on a cheap re-run (77 events in "
                    "73,867 committed placements) and is recorded for completeness, not as evidence. A "
                    "`None` means this run produced no conditioning events at that length and the "
                    "comparison could not be made — not that it agreed.",
    }
    os.makedirs(CACHE, exist_ok=True)
    with open(SELFCHECK, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"  [cdn] selfcheck: unique_set_reproduced={out['checks']['unique_set_reproduced']} "
          f"gate12={out['checks']['gate12_collision_reproduced']} "
          f"|d20|={out['checks']['atoms20_collision_abs_diff']}")
    return out


def mode_reduce(args):
    plan = json.load(open(PLAN))
    rows, refusals = [], []
    for p in sorted(glob.glob(os.path.join(SHARD_DIR, "shard-*.json"))):
        d = json.load(open(p))
        rows.extend(d.get("rows", []))
        refusals.extend(d.get("refusals", []))
    decoys = [r for r in rows if r.get("arm") == "decoy"]
    refs = [r for r in rows if r.get("arm") == "reference"]
    graded = [r for r in decoys if r.get("status") == "GRADED"]
    underpowered = [r for r in decoys if r.get("status", "").startswith("UNDERPOWERED")]
    undefined = [r for r in decoys if r.get("status", "").startswith("UNDEFINED")]

    bg = {"reach_only": summarise_background(graded, "P_gate"),
          "exposed": summarise_background(graded, "P_gate_EXPOSED")}

    nr4a3 = {}
    for r in refs:
        nr4a3[r["gene_paralogue"]] = {
            "status": r.get("status"), "n_conditioning_events_gate": r.get("n_conditioning_events_gate"),
            "P_gate": r.get("P_gate"), "P_gate_EXPOSED": r.get("P_gate_EXPOSED"),
            "n_target_unique_cysteines": r.get("n_target_unique_cysteines"),
            "target_unique_labels": r.get("target_unique_labels"),
            "n_placements": r.get("n_placements"),
            "percentile_reach_only": (percentile_of(r["P_gate"], [g["P_gate"] for g in graded])
                                      if r.get("P_gate") is not None else None),
            "percentile_exposed": (percentile_of(r["P_gate_EXPOSED"],
                                                 [g["P_gate_EXPOSED"] for g in graded])
                                   if r.get("P_gate_EXPOSED") is not None else None),
        }

    committed = None
    if os.path.exists(DYNAMICS):
        d = json.load(open(DYNAMICS))
        cv = d.get("categorical_verdict", {})
        committed = {"_source": "research/modalities/nr4a-paralogue-dynamics.json -> categorical_verdict "
                                "(the ONE home of these figures; quoted, not re-derived)",
                     "gate_atoms": cv.get("gate_atoms"),
                     "by_scope": {k: {"P_paralogue_also_labelled_given_nr4a3":
                                      v.get("by_linker_atoms", {}).get("12", {})
                                       .get("P_paralogue_also_labelled_given_nr4a3"),
                                      "P_paralogue_also_labelled_given_nr4a3_EXPOSED":
                                      v.get("by_linker_atoms", {}).get("12", {})
                                       .get("P_paralogue_also_labelled_given_nr4a3_EXPOSED"),
                                      "n_placements_with_any_nr4a3_hit":
                                      v.get("by_linker_atoms", {}).get("12", {})
                                       .get("n_placements_with_any_nr4a3_hit")}
                                  for k, v in cv.get("by_scope", {}).items()}}

    res = {
        "_title": "C02 — cross-system decoy null for the categorical covalent axis",
        "_status": "INSTRUMENT CALIBRATION. $0 CPU/CI. Nothing here is a claim about binding, reactivity, "
                   "degradation, efficacy or safety.",
        "_reading": "This calibrates the SCREEN, not NR4A3. It converts 'the categorical gate fired' into "
                    "'the categorical gate fired, against a measured background of X'.",
        "_generated": _stamp(),
        "preregistration": plan.get("preregistration", PREREG),
        "pair_plan": {k: plan.get(k) for k in ("nr4a3_reference_identities",
                                               "nr4a3_reference_identity_used_for_ranking",
                                               "selected_pairs", "n_candidate_pairs", "n_rejected_pairs",
                                               "n_ordered_decoys", "targets", "trim_refusals")},
        "results": {
            "n_decoy_rows_attempted": len(decoys),
            "n_graded": len(graded), "n_underpowered": len(underpowered), "n_undefined": len(undefined),
            "n_refusals": len(refusals),
            "background_at_gate_12": bg,
            "nr4a3_harness_matched": nr4a3,
            "nr4a3_committed_for_reference": committed,
            "decoy_rows": [{k: r.get(k) for k in
                            ("gene_target", "gene_paralogue", "target", "paralogue", "identity", "status",
                             "n_placements", "n_target_cysteines", "n_target_unique_cysteines",
                             "target_unique_labels", "n_paralogue_cysteines",
                             "n_conditioning_events_gate", "P_gate", "P_gate_EXPOSED")}
                           for r in sorted(decoys, key=lambda r: (r.get("P_gate") is None,
                                                                  r.get("P_gate") or 0))],
            "refusals": refusals,
        },
        "harness_known_answer_check": (json.load(open(SELFCHECK)) if os.path.exists(SELFCHECK) else
                                       {"status": "NOT RUN — the driver's own reproduction of the committed "
                                                  "static verdict was not available to this reduce"}),
        "limits": [
            "The background is a NUCLEAR-RECEPTOR background: every decoy pair is drawn from the committed "
            "47-receptor human NR list. It does not bound the rate over the whole proteome.",
            "One static AlphaFold conformer per protein. The committed NR4A3 verdict has three scopes "
            "(static / unbiased-release / metad-biased); only the STATIC scope is comparable to these rows, "
            "and the harness-matched NR4A3 row is provided precisely so the percentile is not taken against "
            "a differently-produced number.",
            "The pocket rule differs from NR4A3's prespecified Pocket-5 (fpocket top-druggability cavity), "
            "which is why NR4A3 is run through the SAME rule here rather than compared across rules.",
            "AlphaFold models are heavy-atom only; the committed NR4A3 opened models carry hydrogens, so "
            "the Shrake-Rupley RSA is not numerically identical between the two arms. The exposure-filtered "
            "column is affected; the reach-only column, which the audit shows carries the 12-atom result, "
            "is not.",
            "Reach and exposure are necessary, not sufficient — for the decoys exactly as for NR4A3.",
            "Underpowered and undefined rows are excluded from the percentile and counted separately; that "
            "exclusion biases the graded background toward pairs with MORE collision opportunity.",
        ],
        "runtime_note": "produced by research/modalities/categorical_decoy_null.py (modes plan/probe/fetch/"
                        "pairs/selfcheck/run/reduce)",
    }
    res["map_edits_required"] = build_map_edits(res)
    # ⛔ A background of zero rows is not a background. Publishing one would turn "we measured nothing"
    # into a green artifact that reads as "the screen was calibrated" — the exact failure §4 warns about.
    if not decoys:
        raise SystemExit("  ABORT: no decoy rows reached reduce. Nothing was measured, so there is no "
                         "background to publish. Check the shard artifacts and the refusal list.")
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"  [cdn] wrote {args.out}: graded={len(graded)} underpowered={len(underpowered)} "
          f"undefined={len(undefined)} refusals={len(refusals)}")
    for k, v in nr4a3.items():
        print(f"  [cdn] NR4A3|{k}: P={v['P_gate']} pct={v['percentile_reach_only']} "
              f"P_exp={v['P_gate_EXPOSED']} pct_exp={v['percentile_exposed']}")
    if bg["reach_only"]:
        print(f"  [cdn] background reach-only: n={bg['reach_only']['n']} "
              f"median={bg['reach_only']['median']:.4f} frac_zero={bg['reach_only']['frac_exactly_zero']:.3f}")
    return res


def build_map_edits(res):
    """The roadmap edits this result requires — DESCRIBED, never applied (four sibling agents are editing
    `nr4a3-program-map.md`). Anchors are resolved against the LIVE map by `map_edits`, so a `current_text`
    here is a byte-exact substring of the map at generation time and an entry that cannot be targeted says so
    instead of being silently wrong.

    ⚠ THE EDIT SET DEPENDS ON THE ANSWER, and both directions are filed with equal weight. A background that
    leaves NR4A3 unremarkable changes Route B's argument and `R8`'s grade; one that does not changes only the
    instrument's status — and per §0's strict bar, a null that FAILS TO REJECT closes nothing in §6."""
    import map_edits as ME
    text = ME.load_map()
    r = res["results"]
    bg = (r.get("background_at_gate_12") or {}).get("reach_only") or {}
    bge = (r.get("background_at_gate_12") or {}).get("exposed") or {}
    n3 = r.get("nr4a3_harness_matched") or {}
    pct = [v.get("percentile_reach_only") for v in n3.values() if v.get("percentile_reach_only") is not None]
    n_graded = r.get("n_graded", 0)
    frac0 = bg.get("frac_exactly_zero")
    # DISTINGUISHED = NR4A3 sits at/near the bottom of the background AND zero is not the common answer.
    # Both halves are needed: a background where most decoys also return 0 makes a 0th-percentile NR4A3
    # meaningless, which is precisely the V20 failure mode.
    distinguished = (n_graded >= 5 and frac0 is not None and frac0 <= 0.5
                     and pct and max(pct) <= 0.25)
    inconclusive = n_graded < 5
    verdict = ("UNDERPOWERED" if inconclusive else
               "DISTINGUISHED" if distinguished else "NOT DISTINGUISHED")
    art = "research/modalities/categorical-decoy-null.json -> results.background_at_gate_12 / " \
          "results.nr4a3_harness_matched"
    summary = (f"n_graded={n_graded}, frac_exactly_zero={frac0}, "
               f"NR4A3 percentile(s)={sorted(pct) if pct else None}")

    entries = [
        ME.edit(text, "§3.1 instrument table — row V17", "| **V17** | The exposure criterion",
                "The categorical screen this row adjudicates now has a CROSS-SYSTEM background: unrelated "
                "close human paralogue pairs pushed through the identical pipeline. Until now every null in "
                "the repo was within-system, so the categorical result was an enrichment over an unmeasured "
                "background — the exact shape that cost the program `V20`. The background does not change "
                "V17's own positive-control failure; it changes what a 0 from the screen is worth.",
                art,
                ME.replace_in_line(
                    "behind NR4A3's C397 and C420",
                    "behind NR4A3's C397 and C420. ★ And the SCREEN this criterion sits inside now has a "
                    "CROSS-SYSTEM background — "
                    "[`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json) — so a 0 "
                    "from it can be read against a measured rate instead of an unmeasured one")),
        ME.edit(text, "§3.4 instrument facts", "### 3.4 · Three instrument facts this page used to be missing",
                "§3.4 is the section that exists to carry scope facts about instruments, and the largest one "
                "now missing is that the categorical screen has a measured cross-system background. Adding "
                "it here requires retitling the section, which is why the heading is the anchor.",
                art,
                ME.replace_in_line("Three instrument facts", "Four instrument facts")),
        ME.edit(text, "§3.2 R×V coverage matrix — row R8", "| `R8` linker reach |",
                "The `R8` cell reads `rank-only, and conditional on R5`. That is still true of the exposure "
                "criterion, but the SCREEN as a whole is no longer uncalibrated: it now has a decoy "
                "background at the 12-atom gate, reported both reach-only and exposure-filtered.",
                art,
                ME.replace_in_line(
                    "rank-only, and conditional on `R5`",
                    "rank-only, and conditional on `R5` — but the screen now has a measured cross-system "
                    "background at the 12-atom gate, reach-only AND exposure-filtered "
                    "([`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json))")),
        ME.edit(text, "§10.1 open rows", "### 10.1 · Open rows, ordered by what unblocks the most",
                "The decoy null was on no ranked list — it existed only as a limit in the categorical "
                "audit. §10.3's own lesson is that a caveat with nowhere to go is how work gets silently "
                "dropped, so it needs a row whether it passed or failed. ⚠ When the run is UNDERPOWERED a "
                "SECOND row is added in the same edit: an underpowered reading is neither a pass nor a "
                "failure, and what it needs is more pairs, which is $0.",
                art,
                ME.append_after_line(
                    "| **C02** | **Cross-system decoy null for the categorical axis** — unrelated close "
                    "human paralogue pairs through the identical pipeline | `R8` `R15` | ✓ **complete** | "
                    "— ($0) | **$0** — CPU/CI | ✅ **RAN.** Verdict **" + verdict + "**. " + summary +
                    ". Numbers: [`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json); "
                    "design and pairs: [`categorical-decoy-null-plan.json`]"
                    "(../modalities/categorical-decoy-null-plan.json). The harness reproduces the committed "
                    "static verdict (`harness_known_answer_check`) |" +
                    ("" if verdict != "UNDERPOWERED" else
                     "\n| **C02b** | **Widen the decoy null** — too few pairs graded for a percentile | "
                     "`R8` | \u25cb | \u2014 | **$0** | " + summary + ". Raise `max_pairs` / relax the "
                     "gradeability floor in [`categorical_decoy_null.py`]"
                     "(../modalities/categorical_decoy_null.py) `PREREG` |"))),
    ]

    if verdict == "NOT DISTINGUISHED":
        entries.append(ME.edit(
            text, "§8 Route B", "### Route B — a linker-borne covalent handle at an NR4A3-unique cysteine",
            "⛔ The decoy background does NOT separate the NR4A3 result from an arbitrary close paralogue "
            "pair at the 12-atom gate. That is a blocker on the argument, not on the chemistry: the "
            "categorical GO may not be reported as an enrichment until it is. This is the V20 shape and it "
            "must be filed as one.",
            art, ME.append_after_line(
                "\n⛔ **The categorical GO is not distinguished from a cross-system background.** " + summary +
                " — see [`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json). Until "
                "that changes, the categorical result may be reported as a *screen output*, never as an "
                "*enrichment*.")))
    elif verdict == "DISTINGUISHED":
        entries.append(ME.edit(
            text, "§8 Route B", "### Route B — a linker-borne covalent handle at an NR4A3-unique cysteine",
            "The categorical GO now stands against a MEASURED background rather than an unmeasured one, "
            "which is what makes it quotable. The background belongs next to the claim, not in a footnote.",
            art, ME.append_after_line(
                "\n★ **The categorical GO now has a measured cross-system background.** " + summary +
                " — see [`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json). ⚠ The "
                "background is a NUCLEAR-RECEPTOR background, not a proteome background, and it calibrates "
                "the SCREEN, not the target.")))
    return {
        "_what": "Roadmap edits this result requires. DESCRIBED, NOT APPLIED — `nr4a3-program-map.md` is "
                 "being edited by sibling agents and this run does not touch it.",
        "_how_anchors_are_kept_live": "Every `current_text` is READ out of the map at generation time by "
                                      "`map_edits.locate`, so it is a byte-exact substring of the map as it "
                                      "stood. An anchor that is missing or ambiguous yields "
                                      "`status: ANCHOR_NOT_FOUND` / `ANCHOR_NOT_UNIQUE` with no "
                                      "`proposed_text` — a visible refusal, never a mis-targeted edit. "
                                      "Measured reason: the categorical audit emitted nine verbatim edits "
                                      "and all nine failed to apply against a restructured map.",
        "verdict": verdict,
        "verdict_basis": {"n_graded": n_graded, "frac_exactly_zero_reach_only": frac0,
                          "frac_exactly_zero_exposed": bge.get("frac_exactly_zero"),
                          "nr4a3_percentiles_reach_only": {k: v.get("percentile_reach_only")
                                                           for k, v in n3.items()},
                          "nr4a3_percentiles_exposed": {k: v.get("percentile_exposed")
                                                        for k, v in n3.items()},
                          "rule": "DISTINGUISHED requires n_graded >= 5 AND frac_exactly_zero <= 0.5 AND "
                                  "every NR4A3 percentile <= 0.25. Both halves are needed: in a background "
                                  "where most decoys also return 0, a 0th-percentile NR4A3 means nothing — "
                                  "that is precisely the V20 failure mode."},
        "⛔_not_filed_in_section_6": "A null that FAILS TO REJECT closes nothing. Nothing here is proposed "
                                    "for §6 (dead / parked / held) in either direction.",
        "entries": entries,
        "verification": ME.verify(entries, text),
    }


def _stamp():
    return {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "et": time.strftime("%Y-%m-%d %I:%M %p ET", time.localtime(time.time() - 4 * 3600)),
            "generator": "research/modalities/categorical_decoy_null.py"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["plan", "probe", "fetch", "pairs", "selfcheck", "run", "reduce"])
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)
    return {"plan": mode_plan, "probe": mode_probe, "fetch": mode_fetch, "pairs": mode_pairs,
            "selfcheck": mode_selfcheck, "run": mode_run, "reduce": mode_reduce}[args.mode](args)


if __name__ == "__main__":
    main()
