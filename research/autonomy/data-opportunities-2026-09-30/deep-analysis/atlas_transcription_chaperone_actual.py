import io,json,datetime,contextlib
from pathlib import Path
import atlas_panel_extension as panel
FROZEN={
'cdk7_initiation_module':['CDK7','CCNH','MNAT1'],
'cdk9_elongation_module':['CDK9','CCNT1','CCNT2','AFF4'],
'cdk12_13_processivity':['CDK12','CDK13','CCNK'],
'pol2_transcriptional_output_context':['POLR2A','MYC','GTF2B','TAF1'],
'hsp90_machine':['HSP90AA1','HSP90AB1','HSP90B1','TRAP1'],
'hsp90_co_chaperones':['CDC37','AHSA1','STIP1','PTGES3','PPID'],
'hsp70_arm_and_stress_response':['HSPA8','HSPA4','DNAJB1','HSPH1','HSF1'],
'MTAP_locus':['MTAP','CDKN2A','CDKN2B'],
'PRMT5_methylosome':['PRMT5','WDR77','RIOK1','CLNS1A'],
'proliferation_context':['MKI67','PCNA','TOP2A','CCNB1','RRM2','BUB1','AURKA','MCM2','TYMS','E2F1','CCNA2','CDK1'],
'p53_output_context':['CDKN1A','BBC3','ZMAT3','SESN1','RPS27L','GADD45A'],
'BH3_antiapoptotic':['BCL2','MCL1','BCL2L1','BCL2L2','BCL2A1'],
'BH3_effectors':['BAX','BAK1','BOK'],
'BH3_sensitisers':['BCL2L11','PMAIP1','BID','BAD','BIK'],
'PRC2':['EZH2','EED','SUZ12','RBBP4'],
'SWISNF':['SMARCB1','SMARCA4','ARID1A','PBRM1'],
'ncBAF':['BRD9','BICRA','SMARCD1','SMARCC1'],
'altEJ':['POLQ','LIG3','PARP1','XRCC1']}
def main():
 assert len(FROZEN)==18
 panel.GROUPS.clear();panel.GROUPS.update(FROZEN)
 panel.NR_GENES[:]=[];panel.BOOT_GROUPS[:]=list(FROZEN)
 base=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis')
 outpath=base/'outputs/atlas-transcription-chaperone-actual.json'
 mat=Path('research/autonomy/atlas-hofvander-source-2026-09-06/tpm_matrix.tsv')
 meta=Path('research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json')
 with contextlib.redirect_stdout(io.StringIO()):panel.run(str(mat),str(meta),str(outpath))
 out=json.loads(outpath.read_text());out['schema']='emc-atlas-historical-modules-actual/1'
 out['frozen_panel_source']='research/modalities/emc_expression_panels.py blob e48f8b38fba17237ea5985088f9e2e340a70042c; exact pre-existing memberships, proliferation union of proliferation_reference/confound_control'
 out['extension_amendment']={'dated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observed_before_extension':'Individual scalar RNA summaries from atlas panel run36866309548 were seen; historical module memberships fixed before that execution, no member reselection','scale':'Mean within-specimen gene rank differs from old array gene z scores; annotation-module transfer only','direction':'Equal positive gene coefficients; no validated activity or dependency signatures','complete_coverage':'Score omitted if any frozen gene absent','family_size':18,'multiplicity':'All18 predefined module effects/CIs reported; conditional95% bootstrap intervals are not simultaneous or multiplicity adjusted. No significance selection claimed','conditional_intervals':'Bootstrap2000 within histology/year at patient unit; nine EMC/four matched EMC limitations'}
 out['limitations'].extend(['Transcript module contrasts do not establish CDK phosphorylation, kinase activity, chaperone dependency, apoptotic priming or drug response','Low locus RNA does not establish genomic deletion; p53 output is not genotype; PRC2/SWISNF transcription is not protein loss; altEJ transcription is not repair dependence','Scalar expression cannot alone falsify multi-gene modules','Eighteen modules form one finite predefined transfer extension, not18 independent discoveries'])
 outpath.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 print('EMC_ATLAS_HISTORICAL_MODULES_BEGIN');print(json.dumps(out,separators=(',',':')));print('EMC_ATLAS_HISTORICAL_MODULES_END')
if __name__=='__main__':main()
