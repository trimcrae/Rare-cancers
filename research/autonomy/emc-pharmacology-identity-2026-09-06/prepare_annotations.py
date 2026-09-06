import csv,datetime,hashlib,json,pathlib
P=pathlib.Path(__file__).parent
S=P.parent/'ncc-screen-source-2026-09-06'
rows=list(csv.DictReader((S/'screen.csv').open(encoding='utf-8-sig')))
notes={
'179324-69-7':dict(active_moiety='bortezomib',chemical_family='peptide_boronic_acid',role='confirmed_proteasome_direct',preparation='bortezomib',sources=['velcade.html'],note='A distinct compound, sharing the boronic-acid family with ixazomib; not an independent biological model.'),
'868540-17-4':dict(active_moiety='carfilzomib',chemical_family='peptide_epoxyketone',role='confirmed_proteasome_direct',preparation='carfilzomib',sources=['kyprolis.html'],note='Distinct epoxyketone family.'),
'1072833-77-2':dict(active_moiety='ixazomib',chemical_family='peptide_boronic_acid',role='confirmed_proteasome_direct',preparation='active ixazomib/MLN2238',sources=['ninlaro.html'],note='Active compound; do not count citrate prodrug as another independent active moiety.'),
'1239908-20-3':dict(active_moiety='ixazomib',chemical_family='peptide_boronic_acid',role='confirmed_proteasome_prodrug',preparation='ixazomib citrate, documented boronic ester prodrug',sources=['ninlaro.html','identity-search-evidence.json','pubchem-56844015.json'],note='Regulatory citrate identity matches CAS; hydrolysis to active ixazomib documented under physiological conditions, not measured in NCC wells.'),
'1201902-80-8':dict(active_moiety=None,chemical_family=None,role='unresolved_proteasome_candidate_identity',preparation='source-labelled Ixazomib Citrate (MLN9708)',sources=['identity-search-evidence.json','pubchem-49867936.json','pubchem-56844015.json'],note='PubChem CID49867936 differs in connectivity from regulatory citrate CID56844015. Source screen labels citrate/MLN9708 whereas IC50 table calls it Ixazomib. Purchased compound identity and equivalence unresolved; only a sensitivity may assign it to ixazomib.')
}
# Explicit source-name candidate group audit, not chemical equivalence inference.
candidates={
'abemaciclib':['1231929-97-7','1231930-82-7'], 'afatinib':['439081-18-2','850140-73-7'],
'bendamustine':['16506-27-7','3543-75-7'], 'cabozantinib':['849217-68-1','1140909-48-3'],
'ceritinib':['1032900-25-6','1380575-43-8'], 'crizotinib':['1374356-45-2','877399-52-5','1415560-69-8'],
'cyclophosphamide':['50-18-0','6055-19-2'], 'dabrafenib':['1195765-45-7','1195768-06-9'],
'dasatinib':['302962-49-8','854001-07-3'], 'doxorubicin':['23214-92-8','25316-40-9'],
'enasidenib':['1446502-11-9','1650550-25-6'], 'erlotinib':['183321-74-6','183319-69-9'],
'fludarabine':['21679-14-1','75607-67-9'], 'gefitinib':['184475-35-2','184475-55-6'],
'gemcitabine':['95058-81-4','122111-03-9'], 'imatinib':['152459-95-5','220127-57-1'],
'irinotecan':['97682-44-5','136572-09-3','100286-90-6'], 'ixazomib':['1072833-77-2','1239908-20-3','1201902-80-8'],
'lapatinib':['231277-92-2','388082-77-7'], 'larotrectinib':['1223403-58-4','1223405-08-0'],
'lenvatinib':['417716-92-8','857890-39-2'], 'megestrol':['3562-63-8','595-33-5'],
'nilotinib':['641571-10-0','923288-95-3','923288-90-8'], 'niraparib':['1038915-60-4','1038915-73-9'],
'palbociclib':['571190-30-2','827022-32-2','827022-33-3'], 'pazopanib':['444731-52-6','635702-64-6'],
'pemetrexed':['137281-23-3','150399-23-8'], 'raloxifene':['84449-90-1','82640-04-8'],
'regorafenib':['755037-03-7','835621-07-3','1019206-88-2'], 'ribociclib':['1211441-98-3','1211443-80-9','1374639-75-4'],
'rucaparib':['283173-50-2','459868-92-9','1859053-21-6'], 'sorafenib':['284461-73-0','475207-59-1'],
'sotorasib':['2296729-00-3','2252403-56-6'], 'sunitinib':['557795-19-4','341031-54-7'],
'TAS-102/components':['733030-01-8','183204-72-0'], 'tamoxifen':['10540-29-1','54965-24-1'],
'folinate stereochemistry':['6035-45-6','80433-71-2'], 'topotecan':['123948-87-8','119413-54-6']}
roster=[]
for r in rows:
 d=dict(cas=r['cas'],source_name=r['source_name'],source_row=int(r['source_row']),role='not_identified_as_primary_proteasome_direct_in_bounded_review',active_moiety=None,chemical_family=None,preparation=None,sources=[],note='Full source-name roster read semantically; no complete off-target taxonomy or proof of absent secondary proteasome effects.')
 d.update(notes.get(r['cas'],{}));d['name_group_candidates']=[k for k,v in candidates.items() if r['cas'] in v];roster.append(d)
(P/'identity-roster.json').write_text(json.dumps(roster,indent=2)+'\n')
relationships=[dict(group=k,cas=v,status='source_name_candidate_only_no_collapse',note='Name similarity does not resolve salts, esters, stereoisomers, hydration or mixtures.') for k,v in candidates.items()]
for r in relationships:
 if r['group']=='doxorubicin':r.update(status='source_backed_hydrochloride_relationship',source='doxorubicin.html',note='Label explicitly identifies hydrochloride CAS25316-40-9; source pair retained separately, no equal-exposure assumption.')
 if r['group']=='niraparib':r.update(status='source_backed_tosylate_active_moiety_relationship',source='identity-search-evidence.json',note='FDA GSRS gives niraparib as active moiety of CAS1038915-73-9; no equal-exposure assumption.')
 if r['group']=='ixazomib':r.update(status='one_confirmed_prodrug_relationship_one_unresolved_identity',source='identity-roster.json',note='Two CAS citrate entries must not be silently equated; see exact records.')
(P/'related-entry-candidates.json').write_text(json.dumps(relationships,indent=2)+'\n')
freeze=dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),agent='/root/independent_emc_reader',base_revision='b79868c1adb422098e565cf62418e45b35773c2e',reasoning_effort='medium requested/inherited; no runtime introspection',model='not programmatically exposed',permissions='approval never; danger-full-access',retrospective=True,screen_rows_read=221,files={str(p.relative_to(P.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'protocol.md',P/'identity-roster.json',P/'related-entry-candidates.json',S/'screen.csv',S/'ic50.csv']})
(P/'analysis-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
print('Frozen identity roster and retrospective protocol before rank calculations.')
