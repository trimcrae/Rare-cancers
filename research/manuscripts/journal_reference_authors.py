#!/usr/bin/env python3
"""Author lists for the condensed ASO article's reference list, at the venue's author count.

⭐ WHY. Nucleic Acid Therapeutics' submission checklist, item A4: *all authors up to 11; if more,
first 9 then et al.* Every entry in the list carried FIRST THREE + et al. — a house habit, not the
venue's rule — so twelve entries named too few authors and eleven truncated a list the venue wants
printed in full. The venue's own worked example shows the shape (its Submission Guidelines, captured
verbatim in research/literature/nat-submission-guidelines-2026-08-23.md):

    Garaud S, F Roufosse, P De Silva, C Gu-Trantien, J-N Lodewyckx, H Duvillier, S Dedeurwaerder,
    M Bizet, M Defrance, et al. (2017). FOXP1 is a regulator of quiescence … Eur J Immunol 47:168–179.

nine named authors, a comma before `et al.`, first author `Surname Initials` and every author after
it `Initials Surname`. Two- and three-author entries take `and` before the last name, as that page's
other example shows: `Malerba A, L Boldrin and G Dickson. (2011).`

⛔ THE AUTHOR LISTS ARE READ FROM FETCH PRODUCTS, NEVER TYPED. CLAUDE.md §7: never write an
identifier from recollection, and an author list is a bibliographic fact like any other. `--build`
reads Europe PMC and Crossref products already committed on the `literature-cache` branch and the
reference corpora on `main`, records EVERY candidate list it found with the file it came from, and
writes them to `aso/journal-reference-authors.json`. `--apply` and `--check` are offline and read
only that artifact.

⛔ AND A COUNT AND A NAME ARE SEPARATE FACTS, BECAUSE MEDLINE TRUNCATES. Pre-1996 MEDLINE records
carry at most TEN authors, with no marker to say so. Reference 1 (PMID 8634690, Hum Mol Genet 1995)
reads as exactly ten in every Europe PMC product in this repository, and the publisher's own
Crossref record for the same DOI lists THIRTEEN — Aurias, Delattre and Thomas are in the paper and
not in MEDLINE. Ten would have printed all ten authors as if that were the whole list; thirteen
takes the entry over the venue's threshold and prints nine then `et al.`, which is both the right
rule and the right count. So `n_authors` is taken from the LONGEST list any fetch product gives,
while the printed NAMES are taken from the longest MEDLINE-form list — Crossref writes full given
names, and turning "Alain Aurias" into "A Aurias" would be deriving an identifier rather than
reading one. An entry whose MEDLINE-form list is too short to print what the rule asks for is
REPORTED AS A GAP rather than filled in.

⚠ WHAT THIS IS NOT. It reads and renders author lists. It says nothing about whether an entry's
title, year, volume, pages or PMID are right, and nothing about whether the cited paper supports the
sentence that cites it.

NETWORK. None. Every source is already committed; the literature-cache blobs are read with
`git show`, so `--build` needs that branch fetched (`git fetch origin literature-cache`).

Run:
    python3 research/manuscripts/journal_reference_authors.py            # rebuild the artifact
    python3 research/manuscripts/journal_reference_authors.py --apply    # rewrite the list
    python3 research/manuscripts/journal_reference_authors.py --check    # is the list on the rule?
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REFS = os.path.join(HERE, "aso", "fusion-junction-aso-journal-references.md")
OUT = os.path.join(HERE, "aso", "journal-reference-authors.json")

#: The venue's rule, item A4 of its submission checklist.
NAME_ALL_UP_TO = 11
THEN_FIRST = 9

#: `1. Labelle Y, J Zucman, … et al. (1995). Title. Journal 4:2219–2226. PMID: 8634690.`
#: Anchored on `. (YEAR). ` because that is the one separator an author segment cannot contain —
#: splitting on the first period would cut "Dei Tos AP" style names and every initial in the list.
ENTRY = re.compile(r"^(?P<n>\d+)\. (?P<authors>.+?)\. \((?P<year>\d{4})\)\. ")
PMID_IN_ENTRY = re.compile(r"PMID:\s*(\d+)")

#: Trailing initials as MEDLINE writes them: `J`, `SV`, `J-N`, `AIA`. Anything else and the name is
#: not in `Surname Initials` form, so it is reported rather than flipped on a guess.
INITIALS = re.compile(r"^[A-Z][A-Za-z-]{0,3}$")

#: ⛔ A GENERATIONAL SUFFIX IS NOT AN INITIAL, AND THE NAIVE FLIP PRINTED ONE AS ONE. Europe PMC's
#: `authorList` writes reference 22's sixth author `Harper TA Jr`; taking the last token as the
#: initials rendered him `Jr Harper TA` in the built entry. The suffix is lifted off before the
#: initials are found and put back after the surname: `TA Harper Jr`. Two Europe PMC fields of the
#: same record disagree about it — `authorString` drops the `Jr` — which is why `same_person` below
#: compares names with the suffix stripped rather than reporting a conflict over one.
SUFFIX = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "2nd", "3rd", "4th"}

#: Fetch products on `literature-cache`. Europe PMC `resultType=core` search results and one
#: Crossref work, each holding the author list of one or more cited references. Listed rather than
#: discovered because a scan of that branch reads 70,000 blobs to find eighteen.
LITERATURE_CACHE = (
    "literature/labelle-1995-type3-primary-routes/79_epmc_labelle_core.txt",
    "literature/labelle-1995-type3-primary-routes/75_crossref_labelle_doi.txt",
    "literature/emc-partner-events/paioli2021_epmc_core.txt",
    "literature/emc-partner-events/stacchiotti2019_epmc_core.txt",
    "literature/emc-partner-events/huang2023_epmc_core.txt",
    "literature/emc-partner-events/epmc_search_taf15_fulltext.txt",
    "literature/emc-endpoint-benchmarks-r2/epmc_core_anthracycline_24345066.txt",
    "literature/emc-cell-models-registry-2026-08-15/epmc_emc_models.txt",
    "literature/emc-cell-models-registry-2026-08-15/epmc_nr4a3_cellline.txt",
    "literature/emc-clinical-sweep-fulltext-2026-08-07/epmc_pmid_36103645.txt",
    "literature/ews-type-nomenclature-epmc/epmc_chn_exon2_exon3.txt",
    "literature/aso-round7-precedents-and-geo/epmc_core_PMID21846246.txt",
    "literature/aso-round7-precedents-and-geo/epmc_core_PMID23052253.txt",
    "literature/aso-round7-precedents-and-geo/epmc_core_PMID33241214.txt",
    "literature/aso-round7-precedents-and-geo/epmc_core_PMID36265509.txt",
    "literature/aso-round7-precedents-and-geo/epmc_core_PMID37980543.txt",
    "literature/oswg-offtarget-2025/epmc_core_39912803.txt",
    "literature/oswg-offtarget-2025/crossref_nat20240072.txt",
    "literature/aso-round5-citation-support/_index.json",
    "literature/fusion-oligo-delivery-progress/_index.json",
    "literature/resource-citations/_index.json",
    "literature/aso-bibliography-completion/_index.json",
    "literature/aso-thermo-parameters/_index.json",
)
CACHE_REF = "origin/literature-cache"

#: Reference corpora already on `main`. Cross-checks: a disagreement with the products above is
#: reported, never averaged away.
ON_DISK = (
    "research/manuscripts/aso/fusion-junction-aso-submission-references.json",
    "research/manuscripts/aso/fusion-junction-aso-references.json",
    "research/manuscripts/aso/lit-targets-aso-bibliography-completion.json",
    "research/literature/remaining-reference-metadata-2026-08-09.json",
    "research/literature/submission-reference-metadata-2026-08-09.json",
)


# --------------------------------------------------------------------------- the reference list

def entries(text: str):
    """(line_index, line, pmid, match) for every numbered entry."""
    out = []
    for i, line in enumerate(text.splitlines()):
        if not re.match(r"^\d+\.\s", line):
            continue
        m, p = ENTRY.match(line), PMID_IN_ENTRY.search(line)
        out.append((i, line, p.group(1) if p else None, m))
    return out


# --------------------------------------------------------------------------- rendering the rule

def split_suffix(name: str):
    """`Harper TA Jr` -> ('Harper TA', 'Jr'). Any other name -> (name, '')."""
    head, _, last = name.rpartition(" ")
    return (head, last) if head and last.lower() in SUFFIX else (name, "")


def same_person(a: str, b: str):
    """Two fetched spellings of one name, compared without the generational suffix."""
    return split_suffix(a)[0] == split_suffix(b)[0]


def flip(name: str):
    """`Zucman J` -> `J Zucman`. None when the name is not in `Surname Initials` form."""
    core, suffix = split_suffix(name)
    surname, _, initials = core.rpartition(" ")
    if not surname or not INITIALS.match(initials):
        return None
    return f"{initials} {surname}" + (f" {suffix}" if suffix else "")


def render(names, n_authors):
    """The author segment, at the venue's count. Raises on a name it cannot put in order."""
    shown = names[:THEN_FIRST] if n_authors > NAME_ALL_UP_TO else names[:n_authors]
    parts = [shown[0]]
    for name in shown[1:]:
        flipped = flip(name)
        if flipped is None:
            raise ValueError(f"{name!r} is not `Surname Initials`; it cannot be reordered by rule")
        parts.append(flipped)
    #: ⚠ NO PERIOD AFTER `et al` HERE. The entry template is `N. <authors>. (YEAR). `, so the
    #: period that closes `et al.` is the segment separator the entry already carries. Returning it
    #: from here printed `…, et al.. (1995).` in all eleven truncated entries.
    if n_authors > NAME_ALL_UP_TO:
        return ", ".join(parts) + ", et al"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


