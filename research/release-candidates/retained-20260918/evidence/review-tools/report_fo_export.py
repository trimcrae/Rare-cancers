from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json,re,unicodedata
from pypdf import PdfReader
OUT=Path(__file__).parent
REPO=Path('C:/Users/mcrae/.codex/worktrees/emc-fo-figure4-20260909/EMC-Research')
BASE=REPO/'research/release-candidates/retained-20260918'
ap=OUT/'FO-INITIAL-EXPORT-AUDIT.json';gp=OUT/'FO-GEOMETRY-ADJUDICATION.json'
audit=json.loads(ap.read_text('utf-8')); geo=json.loads(gp.read_text('utf-8'))
receipt=json.loads(Path(audit['render_receipt']).read_text('utf-8'))
def digest(p):return sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('\u00ad','').replace('\u200b','').replace('\ufeff',''))
def clean(s):return '\f'.join(re.sub(r'(?m)^\s*'+str(i)+r'\s*\Z','',p) for i,p in enumerate(s.split('\f'),1))
final={'schema':'emc-fo-export-adjudication/1','checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'FAIL_EXPORT_OMISSION','source_commit':audit['source_commit'],'initial_audit':{'path':str(ap),'sha256':digest(ap)},'geometry_audit':{'path':str(gp),'sha256':digest(gp)},'documents':[]}
for d,g in zip(audit['documents'],geo['documents']):
    assert d['role']==g['role']
    assert digest(Path(d['docx']))==d['docx_sha256'] and digest(Path(d['pdf']))==d['pdf_sha256']
    corpus=norm(clean('\f'.join(p.extract_text() or '' for p in PdfReader(d['pdf']).pages)))
    pos=0;ordered=0;glyph=[];omitted=[];unexpected=[]
    for b,gb in zip(d['blocks'],g['blocks']):
        assert b['paragraph']==gb['paragraph']
        if d['role']=='supplement-2' and b.get('table')==6 and b.get('row',0)>=3:
            omitted.append(b);continue
        if not all(b['match'].values()) and gb['geometry_match']:
            glyph.append({'paragraph':b['paragraph'],'source_text':b['source_text'],'source_text_sha256':b['source_text_sha256'],'adjudication':'Fallback glyph extraction order. Full exact paragraph including every symbol matches independent character-coordinate-based reading order.'});continue
        loc=corpus.find(norm(b['source_text']),pos)
        if loc<0:unexpected.append(b)
        else:ordered+=1;pos=loc+len(norm(b['source_text']))
    assert not unexpected
    row={'role':d['role'],'docx_sha256':d['docx_sha256'],'pdf_sha256':d['pdf_sha256'],'source_hash_authority':d['source_hash_authority'],'source_blocks':d['counts']['blocks'],'raw_exact_block_count':d['counts']['exact_direct'],'exact_in_source_order_excluding_adjudicated_glyphs_and_S14_omission':ordered,'glyph_order_artifact_blocks':glyph,'omitted_block_count':len(omitted),'unexpected_remaining':unexpected,'status':'FAIL_S14_EIGHT_ROWS_OMITTED' if omitted else 'PASS_TEXTUAL_COMPLETENESS'}
    if omitted:
        t=next(t for t in d['tables'] if t['table']==6)
        row['omitted_rows']=[{'source_table':6,'source_row_including_header':i,'cells':cells} for i,cells in enumerate(t['rows'],1) if i>=3]
        row['location']='Supplementary Table S14, rendered SI2 PDF page 2; header and ReMap2022 retained, next page starts Supplementary Table S15.'
    final['documents'].append(row)
c=next(c for c in receipt['combined'] if c['paper']=='FO');cp=REPO/c['path'];cr=PdfReader(cp)
expected=[]
for x in c['components']:expected.extend(p.extract_text() or '' for p in PdfReader(REPO/x['path']).pages)
actual=[p.extract_text() or '' for p in cr.pages]
final['combined_pdf']={'path':str(cp),'sha256':digest(cp),'matches_receipt':digest(cp)==c['sha256'],'pages':len(actual),'page_text_identical_to_components_in_order':actual==expected,'consequence':'S14 omission propagates unchanged into combined aiXiv PDF. Do not post these bytes.'}
final['metadata']='Author, correspondence, ORCID, declaration and preprint lines preserve source text. FO acknowledges existing aiXiv version 1.1; journal-not-submitted wording remains about the journal derivative. No independent external identity/current-page review performed.'
assert final['combined_pdf']['matches_receipt'] and actual==expected
fp=OUT/'FO-EXPORT-ADJUDICATION.json'
with fp.open('x',encoding='utf-8') as f:json.dump(final,f,ensure_ascii=False,indent=2);f.write('\n')
lines=['# Fusion-output DOCX-to-PDF export integrity','', '**FAIL — Supplementary Table S14 loses eight complete data rows in Supplementary File 2 and the combined aiXiv PDF.** No additional textual export loss was found across all five documents after explicit glyph-order adjudication.','',f"Checked {final['checked_at_utc']}; render source commit `{audit['source_commit']}`. This is a read-only comparison, not scientific or prose review.",'','## Bound evidence','',f"- Initial mismatch audit (preserved): `FO-INITIAL-EXPORT-AUDIT.json`, SHA-256 `{digest(ap)}`.",f"- Character-position adjudication: `FO-GEOMETRY-ADJUDICATION.json`, SHA-256 `{digest(gp)}`.",f"- Final adjudication: `FO-EXPORT-ADJUDICATION.json`, SHA-256 `{digest(fp)}`.",f"- Render receipt: `{audit['render_receipt']}`, SHA-256 `{audit['render_receipt_sha256']}`.",f"- Main source authority: `{audit['label_receipt']}`, SHA-256 `{audit['label_receipt_sha256']}`.",'','The main was compared to `rendered/FO/main-with-corrected-labels.docx` (SHA-256 `567d3f02aec8e7e4c0181538dd03f22cb55e53c9e15429a2bd95bbf541d8df34`). The render receipt intentionally retains the original input hash; the corrected Word hash was verified against the label-correction receipt. Other documents use the original inputs and render receipt hashes. All current input/PDF hashes matched these authorities.','','## Comprehensive coverage','','| Role | Source paragraphs including cells | Exact initial matches | Glyph-order artifacts resolved geometrically | Actual omitted cell paragraphs | Result |','| --- | ---: | ---: | ---: | ---: | --- |']
for d in final['documents']:lines.append(f"| {d['role']} | {d['source_blocks']} | {d['raw_exact_block_count']} | {len(d['glyph_order_artifact_blocks'])} | {d['omitted_block_count']} | {d['status']} |")
lines+=['','Source matching includes every nonempty paragraph/table-cell paragraph, all numbers, citations, references and declarations. Normalization is NFKC plus whitespace/line breaks, soft hyphens and zero-width/BOM removal. Only terminal printed page numbers equal to the PDF page ordinal are removed. No scientific digit, sign or citation is discarded. After excluding the specifically documented lost S14 cells and geometrically resolved glyph cases, every other source paragraph matches the actual PDF in source order without reusing occurrences.','','## True loss: eight S14 rows','','In source XML, S14 is table 6 and has a header plus nine data rows. The PDF retains only the header and first data row, ReMap2022 (merged), on page 2. Page 3 proceeds to S15. The omitted source rows are:','','| XML row including header | Experiment |','| ---: | --- |']
lost=next(d for d in final['documents'] if d['omitted_block_count'])
for r in lost['omitted_rows']:lines.append(f"| {r['source_row_including_header']} | {r['cells'][0]} |")
lines+=['','These eight rows contain 56 source cell paragraphs. The initial substring comparison detected 42 missing cell strings; 14 generic/repeated strings also occur elsewhere and therefore initially matched. The complete row/position check establishes that all 56 cells are absent from their required S14 positions. Full exact cell contents and paragraph ordinals are preserved in the initial audit; full omitted rows are reproduced in the final JSON. No other table/paragraph omission remains after adjudication.','','## Non-loss mismatches','','The other 13 initial mismatches are reading-order artifacts from separately emitted fallback glyphs. PDF character-coordinate extraction restores each entire source block exactly, including all signs/symbols. No glyph is waived or dropped to obtain a match.','','- Main XML paragraphs 150, 151, 155 and 335: scientific-notation superscript minus signs; paragraphs 263 and 283: CD1c superscript plus.','- SI2 XML paragraphs 64, 65 and 74: scientific-notation superscript minus; paragraph 270: warning symbol; paragraph 294: set-membership symbol; paragraph 322: CD1c superscript plus; paragraph 326: no-entry symbol.','','`FO-GEOMETRY-ADJUDICATION.json` records character bounding boxes and reconstructed lines. This is text-coordinate inspection without rendering. Raw mismatch records remain intact.','','## Consequence and limits','',f"Combined FO PDF: `{cp}`; SHA-256 `{digest(cp)}`, {len(actual)} pages. Its extracted page text exactly equals the component pages in order, so the S14 omission is also present in the combined upload bytes. **Do not post this PDF.** Repair export pagination, rerender the affected supplement and regenerate the combined PDF, then verify all ten S14 rows (header plus nine data rows) and repeat the affected completeness/visual checks.",'',final['metadata'],'','No source/scientific inputs, repository files or receipts were modified. No UI, browser, rendering, downloads, publication or scientific reevaluation was performed. This report covers textual completeness; visual layout is covered by the separate visual advisor.']
mp=OUT/'FO-EXPORT-REPORT.md'
with mp.open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
print(json.dumps({'report':str(mp),'report_sha256':digest(mp),'adjudication_sha256':digest(fp),'summary':[{'role':d['role'],'source_blocks':d['source_blocks'],'glyph_order_artifact_count':len(d['glyph_order_artifact_blocks']),'omitted_cells':d['omitted_block_count'],'remaining':len(d['unexpected_remaining'])} for d in final['documents']],'combined':final['combined_pdf']}))
