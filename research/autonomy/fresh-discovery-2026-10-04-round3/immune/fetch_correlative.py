from fetch_sources import one,BASE
import concurrent.futures,json
urls={
 'moura2024.pdf':'https://iris.unito.it/bitstream/2318/2019431/1/ccr-24-1782.pdf',
 'moura2024.html':'https://aacrjournals.org/clincancerres/article/30/22/5192/749561/Predictive-and-Dynamic-Signature-for',
 'moura2024-patent.html':'https://patents.google.com/patent/EP4636097A1/en',
 'subramanian2024-tables.xlsx':'https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs43018-024-00743-y/MediaObjects/43018_2024_743_MOESM2_ESM.xlsx',
 'calukovic2024.pdf':'https://ub01.uni-tuebingen.de/xmlui/bitstream/handle/10900/150291/Molekulargenetische%20Charakterisierung%20von%20Sarkomen.pdf?isAllowed=y&sequence=3',
 'frontiers-immune-review.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813480/fullTextXML',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(one,urls.items()))
(BASE/'retrieval-correlative.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
