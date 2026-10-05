#!/usr/bin/env python3
"""Replay the frozen specimen/method/citation mask; never read result sections."""
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw-cache"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, obj):
    (BASE / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")

def section(root, identifier):
    found = [s for s in root.iter("sec") if s.get("id") == identifier]
    assert len(found) == 1
    return found[0]

def paragraphs(sec):
    return [" ".join("".join(p.itertext()).split()) for p in sec.findall("p")]

def sentences(text):
    return re.split(r"(?<=\.)\s+", text)

access = json.loads((BASE / "SOURCE-ACCESS.json").read_text())
for record in access:
    path = BASE / record["raw_path"]
    assert path.stat().st_size == record["bytes"]
    assert digest(path) == record["sha256"]

peg = ET.parse(RAW / "PEG10-primary.source").getroot()
tissue = paragraphs(section(peg, "Sec10"))[0]
assert "seven enchondromas" in tissue
assert "11 grade 1 chondrosarcomas" in tissue
assert "seven grade 2 chondrosarcomas" in tissue
assert "One normal bone specimen" in tissue
lines = paragraphs(section(peg, "Sec11"))
cell_identity_sentences = []
for paragraph in lines:
    for sentence in sentences(paragraph):
        if re.search(r"cell line|SW1353|Hs 819|ATCC|HepG2|C28/I2|UBE6T", sentence, re.I) and not re.search(r"plasmid|siRNA|signal|promoter|recombinant|vector|PEG10", sentence, re.I):
            cell_identity_sentences.append(sentence)
array = paragraphs(section(peg, "Sec14"))
array_platform_sentences = [s for p in array for s in sentences(p)
    if re.search(r"platform|Affymetrix|GeneChip|Gene 2\.0", s, re.I)
    and not re.search(r"regulat|fold|PEG10|knockdown|compar|signature", s, re.I)]
assert any("Gene 2.0 ST Array" in s for s in array_platform_sentences)
write("PEG10-SAFE-METHOD-AND-IDENTITY.json", {
    "source": "PMID29044189/PMC5647403/10.1038/s41598-017-13994-w",
    "source_sha256": digest(RAW / "PEG10-primary.source"),
    "mask": "Sec10 specimen identity; Sec11 identity sentences; Sec14 platform sentence only; no Results, mechanisms or gene outcome cells",
    "specimen_method_excerpt": tissue,
    "cell_identity_sentences": cell_identity_sentences,
    "array_platform_sentences": array_platform_sentences,
    "specimen_groups": [
        {"label": "enchondroma", "specimens": 7, "sex": {"male": 3, "female": 4}, "status": "source diagnosis differs from EMC"},
        {"label": "grade 1 chondrosarcoma", "specimens": 11, "sex": {"male": 3, "female": 8}, "status": "generic diagnosis; native-versus-skeletal individual identity pending"},
        {"label": "grade 2 chondrosarcoma", "specimens": 7, "sex": {"male": 3, "female": 4}, "status": "generic diagnosis; native-versus-skeletal individual identity pending"},
        {"label": "normal bone", "specimens": 1, "sex": {"male": 1}, "status": "normal context; from one grade1 CHS patient's amputated leg; not a new independent donor"}
    ],
    "tumor_specimens": 25,
    "generic_CHS_specimens": 18,
    "donor_limit": "No individual IDs or cross-assay case mapping inspected; 25 tumor specimens are not proved 25 independent donors.",
    "all_reported_line_labels": ["SW1353", "Hs 819.T", "C28/I2", "UBE6T-15", "hFOB 1.19", "MG-63", "HOS", "143B", "Saos-2", "HepG2"],
    "model_limit": "SW1353/Hs819.T are author chondrosarcoma labels, not source-authenticated native EMC. Other source line labels remain separate controls/materials, not patient units or a GPNMB condition map.",
    "measurement_limit": "Human Gene2.0 ST platform declaration is not verified GPNMB probe/sample coverage, source-linked native EMC expression or a published EMC-LGFMS comparison.",
    "supplement_declared": "41598_2017_13994_MOESM1_ESM.pdf; not fetched or interpreted"
})

igf = ET.parse(RAW / "IGF2BP3-pan-cancer-primary.source").getroot()
collection = paragraphs(section(igf, "s2_1"))[0]
allowed_collection = [s for s in sentences(collection) if any(w in s for w in ["Cancer Genome Atlas", "CCLE)", "24 tumor cell lines"])]
assert any("Cancer Genome Atlas" in s for s in allowed_collection)
assert any("CCLE" in s for s in allowed_collection)
write("IGF2BP3-SAFE-SOURCE-LINEAGE.json", {
    "source": "PMID36761737/PMC9905439/10.3389/fimmu.2023.1071675",
    "source_sha256": digest(RAW / "IGF2BP3-pan-cancer-primary.source"),
    "mask": "s2_1 source/collection identity sentences plus s7/s13 availability; no immune/HLA or molecular body, Results or selected gene outcomes",
    "collection_excerpts": allowed_collection,
    "availability_excerpts": paragraphs(section(igf, "s7")),
    "supplement_link_excerpt": paragraphs(section(igf, "s13")),
    "source_inputs": ["TCGA", "GTEx via UCSC Xena", "CCLE"],
    "declared_output_target": "IGF2BP3",
    "individual_native_EMC_map": "not supplied by these inspected source-method paragraphs",
    "GPNMB_target_or_probe_map": "not established; broad source RNA availability does not establish this article's GPNMB measurements",
    "all_condition_limit": "No individual TCGA/GTEx/CCLE diagnosis/condition roster or GPNMB native comparator map was inspected. Underlying source eligibility remains separate and cannot be excluded by this article's title or selected target.",
    "supplement_declared": "DataSheet_1.zip; not fetched or interpreted"
})

reviews = ET.parse(RAW / "review-citation-metadata.source").getroot()
selected = []
for article in reviews.findall("PubmedArticle"):
    pmid = article.findtext("./MedlineCitation/PMID")
    title = "".join(article.find("./MedlineCitation/Article/ArticleTitle").itertext())
    references = article.findall("./PubmedData/ReferenceList/Reference")
    matches = []
    for reference in references:
        citation = reference.findtext("Citation", "")
        if re.search(r"GPNMB|osteoactivin|DC.HIL|extraskeletal.{0,15}myxoid|fibromyxoid", citation, re.I):
            matches.append({"citation": citation, "IDs": [{"type": x.get("IdType"), "value": x.text} for x in reference.findall("./ArticleIdList/ArticleId")]})
    selected.append({"pmid": pmid, "title": title,
        "publication_types": [x.text for x in article.findall("./MedlineCitation/Article/PublicationTypeList/PublicationType")],
        "reference_count": len(references), "selected_gene_or_native_citation_metadata": matches})
assert selected == json.loads((BASE / "REVIEW-CITATION-ELIGIBILITY.json").read_text())

conference = ET.parse(RAW / "conference-PMC-metadata.source").getroot()
schema = []
for article in conference.findall("article"):
    ids = {x.get("pub-id-type"): x.text for x in article.findall("./front/article-meta/article-id")}
    body = article.find("body")
    schema.append({"article_ids": ids, "body_present": body is not None,
        "body_paragraphs": 0 if body is None else len(body.findall(".//p")), "supplement_links": []})
assert schema == json.loads((BASE / "CONFERENCE-SOURCE-SCHEMA.json").read_text())
print(json.dumps({"source_hashes_checked": 4, "tumor_specimens": 25, "generic_CHS_specimens_pending": 18,
    "review_metadata_records": len(selected), "conference_wrappers": len(schema), "new_outcome_cells": 0}))
