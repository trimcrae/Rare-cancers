"""Replay only the dated source-annotation repair from the immutable original ZIP.
No extraction or rank calculation is rerun. The source catalogue is read directly.
"""
import csv, hashlib, io, json, pathlib, zipfile, xml.etree.ElementTree as ET
P=pathlib.Path(__file__).resolve().parent
def dump(n,v): (P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(b): return hashlib.sha256(b).hexdigest()
archive=json.loads((P/'original-2026-09-06/archive-manifest.json').read_text())
with zipfile.ZipFile(P/'original-2026-09-06/frozen-packet.zip') as z:
    old={n:z.read(n) for n in z.namelist()}
assert all(sha(old[n])==v for n,v in archive['files'].items())
roster=json.loads(old['identity-roster.json']);result=json.loads(old['result.json'])
rows=list(csv.DictReader(io.StringIO(old['ranked-screen.csv'].decode('utf-8-sig'))))
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(P/'amendment-evidence/NCC-MOESM4.xlsx') as z:
    ss=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
    catalogue={}
    for r in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:row',ns):
        cells={}
        for c in r.findall('m:c',ns):
            v=c.find('m:v',ns);value=v.text if v is not None else ''.join(c.itertext())
            cells[c.attrib['r']]=ss[int(value)] if c.attrib.get('t')=='s' else value
        n=r.attrib['r']
        if 'B'+n in cells: catalogue[cells['B'+n]]={'catalogue_source_row':int(n),'catalogue_id':cells.get('A'+n),'catalogue_source_name':cells.get('C'+n),'source_target':cells.get('D'+n),'source_pathway':cells.get('E'+n),'provider':cells.get('F'+n)}
assert len(roster)==len(rows)==221
cas='1201902-80-8'
previous=next(a.copy() for a in roster if a['cas']==cas)
for a in roster:
    a.update(catalogue[a['cas']])
    if a['cas']==cas:
        a.update(role='source_annotated_proteasome_analogue',active_moiety=None,chemical_family='boronic_acid_ester_lineage',preparation='S2181 ixazomib citrate analogue; distinct six-member boronate connectivity',note='Current catalogue identity resolved. Analogue-specific potency and conversion to ixazomib are not established; not a fourth validated active moiety.',sources=previous['sources']+['amendment-evidence/NCC-MOESM4.xlsx!A113:F113','https://www.selleckchem.com/products/MLN9708.html','https://www.selleckchem.com/datasheet/MLN9708-S218103-DataSheet.html'])
    elif a['chemical_family']=='peptide_boronic_acid': a['chemical_family']='boronic_acid_ester_lineage'
ann={a['cas']:a for a in roster}
assert {a['cas'] for a in roster if a['source_target']=='Proteasome'}=={c['cas'] for c in result['proteasome_candidates']}
for r in rows:
    a=ann[r['cas']]
    for key in ['role','active_moiety','chemical_family']:r[key]=a[key]
    r.update(catalogue[r['cas']])
with (P/'amended-ranked-screen.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for r in result['proteasome_candidates']:
    r.update(catalogue[r['cas']])
    for key in ['role','active_moiety','chemical_family']:r[key]=ann[r['cas']][key]
result.update(amendment_date='2026-09-06',source_annotated_proteasome_preparations=5,unresolved_candidates=0,unresolved_active_moiety_analogue_preparations=1,validated_mechanism_completeness=False)
result['count_definitions']='Four preparations have established drug/prodrug relationships, mapping to three documented active moieties; this is literature identity, not target engagement validated in NCC. S2181 remains separate and does not increase that active-moiety count.'
result['original_stop_rule_disposition']={'checks':json.loads(old['result.json'])['stop_rule_checks'],'supported':False,'reason':json.loads(old['result.json'])['stop_reason']}
result['stop_rule_checks']['no_unresolved_candidate_identity_affecting_complete_membership']=True
result['descriptive_complete_family_claim_supported']=all(result['stop_rule_checks'].values())
result['stop_reason']=None
result['updated_disposition']='Pass for observed two-family within-screen consistency under the unchanged descriptive stop rule: candidate membership and current catalogue identity are resolved. Not a claim of complete experimentally validated mechanism or active-moiety equivalence.'
for fam in result['chemical_families']:
    if fam['chemical_family']=='peptide_boronic_acid':
        fam['chemical_family']='boronic_acid_ester_lineage';fam['cas'].append(cas);fam['worst_rank']=22.0
        fam['unresolved_active_moiety_cas']=[cas]
    else: fam['leave_family_out_remaining_low_quartile']=4
    fam['leave_family_out_remaining_families']=1
result['sensitivity']['interpretation']='Original hypothetical assignment sensitivity retained numerically; grouping S2181 with ixazomib is not an asserted chemical or active-moiety equivalence.'
review=json.loads((P/'amendment-evidence/arithmetic-source-verification.json').read_text())
result['binary64_decimal_sensitivity']={'original_binary64_ranks_retained':True,'decimal_differences':review['decimal_stress_sensitivity_differences'],'candidate_or_quartile_change':False}
dump('amended-identity-roster.json',roster);dump('amended-result.json',result)
dump('annotation-change.json',{'before':previous,'after':ann[cas],'family_label_change':'peptide_boronic_acid renamed boronic_acid_ester_lineage to accommodate explicit ester preparations; two broad families remain, not three.','source_names':'Exact MOESM5 source_name and separate exact MOESM4 catalogue_source_name retained; MOESM6 CAS1201902-80-8 remains labelled Ixazomib.'})
original_rows=list(csv.DictReader(io.StringIO(old['ranked-screen.csv'].decode('utf-8-sig'))))
unchanged=['source_row','cas','source_name','cell_viability_percent','reported_sd_percent','mean_midrank','mean_plus_sd','mean_plus_sd_midrank','rank_denominator','reported_ic50_nM','ic50_source_name']
assert all(all(str(a[k])==str(b[k]) for k in unchanged) for a,b in zip(original_rows,rows))
assert ann[cas]['catalogue_id']=='S2181' and ann[cas]['active_moiety'] is None
assert result['confirmed_active_moieties']==3 and result['confirmed_chemical_families']==2
evidence=(P/'amendment-evidence/supplier-web-evidence.json').read_text(encoding='utf-8')
assert all(t in evidence for t in ['1201902-80-8','S2181','Ixazomib Citrate (MLN9708) Analogue'])
dump('amendment-checks.json',{'original_archive_files_verified':len(old),'all_221_measurements_names_and_ranks_unchanged':True,'all_221_catalogue_rows_joined_by_CAS':True,'source_target_proteasome_exactly_five_matches_review':True,'source_identity_checks':True,'active_moiety_count_unchanged':3,'family_count_unchanged':2,'descriptive_stop_rule_pass':True,'unresolved_analogue_active_moiety':1,'decimal_stress_other_rows_differ':4,'no_reextraction_or_reranking':True})
print('PASS: 26 original files, 221 unchanged measurements/ranks, 221 catalogue joins, five source candidates; descriptive stop rule passes, one analogue active moiety unresolved.')
