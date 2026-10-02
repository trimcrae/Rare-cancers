"""V2 bounded context/family/version repair; accepted v1 remains unchanged."""
import argparse
from collections import Counter
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import time
import zipfile

SCHEMA = "registry-outcome-family-companion/2"
# A finite lexical vocabulary, not a clinical equivalence ontology. Longest names first.
FAMILY = re.compile(r"(?<![A-Za-z])(?P<modifier>modified\s+|revised\s+)?"
    r"(?P<name>Response\s+Evaluation\s+Criteria\s+in\s+Solid\s+Tumou?rs?"
    r"|World\s+Health\s+Organization|irRC[-\s]RECIST|irRECIST|iRECIST|RECIST"
    r"|iwCLL|irRC|iRANO|RANO|WHO|Lugano|Cheson|Macdonald)(?![A-Za-z])", re.I)
NAMES = {s.lower(): s for s in ("irRC-RECIST", "irRECIST", "iRECIST", "RECIST",
    "iwCLL", "irRC", "iRANO", "RANO", "WHO", "Lugano", "Cheson", "Macdonald")}
# Fixed connectors only: never search ahead through arbitrary words for a number.
VERSION = re.compile(r"\s*\)?\s*(?:\(\s*RECIST\s*\)\s*)?"
    r"(?:(?:response\s+|evaluation\s+)?criteria\s*)?\(?\s*"
    r"(?:version\s*|v\.?\s*)?(?P<number>\d+(?:\.\d+)*)(?![\w.]?\w)", re.I)
WHO_CRITERIA = re.compile(r"^\s*\)?\s*(?:response\s+|evaluation\s+)?criteria\b", re.I)
# History must modify assessment or study use, not patients or comparator controls.
# This finite grammar deliberately does not resolve arbitrary temporal discourse.
HISTORICAL = re.compile(
    r"\b(?:historically|previously|formerly)\s+"
    r"(?:assessed|evaluated|used|applied|defined)\b"
    r"|\bhistorical\s+(?:assessment|evaluation|criteria)\b"
    r"|\b(?:prior|earlier)\s+(?:study|studies)\s+"
    r"(?:using|used|assessed|evaluated|applied)\b", re.I)
