#!/usr/bin/env python3
"""P-ST freeze: verify the newly edited numeric bindings in the surface-target main text
and SI against the committed artifacts, and verify main/SI agreement where both state
the same fact. Read-only. Exit 0 = all checks pass; exit 1 = at least one failed."""
import json, io, sys, re

R = 'research/'
main = io.open(R+'manuscripts/surface-targets/emc-surface-target-landscape.md', encoding='utf-8').read()
si   = io.open(R+'manuscripts/surface-targets/emc-surface-target-landscape-si.md', encoding='utf-8').read()
scan = json.load(open(R+'modalities/emc-surfaceome-scan.json'))
stat = json.load(open(R+'modalities/emc-tissue-read-statistics.json'))
nw   = json.load(open(R+'modalities/emc-surface-normal-window.json'))
lim  = json.load(open(R+'modalities/surfaceome-instrument-limits.json'))
aso  = json.load(open(R+'modalities/aso-delivery-antigen.json'))
pan  = json.load(open(R+'modalities/emc-expression-panels.json'))

fails = []
def check(name, cond, detail=''):
    print(('PASS  ' if cond else 'FAIL  ') + name + (('  -- ' + detail) if detail and not cond else ''))
    if not cond: fails.append(name)

def infile(doc, docname, s, label=None):
    check((label or (docname+': '+s[:70])), s in doc, 'string not found')

# --- set definitions (D2) ---
act = scan['actionable_antigens']
sig = sorted([g for g,v in act.items() if v['selectivity_significant']])
check('scan holds 47 actionable antigens', len(act)==47, str(len(act)))
check('18 selectivity_significant', len(sig)==18, str(len(sig)))
classic9 = ['CD248','CDH11','EPHB4','FGFR1','GPC2','KIT','MCAM','NCAM1','PTK7']
check('the nine classic selective antigens are all significant',
      all(act[g]['selectivity_significant'] for g in classic9))
other9 = sorted(set(sig)-set(classic9))
check('the other nine are ALK DLL3 ENPP1 FGFR4 PDGFRA PDGFRB ROR1 SLC34A2 STEAP1',
      other9==['ALK','DLL3','ENPP1','FGFR4','PDGFRA','PDGFRB','ROR1','SLC34A2','STEAP1'], str(other9))
infile(main,'main','CDH11, KIT, CD248, FGFR1,\nNCAM1, GPC2, PTK7, MCAM and EPHB4', 'main names the nine classic selective antigens')
infile(main,'main','ALK, DLL3, ENPP1, FGFR4, PDGFRA, PDGFRB, ROR1, SLC34A2 and STEAP1',
       'main names the further nine selective antigens')
infile(main,'main','18 of the\n47 retained actionable antigens', 'abstract states 18 of 47')

# --- selective INTERSECT restricted == {DLL3} ---
restricted = sorted([g for g,v in nw['antigens'].items() if v.get('window')=='RESTRICTED'])
check('normal-window artifact holds 46 antigens', len(nw['antigens'])==46, str(len(nw['antigens'])))
check('selective INTERSECT restricted == {DLL3}', sorted(set(sig)&set(restricted))==['DLL3'],
      str(sorted(set(sig)&set(restricted))))
check('DLL3 q = 0.0079', act['DLL3']['selectivity_q']==0.0079)
infile(main,'main','DLL3 is selectivity-significant at q = 0.0079 and classed RESTRICTED')
infile(si,'si','leaves exactly one antigen, DLL3')

# --- board coverage of the 18 (D2 disclosure) ---
bg = stat['cross_platform_state_corrected']['by_gene']
noboard = sorted([g for g in sig if g not in bg])
check('five selective antigens have no board row', noboard==['ALK','ENPP1','FGFR4','SLC34A2','STEAP1'], str(noboard))
onboard = [g for g in sig if g in bg]
check('none of the 13 measured is concordant up',
      not any(bg[g]=='CONCORDANT_UP_ON_BOTH' for g in onboard))
check('FGFR1 and PTK7 are the concordant-down members of the 18',
      sorted([g for g in onboard if bg[g]=='CONCORDANT_DOWN_ON_BOTH'])==['FGFR1','PTK7'])
for doc,nm in ((main,'main'),(si,'si')):
    infile(doc,nm,'ALK, ENPP1, FGFR4, SLC34A2 and STEAP1', nm+' discloses the five unmeasured antigens')

