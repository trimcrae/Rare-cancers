#!/usr/bin/env python3
"""TD1 residual batch 2 — R1/R3/R4 edits to the OWNER-OWNED main manuscript only.

Exact-literal replacement. Every anchor must occur EXACTLY ONCE or the run fails with exit 1 and
writes nothing. No producer, no statistic, no source fetch. Emits a changed-field map with byte
lengths and SHA256 for each edit and for the whole file before/after.
"""
import hashlib
import json
import sys

M = (sys.argv[1] if len(sys.argv) > 2 else
     "research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md")
OUT = sys.argv[2] if len(sys.argv) > 2 else M

EDITS = []


def edit(eid, group, where, old, new):
    EDITS.append({"id": eid, "group": group, "where": where, "old": old, "new": new})


# ---------------------------------------------------------------- R4 · EMC CRISPR availability
edit("M1", "R4", "front-matter `scope:` (M:17-20)",
     "  plus a public cancer cell-line CRISPR dependency release containing no EMC line. Reports no new\n",
     "  plus a public cancer cell-line CRISPR dependency release in which no EMC-labelled model\n"
     "  contributes CRISPR gene-effect data. Reports no new\n")

edit("M2", "R4", "top disclaimer block (M:39-41)",
     "> records and a public dependency release containing no cell line from this disease.\n",
     "> records and a public dependency release in which no EMC-labelled model contributes CRISPR\n"
     "> gene-effect data.\n")

edit("M3", "R4", "§7 Limits bullet (M:405-407)",
     "- **No EMC cell line carrying the fusion appears in the dependency release read here**, so every\n"
     "  dependency figure describes other cancer lines and cannot be transferred to EMC without an\n"
     "  assumption this paper does not test.\n",
     "- **No EMC-labelled model contributes CRISPR gene-effect data to the dependency release read\n"
     "  here.** One EMC-labelled model (ACH-001519) *is* present in that release's model metadata and\n"
     "  carries no gene-effect values (§1.2); that is a data-availability fact, not a determination of\n"
     "  its disease or fusion identity. Every dependency figure therefore describes other cancer lines\n"
     "  and cannot be transferred to EMC without an assumption this paper does not test.\n")

# ---------------------------------------------------------------- R1 · bounded literature scope
edit("M4", "R1", "§4 search-limits bullet, Q13 (M:330-332)",
     "- Query **Q13** located the one systematic human chaperone client screen (PMID 25036637),\n"
     "  whose full text names no FET protein; **whether the FET proteins appear in its deposited\n"
     "  supplementary panel is unknown** and was not retrieved.\n",
     "- Query **Q13** located the one systematic human chaperone client screen (PMID 25036637). ⚠ The\n"
     "  original article and its deposited supplement were **not inspectable in this review**, so this\n"
     "  paper does not assert what that article's body does or does not name. The retained curated\n"
     "  extract records a reading made on the retrieval date and is preserved as dated provenance, not\n"
     "  as verified full-text absence. **Whether the FET proteins appear in its deposited supplementary\n"
     "  panel is unknown** and was not retrieved, so the available material does not establish FET\n"
     "  membership in either direction.\n")