USE = re.compile(r"\b(using|per|according\s+to|based\s+on|assess\w*|evaluat\w*|defined\s+by)\b", re.I)
NEGATIVE = re.compile(r"\b(?:not\s+(?:using\s+|per\s+)?|rather\s+than\s+|instead\s+of\s+)$", re.I)
ROLE_NAMES = {"complete response": "CR", "complete remission": "CR",
              "partial response": "PR", "partial remission": "PR",
              "stable disease": "SD", "progressive disease": "PD",
              "unconfirmed progressive disease": "UPD", "confirmed progressive disease": "CPD"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def sentence_at(text, start, end):
    # Periods within a version number are not sentence boundaries.
    cuts = [0] + [m.end() for m in re.finditer(r"[.!?](?!\d)\s+|\n+", text)] + [len(text)]
    lo = max(p for p in cuts if p <= start)
    hi = min(p for p in cuts if p >= end)
    return lo, hi, text[lo:hi]


def classify_context(outcome):
    mentions = []
    for field in ("title", "description"):
        text = str(outcome.get(field) or "")
        for match in FAMILY.finditer(text):
            raw_name = match["name"]
            normalized = re.sub(r"\s+", " ", raw_name).lower()
            name = ("RECIST" if normalized.startswith("response evaluation criteria") else
                    "WHO" if normalized == "world health organization" else
                    NAMES[re.sub(r"\s+", "-", raw_name).lower()])
            # Case alone is insufficient: uppercase prose can also contain WHO pronouns.
            if name == "WHO" and (raw_name not in ("WHO",) and
                    normalized != "world health organization" or
                    not WHO_CRITERIA.match(text[match.end():])):
                continue
            version_match = VERSION.match(text[match.end():])
            mention_end = match.end() + (version_match.end() if version_match else 0)
            lo, hi, sentence = sentence_at(text, match.start(), mention_end)
            modifier = (match["modifier"] or "").strip().lower()
            version = version_match["number"] if version_match else None
            prefix = text[max(lo, match.start()-60):match.start()]
            negative = bool(NEGATIVE.search(prefix) or
                re.search(r"\bnot\b[^.;\n]{0,50}$", prefix, re.I) or
                re.search(r"\b(?:not\s+(?:used|applied|assessed|evaluated)|never\s+used)\b", sentence, re.I))
            # Description needs an explicit assessment cue or definition, not a bare citation.
            definition = bool(re.match(r"\s*:", text[mention_end:hi]))
            supported = field == "title" or bool(USE.search(sentence)) or definition
            mentions.append({"field": field, "start": match.start(), "end": mention_end,
                "literal": text[match.start():mention_end], "sentenceLiteral": sentence,
                "baseName": name, "modifier": modifier,
                "version": version,
                "explicitAssessmentContext": supported, "negated": negative,
                "historicalContext": bool(HISTORICAL.search(sentence))})
    evidence = [m for m in mentions if m["explicitAssessmentContext"]]
    identities = {(m["baseName"], m["modifier"]) for m in evidence}
    versions = {m["version"] for m in evidence if m["version"] is not None}
    ambiguous = len(identities) > 1 or len(versions) > 1 or any(m["negated"] or m["historicalContext"] for m in evidence)
    status = "ambiguous" if ambiguous else "assigned" if evidence else "unknown"
    chosen = evidence[0] if status == "assigned" else None
    name = ((chosen["modifier"] + " " if chosen["modifier"] else "") + chosen["baseName"]) if chosen else None
    return {"status": status, "familyName": name,
            "criteriaVersion": next(iter(versions)) if len(versions) == 1 and chosen else None,
            "versionStatus": "source-explicit" if chosen and versions else "not-established",
            "mentions": mentions, "evidenceStatus": "explicit-in-outcome" if chosen else
                "conflicting-or-negated-context" if ambiguous else "not-established",
            "crossOutcomeEquivalence": "not-established", "poolingAllowed": False}


def lexical_role(title):
    text = " ".join(str(title or "").casefold().split()).rstrip(".")
    # Confirmation is a distinct lexical state, never folded into PD.
    m = re.fullmatch(r"(i|ir)?(cr|pr|sd|pd|upd|cpd)", text)
    if m:
        return {"role": m[2].upper(), "prefix": m[1] or ""}
    if text in ROLE_NAMES:
        return {"role": ROLE_NAMES[text], "prefix": ""}
    m = re.fullmatch(r"(.+?)\s*\((i|ir)?(cr|pr|sd|pd|upd|cpd)\)", text)
    if m and m[1] in ROLE_NAMES and ROLE_NAMES[m[1]] == m[3].upper():
        return {"role": m[3].upper(), "prefix": m[2] or ""}
    return None


def integer(value):
    return int(str(value)) if not isinstance(value, bool) and re.fullmatch(r"[0-9]+", str(value)) else None


def accompany(unit, source_row, outcome, coordinates):
    accepted = canonical(source_row)
    family = classify_context(outcome)
    roles, cells, mismatch = {}, [], []
    immune = family["familyName"] and any(t in family["familyName"] for t in ("irRC", "irRECIST", "iRECIST", "iRANO"))
    for m in source_row["measurements"]:
        role = lexical_role(m["categoryLiteral"].get("title"))
        cell = {"categoryIndex": m["categoryIndex"], "measurementIndex": m["measurementIndex"],
                "categoryLiteral": copy.deepcopy(m["categoryLiteral"]),
                "measurementLiteral": copy.deepcopy(m["measurementLiteral"]),
                "lexicalRole": role, "familyRole": role["role"] if role and family["status"] == "assigned" else None}
        if role and role["prefix"] and family["status"] == "assigned" and not immune:
            mismatch.append(m["categoryIndex"])
            cell["familyRole"] = None
        cells.append(cell)
        if cell["familyRole"]:
            roles.setdefault(cell["familyRole"], []).append(cell)
    duplicates = sorted(k for k, values in roles.items() if len(values) > 1)
    progression_states = sorted(set(roles) & {"UPD", "CPD"})
    complete = (family["status"] == "assigned" and not mismatch and not duplicates
                and not progression_states and all(len(roles.get(k, [])) == 1 and
                integer(roles[k][0]["measurementLiteral"].get("value")) is not None
                for k in ("CR", "PR", "SD", "PD")))
    family_counts = {k: integer(roles[k][0]["measurementLiteral"]["value"]) for k in ("CR", "PR", "SD", "PD")} if complete else None
    status = "ambiguous" if family["status"] == "ambiguous" or duplicates or mismatch else family["status"]
    suffix_present = any(c["lexicalRole"] and c["lexicalRole"]["prefix"] for c in cells)
    if family["status"] == "unknown" and suffix_present:
        family["evidenceStatus"] = "label-only-no-family-inference"
    require(canonical(source_row) == accepted, "Accepted input row mutated")
    return {"unit": unit, "status": status, "familyScopeKey": unit[:2],
            "sourceCoordinates": copy.deepcopy(coordinates), "family": family,
            "categoryAssignments": cells, "duplicateRoles": duplicates,
            "labelContextMismatchCategoryIndices": mismatch,
            "separateProgressionStates": progression_states,
            "withinFamilyFourCells": family_counts,
            "roleMapStatus": "four-literal-family-cells" if complete else "retain-literal-or-separate-state",
            "acceptedRowSHA256": digest(accepted), "acceptedRowUnchanged": copy.deepcopy(source_row),
            "contextLiteral": {k: copy.deepcopy(outcome.get(k)) for k in
                ("title", "description", "timeFrame", "populationDescription", "paramType", "unitOfMeasure")},
            "scope": "Lexical roles within a source-named outcome family; not clinical criteria implementation or ORR"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("inputs.json"))
    parser.add_argument("--reviewed", type=Path, default=Path(__file__).with_name("reviewed-27.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    require(args.zip.stat().st_size == manifest["zipBytes"], "ZIP size mismatch")
    raw = args.zip.read_bytes()
    require(digest(raw) == manifest["zipSHA256"], "ZIP digest mismatch")
    gold_bytes = args.reviewed.read_bytes()
    require(len(gold_bytes) == manifest["reviewed27"]["bytes"] and digest(gold_bytes) == manifest["reviewed27"]["sha256"], "Reviewed27 digest mismatch")
    needed = {"analysis/generic-literal-outcomes.json", "analysis/generic-literal-rows.json", "analysis/unit-comparison.json"}
    expected = {r["name"]: r for r in manifest["entries"]}
    docs = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())), "Duplicate ZIP member")
        for name in needed:
            entry = archive.getinfo(name)
            require(entry.file_size == expected[name]["bytes"], "ZIP entry size mismatch")
            body = archive.read(name)
            require(digest(body) == expected[name]["sha256"], "ZIP entry digest mismatch")
            docs[name.rsplit("/", 1)[1]] = json.loads(body)
    outcomes = {}
    for r in docs["generic-literal-outcomes.json"]:
        key = (r["nctId"], r["outcomeJSONSha256"])
        require(key not in outcomes and digest(canonical(r["literal"])) == key[1], "Outcome identity/hash mismatch")
        outcomes[key] = r["literal"]
    source_rows = docs["generic-literal-rows.json"]
    comparison = {tuple(r["unit"]): r for r in docs["unit-comparison.json"]}
    require(len(source_rows) == len(comparison) == 575, "Accepted575 scope mismatch")
    all_units = {tuple(r["unit"]) for r in source_rows}
    require(len(all_units) == 575 and all_units == set(comparison), "Accepted unit identity mismatch")
    results = []
    for r in source_rows:
        require(time.monotonic()-started < 120, "Two-minute companion deadline")
        key = tuple(r["unit"])
        accepted = r["row"]
        require(accepted["classIndex"] == key[2] and accepted["groupId"] == key[3], "Class/group mismatch")
        require(accepted["normalizedIntegerCells"] == comparison[key]["newCounts"], "Accepted normalization mismatch")
        require(r["sources"] == comparison[key]["sources"], "Coordinate receipt mismatch")
        results.append(accompany(r["unit"], accepted, outcomes[key[:2]], r["sources"]))
    by_unit = {tuple(r["unit"]): r for r in results}
    gold = json.loads(gold_bytes)["units"]
    require(len(gold) == len({tuple(r["unit"]) for r in gold}) == 27, "Reviewed scope mismatch")
    agreements = []
    for r in gold:
        result = by_unit[tuple(r["unit"])]
        selected = result["acceptedRowUnchanged"]["denominators"]["selectedParticipantEntry"]
        agreements.append({"unit": r["unit"], "familyMatches": result["family"]["familyName"] == r["familyNameLiteral"],
            "cellsMatch": result["withinFamilyFourCells"] == r["cells"],
            "denominatorMatches": bool(selected) and selected["integerValue"] == r["participantDenominator"] and selected["scope"] == r["denominatorScope"],
            "statusAssigned": result["status"] == "assigned"})
    require(all(all(v for k, v in r.items() if k != "unit") for r in agreements), "Reviewed27 agreement failed")
    summary = {"schema": SCHEMA, "status": "completed", "scope": "Known-corpus companion transfer; not held-out clinical validation",
        "sourceZipSHA256": digest(raw), "manifestSHA256": digest(manifest_bytes),
        "codeSHA256": digest(Path(__file__).read_bytes()), "units": len(results),
        "unitStatusCounts": dict(Counter(r["status"] for r in results)),
        "contextStatusCounts": dict(Counter(r["family"]["status"] for r in results)),
        "assignedFamilyUnitCounts": dict(Counter(r["family"]["familyName"] for r in results if r["family"]["status"] == "assigned")),
        "withinFamilyFourCellUnits": sum(r["withinFamilyFourCells"] is not None for r in results),
        "acceptedUnqualifiedFourCellUnitsUnchanged": sum(r["acceptedRowUnchanged"]["normalizedIntegerCells"] is not None for r in results),
        "reviewed27Agreements": agreements, "seconds": time.monotonic()-started,
        "limits": ["Finite vocabulary and cues; unknown does not mean source lacks a definition.",
                   "Family names are outcome-scoped, not equivalence assertions.",
                   "All literals, accepted row fields and denominator scopes remain unchanged."]}
    args.out.mkdir(parents=True, exist_ok=False)
    for name, value in (("family-companions.json", results),
                        ("outcome-literals.json", docs["generic-literal-outcomes.json"]),
                        ("summary.json", summary)):
        data = json.dumps(value, ensure_ascii=False, indent=2).encode()+b"\n"
        require(len(data) < 16*1024**2, "Output cap")
        (args.out/name).write_bytes(data)
    print("EMC_REGISTRY_FAMILY " + json.dumps({k:v for k,v in summary.items() if k not in ("reviewed27Agreements", "limits")}))


if __name__ == "__main__":
    main()