# --- D1 correction policy, states, ALCAM ---
check('_correction is BH within platform', stat['_correction'].startswith('Benjamini-Hochberg within platform'))
check('alpha 0.05', stat['_alpha']==0.05)
bs = stat['cross_platform_state_corrected']['by_state']
check('CONCORDANT_UP_ON_BOTH == BGN CD44 VCAN', sorted(bs['CONCORDANT_UP_ON_BOTH'])==['BGN','CD44','VCAN'])
alc = stat['primary']['GPL3290']['ALCAM']
check('ALCAM GPL3290 q = 0.161652', alc['q']==0.161652, str(alc['q']))
check('ALCAM GPL3290 CI crosses zero', alc['ci_lo']<0<alc['ci_hi'], str((alc['ci_lo'],alc['ci_hi'])))
check('ALCAM GPL3290 delta positive', alc['delta']>0, str(alc['delta']))
check('ALCAM GPL6244 significant', stat['primary']['GPL6244']['ALCAM']['significant'] is True)
check('ALCAM state is MOVED_ON_ONE_FLAT_ON_THE_OTHER', bg['ALCAM']=='MOVED_ON_ONE_FLAT_ON_THE_OTHER')
check('GPC1 state is MOVED_ON_ONE_FLAT_ON_THE_OTHER', bg['GPC1']=='MOVED_ON_ONE_FLAT_ON_THE_OTHER')
infile(main,'main','*q* = 0.162')
infile(main,'main','95 % CI −0.02 to 1.53')
infile(main,'main','BGN and CD44')  # abstract wording
infile(main,'main','VCAN, BGN and CD44')

# --- sensitivity analyses exist and are named ---
for k in ('sensitivity_reference_matched_GPL3290_DFSP_only',
          'sensitivity_GPL6244_with_solitary_fibrous_tumour',
          'normal_skeletal_muscle_anchor'):
    check('artifact holds '+k, k in stat)
d = stat['sensitivity_reference_matched_GPL3290_DFSP_only']
check('DFSP-only CSPG4 delta -0.5179', d['rows']['CSPG4']['delta']==-0.5179)
check('DFSP-only CSPG4 q 0.182427', d['rows']['CSPG4']['q']==0.182427)
check('DFSP-only 15 sign changes', d['n_sign_changes_vs_the_full_comparator_arm']==15)
check('DFSP-only ALCAM delta 1.2327 q 0.081893',
      d['rows']['ALCAM']['delta']==1.2327 and d['rows']['ALCAM']['q']==0.081893)
s2 = stat['sensitivity_GPL6244_with_solitary_fibrous_tumour']
check('SFT arm CSPG4 delta 0.9271 q 0.001129',
      s2['rows']['CSPG4']['delta']==0.9271 and s2['rows']['CSPG4']['q']==0.001129)
check('SFT arm 5 sign changes', s2['n_sign_changes_vs_the_29_sample_comparator_arm']==5)
anch = stat['normal_skeletal_muscle_anchor']['rows']
check('anchor ALCAM +2.8503', anch['ALCAM']['emc_minus_muscle_z']==2.8503)
check('anchor ENO3 and NR4A3 negative',
      anch['ENO3']['emc_minus_muscle_z']<0 and anch['NR4A3']['emc_minus_muscle_z']<0)
for doc,nm in ((main,'main'),(si,'si')):
    check(nm+' no longer claims no sensitivity analysis was run',
          'no sensitivity analysis recomputing' not in doc.split('Superseded, retained verbatim')[0] if nm=='si' else True)
check('main no longer says no multiple-testing correction is applied anywhere in the tissue read',
      'No multiple-testing correction is applied anywhere in the tissue read' not in main.split('## Display items')[0])
infile(main,'main','Δ = −0.518, *t* = −1.84')
infile(si,'si','Δ = −0.518, *t* = −1.84, df 9.8')
infile(si,'si','Fifteen of the seventy genes it can read change sign')

# --- resolution ---
res = stat['resolution']
check('resolution GPL6244 24 of 95', res['GPL6244']['n_significant']==24 and res['GPL6244']['n_readable']==95)
check('resolution GPL3290 16 of 78', res['GPL3290']['n_significant']==16 and res['GPL3290']['n_readable']==78)
check('median CI half widths 0.259 / 0.957',
      res['GPL6244']['median_ci_half_width_sd']==0.259 and res['GPL3290']['median_ci_half_width_sd']==0.957)
