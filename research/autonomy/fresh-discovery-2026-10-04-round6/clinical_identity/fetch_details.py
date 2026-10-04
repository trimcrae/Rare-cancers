import concurrent.futures,json
from fetch_sources import get,D
jobs=[('interobserver2023.pdf','https://cris.unibo.it/retrieve/db118c27-9b88-4be9-b185-eb4d99266f13/1043.full.pdf'),('liver2026-table1.html','https://link.springer.com/article/10.1007/s44178-026-00295-4/tables/1'),('liver2026-supp.docx','https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs44178-026-00295-4/MediaObjects/44178_2026_295_MOESM1_ESM.docx'),('timepoint2023.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11927082/fullTextXML')]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:r=list(p.map(get,jobs))
(D/'detail-fetch-receipts.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
