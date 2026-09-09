#!/usr/bin/env python3
"""
NEOANTIGEN-4 — defect audit of the EWSR1::NR4A3 junction screen's own NOVELTY FILTER.

QUESTION. Across all 174 junction peptides and all 11 ranked binders, how many are
genuinely junction-novel — i.e. do NOT occur verbatim in wild-type human protein
sequence? Reported as a proportion with an exact denominator, naming every non-novel
peptide, its parent protein/isoform and the exact offset.

⛔ WHAT A HIGH NON-NOVEL PROPORTION WOULD AND WOULD NOT LICENCE. It would license
exactly one statement: those peptides are not fusion-specific at the sequence level, so
a screen that ranked them as fusion neoantigens ranked wild-type self sequence. It would
NOT license any claim about immunogenicity, presentation, tolerance, TCR cross-reactivity,
safety or clinical usability — in either direction. A novel peptide is not thereby
presented; a non-novel peptide is not thereby tolerated.

⛔ OFFLINE ONLY. No network. The Ensembl (B1/B2) and surfaceome (B4) routes are CLOSED
and are not retried or proxied around. The wild-type corpus is therefore exactly what is
committed in this checkout — CANONICAL sequences only, NO isoform sequences — and every
number below is scoped to that corpus and says so. The wider reviewed-proteome result
(42,547 sequences WITH isoforms) is not recomputed here; it is READ from the committed
artifact and reconciled, never re-derived.

Writes only into this lane directory.
"""

import datetime
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
MOD = os.path.join(REPO, "research", "modalities")
BREAKPOINTS = os.path.join(MOD, "fusion-breakpoint-neoantigens.json")
NOVELTY = os.path.join(MOD, "junction-proteome-novelty.json")
SELFSIM = os.path.join(MOD, "junction-selfsimilarity.json")
NR4A_CACHE = os.path.join(MOD, "nr4a-sequences-cache.json")
FET_CACHE = os.path.join(MOD, "fet-sequences-cache.json")
OUT = os.path.join(HERE, "neoantigen4-novelty-audit.json")

# Accessions as this repository records them elsewhere (nr4a_paralogue_unique_residues.py,
# emc_fet_construct_designs.py, fusion_neoantigen.py). EWSR1 is Q01844.
ACCESSIONS = {"NR4A3": "Q92570", "EWSR1": "Q01844", "NR4A1": "P22736",
              "NR4A2": "P43354", "TAF15": "Q92804", "FUS": "P35637"}
PARENTS = ("EWSR1", "NR4A3")


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def find_all(hay, needle):
    """Every 1-based offset at which `needle` occurs verbatim in `hay`."""
    out, i = [], hay.find(needle)
    while i != -1:
        out.append(i + 1)
        i = hay.find(needle, i + 1)
    return out


