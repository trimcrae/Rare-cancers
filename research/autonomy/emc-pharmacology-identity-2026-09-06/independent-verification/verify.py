"""Focused repaired-file comparison only; no worker imports, rank rerun or network."""
import csv,hashlib,io,json,pathlib,zipfile
P=pathlib.Path('C:/Users/mcrae/.codex/worktrees/emc-pharmacology-identity-20260906/EMC-Research/research/autonomy/emc-pharmacology-identity-2026-09-06')
O=pathlib.Path(__file__).resolve().parent
PRE=O.parent/'emc-pharmacology-independent'
def sha(b):return hashlib.sha256(b).hexdigest()
def readj(p):return json.loads(p.read_text(encoding='utf-8'))
archive=readj(P/'original-2026-09-06/archive-manifest.json');prior=readj(PRE/'arithmetic-source-verification.json')['inspected_hashes']
prior={k.replace('\\','/'):v for k,v in prior.items()}
zpath=P/'original-2026-09-06/frozen-packet.zip';assert sha(zpath.read_bytes())==archive['zip_sha256']
with zipfile.ZipFile(zpath) as z:
    old={n:z.read(n) for n in z.namelist()}
assert len(old)==len(archive['files'])==26 and set(old)==set(archive['files'])
assert all(sha(b)==archive['files'][n]==prior[n] for n,b in old.items()),'original reviewed byte drift'
changed=[n for n,b in old.items() if (P/n).read_bytes()!=b]
assert set(changed)=={'protocol.md','report.md','file-manifest.json'}
protocol=(P/'protocol.md').read_bytes();start=protocol.index(b'# Retrospective NCC chemical-identity analysis: frozen rules')
prefix,body=protocol[:start],protocol[start:]
assert body.replace(b'\r\n',b'\n').strip()==old['protocol.md'].replace(b'\r\n',b'\n').strip()
assert prefix.splitlines()[0]==b'---'
assert b'Display wrapper only' in prefix
original=json.loads(old['result.json']);amended=readj(P/'amended-result.json')
assert original['descriptive_complete_family_claim_supported'] is False
assert amended['original_stop_rule_disposition']['checks']==original['stop_rule_checks']
assert amended['original_stop_rule_disposition']['reason']==original['stop_reason']
assert amended['validated_mechanism_completeness'] is False
assert amended['unresolved_active_moiety_analogue_preparations']==1 and amended['confirmed_active_moieties']==3
def csvbytes(b):return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
before=csvbytes(old['ranked-screen.csv']);after=csvbytes((P/'amended-ranked-screen.csv').read_bytes())
unchanged=['source_row','cas','source_name','cell_viability_percent','reported_sd_percent','mean_midrank','mean_plus_sd','mean_plus_sd_midrank','rank_denominator','reported_ic50_nM','ic50_source_name']
assert len(before)==len(after)==221
assert all(all(a[k]==b[k] for k in unchanged) for a,b in zip(before,after))
allowed_existing_changes={'role','active_moiety','chemical_family'}
assert all(all(a[k]==b[k] for k in a if k not in allowed_existing_changes) for a,b in zip(before,after))
assert all(a['active_moiety']==b['active_moiety'] for a,b in zip(before,after))
roster=readj(P/'amended-identity-roster.json');ann={r['cas']:r for r in roster}
special=ann['1201902-80-8']
assert special['role']=='source_annotated_proteasome_analogue' and special['active_moiety'] is None
assert special['catalogue_id']=='S2181' and special['provider']=='Selleck  Chemicals'
assert ann['1239908-20-3']['catalogue_id']=='S4432' and ann['1072833-77-2']['catalogue_id']=='S2180'
assert 'not a fourth validated active moiety' in special['note']
change=readj(P/'annotation-change.json');assert change['before']==next(r for r in json.loads(old['identity-roster.json']) if r['cas']=='1201902-80-8') and change['after']==special
for n in ['supplier-web-evidence.json','supplier-locators.json','arithmetic-source-verification.json','verify.py']:
    assert (P/'amendment-evidence'/n).read_bytes()==(PRE/n).read_bytes(),n
