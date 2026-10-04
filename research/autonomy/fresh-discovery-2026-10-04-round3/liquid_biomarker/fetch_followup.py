import json, urllib.request, xml.etree.ElementTree as ET, zipfile,io
from fetch_sources import BASE,fetch
urls=[('localized-supp.zip','https://www.mdpi.com/1422-0067/21/12/4483/s1'),('review-liquid2025.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11941651/fullTextXML'),('eastley2018.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5828212/fullTextXML'),('demoret2019.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6966562/fullTextXML'),('czachor2025.html','https://www.researchwithrowan.com/en/publications/correlation-between-circulating-tumor-dna-ctdna-and-disease-statu/')]
receipts=[fetch(n,u) for n,u in urls]
(BASE/'followup_receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
for r in receipts:print(r)
f=BASE/'localized-supp.zip'
if f.exists() and zipfile.is_zipfile(f):
    with zipfile.ZipFile(f) as z:
        info=[{'name':x.filename,'bytes':x.file_size} for x in z.infolist()]; print(info)
        (BASE/'localized-supp-index.json').write_text(json.dumps(info,indent=2))
        for x in z.infolist():
            if x.filename.lower().endswith(('.pdf','.xlsx','.docx','.txt','.csv')) and x.file_size<2*1024**2:
                (BASE/('localized-'+x.filename.replace('/','_'))).write_bytes(z.read(x))
