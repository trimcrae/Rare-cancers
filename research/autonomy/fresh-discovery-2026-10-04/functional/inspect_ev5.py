"""Bounded missing-condition follow-up identified by independent reviewer.
Keep only the Figure EV5 numerical source workbooks; do not retain the29MB
expanded-view source archive containing unrelated figures.
"""
from pathlib import Path
import io,zipfile,urllib.request,hashlib,json,datetime,shutil
import openpyxl
P=Path(__file__).resolve().parent
URL='https://media.springernature.com/original/springer-static/esm/art%3A10.15252%2Femmm.202216863/MediaObjects/44321_2023_BFEMMM202216863_MOESM3_ESM.zip'
assert shutil.disk_usage(P).free>10*1024**3+35*1024**2
with urllib.request.urlopen(URL,timeout=40) as r:b=r.read(31*1024**2+1)
assert len(b)<31*1024**2
z=zipfile.ZipFile(io.BytesIO(b))
receipt={'url':URL,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'all_top_level_members':[{'name':n.filename,'bytes':n.file_size} for n in z.infolist()],'retained':[]}
output={}
for name in z.namelist():
 if 'EV5' not in name or name.startswith('__MACOSX') or not name.endswith('.zip'):continue
 nested=zipfile.ZipFile(io.BytesIO(z.read(name)))
 for sub in nested.namelist():
  if sub.startswith('__MACOSX') or not sub.endswith('.xlsx'):continue
  d=nested.read(sub);out='ev5-'+Path(sub).name;(P/out).write_bytes(d)
  receipt['retained'].append({'archive_member':name,'nested_member':sub,'path':out,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()})
  wb=openpyxl.load_workbook(io.BytesIO(d),data_only=True)
  output[out]={w.title:[list(row) for row in w.values] for w in wb.worksheets}
(P/'ev5-source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(P/'ev5-sheets.json').write_text(json.dumps(output,indent=2)+'\n')
for name,sheets in output.items():
 for sheet,rows in sheets.items():
  emc=[(i,r) for i,r in enumerate(rows) if any('EMC' in str(v) for v in r)]
  print(name,sheet,'rows',len(rows),'EMC rows',len(emc),'head',rows[:1])
