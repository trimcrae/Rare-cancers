from fetch_sources import one,BASE
import concurrent.futures,json,urllib.parse
urls={
 'pollack2020.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7489365/fullTextXML',
 'kelly2020.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6990941/fullTextXML',
 'frontiers-immune-review-correct.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9853527/fullTextXML',
}
for q in ['IMMUNOSARC','sunitinib AND sarcoma','HTG AND sarcoma','39283727[PubMed ID]','33203750[PubMed ID]']:
 urls['geo-search-'+str(len(urls))+'.json']='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&retmode=json&retmax=100&term='+urllib.parse.quote(q)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(one,urls.items()))
(BASE/'response-cohort-retrieval.json').write_text(json.dumps(rows,indent=2));print([(x['name'],x.get('bytes'),x.get('error')) for x in rows])
