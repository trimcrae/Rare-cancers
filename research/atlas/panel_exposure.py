#!/usr/bin/env python3
"""
EMC Atlas — achievable-exposure evidence for the validation-panel compounds (verbatim, from FDA labels).

WHY. The DepMap result (claim C020) showed the proteostasis panel targets are pan-essential, so the
therapeutic window is a PHARMACOLOGY/exposure question. The atlas's `achievable_free_exposure` fields
were 'to_populate'. To fill them WITHOUT fabricating numbers, this fetches each approved compound's FDA
label (DailyMed) and extracts VERBATIM sentences that mention Cmax / plasma protein binding / half-life,
storing the quote + the label setid + URL as the source. Investigational compounds (no FDA label) are
recorded honestly as 'no_fda_label'. Nothing is invented; the atlas interprets the quotes.

Pure stdlib; DailyMed is NLM (blocked by the sandbox proxy) -> runs in CI.
Output: research/atlas/_generated/panel-exposure.json (+ .md).
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "_generated")
os.makedirs(OUTDIR, exist_ok=True)
DM = "https://dailymed.nlm.nih.gov/dailymed/services/v2"

COMPOUNDS = ["carfilzomib", "bortezomib", "ixazomib", "panobinostat", "romidepsin", "entinostat",
             "doxorubicin", "venetoclax", "navitoclax", "pazopanib", "sunitinib", "brigatinib",
             "selinexor"]
# investigational / no FDA label (recorded honestly, not queried):
NO_LABEL = {"PU-H71": "HSP90 inhibitor (investigational)", "onalespib": "HSP90 inhibitor (investigational)",
            "HDM201/siremadlin": "MDM2 inhibitor (investigational)"}
KW = ["cmax", "maximum plasma concentration", "maximum observed", "protein binding", "protein-binding",
      "bound to plasma", "plasma protein", "half-life", "auc", "steady state", "steady-state"]


def _get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-atlas/1.0", "Accept": "application/json"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url[:80]}: {e}", file=sys.stderr, flush=True)
            time.sleep(2 ** i)
    return b""


def setid_for(drug):
    raw = _get(f"{DM}/spls.json?drug_name={urllib.parse.quote(drug)}&pagesize=5")
    try:
        data = json.loads(raw).get("data", [])
        return data[0]["setid"] if data else None
    except Exception:  # noqa
        return None


def extract(drug):
    sid = setid_for(drug)
    if not sid:
        return {"compound": drug, "status": "no_setid_found"}
    raw = _get(f"{DM}/spls/{sid}.xml", timeout=180)
    if not raw:
        return {"compound": drug, "status": "label_fetch_failed", "setid": sid}
    text = re.sub(r"<[^>]+>", " ", raw.decode("utf-8", "replace"))
    text = re.sub(r"\s+", " ", text)
    sents = re.split(r"(?<=[.;])\s+", text)
    quotes, seen = [], set()
    for s in sents:
        sl = s.lower()
        if any(k in sl for k in KW) and re.search(r"\d", s) and 15 < len(s) < 320:
            key = s[:90]
            if key not in seen:
                seen.add(key)
                quotes.append(s.strip())
        if len(quotes) >= 12:
            break
    return {"compound": drug, "status": "ok" if quotes else "no_pk_sentences_found",
            "setid": sid, "label_url": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={sid}",
            "verbatim_pk_quotes": quotes}


def main():
    out = {"_note": "Achievable-exposure evidence for the validation-panel compounds. VERBATIM Cmax / "
                    "protein-binding / half-life sentences quoted from FDA labels (DailyMed) + source setid/URL. "
                    "No numbers invented; interpret the quotes. Investigational compounds have no FDA label.",
           "_use": "Combine Cmax with protein binding (fu) to bound the achievable UNBOUND concentration, and "
                   "compare to the in-vitro active concentration before selecting panel concentrations (esp. for "
                   "the pan-essential proteostasis targets, where the window is exposure-limited).",
           "compounds": [], "no_fda_label": NO_LABEL}
    for d in COMPOUNDS:
        print(f"fetching label PK: {d}", file=sys.stderr, flush=True)
        try:
            out["compounds"].append(extract(d))
        except Exception as e:  # noqa
            out["compounds"].append({"compound": d, "status": f"error: {e}"})
    json.dump(out, open(os.path.join(OUTDIR, "panel-exposure.json"), "w"), indent=2)

    lines = ["# Validation-panel achievable exposure (verbatim FDA-label PK, CI)", "", out["_note"], ""]
    for c in out["compounds"]:
        lines.append(f"## {c['compound']} — {c['status']}")
        if c.get("label_url"):
            lines.append(f"- source: {c['label_url']}")
        for q in c.get("verbatim_pk_quotes", [])[:6]:
            lines.append(f"  - \"{q}\"")
    if NO_LABEL:
        lines.append("")
        lines.append("**No FDA label (investigational):** " + ", ".join(f"{k} ({v})" for k, v in NO_LABEL.items()))
    open(os.path.join(OUTDIR, "panel-exposure.md"), "w").write("\n".join(lines) + "\n")
    print("wrote panel-exposure.json/.md", file=sys.stderr)


if __name__ == "__main__":
    main()
