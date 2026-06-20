#!/usr/bin/env node
// Automated research-paper ingestion via the Europe PMC REST API.
//
// Europe PMC is an open, programmatic gateway to PubMed/PMC. One host
// (www.ebi.ac.uk) provides BOTH literature search AND open-access full-text XML,
// with no anti-bot blocking - unlike scraping publisher HTML (which 403s).
//
// Commands:
//   node scripts/fetch-paper.mjs search "<query>"        list matching papers (+ open-access flag)
//   node scripts/fetch-paper.mjs studies "<query>"       emit JSON ready to paste into a cancer file's studies.items
//   node scripts/fetch-paper.mjs fetch <PMCID|MED/<pmid>> download one paper's full text (open access only)
//   node scripts/fetch-paper.mjs sync "<query>"          fetch full text of every open-access hit into the cache
//
// Output cache: .cache/literature/ (git-ignored; raw full text is intermediate).
//
// NETWORK: this repo's environment is deny-by-default for egress. Add this host
// to the environment's network egress settings to enable fetching:
//   www.ebi.ac.uk
// (docs: https://code.claude.com/docs/en/claude-code-on-the-web)

import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const API = "https://www.ebi.ac.uk/europepmc/webservices/rest";
const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CACHE = join(ROOT, ".cache", "literature");
const UA = "rare-cancers-hub/1.0 (open-access research aggregation; +https://github.com/trimcrae/rare-cancers)";

async function api(url, asText = false) {
  let res;
  try {
    res = await fetch(url, { headers: { "User-Agent": UA, Accept: asText ? "application/xml" : "application/json" } });
  } catch (e) {
    console.error(`Network error reaching ${new URL(url).host}: ${e.message}`);
    blockedHint();
    process.exit(3);
  }
  const body = await res.text();
  if (!res.ok) {
    if (/allowlist/i.test(body)) { console.error(`\nNETWORK BLOCKED: ${body.trim()}`); blockedHint(); process.exit(3); }
    console.error(`HTTP ${res.status} from ${url}\n${body.slice(0, 300)}`);
    process.exit(4);
  }
  return asText ? body : JSON.parse(body);
}

function blockedHint() {
  console.error(`\nThis environment uses a deny-by-default network egress allowlist.`);
  console.error(`Add this host to the environment's network egress settings, then re-run:`);
  console.error(`   www.ebi.ac.uk        # Europe PMC: literature search + open-access full text`);
  console.error(`(optional, for wider coverage: eutils.ncbi.nlm.nih.gov, api.crossref.org)`);
  console.error(`Docs: https://code.claude.com/docs/en/claude-code-on-the-web\n`);
}

function normalize(r) {
  const url = r.doi ? `https://doi.org/${r.doi}`
    : r.pmcid ? `https://www.ncbi.nlm.nih.gov/pmc/articles/${r.pmcid}/`
    : `https://europepmc.org/article/${r.source}/${r.id}`;
  return {
    title: r.title, authors: r.authorString, journal: r.journalTitle, year: Number(r.pubYear) || r.pubYear,
    pmid: r.pmid, pmcid: r.pmcid, doi: r.doi, source: r.source, id: r.id,
    isOpenAccess: r.isOpenAccess === "Y", citedBy: r.citedByCount, url,
  };
}

async function search(query, pageSize = 100) {
  const url = `${API}/search?query=${encodeURIComponent(query)}&format=json&pageSize=${pageSize}&resultType=core&sort=P_PDATE_D%20desc`;
  const data = await api(url);
  return (data.resultList?.result || []).map(normalize);
}

// Europe PMC full-text XML is available for the open-access subset only.
async function fetchFullText(pmcid) {
  const xml = await api(`${API}/${pmcid}/fullTextXML`, true);
  return xml;
}

function xmlToText(xml) {
  return xml
    .replace(/<\?xml[\s\S]*?\?>/g, "")
    .replace(/<(table-wrap|fig|ref-list|xref|graphic|inline-formula)[\s\S]*?<\/\1>/g, " ")
    .replace(/<title>/g, "\n\n## ").replace(/<\/title>/g, "\n")
    .replace(/<\/(p|sec|abstract|article-title)>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/&#x?[0-9a-f]+;/gi, " ")
    .replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
}

const cmd = process.argv[2];
const arg = process.argv.slice(3).join(" ");

if (!cmd || !arg) {
  console.log("Usage:\n  fetch-paper.mjs search \"<query>\"\n  fetch-paper.mjs studies \"<query>\"\n  fetch-paper.mjs fetch <PMCID>\n  fetch-paper.mjs sync \"<query>\"");
  process.exit(arg ? 0 : 1);
}

if (cmd === "search") {
  const rows = await search(arg);
  console.log(`${rows.length} result(s) for "${arg}":\n`);
  for (const r of rows) console.log(`${r.isOpenAccess ? "[OA]" : "[  ]"} ${r.year}  ${r.pmcid || r.source + "/" + r.id}  ${r.title}`);
  console.log(`\n[OA] = open-access full text fetchable. Use: fetch-paper.mjs fetch <PMCID>`);
} else if (cmd === "studies") {
  // Emit entries shaped like a cancer file's studies.items (verify links before trusting).
  const rows = await search(arg);
  const items = rows.map((r) => ({ title: r.title, authors: r.authors, year: r.year, journal: r.journal, type: "", url: r.url, openAccessUrl: r.pmcid ? `https://www.ncbi.nlm.nih.gov/pmc/articles/${r.pmcid}/` : undefined, verified: false, notes: "" }));
  console.log(JSON.stringify(items, null, 2));
} else if (cmd === "fetch") {
  mkdirSync(CACHE, { recursive: true });
  const xml = await fetchFullText(arg);
  const text = xmlToText(xml);
  const base = join(CACHE, arg.replace(/[^\w.-]/g, "_"));
  writeFileSync(base + ".xml", xml);
  writeFileSync(base + ".txt", text);
  console.log(`Saved ${text.length.toLocaleString()} chars of full text -> ${base}.txt`);
} else if (cmd === "sync") {
  mkdirSync(CACHE, { recursive: true });
  const rows = await search(arg);
  const oa = rows.filter((r) => r.isOpenAccess && r.pmcid);
  console.log(`${rows.length} hits, ${oa.length} open-access. Fetching full text...`);
  const index = [];
  for (const r of oa) {
    try {
      const text = xmlToText(await fetchFullText(r.pmcid));
      const base = join(CACHE, r.pmcid);
      writeFileSync(base + ".txt", text);
      index.push({ ...r, cacheFile: `.cache/literature/${r.pmcid}.txt`, chars: text.length });
      console.log(`  OK  ${r.pmcid}  ${text.length.toLocaleString()} chars  ${r.title.slice(0, 60)}`);
    } catch (e) { console.error(`  ERR ${r.pmcid}: ${e.message}`); }
  }
  writeFileSync(join(CACHE, "_index.json"), JSON.stringify(index, null, 2));
  console.log(`\nCached ${index.length} paper(s). Index: .cache/literature/_index.json`);
} else {
  console.error(`Unknown command: ${cmd}`);
  process.exit(1);
}
