"""Independent source parsing and exact pair-count verification. No worker imports."""
import pathlib,csv,gzip,json,hashlib,datetime,collections,bisect,math
from decimal import Decimal
from fractions import Fraction
import openpyxl
OUT=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('C:/Users/mcrae/.codex/worktrees/atlas-hofvander-validation-20260906/EMC-Research/research/autonomy/atlas-hofvander-validation-2026-09-06')
H=pathlib.Path('C:/Users/mcrae/.codex/worktrees/8010/EMC-Research/.cache/emc-atlas-new-source-20260906')
A=pathlib.Path('C:/Users/mcrae/.codex/worktrees/8010/EMC-Research/.cache/atlas-original-array-recovery-20260906')
EMC='Extraskeletal myxoid chondrosarcoma';PRIMARY=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma'];SHARED=['Low-grade fibromyxoid sarcoma','Myxofibrosarcoma','Solitary fibrous tumor','Desmoid']
GENES='CD276 SSTR2 PRAME FAP CD248 CSPG4 MSLN L1CAM GPC3 ALPP CDH17 CHRNA6'.split()
counts=collections.Counter();discrepancies=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def check(actual,expected,where):
    counts['assertions']+=1
    same=(actual is None and expected is None) or (actual is not None and expected is not None and abs(float(actual)-float(expected))<1e-12)
    if not same:discrepancies.append({'where':where,'actual':actual,'expected':float(expected) if expected is not None else None})
def prob(e,c,val):
    if not e or not c:return None
    ys=sorted(val[i] for i in c);score=0
    for i in e:
        lo=bisect.bisect_left(ys,val[i]);hi=bisect.bisect_right(ys,val[i]);score+=2*lo+hi-lo
    return Fraction(score,2*len(e)*len(c))
def contrast(rows,h,val):
    e=[r['id'] for r in rows if r['d']==EMC];c=[r['id'] for r in rows if r['d']==h]
    cells={};matched=[]
    for y in sorted({r['year'] for r in rows if r['d'] in [EMC,h]}):
        ee=[r['id'] for r in rows if r['d']==EMC and r['year']==y];cc=[r['id'] for r in rows if r['d']==h and r['year']==y]
        v=prob(ee,cc,val);cells[y]=(ee,cc,v)
        if v is not None:matched.extend([v]*len(ee))
    return {'marginal':prob(e,c,val),'matched':sum(matched,Fraction())/len(matched) if matched else None,'cells':cells,'e':e,'c':c}
def summary(rows,hs,val):
    stats={h:contrast(rows,h,val) for h in hs};s={}
    for mode in ['marginal','matched']:
        v=[stats[h][mode] for h in hs];s[mode]=sum(v,Fraction())/len(v) if v and all(x is not None for x in v) else None
    return stats,s
def verify_ev(published,rows,val,where):
    hs=list(published['histologies']);stats,s=summary(rows,hs,val)
    for mode in s:check(published['summary'][mode],s[mode],where+'/summary/'+mode)
    for h,p in published['histologies'].items():
        st=stats[h]
        for mode in ['marginal','matched']:check(p[mode],st[mode],where+'/'+h+'/'+mode)
        if 'cells' in p:
            check(p['n_emc'],len(st['e']),where+'/nE');check(p['n_comparator'],len(st['c']),where+'/nC')
            den=sum(len(e) for e,c,v in st['cells'].values() if v is not None)
            check(p['matched_emc'],den,where+'/matchedN')
            for cell in p['cells']:
                ee,cc,v=st['cells'][cell['year']]
                for key,expected in [('A',v),('n_emc',len(ee)),('n_comparator',len(cc)),('pairs',len(ee)*len(cc)),('weight',Fraction(len(ee),den) if v is not None and den else 0)]:check(cell[key],expected,where+'/cell/'+key)
            for place in p['placements']:
                i=place['sample_id'];y=next(r['year'] for r in rows if r['id']==i)
                check(place['TPM'],val[i],where+'/placementvalue')
                check(place['marginal_placement'],prob([i],st['c'],val),where+'/placementM')
                cc=[r['id'] for r in rows if r['d']==h and r['year']==y]
                check(place['matched_placement'],prob([i],cc,val),where+'/placementY')
    counts['verified_estimate_blocks']+=1
    return stats,s

