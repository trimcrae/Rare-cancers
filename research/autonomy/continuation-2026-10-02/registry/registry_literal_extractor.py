"""Literal CT.gov extraction; conformance utility, not clinical harmonization."""
import argparse
import copy
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

SCHEMA = "ctgov-literal-response/1"
ALIASES = {
    "CR": ("cr", "complete response", "complete remission"),
    "PR": ("pr", "partial response", "partial remission"),
    "SD": ("sd", "stable disease"),
    "PD": ("pd", "progressive disease"),
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def integer(value):
    if isinstance(value, bool):
        return None
    text = str(value).strip()
    return int(text) if re.fullmatch(r"[0-9]+", text) else None


def alias(title):
    text = " ".join(str(title or "").casefold().split()).rstrip(".")
    for category, names in ALIASES.items():
        if text in names:
            return category
        if any(text == name + " (" + category.lower() + ")"
               for name in names if name != category.lower()):
            return category
    return None


def load_verified(raw, expected_sha256, source):
    """Hash ORIGINAL bytes, including any archived text preamble, before parsing."""
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256 or ""):
        raise ValueError("An explicit lowercase SHA256 is required")
    actual = digest(raw)
    if actual != expected_sha256:
        raise ValueError("Input SHA256 mismatch")
    text = raw.decode("utf-8-sig")
    if not text.lstrip().startswith(("{", "[")):
        marker = text.find("=" * 30)
        newline = text.find("\n", marker)
        if marker < 0 or newline < 0:
            raise ValueError("Unrecognized archived JSON preamble")
        text = text[newline + 1:]
    document = json.loads(text)
    receipt = dict(source, sha256=actual, bytes=len(raw))
    if receipt.get("kind") not in ("archived", "live-capture", "synthetic"):
        raise ValueError("Explicit source kind required")
    if receipt["kind"] == "archived" and not receipt.get("revision"):
        raise ValueError("Archived source requires immutable revision")
    return document, receipt


def denominator_entries(denoms, group_id, scope):
    entries = []
    for di, denom in enumerate(denoms):
        for vi, count in enumerate(denom.get("counts", [])):
            if count.get("groupId") == group_id:
                entries.append({
                    "scope": scope, "denomIndex": di, "countIndex": vi,
                    "unitsLiteral": denom.get("units"),
                    "countLiteral": copy.deepcopy(count),
                    "integerValue": integer(count.get("value")),
                })
    return entries


def choose_denominator(outcome, cls, group_id):
    own = denominator_entries(cls.get("denoms", []), group_id, "class")
    overall = denominator_entries(outcome.get("denoms", []),
                                  group_id, "outcome")
    # Never infer scope from only the classes observed for one results group.
    if own:
        eligible = own
    elif not cls.get("denoms") and len(outcome.get("classes", [])) == 1:
        eligible = overall
    else:
        eligible = []
    participants = [x for x in eligible
                    if str(x["unitsLiteral"]).strip().casefold() == "participants"]
    chosen = participants[0] if len(participants) == 1 else None
    if chosen is not None and chosen["integerValue"] is None:
        chosen = None
    return {"classEntries": own, "outcomeEntries": overall,
            "eligibleEntries": eligible, "selectedParticipantEntry": chosen,
            "status": ("one-explicit-participant-count" if chosen else
                       "missing-invalid-or-ambiguous")}


