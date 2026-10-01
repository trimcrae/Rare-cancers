import hashlib,json,pathlib,sys,urllib.request,zipfile
from datetime import datetime,timezone
OUT=pathlib.Path('campaign-output/deepternary-release-inventory.json');OUT.parent.mkdir(parents=True,exist_ok=True);DEST=OUT.parent/'deepternary-released-files';DEST.mkdir(exist_ok=True)
ASSETS=[{'tag':'v1.0.1','name':'output.zip','size':151480895,'sha256':'1eb43229480459730f7993f3c22ac42e9a1a5aee60d747088eb35aac4f3d18c3'},{'tag':'v1.0.0','name':'TernaryDB.zip','size':1667335,'sha256':None}];COORD={'.pdb','.cif','.sdf','.mol2','.mol'};TABLE={'.csv','.tsv','.json','.txt','.log','.yaml','.yml'};results=[];errors=[]
for spec in ASSETS:
 url='https://github.com/youqingxiaozhua/DeepTernary/releases/download/'+spec['tag']+'/'+spec['name'];archive=DEST/(spec['tag']+'-'+spec['name']);result={'tag':spec['tag'],'asset':spec['name'],'url':url,'expectedBytes':spec['size'],'publisherSha256':spec['sha256'],'savedArchive':str(archive),'members':[],'extracted':[]}
 try:
  h=hashlib.sha256();count=0
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-release-reanalysis'}),timeout=180) as response,archive.open('wb') as f:
   for chunk in iter(lambda:response.read(1024*1024),b''):
    count+=len(chunk)
    if count>spec['size']:raise ValueError('asset exceeds verified release size')
    h.update(chunk);f.write(chunk)
  result.update({'downloadedBytes':count,'sha256':h.hexdigest()})
  if count!=spec['size']:raise ValueError('incomplete full published asset')
  if spec['sha256'] and h.hexdigest()!=spec['sha256']:raise ValueError('publisher SHA256 mismatch')
  result['publisherDigestVerified']=bool(spec['sha256'])
  with zipfile.ZipFile(archive) as z:
   for info in z.infolist():
    name=info.filename;suffix=pathlib.PurePosixPath(name).suffix.lower();result['members'].append({'path':name,'bytes':info.file_size,'compressedBytes':info.compress_size,'CRC32':format(info.CRC,'08x'),'directory':info.is_dir()})
    if info.is_dir() or suffix not in COORD|TABLE:continue
    if info.file_size>64*1024*1024:result['extracted'].append({'path':name,'status':'large-text-member-not-extracted','bytes':info.file_size});continue
    pure=pathlib.PurePosixPath(name)
    if pure.is_absolute() or '..' in pure.parts:raise ValueError('unsafe ZIP path '+name)
    raw=z.read(info);save=DEST/(spec['tag']+'-'+spec['name']+'-extracted')/pathlib.Path(*pure.parts);save.parent.mkdir(parents=True,exist_ok=True);save.write_bytes(raw);rec={'path':name,'savedPath':str(save),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'kind':'coordinate' if suffix in COORD else 'table_or_log','status':'extracted'}
    if suffix in TABLE:
     try:
      value=raw.decode('utf-8')
      if len(raw)<=4*1024*1024:rec['text']=value
      else:rec.update({'textPreview':value[:12000],'fullTextSaved':True})
     except UnicodeDecodeError:rec['textDecoding']='notUTF8'
    result['extracted'].append(rec)
  result['nMembers']=len(result['members']);result['nExtracted']=sum(x['status']=='extracted' for x in result['extracted']);result['status']='full-download-verified-and-inspected'
 except Exception as e:result['status']='failed';result['error']=repr(e);errors.append({'asset':spec['name'],'tag':spec['tag'],'error':repr(e)})
 results.append(result)
doc={'schema':'deepternary-full-released-asset-audit/2','completedAt':datetime.now(timezone.utc).isoformat(),'assets':results,'errors':errors,'limits':['Public151MB asset acquired completely; HTTPRange not required.','v1.0.1output.zip checked against publisher SHA256; v1.0.0TernaryDB.zip has recorded local SHA256.','Acquisition is preparation; score native geometry/released poses next.','No GPU, paidAPI, training, inference, or case-count cap.']}
OUT.write_text(json.dumps(doc,indent=2)+'\n');print('DEEPTERNARY_INVENTORY_BEGIN');print(json.dumps(doc,separators=(',',':')));print('DEEPTERNARY_INVENTORY_END')
if errors:sys.exit(1)
