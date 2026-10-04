import concurrent.futures,json
from fetch_sources import get,D
jobs={
 'timepoint2023.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC11927082.1/PMC11927082.1.xml',
 'experience2024.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC11764383.1/PMC11764383.1.xml',
 'kratochwil2019-correct-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.2967/jnumed.119.227967&format=json'
}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:out=list(p.map(get,jobs.items()))
(D/'second-order-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
