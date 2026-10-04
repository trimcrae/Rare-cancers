from fetch_primary import fetch,BASE
from concurrent.futures import ThreadPoolExecutor
import json
SOURCES={
 'ogura2012-full':'https://link.springer.com/article/10.1007/s00402-012-1557-9',
 'ogura2012-table1':'https://link.springer.com/article/10.1007/s00402-012-1557-9/tables/1',
 'ogura2012-table2':'https://link.springer.com/article/10.1007/s00402-012-1557-9/tables/2',
 'paioli2021-full':'https://link.springer.com/article/10.1245/s10434-020-08737-7',
 'paioli2021-table1':'https://link.springer.com/article/10.1245/s10434-020-08737-7/tables/1',
 'paioli2021-table2':'https://link.springer.com/article/10.1245/s10434-020-08737-7/tables/2',
 'mri2025-full':'https://link.springer.com/article/10.1007/s00256-025-05050-w',
 'huang2023-doi':'https://doi.org/10.1016/j.modpat.2023.100161',
}
if __name__=='__main__':
 receipts=list(ThreadPoolExecutor(max_workers=3).map(fetch,SOURCES.items()))
 (BASE/'fetch-springer-receipts.json').write_text(json.dumps(receipts,indent=2))
 print(json.dumps(receipts,indent=2))
