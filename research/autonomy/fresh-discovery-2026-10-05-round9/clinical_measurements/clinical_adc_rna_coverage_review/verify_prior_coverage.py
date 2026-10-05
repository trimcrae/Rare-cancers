"""Offline whitelist checks; never select expression/statistical columns."""
import csv,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
checks=[]
def check(n,ok):
 checks.append({'check':n,'pass':bool(ok)})
 assert ok,n

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads(P.joinpath('PRIOR-EXPOSURE-REPLAY.json').read_text())
s=prior['literal_TSV_source'];check('Exact oldscreen sourcehash',sha(s['path'])==s['sha256'])
with Path(s['path']).open() as h:
 r=csv.reader(h,delimiter='\t');header=next(r);gi=header.index('gene');ai=header.index('allocated')
 masked=[{'gene':row[gi],'allocated':row[ai]} for row in r if row[gi] in ['ERBB2','TACSTD2','NECTIN4','FOLR1','CD276','GPNMB','LRRC15']]
check('NameBoolean whitelist matches',masked==prior['observations'])
for g in ['GPNMB','LRRC15']:check(g+' oldBoolean only',[x for x in masked if x['gene']==g]==[{'gene':g,'allocated':'False'}])
for b in prior['bindings']:check('Priorbinding '+Path(b['path']).name,sha(b['path'])==b['sha256'])
c=json.loads(P.joinpath('NATIVE-TISSUE-CONDITION-COVERAGE.json').read_text())
for b in c['frozen_metadata_bindings']:check('Frozenmetadata '+Path(b['path']).name,sha(b['path'])==b['sha256'])
check('All13Hof metadata units',len(c['all13_Hofvander'])==13)
check('All6and10array metadata units',sorted(len(s['conditions']) for s in c['all16_array_conditions'])==[6,10])
check('All4FFPE3SEQmetadata units',len(c['all4_FFPE_3SEQ_conditions'])==4)
check('No newgenes or matrices',c['new_gene_values_or_matrices']==0)
a=json.loads(P.joinpath('ACCESS-RESOURCE.json').read_text());check('No newsourcecalls/rawinputs',a['new_GETs']==0 and a['new_original_bytes']==0 and a['copied_matrices_or_originals']==0)
check('Freefloor preserved',a['free_bytes']>=a['floor_bytes'])
check('Numericalstage off',a['new_numerical_stage'] is False)
clinical=json.loads(P.joinpath('CLINICAL-METADATA-INDEPENDENT-CHECK.json').read_text())
check('Exact ownerplan beforevalues',sha(clinical['owner_plan']['path'])==clinical['owner_plan']['sha256'])
receipts=json.loads(Path(clinical['owner_queries']['path']).read_text())
check('Ownerqueryreceipt unchanged',sha(clinical['owner_queries']['path'])==clinical['owner_queries']['sha256'])
for record in clinical['evaluated_records']:
 check(record['gene']+' rawhash',sha(record['source_path'])==record['sha256'])
 source=json.loads(Path(record['source_path']).read_text())
 r=next(x for x in receipts if x['gene']==record['gene'])
 check(record['gene']+' matchesactualretrieval',r['sha256']==record['sha256'] and r['bytes']==record['bytes'])
 selected=record['selected_primary']
 metadata=[{k:x.get(k) for k in ['id','pmcid','doi','title','pubYear']} for x in source['resultList']['result'] if x['id']==selected['id']]
 check(record['gene']+' exactcitationonly',metadata==[selected])
print(json.dumps({'scope':'Offline sourcehash/nameBoolean/sourceunitmask verification; no network or expression arrays','count':len(checks),'checks':checks,'all_pass':all(x['pass'] for x in checks)},indent=2))
