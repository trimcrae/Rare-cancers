#!/usr/bin/env python3
"""Build the public preprint catalogue using only explicitly curated public inputs."""
import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
PUBLIC_HOSTS = {"www.qeios.com", "qeios.com", "aixiv.science", "doi.org", "www.researchsquare.com"}
OUTPUT_FILES = {"index.html", "styles.css", "favicon.svg", "publications.json", ".nojekyll"}


def public_url(value):
    parts = urlsplit(value)
    if (parts.scheme != "https" or parts.hostname not in PUBLIC_HOSTS
            or parts.username or parts.password or parts.port or parts.query
            or "/private/" in parts.path):
        raise ValueError(f"Expected a canonical public article URL: {value!r}")
    return value


def load_catalogue():
    data = json.loads((HERE / "publications.json").read_text(encoding="utf-8"))
    checked = date.fromisoformat(data["updated_date"])
    papers = data["publications"]
    if not papers:
        raise ValueError("The public catalogue is empty")
    ids, urls = set(), set()
    for p in papers:
        for key in ("id", "title", "author", "venue", "version", "posted_date", "url", "topic", "summary"):
            if not isinstance(p.get(key), str) or not p[key].strip():
                raise ValueError(f"Missing public metadata: {key}")
        if p["status"] != "Preprint" or not re.fullmatch(r"[a-z0-9-]+", p["id"]):
            raise ValueError("Only identified, publicly posted preprints belong in this catalogue")
        if p["id"] in ids or p["url"] in urls:
            raise ValueError("Keep one latest posted version per paper")
        ids.add(p["id"])
        urls.add(p["url"])
        public_url(p["url"])
        if p.get("availability") not in ("available", "unverified"):
            raise ValueError("Record the live venue availability for each paper")
        if p["availability"] == "unverified" and not p.get("availability_note"):
            raise ValueError("Explain unverified venue availability")
        if p.get("doi_url"):
            public_url(p["doi_url"])
            if p["doi_url"] != "https://doi.org/" + p["doi"]:
                raise ValueError("DOI and DOI link disagree")
        if date.fromisoformat(p["posted_date"]) > checked:
            raise ValueError("A posting cannot be newer than its verification")
    return data, sorted(papers, key=lambda p: (p["posted_date"], p["id"]), reverse=True)


def nice_date(value):
    d = date.fromisoformat(value)
    return f"{d.day} {d.strftime('%b %Y')}"


def card(p, index):
    e = lambda key: escape(p[key], quote=True)
    uncertain = p["availability"] == "unverified"
    version_prefix = "Last confirmed: " if uncertain else ""
    link_label = "Check venue" if uncertain else "Read preprint"
    availability = (f'<p class="availability-note">{e("availability_note")}</p>' if uncertain else '')
    latest = '<span class="latest-label">Latest release</span>' if index == 0 else ''
    doi = (f'<a class="doi" href="{e("doi_url")}" aria-label="DOI for {e("title")}">DOI ↗</a>'
           if p.get("doi_url") else '')
    return f'''<article class="paper{' featured' if index == 0 else ''}" id="{e('id')}">
      <div class="paper-top"><span class="topic">{e('topic')}</span>{latest}</div>
      <div class="paper-meta"><span>{e('venue')} · {version_prefix}v{e('version')}</span><time datetime="{e('posted_date')}">{nice_date(p['posted_date'])}</time></div>
      <h3><a href="{e('url')}">{e('title')}</a></h3>
      {availability}
      <p class="summary">{e('summary')}</p>
      <p class="author">{e('author')}</p>
      <div class="paper-links"><a class="read-link" href="{e('url')}" aria-label="{link_label}: {e('title')}">{link_label} <span aria-hidden="true">↗</span></a>{doi}</div>
    </article>'''


def build(out):
    data, papers = load_catalogue()
    site_url = "https://trimcrae.github.io/Rare-cancers/"
    structured = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "EMC Research — Preprints",
                  "url": site_url, "hasPart": [{"@type": "ScholarlyArticle", "headline": p["title"],
                  "url": p["url"], "datePublished": p["posted_date"], "version": p["version"],
                  "author": {"@type": "Person", "name": p["author"]}} for p in papers if p["availability"] == "available"]}
    html = (HERE / "index.template.html").read_text(encoding="utf-8")
    replacements = {"{{PAPERS}}": "\n".join(card(p, i) for i, p in enumerate(papers)),
                    "{{COUNT}}": str(len(papers)), "{{COUNT_PADDED}}": f"{len(papers):02}",
                    "{{UPDATED}}": nice_date(data["updated_date"]), "{{UPDATED_ISO}}": data["updated_date"],
                    "{{LATEST_DATE}}": nice_date(papers[0]["posted_date"]),
                    "{{STRUCTURED_DATA}}": json.dumps(structured, ensure_ascii=False).replace("<", "\\u003c"),
                    "{{SITE_URL}}": site_url}
    for token, value in replacements.items():
        html = html.replace(token, value)
    if re.search(r"\{\{[A-Z_]+\}\}", html):
        raise ValueError("Unresolved template field")
    # Fail closed if a reused output directory contains anything outside the public allowlist.
    out = out.resolve()
    if out == HERE or HERE.is_relative_to(out):
        raise ValueError("Build output must not overwrite source or its parents")
    if out.exists() and any(p.name not in OUTPUT_FILES or p.is_dir() or p.is_symlink() for p in out.iterdir()):
        raise ValueError("Output directory contains unexpected files; inspect it before publishing")
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8", newline="\n")
    for name in ("styles.css", "favicon.svg"):
        shutil.copyfile(HERE / name, out / name)
    (out / "publications.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(papers)} posted preprints into {out}; metadata verified {data['updated_date']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "_site")
    args = parser.parse_args()
    build(args.output)
