from fetch_sources import BASE,fetch
import json,xml.etree.ElementTree as E
ss={'asano2019':'PMC6428849','heinhuis2020':'PMC7352477','joch2025':'PMC11974511','anderson2025':'PMC11658723'}
rs=[fetch(n+'.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/fullTextXML') for n,pmc in ss.items()]
(BASE/'eligibility-receipts.json').write_text(json.dumps(rs,indent=2),encoding='utf8')
out={};tx=lambda x:' '.join(' '.join(x.itertext()).split())
for n in ss:
 f=BASE/(n+'.xml')
 if not f.exists():continue
 r=E.parse(f).getroot();o={'tables':[tx(t) for t in r.findall('.//table-wrap')],'supplements':[{'text':tx(t),'links':[x.attrib for x in t.iter() if 'href' in str(x.attrib)]} for t in r.findall('.//supplementary-material')],'body':tx(r.find('body'))}
 out[n]=o;print(n)
 for table in o['tables']:print(table[:15000])
 print('SUPPS',o['supplements'])
(BASE/'eligibility-extracts.json').write_text(json.dumps(out,indent=2),encoding='utf8')