def extract(document, receipt, nct_ids=None):
    if isinstance(document, list):
        studies = document
    elif "studies" in document:
        studies = document["studies"]
    elif "protocolSection" in document:
        studies = [document]
    else:
        raise ValueError("Expected CT.gov study or studies envelope")
    result = {"schema": SCHEMA, "aliasVersion": "conservative-exact/1",
              "source": copy.deepcopy(receipt), "outcomes": [], "rows": []}
    for si, study in enumerate(studies):
        protocol = study.get("protocolSection", {})
        nct = protocol.get("identificationModule", {}).get("nctId")
        if nct_ids is not None and nct not in nct_ids:
            continue
        outcomes = study.get("resultsSection", {}).get(
            "outcomeMeasuresModule", {}).get("outcomeMeasures", [])
        for oi, outcome in enumerate(outcomes):
            oid = [receipt["sha256"], si, nct, oi, digest(canonical(outcome))]
            result["outcomes"].append({
                "outcomeKey": oid, "sourcePointer":
                f"/studies/{si}/resultsSection/outcomeMeasuresModule/outcomeMeasures/{oi}",
                "pointerConvention": "study normalized into studies envelope",
                "lastUpdatePostDateStruct": copy.deepcopy(
                    protocol.get("statusModule", {}).get("lastUpdatePostDateStruct")),
                "literal": copy.deepcopy(outcome),
            })
            groups = outcome.get("groups", [])
            for ci, cls in enumerate(outcome.get("classes", [])):
                cells = defaultdict(list)
                group_ids = list(dict.fromkeys(g.get("id") for g in groups))
                for ki, category in enumerate(cls.get("categories", [])):
                    for mi, measure in enumerate(category.get("measurements", [])):
                        gid = measure.get("groupId")
                        if gid not in group_ids:
                            group_ids.append(gid)
                        cells[gid].append({
                            "categoryIndex": ki, "measurementIndex": mi,
                            "categoryLiteral": copy.deepcopy(
                                {k: v for k, v in category.items() if k != "measurements"}),
                            "measurementLiteral": copy.deepcopy(measure),
                            "normalizedCategory": alias(category.get("title")),
                            "integerValue": integer(measure.get("value")),
                        })
                for gid in group_ids:
                    records = cells[gid]
                    mapped = {k: [m for m in records if m["normalizedCategory"] == k]
                              for k in ALIASES}
                    complete = all(len(mapped[k]) == 1 and
                                   mapped[k][0]["integerValue"] is not None
                                   for k in ALIASES)
                    counts = ({k: mapped[k][0]["integerValue"] for k in ALIASES}
                              if complete else None)
                    count_semantics = (
                        outcome.get("paramType") == "COUNT_OF_PARTICIPANTS" and
                        str(outcome.get("unitOfMeasure", "")).strip().casefold()
                        == "participants")
                    result["rows"].append({
                        "rowKey": oid + [ci, gid], "outcomeKey": oid,
                        "classIndex": ci, "groupId": gid,
                        "parentClassCount": len(outcome.get("classes", [])),
                        "groupDefinitions": copy.deepcopy(
                            [g for g in groups if g.get("id") == gid]),
                        "classLiteral": copy.deepcopy(
                            {k: v for k, v in cls.items() if k != "categories"}),
                        "measurements": records,
                        "normalizedIntegerCells": counts,
                        "normalizationStatus": ("four-exact-integer-cells" if complete
                                                else "adjudication-required"),
                        "duplicateAliases": [k for k in ALIASES if len(mapped[k]) > 1],
                        "explicitParticipantCountSemantics": count_semantics,
                        "selectedCategorySum": sum(counts.values()) if complete else None,
                        "denominators": choose_denominator(outcome, cls, gid),
                    })
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--kind", choices=("archived", "live-capture", "synthetic"),
                   required=True)
    p.add_argument("--revision")
    p.add_argument("--nct-id", action="append", help="Filter output; preserve source indices")
    p.add_argument("--source-url")
    p.add_argument("--retrieved-utc")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    source = {"kind": args.kind, "revision": args.revision,
              "url": args.source_url, "retrievedUtc": args.retrieved_utc}
    document, receipt = load_verified(args.input.read_bytes(),
                                      args.expected_sha256, source)
    output = extract(document, receipt, args.nct_id)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({"schema": SCHEMA, "outcomes": len(output["outcomes"]),
                      "rows": len(output["rows"]), "inputSHA256": receipt["sha256"]}))


if __name__ == "__main__":
    main()