edit("M5", "R1", "§4 retained-extract paragraph (M:336-341)",
     "**What the inspected records do contain, with the distinctions kept.** *EWS::FLI1* protein levels fall\n"
     "when the HSP90 machine is perturbed pharmacologically (PMID 24388362; PMID 36495678) and when the\n"
     "HSP90 co-chaperone SGT1/SUGT1 is depleted genetically (PMID 25985210). ⚠ **That is depletion, not\n"
     "binding.** None of those reports includes a cycloheximide chase, a proteasome-block rescue or a\n"
     "parallel mRNA measurement, so a route through the fusion's own autoregulated transcription is not\n"
     "excluded.",
     "**What the retained curated extracts report, with the distinctions kept.** ⚠ What follows is stated\n"
     "at the scope of the **retained curated extracts and abstracts**. Apart from PMID 25985210, whose\n"
     "PMC full text was read on the recorded retrieval date, the original articles were not inspectable\n"
     "in this review, so assay-level detail is reported as what the retained record says, not as an\n"
     "independent reading of the article. Those extracts report that *EWS::FLI1* protein levels fall\n"
     "when the HSP90 machine is perturbed pharmacologically (PMID 24388362; PMID 36495678) and when the\n"
     "HSP90 co-chaperone SGT1/SUGT1 is depleted genetically (PMID 25985210). ⚠ **That is depletion, not\n"
     "binding.** ⚠ The retained extracts **do not establish whether those studies included a\n"
     "cycloheximide chase, a proteasome-block rescue or a parallel mRNA measurement**, and this paper\n"
     "does not assert that they did not. The mechanism of the depletion therefore remains unresolved\n"
     "here, and a route through the fusion's own autoregulated transcription is not excluded.")

edit("M6", "R1", "§5 outcome table, chaperone row (M:366)",
     "two unpaired descriptions. Compensation is not identified; clientship is untested |",
     "two unpaired descriptions. Compensation is not identified; clientship is not established by this evidence |")

# ---------------------------------------------------------------- R3 · temporal / estimand scope
edit("M7", "R3", "§6 update conditions, U4 (M:392)",
     "| U4 | the HSP70-and-stress list gives negative estimates not distinguishable from zero | a positive contrast in a third series would revise this exploratory estimate. ⛔ It would **not** identify a standing proteostatic load or restore a causal interpretation, because this comparison never identified one in either direction |",
     "| U4 | the HSP70-and-stress list gives negative estimates not distinguishable from zero | a positive contrast in a third series would update confidence in **generalization** and could reveal between-series heterogeneity. ⛔ It would **not** revise the fixed estimates recorded here for these two historical cohorts; a pooled or population estimate would be a separately defined analysis, and none is reported here. ⛔ It would **not** identify a standing proteostatic load or restore a causal interpretation, because this comparison never identified one in either direction |")

edit("M8", "R3", "§6 update conditions, U5 (M:393)",
     "| U5 | no qualifying binding result for a FET fusion was identified among the items inspected in the 2026-08-27 search | a published binding assay for a FET-family fusion would close the **search** question. ⛔ A finding in any FET fusion would not establish EWSR1/TAF15::NR4A3 clientship in EMC, which is a separate molecular hypothesis; the search claim and that hypothesis must be updated separately |",
     "| U5 | no qualifying binding result for a FET fusion was identified among the items inspected in the 2026-08-27 search | two temporal cases must be kept apart. A binding assay **published after** 2026-08-27 would update the **present evidence inventory**; it would not change the historical fact of what was identified among the items inspected on that date. An **earlier** qualifying assay shown to have been inside the searched set would instead expose an **extraction or classification error** in that search, and the fixed record would need correcting on that ground. ⛔ In either case, a finding in any FET fusion would not establish EWSR1/TAF15::NR4A3 clientship in EMC, which is a separate molecular hypothesis; the search claim and that hypothesis must be updated separately |")

# ---------------------------------------------------------------- R4 · scoring boundary
edit("M9", "R4", "§1.1 Scoring, aggregation/rounding boundary (after M:118)",
     "EMC-mean minus comparator-mean in units of the array's own probe-distribution SD.\n",
     "EMC-mean minus comparator-mean in units of the array's own probe-distribution SD.\n"
     "\n"
     "⚠ **Aggregation and rounding boundary.** Where several probes map to one gene symbol, their values\n"
     "are **averaged** for that array *before* standardization. The implementation stores the per-array\n"
     "background mean and SD, and the per-gene averaged value, **rounded to four decimal places**, forms\n"
     "the standardized score from those rounded quantities, and stores that score rounded in turn\n"
     "(`emc_expression_panels.py`). ⚠ Every statement about exact reproduction in §8 is bounded by that\n"
     "rounding: the original unrounded probe-level computation is not recoverable from the stored values.\n")

