import json,hashlib,sys,zipfile,csv,io,datetime
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(next(D.glob('xlrd*.whl'))))
import xlrd
b=xlrd.open_workbook(str(D/'foundation-supplement2.xls'))
print('sheets',b.sheet_names())
for sh in b.sheets():print(sh.name,sh.nrows,sh.ncols,[str(sh.cell_value(0,c)) for c in range(min(sh.ncols,5))])
checks=[]
a=json.loads((D/'foundation-emc-all-values.json').read_text())
assert a['final_emc_profiles']==75 and a['NR4A3_supported_final_emc_profiles']==75
checks.append('All75finalEMC have defining-event support in extraction')
for c in a['source_labeled_cases']:
 for e in c['all_events']:
  row=e['source_excel_row']-1
  matched=False
  for sh in b.sheets():
   if sh.nrows>row and sh.ncols>=5:
    vals=sh.row_values(row)
    if vals[0]==e['de-identified ID'] and e['gene'] in vals and e['alteration_type'] in vals:matched=True
  assert matched,(c['source_id'],row,e)
checks.append('Every extracted literal event independently located at savedoriginalExcelrow')
entries=[json.loads(s)for s in (D/'source-receipts.jsonl').read_text().splitlines()if s.strip()]
latest={r['name']:r for r in entries if 'sha256'in r}
for n,r in latest.items():
 p=D/n
 assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],n
 assert p.stat().st_size==r['bytes'] and r['bytes']<20000000,n
checks.append('Latest successfuldownloadreceipts matchallretainedsourcebytes; nodownloadhit20MBreadcap')
out={'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','checks':checks,'source_files_checked':len(latest),'foundation_source_sha256':hashlib.sha256((D/'foundation-supplement2.xls').read_bytes()).hexdigest()}
(D/'verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(out)
