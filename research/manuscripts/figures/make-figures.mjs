#!/usr/bin/env node
// Generate reproducible, data-driven manuscript figures from candidates.json.
// Zero dependencies; emits SVG (the repo is a static site). Re-run after the catalog
// changes:  node research/manuscripts/figures/make-figures.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const cands = JSON.parse(readFileSync(join(here, "../../hypotheses/candidates.json"), "utf8")).candidates;

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// ---------------------------------------------------------------------------
// Figure 1: evidence × novelty map — NOT a score ranking. Rows = how strong the
// EMC-specific evidence is; columns = how novel the hypothesis is. The structure
// (imatinib alone in evidenced-but-known; an empty novel×clinical cell) is the point.
// ---------------------------------------------------------------------------
const FIG_LABEL = {
  "imatinib-kit-subset": "Imatinib (KIT-mut)",
  "vegfr-tki-extension": "VEGFR-TKIs (rego/cabo/lenva…)",
  "zaltoprofen-pparg": "Zaltoprofen (PPARγ)",
  "carfilzomib-proteasome": "Carfilzomib",
  "venetoclax-bcl2": "Venetoclax",
  "anthracycline-combination-synergy": "Anthracycline + carfilzomib/venetoclax",
  "hdac-inhibitors": "HDAC (romidepsin/panobinostat)",
  "brigatinib-screen-hit": "Brigatinib",
  "cdk4-6-inhibitors": "CDK4/6 (palbociclib)",
  "pioglitazone-pparg": "Pioglitazone (PPARγ)",
  "ntrk-inhibitors": "NTRK (laro/entrectinib)",
  "nr4a3-modulation": "NR4A3/NOR1 modulation",
  "transcriptional-bet-cdk": "BET / CDK7–9",
  "mrna-vaccine-checkpoint": "mRNA-vaccine + checkpoint",
};
const ROWS = [
  ["clinical", "Clinical (EMC patient)"],
  ["clinical-class", "Clinical (class)"],
  ["in-vivo", "In-vivo (animal EMC)"],
  ["ex-vivo", "Ex-vivo (EMC models)"],
  ["genomic", "Genomic / IHC"],
  ["mechanistic", "Mechanistic only"],
];
const COLS = [[1, "Known (tried)"], [2, "Partly novel"], [3, "Novel (untried)"]];
const cell = {};
for (const c of cands) {
  const ri = ROWS.findIndex((r) => r[0] === c.evidenceType);
  const ci = COLS.findIndex((co) => co[0] === c.scores.novelty);
  if (ri < 0 || ci < 0) continue;
  (cell[ri + "_" + ci] = cell[ri + "_" + ci] || []).push(FIG_LABEL[c.id] || c.drug);
}
const gPadL = 156, gPadT = 78, colW = 198, labelH = 15, rowMinH = 36;
const rowH = ROWS.map((_, ri) => {
  let mx = 0;
  for (let ci = 0; ci < COLS.length; ci++) mx = Math.max(mx, (cell[ri + "_" + ci] || []).length);
  return Math.max(rowMinH, mx * labelH + 18);
});
const rowY = []; let acc = gPadT; for (const h of rowH) { rowY.push(acc); acc += h; }
const GW = gPadL + COLS.length * colW + 16, GH = acc + 50;
const leadZone = (ri, ci) => (ROWS[ri][0] === "in-vivo" || ROWS[ri][0] === "ex-vivo") && COLS[ci][0] >= 2;

