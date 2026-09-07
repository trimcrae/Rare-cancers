from pathlib import Path
import difflib,hashlib,json,zipfile
from pypdf import PdfReader
old=Path.cwd();root=Path(r'C:/Users/mcrae/.codex/worktrees/8010/EMC-Research');out=old/'review-results/focused-final-verification'
manifest=json.loads((old/'review-input-manifest.json').read_text());changed=[];missing=[];unchanged=[];seen=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n,v in manifest['files'].items():
 assert sha(old/n)==v['sha256'],n
 p=root/n
 if not p.exists():missing.append(n);continue
 h=sha(p);seen.append({'path':n,'sha256':h,'bytes':p.stat().st_size})
 if h!=v['sha256']:changed.append({'path':n,'old_sha256':v['sha256'],'final_sha256':h})
 else:unchanged.append(n)
print('CHANGED',json.dumps(changed,indent=2));print('MISSING',missing);print('UNCHANGED',len(unchanged))
for n in ['research/manuscripts/surface-targets/emc-tissue-rna-prioritization.md','research/manuscripts/surface-targets/plot_emc_tissue_rna.py']:
 diff=''.join(difflib.unified_diff((old/n).read_text().splitlines(True),(root/n).read_text().splitlines(True),fromfile='frozen/'+n,tofile='final/'+n));print(diff);(out/(Path(n).name+'.diff')).write_text(diff)
mp='research/manuscripts/surface-targets/';papers=[mp+'emc-tissue-rna-prioritization-preprint.pdf',mp+'emc-tissue-rna-prioritization-supplementary-information.pdf'];all_text=[];pagechecks=[]
for n in papers:
 a=PdfReader(old/n);b=PdfReader(root/n);assert len(a.pages)==len(b.pages)
 for i,(pa,pb) in enumerate(zip(a.pages,b.pages),1):
  ta=pa.extract_text();tb=pb.extract_text();all_text.append(tb)
  same=ta.replace('c8c7c21ba','8bb8c9d29')==tb
  print('PAGE',Path(n).name,i,'equal_except_source_revision',same)
  if not same:(out/(Path(n).name+f'.page{i}.txt.diff')).write_text(''.join(difflib.unified_diff(ta.splitlines(True),tb.splitlines(True))),encoding='utf-8')
  pagechecks.append({'file':n,'page':i,'exact_text_except_source_revision':same,'media_box_equal':list(pa.mediabox)==list(pb.mediabox),'final_page_text_sha256':hashlib.sha256(tb.encode()).hexdigest()})
combined=root/'research/release-candidates/PUB-SURFACE-TARGETS/2026-09-06/emc-tissue-rna-prioritization-submission.pdf';cp=PdfReader(combined);assert len(cp.pages)==11;assert [p.extract_text() for p in cp.pages]==all_text
print('COMBINED',sha(combined),'page_text_append_exact',True)
package=Path(r'C:/Users/mcrae/.codex/review-workspaces/emc-tissue-rna-package-20260906/emc-tissue-rna-code-data-supplement-8bb8c9d.zip')
with zipfile.ZipFile(package) as z:
 for n in ['README.md','FILES-SHA256.json','source-notes/prame-five-emc-factual-rows.json','source-notes/source-rights-and-retrieval.json']:
  data=z.read(n).decode();print('PACKAGE',n,data if n!='FILES-SHA256.json' else data[:2000])
(out/'initial-focused-checks.json').write_text(json.dumps({'changed_against_frozen':changed,'missing_root_paths':missing,'unchanged_count':len(unchanged),'checked_final_inputs_before':seen,'page_checks':pagechecks,'combined_page_text_append_exact':True,'combined_sha256':sha(combined)},indent=2)+'\n')
