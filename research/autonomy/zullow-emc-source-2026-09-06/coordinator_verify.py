"""Independently verify original source bytes, complete metadata and literal methods.

No expression files are loaded or downloaded.
"""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import json
import re
from html.parser import HTMLParser

P=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class Reader(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self,data): self.parts.append(data)
def text(name):
    reader=Reader();reader.feed((P/name).read_text(encoding='utf-8'))
    return ' '.join(' '.join(reader.parts).split())

manifest=json.loads((P/'manifest.json').read_text())
for item in manifest:
    assert sha(P/item['file'])==item['sha256']
    assert (P/item['file']).stat().st_size==item['bytes']
retrievals=[json.loads(line) for line in (P/'retrievals.jsonl').read_text().splitlines()]
successful=[r for r in retrievals if 'sha256' in r]
for r in successful:
    assert sha(P/r['file'])==r['sha256'] and (P/r['file']).stat().st_size==r['bytes']
source=gzip.decompress((P/'GSE179720_family.soft.gz').read_bytes()).decode()
assert (P/'GSE179720_family.soft').read_text()==source
samples={}
for block in re.split(r'^\^SAMPLE = ',source,flags=re.M)[1:]:
    lines=block.splitlines();fields=collections.defaultdict(list)
    for line in lines[1:]:
        if line.startswith('!') and ' = ' in line:
            key,value=line.split(' = ',1);fields[key].append(value)
    samples[lines[0]]=dict(fields)
assert len(samples)==138
assert not re.search(r'\bEMC\b|chondrosarcoma|NR4A3',source,re.I)
with (P/'PRJNA744758-runs.tsv').open(encoding='utf-8',newline='') as f:
    ena=list(csv.DictReader(f,delimiter='\t'))
assert len(ena)==len({x['sample_accession'] for x in ena})==len({x['run_accession'] for x in ena})==138
ena_titles=collections.defaultdict(list)
for row in ena: ena_titles[row['sample_title']].append(row)
assert set(ena_titles)=={r['!Sample_title'][0] for r in samples.values()}
primary={k:r for k,r in samples.items() if r.get('!Sample_source_name_ch1')==['primary tumor']}
assert len(primary)==22 and all(r['!Sample_library_strategy']==['RNA-Seq'] for r in primary.values())
groups=collections.Counter()
with (P/'primary-RNA-crosswalk.tsv').open(encoding='utf-8',newline='') as f:
    crosswalk=list(csv.DictReader(f,delimiter='\t'))
assert len(crosswalk)==22 and {r['GSM'] for r in crosswalk}==set(primary)
for row in crosswalk:
    fields=primary[row['GSM']];title=fields['!Sample_title'][0]
    assert row['title']==title and row['characteristics']=='; '.join(fields['!Sample_characteristics_ch1'])
    expected='MLS' if 'cell line: MLPS Primary Tumor' in fields['!Sample_characteristics_ch1'] else 'Ewing'
    if expected=='Ewing': assert 'cell line: ES Primary Tumor' in fields['!Sample_characteristics_ch1']
    assert row['group_from_characteristics']==expected
    groups[expected]+=1
    runs=ena_titles[title]
    assert len(runs)==1 and row['ENA_runs']==runs[0]['run_accession']
    assert row['ENA_layout']==runs[0]['library_layout']=='SINGLE'
    assert row['ENA_instrument']==runs[0]['instrument_model']=='NextSeq 500'
    urls=[v for k,values in fields.items() if k.startswith('!Sample_supplementary_file') for v in values if 'ReadsPerGene' in v]
    assert row['processed_RNA_URL']=='; '.join(urls) and urls
assert groups=={'MLS':12,'Ewing':10}
article=text('article.html')
excerpts=json.loads((P/'methods-excerpts.json').read_text())
assert all(value in article for value in excerpts.values())
assert 'extraskeletal myxoid chondrosarcoma (n=7 for RNA-seq)' in excerpts['Human Subjects']
assert 'EMC and MLPS tumors sequenced in this study' in excerpts['Tumor RNA-seq Data Analysis']
assert 'were obtained from a previous study' in excerpts['Tumor RNA-seq Data Analysis']
assert 'NIHMS1790495-supplement-2.xlsx' in (P/'article.html').read_text()
assert not (P/'TableS1.xlsx').read_bytes().startswith(b'PK')
assert b'POW_CHALLENGE' in (P/'TableS1.xlsx').read_bytes()
mcbride=text('McBride2018.html')
assert 'GSE108028' in mcbride and 'EGAS00001002920' in mcbride
assert not re.search(r'\bEMC\b|chondrosarcoma',mcbride,re.I)
result={'status':'passed','manifest_sha256':sha(P/'manifest.json'),'frozen_files_checked':len(manifest),
        'original_retrieval_hashes_checked':len(successful),'GEO_samples':138,'ENA_samples_and_runs':138,
        'all_GEO_ENA_sample_titles_match':True,'primary_RNA_groups':dict(groups),'crosswalk_records_checked':22,
        'methods_excerpts_verified_in_original_HTML':len(excerpts),'TableS1_recovered':False,
        'scope':'Metadata and methods verified. No identified EMC measurement asset in inspected deposit; not universal absence.'}
(P/'coordinator-verification.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps(result,indent=2))
