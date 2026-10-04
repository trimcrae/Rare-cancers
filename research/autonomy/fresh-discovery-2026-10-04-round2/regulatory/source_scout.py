from pathlib import Path
import urllib.request,json,hashlib,xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
sources={'zullow2022.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9465545/fullTextXML','filion2009.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4429309/fullTextXML','brenca2019.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6766969/fullTextXML','GSE179720.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE179720&targ=self&form=text&view=full'}
receipts=[]
for name,url in sources.items():
    try:
        p=P/name
        if not p.exists():
            with urllib.request.urlopen(url,timeout=40) as r:b=r.read(2000001)
            assert len(b)<=2000000;p.write_bytes(b)
        b=p.read_bytes();receipts.append({'file':name,'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        if name.endswith('.xml'):
            root=E.fromstring(b)
            paragraphs=[' '.join(x.itertext()) for x in root.iter() if x.tag in ('p','title','table-wrap','supplementary-material')]
            hit=[x for x in paragraphs if any(k.lower() in x.lower() for k in ('chondrosarcoma','GSE','accession','data availability','supplementary table','supplementary data'))]
            (P/(name+'.excerpts.txt')).write_text('\n\n'.join(hit),encoding='utf-8')
            print(name,'bytes',len(b),'excerpts',len(hit))
        else: print(name,'bytes',len(b))
    except Exception as e:receipts.append({'file':name,'url':url,'error':str(e)});print(name,str(e))
(P/'source-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8')
