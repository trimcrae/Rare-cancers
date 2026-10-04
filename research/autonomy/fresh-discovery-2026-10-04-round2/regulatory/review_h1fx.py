"""Independent source/value challenge; reads lead outputs, never edits them."""
from pathlib import Path
import csv,gzip,json,hashlib,statistics,xml.etree.ElementTree as ET
from collections import Counter
from scipy.stats import mannwhitneyu
P=Path(__file__).resolve().parent
L=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-lead/research/autonomy/fresh-discovery-2026-10-04-round2')
R=Path('C:/Projects/EMC-Research/research/autonomy')
paper=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04/microenvironment/peerj2026.xml')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads((L/'h1fx/expression-results.json').read_text())
sources=[L/'H1FX-FOLLOWUP-CONTRACT.json',L/'h1fx/AMENDMENT-01.json',L/'h1fx/analyze_h1fx.py',L/'h1fx/expression-results.json',L/'h1fx/GSE6481-samples.txt',paper]
with gzip.open(R/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz','rt',encoding='utf-8-sig') as f:
 rd=csv.reader(f,delimiter='\t');head=next(rd);matches=[r for r in rd if r[0] in ['H1FX','H1-10']]
assert len(matches)==1
raw=dict(zip(head[1:],map(float,matches[0][1:])))
assert raw==j['RNA_all_source_gene_values']['H1FX']
emc=j['RNA_all_EMC_metadata']; assert len(emc)==13
def pairwise(a,b):return sum(1 if x>y else .5 if x==y else 0 for x in a for y in b)/(len(a)*len(b))
checks=[]
for scope,es in [('primary9',[s for s in emc if s['eligible']]),('all12primary',[s for s in emc if s['primary_lesion']]),('all13',emc)]:
 a=[raw[s['sample_id']] for s in es]
 for name,ss in j['RNA_comparator_metadata'].items():
  b=[raw[s['sample_id']] for s in ss];old=j['RNA_results']['H1FX'][scope][name]
  result={'scope':scope,'contrast':name,'n':(len(a),len(b)),'A':pairwise(a,b),'EMC_median':statistics.median(a),'comparator_median':statistics.median(b)}
  assert abs(result['A']-old['A'])<1e-14
  assert result['EMC_median']==old['EMC_median'] and result['comparator_median']==old['comparator_median']
  checks.append(result)
array={};sample=None;inside=False;value_col=None
with gzip.open(R/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz','rt') as f:
 for line in f:
  line=line.rstrip('\r\n')
  if line.startswith('^SAMPLE = '):sample=line.split(' = ')[1]
  elif line=='!sample_table_begin':inside=True;value_col=None
  elif line=='!sample_table_end':inside=False
  elif inside:
   cells=line.split('\t')
   if value_col is None:value_col=cells.index('VALUE')
   elif cells[0]=='8090555':array[sample]=float(cells[value_col])
assert array==j['array_per_probe_values']['8090555']
for name,old in j['array_results']['H1FX'].items():
 a=[array[s['sample_id']] for s in j['array_all_sample_metadata'] if s['diagnosis']=='Extraskeletal myxoid chondrosarcoma']
 b=[array[s['sample_id']] for s in j['array_all_sample_metadata'] if s['diagnosis']==name]
 assert abs(pairwise(a,b)-old['A'])<1e-14
 assert abs(mannwhitneyu(a,b,method='exact').pvalue-old['p_two_sided'])<1e-14
 checks.append({'scope':'array','contrast':name,'n':(len(a),len(b)),'A':pairwise(a,b),'EMC_median':statistics.median(a),'comparator_median':statistics.median(b)})
hist=[]
for line in (L/'h1fx/GSE6481-samples.txt').read_text().splitlines():
 if line.startswith('!Sample_characteristics_ch1 = Histology:'):hist.append(line.split('Histology:',1)[1].strip())
assert len(hist)==105 and Counter(hist)['Myxoid liposarcoma']==19
r=ET.parse(paper).getroot()
claims=[' '.join(' '.join(e.itertext()).split()) for e in r.findall('.//p') if any(t in ' '.join(e.itertext()) for t in ['GSE6481','epigenetic anchor','not detectable'])]
out={'date':'2026-10-04','reviewer':'functional_models independent worker',
 'bound_hashes':{str(p):sha(p) for p in sources},'raw_H1FX_RNA_value_check':'PASS, all retained source samples exactly match original TPM row',
 'raw_H1FX_array_value_check':'PASS, all probe8090555 values exactly match original GEO processed tables',
 'summary_checks':checks,'GSE6481_histology_counts':dict(Counter(hist)),'source_claims_evaluated':claims,
 'validity':'Accession mismatch is established for the named GSE6481:105 samples,19 MLPS,zero explicit EMC/cartilaginous tumors. This does not identify the intended 19 cases or prove fabricated measurements. H1FX contrasts in authenticated RNA/array data are arithmetically supported.',
 'scientific_value':'SHELVE standalone biological paper. The original article already reports no enrichment versus soft-tissue sarcomas, and frames the positive lineage claim specifically versus cartilaginous tumors. New myxoid-comparator negative/context does not directly test that key contrast. The serious source-provenance failure removes claimed support but is not yet new disease biology.',
 'contrary_and_limits':['RNA H1FX year2021 EMC specimen227.54TPM exceeds MLPS/LGFMS/MFS medians; pooled contrasts do not establish a uniform lineage program. Same-year strata are tiny and do not resolve technical or donor effects.',
 'Array lower-LGFMS result is a subgroup of a source the article already reports as non-enriched; RNA LGFMS comparison is inconclusive, not validation of a lower disease-specific signal.',
 'Mixed RNA comparator includes benign/intermediate tissue; lead amendment corrects interpretation. Do not label it malignant-only.',
 'Known RNA discovery overlap excluded inprimary9 but retained inall12/13; cross-array RNA patient overlap unresolved. No pooling sample sizes or independent replication assertion.',
 'H1FX protein nondetection and prognostic overfitting already disclosed by authors. No new clinical or dependency inference.',
 'Older public EMC arrays and true cartilaginous comparison still unevaluated for any advanced biological claim. Cultures relevant only if a tumor-cell/functional claim is added; no automatic substitute for tissue.'],
 'reopening':'An identified authentic19-case source and reproducible cartilaginous contrast, or complete authenticated tissue comparison addressing that biologically meaningful distinction, could change the decision. Current result merits preserved provenance record, not a full EMC discovery manuscript.'}
(P/'h1fx-independent-challenge.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('H1FX independent checks PASS:',len(checks),'contrasts; GSE6481',len(hist),'samples. Decision: shelve biological paper.')
