from pathlib import Path
import io,json,zipfile
from openpyxl import load_workbook
root=Path.cwd()
wb=load_workbook(root/'research/autonomy/atlas-prior-art-2026-09-06/428_2023_3606_MOESM1_ESM.xlsx',read_only=True,data_only=True)
for i in [1,2,128,129,130,131,132]:print('PRAME',i,[c.value for c in wb.worksheets[0][i]])
with zipfile.ZipFile(root/'research/autonomy/atlas-normal-context-2026-09-06/original-source-packet.zip') as z:
 c=json.loads(z.read('CSPG4.json'));print('HPA_CSPG4',json.dumps(c,ensure_ascii=False))
with zipfile.ZipFile(root/'research/autonomy/atlas-prior-art-2026-09-06/original-source-audit.zip') as z:
 html=z.read('prame-publisher.html').decode();from bs4 import BeautifulSoup
 text=BeautifulSoup(html,'html.parser').get_text(' ',strip=True)
 for term in ['QR005','negative (0','negative','whole sections']:
  i=text.lower().find(term.lower());print('PRAME_TEXT',term,text[max(0,i-200):i+1000])
