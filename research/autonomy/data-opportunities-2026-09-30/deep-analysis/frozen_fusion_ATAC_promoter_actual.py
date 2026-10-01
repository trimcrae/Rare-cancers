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
for symbol in cached_missing:
 url='https://rest.ensembl.org/lookup/symbol/homo_sapiens/'+symbol+'?content-type=application/json'
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-frozen-public-analysis'}),timeout=90) as f:raw=f.read()
 d=json.loads(raw);assert d.get('assembly_name')=='GRCh38' and d.get('object_type')=='Gene';genes[symbol]={'chrom':d['seq_region_name'],'start':d['start'],'end':d['end'],'strand':d['strand']};updates.append({'symbol':symbol,'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'literal':d})
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
result={'schema':'frozen-NR4A3-fusion-author-DA-promoter-analysis/1','executed_utc':datetime.now(timezone.utc).isoformat(),'predeclared_extension':'Frozen19/core3/native16,fourNR4A3fusionarms, held10kb/15kb plusnarrow2kb/.5kb, all32BEDs descriptive','source_receipts':RECEIPTS,'member_receipts':members,'annotation_missing_in_cached_source':cached_missing,'official_target_annotation_updates':updates,'annotation_coordinate_convention':'Heldstart/endTSS convention, notfreshtranscriptTSS selection','background_genes':background,'original_background_excludes_focus8':True,'background_also_excludes_all_frozen_targets':True,'control_BED_presence':{'NR4A3':'NR4A3' in peaksets,'NR4A3-EWSR1':'NR4A3-EWSR1' in peaksets},'primary_descriptive_family':primary,'all_author_call_summaries':tests,'all_gene_promoter_reads':reads,'author_code_provenance':{'repository':'mfrenkel16/OncofusionPRODATAC','commit':'95aa416a1b662d6b4c62c820668eda443a922653','GGAA_analysis_R_blob':'f2acc326dcf5c135c33778bc71c54ba15a5b9991','marker_rule':'getMarkerFeatures groupedFusion/TSS&fragmentbias,FDR<=.01/log2FC>=1,no explicitEmptybackground','explicit_Empty_contrast_script_blob':'4438c7a95d01ad52eedbb9fdb993d77dfa63e5d5'},'limits':['HEK293Tauthor-marker-call overlaps, notEMCtissue/binding/regulation/efficacy.','ReleasedmarkerBEDs notexplicitfusionvsEmpty/WT contrast; historicalcodeexecutionmatchunresolved.','Raw80.1GBfragments/QC notrerun.','AbsentWT/reciprocalBED unavailable notzero.','DDRbackgroundnotmatchedaccessibility/correlation/annotation; hypergeom/BH descriptiveexchangeability only.','Promoterwindows cannotassign distantpeaks.','Overlappinggenesets notindependentbiology.','Missingtargets usepinnedofficialGRCh38lookup withprovenancesensitivity.']}
path=OUT/'frozen-NR4A3-fusion-promoter-actual.json';path.write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n');print('FROZEN_FUSION_ATAC_BEGIN');print(json.dumps(result,ensure_ascii=False,allow_nan=False));print('FROZEN_FUSION_ATAC_END')
