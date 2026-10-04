"""Reproduce explicit CEL specimen IDs and source-defined fusion context."""
import sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'.cache/python-deps'))
import csv,gzip,hashlib,io,json,re,statistics,urllib.request
import openpyxl

def main():
    R=ROOT/'research/autonomy'; E='Extraskeletal myxoid chondrosarcoma'; O='Ossifying fibromyxoid tumor'
    H=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
    P=BASE/'cel-headers.json'
    S1=R/'atlas-hofvander-source-2026-09-06/ccr-25-3740_supplementary_table_s1_suppts1.xlsx'
    M=R/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
    T=R/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
    sha=lambda b:hashlib.sha256(b).hexdigest()
    receipts={str(p.relative_to(ROOT)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in [P,S1,M,T]}
    def fetch_excel(filename,expected):
        url='https://pmc-oa-opendata.s3.amazonaws.com/PMC13133608.1/'+filename
        with urllib.request.urlopen(url,timeout=30) as response:b=response.read(15_000_001)
        assert len(b)<=15_000_000 and sha(b)==expected
        receipts[url]={'bytes':len(b),'sha256':sha(b)}
        return list(openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True).active.values)
    s1rows=list(openpyxl.load_workbook(S1,read_only=True,data_only=True).active.values)
    allrows={r[0].split('_')[0]:r for r in s1rows[2:706]};assert len(allrows)==704
    m=json.loads(M.read_text())['samples']
    emc=[r for r in m if r['eligible'] and r['diagnosis']==E];assert len(emc)==9
    ofmt=[r for r in m if r['eligible'] and r['diagnosis']==O];assert len(ofmt)==8
    def parameters(h):
        for k,v in h['parameters'].items():yield k,v.get('decoded')
        for parent in h['parents']:yield from parameters(parent)
    crosswalk=[]
    for a in json.loads(P.read_text())['arrays'][:6]:
        d=dict(parameters(a['header']));name=d['affymetrix-fusion-experiment-name']
        specimen=re.fullmatch(r'EMC\s+(\S+)',name).group(1)
        assert d['affymetrix-partial-dat-header'].strip().startswith(name+':')
        crosswalk.append({'GSM':a['accession'],'experiment_name':name,'specimen':specimen,
                          'in_full_704':specimen in allrows,'in_eligible_9':specimen in {r['sample_id'] for r in emc},
                          'DAT_header_repeats_name':True,'header_bytes':a['header_bytes'],'header_sha256':a['sha256'],'source_url':a['url']})
    s3=fetch_excel('ccr-25-3740_supplementary_table_s3_suppts3.xlsx','9fc0cfa2ad56e1cf44214f0a2835e0e6ba6fb0c1004341ae38981fe05671f94e')
    s4=fetch_excel('ccr-25-3740_supplementary_table_s4_suppts4.xlsx','3b27443c5d926ced78a36d7e64ec34987606a44d81cf2aea65f5d51ed965cce7')
    fusion={}
    for rownum,r in enumerate(s3,1):
        if len(r)>1 and r[1]==E:
            sid=r[0].split('_')[0];assert sid not in fusion
            fusion[sid]={'S3_row':rownum,'gene1':r[2],'gene2':r[3],'confidence':r[18],
                         'reading_frame':r[19],'support':r[20],'previously_reported':r[21],'comment':r[22]}
    aggregate=[{'S4_row':i,'cells':[v for v in r if v is not None]} for i,r in enumerate(s4,1) if r and r[0]==E]
    assert len(aggregate)==1
    missing=sorted(set(k for k,v in allrows.items() if v[1]==E)-set(fusion))
    direct=[r for r in emc if r['sample_id'] in fusion and 'NR4A3' in [fusion[r['sample_id']]['gene1'],fusion[r['sample_id']]['gene2']]]
    assert len(direct)==7
    with gzip.open(T,'rt') as f:
        reader=csv.reader(f,delimiter='\t');head=next(reader)[1:];v={}
        for row in reader:
            if row[0] in ['TMEM266','CHRNA6']:v[row[0]]=dict(zip(head,map(float,row[1:])))
    assert set(v)=={'TMEM266','CHRNA6'}
    def values(g,rr):return [v[g][r['sample_id']] for r in rr]
    def A(a,b):return sum((x>y)+.5*(x==y) for x in a for y in b)/(len(a)*len(b))
    individual=[]
    for r in emc:
        sid=r['sample_id'];raw=allrows[sid]
        individual.append({'sample':sid,'TMEM266_TPM':v['TMEM266'][sid],'CHRNA6_TPM':v['CHRNA6'][sid],
                           'S1_fusion':raw[13],'direct_NR4A3_subset':r in direct,'fusion':fusion.get(sid),
                           'fusion_note':'Absent S3; S4 uniquely unassigned TAF15::NR4A3 is indirect, not specimen-linked RT-PCR evidence' if sid in missing else None})
    comparisons={}
    for gene in ['TMEM266','CHRNA6']:
        comparisons[gene]={}
        for label,rr in [('pathology_9',emc),('direct_S3_NR4A3_7',direct)]:
            a=values(gene,rr);c={}
            for hist in [O]+H:
                br=[r for r in m if r['eligible'] and r['diagnosis']==hist];b=values(gene,br)
                c[hist]={'n':len(b),'median':statistics.median(b),'range':[min(b),max(b)],'A':A(a,b)}
            comparisons[gene][label]={'n':len(a),'median':statistics.median(a),'range':[min(a),max(a)],'comparisons':c}
    out={'scope':'Exploratory descriptive follow-up; no identifier-suffix dates, thresholds, classifier, subtype tests or regulation claims. Subset A=1 is inherited, not new validation. Distinct specimen names do not exclude undocumented patient aliases.',
         'crosswalk':crosswalk,'all_9_EMC':individual,
         'OFMT':[{'sample':r['sample_id'],'TMEM266_TPM':v['TMEM266'][r['sample_id']],'CHRNA6_TPM':v['CHRNA6'][r['sample_id']]} for r in ofmt],
         'S4_aggregate':aggregate,'S1_EMC_missing_S3':missing,'comparisons':comparisons,'receipts':receipts}
    (BASE/'cohort-context.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'header_ids':[q['specimen'] for q in crosswalk],
                      'eligible_overlap':sum(q['in_eligible_9'] for q in crosswalk),
                      'direct_NR4A3':comparisons['TMEM266']['direct_S3_NR4A3_7']}))

if __name__=='__main__':main()
