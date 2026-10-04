from fetch_sources import BASE,fetch
import json,urllib.request,zipfile,io,hashlib,datetime,shutil
rs=[fetch('asano2019-supp.pdf','https://static-content.springer-cdn.com/esm/art%3A10.1038%2Fs41467-019-09143-8/MediaObjects/41467_2019_9143_MOESM2_ESM.pdf',3*1024**2)]
for name,pmc in [('heinhuis2020','PMC7352477'),('tsoi2021','PMC8479566'),('joch2025','PMC11974511')]:
 url='https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/supplementaryFiles';r={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'retained':[]}
 try:
  assert shutil.disk_usage(BASE).free>10*1024**3
  with urllib.request.urlopen(url,timeout=45) as resp:raw=resp.read(5*1024**2+1);r['status']=resp.status
  assert len(raw)<=5*1024**2
  r.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  def parse(raw):
   with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for info in z.infolist():
     r.setdefault('members',[]).append({'name':info.filename,'bytes':info.file_size})
     if info.filename.lower().endswith('.zip'):parse(z.read(info))
     elif info.filename.lower().endswith(('.xlsx','.docx','.pdf','.csv','.txt')):
      out=name+'-'+info.filename.split('/')[-1];payload=z.read(info)
      assert sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file())+len(payload)<10*1024**2
      (BASE/out).write_bytes(payload);r['retained'].append({'name':out,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
  parse(raw)
 except Exception as e:r['error']=str(e)
 rs.append(r)
(BASE/'rna-supp-receipts.json').write_text(json.dumps(rs,indent=2),encoding='utf8');print(json.dumps(rs,indent=2))
