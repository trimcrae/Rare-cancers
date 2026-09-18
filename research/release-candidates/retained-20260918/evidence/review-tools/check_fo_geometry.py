from pathlib import Path
import pdfplumber, json, re, unicodedata
from datetime import datetime, timezone
from hashlib import sha256
OUT=Path(__file__).parent
audit=json.loads((OUT/'FO-INITIAL-EXPORT-AUDIT.json').read_text('utf-8'))
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('\u00ad','').replace('\u200b','').replace('\ufeff',''))
result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'method':'Read PDF character bounding boxes via pdfplumber; geometrically reconstruct lines with x_tolerance=1 and y_tolerance=3. This addresses separately emitted fallback glyphs. No raster render. Terminal page-number equal to ordinal removed. Source blocks already exact in both original extractors remain covered by initial audit.','documents':[]}
for d in audit['documents']:
    pdf=pdfplumber.open(d['pdf']); pages=[]; anomalous=[]
    for pi,page in enumerate(pdf.pages,1):
        lines=page.extract_text_lines(x_tolerance=1,y_tolerance=3,return_chars=True)
        for line in lines:
            if any(c in line['text'] for c in '⁻⁺⚠∈⛔'):
                anomalous.append({'page':pi,'left_to_right':line['text'],'bbox':[line['x0'],line['top'],line['x1'],line['bottom']],'characters':[{'text':c['text'],'x0':c['x0'],'top':c['top'],'x1':c['x1'],'bottom':c['bottom']} for c in line['chars']]})
        pagetext='\n'.join(line['text'] for line in lines)
        pagetext=re.sub(r'(?m)^\s*'+str(pi)+r'\s*\Z','',pagetext)
        pages.append(pagetext)
    corpus=norm('\f'.join(pages)); rows=[]
    for b in d['blocks']:
        row={k:b[k] for k in ('paragraph','kind','source_text')}
        row.update({k:b[k] for k in ('table','row','column') if k in b})
        row['geometry_match']=norm(b['source_text']) in corpus
        row['raw_text_match']=all(b['match'].values())
        rows.append(row)
    entry={'role':d['role'],'pdf_sha256':sha256(Path(d['pdf']).read_bytes()).hexdigest(),'counts':{'source_blocks':len(rows),'geometry_matched':sum(b['geometry_match'] for b in rows)},'blocks':rows,'reordered_lines':anomalous}
    result['documents'].append(entry)
    print(json.dumps({'role':d['role'],'counts':entry['counts'],'symbol_line_count':len(anomalous),'remaining_initial_nonS14_mismatches':[b for b in rows if not b['raw_text_match'] and not b['geometry_match'] and not (d['role']=='supplement-2' and b.get('table')==6)]},ensure_ascii=False))
with (OUT/'FO-GEOMETRY-ADJUDICATION.json').open('x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
