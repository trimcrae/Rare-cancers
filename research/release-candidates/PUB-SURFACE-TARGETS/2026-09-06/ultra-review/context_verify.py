from pathlib import Path
import csv,gzip,io,zipfile,xml.etree.ElementTree as ET
from html.parser import HTMLParser
root=Path.cwd()
class Plain(HTMLParser):
 def __init__(self):super().__init__();self.words=[]
 def handle_data(self,d):self.words.append(d)
with zipfile.ZipFile(root/'research/autonomy/atlas-prior-art-2026-09-06/original-source-audit.zip') as z:
 parser=Plain();parser.feed(z.read('prame-publisher.html').decode());text=' '.join(parser.words)
 for term in ['QR005','negative (0','negative','whole sections']:
  i=text.lower().find(term.lower());print('PRAME_TEXT',term,text[max(0,i-150):i+800])
with zipfile.ZipFile(root/'research/autonomy/atlas-normal-context-2026-09-06/original-source-packet.zip') as z:
 xml=ET.fromstring(z.read('CSPG4.xml'))
 for e in xml.iter():
  if e.text and ('cytoplasmic' in e.text.lower() or 'plasma membrane' in e.text.lower()):print('HPA_XML',e.tag,e.attrib,e.text[:500])
p=root/'research/autonomy/atlas-sample-organ-2026-09-06/GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz'
with gzip.open(p,'rt') as f:
 reader=csv.reader(f,delimiter='\t');header=next(reader);print('PEAK_HEADER',header[:10])
 for row in reader:
  if 'CSPG4' in row[:7] or 'CHRNA6' in row[:7]:
   print('PEAK',row[:7]);print([(h,v) for h,v in zip(header,row) if 'EMC_' in h or 'STT5610' in h])
