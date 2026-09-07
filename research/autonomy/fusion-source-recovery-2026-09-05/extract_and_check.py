from pathlib import Path
import json,sys,hashlib,struct,zipfile,xml.etree.ElementTree as ET
from datetime import datetime,timezone
p=Path(__file__).parent
sys.path.insert(0,str(p/'sources/xlrd-2.0.2-py2.py3-none-any.whl'))
import xlrd,openpyxl
from xlrd.compdoc import CompDoc
from PIL import Image
# Reproducible XLS cells and embedded PNG, preserving the source bytes unchanged.
x=p/'sources/10549_2014_3019_MOESM1_ESM.xls';w=xlrd.open_workbook(x)
a=[{'sheet':s.name,'rows':[s.row_values(i) for i in range(s.nrows)]} for s in w.sheets()]
(p/'varley-supplement-cells.json').write_text(json.dumps(a,indent=2)+'\n',encoding='utf8')
b=CompDoc(x.read_bytes()).get_named_stream('Workbook');pos=0;records=[]
while pos+4<=len(b):
 typ,n=struct.unpack_from('<HH',b,pos);records.append((typ,b[pos+4:pos+4+n]));pos+=4+n
joined=b''.join(v for t,v in records if t in [0xeb,0xec,0x3c]);i=joined.find(b'\x89PNG\r\n\x1a\n');j=joined.find(b'IEND',i)+8
assert i>=0 and j>i
(p/'sources/varley-supp-figure1.png').write_bytes(joined[i:j]);Image.open(p/'sources/varley-supp-figure1.png').verify()
w2=openpyxl.load_workbook(p/'sources/ctsd2026-table2.xlsx',read_only=True,data_only=True)
a2=[{'sheet':s.title,'rows':list(s.values)} for s in w2]
(p/'ctsd2026-table2-cells.json').write_text(json.dumps(a2,indent=2)+'\n',encoding='utf8')
checks={'varley_sheets':[(s.name,s.nrows,s.ncols) for s in w.sheets()], 'ctsd2026_sheet_rows':len(a2[0]['rows']), 'ctsd2026_core_matches_varley1':a2[0]['rows'][52][2].split('[')[0]=='ACUACACGCUCAAGGCCCA', 'ctsd2026_core_length':len(a2[0]['rows'][52][2].split('[')[0]), 'embedded_png_valid':True, 'original_varley_xml_matches_prior_manifest':hashlib.sha256((p/'sources/varley.xml').read_bytes()).hexdigest()=='e3671f2796e6649688733fbc53f2206ed19148de2dfab3fa73d1b07d195e8429'}
assert checks['ctsd2026_core_matches_varley1'] and checks['ctsd2026_core_length']==19 and checks['original_varley_xml_matches_prior_manifest']
(p/'checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8');print(json.dumps(checks))
