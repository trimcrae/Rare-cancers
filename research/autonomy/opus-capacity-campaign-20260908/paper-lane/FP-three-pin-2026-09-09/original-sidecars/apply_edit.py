import json, hashlib, io, os
p = 'research/manuscripts/pinned-figures.json'
raw = open(p, 'rb').read()
d = json.loads(raw)

OLD_IDS = ["fusion_partner_dod_fisher_p",
           "fusion_partner_dod_taf15_percent",
           "fusion_partner_dod_comparator_percent"]

af = d["artifact_figures"]
idx = {e["id"]: i for i, e in enumerate(af) if isinstance(e, dict) and "id" in e}
assert all(i in idx for i in OLD_IDS), "missing an expected old id"
positions = sorted(idx[i] for i in OLD_IDS)
assert positions == list(range(positions[0], positions[0] + 3)), positions
first = positions[0]
retired = [af[idx[i]] for i in OLD_IDS]

# freeze the exact retired entries verbatim for the dated retirement record
json.dump(retired, open('/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/fp3/retired_entries.json', 'w'),
          indent=1, ensure_ascii=False)

CUR = ("analyses.B_outcome_by_partner.source_verified_recorded_outcomes"
       ".disease_specific_death")
ART = "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json"
MD = "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md"
REGEN = ("python3 research/manuscripts/emc_fusion_partner_pooling.py --write, then update "
         "every prose quotation of the figure IN THE SAME COMMIT (CLAUDE.md rule 1.3)")
SCOPE = (" ⛔ SCOPE: crude RECORDED disease-specific-death events in ONE consecutive surgical "
         "series (Agaram 2014, MSKCC, cohort `agaram-2014-outcome`, sourceId `agaram2014`, "
         "PMID 24746215), over unequal UNCENSORED observation windows. NOT a common-horizon "
         "survival probability, NOT adjusted, NOT a prognosis. One further EWSR1 patient died of "
         "unknown cause and is outside this numerator.")

new = [
 {
  "id": "fusion_partner_agaram2014_dod_taf15_percent",
  "description": ("The TAF15 arm's RECORDED disease-specific-death proportion in the §3.3 table's "
                  "disease-specific-death row — 3/7. Bound 2026-09-09 as one of three distinctly "
                  "named replacements for the retired pooled pins (see _artifact_figures_note): "
                  "this is a DIFFERENT QUANTITY from the withdrawn 73-patient Agaram+Huang pool, "
                  "not a new value for it. A typed value disagreeing with the artifact is the bug, "
                  "not the artifact." + SCOPE),
  "artifact": ART,
  "key": CUR + ".taf15_arm.percent",
  "format": "{:.1f} %",
  "context": "disease-specific death\\*\\* \\| \\*\\*3/7 = ([\\d.]+) ?%",
  "must_appear_in": [MD],
  "_context_note": ("⚠ The pattern CAPTURES the printed digits and is anchored to the "
                    "disease-specific-death ROW LABEL and its 3/7 numerator, because 6.2 % and "
                    "1/16 also appear on the local-recurrence row directly beneath it. A bare "
                    "number would bind the wrong row."),
  "regenerate": REGEN
 },
 {
  "id": "fusion_partner_agaram2014_dod_comparator_percent",
  "description": ("The EWSR1::NR4A3 comparator arm's RECORDED disease-specific-death proportion "
                  "in the same §3.3 table row — 1/16. Pairs with the TAF15 figure. Bound "
                  "2026-09-09; a distinctly named Agaram-only replacement for the retired pooled "
                  "6/58 = 10.3 % pin, which guarded a different quantity." + SCOPE),
  "artifact": ART,
  "key": CUR + ".comparator_arm.percent",
  "format": "{:.1f} %",
  "context": "disease-specific death\\*\\*.*\\| \\*\\*1/16 = ([\\d.]+) ?%",
  "must_appear_in": [MD],
  "_context_note": ("⚠ Anchored to the disease-specific-death row label: the line BELOW it (local "
                    "recurrence) prints the identical 1/16 = 6.2 %, so an unanchored pattern would "
                    "report a green check on the wrong row."),
  "regenerate": REGEN
 },
 {
  "id": "fusion_partner_agaram2014_dod_fisher_p",
  "description": ("The POST-HOC DESCRIPTIVE two-sided Fisher p printed in the §3.3 table's "
                  "disease-specific-death row. Bound 2026-09-09, replacing the retired "
                  "`fusion_partner_dod_fisher_p`, whose 0.0034 belonged to the withdrawn pooled "
                  "quantity and now survives only inside the §3.3 `Superseded, retained` "
                  "quotation. ⚠ NOT prespecified, not performed in any source report, not "
                  "corrected for the multiple endpoints on that page, and it licenses no claim." + SCOPE),
  "artifact": ART,
  "key": CUR + ".fisher_exact_two_sided_p",
  "format": "{:.4f}",
  "tolerance": 5e-05,
  "context": "disease-specific death\\*\\*.*\\| 36\\.6 pts \\| ([\\d.]+) \\|",
  "must_appear_in": [MD],
  "_context_note": ("⚠ Captures the p cell by its position after the row's difference cell. "
                    "Tolerance is tightened to 5e-05 because the default 0.005 is wider than the "
                    "quantity itself and would pass a materially different p."),
  "regenerate": REGEN
 },
]

for i in sorted(idx[i] for i in OLD_IDS)[::-1]:
    del af[i]
af[first:first] = new

note = d["_artifact_figures_note"]
assert isinstance(note, list)
note.append(
 "⛔ THREE HOMES RETIRED, 2026-09-09 — `fusion_partner_dod_fisher_p`, "
 "`fusion_partner_dod_taf15_percent`, `fusion_partner_dod_comparator_percent`. They bound "
 "`analyses.B_outcome_by_partner.disease_specific_death`, the POOLED Agaram 2014 + Huang 2023 "
 "disease-specific-death object `dod_pooled_agaram2014_huang2023` (7/15 = 46.7 % vs 6/58 = "
 "10.3 %, Fisher 0.0034) over 73 patients. §3.3 line 402 WITHDREW that pooled quantity — its "
 "Huang inputs were removed as source-unverified — and the object no longer exists in the "
 "artifact, so all three pins had been failing A-key-missing. THE FIGURES ARE NOT RESTATED "
 "ANYWHERE AS CURRENT: the 46.7 / 10.3 / 0.0034 text that remains in §3.3 sits inside an "
 "explicit `Superseded, retained` quotation, which is why the old context regexes still matched "
 "and made this look like a lost live headline. It was not. Replacing them are three DISTINCTLY "
 "NAMED entries — `fusion_partner_agaram2014_dod_*` — on the Agaram-only object `dod_agaram2014` "
 "under `source_verified_recorded_outcomes`. ★ THAT IS A DISCLOSED CHANGE OF GUARDED QUANTITY, "
 "NOT A PATH FIX: 3/7 vs 1/16 is not a corrected reading of 7/15 vs 6/58. The retired entries are "
 "preserved verbatim, with their provenance, in research/autonomy/opus-capacity-campaign-20260908/"
 "paper-lane/FP-three-pin-2026-09-09/RETIREMENT-RECORD-2026-09-09.md."
)

out = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
open(p, "w", encoding="utf-8").write(out)
nb = out.encode("utf-8")
print("new bytes", len(nb), "sha", hashlib.sha256(nb).hexdigest())
print("artifact_figures count", len(af))
