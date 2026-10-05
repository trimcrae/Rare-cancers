#!/usr/bin/env python3
"""Replay selected identity/preparation methods; no expression matrices or new outcomes."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/Rare-cancers/research/autonomy')
PEER = Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing')
INPUTS = {
    'brenca_primary': (PEER/'intron_retention_gate/raw/Brenca2019-primary.xml', 'e453b80e71292bb19c1f3287d08108bef44e7a0e88207e6f99bbd3a52a010b68', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6766969/fullTextXML', True),
    'brenca_prior_evaluation': (ROOT/'fresh-discovery-2026-10-04-round7/fusion_transcripts/brenca-source-evaluation.json', None, None, False),
    'brenca_condition_coverage': (ROOT/'fresh-discovery-2026-10-05-round9/rna_processing/intron_retention_gate/ALL-NATIVE-CONDITIONS-COVERAGE.json', None, None, False),
    'brenca_library_methods': (ROOT/'fresh-discovery-2026-10-05-round9/rna_processing/intron_retention_gate/PRIMARY-LIBRARY-METHOD-OBSERVATIONS.json', None, None, False),
    'tempo_primary': (ROOT/'peerj21497-source-2026-09-06/article.xml', '2d9a6ee4ed417860867eb954e0b0a4fa3fa3042787f5af3c0a1fea9bb5fbe768', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13374579/fullTextXML', False),
    'tempo_prior_methods': (ROOT/'tmem266-tissue-2026-10-03/peerj-methods-receipt.json', None, None, False),
    'tempo_prior_cohort': (ROOT/'fresh-discovery-2026-10-04-round3/small_rna/peerj-cohort-reuse.json', None, None, False),
    'culture_context_freeze': (ROOT/'fresh-discovery-2026-10-05-round8/microenvironment/AMENDMENT-07-CULTURE-CONTEXT-FREEZE.json', None, None, False),
    'context_source_bindings': (ROOT/'fresh-discovery-2026-10-05-round8/microenvironment/SOURCE-CONTEXT-BINDINGS.json', None, None, False),
    'davila_census': (ROOT/'tmem266-all-cultures-2026-10-04/davila-census.json', 'e0df07ea33fb0f280680ecd677fae5fdfbf5ec6b2db3ad119b07df2a3b73b23d', None, False),
    'owner_prospective_plan': (PEER/'native_culture_fidelity_gate/PLAN.json', '5524422294d296a11c268e78de5f24c63e2b4e54928efea8cde068a2ddecb33d', None, False),
    'bangerter_culture_primary': (PEER/'native_culture_fidelity_gate/raw/PMC9813045.xml', '2998de01bf31d3b3793dd300b7856545168b40e569fbee4f200e53c394a0a657', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/fullTextXML', True),
    'planas_culture_primary': (PEER/'native_culture_fidelity_gate/raw/PMC10086583.xml', 'f7ab34c0ab6537519694e7d1214146ce7e5a27c71f1f06ac5343e08cd2b19dce', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10086583/fullTextXML', True),
    'GSE221532_metadata_original': (PEER/'native_culture_fidelity_gate/raw/GSE221532-family-metadata.txt', '71f01cf80b6db0024c63c3a8770a3fc7ec9b3be8932127adc520ab254056894b', 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE221532&targ=self&form=text&view=full', True),
    'GSE221532_owner_metadata_roster': (PEER/'native_culture_fidelity_gate/GSE221532-IDENTITY-CONDITION-ROSTER.json', 'b54b0a94261dfe3e17893d570bd39f825012a9ed54c1d155d7fb28312e2cfe2d', None, False),
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def compact(el):
    return ' '.join(' '.join(el.itertext()).split())

def title(sec):
    t = sec.find('title')
    return compact(t) if t is not None else ''

bindings = []
for name, (path, expected, url, cache) in INPUTS.items():
    actual = sha(path)
    if expected:
        assert actual == expected, (name, expected, actual)
    bindings.append({'name': name, 'path': str(path), 'bytes': path.stat().st_size,
                     'sha256': actual, 'source_url': url, 'cache_only_input': cache,
                     'review_scope': 'selected identity/preparation/method fields only; no expression matrix or new paired fidelity outcomes'})

brenca = ET.parse(INPUTS['brenca_primary'][0]).getroot()
pair = [compact(p) for p in brenca.findall('.//body//p') if 'For five samples' in compact(p)]
assert len(pair) == 1
pair_sentence = 'For five samples ' + pair[0].split('For five samples', 1)[1].split('PCA of', 1)[0].strip()
assert 'four EWSR1 and one TAF15' in pair_sentence
assert 'matched FFPE counterpart' in pair_sentence and 'data not shown' in pair_sentence
whole_methods = [s for s in brenca.findall('.//sec') if title(s) == 'Whole transcriptome sequencing and gene functional annotation']
assert len(whole_methods) == 1
prep = compact(whole_methods[0].find('p'))
assert '>70% tumor nuclei' in prep and 'FFPE' in prep and 'frozen samples' in prep
prior = json.loads(INPUTS['brenca_prior_evaluation'][0].read_text())
native_table = prior['specimen_table']
assert len(native_table) == 13
native_rows = [{'source_case': row[0], 'source_partner_label': row[1], 'source_site': row[4],
                'native_preparation': 'FFPE primary tumor transcriptional profile',
                'derived_culture_donor_bridge': None,
                'individual_frozen_preparation_link': None} for row in native_table[1:]]
assert sum(x['source_partner_label'] == 'EWSR1' for x in native_rows) == 7
assert sum(x['source_partner_label'] == 'TAF15' for x in native_rows) == 5

tempo = ET.parse(INPUTS['tempo_primary'][0]).getroot()
sections = {title(s): s for s in tempo.findall('.//sec')}
study = compact(sections['Study design and setting'].find('p'))
participant_p = sections['Participants and study subjects'].findall('p')
preparation = compact(participant_p[1])
assay = [compact(p) for p in sections['TempO-Seq assay'].findall('p')]
assert '22 patients' in compact(participant_p[0])
assert 'leaving 15 patients' in preparation and 'remaining 14 patients' in preparation and '12 EMC patients' in preparation
assert 'Siriraj' in study and 'Columbia' in study
assert 'slide-mounted FFPE' in assay[1] and 'protein-coding genes' in assay[1]
assert 'PRJNA1357027' in assay[0]
assert 'EWSR1' in compact(sections['Fluorescence in situ hybridization (FISH)'])
bangerter = ET.parse(INPUTS['bangerter_culture_primary'][0]).getroot()
bsections = {title(s): s for s in bangerter.findall('.//sec')}
origin = compact(bsections['Ex vivo cell model establishment'].find('p'))
origin_sentence = origin.split('The tumor tissues were mechanically', 1)[0].strip()
authentication = compact(bsections['Authentication and quality control of both established cell models'].find('p'))
assert 'amputation specimen for USZ20-EMC1' in origin_sentence
assert 'fresh diagnostic biopsy for USZ22-EMC2' in origin_sentence
assert 'corresponding native tumor material' in authentication and 'short tandem repeats' in authentication
planas = ET.parse(INPUTS['planas_culture_primary'][0]).getroot()
psections = {title(s): s for s in planas.findall('.//sec')}
rna_method = compact(psections['RNA\u2010sequencing'].find('p'))
deposit = compact(psections['Data availability'].find('p'))
assert 'patient\u2010derived sarcoma cell models' in rna_method
assert 'Stranded mRNA' in rna_method and 'NovaSeq 6000' in rna_method
assert 'GSE221532' in deposit
gsm_raw = {}
current = None
for line in INPUTS['GSE221532_metadata_original'][0].read_text().splitlines():
    if line.startswith('^SAMPLE = '):
        current = line.split(' = ', 1)[1]
        gsm_raw[current] = {}
    elif current and line.startswith('!Sample_') and ' = ' in line:
        k, v = line.split(' = ', 1)
        gsm_raw[current].setdefault(k[len('!Sample_'):], []).append(v)
gsm_owner = json.loads(INPUTS['GSE221532_owner_metadata_roster'][0].read_text())['rows']
assert len(gsm_raw) == len(gsm_owner) == 10
field_checks = 0
gsm_compact = []
for row in gsm_owner:
    raw = gsm_raw[row['GSM']]
    for key, val in row['fields'].items():
        assert raw[key] == val, (row['GSM'], key)
        field_checks += 1
    assert raw['source_name_ch1'] == ['sarcoma tumor']
    assert 'treatment: no treatment' in raw['characteristics_ch1']
    assert any('patient-derived sarcoma cell models' in s for s in raw['extract_protocol_ch1'])
    gsm_compact.append({'GSM': row['GSM'], 'source_title': raw['title'][0],
                        'generic_source_label': raw['source_name_ch1'][0],
                        'condition': 'no treatment', 'primary_assay_unit': 'patient-derived cultured-model RNA',
                        'explicit_EMC_model_reuse': row['GSM'] == 'GSM6883080',
                        'same_donor_native_tumor_rna_partner': None,
                        'other_histology_transfer_from_alias': False})
observations = {
    'source_scope': 'Independent Brenca/TempO native-pair semantic and method check. Owner handles USZ native model source reconciliation. No new numeric outcomes.',
    'brenca': {
        'doi': '10.1002/path.5284', 'pmcid': 'PMC6766969',
        'native_donors': native_rows,
        'primary_paired_preparation_quote': pair_sentence,
        'paired_preparation_status': 'Five same-patient frozen/FFPE preparations (4 EWSR1,1 TAF15), not five derived cultures/new donors; individual public run/case bridge unresolved.',
        'primary_preparation_quote': prep,
        'same_assay_native_tumor_culture_pair': 'not authenticated in inspected source methods',
        'prior_art': 'Original already reports similar frozen/FFPE results (data not shown); this is preparation concordance, not a new culture-fidelity result.',
        'engineered_controls': '11 engineered tBJ/ER source libraries distinct from 12 native tumors; native donor bridge absent. 8 EN/TN aliases mapped, remaining generic 15 need source-specific identity. No sequence or mechanism content inspected.',
        'source_PAIRED_layout': 'paired-end sequencing, not matched biological tissue/culture samples',
        'public_deposit': 'PRJNA692081/SRP301712 and CRO item9167 prior source dispositions reused; all23 generic titles do not authenticate 23 native tumors.'
    },
    'tempo': {
        'doi': '10.7717/peerj.21497', 'pmcid': 'PMC13374579', 'pmid': '42465974',
        'source_site_quote': study,
        'condition_accountability': '22 screened;7 RNA/count exclusions;15 informative;1 outlier exclusion;14 then2 clinical-record exclusions;12 final analysis cases. These are selection denominators, not new expression values.',
        'preparation': 'Archival FFPE slide-scraped tissue areas; Human Whole Transcriptome2.0 protein-coding detector-oligo assay. Not a culture assay or purified malignant-cell assay.',
        'identity_limit': 'Pathologist-reviewed source EMC; inspected assay is EWSR1 break-apart FISH, not NR4A3/partner confirmation for every case. Prior8positive/4negative retained without new identity inference.',
        'public_raw_deposit': 'PRJNA1357027; no raw reads or derived expression matrix inspected/copied here.',
        'native_tumor_culture_donor_bridge': None,
        'tumor_purity_percent': None,
        'comparator_mismatch': 'FFPE fixed-probe tissue and heterogeneous stroma/immune fractions cannot be pooled with unmatched fresh-culture RNAseq to infer intrinsic tumor-cell drift.',
        'distinct_other_assay': 'GSE213065 twelve immune-oriented libraries remain a separate prior source/compartment condition set, not this twelve-case whole-transcriptome cohort or a matched culture bridge.'
    },
    'native_culture_source_origin': {
        'bangerter_doi': '10.1007/s13577-022-00818-x', 'bangerter_pmcid': 'PMC9813045',
        'original_tissue_derivation_quote': origin_sentence,
        'source_authentication_quote': authentication,
        'favorable_evidence': 'Corresponding source native tumor and cultured models have an explicit physical derivation and STR authentication. Do not deny established native tumor-culture origin because paired RNA outputs are missing.',
        'authentication_limit': 'Donor identity/STR authentication does not quantify retained donor-specific transcriptional state. These selected methods do not expose paired source-tumor RNA libraries.',
        'planas_doi': '10.15252/emmm.202216863', 'planas_pmcid': 'PMC10086583',
        'rna_method_quote': rna_method, 'deposit_quote': deposit,
        'compatible_tissue_culture_rna_bridge': None,
        'handling_alternatives': 'Establishment media/sphere versus later DMEM/serum and passage history need per-library ascertainment; tissue selection, admixture and library-capture cannot be removed by expression scaling alone.',
        'prior_art_value': 'Native origin/authentication and broad model validation are prior art. An actual source-linked same-assay donor-specific transcriptional fidelity contrast could be distinct and useful, but is not established by comparing unrelated TCGA tumors or by reusing old panels.'
    },
    'GSE221532_conditions': {
        'all_ten_source_conditions': gsm_compact,
        'independent_raw_to_owner_field_checks': field_checks,
        'source_label_reconciliation': 'Generic sarcoma tumor source labels do not mean these are native tissue RNA: per-library extraction and linked primary RNA methods explicitly specify cultured patient-derived sarcoma models. None has an authenticated matching source-tumor RNA library in this inspected source metadata.',
        'all_source_count': 10,
        'EMC_identity': 'GSM6883080/USZ-22_EMC2 prior verified native source label reused; other nine generic aliases not newly histology-authenticated or assigned by numeric prefix.',
        'measurement_status': 'Actual public raw-count output declared but not downloaded/read; absence of an authenticated paired native tissue library blocks this specific fidelity analysis, not culture expression availability.'
    },
    'interpretation': 'Authentic culture labels or tissue expression availability are necessary but do not establish original tumor-derived donor matching, tumor-cell transcriptional fidelity or useful replication.',
    'pending': ['USZ source-linked paired native tissue and culture RNA, all exact conditions/passage/preparation and controls (owner scope)',
                'Individual Brenca frozen/FFPE source case-to-run links and source-specific native versus engineered mapping',
                'TempO per-case tumor purity, source overlap and any public same-donor culture link; none authenticated in these inspected methods',
                'NCC/USZ20 fullgene RNA availability and USZ20/23 donor overlap remain pending rather than absent'],
}
for name, value in [('INPUT-BINDINGS.json', bindings), ('SELECTED-SOURCE-OBSERVATIONS.json', observations)]:
    (HERE/name).write_text(json.dumps(value, indent=2)+'\n')
print(json.dumps({'status': 'PASS', 'bound_inputs': len(bindings), 'brenca_native_cases': len(native_rows),
                  'native_partner_counts': {'EWSR1': 7, 'TAF15': 5},
                  'paired_preparation_count': 5, 'new_outcomes_read': False,
                  'GSE221532_libraries': len(gsm_compact), 'raw_metadata_fields_compared': field_checks,
                  'new_raw_bytes': 0, 'no_new_matrix_or_sequence_reads': True}))
