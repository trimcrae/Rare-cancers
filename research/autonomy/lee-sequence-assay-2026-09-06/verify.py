import json,hashlib,pathlib,subprocess,sys,re
D=pathlib.Path(__file__).parent;S=D.parent/'fusion-partial-benchmark-2026-09-05'
manifest=json.loads((S/'inputs/input-manifest.json').read_text());verified=[]
for item in manifest['sources']+manifest['members']:
 p=S/'inputs'/item['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'];verified.append(item['file'])
for item in json.loads((D/'retrievals.json').read_text()):
 if 'sha256' in item: assert hashlib.sha256((D/'inputs'/item['file']).read_bytes()).hexdigest()==item['sha256']
primer_text=(S/'inspections/crt-2022-910-Supplementary-Table-3.txt').read_text()
for row in json.loads((D/'primer-mappings.json').read_text()):
 assert row['forward_5to3'] in primer_text and row['reverse_5to3'] in primer_text
# Article references, source exon boundaries, full matches, and retained outcome counts.
assert 'exon            2270..2380' in (D/'inputs/NM_058243.2.gb').read_text()
assert 'exon            483..1191' in (D/'inputs/NM_001284292.2.gb').read_text()
rows=json.loads((D/'design-mappings-and-outcomes.json').read_text());assert len({r['design_id'] for r in rows})==31
assert all([o['endpoint'] for o in r['outcomes']]==['measured_parent','fusion','second_parent'] for r in rows)
assert sum(bool(o['relative_expression_mean']) for r in rows for o in r['outcomes'] if o['endpoint']=='fusion')==31
assert sum(bool(o['relative_expression_mean']) for r in rows for o in r['outcomes'] if o['endpoint']=='second_parent')==0
# Reproduction determinism for computation outputs.
names=['junctions.json','references.fasta','primer-mappings.json','design-mappings-and-outcomes.json','design-mappings.csv','checks.json'];before={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in names}
r=subprocess.run([sys.executable,str(D/'analyze.py')],capture_output=True,text=True);assert r.returncode==0,r.stderr
assert before=={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in names}
result={'status':'passed','scope':'input integrity, primer transcription against retained searchable source, exon boundaries, 31 design / 93 endpoint coverage (31 missing second parent), deterministic rerun','inherited_sources_hash_verified':verified,'deterministic_outputs':before,'not_run':'whole repository preflight or publication gates; sparse worker checkpoint, no commit','independent_review':'not performed by this worker; coordinator pending'}
(D/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
