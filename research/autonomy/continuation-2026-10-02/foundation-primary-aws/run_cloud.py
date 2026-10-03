"""Single new-source execution; reuse historical correction artifact, no refit."""
import hashlib,json,os,pathlib,platform,shutil,subprocess,sys,time,urllib.request
out=pathlib.Path(sys.argv[1]); old=pathlib.Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
inputs=out.parent/"foundation-primary-inputs"; inputs.mkdir(exist_ok=True)
code=pathlib.Path(__file__).resolve().parent
receipt={"revision":os.environ["GITHUB_SHA"],"run_id":os.environ["GITHUB_RUN_ID"],"python":platform.python_version(),"started_unix":time.time(),"steps":[]}
def run(name,cmd,limit):
    t=time.monotonic()
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=limit)
    (out/(name+".stdout")).write_text(r.stdout);(out/(name+".stderr")).write_text(r.stderr)
    receipt["steps"].append({"name":name,"command":cmd,"exit_code":r.returncode,"seconds":time.monotonic()-t})
    if r.returncode: raise RuntimeError(name+" failed")
def verify(p,n,sha):
    raw=p.read_bytes()
    if len(raw)!=n or hashlib.sha256(raw).hexdigest()!=sha: raise ValueError(p.name+" identity mismatch")
def fetch(name,url,n,sha):
    with urllib.request.urlopen(url,timeout=40) as r:
        if r.status!=200:raise ValueError("Unexpected input HTTP status")
        b=r.read(n+1)
    if len(b)!=n or hashlib.sha256(b).hexdigest()!=sha:raise ValueError(name+" identity mismatch")
    p=inputs/name;p.write_bytes(b)
    return p
try:
    if shutil.disk_usage(".").free<11*1024**3:raise ValueError("Insufficient cloud headroom")
    matches=list(old.rglob("data_sv.identity_corrected.tsv"))
    if len(matches)!=1:raise ValueError("Corrected artifact member missing or ambiguous")
    verify(matches[0],180952,"2c910856e5e483c3774af5d0192b6118536f368aade8f05960bb123014a20184")
    corrected=inputs/"data_sv.identity_corrected.tsv";shutil.copyfile(matches[0],corrected)
    mapping=fetch("mapping.json","https://raw.githubusercontent.com/trimcrae/Rare-cancers/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/Foundation-complete-rearrangement-source-mapping.json",1679613,"341f64562039230c581aefb7f03d7da4769969a79290217962216f3d7e567a5e")
    export=fetch("data_sv.txt","https://media.githubusercontent.com/media/cBioPortal/datahub/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/public/sarcoma_msk_2022/data_sv.txt",180393,"d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701")
    run("primary-byte-receipt",[sys.executable,str(code/"fetch_primary_aws.py"),"--out",str(inputs/"primary.xls")],100)
    checker=code.parent/"foundation"/"foundation_primary_workbook_check.py"
    run("primary-independent-check",[sys.executable,str(checker),"--workbook",str(inputs/"primary.xls"),"--mapping",str(mapping),"--export",str(export),"--corrected",str(corrected)],180)
    result=json.loads((out/"primary-independent-check.stdout").read_text())
    if result["status"]!="passed":raise ValueError("Checker did not pass")
    receipt["status"]="passed"
except Exception as e:
    receipt.update(status="failed",error_type=type(e).__name__,error=str(e))
finally:
    receipt["finished_unix"]=time.time()
    receipt["inputs"]=[{"name":p.name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(inputs.glob("*")) if p.is_file()]
    receipt["free_bytes_after"]=shutil.disk_usage(".").free
    (out/"execution.json").write_text(json.dumps(receipt,indent=2)+"\n")
if receipt["status"]!="passed":sys.exit(1)
