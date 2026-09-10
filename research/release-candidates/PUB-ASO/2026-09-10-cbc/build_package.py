"""Repackage the actual submitted ASO v3 without rerunning or altering its science."""
from pathlib import Path
from copy import deepcopy
import hashlib, json, re, shutil
from docx import Document
from docx.shared import Inches, Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-04'
TITLE = ('Computational design and parent transcript liabilities of NR4A3 fusion junction '
         'gapmers in extraskeletal myxoid chondrosarcoma')
ABSTRACT = '''Fusion-junction antisense gapmers could discriminate oncogenic transcripts from their normal parents, but partial parent pairing may escape conventional near-match screens. We computationally designed and screened 190 junction-spanning 16-mers across 38 in-frame NR4A3 fusion junctions in extraskeletal myxoid chondrosarcoma. Five sequence screens examined mature transcripts, exhaustive transcript substitutions, unspliced parents, contiguous mature-parent pairing through the DNA gap, and the genome. At an adopted ten-base-pair full-gap criterion, 87 of 190 designs (45.8%) paired a mature wild-type parent; the longest duplex involved NR4A3 for 61 designs. Exon-terminus chimeras met the same criterion at 40.6%, leaving a disease-specific excess unresolved. Within-junction selection found a parent-clear design for 35 of 38 junctions at this criterion, with substantial sensitivity to the chosen cutoff. Two designs at reported junctions had longest full-gap parent duplexes of eight and nine base pairs. The ten-base-pair criterion is a convention, not a measured cleavage threshold. Patient-derived cell-model junctions remain unresolved relative to these designs. The released sequence records and screening outputs support reproducible computational prioritization and expose parent-transcript liabilities, but establish no cleavage, potency, delivery, safety or therapeutic window. No laboratory work was performed.'''
HIGHLIGHTS = [
    '190 gapmer designs span 38 modelled NR4A3 fusion junctions.',
    '87 designs pair a mature parent through the full gap at an adopted cutoff.',
    'Exon-terminus controls leave a disease-specific liability excess unresolved.',
    'Parent-clear design counts depend strongly on the pairing cutoff.',
    'Sequence predictions do not establish cleavage or a therapeutic window.',
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def simple_doc(title, paragraphs):
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Inches(8.5), Inches(11)
    s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(.8)
    for name in ['Normal', 'Title', 'Heading 1', 'Heading 2']:
        d.styles[name].font.name = 'Times New Roman'
        d.styles[name].font.color.rgb = RGBColor(0, 0, 0)
    d.styles['Title'].font.size = Pt(16)
    for style in d.styles:
        for el in list(style.element.xpath('.//w:pBdr')):
            el.getparent().remove(el)
        for el in style.element.xpath('.//w:rFonts'):
            for attr in ['asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme', 'csTheme']:
                el.attrib.pop(qn('w:'+attr), None)
    d.styles['Normal'].font.size = Pt(11)
    d.styles['Normal'].paragraph_format.space_after = Pt(8)
    d.core_properties.author = 'Tristan D. McRae'
    d.core_properties.title = title
    d.add_paragraph(title, 'Title')
    for p in paragraphs:
        if isinstance(p, tuple):
            d.add_paragraph(p[1], p[0])
        else:
            d.add_paragraph(p)
    return d

def build():
    submitted = BASE / 'submission/manuscript.docx'
    assert sha(submitted) == '7fe0033347e3825678394082157b8b60e5cc4edcdd122061d02d8d5a28d060c7'
    original = Document(submitted)
    d = Document(submitted)
    ps = d.paragraphs
    assert ps[0].style.name == 'Title' and ps[6].text.startswith('Extraskeletal')
    assert len(ABSTRACT.split()) <= 250 and all(len(x) <= 85 for x in HIGHLIGHTS)
    ps[0].text = TITLE
    ps[3].text = 'Running title. Parent pairing in NR4A3 junction gapmer designs'
    ps[6].text = ABSTRACT
    changes = {
        'Introduction': '1 Introduction',
        'Materials and Methods': '2 Materials and methods',
        'Results': '3 Results',
        'The reagents': '3.1 Designs at reported junctions',
        'Selection from a panel of 190 designs': '3.2 Selection and parent liabilities across 190 designs',
        'Controls for the knockdown experiment': '3.3 Computationally screened control sequences',
        'Discussion': '4 Discussion',
        'Test articles': '4.1 Candidate models and unresolved junction correspondence',
        'The falsification experiment': '4.2 Proposed experimental evaluation',
        'Interpretation and limits': '4.3 Interpretation and limits',
        'Author Contributions': 'CRediT authorship contribution statement',
    }
    for p in ps:
        if p.text in changes:
            p.text = changes[p.text]
    # These seven paragraphs describe future models and junction uncertainty, not experiments done.
    assert ps[32].text.startswith('4.1 ') and ps[41].text == '4 Discussion'
    anchor = ps[41]._p
    for p in ps[32:39]:
        anchor.addnext(p._p)
        anchor = p._p
    ps[54].text = ('Tristan D. McRae: Conceptualization, Project administration. '
                   'The author conceived and directed the project and is responsible for its content. '
                   'AI assistance with analysis and manuscript preparation is disclosed below.')
    # Preserve the submitted AI disclosure verbatim, in the journal's requested separate location.
    ai = next(p for p in d.paragraphs if p.text.startswith('Use of artificial intelligence.'))
    refs = next(p for p in d.paragraphs if p.text == 'References')
    refs._p.addprevious(ai._p)
    head = OxmlElement('w:p')
    ai._p.addprevious(head)
    from docx.text.paragraph import Paragraph
    aihead = Paragraph(head, ai._parent)
    aihead.text = 'Declaration of generative AI and AI assisted technologies'
    aihead.style = 'Heading 2'
    d.core_properties.title = TITLE
    d.core_properties.subject = 'Computational Biology and Chemistry full-length research article'
    for p in d.paragraphs:
        if p.style.name == 'Horizontal Line':
            p._p.getparent().remove(p._p)
    for style in d.styles:
        if style.type == 1:
            style.font.color.rgb = RGBColor(0, 0, 0)
            style.paragraph_format.line_spacing = 2.0
        for border in list(style.element.xpath('.//w:pBdr')):
            border.getparent().remove(border)
    for section in d.sections:
        section.top_margin = section.bottom_margin = Cm(3)
        section.left_margin = section.right_margin = Cm(3)
        section.footer_distance = Cm(1.5)
        footer = section.footer.paragraphs[0]
        footer.alignment = 1
        field = OxmlElement('w:fldSimple')
        field.set(qn('w:instr'), 'PAGE')
        footer._p.append(field)
    for p in d.paragraphs:
        p.paragraph_format.line_spacing = 2.0
        if p.text in ['Tables', 'Figure legends']:
            p.paragraph_format.page_break_before = True
    for table in d.tables:
        table.autofit = False
        widths = [0.95, 1.85, 0.65, 1.35, 1.0] if len(table.columns) == 5 else [0.8, 1.9, 1.75, 1.35]
        for col, width in zip(table.columns, widths):
            col.width = Inches(width)
        for i, row in enumerate(table.rows):
            for cell, width in zip(row.cells, widths):
                cell.width = Inches(width)
                shd = OxmlElement('w:shd')
                shd.set(qn('w:fill'), 'FFFFFF')
                cell._tc.get_or_add_tcPr().append(shd)
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = i < len(table.rows)-1
                    for run in p.runs:
                        run.font.size = Pt(10)
        for el in list(table._tbl.xpath('.//w:shd')):
            el.set(qn('w:fill'), 'FFFFFF')
        for borders in table._tbl.xpath('.//w:tblBorders | .//w:tcBorders'):
            for el in borders:
                if el.tag in [qn('w:left'), qn('w:right'), qn('w:insideV'), qn('w:start'), qn('w:end')]:
                    el.set(qn('w:val'), 'nil')
    for p in d.paragraphs:
        if p.text.startswith('Table 2.'):
            p.paragraph_format.page_break_before = True
    d.save(HERE / 'manuscript.docx')
    # Editable table XML and all original sequence/figure bytes remain unchanged.
    assert [[list(c.text for c in row.cells) for row in t.rows] for t in d.tables] == [[list(c.text for c in row.cells) for row in t.rows] for t in original.tables]
    retained = []
    for source, name in [('submission/fusion-junction-aso-sequences.csv', 'fusion-junction-aso-sequences.csv'),
                         ('submission/figure-1.eps', 'figure-1.eps'),
                         ('aso-multipartner-seam.png', 'figure-1.png'),
                         ('aso-multipartner-seam.svg', 'figure-1.svg'),
                         ('submission/supplementary-file-2.pdf', 'original-v3-revision-note.pdf')]:
        src = BASE / source
        shutil.copyfile(src, HERE / name)
        retained.append({'source': str(src.relative_to(HERE.parents[3])), 'output': name,
                         'sha256': sha(src), 'unchanged': sha(src) == sha(HERE / name)})
    note = (BASE / 'submission/revision-note.md').read_text(encoding='utf-8')
    note_body = re.sub(r'^---\n.*?\n---\n', '', note, flags=re.S)
    note_body = note_body.replace('The release contains build_data.py and data-build-stamp.json.', 'The preserved 4 September release contains build_data.py and data-build-stamp.json.')
    note_body = note_body.replace('This note accompanies the manuscript “NR4A3 fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment.”',
                                  'This note accompanies the journal-tailored manuscript “' + TITLE + '”.')
    supplement = simple_doc('Supplementary File 2', [])
    for block in re.split(r'\n\s*\n', note_body.strip()):
        if block.startswith('# '):
            continue
        if block.startswith('## '):
            supplement.add_paragraph(block[3:], 'Heading 1')
        else:
            supplement.add_paragraph(' '.join(block.splitlines()))
    supplement.add_paragraph('Journal presentation update', 'Heading 1')
    supplement.add_paragraph('The Computational Biology and Chemistry package presents the completed computational work in numbered sections. The model-correspondence discussion is moved from Results to Discussion; proposed experimental evaluation remains unperformed. The title, abstract, highlights and graphical abstract summarize the same completed results. Sequence rows, numerical model outputs, tables and the original scientific figure are unchanged from Qeios version 3. The historical archive limitations and the interpretation corrections described above remain in force.')
    supplement.save(HERE / 'supplementary-file-2.docx')
    simple_doc('Highlights', HIGHLIGHTS).save(HERE / 'highlights.docx')
    (HERE / 'highlights.txt').write_text('\n'.join(HIGHLIGHTS) + '\n', encoding='utf-8')
    legends = Document(BASE / 'submission/figure-legends.docx')
    legends.paragraphs[0].text = 'Figure legends for ' + TITLE
    legends.save(HERE / 'figure-legends.docx')
    cover = [
        'Dear Editors,',
        'Please consider “' + TITLE + '” as a Full-length research article in Computational Biology and Chemistry.',
        'This computational study designs 190 antisense gapmers across 38 modelled NR4A3 fusion junctions and compares conventional near-match screening with contiguous parent-transcript pairing through the catalytic gap. It provides reproducible sequence records, threshold sensitivity and a negative limitation: the strongest exon-terminus control does not resolve a disease-specific excess of parent liability. It reports no laboratory validation or therapeutic window.',
        'The manuscript develops the completed computational results and places proposed model testing in Discussion. Its sequence records, numerical results and original figure remain unchanged from the submitted Qeios version 3 (https://www.qeios.com/read/VL3LJR.3). The historical code and analysis archive is https://doi.org/10.5281/zenodo.22229096; the accompanying revision note distinguishes that archive from corrected interpretations in the present package.',
        'We request standard subscription publication with online-only color. Optional open access, print color and paid companion-journal publication are not requested.',
        'The submitted author-interest, funding and AI disclosures are retained in the manuscript. Final personal author declarations and journal submission remain for the author to complete.',
        'Sincerely,', 'Tristan D. McRae', 'Independent researcher, unaffiliated', 'trimcrae@gmail.com',
    ]
    simple_doc('Cover letter', cover).save(HERE / 'cover-letter.docx')
    # Text source/readback retains full reference and table text for independent review.
    blocks = []
    for child in d.element.body:
        if child.tag == qn('w:p'):
            p = Paragraph(child, d._body)
            prefix = '# ' if p.style.name == 'Title' else '## ' if p.style.name.startswith('Heading 2') else '### ' if p.style.name == 'Heading 3' else ''
            if p.text:
                blocks.append(prefix + p.text)
        elif child.tag == qn('w:tbl'):
            from docx.table import Table
            t = Table(child, d._body)
            blocks.append('\n'.join('| ' + ' | '.join(c.text for c in row.cells) + ' |' for row in t.rows))
    (HERE / 'manuscript-readback.txt').write_text('\n\n'.join(blocks), encoding='utf-8')
    graphical_abstract()
    (HERE / 'graphical-abstract-caption.txt').write_text('Computational design and parent pairing results from the existing ASO analysis. The ten-base-pair full-gap criterion is adopted, not a measured cleavage threshold. The exon-terminus null leaves disease-specific excess unresolved. This schematic was prepared with OpenAI Codex assistance from the reported results; it introduces no new measurement or analysis.\n', encoding='utf-8')
    manifest = {'baseline_scientific_commit': '3dc59c67654a4dfc5a6d0b842f12a732e6aeda89',
                'baseline_submitted_docx_sha256': sha(submitted), 'title': TITLE,
                'abstract_words': len(ABSTRACT.split()), 'highlight_lengths': [len(x) for x in HIGHLIGHTS],
                'unchanged_tables': True, 'retained_files': retained,
                'changed_claims': 'No changed scientific claim. Revised title/abstract foreground completed computational results; model discussion moved, proposed work remains unperformed.',
                'render_verification': 'pending', 'independent_review': 'pending',
                'generator_sha256': sha(Path(__file__)),
                'outputs': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)}
                            for p in sorted(HERE.iterdir()) if p.suffix in ['.docx','.pdf','.eps','.png','.svg','.csv','.txt']]}
    (HERE / 'generation-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({'abstract_words': manifest['abstract_words'], 'outputs': len(manifest['outputs']),
                      'table_values_unchanged': True, 'render': 'pending'}))

