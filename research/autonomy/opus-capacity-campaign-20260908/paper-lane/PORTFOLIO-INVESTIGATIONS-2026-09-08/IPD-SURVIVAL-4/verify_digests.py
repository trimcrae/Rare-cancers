#!/usr/bin/env python3
"""Verify the five licensed PDFs in the local scratch cache against the digests the committed
census records. No network call: the files came from the local git object store."""
import hashlib, json, os, sys
CACHE = sys.argv[1]
doc = json.load(open("research/modalities/km-risk-row-detection.json"))
ok = True
for s in doc["sources"]:
    p = os.path.join(CACHE, s["source_id"] + ".pdf")
    b = open(p, "rb").read()
    h = hashlib.sha256(b).hexdigest()
    m = (h == s["pdf_sha256"]) and (len(b) == s["pdf_bytes"])
    ok &= m
    print(f"{s['source_id']:32s} recorded={s['pdf_sha256'][:16]}… measured={h[:16]}… "
          f"bytes {s['pdf_bytes']}/{len(b)} match={m}")
print("ALL_MATCH", ok)
sys.exit(0 if ok else 1)
