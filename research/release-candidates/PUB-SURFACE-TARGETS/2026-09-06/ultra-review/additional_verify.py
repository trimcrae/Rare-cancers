from pathlib import Path
import json,hashlib,sys,platform,importlib.metadata,xml.etree.ElementTree as ET
root=Path.cwd();p=root/'research/autonomy/atlas-hofvander-validation-2026-09-06';out=root/'review-results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((p/'coordinator-authorization.json').read_text());match={n:sha(p/n)==h for n,h in a['sha256'].items()}
print('AUTH_HASH_MATCH',match)
fp=root/'research/manuscripts/figures/surface-tissue-rna-figure-provenance.json';f=json.loads(fp.read_text());print('FIGURE_SELF',sha(fp),f['figures'].get(fp.name));print('FIGURE_OTHER_HASHES',{n:sha(fp.parent/n)==h for n,h in f['figures'].items() if n!=fp.name})
rootxml=ET.parse(root/'research/autonomy/atlas-hofvander-source-2026-09-06/hofvander2026.xml').getroot();tx=' '.join(rootxml.itertext());print('HOF_NAMED_TARGETS',{g:tx.count(g) for g in ['CSPG4','CHRNA6','PRAME']})
rows=(out/'selected-original-platform-rows.tsv').read_text().splitlines();mapping={r.split('\t')[0]:sorted(set(seg.split(' // ')[1].strip() for seg in r.split('\t')[9].split(' /// '))) for r in rows};print('ANNOTATION_GENE_SETS',mapping)
runtime={'python':platform.python_version(),'executable':sys.executable,**{x:importlib.metadata.version(x) for x in ['numpy','openpyxl','et-xmlfile']}}
print('RUNTIME',runtime)
(out/'additional-verification.json').write_text(json.dumps({'authorization_hash_matches':match,'figure_self_reference':{'recorded':f['figures'].get(fp.name),'actual':sha(fp)},'figure_hashes_match':{n:sha(fp.parent/n)==h for n,h in f['figures'].items() if n!=fp.name},'hofvander_named_target_mentions':{g:tx.count(g) for g in ['CSPG4','CHRNA6','PRAME']},'selected_probe_gene_sets':mapping,'verification_runtime':runtime},indent=2)+'\n')
