#!/usr/bin/env python3
"""Export committed DOCX files on an isolated Linux runner and retain exact evidence."""
import datetime as dt
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
OUT = Path('/tmp/methylation-render')
OUT.mkdir(exist_ok=True)


def guard():
    now = dt.datetime.now(ZoneInfo('America/New_York'))
    # Each owned subprocess has a 90-second timeout; refuse the lead-in to 06:00 too.
    if 6 <= now.hour < 10 or (now.hour == 5 and now.minute >= 58):
        raise RuntimeError('Daily computer-use/rendering restriction')
    if shutil.disk_usage(OUT).free < 10.5*1024**3:
        raise RuntimeError('10 GiB storage reserve')


receipt = {'source_revision': subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
           'documents': [], 'libreoffice': subprocess.check_output(['libreoffice','--version']).decode().strip()}
for stem in ['manuscript', 'online-resource-1', 'cover-letter']:
    guard()
    source = HERE/(stem+'.docx')
    subprocess.run(['libreoffice', '-env:UserInstallation=file:///tmp/methylation-lo-profile',
                    '--headless','--convert-to','pdf','--outdir',str(OUT),str(source)],
                   check=True, timeout=90)
    pdf = OUT/(stem+'.pdf')
    assert pdf.is_file() and pdf.stat().st_size > 1000
    guard()
    subprocess.run(['pdftoppm','-png','-r','110',str(pdf),str(OUT/stem)],check=True,timeout=90)
    guard()
    subprocess.run(['pdftotext','-layout',str(pdf),str(OUT/(stem+'.txt'))],check=True,timeout=30)
    receipt['documents'].append({'name':stem,'docx_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                                'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
                                'pages':len(list(OUT.glob(stem+'-*.png')))})
(OUT/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
