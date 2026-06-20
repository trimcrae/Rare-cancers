#!/usr/bin/env node
// Scaffold a new cancer page.
// Usage: node scripts/new-cancer.mjs <slug> "Full Name" "ABBR" ["Category"]
// Example: node scripts/new-cancer.mjs ascps "Alveolar Soft Part Sarcoma" "ASPS" "Soft-tissue sarcoma"
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const [slug, name, abbr, category = "Rare cancer"] = process.argv.slice(2);

if (!slug || !name || !abbr) {
  console.error('Usage: node scripts/new-cancer.mjs <slug> "Full Name" "ABBR" ["Category"]');
  process.exit(1);
}
if (!/^[a-z0-9-]+$/.test(slug)) { console.error("slug must be lowercase letters, numbers and hyphens only"); process.exit(1); }

const dataPath = join(root, "data", "cancers", `${slug}.json`);
const pageDir = join(root, "cancers", slug);
if (existsSync(dataPath) || existsSync(pageDir)) { console.error(`"${slug}" already exists - aborting.`); process.exit(1); }

const today = new Date().toISOString().slice(0, 10);

// data file from template
const template = JSON.parse(readFileSync(join(root, "templates", "cancer.template.json"), "utf8"));
template.meta.slug = slug;
template.meta.name = name;
template.meta.abbreviation = abbr;
template.meta.summary = `REPLACE one-paragraph plain-language summary of ${name}.`;
template.meta.lastReviewed = today;
const q = encodeURIComponent(name);
template.studies.liveSearches = [
  { label: "PubMed", url: `https://pubmed.ncbi.nlm.nih.gov/?term=${q}` },
  { label: "Europe PMC", url: `https://europepmc.org/search?query=${q}` },
  { label: "ClinicalTrials.gov", url: `https://clinicaltrials.gov/search?cond=${q}` },
  { label: "Google Scholar", url: `https://scholar.google.com/scholar?q=${q}` },
];
writeFileSync(dataPath, JSON.stringify(template, null, 2) + "\n");

// page shell
const shell = readFileSync(join(root, "templates", "cancer-shell.html"), "utf8")
  .replaceAll("__SLUG__", slug).replaceAll("__NAME__", name).replaceAll("__ABBR__", abbr);
mkdirSync(pageDir, { recursive: true });
writeFileSync(join(pageDir, "index.html"), shell);

// add to index.json
const indexPath = join(root, "data", "index.json");
const index = JSON.parse(readFileSync(indexPath, "utf8"));
if (!index.cancers.some((c) => c.slug === slug)) {
  index.cancers.push({ slug, name, abbreviation: abbr, category, status: "draft", summary: `REPLACE short summary of ${name}.` });
  index.site.lastUpdated = today;
  writeFileSync(indexPath, JSON.stringify(index, null, 2) + "\n");
}

console.log(`Created:
  data/cancers/${slug}.json   <- fill this in (this is where all the content lives)
  cancers/${slug}/index.html  <- ready, no edits needed
  data/index.json             <- entry added (status: draft)

Next:
  1. Research & fill data/cancers/${slug}.json (see AGENTS.md for the playbook).
  2. node scripts/validate.mjs
  3. Set the index entry status to "published" when ready.`);
