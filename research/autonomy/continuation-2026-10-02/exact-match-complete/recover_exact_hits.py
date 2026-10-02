"""Cloud-only uncapped recovery of 19 accepted exact-positive design targets.
No network, external packages, compiler, extrema search, or ranking recomputation.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import time

RESULT_SHA="ffec759ac33c734d8aa28aa2f71f9f2b5e8296c8ece0e21f8a744606ba1d37ec"
FASTA_SHA="5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56"
WITNESS_BLOB="ca711d16ecdec6cfd17c6775d321f88eae25d6a4"
ENSEMBL_SHA="e2257b8155635433fce8d49fda5039e20486497def7225f7dbe7682983ace50e"
RELEASE_SHA="86e87c46ae1a424702676493d024d0508ce60f6c951b0b2803ce10269e09c20c"
PARENTS={"EWSR1","TAF15","TCF12","FUS","TFG","NR4A3","PGR"}
COLUMNS=["design_id","stratum","metric","value","transcript","gene","start_0based",
         "end_0based_exclusive","window_5to3","gene_id","transcript_name",
         "transcript_biotype_gencode50","transcript_length","saved_previously"]
def require(ok,message):
    if not ok:
        raise ValueError(message)
def normalize(s):
    return "".join(s.split()).upper().replace("U","T")
def positions(sequence,target):
    start=sequence.find(target)
    while start>=0:
        yield start
        start=sequence.find(target,start+1)
def parse_header(header):
    fields=header.split("|")
    if fields[-1]=="":
        fields.pop()
    require(len(fields)==8,"Expected exactly eight GENCODE transcript FASTA header fields")
    tx,gene,hg,ht,tn,gn,length,biotype=fields
    require(re.fullmatch(r"ENST[0-9R]+\.[0-9]+(?:_PAR_Y)?",tx) is not None,"Unversioned/unrecognized transcript ID")
    require(re.fullmatch(r"ENSG[0-9R]+\.[0-9]+(?:_PAR_Y)?",gene) is not None,"Unversioned/unrecognized gene ID")
    require(all(v and not any(c.isspace() for c in v) for v in (tx,gene,tn,gn,biotype)),"Missing or unsafe header field")
    require(length.isdigit(),"Transcript length is not a nonnegative integer")
    return dict(transcript=tx,gene_id=gene,transcript_name=tn,gene=gn,
                transcript_length=int(length),transcript_biotype_gencode50=biotype,
                fasta_header=header)
def fasta_records(stream):
    header=None; parts=[]
    for line in stream:
        if line.startswith(">"):
            if header is not None:
                yield header,normalize("".join(parts))
            header=line[1:].rstrip("\r\n");parts=[]
        elif line.strip():
            require(header is not None,"Sequence before first FASTA header")
            parts.append(line)
    if header is not None:
        yield header,normalize("".join(parts))
def recover(records,targets,deadline=None):
    byseq=defaultdict(list)
    for ident,target in targets.items():
        require(len(target)==16 and set(target)<=set("ACGT"),"Invalid target")
        byseq[target].append(ident)
    hits=[];annotations={};seen=set();count=bases=0
    for header,seq in records:
        if deadline is not None:
            require(time.monotonic()<deadline,"Recovery exceeded bounded deadline")
        a=parse_header(header);tx=a["transcript"]
        require(tx not in seen,"Duplicate transcript identifier: "+tx);seen.add(tx)
        require(len(seq)==a["transcript_length"],"FASTA length mismatch: "+tx)
        count+=1;bases+=len(seq)
        for target,identifiers in byseq.items():
            for start in positions(seq,target):
                require(set(seq[start:start+16])<=set("ACGT"),"Ambiguous exact window")
                annotations[tx]=a
                for ident in identifiers:
                    hits.append(dict(design_id=ident,stratum="gencode_parent" if a["gene"] in PARENTS else "gencode_other",
                        metric="hamming",value="0",start_0based=start,end_0based_exclusive=start+16,
                        window_5to3=target,**{k:v for k,v in a.items() if k!="fasta_header"}))
        require(len(hits)<=10000,"Unexpected hit growth beyond bounded recovery scope")
    require(count>0,"Empty FASTA")
    return hits,annotations,dict(records=count,bases=bases)
def key(row):
    return row["design_id"],row["stratum"],row["transcript"],int(row["start_0based"])
def reconcile(hits,saved,designs):
    full={key(r):r for r in hits};old={key(r):r for r in saved}
    require(len(full)==len(hits),"Duplicate recovered identity")
    require(len(old)==len(saved),"Duplicate saved identity")
    for k,r in old.items():
        require(k in full,"Saved hit absent: "+str(k))
        require(r["metric"]=="hamming" and str(r["value"])=="0","Saved record not an exact Hamming hit")
        for field in ("gene","window_5to3"):
            require(r[field]==full[k][field],"Saved hit field mismatch: "+field)
    expected={}
    for d in designs:
        for s in ("gencode_parent","gencode_other"):
            v=d["strata"][s]
            expected[d["design_id"],s]=v["nearest_occurrences"] if v["min_hamming"]==0 else 0
    actual=Counter((r["design_id"],r["stratum"]) for r in hits)
    require(set(actual)<=set(expected),"Unexpected recovered design/stratum")
    require(all(actual[k]==v for k,v in expected.items()),"Accepted per-design/stratum census disagreement")
    for d in designs:
        for s in ("gencode_parent","gencode_other"):
            if expected[d["design_id"],s]:
                observed={r["gene"] for r in hits if (r["design_id"],r["stratum"])==(d["design_id"],s)}
                require(observed==set(d["strata"][s]["nearest_genes"]),"Accepted nearest-gene census disagreement")
    for r in hits:
        r["saved_previously"]=key(r) in old
    return [r for r in hits if key(r) not in old]
def compare_annotations(annotations,ensembl):
    rows=[]
    for tx,a in sorted(annotations.items()):
        stable,version=tx.split(".",1);b=ensembl.get(stable)
        row=dict(transcript=tx,gene_id_gencode50=a["gene_id"],
                 transcript_biotype_gencode50=a["transcript_biotype_gencode50"],
                 transcript_name_gencode50=a["transcript_name"],length_gencode50=a["transcript_length"],
                 ensembl_snapshot_release=116,ensembl_id="",ensembl_version="",ensembl_gene_id="",
                 ensembl_biotype="",ensembl_display_name="",ensembl_length="",
                 version_matches="",gene_stable_id_matches="",biotype_matches="",length_matches="",
                 comparison_status="not_in_pinned_release116_snapshot")
        if b:
            require(b["id"]==stable,"Ensembl lookup key/returned ID disagreement")
            v=str(b["version"])==version
            row.update(ensembl_id=b["id"],ensembl_version=b["version"],ensembl_gene_id=b["Parent"],
                       ensembl_biotype=b["biotype"],ensembl_display_name=b.get("display_name",""),
                       ensembl_length=b.get("length",""),version_matches=v,
                       gene_stable_id_matches=a["gene_id"].split(".",1)[0]==b["Parent"],
                       biotype_matches=a["transcript_biotype_gencode50"]==b["biotype"],
                       length_matches=a["transcript_length"]==b.get("length"),
                       comparison_status="version_matching_comparison" if v else "version_mismatch")
        rows.append(row)
    return rows
def read_tsv(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f,delimiter="\t"))
def write_tsv(path,rows,fields):
    with path.open("x",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n")
        w.writeheader();w.writerows(rows)
def sha(path,deadline):
    h=hashlib.sha256();size=0
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            require(time.monotonic()<deadline,"Input verification deadline")
            h.update(b);size+=len(b)
    return dict(bytes=size,sha256=h.hexdigest())
def main():
    p=argparse.ArgumentParser()
    for name in ("result","fasta","witnesses","ensembl","release","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args();started=time.monotonic();deadline=started+1080
    require(shutil.disk_usage(a.out.parent).free>=10*1024**3+5*1024**2,"Need 10 GiB headroom plus small-output budget")
    receipts={k:sha(getattr(a,k),deadline) for k in ("result","fasta","witnesses","ensembl","release")}
    for k,expected in (("result",RESULT_SHA),("fasta",FASTA_SHA),("ensembl",ENSEMBL_SHA),("release",RELEASE_SHA)):
        require(receipts[k]["sha256"]==expected,k+": SHA256 mismatch")
    require(receipts["fasta"]["bytes"]==183554921,"FASTA byte length")
    raw=a.witnesses.read_bytes()
    require(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==WITNESS_BLOB,"Saved witness Git blob mismatch")
    result=json.loads(a.result.read_text());designs=[d for d in result["designs"] if d["union_hamming"]==0]
    require(len(designs)==19 and all(not d["control"] for d in designs),"Exact-positive scope")
    require(all(d["strata"]["archived_parent"]["min_hamming"]!=0 for d in designs),"Unexpected archive exact hit outside recovery scope")
    targets={d["design_id"]:d["target"] for d in designs};require(len(targets)==19,"Duplicate design ID")
    saved=read_tsv(a.witnesses);require(len(saved)==128,"Saved witness count")
    require(len({r["transcript"] for r in saved})==60,"Saved transcript scope")
    ensembl=json.loads(a.ensembl.read_text());require(len(ensembl)==60,"Pinned Ensembl snapshot scope")
    require(json.loads(a.release.read_text())=={"releases":[116]},"Release116 receipt")
    with gzip.open(a.fasta,"rt",encoding="ascii") as f:
        hits,annotations,corpus=recover(fasta_records(f),targets,deadline)
    for k,v in corpus.items():
        require(v==result["gencode_corpus"][k],"Full corpus coverage mismatch: "+k)
    new=reconcile(hits,saved,designs);require(len(hits)==134 and len(new)==6,"134 total / six additional occurrence check")
    missing=Counter(r["design_id"] for r in new)
    expected_missing={"TCF12_e5__NR4A3_e3:d9":2,**{"TFG_e2__NR4A3_e3:d"+str(n):1 for n in (6,7,8,9)}}
    require(dict(missing)==expected_missing,"Omitted occurrence allocation disagrees")
    comparison=compare_annotations(annotations,ensembl)
    require({r["transcript"].split(".",1)[0] for r in saved}==set(ensembl),"Saved-hit / Ensembl lookup coverage")
    hits.sort(key=key);new.sort(key=key)
    a.out.mkdir(exist_ok=False)
    write_tsv(a.out/"complete-exact-hits.tsv",hits,COLUMNS)
    write_tsv(a.out/"new-six-occurrences.tsv",new,COLUMNS)
    write_tsv(a.out/"annotation-comparison.tsv",comparison,list(comparison[0]))
    (a.out/"gencode50-hit-headers.json").write_text(json.dumps(annotations,indent=2)+"\n")
    perdesign=[]
    for d in designs:
        rs=[r for r in hits if r["design_id"]==d["design_id"]]
        perdesign.append(dict(design_id=d["design_id"],target=d["target"],occurrences=len(rs),
                              saved=sum(r["saved_previously"] for r in rs),new=sum(not r["saved_previously"] for r in rs),
                              unique_transcripts=len({r["transcript"] for r in rs}),
                              gene_ids=sorted({r["gene_id"] for r in rs}),
                              biotypes=dict(sorted(Counter(r["transcript_biotype_gencode50"] for r in rs).items()))))
    summary=dict(schema="aso-complete-exact-hit-recovery/1",status="passed",source_revision="dece8fd886f554641a6c32276b00731af0d05438",
                 coordinate_convention="Zero-based transcript-sense [start_0based,end_0based_exclusive); width16; no genomic-coordinate inference",
                 source_receipts=receipts,corpus=corpus,designs=19,occurrences=len(hits),saved_verified=len(saved),new_occurrences=len(new),
                 unique_transcripts=len(annotations),new_occurrence_unique_transcripts=len({r["transcript"] for r in new}),
                 newly_seen_transcripts=sorted(set(annotations)-{r["transcript"] for r in saved}),
                 frozen_occurrence_biotypes=dict(sorted(Counter(r["transcript_biotype_gencode50"] for r in hits).items())),
                 frozen_transcript_biotypes=dict(sorted(Counter(r["transcript_biotype_gencode50"] for r in annotations.values()).items())),
                 release116_comparison_status=dict(sorted(Counter(r["comparison_status"] for r in comparison).items())),
                 version_matching_biotype_disagreements=[r["transcript"] for r in comparison if r["version_matches"] is True and r["biotype_matches"] is False],
                 per_design=perdesign,seconds=time.monotonic()-started,
                 limits=["134 design-record-window occurrences are not 134 independent transcripts or specimens.",
                         "GENCODE50 transcript biotype comes from pinned FASTA header field8; this is not gene biotype.",
                         "Ensembl116 comparison uses only the pinned 60-ID snapshot; absent IDs remain unavailable, never inferred.",
                         "No extrema/rankings, tissue expression, cleavage, potency or safety inference."])
    (a.out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    manifest={f.name:sha(f,deadline) for f in a.out.iterdir() if f.is_file()}
    require(sum(v["bytes"] for v in manifest.values())<1024**2,"Unexpected output exceeds1MiB")
    (a.out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(dict(status="passed",occurrences=134,saved_verified=128,new_occurrences=6,unique_transcripts=len(annotations))))
if __name__=="__main__":
    main()

