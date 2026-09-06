"""Derive source metadata only. Never reads expression measurements."""
import collections,csv,gzip,hashlib,json,pathlib,re
from html.parser import HTMLParser
P=pathlib.Path(__file__).parent
class Text(HTMLParser):
    def __init__(self): super().__init__();self.parts=[]
    def handle_data(self,d):self.parts.append(d)
def html_text(name):
    parser=Text();parser.feed((P/name).read_text(encoding='utf-8'))
    return ' '.join(' '.join(parser.parts).split())
s=gzip.decompress((P/'GSE179720_family.soft.gz').read_bytes()).decode()
(P/'GSE179720_family.soft').write_text(s,encoding='utf-8')
rows=[]
for block in s.split('^SAMPLE = ')[1:]:
    d=collections.defaultdict(list);d['accession']=[block.splitlines()[0]]
    for line in block.splitlines()[1:]:
        if line.startswith('!') and ' = ' in line:
            k,v=line.split(' = ',1);d[k].append(v)
    rows.append(dict(d))
(P/'sample-metadata.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
ena=list(csv.DictReader((P/'PRJNA744758-runs.tsv').open(encoding='utf-8'),delimiter='\t'))
by_title=collections.defaultdict(list)
for r in ena:by_title[r['sample_title']].append(r)
fields=['GSM','title','sample_label','specimen_string_from_title','date_string_from_title','group_from_characteristics','characteristics','platform','BioSample','SRA_relation','ENA_runs','ENA_layout','ENA_instrument','processed_RNA_URL']
cross=[]
for r in rows:
    if 'primary tumor' not in r.get('!Sample_source_name_ch1',[]):continue
    title=r['!Sample_title'][0];match=re.fullmatch(r'(\d+)_(MLPS\d+|ES\d+)_RNA_primary_(.+?)(?:_S\d+_R1_001)?',title)
    assert match,title
    c='; '.join(r['!Sample_characteristics_ch1']);e=by_title[title]
    cross.append(dict(zip(fields,[r['accession'][0],title,match[2],match[3],match[1],'MLS' if 'MLPS Primary Tumor' in c else 'Ewing',c,r['!Sample_platform_id'][0],'; '.join(x for x in r.get('!Sample_relation',[]) if x.startswith('BioSample:')),'; '.join(x for x in r.get('!Sample_relation',[]) if x.startswith('SRA:')),'; '.join(x['run_accession'] for x in e),'; '.join(sorted(set(x['library_layout'] for x in e))),'; '.join(sorted(set(x['instrument_model'] for x in e))),'; '.join(v for k,vals in r.items() if k.startswith('!Sample_supplementary_file') for v in vals if 'ReadsPerGene' in v)])))
with (P/'primary-RNA-crosswalk.tsv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(cross)
t=html_text('article.html');(P/'article-text.txt').write_text(t,encoding='utf-8')
sections={}
for start,end in [('Human Subjects','Cell lines'),('RNA Isolation from Tumor Samples','Immunohistochemistry'),('Tumor RNA-seq Data Analysis','QUANTIFICATION AND STATISTICAL ANALYSIS'),('Data and Code Availability','KEY RESOURCES TABLE')]:
    i=t.index(start);j=t.find(end,i+len(start));sections[start]=t[i:j if j>=0 else i+3500]
(P/'methods-excerpts.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2),encoding='utf-8')
checks={'GEO_samples':len(rows),'GEO_assays':dict(collections.Counter(r['!Sample_library_strategy'][0] for r in rows)),'primary_RNA_groups':dict(collections.Counter(r['group_from_characteristics'] for r in cross)),'EMC_NR4A3_chondrosarcoma_match_anywhere_in_SOFT':bool(re.search(r'\bEMC\b|chondrosarcoma|NR4A3',s,re.I)),'ENA_runs':len(ena),'ENA_unique_samples':len(set(r['sample_accession'] for r in ena)),'all_primary_titles_match_ENA':all(by_title[r['title']] for r in cross),'TableS1_response_is_ZIP':(P/'TableS1.xlsx').read_bytes()[:2]==b'PK','TableS1_response_contains_POW_CHALLENGE':b'POW_CHALLENGE' in (P/'TableS1.xlsx').read_bytes()}
assert checks['GEO_samples']==138 and checks['primary_RNA_groups']=={'MLS':12,'Ewing':10}
assert not checks['EMC_NR4A3_chondrosarcoma_match_anywhere_in_SOFT']
assert checks['all_primary_titles_match_ENA'] and not checks['TableS1_response_is_ZIP']
checks['successful_retrieval_hashes_verified']=0
for line in (P/'retrievals.jsonl').read_text().splitlines():
    r=json.loads(line)
    if 'sha256' in r:
        assert hashlib.sha256((P/r['file']).read_bytes()).hexdigest()==r['sha256'];checks['successful_retrieval_hashes_verified']+=1
(P/'checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8');print(json.dumps(checks,indent=2))
