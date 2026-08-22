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


def figures_for(stem, declared=()):
    """The figure files to upload, as (basename, raster present, vector present).

    ⛔ AN EMBED SCAN ALONE REPORTS ZERO FIGURES FOR A PAPER THAT HAS THREE (2026-08-12). This
    matched `![...](path)` only, which is right for a manuscript that embeds its images and wrong
    for one that carries a Figure legends section and ships the files beside it. The ASO paper is
    the second kind, so this printed "none; this paper's display items are all tables" — on the
    line that IS the portal upload checklist. A checklist that omits the deliverables is worse than
    no checklist, because it reads as having been checked.
    ⚠ `declared` comes from `submission_metrics.FIGURE_FILES` via the row, because no committed
    link exists between "Figure 1" in the prose and a filename. A missing declared file is reported
    MISSING rather than dropped.
    """
    md = os.path.join(HERE, stem + ".md")
    if not os.path.exists(md):
        return []
    body = open(md, encoding="utf-8").read()
    out = []
    for ref in declared or ():
        p = os.path.normpath(os.path.join(HERE, ref))
        base = os.path.splitext(p)[0]
        out.append({"file": os.path.basename(ref),
                    "png": any(os.path.exists(base + e) for e in (".png", ".tif", ".tiff")),
                    "vector": any(os.path.exists(base + e) for e in (".pdf", ".eps", ".svg"))})
    for ref in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", body):
        # ⚠ RESOLVED AGAINST THE MANUSCRIPT'S OWN DIRECTORY, not against HERE. Manuscripts moved into
        # per-route folders on 2026-08-12, so their figure links are `../figures/x.png`; joining those
        # to HERE would look for a directory that does not exist and report every figure MISSING.
        png = os.path.normpath(os.path.join(os.path.dirname(md), ref))
        out.append({"file": os.path.basename(ref),
                    "png": os.path.exists(png),
                    "vector": any(os.path.exists(png[:-4] + e) for e in (".pdf", ".eps", ".svg"))})
    return out


#: Suffixes a manuscript stem may carry that its companion documents drop. Ordered longest-first so
#: `-research-article` is stripped before a hypothetical `-article` could match a prefix of it.
#: ⛔ `-journal-article` ADDED 2026-08-22 (round 14 seat 5). The condensed NAT submission's stem is
#: `fusion-junction-aso-journal-article`, which matched none of these, so `_companion` looked for a
#: sibling starting with the FULL stem and the row printed `Cover letter | MISSING` beside a letter
#: sitting in the same directory — the same false negative this list was created to fix, one paper
#: later. The expensive direction, again: a checklist telling a depositor to write a document that
#: already exists.
_STEM_TAILS = ("-research-article", "-journal-article", "-manuscript", "-paper")


def _companion(stem, suffixes):
    """The sibling document playing `role` for this manuscript, or "" if there is none.

    ⛔ RETURNS THE PATH IT FOUND, NOT A BOOLEAN, so the generated row can print the real filename —
    a checklist that says "present" without saying WHICH file is one lookup short of useless, and
    the previous version printed a name it had CONSTRUCTED rather than one it had found, which is
    how it managed to print a filename that did not exist beside a verdict that was wrong.
    ⚠ Matching is anchored at BOTH ends — `startswith(base)` and `endswith(suffix)` — so a companion
    belonging to a different paper in the same directory cannot be claimed by this one.
    """
    d = os.path.join(HERE, os.path.dirname(stem))
    base = os.path.basename(stem)
    for tail in _STEM_TAILS:
        if base.endswith(tail):
            base = base[: -len(tail)]
            break
    if not os.path.isdir(d):
        return ""
    for name in sorted(os.listdir(d)):
        if name.startswith(base) and any(name.endswith(s) for s in suffixes):
            return os.path.join(os.path.dirname(stem), name)
    return ""