def graphical_abstract():
    """Vector schematic of reported results; no new measurements or decorative inferred data."""
    c = canvas.Canvas(str(HERE / 'graphical-abstract.pdf'), pagesize=(1328, 531))
    c.setTitle('Computational NR4A3 junction gapmer design and parent pairing')
    c.setFillColor(HexColor('#172b3a'))
    c.setFont('Helvetica-Bold', 32)
    c.drawString(45, 475, 'NR4A3 junction gapmers: design does not establish discrimination')
    columns = [(45, 'DESIGN', ['38 modelled in-frame junctions', '190 junction-spanning 16-mers']),
               (480, 'PARENT PAIRING', ['87/190 designs (45.8%)', 'Full-gap pairing at adopted 10-bp cut']),
               (915, 'INTERPRETATION', ['Exon-terminus null: 40.6%', 'Disease-specific excess unresolved'])]
    for x, heading, lines in columns:
        c.setFont('Helvetica-Bold', 24)
        c.drawString(x, 360, heading)
        c.setFont('Helvetica', 22)
        for i, line in enumerate(lines):
            c.drawString(x, 305-i*42, line)
    c.setStrokeColor(HexColor('#457b9d'))
    c.setLineWidth(3)
    for x in [420, 855]:
        c.line(x, 325, x+35, 325)
        c.line(x+35, 325, x+25, 334)
        c.line(x+35, 325, x+25, 316)
    c.setFont('Helvetica-Bold', 25)
    c.drawString(45, 165, '10 bp is a screening convention, not a measured cleavage threshold')
    c.setFont('Helvetica', 23)
    c.drawString(45, 115, 'Patient junction and cell-model correspondence remain limiting.')
    c.drawString(45, 73, 'Computational predictions only; no cleavage, efficacy or safety established.')
    c.save()

if __name__ == '__main__':
    build()
