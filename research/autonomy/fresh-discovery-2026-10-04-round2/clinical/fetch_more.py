from fetch_primary import fetch,BASE
from concurrent.futures import ThreadPoolExecutor
import json
SOURCES={
 'agaram2014-full':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4015728/fullTextXML',
 'kapoor2014':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4110079/fullTextXML',
 'bishop2019':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7771031/fullTextXML',
 'case-series2022':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8891938/fullTextXML',
 'surgical-outcomes2023':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10387953/fullTextXML',
 'drilon2008-html':'https://pmc.ncbi.nlm.nih.gov/articles/PMC2779719/',
 'jco2026':'https://ascopubs.org/doi/pdfdirect/10.1200/JCO.2026.44.16_suppl.e23561',
 'oliveira2000-table2':'https://www.nature.com/articles/3880161/tables/2',
}
if __name__=='__main__':
 receipts=list(ThreadPoolExecutor(max_workers=3).map(fetch,SOURCES.items()))
 (BASE/'fetch-more-receipts.json').write_text(json.dumps(receipts,indent=2))
 print(json.dumps(receipts,indent=2))
