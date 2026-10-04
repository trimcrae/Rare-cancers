"""Independent reference-sequence and CDS classification of fixed array map."""
import csv
import hashlib
import json
from pathlib import Path
import urllib.request
BASE=Path(__file__).resolve().parent
rows=list(csv.DictReader((BASE/'probe-map.csv').open()))
receipts=[]
def get(url,cap):
    with urllib.request.urlopen(url,timeout=30) as r:b=r.read(cap+1)
    assert len(b)<=cap
    receipts.append({'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    return json.loads(b)
sequences={}
for assembly,start,end in [('hg19',76352177,76521462),('hg38',76059836,76229121)]:
    u=f'https://api.genome.ucsc.edu/getData/sequence?genome={assembly};chrom=chr15;start={start};end={end}'
    d=get(u,250000)
    sequences[assembly]=(start,d['dna'].upper())
t=get('https://rest.ensembl.org/lookup/id/ENST00000388942?expand=1;content-type=application/json',100000)
cds_start=t['Translation']['start']-1
cds_end=t['Translation']['end']
exons=[(e['start']-1,e['end']) for e in t['Exon']]
assert cds_start==76134287
verified=[]
for row in rows:
    probe=row['sequence']
    rc=probe.translate(str.maketrans('ACGT','TGCA'))[::-1]
    coordinates={}
    for assembly,(offset,seq) in sequences.items():
        assert seq.count(rc)==1,(row['physical_probe_id'],assembly)
        start=offset+seq.index(rc)
        coordinates[assembly]=[start,start+25]
    assert coordinates['hg19']==[int(row['hg19_start0']),int(row['hg19_end0'])]
    a,b=coordinates['hg38']
    eids=[i+1 for i,(s,e) in enumerate(exons) if max(s,a)<min(e,b)]
    assert len(eids)==1,(row['physical_probe_id'],a,b,exons)
    exonic_bases=sum(max(0,min(b,e)-max(a,s)) for s,e in exons)
    coding=max(0,min(b,cds_end)-max(a,cds_start))
    q=int(row['child_probeset'])
    primary=7985069<=q<=7985074
    verified.append(dict(row,coordinates=coordinates,canonical_exon=eids[0],current_exonic_bases=exonic_bases,
        current_coding_bases=coding,current_region_class=('CDS' if coding==25 else 'UTR' if coding==0 else 'mixed'),
        primary_upstream=primary,strict_upstream_coding=primary and coding==25))
strict=[int(x['physical_probe_id']) for x in verified if x['strict_upstream_coding']]
assert len(strict)==12
out={'scope':'Exact matches within TMEM266 locus; not genome-wide off-target or full-transcript validation',
     'reference_receipts':receipts,'current_transcript':t['id']+'.'+str(t['version']),
     'current_CDS_0based_halfopen':[cds_start,cds_end],'rows':verified,
     'strict_upstream_ids':strict,'all30_sequence_checks_pass':True}
(BASE/'probe-sequence-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'all30_pass':True,'strict_count':len(strict),
      'mixed_upstream':[x['physical_probe_id'] for x in verified if x['primary_upstream'] and x['current_region_class']=='mixed']}))
