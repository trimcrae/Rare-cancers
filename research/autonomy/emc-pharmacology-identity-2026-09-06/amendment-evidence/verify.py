import csv,decimal,hashlib,json,pathlib,xml.etree.ElementTree as ET,zipfile
P=pathlib.Path('C:/Users/mcrae/.codex/worktrees/emc-pharmacology-identity-20260906/EMC-Research/research/autonomy/emc-pharmacology-identity-2026-09-06')
OUT=pathlib.Path(__file__).resolve().parent
D=decimal.Decimal
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def table(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def ranks(vals):
    positions={}
    for rank,(key,value) in enumerate(sorted(vals.items(),key=lambda t:t[1]),1):positions.setdefault(value,[]).append(rank)
    return {key:D(sum(positions[value]))/len(positions[value]) for key,value in vals.items()}
def sheet(p):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(p) as z:
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        parsed={}
        for r in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:row',ns):
            row={}
            for c in r.findall('m:c',ns):
                v=c.find('m:v',ns);value=v.text if v is not None else ''.join(c.itertext());row[c.attrib['r']]=ss[int(value)] if c.attrib.get('t')=='s' else value
            parsed[int(r.attrib['r'])]=row
        return parsed
rows=table(P/'source-screen.csv');follow=table(P/'source-ic50.csv');published=table(P/'ranked-screen.csv')
assert len(rows)==len(published)==221 and len(follow)==24 and len({r['cas'] for r in rows})==221
means={r['cas']:D(r['cell_viability_percent']) for r in rows};stress={r['cas']:means[r['cas']]+D(r['reported_sd_percent']) for r in rows}
mr=ranks(means);sr=ranks(stress)
assert ranks({'a':D(1),'b':D(1),'c':D(2)})=={'a':D('1.5'),'b':D('1.5'),'c':D(3)}
rank_differences=[{'cas':r['cas'],'source_name':r['source_name'],'decimal_mean_rank':str(mr[r['cas']]),'worker_mean_rank':r['mean_midrank'],'decimal_stress_rank':str(sr[r['cas']]),'worker_stress_rank':r['mean_plus_sd_midrank'],'exact_stress':str(stress[r['cas']]),'worker_stress':r['mean_plus_sd']} for r in published if mr[r['cas']]!=D(r['mean_midrank']) or sr[r['cas']]!=D(r['mean_plus_sd_midrank'])]
print('RANK_DIFFERENCES',json.dumps(rank_differences))
float_sr=ranks({r['cas']:float(r['cell_viability_percent'])+float(r['reported_sd_percent']) for r in rows})
assert all(mr[r['cas']]==D(r['mean_midrank']) and float_sr[r['cas']]==D(r['mean_plus_sd_midrank']) for r in published)
src=P.parent/'ncc-screen-source-2026-09-06';assert sha(P/'source-screen.csv')==sha(src/'screen.csv') and sha(P/'source-ic50.csv')==sha(src/'ic50.csv')
catalogue=sheet(src/'sources/NCC-MOESM4.xlsx');s5=sheet(src/'sources/NCC-MOESM5.xlsx');s6=sheet(src/'sources/NCC-MOESM6.xlsx')
for r in rows:
    n=int(r['source_row']);v=s5[n]
    assert v['A'+str(n)]==r['cas'] and v['B'+str(n)]==r['source_name']
    for source,field in [('C','cell_viability_percent'),('D','reported_sd_percent')]:assert float(v[source+str(n)])==float(r[field])
for r in follow:
    n=int(r['source_row']);v=s6[n]
    assert v['A'+str(n)]==r['cas'] and v['B'+str(n)]==r['source_name'] and float(v['C'+str(n)])==float(r['ic50_nM'])
candidate_cas=['179324-69-7','868540-17-4','1072833-77-2','1239908-20-3','1201902-80-8'];candidate=[]
for cas in candidate_cas:
    r=next(r for r in rows if r['cas']==cas);n=int(r['source_row']);c=catalogue[n]
    candidate.append({'cas':cas,'source_row':n,'source_name':r['source_name'],'mean_rank':float(mr[cas]),'stress_rank':float(sr[cas]),'catalogue':c['A'+str(n)],'provider':c['F'+str(n)],'source_target':c['D'+str(n)],'source_pathway':c['E'+str(n)],'ic50_rows':[r for r in follow if r['cas']==cas]})
groups={'bortezomib':['179324-69-7'],'carfilzomib':['868540-17-4'],'ixazomib_confirmed':['1072833-77-2','1239908-20-3']}
worst={k:{'mean':float(max(mr[c] for c in v)),'stress':float(max(sr[c] for c in v))} for k,v in groups.items()}
assert worst=={'bortezomib':{'mean':15.,'stress':19.},'carfilzomib':{'mean':24.,'stress':17.},'ixazomib_confirmed':{'mean':17.,'stress':12.}}
quartile=D(221)/4
families={'boronic_lineage':['179324-69-7','1072833-77-2','1239908-20-3'],'epoxyketone':['868540-17-4']}
leave={k:{'remaining_preparations':len([c for kk,v in families.items() if kk!=k for c in v]),'remaining_low_quartile':sum(mr[c]<=quartile for kk,v in families.items() if kk!=k for c in v),'remaining_families':1} for k in families}
ambiguous='1201902-80-8';sens={'group_with_ixazomib_worst_mean':float(max(mr[c] for c in groups['ixazomib_confirmed']+[ambiguous])),'group_with_ixazomib_worst_stress':float(max(sr[c] for c in groups['ixazomib_confirmed']+[ambiguous])),'all_five_mean_low_quartile':all(mr[c]<=quartile for c in candidate_cas),'all_five_stress_low_quartile':all(sr[c]<=quartile for c in candidate_cas)}
missing=[p.name for p in P.glob('*.md') if not p.read_text(encoding='utf-8').startswith('---\n')]
manifest=json.loads((P/'file-manifest.json').read_text());bad=[n for n,v in manifest['files'].items() if sha(P/n)!=v['sha256']]
out={'arithmetic_passed':True,'worker_analyze_imported':False,'source_workbooks_checked':3,'all_221_mean_and_binary64_stress_ranks_match':True,'decimal_stress_sensitivity_differences':rank_differences,'decimal_sensitivity_changes_key_candidates_or_quartile':False,'source_values_names_and_cas_match_workbooks':True,'quartile':str(quartile),'candidates':candidate,'confirmed_group_worst':worst,'leave_family_out':leave,'sensitivity':sens,'rows_outside_zero_to_100':sum(not 0<=v<=100 for v in means.values()),'missing_frontmatter':missing,'worker_manifest_mismatches':bad,'source_field_notes':['MOESM5 title explicitly says cell viability (%), columnD says SD (standard deviation). Report percentage-point interpretation is appropriate; not a confidence interval.','MOESM6 CAS1201902-80-8 is named Ixazomib at row18; preserved faithfully by CSV and worker result, but cannot be substituted for active ixazomib CAS1072833-77-2.','MOESM4 has vendor/catalogue fields already: missing-vendor-catalogue residual claim is incorrect.','PubChem JSON property key is ConnectivitySMILES; worker report calls it connectivity SMILES, correctly.'],'inspected_hashes':{str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file()}}
(OUT/'arithmetic-source-verification.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['arithmetic_passed','candidates','confirmed_group_worst','leave_family_out','sensitivity','missing_frontmatter','worker_manifest_mismatches']},indent=2))
