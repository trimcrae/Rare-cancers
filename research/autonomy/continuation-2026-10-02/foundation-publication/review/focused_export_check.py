from pathlib import Path
import hashlib, json, re, difflib
from pypdf import PdfReader
root=Path(r"C:/Users/mcrae/.codex/private/emc-continuation-20261002/checkpoint07-foundation-root")
own=Path(r"C:/Users/mcrae/.codex/private/emc-continuation-20261002/checkpoint07-foundation-ultra")
priorpath=own/"pre-export-source.md"
b=priorpath.read_bytes()
if hashlib.sha256(b[:-1]).hexdigest()=="006ab3c2ebea1b7ce5633727b7466de07030f138e2b7688c3de44a423c1b8442":
    priorpath.write_bytes(b[:-1])
prior=priorpath.read_text(encoding="utf-8")
sourcepath=root/"source-identity-correspondence.md"
source=sourcepath.read_text(encoding="utf-8")
expected=prior.replace("**Author.** Tristan D. McRae\n\n","**Author.** Tristan D. McRae\n\nIndependent researcher, unaffiliated.\n\n",1)
expected=expected.replace("## Correspondence\n\nA genomic","## Introduction\n\nA genomic",1)
expected=expected.replace("recovered the original sample identifiers.\n\nWe compared all rows","recovered the original sample identifiers.\n\n## Correspondence\n\nWe compared all rows",1)
pdfpath=root/"Foundation-source-identity-correspondence.pdf"
reader=PdfReader(str(pdfpath))
page_text=[page.extract_text() for page in reader.pages]
extracted="\n\n".join(page_text)
supplied=(root/"rendered-text.txt").read_text(encoding="utf-8")
def compact(s):
    return re.sub(r"\s+","",s)
def visible_source(s):
    s=re.sub(r"\A---\n.*?\n---\n","",s,flags=re.S)
    s=re.sub(r"\[([^\]]+)\]\(([^)]+)\)",r"\1",s)
    s=re.sub(r"^#+\s+","",s,flags=re.M)
    s=s.replace("**","").replace("*","").replace("`","")
    lines=[]
    for line in s.splitlines():
        if re.fullmatch(r"\|[:| -]+\|",line.strip()): continue
        if line.startswith("|"): line=" ".join(x.strip() for x in line.strip("|").split("|"))
        lines.append(line)
    return "\n".join(lines)
def clean_pdf(s):
    return "\n".join(line for line in s.splitlines() if not line.startswith("Version of ") and not line.startswith("Research use only") and not re.fullmatch(r"Not peer reviewed\.\s*\d+",line.strip()) and not re.fullmatch(r"Table\s+1",line.strip()))
visible=visible_source(source)
left,right=compact(visible),compact(clean_pdf(extracted))
match=left==right
diff=[]
if not match:
    for op,i,j,k,l in difflib.SequenceMatcher(None,left,right,autojunk=False).get_opcodes():
        if op!="equal": diff.append({"op":op,"source":left[max(0,i-35):min(len(left),j+35)],"pdf":right[max(0,k-35):min(len(right),l+35)]})
links=re.findall(r"\[[^\]]+\]\(([^)]+)\)",source)
pdfuris=[]
for page in reader.pages:
    for ref in page.get("/Annots",[]):
        ann=ref.get_object()
        action=ann.get("/A",{})
        if action and "/URI" in action: pdfuris.append(str(action["/URI"]))
table_rows=[line for line in source.splitlines() if line.startswith("|") and not re.fullmatch(r"\|[:| -]+\|",line.strip())]
table_checks=[{"cells":[x.strip() for x in row.strip("|").split("|")],"present_in_order":compact(" ".join(x.strip() for x in row.strip("|").split("|"))) in compact(extracted)} for row in table_rows]
references=[line for line in source.splitlines() if re.match(r"^[1-7]\. ",line)]
ref_checks=[{"number":int(line[0]),"visible_text_matches":compact(visible_source(line)) in compact(extracted)} for line in references]
out={
"schema":"foundation-focused-export-checks/1",
"prior_source_sha256":hashlib.sha256(priorpath.read_bytes()).hexdigest(),
"source_sha256":hashlib.sha256(sourcepath.read_bytes()).hexdigest(),
"pdf_sha256":hashlib.sha256(pdfpath.read_bytes()).hexdigest(),
"pdf_bytes":pdfpath.stat().st_size,
"supplied_text_sha256":hashlib.sha256((root/"rendered-text.txt").read_bytes()).hexdigest(),
"source_changes_exactly_expected_affiliation_and_headings":expected==source,
"extractor":"pypdf 6.10.0, existing bundled Python",
"pages":len(reader.pages),
"normalized_complete_source_pdf_text_equal":match,
"normalization":"Remove Markdown/YAML presentation, retain link labels and all visible text, flatten table separators; remove only whitespace, renderer build stamp/footer/page numbers and duplicate standalone Table 1 label from PDF. No sentence or scientific-text deletion.",
"unexpected_text_differences":diff,
"independently_extracted_vs_supplied_text_equal_after_whitespace":compact(extracted)==compact(supplied),
"table_checks":table_checks,
"references":ref_checks,
"source_link_count":len(links),
"source_link_targets_all_present_as_pdf_annotations":all(url in pdfuris for url in links),
"missing_pdf_link_targets":[url for url in links if url not in pdfuris],
"pdf_link_annotation_count":len(pdfuris),
"renderer_added_build_stamps":[line for line in extracted.splitlines() if line.startswith("Version of ")],
"renderer_added_footers":[line for line in extracted.splitlines() if re.fullmatch(r"Not peer reviewed\.\s*\d+",line.strip())],
"retired_ASO_footer_absent":"Research use only" not in extracted,
"original_report_sha256":hashlib.sha256((own/"review.md").read_bytes()).hexdigest(),
"original_review_json_sha256":hashlib.sha256((own/"review.json").read_bytes()).hexdigest(),
"visual_inspection_performed":False
}
(own/"focused-export-checks.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
