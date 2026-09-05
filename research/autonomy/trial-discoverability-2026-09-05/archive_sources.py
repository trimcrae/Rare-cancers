"""Archive primary source bytes and metadata. No paid services."""
import retrieve as r
urls={
 'api-version.json':'https://clinicaltrials.gov/api/v2/version',
 'api-search-areas.json':'https://clinicaltrials.gov/api/v2/studies/search-areas',
 'emc-primary.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4015728/fullTextXML',
 'emc-primary.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:24746215%20AND%20SRC:MED&format=json&resultType=core',
 'dsrct-primary.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8187063%20AND%20SRC:MED&format=json&resultType=core',
 'ss-primary.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/ng0894-502&format=json&resultType=core',
 'ss-modern-primary.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=TITLE:%22SS18-SSX%22&format=json&resultType=core&pageSize=5',
 'trialgpt-primary.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41467-024-53081-z&format=json&resultType=core',
 'matchminer-primary.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9537311/fullTextXML',
 'rarecure-primary.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13215153/fullTextXML',
 'trialgpt2-preprint.html':'https://arxiv.org/abs/2609.01202'
}
dest=r.SOURCES/'literature'; dest.mkdir(exist_ok=True)
m=[]
for name,url in urls.items():
 try:
  b,h=r.get(url); p=dest/name; p.write_bytes(b)
  m.append({'file':p.relative_to(r.ROOT).as_posix(),'url':url,'retrieved_at_utc':r.now(),'sha256':r.sha(b),'bytes':len(b),'headers':h})
  print(name,len(b),flush=True)
 except Exception as e:
  m.append({'url':url,'error':repr(e),'retrieved_at_utc':r.now()}); print(name,repr(e),flush=True)
 r.save(dest/'source-manifest.json',m)
