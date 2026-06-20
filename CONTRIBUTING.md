# Contributing

Thank you for helping make rare-cancer information easier to find. Contributions
from patients, carers, clinicians, and researchers are all welcome.

## The one rule that matters most

**Everything clinical must be true and sourced.** Frightened, newly diagnosed
people read this. Please:

- Add a real, working link for every study, statistic, and clinical claim.
- Never invent numbers or "round up" from memory — use ranges from real studies.
- Don't present sample/illustrative patient data as if it were real (see below).
- Don't remove or soften the medical disclaimers.

If you're not a clinician, that's fine — most contributions are about *finding
and linking* good sources, not giving advice.

## Easy ways to help (no coding)

Open an issue (or a PR editing the JSON) with any of:

- A study we're missing → the cancer's `studies.items`
- A support group (Facebook/Reddit/Discord/in-person) → `supportGroups.groups`
- A specialist centre (with city/country) → `centers.list`
- A correction to anything

## Editing a cancer page

All content for a cancer lives in **one file**: `data/cancers/<slug>.json`.
You don't need to touch HTML/CSS/JS.

1. Edit `data/cancers/<slug>.json`.
2. Run `node scripts/validate.mjs`.
3. Commit with a clear message.

## Adding a new cancer

```bash
node scripts/new-cancer.mjs <slug> "Full Name" "ABBR" "Category"
```

Then fill in `data/cancers/<slug>.json`. Use `data/cancers/emc.json` as the
worked example, and follow the playbook in [AGENTS.md](./AGENTS.md).

## The patient registry (individual participant data)

The "what happened to people like me?" tool reads `registry.patients` — one row
per reported patient. To be useful for rare cancers this should pool real cases
from published reports.

- Real rows: include a `source` citation for each, and set
  `registry.dataStatus` to `partial-curated` or `curated`.
- Don't have real rows yet? Keep `dataStatus: "SAMPLE_SYNTHETIC"` and a
  `dataStatusBanner`. The site shows a prominent warning so no one mistakes it
  for real data. Calibrate any sample data to match published group statistics.

Field definitions are in `registry.fields` in each data file and in
`data/schema.json`.

## Style

- Plain, kind, non-alarmist language. Define jargon.
- Keep zero dependencies and no build step.
- Match the existing vanilla-JS style if you touch `assets/js/`.
