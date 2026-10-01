import hashlib,io,json,subprocess,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
from scipy.stats import hypergeom
BASE=Path(__file__).resolve().parents[4];OUT=BASE/'campaign-output/fusion-ATAC';OUT.mkdir(parents=True,exist_ok=True)
PINS={'emc-ret-cistrome-inputs.json':'f08428656f4defb55bcaba985ad591d150c760b7','nr4a3-fusion-targets.json':'7cb7d4d82107ab6f5a27e3901bae2c356d0bbe87','emc-ret-target-scan.json':'5e45ac871d0002079b121f419b22e1d3f8ebc4a2'};RECEIPTS=[]
def held(name):
 path='research/modalities/'+name;blob=subprocess.check_output(['git','rev-parse','HEAD:'+path],cwd=BASE,text=True).strip();assert blob==PINS[name],'Frozenblobmismatch '+path;raw=subprocess.check_output(['git','show','HEAD:'+path],cwd=BASE);RECEIPTS.append({'path':path,'git_blob':blob,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});return json.loads(raw)
defs=held('nr4a3-fusion-targets.json')['set_definitions'];SETS={'core_3':defs['A_fusion_dna_binding_targets']['genes'],'native_16':defs['B_native_nr4a3_dna_binding_targets']['genes'],'pooled_19':defs['A_plus_B_all_dna_binding']['genes']};assert sorted(SETS['core_3']+SETS['native_16'])==sorted(SETS['pooled_19']);assert [len(SETS[k]) for k in ['core_3','native_16','pooled_19']]==[3,16,19];ws=held('emc-ret-target-scan.json')['part_1_nbre_scan']['_window'];assert(ws['upstream_of_tss'],ws['downstream_of_tss'])==(10000,15000);genes=held('emc-ret-cistrome-inputs.json')['genes']['hg38'];TARGETS=set(SETS['pooled_19']);FOCUS8={'RET','ENO3','PPARG','SEMA3C','NR4A3','NR4A1','VEGFA','KDR'}
def valid(g):return g.get('chrom') and g.get('start') is not None and g.get('end') is not None
cached_missing=sorted(s for s in TARGETS if s not in genes or not valid(genes[s]));updates=[]
import gzip,re,time,urllib.error
annotation_attempts=[]
def annotation_fetch(url,payload=None,timeout=90):
 headers={"User-Agent":"Rare-cancers-public-source-audit","Accept":"application/json"}
 if payload is not None:headers["Content-Type"]="application/json"
 for attempt in range(2):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,data=payload,headers=headers),timeout=timeout) as f:raw=f.read();status=f.status
   annotation_attempts.append({"url":url,"attempt":attempt+1,"status":status,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()});return raw
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
   annotation_attempts.append({"url":url,"attempt":attempt+1,"error":str(exc),"status":getattr(exc,"code",None)})
   if attempt==0:time.sleep(2)
 return None
