from fetch_sources import one,BASE
import concurrent.futures,json,datetime
urls={
 'subramanian2024.html':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11058033/',
 'subramanian2024-nature.html':'https://www.nature.com/articles/s43018-024-00743-y',
 'calukovic2024.pdf':'https://publikationen.uni-tuebingen.de/xmlui/bitstream/10900/150291/3/Molekulargenetische%20Charakterisierung%20von%20Sarkomen.pdf',
 'immunosarc2020-supp.pdf':'https://jitc.bmj.com/content/jitc/8/2/e001561/DC1/embed/inline-supplementary-material-1.pdf?download=true',
 'gse-htg-search.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%22IMMUNOSARC%22&format=json&pageSize=50',
 'bostongene-documents.html':'https://www.bostongene.com/news-and-publications/documents',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(one,urls.items()))
(BASE/'retrieval-followup.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
