"""Historical cache-only source projection. No network, sequences, coordinates or counts.
This archival helper was preserved after source-stage closure; no new execution/results
were added then. It reproduces only fixed-source identifier fields for future authorized
metadata replay, not quantities or another scientific stage.
"""
from pathlib import Path
import hashlib,json,openpyxl

HWT=Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round8/microenvironment/raw/HWT2.0-manifest.xlsx')
IDS=Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round9/clinical_measurements/gpnmb_culture_identifier_capture/identifier-cache/ARCHS4.first-column-identifiers.txt')
assert hashlib.sha256(HWT.read_bytes()).hexdigest()=='0dcceee852b5ceec2807641b1c55b3f57e33ffa7687b584d4d4a3806d6752da0'
assert hashlib.sha256(IDS.read_bytes()).hexdigest()=='ce0cadc5ca2f21a7ecb4abc9aa031895080275acbc71a1bd739cf4c00b01f5fe'
wb=openpyxl.load_workbook(HWT,read_only=True,data_only=True)
ws=wb['Human WT 2.0 Manifest']
head=next(ws.iter_rows(min_row=1,max_row=1,min_col=2,max_col=4,values_only=True))
assert head==('Gene Symbol','Entrez ID','ENSEMBL Gene ID')
rows=[]
for source_row,x in enumerate(ws.iter_rows(min_row=2,min_col=2,max_col=4,values_only=True),2):
 if x[0]=='GPNMB':rows.append({'excel_row':source_row,**dict(zip(head,x))})
wb.close();assert len(rows)==1
symbol=rows[0]['Gene Symbol'];entrez=str(rows[0]['Entrez ID']);gene=rows[0]['ENSEMBL Gene ID']
selected=[]
for source_row,line in enumerate(IDS.open(),2):
 ident=line.rstrip('\r\n')
 if ident in (symbol,entrez,gene) or ident.startswith(gene+'.'):
  selected.append({'source_matrix_row':source_row,'identifier':ident,'kind':'unvalidatedversioncandidate' if ident.startswith(gene+'.') else 'exactsourceidentifier'})
print(json.dumps({'allowed_gene_identity_fields':rows,'matching_identifiers_only':selected,'numeric_fields_read':0,'no_expression_or_coverage_inference':True},indent=2))
