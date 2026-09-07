import csv, json, re, hashlib, subprocess, time, datetime
from pathlib import Path
from collections import Counter
from pypdf import PdfReader

t0=time.perf_counter()
W=Path('C:/Users/mcrae/.codex/worktrees/lee-sequence-assay-20260906/EMC-Research')
D=W/'research/autonomy/lee-sequence-assay-2026-09-06'
S=W/'research/autonomy/fusion-partial-benchmark-2026-09-05'
O=Path(__file__).parent
BASE='ac789abf1029d995c364d93a459f286595707568'
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def digest(b):return hashlib.sha256(b).hexdigest()
def positions(seq,query):return [m.start()+1 for m in re.finditer('(?='+query+')',seq)]
def reverse_complement(seq):return ''.join({'A':'T','T':'A','G':'C','C':'G'}[x] for x in reversed(seq))

manifest=json.loads((D/'output-manifest.json').read_text())
for entry in manifest:
    b=(D/entry['file']).read_bytes()
    check(len(b)==entry['bytes'] and digest(b)==entry['sha256'],'output integrity '+entry['file'])
for entry in json.loads((D/'retrievals.json').read_text()):
    if 'sha256' in entry:
        b=(D/'inputs'/entry['file']).read_bytes()
        check(len(b)==entry['bytes'] and digest(b)==entry['sha256'],'retrieved integrity '+entry['file'])
old_manifest=json.loads((S/'inputs/input-manifest.json').read_text())
for entry in old_manifest['sources']+old_manifest['members']:
    b=(S/'inputs'/entry['file']).read_bytes()
    check(len(b)==entry['bytes'] and digest(b)==entry['sha256'],'inherited source integrity '+entry['file'])
git='C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
for name in ['designs.csv','outcomes.csv','inputs/input-manifest.json','inputs/lee2023.xml']:
    raw=subprocess.check_output([git,'show',BASE+':research/autonomy/fusion-partial-benchmark-2026-09-05/'+name],cwd=W)
    # Git checkout can translate LF into CRLF; compare decoded record content.
    check(raw.replace(b'\r\n',b'\n')==(S/name).read_bytes().replace(b'\r\n',b'\n'),'immutable base content '+name)

refs={};exons={}
for p in (D/'inputs').glob('*.gb'):
    text=p.read_text();acc=re.search(r'^VERSION\s+(\S+)',text,re.M).group(1)
    origin=text.split('\nORIGIN')[1].split('//')[0]
    seq=''.join(''.join(line.split()[1:]) for line in origin.splitlines() if line.strip()).upper()
    check(len(seq)==int(re.search(r'^LOCUS\s+\S+\s+(\d+)',text,re.M).group(1)),acc+' length')
    refs[acc]=seq
    exons[acc]=[(a,b,str(i+1)) for i,(a,b) in enumerate(re.findall(r'^     exon\s+(\d+)\.\.(\d+)',text,re.M))]
check(('2270','2380','11') in exons['NM_058243.2'],'BRD4 exon11 annotation')
check(('483','1191','3') in exons['NM_001284292.2'],'NUTM1 exon3 annotation')
# Independently transcribed from visually inspected colored Fig2 and S6.
left='CTCTGACAGCGAAGACTCCGAAACAG';right='CATCTGCATTGCCGGGACCGGATATGAG'
ssleft='CCAGCAGAGGCCTTATGGATATGACCAG';ssright='ATCATGCCCAAGAAGCCAGCAGAGGAAGGAAA'
check(positions(refs['NM_058243.2'],left)==[2355],'Fig2 left unique2355..2380')
check(positions(refs['NM_001284292.2'],right)==[483],'Fig2 right unique483..510 (28nt)')
fusion=refs['NM_058243.2'][:2380]+refs['NM_001284292.2'][482:]
check(len(refs['NM_001284292.2'])==4109 and fusion[2354:2354+len(left+right)]==left+right,'fusion reconstruction')
fasta={x.split('\n',1)[0]:''.join(x.split('\n')[1:]) for x in (D/'references.fasta').read_text().split('>')[1:]}
check(fasta==dict(refs,B4N_reconstructed=fusion),'FASTA independently reconstructed')
designs=list(csv.DictReader((S/'designs.csv').open()))
outcomes=list(csv.DictReader((S/'outcomes.csv').open()))
rows=json.loads((D/'design-mappings-and-outcomes.json').read_text())
byid={r['design_id']:r for r in rows}
calc=[]
for d in designs:
    core=d['sense_5to3_printed'][:-2].replace('U','T');anti=d['antisense_5to3_printed'][:-2].replace('U','T')
    r=byid[d['design_id']]
    check(len(core)==19 and anti==reverse_complement(core),'19nt RC '+d['design_id'])
    seq,boundary=(fusion,2380) if d['target']=='B4N' else (ssleft+ssright,len(ssleft))
    hit=positions(seq,core)
    check(len(hit)==1 and hit[0]<=boundary<hit[0]+18,'unique crossing '+d['design_id'])
    l=boundary-hit[0]+1
    check((l,19-l)==(r['left_parent_nt'],r['right_parent_nt']),'split '+d['design_id'])
    if d['target']=='B4N':
        check(hit==r['fusion_full_start'],'fusion coordinate '+d['design_id'])
        check(all(not positions(v,core) and not positions(v,anti) for v in refs.values()),'no specified-parent 19nt matches '+d['design_id'])
    else:
        check(r['parent_matches'] is None and r['fusion_full_start'] is None and 'unverified' in r['parent_reference_status'],'SS full verdict unverified '+d['design_id'])
    calc.append(dict(id=d['design_id'],start=hit[0],left_nt=l,right_nt=19-l))
