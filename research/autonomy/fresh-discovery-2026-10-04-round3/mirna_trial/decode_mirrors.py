import pathlib,gzip,re,json,hashlib,urllib.request,urllib.parse,datetime
R=pathlib.Path(__file__).resolve().parent
rows=json.loads((R/'mirror-receipts.json').read_text())
out=[]
for row in rows:
 if 'error' in row:continue
 p=R/row['file'];raw=p.read_bytes();d=gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw
 q=p.with_suffix('.decoded.html');q.write_bytes(d)
 images=re.findall(r'<img[^>]+src=["\x27]([^"\x27]+)',d.decode(errors='replace'),re.I)
 out.append({'file':q.name,'source_wire_file':p.name,'sha256':hashlib.sha256(d).hexdigest(),'bytes':len(d),'images':images})
 for i in images:
  if 'june-deck' in p.name and not any(x in i for x in ['img013','img017']):continue
  u=urllib.parse.urljoin(row['url'],i);name=p.stem+'-'+u.rsplit('/',1)[-1]
  rec={'file':name,'url':u,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   with urllib.request.urlopen(u,timeout=35) as f:b=f.read(4*1024*1024+1);rec['status']=f.status
   if b[:2]==b'\x1f\x8b':b=gzip.decompress(b)
   if len(b)>4*1024*1024:raise ValueError('cap')
   (R/name).write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  except Exception as e:rec['error']=str(e)
  out.append(rec)
(R/'decoded-image-receipts.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