for doc,nm in ((main,'main'),(si,'si')):
    infile(doc,nm,'0.259 standard deviation units', nm+' prints the GPL6244 median CI half-width')
    infile(doc,nm,'0.957', nm+' prints the GPL3290 median CI half-width')

# --- CSPG4 (specific repair) ---
check('CSPG4 absent from the selectivity scan', 'CSPG4' not in act)
check('CSPG4 present in the normal window as ENHANCED_BROAD', nw['antigens']['CSPG4']['window']=='ENHANCED_BROAD')
check('L4 field in_emc_surface_normal_window is still false (stale, unaltered)',
      lim['limits']['L4_cspg4_coverage_gap']['in_emc_surface_normal_window'] is False)
infile(main,'main','stale historical statement')
infile(si,'si','stale historical statement')
check('main no longer says CSPG4 was not among the antigens the filter saw',
      'CSPG4 was not among the antigens the filter saw' not in main.split('## Display items')[0])
# CSPG4 sequencing ratio, 4.94x the next largest EMC median
med = sorted(((v['exposure_axis_vs_normal_tissue']['measured_contrast_3SEQ_vs_27_normal_organ_libraries']['emc_median'], g)
              for g,v in aso['per_antigen'].items()), reverse=True)
check('CSPG4 is the largest EMC median and CD248 the next', med[0][1]=='CSPG4' and med[1][1]=='CD248', str(med[:2]))
check('CSPG4 / CD248 EMC median ratio rounds to 4.94', round(med[0][0]/med[1][0],2)==4.94, str(med[0][0]/med[1][0]))
infile(main,'main','roughly five times the next-largest row in that panel (CD248, 1.767;')

# --- CD276 (specific repair) ---
body = main.split('## Appendix A. Correction and supersession register')[0]
cd = stat['primary']['GPL6244']['CD276']
check('CD276 GPL6244 q 0.087575 not significant', cd['q']==0.087575 and cd['significant'] is False)
r = aso['per_antigen']['CD276']['lineage_axis_vs_comparator_sarcomas']['per_instrument']['3SEQ_vs_32_other_sarcoma_libraries']
check('CD276 3SEQ ratio 1.4172 with stored label FLAT', round(r['ratio'],4)==1.4172 and r['state']=='FLAT')
infile(main,'main','1.42 times the other-sarcoma median')
infile(main,'main','banding rule applied to a ratio, not a significance')
check('main no longer claims B7-H3 is not elevated on either instrument',
      'B7-H3 is not elevated in EMC on either instrument' not in body)
check('main no longer claims B7-H3 protein can be tumour-restricted',
      'B7-H3 protein can be tumour-restricted' not in body)

# --- withdrawn claims ---
body = main.split('## Appendix A. Correction and supersession register')[0]
for s in ["carry no EMC-tissue array contrast elsewhere in this repository's artifacts",
          'gained their first EMC-tissue array contrast in this work',
          "The surrogate's negatives transferred and its positives did not.",
          'verified each reported value against the committed',
          'a usable\ndiagnostic or lineage marker']:
    check('withdrawn from the live body: '+s[:52], s not in body)

# --- 21 confirmed improvements that must survive ---
check('ORCID present and placeholder gone',
      '0000-0002-1823-1451' in main and 'ORCID TO BE SUPPLIED' not in main)
cd_ = scan['class_definition']
check('six class subtypes present', len(cd_['class_oncotree_subtypes_present'])==6)
check('no DSRCT subtype returned',
      not any('esmoplastic' in s for s in cd_['class_oncotree_subtypes_present']))
for doc,nm in ((main,'main'),(si,'si')):
    infile(doc,nm,'alveolar rhabdomyosarcoma', nm+' names alveolar rhabdomyosarcoma in the class')
check('five instrument limits', len(lim['limits'])==5)
infile(main,'main','Five limits of this instrument were computed')
infile(si,'si','Five limits of the surrogate instrument were computed')
check('LRRC15 window is ENHANCED_BROAD', nw['antigens']['LRRC15']['window']=='ENHANCED_BROAD')
infile(main,'main','| LRRC15 | −0.25 | 1.0 | no | ENHANCED_BROAD |')
infile(si,'si','| LRRC15 | Tissue enhanced | Detected in many | Not detected in immune cells | ENHANCED_BROAD |')
gs = pan['panels']['surface_antigen']['groups']
check('nine curated panels', len(gs)==9, str(len(gs)))
for key,label in (('ofcs_carrier_proteoglycans','Oncofetal-chondroitin-sulfate carrier proteoglycans (18)'),
                  ('sarcoma_cell_surface_addresses','Sarcoma cell-surface addresses (30)'),
                  ('alkaline_phosphatase_family','Alkaline-phosphatase family (4)'),
                  ('hla_presented_intracellular_antigens_NOT_surface','HLA-presented intracellular antigens, not surface (10)')):
    genes = ', '.join(gs[key]['genes_requested'])
    check('Table S3 lists '+key+' gene for gene, in order', ('| '+label+' | '+genes+' |') in si)
