import concurrent.futures,json
from fetch_sources import get,D
jobs={
 'ferdinandus2022-ts1.docx':'https://pmc-oa-opendata.s3.amazonaws.com/PMC9527500.1/ccr-22-1432_supplementary_table_ts1_suppts1.docx',
 'ferdinandus2022-ts2.docx':'https://pmc-oa-opendata.s3.amazonaws.com/PMC9527500.1/ccr-22-1432_supplementary_table_ts2_suppts2.docx',
 'ferdinandus2022-ts3.docx':'https://pmc-oa-opendata.s3.amazonaws.com/PMC9527500.1/ccr-22-1432_supplementary_table_ts3_suppts3.docx',
 'ferdinandus2022-ts4.docx':'https://pmc-oa-opendata.s3.amazonaws.com/PMC9527500.1/ccr-22-1432_supplementary_table_ts4_suppts4.docx',
 'kessler2022-primary.pdf':'https://jnm.snmjournals.org/content/jnumed/early/2021/04/30/jnumed.121.262096.full.pdf',
 'dynamic2021-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.3389/fonc.2021.651005&format=json',
 'kratochwil2019-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=TITLE:%22FAPI%20PET/CT%22%20AND%20AUTH_LAST:Kratochwil%20AND%20FIRST_PDATE:2019&format=json'
}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:out=list(p.map(get,jobs.items()))
(D/'last-gate-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