# ---------------------------------------------------------------- R4 · fixed identity + reproduction
edit("M10", "R4", "§8 Methods, fixed-identity paragraph (after M:429)",
     "search is `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json`.\n",
     "search is `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json`.\n"
     "\n"
     "**Fixed identities.** ⚠ Those repository-relative paths are mutable; the identities below are not.\n"
     "Each is the Git blob SHA-1 of the exact object this paper was read against, and each is verifiable\n"
     "with `git cat-file -p <id>` in this repository without trusting a path:\n"
     "\n"
     "| object | Git blob SHA-1 |\n"
     "|---|---|\n"
     "| `research/modalities/emc-expression-panels.json` | `330c04cb9277c3900919d45b548c730ec1746849` |\n"
     "| `research/modalities/emc_expression_panels.py` | `d260a5d3f080f2ca1299609e199b5dce492efca1` |\n"
     "| `research/modalities/census-route-expression-grading.json` | `b45a35a4ee2636993e42e897c3be6d7705ccae8a` |\n"
     "| `research/modalities/census_route_expression_grading.py` | `18625608b378122adbe9dbcca16de370c357367b` |\n"
     "| `research/modalities/depmap-sarcoma-dependency.json` | `1f00ad1cf509c540985d2d4be2830bcbec9a94a8` |\n"
     "| `research/modalities/depmap_sarcoma_dependency.py` | `fc0a0cc0316e562b03e2ad9eda36477d0c1c88d9` |\n"
     "| `research/modalities/emc_atr_vulnerability.py` (annotation extraction and sample classifier) | `177df6cfd72a787e316cfba07e71e4c4231026fb` |\n"
     "| `research/modalities/fet-ddr-axis-scan.json` | `41a575d2090457bc8e1eac15a56fab4c0f1bc0ac` |\n"
     "| `research/literature/txn-dependency-class-definitions-2026-08-09.json` | `a8fa744a1bcdabde4d60a1f56760b33070ff47c9` |\n"
     "| `research/literature/fet-fusion-chaperone-clientship-2026-08-27.json` | `8728c34de793da848ccae012e808e668b69b24bd` |\n"
     "\n"
     "⚠ **Numerical inputs versus annotation-only corrections.** A blob identity is a content identity,\n"
     "not provenance for raw data. A dated annotation-only correction to one of these artifacts changes\n"
     "its blob identity while changing **no** number, membership, cohort, threshold or quotation; such\n"
     "corrections are recorded with their own changed-field maps and leaf-invariance receipts under\n"
     "`research/autonomy/opus-capacity-campaign-20260908/paper-lane/`. ⛔ **No hash is claimed for the\n"
     "raw GEO series matrices or the DepMap CSV inputs.** Those files are not held here, no accessible\n"
     "public archive identity for them is asserted, and ⛔ **no producer was re-run to write this\n"
     "version** — the numbers reported are a reading of the committed outputs identified above.\n")

