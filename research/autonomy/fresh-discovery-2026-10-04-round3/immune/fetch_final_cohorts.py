from fetch_sources import one,BASE
import concurrent.futures,json
urls={
 'starzer2021.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7993298/fullTextXML',
 'starzer2021-supp.pdf':'https://jitc.bmj.com/content/jitc/suppl/2021/03/24/jitc-2020-001458.DC1/jitc-2020-001458supp001_data_supplement.pdf',
 'kelly2020.html':'https://pmc.ncbi.nlm.nih.gov/articles/PMC6990941/',
 'pollack2020.html':'https://pmc.ncbi.nlm.nih.gov/articles/PMC7489365/',
 'gse239561.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE239561&targ=gsm&form=text&view=full',
 'gse214779.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE214779&targ=gsm&form=text&view=full',
 'gse172043.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE172043&targ=gsm&form=text&view=full',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: rows=list(ex.map(one,urls.items()))
(BASE/'final-cohort-retrieval.json').write_text(json.dumps(rows,indent=2));print([(x['name'],x.get('bytes'),x.get('error')) for x in rows])
