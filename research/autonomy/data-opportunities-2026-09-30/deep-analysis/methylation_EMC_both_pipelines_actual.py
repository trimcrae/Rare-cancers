import pathlib,subprocess,sys,json,time
here=pathlib.Path(__file__).resolve().parent;rows=[];start=time.monotonic()
for name in ['methylation_EMC_MTAPlocus_conumee_actual.py','methylation_EMC_MTAPlocus_author_BAF_actual.py']:
 result=subprocess.run([sys.executable,str(here/name)],timeout=max(120,int(5100-(time.monotonic()-start))))
 rows.append({'script':name,'returncode':result.returncode,'cumulative_seconds':time.monotonic()-start})
path=pathlib.Path('campaign-output/methylation-EMC-combined-analysis-receipts.json');path.write_text(json.dumps(rows,indent=2)+'\n')
raise SystemExit(0 if all(r['returncode']==0 for r in rows) else 1)
