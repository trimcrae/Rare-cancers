"""Compact source dispositions and freezing, preserving original API/full extracts ignored."""
from pathlib import Path
import datetime,hashlib,json,shutil
ROOT=Path(__file__).resolve().parent
BASE=Path('/workspace/Rare-cancers')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj):ROOT.joinpath(name).write_text(json.dumps(obj,indent=2)+'\n')
def main():
 queries=['SOURCE-QUERIES.json','SOURCE-QUERIES-REFINED.json','SOURCE-QUERIES-EXACT.json','SOURCE-SECRETORY-COMPLETE.json','PRIOR-ART-QUERIES.json']
 records={};prior=[]
 for n in queries:
  f=ROOT/n;original=ROOT/'raw-cache'/('original-'+n);a=json.loads((original if original.exists() else f).read_text());qs=a if isinstance(a,list) else [a]
  # Focus abstract statements before removing entire indexed abstract payloads.
  for q in qs:
   for r in q.get('results',[]):
    if r.get('pmid') in ['41315062','29327709','38447752','15920699','12598313','10895826','11737310','11679947','10728817']:
     records[r['pmid']]=r
  backup=ROOT/'raw-cache'/('original-'+n)
  if not backup.exists():shutil.copy2(f,backup)
  for q in qs:
   for r in q.get('results',[]):r.pop('abstractText',None)
  write(n,a)
 for k,r in sorted(records.items()):
  prior.append({'pmid':k,'doi':r.get('doi'),'title':r.get('title'),'indexed_abstract_statement':r.get('abstractText'),'status':'evaluated indexed abstract; full assay/sample records not inferred','relevance':'Known EMC/neural/diagnostic prior art; not a novel imaging/transport finding' if k!='41315062' else 'One unusual author-labelled EMC, HSPA8::NR4A2/no canonical NR4A3 fusion; SSTR2 keyword does not identify assay/result. Body gated.'})
 write('PRIOR-ART-OBSERVATIONS.json',prior)
 f=ROOT/'FOCUSED-SOURCE-EXTRACTS.json';backup=ROOT/'raw-cache/original-FOCUSED-SOURCE-EXTRACTS.json';a=json.loads((backup if backup.exists() else f).read_text())
 if not backup.exists():shutil.copy2(f,backup)
 observations=[]
 for r in a:
  extracts=r.pop('focused_extracts',[])
  if r['id']=='Barresi2025':r.update(evidence_status='unavailable detailed measurement; evaluated public preview',access_classification='Publisher explicitly states subscription preview/no-access; no body methods/results. No bypass attempted.')
  elif r['id']=='PMC1868116':r['evidence_status']='unavailable primary fulltext via API; alternate official-host response is reCAPTCHA challenge; indexed abstract evaluated'
  else:r['evidence_status']='evaluated relevant public primary text or secondary source; no eligible EMC transporter/uptake observation in pertinent excerpt'
  r['matching_paragraph_count']=len(extracts)
  for x in extracts:
   t=x['text'];low=t.lower()
   if r['id']=='PMC1402209' and 'vesicular monoamine transporter 2' in low:
    observations.append({'source':r['id'],'source_sha256':r.get('sha256'),'observation':'Nurr1 induction of VMAT2/dopamine transporter cited in neuronal models; not measured EMC transporter phenotype.','excerpt':t[:1700],'disease_disposition':'nonEMC neuronal model context, not transferable'})
   elif r['id']=='PMC7102354' and ('vesicular monoamine transporter 2' in low or 'results:' in low and 'myxoid chondrosarcoma' in low):
    observations.append({'source':r['id'],'source_sha256':r.get('sha256'),'excerpt':t[:1900],'observation':'Separate abstract sections: EMC morphology/IHC versus postmortem midbrain VMAT2. They are not one disease observation; no linkage by shared conference PDF.','disease_disposition':'EMC abstract lacks transporter measurement; VMAT2 abstract nonEMC'})
   elif r['id']=='PMC5929452' and 'myxoid chondrosarcoma' in low:
    observations.append({'source':r['id'],'source_sha256':r.get('sha256'),'excerpt':t[:2400],'observation':'Review distinguishes Tateishi EMC MR/cytogenetic pattern from neuroblastoma SLC6A2/FDOPA result; latter is not EMC.','disease_disposition':'No EMC catecholamine transporter/uptake inference'})
 write('FOCUSED-SOURCE-EXTRACTS.json',a);write('LITERATURE-DISPOSITIONS.json',observations)
 reuse=[]
 paths=['research/modalities/aso-delivery-antigen.json','research/autonomy/atlas-hofvander-validation-2026-09-06/results/SSTR2.json','research/autonomy/atlas-hofvander-validation-2026-09-06/replication-results/SSTR2.json','research/autonomy/fresh-discovery-2026-10-04-round2/clinical/oliveira2000-full-paragraphs.json','research/autonomy/fresh-discovery-2026-10-04-round6/diagnostic/OBSERVATIONS.json','research/modalities/geo-gse28866-brunner-series.json']
 for rel in paths:
  p=BASE/rel;reuse.append({'path':rel,'sha256':sha(p),'status':'verified prior source evaluation reused; no unchanged retrieval','purpose':'Prior-art/identity/SSTR2 assay limits, not new measurements'})
 write('VERIFIED-REUSE.json',reuse)
 cover=[
 {'source':'Hofvander2026','status':'evaluated','conditions':13,'disposition':'All13 author-labelled EMC RNA rows; nine primary rows after3known historical discovery overlaps and1LR excluded from primary subset. All13 retained individually. Unknown additional donor overlap remains. Canonical fusion status not authenticated per row by reused metadata.','record':'RNA-RESULTS.json'},
 {'source':'GSE24369/GPL6244','status':'evaluated','conditions':6,'disposition':'All6 EMC biopsies, exact single-gene probes on all9 frozen genes, original RMA signals; all17LGFMS comparator rows. Unknown cross-study overlap, no independent-donor assertion.','record':'ARRAY-RESULTS.json'},
 {'source':'GSE4303/GPL3290','status':'evaluated','conditions':10,'disposition':'All10 verified author-EMC source conditions retained;9SLC6A2 values,1missing;10SLC18A2 values;SLC18A1 probe not mapped, unsuitable for gene read. Six heterogeneous comparator conditions descriptive only. Exact-symbol mapping reused, not new annotation.','record':'ARRAY-RESULTS.json'},
 {'source':'GSE28866/3SEQ','status':'evaluated','conditions':4,'disposition':'All4 verified EMC libraries, one exact SLC18A2 symbol peak. SLC6A2/SLC18A1 absent from exact-symbol peak table, demonstrably unsuitable measurement for these two genes; not biological absence. All6MLPS/3SS/27normal context libraries retained.','record':'3SEQ-RESULTS.json'},
 {'source':'Barresi2025 DOI10.1007/s00428-025-04352-7','status':'unavailable evidence','conditions':1,'disposition':'Public primary abstract/preview evaluated: author-EMC HSPA8::NR4A2 neuroendocrine phenotype, noncanonical NR4A3-negative. SSTR2 keyword/references are not assay results. Full detailed measurement and raw transcriptome request-only; no access/outreach authorized. Cannot count as canonical EMC receptor-positive evidence.','record':'FOCUSED-SOURCE-EXTRACTS.json'},
 {'source':'SSTR2 previous cohorts','status':'verified evaluation reused','disposition':'SSTR2 heterogeneous/flat, older-array discordance and limited normal context; unchanged prior outcomes not discovery.','record':'VERIFIED-REUSE.json'},
 {'source':'Oliveira2000 and older neural-marker studies; INSM1/CHRNA6','status':'verified evaluation reused','disposition':'Published neural/neuroendocrine differentiation and diagnostic markers are prior art, do not authenticate catecholamine uptake machinery. Individual specimen overlap with later cohorts not fully resolved.','record':'PRIOR-ART-OBSERVATIONS.json'},
 {'source':'Sjögren2003 PMID12598313/PMC1868116','status':'unavailable evidence','conditions':2,'disposition':'Indexed abstract documents two different-fusion EMC microarray observations compared with MLPS; already-published neural program. Full primary source API500 then official-host reCAPTCHA; no transporter-specific available measurement or full assay mapping authenticated, no negative gene inference.','record':'PMC1868116-ALTERNATE-RECEIPT.json'},
 {'source':'Exact vesicular query four results','status':'evaluated','disposition':'NR4A review refers to neuronalVMAT2; conference contains separate EMC and postmortem brainVMAT2 abstracts; radiogenomics review has neuroblastomaSLC6A2/FDOPA versus EMC MR. Conference PMC7102355 returns only brief index, detailed abstract unavailable; not evidence of an EMC observation.','record':'LITERATURE-DISPOSITIONS.json'},
 {'source':'Broad NR4A3/VMAT/catecholamine search','status':'pending accessible analysis','disposition':'Broad initial query is truncated and manyhits are other cancers/VMAT radiation modality; retained as exploratory discovery search only. No claim every indexed source evaluated/no suitable remaining public source. Exact disease/vesicular/clinical focused queries complete; secretory106 records metadata/abstract gate, not full-text assay audit.','record':'SOURCE-QUERIES.json'},
 {'source':'Broader known identity-pending RNA/model resources fromR6/R7','status':'pending accessible analysis','disposition':'Generic BO112 donor identities, disputedHEMCSS/MUG-EMCS and broader raw/panel crosswalks not silently accepted as EMC; no new identity or ligand-uptake measurements established here. Identity-pending cannot be pooled.','record':'/handoff/CONTINUE-IN-CLOUD.txt'}]
 write('COVERAGE.json',{'scope':'Bounded catecholamine uptake/storage contrast, not global evidence exhaustion','sources':cover,'promotion_blockers':['Unresolved relevant source identities/body/assay mappings and pending broader source gate; no full public-EMC coverage certificate.','Protein/tumour-cell localization and clinical uptake not measured.'],'donor_rule':'Conditions are not summed as independent donors; known overlap excluded from primary subset only, all conditions retained.'})
 write('DECISION.json',{'decision':'shelve standalone neurosecretory imaging/theranostic finding','reason':'Uptake/storage premise unsupported by measured RNA: NET/SLC6A2 is atmost0.07TPM and VMAT1/SLC18A1 zero in13Hofvander; these estimates do not establish functional absence. VariableVMAT2/SLC18A2 RNA is present but GSE24369 vsLGFMS is nearly neutral(A0.520), and4GSE28866 values overlapMLPS/normalcontext. No consistent transporter combination or independent protein/uptake linkage adds useful clinical inference.','validity':'Descriptive rows/probe readings/source hashes valid at stated resolution; unknown overlap, cell admixture, processed zeros, missing probes and source/body limits prevent stronger conclusions.','novelty_value':'Known neural differentiation and SSTR2 hypotheses are priorart. Isolated/heterogeneous storage-transporter RNA without uptake-protein/clinical link and stable appropriate comparator replication is insufficient scientific value; failed hypothesis is not automatically a negative publication.','strongest_alternative':'Established neural differentiation, nerve/stromal admixture and source/year effects explain variable VMAT2 at least as well as tumour catecholamine uptake/storage phenotype.','negative_inconclusive':'No demonstrated new useful finding; lowRNA not negativeMIBG scan, no treatment-benefit/no-uptake claim. SSTR2 details in unusual NR4A2 case unavailable, not negative.','reopen_when':'New authenticated EMC tumor-cell transporter/receptor protein or case-linked catecholamine/SSTR uptake measurements with dates/acquisition/treatment/donor mapping, or decisive genuinely new transcript/functional contrast that addresses replication/comparator/admixture and full relevant-source coverage; fresh prospective rationale/independent value review required.','global_search_exhausted':False,'TMEM266':'shelved','manuscript':'none'})
 print('compact packet',len(list(ROOT.glob('*'))),'cachebytes',sum(f.stat().st_size for f in (ROOT/'raw-cache').rglob('*') if f.is_file()))
if __name__=='__main__':main()
