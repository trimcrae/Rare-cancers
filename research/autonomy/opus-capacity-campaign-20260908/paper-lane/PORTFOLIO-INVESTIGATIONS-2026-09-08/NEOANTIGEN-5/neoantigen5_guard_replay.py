#!/usr/bin/env python3
"""NEOANTIGEN-5 — independent confirmation of the PARENTS accession defect in
`research/modalities/junction_proteome_novelty.py`, and a before/after equivalence replay of
NEOANTIGEN-4's UNAPPLIED diff on the CURRENTLY COMMITTED inputs.

Read-only. No network (routes B1/B2 closed — no proteome or isoform sequence is fetched; the
committed artifact's recorded hits are replayed, never re-derived). Nothing is applied.

What is replayed, and why that is the whole of the change's effect: `PARENTS` is referenced in
exactly ONE place in the audited module — the loop that builds `parent_hits` from the accessions
already recorded in each peptide's `proteome_hits` — and `⛔_upstream_filter_check.verdict` is a
function of `parent_hits` alone. Peptide hit/miss classification, `n_found_in_proteome`,
`n_novel_proteome_wide` and `n_predicted_binders_found_in_proteome` are computed before `PARENTS`
is consulted and cannot depend on it. So replaying that loop over the committed
`junction-proteome-novelty.json` hit records, under the old map and the new one, reproduces the
patched-vs-unpatched verdicts exactly, for the inputs the published result was computed from.
"""
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
MOD = os.path.join(REPO, "research/modalities/junction_proteome_novelty.py")
TEST = os.path.join(REPO, "research/modalities/tests/test_junction_proteome_novelty.py")
NOVELTY = os.path.join(REPO, "research/modalities/junction-proteome-novelty.json")
SELFSIM = os.path.join(REPO, "research/modalities/junction-selfsimilarity.json")
OUT = os.path.join(os.path.dirname(__file__), "neoantigen5-guard-replay.json")

PARENTS_UNPATCHED = {"P56945": "EWSR1", "Q92570": "NR4A3"}
PARENTS_PATCHED = {"Q01844": "EWSR1", "P56945": "EWSR1", "Q92570": "NR4A3"}


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def confirm_accessions():
    """Step 1 — establish from the SOURCE which accession each artifact records."""
    src = read(MOD)
    m = re.search(r"^PARENTS\s*=\s*(\{.*\})\s*$", src, re.M)
    assert m, "PARENTS assignment not found — the defect claim cannot be checked as described"
    live = eval(m.group(1))  # noqa: S307 — a literal dict from this repository's own source
    assert live == PARENTS_UNPATCHED, f"committed PARENTS differs from the reported one: {live}"
    uses = [i + 1 for i, ln in enumerate(src.splitlines()) if "PARENTS" in ln]

    tsrc = read(TEST)
    fixture_accessions = re.findall(r">sp\|([A-Za-z0-9-]+)\|(\S+)", tsrc)

    ss = json.load(open(SELFSIM, encoding="utf-8"))
    ews_hits = {}
    def walk(o):
        if isinstance(o, dict):
            if "accession" in o and "EWS" in str(o.get("protein", "")):
                ews_hits[o["accession"]] = o.get("protein")
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(ss)

    return {
        "module_PARENTS_line": src.splitlines().index(m.group(0)) + 1,
        "module_PARENTS": live,
        "module_lines_referencing_PARENTS": uses,
        "test_fixture_records": [{"accession": a, "name": n} for a, n in fixture_accessions],
        "selfsimilarity_EWSR1_accessions": ews_hits,
        "other_modules_recording_EWSR1": sorted({
            os.path.relpath(os.path.join(dp, f), REPO)
            for dp, _, fs in os.walk(os.path.join(REPO, "research/modalities"))
            for f in fs if f.endswith((".py", ".json")) and "Q01844" in read(os.path.join(dp, f))
        }),
    }


def replay(parents, artifact):
    """The audited module's parent-hit loop, verbatim in behaviour, over recorded hits."""
    parent_hits = []
    found = artifact["peptides_found_in_proteome"]
    absent = artifact["peptides_novel_proteome_wide"]
    for rec in found:
        for h in rec["proteome_hits"]:
            acc = h["accession"]
            if acc.split("-")[0] in parents:
                parent_hits.append({"peptide": rec["peptide"], "accession": acc,
                                    "parent": parents[acc.split("-")[0]]})
    check = ({"parent_protein_hits": parent_hits,
              "verdict": "BROKEN — a parent-filtered peptide matched a parent protein"}
             if parent_hits else
             {"parent_protein_hits": [],
              "verdict": "consistent — no parent-filtered peptide hit a parent"})
    return {
        "n_peptides_tested": len(found) + len(absent),
        "n_found_in_proteome": len(found),
        "n_novel_proteome_wide": len(absent),
        "n_predicted_binders_found_in_proteome": sum(1 for r in found if r["predicted_binder"]),
        "upstream_filter_check": check,
    }


