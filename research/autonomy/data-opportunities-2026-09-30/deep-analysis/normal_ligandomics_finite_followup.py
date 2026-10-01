#!/usr/bin/env python3
import csv,gzip,hashlib,io,json,math,re,runpy,urllib.request,urllib.parse
from collections import Counter,defaultdict
from pathlib import Path
BASE=Path(__file__).with_name("normal_ligandomics.py")
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=="19f70cd8fb6e8216a35d182e3196c26cd0f4903974c35983bf79a68877f30424"
C=runpy.run_path(str(BASE));flags_sw=defaultdict(set)
for r in C["readers"]["aggregated"]():
 for item in r["donor_alleles"].split(","):
  if item.startswith(("s/","w/")):flags_sw[C["norm"](item[2:])].add(r["peptide_sequence_id"])
def calc(a,c,mode,autopsy=False):
 ds=[d for d in C["decode"](C["carriers"].get(a,0)) if d in C["class_donors"].get(c,set()) and (not autopsy or d.startswith("AUT01-"))];bits=sum(1<<C["di"][d] for d in ds);n=len(ds)
 selected=None if mode=="all" else C["flags"].get(a,set()) if mode=="s" else flags_sw.get(a,set())
 masks=[v&bits for k,v in C["presence"].get(c,{}).items() if v&bits and (selected is None or k in selected)];hist=Counter(x.bit_count() for x in masks);hold=[]
 for d in ds:
  b=1<<C["di"][d];test=sum(bool(x&b) for x in masks);lost=sum(x==b for x in masks)
  hold.append({"donor":d,"test_peptides":test,"not_detected_in_other_carriers":lost,"fraction":lost/test if test else None})
 incidence=sum(x["test_peptides"] for x in hold);single=hist.get(1,0)
 assert incidence==sum(k*v for k,v in hist.items()) and single==sum(x["not_detected_in_other_carriers"] for x in hold)
 curve=[]
 for m in range(1,n+1):
  missing=sum(v*(math.comb(n-k,m)/math.comb(n,m) if n-k>=m else 0) for k,v in hist.items());curve.append({"training_donors":m,"fraction_of_full_union_not_detected":missing/len(masks) if masks else None})
 if masks:assert curve[-1]["fraction_of_full_union_not_detected"]==0
 return {"allele":a,"hla_class":c,"flag_mode":mode,"autopsy_only":autopsy,"donors":ds,"n_donors":n,"peptide_union":len(masks),"singleton_peptides":single,"singleton_fraction":single/len(masks) if masks else None,"donor_breadth_histogram":dict(sorted(hist.items())),"heldout_donor_peptide_incidences":incidence,"pooled_heldout_nonrecovery":single/incidence if incidence else None,"per_donor_holdout":hold,"exact_rarefaction":curve}
rows=[calc(a,c,m) for a,c in C["TARGETS"] for m in ["s","sw","all"]]+[calc("B*15:01","HLA-I",m,True) for m in ["s","sw","all"]]
for a,c in C["TARGETS"]:
 old=next(t["calibration"] for t in C["result"]["targets"] if t["allele"]==a);new=next(x for x in rows if x["allele"]==a and x["flag_mode"]=="s" and not x["autopsy_only"])
 assert old["n_eligible_donors"]==new["n_donors"] and old["n_strong_flagged_peptides_in_carrier_union"]==new["peptide_union"] and old["pooled_heldout_nonrecovery_fraction"]==new["pooled_heldout_nonrecovery"]
R={"schema":"benign-hla-nonrecovery-sensitivity/1","timing":"exploratory after initial result","base_script_sha256":hashlib.sha256(BASE.read_bytes()).hexdigest(),"source_receipts":C["result"]["sources"],"checks":"strong reconstruction exact; incidence/singletonsconsistent; full-unionrarefactionzero","analyses":rows,"interpretation":"Observed reference nonrecovery, not sensitivity/absence/safety; one-donor holdout tautological","primary_totals":{"class_units":{c:sum(1 for d,t,cc in C["units"] if cc==c) for c in C["presence"]},"unique_donor_tissue_units":len({(d,t) for d,t,c in C["units"]}),"class_peptide_unions":{c:len(v) for c,v in C["presence"].items()}}}
(C["OUT"]/"sensitivity.json").write_text(json.dumps(R,indent=2)+"\n");print("LIGANDOMICS_SENSITIVITY_BEGIN");print(json.dumps(R,separators=(",",":")));print("LIGANDOMICS_SENSITIVITY_END")
E={"schema":"frozen-IEDB-and-parent-ligand-audit/1","queries":C["QUERIES"],"iedb":[],"protein_map":{},"sources":[],"errors":[]}
def get(url,cap=4*1024*1024):
 req=urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-public-data-analysis/1","Accept":"application/json","Prefer":"count=exact"})
 with urllib.request.urlopen(req,timeout=40) as r:b=r.read(cap+1);status=r.status;final=r.url;cr=r.headers.get("Content-Range")
 if len(b)>cap:raise RuntimeError("byte cap")
 E["sources"].append({"url":url,"final_url":final,"http_status":status,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"content_range":cr});return b,cr
