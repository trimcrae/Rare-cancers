#!/usr/bin/env node
// Feasibility probe for roadmap #3 (TxGNN/CMap screen): is EMC even a node in the
// public TxGNN/PrimeKG knowledge graph (Harvard Dataverse doi:10.7910/DVN/IXA7BM)?
// Running the trained TxGNN model here is infeasible, so before building any screen we
// check coverage honestly. Prints to the CI log; commits nothing. No dependencies.

const DOI = "doi:10.7910/DVN/IXA7BM";
const BASE = "https://dataverse.harvard.edu/api";
const RX = /chondrosarcoma|myxoid|extraskeletal|sarcoma/i;

const j = (r) => r.json();

async function main() {
  console.log(`Listing files for ${DOI} ...`);
  const meta = await fetch(`${BASE}/datasets/:persistentId/?persistentId=${DOI}`).then(j);
  const files = (meta?.data?.latestVersion?.files || []).map((f) => ({
    name: f.dataFile.filename,
    id: f.dataFile.id,
    mb: +(f.dataFile.filesize / 1e6).toFixed(1),
  }));
  console.log(`Files (${files.length}):`);
  for (const f of files) console.log(`  ${String(f.id).padEnd(10)} ${String(f.mb).padStart(8)}MB  ${f.name}`);

  // Prefer a node / disease feature file; fall back to the full KG edge list.
  const pick =
    files.find((f) => /node/i.test(f.name)) ||
    files.find((f) => /disease/i.test(f.name)) ||
    files.find((f) => /kg\.csv/i.test(f.name)) ||
    files.sort((a, b) => a.mb - b.mb)[0];
  if (!pick) { console.log("No files found."); return; }
  console.log(`\nDownloading "${pick.name}" (${pick.mb}MB, id ${pick.id}) ...`);

  const text = await fetch(`${BASE}/access/datafile/${pick.id}`).then((r) => r.text());
  const lines = text.split(/\r?\n/);
  console.log(`Read ${lines.length} lines. Header: ${lines[0]?.slice(0, 200)}`);

  const hits = [...new Set(lines.filter((l) => RX.test(l)))];
  console.log(`\nLines matching /${RX.source}/ : ${hits.length}`);
  for (const h of hits.slice(0, 40)) console.log("  " + h.slice(0, 200));

  const emc = hits.filter((l) => /myxoid|extraskeletal/i.test(l));
  console.log(`\nEMC-SPECIFIC matches: ${emc.length}`);
  for (const h of emc.slice(0, 20)) console.log("  " + h.slice(0, 200));
  console.log(`\nVERDICT: ${emc.length ? "EMC IS representable in the KG" : (hits.length ? "no EMC node; chondrosarcoma/sarcoma parent present" : "no relevant disease node found")}`);
}

main().catch((e) => { console.error("PROBE ERROR:", e.message || e); process.exit(1); });
