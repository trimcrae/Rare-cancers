from pathlib import Path,PurePosixPath
import copy,difflib,gzip,hashlib,io,json,subprocess,zipfile
from PIL import Image,ImageChops
from openpyxl import load_workbook
old=Path.cwd();root=Path(r'C:/Users/mcrae/.codex/worktrees/8010/EMC-Research');out=old/'review-results/focused-final-verification';p='research/autonomy/atlas-hofvander-validation-2026-09-06/';m='research/manuscripts/surface-targets/';f='research/manuscripts/figures/';rel='research/release-candidates/PUB-SURFACE-TARGETS/2026-09-06/'
pkg=Path(r'C:/Users/mcrae/.codex/review-workspaces/emc-tissue-rna-package-20260906/emc-tissue-rna-code-data-supplement-8bb8c9d.zip');met=pkg.parent/'aixiv-metadata.proposed.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def filesha(p):return sha(p.read_bytes())
def dump(n,x):(out/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert filesha(pkg)=='56e089a6b39b9d5d5140a4185987778803359ab1154d26beb882d6e6197f3ea6'
assert filesha(root/rel/'emc-tissue-rna-code-data-supplement.zip')==filesha(pkg)
assert filesha(met)=='87721750b0c7eeab04b0c7934c59719921ad90195fc70bb81fa30f88c5a2d79d'
oldmanifest=json.loads((old/'review-input-manifest.json').read_text())['files'];package_results={};members={};sourcechecks=[];locked=[];codechecked=[]
with zipfile.ZipFile(pkg) as z:
 names=z.namelist();assert len(names)==148 and len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names);assert z.testzip() is None
 inv=json.loads(z.read('FILES-SHA256.json'));assert {r['path'] for r in inv['files']}==set(names)-{'FILES-SHA256.json'}
 for r in inv['files']:
  data=z.read(r['path']);assert sha(data)==r['sha256'] and len(data)==r['bytes'];members[r['path']]={'sha256':sha(data),'bytes':len(data)}
 package_results['inventory_entries_verified']=len(inv['files']);package_results['members']=len(names)
 same=[];different=[]
 for n in set(names)&set(oldmanifest):
  if sha(z.read(n))==oldmanifest[n]['sha256']:same.append(n)
  else:different.append(n)
 expected_changed=[f+'surface-tissue-rna-figure-provenance.json',m+'emc-tissue-rna-prioritization.md',m+'plot_emc_tissue_rna.py'];assert sorted(different)==sorted(expected_changed)
 for n in different:assert z.read(n)==(root/n).read_bytes()
 package_results['unchanged_from_original_review']=sorted(same);package_results['changed_from_original_review']=different
 lock=json.loads(z.read(p+'replay/input-lock.json'))
 for n,r in lock['bundle_inputs'].items():assert sha(z.read(n))==r['sha256'];locked.append({'path':n,'sha256':r['sha256'],'kind':'bundle_input'})
 for n,h in lock['frozen_inputs'].items():assert sha(z.read(p+n))==h;locked.append({'path':p+n,'sha256':h,'kind':'frozen_input'})
 cf=json.loads(z.read(p+'replay/code-freeze.json'))
 for n,h in cf.items():assert sha(z.read(p+'replay/'+n))==h;codechecked.append({'path':p+'replay/'+n,'sha256':h})
 auth=json.loads(z.read(p+'coordinator-authorization.json'))
 for n,h in auth['sha256'].items():assert sha(z.read(p+n))==h
 hm=json.loads(z.read(p+'metadata-manifest.json'));am=json.loads(z.read(p+'replication-manifest.json'))
 hz=zipfile.ZipFile(io.BytesIO(z.read('research/autonomy/atlas-hofvander-source-2026-09-06/source-provenance.zip')));az=zipfile.ZipFile(io.BytesIO(z.read('research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip')))
 for n,r in hm['source_files'].items():
  data=gzip.decompress(z.read('research/autonomy/atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz')) if n=='source_data/tpm_matrix.tsv' else hz.read(n)
  assert sha(data)==r['sha256'];sourcechecks.append({'cohort':'Hofvander','source_member':n,'sha256':sha(data)})
 for n,r in am['source_files'].items():
  data=z.read('research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz') if n=='GSE24369.soft.gz' else az.read(n)
  assert sha(data)==r['sha256'];sourcechecks.append({'cohort':'array','source_member':n,'sha256':sha(data)})
 required=[p+x for x in ['all12-gene-effects.csv','all-hofvander-contrasts.csv','all-year-cells.csv','all-shared-histology-replication.csv','all-primary-deletions.csv','draft/normal-context.csv','results/selected-values.json','replication-results/array-values.json','protocol.md','amendment-replication-2026-09-06.md','replay/replay.py','replay/report.py','replay/requirements.txt']]
 for n in required:assert z.read(n)==(old/n).read_bytes()
 package_results['required_tables_and_replay_dependencies_unchanged']=required
 fg=json.loads(z.read(f+'surface-tissue-rna-figure-provenance.json'));oldfg=json.loads((old/f/'surface-tissue-rna-figure-provenance.json').read_text());old_removed=copy.deepcopy(oldfg);removed=old_removed['figures'].pop('surface-tissue-rna-figure-provenance.json');new_removed=copy.deepcopy(fg);correction=new_removed.pop('maintenance_correction');assert new_removed==old_removed
 assert correction['prior_record_sha256']==filesha(old/f/'surface-tissue-rna-figure-provenance.json')
 for n,h in fg['figures'].items():assert sha(z.read(f+n))==h==filesha(old/f/n)
 assert (root/rel/'figure-provenance-before-M1-repair.json').read_bytes()==(old/f/'surface-tissue-rna-figure-provenance.json').read_bytes()
 facts=json.loads(z.read('source-notes/prame-five-emc-factual-rows.json'));wb=load_workbook(old/'research/autonomy/atlas-prior-art-2026-09-06/428_2023_3606_MOESM1_ESM.xlsx',read_only=True,data_only=True)
 factscount=0
 for row in facts:
  for cell,v in row.items():assert wb.active[cell].value==v;factscount+=1
 package_results['PRAME_factual_cells_checked_against_original_workbook']=factscount
 notes=json.loads(z.read('source-notes/source-rights-and-retrieval.json'));assert notes['PRAME']['source_sha256']==filesha(old/'research/autonomy/atlas-prior-art-2026-09-06/428_2023_3606_MOESM1_ESM.xlsx')
 package_results['PRAME_original_workbook_omitted_but_exact_retrieval_URL_digest_and_factual_rows_supplied']=True
 package_results['historical_draft_unchanged']=all(sha(z.read(n))==oldmanifest[n]['sha256'] for n in names if n.startswith(p+'draft/') and n in oldmanifest)
