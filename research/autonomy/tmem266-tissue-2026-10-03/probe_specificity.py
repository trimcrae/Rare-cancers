"""Authenticate official v2.0 TMEM266 probe and its exact hg38 junction target.
Reads the 2.48 MB manufacturer workbook in memory; preserves only selected rows.
"""
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parents[2]/'.cache/python-deps'))
import openpyxl

def fetch(url,cap):
    with urllib.request.urlopen(url,timeout=40) as r:
        data=r.read(cap+1)
    assert len(data)<=cap
    return data,{'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

url='https://www.biospyder.com/s/190620HumanWholeTranscriptome20Manifest.xlsx'
data,receipt=fetch(url,2_600_000)
assert receipt['sha256']=='0dcceee852b5ceec2807641b1c55b3f57e33ffa7687b584d4d4a3806d6752da0'
book=openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=True)
selected=[]
headers={}
for ws in book.worksheets:
    for n,row in enumerate(ws.iter_rows(values_only=True),1):
        if n<=3:
            headers.setdefault(ws.title,[]).append(list(row))
        if any(str(v) in ('TMEM266','C15orf27','HVRP1','FLJ38190','ENSG00000169758')
               for v in row):
            selected.append({'sheet':ws.title,'row_number':n,'values':list(row)})
assert len(selected)==1
probe='GTGGTGACCATACACACAGCTGGCTCTGGGACACCGCTGTCACTGCTGGG'
assert probe in selected[0]['values'] and len(probe)==50
rc=probe.translate(str.maketrans('ACGT','TGCA'))[::-1]
regions=[(76202254,76202264),(76203740,76203780)]
sequences=[]
sequence_receipts=[]
for start,end in regions:
    u=f'https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chr15;start={start};end={end}'
    b,r=fetch(u,10000)
    seq=json.loads(b)['dna'].upper()
    assert len(seq)==end-start
    sequences.append(seq)
    sequence_receipts.append(r)
joined=''.join(sequences)
assert joined==rc
annotation=json.loads((BASE/'culture-exon-annotation.json').read_text())
canonical=[x for x in annotation['source_response']['wgEncodeGencodeCompV26']
           if x['name']=='ENST00000388942.7']
assert len(canonical)==1
t=canonical[0]
starts=list(map(int,t['exonStarts'].strip(',').split(',')))
ends=list(map(int,t['exonEnds'].strip(',').split(',')))
assert t['strand']=='+' and len(starts)==11
assert (starts[9],ends[9])==(76202201,76202264)
assert (starts[10],ends[10])==(76203740,76204963)
result={'manifest_receipt':receipt,'first_rows':headers,'selected_rows':selected,
        'probe_length_nt':len(probe),'probe_sequence':probe,'reverse_complement':rc,
        'reference':'hg38','coordinate_system':'0-based half-open',
        'matched_regions':regions,'reference_sequences':sequences,
        'sequence_receipts':sequence_receipts,'exact_spliced_target_match':True,
        'annotated_target':'ENST00000388942.7 exon10 last10nt + exon11 first40nt',
        'shared_antisense_exon_overlap_bp':0,
        'limitations':[
            'Article names assay v2.0 but exact batch/manifest revision is unreported.',
            'Design supports junction-targeting, not an independent assay-specificity experiment.',
            'Shared junction among isoforms cannot establish complete canonical coding transcript.',
            'No malignant-cell localization, protein detection, or therapeutic inference.']}
(BASE/'probe-specificity-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'selected_probes':len(selected),'length_nt':len(probe),
                  'exact_spliced_target_match':True,'target':result['annotated_target']}))
