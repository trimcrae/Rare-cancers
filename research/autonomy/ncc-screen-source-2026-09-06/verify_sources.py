"""Read original XLSX ZIP/XML independently of the source worker's spreadsheet library."""
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
EXPECTED={
 'NCC-MOESM4.xlsx':'8431b84591badcbf71af6a701758be4d046b5b4e1ecd40c3af74135297e81cdb',
 'NCC-MOESM5.xlsx':'c90a668b59b45b87aa9d250f6105180d5693f91505a4e1f11b0bf7af26c21ed9',
 'NCC-MOESM6.xlsx':'2fe320a6fc39a5a8dc21aa36830772caabb3e4d51c8fffb7dca132ca101cbd28'}

def read_sheet(path):
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        tree=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        result=[]
        for row in tree.findall('s:sheetData/s:row',NS):
            cells={}
            for cell in row.findall('s:c',NS):
                assert cell.find('s:f',NS) is None, 'Unexpected formula requires source review'
                col=re.sub(r'\d+','',cell.attrib['r'])
                node=cell.find('s:v',NS)
                if cell.attrib.get('t')=='s':value=strings[int(node.text)] if node is not None else None
                elif cell.attrib.get('t')=='inlineStr':value=''.join(cell.find('s:is',NS).itertext())
                elif node is None:value=None
                else:
                    try:value=float(node.text)
                    except ValueError:value=node.text
                cells[col]=value
            result.append((int(row.attrib['r']),cells))
        return result

def iscas(v):return isinstance(v,str) and re.fullmatch(r'\d+-\d+-\d+',v.strip()) is not None
def numeric(v):return isinstance(v,(int,float)) and math.isfinite(v)

def main():
    hashes={name:hashlib.sha256((HERE/'sources'/name).read_bytes()).hexdigest() for name in EXPECTED}
    assert hashes==EXPECTED
    cat=[(r,c) for r,c in read_sheet(HERE/'sources/NCC-MOESM4.xlsx') if iscas(c.get('B'))]
    screen=[(r,c) for r,c in read_sheet(HERE/'sources/NCC-MOESM5.xlsx') if iscas(c.get('A'))]
    ic50=[(r,c) for r,c in read_sheet(HERE/'sources/NCC-MOESM6.xlsx') if iscas(c.get('A'))]
    cats={c['B'].strip() for _,c in cat}; screens={c['A'].strip() for _,c in screen}; ics={c['A'].strip() for _,c in ic50}
    assert len(cat)==len(cats)==221 and len(screen)==len(screens)==221
    assert len(ic50)==len(ics)==24 and cats==screens and ics<=screens
    assert all(numeric(c.get('C')) and numeric(c.get('D')) and c['D']>=0 for _,c in screen)
    assert all(numeric(c.get('C')) and c['C']>0 for _,c in ic50)
    rows=[{'source_row':r,'cas':c['A'].strip(),'source_name':c['B'],'cell_viability_percent':c['C'],'reported_sd_percent':c['D']} for r,c in screen]
    with (HERE/'screen.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    rows_ic=[{'source_row':r,'cas':c['A'].strip(),'source_name':c['B'],'ic50_nM':c['C']} for r,c in ic50]
    with (HERE/'ic50.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows_ic[0]));w.writeheader();w.writerows(rows_ic)
    result={'status':'passed independent ZIP/XML extraction and identity/value checks','source_sha256':hashes,
      'catalogue_entries':len(cat),'unique_screen_drugs':len(screen),'screen_means_and_sd_complete':True,
      'ic50_entries':len(ic50),'catalogue_screen_cas_sets_equal':True,'all_ic50_cas_in_screen':True,
      'source_screen_range_percent':[min(c['C'] for _,c in screen),max(c['C'] for _,c in screen)],
      'source_means_ge_100_percent':sum(c['C']>=100 for _,c in screen),
      'source_means_ge_50_percent':sum(c['C']>=50 for _,c in screen),
      'biological_scope':'One NCC-EMC1-C1 patient-derived cell model; 221 drugs are not 221 independent biological specimens.',
      'uncertainty':'SD is reported by the source; replicate count and type not established by these workbooks.',
      'unresolved':['Screen concentrations and exposure duration','Normalization and control definition','Replicate count and experimental design','Dose-response range, fitting and censoring','Supplementary Table4 has24 IC50 rows while FigureS2 caption says21 agents; not reconciled'],
      'not_established':['Clinical efficacy or safety','Cross-model reproducibility','Mechanistic drug-target attribution','A new preprint contribution']}
    (HERE/'coordinator-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
