#!/usr/bin/env python3
import hashlib,json,pathlib,re,sys,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timezone
out=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'campaign-output/aso-empirical-sources.json');out.parent.mkdir(parents=True,exist_ok=True)
queries=['(TITLE_ABS:antisense AND TITLE_ABS:"off-target") AND (AUTH_LAST:Hagedorn OR AUTH_LAST:Kamola)','TITLE_ABS:gapmer AND (TITLE_ABS:"RNA-seq" OR TITLE_ABS:"RNA sequencing")','DOI:10.1089/nat.2024.0072']
receipts=[]
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-public-ASO-evidence/1'}),timeout=35) as r:b=r.read(4*1024*1024+1)
    if len(b)>4*1024*1024:raise RuntimeError('4 MiB file limit')
    receipts.append({'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
records={};searches=[];errors=[]
for q in queries:
    try:
        u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':'15'});d=json.loads(get(u));rr=d.get('resultList',{}).get('result',[]);searches.append({'query':q,'hitCount':d.get('hitCount'),'recordsReturned':len(rr)})
        for r in rr:
            k=r.get('pmcid') or r.get('id');records[k]={'id':r.get('id'),'pmcid':r.get('pmcid'),'doi':r.get('doi'),'title':r.get('title'),'year':r.get('pubYear'),'abstract':r.get('abstractText',''),'isOpenAccess':r.get('isOpenAccess'),'source':r.get('source')}
    except Exception as e:errors.append({'query':q,'error':repr(e)})
full=[]
for k,r in records.items():
    if not r.get('pmcid') or len(full)>=10:continue
    try:
        xml=get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+r['pmcid']+'/fullTextXML');root=ET.fromstring(xml);paras=[' '.join(''.join(p.itertext()).split()) for p in root.findall('.//p')]
        selected=[p for p in paras if re.search(r'GSE\d+|E-MTAB-\d+|RNA.seq|RNA sequencing|data availability|supplementary|gapmer|oligonucleotide sequence',p,re.I)]
        links=[{'type':x.attrib.get('ext-link-type'),'href':x.attrib.get('{http://www.w3.org/1999/xlink}href'),'text':' '.join(''.join(x.itertext()).split())} for x in root.findall('.//ext-link')]
        supplements=[{'id':x.attrib.get('id'),'text':' '.join(''.join(x.itertext()).split()),'hrefs':[y.attrib.get('{http://www.w3.org/1999/xlink}href') for y in x.iter() if y.attrib.get('{http://www.w3.org/1999/xlink}href')]} for x in root.findall('.//supplementary-material')]
        full.append({**r,'xmlSha256':hashlib.sha256(xml).hexdigest(),'accessionsMentioned':sorted(set(re.findall(r'GSE\d+|E-MTAB-\d+|SRP\d+',xml.decode()))),'dataAndMethodsExcerpts':selected[:50],'externalLinks':links,'supplements':supplements})
    except Exception as e:errors.append({'pmcid':r.get('pmcid'),'error':repr(e)})
doc={'schema':'public-ASO-empirical-access-search/1','completedAt':datetime.now(timezone.utc).isoformat(),'scope':'Primary-source search, not executed off-target prediction benchmark. Accession mentions may be background references and require confirmation.','searches':searches,'records':list(records.values()),'fullTexts':full,'receipts':receipts,'errors':errors};out.write_text(json.dumps(doc,indent=2)+'\n')
print('ASO_EMPIRICAL_BEGIN');print(json.dumps(doc,separators=(',',':')));print('ASO_EMPIRICAL_END')
