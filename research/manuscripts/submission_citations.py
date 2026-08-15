#!/usr/bin/env python3
"""Resolve the submission manuscript's superscripts to PMIDs, renumber them, and emit its references.

⛔ WHY THIS EXISTS, AND WHY IT IS NOT `build_reference_list.py`. That script reads the WORKING
RECORD, which cites bare inline PMIDs, and produces the 74-entry list for it. The submission was
condensed out of that record and cites bare SUPERSCRIPT NUMBERS with no identifier attached, so the
mapping from "superscript 13" to a paper existed only in the author's head. That is precisely the
state in which a citation drifts silently: nothing in the repository could be asked whether
superscript 13 pointed at the paper the sentence described, and when it was finally asked by hand,
it did not — PMID 36780200 was cited for "a bi-shRNA against the EWS/FLI1 junction taken into
clinical testing" and is a trial of Vigil, a bi-shRNA against *furin*.

THE FIX IS TO PUT THE IDENTIFIER IN THE TEXT. Every superscript carries an HTML comment naming its
PMIDs, e.g. `<sup>12</sup><!--PMID:27166877-->`. Comments do not render, so the manuscript reads
unchanged, but the mapping is now a fact in the file rather than a memory. This script then:

  1. reads those pairs in order of appearance;
  2. assigns each distinct PMID a number by FIRST APPEARANCE, which is what a numbered list means;
  3. rewrites the superscripts to the assigned numbers, so hand-numbering can never drift;
  4. emits the reference list from fetched metadata, reusing `build_reference_list`'s records.

⚠ IT CHECKS CONSISTENCY, NOT CORRECTNESS. It can prove that superscript 12 and its comment agree,
that one PMID has one number, and that the numbering has no gaps. It cannot tell whether PMID
27166877 supports the sentence it is attached to — the failure that actually happened. That check is
human. What this removes is the second failure layered on top: an author who checked the citation
once, then renumbered by hand and moved it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(HERE, "aso", "fusion-junction-aso-research-article.md")
REFS_JSON = os.path.join(HERE, "aso", "fusion-junction-aso-references.json")
OUT_MD = os.path.join(HERE, "aso", "fusion-junction-aso-submission-references.md")
OUT_JSON = os.path.join(HERE, "aso", "fusion-junction-aso-submission-references.json")

#: `<sup>8–11</sup><!--PMID:33241214,36265509,21846246,23052253-->`
CITE = re.compile(r"<sup>([0-9,–\-\s]+)</sup>\s*<!--\s*PMID:\s*([0-9,\s]+?)\s*-->")
BARE = re.compile(r"<sup>([0-9,–\-\s]+)</sup>(?!\s*<!--)")


def parse(text):
    """(span, printed_numbers, pmids) for every annotated citation, in order of appearance."""
    out = []
    for m in CITE.finditer(text):
        pmids = [p.strip() for p in m.group(2).split(",") if p.strip()]
        out.append((m.span(), m.group(1), pmids))
    return out


def assign(cites):
    """PMID -> number, by first appearance. This is the definition of a numbered reference list."""
    order = {}
    for _, _, pmids in cites:
        for p in pmids:
            order.setdefault(p, len(order) + 1)
    return order


def render_run(nums):
    """[8,9,10,11] -> '8–11'; [12] -> '12'; [24,27] -> '24,27'. Runs of three or more collapse."""
    nums = sorted(set(nums))
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            parts.append(f"{nums[i]}–{nums[j]}")
        else:
            parts.extend(str(n) for n in nums[i:j + 1])
        i = j + 1
    return ",".join(parts)


def rewrite(text, cites, order):
    """Rewrite superscripts to assigned numbers, right to left so earlier spans stay valid."""
    for (a, b), _printed, pmids in reversed(cites):
        nums = [order[p] for p in pmids]
        text = text[:a] + f"<sup>{render_run(nums)}</sup><!--PMID:{','.join(pmids)}-->" + text[b:]
    return text


#: The clinical citations were curated into the EMC registry rather than fetched into the ASO
#: corpus, so the ASO reference list has no entry for them at all — the paper's only prospective
#: trial among them. They carry the same fields, are checked by preflight's registry evidence
#: contract, and each is stamped `verified`, so reading them here is reading a tracked record, not
#: filling a gap from memory. Left out, four real references would have printed as "[METADATA NOT
#: RETRIEVED]" while their metadata sat in the repository.
#: (path, dotted key of the {slug: record} map). Order is precedence: the fetched ASO corpus wins,
#: then the curated maps, each of which stamps its entries `verified` and carries the same fields.
CURATED = [
    (os.path.join(HERE, "..", "data", "emc-clinical-registry.json"), "registry.citations"),
    (os.path.join(HERE, "fusion-partner", "emc-fusion-partner-pooling.json"), "citations"),
]


def _dig(d, dotted):
    for k in dotted.split("."):
        d = (d or {}).get(k)
    return d or {}


def _generated_reference_lists():
    """Committed reference lists this module has generated, which carry retrieved records.

    ⚠ A GENERATED FILE IS A LEGITIMATE SOURCE HERE AND THIS IS NOT CIRCULAR. Its `records` block is
    not composed by this module; it is copied verbatim from a retrieval product and stamped with the
    provenance that says so, and any PMID that was never retrieved is listed in
    `without_fetched_metadata` and prints as a gap rather than as text. Reading it back is how a
    record fetched once stays reachable from a plain checkout instead of only from a machine that
    happens to have the `literature-cache` branch.
    """
    return [p for p in (OUT_JSON,) if os.path.exists(p)]


def load_meta():
    """Bibliographic records, keyed by PMID. Read, never typed — see build_reference_list."""
    out = {}
    if os.path.exists(REFS_JSON):
        d = json.load(open(REFS_JSON))
        entries = d if isinstance(d, list) else (d.get("references") or d.get("entries") or [])
        for e in entries:
            p = str(e.get("pmid") or "").strip()
            if p:
                out[p] = e
    for path, key in CURATED:
        if not os.path.exists(path):
            continue
        for e in _dig(json.load(open(path)), key).values():
            p = str((e or {}).get("pmid") or "").strip()
            if p and p not in out:
                out[p] = e

    # ⛔ THE LIST THIS MODULE ITSELF GENERATES IS A RETRIEVED-RECORD SOURCE, AND NOT READING IT TURNED
    # CI RED FOR A REASON THAT WAS NOT A DEFECT (2026-08-13). `test_every_cited_paper_has_a_retrieved
    # _bibliographic_record` failed on `main` for PMID 7545436, the Sugimoto nearest-neighbour
    # reference the ASO manuscript's thermodynamics rests on — while a complete retrieved record for
    # it (`source: MED`, authors, journal, volume, pages, DOI, abstract) sat committed in
    # `fusion-junction-aso-submission-references.json` under `records`, generated by this file.
    # The lookup consulted the working-record corpus, the curated maps and the `literature-cache`
    # BRANCH, and that branch is not present in a CI checkout — so the record was reachable on a
    # developer's machine that happened to have fetched it and nowhere else.
    # ⚠ A CITATION-INTEGRITY TEST THAT FAILS ON A LOOKUP GAP IS WORSE THAN ONE THAT DOES NOT RUN:
    # it spends the credibility of a real guard on a false alarm, and the next red build gets waved
    # through. The record travels with the repository, so the check must look where it lives.
    for path in _generated_reference_lists():
        for p, e in (json.load(open(path)).get("records") or {}).items():
            p = str(p).strip()
            if p and p not in out:
                out[p] = e

    out.update({p: e for p, e in _literature_cache().items() if p not in out})

    # ⛔ A RECORD THAT EXISTS IS NOT THEREBY COMPLETE (2026-08-12). Every source above is
    # first-wins, so a PMID that arrives from a corpus carrying `title`/`authors` and no `journal`
    # keeps that hole for good — later sources are only consulted for PMIDs nobody has at all.
    # Two of the 29 submission references rendered with no journal name for exactly that reason,
    # and the journal for both was sitting in a retrieved record in this repository the whole time.
    # ⚠ ABSENT FIELDS ONLY, NEVER AN OVERWRITE. A retrieved value already in hand outranks another
    # retrieval of the same field; the gap is the only thing being closed.
    harvested = _harvested_records()
    for p, src in harvested.items():
        e = out.setdefault(p, {"pmid": p})
        for k in ("authors", "title", "journal", "volume", "issue", "year", "doi"):
            if not e.get(k) and src.get(k):
                e[k] = src[k]
    return out


#: Retrieval products that are not reference corpora but do carry bibliographic fields. Harvested
#: by walking for any dict with a `pmid`, because these files nest records under query names rather
#: than at a fixed path, and a dotted path would break the next time a query is added.
HARVEST_SOURCES = [
    os.path.join(HERE, "..", "literature", "fusion-consensus-probe.json"),
    os.path.join(HERE, "..", "literature", "submission-reference-metadata-2026-08-09.json"),
    os.path.join(HERE, "fusion-partner", "lit-targets-partner-events.json"),
    # Added 2026-08-15 for the NR4A-redundancy paragraph. Its records were fetched after the ASO
    # corpus was frozen, so no source above can see them — which the `_literature_cache` docstring
    # names as a reason to fetch again and never a reason to type an author list.
    os.path.join(HERE, "aso", "lit-targets-nr4a-redundancy.json"),
]

#: Europe PMC, Crossref, OpenAlex and PubMed disagree on the spelling of the same three fields.
_ALIASES = {"authors": ("authors", "authorString"),
            "journal": ("journal", "journalTitle"),
            "year": ("year", "pubYear")}


def _normalise(rec, pmid):
    out = {"pmid": pmid}
    for canonical, names in _ALIASES.items():
        for n in names:
            if rec.get(n):
                out[canonical] = rec[n]
                break
    for k in ("title", "volume", "issue", "doi"):
        if rec.get(k):
            out[k] = rec[k]
    return out


def _harvested_records():
    """PMID -> record, merged field-wise across every harvest source.

    ⚠ MERGED, NOT FIRST-WINS. One source carries the author list for a 2026 Histopathology paper
    and another carries its journal; taking either whole drops the other's field, which is how a
    reference briefly rendered with a journal and no authors. Fields accumulate, and a field
    already held is never overwritten.

    ⚠ Two shapes are harvested: a dict carrying its own `pmid`, and a dict KEYED by PMID with no
    `pmid` inside — the second is how the curated corpora store records, and a walker that only
    looks for a `pmid` key cannot see it at all.
    """
    out = {}

    def take(pmid, rec):
        if not isinstance(rec, dict):
            return
        dst = out.setdefault(pmid, {"pmid": pmid})
        for k, v in _normalise(rec, pmid).items():
            if not dst.get(k) and v:
                dst[k] = v

    def walk(o):
        if isinstance(o, dict):
            p = str(o.get("pmid") or "").strip()
            if p.isdigit():
                take(p, o)
            for k, v in o.items():
                if isinstance(v, dict) and str(k).isdigit() and 6 <= len(str(k)) <= 9:
                    take(str(k), v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for path in HARVEST_SOURCES:
        if not os.path.exists(path):
            continue
        try:
            walk(json.load(open(path)))
        except Exception:  # noqa: BLE001 — one malformed source must not stop the rest
            continue
    return out


def _literature_cache():
    """Every fetched record on the `literature-cache` branch, keyed by PMID.

    ⭐ THE LAST RESORT, AND THE ONLY ONE THAT CAN COVER A CITATION FETCHED TODAY. The ASO reference
    corpus was built for the working record, so a paper retrieved for the submission after that
    corpus was frozen has metadata nowhere the two sources above can see — which is a reason to
    fetch again, never a reason to type an author list. Read with `git show` against the fetched
    branch: $0, offline, no network, exactly as `build_reference_list` does.
    """
    out = {}
    r = subprocess.run(["git", "ls-tree", "-r", "--name-only", "origin/literature-cache"],
                       cwd=os.path.dirname(os.path.dirname(HERE)), capture_output=True, text=True)
    for path in [ln for ln in r.stdout.splitlines() if ln.endswith("/_index.json")]:
        g = subprocess.run(["git", "show", f"origin/literature-cache:{path}"],
                           cwd=os.path.dirname(os.path.dirname(HERE)),
                           capture_output=True, text=True)
        try:
            d = json.loads(g.stdout)
        except Exception:  # noqa: BLE001 — a malformed index must not stop the others
            continue
        recs = d if isinstance(d, list) else (d.get("records") or list(d.values()))
        for e in recs:
            if not isinstance(e, dict):
                continue
            p = str(e.get("pmid") or "").strip()
            if p and p not in out:
                out[p] = e
    return out


def format_entry(n, pmid, meta):
    e = meta.get(pmid)
    if not e:
        # ⛔ A GAP IS PRINTED AS A GAP. An invented author list is worse than a visible hole:
        # the hole is something the author can see and fix, the invention is not.
        return f"{n}. [METADATA NOT RETRIEVED] PMID: {pmid}."
    bits = []
    for k in ("authors", "title", "journal"):
        if e.get(k):
            bits.append(str(e[k]).rstrip("."))
    tail = ""
    if e.get("year"):
        tail = f" {e['year']}"
        if e.get("volume"):
            tail += f";{e['volume']}"
            if e.get("issue"):
                tail += f"({e['issue']})"
            if e.get("pages"):
                tail += f":{e['pages']}"
        tail += "."
    s = ". ".join(bits) + "." + tail + f" PMID: {pmid}."
    if e.get("doi"):
        s += f" doi:{e['doi']}"
    return f"{n}. {s}"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    text = open(PAPER, encoding="utf-8").read()
    cites = parse(text)
    bare = [m.group(1) for m in BARE.finditer(text)]

    if not cites:
        print("no annotated citations found — nothing to resolve", file=sys.stderr)
        return 2

    order = assign(cites)
    meta = load_meta()
    missing = [p for p in order if p not in meta]

    print(f"{len(cites)} annotated citation(s), {len(order)} distinct PMID(s), "
          f"{len(bare)} UNANNOTATED superscript(s), {len(missing)} without fetched metadata")
    if bare:
        # ⛔ NOT A WARNING TO SKIM PAST. An unannotated superscript is one this tool cannot check
        # and will not renumber, so it keeps whatever number the author last typed — while every
        # citation around it moves. That is worse than the problem this tool was written to fix.
        print(f"  ⛔ unannotated superscripts (these will NOT be renumbered): {sorted(set(bare))}")
    if missing:
        print(f"  ⚠ no fetched record for: {sorted(missing)} — entries print as gaps, never guessed")

    if "--write" in argv:
        new = rewrite(text, cites, order)
        if new != text:
            open(PAPER, "w", encoding="utf-8").write(new)
            print(f"  renumbered superscripts in {os.path.basename(PAPER)}")
        lines = [format_entry(n, p, meta) for p, n in sorted(order.items(), key=lambda kv: kv[1])]
        open(OUT_MD, "w", encoding="utf-8").write(
            "<!-- GENERATED — DO NOT EDIT. Regenerate: python3 "
            "research/manuscripts/submission_citations.py --write -->\n\n"
            "# References — fusion-junction ASO submission\n\n"
            f"*{len(order)} entries, numbered by first citation in the submission manuscript. "
            "Metadata is read from retrieved bibliographic records; an unretrieved field is left "
            "absent rather than completed.*\n\n" + "\n".join(lines) + "\n")
        json.dump({"_what": ("Every reference cited by the submission manuscript, numbered by "
                             "order of first citation, with the bibliographic record each entry "
                             "was rendered from."),
                   "_provenance": ("Records are read from retrieved fetch products — the ASO "
                                   "reference corpus, the curated citation maps, and the "
                                   "literature-cache branch. No field is typed from recollection; "
                                   "a record that was never retrieved is listed in "
                                   "`without_fetched_metadata` and its entry prints as a gap."),
                   "n_references": len(order),
                   "numbering": {p: n for p, n in sorted(order.items(), key=lambda kv: kv[1])},
                   "records": {p: meta[p] for p in order if p in meta},
                   "without_fetched_metadata": sorted(missing),
                   "unannotated_superscripts": sorted(set(bare))},
                  open(OUT_JSON, "w"), indent=2)
        print(f"  wrote {os.path.basename(OUT_MD)} and {os.path.basename(OUT_JSON)}")
    elif "--check" in argv:
        # ⛔ WHY THIS MODE EXISTS (added 2026-08-13, after a data-integrity review caught the gap).
        # Until now this tool had exactly two behaviours: --write, which repairs the numbering, and
        # a default that PRINTS the derived numbering and returns 0. Nothing ever compared the
        # number PRINTED in the manuscript against the number DERIVED from its PMID comments — so a
        # draft in which four numbers each pointed at two different references, with 28 superscripts
        # out of order, exited 0 and passed `test_submission_citations.py`. That is precisely the
        # drift the module docstring says cannot happen, surviving inside the tool written to stop
        # it, because a checker that only recomputes and never compares is a checker of nothing.
        bad = []
        for _span, printed, pmids in cites:
            want = render_run([order[p] for p in pmids])
            got = re.sub(r"\s+", "", printed)
            if got != want:
                bad.append((got, want, ",".join(pmids)))
        for got, want, pmids in bad:
            print(f"  ⛔ superscript {got!r} should be {want!r} for PMID:{pmids}", file=sys.stderr)
        if bad or bare:
            print(f"citation numbering is stale: {len(bad)} mis-numbered superscript(s), "
                  f"{len(bare)} unannotated — re-run with --write", file=sys.stderr)
            return 1
        print("  citation numbering is current")
    else:
        for p, n in sorted(order.items(), key=lambda kv: kv[1]):
            print(f"  {n:>3}  PMID:{p}  {'' if p in meta else '(no fetched record)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
