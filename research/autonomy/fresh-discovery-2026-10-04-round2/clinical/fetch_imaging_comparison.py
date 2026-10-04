from fetch_primary import fetch,BASE
from concurrent.futures import ThreadPoolExecutor
import json
SOURCES={
 'minami2020':'https://ar.iiarjournals.org/content/40/2/1035',
 'minami2020-metadata':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:32014950&resultType=core&format=json',
 'kandoussi2025-full':'https://link.springer.com/article/10.1007/s00256-024-04800-6',
 'kandoussi2025-table1':'https://link.springer.com/article/10.1007/s00256-024-04800-6/tables/1',
 'kandoussi2025-table2':'https://link.springer.com/article/10.1007/s00256-024-04800-6/tables/2',
 'mri2025-metadata':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:41074947&resultType=core&format=json',
}
if __name__=='__main__':
 receipts=list(ThreadPoolExecutor(max_workers=3).map(fetch,SOURCES.items()))
 (BASE/'fetch-imaging-comparison-receipts.json').write_text(json.dumps(receipts,indent=2))
 print(json.dumps(receipts,indent=2))
