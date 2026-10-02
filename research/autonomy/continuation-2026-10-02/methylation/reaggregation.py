#!/usr/bin/env python3
"""Reaggregate frozen methylation losses; stdout only, standard library."""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

REF = "da49c4e836533253825587f83656675dac4c913b"
BASE = "research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/"
FILES = {
    "fusion": "methylation-hallmark-fusion-score-transport-final.json",
    "cases": "methylation-hallmark-fusion-selected-cases-final.json",
    "grouped": "methylation-corrected-full-support-actual.json",
}
EXPECTED_SHA256 = {
    "fusion": "cbac90fa027c620f0b395d6a80365a4da0ab14d28c2410e9fc69318c83344aba",
    "cases": "1f8103cd8ee0366ee2097e21e5b043aa3d4eb58d8720121a2001e1a9b7876b39",
    "grouped": "e375e1f7b390c4a8bdb4be83e6d3e0cb5fc37c3bdec387215ae86b5daf153fbf",
}
EXPECTED_BYTES = {"fusion": 28903, "cases": 2797, "grouped": 525104}
parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
parser.add_argument("--source-dir", type=Path,
                    help="Read the three exact frozen filenames from this directory instead of git show")
args = parser.parse_args()
sources, data = {}, {}
for key, filename in FILES.items():
    path = BASE + filename
    if args.source_dir is None:
        raw = subprocess.check_output(["git", "-C", args.repo, "show", f"{REF}:{path}"])
    else:
        raw = (args.source_dir / filename).read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != EXPECTED_SHA256[key] or len(raw) != EXPECTED_BYTES[key]:
        raise ValueError(f"Frozen source digest/size mismatch: {filename}")
    sources[key] = {"repository": "trimcrae/Rare-cancers", "revision": REF,
                    "path": path, "sha256": actual_sha, "bytes": len(raw),
                    "input_mode": "directory" if args.source_dir is not None else "git-show"}
    data[key] = json.loads(raw)["result"]

fusion = data["fusion"]
classes = fusion["molecular_by_class"]
assert len(classes) == 12
assert sum(c["raw"]["n"] for c in classes.values()) == 120
metrics = {}
for model in ("raw", "reference_temperature"):
    metrics[model] = {}
    for name, field in (("NLL", "NLL_fusion_compatible_label_input_smoothed"),
                        ("Brier", "Brier_fusion_compatible_label")):
        macro = math.fsum(c[model][field] for c in classes.values()) / 12
        micro = math.fsum(c[model]["n"] * c[model][field] for c in classes.values()) / 120
        reported = fusion["molecular_annotation_concordance"][model][field]
        assert math.isclose(micro, reported, rel_tol=0, abs_tol=1e-12)
        metrics[model][name] = {"equal_class": macro, "profile_weighted": micro}

expected = {
    ("raw", "NLL"): (1.0742871213223848, 0.43886850867822524),
    ("reference_temperature", "NLL"): (1.8437918075204678, 0.4359242413670505),
    ("raw", "Brier"): (0.2365079526109961, 0.11232166666666671),
    ("reference_temperature", "Brier"): (0.19326224730468514, 0.03751010299478826),
}
for (model, metric), (macro, micro) in expected.items():
    for key, value in (("equal_class", macro), ("profile_weighted", micro)):
        assert math.isclose(metrics[model][metric][key], value, rel_tol=0, abs_tol=1e-12)

cases = data["cases"]["fusion_audit_selected_profiles"]
assert len(cases) == 3
assert all(not c["our_fusion_concordance"] for c in cases)
case_losses = [{"ID": c["ID"], "target_probability": c["temperature_fusion_target_score"],
                "NLL": -math.log(c["temperature_fusion_target_score"])} for c in cases]
total = 120 * metrics["reference_temperature"]["NLL"]["profile_weighted"]
three_loss = math.fsum(c["NLL"] for c in case_losses)
zero = [c for c in cases if c["raw_fusion_target_vote"] == 0]
assert len(zero) == 1
zero_loss = -math.log(zero[0]["temperature_fusion_target_score"])
assert math.isclose(zero_loss / total, 0.7872747192263749, rel_tol=0, abs_tol=1e-12)
assert math.isclose(three_loss / total, 0.9845830919609586, rel_tol=0, abs_tol=1e-12)
grouped = data["grouped"]["results"]["common_panel"]
assert grouped["profiles"] == 658 and len(grouped["classes"]) == 23
assert "EMCS" not in grouped["classes"]

result = {
    "schema": "methylation-fixed-loss-reaggregation/1", "sources": sources,
    "status": "executed assertions passed", "input_epsilon": 1e-6,
    "analysis": "post hoc descriptive reweighting of fixed saved predictions",
    "profiles": 120, "classes": 12, "metrics": metrics, "case_losses": case_losses,
    "transformed_total_NLL": total, "zero_vote_case_fraction_total_NLL": zero_loss / total,
    "three_discordant_cases_fraction_total_NLL": three_loss / total,
    "remaining_117_mean_transformed_NLL": (total - three_loss) / 117,
    "existing_original_score_below_0_9_stratum": fusion["molecular_original_score_below_0.9"],
    "grouped_panel": grouped,
    "limits": ["No new fits, exclusions, thresholds or outcome searches.",
               "Equal-class and profile-weighted losses target different case mixtures.",
               "Three classes have one profile each; no uncertainty interval inferred.",
               "Case contributions explain total loss; cases remain in every summary.",
               "Loss improvement alone does not establish clinical calibration."]}
print(json.dumps(result, indent=2, allow_nan=False))
