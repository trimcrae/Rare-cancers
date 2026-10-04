#!/usr/bin/env python3
import concurrent.futures, json, urllib.parse
from fetch_sources import ROOT, fetch

specs = [
 ('hirmas2023_title_metadata.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&pageSize=100&query='+urllib.parse.quote('"single-center database" AND "324"')),
 ('hirmas2024_title_metadata.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&pageSize=100&query='+urllib.parse.quote('"Diagnostic accuracy" AND FAPI AND Hirmas')),
 ('interobserver_title_metadata.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&pageSize=100&query='+urllib.parse.quote('"Interobserver" AND "FAPI"')),
 ('three_timepoint_pmc.html','https://pmc.ncbi.nlm.nih.gov/articles/PMC11927082/'),
 ('hirmas2023_jnm.html','https://jnm.snmjournals.org/content/64/5/711'),
 ('hirmas2024_jnm.html','https://jnm.snmjournals.org/content/65/3/372'),
 ('interobserver2023_jnm.html','https://jnm.snmjournals.org/content/64/7/1043'),
 ('liver2026_springer.html','https://link.springer.com/article/10.1007/s44178-026-00295-4'),
 ('liver2026_crossref.json','https://api.crossref.org/works/10.1007/s44178-026-00295-4'),
]
if __name__ == '__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
  r=list(ex.map(fetch,specs))
 (ROOT/'fetch-more-receipts.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps([{k:v for k,v in x.items() if k in ['name','status','bytes','error']} for x in r],indent=2))
