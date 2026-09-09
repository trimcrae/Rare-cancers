#!/usr/bin/env python3
"""Step 0. Dump ONLY the non-outcome metadata of the 162-paper probe corpus, so a genre
classifier can be written against real titles WITHOUT any cue/outcome information being
visible. `has_mechanism_cue`, sentence text and every death-cue field are deliberately
excluded from this dump. Read-only on the committed probe; writes one JSON here.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
PROBE = ROOT / "research/literature/emc-mortality-probe.json"
OUT = pathlib.Path(__file__).with_name("corpus-metadata.json")
EMC_TITLE = re.compile(r"myxoid chondrosarcoma|chordoid sarcoma|NR4A3", re.I)


def main():
    papers = json.loads(PROBE.read_text())["terminal_events"]
    rows = [{"pmid": p.get("pmid"), "pmcid": p.get("pmcid"), "title": p.get("title"),
             "journal": p.get("journal"), "year": p.get("year"),
             "n_death_cue_sentences": p.get("n_sentences"),
             "emc_titled": bool(EMC_TITLE.search(p.get("title") or ""))} for p in papers]
    OUT.write_text(json.dumps({
        "_what_this_is": __doc__.strip(),
        "_excluded_on_purpose": "sentence text and has_mechanism_cue: the outcome is not looked at here",
        "n_papers": len(rows), "n_emc_titled": sum(r["emc_titled"] for r in rows),
        "papers": rows}, indent=1) + "\n")
    for r in rows:
        print(f'{r["pmid"]}\t{"EMC" if r["emc_titled"] else "OTH"}\t{r["journal"]}\t{r["year"]}\t{r["title"]}')
    print(f"\n{len(rows)} papers, {sum(r['emc_titled'] for r in rows)} EMC-titled", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
