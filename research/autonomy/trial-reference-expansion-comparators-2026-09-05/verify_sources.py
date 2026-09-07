"""Reproduce the completed first-reader package against original archived pages.

This checks provenance and checkpoint preservation, not independent semantics.
Run with --write to preserve a new, immutable verification receipt.
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

from checkpoint import OUT, canonical, checkpoint, digest, load, pointer

ROOT = OUT.parents[2]


def verify():
    current = checkpoint()
    final_path = OUT / "first-reader-checkpoint-0074.json"
    assert len(current["labels"]) == 74 and not current["unfinished_pairs"]
    assert load(final_path) == current
    order = load(OUT / "work-order.json")
    prefixes = {}
    for path in sorted(OUT.glob("first-reader-checkpoint-*.json")):
        old = load(path)
        n = len(old["labels"])
        assert old["labels"] == current["labels"][:n], path
        assert old["unfinished_pairs"] == order[n:], path
        assert old["independent_adjudication_complete"] is False
        prefixes[path.name] = digest(path.read_bytes())

    pages = {}

    def page(evidence):
        name = evidence["source"]
        if name not in pages:
            raw = (ROOT / name).read_bytes()
            decoded = gzip.decompress(raw) if name.endswith(".gz") else raw
            pages[name] = (digest(raw), digest(decoded), json.loads(decoded))
        raw_sha, decoded_sha, obj = pages[name]
        assert raw_sha == evidence["source_sha256"], name
        assert decoded_sha == evidence["decoded_sha256"], name
        return obj

    excerpt_count = module_count = copy_count = 0
    packet = load(OUT.parent / "trial-reference-expansion-emc-2026-09-05/source-packet.json")
    for row in current["labels"]:
        copies = packet[row["nct_id"]]["copies"]
        for copy in copies:
            obj = pointer(page(copy), copy["pointer"])
            assert obj == copy["record"], row["pair_id"]
            assert obj == copies[0]["record"], row["pair_id"]
            copy_count += 1
        for ev in row["evidence"]:
            value = pointer(page(ev), ev["pointer"])
            assert value[ev["char_start"]:ev["char_end"]] == ev["excerpt"]
            excerpt_count += 1
        for ev in row["reviewed_modules"]:
            obj = page(ev)
            if ev["module_present"]:
                value = pointer(obj, ev["pointer"])
            else:
                parent, key = ev["pointer"].rsplit("/", 1)
                assert key not in pointer(obj, parent)
                value = None
            assert digest(canonical(value)) == ev["module_sha256"]
            module_count += 1
    return {
        "scope": "Provenance and reproduction of coordinator first-reader judgments; not independent semantic adjudication",
        "checkpoint": final_path.name,
        "checkpoint_sha256": digest(final_path.read_bytes()),
        "pairs": len(current["labels"]),
        "unfinished_pairs": len(current["unfinished_pairs"]),
        "original_record_copies_checked": copy_count,
        "original_pages_checked": len(pages),
        "source_excerpts_checked": excerpt_count,
        "saved_modules_checked": module_count,
        "checkpoint_prefix_sha256": prefixes,
        "first_reader_label_counts": dict(Counter(x["label"] for x in current["labels"])),
        "independent_adjudication_complete": False,
        "clinical_eligibility_established": False,
        "retrieval_performance_established": False,
        "full_publication_gate_run": False,
        "ultra_review_run": False,
    }


if __name__ == "__main__":
    result = verify()
    receipt = OUT / "source-verification.json"
    if "--write" in sys.argv:
        with receipt.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    else:
        assert load(receipt) == result, "Verification receipt differs"
    print(json.dumps(result, ensure_ascii=False))
