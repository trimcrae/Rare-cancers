"""Deterministic structural/provenance checks only; no expression summaries or contrasts."""
import collections, csv, gzip, hashlib, io, json, pathlib, re, xml.etree.ElementTree as ET
P=pathlib.Path(__file__).resolve().parent
PANEL=['CHRNA6','CD276','SSTR2','FAP','CD248','CSPG4','MSLN','PRAME','L1CAM','GPC3','ALPP','CDH17']
def write(name,value): (P/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def inspect():
 soft=gzip.decompress((P/'GSE119630_family.soft.gz').read_bytes()).decode('utf-8')
 samples=[]
 for block in soft.split('^SAMPLE = ')[1:]:
  d=collections.defaultdict(list)
  for line in block.splitlines():
   if line.startswith('!') and ' = ' in line:
    key,value=line.split(' = ',1);d[key[1:]].append(value)
  samples.append({'gsm':block.splitlines()[0],**d})
 human=[s for s in samples if s['Sample_organism_ch1']==['Homo sapiens']]
 write('human-sample-metadata.json',human)
 inventories={};annotations={};mapping=[]
 for name in ['GSE119630_ColonCancerReplicatesMaster.csv.gz','GSE119630_HumanGeneCountsMaster.csv.gz']:
  raw=gzip.decompress((P/name).read_bytes());rows=list(csv.reader(io.StringIO(raw.decode('utf-8'))))
  head=rows[0];data=rows[1:];assert head[:3]==['Probe_ID','Probe_Sequence','Accession']
  assert len(head)==len(set(head)) and all(len(r)==len(head) for r in data)
  # A separate delimiter parser must reproduce all fields; these files have no quoting.
  assert '"' not in raw.decode('utf-8')
  assert rows==[line.split(',') for line in raw.decode('utf-8').splitlines()]
  ids=[r[0] for r in data];assert len(ids)==len(set(ids))
  sequence_anomalies=[{'probe_id':r[0],'sequence':r[1],'characters_outside_ACGT':sorted(set(r[1])-set('ACGT'))} for r in data if not re.fullmatch(r'[ACGT]+',r[1])]
  assert all(r[2] for r in data)
  assert all(re.fullmatch(r'\d+',c) for r in data for c in r[3:])
  ann={r[0]:tuple(r[1:3]) for r in data};annotations[name]=ann
  # Prefix is source label parsing, not independently verified HGNC annotation.
  assert all(re.fullmatch(r'.+_\d+',r[0]) for r in data)
  panel={t:[{'csv_row':i+2,'probe_id':r[0],'probe_sequence':r[1],'accession':r[2]} for i,r in enumerate(data) if r[0].rsplit('_',1)[0]==t] for t in PANEL}
  stem=name.removeprefix('GSE119630_').removesuffix('.gz')
  matched=[]
  for idx,col in enumerate(head[3:],4):
   candidates=[s for s in human if col in s.get('Sample_description',[]) and stem in s.get('Sample_description',[])]
   assert len(candidates)==1,(col,len(candidates)); s=candidates[0]; matched.append(s['gsm'])
   entry={'matrix':name,'column_1based':idx,'column':col,'gsm':s['gsm'],'species':s['Sample_organism_ch1'][0],'metadata_title':s['Sample_title'][0]}
   m=re.fullmatch(r'Patient(\d+)_(Normal|Cancer)_bioRep(\d+)_techRep(\d+)',col)
   if m:
    patient,state,bio,tech=m.groups();entry.update(patient=patient,tissue_state=state,within_donor_biological_replicate=bio,technical_replicate=tech,biological_unit=f'Patient{patient}_{state}_bioRep{bio}',classification_basis='Trejo2019 sec009 p3: pathologist identified normal/cancer regions on colorectal cancer sections; header and GEO title agree',normal_scope='cancer-patient matched pathologist-designated normal region; not healthy donor' if state=='Normal' else None)
    assert f'Patient {patient},' in entry['metadata_title']
    assert f'biological replicate {bio}, technical replicate {tech}' in entry['metadata_title']
    assert ('normal colon tissue' if state=='Normal' else 'cancerous colon tissue') in entry['metadata_title']
   elif col.startswith('F2'): entry.update(tissue_state='cancer',classification_basis='Trejo2019 body text: Fig2 human samples colorectal/prostate adenocarcinoma and pancreatic cancer')
   elif col.startswith('F4'): entry.update(tissue_state='archival cancer',classification_basis='Trejo2019 archival FFPE results: colon1986, kidney1988/1994, hepatocellular carcinoma1993; no donor split inferred from column numeric tokens')
   elif col.startswith('F7'): entry.update(tissue_state='prostate cancer staining/deparaffinization comparison',classification_basis='Trejo2019 H&E results Fig9, despite older GEO Fig7 label')
   elif col.startswith('F6'): entry.update(tissue_state='breast cancer cell line; fresh or fixed',classification_basis='GEO source/preparation and Trejo2019 cell-pellet methods; no normal human tissue')
   else: raise AssertionError(col)
   mapping.append(entry)
  assert len(matched)==len(set(matched))
  inventories[name]={'sha256':sha(P/name),'decompressed_sha256':hashlib.sha256(raw).hexdigest(),'probe_rows':len(data),'annotation_columns':head[:3],'sample_columns':head[3:],'sample_count':len(head)-3,'count_cells_checked':len(data)*(len(head)-3),'all_count_cells_nonnegative_integer_lexemes':True,'finite_count_cells':True,'duplicate_probe_ids':0,'duplicate_sample_headers':0,'all_rows_rectangular':True,'independent_delimiter_decode_matches':True,'sequence_anomalies_preserved':sequence_anomalies,'sequence_length_distribution':dict(sorted(collections.Counter(len(r[1]) for r in data).items())),'distinct_source_symbol_prefixes':len(set(r[0].rsplit('_',1)[0] for r in data)),'fixed_panel':panel}
  with (P/(stem.removesuffix('.csv')+'-probe-annotations.tsv')).open('w',newline='',encoding='utf-8') as f:
   w=csv.writer(f,delimiter='\t');w.writerow(['csv_row','Probe_ID','source_symbol_prefix','Probe_Sequence','Accession']);w.writerows([i+2,r[0],r[0].rsplit('_',1)[0],r[1],r[2]] for i,r in enumerate(data))
 assert len(mapping)==len(human) and len({m['gsm'] for m in mapping})==len(human)
 a,b=annotations.values()
 inventories['between_human_matrices']={'probe_id_sets_equal':a.keys()==b.keys(),'probe_sequence_accession_mapping_equal':a==b,'ordering_equal':list(a)==list(b)}
 normal=[m for m in mapping if m.get('tissue_state')=='Normal']
 assert len(normal)==30 and len({m['patient'] for m in normal})==5 and len({m['biological_unit'] for m in normal})==10
 inventories['metadata']={'series_sample_species_counts':dict(collections.Counter(s['Sample_organism_ch1'][0] for s in samples)),'human_samples':len(human),'all_human_samples_map_exactly_once':True,'normal_libraries':30,'normal_within_patient_biological_units':10,'normal_patients':5,'healthy_donor_samples_identified':0,'normal_unit_description':'Two separately lysed normal-region samples per patient, each assayed three times; not 30 patients or 10 independent donors.'}
 write('sample-column-mapping.json',mapping);write('structural-inventory.json',inventories)
 # Preserve source locators for both articles and the supplied PeerJ methods.
 loc=[]
 for file in [P/'article.xml',P/'yeakley2017.xml',P.parent/'peerj21497-source-2026-09-06/article.xml']:
  t=ET.parse(file)
  for sec in t.findall('.//sec'):
   for i,e in enumerate(sec.findall('p'),1):
    text=''.join(e.itertext())
    if any(k in text.lower() for k in ['probe','normal tissue','pathologist','replicate','attenuat','quality control','normalization','homogenous tumor','prostate cancer slides','archival human tumor']):
     loc.append({'source':str(file.relative_to(P.parent)).replace('\\','/'),'sha256':sha(file),'section_id':sec.get('id'),'section_title':sec.findtext('title'),'direct_p_index_1based':i,'text':text})
 write('primary-method-locators.json',loc)
 return inventories
if __name__=='__main__':
 result=inspect(); print(json.dumps({'status':'passed','matrices':{k:{f:v[f] for f in ['probe_rows','sample_count','count_cells_checked']} for k,v in result.items() if k.endswith('.gz')},'between_human_matrices':result['between_human_matrices'],'metadata':result['metadata']},indent=2))

