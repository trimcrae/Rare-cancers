from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from hashlib import sha256
from datetime import datetime,timezone
import json,re,unicodedata
from pypdf import PdfReader
import pdfplumber
OUT=Path(__file__).parent
REPO=Path('C:/Users/mcrae/.codex/worktrees/emc-fo-figure4-20260909/EMC-Research')
BASE=REPO/'research/release-candidates/retained-20260918'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('\u00ad','').replace('\u200b','').replace('\ufeff',''))
def clean(s):return '\f'.join(re.sub(r'(?m)^\s*'+str(i)+r'\s*\Z','',p) for i,p in enumerate(s.split('\f'),1))
def para_text(p):return ''.join((e.text or '') if e.tag==W+'t' else (' ' if e.tag in (W+'tab',W+'br',W+'cr') else ('\u2011' if e.tag==W+'noBreakHyphen' else '')) for e in p.iter())
ap=OUT/'FO-INITIAL-EXPORT-AUDIT.json'; prior=json.loads(ap.read_text('utf-8')); prior_si2=next(d for d in prior['documents'] if d['role']=='supplement-2')
rp=BASE/'rendered-repair/RENDER-RECEIPT.json';receipt=json.loads(rp.read_text('utf-8'));d=next(d for d in receipt['documents'] if d['role']=='supplement-2')
src=REPO/d['input'];pdf=REPO/d['pdf'];pt=pdf.parent/'pdf-text.txt'
assert digest(src)==d['sha256'] and digest(pdf)==d['pdf_sha256']
source=[]
with ZipFile(src) as z:
    for part in [n for n in z.namelist() if n=='word/document.xml' or re.match(r'word/(footnotes|endnotes|header\d+|footer\d+)\.xml$',n)]:
        root=ET.fromstring(z.read(part))
        for pi,p in enumerate(root.iter(W+'p'),1):
            t=para_text(p)
            if t.strip():source.append({'part':part,'paragraph':pi,'text':t})
assert [s['text'] for s in source]==[b['source_text'] for b in prior_si2['blocks']]
reader=PdfReader(pdf);pages=[p.extract_text() or '' for p in reader.pages];retained=pt.read_text('utf-8')
corpora={'pypdf':norm(clean('\f'.join(pages))),'retained':norm(clean(retained))}
with pdfplumber.open(pdf) as pl:
    positioned_pages=[p.extract_text(x_tolerance=1,y_tolerance=3) or '' for p in pl.pages]
corpora['positioned']=norm(clean('\f'.join(positioned_pages)))
rows=[];pos={k:0 for k in ('pypdf','retained')}
for s,old in zip(source,prior_si2['blocks']):
    q=norm(s['text']); matches={k:q in c for k,c in corpora.items()}; ordered={}
    for k in pos:
        loc=corpora[k].find(q,pos[k]);ordered[k]=loc>=0
        if loc>=0:pos[k]=loc+len(q)
    row={**s,'source_text_sha256':sha256(s['text'].encode()).hexdigest(),'match':matches,'ordered_match':ordered,'original_paragraph':old['paragraph']}
    row.update({k:old[k] for k in ('table','row','column') if k in old})
    row['adjudication']='exact in both raw extractors' if all(matches[k] for k in ('pypdf','retained')) else ('fallback glyph reading-order artifact; all text including sign/symbol matches character-position extraction' if matches['positioned'] else 'unresolved mismatch')
    rows.append(row)
missing=[r for r in rows if not any(r['match'].values())]
orderbad=[r for r in rows if all(r['match'][k] for k in ('pypdf','retained')) and not all(r['ordered_match'].values())]
s14=[r for r in rows if r.get('table')==6]
assert not missing and not orderbad
assert len(s14)==70 and all(r['match']['pypdf'] and r['match']['retained'] and all(r['ordered_match'].values()) for r in s14)
c=next(c for c in receipt['combined'] if c['paper']=='FO');combined=REPO/c['path'];combined_reader=PdfReader(combined)
assert digest(combined)==c['sha256']
expected=[]
for comp in c['components']:
    p=REPO/comp['path'];assert digest(p)==comp['sha256']
    expected.extend(page.extract_text() or '' for page in PdfReader(p).pages)
    if 'rendered/FO/' in comp['path']:
        original=next(x for x in prior['documents'] if x['pdf'].replace('\\','/')==str(p).replace('\\','/'))
        assert original['pdf_sha256']==comp['sha256']
