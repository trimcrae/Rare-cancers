"""Known-corpus transfer audit; standard library, no clinical response imputation."""
import argparse
import collections
import hashlib
import importlib.util
import json
import shutil
import time
import urllib.request
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unwrap(doc, key):
    require(isinstance(doc, dict), "Unexpected artifact envelope")
    if key in doc:
        return doc
    require(isinstance(doc.get("result"), dict) and key in doc["result"],
            "Missing expected result payload: " + key)
    return doc["result"]


def unit(row):
    return (row["nctId"], row["outcomeJSONSha256"],
            row["classIndex"], row["groupId"])


def parent(row):
    return row["nctId"], row["outcomeJSONSha256"], row["groupId"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=Path(__file__).with_name("expected-inputs.json"))
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--download", action="store_true", help="Cloud only; fetch missing pinned inputs")
    ap.add_argument("--max-seconds", type=int, default=600)
    args = ap.parse_args()
    started = time.monotonic()
    deadline = started + args.max_seconds

    def tick():
        require(time.monotonic() < deadline, "Whole replay deadline exceeded")

    manifest_raw = args.manifest.read_bytes()
    manifest = json.loads(manifest_raw)
    specs = manifest["sources"]
    require(len({s["name"] for s in specs}) == len(specs), "Duplicate source names")
    args.source_dir.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    # Reserve all inputs plus 64 MiB for bounded audit products, before any download.
    budget = sum(s["bytes"] for s in specs) + 64 * 1024**2
    if args.download:
        require(shutil.disk_usage(args.source_dir).free >= 10 * 1024**3 + budget,
                "Insufficient 10 GiB plus input/output reserve")
    receipts = []
    for spec in specs:
        tick()
        path = args.source_dir / spec["name"]
        if not path.exists():
            require(args.download, "Missing pinned input: " + spec["name"])
            partial = path.with_name(path.name + ".partial")
            req = urllib.request.Request(spec["url"], headers={"User-Agent": "EMC-known-corpus-replay/1"})
            created_partial = False
            try:
                count = 0
                with urllib.request.urlopen(req, timeout=25) as response, partial.open("xb") as out:
                    created_partial = True
                    require(response.status == 200, "Non-200 source response")
                    while True:
                        tick()
                        block = response.read(1024 * 1024)
                        if not block:
                            break
                        count += len(block)
                        require(count <= spec["bytes"], "Source exceeds pinned byte cap")
                        out.write(block)
                require(count == spec["bytes"], "Truncated source")
                require(sha(partial.read_bytes()) == spec["sha256"], "Downloaded SHA256 mismatch")
                partial.replace(path)
            finally:
                if created_partial and partial.exists():
                    partial.unlink()
        raw = path.read_bytes()
        require(len(raw) == spec["bytes"] and sha(raw) == spec["sha256"],
                "Pinned source mismatch: " + spec["name"])
        receipts.append(dict(spec, verified=True))
    roles = {s["role"]: s for s in specs if s["role"] != "raw"}

    def read_role(role):
        return json.loads((args.source_dir / roles[role]["name"]).read_bytes())

    reconciliation = unwrap(read_role("reconciliation"), "literalTables")
    old = unwrap(read_role("normalization"), "rows")
    compact = read_role("compact-input")["arms"]
    require(not reconciliation["errors"] and reconciliation["allInputRowsReconciled"],
            "Frozen source reconciliation was incomplete")
    require(old["inputSHA256"] == roles["reconciliation"]["sha256"], "Baseline chain mismatch")
    require(len(compact) == len(reconciliation["rows"]) == 552, "Historical compact scope changed")
    require(len(reconciliation["literalTables"]) == 552 and len(old["rows"]) == 575,
            "Historical table/unit scope changed")
    require(sum(r["fourExactCells"] is not None for r in old["rows"]) == 537,
            "Historical qualification scope changed")
    for mapping in reconciliation["rows"]:
        require(mapping["compactCells"] == compact[mapping["inputRow"]]["cells"],
                "Compact vectors do not match frozen mapping")
    module_spec = importlib.util.spec_from_file_location(
        "pinned_literal_extractor", args.source_dir / roles["extractor"]["name"])
    utility = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(utility)
    tables = {parent(t): t for t in reconciliation["literalTables"]}
    require(len(tables) == 552, "Duplicate parent identity")
    old_rows = {unit(r): r for r in old["rows"]}
    require(len(old_rows) == 575, "Duplicate old class-group identity")
    wanted = {(nct, outcome_hash) for nct, outcome_hash, _ in tables}
    wanted_ncts = {k[0] for k in wanted}
    expected_occurrences = set()
    for key, table in tables.items():
        for occ in table["sourceOccurrences"]:
            expected_occurrences.add((occ["sourceFile"], occ["studyIndex"],
                                      occ["outcomeIndex"], key[0], key[1], key[2]))
    require(len(expected_occurrences) == 564, "Historical occurrence scope changed")
    seen_occurrences = set()
    new_rows, coordinates = {}, collections.defaultdict(list)
    literal_outcomes = {}
    raw_counts = []
    for spec in (s for s in specs if s["role"] == "raw"):
        tick()
        raw = (args.source_dir / spec["name"]).read_bytes()
        doc, receipt = utility.load_verified(raw, spec["sha256"], dict(spec, kind="archived"))
        del raw
        studies = doc["studies"]
        raw_counts.append({"source": spec["name"], "studies": len(studies)})
        for si, study in enumerate(studies):
            tick()
            protocol = study.get("protocolSection", {})
            nct = protocol.get("identificationModule", {}).get("nctId")
            if nct not in wanted_ncts:
                continue
            outcomes = study.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
            for oi, outcome in enumerate(outcomes):
                outcome_hash = sha(canonical(outcome))
                if (nct, outcome_hash) not in wanted:
                    continue
                literal_outcomes[(nct, outcome_hash)] = outcome
                # Bounded adapter: literal protocol and full outcome unchanged. Rebase
                # temporary [0,0] positions to physical archived [study,outcome] below.
                envelope = {"studies": [{"protocolSection": protocol, "resultsSection": {
                    "outcomeMeasuresModule": {"outcomeMeasures": [outcome]}}}]}
                extracted = utility.extract(envelope, receipt)
                for row in extracted["rows"]:
                    gid, ci = row["groupId"], row["classIndex"]
                    pk = (nct, outcome_hash, gid)
                    if pk not in tables:
                        continue
                    occurrence = (Path(spec["name"]).stem, si, oi, nct, outcome_hash, gid)
                    seen_occurrences.add(occurrence)
                    row["outcomeKey"][1], row["outcomeKey"][3] = si, oi
                    row["rowKey"][1], row["rowKey"][3] = si, oi
                    key = (nct, outcome_hash, ci, gid)
                    coord = {"source": spec["name"], "sha256": spec["sha256"],
                             "pointer": f"/studies/{si}/resultsSection/outcomeMeasuresModule/outcomeMeasures/{oi}/classes/{ci}",
                             "groupId": gid,
                             "lastUpdatePostDateStruct": protocol.get("statusModule", {}).get("lastUpdatePostDateStruct")}
                    coordinates[key].append(coord)
                    comparable = {k: v for k, v in row.items() if k not in ("rowKey", "outcomeKey")}
                    if key in new_rows:
                        require(new_rows[key] == comparable, "Identical source outcome produced discordant rows")
                    else:
                        new_rows[key] = comparable
        del doc, studies
    old_only = sorted(set(old_rows) - set(new_rows))
    new_only = sorted(set(new_rows) - set(old_rows))
    comparisons, fidelity_errors = [], []
    for key in sorted(set(old_rows) & set(new_rows)):
        a, b = old_rows[key], new_rows[key]
        # Independent comparison with older frozen extraction: preserve multiplicity,
        # class fields, group definition and every category's literal value.
        av = [(z["categoryIndex"], z["categoryTitle"], z["valueLiteral"])
              for z in a["allLiteralMeasurements"]]
        bv = [(z["categoryIndex"], z["categoryLiteral"].get("title") or "",
               z["measurementLiteral"].get("value")) for z in b["measurements"]]
        literal_ok = (av == bv and a["classFields"] == b["classLiteral"]
                      and b["groupDefinitions"] == [a["groupLiteral"]])
        if not literal_ok:
            fidelity_errors.append({"unit": key, "kind": "literal/class/group mismatch"})
        entry = b["denominators"]["selectedParticipantEntry"]
        new_n = entry["integerValue"] if entry else None
        new_scope = entry["scope"] if entry else None
        old_scope = ("class" if a["chosenDenominatorScope"] == "class" else
                     "outcome" if a["chosenDenominatorScope"] == "overall-single-class" else None)
        if a["participantDenominator"] is None:
            old_scope = None
        old_aliases = [z.get("exactAlias", {}).get("category") if z.get("exactAlias") else None
                       for z in a["allLiteralMeasurements"]]
        new_aliases = [z["normalizedCategory"] for z in b["measurements"]]
        comparisons.append({"unit": key, "tableId": a["tableId"], "sources": coordinates[key],
            "literalFidelity": literal_ok, "oldCounts": a["fourExactCells"],
            "newCounts": b["normalizedIntegerCells"], "countVectorChanged": a["fourExactCells"] != b["normalizedIntegerCells"],
            "oldQualified": a["fourExactCells"] is not None,
            "newQualified": b["normalizedIntegerCells"] is not None,
            "oldDenominator": a["participantDenominator"], "newDenominator": new_n,
            "oldDenominatorScope": old_scope, "newDenominatorScope": new_scope,
            "oldDeclaredDenominatorScope": a["chosenDenominatorScope"],
            "oldClassCountForGroup": a["numberOfClasses"], "fullOutcomeClassCount": b["parentClassCount"],
            "denominatorValueChanged": a["participantDenominator"] != new_n,
            "denominatorScopeChanged": old_scope != new_scope,
            "explicitParticipantCountSemantics": b["explicitParticipantCountSemantics"],
            "aliasAssignmentsChanged": old_aliases != new_aliases,
            "aliasDifferences": [{"categoryIndex": z["categoryIndex"],
                "label": z["categoryLiteral"].get("title"), "old": old_aliases[i], "new": new_aliases[i]}
                for i, z in enumerate(b["measurements"]) if literal_ok and old_aliases[i] != new_aliases[i]]})
    unmatched = {"oldOnly": [{"unit": k, "sourceOccurrences": old_rows[k]["sourceOccurrences"]} for k in old_only],
        "newOnly": [{"unit": k, "sources": coordinates[k], "measurementCount": len(new_rows[k]["measurements"]),
                     "reason": "declared class/group retained without measurements" if not new_rows[k]["measurements"] else "populated unmatched unit",
                     "row": new_rows[k]} for k in new_only],
        "missingOccurrences": sorted(expected_occurrences - seen_occurrences),
        "additionalOccurrences": sorted(seen_occurrences - expected_occurrences)}
    transitions = collections.Counter(f"{r['oldQualified']}->{r['newQualified']}" for r in comparisons)
    unexpected_new = [k for k in new_only if new_rows[k]["measurements"]]
    good = not (old_only or unexpected_new or fidelity_errors
                or unmatched["missingOccurrences"] or unmatched["additionalOccurrences"])
    summary = {"schema": "registry-known-full-corpus-transfer/1", "status": "completed" if good else "integrity-review-required",
        "scope": "Same selected known corpus; not held-out validation, registry error rate, clinical ORR or a new retrieval cohort",
        "manifestSHA256": sha(manifest_raw), "inputReceipts": receipts, "rawStudyCounts": raw_counts,
        "historicalParents": len(tables), "historicalUnits": len(old_rows), "genericUnits": len(new_rows),
        "matchedUnits": len(comparisons), "oldOnlyUnits": len(old_only), "newOnlyUnits": len(new_only),
        "oldQualified": sum(r["fourExactCells"] is not None for r in old_rows.values()),
        "newQualifiedAllRetainedUnits": sum(r["normalizedIntegerCells"] is not None for r in new_rows.values()),
        "qualificationTransitions": dict(transitions),
        "matchedChangeCounts": {field: sum(r[field] for r in comparisons) for field in
            ("countVectorChanged", "denominatorValueChanged", "denominatorScopeChanged", "aliasAssignmentsChanged")},
        "matchedExplicitCountSemantics": sum(r["explicitParticipantCountSemantics"] for r in comparisons),
        "physicalOccurrences": len(seen_occurrences), "fidelityErrors": fidelity_errors,
        "seconds": time.monotonic() - started}
    outputs = {"summary.json": summary, "unit-comparison.json": comparisons,
               "unmatched-units.json": unmatched,
               "generic-literal-outcomes.json": [{"nctId": k[0], "outcomeJSONSha256": k[1], "literal": v}
                                                  for k, v in sorted(literal_outcomes.items())],
               "generic-literal-rows.json": [{"unit": k, "sources": coordinates[k], "row": v} for k, v in sorted(new_rows.items())]}
    total = 0
    for name, value in outputs.items():
        tick()
        raw = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        total += len(raw)
        require(total <= 64 * 1024**2, "Audit output cap exceeded")
        (args.out / name).write_bytes(raw)
    print("EMC_REGISTRY_FULL_TRANSFER " + json.dumps({k: v for k, v in summary.items()
        if k not in ("inputReceipts", "rawStudyCounts", "fidelityErrors")}))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
