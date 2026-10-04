"""Bounded read-only replay of culture metadata/search routes; no spectra.
Network indexes can change. Frozen receipts preserve the actual Oct 4 outcome.
"""
from urllib.request import urlopen
from urllib.parse import urlencode
from pathlib import Path
import hashlib,json
q='"NCC-EMC1-C1" OR "NCC-EMC" OR "NCCEMC"'
urls={db:'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urlencode(dict(db=db,term=q,retmode='json')) for db in ['gds','sra','biosample','bioproject']}
urls.update(
    cellosaurus='https://api.cellosaurus.org/search/cell-line?'+urlencode(dict(q='NCC-EMC*',format='txt')),
    biostudies='https://www.ebi.ac.uk/biostudies/api/v1/search?'+urlencode(dict(query='NCC-EMC')),
    pride='https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects?'+urlencode(dict(keyword='NCC-EMC')),
    epmc='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(dict(query='"NCC-EMC" OR "NCC-EMC1-C1"',format='json',pageSize=100)),
    ena='https://www.ebi.ac.uk/ena/portal/api/search?'+urlencode(dict(result='read_run',query='sample_title="*NCC-EMC*" OR study_title="*NCC-EMC*" OR experiment_title="*NCC-EMC*"',fields='run_accession,sample_accession,study_accession,sample_title,study_title,experiment_title',format='json',limit=1000)),
    zurich_geo='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urlencode(dict(db='gds',term='"USZ" AND ("EMC" OR "EMC1" OR "EMC2" OR "EMC3" OR "extraskeletal")',retmax=200,retmode='json')),
    USZ22_metadata='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM6883080&targ=self&form=text&view=full',
    GSE221532_all_samples='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE221532&targ=gsm&form=text&view=full')
if __name__=='__main__':
    out={}
    for name,url in urls.items():
        try:
            with urlopen(url,timeout=30) as r:b=r.read(15000001)
            assert len(b)<=15000000
            out[name]={'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'body':b.decode()}
            print(name,len(b),out[name]['sha256'])
        except Exception as e:out[name]={'url':url,'error':str(e)}
    Path(__file__).with_name('source-search-replay.json').write_text(json.dumps(out,indent=2))
