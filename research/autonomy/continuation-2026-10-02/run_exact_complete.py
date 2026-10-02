"""Bounded cloud recovery of uncaptured ASO exact witnesses and frozen header labels."""
import hashlib,json,os,pathlib,shutil,signal,subprocess,sys,time,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path.cwd()
output=ROOT/"outputs-exact-complete";output.mkdir()
cache=ROOT/"inputs-exact-complete";cache.mkdir()
started=time.monotonic()
receipt={"schema":"emc-exact-complete-execution/1","revision":os.environ.get("GITHUB_SHA"),"run_id":os.environ.get("GITHUB_RUN_ID"),"status":"started","purpose":"Recover six missing exact occurrences and release-specific transcript labels; accepted extrema/rankings unchanged"}
def guard():
    if shutil.disk_usage(ROOT).free < 10.5*1024**3: raise RuntimeError("10 GiB reserve reached")
    if time.monotonic()-started > 1320: raise TimeoutError("Whole-lane22-minute deadline")
def fetch():
    guard();path=cache/"gencode.v50.transcripts.fa.gz";h=hashlib.sha256();n=0
    url="https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz"
    request=urllib.request.Request(url,headers={"User-Agent":"EMC-exact-recovery/1"})
    with urllib.request.urlopen(request,timeout=40) as source,path.open("xb") as target:
        if source.status!=200: raise RuntimeError("Reference response status")
        while True:
            guard();chunk=source.read(1024*1024)
            if not chunk: break
            n+=len(chunk)
            if n>183554921: raise RuntimeError("Reference byte budget exceeded")
            h.update(chunk);target.write(chunk)
    if n!=183554921 or h.hexdigest()!="5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56": raise RuntimeError("Reference hash/size mismatch")
    receipt["reference"]={"url":url,"bytes":n,"sha256":h.hexdigest()}
    return path
def execute(command,logname):
    with (output/logname).open("w") as log:
        proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            while proc.poll() is None:
                guard();time.sleep(1)
        except BaseException:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            raise
    if proc.returncode: raise RuntimeError("Child failed: "+logname+" exit"+str(proc.returncode))
try:
    if shutil.disk_usage(ROOT).free < 12*1024**3: raise RuntimeError("Starting reserve")
    test=[sys.executable,str(HERE/"exact-match-complete/test_recover_exact_hits.py")]
    execute(test,"tests.log");receipt["tests"]="passed"
    fasta=fetch()
    command=[sys.executable,str(HERE/"exact-match-complete/recover_exact_hits.py"),
        "--result",str(HERE/"results/aso-transcriptome.json"),"--fasta",str(fasta),
        "--witnesses",str(HERE/"exact-match-annotation/witnesses.tsv"),
        "--ensembl",str(HERE/"exact-match-annotation/ensembl-transcripts.json"),
        "--release",str(HERE/"exact-match-annotation/ensembl-release.json"),
        "--out",str(output/"analysis")]
    receipt["command"]=command
    execute(command,"execution.log")
    receipt.update(status="passed",exit_code=0)
except Exception as exc:
    receipt.update(status="failed",exit_code=1,error_type=type(exc).__name__,error=str(exc))
finally:
    receipt.update(elapsed_seconds=time.monotonic()-started,free_bytes_after=shutil.disk_usage(ROOT).free)
    (output/"execution-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("EMC_EXACT_RECOVERY_RECEIPT "+json.dumps(receipt))
sys.exit(receipt["exit_code"])