for seq in C["QUERIES"]:
 ep=[]
 for endpoint in ["epitope_search","tcell_search","mhc_search"]:
  url="https://query-api.iedb.org/"+endpoint+"?"+urllib.parse.urlencode({"linear_sequence":"eq."+seq,"limit":100})
  try:
   b,cr=get(url);j=json.loads(b)
   if not isinstance(j,list):raise ValueError("expected list")
   E["iedb"].append({"sequence":seq,"endpoint":endpoint,"status":"retrieved","rows":j,"returned_rows":len(j),"content_range":cr,"limit":100})
   if endpoint=="epitope_search":ep=j
  except Exception as ex:E["iedb"].append({"sequence":seq,"endpoint":endpoint,"status":"failed","error":str(ex)})
 for row in ep:
  if not row.get("structure_id"):continue
  sid=str(row["structure_id"]);url="https://query-api.iedb.org/epitope_to_mhc?"+urllib.parse.urlencode({"structure_id":"eq."+sid,"limit":100})
  try:
   b,cr=get(url);j=json.loads(b)
   if not isinstance(j,list):raise ValueError("expected list")
   E["iedb"].append({"sequence":seq,"endpoint":"epitope_to_mhc","structure_id":sid,"status":"retrieved","rows":j,"returned_rows":len(j),"content_range":cr,"limit":100})
  except Exception as ex:E["iedb"].append({"sequence":seq,"endpoint":"epitope_to_mhc","structure_id":sid,"status":"failed","error":str(ex)})
url="https://hla-ligand-atlas.org/rel/2020.12/protein_map.tsv.gz"
try:
 b,cr=get(url,64*1024*1024);(C["OUT"]/"protein_map.tsv.gz").write_bytes(b)
 if b[:2]==b"\x1f\x8b":b=gzip.decompress(b)
 reader=csv.DictReader(io.StringIO(b.decode("utf-8-sig")),delimiter="\t");head=reader.fieldnames
 assert "peptide_sequence_id" in head,"Unexpected peptide column "+str(head)
 other=[x for x in head if x!="peptide_sequence_id"];assert len(other)==1,"Unexpected headers "+str(head)
 maps=defaultdict(set);n=0
 for row in reader:
  n+=1;accs=re.findall(r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-\d+)?",row[other[0]]);maps[row["peptide_sequence_id"]].update(accs)
 assert any(maps.values())
 targets={"Q92570":"NR4A3","P22736":"NR4A1","P43354":"NR4A2","Q01844":"EWSR1"};selected={k for k,v in maps.items() if any(a.split("-")[0] in targets for a in v)};obs=defaultdict(set)
 for row in C["readers"]["sample_hits"]():
  k=row["peptide_sequence_id"]
  if k in selected:obs[k].add((row["donor"],row["tissue"],row["hla_class"]))
 records=[]
 for acc,gene in targets.items():
  ids=sorted(k for k,v in maps.items() if any(a.split("-")[0]==acc for a in v));peps=[]
  for k in ids:peps.append({"peptide_sequence_id":k,"sequence":C["peptides"].get(k),"all_annotated_protein_accessions":sorted(maps[k]),"annotation_unique_to_gene_accession":len({a.split("-")[0] for a in maps[k]})==1,"positive_donor_tissue_class_units":[list(x) for x in sorted(obs[k])]})
  records.append({"gene":gene,"accession":acc,"annotated_peptide_ids":len(ids),"peptides":peps})
 E["protein_map"]={"status":"retrieved","headers":head,"rows":n,"targets":records,"interpretation":"Observed identifiers annotated to proteins; shared mapping not protein-of-origin/restricting-HLA proof"}
except Exception as ex:E["protein_map"]={"status":"failed","error":str(ex),"url":url}
E["limits"]=["Empty exact IEDB query scoped negative, not assaynegative","HTTP/schema failure unresolved, not nodata","Normal lookup not EMCpresentation/Tcell/safety","Exact original FASTA isoform inclusion unverified"]
(C["OUT"]/"empirical-assay-joins.json").write_text(json.dumps(E,indent=2)+"\n");print("LIGANDOMICS_ASSAY_JOINS_BEGIN");print(json.dumps(E,separators=(",",":")));print("LIGANDOMICS_ASSAY_JOINS_END")