# --------------------------------------------------------------------------- harvesting sources

def split_authors(s: str):
    """A MEDLINE author string -> (names, truncated). `…, et al.` sets truncated."""
    s = s.strip().rstrip(".").strip()
    names = [x.strip() for x in s.split(",") if x.strip()]
    truncated = bool(names) and names[-1].lower().rstrip(".") == "et al"
    if truncated:
        names = names[:-1]
    return names, truncated


def _json_body(raw: str):
    body = raw.split("=" * 70, 1)[-1].strip() if "=" * 70 in raw else raw.strip()
    try:
        return json.loads(body)
    except Exception:  # noqa: BLE001
        return None


def harvest(doc, origin, found):
    """Record every author list `doc` holds for any PMID, keyed by PMID."""
    def add(pmid, names, truncated, form, where):
        if names:
            found.setdefault(str(pmid), []).append(
                {"names": names, "n": len(names), "truncated": truncated,
                 "form": form, "source": f"{origin}{where}"})

    def walk(node, path):
        if isinstance(node, dict):
            # Europe PMC core / search result, and the `_index.json` corpora.
            pmid = node.get("pmid") or node.get("id")
            if isinstance(pmid, (str, int)) and str(pmid).isdigit():
                lst = (node.get("authorList") or {}).get("author")
                if isinstance(lst, list):
                    add(pmid, [a.get("fullName") for a in lst if a.get("fullName")],
                        False, "medline", f"{path} authorList")
                for key in ("authorString", "authors"):
                    if isinstance(node.get(key), str):
                        names, trunc = split_authors(node[key])
                        add(pmid, names, trunc, "medline", f"{path} {key}")
            # A Crossref work: full given names, and a DOI rather than a PMID.
            if isinstance(node.get("author"), list) and node.get("DOI"):
                names = [" ".join(x for x in (a.get("given"), a.get("family")) if x)
                         for a in node["author"] if a.get("family")]
                add(f"doi:{node['DOI'].lower()}", names, False, "crossref", f"{path} author")
            for k, v in node.items():
                # `{"records": {"<pmid>": {...}}}` — the key is the identifier.
                if isinstance(v, dict) and str(k).isdigit() and isinstance(v.get("authors"), str):
                    names, trunc = split_authors(v["authors"])
                    add(k, names, trunc, "medline", f"{path}/{k} authors")
                walk(v, f"{path}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(doc, "")


def _doi_of(line: str):
    m = re.search(r"doi:(\S+)$", line.strip())
    return m.group(1).lower() if m else None


def build():
    text = open(REFS, encoding="utf-8").read()
    rows = entries(text)
    found, sources = {}, []

    for path in LITERATURE_CACHE:
        try:
            raw = subprocess.run(["git", "show", f"{CACHE_REF}:{path}"], cwd=REPO,
                                 capture_output=True, text=True, check=True).stdout
            blob = subprocess.run(["git", "rev-parse", f"{CACHE_REF}:{path}"], cwd=REPO,
                                  capture_output=True, text=True, check=True).stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise SystemExit(f"cannot read {CACHE_REF}:{path} — `git fetch origin "
                             f"literature-cache` first ({exc})")
        doc = _json_body(raw)
        if doc is None:
            raise SystemExit(f"{path} on {CACHE_REF} is not the JSON payload it was when this "
                             "list was written; it must be re-read rather than skipped")
        sources.append({"path": f"{CACHE_REF}:{path}", "blob": blob})
        harvest(doc, f"{CACHE_REF}:{path}", found)

    for rel in ON_DISK:
        full = os.path.join(REPO, rel)
        if not os.path.exists(full):
            continue
        sources.append({"path": rel, "blob": subprocess.run(
            ["git", "hash-object", full], cwd=REPO, capture_output=True,
            text=True).stdout.strip()})
        harvest(json.load(open(full, encoding="utf-8")), rel, found)

    by_pmid, gaps = {}, []
    for _, line, pmid, m in rows:
        if not pmid or not m:
            gaps.append((pmid, "entry does not parse"))
            continue
        cands = found.get(pmid, [])
        doi = _doi_of(line)
        if doi:
            cands = cands + found.get(f"doi:{doi}", [])
        medline = [c for c in cands if c["form"] == "medline" and not c["truncated"]]
        if not medline:
            gaps.append((pmid, "no untruncated MEDLINE-form author list in any fetch product"))
            continue
        names = max(medline, key=lambda c: c["n"])
        # A count may come from any complete list, MEDLINE-form or not — that is what catches the
        # pre-1996 ten-author cap.
        counted = max([c for c in cands if not c["truncated"]], key=lambda c: c["n"])
        n_authors = counted["n"]

        conflicts = []
        for c in cands:
            if c["form"] != "medline":
                continue
            k = c["n"]
            if not all(same_person(x, y) for x, y in zip(c["names"], names["names"][:k])) \
                    or k > len(names["names"]):
                conflicts.append({"source": c["source"], "names": c["names"]})
        need = THEN_FIRST if n_authors > NAME_ALL_UP_TO else n_authors
        if len(names["names"]) < need:
            gaps.append((pmid, f"{n_authors} authors, MEDLINE-form list has only "
                               f"{len(names['names'])}; cannot print {need}"))
            continue
        try:
            rendered = render(names["names"], n_authors)
        except ValueError as exc:
            gaps.append((pmid, str(exc)))
            continue
        by_pmid[pmid] = {
            "n_authors": n_authors,
            "n_authors_source": counted["source"],
            "n_printed": min(need, n_authors),
            "rule": ("all authors" if n_authors <= NAME_ALL_UP_TO
                     else f"more than {NAME_ALL_UP_TO}: first {THEN_FIRST} then et al."),
            "names": names["names"],
            "names_source": names["source"],
            "rendered": rendered,
            "conflicting_sources": conflicts,
            "candidates": sorted({(c["n"], c["truncated"], c["form"], c["source"])
                                  for c in cands}),
        }

    return {
        "_what": ("The author list of every reference the condensed ASO article cites, and the "
                  "author segment each entry prints under the venue's count rule."),
        "_why": ("Nucleic Acid Therapeutics checklist A4: all authors up to 11; more than 11, the "
                 "first 9 then et al. Every entry carried first-three-then-et-al."),
        "_provenance": ("Europe PMC and Crossref fetch products on branch literature-cache, plus "
                        "the reference corpora on main. No author name here was typed by hand; a "
                        "PMID with no fetched list is listed in `without_fetched_authors` and its "
                        "entry is left alone."),
        "⚠_a_count_and_a_name_are_separate_facts": (
            "Pre-1996 MEDLINE caps an author list at ten and marks it in no way. `n_authors` is "
            "the longest list ANY product gives — Crossref included — while `names` is the longest "
            "MEDLINE-form list, because Crossref writes full given names and shortening one to an "
            "initial would derive an identifier rather than read it."),
        "⚠_not_a_verification_of_the_reference": (
            "This reads author lists. It says nothing about whether an entry's title, year, "
            "volume, pages or PMID are correct, nor whether the paper supports its citation."),
        "rule": {"name_all_up_to": NAME_ALL_UP_TO, "then_first": THEN_FIRST,
                 "source": "research/literature/nat-submission-guidelines-2026-08-23.md"},
        "n_entries": len(rows),
        "n_fetched": len(by_pmid),
        "without_fetched_authors": [{"pmid": p, "why": w} for p, w in gaps],
        "sources": sources,
        "by_pmid": by_pmid,
    }


# --------------------------------------------------------------------------- apply / check

def _load():
    if not os.path.exists(OUT):
        print(f"{os.path.basename(OUT)} is not built — run without --apply/--check first",
              file=sys.stderr)
        raise SystemExit(1)
    return json.load(open(OUT, encoding="utf-8"))["by_pmid"]


def apply_to_list() -> int:
    """Rewrite each entry's author segment to the fetched list at the venue's count. Offline."""
    meta = _load()
    text = open(REFS, encoding="utf-8").read()
    lines = text.splitlines()
    changed, unchanged, skipped = 0, 0, []
    for i, line, pmid, m in entries(text):
        if not m or not pmid or pmid not in meta:
            skipped.append((pmid, "no fetched author list"))
            continue
        rec = meta[pmid]
        current = m.group("authors")
        # ⛔ The entry must already name the first author the fetch does, or the record and the
        # entry are about different papers and nothing may be rewritten from it.
        if current.split(",")[0].strip() != rec["names"][0]:
            skipped.append((pmid, f"entry opens {current.split(',')[0]!r}, record opens "
                                  f"{rec['names'][0]!r}"))
            continue
        if current == rec["rendered"]:
            unchanged += 1
            continue
        lines[i] = line[:m.start("authors")] + rec["rendered"] + line[m.end("authors"):]
        changed += 1
    with open(REFS, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"rewrote {changed} author list(s); {unchanged} already on the rule")
    for pmid, why in skipped:
        print(f"  UNCHANGED {pmid}: {why}", file=sys.stderr)
    return 1 if skipped else 0


def check() -> int:
    """Every entry's author segment is the one the fetched list and the rule produce."""
    meta = _load()
    text = open(REFS, encoding="utf-8").read()
    bad = []
    for _, line, pmid, m in entries(text):
        if not m or not pmid or pmid not in meta:
            bad.append((pmid, "no fetched author list", ""))
            continue
        if m.group("authors") != meta[pmid]["rendered"]:
            bad.append((pmid, meta[pmid]["rendered"], m.group("authors")))
    for pmid, want, got in bad:
        print(f"  {pmid}: expected {want!r}, entry has {got!r}", file=sys.stderr)
    print(f"{len(bad)} entries not on the venue's author rule")
    return 1 if bad else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--apply" in argv:
        return apply_to_list()
    if "--check" in argv:
        return check()
    d = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}: {d['n_fetched']} of {d['n_entries']} entries")
    for gap in d["without_fetched_authors"]:
        print(f"  NO AUTHOR LIST {gap['pmid']}: {gap['why']}", file=sys.stderr)
    return 1 if d["without_fetched_authors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
