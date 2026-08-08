#!/usr/bin/env python3
"""Europe PMC probe: how much of the field actually holds the view the fusion paper re-reads.

WHY THIS EXISTS (trimcrae, 2026-08-08): "do we actually have any evidence that that's the
consensus view? Or are we just targeting one or two papers to refute them, without knowing if
they're widely cited?"

The transcriptional-output manuscript re-reads three primary papers (Filion 2009 / PPARG,
Brenca 2019 / SEMA3C, Kim 2016 / ENO3) plus the cohort paper its circularity flag is about
(Subramanian 2005), and it makes three claims ABOUT THE FIELD that no committed artifact
supports:

  * "Two questions are routinely conflated"                       (manuscript S1.2)
  * "the field's prose does not usually say so"                   (manuscript S4.2)
  * "assumed for three decades but never assembled and tested"    (cover letter)

Those are empirical claims about a literature, and the repository measured none of them. This
probe measures what a $0 metadata fetch can measure, which is not the same as reading the prose:

  A. ANCHOR WEIGHT      - citedByCount per anchor paper, so "one or two papers" can be graded.
  B. WHO CITES THEM     - CITES:<pmid>_MED, split by PUB_TYPE:"Review" and by whether the citing
                          paper is an EMC paper. An EMC REVIEW citing the anchor is the closest
                          $0 proxy for "the field restates this as established".
  C. FIELD DENOMINATOR  - the EMC literature's own citation distribution and review corpus, so an
                          anchor's count is read against its field rather than in the abstract.
  D. RESTATEMENT        - does the EMC literature (and its reviews specifically) name PPARG /
                          SEMA3C / ENO3 at all?
  E. PRIOR ASSEMBLY     - has anyone already assembled an NR4A3-fusion target list? This is the
                          cover letter's "never assembled" claim, which is the most falsifiable
                          of the three and the one that would embarrass the submission.
  F. CISTROME RECHECK   - the manuscript's standing negative (S3.11), re-asked as a hit count.

WHAT THIS CANNOT DO. A hit count is not a reading of prose. It can establish that N EMC reviews
cite Filion 2009; it cannot establish that they restate PPARG as a target rather than citing the
paper for something else. So this probe can REFUTE a consensus claim (nobody cites it; no review
mentions the gene) and can only SUPPORT one weakly. Any sentence written from this output must
say which of the two it is. A zero is evidence of absence ONLY for the exact query beside it.

The dev sandbox's egress proxy 403s www.ebi.ac.uk on CONNECT, so this runs on a GitHub runner
(CLAUDE.md section 6, escape hatch 1). Pure stdlib, same shape as scripts/lit_lane_probe.py.

Output: research/literature/fusion-consensus-probe.json, plus a digest printed to the job log,
which is the delivery channel that cannot be lost to a push race or an artifact-host 403.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OUT = pathlib.Path("research/literature/fusion-consensus-probe.json")

# The EMC disease clause, reused verbatim everywhere so every hit count is comparable and the
# clause can be quoted in the paper. "chordoid sarcoma" is EMC's older name and is in the
# manuscript's own GEO-era sources; both hyphenations of extraskeletal appear in the literature.
EMC = ('("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" '
       'OR "chordoid sarcoma")')

# The four papers the manuscript re-reads. `claim` is what the manuscript does to that paper, so
# a reader of the output can see what a low citation count would and would not undermine.
ANCHORS: list[dict] = [
    {"key": "filion_2009_pparg", "pmid": "18855877",
     "cite": "Filion C, et al. J Pathol 2009;217(1):83-93",
     "claim": "class-A source for PPARG; the manuscript reports its strongest EMC reading as circular "
              "and finds zero promoter-window peaks in four deep NR4A3 cistromes"},
    {"key": "brenca_2019_sema3c", "pmid": "31020999",
     "cite": "Brenca M, et al. J Pathol 2019;249(1):90-101",
     "claim": "class-A source for SEMA3C; the manuscript reports SEMA3C surviving nothing and "
              "reversing sign with the comparator"},
    {"key": "kim_2016_eno3", "pmid": "26310886",
     "cite": "Kim AY, et al. Mol Carcinog 2016",
     "claim": "class-A source for ENO3 (TFG::NR4A3, not EWSR1); the one gene that survives"},
    {"key": "subramanian_2005_cohort", "pmid": "15920699",
     "cite": "Subramanian S, et al. J Pathol 2005;206:433-444",
     "claim": "the GSE4303 cohort paper; the manuscript's circularity flag is that PPARG's "
              "strongest reading is scored on the cohort that first published it"},
]


def anchor_queries(a: dict) -> list[tuple[str, str]]:
    """The five questions asked of every anchor paper.

    `CITES:<pmid>_MED` is Europe PMC's citing-article index. The last two are the ones that
    actually bear on 'is this the consensus': a paper cited 300 times by cardiovascular NR4A
    biologists is not evidence that the EMC field holds anything.
    """
    pmid, k = a["pmid"], a["key"]
    cites = f'CITES:{pmid}_MED'
    return [
        (f"{k}__record", f'EXT_ID:{pmid} AND SRC:MED'),
        (f"{k}__citing_all", cites),
        (f"{k}__citing_reviews", f'{cites} AND PUB_TYPE:"Review"'),
        (f"{k}__citing_emc", f'{cites} AND {EMC}'),
        (f"{k}__citing_emc_reviews", f'{cites} AND {EMC} AND PUB_TYPE:"Review"'),
    ]


CONTEXT_QUERIES: list[tuple[str, str]] = [
    # --- C. field denominator: what does being cited N times MEAN in this literature? ---------
    ("emc_corpus_all", EMC),
    ("emc_corpus_reviews", f'{EMC} AND PUB_TYPE:"Review"'),
    ("emc_corpus_since_2019", f'{EMC} AND (FIRST_PDATE:[2019-01-01 TO 2030-12-31])'),

    # --- D. restatement: is the gene named in the EMC literature at all, and in its reviews? --
    ("restate_pparg", f'{EMC} AND (PPARG OR "PPAR gamma" OR "PPARgamma" OR "peroxisome proliferator-activated receptor gamma")'),
    ("restate_pparg_reviews", f'{EMC} AND (PPARG OR "PPAR gamma" OR "PPARgamma") AND PUB_TYPE:"Review"'),
    ("restate_sema3c", f'{EMC} AND (SEMA3C OR semaphorin)'),
    ("restate_sema3c_reviews", f'{EMC} AND (SEMA3C OR semaphorin) AND PUB_TYPE:"Review"'),
    ("restate_eno3", f'{EMC} AND (ENO3 OR "beta-enolase" OR "beta enolase")'),
    ("restate_eno3_reviews", f'{EMC} AND (ENO3 OR "beta-enolase" OR "beta enolase") AND PUB_TYPE:"Review"'),

    # --- E. prior assembly: the cover letter's "never assembled" claim ------------------------
    # If a review has already tabulated NR4A3-fusion target genes, "never assembled" is false and
    # the submission needs rewording. This is the query most likely to return an unwelcome answer,
    # which is why it is here rather than left to a reviewer.
    ("prior_target_assembly",
     '(NR4A3 OR "NOR-1" OR "NOR1" OR "EWS/NOR1" OR "EWSR1-NR4A3" OR "EWSR1::NR4A3" OR "TEC oncoprotein") '
     'AND ("target gene" OR "target genes" OR "downstream target" OR "downstream targets" '
     'OR "transcriptional targets" OR "transcriptional program" OR "transcriptional programme")'),
    ("prior_target_assembly_emc",
     f'{EMC} AND ("target gene" OR "target genes" OR "downstream target" OR "downstream targets" '
     'OR "transcriptional targets" OR "transcriptional program" OR "transcriptional programme")'),
    ("prior_target_assembly_reviews",
     '(NR4A3 OR "NOR-1" OR "EWS/NOR1" OR "EWSR1-NR4A3" OR "EWSR1::NR4A3") '
     'AND ("target gene" OR "target genes" OR "downstream targets" OR "transcriptional targets") '
     'AND PUB_TYPE:"Review"'),

    # --- the driver premise itself: is "the fusion is an aberrant TF" actually stated? --------
    ("driver_premise",
     f'{EMC} AND ("aberrant transcription factor" OR "chimeric transcription factor" '
     'OR "transcriptional activator" OR "aberrant transcriptional" OR "transactivation domain")'),

    # --- G. the date under "the hypothesis is thirty years old" (manuscript S1.2) -------------
    # That figure rests on the fusion's cloning date, and the repository holds NO source for it:
    # a draft's 1995 attribution was withdrawn during preparation because its PMID traced to no
    # held source (manuscript Appendix A), and nothing replaced it. So the manuscript currently
    # carries a dated claim with no anchor, which is the same shape as the defect gate 4 of
    # preflight exists to catch — it escapes only because a bare year carries no identifier.
    # These queries recover the primary cloning papers so the date can be anchored or dropped.
    ("fusion_cloning_primary",
     '(("EWS" OR EWSR1) AND (NOR1 OR "NOR-1" OR TEC OR NR4A3) AND (fusion OR chimeric OR "t(9;22)")) '
     'AND (FIRST_PDATE:[1993-01-01 TO 1999-12-31])'),
    ("fusion_cloning_emc",
     f'{EMC} AND (FIRST_PDATE:[1993-01-01 TO 1999-12-31])'),

    # --- F. the standing S3.11 negative, re-asked as a hit count ------------------------------
    ("nr4a3_chromatin_any",
     '(NR4A3 OR "NOR-1" OR "EWS/NOR1" OR "EWSR1-NR4A3" OR "EWSR1::NR4A3" OR "TFG-TEC") '
     'AND ("ChIP-seq" OR "ChIP seq" OR "CUT&RUN" OR "CUT&Tag" OR "ChIP-exo" OR cistrome OR "ATAC-seq")'),
    ("nr4a3_fusion_chromatin",
     '("EWS/NOR1" OR "EWSR1-NR4A3" OR "EWSR1::NR4A3" OR "TAF15-NR4A3" OR "TFG-TEC" OR "TFG-NR4A3") '
     'AND ("ChIP-seq" OR "CUT&RUN" OR "CUT&Tag" OR cistrome OR "genome-wide" OR "ChIP-chip")'),
]


# ⛔ KNOWN-POSITIVE CONTROL FOR THE `CITES:` SYNTAX.
# Every "is this the consensus" number below is a hitCount on a CITES: query. If that field name,
# the `_MED` suffix or the index itself is wrong, EVERY such query returns hitCount 0 — and 0 reads
# as "nobody cites this paper", which is the strongest possible version of the answer and completely
# false. That is CLAUDE.md §4's absent-reading-as-absence failure with the sign flipped, so it gets a
# control rather than a comment: Wilson 1991 (Science, the NBRE paper, cited in this manuscript's own
# reference list as ref 11) is a 1991 Science paper with citations in the high hundreds. If it comes
# back at or below this floor, the SYNTAX is broken, not the literature, and the run fails loudly
# instead of publishing a page of zeros.
CONTROL_PMID = "1902986"          # Wilson TE, et al. Science 1991;252:1296-1300 — the NBRE.
CONTROL_FLOOR = 50                # far below its true count; this tests plumbing, not popularity.


def fetch(query: str, page_size: int = 25, retries: int = 4) -> dict:
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "resultType": "core",
        "sort": "CITED desc",
    })
    url = f"{BASE}?{params}"
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-consensus-probe/1.0"})
            with urllib.request.urlopen(req, timeout=90) as fh:
                return json.loads(fh.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - report, do not mask
            last = exc
            time.sleep(2 + 3 * attempt)
    return {"__error__": f"{type(last).__name__}: {last}"}


def slim(rec: dict) -> dict:
    return {
        "pmid": rec.get("pmid"),
        "doi": rec.get("doi"),
        "title": (rec.get("title") or "").strip().rstrip("."),
        "journal": (rec.get("journalInfo") or {}).get("journal", {}).get("title")
        or rec.get("journalTitle"),
        "year": rec.get("pubYear"),
        "cited_by": rec.get("citedByCount"),
        "type": rec.get("pubType"),
    }


def run(queries: list[tuple[str, str]], out: dict) -> int:
    errors = 0
    for key, query in queries:
        data = fetch(query)
        if "__error__" in data:
            errors += 1
            out["queries"][key] = {"query": query, "error": data["__error__"]}
            print(f"[ERR ] {key}: {data['__error__']}", file=sys.stderr)
            continue
        results = (data.get("resultList") or {}).get("result", []) or []
        out["queries"][key] = {
            "query": query,
            "hit_count": data.get("hitCount"),
            "returned": len(results),
            "top": [slim(r) for r in results],
        }
        print(f"[ok  ] {key}: hitCount={data.get('hitCount')} returned={len(results)}")
        time.sleep(0.4)
    return errors


def main() -> int:
    out: dict = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "Europe PMC REST search API",
        "asks": (
            "Is the view the transcriptional-output manuscript re-reads actually held by the field, "
            "or is the manuscript re-reading one or two papers nobody cites? Raised by trimcrae "
            "2026-08-08 against research/manuscripts/nr4a3-fusion-transcriptional-output.md."
        ),
        "what_this_cannot_conclude": (
            "A hit count is not a reading of prose. A citing review is evidence that the anchor is "
            "in the field's reference lists, NOT that the review restates the target claim - it may "
            "cite the paper for the cohort, the clinical series or the fusion biology. This probe "
            "can REFUTE a consensus claim outright (nothing cites it; no review names the gene) and "
            "can only support one weakly. Every zero is evidence of absence for its exact query only, "
            "and Europe PMC's CITES: index is not complete."
        ),
        "anchors": ANCHORS,
        "emc_clause": EMC,
        "queries": {},
    }

    control_q = [("__control_cites_syntax", f'CITES:{CONTROL_PMID}_MED')]
    errors = run(control_q, out)
    ctl = out["queries"]["__control_cites_syntax"]
    ctl_hits = ctl.get("hit_count")
    ctl_ok = (not ctl.get("error")) and isinstance(ctl_hits, int) and ctl_hits >= CONTROL_FLOOR
    out["cites_syntax_control"] = {
        "pmid": CONTROL_PMID,
        "floor": CONTROL_FLOOR,
        "hit_count": ctl_hits,
        "passed": ctl_ok,
        "means": ("CITES: resolves, so a zero below is a real zero."
                  if ctl_ok else
                  "CITES: DID NOT RESOLVE — every citing count below is meaningless and must not be "
                  "read as evidence that a paper is uncited."),
    }

    for a in ANCHORS:
        errors += run(anchor_queries(a), out)
    errors += run(CONTEXT_QUERIES, out)
    total = 1 + sum(len(anchor_queries(a)) for a in ANCHORS) + len(CONTEXT_QUERIES)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT} ({OUT.stat().st_size} bytes); {errors}/{total} query error(s)")

    # The job log is the one channel readable from the dev sandbox: a push to a shared ref can be
    # lost to a race, a new ref is refused for want of the `workflows` scope, and the artifact host
    # 403s at the egress proxy. All three measured 2026-08-07 (scripts/lit_lane_probe.py).
    top_n = int(os.environ.get("CONSENSUS_PROBE_DIGEST_N", "6"))
    print("\n===BEGIN CONSENSUS-PROBE-DIGEST===")
    print(f"## CONTROL CITES:{CONTROL_PMID}_MED hits={ctl_hits} floor={CONTROL_FLOOR} "
          f"-> {'PASS' if ctl_ok else 'FAIL'}")
    if not ctl_ok:
        print("   ⛔ READ NO CITING COUNT BELOW. The CITES: index did not resolve, so every count "
              "is a plumbing artifact and a zero is not a reading of absence.")

    print("\n-- A/B. ANCHOR WEIGHT: how cited, and by whom --")
    for a in ANCHORS:
        rec = out["queries"].get(f"{a['key']}__record", {})
        top = (rec.get("top") or [{}])[0] if not rec.get("error") else {}
        counts = {}
        for suffix in ("citing_all", "citing_reviews", "citing_emc", "citing_emc_reviews"):
            r = out["queries"].get(f"{a['key']}__{suffix}", {})
            counts[suffix] = "ERR" if r.get("error") else r.get("hit_count")
        print(f"## {a['key']}\tPMID:{a['pmid']}\t{a['cite']}")
        print(f"   citedByCount={top.get('cited_by')}\tyear={top.get('year')}\ttype={top.get('type')}")
        print("   citing: all={citing_all}  reviews={citing_reviews}  EMC={citing_emc}  "
              "EMC-reviews={citing_emc_reviews}".format(**counts))
        emc_rev = out["queries"].get(f"{a['key']}__citing_emc_reviews", {})
        for r in (emc_rev.get("top") or [])[:top_n]:
            print("     EMCrev PMID:{pmid} | {year} | {journal} | {title}".format(
                pmid=r.get("pmid") or "-", year=r.get("year") or "-",
                journal=(r.get("journal") or "-")[:34], title=(r.get("title") or "-")[:88]))

    print("\n-- C/D/E/F. CONTEXT --")
    for key, q in CONTEXT_QUERIES:
        rec = out["queries"].get(key, {})
        if rec.get("error"):
            print(f"## {key}\tERROR\t{rec['error']}")
            continue
        print(f"## {key}\thits={rec.get('hit_count')}\tq={q[:150]}")
        for r in (rec.get("top") or [])[:top_n]:
            print("   - PMID:{pmid} | {year} | {journal} | {title} | cited:{cited_by} | {type}".format(
                pmid=r.get("pmid") or "-", year=r.get("year") or "-",
                journal=(r.get("journal") or "-")[:32], title=(r.get("title") or "-")[:92],
                cited_by=r.get("cited_by"), type=(r.get("type") or "-")[:28]))
    print("===END CONSENSUS-PROBE-DIGEST===")

    # Fail the run on a broken control. A green run whose citing counts are all plumbing zeros is
    # worse than a red one, because the artifact would read as a finished measurement.
    if not ctl_ok:
        print(f"::error::CITES: control failed (PMID {CONTROL_PMID} returned {ctl_hits}, "
              f"floor {CONTROL_FLOOR}) — the citing counts in this run are not readable",
              file=sys.stderr)
        return 2
    return 1 if errors == total else 0


if __name__ == "__main__":
    raise SystemExit(main())
