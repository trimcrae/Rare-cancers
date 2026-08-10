#!/usr/bin/env python3
"""Full-text term screen over the retrieved EMC prior-art corpus.

WHY THIS EXISTS. The 2026-08-09 prior-art screen matched titles and abstracts, and said so: an
absence in it is evidence that nothing is INDEXED on a pairing, not that no such work exists, and a
surface-antigen result inside a supplementary table would be invisible to it. The manuscript then
rested a priority sentence on that screen. The full texts the screen could have searched were
already fetched: `emc-prior-art-2026-08-09.json` records 322 records with 238 full-text files on
the `literature-cache` branch. This searches them, which costs nothing and needs no new retrieval.

It answers one question and does not answer a second. It answers: among the retrieved full texts,
how many name this disease or its fusion, how many carry a surface-antigen or immunotherapy term,
how many carry both, and in how many does one of the six antigens the manuscript discusses appear
within 2,000 characters of a mention of the disease. It does NOT answer whether any such work
exists elsewhere: the corpus is one Europe PMC query's return, open-access full text only, and a
result in a subscription-only paper or in a supplementary file is outside it.

    git fetch origin literature-cache
    python3 research/modalities/emc_prior_art_fulltext_screen.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "research", "literature",
                   "emc-prior-art-fulltext-screen-2026-08-10.json")

BRANCH = "origin/literature-cache"
CORPUS = "literature/emc-prior-art-2026-08-09"
WINDOW = 2000

DISEASE = re.compile(
    r"extraskeletal\s+myxoid\s+chondrosarcom|EWSR1[:\-]{1,2}NR4A3|EWS[/-]?CHN|"
    r"TAF15[:\-]{1,2}NR4A3|RBP56[/-]CHN|TFG[:\-]{1,2}NR4A3", re.I)

SURFACE = re.compile(
    r"surfaceom|surface antigen|cell[- ]surface protein|chimeric antigen receptor|\bCAR[- ]T\b|"
    r"radioligand|antibody[- ]drug conjugate|\bADC\b|immunotherap|T[- ]cell engager|bispecific|"
    r"theranostic", re.I)

ANTIGENS = {
    "ALCAM": r"\bALCAM\b|\bCD166\b",
    "CD248": r"\bCD248\b|endosialin|\bTEM1\b",
    "CD276": r"\bCD276\b|B7[- ]H3",
    "FAP": r"\bFAP\b|fibroblast activation protein",
    "PRAME": r"\bPRAME\b",
    "SSTR2": r"\bSSTR2\b|somatostatin receptor",
}


def _git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)


def main(argv):
    listing = _git("ls-tree", "-r", "--name-only", BRANCH)
    if listing.returncode != 0:
        raise SystemExit(f"{BRANCH} is not in the local object store. Run: "
                         f"git fetch origin literature-cache")
    files = sorted(f for f in listing.stdout.split("\n")
                   if f.startswith(CORPUS + "/") and f.endswith(".txt"))
    if not files:
        raise SystemExit(f"no full texts under {BRANCH}:{CORPUS}/")

    patterns = {k: re.compile(v, re.I) for k, v in ANTIGENS.items()}
    disease, surface, both = [], [], []
    near = {k: [] for k in ANTIGENS}
    for path in files:
        text = _git("show", f"{BRANCH}:{path}").stdout
        name = os.path.basename(path)[:-4]
        d, s = bool(DISEASE.search(text)), bool(SURFACE.search(text))
        if d:
            disease.append(name)
        if s:
            surface.append(name)
        if not (d and s):
            continue
        both.append(name)
        for gene, pat in patterns.items():
            for m in DISEASE.finditer(text):
                if pat.search(text[max(0, m.start() - WINDOW): m.end() + WINDOW]):
                    near[gene].append(name)
                    break

    out = {
        "_what": "Full-text term screen over the retrieved EMC prior-art corpus, extending the "
                 "2026-08-09 title-and-abstract screen to the full texts it had already fetched.",
        "_why": "The earlier screen stated its own blind spot and a priority sentence in the "
                "manuscript rested on it. The full texts were in hand, so the blind spot was "
                "closeable at no cost.",
        "_cost": "$0. A branch already in the local object store; no network, no GPU.",
        "_corpus": {"branch": BRANCH, "directory": CORPUS,
                    "n_full_text_files": len(files),
                    "retrieval_artifact": "research/literature/emc-prior-art-2026-08-09.json",
                    "_what_the_retrieval_recorded": "322 records, 238 full-text files. The corpus "
                                                    "directory holds one index file beside the "
                                                    "full texts, which is why the count of .txt "
                                                    "files below is one lower."},
        "_what_this_cannot_show": "That no such work exists. The corpus is one Europe PMC query's "
                                  "return and is open-access full text only, so a result in a "
                                  "subscription-only paper, in a supplementary file not carried "
                                  "in the full text, or under terms this screen does not match, "
                                  "is outside it. An absence here is a measured absence in a "
                                  "named corpus and nothing wider.",
        "_terms": {"disease": DISEASE.pattern, "surface_or_immunotherapy": SURFACE.pattern,
                   "antigens": ANTIGENS, "co_occurrence_window_characters": WINDOW},
        "counts": {
            "full_texts_screened": len(files),
            "naming_the_disease_or_its_fusion": len(disease),
            "carrying_a_surface_or_immunotherapy_term": len(surface),
            "carrying_both": len(both),
            "antigen_within_window_of_a_disease_mention":
                {k: len(v) for k, v in sorted(near.items())},
        },
        "hits": {"carrying_both": both,
                 "antigen_within_window_of_a_disease_mention":
                     {k: v for k, v in sorted(near.items())}},
    }

    if "--check" in argv:
        print(json.dumps(out["counts"], indent=1))
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, REPO)}")
    print(json.dumps(out["counts"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
