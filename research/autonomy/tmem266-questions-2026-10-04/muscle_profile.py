"""Frozen mature-muscle profile contrast; not cellular deconvolution."""
import gzip,csv,io,zipfile,json,hashlib
from pathlib import Path
import sys
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'.cache/python-deps'))
import numpy as np

def main():
    ann=ROOT/'research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip'
    soft=ROOT/'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz'
    manifest=ROOT/'research/autonomy/atlas-hofvander-validation-2026-09-06/replication-manifest.json'
    genes=['TMEM266','ACTA1','CKM','MYH1','MYH2','MYH7'];aliases={'C15orf27':'TMEM266'}
    mapped={g:[] for g in genes};excluded=[]
    with zipfile.ZipFile(ann) as z:
        for r in csv.DictReader(io.StringIO(z.read('GPL6244-original-annotation.tsv').decode()),delimiter='\t'):
            ss={aliases.get(p.split(' // ')[1].strip(),p.split(' // ')[1].strip()) for p in r['gene_assignment'].split(' /// ') if ' // ' in p}
            if not ss&set(genes):continue
            if len(ss)==1:mapped[next(iter(ss))].append(r['ID'])
            else:excluded.append({'ID':r['ID'],'symbols':sorted(ss)})
    assert all(len(p)==1 for p in mapped.values()),mapped
    reverse={ps[0]:g for g,ps in mapped.items()};v={g:{} for g in genes}
    table=False;acc=None;col=None
    with gzip.open(soft,'rt') as f:
        for line in f:
            line=line.rstrip('\r\n')
            if line.startswith('^SAMPLE = '):acc=line.split(' = ',1)[1]
            elif line=='!sample_table_begin':table=True;col=None
            elif line=='!sample_table_end':table=False
            elif table:
                row=line.split('\t')
                if col is None:col=row;continue
                if row[0] in reverse:v[reverse[row[0]]][acc]=float(row[col.index('VALUE')])
    samples=json.loads(manifest.read_text())['array_samples'];assert len(samples)==42
    ids=[s['sample_id'] for s in samples]
    assert all(set(v[g])==set(ids) for g in genes)
    pools=[s['sample_id'] for s in samples if s['unit']=='pooled_normal_RNA']
    assert pools==['GSM600968','GSM600969']
    def summarize(anchor):
        rows=[]
        for s in samples:
            sid=s['sample_id'];d={g:v[g][sid]-anchor[g] for g in genes}
            contrast=d['TMEM266']-float(np.median([d[g] for g in genes[1:]]))
            rows.append({'sample_id':sid,'diagnosis':s['diagnosis'],'unit':s['unit'],
                         'difference_from_muscle_reference':d,'target_minus_median_marker_difference':contrast,
                         'individual_marker_contrasts':{g:d['TMEM266']-d[g] for g in genes[1:]}})
        grouped={}
        for h in sorted({s['diagnosis'] for s in samples}):
            q=[r for r in rows if r['diagnosis']==h];a=[r['target_minus_median_marker_difference'] for r in q]
            grouped[h]={'n':len(q),'contrast_median':float(np.median(a)),'contrast_min':min(a),'contrast_max':max(a),
                        'n_positive':sum(x>0 for x in a),'target_difference_median':float(np.median([r['difference_from_muscle_reference']['TMEM266'] for r in q]))}
        return {'reference':anchor,'samples':rows,'groups':grouped}
    means={g:float(np.mean([v[g][p] for p in pools])) for g in genes}
    out={'scope':'Exploratory within-platform muscle-expression-profile contrast; not purity or a cellular-mixture estimate',
         'additional_limit':'EMC and normal muscle scanned on disjoint dates; target/control differences do not remove batch confounding',
         'genes':genes,'mapping':mapped,'ambiguous_clusters_excluded':excluded,'raw_RMA_log2':v,
         'mean_two_pools':summarize(means),
         'separate_pool_sensitivities':{p:summarize({g:v[g][p] for g in genes}) for p in pools},
         'source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ann,soft,manifest]}}
    (BASE/'muscle-profile.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out['mean_two_pools']['groups']))

if __name__=='__main__':main()
