"""Render frozen review copies remotely; never assert visual or publication acceptance."""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import hashlib, json, os, shutil, subprocess, tempfile
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
MANIFEST=json.loads((HERE/'inputs.json').read_text())
OUT=HERE/MANIFEST.get('output_directory','rendered')
LIMIT=MANIFEST['output_budget_bytes']
MIN_FREE=10*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
events=[]

def guard(operation):
    local=datetime.now(ZoneInfo('America/New_York'))
    free=shutil.disk_usage(HERE).free
    produced=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()) if OUT.exists() else 0
    events.append({'operation':operation,'local_time':local.isoformat(),'free_bytes':free,'output_bytes':produced})
    assert not 6<=local.hour<10, 'Daily quiet hours prohibit render operation'
    assert free>=MIN_FREE+max(0,LIMIT-produced), 'Insufficient runner storage headroom'
    assert produced<=LIMIT, 'Bounded output allowance exceeded'

def run(command):
    subprocess.run(command,check=True,timeout=180,env={**os.environ,'SAL_USE_VCLPLUGIN':'svp'})

guard('before export');OUT.mkdir(exist_ok=True)
records=[]
corrected_main=None
if any(x['paper']=='FO' and x['role']=='main' for x in MANIFEST['inputs']):
    from correct_fo_labels import correct
    corrected_main,label_receipt=correct(HERE,guard)
for job in MANIFEST['inputs']:
    source=ROOT/job['input'];assert source.is_file() and sha(source)==job['sha256']
    render_source=corrected_main if job['paper']=='FO' and job['role']=='main' else source
    target=OUT/job['paper']/job['role'];target.mkdir(parents=True,exist_ok=True)
    guard('Word export '+job['paper']+' '+job['role'])
    pdf=target/(render_source.stem+'.pdf')
    if job.get('existing_pdf'):
        existing=ROOT/job['existing_pdf']
        assert sha(existing)==job['existing_pdf_sha256']
        shutil.copyfile(existing,pdf)
    else:
        with tempfile.TemporaryDirectory(prefix='emc-review-lo-') as profile:
            run(['soffice','--headless','--norestore','-env:UserInstallation='+Path(profile).as_uri(),'--convert-to','pdf:writer_pdf_Export','--outdir',str(target),str(render_source)])
    assert pdf.is_file() and pdf.stat().st_size>1000, 'Converter did not produce expected PDF'
    reader=PdfReader(pdf);texts=[page.extract_text() or '' for page in reader.pages]
    assert all(x.strip() for x in texts), 'Empty extracted page; inspect conversion'
    (target/'pdf-text.txt').write_text('\n\f\n'.join(texts),encoding='utf-8')
    guard('page rendering '+job['paper']+' '+job['role'])
    run(['pdftoppm','-r','120','-png',str(pdf),str(target/'page')])
    pages=sorted(target.glob('page-*.png'))
    assert len(pages)==len(reader.pages)
    assert sha(source)==job['sha256'], 'Source changed during export'
    records.append({**job,'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),'pdf_bytes':pdf.stat().st_size,'pages':len(pages),'page_images':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in pages]})

combined=[]
for paper in sorted({x['paper'] for x in records}):
    guard('assemble combined PDF '+paper)
    writer=PdfWriter();components=[]
    roles=MANIFEST.get('combination_roles',{}).get(paper,['main','supplement'])
    for role in roles:
        rec=next(x for x in records+MANIFEST.get('retained_component_records',[]) if x['paper']==paper and x['role']==role)
        assert sha(ROOT/rec['pdf'])==rec['pdf_sha256'], 'Retained component identity changed'
        writer.append(str(ROOT/rec['pdf']));components.append(rec)
    attachment=None
    if paper=='ASO':
        csv=HERE/'inputs/ASO/fusion-junction-aso-sequences.csv'
        assert sha(csv)==MANIFEST['ASO_sequence_csv']['sha256']
        writer.add_attachment(csv.name,csv.read_bytes())
        attachment={'name':csv.name,'sha256':sha(csv),'bytes':csv.stat().st_size}
    dest=OUT/paper/'aixiv-review.pdf'
    with dest.open('wb') as f:writer.write(f)
    readback=PdfReader(dest)
    assert len(readback.pages)==sum(c['pages'] for c in components)
    if attachment:
        assert hashlib.sha256(readback.attachments[attachment['name']][0]).hexdigest()==attachment['sha256']
    combined.append({'paper':paper,'path':str(dest.relative_to(ROOT)),'sha256':sha(dest),'pages':len(readback.pages),'component_order':roles,'components':[{'path':x['pdf'],'sha256':x['pdf_sha256']} for x in components],'embedded_csv':attachment})
guard('after all outputs')
receipt={'utc':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'input_manifest_sha256':sha(HERE/'inputs.json'),'renderer':subprocess.check_output(['soffice','--version'],text=True).strip(),'status':'rendered_awaiting_actual_visual_review','inputs_unchanged':True,'documents':records,'combined':combined,'physical_gates':events,'output_bytes':sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()),'no_scientific_analysis_or_aixiv_submission':True}
(OUT/'RENDER-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'documents':len(records),'combined':combined,'output_bytes':receipt['output_bytes'],'minimum_free_bytes':min(x['free_bytes'] for x in events),'visual_review_pending':True}))
