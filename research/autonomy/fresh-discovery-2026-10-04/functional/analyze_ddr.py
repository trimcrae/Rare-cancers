"""Exploratory fixed-source EMC pharmacology audit; no clinical extrapolation."""
from pathlib import Path
import json,zipfile,io,statistics,hashlib,subprocess,datetime
import openpyxl
ROOT=Path(__file__).resolve().parent
BASE='5d2f2e2116'
REPO='C:/Projects/EMC-Research'
META={'E':('oxaliplatin',4),'F':('doxorubicin',4),'G':('trabectedin',4),'I':('olaparib',12),'J':('niraparib',12),'K':('adavosertib',12)}
def main():
 source=ROOT/'planaspaz2023-publisher-fig5.zip'
 assert hashlib.sha256(source.read_bytes()).hexdigest()=='0a9f33ceb7b9ee17c48436fe7655c2d514d1272b5deebe977c0f0c728f4ffdd0'
 z=zipfile.ZipFile(source);curves=[];excluded=[]
 sources=[(panel,drug,days,f'Fig5/Fig5{panel}.xlsx') for panel,(drug,days) in META.items()]
 sources += [('EV5'+p,drug,8,f'ev5-FigEV5{p}.xlsx') for p,drug in [('A','olaparib'),('B','niraparib'),('C','adavosertib')]]
 for panel,drug,days,member in sources:
  data=z.read(member) if member.startswith('Fig5/') else (ROOT/member).read_bytes()
  wb=openpyxl.load_workbook(io.BytesIO(data),data_only=True)
  assert len(wb.worksheets)==1
  rows=list(wb.active.values);head=rows[0]
  assert head[0]=='Concentration log10 (μM)'
  for col,value in enumerate(head):
   if not isinstance(value,str) or col==0:continue
   assert head[col+1] is None and head[col+2] is None
   points=[]
   for n,row in enumerate(rows[1:],2):
    raw=[v for v in row[col:col+3] if isinstance(v,(int,float))]
    if not raw:continue
    datum={'excel_row':n,'log10_dose_uM':row[0],'reported_replicate_values':raw,'mean':statistics.mean(raw),'min':min(raw),'max':max(raw),'sample_sd':statistics.stdev(raw) if len(raw)>1 else None}
    if isinstance(row[0],(int,float)):datum['dose_uM']=10**row[0]
    else:datum['dose_assignment']='Unlabelled source row; do not impute dose or include in concentration contrast'
    points.append(datum)
   curves.append({'panel':panel,'drug':drug,'exposure_days':days,'model':value,'source_member':member,'points':points})
 emc=[c for c in curves if c['model']=='USZ-22_EMC2']
 assert len(emc)==9
 # All curves and unlabelled rows retained. Technical replicate range is descriptive only.
 out={'schema':'emc-functional-ddr-audit/1','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'additional_source_receipt':'ev5-source-receipt.json','reanalysis':'Exploratory extraction and arithmetic of already-published measured viability. Not a newly demonstrated disease finding.','all_same_assay_model_curves':curves,'EMC_model':'USZ-22_EMC2','independent_emc_models':1,'replication_warning':'Source columns are technical replicates/repetitions; no donor confidence interval or drug-as-donor test.','EMC_curves':emc,'EV5_combinations':{'source_panels':['H','I','J','K'],'actual_models':['USZ-20_REA1','USZ-21_LG1'],'EMC_measured':False,'evidence':'Allfourworkbookssheetnames+originalFigEV5image labels; HRDlow group definition does not establish EMC inclusion in every panel.'}}
 old_receipts=[]
 old_files=['deep-analysis/results/Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json','deep-analysis/results/Iwata-complete221-screen-and24-IC50-literal-measurements-final.json','deep-analysis/results/authentic-EMC-two-model-genotype-supplements.json']
 for name in old_files:
  path='research/autonomy/data-opportunities-2026-09-30/'+name
  data=subprocess.check_output(['git','-C',REPO,'show',BASE+':'+path])
  target=ROOT/('reused-'+Path(name).name);target.write_bytes(data)
  old_receipts.append({'revision':BASE,'path':path,'retained':target.name,'sha256':hashlib.sha256(data).hexdigest(),'status':'Retained prior evaluated output, not an independent biological study or new finding'})
 out['prior_evaluations']=old_receipts
 (ROOT/'ddr-results.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 for c in emc:
  print(c['drug'],c['exposure_days'],'days',[(round(p['dose_uM'],5),round(p['mean'],4)) for p in c['points'] if 'dose_uM' in p])
 print('Total evaluated model-condition curves',len(curves),'EMC',len(emc))
if __name__=='__main__':main()
