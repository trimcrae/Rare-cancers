import pathlib,urllib.request,json,hashlib,gzip,datetime,re
R=pathlib.Path(__file__).resolve().parent
sources={
 'sept-sponsor-original.html':'https://ir.transcodetherapeutics.com/2026-09-28-TransCode-Reports-Continued-Disease-Stabilization-and-Extended-Treatment-Duration-with-TTX-MC138-in-Ongoing-Phase-1a-Clinical-Trial-Follow-Up',
 'esmo-abstract2025.html':'https://www.annalsofoncology.org/article/S0923-7534%2825%2902472-X/abstract',
 'yoo2018.html':'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0201046',
 'june3-mirror.html':'https://app.boardroomalpha.com/sec_feed/2026/QTR2/0001104659-26-069810/tm2616719d1_ex99-1.htm',
}
out=[]
for n,u in sources.items():
 z={'file':n,'url':u,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as f:b=f.read(1024*1024+1);z.update(status=f.status,content_type=f.headers.get('Content-Type'))
  if b[:2]==b'\x1f\x8b':b=gzip.decompress(b)
  assert len(b)<=1024*1024
  (R/n).write_bytes(b);z.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  if n.startswith('yoo'):z['supp_links']=sorted(set(x for x in re.findall(r'href=["\x27]([^"\x27]+)',b.decode(errors='replace')) if 'supp' in x.lower() or 's001' in x.lower() or 's002' in x.lower()))
 except Exception as e:z['error']=str(e)
 out.append(z)
(R/'context-receipts.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
