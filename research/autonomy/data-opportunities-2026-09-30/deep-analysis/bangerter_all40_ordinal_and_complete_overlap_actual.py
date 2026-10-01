import hashlib,json,re
from collections import Counter
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import requests
from PIL import Image
O=Path('campaign-output/bangerter-all40-ordinal');O.mkdir(parents=True,exist_ok=True)
P=Path('campaign-output/bangerter-drug-screen/13577_2022_818_Fig5_HTML.jpg')
SOURCE_SHA='3d22b276d0b845d7d11ca8ef967caefedc3c4798a3d41e2b0ea129912106eb36';B=P.read_bytes()
if hashlib.sha256(B).hexdigest()!=SOURCE_SHA:raise ValueError('Figure5 identity mismatch')
a=np.asarray(Image.open(P).convert('RGB'))
if a.shape[:2]!=(544,677):raise ValueError('Fixed coordinates require actual677x544 source')
def patch(x,y):return np.median(a[y-3:y+4,x-3:x+4].reshape(-1,3),axis=0)
classes=['high','good','moderate','low','none'];legend_y=[474,490,506,521,536];pal=np.asarray([patch(446,y) for y in legend_y])
expected=np.asarray([[0,176,80],[146,208,80],[255,255,0],[255,192,0],[255,0,0]])
if np.any(np.linalg.norm(pal-expected,axis=1)>50):raise ValueError('Legend pixel anchors require review: '+repr(pal.tolist()))
chem=[('Carfilzomib',58),('Doxorubicin HCL',91),('Etoposide',131),('SN-38',172),('Docetaxel',205),('Gemcitabine HCl',236),('Mitomycin C',270),('Fluorouracil',302),('Topotecan HCl',335),('Dacarbazine',351),('Oxaliplatin',375),('Pemetrexed Disodium Hydrate',409),('Bleomycin sulfate',440),('Vinblastine sulfate',465),('Fludarabine phosphate',482),('Paclitaxel',497),('Vinorelbine Tartrate',514)]
target=[('PU-H71',55),('HDM201',68),('Venetoclax',83),('Derazantinib',111),('Ceritinib',139),('AZD5153',152),('Encorafenib',166),('Dabrafenib',180),('Belinostat',193),('Crizotinib',208),('Abmaciclib',221),('Adavosertib',235),('Ipatasertib',249),('Trametinib',263),('Enasidenib',276),('Naraparib Tosylate',290),('Erlotinib HCl',303),('Sorafenib',317),('WE-822',331),('Tazemetostat',345),('Cabozantinib',365),('Ponatinib',400),('Selpercatinib',428)]
rows=[]
for panel,xx,rr in [('A',320,chem),('B',650,target)]:
 for k,(name,yy) in enumerate(rr,1):
  color=patch(xx,yy);ds=np.linalg.norm(pal-color,axis=1);order=np.argsort(ds);best=int(order[0])
  if float(ds[best])>35 or float(ds[order[1]]-ds[best])<35:raise ValueError('Ambiguous source color: '+name+' '+repr(ds.tolist()))
  rows.append({'source_model':'USZ20-EMC1','source_figure':'Fig5','source_panel':panel,'panel_row':k,'literal_figure_drug':name,'source_CAS':None,'ordinal_source_category':classes[best],'pixel_anchor':[xx,yy],'median_source_RGB':color.tolist(),'distance_to_legend':float(ds[best]),'name_provenance':'Manual source-image label transcription; no spelling correction or chemical harmonization'})
U='https://raw.githubusercontent.com/trimcrae/Rare-cancers/af7211708205b5189d8c537c1ce2a23aa4bea076/research/literature/emc-census-2026-09-12/iwata-2025-screen-extraction.json'
q=requests.get(U,timeout=(15,90));q.raise_for_status();ib=q.content;ih=hashlib.sha256(ib).hexdigest()
if ih!='52cfb777f196fdd2440bc74382e7aa276515acc6a9ed79d0660a16ccaef50bb2':raise ValueError('Frozen Iwata input SHA mismatch: '+ih)
(O/'iwata-frozen-source.json').write_bytes(ib);iv=json.loads(ib);screen=iv['tables'][0]['records'];dose=iv['tables'][1]['records']
if len(screen)!=221 or len(dose)!=24:raise ValueError('Frozen source row counts changed')
def qualifier(s):return re.sub(r'\s+',' ',re.sub(r'\([^)]*\)','',s).lower()).strip()
forms=re.compile(r'\b(?:hcl|hydrochloride|dihydrochloride|mesylate|tosylate|malate|maleate|phosphate|disodium|hydrate|dmso solvate|sulfate|tartrate)\b',re.I)
def family(s):return re.sub(r'\s+',' ',forms.sub('',qualifier(s))).strip()
for row in rows:
 n=row['literal_figure_drug'];row['Iwata_exact_literal_screen_rows']=[r for r in screen if r['drug']==n];row['Iwata_exact_literal_IC50_rows']=[r for r in dose if r['drug']==n]
 row['Iwata_parenthetical_case_whitespace_candidates_screen']=[r for r in screen if qualifier(r['drug'])==qualifier(n)];row['Iwata_parenthetical_case_whitespace_candidates_IC50']=[r for r in dose if qualifier(r['drug'])==qualifier(n)]
 row['Iwata_formulation_family_candidates_screen']=[r for r in screen if family(r['drug'])==family(n)];row['Iwata_formulation_family_candidates_IC50']=[r for r in dose if family(r['drug'])==family(n)]
 row['exact_screen_join_status']='unique literal name' if len(row['Iwata_exact_literal_screen_rows'])==1 else ('ambiguous literal name' if len(row['Iwata_exact_literal_screen_rows'])>1 else 'no literal name match')
 row['qualified_screen_join_status']='no candidate' if not row['Iwata_parenthetical_case_whitespace_candidates_screen'] else ('one candidate, chemical identity unverified' if len(row['Iwata_parenthetical_case_whitespace_candidates_screen'])==1 else 'multiple candidates, unresolved');row['chemical_identity_verified']=False
