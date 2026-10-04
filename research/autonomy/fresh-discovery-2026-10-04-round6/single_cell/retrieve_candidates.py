"""Retrieve bounded primary XML and GEO summary metadata; preserve receipts."""
import concurrent.futures, json, pathlib, urllib.parse
from source_followup import repo, ROOT

CANDIDATES={
 'archival_singlecell_2024_PMC11443197':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11443197/fullTextXML',
 'tls_singlecell_2025_PMC12748978':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12748978/fullTextXML',
 'chondro_reanalysis_2026_PMC13021919':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13021919/fullTextXML',
 'tumor_clusters_2025_PMC11970405':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11970405/fullTextXML',
 'bo112_singlecell_2026_PMC13048714':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13048714/fullTextXML',
}
if __name__=='__main__':
 ids=json.loads((ROOT/'sources/geo_alias_search.json').read_text())['esearchresult']['idlist']
 CANDIDATES['geo_alias_summaries']='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urllib.parse.urlencode({'db':'gds','id':','.join(ids),'retmode':'json'})
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: rec=list(pool.map(lambda item:repo(*item,limit=2*1024*1024),CANDIDATES.items()))
 (ROOT/'CANDIDATE-RECEIPTS.json').write_text(json.dumps(rec,indent=2)+'\n')
 for r in rec:print(r['id'],r.get('status',r.get('error')),r.get('bytes'))
