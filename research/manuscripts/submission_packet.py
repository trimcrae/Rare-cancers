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
    ("ORCID", "THE ONE REMAINING ITEM, and the only thing in this packet an agent cannot do. "
              "The British Journal of Cancer's Guide to Authors states that the corresponding "
              "author should also provide an ORCID identifier; the Wiley and Elsevier author "
              "guides are bot-walled, so their position is unknown rather than assumed. "
              "Registration is free at orcid.org and takes a few minutes, and it is an identity "
              "registration, so it must be done by the author and not on their behalf. Each "
              "manuscript now carries an ORCID line in its author block reading ORCID TO BE "
              "SUPPLIED BY THE AUTHOR BEFORE SUBMISSION; replacing that string in four files is "
              "the whole of the remaining work."),
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


#: ⛔ THE PER-PAPER VIEW CANNOT SEE THE ONE THING THAT SINKS A WHOLE PORTFOLIO (2026-08-10).
#: Every venue decision in this repository was taken one manuscript at a time and each was
#: defensible on its own. Read together, FOUR of five papers came to name the same journal and FOUR
#: to re-analyse the same two GEO series — so three manuscripts would have arrived at one editor,
#: from one unaffiliated author, on the same archival data, each cover letter saying only "not under
#: consideration elsewhere". That reads as salami-slicing, and undisclosed concurrent overlapping
#: submission is an integrity matter rather than a matter of taste: it can decline all three rather
#: than the one that gets noticed. Nothing in this packet showed it, which is why it happened.
#: A packet whose purpose is that nothing is re-derived at the portal must therefore report the
#: SET, not only the rows.
GEO_RE = re.compile(r"\bGSE\d+\b")


def journal_of(venue):
    """The JOURNAL, stripped of any limits-profile qualifier.

    ⛔ THE FIRST VERSION OF THIS SECTION UNDER-REPORTED THE COLLISION IT WAS WRITTEN TO CATCH, AND
    DID IT SILENTLY (2026-08-10). It grouped on the venue label, and one manuscript carries
    "Genes, Chromosomes and Cancer (Wiley), held to a verified proxy envelope" because Wiley blocks
    retrieval of its own limits, so that paper is held to BJC's verified envelope as a proxy. The
    qualifier describes which LIMITS apply; the journal is the same journal. Grouping on the label
    printed three manuscripts at GCC when the true count is four -- an under-report of exactly the
    fact the section exists to surface, in the direction that reassures. Group on the journal.
    """
    return venue.split(", held to")[0].strip()


def portfolio(metrics):
    """Venue concentration and shared-dataset overlap across every submission-form manuscript."""
    venues, series = {}, {}
    for row in metrics.get("rows", []):
        venues.setdefault(journal_of(row["venue"]), []).append(row["file"])
        p = os.path.join(HERE, row["file"])
        if os.path.exists(p):
            for acc in sorted(set(GEO_RE.findall(open(p, encoding="utf-8").read()))):
                series.setdefault(acc, []).append(row["file"])
    collisions = {v: f for v, f in venues.items() if len(f) > 1}
    shared = {a: f for a, f in series.items() if len(f) > 1}
    return venues, collisions, shared


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
         "  Submission logistics only, for the manuscripts in submission form, plus the portfolio",
         "  view of venue concentration and shared datasets that no per-paper row can show. It",
         "  reports no result, asserts nothing about any disease or agent, and is not a scientific",
         "  record.",
         "audience: [maintainers]", "date: 2026-08-10", "last_verified: 2026-08-10", "---", "",
         "# Submission packet", "",
         "> Generated by `research/manuscripts/submission_packet.py`. Do not hand-edit: every value "
         "is derived from a committed artifact, and a hand-edit will be overwritten.", ""]

    venues, collisions, shared = portfolio(metrics)
    L += ["## The portfolio, before the per-paper rows", "",
          "Read the set before submitting any member of it. Every venue choice here was made one "
          "manuscript at a time, and a concentration that no single decision created is exactly "
          "what a receiving editor sees first.", ""]
    L += ["| venue | manuscripts |", "|---|---:|"]
    for v, files in sorted(venues.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        L.append(f"| {v} | {len(files)} |")
    L.append("")
    if collisions:
        L += ["**Venue collisions.** More than one manuscript is aimed at the same journal:", ""]
        for v, files in sorted(collisions.items(), key=lambda kv: -len(kv[1])):
            L.append(f"- **{v}** — " + ", ".join(f"`{f}`" for f in sorted(files)))
        L.append("")
    else:
        L += ["**Venue collisions** — none; every manuscript is aimed at a different journal.", ""]
    if shared:
        L += ["**Shared datasets.** These accessions are re-analysed by more than one manuscript. "
              "Where a shared dataset meets a venue collision, the overlap must be disclosed in "
              "both cover letters, naming the companion manuscript and stating what is shared and "
              "what is distinct:", ""]
        for acc, files in sorted(shared.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            same_venue = len({journal_of(r["venue"]) for r in metrics.get("rows", [])
                              if r["file"] in files}) < len(files)
            flag = " — **and these collide on venue**" if same_venue else ""
            L.append(f"- `{acc}` — " + ", ".join(f"`{f}`" for f in sorted(files)) + flag)
        L.append("")
    else:
        L += ["**Shared datasets** — none; no accession is re-analysed by two manuscripts.", ""]
    L += ["⛔ This section reports the overlap. It does not decide what to do about it: "
          "re-diversifying venues, staggering submissions and cross-disclosing in the cover letters "
          "are author decisions, and disclosure is required whichever is chosen.", ""]

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
