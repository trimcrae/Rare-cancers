"""Quiet ordinary public API retrieval; originals retained only in ignored cache."""
import argparse, datetime, hashlib, json, pathlib, urllib.request, urllib.parse
BASE=pathlib.Path(__file__).parent
CACHE=BASE/'.cache'; CACHE.mkdir(exist_ok=True)
def fetch(name,url,cap=8*1024*1024):
    dest=CACHE/name
    req=urllib.request.Request(url,headers={'User-Agent':'EMC-evidence-research/1.0'})
    rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'name':name,'url':url}
    try:
        with urllib.request.urlopen(req,timeout=40) as r:
            b=r.read(cap+1);rec.update(status=r.status,content_type=r.headers.get('Content-Type'),final_url=r.url)
        if len(b)>cap: raise ValueError('response exceeds source cap')
        dest.write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),cache_only=str(dest),status='retained')
    except Exception as e: rec.update(status='unavailable_attempt',error=str(e))
    return rec
def search(name,query):
    u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':query,'format':'json','pageSize':1000,'resultType':'core'})
    return fetch(name+'.json',u)
if __name__=='__main__':
    jobs=[
      ('hallmark_early.json','https://www.gsea-msigdb.org/gsea/msigdb/human/geneset/HALLMARK_ESTROGEN_RESPONSE_EARLY.json'),
      ('hallmark_late.json','https://www.gsea-msigdb.org/gsea/msigdb/human/geneset/HALLMARK_ESTROGEN_RESPONSE_LATE.json'),
      ('hallmark_primary.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4707969/fullTextXML')]
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as ex: records=list(ex.map(lambda z:fetch(*z),jobs))
    queries={
      'emc_endocrine':'("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") AND (estrogen OR oestrogen OR progesterone OR endocrine OR tamoxifen OR PGR OR ESR1 OR hormone)',
      'emc_expression':'("extraskeletal myxoid chondrosarcoma") AND (transcriptome OR transcriptomic OR RNA-seq OR "gene expression" OR immunohistochemical)',
      'fusion_endocrine':'("NR4A3" OR "TEC") AND (estrogen OR progesterone OR PGR OR tamoxifen)'
    }
    with ThreadPoolExecutor(max_workers=3) as ex: records+=list(ex.map(lambda z:search(*z),queries.items()))
    (BASE/'SOURCE-GATE-RECEIPTS.json').write_text(json.dumps(records,indent=2)+'\n')
    for r in records: print(r['name'],r['status'],r.get('bytes'),r.get('error',''))