if cached_missing:
 bulk_url="https://rest.ensembl.org/lookup/symbol/homo_sapiens";bulk_raw=annotation_fetch(bulk_url,json.dumps({"symbols":cached_missing}).encode(),30)
 if bulk_raw is not None:
  (OUT/"official-Ensembl-missing-targets.json").write_bytes(bulk_raw)
  try:bulk=json.loads(bulk_raw)
  except json.JSONDecodeError:bulk={}
  for symbol in cached_missing:
   d=bulk.get(symbol) if isinstance(bulk,dict) else None
   if not isinstance(d,dict) or d.get("assembly_name")!="GRCh38" or d.get("object_type")!="Gene":continue
   genes[symbol]={"chrom":d["seq_region_name"],"start":d["start"],"end":d["end"],"strand":d["strand"]};updates.append({"symbol":symbol,"url":bulk_url,"sha256":hashlib.sha256(bulk_raw).hexdigest(),"literal":d,"annotation_source":"official-Ensembl-GRCh38-bulk-lookup"})
 unresolved=sorted(s for s in cached_missing if s not in genes or not valid(genes[s]))
 if unresolved:
  gtf_raw=None
  for gtf_url in ["https://ftp.ensembl.org/pub/release-113/gtf/homo_sapiens/Homo_sapiens.GRCh38.113.gtf.gz","https://ftp.ebi.ac.uk/ensemblorg/pub/release-113/gtf/homo_sapiens/Homo_sapiens.GRCh38.113.gtf.gz"]:
   gtf_raw=annotation_fetch(gtf_url)
   if gtf_raw is not None and gtf_raw[:2]==b"\x1f\x8b":break
   gtf_raw=None
  if gtf_raw is None:raise RuntimeError("Bounded official GRCh38 annotation fallback failed")
  (OUT/"Homo_sapiens.GRCh38.113.gtf.gz").write_bytes(gtf_raw);gtf_sha=hashlib.sha256(gtf_raw).hexdigest();RECEIPTS.append({"url":gtf_url,"bytes":len(gtf_raw),"sha256":gtf_sha,"source_role":"official-Ensembl-release113-GRCh38-gene-features"})
  by_name={};by_id={};header=[];primary_chroms={str(i) for i in range(1,23)}|{"X","Y","MT"}
  for line in io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(gtf_raw)),encoding="utf-8"):
   line=line.rstrip("\n")
   if line.startswith("#"):
    if len(header)<30:header.append(line)
    continue
   cols=line.split("\t")
   if len(cols)!=9 or cols[2]!="gene" or cols[0] not in primary_chroms:continue
   attrs=dict(re.findall(r'(\w+) "([^"]*)"',cols[8]));stable_id=attrs.get("gene_id","").split(".")[0]
   if not stable_id:continue
   record={"chrom":cols[0],"start":int(cols[3]),"end":int(cols[4]),"strand":1 if cols[6]=="+" else -1,"gene_id":stable_id,"gene_name":attrs.get("gene_name"),"literal_gtf_line":line};by_id.setdefault(stable_id,[]).append(record);by_name.setdefault(attrs.get("gene_name"),[]).append(record)
  if not any(re.match(r"#!genome-build\s+GRCh38(?:\.p\d+)?(?:\s|$)",x) for x in header):raise ValueError("GTF header did not verify GRCh38 build")
  hgnc=None;hgnc_sha=None
  for symbol in unresolved:
   candidates=by_name.get(symbol,[]);alias_row=None
   if len(candidates)!=1:
    if hgnc is None:
     hgnc_url="https://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt";hgnc_raw=annotation_fetch(hgnc_url)
     if hgnc_raw is None:raise RuntimeError("Official HGNC alias qualification unavailable")
     (OUT/"hgnc_complete_set.txt").write_bytes(hgnc_raw);hgnc_sha=hashlib.sha256(hgnc_raw).hexdigest();RECEIPTS.append({"url":hgnc_url,"bytes":len(hgnc_raw),"sha256":hgnc_sha,"source_role":"official-HGNC-symbol-alias-identity-only"})
     import csv
     hgnc=list(csv.DictReader(io.StringIO(hgnc_raw.decode()),delimiter="\t"))
    exact=[r for r in hgnc if r.get("symbol")==symbol and r.get("status")=="Approved"];alias=[r for r in hgnc if r.get("status")=="Approved" and symbol in set((r.get("alias_symbol","")+"|"+r.get("prev_symbol","")).split("|"))];matched=exact if exact else alias
    if len(matched)!=1:raise ValueError("Frozen symbol lacks unique approved HGNC identity: "+symbol)
    alias_row=matched[0];ens_ids=[x for x in alias_row.get("ensembl_gene_id","").split("|") if x];candidates=[r for ident in ens_ids for r in by_id.get(ident,[])]
   if len(candidates)!=1:raise ValueError("Frozen target lacks unique primary-GRCh38 gene feature: "+symbol)
   d=candidates[0];genes[symbol]={k:d[k] for k in ("chrom","start","end","strand")};updates.append({"symbol":symbol,"url":gtf_url,"sha256":gtf_sha,"annotation_source":"official-Ensembl-release113-GRCh38-gene-feature","coordinate_convention":"one-based closed gene start/end; held TSS convention retained","literal":d,"gtf_header":header,"HGNC_identity_row":alias_row,"HGNC_sha256":hgnc_sha if alias_row is not None else None})
 RECEIPTS.append({"source_role":"bounded-annotation-access-attempts","attempts":annotation_attempts})
