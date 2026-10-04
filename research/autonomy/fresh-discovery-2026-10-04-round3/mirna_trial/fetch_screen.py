import pathlib,urllib.request,hashlib,json,datetime,io,zipfile
R=pathlib.Path(__file__).resolve().parent
u='https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0201046.s001'
rec={'url':u,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
try:
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as f:d=f.read(3*1024*1024+1);rec.update(status=f.status,content_type=f.headers.get('Content-Type'),content_disposition=f.headers.get('Content-Disposition'))
 assert len(d)<=3*1024*1024
 (R/'yoo2018-s001.bin').write_bytes(d);rec.update(bytes=len(d),sha256=hashlib.sha256(d).hexdigest(),signature=d[:10].hex())
 if zipfile.is_zipfile(io.BytesIO(d)):rec['zip_members']=zipfile.ZipFile(io.BytesIO(d)).namelist()
except Exception as e:rec['error']=str(e)
(R/'screen-source-receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
