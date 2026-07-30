#!/usr/bin/env python3
"""Which paralogue pairs could carry an S-CALIBRATOR — screened on whether a REAL structure exists on BOTH arms.

★ WHY THIS EXISTS. STRATEGY Open decision 9 (2026-07-30) concluded that `S` — the flagship kill-switch — has
never had a known-answer calibrator, and that the binding constraint on choosing one is **which arm is REAL**,
not what is already staged. The reason is specific: valB_mini's miss is an ENDPOINT-STATE error, and a
known-answer accuracy test does NOT telescope such an error the way a cycle does. On SMARCA2-vs-SMARCA4 as the
repo currently stages it, 8G1Q is a *SMARCA4* structure with the BD sequence substituted to SMARCA2 and
relaxed — so a homology-model error would sit on ONE arm and not cancel, and a failure could not be told apart
from "the S-class quantity does not work." A pair with a solved structure on both arms removes that ambiguity
outright.

★ WHAT THIS SCREENS, AND WHAT IT DELIBERATELY DOES NOT. It answers the STRUCTURAL half, entirely from fetched
RCSB data: for each candidate paralogue pair, does a deposited structure exist for each arm, and is any of them
a TERNARY complex (target + an E3 component)? That is the half that is decidable without a literature claim.

⛔ IT DOES NOT SUPPLY SELECTIVITY MAGNITUDES, AND MUST NOT BE READ AS DOING SO. A calibrator needs a measured,
primary-source selectivity value, and STRATEGY Open decision 7 now binds it: the accuracy band may not be wider
than the signal being calibrated, and the null-rejection rate must be stated up front. No such number is typed
here from memory — every candidate is emitted with `selectivity_kcal: null` and
`needs_primary_source_verification: true`, and the repo's medical-integrity rule means it stays that way until
a primary source is read and cited. A pair that passes the structural screen is a CANDIDATE, not a choice.

★ NO PDB ID IS TYPED. Every accession in the output is returned by the RCSB search API against a GENE NAME, so
the survey cannot invent a structure that does not exist. The candidate list carries only gene-name pairs —
statements about which proteins are paralogues, which is not a claim this file needs to source from the network.

Pure stdlib. Network: RCSB only (search.rcsb.org + data.rcsb.org). The dev sandbox's egress proxy refuses
both, so this runs in CI (CLAUDE.md §6).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "s-calibrator-survey.json")

SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
DATA = "https://data.rcsb.org/rest/v1/core/entry/"

# E3/CRL components whose presence in an entry makes it a TERNARY (or at least E3-bound) structure rather than
# a bare target complex. Gene names, matched against the entry's own polymer-entity gene names.
E3_MARKERS = {"VHL", "CRBN", "DDB1", "ELOB", "ELOC", "TCEB1", "TCEB2", "CUL2", "CUL4A", "RBX1",
              "BIRC2", "DCAF1", "DCAF15", "DCAF16", "KEAP1", "FEM1B", "RNF114", "MDM2"}

# ---------------------------------------------------------------------------------------------------------
# CANDIDATES -- paralogue pairs for which a selective degrader or ligand is reported in the literature.
# Gene names only. The claim being made here is ONLY that these are paralogues and that selectivity has been
# reported for the pair; the magnitude is left to primary-source verification, and the structures are fetched.
# ---------------------------------------------------------------------------------------------------------
CANDIDATES = [
    {"pair": ("SMARCA2", "SMARCA4"), "why": "the repo's incumbent; VHL PROTACs with reported SMARCA2 preference"},
    {"pair": ("BRD4", "BRD2"), "why": "BET family; VHL PROTACs with reported intra-family preference"},
    {"pair": ("BRD4", "BRD3"), "why": "BET family, second pairing"},
    {"pair": ("CDK4", "CDK6"), "why": "close kinase paralogues with reported selective degraders"},
    {"pair": ("IKZF1", "IKZF3"), "why": "CRBN molecular-glue neosubstrates with reported differential degradation"},
    {"pair": ("MAPK14", "MAPK11"), "why": "p38 alpha vs beta; selective degraders reported"},
    {"pair": ("FKBP12", "FKBP51"), "why": "FKBP family; selective ligands reported"},
    {"pair": ("WEE1", "PKMYT1"), "why": "related kinases with selective chemistry reported"},
    {"pair": ("CDK9", "CDK7"), "why": "transcriptional CDKs with reported selective degraders"},
    {"pair": ("HDAC1", "HDAC2"), "why": "class-I HDAC paralogues, reported selective chemistry"},
]


def _post(url, payload, timeout=60, retries=3):
    """POST to RCSB and return parsed JSON, or `None` for an explicit NO-HITS.

    ★ 204 IS A SUCCESS STATUS, WHICH IS EXACTLY WHY IT BIT. RCSB answers a zero-hit query with **204 No
    Content** and an EMPTY BODY. urllib classes 2xx as success, so no HTTPError is ever raised and the `except
    HTTPError ... if e.code == 204` guard written for it can never fire; `json.load` then dies on the empty
    body with `Expecting value: line 1 column 1`. The plain per-gene queries never hit it because every gene
    surveyed has structures -- it only surfaced once the AND-queries started asking genuinely empty questions
    like SMARCA2 AND MDM2. So no-hits is handled HERE, at the transport, where both call sites inherit it.

    Two further hardenings, added together because each RCSB round trip costs a CI run (the dev sandbox's proxy
    refuses RCSB, so none of this is testable locally and iterating one bug at a time is the expensive way):
      * an HTTP error carries the SERVER'S OWN message, since a bare `400 Bad Request` names nothing;
      * transient 5xx / socket errors are retried, so a flaky minute does not read as a schema problem."""
    body = json.dumps(payload).encode()
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as fh:
                if fh.status == 204:
                    return None                      # explicit no-hits, not an error
                raw = fh.read().decode().strip()
                if not raw:
                    return None                      # empty body is the same statement
                try:
                    return json.loads(raw)
                except ValueError:
                    raise RuntimeError("RCSB returned non-JSON (%d): %s" % (fh.status, raw[:300])) from None
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                last = e
                time.sleep(2 ** attempt)
                continue
            try:
                msg = e.read().decode()[:600]
            except Exception:
                msg = "<no body>"
            raise RuntimeError("RCSB HTTP %d on %s :: %s" % (e.code, url, msg)) from None
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                last = e
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("RCSB unreachable after %d attempts: %s" % (retries, last))


def _get(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as fh:
        return json.load(fh)


# Candidate attribute paths for "gene name", most-likely first. RCSB has moved this field between schema
# sections, and the first CI attempt was rejected with a bare 400 — so rather than guess once per run, the
# survey TRIES each and records which one the server actually accepts. `_GENE_ATTR_USED` is that record.
GENE_ATTRS = [
    "rcsb_entity_source_organism.rcsb_gene_name.value",
    "rcsb_polymer_entity.rcsb_gene_name.value",
    "rcsb_gene_name.value",
]
_GENE_ATTR_USED = {"attribute": None, "errors": {}}


def _gene_query(attr, gene, limit):
    return {
        "query": {"type": "terminal", "service": "text",
                  "parameters": {"attribute": attr, "operator": "exact_match", "value": gene}},
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": limit},
                            "results_content_type": ["experimental"]},
    }


def search_by_gene(gene, limit=50):
    """PDB entry IDs carrying this gene name. IDs come from RCSB, never from memory.

    Once one attribute path is known to work it is reused for every later call, so the probing costs at most
    one extra request for the whole survey rather than one per gene."""
    attrs = [_GENE_ATTR_USED["attribute"]] if _GENE_ATTR_USED["attribute"] else GENE_ATTRS
    last = None
    for attr in attrs:
        try:
            r = _post(SEARCH, _gene_query(attr, gene, limit))
        except RuntimeError as e:              # a rejected ATTRIBUTE; a zero-hit query returns None, not this
            _GENE_ATTR_USED["errors"][attr] = str(e)[:200]
            last = e
            continue
        _GENE_ATTR_USED["attribute"] = attr
        return [] if r is None else [h["identifier"] for h in r.get("result_set", [])]
    raise RuntimeError("no RCSB gene-name attribute was accepted; server replies: %s (last: %s)"
                       % (_GENE_ATTR_USED["errors"], last))


def search_gene_and_e3(gene, e3, limit=25):
    """Entries containing BOTH this gene AND this E3 component -- the JOIN done by RCSB, not by us.

    ★ THIS REPLACES A PER-ENTRY GENE FETCH THAT SILENTLY RETURNED NOTHING. The first working run reported
    `n_ternary = 0` for all ten pairs, which is not a finding: BRD4-VHL and SMARCA2-VHL ternary structures are
    well known to exist. The cause was that the per-entry reader looked for gene names under
    `polymer_entity.rcsb_gene_name`, while RCSB keeps them under `rcsb_entity_source_organism.rcsb_gene_name`
    -- the very path the search probe had just proved. Every entry therefore came back with an empty gene set
    and every intersection with E3_MARKERS was empty. Asking the SERVER for the conjunction removes the whole
    class of error: no local join to get wrong, no schema path to guess."""
    attr = _GENE_ATTR_USED["attribute"] or GENE_ATTRS[0]
    q = {
        "query": {"type": "group", "logical_operator": "and", "nodes": [
            {"type": "terminal", "service": "text",
             "parameters": {"attribute": attr, "operator": "exact_match", "value": gene}},
            {"type": "terminal", "service": "text",
             "parameters": {"attribute": attr, "operator": "exact_match", "value": e3}},
        ]},
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": limit},
                            "results_content_type": ["experimental"]},
    }
    r = _post(SEARCH, q)
    return [] if r is None else [h["identifier"] for h in r.get("result_set", [])]


def screen_arm(gene):
    """One paralogue arm: total deposited structures, and which E3 components co-occur with it."""
    ids = search_by_gene(gene)
    hits, by_e3 = [], {}
    for e3 in sorted(E3_MARKERS):
        found = search_gene_and_e3(gene, e3)
        if found:
            by_e3[e3] = found[:6]
            hits.extend(found)
    uniq = sorted(set(hits))
    return {"gene": gene, "n_structures": len(ids), "n_ternary": len(uniq),
            "ternary_pdb_ids": uniq[:10], "e3_partners_found": sorted(by_e3),
            "ternary_by_e3": by_e3,
            "_n_structures_is_a_floor_if_truncated": len(ids) >= 50}


def survey(candidates=None):
    rows = []
    for c in (candidates or CANDIDATES):
        a, b = c["pair"]
        arm_a, arm_b = screen_arm(a), screen_arm(b)
        both_real = arm_a["n_ternary"] > 0 and arm_b["n_ternary"] > 0
        rows.append({
            "pair": [a, b],
            "why_a_candidate": c["why"],
            "arm_a": arm_a,
            "arm_b": arm_b,
            "ternary_structure_on_BOTH_arms": both_real,
            "verdict": ("SYMMETRIC — a solved ternary exists on both arms, so neither arm needs a homology "
                        "substitution and a model error cannot sit on one side only"
                        if both_real else
                        "ASYMMETRIC or ABSENT — at least one arm has no deposited ternary, so that arm would "
                        "have to be modelled and a model error would NOT cancel"),
            "selectivity_kcal": None,
            "needs_primary_source_verification": True,
            "_selectivity_note": ("NOT SUPPLIED BY THIS SURVEY. A calibrator needs a measured, primary-source "
                                 "selectivity value, and STRATEGY Open decision 7 binds it: the accuracy band "
                                 "may not be wider than the signal, and the null-rejection rate must be stated "
                                 "up front. Passing the structural screen makes a pair a CANDIDATE, not a "
                                 "choice."),
        })
    rows.sort(key=lambda r: (not r["ternary_structure_on_BOTH_arms"],
                             -(r["arm_a"]["n_ternary"] + r["arm_b"]["n_ternary"])))
    return {
        "_what": ("structural screen for an S-calibrator: which paralogue pairs have a deposited TERNARY "
                  "structure on BOTH arms, so that a homology-model error cannot sit on one arm only"),
        "_why": ("STRATEGY Open decision 9 — the system must be chosen on WHICH ARM IS REAL, not on what is "
                 "already staged, because a known-answer accuracy test does not telescope an endpoint-state "
                 "error the way a cycle does"),
        "_no_pdb_id_is_typed": "every accession is returned by the RCSB search API against a gene name",
        "_does_not_supply_selectivity": True,
        "_binding_constraint_from_decision_7": ("no accuracy band wider than the signal being calibrated; "
                                                "state the null-rejection rate up front"),
        "rcsb_gene_attribute_accepted": _GENE_ATTR_USED["attribute"],
        "rcsb_gene_attributes_rejected": _GENE_ATTR_USED["errors"],
        "e3_markers_used": sorted(E3_MARKERS),
        "candidates": rows,
        "n_symmetric": sum(1 for r in rows if r["ternary_structure_on_BOTH_arms"]),
        "detector_sanity": _detector_sanity(rows),
    }


def _detector_sanity(rows):
    """★ AN ALL-ZERO SCREEN IS A BROKEN DETECTOR UNTIL PROVEN OTHERWISE, AND THIS FILE HAS ALREADY BEEN WRONG
    THAT WAY ONCE. The first working run returned n_ternary = 0 for all ten pairs, and that was a schema-path
    bug rather than a fact about the PDB. Reporting it would have said "no paralogue pair has a ternary
    structure" -- false, and it would have killed the S-calibrator route on an artifact. So the survey grades
    ITSELF: if not one arm anywhere finds an E3 partner, the run is REFUSED rather than reported."""
    total = sum(r["arm_a"]["n_ternary"] + r["arm_b"]["n_ternary"] for r in rows)
    partners = sorted({e for r in rows for arm in ("arm_a", "arm_b") for e in r[arm]["e3_partners_found"]})
    ok = total > 0
    return {
        "total_ternary_entries_found": total,
        "distinct_e3_partners_seen": partners,
        "detector_credible": ok,
        "verdict": ("PASS -- at least one arm found an E3 partner, so the detector is doing something"
                    if ok else
                    "REFUSED -- zero E3 partners across every arm of every pair. Far more likely a broken "
                    "detector than a fact about the PDB (BRD4-VHL and SMARCA2-VHL ternary structures are "
                    "known to exist). DO NOT read this run as evidence against the S-calibrator route."),
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    rep = survey()
    if "--write" in argv:
        with open(OUT, "w") as fh:
            json.dump(rep, fh, indent=1)
            fh.write("\n")
        print("wrote %s" % OUT)
    print("[S-CALIBRATOR SURVEY] %d of %d candidate pairs have a ternary structure on BOTH arms"
          % (rep["n_symmetric"], len(rep["candidates"])))
    for r in rep["candidates"]:
        print("  %-18s both_arms=%-5s  A: %d struct/%d ternary   B: %d struct/%d ternary"
              % ("/".join(r["pair"]), r["ternary_structure_on_BOTH_arms"],
                 r["arm_a"]["n_structures"], r["arm_a"]["n_ternary"],
                 r["arm_b"]["n_structures"], r["arm_b"]["n_ternary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
