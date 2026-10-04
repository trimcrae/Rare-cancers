from fetch_primary import fetch,BASE
from concurrent.futures import ThreadPoolExecutor
import json
SOURCES={
 'oliveira2000-full':'https://www.nature.com/articles/3880161',
 'agaram2014-html':'https://pmc.ncbi.nlm.nih.gov/articles/PMC4015728/',
 'bishop2019-html':'https://pmc.ncbi.nlm.nih.gov/articles/PMC7771031/',
 'ogura2012-metadata':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:22678528&resultType=core&format=json',
 'all2014-metadata':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=TITLE:extraskeletal%20AND%20FIRST_PDATE:2014&resultType=core&format=json',
 'huang2023':'https://www.sciencedirect.com/science/article/pii/S0893395223000479',
}
if __name__=='__main__':
 receipts=list(ThreadPoolExecutor(max_workers=3).map(fetch,SOURCES.items()))
 (BASE/'fetch-followup-receipts.json').write_text(json.dumps(receipts,indent=2))
 print(json.dumps(receipts,indent=2))
