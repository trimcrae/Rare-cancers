#!/usr/bin/env node
// Dependency-free render smoke test.
// Renders every data/cancers/<slug>.json through the real assets/js/cancer.js
// using a minimal DOM shim, and asserts the page actually renders. This guards
// against the class of bug where a render-time error leaves the page blank.
// Run: node scripts/smoke-render.mjs
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

// ---- minimal DOM shim -------------------------------------------------
class El {
  constructor(tag) { this.tag = tag; this.children = []; this.parent = null; this.attrs = {}; this.id = null; this._cls = ""; this._html = ""; this.value = ""; this.listeners = {}; this.text = null; }
  set className(v) { this._cls = v; } get className() { return this._cls; }
  set innerHTML(v) { this._html = v; this.children = []; } get innerHTML() { return this._html; }
  setAttribute(k, v) { this.attrs[k] = v; if (k === "id") this.id = v; }
  getAttribute(k) { return this.attrs[k]; }
  addEventListener(t, fn) { (this.listeners[t] ||= []).push(fn); }
  appendChild(c) { c.parent = this; this.children.push(c); return c; }
  querySelectorAll(sel) {
    const tags = sel.split(",").map((s) => s.trim());
    const out = [];
    (function walk(n) { n.children.forEach((c) => { if (tags.includes(c.tag)) out.push(c); walk(c); }); })(this);
    return out;
  }
}
const connected = (n, docRoot) => { let p = n; while (p) { if (p === docRoot) return true; p = p.parent; } return false; };
const findById = (node, id, docRoot) => {
  if (node.id === id && connected(node, docRoot)) return node;
  for (const c of node.children) { const r = findById(c, id, docRoot); if (r) return r; }
  return null;
};
const text = (n) => (n.text != null ? n.text : "") + n.children.map(text).join("");
const find = (node, pred) => { if (pred(node)) return node; for (const c of node.children) { const r = find(c, pred); if (r) return r; } return null; };
const findAll = (node, pred, acc = []) => { if (pred(node)) acc.push(node); node.children.forEach((c) => findAll(c, pred, acc)); return acc; };

const cancerJs = readFileSync(join(root, "assets", "js", "cancer.js"), "utf8");
const files = readdirSync(join(root, "data", "cancers")).filter((f) => f.endsWith(".json"));
let failures = 0;

for (const file of files) {
  const slug = file.replace(/\.json$/, "");
  const docRoot = new El("#document");
  const appEl = new El("main"); appEl.setAttribute("id", "app"); docRoot.appendChild(appEl);

  global.document = {
    createElement: (t) => new El(t),
    createTextNode: (t) => { const n = new El("#text"); n.text = t; return n; },
    getElementById: (id) => findById(docRoot, id, docRoot),
    set title(v) {}, get title() { return ""; },
  };
  global.window = { CANCER_SLUG: slug, DATA_BASE: "" };
  global.fetch = async () => ({ ok: true, status: 200, json: async () => JSON.parse(readFileSync(join(root, "data", "cancers", file), "utf8")) });

  let threw = null;
  global.process.removeAllListeners("unhandledRejection");
  global.process.once("unhandledRejection", (e) => { threw = e; });

  eval(cancerJs);
  await new Promise((r) => setTimeout(r, 50)); // let the async IIFE finish

  const problems = [];
  if (threw) problems.push("render threw: " + threw.message);

  // error banner means the try/catch fired
  const banner = find(appEl, (n) => n._cls.includes("banner") && text(n).includes("display error"));
  if (banner) problems.push("error banner rendered: " + text(banner).slice(0, 80));

  const sections = findAll(appEl, (n) => n._cls.split(" ").includes("section")).map((s) => s.id);
  const required = ["overview", "studies", "outcomes", "filter", "treatments", "emerging", "trials", "monitoring", "support", "centers", "questions"];
  for (const id of required) if (!sections.includes(id)) problems.push("missing section: " + id);

  // at least one study link
  if (!find(appEl, (n) => n.tag === "a" && (n.attrs.href || "").includes("http"))) problems.push("no external links rendered");

  // exercise the outcomes filter end-to-end (regression guard for the blank-page bug class)
  const applyBtn = find(appEl, (n) => n.tag === "button" && text(n).trim() === "Apply filters");
  if (!applyBtn) {
    problems.push("Apply filters button not found");
  } else {
    try {
      applyBtn.listeners.click[0]();
      if (!find(appEl, (n) => text(n) === "patients pooled")) problems.push("filter produced no results stats");
    } catch (e) { problems.push("filter click threw: " + e.message); }
  }

  if (problems.length) {
    failures++;
    console.error(`FAIL ${slug}:`);
    problems.forEach((p) => console.error("   - " + p));
  } else {
    console.log(`OK   ${slug}: ${sections.length} sections rendered + filter works`);
  }
}

if (failures) { console.error(`\n${failures} page(s) failed to render.`); process.exit(1); }
console.log(`\nAll ${files.length} page(s) render cleanly.`);
