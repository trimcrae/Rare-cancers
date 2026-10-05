#!/usr/bin/env python3
"""Zero-copy source-claim projection. No response quantities or figure images."""
from pathlib import Path
from lxml import etree
import json,re,hashlib
BASE=Path(__file__).resolve().parent
SRC=Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing/native_culture_fidelity_gate/raw/PMC9813045.xml')
EXPECTED='2998de01bf31d3b3793dd300b7856545168b40e569fbee4f200e53c394a0a657'
raw=SRC.read_bytes(); assert hashlib.sha256(raw).hexdigest()==EXPECTED
root=etree.fromstring(raw)
def txt(el): return ' '.join(' '.join(el.itertext()).split())
def mask(s):
    for a,b in [('USZ20','USZTWENTY'),('USZ22','USZTWENTYTWO')]: s=s.replace(a,b)
    s=re.sub(r'(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?', '[numeric masked]',s)
    return s.replace('USZTWENTYTWO','USZ22').replace('USZTWENTY','USZ20')
restricted=re.compile(r'\b(?:FAP|HLA|glycan|glycosylation|copy.number|structural.genom|chromosomal|STR|fusion.topology)\b',re.I)
selected=[]; skipped=[]
for i,p in enumerate(root.xpath('.//body/sec[@id="Sec14"]/p'),1):
    s=txt(p)
    if 'venetoclax' not in s.lower(): continue
    if restricted.search(s): skipped.append({'section':'Discussion','paragraph':i,'reason':'restricted-scope term: entire paragraph omitted'});continue
    sentences=re.split(r'(?<=[.!?])\s+',s)
    keep=[]
    for j,z in enumerate(sentences):
        if 'venetoclax' in z.lower():
            keep.extend(sentences[j:min(j+3,len(sentences))])
    selected.append({'section':'Discussion','paragraph':i,'numeric_masked_source_text':mask(' '.join(dict.fromkeys(keep)))})
for fig in root.xpath('.//fig[@id="Fig6"]'):
    s=txt(fig.find('caption'))
    if not restricted.search(s):selected.append({'section':'Figure caption text only','figure':'Fig6','numeric_masked_source_text':mask(s)})
obj={'primary':{'doi':'10.1007/s13577-022-00818-x','pmcid':'PMC9813045','cache_path':str(SRC),'bytes':len(raw),'sha256':EXPECTED},'read_scope':'Discussion venetoclax paragraphs and Figure6 textual caption; all response numbers masked before model inspection; no body figures/images/curves; no other drug outcome selection.','selected':selected,'omitted':skipped,'exposure_limit':'Initial numeric-masked Discussion paragraph projection also exposed other qualitative drug and model-description prose; final retained export narrows to venetoclax sentences and contiguous claim context. No quantities, restricted mechanism, or figure values were accepted.','new_network_calls':0,'new_original_bytes':0}
(BASE/'PUBLISHED-QUALITATIVE-CLAIMS.json').write_text(json.dumps(obj,indent=2)+'\n')
print(json.dumps(obj,indent=2))
