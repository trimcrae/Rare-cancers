#!/usr/bin/env python3
"""NEOANTIGEN-7 — bounding the 20 zero-NR4A3 junction peptides NEOANTIGEN-6 left open.

WRITTEN BEFORE COMPUTING (so the reading is not fitted to the outcome).

The question is a BOUNDING question, not a determination:
  (1) reproduce the zero-NR4A3 class independently from committed inputs;
  (2) establish which EWSR1 sequences this checkout actually HOLDS, and whether each of the
      zero-NR4A3 peptides occurs verbatim in what is held;
  (3) count and NAME the EWSR1 isoforms this repository's own artifacts NAME but carry no
      sequence for — that count is the size of the blind spot;
  (4) state the exact minimal input that would settle all of them.

What a HIT in the held set would license: exactly one statement — that peptide occurs verbatim in
that held wild-type sequence, so it is not junction-specific at the sequence level.
What a MISS licenses: exactly one statement — the peptide is NOT PRESENT IN THE HELD SET.
A miss is NOT novelty, NOT absence from the human proteome, and NOT absence from any EWSR1 isoform.
Nothing here is an immunogenicity, presentation, tolerance, efficacy, safety, selectivity,
therapeutic-window or clinical-readiness claim, in either direction. A composition filter is not a
novelty search, and evidence about presentation is not in scope at all.

No network. Routes B1/B2 (Ensembl FASTA) are CLOSED and are not approached: no isoform sequence is
fetched, substituted, reconstructed or guessed here.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research", "modalities")
LANE = os.path.dirname(os.path.abspath(__file__))

PANEL = os.path.join(MOD, "fusion-breakpoint-neoantigens.json")
SELFSIM = os.path.join(MOD, "junction-selfsimilarity.json")
PROTNOV = os.path.join(MOD, "junction-proteome-novelty.json")
FETCACHE = os.path.join(MOD, "fet-sequences-cache.json")
NR4ACACHE = os.path.join(MOD, "nr4a-sequences-cache.json")
N4AUDIT = os.path.join(LANE, "..", "NEOANTIGEN-4", "neoantigen4-novelty-audit.json")
N6PANEL = os.path.join(LANE, "..", "NEOANTIGEN-6", "refiltered-panel.json")

SEAM_INDEX = 10  # junction_context is 10 EWSR1 residues + 1 seam residue + 10 NR4A3 residues


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def partner_split(context_with_bar: str, peptide: str):
    """Return (n_ewsr1, n_seam, n_nr4a3, start) for a peptide placed in a junction context.

    The placement must be UNIQUE in the context, and must cover the seam; both are asserted.
    """
    ctx = context_with_bar.replace("|", "").replace("-", "")
    starts = [i for i in range(len(ctx) - len(peptide) + 1) if ctx[i:i + len(peptide)] == peptide]
    if len(starts) != 1:
        return None
    s = starts[0]
    e = s + len(peptide)
    if not (s <= SEAM_INDEX < e):
        return None
    n_ews = max(0, min(e, SEAM_INDEX) - s)
    n_nr4 = max(0, e - (SEAM_INDEX + 1))
    return n_ews, 1, n_nr4, s


def main() -> int:
    panel = load(PANEL)
    junctions = panel["junctions"]

    # ---------- Step 1 · reproduce the classes from the committed panel ----------
    per_peptide = {}   # peptide -> list of per-junction splits
    failures = []
    for j in junctions:
        ctx = j["junction_context"]
        label = j["junction_label"]
        for pep in j["novel_peptides"]:
            sp = partner_split(ctx, pep)
            if sp is None:
                failures.append({"junction": label, "peptide": pep})
                continue
            n_ews, n_seam, n_nr4, start = sp
            per_peptide.setdefault(pep, []).append(
                {"junction": label, "n_from_EWSR1": n_ews, "n_seam": n_seam,
                 "n_from_NR4A3": n_nr4, "start_in_context": start,
                 "context": ctx.replace("|", "")}
            )
    if failures:
        print("FATAL: peptide placement failed (not unique, or does not cover the seam):", failures)
        return 2

    zero_ews = sorted(p for p, rs in per_peptide.items() if all(r["n_from_EWSR1"] == 0 for r in rs))
    zero_nr4 = sorted(p for p, rs in per_peptide.items() if all(r["n_from_NR4A3"] == 0 for r in rs))
    zero_both = sorted(set(zero_ews) & set(zero_nr4))

    counts = {
        "n_distinct_peptides": len(per_peptide),
        "n_zero_EWSR1": len(zero_ews),
        "n_zero_NR4A3": len(zero_nr4),
        "n_zero_both": len(zero_both),
    }
    expected = {"n_distinct_peptides": 174, "n_zero_EWSR1": 8, "n_zero_NR4A3": 20, "n_zero_both": 0}
    reproduction = {
        "expected_from_NEOANTIGEN_6": expected,
        "observed_here": counts,
        "agrees": counts == expected,
        "disagreements": {k: {"expected": expected[k], "observed": counts[k]}
                          for k in expected if expected[k] != counts[k]},
    }

    # cross-check the 20 against NEOANTIGEN-6's own emitted list, where it records one
    n6_zero_nr4 = []
    try:
        n6 = load(N6PANEL)
        blob = json.dumps(n6)
        n6_zero_nr4 = sorted({p for p in zero_nr4 if '"%s"' % p in blob})
        n6_removed = sorted(re.findall(r'"peptide":\s*"([A-Z]+)"', json.dumps(n6.get("removed", []))))
    except Exception as exc:  # pragma: no cover - recorded, never silently swallowed
        n6_zero_nr4 = ["<unreadable: %s>" % exc]
        n6_removed = []

    # ---------- Step 2 · what EWSR1 sequence this checkout actually HOLDS ----------
    fet = load(FETCACHE)
    nr4a = load(NR4ACACHE)
    held = {}
    for src, d in (("fet-sequences-cache.json", fet), ("nr4a-sequences-cache.json", nr4a)):
        for sym, seq in d.items():
            if isinstance(seq, str) and sym == "EWSR1":
                held.setdefault(hashlib.sha256(seq.encode()).hexdigest(), {
                    "symbol": sym, "length": len(seq),
                    "sha256": hashlib.sha256(seq.encode()).hexdigest(),
                    "sources": [], "sequence_head": seq[:30], "sequence_tail": seq[-15:],
                    "_seq": seq})["sources"].append(src)
    held_list = list(held.values())

    # designed constructs that EMBED EWSR1 sequence — searched SEPARATELY and never counted as
    # wild-type: a hit inside a designed EWSR1::NR4A3 fusion construct is expected by construction
    # and is not evidence of wild-type occurrence.
    construct_files = ["emc-fet-construct-designs.json", "emc-condensate-constructs.json",
                       "emc-construct-inputs.json", "fusion-cofold-constructs.json"]
    constructs = []

    def walk(o, path, fname):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, path + "/" + str(k), fname)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + "[%d]" % i, fname)
        elif isinstance(o, str) and len(o) > 100 and o.startswith("MASTDYSTYSQAAAQQGYSA"):
            constructs.append({"file": fname, "path": path, "length": len(o),
                               "sha256": hashlib.sha256(o.encode()).hexdigest(), "_seq": o})

    for fname in construct_files:
        walk(load(os.path.join(MOD, fname)), "", fname)
    # de-duplicate identical construct sequences, and drop any that is the wild-type canonical
    seen = set()
    uniq_constructs = []
    for c in constructs:
        if c["sha256"] in seen or c["sha256"] in held:
            continue
        seen.add(c["sha256"])
        uniq_constructs.append(c)

    canonical = held_list[0]["_seq"] if held_list else ""

    def search_held(pep: str):
        hits = []
        for h in held_list:
            i = h["_seq"].find(pep)
            if i >= 0:
                hits.append({"kind": "held_wild_type_EWSR1", "sha256": h["sha256"],
                             "offset_1based": i + 1})
        return hits

    def search_constructs(pep: str):
        hits = []
        for c in uniq_constructs:
            i = c["_seq"].find(pep)
            if i >= 0:
                hits.append({"kind": "designed_construct_NOT_wild_type", "file": c["file"],
                             "path": c["path"], "offset_1based": i + 1})
        return hits

    rows = []
    for pep in zero_nr4:
        rs = per_peptide[pep]
        # every zero-NR4A3 peptide ends at the seam residue; its prefix is EWSR1 sequence
        prefix = pep[:-1]
        seam = pep[-1]
        prefix_hits = [i + 1 for i in range(len(canonical)) if canonical.startswith(prefix, i)] \
            if prefix else []
        following = sorted({canonical[i - 1 + len(prefix)]
                            for i in prefix_hits if i - 1 + len(prefix) < len(canonical)})
        rows.append({
            "peptide": pep,
            "length": len(pep),
            "junctions": [r["junction"] for r in rs],
            "n_from_EWSR1": rs[0]["n_from_EWSR1"],
            "n_seam": 1,
            "n_from_NR4A3": 0,
            "seam_residue": seam,
            "verbatim_in_held_wild_type_EWSR1": search_held(pep),
            "verbatim_in_designed_constructs": search_constructs(pep),
            "ewsr1_only_prefix": prefix,
            "prefix_offsets_in_held_canonical_1based": prefix_hits,
            "residues_following_prefix_in_held_canonical": following,
            "seam_matches_wild_type_next_residue": seam in following,
        })

    n_hit = sum(1 for r in rows if r["verbatim_in_held_wild_type_EWSR1"])
    n_miss = len(rows) - n_hit

    # ---------- controls ----------
    # POSITIVE control: a peptide planted verbatim from the held canonical EWSR1 MUST be found.
    planted_offset = 200  # arbitrary interior window, 1-based 201..209
    planted = canonical[planted_offset:planted_offset + 9]
    pos_hits = search_held(planted)
    pos_ok = bool(pos_hits) and pos_hits[0]["offset_1based"] == planted_offset + 1
    # NEGATIVE control: a deterministic scramble of one of the 20 MUST NOT be found.
    src_pep = rows[0]["peptide"] if rows else "AAVEWFDD"
    scrambled = "".join(sorted(src_pep, reverse=True)) + "W"  # W is rare in this region
    neg_hits = search_held(scrambled)
    neg_ok = not neg_hits and scrambled != src_pep

    # ---------- Step 3 · the size of the blind spot ----------
    selfsim = load(SELFSIM)
    protnov = load(PROTNOV)
    named = {}
    for artifact, path in ((selfsim, "junction-selfsimilarity.json"),
                           (protnov, "junction-proteome-novelty.json")):
        blob = json.dumps(artifact)
        for acc in re.findall(r"Q01844(?:-\d+)?", blob):
            named.setdefault(acc, set()).add(path)
    # protein names as recorded, for the isoform accessions
    isoform_names = {}
    for q in selfsim.get("queries", []):
        for h in q.get("hits", []):
            if str(h.get("accession", "")).startswith("Q01844"):
                isoform_names[h["accession"]] = h.get("protein")
    isoforms_named = sorted(a for a in named if "-" in a)
    held_shas = {h["sha256"] for h in held_list}
    blind = [{"accession": a, "protein_name_as_recorded": isoform_names.get(a),
              "named_in": sorted(named[a]),
              "sequence_present_in_checkout": False} for a in isoforms_named]

    out = {
        "_id": "DOC-NEOANTIGEN-7-ZERO-NR4A3-BOUNDING",
        "_what": "Bounding artifact for the 20 zero-NR4A3 EWSR1::NR4A3 junction peptides left open "
                 "by NEOANTIGEN-6: independent reproduction of the class, verbatim search against "
                 "the EWSR1 sequence this checkout actually holds, and an exact count of the EWSR1 "
                 "isoforms this repository's own artifacts NAME but carry no sequence for.",
        "⛔_what_this_is_not": "Not a novelty search, not a presentation, immunogenicity, tolerance, "
                              "efficacy, safety, selectivity, therapeutic-window or clinical claim, "
                              "in either direction. A MISS below means ONLY 'not present in the held "
                              "set'. It never means novel.",
        "_cost": "$0 — no network, no GPU, no paid API. Routes B1/B2 not approached.",
        "_inputs": {
            "fusion-breakpoint-neoantigens.json": {"sha256": sha256_file(PANEL),
                                                   "_utc": panel.get("_utc")},
            "junction-selfsimilarity.json": {"sha256": sha256_file(SELFSIM),
                                             "generated_utc": selfsim.get("generated_utc")},
            "junction-proteome-novelty.json": {"sha256": sha256_file(PROTNOV)},
            "fet-sequences-cache.json": {"sha256": sha256_file(FETCACHE)},
            "nr4a-sequences-cache.json": {"sha256": sha256_file(NR4ACACHE)},
        },
        "step1_reproduction": reproduction,
        "step1_zero_EWSR1_peptides": zero_ews,
        "step1_zero_NR4A3_peptides": zero_nr4,
        "step1_zero_both": zero_both,
        "step1_cross_check_NEOANTIGEN_6": {
            "n_of_the_20_appearing_verbatim_in_NEOANTIGEN-6_artifact": len(n6_zero_nr4),
            "peptides": n6_zero_nr4,
        },
        "step2_held_EWSR1_sequences": [
            {k: v for k, v in h.items() if k != "_seq"} for h in held_list
        ],
        "step2_designed_constructs_embedding_EWSR1_NOT_wild_type": [
            {k: v for k, v in c.items() if k != "_seq"} for c in uniq_constructs
        ],
        "step2_per_peptide": rows,
        "step2_summary": {
            "n_peptides": len(rows),
            "n_verbatim_in_held_wild_type_EWSR1": n_hit,
            "n_not_present_in_held_set": n_miss,
            "reading": "A hit is decisive. A miss is 'not in the held set' and NOTHING else.",
        },
        "controls": {
            "positive": {"planted_peptide": planted,
                         "planted_from": "held canonical EWSR1, 1-based offset %d" % (planted_offset + 1),
                         "found": pos_hits, "passed": pos_ok,
                         "requirement": "a peptide taken verbatim from the held sequence MUST be found"},
            "negative": {"scrambled_peptide": scrambled, "scrambled_from": src_pep,
                         "found": neg_hits, "passed": neg_ok,
                         "requirement": "a scrambled peptide MUST NOT be found"},
        },
        "step3_blind_spot": {
            "n_EWSR1_isoform_accessions_named_without_sequence": len(blind),
            "isoforms": blind,
            "canonical_Q01844_sequence_held": bool(held_shas),
            "⚠_lower_bound": "This counts the EWSR1 isoform accessions this repository's own "
                             "artifacts NAME. It is a LOWER BOUND on the true isoform set: an "
                             "isoform that produced no recorded near-self or exact hit would not be "
                             "named here, and this checkout cannot enumerate UniProt.",
        },
        "step4_minimal_input_to_settle": {
            "requirement": "the amino-acid sequence of each named EWSR1 isoform (%s) — nothing "
                           "less settles the 20, because each of them is EWSR1 sequence up to and "
                           "including the hybrid seam residue, so its status depends entirely on "
                           "what the isoform's residues are at and after the donor position"
                           % ", ".join(isoforms_named),
            "sufficient": "an exact-substring search of the 20 against those isoform sequences, "
                          "run the same way junction-proteome-novelty.json was run",
            "route": "the isoform sequences are behind routes B1/B2 (Ensembl/UniProt isoform FASTA), "
                     "which are CLOSED for this lane",
            "action_taken": "NONE — not fetched, not substituted, not reconstructed, not approached",
        },
    }

    dest = os.path.join(LANE, "neoantigen7-zero-nr4a3-bounding.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    print("reproduction:", json.dumps(reproduction))
    print("zero_NR4A3 (%d):" % len(zero_nr4), zero_nr4)
    print("held wild-type EWSR1 sequences:",
          [(h["length"], h["sha256"][:12], h["sources"]) for h in held_list])
    print("verbatim hits among the %d: %d ; not present in held set: %d" % (len(rows), n_hit, n_miss))
    print("seam_matches_wild_type_next_residue counts:",
          {True: sum(1 for r in rows if r["seam_matches_wild_type_next_residue"]),
           False: sum(1 for r in rows if not r["seam_matches_wild_type_next_residue"])})
    print("positive control:", planted, "passed=%s" % pos_ok)
    print("negative control:", scrambled, "passed=%s" % neg_ok)
    print("blind spot: %d named EWSR1 isoform accessions with no sequence in checkout: %s"
          % (len(blind), isoforms_named))
    print("wrote", dest)

    ok = reproduction["agrees"] and pos_ok and neg_ok
    if not ok:
        print("ASSERTION FAILURE: agrees=%s pos=%s neg=%s"
              % (reproduction["agrees"], pos_ok, neg_ok))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
