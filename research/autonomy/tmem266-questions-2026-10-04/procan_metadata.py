"""Identity-only replay of authenticated range in public ProCan workbook."""
import hashlib,json,urllib.request,zlib,xml.etree.ElementTree as ET
from pathlib import Path
url='https://ftp.pride.ebi.ac.uk/pride/data/archive/2025/05/PXD056810/cohort_1_processed_matrix.xlsx'
with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes=79481707-79527626'}),timeout=30) as r:
    assert r.status==206 and r.getheader('Content-Range')=='bytes 79481707-79527626/79537129'
    b=r.read(45921)
assert len(b)==45920
assert hashlib.sha256(b).hexdigest()=='bb3295c76bb864d7696a49ed2709530df08f7a6c04f3bf883e8bc78550ed0508'
xml=zlib.decompress(b,-15);x=ET.fromstring(xml);ss=[''.join(i.itertext()) for i in x]
assert len(ss)==10474 and x.attrib['uniqueCount']=='10474'
out={'url':url,'range':'79481707-79527626','file_bytes':79537129,'xml_sha256':hashlib.sha256(xml).hexdigest(),
     'strings':len(ss),'EMC_aliases':[(i,s) for i,s in enumerate(ss) if any(t in s.lower() for t in ['extraskeletal','chondrosarcoma','myxoid','nr4a3']) or s.lower()=='emc'],
     'sarcoma_labels':[(i,s) for i,s in enumerate(ss) if 'sarcoma' in s.lower() or 'tissue nos' in s.lower()],
     'scope':'Metadata only; generic sarcoma labels do not establish EMC identity; no target protein values read'}
Path(__file__).with_name('procan-metadata.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
