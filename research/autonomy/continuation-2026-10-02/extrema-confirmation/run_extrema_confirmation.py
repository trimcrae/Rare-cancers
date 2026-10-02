"""Cloud-only full-corpus runner; no network calls. Feed hash-pinned local inputs."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import time

RESULT_BLOB = "54450defc4fac3fb1b9f159e3157a8f713f47f53"
PINS = {
    "catalogue": ("f231499b036e4c6b79f729cee0a44a4c482ab6215167e61c2fc0c4a3ceed7799",40363),
    "archive": ("4cabff15767f8d7b38aefc75fa46233a954d13ac7802010b672aee3d9723c580",356744),
    "gencode": ("5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56",183554921),
}
def require(ok, why):
    if not ok:
        raise ValueError(why)
def rows(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f,delimiter="\t"))
def digest(path):
    h=hashlib.sha256(); size=0
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block);size+=len(block)
    return h.hexdigest(),size
def certificates(designs, collections):
    """Conjoin both corpora; one attainment witness and exhaustive no-counterexample."""
    require(len(collections)==2,"both archive and GENCODE certificate collections required")
    keys={d["design_id"] for d in designs}
    require(len(keys)==len(designs),"duplicate design")
    indexed=[]
    for collection in collections:
        index={r["design_id"]:r for r in collection}
        require(len(index)==len(collection) and set(index)==keys,"certificate ID coverage")
        for row in collection:
            require(row["gap_attained"] in ("0","1") and row["gap_exceeded"] in ("0","1"),"certificate boolean")
            require(row["hamming_found"] in ("0","1","2","3"),"certificate Hamming range")
        indexed.append(index)
    verified=[]
    for d in designs:
        ident=d["design_id"]; h=d["union_hamming"]; g=d["union_gap"]
        require(type(h) is int and 0<=h<=2,"unsupported Hamming challenge")
        require(type(g) is int and (g==0 or 6<=g<=16),"invalid gap challenge")
        rs=[index[ident] for index in indexed]
        require(min(int(r["hamming_found"]) for r in rs)==h,ident+": Hamming certificate failed")
        require(not any(r["gap_exceeded"]=="1" for r in rs),ident+": longer complete-core tract exists")
        require(g==0 or any(r["gap_attained"]=="1" for r in rs),ident+": claimed gap maximum unattained")
        verified.append(ident)
    return verified
def main():
    p=argparse.ArgumentParser()
    for name in ("result","catalogue","archive","gencode","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args();start=time.monotonic()
    raw=a.result.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    require(blob==RESULT_BLOB,"result must match pinned Git blob")
    result=json.loads(raw);designs=result["designs"]
    require(len(designs)==220 and sum(d["control"] is False for d in designs)==215
            and sum(d["control"] is True for d in designs)==5,"design/control scope")
    receipts={}
    for name,(expected,size) in PINS.items():
        actual,n=digest(getattr(a,name))
        require((actual,n)==(expected,size),name+": source identity mismatch")
        receipts[name]={"sha256":actual,"bytes":n}
    catalogue=rows(a.catalogue);index={r["design_id"]:r for r in catalogue}
    require(len(catalogue)==len(index)==220,"catalogue count/unique IDs")
    require(set(index)=={d["design_id"] for d in designs},"catalogue/result ID agreement")
    for d in designs:
        r=index[d["design_id"]]
        require(d["target"]==r["target_RNA_DNA_alphabet_5to3"],"target identity")
        require(d["control"]==(r["control_only"]=="True") and r["control_only"] in ("True","False"),"control identity")
        require(d["antisense"]==r["antisense_5to3"]
                and d["target"]==d["antisense"].translate(str.maketrans("ACGT","TGCA"))[::-1],"target/core orientation")
        require(d["union_hamming_lower_bound"]==d["union_hamming_upper_bound"]==d["union_hamming"],"exact union bounds")
    a.out.mkdir(exist_ok=False,parents=True)
    here=Path(__file__).resolve().parent
    engine=a.out/"extrema-certificate"
    subprocess.run(["g++","-std=c++17","-O3","-Wall","-Wextra",str(here/"extrema_certificate.cpp"),"-lz","-o",str(engine)],check=True,timeout=120)
    subprocess.run(["python3",str(here/"test_extrema_certificate.py"),str(engine)],check=True,timeout=120)
    queries=a.out/"challenges.tsv"
    queries.write_text("".join(f'{d["design_id"]}\t{d["target"]}\t{d["union_hamming"]}\t{d["union_gap"]}\n' for d in designs),encoding="utf-8")
    collections=[];metadata={}
    for name in ("archive","gencode"):
        prefix=a.out/name
        subprocess.run([str(engine),str(queries),str(getattr(a,name)),
                        "archived" if name=="archive" else "gencode",str(prefix)],check=True,timeout=1800)
        collections.append(rows(str(prefix)+"-certificates.tsv"))
        ms=rows(str(prefix)+"-meta.tsv");require(len(ms)==1,"metadata row count")
        m={k:int(v) for k,v in ms[0].items()};metadata[name]=m
        expected=result["archive_corpus" if name=="archive" else "gencode_corpus"]
        for k in ("records","bases","unambiguous_windows","ambiguous_windows",
                  "parent_records","other_records","parent_windows","other_windows","query_count"):
            require(m[k]==expected[k],name+": corpus census mismatch "+k)
    ids=certificates(designs,collections)
    receipt={"schema":"aso-independent-union-extrema-certificate/1","status":"passed",
             "result_git_blob":blob,"result_sha256":hashlib.sha256(raw).hexdigest(),
             "source_receipts":receipts,"corpora":metadata,"designs_verified":len(ids),
             "research_target_designs":215,"annotation_error_controls":5,
             "hamming_extrema_certified":220,"complete_core_gap_extrema_certified":220,
             "verified_design_ids":ids,"seconds":time.monotonic()-start,
             "algorithm":"Literal Aho-Corasick dictionary of <=claimed-radius Hamming patterns and aligned complete-core gap intervals at claimed length and length+1",
             "limits":["Union of archived seven-gene FASTA and GENCODE v50 only.",
                       "Does not independently certify individual-stratum nonzero minima, censoring bounds, gap maxima, nearest counts, or rankings.",
                       "Shares Hamming-neighborhood mathematics with original; independent string representation/automaton instead of original two-bit hash lookup.",
                       "No tissue expression, cleavage, efficacy, or clinical safety inference."]}
    (a.out/"extrema-confirmation.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"passed","union_designs":len(ids),"output":str(a.out/"extrema-confirmation.json")}))
if __name__=="__main__":
    main()