def main():
    art = json.load(open(NOVELTY, encoding="utf-8"))
    facts = confirm_accessions()
    before = replay(PARENTS_UNPATCHED, art)
    after = replay(PARENTS_PATCHED, art)

    # The committed artifact's own recorded verdict must be reproduced by the UNPATCHED replay,
    # otherwise the replay is not modelling the audited code path and proves nothing.
    committed = art["⛔_upstream_filter_check"]
    fidelity = (before["upstream_filter_check"] == committed
                and before["n_found_in_proteome"] == art["n_found_in_proteome"]
                and before["n_novel_proteome_wide"] == art["n_novel_proteome_wide"]
                and before["n_predicted_binders_found_in_proteome"]
                == art["n_predicted_binders_found_in_proteome"])

    identical = before == after
    ews_reachable = any(h["accession"].split("-")[0] == "Q01844"
                        for r in art["peptides_found_in_proteome"] for h in r["proteome_hits"])

    res = {
        "_what": ("NEOANTIGEN-5: source-level confirmation of the PARENTS accession defect and a "
                  "before/after equivalence replay of the UNAPPLIED NEOANTIGEN-4 diff on the "
                  "committed inputs."),
        "⛔_not_a_claim": ("Nothing here is an immunogenicity, presentation, efficacy, safety, "
                          "selectivity, therapeutic-window or clinical-readiness claim."),
        "_inputs": {"module": os.path.relpath(MOD, REPO), "test": os.path.relpath(TEST, REPO),
                    "artifact": os.path.relpath(NOVELTY, REPO),
                    "selfsimilarity": os.path.relpath(SELFSIM, REPO)},
        "step1_accession_facts": facts,
        "step1_defect_reproduces": facts["module_PARENTS"] == PARENTS_UNPATCHED
                                   and "Q01844" not in facts["module_PARENTS"]
                                   and any(a.startswith("Q01844")
                                           for a in facts["selfsimilarity_EWSR1_accessions"]),
        "step2_replay_fidelity_unpatched_reproduces_committed_verdict": fidelity,
        "step2_before_unpatched": before,
        "step2_after_patched": after,
        "step2_identical": identical,
        "step2_note": ("On the committed inputs no recorded proteome hit carries an EWSR1 "
                       "accession at all (Q01844 present among hits: %s), so the added key is "
                       "unreachable here and every count and verdict is unchanged. The change "
                       "therefore ADDS detection capability without altering any published "
                       "result." % ews_reachable),
        "step2_q01844_among_committed_hits": ews_reachable,
    }
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    print("STEP 1 — accession facts from source")
    print(f"  {os.path.relpath(MOD, REPO)}:{facts['module_PARENTS_line']}  PARENTS = "
          f"{facts['module_PARENTS']}")
    print(f"  PARENTS referenced on lines: {facts['module_lines_referencing_PARENTS']}")
    print(f"  test fixture records: {facts['test_fixture_records']}")
    print("  junction-selfsimilarity.json EWSR1 hits:")
    for a, n in sorted(facts["selfsimilarity_EWSR1_accessions"].items()):
        print(f"    {a}  {n}")
    print(f"  defect reproduces as described: {res['step1_defect_reproduces']}")
    print()
    print("STEP 2 — replay over committed junction-proteome-novelty.json")
    print(f"  unpatched replay reproduces the committed verdict block: {fidelity}")
    for label, r in (("BEFORE (unpatched PARENTS)", before), ("AFTER  (patched PARENTS)", after)):
        c = r["upstream_filter_check"]
        print(f"  {label}")
        print(f"    n_peptides_tested={r['n_peptides_tested']} "
              f"n_found_in_proteome={r['n_found_in_proteome']} "
              f"n_novel_proteome_wide={r['n_novel_proteome_wide']} "
              f"n_predicted_binders_found_in_proteome="
              f"{r['n_predicted_binders_found_in_proteome']}")
        print(f"    verdict: {c['verdict']}")
        for h in c["parent_protein_hits"]:
            print(f"      parent hit: {h['peptide']:<12} {h['accession']:<10} {h['parent']}")
    print(f"  IDENTICAL: {identical}")
    print(f"  any Q01844* accession among committed hits: {ews_reachable}")
    print(f"  wrote {os.path.relpath(OUT, REPO)}")
    return 0 if (fidelity and identical and res["step1_defect_reproduces"]) else 2


if __name__ == "__main__":
    sys.exit(main())
