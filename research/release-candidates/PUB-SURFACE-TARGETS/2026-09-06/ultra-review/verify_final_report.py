from pathlib import Path
import hashlib,json
root=Path.cwd()/'review-results'
replacements={'all151':'all 151','across29':'across 29','the2019':'the 2019','frozen11':'frozen 11','these11':'these 11','Python3.12.14':'Python 3.12.14','NumPy2.3.5':'NumPy 2.3.5','openpyxl3.1.5':'openpyxl 3.1.5','et-xmlfile2.0.0':'et-xmlfile 2.0.0','exit0':'exit 0','across29':'across 29'}
for name in ['report.md','findings.json','report.template.md','finalize_review.py']:
 p=root/name;t=p.read_text(encoding='utf-8')
 for a,b in replacements.items():t=t.replace(a,b)
 p.write_text(t,encoding='utf-8')
f=json.loads((root/'findings.json').read_text());r=(root/'report.md').read_text()
assert '__REPLAY_RESULT__' not in r and '__AFTER_RESULT__' not in r and '__RUNNING_STATUS__' not in r
assert f['verdict']=='supported' and not f['blockers'] and not f['process_state']['anything_running']
print(json.dumps({'report':str(root/'report.md'),'report_sha256':hashlib.sha256((root/'report.md').read_bytes()).hexdigest(),'findings':str(root/'findings.json'),'findings_sha256':hashlib.sha256((root/'findings.json').read_bytes()).hexdigest(),'verdict':f['verdict'],'blockers':len(f['blockers']),'maintenance':len(f['maintenance']),'editorial':len(f['editorial']),'verified_inputs_unchanged':f['input_integrity']['files']},indent=2))
