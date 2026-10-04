"""Bounded retrieval of existing public BLAST jobs; never resubmits them.
Wait >=60s between pending checks of a RID and >=10s between requests.
Remote jobs expire; CONFIG, query construction and hashes allow later replay.
"""
import urllib.request,urllib.parse,hashlib,json,re,collections,csv,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
CONFIG={'PROGRAM':'blastn','ENTREZ_QUERY':'txid9606[ORGN]','WORD_SIZE':'7','FILTER':'F','EXPECT':'1000','NUCL_REWARD':'1','NUCL_PENALTY':'-3','GAPCOSTS':'5 2','HITLIST_SIZE':'1000','SHORT_QUERY_ADJUST':'false'}
JOBS={'probe_RNA':{'rid':'C4DC9SDK014','database':'refseq_rna','query_sha256':'90f2051f25527a90d0996abed2c5c1f006013ea0fa9c0bbc01602415b972a7e2'},'probe_genomic':{'rid':'C4DCYTNP014','database':'refseq_genomic','query_sha256':'90f2051f25527a90d0996abed2c5c1f006013ea0fa9c0bbc01602415b972a7e2'},'observed_RNA':{'rid':'C4EVZZYR016','database':'refseq_rna','query_sha256':'56c8c0af432670a53875820fa78652c0d7357db8ae98f6089741f884d0ead572'}}

def queries(which):
    if which.startswith('probe_'):
        with (BASE.parent/'tmem266-prepublication-2026-10-03/probe-map.csv').open() as f:
            pairs=[(r['physical_probe_id'],r['sequence']) for r in csv.DictReader(f)]
        pairs.append(('TempO_TMEM266_14670','GTGGTGACCATACACACAGCTGGCTCTGGGACACCGCTGTCACTGCTGGG'))
    else:
        reads=json.loads((BASE/'usz-selected-reads.json').read_text())['reads']
        pairs=[('alternative_anchor40','AGAGAGCAGCCGTGTGGCAGTTTCCAGCGCATTCCAGTTT')]+[(f"observed_mate{r['mate']}",r['sequence']) for r in reads]
    s=''.join('>'+k+'\n'+v+'\n' for k,v in pairs)
    assert hashlib.sha256(s.encode()).hexdigest()==JOBS[which]['query_sha256']
    return s

def retrieve(which):
    job=JOBS[which];query=queries(which)
    p={'CMD':'Get','RID':job['rid'],'FORMAT_TYPE':'Text','ALIGNMENT_VIEW':'Tabular','DESCRIPTIONS':1000,'ALIGNMENTS':1000}
    url='https://blast.ncbi.nlm.nih.gov/Blast.cgi?'+urllib.parse.urlencode(p)
    with urllib.request.urlopen(url,timeout=45) as h:b=h.read(15000001)
    assert len(b)<=15000000,'output cap exceeded'
    s=b.decode();rr=collections.defaultdict(list)
    for line in s.splitlines():
        t=line.split('\t')
        if len(t)==12:rr[t[0]].append(t)
    out={'url':url,**job,'config':CONFIG,'query_fasta':query,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'status':re.findall(r'Status\s*=\s*\w+',s),'rows':[]}
    for q,hs in rr.items():
        n=40 if q=='alternative_anchor40' else 151 if q.startswith('observed_') else 50 if q=='TempO_TMEM266_14670' else 25
        exact=[t for t in hs if int(t[3])==n and int(t[4])==0 and int(t[5])==0 and int(t[6])==1 and int(t[7])==n]
        near=[t for t in hs if int(t[5])==0 and int(t[4])+n-(int(t[7])-int(t[6])+1)<=2]
        intended={'NM_152335','XM_005254160','XM_017021915','XM_047432151','XM_054377283','XM_054377284','XM_054377285'}
        partial=[t for t in hs if t[1].split('.')[0] in intended and t not in near]
        out['rows'].append({'query':q,'query_length':n,'reported_subjects':len(set(t[1] for t in hs)),'reported_HSPs':len(hs),'hit_limit_reached':len(set(t[1] for t in hs))>=1000,'exact_HSPs':exact,'near_or_terminal_flank_candidates':near,'other_TMEm266_partial_HSPs':partial})
    out['limits']='Short local alignments, hit limits, annotation/database versions and incomplete terminal-flank checks prevent exhaustive experimental specificity conclusions.'
    return out

if __name__=='__main__':
    name=sys.argv[1];out=retrieve(name)
    (BASE/('blast-'+name+'.json')).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'job':name,'status':out['status'],'queries_returned':len(out['rows']),'response_bytes':out['bytes']}))