assert load(W/'results/execution.json')['status']=='complete'
assert load(W/'replication-results/execution.json')['status']=='complete'
hm=load(W/'metadata-manifest.json');am=load(W/'replication-manifest.json')
for m in [hm,am]:
    for name,v in m['source_files'].items():assert sha(pathlib.Path(m['source_location'])/name)==v['sha256'];counts['source_hashes']+=1
hr=load(W/'results/result.json');ar=load(W/'replication-results/result.json')
for result in [hr,ar]:
    for name,digest in result['authorization']['sha256'].items():assert sha(W/name)==digest;counts['authorized_file_hashes']+=1
metadata={r['lab_no']:r for r in csv.DictReader((H/'source_data/meta_data.txt').open(),delimiter='\t')}
s1=openpyxl.load_workbook(H/'ccr-25-3740_supplementary_table_s1_suppts1.xlsx',read_only=True,data_only=True).active
allrows=[]
for v in s1.iter_rows(min_row=3,values_only=True):
    sid=str(v[0] or '').split('_')[0]
    if sid in metadata:
        allrows.append({'id':sid,'d':v[1],'year':metadata[sid]['sequencing_year'],'revised':v[2],'lesion':v[12],'comment':v[21]})
assert len(allrows)==len({r['id'] for r in allrows})==704
old={'104-92':'MDB 9736:3','168-97':'MDB 9736:4','536-00':'MDB 9736:7'}
assert all(next(r['comment'] for r in allrows if r['id']==i)==s for i,s in old.items())
rows=[r for r in allrows if r['id'] not in old and not r['lesion']]
assert len([r for r in rows if r['d']==EMC])==9
assert {r['id'] for r in rows}=={r['sample_id'] for r in hm['samples'] if r['eligible']}
hv={}
with (H/'source_data/tpm_matrix.tsv').open() as f:
    reader=csv.reader(f,delimiter='\t');header=next(reader)[1:];assert len(header)==len(set(header))==704 and set(header)==set(metadata)
    for v in reader:
        if v[0] in GENES:
            assert v[0] not in hv and len(v)==705;hv[v[0]]={k:Decimal(x) for k,x in zip(header,v[1:])}
assert set(hv)==set(GENES)
selected=load(W/'results/selected-values.json')
assert all(all(float(v)==selected[g][i] for i,v in vals.items()) for g,vals in hv.items())
counts['source_Hofvander_values']=12*704

# Original annotation, not the worker's extracted mapping: require exactly one row and no alternative gene.
csv.field_size_limit(2000000);mapping=collections.defaultdict(list)
with (A/'GPL6244-original-annotation.tsv').open(encoding='utf-8-sig') as f:
    for row in csv.DictReader(f,delimiter='\t'):
        syms={part.split(' // ')[1].strip() for part in row['gene_assignment'].split(' /// ') if len(part.split(' // '))>1}
        for g in syms.intersection(GENES):
            assert syms=={g};mapping[g].append(row['ID'])
assert all(len(mapping[g])==1 for g in GENES)
assert {g:ids[0] for g,ids in mapping.items()}==am['gene_to_probe']
rev={ids[0]:g for g,ids in mapping.items()};av={g:{} for g in GENES};rawmeta={};sample=None;table=False
with gzip.open(A/'GSE24369.soft.gz','rt',encoding='utf-8') as f:
    for line in f:
        line=line.rstrip('\r\n')
        if line.startswith('^SAMPLE = '):sample=line.partition(' = ')[2];rawmeta[sample]=collections.defaultdict(list);table=False
        elif line=='!sample_table_begin':table=True;cols=None
        elif line=='!sample_table_end':table=False
        elif table:
            r=line.split('\t')
            if cols is None:cols={v:i for i,v in enumerate(r)}
            elif r[cols['ID_REF']] in rev:
                g=rev[r[cols['ID_REF']]];assert sample not in av[g];av[g][sample]=Decimal(r[cols['VALUE']])
        elif sample and line.startswith('!Sample_'):
            k,sep,v=line.partition(' = ')
            if sep:rawmeta[sample][k].append(v)
assert len(rawmeta)==42 and all(set(v)==set(rawmeta) for v in av.values())
arrayrows=[]
for sid,m in rawmeta.items():
    t=m['!Sample_title'][0].lower()
    if 'extraskeletal' in t:d=EMC
    elif 'low' in t and 'fibromyxoid' in t:d='Low-grade fibromyxoid sarcoma'
    elif 'myxofibrosarcoma' in t:d='Myxofibrosarcoma'
    elif 'desmoid' in t:d='Desmoid'
    elif 'solitary' in t:d='Solitary fibrous tumor'
    elif 'muscle' in t:d='pooled_normal'
    else:raise AssertionError((sid,t))
    arrayrows.append({'id':sid,'d':d,'year':'unknown'})
