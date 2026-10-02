import pathlib,json,hashlib,datetime
p=pathlib.Path(r"C:/Users/mcrae/.codex/private/emc-continuation-20261002/checkpoint03-aso")
d=json.loads((p/"primary-metadata.json").read_text(encoding="utf-8"))
expected={"fusion":"8634690","construct":"31020999","models":"36316541","junction_aso":"1794439","pfred":"33481821","cell_offtarget":"31637814","specificity":"25072142"}
for r in d["records"]:
 assert r["status"]==200 and r["hit_count"]==1 and r["metadata"][0]["id"]==expected[r["name"]]
 r["identity_verified"]=True;r["pubmed_url"]="https://pubmed.ncbi.nlm.nih.gov/"+r["metadata"][0]["id"]+"/"
 r["abstract_read"]=True
 for m in r["metadata"]:m.pop("abstractText",None)
(p/"primary-metadata.json").write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
d=json.loads((p/"fulltext-receipts.json").read_text())
reading={"construct":["Cells and constructs","The type of chimera dictates biology and transcriptional profile of the two EMC variants"],
"models":["Molecular characterization of the ex vivo cell models","Molecular characterization of USZ20-EMC1 and USZ22-EMC2","Figure4 textual legend"],
"pfred":["Materials and methods: off-target annotation paragraphs on PLOS publisher HTML"],
"cell_offtarget":["Discussion: human-cell expression analysis, qPCR follow-up and chemistry/length-dependent complementarity interpretation"],
"specificity":["Selected methods paragraphs","PLOS Results/Figures8-9 and Discussion: RNase H1 context and off-target cleavage"]}
for r in d["records"]:
 if "sections" in r:r["selected_sections_emitted"]=r.pop("sections")
 r["read_scope"]="Bounded relevant reading; initial emitted text was truncated, not every emitted paragraph was inspected."
 r["sections_actually_used"]=reading[r["name"]]
d["additional_web_reading"]=[
 {"url":"https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0238753","date":"2026-10-02","scope":"Materials and methods paragraphs at publisher page lines282-285","raw_response_hash_available":False},
 {"url":"https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0101752","date":"2026-10-02","scope":"Results/Figures8-9 and Discussion at publisher page lines383-473","raw_response_hash_available":False},
 {"url":"https://www.gencodegenes.org/human/release_50.html","date":"2026-10-02","scope":"FASTA ALL transcript resource definition lines79-82","raw_response_hash_available":False},
 {"url":"https://doi.org/10.1093/hmg/4.12.2219","date":"2026-10-02","outcome":"web tool inaccessible-page error; HTTP status not exposed","raw_response_hash_available":False},
 {"url":"https://pubmed.ncbi.nlm.nih.gov/1794439/","date":"2026-10-02","scope":"Bibliographic pagination and abstract; no full text obtained","raw_response_hash_available":False}]
(p/"fulltext-receipts.json").write_text(json.dumps(d,indent=2)+"\n")
receipt=dict(schema="aso-bounded-primary-integration/1",date="2026-10-02",input_revision="4818db097f97ff8f862cd02bb9a2ddcf6c76cb71",
 input_draft_git_blob="e264ff94d88e2e3ad74954a4102fd5d5895d20dc",primary_records=7,fulltext_xml_fetches=5,
 scope="Citation/prose integration only; no sequence rerun, scientific count changes, comprehensive novelty review, outgoing rebuild or ultra review",
 accepted_brief_candidate="da7fab35440a74ea1c46c4ab197cead793333711",
 current_author_declarations=["This research received no funding","The author declares no competing interests"],
 artifacts={f.name:dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in p.iterdir() if f.is_file() and f.name not in ("integration-receipt.json","finalize_intake.py")})
(p/"integration-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,ensure_ascii=True))
