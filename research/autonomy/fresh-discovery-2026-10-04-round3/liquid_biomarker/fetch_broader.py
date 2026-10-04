from fetch_sources import BASE,fetch
import json,urllib.parse,urllib.request
sources={'tsoi2021':'PMC8479566','systematic2025':'PMC11724793','ofmt2014':'PMC4053209','signals2026':'PMC13407131'}
receipts=[fetch(n+'.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/'+p+'/fullTextXML') for n,p in sources.items()]
for name,doi in [('bui2023','10.1158/1078-0432.CCR-23-0250'),('braig2022','10.3390/ijms231810215'),('cfrna2025','10.1186/s12885-025-13950-2'),('rna-review2024','10.3390/ijms252111715')]:
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+urllib.parse.quote('DOI:'+doi)+'&format=json'
    r=fetch(name+'-metadata.json',url);receipts.append(r)
    if 'sha256' in r:
        for entry in json.loads((BASE/(name+'-metadata.json')).read_text())['resultList']['result']:
            if entry.get('pmcid'):receipts.append(fetch(name+'.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/'+entry['pmcid']+'/fullTextXML'));break
(BASE/'broader-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
print(json.dumps(receipts,indent=2))