edit("M11", "R4", "§8 reproduction claim, replaced by three explicit levels (M:446-450)",
     "Given the retained derived summaries, the group statistics, the dependency table, and the conditional\n"
     "arithmetic in §2 are reproducible exactly. ⛔ The underlying standardized scores, the classifier's\n"
     "behaviour on the raw annotation text, and the DepMap per-line distributions are **not** reproducible\n"
     "without the original inputs, which are not held here.\n",
     "**Three levels, stated separately, because they are not the same claim.**\n"
     "\n"
     "1. **Readable back exactly.** The seven memberships, the per-platform readability, the deposited\n"
     "   per-specimen annotation strings and their derived class assignments, the rounded per-sample\n"
     "   `z_vs_array` values with their raw-scale gene averages and array percentiles, the group means,\n"
     "   Δ, Welch *t* and df, and the five dependency rows can all be read back from the committed\n"
     "   artifacts exactly as this paper reports them.\n"
     "2. **Replayable, bounded by rounding.** The deterministic sample classifier **can** be re-run\n"
     "   offline on the retained annotations: every consumed string is retained in\n"
     "   `emc-expression-panels.json` under `platforms.<file>.sample_annotations_verbatim[].annotation`,\n"
     "   and the classifier is source-visible as `emc_atr_vulnerability._classify_sample`, which\n"
     "   `emc_expression_panels.py` imports and applies. The conditional *p*-values and intervals in §2\n"
     "   can likewise be recomputed — but from the **rounded** Δ, *t* and df the artifact prints, so they\n"
     "   are approximate conditional calculations and not a recovery of the original unrounded analysis.\n"
     "3. **Not reproducible from what is held.** ⛔ Replaying the classifier on the retained strings does\n"
     "   **not** verify those strings against the original deposit; that check needs the original GEO\n"
     "   series matrices, which are not held here. ⛔ The all-probe reference distributions cannot be\n"
     "   regenerated from the stored rounded summaries, so the standardized scores cannot be\n"
     "   independently reconstructed from original probe values. ⛔ The probe-to-symbol mapping cannot be\n"
     "   revalidated, and the per-line DepMap Chronos distributions cannot be reconstructed.\n")


edit("M12", "R4", "§8 fixed-identity caveat, pending annotation-only corrections",
     "corrections are recorded with their own changed-field maps and leaf-invariance receipts under\n"
     "`research/autonomy/opus-capacity-campaign-20260908/paper-lane/`. ⛔ **No hash is claimed for the\n",
     "corrections are recorded with their own changed-field maps and leaf-invariance receipts under\n"
     "`research/autonomy/opus-capacity-campaign-20260908/paper-lane/`. ⚠ Two of the objects above —\n"
     "`census-route-expression-grading.json` and `fet-fusion-chaperone-clientship-2026-08-27.json` — have a\n"
     "dated annotation-only correction prepared but not yet integrated at the time of writing; when it is\n"
     "applied their blob identities change and no reported number, membership or quotation does. ⛔ **No\n"
     "hash is claimed for the\n")


edit("M13", "R4", "§1.1 Scoring, grammar of the rounding sentence",
     "background mean and SD, and the per-gene averaged value, **rounded to four decimal places**, forms\n"
     "the standardized score from those rounded quantities, and stores that score rounded in turn\n",
     "background mean and SD, and the per-gene averaged value, **rounded to four decimal places**; it then\n"
     "forms the standardized score from those rounded quantities and stores that score rounded in turn\n")

edit("M14", "R1", "§4 line reflow after the retained-extract correction",
     "here, and a route through the fusion's own autoregulated transcription is not excluded. Separately, engineered protein disaggregases acting on FET fusion proteins were reported\n",
     "here, and a route through the fusion's own autoregulated transcription is not excluded.\n"
     "\n"
     "Separately, engineered protein disaggregases acting on FET fusion proteins were reported\n")


def main():
    with open(M, encoding="utf-8") as fh:
        text = fh.read()
    before = text
    rows, failed = [], []
    for e in EDITS:
        n = text.count(e["old"])
        if n != 1:
            failed.append({"id": e["id"], "occurrences": n})
            continue
        text = text.replace(e["old"], e["new"], 1)
        rows.append({
            "id": e["id"], "group": e["group"], "where": e["where"],
            "old_bytes": len(e["old"].encode()), "new_bytes": len(e["new"].encode()),
            "old_sha256": hashlib.sha256(e["old"].encode()).hexdigest(),
            "new_sha256": hashlib.sha256(e["new"].encode()).hexdigest(),
        })
    if failed:
        json.dump({"status": "FAILED", "anchors_not_unique": failed}, sys.stdout, indent=2,
                  ensure_ascii=False)
        print()
        return 1
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    json.dump({
        "status": "APPLIED", "file": M, "n_edits": len(rows),
        "before_bytes": len(before.encode()),
        "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
        "after_bytes": len(text.encode()),
        "after_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "edits": rows,
    }, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
