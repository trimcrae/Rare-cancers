from pathlib import Path
import json,hashlib,gzip,csv,statistics,zipfile,io,collections
import numpy as np
base=Path(__file__).parent
owner=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round3/dlk1')
root=Path('C:/Projects/EMC-Research/research/autonomy')
plan=json.loads((owner/'PLAN.json').read_text());reported=json.loads((owner/'retained-results.json').read_text())
source=root/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
with gzip.open(source,'rt') as f:
 reader=csv.reader(f,delimiter='\t');header=next(reader)
 rows=[r for r in reader if r[0]=='DLK1']
assert len(rows)==1
measurements={k:float(v) for k,v in zip(header[1:],rows[0][1:])}
ids=plan['primary']['sample_ids'];values=[measurements[i] for i in ids]
assert {i:measurements[i] for i in ids}==reported['tissue']['primary']['values']
rng=np.random.default_rng(41026)
medians=[statistics.median(rng.choice(values,size=len(values),replace=True)) for _ in range(2000)]
median_ci=np.percentile(medians,[2.5,97.5]).tolist()
assert np.allclose(median_ci,reported['tissue']['primary']['median_bootstrap95_percentile'])
atlas={'all13':{i:measurements[i] for i in plan['sensitivities']['all13_ids']},'primary_n':len(values),'primary_median':statistics.median(values),'primary_n_ge10':sum(x>=10 for x in values),'primary_median_bootstrap95':median_ci}
annotation_zip=root/'atlas-original-array-source-2026-09-06/original-source-recovery.zip'
with zipfile.ZipFile(annotation_zip) as z:
 annotation_rows=list(csv.DictReader(io.StringIO(z.read('GPL6244-original-annotation.tsv').decode()),delimiter='\t'))
matches=[]
for r in annotation_rows:
 symbols=set();entrez=set()
 for a in r['gene_assignment'].split(' /// '):
  p=a.split(' // ')
  if len(p)>=5:symbols.add(p[1].strip());entrez.add(p[4].strip())
 if 'DLK1' in symbols or '8788' in entrez:matches.append({'probe':r['ID'],'symbols':sorted(symbols),'entrez':sorted(entrez)})
assert matches==[{'probe':'7976783','symbols':['DLK1'],'entrez':['8788']}]
array_source=root/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz';arr={};sid=None
with gzip.open(array_source,'rt') as f:
 for line in f:
  if line.startswith('^SAMPLE = '):sid=line.rstrip().split(' = ')[1]
  elif sid is not None and line.startswith('7976783\t'):arr[sid]=float(line.split('\t')[1])
assert arr==reported['array']['all_probe_values']['7976783']
groups=collections.defaultdict(list)
for m in plan['array_metadata']:groups[m['diagnosis']].append(m['sample_id'])
emc=[arr[s] for s in groups['Extraskeletal myxoid chondrosarcoma']]
comparisons={}
for name,ss in groups.items():
 if name=='Extraskeletal myxoid chondrosarcoma':continue
 ref=[arr[s]for s in ss]
 a=sum((v>w)+0.5*(v==w)for v in emc for w in ref)/(len(emc)*len(ref))
 comparisons[name]={'n_emc':len(emc),'n_control':len(ref),'A':a,'control_median':statistics.median(ref)}
 assert abs(a-reported['array']['contrasts'][name]['A'])<1e-14
culture=root/'tmem266-all-cultures-2026-10-04/archs4-subset.zip'
with zipfile.ZipFile(culture) as z:
 reader=csv.reader(io.StringIO(z.read('matrix.tsv').decode()),delimiter='\t');header=next(reader);counts=[0]*(len(header)-1);target=[]
 for r in reader:
  for j,v in enumerate(r[1:]):counts[j]+=int(v)
  if r[0]=='DLK1':target.append([int(v)for v in r[1:]])
assert len(target)==1
cult={s:{'rounded_estimated_counts':target[0][i],'column_sum':counts[i],'CPM':target[0][i]/counts[i]*1e6}for i,s in enumerate(header[1:])}
assert {s:r['column_sum']for s,r in cult.items()}==reported['cultures']['column_sums']
assert all(abs(r['CPM']-reported['cultures']['DLK1_rows'][0]['CPM_rounded_estimates'][s])<1e-14 for s,r in cult.items())
files=[owner/'PLAN.json',owner/'retained-results.json',source,annotation_zip,array_source,culture]
out={'status':'PASS','input_hashes':{str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in files},'atlas':atlas,'array':{'annotation_matches':matches,'all_gene_values':arr,'EMC_median':statistics.median(emc),'comparisons':comparisons},'culture':cult,'limits':'Specimens and cultures are not pooled as independent patients; bootstrap is descriptive; operational TPM gate is not a protein/detection threshold; two high bulk specimens do not identify a biological subtype.'}
(base/'numeric-crosscheck.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({'status':'PASS','atlas':atlas,'array_n':len(arr),'culture':cult},indent=2))
