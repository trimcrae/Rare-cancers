"""Describe isoform ambiguity; these are not isoform abundance estimates."""
import hashlib
import json
from pathlib import Path
import urllib.request

BASE=Path(__file__).resolve().parent
data=json.loads((BASE/'culture-exon-coverage-results.json').read_text())
g026=json.loads((BASE/'culture-exon-annotation.json').read_text())
target_donor,target_acceptor=76202264,76203740
out={'scope':'Exon overlap/context, not isoform abundance or full-length evidence',
     'junction':{'chrom':'chr15','donor_end_0based':target_donor,
                 'acceptor_start_0based':target_acceptor},'G026':[],'current_ensembl':[]}

def row(name,exons,biotype=None,translation=None):
    has_junction=any(b==target_donor and c==target_acceptor
                     for (a,b),(c,d) in zip(exons,exons[1:]))
    coverages={}
    for run,values in data['runs'].items():
        intervals=[x for exon in values['exons'] for x in exon['coverage_segments']]
        coverages[run]=[sum(max(0,min(b,e)-max(a,s))*v for a,b,v in intervals)
                        for s,e in exons]
    return {'transcript':name,'biotype':biotype,'translation':translation,
            'exons_0based_halfopen':exons,'probe_junction_present':has_junction,
            'coverage_per_exon':coverages}

for t in g026['source_response']['wgEncodeGencodeCompV26']:
    if t['name2']=='TMEM266':
        exons=list(zip(map(int,t['exonStarts'].strip(',').split(',')),
                       map(int,t['exonEnds'].strip(',').split(','))))
        out['G026'].append(row(t['name'],exons))

url='https://rest.ensembl.org/lookup/id/ENSG00000169758?expand=1;content-type=application/json'
with urllib.request.urlopen(url,timeout=30) as r:
    raw=r.read(100001)
assert len(raw)<=100000
current=json.loads(raw)
out['current_source']={'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                       'assembly':current['assembly_name'],'gene_version':current['version']}
for t in current['Transcript']:
    exons=[(x['start']-1,x['end']) for x in t['Exon']]
    out['current_ensembl'].append(row(t['id']+'.'+str(t['version']),exons,
         t['biotype'],t.get('Translation')))
out['canonical_transcript']=current['canonical_transcript']
(BASE/'isoform-context-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'canonical':out['canonical_transcript'],
 'junction_present_in':[x['transcript'] for x in out['current_ensembl'] if x['probe_junction_present']]}))