const p = [];
p.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${GW}" height="${GH}" viewBox="0 0 ${GW} ${GH}" font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">`);
p.push(`<rect width="${GW}" height="${GH}" fill="#ffffff"/>`);
p.push(`<text x="16" y="26" font-size="15.5" font-weight="700" fill="#202124">EMC candidates by EMC-specific evidence × novelty — not a score ranking</text>`);
p.push(`<text x="16" y="45" font-size="11.5" fill="#5f6368">Rows: how strong the EMC evidence is (top = strongest). Columns: how novel the hypothesis is.</text>`);
p.push(`<text x="16" y="60" font-size="11.5" fill="#1b7837">Green = novel + functional EMC evidence = the actionable leads. Amber = evidenced but already known.</text>`);
COLS.forEach((co, ci) => p.push(`<text x="${gPadL + ci * colW + colW / 2}" y="${gPadT - 8}" font-size="11.5" font-weight="700" fill="#202124" text-anchor="middle">${esc(co[1])}</text>`));
ROWS.forEach((r, ri) => {
  const y = rowY[ri], h = rowH[ri];
  p.push(`<text x="${gPadL - 8}" y="${y + h / 2 + 3}" font-size="11" font-weight="700" fill="#202124" text-anchor="end">${esc(r[1])}</text>`);
  COLS.forEach((co, ci) => {
    const xx = gPadL + ci * colW, items = cell[ri + "_" + ci] || [];
    const known = r[0] === "clinical" && co[0] === 1;
    const fill = leadZone(ri, ci) ? "#e6f4ea" : known ? "#fff7e0" : "#fafafa";
    p.push(`<rect x="${xx}" y="${y}" width="${colW - 6}" height="${h - 6}" rx="4" fill="${fill}" stroke="#e0e0e0" stroke-width="1"/>`);
    items.forEach((lab, k) => p.push(`<text x="${xx + 9}" y="${y + 17 + k * labelH}" font-size="9.7" fill="#202124">• ${esc(lab)}</text>`));
    if (!items.length && (r[0] === "clinical" || r[0] === "clinical-class") && co[0] === 3)
      p.push(`<text x="${xx + colW / 2 - 3}" y="${y + h / 2 + 3}" font-size="10" font-style="italic" fill="#c5221f" text-anchor="middle">— none —</text>`);
  });
});
p.push(`<text x="16" y="${GH - 16}" font-size="10.5" fill="#c5221f">The “novel × clinical” cells are empty: no new drug has EMC clinical evidence — the field's core gap.</text>`);
p.push(`</svg>`);
const out = join(here, "candidate-landscape.svg");
writeFileSync(out, p.join("\n") + "\n");
console.log(`Wrote ${out} (evidence × novelty map)`);

// ---------------------------------------------------------------------------
// Figure 2: three-method triangulation + patient firewall (schematic)
// ---------------------------------------------------------------------------
function box(x, y, w, h, lines, opts = {}) {
  const { fill = "#ffffff", stroke = "#5f6368", bold = false, fs = 11.5, dash = "" } = opts;
  const s = [`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="${fill}" stroke="${stroke}" stroke-width="1.3"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`];
  const arr = Array.isArray(lines) ? lines : [lines];
  const cx = x + w / 2, startY = y + h / 2 - ((arr.length - 1) * (fs + 2)) / 2 + fs / 2 - 1;
  arr.forEach((t, i) => s.push(`<text x="${cx}" y="${startY + i * (fs + 2)}" font-size="${fs}" ${bold ? 'font-weight="700"' : ""} fill="#202124" text-anchor="middle">${esc(t)}</text>`));
  return s.join("\n");
}
function arrow(x1, y1, x2, y2, opts = {}) {
  const { stroke = "#5f6368", dash = "" } = opts;
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="1.4" marker-end="url(#ah)"${dash ? ` stroke-dasharray="${dash}"` : ""}/>`;
}

const FW = 800, FH = 420;
const f = [];
f.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${FW}" height="${FH}" viewBox="0 0 ${FW} ${FH}" font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">`);
f.push(`<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#5f6368"/></marker></defs>`);
f.push(`<rect width="${FW}" height="${FH}" fill="#ffffff"/>`);
f.push(`<text x="24" y="30" font-size="16" font-weight="700" fill="#202124">Three-method triangulation with a patient firewall</text>`);

// inputs
f.push(box(30, 60, 215, 54, ["Mechanism curation", "(expert, literature-driven)"], { fill: "#e8f0fe" }));
f.push(box(292, 60, 215, 54, ["Target→drug enumeration", "(DGIdb, reproducible)"], { fill: "#e8f0fe" }));
f.push(box(555, 60, 215, 54, ["Graph foundation model", "(TxGNN, zero-shot)"], { fill: "#fce8e6" }));

// catalogue
f.push(box(150, 175, 500, 56, ["Scored candidate catalogue — 14 existing drugs", "evidence tiers T0–T3 · priority score 0–18"], { fill: "#f1f3f4", bold: true }));

// arrows from curation + enumeration into catalogue (converge)
f.push(arrow(137, 114, 330, 173));
f.push(arrow(399, 114, 399, 173));
// TxGNN diverges -> side note (NOT into the catalogue)
f.push(arrow(662, 114, 662, 138, { stroke: "#c5221f", dash: "5,4" }));
f.push(`<text x="662" y="156" font-size="10.5" fill="#c5221f" text-anchor="middle">diverged — reported as a limitation;</text>`);
f.push(`<text x="662" y="169" font-size="10.5" fill="#c5221f" text-anchor="middle">no TxGNN hit promoted to a candidate</text>`);