def main():
    bp = load(BREAKPOINTS)
    nov = load(NOVELTY)
    ss = load(SELFSIM)
    nr4a = load(NR4A_CACHE)
    fet = load(FET_CACHE)

    # ---- query sets -------------------------------------------------------
    peptides = {}                       # peptide -> [junction labels]
    contexts = {}                       # junction label -> 21-mer context
    for j in bp["junctions"]:
        ctx = j["junction_context"].replace("|", "")
        contexts[j["junction_label"]] = {
            "context": ctx,
            "donor_len": j["junction_context"].index("|"),
            "seam_residue": j["seam_codon_residue"],
        }
        for p in j["novel_peptides"]:
            peptides.setdefault(p, []).append(j["junction_label"])
    all_pep = sorted(peptides)
    binders = sorted({b["peptide"] for b in bp["predicted_binders_ranked"]})
    assert len(all_pep) == 174, f"expected 174 distinct junction peptides, got {len(all_pep)}"
    assert len(binders) == 11, f"expected 11 distinct ranked binders, got {len(binders)}"
    assert set(binders) <= set(all_pep), "a ranked binder is not a member of the junction set"
    # the committed proteome artifact must be testing the same 174, else reconciliation is void
    committed_set = {r["peptide"] for r in nov["peptides_found_in_proteome"]} | \
                    {r["peptide"] for r in nov["peptides_novel_proteome_wide"]}
    same_input = committed_set == set(all_pep)

    # ---- wild-type corpus actually present in this checkout ---------------
    corpus = []
    for gene in ("NR4A3", "EWSR1", "NR4A1", "NR4A2"):
        seq = nr4a[gene]
        corpus.append({"gene": gene, "accession": ACCESSIONS[gene], "isoform": "canonical",
                       "source_file": "research/modalities/nr4a-sequences-cache.json",
                       "length": len(seq), "sha256_16": sha(seq),
                       "is_fusion_parent": gene in PARENTS, "_seq": seq})
    for gene in ("TAF15", "FUS"):
        seq = fet[gene]
        corpus.append({"gene": gene, "accession": ACCESSIONS[gene], "isoform": "canonical",
                       "source_file": "research/modalities/fet-sequences-cache.json",
                       "length": len(seq), "sha256_16": sha(seq),
                       "is_fusion_parent": False, "_seq": seq})
    # cross-check: the two caches must agree where they overlap, or the corpus is ambiguous
    cache_agreement = {g: (nr4a[g] == fet[g]) for g in ("EWSR1", "NR4A3", "NR4A1", "NR4A2")}
    assert all(cache_agreement.values()), f"sequence caches disagree: {cache_agreement}"

    def search(pep):
        hits = []
        for rec in corpus:
            for off in find_all(rec["_seq"], pep):
                hits.append({"gene": rec["gene"], "accession": rec["accession"],
                             "isoform": rec["isoform"], "offset_1based": off,
                             "is_fusion_parent": rec["is_fusion_parent"]})
        return hits

    # ---- controls ---------------------------------------------------------
    nr4a3 = nr4a["NR4A3"]
    # ⚠ The planted peptide must be UNIQUE in the corpus, else "found at the right offset" is
    # satisfiable by a degenerate tract (NR4A3 carries a 14-residue poly-histidine run, and the
    # first attempt planted HHHHHHHHH from inside it — recorded in checks/01). Take the first
    # 9-mer window of NR4A3 that occurs EXACTLY ONCE across the whole corpus, and require exactly
    # one hit, in the right protein, at the right offset.
    planted, planted_off = None, None
    for i in range(len(nr4a3) - 9):
        cand = nr4a3[i:i + 9]
        if len(search(cand)) == 1:
            planted, planted_off = cand, i + 1
            break
    assert planted is not None, "no unique 9-mer window in NR4A3 to use as a positive control"
    pos_hits = search(planted)
    pos_ok = (len(pos_hits) == 1 and pos_hits[0]["gene"] == "NR4A3"
              and pos_hits[0]["offset_1based"] == planted_off)
    rng = random.Random(20260909)
    src = "DMPCVQAQY"
    scr = src
    for _ in range(64):
        cand = list(src)
        rng.shuffle(cand)
        cand = "".join(cand)
        if cand != src and not search(cand):
            scr = cand
            break
    neg_hits = search(scr)
    neg_ok = (scr != src) and (neg_hits == [])
    # second positive control: a peptide the committed proteome test already calls a hit,
    # searched against the LOCAL corpus, MUST miss - because the isoform it hits is absent here.
    isoform_absent_ok = search("DMPCVQAQY") == []
    controls_pass = pos_ok and neg_ok and isoform_absent_ok

    # ---- arms -------------------------------------------------------------
    def run_arm(queries):
        rows, nonnovel = [], []
        for pep in queries:
            hits = search(pep)
            row = {"peptide": pep, "junctions": peptides[pep],
                   "is_ranked_binder": pep in binders,
                   "local_wildtype_hits": hits, "novel_vs_local_corpus": not hits}
            rows.append(row)
            if hits:
                nonnovel.append(row)
        return rows, nonnovel

    rows174, non174 = run_arm(all_pep)
    rows11, non11 = run_arm(binders)

    # ---- per-partner residue split (all 174) ------------------------------
    split_rows, zero_donor = [], []
    for pep in all_pep:
        best = None
        for lab in peptides[pep]:
            c = contexts[lab]
            offs = find_all(c["context"], pep)
            assert offs, f"{pep} not locatable in context of {lab}"
            o = offs[0] - 1                       # 0-based start in the 21-mer
            dlen = c["donor_len"]                 # donor residues occupy [0, dlen)
            donor = max(0, min(o + len(pep), dlen) - o)
            seam = 1 if o <= dlen < o + len(pep) else 0
            acceptor = len(pep) - donor - seam
            rec = {"peptide": pep, "junction": lab, "n_from_EWSR1": donor,
                   "n_seam_hybrid": seam, "n_from_NR4A3": acceptor}
            if best is None or donor < best["n_from_EWSR1"]:
                best = rec
        split_rows.append(best)
        if best["n_from_EWSR1"] == 0:
            zero_donor.append(best)

    # ---- exact offsets for the committed wider-proteome hits --------------
    ss_exact = {}
    for q in ss["queries"]:
        for h in q["hits"]:
            if h["n_mismatches"] == 0:
                ss_exact.setdefault(q["peptide"], []).append(
                    {"accession": h["accession"], "protein": h["protein"],
                     "offset_1based": h["position"], "source": "junction-selfsimilarity.json"})

    wider = []
    anchor = ss_exact.get("DMPCVQAQY", [{}])[0].get("offset_1based")
    for r in nov["peptides_found_in_proteome"]:
        pep = r["peptide"]
        if pep in ss_exact:
            loc = ss_exact[pep]
            how = "stated by junction-selfsimilarity.json (exact, 0 mismatches)"
        elif anchor and pep.startswith("DMPCVQAQ"):
            loc = [{"accession": h["accession"], "protein": h["protein"],
                    "offset_1based": anchor} for h in r["proteome_hits"]]
            how = ("DERIVED, not stated: every hit peptide shares the prefix DMPCVQAQ with "
                   "DMPCVQAQY, whose exact offset in Q92570-3 IS stated, so all four start at "
                   "the same residue; the isoform sequence is not in this checkout, so this "
                   "offset is not independently verified here")
        else:
            loc, how = [], "UNKNOWN — no committed artifact states the offset"
        wider.append({"peptide": pep, "junctions": r["junctions"],
                      "is_ranked_binder": pep in binders,
                      "proteome_hits": r["proteome_hits"], "offsets": loc, "offset_provenance": how})

    art = {
        "_what": ("Defect audit of the EWSR1::NR4A3 junction screen's NOVELTY FILTER: how many of "
                  "the 174 junction peptides and 11 ranked binders occur VERBATIM in wild-type "
                  "human protein sequence. Two strata, reported separately and never merged: "
                  "(A) recomputed here against the wild-type sequences actually committed in this "
                  "checkout (CANONICAL ONLY, no isoforms); (B) read, not recomputed, from the "
                  "committed reviewed-proteome-with-isoforms result."),
        "⛔_what_this_is_not": ("Not an immunogenicity, presentation, tolerance, TCR-cross-reactivity, "
                               "safety, selectivity or clinical-usability claim, in either direction. "
                               "A verbatim wild-type match shows only that a peptide is not "
                               "fusion-specific AT THE SEQUENCE LEVEL. A miss shows only that it is "
                               "absent from the searched sequences."),
        "_utc": utcnow(),
        "_cost": "$0 — offline, CPU only, no network, no GPU, no paid API.",
        "_inputs": {
            "fusion-breakpoint-neoantigens.json": {"_utc": bp["_utc"], "n_junctions": len(bp["junctions"])},
            "junction-proteome-novelty.json": {"n_peptides_tested": nov["n_peptides_tested"],
                                               "proteome": nov["_proteome"]},
            "junction-selfsimilarity.json": {"generated_utc": ss["generated_utc"],
                                             "n_queries": ss["n_queries"]},
            "sequence caches": ["research/modalities/nr4a-sequences-cache.json",
                                "research/modalities/fet-sequences-cache.json"],
            "committed_novelty_artifact_tests_the_same_174_peptides": same_input,
            "sequence_caches_agree_where_they_overlap": cache_agreement,
        },
        "_denominators": {"junction_peptides": len(all_pep), "ranked_binders": len(binders),
                          "ranked_binders_are_a_subset_of_the_174": True},
        "⛔_wild_type_corpus_limitation": (
            "THE WILD-TYPE SEQUENCE SET IN THIS CHECKOUT IS SMALLER THAN THE ONE "
            "junction-proteome-novelty.json USED. That artifact searched 42,547 reviewed UniProt "
            "sequences WITH isoforms, fetched over the network in CI. This checkout contains NO "
            "proteome FASTA and NO isoform sequence of any protein — only the canonical sequences "
            "listed in _wild_type_corpus. Stratum A is therefore scoped to 6 canonical human "
            "proteins and CANNOT reproduce or contradict the wider result; the wider numbers are "
            "quoted from the committed artifact in stratum B, not recomputed. No network fetch was "
            "attempted: routes B1/B2/B4 are closed."),
        "_wild_type_corpus": [{k: v for k, v in r.items() if k != "_seq"} for r in corpus],
        "controls": {
            "positive_planted": {"peptide": planted,
                                 "planted_from": f"NR4A3 canonical residues {planted_off}-{planted_off + 8}",
                                 "uniqueness": "occurs exactly once in the whole local corpus",
                                 "expected_offset_1based": planted_off,
                                 "expected_n_hits": 1, "hits": pos_hits, "pass": pos_ok},
            "negative_scrambled": {"peptide": scr, "scrambled_from": src, "seed": 20260909,
                                   "hits": neg_hits, "pass": neg_ok},
            "positive_known_hit_must_miss_locally": {
                "peptide": "DMPCVQAQY",
                "expectation": ("hits Q92570-3 in the committed wider result; MUST miss here, "
                                "because no isoform sequence is present in this checkout — this is "
                                "the control that demonstrates the local corpus's stated blind spot"),
                "hits_locally": search("DMPCVQAQY"), "pass": isoform_absent_ok},
            "all_pass": controls_pass,
        },
        "A_local_canonical_corpus": {
            "_scope": "6 canonical human proteins committed in this checkout; NO isoforms.",
            "arm_174_junction_peptides": {
                "n_tested": len(all_pep), "n_non_novel": len(non174),
                "n_novel_vs_this_corpus": len(all_pep) - len(non174),
                "proportion_non_novel": f"{len(non174)}/{len(all_pep)}",
                "non_novel": non174},
            "arm_11_ranked_binders": {
                "n_tested": len(binders), "n_non_novel": len(non11),
                "n_novel_vs_this_corpus": len(binders) - len(non11),
                "proportion_non_novel": f"{len(non11)}/{len(binders)}",
                "non_novel": non11},
            "reading": ("Zero is the EXPECTED result and is not reassurance: fusion_breakpoints.py "
                        "already filters every candidate against canonical EWSR1 and canonical "
                        "NR4A3, so a hit against those two would mean the upstream filter had "
                        "failed outright. The informative content of stratum A is (i) that the "
                        "canonical two-protein filter is confirmed to have been applied, (ii) that "
                        "no peptide is a verbatim NR4A1/NR4A2/TAF15/FUS wild-type peptide either, "
                        "and (iii) that the ONLY recorded non-novelty comes from an ISOFORM, which "
                        "is exactly the sequence class this checkout cannot search."),
        },
        "B_committed_reviewed_proteome_with_isoforms": {
            "_scope": nov["_proteome"],
            "_this_is_read_not_recomputed": True,
            "arm_174_junction_peptides": {
                "n_tested": nov["n_peptides_tested"],
                "n_non_novel": nov["n_found_in_proteome"],
                "n_novel": nov["n_novel_proteome_wide"],
                "proportion_non_novel": f"{nov['n_found_in_proteome']}/{nov['n_peptides_tested']}",
                "non_novel": wider},
            "arm_11_ranked_binders": {
                "n_tested": len(binders),
                "n_non_novel": sum(1 for w in wider if w["is_ranked_binder"]),
                "n_novel": len(binders) - sum(1 for w in wider if w["is_ranked_binder"]),
                "proportion_non_novel": f"{sum(1 for w in wider if w['is_ranked_binder'])}/{len(binders)}",
                "non_novel": [w for w in wider if w["is_ranked_binder"]],
                "note": ("the one non-novel ranked binder is the TOP-RANKED peptide by "
                         "presentation percentile, not a marginal entry")},
            "⛔_what_it_still_does_not_cover": (
                "reviewed (Swiss-Prot) entries only — TrEMBL was deliberately not searched, so "
                "'novel' here means 'absent from reviewed human protein sequence', not 'absent "
                "from every human protein'; and the fetch is a 2026-08-22 snapshot."),
        },
        "C_partner_residue_split_all_174": {
            "_what": ("For every one of the 174 peptides, how many residues come from EWSR1, from "
                      "the hybrid seam codon, and from NR4A3, at the junction offset that minimises "
                      "the EWSR1 contribution. NEOANTIGEN-3 computed this for the 11 ranked binders "
                      "only; this extends it to the full set."),
            "_why_it_matters": ("A peptide contributing ZERO EWSR1 residues is seam + wild-type "
                                "NR4A3 sequence. Its novelty rests entirely on one hybrid residue, "
                                "and it is precisely the class that an isoform with an N-terminal "
                                "extension can reproduce verbatim — which is what happened to all "
                                "four recorded hits."),
            "n_with_zero_EWSR1_residues": len(zero_donor),
            "proportion_with_zero_EWSR1_residues": f"{len(zero_donor)}/{len(all_pep)}",
            "n_ranked_binders_with_zero_EWSR1_residues":
                sum(1 for r in zero_donor if r["peptide"] in binders),
            "zero_EWSR1_peptides": zero_donor,
            "all_rows": split_rows,
        },
        "D_defect_found_in_the_novelty_script_itself": {
            "file": "research/modalities/junction_proteome_novelty.py",
            "line": 85,
            "code": 'PARENTS = {"P56945": "EWSR1", "Q92570": "NR4A3"}',
            "problem": ("P56945 is NOT the UniProt accession this repository uses for human EWSR1. "
                        "Every other module here uses Q01844 (nr4a_paralogue_unique_residues.py:54, "
                        "emc_fet_construct_designs.py:113, fusion_neoantigen.py:78, "
                        "emc-construct-inputs.json, nr4a-paralogue-unique-residues.json), and "
                        "junction-selfsimilarity.json's own proteome hits name EWSR1 as Q01844 / "
                        "Q01844-2 / -3 / -5 / -6."),
            "consequence": ("The ⛔_upstream_filter_check arm can only ever flag NR4A3 hits. A "
                            "junction peptide occurring verbatim in wild-type EWSR1 OR ANY EWSR1 "
                            "ISOFORM would still be counted in n_found_in_proteome, but would NOT "
                            "appear in parent_protein_hits and would NOT trip the BROKEN verdict — "
                            "the guard silently covers one parent instead of two."),
            "impact_on_the_committed_result": ("NONE on the headline counts. All four recorded hits "
                                               "are Q92570-3, so the verdict is BROKEN either way. "
                                               "The defect is in the GUARD's coverage, not in the "
                                               "4/174 number."),
            "status": ("REPORTED ONLY. No shared file was edited; an UNAPPLIED unified diff is in "
                       "this lane directory. Fixing the accession can only make the guard catch "
                       "MORE, never less — it does not weaken it."),
        },
        "_headline": {
            "question": ("of 174 junction peptides and 11 ranked binders, how many are NOT verbatim "
                         "wild-type human sequence?"),
            "best_available_answer": {
                "scope": "reviewed human proteome WITH isoforms, 42,547 sequences (committed, CI-fetched 2026-08-22)",
                "junction_peptides_novel": "170/174 (97.7%)",
                "junction_peptides_non_novel": "4/174 (2.3%)",
                "ranked_binders_novel": "10/11 (90.9%)",
                "ranked_binders_non_novel": "1/11 (9.1%) — DMPCVQAQY, the TOP-RANKED binder, "
                                            "verbatim in NR4A3 isoform Q92570-3 at residue 11",
            },
            "recomputable_here": {
                "scope": "6 canonical human proteins committed in this checkout, no isoforms",
                "junction_peptides_non_novel": f"{len(non174)}/{len(all_pep)}",
                "ranked_binders_non_novel": f"{len(non11)}/{len(binders)}",
            },
            "the_number_that_is_not_reassuring": (
                f"{len(zero_donor)}/{len(all_pep)} junction peptides and "
                f"{sum(1 for r in zero_donor if r['peptide'] in binders)}/{len(binders)} ranked "
                "binders contribute ZERO residues from EWSR1 — they are one hybrid seam residue "
                "away from being wild-type NR4A3 peptides, and the four that a real isoform "
                "happened to reproduce are drawn entirely from that class."),
        },
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    print(f"controls: positive={pos_ok} negative={neg_ok} isoform-blindspot={isoform_absent_ok}")
    print(f"A (local canonical corpus): 174-arm non-novel {len(non174)}/{len(all_pep)}; "
          f"11-arm non-novel {len(non11)}/{len(binders)}")
    print(f"B (committed reviewed proteome + isoforms): 174-arm non-novel "
          f"{nov['n_found_in_proteome']}/{nov['n_peptides_tested']}; 11-arm non-novel "
          f"{sum(1 for w in wider if w['is_ranked_binder'])}/{len(binders)}")
    print(f"C zero-EWSR1-residue peptides: {len(zero_donor)}/{len(all_pep)}; of ranked binders "
          f"{sum(1 for r in zero_donor if r['peptide'] in binders)}/{len(binders)}")
    if not controls_pass:
        print("CONTROLS FAILED — the matcher is not demonstrated", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
