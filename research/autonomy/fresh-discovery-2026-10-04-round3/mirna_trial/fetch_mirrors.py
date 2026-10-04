import urllib.request,json,hashlib,pathlib,datetime,re
ROOT=pathlib.Path(__file__).resolve().parent
BASE='https://app.boardroomalpha.com/sec_feed/'
sources={
 'june-deck-mirror.html':BASE+'2026/QTR2/0001104659-26-075440/tm2618153d1_ex99-1.htm',
 'esmo-poster-mirror.html':BASE+'2025/QTR4/0001104659-25-099029/tm2528668d1_ex99-2.htm',
 'sept-release-mirror.html':BASE+'2026/QTR3/0001104659-26-111170/tm2626237d1_ex99-1.htm',
 'june-subjects.jpg':'https://www.sec.gov/Archives/edgar/data/1829635/000110465926075440/tm2618153d1_ex99-1img013.jpg',
 'june-efficacy.jpg':'https://www.sec.gov/Archives/edgar/data/1829635/000110465926075440/tm2618153d1_ex99-1img017.jpg',
 'esmo-poster.jpg':'https://www.sec.gov/Archives/edgar/data/1829635/000110465925099029/tm2528668d1_ex99-2img001.jpg',
}
rows=[]
for name,url in sources.items():
 r=dict(file=name,url=url,accessed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as f: d=f.read(4*1024*1024+1);r.update(status=f.status,final_url=f.url,content_type=f.headers.get('Content-Type'))
  if len(d)>4*1024*1024:raise ValueError('Scoped cap')
  (ROOT/name).write_bytes(d);r.update(bytes=len(d),sha256=hashlib.sha256(d).hexdigest())
  if name.endswith('.html'):r['images']=re.findall(r'<img[^>]+src=["\x27]([^"\x27]+)',d.decode(errors='replace'),re.I)
 except Exception as e:r['error']=str(e)
 rows.append(r)
(ROOT/'mirror-receipts.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