meta=json.loads(met.read_text());md=(root/m/'emc-tissue-rna-prioritization.md').read_text();ab=md.split('## Abstract',1)[1].split('## Keywords',1)[0].strip();title=md.split('\n# ',1)[1].splitlines()[0]
assert meta['abstract']==ab and meta['title']==title
imagechecks=[]
for i in range(1,12):
 orig=old/'review-results'/(f'article-{i}.png' if i<=7 else f'si-{i-7}.png');final=out/f'final-page-{i:02d}.png';a=Image.open(orig).convert('RGB');b=Image.open(final).convert('RGB');assert a.size==b.size;diff=ImageChops.difference(a,b);bbox=diff.getbbox();imagechecks.append({'page':i,'pixel_identical':bbox is None,'difference_bbox':bbox,'image_size':a.size})
 print('PIXELS',i,bbox)
 if bbox:(diff.point(lambda v:255 if v else 0)).save(out/f'page-{i:02d}-difference.png')
for n in [m+'emc-tissue-rna-prioritization-preprint.build-stamp.json',m+'emc-tissue-rna-prioritization-supplementary-information.build-stamp.json']:
 bs=json.loads((root/n).read_text())
 for dep,h in bs['built_from'].items():assert filesha(root/'research/manuscripts'/dep)==h
bind=[m+'emc-tissue-rna-prioritization.md',m+'emc-tissue-rna-prioritization-si.md',m+'emc-tissue-rna-prioritization-preprint.pdf',m+'emc-tissue-rna-prioritization-supplementary-information.pdf',m+'emc-tissue-rna-prioritization-preprint.build-stamp.json',m+'emc-tissue-rna-prioritization-supplementary-information.build-stamp.json',m+'plot_emc_tissue_rna.py',f+'surface-tissue-rna-figure-provenance.json',rel+'emc-tissue-rna-prioritization-submission.pdf',rel+'emc-tissue-rna-code-data-supplement.zip',rel+'figure-provenance-before-M1-repair.json',rel+'review-repair-disposition.json',rel+'final-pdf-build-receipt.json',rel+'outgoing-pdf-verification.json','research/manuscripts/build_submission_pdf.py']+[f+n for n in fg['figures']]
bindings=[{'path':n,'sha256':filesha(root/n),'bytes':(root/n).stat().st_size} for n in bind]
bindings.extend([{'path':str(pkg),'sha256':filesha(pkg),'bytes':pkg.stat().st_size},{'path':str(met),'sha256':filesha(met),'bytes':met.stat().st_size}])
result={'status':'passed','source_checkpoint':'8bb8c9d2945f2ae68a60455ebd0eef4ee2fb0e0b','artifact_candidate_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'package_results':package_results,'replay_locks_checked':locked,'code_freeze_checked':codechecked,'eight_scientific_authorization_hashes_match':True,'source_member_checks':sourcechecks,'M1':{'fixed':True,'historical_record_preserved':True,'six_figure_bytes_identical':True,'original_generation_provenance_unchanged':True},'metadata_title_abstract_exact':True,'rendered_pixel_checks':imagechecks,'artifact_bindings':bindings,'package_inventory':members}
dump('verification.json',result)
print(json.dumps({'status':result['status'],'package_members':len(members)+1,'locked_inputs':len(locked),'code_freeze_files':len(codechecked),'source_members':len(sourcechecks),'M1':result['M1'],'unchanged_packaged_review_files':len(same),'changed_packaged_review_files':different,'metadata_title_abstract_exact':True,'candidate_commit':result['artifact_candidate_commit']},indent=2))
