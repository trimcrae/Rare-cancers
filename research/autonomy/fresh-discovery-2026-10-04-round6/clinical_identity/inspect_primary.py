import pathlib,json,re,html
D=pathlib.Path(__file__).resolve().parent
out={}
for name in ['timepoint-title-metadata.json','hirmas2023-metadata.json','hirmas2024-metadata.json','interobserver-metadata.json']:
 j=json.loads((D/name).read_text());rows=j.get('resultList',{}).get('result',[])
 print(name,[{k:x.get(k) for k in ['id','pmcid','doi','isOpenAccess','hasSuppl','fullTextUrlList']} for x in rows])
for name in ['liver2026.html','interobserver-repository.html']:
 t=(D/name).read_text();links=sorted(set(html.unescape(x) for x in re.findall('href=[\"\x27]([^\"\x27]+)',t)))
 relevant=[x for x in links if any(k in x.lower() for k in ['supp','esm','pdf','bitstream','table','fulltext'])]
 tabs=[]
 for raw in re.findall(r'<table\b[\s\S]*?</table>',t):
  rows=[]
  for row in re.findall(r'<tr\b[\s\S]*?</tr>',raw):rows.append([' '.join(html.unescape(re.sub('<[^>]+>',' ',c)).split()) for c in re.findall(r'<t[dh]\b[^>]*>([\s\S]*?)</t[dh]>',row)])
  tabs.append(rows)
 out[name]={'links':relevant,'tables':tabs};print(name,'LINKS',relevant,'TABLES',tabs[:1])
(D/'primary-structure.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