// outputs
f.push(arrow(300, 231, 230, 300));
f.push(arrow(500, 231, 560, 300));
f.push(box(70, 302, 320, 60, ["Patient page", "only T3 (real EMC clinical evidence) + clinician review"], { fill: "#e6f4ea", stroke: "#1b7837" }));
f.push(box(440, 302, 320, 60, ["Manuscript & path-to-testing", "n-of-1 · basket trials · model validation · CURE ID"], { fill: "#fff7e0", stroke: "#b06000" }));
// firewall label on the patient-page arrow
f.push(`<text x="250" y="270" font-size="10.5" font-weight="700" fill="#1b7837" text-anchor="middle">FIREWALL</text>`);
f.push(`</svg>`);

const out2 = join(here, "triangulation.svg");
writeFileSync(out2, f.join("\n") + "\n");
console.log(`Wrote ${out2}`);

// ---------------------------------------------------------------------------
// Figure 3: TxGNN sparsity stress-test — where our leads rank across diseases
// ---------------------------------------------------------------------------
let comp = null;
try {
  comp = JSON.parse(readFileSync(join(here, "../../hypotheses/txgnn-relatives-comparison.json"), "utf8"));
} catch { /* comparison not present (e.g. fresh checkout) — skip Fig 3 */ }

if (comp && Array.isArray(comp.diseases) && comp.diseases.length) {
  const SW = 760, rowH = 70, top = 78, padL = 200, padR = 36;
  const axisW = SW - padL - padR;
  const SH = top + comp.diseases.length * rowH + 46;
  const sx = (pct) => padL + (Math.max(0, Math.min(100, pct)) / 100) * axisW;
  const g = [];
  g.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${SW}" height="${SH}" viewBox="0 0 ${SW} ${SH}" font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">`);
  g.push(`<rect width="${SW}" height="${SH}" fill="#ffffff"/>`);
  g.push(`<text x="24" y="28" font-size="15.5" font-weight="700" fill="#202124">TxGNN ranks our mechanism/enumeration leads low — for EMC and its commoner relatives</text>`);
  g.push(`<text x="24" y="46" font-size="11.5" fill="#5f6368">Each dot = one of our 31 candidate drugs, placed at its percentile in TxGNN's 7,957-drug indication ranking (right = better). | = median.</text>`);
  g.push(`<text x="24" y="62" font-size="11.5" fill="#c5221f">The relatives do not rank the leads any higher than EMC — refuting an "EMC-sparsity" explanation.</text>`);
  // axis ticks
  for (const v of [0, 25, 50, 75, 100]) {
    g.push(`<line x1="${sx(v)}" y1="${top - 10}" x2="${sx(v)}" y2="${top + comp.diseases.length * rowH - 16}" stroke="${v === 50 ? "#cfd8dc" : "#eceff1"}" stroke-width="1"${v === 50 ? ' stroke-dasharray="4,4"' : ""}/>`);
    g.push(`<text x="${sx(v)}" y="${top + comp.diseases.length * rowH - 2}" font-size="10" fill="#80868b" text-anchor="middle">${v}</text>`);
  }
  g.push(`<text x="${padL + axisW / 2}" y="${SH - 6}" font-size="10.5" fill="#5f6368" text-anchor="middle">percentile in TxGNN indication ranking (higher = ranked better)</text>`);
  comp.diseases.forEach((d, i) => {
    const cy = top + i * rowH + rowH / 2 - 8;
    g.push(`<text x="${padL - 12}" y="${cy - 4}" font-size="12" font-weight="700" fill="#202124" text-anchor="end">${esc(d.label)}</text>`);
    g.push(`<text x="${padL - 12}" y="${cy + 11}" font-size="10.5" fill="#5f6368" text-anchor="end">median ${d.relevantMedianPercentile} pct</text>`);
    g.push(`<line x1="${sx(0)}" y1="${cy}" x2="${sx(100)}" y2="${cy}" stroke="#e0e0e0" stroke-width="1"/>`);
    (d.relevantDrugRanks || []).filter((r) => r.rank).forEach((r) => {
      g.push(`<circle cx="${sx(r.percentile)}" cy="${cy}" r="3.2" fill="#2c7fb8" fill-opacity="0.55"/>`);
    });
    const m = d.relevantMedianPercentile;
    if (m != null) g.push(`<line x1="${sx(m)}" y1="${cy - 11}" x2="${sx(m)}" y2="${cy + 11}" stroke="#c5221f" stroke-width="2"/>`);
  });
  g.push(`</svg>`);
  const out3 = join(here, "stress-test.svg");
  writeFileSync(out3, g.join("\n") + "\n");
  console.log(`Wrote ${out3}`);
}
