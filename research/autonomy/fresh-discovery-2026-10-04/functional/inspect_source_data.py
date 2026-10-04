"""Preserve and inspect exact source sheets without treating technical reps as donors."""
from pathlib import Path
import json, zipfile, io, hashlib, urllib.request, datetime
import openpyxl
ROOT=Path(__file__).resolve().parent
def main():
 z=zipfile.ZipFile(ROOT/'planaspaz2023-publisher-fig5.zip')
 out={}
 for name in z.namelist():
  if not name.startswith('Fig5/') or not name.endswith('.xlsx'):continue
  wb=openpyxl.load_workbook(io.BytesIO(z.read(name)),data_only=True)
  out[name]={s.title:[list(r) for r in s.values] for s in wb.worksheets}
 (ROOT/'planaspaz2023-fig5-sheets.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 for name,sheets in out.items():
  for sheet,rows in sheets.items():
   hits=[i for i,row in enumerate(rows) if any('EMC' in str(x) for x in row)]
   print(json.dumps({'file':name,'sheet':sheet,'rows':len(rows),'cols':max(map(len,rows)),'EMC_rows':hits,'headers':rows[:4]}))
if __name__=='__main__':main()
