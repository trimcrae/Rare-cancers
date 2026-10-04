"""Independent XLSX-XML arithmetic verification, without openpyxl."""
import io,json,zipfile,xml.etree.ElementTree as E,statistics,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
results=json.loads((P/'ddr-results.json').read_text())
outer=zipfile.ZipFile(P/'planaspaz2023-publisher-fig5.zip')
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
checked=0
for c in results['all_same_assay_model_curves']:
 data=outer.read(c['source_member']) if c['source_member'].startswith('Fig5/') else (P/c['source_member']).read_bytes()
 z=zipfile.ZipFile(io.BytesIO(data))
 shared=[''.join(v.itertext()) for v in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
 cells={}
 for node in E.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:c',ns):
  v=node.find('m:v',ns)
  if v is None:continue
  cells[node.attrib['r']]=shared[int(v.text)] if node.attrib.get('t')=='s' else float(v.text)
 cols=[k[:-1] for k,v in cells.items() if k.endswith('1') and k.rstrip('0123456789')==k[:-1] and v==c['model']]
 assert len(cols)==1,cols
 def ci(col):
  n=0
  for x in col:n=n*26+ord(x)-64
  return n
 start=ci(cols[0])
 def cn(n):
  s=''
  while n:n,m=divmod(n-1,26);s=chr(65+m)+s
  return s
 for point in c['points']:
  row=point['excel_row'];values=[cells.get(cn(j)+str(row)) for j in range(start,start+3)];values=[x for x in values if isinstance(x,(float,int))]
  assert values==point['reported_replicate_values']
  assert abs(statistics.mean(values)-point['mean'])<1e-12
  assert min(values)==point['min'] and max(values)==point['max']
  if 'dose_uM' in point:assert abs(10**cells['A'+str(row)]-point['dose_uM'])<1e-12
  checked+=1
out={'status':'pass','curves_checked':len(results['all_same_assay_model_curves']),'points_checked':checked,'independent_EMC_models':1,'method':'Raw OOXML cells versus openpyxl extraction, all concentrations and all model means/ranges. This verifies arithmetic, not novelty or biological validity.','results_sha256':hashlib.sha256((P/'ddr-results.json').read_bytes()).hexdigest()}
(P/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
