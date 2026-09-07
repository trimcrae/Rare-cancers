"""Reproduce text and selected PNGs from the archived original PDF, offline.

Requires pypdf, pdfplumber and Poppler pdftoppm on PATH. This does not change the
frozen rule extraction or clinical source. Existing generated text/images are replaced.
"""
from pathlib import Path
import subprocess
from pypdf import PdfReader
import pdfplumber

p = Path(__file__).resolve().parent
r = PdfReader(p/'Prot_SAP_000.pdf')
(p/'protocol-extracted.txt').write_text('\n'.join(
    f'\n=== PDF PAGE {i+1} ===\n'+page.extract_text()
    for i, page in enumerate(r.pages)), encoding='utf8')
with pdfplumber.open(p/'Prot_SAP_000.pdf') as document:
    texts = [page.extract_text(x_tolerance=1) for page in document.pages]
(p/'protocol-plumber.txt').write_text('\n'.join(
    f'\n=== PDF PAGE {i+1} ===\n'+text for i,text in enumerate(texts)), encoding='utf8')
for first,last in [(17,19),(29,31),(32,34),(15,15)]:
    subprocess.run(['pdftoppm','-f',str(first),'-l',str(last),'-scale-to','1500',
                    '-png',str(p/'Prot_SAP_000.pdf'),str(p/'page')],check=True)
