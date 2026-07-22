#!/usr/bin/env node
// fetch-grants-eligibility — pull applicant-eligibility detail for specific grants.gov
// opportunities via the public fetchOpportunity API, so we can decide whether an unaffiliated
// individual can actually apply (the coarse Search2 eligibility filter in method-watch.mjs is
// keyword-level; the fetchOpportunity synopsis carries the authoritative applicant types +
// eligibility prose). Runs on a CI runner (grants.gov is proxy-blocked from the dev sandbox).
//
// Usage:  node scripts/fetch-grants-eligibility.mjs <oppId> [<oppId> ...]
//   oppId = the numeric opportunity id from a grants.gov detail URL
//           (…/search-results-detail/<oppId>), e.g. 363268.
// Zero dependencies (Node 22 global fetch). NETWORK host: api.grants.gov.

const API = "https://api.grants.gov/v1/api/fetchOpportunity";

async function fetchOpp(id) {
  const r = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json", "User-Agent": "rare-cancers-grants" },
    body: JSON.stringify({ opportunityId: Number(id) }),
  });
  if (!r.ok) throw new Error(`grants.gov ${r.status}`);
  const j = await r.json();
  return j?.data || {};
}

function line(label, val) {
  if (val === undefined || val === null || val === "") return;
  console.log(`${label}: ${String(val).replace(/\s+/g, " ").trim()}`);
}

async function main() {
  const ids = process.argv.slice(2);
  if (!ids.length) {
    console.error("usage: node scripts/fetch-grants-eligibility.mjs <oppId> [<oppId> ...]");
    process.exit(2);
  }
  for (const id of ids) {
    console.log("\n===== OPPORTUNITY " + id + " =====");
    try {
      const d = await fetchOpp(id);
      const s = d.synopsis || {};
      line("Number", d.opportunityNumber || d.number);
      line("Title", d.opportunityTitle || d.title);
      line("Agency", `${d.agencyName || d.agency || ""} (${d.agencyCode || ""})`);
      line("Open", s.postingDate || s.openDate);
      line("Close", s.responseDate || s.closeDate);
      line("Award ceiling", s.awardCeiling);
      line("Award floor", s.awardFloor);
      line("Expected awards", s.numberOfAwards);
      line("Cost sharing required", s.costSharing);
      const types = (s.applicantTypes || []).map((t) => t.description || t.id).filter(Boolean);
      line("Applicant types", types.join(" | ") || "(none listed)");
      // The prose eligibility field is the authoritative one — print in full (unwrapped).
      const elig = (s.applicantEligibilityDesc || "").replace(/\s+/g, " ").trim();
      if (elig) console.log("Eligibility (verbatim): " + elig);
      else console.log("Eligibility (verbatim): (applicantEligibilityDesc empty — see other fields below)");
      // Fallback: the eligibility clarification may live in another field. Print every scalar
      // synopsis field that looks eligibility/info-bearing, plus any additional-info URL.
      for (const [k, v] of Object.entries(s)) {
        if (typeof v !== "string" || !v.trim()) continue;
        if (/eligib|additionalInformation|fundingActivityCategoryDesc|synopsisDesc/i.test(k)) {
          console.log(`  [${k}]: ${v.replace(/\s+/g, " ").trim().slice(0, 1200)}`);
        }
      }
      // Attachment / full-announcement PDF links (the authoritative eligibility lives here for
      // agencies like CDMRP that don't populate the structured eligibility field). Walk the
      // opportunity object for anything that looks like a downloadable document link.
      const links = new Set();
      const walk = (o) => {
        if (!o || typeof o !== "object") return;
        for (const [k, v] of Object.entries(o)) {
          if (typeof v === "string" && /(https?:\/\/|\/)[^ ]+\.(pdf|docx?|zip)$/i.test(v)) links.add(v);
          else if (typeof v === "string" && /link|url|href/i.test(k) && /^https?:\/\//.test(v)) links.add(v);
          else if (v && typeof v === "object") walk(v);
        }
      };
      walk(d);
      if (links.size) { console.log("  Document links:"); for (const l of links) console.log("    - " + l); }
      else console.log("  Document links: (none found in API — check the grants.gov detail page Related Documents)");
    } catch (e) {
      console.log(`fetch failed: ${e.message}`);
    }
  }
  console.log("\n===== END =====");
}

main().catch((e) => {
  console.error("fetch-grants-eligibility failed:", e);
  process.exit(1);
});
