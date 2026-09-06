"""Outcome-blind source/selection manifest builder; never parses matrix values."""
from pathlib import Path
import argparse,csv,json,hashlib,collections
import openpyxl
PANEL='CD276 SSTR2 PRAME FAP CD248 CSPG4 MSLN L1CAM GPC3 ALPP CDH17'.split()
EMC='Extraskeletal myxoid chondrosarcoma'
PRIMARY=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
CONTEXT=['Myxofibrosarcoma','Dermatofibrosarcoma protuberans']
OLD={'104-92':'MDB 9736:3','168-97':'MDB 9736:4','536-00':'MDB 9736:7'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build(src,out):
    meta={r['lab_no']:{k:r[k] for k in ['lab_no','Diagnosis','sequencing_year']} for r in csv.DictReader((src/'source_data/meta_data.txt').open(),delimiter='\t')}
    with (src/'source_data/tpm_matrix.tsv').open() as f: header=f.readline().rstrip('\n').split('\t')[1:]
    assert len(header)==len(set(header))==704 and set(header)==set(meta)
    features=(src/'matrix-feature-identifiers.txt').read_text().splitlines()
    assert all(features.count(g)==1 for g in PANEL+['CHRNA6'])
    rows=openpyxl.load_workbook(src/'ccr-25-3740_supplementary_table_s1_suppts1.xlsx',read_only=True,data_only=True).active.iter_rows(values_only=True)
    manifest=[];foot=[]
    for n,r in enumerate(rows,1):
        label=str(r[0] or '');sid=label.split('_')[0]
        if sid not in meta:
            if n>705: foot.append([n, str(r[0] or ''),str(r[1] or '')])
            continue
        d=str(r[1] or '');rev=str(r[2] or '');lesion=str(r[12] or '')
        m={'sample_id':sid,'source_label':label,'s1_row':n,'diagnosis':d,'revised_diagnosis':rev,'deposited_diagnosis':meta[sid]['Diagnosis'],'sequencing_year':meta[sid]['sequencing_year'],'specimen_exception':lesion,'prior_comment':str(r[21] or ''),'known_overlap':OLD.get(sid,''),'source_group':'Hofvander2026','patient_group':sid}
        m['primary_lesion']=not lesion
        m['eligible']=not lesion and sid not in OLD
        m['role']='EMC' if d==EMC else 'primary_comparator' if d in PRIMARY else 'context_comparator' if d in CONTEXT else 'not_prespecified'
        m['exclusion_reason']='known_EMC_discovery_overlap' if sid in OLD else 'nonprimary_or_unspecified_exception' if lesion else 'outside_prespecified_histologies' if m['role']=='not_prespecified' else ''
        manifest.append(m)
    assert len(manifest)==704 and len({r['sample_id'] for r in manifest})==704
    included=[r for r in manifest if r['eligible']]
    assert sum(r['diagnosis']==EMC for r in included)==9
    cells={d:dict(sorted(collections.Counter(r['sequencing_year'] for r in included if r['diagnosis']==d).items())) for d in [EMC]+PRIMARY+CONTEXT}
    sources={str(p.relative_to(src)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in [src/'source_data/tpm_matrix.tsv',src/'source_data/meta_data.txt',src/'ccr-25-3740_supplementary_table_s1_suppts1.xlsx',src/'matrix-feature-identifiers.txt',src/'hofvander2026.xml',src/'primary-methods-locators.json']}
    sources={k.replace('\\','/'):v for k,v in sources.items()}
    assert sources['source_data/tpm_matrix.tsv']['sha256']=='b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3'
    out.mkdir(parents=True,exist_ok=True)
    obj={'schema':1,'source_files':sources,'source_location':str(src),'panel':PANEL,'context_control':['CHRNA6'],'primary_histologies':PRIMARY,'context_histologies':CONTEXT,'eligible_year_counts':cells,'samples':manifest,'s1_footnotes':foot}
    (out/'metadata-manifest.json').write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cells':cells,'revision_counts':dict(collections.Counter(r['revised_diagnosis'] for r in manifest if r['role']!='not_prespecified')),'specimen_flags':dict(collections.Counter(r['specimen_exception'] for r in manifest)),'footnotes':foot},indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--output',type=Path,default=Path(__file__).parent);v=a.parse_args();build(v.source,v.output)
