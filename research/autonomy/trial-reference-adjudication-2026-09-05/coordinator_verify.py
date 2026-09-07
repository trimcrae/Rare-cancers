"""Independently check frozen labels against original compressed registry bytes.

This verifies provenance and coverage, not the medical correctness of labels.
Use --root for the checked repository; stdout is the machine-readable receipt.
"""
import argparse
import collections
import datetime
import gzip
import hashlib
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve(value, pointer):
    for key in pointer.split("/")[1:]:
        key = key.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def verify(root):
    folder = root / "research/autonomy/trial-reference-adjudication-2026-09-05"
    prior = root / "research/autonomy/trial-reference-repair-2026-09-05"
    freeze = read(folder / "independent-freeze-receipt.json")
    for base, entries in [(folder, freeze["sha256"]), (prior, freeze["input_sha256"])]:
        for name, expected in entries.items():
            assert digest((base / name).read_bytes()) == expected, name
    selection = read(prior / "selection.json")
    expected = collections.defaultdict(list)
    for stratum in selection["strata"]:
        for nct in stratum["selected_ids"]:
            expected[stratum["diagnosis"] + "|" + nct].append(
                {"set": "metadata", "stratum": stratum["stratum"]})
    for anchor in selection["challenge_anchors"]:
        for diagnosis in anchor["diagnoses"]:
            expected[diagnosis + "|" + anchor["nct_id"]].append(
                {"set": "challenge", "stratum": "anchor"})
    labels = read(folder / "independent-labels.json")
    pairs = labels["pairs"]
    assert len(pairs) == len(expected) == 49
    assert {p["pair_id"] for p in pairs} == set(expected)
    assert not labels["prior_labels_read"] and not labels["unreviewed_ids"]
    evidence = read(folder / "source-evidence.json")["evidence"]
    index = {e["evidence_id"]: e for e in evidence}
    assert len(index) == len(evidence)
    cache = {}
    quotes = values = 0
    for entry in evidence:
        name = entry["source"]
        path = (root / name).resolve()
        assert path.is_relative_to(root.resolve()), name
        raw = path.read_bytes()
        assert digest(raw) == entry["source_sha256"], name
        if name not in cache:
            cache[name] = json.loads(gzip.decompress(raw))
        value = resolve(cache[name], entry["pointer"])
        if "excerpt" in entry:
            excerpt = value[entry["start_codepoint"]:entry["end_codepoint"]]
            assert excerpt == entry["excerpt"], entry["evidence_id"]
            assert digest(excerpt.encode()) == entry["excerpt_utf8_sha256"]
            quotes += 1
        else:
            assert value == entry["value"], entry["evidence_id"]
            encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":")).encode()
            assert digest(encoded) == entry["value_canonical_sha256"]
            values += 1
    for pair in pairs:
        assert pair["memberships"] == expected[pair["pair_id"]]
        assert pair["eligibility_scope"]["label"] == pair["label"]
        for evidence_id in pair["evidence_ids"]:
            assert evidence_id in index
            assert evidence_id.startswith(pair["nct_id"] + ":")
        status = index[pair["nct_id"] + ":statusModule"]["value"]["overallStatus"]
        assert pair["current_availability"]["overall_status_snapshot"] == status
    reading = read(folder / "reading-log.json")
    assert {r["nct_id"] for r in reading["trials"]} == {p["nct_id"] for p in pairs}
    assert len(reading["trials"]) == 37 and not reading["unreviewed_ids"]
    result = {
        "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "root": str(root.resolve()), "status": "passed",
        "independent_labels_sha256": digest((folder / "independent-labels.json").read_bytes()),
        "freeze_sha256": digest((folder / "independent-freeze-receipt.json").read_bytes()),
        "unique_pairs": len(pairs), "trials": len(reading["trials"]),
        "source_pages": len(cache), "module_values": values, "exact_excerpts": quotes,
        "label_counts": dict(collections.Counter(p["label"] for p in pairs)),
        "scope": "Frozen artifact and raw source integrity, independent membership reconstruction and evidence coverage. Semantic validity and reading chronology require separate review."
    }
    adjudicated_path = folder / "adjudicated-reference.json"
    if adjudicated_path.exists():
        first = read(prior / "reference.json")
        first_index = {(p["diagnosis"], p["nct_id"]): p for p in first["pairs"]}
        independent_index = {(p["diagnosis"], p["nct_id"]): p for p in pairs}
        adjudicated = read(adjudicated_path)
        decisions = read(folder / "discrepancy/adjudication.json")
        decision_index = {d["pair_id"]: d for d in decisions["decisions"]}
        rows = adjudicated["pairs"]
        assert len(rows) == len(first_index) == len(decision_index) == 49
        assert {(p["diagnosis"], p["nct_id"]) for p in rows} == set(first_index)
        assert adjudicated["input_reference_sha256"] == digest((prior / "reference.json").read_bytes())
        changes = []
        for row in rows:
            key = row["diagnosis"], row["nct_id"]
            assert row["first_reader"] == first_index[key]
            assert row["independent_reader"] == independent_index[key]
            assert row["adjudication"] == decision_index[row["pair_id"]]
            final = row["adjudicated"]
            decision = row["adjudication"]
            assert decision["first_reader_label"] == row["first_reader"]["label"]
            assert decision["independent_label"] == row["independent_reader"]["label"]
            assert decision["adjudicated_label"] == final["label"]
            assert final["sets"] == row["first_reader"]["sets"]
            assert not final["clinical_eligibility_established"]
            assert not final["external_protocol_reviewed"]
            for evidence_id in decision["evidence_ids"]:
                assert evidence_id in index
                assert evidence_id.startswith(row["nct_id"] + ":")
            discrepant = decision["first_reader_label"] != decision["independent_label"]
            assert discrepant == decision["label_discrepancy"]
            if discrepant:
                changes.append({k: decision[k] for k in ["pair_id", "first_reader_label",
                                                       "independent_label", "adjudicated_label"]})
        assert len(changes) == decisions["label_discrepancy_count"]
        result["adjudication"] = {
            "reference_sha256": digest(adjudicated_path.read_bytes()),
            "both_readers_preserved_for_pairs": len(rows), "label_differences": changes,
            "all_decisions_reference_checked_source_evidence": True}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    print(json.dumps(verify(args.root), ensure_ascii=False, indent=2))
