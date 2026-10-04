"""Independent reference-path check of selected reads, not a variant call."""
import urllib.request as u,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
p=BASE/'usz-selected-reads.json';raw=p.read_bytes();x=json.loads(raw)
assert hashlib.sha256(raw).hexdigest()=='0918f3402eb7fc34d3e4f0f02c6694064082a6d1fecc18e24b067bb33fad0b21'
a=76137832;b=76169870
u1=f'https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chr15;start={a};end={b}'
u2=f'https://rest.ensembl.org/sequence/region/human/15:{a+1}..{b}:1?content-type=text/plain'
with u.urlopen(u1,timeout=40) as r:r1=r.read(100000)
with u.urlopen(u2,timeout=40) as r:r2=r.read(100000)
s1=json.loads(r1)['dna'].upper();s2=r2.decode().strip().upper()
assert s1==s2 and len(s1)==32038
assert hashlib.sha256(s1.encode()).hexdigest()=='93642a752ae8385f12bd45b7067f755e923203846d50b07135a00a5fa9200acd'
blocks={1:[(76137832,76137895),(76156603,76156652),(76160094,76160133)],2:[(76156630,76156652),(76160094,76160168),(76169815,76169870)]}
anchor='AGAGAGCAGCCGTGTGGCAGTTTCCAGCGCATTCCAGTTT';oriented={};ids=set();results=[]
for r in x['reads']:
    m=r['mate'];q=r['sequence'];qual=r['quality_ascii']*r['quality_repeat'];ids.add(r['header'].split()[0])
    if r['orientation']=='-':q=q.translate(str.maketrans('ACGT','TGCA'))[::-1];qual=qual[::-1]
    oriented[m]=q;assert len(q)==len(qual)==151
    ref=''.join(s1[c-a:d-a] for c,d in blocks[m]);gp=[i for c,d in blocks[m] for i in range(c,d)]
    mm=[(i,gp[i],v,w) for i,(v,w) in enumerate(zip(q,ref)) if v!=w]
    at=q.index(anchor);assert at==r['anchor_start_in_oriented_read0'];assert min(ord(c)-33 for c in qual[at:at+40])==40
    assert not [i for i,*_ in mm if at<=i<at+40]
    assert mm==([] if m==1 else [(109,76169828,'C','T')])
    assert q not in s1 and anchor not in s1
    results.append({'mate':m,'blocks_hg38_0based_half_open':blocks[m],'reference_matches':151-len(mm),'anchor_start0':at,'anchor_minimum_Phred':40,'mismatches_index0_genome0_read_ref':mm})
assert len(ids)==1 and oriented[1][90:]==oriented[2][:61]
assert s1[76156652-a:76156654-a]=='GT' and s1[76160092-a:76160094-a]=='AG'
out={'status':'passed','selected_reads_sha256':hashlib.sha256(raw).hexdigest(),
     'sources':[{'url':v,'bytes':len(w),'sha256':hashlib.sha256(w).hexdigest()} for v,w in [(u1,r1),(u2,r2)]],
     'matching_reference_sequence_sha256':hashlib.sha256(s1.encode()).hexdigest(),'results':results,
     'distinct_fragments':len(ids),'exact_overlap_nt':61,'alternative_intron_length':3442,'donor_acceptor':'GT/AG',
     'scope':'One local annotated splice-compatible fragment; read/reference difference is not a demonstrated variant; no abundance, full-length, protein or tissue localization inference'}
(BASE/'splice-read-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'distinct_fragments':len(ids),'results':results},indent=2))
