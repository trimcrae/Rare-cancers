// Renders the homepage list of cancers from data/index.json.
// Pure vanilla JS, no build step. Uses relative paths so it works on any host
// (GitLab Pages, GitHub Pages, a subpath, or file://-ish previews via a server).
(async function () {
  const el = (t, props = {}, kids = []) => {
    const n = document.createElement(t);
    Object.entries(props).forEach(([k, v]) => {
      if (k === "class") n.className = v;
      else if (k === "html") n.innerHTML = v;
      else n.setAttribute(k, v);
    });
    (Array.isArray(kids) ? kids : [kids]).forEach((c) =>
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c)
    );
    return n;
  };

  const root = document.getElementById("app");
  try {
    const data = await fetch("data/index.json").then((r) => r.json());
    document.title = data.site.title;

    const hero = el("section", { class: "hero" }, [
      el("h1", {}, data.site.title),
      el("p", { class: "tagline" }, data.site.tagline),
    ]);
    root.appendChild(el("div", { class: "wrap" }, hero));

    const list = el("div", { class: "grid cols-2" });
    data.cancers
      .filter((c) => c.status !== "hidden")
      .forEach((c) => {
        const card = el("a", { class: "card cancer-card", href: `cancers/${c.slug}/` }, [
          el("div", { class: "spread" }, [
            el("h3", {}, c.name),
            el("span", { class: "pill" }, c.abbreviation),
          ]),
          el("div", { class: "cat" }, c.category || ""),
          el("p", { class: "small muted" }, c.summary || ""),
          el("span", { class: "pill " + (c.status === "published" ? "good" : "warn") }, c.status || "draft"),
        ]);
        list.appendChild(card);
      });

    const section = el("section", { class: "section" }, [
      el("h2", {}, "Cancers covered"),
      el("p", { class: "intro" }, data.site.about),
      list,
    ]);
    root.appendChild(el("div", { class: "wrap" }, section));

    const foot = el("footer", { class: "site" }, [
      el("div", { class: "wrap" }, [
        el("div", { html: "<strong>Not medical advice.</strong> This is patient-built educational information. Always make decisions with your own medical team." }),
        el("div", {}, `Last updated ${data.site.lastUpdated}. Contributions welcome - see the repository's CONTRIBUTING.md.`),
      ]),
    ]);
    root.appendChild(foot);
  } catch (e) {
    root.appendChild(el("div", { class: "wrap" }, el("p", { class: "banner" }, "Could not load site data. If you are previewing locally, serve the folder over HTTP (e.g. `python3 -m http.server`) rather than opening the file directly.")));
    console.error(e);
  }
})();
