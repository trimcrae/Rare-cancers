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

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const RETRYABLE = new Set([429, 500, 502, 503, 504]);

// Throws on failure (never exits the process) so callers decide whether one
// failed request is fatal (e.g. the initial search) or skippable (one paper in
// a 1000-paper sync). Errors carry .exitCode and .blocked for the top-level handler.
function apiError(message, { exitCode = 1, blocked = false } = {}) {
  const e = new Error(message); e.exitCode = exitCode; e.blocked = blocked; return e;
}
async function api(url, asText = false, attempts = 6) {
  for (let attempt = 1; attempt <= attempts; attempt++) {
    let res, body;
    try {
      res = await fetch(url, { headers: { "User-Agent": UA, Accept: asText ? "application/xml" : "application/json" } });
      body = await res.text();
    } catch (e) {
      if (attempt < attempts) { const w = 1000 * 2 ** (attempt - 1); console.error(`Network error (${e.message}); retry ${attempt}/${attempts - 1} in ${w}ms`); await sleep(w); continue; }
      throw apiError(`Network error reaching ${new URL(url).host}: ${e.message}`, { exitCode: 3, blocked: true });
    }
    if (res.ok) return asText ? body : JSON.parse(body);
    if (/allowlist/i.test(body)) throw apiError(`NETWORK BLOCKED: ${body.trim()}`, { exitCode: 3, blocked: true });
    if (RETRYABLE.has(res.status) && attempt < attempts) {
      const w = 1000 * 2 ** (attempt - 1);
      console.error(`HTTP ${res.status} from Europe PMC (transient); retry ${attempt}/${attempts - 1} in ${w}ms`);
      await sleep(w);
      continue;
    }
    throw apiError(`HTTP ${res.status} from ${url}\n${body.slice(0, 200)}`, { exitCode: 4 });
  }
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
    pubType: r.pubType || "", abstract: r.abstractText || "",
    isOpenAccess: r.isOpenAccess === "Y", citedBy: r.citedByCount, url,
  };
}

// Page through the ENTIRE result set with cursorMark so nothing is missed.
async function searchAll(query, { pageSize = 1000, max = Infinity } = {}) {
  let cursor = "*";
  const out = [];
  for (;;) {
    const url = `${API}/search?query=${encodeURIComponent(query)}&format=json&pageSize=${pageSize}&resultType=core&cursorMark=${encodeURIComponent(cursor)}`;
    const data = await api(url);
    const batch = (data.resultList?.result || []).map(normalize);
    out.push(...batch);
    const next = data.nextCursorMark;
    if (!batch.length || !next || next === cursor || out.length >= max) break;
    cursor = next;
  }
  return max === Infinity ? out : out.slice(0, max);
}

async function search(query, max = 200) {
  return searchAll(query, { max });
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

try {
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
  // Comprehensive: every matching record is catalogued (metadata + abstract),
  // and open-access ones additionally get full text. Nothing is dropped.
  const rows = await searchAll(arg);
  const oa = rows.filter((r) => r.isOpenAccess && r.pmcid);
  console.log(`${rows.length} total record(s); ${oa.length} open-access with fetchable full text. Building corpus...`);
  const index = [];
  let fetched = 0, failed = 0;
  for (const r of rows) {
    const rec = { ...r };
    if (r.isOpenAccess && r.pmcid) {
      try {
        const text = xmlToText(await fetchFullText(r.pmcid));
        writeFileSync(join(CACHE, r.pmcid + ".txt"), text);
        rec.fullTextFile = `${r.pmcid}.txt`;
        rec.chars = text.length;
        fetched++;
        if (fetched % 25 === 0) console.log(`  ...${fetched}/${oa.length} full texts fetched`);
        await sleep(120); // be polite to Europe PMC
      } catch (e) { failed++; console.error(`  ERR ${r.pmcid}: ${e.message}`); }
    }
    index.push(rec);
  }
  writeFileSync(join(CACHE, "_index.json"), JSON.stringify(index, null, 2));
  const withAbstract = index.filter((r) => r.abstract).length;
  console.log(`\nCatalogued ${index.length} record(s): ${fetched} full texts (${failed} failed), ${withAbstract} with abstracts.`);
  console.log(`Index: .cache/literature/_index.json`);
} else {
  console.error(`Unknown command: ${cmd}`);
  process.exit(1);
}
} catch (e) {
  if (e.blocked) blockedHint();
  console.error(e.message);
  process.exit(e.exitCode || 1);
}