assert (P/'amendment-evidence/NCC-MOESM4.xlsx').read_bytes()==(P.parent/'ncc-screen-source-2026-09-06/sources/NCC-MOESM4.xlsx').read_bytes()
candidates=amended['proteasome_candidates'];cut=amended['quartile_midrank_cutoff']
assert cut==original['quartile_midrank_cutoff']==221/4 and amended['denominator_preparations']==221
assert {r['cas'] for r in roster if r['source_target']=='Proteasome'}=={r['cas'] for r in candidates}
assert len(candidates)==5 and amended['source_annotated_proteasome_preparations']==5 and amended['confirmed_proteasome_preparations']==4
assert amended['active_moieties']==original['active_moieties']
checks={'all_confirmed_moiety_worst_ranks_in_lowest_quartile':all(g['worst_mean_rank']<=cut for g in amended['active_moieties']),
        'at_least_two_confirmed_chemical_families':len({r['chemical_family'] for r in candidates})>=2,
        'no_unresolved_candidate_identity_affecting_complete_membership':all(r['catalogue_id'] and r['source_target']=='Proteasome' and r['chemical_family'] for r in candidates),
        'leave_each_family_out_retains_lowest_quartile_observation':all(any(r['chemical_family']!=f['chemical_family'] and r['mean_midrank']<=cut for r in candidates) for f in amended['chemical_families'])}
assert checks==amended['stop_rule_checks'] and all(checks.values()) and amended['descriptive_complete_family_claim_supported']
for f in amended['chemical_families']:
    matching=[r for r in candidates if r['chemical_family']==f['chemical_family']]
    other=[r for r in candidates if r['chemical_family']!=f['chemical_family']]
    assert f['worst_rank']==max(r['mean_midrank'] for r in matching)
    assert f['leave_family_out_remaining_low_quartile']==sum(r['mean_midrank']<=cut for r in other)
    assert len({r['chemical_family'] for r in other})==f['leave_family_out_remaining_families']==1
assert amended['followup']==original['followup']
current_manifest=readj(P/'file-manifest.json');bad=[n for n,v in current_manifest['files'].items() if sha((P/n).read_bytes())!=v['sha256']];assert not bad
md=[p.name for p in P.glob('*.md') if p.read_bytes().splitlines()[0]!=b'---'];assert not md
out={'focused_verification_passed':True,'reviewed_packet':str(P),'original_archive_file_count':26,'original_bytes_match_previous_independent_review':True,'changed_original_top_level_files':changed,'protocol_original_bytes_preserved_in_archive':True,'protocol_display_text_unchanged':True,'protocol_display_byte_note':'Wrapper normalizes line endings and adds trailing whitespace; frozen original body remains byte-exact in archive. No rule wording changes.','all_221_measurement_name_rank_and_ic50_mapping_fields_unchanged':True,'copied_independent_supplier_sources_identical':True,'source_identity_resolved_as_catalogue_analogue':True,'unresolved_active_moiety_analogue':True,'no_added_confirmed_active_moiety':True,'independent_application_of_original_descriptive_conditions':checks,'descriptive_pass':True,'validated_mechanism_completeness':False,'current_manifest_verified':True,'missing_frontmatter':md,'findings':[],'disposition':'Accept the focused repair for bounded source-annotated two-family consistency; not publication or mechanistic validation.','scope':'Read changed annotations/report/amendments and original archive; byte and derived-set comparisons only. No worker scripts imported/executed, no rank rerun, no network, no tracked edits, preflight or mail.','reviewed_file_hashes':{p.relative_to(P).as_posix():sha(p.read_bytes()) for p in sorted(P.rglob('*')) if p.is_file()}}
(O/'verification.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='reviewed_file_hashes'},indent=2))
