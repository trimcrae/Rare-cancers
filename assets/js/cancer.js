// Renders a full cancer page + interactive tools from data/cancers/<slug>.json.
// The page's thin shell sets window.CANCER_SLUG and window.DATA_BASE before loading this.
// No build step, no framework. Adding a new cancer requires only a new JSON data file.
(async function () {
  const SLUG = window.CANCER_SLUG;
  const BASE = window.DATA_BASE || "../../";

  // --- tiny DOM helper ---------------------------------------------------
  const el = (t, props = {}, kids = []) => {
    const n = document.createElement(t);
    Object.entries(props).forEach(([k, v]) => {
      if (v == null) return;
      if (k === "class") n.className = v;
      else if (k === "html") n.innerHTML = v;
      else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    });
    (Array.isArray(kids) ? kids : [kids]).forEach((c) => {
      if (c == null) return;
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return n;
  };
  const ext = (href, text) => el("a", { href, target: "_blank", rel: "noopener noreferrer" }, text || href);
  const list = (items, cls) => el("ul", { class: cls || "clean" }, (items || []).map((i) => el("li", {}, i)));

  const app = document.getElementById("app");
  const tocEntries = [];
  const sections = [];
  const addSection = (id, title, ...nodes) => {
    tocEntries.push({ id, title });
    sections.push(el("section", { class: "section", id }, [el("h2", {}, title), ...nodes]));
  };

  let data;
  try {
    data = await fetch(`${BASE}data/cancers/${SLUG}.json`).then((r) => {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    });
  } catch (e) {
    app.appendChild(el("div", { class: "wrap" }, el("p", { class: "banner" }, "Could not load data for this cancer. If previewing locally, serve over HTTP (e.g. `python3 -m http.server`).")));
    console.error(e);
    return;
  }

  const m = data.meta;
  document.title = `${m.name} (${m.abbreviation}) - Rare Cancer Info Hub`;

  try {
  // ---- HERO -------------------------------------------------------------
  const confPill = { draft: "warn", "literature-reviewed": "warn", "clinician-reviewed": "good" }[m.dataConfidence] || "warn";
  const hero = el("section", { class: "hero" }, [
    el("div", { class: "kicker" }, m.aliases && m.aliases.length ? "Also called: " + m.aliases.join(", ") : "Rare cancer"),
    el("h1", {}, `${m.name} (${m.abbreviation})`),
    el("p", { class: "tagline" }, m.patientFriendlyOneLiner || m.summary),
    el("div", { class: "spread", style: "margin-top:12px" }, [
      el("span", { class: "pill " + confPill }, "Data: " + m.dataConfidence),
      el("span", { class: "pill" }, "Last reviewed " + m.lastReviewed),
    ]),
  ]);

  // global disclaimer banner
  const topBanner = el("div", { class: "banner" }, [
    el("span", { html: `<strong>Not medical advice.</strong> This page is patient-built educational information, drafted from public literature and ${m.dataConfidence === "clinician-reviewed" ? "clinician-reviewed" : "<em>not yet clinician-reviewed</em>"}. It cannot replace your own sarcoma/oncology team.` }),
  ]);

  // ---- OVERVIEW ---------------------------------------------------------
  const ov = data.overview || {};
  const ovCards = el("div", { class: "grid cols-2" }, [
    ov.whatItIs && el("div", { class: "card" }, [el("div", { class: "kicker" }, "What it is"), el("p", {}, ov.whatItIs)]),
    ov.howCommon && el("div", { class: "card" }, [el("div", { class: "kicker" }, "How common"), el("p", {}, ov.howCommon)]),
    ov.typicalPatient && el("div", { class: "card" }, [el("div", { class: "kicker" }, "Who gets it"), el("p", {}, ov.typicalPatient)]),
    ov.molecular && el("div", { class: "card" }, [el("div", { class: "kicker" }, "Genetics / biomarkers"), el("p", {}, ov.molecular)]),
    ov.howDiagnosed && el("div", { class: "card" }, [el("div", { class: "kicker" }, "How it's diagnosed"), el("p", {}, ov.howDiagnosed)]),
    ov.commonSites && ov.commonSites.length && el("div", { class: "card" }, [el("div", { class: "kicker" }, "Where it occurs"), list(ov.commonSites)]),
  ].filter(Boolean));
  const ovExtra = ov.keyPointsForNewlyDiagnosed && ov.keyPointsForNewlyDiagnosed.length
    ? el("div", { class: "card" }, [el("div", { class: "kicker" }, "If you were just diagnosed"), list(ov.keyPointsForNewlyDiagnosed)]) : null;
  addSection("overview", "Overview", el("p", { class: "intro" }, m.summary), ovCards, ovExtra);

  // ---- STUDIES ----------------------------------------------------------
  const st = data.studies || {};
  const searchBtns = (st.liveSearches || []).map((s) => ext(s.url, s.label));
  const searchRow = searchBtns.length ? el("div", { class: "card" }, [
    el("div", { class: "kicker" }, "Find newly published studies"),
    el("div", { class: "grid cols-3", style: "margin-top:8px" }, searchBtns.map((b) => el("div", {}, b))),
  ]) : null;
  const studyCards = el("div", { class: "card" }, (st.items || []).map((s) =>
    el("div", { class: "study" }, [
      el("div", { class: "title" }, [ext(s.url, s.title)]),
      el("div", { class: "meta" }, `${s.authors ? s.authors + " - " : ""}${s.journal || ""}${s.year ? " (" + s.year + ")" : ""}`),
      el("div", {}, [
        s.type ? el("span", { class: "tag" }, s.type) : null,
        s.sampleSize ? el("span", { class: "tag" }, "n=" + s.sampleSize) : null,
        s.openAccessUrl ? ext(s.openAccessUrl, " free full text") : null,
        s.verified === false ? el("span", { class: "pill warn", style: "margin-left:6px" }, "verify link") : null,
      ].filter(Boolean)),
      s.notes ? el("div", { class: "notes muted" }, s.notes) : null,
    ])
  ));
  addSection("studies", "Every study we can find", el("p", { class: "intro" }, st.intro || ""), searchRow, studyCards);

  // ---- OUTCOMES (published) --------------------------------------------
  const oc = data.outcomes || {};
  const pubCards = el("div", { class: "results-stats" }, (oc.published || []).map((p) =>
    el("a", { class: "card", href: p.url, target: "_blank", rel: "noopener noreferrer" }, [
      el("div", { class: "stat" }, p.value),
      el("div", { class: "stat-label" }, p.measure),
      el("div", { class: "small muted" }, p.source || ""),
    ])
  ));
  const progList = (oc.prognosticFactors || []).map((f) =>
    el("li", {}, [
      el("span", { class: "pill " + (f.direction === "better" ? "good" : "warn") }, f.direction),
      " " + f.factor + (f.note ? " - " + f.note : ""),
    ])
  );
  const respList = (oc.treatmentResponse || []).map((r) =>
    el("li", {}, [el("strong", {}, r.therapy + ": "), r.result + " ", r.url ? ext(r.url, "(source)") : null])
  );
  addSection("outcomes", "Outcomes (from the published studies)",
    el("p", { class: "intro" }, oc.intro || ""),
    pubCards,
    progList.length ? el("div", { class: "card" }, [el("div", { class: "kicker" }, "What changes the outlook (prognostic factors)"), el("ul", { class: "clean" }, progList)]) : null,
    respList.length ? el("div", { class: "card" }, [el("div", { class: "kicker" }, "How it responds to treatment"), el("ul", { class: "clean" }, respList)]) : null
  );

  // ---- OUTCOMES FILTER TOOL (registry: pooled cohorts + individual cases) ----
  const reg = data.registry || {};
  const patients = reg.patients || [];
  const cohorts = reg.cohorts || [];
  const sample = reg.dataStatus === "SAMPLE_SYNTHETIC";

  const regBanner = reg.dataStatus !== "curated" ? el("div", { class: "banner" }, [
    el("span", { html: "<strong>" + (sample ? "Illustrative sample data." : "Real but limited data.") + "</strong> " + (reg.dataStatusBanner || "These rows are placeholder/sample data and not real individuals.") }),
  ]) : null;

  // filter controls
  const sites = Array.from(new Set(patients.map((p) => p.site).filter(Boolean))).sort();
  const treatments = Array.from(new Set(patients.map((p) => p.primaryTreatment).filter(Boolean))).sort();
  const sel = (id, label, opts) => el("div", {}, [
    el("label", { class: "field", for: id }, label),
    el("select", { id }, [el("option", { value: "" }, "Any"), ...opts.map((o) => el("option", { value: o.v != null ? o.v : o }, o.t != null ? o.t : o))]),
  ]);
  const num = (id, label, ph) => el("div", {}, [el("label", { class: "field", for: id }, label), el("input", { id, type: "number", placeholder: ph || "" })]);

  const controls = el("div", { class: "filter-grid" }, [
    num("f-ageMin", "Age from", "any"),
    num("f-ageMax", "Age to", "any"),
    sel("f-sex", "Sex", [{ v: "F", t: "Female" }, { v: "M", t: "Male" }]),
    sel("f-grade", "Grade", ["low", "high"]),
    sel("f-stage", "Stage at diagnosis", [{ v: "localized", t: "Localised" }, { v: "regional", t: "Regional" }, { v: "distant", t: "Metastatic" }]),
    num("f-sizeMin", "Size from (cm)", "any"),
    num("f-sizeMax", "Size to (cm)", "any"),
    sites.length ? sel("f-site", "Site", sites) : null,
    treatments.length ? sel("f-treatment", "Primary treatment", treatments) : null,
  ].filter(Boolean));

  const statsWrap = el("div", { class: "results-stats" });
  const tableWrap = el("div", { class: "table-scroll" });

  const median = (arr) => {
    if (!arr.length) return null;
    const s = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(s.length / 2);
    return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
  };
  const pct = (n, d) => (d ? Math.round((n / d) * 100) : 0);

  const breakdownWrap = el("div", { class: "table-scroll" });

  // a published cohort's fixed criteria only EXCLUDE it when they directly contradict a set filter;
  // a cohort that spans all values of a dimension still applies (it's broader evidence).
  function cohortMatches(c, f) {
    const cr = c.criteria || {};
    const clash = (k, val) => val && cr[k] && cr[k] !== val;
    if (clash("stage", f.stage) || clash("sex", f.sex) || clash("grade", f.grade) || clash("site", f.site) || clash("treatment", f.treatment)) return false;
    if (f.ageMin != null && c.ageMax != null && c.ageMax < f.ageMin) return false;
    if (f.ageMax != null && c.ageMin != null && c.ageMin > f.ageMax) return false;
    if (f.sizeMin != null && c.sizeMax != null && c.sizeMax < f.sizeMin) return false;
    if (f.sizeMax != null && c.sizeMin != null && c.sizeMin > f.sizeMax) return false;
    return true;
  }
  function patientMatches(p, f) {
    if (f.ageMin != null && !(p.age >= f.ageMin)) return false;
    if (f.ageMax != null && !(p.age <= f.ageMax)) return false;
    if (f.sex && p.sex !== f.sex) return false;
    if (f.grade && p.grade !== f.grade) return false;
    if (f.stage && p.stage !== f.stage) return false;
    if (f.sizeMin != null && !(p.sizeCm >= f.sizeMin)) return false;
    if (f.sizeMax != null && !(p.sizeCm <= f.sizeMax)) return false;
    if (f.site && p.site !== f.site) return false;
    if (f.treatment && p.primaryTreatment !== f.treatment) return false;
    return true;
  }
  const addMetric = (agg, m) => { if (m && m.denom) { agg.events += m.events; agg.denom += m.denom; } };

  function applyFilters() {
    const v = (id) => { const e = document.getElementById(id); return e ? e.value : ""; };
    const nv = (id) => (v(id) === "" ? null : Number(v(id)));
    const f = {
      ageMin: nv("f-ageMin"), ageMax: nv("f-ageMax"), sex: v("f-sex"), grade: v("f-grade"),
      stage: v("f-stage"), sizeMin: nv("f-sizeMin"), sizeMax: nv("f-sizeMax"),
      site: document.getElementById("f-site") ? v("f-site") : "",
      treatment: document.getElementById("f-treatment") ? v("f-treatment") : "",
    };
    renderResults(patients.filter((p) => patientMatches(p, f)), cohorts.filter((c) => cohortMatches(c, f)));
  }

  // collapse matched individual cases into one cohort-shaped row so they pool the same way
  function casesAsCohort(ps) {
    if (!ps.length) return null;
    const rec = { events: 0, denom: 0 }, met = { events: 0, denom: 0 }, dd = { events: 0, denom: 0 };
    ps.forEach((p) => {
      if (typeof p.localRecurrence === "boolean") { rec.denom++; if (p.localRecurrence) rec.events++; }
      if (p.stage !== "distant" && typeof p.metastasis === "boolean") { met.denom++; if (p.metastasis) met.events++; }
      if (typeof p.diseaseSpecificDeath === "boolean") { dd.denom++; if (p.diseaseSpecificDeath) dd.events++; }
    });
    return { label: "Individual published case reports", n: ps.length, pool: true, isCases: true,
      recurrence: rec, metastasis: met, diseaseDeath: dd,
      medianFollowupMonths: median(ps.map((p) => p.followupMonths).filter((x) => typeof x === "number")) };
  }

  function renderResults(outPatients, outCohorts) {
    statsWrap.innerHTML = "";
    breakdownWrap.innerHTML = "";
    tableWrap.innerHTML = "";

    // metastasis is an outcome only for entries not defined by metastasis-at-diagnosis
    const isBaselineMet = (c) => (c.criteria || {}).stage === "distant";
    const entries = outCohorts.map((c) => ({ ...c, metastasis: isBaselineMet(c) ? null : c.metastasis }));
    const caseRow = casesAsCohort(outPatients);
    if (caseRow) entries.push(caseRow);

    const pooled = entries.filter((e) => e.pool !== false);
    const totalN = pooled.reduce((s, e) => s + (e.n || 0), 0);
    const aRec = { events: 0, denom: 0 }, aMet = { events: 0, denom: 0 }, aDD = { events: 0, denom: 0 };
    pooled.forEach((e) => { addMetric(aRec, e.recurrence); addMetric(aMet, e.metastasis); addMetric(aDD, e.diseaseDeath); });

    const stat = (val, label, sub) => el("div", { class: "card" }, [el("div", { class: "stat" }, val), el("div", { class: "stat-label" }, label), sub ? el("div", { class: "small muted" }, sub) : null]);
    if (!entries.length) {
      statsWrap.appendChild(el("p", { class: "small muted", style: "padding:12px" }, "No matching studies or cases. Loosen the filters."));
      return;
    }
    statsWrap.appendChild(stat(String(totalN), "patients pooled", pooled.length + " source(s)"));
    if (aDD.denom) statsWrap.appendChild(stat(pct(aDD.denom - aDD.events, aDD.denom) + "%", "disease-specific survival", "crude, " + aDD.denom + " pts"));
    if (aRec.denom) statsWrap.appendChild(stat(pct(aRec.events, aRec.denom) + "%", "had local recurrence", "crude, " + aRec.denom + " pts"));
    if (aMet.denom) statsWrap.appendChild(stat(pct(aMet.events, aMet.denom) + "%", "developed metastasis", "crude, " + aMet.denom + " pts"));

    // ---- transparent breakdown: every contributing study/cohort ----
    const cell = (m, pctVal, txt) => (m && m.denom) ? (pct(m.events, m.denom) + "% (" + m.events + "/" + m.denom + ")") : (pctVal != null ? pctVal + "%" : (txt || "-"));
    const dssCell = (e) => e.fiveYearDSS != null ? e.fiveYearDSS + "% (5-yr)" : (e.diseaseDeath && e.diseaseDeath.denom ? pct(e.diseaseDeath.denom - e.diseaseDeath.events, e.diseaseDeath.denom) + "% (crude)" : (e.dssText || "-"));
    const cols = ["study / cohort", "n", "role", "local recurrence", "metastasis", "disease-specific survival", "median F/U", "source"];
    const head = el("tr", {}, cols.map((c) => el("th", {}, c)));
    const order = [...entries].sort((a, b) => (a.pool === false) - (b.pool === false));
    const rows = order.map((e) => el("tr", { class: e.pool === false ? "muted" : "" }, [
      el("td", { title: e.note || "" }, e.label),
      el("td", {}, String(e.n != null ? e.n : "-")),
      el("td", {}, el("span", { class: "pill" }, e.pool === false ? "context" : "pooled")),
      el("td", {}, cell(e.recurrence, e.recurrencePct, e.recurrenceText)),
      el("td", {}, isBaselineMet(e) ? "(at diagnosis)" : cell(e.metastasis, e.metastasisPct, e.metastasisText)),
      el("td", {}, dssCell(e)),
      el("td", {}, e.medianFollowupMonths != null ? e.medianFollowupMonths + " mo" : "-"),
      el("td", {}, e.sourceUrl ? ext(e.sourceUrl, e.source || "source") : (e.isCases ? "see table below" : (e.source || ""))),
    ]));
    breakdownWrap.appendChild(el("table", {}, [el("thead", {}, head), el("tbody", {}, rows)]));
    breakdownWrap.appendChild(el("p", { class: "small muted", style: "padding:8px 4px" },
      "Top-line figures sum only the 'pooled' rows (explicit patient counts, non-overlapping populations). 'Context' rows come from larger series shown for comparison - not added in, to avoid double-counting overlapping patients or mixing in percentage-only data."));

    // ---- the individual cases that fed the pool ----
    if (!outPatients.length) { tableWrap.appendChild(el("p", { class: "small muted", style: "padding:8px 4px" }, "No individual case reports match these filters.")); return; }
    const pcols = ["age", "sex", "grade", "stage", "sizeCm", "site", "fusion", "primaryTreatment", "followupMonths", "vitalStatus", "localRecurrence", "metastasis", "source"];
    const phead = el("tr", {}, pcols.map((c) => el("th", {}, c)));
    const prows = outPatients.map((p) => el("tr", {}, pcols.map((c) => {
      if (c === "source" && p.sourceUrl) return el("td", { title: p.note || "" }, ext(p.sourceUrl, p.source || "source"));
      return el("td", { title: c === "source" ? (p.note || "") : "" }, p[c] === undefined ? "" : String(p[c]));
    })));
    tableWrap.appendChild(el("table", {}, [el("thead", {}, phead), el("tbody", {}, prows)]));
  }

  const filterCard = el("div", { class: "card" }, [
    el("div", { class: "kicker" }, "Filter the pooled evidence by your own details"),
    el("p", { class: "small muted" }, "Enter what applies to you to pool the matching published cohorts and case reports. Small, heterogeneous numbers - treat as a rough signal, never a prediction."),
    controls,
    el("div", { class: "spread" }, [
      el("button", { onclick: applyFilters }, "Apply filters"),
      el("button", { class: "secondary", onclick: () => { controls.querySelectorAll("input,select").forEach((e) => (e.value = "")); applyFilters(); } }, "Reset"),
    ]),
  ]);
  addSection("filter", "What happened to people like me?",
    el("p", { class: "intro" }, reg.intro || ""), regBanner, filterCard,
    el("div", { class: "card" }, [el("div", { class: "kicker" }, "Pooled result"), statsWrap]),
    el("div", { class: "card" }, [el("div", { class: "kicker" }, "Where the numbers come from"), breakdownWrap]),
    el("div", { class: "card" }, [el("div", { class: "kicker" }, "Individual case reports in this pool"), el("div", { style: "margin-top:12px" }, tableWrap)])
  );
  applyFilters(); // render the full pool on load

  // ---- TREATMENTS (filter by stage) ------------------------------------
  const tr = data.treatments || {};
  const stageSel = el("select", { id: "tx-stage" }, [
    el("option", { value: "" }, "Show all stages"),
    ...(tr.byStage || []).map((b) => el("option", { value: b.stage }, b.label || b.stage)),
  ]);
  const txBlocks = el("div", { class: "grid" });
  function renderTx() {
    const want = stageSel.value;
    txBlocks.innerHTML = "";
    (tr.byStage || []).filter((b) => !want || b.stage === want).forEach((b) => {
      txBlocks.appendChild(el("div", { class: "card" }, [el("div", { class: "kicker" }, b.label || b.stage), list(b.options)]));
    });
  }
  stageSel.addEventListener("change", renderTx);
  addSection("treatments", "Treatment plans",
    el("p", { class: "intro" }, tr.intro || ""),
    (tr.principles && tr.principles.length) ? el("div", { class: "card" }, [el("div", { class: "kicker" }, "General principles"), list(tr.principles)]) : null,
    el("div", { class: "card" }, [el("label", { class: "field", for: "tx-stage" }, "Filter by your stage"), stageSel]),
    txBlocks,
    tr.disclaimer ? el("p", { class: "disclaimer" }, tr.disclaimer) : null
  );
  renderTx();

  // ---- EMERGING / PROMISING TREATMENTS ---------------------------------
  const et = data.emergingTreatments || {};
  const etCards = el("div", { class: "grid cols-2" }, (et.items || []).map((it) =>
    el("div", { class: "card" }, [
      el("div", { class: "spread" }, [el("strong", {}, it.name), it.url ? ext(it.url, "source") : null]),
      it.status ? el("div", { class: "small" }, [el("span", { class: "pill warn" }, "investigational"), " " + it.status]) : null,
      it.summary ? el("p", { class: "small muted" }, it.summary) : null,
    ])
  ));
  addSection("emerging", "New & promising treatments",
    el("p", { class: "intro" }, et.intro || ""),
    (et.items && et.items.length) ? etCards : el("p", { class: "small muted" }, "Nothing catalogued yet - check the clinical trials below."),
    et.disclaimer ? el("p", { class: "disclaimer" }, et.disclaimer) : null
  );

  // ---- CLINICAL TRIALS --------------------------------------------------
  const ct = data.clinicalTrials || {};
  const ctSearch = (ct.liveSearches || []).length ? el("div", { class: "card" }, [
    el("div", { class: "kicker" }, "Find trials open now (these links update automatically)"),
    el("div", { class: "grid cols-2", style: "margin-top:8px" }, (ct.liveSearches || []).map((s) => el("div", {}, ext(s.url, s.label)))),
  ]) : null;
  const ctFinders = (ct.finders || []).length ? el("div", { class: "card" }, [
    el("div", { class: "kicker" }, "Other trial finders & helplines"),
    el("div", { class: "grid cols-3", style: "margin-top:8px" }, (ct.finders || []).map((s) => el("div", {}, ext(s.url, s.label)))),
  ]) : null;
  const ctHow = (ct.howToEnroll || []).length ? el("div", { class: "card" }, [
    el("div", { class: "kicker" }, "How to sign up"),
    el("ol", { style: "margin:6px 0 0; padding-left:20px" }, (ct.howToEnroll || []).map((x) => el("li", { style: "padding:4px 0" }, x))),
  ]) : null;
  const statusPill = (s) => {
    const v = (s || "").toLowerCase();
    const cls = (v.includes("recruit") && !v.includes("not yet")) ? "good" : (v.includes("not yet") || v.includes("active")) ? "warn" : "";
    return el("span", { class: "pill " + cls }, s || "status unknown");
  };
  const ctTrials = (ct.trials || []).length ? el("div", { class: "card" }, (ct.trials || []).map((t) =>
    el("div", { class: "study" }, [
      el("div", { class: "title" }, [ext(t.url, t.title)]),
      el("div", { class: "meta" }, [t.nctId ? el("span", { class: "tag" }, t.nctId) : null, t.phase ? el("span", { class: "tag" }, t.phase) : null, " ", statusPill(t.status)]),
      t.intervention ? el("div", { class: "small" }, "Intervention: " + t.intervention) : null,
      t.locations ? el("div", { class: "small muted" }, t.locations) : null,
      t.note ? el("div", { class: "small muted" }, t.note) : null,
    ])
  )) : (ct.trialsNote ? el("p", { class: "disclaimer" }, ct.trialsNote) : null);
  addSection("trials", "Clinical trials & how to join",
    el("p", { class: "intro" }, ct.intro || ""), ctSearch, ctFinders, ctHow, ctTrials);

  // ---- MONITORING -------------------------------------------------------
  const mon = data.monitoring || {};
  const monRows = (mon.schedule || []).map((s) =>
    el("tr", {}, [el("td", {}, s.phase), el("td", {}, s.interval), el("td", {}, s.imaging)])
  );
  addSection("monitoring", "Monitoring after treatment (remission)",
    el("p", { class: "intro" }, mon.intro || ""),
    monRows.length ? el("div", { class: "table-scroll" }, el("table", {}, [
      el("thead", {}, el("tr", {}, [el("th", {}, "Phase"), el("th", {}, "How often"), el("th", {}, "What's checked")])),
      el("tbody", {}, monRows),
    ])) : null,
    (mon.whatTheyWatchFor && mon.whatTheyWatchFor.length) ? el("div", { class: "card" }, [el("div", { class: "kicker" }, "What they watch for"), list(mon.whatTheyWatchFor)]) : null,
    (mon.selfMonitoring && mon.selfMonitoring.length) ? el("div", { class: "card" }, [el("div", { class: "kicker" }, "What you can watch for"), list(mon.selfMonitoring)]) : null,
    mon.disclaimer ? el("p", { class: "disclaimer" }, mon.disclaimer) : null
  );

  // ---- SUPPORT GROUPS ---------------------------------------------------
  const sg = data.supportGroups || {};
  const sgCards = el("div", { class: "grid cols-2" }, (sg.groups || []).map((g) =>
    el("div", { class: "card" }, [
      el("div", { class: "spread" }, [el("strong", {}, g.name), el("span", { class: "pill" }, g.platform || "")]),
      g.region ? el("div", { class: "small muted" }, g.region) : null,
      g.notes ? el("p", { class: "small" }, g.notes) : null,
      g.url ? ext(g.url, "Open") : null,
    ])
  ));
  addSection("support", "Support groups & communities",
    el("p", { class: "intro" }, sg.intro || ""), sgCards,
    sg.wanted ? el("p", { class: "disclaimer" }, sg.wanted) : null
  );

  // ---- CENTERS + SPECIALIST FINDER -------------------------------------
  const ce = data.centers || {};
  const centers = ce.list || [];
  const haversine = (a, b) => {
    const R = 6371, toRad = (d) => (d * Math.PI) / 180;
    const dLat = toRad(b.lat - a.lat), dLng = toRad(b.lng - a.lng);
    const x = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLng / 2) ** 2;
    return Math.round(R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x)));
  };
  const centerList = el("div", { class: "card" });
  function renderCenters(origin, countryFilter) {
    centerList.innerHTML = "";
    let items = centers.slice();
    if (countryFilter) items = items.filter((c) => c.country === countryFilter);
    if (origin) items.forEach((c) => (c._d = (c.lat != null && c.lng != null) ? haversine(origin, c) : Infinity));
    items.sort((a, b) => (origin ? (a._d || 0) - (b._d || 0) : a.country.localeCompare(b.country)));
    items.forEach((c) => {
      centerList.appendChild(el("div", { class: "center-item" }, [
        el("div", {}, [
          el("div", {}, [ext(c.url, c.name)]),
          el("div", { class: "small muted" }, `${c.city ? c.city + ", " : ""}${c.country}${c.notes ? " - " + c.notes : ""}`),
        ]),
        origin && c._d !== Infinity ? el("div", { class: "dist" }, `~${c._d.toLocaleString()} km`) : el("div", {}),
      ]));
    });
    if (!items.length) centerList.appendChild(el("p", { class: "small muted" }, "No centres listed for that country yet."));
  }
  const countries = Array.from(new Set(centers.map((c) => c.country))).sort();
  const countrySel = el("select", { id: "ce-country" }, [el("option", { value: "" }, "All countries"), ...countries.map((c) => el("option", { value: c }, c))]);
  const geoStatus = el("span", { class: "small muted" });
  const findBtn = el("button", {
    onclick: () => {
      if (!navigator.geolocation) { geoStatus.textContent = "Geolocation not available; use the country filter."; return; }
      geoStatus.textContent = "Locating...";
      navigator.geolocation.getCurrentPosition(
        (pos) => { geoStatus.textContent = "Sorted by distance from you."; renderCenters({ lat: pos.coords.latitude, lng: pos.coords.longitude }, countrySel.value); },
        () => { geoStatus.textContent = "Location permission denied; use the country filter instead."; }
      );
    },
  }, "Find centres near me");
  countrySel.addEventListener("change", () => renderCenters(null, countrySel.value));
  const dirRow = (ce.directories && ce.directories.length) ? el("div", { class: "card" }, [
    el("div", { class: "kicker" }, "Bigger directories to search"),
    el("div", { class: "grid cols-3", style: "margin-top:8px" }, ce.directories.map((d) => el("div", {}, ext(d.url, d.label)))),
  ]) : null;
  addSection("centers", "Centres of excellence & specialist finder",
    el("p", { class: "intro" }, ce.intro || ""),
    el("div", { class: "card" }, [
      el("div", { class: "kicker" }, "Find a specialist near you"),
      el("div", { class: "spread", style: "margin:8px 0" }, [findBtn, el("div", { style: "min-width:180px" }, countrySel), geoStatus]),
      el("p", { class: "small muted" }, "Your location is used only in your browser to sort the list - it is never sent anywhere."),
    ]),
    centerList,
    dirRow
  );
  renderCenters(null, "");

  // ---- QUESTIONS --------------------------------------------------------
  const qf = data.questionsForOncologist || {};
  const qGroups = (qf.groups || []).map((g) =>
    el("details", { class: "q-group" }, [el("summary", {}, g.topic), list(g.questions)])
  );
  addSection("questions", "Good questions to ask your oncologist",
    el("p", { class: "intro" }, qf.intro || ""), el("div", { class: "card" }, qGroups));

  // ---- ASSEMBLE ---------------------------------------------------------
  const toc = el("aside", { class: "toc" }, el("ul", {}, [
    el("li", {}, el("a", { href: "../../" }, "<- All cancers")),
    ...tocEntries.map((t) => el("li", {}, el("a", { href: "#" + t.id }, t.title))),
  ]));
  const main = el("div", {}, sections);
  app.appendChild(el("div", { class: "wrap" }, hero));
  app.appendChild(el("div", { class: "wrap" }, topBanner));
  app.appendChild(el("div", { class: "wrap" }, el("div", { class: "layout" }, [toc, main])));
  app.appendChild(el("footer", { class: "site" }, el("div", { class: "wrap" }, [
    el("div", { html: "<strong>Not medical advice.</strong> Reviewed status: " + m.dataConfidence + ". Sources are linked throughout - verify with your own team." }),
    el("div", {}, "Spot an error or have data to add? See CONTRIBUTING.md in the repository."),
  ])));
  } catch (err) {
    console.error(err);
    app.appendChild(el("div", { class: "wrap" }, el("p", { class: "banner" }, "Sorry - this page hit a display error while rendering: " + err.message + ". The data is fine; please report this so it can be fixed.")));
  }
})();
