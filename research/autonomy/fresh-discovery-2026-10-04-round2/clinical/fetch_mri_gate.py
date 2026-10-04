from fetch_primary import fetch,BASE
from concurrent.futures import ThreadPoolExecutor
import json
SOURCES={
 'mri2025-table1':'https://link.springer.com/article/10.1007/s00256-025-05050-w/tables/1',
 'mri2025-table2':'https://link.springer.com/article/10.1007/s00256-025-05050-w/tables/2',
 'mri2025-table3':'https://link.springer.com/article/10.1007/s00256-025-05050-w/tables/3',
}
if __name__=='__main__':
 receipts=list(ThreadPoolExecutor(max_workers=3).map(fetch,SOURCES.items()))
 (BASE/'fetch-mri-gate-receipts.json').write_text(json.dumps(receipts,indent=2))
 print(json.dumps(receipts,indent=2))
