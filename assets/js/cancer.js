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

  // ---- OUTCOMES FILTER TOOL (registry / IPD) ---------------------------
  const reg = data.registry || {};
  const patients = reg.patients || [];
  const curated = reg.dataStatus === "curated";

  const regBanner = !curated ? el("div", { class: "banner" }, [
    el("span", { html: "<strong>Illustrative data.</strong> " + (reg.dataStatusBanner || "These patient rows are placeholder/sample data and not real individuals.") }),
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

  function applyFilters() {
    const v = (id) => document.getElementById(id).value;
    const nv = (id) => (v(id) === "" ? null : Number(v(id)));
    const f = {
      ageMin: nv("f-ageMin"), ageMax: nv("f-ageMax"), sex: v("f-sex"), grade: v("f-grade"),
      stage: v("f-stage"), sizeMin: nv("f-sizeMin"), sizeMax: nv("f-sizeMax"),
      site: document.getElementById("f-site") ? v("f-site") : "",
      treatment: document.getElementById("f-treatment") ? v("f-treatment") : "",
    };
    const out = patients.filter((p) => {
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
    });
    renderResults(out);
  }

  function renderResults(out) {
    statsWrap.innerHTML = "";
    tableWrap.innerHTML = "";
    const n = out.length;
    const withVital = out.filter((p) => p.vitalStatus === "alive" || p.vitalStatus === "dead");
    const alive = withVital.filter((p) => p.vitalStatus === "alive").length;
    const dsd = out.filter((p) => p.diseaseSpecificDeath === true).length;
    const rec = out.filter((p) => p.localRecurrence === true).length;
    const met = out.filter((p) => p.metastasis === true).length;
    const fu = median(out.map((p) => p.followupMonths).filter((x) => typeof x === "number"));

    const stat = (val, label) => el("div", { class: "card" }, [el("div", { class: "stat" }, val), el("div", { class: "stat-label" }, label)]);
    statsWrap.appendChild(stat(String(n), "patients match"));
    if (n) {
      statsWrap.appendChild(stat(pct(alive, withVital.length) + "%", "alive at last follow-up"));
      statsWrap.appendChild(stat(pct(n - dsd, n) + "%", "disease-specific survival"));
      statsWrap.appendChild(stat(pct(rec, n) + "%", "had local recurrence"));
      statsWrap.appendChild(stat(pct(met, n) + "%", "developed metastasis"));
      statsWrap.appendChild(stat(fu != null ? fu + " mo" : "-", "median follow-up"));
    }

    if (!n) {
      tableWrap.appendChild(el("p", { class: "small muted", style: "padding:12px" }, "No matching patients. Loosen the filters."));
      return;
    }
    const cols = ["age", "sex", "grade", "stage", "sizeCm", "site", "fusion", "primaryTreatment", "followupMonths", "vitalStatus", "localRecurrence", "metastasis", "source"];
    const head = el("tr", {}, cols.map((c) => el("th", {}, c)));
    const rows = out.map((p) => el("tr", {}, cols.map((c) => el("td", {}, p[c] === undefined ? "" : String(p[c])))));
    tableWrap.appendChild(el("table", {}, [el("thead", {}, head), el("tbody", {}, rows)]));
  }

  const filterCard = el("div", { class: "card" }, [
    el("div", { class: "kicker" }, "Filter the pooled patients by your own details"),
    el("p", { class: "small muted" }, "Enter what applies to you to see how people with similar disease did. Small numbers - treat as a rough signal, never a prediction."),
    controls,
    el("div", { class: "spread" }, [
      el("button", { onclick: applyFilters }, "Apply filters"),
      el("button", { class: "secondary", onclick: () => { controls.querySelectorAll("input,select").forEach((e) => (e.value = "")); applyFilters(); } }, "Reset"),
    ]),
  ]);
  addSection("filter", "What happened to people like me?",
    el("p", { class: "intro" }, reg.intro || ""), regBanner, filterCard,
    el("div", { class: "card" }, [el("div", { class: "kicker" }, "Results"), statsWrap, el("div", { style: "margin-top:12px" }, tableWrap)])
  );

  // ---- TREATMENTS (filter by stage) ------------------------------------
  const tr = data.treatments || {};
  const stageSel = el("select", { id: "tx-stage" }, [
    el("option", { value: "" }, "Show all stages"),
    ...(tr.byStage || []).map((b) => el("option", { value: b.stage }, b.label || b.stage)),
  ]);
  const txBlocks = el("div", { class: "grid" });
  function renderTx() {
    const want = document.getElementById("tx-stage").value;
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
})();
