"""Validate source evidence and materialize immutable, incremental reader checkpoints.

Usage: python -B checkpoint.py [--write]
No semantic judgment is inferred by this program. The reader supplies notes.
"""
import hashlib
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
MODULES = ["identificationModule", "conditionsModule", "descriptionModule",
           "eligibilityModule", "armsInterventionsModule", "designModule", "statusModule"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def pointer(data, path):
    for component in path.strip("/").split("/"):
        component = component.replace("~1", "/").replace("~0", "~")
        data = data[int(component)] if isinstance(data, list) else data[component]
    return data


def checkpoint():
    frozen = load(OUT / "freeze-receipt.json")
    for name, expected in frozen["sha256"].items():
        assert digest((OUT / name).read_bytes()) == expected, name
    protocol = load(OUT / "protocol.json")
    packet_path = OUT.parent / "trial-reference-expansion-emc-2026-09-05/source-packet.json"
    frame_path = packet_path.parent / "unfinished-pairs.json"
    assert digest(packet_path.read_bytes()) == protocol["source_packet_sha256"]
    assert digest(frame_path.read_bytes()) == protocol["unfinished_frame_sha256"]
    packet = load(packet_path)
    order = load(OUT / "work-order.json")
    frame = load(frame_path)
    assert len(order) == 74 and len({x["pair_id"] for x in order}) == 74
    assert {x["pair_id"] for x in order} == {x["pair_id"] for x in frame}
    notes = [(p, i, row) for p in sorted(OUT.glob("judgments-*.json"))
             for i, row in enumerate(load(p))]
    notes.sort(key=lambda item: item[2]["position"])
    assert [n["position"] for _, _, n in notes] == list(range(1, len(notes) + 1))
    labels = []
    for path, index, note in notes:
        pair = order[note["position"] - 1]
        record = packet[pair["nct_id"]]
        assert record["duplicate_copies_equal"], "Differing copies need explicit reconciliation"
        copy = record["copies"][0]
        ps = copy["record"]["protocolSection"]
        assert ps["identificationModule"]["nctId"] == pair["nct_id"]
        assert note["label"] in protocol["labels"]
        assert note["complete_saved_modules_read"] is True
        assert note["quotes"], "A semantic judgment needs source evidence"

        def evidence(source_path):
            return dict(source=copy["source"], source_sha256=copy["source_sha256"],
                        decoded_sha256=copy["decoded_sha256"],
                        pointer=copy["pointer"] + "/protocolSection/" + source_path)

        excerpts = []
        for source_path, quote in note["quotes"]:
            text = pointer(ps, source_path)
            assert isinstance(text, str) and quote in text, (pair, source_path, quote)
            start = text.index(quote)
            excerpts.append(dict(**evidence(source_path), excerpt=quote,
                                 char_start=start, char_end=start + len(quote)))
        modules = [dict(**evidence(m), module_present=m in ps,
                        module_sha256=digest(canonical(ps.get(m)))) for m in MODULES]
        labels.append(dict(**{k: v for k, v in note.items() if k != "quotes"},
                           **{k: v for k, v in pair.items() if k != "position"},
                           title=ps["identificationModule"]["briefTitle"],
                           state="first_reader_pending_independent_verification",
                           reader_context="existing_coordinator_context_not_independent",
                           evidence=excerpts, reviewed_modules=modules,
                           source_note=dict(file=path.name, pointer="/" + str(index),
                                            sha256=digest(path.read_bytes())),
                           external_protocol_reviewed=False,
                           additional_biomarker_established=False,
                           clinical_eligibility_established=False,
                           clinical_benefit_established=False,
                           snapshot_status=ps["statusModule"]["overallStatus"],
                           status_verified_date=ps["statusModule"].get("statusVerifiedDate"),
                           registry_primary_purpose=ps["designModule"].get("designInfo", {}).get("primaryPurpose"),
                           recruitment_uncertainty="Saved overall status only; no live site, phase, cohort or slot verification.",
                           binary_benchmark_use="not_permitted_before_independent_verification_and_endpoint_definition"))
    completed = {p["pair_id"] for p in labels}
    return dict(protocol_sha256=digest((OUT / "protocol.json").read_bytes()),
                source_packet_sha256=protocol["source_packet_sha256"],
                labels=labels, unfinished_pairs=[p for p in order if p["pair_id"] not in completed],
                independent_adjudication_complete=False)


if __name__ == "__main__":
    result = checkpoint()
    path = OUT / f"first-reader-checkpoint-{len(result['labels']):04d}.json"
    if "--write" in sys.argv:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    else:
        assert load(path) == result, "Checkpoint differs from source-linked notes"
    print(json.dumps(dict(checkpoint=path.name, reviewed=len(result["labels"]),
                          unfinished=len(result["unfinished_pairs"]),
                          source_excerpts=sum(len(r["evidence"]) for r in result["labels"]),
                          reviewed_modules=sum(len(r["reviewed_modules"]) for r in result["labels"]),
                          sha256=digest(path.read_bytes()))))