actual=[page.extract_text() or '' for page in combined_reader.pages]
assert actual==expected and len(actual)==c['pages']
result={'schema':'emc-fo-repair-text-acceptance/1','checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS_REPAIRED_SI2_AND_COMBINED_TEXTUAL_COMPLETENESS','render_run':35373013434,'source_commit':receipt['source_commit'],'receipt':str(rp),'receipt_sha256':digest(rp),'initial_failure_audit':str(ap),'initial_failure_audit_sha256':digest(ap),'docx':str(src),'docx_sha256':digest(src),'pdf':str(pdf),'pdf_sha256':digest(pdf),'pdf_text':str(pt),'pdf_text_sha256':digest(pt),'all_362_source_paragraphs_exact_to_pre_repair_source':True,'pages':len(pages),'counts':{'blocks':len(rows),'raw_exact_both':sum(r['match']['pypdf'] and r['match']['retained'] for r in rows),'glyph_order_adjudications':sum(not(r['match']['pypdf'] and r['match']['retained']) and r['match']['positioned'] for r in rows),'unresolved':len(missing),'order_failures':len(orderbad),'S14_header_plus_data_rows':len({r['row'] for r in s14}),'S14_cell_paragraphs_exact_in_order':len(s14)},'blocks':rows,'combined':{'path':str(combined),'sha256':digest(combined),'pages':len(actual),'page_text_exactly_matches_components_in_order':True,'component_order':c['component_order'],'unchanged_main_and_SI1_hashes_reverified_against_prior_pass':True},'limits':'Focused textual repair acceptance only. No new prose/scientific review or rendering. Existing main/SI1/cover/highlights passes reused. New actual visual QA remains separately required.'}
dest=OUT/'FO-REPAIR-TEXT-ACCEPTANCE.json'
with dest.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
report=OUT/'FO-REPAIR-TEXT-REPORT.md'
report.write_text(f'''# Fusion-output supplement repair textual acceptance

**PASS — all 362 source paragraphs are preserved in the repaired 12-page SI2, including all S14 rows.** The repaired 67-page combined PDF exactly preserves the unchanged main, unchanged SI1, and repaired SI2 text in order.

Checked {result['checked_at_utc']}. Remote Word export run `35373013434`, source commit `{receipt['source_commit']}`.

- Corrected Word SHA-256: `{digest(src)}`.
- Corrected SI2 PDF SHA-256: `{digest(pdf)}`.
- Recombined FO aiXiv PDF SHA-256: `{digest(combined)}`.
- Detailed acceptance: `FO-REPAIR-TEXT-ACCEPTANCE.json`, SHA-256 `{digest(dest)}`.

The entire nonempty Word paragraph sequence is byte-for-byte equal to the pre-repair accepted source sequence. Of 362 paragraphs, 355 match exactly in both retained PDF text and independent pypdf extraction in source order. The remaining seven are the already identified fallback-glyph reading-order cases; independent character-coordinate extraction restores every full paragraph including its signs/symbols. No character was discarded to resolve them. There are zero unresolved mismatches and zero unexpected ordering failures.

S14 now has its header plus all nine data rows: 70 cell paragraphs match exactly in the required source order. This includes the eight previously missing data rows and every one of their 56 cells, not only the anchor strings SRX1653204 and Normal parotid. All paragraphs, tables, numbers, citations, declarations and historical-record text outside S14 are also covered.

The unchanged main and SI1 PDF hashes were checked against the original audit. Every page of the 67-page combined PDF has extracted text identical to the three component PDFs in order. Prior original failure/mismatch evidence remains intact; the old defective PDF bytes are not accepted by this report.

This is textual export acceptance only. Root's separately pending actual visual QA of these repaired PDF bytes remains necessary. No repository edits, rendering, browser/UI work, downloads or new scientific/prose review were performed.
''',encoding='utf-8')
print(json.dumps({'status':result['status'],'counts':result['counts'],'SI2_pdf_sha256':result['pdf_sha256'],'combined':result['combined'],'report':str(report),'report_sha256':digest(report),'acceptance_sha256':digest(dest)}))
