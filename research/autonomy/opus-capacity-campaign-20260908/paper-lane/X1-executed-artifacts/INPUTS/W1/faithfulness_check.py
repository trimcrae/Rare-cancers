#!/usr/bin/env python3
"""Independent faithfulness check. Does NOT import the builder.

For every provenanced cell: resolve the JSON path in a FRESH parse of the committed input and
require (a) the recorded value equals the JSON leaf exactly, and (b) its rendered form is present
in the emitted markdown table. Also re-verify the input digest and that registered_predictions is
byte-identical to the committed copy.
"""
import json, hashlib, re, sys

SRC = "research/modalities/emc-fet-construct-designs.json"
LANE = "/tmp/claude-0/w1-lane/"
raw = open(SRC, "rb").read()
dig = hashlib.sha256(raw).hexdigest()
d = json.loads(raw)
prov = json.load(open(LANE + "provenance-cells.json"))
md = open(LANE + "PROPOSED-supplementary-table-s3.md").read()

fail = []
if dig != prov["sha256"]:
    fail.append("DIGEST MISMATCH")

def resolve(path):
    cur = d
    for tok in re.findall(r"[A-Za-z_⛔][\w⛔]*|\[\d+\]", path):
        if tok.startswith("["):
            cur = cur[int(tok[1:-1])]
        else:
            cur = cur[tok]
    return cur

def fmt(v):
    return "yes" if v is True else "no" if v is False else str(v)

checked = 0
for c in prov["cells"]:
    if c["json_path"].startswith("("):        # declared UNRESOLVED, no source path
        if c["value"] != "UNRESOLVED":
            fail.append(f"{c['row']}/{c['column']}: unsourced cell is not UNRESOLVED")
        continue
    try:
        leaf = resolve(c["json_path"])
    except Exception as e:
        fail.append(f"{c['row']}/{c['column']}: path unresolvable ({e})")
        continue
    if leaf != c["value"]:
        fail.append(f"{c['row']}/{c['column']}: JSON {leaf!r} != emitted {c['value']!r}")
    if fmt(leaf).replace("|", "\\|") not in md:
        fail.append(f"{c['row']}/{c['column']}: rendered value absent from markdown")
    checked += 1

# registered_predictions untouched (read-only comparison against committed blob via git show)
import subprocess
committed = subprocess.run(["git", "show", "HEAD:" + SRC], capture_output=True, text=True).stdout
rp_now = json.dumps(d["rgg_dose_calibration_and_predictions"]["registered_predictions"], sort_keys=True)
rp_git = json.dumps(json.loads(committed)["rgg_dose_calibration_and_predictions"]["registered_predictions"], sort_keys=True)
if rp_now != rp_git:
    fail.append("registered_predictions differs from HEAD")
if hashlib.sha256(committed.encode()).hexdigest() != dig:
    fail.append("working-tree input differs from HEAD")

print(f"input sha256      : {dig}")
print(f"cells checked     : {checked} sourced + {len(prov['cells'])-checked} UNRESOLVED = {len(prov['cells'])}")
print(f"registered_predictions vs HEAD : {'IDENTICAL' if rp_now == rp_git else 'DIFFERS'} "
      f"({len(json.loads(rp_git)) if isinstance(json.loads(rp_git), list) else 'n/a'} entries)")
print(f"input file vs HEAD             : {'IDENTICAL' if hashlib.sha256(committed.encode()).hexdigest()==dig else 'DIFFERS'}")
print("RESULT: " + ("PASS — every emitted cell matches its JSON leaf and appears in the table" if not fail
                    else "FAIL\n" + "\n".join(fail)))
sys.exit(1 if fail else 0)
