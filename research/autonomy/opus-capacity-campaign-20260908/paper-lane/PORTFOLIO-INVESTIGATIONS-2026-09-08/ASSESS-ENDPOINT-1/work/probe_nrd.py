import json, re, os, glob
E="/home/user/Rare-cancers/research/manuscripts/endpoint/"
print("### V-PLACEBO20: is emc-endpoint-alternatives.json E10 committed and does it carry 20?")
p=E+"emc-endpoint-alternatives.json"
print("exists:", os.path.exists(p))
d=json.load(open(p))
k=[x for x in d if x.startswith("E10")]
print("E10 keys:", k)
s=json.dumps({kk:d[kk] for kk in k})
for m in re.finditer(r'.{160}20.{160}', s):
    if 'placebo' in m.group(0).lower() or 'objective' in m.group(0).lower():
        print("   ...", m.group(0).replace("\n"," ")[:330]); break
# direct search for a 20 percent placebo ORR
hits=[x for x in re.findall(r'"[^"]{0,200}(?:placebo|crossover)[^"]{0,200}"', s, re.I) if '20' in x]
for h in hits[:6]: print("   HIT:", h[:300])
print()
print("### A-CAPS: any totalCount / reported total (2027 / 16035) in COMMITTED files?")
import subprocess
for pat in ["2027","16035","totalCount","total_count","reported_total"]:
    r=subprocess.run(["grep","-rl","--include=*.json","--include=*.py","--include=*.md",pat,"/home/user/Rare-cancers/research/manuscripts/","/home/user/Rare-cancers/systems/"],capture_output=True,text=True)
    print(pat, "->", (r.stdout.strip().splitlines() or ["(none)"])[:8])
print()
c=json.load(open(E+"endpoint-corpus.json"))
print("C5_retrieval_provenance keys:", json.dumps(c["C5_retrieval_provenance"])[:1500])
