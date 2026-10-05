import collections,datetime,gzip,hashlib,json,pathlib,re,xml.etree.ElementTree as ET
B=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/workspace/Rare-cancers')
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
F=ROOT/'research/autonomy/fresh-discovery-2026-10-04/functional'
a=load(F/'reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json');i=load(F/'reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json')
assert len(a['rows'])==40 and [len(t['records']) for t in i['tables']]==[221,24]
# Literal alias audit only. Unknown brands, spellings and unreported CAS are not assumed chemically resolved.
aliases=['RSL3','ML162','ML210','erastin','imidazole ketone erastin','sulfasalazine','ferrostatin','liproxstatin','FIN56','FINO2','deferoxamine','buthionine sulfoximine']
allrows=[{'cohort':'Bangerter40','label':r['literal_figure_drug']} for r in a['rows']]+[{'cohort':'Iwata_'+t['source']['file'],'label':r['drug']} for t in i['tables'] for r in t['records']]
hits={s:[r for r in allrows if s.lower() in r['label'].lower()] for s in aliases};assert not any(hits.values())
relevant_i=[dict(r,source=t['source']['file']) for t in i['tables'] for r in t['records'] if any(s in r['drug'].lower() for s in ['sorafenib','conoidin','artemether','arsenic','prima-1','aminolevulin'])]
relevant_a=[r for r in a['rows'] if r['literal_figure_drug']=='Sorafenib'];assert len(relevant_i)==7 and len(relevant_a)==1
measurements={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'question':'Prospectively frozen lipid-redox/ferroptosis mechanism; these reused viability observations are not mechanism measurements.','NCC_model':i['model'],'NCC_conditions':relevant_i,'USZ_condition':[{'model':r['source_model'],'drug':r['literal_figure_drug'],'source_panel':r['source_panel'],'category':r['ordinal_source_category'],'literal_legend_range':a['literal_legend_ranges'][r['ordinal_source_category']]} for r in relevant_a],'NCC_screen_limit':i['updated_source_qualification'],'NCC_IC50_units':i['unit_qualification'],'USZ_screen_context':a['screen_context'],'source_cautions':a['limits'],'interpretation':'Unclipped normalized viability and sourceSD; no patient-level pooling, salt equivalence, drug-resistance, ferroptosis, GPX4 dependence, clinical effect or independent replication inferred. Sorafenib viability discordance does not establish a shared mechanism.'}
measurements['selection_disclosure']='The seven NCC redox-adjacent compound labels and one USZ sorafenib row were descriptively selected after reading the complete rosters, based on compound labels rather than positive values. They are not prospective mechanistic endpoints or a new hit-ranking; the original frozen GPX4/xCT question and failure rule remain unchanged.'
(B/'REUSED-MEASUREMENTS.json').write_text(json.dumps(measurements,indent=2)+'\n')
roster={'source_bindings':[bind(F/'reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json'),bind(F/'reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json')],'rows':allrows,'counts':dict(collections.Counter(r['cohort'] for r in allrows)),'canonical_literal_alias_matches':hits,'limits':'Complete declared drug-name roster only, not complete chemical-target coverage. No raw responses reread to select a positive signal; all source means/SD/IC50 remain in bound reused records. No metabolic inference from drug-label absence.'}
(B/'COMPLETE-SCREEN-ROSTER.json').write_text(json.dumps(roster,indent=2)+'\n')
meta=ROOT/'research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json';hof=[r for r in load(meta)['samples'] if r['diagnosis']=='Extraskeletal myxoid chondrosarcoma'];assert len(hof)==13
mp=ROOT/'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz';samples=[];cur=None
with gzip.open(mp,'rt',errors='replace') as f:
 for line in f:
  if line.startswith('^SAMPLE = '):
   if cur:samples.append(cur)
   cur={'accession':line.strip().split(' = ',1)[1],'source_metadata':[]}
  elif cur and line.startswith(('!Sample_title =','!Sample_characteristics_ch1 =','!Sample_molecule_ch1 =')):cur['source_metadata'].append(line.strip())
if cur:samples.append(cur)
gse=[r for r in samples if any('extraskeletal myxoid chondrosarcoma' in x.lower() for x in r['source_metadata'])];assert len(gse)==6
context={'source_bindings':[bind(meta),bind(mp)],'all13_Hofvander_EMC':hof,'all6_GSE24369_EMC':gse,'GSE_total_source_samples':len(samples),'scope':'Every EMC-labelled source record retained, including all prior-context exclusions and overlap flags. These are bulkRNA measurements, unsuitable for direct lipid-peroxidation/nutrient flux/perturbation-rescue inference. No new expression values inspected or surrogate dependency claimed. Past eligibility booleans are historical and do not exclude any of13 here; cross-source independence unproved.'}
(B/'RNA-SOURCE-CONTEXT.json').write_text(json.dumps(context,indent=2)+'\n')
# Focused primary eligibility and opposing mechanism observations, not full-source paragraph dumps.
primary=[]
for pmc in ['PMC10094087','PMC11713734']:
 p=B/'raw'/(pmc+'.xml');root=ET.fromstring(p.read_bytes());pars=[' '.join(' '.join(x.itertext()).split()) for x in root.iter('p')]
 primary.append({'id':pmc,'source_binding':bind(p),'title':' '.join(root.find('.//article-title').itertext()),'selected_eligibility_rows':[s for s in pars if ('SW872' in s and 'MG63' in s and ('ALA (3 mM)' in s or 'purchased' in s)) or (pmc=='PMC11713734' and ('IB106' in s and 'JR588' in s and 'four' in s.lower() and len(s)<1200)) or ('significant toxicity' in s and 'RSL3' in s)]})
for pmc in ['PMC5667900','PMC5933935']:
 p=B/'raw'/(pmc+'-bioc.xml');root=ET.fromstring(p.read_bytes());pars=[x.findtext('text','') for x in root.findall('.//passage')]
 primary.append({'id':pmc,'source_binding':bind(p),'selected_eligibility_rows':[s for s in pars if s.startswith('HT-1080 fibrosarcoma cells') or s.startswith('HER2 amplified breast cancer BT474') or 'SNAIL1' in s and 'TWIST1' in s and 'did not show consistent' in s]})
# Add the shortest exact primary passage that explicitly names the complete UPS roster.
u=ET.fromstring((B/'raw/PMC11713734.xml').read_bytes());candidates=[' '.join(' '.join(x.itertext()).split()) for x in u.iter('p')];full=[s for s in candidates if all(n in s for n in ['IB106','JR588','IB119','KN473'])];assert full
next(x for x in primary if x['id']=='PMC11713734')['complete_four_model_source_passage']=min(full,key=len)
(B/'PRIMARY-ELIGIBILITY-EXCERPTS.json').write_text(json.dumps(primary,indent=2)+'\n')
print('verified all40/221/24 source rows;0canonical named matches;7NCC+1USZ focused observations; all13+6RNA source records;4primary sources')
