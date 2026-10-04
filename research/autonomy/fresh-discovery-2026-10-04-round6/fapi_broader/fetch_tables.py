#!/usr/bin/env python3
import concurrent.futures,json,urllib.parse
from lxml import html
from fetch_sources import ROOT,fetch

specs=[]
for name, path in [('hirmas2023','64/5/711'),('hirmas2024','65/3/372'),('interobserver2023','64/7/1043')]:
 specs.append((name+'_supp_index.html','https://jnm.snmjournals.org/content/'+path+'/tab-supplemental'))
 t=html.fromstring((ROOT/'raw'/f'{name}_jnm.html').read_bytes())
 for i,e in enumerate(t.xpath('//a[normalize-space()="View popup"]')):
  specs.append((name+f'_popup{i+1}.html',urllib.parse.urljoin('https://jnm.snmjournals.org',e.get('href'))))
specs += [
 ('liver2026_table1.html','https://link.springer.com/article/10.1007/s44178-026-00295-4/tables/1'),
 ('liver2026_supp.docx','https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs44178-026-00295-4/MediaObjects/44178_2026_295_MOESM1_ESM.docx'),
 ('three_timepoint_jnm.html','https://jnm.snmjournals.org/content/64/4/618'),
]
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: r=list(ex.map(fetch,specs))
 (ROOT/'table-fetch-receipts.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps([{k:v for k,v in x.items() if k in ['name','status','bytes','error']} for x in r],indent=2))
