"""Build original-array replication metadata without reading expression values."""
from pathlib import Path
import argparse,json,collections
from metadata import PANEL,EMC,sha
BASE=Path(__file__).parent
def build(src):
    roster=[r for r in json.loads((src/'sample-rosters.json').read_text()) if r['gse']=='GSE24369']
    assert len(roster)==42 and len({r['gsm'] for r in roster})==42
    mapping=json.loads((src/'GPL6244-fixed12-probe-map.json').read_text());genes=PANEL+['CHRNA6'];probes={}
    for g in genes:
        found=[r for r in mapping if r['target_symbols']==[g]]
        assert len(found)==1 and found[0]['unique_gene'] and found[0]['all_assigned_symbols']==[g]
        probes[g]=found[0]['probe_id']
    ranges=[(600928,600933,'Desmoid'),(600934,600939,EMC),(600940,600956,'Low-grade fibromyxoid sarcoma'),(600957,600962,'Myxofibrosarcoma'),(600963,600967,'Solitary fibrous tumor'),(600968,600969,'Skeletal muscle pools')]
    rows=[]
    for r in roster:
        n=int(r['gsm'][3:]);diag=next(d for a,b,d in ranges if a<=n<=b)
        assert r['platform']=='GPL6244' and r['VALUE_definition']==['RMA log2 signal']
        rows.append({**r,'sample_id':r['gsm'],'diagnosis':diag,'unit':'pooled_normal_RNA' if n>=600968 else 'tumor_biopsy','lesion_stage':'not established','patient_crosswalk':'not established'})
    hm=json.loads((BASE/'metadata-manifest.json').read_text());hs=['Low-grade fibromyxoid sarcoma','Myxofibrosarcoma','Solitary fibrous tumor','Desmoid']
    hof=[r for r in hm['samples'] if r['eligible'] and r['diagnosis'] in [EMC]+hs]
    files=['GSE24369.soft.gz','GPL6244-original-annotation.tsv','GPL6244-fixed12-probe-map.json','sample-rosters.json','GSE24369.soft-sample-metadata.json']
    sources={f:{'sha256':sha(src/f),'bytes':(src/f).stat().st_size} for f in files}
    assert sources['GSE24369.soft.gz']['sha256']=='98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37'
    out={'schema':1,'source_location':str(src),'source_files':sources,'gene_to_probe':probes,'array_samples':rows,'array_counts':dict(collections.Counter(r['diagnosis'] for r in rows)),'hofvander_samples':hof,'hofvander_counts':dict(collections.Counter(r['diagnosis'] for r in hof)),'primary_replication_histology':hs[0],'secondary_replication_histologies':hs[1:]}
    (BASE/'replication-manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({'array_counts':out['array_counts'],'hofvander_counts':out['hofvander_counts'],'gene_to_probe':probes},indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);build(a.parse_args().source)
