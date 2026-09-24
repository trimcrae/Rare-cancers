from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
W=Path(__file__).resolve().parent;O=W/'ASO/journal-package'
pdf=canvas.Canvas(str(O/'ASO-graphical-abstract.pdf'),pagesize=(1328,531))
pdf.setTitle('NR4A3 gapmer design depends on RNA join and register');pdf.setAuthor('Tristan D. McRae')
pdf.setFillColor(HexColor('#151515'));pdf.setFont('Helvetica-Bold',41);pdf.drawString(38,469,'NR4A3 gapmer design depends on RNA join and register')
panels=[('PRIMARY CATALOGUE',['38 modelled exon-3 joins','190 junction-spanning','16-nucleotide designs']),('ONE-BASE REGISTER SHIFT',['TAF15 e6::NR4A3 e3','Centred: 9 bp (TFG)','Adjacent: 11 bp (NR4A3)']),('ADOPTED 10-bp CRITERION',['Primary designs: 45.8%','Artificial joins: 40.6%','Excess not established'])]
for x,(heading,lines) in zip([38,463,888],panels):
 pdf.setFillColor(HexColor('#f1f1f1'));pdf.roundRect(x,192,402,221,12,fill=1,stroke=0);pdf.setFillColor(HexColor('#151515'));pdf.setFont('Helvetica-Bold',24);pdf.drawString(x+18,371,heading)
 pdf.setFont('Helvetica',30)
 for j,line in enumerate(lines):
  assert pdf.stringWidth(line,'Helvetica',30)<=370
  pdf.drawString(x+18,318-j*45,line)
pdf.setFont('Helvetica',29);pdf.drawString(38,140,'Exon-2 acceptors require different designs.');pdf.drawString(38,99,'Patient-junction correspondence remains unresolved.')
pdf.setFont('Helvetica-Oblique',29);pdf.drawString(38,47,'Sequence predictions only; cleavage and biological selectivity were not measured.')
pdf.showPage();pdf.save()
