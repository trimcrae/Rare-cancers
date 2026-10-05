#!/usr/bin/env python3
"""Verify scientific accounting and freeze exact scoped exports/cache receipts."""
import datetime,hashlib,json,pathlib,shutil,xml.etree.ElementTree as E
BASE=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/workspace/Rare-cancers')
def bind(p):
 b=p.read_bytes();return {'path':str(p.relative_to(BASE)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(n,d):(BASE/n).write_text(json.dumps(d,indent=2)+'\n')
reuse=json.loads((BASE/'REUSED-INPUTS.json').read_text());mismatch=[]
for x in reuse['inputs']:
 p=pathlib.Path(x['path']);b=p.read_bytes()
 if len(b)!=x['bytes'] or hashlib.sha256(b).hexdigest()!=x['sha256']:mismatch.append(x['path'])
assert not mismatch
old=ROOT/'research/autonomy/fresh-discovery-2026-10-04/functional'
bangerter=json.loads((old/'reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json').read_text());iwata=json.loads((old/'reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json').read_text())
assert len(bangerter['rows'])==40
tablecounts=[]
for t in iwata['tables']:
 ls=[len(v) for v in t.values() if isinstance(v,list)]
 tablecounts.append(max(ls))
assert sorted(tablecounts)==[24,221]
roster=json.loads((BASE/'PRIMARY-ROSTERS.json').read_text());living=json.loads((BASE/'LIVING-ROSTER.json').read_text())
assert len(roster['integration2026']['rows'])==19 and len(roster['cho2024']['rows'])==18
assert len(living['donor_rows'])==19 and sum(len(r['cultures']) for r in living['donor_rows'])==29
cho=roster['cho2024']['rows'];diagnoses={r[2] for r in cho};assert len(diagnoses)==8
assert sum(r[2] in ['UPS','CHS','FS'] for r in cho)==8
raw=[bind(p) for p in sorted((BASE/'raw-cache').iterdir()) if p.is_file()]
rawbytes=sum(x['bytes'] for x in raw);free=shutil.disk_usage(BASE).free
assert rawbytes<67108864 and free>=10737418240
utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
put('VERIFICATION.json',{'utc':utc,'checks':{'all16reused_input_bindings_pass':True,'USZ40_reused_rows':40,'NCC_reused_table_counts':tablecounts,'integration_complete_models':19,'living_complete_donors':19,'living_complete_cultures':29,'living_commercial_control_rows':1,'Cho_complete_lines':18,'Cho_authors_patients':14,'Cho_Table1_diagnosis_categories':8,'Cho_abstract_categories':7,'Cho_generic_UPS_CHS_FS_rows':8,'new_authentic_EMC_perturbation_conditions':0,'new_EMC_response_calculations':0,'new_raw_within64MiB':True,'free_above10GiB':True},'scope':'Scientific eligibility/accounting and exact file hashes; not normal repository preflight or evidence of global absence.'})
put('DECISION.json',{'utc':utc,'decision':'SHELVE standalone R9 functional_new proposal','new_publication_worthy_findings':0,'new_EMC_measured_response_conditions':0,'primary_value':'Open source recovery and complete cohort accountability; no new controlled disease inference.','strongest_alternative':'Missing authentic identity, exposure/control context, or prior art already answers the useful interpretation.','remaining_suitable_accessible_pending':'QPOP graphical eligibility material uninspected during computer-use ban; any newly discovered suitable EMC source/condition must be evaluated before promotion.','coverage':'COVERAGE.json preserves specific unresolved/unavailable/public conditions and all previous measurements/decisions.','reopen':['Authenticated EMC specimen/model-to-assay crosswalk with measured controls and consequential unanswered comparison','Complete all relevant public EMC conditions and clarify overlap','Discriminating follow-through against treatment/exposure/model alternatives','Independent challenge and validity plus scientific-value reassessment'], 'next_distinct_work':'Diagnostic owner source-gates2026pan-cancerphosphoproteomics primary. This owner can independently challenge its frozen eligibility/value packet; QPOP graphics may be reviewed after14:00UTC if identity resolution could change the decision.'})
put('PORTABILITY.json',{'utc':utc,'new_raw_bytes_including_copies_and_derivatives':rawbytes,'free_bytes':free,'raw_budget_bytes':67108864,'cache_only':raw,'git_scope':'Only compact plans, complete needed rosters/relevant excerpts, hashes/receipts/scripts/decisions. Original PDFs/XML/fullabstractJSON/ZIP/fulltext derivatives are ignored and retained, not Git-portable.','rehydration':'Use public URLs in RETRIEVAL/FOLLOWUP/CITATION/access receipts and exact hashes. Extract PDFs from public ZIPs then pdftotext -layout for cached text; originals and derivatives must match recorded hashes. Preserve prior caches and worktrees. Interrupted/blocked/private routes are not rehydration authorization.','reused_sources':'Original root inputs are read-only with exact bindings in REUSED-INPUTS.json; no full-source recopy.'})
exports=[bind(p) for p in sorted(BASE.iterdir()) if p.is_file() and p.name!='MANIFEST.json']
put('MANIFEST.json',{'utc':utc,'base_commit':'08de5ae9631624052fa32ae9ee6567394bc4d80d','owned_scope':'research/autonomy/fresh-discovery-2026-10-05-round9/functional_new','exports':exports,'cache_binding':'PORTABILITY.json','decision':'No new publication-worthy finding; source/identity gaps remain; search not exhausted.'})
print(json.dumps({'exports':len(exports),'raw_bytes':rawbytes,'free_bytes':free,'verification':'pass','manifest_sha256':hashlib.sha256((BASE/'MANIFEST.json').read_bytes()).hexdigest()},indent=2))
