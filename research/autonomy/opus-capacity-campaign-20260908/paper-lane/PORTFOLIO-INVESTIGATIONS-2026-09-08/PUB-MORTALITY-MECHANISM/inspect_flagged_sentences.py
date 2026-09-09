#!/usr/bin/env python3
"""Print, verbatim, every death-cue sentence the strict terminal-event lexicon flags, in
both corpora, plus the gold row whose tier is split across three patients. Read-only."""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[6]
d = json.loads((ROOT / "research/literature/emc-mortality-probe.json").read_text())
g = json.loads((ROOT / "research/manuscripts/emc-terminal-events-classified.json").read_text())
EMC = re.compile(r"myxoid chondrosarcoma|chordoid sarcoma|NR4A3", re.I)
S = re.compile(r"\b(respiratory (?:failure|insufficiency|arrest)|pulmonary (?:failure|insufficiency)|"
               r"cardiac arrest|cardiopulmonary arrest|multi-?organ (?:failure|dysfunction)|"
               r"(?:hepatic|liver|renal|heart) failure|septic shock|sepsis|asphyxia|exsanguinat\w+|"
               r"(?:cerebral|intracranial|intracerebral|subarachnoid) (?:haemorrhage|hemorrhage)|"
               r"pulmonary embolism)\b", re.I)
for r in g["individual_events"]:
    if r["mechanism_tier"].startswith("split"):
        print("SPLIT GOLD ROW:", json.dumps(r, indent=1))
for label, want in (("EMC-TITLED", True), ("NOT EMC-TITLED", False)):
    print("\n===", label)
    for p in d["terminal_events"]:
        if bool(EMC.search(p.get("title") or "")) is want:
            for i, s in enumerate(p["sentences"]):
                if S.search(s["sentence"]):
                    print(f'{p.get("pmid")} [{i}] {p["title"]}\n    {s["sentence"]}')