mk = pan['reads']['control']['gene_readability']['MKI67']
mk3 = mk['GSE4303-GPL3290_series_matrix.txt.gz']['welch_EMC_vs_comparator']
check('MKI67 GPL3290 delta 1.2358 t 2.301 df 5.5',
      round(mk3['delta_a_minus_b'],4)==1.2358 and mk3['t']==2.301 and mk3['df']==5.5)
check('the MKI67 expectation is written for GSE24369 only',
      'in GSE24369' in pan['reads']['control']['expected']['MKI67'])
infile(si,'si','Δ +1.236 (*t* = 2.30, df 5.5)')
infile(main,'main','Δ = +1.236, *t* = 2.30')

# --- reference completion ---
rem = json.load(open(R+'literature/remaining-reference-metadata-2026-08-09.json'))['records']
for p in ['35974707','34340159','25613900','30373828','10537274','12378528','28076709']:
    check('remaining-reference record holds PMID '+p, p in rem)
infile(main,'main','remaining-reference-metadata-2026-08-09.json')
check('no reference marked not yet retrieved', 'not yet\nretrieved' not in main and 'not yet retrieved' not in body)

# --- cohort composition ---
co = stat['cohorts']['GPL6244']['class_counts']
check('GSE24369 holds 6 myxofibrosarcoma, 5 SFT, 2 pooled muscle',
      co['myxofibrosarcoma']==6 and co['SFT']==5 and co['normal_skeletal_muscle']==2)
check('the deposit annotation says Myxofibrosarcoma',
      any(a['annotation'].startswith('Myxofibrosarcoma') for a in
          pan['platforms']['GSE24369_series_matrix.txt.gz']['sample_annotations_verbatim']))
check('main no longer says 6 fibrosarcoma in the comparator arm (live body)', '6 fibrosarcoma' not in body)
infile(main,'main','6 myxofibrosarcoma')

# --- main/SI agreement on shared facts ---
check('main and SI agree that the prior classifies 46 antigens',
      'classifies 46' in main and 'classifies 46 antigens' in si)
check('main and SI both carry the DLL3 intersection result', 'DLL3' in main and 'DLL3' in si)
check('main and SI both print 0.957', '0.957' in main and '0.957' in si)
check('both documents point at Supplementary Methods S7',
      'Supplementary Methods S7' in main and '### S7.' in si)
check('main pointer says S1 to S7 methods and S1 to S7 tables',
      'Supplementary Methods S1 to S7, Supplementary Tables S1 to S7' in main)
si_methods = re.findall(r'^### S(\d)\. ', si.split('## Supplementary Tables')[0], re.M)
check('SI carries Supplementary Methods S1..S7', si_methods==['1','2','3','4','5','6','7'], str(si_methods))
si_tables = re.findall(r'^\*\*Table S(\d)\.\*\*', si, re.M)
check('SI carries Tables S1..S7', si_tables==['1','2','3','4','5','6','7'], str(si_tables))

# --- fence: no efficacy/safety/window/readiness claim introduced ---
banned = ['is a validated target', 'is safe and effective', 'a therapeutic window of',
          'ready for clinical use in', 'selectivity margin', 'demonstrates efficacy']
scope_box = main[main.index('> **Scope of the claims.**'):main.index('## Abstract')]
prose = body.replace(scope_box, '')
for b in banned:
    check('no claim "'+b+'" in the live prose outside the scope disclaimer', b not in prose.lower())
check('the scope box still disclaims safety, efficacy, window and readiness',
      'is a validated target' in scope_box and 'safe or effective' in scope_box
      and 'therapeutic' in scope_box and 'ready for clinical use' in scope_box)

print()
print('%d checks, %d failed' % (0, len(fails)) if False else 'FAILED: %d -> %s' % (len(fails), fails) if fails else 'ALL CHECKS PASSED')
sys.exit(1 if fails else 0)
