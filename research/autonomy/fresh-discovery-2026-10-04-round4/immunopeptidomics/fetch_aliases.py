import json,concurrent.futures,urllib.parse
from fetch_sources import D,get
terms=['H-EMC-SS','HEMCSS','USZ20','USZ22','USZ23','NCC-EMC1','V1-34','NR4A2','EMC']
JOBS={f'pride-alias-{t}.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?'+urllib.parse.urlencode({'keyword':t,'pageSize':100,'page':0}) for t in terms}
JOBS['jci2023-ena-runs.tsv']='https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA987736&result=read_run&fields=study_accession,sample_accession,secondary_sample_accession,run_accession,sample_alias,sample_title,library_strategy,library_source,library_selection&format=tsv'
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(get,JOBS.items()))
 (D/'alias-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
