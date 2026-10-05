"""Permitted Europe PMC API source gate. Full responses stay ignored; no browser."""
import concurrent.futures,datetime,hashlib,json,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DISEASE='("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma")'
QUERIES={
 'exact_somatostatin':DISEASE+' AND (somatostatin OR SSTR2 OR SSTR OR DOTATATE OR DOTATOC OR octreotide OR pentetreotide)',
 'exact_transport':DISEASE+' AND (SLC6A2 OR SLC18A1 OR SLC18A2 OR VMAT OR catecholamine OR norepinephrine OR noradrenaline OR MIBG OR iobenguane)',
 'exact_secretory':'TITLE_ABS:('+DISEASE+') AND (neuroendocrine OR chromogranin OR secretory OR synaptophysin OR neural)',
 'historic_transport':'"myxoid chondrosarcoma" AND (SLC18A2 OR SLC6A2 OR MIBG OR DOTATATE OR somatostatin OR catecholamine OR VMAT)',
 'transporter_primary':'TITLE_ABS:(NR4A3 AND sarcoma) AND (SLC6A2 OR SLC18A2 OR VMAT OR MIBG OR catecholamine)'
}
def one(item):
 k,q=item; url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'resultType':'core','pageSize':100,'format':'json'})
 rec={'key':k,'query':q,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url,timeout=40) as r: raw=r.read();rec['http_status']=r.status;rec['response_url']=r.url
  ROOT.joinpath('raw-cache','refined-'+k+'.json').write_bytes(raw);a=json.loads(raw)
  rec.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),hit_count=a.get('hitCount'))
  rows=[]
  for x in a.get('resultList',{}).get('result',[]):
   rows.append({v:x.get(v) for v in ['id','source','pmid','pmcid','doi','title','firstPublicationDate','authorString','abstractText','isOpenAccess','inPMC','hasSuppl']})
  rec['results']=rows;rec['truncated']=a.get('hitCount',0)>len(rows)
 except Exception as e: rec.update(error=type(e).__name__+':'+str(e))
 return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: rows=list(ex.map(one,QUERIES.items()))
 ROOT.joinpath('SOURCE-QUERIES-EXACT.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps([{k:r.get(k) for k in ['key','hit_count','bytes','error','truncated']} for r in rows]))
