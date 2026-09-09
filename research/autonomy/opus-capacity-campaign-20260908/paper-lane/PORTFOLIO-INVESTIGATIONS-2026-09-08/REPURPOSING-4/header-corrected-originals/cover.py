import sys
final=open(sys.argv[2]).read()
miss=[]
tot=0
for ln in open(sys.argv[1]):
    if ln.startswith('+++') or not ln.startswith('+'): continue
    t=ln[1:].rstrip('\n')
    if not t.strip(): continue
    tot+=1
    if t not in final: miss.append(t)
print("patch:",sys.argv[1]); print("added_nonblank_lines:",tot); print("missing_from_final:",len(miss))
for m in miss: print("  MISSING:",m)
