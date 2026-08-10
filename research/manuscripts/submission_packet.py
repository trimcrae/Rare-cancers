#!/usr/bin/env python3
"""Generate the per-paper submission packet: everything a portal asks for, in order.

WHY. By the time four manuscripts were journal-ready, the facts needed to actually submit them were
spread across six artifacts and four editorial comment blocks: the venue and article type in one
place, the fee route in another, the measured word counts in a third, the cover letter in a fourth,
the figure inventory nowhere. Assembling that by hand at submission time is how a detail gets
missed, and it is exactly the re-derivation CLAUDE.md rule 1 exists to stop.

⛔ EVERY VALUE HERE IS DERIVED, NEVER TYPED. Counts come from submission-metrics.json, the fee route
from venue-fee-routes-2026-08-10.json, figures from the filesystem, cover letters from their
presence on disk. If a number here is wrong, the artifact is wrong and this regenerates from it.

⚠ IT LISTS WHAT IS OUTSTANDING AS PROMINENTLY AS WHAT IS DONE. A packet that only shows green is a
packet that gets trusted past the point it should be.

    python3 research/manuscripts/submission_packet.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "SUBMISSION-PACKET.md")

#: Things only the author can supply. Listed per paper so none is discovered at the portal.
#: Things only the author can supply.
#: ⛔ TWO OF THE THREE ENTRIES HERE WERE ASSERTED AND ONE WAS WRONG (2026-08-10). trimcrae asked "I
#: have to suggest my own reviewers?" — a fair question, because I had written that most venues ask
#: for three to five without checking any of them. The British Journal of Cancer's Guide to Authors
#: is the one that answers on plain HTTP, and it contains ZERO occurrences of "suggest" and zero of
#: "oppose" or "exclude": it asks for no reviewer names at all. The same read also corrected the
#: address item — the guide asks for affiliations and a corresponding-author e-mail, never a postal
#: address. The Wiley and Elsevier guides remain unreadable, so their requirements are unknown
#: rather than assumed either way.
AUTHOR_ONLY = [
    ("ORCID", "REQUIRED, and this one is verified: the British Journal of Cancer's Guide to Authors "
              "states that 'the corresponding author should also provide an ORCID identifier'. Free "
              "at orcid.org. The repository carries none and cannot invent one."),
    ("Corresponding-author e-mail and affiliation", "The BJC title-page specification asks for full "
              "author names and affiliations together with the corresponding author's e-mail. The "
              "manuscripts give the e-mail and state 'independent researcher, unaffiliated', which "
              "is an affiliation statement. No postal address is requested."),
    ("Suggested reviewers", "PROBABLY NOT NEEDED, and previously overstated here. BJC's Guide to "
              "Authors does not mention suggesting, opposing or excluding reviewers anywhere. Some "
              "portals offer an optional field; where it is optional it can be left blank. The "
              "Wiley and Elsevier guides could not be retrieved, so their position is unknown. If a "
              "portal does ask, the candidates are in each paper's own reference list, and the "
              "choice is a conflict-of-interest judgement only the author can make."),
]


def _load(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def figures_for(stem):
    md = os.path.join(HERE, stem + ".md")
    if not os.path.exists(md):
        return []
    body = open(md, encoding="utf-8").read()
    out = []
    for ref in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", body):
        rel = ref.lstrip("./")
        png = os.path.join(HERE, rel)
        out.append({"file": os.path.basename(rel),
                    "png": os.path.exists(png),
                    "vector": any(os.path.exists(png[:-4] + e) for e in (".pdf", ".eps", ".svg"))})
    return out


def main():
    metrics = _load("research/manuscripts/submission-metrics.json") or {}
    fees = _load("research/literature/venue-fee-routes-2026-08-10.json") or {}
    verdicts = fees.get("verdicts", {})
    venue_key = {"Genes, Chromosomes and Cancer (Wiley)": "GCC",
                 "Critical Reviews in Oncology/Hematology (Elsevier)": "CROH",
                 "British Journal of Cancer (Springer Nature)": "BJC"}

    L = ["---", "id: DOC-SUBMISSION-PACKET",
         "title: \"Submission packet — what each journal portal asks for, and what is still missing\"",
         "level: L3", "kind: generated", "status: generated",
         "generator: research/manuscripts/submission_packet.py",
         "purpose: >-", "  Assemble, per paper, every fact a journal submission portal asks for, so",
         "  none is re-derived from six artifacts at the moment of submitting.",
         "scope: >-",
         "  Submission logistics only, for the four manuscripts in submission form. It reports no",
         "  result, asserts nothing about any disease or agent, and is not a scientific record.",
         "audience: [maintainers]", "date: 2026-08-10", "last_verified: 2026-08-10", "---", "",
         "# Submission packet", "",
         "> Generated by `research/manuscripts/submission_packet.py`. Do not hand-edit: every value "
         "is derived from a committed artifact, and a hand-edit will be overwritten.", ""]

    for row in metrics.get("rows", []):
        stem = row["file"][:-3]
        m, lim = row["measured"], row["limits"]
        vk = venue_key.get(row["venue"], "")
        v = verdicts.get(vk, {})
        letter = os.path.exists(os.path.join(HERE, stem + "-cover-letter.md"))
        figs = figures_for(stem)
        si = os.path.exists(os.path.join(HERE, stem + "-SI.md")) or \
            os.path.exists(os.path.join(HERE, stem + "-si.md"))

        L += [f"## {row['venue']}", "", f"**Manuscript** `{row['file']}`", ""]
        L += ["| field | value |", "|---|---|",
              f"| Word count, main text | {m['main_words']} "
              f"{'(limit ' + str(lim['main_words']) + ')' if lim.get('main_words') else '(no limit found)'} |",
              f"| Abstract | {m['abstract_words']} words "
              f"{'(limit ' + str(lim['abstract_words']) + ')' if lim.get('abstract_words') else ''} |",
              f"| Display items | {m['display_items']} ({m['figures']} figures, {m['tables']} tables)"
              f"{' (limit ' + str(lim['display_items']) + ')' if lim.get('display_items') else ''} |",
              f"| References | {m['references']}"
              f"{' (limit ' + str(lim['references']) + ')' if lim.get('references') else ''} |",
              f"| Cover letter | {'`' + stem + '-cover-letter.md`' if letter else 'MISSING'} |",
              f"| Supplementary file | {'yes' if si else 'none'} |",
              f"| Fee route | {v.get('zero_dollar_route', 'not recorded')} |", ""]
        if row.get("over_limit"):
            L += ["> **Over a stated limit:** " + "; ".join(row["over_limit"]), ""]
        L += [f"⚠ Limits provenance: {row.get('limits_provenance', 'unknown')}.", ""]
        if figs:
            L += ["**Figures to upload**", ""]
            for f in figs:
                L.append(f"- `{f['file']}` — raster {'present' if f['png'] else 'MISSING'}, "
                         f"vector {'present' if f['vector'] else 'MISSING'}")
            L.append("")
        else:
            L += ["**Figures to upload** — none; this paper's display items are all tables.", ""]

    L += ["## Outstanding for every paper, and only the author can supply these", ""]
    for name, why in AUTHOR_ONLY:
        L += [f"- **{name}.** {why}"]
    L += ["", "## Not verified, and stated rather than assumed", "",
          "- The per-journal author guidelines could not be retrieved: Wiley serves a JavaScript "
          "bot challenge and ScienceDirect blocks the datacenter IP, and both persist under a real "
          "headless browser from CI. Word, abstract and display-item limits above are "
          "search-derived except for the British Journal of Cancer row, which was read from the "
          "journal's own page. Confirm each at the portal, where the pages load normally.",
          "- The $0 route rests on publisher-wide policy statements quoted verbatim in "
          "`research/literature/venue-fee-routes-2026-08-10.json`, not on the per-journal fee page. "
          "Elect the subscription route at the fee step and decline the open-access upgrade.",
          "- The British Journal of Cancer levies a colour charge for figures in print, waived only "
          "for open-access papers. That paper has no figures, so the charge cannot arise.", ""]

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(OUT, REPO)} for {len(metrics.get('rows', []))} paper(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