flatten=[o for r in rows for o in r['outcomes']]
canon=lambda o:json.dumps(o,sort_keys=True)
check(len(flatten)==93 and Counter(map(canon,flatten))==Counter(map(canon,outcomes)),'all93 outcome records exact multiset equality')
for r in rows:check(all(o['design_id']==r['design_id'] for o in r['outcomes']),'correct join '+r['design_id'])
missing=[o for o in flatten if o['endpoint']=='second_parent']
check(len(missing)==31 and all(not o['relative_expression_mean'] for o in missing),'31 absent second-parent observations')

# S3 visual transcription, independently matched against PDF extraction.
primers={'wild_BRD4':('AAAAGGGAATAGTGCCGTGGAG','AGGAACTGACTTTGGTTGGTGG'),'wild_NUTM1':('CTTCCAGACAGCCACAGTTAGT','TCAGAAGTTGGTGGGAGAAAGG'),'BRD4_NUTM1':('GACAGCGAAGACTCCGAAAC','GCACTAGGTTTCATGCTCATATCC'),'wild_SS18':('GTAGATGCTTGATTGTTTTGGTCTC','GTGCTTTGTCTTCCCCTCAC'),'SS18_SSX1':('GTCCTCAGTATCCTAACTACCCACA','GGTGCAGTTGTTTCCCATCG')}
source=''.join(p.extract_text() for p in PdfReader(S/'inputs/crt-2022-910-Supplementary-Table-3.pdf').pages)
assays=json.loads((D/'primer-mappings.json').read_text());amps={}
for a in assays:
    f,r=primers[a['assay']]
    check(f in source and r in source and (f,r)==(a['forward_5to3'],a['reverse_5to3']),'S3 pair '+a['assay'])
    if a['templates'] is None:
        check('SS' in a['assay'] and 'unverified' in a['status'],'SS assay unverified '+a['assay']);continue
    amps[a['assay']]={}
    for t in a['templates']:
        seq=fasta[t['template']];fs=positions(seq,f);rs=positions(seq,reverse_complement(r))
        predictions=[dict(start=x,end=y+len(r)-1,length_bp=y+len(r)-x,sequence=seq[x-1:y+len(r)-1]) for x in fs for y in rs if x+len(f)<=y]
        check(fs==t['forward_sites_1based'] and rs==t['reverse_binding_sites_1based'] and predictions==t['exact_amplicons'],'independent PCR '+a['assay']+' '+t['template'])
        amps[a['assay']][t['template']]=[(x['start'],x['end'],x['length_bp']) for x in predictions]
check(amps['wild_BRD4']['NM_058243.2']==amps['wild_BRD4']['NM_058243.3']==[(4910,5023,114)],'BRD4114bp4910..5023')
check(amps['BRD4_NUTM1']['B4N_reconstructed']==[(2359,2423,65)],'fusion65bp2359..2423')
article=''.join(__import__('xml.etree.ElementTree',fromlist=['parse']).parse(S/'inputs/lee2023.xml').getroot().itertext())
check('NM_058243.2' in article and 'NM_001284292.2' in article and 'NM_058243.3' in source and 'NM_001284292.1' in source,'article-S3 accession discrepancy')
result={'status':'SUPPORTED','base':BASE,'writer_manifest_sha256':digest((D/'output-manifest.json').read_bytes()),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'calculation_elapsed_seconds':time.perf_counter()-t0,'checks':checks,'design_calculations':calc,'amplicons':amps,'B4N15_outcomes':byid['B4N_15']['outcomes'],'scope':'Bounded independent sequence/assay/input integrity and exact frozen outcome join. No writer script executed, no scientific packet edits, no whole-repo tests, no new retrieval.'}
(O/'independent-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','design_calculations','B4N15_outcomes']},indent=2))
print('Passed',len(checks),'checks')
