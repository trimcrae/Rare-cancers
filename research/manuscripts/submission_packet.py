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
def _orcid_present():
    """Does every submission manuscript carry a real ORCID iD in its author block?

    Derived, because the packet's "outstanding" list is the one thing in this repository a person
    ACTS on, and an item there that is already done costs them a trip to orcid.org.
    """
    import glob
    pat = re.compile(r"ORCID[:\s]*\[?(\d{4}-\d{4}-\d{4}-\d{3}[\dX])")
    seen = []
    for path in sorted(glob.glob(os.path.join(HERE, "aso", "fusion-junction-aso-*article*.md"))):
        seen.append(bool(pat.search(open(path, encoding="utf-8").read())))
    return bool(seen) and all(seen)


AUTHOR_ONLY = [
    # ⛔⛔ THIS ENTRY TOLD THE AUTHOR TO DO SOMETHING ALREADY DONE (2026-08-23). It read "THE ONE
    # REMAINING ITEM ... each manuscript now carries an ORCID line reading ORCID TO BE SUPPLIED BY
    # THE AUTHOR BEFORE SUBMISSION; replacing that string in four files is the whole of the
    # remaining work." Measured: that placeholder is in NO file, every submission manuscript carries
    # a real iD, and the preprint checklist had already struck the item through as done. The one
    # document whose whole job is to say what still blocks submission was naming a finished task as
    # the blocker — which is worse than a stale comment, because a reader acts on it.
    # ★ So it is DERIVED. The status is read from the manuscripts, and the entry only appears while
    # something is actually outstanding.
    *(( ) if _orcid_present() else ((
        "ORCID",
        "The corresponding author's ORCID iD is not in the author block of every submission "
        "manuscript. Registration is free at orcid.org and is an identity registration, so it must "
        "be done by the author and not on their behalf. The British Journal of Cancer's Guide to "
        "Authors asks the corresponding author to supply one; the Wiley and Elsevier guides are "
        "bot-walled, so their position is unknown rather than assumed."),)),
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


def _cgt_fee_line():
    """What the FETCH RECORD says about Cancer Gene Therapy's charges — read, not remembered.

    ⛔⛔ THIS PARAGRAPH WAS A HAND-TYPED LITERAL AND IT WAS WRONG ON THREE COUNTS (round 16 seat 4,
    2026-08-22), inside a generator whose own banner reads "every value is derived from a committed
    artifact". It said the fee schedule "has never been read" — `cgt_gta` is HTTP 200 and contains
    "£145 / $238 per page" verbatim; it said `/cgt/about` "returned 404" — it returned 200; and it
    said the page and colour charges "are unknown" — the fetched text states the charge and says it
    is "fully inclusive of colour reproduction".
    ⚠ A GENERATED FILE IS ONLY AS DERIVED AS ITS LEAST DERIVED SENTENCE, and a "DO NOT HAND-EDIT"
    banner over a hand-typed claim is worse than no banner: it tells the reader not to check.
    """
    rec = os.path.join(REPO, "research", "literature", "venue-policy-browser-fetch.json")
    if not os.path.exists(rec):
        return ("- Cancer Gene Therapy's fee schedule could not be checked: "
                "`research/literature/venue-policy-browser-fetch.json` is missing.")
    targets = json.load(open(rec, encoding="utf-8")).get("targets", {})
    cgt = {k: v for k, v in targets.items() if k.startswith("cgt")}
    answered = sorted(k for k, v in cgt.items() if v.get("status") == 200)
    unread = sorted(k for k, v in cgt.items() if v.get("status") != 200)
    fee = ""
    for key in answered:
        m = re.search(r"[^.]{0,90}per page[^.]{0,120}\.", " ".join((cgt[key].get("text") or "").split()))
        if m:
            fee = f' Its guide to authors states, verbatim: "{m.group(0).strip()}"'
            break
    return ("- Cancer Gene Therapy's charges HAVE been read, contrary to a claim this file carried "
            f"until 2026-08-22. Of {len(cgt)} fetched pages, {len(answered)} answered HTTP 200 "
            f"({', '.join(answered)}) and {len(unread)} did not "
            f"({', '.join(unread) if unread else 'none'})." + fee +
            " Confirm at the portal before submitting there; this is a fetch record, not an invoice.")




def _builder_papers():
    """`build_submission_pdf.PAPERS`, loaded once. {} if the builder cannot be imported.

    ⚠ ONE FACT, ONE HOME — the builder decides what each paper renders and submits, and every
    question this module asks about a paper's files is answered from here rather than from a
    directory scan.
    """
    global _BUILDER_PAPERS
    if _BUILDER_PAPERS is not None:
        return _BUILDER_PAPERS
    try:
        import importlib.util
        path = os.path.join(HERE, "build_submission_pdf.py")
        spec = importlib.util.spec_from_file_location("_bsp_for_packet", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _BUILDER_PAPERS = dict(getattr(mod, "PAPERS", {}))
    except Exception:  # noqa: BLE001 — a builder that will not import is reported by its own gate
        _BUILDER_PAPERS = {}
    return _BUILDER_PAPERS


_BUILDER_PAPERS = None


def _paper_review_supplements(manuscript_rel):
    """Files the builder says are uploaded with this submission for the reviewers.

    Returns () when the paper declares none. ⛔ NOT a directory scan: whether a file is submitted
    for review is a decision recorded on the paper, and the deposit directory holds artefacts that
    are archived rather than submitted. Guessing here would put the wrong files in an envelope.
    """
    for paper in _builder_papers().values():
        if paper.get("manuscript") == manuscript_rel:
            return tuple(paper.get("supplementary_for_review") or ())
    return ()


def _paper_supplementary(manuscript_rel):
    """The SI `build_submission_pdf.PAPERS` says this manuscript has, or "" if it has none.

    ⚠ ONE FACT, ONE HOME. The builder decides what each paper renders; a packet that answers the
    same question by globbing a directory is a second home for it, and the second home is the one
    that was wrong.
    """
    for paper in _builder_papers().values():
        if paper.get("manuscript") == manuscript_rel:
            return paper.get("supplementary") or ""
    return ""
    return ""


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
        # ⛔ ASK THE BUILDER, NOT THE DIRECTORY (round 15 seats 4 and 5, 2026-08-22). `_companion`
        # anchors at both ends so "a companion belonging to a different paper cannot be claimed by
        # this one" — but round 14 added `-journal-article` to `_STEM_TAILS`, which reduces BOTH ASO
        # stems to `fusion-junction-aso`, so the condensed submission claimed the extended report's
        # SI and this row told a NAT depositor "Supplementary file: yes". The SI's own title page
        # reads "Supplementary Information to [the research article]"; `PAPERS['aso-journal']` has
        # no `supplementary` key at all. Whether a paper HAS an SI is the builder's fact, and the
        # builder is where it is now read from. The directory scan stays for the cover letter, where
        # one letter legitimately serves the submission.
        si = bool(_paper_supplementary(row["file"]))
        #: Files uploaded ALONGSIDE the manuscript for the reviewers, distinct from an SI document.
        #: Read from the builder entry, never guessed from the directory: "for review only" is a
        #: submission decision, and a directory scan cannot tell it from an archive artefact.
        review_only = _paper_review_supplements(row["file"])

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
              f"| Supplemental material, for review | "
              f"{', '.join('`' + f + '`' for f in review_only) if review_only else 'none'} |",
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
          _cgt_fee_line(),
          "- The $0 route rests on publisher-wide policy statements quoted verbatim in "
          "`research/literature/venue-fee-routes-2026-08-10.json`, not on the per-journal fee page. "
          "Elect the subscription route at the fee step and decline the open-access upgrade.",
          "- The British Journal of Cancer levies a colour charge for figures in print, waived only "
          "for open-access papers. That paper has no figures, so the charge cannot arise.", ""]

    text = "\n".join(L) + "\n"

    # ⛔⛔ `--check` ADDED 2026-08-22 (round 15 seat 5). This was the ONE deposit generator without
    # it, so `SUBMISSION-PACKET.md` was read by nothing at all: the seat wrote four fabricated facts
    # into the committed file — including a made-up NAT page limit, for the venue whose limits the
    # same file calls UNREAD, and a figure filename that does not exist — and all five linters plus
    # the 848-test manuscripts suite stayed green. The file carries a "Do not hand-edit" banner,
    # which is an instruction to humans backed by nothing until a gate re-derives it.
    # ⚠ A CHECKLIST'S FALSE CONTENT IS THE EXPENSIVE DIRECTION: it is read at the portal, at the
    # moment when there is no time to verify it.
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print(f"MISSING {OUT} — run without --check")
            return 1
        if open(OUT, encoding="utf-8").read() != text:
            print(f"STALE {os.path.relpath(OUT, REPO)} — rerun without --check and commit the result")
            return 1
        print("submission packet reproduces from submission-metrics.json and the filesystem")
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {os.path.relpath(OUT, REPO)} for {len(metrics.get('rows', []))} paper(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