background=sorted(s for s,g in genes.items() if s not in FOCUS8 and s not in TARGETS and valid(g));assert not any(s not in genes or not valid(genes[s]) for s in TARGETS);WINDOWS=[('held_10kb_up_15kb_down',10000,15000),('narrow_2kb_up_0.5kb_down',2000,500)];ARMS=['EWSR1-NR4A3','TAF15-NR4A3','TCF12-NR4A3','TFG-NR4A3']
url='https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-024-02347-4/MediaObjects/41587_2024_2347_MOESM3_ESM.zip'
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-frozen-public-analysis'}),timeout=120) as f:raw=f.read()
assert raw.startswith(b'PK\x03\x04') and len(raw)==788065,'FrozenBEDinventorysourcechanged';(OUT/'Frenkel-MOESM3.zip').write_bytes(raw);RECEIPTS.append({'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});peaksets={};members=[]
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 for info in z.infolist():
  if not info.filename.startswith('Supp_Data_1_new/') or not info.filename.endswith('_markers.bed'):continue
  body=z.read(info);arm=Path(info.filename).name.removesuffix('_markers.bed');rows=[]
  for line in body.decode().splitlines():
   if not line.strip():continue
   a,b,c=line.split('\t')[:3];start,end=int(b),int(c);assert start>=0 and end>start;rows.append((a if a.startswith('chr') else 'chr'+a,start,end))
  rows=sorted(set(rows));by={}
  for chrom,start,end in rows:by.setdefault(chrom,[]).append((start,end))
  peaksets[arm]={'by':by,'n':len(rows),'literal_rows':len(body.decode().splitlines())};members.append({'member':info.filename,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'unique_intervals':len(rows)})
assert len(peaksets)==32 and all(a in peaksets for a in ARMS),'FrozenBEDinventorychanged'
def window(symbol,up,down):
 g=genes[symbol];strand=int(g.get('strand',1));tss=int(g['start']) if strand>=0 else int(g['end']);start,end=(tss-up,tss+down) if strand>=0 else(tss-down,tss+up);c=str(g['chrom']);return c if c.startswith('chr') else'chr'+c,max(0,start),end
def overlaps(arm,w):
 c,a,b=w;return[(s,e) for s,e in peaksets[arm]['by'].get(c,[]) if s<b and e>a]
reads=[];tests=[]
for label,up,down in WINDOWS:
 for arm in sorted(peaksets):
  calls={s:overlaps(arm,window(s,up,down)) for s in sorted(TARGETS|set(background))}
  for symbol,ivs in calls.items():reads.append({'window':label,'arm':arm,'symbol':symbol,'in_frozen_targets':symbol in TARGETS,'query':window(symbol,up,down),'author_DA_promoter_hit':bool(ivs),'unique_intervals':len(ivs),'intervals':ivs})
  bg_hits=sum(bool(calls[s]) for s in background)
  for key,gs in SETS.items():
   hits=[s for s in gs if calls[s]];n=len(gs);k=len(hits);p=float(hypergeom.sf(k-1,len(background)+n,bg_hits+k,n));tests.append({'window':label,'arm':arm,'set':key,'members':gs,'n':n,'hit_genes':hits,'hit_n':k,'background_n':len(background),'background_hit_n':bg_hits,'background_fraction':bg_hits/len(background),'source_panel_2percent_floor':bg_hits/len(background)>=.02,'nominal_exchangeable_gene_label_upper_p':p,'primary_family':label==WINDOWS[0][0] and arm in ARMS})
primary=[x for x in tests if x['primary_family']];assert len(primary)==12;order=sorted(range(12),key=lambda i:primary[i]['nominal_exchangeable_gene_label_upper_p']);prev=1.
for rank,i in reversed(list(enumerate(order,1))):prev=min(prev,primary[i]['nominal_exchangeable_gene_label_upper_p']*12/rank);primary[i]['descriptive_BH12']=prev
result={'schema':'frozen-NR4A3-fusion-author-DA-promoter-analysis/1','executed_utc':datetime.now(timezone.utc).isoformat(),'predeclared_extension':'Frozen19/core3/native16,fourNR4A3fusionarms, held10kb/15kb plusnarrow2kb/.5kb, all32BEDs descriptive','source_receipts':RECEIPTS,'member_receipts':members,'annotation_missing_in_cached_source':cached_missing,'official_target_annotation_updates':updates,'annotation_coordinate_convention':'Heldstart/endTSS convention, notfreshtranscriptTSS selection','background_genes':background,'original_background_excludes_focus8':True,'background_also_excludes_all_frozen_targets':True,'control_BED_presence':{'NR4A3':'NR4A3' in peaksets,'NR4A3-EWSR1':'NR4A3-EWSR1' in peaksets},'primary_descriptive_family':primary,'all_author_call_summaries':tests,'all_gene_promoter_reads':reads,'author_code_provenance':{'repository':'mfrenkel16/OncofusionPRODATAC','commit':'95aa416a1b662d6b4c62c820668eda443a922653','GGAA_analysis_R_blob':'f2acc326dcf5c135c33778bc71c54ba15a5b9991','marker_rule':'getMarkerFeatures groupedFusion/TSS&fragmentbias,FDR<=.01/log2FC>=1,no explicitEmptybackground','explicit_Empty_contrast_script_blob':'4438c7a95d01ad52eedbb9fdb993d77dfa63e5d5'},'limits':['HEK293Tauthor-marker-call overlaps, notEMCtissue/binding/regulation/efficacy.','ReleasedmarkerBEDs notexplicitfusionvsEmpty/WT contrast; historicalcodeexecutionmatchunresolved.','Raw80.1GBfragments/QC notrerun.','AbsentWT/reciprocalBED unavailable notzero.','DDRbackgroundnotmatchedaccessibility/correlation/annotation; hypergeom/BH descriptiveexchangeability only.','Promoterwindows cannotassign distantpeaks.','Overlappinggenesets notindependentbiology.','Missing targets use official GRCh38 bulk lookup or pinned Ensembl113 gene-feature fallback with unique HGNC identity where required withprovenancesensitivity.']}
path=OUT/'frozen-NR4A3-fusion-promoter-actual.json';path.write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n');print('FROZEN_FUSION_ATAC_BEGIN');print(json.dumps(result,ensure_ascii=False,allow_nan=False));print('FROZEN_FUSION_ATAC_END')
