"""Independent selected-scalar bootstrap using multinomial stratum weights."""
import pathlib,csv,json,collections,numpy as np,openpyxl
P=pathlib.Path(__file__).parent
S=pathlib.Path('C:/Users/mcrae/.codex/worktrees/8010/EMC-Research/.cache/emc-atlas-new-source-20260906')
W=pathlib.Path('C:/Users/mcrae/.codex/worktrees/atlas-hofvander-validation-20260906/EMC-Research/research/autonomy/atlas-hofvander-validation-2026-09-06')
E='Extraskeletal myxoid chondrosarcoma';HS=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
meta={r['lab_no']:r for r in csv.DictReader((S/'source_data/meta_data.txt').open(),delimiter='\t')};rows=[]
sheet=openpyxl.load_workbook(S/'ccr-25-3740_supplementary_table_s1_suppts1.xlsx',read_only=True,data_only=True).active
for r in sheet.iter_rows(min_row=3,values_only=True):
    i=str(r[0] or '').split('_')[0]
    if i in meta and i not in ['104-92','168-97','536-00'] and not r[12] and r[1] in [E]+HS:rows.append((i,r[1],meta[i]['sequencing_year']))
with (S/'source_data/tpm_matrix.tsv').open() as f:
    rd=csv.reader(f,delimiter='\t');ids=next(rd)[1:]
    for r in rd:
        if r[0]=='CSPG4':v=dict(zip(ids,map(float,r[1:])));break
B=5000;rng=np.random.default_rng(931704);weights=np.zeros((B,len(rows)),dtype=int);strata=collections.defaultdict(list)
for i,(_,h,y) in enumerate(rows):strata[(h,y)].append(i)
for ix in strata.values():weights[:,ix]=rng.multinomial(len(ix),[1/len(ix)]*len(ix),size=B)
def calc(e,c):
    a=np.array([v[rows[i][0]] for i in e]);b=np.array([v[rows[i][0]] for i in c]);pair=(a[:,None]>b).astype(float)+.5*(a[:,None]==b)
    return np.einsum('bi,ij,bj->b',weights[:,e],pair,weights[:,c])/(len(e)*len(c))
mar=[];mat=[]
for h in HS:
    e=[i for i,r in enumerate(rows) if r[1]==E];c=[i for i,r in enumerate(rows) if r[1]==h];mar.append(calc(e,c));components=[];ns=[]
    for y in sorted({r[2] for r in rows}):
        ee=[i for i in e if rows[i][2]==y];cc=[i for i in c if rows[i][2]==y]
        if ee and cc:components.append(calc(ee,cc));ns.append(len(ee))
    mat.append(np.average(components,axis=0,weights=ns))
ind={k:np.percentile(np.mean(z,axis=0),[2.5,97.5]).tolist() for k,z in [('marginal',mar),('matched',mat)]}
published=json.loads((W/'results/CSPG4.json').read_text())['bootstrap_pointwise_conditional_95']['summary']
out={'gene':'CSPG4','method':'Independent5000 multinomial stratum-weight draws; shared EMC weights across all contrasts, different RNG seed931704; not bit-identical rerun.','independent_intervals':ind,'writer_intervals':published,'endpoint_absolute_differences':{k:[abs(a-b) for a,b in zip(ind[k],published[k])] for k in ind},'limitation':'Conditional fixed sparse strata; no correction for unknown batches/purity or eleven-gene multiplicity.'}
(P/'bootstrap-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