def main():
    metrics = _load("research/manuscripts/submission-metrics.json") or {}
    fees = _load("research/literature/venue-fee-routes-2026-08-10.json") or {}
    verdicts = fees.get("verdicts", {})
    venue_key = {"Genes, Chromosomes and Cancer (Wiley)": "GCC",
                 "Critical Reviews in Oncology/Hematology (Elsevier)": "CROH",
                 "British Journal of Cancer (Springer Nature)": "BJC",
                 # ⚠ CGT HAS NO VERDICT IN THE FEE ARTIFACT, AND THE ROW MUST SAY SO RATHER THAN
                 # OMIT THE PAPER. `verdicts.get(vk, {})` degrades to "not recorded", which is the
                 # true state: nature.com/cgt/open-access answered 200 and establishes that open
                 # access is the paid upgrade, so there is no APC on the subscription route — but
                 # every author-facing CGT path tried returned 404, so page, colour and
                 # ⚠ SUPERSEDED 2026-08-22, trimcrae: "NAT is the venue. It's not disqualified."
                 # This file previously carried "Nucleic Acid Therapeutics passed the same APC test
                 # and was then disqualified by mandatory page charges of $90/page" in its
                 # not-verified section, while the packet's own venue table targeted the journal
                 # article AT Nucleic Acid Therapeutics -- a file recommending a venue it elsewhere
                 # called disqualified. The page charge is a real cost to plan the length against,
                 # not a disqualification, and it is why the article carries a page budget.
                 # over-length charges are UNREAD. Nucleic Acid Therapeutics passed the APC test
                 # and was then disqualified by $90/page, so an unread fee schedule is the live
                 # risk on this submission and not a formality.
                 "Cancer Gene Therapy (Springer Nature)": "CGT"}

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
        # ⛔ THIS REPORTED "MISSING" FOR FILES THAT EXIST (measured 2026-08-17). The lookup was
        # `stem + "-cover-letter.md"`, and `stem` is the MANUSCRIPT's full basename — so for
        # `aso/fusion-junction-aso-research-article.md` it asked for
        # `aso/fusion-junction-aso-research-article-cover-letter.md`, while the real file is
        # `aso/fusion-junction-aso-cover-letter.md`. Four of the five papers happened to name their
        # letter after the manuscript stem exactly, so four rows were right and the fifth read
        # MISSING on a 9.4 kB file sitting beside it. The SI lookup had the same shape and the same
        # outcome: `-SI.md`/`-si.md` next to a real `-supplementary-information.md`.
        # ⚠ A SUBMISSION CHECKLIST'S FALSE NEGATIVE IS THE EXPENSIVE DIRECTION — it tells the
        # depositor to write a document that already exists, and this one had been printing MISSING
        # into a generated packet that four other rows made look trustworthy.
        # ⭐ Fixed by asking the DIRECTORY what is there rather than guessing one name: any sibling
        # file whose name starts with a shortened stem and ends in the role's suffix counts. The
        # shortened stem drops a trailing `-research-article`/`-manuscript`/`-paper`, which is the
        # only thing that differed.
        letter = _companion(stem, ("-cover-letter.md",))
        # ⚠ A PREPRINT SERVER TAKES NO COVER LETTER, so "MISSING" would be a false demand and naming
        # the journal letter here would be a false claim about what this deposit carries. Both ASO
        # rows now resolve the same file — there is one cover letter for this work and it is the
        # journal submission's — and this is what keeps the preprint row from claiming it.
        preprint = "preprint" in row["venue"].lower()
        figs = figures_for(stem, row.get("figure_files") or ())
        si = bool(_companion(stem, ("-SI.md", "-si.md", "-supplementary-information.md")))

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
              f"| Cover letter | {'n/a (preprint deposit)' if preprint else ('`' + letter + '`' if letter else 'MISSING')} |",
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
          "- Cancer Gene Therapy is a separate and worse case, because it is a CHOSEN venue whose "
          "fee schedule has never been read. nature.com answers, and its open-access page was read "
          "at HTTP 200 and establishes that open access is the optional paid upgrade — so the "
          "subscription route carries no article processing charge. But `/cgt/for-authors`, "
          "`/cgt/submission-guidelines` and `/cgt/about` all returned 404, so that journal's page, "
          "colour and over-length charges are unknown. Load the journal's author guidelines in an "
          "ordinary browser and confirm the full fee schedule before submitting there.",
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
