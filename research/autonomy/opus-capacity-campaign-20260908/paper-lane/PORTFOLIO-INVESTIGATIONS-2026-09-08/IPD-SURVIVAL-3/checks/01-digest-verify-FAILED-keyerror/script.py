import hashlib, json, os, sys
SCR = sys.argv[1]
art = json.load(open("research/modalities/km-risk-row-detection.json"))
ok = True
for s in art["sources"]:
    p = os.path.join(SCR, s["pdf"] if "pdf" in s else s["id"] + ".pdf")
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    b = os.path.getsize(p)
    m = (h == s["pdf_sha256"]) and (b == s.get("pdf_bytes", b))
    ok &= m
    print(f"{s['id']:32s} recorded={s['pdf_sha256']} measured={h} bytes={b}/{s.get('pdf_bytes')} match={m}")
print("ALL_MATCH", ok)
sys.exit(0 if ok else 1)
