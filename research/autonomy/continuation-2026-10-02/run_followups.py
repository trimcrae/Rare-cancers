"""Bounded cloud follow-up jobs; repository and primary inputs remain pinned."""
import hashlib,json,os,pathlib,shutil,signal,subprocess,sys,time,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path.cwd()
lane=sys.argv[1]
assert lane in ("registry","extrema")
output=ROOT/("outputs-followup-"+lane);output.mkdir()
cache=ROOT/("inputs-followup-"+lane);cache.mkdir()
started=time.monotonic()
limit=900 if lane=="registry" else 2100
receipt={"lane":lane,"revision":os.environ.get("GITHUB_SHA"),"run_id":os.environ.get("GITHUB_RUN_ID"),"status":"started"}
def guard():
    if shutil.disk_usage(ROOT).free < 10.5*1024**3: raise RuntimeError("10 GiB reserve reached")
    if time.monotonic()-started > limit: raise TimeoutError("whole-lane deadline")
def fetch(url,name,size,expected):
    guard();path=cache/name;h=hashlib.sha256();n=0
    req=urllib.request.Request(url,headers={"User-Agent":"EMC-bounded-followup/1"})
    with urllib.request.urlopen(req,timeout=40) as source,path.open("xb") as out:
        if source.status!=200: raise RuntimeError("source status")
        while True:
            guard();chunk=source.read(1024*1024)
            if not chunk: break
            n+=len(chunk)
            if n>size: raise RuntimeError("source size exceeded")
            h.update(chunk);out.write(chunk)
    if n!=size or h.hexdigest()!=expected: raise RuntimeError("source hash/size mismatch: "+name)
    return path
try:
    assert shutil.disk_usage(ROOT).free >= 12*1024**3
    if lane=="registry":
        command=[sys.executable,str(HERE/"registry-full-replay/replay_full_registry.py"),"--source-dir",str(cache),"--out",str(output/"analysis"),"--download","--max-seconds","600"]
    else:
        base="https://raw.githubusercontent.com/trimcrae/Rare-cancers/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/results/"
        catalogue=fetch(base+"all-designs.tsv","all-designs.tsv",40363,"f231499b036e4c6b79f729cee0a44a4c482ab6215167e61c2fc0c4a3ceed7799")
        archive=fetch(base+"normal-reference-transcripts.fasta","archive.fasta",356744,"4cabff15767f8d7b38aefc75fa46233a954d13ac7802010b672aee3d9723c580")
        gencode=fetch("https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz","gencode.fa.gz",183554921,"5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56")
        command=[sys.executable,str(HERE/"extrema-confirmation/run_extrema_confirmation.py"),"--result",str(HERE/"results/aso-transcriptome.json"),"--catalogue",str(catalogue),"--archive",str(archive),"--gencode",str(gencode),"--out",str(output/"analysis")]
    with (output/"execution.log").open("w") as log:
        proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            while proc.poll() is None:
                guard();time.sleep(1)
        except BaseException:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            raise
    receipt.update(status="passed" if proc.returncode==0 else "failed",exit_code=proc.returncode,command=command)
except Exception as exc:
    receipt.update(status="failed",exit_code=1,error_type=type(exc).__name__,error=str(exc))
finally:
    receipt.update(elapsed_seconds=time.monotonic()-started,free_bytes_after=shutil.disk_usage(ROOT).free)
    (output/"execution-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("EMC_FOLLOWUP_RECEIPT "+json.dumps(receipt))
sys.exit(receipt["exit_code"])
