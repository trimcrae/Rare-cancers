import json,concurrent.futures
from fetch_sources import D,get
JOBS={
 'pabst2025.pdf':'https://www.brainlife.org/fulltext/2025/Pabst_KM250804_LancetOncol.pdf',
 'pabst2025-publisher.html':'https://www.sciencedirect.com/science/article/pii/S1470204525002992',
 'lanzafame2024-supp-index.html':'https://jnm.snmjournals.org/content/65/6/880/tab-supplemental',
 'kessler2022-supp-index.html':'https://jnm.snmjournals.org/content/63/1/89/tab-supplemental',
 'liu2026-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1093/bjr/tqag106&format=json',
 'alf2026-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%22FAPI-74%22%20AND%20%22sarcoma%22&format=json'
}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(get,JOBS.items()))
 (D/'clinical-followup-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