counts={p:dict(Counter(r['ordinal_source_category'] for r in rows if r['source_panel']==p)) for p in ['A','B']}
R={'schema':'bangerter-all40-source-ordinal-and-complete-overlap-v1','executed_utc':datetime.now(timezone.utc).isoformat(),'source_figure_SHA256':SOURCE_SHA,'source_image_size':[677,544],'legend_RGB':dict(zip(classes,pal.tolist())),'literal_legend_ranges':{'high':'<10% cell viability','good':'11–20% cell viability','moderate':'21–40% cell viability','low':'41–70% cell viability','none':'>71% cell viability'},'rows':rows,'panel_counts':counts,'total_counts':dict(Counter(r['ordinal_source_category'] for r in rows)),'screen_context':{'model':'USZ20-EMC1','independent_patient_models_screened':1,'rows':40,'author_panel_groups':{'A':'17 chemotherapies','B':'23 targeted agents'},'passage_disagreement':{'Methods':5,'Results':6},'format':'384-well ULA,800 cells,50µl,sarco-spheres','exposure':'6 days','reported_dose_design':'3-log,6-dose curves; library concentrations33pmol/l to200µmol/l','readout':'whole-well ATP,CellTiter-Glo2.0,vehicle normalization; maximalDMSO0.2%','summary_source':'Figure5 ordinal sensitivity colors; continuous per-drugAUC/IC50 and raw replicate matrix not released in the acquired primary/supplements'},'validation_context':{'selected_drugs':['carfilzomib','doxorubicin','venetoclax'],'models':['USZ20-EMC1','USZ22-EMC2'],'source':'Primary prose and Fig6a–h','results_passages':'8–10','format':'96 wells,1000 cells/well,triplicates as reported','exposure':'6 days','author_reported_monotherapy':{'carfilzomib':'high sensitivity in both models','doxorubicin':'good to moderate sensitivity in both models','venetoclax':'no monotherapy response in validation of either model despite moderate initialUSZ20screen category'},'author_reported_combination':'Carfilzomib/venetoclax and carfilzomib/doxorubicin: synergyUSZ20,additiveUSZ22; ZIP/Loewe/Bliss/HSA heatmaps are original author results, not new independent measurements','no_80_row_matrix':'Only USZ20 underwent40-drug screen; both models have selected validation, not40×2 independent response matrix'},'Iwata_frozen_input':{'url':U,'sha256':ih,'table_source_receipts':[t['source'] for t in iv['tables']],'screen_rows':len(screen),'IC50_rows':len(dose)},'join_counts':{'exact_literal_screen_unique':sum(len(r['Iwata_exact_literal_screen_rows'])==1 for r in rows),'qualified_screen_with_any_candidate':sum(bool(r['Iwata_parenthetical_case_whitespace_candidates_screen']) for r in rows),'qualified_screen_ambiguous':sum(len(r['Iwata_parenthetical_case_whitespace_candidates_screen'])>1 for r in rows),'formulation_family_with_any_candidate':sum(bool(r['Iwata_formulation_family_candidates_screen']) for r in rows)},'source_spelling_qualification':['Abmaciclib','Naraparib Tosylate','WE-822'],'limits':['All40 BangerterCAS identifiers unreported; no drug-form identity imputed from IwataCAS. Exact matches are literal labels only.','Case/parenthetical and formulation candidates are diagnostic lists, not primary harmonized joins; all returned source rows retained.','Bangerter ordinal colors are not raw viability/AUC/IC50 values; source interval gaps are not repaired.','Iwata screen dose/exposure/replicate normalization remain unverified;24IC50 rows are selected endpoints. No cross-assay pooled potency, response correlation or concordance threshold is computed.','No fusion-partner causality, target-dependence, clinical efficacy or novel rediscovery of the original author leads.']}
(O/'result.json').write_text(json.dumps(R,indent=2));print('BANGERTER_ALL40_ORDINAL_BEGIN');print(json.dumps(R));print('BANGERTER_ALL40_ORDINAL_END')
