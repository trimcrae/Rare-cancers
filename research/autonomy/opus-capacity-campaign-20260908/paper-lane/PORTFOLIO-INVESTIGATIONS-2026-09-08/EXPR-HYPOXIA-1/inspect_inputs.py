import json, hashlib, os, subprocess
REPO="/home/user/Rare-cancers"
FILES=["research/modalities/emc-expression-panels.json","research/modalities/emc-hypoxia-null-background.json"]
for f in FILES:
    p=os.path.join(REPO,f); h=hashlib.sha256(open(p,'rb').read()).hexdigest()
    st=os.stat(p)
    print(f, "bytes=%d"%st.st_size, "mtime=%s"%st.st_mtime, "sha256=%s"%h)
print("git status:", subprocess.run(["git","status","--porcelain"]+FILES,cwd=REPO,capture_output=True,text=True).stdout.strip() or "(clean)")
print("git log -1 for hypoxia:", subprocess.run(["git","log","-1","--format=%H %ci",  "--", FILES[1]],cwd=REPO,capture_output=True,text=True).stdout.strip())
print("git log -1 for panels:", subprocess.run(["git","log","-1","--format=%H %ci",  "--", FILES[0]],cwd=REPO,capture_output=True,text=True).stdout.strip())
d=json.load(open(os.path.join(REPO,FILES[1])))
def walk(o,pre="",depth=0):
    if depth>3: return
    if isinstance(o,dict):
        ks=list(o.keys())
        print(f"{pre} dict[{len(ks)}] keys={ks[:12]}{'...' if len(ks)>12 else ''}")
        for k in ks[:6]:
            walk(o[k],pre+"/"+str(k),depth+1)
    elif isinstance(o,list):
        print(f"{pre} list[{len(o)}] first={repr(o[0])[:200] if o else None}")
    else:
        print(f"{pre} {type(o).__name__} = {repr(o)[:200]}")
walk(d)
