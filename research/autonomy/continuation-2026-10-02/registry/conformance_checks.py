"""Behavioral checks; synthetic inputs are explicitly labeled."""
import copy
import json
from registry_literal_extractor import extract, load_verified, digest, canonical

def source_for(document):
    raw = canonical(document)
    return load_verified(raw, digest(raw), {"kind": "synthetic"})

def synthetic_checks():
    def denominator(value):
        return {"units": "Participants", "counts": [{"groupId": "OG000", "value": value}]}
    categories = [{"title": k, "measurements": [{"groupId": "OG000", "value": str(v),
                   "comment": "synthetic retained comment"}]}
                  for k, v in zip(("CR", "PR", "SD", "PD"), (1, 2, 3, 4))]
    om = {"title": "SYNTHETIC fixture", "description": "Not patient data",
          "paramType": "COUNT_OF_PARTICIPANTS", "unitOfMeasure": "Participants",
          "groups": [{"id": "OG000", "title": "synthetic group"}],
          "denoms": [denominator("10")], "classes": [{"categories": categories}]}
    def run(outcome):
        doc = {"protocolSection": {"identificationModule": {"nctId": "SYNTHETIC"}},
               "resultsSection": {"outcomeMeasuresModule": {"outcomeMeasures": [outcome]}}}
        original = copy.deepcopy(doc)
        output = extract(*source_for(doc))
        assert doc == original, "extractor mutated input"
        assert output["outcomes"][0]["literal"] == outcome, "literal loss"
        return output["rows"]
    a = copy.deepcopy(om)
    a["classes"][0]["categories"].append(copy.deepcopy(categories[0]))
    assert run(a)[0]["normalizedIntegerCells"] is None, "duplicate alias silently selected"
    a = copy.deepcopy(om)
    a["classes"][0]["categories"][0]["measurements"][0]["value"] = "NA"
    a["classes"][0]["categories"][1]["measurements"][0]["value"] = "-2"
    assert run(a)[0]["normalizedIntegerCells"] is None, "invalid count treated as zero"
    a = copy.deepcopy(om)
    a["denoms"].append(denominator("11"))
    assert run(a)[0]["denominators"]["selectedParticipantEntry"] is None
    a = copy.deepcopy(om)
    a["classes"].append({"title": "unmeasured class", "categories": []})
    rows = run(a)
    assert len(rows) == 2 and all(r["parentClassCount"] == 2 for r in rows)
    assert all(r["denominators"]["selectedParticipantEntry"] is None for r in rows)
    a = copy.deepcopy(om)
    a["paramType"], a["unitOfMeasure"] = "MEAN", "Months"
    a["classes"][0]["categories"][0]["measurements"][0].update(
        spread="1.4", lowerLimit="0.2", upperLimit="2.1")
    row = run(a)[0]
    assert not row["explicitParticipantCountSemantics"]
    assert row["measurements"][0]["measurementLiteral"]["spread"] == "1.4"
    try:
        load_verified(b"{}", "0" * 64, {"kind": "synthetic"})
    except ValueError:
        pass
    else:
        raise AssertionError("checksum mismatch accepted")
    doc = {"studies": [
        {"protocolSection": {"identificationModule": {"nctId": "SKIPPED"}}},
        {"protocolSection": {"identificationModule": {"nctId": "SYNTHETIC"}},
         "resultsSection": {"outcomeMeasuresModule": {"outcomeMeasures": [om]}}}]}
    output = extract(*source_for(doc), nct_ids={"SYNTHETIC"})
    assert output["outcomes"][0]["outcomeKey"][1] == 1
    assert output["outcomes"][0]["sourcePointer"].startswith("/studies/1/")
    return 7

def real_checks(document, receipt, fixtures):
    """Run only cases present; return IDs so CI can enforce complete coverage."""
    output = extract(document, receipt, {c["nctId"] for c in fixtures["cases"]})
    present = {o["outcomeKey"][2] for o in output["outcomes"]}
    completed = []
    for case in fixtures["cases"]:
        nct = case["nctId"]
        if nct not in present:
            continue
        for check in case.get("checks", []):
            matches = [r for r in output["rows"]
                       if r["outcomeKey"][2] == nct
                       and r["outcomeKey"][3] == check["outcomeIndex"]
                       and r["classIndex"] == check["classIndex"]
                       and r["groupId"] == check["groupId"]]
            assert len(matches) == 1, (case["id"], "nonunique row")
            row = matches[0]
            assert row["normalizedIntegerCells"] == dict(
                zip(("CR", "PR", "SD", "PD"), check["cells"])), case["id"]
            den = row["denominators"]["selectedParticipantEntry"]
            assert den is not None
            assert (den["integerValue"], den["scope"]) == (
                check["participantDenominator"], check["denominatorScope"])
            retained = [m for m in row["measurements"] if
                        m["categoryLiteral"].get("title") == check["retainedLabel"]]
            assert len(retained) == 1 and retained[0]["normalizedCategory"] is None
        keys = []
        for check in case.get("identityChecks", []):
            matches = [o for o in output["outcomes"] if o["outcomeKey"][2] == nct
                       and o["outcomeKey"][3] == check["outcomeIndex"]]
            assert len(matches) == 1
            groups = [g for g in matches[0]["literal"]["groups"]
                      if g["id"] == check["groupId"]]
            assert len(groups) == 1 and groups[0]["title"] == check["groupTitle"]
            keys.append(matches[0]["outcomeKey"])
        if keys:
            assert keys[0] != keys[1], "outcome-local identity collapsed"
        completed.append(case["id"])
    return completed
