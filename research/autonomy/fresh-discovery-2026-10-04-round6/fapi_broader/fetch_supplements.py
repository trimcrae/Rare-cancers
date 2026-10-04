#!/usr/bin/env python3
import concurrent.futures,json
from fetch_sources import ROOT,fetch
specs=[
 ('hirmas2023_supp.pdf','https://jnm.snmjournals.org/highwire/filestream/110917/field_highwire_adjunct_files/0/264689_Supplemental_Data.pdf'),
 ('hirmas2024_supp.pdf','https://jnm.snmjournals.org/highwire/filestream/117364/field_highwire_adjunct_files/0/266652_Supplemental_Data.pdf'),
 ('interobserver2023_guide.pdf','https://jnm.snmjournals.org/highwire/filestream/111986/field_highwire_adjunct_files/0/Guide_for_Readers.pdf'),
 ('interobserver2023_teaching.pdf','https://jnm.snmjournals.org/highwire/filestream/111986/field_highwire_adjunct_files/1/Teaching_Cases.pdf'),
 ('three_timepoint_table1.html','https://jnm.snmjournals.org/highwire/markup/110525/expansion?width=1000&height=500&iframe=true&postprocessors=highwire_tables%2Chighwire_reclass%2Chighwire_figures%2Chighwire_math%2Chighwire_inline_linked_media%2Chighwire_embed'),
]
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:r=list(ex.map(fetch,specs))
 (ROOT/'supplement-fetch-receipts.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps([{k:v for k,v in x.items() if k in ['name','status','bytes','error']} for x in r],indent=2))
