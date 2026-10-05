"""Extract all original-source tables and focused body contexts without image inspection."""
from pathlib import Path
import xml.etree.ElementTree as E,json,re,hashlib
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
 records=json.loads((ROOT/'SOURCE-ACCESS.json').read_text())['sources'];out=[]
 for r in records:
  a=r['accepted']
  if not a:continue
  q=ROOT/a['path'];b=q.read_bytes();assert hashlib.sha256(b).hexdigest()==a['sha256'];tree=E.fromstring(b);body=tree.find('body');text=lambda x:' '.join(x.itertext()) if x is not None else ''
  sections=[{'tag':x.tag,'text':text(x)} for x in body.iter() if x.tag in ['p','table-wrap','fig']] if body is not None else []
  hits=[x for x in sections if re.search('extraskeletal|extra-skeletal|myxoid.chondro|NR4A3|EMC|RECIST|spider|growth.modulation|longitudinal|target.lesion|waterfall',x['text'],re.I)]
  tables=[{'id':x.attrib.get('id'),'label':text(x.find('label')),'caption':text(x.find('caption')),'rows':[[text(y) for y in row if y.tag in ['td','th']] for row in x.findall('.//tr')],'footnotes':text(x.find('table-wrap-foot'))} for x in tree.findall('.//table-wrap')]
  suppl=[{'tag':x.tag,'attrs':x.attrib,'text':text(x)} for x in tree.iter() if x.tag in ['supplementary-material','ext-link','media'] and ('supplement' in text(x).lower() or x.tag in ['supplementary-material','media'])]
  rr={'pmcid':r['pmcid'],'source_sha256':a['sha256'],'title':text(tree.find('.//article-title')),'focused_contexts':hits,'all_tables':tables,'supplement_links':suppl};out.append(rr)
 ROOT.joinpath('source-cache/complete-text-extraction.json').write_text(json.dumps(out,indent=2)+'\n')
 for r in out:
  print('\nSOURCE',r['pmcid'],r['title']);print('TABLES',[(t['label'],len(t['rows']),t['caption'][:90]) for t in r['all_tables']]);print('EMC contexts',[(x['tag'],x['text'][:2100]) for x in r['focused_contexts'] if re.search('extraskeletal|extra-skeletal|myxoid.chondro|NR4A3|\bEMC\b',x['text'],re.I)]);print('SUPPL',str(r['supplement_links'])[:1000])
