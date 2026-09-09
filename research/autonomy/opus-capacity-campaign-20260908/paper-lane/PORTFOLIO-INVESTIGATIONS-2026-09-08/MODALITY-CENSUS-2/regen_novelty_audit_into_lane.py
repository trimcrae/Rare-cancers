#!/usr/bin/env python3
"""Regenerate census-novelty-audit.json INTO THIS LANE ONLY.

The tracked generator hard-codes OUT = research/modalities/census-novelty-audit.json. This wrapper
imports it unmodified and redirects OUT to this lane. The tracked artifact is never written, and the
generated file is never hand-edited.
"""
import hashlib, importlib.util, os, subprocess, sys

REPO = subprocess.run(["git","rev-parse","--show-toplevel"],capture_output=True,text=True,check=True).stdout.strip()
LANE = os.path.join(REPO,"research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                         "PORTFOLIO-INVESTIGATIONS-2026-09-08/MODALITY-CENSUS-2")
GEN = os.path.join(REPO,"research/modalities/census_novelty_audit.py")
TRACKED = os.path.join(REPO,"research/modalities/census-novelty-audit.json")
DEST = os.path.join(LANE,"census-novelty-audit.REGENERATED.json")

def stat(p):
    b=open(p,"rb").read(); return len(b), hashlib.sha256(b).hexdigest()

before_bytes, before_sha = stat(TRACKED)
print(f"BEFORE tracked {TRACKED}\n  bytes={before_bytes} sha256={before_sha}")

spec = importlib.util.spec_from_file_location("census_novelty_audit", GEN)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
assert mod.OUT == TRACKED, mod.OUT
mod.OUT = DEST                     # redirect: nothing is written to the tracked path
rc = mod.main()
after_bytes, after_sha = stat(DEST)
print(f"\nAFTER regenerated {DEST}\n  bytes={after_bytes} sha256={after_sha}")
assert stat(TRACKED) == (before_bytes, before_sha), "tracked file changed — abort"
print("tracked file unchanged: CONFIRMED")
sys.exit(rc)