expected={EMC:6,'Low-grade fibromyxoid sarcoma':17,'Myxofibrosarcoma':6,'Desmoid':6,'Solitary fibrous tumor':5,'pooled_normal':2}
assert dict(collections.Counter(r['d'] for r in arrayrows))==expected
for r in arrayrows:
    wr=next(v for v in am['array_samples'] if v['sample_id']==r['id'])
    if r['d']!='pooled_normal':assert r['d']==wr['diagnosis'];assert 'sample type: tumor biopsy' in rawmeta[r['id']]['!Sample_characteristics_ch1']
assert all(all(float(v)==load(W/'replication-results/array-values.json')[g][i] for i,v in vs.items()) for g,vs in av.items())
counts['source_array_values']=12*42
decision_results={};anchors={}
for g in GENES:
    published=hr['genes'][g];stats,ss=verify_ev(published['primary'],rows,hv[g],g+'/primary')
    verify_ev(published['context'],rows,hv[g],g+'/context')
    robust=True
    for kind,deletions in published['deletions'].items():
        for deletion in deletions:
            key=deletion['deleted']
            rr=[r for r in rows if r['year']!=key] if kind=='year' else [r for r in rows if r['id']!=key]
            _,s=verify_ev(deletion,rr,hv[g],g+'/delete/'+kind+'/'+key)
            if kind in ['emc','histology']:robust &= all(v is not None and v>Fraction(1,2) for v in s.values())
    gate=ss['marginal']>=Fraction(7,10) and all(stats[h][m] is not None and stats[h][m]>Fraction(1,2) for h in PRIMARY for m in ['marginal','matched']) and robust
    if g!='CHRNA6':assert gate==published['allocation_rule']['consistent_RNA_rationale'];decision_results[g]=bool(gate)
    revised=[dict(r,d=r['revised'] or r['d']) for r in rows]
    verify_ev(published['revised_diagnosis_sensitivity'],revised,hv[g],g+'/revised')
    anchors[g]={}
    for h,p in ar['genes'][g]['contrasts'].items():
        e=[r['id'] for r in arrayrows if r['d']==EMC];c=[r['id'] for r in arrayrows if r['d']==h]
        ap=prob(e,c,av[g]);check(p['array']['A'],ap,g+'/array/'+h)
        check(p['array']['pairs'],len(e)*len(c),g+'/array/pairs')
        for typ,dels in p['array']['deletions'].items():
            for d in dels:check(d['A'],prob([i for i in e if i!=d['deleted']],[i for i in c if i!=d['deleted']],av[g]),g+'/array/delete')
        for d in p['array']['placements']:check(d['A'],prob([d['sample_id']],c,av[g]),g+'/array/place')
        _,hs=verify_ev(p['hofvander'],rows,hv[g],g+'/shared/'+h)
        for typ,dels in p['hofvander_deletions'].items():
            for d in dels:verify_ev(d,[r for r in rows if r['id']!=d['deleted']],hv[g],g+'/shared/delete')
        sign=lambda v:None if v is None else 'positive' if v>Fraction(1,2) else 'negative' if v<Fraction(1,2) else 'neutral'
        assert p['directions']=={'array_marginal':sign(ap),'hofvander_marginal':sign(hs['marginal']),'hofvander_matched':sign(hs['matched'])}
        anchors[g][h]={'array':float(ap),'hofvander':{k:float(v) if v is not None else None for k,v in hs.items()},'directions':p['directions']}
assert [g for g,v in decision_results.items() if v]==hr['passing_address_genes']
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker_code_imported':False,'arithmetic':'Independent Decimal source parsing and Fraction pair counts; rank lookup by bisect, tolerance1e-12 only for comparison to serialized binary64 results.','counts':dict(counts),'discrepancies':discrepancies,'allocation':decision_results,'anchors':anchors,'raw_source_patient_counts':expected,'input_result_hashes':{str(p):sha(p) for p in [W/'results/result.json',W/'replication-results/result.json']},'terminal_statuses':[load(W/'results/execution.json'),load(W/'replication-results/execution.json')]}
(OUT/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'counts':dict(counts),'discrepancies':len(discrepancies),'allocation':decision_results,'LGFMS':{g:v['Low-grade fibromyxoid sarcoma'] for g,v in anchors.items()}},indent=2))
assert not discrepancies
