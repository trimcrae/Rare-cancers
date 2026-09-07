"""Build provisional source-grounded screening evidence from explicit worker notes.
These are diagnosis-level screening dispositions, not patient eligibility labels.
All records in the initial molecular-only difference and anchors were screened using
diagnosis-bearing criteria excerpts; selected key records had full criteria inspected.
Unresolved broad or ambiguous criteria are retained, never forced negative.
"""
import retrieve as r
packet=r.read(r.ROOT/'review-packet.json')
# Index assignments are checked against stable NCT IDs below before emitting evidence.
notes={
0:('histology_restricted','Ewing family diagnosis required; EWS partner mention is not permission for EMC/DSRCT.'),
1:('other_disease','Hematologic malignancy/transplant population; WT1 antigen does not imply DSRCT.'),
2:('other_disease','Hilar cholangiocarcinoma surgical study; resectability criteria do not support EMC.'),
3:('other_disease','Lumbar facet disease and mechanical fixation; fusion is not a tumor-fusion eligibility criterion.'),
4:('uncertain','Kidney-tumor study broadly includes renal tumors; diagnosis alone cannot establish renal site or compatibility.'),
5:('other_disease','AML tissue/blood study requires AML.'),
6:('other_disease','CML/AML vaccination criteria; WT1 expression is not a DSRCT fusion criterion.'),
7:('other_disease','Crohn disease diagnostic criterion; incidental matching does not concern sarcoma treatment.'),
8:('histology_restricted','Ewing sarcoma with EWS rearrangement required.'),
9:('broad_candidate_historical','Part A includes histologically confirmed solid tumors including other soft tissue sarcomas. Broad histology compatibility, not an EWS-WT1-directed cohort; COMPLETED.'),
10:('uncertain_historical','Phase1 broad extracranial solid tumor part explicitly closed; Phase2 requires NTRK/ROS1 kinase fusion, not defining EWS-WT1. ACTIVE_NOT_RECRUITING.'),
11:('histology_restricted','Ewing sarcoma family and type1 fusion required; not an unrestricted EWS-family invitation.'),
12:('other_disease','Healthy strength-training population; incidental NR4A3 retrieval.'),
13:('histology_restricted','Previously untreated Ewing tumor with specific transcript required.'),
14:('other_disease','AML biomarker master protocol; not DSRCT.'),
15:('other_disease','Healthy participants for strength training; not EMC-directed eligibility.'),
16:('molecular_mismatch','EWSR1-ATF1 fusion required, not EWSR1-NR4A3 or EWSR1-WT1; TERMINATED.'),
17:('other_disease','Motor-complete spinal cord injury required; incidental gene reference.'),
18:('screening_candidate_historical','Pediatric MATCH screening accepts recurrent/refractory solid tumors. Screening is not assignment to a compatible treatment arm; ACTIVE_NOT_RECRUITING.'),
19:('additional_biomarker_required','Pediatric MATCH treatment assignment/actionable mutation required; DSRCT defining fusion does not establish it.'),
20:('additional_biomarker_required','Pediatric MATCH NTRK-arm assignment required; EWS-WT1 is not an NTRK fusion.'),
21:('histology_restricted','High-grade serous ovarian carcinoma required; WT1 staining does not imply DSRCT.'),
22:('screening_candidate','Registry/trial prescreening accepts solid malignancy and biomarker variants/fusions including WT1. Candidate for prescreening, not an interventional treatment opportunity.'),
23:('other_disease','FLT3-mutated AML required.'),
24:('additional_biomarker_required','Pediatric MATCH MAPK-arm assignment required; defining fusion alone insufficient.'),
25:('broad_candidate_historical','Dose escalation includes relapsed/refractory solid tumors; phase2 Ewing/FET-ETS restriction must not be generalized. ACTIVE_NOT_RECRUITING.'),
26:('other_disease','High-risk hematologic malignancy transplantation; myeloid sarcoma is not these soft-tissue sarcomas.'),
27:('other_disease','Prostate-cancer active surveillance; fusion is imaging registration.'),
28:('other_disease','Post-transplant myeloid blood tumors required.'),
29:('uncertain','Allogeneic stem-cell transplant status required, not a defining-fusion sarcoma criterion. No diagnosis-alone treatment candidate established.'),
30:('histology_restricted','Ewing/PNET histology and ETS partner when known; not unrestricted EWS/FUS eligibility.'),
31:('observational_candidate','Rare molecular alteration cohort; observational and Canadian follow-up requirements. No treatment intervention inferred.'),
32:('additional_biomarker_required','Pediatric MATCH IDH1-arm assignment required; EWS-WT1 alone insufficient.'),
33:('additional_biomarker_required','Pediatric MATCH HRAS-arm assignment required; EWS-WT1 alone insufficient.'),
34:('histology_or_fusion_mismatch','EWSR1-ATF1/CREB1, clear cell sarcoma, conventional or dedifferentiated chondrosarcoma specified; EMC is not inferred from parent chondrosarcoma wording.'),
35:('histology_restricted','Ewing/PNET with ETS partner or high-grade osteosarcoma required.'),
36:('other_disease','FUS-associated ALS required; FUS gene name is not a sarcoma diagnosis.'),
37:('other_disease','AML/MDS after allogeneic transplantation required.'),
38:('uncertain','Ewing-like/non-ETS round-cell wording in an observational cohort is not a verified EMC/DSRCT diagnostic invitation; retain ambiguity.'),
39:('broad_candidate','Phase1 accepts recurrent/refractory non-CNS solid tumors; molecular hit is in Ewing-specific Phase2. Broad Phase1 compatibility for EMC/DSRCT, with age/phase/other gates unresolved.'),
40:('additional_biomarker_required','NTRK-fusion/amplification or EWSR1-WT1 DSRCT cohort; EMC defining fusion alone does not match. Historical TERMINATED.'),
41:('other_disease','Suspected prostate cancer biopsy study.'),
42:('molecular_candidate_historical','Elimusertib Part A and B1 explicitly include any EWS-fusion solid tumor and EWS-WT1 examples. DSRCT diagnosis/fusion-level candidate missed by frozen ordinary terms, but ACTIVE_NOT_RECRUITING.'),
43:('ordinary_synonym_candidate','Stratum A names desmoplastic small round blue cell tumor and other soft tissue sarcoma. This is a missing ordinary blue-cell synonym, not molecular-only scientific novelty; unquoted sensitivity checked.'),
44:('uncertain_historical','EWSR1-non-ETS sarcoma wording is gated by Ewing-like pathology review and prior Ewing regimens. Do not label EMC accepted. COMPLETED.'),
45:('histology_restricted','WT1-positive study restricts to colorectal, gastric, pancreatic or ovarian cancer; WT1 positivity not DSRCT eligibility.'),
46:('other_disease','Mechanical neck-pain physiotherapy population, not EMC treatment.'),
47:('uncertain','SS18 appears among SWI/SNF member mutations; no explicit SS18::SSX fusion equivalence. All alterations require PI approval. Not a verified synovial sarcoma positive or negative.'),
48:('histology_restricted','Epithelioid pleural mesothelioma required.'),
49:('histology_restricted','Ewing or EWSR1-negative Ewing-like round-cell sarcoma; defining EMC/DSRCT fusion does not establish criterion.'),
50:('other_disease','AML/MDS post-transplant population.'),
51:('molecular_candidate','LIFFT Phase1 known FET fusion supports EWSR1/TAF15-fused EMC diagnosis-level compatibility. Phase2 is EWS-FLI1 Ewing-specific. DSRCT ordinary-findable but exclusion9 delays enrollment until 3 non-DSRCT patients without DLT; current phase/cohort access unresolved.'),
52:('other_disease','Degenerative spine fusion study explicitly excludes tumor diseases.'),
53:('additional_evidence_required','Selinexor cohortD needs patient-specific evidence and PI approval; other cohorts specify other diagnoses/BCOR. EWS-WT1 alone insufficient.'),
54:('other_disease','Genetic ALS diagnosis or familial hypercholesterolemia control; not a sarcoma treatment study.'),
55:('histology_restricted','PerVision specifies rhabdomyosarcoma, Ewing and synovial sarcoma; supports SS diagnostic scope and is a hard negative for extending generic fusion language to EMC/DSRCT.'),
56:('ordinary_candidate_and_negative_control','EMC appears in conditions and ordinary search; age is 1-30 at diagnostic biopsy. DSRCT explicitly excluded in criteria. Retrieval is not eligibility.'),
57:('other_disease','Genetically confirmed Baker Gordon syndrome required; no SS sarcoma candidate.'),
58:('histology_restricted','DSRCT or synovial sarcoma plus SSTR expression criteria; not EMC.'),
59:('other_disease','Prostate lesion biopsy study; FUS refers to imaging fusion.'),
60:('uncertain','Truncal/extremity sarcoma surveillance includes misspelled EMC, but DSRCT not specifically listed and abdominal/mesenteric/retroperitoneal tumors excluded. Do not infer DSRCT diagnosis-level inclusion.'),
61:('class_candidate_uncertain','TAS cohort supports a class-level candidate for EMC/DSRCT, but class membership accepted by protocol/team is not enumerated. Ordinary SS-findable; parent-sarcoma-findable; not a frozen molecular-query gain.'),
62:('other_disease','T-cell lymphoblastic lymphoma/leukemia post-transplant required.'),
63:('histology_restricted','Synovial sarcoma or myxoid/round-cell liposarcoma required; their molecular terms do not invite EMC/DSRCT.'),
64:('broad_candidate','PEEL224 Phase1 histologic sarcoma criterion supports EMC candidate; molecular terms are in other disease-specific cohorts. Phase2 other-sarcoma slots require cautious interpretation. Parent query retrieves it.'),
65:('histology_restricted','Glioblastoma/grade4 glioma required; WT1 target not DSRCT.'),
66:('histology_and_fusion_exclusion','Ewing diagnosis required and clear FET-non-ETS fusions, including EWSR1-WT1, explicitly do not meet enrollment criteria.'),
67:('histology_restricted','Cancer population is prepubertal neuroblastoma or Ewing sarcoma; generic title does not invite EMC/DSRCT.'),
68:('not_diagnosis_supported','Ewing or protocol-defined Ewing-like under Ewing treatment paradigms; extra-skeletal adjective does not establish EMC. Keep protocol-dependent Ewing-like ambiguity separate from positive labels.'),
69:('histology_restricted','Ewing with EWSR1-ETS fusion required.'),
70:('histology_restricted','Centrally confirmed DSRCT with EWSR1-WT1 required; not EMC.'),
71:('other_disease','AML required and recurrent monitored fusions including FUS-ERG must be absent; gene mention can signal exclusion.'),
72:('histology_and_fusion_exclusion','Ewing histology required; FET-non-ETS fusion cases excluded.'),
73:('histology_and_fusion_restricted','Ewing or DSRCT and specified EWSR1-FLI1/ERG/WT1 breakpoints required; not EMC. DSRCT ordinary-findable; NOT_YET_RECRUITING with safety-staged age/cohort rules.')
}
assert len(packet)==len(notes)==74
assert packet[51]['nct_id']=='NCT05918640' and packet[42]['nct_id']=='NCT05071209' and packet[47]['nct_id']=='NCT05687136'
rows=[]
for i,p in enumerate(packet):
 label,note=notes[i]
 rows.append({'nct_id':p['nct_id'],'diagnoses_screened':p['molecular_only_for'] or ['EMC','DSRCT','SS'],'status':p['status'],'study_type':p['study_type'],'provisional_disposition':label,'rationale':note,'source_pointers':p['source_pointers'],'full_criteria_in_review_packet':True,'review_depth':'Diagnosis-bearing criteria excerpts screened; key positive/negative records additionally read in full. This is not an exhaustive patient-eligibility adjudication.'})
r.save(r.ROOT/'evidence.json',{'label_authority':'Single worker, provisional pending coordinator independent verification','scope':'74 records: original corrected molecular-only union plus historical anchors. Reference corpus is query-bounded, not independently fully labeled. Later ordinary sensitivity may remove apparent gaps but all initial dispositions are preserved.','records':rows})
print('Wrote',len(rows),'provisional screening dispositions')
