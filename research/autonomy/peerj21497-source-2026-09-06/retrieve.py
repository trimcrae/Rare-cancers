import urllib.request, urllib.error, json, hashlib, datetime, pathlib, zipfile
ROOT=pathlib.Path(__file__).resolve().parent
url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13374579/supplementaryFiles'
req=urllib.request.Request(url,headers={'User-Agent':'EMC-research source inspection'})
try:
    r=urllib.request.urlopen(req,timeout=120)
except urllib.error.HTTPError as e:
    r=e
data=r.read()
name='supplementaryFiles.response'
(ROOT/name).write_bytes(data)
record={'url':url,'final_url':r.url,'status':r.code,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'headers':dict(r.headers),'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
(ROOT/'supplement-retrieval.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
if zipfile.is_zipfile(ROOT/name):
    with zipfile.ZipFile(ROOT/name) as z:
        print(z.namelist())
        (ROOT/'archive-members.json').write_text(json.dumps([{'name':i.filename,'bytes':i.file_size} for i in z.infolist()],indent=2)+'\n')
        matches=[n for n in z.namelist() if pathlib.PurePosixPath(n).name=='peerj-14-21497-s009.xlsx']
        if len(matches)!=1: raise ValueError(matches)
        (ROOT/'peerj-14-21497-s009.xlsx').write_bytes(z.read(matches[0]))
